---
name: hebrew-llm-eval-suite
description: "Benchmark and compare LLMs on Hebrew reasoning, comprehension, sentiment, translation, and Israeli cultural knowledge. Wraps the HuggingFace Open Hebrew LLM Leaderboard tasks (HeQ reading comprehension, HebrewSentiment, Hebrew Winograd, NeuLabs-TedTalks translation) plus DictaLM 3.0 benchmark tasks (Summarization, Nikud diacritization, Israeli Trivia) into a reproducible evaluation harness. Runs evals against Claude, GPT, Gemini, AI21 Jamba, DictaLM, Llama, and local HuggingFace models. Produces comparison scorecards in JSON and markdown with per-task breakdowns. Use when choosing an LLM for a Hebrew product, answering procurement questions about Hebrew performance, validating a fine-tuned Hebrew model, or tracking Hebrew regressions after a model upgrade. Do NOT use for Arabic NLP evaluation, speech recognition benchmarking (use ivrit.ai leaderboard for ASR), or general English LLM benchmarks."
license: MIT
---

# Hebrew LLM Eval Suite

## Problem

Israeli product teams pick LLMs blind. There is no standardized Hebrew benchmark that a PM can run in an afternoon to compare Claude against GPT against DictaLM against AI21 Jamba on their actual use case. The HuggingFace Open Hebrew LLM Leaderboard exists but is built for base models and few-shot prompts, not for API-hosted chat models. DictaLM publishes benchmark results but only for its own suite. Teams end up guessing, testing informally, or trusting marketing claims. The result is costly model switches after launch, or shipping Hebrew products on models that silently fail on native speakers.

## Instructions

### Step 1: Pick the right benchmark set for your task

Different benchmarks test different things. Choose the smallest set that covers your actual use case.

| Benchmark | HuggingFace ID | What it tests | When to use |
|-----------|---------------|---------------|-------------|
| HeQ (Hebrew Question Answering) | `pig4431/HeQ_v1` | Reading comprehension, extractive QA on Hebrew Wikipedia and Geektime articles. 30,147 questions | Any product that answers questions over Hebrew text: search, RAG, support, research assistants |
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | Sentiment classification (positive, negative, neutral). 41,305 samples. License CC-BY-4.0 | Social media analysis, review classification, product feedback |
| Hebrew Winograd | Community port of Winograd Schema Challenge | Pronoun resolution requiring world knowledge. Reasoning-heavy | Any product that needs nuanced Hebrew understanding |
| NeuLabs-TedTalks (translation) | Open Hebrew LLM Leaderboard subset | English to Hebrew and Hebrew to English translation quality | Translation products, multilingual apps |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural Language Inference in Hebrew | Classification, content moderation, logical reasoning |
| DictaLM 3.0 Summarization | Dicta benchmark suite | Abstractive summarization of Hebrew news | Summarization tools, executive briefings |
| DictaLM 3.0 Nikud | Dicta benchmark suite | Adding vowel diacritics to unvocalized Hebrew | Educational tools, TTS preprocessing, religious text tools |
| DictaLM 3.0 Israeli Trivia | Dicta benchmark suite | Knowledge of Israeli culture, geography, history, politics | Consumer products where cultural grounding matters |

Rule of thumb: start with HeQ (comprehension) plus one task that matches your specific product. Adding benchmarks past three rarely changes the decision.

### Step 2: Pick the models to compare

A sensible default set for Israeli product teams:

| Provider | Model | Call via |
|----------|-------|----------|
| Anthropic | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Anthropic SDK |
| OpenAI | gpt-5 family | OpenAI SDK |
| Google | gemini-2.x | Google GenAI SDK |
| AI21 (Israeli) | jamba-1.5-large, jamba-1.5-mini | AI21 SDK or Amazon Bedrock |
| Dicta (Israeli, open-weight) | DictaLM-3.0-24B-Base, DictaLM-3.0-Nemotron-12B-Instruct, DictaLM-3.0-1.7B | HuggingFace transformers or vLLM |
| Meta (open-weight) | Llama-3.x-70B-Instruct | HuggingFace transformers or hosted |
| Mistral (open-weight) | Mistral-Large-Instruct | HuggingFace transformers or hosted |

AI21 explicitly positions Jamba 1.5 as supporting Hebrew as a core language. DictaLM is the strongest Hebrew-native open-weight option. Include at least one Hebrew-native model as a baseline, or the comparison tells you nothing about Hebrew-specific performance.

### Step 3: Set up the harness

Use `scripts/run_eval.py` as the runner. It loads benchmarks from HuggingFace, calls the configured model endpoints, and writes results to disk.

```bash
pip install datasets transformers anthropic openai google-genai ai21

export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export AI21_API_KEY=...

python scripts/run_eval.py --benchmark heq --model claude-sonnet-4-6 --limit 100
python scripts/run_eval.py --suite hebrew-core --models claude-sonnet-4-6,gpt-5,jamba-1.5-large
```

The harness uses few-shot prompting for base models and chat format for hosted models. Each benchmark has its own prompt template and scorer in `scripts/benchmarks/`.

### Step 4: Score and aggregate

Each benchmark has a primary metric:

| Benchmark | Primary metric | Secondary |
|-----------|---------------|-----------|
| HeQ | F1, Exact Match | Unanswerable accuracy |
| HebrewSentiment | Accuracy | Macro-F1 |
| Hebrew Winograd | Accuracy | None |
| Translation | BLEU, chrF | Human preference |
| HebNLI | Accuracy | Macro-F1 |
| Summarization | ROUGE-L, BERTScore-HE | Human preference |
| Nikud | Word Accuracy | Character Accuracy |
| Israeli Trivia | Accuracy | Category breakdown |

Use `scripts/score_results.py` to compute metrics. It handles HeQ normalization (Hebrew sofit forms, nikud removal, whitespace).

### Step 5: Generate the scorecard

Use `scripts/make_scorecard.py` to generate a comparison report. Output includes JSON for programmatic use, markdown with a model-vs-benchmark table, per-benchmark winner and gap analysis, and a weighted recommendation.

Example output excerpt:

```
| Model                          | HeQ F1 | Sentiment | Winograd | Trans BLEU | Weighted |
|--------------------------------|--------|-----------|----------|------------|----------|
| claude-sonnet-4-6              | 78.2   | 88.1      | 74.5     | 41.3       | 70.5     |
| gpt-5                          | 76.8   | 87.4      | 73.1     | 40.9       | 69.6     |
| jamba-1.5-large                | 74.1   | 85.9      | 70.2     | 38.7       | 67.2     |
| DictaLM-3.0-24B-Base           | 72.3   | 84.5      | 68.0     | 37.1       | 65.5     |
```

These are illustrative numbers. Actual results depend on prompts, dataset slices, and sampling parameters. Always attach the run config to the scorecard.

### Step 6: Control for statistical noise

A single run on a small subset is not a benchmark. Before trusting a scorecard:

- Run each model at least 3 times and report mean and standard deviation
- Use at least 500 samples per benchmark (ideally 1000+)
- Pin sampling parameters across models for fairness
- Log seeds where applicable
- Use the same prompt template across models unless comparing prompt strategies
- For HeQ, report F1 per question type (answerable vs unanswerable) separately
- For translation, use BLEU and chrF together because each metric has failure modes

`scripts/run_eval.py --runs 3 --samples 1000` handles multi-run aggregation.

### Step 7: Handle closed-source model caveats

API-hosted models change silently. Log the exact model version string from each API response where available. For Claude, use the dated model ID. For OpenAI, log the `model` field from the response. For Gemini, log the model version. This makes historical scorecards reproducible.

## Examples

### Example 1: Choosing a summarization model for a Hebrew news product

User says: "We are building a Hebrew news summary feature and need to pick between Claude, GPT, and DictaLM."

Actions:
1. Pick benchmarks: HeQ, DictaLM Summarization, Hebrew Winograd for nuance
2. Run `python scripts/run_eval.py --suite hebrew-summary --models claude-sonnet-4-6,gpt-5,DictaLM-3.0-24B-Base --samples 1000 --runs 3`
3. Review the scorecard and weighted recommendation
4. Validate top 2 on a small sample of the team's actual news articles with human raters
5. Pick based on weighted score plus cost and latency

Result: Data-backed model choice with a reproducible scorecard.

### Example 2: Tracking Hebrew regression after a provider upgrade

User says: "Anthropic just released a new model version. Did Hebrew quality improve or regress?"

Actions:
1. Re-run the standard suite against the new version and the previous version
2. Compare scorecards with `scripts/diff_scorecards.py prev.json new.json`
3. Flag any benchmark with more than 2 points drop as a regression
4. File a product decision (stay on old, move to new, A/B)

Result: Informed upgrade decision instead of blind follow-the-provider.

## Bundled Resources

### Scripts
- `scripts/run_eval.py` -- Main harness. Loads benchmarks from HuggingFace, calls model endpoints, writes raw outputs to disk. Run: `python scripts/run_eval.py --help`
- `scripts/score_results.py` -- Loads raw outputs and computes per-benchmark metrics (F1, BLEU, accuracy, ROUGE) with Hebrew-specific normalization. Run: `python scripts/score_results.py --help`
- `scripts/make_scorecard.py` -- Aggregates scores into a JSON and markdown scorecard with weighted recommendation. Run: `python scripts/make_scorecard.py --help`

### References
- `references/benchmark-catalog.md` -- Full catalog of Hebrew LLM benchmarks with HuggingFace IDs, licenses, sample counts, and prompt templates. Consult when adding a new benchmark.
- `references/prompt-templates.md` -- Zero-shot, few-shot, and chain-of-thought templates per benchmark, in English and Hebrew. Consult when tuning prompts.

## Recommended MCP Servers

No MCP server is required for running evals. Consider pairing with Hebrew data-source MCPs if you need to collect additional real-world test data beyond public benchmarks.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Open Hebrew LLM Leaderboard (HuggingFace) | https://huggingface.co/blog/leaderboard-hebrew | Leaderboard methodology, benchmark sources |
| HeQ dataset | https://huggingface.co/datasets/pig4431/HeQ_v1 | Dataset card, license, sample format |
| HebrewSentiment dataset | https://huggingface.co/datasets/HebArabNlpProject/HebrewSentiment | License, splits, label definitions |
| DictaLM 3.0 Technical Report | https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf | Dicta's Hebrew benchmark suite and methodology |
| Dicta organization on HuggingFace | https://huggingface.co/dicta-il | Latest DictaLM and DictaBERT models |
| AI21 Jamba model family announcement | https://www.ai21.com/blog/announcing-jamba-model-family/ | Jamba Hebrew support and model specs |
| Hebrew NLP Resources index | https://github.com/NNLP-IL/Hebrew-Resources | Comprehensive list of Hebrew NLP datasets and tools |

## Gotchas

- Closed-source LLM versions change silently. A scorecard from six months ago may not reflect current behavior. Always log the exact model version string returned by the API and re-run before trusting historical numbers.
- HeQ Exact Match scoring is brittle for Hebrew: sofit forms, nikud, and whitespace variations cause false negatives. Use F1 as the primary metric and only report EM with explicit Dicta-compatible normalization. Agents reporting raw EM understate every model's performance.
- Hebrew Winograd has fewer than 300 items. Any single run has high variance. Report results only with multiple runs and standard deviations. Agents that run it once and treat the result as gospel will flip model rankings between runs.
- AI21 Jamba uses a dedicated API (ai21.com or Amazon Bedrock). Do not assume the OpenAI SDK works with it. Use the AI21 Python SDK or Bedrock runtime.
- Translation BLEU on Hebrew is less reliable than BLEU on European languages due to Hebrew morphology. Report chrF alongside BLEU and spot-check low-scoring outputs manually. Agents that rely on BLEU alone miss the actual quality signal.
- DictaLM base models are not chat-tuned by default. Comparing them zero-shot against chat models like Claude is unfair. Use the Dicta instruction-tuned variants or use few-shot prompting with explicit task examples.

## Troubleshooting

### Error: "Rate limited by provider"
Cause: Too many parallel calls on a free tier or low quota.
Solution: Reduce `--parallel` in `run_eval.py` (default 4). For Anthropic and OpenAI, respect their request-rate guidance. Retries with exponential backoff are implemented in the runner.

### Error: "HeQ EM score is near zero for all models"
Cause: Exact match normalization is not applied. Hebrew whitespace, nikud, and sofit variations cause false negatives.
Solution: Use F1 as primary metric. Apply Dicta-compatible normalization via `scripts/score_results.py --normalize hebrew`.

### Error: "Translation BLEU tells the opposite story from human raters"
Cause: BLEU is unreliable on Hebrew due to morphology.
Solution: Use chrF alongside BLEU. Rate a sample of the lowest-scoring outputs manually.
