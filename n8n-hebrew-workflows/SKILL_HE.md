---
name: n8n-hebrew-workflows
description: >-
  Build and optimize n8n 2.x automation workflows (stable line 2.32 as of August 2026) with
  Israeli API integrations including Morning (formerly Green Invoice), EZCount,
  israeli-bank-scrapers, data.gov.il, Israeli SMS gateways, and payment processors
  (Cardcom v11, Tranzila API v2, Grow by Meshulam). Covers the n8n CVE-2026-44789 critical
  patch line, AI Agent nodes with native LangChain + RAG, MCP Client Tool
  and MCP Server Trigger nodes, Israel Invoice Reform 2026 (5,000 NIS pre-VAT threshold
  from June 2026), Hebrew data handling in Code nodes, and Israel-schedule Shabbat and
  holiday gating.
license: MIT
---

# תהליכי עבודה n8n בעברית

## הנחיות

### שלב 1: זיהוי תבנית האוטומציה

לפני שבונים משהו, מתאימים את הצורך העסקי לתבנית n8n מתאימה:

| צורך עסקי | תבנית n8n | צמתים עיקריים | API ישראלי |
|-----------|-----------|---------------|------------|
| התאמת חשבוניות | Schedule Trigger -> HTTP -> Compare -> Update | Schedule Trigger, HTTP Request, IF, Code | Morning (חשבונית ירוקה) API |
| סיווג תנועות בנק | Schedule Trigger -> Code -> Spreadsheet | Schedule Trigger, Code, Google Sheets | israeli-bank-scrapers |
| סנכרון נתוני ממשלה | Schedule Trigger -> HTTP -> Transform -> DB | Schedule Trigger, HTTP Request, Code, Postgres | data.gov.il CKAN API |
| הודעות SMS | Trigger -> Code -> HTTP | Webhook, Code, HTTP Request | 019 Telzar / InforUMobile API |
| טיפול ב-webhooks של תשלומים | Webhook -> Validate -> Process | Webhook, IF, Code, HTTP Request | Cardcom / Tranzila / Grow by Meshulam |
| תזמון מותאם חגים | Schedule Trigger -> HTTP -> IF -> Execute | Schedule Trigger, HTTP Request, IF, Code | Hebcal API |
| תהליך אישור רב-שלבי | Webhook -> Wait -> IF -> Notify | Webhook, Wait, IF, HTTP Request | Slack + שער SMS |
| סיווג חכם עם AI | Schedule Trigger -> Code -> AI Agent -> DB | Schedule Trigger, Code, AI Agent, Postgres | israeli-bank-scrapers + LLM |
| ציות לרפורמת חשבוניות | Webhook -> Code -> HTTP -> HTTP | Webhook, Code, HTTP Request | Morning API + מספרי הקצאה |

**איך בוחרים:**
- אם התהליך רץ לפי לוח זמנים, מתחילים עם Schedule Trigger ובודקים אם צריך השהיה בשבת/חגים (שלב 4)
- אם התהליך מגיב לאירועים חיצוניים (אישור תשלום, הגשת טופס), מתחילים עם Webhook trigger
- אם התהליך מעבד טקסט בעברית, מוסיפים Code node בתחילת הצינור לטיפול בקידוד ו-RTL (שלב 3)
- אם התהליך צריך סיווג או סיכום חכם, משתמשים ב-AI Agent node (שלב 7)

### שלב 2: חיבור API ישראליים ב-n8n

#### Morning (חשבונית ירוקה) API

Morning (לשעבר חשבונית ירוקה, Green Invoice) משתמש ב-API key + secret לקבלת JWT token. זה לא OAuth2. הגדרת HTTP Request node:

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

התגובה מכילה JWT token שתקף ל-60 דקות. שומרים אותו ומעבירים לבקשות הבאות:

```
Authorization: Bearer {{$json.token}}
```

**רפורמת החשבוניות 2026 (הורדת סף):** חשבוניות מס מעל הסף דורשות מספר הקצאה מרשות המסים. הסף יורד במהלך 2026:

| תאריך כניסה לתוקף | סף |
|--------------------|-----|
| 1 בינואר 2026 | 10,000 ש"ח |
| **מ-1 ביוני 2026 ואילך** | **5,000 ש"ח** |

**הסף נמדד לפני מע"מ** (כך קבעה רשות המסים). משווים אותו מול השדה `amount` של Morning ולא מול `totalAmount`. במע"מ של 18% ההפרש בין שני השדות הוא כ-900 ש"ח סביב קו ה-5,000, ולכן השוואה מול השדה הלא נכון מסווגת שגוי חשבוניות בטווח הזה. מעבר ליוני 2026 לא נחקקה הורדה נוספת.

אחרי יצירת מסמך דרך ה-API של Morning, צריך לקרוא לנקודת הקצה של רשות המסים לקבלת מספר הקצאה עבור חשבוניות מזכות. ה-API של Morning מטפל בזה אוטומטית למסמכים שנוצרים דרך הממשק, אבל מסמכים שנוצרים דרך API עשויים לדרוש בקשת הקצאה מפורשת. בנו את בדיקת הסף כמשתנה ב-workflow ולא כמספר קשיח. בדקו בתיעוד ה-API של Morning לתהליך העדכני.

**סכומים בשקלים עשרוניים (לא באגורות).** כשיוצרים מסמכים, `price: 50` זה 50 ש"ח, לא 50 אגורות. אין צורך להכפיל או לחלק ב-100.

נקודות קצה נפוצות של Morning API:

| נקודת קצה | Method | שימוש |
|-----------|--------|-------|
| `/api/v1/documents/search` | POST | חיפוש חשבוניות לפי תאריך, לקוח, סטטוס |
| `/api/v1/documents` | POST | יצירת חשבונית/קבלה חדשה |
| `/api/v1/clients/search` | POST | חיפוש לקוח לפי שם או מספר עוסק |
| `/api/v1/documents/payments/search` | POST | שליפת רשומות תשלום להתאמה |
| `/api/v1/businesses/me` | GET | מידע על העסק הנוכחי |

קודי סוגי מסמכים לשדה `type`:

| קוד | סוג מסמך |
|-----|----------|
| 10 | הצעת מחיר |
| 305 | חשבונית מס |
| 320 | חשבונית מס / קבלה |
| 330 | חשבונית זיכוי / זיכוי |
| 400 | קבלה |

למידע מפורט עיינו ב-`references/israeli-api-endpoints.md`.

#### EZCount (EasyCount) API

EZCount (נכתב גם EasyCount) הוא חלופה פופולרית ל-Morning לעוסקים קטנים. ה-API למסמכים הוא REST עם payload JSON, אימות דרך `api_key` + `api_email` בגוף הבקשה (לא OAuth, לא Bearer).

```
Method: POST
URL: https://api.ezcount.co.il/api/createDoc
Headers:
  Content-Type: application/json
Body:
{
  "api_key": "{{$env.EZCOUNT_API_KEY}}",
  "api_email": "{{$env.EZCOUNT_API_EMAIL}}",
  "developer_email": "you@example.com",
  "type": 320,
  "customer_name": "שם הלקוח",
  "customer_email": "client@example.com",
  "item": [{ "details": "שירותי ייעוץ", "amount": 1, "price": 500, "vat_type": "INC" }]
}
```

קודי סוגי מסמכים תואמים לקודי רשות המסים שבהם משתמש Morning (305 / 320 / 330 / 400). כמו ב-Morning, **הסכומים בשקלים עשרוניים, לא באגורות**. אותה רפורמת חשבוניות 2026 חלה גם כאן, מעל הסף (10,000 ש"ח עד 31.5.2026, 5,000 ש"ח החל מ-1.6.2026) ה-API שולח אוטומטית לסליקה מול שע"ם ומחזיר את מספר ההקצאה בתגובה. בנו ענף נפילה: אם ה-API מחזיר `allocation_status: 'pending'`, בצעו retry אחרי 30 שניות לפני שאתם מסמנים את החשבונית כסופית.

EZCount ו-Morning מפיקים את אותו פלט משפטי (חשבוניות מס מסולקות), אז הבחירה ביניהם תפעולית ולא טכנית. בחרו EZCount אם הלקוח כבר על המערכת החשבונאית של EasyCount, אחרת ל-Morning יש תיעוד API עשיר יותר.

#### israeli-bank-scrapers דרך Code Node

ל-n8n אין node מובנה לבנקים ישראליים. משתמשים ב-Code node להרצת `israeli-bank-scrapers` בצורה פרוגרמטית. החבילה היא ספריית Node.js (לא כלי CLI), לכן חייבים להשתמש ב-`createScraper()`:

**חשוב:** דורש Node.js >= 22.22.2 בסביבת n8n.

שתי הגדרות ב-n8n 2.x חייבות להיות במקום לפני שהקוד הזה רץ בכלל (פירוט בשלב 6): הגדרת `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` כדי ש-`require()` יצליח, ושליפת פרטי ההתחברות מ-credential store במקום מ-`$env` (גישה למשתני סביבה מתוך Code node חסומה כברירת מחדל ב-2.x).

```javascript
// ב-Code node (ב-n8n 2.0: רץ ב-task runner מבודד)
const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');

const scraper = createScraper({
  companyId: CompanyTypes.hapoalim,
  startDate: new Date('2026-01-01'),
  combineInstallments: false,
  showBrowser: false
});

// שדות ההתחברות של הפועלים הם userCode ו-password. בבנקים אחרים השדות שונים.
const credentials = {
  userCode: BANK_USER,
  password
};
const result = await scraper.scrape(credentials);

if (result.success) {
  return result.accounts.flatMap(account =>
    account.txns.map(txn => ({ json: txn }))
  );
} else {
  throw new Error(`Scraping failed: ${result.errorType} - ${result.errorMessage}`);
}
```

סורקים נתמכים (חברי ה-enum בשם `CompanyTypes`): הפועלים (hapoalim), לאומי (leumi), דיסקונט (discount), מרכנתיל (mercantile), מזרחי (mizrahi), אוצר החייל (otsarHahayal), בינלאומי (beinleumi), יוניון (union), מסד (massad), יהב (yahav), בהצדעה (behatsdaa), ביחד בשבילה (beyahadBishvilha), oneZero, פאג"י (pagi), ויזה כאל (visaCal), מקס (max, לשעבר לאומי קארד), ישראכרט (isracard), אמקס (amex).

**שדות ההתחברות שונים מבנק לבנק.** אין מבנה אחיד לפרטי ההתחברות. בדקו את `SCRAPERS[companyId].loginFields` לפני שמחברים credentials:

| בנק | שדות נדרשים |
|------|-------------|
| הפועלים | `userCode`, `password` |
| לאומי, מזרחי, אוצר החייל, מקס, ויזה כאל, יוניון, בינלאומי, מסד, יהב | `username`, `password` |
| דיסקונט, מרכנתיל | `id`, `password`, `num` |
| ישראכרט, אמקס | `id`, `card6Digits`, `password` |

**חסימת Cloudflare (2026):** מתחילת 2026, Cloudflare חוסם דפדפנים headless באתרי אמקס וישראכרט. הפורק המתוחזק `@sergienko4/israeli-bank-scrapers` משתמש ב-Camoufox כפתרון עוקף. אם נתקלים בכשלונות סריקה מתמשכים עם ספקים אלה:

```bash
npm install @sergienko4/israeli-bank-scrapers
```

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

מזהי משאבים שימושיים:

| מסד נתונים | Resource ID | תוכן |
|-----------|-------------|------|
| רשם העמותות | be5b7935-3922-45d4-9638-08871b17ec95 | עמותות רשומות |
| סטטיסטיקת יבוא/יצוא | משתנה | נתוני מסחר לפי קוד HS |

ה-API מחזיר שמות שדות בעברית. משתמשים ב-Code node לנרמול המפתחות לאנגלית לפני עיבוד המשך.

#### שערי SMS ישראליים

| שער | שרת | אימות | מתאים ל |
|-----|------|-------|---------|
| 019 Telzar | `019sms.co.il` | Bearer token, או שם משתמש וסיסמה | שיווק המוני, הודעות עסקיות |
| InforUMobile | `capi.inforu.co.il` | Bearer token (עם רשימת IP מורשים) | OTP, הודעות עסקיות |
| Nexmo/Vonage IL | `rest.nexmo.com` | API key + secret | בינלאומי + מקומי |

דוגמת 019 Telzar SMS ב-HTTP Request node:

```
Method: POST
URL: https://019sms.co.il/api
Headers:
  Content-Type: application/json
  Authorization: Bearer {{$env.SMS_019_TOKEN}}
Body:
{
  "from": "MyBusiness",
  "to": "{{$json.phone}}",
  "message": "{{$json.text}}"
}
```

**שער 019 מחזיר HTTP 200 גם כשהשליחה נכשלת.** כשל אימות חוזר כ-`200 {"status":3,"message":"Username or password is incorrect or Expired and API token is invalid"}`, כך ש-HTTP Request node בהגדרות ברירת המחדל מפרש את זה כהצלחה וה-workflow ממשיך בלי שנשלחה שום הודעה. מפעילים **Always Output Data** על ה-node ומסתעפים לפי `$json.status` (הערך 0 מציין שליחה מוצלחת) ב-IF node, ולא לפי קוד ה-HTTP.

שער InforUMobile אוכף רשימת IP מורשים בנוסף לטוקן. פנייה מכתובת שאינה ברשימה מקבלת `401 {"StatusId": -2, "StatusDescription": "Authentication failed or illegal IP address"}`. מוסיפים את כתובת ה-IP היוצאת של n8n לרשימה בלוח הבקרה של InforU, לצד Cardcom ו-Tranzila (שלב 5).

פורמט מספרי טלפון ישראליים: תמיד שולחים בפורמט בינלאומי `972XXXXXXXXX` (מורידים את ה-0 הפותח). Code node לפני ה-SMS node מטפל בזה:

```javascript
const phone = $input.first().json.phone;
const cleaned = phone.replace(/[-\s]/g, '');
const formatted = cleaned.startsWith('0')
  ? '972' + cleaned.slice(1)
  : cleaned.startsWith('+972')
    ? cleaned.slice(1)
    : cleaned;
return [{ json: { ...$input.first().json, phone: formatted } }];
```

### שלב 3: טיפול בנתונים בעברית ב-n8n

#### טקסט RTL ב-Code Nodes

ב-n8n צמתי Code מעבדים מחרוזות כ-UTF-8, אז עברית עובדת באופן טבעי. הבעיות מופיעות בממשקים: תגובות API, ייצוא CSV, תבניות מייל.

| בעיה | איפה קורה | פתרון |
|------|-----------|-------|
| עברית הפוכה ב-CSV | ייצוא Spreadsheet File node | הגדרת encoding ל-UTF-8-BOM |
| ניקוד שבור | פרסור תגובת HTTP Request | הגדרת encoding ל-UTF-8 מפורשות |
| ערבוב RTL/LTR במיילים | Send Email node | עטיפת טקסט עברי ב-`<div dir="rtl">` |
| מפתחות JSON בעברית | תגובות data.gov.il | נרמול מפתחות ב-Code node |
| עברית קטועה | בדיקות אורך מחרוזת | שימוש ב-`Array.from(str).length` במקום `.length` |

#### פורמט מטבע שקלים

Code node לעיצוב סכומים בשקלים:

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

**לגבי Morning API:** סכומים ב-API הם בשקלים עשרוניים (לא אגורות). `price: 50` זה 50.00 ש"ח. אין צורך להמיר אגורות לשקלים כשעובדים עם Morning API.

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

### שלב 4: תזמון מותאם שבת

תהליכים עסקיים בישראל לא צריכים לרוץ בשבת (כניסת שבת ביום שישי עד מוצאי שבת) ובחגים. ל-Schedule Trigger node של n8n אין תמיכה מובנית בזה, אז בונים צומת בדיקה בתחילת כל תהליך מתוזמן.

**ארכיטקטורה:** Schedule Trigger -> HTTP Request (Hebcal) -> IF (שבת?) -> המשך או עצירה

קריאה ל-Hebcal API ב-HTTP Request node:

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` זה תל אביב. ערים נפוצות נוספות:

| עיר | Geoname ID | הדלקת נרות |
|-----|-----------|------------|
| ירושלים | 281184 | 40 דקות לפני השקיעה |
| תל אביב | 293397 | 18 דקות לפני השקיעה |
| חיפה | 294801 | 30 דקות לפני השקיעה |
| זיכרון יעקב | 293067 | 30 דקות לפני השקיעה |
| באר שבע | 295530 | 18 דקות לפני השקיעה |
| כל שאר הערים | משתנה | 18 דקות לפני השקיעה |

Code node לבדיקה אם הזמן הנוכחי נופל בתוך שבת:

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
GET https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=x&maj=on&mod=on&i=on
```

מסננים פריטים עם `yomtov: true` שבהם חלות מגבלות עבודה (כמו שבת).

שני הפרמטרים האלה קריטיים, ושניהם נכשלים בשקט אם טועים בהם:

- **צריך `month=x` ולא `month=now`.** הערך `now` אינו חוקי בפרמטר הזה. Hebcal מחזיר HTTP 200 עם `"items": []`, בדיקת ה-`yomtov` מחזירה false, וה-workflow רץ ביום כיפור בלי ששום שגיאה נרשמת. הערך `x` מחזיר את כל השנה, ואפשר גם מספר חודש.
- **הפרמטר `i=on` בוחר את לוח השנה של ישראל.** בלעדיו Hebcal מחזיר את לוח התפוצות, כלומר 13 ימי יום טוב לשנת 2026 במקום 8 בישראל. חמשת הימים העודפים (פסח ב', פסח ח', שבועות ב', סוכות ב' ושמחת תורה נפרד) הם ימי עבודה רגילים בישראל, ולכן workflow שמסתמך על לוח התפוצות משבית את העסק חמש פעמים בשנה ללא סיבה. שליחת `geonameid` של עיר ישראלית משיגה את אותה תוצאה.

כדאי לאמת מול שדה ה-`title` בתשובה: הוא חייב להיות `Hebcal Israel <שנה>` או `Hebcal <עיר> <שנה>`, ולעולם לא `Hebcal Diaspora <שנה>`.

למידע מפורט עיינו ב-`references/shabbat-cron-patterns.md`.

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

Code node לוולידציה אחרי ה-Webhook:

```javascript
const data = $input.first().json;

if (data.ReturnValue !== '0') {
  return [{
    json: {
      success: false,
      error: data.DealResponse,
      cardcomId: data.InternalDealNumber
    }
  }];
}

return [{
  json: {
    success: true,
    transactionId: data.InternalDealNumber,
    amount: parseFloat(data.Sum),
    installments: parseInt(data.NumOfPayments),
    customerId: data.CardOwnerID
  }
}];
```

**ממשק Cardcom API v11:** לאינטגרציות חדשות, מגדירים את ה-webhook URL דרך Cardcom API v11 במקום לוח הבקרה הישן. הכתובת `https://secure.cardcom.solutions/api/v11` היא נתיב בסיס ולא נקודת קצה שאפשר לקרוא לה (היא מחזירה 404 בפני עצמה), ולכן מוסיפים אחריה את הפעולה, למשל `POST https://secure.cardcom.solutions/api/v11/LowProfile/Create` לפתיחת דף תשלום מתארח או `POST .../api/v11/Transactions/Transaction` לחיוב ישיר. נקודת ה-v11 גם מאפשרת רישום webhooks לאירועי יצירת מסמכים (קבלות, חשבוניות) בנוסף לקריאות חיוב. ה-webhook חייב להיות HTTPS וזמין לאינטרנט (לא `localhost`, השתמשו ב-ngrok או Cloudflare Tunnel בפיתוח). תיעוד מלא: `https://secure.cardcom.solutions/api/v11/DOCS`.

#### Tranzila

Tranzila משתמש בתבנית callback עם פרמטרי GET:

| שדה | תיאור | ערכים |
|-----|-------|-------|
| `Response` | קוד סטטוס | `000` = אושר, `001`-`999` = שגיאות |
| `index` | אינדקס עסקה | מספרי |
| `sum` | סכום שחויב | עשרוני (שקלים אם `currency=1`) |
| `currency` | קוד מטבע | `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR |
| `Rone` | תשלומים | מספר |

**Tranzila API v2:** Tranzila מציעה אינטגרציית server-to-server (SAQ-D) פלוס iframe ושדות מתארחים לציות PCI. אימות דרך header בשם `X-tranzila-api-app-key` (לא Basic Auth, לא פרמטרי query). ה-v2 API תומך בתשלומי ביט, טוקניזציה, חיוב חוזר, החזרים, ו-3D Secure (חובה לכרטיסי אשראי ישראליים לפי כללי שב"א). לאינטגרציות חדשות, עדיף v2 על פני תבנית ה-CGI הישנה (`tranzila31.cgi`, שכן `tranzila71dl.cgi` כבר מחזיר 404). זרימת ביט: השרת קורא ל-Tranzila v2, התגובה כוללת URL להטמעה ב-iframe (שמציג קוד QR וטלפון להתראת push). תיעוד: `https://docs.tranzila.com/`.

#### Grow by Meshulam

Grow by Meshulam שולח התראות webhook כבקשות POST. **חשוב:** ה-API של Grow משתמש ב-`multipart/form-data` לבקשות (לא JSON). אחרי קבלת webhook, חובה לקרוא ל-`approveTransaction` כדי לסיים את העסקה.

שדות ב-webhook payload:

| שדה | תיאור |
|-----|-------|
| `webhookKey` | מפתח אימות webhook |
| `transactionCode` | קוד עסקה ייחודי |
| `transactionType` | סוג העסקה |
| `asmachta` | מספר אסמכתא |
| `paymentSum` | סכום שחויב |
| `paymentDate` | תאריך התשלום |
| `fullName` | שם מלא של הלקוח |
| `payerPhone` | טלפון הלקוח |
| `payerEmail` | אימייל הלקוח |
| `cardSuffix` | 4 ספרות אחרונות של הכרטיס |
| `cardBrand` | מותג הכרטיס (Visa, Mastercard וכו') |
| `paymentsNum` | מספר תשלומים |

Code node לעיבוד webhook של Grow ואישור:

```javascript
const data = $input.first().json;

const payment = {
  transactionCode: data.transactionCode,
  asmachta: data.asmachta,
  amount: parseFloat(data.paymentSum),
  customerName: data.fullName,
  customerPhone: data.payerPhone,
  customerEmail: data.payerEmail,
  installments: parseInt(data.paymentsNum) || 1
};

// חובה לקרוא ל-approveTransaction אחרי קבלת ה-webhook
// זה נעשה ב-HTTP Request node הבא עם multipart/form-data
return [{ json: payment }];
```

**רשימת IP לבנה:** Cardcom ו-Tranzila דורשים שה-IP של שרת ה-webhook יהיה ברשימה המורשית בלוח הבקרה שלהם. באירוח עצמי השתמשו ב-IP קבוע או reverse proxy עם כתובת יציאה קבועה.

#### תשלומי ביט

ביט הוא אמצעי התשלום הנייד הפופולרי ביותר בישראל. תשלומי ביט זמינים דרך Tranzila (API v2) ו-Grow by Meshulam, לא כ-API עצמאי.

ביט דרך Tranzila v2: יוצרים דף תשלום עם `bit: true` בבקשה. הלקוח סורק QR או מופנה לביט. ה-webhook callback משתמש באותם שדות כמו עסקאות כרטיס אשראי.

ביט דרך Grow by Meshulam: מפעילים ביט בלוח הבקרה של Grow. עסקאות ביט מופיעות באותו תהליך webhook כמו עסקאות כרטיס, עם ערך `transactionType` שונה.

#### אופני אימות ל-Webhook

צומת Webhook של n8n תומך בארבעה אופני אימות. לאור שרשרת ה-CVE של 2026 סביב webhooks לא מאומתים, "None" על webhook ציבורי הוא למעשה פרצת אבטחה. בכל זרימת תשלום או טופס ציבורי בחרו אחד מהשלושה האחרים:

| אופן | איפה מגדירים | מתי להשתמש |
|------|--------------|------------|
| None | dropdown "Authentication" בצומת Webhook | רק בדיקות מקומיות, אסור בפרודקשן |
| Basic Auth | Generic Credential | webhook פנימי מאחורי VPN; עובד עם כל לקוח HTTP |
| Header Auth | credential מסוג Header Auth (למשל `X-API-Key: <token>`) | ברירת המחדל ל-callbacks של שערי SMS ו-webhooks פנימיים |
| JWT Auth | credential מסוג JWT (HMAC HS256/384/512 או RSA/ECDSA דרך PEM) | אינטגרציות בין-ארגוניות שבהן הקורא כבר מנפיק JWT |

**אימות חתימת HMAC (Cardcom, Grow, אינטגרציות מותאמות):** ל-n8n אין מאמת HMAC מובנה. ממשים אותו ב-Code node מיד אחרי ה-Webhook:

```javascript
const crypto = require('crypto');
const signature = $input.first().headers['x-signature']; // או x-cardcom-signature וכו'
const rawBody = JSON.stringify($input.first().body);
const secret = $env.WEBHOOK_HMAC_SECRET;
const expected = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');

// השוואה בטוחה מבחינת זמן כדי לא להדליף את החתימה דרך timing
const a = Buffer.from(signature || '', 'hex');
const b = Buffer.from(expected, 'hex');
if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
  throw new Error('Invalid HMAC signature');
}
return $input.all();
```

**הסתייגות JWT:** ה-JWT Auth של n8n מאמת חתימה אבל לא בודק `exp`, `iss` או `aud`. אם צריך אימות claims, הוסיפו Code node אחרי ה-Webhook שמפענח את הטוקן ומאמת כל claim, אחרת טוקן שפג תוקף יעבור.

### שלב 6: שיקולי אירוח עצמי

#### שינויים משמעותיים ב-n8n 2.0 (דצמבר 2025) + עדכוני אבטחה (2026)

גרסה n8n 2.0 שוחררה בדצמבר 2025; הגרסה היציבה הנוכחית היא 2.32.7 נכון לאוגוסט 2026 (בטא על 2.33.x, עם minor חדש כמעט כל שבוע). נעלו תג ספציפי בפרודקשן במקום `n8nio/n8n:latest`.

**טלאי אבטחה קריטי, חובה לעבור ל-2.32.1 לפחות.** שלוש חולשות ברמת CRITICAL פורסמו ב-14.5.2026 ותוקנו ב-2.22.1:

| CVE | GHSA | השפעה |
|-----|------|-------|
| CVE-2026-44789 | GHSA-c8xv-5998-g76h | זיהום prototype במנגנון ה-pagination של HTTP Request node, שמוביל ל-RCE |
| CVE-2026-44790 | GHSA-57g9-58c2-xjg3 | קריאת קבצים שרירותית דרך צומת Git |
| CVE-2026-44791 | GHSA-wrwr-h859-xh2r | עקיפת הטלאי לזיהום prototype בצומת XML |

חולשת CVE-2026-44789 נמצאת בדיוק על הנתיב הקריטי של הסקיל הזה, מפני שכל אינטגרציה ישראלית כאן היא HTTP Request node. תיקונים נוספים ברמת HIGH נחתו לאורך 2.31.5 ו-2.32.1 (דליפת credentials דרך workflows משותפים, השתלטות על credentials בין דיירים, ובריחה מארגז החול של הביטויים), ולכן **2.32.1 היא רצפת המינימום המעשית** ו-2.32.7 היא הגרסה היציבה הנוכחית.

שתי חולשות מוקדמות יותר מצוטטות הרבה ולרוב מתוארות לא נכון:

- **חולשת CVE-2026-21858 ("Ni8mare", CVSS 10.0), שפורסמה ב-7.1.2026,** היא **גישה לקבצים** ללא אימות דרך טיפול שגוי בבקשות webhook, ולא RCE. היא נוגעת לגרסאות 1.65.0 עד 1.120.x בלבד ותוקנה ב-1.121.0. **קו 2.x מעולם לא היה פגיע**, ולכן היא אינה סיבה לנעול גרסת 2.x כלשהי.
- **חולשות CVE-2026-27493 (CVSS 9.5) ו-CVE-2026-27577 (CVSS 9.4), שפורסמו ב-25.2.2026,** הן הצמד שממנו נגזרה רצפת 2.10.1: הזרקת ביטויים ללא אימות דרך צמתי Form, ובריחה מארגז החול של הביטויים עד כדי RCE. הן נוגעות לגרסאות 1.123.22>, 2.0.0 עד 2.9.2, ו-2.10.0, ותוקנו ב-1.123.22 / 2.9.3 / 2.10.1. הרצפה הזו מוחלפת כעת בדרישת 2.32.1.

כל Webhook ציבורי (כל זרימת תשלום בסקיל הזה חושפת אחד) מרחיב את החשיפה לכל אלה. נעלו את התג ב-`docker-compose.yml` ועקבו אחרי פיד האבטחה של n8n.

n8n 2.0 הביא שינויים משמעותיים שמשפיעים על תהליכים ישראליים:

| שינוי | השפעה | פעולה נדרשת |
|-------|-------|------------|
| גישה ל-`$env` מתוך Code node חסומה כברירת מחדל | כל קריאת `$env.BANK_PASS` או `$env.WEBHOOK_HMAC_SECRET` מחזירה ריק | העברת הסודות ל-credential store, או הגדרת `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` |
| שימוש ב-`require()` מוגבל ב-Code nodes | גם `require('crypto')` וגם `require('israeli-bank-scrapers')` נכשלים | הגדרת `NODE_FUNCTION_ALLOW_BUILTIN` ו-`NODE_FUNCTION_ALLOW_EXTERNAL` |
| Execute Command node מושבת כברירת מחדל | תהליכי סריקת בנקים שמשתמשים ב-Execute Command ישברו | מעבר ל-Code node (שלב 2), או הפעלה מחדש דרך משתנה הסביבה `NODES_EXCLUDE` (ראו למטה) |
| מודל שמירה/פרסום | תהליכים חייבים להתפרסם מפורשות כדי לפעול | פרסום תהליכים אחרי ייבוא או יצירה |
| בידוד task runner ל-Code nodes | Code nodes רצים ב-sandbox מבודד | הגדרת משתני המודולים על ה-**task runner**, לא על הקונטיינר הראשי |
| צומת Python נבנה מחדש על task runners | Python מבוסס Pyodide הוסר, Python נייטיב דורש runners במצב external | הקמת task runners במצב external, או שימוש ב-JavaScript |
| הסרת תמיכה ב-MySQL/MariaDB | לא אפשר להשתמש ב-MySQL/MariaDB כ-DB backend | מעבר ל-PostgreSQL (מומלץ) או SQLite |

**גישה למודולים ב-Code node.** מנגנון `require()` למודולים חיצוניים מושבת ב-n8n אלא אם המשתנה מוגדר, והסקיל הזה זקוק לשניהם:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

בלי הראשון, מאמת ה-HMAC ב-`references/webhook-auth-patterns.md` זורק שגיאה על `require('crypto')`. בלי השני, ה-Code node של סריקת הבנק זורק שגיאה על `require('israeli-bank-scrapers')`. **אם task runners פעילים (ברירת המחדל ב-2.0), מגדירים את המשתנים על ה-task runner ולא על הקונטיינר הראשי של n8n**, אחרת אין להם שום השפעה.

**סודות ב-Code node.** המשתנה `N8N_BLOCK_ENV_ACCESS_IN_NODE` מוגדר כ-`true` כברירת מחדל ב-2.x, ולכן `$env.*` בתוך Code node מחזיר ריק. עדיף להעביר את סודות הבנק וה-HMAC ל-credential store, וזו גם ההמלצה של n8n עצמה בתיעוד השינוי. מגדירים `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` רק אם חייבים לשמר את דפוס ה-`$env`.

ב-n8n 2.0, צומת Execute Command (וגם Local File Trigger) נוסף לרשימת `NODES_EXCLUDE` של ברירת המחדל, ולכן הוא נעלם מלוח הצמתים. כדי להפעיל מחדש את Execute Command, דורסים את `NODES_EXCLUDE` כך שלא יכיל את `n8n-nodes-base.executeCommand`, הדריסה הפשוטה ביותר היא רשימה ריקה, ואז מפעילים מחדש את n8n:
```
NODES_EXCLUDE="[]"
```
לפי תיעוד השינויים של n8n 2.0 זה המנגנון הנתמך, אין משתנה `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE`. הפעלת Execute Command מאפשרת לכל מי שיש לו הרשאת עריכת workflow להריץ פקודות shell שרירותיות, אז עשו זאת רק בסביבות מהימנות וחד-משתמש. הגישה המומלצת נשארת מעבר ל-Code nodes.

#### אפשרויות ענן ישראליות

| ספק | מיקום נתונים | תמיכה ב-n8n | הערות |
|-----|-------------|-------------|-------|
| AWS (il-central-1) | ישראל (תל אביב) | Docker מלא | אזור מלא זמין |
| Azure (Israel Central) | ישראל | Docker מלא | אזור israelcentral |
| Google Cloud (me-west1) | ישראל (תל אביב) | Docker מלא | הושק 2022 |
| Kamatera | ישראל (פתח תקווה) | VPS עם Docker | חברה ישראלית, חיוב בשקלים |
| ActiveCloud / HQserv / MedOne | ישראל | VPS עם Docker | חברות ישראליות, תמיכה מקומית בעברית |

**ציות לרגולציית מיקום נתונים:** הרשות להגנת הפרטיות (PPA) לא דורשת שכל המידע יישאר בישראל. היא מגבילה העברת מידע אישי למדינות ללא הגנה מספקת, או דורשת אמצעי הגנה נוספים (כמו סעיפים חוזיים). לתהליכים שמעבדים מידע אישי (תעודות זהות, פרטי בנק, מידע רפואי), יש לבחור ספק עם מרכז נתונים בישראל או לוודא שמדינת היעד ברשימה המאושרת של הרשות.

#### Docker Compose לאירוח עצמי

```yaml
services:
  n8n:
    # נועלים תג ספציפי. אסור :latest בפרודקשן.
    # חייב להיות לפחות 2.32.1 כדי להיות מטולא נגד שרשרת CVE-2026-44789/44790/44791.
    image: n8nio/n8n:2.32.7
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
      # מומלץ: רוטציה של מפתח ההצפנה רק דרך תהליך המיגרציה המתועד.
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**הערות:**
- n8n 1.0 ומעלה משתמש בניהול משתמשים מובנה (אימייל + סיסמה). משתני הסביבה הישנים `N8N_BASIC_AUTH_*` הוסרו. בהפעלה ראשונה, n8n מבקש ליצור חשבון בעלים.
- `version: '3.8'` לא מופיע כי הוא מיושן ב-Docker Compose V2.
- **קריטי:** חובה להגדיר `GENERIC_TIMEZONE=Asia/Jerusalem` ו-`TZ=Asia/Jerusalem`. בלי זה, כל ה-Schedule Trigger nodes רצים לפי UTC, וחישובי שבת יהיו מוזזים ב-2-3 שעות (ישראל ב-UTC+2 בחורף, UTC+3 בקיץ). שעון קיץ בישראל מתחיל ביום שישי שלפני יום ראשון האחרון של מרץ ומסתיים ביום ראשון האחרון של אוקטובר.

### שלב 7: צמתי AI Agent של n8n לתהליכים ישראליים

n8n 2.x מגיע עם אינטגרציית LangChain מובנית (קבוצת הצמתים "Advanced AI"). מעל 70 צמתי AI: Tools Agent, Conversational Agent, צמתי זיכרון (Window Buffer, Summary Buffer), צמתי Vector Store ל-RAG (Pinecone, Qdrant, Supabase pgvector), וצמתי Model עבור OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet, Claude Opus 4.7 עם מצב חשיבה דינמי), ומודלים מקומיים דרך Ollama. כלים חזקים לאוטומציה עסקית ישראלית.

**בחירת מודל לתוכן ישראלי:**

| שימוש | מודל מומלץ | למה |
|-------|-----------|------|
| סיווג תנועות בעברית | Claude 3.5 Sonnet דרך Anthropic Chat Model node | הבנת עברית חזקה, חלון הקשר גדול, פחות הזיות בקטגוריות מס ישראליות לעומת GPT-4o |
| סיכום מסמכים עברית (PDF ארוכים) | Claude Opus 4.7 עם מצב חשיבה דינמי | n8n 2.21 הוסיף adaptive thinking; טוב יותר מ-GPT-4o לטקסט משפטי עברי מורכב |
| צ'אט עברית בזמן אמת | GPT-4o דרך OpenAI Chat Model node | לטנסי נמוכה יותר מ-Claude לתגובות עברית קצרות |
| On-prem / מיקום נתונים בארץ | Ollama (Llama 3.1, Qwen 2.5) על VPS ישראלי | שומר PII בארץ; העברית של Llama 3.1 סבירה לסיווג, חלשה ליצירה |

**RAG על תוכן ישראלי (צמתי Vector Store):** מחברים צומת Vector Store (Pinecone, Qdrant או Supabase pgvector) ל-AI Agent כדי לבצע retrieval על קורפוסים בעברית (היסטוריית חשבוניות, PDF של חוקי מס, יומני צ'אט לקוחות). השתמשו במודל embedding רב-לשוני שמטפל בעברית (Cohere `embed-multilingual-v3.0` או OpenAI `text-embedding-3-large`); ברירת המחדל `text-embedding-ada-002` חלשה בעברית לעומת שפות בכתב לטיני.

**דוגמה: סיווג אוטומטי של תנועות בנק עם AI**

ארכיטקטורה: Schedule Trigger -> Code (סריקת בנק) -> AI Agent (סיווג) -> Google Sheets

```javascript
// Code node: הכנת תנועות לסיווג AI
const transactions = $input.all().map(item => ({
  json: {
    date: item.json.date,
    description: item.json.description,
    amount: item.json.chargedAmount,
    prompt: `סווג את תנועת הבנק הישראלית הזו למטרות הנהלת חשבונות.
תנועה: "${item.json.description}" על סך ${item.json.chargedAmount} ש"ח בתאריך ${item.json.date}.
קטגוריות: הכנסות, שכר, ספקים, מע"מ, ביטוח לאומי, שכירות, הוצאות משרד, אחר.
השב עם שם הקטגוריה בלבד.`
  }
}));
return transactions;
```

מחברים את הפלט של ה-Code node ל-AI Agent node (Tools Agent) שמוגדר עם ה-LLM המועדף. הסוכן מסווג כל תנועה לפי התיאור העברי וקטגוריות ההוצאות הישראליות המוכרות.

**אינטגרציית MCP ב-n8n (שני צמתים):** n8n 2.x מגיע עם שני צמתי MCP מובנים:

- **MCP Client Tool** (`@n8n/n8n-nodes-langchain.toolMcp`): מתחבר כצומת משנה ל-AI Agent כך שהסוכן יקרא לכלים שחשופים בשרת MCP חיצוני. שימושי לחיבור שרתי MCP מ-agentskills.co.il כמו `hebcal`, `israeli-bank` או `data-gov-il` לסוכנים שלכם.
- **MCP Server Trigger**: חושף תהליך n8n כשלעצמו ככלי MCP. לקוחות AI חיצוניים (Claude Desktop, Cursor, Windsurf, GPT מותאמים) יכולים לגלות ולהפעיל את התהליך כאילו הוא כלי native. שימושי לעטיפת תהליך חיפוש חשבוניות Morning או סורק בנק כך שכל עוזר AI במשרד יוכל להפעיל אותו לפי דרישה.

ביחד הצמתים האלה הופכים את n8n גם למארח כלים וגם לצרכן כלים בסטאק סוכני מבוסס MCP.

### שלב 8: מתי להשתמש ב-n8n לעומת חלופות

| קריטריון | n8n | Make.com | Zapier |
|----------|-----|----------|--------|
| אירוח עצמי (מיקום נתונים) | כן (Docker, כל ענן) | לא (SaaS בלבד) | לא (SaaS בלבד) |
| צמתי API ישראליים | אין מובנים, HTTP/Code | קצת מהקהילה | מעט מאוד |
| מגבלת תהליכים | ללא הגבלה (אירוח עצמי) | לפי תוכנית | לפי תוכנית |
| הרצת קוד | Code nodes מלאים (JS/Python) | JS מוגבל | מוגבל |
| צמתי AI Agent | 70+ צמתי AI, תמיכה ב-MCP | יכולות AI | יכולות AI |
| מחיר (אירוח עצמי) | חינם (קוד פתוח) | לא רלוונטי | לא רלוונטי |
| ממשק בעברית | לא (אנגלית בלבד) | חלקי | לא |
| מתאים ל | מפתחים שצריכים שליטה מלאה, מיקום נתונים, אוטומציות ללא הגבלה | משתמשים לא טכניים שרוצים בונה ויזואלי | אינטגרציות פשוטות, משתמשים לא טכניים |

בחרו n8n כש: צריכים אירוח עצמי למיקום נתוני ישראל, אוטומציות ללא הגבלה, גישה מלאה לקוד לטיפול ב-API ישראליים (קידוד עברית, פורמט טלפונים, חישובי מע"מ), או יכולות AI Agent עם הקשר ישראלי.

### שלב 9: ייבוא וייצוא של workflow כ-JSON

תהליכי n8n הם מסמכי JSON. סוכנים שבונים תהליכים בצורה פרוגרמטית (במקום ללחוץ בממשק) חייבים להבין את המבנה:

```json
{
  "name": "Morning daily reconciliation",
  "nodes": [
    {
      "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 6 * * 0-4" }] } },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [240, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get Token", "type": "main", "index": 0 }]] }
  }
}
```

מבנה עיקרי:
- **`nodes`**: מערך של אובייקטי צמתים. לכל אחד `name` (ייחודי, משמש כמפתח חיבור), `type` (למשל `n8n-nodes-base.httpRequest`), `typeVersion` (חייב להתאים לגרסה ש-n8n תומך בה, אחרת הייבוא נכשל), `parameters` (הגדרות הצומת) ו-`position` (קואורדינטות `[x, y]`).
- **`connections`**: אובייקט שממופתח לפי `name` של צומת המקור, וממפה פלט (`main`) למערך של מערכים של יעדים `{ node, type, index }`. המערך הכפול מאפשר פלטים מרובים (למשל ענפי צומת IF).
- ייצוא דרך הממשק ("Download") או `GET /api/v1/workflows/{id}`; ייבוא דרך "Import from File" או `POST /api/v1/workflows`. אחרי ייבוא ל-n8n 2.0 חובה לפרסם את התהליך לפני שהוא רץ. ערכי `typeVersion` משתנים בין גרסאות, לכן בנו JSON מול גרסת n8n ידועה.

### שלב 10: הגדרת credentials ל-API ישראליים

n8n שומר סודות ב-credential store מוצפן, לעולם לא בתוך ה-workflow JSON:

- **JWT של Morning (חשבונית ירוקה)**: אין credential מובנה. משרשרים HTTP Request nodes, הראשון קורא ל-`/account/token` עם ה-API key וה-secret, הצמתים הבאים שולחים `Authorization: Bearer {{token}}` דרך **Header Auth** או ביטוי. הטוקן פג אחרי 60 דקות, אז מרעננים בכל הרצה במקום לשמור אותו לטווח ארוך.
- **שערי SMS ישראליים (019, InforUMobile)**: יוצרים credential מסוג **Header Auth**, שם `Authorization`, ערך `Bearer <token>`, ומצרפים ל-HTTP Request node.
- **שערי תשלום (Cardcom, Tranzila, Grow)**: שומרים מזהי סוחר / מפתחות API כערכי **Generic Credential** שמופנים דרך `{{$credentials.fieldName}}`. בקשות ה-`multipart/form-data` של Grow עדיין שולפות סודות מה-credential, לא מגוף הצומת.
- באירוח עצמי, הגדירו `N8N_ENCRYPTION_KEY` יציב כדי שה-credential store יישאר ניתן לפענוח בין הפעלות מחדש.

## דוגמאות

### דוגמה 1: חיבור Morning ל-n8n להתאמת חשבוניות יומית

המשתמש אומר: "כל בוקר תמשוך את חשבוניות Morning של אתמול ותסמן את אלה שעדיין לא שולמו."

צומת אחר צומת:
1. **Schedule Trigger**: cron `0 6 * * 0-4` (09:00 שעון ישראל חורף, ראשון-חמישי).
2. **HTTP Request, "Get Token"**: `POST https://api.greeninvoice.co.il/api/v1/account/token` עם `{ id, secret }` מה-credentials. פלט: JWT.
3. **HTTP Request, "Search Documents"**: `POST /api/v1/documents/search` עם `Authorization: Bearer {{$json.token}}`, גוף שמסנן `fromDate`/`toDate` לאתמול ו-`type` ל-305/320.
4. **צומת IF**: מתפצל לפי `status` (פתוח מול סגור) כדי להפריד חשבוניות שלא שולמו.
5. **HTTP Request (SMS) או Send Email**: מודיע למנהל החשבונות על חשבוניות שלא שולמו, גוף בעברית עטוף ב-`<div dir="rtl">`.

עטפו את כל התהליך בבדיקת השבת משלב 4 אם הוא לא אמור לרוץ לעולם בחג שנופל באמצע השבוע.

### דוגמה 2: תנועות בנק ל-Google Sheet, מודע לחגים

המשתמש אומר: "תסרוק את חשבון העסק שלי כל לילה ותוסיף תנועות חדשות לגיליון, אבל תדלג על שבת וחגים."

צומת אחר צומת:
1. **Schedule Trigger**: cron לשעת ערב באמצע השבוע.
2. **HTTP Request (Hebcal)** + **Code (בדיקת שבת)** משלב 4: פלט ריק עוצר את ההרצה בשבת/חג.
3. **Code node**: מריץ `israeli-bank-scrapers` דרך `createScraper()` (שלב 2), פריט אחד לכל תנועה.
4. **Code node**: מנרמל תיאורים בעברית, מעצב סכומים עם `Intl.NumberFormat('he-IL', ...)`, מפרסר תאריכים כ-DD/MM/YYYY.
5. **Google Sheets node** (Append): כותב שורות לגיליון הנהלת החשבונות.
6. תהליך **Error Trigger** נפרד תופס הרצה שנכשלה ומתריע (ראו מלכודות נפוצות).

## שרתי MCP מומלצים

שרתי ה-MCP הבאים מהדירקטוריה נותנים לצומת AI Agent נתונים ישראליים חיים לפי דרישה:

- **hebcal**: לוח השנה היהודי וזמני שבת, חלופה לקריאה ל-Hebcal HTTP API בכל תהליך.
- **israeli-bank**: נתוני חשבונות בנק ישראליים, מאפשר לסוכן למשוך תנועות במקום להריץ `israeli-bank-scrapers` ב-Code node.
- **data-gov-il**: נתונים פתוחים של ממשלת ישראל (CKAN), שאילתת מרשמים בלי לבנות HTTP Request nodes ידנית.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| תיעוד n8n | https://docs.n8n.io/ | מדריך צמתים, ביטויים, אירוח עצמי |
| שינויים שוברים ב-n8n 2.0 | https://docs.n8n.io/changelog/v20-breaking-changes | Execute Command, NODES_EXCLUDE, חסימת $env, DB שהוסרו |
| הפעלת מודולים ב-Code node | https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-modules-in-code-node | NODE_FUNCTION_ALLOW_BUILTIN ו-NODE_FUNCTION_ALLOW_EXTERNAL |
| חסימת גישה לצמתים ב-n8n | https://docs.n8n.io/hosting/securing/blocking-nodes/ | תחביר NODES_EXCLUDE / NODES_INCLUDE |
| API של Morning (חשבונית ירוקה) | https://www.greeninvoice.co.il/api-docs | נקודות קצה, סוגי מסמכים, תהליך הקצאה |
| API של Hebcal | https://www.hebcal.com/home/developer-apis | זמני שבת, חגים, ערכי geonameid |
| CKAN API של data.gov.il | https://data.gov.il/api/3 | datastore_search, resource IDs |

## מלכודות נפוצות

- **סוכנים נועלים `n8nio/n8n:latest` או תג מיושן של 2.1x/2.2x.** גרסה 2.21.4 לבדה נושאת 68 התראות אבטחה שפורסמו, ובהן שלוש ברמת CRITICAL (CVE-2026-44789 זיהום prototype ב-HTTP Request node שמוביל ל-RCE, CVE-2026-44790 קריאת קבצים שרירותית בצומת Git, ו-CVE-2026-44791 עקיפת הטלאי בצומת XML) שתוקנו ב-2.22.1, ועוד תיקונים ברמת HIGH שנחתו לאורך 2.31.5 ו-2.32.1. כל Webhook ציבורי (כל workflow של שער תשלום בסקיל הזה) מרחיב את החשיפה. נעלו תג של 2.32.1 ומעלה, היציב הנוכחי הוא 2.32.7.
- **סוכנים מצטטים את CVE-2026-21858 כסיבה לנעול גרסת 2.x.** מדובר בגישה לקבצים ללא אימות, לא ב-RCE, והיא נוגעת לגרסאות 1.65.0 עד 1.120.x בלבד. קו 2.x מעולם לא היה פגיע. רצפת 2.10.1 נגזרת מ-CVE-2026-27493 ו-CVE-2026-27577 (פורסמו ב-25.2.2026), והיא עצמה מוחלפת בדרישת 2.32.1.
- **סוכנים קוראים סודות עם `$env` בתוך Code nodes.** הגישה חסומה כברירת מחדל ב-2.x (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`), ולכן הקריאה מחזירה ריק בשקט וה-node נכשל על credentials לא מוגדרים. השתמשו ב-credential store.
- **סוכנים קוראים ל-`require()` ב-Code node בלי להתיר את המודול.** הפקודה `require('crypto')` דורשת `NODE_FUNCTION_ALLOW_BUILTIN=crypto`, והפקודה `require('israeli-bank-scrapers')` דורשת `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers`. כאשר task runners פעילים (ברירת המחדל ב-2.0), שני המשתנים מוגדרים על ה-runner ולא על הקונטיינר הראשי.
- **סוכנים מעבירים `userPassword` ל-israeli-bank-scrapers.** שם השדה הוא `password`, והשדה הראשון משתנה מבנק לבנק: `userCode` בהפועלים, `username` בלאומי/מזרחי/מקס, `id` ו-`num` בדיסקונט/מרכנתיל, `id` ו-`card6Digits` בישראכרט/אמקס. אין מבנה אחיד.
- **סוכנים בונים את שער החגים של Hebcal עם `month=now` ובלי `i=on`.** הערך `month=now` אינו חוקי ומחזיר מערך `items` ריק (HTTP 200, בלי שגיאה), ולכן השער אף פעם לא נסגר. השמטת `i=on` מחזירה את לוח התפוצות, שמשבית תהליכים ישראליים בחמישה ימים שהם ימי עבודה רגילים בישראל. השתמשו ב-`month=x&i=on`.
- **סוכנים סומכים על קוד ה-HTTP של שערי SMS ישראליים.** שער 019 מחזיר HTTP 200 עם `status: 3` בכשל אימות. הסתעפו לפי שדה בגוף התשובה, לא לפי קוד הסטטוס.
- **סוכנים מניחים ש-webhook אחד שווה תשלום אחד.** שערי Cardcom, Tranzila ו-Grow שולחים webhooks חוזרים. בצעו deduplication לפי `InternalDealNumber` או `index` או `asmachta` לפני יצירת מסמך, אחרת שליחה חוזרת מפיקה חשבונית כפולה ומבקשת מספר הקצאה שני משע"ם.
- **סוכנים משתמשים ב-UTC כברירת מחדל ל-schedule triggers.** ישראל ב-`Asia/Jerusalem` (UTC+2/+3), ומעבר לשעון קיץ בישראל קורה בתאריכים שונים מארה"ב ואירופה (שעון קיץ מתחיל ביום שישי שלפני יום ראשון האחרון של מרץ, ומסתיים ביום ראשון האחרון של אוקטובר). תמיד להגדיר `GENERIC_TIMEZONE` ולוודא אחרי כל מעבר שעון.
- **סוכנים מפרמטים תאריכים כ-MM/DD/YYYY.** בישראל הפורמט הוא DD/MM/YYYY. כל Code node שמפרסר תאריכים חייב לטפל בזה מפורשות. Morning API מחזיר ISO 8601, אבל מערכות ממשלה מחזירות DD/MM/YYYY כמחרוזות.
- **סוכנים שולחים מספרי טלפון ישראליים עם אפס פותח.** שערי SMS דורשים פורמט בינלאומי (`972XXXXXXXXX`). מספר כמו `050-1234567` חייב להפוך ל-`972501234567`.
- **סוכנים מניחים שמע"מ כלול בסכומים.** חשבוניות ישראליות מציגות בדרך כלל סכומים לפני מע"מ. Morning API מחזיר גם `amount` (לפני מע"מ) וגם `totalAmount` (כולל מע"מ). תמיד לבדוק איזה שדה נדרש. שיעור מע"מ נוכחי: 18% (נכון ל-2026).
- **סוכנים מתעלמים מכך שזמני שבת משתנים לפי עיר.** הדלקת נרות בירושלים 40 דקות לפני השקיעה, בחיפה וזיכרון יעקב 30 דקות, ובתל אביב וכל שאר הערים 18 דקות. זמן קבוע אחד לכל ישראל יגרום לתהליכים לרוץ בשבת בחלק מהערים.
- **Execute Command node מושבת כברירת מחדל ב-n8n 2.0.** תהליכים שהשתמשו ב-Execute Command להרצת סקריפטים (למשל לסריקת בנקים) ייכשלו בשקט אחרי שדרוג ל-n8n 2.0. יש לעבור ל-Code nodes, או להפעיל מחדש דרך דריסת משתנה הסביבה `NODES_EXCLUDE` כך שלא יכיל את `n8n-nodes-base.executeCommand` (אין משתנה `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE`, זו הזיה נפוצה).
- **סכומים ב-Morning API הם בשקלים, לא באגורות.** ה-API משתמש בשקלים עשרוניים (`price: 50` = 50 ש"ח). אין להכפיל ב-100 או לבצע המרות אגורות. זה שונה מכמה שערי תשלום שמשתמשים באגורות.
- **רפורמת החשבוניות 2026 משפיעה על אוטומציות, הסף יורד ב-1 ביוני 2026.** חשבוניות מס מעל הסף (10,000 ש"ח עד 31 במאי 2026, ואז 5,000 ש"ח החל מ-1 ביוני 2026) שנוצרו דרך API דורשות כעת מספרי הקצאה מרשות המסים. הסף נמדד **לפני מע"מ**, ולכן משווים אותו מול `amount` ולא מול `totalAmount`. תהליכים שמייצרים חשבוניות אוטומטית חייבים לטפל בשלב ההקצאה, אחרת החשבונית לא תקפה לניכוי מס. שמרו את הסף כמשתנה ב-workflow, לא כמספר קשיח.
- **קיצורי המקלדת בעורך של n8n נשברים תחת פריסת מקלדת בעברית.** הקנבס קורא את `e.key` במקום `e.code`, אז כשמקלדת עברית פעילה `Ctrl+C` מחזיר `e.key = 'ב'` והקיצור נכשל. החליפו את שפת הקלט לאנגלית בזמן עריכה, או השתמשו בפעולות מהתפריט. issue 12569 ב-GitHub של n8n.
- **לעורך הביטויים והטקסט של n8n אין תמיכה native ב-RTL.** טקסט עברי בשדות ביטוי מוצג משמאל לימין, מה שמקשה לקרוא מחרוזות עברית ארוכות ושובר את היישור הויזואלי עם סימני פיסוק סובבים. למחרוזות עברית ליטרליות ארוכות, שמרו אותן במשתני סביבה או ב-static workflow data וקראו להן בשם, במקום להקליד אותן בעורך הביטויים.
- **תהליכים לא מנוטרים נכשלים בשקט בלי Error Trigger.** סריקת בנק מתוזמנת או סנכרון חשבוניות שזורק שגיאה פשוט נעצר, ואף אחד לא יודע עד שהנתונים מיושנים. צרו תהליך נפרד שמתחיל בצומת **Error Trigger** (n8n מנתב כל הרצה שנכשלה אליו) ששולח התראה בעברית ל-Slack או SMS. לכשלים זמניים (חסימות Cloudflare, טוקנים שפגו, rate limit) הפעילו גם **Retry On Fail** ברמת הצומת עם המתנה סבירה, במקום לתת לכל ההרצה למות בכשל הראשון.

## משאבים מצורפים

### מסמכי עזר
- `references/israeli-api-endpoints.md` -- טבלת עזר מלאה של נקודות קצה API ישראליות לתהליכי n8n, כולל Morning (חשבונית ירוקה), data.gov.il, שערי SMS, שערי תשלום ו-Hebcal. עיינו בו בעת הגדרת HTTP Request nodes לשירותים ישראליים.
- `references/shabbat-cron-patterns.md` -- תבניות תזמון מוכנות מראש מותאמות שבת ל-n8n כולל הגדרות שבועיות, חודשיות ומותאמות חגים עם אינטגרציית Hebcal API. עיינו בו בעת הגדרת כל תהליך מתוזמן שצריך לכבד שבת וחגים.

## פתרון בעיות

### שגיאה: "Morning API מחזיר 401 Unauthorized"
סיבה: ה-JWT token פג תוקף. לטוקנים של Morning יש TTL של 60 דקות.
פתרון: הוספת שלב רענון טוקן בתחילת כל הרצת תהליך. שמירת הטוקן ב-static data של n8n (`$getWorkflowStaticData('global')`) עם חותמת זמן, ורענון אם עבר יותר מ-55 דקות.

### שגיאה: "טקסט עברי מופיע משובש בייצוא CSV"
סיבה: ה-CSV חסר BOM (Byte Order Mark) של UTF-8, אז Excel מפרש אותו כ-ANSI.
פתרון: ב-Code node שמכין נתוני CSV, מוסיפים BOM בתחילה: `'\uFEFF' + csvContent`. לחלופין, מגדירים את אפשרות ה-encoding של Spreadsheet File node ל-UTF-8-BOM.

### שגיאה: "Webhook לא מקבל callbacks מ-Cardcom"
סיבה: Cardcom דורש שה-callback URL יהיה נגיש מהאינטרנט עם תעודת SSL תקינה. n8n באירוח עצמי מאחורי firewall לא יקבל callbacks.
פתרון: שימוש ב-reverse proxy (nginx, Caddy) עם SSL של Let's Encrypt. וידוא שמשתנה הסביבה `WEBHOOK_URL` תואם ל-URL הציבורי. הוספת ה-IP של n8n לרשימה המורשית בלוח הבקרה של Cardcom.

### שגיאה: "Schedule Trigger רץ בשבת למרות בדיקת Hebcal"
סיבה: אזור הזמן של שרת n8n מוגדר ל-UTC במקום Asia/Jerusalem, כך שהשוואת זמני שבת מוסטת ב-2-3 שעות.
פתרון: וידוא `GENERIC_TIMEZONE=Asia/Jerusalem` במשתני הסביבה של n8n. הפעלה מחדש של n8n אחרי שינוי הגדרות אזור זמן. בדיקה על ידי הדפסת `new Date().toString()` ב-Code node.

### שגיאה: "israeli-bank-scrapers נכשל ב-Code node"
סיבה: ב-n8n 2.0, Code nodes רצים ב-task runner מבודד. חבילת `israeli-bank-scrapers` והתלויות שלה (Puppeteer/Playwright) עשויות לא להיות זמינות ב-sandbox.
פתרון: התקנת `israeli-bank-scrapers` כחבילת npm שנגישה ל-task runner של n8n. וידוא שה-Docker container של n8n מקצה מספיק זיכרון (לפחות 1GB) ל-Chromium.

### שגיאה: "Cloudflare חוסם סורק בנקים עבור אמקס/ישראכרט"
סיבה: מתחילת 2026, Cloudflare חוסם דפדפנים headless באתרים פיננסיים ישראליים מסוימים.
פתרון: מעבר לפורק המתוחזק `@sergienko4/israeli-bank-scrapers` שמשתמש ב-Camoufox לעקיפת חסימת Cloudflare. התקנה: `npm install @sergienko4/israeli-bank-scrapers`.
