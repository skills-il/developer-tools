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
| `/documents/{id}/download` | GET | Download PDF | Returns binary PDF |
| `/documents/{id}/send` | POST | Email document to client | `to` (email address) |

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
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026** | **5,000 NIS** |
| Jan 1, 2027 | 5,000 NIS (planned to continue) |

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
| `/payments` | GET | List payments | `fromDate`, `toDate` |
| `/payments/{id}` | GET | Get payment details | Path parameter: payment UUID |

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
| `/searchDocuments` | POST | Search documents | `fromDate`, `toDate`, `type`, `api_key`, `api_email` |
| `/getDocPdf` | POST | Download PDF | `docNum` |
| `/sendDocByEmail` | POST | Email document to client | `docNum`, `to` |

### Document Type Codes

Same Tax Authority codes as Morning: 10 (price quote), 305 (tax invoice), 320 (tax invoice / receipt), 330 (credit note), 400 (receipt).

### Israel Invoice Reform 2026

EZCount auto-clears qualifying tax invoices against SHAAM and returns the allocation number in the response. If `allocation_status: 'pending'`, retry after 30 seconds before treating the invoice as final. SDK code samples in PHP, Java, .NET, ASP, Ruby, Node, and Python on the EZCount developer portal.

### Common Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation result |
| `errMsg` | string | Error in Hebrew |
| `docNum` | string | Document number |
| `pdfLink` | string | Public PDF URL |
| `allocation_number` | string | SHAAM-issued mispar haktza'a (Invoice Reform 2026) |
| `allocation_status` | string | `cleared` / `pending` / `not_required` |

**Amounts are in decimal shekels.** Same convention as Morning.

---

## data.gov.il CKAN API

Base URL: `https://data.gov.il/api/3`

### Core Endpoints

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/action/datastore_search` | GET | Search within a dataset | `resource_id`, `q`, `filters`, `limit`, `offset`, `sort` |
| `/action/datastore_search_sql` | GET | SQL query on dataset | `sql` (PostgreSQL-compatible) |
| `/action/package_show` | GET | Get dataset metadata | `id` (dataset name or UUID) |
| `/action/resource_show` | GET | Get resource details | `id` (resource UUID) |

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
| `/api` | POST | Send single SMS | Bearer token in header |
| `/api/bulk` | POST | Send bulk SMS | Same |
| `/api/status` | GET | Check message status | Bearer token + message ID |

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

Base URL: `https://api.inforu.co.il`

InforUMobile has a legacy XML API and newer JSON API:

JSON API endpoint: `https://api.inforu.co.il/api/v2/SMS/SendSms`

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v2/SMS/SendSms` | POST | Send SMS | Bearer token in header |
| `/api/v2/SMS/GetSmsStatus` | GET | Check status | Bearer token + message ID |

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
| `https://secure.cardcom.solutions/Interface/ChargeToken.aspx` | POST | Charge a stored token |
| `https://secure.cardcom.solutions/Interface/CreateInvoice.aspx` | POST | Create invoice after charge |
| Callback URL (configured via API v11 or merchant dashboard) | POST | Payment result notification |

Callback fields:

| Field | Type | Description |
|-------|------|-------------|
| ReturnValue | string | "0" = success |
| InternalDealNumber | string | Cardcom transaction ID |
| DealResponse | string | Human-readable response (Hebrew) |
| CardOwnerID | string | Customer teudat zehut (9 digits) |
| NumOfPayments | string | Installment count |
| Sum | string | Amount charged |
| Token | string | Card token for future charges |

### Tranzila

Documentation: `https://docs.tranzila.com/`

Tranzila API v2 authenticates via the `X-tranzila-api-app-key` HTTP header (not Basic Auth, not query parameters). v2 covers server-to-server (SAQ-D), iframe, hosted fields, Bit (init returns an iframe URL with QR + push), tokenization, recurring billing, refunds, and 3D Secure.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://secure5.tranzila.com/cgi-bin/tranzila71dl.cgi` | GET/POST | Process payment (legacy CGI, avoid for new integrations) |
| `https://api.tranzila.com/v1/transaction/create` | POST | v2 server-to-server charge (auth: `X-tranzila-api-app-key`) |
| `https://api.tranzila.com/v1/bit/init` | POST | v2 Bit init, response contains iframe URL with QR code |
| Callback URL (configured in terminal settings) | GET | Payment result via query params |

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
| `/api/v1/payments/create` | POST | Create payment page |
| `/api/v1/payments/{id}` | GET | Get payment status |
| `/api/v1/payments/approve` | POST | Approve transaction (required after webhook) |
| Webhook URL (configured in dashboard) | POST | Payment result |

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
