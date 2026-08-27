---
name: telegram-bot-builder
description: "בנו בוטים לטלגרם עם grammY, Telegraf או python-telegram-bot. מכסה Bot API v10.3, webhooks מול polling, מקלדות אינליין, פקודות, middleware, תשלומים ב-Telegram Stars + Gifts, Mini Apps 2.0, מצב Bot Business וטיפול בהודעות בעברית עם RTL. השתמשו כשבונים בוט טלגרם, מגדירים webhooks, מטפלים בהודעות בעברית בתוך בוט, או משלבים תשלומים דרך טלגרם. אל תשתמשו לבוטים של וואטסאפ (השתמשו ב-israeli-whatsapp-business), בוטים קוליים (השתמשו ב-hebrew-voice-bot-builder), או עיצוב צ'אטבוטים כללי (השתמשו ב-hebrew-chatbot-builder)."
license: MIT
---

# בניית בוט טלגרם

בנו בוטים מוכנים לפרודקשן לשוק הישראלי עם grammY, Telegraf או python-telegram-bot. המדריך מכסה Bot API v10.3 (שוחרר ב-24.08.2026), ארכיטקטורות webhook ו-polling, מקלדות אינליין, טיפול בטקסט עברי/RTL, תשלומים ב-Telegram Stars ו-Gifts, Mini Apps 2.0, מצב Bot Business, ודיפלוי לפלטפורמות serverless.

## בעיה

בניית בוטים לטלגרם לקהל ישראלי מביאה כמה דברים שסוכנים נכשלים בהם שוב ושוב:

1. **בלבול בין פריימוורקים** - grammY, Telegraf ו-python-telegram-bot יושבים על גרסאות Bot API שונות ומתערבבים רע. סוכנים מערבבים את ה-API-ים או פולטים תבניות מיושנות.
2. **הגדרת Webhook שגויה** - ברירת המחדל היא polling, ואז ההגדרה לפרודקשן יוצאת שגויה: מגבלת הפורטים (רק 443, 80, 88, 8443), SSL, ואימות secret token.
3. **שיבוש טקסט עברי/RTL** - טקסט דו-כיווני נשבר במקלדות אינליין, ב-callback data ובהודעות מפורמטות כשמתעלמים מתווי הכיווניות של Unicode.
4. **חוסרים בתשלומים** - ל-Telegram Stars יש כללי חשבונית שונים מספקי פיאט, וסוכנים מייצרים קוד תשלומים מיושן.
5. **תקשורת לקויה עם Mini App** - ערוץ ההחזרה תלוי באופן שבו האפליקציה נפתחה, ו-`sendData` אינו זמין מפתיחה בכפתור אינליין.
6. **סחיפת גרסאות** - ה-Bot API משתחרר כמה פעמים בשנה ומודלים לומדים תמונת מצב קפואה. הסקיל הזה אומת מול Bot API 10.3 ב-27.08.2026; בדקו את ה-changelog לפני שסומכים על טענה תלוית גרסה כאן.

## בחירת פריימוורק

בוחרים לפי השפה, יעד הדיפלוי וגרסת Bot API הנדרשת:

| תכונה | grammY v1.46.0 | Telegraf v4.16.3 | python-telegram-bot v22.8 |
|--------|----------------|-------------------|---------------------------|
| שפה | TypeScript/JS | TypeScript/JS | Python 3.10+ |
| גרסת Bot API | עדכנית (v10.3) | v7.1 | v10.0 |
| התקנה | `npm install grammy` | `npm install telegraf` | `pip install python-telegram-bot` |
| פלאגינים | עשיר (sessions, menus, conversations, i18n) | בינוני (scenes, sessions) | הרחבות (JobQueue, persistence) |
| serverless | Vercel, CF Workers, Deno Deploy, Supabase Edge, Fly.io | Express/Fastify/Lambda | ASGI, webhook ידני |
| middleware | Composer (Koa) | Composer (Koa) | Handler groups עם filters |
| Long polling | `bot.start()` | `bot.launch()` | `application.run_polling()` |
| webhook | `webhookCallback()` | `bot.launch({ webhook })` | `application.run_webhook()` |
| כדאי ל... | פרויקטים חדשים, serverless, API עדכני | אפליקציות Express/Fastify קיימות | צוותי Python ו-ML |

השוואה מלאה: [references/framework-comparison.md](references/framework-comparison.md).

**איך בוחרים:**
- צריכים פיצ'רים של Bot API v10.x (Stars subscriptions, Gifts, Bot Business, Mini Apps 2.0, הודעות אפמרליות)? **grammY** הוא היחיד מהשלושה שנמצא כרגע על 10.3. python-telegram-bot על 10.0, ולכן המשטח האפמרלי של 10.2 וכל מה שב-10.3 דורשים שם קריאות API גולמיות.
- כבר יש שרת Express/Fastify? **Telegraf** משתלב חלק, אבל הוא רדום: הגרסה האחרונה 4.16.3 היא מ-29.02.2024 (Bot API 7.1) והוא לא יקבל דבר מ-10.x. לחדש עדיף grammY.
- צוות Python או פייפליין ML? **python-telegram-bot** הבחירה היחידה.
- Vercel, Cloudflare Workers או Deno? ל-**grammY** יש adapters מובנים.

## מה השתנה ב-Bot API 10.3 (24 באוגוסט 2026)

מי שלמד את המשטח הזה על 10.2 צריך לדעת שארבעה דברים זזו.

- **הודעות אפמרליות שונו.** גרסה 10.2 הוסיפה `receiver_user_id` ו-`callback_query_id` ל-`sendMessage` ולשתים עשרה מתודות שליחה נוספות. **גרסה 10.3 החליפה את שתיהן באובייקט אחד, `ephemeral_message_parameters`** (המחלקה `EphemeralMessageParameters`). קוד שנכתב לפי 10.2 נשבר. האובייקט החדש נושא גם את `replace_callback_query_message`, שמציג את ההודעה האפמרלית במקום המקורית ולא כהודעה נוספת.
- **מקלדות קיבלו `disabled` / `DisabledButton` ו-`force_reply`.** ר' מקלדות אינליין למטה.
- **`can_send_welcome_messages`** נוספה למחלקות `ChatAdministratorRights` ו-`ChatMemberAdministrator` ולמתודה `promoteChatMember`. מי שמקדם מנהלים בקוד, ההרשאה הזו קיימת עכשיו.
- **אפשר לעצור יצירת טיוטה.** `sendMessageDraft` ו-`sendRichMessageDraft` קיבלו `can_stop` ו-`keep_on_stop`, והעדכון `MessageGenerationStopped` (השדה `stopped_message_generation` ב-`Update`) נורה כשהמשתמש עוצר. **מי שמזרים תשובת AI לתוך טיוטה חייב לטפל בו**, אחרת ממשיכים לייצר ולחייב משתמש שכבר לחץ עצור.

גם Rich Messages קיבלו כפתורים (`RichMessageButton`, `RichTextButton`, `RichBlockButtons`), בלוק מסמך, וציטוט מתרחב.

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
- מחליפים טוקן עם `/token` ב-BotFather (מהתיעוד: אם הטוקן נחשף או אבד, משתמשים בפקודה `/token` כדי לייצר חדש).
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

## מצב פרטיות בקבוצות

הסיבה הנפוצה ביותר ל"הבוט שלי בקבוצה לא מקבל כלום". **מצב פרטיות דלוק כברירת מחדל לכל בוט שמתווסף לקבוצה.** במצב הזה הבוט רואה רק:

- פקודות שמופנות אליו מפורשות (`/command@this_bot`).
- פקודות כלליות כמו `/start`, אבל רק אם הוא היה הבוט האחרון ששלח הודעה בקבוצה.
- הודעות שנשלחו דרכו ב-inline.
- תשובות להודעות שלו עצמו.

ללא קשר למצב הפרטיות, בוט תמיד מקבל הודעות שירות, את כל ההודעות מצ'אטים פרטיים, ואת כל ההודעות מערוצים שהוא חבר בהם.

שתי דרכים לפתור, לפי סדר עדיפות:

1. **מוסיפים את הבוט לקבוצה כאדמין.** אדמינים מקבלים כל הודעה, בלי לשנות שום הגדרה.
2. **מכבים את מצב הפרטיות** עם `/setprivacy` ב-BotFather. **חייבים אחר כך להסיר את הבוט מהקבוצה ולהוסיף אותו מחדש כדי שהשינוי ייכנס לתוקף**, וזה השלב שרוב האנשים מפספסים. טלגרם ממליצה על זה רק כשאין ברירה; ברוב המקרים force reply פותר את אותה בעיה.

משתמשים יכולים לראות את הגדרת הפרטיות הנוכחית של בוט ברשימת חברי הקבוצה, כך שאפשר לבדוק את זה בלי לגעת בקוד.

## הקמת פרויקט

סקלטים מינימליים ורצים לשלושת הפריימוורקים (פקודות התקנה, `bot.ts` / `bot.py`, טיפול בשגיאות, כיבוי מסודר) נמצאים ב-[references/quickstarts.md](references/quickstarts.md).

שני דברים שחייבים להיות בכל סקלטון, בכל פריימוורק:
- **handler לשגיאות.** בלעדיו הבוט קורס בשקט ב-rejection הראשון שלא נתפס (`bot.catch()` ב-grammY וב-Telegraf, `application.add_error_handler()` ב-python-telegram-bot).
- **קריאת הטוקן מהסביבה**, אף פעם לא כמחרוזת בקוד. נכשלים מהר בעלייה אם `BOT_TOKEN` לא מוגדר.

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

**חוקי callback data:** מקסימום **64 בייטים**, לא תווים. עברית היא 2 בייטים לתו ב-UTF-8, כלומר לכל היותר 32 תווים. משאירים עברית בטקסט הכפתור ומזהים אנגליים קצרים ב-callback data.

המקבילה ב-python-telegram-bot, כולל רישום ה-`CallbackQueryHandler`, נמצאת ב-[references/examples.md](references/examples.md).

**שתי תוספות של 10.3 שייכות לכל מקלדת שאתם בונים.** `InlineKeyboardButton` קיבל שדה **`disabled`** עם מחלקה נלווית **`DisabledButton`**, כך שאפשר להאפיר כפתור במקום, בלי לבנות מחדש את ה-markup. גם `InlineKeyboardMarkup` וגם `ReplyKeyboardMarkup` קיבלו **`force_reply`**, שהיה נגיש קודם רק דרך האובייקט הנפרד `ForceReply`. תמיכת הפריימוורקים מפגרת אחרי ה-API. grammY 1.46.0 מטפס את שניהם. python-telegram-bot 22.8 יושב על Bot API 10.0 והאובייקטים המוטפסים שלו דוחים ארגומנטים לא מוכרים, אז מגיעים אליהם דרך `Bot.do_api_request` ולא דרך הבנאי.

### תבניות Middleware

Middleware רץ לפני ה-handlers ונושא לוגים, הרשאות, הגבלת קצב ו-i18n. ב-grammY וב-Telegraf זו שרשרת בסגנון Koa (`bot.use(async (ctx, next) => ...)`); **ל-python-telegram-bot אין middleware** והוא משתמש בקבוצות handlers במקום (`group=-1` רץ לפני קבוצת ברירת המחדל 0). דוגמאות עובדות לשניהם, כולל שער `adminOnly`, נמצאות ב-[references/middleware.md](references/middleware.md).

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

שני כללים מה-Bot API שקובעים אם תקבלו עדכונים בכלל:

- **השיטות סותרות זו את זו.** מהתיעוד: יש שתי דרכים מוציאות זו את זו לקבל עדכונים, `getUpdates` מצד אחד ו-webhooks מצד שני. webhook מוגדר מרעיב את ה-polling בשקט, אז קוראים ל-`deleteWebhook` לפני מעבר ל-polling.
- **עדכונים שלא נמסרו נמחקים אחרי 24 שעות.** מהתיעוד: עדכונים נשמרים בשרת עד שהבוט מקבל אותם, אך לא יותר מ-24 שעות. בוט שהיה מושבת סוף שבוע לא יקבל את הצבר.

**השדה `allowed_updates` הוא opt-out, עם שלושה חריגים שהם opt-in.** השמטה שלו (או רשימה ריקה) מוסרת כל סוגי העדכונים **חוץ מ**-`chat_member`, `message_reaction` ו-`message_reaction_count`. אם אתם מחווטים טיפול בריאקציות או בחברות בקבוצה ולא מקבלים כלום, זו הסיבה: פרטו אותם מפורשות ב-`allowed_updates` ב-`setWebhook` / `getUpdates`.

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

הגדרות webhook ל-Telegraf ול-python-telegram-bot (שרת מובנה, שילוב עם Express, handler ל-Lambda, `run_webhook`) נמצאות ב-[references/deployment.md](references/deployment.md). שימו לב ש-`application.run_webhook()` דורש את התוספת `[webhooks]`, והוא נכשל בזמן ריצה אחרי `pip install python-telegram-bot` רגיל.

### אימות Webhook

תמיד מוודאים שכותרת `X-Telegram-Bot-Api-Secret-Token` תואמת ל-secret token שלכם. שלושת הפריימוורקים תומכים בזה דרך הפרמטר `secret_token` ב-`setWebhook`.

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

הזרימה המלאה (כפתור `requestContact`, נרמול `+972`/`972`/`0`, ובדיקת האבטחה ש-`contact.user_id === ctx.from.id` כדי שלא ישתפו מספר של אדם אחר) נמצאת ב-[references/examples.md](references/examples.md).

## מגבלות קצב וגדלי קבצים

חריגה מחזירה HTTP 429 עם `retry_after`; התעלמות תוביל לחנק או חסימה של הבוט.

**קצב הודעות יוצאות:** כ-**30 הודעות/שנייה** לשידורים המוניים על פני כל הצ'אטים, **הודעה אחת לשנייה** לכל צ'אט בודד (פרצים קצרים עשויים לעבור לפני שמתחילות שגיאות 429), ו-**20 הודעות/דקה** לקבוצה.

**30 לשנייה זו שכבת החינם, אבל לשכבה בתשלום יש תנאי סף שכמעט אף בוט של עסק ישראלי לא עומד בו.** paid broadcasts מעלים את המגבלה ל-**1000 הודעות/שנייה** בעלות **0.1 כוכבים** לכל הודעה מעל 30 לשנייה, אבל כדי להפעיל את זה הבוט חייב **לפחות 100,000 כוכבים ביתרה ולפחות 100,000 משתמשים פעילים בחודש**. אל תתכננו פיזור סביב 1000 לשנייה לפני שבדקתם את שני המספרים. למי שמתחת לסף, העצה של ה-FAQ עצמו היא לפרוס את השידור על פני **8 עד 12 שעות**.

ל-grammY מומלץ [`@grammyjs/auto-retry`](https://github.com/grammyjs/auto-retry), שמכבד `retry_after` אוטומטית ב-429 (הפלאגין הישן `transformer-throttler` לא שוחרר מאז 2022). ל-python-telegram-bot יש `AIORateLimiter` מובנה דרך התוספת `[rate-limiter]`. ב-Telegraf ממשים token bucket לפי צ'אט או משתמשים בתור חיצוני (BullMQ, Celery).

**השדה `file_id` קשור למזהה בוט אחד.** מהתיעוד: מופע בדיקה לא יכול להשתמש במאגר `file_id` משותף כדי לשלוח מדיה במהירות, וצריך להעלות כל קובץ מחדש. אל תשמרו ערכי `file_id` ותשתמשו בהם מחדש בין טוקנים של בוטים שונים; העתקה מ-dev ל-prod נכשלת עם "wrong file identifier".

**גדלי קבצים:** העלאה **50 MB**, הורדה **20 MB** בשרת ברירת המחדל. **שרת Bot API מקומי** (כל בוט, בלי קשר לפרימיום) מוריד **ללא הגבלת גודל** ומעלה עד **2000 MB**.

להעלאה או הורדה מעל 50 MB, מריצים [שרת Bot API](https://github.com/tdlib/telegram-bot-api) משלכם ומפנים את הבוט אליו דרך `apiRoot` (grammY) / `telegram.apiRoot` (Telegraf) / `base_url` (python-telegram-bot).

**קוראים ל-`logOut` קודם, אחרת הבוט פשוט לא יקבל עדכונים.** מהתיעוד: חובה לנתק את הבוט לפני הרצה מקומית, אחרת אין ערובה שהוא יקבל עדכונים; אחרי ניתוק מוצלח אפשר להתחבר מיד לשרת מקומי, אבל אי אפשר לחזור לשרת הענן במשך 10 דקות. קחו בחשבון את חלון 10 הדקות הזה לפני שמנסים בפרודקשן. `close` משמש למעבר בין שרתים מקומיים, אחרי מחיקת ה-webhook.

## תזמון משימות לפי Asia/Jerusalem

בוטים שצריכים לפעול ב"9 בבוקר שעון ישראל" חייבים להגדיר אזור זמן ישראלי במפורש, לא לפי השרת ולא UTC. בישראל יש מעברי שעון קיץ/חורף שלא תואמים לאזורי ענן (פרנקפורט, us-east-1), אז היסט UTC קבוע יסטה בשעה פעמיים בשנה.

**python-telegram-bot (`JobQueue`):** דורש את התוספת `[job-queue]`. עם `pip install python-telegram-bot` רגיל, `application.job_queue` הוא `None` והקוד הזה זורק `AttributeError`. משתמשים ב-`zoneinfo` מהספרייה הסטנדרטית, לא ב-`pytz`, ש-PTB הפסיקה לדרוש החל מ-v20.

```python
from zoneinfo import ZoneInfo
from datetime import time

application.job_queue.run_daily(
    send_morning_digest,
    time=time(9, 0, tzinfo=ZoneInfo("Asia/Jerusalem")),
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

ב-Bot API 7.2 (31.03.2024) הוצג **Telegram Business**, שמאפשר למשתמש לחבר בוט לחשבון האישי שלו, כך שהבוט קורא ועונה להודעות אישיות בשמו. משתמשים ישראלים מפעילים את זה בהגדרות > Telegram Business > צ'אטבוטים, ומדביקים את ה-`@username` של בוט מאושר.

**חיבור בוט לא דורש מנוי פרימיום.** ב-Bot API 10.0 (מאי 2026) טלגרם אפשרה ל-Secretary Bots לנהל חשבונות בלי פרימיום (ב-changelog אותו סעיף מופיע עם המונח Business Bots), ו-core.telegram.org/api/business מציין שבוטים מחוברים זמינים גם למשתמשים ללא פרימיום. פרימיום עדיין נדרש לשאר פיצ'רי ה-Business (שעות פעילות, מיקום, תשובות מהירות, הודעות פתיחה והיעדרות, עמוד פתיחה מותאם), ולכן אל תתנו למסך ההצטרפות של הבוט לחסום משתמשים שאין להם פרימיום.

כשהמשתמש מחבר את הבוט, הבוט מקבל עדכון `business_connection` עם `business_connection_id`. כל הודעה שמגיעה לאחד הצ'אטים המחוברים נושאת את אותו `business_connection_id`, וכל קריאה יוצאת (`sendMessage`, `editMessageText` וכו׳) חייבת להחזיר אותו כדי שטלגרם תנתב את התשובה דרך החשבון של המשתמש ולא של הבוט.

מה הבוט יכול לעשות אחרי החיבור:
- לקרוא ולענות להודעות DM נכנסות בשם משתמש ה-Telegram Business.
- ההרשאה `rights.can_reply` מוגבלת ל**צ'אטים פרטיים שהתקבלה בהם הודעה ב-24 השעות האחרונות**. מענה אוטומטי בסדר, אבל ריקון תור מאוחר יותר ייכשל גם כש-`can_reply` דלוק.
- לשלוף את פרטי החיבור עצמו עם `getBusinessConnection`. אין מתודה שמחזירה את רשימת הצ'אטים של המשתמש, לומדים על צ'אט רק כשמגיעה בו הודעת `business_message`.
- לפעול בשם המשתמש לפי ההרשאות בשדה `rights` (מסוג `BusinessBotRights`). ה-setters לניהול החשבון הם **set בלבד** חוץ מאחד: ל-`setBusinessAccountName`, `setBusinessAccountUsername`, `setBusinessAccountBio` ו-`setBusinessAccountGiftSettings` אין מקבילת `remove*`. קיים רק `removeBusinessAccountProfilePhoto`.

המטפלים של grammY ללכידת `business_connection` (ההרשאות תחת `conn.rights`, אין שדה `conn.can_reply` ברמה העליונה) ולהחזרת `business_connection_id` בכל תשובה נמצאים ב-[references/examples.md](references/examples.md).

שימושי לבעלי עסקים קטנים בישראל (אופטיקאים, סטודיות יוגה, סוכני ביטוח) שרוצים מענה אוטומטי בטלגרם האישי בשעות לא-פעילות, בלי בוט נפרד.

הפניה: [Telegram Business](https://core.telegram.org/api/business) ו-[`BusinessConnection`](https://core.telegram.org/bots/api#businessconnection).

## API תשלומים

מסלולי התשלום, לפי מה שמוכרים:

- **Telegram Stars (XTR)** - למוצרים דיגיטליים, שירותים ותוכן ב-Mini App. Bot API 7.4 (28.05.2024), בלי ספק חיצוני. מה שמשתמש ישראלי משלם על חבילת כוכבים נקבע בחשבון ה-App Store או Google Play שלו, אז לעולם לא נוקבים מחיר קבוע בשקלים.
- **Stars subscriptions** - מנויים מתחדשים. אותו מטבע `XTR` עם `subscription_period` בקישור החשבונית; ביטול דרך הגדרות > Stars.
- **Gifts API** (`sendGift`) - הבוט שולח מתנה למשתמש, והמקבל שומר אותה על הפרופיל. הוא **לא יכול** להמיר מתנה שהבוט שלח בחזרה לכוכבים.
- **paid_media** - מצמידים מחיר בכוכבים לתמונה/וידאו בצ'אטים וערוצים (המקבל משלם כוכבים כדי לפתוח).
- **ספקי תשלום מסורתיים** (Stripe וכדומה) למוצרים פיזיים ושירותים לא-דיגיטליים. מגדירים provider token ב-BotFather תחת `/mybots > Payments`, ומעבירים `provider_token` עם מטבע פיאט (`ILS`, `USD`).

### יצירת חשבונית

**שלושה כללים נוקשים לחשבוניות כוכבים (`XTR`), שהפרה של כל אחד מהם נכשלת מול ה-API:**
- `provider_token` חייב להיות **מחרוזת ריקה** (הוא נועד רק לספקי מטבע רגיל).
- `prices` חייב להכיל **פריט אחד בדיוק**. פירוט מרובה שורות (מוצר + מס + משלוח) נדחה.
- `max_tip_amount` **לא נתמך** בכוכבים.

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

  await ctx.reply("תודה על הרכישה! המנוי הופעל");
});

// טיפול ב-pre-checkout query (חובה לענות תוך 10 שניות)
bot.on("pre_checkout_query", async (ctx) => {
  // בדיקת ההזמנה, מלאי וכו׳
  await ctx.answerPreCheckoutQuery(true);
  // או דחייה: await ctx.answerPreCheckoutQuery(false, "מוצר אזל מהמלאי");
});
```

מקבילה ב-python-telegram-bot: `references/examples.md`, דוגמה 4.

### מנויים מתחדשים ב-Stars

**השדה `subscription_period` אינו זמין ב-`sendInvoice` / `replyWithInvoice`.** העברה שלו לשם לא עושה כלום; משתמשים ב-`createInvoiceLink`. הוא גם פרמטר חובה ב-`createChatSubscriptionInviteLink`, מסלול נפרד למנויי ערוץ, ושדה ב-`SuccessfulPayment` וב-`StarTransaction`. במקום זה יוצרים קישור ושולחים אותו. הערך חייב להיות כרגע `2592000` (30 יום).

הקריאה המלאה נמצאת ב-[references/examples.md](references/examples.md), דוגמה 7.

משתמשים מנהלים ומבטלים מנויים דרך הגדרות > Stars > המנויים שלי.

**לא מנהלים חידושים לפי `message:successful_payment` בלבד.** גרסה 10.2 הוסיפה עדכון ייעודי: המחלקה **`BotSubscriptionUpdated`** והשדה **`subscription`** ב-`Update`. זה מה שמדווח על חידוש, ביטול או פקיעה. מטפל ב-`successful_payment` רואה את חיוב החידוש אבל לעולם לא רואה ביטול, כך שבוט שנשען רק עליו ממשיך לשרת משתמש שכבר ביטל.

### Gifts API

`sendGift` שולח מדבקת מתנה למשתמש, בתשלום כוכבים מיתרת הבוט. **המקבל לא יכול להמיר מתנה שהבוט שלח בחזרה לכוכבים**, בלשון התיעוד: "The gift can't be converted to Telegram Stars by the receiver". `convertGiftToStars` היא מתודה אחרת של בוט עסקי, שדורשת `business_connection_id` ואת ההרשאה `can_convert_gifts_to_stars` ופועלת על מתנות בבעלות חשבון עסקי מחובר. לעולם לא מבטיחים מסלול פדיון. מתנות הן מזכרת לנאמנות והגרלות, לא מטבע.

החתימה ב-grammY פוזיציונית: `(user_id, gift_id, other?)`. הקריאה המלאה ב-[references/examples.md](references/examples.md), דוגמה 8.

קוראים ל-`getAvailableGifts` קודם כדי לראות קטלוג ומחירים עדכניים.

### paid_media

מצמידים מחיר בכוכבים לתמונה או וידאו בצ'אט או בערוץ; המקבל משלם כוכבים כדי לפתוח. **`sendPaidMedia` היא הדרך היחידה לשלוח את זה.** אין פרמטר `paid_media` ב-`sendMessage` ולא באף מתודת שליחה אחרת: בתיעוד `paid_media` מופיע רק כשדה נכנס ב-`Message` (מסוג `PaidMediaInfo`), בתוך `PaidMediaInfo` עצמו, וב-`StarTransaction`. מגדירים `star_count` ב-`sendPaidMedia`, וקוראים רכישות דרך העדכון `purchased_paid_media`.

## Mini Apps (WebApp)

Mini Apps מטמיעים ממשקי ווב מלאים בתוך טלגרם: הבוט פותח דף, והדף שולח נתונים בחזרה.

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

**בוחרים את ערוץ ההחזרה הנכון, הם לא מתחלפים זה בזה.** המתודה `Telegram.WebApp.sendData()` זמינה, לשון התיעוד, רק ל-Mini Apps שנפתחו מכפתור מקלדת (כפתור `web_app` במקלדת reply, בצ'אטים פרטיים בלבד). **Mini App שנפתח מכפתור אינליין או מכפתור התפריט, כלומר בדיוק שתי הדרכים שהוצגו למעלה, לא יכול לקרוא ל-`sendData` בכלל.**

| דרך הפתיחה | איך הנתונים חוזרים |
|---|---|
| כפתור `web_app` במקלדת reply | `sendData()` ואז הודעת שירות `message:web_app_data` (בלי שרת) |
| כפתור אינליין, כפתור תפריט, קישור ישיר, מצב inline | שליחת POST ל-backend שלכם עם `initData`, עם אימות בצד השרת |

**`sendData` מוגבל ל-4096 בייטים** לפי התיעוד. עגלת קניות מסודרת עם שורות פריטים חוצה את זה בהזמנה אמיתית, בשקט. אם המטען יכול לגדול, משתמשים במסלול `initData` plus backend.

שני המסלולים מקצה לקצה (כפתור המקלדת, קריאות `sendData` ו-`MainButton` בצד הדפדפן, המטפל ב-`message:web_app_data`, ושליחת ה-POST עם `initData`) נמצאים ב-[references/mini-apps.md](references/mini-apps.md).

**לעולם לא סומכים על `initData` בלי לאמת את ה-HMAC בצד השרת.** הוא מגיע מהלקוח וקל לזייף אותו. המימוש המוקשח, כולל בדיקת הטריות של `auth_date`, נמצא באותו קובץ.

### תכונות Mini Apps 2.0 ואימות initData

משטח ה-"Mini Apps 2.0" של Bot API 7.x/8.x (מסך מלא, קיצור למסך הבית, חיישני מכשיר, ביומטריה, מיקום, סטטוס אימוג'י) ומימוש מלא ומוקשח של `validateInitData` נמצאים ב-[references/mini-apps.md](references/mini-apps.md).

**נעילת cross-origin, בתוקף מ-20.07.2026.** ב-Bot API 10.2 טלגרם הקשיחה את האבטחה של Mini Apps וחסמה שימוש במתודות של Mini App ממקורות (origins) שונים מהדומיין המקורי של האפליקציה. Mini App שמטמיע iframes של צד שלישי או מוגש מדומיין משני נשבר. אפשר לבטל את ההגנה דרך ה-Mini App של @BotFather, ואז האחריות על קישורים לא מהימנים עוברת אליכם.

כללים שאין עליהם ויתור אם אתם מגישים Mini App:
- **אף פעם לא בוטחים ב-`initData` בצד הלקוח.** מאמתים בשרת עם סכמת HMAC-SHA256 שמפתחה `WebAppData`, לפני שקוראים ממנו שדה משתמש כלשהו.
- **בודקים את `auth_date`.** בלי חלון טריות, מחרוזת `initData` שנלכדה מאמתת לנצח.
- **משווים hash בזמן קבוע** (`crypto.timingSafeEqual`), לא עם `===`.
- כל מתודות 2.0 הן no-op בגרסאות ישנות, אז בודקים תמיכה לפני קריאה.

## דיפלוי

שלושה יעדים נפוצים, לכל אחד מלכודות ספציפיות לפריימוורק. קונפיגורציות עובדות מלאות נמצאות ב-[references/deployment.md](references/deployment.md):

- **Vercel Serverless (grammY)** - משתמשים ב-`webhookCallback(bot, "std/http")`. חסר מצב, אז צריך אחסון סשנים חיצוני. מגבלות זמן הריצה משתנות לפי תוכנית, בדקו את המגבלות העדכניות של Vercel.
- **Cloudflare Workers (grammY)** - משתמשים במתאם `"cloudflare-mod"` (לא `"cloudflare"`). מגבלות ה-CPU משתנות לפי תוכנית. KV או D1 לאחסון.
- **VPS עם systemd** - כל פריימוורק, מתאים במיוחד ל-long polling. `Restart=always` יחד עם `EnvironmentFile=` לקובץ ה-`.env`.

## משאבים מצורפים

- [סקלטונים להתחלה](references/quickstarts.md) - שלדים רצים לשלושת הפריימוורקים
- [השוואת פריימוורקים](references/framework-comparison.md) - מטריצת תכונות ופלאגינים
- [Middleware](references/middleware.md) - תבניות middleware וקבוצות handlers
- [שיחות](references/conversations.md) - מתכונים לתהליכים רב-שלביים
- [Mini Apps](references/mini-apps.md) - משטח 2.0 ואימות initData
- [דיפלוי](references/deployment.md) - Vercel, Cloudflare Workers, systemd, הגדרות webhook
- [דוגמאות](references/examples.md) - חמישה בוטים עובדים מקצה לקצה
- [צ'קליסט תחום](references/domain-checklist.md) - חוזה הכיסוי של הסקיל

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

מצבי כשל שכיחים כשמייצרים קוד של בוטים לטלגרם:

1. **ערבוב API-ים של פריימוורקים.** גם grammY וגם Telegraf חושפים `ctx.reply()` אבל עם טיפוסי Context שונים; python-telegram-bot משתמש ב-`update.message.reply_text()`. סוכנים מערבבים `ctx.reply()` לקוד PTB, או את `Markup` של Telegraf לתוך grammY.

2. **הגבלת פורט ב-webhook.** טלגרם שולח webhooks רק לפורטים 443, 80, 88 או 8443. הגדרה על 3000 או 8080 נכשלת בשקט בלי שגיאה מצד טלגרם.

3. **שכחה לענות ל-callback queries.** כל `callback_query` חייב להיענות עם `answerCallbackQuery()` גם כשאין מה להציג (`text` מוגבל ל-0-200 תווים), אחרת המשתמש נתקע עם ספינר.

4. **callback data חורג מ-64 בייטים.** עברית היא 2 בייטים לתו ב-UTF-8, כלומר 64 בייטים הם לכל היותר 32 תווים. משתמשים במפתחות אנגליים קצרים ושומרים את הנתונים המלאים ב-session או ב-DB.

5. **חוסר escaping ב-HTML parse mode.** עם `parse_mode: "HTML"` חייבים escaping ל-`<`, `>` ו-`&` בטקסט משתמש. החזרת קלט לא-escaped היא הסיבה הרגילה לשגיאת פרסור.

6. **Polling ו-webhook במקביל.** בלי `deleteWebhook()` לפני polling הבוט לא מקבל כלום. טלגרם שולח לנקודת קצה אחת בלבד, ונכשל בשקט.

7. **timeout של pre-checkout query.** ה-handler של `pre_checkout_query` חייב להגיב תוך 10 שניות, אחרת התשלום נכשל בשקט. שומרים אותו קליל.

8. **session ב-grammY בלי storage adapter.** ברירת המחדל בזיכרון מתאפסת בכל הפעלה מחדש. פרודקשן דורש אחסון חיצוני (Redis, Supabase).

9. **Telegraf v4 מול v3.** דאטה ישן מייצר v3 (`telegraf.startPolling()`). ב-v4 זה `bot.launch()` ו-`bot.webhookCallback()`.

10. **python-telegram-bot v20+ הוא async לחלוטין.** דאטה ישן מייצר `def handler` במקום `async def handler`, או את `Updater` המיושן.

11. **סיוט escaping של MarkdownV2 בעברית.** נדרש escaping ל-`_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`. בטקסט עברי זה בלתי אפשרי בפועל. משתמשים ב-HTML.

12. **חוסר error handler.** בלי `bot.catch()` (grammY) או מקבילה, שגיאה לא מטופלת הורגת את התהליך ב-polling, וב-webhook טלגרם מנסה שוב לתוך לולאת שגיאות אינסופית.

13. **כתיבת קוד אפמרלי של 10.2 מול API של 10.3.** `receiver_user_id` ו-`callback_query_id` הוחלפו ב-`ephemeral_message_parameters`. כל דוגמה שקדמה ל-24.08.2026, כולל כל מה שמודל למד, משתמשת במבנה המת.

## דוגמאות

דוגמאות מלאות מקצה לקצה נמצאות ב-[references/examples.md](references/examples.md): בוט תפריט בעברית עם מקלדות אינליין, בוט webhook על Vercel עם הודעות שגיאה בעברית, תהליך שיחה ב-python-telegram-bot, חשבונית כוכבים ב-python, אימות מספר טלפון ישראלי, וריאנטי המקלדות ב-Telegraf וב-PTB, והמטפלים של Bot Business.

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
4. **בקבוצה: בדקו את מצב הפרטיות** (ראו "מצב פרטיות בקבוצות"). זו הסיבה הנפוצה ביותר, והיא נראית בדיוק כמו webhook שבור.
5. אם אתם מצפים ל-`message_reaction` או ל-`chat_member`, וודאו שהם מפורטים ב-`allowed_updates`, הם לא נמסרים כברירת מחדל.
6. בדקו אם המשתמש חסם את הבוט או הסיר מהקבוצה.

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
- בפלטפורמות serverless זמן הריצה המרבי יכול להיות קצר מאוד (תלוי תוכנית), כך שה-handler נקטע באמצע.

### טקסט עברי מופיע הפוך בלוגים/קונסול

זו בעיית תצוגה בטרמינלים שלא תומכים ב-RTL, לא בעיה בנתונים עצמם. הטקסט שמור נכון ומרונדר כראוי בטלגרם. אל תנסו "לתקן" את זה על ידי היפוך מחרוזות.

### כפתורי מקלדת אינליין לא מתעדכנים

אחרי `editMessageText`, המקלדת הישנה נשארת אלא אם מעבירים `reply_markup` בקריאת העריכה. תמיד העבירו את המקלדת החדשה (או `InlineKeyboard()` ריק כדי להסיר):

```typescript
await ctx.editMessageText("עודכן!", {
  reply_markup: new InlineKeyboard(), // מסיר מקלדת
});
```
