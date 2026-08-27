# Telegram Bot Framework Comparison

Detailed comparison of grammY, Telegraf, and python-telegram-bot for building Telegram bots.

## Version & API Support

| | grammY | Telegraf | python-telegram-bot |
|---|---|---|---|
| **Current version** | v1.46.0 (2026-08-26) | v4.16.3 (2024-02-29) | v22.8 (2026-06-12) |
| **Bot API support** | v10.3 (latest) | v7.1 | v10.0 |
| **Language** | TypeScript / JavaScript | TypeScript / JavaScript | Python 3.10+ |
| **Install** | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| **License** | MIT | MIT | LGPL-3.0 |
| **Async model** | Promise-based | Promise-based | asyncio (fully async) |

## Feature Matrix

| Feature | grammY | Telegraf | python-telegram-bot |
|---------|--------|---------|---------------------|
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| Webhook mode | `webhookCallback()` | `bot.launch({ webhook })` / `createWebhook()` | `application.run_webhook()` |
| Inline keyboards | `InlineKeyboard` class | `Markup.inlineKeyboard()` | `InlineKeyboardMarkup` |
| Reply keyboards | `Keyboard` class | `Markup.keyboard()` | `ReplyKeyboardMarkup` |
| Callback queries | `bot.callbackQuery()` | `bot.action()` | `CallbackQueryHandler` |
| Inline mode | `bot.inlineQuery()` | `bot.on("inline_query")` | `InlineQueryHandler` |
| Middleware | Composer-based (Koa-style) | Composer-based (Koa-style) | Handler groups with priority |
| Sessions | Built-in (`session()` from `grammy`) | Built-in (`session()`) | `persistence` module |
| Conversations | Plugin (`@grammyjs/conversations`) | Scenes / WizardScene | `ConversationHandler` |
| Payments | Native support | Native support | Native support |
| Mini Apps | Native support | Native support | Native support |
| Error handling | `bot.catch()` | `bot.catch()` | `application.add_error_handler()` |
| Rate limiting | `@grammyjs/auto-retry` (retries on 429) or `@grammyjs/ratelimiter` | Community middleware | Built-in `AIORateLimiter` (needs the `[rate-limiter]` extra) |
| i18n | Plugin (`@grammyjs/i18n`) | Community packages | Manual implementation |
| Menu builder | Plugin (`@grammyjs/menu`) | Not built-in | Not built-in |
| File uploads | `ctx.replyWithDocument()` | `ctx.replyWithDocument()` | `update.message.reply_document()` |
| Typed API methods | Auto-generated from Bot API spec | Manually maintained types | Python type hints |

## Deployment Compatibility

| Platform | grammY | Telegraf | python-telegram-bot |
|----------|--------|---------|---------------------|
| **Vercel** | Native adapter (`"std/http"`) | Express adapter + API route | Manual webhook handler |
| **Cloudflare Workers** | Native adapter (`"cloudflare-mod"`) | Not officially supported | Not supported |
| **Deno Deploy** | Native (first-class Deno support) | Limited | Not supported |
| **Supabase Edge Functions** | Native adapter | Not officially supported | Not supported |
| **Fly.io** | Supported (polling or webhook) | Supported | Supported |
| **AWS Lambda** | Native adapter | `createWebhook()` for Lambda | Manual handler |
| **Express/Fastify** | `webhookCallback("express")` | `bot.webhookCallback()` | Manual integration |
| **VPS (polling)** | `bot.start()` | `bot.launch()` | `application.run_polling()` |

## Plugin / Extension Ecosystem

### grammY Plugins (npm: @grammyjs/*)

| Plugin | Purpose |
|--------|---------|
| `@grammyjs/conversations` | Multi-step conversations with await-style flow |
| `@grammyjs/menu` | Interactive inline menus with navigation |
| `@grammyjs/storage-redis`, `-file`, `-free` | Storage adapters for the built-in `session()` (the session middleware itself ships in `grammy`; there is no `@grammyjs/session` package) |
| `@grammyjs/i18n` | Internationalization with Fluent |
| `@grammyjs/ratelimiter` | Rate limiting per user |
| `@grammyjs/hydrate` | Add methods to API response objects |
| `@grammyjs/router` | Route updates by condition |
| `@grammyjs/parse-mode` | Default parse mode for all messages |
| `@grammyjs/auto-retry` | Auto-retry on rate limit (429) errors |
| `@grammyjs/transformer-throttler` | Outgoing request throttling |
| `@grammyjs/runner` | Concurrent update processing |
| `@grammyjs/files` | File download helper |
| `@grammyjs/stateless-question` | Stateless question-answer flows |

### Telegraf Extensions

| Feature | How |
|---------|-----|
| Scenes | Built-in (`Scenes.BaseScene`, `Scenes.WizardScene`) |
| Sessions | Built-in (`session()`) with Redis/Postgres adapters |
| Stage | Built-in scene management |
| Telegraf Test | Community testing utilities |

### python-telegram-bot Extensions

| Feature | How |
|---------|-----|
| `JobQueue` | Built-in scheduled/recurring jobs |
| `persistence` | Built-in state persistence (Pickle, Dict, custom) |
| `ConversationHandler` | Built-in multi-step conversation management |
| `filters` | Extensive built-in message filter system |
| `Defaults` | Global default values for optional parameters |
| `CallbackContext` | Type-safe context with custom data |

## Performance Characteristics

| Aspect | grammY | Telegraf | python-telegram-bot |
|--------|--------|---------|---------------------|
| Cold start (serverless) | Fast (small bundle) | Moderate | Slower (Python runtime) |
| Memory usage | Low | Moderate | Moderate |
| Concurrent updates | `@grammyjs/runner` plugin | Single-threaded by default | asyncio event loop |
| Request batching | Not built-in | Not built-in | Not built-in |
| Backpressure handling | Built-in with runner | Manual | Built-in with update queue |

## Migration Paths

### Telegraf v3 to v4

Common breaking changes agents get wrong:
- `telegraf.startPolling()` -> `bot.launch()`
- `telegraf.webhookCallback()` -> `bot.webhookCallback()`
- `telegraf.handleUpdate()` -> `bot.handleUpdate()`
- `ctx.replyWithMarkdown()` -> `ctx.reply(text, { parse_mode: "MarkdownV2" })`
- Session now requires explicit `session()` middleware

### python-telegram-bot v13 to v20+

Major breaking changes (sync to async):
- `def handler(update, context)` -> `async def handler(update, context)`
- `Updater(token)` -> `Application.builder().token(token).build()`
- `updater.start_polling()` -> `application.run_polling()`
- `updater.start_webhook()` -> `application.run_webhook()`
- `dispatcher.add_handler()` -> `application.add_handler()`
- All handler functions must be `async`
- `MessageHandler(Filters.text, ...)` -> `MessageHandler(filters.TEXT, ...)`

## When to Choose Each

### Choose grammY when:
- Starting a new TypeScript/JavaScript project
- Deploying to serverless (Vercel, Cloudflare Workers, Deno Deploy)
- You need the latest Bot API surface first (grammY tracks v10.3; python-telegram-bot is at v10.0, so the 10.2 ephemeral surface and all of 10.3 need raw API calls there)
- You want a rich plugin ecosystem with official support
- You need concurrent update processing
- You value auto-generated types from the Bot API spec

### Choose Telegraf when:
- You have an existing Express/Fastify application
- Your team is already familiar with Telegraf
- You are maintaining an existing Telegraf codebase (note: Telegraf is effectively dormant, last release 4.16.3 on 2024-02-29, Bot API 7.1, so it will not gain any 10.x surface)
- Bot API v7.1 features are sufficient for your use case
- You prefer scenes/wizards over the conversations plugin model

### Choose python-telegram-bot when:
- Your team primarily works in Python
- You are building ML/AI-powered bots with Python libraries
- You want built-in job scheduling (JobQueue, via the `[job-queue]` extra)
- You need Python-native async support
- Your existing infrastructure is Python-based

## API Call Comparison

### Sending a message with inline keyboard

**grammY:**
```typescript
await ctx.reply("Choose:", {
  reply_markup: new InlineKeyboard().text("Click", "data"),
});
```

**Telegraf:**
```typescript
await ctx.reply("Choose:", Markup.inlineKeyboard([
  Markup.button.callback("Click", "data"),
]));
```

**python-telegram-bot:**
```python
keyboard = [[InlineKeyboardButton("Click", callback_data="data")]]
await update.message.reply_text("Choose:", reply_markup=InlineKeyboardMarkup(keyboard))
```

### Handling callback queries

**grammY:**
```typescript
bot.callbackQuery("data", async (ctx) => {
  await ctx.answerCallbackQuery("Done!");
});
```

**Telegraf:**
```typescript
bot.action("data", async (ctx) => {
  await ctx.answerCbQuery("Done!");
});
```

**python-telegram-bot:**
```python
async def callback(update, context):
    await update.callback_query.answer("Done!")

application.add_handler(CallbackQueryHandler(callback, pattern="data"))
```

### Setting webhook

**grammY:**
```typescript
await bot.api.setWebhook("https://example.com/webhook", {
  secret_token: "my-secret",
});
```

**Telegraf:**
```typescript
await bot.telegram.setWebhook("https://example.com/webhook", {
  secret_token: "my-secret",
});
```

**python-telegram-bot:**
```python
application.run_webhook(
    webhook_url="https://example.com/webhook",
    secret_token="my-secret",
)
```
