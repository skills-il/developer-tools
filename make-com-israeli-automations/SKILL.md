---
name: make-com-israeli-automations
description: Build and configure Make.com scenarios for Israeli business processes, including Morning (formerly Green Invoice) sync, iCount accounting, Monday.com board automation, Priority ERP data exports, WhatsApp Business Hebrew messaging, and payment gateways (Cardcom, Tranzila, Grow, Bit). Covers Make.com AI Agents, the Make.com MCP server for exposing scenarios as agent tools, Israel 2026 Invoice Reform (allocation numbers with a step-down threshold), community modules for Israeli apps, Hebrew data transformations, Data Store for VAT period tracking, and Shabbat-aware scheduling via the Hebcal community module. Use when user asks to "create a Make.com scenario", "build an automation for Israeli billing", "automate Morning / Green Invoice", "connect Israeli apps in Make.com", "set up AI agent in Make.com", or "expose a Make.com scenario as an MCP tool". Do NOT use for n8n workflows (use n8n-hebrew-workflows), Zapier Zaps (use zapier-israeli-integrations), or custom code automation without Make.com.
license: MIT
allowed-tools: Bash(curl:*) Bash(node:*) Bash(python:*)
compatibility: Requires Make.com account (Free plan has 1,000 credits/month). Morning community module requires Best plan or higher. iCount has a native module. Priority ERP community module or HTTP module. WhatsApp Cloud API requires Meta Business verification.
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
- **Processing a list?** Use an Iterator to loop over items (e.g., line items on an invoice).
- **Aggregating data?** Use an Array Aggregator before the final output.
- **AI decision needed?** Use Make.com AI Agents with Module Tools (see Step 8).

### Step 2: Configure Israeli App Connections

**Morning (formerly Green Invoice / Hashbonit Yeruqa)**

Morning has a **community-built** Make.com module, created by Callbox and listed as "Morning by Callbox" on the Make.com marketplace. Make.com states: "Make does not maintain or support this integration." The module requires a **Best subscription tier or higher**.

To set up the connection:

1. In Make.com, search for "Morning" in the module palette (NOT "Green Invoice")
2. Create a connection using your Morning API key and secret (from Morning dashboard: Settings > API Integration)
3. The API domain remains `api.greeninvoice.co.il` despite the rebrand

Available actions (there are NO watch/trigger modules):

| Action | Description | Key Parameters |
|---|---|---|
| Add Client | Create a new client record | `name`, `emails`, `taxId`, `address` |
| Add Document | Create invoice, receipt, quote | `type`, `client`, `income`, `currency`, `lang` |
| Add Expense | Record an expense | `supplier`, `amount`, `date`, `category` |
| Get All Clients | List all client records | Pagination params |
| Get All Documents | List all documents | Pagination params |
| Search Clients | Query clients by criteria | Name, tax ID, etc. |
| Search Documents | Query documents by criteria | `type`, `fromDate`, `toDate`, `status` |
| Search Expenses | Query expenses by criteria | Date range, category, etc. |
| Update Client | Modify existing client | Client ID + fields to update |
| Delete Client | Remove a client record | Client ID |
| Make an API Call | Raw API request | Any Morning API endpoint |

Since there are no triggers, use one of these patterns for event-driven scenarios:
- **Scheduled polling:** Use "Search Documents" on a schedule (e.g., every 15 minutes) filtered to recent documents
- **External webhook:** Have another system (e.g., your app) call a Make.com Custom Webhook when a document is created

Key field mappings for Morning documents:

| Morning Field | Make.com Field | Notes |
|---|---|---|
| `type` | Document type | 10 = Price Quote, 305 = Tax Invoice, 320 = Tax Invoice/Receipt, 330 = Credit Note/Refund, 400 = Receipt |
| `client.name` | Client name | Hebrew characters supported |
| `currency` | Currency code | Use `ILS` for Israeli Shekel |
| `income[].price` | Unit price (ILS) | **Decimal shekels** (e.g., `price: 50` means 50 shekels). NOT agorot. |
| `vatType` | VAT handling | 0 = Exempt, 1 = Included, 2 = Excluded |
| `lang` | Document language | `he` for Hebrew, `en` for English |

**Israel Invoice Reform 2026 (threshold step-down):** Tax invoices over the threshold require a Tax Authority allocation number (mispar haktza'a). The threshold drops in 2026:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |
| Jan 1, 2027 | 5,000 NIS (planned to continue) |

Morning's API supports the allocation number via the `allocationNumber` field. For invoices above the current threshold, your scenario must either:
1. Request an allocation number from the Tax Authority API before creating the document
2. Use Morning's built-in allocation flow (if enabled in your Morning account settings)

Build the threshold check as a configurable variable in your workflow, not a hardcoded number, since the threshold is scheduled to drop again. Failure to include an allocation number on qualifying invoices renders them invalid.

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

**Important (v2 migration):** Monday.com API v1 is maintained only until May 1, 2026. All new scenarios MUST use API v2. If connecting an existing scenario that uses v1, plan migration immediately. The Make.com native module uses v2 by default as of 2025.

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

Common Priority entities for Israeli scenarios:

| Entity | OData Path | Use Case |
|---|---|---|
| `ORDERS` | `/ORDERS` | Sales orders |
| `AINVOICES` | `/AINVOICES` | A/R invoices |
| `PORDERS` | `/PORDERS` | Purchase orders |
| `LOGCOUNTERS` | `/LOGCOUNTERS` | Inventory counts |

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

For SMS automation (019, InforUMobile, SMS4Free):

| Provider | API Endpoint | Auth Method |
|---|---|---|
| 019 SMS | `https://019sms.co.il/api` | Bearer token: `Authorization: Bearer YOUR_TOKEN` |
| InforUMobile | `http://api.inforu.co.il/SendMessage.asmx` | Username + token (ASMX web service, XML format) |
| SMS4Free | `https://www.sms4free.co.il/ApiSMS/SendSMS` | Three credentials: `key`, `user`, `pass` |

Consult `references/make-israeli-modules.md` for full endpoint specs, authentication details, and payload examples.

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
- For Hebrew month names, use a lookup table (Make.com does not have native Hebrew month formatting):

| Month | Hebrew |
|---|---|
| 1 | ינואר |
| 2 | פברואר |
| 3 | מרץ |
| 4 | אפריל |
| 5 | מאי |
| 6 | יוני |
| 7 | יולי |
| 8 | אוגוסט |
| 9 | ספטמבר |
| 10 | אוקטובר |
| 11 | נובמבר |
| 12 | דצמבר |

Use `formatDate(now; "M")` to get the numeric month, then map it to the Hebrew name using a switch function or lookup table in a Set Variable module.

### Step 4: Build Router Patterns for Israeli Billing Cycles

Israeli businesses follow specific billing cycles that differ from US/EU patterns. Use Make.com Routers to branch logic based on these cycles.

**Bimonthly VAT Reporting (Doch Du-Hodshi)**

VAT reports are filed bimonthly for most businesses (businesses under the threshold file annually). The VAT periods are:

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

**Bimonthly Advance Tax Payments (Mikdamot)**

Self-employed and some companies pay bimonthly advance tax (mikdamot), aligned with the same bimonthly VAT reporting periods. The advance payment is due by the 15th-19th of the month following each period:

| Period | Months | Payment Due |
|---|---|---|
| 1 | Jan-Feb | March 15-19 |
| 2 | Mar-Apr | May 15-19 |
| 3 | May-Jun | July 15-19 |
| 4 | Jul-Aug | September 15-19 |
| 5 | Sep-Oct | November 15-19 |
| 6 | Nov-Dec | January 15-19 |

The advance payment is typically a percentage of revenue set by the Tax Authority (commonly 5-15% for new businesses). Store the advance rate in a Make.com Data Store or Set Variable module, since it varies per business and is updated annually.

**Annual Reporting**

Annual tax return deadlines vary by filing method:
- Online filing: April 30
- Accountant filing: extended to May 31 or later (varies by year)

For annual automations, schedule a scenario to run on January 1 that aggregates the previous year's data.

Consult `references/billing-cycle-patterns.md` for detailed router configurations.

### Step 5: Schedule with the Israeli Calendar

**Shabbat-Aware Scheduling**

Make.com scenarios that interact with Israeli businesses or customers should avoid running during Shabbat (Friday sunset to Saturday sunset). The recommended approach is to use the **Hebcal community module** available on Make.com (no API key required):

1. Search for "Hebcal" in the Make.com module palette (community module at `apps.make.com/hebcal-ryuwr8`)
2. Use the Hebcal module to check if today is Shabbat or a holiday
3. Add a Filter module after Hebcal to stop execution on Shabbat/holidays

For a simpler (but less precise) approach, use scheduling settings:

1. Set the scenario schedule to run Sunday through Thursday only
2. For Friday runs, set the latest execution time to 14:00 Israel time (IST, UTC+2 / IDT, UTC+3 during DST)
3. Avoid Saturday entirely

In Make.com scheduling settings:
- Use the "Specify dates" option and exclude Saturday
- Set timezone to `Asia/Jerusalem`

Note: A 14:00 Friday cutoff is a safe conservative default. For precise candle-lighting times, the Hebcal community module is the better choice since it accounts for seasonal variation and specific location.

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
- Friday is a half-day (until ~13:00)

### Step 6: Handle Webhooks from Israeli Payment Gateways

**Cardcom Webhook**

Cardcom sends POST requests to your webhook URL after payment events:

1. Create a Custom Webhook trigger in Make.com
2. Set Cardcom's "Notify URL" to the Make.com webhook URL (Cardcom API v11 supports modern webhook configuration)
3. Key fields in the Cardcom callback:

| Field | Description | Example |
|---|---|---|
| `OperationResponse` | Success/failure code | `0` = success |
| `Amount` | Charge amount in ILS | `150.00` |
| `CardOwnerID` | Teudat Zehut of card owner | 9-digit Israeli ID |
| `NumOfPayments` | Installment count (tashlumim) | `3` |
| `Token` | Card token for recurring charges | |

**Tranzila Webhook**

Tranzila uses a redirect-based flow. To capture results:

1. Create a Custom Webhook trigger
2. Set Tranzila's `notify_url` parameter
3. Key fields:

| Field | Description |
|---|---|
| `Response` | `000` = approved |
| `sum` | Amount in ILS |
| `ccno` | Masked card number |
| `myid` | Customer ID (Teudat Zehut) |
| `fpay` | First payment amount (tashlumim) |
| `spay` | Subsequent payment amount |
| `npay` | Number of **additional** payments (total installments = npay + 1). If npay=2, customer pays 3 installments total. |

**Tranzila API v2** introduces iframe-based hosted payment fields for PCI compliance and supports Bit payments.

**Grow (by Meshulam) Webhook**

Grow is an independent fintech company by Meshulam (NOT affiliated with Bank Leumi).

Grow sends webhook notifications as JSON POST. To verify authenticity, check the `webhookKey` field in the JSON payload body (not a header signature). Grow's API uses **multipart/form-data** for outbound requests, not JSON.

1. Register your Make.com webhook URL in the Grow dashboard
2. Grow sends JSON POST with event type and payment details
3. Verify the webhook by comparing the `webhookKey` value in the JSON body against your configured key

**Bit (by Bank HaPoalim)**

Bit is Israel's dominant P2P payment platform and has a business API. For Bit Business webhooks:

1. Register for Bit Business API access
2. Configure webhook URL in the Bit Business dashboard
3. Bit sends payment notifications for completed transactions

**Additional Gateways**

- **PayMe (by Isracard):** Payment processing with installment support. Configure webhook URL in PayMe dashboard.
- **PayBox:** Digital payment solution with webhook notifications.

For all payment gateways, always validate:
- The response/status code indicates success before processing
- The amount matches the expected charge
- For installments (tashlumim), store both the total and per-payment amounts

### Step 7: Use Data Store for VAT Period Tracking

Make.com Data Store provides persistent storage for tracking billing periods across scenario runs. This prevents duplicate processing and gives you an audit trail.

**Create a Data Store** with these fields:

| Field | Type | Purpose |
|---|---|---|
| `period_type` | Text | `vat_bimonthly`, `advance_bimonthly`, `annual` |
| `period_key` | Text | e.g., `2026-P1`, `2026-P2`, `2026` |
| `status` | Text | `pending`, `processing`, `completed`, `filed` |
| `total_income` | Number | Aggregated income for the period |
| `total_expenses` | Number | Aggregated expenses for the period |
| `vat_payable` | Number | Calculated VAT due |
| `processed_at` | Date | When the scenario last ran |
| `filed_at` | Date | When the report was filed (manual entry) |

**Usage pattern:**

1. At the start of each billing scenario, use "Search records" to check if the current period is already processed
2. If status is `completed` or `filed`, skip execution
3. If status is `pending` or missing, proceed with the scenario
4. After processing, update the record status to `completed` with the aggregated totals

This is especially important for VAT scenarios, since accidentally processing the same period twice would generate incorrect reports.

### Step 8: Make.com AI Agents

Make.com launched AI Agents in April 2025, with Visual AI Agents in the Scenario Builder released in 2026. This enables AI-powered decision making within your Israeli business automations.

**Key capabilities:**

- **Module Tools:** Any Make.com module can be exposed as a tool for the AI Agent. For example, the Morning module's "Search Documents" action can be a tool the agent uses to look up invoice data before deciding what to do.
- **Multi-modal support:** AI Agents can process PDFs, images, and CSVs, useful for extracting data from Hebrew invoices or scanned documents.
- **Reasoning Panel:** Debug and inspect the AI Agent's decision-making process.

**Israeli business use cases for AI Agents:**

| Use Case | AI Agent Role | Module Tools |
|---|---|---|
| Invoice classification | Determine document type from email attachments | Morning (Add Document), Gmail (Watch) |
| Smart expense categorization | Categorize Hebrew expense descriptions | Morning (Add Expense), Google Sheets |
| Customer routing | Route Hebrew support requests to correct department | Monday.com (Create Item), WhatsApp (Send Message) |
| Payment reconciliation | Match payments to invoices across gateways | Cardcom webhook, Morning (Search Documents) |

To set up an AI Agent scenario:
1. Add an AI Agent module to your scenario
2. Configure the agent's instructions (supports Hebrew instructions)
3. Add Module Tools by selecting existing modules in your scenario
4. The agent decides which tools to call based on the input context

### Step 9: Expose Scenarios as MCP Tools (Make.com MCP Server)

Make.com runs a hosted MCP server that lets AI agents (Claude Code, Cursor, and other MCP clients) call your Make scenarios as tools, turning an Israeli automation you have already built (a Morning invoice creator, a bimonthly VAT summary) into a tool an agent can invoke directly.

Connect via OAuth (`https://mcp.make.com`, nothing to store) or an MCP token (`https://<MAKE_ZONE>/mcp/u/<MCP_TOKEN>`). The scenario-run scope is on all plans; the management scope needs a paid plan. For a scenario to appear as a tool it must be **active**, set to **on-demand** scheduling, and have defined inputs, outputs, and a detailed description (Hebrew descriptions work). Scenario-run tools time out at 25s (OAuth) or 40s (token); longer runs return an `executionId` to poll with `executions_get`.

Consult `references/make-mcp-server.md` for the connection-method details, the Claude Code config blocks, the scope table, and Israeli use cases.

### Step 10: When to Use Make.com vs Alternatives

| Criteria | Make.com | n8n | Zapier |
|---|---|---|---|
| **Best for** | Visual automations, non-developers | Self-hosted, code-heavy workflows | Simple 2-app connections |
| **Israeli app modules** | Morning (community), iCount (native), Priority (community), Hebcal (community) | Fewer Israeli modules | Some Israeli apps |
| **AI Agents** | Built-in visual AI Agents | Via code nodes | Limited AI features |
| **Pricing** | Core: $10.59/mo (annual), 5-min minimum schedule | Free (self-hosted) | Starter: $29.99/mo |
| **1-minute scheduling** | Pro plan only | Available on all plans | Available on paid plans |
| **Hebrew UI** | No (English UI, Hebrew data supported) | No | No |
| **Community modules** | Growing Israeli ecosystem | npm packages | Fewer community options |

Choose Make.com when: the team is non-technical, you need visual debugging, and you want community modules for Israeli services. Choose n8n when: you need self-hosting, full code control, or cost-free operation. Choose Zapier when: you only need simple 2-step automations between mainstream apps.

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
7. Add Google Sheets "Add Row" to write period, total income, total credits, and VAT difference
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

For a worked example of exposing a Morning invoice scenario as an MCP tool callable from Claude Code, see `references/make-mcp-server.md`.

## Bundled Resources

### References
- `references/make-israeli-modules.md` - Complete reference of Israeli service modules and HTTP configurations for Make.com, including Morning (formerly Green Invoice), iCount, Monday.com, Priority ERP, WhatsApp Cloud API, Israeli SMS providers, and payment gateways. Consult when setting up a new Israeli app connection or troubleshooting API authentication.
- `references/billing-cycle-patterns.md` - Detailed Israeli billing cycle automation patterns including bimonthly VAT, bimonthly advance payments, annual reporting, and payroll schedules. Includes Make.com Data Store configurations and router patterns. Consult when building time-based automations tied to Israeli tax or billing deadlines.
- `references/make-mcp-server.md` - Make.com MCP server reference: OAuth and MCP-token connection methods, Claude Code config blocks, scopes, the active + on-demand requirement for exposing a scenario as a tool, timeout behavior, and Israeli use cases. Consult when wiring a Make scenario into an AI agent as an MCP tool.

## Gotchas

- Agents default to monthly VAT reporting (US/EU pattern). Israeli VAT reporting is bimonthly for most businesses. Always confirm the reporting frequency before building period filters.
- Morning (Green Invoice) amounts in the API are in **decimal shekels** (e.g., `price: 50` means 50 shekels). Do NOT multiply by 100 or convert to agorot. This is different from some payment gateway APIs.
- The Morning Make.com module is **community-built by Callbox**, not maintained by Make.com. It has no trigger/watch modules, only actions. Plan for scheduled polling instead of event-driven triggers.
- Morning document type codes: 10 = Price Quote, 305 = Tax Invoice, 320 = Tax Invoice/Receipt, 330 = Credit Note/Refund, 400 = Receipt. These are NOT the same as the HTTP status-code-like numbers agents sometimes assume.
- Tranzila's `npay` field means the number of **additional** payments, not total payments. If you set `npay=3`, the customer pays 4 installments total (1 first payment + 3 additional). Always use `npay = total_installments - 1`.
- Make.com's date functions use US-style day-of-week numbering (0 = Sunday). Agents often assume Monday = 0 (ISO 8601). Sunday is 0, Saturday is 6 in Make.com.
- Agents tend to schedule Friday runs at 17:00 or later. Shabbat can start as early as 16:00 in winter. Use 14:00 as the safe Friday cutoff, or better, use the Hebcal community module for precise times.
- Hebrew column names in Monday.com should be referenced by column ID, not by the display title. Agents often try to use the Hebrew title directly, which breaks when users rename columns.
- Make.com filters use a **visual UI** with dropdown operators, not code syntax. There is no `=` vs `==` distinction since you select "equal to" from a dropdown.
- The Israeli tax year is January-December (same as calendar year), but agents sometimes assume April-March (UK pattern) or October-September (US fiscal year).
- **Invoice Reform 2026 affects automation, threshold drops June 1, 2026.** Tax invoices over the threshold (10,000 NIS through May 31, 2026, then 5,000 NIS from June 1, 2026) require Tax Authority allocation numbers. Scenarios that create invoices must check the amount and include the allocation number for qualifying documents. Make the threshold a scenario variable, not a hardcoded literal.
- Monday.com API v1 is maintained only until May 1, 2026. New scenarios must use v2. The Make.com native module defaults to v2.
- A Make scenario only appears as an MCP tool when it is both **active** AND set to **on-demand** scheduling. Agents often satisfy only one condition. A scheduled or instant-trigger scenario will never show up in the MCP tool list, no matter how the inputs and outputs are configured.
- MCP scenario-run tools time out at 25s (OAuth) or 40s (token). A bimonthly VAT aggregation scenario can run longer, in which case the call returns an `executionId` instead of the result. Poll with `executions_get` using that ID. Do not treat the timeout as a failure.

## Troubleshooting

### Error: "Morning API returns 401 Unauthorized"
Cause: API key/secret mismatch, or using sandbox credentials in production (or vice versa)
Solution: Verify you are using the correct environment. Morning sandbox URL is `https://sandbox.d.greeninvoice.co.il/api/v1/`, production is `https://api.greeninvoice.co.il/api/v1/`. Regenerate the API key if needed. Note: the API domain still uses `greeninvoice.co.il` despite the Morning rebrand.

### Error: "Hebrew text appears garbled in output"
Cause: Encoding mismatch. Some Israeli APIs return Windows-1255 or ISO-8859-8 instead of UTF-8.
Solution: Check the API response headers for `charset`. If not UTF-8, add a Text Parser module after the HTTP module and set input encoding to match the source. Morning (Green Invoice) and Monday.com use UTF-8 natively.

### Error: "Make.com scenario runs on Saturday"
Cause: Timezone set to UTC instead of Asia/Jerusalem, causing the schedule to misalign with Israeli time.
Solution: In scenario settings, set timezone to `Asia/Jerusalem`. Use the Hebcal community module for reliable Shabbat detection rather than manual day-of-week checks.

### Error: "Cardcom webhook not triggering"
Cause: Make.com custom webhook must be "listening" (turned on) before Cardcom sends the notification. Also, Cardcom requires HTTPS.
Solution: Ensure the scenario is active and the webhook is in listening mode. Copy the webhook URL after activating it. Verify the URL starts with `https://`. Test with a small transaction first.

### Error: "Morning module not available in Make.com"
Cause: The Morning module requires the Best subscription tier or higher. It is a community module, not included in Free or Core plans.
Solution: Upgrade your Make.com plan to Best or higher. Alternatively, use the "Make an API Call" action from the Morning module, or use a generic HTTP module with the Morning REST API directly.

### Error: "Invoice rejected: missing allocation number"
Cause: Invoices over the Invoice Reform threshold require a Tax Authority allocation number. The threshold is 10,000 NIS through May 31, 2026, then drops to 5,000 NIS on June 1, 2026.
Solution: Add a Filter module before document creation that compares the amount against a workflow variable holding the current threshold (do not hardcode the number, it is scheduled to drop again). If the amount exceeds the threshold, request an allocation number first, then pass it in the `allocationNumber` field when creating the document.

### Error: "Make scenario does not appear as an MCP tool"
Cause: The scenario is not active, is not set to on-demand scheduling, or the MCP connection is missing the scenario-run scope.
Solution: Set the scenario to active status AND on-demand scheduling, both are required. Confirm the MCP connection has the "Run your scenarios" scope (OAuth) or the `mcp:use` scope (token). If the tool list is stale, reconnect the MCP client to refresh it.
