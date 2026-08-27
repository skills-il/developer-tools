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

### Example 4: Telegram Stars Invoice (python-telegram-bot)

**python-telegram-bot:**

```python
from telegram import LabeledPrice

async def buy(update: Update, context) -> None:
    await update.message.reply_invoice(
        title="מנוי פרימיום",
        description="גישה לכל התכונות למשך חודש",
        payload="premium_monthly",
        currency="XTR",
        prices=[LabeledPrice("מנוי חודשי", 100)],
    )

async def precheckout(update: Update, context) -> None:
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context) -> None:
    payment = update.message.successful_payment
    await update.message.reply_text("תודה על הרכישה! המנוי הופעל")

application.add_handler(CommandHandler("buy", buy))
application.add_handler(PreCheckoutQueryHandler(precheckout))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
```

**Critical payment rules:**
- `pre_checkout_query` MUST be answered within 10 seconds or the payment fails.
- Telegram Stars (XTR) amounts are in whole stars (no decimals).
- For physical goods or non-digital services, you need a third-party payment provider (Stripe, etc.) configured via BotFather under `/mybots > Payments`.
- Refunds are done via `refundStarPayment` API method, not manually.


### Example 5: Israeli phone-number verification via request_contact (grammY)

```typescript
import { Keyboard } from "grammy";

bot.command("verify", async (ctx) => {
  const kb = new Keyboard()
    .requestContact("שתף את מספר הטלפון שלי")
    .resized()
    .oneTime();
  await ctx.reply("כדי להמשיך, שתף את מספר הטלפון שלך:", { reply_markup: kb });
});

function normalizeIsraeliPhone(raw: string): string | null {
  // Strip spaces, dashes, parens
  let p = raw.replace(/[\s\-()]/g, "");
  // +972XXXXXXXXX, 972XXXXXXXXX, 0XXXXXXXXX -> +972XXXXXXXXX
  if (p.startsWith("+972")) return p;
  if (p.startsWith("972")) return "+" + p;
  if (p.startsWith("0")) return "+972" + p.slice(1);
  return null;
}

bot.on("message:contact", async (ctx) => {
  const contact = ctx.message.contact;
  // Security: ensure the contact belongs to the sender, not someone they pasted
  if (contact.user_id !== ctx.from.id) {
    return ctx.reply("אנא שתף את המספר שלך, לא של אדם אחר.");
  }
  const phone = normalizeIsraeliPhone(contact.phone_number);
  if (!phone) {
    return ctx.reply("המספר שהתקבל לא נראה כמספר ישראלי תקין.");
  }
  await ctx.reply(`תודה! המספר שלך נשמר: ${phone}`);
});
```


### Example 6: Telegram Stars invoice, successful_payment and pre_checkout (grammY)

```typescript
bot.command("buy", async (ctx) => {
  await ctx.replyWithInvoice(
    "מנוי פרימיום",              // title
    "גישה לכל התכונות למשך חודש",  // description
    "premium_monthly",            // payload (your internal ID)
    "XTR",                        // currency (XTR = Telegram Stars)
    [{ label: "מנוי חודשי", amount: 100 }], // prices (100 Stars)
  );
});

// Handle successful payment
bot.on("message:successful_payment", async (ctx) => {
  const payment = ctx.message.successful_payment;
  console.log(`Payment received: ${payment.total_amount} ${payment.currency}`);
  console.log(`Payload: ${payment.invoice_payload}`);

  await ctx.reply("תודה על הרכישה! המנוי הופעל");
});

// Handle pre-checkout query (MUST answer within 10 seconds)
bot.on("pre_checkout_query", async (ctx) => {
  // Validate the order, check stock, etc.
  await ctx.answerPreCheckoutQuery(true);
  // Or reject: await ctx.answerPreCheckoutQuery(false, "מוצר אזל מהמלאי");
});
```



### Example 7: Stars subscription via createInvoiceLink (grammY)

```typescript
const link = await bot.api.createInvoiceLink(
  "מנוי פרימיום",
  "גישה לכל התכונות, מתחדש מדי חודש",
  "premium_sub_v1",
  "",                                       // provider_token: empty for Stars
  "XTR",
  [{ label: "מנוי חודשי", amount: 100 }],   // exactly one item
  { subscription_period: 2592000 },          // 30 days, the only supported value
);
await ctx.reply(`להצטרפות: ${link}`);
```



### Example 8: sendGift (grammY, positional signature)

```typescript
// grammY's sendGift is positional: (user_id, gift_id, other?)
await bot.api.sendGift(
  ctx.from.id,
  "<one of the IDs returned by getAvailableGifts>",
  { text: "תודה שאתם איתנו!" }, // optional message attached to the gift
);
```



## Inline keyboard, Telegraf and python-telegram-bot

**Telegraf:**

```typescript
import { Markup } from "telegraf";

bot.command("menu", (ctx) => {
  ctx.reply("בחר אפשרות:", Markup.inlineKeyboard([
    [Markup.button.callback("אפשרות א׳", "option_a"),
     Markup.button.callback("אפשרות ב׳", "option_b")],
    [Markup.button.callback("ביטול", "cancel")]
  ]));
});

bot.action("option_a", (ctx) => {
  ctx.answerCbQuery("בחרת אפשרות א׳!");
  ctx.editMessageText("בחרת: אפשרות א׳");
});
```

**python-telegram-bot:**

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def menu(update: Update, context) -> None:
    keyboard = [
        [
            InlineKeyboardButton("אפשרות א׳", callback_data="option_a"),
            InlineKeyboardButton("אפשרות ב׳", callback_data="option_b"),
        ],
        [InlineKeyboardButton("ביטול", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("בחר אפשרות:", reply_markup=reply_markup)


async def button_handler(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "option_a":
        await query.edit_message_text("בחרת: אפשרות א׳")
    elif query.data == "option_b":
        await query.edit_message_text("בחרת: אפשרות ב׳")
    elif query.data == "cancel":
        await query.delete_message()

# Register handler
application.add_handler(CallbackQueryHandler(button_handler))
```


## Bot Business: capturing the connection and replying

```typescript
// Capture the connection (store business_connection_id per business user)
bot.on("business_connection", async (ctx) => {
  const conn = ctx.businessConnection;
  // Permissions live under conn.rights (BusinessBotRights).
  // There is no top-level conn.can_reply field.
  console.log(`Connected to business user ${conn.user.id}, can_reply=${conn.rights?.can_reply}`);
  // Persist conn.id keyed by conn.user.id
});

// Reply to an incoming business message - echo business_connection_id
bot.on("business_message", async (ctx) => {
  await ctx.api.sendMessage(ctx.businessMessage.chat.id, "אני אחזור אליך תוך מספר דקות", {
    business_connection_id: ctx.businessMessage.business_connection_id,
  });
});
```
