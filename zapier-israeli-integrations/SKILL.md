---
name: zapier-israeli-integrations
description: Build Zapier Zaps connecting Israeli business apps (Morning/Green Invoice, Cardcom, Tranzila, iCount, Grow) with global services for billing, payment, and workflow automation. Use when asked to "create a Zap for Israeli invoicing", "automate Morning receipts", "connect Cardcom to my CRM", or set up payment notifications. Covers Hebrew text handling, ILS formatting, bimonthly VAT logic, Invoice Reform 2026, Zapier AI (Copilot, Agents, MCP), and webhooks from Israeli processors. All amounts use decimal shekels, not agorot. Customer WhatsApp requires Twilio/WATI (not Zapier native). Do NOT use for n8n (use n8n-hebrew-workflows), Make.com (use make-com-israeli-automations), or non-Zapier automation.
license: MIT
allowed-tools: Bash(curl:*) Bash(node:*) Bash(python:*)
compatibility: Requires Zapier account. Free plan includes unlimited two-step Zaps, 100 tasks/month, Copilot AI, Tables, and Interfaces. Multi-step Zaps require the Starter plan ($19.99/month annual, $29.99 monthly, 750 tasks); Professional ($49/month annual, 2,000 tasks) adds advanced features like custom logic and conditional steps. Webhook triggers use Webhooks by Zapier (available on all plans). No local dependencies.
---

# Zapier Israeli Integrations

## Instructions

### Step 1: Choose the Right Zap Pattern

Match the Israeli business need to the correct Zap architecture.

| Business Need | Zap Trigger | Action Chain | Israeli Apps |
|---------------|-------------|--------------|--------------|
| Auto-receipt after payment | Cardcom/Tranzila webhook | Parse payment -> Create Morning doc -> Email customer | Cardcom, Morning |
| Invoice-to-bookkeeping sync | Morning new document webhook | Map fields -> Create entry in Zapier Tables or accounting tool -> Tag VAT period | Morning, Zapier Tables |
| Payment reminder (freelancer) | Schedule trigger (bimonthly) | Query unpaid invoices -> Filter overdue -> Send Hebrew reminder | Morning, email/SMS provider |
| E-commerce order processing | WooCommerce/Shopify new order | Create invoice in Morning -> Send email confirmation -> Update Monday.com board | Morning, Monday.com |
| WhatsApp order confirmation | Payment webhook | Format Hebrew message -> Send via Twilio WhatsApp Business API | Twilio (WhatsApp Business) |
| Expense categorization | Email (receipt attached) | Parse receipt -> Categorize by tax deduction type -> Log to Zapier Tables | Gmail, Zapier Tables |
| Lead capture with CRM | Form submission (Typeform, Google Forms) | Extract Hebrew name -> Create CRM contact -> Send email follow-up | Monday.com, HubSpot |
| Multi-gateway consolidation | Multiple webhooks (Cardcom, Tranzila, Grow) | Normalize amounts -> Log to unified Zapier Table | Cardcom, Tranzila, Grow |

**Choosing single-step vs multi-step:**
- Single-step Zaps (free plan): Direct trigger-to-action, e.g., "New Cardcom payment -> Create Zapier Tables row." Free plan includes unlimited Zaps but only two-step (one trigger, one action), 100 tasks/month, and 15-minute polling.
- Multi-step Zaps (Starter plan, $19.99/month annual or $29.99/month monthly, 750 tasks): Chain actions with logic, e.g., "New payment -> Create invoice -> Send email -> Update CRM". The Professional plan ($49/month annual, 2,000 tasks) adds advanced features like conditional steps and filters.
- Use Paths (branching) when the Zap needs to handle different scenarios, e.g., "If payment is over the Invoice Reform threshold (10,000 ILS through May 31, 2026, then 5,000 ILS from June 1, 2026), add Invoice Reform allocation number". Store the threshold in a workflow variable, not a hardcoded number, since it is scheduled to drop again.

**Use Zapier Copilot** (available on all plans, including free) to describe what you want in plain English or Hebrew. Copilot suggests Zap structures, finds the right apps, and maps fields automatically. Example: "When I get a Cardcom payment, create a Morning receipt and email it to the customer."

### Step 2: Connect Israeli Apps in Zapier

Israeli apps connect to Zapier through three mechanisms. Choose based on what the app supports.

| App | Connection Method | Auth Type | Notes |
|-----|-------------------|-----------|-------|
| Morning (formerly Green Invoice) | Webhooks by Zapier | API key + Webhook | No native Zapier app for Morning. Connect via webhooks: use Morning's webhook notifications as triggers and their REST API (`api.greeninvoice.co.il`) via Webhooks by Zapier for actions. Generate API key from Morning dashboard under Settings > API. |
| Cardcom | Webhooks by Zapier | IndicatorUrl (GET callback) | Cardcom calls your Zapier webhook URL with GET query parameters on payment events. Configure the IndicatorUrl in Cardcom terminal settings. |
| Tranzila | Webhooks by Zapier | Webhook URL | Tranzila V2 uses iframe-based hosted fields for payment. Configure notification URL in Tranzila merchant panel for post-payment callbacks. |
| Monday.com | Zapier native integration | OAuth | Full support. Monday.com is a global app with strong Israeli adoption. |
| iCount | Webhooks by Zapier | API key | Israeli accounting SaaS. Use iCount REST API via Webhooks by Zapier for creating invoices, receipts, and managing contacts. |
| EZcount | Webhooks by Zapier | API key | Popular Israeli invoicing platform. REST API for document creation and customer management. |
| Grow by Meshulam | Webhooks by Zapier | Webhook URL | Israeli payment gateway supporting credit cards, Bit, Apple Pay, Google Pay. Sends JSON POST webhooks on payment events. |
| Sumit | Webhooks by Zapier | API key | Israeli invoicing and receipts platform with REST API. |
| Rivhit (accounting) | Webhooks by Zapier | API key in header | No native integration. Use webhook + custom API calls. |
| Priority ERP | Webhooks by Zapier | Basic auth | Use Priority's OData REST API via webhook actions. |
| SMS providers (019, InforUMobile) | Webhooks by Zapier | API key | Send SMS via HTTP POST action with provider's API. |

**Morning (formerly Green Invoice) API setup:**
1. Log in to Morning dashboard (app.greeninvoice.co.il)
2. Navigate to Settings > API Integration
3. Generate a new API key (JWT-based authentication)
4. In Zapier, use "Webhooks by Zapier" with Custom Request to call Morning's REST API at `api.greeninvoice.co.il`
5. Set the Authorization header with your JWT token

**Morning document type codes** (use numeric codes in API calls):

| Code | Document Type | Hebrew |
|------|--------------|--------|
| 10 | Price Quote | הצעת מחיר |
| 305 | Tax Invoice | חשבונית מס |
| 320 | Tax Invoice/Receipt | חשבונית מס קבלה |
| 330 | Credit Note/Refund | חשבונית זיכוי |
| 400 | Receipt | קבלה |

**Cardcom IndicatorUrl setup:**
1. In Zapier, create a new Zap with "Webhooks by Zapier" as the trigger
2. Choose "Catch Hook" as the trigger event
3. Copy the generated webhook URL
4. In Cardcom terminal settings, paste the URL in the IndicatorUrl field
5. Cardcom sends a GET request with query parameters (not JSON POST) on payment completion
6. Key parameters: `InternalDealNumber` (transaction ID), `Amount` (decimal shekels, e.g., 150.50), `CardOwnerName`, `CardOwnerEmail`, `CardOwnerPhone`, `NumOfPayments`
7. Make a test payment to send sample data to Zapier

**Tranzila setup (modern API V2):**
Tranzila has moved to iframe-based API V2 with hosted fields for PCI compliance. For post-payment webhooks:
1. Configure the notification URL in your Tranzila merchant panel
2. Tranzila sends payment confirmation with fields: `index` (transaction ID), `sum` (amount in ILS), `ccno` (last 4 digits), `npay` (installments)
3. The legacy redirect-based ok_page/fail_page approach still works but is deprecated

### Step 3: Handle Hebrew Text in Zap Steps

Hebrew text requires special handling in Zapier to avoid display and encoding issues.

**Cleaning Hebrew text with Unicode directional markers:**
Zapier's "Formatter > Text > Trim Whitespace" removes standard whitespace but does NOT strip Unicode directional markers (U+200F RLM, U+200E LRM). To properly clean Hebrew input that contains these invisible characters, use a "Code by Zapier" step:

```javascript
const cleaned = inputData.text.replace(/[\u200F\u200E\u200B\u200C\u200D\uFEFF]/g, '').trim();
output = [{text: cleaned}];
```

**Name formatting:** Hebrew names are "First Last" (no middle name convention). Use "Formatter > Text > Titlecase" only for English names. For Hebrew, pass through as-is.

**Mixed-direction text:** When concatenating Hebrew and English text (e.g., "Order #12345 - הזמנה חדשה"), place the English portion first, then Hebrew. Zapier renders mixed-direction text LTR by default.

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

**Bimonthly VAT period Zaps:**
Israeli businesses report VAT bimonthly: Jan-Feb, Mar-Apr, May-Jun, Jul-Aug, Sep-Oct, Nov-Dec. The VAT report is due by the 15th of the month following the period (online filing extends the deadline to the 19th). Use Schedule by Zapier:
- Trigger: Schedule on specific months (March, May, July, September, November, January) on the 10th of the month
- Action: Pull all invoices/receipts from the previous 2 months via Morning API and compile for VAT reporting
- This approach is simpler than a monthly trigger with odd-month filter

**Advance tax payment reminders (mikdamot):**
Self-employed individuals pay advance tax payments (mikdamot) bimonthly (some pay monthly, depending on Tax Authority classification). Payments are due by the 15th of the month following the reporting period (online filing extends to the 19th). Set up reminders:
- Schedule trigger: Monthly on the 10th
- Filter: Only continue in months when mikdamot are due (depends on individual schedule, typically bimonthly)
- Action: Send reminder email with upcoming payment deadline and estimated amount

**Annual report triggers:**
- Schedule: January 15th
- Action: Compile annual summary from Morning, send to accountant email
- Include: Total revenue, total expenses, VAT paid, tax withheld at source (nikui mas ba-makor)

**Key Israeli tax dates to encode in Zaps:**

| Date | Event | Zap Action |
|------|-------|------------|
| 15th of month after bimonthly period (19th online) | VAT report deadline | Send reminder 5 days before |
| 15th of month after reporting period (19th online) | Advance tax payment (mikdamot) | Send reminder + amount estimate |
| January 15 | Previous year annual summary | Compile and send to accountant |
| April 30 | Annual tax filing deadline (standard) | Filing reminder |
| May 31+ | Extended deadline (with accountant representation) | Filing reminder |

**Israel Invoice Reform 2026 (threshold step-down):**
Tax invoices over the threshold require a Tax Authority allocation number (mispar haktza'a). The threshold drops in 2026:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |
| Jan 1, 2027 | 5,000 NIS (planned to continue) |

When building invoice-creation Zaps:
- Add a Filter step that compares the invoice amount to a workflow variable holding the current threshold, and flag for allocation number when it exceeds it. Build the threshold check as a configurable variable in your workflow, not a hardcoded number, since the threshold is scheduled to drop again.
- The allocation number must be obtained from the Tax Authority system before the invoice is issued
- Morning and other authorized invoicing platforms handle this automatically through their API, but verify the document response includes the allocation number
- For manual webhook-based flows, add a Code by Zapier step that calls the Tax Authority allocation API before creating the invoice

### Step 5: Set Up Webhook-Based Israeli Integrations

Many Israeli payment processors and services do not have native Zapier integrations. Use webhooks to bridge the gap.

**Cardcom payment webhook as Zap trigger:**

Cardcom uses an IndicatorUrl callback mechanism. When a transaction completes, Cardcom sends a GET request to your webhook URL with payment details as query parameters. Key parameters:

| Field | Description | Example |
|-------|-------------|---------|
| `InternalDealNumber` | Transaction ID | `12345678` |
| `Amount` | Payment amount in decimal shekels | `150.50` (= 150.50 ILS) |
| `CardOwnerName` | Cardholder name | `ישראל ישראלי` |
| `CardOwnerEmail` | Customer email | `israel@example.com` |
| `CardOwnerPhone` | Customer phone | `0541234567` |
| `NumOfPayments` | Installment count (tashlumim) | `3` |
| `DealResponse` | Response code (0 = success) | `0` |
| `CardNum` | Last 4 digits | `1234` |

Cardcom amounts are in decimal shekels (e.g., 150.50 means 150.50 ILS). No conversion needed. Use the value directly in your invoice creation step.

**Tranzila payment webhook:**

Key fields for Tranzila post-payment notifications:

| Field | Description | Example |
|-------|-------------|---------|
| `index` | Transaction ID | `87654321` |
| `sum` | Amount in decimal ILS | `250.00` |
| `ccno` | Last 4 digits | `5678` |
| `npay` | Installments | `1` |
| `contact` | Customer name | `ישראל ישראלי` |
| `email` | Customer email | `israel@example.com` |
| `phone` | Customer phone | `0541234567` |

Both Cardcom and Tranzila send amounts in decimal shekels. No unit conversion is needed for either processor.

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

### Step 6: WhatsApp Business Messaging (Limitations and Alternatives)

**Zapier's native WhatsApp integration cannot send messages to customers.** As of January 2026, Zapier's built-in WhatsApp integration can only send messages to yourself (the account holder). It supports only 7 prefilled English templates and cannot send custom Hebrew messages to clients.

To send WhatsApp messages to customers from Zaps, use one of these third-party providers:

| Provider | Zapier Integration | Hebrew Support | Approval Required |
|----------|-------------------|----------------|-------------------|
| Twilio WhatsApp Business API | Native Zapier app ("Twilio") | Yes, via pre-approved templates | Meta Business verification + template approval |
| WATI | Native Zapier app ("WATI") | Yes, via pre-approved templates | Meta Business verification + template approval |
| Respond.io | Native Zapier app ("Respond.io") | Yes | Meta Business verification |

**Important caveats for WhatsApp Business:**
- All customer-facing WhatsApp messages require Meta-approved message templates
- Templates must be submitted for approval in advance (typically 24-48 hours)
- Hebrew templates are supported but must be submitted with the Hebrew text
- You cannot send free-form Hebrew messages to customers, only fill in template variables
- Example approved template: "שלום {{1}}, קיבלנו את התשלום שלך בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
- For internal notifications to yourself or your team, Zapier's native WhatsApp works fine

### Step 7: Use Zapier Tables and Interfaces (2026)

Zapier Tables and Interfaces are free on all plans in 2026 and provide a better alternative to Google Sheets for many Israeli business workflows.

**Zapier Tables** (replace Google Sheets for structured data):
- Native database within Zapier, no external app connection needed
- Supports field types: text, number, date, email, URL, dropdown, checkbox
- Built-in views, filters, and linked records
- Triggers available: "New Record" and "Updated Record" can start Zaps
- Better for: client databases, invoice logs, payment records, expense tracking

**When to use Tables vs Google Sheets:**

| Scenario | Use Zapier Tables | Use Google Sheets |
|----------|-------------------|-------------------|
| Simple payment log | Yes (faster, no auth) | Overkill |
| Shared with accountant | No (accountant needs Google access) | Yes |
| CRM-style client list | Yes (linked records, views) | Limited |
| Complex formulas/pivots | No | Yes |
| VAT period reporting | Either works | Yes if accountant reviews directly |

**Zapier Interfaces** (custom forms and dashboards):
- Build client intake forms, payment request pages, and dashboards without code
- Forms submit directly to Zapier Tables or trigger Zaps
- Useful for: freelancer client onboarding forms, payment request links, service feedback forms

### Step 8: Use Zapier AI Features

**Zapier Copilot** (available free on all plans):
- AI assistant that helps build Zaps from natural language descriptions
- Describe your workflow in English or Hebrew: "When I receive a Cardcom payment, create a receipt in Morning and email it"
- Copilot suggests the trigger, actions, and field mappings
- Can troubleshoot failing Zaps and suggest fixes

**Zapier Agents** (autonomous AI agents):
- Create AI agents that work across 8,000+ apps autonomously
- Example: "Monitor my Morning account for unpaid invoices older than 30 days and send reminder emails in Hebrew"
- Agents can make decisions based on context without predefined Zap steps

**Zapier Chatbots** (GPT-4o powered):
- Build customer-facing chatbots that connect to your Zaps
- Potential for Hebrew customer support (GPT-4o handles Hebrew well)
- Can answer questions about orders, payments, and services by querying your Zapier Tables

**Zapier MCP Server:**
- Connects AI coding tools (Claude Code, ChatGPT, Cursor) to 30,000+ Zapier actions
- Agents can invoke Zapier actions directly from the development environment
- Useful for building and testing Israeli business automations programmatically

**AI Guardrails:**
- PII detection to prevent sensitive data (Israeli ID numbers, credit card details) from leaking
- Toxic language filtering
- Prompt injection prevention for chatbot-based flows

### Step 9: Use Common Zap Templates for Israeli Businesses

**Template 1: Freelancer invoice-to-bookkeeping**
1. Trigger: Morning webhook (new document created)
2. Filter: Document type = Tax Invoice (305) or Tax Invoice/Receipt (320)
3. Action: Create record in Zapier Tables with columns: Date, Client Name, Amount (before VAT), VAT Amount, Total, Document Number
4. Action: If amount exceeds the Invoice Reform threshold variable (10,000 ILS through May 31, 2026, then 5,000 ILS from June 1, 2026), verify Invoice Reform allocation number is present
5. Action: If amount > 25,000 ILS, send Slack notification to accountant channel

**Template 2: E-commerce order-to-invoice**
1. Trigger: Shopify/WooCommerce > New Order
2. Action: Create document in Morning via Webhooks by Zapier (type: 320 Tax Invoice/Receipt or 400 Receipt based on business preference)
3. Action: Send email confirmation with receipt details (RTL HTML template)
4. Action: Update Monday.com board with order status

**Template 3: Payment-to-receipt (Cardcom)**
1. Trigger: Webhooks by Zapier (Cardcom IndicatorUrl GET callback)
2. Filter: `DealResponse` = 0 (successful payment only)
3. Action: Morning API > Create Document (type: 400 Receipt). Amount field uses the `Amount` value directly (already in decimal shekels).
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
- Zap A: Cardcom IndicatorUrl webhook -> Zapier Tables (Amount in decimal ILS)
- Zap B: Tranzila webhook -> Zapier Tables (sum in decimal ILS)
- Zap C: Grow by Meshulam webhook -> Zapier Tables (amount in decimal ILS)
All three processors send amounts in decimal shekels. No conversion needed.

## Examples

### Example 1: Auto-Receipt for Cardcom Payments

User says: "I want to automatically create a Morning receipt when someone pays through Cardcom"

Actions:
1. Create a Zap with Webhooks by Zapier > Catch Hook as trigger
2. Configure Cardcom IndicatorUrl to point to the webhook URL
3. Add a Filter step: only continue if `DealResponse` = 0 (successful payment)
4. Add Webhooks by Zapier > Custom Request to call Morning API, Create Document type 400 (Receipt). Use the `Amount` field directly as the item price (Cardcom sends decimal shekels, e.g., 150.50 = 150.50 ILS).
5. Map fields: `CardOwnerName` to client name, `CardOwnerEmail` to client email, `Amount` to item price
6. If amount exceeds the Invoice Reform threshold variable (10,000 ILS through May 31, 2026, then 5,000 ILS from June 1, 2026), verify the Morning API response includes an Invoice Reform allocation number
7. Add email action to send receipt link to customer

Result: Every successful Cardcom payment automatically generates a Morning receipt and emails it to the customer.

### Example 2: Bimonthly VAT Summary

User says: "Send me a summary of all invoices at the end of each VAT period for my accountant"

Actions:
1. Create a Zap with Schedule by Zapier, running on the 10th of specific months: March, May, July, September, November, January
2. Add Webhooks by Zapier > Custom Request to call Morning API Find Documents for the previous 2 months
3. Add Code by Zapier to calculate total revenue, total VAT collected, invoice count
4. Add Email action to accountant with RTL HTML summary table
5. Add Zapier Tables action to archive the period summary

Result: On the 10th of March, May, July, September, November, and January, an automated email goes to the accountant with the previous bimonthly period's invoice summary, giving 5 days before the 15th deadline (or 9 days before the 19th online deadline).

### Example 3: WhatsApp Payment Confirmation via Twilio

User says: "Send a Hebrew WhatsApp message to customers when they pay"

Actions:
1. Set up payment webhook trigger (Cardcom IndicatorUrl or Tranzila notification)
2. Add Formatter to format amount with " ש\"ח" suffix
3. Add Code by Zapier to format phone number: replace leading 0 with +972
4. Add Twilio > Send WhatsApp Message action using a pre-approved Hebrew template
5. The template must be approved by Meta in advance, e.g.: "שלום {{1}}, קיבלנו תשלום בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
6. Map template variables: {{1}} = customer name, {{2}} = formatted amount, {{3}} = transaction ID

Important: This requires a Twilio WhatsApp Business API account with Meta-approved templates. Zapier's native WhatsApp integration cannot send messages to customers.

Result: Customer receives a Hebrew WhatsApp confirmation within seconds of payment, using a Meta-approved template.

### Example 4: Freelancer End-of-Year Automation

User says: "I need a Zap that compiles my annual invoice summary for tax filing"

Actions:
1. Create a Zap with Schedule by Zapier, running January 15th
2. Add Webhooks by Zapier > Custom Request to call Morning API Find Documents for the entire previous year
3. Add Code by Zapier step to calculate totals: revenue, expenses, VAT, withholding tax
4. Add Gmail action to send formatted RTL summary to accountant
5. Add Zapier Tables action to archive the annual summary

Result: Annual tax preparation data is automatically compiled and sent to the accountant every January, well before the April 30 standard deadline (or May 31+ with accountant representation).

## Bundled Resources

### References
- `references/israeli-zapier-apps.md` -- Directory of Israeli apps available on Zapier (native integrations and webhook-based connections), including auth methods, API endpoints, and field mappings. Consult when connecting a new Israeli app to Zapier or troubleshooting authentication.
- `references/zap-templates.md` -- Ready-to-use Zap template configurations for common Israeli business workflows, with step-by-step field mappings and trigger/action details. Consult when building a new Zap and looking for a starting point that fits an Israeli business scenario.

## Recommended MCP Servers

[Green Invoice MCP](https://agentskills.co.il/he/mcps/accounting/green-invoice-mcp) for direct agent access to Morning. Zapier ships its own MCP at `mcp.zapier.com` exposing published Zaps.

## Reference Links

| Source | URL |
|--------|-----|
| Zapier pricing | https://zapier.com/pricing |
| Zapier Platform docs | https://platform.zapier.com |
| Webhooks by Zapier | https://zapier.com/apps/webhook/integrations |
| Green Invoice API | https://www.greeninvoice.co.il/api-docs/ |
| Cardcom v11 API | https://kb.cardcom.solutions/category/19-API |
| Invoice Reform 2026 (ITA) | https://www.gov.il/en/departments/legalInfo/digital_invoice |

## Gotchas

- **Cardcom amounts are decimal shekels, not agorot**: Cardcom sends `Amount` as decimal shekel values (e.g., 150.50 means 150.50 ILS). Do NOT divide by 100. The Cardcom v11 API Swagger spec confirms `Amount` uses decimal shekel values. Dividing by 100 would create invoices at 1/100th the correct amount.
- **All Israeli processors use decimal shekels**: Cardcom, Tranzila, Morning (Green Invoice), Grow, iCount, and EZcount all send and receive amounts in decimal shekels (e.g., 10.50 = ten shekels and fifty agorot). There is no agorot-to-shekel conversion needed for any of them.
- **WhatsApp native integration is self-only**: Zapier's built-in WhatsApp can only send messages to yourself. It has 7 prefilled English templates and cannot send custom Hebrew messages to clients. For customer-facing WhatsApp, use Twilio WhatsApp Business API, WATI, or Respond.io, all of which require Meta Business verification and pre-approved message templates.
- **Cardcom webhook is GET, not POST**: Cardcom's IndicatorUrl sends a GET request with query parameters (`InternalDealNumber`, `Amount`, `CardOwnerName`, etc.), not a JSON POST body. The field name for the transaction ID is `InternalDealNumber`, not `Transaction`.
- **No native Morning/Green Invoice Zapier app**: There is no built-in Morning or Green Invoice integration in Zapier's app directory. All Morning connections must go through "Webhooks by Zapier" using Morning's REST API at `api.greeninvoice.co.il`.
- **Date format mismatch**: Zapier defaults to US date format (MM/DD/YYYY). Israeli documents, invoices, and tax forms use DD/MM/YYYY. Always add an explicit date formatter step.
- **Hebrew in code steps**: When using "Code by Zapier" (JavaScript or Python), Hebrew string literals work fine, but Hebrew in variable names will break. Keep variable names in English, use Hebrew only in string values.
- **Morning document types**: Ask the user which document type they need. Receipt (400) is issued after payment, Tax Invoice (305) before or at time of sale, and Tax Invoice/Receipt (320) combines both. Agents often default to the wrong type.
- **Phone number format for WhatsApp/Twilio**: Israeli mobile numbers must include the +972 prefix and drop the leading 0 (e.g., 0541234567 becomes +972541234567). Use Code by Zapier: `phone.replace(/^0/, '+972')`.
- **VAT rate**: The current Israeli VAT rate is 18% (since January 2025). Agents sometimes use the outdated 17% rate in calculations.
- **Formatter does NOT strip Unicode markers**: "Trim Whitespace" removes standard whitespace but not RTL/LTR markers (U+200F, U+200E). Use a Code by Zapier step with regex to clean Hebrew text properly.
- **Invoice Reform 2026 affects automation, threshold drops June 1, 2026.** Tax invoices over the threshold (10,000 NIS through May 31, 2026, then 5,000 NIS from June 1, 2026) require a Tax Authority allocation number. Verify your invoicing API flow includes this step. Store the threshold in a Zap variable, not a hardcoded literal.
- **Free plan limitations**: The free plan supports unlimited Zaps but only two-step (trigger + one action) and 100 tasks/month. Most Israeli business automations need multi-step Zaps, which require the Starter plan ($19.99/month annual). Professional ($49/month) is only needed for advanced filters and conditional logic.

## Troubleshooting

### Error: "Webhook not receiving data from Cardcom"
Cause: IndicatorUrl is misconfigured or the terminal is in test mode.
Solution: Verify the IndicatorUrl in Cardcom terminal settings. Ensure the terminal is in production mode, not sandbox. Make a real small-amount payment (1 ILS) to test. Check Zapier's webhook history for incoming GET requests (not POST). If using Catch Hook, verify it accepts GET requests.

### Error: "Morning API returns 401 Unauthorized"
Cause: API key (JWT token) is invalid, expired, or incorrectly formatted in the Authorization header.
Solution: Generate a new API key from Morning dashboard (Settings > API Integration at app.greeninvoice.co.il). Ensure the token is sent as `Bearer <token>` in the Authorization header. API tokens may expire depending on your Morning plan settings.

### Error: "Hebrew text appears garbled in emails"
Cause: Email template missing UTF-8 charset or RTL direction.
Solution: Wrap Hebrew content in a `<div dir="rtl">` tag. Ensure the email HTML includes `<meta charset="UTF-8">` in the head. If using plain text email, Hebrew should display correctly in modern clients but may appear reversed in older ones.

### Error: "WhatsApp message fails to send to customer"
Cause: Using Zapier's native WhatsApp integration, which only sends to yourself.
Solution: Switch to Twilio WhatsApp Business API, WATI, or Respond.io. These require Meta Business verification and pre-approved message templates. You cannot send free-form messages to customers via WhatsApp Business API.

### Error: "Invoice Reform allocation number missing"
Cause: Invoice over the Invoice Reform threshold created without a Tax Authority allocation number. The threshold is 10,000 NIS through May 31, 2026, then drops to 5,000 NIS on June 1, 2026.
Solution: Ensure your Morning API call includes the allocation number request. Morning's API handles this automatically for documents created through their system. If using a manual webhook flow, add a step that requests an allocation number from the Tax Authority before creating the invoice. Compare the amount to a workflow variable holding the current threshold rather than a hardcoded number, since the threshold is scheduled to drop again.

### Error: "Cardcom amount is wrong in Morning invoice"
Cause: Incorrectly dividing the Cardcom amount by 100 (legacy advice that is wrong).
Solution: Do NOT divide Cardcom amounts by 100. Cardcom's `Amount` field is already in decimal shekels (e.g., 150.50 = 150.50 ILS). Use the value as-is when creating Morning documents.

## When to Use Zapier vs Alternatives

| Factor | Zapier | Make.com (Integromat) | n8n |
|--------|--------|----------------------|-----|
| Ease of use | Simplest, visual builder + Copilot AI | Visual, slightly steeper learning curve | Requires self-hosting or cloud plan, most technical |
| Native integrations | 7,000+ apps | 2,000+ apps | 400+ built-in nodes, community nodes |
| Israeli app support | Webhook-based (no native Israeli apps) | Webhook-based + some HTTP modules | Full HTTP/webhook flexibility |
| AI features | Copilot, Agents, Chatbots, MCP Server | AI modules available | AI nodes (self-configured) |
| Free tier | Unlimited 2-step Zaps, 100 tasks/month | 1,000 ops/month, limited scenarios | Self-host free, cloud plan has limits |
| Best for | Non-technical users, quick setup, AI-assisted building | Complex multi-branch workflows, cost-sensitive high-volume | Developers, self-hosted, full control |
| Israeli community | Large | Growing | Small but technical |

**Recommendation**: For non-technical Israeli business owners who want fast results, Zapier with Copilot AI is the easiest path. For complex workflows with high task volumes, Make.com may be more cost-effective. For developers who want full control and self-hosting, use n8n.
