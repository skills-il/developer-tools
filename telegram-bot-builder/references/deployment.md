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

export default webhookCallback(bot, "std/http");
```

**Set webhook after deploying:**

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=https://your-app.vercel.app/api/webhook&secret_token=${SECRET}"
```

**Important Vercel caveats:**
- Vercel function timeouts vary by plan; check Vercel's current limits. Long-running operations will fail.
- Each invocation is stateless. Use external storage (Redis, database) for session data.
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
app.use(bot.webhookCallback("/webhook"));
app.listen(443);
await bot.telegram.setWebhook("https://your-domain.com/webhook", {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});

// Option 3: Lambda/serverless
// Export the handler
// createWebhook() is async: it returns a Promise of an Express-style middleware
export const handler = await bot.createWebhook({ domain: "https://your-domain.com" });
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

