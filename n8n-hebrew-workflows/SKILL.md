---
name: n8n-hebrew-workflows
description: Build n8n 2.x automation workflows (stable 2.32) with Israeli API integrations including Morning (Green Invoice), EZCount, israeli-bank-scrapers, data.gov.il, SMS gateways, Cardcom v11, Tranzila v2, Grow by Meshulam. Use when user asks to "create n8n workflow for Israeli business", "connect Morning to n8n", "automate hashbonit", "Shabbat-aware schedule trigger", "n8n AI agent", or integrate Israeli payment gateways. Covers Hebrew data handling, NIS formatting, Hebcal scheduling, n8n 2.x security patches (CVE-2026-44789 chain), AI Agent nodes with LangChain + RAG, MCP Client Tool and MCP Server Trigger, Israel Invoice Reform 2026 (allocation numbers, 5,000 NIS threshold from June 2026). Do NOT use for invoice management outside an n8n workflow (use green-invoice-il), general n8n tutorials without Israeli context, or Hebrew NLP (use hebrew-nlp-toolkit).
license: MIT
allowed-tools: Bash(n8n:*) Bash(curl:*) Bash(node:*) Bash(npx:*) Bash(docker:*)
compatibility: Requires n8n 2.32.1 or later (patches the CVE-2026-44789/44790/44791 chain); current stable 2.32.7. Node.js 22.22.2+ for israeli-bank-scrapers. Docker recommended for self-hosting. Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Gemini CLI.
---

# n8n Hebrew Workflows

## Instructions

### Step 1: Identify the Automation Pattern

Map the user's Israeli business need to an n8n workflow pattern:

See the field reference in `references/israeli-api-endpoints.md`.

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
| **Jun 1, 2026 onwards** | **5,000 NIS** |

**The threshold is measured BEFORE VAT** (the Tax Authority sets it lifnei maam). Compare it against Morning's `amount` field, NOT `totalAmount`. At 18% VAT the two differ by a 900 NIS band around the 5,000 NIS line, so comparing the wrong field misclassifies invoices in that range.

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

n8n has no native Israeli bank node. Use a Code node to run `israeli-bank-scrapers` programmatically (it is a Node.js library, NOT a CLI). Requires Node.js >= 22.22.2.

Two n8n 2.x settings are required before this runs at all (see Step 6): `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` so `require()` resolves, and credentials pulled from the credential store rather than `$env` (Code-node env access is blocked by default in 2.x).

```javascript
const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');
const scraper = createScraper({
  companyId: CompanyTypes.hapoalim,
  startDate: new Date('2026-01-01'),
  combineInstallments: false,
  showBrowser: false
});
// Hapoalim's login fields are userCode + password. Other banks differ, see below.
const password = BANK_PASS; // Hapoalim uses userCode + password
const result = await scraper.scrape({ userCode: BANK_USER, password });
if (!result.success) throw new Error(`${result.errorType}: ${result.errorMessage}`);
return result.accounts.flatMap(a => a.txns.map(txn => ({ json: txn })));
```

Supported scrapers (`CompanyTypes` members): hapoalim, leumi, discount, mercantile, mizrahi, otsarHahayal, beinleumi, union, massad, yahav, behatsdaa, beyahadBishvilha, oneZero, pagi, visaCal, max (formerly Leumi Card), isracard, amex.

**Login fields vary per bank.** There is no universal credential shape. See the per-bank table in `references/israeli-api-endpoints.md`; read `SCRAPERS[companyId].loginFields` before wiring credentials.
**Cloudflare blocking (2026):** Cloudflare's bot detection blocks headless browsers on Amex and Isracard. The maintained fork `@sergienko4/israeli-bank-scrapers` uses Camoufox as a workaround: `npm install @sergienko4/israeli-bank-scrapers`.

Store credentials in n8n's credential store, never in workflow JSON.

#### data.gov.il CKAN API

```
GET https://data.gov.il/api/3/action/datastore_search?resource_id=<guid>&q=<term>&limit=100
```

Useful resource IDs: Non-Profit Registry (`be5b7935-3922-45d4-9638-08871b17ec95`) for registered amutot; trade statistics by HS code (various IDs). The API returns Hebrew field names; use a Code node to normalize keys to English before downstream processing.

#### Israeli SMS Gateways

| Gateway | Host | Auth | Best For |
|---------|------|------|----------|
| 019 Telzar | `019sms.co.il` | Bearer token, or username + password | Bulk marketing, transactional |
| InforUMobile | `capi.inforu.co.il` | Bearer token (IP allowlist enforced) | OTP, transactional |
| Nexmo/Vonage IL | `rest.nexmo.com` | API key + secret | International + local |

019 Telzar example:

```
POST https://019sms.co.il/api
Headers: Authorization: Bearer {{$env.SMS_019_TOKEN}}
Body: { "from": "MyBusiness", "to": "{{$json.phone}}", "message": "{{$json.text}}" }
```

**019 returns HTTP 200 even when the send fails.** An auth failure comes back as `200 {"status":3,"message":"Username or password is incorrect or Expired and API token is invalid"}`, so an HTTP Request node with default settings treats it as success and the workflow continues with no SMS delivered. Enable **Always Output Data** on the node and branch on `$json.status` (0 = sent) with an IF node, not on the HTTP status code.

InforUMobile enforces an IP allowlist in addition to the token: a request from an unlisted IP returns `401 {"StatusId": -2, "StatusDescription": "Authentication failed or illegal IP address"}`. Whitelist your n8n egress IP in the InforU dashboard alongside Cardcom and Tranzila (Step 5).

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

For Jewish holidays, query `https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=x&maj=on&mod=on&i=on` and filter for `yomtov: true`. Consult `references/shabbat-cron-patterns.md` for pre-built patterns.

Both parameters are load-bearing:

- **`month=x`, not `month=now`.** `month=now` is not a valid Hebcal parameter. It returns HTTP 200 with `"items": []`, so a `.some(i => i.yomtov)` gate evaluates false and the workflow runs on Yom Kippur with no error anywhere. Use `month=x` for the whole year, or a numeric month.
- **`i=on` selects the Israel schedule.** Without it Hebcal defaults to Diaspora, which returns 13 yomtov days for 2026 instead of Israel's 8. The five extra days (Pesach II, Pesach VIII, Shavuot II, Sukkot II, Simchat Torah) are ordinary working days in Israel, so a Diaspora-gated workflow shuts the business down five times a year for no reason. Passing an Israeli `geonameid` has the same effect as `i=on`.

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

For modern integrations, use the Cardcom API v11. `https://secure.cardcom.solutions/api/v11` is the **base path**, not a callable endpoint (it returns 404 on its own); append the operation, for example `POST https://secure.cardcom.solutions/api/v11/LowProfile/Create` to open a hosted payment page or `POST .../api/v11/Transactions/Transaction` for a direct charge. v11 also lets you register webhooks for document-creation events. URLs must be HTTPS and publicly routable (no `localhost`; use ngrok or Cloudflare Tunnel in dev). Full docs: `https://secure.cardcom.solutions/api/v11/DOCS`.

#### Tranzila

Tranzila callbacks deliver GET parameters:

```
https://your-n8n.example.com/webhook/tranzila-callback?Response=000&index=12345&sum=100.00&currency=1
```

`Response=000` is approved. Currency: `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR. `Rone` = installments.

**Tranzila API v2** offers modern server-to-server (SAQ-D) plus iframe / hosted fields. Authentication uses an `X-tranzila-api-app-key` header (header confirmed via Stoplight API explorer at docs.tranzila.com). v2 supports Bit, tokenization, recurring billing, refunds, and 3D Secure (mandatory under SHVA rules). Prefer v2 over the legacy CGI pattern (`tranzila31.cgi`; the older `tranzila71dl.cgi` now 404s). Bit flow: server calls Tranzila v2, response includes a URL to embed in an iframe (QR code + phone push). See `https://docs.tranzila.com/` for the v2 documentation.

#### Grow by Meshulam

Grow sends webhooks as POST. **Important:** the Grow API uses `multipart/form-data` (not JSON). After receiving a webhook, call `approveTransaction` to finalize the payment.

Webhook payload includes: `webhookKey`, `transactionCode`, `transactionType`, `asmachta` (transaction reference), `paymentSum`, `paymentDate`, `fullName`, `payerPhone`, `payerEmail`, `cardSuffix`, `cardBrand`, `paymentsNum`.

#### Bit Payments

Bit is Israel's most popular mobile payment method, available through Tranzila (API v2) and Grow by Meshulam, not as a standalone API. Via Tranzila v2: create a payment page with `bit: true`; the customer scans a QR code or is redirected to Bit. Via Grow: enable Bit in the merchant dashboard; Bit transactions appear in the same webhook flow with a different `transactionType`.

#### Webhook Authentication

n8n's Webhook node supports four auth modes: None, Basic Auth, Header Auth, JWT Auth. Given the 2026 unauthenticated-webhook CVE history, the "None" mode on a publicly-routable webhook is effectively a vulnerability; use Header Auth (default for Israeli SMS callbacks), Basic Auth (private/VPN), or JWT Auth (cross-org).

n8n has no built-in HMAC verifier and no automatic `exp`/`iss`/`aud` claim validation on JWTs. See `references/webhook-auth-patterns.md` for HMAC verification and JWT claim-validation Code-node snippets.

**IP whitelisting:** Cardcom and Tranzila require your webhook server's IP to be whitelisted. If self-hosting, use a static IP or a reverse proxy with a fixed egress IP.

### Step 6: Self-Hosting Considerations

#### n8n 2.x Security Patches and Breaking Changes

n8n 2.0 shipped in December 2025; current stable is 2.32.7 as of August 2026 (beta on 2.33.x, new minor most weeks). Pin a specific tag in production, never `n8nio/n8n:latest`.

**CRITICAL security patch (pin >= 2.32.1).** Three CRITICAL vulnerabilities were disclosed 2026-05-14 and patched in 2.22.1:

| CVE | GHSA | Impact |
|-----|------|--------|
| CVE-2026-44789 | GHSA-c8xv-5998-g76h | HTTP Request node pagination prototype pollution **to RCE** |
| CVE-2026-44790 | GHSA-57g9-58c2-xjg3 | Arbitrary file read via Git node |
| CVE-2026-44791 | GHSA-wrwr-h859-xh2r | XML node prototype pollution patch bypass |

CVE-2026-44789 sits on this skill's critical path: every Israeli integration here is an HTTP Request node. Further HIGH-severity fixes landed through 2.31.5 and 2.32.1 (credential exfiltration via shared workflows, cross-tenant credential takeover, expression sandbox escapes), so **2.32.1 is the practical minimum** and 2.32.7 is the current stable.

Two earlier issues are often cited and frequently misdescribed:

- **CVE-2026-21858 ("Ni8mare", CVSS 10.0), published 2026-01-07** is unauthenticated **file access** via improper webhook request handling, not RCE. It affects 1.65.0 through 1.120.x only and was patched in 1.121.0. **The 2.x line was never affected**, so it is not a reason to pin any 2.x version.
- **CVE-2026-27493 (CVSS 9.5) + CVE-2026-27577 (CVSS 9.4), published 2026-02-25** are the pair that motivates the 2.10.1 floor: unauthenticated expression injection via Form nodes plus an expression sandbox escape to RCE, affecting <1.123.22, 2.0.0-2.9.2 and 2.10.0, patched in 1.123.22 / 2.9.3 / 2.10.1. That floor is now superseded by the 2.32.1 requirement above.

Any public Webhook node (every payment-gateway workflow in this skill) widens the exposure of all of these.

Key n8n 2.0 changes affecting Israeli workflows:

| Change | Impact | Action |
|--------|--------|--------|
| Code-node `$env` access blocked by default | Every `$env.BANK_PASS` / `$env.WEBHOOK_HMAC_SECRET` read returns nothing | Move secrets to the credential store, or set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` |
| `require()` restricted in Code nodes | `require('crypto')` and `require('israeli-bank-scrapers')` both fail | Set `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL` |
| Execute Command node disabled by default | Bank-scraper workflows using Execute Command break | Use Code node, or re-enable via `NODES_EXCLUDE` |
| Save/Publish model | Workflows must be explicitly published | Publish after import or creation |
| Task runner isolation for Code nodes | Code runs in isolated sandboxes | Set the module vars on the **runner**, not the main container |
| Python Code node rebuilt on task runners | Pyodide-based Python removed; native Python needs runners in external mode | Set up external-mode task runners, or use JavaScript |
| MySQL/MariaDB support removed | Cannot use them as n8n backend DB | Migrate to PostgreSQL or SQLite |

**Code node module access.** n8n disables `require()` for external modules unless the variable is set, and this skill needs both:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

Without the first, the HMAC webhook verifier in `references/webhook-auth-patterns.md` throws on `require('crypto')`. Without the second, the bank-scraper Code node throws on `require('israeli-bank-scrapers')`. **If task runners are enabled (the default in 2.0), set these on the task runner, not on the main n8n container** or they have no effect.

**Code node secrets.** `N8N_BLOCK_ENV_ACCESS_IN_NODE` defaults to `true` in 2.x, so `$env.*` inside a Code node returns nothing. Prefer moving bank and HMAC secrets into the credential store (n8n's own migration guidance for this change); set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` only if you must keep the `$env` pattern.

To re-enable Execute Command, override `NODES_EXCLUDE` so it no longer contains `n8n-nodes-base.executeCommand` (empty list works), then restart n8n:

```
NODES_EXCLUDE="[]"
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
    # Must be >= 2.32.1 to be patched for the CVE-2026-44789/44790/44791 critical chain.
    image: n8nio/n8n:2.32.7
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
- If Code nodes need `require()` or `$env`, add `NODE_FUNCTION_ALLOW_BUILTIN`, `NODE_FUNCTION_ALLOW_EXTERNAL` and (only if needed) `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` to the task-runner service rather than here.

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
| n8n 2.0 Breaking Changes | https://docs.n8n.io/changelog/v20-breaking-changes |
| n8n Enable Modules in Code Node | https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-modules-in-code-node |
| n8n Block Access to Nodes | https://docs.n8n.io/hosting/securing/blocking-nodes/ |
| Morning (Green Invoice) API | https://www.greeninvoice.co.il/api-docs |
| Hebcal API | https://www.hebcal.com/home/developer-apis |
| data.gov.il CKAN API | https://data.gov.il/api/3 |

## Gotchas

- **Agents pin `:latest` or a stale 2.1x/2.2x tag.** 2.21.4 alone carries 68 published advisories, including three CRITICAL (CVE-2026-44789 HTTP Request node prototype pollution to RCE, CVE-2026-44790 Git node arbitrary file read, CVE-2026-44791 XML node patch bypass) fixed in 2.22.1, plus HIGH-severity credential-exfiltration fixes landing through 2.31.5 and 2.32.1. Any public Webhook node widens the exposure. Pin >= 2.32.1; current stable is 2.32.7.
- **Agents cite CVE-2026-21858 as a reason to pin a 2.x version.** It is unauthenticated file access, not RCE, and it affects only 1.65.0 through 1.120.x. The 2.x line was never affected. The 2.10.1 floor comes from CVE-2026-27493 + CVE-2026-27577 (published 2026-02-25), and is itself superseded by the 2.32.1 requirement.
- **Agents read secrets with `$env` inside Code nodes.** Blocked by default in 2.x (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`), so the read silently yields nothing and the node fails on undefined credentials. Use the credential store.
- **Agents call `require()` in a Code node without allowlisting the module.** `require('crypto')` needs `NODE_FUNCTION_ALLOW_BUILTIN=crypto`; `require('israeli-bank-scrapers')` needs `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers`. With task runners on (the 2.0 default) both go on the runner, not the main container.
- **Agents pass `userPassword` to `israeli-bank-scrapers`.** The key is `password`, and the first field is per-bank: `userCode` for Hapoalim, `username` for Leumi/Mizrahi/Max, `id` + `num` for Discount/Mercantile, `id` + `card6Digits` for Isracard/Amex. There is no universal shape.
- **Agents default to UTC for schedule triggers.** Israel uses `Asia/Jerusalem` (UTC+2/+3); DST runs Friday-before-last-Sunday-of-March through last Sunday of October. Always set `GENERIC_TIMEZONE` and verify timing after every DST change.
- **Agents format dates as MM/DD/YYYY.** Israeli docs use DD/MM/YYYY. Morning returns ISO 8601, but government datasets often return DD/MM/YYYY as strings.
- **Agents send Israeli phone numbers with leading zero.** SMS gateways require `972XXXXXXXXX`. `050-1234567` becomes `972501234567`.
- **Agents assume VAT is included.** Israeli invoices often show amounts before VAT (lifnei maam). Morning returns both `amount` (before VAT) and `totalAmount` (with VAT). Current VAT is 18% (2026).
- **Agents miss that Shabbat times vary by city.** Candle lighting: Jerusalem 40 min before sunset, Haifa/Zikhron Ya'akov 30 min, Tel Aviv and all other cities 18 min. A single hardcoded time will cause runs during Shabbat in some cities.
- **Execute Command node is disabled by default in n8n 2.0.** If your workflow used it for bank scraping it silently fails after upgrade. Migrate to Code nodes or re-enable via `NODES_EXCLUDE` (there is NO `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable, that is a hallucination).
- **Morning amounts are shekels, not agorot.** `price: 50` = 50 NIS. Different from some Israeli payment gateways that use agorot.
- **Invoice Reform 2026 threshold drops June 1, 2026.** Invoices over the threshold (10K NIS through May 31, 5K NIS from June 1) created via API require allocation numbers from the Tax Authority. The threshold is measured **before VAT**, so compare it against Morning's `amount`, not `totalAmount`. Make the threshold a workflow variable, not a hardcoded literal.
- **Agents build the Hebcal holiday gate with `month=now` and no `i=on`.** `month=now` is invalid and returns an empty `items` array (HTTP 200, no error), so the gate never fires. Omitting `i=on` returns the Diaspora calendar, which halts Israeli workflows on five days that are ordinary working days here. Use `month=x&i=on`.
- **Agents trust the HTTP status from Israeli SMS gateways.** 019 returns HTTP 200 with `status: 3` on auth failure. Branch on the body field, not the status code.
- **Agents assume one webhook equals one payment.** Cardcom, Tranzila and Grow all retry webhooks. Deduplicate on `InternalDealNumber` / `index` / `asmachta` before creating a document, or a retry issues a duplicate invoice and requests a second allocation number from SHAAM.
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
Three separate causes, in the order they bite:

1. `require()` is blocked. Set `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` **on the task runner** (n8n 2.0 enables runners by default, and the variable has no effect on the main container in that setup).
2. Credentials come back undefined. `$env` is blocked inside Code nodes in 2.x (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`). Pull them from the credential store instead.
3. Wrong credential keys. The key is `password`, not `userPassword`, and the first field is per-bank (`userCode` for Hapoalim). See the login-fields table in Step 2.

Also install the package and its Puppeteer/Playwright dependency in the runner image, and give the container >= 1GB memory for Chromium. Execute Command (legacy approach) is disabled by default in 2.0.

### Cloudflare blocks bank scraper for Amex/Isracard
Switch to the maintained fork: `npm install @sergienko4/israeli-bank-scrapers` (uses Camoufox).
