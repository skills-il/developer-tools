# Hebrew LLM Benchmark Catalog

Complete catalog of Hebrew LLM benchmarks used by this skill, with HuggingFace IDs, licenses, sample counts, and prompt template notes.

## Open Hebrew LLM Leaderboard benchmarks

The Open Hebrew LLM Leaderboard is hosted by HuggingFace in collaboration with DDR&D IMOD (Israeli National Program for NLP in Hebrew and Arabic), DICTA, and Webiks.

### HeQ (Hebrew Question Answering)

- HuggingFace ID: `Etelis/HeQ_v1` (the older `pig4431/HeQ_v1` now 307-redirects here after a repo rename)
- Original paper: Cohen et al., "HeQ: a Large and Diverse Hebrew Reading Comprehension Benchmark", EMNLP Findings 2023
- Source: `https://aclanthology.org/2023.findings-emnlp.915.pdf`
- Repository: `https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset`
- Sample count: 30,147 questions total (per the HeQ paper and the dataset card). The answerable / unanswerable split is not stated on either source; count it yourself from the loaded split rather than quoting a figure.
- Sources of paragraphs: Hebrew Wikipedia and Geektime (Israeli tech news)
- Format: SQuAD-style extractive QA
- Primary metric: F1 (not Exact Match, which is brittle on Hebrew)
- Secondary: Accuracy on unanswerable subset
- Normalization: strip nikud, normalize sofit forms, collapse whitespace before scoring

Gotcha: treating Exact Match as the primary metric gives near-zero scores even on correct answers due to Hebrew morphology.

### HebrewSentiment

- HuggingFace ID: `HebArabNlpProject/HebrewSentiment`
- Creator: Israel National NLP Program
- License: `other` (verified on the dataset card 2026-08-19). NOT CC-BY-4.0. Read the card before any commercial use.
- Access: public. The dataset card frontmatter still carries `private: true`, but that field is stale: the repo API reports `gated: false, private: false` and an anonymous `load_dataset` succeeds. Trust the API over the card field.
- Gold label field: `tag_ids`, NOT `label`. Values are `Positive` / `Negative` / `Neutral` in title case. The row schema is `id, task_name, tag_ids, text, campaign_id, annotator_agreement_strength, survey_name, industry, type`. A scorer keyed on `label` matches nothing and silently returns 0.0 for every model.
- Provenance caveat: the rows carry `survey_name` and `industry` fields (market-research surveys, e.g. tobacco), so this is consumer-survey text, not general social media. Check that the domain matches your product before treating a score here as representative.
- Sample count: 43,645 rows total (train 35,135 / validation 2,000 / test 6,510), per the HuggingFace datasets-server size endpoint, 2026-08-19
- Not the same data as the leaderboard's sentiment task, which uses an early Mafat/NNLP-IL subset of 3,000 examples. Scores from the two are not comparable.
- Labels: Positive, Negative, Neutral
- Primary metric: Accuracy
- Secondary: Macro-F1 (important because of class imbalance)
- Paired DictaBERT model: `dicta-il/dictabert-sentiment`

### Hebrew Winograd Schema Challenge

- Source: translation of the original Winograd Schema Challenge by Dr. Vered Schwartz
- File: `https://www.cs.ubc.ca/~vshwartz/resources/winograd_he.jsonl` (verified reachable 2026-08-19)
- Sample count: 278 items, matching the count the leaderboard documents for its Winograd task
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

## AlephBench and the 2026 HebArabNlpProject benchmarks

The same body that runs the Open Hebrew LLM Leaderboard now publishes benchmarks directly as HuggingFace datasets. These are more reproducible than the DictaLM suite, whose task data is described in the technical report but not released as a downloadable dataset.

| Dataset | HuggingFace ID | What it covers |
|---------|---------------|----------------|
| AlephBench | `HebArabNlpProject/AlephBench` | 11 Hebrew tasks, frozen prompts, per-row model outputs, CC-BY-4.0 |
| Asmachta | `HebArabNlpProject/asmachta` | Attributed QA, a deliberate share of questions unanswerable, to measure hallucination vs abstention |
| Abstractive QA eval | `HebArabNlpProject/abstractive-qa-llm-eval` | Grounding records for abstractive Hebrew QA |
| LCHAIM | `HebArabNlpProject/LCHAIM` | Long-context Hebrew NLI |
| HebSummaries | `HebArabNlpProject/HebSummaries` | Human-annotated Hebrew summarization; the downloadable substitute for the DictaLM Summarization task |
| ASAS | `HebArabNlpProject/ASAS` | Short-answer scoring |

## Hebrew MMLU

- HuggingFace ID: `CohereLabs/Global-MMLU`, config `he`
- Shipped as the native `global_mmlu` task in `lm-evaluation-harness`, which makes it the reproducible route to a Hebrew MMLU number
- `openai/MMMLU` covers 14 languages and Hebrew is NOT among them. Do not substitute it.
- Community Hebrew-MMLU forks exist and are not mutually comparable. Always name the fork you scored.

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
- Listing of Hebrew NLP resources from the Israeli National NLP Program. Last pushed 2025-05-11, so treat it as a historical index rather than a current feed. The `HebArabNlpProject` HuggingFace org is where new benchmarks actually land.

## Licensing summary

| Benchmark | License (verified 2026-08-19) | Commercial use | Attribution |
|-----------|------------------------------|----------------|-------------|
| HeQ | `cc-by-4.0` on the `Etelis/HeQ_v1` card | Yes | Required |
| HebrewSentiment | `other` (repo itself is public) | Do NOT assume yes. Read the card | Required |
| AlephBench | `cc-by-4.0` | Yes | Required |
| Hebrew Winograd | Verify per port | Check | Required |
| NeuLabs-TedTalks | CC-BY-NC-ND | Non-commercial only | Required |
| DictaLM suite | Dicta terms; task data not released as a dataset | Check per dataset | Required |
| HebNLI | `other` on the card | Check | Required |

Always check the current license on the dataset card before commercial use. Licenses change.

## Running a new benchmark

To add a benchmark to this catalog:

1. Confirm the dataset exists on HuggingFace or a stable source
2. Check and document the license
3. Add a scorer to `scripts/score_results.py` with appropriate normalization
4. Add a prompt template to `references/prompt-templates.md`
5. Register it in `scripts/run_eval.py` benchmark dispatch
6. Verify with a baseline model (DictaLM-3.0) and sanity-check the score against published results
