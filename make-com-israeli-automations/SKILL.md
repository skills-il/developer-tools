---
name: make-com-israeli-automations
description: Build and configure Make.com scenarios for Israeli business processes, including Morning (formerly Green Invoice) sync, iCount accounting, Monday.com board automation, Priority ERP data exports, WhatsApp Business Hebrew messaging, and payment gateways (Cardcom, Tranzila, Grow, Bit). Covers Make.com AI Agents, the Make.com MCP server for exposing scenarios as agent tools, Israel 2026 Invoice Reform (allocation numbers with a step-down threshold), community modules for Israeli apps, Hebrew data transformations, Data Store for VAT period tracking, and Shabbat-aware scheduling via the Hebcal community module. Use when user asks to "create a Make.com scenario", "build an automation for Israeli billing", "automate Morning / Green Invoice", "connect Israeli apps in Make.com", "set up AI agent in Make.com", or "expose a Make.com scenario as an MCP tool". Do NOT use for n8n workflows (use n8n-hebrew-workflows), Zapier Zaps (use zapier-israeli-integrations), or custom code automation without Make.com.
license: MIT
allowed-tools: Bash(curl:*) Bash(node:*) Bash(python:*)
compatibility: Requires Make.com account (Free plan has 1,000 credits/month). Morning community module requires a Morning Best plan or higher (Morning's Basic plan has no API access). iCount has a native module. Priority ERP community module or HTTP module. WhatsApp Cloud API requires Meta Business verification.
---

# Make.com Israeli Automations

## Instructions

### Step 1: Identify the Scenario Pattern

Before building any scenario, map the business workflow to a Make.com pattern. Israeli business automations fall into predictable categories:

| Business Workflow | Make.com Pattern | Core Modules | Trigger Type |
|---|---|---|---|
| Invoice creation and sync | Watch + Create | Morning (community), iCount (native), Monday.com | Webhook / Scheduled |
| Billing cycle reporting | Router + Aggregator | Morning, Google Sheets, HTTP | Scheduled (monthly/bimonthly) |
| Customer messaging | Watch + Iterator + Module | WhatsApp Business Cloud (native), Monday.com | Webhook |
| ERP data export | HTTP + JSON Parse + Router | Priority (community or HTTP), Google Sheets | Scheduled |
| Payment notification | Webhook + Router + Create | Cardcom/Tranzila/Grow/Bit webhook, Slack/Email | Instant (webhook) |
| Document generation | Watch + Template + Email | Morning, Google Docs, Gmail | Event-driven |
| AI-powered processing | AI Agent + Module Tools | Any module as AI tool, Router | Event-driven / Scheduled |

Choose the pattern based on these criteria:
- **Real-time needed?** Use webhooks (instant triggers). Otherwise, use scheduled polling.
- **Multiple destinations?** Use a Router module to branch the flow.
- **Either/or branches that must rejoin?** Use If-else plus Merge. A Router "Runs all conditions in the set order" and its routes "can't be merged back together", so you end up duplicating the downstream module on every route. Make documents both If-else and Merge as using operations but consuming no credits.
- **Processing a list?** Use an Iterator to loop over items (e.g., line items on an invoice).
- **Aggregating data?** Use an Array Aggregator before the final output.
- **AI decision needed?** Use Make.com AI Agents with Module Tools (see Step 8).

### Step 2: Configure Israeli App Connections

**Morning (formerly Green Invoice / Hashbonit Yeruqa)**

Morning has a **community-built** Make.com module, created by Callbox and listed as "Morning by Callbox" on the Make.com marketplace. Make.com states: "Make does not maintain or support this integration." It requires a **Morning Best plan or higher**: Best is Morning's own subscription tier (the first one with API access, above Basic), not a Make plan.

To set up the connection:

1. In Make.com, search for "Morning" in the module palette (NOT "Green Invoice")
2. Create a connection with your Morning API keys, which Morning now issues as OAuth 2.0 client credentials (a client ID and secret per environment)
3. The API base remains `https://api.greeninvoice.co.il/api/v1` despite the rebrand

Available actions (there are NO watch/trigger modules):

The module's action list (Add Client, Add Document, Add Expense, the Get All / Search variants, Update and Delete Client, Add Supplier, Get Document, plus the raw `Make an API Call`) is tabulated with its key parameters in `references/make-israeli-modules.md`.

Since there are no triggers, use one of these patterns for event-driven scenarios:
- **Scheduled polling:** Use "Search Documents" on a schedule (e.g., every 15 minutes) filtered to recent documents
- **Morning's own webhook (preferred):** Morning sends a `document/created` webhook whose payload carries the document `type`, `number`, `subtotal`, `total` and `recipient`. Point it at a Make.com Custom Webhook. Morning lists webhooks from its Best plan up

Key field mappings for Morning documents:

The Morning field mapping (document `type` codes, `currency`, `vatType`, `lang`) is tabulated in `references/make-israeli-modules.md`. Two that cause real damage if guessed: `income[].price` is in **decimal shekels, not agorot** (`price: 50` is 50 shekels), and `type` is a numeric code (305 = tax invoice, 320 = tax invoice/receipt, 400 = receipt).

**Israel Invoice Reform 2026 (threshold step-down):** Tax invoices over the threshold require a Tax Authority allocation number (mispar haktza'a). The threshold drops in 2026:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |

Morning supports the Israel Invoice model, and its document response carries `allocationNumber` ("Allocation Number issued by the Israeli Tax Authority"). Read it back from the created document and store it. The gov.il online request form is for businesses using a paper booklet or software not connected to the service, and it asks for the customer's osek murshe number, so the requirement applies when the buyer is an osek murshe.

**Compare the amount BEFORE VAT.** The Tax Authority states the requirement applies "כשסכום העסקה לפני מע"מ גבוה מ-5,000 ₪". A scenario that tests the gross document total requests an allocation number on every invoice between roughly 4,238 and 5,000 NIS net that does not need one.

**What actually happens without one:** the allocation number is a condition for the RECIPIENT deducting input VAT (`יידרשו כתנאי לניכוי מס התשומות`), not a condition of the invoice's validity. The invoice is not void; the buyer simply cannot deduct מס תשומות.

After Add Document, route through an If-else (buyer is an osek murshe AND net amount above the threshold: check `allocationNumber` is present, alert if not) and Merge back. Hold the threshold in a workflow variable for maintainability; the published schedule ends at 5,000 NIS from 1 June 2026 and no further step-down has been legislated.

**iCount**

iCount has a **native Make.com module** (first-party supported). This is a significant option for Israeli accounting automation.

Available actions include:
- Create/manage expenses, leads, tasks, events
- Inventory management
- Client management
- Create documents (invoices, receipts, quotes)

To set up: search "iCount" in the module palette, connect with your iCount API credentials.

**Monday.com**

Monday.com has a native Make.com module. Israeli businesses commonly use it for project billing.

**Important (API versioning):** monday.com does not version its API as v1/v2. `api.monday.com/v2` is the GraphQL ENDPOINT path, and it has not changed. The API *version* is date-based and rolls quarterly: since October 1st, 2026 `2026-10` is the current default, `2026-07` is in maintenance and `2027-01` is the release candidate (current from January 15th, 2027). Select it per request with an `API-Version` header and pin it explicitly; monday states that "Each version deprecation will be announced at least six months in advance".

Separately, Make's own monday.com app has two versions: "monday.com Version 1 is now legacy and its maintenance has ended". Click the upgrade arrow on each existing monday.com module to switch it to Version 2.

1. Use "Watch Items" as trigger (set to a specific board)
2. Map column values using the column ID (not the title, since titles may be in Hebrew and can be renamed)
3. For status columns, use the label index (not the Hebrew label text) for reliable matching

**Priority ERP**

Priority has a **community-built Make.com module** available on the marketplace. Search for "Priority" in the module palette. Alternatively, use HTTP modules for full control.

For the community module:
1. Search "Priority" in Make.com modules
2. Connect with your Priority credentials

For HTTP module approach:
1. Add an HTTP "Make a request" module
2. URL pattern: `https://{your-priority-domain}/odata/Priority/tabula.ini/{company}/{entity}`
3. Authentication options: Basic Auth, Personal Access Token (PAT), or OAuth2 (Priority supports all three)
4. Set header `Content-Type: application/json`
5. For Hebrew field values, ensure the request body is UTF-8 encoded

Entity (form) names are installation-dependent: Priority's docs use `ORDERS` (sales orders) as the example, and for anything else read `$metadata` from your own installation rather than guessing a form name.

**WhatsApp Business**

Make.com has a **native first-party WhatsApp Business Cloud module**. Use this instead of the HTTP module approach for simpler setup and built-in error handling.

Available triggers and actions:
- **Watch Events** (trigger): Receives incoming messages, status updates
- **Send a Message**: Send text, image, document, or location messages
- **Send a Template Message**: Send pre-approved template messages (required for outbound initiation)

To set up:
1. Connect your Meta Business account in Make.com
2. Select your WhatsApp Business phone number
3. For Hebrew templates, set the template language to `he`

For advanced use cases not covered by the native module, use the HTTP module with the WhatsApp Cloud API. Use the latest API version (check Meta's changelog rather than hardcoding a version number).

**Israeli SMS Providers (via HTTP module)**

For SMS (019, InforUMobile, SMS4Free), call the provider's API from an HTTP module (endpoints and payloads in `references/make-israeli-modules.md`). Marketing SMS or email needs the recipient's prior consent under Communications Law section 30A, every message must offer a way to opt out, and compensation reaches up to 1,000 NIS per message without proof of damage. The old InforU `SendMessage.asmx` host no longer resolves, so do not use it.

### Step 3: Handle Hebrew Data

**Text Parsing and Transformation**

When processing Hebrew text in Make.com:

- Use the `toString` function to safely handle Hebrew string values from API responses
- For regex on Hebrew text, use Unicode character classes: `\p{Hebrew}` matches Hebrew letters
- When concatenating Hebrew and English (e.g., invoice references), place the Hebrew segment first to maintain RTL reading order
- Use `trim` on Hebrew text fields, as some Israeli APIs pad with invisible Unicode characters (LTR/RTL marks)

**ILS Currency Formatting**

Make.com's `formatNumber` function handles ILS:

| Expression | Output | Use Case |
|---|---|---|
| `formatNumber(amount; 2; "."; ",")` | `1,234.56` | Standard ILS display |
| `"₪" + formatNumber(amount; 2; "."; ",")` | `₪1,234.56` | With currency symbol |

Note: the Shekel sign is Unicode U+20AA. Do not use `NIS` as a symbol in customer-facing output.

**Hebrew Date Conversion**

Make.com stores dates in ISO 8601 format. For Hebrew display:

- Use `formatDate(date; "DD/MM/YYYY")` for Israeli date format (day/month/year)
- For Hebrew month names, Make has no native Hebrew month formatting. Get the numeric month with `formatDate(now; "M")` and map it with a switch function or a Set Variable lookup; the full 12-row table is in `references/make-israeli-modules.md` under "Hebrew Month Names".

### Step 4: Build Router Patterns for Israeli Billing Cycles

Israeli businesses follow specific billing cycles that differ from US/EU patterns. Use Make.com Routers to branch logic based on these cycles.

**Bimonthly VAT Reporting (Doch Du-Hodshi)**

An osek murshe files bimonthly when turnover in the determining year is up to 1,775,000 NIS (2026; 1,805,000 NIS from 1 January 2027) and monthly above it. An osek patur files only an annual turnover declaration, by 31 January. Reports are due by the 15th of the month after the period; online filers who are not detailed reporters may file and pay up to the 19th. The bimonthly periods are:

| Period | Months | Filing Deadline |
|---|---|---|
| 1 | Jan-Feb | March 15 |
| 2 | Mar-Apr | May 15 |
| 3 | May-Jun | July 15 |
| 4 | Jul-Aug | September 15 |
| 5 | Sep-Oct | November 15 |
| 6 | Nov-Dec | January 15 |

Build a Router with 6 branches, each filtering invoices for the relevant period. After the router, use an Array Aggregator to sum amounts per period for the VAT report.

Use a Make.com Data Store to track which periods have been processed and prevent duplicate runs. See Step 7 for Data Store configuration details.

**Advance Tax Payments (Mikdamot): monthly by default**

By law, self-employed advance income-tax payments (mikdamot) are MONTHLY: report the previous month's turnover (excluding VAT) and pay by the 15th. Only a low-turnover business whose advance booklet (פנקס מקדמות) approves it may report and pay every two months, on the 15th. Paid through the Tax Authority website, the deadline extends to the 19th at 18:30. Read the frequency from the booklet; do not assume bimonthly because VAT is bimonthly.

The advance rate is set per business by the assessing officer and printed in the booklet, computed on turnover rather than profit. Store it in a Data Store or Set Variable, since it can be changed on request.

**Annual Reporting**

Annual-return deadlines and their yearly extensions are published by the Tax Authority each year (accountant-represented filers usually get later dates). Read the current year's dates rather than hardcoding them.

For annual automations, schedule a scenario to run on January 1 that aggregates the previous year's data.

Consult `references/billing-cycle-patterns.md` for detailed router configurations.

### Step 5: Schedule with the Israeli Calendar

**Shabbat-Aware Scheduling**

Make.com scenarios that interact with Israeli businesses or customers should avoid running during Shabbat (Friday sunset to Saturday nightfall). The recommended approach is to use the **Hebcal community module** available on Make.com (no API key required):

1. Search for "Hebcal" in the Make.com module palette (community module at `apps.make.com/hebcal-ryuwr8`)
2. Use the Hebcal module to check if today is Shabbat or a holiday
3. Add a Filter module after Hebcal to stop execution on Shabbat/holidays

For a simpler (but less precise) approach, use scheduling settings:

1. Set the scenario schedule to run Sunday through Thursday only
2. For Friday runs, set the latest execution time to 14:00 Israel time (IST, UTC+2 / IDT, UTC+3 during DST)
3. Avoid Saturday entirely

In Make.com scheduling settings:
- Use the "Specify dates" option and exclude Saturday
- Set the ORGANIZATION time zone to `Asia/Jerusalem`: Make runs schedules in the organization time zone, not a per-scenario one

**Israeli Holiday Detection**

Use the Hebcal community module for holiday detection. It handles Rosh Hashana, Yom Kippur, Sukkot, Pesach, Shavuot, and other holidays without requiring an API key or HTTP module configuration.

If you need more control, you can use the Hebcal REST API via HTTP module:

```
https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&geo=pos&latitude=32.0853&longitude=34.7818
```

Parse the response for today's date. If a major holiday (`"category": "holiday"`) is found, use a Filter module to stop execution.

**Business Hours (Sunday-Thursday)**

Israeli business hours are typically Sunday through Thursday, 09:00-18:00. For B2B automations:
- Schedule runs between 09:00-17:00 IST
- Use Sunday as the first day of the business week

### Step 6: Handle Webhooks from Israeli Payment Gateways

**Cardcom Webhook**

Cardcom has two webhook generations with different field names, confirm which your terminal uses:
- **API v11 (current)**: posts a JSON body. Success is `ResponseCode` = 0 (with `Description`), plus `TranzactionId` and `Amount`; card-owner/token data are nested. Verify exact field names against the v11 docs (`https://secure.cardcom.solutions/Api/v11/Docs`), do not assume the legacy names below.
- **Legacy LowProfile (v10)**: older terminals use a different, non-JSON field set, listed in the reference but not re-verified this cycle.

1. Create a Custom Webhook trigger in Make.com
2. Pass the Make.com webhook URL as `WebHookUrl` in the v11 `LowProfile/Create` request (required there)
3. Map fields: both field sets are in `references/make-israeli-modules.md`. Confirm your terminal's generation first.

**Tranzila Webhook**

Tranzila uses a redirect-based flow. To capture results:

1. Create a Custom Webhook trigger
2. Set Tranzila's `notify_url` parameter
3. Key fields:

The Tranzila notify fields (`Response`, `sum`, `ccno`, `myid`, and the installment trio `fpay` / `spay` / `npay`) are tabulated in `references/make-israeli-modules.md`. The one that catches people: `npay` is the number of ADDITIONAL payments, so total installments = `npay + 1`.

**Tranzila API v2** introduces iframe-based hosted payment fields for PCI compliance and supports Bit payments.

**Grow (by Meshulam) Webhook**

Grow (formerly Meshulam; meshulam.co.il now redirects to grow.business) is operated by Grow Payments Ltd, a licensed payment company, not by a bank.

Grow has two separate mechanisms. The `notifyUrl` callback of a payment process is a form POST, "NOT as JSON", carrying `err`, `status` and `data` (`sum`, `transactionId`, `asmachta`, `paymentsNum`). Echo it back with ApproveTransaction, which only acknowledges ("does not alter the transaction status") and is skipped for token, J4/J5 delayed and save-token-only transactions; Grow resends the update up to 5 more times without it. Re-check the amount with Get Transaction Info. Grow's separate Webhooks service (enabled by Grow support) carries a `webhookKey` to check; fields are in the reference. Grow can also issue invoices itself, so never let both Grow and Morning issue a document for one sale.

**Bit** usually reaches a small business through a gateway (Grow and Tranzila both support it), so it arrives in that gateway's callback. **PayMe** and **PayBox** also send webhook notifications; configure them in their dashboards.

**For every payment webhook, before creating a document:**
- **Don't trust the payload.** A Custom Webhook URL accepts any POST. Re-query Cardcom with v11 `LowProfile/GetLpResult`, re-check Grow with Get Transaction Info, and compare the amount with the charge you expected.
- **Deduplicate.** Before Add Document, look up the gateway transaction ID in a Data Store, stop if it exists, otherwise write it as `processing`; put the ID in the document remarks and search Morning for it before any retry. Gateways retry, and instant webhooks "are processed in parallel" by default, so enable **Process data in order** in scenario settings.
- **Never Skip the invoice step.** Put a Retry error handler on it and enable **Store incomplete executions** ("disabled by default"), and alert on final failure; otherwise a captured payment ends with no invoice.
- **Keep the webhook attached.** Make deactivates a webhook not connected to any scenario for 5 days (410 Gone) and returns 429 above 300 requests per 10 seconds.
- For installments (tashlumim), store both the total and per-payment amounts.

### Step 7: Use Data Store for VAT Period Tracking

Make.com Data Store provides persistent storage for tracking billing periods across scenario runs. This prevents duplicate processing and gives you an audit trail.

**Create a Data Store** with these fields:

| Field | Type | Purpose |
|---|---|---|
| `period_type` | Text | `vat_bimonthly`, `advance_monthly`, `annual` |
| `period_key` | Text | e.g., `2026-P1`, `2026-P2`, `2026` |
| `status` | Text | `pending`, `processing`, `completed`, `filed` |
| `total_income` | Number | Aggregated income for the period |
| `total_expenses` | Number | Aggregated expenses for the period |
| `vat_total` | Number | Sum of the VAT amounts Morning returned |
| `processed_at` | Date | When the scenario last ran |
| `filed_at` | Date | When the report was filed (manual entry) |

**Usage pattern:**

1. At the start of each billing scenario, use "Search records" to check if the current period is already processed
2. If status is `completed` or `filed`, skip execution
3. If status is `pending` or missing, proceed with the scenario
4. After processing, update the record status to `completed` with the aggregated totals

This is especially important for VAT scenarios, since accidentally processing the same period twice would generate incorrect reports.

### Step 8: Make.com AI Agents

Make AI Agents add AI-powered decisions to a scenario. The current app is "Make AI Agents (New)", added through its "Run an agent (New)" module.

**Key capabilities:**

- **Module Tools:** Any Make.com module can be exposed as a tool for the AI Agent. For example, the Morning module's "Search Documents" action can be a tool the agent uses to look up invoice data before deciding what to do.
- **Multi-modal support:** AI Agents can process PDFs, images, and CSVs, useful for extracting data from Hebrew invoices or scanned documents.
- **Reasoning Panel:** Debug and inspect the AI Agent's decision-making process.

Israeli use cases: classifying Hebrew invoices from email attachments, categorizing expenses, routing Hebrew support requests, and matching payments to invoices.

To set up an AI Agent scenario:
1. Add the Make AI Agents (New) > Run an agent (New) module to your scenario
2. Configure the agent's instructions (supports Hebrew instructions)
3. Add Module Tools by selecting existing modules in your scenario
4. The agent decides which tools to call based on the input context

### Step 9: Expose Scenarios as MCP Tools (Make.com MCP Server)

Make.com runs a hosted MCP server that lets AI agents (Claude Code, Cursor, and other MCP clients) call your Make scenarios as tools, turning an Israeli automation you have already built (a Morning invoice creator, a bimonthly VAT summary) into a tool an agent can invoke directly.

Connect via OAuth (`https://mcp.make.com`, nothing to store) or an MCP token (`https://<MAKE_ZONE>/mcp/u/<MCP_TOKEN>`). The scenario-run scope is on all plans; the management scope needs a paid plan. For a scenario to appear as a tool it must be **active**, set to **on-demand** scheduling, and have defined inputs, outputs, and a detailed description (Hebrew descriptions work). Scenario-run tools time out at 25s (OAuth) or 40s (token); longer runs return an `executionId` to poll with `executions_get`.

Consult `references/make-mcp-server.md` for the connection-method details, the Claude Code config blocks, the scope table, and Israeli use cases.

### Step 10: When to Use Make.com vs Alternatives

Make for non-technical teams wanting visual debugging and Israeli community modules, n8n for self-hosting and code control, Zapier for simple 2-step automations. The plan-by-plan comparison (Free: 1,000 credits/mo, 2 active scenarios, 15-minute minimum interval; paid plans from $9/mo with 1-minute scheduling) is in `references/make-israeli-modules.md`.

## Examples

### Example 1: Sync Morning to Monday.com

User says: "Create a Make.com scenario that adds a new Monday.com item whenever a Morning tax invoice is created"

Actions:
1. Add Morning "Search Documents" action on a 15-minute schedule, filtered to type 305 (tax invoice) and recent creation date
2. Add Monday.com "Create an Item" action
3. Map fields: invoice number to Name column, client name to Client column (by column ID), amount to Amount column (number type, already in shekels), date to Date column using `formatDate`
4. Set schedule to every 15 minutes, Sunday-Thursday + Friday until 14:00, timezone `Asia/Jerusalem`

Result: New Monday.com items created automatically for each tax invoice, with Hebrew client names preserved and ILS amounts correctly formatted.

### Example 2: Bimonthly VAT Summary

User says: "Build a scenario that generates a VAT summary spreadsheet at the end of each bimonthly period"

Actions:
1. Schedule trigger for the 1st of March, May, July, September, November, January
2. Check Data Store for period status (skip if already processed)
3. Add Morning "Search Documents" to fetch all documents from the previous 2-month period
4. Add Iterator to process each document
5. Add Router with branches for income (type 305, Tax Invoice) and credit notes (type 330, Credit Note)
6. Add Array Aggregator per branch to sum amounts
7. Add Google Sheets "Add Row" to write period, income and credit subtotals, and the VAT amounts Morning returned, for the accountant
8. Update Data Store record with status `completed` and totals

Result: Automated bimonthly VAT summary that matches the Israeli tax authority reporting periods, with Data Store preventing duplicate processing.

### Example 3: WhatsApp Order Confirmation in Hebrew

User says: "Send a WhatsApp message in Hebrew when a customer places an order"

Actions:
1. Add Custom Webhook trigger to receive order events
2. Add WhatsApp Business Cloud "Send a Template Message" action (native module)
3. Select a pre-approved Hebrew message template with variables: customer name, order number, total in ILS
4. Format amount with `"₪" + formatNumber(amount; 2; "."; ",")`
5. Use Hebcal community module + Filter to queue messages during Shabbat for delivery on Sunday morning

Result: Customers receive Hebrew WhatsApp confirmations with properly formatted ILS amounts, respecting Shabbat hours.

### Example 4: AI Agent for Invoice Processing

User says: "Set up an AI agent that reads email attachments and creates the right type of document in Morning"

Actions:
1. Add Gmail "Watch Emails" trigger filtered to emails with attachments
2. Add Make.com AI Agent module with Hebrew instructions: classify the attachment as invoice, receipt, quote, or credit note
3. Add Morning "Add Document" as a Module Tool, with type parameter mapped from the agent's classification (305 = Tax Invoice, 320 = Tax Invoice/Receipt, 400 = Receipt, 10 = Price Quote)
4. Add Morning "Search Clients" as a Module Tool so the agent can look up existing clients
5. Add an error handler route for unclassifiable documents

Result: AI-powered document processing that automatically classifies Hebrew invoices and creates the correct document type in Morning.


## Bundled Resources

### References
- `references/make-israeli-modules.md` - Complete reference of Israeli service modules and HTTP configurations for Make.com, including Morning (formerly Green Invoice), iCount, Monday.com, Priority ERP, WhatsApp Cloud API, Israeli SMS providers, and payment gateways. Consult when setting up a new Israeli app connection or troubleshooting API authentication.
- `references/billing-cycle-patterns.md` - Detailed Israeli billing cycle automation patterns including bimonthly VAT, monthly advance payments, annual reporting, and payroll schedules. Includes Make.com Data Store configurations and router patterns. Consult when building time-based automations tied to Israeli tax or billing deadlines.
- `references/make-mcp-server.md` - Make.com MCP server reference: OAuth and MCP-token connection methods, Claude Code config blocks, scopes, the active + on-demand requirement for exposing a scenario as a tool, timeout behavior, and Israeli use cases. Consult when wiring a Make scenario into an AI agent as an MCP tool.

## Gotchas

- Agents get the frequencies backwards. VAT is bimonthly up to the turnover threshold (monthly above it), while mikdamot are MONTHLY unless the advance booklet approves bimonthly. Confirm each frequency separately before building period filters.
- Morning (Green Invoice) amounts in the API are in **decimal shekels** (e.g., `price: 50` means 50 shekels). Do NOT multiply by 100 or convert to agorot. This is different from some payment gateway APIs.
- The Morning Make.com module is **community-built by Callbox**, not maintained by Make.com. It has no trigger/watch modules, only actions. For event-driven flows use Morning's `document/created` webhook into a Custom Webhook; otherwise poll.
- Morning document type codes: 10 = Price Quote, 305 = Tax Invoice, 320 = Tax Invoice/Receipt, 330 = Credit Invoice, 400 = Receipt. 300 is a transaction account, NOT a tax invoice.
- Tranzila's `npay` field means the number of **additional** payments, not total payments. Always use `npay = total_installments - 1`.
- Make.com's date functions use US-style day-of-week numbering (0 = Sunday). Agents often assume Monday = 0 (ISO 8601). Sunday is 0, Saturday is 6 in Make.com.
- Agents tend to schedule Friday runs at 17:00 or later. Shabbat can start as early as 16:00 in winter. Use 14:00 as the safe Friday cutoff, or better, use the Hebcal community module for precise times.
- Hebrew column names in Monday.com should be referenced by column ID, not by the display title. Agents often try to use the Hebrew title directly, which breaks when users rename columns.
- Make.com filters use a **visual UI** with dropdown operators, not code syntax. There is no `=` vs `==` distinction since you select "equal to" from a dropdown.
- The Israeli tax year is January-December (same as calendar year), but agents sometimes assume April-March (UK pattern) or October-September (US fiscal year).
- **Invoice Reform 2026 affects automation, and the comparison is made BEFORE VAT.** Tax invoices over 5,000 NIS (from 1 June 2026; 10,000 NIS before that) need a Tax Authority allocation number, measured on the amount before VAT. Filtering on the gross total over-requests on every invoice between roughly 4,238 and 5,000 NIS net. The number is a condition of the recipient's input-VAT deduction, not of the invoice's validity.
- monday.com has no v1/v2 API split. `api.monday.com/v2` is the GraphQL endpoint path; the API version is date-based (`2026-10` current since October 1st, 2026, rolling quarterly) and set per request with an `API-Version` header. Pin one explicitly rather than inheriting whatever the default becomes.
- A Make scenario only appears as an MCP tool when it is both **active** AND set to **on-demand** scheduling. Agents often satisfy only one condition; a scheduled or instant-trigger scenario will never show up in the MCP tool list.
- MCP scenario-run tools time out at 25s (OAuth) or 40s (token). A longer scenario returns an `executionId` instead of the result, poll with `executions_get` using that ID rather than treating the timeout as a failure.

## Troubleshooting

### Error: "Morning API returns 401 Unauthorized"
Cause: wrong client ID or secret, keys from the other environment ("Each environment requires its own set of API keys"), or an access token past its 1-hour validity.
Solution: Morning authenticates with OAuth 2.0 client credentials. In an HTTP module, POST `grant_type`, `client_id` and `client_secret` as JSON to `https://api.morning.co/idp/v1/oauth/token`, then send `Authorization: Bearer <accessToken>` to `https://api.greeninvoice.co.il/api/v1`. Take sandbox URLs from the docs' Sandbox tab, and re-check any older integration that still calls `/account/token`.

### Error: "Hebrew text appears garbled in output"
Cause: Encoding mismatch. Some Israeli APIs return Windows-1255 or ISO-8859-8 instead of UTF-8.
Solution: Check the API response headers for `charset`. If not UTF-8, add a Text Parser module after the HTTP module and set input encoding to match the source. Morning (Green Invoice) and Monday.com use UTF-8 natively.

### Error: "Make.com scenario runs on Saturday"
Cause: The organization time zone is not Asia/Jerusalem, causing the schedule to misalign with Israeli time.
Solution: Set the organization time zone (not a scenario setting) to `Asia/Jerusalem`. Use the Hebcal community module for reliable Shabbat detection rather than manual day-of-week checks.

### Error: "Cardcom webhook not triggering"
Cause: Make.com custom webhook must be "listening" (turned on) before Cardcom sends the notification. Also, Cardcom requires HTTPS.
Solution: Ensure the scenario is active and the webhook is in listening mode. Copy the webhook URL after activating it. Verify the URL starts with `https://`. Test with a small transaction first.

### Error: "Morning module not available in Make.com"
Cause: The Callbox app page requires "a Best or higher subscription and an API Key" on the Morning side. Best is Morning's plan, not Make's, and Morning's Basic plan does not include API access.
Solution: Upgrade the Morning account to Best or higher and generate an API key. Alternatively use **iCount, which has a native first-party Make module** (it requires a paid iCount account).

### Problem: a qualifying invoice was issued without an allocation number
Cause: Tax invoices to an osek murshe above 5,000 NIS before VAT (from 1 June 2026; 10,000 NIS before that) need a Tax Authority allocation number, and the buyer cannot deduct input VAT without it.
Solution: Check the created document's `allocationNumber` in the post-create If-else, alert the business when it is empty, and resolve it in Morning before the buyer files.

### Error: "Make scenario does not appear as an MCP tool"
Cause: The scenario is not active, is not set to on-demand scheduling, or the MCP connection is missing the scenario-run scope.
Solution: Set the scenario to active status AND on-demand scheduling, both are required. Confirm the MCP connection has the "Run your scenarios" scope (OAuth) or the `mcp:use` scope (token). If the tool list is stale, reconnect the MCP client to refresh it.
