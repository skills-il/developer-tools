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
| Hebrew LLM pre-training | Large Hebrew text corpus | Dicta's corpora, MADLAD-400 Hebrew subset, OSCAR Hebrew, Hebrew Wikipedia, Knesset Plenums |
| Hebrew LLM instruction tuning | Prompt-response pairs in Hebrew | Dicta instruction datasets, translated Alpaca-style datasets, custom |
| Reading comprehension / QA | Text + Q&A pairs | HeQ (`pig4431/HeQ_v1`) |
| Sentiment classification | Hebrew text + labels | HebrewSentiment (`HebArabNlpProject/HebrewSentiment`) |
| Natural language inference | Hebrew premise-hypothesis pairs | HebNLI (`HebArabNlpProject/HebNLI`) |
| Named entity recognition | Hebrew text + entity tags | Dicta NER datasets, historical NNLP-IL releases |
| Morphological analysis | Hebrew text + morph tags | Dicta morph datasets |
| Diacritization (nikud) | Unvocalized + vocalized Hebrew | Dicta nikud datasets |
| Paraphrase detection | Hebrew text pairs | NNLP-IL Hebrew paraphrase dataset (9,750 pairs) |
| Hebrew-English translation | Parallel corpora | NeuLabs-TedTalks, OPUS Hebrew subsets |
| Yiddish ASR | Yiddish audio + transcripts | ivrit.ai Yiddish models (yi-whisper) and crowd datasets |
| Yiddish text | Yiddish corpora | ivrit.ai crowd-whatsapp-yi, crowd-recital-yi |

### Step 2: Key organizations and what they publish

Bookmark and subscribe to updates from these organizations. They are the authoritative sources for Hebrew ML.

#### ivrit.ai (`huggingface.co/ivrit-ai`)

Non-profit focused on Hebrew speech resources. As of 2025-2026 they host the world's largest public Hebrew audio corpus (22,000+ hours) under permissive licenses that explicitly allow commercial training.

Key artifacts:
- `ivrit-ai/crowd-transcribe-v5` — latest crowd-sourced Hebrew ASR dataset
- `ivrit-ai/crowd-recital` — Hebrew audio with careful recital
- `ivrit-ai/audio-v2` and `audio-v2-opus` — bulk Hebrew audio corpus
- `ivrit-ai/whisper-large-v3` — Hebrew-tuned Whisper ASR (full precision)
- `ivrit-ai/whisper-large-v3-ct2` — CTranslate2-optimized for fast inference
- `ivrit-ai/whisper-large-v3-turbo-ct2` — turbo variant, fastest
- `ivrit-ai/whisper-large-v3-ggml` — GGML-quantized for CPU inference
- `ivrit-ai/pyannote-speaker-diarization-3.1` — Hebrew-tuned speaker diarization
- `ivrit-ai/yi-whisper-large-v3` — Yiddish ASR
- Knesset Plenums dataset — Hebrew parliamentary speeches (large-scale)

License posture: permissive, commercial use explicitly allowed. Always check the specific dataset card for attribution requirements.

#### Dicta: The Israel Center for Text Analysis (`huggingface.co/dicta-il`)

The leading Hebrew LLM and BERT organization in Israel. Publishes both base and instruction-tuned models plus BERT variants for downstream tasks.

Key artifacts:
- `dicta-il/DictaLM-3.0-24B-Base` — flagship Hebrew base LLM (Mistral-adapted)
- `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` — instruction-tuned mid-size
- `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF` — small model with reasoning, runnable on consumer hardware
- `dicta-il/dictabert` — baseline Hebrew BERT (fill-mask)
- `dicta-il/dictabert-seg` — Hebrew word segmentation
- `dicta-il/dictabert-morph` — Hebrew morphological analysis
- `dicta-il/dictabert-heq` — fine-tuned for Hebrew reading comprehension
- `dicta-il/dictabert-sentiment` — Hebrew sentiment classification
- `dicta-il/neodictabert-bilingual-embed` — Hebrew-English sentence embeddings

License posture: check each model card individually. Many permit commercial use but with attribution. DictaLM 3.0 sizes derive from different base models (Mistral, Nemotron, Qwen) which inherit their upstream licenses.

#### Israeli National NLP Program (`huggingface.co/HebArabNlpProject`)

National initiative for Hebrew and Arabic NLP infrastructure, sponsored by DDR&D IMOD and supported by Dicta and Webiks.

Key artifacts:
- `HebArabNlpProject/HebrewSentiment` — 41,305 labeled Hebrew sentiment samples, CC-BY-4.0
- `HebArabNlpProject/HebNLI` — Hebrew natural language inference
- Paraphrase datasets, NER datasets, and other Hebrew benchmarks

License posture: generally permissive with CC-BY-4.0 or similar. Most are commercial-friendly with attribution.

#### NNLP-IL on GitHub (`github.com/NNLP-IL`)

Resource curation and benchmark dataset hosting.

Key repositories:
- `NNLP-IL/Hebrew-Resources` — comprehensive list of Hebrew NLP datasets, models, tools
- `NNLP-IL/Hebrew-Question-Answering-Dataset` — HeQ source repo
- `NNLP-IL/NNLP-IL` — program meta-repository

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

## Examples

### Example 1: Training a Hebrew customer support sentiment model

User says: "We need to classify sentiment in Hebrew customer support messages for a commercial SaaS product."

Actions:
1. Task: sentiment classification on conversational Hebrew
2. Check `HebArabNlpProject/HebrewSentiment` — 41,305 samples, CC-BY-4.0, includes some spoken register. Commercial use OK with attribution.
3. Check `dicta-il/dictabert-sentiment` as a ready baseline before fine-tuning anything
4. Start with the Dicta sentiment model and evaluate on a held-out set of real customer support chats
5. If the baseline is insufficient, fine-tune `dicta-il/dictabert` on HebrewSentiment + your labeled data
6. Document attribution in the product (About page or release notes)

Result: Data-backed model selection plus compliant attribution.

### Example 2: Building a Hebrew podcast transcription product

User says: "We want to transcribe Hebrew podcasts for a new product. Which ASR model should we start with?"

Actions:
1. Task: Hebrew speech-to-text on conversational audio
2. Check ivrit.ai models — `whisper-large-v3` family is SOTA for Hebrew ASR
3. For production latency, use `whisper-large-v3-turbo-ct2` (CTranslate2-optimized)
4. For diarized podcasts (multi-speaker), pair with `pyannote-speaker-diarization-3.1`
5. Verify ivrit.ai's permissive license allows commercial use — it does, by design
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
| Dicta organization | https://huggingface.co/dicta-il | DictaLM 3.0 family, DictaBERT variants |
| Dicta website | https://dicta.org.il | Publications, DictaLM 3.0 technical report |
| Israeli National NLP Program | https://huggingface.co/HebArabNlpProject | Hebrew and Arabic benchmarks |
| NNLP-IL Hebrew Resources index | https://github.com/NNLP-IL/Hebrew-Resources | Comprehensive curated list |
| Hebrew-Question-Answering-Dataset | https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset | HeQ source and methodology |
| Open Hebrew LLM Leaderboard | https://huggingface.co/blog/leaderboard-hebrew | Benchmark methodology, leaderboard |

## Gotchas

- "Hebrew dataset" is not a single thing. Register (modern, religious, spoken, academic) matters more than total size. A 10GB modern-news corpus is useless for a religious-text product. Agents often quote dataset size without checking register alignment.
- ivrit.ai uses a bespoke permissive license that explicitly allows commercial use. Many agents default to citing CC-BY-NC out of habit for scraped audio. Read the specific ivrit.ai dataset card.
- DictaLM 3.0 comes in multiple sizes derived from DIFFERENT base models (Mistral, Nemotron, Qwen). Upstream licenses differ. Do not assume one license applies to all DictaLM variants. Check each model card.
- HeQ's primary metric should be F1, not Exact Match. Hebrew morphology and sofit forms make EM brittle. Agents reporting raw EM on HeQ understate model performance systematically.
- Yiddish and Hebrew share an alphabet but are DIFFERENT languages with different models. Do not train a Hebrew model on Yiddish data or vice versa without explicit cross-lingual transfer planning. ivrit.ai maintains separate `yi-whisper` models for exactly this reason.
- The dataset `pig4431/HeQ_v1` is a community-maintained HuggingFace mirror. The canonical source is `NNLP-IL/Hebrew-Question-Answering-Dataset` on GitHub. Verify current versioning before publishing benchmark results.

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
