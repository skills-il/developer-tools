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

// bot.catch() only runs under long polling ("Calling bot.catch when using other
// means of running your bot (or webhooks) has no effect"). On a webhook an uncaught
// error reaches webhookCallback, Telegram gets a non-2XX and retries. Register the
// handlers inside an errorBoundary instead.
const safe = bot.errorBoundary(async (err) => {
  console.error("Bot error:", err.error);
  if (err.error instanceof GrammyError) {
    console.error("Telegram API error:", err.error.description);
  }
  // Tell the user in Hebrew; ignore a failure here so the boundary itself never throws
  await err.ctx.reply("אירעה תקלה זמנית. נסו שוב בעוד רגע.").catch(() => {});
});

safe.command("start", async (ctx) => {
  await ctx.reply(
    "שלום! אני בוט שירות לקוחות.\n\n" +
    "שלחו לי הודעה ואחזור אליכם בהקדם.\n" +
    "לתפריט, שלחו /menu",
    { parse_mode: "HTML" }
  );
});

safe.command("menu", async (ctx) => {
  await ctx.reply(
    "<b>תפריט ראשי</b>\n\n" +
    "/status - בדיקת סטטוס הזמנה\n" +
    "/contact - פרטי התקשרות\n" +
    "/hours - שעות פעילות",
    { parse_mode: "HTML" }
  );
});

safe.command("hours", async (ctx) => {
  await ctx.reply(
    "<b>שעות פעילות</b>\n\n" +
    "ראשון-חמישי: 09:00-18:00\n" +
    "שישי: 09:00-14:00\n" +
    "שבת: סגור",
    { parse_mode: "HTML" }
  );
});

safe.on("message:text", async (ctx) => {
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

export default webhookCallback(bot, "std/http", {
  secretToken: process.env.WEBHOOK_SECRET_TOKEN, // without it grammY accepts any POST
});
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
    # Persist BEFORE delivering: the charge id is what refundStarPayment and
    # editUserStarSubscription need. save_payment is your own DB call
    # (INSERT ... ON CONFLICT DO NOTHING) returning True only for a new row,
    # so a redelivered update delivers nothing twice.
    is_new = await save_payment(
        user_id=update.effective_user.id,
        charge_id=payment.telegram_payment_charge_id,
        payload=payment.invoice_payload,
    )
    if not is_new:
        return
    await update.message.reply_text("תודה על הרכישה! המנוי הופעל")

application.add_handler(CommandHandler("buy", buy))
application.add_handler(PreCheckoutQueryHandler(precheckout))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
```

**Critical payment rules:**
- `pre_checkout_query` MUST be answered within 10 seconds or the payment fails.
- Telegram Stars (XTR) amounts are in whole stars (no decimals).
- For physical goods or non-digital services, you need a third-party payment provider (Stripe, etc.) configured via BotFather under `/mybots > Payments`.
- Refunds are done via `refundStarPayment(user_id, telegram_payment_charge_id)`, which is why the handler stores the charge id.


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
  // Persist before delivering, unique on telegram_payment_charge_id (refunds need it).
  // savePayment is your own DB call (INSERT ... ON CONFLICT DO NOTHING) and returns
  // true only when the row is new, so a redelivered update delivers nothing twice.
  const isNew = await savePayment({
    userId: ctx.from.id,
    chargeId: payment.telegram_payment_charge_id,
    payload: payment.invoice_payload,
    expiresAt: payment.subscription_expiration_date, // subscriptions only
  });
  if (!isNew) return;

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

## Bilingual command menus (setMyCommands)

Set the English list without `language_code` first: it is the fallback for every user "for whose language there are no dedicated commands". Then layer the Hebrew list and any scoped menus on top. The resolution order is documented under "Determining list of commands", and "the first list of commands which is set is returned". Each tier is tried first with the user's `language_code`, then without. In the chat with the bot: `chat`, `all_private_chats`, `default`. In groups: `chat_member`, `chat_administrators` (admins only), `chat`, `all_chat_administrators` (admins only), `all_group_chats`, `default`. Run once at deploy time, not on every update.

```typescript
// grammY (type-checked against grammy 1.46.0)
await bot.api.setMyCommands([
  { command: "start", description: "Start" },
  { command: "help", description: "Help" },
]);
await bot.api.setMyCommands([
  { command: "start", description: "התחלה" },
  { command: "help", description: "עזרה" },
], { language_code: "he" });
// Group admins: lists do NOT merge (the first matching list wins), so repeat the
// base commands, once per language
await bot.api.setMyCommands([
  { command: "start", description: "התחלה" },
  { command: "help", description: "עזרה" },
  { command: "stats", description: "סטטיסטיקה" },
], { scope: { type: "all_chat_administrators" }, language_code: "he" });
await bot.api.setMyCommands([
  { command: "start", description: "Start" },
  { command: "help", description: "Help" },
  { command: "stats", description: "Stats" },
], { scope: { type: "all_chat_administrators" } });

// Telegraf: same arguments on bot.telegram
await bot.telegram.setMyCommands([{ command: "help", description: "עזרה" }], { language_code: "he" });
```

```python
# python-telegram-bot 22.8: set_my_commands(commands, scope=None, language_code=None)
from telegram import BotCommand, BotCommandScopeAllChatAdministrators

await application.bot.set_my_commands([BotCommand("start", "Start"), BotCommand("help", "Help")])
await application.bot.set_my_commands(
    [BotCommand("start", "התחלה"), BotCommand("help", "עזרה")], language_code="he"
)
await application.bot.set_my_commands(
    [BotCommand("start", "התחלה"), BotCommand("help", "עזרה"), BotCommand("stats", "סטטיסטיקה")],
    scope=BotCommandScopeAllChatAdministrators(),
    language_code="he",
)
```

Command names themselves stay Latin (`a-z`, `0-9`, `_`); only the description is Hebrew. A Hebrew-word alias such as typing "עזרה" is a text handler, see "Hebrew Command Aliases" in SKILL.md.

## Scheduling in Asia/Jerusalem

```python
# python-telegram-bot: needs pip install "python-telegram-bot[job-queue]"
from zoneinfo import ZoneInfo
from datetime import time

application.job_queue.run_daily(
    send_morning_digest,
    time=time(9, 0, tzinfo=ZoneInfo("Asia/Jerusalem")),
    name="morning_digest",
)
```

```typescript
// grammY / Telegraf with node-cron (croner takes the same timezone option)
import cron from "node-cron";

cron.schedule("0 9 * * *", sendMorningDigest, {
  timezone: "Asia/Jerusalem",
});
```
