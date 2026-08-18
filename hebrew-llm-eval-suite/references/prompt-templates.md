# Hebrew LLM Benchmark Prompt Templates

Zero-shot, few-shot, and chain-of-thought prompt templates per benchmark. Use these as starting points and tune per model when necessary.

## Template design rules

1. Keep instructions in English unless you explicitly want to test Hebrew-instruction-following
2. Provide the Hebrew content in the user turn, not the system prompt, so models that route long text differently handle it the same way
3. Use the same template across all models in a comparison run (unless comparing prompt strategies)
4. Log the exact template used in the scorecard's run config section

## HeQ (extractive question answering)

### Zero-shot

```
System: You are an expert reading-comprehension assistant. Read the Hebrew passage and answer the question. If the answer is not in the passage, respond exactly with UNANSWERABLE.

User:
Passage: {passage}

Question: {question}

Answer (quote exactly from the passage, or UNANSWERABLE):
```

### Few-shot (recommended for base models)

Include 3-5 example passage-question-answer triples before the target question. Use examples from the HeQ train split, not the test split.

### Scoring notes

- Compute F1 between predicted and gold answer after Hebrew normalization (strip nikud, normalize sofit forms, collapse whitespace)
- For unanswerable questions, check whether the model responded with UNANSWERABLE (exact string match, case-insensitive)
- Report F1 and Unanswerable Accuracy separately

## HebrewSentiment (classification)

### Zero-shot

```
System: You are a Hebrew text classifier. Read the text and label its sentiment as POSITIVE, NEGATIVE, or NEUTRAL. Respond with only one word.

User:
Text: {hebrew_text}

Sentiment:
```

### Few-shot

Add 2 examples per class (6 total) before the target text.

### Scoring notes

- Case-insensitive match against gold label
- Compute both overall accuracy and macro-F1 (important due to class imbalance)

## Hebrew Winograd (pronoun resolution)

### Zero-shot

```
System: You are a logical reasoning assistant. Read the Hebrew sentence and determine what the pronoun refers to.

User:
Sentence: {hebrew_sentence}

The pronoun "{pronoun}" refers to which of these? Answer with exactly one:
A) {option_a}
B) {option_b}

Answer (A or B):
```

### Scoring notes

- Binary choice, simple accuracy
- Small dataset (<300 items) requires multiple runs for reliable estimates

## Translation (English to Hebrew or Hebrew to English)

### Zero-shot

```
System: You are a professional translator. Translate the following text accurately and naturally.

User:
Translate this {source_language} text to {target_language}:

{source_text}

Translation:
```

### Scoring notes

- Primary: BLEU (compare to reference)
- Secondary: chrF (more reliable for Hebrew morphology)
- For cross-model comparisons, use the same reference processing pipeline
- Tokenize Hebrew with a language-aware tokenizer before BLEU

## HebNLI (Natural Language Inference)

### Zero-shot

```
System: You are a natural language inference expert. Given a premise and a hypothesis in Hebrew, determine the relationship.

User:
Premise: {hebrew_premise}
Hypothesis: {hebrew_hypothesis}

Does the premise entail, contradict, or have a neutral relationship with the hypothesis?
Answer with one word: ENTAILMENT, CONTRADICTION, or NEUTRAL.

Answer:
```

## Summarization

### Zero-shot

```
System: You are a professional summarizer. Read the Hebrew article and produce a concise summary in Hebrew.

User:
Article:
{hebrew_article}

Write a 3-sentence summary in Hebrew:
```

### Scoring notes

- ROUGE-L against reference summary
- Optional BERTScore-HE for semantic similarity
- Human preference ratings give the most reliable signal for abstractive tasks

## Nikud (Diacritization)

### Zero-shot

```
System: You are a Hebrew diacritization expert. Add full nikud (vowel points) to the Hebrew text. Preserve the exact words and order. Do not add or remove characters except for nikud marks.

User:
Text without nikud:
{unvocalized_hebrew}

Text with nikud:
```

### Scoring notes

- Word accuracy: percentage of words with all nikud marks correct
- Character accuracy: percentage of individual nikud marks correct
- Use Dicta's canonical nikud mapping for normalization

## Israeli Trivia

### Zero-shot

```
System: You are an expert on Israeli culture, geography, history, and current events. Answer the question concisely.

User:
Question: {hebrew_question}

Answer:
```

### Scoring notes

- Exact-match or semantic match (embedding similarity over a threshold) depending on answer type
- Report accuracy by category: culture, geography, history, politics, sports, music

## Chain-of-thought prompts

For models that benefit from CoT (Claude Sonnet, GPT-5, Gemini Pro), prepend:

```
Think step by step before answering, then give your final answer on the last line prefixed with "Final answer:".
```

Extract the line after "Final answer:" as the final response for scoring.

CoT can improve HeQ, Winograd, and Israeli Trivia scores by 3-8 points but costs more tokens. Report both CoT-on and CoT-off when comparing.

## Prompt language: English vs Hebrew instructions

By default, these templates use English instructions and Hebrew content. Some Hebrew-native models (DictaLM, Jamba with Hebrew focus) may perform differently with Hebrew-language instructions. When comparing Hebrew-native to English-native models, run both variants and report.

English-instruction variant is default because:
1. It isolates Hebrew understanding from Hebrew instruction-following
2. English-trained models have lower instruction-following variance
3. It matches how most production Israeli products actually work (English backend prompts, Hebrew user content)
