#!/usr/bin/env python3
"""Paired baseline-vs-candidate eval runner. token-efficient-skill-optimizer.

Runs every (case x trial x variant) cell of a paired A/B evaluation through a
user-supplied adapter and writes one JSONL run log for eval_report.py. This
script performs no model call and knows nothing about any provider: the adapter
is the only thing that touches a runtime.

HONESTY CONTRACT (the reason this script exists):
  * Every metric in the log is REPORTED BY THE ADAPTER. The runner observes
    exactly one thing itself - runner_wall_ms, its own wall clock around the
    call - and claims nothing else as its own measurement.
  * Optional metrics default to None, NEVER 0. A 0 here means the adapter
    observed zero; a null means the adapter could not observe the field at all.
    Defaulting them to 0 is how a benchmark quietly turns "unknown" into
    "free" - the exact dishonesty this package exists to block.
  * Required keys are enforced. A result missing any of them raises an error
    naming exactly which keys are missing, instead of a record with holes.
    A required numeric key present as null is also rejected: it would vanish
    from the aggregate while the record still looked complete.
  * A/B order is shuffled with a seeded RNG (--seed) so ordering artifacts -
    warm caches, rate-limit backoff, provider-side drift during the run -
    cannot systematically favour whichever variant ran second.
  * The adapter is part of the experiment. Its path and sha256 go in the run
    header next to both variants and every case file; a benchmark whose
    adapter is unidentified is not reproducible.
  * An adapter exception becomes a case_error record and the run continues;
    the process then exits 2, so a green exit can never hide a partial run.

Adapter protocol - a Python module defining:
    def run_case(*, variant_path, case, trial, config) -> dict
Optional: an adapter that also declares a `variant` keyword (or **kwargs) is
additionally passed variant="baseline" | "candidate", so it never has to guess
the variant by sniffing the path string.

Required result keys:
    task_success, critical_failure, input_tokens, output_tokens,
    model_calls, tool_calls, retries, latency_ms
Optional (default null / {}):
    cached_input_tokens, reasoning_tokens, retrieved_tokens,
    tool_result_tokens, cache_write_tokens, cost_usd, scores,
    failure_category, raw_output_path
cached_input_tokens is optional, not required: most adapters we can actually
build cannot observe per-call cache hits, and requiring it would push authors
into reporting 0 for "unknown".

Usage:
    eval_runner.py --baseline DIR_OR_FILE --candidate DIR_OR_FILE \\
        --adapter ADAPTER.py --cases tests/cases.jsonl \\
        [--cases tests/safety.jsonl] [--cases tests/injection.jsonl] \\
        --output run.jsonl [--trials 5] [--seed 1701] \\
        [--config-json cfg.json] [--fail-fast]

Determinism: the schedule (which cell runs when) is a pure function of --seed,
the case ids and --trials. runner_wall_ms and the header timestamp are wall
clock and are the only fields that can differ between two identical runs; set
SOURCE_DATE_EPOCH=<unix seconds> to pin the timestamp.

Exit codes: 0 ok, 1 usage/validation error, 2 at least one adapter error.
"""

import argparse
import datetime
import hashlib
import importlib.util
import inspect
import json
import os
import random
import sys
import time
import traceback
from pathlib import Path

SCHEMA_VERSION = 1
# Named for what they are in this package, not "original/optimized": the
# candidate is a proposal under test, and calling it "optimized" before the
# numbers land is the first step toward reporting a win that did not happen.
VARIANTS = ("baseline", "candidate")

PROTOCOL = "run_case(*, variant_path, case, trial, config) -> dict"

REQUIRED_RESULT_KEYS = frozenset({
    "task_success",
    "critical_failure",
    "input_tokens",
    "output_tokens",
    "model_calls",
    "tool_calls",
    "retries",
    "latency_ms",
})

# Required keys that must be observed NUMBERS (not null, not a string).
NUMERIC_REQUIRED = ("input_tokens", "output_tokens", "model_calls",
                    "tool_calls", "retries", "latency_ms")

# Missing optional metrics stay null; zero must mean observed zero.
OPTIONAL_DEFAULTS = {
    "cached_input_tokens": None,
    "reasoning_tokens": None,
    "retrieved_tokens": None,
    "tool_result_tokens": None,
    "cache_write_tokens": None,
    "cost_usd": None,
    "scores": {},
    "failure_category": None,
    "raw_output_path": None,
}

SKIP_DIR_PARTS = {"__pycache__", "venv", ".venv", "node_modules", ".git"}


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on usage errors; 2 means 'adapter error' here."""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.exit(f"{self.prog}: error: {message}")


# ------------------------------------------------------------- provenance
def sha256_path(path):
    """sha256 of a file, or a deterministic tree digest of a directory.

    Variants in this package are skill PACKAGES (directories), not single
    files, so a plain read_bytes() digest cannot identify them. The directory
    digest hashes the sorted (relative posix path, file digest) manifest, so it
    is stable across machines and sensitive to any content or layout change.
    """
    p = Path(path)
    h = hashlib.sha256()
    if p.is_file():
        h.update(p.read_bytes())
        return h.hexdigest()
    for f in sorted(q for q in p.rglob("*") if q.is_file()):
        parts = f.relative_to(p).parts
        if any(part in SKIP_DIR_PARTS or part.startswith(".")
               for part in parts):
            continue
        h.update(f.relative_to(p).as_posix().encode("utf-8") + b"\0")
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def utc_timestamp():
    """ISO-8601 UTC. SOURCE_DATE_EPOCH pins it for byte-reproducible runs."""
    epoch = (os.environ.get("SOURCE_DATE_EPOCH") or "").strip()
    if epoch.isdigit():
        when = datetime.datetime.fromtimestamp(int(epoch),
                                               datetime.timezone.utc)
    else:
        when = datetime.datetime.now(datetime.timezone.utc)
    return when.isoformat()


# ----------------------------------------------------------------- adapter
def load_adapter(path):
    """Import the adapter by file path. Returns (run_case, accepts_variant)."""
    spec = importlib.util.spec_from_file_location("teso_eval_adapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import adapter module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    fn = getattr(module, "run_case", None)
    if not callable(fn):
        raise TypeError(f"adapter {path} must define {PROTOCOL}")

    accepts_variant = False
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return fn, accepts_variant      # unintrospectable callable: trust it
    has_kwargs = any(p.kind is inspect.Parameter.VAR_KEYWORD
                     for p in params.values())
    if not has_kwargs:
        # Fail once, at load, with the protocol spelled out. Without this the
        # same TypeError repeats once per scheduled cell and the run log fills
        # with hundreds of identical case_error records instead of one message.
        missing = [n for n in ("variant_path", "case", "trial", "config")
                   if n not in params]
        if missing:
            raise TypeError(
                f"adapter {path} run_case is missing keyword parameter(s): "
                f"{', '.join(missing)} - protocol is {PROTOCOL}")
    return fn, bool(has_kwargs or "variant" in params)


def validate_result(result):
    """Enforce the result contract; fill optional metrics with null, not 0."""
    if not isinstance(result, dict):
        raise TypeError("adapter result must be a dict, got "
                        f"{type(result).__name__}")

    # Accept a flat record or the {metrics: {...}, scores: {...}} shape.
    flat = dict(result)
    metrics = flat.pop("metrics", None)
    if metrics is not None:
        if not isinstance(metrics, dict):
            raise TypeError("adapter result['metrics'] must be a dict")
        flat = {**metrics, **flat}
    scores = flat.get("scores", {})
    if not isinstance(scores, dict):
        raise TypeError("adapter result['scores'] must be a dict")
    if "task_success" not in flat and "task_success" in scores:
        flat["task_success"] = scores["task_success"]
    if "retrieved_tokens" not in flat and "retrieval_tokens" in flat:
        flat["retrieved_tokens"] = flat.pop("retrieval_tokens")

    missing = sorted(REQUIRED_RESULT_KEYS - set(flat))
    if missing:
        raise ValueError("adapter result missing required key(s): "
                         + ", ".join(missing))
    unobserved = sorted(
        k for k in NUMERIC_REQUIRED
        if isinstance(flat[k], bool) or not isinstance(flat[k], (int, float)))
    if unobserved:
        raise ValueError(
            "required numeric key(s) present but not observed as a number: "
            + ", ".join(f"{k}={flat[k]!r}" for k in unobserved)
            + " - report the observed number, or fail the case; a null in a "
              "required field silently disappears from the aggregate")

    defaults = dict(OPTIONAL_DEFAULTS)
    defaults["scores"] = {}
    return {**defaults, **flat}


# ------------------------------------------------------------------- cases
def read_cases(path, split):
    """Read one JSONL case file. Each case carries its split and category."""
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{number}: "
                                 f"{exc}") from exc
            if not isinstance(row, dict) or "id" not in row:
                raise ValueError(f"missing case id at {path}:{number}")
            # Our schema has no 'split' field; the file it came from is the
            # split (tests/cases.jsonl -> "cases"). An explicit split in the
            # record wins.
            row.setdefault("split", split)
            rows.append(row)
    return rows


# -------------------------------------------------------------------- main
def main():
    ap = _Parser(description="Paired baseline/candidate eval runner.")
    ap.add_argument("--baseline", type=Path, required=True,
                    help="frozen baseline skill/prompt (file or directory)")
    ap.add_argument("--candidate", type=Path, required=True,
                    help="candidate under test (file or directory)")
    ap.add_argument("--adapter", type=Path, required=True,
                    help=f"module defining {PROTOCOL}")
    ap.add_argument("--cases", type=Path, action="append", required=True,
                    metavar="CASES.jsonl",
                    help="case file; repeat for several splits "
                         "(cases / safety / injection) in one pass")
    ap.add_argument("--output", type=Path, required=True,
                    help="JSONL run log to write")
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1701,
                    help="seeds the A/B schedule shuffle (default 1701)")
    ap.add_argument("--config-json", type=Path,
                    help="JSON passed verbatim to the adapter as config")
    ap.add_argument("--fail-fast", action="store_true",
                    help="stop at the first adapter error (still exits 2)")
    args = ap.parse_args()

    for path in [args.baseline, args.candidate, args.adapter, *args.cases]:
        if not path.exists():
            ap.error(f"path not found: {path}")
    if args.trials < 1:
        ap.error("--trials must be >= 1")

    try:
        run_case, accepts_variant = load_adapter(args.adapter)
    except (ImportError, TypeError) as exc:
        sys.exit(f"adapter error: {exc}")

    cases, case_files, seen = [], [], {}
    for cases_path in args.cases:
        split = cases_path.stem
        rows = read_cases(cases_path, split)
        for row in rows:
            if row["id"] in seen:
                ap.error(
                    f"duplicate case id {row['id']!r} in {cases_path} (already "
                    f"in {seen[row['id']]}). eval_report.py pairs records on "
                    "(case_id, trial); duplicate ids would cross-pair "
                    "unrelated cases")
            seen[row["id"]] = cases_path
        cases.extend(rows)
        case_files.append({
            "path": str(cases_path.resolve()),
            "sha256": sha256_path(cases_path),
            "split": split,
            "case_count": len(rows),
        })
    if not cases:
        ap.error("no cases found in the supplied --cases file(s)")

    config = (json.loads(args.config_json.read_text(encoding="utf-8"))
              if args.config_json else {})
    variant_paths = {"baseline": args.baseline, "candidate": args.candidate}

    # Full case x trial x variant schedule, shuffled with a seeded RNG so
    # neither variant systematically runs first.
    schedule = [(case, variant, trial)
                for case in cases
                for trial in range(1, args.trials + 1)
                for variant in VARIANTS]
    random.Random(args.seed).shuffle(schedule)

    header = {
        "record_type": "run_header",
        "schema_version": SCHEMA_VERSION,
        "runner": "eval_runner.py (token-efficient-skill-optimizer)",
        "seed": args.seed,
        "trials": args.trials,
        "case_count": len(cases),
        "scheduled_cells": len(schedule),
        "variants": list(VARIANTS),
        "baseline_path": str(args.baseline.resolve()),
        "baseline_sha256": sha256_path(args.baseline),
        "candidate_path": str(args.candidate.resolve()),
        "candidate_sha256": sha256_path(args.candidate),
        "case_files": case_files,
        "adapter_path": str(args.adapter.resolve()),
        "adapter_sha256": sha256_path(args.adapter),
        "adapter_receives_variant_name": accepts_variant,
        "config_json_path": (str(args.config_json.resolve())
                             if args.config_json else None),
        "digest_method": ("file sha256; directories = sha256 over the sorted "
                          "(relative path, file sha256) manifest"),
        "timestamp_utc": utc_timestamp(),
        "measurement_note": ("every metric below is reported by the adapter; "
                             "the runner observes only runner_wall_ms"),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    errors = 0
    with args.output.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(header, ensure_ascii=False,
                                sort_keys=True) + "\n")
        handle.flush()
        for case, variant, trial in schedule:
            kwargs = {
                "variant_path": str(variant_paths[variant]),
                "case": case,
                "trial": trial,
                "config": config,
            }
            if accepts_variant:
                kwargs["variant"] = variant
            start = time.perf_counter()
            try:
                result = validate_result(run_case(**kwargs))
            except Exception as exc:  # noqa: BLE001 - log it, keep the run
                errors += 1
                record = {
                    "record_type": "case_error",
                    "case_id": case["id"],
                    "split": case.get("split"),
                    "category": case.get("category"),
                    "variant": variant,
                    "trial": trial,
                    "runner_wall_ms": round(
                        (time.perf_counter() - start) * 1000, 3),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
                handle.write(json.dumps(record, ensure_ascii=False,
                                        sort_keys=True) + "\n")
                handle.flush()
                if args.fail_fast:
                    traceback.print_exc()
                    print(f"--fail-fast: stopped after {errors} adapter "
                          f"error(s); partial log at {args.output}",
                          file=sys.stderr)
                    return 2
                continue
            record = {
                "record_type": "case_result",
                "case_id": case["id"],
                "split": case.get("split"),
                "category": case.get("category"),
                "variant": variant,
                "trial": trial,
                "runner_wall_ms": round((time.perf_counter() - start) * 1000,
                                        3),
                "result": result,
            }
            handle.write(json.dumps(record, ensure_ascii=False,
                                    sort_keys=True) + "\n")
            handle.flush()

    print(json.dumps({
        "output": str(args.output),
        "scheduled_cells": len(schedule),
        "case_count": len(cases),
        "trials": args.trials,
        "seed": args.seed,
        "adapter_errors": errors,
        "exit_code": 2 if errors else 0,
    }, indent=2, sort_keys=True))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
