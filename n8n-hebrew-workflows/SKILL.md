---
name: n8n-hebrew-workflows
description: Build and optimize n8n 2.0 automation workflows with Israeli API integrations including Morning (formerly Green Invoice), israeli-bank-scrapers, data.gov.il, Israeli SMS gateways, and payment processors (Cardcom, Tranzila, Grow by Meshulam). Use when user asks to "create n8n workflow for Israeli business", "connect Morning/Green Invoice to n8n", "automate hashbonit", "tazrim avoda b'ivrit", "set up Shabbat-aware schedule trigger", "n8n AI agent for Israeli business", or integrate Israeli payment gateways into n8n flows. Covers Hebrew data handling in Code nodes, NIS currency formatting, Shabbat/holiday-aware scheduling via Hebcal API, n8n 2.0 breaking changes, AI Agent nodes for Israeli use cases, MCP integration, Israel Invoice Reform 2026 (allocation numbers), and self-hosting on Israeli cloud. Do NOT use for general n8n tutorials without Israeli context (use n8n official docs), standalone invoice management (use green-invoice-il), or Hebrew NLP tasks (use hebrew-nlp-toolkit).
license: MIT
allowed-tools: Bash(n8n:*) Bash(curl:*) Bash(node:*) Bash(npx:*) Bash(docker:*)
compatibility: Requires n8n 1.0+ (n8n 2.0 recommended). Node.js 22.12.0+ for israeli-bank-scrapers. Docker recommended for self-hosting. Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Gemini CLI.
---

# n8n Hebrew Workflows

## Instructions

### Step 1: Identify the Automation Pattern

Map the user's Israeli business need to an n8n workflow pattern. Use this table to select the right architecture before building anything:

| Business Need | n8n Pattern | Key Nodes | Israeli API |
|--------------|-------------|-----------|-------------|
| Invoice reconciliation | Schedule Trigger -> HTTP -> Compare -> Update | Schedule Trigger, HTTP Request, IF, Code | Morning (Green Invoice) API |
| Bank transaction categorization | Schedule Trigger -> Code -> Spreadsheet | Schedule Trigger, Code, Google Sheets | israeli-bank-scrapers |
| Government data sync | Schedule Trigger -> HTTP -> Transform -> DB | Schedule Trigger, HTTP Request, Code, Postgres | data.gov.il CKAN API |
| SMS notifications | Trigger -> Code -> HTTP | Webhook, Code, HTTP Request | 019 Telzar / InforUMobile API |
| Payment webhook handling | Webhook -> Validate -> Process | Webhook, IF, Code, HTTP Request | Cardcom / Tranzila / Grow by Meshulam |
| Holiday-aware scheduling | Schedule Trigger -> HTTP -> IF -> Execute | Schedule Trigger, HTTP Request, IF, Code | Hebcal API |
| Multi-step approval flow | Webhook -> Wait -> IF -> Notify | Webhook, Wait, IF, HTTP Request | Slack + SMS gateway |
| AI-powered categorization | Schedule Trigger -> Code -> AI Agent -> DB | Schedule Trigger, Code, AI Agent, Postgres | israeli-bank-scrapers + LLM |
| Invoice Reform compliance | Webhook -> Code -> HTTP -> HTTP | Webhook, Code, HTTP Request | Morning API + Tax Authority allocation |

**Decision criteria for choosing between patterns:**
- If the flow runs on a schedule, start with a Schedule Trigger node and consider Shabbat/holiday pausing (Step 4)
- If the flow responds to external events (payment confirmations, form submissions), start with a Webhook trigger
- If the flow processes Hebrew text, add a Code node early in the pipeline for encoding/RTL handling (Step 3)
- If the flow needs intelligent categorization or summarization, use an AI Agent node (Step 7)

### Step 2: Connect Israeli APIs in n8n

#### Morning (formerly Green Invoice) API

Morning (formerly Green Invoice, "hashbonit yeruka" / חשבונית ירוקה) uses API key + secret to obtain a JWT token. This is NOT OAuth2. Configure the HTTP Request node:

```
Method: POST
URL: https://api.greeninvoice.co.il/api/v1/account/token
Headers:
  Content-Type: application/json
Body:
{
  "id": "{{$env.GREEN_INVOICE_API_KEY}}",
  "secret": "{{$env.GREEN_INVOICE_API_SECRET}}"
}
```

The response contains a JWT token valid for 60 minutes. Store it and pass to subsequent requests:

```
Authorization: Bearer {{$json.token}}
```

**Israel Invoice Reform 2026 (threshold step-down):** Tax invoices over the threshold require an allocation number (mispar haktza'a) from the Israel Tax Authority. The threshold drops in 2026:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |
| Jan 1, 2027 | 5,000 NIS (planned to continue) |

After creating a document via the Morning API, call the Tax Authority allocation endpoint for qualifying invoices. Morning's API handles this automatically for documents created through their UI, but API-created documents may require explicit allocation requests depending on your integration. Build the threshold check as a configurable variable in your workflow, not a hardcoded number, since the threshold is scheduled to drop again. Check Morning's API documentation for the latest allocation workflow.

**Amounts are in decimal shekels (NOT agorot).** When creating documents, `price: 50` means 50 NIS, not 50 agorot. Do not multiply or divide by 100.

Common Morning API endpoints for n8n workflows:

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/api/v1/documents/search` | POST | Search invoices by date range, client, status |
| `/api/v1/documents` | POST | Create new invoice/receipt |
| `/api/v1/clients/search` | POST | Look up client by name or tax ID (osek number) |
| `/api/v1/payments` | GET | Fetch payment records for reconciliation |
| `/api/v1/businesses/me` | GET | Get current business info (company name, tax ID) |

Document type codes for the `type` field:

| Code | Document Type |
|------|--------------|
| 10 | Price Quote (hatzaat mechir) |
| 305 | Tax Invoice (hashbonit mas) |
| 320 | Tax Invoice / Receipt (hashbonit mas / kabala) |
| 330 | Credit Note / Refund (hashbonit zikui) |
| 400 | Receipt (kabala) |

Consult `references/israeli-api-endpoints.md` for full endpoint details, required fields, and response schemas.

#### israeli-bank-scrapers via Code Node

n8n does not have a native Israeli bank node. Use a Code node to run `israeli-bank-scrapers` programmatically. The package is a Node.js library (NOT a CLI tool), so you must use `createScraper()`:

**Important:** Requires Node.js >= 22.12.0 in your n8n environment.

```javascript
// In a Code node (n8n 2.0: runs in isolated task runner)
const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');

const scraper = createScraper({
  companyId: CompanyTypes.hapoalim,
  startDate: new Date('2026-01-01'),
  combineInstallments: false,
  showBrowser: false
});

const credentials = {
  username: $env.BANK_USER,
  // Store bank credentials in n8n environment variables
  userPassword: $env.BANK_PASS
};
const result = await scraper.scrape(credentials);

if (result.success) {
  return result.accounts.flatMap(account =>
    account.txns.map(txn => ({ json: txn }))
  );
} else {
  throw new Error(`Scraping failed: ${result.errorType} - ${result.errorMessage}`);
}
```

Supported scrapers: hapoalim, leumi, discount, mizrahi, otsarHahayal, beinleumi, massad, yahav, beyahadMishkantaot, oneZero, behatsdaa, visaCal, max (formerly Leumi Card), isracard, amex, mercantile.

**Cloudflare blocking (2026):** Since early 2026, Cloudflare's bot detection blocks headless browsers on Amex and Isracard sites. The maintained fork `@sergienko4/israeli-bank-scrapers` uses Camoufox as a workaround. If you encounter persistent scraping failures with these providers, switch to the fork:

```bash
npm install @sergienko4/israeli-bank-scrapers
```

**Security note:** Store credentials in n8n's credential store, not in workflow JSON. Use environment variables for sensitive values.

#### data.gov.il CKAN API

Israeli government open data uses the CKAN API:

```
GET https://data.gov.il/api/3/action/datastore_search
Parameters:
  resource_id: <resource-guid>
  q: <search-term>
  limit: 100
  offset: 0
```

Useful resource IDs for common workflows:

| Dataset | Resource ID | Content |
|---------|-------------|---------|
| Non-Profit Registry | be5b7935-3922-45d4-9638-08871b17ec95 | Registered amutot (non-profits) |
| Import/Export Stats | Various | Trade statistics by HS code |

The API returns Hebrew field names. Use a Code node to normalize keys to English for downstream processing.

#### Israeli SMS Gateways

| Gateway | API Type | Auth | Best For |
|---------|----------|------|----------|
| 019 Telzar | REST | Bearer token | Bulk marketing, transactional |
| InforUMobile | REST | Bearer token | OTP, transactional, WhatsApp |
| Nexmo/Vonage IL | REST | API key + secret | International + local |

019 Telzar SMS example in an HTTP Request node:

```
Method: POST
URL: https://019sms.co.il/api
Headers:
  Content-Type: application/json
  Authorization: Bearer {{$env.SMS_019_TOKEN}}
Body:
{
  "from": "MyBusiness",
  "to": "{{$json.phone}}",
  "message": "{{$json.text}}"
}
```

Israeli phone number formatting: Always send in international format `972XXXXXXXXX` (drop the leading 0). A Code node before the SMS node should handle this:

```javascript
const phone = $input.first().json.phone;
const cleaned = phone.replace(/[-\s]/g, '');
const formatted = cleaned.startsWith('0')
  ? '972' + cleaned.slice(1)
  : cleaned.startsWith('+972')
    ? cleaned.slice(1)
    : cleaned;
return [{ json: { ...$input.first().json, phone: formatted } }];
```

### Step 3: Handle Hebrew Data in n8n Nodes

#### RTL Text in Code Nodes

n8n Code nodes process strings as UTF-8, so Hebrew works natively. The problems arise at boundaries: API responses, CSV exports, email templates.

**Common Hebrew data issues and fixes:**

| Issue | Where It Happens | Fix |
|-------|-----------------|-----|
| Reversed Hebrew in CSV | Spreadsheet File node export | Set encoding to UTF-8-BOM in output options |
| Broken nikud (vowels) | HTTP Request response parsing | Set response encoding to UTF-8 explicitly |
| Mixed RTL/LTR in emails | Send Email node | Wrap Hebrew text in `<div dir="rtl">` |
| Hebrew JSON keys | data.gov.il API responses | Normalize keys in Code node before processing |
| Truncated Hebrew | String length checks | Use `Array.from(str).length` for character count, not `.length` |

#### NIS Currency Formatting

Use this Code node snippet for proper Israeli Shekel formatting:

```javascript
function formatNIS(amount) {
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: 'ILS',
    minimumFractionDigits: 2
  }).format(amount);
}

// Input:  12345.60
// Output: 12,345.60 ₪
```

**Note on Morning (Green Invoice) API:** Amounts in the API are in decimal shekels (not agorot). `price: 50` means 50.00 NIS. Do not perform agorot-to-shekel conversions when working with Morning API responses or request payloads.

#### Hebrew Date Parsing

Israeli documents often use Hebrew dates or DD/MM/YYYY format. Parse with care:

```javascript
// Parse Israeli date format DD/MM/YYYY
function parseIsraeliDate(dateStr) {
  const [day, month, year] = dateStr.split('/').map(Number);
  return new Date(year, month - 1, day);
}

// Parse Hebrew month names (common in government docs)
const hebrewMonths = {
  'ינואר': 0, 'פברואר': 1, 'מרץ': 2, 'אפריל': 3,
  'מאי': 4, 'יוני': 5, 'יולי': 6, 'אוגוסט': 7,
  'ספטמבר': 8, 'אוקטובר': 9, 'נובמבר': 10, 'דצמבר': 11
};
```

### Step 4: Shabbat-Aware Scheduling

Business workflows in Israel must not run during Shabbat (Friday sundown to Saturday sundown) and Jewish holidays. n8n's built-in Schedule Trigger node does not support this, so build a check node at the start of every scheduled workflow.

**Architecture:** Schedule Trigger -> HTTP Request (Hebcal) -> IF (is Shabbat?) -> Continue or Stop

Hebcal API call in an HTTP Request node:

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` is Tel Aviv. Other common cities:

| City | Geoname ID | Candle Lighting |
|------|-----------|-----------------|
| Jerusalem | 281184 | 40 minutes before sunset |
| Tel Aviv | 293397 | 18 minutes before sunset |
| Haifa | 294801 | 30 minutes before sunset |
| Zikhron Ya'akov | 293067 | 30 minutes before sunset |
| Beer Sheva | 295530 | 18 minutes before sunset |
| All other cities | varies | 18 minutes before sunset |

The response includes candle lighting and havdalah times. Use a Code node to determine if the current time falls within Shabbat:

```javascript
const now = new Date();
const shabbatData = $input.first().json;

const candleLighting = shabbatData.items.find(
  item => item.category === 'candles'
);
const havdalah = shabbatData.items.find(
  item => item.category === 'havdalah'
);

if (candleLighting && havdalah) {
  const shabbatStart = new Date(candleLighting.date);
  const shabbatEnd = new Date(havdalah.date);

  if (now >= shabbatStart && now <= shabbatEnd) {
    return []; // Empty output stops the workflow
  }
}

return $input.all(); // Continue workflow
```

For Jewish holidays, query the Hebcal holidays API:

```
GET https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&mod=on
```

Filter for `yomtov: true` items. These are days when work restrictions apply (similar to Shabbat).

Consult `references/shabbat-cron-patterns.md` for pre-built patterns covering weekly, monthly, and custom schedules with holiday awareness.

### Step 5: Israeli Payment Gateway Webhooks

Israeli payment gateways send transaction results via webhooks (callback URLs). Configure n8n Webhook nodes to receive and process these.

#### Cardcom

Cardcom sends POST with form-encoded data to your callback URL:

```
n8n Webhook URL: https://your-n8n.example.com/webhook/cardcom-callback
Method: POST
Content-Type: application/x-www-form-urlencoded
```

Key fields in the Cardcom callback:

| Field | Description | Values |
|-------|-------------|--------|
| `ReturnValue` | Transaction status | `0` = success, other = error code |
| `InternalDealNumber` | Cardcom transaction ID | Numeric string |
| `DealResponse` | Response description | Hebrew text |
| `CardOwnerID` | Customer Israeli ID (teudat zehut) | 9 digits |
| `NumOfPayments` | Installments (tashlumim) count | 1-36 |

Validation Code node after the Webhook:

```javascript
const data = $input.first().json;

if (data.ReturnValue !== '0') {
  return [{
    json: {
      success: false,
      error: data.DealResponse,
      cardcomId: data.InternalDealNumber
    }
  }];
}

return [{
  json: {
    success: true,
    transactionId: data.InternalDealNumber,
    amount: parseFloat(data.Sum),
    installments: parseInt(data.NumOfPayments),
    customerId: data.CardOwnerID
  }
}];
```

**Cardcom API v11:** For modern integrations, configure the webhook URL in the Cardcom API v11 endpoint rather than the legacy merchant dashboard. See Cardcom's developer documentation for the updated webhook registration flow.

#### Tranzila

Tranzila uses a callback pattern where the callback URL receives GET parameters:

```
https://your-n8n.example.com/webhook/tranzila-callback?Response=000&index=12345&sum=100.00&currency=1
```

| Field | Description | Values |
|-------|-------------|--------|
| `Response` | Status code | `000` = approved, `001`-`999` = error codes |
| `index` | Transaction index | Numeric |
| `sum` | Amount charged | Decimal (NIS if `currency=1`) |
| `currency` | Currency code | `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR |
| `Rone` | Installments | Number |

**Tranzila API v2:** Tranzila offers a modern iframe-based and hosted fields integration for PCI compliance. The v2 API also supports Bit payments (see Step 5b). For new integrations, prefer the v2 API over the legacy `tranzila71dl.cgi` pattern shown above. See `https://docs.tranzila.com/` for the v2 documentation.

#### Grow by Meshulam

Grow by Meshulam sends webhook notifications as POST requests. **Important:** The Grow API uses `multipart/form-data` for API requests (not JSON). After receiving a webhook, you must call `approveTransaction` to finalize the payment.

Webhook payload fields:

| Field | Description |
|-------|-------------|
| `webhookKey` | Webhook verification key |
| `transactionCode` | Unique transaction code |
| `transactionType` | Type of transaction |
| `asmachta` | Transaction reference number (asmachta) |
| `paymentSum` | Amount charged |
| `paymentDate` | Date of payment |
| `fullName` | Customer full name |
| `payerPhone` | Customer phone number |
| `payerEmail` | Customer email |
| `cardSuffix` | Last 4 digits of card |
| `cardBrand` | Card brand (Visa, Mastercard, etc.) |
| `paymentsNum` | Number of installments |

Code node to process Grow webhook and approve:

```javascript
const data = $input.first().json;

// Verify and extract payment data
const payment = {
  transactionCode: data.transactionCode,
  asmachta: data.asmachta,
  amount: parseFloat(data.paymentSum),
  customerName: data.fullName,
  customerPhone: data.payerPhone,
  customerEmail: data.payerEmail,
  installments: parseInt(data.paymentsNum) || 1
};

// You must call approveTransaction after receiving the webhook
// This is done in a subsequent HTTP Request node using multipart/form-data
return [{ json: payment }];
```

**IP whitelisting:** Cardcom and Tranzila require your webhook server's IP to be whitelisted in their dashboard. If self-hosting n8n, use a static IP or configure a reverse proxy with a fixed egress IP.

#### Bit Payments

Bit is Israel's most popular mobile payment method. Bit payments are available through Tranzila (API v2) and Grow by Meshulam, not as a standalone API.

To accept Bit via Tranzila v2: create a payment page with `bit: true` in the payment request. The customer scans a QR code or is redirected to Bit. The webhook callback uses the same fields as credit card transactions.

To accept Bit via Grow by Meshulam: enable Bit in the Grow merchant dashboard. Bit transactions appear in the same webhook flow as card transactions, with a different `transactionType` value.

### Step 6: Self-Hosting Considerations

#### n8n 2.0 Breaking Changes (December 2025)

n8n 2.0 shipped in December 2025; the stable line is on 2.x (2.19.x as of May 2026, new minor most weeks). Pin a specific tag in production rather than `n8nio/n8n:latest`.

n8n 2.0 introduced significant changes that affect Israeli workflows:

| Change | Impact | Action Required |
|--------|--------|----------------|
| Execute Command node disabled by default | Bank scraper workflows using Execute Command will break | Use Code node instead (see Step 2), or re-enable via the `NODES_EXCLUDE` env var (see below) |
| Save/Publish workflow model | Workflows must be explicitly published to be active | Publish workflows after importing or creating them |
| Task runner isolation for Code nodes | Code nodes run in isolated sandboxes | Ensure all required packages are available in the task runner environment |
| MySQL/MariaDB support removed | Cannot use MySQL/MariaDB as n8n backend DB | Migrate to PostgreSQL (recommended) or SQLite |
| Security hardening | Stricter defaults for community nodes and external access | Review security settings if using community nodes for Israeli integrations |

In n8n 2.0, the Execute Command node (and Local File Trigger) are added to the default `NODES_EXCLUDE` list, which is why they vanish from the node panel. To re-enable Execute Command, override `NODES_EXCLUDE` so it no longer contains `n8n-nodes-base.executeCommand`, the simplest override is an empty list, then restart n8n:

```
NODES_EXCLUDE=[]
```

Per the n8n 2.0 breaking-changes docs this is the supported mechanism, there is no `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable. Enabling Execute Command lets anyone with workflow edit access run arbitrary shell commands, so only do this in trusted single-user deployments. Migrating to Code nodes remains the recommended path.

#### Israeli Cloud Options

| Provider | Data Residency | n8n Support | Notes |
|----------|---------------|-------------|-------|
| AWS (il-central-1) | Israel (Tel Aviv) | Full Docker support | Local zone launched 2023, full region available |
| Azure (Israel Central) | Israel | Full Docker support | israelcentral region |
| Google Cloud (me-west1) | Israel (Tel Aviv) | Full Docker support | Launched 2022 |
| Kamatera | Israel (Petah Tikva DC) | VPS with Docker | Israeli company, NIS billing |
| ActiveCloud / HQserv / MedOne | Israel | VPS with Docker | Israeli companies, local support in Hebrew |

**Data residency compliance:** Israel's Privacy Protection Authority (PPA, rashut le-haganat ha-prat) does not mandate that all data remain within Israel. It restricts transfer of personal data to countries without adequate data protection, or requires additional safeguards (like contractual clauses) for transfers to other jurisdictions. For workflows that process PII (teudat zehut numbers, bank details, medical data), either choose a provider with an Israeli data center or ensure the destination country has adequate protection per the PPA's approved list.

#### Docker Compose for Self-Hosted n8n

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**Notes:**
- n8n 1.0+ uses built-in user management (email + password). The old `N8N_BASIC_AUTH_*` environment variables were removed. On first launch, n8n prompts you to create an owner account.
- `version: '3.8'` is omitted because it is obsolete in Docker Compose V2.
- **Critical:** Set `GENERIC_TIMEZONE=Asia/Jerusalem` and `TZ=Asia/Jerusalem`. Without this, all Schedule Trigger nodes use UTC, and Shabbat calculations will be off by 2-3 hours (Israel is UTC+2 in winter, UTC+3 in summer). Israeli DST begins on the Friday before the last Sunday of March and ends on the last Sunday of October.

### Step 7: n8n AI Agent Nodes for Israeli Workflows

n8n 2.0 includes 70+ AI nodes including Tools Agent, Conversational Agent, and LLM integrations. These are powerful for Israeli business automation.

**Example: AI-powered bank transaction categorizer**

Architecture: Schedule Trigger -> Code (bank scraper) -> AI Agent (categorize) -> Google Sheets

```javascript
// Code node: prepare transactions for AI categorization
const transactions = $input.all().map(item => ({
  json: {
    date: item.json.date,
    description: item.json.description,
    amount: item.json.chargedAmount,
    prompt: `Categorize this Israeli bank transaction for accounting purposes.
Transaction: "${item.json.description}" for ${item.json.chargedAmount} NIS on ${item.json.date}.
Categories: הכנסות (revenue), שכר (salary), ספקים (suppliers), מע"מ (VAT), ביטוח לאומי (Bituach Leumi), שכירות (rent), הוצאות משרד (office), אחר (other).
Respond with ONLY the Hebrew category name.`
  }
}));
return transactions;
```

Connect the Code node output to an AI Agent node (Tools Agent) configured with your preferred LLM. The agent categorizes each transaction based on the Hebrew description and known Israeli expense categories.

**n8n MCP Integration:** n8n supports Model Context Protocol (MCP) servers. You can connect an `israeli-bank-scrapers` MCP server to an n8n AI Agent node, allowing the agent to pull bank data on demand as part of a conversational workflow.

### Step 8: When to Use n8n vs Alternatives

| Criteria | n8n | Make.com | Zapier |
|----------|-----|----------|--------|
| Self-hosting (data residency) | Yes (Docker, any cloud) | No (SaaS only) | No (SaaS only) |
| Israeli API nodes | None built-in, use HTTP/Code | Some community | Very few |
| Workflow limit | Unlimited (self-hosted) | Plan-based | Plan-based |
| Code execution | Full Code nodes (JS/Python) | Limited JS | Limited |
| AI Agent nodes | 70+ AI nodes, MCP support | AI features | AI features |
| Pricing (self-hosted) | Free (open source) | N/A | N/A |
| Hebrew UI | No (English only) | Partial | No |
| Best for | Developers needing full control, data residency, unlimited automation | Non-developers wanting visual builder | Simple integrations, non-technical users |

Choose n8n when: you need self-hosting for Israeli data residency, unlimited automations, full code access for Israeli API quirks (Hebrew encoding, phone formatting, VAT calculations), or AI Agent capabilities with Israeli context.

### Step 9: Workflow JSON Import/Export

n8n workflows are JSON documents. Agents that build workflows programmatically (instead of clicking in the UI) must understand the shape:

```json
{
  "name": "Morning daily reconciliation",
  "nodes": [
    {
      "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 6 * * 0-4" }] } },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [240, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get Token", "type": "main", "index": 0 }]] }
  }
}
```

Key structure:
- **`nodes`**: array of node objects. Each has `name` (unique, used as the connection key), `type` (e.g. `n8n-nodes-base.httpRequest`), `typeVersion` (must match a version n8n supports, or import fails), `parameters` (node config), and `position` (`[x, y]` coords).
- **`connections`**: object keyed by source node `name`, mapping an output (`main`) to an array of arrays of `{ node, type, index }` targets. The double array allows multiple outputs (e.g. an IF node's branches).
- Export via the UI ("Download") or `GET /api/v1/workflows/{id}`; import via "Import from File" or `POST /api/v1/workflows`. After importing into n8n 2.0 you must **publish** the workflow before it runs. `typeVersion` values change between releases, so build JSON against a known n8n version.

### Step 10: Credentials Setup for Israeli APIs

n8n stores secrets in its encrypted credential store, never inline in workflow JSON:

- **Morning (Green Invoice) JWT**: no n8n-native credential. Chain HTTP Request nodes, the first calls `/account/token` with the API key + secret, later nodes send `Authorization: Bearer {{token}}` via **Header Auth** or an expression. The token expires after 60 minutes, so refresh per execution rather than storing it long-lived.
- **Israeli SMS gateways (019, InforUMobile)**: create a **Header Auth** credential, name `Authorization`, value `Bearer <token>`, attach it to the HTTP Request node.
- **Payment gateways (Cardcom, Tranzila, Grow)**: store merchant IDs / API keys as **Generic Credential** values referenced via `{{$credentials.fieldName}}`. Grow's `multipart/form-data` requests still pull secrets from the credential, not the node body.
- For self-hosted n8n, set a stable `N8N_ENCRYPTION_KEY` so the credential store stays decryptable across restarts.

## Examples

### Example 1: Connect Morning to n8n for daily invoice reconciliation

User says: "Every morning, pull yesterday's Morning invoices and flag any that are still unpaid."

Node-by-node:
1. **Schedule Trigger** (`scheduleTrigger`): cron `0 6 * * 0-4` (09:00 Israel winter, Sunday-Thursday).
2. **HTTP Request, "Get Token"**: `POST https://api.greeninvoice.co.il/api/v1/account/token` with `{ id, secret }` from credentials. Output: JWT.
3. **HTTP Request, "Search Documents"**: `POST /api/v1/documents/search` with `Authorization: Bearer {{$json.token}}`, body filtering `fromDate`/`toDate` to yesterday and `type` to 305/320.
4. **IF node**: branch on `status` (open vs closed) to separate unpaid invoices.
5. **HTTP Request (SMS) or Send Email**: notify the bookkeeper about unpaid invoices, Hebrew body wrapped in `<div dir="rtl">`.

Wrap the whole flow with the Shabbat check from Step 4 if it must never run on a holiday that falls on a weekday.

### Example 2: Bank transactions to a Google Sheet, holiday-aware

User says: "Scrape my business account nightly and append new transactions to a sheet, but skip Shabbat and holidays."

Node-by-node:
1. **Schedule Trigger**: cron for a weeknight time.
2. **HTTP Request (Hebcal)** + **Code (Shabbat check)** from Step 4: empty output stops the run during Shabbat/holiday.
3. **Code node**: run `israeli-bank-scrapers` via `createScraper()` (Step 2), one item per transaction.
4. **Code node**: normalize Hebrew descriptions, format amounts with `Intl.NumberFormat('he-IL', ...)`, parse dates as DD/MM/YYYY.
5. **Google Sheets node** (Append): write rows to the bookkeeping sheet.
6. A separate **Error Trigger** workflow catches a failed run and alerts (see Gotchas).

## Recommended MCP Servers

These MCP servers from the directory give an AI Agent node live Israeli data on demand:

- **hebcal**: Hebrew/Jewish calendar and Shabbat times, an alternative to calling the Hebcal HTTP API in every workflow.
- **israeli-bank**: Israeli bank account data, lets an agent pull transactions instead of running `israeli-bank-scrapers` in a Code node.
- **data-gov-il**: Israeli government open data (CKAN), query registries without hand-building HTTP Request nodes.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| n8n Documentation | https://docs.n8n.io/ | Node reference, expressions, self-hosting |
| n8n 2.0 Breaking Changes | https://docs.n8n.io/2-0-breaking-changes/ | Execute Command, NODES_EXCLUDE, removed DBs |
| n8n Block Access to Nodes | https://docs.n8n.io/hosting/securing/blocking-nodes/ | NODES_EXCLUDE / NODES_INCLUDE syntax |
| Morning (Green Invoice) API | https://www.greeninvoice.co.il/api-docs | Endpoints, document types, allocation flow |
| Hebcal API | https://www.hebcal.com/home/developer-apis | Shabbat times, holidays, geonameid values |
| data.gov.il CKAN API | https://data.gov.il/api/3 | datastore_search, resource IDs |

## Gotchas

- **Agents default to UTC for schedule triggers.** Israel uses `Asia/Jerusalem` (UTC+2/+3), and Israeli DST transitions happen on different dates than US/EU (DST begins on the Friday before the last Sunday of March, ends on the last Sunday of October). Always set `GENERIC_TIMEZONE` in n8n config and verify trigger timing after every DST change.
- **Agents format dates as MM/DD/YYYY.** Israeli documents, APIs, and users universally use DD/MM/YYYY. Every date parsing Code node must explicitly handle this. Morning (Green Invoice) API returns ISO 8601, but government datasets often return DD/MM/YYYY as strings.
- **Agents send Israeli phone numbers with leading zero.** SMS gateway APIs require international format (`972XXXXXXXXX`). A phone number like `050-1234567` must become `972501234567`. Always strip the leading zero and prepend `972`.
- **Agents assume VAT is included in amounts.** Israeli invoices commonly show amounts before VAT (lifnei maam). Morning (Green Invoice) API returns both `amount` (before VAT) and `totalAmount` (with VAT). Always check which field you need. Current VAT rate is 18% (as of 2026).
- **Agents miss that Shabbat times vary by city.** Candle lighting in Jerusalem is 40 minutes before sunset, in Haifa and Zikhron Ya'akov 30 minutes, and in Tel Aviv and all other cities 18 minutes. Using a single hardcoded time for all of Israel will cause workflows to run during Shabbat in some cities.
- **Execute Command node is disabled by default in n8n 2.0.** If your workflow used Execute Command to run shell scripts (e.g., for bank scraping), it will silently fail after upgrading to n8n 2.0. Migrate to Code nodes, or re-enable it by overriding the `NODES_EXCLUDE` env var so it no longer lists `n8n-nodes-base.executeCommand` (there is no `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable, that is a common hallucination).
- **Morning (Green Invoice) amounts are in shekels, not agorot.** The API uses decimal shekels (`price: 50` = 50 NIS). Do not multiply by 100 or perform agorot conversions. This is different from some Israeli payment gateways that use agorot.
- **Invoice Reform 2026 affects automation, threshold drops June 1, 2026.** Tax invoices over the threshold (10,000 NIS through May 31, 2026, then 5,000 NIS from June 1, 2026) created via API require allocation numbers from the Tax Authority. Workflows that auto-generate invoices must handle the allocation step or the invoice may be invalid for tax deduction purposes. Make the threshold a workflow variable, not a hardcoded literal.
- **Unattended workflows fail silently without an Error Trigger.** A scheduled bank scrape or invoice sync that throws will just stop, no one sees it until the data is stale. Create a separate workflow starting with an **Error Trigger** node (n8n routes any failed execution to it) that sends a Hebrew alert to Slack or SMS. For transient failures (Cloudflare blocks, expired tokens, rate limits), also enable per-node **Retry On Fail** with a sensible wait, rather than letting the whole run die on the first hiccup.

## Bundled Resources

### References
- `references/israeli-api-endpoints.md` -- Complete reference table of Israeli API endpoints for n8n workflows, including Morning (Green Invoice), data.gov.il, SMS gateways, payment gateways, and Hebcal. Consult when configuring HTTP Request nodes for Israeli services.
- `references/shabbat-cron-patterns.md` -- Pre-built Shabbat-aware scheduling patterns for n8n including weekly, monthly, and holiday-aware configurations with Hebcal API integration. Consult when setting up any schedule-triggered workflow that should respect Shabbat and Jewish holidays.

## Troubleshooting

### Error: "Morning (Green Invoice) API returns 401 Unauthorized"
Cause: JWT token expired. Morning tokens have a TTL of 60 minutes.
Solution: Add a token refresh step at the beginning of every workflow execution. Store the token in n8n's static data (`$getWorkflowStaticData('global')`) with a timestamp, and refresh it if older than 55 minutes.

### Error: "Hebrew text appears garbled in CSV export"
Cause: The exported CSV lacks a UTF-8 BOM (Byte Order Mark), so Excel interprets it as ANSI.
Solution: In the Code node that prepares CSV data, prepend the BOM character: `'\uFEFF' + csvContent`. Alternatively, set the Spreadsheet File node's encoding option to UTF-8-BOM.

### Error: "Webhook not receiving Cardcom callbacks"
Cause: Cardcom requires the callback URL to be publicly accessible with a valid SSL certificate. Self-hosted n8n behind a firewall will not receive callbacks.
Solution: Use a reverse proxy (nginx, Caddy) with Let's Encrypt SSL. Ensure the n8n `WEBHOOK_URL` environment variable matches the public URL. Whitelist n8n's IP in the Cardcom merchant dashboard.

### Error: "Schedule Trigger runs during Shabbat despite Hebcal check"
Cause: n8n server timezone is set to UTC instead of Asia/Jerusalem, so the Shabbat time comparison is offset by 2-3 hours.
Solution: Verify `GENERIC_TIMEZONE=Asia/Jerusalem` in n8n environment variables. Restart n8n after changing timezone settings. Test by logging `new Date().toString()` in a Code node to confirm the server's effective timezone.

### Error: "israeli-bank-scrapers fails in Code node"
Cause: In n8n 2.0, Code nodes run in an isolated task runner. The `israeli-bank-scrapers` package and its dependencies (Puppeteer/Playwright) may not be available in the sandbox.
Solution: Install `israeli-bank-scrapers` as an npm package accessible to the n8n task runner. Ensure the n8n Docker container has sufficient memory (at least 1GB) for Chromium. If using the Execute Command approach (legacy), note that Execute Command is disabled by default in n8n 2.0.

### Error: "Cloudflare blocks bank scraper for Amex/Isracard"
Cause: Since early 2026, Cloudflare's bot detection blocks headless browsers on some Israeli financial sites.
Solution: Switch to the maintained fork `@sergienko4/israeli-bank-scrapers` which uses Camoufox to bypass Cloudflare detection. Install via `npm install @sergienko4/israeli-bank-scrapers`.
