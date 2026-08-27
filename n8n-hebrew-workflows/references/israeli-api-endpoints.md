# Israeli API Endpoints Reference for n8n

Quick reference for configuring HTTP Request nodes when connecting to Israeli services.

## Morning (formerly Green Invoice) API

Base URL: `https://api.greeninvoice.co.il/api/v1`

Note: The company rebranded from "Green Invoice" to "Morning" (חשבונית ירוקה). The API domain remains `api.greeninvoice.co.il`.

### Authentication

| Step | Method | Endpoint | Body |
|------|--------|----------|------|
| Get token | POST | `/account/token` | `{ "id": "<api_key>", "secret": "<api_secret>" }` |

Authentication is API key + secret -> JWT. This is NOT OAuth2.

Token TTL: 60 minutes. Refresh proactively before expiry.

### Document Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/documents/search` | POST | Search invoices/receipts | `fromDate`, `toDate`, `type`, `status`, `client` |
| `/documents` | POST | Create document | `type`, `client`, `income` (line items array) |
| `/documents/{id}` | GET | Get document by ID | Path parameter: document UUID |
| `/documents/{id}/download/links` | GET | Get download links for the document | Returns URLs, not the binary itself |

There is no endpoint that emails an existing document. Delivery is a property
of creation: pass `emailContent` and `attachment` on `POST /documents`.

### Document Types (type field)

| Code | Type (Hebrew) | Type (English) |
|------|--------------|----------------|
| 10 | הצעת מחיר | Price Quote |
| 305 | חשבונית מס | Tax Invoice |
| 320 | חשבונית מס / קבלה | Tax Invoice / Receipt |
| 330 | חשבונית זיכוי | Credit Note / Refund |
| 400 | קבלה | Receipt |

### Israel Invoice Reform 2026

Tax invoices (type 305, 320) over the threshold require an allocation number (mispar haktza'a) from the Israel Tax Authority via SHAAM clearance. Threshold schedule:

| Effective | Threshold |
|-----------|-----------|
| May 2024 | 25,000 NIS |
| Jan 2025 | 20,000 NIS |
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026 onwards** | **5,000 NIS** |

**Thresholds are before VAT** (lifnei maam). Compare against the `amount` field, NOT `totalAmount`. No further step-down is legislated beyond June 2026.

When creating documents via API, check Morning's documentation for the allocation workflow applicable to API-created documents. Build the threshold as a workflow variable rather than a hardcoded literal.

### Client Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/clients/search` | POST | Search clients | `name`, `taxId`, `email` |
| `/clients` | POST | Create client | `name`, `taxId`, `emails`, `address` |
| `/clients/{id}` | PUT | Update client | Full client object |

### Payment Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/documents/payments/search` | POST | Search payments recorded on documents | `fromDate`, `toDate` |
| `/payments/form` | POST | Create a hosted payment form | |
| `/payments/tokens/search` | POST | Search stored payment tokens | |
| `/payments/tokens/{id}/charge` | POST | Charge a stored token | Path parameter: token ID |

Note there is no `GET /payments` collection; reconciliation goes through
`POST /documents/payments/search`.

### Common Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Document UUID |
| `number` | integer | Document number (sequential) |
| `amount` | number | Amount before VAT (in decimal shekels, NOT agorot) |
| `vat` | number | VAT amount (in decimal shekels) |
| `totalAmount` | number | Amount including VAT (in decimal shekels) |
| `status` | integer | 0=draft, 10=open, 20=closed, 30=canceled |
| `createdAt` | string | ISO 8601 timestamp |
| `client.name` | string | Client name (may be Hebrew) |
| `client.taxId` | string | Israeli tax ID (osek morshe/patur number) |

**Amounts are in decimal shekels.** `amount: 50` means 50.00 NIS. Do not multiply or divide by 100.

---

## EZCount (EasyCount) API

Base URL: `https://api.ezcount.co.il/api`

EZCount is a Morning alternative for SMB invoicing in Israel.

### Authentication

Authentication via `api_key` + `api_email` in the request body (not OAuth, not Bearer).

### Document Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/createDoc` | POST | Create document | `type`, `customer_name`, `item[]`, `api_key`, `api_email` |
| `/getLastAPIRequestData` | GET | Inspect the last API request (debugging) | `debug_key`, `api_key` |
| `/documents/getTaxMinistryAllocationNumber/{DOC_UUID}` | POST | Fetch the SHAAM allocation number | Path parameter: document UUID |

Only the calls above appear in EZCount's published Postman collection
(linked from ezcount.co.il/api). Endpoint names for searching documents,
downloading a PDF, or emailing a document are not documented publicly, and
`/searchDocuments` returns a 404 page. Read the exact names off the API tab
in your own EZCount account (Settings > API) rather than guessing them.

Note when probing this host: unknown paths return HTTP 200 with a
`MULTIPE POST PROBLEM` body rather than a 404, so a 200 here is not evidence
that an endpoint exists.

### Document Type Codes

Same Tax Authority codes as Morning: 10 (price quote), 305 (tax invoice), 320 (tax invoice / receipt), 330 (credit note), 400 (receipt).

### Israel Invoice Reform 2026

EZCount handles the SHAAM allocation request as part of document creation. When the Tax Authority has not (yet) allocated a number, the API returns **HTTP status `417`**, verbatim from the docs: "When the document is waiting for the Tax Authority allocation number we will return status `417`". There is no `allocation_status` field and no retry that clears a 417. The docs give four options at that point: skip the allocation number, cancel the document, file a further objection, or reverse charge (cancel and re-issue at zero-rate VAT, with the buyer issuing a self-invoice). You may also set your own allocation number. Where the status is 417 with error code 460, the Tax Authority's Hebrew refusal text must be surfaced to the document creator. Rate limit: 250 requests per 10 seconds, sequential rather than parallel.

### Common Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation result |
| `errMsg` | string | Error in Hebrew |
| `docNum` | string | Document number |
| `pdfLink` | string | Public PDF URL |
| `allocation_number` | string | SHAAM-issued mispar haktza'a (Invoice Reform 2026) |

**Amounts are in decimal shekels.** Same convention as Morning.

---

## data.gov.il CKAN API

Base URL: `https://data.gov.il/api/3`

### Core Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/action/datastore_search` | GET | Search within a dataset | `resource_id`, `q`, `filters`, `limit`, `offset`, `sort` |
| `/action/package_show` | GET | Get dataset metadata | `id` (dataset name or UUID) |
| `/action/resource_show` | GET | Get resource details | `id` (resource UUID) |
| `/action/datastore_search_sql` | GET | Run SQL against a resource | `sql` |

**`datastore_search_sql` DOES work on data.gov.il.** An earlier version of this
reference stated it was unavailable and that a WAF blocked SQL in the query
string. Both are false: `help_show?name=datastore_search_sql` returns the real
CKAN docstring ("Execute SQL queries on the DataStore"), and a live query
against the amutot resource returns records with HTTP 200. Quote the resource id
and URL-encode the statement:

```
GET https://data.gov.il/api/3/action/datastore_search_sql?sql=SELECT%20*%20FROM%20%22be5b7935-3922-45d4-9638-08871b17ec95%22%20LIMIT%201
```

Note the opposite quirk on this instance: `help_show?name=datastore_search`
returns a broken Python `partial(func, *args, **keywords)` docstring rather than
the action's own documentation, so use the `datastore_search_sql` help entry or
upstream CKAN docs when you need the parameter reference.

### Useful Resource IDs

| Dataset | Resource ID | Content | Update Frequency |
|---------|-------------|---------|-----------------|
| Non-Profit Registry (amutot) | be5b7935-3922-45d4-9638-08871b17ec95 | Registered non-profits | Weekly |
| Licensed Businesses | varies by municipality | Licensed businesses per city | Monthly |
| Election Results | varies by election | Voting results by ballot box | After elections |

Note: The Companies Registry resource ID may change. Verify the current resource ID via the data.gov.il portal before using.

### Query Examples

Search non-profits by name:
```
GET https://data.gov.il/api/3/action/datastore_search?resource_id=be5b7935-3922-45d4-9638-08871b17ec95&q=עמותה
```

### Response Format

```json
{
  "success": true,
  "result": {
    "records": [...],
    "total": 12345,
    "fields": [
      { "id": "field_name", "type": "text" }
    ]
  }
}
```

Note: Field names are in Hebrew. Normalize to English keys in a Code node for downstream compatibility.

---

## Israeli SMS Gateways

### 019 Telzar

Base URL: `https://019sms.co.il/api`

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api` | POST | All operations, including bulk sends | Bearer token in header |

019 exposes a single `/api` endpoint; the operation is selected in the request
body, not by the path. There are no `/api/bulk` or `/api/status` routes. A POST
to either returns the same generic HTTP 500 page as a path that was never
defined, and a GET returns a byte-identical 4,242-byte catch-all HTML page for
`/api/bulk`, `/api/status` and `/api/zzz_nonexistent` alike. Only `/api` itself
answers with JSON (an auth error). On this host, judge a route by whether the
body is JSON, not by the status code.

Send SMS request:
```
Headers:
  Content-Type: application/json
  Authorization: Bearer <token>
Body:
{
  "from": "MyBusiness",
  "to": "972501234567",
  "message": "הודעה בעברית"
}
```

### InforUMobile

Base URL: `https://capi.inforu.co.il`

Note: `api.inforu.co.il` returns 404 for the v2 paths. The API host is `capi.inforu.co.il`.

InforUMobile has a legacy XML API and newer JSON API:

JSON API endpoint: `https://capi.inforu.co.il/api/v2/SMS/SendSms`

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v2/SMS/SendSms` | POST | Send SMS | Bearer token in header + IP allowlist |

`SendSms` is the only v2 path confirmed to exist (it answers 401 unauthenticated).
`GetSmsStatus` returns 404, identical to an undefined path, so it is not the
delivery-status endpoint. Take the correct path from InforU's own documentation
for your account rather than guessing a name.

Auth failures return HTTP 401 with `{"StatusId": -2, "StatusDescription": "Authentication failed or illegal IP address"}`. The same status covers a bad token and an unlisted source IP, so whitelist your n8n egress IP in the InforU dashboard before debugging the token.

Send SMS body (JSON API):
```json
{
  "Message": "הודעה בעברית",
  "Recipients": [{ "Phone": "972501234567" }],
  "Settings": {
    "Sender": "MyBusiness",
    "MessageType": 1
  }
}
```

### Phone Number Format Rules

| Input Format | Converted Format | Notes |
|-------------|-----------------|-------|
| 050-1234567 | 972501234567 | Strip dash and leading 0, add 972 |
| 0501234567 | 972501234567 | Strip leading 0, add 972 |
| +972501234567 | 972501234567 | Strip + prefix |
| 972501234567 | 972501234567 | Already correct |
| 05012345678 | Invalid | Israeli mobile is 10 digits total |

Israeli mobile prefixes: 050, 051, 052, 053, 054, 055, 058

---

## Israeli Payment Gateways

### Cardcom

Documentation: `https://www.cardcom.solutions/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://secure.cardcom.solutions/api/v11/LowProfile/Create` | POST | v11 hosted payment page |
| `https://secure.cardcom.solutions/api/v11/Transactions/Transaction` | POST | v11 direct charge |
| `https://secure.cardcom.solutions/Interface/ChargeToken.aspx` | POST | Charge a stored token (legacy) |
| `https://secure.cardcom.solutions/Interface/CreateInvoice.aspx` | POST | Create invoice after charge (legacy) |
| Callback URL (configured via API v11 or merchant dashboard) | POST | Payment result notification |

`https://secure.cardcom.solutions/api/v11` is a base path and returns 404 on its own. Always append the operation.

Callback fields, from the v11 `LowProfileResult` schema (`https://secure.cardcom.solutions/swagger/v11/swagger.json`):

| Field | Description |
|-------|-------------|
| `ResponseCode` | **`0` = success**, anything else is a failure; read `Description` |
| `Description` | Response description |
| `LowProfileId` | Hosted-payment-page id |
| `TranzactionId` | Cardcom transaction id, and the correct dedup key |
| `ReturnValue` | Your OWN pass-through value, echoed back. **Not a status.** |
| `TranzactionInfo` | Nested: `CardOwnerIdentityNumber` (teudat zehut), `NumberOfPayments`, `ApprovalNumber`, amount |
| `DocumentInfo` | Document details where Cardcom also issued the invoice |
| `TokenInfo` | Card token for future charges |

`ReturnValue` is documented by Cardcom on the request as "A string of data to save on the transaction, usually send your unique order Id, you will get it back in the WebHook URL" and on the result as "Same value that was sent on the CreateLowProfile request". `DealResponse` does not exist in v11 (zero occurrences in the spec), and `InternalDealNumber` / `CardOwnerID` / `NumOfPayments` are legacy classic-API names absent from the result object.

### Tranzila

Documentation: `https://docs.tranzila.com/`

Tranzila API v2 authenticates via the `X-tranzila-api-app-key` HTTP header (not Basic Auth, not query parameters). v2 covers server-to-server (SAQ-D), iframe, hosted fields, Bit (init returns an iframe URL with QR + push), tokenization, recurring billing, refunds, and 3D Secure.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://secure5.tranzila.com/cgi-bin/tranzila31.cgi` | GET/POST | Process payment (legacy CGI, avoid for new integrations) |
| `https://api.tranzila.com/v1/transaction/credit_card/create` | POST | v2 server-to-server charge (auth: `X-tranzila-api-app-key`) |
| `https://api.tranzila.com/v1/transaction/bit/init` | POST | v2 Bit init, response contains iframe URL with QR code |
| Callback URL (configured in terminal settings) | GET | Payment result via query params |

Note the `credit_card` and `bit` segments in the v2 paths. `/v1/transaction/create` and `/v1/bit/init` do not exist and return 404. Unauthenticated calls to the correct paths return `401 {"code":401,"message":"Unauthorized"}`, which is the quickest way to confirm a path before wiring credentials. The legacy `tranzila71dl.cgi` endpoint also 404s; `tranzila31.cgi` is the surviving CGI entry point.

Callback query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| Response | string | "000" = approved |
| index | string | Transaction index |
| sum | string | Amount (decimal) |
| currency | string | "1"=ILS, "2"=USD, "3"=GBP, "7"=EUR |
| Rone | string | Installment count |
| ConfirmationCode | string | Shva confirmation code |
| ccno | string | Masked card number |

Tranzila API v2 also supports Bit payments. For new integrations, prefer v2 over the legacy CGI pattern.

### Grow by Meshulam

Documentation: `https://grow-il.readme.io/`

| Endpoint | Method | Description |
|----------|--------|-------------|
Base URL: `https://secure.meshulam.co.il` (sandbox: `https://sandbox.meshulam.co.il`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/light/server/1.0/createPaymentProcess/` | POST | Create payment page |
| `/api/light/server/1.0/getPaymentProcessInfo/` | POST | Get payment status |
| `/api/light/server/1.0/approveTransaction/` | POST | Approve transaction (required after webhook) |
| Webhook URL (configured in dashboard) | POST | Payment result |

Every operation is POST, including the status read. The API replies to an
undefined path with `{"err":"unknown method"}` and HTTP 200, so check the
`err` field rather than the status code when confirming a path.

**Important:** Grow API requests use `multipart/form-data`, not JSON.

Webhook payload fields:

| Field | Type | Description |
|-------|------|-------------|
| webhookKey | string | Webhook verification key |
| transactionCode | string | Unique transaction code |
| transactionType | string | Type of transaction |
| asmachta | string | Transaction reference number |
| paymentSum | string | Amount charged |
| paymentDate | string | Date of payment |
| fullName | string | Customer name (may be Hebrew) |
| payerPhone | string | Customer phone |
| payerEmail | string | Customer email |
| cardSuffix | string | Last 4 digits of card |
| cardBrand | string | Card brand (Visa, Mastercard, etc.) |
| paymentsNum | string | Installment count |

**After receiving a webhook, you must call `approveTransaction` to finalize the payment.**

Grow also supports Bit payments when enabled in the merchant dashboard.

---

## Hebcal API

Base URL: `https://www.hebcal.com`

### Shabbat Times

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/shabbat` | GET | Shabbat candle lighting and havdalah | `cfg=json`, `geonameid`, `M=on` |

### Holiday Calendar

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/hebcal` | GET | Jewish holidays | `v=1`, `cfg=json`, `year`, `month`, `maj=on`, `mod=on` |

### Israeli City Geoname IDs

| City | Geoname ID | Candle Lighting |
|------|-----------|-----------------|
| Jerusalem (yerushalayim) | 281184 | 40 min before sunset |
| Tel Aviv (tel aviv-yafo) | 293397 | 18 min before sunset |
| Haifa (haifa) | 294801 | 30 min before sunset |
| Zikhron Ya'akov | 293067 | 30 min before sunset |
| Beer Sheva (be'er sheva) | 295530 | 18 min before sunset |
| Rishon LeZion | 293703 | 18 min before sunset |
| Petah Tikva | 293918 | 18 min before sunset |
| Ashdod | 295629 | 18 min before sunset |
| Netanya | 294098 | 18 min before sunset |
| Bnei Brak | 295514 | 18 min before sunset |
| Holon | 294751 | 18 min before sunset |
| Ramat Gan | 293768 | 18 min before sunset |
| Herzliya | 294778 | 18 min before sunset |

### Shabbat Response Format

```json
{
  "title": "Shabbat Times for Tel Aviv-Yafo",
  "date": "2026-01-16",
  "items": [
    {
      "title": "Candle lighting: 4:38pm",
      "date": "2026-01-16T16:38:00+02:00",
      "category": "candles",
      "memo": "Parashat Beshalach"
    },
    {
      "title": "Havdalah (50 min): 5:42pm",
      "date": "2026-01-17T17:42:00+02:00",
      "category": "havdalah"
    }
  ]
}
```

### Holiday Response Fields

| Field | Type | Description |
|-------|------|-------------|
| title | string | Holiday name in English |
| hebrew | string | Holiday name in Hebrew |
| date | string | ISO 8601 date |
| category | string | "holiday", "candles", "havdalah" |
| yomtov | boolean | True if work restrictions apply |
| memo | string | Additional info (Torah portion, etc.) |


## israeli-bank-scrapers login fields (per bank)

**Login fields vary per bank.** There is no universal credential shape. Read `SCRAPERS[companyId].loginFields` before wiring credentials:

| Bank | Required fields |
|------|----------------|
| hapoalim | `userCode`, `password` |
| leumi, mizrahi, otsarHahayal, max, visaCal, union, beinleumi, massad, yahav | `username`, `password` |
| discount, mercantile | `id`, `password`, `num` |
| isracard, amex | `id`, `card6Digits`, `password` |



## Gateway field reference (relocated from SKILL.md)

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


---

# Israeli Payment Gateway Callbacks (moved from SKILL.md Step 5)

## Cardcom

**`ReturnValue` is NOT the success flag.** Cardcom's v11 spec defines it on the request as "A string of data to save on the transaction, usually send your unique order Id, you will get it back in the WebHook URL", and on the result as "Same value that was sent on the CreateLowProfile request". It is your own pass-through. Branching on `ReturnValue == 0` approves declined payments whenever the merchant happened to send something else. The success field is **`ResponseCode`** ("if equel zero then success").

The v11 `LowProfileResult` delivered to your `WebHookUrl` carries:

| Field | Description |
|-------|-------------|
| `ResponseCode` | **`0` = success**, anything else is a failure; read `Description` for detail |
| `LowProfileId` | The hosted-payment-page id; use with `TranzactionId` as the dedup key |
| `TranzactionId` | Cardcom transaction id |
| `ReturnValue` | Your own order id, echoed back. Not a status. |
| `TranzactionInfo` | Nested object carrying `CardOwnerIdentityNumber` (teudat zehut), `NumberOfPayments`, `ApprovalNumber` |
| `DocumentInfo` | Document details when Cardcom also issued the invoice |

There is no `DealResponse` field in v11 (zero occurrences in the spec), and `InternalDealNumber` / `CardOwnerID` / `NumOfPayments` are legacy classic-API names that do not appear in the result object. A dedup key built from `InternalDealNumber` is always `undefined`, so the duplicate-invoice guard never fires. Use `TranzactionId`.

Use the Cardcom API v11. `https://secure.cardcom.solutions/api/v11` is the **base path**, not a callable endpoint (it returns 404 on its own); append the operation, for example `POST https://secure.cardcom.solutions/api/v11/LowProfile/Create` to open a hosted payment page or `POST .../api/v11/Transactions/Transaction` for a direct charge. v11 also lets you register webhooks for document-creation events. URLs must be HTTPS and publicly routable (no `localhost`; use ngrok or Cloudflare Tunnel in dev). Full docs: `https://secure.cardcom.solutions/api/v11/DOCS`.

## Tranzila

Tranzila callbacks deliver GET parameters:

```
https://your-n8n.example.com/webhook/tranzila-callback?Response=000&index=12345&sum=100.00&currency=1
```

`Response=000` is approved. Currency: `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR. `Rone` = installments.

**Tranzila API v2** offers modern server-to-server (SAQ-D) plus iframe / hosted fields. Authentication uses an `X-tranzila-api-app-key` header (header confirmed via Stoplight API explorer at docs.tranzila.com). v2 supports Bit, tokenization, recurring billing, refunds, and 3D Secure (mandatory under SHVA rules). Prefer v2 over the legacy CGI pattern (`tranzila31.cgi`; the older `tranzila71dl.cgi` now 404s). Bit flow: server calls Tranzila v2, response includes a URL to embed in an iframe (QR code + phone push). See `https://docs.tranzila.com/` for the v2 documentation.

## Grow by Meshulam

Grow sends webhooks as POST. **Important:** the Grow API uses `multipart/form-data` (not JSON). After receiving a webhook, call `approveTransaction` to finalize the payment.

Webhook payload includes: `webhookKey`, `transactionCode`, `transactionType`, `asmachta` (transaction reference), `paymentSum`, `paymentDate`, `fullName`, `payerPhone`, `payerEmail`, `cardSuffix`, `cardBrand`, `paymentsNum`.

## Bit Payments

Bit is Israel's most popular mobile payment method, available through Tranzila (API v2) and Grow by Meshulam, not as a standalone API. Via Tranzila v2: create a payment page with `bit: true`; the customer scans a QR code or is redirected to Bit. Via Grow: enable Bit in the merchant dashboard; Bit transactions appear in the same webhook flow with a different `transactionType`.



---

# Israeli SMS Gateways (moved from SKILL.md Step 2)

## Israeli SMS Gateways

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

## Before You Issue Anything: Three Israeli Rules That Gate the Whole Workflow

**1. Not every business may issue a tax invoice.** An עוסק פטור (osek patur) may not issue a חשבונית מס (types 305 / 320) and may not charge VAT at all; they issue a קבלה or a חשבונית עסקה. Ask the business's VAT status before choosing a document type, and never hardcode 305/320. Building an osek patur a workflow that charges 18% VAT makes them charge tax unlawfully and produces an invalid document. Zero-rated cases (exports, services to a foreign resident) and the Eilat free-trade-zone exemption also change the rate, so `vat_type` / `vatType` is a per-transaction decision, not a constant.

**2. Automated commercial messaging is regulated.** תיקון 40 לחוק התקשורת governs every SMS and WhatsApp send this skill can build: it requires prior consent from the recipient, identification of the sender, the word `פרסומת` on a commercial message, and a working opt-out in the same channel. Statutory damages reach 1,000 NIS per message with no proof of damage, which is exactly the exposure profile of a bulk loop. Meta's 24-hour window is a platform rule, not the legal one, and clearing it does not clear consent. Build the opt-out and the consent check into the workflow, not into a later phase.

**3. The data these workflows touch is regulated personal data.** Teudat zehut from a payment callback, live bank credentials, and Hebrew transaction descriptions piped into a third-party LLM all fall under the Privacy Protection Law as amended (Amendment 13, in force August 2025) and the 2017 security regulations. Minimise what you persist (do not store a teudat zehut you do not need), treat the Google Sheet as a regulated database with a retention rule, and do not send identifiable customer data to a foreign model without a lawful basis.

Also note the bookkeeping rules the API will not enforce for you: document numbering is sequential and immutable, a mistaken invoice is cancelled with a credit note (330) and never deleted, and the document itself must be retained for seven years, so persist the PDF rather than storing an expiring link.



---

# israeli-bank-scrapers in a Code Node (moved from SKILL.md Step 2)

## israeli-bank-scrapers via Code Node

n8n has no native Israeli bank node. Use a Code node to run `israeli-bank-scrapers` programmatically (it is a Node.js library, NOT a CLI). Requires Node.js >= 22.22.2.

Two n8n 2.x settings gate this (see Step 6). `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` so `require()` resolves, and a working route to the secrets.

**The secret route needs care, because "use the credential store" is not implementable from inside a Code node.** The n8n Code node declares no credentials, so there is no `$credentials` to read there. `$env` is separately blocked by default in 2.x. That leaves three real options: set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` **on the task runner** and keep the `$env` pattern; or pass the secret in from a preceding credential-bearing node, accepting that it then appears in execution data; or use external secrets on an enterprise plan. Pick one deliberately. The variables below are placeholders for whichever route you chose, not globals that exist by themselves.

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



---

# Hebrew Data Handling in n8n (moved from SKILL.md Step 3)

## Handle Hebrew Data in n8n Nodes

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



---

# שערי תשלום ישראליים (הועבר מ-SKILL.md שלב 5)

## Cardcom

Cardcom שולח POST עם נתונים בפורמט form-encoded:

שדות ה-callback לפי סכימת `LowProfileResult` ב-v11 (`https://secure.cardcom.solutions/swagger/v11/swagger.json`):

| שדה | תיאור |
|-----|-------|
| `ResponseCode` | **`0` = הצלחה**, כל ערך אחר הוא כישלון; הפירוט ב-`Description` |
| `Description` | תיאור התגובה |
| `LowProfileId` | מזהה דף התשלום המתארח |
| `TranzactionId` | מזהה העסקה ב-Cardcom, וזהו מפתח הדה-דופליקציה הנכון |
| `ReturnValue` | הערך שאתם עצמכם שלחתם, חוזר אליכם. **אינו סטטוס.** |
| `TranzactionInfo` | אובייקט מקונן: `CardOwnerIdentityNumber` (תעודת זהות), `NumberOfPayments`, `ApprovalNumber`, סכום |
| `DocumentInfo` | פרטי המסמך כאשר Cardcom הפיקה גם את החשבונית |

השדה `DealResponse` אינו קיים ב-v11 כלל, והשדות `InternalDealNumber` / `CardOwnerID` / `NumOfPayments` הם שמות של ה-API הישן שאינם מופיעים באובייקט התוצאה.

Code node לוולידציה אחרי ה-Webhook. שימו לב שהוא **אינו** מסיים את הבדיקה: אף שער ישראלי לא חותם על המטען, ולכן חובה לקרוא את העסקה מחדש מול Cardcom לפי `TranzactionId` לפני הפקת מסמך כלשהו.

```javascript
const data = $input.first().json.body ?? $input.first().json;

if (Number(data.ResponseCode) !== 0) {
  return [{ json: { success: false, error: data.Description, lowProfileId: data.LowProfileId } }];
}

const info = data.TranzactionInfo ?? {};
return [{
  json: {
    success: true,
    transactionId: data.TranzactionId,      // מפתח הדה-דופליקציה
    orderId: data.ReturnValue,              // המזהה שלכם, לא סטטוס
    installments: info.NumberOfPayments,
    customerId: info.CardOwnerIdentityNumber
  }
}];
```

**ממשק Cardcom API v11:** לאינטגרציות חדשות, מגדירים את ה-webhook URL דרך Cardcom API v11 במקום לוח הבקרה הישן. הכתובת `https://secure.cardcom.solutions/api/v11` היא נתיב בסיס ולא נקודת קצה שאפשר לקרוא לה (היא מחזירה 404 בפני עצמה), ולכן מוסיפים אחריה את הפעולה, למשל `POST https://secure.cardcom.solutions/api/v11/LowProfile/Create` לפתיחת דף תשלום מתארח או `POST .../api/v11/Transactions/Transaction` לחיוב ישיר. נקודת ה-v11 גם מאפשרת רישום webhooks לאירועי יצירת מסמכים (קבלות, חשבוניות) בנוסף לקריאות חיוב. ה-webhook חייב להיות HTTPS וזמין לאינטרנט (לא `localhost`, השתמשו ב-ngrok או Cloudflare Tunnel בפיתוח). תיעוד מלא: `https://secure.cardcom.solutions/api/v11/DOCS`.

## Tranzila

Tranzila משתמש בתבנית callback עם פרמטרי GET:

| שדה | תיאור | ערכים |
|-----|-------|-------|
| `Response` | קוד סטטוס | `000` = אושר, `001`-`999` = שגיאות |
| `index` | אינדקס עסקה | מספרי |
| `sum` | סכום שחויב | עשרוני (שקלים אם `currency=1`) |
| `currency` | קוד מטבע | `1` = ILS, `2` = USD, `3` = GBP, `7` = EUR |
| `Rone` | תשלומים | מספר |

**Tranzila API v2:** Tranzila מציעה אינטגרציית server-to-server (SAQ-D) פלוס iframe ושדות מתארחים לציות PCI. אימות דרך header בשם `X-tranzila-api-app-key` (לא Basic Auth, לא פרמטרי query). ה-v2 API תומך בתשלומי ביט, טוקניזציה, חיוב חוזר, החזרים, ו-3D Secure (חובה לכרטיסי אשראי ישראליים לפי כללי שב"א). לאינטגרציות חדשות, עדיף v2 על פני תבנית ה-CGI הישנה (`tranzila31.cgi`, שכן `tranzila71dl.cgi` כבר מחזיר 404). זרימת ביט: השרת קורא ל-Tranzila v2, התגובה כוללת URL להטמעה ב-iframe (שמציג קוד QR וטלפון להתראת push). תיעוד: `https://docs.tranzila.com/`.

## Grow by Meshulam

Grow by Meshulam שולח התראות webhook כבקשות POST. **חשוב:** ה-API של Grow משתמש ב-`multipart/form-data` לבקשות (לא JSON). אחרי קבלת webhook, חובה לקרוא ל-`approveTransaction` כדי לסיים את העסקה.

שדות ב-webhook payload:

| שדה | תיאור |
|-----|-------|
| `webhookKey` | מפתח אימות webhook |
| `transactionCode` | קוד עסקה ייחודי |
| `transactionType` | סוג העסקה |
| `asmachta` | מספר אסמכתא |
| `paymentSum` | סכום שחויב |
| `paymentDate` | תאריך התשלום |
| `fullName` | שם מלא של הלקוח |
| `payerPhone` | טלפון הלקוח |
| `payerEmail` | אימייל הלקוח |
| `cardSuffix` | 4 ספרות אחרונות של הכרטיס |
| `cardBrand` | מותג הכרטיס (Visa, Mastercard וכו') |
| `paymentsNum` | מספר תשלומים |

Code node לעיבוד webhook של Grow ואישור:

```javascript
const data = $input.first().json;

const payment = {
  transactionCode: data.transactionCode,
  asmachta: data.asmachta,
  amount: parseFloat(data.paymentSum),
  customerName: data.fullName,
  customerPhone: data.payerPhone,
  customerEmail: data.payerEmail,
  installments: parseInt(data.paymentsNum) || 1
};

// חובה לקרוא ל-approveTransaction אחרי קבלת ה-webhook
// זה נעשה ב-HTTP Request node הבא עם multipart/form-data
return [{ json: payment }];
```

**רשימת IP לבנה:** Cardcom ו-Tranzila דורשים שה-IP של שרת ה-webhook יהיה ברשימה המורשית בלוח הבקרה שלהם. באירוח עצמי השתמשו ב-IP קבוע או reverse proxy עם כתובת יציאה קבועה.

## תשלומי ביט

ביט הוא אמצעי התשלום הנייד הפופולרי ביותר בישראל. תשלומי ביט זמינים דרך Tranzila (API v2) ו-Grow by Meshulam, לא כ-API עצמאי.

ביט דרך Tranzila v2: יוצרים דף תשלום עם `bit: true` בבקשה. הלקוח סורק QR או מופנה לביט. ה-webhook callback משתמש באותם שדות כמו עסקאות כרטיס אשראי.

ביט דרך Grow by Meshulam: מפעילים ביט בלוח הבקרה של Grow. עסקאות ביט מופיעות באותו תהליך webhook כמו עסקאות כרטיס, עם ערך `transactionType` שונה.



---

# טיפול בנתונים בעברית ב-n8n (הועבר מ-SKILL.md שלב 3)

## טקסט RTL ב-Code Nodes

ב-n8n צמתי Code מעבדים מחרוזות כ-UTF-8, אז עברית עובדת באופן טבעי. הבעיות מופיעות בממשקים: תגובות API, ייצוא CSV, תבניות מייל.

| בעיה | איפה קורה | פתרון |
|------|-----------|-------|
| עברית הפוכה ב-CSV | ייצוא Spreadsheet File node | הגדרת encoding ל-UTF-8-BOM |
| ניקוד שבור | פרסור תגובת HTTP Request | הגדרת encoding ל-UTF-8 מפורשות |
| ערבוב RTL/LTR במיילים | Send Email node | עטיפת טקסט עברי ב-`<div dir="rtl">` |
| מפתחות JSON בעברית | תגובות data.gov.il | נרמול מפתחות ב-Code node |
| עברית קטועה | בדיקות אורך מחרוזת | שימוש ב-`Array.from(str).length` במקום `.length` |

## פורמט מטבע שקלים

Code node לעיצוב סכומים בשקלים:

```javascript
function formatNIS(amount) {
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: 'ILS',
    minimumFractionDigits: 2
  }).format(amount);
}

// קלט:  12345.60
// פלט: 12,345.60 ₪
```

**לגבי Morning API:** סכומים ב-API הם בשקלים עשרוניים (לא אגורות). `price: 50` זה 50.00 ש"ח. אין צורך להמיר אגורות לשקלים כשעובדים עם Morning API.

## פרסור תאריכים ישראליים

מסמכים ישראליים משתמשים בפורמט DD/MM/YYYY. חשוב לפרסר נכון:

```javascript
// פרסור תאריך ישראלי DD/MM/YYYY
function parseIsraeliDate(dateStr) {
  const [day, month, year] = dateStr.split('/').map(Number);
  return new Date(year, month - 1, day);
}

// פרסור שמות חודשים בעברית (נפוץ במסמכי ממשלה)
const hebrewMonths = {
  'ינואר': 0, 'פברואר': 1, 'מרץ': 2, 'אפריל': 3,
  'מאי': 4, 'יוני': 5, 'יולי': 6, 'אוגוסט': 7,
  'ספטמבר': 8, 'אוקטובר': 9, 'נובמבר': 10, 'דצמבר': 11
};
```



---

# israeli-bank-scrapers ב-Code Node (הועבר מ-SKILL.md שלב 2)

## israeli-bank-scrapers דרך Code Node

ל-n8n אין node מובנה לבנקים ישראליים. משתמשים ב-Code node להרצת `israeli-bank-scrapers` בצורה פרוגרמטית. החבילה היא ספריית Node.js (לא כלי CLI), לכן חייבים להשתמש ב-`createScraper()`:

**חשוב:** דורש Node.js >= 22.22.2 בסביבת n8n.

שתי הגדרות ב-n8n 2.x חייבות להיות במקום לפני שהקוד הזה רץ בכלל (פירוט בשלב 6): הגדרת `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` כדי ש-`require()` יצליח, ושליפת פרטי ההתחברות מ-credential store במקום מ-`$env` (גישה למשתני סביבה מתוך Code node חסומה כברירת מחדל ב-2.x).

```javascript
// ב-Code node (ב-n8n 2.0: רץ ב-task runner מבודד)
const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');

const scraper = createScraper({
  companyId: CompanyTypes.hapoalim,
  startDate: new Date('2026-01-01'),
  combineInstallments: false,
  showBrowser: false
});

// שדות ההתחברות של הפועלים הם userCode ו-password. בבנקים אחרים השדות שונים.
const credentials = {
  userCode: BANK_USER,
  password
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

סורקים נתמכים (חברי ה-enum בשם `CompanyTypes`): הפועלים (hapoalim), לאומי (leumi), דיסקונט (discount), מרכנתיל (mercantile), מזרחי (mizrahi), אוצר החייל (otsarHahayal), בינלאומי (beinleumi), יוניון (union), מסד (massad), יהב (yahav), בהצדעה (behatsdaa), ביחד בשבילה (beyahadBishvilha), oneZero, פאג"י (pagi), ויזה כאל (visaCal), מקס (max, לשעבר לאומי קארד), ישראכרט (isracard), אמקס (amex).

**שדות ההתחברות שונים מבנק לבנק.** אין מבנה אחיד לפרטי ההתחברות. בדקו את `SCRAPERS[companyId].loginFields` לפני שמחברים credentials:

| בנק | שדות נדרשים |
|------|-------------|
| הפועלים | `userCode`, `password` |
| לאומי, מזרחי, אוצר החייל, מקס, ויזה כאל, יוניון, בינלאומי, מסד, יהב | `username`, `password` |
| דיסקונט, מרכנתיל | `id`, `password`, `num` |
| ישראכרט, אמקס | `id`, `card6Digits`, `password` |

**חסימת Cloudflare (2026):** מתחילת 2026, Cloudflare חוסם דפדפנים headless באתרי אמקס וישראכרט. הפורק המתוחזק `@sergienko4/israeli-bank-scrapers` משתמש ב-Camoufox כפתרון עוקף. אם נתקלים בכשלונות סריקה מתמשכים עם ספקים אלה:

```bash
npm install @sergienko4/israeli-bank-scrapers
```

**אבטחה:** פרטי התחברות נשמרים ב-credential store של n8n, לא בתוך ה-workflow JSON. משתמשים במשתני סביבה לערכים רגישים.



---

# שערי SMS ישראליים (הועבר מ-SKILL.md שלב 2)

## שערי SMS ישראליים

| שער | שרת | אימות | מתאים ל |
|-----|------|-------|---------|
| 019 Telzar | `019sms.co.il` | Bearer token, או שם משתמש וסיסמה | שיווק המוני, הודעות עסקיות |
| InforUMobile | `capi.inforu.co.il` | Bearer token (עם רשימת IP מורשים) | OTP, הודעות עסקיות |
| Nexmo/Vonage IL | `rest.nexmo.com` | API key + secret | בינלאומי + מקומי |

דוגמת 019 Telzar SMS ב-HTTP Request node:

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

**שער 019 מחזיר HTTP 200 גם כשהשליחה נכשלת.** כשל אימות חוזר כ-`200 {"status":3,"message":"Username or password is incorrect or Expired and API token is invalid"}`, כך ש-HTTP Request node בהגדרות ברירת המחדל מפרש את זה כהצלחה וה-workflow ממשיך בלי שנשלחה שום הודעה. מפעילים **Always Output Data** על ה-node ומסתעפים לפי `$json.status` (הערך 0 מציין שליחה מוצלחת) ב-IF node, ולא לפי קוד ה-HTTP.

שער InforUMobile אוכף רשימת IP מורשים בנוסף לטוקן. פנייה מכתובת שאינה ברשימה מקבלת `401 {"StatusId": -2, "StatusDescription": "Authentication failed or illegal IP address"}`. מוסיפים את כתובת ה-IP היוצאת של n8n לרשימה בלוח הבקרה של InforU, לצד Cardcom ו-Tranzila (שלב 5).

פורמט מספרי טלפון ישראליים: תמיד שולחים בפורמט בינלאומי `972XXXXXXXXX` (מורידים את ה-0 הפותח). Code node לפני ה-SMS node מטפל בזה:

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



---

# WhatsApp Business Cloud in n8n (detail)

## WhatsApp Business Cloud

WhatsApp is the dominant Israeli business messaging channel and n8n ships first-class nodes: **`n8n-nodes-base.whatsApp`** ("WhatsApp Business Cloud", typeVersion 1.1, credential `whatsAppApi`) for sending, and **`n8n-nodes-base.whatsAppTrigger`** for inbound messages. Message operations are Send, Send Template, and Send and Wait for Response; message types cover text, image, document, audio, video, location and contacts. A separate Media resource handles upload / URL-get / delete.

Two Meta platform rules break these workflows in production, and neither is an n8n concern:

- **The 24-hour customer service window.** A user messaging (or calling) your number opens a 24-hour window; inside it you may send free-form messages. Outside it, only a pre-approved template will deliver. A scheduled Israeli workflow, by definition, fires outside the window, so it must use Send Template.
- **Templates need prior approval in one of three categories:** Marketing, Utility, Authentication. Approval takes real time and Hebrew templates are reviewed like any other, so approve the template before the workflow ships, not on launch day.

Pricing is per delivered message (conversation-based pricing was replaced on July 1, 2025), so a fan-out loop costs money per item. Rate-limit deliberately.



---

# WhatsApp Business Cloud ב-n8n (פירוט)

## WhatsApp Business Cloud

וואטסאפ הוא ערוץ ההודעות העסקי הדומיננטי בישראל, ול-n8n יש צמתים ייעודיים: **`n8n-nodes-base.whatsApp`** ("WhatsApp Business Cloud", typeVersion 1.1, credential בשם `whatsAppApi`) לשליחה, ו-**`n8n-nodes-base.whatsAppTrigger`** לקליטת הודעות נכנסות. פעולות ההודעה הן Send, Send Template ו-Send and Wait for Response, וסוגי ההודעה כוללים טקסט, תמונה, מסמך, אודיו, וידאו, מיקום ואנשי קשר. משאב Media נפרד מטפל בהעלאה, קבלת URL ומחיקה.

שני כללים של מטא שוברים את התהליכים האלה בפרודקשן, ושניהם לא בשליטת n8n:

- **חלון שירות הלקוחות של 24 שעות.** משתמש ששולח לכם הודעה (או מתקשר) פותח חלון של 24 שעות שבתוכו אפשר לשלוח הודעות חופשיות. מחוצה לו רק תבנית מאושרת מראש תגיע ליעד. תהליך מתוזמן ישראלי, מעצם הגדרתו, רץ מחוץ לחלון, ולכן חייב להשתמש ב-Send Template.
- **תבניות דורשות אישור מראש באחת משלוש קטגוריות:** Marketing, Utility, Authentication. האישור לוקח זמן אמיתי ותבניות בעברית נבדקות כמו כל תבנית אחרת, אז אשרו את התבנית לפני שהתהליך עולה לאוויר ולא ביום ההשקה.

התמחור הוא לפי הודעה שנמסרה (התמחור לפי שיחה הוחלף ב-1.7.2025), ולכן לולאת פיזור עולה כסף על כל פריט. הגבילו קצב במכוון.

