---
name: telegram-bot-builder
description: "Build Telegram bots with grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.2 webhooks vs polling, inline keyboards, commands, middleware patterns, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, and Hebrew message handling. Use when building a Telegram bot, setting up webhooks, handling Hebrew/RTL messages in a bot, or integrating Telegram payments. Do NOT use for WhatsApp bots (use israeli-whatsapp-business), voice bots (use hebrew-voice-bot-builder), or general chatbot design patterns (use hebrew-chatbot-builder)."
license: MIT
---

# Telegram Bot Builder

Build production-ready Telegram bots for the Israeli market using grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.2 (July 2026), webhooks vs polling, inline keyboards, Hebrew/RTL text, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, and serverless deployment.

## Problem

Building Telegram bots for Israeli users involves several challenges that agents consistently get wrong:

1. **Framework choice confusion** - grammY, Telegraf, and python-telegram-bot have different Bot API version support, plugin ecosystems, and deployment models. Agents often mix their APIs or suggest deprecated patterns.
2. **Webhook vs polling misconfiguration** - Agents default to polling (good for development) but fail to set up webhooks correctly for production, missing port restrictions (443, 80, 88, 8443 only), SSL requirements, and secret token verification.
3. **Hebrew/RTL text corruption** - Bidirectional text mixing Hebrew and English (common in Israeli bots) breaks in inline keyboards, callback data, and formatted messages. Agents ignore Unicode control characters and text direction markers.
4. **Payment integration gaps** - Telegram Stars (the in-app currency) has specific invoice creation flows that differ from traditional payment providers. Agents often generate code for deprecated payment APIs.
5. **Mini App data exchange** - The communication protocol between a Telegram Mini App (WebApp) and the bot uses `web_app_data` events, not regular messages. Agents frequently implement this incorrectly.

## Framework Selection

Choose your framework based on your runtime, deployment target, and Bot API version needs:

| Feature | grammY v1.45.1 | Telegraf v4.16.3 | python-telegram-bot v22.8 |
|---------|----------------|-------------------|---------------------------|
| Language | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| Bot API version | Latest (v10.2) | v7.1 | v10.0 |
| Install | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| Plugin ecosystem | Rich (sessions, menus, conversations, i18n) | Moderate (scenes, sessions) | Extensions (JobQueue, persistence) |
| Serverless support | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda adapters | ASGI adapters, manual webhook handlers |
| Middleware model | Composer-based (like Koa) | Composer-based (like Koa) | Handler groups with filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| Webhook mode | `webhookCallback()` adapter | `bot.launch({ webhook })` or `createWebhook()` | `application.run_webhook()` |
| TypeScript types | First-class, auto-generated | Good, manual maintenance | N/A (Python type hints) |
| Recommended for | New projects, serverless, latest API features | Existing Express/Fastify apps | Python shops, data/ML pipelines |

**Decision guide:**
- Need Bot API v10.x features (Stars subscriptions, Gifts, Bot Business, Mini Apps 2.0)? Use **grammY** or **python-telegram-bot**.
- Already have an Express/Fastify server? **Telegraf** integrates cleanly, but note it is effectively dormant: last release 4.16.3 on 2024-02-29 (Bot API 7.1), so it will not see any 10.x surface. Prefer grammY for anything new.
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
- Tokens are rotated with `/token` in BotFather (the docs: "If your existing token is compromised or you lost it for some reason, use the `/token` command to generate a new one").
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

## Group Privacy Mode

The single most common cause of "my group bot receives nothing". **Privacy mode is ON by default for every bot added to a group.** In that state the bot only sees:

- Commands explicitly addressed to it (`/command@this_bot`).
- General commands like `/start`, but only if it was the last bot to post in the group.
- Messages sent via the bot inline.
- Replies to its own messages.

Regardless of privacy mode, a bot always receives service messages, all private-chat messages, and all channel messages where it is a member.

Two ways out, in order of preference:

1. **Add the bot as a group admin.** Admins always receive every message, no setting change needed.
2. **Disable privacy mode** via `/setprivacy` in BotFather. **The bot must then be removed and re-added to the group to take effect**, which is the step people miss. Telegram recommends this only when necessary; a force-reply prompt usually solves the same problem.

The current setting is visible in the group's member list, so this is checkable without touching code.

## Project Setup

Runnable scaffolds for all three frameworks are in [references/quickstarts.md](references/quickstarts.md).

Two things every scaffold needs, in any framework:
- **An error handler.** Without one the bot crashes silently on the first unhandled rejection (`bot.catch()` in grammY and Telegraf, `application.add_error_handler()` in python-telegram-bot).
- **The token read from the environment**, never a literal. Fail fast at startup if `BOT_TOKEN` is unset.

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
- Maximum 64 bytes (not characters). Each Hebrew character is 2 bytes in UTF-8, so 64 bytes is at most 32 Hebrew characters.
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

Middleware runs before handlers and carries logging, auth, rate limiting, and i18n. grammY and Telegraf use a Koa-style `bot.use(async (ctx, next) => ...)` chain; **python-telegram-bot has no middleware** and uses handler groups instead (`group=-1` runs before the default group 0). Worked examples for both, including an `adminOnly` gate, are in [references/middleware.md](references/middleware.md).

### Conversation / Multi-Step Flows

For multi-step flows (registration wizards, order forms), each framework has its own pattern: grammY's `@grammyjs/conversations` plugin (await-style flow), Telegraf's `Scenes.WizardScene`, and python-telegram-bot's `ConversationHandler`. Full working snippets in [references/conversations.md](references/conversations.md).


## Webhook vs Polling

Two rules from the Bot API that decide whether you receive anything at all:

- **They are mutually exclusive.** "There are two mutually exclusive ways of receiving updates for your bot - the `getUpdates` method on one hand and webhooks on the other." A set webhook silently starves polling; call `deleteWebhook` before switching.
- **Undelivered updates expire after 24 hours.** "Incoming updates are stored on the server until the bot receives them either way, but they will not be kept longer than 24 hours." A bot down for a weekend does not get the backlog.

**`allowed_updates` is opt-out, with three exceptions that are opt-in.** Omitting it (or passing an empty list) delivers every update type **except** `chat_member`, `message_reaction`, and `message_reaction_count`. If you are wiring reaction or membership handling and receiving nothing, this is why: name them explicitly in `allowed_updates` on `setWebhook` / `getUpdates`.

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

Telegraf and python-telegram-bot webhook setups are in [references/deployment.md](references/deployment.md). Note that `application.run_webhook()` needs the `[webhooks]` extra; it fails at runtime after a bare `pip install python-telegram-bot`.

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
2. **Callback data encoding** - Keep callback data in ASCII/English. Hebrew in callback data wastes the 64-byte limit (Hebrew UTF-8 = 2 bytes per char).
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

Full implementation with a `normalizeIsraeliPhone` helper: [references/examples.md](references/examples.md), Example 5.

**Security rule:** always check `contact.user_id === ctx.from.id`. Without it a user can forward someone else's contact card and verify a number they do not own.


## Rate Limits & File Size Limits

Telegram enforces hard limits on outgoing traffic. Hitting them returns HTTP 429 with `retry_after`; ignore them and your bot gets throttled or banned.

**Outgoing message rates:**
- **30 messages/second** global, across all chats
- **1 message/second** per individual chat (short bursts may pass before you get 429s)
- **20 messages/minute** per group chat (broadcasts to the same group)

For grammY use [`@grammyjs/auto-retry`](https://github.com/grammyjs/auto-retry), which honours `retry_after` on a 429 automatically (the older `transformer-throttler` has not been released since 2022). python-telegram-bot ships `AIORateLimiter` via its `[rate-limiter]` extra. For Telegraf, implement a per-chat token bucket or use an external queue (BullMQ, Celery).

**`file_id` is tied to a single bot id.** The docs: "your test instance cannot use a shared file_id database to quickly send media, files must be individually reuploaded". Never cache `file_id` values and reuse them across bot tokens; a dev-to-prod copy fails with "wrong file identifier".

**File size limits:**
- **Bot file upload:** 50 MB (default Bot API server)
- **Bot file download:** 20 MB
- **Local Bot API server (any bot, no Premium involved):** downloads with **no size limit**, uploads up to 2000 MB

To upload or download files larger than 50 MB, run a self-hosted [Bot API server](https://github.com/tdlib/telegram-bot-api) and point your bot at it via the `apiRoot` (grammY) / `telegram.apiRoot` (Telegraf) / `base_url` (python-telegram-bot) option.

**Call `logOut` first, or the bot silently receives nothing.** The docs: "You must log out the bot before running it locally, otherwise there is no guarantee that the bot will receive updates. After a successful call, you can immediately log in on a local server, but will not be able to log in back to the cloud Bot API server for 10 minutes." Budget for that 10-minute lockout before you try it in production. Use `close` when moving the bot between local servers, deleting the webhook first.

## Scheduling Jobs in Asia/Jerusalem

Bots that fire at "9 AM Israel time" must use an explicit Israel timezone, not server-local or UTC. Israel observes DST shifts that don't align with most cloud regions (Frankfurt, us-east-1), so a naive UTC offset will drift twice a year.

**python-telegram-bot (`JobQueue`):** requires the `[job-queue]` extra. With a bare `pip install python-telegram-bot`, `application.job_queue` is `None` and this raises `AttributeError`. Use `zoneinfo` from the standard library, not `pytz`, which PTB v20+ dropped as a dependency.

```python
from zoneinfo import ZoneInfo
from datetime import time

application.job_queue.run_daily(
    send_morning_digest,
    time=time(9, 0, tzinfo=ZoneInfo("Asia/Jerusalem")),
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

Introduced in Bot API 7.2 (2024), **Telegram Business** lets a user connect a bot to their personal account so the bot can read and reply to direct messages on their behalf. Israeli users flip this on under Settings > Telegram Business > Chatbots and paste the `@username` of an approved bot.

**Connecting a bot does NOT require Telegram Premium.** Bot API 10.0 (May 2026) "allowed Secretary Bots to manage accounts of users without a Telegram Premium subscription", and the official docs now state that "connected bots are also available to non-Premium users". Premium is still required for the *other* Business features (opening hours, location, quick replies, away/greeting messages, custom start page), so do not gate your bot's onboarding on a Premium check.

When the user connects the bot, your bot receives a `business_connection` update with a `business_connection_id`. Every message that arrives in one of the user's connected chats then carries that same `business_connection_id` field, and any outgoing call (`sendMessage`, `editMessageText`, etc.) must echo it back so Telegram routes the reply through the user's account rather than the bot's account.

What the bot can do once connected:
- Read and reply to incoming DMs on behalf of the Telegram Business user.
- `rights.can_reply` is scoped: it means the bot may send and edit messages **only in private chats that had an incoming message in the last 24 hours**. An off-hours auto-reply is fine; a delayed queue drain or a scheduled follow-up outside that window fails even when `can_reply` is true.
- Fetch the connection itself with `getBusinessConnection` (there is no method that lists the user's chats; you learn about a chat only when a `business_message` arrives in it).
- Send messages, edit, and delete on the user's behalf, gated by the `rights` (`BusinessBotRights`) the user granted.

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

Useful for Israeli small-business owners (אופטיקאים, סטודיות יוגה, סוכני ביטוח) who want auto-replies on their personal Telegram during off-hours without exposing customers to a separate "bot" persona.

Reference: [Telegram Business (API overview)](https://core.telegram.org/api/business) and the [`BusinessConnection`](https://core.telegram.org/bots/api#businessconnection) class in the Bot API reference.

## Payments API

Telegram offers three payment paths. Pick by what you sell:

- **Telegram Stars (XTR)** for digital goods, services, and Mini App content. Released in Bot API 7.4 (May 28, 2024). No external provider needed. Invoices are denominated in `XTR`; what an Israeli user pays for a Stars pack is set by their App Store / Google Play account, so do not quote a fixed shekel price for a Stars amount in your copy.
- **Stars subscriptions** for recurring access (added later in 2024). Same `XTR` currency, with `subscription_period` set on the invoice; users can cancel from Telegram Settings > Stars.
- **Gifts API** (`sendGift`) lets a bot send named gifts to users, which recipients keep on their profile. They **cannot** convert a bot-sent gift back to Stars.
- **paid_media** lets you attach a Stars price to photos/videos posted in chats and channels (the receiver pays Stars to unlock).
- **Traditional payment providers** (Stripe LIVE/TEST, etc.) are still supported for physical goods and non-digital services. Configure a provider token via `/mybots > Payments` in BotFather, then pass it as `provider_token` and a fiat currency (`ILS`, `USD`, etc.).

### Creating an Invoice

**Three hard rules for Stars (`XTR`) invoices, each a hard API failure if broken:**
- `provider_token` must be an **empty string** (it is only for fiat providers).
- `prices` must contain **exactly one item**. A multi-line breakdown is rejected.
- `max_tip_amount` is **not supported** for Stars.

**grammY:**

Worked grammY invoice flow, including the `successful_payment` handler and the `pre_checkout_query` handler (which **must** be answered within 10 seconds), is in [references/examples.md](references/examples.md), Example 6. The python-telegram-bot equivalent is Example 4 in the same file.

### Stars Subscriptions (Recurring)

**`subscription_period` exists ONLY on `createInvoiceLink`, not on `sendInvoice` / `replyWithInvoice`.** Passing it to `sendInvoice` does nothing. Create a link and send that instead. The value must currently always be `2592000` (30 days).

Worked call: [references/examples.md](references/examples.md), Example 7.

Users manage and cancel subscriptions from Telegram Settings > Stars > My Subscriptions. Listen for `message:successful_payment` on each renewal to extend access in your DB.

### Gifts API

`sendGift` lets the bot send a named gift sticker to a user (paid in Stars from the bot's balance). **The receiver CANNOT convert a bot-sent gift back into Stars** (the API states verbatim: "The gift can't be converted to Telegram Stars by the receiver"). `convertGiftToStars` is a different thing: a business-bot method that needs a `business_connection_id` plus the `can_convert_gifts_to_stars` right, acting on gifts owned by a connected business account. Do not promise users a cash-out path. Useful for loyalty rewards and giveaways as a keepsake, not as currency.

Worked call: [references/examples.md](references/examples.md), Example 8. grammY's signature is positional.

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

A persistent menu button is set with `setChatMenuButton` ([references/mini-apps.md](references/mini-apps.md)).

### Receiving Data from Mini App

**Pick the right return channel, they are not interchangeable.** `Telegram.WebApp.sendData()` is *"only available for Mini Apps launched via a Keyboard button"* (a reply-keyboard `web_app` button, private chats only). A Mini App opened from an **inline-keyboard button or the chat menu button, the two launches shown above, cannot call `sendData` at all.**

| Launch path | How data comes back |
|---|---|
| Reply-keyboard `web_app` button | `sendData()` -> `message:web_app_data` service message (no server needed) |
| Inline-keyboard button, menu button, direct link, inline mode | POST to your own backend with `initData`, validated server-side (below) |

For the `sendData` path the button must be a reply keyboard, not an inline one:

```typescript
import { Keyboard } from "grammy";

const kb = new Keyboard()
  .webApp("פתח אפליקציה", "https://your-app.com/mini-app")
  .resized();
await ctx.reply("לחצו לפתיחה:", { reply_markup: kb });
```

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

### Mini Apps 2.0 Features and initData Validation

The Bot API 7.x/8.x "Mini Apps 2.0" surface (fullscreen, home-screen shortcuts, device sensors, biometrics, geolocation, emoji status) and a complete, hardened `validateInitData` implementation are in [references/mini-apps.md](references/mini-apps.md).

**Cross-origin lockdown, in force since 2026-07-20.** Bot API 10.2 "hardened the security of Mini Apps by disallowing the usage of Mini App methods from origins different from the original Mini App domain". A Mini App that embeds third-party iframes or serves from a secondary domain breaks. You can opt out via the @BotFather Mini App, which makes untrusted-link safety your responsibility.

Non-negotiable rules if you serve a Mini App:
- **Never trust `initData` client-side.** Validate it on your server with the HMAC-SHA256 scheme keyed by `WebAppData`, before you read any user field from it.
- **Check `auth_date`.** Without a freshness window a captured `initData` string authenticates forever.
- **Compare hashes in constant time** (`crypto.timingSafeEqual`), not with `===`.
- All 2.0 methods are no-ops on older clients, so feature-detect before calling.

## Deployment

Three common targets, each with framework-specific gotchas. Full working configs are in [references/deployment.md](references/deployment.md):

- **Vercel (grammY)** - `webhookCallback(bot, "std/http")`. Stateless, so use external session storage. Timeouts vary by plan.
- **Cloudflare Workers (grammY)** - the `"cloudflare-mod"` adapter, not `"cloudflare"`. CPU limits vary by plan. KV or D1.
- **VPS with systemd** - any framework, good fit for long polling. `Restart=always` + `EnvironmentFile=`.

## Bundled Resources

- [Quickstarts](references/quickstarts.md) - runnable scaffolds for all three frameworks
- [Framework Comparison](references/framework-comparison.md) - feature matrix and plugin tables
- [Middleware](references/middleware.md) - middleware and handler-group patterns
- [Conversations](references/conversations.md) - multi-step flow recipes
- [Mini Apps](references/mini-apps.md) - 2.0 feature surface and initData validation
- [Deployment](references/deployment.md) - Vercel, Cloudflare Workers, systemd, webhook setups
- [Examples](references/examples.md) - five working end-to-end bots

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

3. **Forgetting to answer callback queries.** Every `callback_query` update MUST be answered with `answerCallbackQuery()`, even if you have nothing to show (the optional `text` is capped at 0-200 characters). Failure causes a persistent loading spinner on the user's button. Agents often handle the logic but forget the answer call.

4. **Callback data exceeding 64 bytes.** Agents put Hebrew strings, JSON objects, or long identifiers in callback data. Hebrew characters are 2 bytes each in UTF-8, so 64 bytes is at most 32 Hebrew characters. Use short English keys and store full data in session/database.

5. **HTML parse mode escaping.** When using `parse_mode: "HTML"`, the characters `<`, `>`, and `&` in user-provided text MUST be escaped. Agents often echo user input back in HTML mode without escaping, causing parse errors.

6. **Polling and webhook running simultaneously.** If you forget to call `deleteWebhook()` before starting polling, the bot receives no updates via polling. Telegram only sends updates to one endpoint. This is a silent failure.

7. **Pre-checkout query timeout.** The `pre_checkout_query` handler MUST respond within 10 seconds. If the handler does async work (database calls, external APIs) that takes too long, the payment silently fails. Keep the handler lightweight.

8. **grammY session without storage adapter.** The default in-memory session store in grammY resets on every restart. For production, you MUST configure an external session storage (Redis, Supabase, etc.). Agents often skip this and wonder why sessions are lost.

9. **Telegraf v4 vs v3 API changes.** Agents trained on older data may generate Telegraf v3 code (`telegraf.startPolling()`, `telegraf.webhookCallback()`). In v4, it is `bot.launch()` and `bot.webhookCallback()`.

10. **python-telegram-bot v20+ async migration.** Versions before v20 used synchronous handlers. v22.8 is fully async. Agents sometimes generate synchronous code (`def handler` instead of `async def handler`) or use the deprecated `Updater` class.

11. **Hebrew Markdown escaping nightmare.** MarkdownV2 requires escaping: `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`. In Hebrew text this is error-prone. Use HTML parse mode instead.

12. **Missing error handler.** Without a `bot.catch()` (grammY) or error handler, unhandled errors crash the bot process silently. In polling mode, this kills the bot. In webhook mode, Telegram retries the update, potentially causing an infinite error loop.

## Examples

Five complete end-to-end examples are in [references/examples.md](references/examples.md): a Hebrew menu bot with inline keyboards, a Vercel webhook bot with Hebrew error messages, a python-telegram-bot conversation flow, a Stars invoice in Python, and Israeli phone-number verification.

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
4. **In a group: check privacy mode** (see "Group Privacy Mode"). This is the most common cause by far, and it looks identical to a broken webhook.
5. If you are expecting `message_reaction` or `chat_member`, confirm they are named in `allowed_updates`, they are not delivered by default.
6. Check if the bot was blocked by the user or removed from the group.

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
- On serverless the function timeout can be very short (plan-dependent), cutting long handlers off.

### Hebrew text appears reversed in logs/console

This is a display issue in terminals that do not support RTL, not an actual data problem. The text is stored correctly and renders properly in Telegram. Do not try to "fix" this by reversing strings.

### Inline keyboard buttons not updating

After `editMessageText`, the old keyboard remains unless you explicitly set `reply_markup` in the edit call. Always pass the new keyboard (or an empty `InlineKeyboard()` to remove it):

```typescript
await ctx.editMessageText("עודכן!", {
  reply_markup: new InlineKeyboard(), // removes keyboard
});
```
