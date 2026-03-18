# Israeli Service Modules and HTTP Configurations for Make.com

Reference guide for connecting Israeli services in Make.com scenarios. Covers native modules, HTTP module configurations, authentication patterns, and payload examples.

## Green Invoice (Hashbonit Yeruqa)

### Native Module

Green Invoice has a built-in Make.com module. Search "Green Invoice" in the module palette.

**Connection Setup:**
1. Go to Green Invoice dashboard: Settings > API Integration
2. Generate API Key and Secret
3. In Make.com, create a new Green Invoice connection with these credentials
4. Select environment: Production or Sandbox

**Sandbox vs Production:**

| Setting | Sandbox | Production |
|---|---|---|
| Base URL | `https://sandbox.d.greeninvoice.co.il/api/v1/` | `https://api.greeninvoice.co.il/api/v1/` |
| Documents | Test only, not legally valid | Real tax documents |
| Rate limits | More lenient | Standard |

### Available Triggers

| Trigger | Description | Recommended Interval |
|---|---|---|
| Watch Documents | New or updated documents | 15 minutes |
| Watch Payments | New payment records | 15 minutes |
| Watch Clients | New client records | 1 hour |

### Available Actions

| Action | Description | Key Parameters |
|---|---|---|
| Create Document | Create invoice, receipt, quote | `type`, `client`, `income`, `currency`, `lang` |
| Create Client | Add a new client record | `name`, `emails`, `taxId`, `address` |
| Get Document | Retrieve document by ID | `id` |
| Search Documents | Query documents by criteria | `type`, `fromDate`, `toDate`, `status` |

### Document Type Codes

| Code | Type (English) | Type (Hebrew) |
|---|---|---|
| 300 | Invoice + Receipt | חשבונית מס / קבלה |
| 305 | Credit Note | חשבונית זיכוי |
| 320 | Tax Invoice | חשבונית מס |
| 330 | Receipt | קבלה |
| 400 | Quote | הצעת מחיר |
| 405 | Purchase Order | הזמנת רכש |
| 500 | Delivery Note | תעודת משלוח |

### Example: Create Tax Invoice Payload

```json
{
  "type": 320,
  "lang": "he",
  "currency": "ILS",
  "client": {
    "name": "חברה לדוגמה בע\"מ",
    "taxId": "515123456",
    "emails": ["billing@example.co.il"]
  },
  "income": [
    {
      "description": "שירותי פיתוח תוכנה",
      "quantity": 1,
      "price": 15000,
      "currency": "ILS",
      "vatType": 1
    }
  ]
}
```

Note: `price` in the API is in whole shekels (not agorot) when creating documents. However, `amount` in webhook responses and search results is in agorot. This inconsistency is a common source of bugs.

### VAT Type Values

| Value | Meaning | When to Use |
|---|---|---|
| 0 | Exempt from VAT | Non-profit, certain services |
| 1 | VAT included in price | B2C, retail pricing |
| 2 | VAT excluded (added on top) | B2B, wholesale pricing |

## Monday.com

### Native Module

Monday.com has a built-in Make.com module.

**Connection Setup:**
1. In Monday.com: Avatar > Developers > My Access Tokens
2. Copy the personal API token (or create an app-level token)
3. In Make.com, create a Monday.com connection with the token

### Column ID Mapping

Monday.com columns have both display titles (which may be in Hebrew) and column IDs (stable English identifiers). Always use column IDs in Make.com mappings.

To find column IDs:
1. Open the board
2. Click column header > Column Settings > Column Info > Copy ID
3. Or use the API Explorer: `boards(ids: [BOARD_ID]) { columns { id title type } }`

Common column types and their Make.com value formats:

| Column Type | Make.com Value Format | Example |
|---|---|---|
| Text | Plain string | `"חברה לדוגמה"` |
| Number | Numeric string | `"1500.50"` |
| Status | Label index or label text | `{"label": "Done"}` |
| Date | ISO date string | `"2026-03-15"` |
| People | User IDs array | `{"personsAndTeams": [{"id": 12345}]}` |
| Dropdown | Dropdown IDs | `{"ids": [1, 2]}` |

### Board Templates for Israeli Business

| Board Template | Common Use | Key Columns |
|---|---|---|
| Project Tracker | Billing by project | Status, Client, Budget (ILS), Hours |
| Sales CRM | Lead/deal pipeline | Deal Value, Stage, Contact, Close Date |
| Invoice Tracker | AP/AR management | Amount, Due Date, Status, Client Name |

## Priority ERP (via HTTP Module)

Priority does not have a native Make.com module. All interactions use the HTTP module with OData API.

### Connection Setup

**HTTP Module Configuration:**

| Setting | Value |
|---|---|
| URL | `https://{domain}/odata/Priority/tabula.ini/{company}/{entity}` |
| Method | GET (read), POST (create), PATCH (update) |
| Auth | Basic (Priority username:password) |
| Headers | `Content-Type: application/json`, `Accept: application/json` |

Replace `{domain}` with your Priority instance domain, `{company}` with the company name in Priority (usually "demo" for testing), and `{entity}` with the OData entity name.

### Common Entities

| Entity | Path | Description | Key Fields |
|---|---|---|---|
| ORDERS | `/ORDERS` | Sales orders | `ORDNAME`, `CUSTNAME`, `QPRICE`, `CURDATE` |
| AINVOICES | `/AINVOICES` | A/R invoices | `IVNUM`, `CUSTNAME`, `TOTPRICE`, `IVDATE` |
| PINVOICES | `/PINVOICES` | A/P invoices | `IVNUM`, `SUPNAME`, `TOTPRICE`, `IVDATE` |
| PORDERS | `/PORDERS` | Purchase orders | `ORDNAME`, `SUPNAME`, `QPRICE` |
| CUSTOMERS | `/CUSTOMERS` | Customer master | `CUSTNAME`, `CUSTDES`, `PHONE`, `EMAIL` |
| SUPPLIERS | `/SUPPLIERS` | Supplier master | `SUPNAME`, `SUPDES`, `PHONE`, `EMAIL` |
| PART | `/PART` | Item master | `PARTNAME`, `PARTDES`, `TBALANCE` |
| LOGCOUNTERS | `/LOGCOUNTERS` | Inventory counts | `PARTNAME`, `LOCNAME`, `TBALANCE` |

### OData Query Examples

**Get invoices from this month:**
```
/AINVOICES?$filter=IVDATE ge 2026-03-01T00:00:00Z&$orderby=IVDATE desc&$top=100
```

**Get customer by name (Hebrew):**
```
/CUSTOMERS?$filter=CUSTDES eq 'חברה לדוגמה'
```

Note: Hebrew values in OData filters must be URL-encoded. Make.com's HTTP module handles this automatically when using the query string builder.

**Expand related entities:**
```
/ORDERS?$expand=ORDERITEMS_SUBFORM&$filter=CURDATE ge 2026-01-01T00:00:00Z
```

### Priority API Gotchas

- Priority field names are ALL CAPS (e.g., `CUSTNAME`, not `custName`)
- Date format in responses: `YYYY-MM-DDT00:00:00+02:00` (Israel timezone offset)
- Hebrew text in responses is UTF-8 encoded
- Pagination: use `$skip` and `$top` (default page size is 20)
- Some on-prem installations require VPN or IP whitelisting

## WhatsApp Cloud API (via HTTP Module)

### Connection Setup

1. Create a Meta Business account and verify your business
2. Set up WhatsApp Business API in the Meta Developer Console
3. Get a permanent system user access token
4. Note your Phone Number ID

**HTTP Module Configuration:**

| Setting | Value |
|---|---|
| URL | `https://graph.facebook.com/v21.0/{phone-number-id}/messages` |
| Method | POST |
| Auth | Bearer Token (your permanent access token) |
| Headers | `Content-Type: application/json` |

### Message Types

**Template Message (for outbound, requires pre-approval):**
```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "template",
  "template": {
    "name": "order_confirmation_he",
    "language": {
      "code": "he"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "ישראל ישראלי"},
          {"type": "text", "text": "ORD-12345"},
          {"type": "text", "text": "₪1,500.00"}
        ]
      }
    ]
  }
}
```

**Text Message (for replies within 24-hour window):**
```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "text",
  "text": {
    "body": "שלום! ההזמנה שלך התקבלה בהצלחה."
  }
}
```

### Phone Number Formatting

Israeli phone numbers for WhatsApp must be in international format without the leading zero or plus sign:

| Input | Correct Format | Notes |
|---|---|---|
| 050-123-4567 | `972501234567` | Remove leading 0, add 972 |
| +972-50-123-4567 | `972501234567` | Remove + and hyphens |
| 03-123-4567 | `97231234567` | Landline (rarely on WhatsApp) |

Make.com expression to format: `replace(replace(phone; "+"; ""); "-"; "")` then check if it starts with "0" and replace with "972".

## Israeli SMS Providers (via HTTP Module)

### 019 SMS

| Setting | Value |
|---|---|
| URL | `https://019sms.co.il/api` |
| Method | POST |
| Auth | API key in `Authorization` header |
| Content-Type | `application/json` |

```json
{
  "sms": {
    "user": {
      "username": "your_username"
    },
    "source": "YourBrand",
    "targets": {
      "phone": ["0501234567"]
    },
    "message": {
      "msg": "הודעה בעברית"
    }
  }
}
```

### InforUMobile

| Setting | Value |
|---|---|
| URL | `https://api.inforu.co.il/SendMessageXml.ashx` |
| Method | POST |
| Content-Type | `application/xml` |

Note: InforUMobile uses XML format, not JSON. Set the Make.com HTTP module body type to "Raw" and build the XML string.

### SMS4Free

| Setting | Value |
|---|---|
| URL | `https://www.sms4free.co.il/ApiSMS/SendSMS` |
| Method | POST |
| Content-Type | `application/json` |

```json
{
  "key": "your_api_key",
  "user": "your_username",
  "pass": "your_password",
  "sender": "YourBrand",
  "recipient": "0501234567",
  "msg": "הודעה בעברית"
}
```

## Israeli Payment Gateway Webhooks

### Cardcom

**Webhook URL Setup:**
In the Cardcom dashboard, go to Settings > Notification URL > set your Make.com Custom Webhook URL.

**Callback Fields (POST body, form-encoded):**

| Field | Type | Description |
|---|---|---|
| `OperationResponse` | String | `0` = success, other = failure |
| `OperationResponseText` | String | Hebrew description of result |
| `InternalDealNumber` | String | Cardcom's transaction ID |
| `Amount` | String | Charge amount (ILS, decimal) |
| `CardOwnerID` | String | Teudat Zehut (9 digits) |
| `CardOwnerName` | String | Name on card (may be Hebrew) |
| `CardOwnerEmail` | String | Cardholder email |
| `CardOwnerPhone` | String | Cardholder phone |
| `NumOfPayments` | String | Number of installments |
| `FirstPaymentAmount` | String | First installment amount |
| `Token` | String | Card token (for recurring) |
| `ApprovalNumber` | String | Bank approval number |
| `Last4Digits` | String | Last 4 digits of card |

### Tranzila

**Redirect Parameters (GET query string or POST body):**

| Field | Type | Description |
|---|---|---|
| `Response` | String | `000` = approved, `001`-`999` = error codes |
| `sum` | String | Amount in ILS |
| `currency` | String | Currency code (`1` = ILS, `2` = USD) |
| `ccno` | String | Masked card number |
| `myid` | String | Teudat Zehut |
| `fpay` | String | First payment amount |
| `spay` | String | Subsequent payment amount |
| `npay` | String | Number of payments |
| `ConfirmationCode` | String | Bank confirmation code |
| `index` | String | Tranzila transaction index |
| `TranzilaTK` | String | Token for recurring charges |

**Tranzila Response Codes (common):**

| Code | Meaning |
|---|---|
| `000` | Approved |
| `001` | Card blocked |
| `002` | Card stolen |
| `003` | Contact credit company |
| `004` | Declined |
| `006` | ID mismatch |
| `033` | Card expired |

### Grow (by Leumi)

**Webhook Payload (JSON POST):**

Grow sends a JSON payload with a signature header for verification.

**Signature Verification:**
1. Read the raw POST body
2. Compute HMAC-SHA256 using your shared secret
3. Compare with the `X-Grow-Signature` header value

| Field | Type | Description |
|---|---|---|
| `event_type` | String | `payment.completed`, `payment.failed`, `refund.completed` |
| `payment.amount` | Number | Amount in ILS (decimal, not agorot) |
| `payment.currency` | String | `ILS` |
| `payment.id` | String | Grow payment ID |
| `payment.customer.name` | String | Customer name |
| `payment.customer.email` | String | Customer email |
| `payment.customer.phone` | String | Customer phone |
| `payment.installments` | Number | Number of installments |
| `payment.status` | String | `completed`, `failed`, `refunded` |

## Rate Limits and Best Practices

| Service | Rate Limit | Recommended Polling Interval |
|---|---|---|
| Green Invoice API | 100 req/min | 15 minutes |
| Monday.com API | 10,000 complexity/min | 5 minutes |
| Priority OData | Varies by installation | 15 minutes |
| WhatsApp Cloud API | 250 messages/sec (business) | N/A (event-driven) |
| Cardcom | No documented limit | N/A (webhook) |
| Tranzila | No documented limit | N/A (webhook) |

For all scheduled scenarios, prefer longer intervals (15+ minutes) during non-business hours to conserve Make.com operations.
