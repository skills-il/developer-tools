#!/usr/bin/env python3
"""Score raw eval outputs from run_eval.py into per-benchmark metrics.

Handles Hebrew-specific normalization (sofit forms, nikud removal,
whitespace collapse) required for fair HeQ scoring.

Usage:
    python score_results.py --input eval-results/
    python score_results.py --input eval-results/ --normalize hebrew
    python score_results.py --input eval-results/heq__claude-sonnet-4-6__run0.json
"""

import argparse
import json
import re
import string
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Hebrew sofit (final form) to non-sofit mapping
SOFIT_MAP = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

NIKUD_RE = re.compile(r"[\u0591-\u05C7]")


def normalize_hebrew(text: str) -> str:
    """Hebrew-aware normalization for scoring."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = NIKUD_RE.sub("", text)
    for sofit, plain in SOFIT_MAP.items():
        text = text.replace(sofit, plain)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def f1_score(pred: str, gold: str, normalize: bool = True) -> float:
    if normalize:
        pred = normalize_hebrew(pred)
        gold = normalize_hebrew(gold)
    pred_tokens = pred.split()
    gold_tokens = gold.split()
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def exact_match(pred: str, gold: str, normalize: bool = True) -> float:
    if normalize:
        pred = normalize_hebrew(pred)
        gold = normalize_hebrew(gold)
    return 1.0 if pred == gold else 0.0


def score_heq(outputs: list[dict]) -> dict:
    em_scores = []
    f1_scores = []
    unanswerable_total = 0
    unanswerable_correct = 0
    for o in outputs:
        resp = (o.get("response") or "").strip()
        ex = o.get("example", {})
        gold_answers = ex.get("answers", {}).get("text", [])
        is_unanswerable = len(gold_answers) == 0 or gold_answers == [""]
        if is_unanswerable:
            unanswerable_total += 1
            if resp.strip().upper() == "UNANSWERABLE":
                unanswerable_correct += 1
            continue
        if not gold_answers:
            continue
        best_em = max((exact_match(resp, g) for g in gold_answers), default=0.0)
        best_f1 = max((f1_score(resp, g) for g in gold_answers), default=0.0)
        em_scores.append(best_em)
        f1_scores.append(best_f1)
    return {
        "f1": sum(f1_scores) / len(f1_scores) if f1_scores else 0.0,
        "em": sum(em_scores) / len(em_scores) if em_scores else 0.0,
        "unanswerable_acc": (
            unanswerable_correct / unanswerable_total if unanswerable_total else None
        ),
        "num_answerable": len(f1_scores),
        "num_unanswerable": unanswerable_total,
    }


def score_classification(outputs: list[dict], label_key: str, valid_labels: set[str]) -> dict:
    correct = 0
    total = 0
    per_label_correct: Counter = Counter()
    per_label_total: Counter = Counter()
    for o in outputs:
        resp = (o.get("response") or "").strip().upper().split("\n")[0].split()[0] if o.get("response") else ""
        gold = str(o.get("example", {}).get(label_key, "")).upper()
        if gold not in valid_labels:
            continue
        total += 1
        per_label_total[gold] += 1
        if resp.upper() == gold:
            correct += 1
            per_label_correct[gold] += 1
    per_label_acc = {
        label: per_label_correct[label] / per_label_total[label] if per_label_total[label] else 0.0
        for label in valid_labels
    }
    macro_f1 = sum(per_label_acc.values()) / len(valid_labels) if valid_labels else 0.0
    return {
        "accuracy": correct / total if total else 0.0,
        "macro_f1": macro_f1,
        "per_label_accuracy": per_label_acc,
        "num": total,
    }


def score_file(path: Path) -> dict:
    data = json.loads(path.read_text())
    benchmark = data.get("benchmark")
    outputs = data.get("outputs", [])
    if benchmark == "heq":
        metrics = score_heq(outputs)
    elif benchmark == "sentiment":
        metrics = score_classification(outputs, "label", {"POSITIVE", "NEGATIVE", "NEUTRAL"})
    elif benchmark == "hebnli":
        metrics = score_classification(outputs, "label", {"ENTAILMENT", "CONTRADICTION", "NEUTRAL"})
    else:
        metrics = {"error": f"No scorer for benchmark {benchmark}"}
    return {
        "benchmark": benchmark,
        "model": data.get("model"),
        "run_idx": data.get("run_idx"),
        "metrics": metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Hebrew eval outputs")
    parser.add_argument("--input", required=True, help="File or directory of raw eval outputs")
    parser.add_argument("--output", help="Write scores as JSON to this path")
    parser.add_argument("--normalize", default="hebrew", help="Normalization mode (hebrew)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_file():
        files = [input_path]
    else:
        files = sorted(input_path.glob("*.json"))

    results = []
    for f in files:
        try:
            results.append(score_file(f))
        except Exception as e:
            print(f"Error scoring {f}: {e}", file=sys.stderr)

    if args.output:
        Path(args.output).write_text(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
