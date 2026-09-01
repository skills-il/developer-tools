# Hebrew and Yiddish ML Dataset Catalog

Curated catalog of Hebrew and Yiddish machine learning datasets available as of 2026. Always verify on the dataset card before use.

## Speech (Audio + Transcripts)

### ivrit.ai family

Organization: `huggingface.co/ivrit-ai`

| Dataset | HuggingFace ID | Language | Size | Use case |
|---------|---------------|----------|------|----------|
| crowd-transcribe-v5 | `ivrit-ai/crowd-transcribe-v5` | Hebrew | Large-scale (part of 20K+ hours total) | ASR training, latest crowd-sourced |
| crowd-transcribe-v4 | `ivrit-ai/crowd-transcribe-v4` | Hebrew | Previous version | Backward compatibility |
| crowd-recital | `ivrit-ai/crowd-recital` | Hebrew | Crowd recital audio | High-quality Hebrew audio |
| audio-v2 | `ivrit-ai/audio-v2` | Hebrew | Bulk Hebrew audio | Pre-training or large-scale fine-tuning |
| audio-v2-40s | `ivrit-ai/audio-v2-40s` | Hebrew | 40-second clips | Easier chunked processing |
| audio-v2-opus | `ivrit-ai/audio-v2-opus` | Hebrew | Opus-encoded variant | Smaller file size for bulk processing |
| crowd-whatsapp-yi | `ivrit-ai/crowd-whatsapp-yi` | Yiddish | Text | Yiddish written corpus |
| crowd-recital-yi | `ivrit-ai/crowd-recital-yi` | Yiddish | Audio | Yiddish speech training |
| Knesset Plenums (audio) | `ivrit-ai/knesset-plenums` | Hebrew | Large | Political speech, formal Hebrew. Gated, bespoke ivrit.ai licence |
| Knesset Committees (audio) | `ivrit-ai/knesset-committees` | Hebrew | Large | Gated, bespoke ivrit.ai licence |
| VoxKnesset | `ivrit-ai/VoxKnesset` | Hebrew | Large | Longitudinal speech, aging-speaker modelling (arXiv 2603.01270). Gated |
| Knesset Corpus (annotated text) | `HaifaCLGroup/KnessetCorpus` | Hebrew | Large | Academic text corpus (arXiv 2405.18115). `cc-by-sa-4.0`, NOT gated. ShareAlike propagates to derived databases |

License posture: the ivrit.ai licence is bespoke (`license_name: ivrit.ai`, and `ivrit.ai-v2` on at least one dataset), permissive by design and intended to allow commercial training. It is not an OSI licence.

**Gating:** 24 of the 28 ivrit.ai datasets on the Hub are gated with auto-approval (the exceptions as of 2026-09 are `jpress2`, `audio-v2-40s`, `tts-arena-preferences` and `jbd`); the models are not gated. Accept the terms with the same HuggingFace account whose `HF_TOKEN` your trainer uses, and note that accepting is what binds you to the licence.

**Undeclared licences:** `HebArabNlpProject/HebrewSentiment` and `HebNLI` declare `license: other` with no name; `HebSummaries`, `biunlp/HeSum`, `uonlp/CulturaX`, `imvladikon/parashoot` and `ivrit-ai/tts-arena-preferences` declare none at all. An undeclared or unnamed licence is not a grant. Treat it as all rights reserved and ask the depositor.

## Text (Classification, Inference, QA)

### Israeli National NLP Program (HebArabNlpProject)

Organization: `huggingface.co/HebArabNlpProject`

| Dataset | HuggingFace ID | Task | Size | License |
|---------|---------------|------|------|---------|
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | Sentiment (3-class) | Split across train/validation/test; verify totals on the card | `other`, no license_name declared. **Not a grant** |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural language inference | Verify on the card | `other`, no license_name declared. **Not a grant** |

### Hebrew Question Answering

| Dataset | Source | Task | Size | License |
|---------|--------|------|------|---------|
| HeQ | `Etelis/HeQ_v1` (HF), `NNLP-IL/Hebrew-Question-Answering-Dataset` (GitHub canonical) | Extractive QA | 30,147 questions (21,784 answerable + 8,363 unanswerable) | `cc-by-4.0`, not gated |

HeQ paragraphs come from Hebrew Wikipedia and Geektime (Israeli tech news). Register: modern standard written Hebrew.

### Dicta text corpora

Organization: `huggingface.co/dicta-il`

| Dataset | Task | Notes |
|---------|------|-------|
| hebrew-space-restoration-corpus | Space restoration | Unique Hebrew-specific task |
| hebrew_suffix_verbal_forms | Morphological forms | Morph analysis training |
| dictalm2.0-quant-calib-dataset | Quantization calibration | For quantizing DictaLM |
| MathCOT-oss-vs-DeepSeek | Math chain-of-thought | Reasoning comparison, 484k rows |

## Translation

| Dataset | Source | Direction | Notes |
|---------|--------|-----------|-------|
| NeuLabs-TedTalks | Open Hebrew LLM Leaderboard subset | En↔He | Used by the HuggingFace Hebrew LLM Leaderboard |
| OPUS Hebrew corpora | OPUS project | Multiple pairs | Broad coverage, licenses vary per sub-corpus |
| MADLAD-400 Hebrew subset | Google MADLAD-400 | Hebrew as one of 400+ | Pre-training scale |

## Yiddish

Yiddish and Hebrew share an alphabet but are different languages. Do not mix training data.

| Dataset | HuggingFace ID | Type | Language |
|---------|---------------|------|----------|
| crowd-whatsapp-yi | `ivrit-ai/crowd-whatsapp-yi` | Text | Yiddish |
| crowd-recital-yi | `ivrit-ai/crowd-recital-yi` | Audio | Yiddish |

## Register quick reference

| Register | Where to find it |
|----------|-----------------|
| Modern standard | Wikipedia, news, Geektime (HeQ), OSCAR Hebrew |
| Spoken | Podcasts, ivrit.ai audio, crowd-recital |
| Academic | Dicta academic corpora |
| Religious / classical | Tanakh, Talmud, rabbinic (various sources) |
| Parliamentary | ivrit.ai Knesset Plenums |
| Mixed Hebrew-English | Tech and startup communities (scattered) |

## Adding a new dataset to this catalog

When ivrit.ai, Dicta, or NNLP-IL releases a new dataset, add it here with:
1. Full HuggingFace ID
2. Task
3. Size (samples or hours)
4. License
5. Register (modern, spoken, religious, etc.)
6. Any notes on known limitations or biases
