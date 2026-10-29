# Israeli Apps on Zapier: Connection Reference

This reference covers Israeli-origin and Israel-popular apps available on Zapier, including native integrations, webhook-based connections, and API-only workarounds.

## Native Zapier Integrations (Built-In)

These apps have official Zapier integrations with full trigger/action support.

### Monday.com

| Property | Value |
|----------|-------|
| Zapier search name | "monday.com" (slug `monday`) |
| Auth type | Managed by Zapier |
| Supported triggers | `New Item in Board`, `Any Column Value Changed in Board`, `Specific Column Value Changed in Board`, `Item Moved to Group (Same or Different Board)`, `New Update in Board`, `New Subitem on Board`, `New Board`, `New User` and further subitem variants (verbatim from the app directory, 2026-10-29). There is no trigger named "Status Changed": watch the status column with `Specific Column Value Changed in Board`. |
| Supported actions | `Create Item`, `Update Item`, `Create Update`, `Create Subitem`, `Move Item to Group`, `Update Item Name` among 19, plus searches such as `Find Items` |
| Notes | Global app with very strong Israeli adoption. Works seamlessly with Zapier. Good for project management workflows combined with Israeli billing apps. |

### Wix

| Property | Value |
|----------|-------|
| Zapier search name | "Wix" |
| Auth type | OAuth 2.0 |
| Supported triggers | Product-area triggers rather than single events: `eCommerce`, `Forms`, `Payments`, `Bookings`, `Members and Contacts`, `Pricing Plans` and more (you pick the specific event inside each, verbatim category names from the app directory, 2026-10-29) |
| Supported actions | **None.** The Wix app is trigger-only: it starts Zaps from Wix events but cannot create or update anything in Wix |
| Notes | Israeli-founded. Commonly used for e-commerce sites that need invoicing integration: an `eCommerce` order trigger feeding a Morning document is the usual shape. |

### SUMIT

| Property | Value |
|----------|-------|
| Zapier search name | "SUMIT" |
| Auth type | Managed by Zapier |
| Supported triggers | Card Updated |
| Supported actions | Create Document, Create Card, Update Card, Get Card, Send SMS, Add Recipient to Email Mailing List, Add Recipient to SMS Mailing List |
| Notes | Israeli invoicing and business-management platform, described on Zapier as "A comprehensive system for planning, management and execution for the self-employed, non-profit organizations and business organizations." Use `Create Document` rather than hand-building invoice HTTP calls. |

### Priority ERP

| Property | Value |
|----------|-------|
| Zapier search name | "Priority" |
| Auth type | Managed by Zapier |
| Supported triggers | Catch Changed Customer Order Status Webhook, Catch Changed Purchase Order Status Webhook, Catch Contacts Webhook |
| Supported actions | `Create a New Sales Order`, `Create a Sales Opportunity`, `Create New Lead in Priority`, `Find Customer by Email` (verbatim strings from the app directory, verified 2026-09-02; the app also exposes further order and candidate actions, read the directory before mapping) |
| Notes | Israeli ERP widely used in the local mid-market. A native Zapier app exists, so the OData-over-webhook approach is no longer the default path. On-premise installations may still require IP whitelisting. |

### InforUMobile

| Property | Value |
|----------|-------|
| Zapier search name | "InforUMobile" |
| Auth type | Managed by Zapier |
| Supported triggers | New Lead From Landing Page, Contact Unsubscribe |
| Supported actions | Send SMS, Send Whatsapp Template Message, Send SMS Voice Hybrid, Send IVR Campaign, Send IVR Message, Create and Send Newsletter, Send Newsletter Campaign, Add Contact to Group, Remove Contact From Group, Unsubscribe Contact, Reactivate Unsubscribe, Start Automation |
| Notes | Israeli SMS and multichannel marketing gateway, described on Zapier as "Multi channel marketing software offering SMS, email marketing, landing pages, surveys and Facebook advertising." Hebrew supported. `Send Whatsapp Template Message` is a native Israeli WhatsApp path that avoids adding a separate BSP. |

### PayPlus

| Property | Value |
|----------|-------|
| Zapier search name | "PayPlus" (slug `payplus`; the app lists `https://www.payplus.co.il/` as its site) |
| Auth type | API key plus Secret key from the PayPlus dashboard |
| Supported triggers | `New Approval`, `New Charge`, `New Invoice` |
| Supported actions | None (trigger-only) |
| Notes | The one Israeli payment gateway in this reference with a native Zapier app, documented on PayPlus's own knowledge base ("Zapier Documentation"). Event subscriptions are per company, not per user: PayPlus says each event "can only be subscribed to once per company", so a second Zap on the same event from a colleague's login will not register. Amount units are not stated in that documentation; check a test payload before mapping. |

**Note on Elementor:** earlier versions of this reference listed Elementor as a native Zapier app. It has no app in the Zapier directory. Elementor Pro Forms integrates with Zapier through a webhook configured on the WordPress side, so treat it as a webhook source, not a Zapier app.

## Webhook-Based Connections (No Native Integration)

These apps do not have native Zapier integrations. Connect them via "Webhooks by Zapier."

### Morning (formerly Green Invoice / Hashbonit Yeruka)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | **OAuth 2.0 client_credentials.** POST a JSON body `{"grant_type":"client_credentials","client_id":"...","client_secret":"..."}` with header `Content-Type: application/json` to `https://api.morning.co/idp/v1/oauth/token`, take `accessToken` from the response and send it as `Authorization: Bearer <accessToken>`. The token is a signed JWT valid for **1 hour**, so a Zap must fetch one per run rather than carrying a pasted token. |
| API base URL | `https://api.greeninvoice.co.il/api/v1` (sandbox `https://sandbox.d.greeninvoice.co.il/api/v1`). The token path is the exception and overrides to `https://api.morning.co` (sandbox `https://api.sandbox.morning.dev`). |
| Dashboard | `https://app.greeninvoice.co.il/login` |
| API documentation | `https://developers.morning.co/` (the old `greeninvoice.co.il/api-docs/` URL now redirects here) |
| API key location | Dashboard > Settings > API Integration at app.greeninvoice.co.il. These are the client ID and secret you exchange for a token; they are not themselves the Bearer token. |
| Amount unit | **Decimal shekels** (e.g., 150.50 = 150.50 ILS) |
| Document type codes | 10=Price Quote, 305=Tax Invoice, 320=Tax Invoice/Receipt, 330=Credit Note/Refund, 400=Receipt |
| Notes | No native Zapier app exists. Morning (formerly Green Invoice) is the most popular Israeli invoicing platform. All connections must use "Webhooks by Zapier" with Morning's REST API. The API domain remains `api.greeninvoice.co.il`. |

**Common field mappings for Morning documents:**

| Morning API Field | Description | Format |
|-------------------|-------------|--------|
| `type` | Document type code | Integer (10, 305, 320, 330, 400) |
| `client.name` | Client name | String (Hebrew OK) |
| `client.emails` | Client email(s) | Array of strings |
| `client.taxId` | Buyer's ח.פ. / osek number or ID | String (digits) |
| `currency` | Currency code | `ILS` for shekels |
| `lang` | Document language, **required** | e.g. `he` |
| `income[].description` | Line row description, required per row | String (Hebrew OK) |
| `income[].price` | Price per unit in decimal ILS, required per row | Number (e.g., 150.50) |
| `income[].quantity` | Quantity, required per row | Number |
| `income[].currency` | Row currency, required per row | `ILS` |
| `income[].vatType` | Row VAT type, required per row (`ItemVatType`) | `0` = VAT added on top of `price`, `1` = `price` already includes VAT, `2` = exempt |
| `vatType` | Document VAT type, **required** (`DocumentVatType`, a DIFFERENT enum) | `0` = default for the business type, `1` = **exempt**, `2` = mixed |

**The two `vatType` fields use different codes, and confusing them issues a wrong tax document.** At row level `1` means
"VAT included"; at document level `1` means **VAT-exempt**. A gateway amount (Cardcom `TranzactionInfo.Amount`, Grow
`paymentSum`) already includes VAT, so the safe mapping for an osek murshe is document `vatType: 0` and row `vatType: 1`.
Row `vatType: 0` with a gross amount adds 18% on top and overstates the document; document `vatType: 1` issues it as exempt.

**Verified against the live spec on 2026-10-29** (`https://developers.morning.co/docs/openapi.bundled.json`). Two traps
here, both of which produce a hard 400:

- The line array is **`income[]`, not `items[]`**, and the price field is **`price`, not `unitPrice`**. `CreateDocumentRequest`
  has no `items` property at all.
- `CreateDocumentRequest.required` is `["type","lang","currency","vatType","income"]`, so **`lang` is mandatory** and is the
  field most often omitted. Each `income[]` row separately requires `description`, `quantity`, `price`, `currency` and `vatType`.

**The create response does not carry the allocation number.** `CreateDocumentResponse` returns `id`, `number`, `dueDate`,
`type`, `signed`, `lang`, `client`, `url`, `vatRate`, `taxAuthorityConfirmationInitiated` and `taxAuthorityConfirmationLastError`.
`allocationNumber` is a field on the `Document` schema, so read it from `GET /documents/{id}` or from the `document/created`
webhook, never from the 201.

**A receipt-type document records the payment in `payment[]`.** For 320 or 400, each `payment[]` row requires `date`, `type`,
`price` and `currency`; the installment count is `payment[].numPayments` (there is no `installments` field). Document search
is `POST /documents/search` with a JSON filter (`fromDate`, `toDate`, `type`, `status`, `page`, `pageSize`).

### Cardcom (Kardkom)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Pass the Catch Hook URL as the `WebHookUrl` field on each `CreateLowProfile` API request. `WebHookUrl` is a required field on that request. |
| Callback method | **JSON POST** carrying a `LowProfileResult` object (not a GET with query parameters) |
| API docs | `https://secure.cardcom.solutions/swagger/index.html`, spec at `https://secure.cardcom.solutions/swagger/v11/swagger.json` |
| Amount location | **`TranzactionInfo.Amount`**, NOT a top-level `Amount`. Verified against the v11 spec on 2026-09-02: `LowProfileResult` has no `Amount` property. `TranzactionInfo` is documented as "Will no be null at operations: ChargeOnly, ChargeAndCreateToken", so guard for null. The `Amount` people copy from the docs is on the `CreateLowProfile` REQUEST schema, not the callback. |
| Amount unit | **Decimal shekels** (150.50 = 150.50 ILS), `format: decimal`. Do NOT divide by 100. |
| Key fields | `ResponseCode` (0 = success), `Description` (text for the response code), `TranzactionId` (credit-card transaction ID), `LowProfileId`, `ReturnValue` (echo of what you sent, typically your order ID), `TranzactionInfo.Amount` (decimal ILS), and cardholder details nested under `UIValues`. Full top-level set: `ResponseCode`, `Description`, `TerminalNumber`, `LowProfileId`, `TranzactionId`, `ReturnValue`, `Operation`, `UIValues`, `DocumentInfo`, `TokenInfo`, `SuspendedInfo`, `TranzactionInfo`, `ExternalPaymentVector`, `Country`, `UTM`, `IssuerAuthCodeDescription`, `AccountId`, `PendingReason` (why a deal is still pending, ResponseCodes 5117/5118/5119). `Operation` is one of `ChargeOnly`, `ChargeAndCreateToken`, `CreateTokenOnly`, `SuspendedDeal`, `Do3DSAndSubmit`; filter on it, because a successful token-only deal also returns `ResponseCode` 0 with no `TranzactionInfo`. Inside `TranzactionInfo`: `CoinId` (1 ILS, 2 USD), `IsRefund`, `CreateDate`, `Last4CardDigitsString`, `NumberOfPayments`, `FirstPaymentAmount`. `DocumentInfo` is filled when Cardcom itself created a document. |
| `UIValues` sub-fields | `CardOwnerName`, `CardOwnerEmail`, `CardOwnerPhone`, `CardOwnerIdentityNumber`, `NumOfPayments`, `CardYear`, `CardMonth`, `IsAbroadCard`, `CustomFields`. The phone is empty unless the request's `UIDefinition` sets `IsCardOwnerPhoneRequired` |
| Re-fetch | `POST https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult` with `TerminalNumber`, `ApiName`, `LowProfileId`; returns the same `LowProfileResult` |
| Installments (tashlumim) | `UIValues.NumOfPayments` indicates installment count. |

**Legacy note:** older Cardcom integrations configured an `IndicatorUrl` in terminal settings that fired a GET with query parameters including `InternalDealNumber` and `DealResponse`. Neither `IndicatorUrl` nor `DealResponse` appears in the v11 API. In v11, `InternalDealNumber` is not in `LowProfileResult` or `TransactionInfo`, so it is not a webhook field. Migrate legacy Zaps to `WebHookUrl` and `ResponseCode`.

### Tranzila

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | **Notify URL.** Either pass `notify_url_address` on the iframe/redirect payment page, or set it in my.tranzila: Settings > Terminal > Payment Page > Security > Notify URL, with Notify Format `QSTR` |
| Callback method | Form-encoded POST (`application/x-www-form-urlencoded`), **not JSON**. Catch Hook parses it; map the fields by name |
| Payment integration | Iframe payment page with hosted fields (PCI compliant). **The legacy iframe on `direct.tranzila.com` is being retired: Tranzila marks it deprecated with official support ending on 1 January 2027, and points to the DirectNG iframe at `https://directng.tranzila.com/terminalname/iframenew.php`, which keeps `notify_url_address`** |
| API docs | `https://docs.tranzila.com/` |
| Amount unit | **Decimal ILS** (e.g., 250.00 = 250.00 ILS) |
| Notify fields | `Response` (`000` or `0` = success), `sum` (decimal ILS), `TranzilaTK`, `ConfirmationCode`, `currency` (1 = ILS), plus the request parameters you sent (`contact`, `email`, `phone`, `company`) echoed back. Tranzila's iframe docs say the same transaction data goes to the Notify page in parallel, and their response examples carry further fields (card, index and token details); map any of those only from one real test payload |
| Notes | Widely used Israeli payment processor. Supports Bit payments (Tranzila's docs carry a dedicated Bit API page). Tranzila's iframe docs say that "If a Notify page was defined, transaction data will also be sent to it in parallel" to the success/failure redirect, so the notify call is the server-to-server path a Zap should use, not the cardholder's browser redirect. Filter on `Response` before creating any document. The field list comes from Tranzila's own Notify-page guide (`docs.tranzila.com/docs/vibe-coding/closing-an-order-in-base44-using-notify-page`); confirm it with one test transaction. Tranzila's docs also now carry Invoices and Reports API sections. |

### Grow by Meshulam

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Docs | `https://developers.grow.business` |
| Webhook configuration | **Enabled by Grow support**, not self-serve: Grow's docs say "Contact our support team to enable Webhooks for your account." |
| Callback method | The Webhooks service sends **JSON**. The separate API callback (the `notifyUrl` on `CreatePaymentProcess`) is a form POST, "NOT as JSON", and requires you to call `ApproveTransaction` back, so it is not a fit for a bare Catch Hook |
| Amount unit | **Decimal ILS** (`"paymentSum":2.00` in Grow's example) |
| Payment methods | Grow's webhook examples show only `transactionType` `אשראי` (with a numeric `transactionTypeId`). Other methods' strings are not in that page, so read them from a test payload before branching on them |
| Key fields (Webhooks service) | `transactionCode`, `paymentSum`, `paymentsNum`, `transactionType`, `paymentDate` (day-first, e.g. `14/10/21`), `asmachta`, `fullName`, `payerPhone`, `payerEmail`, `cardSuffix`, `webhookKey`. Note `allPaymentNum` here vs `allPaymentsNum` on the API callback |
| Notes | Israeli payment gateway by Meshulam (not by any bank). Growing adoption among small businesses. One of the few gateways with native Bit support. **Do not search Zapier for "Grow":** `zapier.com/apps/grow` is an unrelated US product ("Grow helps publishers build their mailing list"). Grow by Meshulam has no Zapier app. The `webhookKey` in the body identifies your account; check it in a Filter step. |

### iCount

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | Long-lived API token sent as `Authorization: Bearer` (iCount's recommended method); base `https://api.icount.co.il/api/v3.php/`, docs at `https://apiv3.icount.co.il/` |
| API format | REST API, POST JSON |
| Amount unit | Decimal ILS. Item `unitprice` is before VAT; `unitprice_incvat` takes a VAT-inclusive price and iCount extracts the VAT, which is the field to map a gateway total into |
| Notes | Israeli accounting SaaS. REST API for creating invoices, receipts, expenses, and managing contacts. No native Zapier integration. |

### EZcount

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | `api_key` plus `developer_email` in the request body; `demo.ezcount.co.il` for testing and `api.ezcount.co.il` for production, with different keys |
| API format | REST API |
| Amount unit | Decimal ILS |
| Notes | Popular Israeli invoicing platform. API supports document creation, customer management, and payment tracking. **Trap:** in a `createDoc` item, money is `price` and **`amount` is the QUANTITY**. Mapping a gateway "amount" into `amount` issues a document for N units. |

### Rivhit (Accounting Software)

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier (Webhooks by Zapier > Custom Request) |
| Auth | `api_token` (Rivhit Merchant API Identifier) sent as a body parameter on each POST, not an Authorization header |
| API base URL | `https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/` |
| Key endpoints | `Document.New`, `Customer.New`, `Customer.List`, `Document.List` (dot-separated, POST, e.g. `https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Document.New`). Documented at `https://rivhit-api.readme.io/reference/api-reference-overview`. The bare `.svc/` base returns 404 to an unauthenticated request; that is expected, not an outage. |
| Notes | Popular Israeli accounting software. No native Zapier integration. Use outbound HTTP requests from Zapier to create documents. |

### Hashavshevet (Accounting)

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier, if the installed version exposes an API |
| Notes | Legacy Israeli accounting software. API availability and its auth method vary by version and are not published; ask the vendor before planning a Zap. |

## SMS and Messaging Providers

### InforUMobile (Israeli SMS Gateway)

**Use the native Zapier app.** See the InforUMobile entry under Native Zapier Integrations above: the `Send SMS` and `Send Whatsapp Template Message` actions replace the hand-built XML call for most workflows.

| Property | Value |
|----------|-------|
| Preferred connection | Native Zapier app ("InforUMobile") |
| Fallback connection | Webhooks by Zapier > Custom Request |
| Fallback API endpoint | `POST https://capi.inforu.co.il/api/v2/SMS/SendSms` (JSON), the API documented at `https://apidoc.inforu.co.il/` |
| Fallback auth | HTTP Basic auth |
| Notes | Popular Israeli SMS provider. Hebrew text supported natively. Only drop to the raw API for cases the native app's actions do not cover. The older `https://api.inforu.co.il/SendMessageXml.ashx` (credentials inside an XML body) still answers but no longer appears in InforU's API docs; do not build new flows on it. |

### 019 SMS

| Property | Value |
|----------|-------|
| Connection method | HTTP POST via Zapier |
| Auth | API token created in the 019 web interface (creating tokens from a username and password is no longer supported) |
| API endpoint | `https://019sms.co.il/api`, XML or JSON over HTTP POST, docs at `https://docs.019sms.co.il/` |
| Notes | Israeli SMS API. Supports Hebrew. |

### WhatsApp on Zapier: two different apps

| Zapier app | Reaches | Capability |
|------------|---------|------------|
| WhatsApp Notifications | Only the phone number that authenticated the connection. Premium app since 1 October 2025, so paid plans only | Single `Send Message` action, restricted to prefilled templates that cannot be customized. Described on Zapier as "Receive notifications on WhatsApp." Internal alerting only. |
| **WhatsApp Business** | **Customers** (premium app, paid plans only) | Triggers `New Message Received`, `Message Status Updated`. Actions `Send Template Message`, `Send Freeform Message` and `Send Media Message` (both of the last two only inside the 24-hour customer-service window); search `Get Attachment`. Described on Zapier as "a customer messaging app that delivers fast, reliable communication through organized chats, automated responses, and business profiles." |

Use **WhatsApp Business** for customer-facing Hebrew messaging. Outside the 24-hour window a Meta-approved template is required; inside it, freeform Hebrew works. InforUMobile's native app also offers `Send Whatsapp Template Message` if you already use it for SMS.

The BSP providers below are worth adding only for high volume, a shared team inbox, or multi-channel routing beyond what the native app covers:

#### Twilio WhatsApp Business API

| Property | Value |
|----------|-------|
| Zapier search name | "Twilio" |
| Auth type | Account SID + Auth Token |
| Action | Send WhatsApp Message |
| Phone format | Must use +972 prefix (drop leading 0) |
| Notes | Requires Twilio WhatsApp Business API account with Meta Business verification. Customer-facing messages must use Meta-approved templates. Hebrew templates are supported but must be submitted for approval; Meta's template documentation says review can take up to 24 hours. |

#### WATI

| Property | Value |
|----------|-------|
| Zapier search name | "WATI" |
| Auth type | API key |
| Action | Send Template Message |
| Notes | WhatsApp Business API provider with native Zapier integration. Good for high-volume messaging. Requires Meta Business verification and template approval. |

#### Respond.io

| Property | Value |
|----------|-------|
| Zapier search name | "Respond.io" (app slug `respondio`, not `respond-io`) |
| Auth type | API key |
| Notes | Omnichannel messaging platform with WhatsApp Business support. Native Zapier integration. Requires Meta Business verification. |

## Gov.il and Government Services

### Gov.il Forms

| Property | Value |
|----------|-------|
| Connection method | Email notifications from form submissions (use Gmail trigger > New Email matching specific subject) |
| Notes | No unified API and no verified webhook support. Each ministry/service has its own form system. The most reliable approach is to use email notifications from gov.il forms as Zapier triggers. |

### Bituach Leumi (National Insurance)

| Property | Value |
|----------|-------|
| Connection method | No API. Manual or email-based. |
| Notes | No automation path. Use scheduled reminders for payment deadlines instead. A self-employed direct debit (הוראת קבע) is charged on the 22nd of each month for the previous month, moved when the 22nd falls on Shabbat or a holiday (btl.gov.il); card payers pay on the dates in the payment slip Bituach Leumi sends. |

### Israel Tax Authority (Rashut HaMisim)

| Property | Value |
|----------|-------|
| Connection method | No direct API for Zapier. |
| Notes | Allocation numbers are requested manually on the Tax Authority's online form or automatically by invoicing software connected to its systems, so route documents through such a platform (Morning and others) rather than calling the Tax Authority from Zapier. Since June 2026 a tax invoice over 5,000 NIS **before VAT** to an Israeli business that deducts input VAT needs one, and must carry the buyer's ח.פ. |

## Field Mapping Quick Reference

Common fields across Israeli payment processors, mapped to Morning document fields. All amounts are decimal units of the transaction currency, never agorot; check the currency field before treating one as ILS.

Tranzila fields come from its Notify-page guide and Grow fields from its Webhooks service docs; confirm both against one test payload. Every gateway amount below INCLUDES VAT, so map it with Morning row `vatType: 1` (see the Morning section).

| Concept | Cardcom v11 Field | Tranzila Notify Field | Grow Webhook Field | Morning API Field |
|---------|-------------------|-----------------------|--------------------|-------------------|
| Transaction ID | `TranzactionId` | `ConfirmationCode` / `TranzilaTK` | `transactionCode` | (auto-generated) |
| Success flag | `ResponseCode` (0 = success) | `Response` (`000` = success) | (webhook fires on payment) | N/A |
| Your order ID | `ReturnValue` | (your own request parameter, echoed) | N/A | N/A |
| Amount (decimal, VAT-inclusive) | `TranzactionInfo.Amount` | `sum` | `paymentSum` | `income[].price` with row `vatType: 1` |
| Customer name | `UIValues.CardOwnerName` | `contact` (echoed request parameter) | `fullName` | `client.name` |
| Customer email | `UIValues.CardOwnerEmail` | `email` (echoed request parameter) | `payerEmail` | `client.emails[0]` (array) |
| Customer phone | `UIValues.CardOwnerPhone` | `phone` (echoed request parameter) | `payerPhone` | `client.phone` |
| Installments | `UIValues.NumOfPayments` | not verified | `paymentsNum` | `payment[].numPayments` |
| Payment method | credit card, unless `ExternalPaymentVector` shows Bit or PayPal on a test payment | not verified | `transactionType` | `payment[].type` |
| Currency | `TranzactionInfo.CoinId` (1 ILS, 2 USD, otherwise ISO 4217) | `currency` (1 = ILS) | not verified, check a test payload | `currency` |


## Per-vendor connection detail (relocated from SKILL.md)

**Morning (formerly Green Invoice) API setup:**
1. Log in to Morning dashboard (app.greeninvoice.co.il)
2. Navigate to Settings > API Integration
3. Generate an API key: this gives you a client ID and secret, not a Bearer token
4. In the Zap, add a Custom Request that POSTs the JSON token request to `https://api.morning.co/idp/v1/oauth/token` (header `Content-Type: application/json`) on every run
5. Call Morning's REST API at `api.greeninvoice.co.il` with `Authorization: Bearer <accessToken>` from that step

**Morning document type codes** (use numeric codes in API calls):

| Code | Document Type | Hebrew |
|------|--------------|--------|
| 10 | Price Quote | הצעת מחיר |
| 305 | Tax Invoice | חשבונית מס |
| 320 | Tax Invoice/Receipt | חשבונית מס קבלה |
| 330 | Credit Note/Refund | חשבונית זיכוי |
| 400 | Receipt | קבלה |

**Cardcom `WebHookUrl` setup (API v11):**
1. In Zapier, create a new Zap with "Webhooks by Zapier" as the trigger
2. Choose "Catch Hook" as the trigger event
3. Copy the generated webhook URL
4. Pass that URL as the `WebHookUrl` field on every `CreateLowProfile` request. It is a required field, alongside `TerminalNumber`, `ApiName`, `Amount`, `SuccessRedirectUrl` and `FailedRedirectUrl`
5. On payment completion Cardcom sends a **JSON POST** body (a `LowProfileResult` object) to that URL
6. Key fields: `ResponseCode` (0 = success), `TranzactionId` (credit-card transaction ID), `LowProfileId`, `ReturnValue` (whatever you sent on the request, typically your order ID), `TranzactionInfo.Amount` (decimal shekels, e.g., 150.50; there is NO top-level `Amount` on the callback, and `TranzactionInfo` is null outside `ChargeOnly` / `ChargeAndCreateToken`), and cardholder details nested under `UIValues`: `UIValues.CardOwnerName`, `UIValues.CardOwnerEmail`, `UIValues.CardOwnerPhone`, `UIValues.NumOfPayments`
7. Make a test payment to send sample data to Zapier

Older Cardcom integrations used an `IndicatorUrl` configured in terminal settings that fired a GET with query parameters. That mechanism does not appear in the v11 API. If an existing Zap is built on `IndicatorUrl` and `DealResponse`, it is on the legacy path and should be migrated to `WebHookUrl` and `ResponseCode`.

**Tranzila setup (modern API V2):**
Tranzila has moved to iframe-based API V2 with hosted fields for PCI compliance.

**Tranzila Notify URL setup:**
1. In Zapier, create a Catch Hook and copy its URL
2. Either send it as `notify_url_address` when you build the payment page, or paste it in my.tranzila under Settings > Terminal > Payment Page > Security > Notify URL, and set Notify Format to `QSTR`
3. Tranzila POSTs the transaction form-encoded to that URL in parallel with the cardholder's redirect
4. Filter on `Response` = `000` (or `0`), then map `sum`, `ConfirmationCode` and the contact fields you sent
5. Run one real test transaction and map from the payload Zapier actually caught



## Connection method by app (relocated from SKILL.md Step 2)

| App | Connection Method | Auth Type | Notes |
|-----|-------------------|-----------|-------|
| Morning (formerly Green Invoice) | Webhooks by Zapier | Token exchange, see note | No native Zapier app for Morning. Connect via webhooks: use Morning's webhook notifications as triggers and their REST API via Webhooks by Zapier for actions. Auth is OAuth 2.0: the current spec (`https://developers.morning.co/docs/openapi.bundled.json`, info.version 2.0.0) documents `POST https://api.morning.co/idp/v1/oauth/token` with `grant_type=client_credentials`, returning a short-lived JWT sent as `Authorization: Bearer`. Errors follow the RFC 6749 OAuth error format: 400 `invalid_request` (missing `grant_type`), 400 `unsupported_grant_type`, 400 `invalid_grant` (API key privilege expired, revoked or pending), 400 `unauthorized_client` (no active subscription, or one without API access), 401 `invalid_client` (missing or wrong `client_id` / `client_secret`, or a blocked account). The production base for all other calls is still `https://api.greeninvoice.co.il/api/v1` (sandbox `https://sandbox.d.greeninvoice.co.il/api/v1`); the token path itself overrides to `https://api.morning.co` (sandbox `https://api.sandbox.morning.dev`). The token is a signed JWT valid for 1 hour, so refresh it rather than caching it across a long Zap run. The legacy `POST /api/v1/account/token` is gone: it is absent from the spec and returned HTTP 404 on 2026-10-29 while neighbouring endpoints answered 401, so any Zap still using it is broken. Amounts are decimal shekels, never agorot. |
| Cardcom | Webhooks by Zapier | `WebHookUrl` (JSON POST callback) | Cardcom POSTs a JSON body to the `WebHookUrl` you supply on the `CreateLowProfile` request. `WebHookUrl` is a required field on that request. |
| Tranzila | Webhooks by Zapier | Notify URL (form POST) | Tranzila V2 uses iframe-based hosted fields for payment. Point its Notify URL at a Catch Hook; the notification is form-encoded, not JSON. See the Tranzila section above. |
| monday.com | Zapier native integration | Managed by Zapier | Full support. monday.com is a global app with strong Israeli adoption. |
| PayPlus | **Zapier native integration** | API key + Secret key | Israeli payment gateway. Trigger-only app: `New Approval`, `New Charge`, `New Invoice`. One subscription per event per company. |
| SUMIT | **Zapier native integration** | Managed by Zapier | Israeli invoicing and business-management platform. Native app with a `Card Updated` trigger and `Create Document`, `Create Card`, `Update Card`, `Get Card`, `Send SMS` actions. Use `Create Document` instead of hand-rolling invoice HTTP calls. |
| Priority ERP | **Zapier native integration** | Managed by Zapier | Israeli ERP. Native app with `Catch Changed Customer Order Status Webhook` and `Catch Changed Purchase Order Status Webhook` triggers, plus `Create a New Sales Order`, `Create a Sales Opportunity`, `Create New Lead in Priority` and `Find Customer by Email` actions. Check the exact strings in the app directory before mapping them; several differ from the shorthand people use. |
| InforUMobile | **Zapier native integration** | Managed by Zapier | Israeli SMS and marketing gateway. Native app with `New Lead From Landing Page` trigger and `Send SMS`, `Send Whatsapp Template Message`, `Add Contact to Group` actions. Prefer this over the raw XML API. |
| iCount | Webhooks by Zapier | API key | Israeli accounting SaaS. No native Zapier app. Use iCount REST API via Webhooks by Zapier for creating invoices, receipts, and managing contacts. |
| EZcount | Webhooks by Zapier | API key | Popular Israeli invoicing platform. No native Zapier app. REST API for document creation and customer management. |
| Grow by Meshulam | Webhooks by Zapier | Webhook URL, enabled by Grow support | Israeli payment gateway supporting credit cards, Bit, Apple Pay, Google Pay. Its Webhooks service sends JSON (`transactionCode`, `paymentSum`, `fullName`, `payerEmail`), per `developers.grow.business`. **Do not search Zapier for "Grow"**: the app at `zapier.com/apps/grow` is an unrelated US mailing-list product ("Grow helps publishers build their mailing list"), not Meshulam. |
| Rivhit (accounting) | Webhooks by Zapier | `api_token` in the request body | No native integration. Use webhook + custom API calls. |
| 019 SMS | Webhooks by Zapier | API token | No native Zapier app. Send SMS via HTTP POST to `https://019sms.co.il/api`. |



## שיטת חיבור לפי אפליקציה (הועבר מ-SKILL_HE.md שלב 2)

אפליקציות ישראליות מתחברות ל-Zapier בשלוש דרכים. **תמיד בדוק קודם בספריית האפליקציות של Zapier** (`zapier.com/apps/<app-slug>/integrations`): כמה ספקים ישראליים כבר מציעים אפליקציה מובנית, ואפליקציה מובנית תמיד פשוטה ואמינה יותר מ-Custom Request שבונים ביד. רד ל-webhooks רק כשאין אפליקציה מובנית.

| אפליקציה | שיטת חיבור | סוג אימות | הערות |
|----------|-----------|----------|-------|
| Morning (חשבונית ירוקה) | Webhooks by Zapier | OAuth 2.0, ראו הערה | אין אפליקציה מובנית של Morning ב-Zapier. חיבור דרך webhooks: שימוש ב-webhook notifications של Morning כטריגרים וב-REST API שלהם דרך Webhooks by Zapier לפעולות. האימות הוא OAuth 2.0: המפרט הנוכחי (`https://developers.morning.co/docs/openapi.bundled.json`, גרסה 2.0.0) מתעד את `POST https://api.morning.co/idp/v1/oauth/token` עם `grant_type=client_credentials`, שמחזיר JWT קצר-מועד שנשלח כ-`Authorization: Bearer`. בסיס הייצור לשאר הקריאות עדיין `https://api.greeninvoice.co.il/api/v1`. נקודת הקצה הישנה `POST /api/v1/account/token` הוסרה: היא נעדרת מהמפרט והחזירה HTTP 404 ב-29.10.2026 בזמן שנקודות קצה סמוכות החזירו 401, ולכן כל Zap שעדיין משתמש בה שבור. הסכומים שקלים עשרוניים, לא אגורות. |
| קארדקום (Cardcom) | Webhooks by Zapier | `WebHookUrl` (callback בשיטת JSON POST) | קארדקום שולח גוף JSON לכתובת `WebHookUrl` שמעבירים בבקשת `CreateLowProfile`. זהו שדה חובה באותה בקשה. |
| טרנזילה (Tranzila) | Webhooks by Zapier | Notify URL (POST בקידוד טופס) | טרנזילה V2 משתמשת ב-iframe עם hosted fields. כוונו את ה-Notify URL שלה ל-Catch Hook; ההתראה מקודדת כטופס ולא JSON. ראו את סעיף טרנזילה למעלה. |
| monday.com | אינטגרציה מובנית ב-Zapier | מנוהל על ידי Zapier | תמיכה מלאה. |
| PayPlus | **אינטגרציה מובנית ב-Zapier** | מפתח API ומפתח סודי | שער תשלומים ישראלי. אפליקציה עם טריגרים בלבד: `New Approval`, `New Charge`, `New Invoice`. מינוי אחד לכל אירוע לכל חברה. |
| SUMIT | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | פלטפורמת חשבוניות וניהול עסקי ישראלית. אפליקציה מובנית עם טריגר `Card Updated` ופעולות `Create Document`, `Create Card`, `Update Card`, `Get Card`, `Send SMS`. עדיף על בניית קריאות HTTP ידניות. |
| Priority ERP | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | מערכת ERP ישראלית. אפליקציה מובנית עם טריגרים `Catch Changed Customer Order Status Webhook` ו-`Catch Changed Purchase Order Status Webhook`, ופעולות `Create a New Sales Order`, `Create a Sales Opportunity`, `Create New Lead in Priority`, `Find Customer by Email`. בדקו את המחרוזות המדויקות בספריית האפליקציות לפני מיפוי, כמה מהן שונות מהקיצור שנהוג להשתמש בו. |
| InforUMobile | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | שער SMS ושיווק ישראלי. אפליקציה מובנית עם טריגר `New Lead From Landing Page` ופעולות `Send SMS`, `Send Whatsapp Template Message`, `Add Contact to Group`. עדיף על ה-API הגולמי ב-XML. |
| iCount | Webhooks by Zapier | מפתח API | מערכת הנהלת חשבונות ישראלית ללא אפליקציה מובנית. שימוש ב-REST API ליצירת חשבוניות, קבלות וניהול לקוחות. |
| EZcount | Webhooks by Zapier | מפתח API | פלטפורמת חשבוניות ישראלית פופולרית עם REST API. |
| Grow by Meshulam | Webhooks by Zapier | כתובת Webhook, מופעל דרך התמיכה של Grow | שער תשלומים ישראלי שתומך בכרטיסי אשראי, ביט, Apple Pay, Google Pay. שירות ה-Webhooks שלו שולח JSON (`transactionCode`, `paymentSum`, `fullName`, `payerEmail`), לפי `developers.grow.business`. **אל תחפשו "Grow" ב-Zapier**: האפליקציה בכתובת `zapier.com/apps/grow` היא מוצר אמריקאי לא קשור לניהול רשימות תפוצה, לא משולם. |
| ריווחית (Rivhit) | Webhooks by Zapier | `api_token` בגוף הבקשה | אין אינטגרציה מובנית. webhook + קריאות API. |
| 019 SMS | Webhooks by Zapier | טוקן API | אין אפליקציה מובנית. שליחת SMS דרך HTTP POST לכתובת `https://019sms.co.il/api`. |

**הגדרת API של Morning (חשבונית ירוקה):**
1. היכנס לדשבורד של Morning באתר app.greeninvoice.co.il
2. נווט להגדרות > אינטגרציית API
3. צרו מפתח API: הוא נותן מזהה לקוח וסוד, ולא טוקן Bearer
4. ב-Zap, הוסיפו Custom Request ששולח בכל הרצה את בקשת הטוקן כ-JSON לכתובת `https://api.morning.co/idp/v1/oauth/token` (עם הכותרת `Content-Type: application/json`)
5. קראו ל-REST API של Morning בכתובת `api.greeninvoice.co.il` עם `Authorization: Bearer <accessToken>` מאותו שלב

**קודי סוגי מסמכים ב-Morning** (השתמש בקודים המספריים בקריאות API):

| קוד | סוג מסמך |
|-----|----------|
| 10 | הצעת מחיר |
| 305 | חשבונית מס |
| 320 | חשבונית מס קבלה |
| 330 | חשבונית זיכוי / החזר |
| 400 | קבלה |

**הגדרת `WebHookUrl` של קארדקום (API v11):**
1. ב-Zapier, צור Zap חדש עם "Webhooks by Zapier" כטריגר
2. בחר "Catch Hook" כאירוע טריגר
3. העתק את כתובת ה-webhook שנוצרה
4. העבר את הכתובת הזו בשדה `WebHookUrl` בכל בקשת `CreateLowProfile`. זהו שדה חובה, לצד `TerminalNumber`, `ApiName`, `Amount`, `SuccessRedirectUrl` ו-`FailedRedirectUrl`
5. בסיום התשלום קארדקום שולח **גוף JSON ב-POST** (אובייקט `LowProfileResult`) לאותה כתובת
6. שדות עיקריים: `ResponseCode` (0 = הצלחה), `TranzactionId` (מזהה עסקת אשראי), `LowProfileId`, `ReturnValue` (מה ששלחת בבקשה, בדרך כלל מספר ההזמנה), `TranzactionInfo.Amount` (שקלים עשרוניים; אין שדה `Amount` ברמה העליונה של ה-callback, ו-`TranzactionInfo` הוא null מחוץ ל-`ChargeOnly` ו-`ChargeAndCreateToken`), ופרטי בעל הכרטיס מקוננים תחת `UIValues`: `UIValues.CardOwnerName`, `UIValues.CardOwnerEmail`, `UIValues.CardOwnerPhone`, `UIValues.NumOfPayments`
7. בצע תשלום ניסיון כדי לשלוח נתוני דוגמה ל-Zapier

אינטגרציות ישנות של קארדקום השתמשו ב-`IndicatorUrl` שהוגדר בהגדרות המסוף ושלח GET עם פרמטרים. המנגנון הזה לא מופיע ב-API v11. אם Zap קיים בנוי על `IndicatorUrl` ועל `DealResponse`, הוא על המסלול הישן וצריך לעבור ל-`WebHookUrl` ול-`ResponseCode`.

**הגדרת טרנזילה (API V2 מודרני):**
טרנזילה עברה ל-API V2 מבוסס iframe עם hosted fields לתאימות PCI.

**הגדרת Notify URL בטרנזילה:**
1. ב-Zapier, צרו Catch Hook והעתיקו את הכתובת
2. העבירו אותה כ-`notify_url_address` כשבונים את דף התשלום, או הדביקו אותה ב-my.tranzila תחת הגדרות > מסוף > דף תשלום > אבטחה > Notify URL, וקבעו את Notify Format ל-`QSTR`
3. טרנזילה שולחת את העסקה ב-POST מקודד כטופס לאותה כתובת, במקביל להפניית בעל הכרטיס
4. סננו על `Response` = `000` (או `0`), ואז מפו את `sum`, `ConfirmationCode` ושדות הקשר ששלחתם
5. הריצו עסקת בדיקה אמיתית אחת ומפו לפי מה ש-Zapier קלט בפועל



## 2026 Tax Authority reporting dates, by report type

From the Tax Authority's annual table (`https://www.gov.il/he/pages/pa151025-2`, published 15.10.2025). Each
report type is its own column; do not reuse one set for another. Statutory undeferred dates are the 15th
(periodic VAT and income-tax advances), the 16th (income-tax withholding) and the 23rd (detailed VAT report),
with online filing extending to the 19th at 18:30.

| Report | 2026 dates |
|--------|-----------|
| Periodic VAT + mikdamot | 16.2, 16.3, 27.4, 18.5, 15.6, 15.7, 17.8, 24.9, 19.10, 16.11, 15.12, 18.1.2027 |
| Income-tax withholding (nikuyim) | as periodic except for the May, June and November periods, due 16.6, 16.7 and 16.12 |
| Detailed VAT report (doch meforat) | 23.2, 26.3, 27.4, 26.5, 23.6, 27.7, 24.8, 24.9, 26.10, 23.11, 23.12, 26.1.2027 |

Separate in-year announcements (security situations, emergencies) defer individual periods further, so check
for a superseding announcement before treating any date as final. This happened in 2026: a notice of 5.3.2026
(ילקוט הפרסומים 14327) moved the periodic reports for the period ending February (January-February for bimonthly filers)
to 26.3.2026, overriding the 16.3 in the table above. Re-import the table each January.


## Step 4 deadline detail (relocated from SKILL.md)

**Do not hardcode the 15th.** The statutory date is the 15th of the month following the period (the 16th for income-tax withholding, the 23rd for the detailed VAT report), and online filing extends it to the 19th at 18:30. But the Tax Authority publishes an **annual deferral table** that moves most of those dates, for weekends, rest days of different faiths, and business-day counts. For 2026 the periodic VAT and mikdamot dates are 16.2, 16.3, **27.4**, 18.5, 15.6, 15.7, 17.8, **24.9**, **19.10**, 16.11, 15.12 and 18.1.2027. Nine of the twelve are not the 15th, and the deferrals are as large as twelve days.

**Each report type gets its own column, so do not reuse one set of dates for another.** Withholding (nikuyim) diverges from the VAT dates for the May, June and November periods (due 16.6, 16.7 and 16.12), and the detailed VAT report is a separate set entirely, so a Zap reminding on the periodic dates is wrong for it in most months. Both full 2026 columns are in the table above.

**The annual table is not the last word either.** The Tax Authority issues separate announcements during the year (security situations, emergencies) that defer individual periods further. Check for a superseding announcement before treating any date as final.

Build the reminder Zap so the date is data, not code: keep the current year's deadlines in a Zapier Table (period, deadline date) and have the Schedule Zap look the row up, or set the trigger conservatively early. Re-import the table each January when the Tax Authority publishes the new one. A Zap that fires "five days before the 15th" was, in 2026, twelve days early in April and nine days early in September.

**Mikdamot (advance tax) reminders** ride the SAME deferred dates as periodic VAT in the annual table, so drive them from the same Zapier Table row rather than a hardcoded day. Whether a given business pays bimonthly or monthly is set by its Tax Authority classification, so confirm it per client instead of assuming.

**Annual report trigger:** Schedule in January, compile total revenue, expenses, VAT paid and tax withheld at source (nikui mas ba-makor) from Morning, send to the accountant.

**Key Israeli tax dates to encode in Zaps:**

| Date | Event | Zap Action |
|------|-------|------------|
| That period's row in the annual table | VAT report and mikdamot deadline | Look the date up, remind several days before |
| January | Previous year annual summary | Compile and send to accountant |
| Announced annually | Annual tax filing deadline | Filing reminder. Do NOT hardcode a date, see below |

**The annual filing deadline is announced each year and is not a fixed date.** The Ordinance dates (30 April for a non-online individual, 31 May for an online one) are routinely deferred, often by a month or more: for tax year 2025 the operative dates were **31.5.2026** for individuals not required to file online, **30.6.2026** for individuals filing online, and **30.7.2026** for companies, NPOs and controlling shareholders. The representatives' extension arrangement (הסדר האורכות למייצגים) runs later still and is announced separately. Read the current year's announcement before encoding any date, and prefer a Zapier Table row over a literal in a Filter step.

Note this section does not cover Bituach Leumi advances, which run on their own schedule and are a separate obligation: see the Bituach Leumi section of this file.


## Responder / Responder Live (רב מסר)

| Property | Value |
|----------|-------|
| Connection method | Zapier native integration |
| Zapier slugs | `responder` (Responder (רב מסר)) and `responder-live` (Responder Live (רב מסר)) |
| What it is | Israeli marketing-automation and mailing/SMS platform |
| Why it matters | Native, so contact and campaign steps are a click rather than a Custom Request. Verified present in the directory on 2026-09-02. |

Verbatim strings from the app directory (2026-10-29). Responder: triggers `New Subscriber Added`, `Subscriber Did Not Open Emails`, `Subscriber Reached Seniority`, `New List Created`; actions `Subscribe a New Subscriber`, `Change Subscriber Status`, `Unsubscribe a Subscriber`, `Delete Subscriber`, `Create a List`. Responder Live: trigger `New Subscriber`, action `Create Subscriber`, search `Find a Subscriber`. Re-check before mapping, as with every native app here.

## Cardcom webhook authenticity: there is nothing to verify against

A Zapier Catch Hook URL is a public, unauthenticated endpoint. Anyone who learns it can POST
`{"ResponseCode":0, ...}` and cause a Zap to mint a real Morning tax document. Filtering on
`ResponseCode = 0` does not help: a forger supplies that for free.

We grepped the v11 spec (2026-09-02) for a signature, HMAC or checksum mechanism on the callback and
found none, so there appears to be no signing scheme to validate against. Treat that as "none found in
the spec" rather than a guarantee, and confirm with Cardcom support before relying on it.

Practical mitigations, in order of strength:

1. **Re-fetch before you issue.** On receiving the callback, POST `TerminalNumber`, `ApiName` and the
   `LowProfileId` to `https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult` and issue the
   document only from the values it returns. A forged POST cannot fake that. Template 1 wires this in.
2. **Echo a secret through `ReturnValue`.** Put an unguessable token in `ReturnValue` on the
   `CreateLowProfile` request and Filter on it in the Zap. It stops casual replay, not someone who has
   seen a real payload.
3. **Rotate the Catch Hook URL** if it has ever been pasted into a shared doc or a support ticket.

## WhatsApp Business: the prerequisites Zapier does not put in front of you

Connecting the WhatsApp Business Zapier app is NOT like the Notifications app, where you confirm your
own number with an OTP and start sending. Before a single customer message goes out you need a Meta
Business account, business verification, a WhatsApp Business Platform (Cloud API) app, and a phone
number registered to that platform. That number **cannot simultaneously be in use on the consumer
WhatsApp app**, which is the step that stops most freelancers: the number they wanted to use is
already their personal WhatsApp.

Budget for this as a multi-day onboarding, not a Zap-building afternoon, and note it is also **not
free**. Meta's pricing page says it "charges by category–market, and only for messages from businesses
to users", per delivered message. From 1 October 2026 Meta resumed charging for utility templates sent
inside an open customer-service window (free since 1 July 2025), and only the first 1,000 service
messages per business number each month are free. A payment confirmation is a utility template, so it
is charged whether or not the window is open. Price it before promising the client automatic
confirmations.

## Bituach Leumi is a separate deadline from anything in Step 4

Step 4 of the skill covers VAT periods, mikdamot, income-tax withholding, the detailed VAT report and
the annual filing. An osek murshe ALSO owes monthly Bituach Leumi advances on their own schedule, and
it is one of the deadlines clients miss most often. A reminder Zap built only from Step 4 covers the
user's VAT and silently misses their National Insurance. Confirm the current due date and rate bands
at btl.gov.il before encoding anything, and see the `israeli-freelancer-ops` skill for the
self-employed obligation set as a whole.
