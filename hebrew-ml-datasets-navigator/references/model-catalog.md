# Hebrew and Yiddish ML Model Catalog

Curated catalog of Hebrew and Yiddish machine learning models available as of 2026. Always verify the current model card before production use.

## Hebrew ASR (Speech-to-Text)

### ivrit.ai Whisper family

Organization: `huggingface.co/ivrit-ai`

| Model | HuggingFace ID | Variant | Use case |
|-------|---------------|---------|----------|
| whisper-large-v3 | `ivrit-ai/whisper-large-v3` | Full precision | Research, maximum accuracy |
| whisper-large-v3-ct2 | `ivrit-ai/whisper-large-v3-ct2` | CTranslate2-optimized | Fast inference (CPU/GPU) |
| whisper-large-v3-turbo-ct2 | `ivrit-ai/whisper-large-v3-turbo-ct2` | Turbo + CT2 | Production latency, most popular |
| whisper-large-v3-ggml | `ivrit-ai/whisper-large-v3-ggml` | GGML-quantized | Consumer hardware, CPU inference |
| whisper-large-v3-turbo-onnx | `ivrit-ai/whisper-large-v3-turbo-onnx` | ONNX | Cross-platform serving |
| whisper-v2-d3-e3 | `ivrit-ai/whisper-v2-d3-e3` | Older variant | Backward compatibility |

Selection guide:
- For production with latency constraints: `whisper-large-v3-turbo-ct2`
- For highest accuracy (non-real-time): `whisper-large-v3`
- For CPU-only or edge: `whisper-large-v3-ggml`

## Yiddish ASR

| Model | HuggingFace ID | Variant |
|-------|---------------|---------|
| yi-whisper-large-v3 | `ivrit-ai/yi-whisper-large-v3` | Full precision |
| yi-whisper-large-v3-ct2 | `ivrit-ai/yi-whisper-large-v3-ct2` | CT2-optimized |
| yi-whisper-large-v3-turbo | `ivrit-ai/yi-whisper-large-v3-turbo` | Turbo, smaller |

## Speaker Diarization

| Model | HuggingFace ID | Task |
|-------|---------------|------|
| pyannote-speaker-diarization-3.1 | `ivrit-ai/pyannote-speaker-diarization-3.1` | Hebrew-tuned speaker diarization |

Pair with ivrit.ai ASR for multi-speaker transcription (interviews, podcasts, meetings).

## Hebrew LLMs

### DictaLM 3.0 family

Organization: `huggingface.co/dicta-il`

| Model | HuggingFace ID | Size | Type | Base |
|-------|---------------|------|------|------|
| DictaLM-3.0-24B-Base | `dicta-il/DictaLM-3.0-24B-Base` | 24B | Base | Mistral-Small-3.1 |
| DictaLM-3.0-24B-Base-FP8 | `dicta-il/DictaLM-3.0-24B-Base-FP8` | 24B | Base (FP8 quant) | Mistral-Small-3.1 |
| DictaLM-3.0-24B-Thinking | `dicta-il/DictaLM-3.0-24B-Thinking` | 24B | Reasoning | Mistral-Small-3.1 |
| DictaLM-3.0-Nemotron-12B-Instruct | `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` | 12B | Instruct | NVIDIA Nemotron Nano V2 |
| DictaLM-3.0-Nemotron-12B-Base | `dicta-il/DictaLM-3.0-Nemotron-12B-Base` | 12B | Base | NVIDIA Nemotron Nano V2 |
| DictaLM-3.0-1.7B-Thinking-GGUF | `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF` | 1.7B | Reasoning (quantized) | Qwen3-1.7B |

Selection guide:
- Highest quality: 24B-Thinking or 24B-Base
- Balanced: Nemotron-12B-Instruct (best for instruction-following)
- Consumer hardware: 1.7B-Thinking-GGUF

License note: each variant inherits from its upstream base model. Mistral license, NVIDIA license, Qwen license apply respectively. Check the model card before commercial use.

### AI21 Jamba (Israeli, hosted)

Organization: AI21 Labs

| Model | Access | Hebrew support |
|-------|--------|----------------|
| jamba-1.6-large | AI21 SDK or Amazon Bedrock | Core language support per AI21 |
| jamba-1.6-mini | AI21 SDK or Amazon Bedrock | Core language support per AI21 |
| jamba-reasoning-3b | Open weights on Hugging Face | Compact reasoning model |
| jamba-1.5-large | Legacy SDK and Bedrock | Predecessor of 1.6 |
| jamba-1.5-mini | Legacy SDK and Bedrock | Predecessor of 1.6 |

AI21 markets Hebrew as a "core language" for the Jamba family, making it a relevant option for Hebrew-first products. The 3B reasoning model is the most accessible self-hostable Jamba variant.

## Hebrew BERT Models

### DictaBERT family

Organization: `huggingface.co/dicta-il`

| Model | HuggingFace ID | Task | Notes |
|-------|---------------|------|-------|
| dictabert | `dicta-il/dictabert` | Fill-mask | Baseline Hebrew BERT |
| dictabert-seg | `dicta-il/dictabert-seg` | Word segmentation | Hebrew morpheme splitting |
| dictabert-morph | `dicta-il/dictabert-morph` | Morphological analysis | POS, features |
| dictabert-heq | `dicta-il/dictabert-heq` | Question answering | Fine-tuned on HeQ |
| dictabert-sentiment | `dicta-il/dictabert-sentiment` | Sentiment classification | Fine-tuned on HebrewSentiment |
| dictabert-ner | `dicta-il/dictabert-ner` | Named entity recognition | Fine-tuned for Hebrew NER. Recognizes PER, GPE, TIMEX, TTL. CC-BY-4.0. |

### Other Hebrew BERT models

| Model | Source | Notes |
|-------|--------|-------|
| AlephBERT | `onlplab/alephbert-base` | Earlier Hebrew BERT, still used for embedding/similarity |
| HeBERT | Community | Earlier generation, emotion-focused |

## Hebrew Embeddings

| Model | HuggingFace ID | Dimensionality | Notes |
|-------|---------------|----------------|-------|
| neodictabert-bilingual-embed | `dicta-il/neodictabert-bilingual-embed` | Per card | Hebrew-English bilingual, recommended |
| multilingual-e5-large | `intfloat/multilingual-e5-large` | 1024 | General multilingual, includes Hebrew |

## Selection guide by task

| Task | Start with | Fine-tune on |
|------|------------|--------------|
| Hebrew sentiment | `dicta-il/dictabert-sentiment` (use directly) | HebrewSentiment + your data |
| Hebrew QA | `dicta-il/dictabert-heq` (use directly) | HeQ + your data |
| Hebrew NER | `dicta-il/dictabert` | Your labeled NER data |
| Hebrew ASR | `ivrit-ai/whisper-large-v3-turbo-ct2` | Your domain audio |
| Hebrew instruction LLM | `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` | Your instruction pairs (LoRA recommended) |
| Hebrew base LLM | `dicta-il/DictaLM-3.0-24B-Base` | Your pre-training data |
| Hebrew embeddings | `dicta-il/neodictabert-bilingual-embed` | Your paired data |
| Yiddish ASR | `ivrit-ai/yi-whisper-large-v3` | Your Yiddish audio |
| Multi-speaker transcription | `ivrit-ai/whisper-large-v3` + `ivrit-ai/pyannote-speaker-diarization-3.1` | Domain fine-tuning optional |

## Adding a new model

When a new Hebrew or Yiddish model is released, add it with:
1. Full HuggingFace ID
2. Task or capability
3. Parameter count
4. Base model (if adapted)
5. License and commercial use notes
6. Training data summary (if published)
