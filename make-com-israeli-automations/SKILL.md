---
name: make-com-israeli-automations
description: >-
  Build and configure Make.com (formerly Integromat) scenarios for Israeli business
  processes, including Green Invoice sync, Monday.com board automation, Priority ERP
  data exports, and WhatsApp Business Hebrew messaging. Use when user asks to "create
  a Make.com scenario", "build an automation for Israeli billing", "automate Green
  Invoice", "otomatzia shel Make", "tizmun scenario", or "connect Israeli apps in
  Make.com". Covers Israeli app module configuration, Hebrew data transformations,
  ILS currency handling, router patterns for bimonthly VAT and quarterly advance
  payments, Shabbat-aware scheduling, and webhook receivers for Israeli payment
  gateways (Cardcom, Tranzila, Grow). Do NOT use for n8n workflows (use
  n8n-hebrew-workflows), Zapier Zaps (use zapier-israeli-integrations), or custom
  code automation without Make.com.
license: MIT
allowed-tools: 'Bash(curl:*) Bash(node:*) Bash(python:*)'
compatibility: >-
  Requires Make.com account (free tier available). Some modules require paid plans.
  Green Invoice API requires a developer account. Priority ERP requires on-prem or
  cloud API access. WhatsApp Cloud API requires Meta Business verification.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - Make.com
      - Integromat
      - אוטומציה
      - תהליכי-עבודה
      - ישראל
      - חשבונית-ירוקה
    en:
      - make-com
      - integromat
      - automation
      - workflows
      - israel
      - green-invoice
  display_name:
    he: אוטומציות Make.com לישראל
    en: Make.com Israeli Automations
  display_description:
    he: >-
      בנייה והגדרה של תרחישי Make.com לתהליכים עסקיים ישראליים, כולל סנכרון
      חשבונית ירוקה, אוטומציה של Monday.com, ייצוא נתוני Priority ERP, והודעות
      WhatsApp Business בעברית. מכסה מודולים ישראליים, טיפול בנתונים בעברית,
      תזמון מודע שבת, ו-webhook לשערי תשלום ישראליים.
    en: >-
      Build and configure Make.com scenarios for Israeli business processes,
      including Green Invoice sync, Monday.com board automation, Priority ERP
      data exports, and WhatsApp Business Hebrew messaging. Covers Israeli app
      modules, Hebrew data transformations, ILS currency handling, Shabbat-aware
      scheduling, and webhook receivers for Israeli payment gateways.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Make.com Israeli Automations

## Instructions

### Step 1: Identify the Scenario Pattern

Before building any scenario, map the business workflow to a Make.com pattern. Israeli business automations fall into predictable categories:

| Business Workflow | Make.com Pattern | Core Modules | Trigger Type |
|---|---|---|---|
| Invoice creation and sync | Watch + Create | Green Invoice, Monday.com | Webhook / Scheduled |
| Billing cycle reporting | Router + Aggregator | Green Invoice, Google Sheets, HTTP | Scheduled (monthly/bimonthly) |
| Customer messaging | Watch + Iterator + HTTP | WhatsApp Cloud API, Monday.com | Webhook |
| ERP data export | HTTP + JSON Parse + Router | Priority ERP (HTTP), Google Sheets | Scheduled |
| Payment notification | Webhook + Router + Create | Cardcom/Tranzila webhook, Slack/Email | Instant (webhook) |
| Document generation | Watch + Template + Email | Green Invoice, Google Docs, Gmail | Event-driven |

Choose the pattern based on these criteria:
- **Real-time needed?** Use webhooks (instant triggers). Otherwise, use scheduled polling.
- **Multiple destinations?** Use a Router module to branch the flow.
- **Processing a list?** Use an Iterator to loop over items (e.g., line items on an invoice).
- **Aggregating data?** Use an Array Aggregator before the final output.

### Step 2: Configure Israeli App Connections

**Green Invoice (Hashbonit Yeruqa)**

Green Invoice provides a native Make.com module. To set up the connection:

1. In Make.com, search for "Green Invoice" in the module palette
2. Create a connection using your Green Invoice API key and secret
3. Available triggers: New Document, Updated Document, New Payment
4. Available actions: Create Document, Create Client, Get Document

Key field mappings for Green Invoice documents:

| Green Invoice Field | Make.com Field | Notes |
|---|---|---|
| `type` | Document type | 320 = Tax Invoice, 330 = Receipt, 400 = Quote |
| `client.name` | Client name | Hebrew characters supported |
| `currency` | Currency code | Use `ILS` for Israeli Shekel |
| `amount` | Total (ILS) | In agorot (multiply by 100 for API, divide by 100 for display) |
| `vatType` | VAT handling | 0 = Exempt, 1 = Included, 2 = Excluded |
| `lang` | Document language | `he` for Hebrew, `en` for English |

**Monday.com**

Monday.com has a native Make.com module. Israeli businesses commonly use it for project billing:

1. Use "Watch Items" as trigger (set to a specific board)
2. Map column values using the column ID (not the title, since titles may be in Hebrew)
3. For status columns, use the label index (not the Hebrew label text) for reliable matching

**Priority ERP (via HTTP module)**

Priority does not have a native Make.com module. Use HTTP modules:

1. Add an HTTP "Make a request" module
2. URL pattern: `https://{your-priority-domain}/odata/Priority/tabula.ini/{company}/{entity}`
3. Authentication: Basic Auth with Priority credentials
4. Set header `Content-Type: application/json`
5. For Hebrew field values, ensure the request body is UTF-8 encoded

Common Priority entities for Israeli scenarios:

| Entity | OData Path | Use Case |
|---|---|---|
| `ORDERS` | `/ORDERS` | Sales orders |
| `AINVOICES` | `/AINVOICES` | A/R invoices |
| `PORDERS` | `/PORDERS` | Purchase orders |
| `LOGCOUNTERS` | `/LOGCOUNTERS` | Inventory counts |

**WhatsApp Business (via HTTP module)**

Use the WhatsApp Cloud API through Make.com's HTTP module:

1. Base URL: `https://graph.facebook.com/v21.0/{phone-number-id}/messages`
2. Auth: Bearer token (use your Meta Business permanent token)
3. For Hebrew message templates, set the template language to `he`
4. Body encoding: JSON with UTF-8 for Hebrew text

**Israeli SMS Providers (via HTTP module)**

For SMS automation (019, InforUMobile, SMS4Free):

| Provider | API Endpoint | Auth Method |
|---|---|---|
| 019 SMS | `https://019sms.co.il/api` | API key in header |
| InforUMobile | `https://api.inforu.co.il/SendMessageXml.ashx` | Username + token |
| SMS4Free | `https://www.sms4free.co.il/ApiSMS/SendSMS` | Key + secret |

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
| `formatNumber(amount / 100; 2; "."; ",")` | `12.35` | Converting agorot to shekels |
| `"₪" + formatNumber(amount; 2; "."; ",")` | `₪1,234.56` | With currency symbol |

Note: the Shekel sign (₪) is Unicode U+20AA. Do not use `NIS` as a symbol in customer-facing output.

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

| Period | Months | Filing Deadline | Filter Expression |
|---|---|---|---|
| 1 | Jan-Feb | March 15 | `formatDate(now; "M") = 1 OR formatDate(now; "M") = 2` |
| 2 | Mar-Apr | May 15 | `formatDate(now; "M") = 3 OR formatDate(now; "M") = 4` |
| 3 | May-Jun | July 15 | `formatDate(now; "M") = 5 OR formatDate(now; "M") = 6` |
| 4 | Jul-Aug | September 15 | `formatDate(now; "M") = 7 OR formatDate(now; "M") = 8` |
| 5 | Sep-Oct | November 15 | `formatDate(now; "M") = 9 OR formatDate(now; "M") = 10` |
| 6 | Nov-Dec | January 15 | `formatDate(now; "M") = 11 OR formatDate(now; "M") = 12` |

Build a Router with 6 branches, each filtering invoices for the relevant period. After the router, use an Array Aggregator to sum amounts per period for the VAT report.

**Quarterly Advance Tax Payments (Mikdamot)**

Self-employed and some companies pay quarterly advance tax:

| Quarter | Months | Payment Due |
|---|---|---|
| Q1 | Jan-Mar | April 15 |
| Q2 | Apr-Jun | July 15 |
| Q3 | Jul-Sep | October 15 |
| Q4 | Oct-Dec | January 15 |

**Annual Reporting**

Annual tax return deadlines vary by filing method:
- Online filing: April 30
- Accountant filing: extended to May 31 or later (varies by year)

For annual automations, schedule a scenario to run on January 1 that aggregates the previous year's data.

Consult `references/billing-cycle-patterns.md` for detailed router configurations and Make.com filter expressions.

### Step 5: Schedule with the Israeli Calendar

**Shabbat-Aware Scheduling**

Make.com scenarios that interact with Israeli businesses or customers should avoid running during Shabbat (Friday sunset to Saturday sunset). Configure scheduling as follows:

1. Set the scenario schedule to run Sunday through Thursday only
2. For Friday runs, set the latest execution time to 14:00 Israel time (IST, UTC+2 / IDT, UTC+3 during DST)
3. Avoid Saturday entirely

In Make.com scheduling settings:
- Use the "Specify dates" option and exclude Saturday
- Set timezone to `Asia/Jerusalem`
- For Friday cutoff, add a Filter module at the start of the scenario:

Filter condition to skip Shabbat hours:
```
formatDate(now; "d") != 6
OR
(formatDate(now; "d") = 6 AND formatDate(now; "H") < 14)
```

Where `d` = day of week (0=Sunday, 6=Saturday) and `H` = 24-hour format.

Note: `d = 5` is Friday. For summer months, Shabbat starts earlier (sometimes 19:00+), but a 14:00 Friday cutoff is a safe conservative default. For precise candle-lighting times, use an external API like Hebcal.

**Israeli Holiday Detection**

For scenarios that should pause during Israeli holidays (Rosh Hashana, Yom Kippur, Sukkot, Pesach, etc.), add an HTTP module at the beginning that checks the Hebcal API:

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
2. Set Cardcom's "Notify URL" to the Make.com webhook URL
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
| `npay` | Number of payments |

**Grow (by Leumi) Webhook**

Grow provides a modern REST webhook:

1. Register your Make.com webhook URL in the Grow dashboard
2. Grow sends JSON POST with event type and payment details
3. Verify the webhook signature using the shared secret in the `X-Grow-Signature` header

For all payment gateways, always validate:
- The response/status code indicates success before processing
- The amount matches the expected charge
- For installments (tashlumim), store both the total and per-payment amounts

## Examples

### Example 1: Sync Green Invoice to Monday.com

User says: "Create a Make.com scenario that adds a new Monday.com item whenever a Green Invoice tax invoice is created"

Actions:
1. Add Green Invoice "Watch Documents" trigger, filter for type 320 (tax invoice)
2. Add Monday.com "Create an Item" action
3. Map fields: invoice number to Name column, client name to Client column, amount to Amount column (number type), date to Date column using `formatDate`
4. Set schedule to every 15 minutes, Sunday-Thursday + Friday until 14:00

Result: New Monday.com items created automatically for each tax invoice, with Hebrew client names preserved and ILS amounts correctly formatted.

### Example 2: Bimonthly VAT Summary

User says: "Build a scenario that generates a VAT summary spreadsheet at the end of each bimonthly period"

Actions:
1. Schedule trigger for the 1st of March, May, July, September, November, January
2. Add Green Invoice "Search Documents" to fetch all invoices from the previous 2-month period
3. Add Iterator to process each invoice
4. Add Router with branches for income (type 320) and expenses (type 305)
5. Add Array Aggregator per branch to sum amounts
6. Add Google Sheets "Add Row" to write period, total income, total expenses, and VAT difference

Result: Automated bimonthly VAT summary that matches the Israeli tax authority reporting periods.

### Example 3: WhatsApp Order Confirmation in Hebrew

User says: "Send a WhatsApp message in Hebrew when a customer places an order"

Actions:
1. Add Custom Webhook trigger to receive order events
2. Add HTTP module calling WhatsApp Cloud API
3. Use a pre-approved Hebrew message template with variables: customer name, order number, total in ILS
4. Format amount with `"₪" + formatNumber(amount; 2; "."; ",")`
5. Add Shabbat filter to queue messages during Shabbat for delivery on Sunday morning

Result: Customers receive Hebrew WhatsApp confirmations with properly formatted ILS amounts, respecting Shabbat hours.

## Bundled Resources

### References
- `references/make-israeli-modules.md` - Complete reference of Israeli service modules and HTTP configurations for Make.com, including Green Invoice, Monday.com, Priority ERP, WhatsApp Cloud API, Israeli SMS providers, and payment gateways. Consult when setting up a new Israeli app connection or troubleshooting API authentication.
- `references/billing-cycle-patterns.md` - Detailed Israeli billing cycle automation patterns including bimonthly VAT, quarterly advance payments, annual reporting, and payroll schedules. Includes Make.com filter expressions and router configurations. Consult when building time-based automations tied to Israeli tax or billing deadlines.

## Gotchas

- Agents default to monthly VAT reporting (US/EU pattern). Israeli VAT reporting is bimonthly for most businesses. Always confirm the reporting frequency before building period filters.
- Make.com's date functions use US-style day-of-week numbering (0 = Sunday). Agents often assume Monday = 0 (ISO 8601). Sunday is 0, Saturday is 6 in Make.com.
- Green Invoice amounts in the API are in agorot (integer), not shekels. Agents frequently forget to divide by 100 for display or multiply by 100 when sending to the API.
- Agents tend to schedule Friday runs at 17:00 or later. Shabbat can start as early as 16:00 in winter. Use 14:00 as the safe Friday cutoff.
- Hebrew column names in Monday.com should be referenced by column ID, not by the display title. Agents often try to use the Hebrew title directly, which breaks when users rename columns.
- Make.com filter expressions use single equals (`=`) for comparison, not double (`==`). Agents habitually write `==` from programming experience.
- The Israeli tax year is January-December (same as calendar year), but agents sometimes assume April-March (UK pattern) or October-September (US fiscal year).

## Troubleshooting

### Error: "Green Invoice API returns 401 Unauthorized"
Cause: API key/secret mismatch, or using sandbox credentials in production (or vice versa)
Solution: Verify you are using the correct environment. Green Invoice sandbox URL is `https://sandbox.d.greeninvoice.co.il/api/v1/`, production is `https://api.greeninvoice.co.il/api/v1/`. Regenerate the API key if needed.

### Error: "Hebrew text appears garbled in output"
Cause: Encoding mismatch. Some Israeli APIs return Windows-1255 or ISO-8859-8 instead of UTF-8.
Solution: Check the API response headers for `charset`. If not UTF-8, add a Text Parser module after the HTTP module and set input encoding to match the source. Green Invoice and Monday.com use UTF-8 natively.

### Error: "Make.com scenario runs on Saturday"
Cause: Timezone set to UTC instead of Asia/Jerusalem, causing the schedule to misalign with Israeli time.
Solution: In scenario settings, set timezone to `Asia/Jerusalem`. Verify the Shabbat filter uses the correct day-of-week value (6 = Saturday in Make.com).

### Error: "Cardcom webhook not triggering"
Cause: Make.com custom webhook must be "listening" (turned on) before Cardcom sends the notification. Also, Cardcom requires HTTPS.
Solution: Ensure the scenario is active and the webhook is in listening mode. Copy the webhook URL after activating it. Verify the URL starts with `https://`. Test with a small transaction first.
