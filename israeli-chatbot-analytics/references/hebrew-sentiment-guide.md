# Hebrew Sentiment Analysis Guide / מדריך ניתוח רגשות בעברית

A detailed guide to the challenges and solutions for sentiment analysis in Hebrew text, particularly in chatbot conversations. This reference covers negation handling, sarcasm detection, slang, mixed-language issues, and practical approaches for Israeli chatbot analytics.

## Why Hebrew Sentiment Analysis Is Different

Hebrew poses unique challenges for sentiment analysis compared to English:

1. **Morphological richness**: Hebrew is a morphologically complex language with root-based word formation, prefix/suffix particles, and gender/number inflection. A single word can carry information that requires several English words.

2. **Right-to-left (RTL) script**: Text direction affects tokenization tools, regex patterns, and display in analytics dashboards.

3. **Informal vs. formal registers**: Israeli internet and chat language differs significantly from formal written Hebrew, with heavy use of slang, abbreviations, and Arabic loanwords.

4. **Small training datasets**: Compared to English, Hebrew has fewer labeled sentiment datasets, making fine-tuning more challenging.

## Negation Patterns / דפוסי שלילה

Hebrew negation interacts with sentiment in ways that differ from English:

### Simple Negation with "לא" (lo, "not")

```
"לא טוב" (lo tov) = "not good" -> Negative
"לא רע" (lo ra) = "not bad" -> Mildly positive in Israeli usage
"לא נורא" (lo nora) = "not terrible" -> Mildly positive / neutral
```

**Key insight:** In Israeli conversational Hebrew, "לא רע" (not bad) is more positive than its English equivalent. It often means "actually pretty good."

### Double Negation

```
"לא שלא" (lo she'lo) = "not that not" -> Positive
"אי אפשר שלא" (i efshar shelo) = "impossible not to" -> Strong positive
Example: "אי אפשר שלא לאהוב את המוצר הזה" = "impossible not to love this product"
```

### Negation with Prefix

```
"בלתי אפשרי" (bilti efshari) = "impossible" -> Negative or neutral depending on context
"אי-שביעות רצון" (i-svi'ut ratzon) = "dissatisfaction" -> Negative
```

### Handling Strategy

```python
# Negation detection patterns for Hebrew sentiment
NEGATION_WORDS = ["לא", "אין", "בלי", "ללא", "אל"]

def handle_hebrew_negation(text: str, base_sentiment: float) -> float:
    """Adjust sentiment score based on Hebrew negation patterns."""

    # Check for double negation (reinforces positive)
    double_neg_patterns = ["לא שלא", "אי אפשר שלא", "אין דבר שלא"]
    for pattern in double_neg_patterns:
        if pattern in text:
            return abs(base_sentiment) * 0.8  # Strong positive

    # Check for "לא רע" pattern (mildly positive in Israeli usage)
    if "לא רע" in text or "לא נורא" in text:
        return 0.3  # Mildly positive

    # Standard negation flips sentiment
    words = text.split()
    for i, word in enumerate(words):
        if word in NEGATION_WORDS and i + 1 < len(words):
            return -base_sentiment * 0.7  # Flip with dampening

    return base_sentiment
```

## Sarcasm and Irony / סרקזם ואירוניה

Israeli communication culture is known for directness and frequent sarcasm. This makes sentiment analysis particularly challenging:

### Common Sarcastic Patterns

```
"יופי, בדיוק מה שחיכיתי לו" (Yofi, bidiyuk ma she'khikiti lo)
= "Great, exactly what I was waiting for"
Literal sentiment: Positive | Actual sentiment: Negative

"תודה רבה על השירות המדהים" (Toda raba al hasherut hamad'him)
= "Thanks a lot for the amazing service"
Literal sentiment: Positive | Actual sentiment: Often sarcastic/negative

"כל הכבוד, הצלחתם" (Kol hakavod, hitzlakhtem)
= "Well done, you succeeded"
Literal sentiment: Positive | Actual sentiment: Context-dependent
```

### Sarcasm Indicators

Look for these signals that suggest sarcasm:

1. **Preceding frustration**: If earlier messages in the conversation expressed frustration, a sudden "positive" statement is likely sarcastic.

2. **Punctuation patterns**: Excessive exclamation marks ("!!!"), ellipsis ("..."), or question marks after positive words.

3. **Contrast with context**: Positive words used after a service failure or complaint.

4. **Specific constructions**:
   - "כאילו" (ke'ilu, "like/as if") before a positive statement
   - "ברור ש..." (barur she, "obviously...") with positive followup
   - Quotation marks around positive adjectives ("שירות 'מעולה'")

### Detection Strategy

```python
def detect_potential_sarcasm(
    current_message: str,
    conversation_history: list[dict],
    current_sentiment: str,
) -> float:
    """Estimate probability that a message is sarcastic.

    Args:
        current_message: The message to evaluate.
        conversation_history: Previous messages in the conversation.
        current_sentiment: Detected sentiment before sarcasm check.

    Returns:
        Sarcasm probability (0.0 to 1.0).
    """
    sarcasm_score = 0.0

    # Only check messages that seem positive on the surface
    if current_sentiment != "positive":
        return 0.0

    # Check for excessive punctuation
    if current_message.count("!") >= 3:
        sarcasm_score += 0.2
    if "..." in current_message:
        sarcasm_score += 0.15

    # Check for sarcasm indicators
    sarcasm_markers = ["כאילו", "ברור", "בטח", "נו באמת", "כל הכבוד"]
    for marker in sarcasm_markers:
        if marker in current_message:
            sarcasm_score += 0.2

    # Check for quoted positive words (suggesting irony)
    import re
    quoted = re.findall(r'["\']([^"\']+)["\']', current_message)
    positive_words = ["מעולה", "מצוין", "נהדר", "מדהים", "אחלה"]
    for q in quoted:
        if any(pw in q for pw in positive_words):
            sarcasm_score += 0.3

    # Check preceding conversation sentiment
    if len(conversation_history) >= 2:
        recent_sentiments = [
            m.get("sentiment", "neutral")
            for m in conversation_history[-3:]
            if m.get("sender") == "user"
        ]
        negative_ratio = recent_sentiments.count("negative") / max(len(recent_sentiments), 1)
        if negative_ratio > 0.5:
            sarcasm_score += 0.25  # Preceded by frustration

    return min(sarcasm_score, 1.0)
```

## Hebrew Slang and Colloquialisms / סלנג וביטויים מדוברים

Israeli chat language includes many slang terms, Arabic loanwords, and abbreviations that standard NLP models may miss:

### Positive Slang

| Term | Origin | Transliteration | Meaning | Intensity |
|------|--------|-----------------|---------|-----------|
| אחלה | Arabic | akhla | great, awesome | High positive |
| סבבה | Arabic | sababa | cool, alright | Medium positive |
| בומבה | Slang | bomba | amazing, bomb | Very high positive |
| חבל על הזמן | Idiom | khaval al hazman | waste of time (but means "incredible") | Very high positive |
| אש | Slang | esh | fire (means great) | High positive |
| על הפנים | Idiom | al hapanim | on the face (ironically positive when preceded by "לא") | Context-dependent |
| מגניב | Slang | magniv | cool | Medium positive |
| עולמות | Slang | olamot | worlds (means amazing) | High positive |
| שיגעון | Slang | shiga'on | madness (means incredible) | High positive |

### Negative Slang

| Term | Origin | Transliteration | Meaning | Intensity |
|------|--------|-----------------|---------|-----------|
| חרא | Arabic | khara | crap/terrible | Very high negative |
| פאדיחה | Arabic | fadiha | embarrassment | High negative |
| על הפנים | Idiom | al hapanim | on the face (terrible) | High negative |
| חפרת לי | Slang | khafarta li | you bored me | Medium negative |
| דפוק | Slang | dafuk | messed up | High negative |
| מבאס | Slang | meva'es | bummer, disappointing | Medium negative |
| בזבוז | Standard | bizbuz | waste | Medium negative |
| מעצבן | Standard | ma'atzben | annoying | Medium negative |

### Neutral/Ambiguous

| Term | Transliteration | Context | Sentiment |
|------|-----------------|---------|-----------|
| וואלה | walla | "really?" / "wow" | Context-dependent |
| יאללה | yalla | "let's go" / "come on" | Context-dependent (impatience or enthusiasm) |
| נו | nu | "well..." / "come on" | Usually impatient / mildly negative |
| סתם | stam | "just kidding" / "nothing" | Neutralizer |
| מסתדר | mistader | "managing" / "getting by" | Neutral to mildly positive |

### Abbreviations and Textspeak

| Abbreviation | Full Form | Meaning |
|-------------|-----------|---------|
| תנצ"ל | תודה ניצחת לי | Thanks (slang) |
| חחח / ההה | Laughter | LOL equivalent |
| אמא'לה | אמא שלי | OMG equivalent |
| בלה"ב | בלי הנחה | Without discount |
| ב"ה | ברוך השם | Thank God |
| נ"ל | נראה לי | I think / seems to me |
| תכל'ס | תכלית | Bottom line / practically |

### Sentiment Lexicon Extension

```python
# Extended Hebrew sentiment lexicon including slang
HEBREW_SLANG_SENTIMENT = {
    # Positive slang
    "אחלה": 0.85,
    "סבבה": 0.5,
    "בומבה": 0.95,
    "חבל על הזמן": 0.9,  # Counterintuitively positive
    "אש": 0.8,
    "מגניב": 0.7,
    "עולמות": 0.85,
    "שיגעון": 0.85,
    "מטורף": 0.7,  # Can be positive or negative
    "חייב לנסות": 0.75,

    # Negative slang
    "חרא": -0.95,
    "פאדיחה": -0.8,
    "על הפנים": -0.85,
    "חפרת": -0.6,
    "דפוק": -0.85,
    "מבאס": -0.65,
    "מעצבן": -0.7,

    # Chat indicators
    "חחח": 0.4,     # Laughter, mildly positive
    "ההה": 0.3,     # Softer laughter
    "אמא'לה": 0.0,  # Exclamation, neutral

    # Ambiguous (default to neutral, use context)
    "וואלה": 0.0,
    "יאללה": 0.0,
    "נו": -0.15,
    "סתם": 0.0,
}
```

## Mixed Hebrew-English Text / טקסט מעורב עברית-אנגלית

Israeli users, especially in tech-related contexts, frequently mix Hebrew and English within the same message.

### Common Patterns

```
"ה-support שלכם גרוע" = "Your support is terrible"
"עשיתי upgrade ועכשיו הכל crash" = "I did an upgrade and now everything crashes"
"ה-UI ממש user friendly" = "The UI is really user friendly"
"צריך לעשות restart" = "Need to do a restart"
```

### Handling Strategy

1. **Language detection per segment**: Split the message into Hebrew and English segments and analyze each with the appropriate model.

2. **Unified approach**: Use a multilingual model that handles code-switching (like mBERT or XLM-R).

3. **Entity-aware splitting**: Technical terms in English within Hebrew sentences are often neutral (brand names, product names). Focus sentiment analysis on the Hebrew context words.

```python
import re

def split_mixed_text(text: str) -> list[dict]:
    """Split mixed Hebrew-English text into language segments.

    Returns list of dicts with 'text', 'language', 'start', 'end'.
    """
    segments = []
    # Find contiguous Hebrew or English runs
    pattern = r'([\u0590-\u05FF\s]+|[a-zA-Z\s]+|[^a-zA-Z\u0590-\u05FF]+)'
    matches = re.finditer(pattern, text)

    for match in matches:
        segment_text = match.group().strip()
        if not segment_text:
            continue

        if re.search(r'[\u0590-\u05FF]', segment_text):
            lang = "he"
        elif re.search(r'[a-zA-Z]', segment_text):
            lang = "en"
        else:
            lang = "other"

        segments.append({
            "text": segment_text,
            "language": lang,
            "start": match.start(),
            "end": match.end(),
        })

    return segments


def analyze_mixed_sentiment(text: str, he_analyzer, en_analyzer) -> dict:
    """Analyze sentiment of mixed Hebrew-English text.

    Uses separate analyzers for each language and combines results
    weighted by text proportion.
    """
    segments = split_mixed_text(text)
    he_segments = [s for s in segments if s["language"] == "he"]
    en_segments = [s for s in segments if s["language"] == "en"]

    he_text = " ".join(s["text"] for s in he_segments)
    en_text = " ".join(s["text"] for s in en_segments)

    results = {"segments": segments}

    he_weight = len(he_text) / max(len(he_text) + len(en_text), 1)
    en_weight = 1 - he_weight

    combined_score = 0.0

    if he_text.strip():
        he_result = he_analyzer.analyze(he_text)
        results["hebrew_sentiment"] = he_result
        he_score = he_result.get("score", 0) * (
            1 if he_result.get("label") == "positive"
            else -1 if he_result.get("label") == "negative"
            else 0
        )
        combined_score += he_score * he_weight

    if en_text.strip():
        en_result = en_analyzer.analyze(en_text)
        results["english_sentiment"] = en_result
        en_score = en_result.get("score", 0) * (
            1 if en_result.get("label") == "positive"
            else -1 if en_result.get("label") == "negative"
            else 0
        )
        combined_score += en_score * en_weight

    results["combined_score"] = round(combined_score, 3)
    results["combined_label"] = (
        "positive" if combined_score > 0.2
        else "negative" if combined_score < -0.2
        else "neutral"
    )

    return results
```

## Recommended Models and Tools

### DictaBERT (dicta-il/dictabert)
- **Type**: BERT-based Hebrew language model
- **Developer**: Dicta, Bar-Ilan University
- **Training data**: 10B+ Hebrew tokens
- **Strengths**: Best Hebrew language understanding, good for fine-tuning
- **Sentiment variant**: `dicta-il/dictabert-sentiment` (if available)
- **URL**: https://huggingface.co/dicta-il

### DictaLM (dicta-il/dictalm2.0)
- **Type**: Generative language model for Hebrew
- **Developer**: Dicta, Bar-Ilan University
- **Strengths**: Can perform zero-shot sentiment classification via prompting
- **Usage**: Good for nuanced sentiment when fine-tuned models are not available

### AlephBERT
- **Type**: BERT model for Hebrew
- **Developer**: TAU NLP Group (Tel Aviv University)
- **URL**: https://huggingface.co/onlplab/alephbert-base
- **Strengths**: Solid baseline for Hebrew NLP tasks

### YAP (Yet Another Parser)
- **Type**: Morphological analyzer for Hebrew
- **URL**: https://github.com/OnlpLab/yap
- **Usage**: Proper tokenization/lemmatization before sentiment analysis

### Practical Recommendations

1. **For production accuracy**: Fine-tune DictaBERT on your chatbot's domain data. Label 500-1000 messages manually as positive/neutral/negative, then fine-tune.

2. **For quick setup**: Use the slang-extended lexicon in this guide as a baseline, and add domain-specific terms.

3. **For mixed language**: Use multilingual models (mBERT, XLM-R) or the segment-and-combine approach described above.

4. **For sarcasm**: No automated approach is fully reliable. Build a sarcasm flag based on the detection strategy above and route flagged messages for human review.

5. **For evolving slang**: Review the lexicon quarterly. Israeli slang evolves with pop culture, social media trends, and news events. Assign someone to update the slang dictionary.
