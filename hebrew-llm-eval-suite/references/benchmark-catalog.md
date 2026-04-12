# Hebrew LLM Benchmark Catalog

Complete catalog of Hebrew LLM benchmarks used by this skill, with HuggingFace IDs, licenses, sample counts, and prompt template notes.

## Open Hebrew LLM Leaderboard benchmarks

The Open Hebrew LLM Leaderboard is hosted by HuggingFace in collaboration with DDR&D IMOD (Israeli National Program for NLP in Hebrew and Arabic), DICTA, and Webiks.

### HeQ (Hebrew Question Answering)

- HuggingFace ID: `pig4431/HeQ_v1`
- Original paper: Cohen et al., "HeQ: a Large and Diverse Hebrew Reading Comprehension Benchmark", EMNLP Findings 2023
- Source: `https://aclanthology.org/2023.findings-emnlp.915.pdf`
- Repository: `https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset`
- Sample count: 30,147 questions total
  - Answerable: 21,784 (answer present in paragraph)
  - Unanswerable: 8,363 (question related to paragraph but answer not present)
- Sources of paragraphs: Hebrew Wikipedia and Geektime (Israeli tech news)
- Format: SQuAD-style extractive QA
- Primary metric: F1 (not Exact Match, which is brittle on Hebrew)
- Secondary: Accuracy on unanswerable subset
- Normalization: strip nikud, normalize sofit forms, collapse whitespace before scoring

Gotcha: treating Exact Match as the primary metric gives near-zero scores even on correct answers due to Hebrew morphology.

### HebrewSentiment

- HuggingFace ID: `HebArabNlpProject/HebrewSentiment`
- Creator: Israel National NLP Program
- License: CC-BY-4.0
- Sample count: 41,305 total
  - Train: 39,135 (positive 8,968, negative 7,669, neutral 22,498)
  - Test: 2,170 (positive 503, negative 433, neutral 1,234)
- Labels: Positive, Negative, Neutral
- Primary metric: Accuracy
- Secondary: Macro-F1 (important because of class imbalance)
- Paired DictaBERT model: `dicta-il/dictabert-sentiment`

### Hebrew Winograd Schema Challenge

- Source: translation of the original Winograd Schema Challenge by Dr. Vered Schwartz
- Sample count: under 300 items (exact count varies by version)
- Format: pronoun resolution with two candidate antecedents
- Primary metric: Accuracy
- High variance on single runs due to small dataset. Always report with standard deviation from multiple runs.

### NeuLabs-TedTalks Translation

- Source: NeuLabs-TedTalks aligned parallel corpus
- Used by: Open Hebrew LLM Leaderboard
- Format: sentence-pair translation (English to Hebrew and Hebrew to English)
- Primary metrics: BLEU, chrF
- Optional: human preference rating
- BLEU on Hebrew underestimates quality due to morphology. Always pair with chrF.

## DictaLM 3.0 benchmark suite

Dicta introduced a dedicated chat-LLM benchmark suite for DictaLM 3.0 covering Translation, Summarization, Winograd, Israeli Trivia, and Diacritization (Nikud).

Source: DictaLM 3.0 Technical Report at `https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf`

### Summarization

- Task: abstractive summarization of Hebrew news articles
- Primary metric: ROUGE-L
- Secondary: BERTScore-HE (a Hebrew-tuned BERTScore variant) or human preference
- Gotcha: ROUGE is unreliable for abstractive tasks. Human preference correlates better with quality but is expensive.

### Nikud (Diacritization)

- Task: add vowel diacritics (nikud) to unvocalized Hebrew text
- Primary metric: Word Accuracy (full word diacritization correct)
- Secondary: Character Accuracy
- Use case: TTS, educational tools, religious text processing

### Israeli Trivia

- Task: knowledge questions about Israeli culture, geography, history, politics, sports, music
- Primary metric: Accuracy
- Secondary: per-category breakdown
- Use case: any consumer-facing Hebrew product that needs cultural grounding

## Additional Hebrew datasets (not in the default suite)

### HebNLI

- HuggingFace ID: `HebArabNlpProject/HebNLI`
- Task: Natural Language Inference (entailment, contradiction, neutral)
- Use case: logical reasoning, content moderation

### HeBERT Emotion

- Task: fine-grained emotion classification beyond polarity
- Use case: mental health chatbots, customer emotion detection

### Hebrew-Resources index

- GitHub: `https://github.com/NNLP-IL/Hebrew-Resources`
- Comprehensive listing of Hebrew NLP resources maintained by the Israeli National NLP Program. Check periodically for new benchmarks.

## Licensing summary

| Benchmark | License | Commercial use | Attribution |
|-----------|---------|----------------|-------------|
| HeQ | CC-BY (confirm current version) | Yes | Required |
| HebrewSentiment | CC-BY-4.0 | Yes | Required |
| Hebrew Winograd | Non-commercial (verify per port) | Check | Required |
| NeuLabs-TedTalks | CC-BY-NC-ND | Non-commercial only | Required |
| DictaLM suite | Dicta terms (permissive for research) | Check per dataset | Required |
| HebNLI | CC-BY (confirm) | Yes | Required |

Always check the current license on the dataset card before commercial use. Licenses change.

## Running a new benchmark

To add a benchmark to this catalog:

1. Confirm the dataset exists on HuggingFace or a stable source
2. Check and document the license
3. Add a scorer to `scripts/score_results.py` with appropriate normalization
4. Add a prompt template to `references/prompt-templates.md`
5. Register it in `scripts/run_eval.py` benchmark dispatch
6. Verify with a baseline model (DictaLM-3.0) and sanity-check the score against published results
