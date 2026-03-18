# Zap Templates for Israeli Businesses

Ready-to-use Zap configurations for common Israeli business workflows. Each template includes the trigger, action chain, field mappings, and notes on customization.

## Template 1: Cardcom Payment to Green Invoice Receipt

**Use case:** Auto-generate a receipt (kabala) in Green Invoice when a customer pays through Cardcom.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Copy webhook URL to Cardcom terminal > Notifications |
| 2. Format | Formatter by Zapier | Math > Divide | Input: `Amount`, Operation: Divide, Value: `100` |
| 3. Format | Formatter by Zapier | Date/Time > Format | Input: current date, To Format: `DD/MM/YYYY` |
| 4. Action | Green Invoice | Create Document | Type: Receipt, fields mapped below |
| 5. Action | Gmail | Send Email | Send receipt link to customer |

**Green Invoice field mapping (Step 4):**

| Green Invoice Field | Source | Notes |
|---------------------|--------|-------|
| Document Type | Static: `Receipt` | Use "Receipt" for post-payment documents |
| Client Name | Step 1: `CustomerName` | Hebrew names pass through as-is |
| Client Email | Step 1: `Email` | |
| Item Description | Static or Step 1: `CustomFields` | e.g., "תשלום עבור שירות" |
| Item Price | Step 2: output (divided amount) | This is the ILS amount |
| Item Quantity | Static: `1` | |
| VAT Type | Static: `0` (before VAT) or `1` (included) | Ask user preference |
| Currency | Static: `ILS` | |
| Date | Step 3: formatted date | DD/MM/YYYY |

**Customization options:**
- Add a Filter after Step 1 to only process successful payments (`ResponseCode` = `0`)
- Add a Slack notification step for payments above a threshold
- For installment payments (tashlumim), include `NumOfPayments` in the description

---

## Template 2: Green Invoice to Google Sheets Bookkeeping Log

**Use case:** Automatically log every new Green Invoice document to a Google Sheets spreadsheet for bookkeeping.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Green Invoice | New Document Created | Triggers on any new document |
| 2. Filter | Filter by Zapier | Only Continue If | Document type is Invoice, Receipt, or Invoice-Receipt |
| 3. Format | Formatter by Zapier | Numbers > Format Number | Format amount with 2 decimal places |
| 4. Action | Google Sheets | Create Spreadsheet Row | Map fields to columns |

**Google Sheets columns and mapping (Step 4):**

| Column | Source | Notes |
|--------|--------|-------|
| A: Date | Step 1: `date` | Reformat to DD/MM/YYYY if needed |
| B: Document Number | Step 1: `number` | e.g., "1001" |
| C: Document Type | Step 1: `type` | Invoice / Receipt / Invoice-Receipt |
| D: Client Name | Step 1: `client.name` | |
| E: Amount Before VAT | Step 1: `amount` (calculated) | Total minus VAT |
| F: VAT Amount | Step 1: `vat` | |
| G: Total Amount | Step 1: `total` | |
| H: Payment Status | Step 1: `status` | Paid / Unpaid / Partially Paid |
| I: VAT Period | Step 1: derive from date | e.g., "Jan-Feb 2026" |

**VAT period derivation:**
Use Formatter > Date/Time to extract the month number, then use a Lookup Table:
- Months 1-2: "Jan-Feb" (ינואר-פברואר)
- Months 3-4: "Mar-Apr" (מרץ-אפריל)
- Months 5-6: "May-Jun" (מאי-יוני)
- Months 7-8: "Jul-Aug" (יולי-אוגוסט)
- Months 9-10: "Sep-Oct" (ספטמבר-אוקטובר)
- Months 11-12: "Nov-Dec" (נובמבר-דצמבר)

---

## Template 3: E-Commerce Order to Invoice + WhatsApp Confirmation

**Use case:** When an order comes in from Shopify or WooCommerce, create a Green Invoice document and send a WhatsApp confirmation in Hebrew.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Shopify | New Order | Or WooCommerce > New Order |
| 2. Format | Formatter by Zapier | Text > Trim Whitespace | Clean customer name (Hebrew input) |
| 3. Format | Formatter by Zapier | Phone > Format | Convert to +972 format |
| 4. Action | Green Invoice | Create Document | Type: Invoice-Receipt |
| 5. Action | Twilio | Send WhatsApp Message | Hebrew confirmation |
| 6. Action | Monday.com | Create Item | Track order in board |

**Phone formatting (Step 3):**
Israeli mobile: remove leading `0`, prepend `+972`
- Input: `0541234567`
- Formatter: Text > Replace (find: `^0`, replace: `+972`)
- Output: `+972541234567`

If Formatter regex is not available, use a Code by Zapier step:
```javascript
const phone = inputData.phone.replace(/^0/, '+972');
output = [{phone: phone}];
```

**WhatsApp message template (Step 5):**

| Field | Value |
|-------|-------|
| To | Step 3 output (formatted phone) |
| Body | See Hebrew template below |

Hebrew message:
```
שלום {{customer_name}},

ההזמנה שלך מספר {{order_number}} התקבלה בהצלחה.

סה"כ: {{total}} ש"ח
סטטוס: בטיפול

תודה שקנית אצלנו!
```

---

## Template 4: Freelancer Monthly Invoice Reminder

**Use case:** Send monthly reminders to a freelancer (atzmai) about unpaid invoices and upcoming tax deadlines.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Every Month | Day: 1st of month |
| 2. Action | Green Invoice | Find Documents | Filter: unpaid invoices from last 60 days |
| 3. Filter | Filter by Zapier | Only Continue If | Step 2 returns results |
| 4. Format | Formatter by Zapier | Numbers | Sum up outstanding amounts |
| 5. Action | Gmail | Send Email | Summary to self or accountant |

**Email template (Step 5):**

Subject: "סיכום חשבוניות פתוחות - {{current_month}} {{current_year}}"

```html
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <h2>סיכום חשבוניות פתוחות</h2>
  <p>נכון ל-{{date}}, יש לך {{count}} חשבוניות שטרם שולמו:</p>
  <p><strong>סה"כ חוב פתוח: {{total}} ש"ח</strong></p>
  <hr>
  <p><em>תזכורת: מועד דיווח מע"מ הבא - {{next_vat_deadline}}</em></p>
</div>
```

---

## Template 5: Form Submission to CRM + Hebrew WhatsApp

**Use case:** Capture leads from a Hebrew form and automatically add to CRM and send WhatsApp greeting.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Typeform | New Response | Or Google Forms, Elementor, Wix Forms |
| 2. Format | Formatter by Zapier | Text > Trim Whitespace | Clean Hebrew text fields |
| 3. Format | Formatter by Zapier | Phone > Format | Convert to +972 |
| 4. Action | Monday.com | Create Item | Add lead to "Leads" board |
| 5. Action | Twilio | Send WhatsApp Message | Hebrew welcome message |
| 6. Action | Schedule by Zapier | Delay | Wait 3 days |
| 7. Action | Gmail | Send Email | Follow-up email |

**Monday.com board setup (Step 4):**

| Column | Type | Mapping |
|--------|------|---------|
| Name | Text | Lead's full name from form |
| Status | Status | "New Lead" (ליד חדש) |
| Phone | Phone | Formatted +972 number |
| Email | Email | From form |
| Source | Text | Form name/platform |
| Date | Date | Submission date |

---

## Template 6: Expense Receipt Categorization

**Use case:** Automatically categorize expense receipts from email and log them for tax deduction purposes.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Gmail | New Email | Match subject or body containing "קבלה", "חשבונית", "receipt" |
| 2. Format | Formatter by Zapier | Text > Extract Pattern | Extract amount using regex |
| 3. Action | Code by Zapier | Run JavaScript | Categorize by sender |
| 4. Action | Google Sheets | Create Spreadsheet Row | Log to expenses sheet |

**Categorization logic (Step 3):**

```javascript
const sender = inputData.sender_email.toLowerCase();
const subject = inputData.subject || '';

let category = 'other';

const categories = {
  'office': ['office depot', 'mahsanei', 'kravitz'],
  'telecom': ['partner', 'cellcom', 'pelephone', 'hot', 'bezeq'],
  'internet': ['netvision', 'smile', '013'],
  'fuel': ['paz', 'delek', 'sonol', 'amisragas'],
  'software': ['google', 'microsoft', 'adobe', 'github', 'aws', 'vercel'],
  'insurance': ['harel', 'migdal', 'phoenix', 'clal', 'menora'],
  'vehicle': ['test-il', 'rav-kav', 'parking'],
  'meals': ['wolt', 'tenbis', 'cibus', 'japanika', 'aroma']
};

for (const [cat, keywords] of Object.entries(categories)) {
  if (keywords.some(kw => sender.includes(kw) || subject.includes(kw))) {
    category = cat;
    break;
  }
}

output = [{category: category}];
```

**Google Sheets columns (Step 4):**

| Column | Source |
|--------|--------|
| Date | Email received date |
| Sender | Email sender |
| Subject | Email subject |
| Amount | Step 2 extracted amount |
| Category | Step 3 category output |
| Tax Deductible | Formula based on category (in sheet) |
| VAT Period | Derived from date |
| Notes | (empty, for manual annotation) |

---

## Template 7: Bimonthly VAT Period Summary

**Use case:** Automatically compile and send a VAT period summary at the end of each bimonthly period.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Every Month | Day: 1st |
| 2. Filter | Filter by Zapier | Only Continue If | Month is odd (1, 3, 5, 7, 9, 11) |
| 3. Action | Green Invoice | Find Documents | Date range: previous 2 months |
| 4. Action | Code by Zapier | Run JavaScript | Calculate totals |
| 5. Action | Gmail | Send Email | Summary to accountant |

**Calculation logic (Step 4):**

```javascript
const docs = JSON.parse(inputData.documents);
let totalRevenue = 0;
let totalVAT = 0;
let invoiceCount = 0;
let receiptCount = 0;

for (const doc of docs) {
  if (doc.type === 'invoice' || doc.type === 'invoice_receipt') {
    totalRevenue += doc.amount;
    totalVAT += doc.vat;
    invoiceCount++;
  }
  if (doc.type === 'receipt') {
    receiptCount++;
  }
}

output = [{
  totalRevenue: totalRevenue.toFixed(2),
  totalVAT: totalVAT.toFixed(2),
  totalWithVAT: (totalRevenue + totalVAT).toFixed(2),
  invoiceCount: invoiceCount,
  receiptCount: receiptCount
}];
```

**Accountant email template (Step 5):**

Subject: "סיכום תקופת מע"מ {{period}} {{year}}"

```html
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <h2>סיכום תקופת מע"מ</h2>
  <table border="1" cellpadding="8" style="border-collapse: collapse; direction: rtl;">
    <tr><td>תקופה</td><td>{{period}}</td></tr>
    <tr><td>מספר חשבוניות</td><td>{{invoiceCount}}</td></tr>
    <tr><td>מספר קבלות</td><td>{{receiptCount}}</td></tr>
    <tr><td>סה"כ הכנסות (לפני מע"מ)</td><td>{{totalRevenue}} ש"ח</td></tr>
    <tr><td>סה"כ מע"מ</td><td>{{totalVAT}} ש"ח</td></tr>
    <tr><td>סה"כ כולל מע"מ</td><td>{{totalWithVAT}} ש"ח</td></tr>
  </table>
  <p><em>דוח זה נוצר אוטומטית. נא לאמת מול הנתונים במערכת.</em></p>
</div>
```

---

## Template 8: Multi-Channel Payment Consolidation

**Use case:** Consolidate payments from multiple Israeli processors (Cardcom, Tranzila, Green Invoice direct) into a single tracking sheet.

**Implementation:** Create 3 separate Zaps, all writing to the same Google Sheet.

**Zap A: Cardcom payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Cardcom webhook)
2. Format: Divide amount by 100 (agorot to ILS)
3. Action: Google Sheets > Create Row

**Zap B: Tranzila payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Tranzila webhook)
2. Action: Google Sheets > Create Row (amount already in ILS)

**Zap C: Green Invoice payments**
1. Trigger: Green Invoice > Document Status Changed (status = "paid")
2. Action: Google Sheets > Create Row

**Shared Google Sheets columns:**

| Column | Cardcom Source | Tranzila Source | Green Invoice Source |
|--------|---------------|-----------------|----------------------|
| Date | Webhook timestamp | Webhook timestamp | Document date |
| Source | Static: "Cardcom" | Static: "Tranzila" | Static: "Green Invoice" |
| Amount (ILS) | `Amount` / 100 | `sum` | `total` |
| Customer | `CustomerName` | `contact` | `client.name` |
| Reference | `Transaction` | `index` | Document number |
| Installments | `NumOfPayments` | `npay` | (N/A) |
| Status | (always "Completed") | (always "Completed") | Document status |
