# Conversation / Multi-Step Flows

For multi-step interactions (forms, wizards), each framework has its own approach. Pick by the framework you're already in.

## grammY - Conversations plugin (2.x)

Written against `@grammyjs/conversations` 2.1.1 and grammy 1.46.0, and type-checked with `tsc --strict`. Three things v1-era samples get wrong: the context flavor, side effects outside `conversation.external()`, and the assumption that `session()` is required.

```typescript
import { Bot, type Context } from "grammy";
import {
  type Conversation,
  type ConversationFlavor,
  conversations,
  createConversation,
} from "@grammyjs/conversations";

// Without the flavor, bot.use(conversations()) does not compile.
type MyContext = ConversationFlavor<Context>;
type MyConversation = Conversation<MyContext, Context>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// 2.x keeps conversation state itself, in memory by default (lost on restart, and
// on Vercel/Workers lost between invocations). On serverless, from day one:
//   import { RedisAdapter } from "@grammyjs/storage-redis";
//   bot.use(conversations({ storage: new RedisAdapter({ instance: redis }) }));
bot.use(conversations());

async function registration(conversation: MyConversation, ctx: Context) {
  await ctx.reply("מה השם שלך?");
  const name = (await conversation.waitFor("message:text")).message.text;

  await ctx.reply("מה האימייל שלך?");
  const email = (await conversation.waitFor("message:text")).message.text;

  // The function is replayed on every update. Anything with a side effect
  // (DB write, HTTP call, Date.now(), Math.random()) must run inside external(),
  // or it runs again on each replay.
  await conversation.external(() => saveUser({ name, email }));

  // \u2068...\u2069 isolates the LTR email so the Hebrew punctuation stays in place
  await ctx.reply(`תודה ${name}! נרשמת עם \u2068${email}\u2069`);
}

bot.use(createConversation(registration));
bot.command("register", async (ctx) => {
  await ctx.conversation.enter("registration");
});
```

`waitFor("message:text")` narrows the type, so `.message.text` needs no optional chaining, and a sticker or photo sent mid-flow is skipped instead of producing `undefined`.

## Telegraf - Scenes / WizardScene

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

## python-telegram-bot - ConversationHandler

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
