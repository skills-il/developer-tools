# Telegram Bot Deployment Recipes

End-to-end webhook deployments for grammY (Vercel, Cloudflare Workers) and a generic systemd unit for VPS-hosted bots.

## Vercel Serverless (grammY)

**`api/webhook.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

// Register all handlers
bot.command("start", (ctx) => ctx.reply("שלום!"));
// ... more handlers

// secretToken makes grammY reject requests whose X-Telegram-Bot-Api-Secret-Token
// header does not match. Omit it and grammY accepts every POST to this URL.
export default webhookCallback(bot, "std/http", {
  secretToken: process.env.WEBHOOK_SECRET_TOKEN,
});
```

**Set webhook after deploying:**

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=https://your-app.vercel.app/api/webhook&secret_token=${WEBHOOK_SECRET_TOKEN}"
```

**Important Vercel caveats:**
- Vercel function timeouts vary by plan; check Vercel's current limits. Long-running operations will fail.
- Each invocation is stateless. Use external storage (Redis, database) for session data AND for conversations: `conversations({ storage: new RedisAdapter({ instance }) })` from `@grammyjs/storage-redis` (works with Vercel KV per that package's README). The in-memory default loses a half-finished wizard on the next cold start.
- grammY's `webhookCallback` gives up after 10 seconds by default (`timeoutMilliseconds`, `onTimeout: "throw"`). Telegram treats that as a failure and redelivers, so pair slow handlers with the dedupe middleware below.
- grammY's `webhookCallback("std/http")` is the correct adapter for Vercel Edge/Serverless.

## Cloudflare Workers (grammY)

**`src/index.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN);

    bot.command("start", (ctx) => ctx.reply("שלום!"));
    // ... more handlers

    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

**Cloudflare caveats:**
- Use `"cloudflare-mod"` adapter (not `"cloudflare"`).
- Workers CPU time limits vary by plan.
- Use KV or D1 for persistence, not in-memory state.

## VPS with systemd (Any Framework)

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

## Webhook setup: Telegraf and python-telegram-bot

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
app.use(bot.webhookCallback("/webhook", { secretToken: process.env.WEBHOOK_SECRET_TOKEN }));
app.listen(443);
await bot.telegram.setWebhook("https://your-domain.com/webhook", {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});

// Option 3: Lambda/serverless
// Export the handler
// createWebhook() is async: it returns a Promise of an Express-style middleware
// Pass secret_token: createWebhook then also checks the header on every request
export const handler = await bot.createWebhook({
  domain: "https://your-domain.com",
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});
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

## Local Bot API server (files above 50 MB)

Run a self-hosted [Bot API server](https://github.com/tdlib/telegram-bot-api) and point the bot at it via `apiRoot` (grammY), `telegram.apiRoot` (Telegraf) or `base_url` (python-telegram-bot). It downloads with no size limit and uploads up to 2000 MB.

**Call `logOut` first, or the bot silently receives nothing.** The docs: "You must log out the bot before running it locally, otherwise there is no guarantee that the bot will receive updates. After a successful call, you can immediately log in on a local server, but will not be able to log in back to the cloud Bot API server for 10 minutes." Budget for that lockout before trying it in production. Use `close` when moving between local servers, deleting the webhook first.

## Deduplicating webhook updates (grammY + Redis)

Telegram repeats a webhook request on any non-2XX answer, so the same update can arrive twice. Mark each `update_id` with a TTL'd key and skip repeats. Never keep a "highest id seen" watermark: "If there are no new updates for at least a week, then identifier of the next update will be chosen randomly instead of sequentially", which would make a watermark drop everything after a quiet week.

```typescript
import IORedis from "ioredis";
const redis = new IORedis(process.env.REDIS_URL!);

// Install first, before any handler. Type-checked against grammy 1.46.0 + ioredis 5.
bot.use(async (ctx, next) => {
  const key = `tg:upd:${ctx.update.update_id}`;
  const fresh = await redis.set(key, "1", "EX", 86400, "NX");
  if (fresh === null) return; // already seen: answer 200 and do nothing
  try {
    await next();
  } catch (err) {
    await redis.del(key); // let Telegram's retry through
    throw err;
  }
});
```

The rollback lives in the middleware because `bot.catch()` "has no effect" for webhooks. If you would rather never retry, drop the `try` and answer every failure with 200 through `bot.errorBoundary()`. Note the two do not combine silently: an `errorBoundary` swallows the error, so the rollback above never runs unless the boundary's handler rethrows. For payments, also put a unique constraint on `telegram_payment_charge_id`: that is the business-level key, `update_id` only the transport one.

