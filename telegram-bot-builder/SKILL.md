---
name: telegram-bot-builder
description: "Build Telegram bots with grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.3 webhooks vs polling, inline keyboards, commands, middleware patterns, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, and Hebrew message handling. Use when building a Telegram bot, setting up webhooks, handling Hebrew/RTL messages in a bot, or integrating Telegram payments. Do NOT use for WhatsApp bots (use israeli-whatsapp-business), voice bots (use hebrew-voice-bot-builder), or general chatbot design patterns (use hebrew-chatbot-builder)."
license: MIT
---

# Telegram Bot Builder

Build production-ready Telegram bots for the Israeli market using grammY, Telegraf, or python-telegram-bot. Covers Bot API v10.3 (24 August 2026), webhooks vs polling, inline keyboards, Hebrew/RTL text, Telegram Stars + Gifts payments, Mini Apps 2.0, Bot Business mode, and serverless deployment.

## Problem

Building Telegram bots for Israeli users involves several things agents consistently get wrong:

1. **Framework confusion** - grammY, Telegraf and python-telegram-bot sit on different Bot API versions and mix badly. Agents blend their APIs or emit deprecated patterns.
2. **Webhook misconfiguration** - agents default to polling and then set webhooks up wrong for production, missing the port restriction (443, 80, 88, 8443 only), SSL, and secret-token verification.
3. **Hebrew/RTL corruption** - bidirectional text breaks in inline keyboards, callback data and formatted messages when Unicode direction marks are ignored.
4. **Payment gaps** - Telegram Stars has invoice rules that differ from fiat providers, and agents generate deprecated payment code.
5. **Mini App data exchange** - the WebApp-to-bot channel depends on how the app was launched, and `sendData` is unavailable from inline-keyboard launches.
6. **Version drift** - the Bot API ships several times a year and models learn a frozen snapshot. This skill was last verified against Bot API 10.3 on 2026-08-27; check the changelog before trusting any version-specific claim here.

## Framework Selection

Choose by runtime, deployment target and Bot API version:

| Feature | grammY v1.46.0 | Telegraf v4.16.3 | python-telegram-bot v22.8 |
|---------|----------------|-------------------|---------------------------|
| Language | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| Bot API version | Latest (v10.3) | v7.1 | v10.0 |
| Install | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| Plugin ecosystem | Rich (sessions, menus, conversations, i18n) | Moderate (scenes, sessions) | Extensions (JobQueue, persistence) |
| Serverless | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda adapters | ASGI adapters, manual handlers |
| Middleware | Composer (Koa-style) | Composer (Koa-style) | Handler groups with filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| Webhook | `webhookCallback()` | `bot.launch({ webhook })` | `application.run_webhook()` |
| Recommended for | New projects, serverless, latest API | Existing Express/Fastify apps | Python and ML shops |

Full comparison: [references/framework-comparison.md](references/framework-comparison.md).

**Decision guide:**
- Need Bot API v10.x features (Stars subscriptions, Gifts, Bot Business, Mini Apps 2.0, ephemeral messages)? Use **grammY**, which is the only one of the three currently on 10.3. python-telegram-bot is on 10.0, so the 10.2 ephemeral surface and everything in 10.3 needs raw API calls there.
- Already have an Express/Fastify server? **Telegraf** integrates cleanly, but note it is effectively dormant: last release 4.16.3 on 2024-02-29 (Bot API 7.1), so it will not see any 10.x surface. Prefer grammY for anything new.
- Python team or ML pipeline? **python-telegram-bot** is the only choice.
- Vercel, Cloudflare Workers or Deno? **grammY** has native adapters.

## What Bot API 10.3 Changed (24 August 2026)

If you learned this surface on 10.2, four things moved.

- **Ephemeral messages were re-shaped.** 10.2 added `receiver_user_id` and `callback_query_id` to `sendMessage` and twelve sibling send methods. **10.3 replaced both with a single `ephemeral_message_parameters` object** (class `EphemeralMessageParameters`). Code written against the 10.2 shape breaks. The new object also carries `replace_callback_query_message`, which shows the ephemeral message in place of the original rather than as a new one.
- **Keyboards gained `disabled` / `DisabledButton` and `force_reply`.** See Inline Keyboards below.
- **`can_send_welcome_messages`** was added to `ChatAdministratorRights`, `ChatMemberAdministrator` and `promoteChatMember`. If you promote admins programmatically, this right now exists.
- **Draft generation can be stopped.** `sendMessageDraft` and `sendRichMessageDraft` gained `can_stop` and `keep_on_stop`, and `MessageGenerationStopped` (field `stopped_message_generation` on `Update`) fires when the user stops. **If you stream an AI reply into a draft, handle it**, or you keep generating and billing against a user who already pressed stop.

Rich Messages also gained buttons (`RichMessageButton`, `RichTextButton`, `RichBlockButtons`), a document block and an expandable block quotation.

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

The single most common cause of "my group bot receives nothing". **Privacy mode is ON by default for every bot in a group.** In that state the bot sees only commands addressed to it (`/command@this_bot`), general commands like `/start` if it was the last bot to post, messages sent via the bot inline, and replies to its own messages. Regardless of the setting it always gets service messages, all private-chat messages, and channel messages where it is a member.

Two ways out, in order of preference:

1. **Add the bot as a group admin.** Admins receive every message, with no setting change.
2. **Disable privacy mode** via `/setprivacy` in BotFather, then **remove and re-add the bot to the group**, which is the step people miss. A force-reply prompt usually solves the same problem with less exposure.

The current setting is visible in the group's member list, so it is checkable without touching code.

## Project Setup

Runnable scaffolds for all three frameworks are in [references/quickstarts.md](references/quickstarts.md).

Two things every scaffold needs, in any framework:
- **An error handler.** Without one the bot crashes silently on the first unhandled rejection (`bot.catch()` in grammY and Telegraf, `application.add_error_handler()` in python-telegram-bot).
- **The token read from the environment**, never a literal. Fail fast at startup if `BOT_TOKEN` is unset.

## Core Patterns

### Inline Keyboards

Inline keyboards attach buttons directly to messages, the primary interactive element in Telegram bots.

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

**Callback data rules:** maximum **64 bytes**, not characters. Hebrew is 2 bytes per character in UTF-8, so that is at most 32 Hebrew characters. Keep Hebrew in the button text and short English identifiers in the callback data.

The Telegraf and python-telegram-bot equivalents of the same menu, including the `CallbackQueryHandler` registration, are in [references/examples.md](references/examples.md).

**Two 10.3 additions belong on every keyboard you build.** `InlineKeyboardButton` gained a **`disabled`** field with a companion **`DisabledButton`** class, so you can grey a button out in place instead of rebuilding the markup. Both `InlineKeyboardMarkup` and `ReplyKeyboardMarkup` gained **`force_reply`**, previously reachable only through the separate `ForceReply` object. grammY 1.46.0 types both. python-telegram-bot 22.8 sits on Bot API 10.0 and its typed objects reject unknown keyword arguments, so reach them through `Bot.do_api_request`.

### Middleware Patterns

Middleware carries logging, auth, rate limiting and i18n. grammY and Telegraf use a Koa-style `bot.use(async (ctx, next) => ...)` chain; **python-telegram-bot has no middleware** and uses handler groups (`group=-1` runs before the default 0). Examples including an `adminOnly` gate: [references/middleware.md](references/middleware.md).

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

Telegram pushes updates to your server. Lower latency, required for serverless.

**Requirements:** HTTPS with a valid certificate (self-signed works but is not recommended); a public URL Telegram can reach; a **port that is 443, 80, 88 or 8443**, which is a hard restriction agents frequently miss; and a secret token to stop spoofed requests.

**grammY webhook setup (Express):**

```typescript
import express from "express";
import { webhookCallback } from "grammy";

const app = express();
app.use(express.json());

// Put a secret in the path as well as in the header
app.use("/webhook/" + process.env.WEBHOOK_SECRET, webhookCallback(bot, "express"));
app.listen(443);

await bot.api.setWebhook(`https://your-domain.com/webhook/${process.env.WEBHOOK_SECRET}`, {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN, // arrives as X-Telegram-Bot-Api-Secret-Token
});
```

Telegraf and PTB webhook setups: [references/deployment.md](references/deployment.md). Note `application.run_webhook()` needs the `[webhooks]` extra and fails at runtime after a bare `pip install python-telegram-bot`.

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

Hitting these returns HTTP 429 with `retry_after`; ignore them and the bot gets throttled or banned.

**Outgoing message rates:** about **30 messages/second** for bulk broadcasts across all chats, **1 message/second** per individual chat (short bursts may pass before the 429s start), and **20 messages/minute** per group chat.

**30/second is the free tier, but the paid tier has an eligibility gate almost no Israeli SMB bot clears.** Paid broadcasts raise the limit to **1000 messages/second** at **0.1 Stars** per message above the free 30/second, but to enable it "a bot must have at least 100,000 Stars on its balance and at least 100,000 monthly active users". Do not architect a fan-out around 1000/second before checking those two numbers. Below the gate, the FAQ's own advice is the answer: spread the broadcast over **8-12 hours** instead of pushing it through at once.

For grammY use [`@grammyjs/auto-retry`](https://github.com/grammyjs/auto-retry), which honours `retry_after` on a 429 (the older `transformer-throttler` has not shipped since 2022). python-telegram-bot has `AIORateLimiter` in its `[rate-limiter]` extra. Telegraf needs a per-chat token bucket or an external queue.

**`file_id` is tied to a single bot id.** The docs: "the file_id field is tied to a single bot id, so your test instance cannot use a shared file_id database to quickly send media - files must be individually reuploaded". Never reuse `file_id` values across bot tokens; a dev-to-prod copy fails with "wrong file identifier".

**File size limits:** upload **50 MB**, download **20 MB** on the default server. A **local Bot API server** (no Premium involved) downloads with **no size limit** and uploads up to **2000 MB**.

For files above 50 MB, run a self-hosted [Bot API server](https://github.com/tdlib/telegram-bot-api) and point the bot at it via `apiRoot` (grammY), `telegram.apiRoot` (Telegraf) or `base_url` (python-telegram-bot).

**Call `logOut` first, or the bot silently receives nothing.** The docs: "You must log out the bot before running it locally, otherwise there is no guarantee that the bot will receive updates. After a successful call, you can immediately log in on a local server, but will not be able to log in back to the cloud Bot API server for 10 minutes." Budget for that lockout before trying it in production. Use `close` when moving between local servers, deleting the webhook first.

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

**Connecting a bot does NOT require Telegram Premium.** Bot API 10.0 (May 2026) "allowed Secretary Bots to manage accounts of users without a Telegram Premium subscription" (the changelog words the same item as "Business Bots"), and core.telegram.org/api/business states that "connected bots are also available to non-Premium users". Premium is still required for the *other* Business features (opening hours, location, quick replies, away/greeting messages, custom start page), so do not gate onboarding on a Premium check.

When the user connects the bot, your bot receives a `business_connection` update with a `business_connection_id`. Every message that arrives in one of the user's connected chats then carries that same `business_connection_id` field, and any outgoing call (`sendMessage`, `editMessageText`, etc.) must echo it back so Telegram routes the reply through the user's account rather than the bot's account.

What the bot can do once connected:
- Read and reply to incoming DMs on behalf of the Telegram Business user.
- `rights.can_reply` is scoped: it lets the bot send and edit **only in private chats that had an incoming message in the last 24 hours**. An off-hours auto-reply is fine; a delayed queue drain outside that window fails even when `can_reply` is true.
- Fetch the connection with `getBusinessConnection`. There is no method that lists the user's chats; you learn about a chat only when a `business_message` arrives in it.
- Act on the user's behalf gated by the `rights` (`BusinessBotRights`) they granted. Note the account-management setters are **set-only** except one: `setBusinessAccountName`, `setBusinessAccountUsername`, `setBusinessAccountBio` and `setBusinessAccountGiftSettings` have no `remove*` counterpart. Only `removeBusinessAccountProfilePhoto` exists.

The grammY handlers for capturing `business_connection` (permissions live under `conn.rights`, there is no top-level `conn.can_reply`) and for echoing `business_connection_id` back on every reply are in [references/examples.md](references/examples.md).

Useful for Israeli small-business owners (אופטיקאים, סטודיות יוגה, סוכני ביטוח) who want off-hours auto-replies on their personal Telegram without a separate "bot" persona.

Reference: [Telegram Business](https://core.telegram.org/api/business) and [`BusinessConnection`](https://core.telegram.org/bots/api#businessconnection).

## Payments API

Telegram offers three payment paths. Pick by what you sell:

- **Telegram Stars (XTR)** for digital goods, services and Mini App content. Bot API 7.4 (28 May 2024), no external provider needed. What an Israeli user pays for a Stars pack is set by their App Store or Google Play account, so never quote a fixed shekel price for a Stars amount.
- **Stars subscriptions** for recurring access. Same `XTR` currency with `subscription_period` on the invoice link; users cancel from Settings > Stars.
- **Gifts API** (`sendGift`) lets a bot send named gifts to users, which recipients keep on their profile. They **cannot** convert a bot-sent gift back to Stars.
- **paid_media** lets you attach a Stars price to photos/videos posted in chats and channels (the receiver pays Stars to unlock).
- **Traditional payment providers** (Stripe and friends) still cover physical goods and non-digital services. Configure a provider token via `/mybots > Payments` in BotFather, then pass `provider_token` plus a fiat currency (`ILS`, `USD`).

### Creating an Invoice

**Three hard rules for Stars (`XTR`) invoices, each an API failure if broken:** `provider_token` must be an **empty string** (fiat only); `prices` must contain **exactly one item**, so no multi-line breakdown; and `max_tip_amount` is **not supported**.

**grammY:**

The grammY invoice flow, with the `successful_payment` handler and the `pre_checkout_query` handler (which **must** answer within 10 seconds), is Example 6 in [references/examples.md](references/examples.md); the PTB equivalent is Example 4.

### Stars Subscriptions (Recurring)

**`subscription_period` is not available on `sendInvoice` / `replyWithInvoice`.** Passing it there does nothing; use `createInvoiceLink` and send the link. It is also required on `createChatSubscriptionInviteLink`, the separate channel-subscription path, and appears on `SuccessfulPayment` and `StarTransaction`. The value must currently always be `2592000` (30 days).

Worked call: [references/examples.md](references/examples.md), Example 7.

Users manage and cancel subscriptions from Telegram Settings > Stars > My Subscriptions.

**Do not drive renewals off `message:successful_payment` alone.** Bot API 10.2 added a dedicated update for this: the class **`BotSubscriptionUpdated`** and the field **`subscription`** on `Update` ("Added updates about changes to a user payment subscription"). That is what tells you a subscription was renewed, cancelled, or expired. A `successful_payment` handler sees the renewal charge but never sees a cancellation, so a bot built only on it keeps serving a user who cancelled.

### Gifts API

`sendGift` sends a named gift sticker to a user, paid in Stars from the bot's balance. **The receiver CANNOT convert a bot-sent gift back into Stars**, verbatim: "The gift can't be converted to Telegram Stars by the receiver". `convertGiftToStars` is a different method: a business-bot one needing a `business_connection_id` and the `can_convert_gifts_to_stars` right, acting on gifts owned by a connected business account. Never promise a cash-out path. Treat gifts as keepsakes for loyalty and giveaways, not currency.

Worked call: [references/examples.md](references/examples.md), Example 8. grammY's signature is positional.

Always call `getAvailableGifts` first to fetch the current catalog and pricing.

### paid_media

Attach a Stars price to a photo or video in a chat or channel. **`sendPaidMedia` is the only way to send it.** There is no `paid_media` parameter on `sendMessage` or any other send method: in the reference `paid_media` appears only as an incoming field on `Message`, inside `PaidMediaInfo`, and on `StarTransaction`. Set `star_count` on `sendPaidMedia` and read purchases from the `purchased_paid_media` update.

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
| Inline-keyboard button, menu button, direct link, inline mode | POST to your own backend with `initData`, validated server-side |

**`sendData` is capped at 4096 bytes.** A serialised cart with line items crosses that on a real order, silently. If the payload can grow, use the `initData` plus backend route.

Both flows end to end (the reply-keyboard button, the browser-side `sendData` and `MainButton` calls, the `message:web_app_data` handler, and the server-side `initData` POST) are in [references/mini-apps.md](references/mini-apps.md).

**Never trust `initData` without validating the HMAC server-side**; it is trivially forged. The hardened implementation, with the `auth_date` freshness check, is in the same reference.

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

Common failure modes when generating Telegram bot code:

1. **Mixing framework APIs.** grammY and Telegraf both expose `ctx.reply()` but with different Context types; python-telegram-bot uses `update.message.reply_text()`. Agents mix `ctx.reply()` into python-telegram-bot code, or Telegraf's `Markup` into grammY.

2. **Webhook port restriction.** Telegram only delivers webhooks to ports 443, 80, 88, or 8443. Agents often set up webhooks on port 3000 or 8080, which silently fail with no error from Telegram's side.

3. **Forgetting to answer callback queries.** Every `callback_query` MUST be answered with `answerCallbackQuery()` even with nothing to show (`text` is capped at 0-200 chars), or the user gets a stuck spinner.

4. **Callback data exceeding 64 bytes.** Hebrew is 2 bytes per character in UTF-8, so 64 bytes is at most 32 Hebrew characters. Use short English keys and keep full data in session or a database.

5. **HTML parse mode escaping.** With `parse_mode: "HTML"`, `<`, `>` and `&` in user text MUST be escaped. Echoing user input unescaped is the usual cause of a parse error.

6. **Polling and webhook at once.** Without `deleteWebhook()` before polling, the bot receives nothing. Telegram delivers to one endpoint only, and fails silently.

7. **Pre-checkout query timeout.** The `pre_checkout_query` handler MUST respond within 10 seconds. If the handler does async work (database calls, external APIs) that takes too long, the payment silently fails. Keep the handler lightweight.

8. **grammY session without a storage adapter.** The default in-memory store resets on every restart. Production needs external storage (Redis, Supabase).

9. **Telegraf v4 vs v3.** Older training data generates v3 (`telegraf.startPolling()`). In v4 it is `bot.launch()` and `bot.webhookCallback()`.

10. **python-telegram-bot v20+ is fully async.** Pre-v20 training data generates `def handler` instead of `async def handler`, or the deprecated `Updater`.

11. **Hebrew Markdown escaping nightmare.** MarkdownV2 requires escaping: `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`. In Hebrew text this is error-prone. Use HTML parse mode instead.

12. **Missing error handler.** Without `bot.catch()` (grammY) or an equivalent, an unhandled error kills the process in polling mode, and in webhook mode Telegram retries the update into an infinite error loop.

13. **Writing 10.2 ephemeral code against a 10.3 API.** `receiver_user_id` and `callback_query_id` were replaced by `ephemeral_message_parameters`. Any sample dated before 24 August 2026, including anything a model learned from, uses the dead shape.

## Examples

Eight complete end-to-end examples are in [references/examples.md](references/examples.md), covering Hebrew menu bots, a Vercel webhook bot, conversation flows, Stars invoices and subscription links, `sendGift`, phone-number verification, the Telegraf and PTB keyboard variants, and the Bot Business handlers.

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
