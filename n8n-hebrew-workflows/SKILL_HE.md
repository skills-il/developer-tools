---
name: n8n-hebrew-workflows
description: >-
  Build and optimize n8n 2.x automation workflows (stable line 2.36 as of August 2026) with
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

המשטר החל במאי 2024 (25,000 ש"ח), ובינואר 2025 ירד ל-20,000. תהליך שנוגע בחשבוניות היסטוריות חייב לבחון כל חשבונית מול הסף שהיה בתוקף בתאריך שלה עצמה; הטבלה המלאה נמצאת ב-`references/israeli-api-endpoints.md`.

**שני כללים נפרדים חלים כאן, ותהליך שמערבב ביניהם שגוי.** חובת המוכר יושבת בסעיף 47(א2)(1) לחוק מע"מ, קמה רק לפי דרישת הקונה, ואינה חלה על עסקה בשיעור אפס: "ובעסקה שסכומה, בלא המס, עולה על הסכום האמור בסעיף 38(א1), חייב הוא לעשות כן לפי דרישת הקונה; הוראות סעיף קטן זה יחולו לעניין חשבונית מס שהוצאה בשל עסקה שהמס שחל לגביה אינו בשיעור אפס". שלילת ניכוי מס התשומות מהקונה יושבת בסעיף 38(א1), ואין בה שום תנאי של דרישת הקונה: "לא יותר ניכוי מס התשומות הכלול בחשבונית מס שסכומה, בלא המס, עולה על 5,000 שקלים חדשים (מינואר 2026 ועד מאי 2026: 10,000 שקלים חדשים) ושאינה כוללת מספר שהקצה לה המנהל". לכן צומת ולידציה לא יכול להתייחס ל"הקונה לא ביקש" כאישור. שימו לב למילה `עולה על` בחוק: חשבונית שיושבת בדיוק על 5,000 נמצאת מחוץ לכלל, אז השתמשו ב-`>` ולא ב-`>=`.

**הסף נמדד לפני מע"מ.** משווים אותו מול השדה `amount` של Morning ולא מול `totalAmount`. במע"מ של 18% ההפרש בין שני השדות הוא כ-900 ש"ח סביב קו ה-5,000, ולכן השוואה מול השדה הלא נכון מסווגת שגוי חשבוניות בטווח הזה. מעבר ליוני 2026 לא נחקקה הורדה נוספת.

בנו את בדיקת הסף כמשתנה ב-workflow ולא כמספר קשיח. **המנגנון שבו מסמך של Morning מקבל מספר הקצאה אינו מתועד בסקיל הזה**, כי תיעוד ה-API של Morning מוגש כאפליקציית JS שמחזירה 200 לכל נתיב, ולכן אף שם שדה לא ניתן לאימות. אל תמציאו שם שדה ואל תניחו שהוא זהה ל-EZCount. בררו מול Morning, ובינתיים טפלו במסמך שנוצר בלי מספר הקצאה כמצב שדורש התערבות אנושית.

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

קודי סוגי מסמכים תואמים לקודי רשות המסים שבהם משתמש Morning (305 / 320 / 330 / 400). כמו ב-Morning, **הסכומים בשקלים עשרוניים, לא באגורות**. ברירת המחדל של `vat_type` היא `PRE` (מחיר לפני מע"מ), ו-`INC` למחיר כולל מע"מ.

**עיכוב ההקצאה מגיע כסטטוס 417, לא כשדה שאפשר לנסות שוב.** בתיעוד של EZCount כתוב: "When the document is waiting for the Tax Authority allocation number we will return status `417`". אין שדה `allocation_status`, וניסיון חוזר לא מנקה את המצב. במקרה של 417 התיעוד נותן ארבע אפשרויות: לוותר על מספר ההקצאה, לבטל את המסמך, להגיש השגה נוספת, או לבצע היפוך חיוב (ביטול והפקה מחדש בשיעור אפס, כך שהקונה מפיק חשבונית עצמית). התפצלו על ה-417, הציגו למשתמש את הודעת רשות המסים, ותנו לאדם לבחור, כי לשלוש מתוך ארבע האפשרויות יש השלכות מס. שימו לב גם למגבלת הקצב: 250 בקשות ב-10 שניות, והבקשות חייבות להישלח בזו אחר זו ולא במקביל.

EZCount ו-Morning מפיקים את אותו פלט משפטי (חשבוניות מס מסולקות), אז הבחירה ביניהם תפעולית ולא טכנית. בחרו EZCount אם הלקוח כבר על המערכת החשבונאית של EasyCount, אחרת ל-Morning יש תיעוד API עשיר יותר.

#### israeli-bank-scrapers דרך Code Node

ל-n8n אין צומת מובנה לבנקים ישראליים. החבילה `israeli-bank-scrapers` היא ספריית Node.js ו**לא כלי CLI**, ולכן היא רצה בתוך Code node דרך `createScraper()`. דורשת Node.js >= 22.22.2. שלושה דברים חוסמים אותה, לפי הסדר שבו הם נתקלים: הגדרת `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` **על ה-task runner** כדי ש-`require()` יצליח; דרך עובדת להעברת הסודות (ראו למטה, "credential store" לא עובד מתוך Code node); ומפתחות ההתחברות הנכונים לכל בנק. המפתח הוא `password` ולעולם לא `userPassword`, והשדה הראשון שונה מבנק לבנק (`userCode` בהפועלים, `username` בלאומי/מזרחי/מקס, `id` + `num` בדיסקונט/מרכנתיל, `id` + `card6Digits` בישראכרט/אמקס). קראו את `SCRAPERS[companyId].loginFields` במקום להניח מבנה.

**דרך הסודות דורשת בחירה מודעת, כי "שלפו מה-credential store" אינו בר-מימוש בתוך Code node.** ל-Code node אין credentials מוגדרים, ולכן אין שם `$credentials`, ובנפרד `$env` חסום כברירת מחדל ב-2.x. שלוש האפשרויות האמיתיות: להגדיר `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` על ה-task runner ולהישאר עם `$env`; להעביר את הסוד מצומת קודם שנושא credential, בידיעה שהוא מופיע אז בנתוני ההרצה; או external secrets בתוכנית enterprise.

**חסימת Cloudflare (2026):** זיהוי בוטים חוסם דפדפנים headless באמקס ובישראכרט. הפורק המתוחזק `@sergienko4/israeli-bank-scrapers` עוקף זאת עם Camoufox.

**שקלו אם סריקה היא בכלל הדרך הנכונה.** הדפוס הזה שומר את פרטי ההתחברות החיים של הלקוח לבנק כדי שדפדפן headless יתחבר בשמו, וזה עומד בניגוד לתנאי השימוש של רוב הבנקים בישראל בנוגע לשיתוף פרטי התחברות. החלופה המורשית לפי חוק שירות מידע פיננסי (Open Banking) קיימת והיא הדרך שניתן להגן עליה בכל מוצר שפונה ללקוחות. קוד לדוגמה, רשימת ה-`CompanyTypes` המלאה וטבלת שדות ההתחברות לכל בנק נמצאים ב-`references/israeli-api-endpoints.md`.

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

#### WhatsApp Business Cloud

ל-n8n יש צמתים ייעודיים: **`n8n-nodes-base.whatsApp`** ("WhatsApp Business Cloud", typeVersion 1.1, credential בשם `whatsAppApi`) לשליחה, ו-**`n8n-nodes-base.whatsAppTrigger`** לקליטה. פעולות: Send, Send Template, Send and Wait for Response.

שני כללים של מטא שוברים את התהליכים האלה, ושניהם לא בשליטת n8n. **חלון שירות הלקוחות של 24 שעות:** משתמש ששולח לכם הודעה או מתקשר פותח חלון של 24 שעות שבתוכו הודעות חופשיות נמסרות; מחוצה לו רק תבנית מאושרת מראש תגיע. תהליך מתוזמן ישראלי רץ מחוץ לחלון מעצם הגדרתו, ולכן חייב Send Template. **תבניות דורשות אישור מראש** באחת משלוש קטגוריות, Marketing, Utility או Authentication, ותבניות בעברית נבדקות כמו כל תבנית, אז אשרו מוקדם. התמחור הוא לפי הודעה שנמסרה (התמחור לפי שיחה הסתיים ב-1.7.2025), ולכן לולאת פיזור עולה כסף על כל פריט.

#### שערי SMS ישראליים

| שער | Host | אימות | מתאים ל |
|-----|------|-------|---------|
| 019 טלזר | `019sms.co.il` | Bearer token, או שם משתמש + סיסמה | דיוור המוני, טרנזקציוני |
| InforUMobile | `capi.inforu.co.il` | Bearer token (עם רשימת IP מורשים) | OTP, טרנזקציוני |
| Nexmo/Vonage IL | `rest.nexmo.com` | API key + secret | בינלאומי + מקומי |

**שער 019 מחזיר HTTP 200 גם כשהשליחה נכשלת.** כשל אימות חוזר כ-`200 {"status":3,"message":"Username or password is incorrect..."}`, ולכן HTTP Request node בהגדרות ברירת מחדל מפרש את זה כהצלחה והתהליך ממשיך בלי שנשלחה הודעה. הפעילו **Always Output Data** והתפצלו על `$json.status` (0 = נשלח) עם IF node, לעולם לא על קוד ה-HTTP. שער InforUMobile אוכף בנוסף רשימת IP מורשים מעבר לטוקן, אז הוסיפו את ה-IP היוצא של n8n גם שם וגם אצל Cardcom ו-Tranzila.

מספרי טלפון חייבים להיות בפורמט בינלאומי `972XXXXXXXXX` (בלי האפס המוביל), והנרמול חייב **לאמת** ולא רק לעצב מחדש: קידומת קווית ישראלית (02/03/04/08/09, 072-077) ומספרי 1-800 או *NNNN אינם יכולים לקבל SMS בכלל, ולכן החלפה עיוורת של `0` ב-`972` מעוותת אותם בשקט. גופי הבקשות, שמות השדות בכל שער ומנרמל שבודק קידומת נמצאים ב-`references/israeli-api-endpoints.md`.

#### שלושה כללים ישראליים שחוסמים את כל התהליך

**1. לא כל עסק רשאי להוציא חשבונית מס.** עוסק פטור אינו רשאי להוציא חשבונית מס (סוגים 305 / 320) ואינו רשאי לגבות מע"מ כלל; הוא מוציא קבלה או חשבונית עסקה. בררו את מעמד המע"מ של העסק לפני שבוחרים סוג מסמך ואל תקבעו 305/320 קשיח, אחרת עוסק פטור יגבה מס שלא כדין על מסמך לא תקף. גם עסקאות בשיעור אפס (ייצוא, שירות לתושב חוץ) והפטור באילת מזיזים את השיעור, ולכן `vat_type` הוא החלטה לכל עסקה. המספור רציף ובלתי ניתן לשינוי, חשבונית שגויה מבוטלת בחשבונית זיכוי (330) ולא נמחקת, והמסמך נשמר שבע שנים, אז שמרו את ה-PDF ולא קישור שפג.

**2. דיוור מסחרי אוטומטי מוסדר בחוק.** סעיף 30א לחוק התקשורת (תיקון 40) חל על כל שליחת SMS ווואטסאפ שאפשר לבנות עם הסקיל הזה. סעיף 30א(ב) דורש **הסכמה מפורשת מראש בכתב** לפני השליחה בכלל. סעיף 30א(י)(1) מאפשר פיצוי ללא הוכחת נזק של עד **1,000 ש"ח לכל דבר פרסומת שהתקבל בניגוד לחוק**, וזו בדיוק החשיפה של לולאת דיוור. חלון 24 השעות של מטא הוא כלל של פלטפורמה ולא הכלל המשפטי, ועמידה בו אינה מייתרת הסכמה.

דרישת הסימון תלוית ערוץ ולרוב מיושמת שגוי. הכלל הכללי, סעיף 30א(ה)(1)(א), דורש את המילה `פרסומת` בתחילת ההודעה. אבל סעיף 30א(ה)(2) הוא חריג ל-SMS: בדבר פרסומת שמשוגר בהודעת מסר קצר המפרסם "יציין בדבר הפרסומת רק את שמו ואת דרכי יצירת הקשר עמו לצורך מתן הודעת סירוב". אל תוסיפו קידומת `פרסומת` לתבנית SMS מתוך הנחה שהכלל הכללי חל.

**3. הנתונים שהתהליכים האלה נוגעים בהם הם מידע אישי מוסדר.** תעודת זהות שמגיעה מ-callback של תשלום, פרטי התחברות חיים לבנק, ותיאורי תנועות שמוזרמים למודל שפה של צד שלישי, כולם נכנסים לחוק הגנת הפרטיות כפי שתוקן (תיקון 13, בתוקף מאוגוסט 2025). צמצמו את מה שאתם שומרים, התייחסו לגיליון הגוגל כמאגר מידע מוסדר עם כלל שמירה, ואל תשלחו מידע מזהה של לקוח למודל זר בלי בסיס חוקי.

### שלב 3: טיפול בנתונים בעברית ב-n8n

צמתי Code מעבדים מחרוזות ב-UTF-8, ולכן עברית עובדת נטיבית. הבעיות מתחילות בגבולות: ייצוא CSV דורש UTF-8-BOM אחרת אקסל קורא ANSI, תגובות HTTP Request דורשות קידוד תגובה מפורש, גוף מייל דורש `<div dir="rtl">`, data.gov.il מחזיר מפתחות JSON בעברית שכדאי לנרמל ב-Code node, ואורך מחרוזת חייב `Array.from(str).length` ולא `.length`. ייצואים ישנים מבנקים ומתוכנות הנהלת חשבונות ישראליות הם לרוב Windows-1255 ולא UTF-8, וה-BOM לא פותר את זה, ושמות שמגיעים מלקוחות עלולים לשאת תווי בקרה דו-כיווניים שמסדרים מחדש ויזואלית סכום על חשבונית מודפסת.

עיצוב מטבע דרך `Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' })`. מסמכים ישראליים משתמשים ב-DD/MM/YYYY: Morning מחזיר ISO 8601 אבל מאגרי ממשלה מחזירים DD/MM/YYYY כמחרוזת, אז פרסרו במפורש ואל תסמכו על `new Date(s)`. פונקציות עזר, מפת חודשים בעברית ומנרמל טלפונים שבודק קידומת נמצאים ב-`references/israeli-api-endpoints.md`.

### שלב 4: תזמון מותאם שבת

תהליכים עסקיים בישראל לא צריכים לרוץ בשבת (כניסת שבת ביום שישי עד מוצאי שבת) ובחגים. ל-Schedule Trigger node של n8n אין תמיכה מובנית בזה, אז בונים צומת בדיקה בתחילת כל תהליך מתוזמן.

**ארכיטקטורה:** Schedule Trigger -> HTTP Request (Hebcal) -> IF (שבת?) -> המשך או עצירה

קריאה ל-Hebcal API ב-HTTP Request node:

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` זה תל אביב; ירושלים 281184, חיפה 294801, באר שבע 295530. הדלקת נרות היא 40 דקות לפני השקיעה בירושלים, 30 בחיפה ובזיכרון יעקב, 18 בשאר הערים, ולכן ה-geonameid נושא משקל. Code node לחסימת התהליך:

```javascript
const now = new Date();
const items = $input.first().json?.items;
// כישלון סגור: אם אי אפשר לקרוא את הלוח, אנחנו לא יודעים, ולכן לא רצים.
if (!Array.isArray(items) || items.length === 0) return [];

// מזווגים כל הדלקת נרות עם ההבדלה הראשונה שאחריה. לקיחת
// items.find('candles') ו-items.find('havdalah') שגויה: בשאילתה שנשלחת
// בתוך חג, Hebcal מחזיר את ההבדלה של אותו חג לפני הדלקת הנרות של החג
// הבא, ולכן תנאי הטווח לעולם לא מתקיים והתהליך רץ ביום כיפור.
const ev = items.filter(i => i.category === 'candles' || i.category === 'havdalah')
  .map(i => ({ cat: i.category, at: new Date(i.date) }))
  .sort((a, b) => a.at - b.at);

for (let k = 0; k < ev.length - 1; k++) {
  if (ev[k].cat === 'candles' && ev[k + 1].cat === 'havdalah'
      && now >= ev[k].at && now <= ev[k + 1].at) return [];
}
if (ev.length && ev[0].cat === 'havdalah' && now <= ev[0].at) return [];
return $input.all();
```

**אל תזרקו את העבודה בשקט.** הפקודה `return []` מסיימת את הענף, ולכן חשבונית או הודעה ללקוח שאמורות לצאת בשבת אובדות ולא נדחות. לכל דבר שלקוח ממתין לו, הכניסו את הפריטים לתור (workflow static data או טבלה) ורוקנו אותו בתהליך נפרד אחרי צאת השבת.

לחגים יהודיים, שאילתה ל-Hebcal holidays API:

```
GET https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=x&maj=on&mod=on&i=on
```

מסננים פריטים עם `yomtov: true`. שני הפרמטרים קריטיים ושניהם נכשלים בשקט: הערך `month=now` אינו חוקי ו-Hebcal מחזיר HTTP 200 עם `"items": []`, ולכן החסימה לעולם לא מופעלת; ובלי `i=on` Hebcal מחזיר את לוח התפוצות, 13 ימי יום טוב ל-2026 מול 8 בישראל, ומשבית את העסק בחמישה ימי עבודה רגילים. אמתו מול שדה ה-`title` בתשובה: `Hebcal Israel <שנה>` או `Hebcal <עיר> <שנה>`, לעולם לא `Hebcal Diaspora`.

**קרון של ימי חול אינו מייתר את החסימה הזו:** שישה מתוך שמונת ימי היום טוב של 2026 בישראל נופלים בין ראשון לחמישי, ויום כיפור ביניהם. בקובץ `references/shabbat-cron-patterns.md` נמצאים הדפוסים המתוקנים, חישוב התאריך בשעון ישראל שנדרש לערב חג, ומקרי הצומות וחול המועד שהחסימה הזו מתעלמת מהם.

### שלב 5: Webhooks של שערי תשלום ישראליים

שערי תשלום ישראליים שולחים תוצאות עסקאות דרך webhooks. מגדירים Webhook nodes ב-n8n לקליטה ועיבוד.

שלושה שערים מכסים כמעט את כל תעבורת הכרטיסים בישראל, וכל אחד מוסר את ה-callback אחרת. טבלאות השדות המלאות, נתיבי הבסיס וזרימת ביט נמצאות ב-`references/israeli-api-endpoints.md`; מה שקובע נכונות נמצא כאן.

| שער | צורת ה-callback | בדיקת הצלחה | מפתח דה-דופליקציה |
|---|---|---|---|
| Cardcom v11 | POST של `LowProfileResult` ל-`WebHookUrl` שלכם | **`ResponseCode == 0`** | `TranzactionId` |
| Tranzila | פרמטרים ב-GET | `Response == '000'` | `index` |
| Grow by Meshulam | POST בפורמט `multipart/form-data` (לא JSON) | התאמת `webhookKey` למפתח השמור, ואז קריאה חוזרת | `asmachta` |

**השדה `ReturnValue` אינו שדה סטטוס של Cardcom.** במפרט v11 של Cardcom עצמה הוא מתואר כ-"A string of data to save on the transaction, usually send your unique order Id, you will get it back in the WebHook URL", כלומר ערך שאתם שולחים וחוזר אליכם. התפצלות עליו מאשרת עסקאות שנדחו. שדה `DealResponse` לא קיים כלל ב-v11, והשדות `InternalDealNumber` / `CardOwnerID` / `NumOfPayments` הם שמות של ה-API הישן שאינם מופיעים באובייקט התוצאה, ולכן מפתח דה-דופליקציה שבנוי על `InternalDealNumber` תמיד `undefined` והשמירה מפני חשבונית כפולה אף פעם לא פועלת. תעודת הזהות ומספר התשלומים יושבים תחת `TranzactionInfo` בשמות `CardOwnerIdentityNumber` ו-`NumberOfPayments`.

**לעולם אל תפיקו מסמך ישירות מגוף ה-callback.** כתובת ה-webhook פומבית ואף אחד משלושת השערים האלה לא חותם על המטען, ולכן POST מזויף עם סכום סביר יגרום לתהליך שלכם להפיק חשבונית מס אמיתית ולשרוף מספר הקצאה אמיתי. קראו קודם את העסקה מחדש בצד השרת (Cardcom לפי `LowProfileId` / `TranzactionId`, Grow דרך `getPaymentProcessInfo`, Tranzila לפי `index`), אמתו את הסכום, ורק אז הפיקו. ב-Grow צריך בנוסף לקרוא ל-`approveTransaction` כדי לסגור את התשלום.

ביט אינו API עצמאי: מגיעים אליו דרך Tranzila v2 (`bit: true` בעמוד התשלום) או דרך Grow עם ביט מופעל, והוא מגיע באותה זרימת webhook עם `transactionType` שונה.

#### אופני אימות ל-Webhook

צומת Webhook של n8n תומך בארבעה אופני אימות. לאור שרשרת ה-CVE של 2026 סביב webhooks לא מאומתים, "None" על webhook ציבורי הוא למעשה פרצת אבטחה. בכל זרימת תשלום או טופס ציבורי בחרו אחד מהשלושה האחרים:

| אופן | איפה מגדירים | מתי להשתמש |
|------|--------------|------------|
| None | dropdown "Authentication" בצומת Webhook | רק בדיקות מקומיות, אסור בפרודקשן |
| Basic Auth | Generic Credential | webhook פנימי מאחורי VPN; עובד עם כל לקוח HTTP |
| Header Auth | credential מסוג Header Auth (למשל `X-API-Key: <token>`) | ברירת המחדל ל-callbacks של שערי SMS ו-webhooks פנימיים |
| JWT Auth | credential מסוג JWT (HMAC HS256/384/512 או RSA/ECDSA דרך PEM) | אינטגרציות בין-ארגוניות שבהן הקורא כבר מנפיק JWT |

**אבל עבור שלושת השערים הישראליים, HMAC אינו הבקרה הנכונה.** אף אחד מהם לא חותם על המטען: ל-Cardcom v11 אין שדה חתימה כלל, ו-Grow שולח `webhookKey` משותף בתוך הגוף. מה שבאמת מגן עליכם הוא קריאה חוזרת של העסקה בצד השרת לפני הפקת מסמך כלשהו, כמתואר למעלה.

**אימות חתימת HMAC (לשולחים שבאמת חותמים):** ל-n8n אין מאמת HMAC מובנה, אז הוא נכתב ב-Code node. שלושה דברים שוברים את הגרסה הנאיבית: צומת Webhook פולט `{ json: { headers, params, query, body } }`, ולכן `$input.first().headers` מחזיר `undefined`; `$env` חסום בתוך Code nodes כברירת מחדל ב-2.x, ולכן הסוד יוצא `undefined` בשקט; ו-`JSON.stringify(body)` אינו מה שהשולח חתם עליו, כי סדר המפתחות והרווחים שונים. הקוד המלא, כולל טיפול ב-raw body, נמצא ב-`references/webhook-auth-patterns.md`.

**הסתייגות JWT, מתוקנת:** ה-JWT Auth של n8n **כן** אוכף את `exp`. הוא קורא ל-`jwt.verify` מ-`jsonwebtoken`, שדוחה טוקן שפג תוקף כברירת מחדל. גרסה קודמת של הסקיל טענה אחרת וזו הייתה טעות. מה שהוא לא בודק זה `iss` ו-`aud`, כי לא מועברים לו `issuer` ו-`audience`. הוסיפו בדיקת claims לשני אלה בלבד, ורק אחרי שאופן האימות JWT Auth כבר אימת את החתימה.

### שלב 6: שיקולי אירוח עצמי

#### קו האבטחה של n8n 2.x ונעילת גרסה

גרסה n8n 2.0 שוחררה בדצמבר 2025; הגרסה היציבה הנוכחית היא 2.36.7 נכון לאוגוסט 2026. **נעלו תג של 2.32.1 ומעלה** ולעולם לא `n8nio/n8n:latest`. שלוש חולשות ברמת CRITICAL (CVE-2026-44789 זיהום prototype ב-HTTP Request node שמוביל ל-RCE, CVE-2026-44790 קריאת קבצים שרירותית בצומת Git, CVE-2026-44791 עקיפת הטלאי בצומת XML) פורסמו ב-14.5.2026 ותוקנו ב-2.22.1, ותיקונים נוספים ברמת HIGH של דליפת credentials ובריחה מארגז החול נחתו לאורך 2.31.5 ו-2.32.1. חולשת CVE-2026-44789 יושבת בדיוק על הנתיב הקריטי של הסקיל הזה, כי כל אינטגרציה ישראלית כאן היא HTTP Request node, וכל זרימת תשלום מוסיפה Webhook ציבורי.

שתי הגדרות מהשינויים של 2.0 חוסמות את הקוד בסקיל הזה, וכשה-task runners פעילים (ברירת המחדל ב-2.0) שתיהן שייכות ל-**runner** ולא לקונטיינר הראשי:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

בלי הראשון, מאמת ה-HMAC ב-`references/webhook-auth-patterns.md` זורק שגיאה על `require('crypto')`. גם `N8N_BLOCK_ENV_ACCESS_IN_NODE` מוגדר `true` כברירת מחדל ב-2.x, ולכן `$env.*` בתוך Code node מחזיר ריק בשקט. שימו לב ש-credential store אינו הפתרון כאן (ל-Code node אין credentials); בחרו אחת משלוש הדרכים בשלב 2.

**גרסה n8n 3.0 נוחתת באוקטובר 2026** ומסירה התקנות npm לאירוח עצמי (Docker בלבד), את הצמתים Function, Function Item ו-Item Lists, את העוזר `$getPairedItem`, ואת AI Agent node בגרסה 1 יחד עם כל מצבי הסוכן הישנים. בנו את שלב 7 על Tools Agent הנוכחי.

בקובץ `references/n8n-version-migration.md` נמצאים היסטוריית ה-CVE המלאה, טבלת השינויים השוברים של 2.0, ההפעלה מחדש של Execute Command, הרשימה המלאה של 3.0, ואפשרויות האירוח הישראליות.

#### הגדרות אירוח עצמי שחשובות בישראל

הגדירו **גם** `GENERIC_TIMEZONE=Asia/Jerusalem` וגם `TZ=Asia/Jerusalem`. בלעדיהן צמתי Schedule Trigger רצים לפי UTC וחישובי השבת מוזזים ב-2-3 שעות; שעון הקיץ בישראל מתחיל ביום שישי שלפני יום ראשון האחרון של מרץ ומסתיים ביום ראשון האחרון של אוקטובר. הגדירו `N8N_ENCRYPTION_KEY` יציב כדי שה-credential store ישרוד הפעלות מחדש, נעלו את תג ה-image, ושימו את משתני המודולים של ה-Code node על שירות ה-task runner. קובץ Compose מוכן וטבלת האירוח הישראלי נמצאים ב-`references/n8n-version-migration.md`.

### שלב 7: צמתי AI Agent של n8n לתהליכים ישראליים

n8n 2.x מגיע עם אינטגרציית LangChain מובנית (קבוצת "Advanced AI"): Tools Agent, צמתי זיכרון, צמתי Vector Store ל-RAG (Pinecone, Qdrant, Supabase pgvector), וצמתי Model עבור OpenAI, Anthropic ומודלים מקומיים דרך Ollama. בנו על **Tools Agent**: גרסה 3.0 מסירה את AI Agent node בגרסה 1 יחד עם המצבים SQL, Conversational, OpenAI Functions, Plan-and-Execute ו-ReAct.

**אל תקבעו שם מודל קשיח מתוך מדריך.** צומת Anthropic Chat Model הנוכחי מושך את רשימת המודלים מה-API של Anthropic בזמן ריצה ולא מרשימה נעולה, ולכן הרשימה זזה בלי גרסה חדשה של n8n. בחרו לפי הדרישה (מודל frontier מדרג הביניים לסיווג בעברית, החזק ביותר הזמין לטקסט משפטי עברי ארוך, בעל הלטנסי הנמוך ביותר לצ'אט בזמן אמת, ומודל מקומי רב-לשוני על VPS ישראלי כשמידע אישי חייב להישאר בישראל), וקחו את מה שהצומת מציע היום. ל-RAG על קורפוס עברי השתמשו במודל embedding רב-לשוני (Cohere `embed-multilingual-v3.0` או OpenAI `text-embedding-3-large`); המודל `text-embedding-ada-002` חלש בעברית. שימו לב שהזרמת תיאורי תנועות של לקוחות למודל זר היא החלטת פרטיות ולא רק החלטת איכות.

**צמתי MCP.** הצומת MCP Client Tool (`@n8n/n8n-nodes-langchain.mcpClientTool`) מתחבר כצומת משנה כדי ש-AI Agent יקרא לכלים בשרת MCP חיצוני, למשל השרתים `hebcal`, `israeli-bank` ו-`data-gov-il` של agentskills.co.il. הצומת MCP Server Trigger (`@n8n/n8n-nodes-langchain.mcpTrigger`) חושף תהליך n8n עצמו ככלי MCP עבור Claude Desktop, Cursor או Windsurf, ומגרסה 2 הוא מציע גם n8n User Auth (OAuth2). צומת `toolMcp` לא קיים: זו הזיה נפוצה ו-n8n דוחה JSON של תהליך שמשתמש בו. דוגמה מלאה של מסווג תנועות בעברית נמצאת ב-`references/n8n-workflow-authoring.md`.

### שלב 8: בחירת פלטפורמה, מבנה ה-JSON ו-credentials

בחרו ב-n8n על פני Make.com או Zapier כשצריך אירוח עצמי בגלל מיקום נתונים בישראל, אוטומציות ללא הגבלה, או גישה מלאה לקוד בשביל המוזרויות של API ישראליים. אף אחת מהשלוש לא מגיעה עם צמתים ישראליים מובנים, ולכן העבודה נעשית ב-HTTP Request וב-Code בכל מקרה; רק את n8n אפשר לארח באזור ישראלי.

תהליכים הם JSON: מערך `nodes` (לכל אחד `name` ייחודי שמשמש כמפתח החיבורים, `type` כמו `n8n-nodes-base.httpRequest`, `typeVersion`, `parameters` ו-`position`) ואובייקט `connections` שממופתח לפי שם צומת המקור. מייבאים דרך `POST /api/v1/workflows` ואז **מפרסמים** לפני הרצה. נעלו את ה-`typeVersion` הנוכחי של כל צומת ולא מספר ישן ממדריך: Schedule Trigger, למשל, נמצא כבר על 1.4 בעוד רוב הדוגמאות מראות 1.2.

סודות נשמרים ב-credential store המוצפן של n8n ולא בתוך ה-JSON, עם חריג אחד שחשוב כאן: ל-Code node אין credentials, ולכן סודות בנק ו-HMAC צריכים אחת מהדרכים שתוארו בשלב 2. גם ל-Morning אין credential נטיבי, אז משרשרים HTTP Request ל-`/account/token` ומעבירים `Authorization: Bearer {{token}}` הלאה, עם רענון בכל הרצה כי ה-JWT פג אחרי 60 דקות.

טבלת ההשוואה המלאה, דוגמת JSON שלמה של תהליך והגדרת ה-credentials לכל שירות נמצאות ב-`references/n8n-workflow-authoring.md`.

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
| CKAN API של data.gov.il | https://data.gov.il/api/3/action/help_show?name=datastore_search_sql | datastore_search, resource IDs |

## מלכודות נפוצות

- **סוכנים נועלים `n8nio/n8n:latest` או תג מיושן של 2.1x/2.2x.** גרסה 2.21.4 לבדה נושאת 68 התראות אבטחה שפורסמו, ובהן שלוש ברמת CRITICAL (CVE-2026-44789 זיהום prototype ב-HTTP Request node שמוביל ל-RCE, CVE-2026-44790 קריאת קבצים שרירותית בצומת Git, ו-CVE-2026-44791 עקיפת הטלאי בצומת XML) שתוקנו ב-2.22.1, ועוד תיקונים ברמת HIGH שנחתו לאורך 2.31.5 ו-2.32.1. כל Webhook ציבורי (כל workflow של שער תשלום בסקיל הזה) מרחיב את החשיפה. נעלו תג של 2.32.1 ומעלה, היציב הנוכחי הוא 2.36.7.
- **סוכנים כותבים `@n8n/n8n-nodes-langchain.toolMcp` ל-MCP Client Tool.** צומת כזה לא קיים. השמות הם `mcpClientTool` ו-`mcpTrigger`.
- **סוכנים שולחים הודעת וואטסאפ חופשית מתהליך מתוזמן.** חלון שירות הלקוחות של 24 שעות כבר נסגר, ולכן רק תבנית מאושרת תגיע. השתמשו ב-Send Template ואשרו את התבנית מראש.
- **סוכנים מנסים שוב 417 של EZCount כאילו מדובר בשגיאה חולפת.** 417 אומר שרשות המסים לא הקצתה מספר, וניסיון חוזר לעולם לא ינקה את זה. אין שדה `allocation_status`. התפצלו על ה-417 והציגו את ארבע האפשרויות המתועדות.
- **סוכנים מצטטים את CVE-2026-21858 כסיבה לנעול גרסת 2.x.** מדובר בגישה לקבצים ללא אימות, לא ב-RCE, והיא נוגעת לגרסאות 1.65.0 עד 1.120.x בלבד. קו 2.x מעולם לא היה פגיע. רצפת המינימום המעשית היא 2.32.1.
- **סוכנים קוראים סודות עם `$env` בתוך Code nodes.** הגישה חסומה כברירת מחדל ב-2.x (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`), ולכן הקריאה מחזירה ריק בשקט וה-node נכשל על ערך לא מוגדר. אבל credential store אינו הפתרון (ל-Code node אין credentials); בחרו אחת משלוש הדרכים בשלב 2.
- **סוכנים קוראים ל-`require()` ב-Code node בלי להתיר את המודול.** הפקודה `require('crypto')` דורשת `NODE_FUNCTION_ALLOW_BUILTIN=crypto`, והפקודה `require('israeli-bank-scrapers')` דורשת `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers`. כאשר task runners פעילים (ברירת המחדל ב-2.0), שני המשתנים מוגדרים על ה-runner ולא על הקונטיינר הראשי.
- **סוכנים מעבירים `userPassword` ל-israeli-bank-scrapers.** שם השדה הוא `password`, והשדה הראשון משתנה מבנק לבנק: `userCode` בהפועלים, `username` בלאומי/מזרחי/מקס, `id` ו-`num` בדיסקונט/מרכנתיל, `id` ו-`card6Digits` בישראכרט/אמקס. אין מבנה אחיד.
- **סוכנים בונים את שער החגים של Hebcal עם `month=now` ובלי `i=on`.** הערך `month=now` אינו חוקי ומחזיר מערך `items` ריק (HTTP 200, בלי שגיאה), ולכן השער אף פעם לא נסגר. השמטת `i=on` מחזירה את לוח התפוצות, שמשבית תהליכים ישראליים בחמישה ימים שהם ימי עבודה רגילים בישראל. השתמשו ב-`month=x&i=on`.
- **סוכנים סומכים על קוד ה-HTTP של שערי SMS ישראליים.** שער 019 מחזיר HTTP 200 עם `status: 3` בכשל אימות. הסתעפו לפי שדה בגוף התשובה, לא לפי קוד הסטטוס.
- **סוכנים מניחים ש-webhook אחד שווה תשלום אחד.** שלושת השערים שולחים webhooks חוזרים. בצעו דה-דופליקציה לפי `TranzactionId` או `index` או `asmachta` לפני יצירת מסמך, אחרת שליחה חוזרת מפיקה חשבונית כפולה ושורפת מספר הקצאה שני.
- **סוכנים מתפצלים על `ReturnValue` ב-webhook של Cardcom.** זהו מזהה ההזמנה שלכם שחוזר אליכם, לא סטטוס. השתמשו ב-`ResponseCode == 0`, ובצעו דה-דופליקציה לפי `TranzactionId` ולא לפי `InternalDealNumber` שאינו קיים.
- **סוכנים בונים את חסימת השבת עם `items.find('candles')` ו-`items.find('havdalah')`.** בשאילתה שנשלחת בתוך חג, Hebcal מחזיר את ההבדלה לפני הדלקת הנרות הבאה, ולכן התנאי לעולם לא מתקיים והתהליך רץ ביום כיפור. זווגו כל הדלקת נרות עם ההבדלה שאחריה, וכשלו סגור כשאי אפשר לקרוא את הלוח.
- **סוכנים אומרים למשתמש לשמור סודות של Code node ב-credential store.** ל-Code node אין credentials. שחררו `$env` על ה-runner, או העבירו את הסוד מצומת קודם.
- **סוכנים מפיקים חשבונית ישירות מגוף ה-webhook של התשלום.** הכתובת פומבית ואף שער ישראלי לא חותם על המטען. קראו קודם את העסקה מחדש בצד השרת.
- **סוכנים קובעים סוג מסמך 305/320 קשיח.** עוסק פטור אינו רשאי להוציא חשבונית מס ואינו רשאי לגבות מע"מ כלל. בררו את מעמד המע"מ קודם.
- **סוכנים בונים דיוור SMS או וואטסאפ בלי בדיקת הסכמה ובלי הסרה.** תיקון 40 לחוק התקשורת נושא פיצוי של עד 1,000 ש"ח להודעה ללא הוכחת נזק.
- **סוכנים משתמשים ב-UTC כברירת מחדל ל-schedule triggers.** ישראל ב-`Asia/Jerusalem` (UTC+2/+3), ומעבר לשעון קיץ בישראל קורה בתאריכים שונים מארה"ב ואירופה (שעון קיץ מתחיל ביום שישי שלפני יום ראשון האחרון של מרץ, ומסתיים ביום ראשון האחרון של אוקטובר). תמיד להגדיר `GENERIC_TIMEZONE` ולוודא אחרי כל מעבר שעון.
- **סוכנים מפרמטים תאריכים כ-MM/DD/YYYY.** בישראל הפורמט הוא DD/MM/YYYY. כל Code node שמפרסר תאריכים חייב לטפל בזה מפורשות. Morning API מחזיר ISO 8601, אבל מערכות ממשלה מחזירות DD/MM/YYYY כמחרוזות.
- **סוכנים שולחים מספרי טלפון ישראליים עם אפס פותח.** שערי SMS דורשים פורמט בינלאומי (`972XXXXXXXXX`). מספר כמו `050-1234567` חייב להפוך ל-`972501234567`.
- **סוכנים מניחים שמע"מ כלול בסכומים.** חשבוניות ישראליות מציגות בדרך כלל סכומים לפני מע"מ. Morning API מחזיר גם `amount` (לפני מע"מ) וגם `totalAmount` (כולל מע"מ). תמיד לבדוק איזה שדה נדרש. שיעור מע"מ נוכחי: 18% (נכון ל-2026).
- **סוכנים מתעלמים מכך שזמני שבת משתנים לפי עיר.** הדלקת נרות בירושלים 40 דקות לפני השקיעה, בחיפה וזיכרון יעקב 30 דקות, ובתל אביב וכל שאר הערים 18 דקות. זמן קבוע אחד לכל ישראל יגרום לתהליכים לרוץ בשבת בחלק מהערים.
- **Execute Command node מושבת כברירת מחדל ב-n8n 2.0.** תהליכים שהשתמשו ב-Execute Command להרצת סקריפטים (למשל לסריקת בנקים) ייכשלו בשקט אחרי שדרוג ל-n8n 2.0. יש לעבור ל-Code nodes, או להפעיל מחדש דרך דריסת משתנה הסביבה `NODES_EXCLUDE` כך שלא יכיל את `n8n-nodes-base.executeCommand` (אין משתנה `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE`, זו הזיה נפוצה).
- **סכומים ב-Morning API הם בשקלים, לא באגורות.** ה-API משתמש בשקלים עשרוניים (`price: 50` = 50 ש"ח). אין להכפיל ב-100 או לבצע המרות אגורות. זה שונה מכמה שערי תשלום שמשתמשים באגורות.
- **רפורמת החשבוניות 2026 משפיעה על אוטומציות, הסף יורד ב-1 ביוני 2026.** חשבוניות מס מעל הסף (10,000 ש"ח עד 31 במאי 2026, ואז 5,000 ש"ח החל מ-1 ביוני 2026) שנוצרו דרך API דורשות כעת מספרי הקצאה מרשות המסים. הסף נמדד **לפני מע"מ**, ולכן משווים אותו מול `amount` ולא מול `totalAmount`. תהליכים שמייצרים חשבוניות אוטומטית חייבים לטפל בשלב ההקצאה, אחרת החשבונית לא תקפה לניכוי מס. שמרו את הסף כמשתנה ב-workflow, לא כמספר קשיח. החוק אומר `עולה על`, אז השתמשו ב-`>` ולא ב-`>=`, ואל תתנו לשאלה אם הקונה ביקש להשפיע: סעיף 38(א1) שולל את ניכוי מס התשומות מהקונה בכל מקרה.
- **קיצורי המקלדת בעורך של n8n נשברים תחת פריסת מקלדת בעברית.** הקנבס קורא את `e.key` במקום `e.code`, אז כשמקלדת עברית פעילה `Ctrl+C` מחזיר `e.key = 'ב'` והקיצור נכשל. החליפו את שפת הקלט לאנגלית בזמן עריכה, או השתמשו בפעולות מהתפריט. issue 12569 ב-GitHub של n8n.
- **לעורך הביטויים והטקסט של n8n אין תמיכה native ב-RTL.** טקסט עברי בשדות ביטוי מוצג משמאל לימין, מה שמקשה לקרוא מחרוזות עברית ארוכות ושובר את היישור הויזואלי עם סימני פיסוק סובבים. למחרוזות עברית ליטרליות ארוכות, שמרו אותן במשתני סביבה או ב-static workflow data וקראו להן בשם, במקום להקליד אותן בעורך הביטויים.
- **תהליכים לא מנוטרים נכשלים בשקט בלי Error Trigger.** סריקת בנק מתוזמנת או סנכרון חשבוניות שזורק שגיאה פשוט נעצר, ואף אחד לא יודע עד שהנתונים מיושנים. צרו תהליך נפרד שמתחיל בצומת **Error Trigger** (n8n מנתב כל הרצה שנכשלה אליו) ששולח התראה בעברית ל-Slack או SMS. לכשלים זמניים (חסימות Cloudflare, טוקנים שפגו, rate limit) הפעילו גם **Retry On Fail** ברמת הצומת עם המתנה סבירה, במקום לתת לכל ההרצה למות בכשל הראשון.

## משאבים מצורפים

### מסמכי עזר
- `references/israeli-api-endpoints.md` -- טבלת עזר מלאה של נקודות קצה API ישראליות לתהליכי n8n, כולל Morning (חשבונית ירוקה), data.gov.il, שערי SMS, שערי תשלום ו-Hebcal. עיינו בו בעת הגדרת HTTP Request nodes לשירותים ישראליים.
- `references/webhook-auth-patterns.md` -- קטעי Code node לאימות חתימת HMAC ולבדיקת claims של JWT.
- `references/n8n-version-migration.md` -- היסטוריית CVE מלאה, טבלת השינויים השוברים של 2.0, הרשימה המלאה של 3.0, ואפשרויות אירוח ישראליות.
- `references/n8n-workflow-authoring.md` -- בחירת פלטפורמה, מבנה ה-JSON של תהליך, הגדרת credentials, צמתי AI, ופתרון בעיות מורחב.
- `references/shabbat-cron-patterns.md` -- תבניות תזמון מוכנות מראש מותאמות שבת ל-n8n כולל הגדרות שבועיות, חודשיות ומותאמות חגים עם אינטגרציית Hebcal API. עיינו בו בעת הגדרת כל תהליך מתוזמן שצריך לכבד שבת וחגים.

## פתרון בעיות

| תסמין | סיבה | פתרון |
|---|---|---|
| Morning מחזיר 401 | ה-JWT פג (60 דקות) | רעננו את הטוקן בתחילת כל הרצה; שמרו אותו ב-`$getWorkflowStaticData('global')` עם חותמת זמן ורעננו אחרי 55 דקות |
| עברית משובשת בייצוא CSV | חסר UTF-8 BOM ואקסל קורא ANSI | הגדירו קידוד UTF-8-BOM בצומת Spreadsheet File |
| callbacks של Cardcom לא מגיעים | הכתובת אינה נגישה מבחוץ, או שה-IP לא ברשימה המורשית | HTTPS ציבורי עם SSL תקין, `WEBHOOK_URL` שתואם לכתובת הציבורית, וה-IP של n8n ברשימה המורשית ב-Cardcom |
| Schedule Trigger רץ בשבת | אזור הזמן של השרת הוא UTC, או שהחסימה זיווגה נרות והבדלה לא נכון (שלב 4) | הגדירו `GENERIC_TIMEZONE` ו-`TZ`, הדפיסו `new Date().toString()` ב-Code node לאימות, והשתמשו בחסימה עם הזיווג המסודר |
| israeli-bank-scrapers נכשל ב-Code node | `require()` חסום, סודות undefined, או מפתחות התחברות שגויים | הגדירו `NODE_FUNCTION_ALLOW_EXTERNAL` **על ה-task runner**, בחרו דרך סודות עובדת (שלב 2), וקראו את `SCRAPERS[companyId].loginFields` |
| Cloudflare חוסם סריקה באמקס וישראכרט | זיהוי בוטים על דפדפנים headless | עברו לפורק המתוחזק `@sergienko4/israeli-bank-scrapers` (Camoufox) |

אבחונים מפורטים יותר, כולל התלויות בתמונת ה-runner ורצפת הזיכרון ל-Chromium, נמצאים ב-`references/n8n-workflow-authoring.md`.
