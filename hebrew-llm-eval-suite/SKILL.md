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
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | Sentiment classification (positive, negative, neutral). 43,645 rows. License `other` (not CC-BY-4.0), so check the card before commercial use | Social media analysis, review classification, product feedback |
| Hebrew Winograd | Community port of Winograd Schema Challenge (`cs.ubc.ca/~vshwartz/resources/winograd_he.jsonl`) | Pronoun resolution requiring world knowledge. Reasoning-heavy | Any product that needs nuanced Hebrew understanding |
| NeuLabs-TedTalks (translation) | OPUS NeuLab-TedTalks en-he subset | English to Hebrew and Hebrew to English translation quality | Translation products, multilingual apps |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural Language Inference in Hebrew | Classification, content moderation, logical reasoning |
| Hebrew MMLU | `CohereLabs/Global-MMLU`, config `he` | General-knowledge accuracy; the Hebrew split of Global-MMLU. Shipped as the native `global_mmlu` task in lm-evaluation-harness, so this is the reproducible route. (`openai/MMMLU` covers 14 languages and Hebrew is NOT among them) | General-purpose chat/RAG products that need broad world knowledge in Hebrew |
| DictaLM 3.0 Summarization | Dicta benchmark suite (see DictaLM 3.0 technical report) | Abstractive summarization of Hebrew news | Summarization tools, executive briefings |
| DictaLM 3.0 Nikud | Dicta benchmark suite | Adding vowel diacritics to unvocalized Hebrew | Educational tools, TTS preprocessing, religious text tools |
| DictaLM 3.0 Israeli Trivia | Dicta benchmark suite | Knowledge of Israeli culture, geography, history, politics. 300 questions | Consumer products where cultural grounding matters |
| AlephBench | `HebArabNlpProject/AlephBench` | 11 Hebrew tasks with frozen prompts and per-row model outputs, published by the same body that runs the leaderboard. License CC-BY-4.0 | The closest thing to a reproducible, single-repo Hebrew benchmark. Start here if you want frozen prompts |
| Grounding / abstention | `HebArabNlpProject/asmachta`, `HebArabNlpProject/abstractive-qa-llm-eval` | Attributed QA where a deliberate share of questions is unanswerable, so you measure hallucination-vs-abstention directly | Hebrew RAG and support bots, where a confident wrong answer is the expensive failure |
| Long-context NLI | `HebArabNlpProject/LCHAIM` | Hebrew NLI over long contexts | Products that reason over long Hebrew documents |
| Hebrew summarization | `HebArabNlpProject/HebSummaries` | Human-annotated Hebrew summarization | Downloadable alternative to the DictaLM Summarization task, whose data is not published as a dataset |

Rule of thumb: start with HeQ (comprehension) plus one task that matches your specific product. Adding benchmarks past three rarely changes the decision. For products that need broad world knowledge, add the Hebrew split of Global-MMLU.

The Open Hebrew LLM Leaderboard itself scores six tasks, not four: SNLI Accuracy, QA TLNLS (HeQ), Sentiment Accuracy, Winograd Binary Accuracy, Translation BLEU, and Israeli Trivia. If your goal is leaderboard parity, match that set. Note that the leaderboard's sentiment split is an early Mafat/NNLP-IL subset and is NOT the same data as the `HebArabNlpProject/HebrewSentiment` card, so scores from the two are not comparable.

#### Recommended frameworks

Wrap the benchmarks above in an established eval framework rather than rolling a runner from scratch:

- **`lm-evaluation-harness` (EleutherAI)**: standard for reproducible base-model evals, used by the HuggingFace Open LLM Leaderboard. HeQ, HebrewSentiment, and HebNLI are NOT shipped as native tasks (re-checked 2026-08-19; there is no Hebrew task directory in the repo), so add them as custom YAML tasks pointing at the HF dataset IDs above. The one exception is Hebrew MMLU, which IS native via the `global_mmlu` task. Good fit when comparing open-weight models with consistent few-shot prompting.
- **`inspect_ai` (UK AI Security Institute)**: opinionated framework with primitives for dataset, Task, Solver, and Scorer, plus multi-turn agent flows and a log viewer. Adopted by Anthropic, DeepMind, and others through 2024-25. Good fit for chat-model evals and graded scoring. Companion repo `UKGovernmentBEIS/inspect_evals` ships 171 pre-built evals; Hebrew tasks are not in the default set but the harness is straightforward to extend.

Pick `lm-evaluation-harness` for base-model leaderboard parity, pick `inspect_ai` for chat-model and agent evals.

### Step 2: Pick the models to compare

A sensible default set for Israeli product teams:

| Provider | Model | Call via |
|----------|-------|----------|
| Anthropic | `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`, and `claude-fable-5` for the most demanding tasks | Anthropic SDK |
| OpenAI | `gpt-5.6` family (`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`) | OpenAI SDK |
| Google | `gemini-3.7-flash` (current flagship), `gemini-3.5-flash`, `gemini-2.5-pro`. `gemini-3-pro-preview` and `gemini-3-flash-preview` exist but are preview-only, so do not pin a published scorecard to them | Google GenAI SDK |
| AI21 (Israeli) | `jamba-large` and `jamba-mini` (the unversioned aliases, currently resolving to `jamba-large-1.7-2025-07` and `jamba-mini-2-2026-01`); pin `jamba-large-1.7` or `jamba-mini-2` for a reproducible scorecard | AI21 SDK or Amazon Bedrock |
| Dicta (Israeli, open-weight) | `dicta-il/DictaLM-3.0-24B-Base`, `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct`, `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF`, `dicta-il/DictaLM-3.0-24B-Thinking`, plus `dicta-il/dictalm2.0-instruct` (DictaLM 2.0, 7B Mistral-based) | HuggingFace transformers or vLLM |
| Cohere (multilingual, Hebrew supported) | `CohereLabs/aya-expanse-8b`, `CohereLabs/aya-expanse-32b`, `CohereLabs/aya-23-8B`, `CohereLabs/aya-23-35B` | HuggingFace transformers or Cohere API |
| Hebrew-finetuned community models | `yam-peleg/Hebrew-Mistral-7B`, `yam-peleg/Hebrew-Gemma-11B-Instruct`, `yam-peleg/Hebrew-Mixtral-8x22B` | HuggingFace transformers |
| Meta (open-weight) | Llama-3.x-70B-Instruct | HuggingFace transformers or hosted |
| Mistral (open-weight) | Mistral-Large-Instruct | HuggingFace transformers or hosted |

AI21 documents Hebrew in the supported-language list on the Jamba 1.5 and 1.6 model cards. The 1.7 cards are access-gated and the Jamba2 cards carry no language field, so do not assert Hebrew support for anything past 1.6 without checking the card yourself. DictaLM is the strongest Hebrew-native open-weight option. Cohere's Aya-23 and Aya Expanse list Hebrew among their supported languages. Yam Peleg's Hebrew-* community models are continuously pretrained from Mistral, Gemma, and Mixtral with extended Hebrew tokenizers. Include at least one Hebrew-native model as a baseline, or the comparison tells you nothing about Hebrew-specific performance.

### Step 3: Set up the harness

Use `scripts/run_eval.py` as the runner. It loads benchmarks from HuggingFace, calls the configured model endpoints, and writes results to disk.

```bash
pip install datasets transformers anthropic openai google-genai ai21

export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export AI21_API_KEY=...

python scripts/run_eval.py --benchmark heq --model claude-sonnet-5 --limit 100
python scripts/run_eval.py --suite hebrew-core --models claude-sonnet-5,gpt-5.6,jamba-large
```

The harness uses few-shot prompting for base models and chat format for hosted models. Prompt templates live in `references/prompt-templates.md`; the per-benchmark prompt builder and scorers are inside `scripts/run_eval.py` and `scripts/score_results.py` themselves.

`run_eval.py` ships as a working skeleton, not a finished product. Read it before trusting a scorecard: `--benchmark` currently dispatches only `heq`, `sentiment`, and `hebnli`; local HuggingFace models raise `NotImplementedError`; and there is no retry, no backoff, and no parallelism, so a provider rate limit will surface as a raw SDK exception. Add those before running a large sweep.

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

A single run on a small subset is not a benchmark. Two different uncertainties are in play and the smaller one is the one people measure.

**Sampling error over examples is the dominant term, and one run already gives it to you.** Re-running the same 1,000 examples three times measures only decoding noise. It does not tell you how much the score would move if you had drawn a different 1,000 examples, which is the uncertainty that actually matters when you generalize to your product. Compute a bootstrap confidence interval by resampling the per-example scores of a single run (10,000 resamples is plenty), and report the interval, not just the mean.

Scale discipline matters most on the small sets. Hebrew Winograd has 278 items, so the binomial confidence interval at the conventional level is roughly plus or minus 6 accuracy points. A mean and standard deviation over 3 reruns on that set will print as plus or minus 1 and convey precision that is not there.

- Report a confidence interval per benchmark, not just a mean
- Run each model at least 3 times to capture decoding noise, and report the standard deviation as a separate number from the sampling CI
- Use at least 500 examples per benchmark, ideally 1,000+, and state n next to every score
- Compare models on the SAME examples and use a paired test (McNemar for accuracy, a paired bootstrap for F1). Comparing two independent means throws away the pairing and needs a much larger gap to reach significance
- Before declaring a regression or a winner, state the minimum detectable effect at your n. A fixed rule like "flag any 2-point drop" is meaningless without it: at n=278 two points is noise, at n=6,510 one point can be real
- Pin sampling parameters across models. Set temperature explicitly rather than inheriting each SDK's default, or you are comparing models at different temperatures
- Log seeds where applicable
- Use the same prompt template across models unless you are deliberately comparing prompt strategies
- For HeQ, report F1 per question type (answerable vs unanswerable) separately
- For translation, use BLEU and chrF together because each metric has failure modes

`scripts/run_eval.py --runs 3 --samples 1000` executes the repeat runs and writes one result file per run. It does NOT aggregate them: the mean and standard deviation are computed later by `make_scorecard.py`, so score the whole set of run files together rather than one at a time.

### Step 7: Handle closed-source model caveats

API-hosted models change silently. Log the exact model version string from each API response where available. For Claude, note that current model IDs carry NO date suffix: `claude-opus-5` is the complete, pinnable ID and appending a date produces an invalid model. Record the `model` field returned in the response, which is the authoritative record of what actually served the request. For OpenAI, log the `model` field from the response and the `system_fingerprint` when available. For Gemini, log the `modelVersion` from the response metadata. This makes historical scorecards reproducible.

The bundled runner does NOT do this for you. `call_model()` returns only the response text and discards the response object, so the result files record the model string you REQUESTED, not the one that served the request, and no token usage or fingerprint at all. If you need a scorecard that survives procurement scrutiny, change `call_model()` to return the full response and persist the returned model ID, the usage block, and your sampling parameters alongside each run. Pin the dataset too: pass a `revision=` to `load_dataset` and record the split actually used, since a dataset card update silently changes your numbers.

### Step 8: Account for tokenizer fairness

Tokenizer differences materially affect Hebrew evals on cost, latency, and even task accuracy:

- **BPE tokenizers** (GPT-4, Llama-3, Mistral) treat Hebrew as a long-tail language. Fertility (tokens per Hebrew word) is typically 3-5x higher than English. A 1,000-Hebrew-word prompt can balloon to 4,000-5,000 tokens.
- **SentencePiece tokenizers with Hebrew extensions** (DictaLM 2.0/3.0, Hebrew-Mistral-7B, Hebrew-Gemma-11B) inject Hebrew-specific tokens. DictaLM 2.0 reports compression of 2.76 tokens/Hebrew-word vs Mistral-7B's 5.78 tokens/word.
- **Aya/Cohere tokenizers** are tuned for the 23 supported languages including Hebrew, with fertility closer to native-tuned models than to vanilla BPE.

Implications for evals:
- Always log tokens-in and tokens-out per benchmark, not just sample count, when comparing cost or latency
- A model with worse raw F1 but 3x better tokenizer fertility may still be the right pick for a cost-sensitive product
- Models with high fertility hit context limits sooner; truncate fairly across the comparison set
- Size the output budget for the most expensive model in the set, not the cheapest. A reasoning model spends its budget on reasoning before emitting a visible answer, so a tight `max_tokens` returns an empty string that scores as a wrong answer rather than as a configuration error. Comparing a model with reasoning enabled against one without is a category error in the first place: either disable it everywhere or match the effort setting across the set

Report a "fertility table" alongside the scorecard: model, mean tokens per Hebrew word on the same reference paragraph (use a fixed sample such as the first 1,000 words of the HeQ test set). No bundled script computes this. For open-weight models, run each model's own tokenizer over the sample and divide token count by word count. For API-hosted models where the tokenizer is not published, use the provider's token-counting endpoint on that same sample rather than a local approximation, since a third-party tokenizer will not match.

### Step 9: Normalize Hebrew text before scoring

HeQ scoring already calls Dicta-compatible normalization. Sentiment, NLI, and translation evals also need normalization or you will see artificial losses:

- **Strip nikud (vowel diacritics)** before string comparison. Reference labels and model outputs may differ only in nikud presence. Use the Unicode range U+05B0-U+05BC, U+05BD, U+05BF, U+05C1-U+05C2, U+05C7 plus the cantillation marks U+0591-U+05AF.
- **Normalize sofit (final) forms** for HeQ EM and string-match scorers: כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ. Replace the final-form variant with its base form on both sides.
- **Collapse whitespace** including non-breaking space U+00A0 and zero-width joiner U+200D, and strip the Hebrew geresh/gershayim U+05F3-U+05F4, which Python's `string.punctuation` does not cover because they are not ASCII.
- **Convert the maqaf U+05BE to a space, do not delete it.** It is a word-joining hyphen, so deleting it turns `תל־אביב` into `תלאביב`, which then fails to match the spaced form and silently costs you a correct answer. It also sits inside the nikud codepoint range, so it must be handled before the nikud strip or the range will swallow it.
- **Lowercase Latin script** for translation outputs but leave Hebrew untouched (Hebrew has no case).
- **For sentiment and NLI**, model outputs can be a label word in nikud or with definite article. Apply nikud strip plus prefix-removal for ה־ before mapping to the label vocabulary.

`scripts/score_results.py --normalize hebrew` is the only normalization mode the bundled scorer implements, and it covers nikud stripping, sofit folding, and whitespace collapsing. Prefix removal and the translation-safe variant described above are NOT implemented; add them to `normalize_hebrew()` in `scripts/score_results.py` if your eval needs them, and do not apply sofit folding to translation outputs where it would change meaning.

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

### Step 11: Guard against benchmark contamination

Every benchmark in Step 1 is public, old, and mostly Wikipedia-derived. HeQ is built on Hebrew Wikipedia and Geektime, Global-MMLU translates a corpus that has been in every crawl for years, Israeli Trivia is 300 published questions, and Hebrew Winograd is a public JSONL on a university web server. A frontier model's score on any of them is partly a memorization measurement, and the whole point of this skill is to produce a number you can defend in procurement.

This cuts against the skill's own advice in one place worth naming: the Hebrew-native open-weight models you are told to include as a baseline are trained heavily on Hebrew Wikipedia, which is exactly what HeQ is built from. They are among the most exposed to contamination, not the least.

What to do:

- **Build a private held-out set from your own Hebrew production data and make it the decision anchor.** 100 to 200 examples scored well beats 1,000 examples of a public benchmark that may be in the training data. Demote the public benchmarks to sanity checks that catch gross failures.
- **Never publish your private set**, not in a repo, not in an appendix, not to a model provider's logging-enabled endpoint. The moment it is public it starts decaying.
- **Probe for memorization** on the public sets before trusting a surprisingly high score. Give the model a prefix of a benchmark passage and ask it to continue: verbatim continuation of a passage it should not know is a strong contamination signal. Compare performance on data published before and after a model's stated training cutoff, where the provider states one.
- **Treat a leaderboard ranking as evidence about the leaderboard**, not purely about Hebrew ability. Models whose training corpora ingested the leaderboard data rank higher for reasons unrelated to the quality you are buying.
- **Re-validate on a cadence.** Record the date, the dataset revision, and the model IDs with every scorecard, and re-run before reusing a number older than a couple of model releases.


## Examples

### Example 1: Choosing a summarization model for a Hebrew news product

User says: "We are building a Hebrew news summary feature and need to pick between Claude, GPT, and DictaLM."

Actions:
1. Recognize what the bundled harness can and cannot score. There is no summarization scorer in `scripts/`, so a summarization decision cannot be made from the bundled suites alone. Use `--suite hebrew-core` for a general Hebrew-competence signal and score summarization separately.
2. Run `python scripts/run_eval.py --suite hebrew-core --models claude-sonnet-5,gpt-5.6 --samples 1000 --runs 3`. Note that `DictaLM-3.0-24B-Base` is an open-weight model: the bundled runner raises `NotImplementedError` for it rather than scoring it, so serve it yourself with vLLM and score its outputs through the same `score_results.py`. Passing it to the runner directly records an error for every example, which the scorer now reports as an error count rather than as a score of zero.
3. Build a held-out set of 100 to 200 of the team's OWN Hebrew news articles with human reference summaries. This, not the public benchmark, is the decision anchor (see Step 11)
4. Score summarization on that private set with human raters or a calibrated judge, and report a confidence interval
5. Pick based on the private-set result, with the public scorecard as a sanity check, plus cost and latency

Result: A model choice anchored on your own data, with a reproducible public-benchmark scorecard alongside it.

### Example 2: Tracking Hebrew regression after a provider upgrade

User says: "Anthropic just released a new model version. Did Hebrew quality improve or regress?"

Actions:
1. Re-run the standard suite against the new version and the previous version
2. Compare the two scorecard JSON files produced by `make_scorecard.py`, per benchmark. No bundled script diffs them
3. Flag any benchmark with more than 2 points drop as a regression
4. File a product decision (stay on old, move to new, A/B)

Result: Informed upgrade decision instead of blind follow-the-provider.

## Bundled Resources

### Scripts
- `scripts/run_eval.py` -- Main harness. Loads benchmarks from HuggingFace, calls model endpoints, writes raw outputs to disk. Run: `python scripts/run_eval.py --help`
- `scripts/score_results.py` -- Loads raw outputs and computes metrics with Hebrew-specific normalization. Implements HeQ (F1, exact match, unanswerable accuracy) and the two classification tasks (accuracy, macro-recall). It does NOT implement BLEU, chrF, ROUGE, or BERTScore; those benchmarks fall through to a "no scorer" branch and you must add them. Run: `python scripts/score_results.py --help`
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
| AlephBench dataset | https://huggingface.co/datasets/HebArabNlpProject/AlephBench | 11 Hebrew tasks with frozen prompts, from the body that runs the leaderboard |
| Global-MMLU (Hebrew split) | https://huggingface.co/datasets/CohereLabs/Global-MMLU | Hebrew MMLU config `he`; native `global_mmlu` task in lm-evaluation-harness |
| Anthropic model list | https://docs.claude.com/en/docs/about-claude/models/overview | Current Claude model IDs. They carry no date suffix |
| OpenAI model list | https://developers.openai.com/api/docs/models | Current OpenAI model IDs |
| Google Gemini model list | https://ai.google.dev/gemini-api/docs/models | Current Gemini model IDs, and which are preview-only |
| AI21 Jamba model list | https://docs.ai21.com/docs/jamba-foundation-models | Current Jamba API IDs and what the unversioned aliases resolve to |
| Dicta organization on HuggingFace | https://huggingface.co/dicta-il | Latest DictaLM 3.0 variants (24B-Base, Nemotron-12B-Instruct, 1.7B-Thinking-GGUF, 24B-Thinking) and DictaBERT models |
| Cohere Aya organization | https://huggingface.co/CohereLabs | Aya-23 (8B/35B) and Aya Expanse (8B/32B) multilingual models with Hebrew support |
| Yam Peleg Hebrew models | https://huggingface.co/yam-peleg | Hebrew-Mistral-7B, Hebrew-Gemma-11B-Instruct, Hebrew-Mixtral-8x22B community finetunes |
| AI21 Jamba model card (Hebrew in supported languages) | https://huggingface.co/ai21labs/AI21-Jamba-Mini-1.5 | Jamba Hebrew support and model specs |
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
- Hebrew MMLU has multiple community translations and forks, and numbers from different translations are not comparable. Pin `CohereLabs/Global-MMLU` config `he` (or state which fork you used) before publishing a benchmark. Agents that say "MMLU Hebrew" without naming the fork produce a number nobody can reproduce.
- `HebArabNlpProject/HebrewSentiment` is licensed `other`, not CC-BY-4.0, so it does not carry blanket commercial-use permission. Read the card before shipping a commercial eval on it. Its dataset card frontmatter also still says `private: true`, which is stale: the repo API reports `gated: false, private: false` and an anonymous read succeeds. Trust the API over the card field.
- The gold label in `HebrewSentiment` is in a field called `tag_ids`, NOT `label`, and its values are `Positive`/`Negative`/`Neutral` in title case. A scorer that reads `example["label"]` and compares against uppercase strings matches nothing, skips every row, and reports 0.0 for every model. `score_results.py` now probes a candidate list of label fields and refuses to emit a score when nothing was scorable, but any harness you write yourself needs the same guard.
- Model IDs in this skill go stale faster than anything else in it. Before every published run, re-check each provider's current model list, and record the ID the API actually returned rather than the one you requested. Anthropic IDs take no date suffix, so appending one produces an invalid model rather than a pinned snapshot.
- `scripts/score_results.py` scores whatever it can parse and returns 0.0 for the rest rather than raising. Its input contract is `{"benchmark": ..., "outputs": [{"example": ..., "response": ...}]}`, exactly as `run_eval.py` writes it. Hand-built or reshaped files with different key names score a clean, plausible 0.0 across every model. If a whole run scores zero, suspect the file shape before you conclude the models failed.
- `scripts/run_eval.py` is a reference skeleton: serial calls, no retry, no backoff, no local-model inference. It is fine for a 100-example smoke test and will fall over on a 1,000-example three-run sweep. Agents that treat it as production-ready will report a partial run as a complete one.

## Troubleshooting

### Error: "Rate limited by provider"
Cause: Your quota is lower than the request rate, or a prior run left a burst in flight.
Solution: `run_eval.py` issues calls serially and implements NO retry or backoff. Critically, the run does NOT die: `run_one()` catches every exception and writes the string `__ERROR__: ...` as that example's response, so you get a full-length, structurally valid result file in which the rate-limited examples are failures. `score_results.py` now excludes those from the score and reports them as `num_errored`, so check that field on every run. Wrap `call_model()` in the provider SDK's retry helper (or a simple exponential backoff) before a large sweep, and lower `--limit` while you tune. There is no `--parallel` flag.

### Error: "HeQ EM score is near zero for all models"
Cause: Exact match normalization is not applied. Hebrew whitespace, nikud, and sofit variations cause false negatives.
Solution: Use F1 as the primary metric. Apply normalization via `scripts/score_results.py --normalize hebrew`, which is the only mode implemented.

### Error: "Translation BLEU tells the opposite story from human raters"
Cause: BLEU is unreliable on Hebrew due to morphology.
Solution: Use chrF alongside BLEU. Rate a sample of the lowest-scoring outputs manually.
