# Conversation / Multi-Step Flows

For multi-step interactions (forms, wizards), each framework has its own approach. Pick by the framework you're already in.

## grammY - Conversations plugin

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
