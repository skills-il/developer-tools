# Zap Templates for Israeli Businesses

Ready-to-use Zap configurations for common Israeli business workflows. Each template includes the trigger, action chain, field mappings, and notes on customization.

All Israeli payment processors (Cardcom, Tranzila, Grow, Morning) send amounts in decimal shekels. No unit conversion is needed. Note that gateway amounts INCLUDE VAT, so divide by 1.18 before comparing against the Invoice Reform threshold, which is measured before VAT.

## Template 1: Cardcom Payment to Morning Receipt

**Use case:** Auto-generate a receipt (kabala) in Morning (formerly Green Invoice) when a customer pays through Cardcom.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Pass the webhook URL as `WebHookUrl` on your Cardcom `CreateLowProfile` request |
| 2. Filter | Filter by Zapier | Only Continue If | `ResponseCode` = 0 (successful payment) |
| 3. Format | Formatter by Zapier | Date/Time > Format | Input: current date, To Format: `DD/MM/YYYY` |
| 4. Action | Webhooks by Zapier | Custom Request | Fetch a Morning token, then POST to Morning API: Create Document type 320 (חשבונית מס/קבלה) |
| 5. Action | Gmail | Send Email | Send receipt link to customer |

**Morning API field mapping (Step 4):**

| Morning API Field | Source | Notes |
|-------------------|--------|-------|
| `type` | Static: `320` | חשבונית מס/קבלה. Use 320 rather than a bare 400 receipt for an osek murshe card sale: 320 is the tax invoice the customer deducts input VAT against, and the document an allocation number attaches to. |
| `lang` | Static: `he` | **Required.** The most commonly omitted field; without it the request 400s. |
| `client.name` | Step 1: `UIValues.CardOwnerName` | Hebrew names pass through as-is |
| `client.emails` | Step 1: `UIValues.CardOwnerEmail` | Array: `[UIValues.CardOwnerEmail]` |
| `income[].description` | Static or custom | e.g., "תשלום עבור שירות". Required per row. |
| `income[].price` | Step 1: `TranzactionInfo.Amount` | The callback has NO top-level `Amount`. Already decimal ILS, use as-is. Required per row. |
| `income[].quantity` | Static: `1` | Required per row. |
| `income[].currency` | Static: `ILS` | Required per row. |
| `income[].vatType` | Static: `0` (before VAT) or `1` (included) | Required per row. |
| `vatType` | Static: `0` (before VAT) or `1` (included) | **Required** at document level too. Ask user preference. |
| `currency` | Static: `ILS` | **Required.** |

**Customization options:**
- If the pre-VAT amount exceeds 5,000 ILS an Invoice Reform allocation number is required (since June 2026). Divide the gateway total by 1.18 before comparing: the threshold is measured before VAT. Note the create-document response does NOT return the allocation number; check `taxAuthorityConfirmationInitiated` / `taxAuthorityConfirmationLastError` on it, then read `allocationNumber` from a follow-up `GET /documents/{id}` or the `document/created` webhook.
- Add a Slack notification step for payments above a threshold
- For installment payments (tashlumim), include `UIValues.NumOfPayments` in the description
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
| Allocation Number | `allocationNumber`, from `GET /documents/{id}` or the `document/created` webhook, NOT from the create response | Required for invoices > 5,000 NIS before VAT since Jun 2026 |

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

**Note on WhatsApp:** use the **WhatsApp Business** app (not "WhatsApp Notifications", which only messages your own number). A proactive order confirmation falls outside the 24-hour customer-service window, so it needs a Meta-approved Hebrew template. Inside that window, `Send Freeform Message` sends arbitrary Hebrew.

---

## Template 4: Freelancer Monthly Invoice Reminder

**Use case:** Send monthly reminders to a freelancer (atzmai) about unpaid invoices and upcoming tax deadlines.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Every Month | Day: 1st of month |
| 2. Action | Webhooks by Zapier | Custom Request | POST to Morning API document search: unpaid documents from last 60 days (the search endpoint takes a JSON filter body, not GET query params) |
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
| 1. Trigger | Typeform | New Response | Or Google Forms or Wix Forms. Elementor has no Zapier app; its Pro Forms push to Zapier via a WordPress-side webhook, so use Catch Hook for those. |
| 2. Format | Code by Zapier | Run JavaScript | Clean Hebrew text and format phone |
| 3. Action | Monday.com | Create Item | Add lead to "Leads" board |
| 4. Action | Gmail | Send Email | Hebrew RTL welcome email |
| 5. Action | Delay by Zapier | Delay For | Wait 3 days (Schedule by Zapier is trigger-only and cannot be used as an action step) |
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

**Note:** For a WhatsApp greeting, use the **WhatsApp Business** app's `Send Template Message` with a Meta-approved Hebrew template. Do not use "WhatsApp Notifications", which only messages your own number.

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
| 2. Action | Webhooks by Zapier | Custom Request | POST to Morning API document search: documents for previous 2 months (the search endpoint takes a JSON filter body, not GET query params) |
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
  <p><em>תזכורת: מועד הדיווח לתקופה זו - {{deadlineDate}} (קראו אותו מטבלת המועדים השנתית, אל תקבעו את ה-15 בקוד)</em></p>
  <p><em>דוח זה נוצר אוטומטית. נא לאמת מול הנתונים במערכת.</em></p>
</div>
```

---

## Template 8: Multi-Channel Payment Consolidation

**Use case:** Consolidate payments from multiple Israeli processors (Cardcom, Tranzila, Grow, Morning direct) into a single Zapier Table.

**Implementation:** Create 4 separate Zaps, all writing to the same Zapier Table. All processors send amounts in decimal shekels.

**Zap A: Cardcom payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Cardcom `WebHookUrl` JSON POST callback)
2. Filter: `ResponseCode` = 0
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

| Column | Cardcom v11 Source | Tranzila Source (unverified) | Grow Source (unverified) | Morning Source |
|--------|---------------|-----------------|-------------|----------------|
| Date | Webhook timestamp | Webhook timestamp | Webhook timestamp | Document date |
| Source | Static: "Cardcom" | Static: "Tranzila" | Static: "Grow" | Static: "Morning" |
| Amount (ILS) | `TranzactionInfo.Amount` | `sum` | `amount` | `total` |
| Customer | `UIValues.CardOwnerName` | `contact` | `customer_name` | `client.name` |
| Reference | `TranzactionId` | `index` | `transaction_id` | Document number |
| Payment Method | Static: "Credit Card" | Static: "Credit Card" | `payment_method` | N/A |
| Installments | `UIValues.NumOfPayments` | `npay` | N/A | N/A |
| Status | (always "Completed") | (always "Completed") | (always "Completed") | Document status |


## Relocated from SKILL.md
### Step 9: Use Common Zap Templates for Israeli Businesses

**Template 1: Freelancer invoice-to-bookkeeping**
1. Trigger: Morning webhook (new document created)
2. Filter: Document type = Tax Invoice (305) or Tax Invoice/Receipt (320)
3. Action: Create record in Zapier Tables with columns: Date, Client Name, Amount (before VAT), VAT Amount, Total, Document Number
4. Action: If the pre-VAT amount exceeds the Invoice Reform threshold variable (currently 5,000 ILS), verify Invoice Reform allocation number is present
5. Action: If amount > 25,000 ILS, send Slack notification to accountant channel

**Template 2: E-commerce order-to-invoice**
1. Trigger: Shopify/WooCommerce > New Order
2. Action: Create document in Morning via Webhooks by Zapier (type: 320 Tax Invoice/Receipt or 400 Receipt based on business preference)
3. Action: Send email confirmation with receipt details (RTL HTML template)
4. Action: Update Monday.com board with order status

**Template 3: Payment-to-receipt (Cardcom)**
1. Trigger: Webhooks by Zapier (Cardcom `WebHookUrl` JSON POST callback)
2. Filter: `ResponseCode` = 0 (successful payment only)
3. Action: fetch a Morning token (POST `grant_type=client_credentials` to `https://api.morning.co/idp/v1/oauth/token`; it expires in 1 hour, so fetch per run), then Morning API > Create Document (type: 320 חשבונית מס/קבלה). Map the price from `TranzactionInfo.Amount`, already decimal shekels; there is no top-level `Amount`.
4. Action: Send email with receipt PDF link to customer
5. Action: Log to Zapier Tables for reconciliation

**Template 4: Lead capture to CRM follow-up**
1. Trigger: Typeform/Google Forms > New Response
2. Action: Code by Zapier to clean Hebrew text (strip Unicode directional markers)
3. Action: Create contact in CRM (Monday.com or HubSpot)
4. Action: Send welcome email with RTL HTML template
5. Action: Create follow-up task in Monday.com for 3 days later

**Template 5: Expense receipt categorization**
1. Trigger: Gmail > New Email with attachment matching "קבלה" or "חשבון"
2. Action: Code by Zapier to extract amount and categorize by sender
3. Filter: Only continue if amount is parseable
4. Action: Create record in Zapier Tables "Tax Deductions" with category column

**Template 6: Multi-gateway payment consolidation**
Create 3 separate Zaps, all writing to the same Zapier Table:
- Zap A: Cardcom `WebHookUrl` webhook -> Zapier Tables (Amount in decimal ILS)
- Zap B: Tranzila webhook -> Zapier Tables (sum in decimal ILS)
- Zap C: Grow by Meshulam webhook -> Zapier Tables (amount in decimal ILS)
All three processors send amounts in decimal shekels. No conversion needed.


### Step 5: Set Up Webhook-Based Israeli Integrations

Many Israeli payment processors and services do not have native Zapier integrations. Use webhooks to bridge the gap.

**Cardcom payment webhook as Zap trigger:**

Cardcom v11 uses a `WebHookUrl` callback. When a transaction completes, Cardcom sends a **JSON POST** to that URL carrying a `LowProfileResult` object. Key fields:

| Field | Description | Example |
|-------|-------------|---------|
| `ResponseCode` | Response code (0 = success) | `0` |
| `TranzactionId` | Credit-card transaction ID | `12345678` |
| `LowProfileId` | Unique ID of the low-profile transaction | `a1b2c3d4-...` |
| `ReturnValue` | Whatever you sent on the request, typically your order ID | `Z12332X` |
| `TranzactionInfo.Amount` | Payment amount in decimal shekels. There is NO top-level `Amount` on the callback; `TranzactionInfo` is null outside `ChargeOnly` / `ChargeAndCreateToken`. | `150.50` (= 150.50 ILS) |
| `UIValues.CardOwnerName` | Cardholder name | `ישראל ישראלי` |
| `UIValues.CardOwnerEmail` | Customer email | `israel@example.com` |
| `UIValues.CardOwnerPhone` | Customer phone | `0541234567` |
| `UIValues.NumOfPayments` | Installment count (tashlumim) | `3` |
| `Description` | Human-readable description of `ResponseCode` | `Success` |

Note the nesting: cardholder details live under `UIValues`, not at the top level. In Zapier's field mapper they appear as `UIValues CardOwnerName` and similar.

Cardcom amounts are in decimal shekels (e.g., 150.50 means 150.50 ILS). No conversion needed. Use the value directly in your invoice creation step.

**Tranzila payment webhook:**

**Unverified.** See the Tranzila caveat in Step 2. Tranzila's current documentation does not describe a merchant-panel webhook, and the `index` / `sum` / `ccno` / `npay` / `contact` / `email` / `phone` field names are the legacy redirect-response parameters rather than a documented server-to-server callback payload. Confirm the mechanism in the merchant panel before relying on it.

Cardcom sends amounts in decimal shekels. No unit conversion is needed.

**Grow by Meshulam payment webhook:**

Grow supports credit cards, Bit, Apple Pay, and Google Pay. Sends JSON POST webhooks:

| Field | Description | Example |
|-------|-------------|---------|
| `transaction_id` | Transaction ID | `GRW-123456` |
| `amount` | Amount in decimal ILS | `99.90` |
| `payment_method` | Payment type | `credit_card`, `bit`, `apple_pay`, `google_pay` |
| `customer_name` | Customer name | `ישראל ישראלי` |
| `customer_email` | Customer email | `israel@example.com` |
| `customer_phone` | Customer phone | `0541234567` |

**Bit payments:** Bit is Israel's dominant P2P payment app with growing business adoption. To accept Bit payments and trigger Zaps, use one of these gateways:
- Grow by Meshulam (native Bit support via their checkout page)
- Tranzila (Bit integration available)
- Direct Bit Business API (requires separate merchant agreement)



## Zap pattern index (relocated from SKILL.md Step 1)

Match the Israeli business need to the correct Zap architecture.

| Business Need | Zap Trigger | Action Chain | Israeli Apps |
|---------------|-------------|--------------|--------------|
| Auto-receipt after payment | Cardcom/Tranzila webhook | Parse payment -> Create Morning doc -> Email customer | Cardcom, Morning |
| Invoice-to-bookkeeping sync | Morning new document webhook | Map fields -> Create entry in Zapier Tables or accounting tool -> Tag VAT period | Morning, Zapier Tables |
| Payment reminder (freelancer) | Schedule trigger (bimonthly) | Query unpaid invoices -> Filter overdue -> Send Hebrew reminder | Morning, email/SMS provider |
| E-commerce order processing | WooCommerce/Shopify new order | Create invoice in Morning -> Send email confirmation -> Update Monday.com board | Morning, Monday.com |
| WhatsApp order confirmation | Payment webhook | Format Hebrew message -> Send via Twilio WhatsApp Business API | Twilio (WhatsApp Business) |
| Lead capture with CRM | Form submission (Typeform, Google Forms) | Extract Hebrew name -> Create CRM contact -> Send email follow-up | Monday.com, HubSpot |
| Multi-gateway consolidation | Multiple webhooks (Cardcom, Tranzila, Grow) | Normalize amounts -> Log to unified Zapier Table | Cardcom, Tranzila, Grow |

