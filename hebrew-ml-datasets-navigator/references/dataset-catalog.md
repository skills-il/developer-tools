# Hebrew and Yiddish ML Dataset Catalog

Curated catalog of Hebrew and Yiddish machine learning datasets available as of 2026. Always verify on the dataset card before use.

## Speech (Audio + Transcripts)

### ivrit.ai family

Organization: `huggingface.co/ivrit-ai`

| Dataset | HuggingFace ID | Language | Size | Use case |
|---------|---------------|----------|------|----------|
| crowd-transcribe-v5 | `ivrit-ai/crowd-transcribe-v5` | Hebrew | Large-scale (part of 22K+ hours total) | ASR training, latest crowd-sourced |
| crowd-transcribe-v4 | `ivrit-ai/crowd-transcribe-v4` | Hebrew | Previous version | Backward compatibility |
| crowd-recital | `ivrit-ai/crowd-recital` | Hebrew | Crowd recital audio | High-quality Hebrew audio |
| audio-v2 | `ivrit-ai/audio-v2` | Hebrew | Bulk Hebrew audio | Pre-training or large-scale fine-tuning |
| audio-v2-40s | `ivrit-ai/audio-v2-40s` | Hebrew | 40-second clips | Easier chunked processing |
| audio-v2-opus | `ivrit-ai/audio-v2-opus` | Hebrew | Opus-encoded variant | Smaller file size for bulk processing |
| crowd-whatsapp-yi | `ivrit-ai/crowd-whatsapp-yi` | Yiddish | Text | Yiddish written corpus |
| crowd-recital-yi | `ivrit-ai/crowd-recital-yi` | Yiddish | Audio | Yiddish speech training |
| Knesset Plenums | via `ivrit-ai` spaces | Hebrew | Large | Political speech, formal Hebrew |

License posture: permissive, commercial use explicitly allowed per ivrit.ai's stated mission. Confirm on each dataset card before production use.

## Text (Classification, Inference, QA)

### Israeli National NLP Program (HebArabNlpProject)

Organization: `huggingface.co/HebArabNlpProject`

| Dataset | HuggingFace ID | Task | Size | License |
|---------|---------------|------|------|---------|
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | Sentiment (3-class) | Check dataset card (split across train/validation/test) | Check dataset card |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural language inference | Check card | Check card |

### Hebrew Question Answering

| Dataset | Source | Task | Size | License |
|---------|--------|------|------|---------|
| HeQ | `pig4431/HeQ_v1` (HF), `NNLP-IL/Hebrew-Question-Answering-Dataset` (GitHub canonical) | Extractive QA | 30,147 questions (21,784 answerable + 8,363 unanswerable) | Check dataset card |

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
