"""
WhatsApp Cloud API Webhook Handler

A complete webhook handler for the WhatsApp Business Cloud API with:
- Webhook verification (GET endpoint)
- Message signature verification
- Incoming message routing (text, interactive, media)
- Hebrew response templates
- Session management for conversation state

Requirements:
  pip install flask requests

Environment Variables:
  WHATSAPP_VERIFY_TOKEN   - Token for webhook verification
  WHATSAPP_APP_SECRET     - App secret for signature verification
  WHATSAPP_ACCESS_TOKEN   - Access token for sending messages
  WHATSAPP_PHONE_ID       - Phone number ID from Meta dashboard

Usage:
  export WHATSAPP_VERIFY_TOKEN=your_verify_token
  export WHATSAPP_APP_SECRET=your_app_secret
  export WHATSAPP_ACCESS_TOKEN=your_access_token
  export WHATSAPP_PHONE_ID=your_phone_number_id
  python whatsapp-webhook-handler.py
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import requests
from flask import Flask, jsonify, request

# Configuration
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
APP_SECRET = os.environ.get("WHATSAPP_APP_SECRET", "")
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
GRAPH_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp-bot")

# Flask app
app = Flask(__name__)

# Simple in-memory session store (use Redis in production)
sessions: dict[str, dict[str, Any]] = {}


# =============================================================================
# Hebrew Response Templates
# =============================================================================

RESPONSES = {
    "welcome": (
        "שלום! ברוכים הבאים.\n\n"
        "איך אפשר לעזור לך היום?"
    ),
    "main_menu": "בחר/י אחת מהאפשרויות:",
    "not_understood": "לא הצלחתי להבין. אפשר לנסח אחרת?",
    "processing": "רגע, בודק/ת...",
    "error": "משהו השתבש. נסה/י שוב מאוחר יותר.",
    "goodbye": "תודה ויום טוב!",
    "human_handoff": (
        "מעביר/ה אותך לנציג אנושי.\n"
        "שעות פעילות: א'-ה' 9:00-17:00\n"
        "נציג יחזור אליך בהקדם."
    ),
    "after_hours": (
        "שעות הפעילות שלנו הן א'-ה' 9:00-17:00.\n"
        "השאר/י הודעה ונחזור אליך ביום העסקים הבא."
    ),
    "order_ask_number": "שלח/י לי את מספר ההזמנה:",
    "order_not_found": "לא מצאתי הזמנה עם המספר הזה. בדוק/י ונסה/י שוב.",
    "faq_hours": "שעות פעילות:\nא'-ה': 9:00-17:00\nו': 9:00-13:00\nשבת: סגור",
    "faq_returns": "ניתן להחזיר מוצרים עד 14 יום מתאריך הרכישה.\nיש להציג חשבונית.",
    "faq_shipping": "אנחנו שולחים לכל הארץ.\nמשלוח רגיל: 5-7 ימי עסקים.\nמשלוח מהיר: 1-2 ימי עסקים.",
    "faq_payment": (
        "אמצעי תשלום:\n"
        "- כרטיס אשראי (ויזה, מאסטרקארד, אמקס)\n"
        "- ביט / פייבוקס\n"
        "- העברה בנקאית\n"
        "- תשלומים (עד 12 ת\"ש ללא ריבית)"
    ),
}


# =============================================================================
# WhatsApp API Helpers
# =============================================================================

def send_text_message(to: str, text: str) -> dict:
    """Send a text message to a WhatsApp number."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    return _send_message(payload)


def send_interactive_buttons(to: str, body_text: str, buttons: list[dict]) -> dict:
    """Send interactive buttons.

    buttons: [{"id": "btn_id", "title": "Button Label"}, ...]
    Max 3 buttons.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons[:3]
                ]
            },
        },
    }
    return _send_message(payload)


def send_interactive_list(
    to: str, body_text: str, button_label: str, sections: list[dict]
) -> dict:
    """Send an interactive list.

    sections: [{"title": "Section", "rows": [{"id": "row_id", "title": "...", "description": "..."}]}]
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {"button": button_label, "sections": sections},
        },
    }
    return _send_message(payload)


def mark_as_read(message_id: str) -> dict:
    """Mark a message as read (blue checkmarks)."""
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    return _send_message(payload)


def _send_message(payload: dict) -> dict:
    """Send a message via the WhatsApp Cloud API."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(GRAPH_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Failed to send message: %s", e)
        return {"error": str(e)}


# =============================================================================
# Session Management
# =============================================================================

def get_session(phone: str) -> dict:
    """Get or create a session for a phone number."""
    if phone not in sessions:
        sessions[phone] = {
            "state": "main_menu",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "fallback_count": 0,
            "data": {},
        }
    sessions[phone]["last_activity"] = datetime.now(timezone.utc).isoformat()
    return sessions[phone]


def set_state(phone: str, state: str):
    """Update session state."""
    session = get_session(phone)
    session["state"] = state
    session["fallback_count"] = 0  # Reset on valid state change


# =============================================================================
# Message Handlers
# =============================================================================

def handle_text_message(phone: str, text: str, message_id: str):
    """Handle an incoming text message."""
    # Mark as read
    mark_as_read(message_id)

    session = get_session(phone)
    state = session["state"]
    text_clean = text.strip()

    # Global commands (work from any state)
    if text_clean in ("תפריט", "menu", "start", "/start"):
        show_main_menu(phone)
        return

    if text_clean in ("עזרה", "help", "/help"):
        send_text_message(phone, "הקלד/י 'תפריט' לאפשרויות, או 'נציג' לשיחה עם אדם.")
        return

    if text_clean in ("נציג", "אדם", "agent"):
        send_text_message(phone, RESPONSES["human_handoff"])
        set_state(phone, "human_handoff")
        return

    # State-specific handling
    if state == "main_menu":
        show_main_menu(phone)

    elif state == "waiting_order_number":
        handle_order_lookup(phone, text_clean)

    elif state == "human_handoff":
        # User is waiting for human, acknowledge
        send_text_message(phone, "ההודעה שלך נשמרה. נציג יחזור אליך בהקדם.")

    else:
        # Fallback
        session["fallback_count"] += 1
        if session["fallback_count"] >= 3:
            send_text_message(
                phone,
                "נראה שאני מתקשה להבין. הקלד/י 'תפריט' לאפשרויות או 'נציג' לשיחה עם אדם."
            )
            session["fallback_count"] = 0
        else:
            send_text_message(phone, RESPONSES["not_understood"])


def handle_button_reply(phone: str, button_id: str, message_id: str):
    """Handle an interactive button reply."""
    mark_as_read(message_id)

    if button_id == "check_order":
        send_text_message(phone, RESPONSES["order_ask_number"])
        set_state(phone, "waiting_order_number")

    elif button_id == "support":
        send_text_message(phone, RESPONSES["human_handoff"])
        set_state(phone, "human_handoff")

    elif button_id == "hours":
        send_text_message(phone, RESPONSES["faq_hours"])
        show_main_menu(phone)

    elif button_id == "faq":
        show_faq_list(phone)

    elif button_id == "back_menu":
        show_main_menu(phone)

    else:
        send_text_message(phone, RESPONSES["not_understood"])


def handle_list_reply(phone: str, list_id: str, message_id: str):
    """Handle an interactive list selection."""
    mark_as_read(message_id)

    faq_responses = {
        "faq_hours": RESPONSES["faq_hours"],
        "faq_returns": RESPONSES["faq_returns"],
        "faq_shipping": RESPONSES["faq_shipping"],
        "faq_payment": RESPONSES["faq_payment"],
    }

    if list_id in faq_responses:
        send_text_message(phone, faq_responses[list_id])
        # Offer to go back to menu
        send_interactive_buttons(
            phone,
            "צריך עוד משהו?",
            [
                {"id": "back_menu", "title": "חזרה לתפריט"},
                {"id": "support", "title": "דבר/י עם נציג"},
            ],
        )
    else:
        send_text_message(phone, RESPONSES["not_understood"])


# =============================================================================
# Flow Functions
# =============================================================================

def show_main_menu(phone: str):
    """Show the main menu with interactive buttons."""
    set_state(phone, "main_menu")
    send_interactive_buttons(
        phone,
        RESPONSES["welcome"],
        [
            {"id": "check_order", "title": "בדיקת הזמנה"},
            {"id": "faq", "title": "שאלות נפוצות"},
            {"id": "support", "title": "דבר/י עם נציג"},
        ],
    )


def show_faq_list(phone: str):
    """Show FAQ options as an interactive list."""
    send_interactive_list(
        phone,
        "בחר/י את הנושא שמעניין אותך:",
        "לרשימת הנושאים",
        [
            {
                "title": "שאלות נפוצות",
                "rows": [
                    {"id": "faq_hours", "title": "שעות פעילות", "description": "מתי אנחנו פתוחים"},
                    {"id": "faq_returns", "title": "מדיניות החזרות", "description": "איך מחזירים מוצר"},
                    {"id": "faq_shipping", "title": "משלוחים", "description": "אזורי משלוח וזמנים"},
                    {"id": "faq_payment", "title": "אמצעי תשלום", "description": "דרכי תשלום מקובלות"},
                ],
            }
        ],
    )


def handle_order_lookup(phone: str, order_number: str):
    """Look up an order by number."""
    # Validate order number format
    if not order_number.isdigit() or len(order_number) < 4:
        send_text_message(phone, "מספר הזמנה לא תקין. שלח/י את המספר שוב:")
        return

    # TODO: Replace with actual order lookup
    # order = lookup_order(order_number)
    # if order:
    #     send_text_message(phone, f"הזמנה {order_number}: {order['status']}")
    # else:
    #     send_text_message(phone, RESPONSES["order_not_found"])

    # Demo response
    send_text_message(
        phone,
        f"הזמנה מספר {order_number}:\n"
        f"סטטוס: בדרך אליך\n"
        f"צפי הגעה: מחר, 14:00-18:00"
    )
    set_state(phone, "main_menu")


# =============================================================================
# Webhook Endpoints
# =============================================================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Handle webhook verification from Meta."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge, 200

    logger.warning("Webhook verification failed")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Process incoming webhook events from WhatsApp."""
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = request.get_data()

    if APP_SECRET:
        expected = "sha256=" + hmac.new(
            APP_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            logger.warning("Invalid webhook signature")
            return "Invalid signature", 403

    data = request.get_json()

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # Handle incoming messages
                for message in value.get("messages", []):
                    phone = message["from"]
                    msg_id = message["id"]
                    msg_type = message["type"]

                    logger.info("Received %s from %s", msg_type, phone)

                    if msg_type == "text":
                        handle_text_message(phone, message["text"]["body"], msg_id)

                    elif msg_type == "interactive":
                        interactive = message["interactive"]
                        if "button_reply" in interactive:
                            handle_button_reply(
                                phone, interactive["button_reply"]["id"], msg_id
                            )
                        elif "list_reply" in interactive:
                            handle_list_reply(
                                phone, interactive["list_reply"]["id"], msg_id
                            )

                    elif msg_type in ("image", "document", "audio", "video"):
                        send_text_message(
                            phone,
                            "קיבלתי את הקובץ. כרגע אני יודע/ת לטפל רק בהודעות טקסט."
                        )

                # Handle status updates (sent, delivered, read)
                for status in value.get("statuses", []):
                    logger.debug(
                        "Message %s status: %s",
                        status.get("id"),
                        status.get("status"),
                    )

    except Exception:
        logger.exception("Error processing webhook")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "whatsapp-bot"}), 200


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    if not VERIFY_TOKEN:
        logger.warning("WHATSAPP_VERIFY_TOKEN not set")
    if not ACCESS_TOKEN:
        logger.warning("WHATSAPP_ACCESS_TOKEN not set")

    app.run(host="0.0.0.0", port=8080, debug=True)
