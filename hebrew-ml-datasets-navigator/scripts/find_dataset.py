#!/usr/bin/env python3
"""Interactive Hebrew ML dataset finder.

Filters a curated catalog of Hebrew and Yiddish ML datasets by task,
license, register, and language. Prints recommendations with HuggingFace
IDs, license notes, and pairing suggestions.

Usage:
    python find_dataset.py --task sentiment
    python find_dataset.py --task asr --language hebrew --commercial
    python find_dataset.py --list-tasks
    python find_dataset.py --interactive
"""

import argparse
import json
import sys

CATALOG = [
    {
        "id": "HebArabNlpProject/HebrewSentiment",
        "name": "HebrewSentiment",
        "task": "sentiment",
        "language": "hebrew",
        "register": ["mixed"],
        "size": "train + validation + test splits — verify current totals on the dataset card",
        "license": "check dataset card",
        "commercial_ok": None,
        "paired_model": "dicta-il/dictabert-sentiment",
        "notes": "3-class sentiment (positive, negative, neutral). Class distribution and license posture should be re-verified on the dataset card before commercial use.",
    },
    {
        "id": "HebArabNlpProject/HebNLI",
        "name": "HebNLI",
        "task": "nli",
        "language": "hebrew",
        "register": ["modern"],
        "size": "Check dataset card",
        "license": "Check dataset card",
        "commercial_ok": None,
        "paired_model": "dicta-il/dictabert",
        "notes": "Natural Language Inference (entailment, contradiction, neutral).",
    },
    {
        "id": "pig4431/HeQ_v1",
        "name": "HeQ",
        "task": "qa",
        "language": "hebrew",
        "register": ["modern", "technical"],
        "size": "30,147 questions (21,784 answerable + 8,363 unanswerable)",
        "license": "Check dataset card",
        "commercial_ok": None,
        "paired_model": "dicta-il/dictabert-heq",
        "notes": "Extractive QA on Hebrew Wikipedia and Geektime. Use F1 as primary metric (EM brittle).",
    },
    {
        "id": "ivrit-ai/crowd-transcribe-v5",
        "name": "ivrit.ai Crowd Transcribe v5",
        "task": "asr",
        "language": "hebrew",
        "register": ["spoken", "mixed"],
        "size": "Part of 22,000+ hours Hebrew audio",
        "license": "ivrit.ai permissive (commercial allowed)",
        "commercial_ok": True,
        "paired_model": "ivrit-ai/whisper-large-v3",
        "notes": "Latest crowd-sourced Hebrew ASR training data.",
    },
    {
        "id": "ivrit-ai/crowd-recital",
        "name": "ivrit.ai Crowd Recital",
        "task": "asr",
        "language": "hebrew",
        "register": ["read-aloud"],
        "size": "Part of 22,000+ hours",
        "license": "ivrit.ai permissive (commercial allowed)",
        "commercial_ok": True,
        "paired_model": "ivrit-ai/whisper-large-v3",
        "notes": "High-quality read-aloud audio, good for initial training.",
    },
    {
        "id": "ivrit-ai/audio-v2-opus",
        "name": "ivrit.ai Audio v2 (Opus)",
        "task": "asr",
        "language": "hebrew",
        "register": ["mixed"],
        "size": "Large-scale Hebrew audio, Opus-encoded",
        "license": "ivrit.ai permissive",
        "commercial_ok": True,
        "paired_model": "ivrit-ai/whisper-large-v3",
        "notes": "Smaller file size variant for bulk pre-training.",
    },
    {
        "id": "ivrit-ai/crowd-whatsapp-yi",
        "name": "ivrit.ai Yiddish WhatsApp",
        "task": "text",
        "language": "yiddish",
        "register": ["spoken", "informal"],
        "size": "Check dataset card",
        "license": "ivrit.ai permissive",
        "commercial_ok": True,
        "paired_model": None,
        "notes": "Yiddish text corpus. Do NOT mix with Hebrew models without careful cross-lingual handling.",
    },
    {
        "id": "ivrit-ai/crowd-recital-yi",
        "name": "ivrit.ai Yiddish Crowd Recital",
        "task": "asr",
        "language": "yiddish",
        "register": ["read-aloud"],
        "size": "Check dataset card",
        "license": "ivrit.ai permissive",
        "commercial_ok": True,
        "paired_model": "ivrit-ai/yi-whisper-large-v3",
        "notes": "Yiddish ASR training data.",
    },
    {
        "id": "Helsinki-NLP/opus-100",
        "name": "OPUS-100 (Hebrew subset)",
        "task": "translation",
        "language": "hebrew",
        "register": ["mixed"],
        "size": "Large multilingual parallel corpus (Hebrew is one of 100 languages paired with English)",
        "license": "Varies per sub-corpus, mostly permissive",
        "commercial_ok": None,
        "paired_model": None,
        "notes": "Broad He-En parallel data from the OPUS project. License varies per sub-corpus; read carefully before commercial use.",
    },
    {
        "id": "allenai/MADLAD-400",
        "name": "MADLAD-400 (Hebrew subset)",
        "task": "translation",
        "language": "hebrew",
        "register": ["mixed"],
        "size": "Pre-training scale, Hebrew is one of 400+ languages",
        "license": "ODC-BY",
        "commercial_ok": True,
        "paired_model": None,
        "notes": "Google's large multilingual dataset. Hebrew slice is useful for LLM pre-training. Check the Hebrew quality threshold in the paper.",
    },
    {
        "id": "opus.nlpl.eu/NeuLab-TedTalks",
        "name": "NeuLab-TedTalks (He-En) [OPUS, not on HF]",
        "task": "translation",
        "language": "hebrew",
        "register": ["spoken", "modern"],
        "size": "Check the OPUS page",
        "license": "Check the OPUS page",
        "commercial_ok": None,
        "paired_model": None,
        "notes": "Aligned He-En TED Talks corpus. Hosted on OPUS (opus.nlpl.eu/NeuLab-TedTalks/en&he/v1/NeuLab-TedTalks), NOT on HuggingFace. Used by the Open Hebrew LLM Leaderboard for translation evaluation.",
    },
    {
        "id": "dicta-il/hebrew-space-restoration-corpus",
        "name": "Hebrew Space Restoration Corpus",
        "task": "text",
        "language": "hebrew",
        "register": ["social-media"],
        "size": "5,959 test samples",
        "license": "Check dataset card",
        "commercial_ok": None,
        "paired_model": "dicta-il/dictabert-char-spacefix",
        "notes": "Test corpus for restoring missing spaces in scraped Hebrew social media text (W-NUT 2025). Derived from FineWeb-2 Hebrew portion. Test split only; train your own from FineWeb-2 if needed.",
    },
    {
        "id": "dicta-il/hebrew_suffix_verbal_forms",
        "name": "Hebrew Suffix Verbal Forms",
        "task": "text",
        "language": "hebrew",
        "register": ["modern"],
        "size": "2,853 rows (test split: 2,589 No_Suffix + 264 With_Suffix)",
        "license": "CC-BY-4.0",
        "commercial_ok": True,
        "paired_model": "dicta-il/dictabert-morph",
        "notes": "Binary classification for disambiguating pronominal suffixes in Hebrew verbs (e.g., 'למדם' as 'he taught him' vs 'they taught'). Class-imbalanced.",
    },
    {
        "id": "dicta-il/dictalm2.0-quant-calib-dataset",
        "name": "DictaLM 2.0 Quantization Calibration",
        "task": "text",
        "language": "hebrew",
        "register": ["mixed"],
        "size": "1,024 documents (512 Hebrew from Wikipedia+OSCAR, 512 English from FineWeb-EDU)",
        "license": "ODC-BY",
        "commercial_ok": True,
        "paired_model": "dicta-il/dictalm2.0",
        "notes": "Bilingual He-En calibration data for quantizing DictaLM 2.0 (GPTQ, AWQ). For DictaLM 3.0 quantization, check Dicta's latest releases.",
    },
]

TASKS = sorted({d["task"] for d in CATALOG})
LANGUAGES = sorted({d["language"] for d in CATALOG})


def filter_catalog(task: str | None, language: str | None, commercial: bool) -> list[dict]:
    result = CATALOG
    if task:
        result = [d for d in result if d["task"] == task]
    if language:
        result = [d for d in result if d["language"] == language]
    if commercial:
        result = [d for d in result if d.get("commercial_ok") is True]
    return result


def render(datasets: list[dict]) -> str:
    if not datasets:
        return "No datasets match the criteria. Check --list-tasks or widen the filters."
    lines = []
    for d in datasets:
        lines.append(f"# {d['name']} ({d['id']})")
        lines.append(f"- Task: {d['task']}")
        lines.append(f"- Language: {d['language']}")
        lines.append(f"- Register: {', '.join(d['register'])}")
        lines.append(f"- Size: {d['size']}")
        lines.append(f"- License: {d['license']}")
        commercial = (
            "Yes" if d.get("commercial_ok") is True
            else "No" if d.get("commercial_ok") is False
            else "Check dataset card"
        )
        lines.append(f"- Commercial use: {commercial}")
        if d.get("paired_model"):
            lines.append(f"- Recommended starting model: {d['paired_model']}")
        lines.append(f"- Notes: {d['notes']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Find Hebrew or Yiddish ML datasets")
    parser.add_argument("--task", choices=TASKS, help="Filter by task")
    parser.add_argument("--language", choices=LANGUAGES, help="Filter by language")
    parser.add_argument("--commercial", action="store_true", help="Only show commercial-friendly datasets")
    parser.add_argument("--list-tasks", action="store_true", help="List available task filters")
    parser.add_argument("--list-languages", action="store_true", help="List available language filters")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list_tasks:
        print("Available tasks: " + ", ".join(TASKS))
        return 0
    if args.list_languages:
        print("Available languages: " + ", ".join(LANGUAGES))
        return 0

    datasets = filter_catalog(args.task, args.language, args.commercial)
    if args.json:
        print(json.dumps(datasets, ensure_ascii=False, indent=2))
    else:
        print(render(datasets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
