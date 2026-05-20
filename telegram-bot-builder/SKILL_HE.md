---
name: telegram-bot-builder
description: "בנו בוטים לטלגרם עם grammY, Telegraf או python-telegram-bot. מכסה Bot API v10.0, webhooks מול polling, מקלדות אינליין, פקודות, middleware, תשלומים ב-Telegram Stars + Gifts, Mini Apps 2.0, מצב Bot Business וטיפול בהודעות בעברית עם RTL. השתמשו כשבונים בוט טלגרם, מגדירים webhooks, מטפלים בהודעות בעברית בתוך בוט, או משלבים תשלומים דרך טלגרם. אל תשתמשו לבוטים של וואטסאפ (השתמשו ב-israeli-whatsapp-business), בוטים קוליים (השתמשו ב-hebrew-voice-bot-builder), או עיצוב צ'אטבוטים כללי (השתמשו ב-hebrew-chatbot-builder)."
license: MIT
---

# בניית בוט טלגרם

בנו בוטים מוכנים לפרודקשן לשוק הישראלי עם grammY, Telegraf או python-telegram-bot. המדריך מכסה Bot API v10.0 (שוחרר באפריל 2026; אומת ב-20.05.2026), ארכיטקטורות webhook ו-polling, מקלדות אינליין, טיפול בטקסט עברי/RTL, תשלומים ב-Telegram Stars ו-Gifts, Mini Apps 2.0, מצב Bot Business, זרימת Managed Bots מ-v9.6, זרימת guest-bot של v10.0 לאיגנט-טים, ודיפלוי לפלטפורמות serverless.

## בעיה

בניית בוטים לטלגרם לקהל ישראלי מביאה עמה כמה אתגרים שסוכנים נוטים להיכשל בהם שוב ושוב:

1. **בחירת פריימוורק לא מתאים** - grammY, Telegraf ו-python-telegram-bot תומכים בגרסאות שונות של Bot API, יש להם מערכות פלאגינים שונות ומודלי דיפלוי שונים. סוכנים מערבבים בין ה-API-ים או מציעים תבניות מיושנות.
2. **הגדרת Webhook שגויה** - סוכנים בוחרים polling כברירת מחדל (טוב לפיתוח) אבל לא מגדירים נכון webhook לפרודקשן. חוסר בפורטים מותרים (רק 443, 80, 88, 8443), דרישות SSL ואימות secret token.
3. **שיבוש טקסט עברי/RTL** - ערבוב טקסט עברי ואנגלי (נפוץ מאוד בבוטים ישראליים) נשבר במקלדות אינליין, callback data והודעות מפורמטות. סוכנים מתעלמים מתווים Unicode לכיווניות.
4. **חוסרים באינטגרציית תשלומים** - ל-Telegram Stars (המטבע הפנימי) יש flow ספציפי ליצירת חשבוניות שונה מספקי תשלום רגילים. סוכנים מייצרים קוד ל-API-ים ישנים.
5. **תקשורת לקויה עם Mini App** - הפרוטוקול בין Mini App של טלגרם לבוט משתמש באירועי `web_app_data`, לא בהודעות רגילות. סוכנים מממשים את זה לא נכון.

## בחירת פריימוורק

בחרו פריימוורק לפי השפה, יעד הדיפלוי וגרסת Bot API שאתם צריכים:

| תכונה | grammY v1.42.0 | Telegraf v4.16.3 | python-telegram-bot v22.7 |
|--------|----------------|-------------------|---------------------------|
| שפה | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| גרסת Bot API | עדכנית (v9.6) | v7.1 | v9.6 |
| התקנה | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| פלאגינים | עשיר (sessions, menus, conversations, i18n) | בינוני (scenes, sessions) | הרחבות (JobQueue, persistence) |
| serverless | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda adapters | ASGI adapters, webhook ידני |
| מודל middleware | Composer (כמו Koa) | Composer (כמו Koa) | Handler groups עם filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| מצב webhook | `webhookCallback()` | `bot.launch({ webhook })` או `createWebhook()` | `application.run_webhook()` |
| כדאי ל... | פרויקטים חדשים, serverless, פיצ'רים חדשים | אפליקציות Express/Fastify קיימות | צוותי Python, ML/data pipelines |

**איך בוחרים:**
- צריכים פיצ'רים של Bot API v10.0 (Stars subscriptions, Gifts API, Bot Business, Mini Apps 2.0)? בחרו **grammY** או **python-telegram-bot**.
- כבר יש לכם שרת Express/Fastify? **Telegraf** משתלב חלק.
- צוות Python או פייפליין ML/data? **python-telegram-bot** הבחירה היחידה.
- דיפלוי ל-Vercel/Cloudflare Workers/Deno? ל-**grammY** יש adapters מובנים.

## יצירת בוט עם BotFather

כל בוט טלגרם מתחיל ב-@BotFather. אין דרך אחרת ליצור בוט.

### שלבים

1. פתחו טלגרם, חפשו `@BotFather`, התחילו צ'אט
2. שלחו `/newbot`
3. בחרו שם תצוגה (למשל "הבוט הישראלי שלי")
4. בחרו username שנגמר ב-`bot` (למשל `my_israeli_bot`)
5. BotFather מחזיר טוקן בפורמט: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### כללי אבטחת טוקן

- **לעולם אל תעלו טוקנים ל-git.** השתמשו במשתני סביבה: `BOT_TOKEN` או `TELEGRAM_BOT_TOKEN`.
- אפשר לבטל טוקנים דרך `/revokentoken` ב-BotFather.
- פורמט הטוקן הוא `{bot_id}:{secret}`. החלק לפני הנקודתיים הוא ה-user ID המספרי של הבוט.
- שמרו בקובץ `.env` (הוסיפו ל-`.gitignore`) או בניהול סודות של הפלטפורמה.

### פקודות הגדרה ב-BotFather

```
/setdescription - תיאור הבוט שמוצג לפני שהמשתמש מתחיל
/setabouttext - מוצג בפרופיל הבוט
/setuserpic - אווטאר הבוט
/setcommands - תפריט פקודות (קריטי ל-UX)
/setprivacy - מצב פרטיות בקבוצות (כבו כדי לקרוא את כל ההודעות)
/setinline - הפעלת inline mode
/setinlinefeedback - הסתברות לקבלת עדכוני chosen_inline_result
```

## הקמת פרויקט

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

// טיפול בפקודות
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

// טיפול בהודעות
bot.on("message:text", async (ctx) => {
  await ctx.reply(`קיבלתי: ${ctx.message.text}`);
});

// טיפול בשגיאות (קריטי - בלי זה שגיאות מפילות את הבוט בשקט)
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

// הפעלה עם long polling (פיתוח)
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

// כיבוי מסודר
process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));

// הפעלה עם long polling (פיתוח)
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

    # הפעלה עם long polling (פיתוח)
    application.run_polling()


if __name__ == "__main__":
    main()
```

## תבניות ליבה

### מקלדות אינליין

מקלדות אינליין מצמידות כפתורים ישירות להודעות. זה רכיב ה-UI האינטראקטיבי העיקרי בבוטים.

**grammY:**

```typescript
import { InlineKeyboard } from "grammy";

bot.command("menu", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .text("אפשרות א׳", "option_a")
    .text("אפשרות ב׳", "option_b")
    .row()
    .text("ביטול", "cancel");

  await ctx.reply("בחרו אפשרות:", { reply_markup: keyboard });
});

// טיפול בלחיצות כפתורים
bot.callbackQuery("option_a", async (ctx) => {
  await ctx.answerCallbackQuery({ text: "בחרתם אפשרות א׳!" });
  await ctx.editMessageText("בחרתם: אפשרות א׳");
});

bot.callbackQuery("option_b", async (ctx) => {
  await ctx.answerCallbackQuery({ text: "בחרתם אפשרות ב׳!" });
  await ctx.editMessageText("בחרתם: אפשרות ב׳");
});

bot.callbackQuery("cancel", async (ctx) => {
  await ctx.answerCallbackQuery();
  await ctx.deleteMessage();
});
```

**חוקי callback data קריטיים:**
- מקסימום 64 בייטים (לא תווים). עברית צורכת 2-3 בייטים לתו ב-UTF-8, אז מקבלים בערך 21-32 תווים בעברית.
- השתמשו במזהים קצרים באנגלית ל-callback data, הציגו עברית בטקסט הכפתור.
- כלל אצבע: `טקסט כפתור = עברית למשתמש`, `callback data = מזהה אנגלי לקוד`.

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
    await update.message.reply_text("בחרו אפשרות:", reply_markup=reply_markup)


async def button_handler(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "option_a":
        await query.edit_message_text("בחרתם: אפשרות א׳")
    elif query.data == "option_b":
        await query.edit_message_text("בחרתם: אפשרות ב׳")
    elif query.data == "cancel":
        await query.delete_message()

# רישום handler
application.add_handler(CallbackQueryHandler(button_handler))
```

### תבניות Middleware

Middleware רץ לפני handlers וחיוני ללוגים, אימות, rate limiting ו-i18n.

**middleware ב-grammY:**

```typescript
// middleware לוגים
bot.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`Update ${ctx.update.update_id} processed in ${ms}ms`);
});

// middleware הרשאות (הגבלה למשתמשים ספציפיים)
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

**python-telegram-bot לא משתמש ב-middleware** באותו אופן. במקום זאת, השתמשו ב-handler groups עם עדיפויות:

```python
# handlers של group 0 (ברירת מחדל) רצים קודם, אחר כך group 1 וכו׳
# השתמשו ב-group -1 להתנהגות דמוית middleware
async def log_update(update: Update, context) -> None:
    logger.info(f"Update from user {update.effective_user.id}")

application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)
```

### שיחות / תהליכים רב-שלביים

לאינטראקציות רב-שלביות (טפסים, אשפים), לכל פריימוורק גישה משלו:

**grammY - פלאגין Conversations:**

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

## Webhook מול Polling

### Polling (פיתוח)

Polling גורם לבוט לשאול את טלגרם שוב ושוב "יש עדכונים חדשים?" דרך `getUpdates`. פשוט להגדרה, לא דורש URL ציבורי.

```
Bot --> Telegram: getUpdates?offset=X
Telegram --> Bot: [update1, update2, ...]
Bot --> Telegram: getUpdates?offset=X+2
```

**מתי להשתמש:** פיתוח מקומי, בדיקות, בוטים פשוטים עם תעבורה נמוכה.

### Webhooks (פרודקשן)

Webhooks גורמים לטלגרם לדחוף עדכונים לשרת שלכם. יעיל יותר, latency נמוך יותר, נדרש ל-serverless.

```
משתמש שולח הודעה --> טלגרם --> POST https://your-domain.com/webhook --> הבוט שלכם
```

**דרישות:**
- HTTPS עם תעודת SSL תקפה (self-signed עובד אבל לא מומלץ)
- URL ציבורי נגיש משרתי טלגרם
- **הפורט חייב להיות אחד מ: 443, 80, 88 או 8443** (הגבלה קשיחה של טלגרם, סוכנים מפספסים את זה כל הזמן)
- Secret token לאימות (מומלץ, מונע בקשות מזויפות)

**הגדרת webhook ב-grammY (Express):**

```typescript
import express from "express";
import { webhookCallback } from "grammy";

const app = express();
app.use(express.json());

app.use("/webhook/" + process.env.WEBHOOK_SECRET, webhookCallback(bot, "express"));

app.listen(443, () => {
  console.log("Webhook server running on port 443");
});

// הגדרת URL ה-webhook בטלגרם
await bot.api.setWebhook(`https://your-domain.com/webhook/${process.env.WEBHOOK_SECRET}`, {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});
```

**הגדרת webhook ב-Telegraf:**

```typescript
// אפשרות 1: שרת webhook מובנה
bot.launch({
  webhook: {
    domain: "https://your-domain.com",
    port: 443,
    secretToken: process.env.WEBHOOK_SECRET_TOKEN,
  },
});

// אפשרות 2: אינטגרציה עם Express
import express from "express";
const app = express();
app.use(bot.webhookCallback("/webhook"));
app.listen(443);
await bot.telegram.setWebhook("https://your-domain.com/webhook", {
  secret_token: process.env.WEBHOOK_SECRET_TOKEN,
});

// אפשרות 3: Lambda/serverless
export const handler = bot.createWebhook({ domain: "https://your-domain.com" });
```

**הגדרת webhook ב-python-telegram-bot:**

```python
application = ApplicationBuilder().token(TOKEN).build()
# ... הוספת handlers ...

application.run_webhook(
    listen="0.0.0.0",
    port=443,
    url_path="webhook",
    webhook_url="https://your-domain.com/webhook",
    secret_token=os.getenv("WEBHOOK_SECRET_TOKEN"),
)
```

### מעבר בין מצבים

להסרת webhook (חזרה ל-polling):

```
GET https://api.telegram.org/bot<token>/deleteWebhook
```

או בקוד:
```typescript
await bot.api.deleteWebhook(); // grammY
await bot.telegram.deleteWebhook(); // Telegraf
```

## טיפול בהודעות בעברית

### בעיית הטקסט הדו-כיווני

עברית היא RTL, אבל הודעות בטלגרם מערבבות לעתים קרובות עברית עם תוכן LTR (מילים באנגלית, כתובות URL, מספרים, קוד). זה יוצר בעיות רינדור:

1. **מקלדות אינליין עם כיוונים מעורבים** - כפתור שמציג "שלח 5 הודעות" עלול לרנדר את המספר במיקום הלא נכון.
2. **קידוד callback data** - שמרו callback data ב-ASCII/אנגלית. עברית ב-callback data מבזבזת את מגבלת 64 הבייטים.
3. **פרסור Markdown/HTML עם עברית** - סימני bold/italic יכולים להישבר עם שינוי כיוון RTL.

### פתרונות

**השתמשו בסימני כיווניות Unicode בעת ערבוב שפות:**

```typescript
const RTL_MARK = "\u200F"; // Right-to-Left Mark
const LTR_MARK = "\u200E"; // Left-to-Right Mark

// כפיית הקשר RTL לטקסט עברי שמכיל מספרים
await ctx.reply(`${RTL_MARK}סה"כ: ${LTR_MARK}₪150${RTL_MARK} לתשלום`);
```

**השתמשו ב-HTML parse mode (צפוי יותר מ-Markdown ל-RTL):**

```typescript
await ctx.reply(
  `<b>סיכום הזמנה</b>\n` +
  `מוצר: חולצה\n` +
  `מחיר: ₪150\n` +
  `כמות: 3`,
  { parse_mode: "HTML" }
);
```

**למה HTML ולא Markdown לעברית:**
- סימני `*bold*` ו-`_italic_` של Markdown מתבלבלים מסידור מחדש של RTL
- תגיות HTML (`<b>`, `<i>`) חד-משמעיות ללא קשר לכיוון הטקסט
- MarkdownV2 דורש escaping של תווים רבים שמופיעים בטקסט עברי

### פקודות עבריות

פקודות טלגרם חייבות להתחיל ב-`/` ולהשתמש בתווים לטיניים. ל-UX עברי, ספקו את שניהם:

```typescript
// רשמו פקודות לטיניות ב-BotFather
// אבל גם טפלו בטריגרים עבריים
bot.command("help", handleHelp);
bot.hears("עזרה", handleHelp);
bot.hears("תפריט", handleMenu);

// או השתמשו ב-regex להתאמה גמישה
bot.hears(/^(help|עזרה)$/i, handleHelp);
```

### כפתורי מקלדת עברית (ReplyKeyboard)

למשתמשים לא טכניים, מקלדת reply עם כפתורים בעברית נגישה יותר מפקודות slash:

```typescript
import { Keyboard } from "grammy";

const hebrewMenu = new Keyboard()
  .text("תפריט ראשי").text("עזרה").row()
  .text("ההזמנות שלי").text("צור קשר")
  .resized()    // התאמה לתוכן
  .persistent(); // שמירה על הנראות

await ctx.reply("בחרו מהתפריט:", { reply_markup: hebrewMenu });
```

### זיהוי לפי מספר טלפון ישראלי

הדרך הנקייה ביותר לזהות משתמש לפי מספר טלפון ישראלי היא כפתור `request_contact` במקלדת reply. המשתמש לוחץ, טלגרם מציג חלון אישור, ובאישור הבוט מקבל שדה `contact` עם `phone_number` מאומת. מספרים ישראליים יכולים להגיע עם `+972` או בלעדיו, אז תמיד מנרמלים.

```typescript
import { Keyboard } from "grammy";

bot.command("verify", async (ctx) => {
  const kb = new Keyboard()
    .requestContact("שתפו את מספר הטלפון שלי")
    .resized()
    .oneTime();
  await ctx.reply("כדי להמשיך, שתפו את מספר הטלפון שלכם:", { reply_markup: kb });
});

function normalizeIsraeliPhone(raw: string): string | null {
  // הסרת רווחים, מקפים וסוגריים
  let p = raw.replace(/[\s\-()]/g, "");
  // +972XXXXXXXXX, 972XXXXXXXXX, 0XXXXXXXXX -> +972XXXXXXXXX
  if (p.startsWith("+972")) return p;
  if (p.startsWith("972")) return "+" + p;
  if (p.startsWith("0")) return "+972" + p.slice(1);
  return null;
}

bot.on("message:contact", async (ctx) => {
  const contact = ctx.message.contact;
  // אבטחה: לוודא שהאיש קשר שייך לשולח עצמו, לא למישהו אחר שהוא הדביק
  if (contact.user_id !== ctx.from.id) {
    return ctx.reply("אנא שתפו את המספר שלכם, לא של אדם אחר.");
  }
  const phone = normalizeIsraeliPhone(contact.phone_number);
  if (!phone) {
    return ctx.reply("המספר שהתקבל לא נראה כמספר ישראלי תקין.");
  }
  await ctx.reply(`תודה! המספר שלך נשמר: ${phone}`);
});
```

## מגבלות קצב וגדלי קבצים

טלגרם אוכפת מגבלות קשיחות על תעבורה יוצאת. חריגה מחזירה HTTP 429 עם `retry_after`; התעלמות תוביל לחנק או חסימה של הבוט.

**קצב הודעות יוצאות:**
- **30 הודעות/שנייה** גלובלי, על פני כל הצ'אטים
- **הודעה אחת לשנייה** לכל צ'אט בודד (DM או קבוצה)
- **20 הודעות/דקה** לקבוצה (שידור לאותה קבוצה)

ל-grammY מומלץ להשתמש ב-[`@grammyjs/transformer-throttler`](https://github.com/grammyjs/transformer-throttler) שיכניס לתור ויכבד את המגבלות אוטומטית. ב-Telegraf וב-python-telegram-bot ממשים token bucket לפי צ'אט או משתמשים בתור חיצוני (BullMQ, Celery).

**גדלי קבצים:**
- **העלאת קובץ מהבוט:** 50 MB (שרת Bot API ברירת מחדל)
- **הורדת קובץ מהבוט:** 20 MB
- **בוט פרימיום עם שרת Bot API מקומי:** עד **2 GB**

להעלאה או הורדה מעל 50 MB, מריצים [שרת Bot API](https://github.com/tdlib/telegram-bot-api) משלכם ומפנים את הבוט אליו דרך `apiRoot` (grammY) / `telegram.apiRoot` (Telegraf) / `base_url` (python-telegram-bot). שרת Bot API מקומי הוא גם דרישה קשיחה לשידור עדכוני אודיו/וידאו חיים ולמדיה גדולה במיוחד בקבוצות.

## תזמון משימות לפי Asia/Jerusalem

בוטים שצריכים לפעול ב"9 בבוקר שעון ישראל" חייבים להגדיר אזור זמן ישראלי במפורש, לא לפי השרת ולא UTC. בישראל יש מעברי שעון קיץ/חורף שלא תואמים לאזורי ענן (פרנקפורט, us-east-1), אז היסט UTC קבוע יסטה בשעה פעמיים בשנה.

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

**Node (grammY/Telegraf עם `node-cron` או `croner`):**

```typescript
import cron from "node-cron";

cron.schedule("0 9 * * *", sendMorningDigest, {
  timezone: "Asia/Jerusalem",
});
```

הימנעו מ-`setInterval` למשימות יומיות, הוא סוטה בשעה פעמיים בשנה במעבר השעון.

## מצב Bot Business

ב-Bot API 7.2 הושק **Telegram Business**, שמאפשר למשתמש פרימיום של טלגרם לחבר בוט לחשבון האישי שלו, כך שהבוט קורא ועונה להודעות אישיות בשמו. משתמשי פרימיום ישראלים יכולים להפעיל את זה בהגדרות > Telegram Business > צ'אטבוטים, ולהדביק את ה-`@username` של בוט מאושר.

כשהמשתמש מחבר את הבוט, הבוט מקבל עדכון `business_connection` עם `business_connection_id`. כל הודעה שמגיעה לאחד הצ'אטים המחוברים נושאת את אותו `business_connection_id`, וכל קריאה יוצאת (`sendMessage`, `editMessageText` וכו׳) חייבת להחזיר אותו כדי שטלגרם תנתב את התשובה דרך החשבון של המשתמש ולא של הבוט.

מה הבוט יכול לעשות אחרי החיבור:
- לקרוא ולענות להודעות DM נכנסות בשם משתמש ה-Telegram Business.
- לקבל את רשימת הצ'אטים שהמשתמש מתכתב איתם (`getBusinessConnection`, אחר כך `getBusinessAccountChats`).
- לשלוח, לערוך ולמחוק הודעות בשם המשתמש (לפי הרשאות לכל צ'אט שטלגרם חושפת).

```typescript
// תפיסת החיבור (שומרים את business_connection_id לפי המשתמש)
bot.on("business_connection", async (ctx) => {
  const conn = ctx.businessConnection;
  console.log(`Connected to business user ${conn.user.id}, can_reply=${conn.can_reply}`);
  // לשמור את conn.id לפי conn.user.id
});

// תשובה להודעת business נכנסת, חייבים לכלול business_connection_id
bot.on("business_message", async (ctx) => {
  await ctx.api.sendMessage(ctx.businessMessage.chat.id, "אני אחזור אליך תוך מספר דקות", {
    business_connection_id: ctx.businessMessage.business_connection_id,
  });
});
```

שימושי לבעלי עסקים קטנים בישראל (אופטיקאים, סטודיות יוגה, סוכני ביטוח) שרוצים מענה אוטומטי בטלגרם האישי שלהם בשעות לא-פעילות, בלי להעביר לקוחות לבוט נפרד.

הפניה: [https://core.telegram.org/bots/business](https://core.telegram.org/bots/business)

## API תשלומים

לטלגרם יש שלושה מסלולי תשלום, בוחרים לפי מה שמוכרים:

- **Telegram Stars (XTR)** - למוצרים דיגיטליים, שירותים ותוכן בתוך Mini App. הושק בערך ב-Bot API 7.4 (2024). לא צריך ספק תשלום חיצוני. משתמשים ישראלים רואים את המחיר בשקלים בחלון הרכישה (טלגרם ממירה אוטומטית לפי האזור של ה-App Store / Google Play של המשתמש), כלומר חשבונית של 100 כוכבים מוצגת כשווה ערך בשקלים בזמן הרכישה.
- **Stars subscriptions** - מנויים מתחדשים (התווסף מאוחר יותר ב-2024). אותו מטבע `XTR`, עם `subscription_period` בחשבונית. משתמשים יכולים לבטל דרך הגדרות > Stars.
- **Gifts API** (`sendGift`, `convertGiftToStars`) - הבוט שולח מתנה למשתמש; המקבל יכול להשאיר אותה על הפרופיל או להמיר חזרה לכוכבים.
- **paid_media** - מצמידים מחיר בכוכבים לתמונה/וידאו בצ'אטים וערוצים (המקבל משלם כוכבים כדי לפתוח).
- **ספקי תשלום מסורתיים** (Stripe LIVE/TEST וכו׳) עדיין נתמכים למוצרים פיזיים ושירותים לא-דיגיטליים. מגדירים provider token דרך BotFather תחת `/mybots > Payments`, ומעבירים אותו כ-`provider_token` עם מטבע פיאט (`ILS`, `USD`).

### יצירת חשבונית

**grammY:**

```typescript
bot.command("buy", async (ctx) => {
  await ctx.replyWithInvoice(
    "מנוי פרימיום",              // כותרת
    "גישה לכל התכונות למשך חודש",  // תיאור
    "premium_monthly",            // payload (מזהה פנימי שלכם)
    "XTR",                        // מטבע (XTR = Telegram Stars)
    [{ label: "מנוי חודשי", amount: 100 }], // מחירים (100 כוכבים)
  );
});

// טיפול בתשלום מוצלח
bot.on("message:successful_payment", async (ctx) => {
  const payment = ctx.message.successful_payment;
  console.log(`Payment received: ${payment.total_amount} ${payment.currency}`);
  console.log(`Payload: ${payment.invoice_payload}`);

  await ctx.reply("!תודה על הרכישה! המנוי הופעל");
});

// טיפול ב-pre-checkout query (חובה לענות תוך 10 שניות)
bot.on("pre_checkout_query", async (ctx) => {
  // בדיקת ההזמנה, מלאי וכו׳
  await ctx.answerPreCheckoutQuery(true);
  // או דחייה: await ctx.answerPreCheckoutQuery(false, "מוצר אזל מהמלאי");
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

**כללים קריטיים לתשלומים:**
- חובה לענות ל-`pre_checkout_query` תוך 10 שניות, אחרת התשלום נכשל.
- סכומי Telegram Stars (XTR) הם במספרים שלמים (ללא עשרוניות).
- למוצרים פיזיים או שירותים לא-דיגיטליים, צריך ספק תשלום צד שלישי (Stripe וכו׳) שמוגדר דרך BotFather תחת `/mybots > Payments`.
- החזרים מתבצעים דרך מתודת `refundStarPayment`, לא ידנית.

### מנויים מתחדשים ב-Stars

מעבירים `subscription_period` (בשניות, כרגע 30 יום בלבד) בחשבונית כדי להפוך תשלום חד-פעמי בכוכבים למנוי מתחדש. טלגרם מטפלת במחזור החיוב, והבוט מקבל עדכון `successful_payment` בכל חידוש.

```typescript
await ctx.replyWithInvoice(
  "מנוי פרימיום",
  "גישה לכל התכונות, מתחדש מדי חודש",
  "premium_sub_v1",
  "XTR",
  [{ label: "מנוי חודשי", amount: 100 }],
  {
    subscription_period: 30 * 24 * 60 * 60, // 30 יום, היחיד שנתמך כרגע
  },
);
```

משתמשים מנהלים ומבטלים מנויים דרך הגדרות > Stars > המנויים שלי. האזינו ל-`message:successful_payment` בכל חידוש כדי להאריך גישה ב-DB.

### Gifts API

`sendGift` שולח מדבקת מתנה למשתמש (משלמים בכוכבים מיתרת הבוט). המקבל יכול להציג אותה על הפרופיל או להפעיל `convertGiftToStars` כדי להחזיר אותה לכוכבים. שימושי לתוכניות נאמנות, הגרלות ומבצעים.

```typescript
await bot.api.sendGift({
  user_id: ctx.from.id,
  gift_id: "<אחד מה-IDs ש-getAvailableGifts מחזיר>",
  text: "תודה שאתם איתנו!", // הודעה אופציונלית
});
```

תמיד קוראים ל-`getAvailableGifts` קודם כדי לראות את הקטלוג ואת המחירים העדכניים.

### paid_media

מצמידים מחיר בכוכבים לתמונה או וידאו בצ'אט/ערוץ; המקבל משלם כוכבים כדי לפתוח. משתמשים ב-`sendPaidMedia` (או בשדה `paid_media` במתודות `sendMessage`) עם `star_count` למחיר.

## Mini Apps (WebApp)

Mini Apps מאפשרים להטמיע ממשקי ווב מלאים בתוך טלגרם. הבוט פותח דף ווב, והדף יכול לשלוח נתונים בחזרה לבוט.

### הגדרת כפתור Mini App

**grammY:**

```typescript
import { InlineKeyboard } from "grammy";

bot.command("app", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .webApp("פתח אפליקציה", "https://your-app.com/mini-app");

  await ctx.reply("לחצו לפתיחת האפליקציה:", { reply_markup: keyboard });
});
```

**שימוש ב-MenuButton (כפתור קבוע ליד שדה הטקסט):**

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

### קבלת נתונים מ-Mini App

כשהמשתמש מבצע פעולה ב-Mini App ושולח נתונים בחזרה:

**ב-Mini App (JavaScript בצד הדפדפן):**

```javascript
// Telegram WebApp SDK מוזרק על ידי טלגרם
const tg = window.Telegram.WebApp;

// שליחת נתונים בחזרה לבוט (סוגר את ה-Mini App)
tg.sendData(JSON.stringify({
  action: "order",
  items: ["item1", "item2"],
  total: 150,
}));

// או שימוש ב-MainButton ל-UX נקי יותר
tg.MainButton.text = "אישור הזמנה";
tg.MainButton.show();
tg.MainButton.onClick(() => {
  tg.sendData(JSON.stringify({ confirmed: true }));
});
```

**בבוט (קבלת הנתונים):**

```typescript
bot.on("message:web_app_data", async (ctx) => {
  const data = JSON.parse(ctx.message.web_app_data.data);
  console.log("Received from Mini App:", data);

  await ctx.reply(`הזמנה התקבלה! סה"כ: ₪${data.total}`);
});
```

### תכונות Mini Apps 2.0

Bot API 7.x ו-8.x הוסיפו אוסף יכולות "Mini Apps 2.0" שחשופות דרך `window.Telegram.WebApp`. כולן דורשות גרסאות עדכניות של טלגרם, ואין להן אפקט בגרסאות ישנות, אז כדאי לבדוק תמיכה לפני קריאה.

**אחסון בענן** (`window.Telegram.WebApp.CloudStorage`) - אחסון key-value לכל משתמש שנשמר בין סשנים ובין מכשירים. עד 1024 מפתחות למשתמש, 4 KB לערך. לא צריך backend בשביל העדפות פשוטות:

```javascript
const tg = window.Telegram.WebApp;
tg.CloudStorage.setItem("last_order_id", "12345");
tg.CloudStorage.getItem("last_order_id", (err, value) => {
  console.log("Restored:", value);
});
```

**אימות ביומטרי** (`window.Telegram.WebApp.BiometricManager`) - מבקשים מהמשתמש Face ID / Touch ID / טביעת אצבע כדי לחסום פעולות רגישות בתוך ה-Mini App. שימושי לאישור רכישות גדולות בכוכבים או שחרור טוקני תשלום שמורים:

```javascript
tg.BiometricManager.init(() => {
  if (tg.BiometricManager.isBiometricAvailable) {
    tg.BiometricManager.authenticate({ reason: "אישור תשלום" }, (success) => {
      if (success) submitOrder();
    });
  }
});
```

**שירות מיקום** (`window.Telegram.WebApp.LocationManager`) - בקשת קואורדינטות GPS בהרשאה מפורשת. מתאים לזרימות "מצא את הסניף הקרוב" בבוטים של רשתות ישראליות.

**מצב מסך מלא** - `tg.requestFullscreen()` מרחיב את ה-Mini App לכל מסך הנייד. משלימים עם `tg.exitFullscreen()`.

**התקנה למסך הבית** - `tg.addToHomeScreen()` מוסיף קיצור ל-Mini App על המסך הראשי באנדרואיד (ב-iOS מוצגות כרגע הוראות ידניות). עובד אחרי ש-`tg.checkHomeScreenStatus()` מאשר שהאפליקציה זמינה לכך.

**הפניה:** [https://core.telegram.org/bots/webapps](https://core.telegram.org/bots/webapps)

### אימות Mini App

תמיד אמתו את ה-`initData` בשרת כדי לוודא שהבקשה באמת מגיעה מטלגרם:

```typescript
import crypto from "crypto";

function validateInitData(initData: string, botToken: string): boolean {
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  params.delete("hash");

  // מיון פרמטרים אלפביתי
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

## דיפלוי

### Vercel Serverless (grammY)

**`api/webhook.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

// רישום כל ה-handlers
bot.command("start", (ctx) => ctx.reply("!שלום"));
// ... handlers נוספים

export default webhookCallback(bot, "std/http");
```

**הגדרת webhook אחרי הדיפלוי:**

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=https://your-app.vercel.app/api/webhook&secret_token=${SECRET}"
```

**אזהרות Vercel:**
- לפונקציות Vercel יש timeout של 10 שניות בתוכנית Hobby, 60 שניות ב-Pro. פעולות ארוכות ייכשלו.
- כל הרצה היא stateless. השתמשו באחסון חיצוני (Redis, database) לנתוני session.
- `webhookCallback("std/http")` של grammY הוא ה-adapter הנכון ל-Vercel.

### Cloudflare Workers (grammY)

**`src/index.ts`:**

```typescript
import { Bot, webhookCallback } from "grammy";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN);

    bot.command("start", (ctx) => ctx.reply("!שלום"));
    // ... handlers נוספים

    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

**אזהרות Cloudflare:**
- השתמשו ב-adapter `"cloudflare-mod"` (לא `"cloudflare"`).
- ל-Workers יש מגבלת זמן CPU של 30 שניות (מספיק לרוב פעולות הבוט).
- השתמשו ב-KV או D1 לשמירת מצב, לא בזיכרון.

### VPS עם systemd (כל פריימוורק)

לבוטים שצריכים long polling או חיבורים קבועים:

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
sudo journalctl -u telegram-bot -f  # צפייה בלוגים
```

## משאבים מצורפים

- [השוואת פריימוורקים](references/framework-comparison.md) - מטריצת תכונות מפורטת של grammY מול Telegraf מול python-telegram-bot

## שרתי MCP מומלצים

אין כרגע MCP ייעודי לטלגרם בספרייה.

## קישורי עזר

| מקור | URL |
|------|-----|
| Telegram Bot API changelog | https://core.telegram.org/bots/api-changelog |
| ערוץ BotNews של טלגרם | https://t.me/botnews |
| תיעוד grammY | https://grammy.dev/ |
| תיעוד python-telegram-bot | https://docs.python-telegram-bot.org/ |
| תיעוד Telegraf | https://telegraf.js.org/ |

## מלכודות נפוצות

אלה מצבי כשל שכיחים שסוכנים נתקלים בהם כשמייצרים קוד של בוטים לטלגרם:

1. **ערבוב בין API-ים של פריימוורקים.** grammY משתמש ב-`ctx.reply()`, Telegraf משתמש ב-`ctx.reply()` (נראה אותו דבר אבל Context שונה), python-telegram-bot משתמש ב-`update.message.reply_text()`. סוכנים מערבבים `ctx.reply()` לתוך קוד python-telegram-bot או משתמשים ב-`Markup` של Telegraf עם grammY.

2. **הגבלת פורט ב-webhook.** טלגרם שולח webhooks רק לפורטים 443, 80, 88 או 8443. סוכנים מגדירים webhooks על פורט 3000 או 8080, שנכשלים בשקט ללא שגיאה מצד טלגרם.

3. **שכחה לענות ל-callback queries.** כל עדכון `callback_query` חייב להיענות עם `answerCallbackQuery()` תוך 30 שניות, גם אם אין מה להציג. אי-מענה גורם לספינר טעינה קבוע על הכפתור של המשתמש. סוכנים מטפלים בלוגיקה אבל שוכחים את קריאת ה-answer.

4. **callback data חורג מ-64 בייטים.** סוכנים שמים מחרוזות בעברית, אובייקטי JSON או מזהים ארוכים ב-callback data. תווי עברית צורכים 2-3 בייטים כל אחד ב-UTF-8. השתמשו במפתחות אנגליים קצרים ושמרו נתונים מלאים ב-session/database.

5. **חוסר escaping ב-HTML parse mode.** כשמשתמשים ב-`parse_mode: "HTML"`, התווים `<`, `>` ו-`&` בטקסט שהמשתמש סיפק חייבים escaping. סוכנים מחזירים קלט משתמש במצב HTML בלי escaping, מה שגורם לשגיאות פרסור.

6. **Polling ו-webhook רצים במקביל.** אם שוכחים לקרוא ל-`deleteWebhook()` לפני הפעלת polling, הבוט לא מקבל עדכונים דרך polling. טלגרם שולח עדכונים רק לנקודת קצה אחת. זה כשל שקט.

7. **timeout של pre-checkout query.** ה-handler של `pre_checkout_query` חייב להגיב תוך 10 שניות. אם ה-handler עושה עבודה אסינכרונית (קריאות database, APIs חיצוניים) שלוקחת יותר מדי זמן, התשלום נכשל בשקט. שמרו על handler קליל.

8. **session ב-grammY בלי storage adapter.** ברירת המחדל של session store בזיכרון ב-grammY מתאפסת בכל הפעלה מחדש. לפרודקשן חובה להגדיר אחסון session חיצוני (Redis, Supabase וכו׳). סוכנים מדלגים על זה ותוהים למה sessions נעלמים.

9. **שינויי API בין Telegraf v4 ל-v3.** סוכנים שאומנו על דאטה ישן מייצרים קוד Telegraf v3 (`telegraf.startPolling()`, `telegraf.webhookCallback()`). ב-v4 זה `bot.launch()` ו-`bot.webhookCallback()`.

10. **מיגרציה ל-async ב-python-telegram-bot v20+.** גרסאות לפני v20 השתמשו ב-handlers סינכרוניים. v22.7 הוא async לחלוטין. סוכנים מייצרים קוד סינכרוני (`def handler` במקום `async def handler`) או משתמשים בקלאס `Updater` המיושן.

11. **סיוט escaping של Markdown בעברית.** MarkdownV2 דורש escaping ל: `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`. בטקסט עברי זה גורם לשגיאות בלי סוף. השתמשו ב-HTML parse mode במקום.

12. **חוסר error handler.** בלי `bot.catch()` (grammY) או error handler, שגיאות לא מטופלות מפילות את תהליך הבוט בשקט. במצב polling, זה הורג את הבוט. במצב webhook, טלגרם מנסה שוב את העדכון, ועלול לגרום ללולאת שגיאות אינסופית.

## דוגמאות

### דוגמה 1: בוט תפריט בעברית עם מקלדות אינליין

בוט תפריט מסעדה שמציג קטגוריות ופריטים בעברית:

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

### דוגמה 2: בוט Webhook על Vercel עם הודעות שגיאה בעברית

בוט webhook בפרודקשן שמדפלוי על Vercel ומטפל בשגיאות עם הודעות בעברית:

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

### דוגמה 3: python-telegram-bot עם תהליך שיחה ועברית

בוט Python שמממש טופס הזמנה רב-שלבי:

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

# מצבי שיחה
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

## פתרון בעיות

### "Conflict: terminated by other getUpdates request"

עוד מופע של הבוט שלכם רץ (אולי תהליך קודם, שרת שני, או webhook שנשאר). תיקון:
1. עצרו את כל המופעים האחרים של הבוט.
2. קראו ל-`deleteWebhook` כדי לנקות webhook שהוגדר.
3. הפעילו את הבוט מחדש.

### הבוט לא מקבל עדכונים

1. בדקו אם webhook מוגדר: `GET https://api.telegram.org/bot<token>/getWebhookInfo`
2. אם `url` מוגדר ואתם רוצים polling, קראו ל-`deleteWebhook` קודם.
3. אם משתמשים ב-webhooks, וודאו שה-URL נגיש ציבורית ועל פורט תקף (443, 80, 88, 8443).
4. בדקו אם המשתמש חסם את הבוט או הסיר מהקבוצה.

### "Bad Request: can't parse entities"

יש HTML/Markdown לא תקין בהודעה. סיבות נפוצות:
- `<`, `>`, `&` ללא escaping במצב HTML
- תווים מיוחדים ללא escaping במצב MarkdownV2
- תגיות סגירה חסרות ב-HTML

תיקון: עשו escape לקלט משתמש לפני הכללה בהודעות מפורמטות:

```typescript
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
```

### "Forbidden: bot was blocked by the user"

המשתמש חסם את הבוט. זה נורמלי. טפלו בזה בצורה חלקה:

```typescript
try {
  await bot.api.sendMessage(userId, "הודעה");
} catch (e) {
  if (e instanceof GrammyError && e.error_code === 403) {
    // המשתמש חסם את הבוט, הסירו מרשימת המשתמשים הפעילים
    console.log(`User ${userId} blocked the bot`);
  }
}
```

### Webhook מחזיר 502/504 timeout

ה-handler שלכם לוקח יותר מדי זמן. טלגרם מצפה לתשובה תוך כ-60 שניות ל-webhooks (אבל בפועל כדאי לכוון מתחת ל-30 שניות). פתרונות:
- העבירו עיבוד כבד לתור משימות ברקע.
- שלחו תשובה מיידית "מעבד...", ועדכנו כשסיימתם.
- בפלטפורמות serverless (Vercel Hobby), ה-timeout יכול להיות נמוך כמו 10 שניות.

### טקסט עברי מופיע הפוך בלוגים/קונסול

זו בעיית תצוגה בטרמינלים שלא תומכים ב-RTL, לא בעיה בנתונים עצמם. הטקסט שמור נכון ומרונדר כראוי בטלגרם. אל תנסו "לתקן" את זה על ידי היפוך מחרוזות.

### כפתורי מקלדת אינליין לא מתעדכנים

אחרי `editMessageText`, המקלדת הישנה נשארת אלא אם מעבירים `reply_markup` בקריאת העריכה. תמיד העבירו את המקלדת החדשה (או `InlineKeyboard()` ריק כדי להסיר):

```typescript
await ctx.editMessageText("עודכן!", {
  reply_markup: new InlineKeyboard(), // מסיר מקלדת
});
```
