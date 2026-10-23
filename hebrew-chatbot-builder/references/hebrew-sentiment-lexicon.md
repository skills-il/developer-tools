# Hebrew Sentiment Lexicon

A starter lexicon and matcher for basic Hebrew sentiment scoring in a chatbot (for example, to route an angry customer to a human sooner). It matches multi-word expressions first, longest first, so "לא טוב" is scored before "טוב".

This is a baseline, not a production classifier: a lexicon misses negation it has no entry for, sarcasm, and slang it has not seen. For production, use an LLM or a Hebrew-trained model and keep this as a cheap pre-filter.

```python
# Simple Hebrew sentiment lexicon (for basic analysis)
# For production, use an LLM or Hebrew-trained model
HEBREW_SENTIMENT = {
    # Positive
    "מעולה": 1.0, "מצוין": 1.0, "נהדר": 0.9, "אהבתי": 0.9,
    "טוב": 0.6, "יפה": 0.6, "נחמד": 0.5, "בסדר": 0.3,
    "תודה": 0.4, "תודה רבה": 0.7, "ממליץ": 0.8, "ממליצה": 0.8,
    "מרוצה": 0.8, "שמח": 0.7, "שמחה": 0.7, "אחלה": 0.8,
    "סבבה": 0.5, "קול": 0.5, "בומבה": 0.9,

    # Negative
    "גרוע": -0.9, "נורא": -0.9, "איום": -1.0, "מאכזב": -0.8,
    "רע": -0.7, "לא טוב": -0.6, "בעיה": -0.5, "תקלה": -0.5,
    "לא עובד": -0.7, "לא מרוצה": -0.8, "מתסכל": -0.7, "עצבני": -0.8,
    "חרא": -1.0, "זבל": -0.9, "בושה": -0.8, "אכזבה": -0.8,
}

def analyze_hebrew_sentiment(text: str) -> dict:
    """Basic Hebrew sentiment analysis using lexicon matching."""
    scores = []
    words_found = []

    # Check multi-word expressions first (sorted by length, longest first)
    sorted_expressions = sorted(HEBREW_SENTIMENT.keys(), key=len, reverse=True)

    remaining_text = text
    for expression in sorted_expressions:
        if expression in remaining_text:
            scores.append(HEBREW_SENTIMENT[expression])
            words_found.append(expression)
            remaining_text = remaining_text.replace(expression, "", 1)

    if not scores:
        return {"sentiment": "neutral", "score": 0.0, "words": []}

    avg_score = sum(scores) / len(scores)

    if avg_score > 0.2:
        sentiment = "positive"
    elif avg_score < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "score": round(avg_score, 2),
        "words": words_found,
    }
```
