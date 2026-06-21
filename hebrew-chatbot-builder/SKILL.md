---
name: hebrew-chatbot-builder
description: Build conversational AI chatbots with native Hebrew support, including WhatsApp Business API integration, Telegram bot scaffolding, web chat widgets, Hebrew NLP patterns, and RTL chat UI components. Prevents common Hebrew chatbot mistakes like broken RTL alignment, incorrect gender inflections, and poor tokenization of prefixed prepositions that break intent detection. Use when user asks to "build a Hebrew chatbot", "integrate WhatsApp bot in Hebrew", "binui bot b'ivrit", or design conversation flows for Hebrew speakers. Covers intent detection for Hebrew morphology, entity extraction for Israeli data (NIS amounts, phone numbers, dates), and gender-aware responses. Do NOT use for non-Hebrew chatbots or general NLP pipelines without a Hebrew component.
license: MIT
---

# Hebrew Chatbot Builder

Build production-ready conversational AI chatbots with native Hebrew support. This skill covers platform integrations (WhatsApp, Telegram, web), Hebrew language patterns, RTL UI components, and conversation flow design for Hebrew speakers.

## Instructions

Follow this procedure when building a Hebrew chatbot:

1. **Identify the platform/channel.** Confirm whether the bot runs on WhatsApp Business API, Telegram, an embedded web widget, or several at once. Each has a different scaffold and message model.
2. **Confirm formal or informal register.** Ask the user whether the audience expects informal Hebrew ("דוגרי", recommended for most consumer bots) or formal Hebrew (government, banking, legal). This decision shapes every response string.
3. **Ask the gender-handling strategy.** Decide between asking the user's gender early and remembering it, using gender-neutral phrasing throughout, or slash notation ("את/ה"). See the Gender-Aware Responses section.
4. **Scaffold via the relevant bundled script.** Use `scripts/whatsapp-webhook-handler.py` for WhatsApp or `scripts/telegram-bot-scaffold.py` for Telegram as the starting point, then adapt the Hebrew response templates and conversation flows.
5. **Wire entity extraction.** Add `extract_israeli_entities()` (or an equivalent) so the bot recognizes Israeli phone numbers, shekel amounts, dates, and Teudat Zehut from free-text Hebrew input.
6. **Verify RTL rendering.** For web widgets, set `dir="rtl"` on the outermost container and test on a real device. For WhatsApp and Telegram, verify Hebrew text and interactive buttons render correctly on both iOS and Android.

## Examples

### Example 1: WhatsApp order-status bot in Hebrew

User says: "Build a WhatsApp bot in Hebrew that lets customers check their order status."

Actions:
1. Identify the channel: WhatsApp Business Cloud API.
2. Confirm informal register (consumer audience) and gender-neutral phrasing for broad reach.
3. Start from `scripts/whatsapp-webhook-handler.py`, which already includes webhook verification, signature checks, and Hebrew response templates.
4. Wire an interactive button menu ("בדיקת הזמנה", "שאלות נפוצות", "דבר/י עם נציג") and a `waiting_order_number` state that validates the order number and looks it up.
5. Submit a Hebrew `order_confirmation_he` template via Meta Business Suite for proactive outbound updates.

Result: A working webhook handler that greets users in Hebrew, routes button replies, and answers order-status queries.

### Example 2: Add an RTL Hebrew web chat widget to an existing site

User says: "Add a Hebrew chat widget to my website with proper RTL layout."

Actions:
1. Identify the channel: embedded web widget.
2. Confirm informal register and slash notation for CTAs.
3. Use the RTL Chat Bubble Layout CSS and the `MessageBubble` / `detectDirection` components from the Web Chat Widget section.
4. Set `dir="rtl"` on the outermost chat container element (not only in CSS) and add `direction: rtl` to the input field.
5. Verify alignment in browser DevTools: user bubbles on the right, bot bubbles on the left, timestamps on the trailing side.

Result: A chat widget that renders Hebrew naturally, handles mixed Hebrew/English messages per-bubble, and does not break when a parent framework sets `direction: ltr`.

## Hebrew Conversation Design

### Formal vs Informal Register

Hebrew has distinct formal and informal registers. Choose based on your audience:

**Informal (recommended for most consumer bots):**
- Use second person singular: את/ה (you)
- Shorter sentences
- Colloquial expressions: "מה קורה?", "אין בעיה", "סבבה"

**Formal (recommended for government, banking, legal):**
- Use second person plural or passive voice
- Full sentences with proper grammar
- Formal expressions: "כיצד נוכל לסייע?", "בבקשה המתן/י"

### Gender-Aware Responses

Hebrew verbs and adjectives are gender-inflected. Handle this gracefully:

**Strategy 1: Ask early and remember**
```
Bot: "היי! לפני שנתחיל, איך לפנות אליך?"
Options: [זכר] [נקבה] [לא משנה לי]
```

**Strategy 2: Use gender-neutral phrasing**
```
-- Instead of: "אתה/את מוזמן/מוזמנת להמשיך"
-- Use: "ניתן להמשיך" or "אפשר להמשיך"

-- Instead of: "רוצה/רוצה לראות?"
-- Use: "לראות עוד אפשרויות?"
```

**Strategy 3: Slash notation (common in Israeli tech)**
```
"את/ה מוזמן/ת לבדוק את האפשרויות"
```

### Hebrew Date/Time Formatting in Chat

```python
# Date formats for chat messages
# Israeli standard: DD/MM/YYYY or DD.MM.YYYY
# In conversation: "יום שלישי, 14 במרץ" (Tuesday, March 14)

# Time format: 24-hour clock is standard in Israel
# "בשעה 14:30" (at 14:30), not "2:30 PM"

# Relative time in Hebrew
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

## WhatsApp Business API Integration

### Setup via Cloud API

The WhatsApp Cloud API (Meta's official API) is the recommended approach for Israeli businesses:

1. **Create a Meta Business Account** at business.facebook.com
2. **Set up a WhatsApp Business Account** in Meta Business Suite
3. **Create an App** in Meta Developers and add WhatsApp product
4. **Get a phone number**: Israeli numbers (+972) are supported
5. **Generate an access token** for API calls

### Message Templates (Hebrew)

WhatsApp requires pre-approved templates for outbound messages. Submit Hebrew templates via the Meta Business Suite:

```python
# Template example: Order confirmation
# Template name: order_confirmation_he
# Language: he
# Body: "שלום {{1}}, ההזמנה שלך מספר {{2}} התקבלה בהצלחה. סכום: ₪{{3}}. צפי למשלוח: {{4}}."

import requests

def send_template_message(phone_number: str, template_data: dict):
    """Send a WhatsApp template message in Hebrew."""
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,  # E.164 format: 972501234567
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

### Interactive Messages

WhatsApp supports interactive buttons and lists, which work well with Hebrew:

```python
def send_interactive_buttons(phone_number: str):
    """Send interactive buttons in Hebrew."""
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


def send_interactive_list(phone_number: str):
    """Send an interactive list in Hebrew."""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "בחר/י את הנושא שמעניין אותך:"
            },
            "action": {
                "button": "לרשימת האפשרויות",
                "sections": [
                    {
                        "title": "שירותים",
                        "rows": [
                            {"id": "pricing", "title": "מחירון", "description": "צפייה במחירים עדכניים"},
                            {"id": "catalog", "title": "קטלוג", "description": "עיון במוצרים שלנו"},
                            {"id": "branches", "title": "סניפים", "description": "מציאת הסניף הקרוב"}
                        ]
                    },
                    {
                        "title": "תמיכה",
                        "rows": [
                            {"id": "faq", "title": "שאלות נפוצות", "description": "תשובות לשאלות שכיחות"},
                            {"id": "human", "title": "נציג אנושי", "description": "שיחה עם נציג"}
                        ]
                    }
                ]
            }
        }
    }

    return send_whatsapp_message(payload)
```

### Webhook Handling

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

VERIFY_TOKEN = "your_verify_token"
APP_SECRET = "your_app_secret"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Handle WhatsApp webhook verification."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Process incoming WhatsApp messages."""
    # Verify signature
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

def handle_incoming_message(message: dict):
    """Process a single incoming message."""
    sender = message["from"]  # Phone number
    msg_type = message["type"]

    if msg_type == "text":
        text = message["text"]["body"]
        # Process Hebrew text
        process_hebrew_input(sender, text)

    elif msg_type == "interactive":
        # Handle button/list replies
        if "button_reply" in message["interactive"]:
            button_id = message["interactive"]["button_reply"]["id"]
            handle_button_click(sender, button_id)
        elif "list_reply" in message["interactive"]:
            list_id = message["interactive"]["list_reply"]["id"]
            handle_list_selection(sender, list_id)
```

## Telegram Bot Integration

### BotFather Setup

1. Open @BotFather on Telegram
2. Send `/newbot` and follow prompts
3. Set Hebrew description: `/setdescription` then send Hebrew text
4. Set Hebrew commands menu:

```
/setcommands

start - התחל שיחה
help - עזרה
menu - תפריט ראשי
order - הזמנה חדשה
status - סטטוס הזמנה
language - שפה / Language
```

### Hebrew Inline Keyboards

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

async def start(update: Update, context):
    """Send a Hebrew welcome message with inline keyboard."""
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
        "שלום! 👋\n\n"
        "אני הבוט של [שם העסק]. איך אפשר לעזור?",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    if query.data == "new_order":
        await query.edit_message_text("מעולה! בוא/י נתחיל הזמנה.\n\nמה תרצה/י להזמין?")
    elif query.data == "check_status":
        await query.edit_message_text("שלח/י לי את מספר ההזמנה ואבדוק עבורך.")
    elif query.data == "faq":
        await show_faq(query)
    elif query.data == "human_agent":
        await query.edit_message_text(
            "מעביר אותך לנציג אנושי.\n"
            "שעות הפעילות שלנו: א'-ה' 9:00-17:00\n"
            "נציג יחזור אליך בהקדם."
        )
    elif query.data == "lang_en":
        await query.edit_message_text("Switching to English. How can I help you?")

# Build the application
app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
```

### Group Bot Permissions

For Hebrew group bots, set appropriate permissions:

```python
# In BotFather:
# /setjoingroups - Enable/disable joining groups
# /setprivacy - Set privacy mode (recommended: enabled, bot only sees commands)

# Handle group messages differently
async def handle_message(update: Update, context):
    chat_type = update.effective_chat.type

    if chat_type in ("group", "supergroup"):
        # In groups, only respond to commands or mentions
        if update.message.text and (
            update.message.text.startswith("/") or
            f"@{context.bot.username}" in update.message.text
        ):
            await process_group_command(update, context)
    else:
        # In private chat, respond to all messages
        await process_private_message(update, context)
```

## Web Chat Widget

### RTL Chat Bubble Layout

```css
/* RTL Chat Container */
.chat-container {
  direction: rtl;
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Heebo', 'Assistant', sans-serif;
}

/* Message area */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Message bubble base */
.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

/* User message (right side in RTL) */
.message-user {
  align-self: flex-start; /* In RTL, flex-start is right */
  background-color: #dcf8c6;
  border-bottom-right-radius: 4px; /* Tail on right for RTL */
  color: #111;
}

/* Bot message (left side in RTL) */
.message-bot {
  align-self: flex-end; /* In RTL, flex-end is left */
  background-color: #fff;
  border-bottom-left-radius: 4px; /* Tail on left for RTL */
  color: #111;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Timestamp */
.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: left; /* Time on the trailing side */
}

/* Input area */
.chat-input-container {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e0e0e0;
  background: #fff;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 14px;
  direction: rtl;
  text-align: right;
  font-family: inherit;
}

.chat-input::placeholder {
  color: #999;
  text-align: right;
}

.chat-send-btn {
  background: #25d366;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Flip send icon for RTL */
  transform: scaleX(-1);
}
```

### Hebrew Typing Indicator

```typescript
// React component for Hebrew typing indicator
interface TypingIndicatorProps {
  isTyping: boolean;
}

function TypingIndicator({ isTyping }: TypingIndicatorProps) {
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

// CSS for typing animation
/*
.typing-dots {
  display: inline-flex;
  gap: 4px;
  margin-right: 8px;
}

.typing-dots .dot {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-dots .dot:nth-child(1) { animation-delay: 0s; }
.typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}
*/
```

### Message Alignment Logic

```typescript
// Determine text direction for mixed Hebrew/English messages
function detectDirection(text: string): 'rtl' | 'ltr' {
  // Check first strong directional character
  const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF\u0700-\u074F]/;
  const ltrRegex = /[a-zA-Z]/;

  for (const char of text) {
    if (rtlRegex.test(char)) return 'rtl';
    if (ltrRegex.test(char)) return 'ltr';
  }

  return 'rtl'; // Default to RTL for Hebrew-first apps
}

// Apply to message bubble
function MessageBubble({ text, sender }: { text: string; sender: 'user' | 'bot' }) {
  const direction = detectDirection(text);

  return (
    <div
      className={`message-bubble message-${sender}`}
      style={{ direction, textAlign: direction === 'rtl' ? 'right' : 'left' }}
    >
      {text}
    </div>
  );
}
```

## Hebrew NLP Patterns

### Intent Detection

Hebrew morphological complexity makes intent detection challenging. Key strategies:

```python
# Common Hebrew intents with example phrases
HEBREW_INTENTS = {
    "greeting": [
        "שלום", "היי", "הי", "בוקר טוב", "ערב טוב",
        "מה קורה", "מה נשמע", "אהלן",
    ],
    "farewell": [
        "ביי", "להתראות", "שלום", "יום טוב", "לילה טוב",
        "תודה וביי", "נתראה",
    ],
    "help": [
        "עזרה", "אני צריך עזרה", "אני צריכה עזרה",
        "תעזור לי", "תעזרי לי", "איך עושים", "מה עושים",
    ],
    "order_status": [
        "איפה ההזמנה", "סטטוס הזמנה", "מתי מגיע",
        "עדכון משלוח", "בדיקת הזמנה", "מספר מעקב",
    ],
    "complaint": [
        "לא מרוצה", "בעיה", "תלונה", "לא עובד",
        "שירות גרוע", "רוצה להתלונן", "קיבלתי מוצר פגום",
    ],
    "pricing": [
        "כמה עולה", "מה המחיר", "מחירון", "הנחה",
        "מבצע", "זול יותר", "יקר מדי",
    ],
    "human_agent": [
        "נציג", "אדם אמיתי", "תעביר לנציג",
        "לדבר עם מישהו", "מנהל", "אני רוצה לדבר עם בנאדם",
    ],
}

def detect_intent(text: str) -> tuple[str, float]:
    """Detect intent from Hebrew text using keyword matching.
    For production, use an LLM or fine-tuned model instead."""
    text_lower = text.strip()
    best_intent = "unknown"
    best_score = 0.0

    for intent, phrases in HEBREW_INTENTS.items():
        for phrase in phrases:
            if phrase in text_lower:
                # Longer phrase match = higher confidence
                score = len(phrase) / max(len(text_lower), 1)
                if score > best_score:
                    best_score = score
                    best_intent = intent

    return best_intent, min(best_score * 2, 1.0)  # Normalize score
```

**Caveats of naive substring matching (read before shipping):**

- **Nikud / vocalization**: the keyword lists above assume unvocalized text. If user input (or your lists) contain nikud, `phrase in text` fails. Strip nikud from both sides first, for example `re.sub(r'[֑-ׇ]', '', text)`.
- **Prefix prepositions**: Hebrew attaches ב/ל/מ/ה/ו/כ/ש to the following word, so "בהזמנה" will not match the keyword "הזמנה". Naive `phrase in text` silently misses these. For anything beyond a demo, use Hebrew NLP tooling that handles morphology, for example the YAP morphological analyzer (https://github.com/OnlpLab/yap) or Stanza's Hebrew pipeline, or move to an LLM (below).

**LLM-based intent classification and response generation (recommended for production):**

Substring matching breaks on paraphrases, typos, and morphology. For production, prompt an LLM to classify intent and draft the response. A compact pattern:

```python
# Pseudocode - call your provider's SDK (Anthropic, OpenAI, or Google).
INTENT_SYSTEM_PROMPT = """אתה מסווג כוונות לצ'אטבוט שירות בעברית.
החזר JSON בלבד: {"intent": "<one of: greeting|farewell|help|order_status|complaint|pricing|human_agent|unknown>", "confidence": 0.0-1.0}.
התחשב במורפולוגיה עברית (אותיות שימוש ב/ל/מ), שגיאות כתיב וסלנג."""

# 1. Classification turn: send INTENT_SYSTEM_PROMPT + the user message, parse the JSON.
# 2. Response turn: send a separate system prompt with the detected intent,
#    the conversation history, and the register/gender decisions, ask for the Hebrew reply.
```

Guidance:
- Keep classification and response generation as two calls so you can log intent accuracy separately.
- Force JSON output and validate it; fall back to the keyword matcher if parsing fails.
- Models that handle Hebrew well (current as of mid-2026): Anthropic Claude (Sonnet/Opus tiers), the OpenAI GPT-5.x family, and Google Gemini 3.x. Model names and tiers change often (GPT-4o/4.1 and Gemini 2.x were retired in early 2026), so check each provider's current model list before pinning one.
- For a Hebrew-native option, evaluate Dicta-LM 3.0 (Dicta, Bar-Ilan University) for on-prem classification.
- **Guard against prompt injection (OWASP LLM01).** When free-text user input reaches an LLM that can trigger actions (order lookup, human handoff, ticket creation), treat it as untrusted: wrap the user text in clear delimiters, instruct the model to ignore any instructions inside it, never echo the system prompt, and validate the model's chosen action against an allowlist before executing it.
- **Stream on the web widget, buffer on WhatsApp/Telegram.** A web chat should stream tokens for low perceived latency; WhatsApp and Telegram cannot stream a partial message, so show a typing indicator and send the full reply once it is ready.

### Entity Extraction

Extract Israeli-specific entities from Hebrew text:

```python
import re

def extract_israeli_entities(text: str) -> dict:
    """Extract Israeli-specific entities from Hebrew text."""
    entities = {}

    # Israeli phone numbers
    phone_patterns = [
        r'05\d[\s-]?\d{3}[\s-]?\d{4}',   # Mobile: 050-1234567
        r'0[2-9][\s-]?\d{3}[\s-]?\d{4}',  # Landline: 02-1234567
        r'\+972[\s-]?\d{1,2}[\s-]?\d{3}[\s-]?\d{4}',  # International
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("phone_numbers", []).extend(matches)

    # NIS amounts (shekel)
    nis_patterns = [
        r'₪\s?[\d,]+(?:\.\d{2})?',           # ₪100 or ₪1,000.00
        r'[\d,]+(?:\.\d{2})?\s?(?:₪|שקל|שקלים|ש"ח|שח)',  # 100 שקל
    ]
    for pattern in nis_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("amounts_nis", []).extend(matches)

    # Israeli dates (DD/MM/YYYY or DD.MM.YYYY)
    date_patterns = [
        r'\d{1,2}[/.]\d{1,2}[/.]\d{2,4}',    # 14/03/2025
        r'\d{1,2}\s+ב?(?:ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            entities.setdefault("dates", []).extend(matches)

    # Teudat Zehut (9 digits, standalone)
    # NOTE: this regex matches ANY 9-digit run with no check-digit validation.
    # It will accept phone numbers, order IDs, and typos. Validate matches
    # with is_valid_teudat_zehut() below before treating them as a real ID.
    tz_pattern = r'(?<!\d)\d{9}(?!\d)'
    tz_matches = [m for m in re.findall(tz_pattern, text) if is_valid_teudat_zehut(m)]
    if tz_matches:
        entities["teudat_zehut"] = tz_matches

    # Email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        entities["emails"] = email_matches

    return entities


def is_valid_teudat_zehut(value: str) -> bool:
    """Validate an Israeli Teudat Zehut using the official check-digit algorithm.

    A 9-digit run is NOT a valid ID just because it has 9 digits. This applies
    the Luhn-style weighting the Interior Ministry uses, so phone numbers and
    random digit runs are rejected.
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

### Sentiment Analysis for Hebrew

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

## Conversation Flows

### Hebrew Menu Tree

```python
# Conversation state machine for Hebrew chatbot
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
    "order_quantity": {
        "message": "כמה יחידות?",
        "type": "number",
        "validation": {"min": 1, "max": 100},
        "error": "נא להזין מספר בין 1 ל-100",
        "next": "order_confirm",
        "back": "new_order",
    },
    "order_confirm": {
        "message": "לסיכום:\n{order_summary}\n\nלאשר הזמנה?",
        "options": {
            "1": {"label": "אישור", "next": "order_complete"},
            "2": {"label": "ביטול", "next": "main_menu"},
        },
    },
    "order_complete": {
        "message": "ההזמנה בוצעה בהצלחה!\nמספר הזמנה: {order_id}\nתודה ויום טוב!",
        "next": "main_menu",
    },
    "check_status": {
        "message": "שלח/י לי את מספר ההזמנה (6 ספרות):",
        "type": "pattern",
        "pattern": r"^\d{6}$",
        "error": "מספר הזמנה צריך להכיל 6 ספרות. נסה/י שוב:",
        "next": "show_status",
        "back": "main_menu",
    },
    "faq": {
        "message": "שאלות נפוצות:\n\n1. שעות פעילות\n2. מדיניות החזרות\n3. אזורי משלוח\n4. אמצעי תשלום\n\nבחר/י נושא:",
        "options": {
            "1": {"label": "שעות פעילות", "response": "שעות פעילות:\nא'-ה': 9:00-17:00\nו': 9:00-13:00\nשבת: סגור"},
            "2": {"label": "החזרות", "response": "ניתן להחזיר מוצרים עד 14 יום מתאריך הרכישה.\nיש להציג חשבונית."},
            "3": {"label": "משלוחים", "response": "אנחנו שולחים לכל הארץ.\nמשלוח רגיל: 5-7 ימי עסקים.\nמשלוח מהיר: 1-2 ימי עסקים."},
            "4": {"label": "תשלום", "response": "אמצעי תשלום:\n- כרטיס אשראי (ויזה, מאסטרקארד, אמקס)\n- ביט / פייבוקס\n- העברה בנקאית\n- תשלומים (עד 12 תשלומים ללא ריבית)"},
        },
        "back": "main_menu",
    },
    "human_handoff": {
        "message": "מעביר אותך לנציג אנושי.\nשעות פעילות: א'-ה' 9:00-17:00.\n\nבינתיים, תאר/י בקצרה את הנושא שלך כדי שנוכל לעזור מהר יותר:",
        "type": "free_text",
        "action": "create_support_ticket",
    },
}
```

### Fallback Handling in Hebrew

```python
FALLBACK_RESPONSES = [
    "לא הצלחתי להבין. אפשר לנסח אחרת?",
    "סליחה, לא הבנתי את הבקשה. נסה/י שוב או הקלד/י 'תפריט' לאפשרויות.",
    "לא בטוח/ה שהבנתי. אפשר לבחור מהאפשרויות או לכתוב 'עזרה'.",
]

CONFUSED_AFTER_ATTEMPTS = (
    "נראה שאני מתקשה להבין. בוא/י ננסה אחרת.\n"
    "הקלד/י מספר מהתפריט, או 'נציג' לשיחה עם אדם."
)

def get_fallback_response(attempt_count: int) -> str:
    """Get an appropriate fallback response based on attempt count."""
    if attempt_count >= 3:
        return CONFUSED_AFTER_ATTEMPTS
    return FALLBACK_RESPONSES[attempt_count % len(FALLBACK_RESPONSES)]
```

### Handoff to Human Agent

```python
async def handoff_to_human(user_id: str, context: dict):
    """Transfer conversation to human agent."""
    handoff_message = (
        "תודה על הסבלנות. מעביר/ה אותך לנציג אנושי.\n"
        "זמן המתנה משוער: {wait_time} דקות.\n\n"
        "כל מה שכתבת עד עכשיו יועבר לנציג."
    )

    # Create support ticket with conversation history
    ticket = {
        "user_id": user_id,
        "channel": context.get("channel", "web"),  # whatsapp/telegram/web
        "language": "he",
        "conversation_history": context.get("history", []),
        "detected_intent": context.get("last_intent", "unknown"),
        "sentiment": context.get("sentiment", "neutral"),
        "created_at": datetime.now().isoformat(),
    }

    # Queue for human agent
    await support_queue.add(ticket)

    return handoff_message.format(
        wait_time=await support_queue.estimated_wait()
    )
```

## Common Hebrew Chatbot Phrases

### Essential Phrases

For a copy-paste set of Hebrew conversational phrases (greeting, confirmation, processing, success, error, fallback, goodbye, hold, apology) with transliterations and when to use each, see `references/hebrew-chatbot-phrases.md`.

## Bundled Resources

This skill includes helper scripts in the `scripts/` directory:

- `whatsapp-webhook-handler.py`: Complete WhatsApp Cloud API webhook handler with signature verification, message routing, and Hebrew response templates
- `telegram-bot-scaffold.py`: Telegram bot starter with Hebrew support, inline keyboards, conversation state management, and command handlers

And reference documents in `references/`:

- `hebrew-chatbot-phrases.md`: Comprehensive Hebrew conversational phrases for bots, organized by category with transliterations
- `whatsapp-business-api-guide.md`: Step-by-step WhatsApp Business API setup guide for Israeli businesses

## Gotchas

- Hebrew chatbot responses must be RTL-aligned. Agents may generate HTML/CSS without dir="rtl" attributes, causing Hebrew text to align left and appear unnatural.
- Hebrew has gendered verb conjugations. A chatbot addressing a user should either use gender-neutral forms or ask for the user's preferred gender. Agents may default to masculine Hebrew forms.
- Common Hebrew greetings change by time of day: "בוקר טוב" (morning), "צהריים טובים" (noon), "ערב טוב" (evening). Agents may use a single greeting regardless of time.
- Hebrew word tokenization differs from English. Prefixed prepositions (ב-, ל-, מ-) are attached to the following word. Agents may split tokens incorrectly, breaking intent detection.
- Israeli users expect informal chatbot communication ("דוגרי"). Overly formal Hebrew sounds robotic and unnatural. Agents may generate formal Hebrew that alienates Israeli users.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| WhatsApp Cloud API Docs | https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform | API version, message types, webhook format |
| Meta Graph API Changelog | https://developers.facebook.com/docs/graph-api/changelog/ | Latest API version, breaking changes |
| Telegram Bot API Docs | https://core.telegram.org/bots/api | Bot API methods, inline keyboards, webhook setup |
| python-telegram-bot Docs | https://docs.python-telegram-bot.org/ | Library version, async API changes |
| Meta Business Suite | https://business.facebook.com/ | Template creation, phone number setup |

## Troubleshooting

**WhatsApp webhook returns 403 after deployment**
- Cause: The `X-Hub-Signature-256` verification is failing because `APP_SECRET` is not set or uses the wrong value. Meta signs webhook payloads with your App Secret, not the verify token.
- Solution: Set `WHATSAPP_APP_SECRET` to the value from Meta Developers > App Settings > Basic > App Secret. Restart the server and verify it matches exactly (no trailing whitespace).

**Hebrew text in WhatsApp template rejected by Meta**
- Cause: Template body contains variables ({{1}}) that make up the entire message, or uses promotional language in a Utility-category template. Meta's review process flags these patterns.
- Solution: Ensure template text has substantial fixed content around variables. If rejected, check the rejection reason in Meta Business Suite > WhatsApp > Message Templates, adjust the wording, and resubmit.

**Telegram bot ignores messages in groups**
- Cause: Privacy mode is enabled by default in BotFather. In privacy mode, the bot only receives messages that start with `/` or mention the bot by @username.
- Solution: Either design your bot to work with commands only in groups (recommended), or disable privacy mode via BotFather: `/setprivacy` > Disable. Note that disabling privacy means the bot receives all group messages.

**RTL chat widget text aligns left despite `direction: rtl`**
- Cause: A child element overrides the direction, or the CSS is applied to the wrong container. Common when using a UI framework that sets `direction: ltr` at the body level.
- Solution: Set `dir="rtl"` on the outermost chat container HTML element (not just CSS). Also add `direction: rtl` to the input field and any message bubble containers individually. Inspect with browser DevTools to find where the override occurs.
