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


def weighted_score(model_scores: dict, weights: dict) -> float:
    total = 0.0
    total_weight = 0.0
    for bench, w in weights.items():
        if bench in model_scores:
            total += model_scores[bench]["mean"] * w
            total_weight += w
    return total / total_weight if total_weight else 0.0


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
        weighted = weighted_score(benches, weights) * 100
        row.append(f"{weighted:.1f}")
        model_rows.append((weighted, row))

    model_rows.sort(key=lambda x: -x[0])
    for _, row in model_rows:
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    if model_rows:
        winner = model_rows[0][1][0]
        winner_score = model_rows[0][0]
        lines.append(f"Top model by weighted score: **{winner}** ({winner_score:.1f})")
        if len(model_rows) > 1:
            runner = model_rows[1][1][0]
            gap = model_rows[0][0] - model_rows[1][0]
            lines.append(f"Runner-up: {runner} (gap: {gap:.1f} points)")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Results are per-benchmark primary metric (HeQ F1, sentiment accuracy, HebNLI accuracy).")
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
