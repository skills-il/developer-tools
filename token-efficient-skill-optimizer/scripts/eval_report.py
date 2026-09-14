#!/usr/bin/env python3
"""Aggregate an eval_runner.py run log into an honest paired report.

Reads the JSONL written by eval_runner.py and produces per-variant summaries,
per-case paired deltas, a bootstrap CI on the mean delta, and the list of cases
where the CANDIDATE cost MORE than the baseline. Writes JSON (--json) and a
readable stdout summary.

HONESTY CONTRACT:
  * Nothing is invented. A metric the adapter never reported renders as the
    literal string "not observed" - never 0, never silently omitted. n on each
    row is the count of records that actually carried the metric.
  * Deltas are PAIRED, matched on (case_id, trial). A pair missing either side
    goes to incomplete_pairs and is reported; it is never quietly dropped, and
    its presence forces the release gate to "unresolved".
  * The bootstrap 95% CI (5000 draws, seeded) is returned as null when fewer
    than 5 pairs exist. An interval computed from 3 observations looks like
    evidence and is not; refusing to print it is the point.
  * higher_token_cases is a first-class output, printed in the summary and not
    only in the JSON. An optimization that regresses some cases while winning
    on the mean is the normal outcome, and hiding the regressions is how a
    "37% saving" gets shipped that nobody can reproduce.
  * total_observed_tokens is compared between variants only when BOTH sides
    observed the SAME token fields. Summing a different set of fields on each
    side produces a delta that measures adapter coverage, not the skill.
  * The release gate is deliberately non-committal. It reports "unresolved" on
    any adapter error, any incomplete pair, or no paired deltas at all, and the
    quality gate always demands a rubric-specific non-inferiority review. This
    script cannot certify a release; it can only refuse to pretend it did.

Every quantitative line in the stdout summary carries [measured] - the numbers
come from actual adapter-reported runs - so redirecting stdout into a .md file
passes scripts/validate_report.py (the run log is listed under "Harness data"
as the required data pointer).

Usage:
    eval_report.py RUN.jsonl [--json report.json] [--seed 1701]

Exit codes: 0 ok, 1 usage/parse error.
"""

import argparse
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

VARIANTS = ("baseline", "candidate")
NOT_OBSERVED = "not observed"
BOOTSTRAP_DRAWS = 5000
BOOTSTRAP_MIN_N = 5

# Token fields that make up total_observed_tokens.
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "retrieved_tokens",
    "tool_result_tokens",
)

# Fixed order so two runs on the same log print identically.
METRICS = list(TOKEN_FIELDS) + [
    "total_observed_tokens",
    "model_calls",
    "tool_calls",
    "retries",
    "latency_ms",
    "cost_usd",
    "task_success",
]


def is_number(value):
    """bool counts: task_success is often reported as True/False."""
    return isinstance(value, (int, float))


# --------------------------------------------------------------- statistics
def percentile(values, fraction):
    """Linear-interpolation percentile. None on an empty sample."""
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * fraction
    lower, upper = math.floor(rank), math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower]
                 + (ordered[upper] - ordered[lower]) * (rank - lower))


def summarize(values, total_records):
    """n/mean/p50/p95/min/max. Unobserved records are counted, not hidden."""
    return {
        "n": len(values),
        "unobserved": max(0, total_records - len(values)),
        "mean": statistics.fmean(values) if values else None,
        "p50": statistics.median(values) if values else None,
        "p95": percentile(values, 0.95),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def bootstrap_ci_mean(values, seed):
    """Seeded bootstrap 95% CI of the mean. None below BOOTSTRAP_MIN_N."""
    if len(values) < BOOTSTRAP_MIN_N:
        return None
    rng = random.Random(seed)
    n = len(values)
    means = [statistics.fmean(rng.choices(values, k=n))
             for _ in range(BOOTSTRAP_DRAWS)]
    low, high = percentile(means, 0.025), percentile(means, 0.975)
    if low is None or high is None:
        return None
    return [float(low), float(high)]


def ci_status(values):
    if len(values) >= BOOTSTRAP_MIN_N:
        return (f"bootstrap {BOOTSTRAP_DRAWS} draws, seeded, "
                f"n={len(values)} pairs")
    return (f"not computed (n={len(values)} < {BOOTSTRAP_MIN_N} pairs; a 95% "
            "interval from this few observations cannot mean anything)")


# ------------------------------------------------------------------ reading
def observed_token_fields(result):
    return tuple(f for f in TOKEN_FIELDS if is_number(result.get(f)))


def total_observed_tokens(result):
    fields = observed_token_fields(result)
    if not fields:
        return None
    return float(sum(result[f] for f in fields))


def read_log(path):
    header, results, errors = None, [], []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{number}: "
                                 f"{exc}") from exc
            kind = row.get("record_type")
            if kind == "run_header":
                header = row
            elif kind == "case_result":
                results.append(row)
            elif kind == "case_error":
                errors.append(row)
            else:
                raise ValueError(f"unknown record_type at {path}:{number}: "
                                 f"{kind!r}")
    return header, results, errors


# ---------------------------------------------------------------- aggregate
def aggregate(path, seed):
    header, rows, errors = read_log(path)

    by_variant = defaultdict(list)
    by_pair = defaultdict(dict)
    # Which cases failed critically, by identity -- the safety gate needs to know
    # WHICH case regressed, not how many did.
    crit_ids_by_variant = defaultdict(set)
    for row in rows:
        variant = row.get("variant")
        result = dict(row.get("result") or {})
        result["total_observed_tokens"] = total_observed_tokens(result)
        result["_token_fields"] = observed_token_fields(result)
        by_variant[variant].append(result)
        pair_key = (row.get("case_id"), int(row.get("trial", 0)))
        by_pair[pair_key][variant] = result
        if bool(result.get("critical_failure")):
            crit_ids_by_variant[variant].add(pair_key)

    variant_summaries = {}
    for variant in sorted(by_variant, key=str):
        records = by_variant[variant]
        metric_summary = {}
        for metric in METRICS:
            observed = [float(r[metric]) for r in records
                        if is_number(r.get(metric))]
            metric_summary[metric] = summarize(observed, len(records))
        variant_summaries[variant] = {
            "records": len(records),
            "critical_failures": sum(1 for r in records
                                     if bool(r.get("critical_failure"))),
            "metrics": metric_summary,
        }

    paired_deltas = defaultdict(list)
    higher_token_cases, incomplete_pairs, incomparable = [], [], []
    pairs_matched = 0
    for key in sorted(by_pair, key=lambda k: (str(k[0]), k[1])):
        present = by_pair[key]
        if set(present) != set(VARIANTS):
            incomplete_pairs.append({
                "case_id": key[0], "trial": key[1],
                "variants_present": sorted(str(v) for v in present),
                "note": "not dropped: this pair is excluded from every delta",
            })
            continue
        pairs_matched += 1
        base, cand = present["baseline"], present["candidate"]
        comparable = base["_token_fields"] == cand["_token_fields"]
        if not comparable:
            incomparable.append({
                "case_id": key[0], "trial": key[1],
                "baseline_token_fields": list(base["_token_fields"]),
                "candidate_token_fields": list(cand["_token_fields"]),
                "note": ("token totals not compared: the two sides observed "
                         "different fields, so their difference would measure "
                         "adapter coverage, not the skill"),
            })
        for metric in METRICS:
            if metric == "total_observed_tokens" and not comparable:
                continue
            before, after = base.get(metric), cand.get(metric)
            if is_number(before) and is_number(after):
                paired_deltas[metric].append(float(after) - float(before))
        if comparable:
            before = base.get("total_observed_tokens")
            after = cand.get("total_observed_tokens")
            if is_number(before) and is_number(after) and after > before:
                higher_token_cases.append({
                    "case_id": key[0], "trial": key[1],
                    "before": before, "after": after,
                    "delta": after - before,
                })

    paired_summaries = {}
    for metric in METRICS:
        values = paired_deltas.get(metric)
        if not values:
            continue
        paired_summaries[metric] = {
            "delta_candidate_minus_baseline": summarize(values, len(values)),
            "bootstrap_95_ci_mean_delta": bootstrap_ci_mean(values, seed),
            "ci_status": ci_status(values),
        }

    base_crit = variant_summaries.get("baseline", {}).get("critical_failures",
                                                          0)
    cand_crit = variant_summaries.get("candidate", {}).get("critical_failures",
                                                           0)
    # The gate compares IDENTITIES, not counts. `max(0, cand_crit - base_crit)`
    # reported "pass" whenever the totals matched: baseline fails case A, the
    # candidate fixes A and critically fails case B, both totals are 1, and a
    # brand-new safety regression shipped. Counts are still reported because
    # they are informative, but they no longer decide anything.
    base_crit_ids = crit_ids_by_variant.get("baseline", set())
    cand_crit_ids = crit_ids_by_variant.get("candidate", set())
    # Fail-closed on an unpaired candidate failure: a case the candidate fails
    # critically and the baseline has no record for counts as new, because
    # nothing shows it was pre-existing.
    new_critical_ids = sorted(cand_crit_ids - base_crit_ids,
                              key=lambda k: (str(k[0]), k[1]))
    fixed_critical_ids = sorted(base_crit_ids - cand_crit_ids,
                                key=lambda k: (str(k[0]), k[1]))
    new_critical = len(new_critical_ids)
    unresolved = bool(errors or incomplete_pairs or not paired_deltas)
    release_gate = {
        "baseline_critical_failures": base_crit,
        "candidate_critical_failures": cand_crit,
        "new_critical_failures": new_critical,
        "new_critical_cases": [{"case_id": c, "trial": t}
                               for c, t in new_critical_ids],
        "fixed_critical_cases": [{"case_id": c, "trial": t}
                                 for c, t in fixed_critical_ids],
        "safety_gate": ("unresolved" if unresolved
                        else "pass" if new_critical == 0 else "fail"),
        "quality_gate": "requires rubric-specific non-inferiority review",
        "efficiency_gate": ("requires paired confidence/practical-threshold "
                            "review" if paired_deltas else "unresolved"),
        "overall": ("unresolved" if unresolved
                    else "manual gate review required"),
        "unresolved_reasons": [
            r for r in (
                f"{len(errors)} adapter error(s)" if errors else "",
                f"{len(incomplete_pairs)} incomplete pair(s)"
                if incomplete_pairs else "",
                "no paired deltas" if not paired_deltas else "",
            ) if r
        ],
    }

    return {
        "source_log": str(Path(path).resolve()),
        "bootstrap_seed": seed,
        "header": header,
        "adapter_errors": errors,
        "incomplete_pairs": incomplete_pairs,
        "incomparable_token_pairs": incomparable,
        "pairs_matched": pairs_matched,
        "variant_summaries": variant_summaries,
        "paired_summaries": paired_summaries,
        "higher_token_cases": higher_token_cases,
        "release_gate": release_gate,
        "notes": [
            "'not observed' means the adapter never reported the metric; it is "
            "not zero and must never be rendered as zero.",
            "deltas are candidate minus baseline; negative = candidate used "
            "less of that metric.",
            "a bootstrap CI is null below "
            f"{BOOTSTRAP_MIN_N} paired observations, by design.",
            "this report is evidence for a human release decision, not a "
            "release decision.",
        ],
    }


# ------------------------------------------------------------------ printing
def fmt(value, digits=3):
    if value is None:
        return NOT_OBSERVED
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def fmt_ci(entry):
    ci = entry["bootstrap_95_ci_mean_delta"]
    if ci is None:
        return f"{NOT_OBSERVED} (n<{BOOTSTRAP_MIN_N})"
    return f"[{fmt(ci[0])}, {fmt(ci[1])}]"


def render(report, json_path):
    out = []
    w = 72
    out.append("=" * w)
    out.append("PAIRED EVAL REPORT  (candidate vs baseline)")
    out.append("=" * w)
    out.append("")

    # A fenced path list: the validator skips fenced lines, and its "Harness
    # data" scan still resolves the pointer that every [measured] line needs.
    out.append("## Harness data")
    out.append("")
    out.append("```")
    out.append(report["source_log"])
    if json_path:
        out.append(str(Path(json_path).resolve()))
    out.append("```")
    out.append("")

    header = report["header"] or {}
    out.append("## Run header")
    out.append("")
    if header:
        out.append(
            f"seed={header.get('seed')}  trials={header.get('trials')}  "
            f"cases={header.get('case_count')}  "
            f"scheduled_cells={header.get('scheduled_cells')}  "
            f"schema={header.get('schema_version')}  [measured]")
        out.append(f"timestamp_utc={header.get('timestamp_utc')}  [measured]")
        out.append("")
        out.append("```")
        for label, key in (("baseline ", "baseline"),
                           ("candidate", "candidate"),
                           ("adapter  ", "adapter")):
            out.append(f"{label} {header.get(key + '_path')}")
            out.append(f"{' ' * len(label)} sha256="
                       f"{header.get(key + '_sha256')}")
        out.append("```")
    else:
        out.append("no run_header record in the log - provenance UNKNOWN; "
                   "treat every number below as unattributable")
    out.append("")

    out.append("## Variant summaries")
    out.append("")
    out.append("n = records in which the adapter actually reported the "
               "metric.")
    out.append(f"'{NOT_OBSERVED}' = the adapter never reported it. It is not "
               "zero.")
    out.append("")
    for variant in VARIANTS:
        data = report["variant_summaries"].get(variant)
        if not data:
            out.append(f"{variant}: no records in the log")
            out.append("")
            continue
        out.append(f"{variant}: records={data['records']}  "
                   f"critical_failures={data['critical_failures']}  "
                   "[measured]")
        for metric in METRICS:
            s = data["metrics"][metric]
            if not s["n"]:
                out.append(f"  {metric:<22}{NOT_OBSERVED} "
                           f"(0 of {data['records']} records)  [measured]")
                continue
            out.append(
                f"  {metric:<22}n={s['n']:<5} mean={fmt(s['mean'])}  "
                f"p50={fmt(s['p50'])}  p95={fmt(s['p95'])}  "
                f"min={fmt(s['min'])}  max={fmt(s['max'])}  [measured]")
        out.append("")
    # Records under an unexpected variant name are surfaced, never hidden.
    for variant in sorted(report["variant_summaries"], key=str):
        if variant not in VARIANTS:
            out.append(f"UNEXPECTED VARIANT {variant!r}: "
                       f"{report['variant_summaries'][variant]['records']} "
                       "record(s) excluded from every pair  [measured]")
            out.append("")

    out.append("## Paired deltas (candidate minus baseline)")
    out.append("")
    out.append("Matched on (case_id, trial). Negative = candidate used less.")
    out.append(f"A CI is emitted only at n >= {BOOTSTRAP_MIN_N} pairs; below "
               f"that it reads '{NOT_OBSERVED}' and the JSON carries the "
               "reason in ci_status.")
    out.append("")
    out.append(f"pairs_matched={report['pairs_matched']}  "
               f"incomplete_pairs={len(report['incomplete_pairs'])}  "
               "[measured]")
    if not report["paired_summaries"]:
        out.append("  no paired deltas could be computed  [measured]")
    for metric in METRICS:
        entry = report["paired_summaries"].get(metric)
        if not entry:
            continue
        s = entry["delta_candidate_minus_baseline"]
        out.append(
            f"  {metric:<22}n={s['n']:<5} mean={fmt(s['mean'])}  "
            f"p50={fmt(s['p50'])}  p95={fmt(s['p95'])}  "
            f"ci95={fmt_ci(entry)}  [measured]")
    out.append("")

    out.append("## Higher-token cases (candidate used MORE observed tokens)")
    out.append("")
    higher = report["higher_token_cases"]
    out.append(f"count={len(higher)} of {report['pairs_matched']} matched "
               "pairs  [measured]")
    if not higher:
        out.append("  none - no matched pair regressed on total observed "
                   "tokens  [measured]")
    for row in higher[:50]:
        out.append(f"  {str(row['case_id']):<10} trial {row['trial']}  "
                   f"before={fmt(row['before'])}  after={fmt(row['after'])}  "
                   f"delta=+{fmt(row['delta'])}  [measured]")
    if len(higher) > 50:
        out.append(f"  ... {len(higher) - 50} more in the JSON report  "
                   "[measured]")
    out.append("")

    out.append("## Release gate (synthesis, not a verdict)")
    out.append("")
    gate = report["release_gate"]
    out.append(f"baseline_critical_failures={gate['baseline_critical_failures']}"
               f"  candidate_critical_failures="
               f"{gate['candidate_critical_failures']}  "
               f"new_critical_failures={gate['new_critical_failures']}  "
               "[measured]")
    # Counts alone hid a swap: one failure fixed, a different one introduced.
    # Naming the cases is what makes the gate auditable.
    for row in gate["new_critical_cases"]:
        out.append(f"  NEW CRITICAL   {str(row['case_id']):<10} "
                   f"trial {row['trial']}  [measured]")
    for row in gate["fixed_critical_cases"]:
        out.append(f"  fixed critical {str(row['case_id']):<10} "
                   f"trial {row['trial']}  [measured]")
    for key in ("safety_gate", "quality_gate", "efficiency_gate", "overall"):
        out.append(f"{key + ':':<18}{gate[key]}")
    if gate["unresolved_reasons"]:
        out.append("unresolved because: " + "; ".join(
            gate["unresolved_reasons"]) + "  [measured]")
    out.append("")

    out.append("## Exceptions")
    out.append("")
    out.append(f"adapter_errors={len(report['adapter_errors'])}  "
               f"incomplete_pairs={len(report['incomplete_pairs'])}  "
               f"incomparable_token_pairs="
               f"{len(report['incomparable_token_pairs'])}  [measured]")
    for row in report["adapter_errors"][:20]:
        out.append(f"  ERROR {row.get('case_id')} {row.get('variant')} "
                   f"trial {row.get('trial')}: {row.get('error_type')}: "
                   f"{str(row.get('error'))[:100]}")
    for row in report["incomplete_pairs"][:20]:
        out.append(f"  INCOMPLETE {row['case_id']} trial {row['trial']}: "
                   f"only {', '.join(row['variants_present']) or 'nothing'}")
    for row in report["incomparable_token_pairs"][:20]:
        out.append(f"  INCOMPARABLE {row['case_id']} trial {row['trial']}: "
                   f"baseline={row['baseline_token_fields']} "
                   f"candidate={row['candidate_token_fields']}")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Aggregate an eval_runner.py log.")
    ap.add_argument("input", type=Path, help="run log JSONL from eval_runner")
    ap.add_argument("--json", dest="json_out", type=Path,
                    help="write the full report as JSON")
    ap.add_argument("--seed", type=int, default=1701,
                    help="bootstrap seed (default 1701)")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: {args.input} not found")
    try:
        report = aggregate(args.input, args.seed)
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, sort_keys=True,
                       ensure_ascii=False) + "\n", encoding="utf-8")
    print(render(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
