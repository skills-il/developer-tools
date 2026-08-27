# Quickstart Scaffolds

Minimal runnable starting points for each framework. All three use long polling; see the Webhook section of SKILL.md for production.

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
  await ctx.reply("שלום! אני הבוט שלך");
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

bot.start((ctx) => ctx.reply("שלום! אני הבוט שלך"));

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
pip install "python-telegram-bot[job-queue,webhooks]" python-dotenv
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
    await update.message.reply_text("שלום! אני הבוט שלך")


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

