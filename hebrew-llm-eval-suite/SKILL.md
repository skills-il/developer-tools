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
| HeQ (Hebrew Question Answering) | `Etelis/HeQ_v1` (HF mirror); canonical at `github.com/NNLP-IL/Hebrew-Question-Answering-Dataset` | Reading comprehension, extractive QA on Hebrew Wikipedia and Geektime articles. 30,147 questions | Any product that answers questions over Hebrew text: search, RAG, support, research assistants |
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | Sentiment classification (positive, negative, neutral). 41,305 samples. License CC-BY-4.0 | Social media analysis, review classification, product feedback |
| Hebrew Winograd | Community port of Winograd Schema Challenge (`cs.ubc.ca/~vshwartz/resources/winograd_he.jsonl`) | Pronoun resolution requiring world knowledge. Reasoning-heavy | Any product that needs nuanced Hebrew understanding |
| NeuLabs-TedTalks (translation) | OPUS NeuLab-TedTalks en-he subset | English to Hebrew and Hebrew to English translation quality | Translation products, multilingual apps |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural Language Inference in Hebrew | Classification, content moderation, logical reasoning |
| HEBREW-MMLU (general knowledge) | Hebrew-translated MMLU subset, used by the Open Hebrew LLM Leaderboard ecosystem (verify the active HF mirror before use; `openai/MMMLU` covers 14 languages but Hebrew is not in the official set) | 14-subject general-knowledge accuracy; Hebrew adaptation of Massive Multitask Language Understanding | General-purpose chat/RAG products that need broad world knowledge in Hebrew |
| DictaLM 3.0 Summarization | Dicta benchmark suite (see DictaLM 3.0 technical report) | Abstractive summarization of Hebrew news | Summarization tools, executive briefings |
| DictaLM 3.0 Nikud | Dicta benchmark suite | Adding vowel diacritics to unvocalized Hebrew | Educational tools, TTS preprocessing, religious text tools |
| DictaLM 3.0 Israeli Trivia | Dicta benchmark suite | Knowledge of Israeli culture, geography, history, politics | Consumer products where cultural grounding matters |

Rule of thumb: start with HeQ (comprehension) plus one task that matches your specific product. Adding benchmarks past three rarely changes the decision. For products that need broad world knowledge, add HEBREW-MMLU.

#### Recommended frameworks

Wrap the benchmarks above in an established eval framework rather than rolling a runner from scratch:

- **`lm-evaluation-harness` (EleutherAI)**: standard for reproducible base-model evals, used by the HuggingFace Open LLM Leaderboard. Hebrew tasks like HeQ, HebrewSentiment, and HebNLI are NOT shipped as native tasks (last checked April 2026); add them as custom YAML tasks pointing at the HF dataset IDs above. Good fit when comparing open-weight models with consistent few-shot prompting.
- **`inspect_ai` (UK AI Security Institute)**: opinionated framework with primitives for dataset, Task, Solver, and Scorer, plus multi-turn agent flows and a log viewer. Adopted by Anthropic, DeepMind, and others through 2024-25. Good fit for chat-model evals and graded scoring. Companion repo `UKGovernmentBEIS/inspect_evals` ships 200+ pre-built evals; Hebrew tasks are not in the default set but the harness is straightforward to extend.

Pick `lm-evaluation-harness` for base-model leaderboard parity, pick `inspect_ai` for chat-model and agent evals.

### Step 2: Pick the models to compare

A sensible default set for Israeli product teams:

| Provider | Model | Call via |
|----------|-------|----------|
| Anthropic | claude-opus-4-7 (1M context), claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Anthropic SDK |
| OpenAI | gpt-5 family | OpenAI SDK |
| Google | gemini-3 family (gemini-3-pro, gemini-3-flash), gemini-2.5-pro | Google GenAI SDK |
| AI21 (Israeli) | jamba-1.6-large, jamba-1.6-mini, jamba-reasoning-3b (open weights), legacy jamba-1.5-large, jamba-1.5-mini | AI21 SDK or Amazon Bedrock |
| Dicta (Israeli, open-weight) | `dicta-il/DictaLM-3.0-24B-Base`, `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct`, `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF`, `dicta-il/DictaLM-3.0-24B-Thinking`, plus `dicta-il/dictalm2.0-instruct` (DictaLM 2.0, 7B Mistral-based) | HuggingFace transformers or vLLM |
| Cohere (multilingual, Hebrew supported) | `CohereLabs/aya-expanse-8b`, `CohereLabs/aya-expanse-32b`, `CohereLabs/aya-23-8B`, `CohereLabs/aya-23-35B` | HuggingFace transformers or Cohere API |
| Hebrew-finetuned community models | `yam-peleg/Hebrew-Mistral-7B`, `yam-peleg/Hebrew-Gemma-11B-Instruct`, `yam-peleg/Hebrew-Mixtral-8x22B` | HuggingFace transformers |
| Meta (open-weight) | Llama-3.x-70B-Instruct | HuggingFace transformers or hosted |
| Mistral (open-weight) | Mistral-Large-Instruct | HuggingFace transformers or hosted |

AI21 explicitly positions Jamba 1.5 as supporting Hebrew as a core language. DictaLM is the strongest Hebrew-native open-weight option. Cohere's Aya-23 and Aya Expanse list Hebrew among their supported languages. Yam Peleg's Hebrew-* community models are continuously pretrained from Mistral, Gemma, and Mixtral with extended Hebrew tokenizers. Include at least one Hebrew-native model as a baseline, or the comparison tells you nothing about Hebrew-specific performance.

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

Example output excerpt (ILLUSTRATIVE PLACEHOLDERS, NOT MEASURED RESULTS):

```
| Model                          | HeQ F1 | Sentiment | Winograd | Trans BLEU | Weighted |
|--------------------------------|--------|-----------|----------|------------|----------|
| MODEL_A (placeholder)          | XX.X   | XX.X      | XX.X     | XX.X       | XX.X     |
| MODEL_B (placeholder)          | XX.X   | XX.X      | XX.X     | XX.X       | XX.X     |
| MODEL_C (placeholder)          | XX.X   | XX.X      | XX.X     | XX.X       | XX.X     |
| MODEL_D (placeholder)          | XX.X   | XX.X      | XX.X     | XX.X       | XX.X     |
```

The numbers above are placeholders for the shape of the scorecard, not real benchmark scores. Run your own evaluation (see Step 4) to fill in real values; actual results depend on prompts, dataset slices, sampling parameters, and the snapshot date of API-hosted models. Always attach the run config to the scorecard.

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

API-hosted models change silently. Log the exact model version string from each API response where available. For Claude, use the dated model ID (e.g. `claude-opus-4-7-20260415`) and log the `model` field returned in the response. For OpenAI, log the `model` field from the response and the `system_fingerprint` when available. For Gemini, log the `modelVersion` from the response metadata. This makes historical scorecards reproducible.

### Step 8: Account for tokenizer fairness

Tokenizer differences materially affect Hebrew evals on cost, latency, and even task accuracy:

- **BPE tokenizers** (GPT-4, Llama-3, Mistral) treat Hebrew as a long-tail language. Fertility (tokens per Hebrew word) is typically 3-5x higher than English. A 1,000-Hebrew-word prompt can balloon to 4,000-5,000 tokens.
- **SentencePiece tokenizers with Hebrew extensions** (DictaLM 2.0/3.0, Hebrew-Mistral-7B, Hebrew-Gemma-11B) inject Hebrew-specific tokens. DictaLM 2.0 reports compression of 2.76 tokens/Hebrew-word vs Mistral-7B's 5.78 tokens/word.
- **Aya/Cohere tokenizers** are tuned for the 23 supported languages including Hebrew, with fertility closer to native-tuned models than to vanilla BPE.

Implications for evals:
- Always log tokens-in and tokens-out per benchmark, not just sample count, when comparing cost or latency
- A model with worse raw F1 but 3x better tokenizer fertility may still be the right pick for a cost-sensitive product
- Models with high fertility hit context limits sooner; truncate fairly across the comparison set

Report a "fertility table" alongside the scorecard: model, mean tokens per Hebrew word on the same reference paragraph (we use the first 1,000 words of the HeQ test set as a fixed sample). `scripts/measure_fertility.py` computes this.

### Step 9: Normalize Hebrew text before scoring

HeQ scoring already calls Dicta-compatible normalization. Sentiment, NLI, and translation evals also need normalization or you will see artificial losses:

- **Strip nikud (vowel diacritics)** before string comparison. Reference labels and model outputs may differ only in nikud presence. Use the Unicode range U+05B0-U+05BC, U+05BD, U+05BF, U+05C1-U+05C2, U+05C7 plus the cantillation marks U+0591-U+05AF.
- **Normalize sofit (final) forms** for HeQ EM and string-match scorers: כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ. Replace the final-form variant with its base form on both sides.
- **Collapse whitespace** including non-breaking space U+00A0, zero-width joiner U+200D, and the Hebrew geresh/gershayim U+05F3-U+05F4 when comparing strings.
- **Lowercase Latin script** for translation outputs but leave Hebrew untouched (Hebrew has no case).
- **For sentiment and NLI**, model outputs can be a label word in nikud or with definite article. Apply nikud strip plus prefix-removal for ה־ before mapping to the label vocabulary.

`scripts/score_results.py --normalize hebrew-strict` applies all of the above. `--normalize hebrew-loose` skips sofit and prefix removal for translation evals where they would change meaning.

### Step 10: LLM-as-judge caveats for Hebrew

For graded scoring (summarization, translation, open-ended QA), an LLM judge is convenient but has Hebrew-specific failure modes:

- **English-style answer bias.** Most judge models were trained predominantly on English judgements. They tend to reward Hebrew responses that mirror English style (long, hedged, qualified) over native Israeli style (direct, terse, idiomatic). This systematically penalizes Hebrew-native models.
- **Script-switching false positives.** A judge may rate a Hebrew response with English technical terms more favorably than the same response in pure Hebrew, because mixed-script answers look more "informative" to a model trained on English.
- **Nikud and sofit confusion.** Some judge models penalize correct Hebrew that uses or omits nikud differently from their training distribution.
- **Cultural grounding gaps.** Judge models trained predominantly on English data miss subtle Israeli context (slang, military shorthand, holiday references) and may flag accurate answers as wrong.

Mitigations:
- Use at least two judge models from different vendors and report agreement; flag disagreements for human review
- Calibrate the judge with 30-50 human-rated Hebrew examples and report judge-vs-human agreement before trusting at scale
- Prefer Hebrew-native or strongly multilingual judges (Claude family, Gemini 2.x, Aya Expanse) over English-first judges
- For sentiment, NLI, and HeQ, prefer reference-based metrics (accuracy, F1) over LLM-as-judge entirely

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
| Open Hebrew LLM Leaderboard (live space) | https://huggingface.co/spaces/hebrew-llm-leaderboard/leaderboard | Live rankings, model submissions, current benchmark scores |
| Open Hebrew LLM Leaderboard (announcement blog) | https://huggingface.co/blog/leaderboard-hebrew | Leaderboard methodology, benchmark sources |
| HeQ dataset (HF mirror) | https://huggingface.co/datasets/Etelis/HeQ_v1 | Dataset card, sample format. Canonical source: github.com/NNLP-IL/Hebrew-Question-Answering-Dataset |
| HebrewSentiment dataset | https://huggingface.co/datasets/HebArabNlpProject/HebrewSentiment | License, splits, label definitions |
| HebNLI dataset | https://huggingface.co/datasets/HebArabNlpProject/HebNLI | License, splits, premise-hypothesis structure |
| DictaLM 3.0 Technical Report | https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf | Dicta's Hebrew benchmark suite and methodology (note: filename uses "Techincal" not "Technical") |
| Dicta organization on HuggingFace | https://huggingface.co/dicta-il | Latest DictaLM 3.0 variants (24B-Base, Nemotron-12B-Instruct, 1.7B-Thinking-GGUF, 24B-Thinking) and DictaBERT models |
| Cohere Aya organization | https://huggingface.co/CohereLabs | Aya-23 (8B/35B) and Aya Expanse (8B/32B) multilingual models with Hebrew support |
| Yam Peleg Hebrew models | https://huggingface.co/yam-peleg | Hebrew-Mistral-7B, Hebrew-Gemma-11B-Instruct, Hebrew-Mixtral-8x22B community finetunes |
| AI21 Jamba model family announcement | https://www.ai21.com/blog/announcing-jamba-model-family/ | Jamba Hebrew support and model specs |
| EleutherAI lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Standard base-model eval framework; Hebrew tasks must be added as custom YAMLs |
| UK AISI Inspect AI | https://github.com/UKGovernmentBEIS/inspect_ai | Chat-model eval framework with agent and graded-scoring primitives |
| Hebrew NLP Resources index | https://github.com/NNLP-IL/Hebrew-Resources | Comprehensive list of Hebrew NLP datasets and tools |

## Gotchas

- Closed-source LLM versions change silently. A scorecard from six months ago may not reflect current behavior. Always log the exact model version string returned by the API and re-run before trusting historical numbers.
- HeQ Exact Match scoring is brittle for Hebrew: sofit forms, nikud, and whitespace variations cause false negatives. Use F1 as the primary metric and only report EM with explicit Dicta-compatible normalization. Agents reporting raw EM understate every model's performance.
- Hebrew Winograd has fewer than 300 items. Any single run has high variance. Report results only with multiple runs and standard deviations. Agents that run it once and treat the result as gospel will flip model rankings between runs.
- AI21 Jamba uses a dedicated API (ai21.com or Amazon Bedrock). Do not assume the OpenAI SDK works with it. Use the AI21 Python SDK or Bedrock runtime.
- Translation BLEU on Hebrew is less reliable than BLEU on European languages due to Hebrew morphology. Report chrF alongside BLEU and spot-check low-scoring outputs manually. Agents that rely on BLEU alone miss the actual quality signal.
- DictaLM base models are not chat-tuned by default. Comparing them zero-shot against chat models like Claude is unfair. Use the Dicta instruction-tuned variants (Nemotron-12B-Instruct, dictalm2.0-instruct) or use few-shot prompting with explicit task examples.
- Tokenizer fertility skews cost and latency comparisons. A vanilla BPE model can use 3-5x more tokens per Hebrew word than a Hebrew-tuned SentencePiece tokenizer. Always log tokens-in/tokens-out per benchmark, not just sample count.
- LLM-as-judge for Hebrew is biased toward English-style answers (long, hedged) over native Israeli style (direct, terse). Use at least two judges from different vendors, calibrate against 30-50 human ratings, and prefer reference-based metrics where they exist.
- HEBREW-MMLU has multiple community translations and forks. Verify the active dataset ID before publishing a benchmark; numbers from different translations are not comparable.

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
