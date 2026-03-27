# Israeli Service Modules and HTTP Configurations for Make.com

Reference guide for connecting Israeli services in Make.com scenarios. Covers community and native modules, HTTP module configurations, authentication patterns, and payload examples.

## Morning (formerly Green Invoice / Hashbonit Yeruqa)

### Community Module (by Callbox)

Morning has a **community-built** Make.com module. Search "Morning" in the module palette. Listed as "Morning by Callbox". Requires **Best subscription tier or higher**. Make.com states: "Make does not maintain or support this integration."

**Connection Setup:**
1. Go to Morning dashboard: Settings > API Integration
2. Generate API Key and Secret
3. In Make.com, create a new Morning connection with these credentials
4. Select environment: Production or Sandbox

**Sandbox vs Production:**

| Setting | Sandbox | Production |
|---|---|---|
| Base URL | `https://sandbox.d.greeninvoice.co.il/api/v1/` | `https://api.greeninvoice.co.il/api/v1/` |
| Documents | Test only, not legally valid | Real tax documents |
| Rate limits | More lenient | Standard |

Note: The API domain remains `greeninvoice.co.il` despite the Morning rebrand.

### Available Actions (NO triggers/watches)

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
| Update Client | Modify existing client | Client ID + fields |
| Delete Client | Remove a client record | Client ID |
| Make an API Call | Raw API request | Any Morning API endpoint |

### Document Type Codes

| Code | Type (English) | Type (Hebrew) |
|---|---|---|
| 10 | Price Quote | הצעת מחיר |
| 100 | Order | הזמנה |
| 300 | Invoice + Receipt | חשבונית מס / קבלה |
| 305 | Tax Invoice | חשבונית מס |
| 320 | Tax Invoice / Receipt | חשבונית מס / קבלה |
| 330 | Credit Note / Refund | הודעת זיכוי |
| 400 | Receipt | קבלה |
| 405 | Purchase Order | הזמנת רכש |
| 500 | Delivery Note | תעודת משלוח |

### Example: Create Tax Invoice Payload

```json
{
  "type": 305,
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

**Important:** `price` in the API is in **decimal shekels** (e.g., `15000` = 15,000 shekels). NOT agorot. Do NOT multiply by 100.

### Israel Invoice Reform 2026

Since January 2026, invoices exceeding 10,000 NIS require a Tax Authority allocation number (mispar hiktzava). Include the `allocationNumber` field for qualifying documents:

```json
{
  "type": 305,
  "allocationNumber": "ALLOCATION_NUMBER_FROM_TAX_AUTHORITY",
  "income": [...]
}
```

### VAT Type Values

| Value | Meaning | When to Use |
|---|---|---|
| 0 | Exempt from VAT | Non-profit, certain services |
| 1 | VAT included in price | B2C, retail pricing |
| 2 | VAT excluded (added on top) | B2B, wholesale pricing |

## iCount

### Native Module

iCount has a **native (first-party) Make.com module**. Search "iCount" in the module palette.

**Available actions:**
- Expenses: Create, update, manage expense records
- Leads: Create and manage leads
- Tasks: Create and manage tasks
- Events: Create and manage calendar events
- Inventory: Manage inventory items
- Clients: Create and manage client records
- Documents: Create invoices, receipts, quotes

iCount is a strong alternative to Morning for Israeli accounting automation, especially if you want a natively supported Make.com module without the Best plan requirement.

## Monday.com

### Native Module

Monday.com has a built-in Make.com module.

**Important:** Monday.com API v1 is maintained only until May 1, 2026. The Make.com native module uses v2 by default. Do NOT create new scenarios with v1.

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

## Priority ERP

### Community Module

Priority has a **community-built Make.com module**. Search "Priority" in the module palette. This is simpler than the HTTP approach for common operations.

### HTTP Module (Full Control)

For full OData API access, use the HTTP module.

**HTTP Module Configuration:**

| Setting | Value |
|---|---|
| URL | `https://{domain}/odata/Priority/tabula.ini/{company}/{entity}` |
| Method | GET (read), POST (create), PATCH (update) |
| Auth | Basic Auth, PAT (Personal Access Token), or OAuth2 |
| Headers | `Content-Type: application/json`, `Accept: application/json` |

Replace `{domain}` with your Priority instance domain, `{company}` with the company name in Priority (usually "demo" for testing), and `{entity}` with the OData entity name.

Priority supports three authentication methods:
- **Basic Auth:** Username and password
- **Personal Access Token (PAT):** Token-based, more secure
- **OAuth2:** Full OAuth2 flow for enterprise integrations

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

## WhatsApp Business Cloud

### Native Module (Recommended)

Make.com has a **native first-party WhatsApp Business Cloud module**. Use this instead of the HTTP approach.

**Available triggers:**
- Watch Events: Incoming messages, status updates, read receipts

**Available actions:**
- Send a Message: Text, image, document, location messages
- Send a Template Message: Pre-approved templates (required for outbound initiation)

**Connection Setup:**
1. Connect your Meta Business account in Make.com
2. Select your WhatsApp Business phone number

### HTTP Module (Advanced)

For advanced use cases not covered by the native module:

**HTTP Module Configuration:**

| Setting | Value |
|---|---|
| URL | `https://graph.facebook.com/{api-version}/{phone-number-id}/messages` |
| Method | POST |
| Auth | Bearer Token (your permanent access token) |
| Headers | `Content-Type: application/json` |

Use the latest API version from Meta's changelog rather than hardcoding a version number.

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
| Auth | Bearer token: `Authorization: Bearer YOUR_TOKEN` |
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
| URL | `http://api.inforu.co.il/SendMessage.asmx` |
| Method | POST |
| Content-Type | `application/xml` |

Note: InforUMobile uses an ASMX web service with XML format, not JSON. Set the Make.com HTTP module body type to "Raw" and build the XML string. The endpoint is `.asmx` (not `.ashx`).

### SMS4Free

| Setting | Value |
|---|---|
| URL | `https://www.sms4free.co.il/ApiSMS/SendSMS` |
| Method | POST |
| Content-Type | `application/json` |

SMS4Free requires three credentials: `key`, `user`, and `pass`:

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
In the Cardcom dashboard, go to Settings > Notification URL > set your Make.com Custom Webhook URL. Cardcom API v11 supports modern webhook configuration.

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
| `npay` | String | Number of **additional** payments. Total installments = npay + 1. |
| `ConfirmationCode` | String | Bank confirmation code |
| `index` | String | Tranzila transaction index |
| `TranzilaTK` | String | Token for recurring charges |

**Tranzila API v2** introduces iframe-based hosted payment fields for PCI compliance and supports Bit payments.

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

### Grow (by Meshulam)

Grow is an independent fintech company by Meshulam (NOT affiliated with Bank Leumi).

**Webhook Payload (JSON POST):**

Grow sends a JSON payload. Verify authenticity by checking the `webhookKey` field in the JSON body (not a header).

**Webhook Verification:**
1. Parse the JSON body
2. Compare the `webhookKey` value against your configured key in Grow dashboard

**Important:** Grow's API uses **multipart/form-data** for outbound requests, not JSON. Configure your HTTP module accordingly when making API calls to Grow.

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
| `webhookKey` | String | Key for webhook verification |

### Bit (by Bank HaPoalim)

Bit is Israel's dominant P2P payment platform with a business API.

**Bit Business API:** Register for API access through the Bit Business program. Configure webhook URL in the Bit Business dashboard to receive payment notifications.

### PayMe (by Isracard)

Payment processing with installment support. Configure webhook URL in PayMe dashboard to receive payment status notifications.

### PayBox

Digital payment solution with webhook notifications for completed transactions.

## Rate Limits and Best Practices

| Service | Rate Limit | Recommended Polling Interval |
|---|---|---|
| Morning (Green Invoice) API | 100 req/min | 15 minutes |
| iCount API | Check iCount docs | 15 minutes |
| Monday.com API | 10,000 complexity/min | 5 minutes |
| Priority OData | Varies by installation | 15 minutes |
| WhatsApp Cloud API | 250 messages/sec (business) | N/A (event-driven) |
| Cardcom | No documented limit | N/A (webhook) |
| Tranzila | No documented limit | N/A (webhook) |

For all scheduled scenarios, prefer longer intervals (15+ minutes) during non-business hours to conserve Make.com credits.
