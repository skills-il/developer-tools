#!/usr/bin/env python3
"""Hebrew LLM eval runner.

Loads a benchmark from HuggingFace, calls a model endpoint, writes raw
outputs to disk. This is a reference implementation: for production runs,
wire it to your preferred orchestration (Airflow, Ray, LangChain, etc.).

Usage:
    python run_eval.py --benchmark heq --model claude-sonnet-4-6 --limit 100
    python run_eval.py --suite hebrew-core --models claude-sonnet-4-6,gpt-5,jamba-1.5-large
    python run_eval.py --suite hebrew-core --models claude-sonnet-4-6 --samples 1000 --runs 3

Before running:
    pip install datasets transformers anthropic openai google-genai ai21
    export ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, AI21_API_KEY

This file is a stub that demonstrates the CLI surface and dispatch logic.
The actual API calls must be implemented per provider. See references/
prompt-templates.md for template guidance.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BENCHMARKS = {
    "heq": {"hf_id": "pig4431/HeQ_v1", "metric": "f1"},
    "sentiment": {"hf_id": "HebArabNlpProject/HebrewSentiment", "metric": "accuracy"},
    "hebnli": {"hf_id": "HebArabNlpProject/HebNLI", "metric": "accuracy"},
}

SUITES = {
    "hebrew-core": ["heq", "sentiment", "hebnli"],
    "hebrew-summary": ["heq", "sentiment"],
    "hebrew-qa": ["heq"],
}

SUPPORTED_MODELS = {
    "claude-opus-4-7": "anthropic",
    "claude-opus-4-6": "anthropic",
    "claude-sonnet-4-6": "anthropic",
    "claude-haiku-4-5": "anthropic",
    "gpt-5": "openai",
    "gemini-3-pro": "google",
    "gemini-3-flash": "google",
    "gemini-2.5-pro": "google",
    "jamba-1.6-large": "ai21",
    "jamba-1.6-mini": "ai21",
    "jamba-reasoning-3b": "ai21",
    "jamba-1.5-large": "ai21",
    "jamba-1.5-mini": "ai21",
    "DictaLM-3.0-24B-Base": "huggingface",
    "DictaLM-3.0-24B-Thinking": "huggingface",
    "DictaLM-3.0-Nemotron-12B-Instruct": "huggingface",
    "DictaLM-3.0-1.7B": "huggingface",
    "DictaLM-3.0-1.7B-Thinking-GGUF": "huggingface",
}


def load_benchmark(name: str, limit: int | None = None) -> list[dict]:
    """Load a benchmark from HuggingFace. Returns a list of examples."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("datasets library not installed. Run: pip install datasets", file=sys.stderr)
        sys.exit(1)
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark: {name}. Available: {list(BENCHMARKS)}")
    hf_id = BENCHMARKS[name]["hf_id"]
    try:
        ds = load_dataset(hf_id, split="test")
    except Exception:
        ds = load_dataset(hf_id, split="validation")
    examples = list(ds)
    if limit:
        examples = examples[:limit]
    return examples


def build_prompt(benchmark: str, example: dict) -> str:
    """Return a zero-shot prompt for the given benchmark example."""
    if benchmark == "heq":
        return (
            "Read the Hebrew passage and answer the question. If the answer is "
            "not in the passage, respond exactly with UNANSWERABLE.\n\n"
            f"Passage: {example.get('context', '')}\n\n"
            f"Question: {example.get('question', '')}\n\nAnswer:"
        )
    if benchmark == "sentiment":
        return (
            "Classify the sentiment of the Hebrew text as POSITIVE, NEGATIVE, "
            "or NEUTRAL. Respond with one word only.\n\n"
            f"Text: {example.get('text', '')}\n\nSentiment:"
        )
    if benchmark == "hebnli":
        return (
            "Determine the relationship between the Hebrew premise and hypothesis. "
            "Answer with ENTAILMENT, CONTRADICTION, or NEUTRAL.\n\n"
            f"Premise: {example.get('premise', '')}\n"
            f"Hypothesis: {example.get('hypothesis', '')}\n\nAnswer:"
        )
    raise ValueError(f"No prompt template for benchmark {benchmark}")


def call_model(model: str, prompt: str) -> str:
    """Call a model endpoint. Returns the model's text response.

    This is a stub. Implement per provider using the provider's SDK.
    """
    provider = SUPPORTED_MODELS.get(model)
    if provider is None:
        raise ValueError(f"Unknown model: {model}. Add to SUPPORTED_MODELS.")

    if provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("Install anthropic: pip install anthropic")
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model=model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    if provider == "openai":
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("Install openai: pip install openai")
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
        )
        return resp.choices[0].message.content or ""

    if provider == "google":
        try:
            from google import genai
        except ImportError:
            raise RuntimeError("Install google-genai: pip install google-genai")
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        resp = client.models.generate_content(model=model, contents=prompt)
        return resp.text or ""

    if provider == "ai21":
        try:
            from ai21 import AI21Client
            from ai21.models.chat import ChatMessage
        except ImportError:
            raise RuntimeError("Install ai21: pip install ai21")
        client = AI21Client(api_key=os.environ["AI21_API_KEY"])
        resp = client.chat.completions.create(
            model=model,
            messages=[ChatMessage(role="user", content=prompt)],
        )
        return resp.choices[0].message.content

    if provider == "huggingface":
        raise NotImplementedError(
            "HuggingFace local inference not implemented in this stub. "
            "Use transformers or vLLM to run DictaLM models locally."
        )

    raise ValueError(f"Provider {provider} not handled")


def run_one(benchmark: str, model: str, limit: int, run_idx: int) -> dict:
    examples = load_benchmark(benchmark, limit=limit)
    outputs = []
    for i, ex in enumerate(examples):
        prompt = build_prompt(benchmark, ex)
        try:
            response = call_model(model, prompt)
        except Exception as e:
            response = f"__ERROR__: {e}"
        outputs.append({"idx": i, "example": ex, "response": response})
        if (i + 1) % 50 == 0:
            print(f"  [{benchmark}/{model}/run{run_idx}] processed {i + 1}/{len(examples)}", file=sys.stderr)
    return {
        "benchmark": benchmark,
        "model": model,
        "run_idx": run_idx,
        "ts": datetime.now(timezone.utc).isoformat(),
        "outputs": outputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hebrew LLM eval runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--benchmark", choices=list(BENCHMARKS))
    group.add_argument("--suite", choices=list(SUITES))
    parser.add_argument("--model", help="Single model ID")
    parser.add_argument("--models", help="Comma-separated model IDs")
    parser.add_argument("--limit", type=int, default=None, help="Max examples per benchmark")
    parser.add_argument("--samples", type=int, default=None, help="Alias for --limit")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs for statistical noise")
    parser.add_argument("--output-dir", default="./eval-results", help="Where to write results")
    args = parser.parse_args()

    limit = args.samples or args.limit

    if args.benchmark:
        benchmarks = [args.benchmark]
    else:
        benchmarks = SUITES[args.suite]

    if args.model:
        models = [args.model]
    elif args.models:
        models = [m.strip() for m in args.models.split(",")]
    else:
        print("Error: must specify --model or --models", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for model in models:
        for benchmark in benchmarks:
            for run_idx in range(args.runs):
                print(f"Running {benchmark} on {model} run {run_idx + 1}/{args.runs}", file=sys.stderr)
                result = run_one(benchmark, model, limit or 0, run_idx)
                fname = f"{benchmark}__{model.replace('/', '_')}__run{run_idx}.json"
                (out_dir / fname).write_text(json.dumps(result, ensure_ascii=False, indent=2))
                print(f"  wrote {out_dir / fname}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
