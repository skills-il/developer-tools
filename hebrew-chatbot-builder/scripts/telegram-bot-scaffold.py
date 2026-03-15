"""
Telegram Bot Scaffold with Hebrew Support

A starter Telegram bot with:
- Hebrew command menus and inline keyboards
- Conversation state management
- RTL text support
- FAQ system
- Human agent handoff
- Bilingual support (Hebrew/English toggle)

Requirements:
  pip install python-telegram-bot>=20.0

Environment Variables:
  TELEGRAM_BOT_TOKEN - Bot token from @BotFather

Usage:
  export TELEGRAM_BOT_TOKEN=your_bot_token
  python telegram-bot-scaffold.py
"""

import logging
import os
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telegram-bot")


# =============================================================================
# Conversation States
# =============================================================================

class State(Enum):
    MAIN_MENU = auto()
    WAITING_ORDER_NUMBER = auto()
    WAITING_FEEDBACK = auto()
    LANGUAGE_SELECT = auto()
    HUMAN_HANDOFF = auto()


# =============================================================================
# Hebrew Text Constants
# =============================================================================

TEXTS = {
    "he": {
        "welcome": (
            "שלום! אני הבוט של [שם העסק].\n\n"
            "איך אפשר לעזור לך היום?"
        ),
        "help": (
            "הנה מה שאני יודע/ת לעשות:\n\n"
            "/start - התחלת שיחה חדשה\n"
            "/menu - תפריט ראשי\n"
            "/order - בדיקת סטטוס הזמנה\n"
            "/faq - שאלות נפוצות\n"
            "/language - שינוי שפה\n"
            "/help - הצגת עזרה"
        ),
        "main_menu": "בחר/י אחת מהאפשרויות:",
        "btn_new_order": "הזמנה חדשה",
        "btn_check_status": "בדיקת סטטוס",
        "btn_faq": "שאלות נפוצות",
        "btn_contact": "דבר/י עם נציג",
        "btn_back": "חזרה לתפריט",
        "order_ask": "שלח/י לי את מספר ההזמנה:",
        "order_invalid": "מספר הזמנה לא תקין. צריך להכיל לפחות 4 ספרות. נסה/י שוב:",
        "order_not_found": "לא מצאתי הזמנה עם המספר הזה. בדוק/י ונסה/י שוב.",
        "not_understood": "לא הצלחתי להבין. הקלד/י /menu לתפריט.",
        "goodbye": "תודה ויום טוב!",
        "human_handoff": (
            "מעביר/ה אותך לנציג אנושי.\n"
            "שעות פעילות: א'-ה' 9:00-17:00\n\n"
            "תאר/י בקצרה את הנושא שלך:"
        ),
        "human_ack": "ההודעה שלך נשמרה. נציג יחזור אליך בהקדם.",
        "faq_title": "שאלות נפוצות:",
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
        "feedback_ask": "נשמח לשמוע מה חשבת! כתוב/י לנו משוב:",
        "feedback_thanks": "תודה על המשוב! זה עוזר לנו להשתפר.",
        "language_prompt": "בחר/י שפה / Choose language:",
        "language_changed": "השפה שונתה לעברית.",
    },
    "en": {
        "welcome": (
            "Hello! I'm the [Business Name] bot.\n\n"
            "How can I help you today?"
        ),
        "help": (
            "Here's what I can do:\n\n"
            "/start - Start a new conversation\n"
            "/menu - Main menu\n"
            "/order - Check order status\n"
            "/faq - Frequently asked questions\n"
            "/language - Change language\n"
            "/help - Show help"
        ),
        "main_menu": "Choose an option:",
        "btn_new_order": "New Order",
        "btn_check_status": "Check Status",
        "btn_faq": "FAQ",
        "btn_contact": "Contact Agent",
        "btn_back": "Back to Menu",
        "order_ask": "Send me your order number:",
        "order_invalid": "Invalid order number. Must be at least 4 digits. Try again:",
        "order_not_found": "Order not found. Please check and try again.",
        "not_understood": "I didn't understand. Type /menu for options.",
        "goodbye": "Thank you and have a great day!",
        "human_handoff": (
            "Transferring you to a human agent.\n"
            "Business hours: Sun-Thu 9:00-17:00\n\n"
            "Please describe your issue briefly:"
        ),
        "human_ack": "Your message has been saved. An agent will get back to you soon.",
        "faq_title": "Frequently Asked Questions:",
        "faq_hours": "Business Hours:\nSun-Thu: 9:00-17:00\nFri: 9:00-13:00\nSat: Closed",
        "faq_returns": "Products can be returned within 14 days of purchase.\nReceipt required.",
        "faq_shipping": "We ship nationwide.\nStandard: 5-7 business days.\nExpress: 1-2 business days.",
        "faq_payment": (
            "Payment methods:\n"
            "- Credit card (Visa, Mastercard, Amex)\n"
            "- Bit / PayBox\n"
            "- Bank transfer\n"
            "- Installments (up to 12, interest-free)"
        ),
        "feedback_ask": "We'd love to hear your feedback! Write us a note:",
        "feedback_thanks": "Thank you for your feedback! It helps us improve.",
        "language_prompt": "Choose language / בחר/י שפה:",
        "language_changed": "Language changed to English.",
    },
}


def get_text(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    """Get localized text based on user's language preference."""
    lang = context.user_data.get("language", "he")
    return TEXTS.get(lang, TEXTS["he"]).get(key, key)


# =============================================================================
# Keyboard Builders
# =============================================================================

def build_main_menu_keyboard(lang: str = "he") -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    t = TEXTS.get(lang, TEXTS["he"])
    keyboard = [
        [
            InlineKeyboardButton(t["btn_new_order"], callback_data="new_order"),
            InlineKeyboardButton(t["btn_check_status"], callback_data="check_status"),
        ],
        [
            InlineKeyboardButton(t["btn_faq"], callback_data="faq"),
            InlineKeyboardButton(t["btn_contact"], callback_data="human_agent"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_faq_keyboard(lang: str = "he") -> InlineKeyboardMarkup:
    """Build the FAQ inline keyboard."""
    t = TEXTS.get(lang, TEXTS["he"])

    if lang == "he":
        rows = [
            [InlineKeyboardButton("שעות פעילות", callback_data="faq_hours")],
            [InlineKeyboardButton("מדיניות החזרות", callback_data="faq_returns")],
            [InlineKeyboardButton("משלוחים", callback_data="faq_shipping")],
            [InlineKeyboardButton("אמצעי תשלום", callback_data="faq_payment")],
            [InlineKeyboardButton(t["btn_back"], callback_data="back_menu")],
        ]
    else:
        rows = [
            [InlineKeyboardButton("Business Hours", callback_data="faq_hours")],
            [InlineKeyboardButton("Return Policy", callback_data="faq_returns")],
            [InlineKeyboardButton("Shipping", callback_data="faq_shipping")],
            [InlineKeyboardButton("Payment Methods", callback_data="faq_payment")],
            [InlineKeyboardButton(t["btn_back"], callback_data="back_menu")],
        ]

    return InlineKeyboardMarkup(rows)


def build_back_keyboard(lang: str = "he") -> InlineKeyboardMarkup:
    """Build a simple back-to-menu keyboard."""
    t = TEXTS.get(lang, TEXTS["he"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["btn_back"], callback_data="back_menu")]
    ])


def build_language_keyboard() -> InlineKeyboardMarkup:
    """Build language selection keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("עברית", callback_data="lang_he"),
            InlineKeyboardButton("English", callback_data="lang_en"),
        ]
    ])


# =============================================================================
# Command Handlers
# =============================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    # Default to Hebrew
    if "language" not in context.user_data:
        context.user_data["language"] = "he"

    lang = context.user_data["language"]
    await update.message.reply_text(
        get_text(context, "welcome"),
        reply_markup=build_main_menu_keyboard(lang),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(get_text(context, "help"))


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command."""
    lang = context.user_data.get("language", "he")
    await update.message.reply_text(
        get_text(context, "main_menu"),
        reply_markup=build_main_menu_keyboard(lang),
    )


async def cmd_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order command."""
    context.user_data["state"] = State.WAITING_ORDER_NUMBER.value
    await update.message.reply_text(get_text(context, "order_ask"))


async def cmd_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /faq command."""
    lang = context.user_data.get("language", "he")
    await update.message.reply_text(
        get_text(context, "faq_title"),
        reply_markup=build_faq_keyboard(lang),
    )


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command."""
    await update.message.reply_text(
        TEXTS["he"]["language_prompt"],
        reply_markup=build_language_keyboard(),
    )


# =============================================================================
# Callback Query Handler (Inline Keyboard Buttons)
# =============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("language", "he")
    data = query.data

    # Language selection
    if data == "lang_he":
        context.user_data["language"] = "he"
        await query.edit_message_text(
            TEXTS["he"]["language_changed"],
            reply_markup=build_main_menu_keyboard("he"),
        )
        return

    if data == "lang_en":
        context.user_data["language"] = "en"
        await query.edit_message_text(
            TEXTS["en"]["language_changed"],
            reply_markup=build_main_menu_keyboard("en"),
        )
        return

    # Main menu actions
    if data == "back_menu":
        await query.edit_message_text(
            get_text(context, "main_menu"),
            reply_markup=build_main_menu_keyboard(lang),
        )
        return

    if data == "new_order":
        # TODO: Implement order creation flow
        await query.edit_message_text(
            get_text(context, "order_ask") if lang == "he"
            else "What would you like to order?",
            reply_markup=build_back_keyboard(lang),
        )
        return

    if data == "check_status":
        context.user_data["state"] = State.WAITING_ORDER_NUMBER.value
        await query.edit_message_text(
            get_text(context, "order_ask"),
            reply_markup=build_back_keyboard(lang),
        )
        return

    if data == "faq":
        await query.edit_message_text(
            get_text(context, "faq_title"),
            reply_markup=build_faq_keyboard(lang),
        )
        return

    if data == "human_agent":
        context.user_data["state"] = State.HUMAN_HANDOFF.value
        await query.edit_message_text(get_text(context, "human_handoff"))
        return

    # FAQ answers
    faq_keys = ["faq_hours", "faq_returns", "faq_shipping", "faq_payment"]
    if data in faq_keys:
        await query.edit_message_text(
            get_text(context, data),
            reply_markup=build_back_keyboard(lang),
        )
        return


# =============================================================================
# Text Message Handler
# =============================================================================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text messages based on conversation state."""
    text = update.message.text.strip()
    state = context.user_data.get("state")
    lang = context.user_data.get("language", "he")

    # Waiting for order number
    if state == State.WAITING_ORDER_NUMBER.value:
        if text.isdigit() and len(text) >= 4:
            # TODO: Replace with actual order lookup
            order_info = (
                f"הזמנה מספר {text}:\n"
                f"סטטוס: בדרך אליך\n"
                f"צפי הגעה: מחר, 14:00-18:00"
            ) if lang == "he" else (
                f"Order #{text}:\n"
                f"Status: On the way\n"
                f"ETA: Tomorrow, 14:00-18:00"
            )
            await update.message.reply_text(
                order_info,
                reply_markup=build_back_keyboard(lang),
            )
            context.user_data["state"] = None
        else:
            await update.message.reply_text(get_text(context, "order_invalid"))
        return

    # Human handoff: save message for agent
    if state == State.HUMAN_HANDOFF.value:
        # TODO: Forward to support system
        logger.info(
            "Support ticket from %s: %s",
            update.effective_user.id,
            text,
        )
        await update.message.reply_text(
            get_text(context, "human_ack"),
            reply_markup=build_back_keyboard(lang),
        )
        context.user_data["state"] = None
        return

    # Waiting for feedback
    if state == State.WAITING_FEEDBACK.value:
        logger.info("Feedback from %s: %s", update.effective_user.id, text)
        await update.message.reply_text(
            get_text(context, "feedback_thanks"),
            reply_markup=build_back_keyboard(lang),
        )
        context.user_data["state"] = None
        return

    # Default: not understood
    await update.message.reply_text(get_text(context, "not_understood"))


# =============================================================================
# Error Handler
# =============================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error("Exception while handling update:", exc_info=context.error)


# =============================================================================
# Main
# =============================================================================

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return

    # Build application
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("order", cmd_order))
    app.add_handler(CommandHandler("faq", cmd_faq))
    app.add_handler(CommandHandler("language", cmd_language))

    # Callback query handler (inline keyboard buttons)
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Text message handler (must be added last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Error handler
    app.add_error_handler(error_handler)

    # Start polling
    logger.info("Bot started. Polling for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
