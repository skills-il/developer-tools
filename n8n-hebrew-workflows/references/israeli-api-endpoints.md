# Israeli API Endpoints Reference for n8n

Quick reference for configuring HTTP Request nodes when connecting to Israeli services.

## Green Invoice API

Base URL: `https://api.greeninvoice.co.il/api/v1`

### Authentication

| Step | Method | Endpoint | Body |
|------|--------|----------|------|
| Get token | POST | `/account/token` | `{ "id": "<api_key>", "secret": "<api_secret>" }` |

Token TTL: ~30 minutes. Refresh proactively before expiry.

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
| 10 | קבלה | Receipt |
| 20 | חשבונית מס | Tax Invoice |
| 100 | חשבונית מס / קבלה | Tax Invoice / Receipt |
| 300 | הצעת מחיר | Price Quote |
| 305 | הזמנה | Order |
| 320 | חשבונית עסקה | Transaction Invoice |
| 400 | קבלה על תרומה | Donation Receipt |
| 405 | חשבונית זיכוי | Credit Invoice |

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
| `amount` | number | Amount before VAT |
| `vat` | number | VAT amount |
| `totalAmount` | number | Amount including VAT |
| `status` | integer | 0=draft, 10=open, 20=closed, 30=canceled |
| `createdAt` | string | ISO 8601 timestamp |
| `client.name` | string | Client name (may be Hebrew) |
| `client.taxId` | string | Israeli tax ID (osek morshe/patur number) |

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
| Companies Registry (rasham hachavarot) | 8f714b7f-c35c-4b40-a0e0-55b6ac4ae2d2 | All registered Israeli companies | Weekly |
| Non-Profit Registry (amutot) | be5b7935-3922-45d4-9638-08871b17ec95 | Registered non-profits | Weekly |
| Licensed Businesses | varies by municipality | Licensed businesses per city | Monthly |
| Election Results | varies by election | Voting results by ballot box | After elections |

### Query Examples

Search companies by name:
```
GET https://data.gov.il/api/3/action/datastore_search?resource_id=8f714b7f-c35c-4b40-a0e0-55b6ac4ae2d2&q=אלביט
```

SQL query with filters:
```
GET https://data.gov.il/api/3/action/datastore_search_sql?sql=SELECT * FROM "8f714b7f-c35c-4b40-a0e0-55b6ac4ae2d2" WHERE "שם חברה" LIKE '%טכנולוגי%' LIMIT 10
```

### Response Format

```json
{
  "success": true,
  "result": {
    "records": [...],
    "total": 12345,
    "fields": [
      { "id": "שם חברה", "type": "text" },
      { "id": "מספר חברה", "type": "numeric" }
    ]
  }
}
```

Note: Field names are in Hebrew. Normalize to English keys in a Function node for downstream compatibility.

---

## Israeli SMS Gateways

### 019 SMS (InfruSMS)

Base URL: `https://www.019sms.co.il/api`

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api` | POST | Send single SMS | API key + secret in body |
| `/api/bulk` | POST | Send bulk SMS | Same |
| `/api/status` | GET | Check message status | API key + message ID |

Send SMS body:
```json
{
  "user": "<username>",
  "password": "<password>",
  "from": "MyBusiness",
  "to": "972501234567",
  "message": "הודעה בעברית"
}
```

### Inforu (SMSGlobal IL)

Base URL: `https://api.inforu.co.il/SendMessageXml.ashx`

Inforu uses XML-based API (legacy) and newer JSON API:

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

Documentation: `https://kb.cardcom.co.il/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://secure.cardcom.solutions/Interface/ChargeToken.aspx` | POST | Charge a stored token |
| `https://secure.cardcom.solutions/Interface/CreateInvoice.aspx` | POST | Create invoice after charge |
| Callback URL (configured in merchant dashboard) | POST | Payment result notification |

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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://secure5.tranzila.com/cgi-bin/tranzila71dl.cgi` | GET/POST | Process payment |
| Callback URL (configured in terminal settings) | GET | Payment result via query params |

Callback query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| Response | string | "000" = approved |
| index | string | Transaction index |
| sum | string | Amount (decimal) |
| currency | string | "1"=ILS, "2"=USD, "3"=EUR |
|Rone | string | Installment count |
| ConfirmationCode | string | Shva confirmation code |
| ccno | string | Masked card number |

### Grow (Meshulam)

Documentation: `https://grow.link/developers`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/payments/create` | POST | Create payment page |
| `/api/v1/payments/{id}` | GET | Get payment status |
| Webhook URL (configured in dashboard) | POST | Payment result JSON |

Webhook JSON body:

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | string | Unique transaction ID |
| status | string | "success", "failed", "pending" |
| amount | number | Amount in ILS |
| currency | string | "ILS" |
| payments_number | integer | Installment count |
| customer.name | string | Customer name (may be Hebrew) |
| customer.email | string | Customer email |
| customer.phone | string | Customer phone |

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

| City | Geoname ID |
|------|-----------|
| Jerusalem (yerushalayim) | 281184 |
| Tel Aviv (tel aviv-yafo) | 293397 |
| Haifa (haifa) | 294801 |
| Beer Sheva (be'er sheva) | 295530 |
| Rishon LeZion | 293703 |
| Petah Tikva | 293918 |
| Ashdod | 295629 |
| Netanya | 294098 |
| Bnei Brak | 295514 |
| Holon | 294751 |
| Ramat Gan | 293768 |
| Herzliya | 294778 |

### Shabbat Response Format

```json
{
  "title": "Shabbat Times for Tel Aviv-Yafo",
  "date": "2025-01-17",
  "items": [
    {
      "title": "Candle lighting: 4:38pm",
      "date": "2025-01-17T16:38:00+02:00",
      "category": "candles",
      "memo": "Parashat Beshalach"
    },
    {
      "title": "Havdalah (50 min): 5:42pm",
      "date": "2025-01-18T17:42:00+02:00",
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
