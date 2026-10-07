# Israeli Service Modules and HTTP Configurations for Make.com

Reference guide for connecting Israeli services in Make.com scenarios. Covers community and native modules, HTTP module configurations, authentication patterns, and payload examples.

## Morning (formerly Green Invoice / Hashbonit Yeruqa)

### Community Module (by Callbox)

Morning has a **community-built** Make.com module. Search "Morning" in the module palette. Listed as "Morning by Callbox". Requires a **Morning Best plan or higher** (Best is Morning's own subscription tier, the first with API access; it is not a Make plan). Make.com states: "Make does not maintain or support this integration."

**Connection Setup:**
1. Generate API keys in your Morning account. Morning issues them as OAuth 2.0 client credentials (client ID + secret), and "Each environment requires its own set of API keys" (Production and Sandbox).
2. In Make.com, create a new Morning connection with these credentials.

**Direct API (HTTP module):** POST `{"grant_type":"client_credentials","client_id":"...","client_secret":"..."}` to `https://api.morning.co/idp/v1/oauth/token`. The response's `accessToken` (a JWT, valid for 1 hour) goes in `Authorization: Bearer <accessToken>`. The production API base remains `https://api.greeninvoice.co.il/api/v1` despite the rebrand. Sandbox base and token URLs are on the Sandbox tab of `https://www.greeninvoice.co.il/api-docs`; sandbox documents are test data only.

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
| Add Supplier, Add Expense Draft by File, Get Document, Get a Preview Document | Also listed on the Callbox app page | See the app page |
| Make an API Call | Raw call to any Morning endpoint | Path, method, body |
| Make an API Call | Raw API request | Any Morning API endpoint |

### Document Type Codes

| Code | Type (English) | Type (Hebrew, as Morning names it) |
|---|---|---|
| 10 | Price quote | הצעת מחיר |
| 20 | Bill / payment confirmation | חשבון / אישור תשלום |
| 100 | Order | הזמנה |
| 200 | Delivery note | תעודת משלוח |
| 210 | Return note | תעודת החזרה |
| 300 | Transaction account (NOT a tax invoice) | חשבון עסקה |
| 305 | Tax invoice | חשבונית מס |
| 320 | Tax invoice / receipt | חשבונית מס / קבלה |
| 330 | Credit invoice | חשבונית זיכוי |
| 400 | Receipt | קבלה |
| 405 | Donation receipt | קבלה על תרומה |
| 410 | Donation cancellation | ביטול תרומה |
| 500 | Purchase order | הזמנת רכש |
| 600 | Deposit receipt | קבלת פיקדון |
| 610 | Deposit withdrawal | משיכת פיקדון |

For a paid gateway sale, an osek murshe normally issues 320 (tax invoice / receipt). Never use 300 for a paid sale: a transaction account is not a tax document, so a business buyer cannot deduct input VAT on it. Confirm the document policy with the business's accountant.

### Example: Create Tax Invoice Payload

```json
{
  "type": 305,
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
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
      "currency": "ILS"
    }
  ]
}
```

**Important:** `price` in the API is in **decimal shekels** (e.g., `15000` = 15,000 shekels). NOT agorot. Do NOT multiply by 100.

### Israel Invoice Reform 2026

Tax invoices over the Tax Authority allocation-number threshold require an allocation number (mispar hiktzava). The threshold steps down during 2026: 10,000 NIS from January 1, 2026, then 5,000 NIS from June 1, 2026 (the value in force now), compared on the amount BEFORE VAT. The published schedule ends at 5,000 NIS and no further step has been legislated; still hold the threshold in a scenario variable for maintainability.

Morning returns the number on the created document as `allocationNumber` ("Allocation Number issued by the Israeli Tax Authority"). Read it back and store it; alert when it is empty on an invoice to an osek murshe above the threshold. The gov.il online request form serves businesses on a paper booklet or unconnected software and asks for the customer's osek murshe number.

### VAT Type Values

`vatType` is required at document level, where Morning documents: 0 = default (VAT by business type), 1 = exempt (VAT-free), 2 = mixed (exempt and taxable rows). Income rows have their own `vatType` field; expand the income-row schema in Morning's API docs before setting it, and never assume a value means "VAT added on top". Setting the wrong value issues a VAT-exempt tax invoice or double-counts VAT.

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

iCount is a strong alternative to Morning for Israeli accounting automation, especially if you want a natively supported Make.com module. Make's app page notes it requires a paid iCount account.

## Monday.com

### Native Module

Monday.com has a built-in Make.com module.

**Make app version:** Make states "monday.com Version 1 is now legacy and its maintenance has ended". Use the upgrade arrow on each module to switch to Version 2.

**Important:** monday.com versions its API by DATE, not as v1/v2. `api.monday.com/v2` is the GraphQL endpoint path and is unrelated to the API version. Versions roll quarterly. Since October 1st, 2026 the current default is `2026-10`; `2026-07` is in maintenance and `2027-01` is the release candidate (current from January 15th, 2027). Set the version explicitly with an `API-Version` request header. Deprecations get at least six months' notice.

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

### Entities: read them from your installation

Entity (form) names and their fields are installation-dependent. Priority's own REST docs say forms and fields "must be matched exactly. When in doubt, check the metadata for the entity", and their examples use `ORDERS` (sales orders) with `ORDERITEMS` lines. For any other entity, read `{service root}/$metadata` from your own installation instead of guessing a form name.

Note: Hebrew values in OData filters must be URL-encoded. Make.com's HTTP module handles this automatically when using the query string builder.


### Priority API Gotchas

- Priority field names are ALL CAPS (e.g., `CUSTNAME`, not `custName`)
- Date format in responses: `YYYY-MM-DDT00:00:00+02:00` (Israel timezone offset)
- Hebrew text in responses is UTF-8 encoded
- Pagination: use `$skip` and `$top`
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
    "destinations": {
      "phone": [{ "_": "5xxxxxxxx" }]
    },
    "message": "הודעה בעברית"
  }
}
```

### InforUMobile

| Setting | Value |
|---|---|
| URL | `https://api.inforu.co.il/SendMessageXml.ashx` (XML) or `https://capi.inforu.co.il/api/v2/SMS/SendSms` (JSON REST). The legacy `http://api.inforu.co.il/SendMessage.asmx` does not resolve. |
| Method | POST |
| Content-Type | `application/xml` |

Note: the `SendMessageXml.ashx` endpoint takes XML, so set the Make.com HTTP module body type to "Raw" and build the XML string. The JSON alternative is the `capi.inforu.co.il` v2 REST endpoint. Take the exact XML/JSON schema from InforU's developer docs.

### SMS4Free

| Setting | Value |
|---|---|
| URL | `https://api.sms4free.co.il/ApiSMS/v2/SendSMS` |
| Method | POST |
| Content-Type | `application/json` |

The API host is `api.sms4free.co.il`; `www.sms4free.co.il/ApiSMS/...` only redirects to the marketing site. An unauthenticated POST returns `{"status":-1,"message":"Incorrect key, username or password"}`, so the call needs an API key, a username and a password. Take the exact JSON field names from SMS4Free's API documentation in your account rather than guessing them.

## Israeli Payment Gateway Webhooks

### Cardcom

**Webhook URL Setup:**
Cardcom has two webhook generations. The **current API v11** POSTs a JSON body to the `WebHookUrl` you pass in `LowProfile/Create` (a required field there); success is `ResponseCode` = 0 with `Description`, plus `TranzactionId` and `Amount`. Verify exact v11 field names against https://secure.cardcom.solutions/Api/v11/Docs before mapping them. The table below is the **legacy LowProfile (v10)** field set; it was NOT re-verified against a current Cardcom page this cycle, so confirm it against your own terminal's documentation.

**Legacy LowProfile (v10) callback fields (unverified this cycle):**

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

Grow (formerly Meshulam; meshulam.co.il now redirects to grow.business) is operated by Grow Payments Ltd, a licensed payment company, not by a bank.

Grow has two separate notification mechanisms. Do not mix their fields.

**1. `notifyUrl` server-to-server callback** (the URL you pass in CreatePaymentProcess): an HTTP POST, "NOT as JSON", with `err`, `status` and a `data` object (`sum`, `transactionId`, `transactionToken`, `asmachta`, `paymentsNum`, `allPaymentsNum`, `processId`, `processToken`, ...). It carries no `webhookKey`. "Upon receiving the update, you are required to execute the ApproveTransaction API call." ApproveTransaction "serves as an acknowledgment that your system has received the server notification"; it does not return a verified amount, and "The transaction will be processed even if the ApproveTransaction request is not executed or fails." Without acknowledgments Grow resends the update up to 5 additional times, so deduplicate on `transactionId`. The step "does not alter the transaction status"; "Do not send this request in the case of token transactions (created with createTransactionWithToken) or delayed transactions (J4J5), or for save token only scenarios." To re-check the amount, use Get Transaction Info, not ApproveTransaction.

**2. Dashboard Webhooks service** ("Contact our support team to enable Webhooks for your account"): flat fields such as `webhookKey`, `transactionCode`, `transactionType`, `paymentSum`, `paymentsNum`, `allPaymentNum`, `firstPaymentSum`, `paymentType`, `paymentDate`, `asmachta`, `paymentDesc`, `fullName`, `payerPhone`, `payerEmail`, `cardSuffix`. Compare `webhookKey` with your key. Recurring, failed-recurring and invoice webhooks use different formats; see `https://developers.grow.business/reference/webhooks`.

**Invoices:** Grow can issue invoices itself and sends a separate invoice webhook (`transactionCode`, `invoiceNumber`, `invoiceUrl`). If that is on, do not also create a Morning document for the same sale.

### Bit (by Bank HaPoalim)

Bit usually reaches a small business through a payment gateway (Grow and Tranzila both support it), so it arrives in that gateway's callback rather than from a separate Bit dashboard.

### PayMe (by Isracard)

Payment processing with installment support. Configure webhook URL in PayMe dashboard to receive payment status notifications.

### PayBox

Digital payment solution with webhook notifications for completed transactions.

## Rate Limits and Best Practices

| Service | Rate Limit | Recommended Polling Interval |
|---|---|---|
| Morning (Green Invoice) API | 100 req/min (uncited, confirm against Morning's docs before sizing a scenario) | 15 minutes |
| iCount API | Check iCount docs | 15 minutes |
| Monday.com API | Complexity budget, not a request count: 5M points/min each for reads and writes on an app token, or a combined 10M/min on a personal token (1M for trial, NGO and free accounts); a single query is capped at 5M | 5 minutes |
| Priority OData | Varies by installation | 15 minutes |
| WhatsApp Cloud API | Up to 80 messages/sec per business phone number by default, up to 1,000 by automatic upgrade; a number shared with the WhatsApp Business app (coexistence) is fixed at 20 | N/A (event-driven) |
| Cardcom | No documented limit | N/A (webhook) |
| Tranzila | No documented limit | N/A (webhook) |

For all scheduled scenarios, prefer longer intervals (15+ minutes) during non-business hours to conserve Make.com credits.

## Hebrew Month Names

Make has no native Hebrew month formatting. Get the numeric month with `formatDate(now; "M")`, then map it with a switch function or a Set Variable lookup:

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

## Make.com vs n8n vs Zapier

| Criteria | Make.com | n8n | Zapier |
|---|---|---|---|
| **Best for** | Visual automations, non-developers | Self-hosted, code-heavy workflows | Simple 2-app connections |
| **Israeli app modules** | Morning (community), iCount (native), Priority (community), Hebcal (community) | Fewer Israeli modules | Some Israeli apps |
| **AI Agents** | Built-in visual AI Agents | Via code nodes | Limited AI features |
| **Pricing** | Free: $0 (1,000 credits/mo, 2 active scenarios); Core from $9/mo; Pro from $16/mo; Teams from $29/mo | Free (self-hosted) | Paid plans; check zapier.com/pricing |
| **Community modules** | Growing Israeli ecosystem | npm packages | Fewer community options |

On Make, every paid plan schedules down to 1 minute; only Free is capped, at 15 minutes. Check n8n and Zapier limits on their own pricing pages.
