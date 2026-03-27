# Zap Templates for Israeli Businesses

Ready-to-use Zap configurations for common Israeli business workflows. Each template includes the trigger, action chain, field mappings, and notes on customization.

All Israeli payment processors (Cardcom, Tranzila, Grow, Morning) send amounts in decimal shekels. No unit conversion is needed.

## Template 1: Cardcom Payment to Morning Receipt

**Use case:** Auto-generate a receipt (kabala) in Morning (formerly Green Invoice) when a customer pays through Cardcom.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Copy webhook URL to Cardcom terminal IndicatorUrl |
| 2. Filter | Filter by Zapier | Only Continue If | `DealResponse` = 0 (successful payment) |
| 3. Format | Formatter by Zapier | Date/Time > Format | Input: current date, To Format: `DD/MM/YYYY` |
| 4. Action | Webhooks by Zapier | Custom Request | POST to Morning API: Create Document type 400 (Receipt) |
| 5. Action | Gmail | Send Email | Send receipt link to customer |

**Morning API field mapping (Step 4):**

| Morning API Field | Source | Notes |
|-------------------|--------|-------|
| `type` | Static: `400` | Receipt (kabala) |
| `client.name` | Step 1: `CardOwnerName` | Hebrew names pass through as-is |
| `client.emails` | Step 1: `CardOwnerEmail` | Array: `[CardOwnerEmail]` |
| `items[].description` | Static or custom | e.g., "תשלום עבור שירות" |
| `items[].unitPrice` | Step 1: `Amount` | Already in decimal ILS (e.g., 150.50). Use as-is. |
| `items[].quantity` | Static: `1` | |
| `vatType` | Static: `0` (before VAT) or `1` (included) | Ask user preference |
| `currency` | Static: `ILS` | |

**Customization options:**
- For amounts > 10,000 ILS, verify the Morning API response includes an Invoice Reform allocation number (required since January 2026)
- Add a Slack notification step for payments above a threshold
- For installment payments (tashlumim), include `NumOfPayments` in the description
- Use Zapier Tables instead of Gmail for logging (simpler, no external auth needed)

---

## Template 2: Morning to Zapier Tables Bookkeeping Log

**Use case:** Automatically log every new Morning document to a Zapier Table for bookkeeping. (Alternative: use Google Sheets if the accountant needs direct spreadsheet access.)

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Configure Morning webhook to fire on new document creation |
| 2. Filter | Filter by Zapier | Only Continue If | Document type is 305 (Invoice), 320 (Invoice-Receipt), or 400 (Receipt) |
| 3. Format | Formatter by Zapier | Numbers > Format Number | Format amount with 2 decimal places |
| 4. Action | Zapier Tables | Create Record | Map fields to columns |

**Zapier Tables columns and mapping (Step 4):**

| Column | Source | Notes |
|--------|--------|-------|
| Date | Step 1: `date` | Reformat to DD/MM/YYYY if needed |
| Document Number | Step 1: `number` | e.g., "1001" |
| Document Type | Step 1: `type` | Map code: 305=Invoice, 320=Invoice-Receipt, 400=Receipt |
| Client Name | Step 1: `client.name` | |
| Amount Before VAT | Step 1: `amount` (calculated) | Total minus VAT |
| VAT Amount | Step 1: `vat` | |
| Total Amount | Step 1: `total` | |
| Payment Status | Step 1: `status` | Paid / Unpaid / Partially Paid |
| VAT Period | Step 1: derive from date | e.g., "Jan-Feb 2026" |
| Allocation Number | Step 1: `allocationNumber` | Required for invoices > 10,000 NIS since Jan 2026 |

**VAT period derivation:**
Use Formatter > Date/Time to extract the month number, then use a Lookup Table:
- Months 1-2: "Jan-Feb" (ינואר-פברואר)
- Months 3-4: "Mar-Apr" (מרץ-אפריל)
- Months 5-6: "May-Jun" (מאי-יוני)
- Months 7-8: "Jul-Aug" (יולי-אוגוסט)
- Months 9-10: "Sep-Oct" (ספטמבר-אוקטובר)
- Months 11-12: "Nov-Dec" (נובמבר-דצמבר)

---

## Template 3: E-Commerce Order to Invoice + Email Confirmation

**Use case:** When an order comes in from Shopify or WooCommerce, create a Morning document and send an email confirmation in Hebrew.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Shopify | New Order | Or WooCommerce > New Order |
| 2. Format | Code by Zapier | Run JavaScript | Clean Hebrew text and format phone number |
| 3. Action | Webhooks by Zapier | Custom Request | POST to Morning API: Create Document type 320 (Invoice-Receipt) |
| 4. Action | Gmail | Send Email | Hebrew RTL confirmation email |
| 5. Action | Monday.com | Create Item | Track order in board |

**Phone formatting and Hebrew text cleaning (Step 2):**

```javascript
const phone = inputData.phone.replace(/^0/, '+972');
const name = inputData.name.replace(/[\u200F\u200E\u200B\u200C\u200D\uFEFF]/g, '').trim();
output = [{phone: phone, name: name}];
```

**Note on WhatsApp:** Zapier's native WhatsApp integration cannot send messages to customers. If WhatsApp confirmation is needed, use Twilio WhatsApp Business API with a Meta-approved Hebrew template. This requires separate Meta Business verification and template approval (24-48 hours).

---

## Template 4: Freelancer Monthly Invoice Reminder

**Use case:** Send monthly reminders to a freelancer (atzmai) about unpaid invoices and upcoming tax deadlines.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Every Month | Day: 1st of month |
| 2. Action | Webhooks by Zapier | Custom Request | GET Morning API: Find unpaid documents from last 60 days |
| 3. Filter | Filter by Zapier | Only Continue If | Step 2 returns results |
| 4. Action | Code by Zapier | Run JavaScript | Sum outstanding amounts |
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

## Template 5: Form Submission to CRM + Email Follow-up

**Use case:** Capture leads from a Hebrew form and automatically add to CRM with email follow-up.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Typeform | New Response | Or Google Forms, Elementor, Wix Forms |
| 2. Format | Code by Zapier | Run JavaScript | Clean Hebrew text and format phone |
| 3. Action | Monday.com | Create Item | Add lead to "Leads" board |
| 4. Action | Gmail | Send Email | Hebrew RTL welcome email |
| 5. Action | Schedule by Zapier | Delay | Wait 3 days |
| 6. Action | Gmail | Send Email | Follow-up email |

**Hebrew text cleaning (Step 2):**

```javascript
const phone = inputData.phone.replace(/^0/, '+972');
const name = inputData.name.replace(/[\u200F\u200E\u200B\u200C\u200D\uFEFF]/g, '').trim();
output = [{phone: phone, name: name}];
```

**Monday.com board setup (Step 3):**

| Column | Type | Mapping |
|--------|------|---------|
| Name | Text | Lead's full name from form |
| Status | Status | "New Lead" (ליד חדש) |
| Phone | Phone | Formatted +972 number |
| Email | Email | From form |
| Source | Text | Form name/platform |
| Date | Date | Submission date |

**Note:** For WhatsApp greeting, use Twilio WhatsApp Business API with a Meta-approved template. Zapier's native WhatsApp cannot send to customers.

---

## Template 6: Expense Receipt Categorization

**Use case:** Automatically categorize expense receipts from email and log them for tax deduction purposes.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Gmail | New Email | Match subject or body containing "קבלה", "חשבונית", "receipt" |
| 2. Format | Formatter by Zapier | Text > Extract Pattern | Extract amount using regex |
| 3. Action | Code by Zapier | Run JavaScript | Categorize by sender |
| 4. Action | Zapier Tables | Create Record | Log to expenses table |

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

**Zapier Tables columns (Step 4):**

| Column | Source |
|--------|--------|
| Date | Email received date |
| Sender | Email sender |
| Subject | Email subject |
| Amount | Step 2 extracted amount |
| Category | Step 3 category output |
| Tax Deductible | Dropdown based on category |
| VAT Period | Derived from date |
| Notes | (empty, for manual annotation) |

---

## Template 7: Bimonthly VAT Period Summary

**Use case:** Automatically compile and send a VAT period summary at the end of each bimonthly period.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Specific months | March, May, July, September, November, January on the 10th |
| 2. Action | Webhooks by Zapier | Custom Request | GET Morning API: Find documents for previous 2 months |
| 3. Action | Code by Zapier | Run JavaScript | Calculate totals |
| 4. Action | Gmail | Send Email | Summary to accountant |
| 5. Action | Zapier Tables | Create Record | Archive period summary |

**Calculation logic (Step 3):**

```javascript
const docs = JSON.parse(inputData.documents);
let totalRevenue = 0;
let totalVAT = 0;
let invoiceCount = 0;
let receiptCount = 0;

for (const doc of docs) {
  if (doc.type === 305 || doc.type === 320) {
    totalRevenue += doc.amount;
    totalVAT += doc.vat;
    invoiceCount++;
  }
  if (doc.type === 400) {
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

**Accountant email template (Step 4):**

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
  <p><em>תזכורת: מועד הדיווח - 15 לחודש (19 בדיווח מקוון)</em></p>
  <p><em>דוח זה נוצר אוטומטית. נא לאמת מול הנתונים במערכת.</em></p>
</div>
```

---

## Template 8: Multi-Channel Payment Consolidation

**Use case:** Consolidate payments from multiple Israeli processors (Cardcom, Tranzila, Grow, Morning direct) into a single Zapier Table.

**Implementation:** Create 4 separate Zaps, all writing to the same Zapier Table. All processors send amounts in decimal shekels.

**Zap A: Cardcom payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Cardcom IndicatorUrl GET callback)
2. Filter: `DealResponse` = 0
3. Action: Zapier Tables > Create Record

**Zap B: Tranzila payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Tranzila webhook)
2. Action: Zapier Tables > Create Record

**Zap C: Grow by Meshulam payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Grow JSON webhook)
2. Action: Zapier Tables > Create Record

**Zap D: Morning direct payments**
1. Trigger: Morning webhook (document status = "paid")
2. Action: Zapier Tables > Create Record

**Shared Zapier Tables columns:**

| Column | Cardcom Source | Tranzila Source | Grow Source | Morning Source |
|--------|---------------|-----------------|-------------|----------------|
| Date | Webhook timestamp | Webhook timestamp | Webhook timestamp | Document date |
| Source | Static: "Cardcom" | Static: "Tranzila" | Static: "Grow" | Static: "Morning" |
| Amount (ILS) | `Amount` | `sum` | `amount` | `total` |
| Customer | `CardOwnerName` | `contact` | `customer_name` | `client.name` |
| Reference | `InternalDealNumber` | `index` | `transaction_id` | Document number |
| Payment Method | Static: "Credit Card" | Static: "Credit Card" | `payment_method` | N/A |
| Installments | `NumOfPayments` | `npay` | N/A | N/A |
| Status | (always "Completed") | (always "Completed") | (always "Completed") | Document status |
