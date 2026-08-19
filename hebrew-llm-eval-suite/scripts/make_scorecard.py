#!/usr/bin/env python3
"""Aggregate per-run scores into a JSON and markdown scorecard.

Takes the output of score_results.py, aggregates across runs (mean and
standard deviation), and produces:

- scorecard.json: machine-readable scorecard for programmatic use
- scorecard.md: human-readable markdown report with model-vs-benchmark
  table and weighted recommendation

Usage:
    python make_scorecard.py --scores scores.json --out-json scorecard.json --out-md scorecard.md
    python make_scorecard.py --scores scores.json --weights '{"heq":0.4,"sentiment":0.2,"hebnli":0.4}'
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PRIMARY_METRICS = {
    "heq": "f1",
    "sentiment": "accuracy",
    "hebnli": "accuracy",
}

DEFAULT_WEIGHTS = {
    "heq": 0.4,
    "sentiment": 0.3,
    "hebnli": 0.3,
}


def aggregate(scores: list[dict]) -> dict:
    """Aggregate raw scores into per-model per-benchmark mean and std."""
    agg: dict = defaultdict(lambda: defaultdict(list))
    for s in scores:
        model = s.get("model")
        bench = s.get("benchmark")
        metric_key = PRIMARY_METRICS.get(bench, "accuracy")
        val = s.get("metrics", {}).get(metric_key)
        if val is None:
            continue
        agg[model][bench].append(val)
    result: dict = {}
    for model, benches in agg.items():
        result[model] = {}
        for bench, values in benches.items():
            mean = statistics.mean(values) if values else 0.0
            std = statistics.stdev(values) if len(values) > 1 else 0.0
            result[model][bench] = {"mean": mean, "std": std, "n_runs": len(values)}
    return result


def weighted_score(model_scores: dict, weights: dict) -> tuple[float, float]:
    """Return (weighted score, coverage) where coverage is the share of weight present.

    Coverage is returned rather than swallowed because renormalising over only
    the benchmarks a model happens to have present rewards the model that
    FAILED its weakest benchmark: it gets averaged over its remaining, better
    results and can outrank a model that was measured on everything.
    """
    total = 0.0
    total_weight = 0.0
    all_weight = sum(weights.values())
    for bench, w in weights.items():
        if bench in model_scores:
            total += model_scores[bench]["mean"] * w
            total_weight += w
    score = total / total_weight if total_weight else 0.0
    coverage = total_weight / all_weight if all_weight else 0.0
    return score, coverage


def render_markdown(agg: dict, weights: dict) -> str:
    benchmarks = sorted({b for m in agg.values() for b in m})
    lines = [
        "# Hebrew LLM Scorecard",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Weights",
        "",
        "| Benchmark | Weight |",
        "|-----------|--------|",
    ]
    for b, w in weights.items():
        lines.append(f"| {b} | {w:.2f} |")
    lines.append("")

    header_cells = ["Model"] + benchmarks + ["Weighted"]
    lines.append("## Results (mean of runs)")
    lines.append("")
    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append("|" + "---|" * len(header_cells))

    model_rows = []
    for model, benches in agg.items():
        row = [model]
        for b in benchmarks:
            if b in benches:
                s = benches[b]
                if s["std"]:
                    row.append(f"{s['mean'] * 100:.1f} ± {s['std'] * 100:.1f}")
                else:
                    row.append(f"{s['mean'] * 100:.1f}")
            else:
                row.append("-")
        weighted_raw, coverage = weighted_score(benches, weights)
        weighted = weighted_raw * 100
        if coverage < 1.0:
            row.append(f"{weighted:.1f} (only {coverage * 100:.0f}% of weight measured)")
        else:
            row.append(f"{weighted:.1f}")
        # Widest per-benchmark std, used below to say whether the top-two gap
        # is bigger than the run-to-run noise behind it.
        worst_std = max((s["std"] * 100 for s in benches.values()), default=0.0)
        model_rows.append((weighted, row, coverage, worst_std))

    model_rows.sort(key=lambda x: -x[0])
    for entry in model_rows:
        lines.append("| " + " | ".join(entry[1]) + " |")

    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    if model_rows:
        winner = model_rows[0][1][0]
        winner_score = model_rows[0][0]
        lines.append(f"Top model by weighted score: **{winner}** ({winner_score:.1f})")
        if model_rows[0][2] < 1.0:
            lines.append("")
            lines.append(
                f"WARNING: {winner} was measured on only "
                f"{model_rows[0][2] * 100:.0f}% of the weighted benchmarks. Its score is "
                "renormalised over what it completed, so it is NOT comparable to a "
                "fully measured model. Treat this ranking as provisional."
            )
        if len(model_rows) > 1:
            runner = model_rows[1][1][0]
            gap = model_rows[0][0] - model_rows[1][0]
            noise = max(model_rows[0][3], model_rows[1][3])
            lines.append(f"Runner-up: {runner} (gap: {gap:.1f} points)")
            if noise and gap < 2 * noise:
                lines.append("")
                lines.append(
                    f"WARNING: the {gap:.1f}-point gap is within twice the run-to-run "
                    f"standard deviation ({noise:.1f}). This ranking is not "
                    "distinguishable from noise. Do not report a winner on this "
                    "evidence: add runs, add examples, or run a paired significance "
                    "test on the per-example results."
                )
            elif not noise:
                lines.append("")
                lines.append(
                    "NOTE: only one run per model, so there is no variance estimate "
                    "and this gap cannot be called significant. Re-run with --runs 3."
                )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Results are per-benchmark primary metric (HeQ F1, sentiment accuracy, HebNLI accuracy).")
    lines.append("- Scores across benchmarks are NOT commensurable: HeQ F1 has a nonzero floor, while the three-class tasks have a one-in-three chance baseline. The weighted column is a decision aid, not a measurement.")
    lines.append("- Public-benchmark scores are partly a memorisation measurement. Anchor a procurement decision on a private held-out set built from your own Hebrew data.")
    lines.append("- Hebrew normalization applied: nikud stripped, sofit forms normalized, whitespace collapsed.")
    lines.append("- Multi-run mean and standard deviation where n_runs > 1.")
    lines.append("- Always verify with human evaluation on your specific use case before shipping.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Hebrew LLM scorecard")
    parser.add_argument("--scores", required=True, help="Path to score_results.py JSON output")
    parser.add_argument("--out-json", default="scorecard.json")
    parser.add_argument("--out-md", default="scorecard.md")
    parser.add_argument("--weights", help="JSON dict of benchmark weights", default=None)
    args = parser.parse_args()

    scores_path = Path(args.scores)
    if not scores_path.exists():
        print(f"Scores file not found: {scores_path}", file=sys.stderr)
        return 1
    scores = json.loads(scores_path.read_text())
    if isinstance(scores, dict):
        scores = [scores]

    weights = DEFAULT_WEIGHTS
    if args.weights:
        weights = json.loads(args.weights)

    agg = aggregate(scores)
    Path(args.out_json).write_text(json.dumps({"weights": weights, "scores": agg}, ensure_ascii=False, indent=2))
    Path(args.out_md).write_text(render_markdown(agg, weights))
    print(f"Wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
