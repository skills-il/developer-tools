---
name: n8n-hebrew-workflows
description: Build and optimize n8n automation workflows with Israeli API integrations including Green Invoice, israeli-bank-scrapers, data.gov.il, and Israeli SMS gateways. Use when user asks to "create n8n workflow for Israeli business", "connect Green Invoice to n8n", "automate hashbonit", "tazrim avoda b'ivrit", "set up Shabbat-aware cron", or integrate Israeli payment gateways (Cardcom, Tranzila, Grow/Meshulam) into n8n flows. Covers Hebrew data handling in Function nodes, NIS currency formatting, Shabbat/holiday-aware scheduling via Hebcal API, and self-hosting on Israeli cloud with data residency compliance. Do NOT use for general n8n tutorials without Israeli context (use n8n official docs), standalone invoice management (use green-invoice-il), or Hebrew NLP tasks (use hebrew-nlp-toolkit).
license: MIT
allowed-tools: Bash(n8n:*) Bash(curl:*) Bash(node:*) Bash(npx:*) Bash(docker:*)
compatibility: Requires n8n instance (self-hosted or n8n Cloud). Node.js 18+ for custom nodes. Docker recommended for self-hosting. Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex.
---

# n8n Hebrew Workflows

## Instructions

### Step 1: Identify the Automation Pattern

Map the user's Israeli business need to an n8n workflow pattern. Use this table to select the right architecture before building anything:

| Business Need | n8n Pattern | Key Nodes | Israeli API |
|--------------|-------------|-----------|-------------|
| Invoice reconciliation | Cron -> HTTP -> Compare -> Update | Cron, HTTP Request, IF, Function | Green Invoice API |
| Bank transaction categorization | Cron -> Code -> Spreadsheet | Cron, Execute Command, Google Sheets | israeli-bank-scrapers |
| Government data sync | Cron -> HTTP -> Transform -> DB | Cron, HTTP Request, Function, Postgres | data.gov.il CKAN API |
| SMS notifications | Trigger -> Function -> HTTP | Webhook, Function, HTTP Request | 019 SMS / Inforu API |
| Payment webhook handling | Webhook -> Validate -> Process | Webhook, IF, Function, HTTP Request | Cardcom / Tranzila / Grow |
| Holiday-aware scheduling | Cron -> HTTP -> IF -> Execute | Cron, HTTP Request, IF, Function | Hebcal API |
| Multi-step approval flow | Webhook -> Wait -> IF -> Notify | Webhook, Wait, IF, HTTP Request | Slack + SMS gateway |

**Decision criteria for choosing between patterns:**
- If the flow runs on a schedule, start with a Cron trigger and consider Shabbat/holiday pausing (Step 4)
- If the flow responds to external events (payment confirmations, form submissions), start with a Webhook trigger
- If the flow processes Hebrew text, add a Function node early in the pipeline for encoding/RTL handling (Step 3)

### Step 2: Connect Israeli APIs in n8n

#### Green Invoice API

Green Invoice (hashbonit yeruka) uses OAuth2 with API key + secret. Configure the HTTP Request node:

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

Store the JWT token from the response and pass it to subsequent requests:

```
Authorization: Bearer {{$json.token}}
```

Common Green Invoice endpoints for n8n workflows:

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/api/v1/documents/search` | POST | Search invoices by date range, client, status |
| `/api/v1/documents` | POST | Create new invoice/receipt |
| `/api/v1/clients/search` | POST | Look up client by name or tax ID (osek number) |
| `/api/v1/payments` | GET | Fetch payment records for reconciliation |
| `/api/v1/businesses/me` | GET | Get current business info (company name, tax ID) |

Consult `references/israeli-api-endpoints.md` for full endpoint details, required fields, and response schemas.

#### israeli-bank-scrapers via Execute Command

n8n does not have a native Israeli bank node. Use the Execute Command node to run `israeli-bank-scrapers`:

```bash
npx israeli-bank-scrapers --company $BANK_NAME --id $USER_ID --password $PASSWORD --output json
```

Supported banks: hapoalim, leumi, discount, mizrahi, otsarHahayal, beinleumi, massad, yahav, beyahadMishkantaot, oneZero, behatsdaa.

**Security note:** Store credentials in n8n's credential store, not in workflow JSON. Use environment variables for sensitive values. The `--save-to-file` option writes to the n8n container's filesystem, so mount a volume if persistence is needed.

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
| Companies Registry | 8f714b7f-c35c-4b40-a0e0-55b6ac4ae2d2 | Registered Israeli companies |
| Non-Profit Registry | be5b7935-3922-45d4-9638-08871b17ec95 | Registered amutot (non-profits) |
| Import/Export Stats | Various | Trade statistics by HS code |

The API returns Hebrew field names. Use a Function node to normalize keys to English for downstream processing.

#### Israeli SMS Gateways

| Gateway | API Type | Auth | Best For |
|---------|----------|------|----------|
| 019 SMS (InfruSMS) | REST | API key + secret | Bulk marketing, transactional |
| Inforu (SMSGlobal IL) | REST | Username + token | OTP, transactional, WhatsApp |
| Nexmo/Vonage IL | REST | API key + secret | International + local |

019 SMS example in an HTTP Request node:

```
Method: POST
URL: https://www.019sms.co.il/api
Headers:
  Content-Type: application/json
Body:
{
  "user": "{{$env.SMS_019_USER}}",
  "password": "{{$env.SMS_019_PASS}}",
  "from": "MyBusiness",
  "to": "{{$json.phone}}",
  "message": "{{$json.text}}"
}
```

Israeli phone number formatting: Always send in international format `972XXXXXXXXX` (drop the leading 0). A Function node before the SMS node should handle this:

```javascript
const phone = $input.first().json.phone;
const formatted = phone.startsWith('0')
  ? '972' + phone.slice(1)
  : phone.startsWith('+972')
    ? phone.slice(1)
    : phone;
return [{ json: { ...items[0].json, phone: formatted } }];
```

### Step 3: Handle Hebrew Data in n8n Nodes

#### RTL Text in Function Nodes

n8n Function nodes process strings as UTF-8, so Hebrew works natively. The problems arise at boundaries: API responses, CSV exports, email templates.

**Common Hebrew data issues and fixes:**

| Issue | Where It Happens | Fix |
|-------|-----------------|-----|
| Reversed Hebrew in CSV | Spreadsheet File node export | Set encoding to UTF-8-BOM in output options |
| Broken nikud (vowels) | HTTP Request response parsing | Set response encoding to UTF-8 explicitly |
| Mixed RTL/LTR in emails | Send Email node | Wrap Hebrew text in `<div dir="rtl">` |
| Hebrew JSON keys | data.gov.il API responses | Normalize keys in Function node before processing |
| Truncated Hebrew | String length checks | Use `Array.from(str).length` for character count, not `.length` |

#### NIS Currency Formatting

Use this Function node snippet for proper Israeli Shekel formatting:

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

For agorot (cents) precision in financial workflows, always work in agorot internally (integers) and convert to shekels only at display:

```javascript
const amountInAgorot = Math.round(shekelAmount * 100);
// All calculations in agorot
const totalAgorot = amountInAgorot + taxAgorot;
// Convert back for display
const displayAmount = formatNIS(totalAgorot / 100);
```

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

### Step 4: Shabbat-Aware Cron Scheduling

Business workflows in Israel must not run during Shabbat (Friday sundown to Saturday sundown) and Jewish holidays. n8n's built-in cron does not support this, so build a check node at the start of every scheduled workflow.

**Architecture:** Cron Trigger -> HTTP Request (Hebcal) -> IF (is Shabbat?) -> Continue or Stop

Hebcal API call in an HTTP Request node:

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` is Tel Aviv. Other common cities:

| City | Geoname ID |
|------|-----------|
| Jerusalem | 281184 |
| Tel Aviv | 293397 |
| Haifa | 294801 |
| Beer Sheva | 295530 |

The response includes candle lighting and havdalah times. Use a Function node to determine if the current time falls within Shabbat:

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

Validation Function node after the Webhook:

```javascript
const data = $input.first().json;

if (data.ReturnValue !== '0') {
  // Transaction failed
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

#### Tranzila

Tranzila uses a different callback pattern. The callback URL receives GET parameters:

```
https://your-n8n.example.com/webhook/tranzila-callback?Response=000&index=12345&sum=100.00&currency=1
```

| Field | Description | Values |
|-------|-------------|--------|
| `Response` | Status code | `000` = approved, `001`-`999` = error codes |
| `index` | Transaction index | Numeric |
| `sum` | Amount charged | Decimal (NIS if `currency=1`) |
| `currency` | Currency code | `1` = ILS, `2` = USD, `3` = EUR |
| `Rone` | Installments | Number |

#### Grow (Meshulam)

Grow sends JSON POST to your webhook:

```json
{
  "transaction_id": "abc123",
  "status": "success",
  "amount": 150.00,
  "currency": "ILS",
  "payments_number": 3,
  "customer": {
    "name": "ישראל ישראלי",
    "email": "israel@example.com",
    "phone": "0501234567"
  }
}
```

**IP whitelisting:** Cardcom and Tranzila require your webhook server's IP to be whitelisted in their dashboard. If self-hosting n8n, use a static IP or configure a reverse proxy with a fixed egress IP.

### Step 6: Self-Hosting Considerations

#### Israeli Cloud Options

| Provider | Data Residency | n8n Support | Notes |
|----------|---------------|-------------|-------|
| AWS (il-central-1) | Israel (Tel Aviv) | Full Docker support | Local zone launched 2023, full region available |
| Azure (Israel Central) | Israel | Full Docker support | israelcentral region |
| Google Cloud (me-west1) | Israel (Tel Aviv) | Full Docker support | Launched 2022 |
| Kamatera | Israel (Petah Tikva DC) | VPS with Docker | Israeli company, NIS billing |
| CloudSpace IL | Israel | VPS with Docker | Israeli company, local support |

**Data residency compliance:** Israeli Privacy Protection Authority (PPPA, rashut le-haganat ha-prat) regulations require personal data of Israeli citizens to remain within approved jurisdictions. For workflows that process PII (teudat zehut numbers, bank details, medical data), choose a provider with an Israeli data center.

#### Docker Compose for Self-Hosted n8n

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
    volumes:
      - n8n_data:/home/node/.n8n
      - ./scripts:/home/node/scripts

volumes:
  n8n_data:
```

**Critical:** Set `GENERIC_TIMEZONE=Asia/Jerusalem` and `TZ=Asia/Jerusalem`. Without this, all cron triggers use UTC, and Shabbat calculations will be off by 2-3 hours (Israel is UTC+2 in winter, UTC+3 in summer with DST changes on different dates than US/EU).

## Gotchas

- **Agents default to UTC for cron expressions.** Israel uses `Asia/Jerusalem` (UTC+2/+3), and Israeli DST transitions happen on different dates than US/EU. Always set `GENERIC_TIMEZONE` in n8n config and verify cron timing after every DST change (typically last Friday of March and last Sunday of October).
- **Agents format dates as MM/DD/YYYY.** Israeli documents, APIs, and users universally use DD/MM/YYYY. Every date parsing Function node must explicitly handle this. Green Invoice API returns ISO 8601, but government datasets often return DD/MM/YYYY as strings.
- **Agents send Israeli phone numbers with leading zero.** SMS gateway APIs require international format (`972XXXXXXXXX`). A phone number like `050-1234567` must become `972501234567`. Always strip the leading zero and prepend `972`.
- **Agents assume VAT is included in amounts.** Israeli invoices commonly show amounts before VAT (lifnei maam). Green Invoice API returns both `amount` (before VAT) and `totalAmount` (with VAT). Always check which field you need. Current VAT rate is 18% (as of January 2025).
- **Agents miss that Shabbat times vary by city.** Candle lighting in Jerusalem is 40 minutes before sunset, while in Tel Aviv it is 20-30 minutes. Using a single hardcoded time for all of Israel will cause workflows to run during Shabbat in some cities.

## Bundled Resources

### References
- `references/israeli-api-endpoints.md` -- Complete reference table of Israeli API endpoints for n8n workflows, including Green Invoice, data.gov.il, SMS gateways, payment gateways, and Hebcal. Consult when configuring HTTP Request nodes for Israeli services.
- `references/shabbat-cron-patterns.md` -- Pre-built Shabbat-aware scheduling patterns for n8n including weekly, monthly, and holiday-aware configurations with Hebcal API integration. Consult when setting up any cron-triggered workflow that should respect Shabbat and Jewish holidays.

## Troubleshooting

### Error: "Green Invoice API returns 401 Unauthorized"
Cause: JWT token expired. Green Invoice tokens have a short TTL (around 30 minutes).
Solution: Add a token refresh step at the beginning of every workflow execution. Store the token in n8n's static data (`$getWorkflowStaticData('global')`) with a timestamp, and refresh it if older than 25 minutes.

### Error: "Hebrew text appears garbled in CSV export"
Cause: The exported CSV lacks a UTF-8 BOM (Byte Order Mark), so Excel interprets it as ANSI.
Solution: In the Function node that prepares CSV data, prepend the BOM character: `'\uFEFF' + csvContent`. Alternatively, set the Spreadsheet File node's encoding option to UTF-8-BOM.

### Error: "Webhook not receiving Cardcom callbacks"
Cause: Cardcom requires the callback URL to be publicly accessible with a valid SSL certificate. Self-hosted n8n behind a firewall will not receive callbacks.
Solution: Use a reverse proxy (nginx, Caddy) with Let's Encrypt SSL. Ensure the n8n `WEBHOOK_URL` environment variable matches the public URL. Whitelist n8n's IP in the Cardcom merchant dashboard.

### Error: "Cron runs during Shabbat despite Hebcal check"
Cause: n8n server timezone is set to UTC instead of Asia/Jerusalem, so the Shabbat time comparison is offset by 2-3 hours.
Solution: Verify `GENERIC_TIMEZONE=Asia/Jerusalem` in n8n environment variables. Restart n8n after changing timezone settings. Test by logging `new Date().toString()` in a Function node to confirm the server's effective timezone.

### Error: "israeli-bank-scrapers times out in Execute Command node"
Cause: Bank scraping involves headless browser automation which can take 30-60 seconds. n8n's default Execute Command timeout is too short.
Solution: Increase the timeout in the Execute Command node settings (set to 120000ms). Ensure the n8n Docker container has sufficient memory (at least 1GB) for Chromium. Install required dependencies: `apt-get install -y chromium-browser` in the container.
