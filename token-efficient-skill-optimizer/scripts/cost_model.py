#!/usr/bin/env python3
"""Cost model for skill context footprints. token-efficient-skill-optimizer.

Reads a measure_tokens.py JSON report + provider-cost-profiles.yaml and prints
per-model cost RANGES for a usage scenario. Every number is labeled. Costs are
always ranges (token-estimate uncertainty x per-model rates), never points.

What this models (input-side context cost of a skill package):
  metadata tier  -> billed as input in EVERY session (N sessions)
  body tier      -> billed as input when the skill triggers (N * trigger_rate)
  conditional    -> billed as input when a reference is read (N * trigger_rate * read_rate)
Output-side generation cost depends on the skill's output contract and is NOT
modeled here - it must come from live runs or be labeled projected.

Usage:
    cost_model.py MEASURE.json [--config provider-cost-profiles.yaml]
        [--sessions 100] [--trigger-rate 0.3] [--ref-read-rate 0.5]
        [--cached | --uncached]   (default: report both)

Requires pyyaml (in the project venv).
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required (use the project venv)", file=sys.stderr)
    sys.exit(1)


def mtok_cost(tokens, rate_per_mtok):
    return tokens / 1_000_000 * rate_per_mtok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("measure_json")
    ap.add_argument("--config", default=str(
        Path(__file__).resolve().parent.parent / "config" /
        "provider-cost-profiles.yaml"))
    ap.add_argument("--sessions", type=int, default=100)
    ap.add_argument("--trigger-rate", type=float, default=0.3)
    ap.add_argument("--ref-read-rate", type=float, default=0.5)
    ap.add_argument("--date", default=None,
                    help="costing date YYYY-MM-DD; rows whose effective window "
                         "excludes it are refused, not silently used")
    args = ap.parse_args()

    report = json.loads(Path(args.measure_json).read_text(encoding="utf-8"))
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    snap = cfg["snapshot"]
    tt = report["tier_totals"]

    def rng(tier):
        return (tt[tier]["tokens_claude_low"], tt[tier]["tokens_claude_high"])

    meta_lo, meta_hi = rng("metadata")
    body_lo, body_hi = rng("body")
    cond_lo, cond_hi = rng("conditional")

    n = args.sessions
    trig = args.trigger_rate
    rr = args.ref_read_rate

    # expected input-tokens over the scenario (uncached)
    exp_lo = n * meta_lo + n * trig * (body_lo + rr * cond_lo)
    exp_hi = n * meta_hi + n * trig * (body_hi + rr * cond_hi)

    tok_label = report["token_label"]
    price_label = (f"estimated (pricing snapshot {snap['snapshot_date']}, "
                   f"source: {snap['anthropic_source']})")

    print("=" * 72)
    print(f"COST MODEL - scenario: {n} sessions, trigger_rate={trig}, "
          f"ref_read_rate={rr}")
    print(f"token basis:  {tok_label}")
    print(f"price basis:  {price_label}")
    print("=" * 72)
    print(f"expected input tokens over scenario: "
          f"{exp_lo:,.0f} - {exp_hi:,.0f}  [{'measured' if report['token_method']=='api' else 'estimated'}]")
    print()
    print(f"{'model':<22} {'uncached USD':>18} {'warm-cache USD':>18}")
    econ = cfg["anthropic"]["cache_economics"]
    # A price row is valid only inside its effective window. Costing outside it
    # silently uses a superseded price - so we skip the row and say we skipped
    # it, rather than emitting a number that looks authoritative and is stale.
    costing_date = args.date or snap["snapshot_date"]
    skipped = []

    def in_window(m):
        start, end = m.get("effective_start"), m.get("effective_end")
        if start and costing_date < str(start):
            return False, f"not yet effective (starts {start})"
        if end and costing_date > str(end):
            return False, f"expired on {end}; use the dated successor row"
        return True, ""

    seen = set()
    for m in cfg["anthropic"]["models"]:
        ok, why = in_window(m)
        if not ok:
            skipped.append(f"{m['display_name']}: {why}")
            continue
        label = m.get("api_model_id") or m["display_name"]
        if label in seen:   # e.g. intro vs standard pricing rows: show both
            label = m["display_name"]
        seen.add(label)
        rate = m["input_per_mtok"]
        u_lo, u_hi = mtok_cost(exp_lo, rate), mtok_cost(exp_hi, rate)
        # warm cache: metadata+body land in a cached prefix after first write;
        # approximate steady state as cache-read multiplier on the whole footprint.
        c_lo = u_lo * econ["cache_read_multiplier"]
        c_hi = u_hi * econ["cache_read_multiplier"]
        print(f"{label:<44} {u_lo:>8.4f}-{u_hi:<8.4f} "
              f"{c_lo:>8.4f}-{c_hi:<8.4f}  [estimated]")
    print()
    if skipped:
        print(f"rows refused for costing date {costing_date} (not silently used):")
        for s in skipped:
            print(f"  - {s}")
        print()
    print("caveats:")
    print("  - warm-cache column assumes the skill sits inside a stable cached")
    print("    prefix >= the model's minimum cacheable size and TTL is not")
    print("    exceeded between requests; first request pays the write premium")
    print(f"    (x{econ['cache_write_multiplier_5m']} for 5m TTL, "
          f"x{econ['cache_write_multiplier_1h']} for 1h TTL). [estimated]")
    print("  - output-side generation cost is NOT included. [not modeled]")
    print("  - latency: not measured; projection only.")
    if not cfg.get("openai", {}).get("models"):
        print("  - openai: no verified pricing snapshot present; refusing to")
        print("    fabricate rates. Run Refresh Evidence mode to populate.")


if __name__ == "__main__":
    main()
