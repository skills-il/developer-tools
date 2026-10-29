---
name: zapier-israeli-integrations
description: Build Zapier Zaps connecting Israeli business apps (Morning/Green Invoice, Cardcom, Tranzila, iCount, Grow, SUMIT, Priority, InforUMobile) with global services for billing, payment, and workflow automation. Use when asked to "create a Zap for Israeli invoicing", "automate Morning receipts", "connect Cardcom to my CRM", or set up payment notifications. Covers Hebrew text handling, ILS formatting, bimonthly VAT logic, Invoice Reform allocation numbers, Zapier AI (Copilot, Agents, MCP), and webhooks from Israeli processors. All amounts use decimal shekels, not agorot. Do NOT use for n8n (use n8n-hebrew-workflows), Make.com (use make-com-israeli-automations), or non-Zapier automation.
license: MIT
compatibility: Requires Zapier account. Free plan includes unlimited two-step Zaps and 100 tasks/month. Multi-step Zaps require Professional, the entry paid tier at $19.99/month annual for 750 tasks, scaling by task tier within the same plan; Team is $69/month annual. Webhooks by Zapier is a premium app, so every webhook-based Israeli vendor (Morning, Cardcom, Tranzila, Grow, iCount) needs a paid plan. No local dependencies.
---

# Zapier Israeli Integrations

## Instructions

### Step 1: Choose the Right Zap Pattern

Match the Israeli business need to the correct Zap architecture.

| Business Need | Zap Trigger | Action Chain | Israeli Apps |
|---------------|-------------|--------------|--------------|
| Auto-receipt after payment | Cardcom/Tranzila webhook | Parse payment -> Create Morning doc -> Email customer | Cardcom, Morning |
| Payment reminder (freelancer) | Schedule trigger | Query unpaid invoices -> Filter overdue -> Send Hebrew reminder | Morning, email/SMS provider |
| WhatsApp order confirmation | Payment webhook | Format Hebrew message -> Send approved template | WhatsApp Business or InforUMobile |

Five more patterns (invoice-to-bookkeeping sync, e-commerce orders, expense categorisation, lead capture, multi-gateway consolidation) with full field mappings: `references/zap-templates.md`.

**Single-step vs multi-step.** Free gives unlimited Zaps but only two steps (one trigger, one action), 100 tasks/month and 15-minute polling, and it cannot use Webhooks by Zapier, a premium app: Zapier says premium apps "are only available to users on a paid Zapier plan or while on a free trial". So on Free none of the webhook-based vendors below can be connected at all, and only a native-app trigger such as PayPlus `New Charge` feeding one action fits. Almost every automation here needs multi-step, which starts at Professional. Paths (branching) handle the "if the pre-VAT amount is over the Invoice Reform threshold, add an allocation number" shape; keep that threshold in a workflow variable rather than a hardcoded number, so a future change is a one-line edit. Per-plan prices and limits: `references/zapier-platform-notes.md`.

**Use Zapier Copilot** to describe what you want in plain English or Hebrew ("when I get a Cardcom payment, create a Morning receipt and email it"). It suggests the structure, finds the apps and maps fields. On every plan, with a daily message limit on Free.

### Step 2: Connect Israeli Apps in Zapier

Israeli apps reach Zapier three ways. **Always check the app directory first** (`zapier.com/apps/<app-slug>/integrations`): a native app is simpler and more reliable than a hand-built Custom Request, and several Israeli vendors now ship one. Fall back to Webhooks by Zapier only when none exists.

- **Native Zapier apps:** SUMIT, Priority ERP, InforUMobile, PayPlus (payment gateway, trigger-only: `New Approval`, `New Charge`, `New Invoice`), Responder and Responder Live (רב מסר), monday.com, Wix (trigger-only). Prefer these over raw HTTP every time.
- **Webhooks by Zapier:** Morning (formerly Green Invoice), Cardcom, Tranzila, iCount, EZcount, Rivhit, 019 SMS, and Grow. None of these has a native app.
- **Do not search Zapier for "Grow".** The app at `zapier.com/apps/grow` is an unrelated US mailing-list product, not the Israeli payment gateway. The gateway's own brand is now simply Grow (`meshulam.co.il` redirects to `grow.business`), which makes the collision worse, not better.

**Morning auth is OAuth 2.0 now.** The current spec (`https://developers.morning.co/docs/openapi.bundled.json`, `openapi: 3.0.3`, info.version 2.0.0) documents `POST https://api.morning.co/idp/v1/oauth/token` with a JSON body (`grant_type: client_credentials`, `client_id`, `client_secret`) and header `Content-Type: application/json`, returning a one-hour JWT you send as `Authorization: Bearer`. The production base for every other call is still `https://api.greeninvoice.co.il/api/v1`. The legacy `POST /api/v1/account/token` is gone: absent from the spec, it returned HTTP 404 on 2026-10-29 while its neighbours answered 401, so a Zap still using it is broken. Amounts are decimal shekels, never agorot.

Per-app connection method, auth type, webhook payload fields, exact native trigger and action names, and migration notes: `references/israeli-zapier-apps.md`.

### Step 3: Handle Hebrew Text in Zap Steps

Hebrew text requires special handling in Zapier to avoid display and encoding issues.

**Cleaning Hebrew text with Unicode directional markers:**
Zapier's "Formatter > Text > Trim Whitespace" removes standard whitespace but does NOT strip Unicode directional controls (RLM/LRM, the RLE/PDF embeddings and the isolates that text pasted from Word or a phone carries). Use a "Code by Zapier" step:

```javascript
const cleaned = (inputData.text || '').replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u061C\u200B-\u200D\u2060\uFEFF]/g, '').trim();
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

**ILS currency and Israeli dates.** Formatter > Numbers > Format Number only regroups separators; Zapier's docs say it "cannot round or pad numbers", so it will not give you two decimals. Use a Code step (`Number(x).toFixed(2)`) or Formatter's Format Currency, then add " ש\"ח". For human-facing dates set Formatter > Date/Time's To Format explicitly to `DD/MM/YYYY`: a month-first date is misread by Israeli recipients, silently so for any day under 13. Two traps sit next to that advice. Formatter's To Timezone defaults to UTC, so set `Asia/Jerusalem` or a payment at 01:30 is dated the day before. And Zapier Tables accepts dates only as `MM/DD/YYYY`, `YYYY-MM-DD` or `YYYY-MM-DDhh:mm:ssZ`, so write `YYYY-MM-DD` to Tables and keep DD/MM/YYYY for emails and messages.

### Step 4: Build Israeli Billing Cycle Automations

Israeli tax reporting follows specific cycles. Build Zaps that align with these periods.

**First establish whether the business reports bimonthly or MONTHLY.** This is set by turnover, and a Zap built on the wrong cadence silently misses filings. Under `סעיף 67(א2)(1)` of the VAT Law (with `תקנה 20(ג)(1)` of the VAT Regulations), bimonthly reporting applies to a turnover of up to **1,775,000 NIS**; a turnover **above** that reports **monthly**. The figure shown is the one in force for 2026. `סעיף 126(ד)` of the Law re-indexes it on 1 September each year, rounded to the nearest 5,000 NIS, and the September 2026 figure (which governs 2027) can be gazetted months late: the 2025 one was signed only on 30.6.2026. Re-read it annually rather than hardcoding it. A bimonthly Schedule Zap built for a business over the line misses six filings a year and nothing in Zapier will tell you.

**Bimonthly VAT period Zaps** (turnover at or below the threshold): the periods are Jan-Feb, Mar-Apr, May-Jun, Jul-Aug, Sep-Oct, Nov-Dec. Use Schedule by Zapier:
- Trigger: Schedule on specific months (March, May, July, September, November, January), several days before that period's actual deadline
- Action: Pull all invoices/receipts from the previous 2 months via Morning API and compile for VAT reporting
- This is simpler than a monthly trigger with an odd-month filter

**Deadlines are data, not code.** The statutory dates are the 15th (periodic VAT and mikdamot), the 16th (withholding) and the 23rd (detailed VAT report), with online filing to the 19th at 18:30, but the Tax Authority's annual deferral table moves most of them: in 2026 nine of the twelve periodic dates are not the 15th, up to twelve days later. Each report type has its own column, and in-year announcements defer single periods further. Keep the year's deadlines in a Zapier Table (period, report type, date), have the Schedule Zap look the row up, and re-import each January. Mikdamot ride the periodic VAT row. The annual filing deadline is announced yearly and routinely deferred, so never encode it as a literal. Bituach Leumi advances are a separate schedule. The 2026 columns, the annual-filing dates and the Bituach Leumi note: `references/israeli-zapier-apps.md`.

**Israel Invoice Reform allocation numbers:**
A tax invoice (305 or 320) above the threshold, issued to an Israeli business that will deduct the input VAT, needs a Tax Authority allocation number (mispar haktza'a), and the invoice must carry the buyer's ח.פ. or osek number; without the number the buyer cannot deduct that VAT. A sale to a private consumer or a foreign customer needs none: Morning says the regime governs transactions between Israeli-registered businesses that offset input VAT. **The current threshold is 5,000 NIS, in force since June 2026.** The step-down to date:

| Effective | Threshold |
|-----------|-----------|
| May 2024 | 25,000 NIS |
| Jan 2025 | 20,000 NIS |
| Jan 2026 | 10,000 NIS |
| **Jun 2026 onward (current)** | **5,000 NIS** |

**The threshold is measured BEFORE VAT.** This is the most common way an Invoice Reform Zap goes wrong: gateways send the charged total, which already includes VAT, so comparing it directly against 5,000 over-flags every charge between 5,000 and 5,900 gross. At 18% VAT a 5,900 ILS charge is exactly a 5,000 ILS base.

When building invoice-creation Zaps:
- Collect the buyer's ח.פ. on your checkout (your own form, or a Cardcom custom field returned in `UIValues.CustomFields`) and send it as `client.taxId`. Branch with Paths only on "tax ID present AND pre-VAT amount over the threshold variable": flagging every large consumer sale asks for numbers nobody needs.
- Take the pre-VAT amount from the document, not a literal 1.18: Morning's `amount - vat` on search results (after discount, unlike `amountDueVat`) or `subtotal` on the `document/created` webhook. From a gateway total, keep the VAT rate in a variable beside the threshold. Convert a foreign-currency document with its `currencyRate` / `foreignCurrencyRate` first: a 2,000 USD base is far over 5,000 NIS.
- Do not call the Tax Authority yourself, and do not let an agent invent an endpoint. The number is requested either manually on the Tax Authority's online form or automatically by invoicing software connected to its systems, so route the document through such a platform (Morning, iCount, EZcount, SUMIT). In Morning that connection must be active; Morning says it lasts three months and is then renewed.
- Read the number from `GET /documents/{id}` or the `document/created` webhook, never from the create response, which never carries it (Example 1, step 8).
- **Never split an invoice to stay under the threshold.** A Tax Authority research publication dated 2 June 2026 states that artificial splitting of a transaction is contrary to law (`פיצול מלאכותי של עסקה הינו בניגוד לחוק`), quantifies it at 12.2 to 16.4 billion NIS of 2025 transactions shifted below the line, and floats requiring an allocation number from the first shekel. A Filter comparing a pre-VAT amount to the threshold is one careless step from a splitting rule: keep it a flag-for-allocation branch, never a split-the-charge branch.

### Step 5: Set Up Webhook-Based Israeli Integrations

For vendors with no native Zapier app, use Webhooks by Zapier (Catch Hook for inbound, Custom Request for outbound). The three gateways send three different shapes, so do not reuse one Zap's mappings for another:
- **Cardcom v11** POSTs JSON to `WebHookUrl`; success is `ResponseCode == 0`; the amount is `TranzactionInfo.Amount`; cardholder fields nest under `UIValues`.
- **Tranzila** POSTs to its **Notify URL** (`notify_url_address`, or my.tranzila > Payment Page > Security, Notify Format `QSTR`) as a **form-encoded** body, not JSON; success is `Response` = `000`, the amount is `sum`. Its legacy iframe on `direct.tranzila.com` loses official support on 1 January 2027; the DirectNG iframe keeps the Notify URL.
- **Grow** sends JSON from its Webhooks service, which Grow support enables for you; the amount is `paymentSum` and the payer is `fullName` / `payerEmail` / `payerPhone`.

All three amounts include VAT. Full payload tables: `references/israeli-zapier-apps.md`.

### Step 6: WhatsApp Business Messaging

Zapier has **two different WhatsApp apps** and they are routinely confused. Both are premium apps, so both need a paid plan (Notifications became premium on 1 October 2025).

| Zapier app | Who it can message | What it does |
|------------|--------------------|--------------|
| **WhatsApp Notifications** | **Only yourself.** Zapier's own help page is explicit: it sends "yourself WhatsApp messages to your WhatsApp account", and the connection is authenticated by confirming your own phone number via an OTP | Exactly one action and no triggers: `Send Message`. Limited to seven prefilled templates (New Lead, New Message, Payment Confirmation, New Order, Shipping Confirmation, Calendar Reminder, Zap Error), capped at 1024 characters, and "custom templates cannot be created". Good for "alert me when a payment lands". Not usable for customers. |
| **WhatsApp Business** | **Your customers** | Triggers `New Message Received` and `Message Status Updated`. Actions `Send Template Message`, `Send Freeform Message`, `Send Media Message`; search `Get Attachment`. |

**Use WhatsApp Business for anything customer-facing.** Meta's window rule decides which action you need: outside the 24-hour customer-service window you must send a Meta-approved template (submitted in advance; Meta's template docs say review can take up to 24 hours, Hebrew supported but the Hebrew text is what gets approved); inside the window, opened when the customer messages you first, `Send Freeform Message` sends arbitrary Hebrew with no template, and `Send Media Message` is likewise window-only. A proactive payment confirmation is outside the window and needs a template. A reply to "did my payment go through?" does not. **A green Zap run is not delivery:** Zapier says runs "will always appear as successful, even if they fail to send", so watch `Message Status Updated` for `failed` or check Meta Business Manager.

If you already use InforUMobile for SMS, its native Zapier app has a `Send Whatsapp Template Message` action and saves a second vendor. Twilio, WATI and Respond.io (slug `respondio`) are the BSP options, worth it only for high volume, a shared inbox or multi-channel routing.

**Budget real setup time before promising this to a client:** WhatsApp Business needs a Meta Business account, business verification, a Cloud API app and a number NOT already on consumer WhatsApp. It also costs money per message: Meta bills each delivered business-to-user message by category and market, and since 1 October 2026 utility templates are charged even inside the window, with 1,000 free service messages per number a month. Details: `references/israeli-zapier-apps.md`.

### Step 7: Use Zapier Tables and Forms (2026)

**Zapier Interfaces is now Zapier Forms** (`zapier.com/interfaces` redirects to `zapier.com/forms`). Tables is a native database whose "New Record" and "Updated Record" triggers can start a Zap and which needs no external auth, so it beats Google Sheets for payment logs and invoice archives; Sheets still wins when the accountant needs direct access or pivots. Both are on every plan, but Free caps Tables at 2,500 records and Forms at 10 pages, so size that against your invoice volume. Limits, field types and use cases: `references/zapier-platform-notes.md`.

### Step 8: Use Zapier AI Features

**Copilot** builds Zaps from a natural-language description in English or Hebrew and can troubleshoot a failing Zap. It is on every plan, but Free carries a daily message limit.

**Zapier Agents** (`agents.zapier.com`) are autonomous agents that act across Zapier's app catalogue without predefined steps, for example "chase Morning invoices unpaid past 30 days with Hebrew reminder emails". It launched as **Zapier Central** and was renamed, so older tutorials use the old name. Agents consume a separate activity allowance, not your task quota. Zapier is now migrating Agents into **AI by Zapier**, a step inside an ordinary Zap billed in tasks, and has "not set a date to turn off Agents yet": build new agentic flows that way.

**Zapier MCP** (`zapier.com/mcp`) exposes the actions of Zapier's 9,000+ apps as tools to Claude Code, ChatGPT and Cursor, the fastest way to build and test an Israeli automation from your editor. Each successful tool call uses two tasks, which on Free comes out of the same 100.

**AI Guardrails** is an action step you place after an AI step to screen its output for PII and prompt attacks. Zapier states "PII detection supports English and Spanish only", so do not rely on it to catch a Teudat Zehut in Hebrew text: add your own Code-step check (9 digits, the last of which is the check digit). **Chatbots** answer Hebrew customer questions against your Zapier Tables. Full notes, including why you must never hardcode a model name: `references/zapier-platform-notes.md`.

### Step 9: Use Common Zap Templates for Israeli Businesses

Ready-made patterns for invoicing, payment reconciliation, VAT-cycle reminders and WhatsApp follow-ups: `references/zap-templates.md`.

## Examples

### Example 1: Auto-Receipt for Cardcom Payments

User says: "I want to automatically create a Morning receipt when someone pays through Cardcom"

First rule out the paths that need no Zap and would otherwise produce a second tax invoice for the same sale: a Morning payment form (it charges through a clearing plugin and issues the document itself), or a `CreateLowProfile` request that sends a `Document` object (Cardcom then creates its own document, and the callback's `DocumentInfo` is not null). This recipe also assumes your site creates the Cardcom page by API, because `WebHookUrl` is sent on each request; for a page built another way, ask Cardcom how it reports transactions. An osek patur issues a 400 receipt, not a 320.

Actions:
1. Trigger: Webhooks by Zapier > Catch Hook. Pass its URL as `WebHookUrl` on each `CreateLowProfile` request, and put your order ID plus an unguessable secret in `ReturnValue`.
2. Filter: continue only if `ResponseCode` = 0, `Operation` is `ChargeOnly` or `ChargeAndCreateToken`, `TranzactionInfo Amount` exists and is above 0, `TranzactionInfo IsRefund` is not true, `TranzactionInfo CoinId` = 1 (ILS), and `ReturnValue` carries your secret. Repeat the `ResponseCode`, amount, refund and currency conditions on the step 3 response, which is the one you can trust. A successful token-only deal also returns 0, with no amount; a refund belongs on a 330 credit note, never a positive 320.
3. Re-fetch: Custom Request POST `https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult` with `TerminalNumber`, `ApiName` and the callback's `LowProfileId`, and take every value below from its response. A Catch Hook is a public URL, so a forged POST can carry anything; this call cannot be forged.
4. Dedupe: Zapier Tables > Find Record on `TranzactionId`, stop if found, and write the row after step 7. A replayed or retried run otherwise mints a second tax document, which then has to be reversed with a 330.
5. Token: Custom Request POST `https://api.morning.co/idp/v1/oauth/token`. Custom Request sends its Data "exactly as entered", so type `{"grant_type":"client_credentials","client_id":"...","client_secret":"..."}` and add `Content-Type: application/json` yourself. It returns `accessToken`, which **lives one hour**, so fetch it on every run.
6. Body: build it in Code by Zapier with `JSON.stringify`, never by mapping fields into a hand-typed JSON Data box. A customer named `כהן בע"מ` carries an ASCII quote that breaks hand-typed JSON and 400s the request for exactly those customers. Type 320, `lang: he`, `currency: ILS`, document `vatType: 0`; one `income[]` row (not `items[]`) with `price` (not `unitPrice`) = `TranzactionInfo.Amount` and row `vatType: 1`; one `payment[]` row with `type: 3` (credit card), the same `price`, `cardNum` = last 4 digits, `numPayments`, `dealType` 2 for installments, else 1, and `date` from the charge's own `CreateDate` (Israel time, `YYYY-MM-DD`), not the run date. A Bit or PayPal payment on the same page, or a sale your accountant treats as zero-rated (an exported service), needs a different row or no Zap: this body always records a card and extracts 18%. Add `client.taxId` for a business buyer (Step 4). Code: `references/zap-templates.md` Template 1.
7. Create: Custom Request `POST /documents` on `https://api.greeninvoice.co.il/api/v1`, Data = the Code step's string, headers `Content-Type: application/json` and `Authorization: Bearer <accessToken>`. With the customer's address in `client.emails` Morning emails the document link itself, so add no second email.
8. Allocation (B2B over the threshold only): the create response never carries the number, only `taxAuthorityConfirmationInitiated` and `taxAuthorityConfirmationLastError`. Wait with Delay by Zapier, then `GET /documents/{id}` and read `allocationNumber`. If it is missing or the error is not 0, alert yourself and hold the customer message; do not issue a second document.

Result: every genuine Cardcom charge becomes one Morning tax invoice/receipt, emailed by Morning. Budget about 5 tasks per payment (steps 3, 5, 6, 7 and the GET; Filter, Delay and Tables steps use none), so the base 750-task Professional tier covers roughly 150 payments a month. Past the limit Zapier either bills extra tasks (pay-per-task, up to 3x the plan) or holds the runs; it does not drop them.

### Example 2: Bimonthly VAT Summary

User says: "Send me a summary of all invoices at the end of each VAT period for my accountant"

Actions:
1. Create a Zap with Schedule by Zapier on specific months (March, May, July, September, November, January), reading the actual deadline for that period from a Zapier Table rather than assuming the 15th
2. Add the Morning token step (Example 1, step 5)
3. Add Code by Zapier that pages through `POST /documents/search` for the previous 2 months and totals revenue, VAT and credit notes in ILS (`references/zap-templates.md` Template 7; one search page holds only 25 documents by default)
4. Add Email action to accountant with RTL HTML summary table
5. Add Zapier Tables action to archive the period summary

Result: in each of those months an automated email reaches the accountant with the previous bimonthly period's invoice summary, comfortably ahead of that period's actual deadline. Check the business is genuinely on the bimonthly cycle first: above the turnover threshold in Step 4 it files monthly, and this Zap would then cover half its filings.

### Example 3: WhatsApp Payment Confirmation

User says: "Send a Hebrew WhatsApp message to customers when they pay"

Actions:
1. Set up the payment webhook trigger (Cardcom `WebHookUrl` JSON POST) with Example 1's Filter and re-fetch, or the customer is thanked for a declined card, a token-only deal, a refund or a forged POST
2. Add Formatter to format amount with " ש\"ח" suffix
3. Add Code by Zapier to normalise the phone with the function in the Gotchas. `UIValues.CardOwnerPhone` is empty unless the payment page sets `UIDefinition.IsCardOwnerPhoneRequired`.
4. Add **WhatsApp Business > Send Template Message** using a pre-approved Hebrew template
5. The template must be approved by Meta in advance, e.g.: "שלום {{1}}, קיבלנו תשלום בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
6. Map template variables: {{1}} = customer name, {{2}} = formatted amount, {{3}} = transaction ID. To send the document itself, run this after Example 1's create step and add a variable for its `url.he` link.

A proactive payment confirmation is outside the 24-hour customer-service window, so it must be a template. If instead the customer messaged you first, use the `New Message Received` trigger and `Send Freeform Message`, which sends arbitrary Hebrew with no template.

Do not use the "WhatsApp Notifications" app here. It only messages your own number. Twilio or WATI are alternatives if you need BSP-grade volume or a shared inbox.

Result: Customer receives a Hebrew WhatsApp confirmation within seconds of payment, using a Meta-approved template.

## Bundled Resources

### References
- `references/israeli-zapier-apps.md` -- Directory of Israeli apps available on Zapier (native integrations and webhook-based connections), including auth methods, API endpoints, and field mappings. Consult when connecting a new Israeli app to Zapier or troubleshooting authentication.
- `references/zapier-platform-notes.md` -- Facts about Zapier itself: plan names and limits, Tables and Forms, the AI features, the two WhatsApp apps, and the comparison against Make.com and n8n. Consult before quoting a price, a limit or a product name.
- `references/zap-templates.md` -- Ready-to-use Zap template configurations for common Israeli business workflows, with step-by-step field mappings and trigger/action details. Consult when building a new Zap and looking for a starting point that fits an Israeli business scenario.

## Related Skills and MCP Servers

The [green-invoice skill](https://agentskills.co.il/he/skills/accounting/green-invoice) covers Morning/Green Invoice API work directly and is the better starting point for invoice-document logic. Zapier ships its own MCP at `mcp.zapier.com`; its tools are individual app actions (the same ones Zaps use), not your published Zaps.

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
| Invoice Reform allocation numbers (ITA) | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice |

## Gotchas

- **The Cardcom callback has no top-level `Amount`**: the amount is **`TranzactionInfo.Amount`**, and `TranzactionInfo` is null on operations other than `ChargeOnly` and `ChargeAndCreateToken`. `Amount` exists on the `CreateLowProfile` REQUEST, which is where people copy it from. A top-level mapping sends an empty string.
- **Amounts are decimal shekels, not agorot**: Cardcom's `TranzactionInfo.Amount` (150.50 means 150.50 ILS), Tranzila's `sum`, Grow's `paymentSum`, iCount, EZcount and Morning all use decimal shekels. Never divide by 100. Every gateway amount INCLUDES VAT.
- **Morning's two `vatType` fields use different codes**: on a row (`income[].vatType`) `1` means the price INCLUDES VAT; on the document `1` means **exempt** (`0` default, `2` mixed). Map a gateway total with row `1` and document `0`. Getting either wrong returns no error.
- **Two different WhatsApp apps on Zapier**: "WhatsApp Notifications" only messages your own number; "WhatsApp Business" messages customers. Agents pick the first and conclude customer messaging is impossible. It is not.
- **Cardcom v11 webhook is a JSON POST to `WebHookUrl`** with `ResponseCode` (0) and `TranzactionId`, not the legacy `IndicatorUrl` GET with `DealResponse`, neither of which appears in v11. Migrate a Zap still filtering on `DealResponse`.
- **Webhooks by Zapier is premium**, so every Morning, Cardcom, Tranzila, Grow or iCount recipe needs a paid plan, whatever a help page's generic "Free" banner says.
- **Check the Zapier app directory before hand-rolling**: SUMIT, Priority ERP, InforUMobile and PayPlus have native apps. Morning, Cardcom, Tranzila, iCount, EZcount and Rivhit have none.
- **"Grow" on Zapier is not Meshulam**: `zapier.com/apps/grow` is an unrelated mailing-list product. Use Grow's JSON Webhooks service (enabled through Grow support); its API `notifyUrl` callback is form-encoded and expects an `ApproveTransaction` call back, so it is not a Catch Hook fit.
- **Allocation numbers are B2B, pre-VAT and never on the create response**: compare the pre-VAT amount to a threshold variable, only for a buyer with a `client.taxId`, and read `allocationNumber` from `GET /documents/{id}` or the `document/created` webhook.
- **Morning's access token expires in one hour, flat**, and line rows are `income[]` with `price`, with `lang` required. A pasted token or `items[]` / `unitPrice` / a missing `lang` produces 401 or 400.
- **Never hand-type mapped values into a JSON Data box**: Hebrew business names carry ASCII quotes (`בע"מ`, `רו"ח`) that break the JSON. Build bodies with `JSON.stringify` in a Code step.
- **Legacy ChatGPT Zap steps stopped working on 26 August 2026**: Zapier auto-migrated `Conversation With Assistant (Legacy)` steps to the new `Conversation` action but **left those Zaps turned off**, so a Hebrew summarization Zap that went quiet in late August is waiting to be re-enabled. `Create Assistant`, `Upload File` and the assistant searches have no replacement.
- **Morning document types**: Receipt (400) after payment, Tax Invoice (305) before or at the sale, Tax Invoice/Receipt (320) both. For an osek murshe card sale 320 is usually right: a bare 400 is not the tax invoice the customer deducts input VAT against. Agents default to 400.
- **Phone numbers for WhatsApp/Twilio**: one Israeli-only normaliser, used everywhere: `let d=(inputData.phone||'').replace(/\D/g,'').replace(/^00/,''); if (d.startsWith('972')) d=d.slice(3); d=d.replace(/^0/,''); const phone = d ? '+972'+d : '';`. It handles `054-123-4567`, `+972-54-...`, `00972...` and `+972 (0)54...`. Do not run it on a number that arrived with another country code.
- **VAT rate**: 18% since January 2025. Agents sometimes use the outdated 17%.
- **There is no Starter plan**: it was discontinued on 2 April 2024 and folded into Professional.

## Troubleshooting

### Error: "Webhook not receiving data from Cardcom"
Cause: most often the Zap is built against the legacy `IndicatorUrl` GET rather than the v11 `WebHookUrl` JSON POST.
Solution: send the Catch Hook URL as `WebHookUrl` on each `CreateLowProfile` request (a required field, so the call fails validation without it). Look in Zapier's webhook history for **POST** requests with a JSON body, filter on `ResponseCode`, not `DealResponse`, and test with a real 1 ILS payment on a production terminal.

### Error: "Morning API returns 401 Unauthorized"
Cause: almost always an expired token. `accessToken` is valid for one hour.
Solution: fetch a token in the Zap on every run (Example 1, step 5) and map it into `Authorization: Bearer <accessToken>`. Errors follow the RFC 6749 OAuth format; the per-code table is in `references/israeli-zapier-apps.md`.

### Error: "Hebrew text appears garbled in emails"
Cause: Email template missing UTF-8 charset or RTL direction.
Solution: Wrap Hebrew content in a `<div dir="rtl">` tag and include `<meta charset="UTF-8">` in the head.

### Error: "WhatsApp message fails to send to customer"
Cause: using "WhatsApp Notifications", which only sends to the number that authenticated the connection.
Solution: switch to "WhatsApp Business". Outside the 24-hour window use a Meta-approved template. A green Zap run is not delivery: Zapier marks WhatsApp Business runs successful even when the send fails, so read `Message Status Updated` or Meta Business Manager.

### Error: "Invoice Reform allocation number missing"
Cause: the Zap read it from the create-document response, which never carries it, or read the document before Morning finished the request, or the buyer has no `client.taxId`.
Solution: check `taxAuthorityConfirmationLastError` on the create response, wait, then read `allocationNumber` from `GET /documents/{id}` or the `document/created` webhook. Confirm Morning's Tax Authority connection is active and the invoice carries the buyer's ח.פ.

## When to Use Zapier vs Alternatives

Zapier is the easiest path for a non-technical Israeli business owner: the biggest catalogue, a visual builder and Copilot. Make.com is usually cheaper at high task volume, and n8n is the choice for self-hosting, the only one of the three where payment data never leaves your infrastructure. Full comparison: `references/zapier-platform-notes.md`.
