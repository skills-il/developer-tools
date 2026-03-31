---
name: telegram-bot-builder
description: "Build Telegram bots with grammY, Telegraf, or python-telegram-bot. Covers Bot API v9.5 webhooks vs polling, inline keyboards, commands, middleware patterns, payments API, Mini Apps, and Hebrew message handling. Use when building a Telegram bot, setting up webhooks, handling Hebrew/RTL messages in a bot, or integrating Telegram payments. Do NOT use for WhatsApp bots (use israeli-whatsapp-business), voice bots (use hebrew-voice-bot-builder), or general chatbot design patterns (use hebrew-chatbot-builder)."
license: MIT
---

# Telegram Bot Builder

Build production-ready Telegram bots for the Israeli market using grammY, Telegraf, or python-telegram-bot. This skill covers Bot API v9.5, webhook and polling architectures, inline keyboards, Hebrew/RTL text handling, Telegram Payments, Mini Apps, and deployment to serverless platforms.

## Problem

Building Telegram bots for Israeli users involves several challenges that agents consistently get wrong:

1. **Framework choice confusion** - grammY, Telegraf, and python-telegram-bot have different Bot API version support, plugin ecosystems, and deployment models. Agents often mix their APIs or suggest deprecated patterns.
2. **Webhook vs polling misconfiguration** - Agents default to polling (good for development) but fail to set up webhooks correctly for production, missing port restrictions (443, 80, 88, 8443 only), SSL requirements, and secret token verification.
3. **Hebrew/RTL text corruption** - Bidirectional text mixing Hebrew and English (common in Israeli bots) breaks in inline keyboards, callback data, and formatted messages. Agents ignore Unicode control characters and text direction markers.
4. **Payment integration gaps** - Telegram Stars (the in-app currency) has specific invoice creation flows that differ from traditional payment providers. Agents often generate code for deprecated payment APIs.
5. **Mini App data exchange** - The communication protocol between a Telegram Mini App (WebApp) and the bot uses `web_app_data` events, not regular messages. Agents frequently implement this incorrectly.

## Framework Selection

Choose your framework based on your runtime, deployment target, and Bot API version needs:

| Feature | grammY v1.41.1 | Telegraf v4.16.3 | python-telegram-bot v22.7 |
|---------|----------------|-------------------|---------------------------|
| Language | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| Bot API version | Latest (v9.5) | v7.1 | v9.5 |
| Install | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| Plugin ecosystem | Rich (sessions, menus, conversations, i18n) | Moderate (scenes, sessions) | Extensions (JobQueue, persistence) |
| Serverless support | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda adapters | ASGI adapters, manual webhook handlers |
| Middleware model | Composer-based (like Koa) | Composer-based (like Koa) | Handler groups with filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| Webhook mode | `webhookCallback()` adapter | `bot.launch({ webhook })` or `createWebhook()` | `application.run_webhook()` |
| TypeScript types | First-class, auto-generated | Good, manual maintenance | N/A (Python type hints) |
| Recommended for | New projects, serverless, latest API features | Existing Express/Fastify apps | Python shops, data/ML pipelines |

**Decision guide:**
- Need Bot API v9.5 features (e.g., latest inline query improvements, new message types)? Use **grammY** or **python-telegram-bot**.
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

For multi-step interactions (forms, wizards), each framework has its own approach:

**grammY - Conversations plugin:**

```typescript
import { conversations, createConversation } from "@grammyjs/conversations";

bot.use(session({ initial: () => ({}) }));
bot.use(conversations());

async function registration(conversation, ctx) {
  await ctx.reply("מה השם שלך?");
  const nameCtx = await conversation.wait();
  const name = nameCtx.message?.text;

  await ctx.reply("מה האימייל שלך?");
  const emailCtx = await conversation.wait();
  const email = emailCtx.message?.text;

  await ctx.reply(`תודה ${name}! נרשמת עם ${email}`);
}

bot.use(createConversation(registration));
bot.command("register", async (ctx) => {
  await ctx.conversation.enter("registration");
});
```

**Telegraf - Scenes/Wizard:**

```typescript
import { Scenes, session } from "telegraf";

const registrationWizard = new Scenes.WizardScene(
  "registration",
  async (ctx) => {
    await ctx.reply("מה השם שלך?");
    return ctx.wizard.next();
  },
  async (ctx) => {
    ctx.wizard.state.name = ctx.message.text;
    await ctx.reply("מה האימייל שלך?");
    return ctx.wizard.next();
  },
  async (ctx) => {
    const email = ctx.message.text;
    const name = ctx.wizard.state.name;
    await ctx.reply(`תודה ${name}! נרשמת עם ${email}`);
    return ctx.scene.leave();
  }
);

const stage = new Scenes.Stage([registrationWizard]);
bot.use(session());
bot.use(stage.middleware());
bot.command("register", (ctx) => ctx.scene.enter("registration"));
```

**python-telegram-bot - ConversationHandler:**

```python
from telegram.ext import ConversationHandler

NAME, EMAIL = range(2)

async def register_start(update, context):
    await update.message.reply_text("מה השם שלך?")
    return NAME

async def get_name(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("מה האימייל שלך?")
    return EMAIL

async def get_email(update, context):
    name = context.user_data["name"]
    email = update.message.text
    await update.message.reply_text(f"תודה {name}! נרשמת עם {email}")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register", register_start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
application.add_handler(conv_handler)
```

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

## Payments API (Telegram Stars)

Telegram supports in-app payments using Telegram Stars (XTR), an in-app currency. No external payment provider needed for digital goods.

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
- For physical goods or non-digital services, you need a third-party payment provider (Stripe, etc.) configured via BotFather.
- Refunds are done via `refundStarPayment` API method, not manually.

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

### Vercel Serverless (grammY)

**`api/webhook.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

// Register all handlers
bot.command("start", (ctx) => ctx.reply("!שלום"));
// ... more handlers

export default webhookCallback(bot, "std/http");
```

**Set webhook after deploying:**

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=https://your-app.vercel.app/api/webhook&secret_token=${SECRET}"
```

**Important Vercel caveats:**
- Vercel functions have a 10-second timeout on Hobby plan, 60 seconds on Pro. Long-running operations will fail.
- Each invocation is stateless. Use external storage (Redis, database) for session data.
- grammY's `webhookCallback("std/http")` is the correct adapter for Vercel Edge/Serverless.

### Cloudflare Workers (grammY)

**`src/index.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN);

    bot.command("start", (ctx) => ctx.reply("!שלום"));
    // ... more handlers

    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

**Cloudflare caveats:**
- Use `"cloudflare-mod"` adapter (not `"cloudflare"`).
- Workers have a 30-second CPU time limit (enough for most bot operations).
- Use KV or D1 for persistence, not in-memory state.

### VPS with systemd (Any Framework)

For bots that need long polling or persistent connections:

**`/etc/systemd/system/telegram-bot.service`:**

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/telegram-bot
ExecStart=/usr/bin/node dist/bot.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
EnvironmentFile=/opt/telegram-bot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo journalctl -u telegram-bot -f  # View logs
```

## Bundled Resources

- [Framework Comparison](references/framework-comparison.md) - Detailed feature matrix of grammY vs Telegraf vs python-telegram-bot

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

## Examples

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
