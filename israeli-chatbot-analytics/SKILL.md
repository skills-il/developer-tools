---
name: israeli-chatbot-analytics
description: Analyze and optimize Hebrew chatbot performance with conversation flow analytics, Hebrew sentiment analysis, drop-off detection, user satisfaction scoring, A/B testing for response variants, and reporting dashboards. Use when user asks to "analyze chatbot performance", "measure chatbot satisfaction", "track Hebrew bot metrics", "analitika shel tsatbot" (Hebrew transliteration), or needs help with conversation analytics, intent accuracy tracking, or chatbot reporting. Supports Dialogflow, Rasa, and custom bot platforms. Do NOT use for building chatbots (use hebrew-chatbot-builder), Hebrew NLP model training (use hebrew-nlp-toolkit), customer support workflow setup (use israeli-customer-support-automator), or voice bot development (use hebrew-voice-bot-builder).
license: MIT
allowed-tools: Bash(python:*), Bash(pip:*)
compatibility: Requires Python 3.10+. Works with Claude Code, Cursor, Windsurf.
---

# Israeli Chatbot Analytics

Analyze and optimize Hebrew chatbot performance. This skill covers conversation flow analytics, Hebrew-specific sentiment analysis, drop-off detection, user satisfaction scoring, A/B testing for Hebrew response variants, intent recognition accuracy tracking, anomaly alerting, and reporting dashboards. Use it to understand whether your Hebrew chatbot is actually helping users and where to focus improvements.

## Instructions

### Step 1: Collect and Structure Conversation Logs

Before analyzing, ensure conversation data is structured consistently. Each conversation session should include:

```python
# Standard conversation log schema
conversation_log = {
    "session_id": "uuid-string",
    "user_id": "anonymous-or-identified",
    "channel": "whatsapp|telegram|web|app",
    "language": "he",           # Primary language detected
    "started_at": "ISO-8601",
    "ended_at": "ISO-8601",
    "messages": [
        {
            "timestamp": "ISO-8601",
            "sender": "user|bot",
            "text": "שלום, אני צריך עזרה",
            "intent": "greeting",           # Detected intent
            "intent_confidence": 0.92,       # Model confidence
            "entities": [],                  # Extracted entities
            "response_time_ms": 340,         # Bot response latency
        }
    ],
    "outcome": "resolved|escalated|abandoned|unknown",
    "satisfaction_score": null,   # CSAT score if collected
    "metadata": {
        "bot_version": "2.1.0",
        "ab_variant": "formal_he",
    }
}
```

If your platform does not export in this format, write a transformer to normalize logs before analysis. Common platforms and their export formats:

| Platform | Export Method | Format |
|----------|-------------|--------|
| Dialogflow CX | BigQuery export | JSON rows with session context |
| Rasa | Tracker Store (SQL/Mongo) | Events list per conversation |
| Custom bots | Application logs | Varies (normalize to schema above) |
| WhatsApp Cloud API | Webhook logs | Message objects with metadata |

### Step 2: Conversation Flow Analysis

Analyze session-level metrics to understand overall chatbot health:

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics

@dataclass
class ConversationMetrics:
    """Compute session-level metrics from conversation logs."""

    total_sessions: int = 0
    completed_sessions: int = 0
    escalated_sessions: int = 0
    abandoned_sessions: int = 0

    session_lengths: list = field(default_factory=list)    # message counts
    session_durations: list = field(default_factory=list)  # seconds

    @property
    def completion_rate(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.completed_sessions / self.total_sessions

    @property
    def escalation_rate(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.escalated_sessions / self.total_sessions

    @property
    def abandonment_rate(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.abandoned_sessions / self.total_sessions

    @property
    def avg_session_length(self) -> float:
        if not self.session_lengths:
            return 0.0
        return statistics.mean(self.session_lengths)

    @property
    def median_session_duration_seconds(self) -> float:
        if not self.session_durations:
            return 0.0
        return statistics.median(self.session_durations)


def compute_flow_metrics(conversations: list[dict]) -> ConversationMetrics:
    """Analyze conversation flow from structured logs."""
    metrics = ConversationMetrics()

    for convo in conversations:
        metrics.total_sessions += 1
        msg_count = len(convo.get("messages", []))
        metrics.session_lengths.append(msg_count)

        # Duration
        started = datetime.fromisoformat(convo["started_at"])
        ended = datetime.fromisoformat(convo.get("ended_at", convo["started_at"]))
        metrics.session_durations.append((ended - started).total_seconds())

        # Outcome
        outcome = convo.get("outcome", "unknown")
        if outcome == "resolved":
            metrics.completed_sessions += 1
        elif outcome == "escalated":
            metrics.escalated_sessions += 1
        elif outcome == "abandoned":
            metrics.abandoned_sessions += 1

    return metrics
```

**Key benchmarks for Hebrew chatbots (Israeli market, 2025-2026):**

| Metric | Good | Average | Needs Improvement |
|--------|------|---------|-------------------|
| Completion rate | > 70% | 50-70% | < 50% |
| Escalation rate | < 15% | 15-30% | > 30% |
| Abandonment rate | < 20% | 20-35% | > 35% |
| Avg session length | 4-8 messages | 8-15 messages | > 15 messages |
| First-contact resolution | > 65% | 45-65% | < 45% |

### Step 3: Drop-off Point Detection

Identify where users abandon conversations. This reveals UX problems, confusing prompts, or missing capabilities:

```python
def detect_drop_off_points(conversations: list[dict]) -> dict:
    """Find where users commonly abandon conversations.

    Returns a mapping of (intent, message_index) to drop-off count.
    """
    drop_offs = Counter()
    intent_at_drop = Counter()
    last_bot_messages = Counter()

    for convo in conversations:
        if convo.get("outcome") != "abandoned":
            continue

        messages = convo.get("messages", [])
        if not messages:
            continue

        # Where in the flow did they leave?
        drop_index = len(messages)

        # What was the last bot message?
        for msg in reversed(messages):
            if msg["sender"] == "bot":
                last_bot_messages[msg["text"][:80]] += 1
                break

        # What intent was active?
        for msg in reversed(messages):
            if msg.get("intent"):
                intent_at_drop[msg["intent"]] += 1
                break

        # At what conversation depth?
        drop_offs[drop_index] += 1

    return {
        "drop_off_by_depth": dict(drop_offs.most_common(20)),
        "drop_off_by_intent": dict(intent_at_drop.most_common(10)),
        "drop_off_by_last_bot_msg": dict(last_bot_messages.most_common(10)),
    }


def detect_conversation_loops(conversations: list[dict], threshold: int = 3) -> list[dict]:
    """Detect conversations where the bot repeats the same response,
    indicating the user is stuck in a loop.

    Args:
        conversations: List of conversation log dicts.
        threshold: Number of repeated bot messages to flag as a loop.

    Returns:
        List of flagged sessions with loop details.
    """
    looped_sessions = []

    for convo in conversations:
        bot_messages = [
            m["text"] for m in convo.get("messages", [])
            if m["sender"] == "bot"
        ]

        # Check for consecutive repeated messages
        repeat_count = 1
        for i in range(1, len(bot_messages)):
            if bot_messages[i] == bot_messages[i - 1]:
                repeat_count += 1
                if repeat_count >= threshold:
                    looped_sessions.append({
                        "session_id": convo["session_id"],
                        "repeated_message": bot_messages[i][:100],
                        "repeat_count": repeat_count,
                        "total_messages": len(convo["messages"]),
                    })
                    break
            else:
                repeat_count = 1

    return looped_sessions
```

### Step 4: Hebrew Sentiment Analysis

Hebrew sentiment analysis requires special handling due to morphological complexity, negation patterns, and slang. Use DictaBERT or DictaLM for production accuracy, or a lexicon-based approach for lightweight analysis.

**Using DictaBERT (recommended for production):**

```python
# DictaBERT: Hebrew BERT model by Dicta (Bar-Ilan University)
# Pretrained on 10B+ Hebrew tokens
# https://huggingface.co/dicta-il/dictabert

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class HebrewSentimentAnalyzer:
    """Hebrew sentiment analysis using DictaBERT fine-tuned model."""

    def __init__(self, model_name: str = "dicta-il/dictabert-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.labels = ["negative", "neutral", "positive"]

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of Hebrew text.

        Returns:
            dict with 'label', 'score', and 'scores' (all class probabilities).
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)

        scores = {
            label: round(prob.item(), 4)
            for label, prob in zip(self.labels, probabilities[0])
        }
        best_label = max(scores, key=scores.get)

        return {
            "label": best_label,
            "score": scores[best_label],
            "scores": scores,
        }

    def analyze_batch(self, texts: list[str], batch_size: int = 32) -> list[dict]:
        """Analyze sentiment for a batch of Hebrew texts."""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)

            for probs in probabilities:
                scores = {
                    label: round(p.item(), 4)
                    for label, p in zip(self.labels, probs)
                }
                best = max(scores, key=scores.get)
                results.append({
                    "label": best,
                    "score": scores[best],
                    "scores": scores,
                })

        return results
```

**Hebrew-specific sentiment challenges:**

1. **Negation with prefix**: Hebrew attaches negation as a prefix (e.g., "לא" before adjectives) and this can flip meaning. "לא רע" (not bad) is mildly positive in Israeli usage.

2. **Sarcasm and irony**: Israeli communication is often sarcastic. "יופי, בדיוק מה שחיכיתי לו" (Great, exactly what I was waiting for) can be deeply negative. DictaBERT handles some sarcasm; for better coverage, fine-tune on your domain data.

3. **Slang and abbreviations**: Israeli chat slang evolves rapidly. Common patterns:
   - "אחלה" (akhla, from Arabic) = great/positive
   - "סבבה" (sababa) = cool/okay
   - "בומבה" (bomba) = amazing
   - "חרא" (khara) = terrible
   - "פאדיחה" (fadiha, from Arabic) = embarrassing/bad
   - "וואלה" (walla) = really? / wow (context-dependent)

4. **Mixed Hebrew-English**: Israeli users frequently mix English words into Hebrew sentences. Ensure your model or lexicon handles "הsupport שלכם גרוע" (your support is terrible).

See `references/hebrew-sentiment-guide.md` for a detailed reference on Hebrew sentiment analysis challenges.

### Step 5: Intent Recognition Accuracy Tracking

Track how well your chatbot understands user requests over time:

```python
import numpy as np
from collections import defaultdict

class IntentAccuracyTracker:
    """Track and analyze intent recognition accuracy."""

    def __init__(self):
        self.predictions = []  # (predicted, actual, confidence)
        self.daily_accuracy = defaultdict(list)  # date -> [correct/incorrect]

    def log_prediction(
        self,
        predicted_intent: str,
        actual_intent: str,
        confidence: float,
        timestamp: str,
    ):
        """Log a single intent prediction for analysis."""
        correct = predicted_intent == actual_intent
        self.predictions.append({
            "predicted": predicted_intent,
            "actual": actual_intent,
            "confidence": confidence,
            "correct": correct,
            "timestamp": timestamp,
        })

        date_key = timestamp[:10]  # YYYY-MM-DD
        self.daily_accuracy[date_key].append(correct)

    def confusion_matrix(self) -> dict:
        """Build a confusion matrix for intent classification.

        Returns:
            dict with 'matrix' (2D dict) and 'intents' (sorted list).
        """
        matrix = defaultdict(lambda: defaultdict(int))
        intents = set()

        for pred in self.predictions:
            matrix[pred["actual"]][pred["predicted"]] += 1
            intents.add(pred["actual"])
            intents.add(pred["predicted"])

        sorted_intents = sorted(intents)
        return {
            "matrix": {
                actual: {pred: matrix[actual][pred] for pred in sorted_intents}
                for actual in sorted_intents
            },
            "intents": sorted_intents,
        }

    def misclassification_report(self, min_count: int = 5) -> list[dict]:
        """Identify the most common misclassifications.

        Args:
            min_count: Minimum number of misclassifications to include.

        Returns:
            Sorted list of misclassification pairs with counts.
        """
        misclass = Counter()

        for pred in self.predictions:
            if not pred["correct"]:
                pair = (pred["actual"], pred["predicted"])
                misclass[pair] += 1

        return [
            {
                "actual_intent": actual,
                "predicted_as": predicted,
                "count": count,
            }
            for (actual, predicted), count in misclass.most_common()
            if count >= min_count
        ]

    def low_confidence_intents(self, threshold: float = 0.6) -> dict:
        """Find intents where the model frequently has low confidence.

        Returns:
            Dict mapping intent names to average confidence and sample count.
        """
        intent_confidences = defaultdict(list)

        for pred in self.predictions:
            intent_confidences[pred["predicted"]].append(pred["confidence"])

        low_conf = {}
        for intent, confidences in intent_confidences.items():
            avg_conf = statistics.mean(confidences)
            if avg_conf < threshold:
                low_conf[intent] = {
                    "avg_confidence": round(avg_conf, 3),
                    "sample_count": len(confidences),
                    "below_threshold_pct": round(
                        sum(1 for c in confidences if c < threshold)
                        / len(confidences) * 100, 1
                    ),
                }

        return dict(sorted(low_conf.items(), key=lambda x: x[1]["avg_confidence"]))

    def accuracy_trend(self) -> list[dict]:
        """Get daily accuracy trend for plotting.

        Returns:
            List of dicts with 'date', 'accuracy', 'sample_count'.
        """
        trend = []
        for date in sorted(self.daily_accuracy.keys()):
            results = self.daily_accuracy[date]
            trend.append({
                "date": date,
                "accuracy": round(sum(results) / len(results), 4),
                "sample_count": len(results),
            })
        return trend
```

**How to get ground truth labels:**

- **Manual labeling**: Sample 100-200 conversations per week and have Hebrew-speaking annotators label actual intents. This is the gold standard.
- **Escalation signals**: When a user explicitly corrects the bot ("לא, התכוונתי ל...") or asks for a human agent after a misunderstanding, flag the prior intent as incorrect.
- **Post-chat surveys**: Ask "Did the bot understand what you needed?" and correlate with detected intent.

### Step 6: User Satisfaction Measurement

Combine multiple signals to build a satisfaction score:

```python
@dataclass
class SatisfactionSignals:
    """Combine multiple satisfaction signals into a composite score."""

    # Direct feedback (if available)
    csat_score: float | None = None      # 1-5 scale
    thumbs_rating: str | None = None     # "up" or "down"

    # Behavioral signals
    session_resolved: bool = False
    escalated_to_human: bool = False
    abandoned: bool = False
    repeated_fallbacks: int = 0
    loop_detected: bool = False

    # Sentiment signals
    final_sentiment: str = "neutral"     # positive/neutral/negative
    sentiment_trend: str = "stable"      # improving/stable/declining

    def composite_score(self) -> float:
        """Calculate a composite satisfaction score (0.0 to 1.0)."""
        score = 0.5  # Start neutral

        # Direct feedback (highest weight)
        if self.csat_score is not None:
            score = (self.csat_score - 1) / 4  # Normalize 1-5 to 0-1
            return round(score, 2)

        if self.thumbs_rating == "up":
            score = 0.8
        elif self.thumbs_rating == "down":
            score = 0.2

        # Behavioral adjustments
        if self.session_resolved:
            score += 0.15
        if self.escalated_to_human:
            score -= 0.1
        if self.abandoned:
            score -= 0.2
        if self.repeated_fallbacks > 2:
            score -= 0.15
        if self.loop_detected:
            score -= 0.2

        # Sentiment adjustments
        sentiment_adj = {
            "positive": 0.1,
            "neutral": 0.0,
            "negative": -0.15,
        }
        score += sentiment_adj.get(self.final_sentiment, 0)

        trend_adj = {
            "improving": 0.05,
            "stable": 0.0,
            "declining": -0.1,
        }
        score += trend_adj.get(self.sentiment_trend, 0)

        return round(max(0.0, min(1.0, score)), 2)


def collect_post_chat_survey_he() -> dict:
    """Template for Hebrew post-chat survey.

    Returns the survey structure for integration with your chat platform.
    """
    return {
        "title": "נשמח לשמוע מה חשבת",
        "questions": [
            {
                "id": "satisfaction",
                "type": "rating",
                "text": "עד כמה הצ'אטבוט עזר לך?",
                "scale": {"min": 1, "max": 5},
                "labels": {
                    1: "לא עזר בכלל",
                    2: "עזר מעט",
                    3: "עזר בינוני",
                    4: "עזר טוב",
                    5: "עזר מצוין",
                },
            },
            {
                "id": "understood",
                "type": "yes_no",
                "text": "האם הצ'אטבוט הבין את מה שרצית?",
            },
            {
                "id": "open_feedback",
                "type": "free_text",
                "text": "רוצה לשתף עוד משהו? (לא חובה)",
                "required": False,
            },
        ],
        "submit_label": "שלח משוב",
        "thank_you": "תודה על המשוב! זה עוזר לנו להשתפר.",
    }
```

### Step 7: A/B Testing for Hebrew Response Variants

Test different phrasings, formality levels, and gender handling strategies:

```python
import hashlib
import random
from datetime import datetime

class HebrewABTestManager:
    """Manage A/B tests for Hebrew chatbot responses."""

    def __init__(self):
        self.active_tests = {}
        self.results = defaultdict(lambda: {
            "impressions": 0,
            "completions": 0,
            "satisfaction_scores": [],
            "escalations": 0,
        })

    def create_test(
        self,
        test_id: str,
        variants: dict[str, str],
        traffic_split: dict[str, float] | None = None,
    ):
        """Create a new A/B test.

        Args:
            test_id: Unique identifier for the test.
            variants: Dict of variant_name -> response_text.
            traffic_split: Dict of variant_name -> percentage (0-1).
                Defaults to equal split.

        Example:
            create_test(
                "welcome_message",
                variants={
                    "formal": "שלום וברוכים הבאים. כיצד נוכל לסייע לכם?",
                    "casual": "היי! איך אפשר לעזור?",
                    "gender_neutral": "שלום! ניתן לבחור מהאפשרויות הבאות:",
                },
            )
        """
        if traffic_split is None:
            n = len(variants)
            traffic_split = {name: 1.0 / n for name in variants}

        self.active_tests[test_id] = {
            "variants": variants,
            "traffic_split": traffic_split,
            "created_at": datetime.now().isoformat(),
        }

    def assign_variant(self, test_id: str, user_id: str) -> str:
        """Deterministically assign a user to a test variant.

        Uses a hash of user_id + test_id for consistent assignment.
        The same user always sees the same variant.
        """
        test = self.active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")

        # Deterministic assignment based on user hash
        hash_input = f"{user_id}:{test_id}"
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_val % 1000) / 1000.0

        cumulative = 0.0
        for variant_name, split in test["traffic_split"].items():
            cumulative += split
            if bucket < cumulative:
                return variant_name

        # Fallback to last variant
        return list(test["traffic_split"].keys())[-1]

    def get_response(self, test_id: str, user_id: str) -> tuple[str, str]:
        """Get the response text for a user in a test.

        Returns:
            Tuple of (variant_name, response_text).
        """
        variant = self.assign_variant(test_id, user_id)
        text = self.active_tests[test_id]["variants"][variant]

        # Track impression
        result_key = f"{test_id}:{variant}"
        self.results[result_key]["impressions"] += 1

        return variant, text

    def record_outcome(
        self,
        test_id: str,
        variant: str,
        completed: bool = False,
        satisfaction: float | None = None,
        escalated: bool = False,
    ):
        """Record the outcome for a test variant."""
        result_key = f"{test_id}:{variant}"
        if completed:
            self.results[result_key]["completions"] += 1
        if satisfaction is not None:
            self.results[result_key]["satisfaction_scores"].append(satisfaction)
        if escalated:
            self.results[result_key]["escalations"] += 1

    def get_test_results(self, test_id: str) -> dict:
        """Get results summary for a test."""
        test = self.active_tests.get(test_id)
        if not test:
            return {}

        summary = {}
        for variant_name in test["variants"]:
            key = f"{test_id}:{variant_name}"
            data = self.results[key]
            impressions = data["impressions"]

            summary[variant_name] = {
                "impressions": impressions,
                "completion_rate": (
                    round(data["completions"] / impressions, 4)
                    if impressions > 0 else 0
                ),
                "avg_satisfaction": (
                    round(statistics.mean(data["satisfaction_scores"]), 2)
                    if data["satisfaction_scores"] else None
                ),
                "escalation_rate": (
                    round(data["escalations"] / impressions, 4)
                    if impressions > 0 else 0
                ),
            }

        return summary
```

**Common Hebrew A/B test dimensions:**

| Dimension | Variant A | Variant B | What to Measure |
|-----------|-----------|-----------|-----------------|
| Formality | "כיצד נוכל לסייע?" | "איך אפשר לעזור?" | Completion rate |
| Gender | Slash notation ("את/ה") | Gender-neutral ("ניתן ל...") | Satisfaction score |
| Length | Detailed explanation | Short, punchy response | Drop-off rate |
| Emoji usage | With emoji | Without emoji | Engagement |
| Error phrasing | "לא הצלחתי להבין" | "אפשר לנסח אחרת?" | Retry rate |

### Step 8: Performance Dashboards and KPIs

Track these key metrics in your dashboard:

```python
@dataclass
class ChatbotDashboard:
    """Key metrics for chatbot performance dashboard."""

    # Core metrics
    total_conversations: int = 0
    resolution_rate: float = 0.0        # % resolved without escalation
    first_contact_resolution: float = 0.0  # % resolved in first session
    avg_handle_time_seconds: float = 0.0
    escalation_rate: float = 0.0
    abandonment_rate: float = 0.0

    # User satisfaction
    avg_csat: float = 0.0               # 1-5 scale
    nps_score: float = 0.0              # -100 to 100
    thumbs_up_ratio: float = 0.0        # % positive

    # Intent accuracy
    intent_accuracy: float = 0.0        # % correctly classified
    fallback_rate: float = 0.0          # % of messages hitting fallback

    # Performance
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0

    # Volume
    conversations_per_day: float = 0.0
    peak_hour: int = 0                  # 0-23
    busiest_day: str = ""               # "Sunday" etc.

    def to_report_dict(self) -> dict:
        """Format metrics for reporting."""
        return {
            "core": {
                "total_conversations": self.total_conversations,
                "resolution_rate": f"{self.resolution_rate:.1%}",
                "first_contact_resolution": f"{self.first_contact_resolution:.1%}",
                "avg_handle_time": f"{self.avg_handle_time_seconds:.0f}s",
                "escalation_rate": f"{self.escalation_rate:.1%}",
                "abandonment_rate": f"{self.abandonment_rate:.1%}",
            },
            "satisfaction": {
                "avg_csat": f"{self.avg_csat:.1f}/5",
                "nps": f"{self.nps_score:+.0f}",
                "thumbs_up": f"{self.thumbs_up_ratio:.1%}",
            },
            "accuracy": {
                "intent_accuracy": f"{self.intent_accuracy:.1%}",
                "fallback_rate": f"{self.fallback_rate:.1%}",
            },
            "performance": {
                "avg_response_time": f"{self.avg_response_time_ms:.0f}ms",
                "p95_response_time": f"{self.p95_response_time_ms:.0f}ms",
            },
            "volume": {
                "daily_avg": f"{self.conversations_per_day:.0f}",
                "peak_hour": f"{self.peak_hour}:00",
                "busiest_day": self.busiest_day,
            },
        }


def build_dashboard(
    conversations: list[dict],
    period_days: int = 7,
) -> ChatbotDashboard:
    """Build a dashboard from conversation logs.

    Args:
        conversations: List of conversation log dicts.
        period_days: Number of days in the reporting period.
    """
    dashboard = ChatbotDashboard()
    dashboard.total_conversations = len(conversations)

    if not conversations:
        return dashboard

    # Outcome counts
    outcomes = Counter(c.get("outcome", "unknown") for c in conversations)
    resolved = outcomes.get("resolved", 0)
    escalated = outcomes.get("escalated", 0)
    abandoned = outcomes.get("abandoned", 0)

    dashboard.resolution_rate = resolved / len(conversations)
    dashboard.escalation_rate = escalated / len(conversations)
    dashboard.abandonment_rate = abandoned / len(conversations)

    # Handle time
    durations = []
    for c in conversations:
        if c.get("started_at") and c.get("ended_at"):
            start = datetime.fromisoformat(c["started_at"])
            end = datetime.fromisoformat(c["ended_at"])
            durations.append((end - start).total_seconds())
    if durations:
        dashboard.avg_handle_time_seconds = statistics.mean(durations)

    # CSAT
    csat_scores = [
        c["satisfaction_score"] for c in conversations
        if c.get("satisfaction_score") is not None
    ]
    if csat_scores:
        dashboard.avg_csat = statistics.mean(csat_scores)

    # Response times
    response_times = []
    for c in conversations:
        for msg in c.get("messages", []):
            if msg["sender"] == "bot" and msg.get("response_time_ms"):
                response_times.append(msg["response_time_ms"])
    if response_times:
        dashboard.avg_response_time_ms = statistics.mean(response_times)
        sorted_rt = sorted(response_times)
        p95_idx = int(len(sorted_rt) * 0.95)
        dashboard.p95_response_time_ms = sorted_rt[min(p95_idx, len(sorted_rt) - 1)]

    # Intent accuracy
    total_intents = 0
    correct_intents = 0
    fallback_count = 0
    total_messages = 0
    for c in conversations:
        for msg in c.get("messages", []):
            if msg["sender"] == "user":
                total_messages += 1
                if msg.get("intent"):
                    total_intents += 1
                    if msg.get("intent_confidence", 0) > 0.7:
                        correct_intents += 1
                    if msg["intent"] == "fallback":
                        fallback_count += 1

    if total_intents > 0:
        dashboard.intent_accuracy = correct_intents / total_intents
    if total_messages > 0:
        dashboard.fallback_rate = fallback_count / total_messages

    # Volume
    dashboard.conversations_per_day = len(conversations) / max(period_days, 1)

    # Peak hour and busiest day
    hour_counts = Counter()
    day_counts = Counter()
    for c in conversations:
        if c.get("started_at"):
            dt = datetime.fromisoformat(c["started_at"])
            hour_counts[dt.hour] += 1
            day_counts[dt.strftime("%A")] += 1

    if hour_counts:
        dashboard.peak_hour = hour_counts.most_common(1)[0][0]
    if day_counts:
        dashboard.busiest_day = day_counts.most_common(1)[0][0]

    return dashboard
```

**Israeli traffic patterns to expect:**
- Peak hours are typically 10:00-12:00 and 19:00-22:00 (Israel Time, UTC+2/+3)
- Sunday is the busiest day (first workday of the Israeli week)
- Friday afternoon and Saturday see minimal traffic
- Holiday periods (Rosh Hashana, Pesach, Sukkot) show different patterns

### Step 9: Hebrew-Specific Analytics Challenges

#### RTL Text in Charts and Visualizations

When rendering analytics dashboards that display Hebrew text, handle these RTL issues:

```python
import matplotlib.pyplot as plt
import matplotlib

# Use a font that supports Hebrew
matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Arial", "Heebo"]

# Tip: Use horizontal bar charts so Hebrew labels read naturally on the y-axis.
# For interactive dashboards, Plotly handles RTL better than matplotlib.
# Use font-family "Heebo, Arial, sans-serif" and add extra left margin for labels.
```

#### Hebrew Word Tokenization for Word Clouds

Standard whitespace tokenization does not work well for Hebrew due to prefix particles (ב, ה, ו, ל, מ, כ, ש):

```python
# Standard whitespace tokenization fails for Hebrew due to prefix particles.
# Use YAP (https://github.com/OnlpLab/yap) for production, or strip common prefixes:
HEBREW_PREFIXES = ["ב", "ה", "ו", "ל", "מ", "כ", "ש", "וה", "של", "לה"]

# Strip prefixes only if word is long enough (>3 chars) and remainder >= 2 chars.
# For word clouds: use bidi algorithm to convert Hebrew for display,
# remove stopwords (של, את, על, עם, אני, זה, כי, גם, לא, יש, אין, מה).
# See references/hebrew-sentiment-guide.md for detailed tokenization code.
```

#### Mixed Hebrew-English Query Handling

Israeli users frequently mix languages. Track language distribution and handle accordingly:

```python
import re

def detect_message_language(text: str) -> str:
    """Detect primary language by counting Hebrew vs English characters."""
    hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total = hebrew_chars + english_chars
    if total == 0:
        return "unknown"
    return "he" if hebrew_chars / total >= 0.5 else "en"

# Track mixed-language rate: messages where 20-80% is Hebrew.
# Israeli users frequently code-switch between Hebrew and English.
```

### Step 10: Alerting and Anomaly Detection

Set up alerts to catch problems before they affect too many users:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class AlertRule:
    """Define an alerting rule for chatbot metrics."""
    name: str
    metric: str
    operator: str          # "gt" (greater than), "lt" (less than)
    threshold: float
    window_minutes: int    # Rolling window
    severity: str          # "critical", "warning", "info"
    description_he: str    # Hebrew description for ops team


# Recommended alert rules for Hebrew chatbots
DEFAULT_ALERT_RULES = [
    AlertRule(
        name="high_escalation_rate",
        metric="escalation_rate",
        operator="gt",
        threshold=0.35,
        window_minutes=60,
        severity="warning",
        description_he="שיעור הסלמה גבוה מ-35% בשעה האחרונה",
    ),
    AlertRule(
        name="satisfaction_drop",
        metric="avg_csat",
        operator="lt",
        threshold=3.0,
        window_minutes=120,
        severity="critical",
        description_he="שביעות רצון ממוצעת ירדה מתחת ל-3.0 בשעתיים האחרונות",
    ),
    AlertRule(
        name="high_abandonment",
        metric="abandonment_rate",
        operator="gt",
        threshold=0.40,
        window_minutes=60,
        severity="critical",
        description_he="שיעור נטישה גבוה מ-40% בשעה האחרונה",
    ),
    AlertRule(
        name="high_fallback_rate",
        metric="fallback_rate",
        operator="gt",
        threshold=0.25,
        window_minutes=30,
        severity="warning",
        description_he="שיעור fallback גבוה מ-25% בחצי שעה האחרונה",
    ),
    AlertRule(
        name="slow_response",
        metric="p95_response_time_ms",
        operator="gt",
        threshold=3000,
        window_minutes=15,
        severity="warning",
        description_he="זמן תגובה P95 חורג מ-3 שניות ברבע השעה האחרון",
    ),
    AlertRule(
        name="new_unrecognized_intents",
        metric="new_unknown_intents_count",
        operator="gt",
        threshold=20,
        window_minutes=60,
        severity="info",
        description_he="יותר מ-20 כוונות לא מזוהות חדשות בשעה האחרונה",
    ),
]


class AlertManager:
    """Monitor metrics and trigger alerts."""

    def __init__(self, rules: list[AlertRule] | None = None):
        self.rules = rules or DEFAULT_ALERT_RULES
        self.triggered_alerts = []

    def check_metrics(self, current_metrics: dict) -> list[dict]:
        """Check current metrics against alert rules.

        Args:
            current_metrics: Dict of metric_name -> current_value.

        Returns:
            List of triggered alerts.
        """
        alerts = []

        for rule in self.rules:
            value = current_metrics.get(rule.metric)
            if value is None:
                continue

            triggered = False
            if rule.operator == "gt" and value > rule.threshold:
                triggered = True
            elif rule.operator == "lt" and value < rule.threshold:
                triggered = True

            if triggered:
                alert = {
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "metric": rule.metric,
                    "current_value": value,
                    "threshold": rule.threshold,
                    "description_he": rule.description_he,
                    "triggered_at": datetime.now().isoformat(),
                }
                alerts.append(alert)
                self.triggered_alerts.append(alert)

        return alerts
```

### Step 11: Reporting Templates

Generate periodic reports summarizing chatbot performance:

```python
def generate_weekly_report(
    dashboard: ChatbotDashboard,
    previous_dashboard: ChatbotDashboard | None = None,
    period_start: str = "",
    period_end: str = "",
) -> str:
    """Generate a Hebrew weekly performance report.

    Args:
        dashboard: Current period metrics.
        previous_dashboard: Previous period for comparison.
        period_start: Report start date (YYYY-MM-DD).
        period_end: Report end date (YYYY-MM-DD).

    Returns:
        Formatted report string in Hebrew.
    """

    def trend_arrow(current: float, previous: float, higher_is_better: bool = True) -> str:
        if previous == 0:
            return ""
        diff = current - previous
        pct = (diff / previous) * 100
        if abs(pct) < 1:
            return "(ללא שינוי)"
        arrow = "+" if diff > 0 else ""
        good = (diff > 0) == higher_is_better
        indicator = "[v]" if good else "[!]"
        return f"{indicator} {arrow}{pct:.1f}%"

    lines = [
        f"# דוח ביצועי צ'אטבוט שבועי",
        f"## תקופה: {period_start} עד {period_end}",
        "",
        "## מדדים מרכזיים",
        "",
        f"| מדד | ערך | שינוי מהשבוע הקודם |",
        f"|------|------|---------------------|",
    ]

    prev = previous_dashboard

    metrics = [
        ("שיחות", f"{dashboard.total_conversations:,}",
         trend_arrow(dashboard.total_conversations,
                     prev.total_conversations if prev else 0)),
        ("שיעור פתרון", f"{dashboard.resolution_rate:.1%}",
         trend_arrow(dashboard.resolution_rate,
                     prev.resolution_rate if prev else 0)),
        ("שביעות רצון (CSAT)", f"{dashboard.avg_csat:.1f}/5",
         trend_arrow(dashboard.avg_csat,
                     prev.avg_csat if prev else 0)),
        ("שיעור הסלמה", f"{dashboard.escalation_rate:.1%}",
         trend_arrow(dashboard.escalation_rate,
                     prev.escalation_rate if prev else 0, higher_is_better=False)),
        ("שיעור נטישה", f"{dashboard.abandonment_rate:.1%}",
         trend_arrow(dashboard.abandonment_rate,
                     prev.abandonment_rate if prev else 0, higher_is_better=False)),
        ("דיוק זיהוי כוונות", f"{dashboard.intent_accuracy:.1%}",
         trend_arrow(dashboard.intent_accuracy,
                     prev.intent_accuracy if prev else 0)),
        ("זמן תגובה ממוצע", f"{dashboard.avg_response_time_ms:.0f}ms",
         trend_arrow(dashboard.avg_response_time_ms,
                     prev.avg_response_time_ms if prev else 0, higher_is_better=False)),
    ]

    for name, value, change in metrics:
        lines.append(f"| {name} | {value} | {change} |")

    lines.extend([
        "",
        "## תנועה",
        f"- ממוצע שיחות ביום: {dashboard.conversations_per_day:.0f}",
        f"- שעת שיא: {dashboard.peak_hour}:00",
        f"- יום עמוס ביותר: {dashboard.busiest_day}",
    ])

    return "\n".join(lines)
```

### Step 12: Integration with Chatbot Platforms

#### Dialogflow CX Analytics

```python
def parse_dialogflow_cx_logs(bigquery_rows: list[dict]) -> list[dict]:
    """Transform Dialogflow CX BigQuery export to standard conversation format.

    Dialogflow CX stores conversation data in BigQuery when configured.
    Export query:
        SELECT * FROM `project.dataset.dialogflow_cx_interactions`
        WHERE DATE(request_time) BETWEEN @start AND @end
    """
    sessions = defaultdict(lambda: {
        "messages": [],
        "started_at": None,
        "ended_at": None,
    })

    for row in bigquery_rows:
        session_id = row["session_id"]
        timestamp = row["request_time"]

        session = sessions[session_id]

        if session["started_at"] is None or timestamp < session["started_at"]:
            session["started_at"] = timestamp
        if session["ended_at"] is None or timestamp > session["ended_at"]:
            session["ended_at"] = timestamp

        # User message
        if row.get("query_text"):
            session["messages"].append({
                "timestamp": timestamp,
                "sender": "user",
                "text": row["query_text"],
                "intent": row.get("matched_intent", ""),
                "intent_confidence": row.get("intent_confidence", 0),
            })

        # Bot response
        if row.get("response_text"):
            session["messages"].append({
                "timestamp": timestamp,
                "sender": "bot",
                "text": row["response_text"],
            })

    # Convert to standard format
    conversations = []
    for session_id, session in sessions.items():
        session["messages"].sort(key=lambda m: m["timestamp"])
        conversations.append({
            "session_id": session_id,
            "started_at": session["started_at"],
            "ended_at": session["ended_at"],
            "messages": session["messages"],
            "outcome": "unknown",  # Derive from flow completion
            "language": "he",
        })

    return conversations
```

#### Rasa Tracker Store Analytics

```python
def parse_rasa_tracker_events(tracker_events: list[dict]) -> list[dict]:
    """Transform Rasa tracker store events to standard conversation format.

    Rasa stores events per sender_id in its tracker store.
    Query from SQL tracker store:
        SELECT * FROM events WHERE sender_id = @sender_id ORDER BY timestamp
    """
    conversations = []

    current_session = {
        "messages": [],
        "started_at": None,
        "ended_at": None,
    }

    for event in tracker_events:
        event_type = event.get("event")
        timestamp = event.get("timestamp", "")

        if event_type == "session_started":
            if current_session["messages"]:
                conversations.append(current_session)
            current_session = {
                "session_id": event.get("metadata", {}).get("session_id", ""),
                "messages": [],
                "started_at": timestamp,
                "ended_at": None,
                "outcome": "unknown",
                "language": "he",
            }

        elif event_type == "user":
            current_session["ended_at"] = timestamp
            intent_data = event.get("parse_data", {}).get("intent", {})
            current_session["messages"].append({
                "timestamp": timestamp,
                "sender": "user",
                "text": event.get("text", ""),
                "intent": intent_data.get("name", ""),
                "intent_confidence": intent_data.get("confidence", 0),
            })

        elif event_type == "bot":
            current_session["ended_at"] = timestamp
            current_session["messages"].append({
                "timestamp": timestamp,
                "sender": "bot",
                "text": event.get("text", ""),
            })

        elif event_type == "action" and event.get("name") == "action_human_handoff":
            current_session["outcome"] = "escalated"

    if current_session["messages"]:
        conversations.append(current_session)

    return conversations
```

## Examples

### Example 1: Analyze chatbot performance for the past week

User says: "Analyze my Hebrew chatbot logs from the past week and show me where users are dropping off."

Actions:
1. Load conversation logs from the specified time period.
2. Run `compute_flow_metrics()` to get session-level stats.
3. Run `detect_drop_off_points()` to find abandonment patterns.
4. Run `detect_conversation_loops()` to identify stuck users.
5. Generate a summary with actionable recommendations.

Result: Report with completion rate, top drop-off points, looping conversations, and abandonment patterns.

### Example 2: Set up A/B testing for greeting messages

User says: "I want to test whether a formal or casual Hebrew greeting works better."

Actions:
1. Create an A/B test with `HebrewABTestManager.create_test()`.
2. Define variants: formal ("כיצד נוכל לסייע לכם היום?") vs. casual ("היי! מה אפשר לעשות בשבילך?").
3. Configure traffic split (50/50).
4. Integrate with the bot's greeting handler.
5. Set up outcome tracking (completion rate, CSAT, escalation).

Result: Running A/B test with deterministic user assignment and statistical outcome tracking.

### Example 3: Set up anomaly alerting

User says: "Alert me if chatbot satisfaction drops suddenly."

Actions:
1. Configure `AlertManager` with satisfaction and escalation rules.
2. Set up rolling window calculations for recent metrics.
3. Connect alerts to notification channels (Slack, email, PagerDuty).
4. Add Hebrew-language alert descriptions for the ops team.

Result: Real-time monitoring that triggers alerts when CSAT drops below 3.0, escalation rate exceeds 35%, or abandonment spikes above 40%.

### Example 4: Generate a weekly performance report

User says: "Create a Hebrew weekly report for the chatbot team."

Actions:
1. Run `build_dashboard()` for the current and previous weeks.
2. Call `generate_weekly_report()` with both dashboards for trend arrows.
3. Include drop-off analysis and intent accuracy breakdown.
4. Format output in Hebrew with RTL-compatible tables.

Result: A formatted Hebrew report with week-over-week comparisons, trend indicators, and key metrics ready to share with the team.

## Bundled Resources

### Scripts
- `scripts/conversation-analyzer.py` -- Analyze chatbot conversation logs for key metrics (drop-off, sentiment, resolution). Run: `python scripts/conversation-analyzer.py --help`

### References
- `references/chatbot-metrics-glossary.md` -- Glossary of chatbot analytics metrics with Hebrew translations and industry benchmarks. Consult when defining KPIs or explaining metrics to Hebrew-speaking stakeholders.
- `references/hebrew-sentiment-guide.md` -- Guide to Hebrew sentiment analysis challenges including negation, sarcasm, slang, and mixed-language handling. Consult when building or tuning Hebrew sentiment models.

## Gotchas

- Hebrew sentiment analysis requires Israeli-specific training data. Standard English sentiment models misclassify Hebrew sarcasm (very common in Israeli communication) as neutral or positive.
- Israeli chatbot usage peaks on Sunday mornings (start of work week), not Monday. Weekly analytics reports should anchor to Sunday-Thursday.
- Hebrew text analytics must handle prefixed particles (ב-, ל-, כ-, מ-) that change word boundaries. Standard tokenizers trained on English split Hebrew words incorrectly.
- Israeli users frequently code-switch between Hebrew and English within a single chatbot conversation. Analytics tools must handle bilingual sessions, not treat them as two separate languages.

## Troubleshooting

### Error: "DictaBERT model not loading"
Cause: The `dicta-il/dictabert-sentiment` model requires PyTorch and the `transformers` library. It is approximately 500MB.
Solution: Install dependencies with `pip install torch transformers` and ensure sufficient disk space. For CPU-only environments, install `torch` with `pip install torch --index-url https://download.pytorch.org/whl/cpu`.

### Error: "Hebrew text appears reversed in charts"
Cause: Matplotlib does not natively support RTL text rendering. Hebrew strings are drawn left-to-right by default.
Solution: Use the `python-bidi` library (`pip install python-bidi`) to apply the BiDi algorithm before rendering, or switch to Plotly which has better RTL support. For word clouds, use `bidi.algorithm.get_display()` on each Hebrew string.

### Error: "Tokenization produces wrong word frequencies"
Cause: Simple whitespace splitting does not account for Hebrew prefix particles (ב, ה, ו, ל, מ, כ, ש) that attach to words.
Solution: Use the prefix-stripping tokenizer in Step 9, or for production accuracy, use the YAP morphological analyzer (https://github.com/OnlpLab/yap).

### Error: "Sentiment scores are unreliable for short messages"
Cause: Very short Hebrew messages (1-3 words) lack context for accurate sentiment analysis. Colloquial responses like "סבבה" (okay/cool) can be positive or neutral depending on context.
Solution: For messages under 4 words, rely on behavioral signals (did the user continue, escalate, or abandon?) rather than text-based sentiment. Combine sentiment with satisfaction signals as shown in Step 6.

### Error: "A/B test results are not statistically significant"
Cause: Insufficient sample size. Hebrew chatbots in Israel often serve smaller user bases compared to global products.
Solution: Run tests for at least 2 weeks and aim for 200+ impressions per variant before drawing conclusions. Use a significance calculator and target p < 0.05.
