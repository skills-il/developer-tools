---
name: hebrew-ml-datasets-navigator
description: "Navigate the fragmented landscape of Hebrew and Yiddish ML datasets and models. Covers ivrit.ai (22K+ hours of Hebrew audio, whisper-large-v3 ASR variants, Yiddish models), Dicta (DictaLM 3.0 LLM family, DictaBERT variants, HeQ reading comprehension), the Israeli National NLP Program / NNLP-IL (HebrewSentiment, HebNLI), AlephBERT, and Knesset Plenums. Helps researchers and ML engineers pick the right dataset for a task by use case, license (commercial vs research), Hebrew register coverage, and model-dataset pairing. Use when choosing training data for a Hebrew NLP or ASR project, verifying license compatibility for a commercial product, finding a baseline model for a Hebrew downstream task, or exploring Yiddish ML resources. Do NOT use for Arabic NLP datasets (a separate ecosystem), general HuggingFace dataset discovery (use HuggingFace Hub search), or Hebrew OCR dataset selection (use hebrew-ocr-forms)."
license: MIT
---

# Hebrew ML Datasets Navigator

## Problem

The Israeli ML community punches above its weight, but the datasets and models are scattered. ivrit.ai publishes world-class Hebrew speech corpora on one HuggingFace org, Dicta publishes Hebrew LLMs and BERT variants on another, the Israeli National NLP Program maintains benchmarks under `HebArabNlpProject`, and classic resources like AlephBERT live elsewhere. Licenses vary from fully commercial-friendly to research-only. Hebrew register coverage varies dramatically: some corpora are all modern standard, others are half religious texts, others are spoken colloquial. A researcher trying to pick the right combination for "fine-tune a Hebrew sentiment classifier on customer support chat for a commercial product" has to hunt across five orgs and read every dataset card to understand what they can actually use.

## Instructions

### Step 1: Identify the task

Different Hebrew ML tasks need different datasets. Match your task to a dataset family before searching.

| Task | Primary data type | Dataset families to check first |
|------|-------------------|--------------------------------|
| Speech-to-text (Hebrew ASR) | Audio + transcripts | ivrit.ai (crowd-transcribe, crowd-recital, audio-v2) |
| Text-to-speech (Hebrew TTS) | Text + studio audio | Public-domain audio with permissive licenses (limited; often requires custom recording) |
| Hebrew LLM pre-training | Large Hebrew text corpus | Dicta's corpora, `allenai/MADLAD-400` Hebrew subset, `oscar-corpus/OSCAR-2301` Hebrew, `uonlp/CulturaX` Hebrew slice, `HuggingFaceFW/fineweb-2` `heb_Hebr` filter, mC4 (Hebrew quality is weak), Hebrew Wikipedia, Knesset Plenums |
| Hebrew LLM instruction tuning | Prompt-response pairs in Hebrew | Dicta instruction datasets, translated Alpaca-style datasets, custom |
| Reading comprehension / QA | Text + Q&A pairs | HeQ (`Etelis/HeQ_v1` HF mirror, canonical at `github.com/NNLP-IL/Hebrew-Question-Answering-Dataset`); `omrikeren/ParaShoot` (~3K few-shot QA examples) |
| Sentiment classification | Hebrew text + labels | HebrewSentiment (`HebArabNlpProject/HebrewSentiment`) |
| Natural language inference | Hebrew premise-hypothesis pairs | HebNLI (`HebArabNlpProject/HebNLI`) |
| Named entity recognition | Hebrew text + entity tags | Dicta NER datasets, historical NNLP-IL releases |
| Morphological analysis | Hebrew text + morph tags | Dicta morph datasets |
| Diacritization (nikud) | Unvocalized + vocalized Hebrew | Dicta nikud datasets |
| Paraphrase detection | Hebrew text pairs | NNLP-IL Hebrew paraphrase dataset (9,750 pairs) |
| Summarization | Hebrew article + summary | `biunlp/HeSum` (10K article-summary pairs from Hebrew news, BIU NLP), `HebArabNlpProject/HebSummaries` |
| General knowledge benchmarking | MCQ + answers | HEBREW-MMLU (Hebrew-translated MMLU subset; verify the active HF mirror, multiple community translations exist) |
| Hebrew-English translation | Parallel corpora | NeuLabs-TedTalks, OPUS Hebrew subsets |
| Yiddish ASR | Yiddish audio + transcripts | ivrit.ai Yiddish models (yi-whisper) and crowd datasets |
| Yiddish text | Yiddish corpora | ivrit.ai crowd-whatsapp-yi, crowd-recital-yi |

### Step 2: Key organizations and what they publish

Bookmark and subscribe to updates from these organizations. They are the authoritative sources for Hebrew ML.

#### ivrit.ai (`huggingface.co/ivrit-ai`)

Non-profit focused on Hebrew speech resources. As of 2025-2026 they host the world's largest public Hebrew audio corpus (22,000+ hours) under permissive licenses that explicitly allow commercial training.

Key artifacts:
- `ivrit-ai/crowd-transcribe-v5` ,  latest crowd-sourced Hebrew ASR dataset
- `ivrit-ai/crowd-recital` ,  Hebrew audio with careful recital
- `ivrit-ai/audio-v2` and `audio-v2-opus` ,  bulk Hebrew audio corpus
- `ivrit-ai/whisper-large-v3` ,  Hebrew-tuned Whisper ASR (full precision)
- `ivrit-ai/whisper-large-v3-ct2` ,  CTranslate2-optimized for fast inference
- `ivrit-ai/whisper-large-v3-turbo-ct2` ,  turbo variant, fastest
- `ivrit-ai/whisper-large-v3-ggml` ,  GGML-quantized for CPU inference
- `ivrit-ai/pyannote-speaker-diarization-3.1` ,  Hebrew-tuned speaker diarization
- `ivrit-ai/yi-whisper-large-v3` ,  Yiddish ASR
- Knesset Plenums dataset ,  Hebrew parliamentary speeches (large-scale)

License posture: permissive, commercial use explicitly allowed. Always check the specific dataset card for attribution requirements.

#### Dicta: The Israel Center for Text Analysis (`huggingface.co/dicta-il`)

The leading Hebrew LLM and BERT organization in Israel. Publishes both base and instruction-tuned models plus BERT variants for downstream tasks.

Key artifacts (verified on huggingface.co/dicta-il):
- `dicta-il/DictaLM-3.0-24B-Base` ,  flagship Hebrew base LLM (24B, Mistral-adapted)
- `dicta-il/DictaLM-3.0-24B-Thinking` ,  reasoning-tuned 24B variant
- `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` ,  instruction-tuned mid-size (12B, Nemotron base)
- `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF` ,  small reasoning model, runnable on consumer hardware
- Quantized variants for production: `*-FP8`, `*-W4A16`, `*-GGUF` (e.g. `DictaLM-3.0-Nemotron-12B-Instruct-FP8`, `DictaLM-3.0-24B-Thinking-GGUF`)
- `dicta-il/dictalm2.0-instruct` ,  previous generation, 7B Mistral-7B-based, instruct fine-tuned (Zephyr recipe). Also `dictalm2.0-instruct-GGUF`, `-AWQ`, `-GPTQ`
- `dicta-il/dictabert` ,  baseline Hebrew BERT (fill-mask)
- `dicta-il/dictabert-seg` ,  Hebrew word segmentation
- `dicta-il/dictabert-morph` ,  Hebrew morphological analysis
- `dicta-il/dictabert-heq` ,  fine-tuned for Hebrew reading comprehension
- `dicta-il/dictabert-sentiment` ,  Hebrew sentiment classification
- `dicta-il/neodictabert-bilingual-embed` ,  Hebrew-English sentence embeddings

License posture: check each model card individually. Many permit commercial use but with attribution. DictaLM 3.0 sizes derive from different base models (Mistral for the 24B, NVIDIA Nemotron for the 12B, smaller variants vary) which inherit their upstream licenses.

#### Israeli National NLP Program (`huggingface.co/HebArabNlpProject`)

National initiative for Hebrew and Arabic NLP infrastructure, sponsored by DDR&D IMOD and supported by Dicta and Webiks.

Key artifacts:
- `HebArabNlpProject/HebrewSentiment` ,  labeled Hebrew sentiment samples across train/validation/test splits; check the dataset card for current license and exact sample counts before commercial use
- `HebArabNlpProject/HebNLI` ,  Hebrew natural language inference
- Paraphrase datasets, NER datasets, and other Hebrew benchmarks

License posture: generally permissive with CC-BY-4.0 or similar. Most are commercial-friendly with attribution.

#### NNLP-IL on GitHub (`github.com/NNLP-IL`)

Resource curation and benchmark dataset hosting.

Key repositories:
- `NNLP-IL/Hebrew-Resources` ,  comprehensive list of Hebrew NLP datasets, models, tools
- `NNLP-IL/Hebrew-Question-Answering-Dataset` ,  HeQ source repo
- `NNLP-IL/HebNLI` ,  HebNLI source repo
- `NNLP-IL/NNLP-IL` ,  program meta-repository

#### Multilingual web-scale corpora with Hebrew slices

Use these for LLM pre-training when you need scale that no Hebrew-only corpus can provide. Always filter to the Hebrew-script subset and re-deduplicate against your domain data.

- `uonlp/CulturaX` ,  6.3T tokens across 167 languages, combining mC4 v3.1.0 with OSCAR releases through 2023-01. Heavy cleaning and deduplication. Pull the Hebrew subset by language code. Apache 2.0 (terms tied to the underlying mC4/OSCAR licenses; check before commercial training).
- `HuggingFaceFW/fineweb-2` ,  ~20TB across 1,868 language-script pairs. Hebrew available as `heb_Hebr`. Higher-quality filtering than CulturaX. Sourced from CommonCrawl 2013 to April 2024.
- `allenai/MADLAD-400` ,  document-level multilingual corpus across 419 languages. Two variants: noisy (LangID only) and clean (filtered). Hebrew is included; pull by language code.
- `oscar-corpus/OSCAR-2301` ,  CommonCrawl-derived multilingual corpus, Hebrew slice available. Note `OSCAR-2301` is gated behind a HuggingFace agreement; request access on the dataset page before using.
- `mC4` (Hebrew slice) ,  not deprecated, but the Hebrew partition has been criticized for noisier text and weaker filtering than newer corpora. Prefer FineWeb-2 or CulturaX where you can.

Always re-tokenize and re-deduplicate when combining corpora; CulturaX already incorporates mC4 + OSCAR through 2023, so layering them on top creates substantial duplication.

### Step 3: License compatibility by use case

Pick the most-permissive license that meets your commercial needs.

| Your product | Licenses you can use | Avoid |
|--------------|----------------------|-------|
| Commercial SaaS / product | CC-BY-4.0, MIT, Apache 2.0, ivrit.ai permissive license, Dicta commercial-friendly | CC-BY-NC, GPL (unless your product is GPL), any "research only" |
| Research publication | Any license that permits distribution for research (most) | Datasets under NDA or closed-source |
| Internal prototype (non-distributed) | Very permissive, research-allowed covers most needs | Check carefully if prototype becomes a product |
| Government / defense | Depends on contract terms; may require sovereign-safe data | Data with uncertain provenance or scraped PII |

Always read the specific dataset card. Licenses change. HuggingFace dataset cards are the authoritative source for current licensing.

### Step 4: Hebrew register and demographic coverage

A "Hebrew dataset" is not homogeneous. Before training on it, understand what kind of Hebrew is represented.

| Register | Typical sources | When it matters |
|----------|-----------------|-----------------|
| Modern standard written | Wikipedia, news sites, Geektime | General-purpose LLMs, search, summarization |
| Spoken / colloquial | Podcasts, YouTube, WhatsApp corpora | Conversational AI, voice interfaces, customer support |
| Academic / formal | Dicta academic corpora, legal texts | Legal, scientific, government applications |
| Religious / classical | Tanakh, Talmud, rabbinic texts | Religious tools, historical text processing |
| Knesset plenary speech | Parliamentary records (via ivrit.ai) | Political NLP, civic tech, sentiment on public discourse |
| Mixed Hebrew-English | Tech discussions, code-switching corpora | Startup-facing products, developer tools |

A customer-support chatbot trained only on Wikipedia will feel robotic. A religious-text model trained only on spoken podcasts will miss the entire target domain. Match register to use case.

### Step 5: Pair datasets with models

For many tasks, the best approach is to use a published model as a starting point and fine-tune on your task-specific data. Model-dataset pairings that work well:

| Task | Starting model | Fine-tune on | Notes |
|------|----------------|--------------|-------|
| Sentiment | `dicta-il/dictabert` | `HebArabNlpProject/HebrewSentiment` | Dicta published `dictabert-sentiment` using exactly this recipe |
| QA / reading comprehension | `dicta-il/dictabert` | `pig4431/HeQ_v1` | Dicta published `dictabert-heq` using exactly this recipe |
| Hebrew ASR | `ivrit-ai/whisper-large-v3` | Your domain-specific audio | Use the turbo-ct2 variant in production for latency |
| Yiddish ASR | `ivrit-ai/yi-whisper-large-v3` | Your Yiddish audio | Tight niche; limited data |
| Hebrew LLM instruction-following | `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` | Your instruction pairs | Use LoRA to save compute |
| Hebrew sentence embeddings | `dicta-il/neodictabert-bilingual-embed` | Your pairs | Strong Hebrew-English bilingual baseline |

### Step 6: Verify before training

Before committing compute to fine-tuning:

1. Confirm the dataset exists at the HuggingFace ID you are using
2. Read the dataset card fully (especially license, limitations, known biases)
3. Check the sample count and splits; verify the test split is held out
4. For audio datasets, listen to a few samples and verify quality
5. For text datasets, read a few samples and verify the register matches your target
6. Check the license compatibility for your specific commercial use
7. Identify attribution requirements and plan how to comply

### Step 7: Missing benchmarks for Hebrew

The Hebrew NLP ecosystem has gaps. Note that the DictaLM 3.0 release (Feb 2026) shipped its own benchmark suite covering Translation, Summarization, Winograd-style schemas, Israeli Trivia, and Hebrew Diacritization, narrowing the gap for those tasks. The list below is what is still missing as of May 2026: if your task is in this list, expect to either build evaluation data yourself or pair the closest existing benchmark with domain-specific human evaluation.

- **Hebrew safety / red-team evals** ,  no public Hebrew counterpart to ToxicChat, HarmBench. Build internal red-team prompts.
- **Hebrew code generation** ,  no Hebrew-language docstring or comment benchmark. Use English HumanEval/MBPP and accept the language mismatch.
- **Hebrew long-context evals** ,  no Hebrew Needle-in-a-Haystack or LongBench. Construct internally from Hebrew Wikipedia or Knesset transcripts.
- **Hebrew tool-use / function-calling** ,  no public Hebrew benchmark. Translate BFCL prompts to Hebrew if needed.
- **Hebrew preference / RLHF data** ,  scarce. Most Hebrew-aligned preference signal is private (Dicta, AI21, Hebrew-Mistral teams).
- **Spoken Hebrew dialogue evals** ,  ivrit.ai covers ASR but there is no public dialogue-quality benchmark. Build internal eval from real conversations.
- **Hebrew multimodal (vision-language)** ,  almost nothing public. Document understanding for Hebrew documents is largely covered only by commercial OCR + translation pipelines.

Known to exist but limited:
- **HEBREW-MMLU** ,  Hebrew-translated MMLU referenced by the Open Hebrew LLM Leaderboard ecosystem; multiple community translations exist with different qualities. Verify the active mirror before publishing comparable numbers. `openai/MMMLU` covers 14 languages but Hebrew is not in that official set.
- **Hebrew Winograd** ,  community port of Winograd Schema Challenge, fewer than 300 items. High variance in single-run evals.

### Step 8: Academic Hebrew NLP resources

Beyond ivrit.ai, Dicta, and the Israeli National NLP Program, several university labs release Hebrew NLP work that is worth tracking:

- **BIU NLP Lab (Bar-Ilan University)** ,  group behind HeSum (`biunlp/HeSum`), original AlephBERT, and many Hebrew tagging benchmarks. Papers and resources at `nlp.biu.ac.il`.
- **Open University of Israel** ,  Hebrew corpora and historical text resources (e.g. Knesset corpora prior to ivrit.ai's release).
- **Technion / NLPH Lab** ,  Hebrew NLP papers, Hebrew tokenization and morphology research.
- **Hebrew University of Jerusalem (HUJI)** ,  Open University collaborations on Hebrew syntax, morphology, and historical Hebrew. The original Winograd-HE port (vshwartz) traces back here.
- **Reichman University / IDC NLP** ,  occasional Hebrew benchmark releases tied to industry collaborations.

Tracking strategy: subscribe to the `NNLP-IL/Hebrew-Resources` repo for community curation; for primary releases follow the labs' own pages and the authors on Hugging Face.

## Examples

### Example 1: Training a Hebrew customer support sentiment model

User says: "We need to classify sentiment in Hebrew customer support messages for a commercial SaaS product."

Actions:
1. Task: sentiment classification on conversational Hebrew
2. Check `HebArabNlpProject/HebrewSentiment` ,  Hebrew sentiment samples across train/validation/test, includes some spoken register. Verify the current license posture on the dataset card before relying on it for commercial use.
3. Check `dicta-il/dictabert-sentiment` as a ready baseline before fine-tuning anything
4. Start with the Dicta sentiment model and evaluate on a held-out set of real customer support chats
5. If the baseline is insufficient, fine-tune `dicta-il/dictabert` on HebrewSentiment + your labeled data
6. Document attribution in the product (About page or release notes)

Result: Data-backed model selection plus compliant attribution.

### Example 2: Building a Hebrew podcast transcription product

User says: "We want to transcribe Hebrew podcasts for a new product. Which ASR model should we start with?"

Actions:
1. Task: Hebrew speech-to-text on conversational audio
2. Check ivrit.ai models ,  `whisper-large-v3` family is SOTA for Hebrew ASR
3. For production latency, use `whisper-large-v3-turbo-ct2` (CTranslate2-optimized)
4. For diarized podcasts (multi-speaker), pair with `pyannote-speaker-diarization-3.1`
5. Verify ivrit.ai's permissive license allows commercial use ,  it does, by design
6. Plan attribution per the dataset card
7. Consider fine-tuning on a small set of your own podcast audio if domain mismatch is significant

Result: Launch-ready ASR stack with the right open-weight models and clear licensing.

## Bundled Resources

### Scripts
- `scripts/find_dataset.py` -- Interactive dataset finder. Filters the curated catalog by task, license, register, and Hebrew/Yiddish/mixed. Prints recommended datasets with HuggingFace IDs and license notes. Run: `python scripts/find_dataset.py --help`

### References
- `references/dataset-catalog.md` -- Comprehensive catalog of Hebrew and Yiddish datasets with HuggingFace IDs, license info, sample counts, and register notes. Consult when picking datasets.
- `references/model-catalog.md` -- Comprehensive catalog of Hebrew and Yiddish models (ASR, LLM, BERT, embeddings, diarization) with HuggingFace IDs, parameter counts, and intended use. Consult when picking a starting model.
- `references/license-quick-guide.md` -- Plain-English summary of the most common licenses in the Hebrew ML ecosystem and what they allow for commercial use. Consult when evaluating license compatibility.

## Recommended MCP Servers

No MCP server is required for navigating datasets. Pair with the HuggingFace Hub for actual downloads.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| ivrit.ai organization | https://huggingface.co/ivrit-ai | Latest Hebrew ASR models, datasets, diarization |
| ivrit.ai website | https://www.ivrit.ai/en/ivrit-ai-2/ | Mission, licensing posture, announcements |
| Dicta organization | https://huggingface.co/dicta-il | DictaLM 3.0 family (24B-Base, Nemotron-12B-Instruct, 1.7B-Thinking-GGUF, 24B-Thinking), DictaLM 2.0, DictaBERT variants |
| Dicta website | https://dicta.org.il | Publications, DictaLM 3.0 technical report |
| Israeli National NLP Program | https://huggingface.co/HebArabNlpProject | HebrewSentiment, HebNLI, HebSummaries, and other benchmarks |
| NNLP-IL Hebrew Resources index | https://github.com/NNLP-IL/Hebrew-Resources | Comprehensive curated list |
| Hebrew-Question-Answering-Dataset | https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset | HeQ source and methodology |
| HeQ on HuggingFace (mirror) | https://huggingface.co/datasets/Etelis/HeQ_v1 | HF mirror of HeQ for direct loading |
| HeSum dataset | https://huggingface.co/datasets/biunlp/HeSum | Hebrew abstractive summarization, 10K article-summary pairs (BIU NLP) |
| ParaShoot | https://github.com/omrikeren/ParaShoot | Hebrew SQuAD-style QA, ~3K few-shot examples |
| CulturaX | https://huggingface.co/datasets/uonlp/CulturaX | Multilingual pre-training corpus, Hebrew slice via language code |
| FineWeb-2 | https://huggingface.co/datasets/HuggingFaceFW/fineweb-2 | Multilingual web corpus, Hebrew at `heb_Hebr` |
| MADLAD-400 | https://huggingface.co/datasets/allenai/MADLAD-400 | Document-level multilingual corpus, Hebrew supported |
| OSCAR-2301 | https://huggingface.co/datasets/oscar-corpus/OSCAR-2301 | CommonCrawl-derived multilingual, Hebrew slice (gated; request access) |
| Open Hebrew LLM Leaderboard (live space) | https://huggingface.co/spaces/hebrew-llm-leaderboard/leaderboard | Live rankings, current benchmark scores |
| Open Hebrew LLM Leaderboard (announcement) | https://huggingface.co/blog/leaderboard-hebrew | Benchmark methodology |
| BIU NLP Lab | https://nlp.biu.ac.il | Bar-Ilan academic Hebrew NLP releases (HeSum, AlephBERT origins) |

## Gotchas

- "Hebrew dataset" is not a single thing. Register (modern, religious, spoken, academic) matters more than total size. A 10GB modern-news corpus is useless for a religious-text product. Agents often quote dataset size without checking register alignment.
- ivrit.ai uses a bespoke permissive license that explicitly allows commercial use. Many agents default to citing CC-BY-NC out of habit for scraped audio. Read the specific ivrit.ai dataset card.
- DictaLM 3.0 comes in multiple sizes derived from DIFFERENT base models (Mistral, Nemotron, Qwen). Upstream licenses differ. Do not assume one license applies to all DictaLM variants. Check each model card.
- HeQ's primary metric should be F1, not Exact Match. Hebrew morphology and sofit forms make EM brittle. Agents reporting raw EM on HeQ understate model performance systematically.
- Yiddish and Hebrew share an alphabet but are DIFFERENT languages with different models. Do not train a Hebrew model on Yiddish data or vice versa without explicit cross-lingual transfer planning. ivrit.ai maintains separate `yi-whisper` models for exactly this reason.
- The HuggingFace HeQ mirrors (`pig4431/HeQ_v1`, `Etelis/HeQ_v1`) are community-maintained. The canonical source is `NNLP-IL/Hebrew-Question-Answering-Dataset` on GitHub. Verify current versioning before publishing benchmark results.
- Layering CulturaX on top of mC4 + OSCAR-2301 introduces heavy duplication. CulturaX already incorporates mC4 v3.1.0 and OSCAR through 2023-01. Either pick one corpus, or de-dup explicitly (sha256 of normalized text) before training.
- mC4 is NOT deprecated, but its Hebrew slice has weaker filtering than FineWeb-2 or CulturaX. If you need pre-2024 web Hebrew, prefer CulturaX over raw mC4.
- HEBREW-MMLU references float around with multiple community translations and forks. Verify the active dataset ID before publishing benchmark results; numbers from different translations are not directly comparable. `openai/MMMLU` covers 14 languages but Hebrew is not included in that official set.
- DictaLM 3.0 release naming includes both base/thinking/instruct families AND quantization variants (FP8, W4A16, GGUF). When citing benchmark results, log the exact model ID from the HF page including any quantization suffix; numbers do not transfer across quantizations.
- `oscar-corpus/OSCAR-2301` is gated on HuggingFace. Plan for access approval before training pipelines that depend on it.

## Troubleshooting

### Error: "Dataset license is unclear or changed"
Cause: HuggingFace dataset cards can be updated, and licenses occasionally change.
Solution: Use the current dataset card as the authoritative source. When in doubt, email the dataset owner listed on HuggingFace. Do not rely on outdated blog posts or cached summaries.

### Error: "Model fine-tuned on HeQ fails on real-world Hebrew"
Cause: HeQ paragraphs come from Wikipedia and Geektime, which skew formal. Real-world chat or spoken Hebrew may perform worse.
Solution: Add domain-specific training data. HeQ is a benchmark, not a universal training set. For chatbot-style Hebrew, augment with conversational data.

### Error: "Attribution requirements are unclear"
Cause: Different datasets have different attribution clauses.
Solution: Read the LICENSE and CITATION files in the dataset. For HuggingFace datasets, the dataset card includes a "Citation" section. Include required attribution in your product documentation.
