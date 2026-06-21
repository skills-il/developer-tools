---
name: hebrew-chatbot-builder
description: >-
  Build conversational AI chatbots with native Hebrew support, including
  WhatsApp Business API integration, Telegram bot scaffolding, web chat
  widgets, Hebrew NLP patterns, and RTL chat UI components. Prevents common
  Hebrew chatbot mistakes like broken RTL alignment, incorrect gender
  inflections, and poor tokenization of prefixed prepositions that break
  intent detection. Use when user asks to "build a Hebrew chatbot",
  "integrate WhatsApp bot in Hebrew", "binui bot b'ivrit", or design
  conversation flows for Hebrew speakers. Covers intent detection for
  Hebrew morphology, entity extraction for Israeli data (NIS amounts,
  phone numbers, dates), and gender-aware responses. Do NOT use for
  non-Hebrew chatbots or general NLP pipelines without a Hebrew component.
license: MIT
---

# בונה צ'אטבוט בעברית

מדריך מקיף לבניית צ'אטבוטים מבוססי AI עם תמיכה מלאה בעברית. הסקיל הזה מכסה אינטגרציות עם פלטפורמות (וואטסאפ, טלגרם, אתרים), דפוסי שפה עבריים, רכיבי ממשק RTL, ועיצוב זרימות שיחה למשתמשים דוברי עברית.

## הוראות

עקבו אחר התהליך הזה כשבונים צ'אטבוט בעברית:

1. **זיהוי הפלטפורמה והערוץ.** ודאו אם הבוט רץ על WhatsApp Business API, טלגרם, ווידג'ט צ'אט מוטמע באתר, או כמה מהם יחד. לכל אחד יש scaffold ומודל הודעות שונה.
2. **קביעת רגיסטר רשמי או לא רשמי.** שאלו את המשתמש אם הקהל מצפה לעברית לא רשמית ("דוגרי", מומלץ לרוב הבוטים לצרכנים) או לעברית רשמית (ממשלה, בנקאות, משפטי). ההחלטה הזו מעצבת כל מחרוזת תגובה.
3. **בירור אסטרטגיית הטיפול במגדר.** בחרו בין לשאול את המשתמש על מגדרו בתחילת השיחה ולזכור, ניסוח ניטרלי מבחינת מגדר לאורך כל השיחה, או סימון לוכסן ("את/ה"). ראו את הסעיף תגובות מודעות מגדר.
4. **בניית scaffold דרך הסקריפט המצורף הרלוונטי.** השתמשו ב-`scripts/whatsapp-webhook-handler.py` לוואטסאפ או ב-`scripts/telegram-bot-scaffold.py` לטלגרם כנקודת התחלה, ואז התאימו את תבניות התגובה בעברית ואת זרימות השיחה.
5. **חיבור חילוץ ישויות.** הוסיפו את `extract_israeli_entities()` (או מקבילה) כדי שהבוט יזהה מספרי טלפון ישראליים, סכומים בשקלים, תאריכים ותעודת זהות מטקסט חופשי בעברית.
6. **אימות רינדור RTL.** לווידג'טים באתר, הגדירו `dir="rtl"` על המכולה החיצונית ובדקו על מכשיר אמיתי. לוואטסאפ וטלגרם, ודאו שטקסט עברי וכפתורים אינטראקטיביים מוצגים נכון גם ב-iOS וגם ב-Android.

## דוגמאות

### דוגמה 1: בוט סטטוס הזמנה בוואטסאפ בעברית

המשתמש אומר: "תבנה לי בוט וואטסאפ בעברית שמאפשר ללקוחות לבדוק את סטטוס ההזמנה."

פעולות:
1. זיהוי הערוץ: WhatsApp Business Cloud API.
2. אישור רגיסטר לא רשמי (קהל צרכני) וניסוח ניטרלי מבחינת מגדר לפנייה רחבה.
3. התחלה מ-`scripts/whatsapp-webhook-handler.py`, שכבר כולל אימות webhook, בדיקות חתימה ותבניות תגובה בעברית.
4. חיבור תפריט כפתורים אינטראקטיבי ("בדיקת הזמנה", "שאלות נפוצות", "דבר/י עם נציג") ומצב `waiting_order_number` שמאמת את מספר ההזמנה ומחפש אותה.
5. הגשת תבנית `order_confirmation_he` בעברית דרך Meta Business Suite לעדכונים יזומים יוצאים.

תוצאה: מטפל webhook עובד שמברך משתמשים בעברית, מנתב תגובות כפתורים ועונה על שאילתות סטטוס הזמנה.

### דוגמה 2: הוספת ווידג'ט צ'אט עברי RTL לאתר קיים

המשתמש אומר: "תוסיף לי ווידג'ט צ'אט בעברית לאתר עם פריסת RTL תקינה."

פעולות:
1. זיהוי הערוץ: ווידג'ט צ'אט מוטמע באתר.
2. אישור רגיסטר לא רשמי וסימון לוכסן לכפתורי פעולה.
3. שימוש ב-CSS של פריסת בועות צ'אט RTL וברכיבי `MessageBubble` / `detectDirection` מסעיף ווידג'ט צ'אט לאתרים.
4. הגדרת `dir="rtl"` על אלמנט מכולת הצ'אט החיצונית (לא רק ב-CSS) והוספת `direction: rtl` לשדה הקלט.
5. אימות היישור ב-DevTools של הדפדפן: בועות משתמש בצד ימין, בועות בוט בצד שמאל, חותמות זמן בצד הנגרר.

תוצאה: ווידג'ט צ'אט שמרנדר עברית בצורה טבעית, מטפל בהודעות מעורבות עברית/אנגלית לכל בועה בנפרד, ולא נשבר כש-framework אב מגדיר `direction: ltr`.

## עיצוב שיחות בעברית

### רשמי מול לא רשמי

בעברית יש הבדל ברור בין רגיסטר רשמי ללא רשמי. בחרו לפי קהל היעד:

**לא רשמי (כדאי לרוב הבוטים לצרכנים):**
- גוף שני יחיד: את/ה
- משפטים קצרים
- ביטויים מדוברים: "מה קורה?", "אין בעיה", "סבבה"

**רשמי (כדאי לממשלה, בנקאות, משפטי):**
- גוף שני רבים או סביל
- משפטים מלאים בדקדוק תקין
- ביטויים רשמיים: "כיצד נוכל לסייע?", "בבקשה המתן/י"

### תגובות מודעות מגדר

בעברית, פעלים ותארים מוטי מגדר. טפלו בזה בחוכמה:

**אסטרטגיה 1: שאלו בתחילת השיחה ותזכרו**
```
בוט: "היי! לפני שנתחיל, איך לפנות אליך?"
אפשרויות: [זכר] [נקבה] [לא משנה לי]
```

**אסטרטגיה 2: ניסוח ניטרלי מבחינת מגדר**
```
-- במקום: "אתה/את מוזמן/מוזמנת להמשיך"
-- כתוב: "ניתן להמשיך" או "אפשר להמשיך"

-- במקום: "רוצה לראות?"
-- כתוב: "לראות עוד אפשרויות?"
```

**אסטרטגיה 3: סימון לוכסן (נפוץ בהייטק הישראלי)**
```
"את/ה מוזמן/ת לבדוק את האפשרויות"
```

### עיצוב תאריכים ושעות בצ'אט

```python
# פורמט תאריכים להודעות צ'אט
# תקן ישראלי: DD/MM/YYYY או DD.MM.YYYY
# בשיחה: "יום שלישי, 14 במרץ"

# פורמט שעות: שעון 24 שעות הוא הסטנדרט בישראל
# "בשעה 14:30", לא "2:30 PM"

# זמן יחסי בעברית
RELATIVE_TIME_HE = {
    "just_now": "עכשיו",
    "minutes_ago": "לפני {n} דקות",
    "hours_ago": "לפני {n} שעות",
    "yesterday": "אתמול",
    "days_ago": "לפני {n} ימים",
    "today": "היום",
    "tomorrow": "מחר",
}
```

## אינטגרציה עם WhatsApp Business API

### הגדרה דרך Cloud API

ה-Cloud API של וואטסאפ (ה-API הרשמי של מטא) הוא הגישה המומלצת לעסקים ישראליים:

1. **צרו חשבון עסקי של מטא** ב-business.facebook.com
2. **הגדירו חשבון WhatsApp Business** ב-Meta Business Suite
3. **צרו אפליקציה** ב-Meta Developers והוסיפו את מוצר WhatsApp
4. **קבלו מספר טלפון**: מספרים ישראליים (+972) נתמכים
5. **ייצרו access token** לקריאות API

### תבניות הודעות בעברית

וואטסאפ דורש תבניות שאושרו מראש להודעות יוצאות. הגישו תבניות בעברית דרך Meta Business Suite:

```python
# דוגמה לתבנית: אישור הזמנה
# שם תבנית: order_confirmation_he
# שפה: he
# גוף: "שלום {{1}}, ההזמנה שלך מספר {{2}} התקבלה בהצלחה. סכום: ₪{{3}}. צפי למשלוח: {{4}}."

import requests

def send_template_message(phone_number: str, template_data: dict):
    """שליחת הודעת תבנית בוואטסאפ בעברית."""
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,  # פורמט E.164: 972501234567
        "type": "template",
        "template": {
            "name": "order_confirmation_he",
            "language": {"code": "he"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": template_data["customer_name"]},
                        {"type": "text", "text": template_data["order_id"]},
                        {"type": "text", "text": template_data["amount"]},
                        {"type": "text", "text": template_data["delivery_date"]},
                    ]
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### הודעות אינטראקטיביות

וואטסאפ תומך בכפתורים ורשימות אינטראקטיביות שעובדים מצוין עם עברית:

```python
def send_interactive_buttons(phone_number: str):
    """שליחת כפתורים אינטראקטיביים בעברית."""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "איך אפשר לעזור לך היום?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "check_order", "title": "בדיקת הזמנה"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "support", "title": "תמיכה טכנית"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "hours", "title": "שעות פעילות"}
                    }
                ]
            }
        }
    }

    return send_whatsapp_message(payload)
```

### טיפול ב-Webhook

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """אימות webhook של וואטסאפ."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """עיבוד הודעות נכנסות מוואטסאפ."""
    # אימות חתימה
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = request.get_data()
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return "Invalid signature", 403

    data = request.get_json()
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change["field"] == "messages":
                for message in change["value"].get("messages", []):
                    handle_incoming_message(message)

    return jsonify({"status": "ok"}), 200
```

## אינטגרציה עם טלגרם

### הגדרת BotFather

1. פתחו את @BotFather בטלגרם
2. שלחו `/newbot` ועקבו אחרי ההוראות
3. הגדירו תיאור בעברית: `/setdescription` ושלחו טקסט בעברית
4. הגדירו תפריט פקודות בעברית:

```
/setcommands

start - התחל שיחה
help - עזרה
menu - תפריט ראשי
order - הזמנה חדשה
status - סטטוס הזמנה
language - שפה / Language
```

### מקלדות Inline בעברית

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

async def start(update: Update, context):
    """שליחת הודעת פתיחה בעברית עם מקלדת inline."""
    keyboard = [
        [
            InlineKeyboardButton("הזמנה חדשה", callback_data="new_order"),
            InlineKeyboardButton("בדיקת סטטוס", callback_data="check_status"),
        ],
        [
            InlineKeyboardButton("שאלות נפוצות", callback_data="faq"),
            InlineKeyboardButton("דבר/י עם נציג", callback_data="human_agent"),
        ],
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "שלום!\n\nאני הבוט של [שם העסק]. איך אפשר לעזור?",
        reply_markup=reply_markup,
    )
```

### הרשאות בוט קבוצתי

לבוטים בקבוצות טלגרם, הגדירו הרשאות מתאימות:

```python
# ב-BotFather:
# /setjoingroups - הפעלה/כיבוי הצטרפות לקבוצות
# /setprivacy - הגדרת מצב פרטיות (מומלץ: מופעל, הבוט רואה רק פקודות)

# טיפול שונה בהודעות קבוצתיות
async def handle_message(update: Update, context):
    chat_type = update.effective_chat.type

    if chat_type in ("group", "supergroup"):
        # בקבוצות, הגיבו רק לפקודות או אזכורים
        if update.message.text and (
            update.message.text.startswith("/") or
            f"@{context.bot.username}" in update.message.text
        ):
            await process_group_command(update, context)
    else:
        # בצ'אט פרטי, הגיבו לכל ההודעות
        await process_private_message(update, context)
```

## ווידג'ט צ'אט לאתרים

### פריסת בועות צ'אט RTL

```css
/* מכולת צ'אט RTL */
.chat-container {
  direction: rtl;
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Heebo', 'Assistant', sans-serif;
}

/* הודעת משתמש (צד ימין ב-RTL) */
.message-user {
  align-self: flex-start; /* ב-RTL, flex-start הוא ימין */
  background-color: #dcf8c6;
  border-bottom-right-radius: 4px;
  color: #111;
}

/* הודעת בוט (צד שמאל ב-RTL) */
.message-bot {
  align-self: flex-end; /* ב-RTL, flex-end הוא שמאל */
  background-color: #fff;
  border-bottom-left-radius: 4px;
  color: #111;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* שדה קלט */
.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 14px;
  direction: rtl;
  text-align: right;
}

/* כפתור שליחה */
.chat-send-btn {
  background: #25d366;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transform: scaleX(-1); /* היפוך אייקון שליחה ל-RTL */
}
```

### אינדיקטור הקלדה בעברית

```typescript
function TypingIndicator({ isTyping }: { isTyping: boolean }) {
  if (!isTyping) return null;

  return (
    <div className="message-bubble message-bot typing-indicator">
      <span className="typing-text">מקליד/ה...</span>
      <span className="typing-dots">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </span>
    </div>
  );
}
```

### לוגיקת יישור הודעות

```typescript
// זיהוי כיוון טקסט להודעות מעורבות עברית/אנגלית
function detectDirection(text: string): 'rtl' | 'ltr' {
  const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF]/;
  const ltrRegex = /[a-zA-Z]/;

  for (const char of text) {
    if (rtlRegex.test(char)) return 'rtl';
    if (ltrRegex.test(char)) return 'ltr';
  }

  return 'rtl'; // ברירת מחדל RTL לאפליקציות עבריות
}
```

## דפוסי NLP בעברית

### זיהוי כוונה (Intent Detection)

המורפולוגיה המורכבת של עברית מאתגרת את זיהוי הכוונות. אסטרטגיות מרכזיות:

```python
# כוונות נפוצות בעברית עם ביטויים לדוגמה
HEBREW_INTENTS = {
    "greeting": [
        "שלום", "היי", "הי", "בוקר טוב", "ערב טוב",
        "מה קורה", "מה נשמע", "אהלן",
    ],
    "farewell": [
        "ביי", "להתראות", "שלום", "יום טוב", "לילה טוב",
    ],
    "help": [
        "עזרה", "אני צריך עזרה", "אני צריכה עזרה",
        "תעזור לי", "תעזרי לי", "איך עושים",
    ],
    "order_status": [
        "איפה ההזמנה", "סטטוס הזמנה", "מתי מגיע",
        "עדכון משלוח", "מספר מעקב",
    ],
    "complaint": [
        "לא מרוצה", "בעיה", "תלונה", "לא עובד",
        "שירות גרוע", "רוצה להתלונן",
    ],
    "human_agent": [
        "נציג", "אדם אמיתי", "תעביר לנציג",
        "לדבר עם מישהו", "אני רוצה לדבר עם בנאדם",
    ],
}
```

**מגבלות של התאמת תת-מחרוזת נאיבית (קראו לפני שמשיקים):**

- ניקוד: רשימות מילות המפתח למעלה מניחות טקסט לא מנוקד. אם קלט המשתמש (או הרשימות שלכם) מכילים ניקוד, `phrase in text` נכשל. הסירו ניקוד משני הצדדים קודם, למשל `re.sub(r'[֑-ׇ]', '', text)`.
- אותיות שימוש: בעברית מתחברות ב/ל/מ/ה/ו/כ/ש למילה הבאה, ולכן "בהזמנה" לא יתאים למילת המפתח "הזמנה". התאמת `phrase in text` נאיבית מחמיצה את אלה בשקט. לכל דבר מעבר לדמו, השתמשו בכלי NLP לעברית שמטפלים במורפולוגיה, למשל המנתח המורפולוגי YAP (https://github.com/OnlpLab/yap) או צינור העברית של Stanza, או עברו ל-LLM (למטה).

**סיווג כוונה והפקת תגובה מבוססי LLM (מומלץ לייצור):**

התאמת תת-מחרוזת נשברת על פרפרזות, שגיאות כתיב ומורפולוגיה. לייצור, הנחו LLM לסווג כוונה ולנסח את התגובה. דפוס תמציתי:

```python
# פסאודו-קוד - קראו ל-SDK של הספק שלכם (Anthropic, OpenAI או Google).
INTENT_SYSTEM_PROMPT = """אתה מסווג כוונות לצ'אטבוט שירות בעברית.
החזר JSON בלבד: {"intent": "<one of: greeting|farewell|help|order_status|complaint|pricing|human_agent|unknown>", "confidence": 0.0-1.0}.
התחשב במורפולוגיה עברית (אותיות שימוש ב/ל/מ), שגיאות כתיב וסלנג."""

# 1. תור סיווג: שלחו את INTENT_SYSTEM_PROMPT + הודעת המשתמש, פרסו את ה-JSON.
# 2. תור תגובה: שלחו system prompt נפרד עם הכוונה שזוהתה, היסטוריית השיחה,
#    והחלטות הרגיסטר והמגדר, ובקשו את התשובה בעברית.
```

הנחיות:
- שמרו את הסיווג ואת הפקת התגובה כשתי קריאות נפרדות כדי שתוכלו לתעד דיוק כוונות בנפרד.
- כפו פלט JSON ואמתו אותו; חזרו למתאם מילות המפתח אם הפענוח נכשל.
- מודלים שמטפלים בעברית היטב (נכון לאמצע 2026): Anthropic Claude (דרגות Sonnet/Opus), משפחת OpenAI GPT-5.x, ו-Google Gemini 3.x. שמות המודלים והדרגות משתנים תכופות (GPT-4o/4.1 ו-Gemini 2.x הוצאו משימוש בתחילת 2026), אז בדקו את רשימת המודלים העדכנית של כל ספק לפני שמקבעים אחד.
- לאפשרות עברית-נייטיב, בחנו את Dicta-LM 3.0 (דיקטה, אוניברסיטת בר-אילן) לסיווג on-prem.
- **התגוננו מפני prompt injection (OWASP LLM01).** כשטקסט חופשי של משתמש מגיע ל-LLM שיכול להפעיל פעולות (חיפוש הזמנה, העברה לנציג, פתיחת פנייה), התייחסו אליו כלא-מהימן: עטפו את טקסט המשתמש במפרידים ברורים, הנחו את המודל להתעלם מכל הוראה שבתוכו, לעולם אל תחשפו את הפרומפט המערכתי, ואמתו את הפעולה שהמודל בחר מול רשימת היתר לפני ביצוע.
- **בצעו streaming בווידג'ט הווב, ובאפר ב-WhatsApp/Telegram.** צ'אט ווב צריך לזרום טוקנים להשהיה נתפסת נמוכה; WhatsApp ו-Telegram לא יכולים לזרום הודעה חלקית, אז הציגו אינדיקטור הקלדה ושלחו את התשובה המלאה כשהיא מוכנה.

### חילוץ ישויות (Entity Extraction)

חילוץ ישויות ספציפיות לישראל מטקסט עברי:

```python
import re

def extract_israeli_entities(text: str) -> dict:
    """חילוץ ישויות ישראליות מטקסט עברי."""
    entities = {}

    # מספרי טלפון ישראליים
    phone_patterns = [
        r'05\d[\s-]?\d{3}[\s-]?\d{4}',   # נייד: 050-1234567
        r'0[2-9][\s-]?\d{3}[\s-]?\d{4}',  # קווי: 02-1234567
        r'\+972[\s-]?\d{1,2}[\s-]?\d{3}[\s-]?\d{4}',  # בינלאומי
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("phone_numbers", []).extend(matches)

    # סכומים בשקלים
    nis_patterns = [
        r'₪\s?[\d,]+(?:\.\d{2})?',
        r'[\d,]+(?:\.\d{2})?\s?(?:₪|שקל|שקלים|ש"ח|שח)',
    ]
    for pattern in nis_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("amounts_nis", []).extend(matches)

    # תאריכים ישראליים (DD/MM/YYYY)
    date_patterns = [
        r'\d{1,2}[/.]\d{1,2}[/.]\d{2,4}',
        r'\d{1,2}\s+ב?(?:ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("dates", []).extend(matches)

    # תעודת זהות (9 ספרות)
    # שימו לב: ה-regex תופס כל רצף של 9 ספרות בלי אימות ספרת ביקורת.
    # הוא יקבל מספרי טלפון, מספרי הזמנה ושגיאות כתיב. אמתו את ההתאמות
    # עם is_valid_teudat_zehut() למטה לפני שמתייחסים אליהן כתעודת זהות אמיתית.
    tz_matches = [m for m in re.findall(r'(?<!\d)\d{9}(?!\d)', text)
                  if is_valid_teudat_zehut(m)]
    if tz_matches:
        entities["teudat_zehut"] = tz_matches

    return entities


def is_valid_teudat_zehut(value: str) -> bool:
    """אימות תעודת זהות ישראלית באמצעות אלגוריתם ספרת הביקורת הרשמי.

    רצף של 9 ספרות אינו תעודת זהות תקינה רק כי יש בו 9 ספרות. הפונקציה
    מיישמת את שקלול הספרות שמשרד הפנים משתמש בו, כך שמספרי טלפון
    ורצפי ספרות אקראיים נדחים.
    """
    digits = value.strip()
    if len(digits) != 9 or not digits.isdigit():
        return False
    total = 0
    for i, ch in enumerate(digits):
        n = int(ch) * (1 if i % 2 == 0 else 2)
        total += n if n < 10 else n - 9
    return total % 10 == 0
```

### ניתוח סנטימנט לעברית

```python
# מילון סנטימנט פשוט לעברית
HEBREW_SENTIMENT = {
    # חיובי
    "מעולה": 1.0, "מצוין": 1.0, "נהדר": 0.9, "אהבתי": 0.9,
    "טוב": 0.6, "נחמד": 0.5, "תודה רבה": 0.7, "ממליץ": 0.8,
    "מרוצה": 0.8, "אחלה": 0.8, "סבבה": 0.5, "בומבה": 0.9,

    # שלילי
    "גרוע": -0.9, "נורא": -0.9, "מאכזב": -0.8,
    "רע": -0.7, "לא טוב": -0.6, "בעיה": -0.5,
    "לא עובד": -0.7, "לא מרוצה": -0.8, "אכזבה": -0.8,
}

def analyze_hebrew_sentiment(text: str) -> dict:
    """ניתוח סנטימנט בסיסי בעברית באמצעות מילון."""
    scores = []
    for expression, score in sorted(
        HEBREW_SENTIMENT.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if expression in text:
            scores.append(score)

    if not scores:
        return {"sentiment": "neutral", "score": 0.0}

    avg = sum(scores) / len(scores)
    sentiment = "positive" if avg > 0.2 else "negative" if avg < -0.2 else "neutral"
    return {"sentiment": sentiment, "score": round(avg, 2)}
```

## זרימות שיחה

### עץ תפריט בעברית

```python
CONVERSATION_FLOWS = {
    "main_menu": {
        "message": "שלום! איך אפשר לעזור?\nבחר/י אחת מהאפשרויות:",
        "options": {
            "1": {"label": "הזמנה חדשה", "next": "new_order"},
            "2": {"label": "בדיקת סטטוס", "next": "check_status"},
            "3": {"label": "שאלות נפוצות", "next": "faq"},
            "4": {"label": "דבר/י עם נציג", "next": "human_handoff"},
        },
    },
    "new_order": {
        "message": "מעולה! בוא/י נתחיל הזמנה.\nמה תרצה/י להזמין?",
        "type": "free_text",
        "next": "order_quantity",
        "back": "main_menu",
    },
    "faq": {
        "message": "שאלות נפוצות:\n\n1. שעות פעילות\n2. מדיניות החזרות\n3. אזורי משלוח\n4. אמצעי תשלום",
        "options": {
            "1": {"label": "שעות", "response": "א'-ה': 9:00-17:00\nו': 9:00-13:00\nשבת: סגור"},
            "2": {"label": "החזרות", "response": "ניתן להחזיר עד 14 יום מהרכישה עם חשבונית."},
            "3": {"label": "משלוחים", "response": "שולחים לכל הארץ. רגיל: 5-7 ימים. מהיר: 1-2 ימים."},
            "4": {"label": "תשלום", "response": "ויזה, מאסטרקארד, ביט, פייבוקס, העברה, תשלומים."},
        },
        "back": "main_menu",
    },
}
```

### טיפול ב-Fallback

```python
FALLBACK_RESPONSES = [
    "לא הצלחתי להבין. אפשר לנסח אחרת?",
    "סליחה, לא הבנתי. נסה/י שוב או הקלד/י 'תפריט'.",
    "לא בטוח/ה שהבנתי. אפשר לבחור מהאפשרויות או לכתוב 'עזרה'.",
]

# אחרי 3 ניסיונות כושלים
CONFUSED_RESPONSE = (
    "נראה שאני מתקשה להבין. בוא/י ננסה אחרת.\n"
    "הקלד/י מספר מהתפריט, או 'נציג' לשיחה עם אדם."
)
```

### העברה לנציג אנושי

```python
async def handoff_to_human(user_id: str, context: dict):
    """העברת שיחה לנציג אנושי."""
    handoff_message = (
        "תודה על הסבלנות. מעביר/ה אותך לנציג אנושי.\n"
        "זמן המתנה משוער: {wait_time} דקות.\n\n"
        "כל מה שכתבת עד עכשיו יועבר לנציג."
    )

    ticket = {
        "user_id": user_id,
        "channel": context.get("channel", "web"),
        "language": "he",
        "conversation_history": context.get("history", []),
    }

    await support_queue.add(ticket)
    return handoff_message.format(wait_time=await support_queue.estimated_wait())
```

## ביטויים נפוצים לצ'אטבוט בעברית

### ביטויים חיוניים

לקובץ מוכן להעתקה של ביטויי שיחה בעברית (פתיחה, אישור, עיבוד, הצלחה, שגיאה, fallback, סיום, המתנה, התנצלות) עם תעתיק ומתי להשתמש בכל אחד, ראו `references/hebrew-chatbot-phrases.md`.

## משאבים מצורפים

הסקיל הזה כולל סקריפטים בתיקיית `scripts/`:

- `whatsapp-webhook-handler.py`: מטפל webhook מלא ל-WhatsApp Cloud API עם אימות חתימה, ניתוב הודעות ותבניות תגובה בעברית
- `telegram-bot-scaffold.py`: בוט טלגרם מוכן עם תמיכה בעברית, מקלדות inline, ניהול מצב שיחה ומטפלי פקודות

ומסמכי עזר בתיקיית `references/`:

- `hebrew-chatbot-phrases.md`: ביטויים שיחתיים בעברית לבוטים, מאורגנים לפי קטגוריות עם תעתיקים
- `whatsapp-business-api-guide.md`: מדריך הגדרת WhatsApp Business API לעסקים ישראליים

## מלכודות נפוצות

- תגובות צ'אטבוט בעברית חייבות להיות מיושרות RTL. סוכנים עלולים ליצור HTML/CSS ללא dir="rtl", מה שגורם לטקסט עברי להתיישר שמאלה ולהיראות לא טבעי.
- בעברית יש הטיות פועל מגדריות. צ'אטבוט שפונה למשתמש צריך להשתמש בצורות ניטרליות מגדרית או לשאול את המשתמש על המגדר המועדף. סוכנים עלולים להשתמש כברירת מחדל בצורות זכר.
- ברכות נפוצות בעברית משתנות לפי שעת היום: "בוקר טוב" (בוקר), "צהריים טובים" (צהריים), "ערב טוב" (ערב). סוכנים עלולים להשתמש בברכה אחידה ללא התחשבות בשעה.
- טוקניזציה של מילים בעברית שונה מאנגלית. אותיות שימוש (ב-, ל-, מ-) מחוברות למילה הבאה. סוכנים עלולים לפצל טוקנים בצורה שגויה ולפגוע בזיהוי כוונות.
- משתמשים ישראליים מצפים לתקשורת צ'אטבוט לא פורמלית ("דוגרי"). עברית רשמית מדי נשמעת רובוטית ומנוכרת. סוכנים עלולים ליצור עברית פורמלית שמרחיקה משתמשים ישראליים.

## קישורי עזר

| מקור | קישור | מה לבדוק |
|------|--------|----------|
| WhatsApp Cloud API Docs | https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform | גרסת API, סוגי הודעות, פורמט webhook |
| Meta Graph API Changelog | https://developers.facebook.com/docs/graph-api/changelog/ | גרסת API עדכנית, שינויים שוברים |
| Telegram Bot API Docs | https://core.telegram.org/bots/api | מתודות Bot API, מקלדות inline, הגדרת webhook |
| python-telegram-bot Docs | https://docs.python-telegram-bot.org/ | גרסת ספרייה, שינויים ב-API אסינכרוני |
| Meta Business Suite | https://business.facebook.com/ | יצירת תבניות, הגדרת מספר טלפון |

## פתרון בעיות

**Webhook של וואטסאפ מחזיר 403 אחרי פריסה**
- סיבה: אימות `X-Hub-Signature-256` נכשל כי `APP_SECRET` לא הוגדר או מכיל ערך שגוי. מטא חותמת את הודעות ה-webhook עם ה-App Secret, לא עם ה-verify token.
- פתרון: הגדירו את `WHATSAPP_APP_SECRET` לערך מ-Meta Developers > App Settings > Basic > App Secret. הפעילו מחדש את השרת וודאו שהערך תואם בדיוק (ללא רווחים מיותרים).

**תבנית הודעה בעברית נדחתה על ידי מטא**
- סיבה: גוף התבנית מכיל משתנים ({{1}}) שמרכיבים את כל ההודעה, או משתמש בשפה שיווקית בתבנית מסוג Utility. תהליך הביקורת של מטא מסמן דפוסים כאלה.
- פתרון: וודאו שטקסט התבנית מכיל תוכן קבוע משמעותי סביב המשתנים. אם נדחתה, בדקו את סיבת הדחייה ב-Meta Business Suite > WhatsApp > Message Templates, התאימו את הנוסח ושלחו מחדש.

**בוט טלגרם מתעלם מהודעות בקבוצות**
- סיבה: מצב פרטיות מופעל כברירת מחדל ב-BotFather. במצב פרטיות, הבוט מקבל רק הודעות שמתחילות ב-`/` או שמזכירות את הבוט עם @.
- פתרון: תכננו את הבוט לעבוד עם פקודות בלבד בקבוצות (מומלץ), או כבו את מצב הפרטיות דרך BotFather: `/setprivacy` > Disable. שימו לב שכיבוי הפרטיות גורם לבוט לקבל את כל הודעות הקבוצה.

**טקסט RTL בווידג'ט צ'אט מיושר שמאלה למרות `direction: rtl`**
- סיבה: אלמנט צאצא דורס את הכיוון, או שה-CSS מוחל על המכולה הלא נכונה. נפוץ בשימוש עם framework שמגדיר `direction: ltr` ברמת ה-body.
- פתרון: הגדירו `dir="rtl"` על אלמנט ה-HTML של מכולת הצ'אט החיצונית (לא רק ב-CSS). הוסיפו גם `direction: rtl` לשדה הקלט ולכל מכולות בועות ההודעות בנפרד. בדקו עם DevTools בדפדפן היכן הדריסה מתרחשת.
