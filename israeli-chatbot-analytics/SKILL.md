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
    """Session-level metrics computed from conversation logs."""

    total_sessions: int = 0
    completed_sessions: int = 0
    escalated_sessions: int = 0
    abandoned_sessions: int = 0
    session_lengths: list = field(default_factory=list)    # message counts
    session_durations: list = field(default_factory=list)  # seconds

    def _rate(self, n: int) -> float:
        return n / self.total_sessions if self.total_sessions else 0.0

    @property
    def completion_rate(self) -> float:
        return self._rate(self.completed_sessions)

    @property
    def escalation_rate(self) -> float:
        return self._rate(self.escalated_sessions)

    @property
    def abandonment_rate(self) -> float:
        return self._rate(self.abandoned_sessions)

    @property
    def avg_session_length(self) -> float:
        return statistics.mean(self.session_lengths) if self.session_lengths else 0.0

    @property
    def median_session_duration_seconds(self) -> float:
        return statistics.median(self.session_durations) if self.session_durations else 0.0


def compute_flow_metrics(conversations: list[dict]) -> ConversationMetrics:
    """Analyze conversation flow from structured logs."""
    m = ConversationMetrics()
    for convo in conversations:
        m.total_sessions += 1
        m.session_lengths.append(len(convo.get("messages", [])))
        started = datetime.fromisoformat(convo["started_at"])
        ended = datetime.fromisoformat(convo.get("ended_at", convo["started_at"]))
        m.session_durations.append((ended - started).total_seconds())
        outcome = convo.get("outcome", "unknown")
        if outcome == "resolved":
            m.completed_sessions += 1
        elif outcome == "escalated":
            m.escalated_sessions += 1
        elif outcome == "abandoned":
            m.abandoned_sessions += 1
    return m
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
    """Find where users commonly abandon conversations (by depth, intent, last msg)."""
    drop_offs, intent_at_drop, last_bot_messages = Counter(), Counter(), Counter()
    for convo in conversations:
        if convo.get("outcome") != "abandoned":
            continue
        messages = convo.get("messages", [])
        if not messages:
            continue
        drop_offs[len(messages)] += 1  # conversation depth at drop
        for msg in reversed(messages):  # last bot message
            if msg["sender"] == "bot":
                last_bot_messages[msg["text"][:80]] += 1
                break
        for msg in reversed(messages):  # active intent at drop
            if msg.get("intent"):
                intent_at_drop[msg["intent"]] += 1
                break
    return {
        "drop_off_by_depth": dict(drop_offs.most_common(20)),
        "drop_off_by_intent": dict(intent_at_drop.most_common(10)),
        "drop_off_by_last_bot_msg": dict(last_bot_messages.most_common(10)),
    }


def detect_conversation_loops(conversations: list[dict], threshold: int = 3) -> list[dict]:
    """Flag sessions where the bot repeats the same response >= threshold times
    in a row, indicating the user is stuck in a loop."""
    looped = []
    for convo in conversations:
        bot_msgs = [m["text"] for m in convo.get("messages", []) if m["sender"] == "bot"]
        repeat = 1
        for i in range(1, len(bot_msgs)):
            if bot_msgs[i] == bot_msgs[i - 1]:
                repeat += 1
                if repeat >= threshold:
                    looped.append({
                        "session_id": convo["session_id"],
                        "repeated_message": bot_msgs[i][:100],
                        "repeat_count": repeat,
                        "total_messages": len(convo["messages"]),
                    })
                    break
            else:
                repeat = 1
    return looped
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

    def _score(self, probs) -> dict:
        """Turn a probability row into a {label, score, scores} dict."""
        scores = {lbl: round(p.item(), 4) for lbl, p in zip(self.labels, probs)}
        best = max(scores, key=scores.get)
        return {"label": best, "score": scores[best], "scores": scores}

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of a single Hebrew string."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=512, padding=True)
        with torch.no_grad():
            probs = torch.softmax(self.model(**inputs).logits, dim=-1)
        return self._score(probs[0])

    def analyze_batch(self, texts: list[str], batch_size: int = 32) -> list[dict]:
        """Analyze sentiment for a batch of Hebrew texts."""
        results = []
        for i in range(0, len(texts), batch_size):
            inputs = self.tokenizer(texts[i:i + batch_size], return_tensors="pt",
                                    truncation=True, max_length=512, padding=True)
            with torch.no_grad():
                probs = torch.softmax(self.model(**inputs).logits, dim=-1)
            results.extend(self._score(row) for row in probs)
        return results
```

**Hebrew-specific sentiment challenges (summary):**

1. **Negation**: "לא" before an adjective flips meaning. "לא רע" (not bad) reads mildly positive in Israeli usage.
2. **Sarcasm and irony**: very common in Israeli communication ("יופי, בדיוק מה שחיכיתי לו" can be deeply negative). DictaBERT handles some of it; fine-tune on domain data for better coverage.
3. **Slang**: evolves fast. "אחלה" / "סבבה" / "בומבה" are positive, "חרא" / "פאדיחה" are negative, "וואלה" is context-dependent.
4. **Mixed Hebrew-English**: users mix English words into Hebrew ("ה-support שלכם גרוע"). Ensure your model or lexicon handles both scripts in one message.

See `references/hebrew-sentiment-guide.md` for the full treatment of these challenges, including the slang lexicon and negation-handling code.

### Step 5: Intent Recognition Accuracy Tracking

Track how well your chatbot understands user requests over time:

```python
import numpy as np
from collections import defaultdict

class IntentAccuracyTracker:
    """Track and analyze intent recognition accuracy."""

    def __init__(self):
        self.predictions = []                    # list of prediction dicts
        self.daily_accuracy = defaultdict(list)  # date -> [correct bools]

    def log_prediction(self, predicted_intent: str, actual_intent: str,
                       confidence: float, timestamp: str):
        """Log a single intent prediction for analysis."""
        correct = predicted_intent == actual_intent
        self.predictions.append({
            "predicted": predicted_intent, "actual": actual_intent,
            "confidence": confidence, "correct": correct, "timestamp": timestamp,
        })
        self.daily_accuracy[timestamp[:10]].append(correct)

    def confusion_matrix(self) -> dict:
        """Build a confusion matrix: returns 'matrix' (2D dict) + sorted 'intents'."""
        matrix = defaultdict(lambda: defaultdict(int))
        intents = set()
        for p in self.predictions:
            matrix[p["actual"]][p["predicted"]] += 1
            intents.update((p["actual"], p["predicted"]))
        si = sorted(intents)
        return {
            "matrix": {a: {pr: matrix[a][pr] for pr in si} for a in si},
            "intents": si,
        }

    def misclassification_report(self, min_count: int = 5) -> list[dict]:
        """Most common misclassification pairs with count >= min_count."""
        misclass = Counter()
        for p in self.predictions:
            if not p["correct"]:
                misclass[(p["actual"], p["predicted"])] += 1
        return [
            {"actual_intent": a, "predicted_as": pr, "count": c}
            for (a, pr), c in misclass.most_common() if c >= min_count
        ]

    def low_confidence_intents(self, threshold: float = 0.6) -> dict:
        """Intents whose average prediction confidence falls below threshold."""
        by_intent = defaultdict(list)
        for p in self.predictions:
            by_intent[p["predicted"]].append(p["confidence"])
        low = {}
        for intent, confs in by_intent.items():
            avg = statistics.mean(confs)
            if avg < threshold:
                low[intent] = {
                    "avg_confidence": round(avg, 3),
                    "sample_count": len(confs),
                    "below_threshold_pct": round(
                        sum(c < threshold for c in confs) / len(confs) * 100, 1),
                }
        return dict(sorted(low.items(), key=lambda x: x[1]["avg_confidence"]))

    def accuracy_trend(self) -> list[dict]:
        """Daily accuracy trend for plotting: list of date/accuracy/sample_count."""
        return [
            {"date": d, "accuracy": round(sum(r) / len(r), 4), "sample_count": len(r)}
            for d, r in sorted(self.daily_accuracy.items())
        ]
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
        """Composite satisfaction score (0.0-1.0). Direct CSAT wins if present."""
        if self.csat_score is not None:
            return round((self.csat_score - 1) / 4, 2)  # normalize 1-5 to 0-1

        score = 0.5  # start neutral
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
        score += {"positive": 0.1, "neutral": 0.0, "negative": -0.15}.get(
            self.final_sentiment, 0)
        score += {"improving": 0.05, "stable": 0.0, "declining": -0.1}.get(
            self.sentiment_trend, 0)
        return round(max(0.0, min(1.0, score)), 2)


def collect_post_chat_survey_he() -> dict:
    """Hebrew post-chat survey template for integration with your chat platform."""
    return {
        "title": "נשמח לשמוע מה חשבת",
        "questions": [
            {"id": "satisfaction", "type": "rating",
             "text": "עד כמה הצ'אטבוט עזר לך?", "scale": {"min": 1, "max": 5},
             "labels": {1: "לא עזר בכלל", 2: "עזר מעט", 3: "עזר בינוני",
                        4: "עזר טוב", 5: "עזר מצוין"}},
            {"id": "understood", "type": "yes_no",
             "text": "האם הצ'אטבוט הבין את מה שרצית?"},
            {"id": "open_feedback", "type": "free_text",
             "text": "רוצה לשתף עוד משהו? (לא חובה)", "required": False},
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

    def create_test(self, test_id: str, variants: dict[str, str],
                    traffic_split: dict[str, float] | None = None):
        """Create a new A/B test.

        variants: variant_name -> response_text. traffic_split: variant_name ->
        percentage (0-1), defaults to equal split. Example variants:
        {"formal": "שלום וברוכים הבאים. כיצד נוכל לסייע לכם?",
         "casual": "היי! איך אפשר לעזור?",
         "gender_neutral": "שלום! ניתן לבחור מהאפשרויות הבאות:"}
        """
        if traffic_split is None:
            traffic_split = {name: 1.0 / len(variants) for name in variants}
        self.active_tests[test_id] = {
            "variants": variants, "traffic_split": traffic_split,
            "created_at": datetime.now().isoformat(),
        }

    def assign_variant(self, test_id: str, user_id: str) -> str:
        """Deterministically assign a user to a variant (same user, same variant)."""
        test = self.active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")
        hash_val = int(hashlib.md5(f"{user_id}:{test_id}".encode()).hexdigest(), 16)
        bucket = (hash_val % 1000) / 1000.0
        cumulative = 0.0
        for name, split in test["traffic_split"].items():
            cumulative += split
            if bucket < cumulative:
                return name
        return list(test["traffic_split"].keys())[-1]

    def get_response(self, test_id: str, user_id: str) -> tuple[str, str]:
        """Return (variant_name, response_text) and track an impression."""
        variant = self.assign_variant(test_id, user_id)
        self.results[f"{test_id}:{variant}"]["impressions"] += 1
        return variant, self.active_tests[test_id]["variants"][variant]

    def record_outcome(self, test_id: str, variant: str, completed: bool = False,
                       satisfaction: float | None = None, escalated: bool = False):
        """Record the outcome for a test variant."""
        r = self.results[f"{test_id}:{variant}"]
        if completed:
            r["completions"] += 1
        if satisfaction is not None:
            r["satisfaction_scores"].append(satisfaction)
        if escalated:
            r["escalations"] += 1

    def get_test_results(self, test_id: str) -> dict:
        """Get a results summary (completion + escalation rates, avg satisfaction)."""
        test = self.active_tests.get(test_id)
        if not test:
            return {}
        summary = {}
        for name in test["variants"]:
            data = self.results[f"{test_id}:{name}"]
            imp = data["impressions"]
            summary[name] = {
                "impressions": imp,
                "completion_rate": round(data["completions"] / imp, 4) if imp else 0,
                "avg_satisfaction": (round(statistics.mean(data["satisfaction_scores"]), 2)
                                     if data["satisfaction_scores"] else None),
                "escalation_rate": round(data["escalations"] / imp, 4) if imp else 0,
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
        """Format metrics into grouped sections for reporting."""
        return {
            "core": {
                "total_conversations": self.total_conversations,
                "resolution_rate": f"{self.resolution_rate:.1%}",
                "first_contact_resolution": f"{self.first_contact_resolution:.1%}",
                "avg_handle_time": f"{self.avg_handle_time_seconds:.0f}s",
                "escalation_rate": f"{self.escalation_rate:.1%}",
                "abandonment_rate": f"{self.abandonment_rate:.1%}",
            },
            "satisfaction": {"avg_csat": f"{self.avg_csat:.1f}/5",
                             "nps": f"{self.nps_score:+.0f}",
                             "thumbs_up": f"{self.thumbs_up_ratio:.1%}"},
            "accuracy": {"intent_accuracy": f"{self.intent_accuracy:.1%}",
                         "fallback_rate": f"{self.fallback_rate:.1%}"},
            "performance": {"avg_response_time": f"{self.avg_response_time_ms:.0f}ms",
                            "p95_response_time": f"{self.p95_response_time_ms:.0f}ms"},
            "volume": {"daily_avg": f"{self.conversations_per_day:.0f}",
                       "peak_hour": f"{self.peak_hour}:00",
                       "busiest_day": self.busiest_day},
        }


def build_dashboard(conversations: list[dict], period_days: int = 7) -> ChatbotDashboard:
    """Build a dashboard from conversation logs."""
    d = ChatbotDashboard()
    d.total_conversations = len(conversations)
    if not conversations:
        return d
    n = len(conversations)

    # Outcome rates
    outcomes = Counter(c.get("outcome", "unknown") for c in conversations)
    d.resolution_rate = outcomes.get("resolved", 0) / n
    d.escalation_rate = outcomes.get("escalated", 0) / n
    d.abandonment_rate = outcomes.get("abandoned", 0) / n

    # Handle time
    durations = [
        (datetime.fromisoformat(c["ended_at"]) - datetime.fromisoformat(c["started_at"])).total_seconds()
        for c in conversations if c.get("started_at") and c.get("ended_at")
    ]
    if durations:
        d.avg_handle_time_seconds = statistics.mean(durations)

    # CSAT
    csat = [c["satisfaction_score"] for c in conversations if c.get("satisfaction_score") is not None]
    if csat:
        d.avg_csat = statistics.mean(csat)

    # Response times (avg + p95)
    rts = [
        m["response_time_ms"] for c in conversations for m in c.get("messages", [])
        if m["sender"] == "bot" and m.get("response_time_ms")
    ]
    if rts:
        d.avg_response_time_ms = statistics.mean(rts)
        sorted_rt = sorted(rts)
        d.p95_response_time_ms = sorted_rt[min(int(len(sorted_rt) * 0.95), len(sorted_rt) - 1)]

    # Intent accuracy + fallback rate (uses confidence > 0.7 as a proxy for correct)
    total_intents = correct = fallbacks = total_msgs = 0
    for c in conversations:
        for m in c.get("messages", []):
            if m["sender"] != "user":
                continue
            total_msgs += 1
            if m.get("intent"):
                total_intents += 1
                if m.get("intent_confidence", 0) > 0.7:
                    correct += 1
                if m["intent"] == "fallback":
                    fallbacks += 1
    if total_intents:
        d.intent_accuracy = correct / total_intents
    if total_msgs:
        d.fallback_rate = fallbacks / total_msgs

    # Volume, peak hour, busiest day
    d.conversations_per_day = n / max(period_days, 1)
    hours, days = Counter(), Counter()
    for c in conversations:
        if c.get("started_at"):
            dt = datetime.fromisoformat(c["started_at"])
            hours[dt.hour] += 1
            days[dt.strftime("%A")] += 1
    if hours:
        d.peak_hour = hours.most_common(1)[0][0]
    if days:
        d.busiest_day = days.most_common(1)[0][0]

    return d
```

**Israeli traffic patterns to expect:**
- Peak hours are typically 10:00-12:00 and 19:00-22:00 (Israel Time, UTC+2/+3)
- Sunday is the busiest day (first workday of the Israeli week)
- Friday afternoon and Saturday see minimal traffic
- Holiday periods (Rosh Hashana, Pesach, Sukkot) show different patterns

#### Retention and Returning-User Metrics

Session-level metrics tell you how a single conversation went, but not whether the bot earns repeat use. Track these retention dimensions alongside the dashboard above (all require a stable `user_id` across sessions, pseudonymized per the Privacy and Consent section):

```python
from datetime import datetime, timedelta

def compute_retention_metrics(conversations: list[dict]) -> dict:
    """Compute D1/D7 return rate and repeat-contact rate from logs."""
    # Map each user to the set of dates they had a conversation.
    user_days: dict[str, set] = {}
    for c in conversations:
        uid, started = c.get("user_id"), c.get("started_at")
        if uid and started:
            user_days.setdefault(uid, set()).add(
                datetime.fromisoformat(started).date())

    d1 = d7 = repeat = 0
    for days in user_days.values():
        first = min(days)
        if len(days) > 1:
            repeat += 1
        if (first + timedelta(days=1)) in days:
            d1 += 1
        if any(first + timedelta(days=n) in days for n in range(2, 8)):
            d7 += 1

    n = len(user_days) or 1
    return {
        "d1_return_rate": round(d1 / n, 4),
        "d7_return_rate": round(d7 / n, 4),
        "repeat_contact_rate": round(repeat / n, 4),
        "unique_users": len(user_days),
    }
```

- **D1 / D7 return rate**: share of users who start a new conversation the day after, or within a week of, their first contact. D7 is more stable than D1 for low-volume Israeli bots.
- **Repeat-contact rate**: share of users with more than one conversation. On a support bot this can be good (trust) or bad (unresolved issues), so read it with first-contact resolution.

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
# AlertRule(name, metric, operator, threshold, window_minutes, severity, description_he)
DEFAULT_ALERT_RULES = [
    AlertRule("high_escalation_rate", "escalation_rate", "gt", 0.35, 60, "warning",
              "שיעור הסלמה גבוה מ-35% בשעה האחרונה"),
    AlertRule("satisfaction_drop", "avg_csat", "lt", 3.0, 120, "critical",
              "שביעות רצון ממוצעת ירדה מתחת ל-3.0 בשעתיים האחרונות"),
    AlertRule("high_abandonment", "abandonment_rate", "gt", 0.40, 60, "critical",
              "שיעור נטישה גבוה מ-40% בשעה האחרונה"),
    AlertRule("high_fallback_rate", "fallback_rate", "gt", 0.25, 30, "warning",
              "שיעור fallback גבוה מ-25% בחצי שעה האחרונה"),
    AlertRule("slow_response", "p95_response_time_ms", "gt", 3000, 15, "warning",
              "זמן תגובה P95 חורג מ-3 שניות ברבע השעה האחרון"),
    AlertRule("new_unrecognized_intents", "new_unknown_intents_count", "gt", 20, 60,
              "info", "יותר מ-20 כוונות לא מזוהות חדשות בשעה האחרונה"),
]


class AlertManager:
    """Monitor metrics and trigger alerts."""

    def __init__(self, rules: list[AlertRule] | None = None):
        self.rules = rules or DEFAULT_ALERT_RULES
        self.triggered_alerts = []

    def check_metrics(self, current_metrics: dict) -> list[dict]:
        """Check current metrics (metric_name -> value) against the rules."""
        alerts = []
        for rule in self.rules:
            value = current_metrics.get(rule.metric)
            if value is None:
                continue
            triggered = ((rule.operator == "gt" and value > rule.threshold)
                         or (rule.operator == "lt" and value < rule.threshold))
            if triggered:
                alert = {
                    "rule_name": rule.name, "severity": rule.severity,
                    "metric": rule.metric, "current_value": value,
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
def generate_weekly_report(dashboard: ChatbotDashboard,
                           previous_dashboard: ChatbotDashboard | None = None,
                           period_start: str = "", period_end: str = "") -> str:
    """Generate a Hebrew weekly performance report (with week-over-week trends)."""

    def trend_arrow(current: float, previous: float, higher_is_better: bool = True) -> str:
        if previous == 0:
            return ""
        pct = ((current - previous) / previous) * 100
        if abs(pct) < 1:
            return "(ללא שינוי)"
        good = (current - previous > 0) == higher_is_better
        arrow = "+" if current - previous > 0 else ""
        return f"{'[v]' if good else '[!]'} {arrow}{pct:.1f}%"

    d, prev = dashboard, previous_dashboard
    # (label, formatted value, current, previous, higher_is_better)
    rows = [
        ("שיחות", f"{d.total_conversations:,}", d.total_conversations,
         prev.total_conversations if prev else 0, True),
        ("שיעור פתרון", f"{d.resolution_rate:.1%}", d.resolution_rate,
         prev.resolution_rate if prev else 0, True),
        ("שביעות רצון (CSAT)", f"{d.avg_csat:.1f}/5", d.avg_csat,
         prev.avg_csat if prev else 0, True),
        ("שיעור הסלמה", f"{d.escalation_rate:.1%}", d.escalation_rate,
         prev.escalation_rate if prev else 0, False),
        ("שיעור נטישה", f"{d.abandonment_rate:.1%}", d.abandonment_rate,
         prev.abandonment_rate if prev else 0, False),
        ("דיוק זיהוי כוונות", f"{d.intent_accuracy:.1%}", d.intent_accuracy,
         prev.intent_accuracy if prev else 0, True),
        ("זמן תגובה ממוצע", f"{d.avg_response_time_ms:.0f}ms", d.avg_response_time_ms,
         prev.avg_response_time_ms if prev else 0, False),
    ]
    lines = [
        "# דוח ביצועי צ'אטבוט שבועי",
        f"## תקופה: {period_start} עד {period_end}",
        "", "## מדדים מרכזיים", "",
        "| מדד | ערך | שינוי מהשבוע הקודם |",
        "|------|------|---------------------|",
    ]
    for name, value, cur, prv, hib in rows:
        lines.append(f"| {name} | {value} | {trend_arrow(cur, prv, hib)} |")
    lines += [
        "", "## תנועה",
        f"- ממוצע שיחות ביום: {d.conversations_per_day:.0f}",
        f"- שעת שיא: {d.peak_hour}:00",
        f"- יום עמוס ביותר: {d.busiest_day}",
    ]
    return "\n".join(lines)
```

### Step 12: Integration with Chatbot Platforms

#### Dialogflow CX Analytics

```python
def parse_dialogflow_cx_logs(bigquery_rows: list[dict]) -> list[dict]:
    """Transform a Dialogflow CX BigQuery export to the standard format.

    Export query: SELECT * FROM `project.dataset.dialogflow_cx_interactions`
    WHERE DATE(request_time) BETWEEN @start AND @end
    """
    sessions = defaultdict(lambda: {"messages": [], "started_at": None, "ended_at": None})
    for row in bigquery_rows:
        s = sessions[row["session_id"]]
        ts = row["request_time"]
        if s["started_at"] is None or ts < s["started_at"]:
            s["started_at"] = ts
        if s["ended_at"] is None or ts > s["ended_at"]:
            s["ended_at"] = ts
        if row.get("query_text"):
            s["messages"].append({
                "timestamp": ts, "sender": "user", "text": row["query_text"],
                "intent": row.get("matched_intent", ""),
                "intent_confidence": row.get("intent_confidence", 0),
            })
        if row.get("response_text"):
            s["messages"].append({
                "timestamp": ts, "sender": "bot", "text": row["response_text"],
            })

    conversations = []
    for sid, s in sessions.items():
        s["messages"].sort(key=lambda m: m["timestamp"])
        conversations.append({
            "session_id": sid, "started_at": s["started_at"],
            "ended_at": s["ended_at"], "messages": s["messages"],
            "outcome": "unknown",  # derive from flow completion
            "language": "he",
        })
    return conversations
```

#### Rasa Tracker Store Analytics

Note: Rasa Open Source is in maintenance mode. The intent-based tracker-store analytics below apply to existing Rasa OSS deployments; new Rasa builds use CALM (Conversational AI with Language Models), which is dialogue-driven rather than intent-driven, so intent-accuracy metrics map differently there. See the legacy OSS docs at https://legacy-docs-oss.rasa.com/docs/rasa/ for tracker-store details.

```python
def parse_rasa_tracker_events(tracker_events: list[dict]) -> list[dict]:
    """Transform Rasa tracker-store events to the standard format.

    Query: SELECT * FROM events WHERE sender_id = @sender_id ORDER BY timestamp
    """
    conversations = []
    current = {"messages": [], "started_at": None, "ended_at": None}

    for event in tracker_events:
        et = event.get("event")
        ts = event.get("timestamp", "")
        if et == "session_started":
            if current["messages"]:
                conversations.append(current)
            current = {
                "session_id": event.get("metadata", {}).get("session_id", ""),
                "messages": [], "started_at": ts, "ended_at": None,
                "outcome": "unknown", "language": "he",
            }
        elif et == "user":
            current["ended_at"] = ts
            intent = event.get("parse_data", {}).get("intent", {})
            current["messages"].append({
                "timestamp": ts, "sender": "user", "text": event.get("text", ""),
                "intent": intent.get("name", ""),
                "intent_confidence": intent.get("confidence", 0),
            })
        elif et == "bot":
            current["ended_at"] = ts
            current["messages"].append({
                "timestamp": ts, "sender": "bot", "text": event.get("text", ""),
            })
        elif et == "action" and event.get("name") == "action_human_handoff":
            current["outcome"] = "escalated"

    if current["messages"]:
        conversations.append(current)
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

## Privacy and Consent

This skill ingests full conversation transcripts and `user_id` values, and runs sentiment analysis on user messages. Conversation text is personal data and often contains sensitive content (health, finances, complaints). Handle it under Israel's Privacy Protection Law, including Amendment 13 (in force August 2025), which tightened consent, notice, accountability, and data-minimization obligations.

Practical rules:

- **Consent and notice.** Get consent to store and analyze chat content, and tell users in your privacy notice that conversations are retained and analyzed for quality. Sentiment analysis on user messages is a processing purpose that should be disclosed.
- **Pseudonymize `user_id`.** Do not analyze raw phone numbers, emails, or Teudat Zehut as the identifier. Hash or tokenize `user_id` before it reaches the analytics pipeline, and keep the mapping table separate and access-controlled. Retention and A/B-test bucketing still work on a stable pseudonymous ID.
- **Minimize and redact.** Strip or mask entities you do not need for analytics (ID numbers, full names, card numbers) before storing transcripts. You rarely need the raw PII to measure drop-off or sentiment.
- **Retention limits.** Set an explicit retention window for raw transcripts (for example 90 days) and keep only aggregated metrics long-term. Document the window and delete on schedule.
- **Access control and location.** Restrict who can read raw conversations, log access, and confirm where the data is stored and processed.
- This is engineering guidance, not legal advice. Confirm your specific obligations with a privacy professional.

## Recommended MCP Servers

No MCP server is required for this skill. It operates entirely on exported conversation logs (BigQuery exports, Rasa tracker-store dumps, application log files) that you load from disk and analyze locally with the bundled Python script. There is no live API to wrap, so no MCP integration is needed.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Dialogflow CX analytics | https://cloud.google.com/dialogflow/cx/docs/concept/analytics | Built-in conversation analytics, intent metrics |
| Rasa OSS documentation (legacy) | https://legacy-docs-oss.rasa.com/docs/rasa/ | Event tracking, tracker stores, custom analytics integrations |
| Mixpanel help | https://mixpanel.com/help | Funnel analysis, cohort retention for chat flows |
| Matomo analytics | https://matomo.org/docs/ | Self-hosted event tracking, privacy-friendly |
| HuggingFace Hebrew models | https://huggingface.co/models?language=he | Hebrew sentiment/classification models |

## Troubleshooting

- **DictaBERT model not loading**: the `dicta-il/dictabert-sentiment` model needs PyTorch + `transformers` (~500MB). Run `pip install torch transformers`; for CPU-only, install torch from `https://download.pytorch.org/whl/cpu`.
- **Hebrew text appears reversed in charts**: matplotlib has no native RTL. Apply `python-bidi` (`bidi.algorithm.get_display()`) before rendering, or switch to Plotly.
- **Tokenization produces wrong word frequencies**: whitespace splitting ignores Hebrew prefix particles. Use the prefix-stripping tokenizer in Step 9, or the YAP morphological analyzer (https://github.com/OnlpLab/yap) for production.
- **Sentiment scores unreliable for short messages**: messages of 1-3 words lack context ("סבבה" can be positive or neutral). For under 4 words, rely on behavioral signals (continued / escalated / abandoned) instead, combined with satisfaction signals from Step 6.
- **A/B test results not statistically significant**: usually insufficient sample size, common for smaller Israeli user bases. Run at least 2 weeks, aim for 200+ impressions per variant, target p < 0.05.
