---
name: telegram-bot-builder
description: "Build Telegram bots with grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.0 webhooks vs polling, inline keyboards, commands, middleware patterns, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, and Hebrew message handling. Use when building a Telegram bot, setting up webhooks, handling Hebrew/RTL messages in a bot, or integrating Telegram payments. Do NOT use for WhatsApp bots (use israeli-whatsapp-business), voice bots (use hebrew-voice-bot-builder), or general chatbot design patterns (use hebrew-chatbot-builder)."
license: MIT
---

# Telegram Bot Builder

Build production-ready Telegram bots for the Israeli market using grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.0 (April 2026), webhooks vs polling, inline keyboards, Hebrew/RTL text, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, Managed Bots, and serverless deployment.

## Problem

Building Telegram bots for Israeli users involves several challenges that agents consistently get wrong:

1. **Framework choice confusion** - grammY, Telegraf, and python-telegram-bot have different Bot API version support, plugin ecosystems, and deployment models. Agents often mix their APIs or suggest deprecated patterns.
2. **Webhook vs polling misconfiguration** - Agents default to polling (good for development) but fail to set up webhooks correctly for production, missing port restrictions (443, 80, 88, 8443 only), SSL requirements, and secret token verification.
3. **Hebrew/RTL text corruption** - Bidirectional text mixing Hebrew and English (common in Israeli bots) breaks in inline keyboards, callback data, and formatted messages. Agents ignore Unicode control characters and text direction markers.
4. **Payment integration gaps** - Telegram Stars (the in-app currency) has specific invoice creation flows that differ from traditional payment providers. Agents often generate code for deprecated payment APIs.
5. **Mini App data exchange** - The communication protocol between a Telegram Mini App (WebApp) and the bot uses `web_app_data` events, not regular messages. Agents frequently implement this incorrectly.

## Framework Selection

Choose your framework based on your runtime, deployment target, and Bot API version needs:

| Feature | grammY v1.42.0 | Telegraf v4.16.3 | python-telegram-bot v22.7 |
|---------|----------------|-------------------|---------------------------|
| Language | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| Bot API version | Latest (v10.0) | v7.1 | v10.0 |
| Install | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| Plugin ecosystem | Rich (sessions, menus, conversations, i18n) | Moderate (scenes, sessions) | Extensions (JobQueue, persistence) |
| Serverless support | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda adapters | ASGI adapters, manual webhook handlers |
| Middleware model | Composer-based (like Koa) | Composer-based (like Koa) | Handler groups with filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| Webhook mode | `webhookCallback()` adapter | `bot.launch({ webhook })` or `createWebhook()` | `application.run_webhook()` |
| TypeScript types | First-class, auto-generated | Good, manual maintenance | N/A (Python type hints) |
| Recommended for | New projects, serverless, latest API features | Existing Express/Fastify apps | Python shops, data/ML pipelines |

**Decision guide:**
- Need Bot API v10.0 features (Stars subscriptions, Gifts, Bot Business, Mini Apps 2.0, Managed Bots, guest-bot)? Use **grammY** or **python-telegram-bot**.
- Already have an Express/Fastify server? **Telegraf** integrates cleanly.
- Python team or ML/data pipeline? **python-telegram-bot** is the only choice.
- Deploying to Vercel/Cloudflare Workers/Deno? **grammY** has native adapters for all of them.

## Bot Creation with BotFather

Every Telegram bot starts with @BotFather. This is not optional, there is no API-only bot creation.

### Steps

1. Open Telegram, search for `@BotFather`, start a chat
2. Send `/newbot`
3. Provide a display name (e.g., "My Israeli Bot")
4. Provide a username ending in `bot` (e.g., `my_israeli_bot`)
5. BotFather returns a token in the format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### Token Security Rules

- **Never commit tokens to git.** Use environment variables: `BOT_TOKEN` or `TELEGRAM_BOT_TOKEN`.
- Tokens can be revoked via `/revokentoken` in BotFather.
- The token format is `{bot_id}:{secret}`. The bot_id portion (before the colon) is the bot's numeric user ID.
- Store in `.env` file (add to `.gitignore`) or use your platform's secret management.

### BotFather Configuration Commands

```
/setdescription - Bot bio shown before user starts it
/setabouttext - Shown in bot profile
/setuserpic - Bot avatar
/setcommands - Command menu (critical for UX)
/setprivacy - Group privacy mode (disable to read all group messages)
/setinline - Enable inline mode
/setinlinefeedback - Probability of receiving chosen_inline_result updates
```

## Project Setup

### grammY (TypeScript)

```bash
mkdir my-telegram-bot && cd my-telegram-bot
npm init -y
npm install grammy dotenv
npm install -D typescript @types/node
npx tsc --init
```

**`src/bot.ts`:**

```typescript
import { Bot, Context, session, GrammyError, HttpError } from "grammy";
import "dotenv/config";

const token = process.env.BOT_TOKEN;
if (!token) throw new Error("BOT_TOKEN environment variable is required");

const bot = new Bot(token);

// Command handlers
bot.command("start", async (ctx) => {
  await ctx.reply("!שלום! אני הבוט שלך");
});

bot.command("help", async (ctx) => {
  await ctx.reply(
    "הפקודות הזמינות:\n" +
    "/start - התחלה\n" +
    "/help - עזרה"
  );
});

// Message handler
bot.on("message:text", async (ctx) => {
  await ctx.reply(`קיבלתי: ${ctx.message.text}`);
});

// Error handling (critical - without this, errors crash the bot silently)
bot.catch((err) => {
  const ctx = err.ctx;
  console.error(`Error while handling update ${ctx.update.update_id}:`);
  const e = err.error;
  if (e instanceof GrammyError) {
    console.error("Error in request:", e.description);
  } else if (e instanceof HttpError) {
    console.error("Could not contact Telegram:", e);
  } else {
    console.error("Unknown error:", e);
  }
});

// Start with long polling (development)
bot.start();
console.log("Bot is running...");
```

### Telegraf (TypeScript)

```bash
mkdir my-telegram-bot && cd my-telegram-bot
npm init -y
npm install telegraf dotenv
npm install -D typescript @types/node
npx tsc --init
```

**`src/bot.ts`:**

```typescript
import { Telegraf, Context } from "telegraf";
import "dotenv/config";

const token = process.env.BOT_TOKEN;
if (!token) throw new Error("BOT_TOKEN environment variable is required");

const bot = new Telegraf(token);

bot.start((ctx) => ctx.reply("!שלום! אני הבוט שלך"));

bot.help((ctx) => ctx.reply(
  "הפקודות הזמינות:\n" +
  "/start - התחלה\n" +
  "/help - עזרה"
));

bot.on("text", (ctx) => ctx.reply(`קיבלתי: ${ctx.message.text}`));

// Graceful shutdown
process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));

// Start with long polling (development)
bot.launch();
console.log("Bot is running...");
```

### python-telegram-bot (Python)

```bash
mkdir my-telegram-bot && cd my-telegram-bot
python -m venv venv
source venv/bin/activate
pip install python-telegram-bot python-dotenv
```

**`bot.py`:**

```python
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")


async def start(update: Update, context) -> None:
    await update.message.reply_text("!שלום! אני הבוט שלך")


async def help_command(update: Update, context) -> None:
    await update.message.reply_text(
        "הפקודות הזמינות:\n"
        "/start - התחלה\n"
        "/help - עזרה"
    )


async def echo(update: Update, context) -> None:
    await update.message.reply_text(f"קיבלתי: {update.message.text}")


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start with long polling (development)
    application.run_polling()


if __name__ == "__main__":
    main()
```

## Core Patterns

### Inline Keyboards

Inline keyboards attach buttons directly to messages. They are the primary interactive UI element in Telegram bots.

**grammY:**

```typescript
import { InlineKeyboard } from "grammy";

bot.command("menu", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .text("אפשרות א׳", "option_a")
    .text("אפשרות ב׳", "option_b")
    .row()
    .text("ביטול", "cancel");

  await ctx.reply("בחר אפשרות:", { reply_markup: keyboard });
});

// Handle button presses
bot.callbackQuery("option_a", async (ctx) => {
  await ctx.answerCallbackQuery({ text: "בחרת אפשרות א׳!" });
  await ctx.editMessageText("בחרת: אפשרות א׳");
});

bot.callbackQuery("option_b", async (ctx) => {
  await ctx.answerCallbackQuery({ text: "בחרת אפשרות ב׳!" });
  await ctx.editMessageText("בחרת: אפשרות ב׳");
});

bot.callbackQuery("cancel", async (ctx) => {
  await ctx.answerCallbackQuery();
  await ctx.deleteMessage();
});
```

**Critical: Callback data rules:**
- Maximum 64 bytes (not characters). Hebrew uses 2-3 bytes per character in UTF-8, so you get roughly 21-32 Hebrew characters.
- Use short English identifiers for callback data, display Hebrew in button text.
- Pattern: `button text = Hebrew for user`, `callback data = English identifier for code`.

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

### Middleware Patterns

Middleware runs before handlers and is essential for logging, authentication, rate limiting, and i18n.

**grammY middleware:**

```typescript
// Logging middleware
bot.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`Update ${ctx.update.update_id} processed in ${ms}ms`);
});

// Auth middleware (restrict to specific users)
function adminOnly(ctx: Context, next: () => Promise<void>) {
  const adminIds = [123456789, 987654321]; // Telegram user IDs
  if (ctx.from && adminIds.includes(ctx.from.id)) {
    return next();
  }
  return ctx.reply("אין לך הרשאה לפקודה זו.");
}

bot.command("admin", adminOnly, async (ctx) => {
  await ctx.reply("פאנל ניהול");
});
```

**python-telegram-bot does not use middleware** in the same way. Instead, use handler groups with different priorities:

```python
# Group 0 (default) handlers run first, then group 1, etc.
# Use group -1 for "middleware-like" behavior
async def log_update(update: Update, context) -> None:
    logger.info(f"Update from user {update.effective_user.id}")

application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)
```

### Conversation / Multi-Step Flows

For multi-step flows (registration wizards, order forms), each framework has its own pattern: grammY's `@grammyjs/conversations` plugin (await-style flow), Telegraf's `Scenes.WizardScene`, and python-telegram-bot's `ConversationHandler`. Full working snippets in [references/conversations.md](references/conversations.md).


## Webhook vs Polling

### Polling (Development)

Polling has the bot repeatedly ask Telegram "any new updates?" via `getUpdates`. Simple to set up, no public URL needed.

```
Bot --> Telegram: getUpdates?offset=X
Telegram --> Bot: [update1, update2, ...]
Bot --> Telegram: getUpdates?offset=X+2
```

**When to use:** Local development, testing, simple bots with low traffic.

**All frameworks default to polling** (see project setup above).

### Webhooks (Production)

Webhooks have Telegram push updates to your server. More efficient, lower latency, required for serverless.

```
User sends message --> Telegram --> POST https://your-domain.com/webhook --> Your bot
```

**Requirements:**
- HTTPS with a valid SSL certificate (self-signed works but not recommended)
- Public URL accessible from Telegram's servers
- **Port must be one of: 443, 80, 88, or 8443** (this is a hard Telegram restriction, agents frequently miss this)
- Secret token for verification (recommended, prevents spoofed requests)

**grammY webhook setup (Express):**

```typescript
import express from "express";
import { webhookCallback } from "grammy";

const app = express();
app.use(express.json());

// The webhook path should include a secret or random string
app.use("/webhook/" + process.env.WEBHOOK_SECRET, webhookCallback(bot, "express"));

app.listen(443, () => {
  console.log("Webhook server running on port 443");
});

// Set webhook URL with Telegram
await bot.api.setWebhook(`https://your-domain.com/webhook/${process.env.WEBHOOK_SECRET}`, {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN, // Telegram sends this in X-Telegram-Bot-Api-Secret-Token header
});
```

**Telegraf webhook setup:**

```typescript
// Option 1: Built-in webhook server
bot.launch({
  webhook: {
    domain: "https://your-domain.com",
    port: 443,
    secretToken: process.env.WEBHOOK_SECRET_TOKEN,
  },
});

// Option 2: Express integration
import express from "express";
const app = express();
app.use(bot.webhookCallback("/webhook"));
app.listen(443);
await bot.telegram.setWebhook("https://your-domain.com/webhook", {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});

// Option 3: Lambda/serverless
// Export the handler
export const handler = bot.createWebhook({ domain: "https://your-domain.com" });
```

**python-telegram-bot webhook setup:**

```python
application = ApplicationBuilder().token(TOKEN).build()
# ... add handlers ...

# Option 1: Built-in webhook server
application.run_webhook(
    listen="0.0.0.0",
    port=443,
    url_path="webhook",
    webhook_url="https://your-domain.com/webhook",
    secret_token=os.getenv("WEBHOOK_SECRET_TOKEN"),
)

# Option 2: Custom ASGI/WSGI integration
# Use application.update_queue.put() to feed updates manually
```

### Webhook Verification

Always verify the `X-Telegram-Bot-Api-Secret-Token` header matches your secret token. All three frameworks support this via the `secret_token` parameter in `setWebhook`.

### Switching Between Modes

To remove a webhook (switch back to polling):

```
GET https://api.telegram.org/bot<token>/deleteWebhook
```

Or in code:
```typescript
await bot.api.deleteWebhook(); // grammY
await bot.telegram.deleteWebhook(); // Telegraf
```

## Hebrew Message Handling

### The Bidirectional Text Problem

Hebrew is RTL, but Telegram messages often mix Hebrew with LTR content (English words, URLs, numbers, code). This creates rendering issues:

1. **Mixed-direction inline keyboards** - A button showing "שלח 5 הודעות" may render the number in the wrong position.
2. **Callback data encoding** - Keep callback data in ASCII/English. Hebrew in callback data wastes the 64-byte limit (Hebrew UTF-8 = 2-3 bytes per char).
3. **Markdown/HTML parsing with Hebrew** - Bold/italic markers can break with RTL text reordering.

### Solutions

**Use Unicode directional markers when mixing languages:**

```typescript
const RTL_MARK = "\u200F"; // Right-to-Left Mark
const LTR_MARK = "\u200E"; // Left-to-Right Mark

// Force RTL context for Hebrew text containing numbers
await ctx.reply(`${RTL_MARK}סה"כ: ${LTR_MARK}₪150${RTL_MARK} לתשלום`);
```

**Use HTML parse mode (more predictable than Markdown for RTL):**

```typescript
await ctx.reply(
  `<b>סיכום הזמנה</b>\n` +
  `מוצר: חולצה\n` +
  `מחיר: ₪150\n` +
  `כמות: 3`,
  { parse_mode: "HTML" }
);
```

**Why HTML over Markdown for Hebrew:**
- Markdown's `*bold*` and `_italic_` markers can get confused by RTL reordering
- HTML tags (`<b>`, `<i>`) are unambiguous regardless of text direction
- MarkdownV2 requires escaping many characters that appear in Hebrew text

### Hebrew Command Aliases

Telegram commands must start with `/` and use Latin characters. For Hebrew UX, provide both:

```typescript
// Register Latin commands with BotFather
// But also handle Hebrew text triggers
bot.command("help", handleHelp);
bot.hears("עזרה", handleHelp);
bot.hears("תפריט", handleMenu);

// Or use a regex for flexible matching
bot.hears(/^(help|עזרה)$/i, handleHelp);
```

### Hebrew Keyboard Buttons (ReplyKeyboard)

For non-technical users, reply keyboards with Hebrew buttons are more accessible than slash commands:

```typescript
import { Keyboard } from "grammy";

const hebrewMenu = new Keyboard()
  .text("תפריט ראשי").text("עזרה").row()
  .text("ההזמנות שלי").text("צור קשר")
  .resized()    // Fit to content
  .persistent(); // Keep visible

await ctx.reply("בחר מהתפריט:", { reply_markup: hebrewMenu });
```

### Israeli Phone-Number Contact Discovery

The cleanest way to identify a user by their Israeli phone number is `request_contact` on a reply-keyboard button. The user taps the button, Telegram sends a confirmation sheet, and on confirm the bot gets a `contact` field with the verified `phone_number`. Israeli numbers may arrive with or without the leading `+972`, so always normalize.

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

## Rate Limits & File Size Limits

Telegram enforces hard limits on outgoing traffic. Hitting them returns HTTP 429 with `retry_after`; ignore them and your bot gets throttled or banned.

**Outgoing message rates:**
- **30 messages/second** global, across all chats
- **1 message/second** per individual chat (DM or group)
- **20 messages/minute** per group chat (broadcasts to the same group)

For grammY use [`@grammyjs/transformer-throttler`](https://github.com/grammyjs/transformer-throttler) to queue and respect these limits automatically. For Telegraf and python-telegram-bot, implement a per-chat token bucket or use an external queue (BullMQ, Celery).

**File size limits:**
- **Bot file upload:** 50 MB (default Bot API server)
- **Bot file download:** 20 MB
- **Premium-bot via local Bot API server:** up to **2 GB**

To upload or download files larger than 50 MB, run a self-hosted [Bot API server](https://github.com/tdlib/telegram-bot-api) and point your bot at it via the `apiRoot` (grammY) / `telegram.apiRoot` (Telegraf) / `base_url` (python-telegram-bot) option. Hosting a local Bot API server is also a hard requirement for streaming live audio/video updates and very large media in groups.

## Scheduling Jobs in Asia/Jerusalem

Bots that fire at "9 AM Israel time" must use an explicit Israel timezone, not server-local or UTC. Israel observes DST shifts that don't align with most cloud regions (Frankfurt, us-east-1), so a naive UTC offset will drift twice a year.

**python-telegram-bot (`JobQueue`):**

```python
import pytz
from datetime import time

application.job_queue.run_daily(
    send_morning_digest,
    time=time(9, 0, tzinfo=pytz.timezone("Asia/Jerusalem")),
    name="morning_digest",
)
```

**Node (grammY/Telegraf with `node-cron` or `croner`):**

```typescript
import cron from "node-cron";

cron.schedule("0 9 * * *", sendMorningDigest, {
  timezone: "Asia/Jerusalem",
});
```

Avoid `setInterval` for daily jobs, it drifts by an hour twice a year on the DST boundary.

## Bot Business Mode

Released around Bot API 7.2, **Telegram Business** lets a Telegram Premium subscriber connect a bot to their personal account so the bot can read and reply to direct messages on their behalf. Israeli Premium subscribers can flip this on under Settings > Telegram Business > Chatbots and paste the `@username` of an approved bot.

When the user connects the bot, your bot receives a `business_connection` update with a `business_connection_id`. Every message that arrives in one of the user's connected chats then carries that same `business_connection_id` field, and any outgoing call (`sendMessage`, `editMessageText`, etc.) must echo it back so Telegram routes the reply through the user's account rather than the bot's account.

What the bot can do once connected:
- Read and reply to incoming DMs on behalf of the Telegram Business user.
- Get the list of chats the user is talking with (`getBusinessConnection`, then `getBusinessAccountChats`).
- Send messages, edit, and delete on the user's behalf (subject to per-chat permissions Telegram exposes).

```typescript
// Capture the connection (store business_connection_id per Premium user)
bot.on("business_connection", async (ctx) => {
  const conn = ctx.businessConnection;
  console.log(`Connected to business user ${conn.user.id}, can_reply=${conn.can_reply}`);
  // Persist conn.id keyed by conn.user.id
});

// Reply to an incoming business message - echo business_connection_id
bot.on("business_message", async (ctx) => {
  await ctx.api.sendMessage(ctx.businessMessage.chat.id, "אני אחזור אליך תוך מספר דקות", {
    business_connection_id: ctx.businessMessage.business_connection_id,
  });
});
```

Useful for Israeli small-business owners (אופטיקאים, סטודיות יוגה, סוכני ביטוח) who want auto-replies on their personal Telegram during off-hours without exposing customers to a separate "bot" persona.

Reference: [https://core.telegram.org/bots/business](https://core.telegram.org/bots/business)

## Payments API

Telegram offers three payment paths. Pick by what you sell:

- **Telegram Stars (XTR)** for digital goods, services, and Mini App content. Released ~Bot API 7.4 (2024). No external provider needed. Israeli users see Stars priced in ILS in the purchase sheet (Telegram converts automatically based on the user's App Store / Google Play region), so a 100 Stars invoice surfaces as roughly the local-currency equivalent at purchase time.
- **Stars subscriptions** for recurring access (added later in 2024). Same `XTR` currency, with `subscription_period` set on the invoice; users can cancel from Telegram Settings > Stars.
- **Gifts API** (`sendGift`, `convertGiftToStars`) lets a bot send named gifts to users; recipients can keep the gift on their profile or convert it back to Stars.
- **paid_media** lets you attach a Stars price to photos/videos posted in chats and channels (the receiver pays Stars to unlock).
- **Traditional payment providers** (Stripe LIVE/TEST, etc.) are still supported for physical goods and non-digital services. Configure a provider token via `/mybots > Payments` in BotFather, then pass it as `provider_token` and a fiat currency (`ILS`, `USD`, etc.).

### Creating an Invoice

**grammY:**

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

  await ctx.reply("!תודה על הרכישה! המנוי הופעל");
});

// Handle pre-checkout query (MUST answer within 10 seconds)
bot.on("pre_checkout_query", async (ctx) => {
  // Validate the order, check stock, etc.
  await ctx.answerPreCheckoutQuery(true);
  // Or reject: await ctx.answerPreCheckoutQuery(false, "מוצר אזל מהמלאי");
});
```

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
    await update.message.reply_text("!תודה על הרכישה! המנוי הופעל")

application.add_handler(CommandHandler("buy", buy))
application.add_handler(PreCheckoutQueryHandler(precheckout))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
```

**Critical payment rules:**
- `pre_checkout_query` MUST be answered within 10 seconds or the payment fails.
- Telegram Stars (XTR) amounts are in whole stars (no decimals).
- For physical goods or non-digital services, you need a third-party payment provider (Stripe, etc.) configured via BotFather under `/mybots > Payments`.
- Refunds are done via `refundStarPayment` API method, not manually.

### Stars Subscriptions (Recurring)

Pass `subscription_period` (in seconds, currently a fixed 30-day period) on the invoice to turn a one-time Stars payment into a renewing subscription. Telegram handles the renewal cycle, and your bot receives `successful_payment` updates on each renewal.

```typescript
await ctx.replyWithInvoice(
  "מנוי פרימיום",
  "גישה לכל התכונות, מתחדש מדי חודש",
  "premium_sub_v1",
  "XTR",
  [{ label: "מנוי חודשי", amount: 100 }],
  {
    subscription_period: 30 * 24 * 60 * 60, // 30 days, the only currently supported period
  },
);
```

Users manage and cancel subscriptions from Telegram Settings > Stars > My Subscriptions. Listen for `message:successful_payment` on each renewal to extend access in your DB.

### Gifts API

`sendGift` lets the bot send a named gift sticker to a user (paid in Stars from the bot's balance). The recipient can pin the gift on their profile or `convertGiftToStars` to convert it back into Stars. Useful for loyalty rewards, drawing winners, and giveaways.

```typescript
await bot.api.sendGift({
  user_id: ctx.from.id,
  gift_id: "<one of the IDs returned by getAvailableGifts>",
  text: "תודה שאתם איתנו!", // optional message attached to the gift
});
```

Always call `getAvailableGifts` first to fetch the current catalog and pricing.

### paid_media

Attach a Stars price to a photo or video posted in a chat or channel; the recipient pays Stars to unlock the media. Use `sendPaidMedia` (or the `paid_media` field on `sendMessage`-style methods) with `star_count` set to the price.

## Mini Apps (WebApp)

Mini Apps let you embed full web interfaces inside Telegram. The bot opens a web page, and the page can send data back to the bot.

### Setting Up a Mini App Button

**grammY:**

```typescript
import { InlineKeyboard } from "grammy";

bot.command("app", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .webApp("פתח אפליקציה", "https://your-app.com/mini-app");

  await ctx.reply("לחץ לפתיחת האפליקציה:", { reply_markup: keyboard });
});
```

**Using MenuButton (persistent button next to text input):**

```typescript
await bot.api.setChatMenuButton({
  chat_id: ctx.chat.id,
  menu_button: {
    type: "web_app",
    text: "פתח",
    web_app: { url: "https://your-app.com/mini-app" },
  },
});
```

### Receiving Data from Mini App

When the user interacts with the Mini App and sends data back:

**In the Mini App (browser-side JavaScript):**

```javascript
// Telegram WebApp SDK is injected by Telegram
const tg = window.Telegram.WebApp;

// Send data back to the bot (closes the Mini App)
tg.sendData(JSON.stringify({
  action: "order",
  items: ["item1", "item2"],
  total: 150,
}));

// Or use MainButton for a cleaner UX
tg.MainButton.text = "אישור הזמנה";
tg.MainButton.show();
tg.MainButton.onClick(() => {
  tg.sendData(JSON.stringify({ confirmed: true }));
});
```

**In the bot (receiving the data):**

```typescript
bot.on("message:web_app_data", async (ctx) => {
  const data = JSON.parse(ctx.message.web_app_data.data);
  console.log("Received from Mini App:", data);

  await ctx.reply(`הזמנה התקבלה! סה"כ: ₪${data.total}`);
});
```

### Mini Apps 2.0 Features

Bot API 7.x and 8.x added a set of "Mini Apps 2.0" capabilities exposed through `window.Telegram.WebApp`. All of them require the latest Telegram clients and are no-ops on older ones, so feature-detect before calling.

**Cloud storage** (`window.Telegram.WebApp.CloudStorage`) - per-user key-value storage that survives between sessions and devices. Up to 1024 keys per user, 4 KB per value. No backend needed for lightweight preferences:

```javascript
const tg = window.Telegram.WebApp;
tg.CloudStorage.setItem("last_order_id", "12345");
tg.CloudStorage.getItem("last_order_id", (err, value) => {
  console.log("Restored:", value);
});
```

**Biometric authentication** (`window.Telegram.WebApp.BiometricManager`) - prompt the user for Face ID / Touch ID / fingerprint to gate sensitive actions inside the Mini App. Useful for confirming high-value Stars purchases or releasing saved payment tokens:

```javascript
tg.BiometricManager.init(() => {
  if (tg.BiometricManager.isBiometricAvailable) {
    tg.BiometricManager.authenticate({ reason: "אישור תשלום" }, (success) => {
      if (success) submitOrder();
    });
  }
});
```

**Location service** (`window.Telegram.WebApp.LocationManager`) - request the user's GPS coordinates with explicit permission. Good for "find my nearest branch" flows in Israeli retail bots.

**Fullscreen mode** - `tg.requestFullscreen()` expands the Mini App to fill the device screen on mobile. Pair with `tg.exitFullscreen()` when you're done.

**Home-screen install** - `tg.addToHomeScreen()` lets the user add the Mini App as a launcher icon on Android (currently iOS shows a manual instructions sheet). Works once `tg.checkHomeScreenStatus()` reports the app is eligible.

**Reference:** [https://core.telegram.org/bots/webapps](https://core.telegram.org/bots/webapps)

### Mini App Validation

Always validate the `initData` on your server to ensure the request is genuinely from Telegram:

```typescript
import crypto from "crypto";

function validateInitData(initData: string, botToken: string): boolean {
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  params.delete("hash");

  // Sort params alphabetically
  const dataCheckString = Array.from(params.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${key}=${value}`)
    .join("\n");

  const secretKey = crypto
    .createHmac("sha256", "WebAppData")
    .update(botToken)
    .digest();

  const calculatedHash = crypto
    .createHmac("sha256", secretKey)
    .update(dataCheckString)
    .digest("hex");

  return calculatedHash === hash;
}
```

## Deployment

Three common targets, each with framework-specific gotchas. Full working configs are in [references/deployment.md](references/deployment.md):

- **Vercel Serverless (grammY)** - use `webhookCallback(bot, "std/http")`. 10s timeout on Hobby, 60s on Pro. Stateless, so use external session storage.
- **Cloudflare Workers (grammY)** - use the `"cloudflare-mod"` adapter (not `"cloudflare"`). 30s CPU limit. KV or D1 for persistence.
- **VPS with systemd** - any framework, good fit for long polling. `Restart=always` + `EnvironmentFile=` for the `.env` file.

## Bundled Resources

- [Framework Comparison](references/framework-comparison.md)
- [Conversations](references/conversations.md) - multi-step flow recipes
- [Deployment](references/deployment.md) - Vercel, Cloudflare Workers, systemd
- [Examples](references/examples.md) - working bots: Hebrew menu, Vercel webhook, python conversation

## Recommended MCP Servers

No Telegram-specific MCP in the directory yet.

## Reference Links

- Bot API changelog: https://core.telegram.org/bots/api-changelog
- BotNews channel: https://t.me/botnews
- grammY: https://grammy.dev/
- python-telegram-bot: https://docs.python-telegram-bot.org/
- Telegraf: https://telegraf.js.org/

## Gotchas

These are common failure modes that agents encounter when generating Telegram bot code:

1. **Mixing framework APIs.** grammY uses `ctx.reply()`, Telegraf uses `ctx.reply()` (looks the same but different Context types), python-telegram-bot uses `update.message.reply_text()`. Agents mix `ctx.reply()` into python-telegram-bot code or use Telegraf's `Markup` with grammY.

2. **Webhook port restriction.** Telegram only delivers webhooks to ports 443, 80, 88, or 8443. Agents often set up webhooks on port 3000 or 8080, which silently fail with no error from Telegram's side.

3. **Forgetting to answer callback queries.** Every `callback_query` update MUST be answered with `answerCallbackQuery()` within 30 seconds, even if you have nothing to show. Failure causes a persistent loading spinner on the user's button. Agents often handle the logic but forget the answer call.

4. **Callback data exceeding 64 bytes.** Agents put Hebrew strings, JSON objects, or long identifiers in callback data. Hebrew characters use 2-3 bytes each in UTF-8. Use short English keys and store full data in session/database.

5. **HTML parse mode escaping.** When using `parse_mode: "HTML"`, the characters `<`, `>`, and `&` in user-provided text MUST be escaped. Agents often echo user input back in HTML mode without escaping, causing parse errors.

6. **Polling and webhook running simultaneously.** If you forget to call `deleteWebhook()` before starting polling, the bot receives no updates via polling. Telegram only sends updates to one endpoint. This is a silent failure.

7. **Pre-checkout query timeout.** The `pre_checkout_query` handler MUST respond within 10 seconds. If the handler does async work (database calls, external APIs) that takes too long, the payment silently fails. Keep the handler lightweight.

8. **grammY session without storage adapter.** The default in-memory session store in grammY resets on every restart. For production, you MUST configure an external session storage (Redis, Supabase, etc.). Agents often skip this and wonder why sessions are lost.

9. **Telegraf v4 vs v3 API changes.** Agents trained on older data may generate Telegraf v3 code (`telegraf.startPolling()`, `telegraf.webhookCallback()`). In v4, it is `bot.launch()` and `bot.webhookCallback()`.

10. **python-telegram-bot v20+ async migration.** Versions before v20 used synchronous handlers. v22.7 is fully async. Agents sometimes generate synchronous code (`def handler` instead of `async def handler`) or use the deprecated `Updater` class.

11. **Hebrew Markdown escaping nightmare.** MarkdownV2 requires escaping: `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`. In Hebrew text this is error-prone. Use HTML parse mode instead.

12. **Missing error handler.** Without a `bot.catch()` (grammY) or error handler, unhandled errors crash the bot process silently. In polling mode, this kills the bot. In webhook mode, Telegram retries the update, potentially causing an infinite error loop.

## Troubleshooting

### "Conflict: terminated by other getUpdates request"

Another instance of your bot is running (maybe a previous process, a second server, or a leftover webhook). Fix:
1. Stop all other bot instances.
2. Call `deleteWebhook` to clear any set webhook.
3. Start your bot again.

### Bot receives no updates

1. Check if a webhook is set: `GET https://api.telegram.org/bot<token>/getWebhookInfo`
2. If `url` is set and you want polling, call `deleteWebhook` first.
3. If using webhooks, verify the URL is publicly accessible and on a valid port (443, 80, 88, 8443).
4. Check if the bot was blocked by the user or removed from the group.

### "Bad Request: can't parse entities"

You have unclosed or malformed HTML/Markdown in your message. Common causes:
- Unescaped `<`, `>`, `&` in HTML mode
- Unescaped special characters in MarkdownV2 mode
- Missing closing tags in HTML

Fix: escape user input before including it in formatted messages:

```typescript
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
```

### "Forbidden: bot was blocked by the user"

The user blocked your bot. This is normal. Handle it gracefully:

```typescript
try {
  await bot.api.sendMessage(userId, "הודעה");
} catch (e) {
  if (e instanceof GrammyError && e.error_code === 403) {
    // User blocked the bot, remove from active users
    console.log(`User ${userId} blocked the bot`);
  }
}
```

### Webhook returns 502/504 timeout

Your handler takes too long. Telegram expects a response within ~60 seconds for webhooks (but in practice, aim for under 30 seconds). Solutions:
- Move heavy processing to a background job queue.
- Send an immediate "processing..." reply, then follow up when done.
- On serverless platforms (Vercel Hobby), the timeout may be as low as 10 seconds.

### Hebrew text appears reversed in logs/console

This is a display issue in terminals that do not support RTL, not an actual data problem. The text is stored correctly and renders properly in Telegram. Do not try to "fix" this by reversing strings.

### Inline keyboard buttons not updating

After `editMessageText`, the old keyboard remains unless you explicitly set `reply_markup` in the edit call. Always pass the new keyboard (or an empty `InlineKeyboard()` to remove it):

```typescript
await ctx.editMessageText("עודכן!", {
  reply_markup: new InlineKeyboard(), // removes keyboard
});
```
