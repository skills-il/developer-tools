---
name: n8n-hebrew-workflows
description: >-
  Build and optimize n8n automation workflows with Israeli API integrations
  including Green Invoice, israeli-bank-scrapers, data.gov.il, and Israeli SMS
  gateways. Use when user asks to "create n8n workflow for Israeli business",
  "connect Green Invoice to n8n", "automate hashbonit", "tazrim avoda b'ivrit",
  "set up Shabbat-aware cron", or integrate Israeli payment gateways (Cardcom,
  Tranzila, Grow/Meshulam) into n8n flows. Covers Hebrew data handling in
  Function nodes, NIS currency formatting, Shabbat/holiday-aware scheduling via
  Hebcal API, and self-hosting on Israeli cloud with data residency compliance.
  Do NOT use for general n8n tutorials without Israeli context (use n8n official
  docs), standalone invoice management (use green-invoice-il), or Hebrew NLP
  tasks (use hebrew-nlp-toolkit).
license: MIT
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
---

# תהליכי עבודה n8n בעברית

## הנחיות

### שלב 1: זיהוי תבנית האוטומציה

לפני שבונים משהו, מתאימים את הצורך העסקי לתבנית n8n מתאימה:

| צורך עסקי | תבנית n8n | צמתים עיקריים | API ישראלי |
|-----------|-----------|---------------|------------|
| התאמת חשבוניות | Cron -> HTTP -> Compare -> Update | Cron, HTTP Request, IF, Function | Green Invoice API |
| סיווג תנועות בנק | Cron -> Code -> Spreadsheet | Cron, Execute Command, Google Sheets | israeli-bank-scrapers |
| סנכרון נתוני ממשלה | Cron -> HTTP -> Transform -> DB | Cron, HTTP Request, Function, Postgres | data.gov.il CKAN API |
| הודעות SMS | Trigger -> Function -> HTTP | Webhook, Function, HTTP Request | 019 SMS / Inforu API |
| טיפול ב-webhooks של תשלומים | Webhook -> Validate -> Process | Webhook, IF, Function, HTTP Request | Cardcom / Tranzila / Grow |
| תזמון מותאם חגים | Cron -> HTTP -> IF -> Execute | Cron, HTTP Request, IF, Function | Hebcal API |
| תהליך אישור רב-שלבי | Webhook -> Wait -> IF -> Notify | Webhook, Wait, IF, HTTP Request | Slack + שער SMS |

**איך בוחרים:**
- אם התהליך רץ לפי לוח זמנים, מתחילים עם Cron trigger ובודקים אם צריך השהיה בשבת/חגים (שלב 4)
- אם התהליך מגיב לאירועים חיצוניים (אישור תשלום, הגשת טופס), מתחילים עם Webhook trigger
- אם התהליך מעבד טקסט בעברית, מוסיפים Function node בתחילת הצינור לטיפול בקידוד ו-RTL (שלב 3)

### שלב 2: חיבור API ישראליים ב-n8n

#### Green Invoice API

Green Invoice משתמש ב-OAuth2 עם API key ו-secret. הגדרת HTTP Request node:

```
Method: POST
URL: https://api.greeninvoice.co.il/api/v1/account/token
Headers:
  Content-Type: application/json
Body:
{
  "id": "{{$env.GREEN_INVOICE_API_KEY}}",
  "secret": "{{$env.GREEN_INVOICE_API_SECRET}}"
}
```

שמירת ה-JWT token מהתגובה והעברתו לבקשות הבאות:

```
Authorization: Bearer {{$json.token}}
```

נקודות קצה נפוצות של Green Invoice:

| נקודת קצה | Method | שימוש |
|-----------|--------|-------|
| `/api/v1/documents/search` | POST | חיפוש חשבוניות לפי תאריך, לקוח, סטטוס |
| `/api/v1/documents` | POST | יצירת חשבונית/קבלה חדשה |
| `/api/v1/clients/search` | POST | חיפוש לקוח לפי שם או מספר עוסק |
| `/api/v1/payments` | GET | שליפת רשומות תשלום להתאמה |
| `/api/v1/businesses/me` | GET | מידע על העסק הנוכחי |

למידע מפורט יש לעיין ב-`references/israeli-api-endpoints.md`.

#### israeli-bank-scrapers דרך Execute Command

ל-n8n אין node מובנה לבנקים ישראליים. משתמשים ב-Execute Command node להרצת `israeli-bank-scrapers`:

```bash
npx israeli-bank-scrapers --company $BANK_NAME --id $USER_ID --password $PASSWORD --output json
```

בנקים נתמכים: הפועלים, לאומי, דיסקונט, מזרחי, אוצר החייל, בינלאומי, מסד, יהב, ביחד משכנתאות, oneZero, בהצדעה.

**אבטחה:** פרטי התחברות נשמרים ב-credential store של n8n, לא בתוך ה-workflow JSON. משתמשים במשתני סביבה לערכים רגישים.

#### data.gov.il CKAN API

נתונים פתוחים של ממשלת ישראל דרך CKAN API:

```
GET https://data.gov.il/api/3/action/datastore_search
Parameters:
  resource_id: <resource-guid>
  q: <search-term>
  limit: 100
  offset: 0
```

ה-API מחזיר שמות שדות בעברית. מומלץ להשתמש ב-Function node לנרמול המפתחות לאנגלית לפני עיבוד המשך.

#### שערי SMS ישראליים

| שער | סוג API | אימות | מתאים ל |
|-----|---------|-------|---------|
| 019 SMS | REST | API key + secret | שיווק המוני, הודעות עסקיות |
| Inforu | REST | Username + token | OTP, הודעות עסקיות, WhatsApp |
| Nexmo/Vonage IL | REST | API key + secret | בינלאומי + מקומי |

פורמט מספרי טלפון ישראליים: תמיד שולחים בפורמט בינלאומי `972XXXXXXXXX` (מורידים את ה-0 הפותח). Function node לפני ה-SMS node מטפל בזה:

```javascript
const phone = $input.first().json.phone;
const formatted = phone.startsWith('0')
  ? '972' + phone.slice(1)
  : phone.startsWith('+972')
    ? phone.slice(1)
    : phone;
return [{ json: { ...items[0].json, phone: formatted } }];
```

### שלב 3: טיפול בנתונים בעברית ב-n8n

#### טקסט RTL ב-Function Nodes

n8n מעבד מחרוזות כ-UTF-8, אז עברית עובדת באופן טבעי. הבעיות מופיעות בממשקים: תגובות API, ייצוא CSV, תבניות מייל.

| בעיה | איפה קורה | פתרון |
|------|-----------|-------|
| עברית הפוכה ב-CSV | ייצוא Spreadsheet File node | הגדרת encoding ל-UTF-8-BOM |
| ניקוד שבור | פרסור תגובת HTTP Request | הגדרת encoding ל-UTF-8 מפורשות |
| ערבוב RTL/LTR במיילים | Send Email node | עטיפת טקסט עברי ב-`<div dir="rtl">` |
| מפתחות JSON בעברית | תגובות data.gov.il | נרמול מפתחות ב-Function node |
| עברית קטועה | בדיקות אורך מחרוזת | שימוש ב-`Array.from(str).length` במקום `.length` |

#### פורמט מטבע שקלים

Function node לעיצוב סכומים בשקלים:

```javascript
function formatNIS(amount) {
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: 'ILS',
    minimumFractionDigits: 2
  }).format(amount);
}

// קלט:  12345.60
// פלט: 12,345.60 ₪
```

בתהליכים פיננסיים, עובדים תמיד באגורות (מספרים שלמים) וממירים לשקלים רק בתצוגה:

```javascript
const amountInAgorot = Math.round(shekelAmount * 100);
const totalAgorot = amountInAgorot + taxAgorot;
const displayAmount = formatNIS(totalAgorot / 100);
```

#### פרסור תאריכים ישראליים

מסמכים ישראליים משתמשים בפורמט DD/MM/YYYY. חשוב לפרסר נכון:

```javascript
// פרסור תאריך ישראלי DD/MM/YYYY
function parseIsraeliDate(dateStr) {
  const [day, month, year] = dateStr.split('/').map(Number);
  return new Date(year, month - 1, day);
}

// פרסור שמות חודשים בעברית (נפוץ במסמכי ממשלה)
const hebrewMonths = {
  'ינואר': 0, 'פברואר': 1, 'מרץ': 2, 'אפריל': 3,
  'מאי': 4, 'יוני': 5, 'יולי': 6, 'אוגוסט': 7,
  'ספטמבר': 8, 'אוקטובר': 9, 'נובמבר': 10, 'דצמבר': 11
};
```

### שלב 4: תזמון Cron מותאם שבת

תהליכים עסקיים בישראל לא צריכים לרוץ בשבת (כניסת שבת ביום שישי עד מוצאי שבת) ובחגים. ל-n8n אין תמיכה מובנית בזה, אז בונים צומת בדיקה בתחילת כל תהליך מתוזמן.

**ארכיטקטורה:** Cron Trigger -> HTTP Request (Hebcal) -> IF (שבת?) -> המשך או עצירה

קריאה ל-Hebcal API ב-HTTP Request node:

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` זה תל אביב. ערים נפוצות נוספות:

| עיר | Geoname ID |
|-----|-----------|
| ירושלים | 281184 |
| תל אביב | 293397 |
| חיפה | 294801 |
| באר שבע | 295530 |

Function node לבדיקה אם הזמן הנוכחי נופל בתוך שבת:

```javascript
const now = new Date();
const shabbatData = $input.first().json;

const candleLighting = shabbatData.items.find(
  item => item.category === 'candles'
);
const havdalah = shabbatData.items.find(
  item => item.category === 'havdalah'
);

if (candleLighting && havdalah) {
  const shabbatStart = new Date(candleLighting.date);
  const shabbatEnd = new Date(havdalah.date);

  if (now >= shabbatStart && now <= shabbatEnd) {
    return []; // פלט ריק עוצר את התהליך
  }
}

return $input.all(); // ממשיך את התהליך
```

לחגים יהודיים, שאילתה ל-Hebcal holidays API:

```
GET https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&mod=on
```

מסננים פריטים עם `yomtov: true` שבהם חלות מגבלות עבודה (כמו שבת).

למידע מפורט יש לעיין ב-`references/shabbat-cron-patterns.md`.

### שלב 5: Webhooks של שערי תשלום ישראליים

שערי תשלום ישראליים שולחים תוצאות עסקאות דרך webhooks. מגדירים Webhook nodes ב-n8n לקליטה ועיבוד.

#### Cardcom

Cardcom שולח POST עם נתונים בפורמט form-encoded:

שדות מפתח ב-callback של Cardcom:

| שדה | תיאור | ערכים |
|-----|-------|-------|
| `ReturnValue` | סטטוס עסקה | `0` = הצלחה, אחר = קוד שגיאה |
| `InternalDealNumber` | מזהה עסקה ב-Cardcom | מחרוזת מספרית |
| `DealResponse` | תיאור תגובה | טקסט בעברית |
| `CardOwnerID` | תעודת זהות הלקוח | 9 ספרות |
| `NumOfPayments` | מספר תשלומים | 1-36 |

#### Tranzila

Tranzila משתמש בתבנית callback שונה עם פרמטרי GET:

| שדה | תיאור | ערכים |
|-----|-------|-------|
| `Response` | קוד סטטוס | `000` = אושר, `001`-`999` = שגיאות |
| `index` | אינדקס עסקה | מספרי |
| `sum` | סכום שחויב | עשרוני (שקלים אם `currency=1`) |
| `currency` | קוד מטבע | `1` = ILS, `2` = USD, `3` = EUR |
| `Rone` | תשלומים | מספר |

#### Grow (משולם)

Grow שולח JSON POST ל-webhook. כולל פרטי עסקה, סכום במטבע ישראלי ופרטי לקוח.

**רשימת IP לבנה:** Cardcom ו-Tranzila דורשים שה-IP של שרת ה-webhook יהיה ברשימה המורשית בלוח הבקרה שלהם. באירוח עצמי יש להשתמש ב-IP קבוע או reverse proxy עם כתובת יציאה קבועה.

### שלב 6: שיקולי אירוח עצמי

#### אפשרויות ענן ישראליות

| ספק | מיקום נתונים | תמיכה ב-n8n | הערות |
|-----|-------------|-------------|-------|
| AWS (il-central-1) | ישראל (תל אביב) | Docker מלא | אזור מלא זמין |
| Azure (Israel Central) | ישראל | Docker מלא | אזור israelcentral |
| Google Cloud (me-west1) | ישראל (תל אביב) | Docker מלא | הושק 2022 |
| Kamatera | ישראל (פתח תקווה) | VPS עם Docker | חברה ישראלית, חיוב בשקלים |
| CloudSpace IL | ישראל | VPS עם Docker | חברה ישראלית, תמיכה מקומית |

**ציות לרגולציית מיקום נתונים:** תקנות הרשות להגנת הפרטיות דורשות שנתונים אישיים של אזרחי ישראל יישמרו בתחומי שיפוט מאושרים. לתהליכים שמעבדים מידע אישי (תעודות זהות, פרטי בנק, מידע רפואי), יש לבחור ספק עם מרכז נתונים בישראל.

#### Docker Compose לאירוח עצמי

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**קריטי:** חובה להגדיר `GENERIC_TIMEZONE=Asia/Jerusalem` ו-`TZ=Asia/Jerusalem`. בלי זה, כל ה-Cron triggers רצים לפי UTC, וחישובי שבת יהיו מוזזים ב-2-3 שעות (ישראל ב-UTC+2 בחורף, UTC+3 בקיץ, עם מעבר לשעון קיץ בתאריכים שונים מארה"ב ואירופה).

## מלכודות נפוצות

- **סוכנים משתמשים ב-UTC כברירת מחדל ב-cron.** ישראל ב-`Asia/Jerusalem` (UTC+2/+3), ומעבר לשעון קיץ בישראל קורה בתאריכים שונים מארה"ב ואירופה. תמיד להגדיר `GENERIC_TIMEZONE` ולוודא אחרי כל מעבר שעון.
- **סוכנים מפרמטים תאריכים כ-MM/DD/YYYY.** בישראל הפורמט הוא DD/MM/YYYY. כל Function node שמפרסר תאריכים חייב לטפל בזה מפורשות. Green Invoice מחזיר ISO 8601, אבל מערכות ממשלה מחזירות DD/MM/YYYY כמחרוזות.
- **סוכנים שולחים מספרי טלפון ישראליים עם אפס פותח.** שערי SMS דורשים פורמט בינלאומי (`972XXXXXXXXX`). מספר כמו `050-1234567` חייב להפוך ל-`972501234567`.
- **סוכנים מניחים שמע"מ כלול בסכומים.** חשבוניות ישראליות מציגות בדרך כלל סכומים לפני מע"מ. Green Invoice API מחזיר גם `amount` (לפני מע"מ) וגם `totalAmount` (כולל מע"מ). תמיד לבדוק איזה שדה נדרש. שיעור מע"מ נוכחי: 18% (נכון לינואר 2025).
- **סוכנים מתעלמים מכך שזמני שבת משתנים לפי עיר.** הדלקת נרות בירושלים 40 דקות לפני השקיעה, בעוד בתל אביב 20-30 דקות. זמן קבוע אחד לכל ישראל יגרום לתהליכים לרוץ בשבת בחלק מהערים.

## משאבים מצורפים

### מסמכי עזר
- `references/israeli-api-endpoints.md` -- טבלת עזר מלאה של נקודות קצה API ישראליות לתהליכי n8n, כולל Green Invoice, data.gov.il, שערי SMS, שערי תשלום ו-Hebcal. יש לעיין בו בעת הגדרת HTTP Request nodes לשירותים ישראליים.
- `references/shabbat-cron-patterns.md` -- תבניות תזמון מוכנות מראש מותאמות שבת ל-n8n כולל הגדרות שבועיות, חודשיות ומותאמות חגים עם אינטגרציית Hebcal API. יש לעיין בו בעת הגדרת כל תהליך מתוזמן שצריך לכבד שבת וחגים.

## פתרון בעיות

### שגיאה: "Green Invoice API מחזיר 401 Unauthorized"
סיבה: ה-JWT token פג תוקף. לטוקנים של Green Invoice יש TTL קצר (כ-30 דקות).
פתרון: הוספת שלב רענון טוקן בתחילת כל הרצת תהליך. שמירת הטוקן ב-static data של n8n (`$getWorkflowStaticData('global')`) עם חותמת זמן, ורענון אם עבר יותר מ-25 דקות.

### שגיאה: "טקסט עברי מופיע משובש בייצוא CSV"
סיבה: ה-CSV חסר BOM (Byte Order Mark) של UTF-8, אז Excel מפרש אותו כ-ANSI.
פתרון: ב-Function node שמכין נתוני CSV, מוסיפים BOM בתחילה: `'\uFEFF' + csvContent`. לחלופין, מגדירים את אפשרות ה-encoding של Spreadsheet File node ל-UTF-8-BOM.

### שגיאה: "Webhook לא מקבל callbacks מ-Cardcom"
סיבה: Cardcom דורש שה-callback URL יהיה נגיש מהאינטרנט עם תעודת SSL תקינה. n8n באירוח עצמי מאחורי firewall לא יקבל callbacks.
פתרון: שימוש ב-reverse proxy (nginx, Caddy) עם SSL של Let's Encrypt. וידוא שמשתנה הסביבה `WEBHOOK_URL` תואם ל-URL הציבורי. הוספת ה-IP של n8n לרשימה המורשית בלוח הבקרה של Cardcom.

### שגיאה: "Cron רץ בשבת למרות בדיקת Hebcal"
סיבה: אזור הזמן של שרת n8n מוגדר ל-UTC במקום Asia/Jerusalem, כך שהשוואת זמני שבת מוסטת ב-2-3 שעות.
פתרון: וידוא `GENERIC_TIMEZONE=Asia/Jerusalem` במשתני הסביבה של n8n. הפעלה מחדש של n8n אחרי שינוי הגדרות אזור זמן. בדיקה על ידי הדפסת `new Date().toString()` ב-Function node.

### שגיאה: "israeli-bank-scrapers נתקע ב-Execute Command node"
סיבה: גרידת בנקים כוללת אוטומציה של דפדפן headless שלוקחת 30-60 שניות. ה-timeout בברירת המחדל של Execute Command קצר מדי.
פתרון: הגדלת ה-timeout בהגדרות Execute Command node (להגדיר 120000ms). וידוא ש-Docker container של n8n מקצה מספיק זיכרון (לפחות 1GB) ל-Chromium.
