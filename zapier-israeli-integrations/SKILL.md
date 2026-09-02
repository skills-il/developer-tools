---
name: zapier-israeli-integrations
description: Build Zapier Zaps connecting Israeli business apps (Morning/Green Invoice, Cardcom, Tranzila, iCount, Grow, SUMIT, Priority, InforUMobile) with global services for billing, payment, and workflow automation. Use when asked to "create a Zap for Israeli invoicing", "automate Morning receipts", "connect Cardcom to my CRM", or set up payment notifications. Covers Hebrew text handling, ILS formatting, bimonthly VAT logic, Invoice Reform allocation numbers, Zapier AI (Copilot, Agents, MCP), and webhooks from Israeli processors. All amounts use decimal shekels, not agorot. Do NOT use for n8n (use n8n-hebrew-workflows), Make.com (use make-com-israeli-automations), or non-Zapier automation.
license: MIT
compatibility: Requires Zapier account. Free plan includes unlimited two-step Zaps and 100 tasks/month. Multi-step Zaps require Professional, the entry paid tier at $19.99/month annual for 750 tasks, scaling by task tier within the same plan; Team is $69/month annual. Webhook triggers use Webhooks by Zapier (available on all plans). No local dependencies.
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

**Single-step vs multi-step.** Free gives unlimited Zaps but only two steps (one trigger, one action), 100 tasks/month and 15-minute polling, so it fits "new payment -> log a row" and little else. Almost every automation here needs multi-step, which starts at Professional. Paths (branching) handle the "if the pre-VAT amount is over the Invoice Reform threshold, add an allocation number" shape; keep that threshold in a workflow variable rather than a hardcoded number, so a future change is a one-line edit. Per-plan prices and limits: `references/zapier-platform-notes.md`.

**Use Zapier Copilot** to describe what you want in plain English or Hebrew ("when I get a Cardcom payment, create a Morning receipt and email it"). It suggests the structure, finds the apps and maps fields. On every plan, with a daily message limit on Free.

### Step 2: Connect Israeli Apps in Zapier

Israeli apps reach Zapier three ways. **Always check the app directory first** (`zapier.com/apps/<app-slug>/integrations`): a native app is simpler and more reliable than a hand-built Custom Request, and several Israeli vendors now ship one. Fall back to Webhooks by Zapier only when none exists.

- **Native Zapier apps:** SUMIT, Priority ERP, InforUMobile, Responder and Responder Live (רב מסר), Monday.com, Wix. Prefer these over raw HTTP every time.
- **Webhooks by Zapier:** Morning (formerly Green Invoice), Cardcom, Tranzila, iCount, EZcount, Rivhit, 019 SMS, and Grow. None of these has a native app.
- **Do not search Zapier for "Grow".** The app at `zapier.com/apps/grow` is an unrelated US mailing-list product, not the Israeli payment gateway. The gateway's own brand is now simply Grow (`meshulam.co.il` redirects to `grow.business`), which makes the collision worse, not better.

**Morning auth is OAuth 2.0 now.** The current spec (`https://developers.morning.co/docs/openapi.bundled.json`, `openapi: 3.0.3`, info.version 2.0.0) documents `POST https://api.morning.co/idp/v1/oauth/token` with `grant_type=client_credentials`, returning a short-lived JWT you send as `Authorization: Bearer`. The production base for every other call is still `https://api.greeninvoice.co.il/api/v1`. The legacy `POST /api/v1/account/token` on that host still answers, but it no longer appears anywhere in the spec: treat it as undocumented legacy, not as an equal alternative, and do not build a new Zap on it. Amounts are decimal shekels, never agorot.

Per-app connection method, auth type, webhook payload fields, exact native trigger and action names, and migration notes: `references/israeli-zapier-apps.md`.

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

**ILS currency and Israeli dates.** Zapier has no native ILS currency format, so use Formatter > Numbers > Format Number (2 decimals, `.` decimal, `,` thousands) and concatenate " ש\"ח" yourself. For dates use Formatter > Date/Time with `DD/MM/YYYY`: the default MM/DD/YYYY will be misread by Israeli recipients, and silently so for any day under 13. Exact settings: `references/zapier-platform-notes.md`.

### Step 4: Build Israeli Billing Cycle Automations

Israeli tax reporting follows specific cycles. Build Zaps that align with these periods.

**First establish whether the business reports bimonthly or MONTHLY.** This is set by turnover, and a Zap built on the wrong cadence silently misses filings. Under `סעיף 67(א2)(1)` of the VAT Law and `תקנה 20(ג)(1)` of the VAT Regulations, bimonthly reporting applies to a turnover of up to **1,775,000 NIS**; a turnover **above** that reports **monthly**. The figure shown is the one in force for 2026; `תקנה 20(ג)(2)` re-indexes it on 1 September each year and rounds to the nearest 5,000 NIS, so re-read it annually rather than hardcoding it. A bimonthly Schedule Zap built for a business over the line misses six filings a year and nothing in Zapier will tell you.

**Bimonthly VAT period Zaps** (turnover at or below the threshold): the periods are Jan-Feb, Mar-Apr, May-Jun, Jul-Aug, Sep-Oct, Nov-Dec. Use Schedule by Zapier:
- Trigger: Schedule on specific months (March, May, July, September, November, January), several days before that period's actual deadline
- Action: Pull all invoices/receipts from the previous 2 months via Morning API and compile for VAT reporting
- This is simpler than a monthly trigger with an odd-month filter

**Do not hardcode the 15th.** The statutory date is the 15th of the month following the period (the 16th for income-tax withholding, the 23rd for the detailed VAT report), and online filing extends it to the 19th at 18:30. But the Tax Authority publishes an **annual deferral table** that moves most of those dates, for weekends, rest days of different faiths, and business-day counts. For 2026 the periodic VAT and mikdamot dates are 16.2, 16.3, **27.4**, 18.5, 15.6, 15.7, 17.8, **24.9**, **19.10**, 16.11, 15.12 and 18.1.2027. Eight of the twelve are not the 15th, and the deferrals are as large as twelve days.

**Each report type gets its own column, so do not reuse one set of dates for another.** Withholding (nikuyim) diverges from the VAT dates in June, July and December, and the detailed VAT report is a separate set entirely, so a Zap reminding on the periodic dates is wrong for it in most months. Both full 2026 columns: `references/israeli-zapier-apps.md`.

**The annual table is not the last word either.** The Tax Authority issues separate announcements during the year (security situations, emergencies) that defer individual periods further. Check for a superseding announcement before treating any date as final.

Build the reminder Zap so the date is data, not code: keep the current year's deadlines in a Zapier Table (period, deadline date) and have the Schedule Zap look the row up, or set the trigger conservatively early. Re-import the table each January when the Tax Authority publishes the new one. A Zap that fires "five days before the 15th" was, in 2026, twelve days early in April and nine days early in September.

**Mikdamot (advance tax) reminders** ride the SAME deferred dates as periodic VAT in the annual table, so drive them from the same Zapier Table row rather than a hardcoded day. Whether a given business pays bimonthly or monthly is set by its Tax Authority classification, so confirm it per client instead of assuming.

**Annual report trigger:** Schedule in January, compile total revenue, expenses, VAT paid and tax withheld at source (nikui mas ba-makor) from Morning, send to the accountant.

**Key Israeli tax dates to encode in Zaps:**

| Date | Event | Zap Action |
|------|-------|------------|
| That period's row in the annual table | VAT report and mikdamot deadline | Look the date up, remind several days before |
| January | Previous year annual summary | Compile and send to accountant |
| Announced annually | Annual tax filing deadline | Filing reminder. Do NOT hardcode a date, see below |

**The annual filing deadline is announced each year and is not a fixed date.** The Ordinance dates (30 April for a non-online individual, 31 May for an online one) are routinely deferred, often by a month or more: for tax year 2025 the operative dates were **31.5.2026**, **30.6.2026** and **30.7.2026** for companies, NPOs and controlling shareholders respectively. The representatives' extension arrangement (הסדר האורכות למייצגים) runs later still and is announced separately. Read the current year's announcement before encoding any date, and prefer a Zapier Table row over a literal in a Filter step.

Note this section does not cover Bituach Leumi advances, which run on their own schedule and are a separate obligation: see `references/israeli-zapier-apps.md`.

**Israel Invoice Reform allocation numbers:**
Tax invoices over the threshold require a Tax Authority allocation number (mispar haktza'a). **The current threshold is 5,000 NIS, in force since June 2026.** The step-down to date:

| Effective | Threshold |
|-----------|-----------|
| May 2024 | 25,000 NIS |
| Jan 2025 | 20,000 NIS |
| Jan 2026 | 10,000 NIS |
| **Jun 2026 onward (current)** | **5,000 NIS** |

**The threshold is measured BEFORE VAT.** This is the most common way an Invoice Reform Zap goes wrong: gateways send the charged total, which already includes VAT, so comparing it directly against 5,000 over-flags every invoice whose pre-VAT base is under the threshold. At 18% VAT a 5,900 ILS charge is exactly a 5,000 ILS base.

When building invoice-creation Zaps:
- Derive the pre-VAT amount first: divide the gateway total by 1.18, or read Morning's pre-VAT figure rather than the total. Compare that against a workflow variable holding the threshold, not a hardcoded number.
- The allocation number must be obtained before the invoice is issued, and **there is no public REST API for it**: access is via registered software houses under a signed undertaking, or the manual request form. Do not let an agent invent an endpoint. Route the document through an authorized platform (Morning, iCount, EZcount, SUMIT) and let it request the number.
- **But do not read the number off the create response, which never carries it.** `POST /documents` returns `taxAuthorityConfirmationInitiated` and `taxAuthorityConfirmationLastError`; `allocationNumber` lives on the document, so fetch it from `GET /documents/{id}` or the `document/created` webhook. A Filter on the create response tests a permanently blank field and reports success either way.
- **Never split an invoice to stay under the threshold.** A Tax Authority research publication dated 2 June 2026 states that artificial splitting of a transaction is contrary to law (`פיצול מלאכותי של עסקה הינו בניגוד לחוק`), quantifies it at 12.2 to 16.4 billion NIS of 2025 transactions shifted below the line, and floats requiring an allocation number from the first shekel. A Filter comparing a pre-VAT amount to the threshold is one careless step from a splitting rule: keep it a flag-for-allocation branch, never a split-the-charge branch.

### Step 5: Set Up Webhook-Based Israeli Integrations

For vendors with no native Zapier app, use Webhooks by Zapier (Catch Hook for inbound, Custom Request for outbound). Cardcom v11 POSTs JSON to `WebHookUrl`; success is `ResponseCode == 0`; cardholder fields nest under `UIValues`. Full payload tables and the Tranzila caveat: `references/israeli-zapier-apps.md`.

### Step 6: WhatsApp Business Messaging

Zapier has **two different WhatsApp apps** and they are routinely confused.

| Zapier app | Who it can message | What it does |
|------------|--------------------|--------------|
| **WhatsApp Notifications** | **Only yourself.** Zapier's own help page is explicit: it sends "yourself WhatsApp messages to your WhatsApp account", and the connection is authenticated by confirming your own phone number via an OTP | Exactly one action and no triggers: `Send Message`. Limited to seven prefilled templates (New Lead, New Message, Payment Confirmation, New Order, Shipping Confirmation, Calendar Reminder, Zap Error), capped at 1024 characters, and "custom templates cannot be created". Good for "alert me when a payment lands". Not usable for customers. |
| **WhatsApp Business** | **Your customers** | Triggers `New Message Received` and `Message Status Updated`. Actions `Send Template Message`, `Send Freeform Message`, `Send Media Message`, `Get Attachment`. |

**Use WhatsApp Business for anything customer-facing.** Meta's window rule decides which action you need: outside the 24-hour customer-service window you must send a Meta-approved template (submitted in advance; Meta's template docs say review can take up to 24 hours, Hebrew supported but the Hebrew text is what gets approved); inside the window, opened when the customer messages you first, `Send Freeform Message` sends arbitrary Hebrew with no template. A proactive payment confirmation is outside the window and needs a template. A reply to "did my payment go through?" does not.

If you already use InforUMobile for SMS, its native Zapier app has a `Send Whatsapp Template Message` action and saves a second vendor. Twilio, WATI and Respond.io (slug `respondio`) are the BSP options, worth it only for high volume, a shared inbox or multi-channel routing.

**Budget real setup time before promising this to a client.** WhatsApp Business is not the OTP-and-go flow the Notifications app uses: it needs a Meta Business account, business verification, a Cloud API app, and a phone number that is NOT already on consumer WhatsApp. It also costs money per message outside the 24-hour window. Prerequisites, pricing and approved-template examples: `references/zapier-platform-notes.md` and `references/israeli-zapier-apps.md`.

### Step 7: Use Zapier Tables and Forms (2026)

**Zapier Interfaces is now Zapier Forms** (`zapier.com/interfaces` redirects to `zapier.com/forms`), so older tutorials name a product that no longer exists under that name. Tables is a native database inside Zapier that beats Google Sheets for payment logs, client lists and invoice archives, because it needs no external auth and its "New Record" and "Updated Record" triggers can start a Zap. Google Sheets still wins when the accountant needs direct access, or when you need pivots and complex formulas.

Both are on every plan including Free, but "available" is not "unmetered": Free caps Tables at 2,500 records and Forms at 10 pages per account. Size that against your invoice volume before you build on it.

Per-plan limits, the comparison table, field types and the Forms use cases: `references/zapier-platform-notes.md`.

### Step 8: Use Zapier AI Features

**Copilot** builds Zaps from a natural-language description in English or Hebrew and can troubleshoot a failing Zap. It is on every plan, but Free carries a daily message limit.

**Zapier Agents** (`agents.zapier.com`) are autonomous agents that act across Zapier's app catalogue without predefined steps, for example "chase Morning invoices unpaid past 30 days with Hebrew reminder emails". It launched as **Zapier Central** and was renamed, so older tutorials use the old name. Agents consume a separate activity allowance, not your task quota.

**Zapier MCP** (`zapier.com/mcp`) exposes 30,000+ actions across 9,000+ apps to Claude Code, ChatGPT and Cursor, the fastest way to build and test an Israeli automation from your editor.

**AI Guardrails** adds PII detection (Teudat Zehut numbers, card details) and prompt-attack detection to AI steps; turn it on for any flow touching identity or payment data. **Chatbots** answer Hebrew customer questions against your Zapier Tables. Full notes, including why you must never hardcode a model name: `references/zapier-platform-notes.md`.

### Step 9: Use Common Zap Templates for Israeli Businesses

Ready-made patterns for invoicing, payment reconciliation, VAT-cycle reminders and WhatsApp follow-ups: `references/zap-templates.md`.

## Examples

### Example 1: Auto-Receipt for Cardcom Payments

User says: "I want to automatically create a Morning receipt when someone pays through Cardcom"

Actions:
1. Create a Zap with Webhooks by Zapier > Catch Hook as trigger
2. Pass the Catch Hook URL as `WebHookUrl` on your Cardcom `CreateLowProfile` request
3. Add a Filter step: only continue if `ResponseCode` = 0 (successful payment)
4. Add a FIRST Webhooks by Zapier > Custom Request that POSTs `grant_type=client_credentials` with your client ID and secret to `https://api.morning.co/idp/v1/oauth/token`. It returns `accessToken` (a JWT) and `expiresAt`. **The token lives one hour**, so this step belongs in every run; a token pasted once into a static header stops working the same afternoon.
5. Add a SECOND Custom Request to `POST /documents` on `https://api.greeninvoice.co.il/api/v1`, passing the `accessToken` from step 4 as `Authorization: Bearer <accessToken>`. For a card sale by an osek murshe, create **type 320 (חשבונית מס/קבלה)**, not a bare 400 receipt: 320 is the tax invoice that lets the customer deduct input VAT and is the document an allocation number attaches to.
6. Build the body against the real schema: line rows go in `income[]` (there is no `items[]`) and the price field is `price`, not `unitPrice`. Full required-field list and the client mapping: `references/zap-templates.md`.
7. Map **`TranzactionInfo.Amount`** to `income[0].price`. The amount is NOT at the top level of the callback, see the Gotchas.
8. The create response does NOT carry the allocation number. Check `taxAuthorityConfirmationInitiated` on it, then read `allocationNumber` from a follow-up `GET /documents/{id}` or Morning's `document/created` webhook.
9. Add email action to send the document link to the customer

Result: Every successful Cardcom payment automatically generates a Morning tax invoice/receipt and emails it to the customer.

### Example 2: Bimonthly VAT Summary

User says: "Send me a summary of all invoices at the end of each VAT period for my accountant"

Actions:
1. Create a Zap with Schedule by Zapier on specific months (March, May, July, September, November, January), reading the actual deadline for that period from a Zapier Table rather than assuming the 15th
2. Add Webhooks by Zapier > Custom Request to call Morning API Find Documents for the previous 2 months
3. Add Code by Zapier to calculate total revenue, total VAT collected, invoice count
4. Add Email action to accountant with RTL HTML summary table
5. Add Zapier Tables action to archive the period summary

Result: in each of those months an automated email reaches the accountant with the previous bimonthly period's invoice summary, comfortably ahead of that period's actual deadline. Check the business is genuinely on the bimonthly cycle first: above the turnover threshold in Step 4 it files monthly, and this Zap would then cover half its filings.

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

Result: annual tax preparation data is compiled and sent to the accountant every January, months ahead of any plausible filing deadline. Do not encode the deadline itself in the Zap: it is announced annually and moves (for tax year 2025 it was 31.5.2026 for individuals not filing online, 30.6.2026 for those filing online, and 30.7.2026 for companies).

## Bundled Resources

### References
- `references/israeli-zapier-apps.md` -- Directory of Israeli apps available on Zapier (native integrations and webhook-based connections), including auth methods, API endpoints, and field mappings. Consult when connecting a new Israeli app to Zapier or troubleshooting authentication.
- `references/zapier-platform-notes.md` -- Facts about Zapier itself: plan names and limits, Tables and Forms, the AI features, the two WhatsApp apps, and the comparison against Make.com and n8n. Consult before quoting a price, a limit or a product name.
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
| Invoice Reform allocation numbers (ITA) | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice |

## Gotchas

- **The Cardcom callback has no top-level `Amount`**: this is the single most common way a Cardcom-to-Morning Zap silently breaks. In the v11 `LowProfileResult` schema the amount is at **`TranzactionInfo.Amount`**, and `TranzactionInfo` is null on operations other than `ChargeOnly` and `ChargeAndCreateToken`. `Amount` exists on the `CreateLowProfile` REQUEST, which is where people read it from. Mapping a top-level `Amount` sends an empty string, and Morning then rejects the row or issues a zero-value document.
- **Cardcom amounts are decimal shekels, not agorot**: the value at `TranzactionInfo.Amount` is decimal shekels (150.50 means 150.50 ILS). Do NOT divide by 100; that would create documents at 1/100th the correct amount. Morning also takes decimal shekels. Tranzila, Grow, iCount and EZcount units are NOT verified here, so confirm each against its own vendor docs before assuming.
- **Two different WhatsApp apps on Zapier**: "WhatsApp Notifications" only messages your own number and is limited to prefilled templates. "WhatsApp Business" messages customers and offers `Send Template Message`, `Send Freeform Message` (inside the 24-hour window) and `Send Media Message`. Agents routinely pick the first and conclude customer messaging is impossible. It is not.
- **Cardcom v11 webhook is a JSON POST to `WebHookUrl`**: Not a GET to `IndicatorUrl`. The success field is `ResponseCode` (0 = success), not `DealResponse`, and the transaction ID is `TranzactionId`. `InternalDealNumber` exists in the v11 API only as a lookup key on transaction-info requests, not as a webhook field. Cardholder details are nested under `UIValues`. Zaps written against `IndicatorUrl` / `DealResponse` are on the legacy path and will never fire.
- **Check the Zapier app directory before hand-rolling**: SUMIT, Priority ERP and InforUMobile all have native Zapier apps, so `Create Document` and `Send SMS` are one click rather than a Custom Request. Morning, Cardcom, Tranzila, iCount, EZcount and Rivhit genuinely have none and do require webhooks.
- **"Grow" on Zapier is not Meshulam**: `zapier.com/apps/grow` is an unrelated mailing-list product for publishers. Grow by Meshulam has no Zapier app; use its JSON webhook.
- **Invoice Reform thresholds are pre-VAT**: gateway amounts include VAT, so divide by 1.18 (or read Morning's pre-VAT figure) before comparing to the 5,000 ILS threshold, or the Zap over-flags every invoice between 5,000 and 5,900 gross. Keep the threshold in a Zap variable, not a literal.
- **The Morning create-document response does not contain the allocation number**: it returns `taxAuthorityConfirmationInitiated` and `taxAuthorityConfirmationLastError`. `allocationNumber` lives on the document, so read it from `GET /documents/{id}` or the `document/created` webhook. A Filter built on the create response compares against a permanently blank field and reports success either way.
- **Morning's access token expires in one hour, flat**: it is not a plan setting. Every Zap needs its own token-fetch step (`grant_type=client_credentials` to `https://api.morning.co/idp/v1/oauth/token`); a token pasted into a static header works while you test and dies the same afternoon.
- **Morning line rows are `income[]`, not `items[]`**, and the price field is `price`, not `unitPrice`. `lang` is also required at document level and is the field most often omitted. Any of these produces a hard 400.
- **Legacy ChatGPT Zap steps stop working after August 26, 2026**: Zaps built on the deprecated ChatGPT / OpenAI Assistants actions (creating assistants, uploading files) break on that date. If a Hebrew summarization or categorization step uses them, migrate it before then.
- **Hebrew in code steps**: When using "Code by Zapier" (JavaScript or Python), Hebrew string literals work fine, but Hebrew in variable names will break. Keep variable names in English, use Hebrew only in string values.
- **Morning document types**: Receipt (400) is issued after payment, Tax Invoice (305) before or at the sale, and Tax Invoice/Receipt (320) combines both. For an osek murshe card sale, 320 is usually right: a bare 400 documents the money but is not the tax invoice the customer deducts input VAT against, and an allocation number attaches to the invoice, not the receipt. Agents default to 400 and get this wrong.
- **Phone number format for WhatsApp/Twilio**: Israeli mobile numbers must include the +972 prefix and drop the leading 0 (e.g., 0541234567 becomes +972541234567). Use Code by Zapier: `phone.replace(/^0/, '+972')`.
- **VAT rate**: The current Israeli VAT rate is 18% (since January 2025). Agents sometimes use the outdated 17% rate in calculations.
- **Formatter does NOT strip Unicode markers**: "Trim Whitespace" removes standard whitespace but not RTL/LTR markers (U+200F, U+200E). Use a Code by Zapier step with regex to clean Hebrew text properly.
- **There is no Starter plan**: it was discontinued on 2 April 2024 and folded into Professional, so tutorials pricing "Starter" describe a plan that no longer exists. Free is two-step only and 100 tasks/month, which almost no Israeli billing automation fits.

## Troubleshooting

### Error: "Webhook not receiving data from Cardcom"
Cause: most often the Zap is built against the legacy `IndicatorUrl` GET mechanism rather than the v11 `WebHookUrl` JSON POST.
Solution: Confirm you are passing the Zapier Catch Hook URL as the `WebHookUrl` field on each `CreateLowProfile` request. It is a required field on that request, so if you are not sending it the call itself will fail validation. Check Zapier's webhook history for incoming **POST** requests carrying a JSON body. If your Filter tests `DealResponse`, it will never match: the v11 field is `ResponseCode`. Then confirm the terminal is in production mode, not sandbox, and make a real small-amount payment (1 ILS) to test.

### Error: "Morning API returns 401 Unauthorized"
Cause: most often the access token has simply expired. Morning's `accessToken` is valid for **one hour**, flat, and this is not a plan setting. A Zap that carries a token pasted into a static header works while you test and then 401s on the next real payment.
Solution: add a token-fetch step to the Zap itself (POST `grant_type=client_credentials` to `https://api.morning.co/idp/v1/oauth/token`) and map the returned `accessToken` into the next step's `Authorization: Bearer <accessToken>` header, rather than hardcoding one. The response also returns `expiresAt`. Errors follow the RFC 6749 OAuth format; the per-code table is in `references/israeli-zapier-apps.md`.

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
Cause: either the amount was divided by 100 (legacy advice that is wrong), or, far more often, the Zap mapped a top-level `Amount` that the callback does not contain, so an empty value reached Morning.
Solution: map **`TranzactionInfo.Amount`**, and check it is populated (it is null outside `ChargeOnly` / `ChargeAndCreateToken`). The value is already decimal shekels, so use it as-is and do NOT divide by 100. A document that comes out as 0 is the mapped-field-missing case; one that comes out 100x too small is the division case.

## When to Use Zapier vs Alternatives

Zapier is the easiest path for a non-technical Israeli business owner: the biggest app catalogue, a visual builder, Copilot to draft the Zap, and native apps for SUMIT, Priority, InforUMobile, Responder (רב מסר), Monday.com and Wix (everything else Israeli is webhook-based). Make.com is usually more cost-effective at high task volume and handles complex multi-branch scenarios better. n8n is the choice when you want self-hosting and full control, and it is the only one of the three where Hebrew transcripts and payment data never leave your own infrastructure.

Full comparison across ease of use, integrations, AI features, free tiers and Israeli community size: `references/zapier-platform-notes.md`.
