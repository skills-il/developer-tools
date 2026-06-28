---
name: sumit-api-integration
description: >-
  Integrate the SUMIT (formerly OfficeGuy) REST API into applications for
  Israeli invoicing, accounting, and business automation. Use when user asks to
  connect to SUMIT, "samit", "officeguy", create an invoice via SUMIT, "hashbonit",
  charge a credit card, "slikat ashrai", pull income or expense reports, "shaivat
  dohot", manage customers, or set up SUMIT webhooks. Covers authentication
  (CompanyID + APIKey), document creation (23 document types), tokenized card
  charging, recurring billing, expense ingestion, data retrieval, and Triggers/IPN
  webhooks. Do NOT use for Green Invoice/Morning (use green-invoice), Tranzila (use
  tranzila-payment-gateway), or SHAAM e-invoice allocation (use israeli-e-invoice).
license: MIT
allowed-tools: 'Bash(python:*) Bash(curl:*)'
compatibility: >-
  No SDK required, uses plain HTTP/JSON over stdlib. Requires network access to
  api.sumit.co.il. Works with Claude Code, Claude.ai, Cursor.
---

# אינטגרציית SUMIT API

## סקירה

SUMIT (לשעבר OfficeGuy) היא פלטפורמת ענן ישראלית לניהול עסקי: חשבוניות, סליקת אשראי, הוראות קבע, CRM וקליטת הוצאות. ה-skill מכסה את ה-REST API הציבורי בכתובת api.sumit.co.il, החושף 84 פעולות ב-27 מודולים.

שני עקרונות מעצבים כל קריאה:
1. כל endpoint הוא POST עם גוף JSON, גם שליפות (list/get). אין GET/PUT/DELETE לפי משאב.
2. האימות הוא אובייקט Credentials בתוך גוף ה-JSON (CompanyID ו-APIKey), לא בכותרת HTTP.

## הוראות

### שלב 1: השגת מפתחות

מתוך ממשק SUMIT: הגדרות, ואז מפתחות API. נדרשים שלושה ערכים, הנשמרים כמשתני סביבה (לעולם לא בקוד):

- מזהה חברה: משתנה הסביבה SUMIT_COMPANY_ID. נכנס לכל בקשה.
- מפתח API סודי: משתנה הסביבה SUMIT_API_KEY. רק בקריאות צד-שרת.
- מפתח API ציבורי: משתנה הסביבה SUMIT_API_PUBLIC_KEY. רק לטוקניזציה בדפדפן.

המפתח הסודי APIKey לעולם לא יגיע לדפדפן. המפתח הציבורי הוא היחיד המותר בצד הלקוח.

### שלב 2: ביצוע קריאה מאומתת

כתובת בסיס: api.sumit.co.il. תבנית נתיב: controller ואז action. שלח Content-Type של application/json. כותרת אופציונלית Content-Language בערך he-IL קובעת את שפת התשובה.

כל תשובה משתמשת במעטפת אחת: Status (Success=0, BusinessError=1, TechnicalError=2), UserErrorMessage (טקסט שגיאה למשתמש), TechnicalErrorDetails (פירוט טכני), ו-Data (התוכן הספציפי לפעולה).

קריטי: קוד HTTP 200 עדיין יכול לשאת BusinessError. תמיד בדוק את Status, לא רק את קוד ה-HTTP. השתמש ב-scripts/sumit_client.py כעוטף הקריאות היחיד. ראה references/api-endpoints.md למפת הפעולות המלאה.

### שלב 3: יצירת מסמך (חשבונית או קבלה)

נתיב create של documents. בחר Type מתוך 23 סוגי המסמך (ראה references/document-types-and-enums.md). נפוצים: InvoiceAndReceipt (1), Invoice (0), Receipt (2), PriceQuotation (12).

```json
{
  "Credentials": { "CompanyID": 0, "APIKey": "..." },
  "Details": {
    "Type": "InvoiceAndReceipt",
    "Customer": { "Name": "...", "EmailAddress": "...", "SearchMode": "EmailAddress" },
    "Description": "...", "Language": "Hebrew", "Currency": "ILS"
  },
  "Items":   [ { "Quantity": 1, "UnitPrice": 1000, "Description": "..." } ],
  "Payments":[ { "Amount": 1180, "Details_BankTransfer": {} } ],
  "VATIncluded": false, "VATRate": 18
}
```

התשובה ב-Data: DocumentID, DocumentNumber, CustomerID, DocumentDownloadURL. השדה SearchMode מאפשר upsert (צור-או-מצא) ומונע כפילות לקוחות.

### שלב 4: סליקת אשראי (טוקניזציה תואמת PCI)

פרטי הכרטיס לעולם לא נוגעים בשרת שלך. הזרימה:
1. הדפדפן טוען את payments.js מ-app.sumit.co.il.
2. הקריאה OfficeGuy.Payments.BindFormSubmit עם CompanyID ו-APIPublicKey מטקנת את הכרטיס ומזריקה og-token.
3. שלח את og-token לשרת שלך, ואז קרא ל-charge עם SingleUseToken.

הפעולה charge מחייבת ומפיקה חשבונית בקריאה אחת. שדות מרכזיים: SingleUseToken, Items, VATIncluded, SendDocumentByEmail, AuthoriseOnly (אימות ללא חיוב, מצוין לבדיקות). הזרימה המלאה ב-references/payments-and-tokenization.md.

### שלב 5: הוראות קבע

הנתיב charge של recurring מחייב ויוצר הוראת קבע. הגדר Duration_Months בפריט (1 לחיוב חודשי), Recurrence (למשל 12), ו-Date_Start. נהל עם listforcustomer, update ו-cancel. שמור טוקן כרטיס דרך paymentmethods/setforcustomer לחיובים חוזרים.

### שלב 6: קליטת הוצאות

הנתיב addexpense דוחף הוצאת ספק עם קובץ Base64 (ExpenseFile), Supplier, Lines ו-Payments. כדי למשוך הוצאות ש-SUMIT קלטה אוטומטית (דרך קליטת ה-AI מוואטסאפ ומייל), קרא ל-documents/list עם DocumentTypes של הוצאה: ExpenseInvoice (16), ExpenseInvoiceReceipt (15), ExpenseReceipt (17).

### שלב 7: שאיבת נתונים (דוחות)

כל השליפות הן POST, כולן עם עימוד (Paging.PageSize בין 10 ל-1000):

- רשימת מסמכים: documents/list
- פרטי מסמך: documents/getdetails
- PDF של מסמך: documents/getpdf
- רשימת תשלומים: payments/list
- חוב לקוח: documents/getdebt ו-getdebtreport
- רשימת לקוחות: crm/data/listentities עם Folder של Customers ו-LoadProperties אמת

### שלב 8: קבלת נתונים בזמן אמת (webhooks)

שני ערוצי Push:
1. Triggers: הנתיב subscribe עם URL, Folder ו-TriggerType (CreateOrUpdate, Create, Update, Archive, Delete). מופעל על שינויי ישות.
2. IPN: העברת IPNURL ל-beginredirect מחזירה התראת שרת-לשרת על תוצאת תשלום.

אמת את מקור הבקשה, החזר HTTP 200 מהר, ואז עבד אסינכרונית ואידמפוטנטית.

## דוגמאות

### דוגמה 1: הפקת חשבונית מס-קבלה
המשתמש אומר: צור חשבונית מס-קבלה על 1000 בתוספת מע"מ ללקוח לפי מייל.
פעולות:
1. בנה את גוף documents/create עם Type של InvoiceAndReceipt, UnitPrice של 1000, VATIncluded שקר, VATRate של 18.
2. קרא דרך scripts/sumit_client.py.
3. קרא את DocumentNumber ו-DocumentDownloadURL מ-Data.
תוצאה: החשבונית הופקה, קישור PDF הוחזר.

### דוגמה 2: חיוב כרטיס שמור חודשי
המשתמש אומר: הקם סליקת אשראי חודשית של 99 שקלים.
פעולות:
1. טקן פעם אחת עם payments.js לקבלת og-token.
2. קרא ל-recurring/charge עם SingleUseToken, Duration_Months של 1, Recurrence של 12.
תוצאה: הוראת קבע נוצרה, החשבונית הראשונה הופקה.

### דוגמה 3: שאיבת הוצאות החודש
המשתמש אומר: שאיבת דוחות של הוצאות החודש.
פעולות:
1. קרא ל-documents/list עם DocumentTypes של ExpenseInvoice, ExpenseInvoiceReceipt, ExpenseReceipt וטווח DateFrom ו-DateTo.
2. דפדף עם Paging.
תוצאה: רשימת מסמכי הוצאה לתקופה.

## משאבים מצורפים

### סקריפטים
- scripts/sumit_client.py -- לקוח API ו-CLI ל-SUMIT ללא תלויות (stdlib בלבד): עוטף את מעטפת ה-Credentials, שולח JSON, וזורק שגיאה כש-Status אינו Success. הרצה: python scripts/sumit_client.py --help

### מסמכי עזר
- references/api-endpoints.md -- מפת כל 84 הפעולות ב-27 המודולים עם נתיבים ותיאור שורה. עיין כשצריך endpoint שלא מכוסה בשלבים.
- references/document-types-and-enums.md -- כל 23 סוגי המסמך, אמצעי תשלום, מטבעות, מצבי חיפוש ו-enum הסטטוס. עיין בבחירת Type או בפענוח ערך enum.
- references/payments-and-tokenization.md -- זרימת הסליקה התואמת PCI, הקמת payments.js, כרטיסים שמורים, הוראות קבע ודפי תשלום מתארחים. עיין במימוש כל מסלול סליקה.

## קישורי עזר

מקורות רשמיים לאימות ועדכון המידע ב-skill:

- SUMIT API (Swagger): https://app.sumit.co.il/help/developers/swagger/index.html -- רשימת endpoints חיה וסכמות
- מפרט OpenAPI: https://app.sumit.co.il/swagger/v1/swagger.json -- spec גולמי קריא-מכונה
- מרכז המידע למפתחים: https://help.sumit.co.il/he/collections/3333669 -- מדריכי אינטגרציה, בדיקות, מפתחות
- Payments JavaScript API: https://help.sumit.co.il/he/articles/5893615-payments-javascript-api -- טוקניזציה, BindFormSubmit, כרטיסי בדיקה

## נקודות חשובות

- כל פעולה היא POST, כולל כל השליפות. אין פועל REST לפי משאב; מחיקת ישות היא POST לנתיב crm/data/deleteentity.
- Credentials נמצא בגוף ה-JSON, לא בכותרת Authorization.
- HTTP 200 אינו אומר הצלחה. בדוק את שדה Status בכל תשובה.
- המפתח הסודי APIKey נשאר בצד-שרת. רק APIPublicKey מותר בדפדפן.
- השדה ResponseLanguage בגוף הבקשה מיושן; השתמש בכותרת Content-Language במקום.

## פתרון בעיות

### שגיאה: התשובה עם Status של BusinessError
סיבה: בעיה לוגית (חסר שם לקוח, אשראי נדחה, כשל ולידציה).
פתרון: הצג את UserErrorMessage למשתמש. אל תנסה שוב באופן עיוור; תקן את הקלט קודם.

### שגיאה: התשובה עם Status של TechnicalError
סיבה: תקלה זמנית או מערכתית בצד SUMIT.
פתרון: רשום ללוג את TechnicalErrorDetails, נסה שוב עם backoff, ודווח לתמיכת SUMIT אם נמשך.

### שגיאה: חיוב הכרטיס נכשל ללא טוקן
סיבה: השרת קיבל שדות כרטיס גולמיים במקום SingleUseToken.
פתרון: טקן בדפדפן עם payments.js קודם; השרת צריך לראות רק את og-token.
