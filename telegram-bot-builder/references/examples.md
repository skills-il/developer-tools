# Telegram Bot Examples

Full working code examples for grammY and python-telegram-bot, covering Hebrew menus, Vercel webhook deployment, and multi-step conversations.


### Example 1: Hebrew Menu Bot with Inline Keyboards

A simple restaurant menu bot that displays categories and items in Hebrew:

```typescript
import { Bot, InlineKeyboard } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

const menu = {
  starters: {
    label: "מנות ראשונות",
    items: [
      { name: "חומוס", price: 32 },
      { name: "סלט ירוק", price: 28 },
      { name: "מרק יום", price: 35 },
    ],
  },
  mains: {
    label: "מנות עיקריות",
    items: [
      { name: "שניצל", price: 52 },
      { name: "המבורגר", price: 58 },
      { name: "פסטה", price: 48 },
    ],
  },
};

bot.command("start", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .text(menu.starters.label, "cat:starters")
    .text(menu.mains.label, "cat:mains");

  await ctx.reply("ברוכים הבאים! בחרו קטגוריה:", { reply_markup: keyboard });
});

bot.callbackQuery(/^cat:(.+)$/, async (ctx) => {
  const category = ctx.match[1] as keyof typeof menu;
  const cat = menu[category];
  if (!cat) return ctx.answerCallbackQuery("קטגוריה לא נמצאה");

  const keyboard = new InlineKeyboard();
  cat.items.forEach((item) => {
    keyboard.text(`${item.name} - ₪${item.price}`, `item:${category}:${item.name}`).row();
  });
  keyboard.text("חזרה", "back");

  await ctx.answerCallbackQuery();
  await ctx.editMessageText(`${cat.label}:`, { reply_markup: keyboard });
});

bot.callbackQuery("back", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .text(menu.starters.label, "cat:starters")
    .text(menu.mains.label, "cat:mains");

  await ctx.answerCallbackQuery();
  await ctx.editMessageText("בחרו קטגוריה:", { reply_markup: keyboard });
});

bot.catch((err) => console.error(err));
bot.start();
```

### Example 2: Webhook Bot on Vercel with Hebrew Error Messages

A production webhook bot deployed on Vercel that handles errors gracefully with Hebrew messages:

```typescript
// api/webhook.ts (Vercel serverless function)
import { Bot, webhookCallback, GrammyError } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

bot.command("start", async (ctx) => {
  await ctx.reply(
    "שלום! אני בוט שירות לקוחות.\n\n" +
    "שלחו לי הודעה ואחזור אליכם בהקדם.\n" +
    "לתפריט, שלחו /menu",
    { parse_mode: "HTML" }
  );
});

bot.command("menu", async (ctx) => {
  await ctx.reply(
    "<b>תפריט ראשי</b>\n\n" +
    "/status - בדיקת סטטוס הזמנה\n" +
    "/contact - פרטי התקשרות\n" +
    "/hours - שעות פעילות",
    { parse_mode: "HTML" }
  );
});

bot.command("hours", async (ctx) => {
  await ctx.reply(
    "<b>שעות פעילות</b>\n\n" +
    "ראשון-חמישי: 09:00-18:00\n" +
    "שישי: 09:00-14:00\n" +
    "שבת: סגור",
    { parse_mode: "HTML" }
  );
});

bot.on("message:text", async (ctx) => {
  // Forward user messages to admin group
  const adminChatId = process.env.ADMIN_CHAT_ID;
  if (adminChatId) {
    await bot.api.sendMessage(
      adminChatId,
      `הודעה מ-${ctx.from.first_name} (${ctx.from.id}):\n\n${ctx.message.text}`
    );
  }
  await ctx.reply("ההודעה התקבלה! נחזור אליכם בהקדם.");
});

bot.catch((err) => {
  console.error("Bot error:", err.error);
  if (err.error instanceof GrammyError) {
    console.error("Telegram API error:", err.error.description);
  }
});

export default webhookCallback(bot, "std/http");
```

### Example 3: python-telegram-bot with Conversation Flow and Hebrew

A Python bot implementing a multi-step order form:

```python
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")

# Conversation states
CHOOSING_ITEM, CHOOSING_QUANTITY, CONFIRMING = range(3)

ITEMS = {
    "coffee": {"he": "קפה", "price": 15},
    "tea": {"he": "תה", "price": 12},
    "cake": {"he": "עוגה", "price": 25},
}


async def start_order(update: Update, context) -> int:
    keyboard = [
        [InlineKeyboardButton(f"{v['he']} - ₪{v['price']}", callback_data=k)]
        for k, v in ITEMS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("מה תרצו להזמין?", reply_markup=reply_markup)
    return CHOOSING_ITEM


async def item_chosen(update: Update, context) -> int:
    query = update.callback_query
    await query.answer()

    item_key = query.data
    context.user_data["item"] = item_key
    item = ITEMS[item_key]
    await query.edit_message_text(f"בחרתם {item['he']}. כמה יחידות?")
    return CHOOSING_QUANTITY


async def quantity_chosen(update: Update, context) -> int:
    try:
        quantity = int(update.message.text)
        if quantity < 1 or quantity > 10:
            raise ValueError
    except ValueError:
        await update.message.reply_text("אנא הזינו מספר בין 1 ל-10:")
        return CHOOSING_QUANTITY

    context.user_data["quantity"] = quantity
    item_key = context.user_data["item"]
    item = ITEMS[item_key]
    total = item["price"] * quantity

    keyboard = [
        [
            InlineKeyboardButton("אישור", callback_data="confirm"),
            InlineKeyboardButton("ביטול", callback_data="cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"סיכום הזמנה:\n"
        f"פריט: {item['he']}\n"
        f"כמות: {quantity}\n"
        f"סה\"כ: ₪{total}\n\n"
        f"לאשר?",
        reply_markup=reply_markup,
    )
    return CONFIRMING


async def confirm_order(update: Update, context) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        await query.edit_message_text("ההזמנה אושרה! תודה רבה 🎉")
    else:
        await query.edit_message_text("ההזמנה בוטלה.")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context) -> int:
    await update.message.reply_text("ההזמנה בוטלה.")
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", start_order)],
        states={
            CHOOSING_ITEM: [CallbackQueryHandler(item_chosen)],
            CHOOSING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_chosen)],
            CONFIRMING: [CallbackQueryHandler(confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
```
