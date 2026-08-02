---
name: zapier-israeli-integrations
description: Build Zapier Zaps connecting Israeli business apps (Morning/Green Invoice, Cardcom, Tranzila, iCount, Grow, SUMIT, Priority, InforUMobile) with global services for billing, payment, and workflow automation. Use when asked to "create a Zap for Israeli invoicing", "automate Morning receipts", "connect Cardcom to my CRM", or set up payment notifications. Covers Hebrew text handling, ILS formatting, bimonthly VAT logic, Invoice Reform allocation numbers, Zapier AI (Copilot, Agents, MCP), and webhooks from Israeli processors. All amounts use decimal shekels, not agorot. Do NOT use for n8n (use n8n-hebrew-workflows), Make.com (use make-com-israeli-automations), or non-Zapier automation.
license: MIT
compatibility: Requires Zapier account. Free plan includes unlimited two-step Zaps and 100 tasks/month. Multi-step Zaps require Professional, the entry paid tier at $19.99/month annual ($29.99 monthly) for 750 tasks, scaling by task tier within the same plan; Team is $69/month annual. Webhook triggers use Webhooks by Zapier (available on all plans). No local dependencies.
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
- Multi-step Zaps (Professional plan, the entry paid tier, $19.99/month annual or $29.99/month monthly for 750 tasks): Chain actions with logic, e.g., "New payment -> Create invoice -> Send email -> Update CRM". Professional also carries Paths, filters and advanced Zap settings; higher task volumes are a tier selector inside the same Professional plan, not a separate plan. Team ($69/month annual) adds shared workspaces and up to 25 users.
- Use Paths (branching) when the Zap needs to handle different scenarios, e.g., "If the pre-VAT amount is over the Invoice Reform threshold (5,000 ILS), add Invoice Reform allocation number". Store the threshold in a workflow variable, not a hardcoded number, so a future change is a one-line edit.

**Use Zapier Copilot** (available on all plans, including free) to describe what you want in plain English or Hebrew. Copilot suggests Zap structures, finds the right apps, and maps fields automatically. Example: "When I get a Cardcom payment, create a Morning receipt and email it to the customer."

### Step 2: Connect Israeli Apps in Zapier

Israeli apps connect to Zapier through three mechanisms. **Always check the Zapier app directory first** (`https://zapier.com/apps/<name>/integrations`): several Israeli vendors now ship native Zapier apps, and a native app is always simpler and more reliable than a hand-built Custom Request. Fall back to webhooks only when no native app exists.

| App | Connection Method | Auth Type | Notes |
|-----|-------------------|-----------|-------|
| Morning (formerly Green Invoice) | Webhooks by Zapier | API key + Webhook | No native Zapier app for Morning. Connect via webhooks: use Morning's webhook notifications as triggers and their REST API (`api.greeninvoice.co.il`) via Webhooks by Zapier for actions. Generate API key from Morning dashboard under Settings > API. |
| Cardcom | Webhooks by Zapier | `WebHookUrl` (JSON POST callback) | Cardcom POSTs a JSON body to the `WebHookUrl` you supply on the `CreateLowProfile` request. `WebHookUrl` is a required field on that request. |
| Tranzila | Webhooks by Zapier | See caveat below | Tranzila V2 uses iframe-based hosted fields for payment. See the Tranzila section in Step 5 before building: the current documentation does not describe a merchant-panel webhook. |
| Monday.com | Zapier native integration | OAuth | Full support. Monday.com is a global app with strong Israeli adoption. |
| SUMIT | **Zapier native integration** | Managed by Zapier | Israeli invoicing and business-management platform. Native app with a `Card Updated` trigger and `Create Document`, `Create Card`, `Update Card`, `Get Card`, `Send SMS` actions. Use `Create Document` instead of hand-rolling invoice HTTP calls. |
| Priority ERP | **Zapier native integration** | Managed by Zapier | Israeli ERP. Native app with `Catch Changed Customer Order Status Webhook` and `Catch Changed Purchase Order Status Webhook` triggers, plus `Create Sales Orders`, `Create Sales Opportunity`, `Create New Lead` and `Find Customer by Email` actions. |
| InforUMobile | **Zapier native integration** | Managed by Zapier | Israeli SMS and marketing gateway. Native app with `New Lead From Landing Page` trigger and `Send SMS`, `Send Whatsapp Template Message`, `Add Contact to Group` actions. Prefer this over the raw XML API. |
| iCount | Webhooks by Zapier | API key | Israeli accounting SaaS. No native Zapier app. Use iCount REST API via Webhooks by Zapier for creating invoices, receipts, and managing contacts. |
| EZcount | Webhooks by Zapier | API key | Popular Israeli invoicing platform. No native Zapier app. REST API for document creation and customer management. |
| Grow by Meshulam | Webhooks by Zapier | Webhook URL | Israeli payment gateway supporting credit cards, Bit, Apple Pay, Google Pay. Sends JSON POST webhooks on payment events. **Do not search Zapier for "Grow"**: the app at `zapier.com/apps/grow` is an unrelated US mailing-list product ("Grow helps publishers build their mailing list"), not Meshulam. |
| Rivhit (accounting) | Webhooks by Zapier | API key in header | No native integration. Use webhook + custom API calls. |
| 019 SMS | Webhooks by Zapier | API key | No native Zapier app. Send SMS via HTTP POST action with the provider's API. |

Per-vendor connection steps, webhook payload fields and migration notes: `references/israeli-zapier-apps.md`.
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

**Israel Invoice Reform allocation numbers:**
Tax invoices over the threshold require a Tax Authority allocation number (mispar haktza'a). **The current threshold is 5,000 NIS, in force since June 2026.** The step-down to date:

| Effective | Threshold |
|-----------|-----------|
| May 2024 | 25,000 NIS |
| Jan 2025 | 20,000 NIS |
| Jan 2026 | 10,000 NIS |
| **Jun 2026 onward (current)** | **5,000 NIS** |

**The threshold is measured on the amount BEFORE VAT.** This is the single most common way an Invoice Reform Zap goes wrong: payment gateways send the charged total, which already includes VAT, so comparing a gateway amount directly against 5,000 over-flags every invoice whose pre-VAT base is actually under the threshold. At 18% VAT a 5,900 ILS charge is exactly a 5,000 ILS base.

When building invoice-creation Zaps:
- Derive the pre-VAT amount before comparing. Either divide the gateway total by 1.18 in a Code by Zapier or Formatter step, or read Morning's pre-VAT `amount` field rather than `total`.
- Add a Filter step that compares that pre-VAT amount to a workflow variable holding the current threshold, and flag for allocation number when it exceeds it. Keep the threshold in a variable rather than a hardcoded number so a future change is a one-line edit.
- The allocation number must be obtained from the Tax Authority system before the invoice is issued
- Morning and other authorized invoicing platforms handle this automatically through their API, but verify the document response includes the allocation number
- For manual webhook-based flows, add a Code by Zapier step that calls the Tax Authority allocation API before creating the invoice

### Step 5: Set Up Webhook-Based Israeli Integrations

For vendors with no native Zapier app, use Webhooks by Zapier (Catch Hook for inbound, Custom Request for outbound). Cardcom v11 POSTs JSON to `WebHookUrl`; success is `ResponseCode == 0`; cardholder fields nest under `UIValues`. Full payload tables and the Tranzila caveat: `references/israeli-zapier-apps.md`.

### Step 6: WhatsApp Business Messaging

Zapier has **two different WhatsApp apps** and they are routinely confused. Pick by who you are messaging.

| Zapier app | Who it can message | What it does |
|------------|--------------------|--------------|
| **WhatsApp Notifications** | **Only yourself**, the phone number used to authenticate the connection | One action, `Send Message`, restricted to prefilled templates that cannot be customized. Good for "alert me when a payment lands." Not usable for customers. |
| **WhatsApp Business** | **Your customers** | Triggers `New Message Received` (a customer messages your WhatsApp Business number) and `Message Status Updated` (sent, delivered, read, failed). Actions `Send Template Message`, `Send Freeform Message`, `Send Media Message`, `Get Attachment`. |

**Use WhatsApp Business for customer-facing Hebrew messaging.** It requires a WhatsApp Business account connected to Zapier, and the usual Meta rules apply:
- Outside the 24-hour customer-service window you must use a Meta-approved template. Templates are submitted for approval in advance (typically 24-48 hours). Hebrew templates are supported but must be submitted with the Hebrew text.
- Example approved template: "שלום {{1}}, קיבלנו את התשלום שלך בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
- **Inside** the 24-hour window, opened when the customer messages you first, `Send Freeform Message` sends arbitrary Hebrew text with no template. This is the path for live support replies and follow-up questions.
- A payment confirmation sent proactively is outside the window, so it needs a template. A reply to a customer who just asked "did my payment go through?" does not.

**Israeli alternative:** InforUMobile's native Zapier app carries a `Send Whatsapp Template Message` action. If you already use InforUMobile for SMS, this avoids adding a second vendor.

**BSP providers**, worth adding only if you need high volume, a shared team inbox, or multi-channel routing that the native app does not cover:

| Provider | Zapier Integration | Hebrew Support | Approval Required |
|----------|-------------------|----------------|-------------------|
| Twilio WhatsApp Business API | Native Zapier app ("Twilio") | Yes, via pre-approved templates | Meta Business verification + template approval |
| WATI | Native Zapier app ("WATI") | Yes, via pre-approved templates | Meta Business verification + template approval |
| Respond.io | Native Zapier app (search "Respond.io", app slug `respondio`) | Yes | Meta Business verification |

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
- Create AI agents that work across 9,000+ apps autonomously
- Lives at `agents.zapier.com`. This product was launched as **Zapier Central** and renamed to Zapier Agents in January 2025, so older tutorials and forum posts will call it Central
- Example: "Monitor my Morning account for unpaid invoices older than 30 days and send reminder emails in Hebrew"
- Agents can make decisions based on context without predefined Zap steps

**Zapier Chatbots:**
- Build customer-facing chatbots that connect to your Zaps
- Usable for Hebrew customer support
- Can answer questions about orders, payments, and services by querying your Zapier Tables
- The underlying model changes as Zapier migrates providers, so do not hardcode a model name into your process docs

**Zapier MCP Server:**
- Connects AI coding tools (Claude Code, ChatGPT, Cursor) to 30,000+ actions across 9,000+ apps
- Agents can invoke Zapier actions directly from the development environment
- Useful for building and testing Israeli business automations programmatically

**AI Guardrails:**
- PII detection to prevent sensitive data (Israeli ID numbers, credit card details) from leaking
- Toxic language filtering
- Prompt injection prevention for chatbot-based flows

### Step 9: Use Common Zap Templates for Israeli Businesses

Ready-made patterns for invoicing, payment reconciliation, VAT-cycle reminders and WhatsApp follow-ups: `references/zap-templates.md`.

## Examples

### Example 1: Auto-Receipt for Cardcom Payments

User says: "I want to automatically create a Morning receipt when someone pays through Cardcom"

Actions:
1. Create a Zap with Webhooks by Zapier > Catch Hook as trigger
2. Pass the Catch Hook URL as `WebHookUrl` on your Cardcom `CreateLowProfile` request
3. Add a Filter step: only continue if `ResponseCode` = 0 (successful payment)
4. Add Webhooks by Zapier > Custom Request to call Morning API, Create Document type 400 (Receipt). Use the `Amount` field directly as the item price (Cardcom sends decimal shekels, e.g., 150.50 = 150.50 ILS).
5. Map fields: `UIValues.CardOwnerName` to client name, `UIValues.CardOwnerEmail` to client email, `Amount` to item price
6. If the pre-VAT amount exceeds the Invoice Reform threshold variable (currently 5,000 ILS), verify the Morning API response includes an Invoice Reform allocation number
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

### Example 3: WhatsApp Payment Confirmation

User says: "Send a Hebrew WhatsApp message to customers when they pay"

Actions:
1. Set up payment webhook trigger (Cardcom `WebHookUrl` JSON POST)
2. Add Formatter to format amount with " ש\"ח" suffix
3. Add Code by Zapier to format phone number: replace leading 0 with +972
4. Add **WhatsApp Business > Send Template Message** using a pre-approved Hebrew template
5. The template must be approved by Meta in advance, e.g.: "שלום {{1}}, קיבלנו תשלום בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
6. Map template variables: {{1}} = customer name, {{2}} = formatted amount, {{3}} = transaction ID

A proactive payment confirmation is outside the 24-hour customer-service window, so it must be a template. If instead the customer messaged you first, use the `New Message Received` trigger and `Send Freeform Message`, which sends arbitrary Hebrew with no template.

Do not use the "WhatsApp Notifications" app here. It only messages your own number. Twilio or WATI are alternatives if you need BSP-grade volume or a shared inbox.

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

## Related Skills and MCP Servers

The [green-invoice skill](https://agentskills.co.il/he/skills/accounting/green-invoice) covers Morning/Green Invoice API work directly and is the better starting point for invoice-document logic. Zapier ships its own MCP at `mcp.zapier.com` exposing published Zaps.

## Reference Links

| Source | URL |
|--------|-----|
| Zapier pricing | https://zapier.com/pricing |
| Zapier Platform docs | https://platform.zapier.com |
| Webhooks by Zapier | https://zapier.com/apps/webhook/integrations |
| Morning (Green Invoice) API docs | https://developers.morning.co/ |
| Cardcom v11 API (ReDoc) | https://secure.cardcom.solutions/swagger/index.html |
| Cardcom v11 OpenAPI spec | https://secure.cardcom.solutions/swagger/v11/swagger.json |
| Tranzila developer docs | https://docs.tranzila.com/ |
| Invoice Reform (ITA) | https://www.gov.il/en/departments/legalInfo/digital_invoice |

## Gotchas

- **Cardcom amounts are decimal shekels, not agorot**: Cardcom sends `Amount` as decimal shekel values (e.g., 150.50 means 150.50 ILS). Do NOT divide by 100. The Cardcom v11 API Swagger spec confirms `Amount` uses decimal shekel values. Dividing by 100 would create invoices at 1/100th the correct amount.
- **All Israeli processors use decimal shekels**: Cardcom, Tranzila, Morning (Green Invoice), Grow, iCount, and EZcount all send and receive amounts in decimal shekels (e.g., 10.50 = ten shekels and fifty agorot). There is no agorot-to-shekel conversion needed for any of them.
- **Two different WhatsApp apps on Zapier**: "WhatsApp Notifications" only messages your own number and is limited to prefilled templates. "WhatsApp Business" messages customers and offers `Send Template Message`, `Send Freeform Message` (inside the 24-hour window) and `Send Media Message`. Agents routinely pick the first and conclude customer messaging is impossible. It is not.
- **Cardcom v11 webhook is a JSON POST to `WebHookUrl`**: Not a GET to `IndicatorUrl`. The success field is `ResponseCode` (0 = success), not `DealResponse`, and the transaction ID is `TranzactionId`. `InternalDealNumber` exists in the v11 API only as a lookup key on transaction-info requests, not as a webhook field. Cardholder details are nested under `UIValues`. Zaps written against `IndicatorUrl` / `DealResponse` are on the legacy path and will never fire.
- **Check the Zapier app directory before hand-rolling**: SUMIT, Priority ERP and InforUMobile all have native Zapier apps, so `Create Document` and `Send SMS` are one click rather than a Custom Request. Morning, Cardcom, Tranzila, iCount, EZcount and Rivhit genuinely have none and do require webhooks.
- **"Grow" on Zapier is not Meshulam**: `zapier.com/apps/grow` is an unrelated mailing-list product for publishers. Grow by Meshulam has no Zapier app; use its JSON webhook.
- **Invoice Reform thresholds are pre-VAT**: Gateway amounts include VAT. Divide by 1.18 (or read Morning's pre-VAT `amount`) before comparing to the 5,000 ILS threshold, or the Zap over-flags every invoice between 5,000 and 5,900 gross.
- **Legacy ChatGPT Zap steps stop working after August 26, 2026**: Zaps built on the deprecated ChatGPT / OpenAI Assistants actions (creating assistants, uploading files) break on that date. If a Hebrew summarization or categorization step uses them, migrate it before then.
- **Date format mismatch**: Zapier defaults to US date format (MM/DD/YYYY). Israeli documents, invoices, and tax forms use DD/MM/YYYY. Always add an explicit date formatter step.
- **Hebrew in code steps**: When using "Code by Zapier" (JavaScript or Python), Hebrew string literals work fine, but Hebrew in variable names will break. Keep variable names in English, use Hebrew only in string values.
- **Morning document types**: Ask the user which document type they need. Receipt (400) is issued after payment, Tax Invoice (305) before or at time of sale, and Tax Invoice/Receipt (320) combines both. Agents often default to the wrong type.
- **Phone number format for WhatsApp/Twilio**: Israeli mobile numbers must include the +972 prefix and drop the leading 0 (e.g., 0541234567 becomes +972541234567). Use Code by Zapier: `phone.replace(/^0/, '+972')`.
- **VAT rate**: The current Israeli VAT rate is 18% (since January 2025). Agents sometimes use the outdated 17% rate in calculations.
- **Formatter does NOT strip Unicode markers**: "Trim Whitespace" removes standard whitespace but not RTL/LTR markers (U+200F, U+200E). Use a Code by Zapier step with regex to clean Hebrew text properly.
- **Invoice Reform allocation numbers are required above 5,000 NIS pre-VAT** (in force since June 2026). Verify your invoicing API flow includes this step. Store the threshold in a Zap variable, not a hardcoded literal.
- **Free plan limitations**: The free plan supports unlimited Zaps but only two-step (trigger + one action) and 100 tasks/month. Most Israeli business automations need multi-step Zaps, which require Professional, the entry paid tier at $19.99/month annual ($29.99 monthly) for 750 tasks. There is no Starter plan; it was discontinued on April 2, 2024 and its features folded into Professional. Higher task volumes are a tier selector within Professional, not a separate plan.

## Troubleshooting

### Error: "Webhook not receiving data from Cardcom"
Cause: most often the Zap is built against the legacy `IndicatorUrl` GET mechanism rather than the v11 `WebHookUrl` JSON POST.
Solution: Confirm you are passing the Zapier Catch Hook URL as the `WebHookUrl` field on each `CreateLowProfile` request. It is a required field on that request, so if you are not sending it the call itself will fail validation. Check Zapier's webhook history for incoming **POST** requests carrying a JSON body. If your Filter tests `DealResponse`, it will never match: the v11 field is `ResponseCode`. Then confirm the terminal is in production mode, not sandbox, and make a real small-amount payment (1 ILS) to test.

### Error: "Morning API returns 401 Unauthorized"
Cause: API key (JWT token) is invalid, expired, or incorrectly formatted in the Authorization header.
Solution: Generate a new API key from Morning dashboard (Settings > API Integration at app.greeninvoice.co.il). Ensure the token is sent as `Bearer <token>` in the Authorization header. API tokens may expire depending on your Morning plan settings.

### Error: "Hebrew text appears garbled in emails"
Cause: Email template missing UTF-8 charset or RTL direction.
Solution: Wrap Hebrew content in a `<div dir="rtl">` tag. Ensure the email HTML includes `<meta charset="UTF-8">` in the head. If using plain text email, Hebrew should display correctly in modern clients but may appear reversed in older ones.

### Error: "WhatsApp message fails to send to customer"
Cause: Using the "WhatsApp Notifications" app, which only sends to the phone number that authenticated the connection.
Solution: Switch to the "WhatsApp Business" app, which has `Send Template Message`, `Send Freeform Message` and `Send Media Message` actions for customers. Outside the 24-hour customer-service window the message must use a Meta-approved template; inside it, freeform Hebrew works. Twilio, WATI or Respond.io are alternatives if you need BSP-grade volume or a shared inbox.

### Error: "Invoice Reform allocation number missing"
Cause: Invoice over the Invoice Reform threshold created without a Tax Authority allocation number. The threshold is 5,000 NIS measured before VAT.
Solution: Ensure your Morning API call includes the allocation number request. Morning's API handles this automatically for documents created through their system. If using a manual webhook flow, add a step that requests an allocation number from the Tax Authority before creating the invoice. Compare the **pre-VAT** amount, not the gateway total, to a workflow variable holding the current threshold.

### Error: "Cardcom amount is wrong in Morning invoice"
Cause: Incorrectly dividing the Cardcom amount by 100 (legacy advice that is wrong).
Solution: Do NOT divide Cardcom amounts by 100. Cardcom's `Amount` field is already in decimal shekels (e.g., 150.50 = 150.50 ILS). Use the value as-is when creating Morning documents.

## When to Use Zapier vs Alternatives

| Factor | Zapier | Make.com (Integromat) | n8n |
|--------|--------|----------------------|-----|
| Ease of use | Simplest, visual builder + Copilot AI | Visual, slightly steeper learning curve | Requires self-hosting or cloud plan, most technical |
| Native integrations | 9,000+ apps | 2,000+ apps | 400+ built-in nodes, community nodes |
| Israeli app support | Native apps for SUMIT, Priority ERP, InforUMobile, Monday.com and Wix; webhook-based for Morning, Cardcom, Tranzila, iCount, EZcount, Rivhit and Grow | Webhook-based + some HTTP modules | Full HTTP/webhook flexibility |
| AI features | Copilot, Agents, Chatbots, MCP Server | AI modules available | AI nodes (self-configured) |
| Free tier | Unlimited 2-step Zaps, 100 tasks/month | 1,000 ops/month, limited scenarios | Self-host free, cloud plan has limits |
| Best for | Non-technical users, quick setup, AI-assisted building | Complex multi-branch workflows, cost-sensitive high-volume | Developers, self-hosted, full control |
| Israeli community | Large | Growing | Small but technical |

**Recommendation**: For non-technical Israeli business owners who want fast results, Zapier with Copilot AI is the easiest path. For complex workflows with high task volumes, Make.com may be more cost-effective. For developers who want full control and self-hosting, use n8n.
