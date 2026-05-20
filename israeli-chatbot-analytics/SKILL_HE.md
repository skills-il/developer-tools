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

אם הפלטפורמה שלכם לא מייצאת בפורמט הזה, כתוב transformer שינרמל את הלוגים. פלטפורמות נפוצות:

| פלטפורמה | שיטת ייצוא | פורמט |
|-----------|------------|-------|
| Dialogflow CX | ייצוא BigQuery | שורות JSON עם הקשר סשן. השתמשו בקוד שפה `he-il` בסוכנים חדשים, `iw` הוצא משימוש (ראו https://docs.cloud.google.com/dialogflow/cx/docs/reference/language). |
| Rasa Pro / CALM | דשבורד אנליטיקה + אירועי tracker | אירועי שלב-בזרימה (Rasa Pro 3.x עם CALM מבוסס-דיאלוג ולא מבוסס-כוונות, ולכן מדדי דיוק כוונות ממופים שם אחרת). |
| Rasa Open Source (ישן) | Tracker Store (SQL/Mongo) | רשימת אירועים לכל שיחה. נכנס למצב תחזוקה ב-2025, ראו https://legacy-docs-oss.rasa.com/docs/rasa/. |
| Botpress | ייצוא שיחות / DB | JSON. עברית מופיעה כשפה נתמכת אבל יישור RTL בווידג'ט ברירת המחדל עדיין לא שלם נכון ל-2026, בדקו את היישור של בועות ההודעות לפני שאתם מדווחים על התפלגות שפה. |
| בוטים מותאמים | לוגי אפליקציה | משתנה (לנרמל לסכמה למעלה) |
| WhatsApp Cloud API | לוגי Webhook | אובייקטי הודעות עם metadata. ראו את הסעיף על תמחור WhatsApp למטה. |
| ManyChat | ייצוא קהל + flow | CSV/JSON. עלויות שליחה ב-WhatsApp עוברות דרך התעריף לפי הודעה של Meta. |

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

ניתוח רגשות בעברית דורש טיפול מיוחד בגלל המורפולוגיה המורכבת, דפוסי שלילה, וסלנג. משתמשים ב-DictaBERT (אנקודר לסיווג), DictaLM 2.0-Instruct (גנרטיבי, 7B פרמטרים, מבוסס Mistral) לדיוק בסביבת ייצור, AlephBERT (`onlplab/alephbert-base` מ-OnlpLab של אוניברסיטת בר-אילן) כאלטרנטיבת אנקודר, או בגישה מבוססת מילון לניתוח קל. DictaLM 2.0 (שוחרר ביולי 2024) הוא ה-LLM הישראלי המוביל היום מ-Dicta, עם וריאנט instruct שאומן על כ-200 מיליארד טוקנים בעברית ואנגלית ויחס דחיסה של 2.76 טוקנים למילה. שימושי כשרוצים מודל אחד שמסווג סנטימנט וגם מסכם את השיחה בפרוזה עברית לצוות התפעול.

**שימוש ב-DictaBERT (כדאי לייצור):**

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

- א. **שלילה עם תחיליות**: בעברית השלילה מגיעה כמילה נפרדת ("לא") לפני שמות תואר, ויכולה להפוך את המשמעות. "לא רע" בשימוש ישראלי הוא חיובי קלות.

- ב. **סרקזם ואירוניה**: תקשורת ישראלית מלאה בסרקזם. "יופי, בדיוק מה שחיכיתי לו" יכול להיות שלילי מאוד. DictaBERT מתמודד עם חלק מהסרקזם; לכיסוי טוב יותר, עשו fine-tune על הנתונים שלכם.

- ג. **סלנג וקיצורים**: הסלנג הישראלי משתנה מהר. דפוסים נפוצים:
   - "אחלה" (מערבית) = מעולה/חיובי
   - "סבבה" = בסדר/מגניב
   - "בומבה" = מדהים
   - "חרא" = נורא
   - "פאדיחה" (מערבית) = מביך/גרוע
   - "וואלה" = באמת?/וואו (תלוי הקשר)

- ד. **עירוב עברית-אנגלית**: משתמשים ישראליים מערבבים מילים באנגלית לתוך משפטים בעברית. ודאו שהמודל מתמודד עם "ה-support שלכם גרוע".

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
| מגדר | סימון לוכסן ("את/ה") | ניסוח ניטרלי ("אפשר ל...") | שביעות רצון |
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

#### מדדי שימור ומשתמשים חוזרים

מדדים ברמת הסשן מספרים לכם איך עברה שיחה בודדת, אבל לא אם הבוט מזכה בשימוש חוזר. עקבו אחרי ממדי השימור האלה לצד הדשבורד למעלה:

```python
from datetime import datetime, timedelta

def compute_retention_metrics(conversations: list[dict]) -> dict:
    """חישוב מדדי שיעור חזרה מלוגי שיחות.

    דורש user_id יציב בין סשנים (ראו את סעיף פרטיות והסכמה
    לפני שמתמידים מזהים).
    """
    # מיפוי כל משתמש לקבוצת התאריכים שבהם ניהל שיחה.
    user_days: dict[str, set] = {}
    for convo in conversations:
        uid = convo.get("user_id")
        if not uid or not convo.get("started_at"):
            continue
        day = datetime.fromisoformat(convo["started_at"]).date()
        user_days.setdefault(uid, set()).add(day)

    d1_eligible = d1_returned = 0
    d7_eligible = d7_returned = 0
    repeat_contact_users = 0

    for uid, days in user_days.items():
        sorted_days = sorted(days)
        first = sorted_days[0]
        if len(days) > 1:
            repeat_contact_users += 1
        # D1: האם המשתמש חזר ביום שאחרי המגע הראשון?
        d1_eligible += 1
        if (first + timedelta(days=1)) in days:
            d1_returned += 1
        # D7: האם המשתמש חזר תוך 2-7 ימים מהמגע הראשון?
        d7_eligible += 1
        if any(first + timedelta(days=n) in days for n in range(2, 8)):
            d7_returned += 1

    total_users = len(user_days) or 1
    return {
        "d1_return_rate": round(d1_returned / d1_eligible, 4) if d1_eligible else 0.0,
        "d7_return_rate": round(d7_returned / d7_eligible, 4) if d7_eligible else 0.0,
        "repeat_contact_rate": round(repeat_contact_users / total_users, 4),
        "unique_users": len(user_days),
    }
```

- שיעור חזרה D1: אחוז המשתמשים שמתחילים שיחה חדשה ביום שאחרי המגע הראשון. סיגנל שימושי לבוטי שירות שמטרתם ליצור הרגל.
- שיעור חזרה D7: אחוז המשתמשים שחוזרים תוך שבוע. יציב יותר מ-D1 לבוטים ישראליים בנפח נמוך.
- שיעור מגע חוזר: אחוז המשתמשים עם יותר משיחה אחת בסך הכל. שיעור מגע חוזר גבוה בבוט שירות יכול להיות טוב (אמון) או רע (בעיות לא נפתרות), אז קראו אותו יחד עם פתרון במגע ראשון.

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

הערה: Rasa Open Source נמצאת במצב תחזוקה. אנליטיקת ה-tracker-store מבוססת-הכוונות שלמטה רלוונטית לפריסות Rasa OSS קיימות; בנייה חדשה ב-Rasa משתמשת ב-CALM (Conversational AI with Language Models) שהיא מבוססת-דיאלוג ולא מבוססת-כוונות, ולכן מדדי דיוק כוונות ממופים שם אחרת. ראו את תיעוד ה-OSS הישן ב-https://legacy-docs-oss.rasa.com/docs/rasa/ לפרטי tracker-store.

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

## תמחור WhatsApp Business Platform

הרבה צ'אטבוטים ישראליים רצים על WhatsApp Cloud API, ועלות שליחה היא ממד אנליטיקה מרכזי. התמחור השתנה ב-1 ביולי 2025 ממודל לפי שיחה ל**חיוב לפי הודעה ב-4 קטגוריות**:

| קטגוריה | עמדת תמחור | מתי להשתמש |
|----------|------------|--------------|
| שיווק (marketing) | תעריף הגבוה ביותר להודעה, ללא הנחת נפח | מבצעים, broadcast, החזרת לקוחות |
| תועלת (utility) | נמוך משיווק (בדרך כלל פחות מ-$0.03 להודעה), זכאי להנחת נפח | עדכוני הזמנה, תזכורות לתורים, הודעות חשבון שנשלחות בעקבות פעולת משתמש |
| אימות (authentication) | התעריף הזול ביותר מבין המחויבים, זכאי להנחת נפח | קוד חד-פעמי לכניסה / תשלום / 2FA |
| שירות (service) | **חינם** | כל תגובה של העסק בתוך חלון השירות של 24 שעות (סשן ביוזמת המשתמש) |

שני חלונות חינם שכדאי לעקוב אחריהם באנליטיקה במפורש:

- א. **חלון שירות של 24 שעות.** כשמשתמש שולח הודעה נכנסת, אפשר להגיב בטקסט חופשי (בלי תבנית, בלי חיוב) במשך 24 השעות הבאות. אופטימיזציה של אנליטיקה ל"האם פתרנו בתוך חלון השירות?" יכולה להוריד שורה שלמה של עלות תבניות בזרימות תמיכה תגובתיות. ראו https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.
- ב. **חלון 72 שעות מלחיצה על מודעת click-to-WhatsApp או CTA של פייסבוק.** כשמשתמש מגיע מקליק על מודעת click-to-WhatsApp או על כפתור CTA בעמוד פייסבוק, כל ההודעות (כולל תבניות) חינם ב-72 השעות הבאות.

הוסיפו `template_category` (marketing/utility/authentication/service) ו-`arrived_via_ctw_ad` בוליאני לסכמת ה-conversation log שלכם, כדי שכספים ומוצר יוכלו לפצל CSAT והשלמה לפי אינטראקציה בתשלום מול חינמית. תעריפים ספציפיים לישראל לא מתפרסמים במסמכי הציבור, הוציאו את התעריף שלכם מ-Meta Business Manager או מה-BSP (Twilio / 360dialog / Vonage) לפני שמודדים קמפיין.

## תאימות אנטי-ספאם (חוק התקשורת, סעיף 30א)

אם הצ'אטבוט שלכם שולח הודעות שיווקיות (broadcast, תבניות פרסום ב-WhatsApp, קמפיינים בטלגרם, ריטרגטינג ב-SMS), סעיף 30א לחוק התקשורת (בזק ושידורים), התשמ"ב-1982 חל עליכם. החוק דורש **הסכמה מפורשת מראש בכתב** לפני שליחת דברי פרסומת ב-SMS, אימייל, פקס, חיוג רובוטי, וגם, לפי לשון התיקון מ-2008 כפי שפורשה על ידי בתי המשפט בישראל, תקשורת אלקטרונית שכוללת WhatsApp, טלגרם ואפליקציות הודעות דומות. המונח "דבר פרסומת" מפורש בהרחבה, וכל הודעה שאינה תפעולית טהורה עלולה להיחשב לפרסומת.

מעקב אנליטיקה מעשי:

- **תייגו כל שליחה ב-`opt_in_basis`**: "explicit_form" / "ctw_ad_click" / "service_reply" / "transactional". זה ה-audit trail שלכם אם תלונה מגיעה למשרד התקשורת.
- **עקבו אחרי שיעור הצלחה של נתיב ההסרה.** הודעות פרסומת חייבות לכלול את המילה "פרסומת", את שם השולח וכתובתו, ונתיב הסרה פעיל. מדדו את הזמן עד הסרה ואת שיעור ההצלחה של זרימת ההסרה כ-KPI תאימות.
- **פיצול שירות מול שיווק.** הריצו שיעור השלמה ו-CSAT בנפרד לזרימות שיווק עם opt-in מול זרימות שירות ביוזמת משתמש, הן מתנהגות שונה לחלוטין ושילוב שלהן מסתיר את שתיהן.
- הצלבה: `gws-hebrew-email-automation` ו-`israeli-telegram-business-bot` מכסים את אותו משטר opt-in לאימייל וטלגרם. השתמשו בהם אם אתם מפעילים גם את הערוצים האלה.

זו הנחיה הנדסית, לא ייעוץ משפטי. הפיצוי הסטטוטורי המקסימלי להודעת פרסומת לא רצויה הוא 1,000 ש"ח בלי הוכחת נזק, אז broadcast שגוי אפילו לכמה מאות נמענים שלא הסכימו יכול להפוך לאירוע כספי משמעותי. אמתו עם עו"ד פרטיות.

## פלטפורמות ניסוי לצ'אטבוטים בעברית

כשגולשים מעבר ל-`HebrewABTestManager` (bucketing בתהליך, תוצאות בזיכרון) וצריך ניתוח סטטיסטי אמיתי עם sequential testing והפחתת שונות CUPED, פלטפורמות ה-feature-flag והניסויים המרכזיות עובדות מצוין עם צ'אטבוטים בעברית, אף אחת מהן לא מתעניינת באיזו שפה ה-`variant_text` שלכם. בחרו לפי התאמת צוות ותשתית:

| פלטפורמה | התאמה | הערות לצוותי צ'אטבוט בעברית |
|----------|--------|---------------------------------|
| Statsig | צוותים שרוצים flags + ניסויים + אנליטיקת מוצר במחסנית אחת | OpenAI רכשה את Statsig ב-2025 ב-1.1 מיליארד דולר; ה-free tier עדיין נדיב לבוטים ישראליים קטנים. |
| LaunchDarkly | צוותי אנטרפרייז בוגרים שצריכים אישורים, audit logs, RBAC | הבחירה ה"בטוחה" לאנטרפרייז; שלבו עם האנליטיקה הקיימת לחישובים. |
| GrowthBook | צוותים עם data warehouse (BigQuery, Snowflake, Postgres) שרוצים להריץ סטטיסטיקה על הנתונים שלהם | open source; לא אוסף נתוני אירועים, אז תמלילים בעברית אף פעם לא יוצאים מה-warehouse שלכם, שימושי לעמדה של תיקון 13 לגבי data residency. |

לגבי gotchas ספציפיים לעברית, צפו למשך בדיקה ארוך יותר (שבועיים+, 200+ חשיפות לווריאנט), בסיסי משתמשים ישראליים קטנים יותר וסזונליות שבועית (א'-ה' שבוע עבודה) הופכת בדיקות של שבוע אחד לא אמינות.

## הערות על מחסנית אנליטיקה מודרנית (GA4 + Mixpanel, 2026)

- **ערוץ "AI Assistant" ב-GA4.** GA4 מספק היום `Channel Group: AI Assistant` מובנה (Medium `ai-assistant`) שמסווג אוטומטית תנועה מ-ChatGPT, Gemini, Claude ו-Perplexity. אם משבצים את הבוט באתר שיווקי, זו הדרך הקלה ביותר לייחס תנועה נכנסת שהופנתה מ-LLM לפאנל הבוט, בלי regex מותאם (https://martech.org/ga4-now-tracks-ai-chatbot-traffic-automatically/).
- **Mixpanel Spark + MCP Server.** Mixpanel שחררה את Spark (בונה שאילתות AI) ו-MCP server ב-2025-2026 שמאפשרים ל-Claude / ChatGPT / Cursor לתשאל את Mixpanel בשיחה. לדשבורדים בעברית זה רלוונטי כי אפשר לשאול שאלות המשך בעברית ו-Spark מנתב אותן לאירוע/תכונה הנכונים, שימושי כשצוות התפעול לא שולט בממשק שאילתת המשפך.

## דוגמאות

### דוגמה 1: ניתוח ביצועי צ'אטבוט לשבוע האחרון

המשתמש אומר: "תנתח את הלוגים של הצ'אטבוט בעברית שלי מהשבוע האחרון ותראה לי איפה משתמשים נוטשים."

פעולות:
- א. טעינת לוגי שיחות מהתקופה המבוקשת.
- ב. הרצת `compute_flow_metrics()` לסטטיסטיקות ברמת סשן.
- ג. הרצת `detect_drop_off_points()` לזיהוי דפוסי נטישה.
- ד. הרצת `detect_conversation_loops()` לזיהוי משתמשים תקועים.
- ה. הפקת סיכום עם המלצות פרקטיות.

תוצאה: דוח שמציג שיעור השלמה, 5 נקודות הנטישה המובילות לפי כוונה, שיחות בלולאה, והודעות בוט ספציפיות שמקדימות נטישה.

### דוגמה 2: הקמת בדיקות A/B להודעות פתיחה

המשתמש אומר: "אני רוצה לבדוק אם ברכה רשמית או לא רשמית עובדת יותר טוב בעברית."

פעולות:
- א. יצירת בדיקת A/B עם `HebrewABTestManager.create_test()`.
- ב. הגדרת ווריאנטים: רשמי ("כיצד נוכל לסייע לכם היום?") מול לא רשמי ("היי! מה אפשר לעשות בשבילך?").
- ג. הגדרת חלוקת תנועה (50/50).
- ד. אינטגרציה עם handler הפתיחה של הבוט.
- ה. הגדרת מעקב תוצאות (שיעור השלמה, CSAT, הסלמה).

תוצאה: בדיקת A/B רצה עם שיוך דטרמיניסטי למשתמשים ומעקב תוצאות.

### דוגמה 3: הקמת התראות חריגים

המשתמש אומר: "תתריע לי אם שביעות הרצון מהצ'אטבוט יורדת פתאום."

פעולות:
- א. הגדרת `AlertManager` עם כללי שביעות רצון והסלמה.
- ב. הגדרת חישובי חלון מתגלגל למדדים עדכניים.
- ג. חיבור התראות לערוצי התראה (Slack, אימייל, PagerDuty).
- ד. הוספת תיאורים בעברית להתראות לצוות התפעול.

תוצאה: מוניטורינג בזמן אמת שמפעיל התראות כש-CSAT יורד מתחת ל-3.0, שיעור הסלמה עולה מעל 35%, או נטישה קופצת מעל 40%.

### דוגמה 4: הפקת דוח שבועי

המשתמש אומר: "תייצר לי דוח שבועי בעברית לצוות הצ'אטבוט."

פעולות:
- א. הרצת `build_dashboard()` לשבוע הנוכחי והקודם.
- ב. קריאה ל-`generate_weekly_report()` עם שני הדשבורדים לחיצי מגמה.
- ג. הוספת ניתוח נטישה ופירוט דיוק כוונות.
- ד. עיצוב הפלט בעברית עם טבלאות תואמות RTL.

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

## פרטיות והסכמה

הסקיל הזה קולט תמלילי שיחות מלאים וערכי `user_id`, ומריץ ניתוח רגשות על הודעות משתמשים. טקסט שיחה הוא מידע אישי ולעתים קרובות מכיל תוכן רגיש (בריאות, כספים, תלונות). טפלו בו תחת חוק הגנת הפרטיות הישראלי, כולל תיקון 13 (נכנס לתוקף באוגוסט 2025), שהחמיר את חובות ההסכמה, היידוע, האחריותיות וצמצום המידע.

כללים מעשיים:

- הסכמה ויידוע: קבלו הסכמה לאחסון ולניתוח של תוכן השיחה, וציינו בהצהרת הפרטיות שלכם ששיחות נשמרות ומנותחות לצורכי איכות. ניתוח רגשות על הודעות משתמשים הוא מטרת עיבוד שצריך לחשוף.
- פסבדונימיזציה של `user_id`: אל תנתחו מספרי טלפון, אימיילים או תעודות זהות גולמיים כמזהה. גבבו או טוקנו את ה-`user_id` לפני שהוא מגיע לצינור האנליטיקה, ושמרו את טבלת המיפוי בנפרד ובגישה מבוקרת. שימור ושיוך לבדיקות A/B עדיין עובדים על מזהה פסבדונימי יציב.
- צמצום והסתרה: הסירו או מסכו ישויות שאתם לא צריכים לאנליטיקה (מספרי זהות, שמות מלאים, מספרי כרטיס) לפני אחסון תמלילים. נדיר שצריך את ה-PII הגולמי כדי למדוד נטישה או סנטימנט.
- הגבלות שימור: הגדירו חלון שימור מפורש לתמלילים גולמיים (למשל 90 יום) ושמרו לטווח ארוך רק מדדים מצרפיים. תעדו את החלון ומחקו לפי לוח זמנים.
- בקרת גישה ומיקום: הגבילו מי יכול לקרוא שיחות גולמיות, תעדו גישה, וודאו היכן המידע מאוחסן ומעובד.
- זו הנחיה הנדסית, לא ייעוץ משפטי. אמתו את החובות הספציפיות שלכם מול איש מקצוע בתחום הפרטיות.

## שרתי MCP מומלצים

אין צורך בשרת MCP לסקיל הזה. הוא עובד כולו על לוגי שיחות מיוצאים (ייצוא BigQuery, dumps של Rasa tracker-store, קבצי לוג של האפליקציה) שאתם טוענים מהדיסק ומנתחים מקומית עם סקריפט הפייתון המצורף. אין API חי לעטוף, ולכן אין צורך באינטגרציית MCP.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| Dialogflow CX language reference | https://docs.cloud.google.com/dialogflow/cx/docs/reference/language | קוד שפה לעברית `he-il` (`iw` הוצא משימוש לסוכנים חדשים) |
| Dialogflow CX analytics | https://cloud.google.com/dialogflow/cx/docs/concept/analytics | אנליטיקת שיחות מובנית, מדדי כוונה |
| Rasa CALM docs | https://rasa.com/docs/learn/concepts/calm/ | זרימות מבוססות-דיאלוג ל-Rasa Pro 3.x, מחליף עיצוב מבוסס-כוונות לבנייה חדשה |
| תיעוד Rasa OSS (ישן) | https://legacy-docs-oss.rasa.com/docs/rasa/ | מעקב אירועים, tracker stores, אינטגרציות אנליטיקה מותאמות (מצב תחזוקה) |
| תמחור WhatsApp Business Platform | https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing | תעריפים לפי הודעה לפי מדינה + קטגוריה (שיווק/תועלת/אימות/שירות), חוקי חלון 24 שעות חינם |
| DictaBERT (חבילת BERT לעברית) | https://huggingface.co/dicta-il/dictabert | BERT מאומן מראש בעברית לסיווג fine-tune |
| DictaBERT sentiment | https://huggingface.co/dicta-il/dictabert-sentiment | מסווג סנטימנט בעברית מן המוכן (3 סיווגים) |
| DictaLM 2.0 Instruct | https://huggingface.co/dicta-il/dictalm2.0-instruct | LLM גנרטיבי בעברית (7B, מבוסס Mistral) לסיכומים + סיווג בקריאה אחת |
| AlephBERT | https://huggingface.co/onlplab/alephbert-base | BERT עברי חלופי מ-OnlpLab של בר-אילן |
| מודלים בעברית ב-HuggingFace | https://huggingface.co/models?language=he | סקירת קטלוג המודלים המלא בעברית |
| Mixpanel help | https://mixpanel.com/help | ניתוח משפך, שימור קבוצות לזרימות צ'אט |
| Matomo analytics | https://matomo.org/docs/ | מעקב אירועים עצמי, ידידותי לפרטיות |
| תיקון 13 לחוק הגנת הפרטיות (IAPP) | https://iapp.org/news/a/israel-marks-a-new-era-in-privacy-law-amendment-13-ushers-in-sweeping-reform | בתוקף 14 באוגוסט 2025: הסכמה, יידוע, הגבלות שימור, מנגנוני מחיקה |
| מדריך לסעיף 30א (DLA Piper) | https://www.dlapiperdataprotection.com/index.html?t=electronic-marketing&c=IL | משטר opt-in לשיווק ב-SMS / אימייל / אפליקציות הודעות בישראל |

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
