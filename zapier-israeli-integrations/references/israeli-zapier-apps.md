# Israeli Apps on Zapier: Connection Reference

This reference covers Israeli-origin and Israel-popular apps available on Zapier, including native integrations, webhook-based connections, and API-only workarounds.

## Native Zapier Integrations (Built-In)

These apps have official Zapier integrations with full trigger/action support.

### Monday.com

| Property | Value |
|----------|-------|
| Zapier search name | "Monday.com" |
| Auth type | OAuth 2.0 |
| Supported triggers | New Item, Item Column Changed, New Update, Status Changed |
| Supported actions | Create Item, Update Item, Create Update, Create Subitem |
| Notes | Global app with very strong Israeli adoption. Works seamlessly with Zapier. Good for project management workflows combined with Israeli billing apps. |

### Wix

| Property | Value |
|----------|-------|
| Zapier search name | "Wix" |
| Auth type | OAuth 2.0 |
| Supported triggers | New Form Submission, New Order, New Contact |
| Supported actions | Create Contact, Update Contact |
| Notes | Israeli-founded. Commonly used for e-commerce sites that need invoicing integration. |

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

**Note on Elementor:** earlier versions of this reference listed Elementor as a native Zapier app. It has no app in the Zapier directory. Elementor Pro Forms integrates with Zapier through a webhook configured on the WordPress side, so treat it as a webhook source, not a Zapier app.

## Webhook-Based Connections (No Native Integration)

These apps do not have native Zapier integrations. Connect them via "Webhooks by Zapier."

### Morning (formerly Green Invoice / Hashbonit Yeruka)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | **OAuth 2.0 client_credentials.** POST to `https://api.morning.co/idp/v1/oauth/token`, take `accessToken` from the response and send it as `Authorization: Bearer <accessToken>`. The token is a signed JWT valid for **1 hour**, so a Zap must fetch one per run rather than carrying a pasted token. |
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
| `client.taxId` | Business number (osek murshe) or ID | String, 9 digits |
| `currency` | Currency code | `ILS` for shekels |
| `lang` | Document language, **required** | e.g. `he` |
| `income[].description` | Line row description, required per row | String (Hebrew OK) |
| `income[].price` | Price per unit in decimal ILS, required per row | Number (e.g., 150.50) |
| `income[].quantity` | Quantity, required per row | Number |
| `income[].currency` | Row currency, required per row | `ILS` |
| `income[].vatType` | Row VAT type, required per row | `0` = before VAT, `1` = VAT included |
| `vatType` | Document VAT inclusion, **required** | `0` = before VAT, `1` = VAT included |

**Verified against the live spec on 2026-09-02** (`https://developers.morning.co/docs/openapi.bundled.json`). Two traps
here, both of which produce a hard 400:

- The line array is **`income[]`, not `items[]`**, and the price field is **`price`, not `unitPrice`**. `CreateDocumentRequest`
  has no `items` property at all.
- `CreateDocumentRequest.required` is `["type","lang","currency","vatType","income"]`, so **`lang` is mandatory** and is the
  field most often omitted. Each `income[]` row separately requires `description`, `quantity`, `price`, `currency` and `vatType`.

**The create response does not carry the allocation number.** `CreateDocumentResponse` returns `id`, `number`, `dueDate`,
`type`, `signed`, `lang`, `client`, `url`, `vatRate`, `taxAuthorityConfirmationInitiated` and `taxAuthorityConfirmationLastError`.
`allocationNumber` is a field on the `Document` schema, so read it from `GET /documents/{id}` or from the `document/created`
webhook, never from the 201.

### Cardcom (Kardkom)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Pass the Catch Hook URL as the `WebHookUrl` field on each `CreateLowProfile` API request. `WebHookUrl` is a required field on that request. |
| Callback method | **JSON POST** carrying a `LowProfileResult` object (not a GET with query parameters) |
| API docs | `https://secure.cardcom.solutions/swagger/index.html`, spec at `https://secure.cardcom.solutions/swagger/v11/swagger.json` |
| Amount location | **`TranzactionInfo.Amount`**, NOT a top-level `Amount`. Verified against the v11 spec on 2026-09-02: `LowProfileResult` has no `Amount` property. `TranzactionInfo` is documented as "Will no be null at operations: ChargeOnly, ChargeAndCreateToken", so guard for null. The `Amount` people copy from the docs is on the `CreateLowProfile` REQUEST schema, not the callback. |
| Amount unit | **Decimal shekels** (150.50 = 150.50 ILS), `format: decimal`. Do NOT divide by 100. |
| Key fields | `ResponseCode` (0 = success), `Description` (text for the response code), `TranzactionId` (credit-card transaction ID), `LowProfileId`, `ReturnValue` (echo of what you sent, typically your order ID), `TranzactionInfo.Amount` (decimal ILS), and cardholder details nested under `UIValues`. Full top-level set: `ResponseCode`, `Description`, `TerminalNumber`, `LowProfileId`, `TranzactionId`, `ReturnValue`, `Operation`, `UIValues`, `DocumentInfo`, `TokenInfo`, `SuspendedInfo`, `TranzactionInfo`, `ExternalPaymentVector`, `Country`, `UTM`, `IssuerAuthCodeDescription`, `AccountId`. |
| `UIValues` sub-fields | `CardOwnerName`, `CardOwnerEmail`, `CardOwnerPhone`, `CardOwnerIdentityNumber`, `NumOfPayments`, `CardYear`, `CardMonth`, `IsAbroadCard`, `CustomFields` |
| Installments (tashlumim) | `UIValues.NumOfPayments` indicates installment count. |
| Test mode | Cardcom sandbox sends test webhooks. Verify `ResponseCode` = `0` for successful transactions. |

**Legacy note:** older Cardcom integrations configured an `IndicatorUrl` in terminal settings that fired a GET with query parameters including `InternalDealNumber` and `DealResponse`. Neither `IndicatorUrl` nor `DealResponse` appears in the v11 API. In v11, `InternalDealNumber` survives only as a lookup key on `TransactionInfoRequest`, not as a webhook field. Migrate legacy Zaps to `WebHookUrl` and `ResponseCode`.

### Tranzila

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | **UNVERIFIED, confirm in the merchant panel before building** |
| Payment integration | API V2 with iframe-based hosted fields (PCI compliant) |
| API docs | `https://docs.tranzila.com/` |
| Amount unit | **Decimal ILS** (e.g., 250.00 = 250.00 ILS) |
| Legacy redirect params | `index` (transaction ID), `sum` (amount in decimal ILS), `ccno` (last 4 digits), `npay` (installments), `contact`, `email`, `phone` |
| Notes | Widely used Israeli payment processor. Supports Bit payments (Tranzila's docs carry a dedicated Bit API page). **Caveat:** Tranzila's current documentation has no webhook or notification-URL page. Its Payments and Billing section covers Authentication, Hosted Fields, Iframe Integration, Iframe Integration new DirectNG, Apple Pay via Iframe, PayPal Integration and Transaction Response Codes; the APIS section covers Transactions API, 3DS, Bit, Handshake API V2, MASAV API, Payment request and STO API. The field names above are the legacy redirect/handshake response parameters returned to your `ok_page`, not a documented server-to-server callback. If no true webhook exists, forward the redirect parameters to a Zapier Catch Hook from a thin intermediary. |

### Grow by Meshulam

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Grow merchant dashboard > Developer settings |
| Callback method | JSON POST |
| Amount unit | **Decimal ILS** |
| Payment methods | Credit cards, Bit, Apple Pay, Google Pay |
| Key fields | **UNVERIFIED:** `transaction_id`, `amount` (decimal ILS), `payment_method`, `customer_name`, `customer_email`, `customer_phone`. Meshulam publishes no public spec at a resolvable developer host, so confirm the exact payload against a real test webhook before mapping fields. |
| Notes | Israeli payment gateway by Meshulam (not by any bank). Growing adoption among small businesses. One of the few gateways with native Bit support. **Do not search Zapier for "Grow":** `zapier.com/apps/grow` is an unrelated US product ("Grow helps publishers build their mailing list"). Grow by Meshulam has no Zapier app. |

### iCount

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | API key |
| API format | REST API |
| Amount unit | Decimal ILS |
| Notes | Israeli accounting SaaS. REST API for creating invoices, receipts, expenses, and managing contacts. No native Zapier integration. |

### EZcount

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | API key |
| API format | REST API |
| Amount unit | Decimal ILS |
| Notes | Popular Israeli invoicing platform. API supports document creation, customer management, and payment tracking. |

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
| Connection method | HTTP request via Zapier |
| Auth | API key |
| Notes | Legacy Israeli accounting software. API availability varies by version. Check with vendor for API access. |

## SMS and Messaging Providers

### InforUMobile (Israeli SMS Gateway)

**Use the native Zapier app.** See the InforUMobile entry under Native Zapier Integrations above: the `Send SMS` and `Send Whatsapp Template Message` actions replace the hand-built XML call for most workflows.

| Property | Value |
|----------|-------|
| Preferred connection | Native Zapier app ("InforUMobile") |
| Fallback connection | HTTP POST via Zapier |
| Fallback API endpoint | `https://api.inforu.co.il/SendMessageXml.ashx` |
| Fallback auth | Username/password in XML body |
| Fallback format | XML payload |
| Notes | Popular Israeli SMS provider. Hebrew text supported natively. Only drop to the raw XML API for cases the native app's actions do not cover, since the fallback puts credentials in the request body. |

### 019 SMS

| Property | Value |
|----------|-------|
| Connection method | HTTP POST via Zapier |
| Auth | API key |
| Notes | Bezeq International SMS API. REST-based. Supports Hebrew. |

### WhatsApp on Zapier: two different apps

| Zapier app | Reaches | Capability |
|------------|---------|------------|
| WhatsApp Notifications | Only the phone number that authenticated the connection | Single `Send Message` action, restricted to prefilled templates that cannot be customized. Described on Zapier as "Receive notifications on WhatsApp." Internal alerting only. |
| **WhatsApp Business** | **Customers** | Triggers `New Message Received`, `Message Status Updated`. Actions `Send Template Message`, `Send Freeform Message` (inside the 24-hour customer-service window), `Send Media Message`, `Get Attachment`. Described on Zapier as "a customer messaging app that delivers fast, reliable communication through organized chats, automated responses, and business profiles." |

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
| Notes | No automation path. Use scheduled reminders for payment deadlines instead. |

### Israel Tax Authority (Rashut HaMisim)

| Property | Value |
|----------|-------|
| Connection method | No direct API for Zapier. |
| Notes | The Shaam system (e-invoicing) has APIs for authorized software, but these are not accessible via Zapier. Use Morning or other authorized invoicing platforms as intermediaries. Since June 2026, invoices over 5,000 NIS **before VAT** require Tax Authority allocation numbers (mispar haktza'a). |

## Field Mapping Quick Reference

Common fields across Israeli payment processors, mapped to Morning document fields. All amounts are in decimal shekels (no conversion needed for any processor).

Tranzila and Grow columns are marked unverified for the reasons given in their sections above.

| Concept | Cardcom v11 Field | Tranzila Field (unverified) | Grow Field (unverified) | Morning API Field |
|---------|-------------------|-----------------------------|-------------------------|-------------------|
| Transaction ID | `TranzactionId` | `index` | `transaction_id` | (auto-generated) |
| Success flag | `ResponseCode` (0 = success) | (see Transaction Response Codes) | N/A | N/A |
| Your order ID | `ReturnValue` | N/A | N/A | N/A |
| Amount (decimal ILS) | `TranzactionInfo.Amount` | `sum` | `amount` | `income[].price` |
| Customer name | `UIValues.CardOwnerName` | `contact` | `customer_name` | `client.name` |
| Customer email | `UIValues.CardOwnerEmail` | `email` | `customer_email` | `client.emails[0]` (array) |
| Customer phone | `UIValues.CardOwnerPhone` | `phone` | `customer_phone` | `client.phone` |
| Installments | `UIValues.NumOfPayments` | `npay` | N/A | `payment.installments` |
| Last 4 digits | (not on the webhook payload) | `ccno` | N/A | (not mapped) |
| Payment method | (always credit card) | (always credit card) | `payment_method` | N/A |
| Currency | (always ILS) | (always ILS) | (always ILS) | `currency: "ILS"` |


## Per-vendor connection detail (relocated from SKILL.md)

**Morning (formerly Green Invoice) API setup:**
1. Log in to Morning dashboard (app.greeninvoice.co.il)
2. Navigate to Settings > API Integration
3. Generate a new API key (JWT-based authentication)
4. In Zapier, use "Webhooks by Zapier" with Custom Request to call Morning's REST API at `api.greeninvoice.co.il`
5. Set the Authorization header with your JWT token

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

**Unverified, confirm before building:** this skill previously documented a merchant-panel "notification URL" that POSTs `index`, `sum`, `ccno`, `npay`, `contact`, `email` and `phone`. Tranzila's current documentation at `https://docs.tranzila.com/` has no webhook or notification-URL page. Those field names are the legacy redirect/handshake response parameters, i.e. what Tranzila appends when returning the cardholder to your `ok_page`. Before building a Tranzila trigger, confirm in the merchant panel whether a true server-to-server callback exists. If it does not, the workable pattern is a thin intermediary that receives the redirect and forwards its parameters to a Zapier Catch Hook.



## Connection method by app (relocated from SKILL.md Step 2)

| App | Connection Method | Auth Type | Notes |
|-----|-------------------|-----------|-------|
| Morning (formerly Green Invoice) | Webhooks by Zapier | Token exchange, see note | No native Zapier app for Morning. Connect via webhooks: use Morning's webhook notifications as triggers and their REST API via Webhooks by Zapier for actions. Auth is OAuth 2.0: the current spec (`https://developers.morning.co/docs/openapi.bundled.json`, info.version 2.0.0) documents `POST https://api.morning.co/idp/v1/oauth/token` with `grant_type=client_credentials`, returning a short-lived JWT sent as `Authorization: Bearer`. Errors follow the RFC 6749 OAuth error format. The production base for all other calls is still `https://api.greeninvoice.co.il/api/v1` (sandbox `https://sandbox.d.greeninvoice.co.il/api/v1`); the token path itself overrides to `https://api.morning.co` (sandbox `https://api.sandbox.morning.dev`). The token is a signed JWT valid for 1 hour, so refresh it rather than caching it across a long Zap run. The legacy `POST /api/v1/account/token` still answers but is absent from the spec: undocumented legacy, do not build new Zaps on it. Amounts are decimal shekels, never agorot. |
| Cardcom | Webhooks by Zapier | `WebHookUrl` (JSON POST callback) | Cardcom POSTs a JSON body to the `WebHookUrl` you supply on the `CreateLowProfile` request. `WebHookUrl` is a required field on that request. |
| Tranzila | Webhooks by Zapier | See caveat below | Tranzila V2 uses iframe-based hosted fields for payment. See the Tranzila section in Step 5 before building: the current documentation does not describe a merchant-panel webhook. |
| Monday.com | Zapier native integration | OAuth | Full support. Monday.com is a global app with strong Israeli adoption. |
| SUMIT | **Zapier native integration** | Managed by Zapier | Israeli invoicing and business-management platform. Native app with a `Card Updated` trigger and `Create Document`, `Create Card`, `Update Card`, `Get Card`, `Send SMS` actions. Use `Create Document` instead of hand-rolling invoice HTTP calls. |
| Priority ERP | **Zapier native integration** | Managed by Zapier | Israeli ERP. Native app with `Catch Changed Customer Order Status Webhook` and `Catch Changed Purchase Order Status Webhook` triggers, plus `Create a New Sales Order`, `Create a Sales Opportunity`, `Create New Lead in Priority` and `Find Customer by Email` actions. Check the exact strings in the app directory before mapping them; several differ from the shorthand people use. |
| InforUMobile | **Zapier native integration** | Managed by Zapier | Israeli SMS and marketing gateway. Native app with `New Lead From Landing Page` trigger and `Send SMS`, `Send Whatsapp Template Message`, `Add Contact to Group` actions. Prefer this over the raw XML API. |
| iCount | Webhooks by Zapier | API key | Israeli accounting SaaS. No native Zapier app. Use iCount REST API via Webhooks by Zapier for creating invoices, receipts, and managing contacts. |
| EZcount | Webhooks by Zapier | API key | Popular Israeli invoicing platform. No native Zapier app. REST API for document creation and customer management. |
| Grow by Meshulam | Webhooks by Zapier | Webhook URL | Israeli payment gateway supporting credit cards, Bit, Apple Pay, Google Pay. Sends JSON POST webhooks on payment events. **Do not search Zapier for "Grow"**: the app at `zapier.com/apps/grow` is an unrelated US mailing-list product ("Grow helps publishers build their mailing list"), not Meshulam. |
| Rivhit (accounting) | Webhooks by Zapier | API key in header | No native integration. Use webhook + custom API calls. |
| 019 SMS | Webhooks by Zapier | API key | No native Zapier app. Send SMS via HTTP POST action with the provider's API. |



## שיטת חיבור לפי אפליקציה (הועבר מ-SKILL_HE.md שלב 2)

אפליקציות ישראליות מתחברות ל-Zapier בשלוש דרכים. **תמיד בדוק קודם בספריית האפליקציות של Zapier** (`zapier.com/apps/<app-slug>/integrations`): כמה ספקים ישראליים כבר מציעים אפליקציה מובנית, ואפליקציה מובנית תמיד פשוטה ואמינה יותר מ-Custom Request שבונים ביד. רד ל-webhooks רק כשאין אפליקציה מובנית.

| אפליקציה | שיטת חיבור | סוג אימות | הערות |
|----------|-----------|----------|-------|
| Morning (חשבונית ירוקה) | Webhooks by Zapier | OAuth 2.0, ראו הערה | אין אפליקציה מובנית של Morning ב-Zapier. חיבור דרך webhooks: שימוש ב-webhook notifications של Morning כטריגרים וב-REST API שלהם דרך Webhooks by Zapier לפעולות. האימות הוא OAuth 2.0: המפרט הנוכחי (`https://developers.morning.co/docs/openapi.bundled.json`, גרסה 2.0.0) מתעד את `POST https://api.morning.co/idp/v1/oauth/token` עם `grant_type=client_credentials`, שמחזיר JWT קצר-מועד שנשלח כ-`Authorization: Bearer`. בסיס הייצור לשאר הקריאות עדיין `https://api.greeninvoice.co.il/api/v1`. נקודת הקצה הישנה `POST /api/v1/account/token` עדיין מגיבה אך נעדרת מהמפרט: מורשת לא מתועדת, אל תבנו עליה Zap חדש. הסכומים שקלים עשרוניים, לא אגורות. |
| קארדקום (Cardcom) | Webhooks by Zapier | `WebHookUrl` (callback בשיטת JSON POST) | קארדקום שולח גוף JSON לכתובת `WebHookUrl` שמעבירים בבקשת `CreateLowProfile`. זהו שדה חובה באותה בקשה. |
| טרנזילה (Tranzila) | Webhooks by Zapier | ראו הסתייגות בהמשך | טרנזילה V2 משתמשת ב-iframe עם hosted fields. קראו את סעיף טרנזילה בשלב 5 לפני הבנייה: התיעוד הנוכחי לא מתאר webhook בפאנל הסוחר. |
| Monday.com | אינטגרציה מובנית ב-Zapier | OAuth | תמיכה מלאה. |
| SUMIT | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | פלטפורמת חשבוניות וניהול עסקי ישראלית. אפליקציה מובנית עם טריגר `Card Updated` ופעולות `Create Document`, `Create Card`, `Update Card`, `Get Card`, `Send SMS`. עדיף על בניית קריאות HTTP ידניות. |
| Priority ERP | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | מערכת ERP ישראלית. אפליקציה מובנית עם טריגרים `Catch Changed Customer Order Status Webhook` ו-`Catch Changed Purchase Order Status Webhook`, ופעולות `Create a New Sales Order`, `Create a Sales Opportunity`, `Create New Lead in Priority`, `Find Customer by Email`. בדקו את המחרוזות המדויקות בספריית האפליקציות לפני מיפוי, כמה מהן שונות מהקיצור שנהוג להשתמש בו. |
| InforUMobile | **אינטגרציה מובנית ב-Zapier** | מנוהל על ידי Zapier | שער SMS ושיווק ישראלי. אפליקציה מובנית עם טריגר `New Lead From Landing Page` ופעולות `Send SMS`, `Send Whatsapp Template Message`, `Add Contact to Group`. עדיף על ה-API הגולמי ב-XML. |
| iCount | Webhooks by Zapier | מפתח API | מערכת הנהלת חשבונות ישראלית ללא אפליקציה מובנית. שימוש ב-REST API ליצירת חשבוניות, קבלות וניהול לקוחות. |
| EZcount | Webhooks by Zapier | מפתח API | פלטפורמת חשבוניות ישראלית פופולרית עם REST API. |
| Grow by Meshulam | Webhooks by Zapier | כתובת Webhook | שער תשלומים ישראלי שתומך בכרטיסי אשראי, ביט, Apple Pay, Google Pay. שולח webhooks בפורמט JSON. **אל תחפשו "Grow" ב-Zapier**: האפליקציה בכתובת `zapier.com/apps/grow` היא מוצר אמריקאי לא קשור לניהול רשימות תפוצה, לא משולם. |
| ריווחית (Rivhit) | Webhooks by Zapier | מפתח API ב-header | אין אינטגרציה מובנית. webhook + קריאות API. |
| 019 SMS | Webhooks by Zapier | מפתח API | אין אפליקציה מובנית. שליחת SMS דרך פעולת HTTP POST. |

**הגדרת API של Morning (חשבונית ירוקה):**
1. היכנס לדשבורד של Morning באתר app.greeninvoice.co.il
2. נווט להגדרות > אינטגרציית API
3. צור מפתח API חדש (אימות מבוסס JWT)
4. ב-Zapier, השתמש ב-"Webhooks by Zapier" עם Custom Request כדי לקרוא ל-REST API של Morning בכתובת `api.greeninvoice.co.il`
5. הגדר את כותרת Authorization עם ה-JWT token

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

**לא אומת, יש לאשר לפני בנייה:** בגרסאות קודמות תועדה כאן כתובת התראה בפאנל הסוחר ששולחת `index`, `sum`, `ccno`, `npay`, `contact`, `email` ו-`phone`. בתיעוד הנוכחי של טרנזילה בכתובת `https://docs.tranzila.com/` אין עמוד webhook או notification URL. שמות השדות האלה הם פרמטרי ההחזרה הישנים, כלומר מה שטרנזילה מוסיפה כשהיא מחזירה את הלקוח ל-`ok_page`. לפני בניית טריגר, בדקו בפאנל הסוחר אם קיים callback אמיתי שרת-לשרת. אם אין, הדפוס שעובד הוא מתווך דק שמקבל את ההחזרה ומעביר את הפרמטרים ל-Catch Hook.



## 2026 Tax Authority reporting dates, by report type

From the Tax Authority's annual table (`https://www.gov.il/he/pages/pa151025-2`, published 15.10.2025). Each
report type is its own column; do not reuse one set for another. Statutory undeferred dates are the 15th
(periodic VAT and income-tax advances), the 16th (income-tax withholding) and the 23rd (detailed VAT report),
with online filing extending to the 19th at 18:30.

| Report | 2026 dates |
|--------|-----------|
| Periodic VAT + mikdamot | 16.2, 16.3, 27.4, 18.5, 15.6, 15.7, 17.8, 24.9, 19.10, 16.11, 15.12, 18.1.2027 |
| Income-tax withholding (nikuyim) | as periodic except June, July and December: 16.6, 16.7, 16.12 |
| Detailed VAT report (doch meforat) | 23.2, 26.3, 27.4, 26.5, 23.6, 27.7, 24.8, 24.9, 26.10, 23.11, 23.12, 26.1.2027 |

Separate in-year announcements (security situations, emergencies) defer individual periods further, so check
for a superseding announcement before treating any date as final. Re-import the table each January.


## Responder / Responder Live (רב מסר)

| Property | Value |
|----------|-------|
| Connection method | Zapier native integration |
| Zapier slugs | `responder` (Responder (רב מסר)) and `responder-live` (Responder Live (רב מסר)) |
| What it is | Israeli marketing-automation and mailing/SMS platform |
| Why it matters | Native, so contact and campaign steps are a click rather than a Custom Request. Verified present in the directory on 2026-09-02. |

Check the exact trigger and action strings in the app directory before mapping them, as with every native app here.

## Cardcom webhook authenticity: there is nothing to verify against

A Zapier Catch Hook URL is a public, unauthenticated endpoint. Anyone who learns it can POST
`{"ResponseCode":0, ...}` and cause a Zap to mint a real Morning tax document. Filtering on
`ResponseCode = 0` does not help: a forger supplies that for free.

We grepped the v11 spec (2026-09-02) for a signature, HMAC or checksum mechanism on the callback and
found none, so there appears to be no signing scheme to validate against. Treat that as "none found in
the spec" rather than a guarantee, and confirm with Cardcom support before relying on it.

Practical mitigations, in order of strength:

1. **Re-fetch before you issue.** On receiving the callback, call Cardcom back by `LowProfileId` and
   issue the document only from the values the API returns. A forged POST cannot fake that.
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
free**: Meta moved to per-message pricing on 1 July 2025, and a proactive payment confirmation is a
utility template sent outside the 24-hour window, which is charged. Messages sent inside the window
are free. For a per-transaction automation that is a real running cost, so price it before promising
the client automatic confirmations.

## Bituach Leumi is a separate deadline from anything in Step 4

Step 4 of the skill covers VAT periods, mikdamot, income-tax withholding, the detailed VAT report and
the annual filing. An osek murshe ALSO owes monthly Bituach Leumi advances on their own schedule, and
it is one of the deadlines clients miss most often. A reminder Zap built only from Step 4 covers the
user's VAT and silently misses their National Insurance. Confirm the current due date and rate bands
at btl.gov.il before encoding anything, and see the `israeli-freelancer-ops` skill for the
self-employed obligation set as a whole.
