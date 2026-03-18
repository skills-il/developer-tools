---
name: israeli-chatbot-analytics
description: >-
  ניתוח ואופטימיזציה של ביצועי צ'אטבוטים בעברית, כולל אנליטיקת זרימת שיחה,
  ניתוח רגשות בעברית, זיהוי נקודות נטישה, מדידת שביעות רצון, בדיקות A/B
  לווריאציות תגובה, מעקב דיוק זיהוי כוונות, ודשבורדים לדיווח. להשתמש כשמבקשים
  "לנתח ביצועי צ'אטבוט", "למדוד שביעות רצון מבוט", "לעקוב אחרי מדדי בוט",
  "analitika shel tsatbot", או כשצריכים עזרה באנליטיקת שיחות, מעקב דיוק כוונות,
  או דוחות צ'אטבוט. תומך ב-Dialogflow, Rasa ופלטפורמות מותאמות אישית. לא
  להשתמש לבניית צ'אטבוטים (יש hebrew-chatbot-builder), אימון מודלי NLP בעברית
  (יש hebrew-nlp-toolkit), הקמת מערכת תמיכה (יש israeli-customer-support-automator),
  או פיתוח בוט קולי (יש hebrew-voice-bot-builder).
license: MIT
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
---

# אנליטיקת צ'אטבוטים ישראלית

ניתוח ואופטימיזציה של ביצועי צ'אטבוטים בעברית. הסקיל הזה מכסה אנליטיקת זרימת שיחה, ניתוח רגשות ייחודי לעברית, זיהוי נקודות נטישה, מדידת שביעות רצון, בדיקות A/B לווריאציות תגובה בעברית, מעקב דיוק זיהוי כוונות, התראות חריגים, ודשבורדים לדיווח. בעזרתו אפשר להבין אם הצ'אטבוט שלכם באמת עוזר למשתמשים ואיפה צריך לשפר.

## הוראות

### שלב 1: איסוף ומבנה לוגים של שיחות

לפני הניתוח, ודאו שהנתונים מובנים באופן אחיד. כל סשן שיחה צריך לכלול:

```python
# סכמה סטנדרטית ללוג שיחות
conversation_log = {
    "session_id": "uuid-string",
    "user_id": "anonymous-or-identified",
    "channel": "whatsapp|telegram|web|app",
    "language": "he",           # שפה ראשית שזוהתה
    "started_at": "ISO-8601",
    "ended_at": "ISO-8601",
    "messages": [
        {
            "timestamp": "ISO-8601",
            "sender": "user|bot",
            "text": "שלום, אני צריך עזרה",
            "intent": "greeting",           # כוונה שזוהתה
            "intent_confidence": 0.92,       # רמת ביטחון המודל
            "entities": [],                  # ישויות שחולצו
            "response_time_ms": 340,         # זמן תגובת הבוט
        }
    ],
    "outcome": "resolved|escalated|abandoned|unknown",
    "satisfaction_score": null,   # ציון CSAT אם נאסף
    "metadata": {
        "bot_version": "2.1.0",
        "ab_variant": "formal_he",
    }
}
```

אם הפלטפורמה שלכם לא מייצאת בפורמט הזה, כתבו transformer שינרמל את הלוגים. פלטפורמות נפוצות:

| פלטפורמה | שיטת ייצוא | פורמט |
|-----------|------------|-------|
| Dialogflow CX | ייצוא BigQuery | שורות JSON עם הקשר סשן |
| Rasa | Tracker Store (SQL/Mongo) | רשימת אירועים לכל שיחה |
| בוטים מותאמים | לוגי אפליקציה | משתנה (לנרמל לסכמה למעלה) |
| WhatsApp Cloud API | לוגי Webhook | אובייקטי הודעות עם metadata |

### שלב 2: ניתוח זרימת שיחה

ניתוח מדדים ברמת הסשן כדי להבין את בריאות הצ'אטבוט:

```python
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import statistics

@dataclass
class ConversationMetrics:
    """חישוב מדדים ברמת סשן מלוגים של שיחות."""

    total_sessions: int = 0
    completed_sessions: int = 0
    escalated_sessions: int = 0
    abandoned_sessions: int = 0

    session_lengths: list = field(default_factory=list)    # מספרי הודעות
    session_durations: list = field(default_factory=list)  # שניות

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


def compute_flow_metrics(conversations: list[dict]) -> ConversationMetrics:
    """ניתוח זרימת שיחה מלוגים מובנים."""
    metrics = ConversationMetrics()

    for convo in conversations:
        metrics.total_sessions += 1
        msg_count = len(convo.get("messages", []))
        metrics.session_lengths.append(msg_count)

        started = datetime.fromisoformat(convo["started_at"])
        ended = datetime.fromisoformat(convo.get("ended_at", convo["started_at"]))
        metrics.session_durations.append((ended - started).total_seconds())

        outcome = convo.get("outcome", "unknown")
        if outcome == "resolved":
            metrics.completed_sessions += 1
        elif outcome == "escalated":
            metrics.escalated_sessions += 1
        elif outcome == "abandoned":
            metrics.abandoned_sessions += 1

    return metrics
```

**בנצ'מרקים לצ'אטבוטים בעברית (שוק ישראלי, 2025-2026):**

| מדד | טוב | ממוצע | דורש שיפור |
|------|------|--------|------------|
| שיעור השלמה | > 70% | 50-70% | < 50% |
| שיעור הסלמה | < 15% | 15-30% | > 30% |
| שיעור נטישה | < 20% | 20-35% | > 35% |
| אורך סשן ממוצע | 4-8 הודעות | 8-15 הודעות | > 15 הודעות |
| פתרון במגע ראשון | > 65% | 45-65% | < 45% |

### שלב 3: זיהוי נקודות נטישה

זיהוי המקומות שבהם משתמשים נוטשים את השיחה. זה חושף בעיות UX, הודעות מבלבלות, או יכולות חסרות:

```python
def detect_drop_off_points(conversations: list[dict]) -> dict:
    """מציאת נקודות נטישה נפוצות.

    מחזיר מיפוי של (כוונה, אינדקס הודעה) לספירת נטישות.
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

        # איפה בזרימה הם עזבו?
        drop_index = len(messages)
        drop_offs[drop_index] += 1

        # מה הייתה ההודעה האחרונה של הבוט?
        for msg in reversed(messages):
            if msg["sender"] == "bot":
                last_bot_messages[msg["text"][:80]] += 1
                break

        # איזו כוונה הייתה פעילה?
        for msg in reversed(messages):
            if msg.get("intent"):
                intent_at_drop[msg["intent"]] += 1
                break

    return {
        "drop_off_by_depth": dict(drop_offs.most_common(20)),
        "drop_off_by_intent": dict(intent_at_drop.most_common(10)),
        "drop_off_by_last_bot_msg": dict(last_bot_messages.most_common(10)),
    }


def detect_conversation_loops(conversations: list[dict], threshold: int = 3) -> list[dict]:
    """זיהוי שיחות שבהן הבוט חוזר על אותה תגובה (המשתמש תקוע בלולאה).

    Args:
        conversations: רשימת שיחות.
        threshold: מספר חזרות שמסמנות לולאה.
    """
    looped_sessions = []

    for convo in conversations:
        bot_messages = [
            m["text"] for m in convo.get("messages", [])
            if m["sender"] == "bot"
        ]

        repeat_count = 1
        for i in range(1, len(bot_messages)):
            if bot_messages[i] == bot_messages[i - 1]:
                repeat_count += 1
                if repeat_count >= threshold:
                    looped_sessions.append({
                        "session_id": convo["session_id"],
                        "repeated_message": bot_messages[i][:100],
                        "repeat_count": repeat_count,
                    })
                    break
            else:
                repeat_count = 1

    return looped_sessions
```

### שלב 4: ניתוח רגשות בעברית

ניתוח רגשות בעברית דורש טיפול מיוחד בגלל המורפולוגיה המורכבת, דפוסי שלילה, וסלנג. משתמשים ב-DictaBERT או DictaLM לדיוק בסביבת ייצור, או בגישה מבוססת מילון לניתוח קל.

**שימוש ב-DictaBERT (מומלץ לייצור):**

```python
# DictaBERT: מודל BERT לעברית של דיקטה (אוניברסיטת בר-אילן)
# אומן מראש על 10+ מיליארד טוקנים בעברית
# https://huggingface.co/dicta-il/dictabert

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class HebrewSentimentAnalyzer:
    """ניתוח רגשות בעברית באמצעות מודל DictaBERT."""

    def __init__(self, model_name: str = "dicta-il/dictabert-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.labels = ["negative", "neutral", "positive"]

    def analyze(self, text: str) -> dict:
        """ניתוח רגשות של טקסט בעברית."""
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512, padding=True,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)

        scores = {
            label: round(prob.item(), 4)
            for label, prob in zip(self.labels, probabilities[0])
        }
        best_label = max(scores, key=scores.get)
        return {"label": best_label, "score": scores[best_label], "scores": scores}
```

**אתגרים ייחודיים בניתוח רגשות בעברית:**

1. **שלילה עם תחיליות**: בעברית השלילה מגיעה כמילה נפרדת ("לא") לפני שמות תואר, ויכולה להפוך את המשמעות. "לא רע" בשימוש ישראלי הוא חיובי קלות.

2. **סרקזם ואירוניה**: תקשורת ישראלית מלאה בסרקזם. "יופי, בדיוק מה שחיכיתי לו" יכול להיות שלילי מאוד. DictaBERT מתמודד עם חלק מהסרקזם; לכיסוי טוב יותר, עשו fine-tune על הנתונים שלכם.

3. **סלנג וקיצורים**: הסלנג הישראלי משתנה מהר. דפוסים נפוצים:
   - "אחלה" (מערבית) = מעולה/חיובי
   - "סבבה" = בסדר/מגניב
   - "בומבה" = מדהים
   - "חרא" = נורא
   - "פאדיחה" (מערבית) = מביך/גרוע
   - "וואלה" = באמת?/וואו (תלוי הקשר)

4. **עירוב עברית-אנגלית**: משתמשים ישראליים מערבבים מילים באנגלית לתוך משפטים בעברית. ודאו שהמודל מתמודד עם "ה-support שלכם גרוע".

ראו `references/hebrew-sentiment-guide.md` לעזר מפורט.

### שלב 5: מעקב דיוק זיהוי כוונות

מעקב אחרי רמת הדיוק של הצ'אטבוט בהבנת בקשות משתמשים:

```python
from collections import defaultdict, Counter
import statistics

class IntentAccuracyTracker:
    """מעקב וניתוח דיוק זיהוי כוונות."""

    def __init__(self):
        self.predictions = []
        self.daily_accuracy = defaultdict(list)

    def log_prediction(self, predicted_intent: str, actual_intent: str,
                       confidence: float, timestamp: str):
        """רישום תחזית כוונה בודדת לניתוח."""
        correct = predicted_intent == actual_intent
        self.predictions.append({
            "predicted": predicted_intent,
            "actual": actual_intent,
            "confidence": confidence,
            "correct": correct,
            "timestamp": timestamp,
        })
        self.daily_accuracy[timestamp[:10]].append(correct)

    def confusion_matrix(self) -> dict:
        """בניית מטריצת בלבול לסיווג כוונות."""
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
        """זיהוי הטעויות הנפוצות ביותר בסיווג."""
        misclass = Counter()
        for pred in self.predictions:
            if not pred["correct"]:
                misclass[(pred["actual"], pred["predicted"])] += 1
        return [
            {"actual_intent": a, "predicted_as": p, "count": c}
            for (a, p), c in misclass.most_common() if c >= min_count
        ]

    def accuracy_trend(self) -> list[dict]:
        """מגמת דיוק יומית לגרף."""
        return [
            {
                "date": date,
                "accuracy": round(sum(r) / len(r), 4),
                "sample_count": len(r),
            }
            for date, r in sorted(self.daily_accuracy.items())
        ]
```

**איך להשיג תיוגים אמיתיים (ground truth):**

- **תיוג ידני**: דגמו 100-200 שיחות בשבוע ותנו לאנוטטורים דוברי עברית לתייג את הכוונות האמיתיות. זה הסטנדרט הטוב ביותר.
- **סיגנלי הסלמה**: כשמשתמש מתקן במפורש את הבוט ("לא, התכוונתי ל...") או מבקש נציג אנושי אחרי אי הבנה, סמנו את הכוונה הקודמת כשגויה.
- **סקרים אחרי שיחה**: שאלו "האם הבוט הבין מה רצית?" וחברו עם הכוונה שזוהתה.

### שלב 6: מדידת שביעות רצון

שילוב מספר סיגנלים לציון שביעות רצון מורכב:

```python
from dataclasses import dataclass

@dataclass
class SatisfactionSignals:
    """שילוב סיגנלי שביעות רצון לציון מורכב."""

    # משוב ישיר
    csat_score: float | None = None      # סקאלה 1-5
    thumbs_rating: str | None = None     # "up" או "down"

    # סיגנלים התנהגותיים
    session_resolved: bool = False
    escalated_to_human: bool = False
    abandoned: bool = False
    repeated_fallbacks: int = 0
    loop_detected: bool = False

    # סיגנלי רגשות
    final_sentiment: str = "neutral"
    sentiment_trend: str = "stable"      # improving/stable/declining

    def composite_score(self) -> float:
        """חישוב ציון שביעות רצון מורכב (0.0 עד 1.0)."""
        score = 0.5  # התחלה ניטרלית

        if self.csat_score is not None:
            return round((self.csat_score - 1) / 4, 2)

        if self.thumbs_rating == "up":
            score = 0.8
        elif self.thumbs_rating == "down":
            score = 0.2

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

        sentiment_adj = {"positive": 0.1, "neutral": 0.0, "negative": -0.15}
        score += sentiment_adj.get(self.final_sentiment, 0)

        return round(max(0.0, min(1.0, score)), 2)
```

**תבנית סקר אחרי שיחה בעברית:**

```python
post_chat_survey = {
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

### שלב 7: בדיקות A/B לווריאציות תגובה בעברית

בדיקת ניסוחים שונים, רמות רשמיות, ואסטרטגיות מגדר:

```python
import hashlib
from collections import defaultdict

class HebrewABTestManager:
    """ניהול בדיקות A/B לתגובות צ'אטבוט בעברית."""

    def __init__(self):
        self.active_tests = {}
        self.results = defaultdict(lambda: {
            "impressions": 0, "completions": 0,
            "satisfaction_scores": [], "escalations": 0,
        })

    def create_test(self, test_id: str, variants: dict[str, str],
                    traffic_split: dict[str, float] | None = None):
        """יצירת בדיקת A/B חדשה.

        דוגמה:
            create_test("welcome_message", variants={
                "formal": "שלום וברוכים הבאים. כיצד נוכל לסייע לכם?",
                "casual": "היי! איך אפשר לעזור?",
                "gender_neutral": "שלום! ניתן לבחור מהאפשרויות הבאות:",
            })
        """
        if traffic_split is None:
            n = len(variants)
            traffic_split = {name: 1.0 / n for name in variants}
        self.active_tests[test_id] = {
            "variants": variants,
            "traffic_split": traffic_split,
        }

    def assign_variant(self, test_id: str, user_id: str) -> str:
        """שיוך דטרמיניסטי של משתמש לווריאנט. אותו משתמש תמיד רואה את אותו ווריאנט."""
        test = self.active_tests[test_id]
        hash_val = int(hashlib.md5(f"{user_id}:{test_id}".encode()).hexdigest(), 16)
        bucket = (hash_val % 1000) / 1000.0
        cumulative = 0.0
        for variant_name, split in test["traffic_split"].items():
            cumulative += split
            if bucket < cumulative:
                return variant_name
        return list(test["traffic_split"].keys())[-1]
```

**ממדים נפוצים לבדיקות A/B בעברית:**

| ממד | ווריאנט A | ווריאנט B | מה למדוד |
|------|-----------|-----------|----------|
| רשמיות | "כיצד נוכל לסייע?" | "איך אפשר לעזור?" | שיעור השלמה |
| מגדר | סימון לוכסן ("את/ה") | ניסוח ניטרלי ("ניתן ל...") | שביעות רצון |
| אורך | הסבר מפורט | תגובה קצרה ותכליתית | שיעור נטישה |
| שגיאות | "לא הצלחתי להבין" | "אפשר לנסח אחרת?" | שיעור ניסיון חוזר |

### שלב 8: דשבורדים ומדדי ביצוע

מדדים מרכזיים לדשבורד:

```python
from dataclasses import dataclass

@dataclass
class ChatbotDashboard:
    """מדדים מרכזיים לדשבורד ביצועי צ'אטבוט."""

    total_conversations: int = 0
    resolution_rate: float = 0.0        # אחוז שנפתר בלי הסלמה
    first_contact_resolution: float = 0.0  # אחוז שנפתר בסשן הראשון
    avg_handle_time_seconds: float = 0.0
    escalation_rate: float = 0.0
    abandonment_rate: float = 0.0

    avg_csat: float = 0.0               # סקאלה 1-5
    intent_accuracy: float = 0.0        # אחוז סיווג נכון
    fallback_rate: float = 0.0          # אחוז הודעות שהגיעו ל-fallback

    avg_response_time_ms: float = 0.0
    conversations_per_day: float = 0.0
    peak_hour: int = 0                  # 0-23
    busiest_day: str = ""

    def to_report_dict(self) -> dict:
        """עיצוב מדדים לדיווח."""
        return {
            "ליבה": {
                "סה\"כ שיחות": f"{self.total_conversations:,}",
                "שיעור פתרון": f"{self.resolution_rate:.1%}",
                "שיעור הסלמה": f"{self.escalation_rate:.1%}",
                "שיעור נטישה": f"{self.abandonment_rate:.1%}",
            },
            "שביעות רצון": {
                "CSAT ממוצע": f"{self.avg_csat:.1f}/5",
            },
            "דיוק": {
                "דיוק זיהוי כוונות": f"{self.intent_accuracy:.1%}",
                "שיעור fallback": f"{self.fallback_rate:.1%}",
            },
        }
```

**דפוסי תנועה ישראליים שכדאי לצפות:**
- שעות שיא: בדרך כלל 10:00-12:00 ו-19:00-22:00 (שעון ישראל)
- יום ראשון הוא היום העמוס ביותר (יום עבודה ראשון בשבוע הישראלי)
- שישי אחר הצהריים ושבת עם תנועה מינימלית
- תקופות חג (ראש השנה, פסח, סוכות) מראות דפוסים שונים

### שלב 9: אתגרים ייחודיים באנליטיקה בעברית

#### טקסט RTL בגרפים ויזואליזציות

כשמציגים דשבורדים אנליטיים עם טקסט בעברית, טפלו בנושאי RTL:

```python
# matplotlib לא תומך ב-RTL באופן מקורי
# עדיף להשתמש ב-Plotly שתומך בעברית טוב יותר:

import plotly.graph_objects as go

def create_hebrew_chart(data: dict[str, float], title: str) -> go.Figure:
    """יצירת גרף אינטראקטיבי עם תמיכה בעברית באמצעות Plotly."""
    fig = go.Figure(data=[
        go.Bar(
            y=list(data.keys()),
            x=list(data.values()),
            orientation="h",
            marker_color="#4F46E5",
            text=[f"{v:.1%}" for v in data.values()],
            textposition="outside",
        )
    ])
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(tickformat=".0%"),
        font=dict(family="Heebo, Arial, sans-serif"),
        height=400,
        margin=dict(l=150),  # מרווח שמאלי נוסף לתוויות בעברית
    )
    return fig
```

#### טוקניזציה של מילים בעברית לענני מילים

טוקניזציה רגילה לפי רווחים לא עובדת טוב בעברית בגלל תחיליות (ב, ה, ו, ל, מ, כ, ש):

```python
HEBREW_PREFIXES = ["ב", "ה", "ו", "ל", "מ", "כ", "ש", "וה", "של", "לה"]

def simple_hebrew_tokenize(text: str) -> list[str]:
    """טוקנייזר פשוט לעברית עם הסרת תחיליות.

    לסביבת ייצור, השתמשו ב-YAP (Yet Another Parser):
    https://github.com/OnlpLab/yap
    """
    import re
    tokens = re.findall(r'[\u0590-\u05FF]+', text)

    cleaned = []
    for token in tokens:
        stripped = token
        if len(token) > 3:
            for prefix in sorted(HEBREW_PREFIXES, key=len, reverse=True):
                if token.startswith(prefix) and len(token) - len(prefix) >= 2:
                    stripped = token[len(prefix):]
                    break
        cleaned.append(stripped)
    return cleaned
```

#### טיפול בשאילתות מעורבות עברית-אנגלית

משתמשים ישראליים מערבבים שפות לעתים קרובות. עקבו אחרי התפלגות השפות:

```python
import re

def detect_message_language(text: str) -> dict:
    """זיהוי הרכב שפתי של הודעה."""
    hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total = hebrew_chars + english_chars

    if total == 0:
        return {"primary_language": "unknown", "hebrew_ratio": 0, "english_ratio": 0}

    he_ratio = hebrew_chars / total
    return {
        "primary_language": "he" if he_ratio >= 0.5 else "en",
        "hebrew_ratio": round(he_ratio, 2),
        "english_ratio": round(1 - he_ratio, 2),
        "is_mixed": 0.2 < he_ratio < 0.8,
    }
```

### שלב 10: התראות וזיהוי חריגים

הגדירו התראות כדי לתפוס בעיות לפני שהן משפיעות על יותר מדי משתמשים:

```python
from dataclasses import dataclass

@dataclass
class AlertRule:
    """הגדרת כלל התראה למדדי צ'אטבוט."""
    name: str
    metric: str
    operator: str          # "gt" (גדול מ) או "lt" (קטן מ)
    threshold: float
    window_minutes: int    # חלון מתגלגל
    severity: str          # "critical", "warning", "info"
    description_he: str    # תיאור בעברית לצוות תפעול

# כללי התראה מומלצים לצ'אטבוטים בעברית
DEFAULT_ALERT_RULES = [
    AlertRule(
        name="high_escalation_rate",
        metric="escalation_rate",
        operator="gt", threshold=0.35, window_minutes=60,
        severity="warning",
        description_he="שיעור הסלמה גבוה מ-35% בשעה האחרונה",
    ),
    AlertRule(
        name="satisfaction_drop",
        metric="avg_csat",
        operator="lt", threshold=3.0, window_minutes=120,
        severity="critical",
        description_he="שביעות רצון ממוצעת ירדה מתחת ל-3.0 בשעתיים האחרונות",
    ),
    AlertRule(
        name="high_abandonment",
        metric="abandonment_rate",
        operator="gt", threshold=0.40, window_minutes=60,
        severity="critical",
        description_he="שיעור נטישה גבוה מ-40% בשעה האחרונה",
    ),
    AlertRule(
        name="high_fallback_rate",
        metric="fallback_rate",
        operator="gt", threshold=0.25, window_minutes=30,
        severity="warning",
        description_he="שיעור fallback גבוה מ-25% בחצי שעה האחרונה",
    ),
    AlertRule(
        name="slow_response",
        metric="p95_response_time_ms",
        operator="gt", threshold=3000, window_minutes=15,
        severity="warning",
        description_he="זמן תגובה P95 חורג מ-3 שניות ברבע השעה האחרון",
    ),
]
```

### שלב 11: תבניות דיווח

הפקת דוחות תקופתיים שמסכמים ביצועי צ'אטבוט:

```python
def generate_weekly_report(
    dashboard: ChatbotDashboard,
    previous_dashboard: ChatbotDashboard | None = None,
    period_start: str = "",
    period_end: str = "",
) -> str:
    """הפקת דוח שבועי בעברית."""

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

    prev = previous_dashboard
    lines = [
        f"# דוח ביצועי צ'אטבוט שבועי",
        f"## תקופה: {period_start} עד {period_end}",
        "",
        "## מדדים מרכזיים",
        "",
        f"| מדד | ערך | שינוי |",
        f"|------|------|--------|",
        f"| שיחות | {dashboard.total_conversations:,} | "
        f"{trend_arrow(dashboard.total_conversations, prev.total_conversations if prev else 0)} |",
        f"| שיעור פתרון | {dashboard.resolution_rate:.1%} | "
        f"{trend_arrow(dashboard.resolution_rate, prev.resolution_rate if prev else 0)} |",
        f"| שביעות רצון | {dashboard.avg_csat:.1f}/5 | "
        f"{trend_arrow(dashboard.avg_csat, prev.avg_csat if prev else 0)} |",
        f"| שיעור הסלמה | {dashboard.escalation_rate:.1%} | "
        f"{trend_arrow(dashboard.escalation_rate, prev.escalation_rate if prev else 0, False)} |",
        f"| שיעור נטישה | {dashboard.abandonment_rate:.1%} | "
        f"{trend_arrow(dashboard.abandonment_rate, prev.abandonment_rate if prev else 0, False)} |",
        f"| דיוק זיהוי כוונות | {dashboard.intent_accuracy:.1%} | "
        f"{trend_arrow(dashboard.intent_accuracy, prev.intent_accuracy if prev else 0)} |",
        "",
        "## תנועה",
        f"- ממוצע שיחות ביום: {dashboard.conversations_per_day:.0f}",
        f"- שעת שיא: {dashboard.peak_hour}:00",
        f"- יום עמוס ביותר: {dashboard.busiest_day}",
    ]

    return "\n".join(lines)
```

### שלב 12: אינטגרציה עם פלטפורמות צ'אטבוט

#### Dialogflow CX

```python
from collections import defaultdict

def parse_dialogflow_cx_logs(bigquery_rows: list[dict]) -> list[dict]:
    """המרת ייצוא BigQuery של Dialogflow CX לפורמט שיחות סטנדרטי."""
    sessions = defaultdict(lambda: {"messages": [], "started_at": None, "ended_at": None})

    for row in bigquery_rows:
        session_id = row["session_id"]
        timestamp = row["request_time"]
        session = sessions[session_id]

        if session["started_at"] is None or timestamp < session["started_at"]:
            session["started_at"] = timestamp
        if session["ended_at"] is None or timestamp > session["ended_at"]:
            session["ended_at"] = timestamp

        if row.get("query_text"):
            session["messages"].append({
                "timestamp": timestamp, "sender": "user",
                "text": row["query_text"],
                "intent": row.get("matched_intent", ""),
                "intent_confidence": row.get("intent_confidence", 0),
            })
        if row.get("response_text"):
            session["messages"].append({
                "timestamp": timestamp, "sender": "bot",
                "text": row["response_text"],
            })

    return [
        {"session_id": sid, **s, "outcome": "unknown", "language": "he"}
        for sid, s in sessions.items()
    ]
```

#### Rasa Tracker Store

```python
def parse_rasa_tracker_events(tracker_events: list[dict]) -> list[dict]:
    """המרת אירועי Tracker Store של Rasa לפורמט שיחות סטנדרטי."""
    conversations = []
    current = {"messages": [], "started_at": None, "ended_at": None}

    for event in tracker_events:
        event_type = event.get("event")
        timestamp = event.get("timestamp", "")

        if event_type == "session_started":
            if current["messages"]:
                conversations.append(current)
            current = {"session_id": "", "messages": [], "started_at": timestamp,
                       "ended_at": None, "outcome": "unknown", "language": "he"}

        elif event_type == "user":
            current["ended_at"] = timestamp
            intent_data = event.get("parse_data", {}).get("intent", {})
            current["messages"].append({
                "timestamp": timestamp, "sender": "user",
                "text": event.get("text", ""),
                "intent": intent_data.get("name", ""),
                "intent_confidence": intent_data.get("confidence", 0),
            })

        elif event_type == "bot":
            current["ended_at"] = timestamp
            current["messages"].append({
                "timestamp": timestamp, "sender": "bot",
                "text": event.get("text", ""),
            })

        elif event_type == "action" and event.get("name") == "action_human_handoff":
            current["outcome"] = "escalated"

    if current["messages"]:
        conversations.append(current)
    return conversations
```

## דוגמאות

### דוגמה 1: ניתוח ביצועי צ'אטבוט לשבוע האחרון

המשתמש אומר: "תנתח את הלוגים של הצ'אטבוט בעברית שלי מהשבוע האחרון ותראה לי איפה משתמשים נוטשים."

פעולות:
1. טעינת לוגי שיחות מהתקופה המבוקשת.
2. הרצת `compute_flow_metrics()` לסטטיסטיקות ברמת סשן.
3. הרצת `detect_drop_off_points()` לזיהוי דפוסי נטישה.
4. הרצת `detect_conversation_loops()` לזיהוי משתמשים תקועים.
5. הפקת סיכום עם המלצות פרקטיות.

תוצאה: דוח שמציג שיעור השלמה, 5 נקודות הנטישה המובילות לפי כוונה, שיחות בלולאה, והודעות בוט ספציפיות שמקדימות נטישה.

### דוגמה 2: הקמת בדיקות A/B להודעות פתיחה

המשתמש אומר: "אני רוצה לבדוק אם ברכה רשמית או לא רשמית עובדת יותר טוב בעברית."

פעולות:
1. יצירת בדיקת A/B עם `HebrewABTestManager.create_test()`.
2. הגדרת ווריאנטים: רשמי ("כיצד נוכל לסייע לכם היום?") מול לא רשמי ("היי! מה אפשר לעשות בשבילך?").
3. הגדרת חלוקת תנועה (50/50).
4. אינטגרציה עם handler הפתיחה של הבוט.
5. הגדרת מעקב תוצאות (שיעור השלמה, CSAT, הסלמה).

תוצאה: בדיקת A/B רצה עם שיוך דטרמיניסטי למשתמשים ומעקב תוצאות.

### דוגמה 3: הקמת התראות חריגים

המשתמש אומר: "תתריע לי אם שביעות הרצון מהצ'אטבוט יורדת פתאום."

פעולות:
1. הגדרת `AlertManager` עם כללי שביעות רצון והסלמה.
2. הגדרת חישובי חלון מתגלגל למדדים עדכניים.
3. חיבור התראות לערוצי התראה (Slack, אימייל, PagerDuty).
4. הוספת תיאורים בעברית להתראות לצוות התפעול.

תוצאה: מוניטורינג בזמן אמת שמפעיל התראות כש-CSAT יורד מתחת ל-3.0, שיעור הסלמה עולה מעל 35%, או נטישה קופצת מעל 40%.

### דוגמה 4: הפקת דוח שבועי

המשתמש אומר: "תייצר לי דוח שבועי בעברית לצוות הצ'אטבוט."

פעולות:
1. הרצת `build_dashboard()` לשבוע הנוכחי והקודם.
2. קריאה ל-`generate_weekly_report()` עם שני הדשבורדים לחיצי מגמה.
3. הוספת ניתוח נטישה ופירוט דיוק כוונות.
4. עיצוב הפלט בעברית עם טבלאות תואמות RTL.

תוצאה: דוח מעוצב בעברית עם השוואות שבוע-על-שבוע, אינדיקטורי מגמה, ומדדים מרכזיים מוכנים לשיתוף עם הצוות.

## משאבים מצורפים

### סקריפטים
- `scripts/conversation-analyzer.py` -- ניתוח לוגי שיחות צ'אטבוט למדדים מרכזיים (נטישה, רגשות, פתרון). הרצה: `python scripts/conversation-analyzer.py --help`

### מסמכי עזר
- `references/chatbot-metrics-glossary.md` -- מילון מונחי אנליטיקת צ'אטבוט עם תרגומים לעברית ובנצ'מרקים ענפיים. לשימוש בהגדרת KPIs או הסבר מדדים לבעלי עניין דוברי עברית.
- `references/hebrew-sentiment-guide.md` -- מדריך לאתגרי ניתוח רגשות בעברית כולל שלילה, סרקזם, סלנג, וטיפול בשפה מעורבת. לשימוש בבנייה או כוונון של מודלי סנטימנט בעברית.

## מלכודות נפוצות

- ניתוח סנטימנט בעברית דורש נתוני אימון ישראליים ספציפיים. מודלים סטנדרטיים באנגלית מסווגים בטעות אירוניה ישראלית (נפוצה מאוד בתקשורת ישראלית) כניטרלית או חיובית.
- שימוש בצ'אטבוטים ישראליים מגיע לשיא בבקרי יום ראשון (תחילת שבוע העבודה), לא בשני. דוחות אנליטיקה שבועיים צריכים להתבסס על ראשון עד חמישי.
- אנליטיקת טקסט בעברית חייבת להתמודד עם אותיות שימוש (ב-, ל-, כ-, מ-) שמשנות גבולות מילים. טוקנייזרים שאומנו על אנגלית מפצלים מילים בעברית בצורה שגויה.
- משתמשים ישראליים עוברים תדיר בין עברית לאנגלית בתוך שיחת צ'אטבוט אחת. כלי אנליטיקה חייבים לטפל בסשנים דו-לשוניים ולא להתייחס אליהם כשתי שפות נפרדות.

## פתרון בעיות

### שגיאה: "מודל DictaBERT לא נטען"
סיבה: המודל `dicta-il/dictabert-sentiment` דורש PyTorch ואת ספריית `transformers`. הוא שוקל כ-500MB.
פתרון: התקינו תלויות עם `pip install torch transformers` וודאו שיש מספיק מקום בדיסק. לסביבות ללא GPU, התקינו `torch` עם `pip install torch --index-url https://download.pytorch.org/whl/cpu`.

### שגיאה: "טקסט בעברית מופיע הפוך בגרפים"
סיבה: matplotlib לא תומך ב-RTL באופן מקורי. מחרוזות עבריות מצוירות משמאל לימין כברירת מחדל.
פתרון: השתמשו בספריית `python-bidi` (`pip install python-bidi`) כדי להפעיל את אלגוריתם ה-BiDi לפני הרנדור, או עברו ל-Plotly שתומך ב-RTL טוב יותר.

### שגיאה: "טוקניזציה מייצרת תדירויות מילים שגויות"
סיבה: חלוקה לפי רווחים לא מתחשבת בתחיליות עבריות (ב, ה, ו, ל, מ, כ, ש) שמתחברות למילים.
פתרון: השתמשו בטוקנייזר עם הסרת תחיליות משלב 9, או לדיוק בסביבת ייצור, השתמשו במנתח המורפולוגי YAP (https://github.com/OnlpLab/yap).

### שגיאה: "ציוני סנטימנט לא אמינים להודעות קצרות"
סיבה: הודעות קצרות מאוד בעברית (1-3 מילים) חסרות הקשר לניתוח רגשות מדויק. תגובות מדוברות כמו "סבבה" יכולות להיות חיוביות או ניטרליות לפי ההקשר.
פתרון: עבור הודעות מתחת ל-4 מילים, הסתמכו על סיגנלים התנהגותיים (האם המשתמש המשיך, הסלים, או נטש?) במקום סנטימנט מבוסס טקסט. שלבו סנטימנט עם סיגנלי שביעות רצון כמו בשלב 6.
