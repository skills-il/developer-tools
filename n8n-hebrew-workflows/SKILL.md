---
name: n8n-hebrew-workflows
description: Build n8n 2.x automation workflows (stable 2.21) with Israeli API integrations including Morning (Green Invoice), EZCount, israeli-bank-scrapers, data.gov.il, SMS gateways, Cardcom v11, Tranzila v2, Grow by Meshulam. Use when user asks to "create n8n workflow for Israeli business", "connect Morning to n8n", "automate hashbonit", "Shabbat-aware schedule trigger", "n8n AI agent", or integrate Israeli payment gateways. Covers Hebrew data handling, NIS formatting, Hebcal scheduling, n8n 2.x security patches (Ni8mare CVE-2026-21858), AI Agent nodes with LangChain + RAG, MCP Client Tool and MCP Server Trigger, Israel Invoice Reform 2026 (allocation numbers, 5,000 NIS threshold from June 2026). Do NOT use for general n8n tutorials without Israeli context, standalone invoice management (use green-invoice-il), or Hebrew NLP (use hebrew-nlp-toolkit).
license: MIT
allowed-tools: Bash(n8n:*) Bash(curl:*) Bash(node:*) Bash(npx:*) Bash(docker:*)
compatibility: Requires n8n 2.10.1+ (security patch for CVE-2026-21858 / Ni8mare); stable line is 2.21.x as of May 2026. Node.js 22.12.0+ for israeli-bank-scrapers. Docker recommended for self-hosting. Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Gemini CLI.
---

# n8n Hebrew Workflows

## Instructions

### Step 1: Identify the Automation Pattern

Map the user's Israeli business need to an n8n workflow pattern:

| Business Need | n8n Pattern | Key Nodes | Israeli API |
|--------------|-------------|-----------|-------------|
| Invoice reconciliation | Schedule -> HTTP -> Compare -> Update | Schedule, HTTP, IF, Code | Morning (Green Invoice) |
| Bank transaction categorization | Schedule -> Code -> Spreadsheet | Schedule, Code, Sheets | israeli-bank-scrapers |
| Government data sync | Schedule -> HTTP -> Transform -> DB | Schedule, HTTP, Code, Postgres | data.gov.il CKAN |
| SMS notifications | Trigger -> Code -> HTTP | Webhook, Code, HTTP | 019 Telzar / InforUMobile |
| Payment webhook handling | Webhook -> Validate -> Process | Webhook, IF, Code, HTTP | Cardcom / Tranzila / Grow |
| Holiday-aware scheduling | Schedule -> HTTP -> IF -> Execute | Schedule, HTTP, IF, Code | Hebcal |
| AI-powered categorization | Schedule -> Code -> AI Agent -> DB | Schedule, Code, AI Agent, Postgres | israeli-bank-scrapers + LLM |
| Invoice Reform compliance | Webhook -> Code -> HTTP -> HTTP | Webhook, Code, HTTP | Morning + Tax Authority allocation |

Scheduled flows start with a Schedule Trigger and should add Shabbat/holiday pausing (Step 4). Event-driven flows (payment confirmations, form submissions) start with a Webhook trigger. Add a Code node early when Hebrew text needs encoding/RTL handling (Step 3), and an AI Agent node when categorization or summarization is involved (Step 7).

### Step 2: Connect Israeli APIs in n8n

#### Morning (formerly Green Invoice) API

Morning ("hashbonit yeruka" / חשבונית ירוקה) uses API key + secret to obtain a JWT token (NOT OAuth2). Configure HTTP Request:

```
POST https://api.greeninvoice.co.il/api/v1/account/token
Body: { "id": "{{$env.GREEN_INVOICE_API_KEY}}", "secret": "{{$env.GREEN_INVOICE_API_SECRET}}" }
```

The response contains a JWT token valid for 60 minutes. Pass it to subsequent requests as `Authorization: Bearer {{$json.token}}`.

**Israel Invoice Reform 2026 (threshold step-down):** Tax invoices over the threshold require an allocation number (mispar haktza'a) from the Tax Authority. The threshold drops mid-year:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |
| Jan 1, 2027 | 5,000 NIS (planned to continue) |

Build the threshold as a configurable variable, not a hardcoded number. Check Morning's API docs for the latest allocation workflow.

**Amounts are in decimal shekels (NOT agorot).** `price: 50` means 50 NIS, not 50 agorot.

Common Morning endpoints:

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/api/v1/documents/search` | POST | Search invoices by date range, client, status |
| `/api/v1/documents` | POST | Create new invoice/receipt |
| `/api/v1/clients/search` | POST | Look up client by name or osek number |
| `/api/v1/payments` | GET | Fetch payment records for reconciliation |
| `/api/v1/businesses/me` | GET | Get current business info |

Document type codes: 10 (Price Quote / hatzaat mechir), 305 (Tax Invoice / hashbonit mas), 320 (Tax Invoice + Receipt / hashbonit mas + kabala), 330 (Credit Note / hashbonit zikui), 400 (Receipt / kabala).

Consult `references/israeli-api-endpoints.md` for full endpoint details and response schemas.

#### EZCount (EasyCount) API

EZCount is a popular Morning alternative for SMB invoicing. REST + JSON, authenticated via `api_key` + `api_email` in the request body (not Bearer, not OAuth).

```
POST https://api.ezcount.co.il/api/createDoc
Body: { "api_key": "...", "api_email": "...", "developer_email": "you@example.com",
        "type": 320, "customer_name": "שם הלקוח", "customer_email": "client@example.com",
        "item": [{ "details": "שירותי ייעוץ", "amount": 1, "price": 500, "vat_type": "INC" }] }
```

Document type codes match the Tax Authority numbering used by Morning (305/320/330/400). Amounts are decimal shekels. The same Invoice Reform 2026 allocation flow applies; if the API returns `allocation_status: 'pending'`, retry after 30s. EZCount and Morning produce the same legal output, so pick by which accounting suite the user already uses.

#### israeli-bank-scrapers via Code Node

n8n has no native Israeli bank node. Use a Code node to run `israeli-bank-scrapers` programmatically (it is a Node.js library, NOT a CLI). Requires Node.js >= 22.12.0.

```javascript
const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');
const scraper = createScraper({
  companyId: CompanyTypes.hapoalim,
  startDate: new Date('2026-01-01'),
  combineInstallments: false,
  showBrowser: false
});
const result = await scraper.scrape({ username: $env.BANK_USER, userPassword: $env.BANK_PASS });
if (!result.success) throw new Error(`${result.errorType}: ${result.errorMessage}`);
return result.accounts.flatMap(a => a.txns.map(txn => ({ json: txn })));
```

Supported scrapers: hapoalim, leumi, discount, mizrahi, otsarHahayal, beinleumi, massad, yahav, beyahadMishkantaot, oneZero, behatsdaa, visaCal, max (formerly Leumi Card), isracard, amex, mercantile.

**Cloudflare blocking (2026):** Cloudflare's bot detection blocks headless browsers on Amex and Isracard. The maintained fork `@sergienko4/israeli-bank-scrapers` uses Camoufox as a workaround: `npm install @sergienko4/israeli-bank-scrapers`.

Store credentials in n8n's credential store, never in workflow JSON.

#### data.gov.il CKAN API

```
GET https://data.gov.il/api/3/action/datastore_search?resource_id=<guid>&q=<term>&limit=100
```

Useful resource IDs: Non-Profit Registry (`be5b7935-3922-45d4-9638-08871b17ec95`) for registered amutot; trade statistics by HS code (various IDs). The API returns Hebrew field names; use a Code node to normalize keys to English before downstream processing.

#### Israeli SMS Gateways

| Gateway | Auth | Best For |
|---------|------|----------|
| 019 Telzar | Bearer token | Bulk marketing, transactional |
| InforUMobile | Bearer token | OTP, transactional, WhatsApp |
| Nexmo/Vonage IL | API key + secret | International + local |

019 Telzar example:

```
POST https://019sms.co.il/api
Headers: Authorization: Bearer {{$env.SMS_019_TOKEN}}
Body: { "from": "MyBusiness", "to": "{{$json.phone}}", "message": "{{$json.text}}" }
```

Phone numbers must be international format `972XXXXXXXXX` (drop leading 0). Normalize in a Code node:

```javascript
const phone = $input.first().json.phone.replace(/[-\s]/g, '');
const formatted = phone.startsWith('0') ? '972' + phone.slice(1)
                : phone.startsWith('+972') ? phone.slice(1) : phone;
return [{ json: { ...$input.first().json, phone: formatted } }];
```

### Step 3: Handle Hebrew Data in n8n Nodes

n8n Code nodes process strings as UTF-8, so Hebrew works natively. Problems arise at boundaries (API responses, CSV exports, email templates):

| Issue | Where | Fix |
|-------|-------|-----|
| Reversed Hebrew in CSV | Spreadsheet File export | Set encoding to UTF-8-BOM |
| Broken nikud | HTTP Request response | Set response encoding to UTF-8 explicitly |
| Mixed RTL/LTR in emails | Send Email node | Wrap Hebrew in `<div dir="rtl">` |
| Hebrew JSON keys | data.gov.il responses | Normalize keys in Code node |
| Truncated Hebrew | String length checks | Use `Array.from(str).length`, not `.length` |

**NIS currency formatting:**

```javascript
new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS', minimumFractionDigits: 2 }).format(amount);
// 12345.60  ->  12,345.60 ₪
```

**Date parsing:** Israeli docs use DD/MM/YYYY. Morning API returns ISO 8601, but government datasets often return DD/MM/YYYY:

```javascript
function parseIsraeliDate(s) { const [d, m, y] = s.split('/').map(Number); return new Date(y, m - 1, d); }
const hebrewMonths = { 'ינואר': 0, 'פברואר': 1, 'מרץ': 2, 'אפריל': 3, 'מאי': 4, 'יוני': 5,
                        'יולי': 6, 'אוגוסט': 7, 'ספטמבר': 8, 'אוקטובר': 9, 'נובמבר': 10, 'דצמבר': 11 };
```

### Step 4: Shabbat-Aware Scheduling

Business workflows in Israel must not run during Shabbat (Friday sundown to Saturday sundown) and Jewish holidays. n8n's Schedule Trigger has no native support, so add a check node at the start of every scheduled workflow.

**Architecture:** Schedule Trigger -> HTTP Request (Hebcal) -> IF (is Shabbat?) -> Continue or Stop

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

Code node to gate the workflow on candle lighting / havdalah:

```javascript
const now = new Date();
const data = $input.first().json;
const candles = data.items.find(i => i.category === 'candles');
const havdalah = data.items.find(i => i.category === 'havdalah');
if (candles && havdalah) {
  const start = new Date(candles.date), end = new Date(havdalah.date);
  if (now >= start && now <= end) return []; // empty output stops workflow
}
return $input.all();
```

For Jewish holidays, query `https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&mod=on` and filter for `yomtov: true`. Consult `references/shabbat-cron-patterns.md` for pre-built patterns.

### Step 5: Israeli Payment Gateway Webhooks

#### Cardcom

Cardcom sends POST with form-encoded data:

| Field | Description |
|-------|-------------|
| `ReturnValue` | `0` = success, other = error code |
| `InternalDealNumber` | Cardcom transaction ID |
| `DealResponse` | Response description (Hebrew) |
| `CardOwnerID` | Customer teudat zehut (9 digits) |
| `NumOfPayments` | Installments (tashlumim) count |

For modern integrations, use the Cardcom API v11 endpoint (`https://secure.cardcom.solutions/api/v11`); it also lets you register webhooks for document-creation events. URLs must be HTTPS and publicly routable (no `localhost`; use ngrok or Cloudflare Tunnel in dev). Full docs: `https://secure.cardcom.solutions/api/v11/DOCS`.

#### Tranzila

Tranzila callbacks deliver GET parameters:

```
https://your-n8n.example.com/webhook/tranzila-callback?Response=000&index=12345&sum=100.00&currency=1
```

`Response=000` is approved. Currency: `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR. `Rone` = installments.

**Tranzila API v2** offers modern server-to-server (SAQ-D) plus iframe / hosted fields. Authentication uses an `X-tranzila-api-app-key` header (header confirmed via Stoplight API explorer at docs.tranzila.com). v2 supports Bit, tokenization, recurring billing, refunds, and 3D Secure (mandatory under SHVA rules). Prefer v2 over the legacy `tranzila71dl.cgi` CGI pattern. Bit flow: server calls Tranzila v2, response includes a URL to embed in an iframe (QR code + phone push). See `https://docs.tranzila.com/` for the v2 documentation.

#### Grow by Meshulam

Grow sends webhooks as POST. **Important:** the Grow API uses `multipart/form-data` (not JSON). After receiving a webhook, call `approveTransaction` to finalize the payment.

Webhook payload includes: `webhookKey`, `transactionCode`, `transactionType`, `asmachta` (transaction reference), `paymentSum`, `paymentDate`, `fullName`, `payerPhone`, `payerEmail`, `cardSuffix`, `cardBrand`, `paymentsNum`.

#### Bit Payments

Bit is Israel's most popular mobile payment method, available through Tranzila (API v2) and Grow by Meshulam, not as a standalone API. Via Tranzila v2: create a payment page with `bit: true`; the customer scans a QR code or is redirected to Bit. Via Grow: enable Bit in the merchant dashboard; Bit transactions appear in the same webhook flow with a different `transactionType`.

#### Webhook Authentication

n8n's Webhook node supports four auth modes: None, Basic Auth, Header Auth, JWT Auth. After CVE-2026-21858 (Ni8mare), the "None" mode on a publicly-routable webhook is effectively a vulnerability; use Header Auth (default for Israeli SMS callbacks), Basic Auth (private/VPN), or JWT Auth (cross-org).

n8n has no built-in HMAC verifier and no automatic `exp`/`iss`/`aud` claim validation on JWTs. See `references/webhook-auth-patterns.md` for HMAC verification and JWT claim-validation Code-node snippets.

**IP whitelisting:** Cardcom and Tranzila require your webhook server's IP to be whitelisted. If self-hosting, use a static IP or a reverse proxy with a fixed egress IP.

### Step 6: Self-Hosting Considerations

#### n8n 2.x Security Patches and Breaking Changes

n8n 2.0 shipped in December 2025; the stable line is 2.21.x as of May 2026 (beta on 2.22.0, new minor most weeks). Pin a specific tag in production, never `n8nio/n8n:latest`.

**CRITICAL security patch (pin >= 2.10.1):** CVE-2026-21858 ("Ni8mare", CVSS 10.0) is an unauthenticated RCE via webhook/form requests, disclosed January 2026 and patched in 1.121.0 and 2.10.1. A chained pair (CVE-2026-27493 + CVE-2026-27577, March 2026) escalates to host RCE on versions <2.10.1, <2.9.3, <1.123.22. Any public Webhook node (every payment-gateway workflow in this skill) makes the host exploitable. Pin >= 2.10.1, ideally current 2.21.x.

Key n8n 2.0 changes affecting Israeli workflows:

| Change | Impact | Action |
|--------|--------|--------|
| Execute Command node disabled by default | Bank-scraper workflows using Execute Command break | Use Code node, or re-enable via `NODES_EXCLUDE` |
| Save/Publish model | Workflows must be explicitly published | Publish after import or creation |
| Task runner isolation for Code nodes | Code runs in isolated sandboxes | Ensure required packages are in the runner env |
| MySQL/MariaDB support removed | Cannot use them as n8n backend DB | Migrate to PostgreSQL or SQLite |

To re-enable Execute Command, override `NODES_EXCLUDE` so it no longer contains `n8n-nodes-base.executeCommand` (empty list works), then restart n8n:

```
NODES_EXCLUDE=[]
```

There is no `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable (a common hallucination). Enabling Execute Command lets anyone with workflow edit access run arbitrary shell, so use only in trusted single-user deployments. Code nodes remain the recommended path.

#### Israeli Cloud Options

| Provider | Data Residency | Notes |
|----------|---------------|-------|
| AWS (il-central-1) | Israel (Tel Aviv) | Full Docker support, region GA |
| Azure (Israel Central) | Israel | `israelcentral` region |
| Google Cloud (me-west1) | Israel (Tel Aviv) | Launched 2022 |
| Kamatera | Israel (Petah Tikva) | VPS + Docker, Israeli company, NIS billing |
| ActiveCloud / HQserv / MedOne | Israel | VPS + Docker, Hebrew support |

Israel's Privacy Protection Authority (PPA) does not mandate that all data stay in Israel, but restricts transfers to countries without adequate data protection. For workflows processing PII (teudat zehut, bank, medical), choose an Israeli DC or verify destination adequacy on the PPA's approved list.

#### Docker Compose for Self-Hosted n8n

```yaml
services:
  n8n:
    # Must be >= 2.10.1 to be patched for CVE-2026-21858 (Ni8mare).
    image: n8nio/n8n:2.21.4
    restart: unless-stopped
    ports: ["5678:5678"]
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
```

Notes:
- n8n 1.0+ uses built-in user management; old `N8N_BASIC_AUTH_*` vars are removed. n8n prompts for an owner account on first launch.
- Set both `GENERIC_TIMEZONE=Asia/Jerusalem` AND `TZ=Asia/Jerusalem`. Without these, Schedule Trigger nodes default to UTC and Shabbat calculations drift 2-3 hours. Israeli DST runs Friday-before-last-Sunday-of-March through last Sunday of October.
- Never run `:latest` in production after the 2026 CVE chain. Pin the tag and update via controlled redeploy.

### Step 7: n8n AI Agent Nodes for Israeli Workflows

n8n 2.x ships native LangChain integration (the "Advanced AI" node group): 70+ AI nodes including Tools Agent, Conversational Agent, Memory (Window/Summary Buffer), Vector Store nodes (Pinecone, Qdrant, Supabase pgvector for RAG), and Model nodes for OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet, Claude Opus 4.7 with adaptive thinking), and local models via Ollama.

| Use case | Recommended model | Why |
|----------|-------------------|-----|
| Hebrew transaction categorization | Claude 3.5 Sonnet | Strong Hebrew, low hallucination on Israeli tax categories |
| Hebrew document summarization | Claude Opus 4.7 (adaptive thinking) | Best for complex Hebrew legal text |
| Real-time Hebrew chat | GPT-4o | Lower latency for short Hebrew responses |
| On-prem / data residency | Ollama (Llama 3.1, Qwen 2.5) on Israeli VPS | PII stays in Israel; acceptable for categorization |

**RAG with Israeli content:** Connect a Vector Store node (Pinecone, Qdrant, Supabase pgvector) to an AI Agent for retrieval over Israeli corpora. Use a multilingual embedding model that handles Hebrew (Cohere `embed-multilingual-v3.0` or OpenAI `text-embedding-3-large`); the default `text-embedding-ada-002` is weak on Hebrew.

**Example: AI bank transaction categorizer.** Schedule -> Code (bank scraper) -> AI Agent (categorize) -> Google Sheets:

```javascript
return $input.all().map(item => ({ json: {
  date: item.json.date, description: item.json.description, amount: item.json.chargedAmount,
  prompt: `Categorize this Israeli bank transaction. Transaction: "${item.json.description}" for ${item.json.chargedAmount} NIS on ${item.json.date}.
Categories: הכנסות, שכר, ספקים, מע"מ, ביטוח לאומי, שכירות, הוצאות משרד, אחר.
Respond with ONLY the Hebrew category name.`
}}));
```

**n8n MCP nodes:**

- **MCP Client Tool** (`@n8n/n8n-nodes-langchain.toolMcp`): attach as a sub-node so an AI Agent can call tools on an external MCP server (e.g. agentskills.co.il's `hebcal`, `israeli-bank`, `data-gov-il` servers).
- **MCP Server Trigger**: exposes an n8n workflow itself as an MCP tool, so external clients (Claude Desktop, Cursor, Windsurf, custom GPTs) can discover and invoke your Morning-invoice-lookup or bank-scraper workflow.

### Step 8: When to Use n8n vs Alternatives

| Criteria | n8n | Make.com | Zapier |
|----------|-----|----------|--------|
| Self-hosting (data residency) | Yes (Docker) | No | No |
| Israeli API nodes | None built-in, use HTTP/Code | Some community | Very few |
| Workflow limit | Unlimited (self-hosted) | Plan-based | Plan-based |
| Code execution | Full JS/Python | Limited JS | Limited |
| AI Agent nodes | 70+ AI, MCP support | AI features | AI features |
| Hebrew UI | No | Partial | No |

Choose n8n when you need self-hosting for Israeli data residency, unlimited automations, or full code access for Israeli API quirks (Hebrew encoding, phone formatting, VAT, allocation numbers).

### Step 9: Workflow JSON Import/Export

n8n workflows are JSON documents. Agents building workflows programmatically must understand the shape:

```json
{
  "name": "Morning daily reconciliation",
  "nodes": [{
    "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 6 * * 0-4" }] } },
    "name": "Schedule Trigger", "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2, "position": [240, 300]
  }],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get Token", "type": "main", "index": 0 }]] }
  }
}
```

- **`nodes`**: each has unique `name` (used as connection key), `type` (e.g. `n8n-nodes-base.httpRequest`), `typeVersion` (must match a version n8n supports), `parameters`, and `position`.
- **`connections`**: keyed by source node name, mapping `main` output to an array of arrays of `{ node, type, index }` targets (double array allows multiple outputs, e.g. IF branches).
- Export via UI Download or `GET /api/v1/workflows/{id}`; import via "Import from File" or `POST /api/v1/workflows`. After importing into n8n 2.0 you must **publish** before it runs. `typeVersion` changes between releases.

### Step 10: Credentials Setup for Israeli APIs

n8n stores secrets in its encrypted credential store, never inline in workflow JSON:

- **Morning (Green Invoice) JWT**: no native credential. Chain HTTP Request nodes; the first calls `/account/token`, later nodes send `Authorization: Bearer {{token}}` via Header Auth or an expression. Token expires after 60 minutes, so refresh per execution.
- **Israeli SMS gateways (019, InforUMobile)**: Header Auth credential, name `Authorization`, value `Bearer <token>`.
- **Payment gateways (Cardcom, Tranzila, Grow)**: store merchant IDs / API keys as Generic Credential, referenced via `{{$credentials.fieldName}}`. Grow's `multipart/form-data` requests still pull secrets from the credential.
- For self-hosted n8n, set a stable `N8N_ENCRYPTION_KEY` so the credential store survives restarts.

## Examples

### Example 1: Connect Morning to n8n for daily invoice reconciliation

User: "Every morning, pull yesterday's Morning invoices and flag any still unpaid."

1. **Schedule Trigger** (`scheduleTrigger`): cron `0 6 * * 0-4` (09:00 Israel winter, Sun-Thu).
2. **HTTP Request, "Get Token"**: `POST /api/v1/account/token` with `{ id, secret }`. Output: JWT.
3. **HTTP Request, "Search Documents"**: `POST /api/v1/documents/search` with `Authorization: Bearer {{$json.token}}`, body filtering `fromDate`/`toDate` to yesterday and `type` to 305/320.
4. **IF node**: branch on `status` (open vs closed).
5. **HTTP Request (SMS) or Send Email**: notify bookkeeper, Hebrew body wrapped in `<div dir="rtl">`.

Wrap the whole flow with the Shabbat check from Step 4 if it must never run on a holiday weekday.

### Example 2: Bank transactions to a Google Sheet, holiday-aware

User: "Scrape my business account nightly and append new transactions to a sheet, but skip Shabbat and holidays."

1. **Schedule Trigger**: cron for a weeknight time.
2. **HTTP Request (Hebcal)** + **Code (Shabbat check)** from Step 4.
3. **Code node**: run `israeli-bank-scrapers` via `createScraper()` (Step 2), one item per transaction.
4. **Code node**: normalize Hebrew descriptions, format amounts with `Intl.NumberFormat('he-IL', ...)`, parse DD/MM/YYYY dates.
5. **Google Sheets** (Append): write rows.
6. Separate **Error Trigger** workflow catches failed runs (see Gotchas).

## Recommended MCP Servers

- **hebcal**: Hebrew/Jewish calendar and Shabbat times, alternative to calling Hebcal HTTP in every workflow.
- **israeli-bank**: Israeli bank account data; lets an agent pull transactions without running `israeli-bank-scrapers` in a Code node.
- **data-gov-il**: Israeli government open data (CKAN), query registries without hand-building HTTP Request nodes.

## Reference Links

| Source | URL |
|--------|-----|
| n8n Documentation | https://docs.n8n.io/ |
| n8n 2.0 Breaking Changes | https://docs.n8n.io/2-0-breaking-changes/ |
| n8n Block Access to Nodes | https://docs.n8n.io/hosting/securing/blocking-nodes/ |
| Morning (Green Invoice) API | https://www.greeninvoice.co.il/api-docs |
| Hebcal API | https://www.hebcal.com/home/developer-apis |
| data.gov.il CKAN API | https://data.gov.il/api/3 |

## Gotchas

- **Agents pin `:latest` or an old 1.x tag.** Versions before 2.10.1 / 1.121.0 are vulnerable to Ni8mare (CVE-2026-21858, CVSS 10.0) plus the March 2026 chain (CVE-2026-27493 + CVE-2026-27577). Any public Webhook node makes the host exploitable. Pin >= 2.10.1 (current stable 2.21.x).
- **Agents default to UTC for schedule triggers.** Israel uses `Asia/Jerusalem` (UTC+2/+3); DST runs Friday-before-last-Sunday-of-March through last Sunday of October. Always set `GENERIC_TIMEZONE` and verify timing after every DST change.
- **Agents format dates as MM/DD/YYYY.** Israeli docs use DD/MM/YYYY. Morning returns ISO 8601, but government datasets often return DD/MM/YYYY as strings.
- **Agents send Israeli phone numbers with leading zero.** SMS gateways require `972XXXXXXXXX`. `050-1234567` becomes `972501234567`.
- **Agents assume VAT is included.** Israeli invoices often show amounts before VAT (lifnei maam). Morning returns both `amount` (before VAT) and `totalAmount` (with VAT). Current VAT is 18% (2026).
- **Agents miss that Shabbat times vary by city.** Candle lighting: Jerusalem 40 min before sunset, Haifa/Zikhron Ya'akov 30 min, Tel Aviv and all other cities 18 min. A single hardcoded time will cause runs during Shabbat in some cities.
- **Execute Command node is disabled by default in n8n 2.0.** If your workflow used it for bank scraping it silently fails after upgrade. Migrate to Code nodes or re-enable via `NODES_EXCLUDE` (there is NO `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable, that is a hallucination).
- **Morning amounts are shekels, not agorot.** `price: 50` = 50 NIS. Different from some Israeli payment gateways that use agorot.
- **Invoice Reform 2026 threshold drops June 1, 2026.** Invoices over the threshold (10K NIS through May 31, 5K NIS from June 1) created via API require allocation numbers from the Tax Authority. Make the threshold a workflow variable, not a hardcoded literal.
- **n8n editor keyboard shortcuts break under Hebrew layout.** Canvas reads `e.key` instead of `e.code`, so `Ctrl+C` produces `e.key = 'ב'` and shortcuts fail. Switch input to English while editing, or use menu actions. Tracked in n8n GitHub issue #12569.
- **n8n's expression editor has no RTL support.** Hebrew renders left-to-right. For long Hebrew literals, store them in env vars or static workflow data and reference by name.
- **Unattended workflows fail silently without an Error Trigger.** A scheduled scrape or sync that throws just stops. Create a separate workflow starting with an Error Trigger node that sends a Hebrew alert to Slack/SMS. For transient failures (Cloudflare, expired tokens, rate limits), enable per-node Retry On Fail with a sensible wait.

## Bundled Resources

### References
- `references/israeli-api-endpoints.md` -- Israeli API endpoint reference (Morning, data.gov.il, SMS gateways, payment gateways, Hebcal).
- `references/shabbat-cron-patterns.md` -- Pre-built Shabbat-aware scheduling patterns with Hebcal integration.
- `references/webhook-auth-patterns.md` -- HMAC signature verification + JWT claim validation Code-node snippets.

## Troubleshooting

### Morning (Green Invoice) API returns 401 Unauthorized
JWT expired (60 min TTL). Add a token refresh step at the start of every execution. Store the token in `$getWorkflowStaticData('global')` with a timestamp and refresh if older than 55 min.

### Hebrew text appears garbled in CSV export
Missing UTF-8 BOM, so Excel reads it as ANSI. Prepend `'﻿'` to CSV content, or set Spreadsheet File encoding to UTF-8-BOM.

### Webhook not receiving Cardcom callbacks
Cardcom needs the callback URL publicly accessible with valid SSL. Use nginx/Caddy + Let's Encrypt. Ensure `WEBHOOK_URL` matches the public URL. Whitelist n8n's IP in the Cardcom dashboard.

### Schedule Trigger runs during Shabbat despite Hebcal check
Server timezone is UTC, not Asia/Jerusalem. Verify `GENERIC_TIMEZONE=Asia/Jerusalem`, restart n8n, and log `new Date().toString()` in a Code node to confirm.

### israeli-bank-scrapers fails in Code node
n8n 2.0 runs Code in an isolated task runner; the package and Puppeteer/Playwright may not be available. Install it in the runner env. Give the container >= 1GB memory for Chromium. Execute Command (legacy approach) is disabled by default in 2.0.

### Cloudflare blocks bank scraper for Amex/Isracard
Switch to the maintained fork: `npm install @sergienko4/israeli-bank-scrapers` (uses Camoufox).
