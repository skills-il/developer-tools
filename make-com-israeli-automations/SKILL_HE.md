---
name: make-com-israeli-automations
description: >-
  Build and configure Make.com (formerly Integromat) scenarios for Israeli business
  processes, including Green Invoice sync, Monday.com board automation, Priority ERP
  data exports, and WhatsApp Business Hebrew messaging. Use when user asks to "create
  a Make.com scenario", "build an automation for Israeli billing", "automate Green
  Invoice", "otomatzia shel Make", "tizmun scenario", or "connect Israeli apps in
  Make.com". Covers Israeli app module configuration, Hebrew data transformations,
  ILS currency handling, router patterns for bimonthly VAT and quarterly advance
  payments, Shabbat-aware scheduling, and webhook receivers for Israeli payment
  gateways (Cardcom, Tranzila, Grow). Do NOT use for n8n workflows (use
  n8n-hebrew-workflows), Zapier Zaps (use zapier-israeli-integrations), or custom
  code automation without Make.com.
license: MIT
allowed-tools: 'Bash(curl:*) Bash(node:*) Bash(python:*)'
compatibility: >-
  Requires Make.com account (free tier available). Some modules require paid plans.
  Green Invoice API requires a developer account. Priority ERP requires on-prem or
  cloud API access. WhatsApp Cloud API requires Meta Business verification.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - Make.com
      - Integromat
      - אוטומציה
      - תהליכי-עבודה
      - ישראל
      - חשבונית-ירוקה
    en:
      - make-com
      - integromat
      - automation
      - workflows
      - israel
      - green-invoice
  display_name:
    he: אוטומציות Make.com לישראל
    en: Make.com Israeli Automations
  display_description:
    he: >-
      בנייה והגדרה של תרחישי Make.com לתהליכים עסקיים ישראליים, כולל סנכרון
      חשבונית ירוקה, אוטומציה של Monday.com, ייצוא נתוני Priority ERP, והודעות
      WhatsApp Business בעברית. מכסה מודולים ישראליים, טיפול בנתונים בעברית,
      תזמון מודע שבת, ו-webhook לשערי תשלום ישראליים.
    en: >-
      Build and configure Make.com scenarios for Israeli business processes,
      including Green Invoice sync, Monday.com board automation, Priority ERP
      data exports, and WhatsApp Business Hebrew messaging. Covers Israeli app
      modules, Hebrew data transformations, ILS currency handling, Shabbat-aware
      scheduling, and webhook receivers for Israeli payment gateways.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# אוטומציות Make.com לישראל

## הוראות

### שלב 1: זיהוי דפוס התרחיש

לפני בניית תרחיש כלשהו, יש למפות את התהליך העסקי לדפוס Make.com מתאים. אוטומציות עסקיות ישראליות נופלות לקטגוריות צפויות:

| תהליך עסקי | דפוס Make.com | מודולים מרכזיים | סוג טריגר |
|---|---|---|---|
| הפקת חשבוניות וסנכרון | Watch + Create | חשבונית ירוקה, Monday.com | Webhook / מתוזמן |
| דיווח מחזורי חיוב | Router + Aggregator | חשבונית ירוקה, Google Sheets, HTTP | מתוזמן (חודשי/דו-חודשי) |
| שליחת הודעות ללקוחות | Watch + Iterator + HTTP | WhatsApp Cloud API, Monday.com | Webhook |
| ייצוא נתוני ERP | HTTP + JSON Parse + Router | Priority ERP (HTTP), Google Sheets | מתוזמן |
| התראת תשלום | Webhook + Router + Create | Webhook של Cardcom/Tranzila, Slack/Email | מיידי (webhook) |
| הפקת מסמכים | Watch + Template + Email | חשבונית ירוקה, Google Docs, Gmail | מבוסס אירוע |

קריטריונים לבחירת דפוס:
- **צריך תגובה בזמן אמת?** השתמש ב-webhooks (טריגרים מיידיים). אחרת, השתמש בסריקה מתוזמנת.
- **מספר יעדים?** השתמש במודול Router לפיצול הזרימה.
- **עיבוד רשימה?** השתמש ב-Iterator למעבר על פריטים (למשל שורות בחשבונית).
- **צבירת נתונים?** השתמש ב-Array Aggregator לפני הפלט הסופי.

### שלב 2: הגדרת חיבורים לאפליקציות ישראליות

**חשבונית ירוקה**

לחשבונית ירוקה יש מודול Make.com מובנה. הגדרת החיבור:

1. ב-Make.com, חפש "Green Invoice" בפלטת המודולים
2. צור חיבור באמצעות מפתח API וסוד (secret) של חשבונית ירוקה
3. טריגרים זמינים: מסמך חדש, מסמך מעודכן, תשלום חדש
4. פעולות זמינות: יצירת מסמך, יצירת לקוח, שליפת מסמך

מיפוי שדות עיקריים:

| שדה בחשבונית ירוקה | שדה Make.com | הערות |
|---|---|---|
| `type` | סוג מסמך | 320 = חשבונית מס, 330 = קבלה, 400 = הצעת מחיר |
| `client.name` | שם לקוח | תומך בעברית |
| `currency` | קוד מטבע | `ILS` לשקל |
| `amount` | סכום | באגורות (כפול 100 ל-API, חלק ב-100 להצגה) |
| `vatType` | טיפול מע"מ | 0 = פטור, 1 = כולל, 2 = לא כולל |
| `lang` | שפת מסמך | `he` לעברית, `en` לאנגלית |

**Monday.com**

ל-Monday.com יש מודול Make.com מובנה. שימוש נפוץ לחיוב פרויקטים:

1. השתמש ב-"Watch Items" כטריגר (הגדר ללוח ספציפי)
2. מפה ערכי עמודות לפי מזהה העמודה (column ID) ולא לפי הכותרת, כי הכותרות עשויות להיות בעברית ולהשתנות
3. לעמודות סטטוס, השתמש באינדקס התווית (label index) ולא בטקסט העברי

**Priority ERP (דרך מודול HTTP)**

ל-Priority אין מודול Make.com מובנה. יש להשתמש במודולי HTTP:

1. הוסף מודול HTTP "Make a request"
2. תבנית URL: `https://{your-priority-domain}/odata/Priority/tabula.ini/{company}/{entity}`
3. אימות: Basic Auth עם פרטי Priority
4. הגדר כותרת `Content-Type: application/json`
5. לערכי שדות בעברית, וודא שגוף הבקשה מקודד ב-UTF-8

ישויות Priority נפוצות:

| ישות | נתיב OData | שימוש |
|---|---|---|
| `ORDERS` | `/ORDERS` | הזמנות מכירה |
| `AINVOICES` | `/AINVOICES` | חשבוניות חייבים |
| `PORDERS` | `/PORDERS` | הזמנות רכש |
| `LOGCOUNTERS` | `/LOGCOUNTERS` | ספירת מלאי |

**WhatsApp Business (דרך מודול HTTP)**

שימוש ב-WhatsApp Cloud API דרך מודול HTTP של Make.com:

1. URL בסיס: `https://graph.facebook.com/v21.0/{phone-number-id}/messages`
2. אימות: Bearer token (טוקן קבוע מ-Meta Business)
3. לתבניות הודעה בעברית, הגדר שפת תבנית ל-`he`
4. קידוד גוף: JSON עם UTF-8 לטקסט בעברית

**ספקי SMS ישראליים (דרך מודול HTTP)**

| ספק | נקודת קצה | שיטת אימות |
|---|---|---|
| 019 SMS | `https://019sms.co.il/api` | מפתח API בכותרת |
| InforUMobile | `https://api.inforu.co.il/SendMessageXml.ashx` | שם משתמש + טוקן |
| SMS4Free | `https://www.sms4free.co.il/ApiSMS/SendSMS` | מפתח + סוד |

עיין ב-`references/make-israeli-modules.md` למפרטי נקודות קצה מלאים, פרטי אימות ודוגמאות payload.

### שלב 3: טיפול בנתונים בעברית

**ניתוח טקסט וטרנספורמציה**

בעיבוד טקסט עברי ב-Make.com:

- השתמש בפונקציית `toString` לטיפול בטוח בערכי מחרוזות עבריים מתגובות API
- ל-regex על טקסט עברי, השתמש בקלאסים של תווי Unicode: `\p{Hebrew}` מתאים לאותיות עבריות
- בשרשור עברית ואנגלית (למשל מספרי חשבונית), הצב את החלק העברי ראשון כדי לשמר את סדר הקריאה RTL
- השתמש ב-`trim` על שדות טקסט בעברית, כי חלק מה-API הישראליים מרפדים בתווי Unicode בלתי נראים (סימני LTR/RTL)

**פורמט מטבע שקלים**

פונקציית `formatNumber` של Make.com מטפלת ב-ILS:

| ביטוי | פלט | שימוש |
|---|---|---|
| `formatNumber(amount; 2; "."; ",")` | `1,234.56` | תצוגה סטנדרטית |
| `formatNumber(amount / 100; 2; "."; ",")` | `12.35` | המרת אגורות לשקלים |
| `"₪" + formatNumber(amount; 2; "."; ",")` | `₪1,234.56` | עם סימן מטבע |

הערה: סימן השקל (₪) הוא Unicode U+20AA. אל תשתמש ב-`NIS` כסימן בפלט ללקוחות.

**המרת תאריכים עבריים**

Make.com מאחסן תאריכים בפורמט ISO 8601. להצגה ישראלית:

- השתמש ב-`formatDate(date; "DD/MM/YYYY")` לפורמט תאריך ישראלי (יום/חודש/שנה)
- לשמות חודשים בעברית, השתמש בטבלת מיפוי (ל-Make.com אין פורמט חודשים בעברית מובנה):

| חודש | עברית |
|---|---|
| 1 | ינואר |
| 2 | פברואר |
| 3 | מרץ |
| 4 | אפריל |
| 5 | מאי |
| 6 | יוני |
| 7 | יולי |
| 8 | אוגוסט |
| 9 | ספטמבר |
| 10 | אוקטובר |
| 11 | נובמבר |
| 12 | דצמבר |

השתמש ב-`formatDate(now; "M")` לקבלת מספר החודש, ואז מפה אותו לשם העברי באמצעות פונקציית switch או טבלת מיפוי במודול Set Variable.

### שלב 4: בניית דפוסי Router למחזורי חיוב ישראליים

עסקים ישראליים עובדים לפי מחזורי חיוב ספציפיים שונים מדפוסים אמריקאיים או אירופיים. השתמש ב-Routers של Make.com לפיצול לוגיקה לפי מחזורים אלה.

**דיווח מע"מ דו-חודשי (דו"ח דו-חודשי)**

דוחות מע"מ מוגשים דו-חודשית עבור רוב העסקים (עסקים מתחת לסף מדווחים שנתית). תקופות המע"מ:

| תקופה | חודשים | מועד הגשה | ביטוי סינון |
|---|---|---|---|
| 1 | ינואר-פברואר | 15 מרץ | `formatDate(now; "M") = 1 OR formatDate(now; "M") = 2` |
| 2 | מרץ-אפריל | 15 מאי | `formatDate(now; "M") = 3 OR formatDate(now; "M") = 4` |
| 3 | מאי-יוני | 15 יולי | `formatDate(now; "M") = 5 OR formatDate(now; "M") = 6` |
| 4 | יולי-אוגוסט | 15 ספטמבר | `formatDate(now; "M") = 7 OR formatDate(now; "M") = 8` |
| 5 | ספטמבר-אוקטובר | 15 נובמבר | `formatDate(now; "M") = 9 OR formatDate(now; "M") = 10` |
| 6 | נובמבר-דצמבר | 15 ינואר | `formatDate(now; "M") = 11 OR formatDate(now; "M") = 12` |

בנה Router עם 6 ענפים, כל אחד מסנן חשבוניות לתקופה הרלוונטית. אחרי ה-Router, השתמש ב-Array Aggregator לסיכום סכומים לכל תקופה לדו"ח המע"מ.

**מקדמות מס רבעוניות**

עצמאים וחברות מסוימות משלמים מקדמות מס רבעוניות:

| רבעון | חודשים | מועד תשלום |
|---|---|---|
| Q1 | ינואר-מרץ | 15 אפריל |
| Q2 | אפריל-יוני | 15 יולי |
| Q3 | יולי-ספטמבר | 15 אוקטובר |
| Q4 | אוקטובר-דצמבר | 15 ינואר |

**דיווח שנתי**

מועדי הגשת דו"ח שנתי משתנים לפי שיטת ההגשה:
- הגשה מקוונת: 30 אפריל
- הגשה דרך רואה חשבון: הארכה עד 31 מאי או מאוחר יותר (משתנה לפי שנה)

לאוטומציות שנתיות, תזמן תרחיש לרוץ ב-1 ינואר שצובר את נתוני השנה הקודמת.

עיין ב-`references/billing-cycle-patterns.md` להגדרות router מפורטות וביטויי סינון של Make.com.

### שלב 5: תזמון עם הלוח הישראלי

**תזמון מודע שבת**

תרחישי Make.com שמתקשרים עם עסקים או לקוחות ישראליים צריכים להימנע מריצה בשבת (כניסת שבת ביום שישי עד צאת שבת). הגדר את התזמון כך:

1. הגדר את תזמון התרחיש לרוץ ימים ראשון עד חמישי בלבד
2. לריצות ביום שישי, הגדר זמן ריצה אחרון ל-14:00 שעון ישראל
3. הימנע משבת לחלוטין

בהגדרות תזמון Make.com:
- השתמש באפשרות "Specify dates" והחרג שבת
- הגדר אזור זמן ל-`Asia/Jerusalem`
- לחתך של יום שישי, הוסף מודול Filter בתחילת התרחיש:

תנאי סינון לדילוג על שעות שבת:
```
formatDate(now; "d") != 6
OR
(formatDate(now; "d") = 6 AND formatDate(now; "H") < 14)
```

כאשר `d` = יום בשבוע (0=ראשון, 6=שבת) ו-`H` = פורמט 24 שעות.

הערה: `d = 5` הוא יום שישי. בחודשי הקיץ שבת נכנסת מאוחר יותר (לפעמים אחרי 19:00), אבל 14:00 ביום שישי הוא ברירת מחדל שמרנית ובטוחה. לזמני הדלקת נרות מדויקים, השתמש ב-API חיצוני כמו Hebcal.

**זיהוי חגים ישראליים**

לתרחישים שצריכים להשהות בחגים ישראליים (ראש השנה, יום כיפור, סוכות, פסח וכו'), הוסף מודול HTTP בתחילת התרחיש שבודק את ה-API של Hebcal:

```
https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&geo=pos&latitude=32.0853&longitude=34.7818
```

נתח את התגובה לתאריך היום. אם נמצא חג ראשי (`"category": "holiday"`), השתמש במודול Filter לעצירת הריצה.

**שעות פעילות (ראשון-חמישי)**

שעות פעילות עסקיות בישראל הן בדרך כלל ראשון עד חמישי, 09:00-18:00. לאוטומציות B2B:
- תזמן ריצות בין 09:00-17:00 שעון ישראל
- יום ראשון הוא היום העסקי הראשון בשבוע
- יום שישי הוא חצי יום (עד 13:00 בערך)

### שלב 6: טיפול ב-Webhooks משערי תשלום ישראליים

**Webhook של Cardcom**

Cardcom שולח בקשות POST ל-webhook URL שלך אחרי אירועי תשלום:

1. צור טריגר Custom Webhook ב-Make.com
2. הגדר את "Notify URL" של Cardcom ל-URL של ה-webhook ב-Make.com
3. שדות עיקריים ב-callback של Cardcom:

| שדה | תיאור | דוגמה |
|---|---|---|
| `OperationResponse` | קוד הצלחה/כישלון | `0` = הצלחה |
| `Amount` | סכום חיוב בשקלים | `150.00` |
| `CardOwnerID` | תעודת זהות של בעל הכרטיס | מספר בן 9 ספרות |
| `NumOfPayments` | מספר תשלומים | `3` |
| `Token` | טוקן כרטיס לחיובים חוזרים | |

**Webhook של Tranzila**

Tranzila משתמשת בזרימה מבוססת הפניה. ללכידת תוצאות:

1. צור טריגר Custom Webhook
2. הגדר את פרמטר `notify_url` של Tranzila
3. שדות עיקריים:

| שדה | תיאור |
|---|---|
| `Response` | `000` = מאושר |
| `sum` | סכום בשקלים |
| `ccno` | מספר כרטיס ממוסך |
| `myid` | תעודת זהות לקוח |
| `fpay` | סכום תשלום ראשון |
| `spay` | סכום תשלומים עוקבים |
| `npay` | מספר תשלומים |

**Webhook של Grow (של לאומי)**

Grow מספקת webhook מודרני בסגנון REST:

1. רשום את URL ה-webhook של Make.com בדשבורד של Grow
2. Grow שולחת JSON POST עם סוג אירוע ופרטי תשלום
3. אמת את חתימת ה-webhook באמצעות הסוד המשותף בכותרת `X-Grow-Signature`

לכל שערי התשלום, תמיד ודא:
- קוד התגובה/סטטוס מצביע על הצלחה לפני עיבוד
- הסכום תואם את החיוב הצפוי
- לתשלומים, שמור גם את הסכום הכולל וגם את הסכום לכל תשלום

## דוגמאות

### דוגמה 1: סנכרון חשבונית ירוקה ל-Monday.com

המשתמש אומר: "צור תרחיש Make.com שמוסיף פריט ב-Monday.com בכל פעם שנוצרת חשבונית מס בחשבונית ירוקה"

פעולות:
1. הוסף טריגר "Watch Documents" של חשבונית ירוקה, סנן לסוג 320 (חשבונית מס)
2. הוסף פעולת "Create an Item" של Monday.com
3. מפה שדות: מספר חשבונית לעמודת שם, שם לקוח לעמודת לקוח, סכום לעמודת סכום (סוג מספר), תאריך לעמודת תאריך עם `formatDate`
4. הגדר תזמון לכל 15 דקות, ראשון-חמישי + שישי עד 14:00

תוצאה: פריטי Monday.com חדשים נוצרים אוטומטית לכל חשבונית מס, עם שמות לקוח בעברית שמורים וסכומי שקלים מפורמטים נכון.

### דוגמה 2: סיכום מע"מ דו-חודשי

המשתמש אומר: "בנה תרחיש שמייצר גיליון סיכום מע"מ בסוף כל תקופה דו-חודשית"

פעולות:
1. טריגר מתוזמן ל-1 במרץ, מאי, יולי, ספטמבר, נובמבר, ינואר
2. הוסף "Search Documents" של חשבונית ירוקה לשליפת כל החשבוניות מהתקופה הדו-חודשית הקודמת
3. הוסף Iterator לעיבוד כל חשבונית
4. הוסף Router עם ענפים להכנסות (סוג 320) והוצאות (סוג 305)
5. הוסף Array Aggregator לכל ענף לסיכום סכומים
6. הוסף "Add Row" של Google Sheets לכתיבת תקופה, סה"כ הכנסות, סה"כ הוצאות, והפרש מע"מ

תוצאה: סיכום מע"מ דו-חודשי אוטומטי שתואם את תקופות הדיווח של רשות המסים.

### דוגמה 3: אישור הזמנה ב-WhatsApp בעברית

המשתמש אומר: "שלח הודעת WhatsApp בעברית כשלקוח מבצע הזמנה"

פעולות:
1. הוסף טריגר Custom Webhook לקבלת אירועי הזמנה
2. הוסף מודול HTTP שקורא ל-WhatsApp Cloud API
3. השתמש בתבנית הודעה בעברית מאושרת מראש עם משתנים: שם לקוח, מספר הזמנה, סכום כולל בשקלים
4. פרמט סכום עם `"₪" + formatNumber(amount; 2; "."; ",")`
5. הוסף פילטר שבת לתור הודעות בשבת למשלוח ביום ראשון בבוקר

תוצאה: לקוחות מקבלים אישורי WhatsApp בעברית עם סכומי שקלים מפורמטים נכון, בכבוד לשעות השבת.

## משאבים מצורפים

### מסמכי עזר
- `references/make-israeli-modules.md` - מדריך מלא של מודולים ישראליים והגדרות HTTP ל-Make.com, כולל חשבונית ירוקה, Monday.com, Priority ERP, WhatsApp Cloud API, ספקי SMS ישראליים ושערי תשלום. עיין בו בעת הגדרת חיבור חדש לאפליקציה ישראלית או פתרון בעיות אימות API.
- `references/billing-cycle-patterns.md` - דפוסי אוטומציה מפורטים למחזורי חיוב ישראליים כולל מע"מ דו-חודשי, מקדמות רבעוניות, דיווח שנתי ולוחות זמנים לשכר. כולל ביטויי סינון והגדרות Router של Make.com. עיין בו בעת בניית אוטומציות מבוססות זמן הקשורות למועדי מס או חיוב ישראליים.

## מלכודות נפוצות

- סוכנים מניחים דיווח מע"מ חודשי (דפוס אמריקאי/אירופי). דיווח מע"מ בישראל הוא דו-חודשי עבור רוב העסקים. תמיד יש לאשר את תדירות הדיווח לפני בניית פילטרי תקופה.
- פונקציות התאריך של Make.com משתמשות במספור יום בשבוע בסגנון אמריקאי (0 = ראשון). סוכנים מניחים לעיתים קרובות שני = 0 (ISO 8601). ב-Make.com, ראשון הוא 0 ושבת היא 6.
- סכומים ב-API של חשבונית ירוקה הם באגורות (מספר שלם), לא בשקלים. סוכנים שוכחים לעיתים קרובות לחלק ב-100 להצגה או להכפיל ב-100 בשליחה ל-API.
- סוכנים נוטים לתזמן ריצות יום שישי ב-17:00 או מאוחר יותר. שבת יכולה להיכנס כבר ב-16:00 בחורף. יש להשתמש ב-14:00 כזמן חתך בטוח ליום שישי.
- שמות עמודות בעברית ב-Monday.com צריכים להיות מופנים לפי מזהה עמודה (column ID), לא לפי כותרת התצוגה. סוכנים מנסים לעיתים קרובות להשתמש בכותרת העברית ישירות, מה ששובר כשמשתמשים משנים שמות עמודות.
- ביטויי סינון ב-Make.com משתמשים בשווה בודד (`=`) להשוואה, לא שווה כפול (`==`). סוכנים כותבים `==` מניסיון בתכנות.
- שנת המס הישראלית היא ינואר-דצמבר (כמו שנה קלנדרית), אבל סוכנים מניחים לפעמים אפריל-מרץ (דפוס בריטי) או אוקטובר-ספטמבר (שנת כספים אמריקאית).

## פתרון בעיות

### שגיאה: "Green Invoice API מחזיר 401 Unauthorized"
סיבה: אי-התאמה במפתח API/סוד, או שימוש בפרטי sandbox בייצור (או להפך)
פתרון: ודא שאתה משתמש בסביבה הנכונה. כתובת sandbox של חשבונית ירוקה היא `https://sandbox.d.greeninvoice.co.il/api/v1/`, ייצור היא `https://api.greeninvoice.co.il/api/v1/`. חדש את מפתח ה-API אם נדרש.

### שגיאה: "טקסט עברי מופיע משובש בפלט"
סיבה: אי-התאמת קידוד. חלק מה-API הישראליים מחזירים Windows-1255 או ISO-8859-8 במקום UTF-8.
פתרון: בדוק את כותרות תגובת ה-API עבור `charset`. אם לא UTF-8, הוסף מודול Text Parser אחרי מודול ה-HTTP והגדר קידוד קלט שמתאים למקור. חשבונית ירוקה ו-Monday.com משתמשים ב-UTF-8 באופן מובנה.

### שגיאה: "תרחיש Make.com רץ בשבת"
סיבה: אזור זמן מוגדר ל-UTC במקום Asia/Jerusalem, מה שגורם ללוח הזמנים להיות לא מיושר עם שעון ישראל.
פתרון: בהגדרות התרחיש, הגדר אזור זמן ל-`Asia/Jerusalem`. ודא שפילטר השבת משתמש בערך יום-בשבוע הנכון (6 = שבת ב-Make.com).

### שגיאה: "Webhook של Cardcom לא מופעל"
סיבה: ה-Custom Webhook של Make.com חייב להיות במצב "האזנה" (מופעל) לפני ש-Cardcom שולחת את ההתראה. כמו כן, Cardcom דורשת HTTPS.
פתרון: וודא שהתרחיש פעיל וה-webhook במצב האזנה. העתק את כתובת ה-webhook אחרי הפעלתו. ודא שהכתובת מתחילה ב-`https://`. בדוק עם עסקה קטנה קודם.
