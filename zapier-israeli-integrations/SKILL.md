---
name: zapier-israeli-integrations
description: Build Zapier Zaps that connect Israeli business apps (Green Invoice, Cardcom, Tranzila, Monday.com) with global services for billing, payment, and workflow automation. Use when user asks to "create a Zap for Israeli invoicing", "automate Green Invoice receipts", "connect Cardcom to my CRM", "lehavir heshbonit automatit", "otomatzia le-asakim", or set up Hebrew WhatsApp notifications from payment events. Handles Hebrew text in Zap steps, ILS currency formatting, bimonthly VAT period logic, and webhook-based triggers from Israeli payment processors. Do NOT use for n8n workflows (use n8n-hebrew-workflows), Make.com scenarios (use make-com-israeli-automations), or custom code automation without Zapier.
license: MIT
allowed-tools: Bash(curl:*) Bash(node:*) Bash(python:*)
compatibility: Requires Zapier account (free tier supports 5 single-step Zaps). Multi-step Zaps require paid plan. Webhook triggers require Zapier Premium or Webhooks by Zapier integration. No local dependencies.
---

# Zapier Israeli Integrations

## Instructions

### Step 1: Choose the Right Zap Pattern

Match the Israeli business need to the correct Zap architecture. Use this table to determine which trigger, action chain, and Israeli apps are involved.

| Business Need | Zap Trigger | Action Chain | Israeli Apps |
|---------------|-------------|--------------|--------------|
| Auto-receipt after payment | Cardcom/Tranzila webhook | Parse payment -> Create Green Invoice doc -> Email customer | Cardcom, Green Invoice |
| Lead-to-WhatsApp follow-up | Form submission (Typeform, Google Forms) | Extract Hebrew name -> Format greeting -> Send WhatsApp via Twilio | WhatsApp (Twilio), form provider |
| Invoice-to-bookkeeping sync | Green Invoice new document | Map fields -> Create entry in accounting tool -> Tag VAT period | Green Invoice, accounting tool |
| Payment reminder (freelancer) | Schedule trigger (bimonthly) | Query unpaid invoices -> Filter overdue -> Send Hebrew reminder | Green Invoice, email/SMS provider |
| E-commerce order processing | WooCommerce/Shopify new order | Create invoice in Green Invoice -> Send WhatsApp confirmation -> Update Monday.com board | Green Invoice, Monday.com |
| Expense categorization | Email (receipt attached) | Parse receipt -> Categorize by tax deduction type -> Log to spreadsheet | Gmail, Google Sheets |

**Choosing single-step vs multi-step:**
- Single-step Zaps (free tier): Direct trigger-to-action, e.g., "New Cardcom payment -> Create Google Sheets row"
- Multi-step Zaps (paid): Chain actions with logic, e.g., "New payment -> Create invoice -> Send WhatsApp -> Update CRM"
- Use Paths (branching) when the Zap needs to handle different scenarios, e.g., "If payment > 5,000 ILS, require manager approval"

### Step 2: Connect Israeli Apps in Zapier

Israeli apps connect to Zapier through three mechanisms. Choose based on what the app supports.

| App | Connection Method | Auth Type | Notes |
|-----|-------------------|-----------|-------|
| Green Invoice | Webhooks by Zapier | API key + Webhook | No native Zapier app exists in the Zapier directory. Connect via webhooks: use Green Invoice's webhook notifications as triggers and their REST API via Webhooks by Zapier for actions. Generate API key from Green Invoice dashboard under Settings > API. |
| Cardcom | Webhooks by Zapier | Webhook URL | Cardcom sends POST to Zapier catch hook on payment events. Configure in Cardcom terminal settings > Notifications. |
| Tranzila | Webhooks by Zapier | Webhook URL | Similar to Cardcom. Set notification URL in Tranzila merchant panel. |
| Monday.com | Zapier native integration | OAuth | Full support. Monday.com is a global app with strong Israeli adoption. |
| Rivhit (accounting) | Webhooks by Zapier | API key in header | No native integration. Use webhook + custom API calls. |
| Priority ERP | Webhooks by Zapier | Basic auth | Use Priority's REST API via webhook actions. |
| SMS providers (019, InforUMobile) | Webhooks by Zapier | API key | Send SMS via HTTP POST action with provider's API. |

**Green Invoice API key setup:**
1. Log in to Green Invoice dashboard
2. Navigate to Settings > API Integration (hagdarot > integratziat API)
3. Generate a new API key
4. In Zapier, use "Webhooks by Zapier" to connect via Green Invoice's REST API with the API key in the Authorization header

**Webhook-based connection setup (Cardcom, Tranzila):**
1. In Zapier, create a new Zap with "Webhooks by Zapier" as the trigger
2. Choose "Catch Hook" as the trigger event
3. Copy the generated webhook URL
4. In the payment processor's dashboard, paste the URL in the notification/callback URL field
5. Make a test payment to send sample data to Zapier
6. Map the webhook fields in subsequent Zap steps

### Step 3: Handle Hebrew Text in Zap Steps

Hebrew text requires special handling in Zapier to avoid display and encoding issues.

**Formatter steps for Hebrew:**
- Use "Formatter by Zapier > Text > Trim Whitespace" to clean Hebrew input that may carry invisible RTL/LTR markers (U+200F, U+200E)
- For name formatting: Hebrew names are "First Last" (no middle name convention). Use "Formatter > Text > Titlecase" only for English names. For Hebrew, pass through as-is.
- When concatenating Hebrew and English text (e.g., "Order #12345 - הזמנה חדשה"), place the English portion first, then Hebrew. Zapier renders mixed-direction text LTR by default.

**RTL-safe email templates:**
When sending HTML emails through Zapier, wrap Hebrew content with explicit direction:

```html
<div dir="rtl" style="text-align: right; font-family: Arial, sans-serif;">
  <p>שלום {{customer_name}},</p>
  <p>קיבלנו את התשלום שלך בסך {{amount}} ש"ח.</p>
  <p>מספר חשבונית: {{invoice_number}}</p>
</div>
```

**ILS currency formatting:**
Zapier's built-in currency formatter does not support ILS natively. Use Formatter by Zapier > Numbers > Format Number with these settings:
- Decimal places: 2
- Decimal separator: `.` (period)
- Thousands separator: `,` (comma)
- Then append " ש\"ח" (ILS in Hebrew) or " ILS" via a text concatenation step

**Date formatting for Israeli context:**
Israeli documents use DD/MM/YYYY. Use Formatter by Zapier > Date/Time > Format with:
- To Format: `DD/MM/YYYY`
- Do not use the default MM/DD/YYYY, which will confuse Israeli recipients

### Step 4: Build Israeli Billing Cycle Automations

Israeli tax reporting follows specific cycles. Build Zaps that align with these periods.

**Bimonthly VAT period Zaps (tekufat maam du-chodshit):**
Israeli businesses report VAT bimonthly: Jan-Feb, Mar-Apr, May-Jun, Jul-Aug, Sep-Oct, Nov-Dec. Use Schedule by Zapier with these settings:
- Trigger: "Every Month" on the 1st
- Add a Filter step: "Only continue if current month is odd" (January=1, March=3, etc.)
- This fires on the first day after each bimonthly period closes
- Action: Pull all invoices/receipts from the previous 2 months via Green Invoice API and compile for VAT reporting

**Quarterly advance payment reminders (mikdamot):**
Self-employed individuals pay advance tax payments quarterly. Set up reminders:
- Schedule trigger: Monthly on the 10th
- Filter: Only months 1, 4, 7, 10 (January, April, July, October)
- Action: Send reminder email with upcoming payment deadline and estimated amount

**Annual report triggers:**
- Schedule: January 15th
- Action: Compile annual summary from Green Invoice, send to accountant email
- Include: Total revenue, total expenses, VAT paid, tax withheld at source (nikui mas ba-makor)

**Key Israeli tax dates to encode in Zaps:**

| Date | Event | Zap Action |
|------|-------|------------|
| 15th of odd months | VAT report deadline | Send reminder 5 days before |
| 15th of Jan/Apr/Jul/Oct | Advance payment deadline | Send reminder + amount estimate |
| January 15 | Previous year annual summary | Compile and send to accountant |
| March 31 | Annual tax filing deadline (for self-employed with accountant) | Filing reminder |
| April 30 | Annual tax filing (without accountant extension) | Filing reminder |

### Step 5: Set Up Webhook-Based Israeli Integrations

Many Israeli payment processors and services do not have native Zapier integrations. Use webhooks to bridge the gap.

**Cardcom payment webhook as Zap trigger:**

Cardcom sends a POST request with payment details when a transaction completes. The payload typically includes:

| Field | Description | Example |
|-------|-------------|---------|
| `Transaction` | Transaction ID | `12345678` |
| `Amount` | Payment amount in agorot (divide by 100 for ILS) | `15000` (= 150.00 ILS) |
| `CardNum` | Last 4 digits | `1234` |
| `NumOfPayments` | Installment count (tashlumim) | `3` |
| `CustomerName` | Cardholder name | `ישראל ישראלי` |
| `Email` | Customer email | `israel@example.com` |
| `CustomFields` | Your custom data | varies |

Important: Cardcom sends amounts in agorot (agurot). Always divide by 100 to get ILS. Add a Formatter > Numbers > Math > Divide by 100 step immediately after the webhook trigger.

**Tranzila payment webhook:**

Similar to Cardcom but with different field names. Key fields:

| Cardcom Field | Tranzila Equivalent | Notes |
|---------------|---------------------|-------|
| `Transaction` | `index` | Transaction reference |
| `Amount` | `sum` | Already in ILS (not agorot) |
| `CardNum` | `ccno` | Last 4 digits |
| `NumOfPayments` | `npay` | Installments |

Note the critical difference: Tranzila `sum` is in ILS, Cardcom `Amount` is in agorot. Mixing this up is a common source of billing errors.

**Gov.il form submission webhooks:**
Some gov.il digital forms support notification webhooks. The response format varies by form, but generally:
- Content-Type: `application/json`
- Hebrew field values are UTF-8 encoded
- Date fields use DD/MM/YYYY
- Phone fields may include country code (+972) or local format (05x)

### Step 6: Use Common Zap Templates for Israeli Businesses

**Template 1: Freelancer invoice-to-bookkeeping (le-atzmaim)**
1. Trigger: Green Invoice > New Document Created
2. Filter: Document type = "Invoice" (hashbonit mas) or "Invoice-Receipt" (hashbonit mas kabala)
3. Action: Create row in Google Sheets with columns: Date, Client Name, Amount (before VAT), VAT Amount, Total, Document Number
4. Action: If amount > 25,000 ILS, send Slack notification to accountant channel

**Template 2: E-commerce order-to-invoice (le-chanut online)**
1. Trigger: Shopify/WooCommerce > New Order
2. Action: Create document in Green Invoice (type: receipt or invoice-receipt based on business preference)
3. Action: Send WhatsApp message via Twilio with Hebrew order confirmation
4. Action: Update Monday.com board with order status

**Template 3: Payment-to-receipt (tashlum le-kabala)**
1. Trigger: Webhooks by Zapier (Cardcom catch hook)
2. Action: Formatter > Math > Divide amount by 100 (agorot to ILS)
3. Action: Green Invoice > Create Document (type: Receipt)
4. Action: Send email with receipt PDF link to customer
5. Action: Log to Google Sheets for reconciliation

**Template 4: Lead capture to Hebrew CRM follow-up**
1. Trigger: Typeform/Google Forms > New Response
2. Action: Formatter > Text > Trim Whitespace (clean Hebrew input)
3. Action: Create contact in CRM (Monday.com or HubSpot)
4. Action: Send WhatsApp greeting in Hebrew via Twilio
5. Action: Schedule follow-up task in 3 days

**Template 5: Expense receipt to categorization (hozaot le-sivug)**
1. Trigger: Gmail > New Email with attachment matching "kabala" or "heshbon"
2. Action: Formatter > Extract receipt amount from email body
3. Filter: Only continue if amount is parseable
4. Action: Categorize by sender domain (known vendors) or keywords
5. Action: Append to "Tax Deductions" Google Sheet with category column

## Examples

### Example 1: Auto-Receipt for Cardcom Payments

User says: "I want to automatically create a Green Invoice receipt when someone pays through Cardcom"

Actions:
1. Create a Zap with Webhooks by Zapier > Catch Hook as trigger
2. Configure Cardcom to POST to the webhook URL on successful payment
3. Add Formatter step: divide `Amount` by 100 (agorot to ILS)
4. Add Green Invoice > Create Document action with type "Receipt" (kabala)
5. Map fields: customer name, email, amount, description from webhook payload
6. Add email action to send receipt link to customer

Result: Every successful Cardcom payment automatically generates a Green Invoice receipt and emails it to the customer.

### Example 2: Bimonthly VAT Summary

User says: "Send me a summary of all invoices at the end of each VAT period for my accountant"

Actions:
1. Create a Zap with Schedule by Zapier, running on the 1st of each month
2. Add Filter: Only continue if month number is odd (start of new VAT period)
3. Add Green Invoice > Find Documents action filtered to previous 2 months
4. Add Formatter to calculate total revenue, total VAT collected
5. Add Email action to accountant with summary table

Result: On the 1st of March, May, July, September, November, and January, an automated email goes to the accountant with the previous bimonthly period's invoice summary.

### Example 3: Hebrew WhatsApp Notification on Payment

User says: "Send a Hebrew WhatsApp message to customers when they pay"

Actions:
1. Set up payment webhook trigger (Cardcom or Tranzila)
2. Add Formatter to convert amount to ILS and format with " ש\"ח"
3. Add Formatter to construct Hebrew message: "שלום {{name}}, קיבלנו תשלום בסך {{amount}} ש\"ח. תודה!"
4. Add Twilio > Send WhatsApp Message action
5. Set "To" field to customer phone (ensure +972 prefix)

Result: Customer receives a Hebrew WhatsApp confirmation within seconds of payment.

### Example 4: Freelancer End-of-Year Automation

User says: "I need a Zap that compiles my annual invoice summary for tax filing"

Actions:
1. Create a Zap with Schedule by Zapier, running January 15th
2. Add Green Invoice > Find Documents for the entire previous year
3. Add Code by Zapier step to calculate totals: revenue, expenses, VAT, withholding tax
4. Add Gmail action to send formatted summary to accountant
5. Add Google Sheets action to archive the annual summary

Result: Annual tax preparation data is automatically compiled and sent to the accountant every January.

## Bundled Resources

### References
- `references/israeli-zapier-apps.md` -- Directory of Israeli apps available on Zapier (native integrations and webhook-based connections), including auth methods, API endpoints, and field mappings. Consult when connecting a new Israeli app to Zapier or troubleshooting authentication.
- `references/zap-templates.md` -- Ready-to-use Zap template configurations for common Israeli business workflows, with step-by-step field mappings and trigger/action details. Consult when building a new Zap and looking for a starting point that fits an Israeli business scenario.

## Gotchas

- **Agorot vs ILS confusion**: Cardcom sends amounts in agorot (1/100 of a shekel), but Tranzila sends amounts in ILS. Agents often assume all payment amounts are in the same unit. Always check which processor is being used and add a divide-by-100 step for Cardcom.
- **Date format mismatch**: Zapier defaults to US date format (MM/DD/YYYY). Israeli documents, invoices, and tax forms use DD/MM/YYYY. Always add an explicit date formatter step. Failing to do so can cause invoice dates like "03/01/2026" to mean January 3rd instead of March 1st.
- **Hebrew in code steps**: When using "Code by Zapier" (JavaScript or Python), Hebrew string literals in the code block work fine, but Hebrew in variable names will break. Keep variable names in English, use Hebrew only in string values.
- **Green Invoice document types**: Agents often default to "Invoice" (hashbonit mas) when the user needs "Invoice-Receipt" (hashbonit mas kabala) or "Receipt" (kabala). Ask the user which document type they need. In Israel, a receipt (kabala) is issued after payment, an invoice (hashbonit mas) before or at time of sale, and an invoice-receipt (hashbonit mas kabala) combines both.
- **Phone number format for WhatsApp**: Israeli mobile numbers must include the +972 prefix and drop the leading 0 (e.g., 0541234567 becomes +972541234567). Agents tend to pass the local format, which causes Twilio WhatsApp sends to fail silently.
- **VAT rate**: The current Israeli VAT rate is 18% (as of January 2025). Agents sometimes use the outdated 17% rate in calculations. Always verify the current rate before building tax-related Zap steps.
- **Zapier Hebrew search**: When searching for Israeli apps in Zapier's app directory, search in English ("Green Invoice", not "חשבונית ירוקה"). The app names in Zapier are in English even for Israeli-origin apps.
- **Free tier limitations**: Zapier's free tier only supports single-step Zaps (one trigger, one action). Most Israeli business automations require multi-step Zaps (e.g., trigger -> format -> create invoice -> send email). Make sure the user knows they need a paid plan for real workflows.

## Troubleshooting

### Error: "Webhook not receiving data from Cardcom"
Cause: Cardcom webhook URL is misconfigured or the terminal is in test mode
Solution: Verify the webhook URL in Cardcom terminal settings under "Notifications" (hatharot). Ensure the terminal is in production mode, not sandbox. Make a real small-amount payment (1 ILS) to test. Check Zapier's webhook history for incoming requests.

### Error: "Green Invoice returns 401 Unauthorized"
Cause: API key is invalid or expired
Solution: Generate a new API key from Green Invoice dashboard (Settings > API Integration). Re-authenticate the Green Invoice connection in Zapier. API keys do not expire automatically, so this usually means the key was regenerated or the account plan changed.

### Error: "Hebrew text appears garbled in emails"
Cause: Email template missing UTF-8 charset or RTL direction
Solution: Wrap Hebrew content in a `<div dir="rtl">` tag. Ensure the email HTML includes `<meta charset="UTF-8">` in the head. If using plain text email, Hebrew should display correctly in modern clients but may appear reversed in older ones.

### Error: "Amount is 100x too large in Green Invoice"
Cause: Cardcom webhook amount is in agorot, not ILS
Solution: Add a Formatter > Numbers > Math > Divide by 100 step between the webhook trigger and the Green Invoice action. This is the single most common error in Cardcom-to-Green Invoice Zaps.
