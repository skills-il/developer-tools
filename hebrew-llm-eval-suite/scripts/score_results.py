#!/usr/bin/env python3
"""Score raw eval outputs from run_eval.py into per-benchmark metrics.

Handles Hebrew-specific normalization (sofit forms, nikud removal,
whitespace collapse) required for fair HeQ scoring.

Usage:
    python score_results.py --input eval-results/
    python score_results.py --input eval-results/ --normalize hebrew
    python score_results.py --input eval-results/heq__claude-opus-5__run0.json
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

# U+05BE MAQAF is a word-JOINING hyphen, so it must become a space rather than
# be deleted: deleting it turns "תל־אביב" into "תלאביב", which then fails to
# match the spaced form "תל אביב" and silently costs you a correct answer.
# It sits inside the NIKUD_RE range, so it has to be handled BEFORE that sub.
MAQAF = "\u05BE"
# Geresh (U+05F3) and gershayim (U+05F4) are not ASCII, so string.punctuation
# does not touch them.
GERESH_RE = re.compile(r"[\u05F3\u05F4]")


def normalize_hebrew(text: str) -> str:
    """Hebrew-aware normalization for scoring."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace(MAQAF, " ")
    text = GERESH_RE.sub("", text)
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
    errored = 0
    for o in outputs:
        resp = (o.get("response") or "").strip()
        if resp.startswith("__ERROR__"):
            # An API failure is not a wrong answer. Counting it as one is how a
            # rate-limited run gets reported as a model that performs badly.
            errored += 1
            continue
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
        "num_errored": errored,
        "error": (
            f"all {len(outputs)} responses were API errors; this is a harness or "
            "quota failure, not model performance."
        ) if errored and not f1_scores and not unanswerable_total else None,
    }


# Real Hebrew classification datasets do not agree on what the gold field is
# called. HebArabNlpProject/HebrewSentiment, for example, has NO "label" field
# at all: its gold value lives in "tag_ids". Reading a single hardcoded key
# meant every gold lookup returned "", every example was skipped, and the
# scorer reported a clean, plausible 0.0 for every model. Probe a candidate
# list instead, and fail loudly rather than returning a fake zero.
LABEL_KEY_CANDIDATES = ("label", "tag_ids", "gold", "answer", "sentiment", "class")


def resolve_label(example: dict, label_key: str, valid_labels: set[str]) -> str:
    """Find the gold label in an example, tolerating dataset field-name drift."""
    keys = (label_key,) + tuple(k for k in LABEL_KEY_CANDIDATES if k != label_key)
    for key in keys:
        if key not in example:
            continue
        raw = str(example.get(key, "")).strip().upper()
        if raw in valid_labels:
            return raw
    return ""


def score_classification(outputs: list[dict], label_key: str, valid_labels: set[str]) -> dict:
    correct = 0
    total = 0
    skipped = 0
    errored = 0
    per_label_correct: Counter = Counter()
    per_label_total: Counter = Counter()
    for o in outputs:
        raw_resp = (o.get("response") or "").strip()
        if raw_resp.startswith("__ERROR__"):
            errored += 1
            continue
        tokens = raw_resp.upper().split()
        resp = tokens[0] if tokens else ""
        gold = resolve_label(o.get("example", {}), label_key, valid_labels)
        if gold not in valid_labels:
            skipped += 1
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
    # This is the mean of per-label RECALL, not macro-F1: no precision term is
    # computed anywhere here. Naming it macro_f1 put a misstated metric into
    # procurement scorecards, so it is reported under its real name.
    macro_recall = sum(per_label_acc.values()) / len(valid_labels) if valid_labels else 0.0
    return {
        "accuracy": correct / total if total else None,
        "macro_recall": macro_recall if total else None,
        "per_label_accuracy": per_label_acc,
        "num": total,
        "num_skipped_no_gold_label": skipped,
        "num_errored": errored,
        # A run where nothing was scorable is a pipeline failure, not a model
        # scoring zero. Surface it instead of averaging a fake 0.0 into a rank.
        "error": (
            f"0 of {len(outputs)} examples had a usable gold label "
            f"(tried {LABEL_KEY_CANDIDATES}). This is a field-name mismatch, "
            "not model performance."
        ) if total == 0 else None,
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
