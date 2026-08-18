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
| Supported actions | Create Sales Orders (existing or new customers), Create Sales Opportunity, Create New Lead, Create Potential Customer, Create Job Candidate, Find Customer by Email, Update Sales Opportunity/Order Status, Add Shipping Charges to Orders |
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
| Auth | JWT token in Authorization header (`Bearer <token>`) |
| API base URL | host `api.greeninvoice.co.il` (exact base path is documented at https://developers.morning.co/ , do not guess it) |
| Dashboard | `https://app.greeninvoice.co.il/login` |
| API documentation | `https://developers.morning.co/` (the old `greeninvoice.co.il/api-docs/` URL now redirects here) |
| API key location | Dashboard > Settings > API Integration |
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
| `items[].description` | Line item description | String (Hebrew OK) |
| `items[].unitPrice` | Price per unit in decimal ILS | Number (e.g., 150.50) |
| `items[].quantity` | Quantity | Number |
| `vatType` | VAT inclusion | `0` = before VAT, `1` = VAT included |

### Cardcom (Kardkom)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Pass the Catch Hook URL as the `WebHookUrl` field on each `CreateLowProfile` API request. `WebHookUrl` is a required field on that request. |
| Callback method | **JSON POST** carrying a `LowProfileResult` object (not a GET with query parameters) |
| API docs | `https://secure.cardcom.solutions/swagger/index.html`, spec at `https://secure.cardcom.solutions/swagger/v11/swagger.json` |
| Amount unit | **Decimal shekels** (e.g., 150.50 = 150.50 ILS). Do NOT divide by 100. The v11 spec describes `Amount` as "Amount of tranzaction (12.36)" with format `decimal`. |
| Key fields | `ResponseCode` (0 = success), `Description` (text for the response code), `TranzactionId` (credit-card transaction ID), `LowProfileId`, `ReturnValue` (echo of what you sent, typically your order ID), `Amount` (decimal ILS), and cardholder details nested under `UIValues` |
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
| Notes | Requires Twilio WhatsApp Business API account with Meta Business verification. Customer-facing messages must use Meta-approved templates. Hebrew templates are supported but must be submitted for approval (24-48 hours). |

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
| Amount (decimal ILS) | `Amount` | `sum` | `amount` | `items[].unitPrice` |
| Customer name | `UIValues.CardOwnerName` | `contact` | `customer_name` | `client.name` |
| Customer email | `UIValues.CardOwnerEmail` | `email` | `customer_email` | `client.emails[0]` |
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
6. Key fields: `ResponseCode` (0 = success), `TranzactionId` (credit-card transaction ID), `LowProfileId`, `ReturnValue` (whatever you sent on the request, typically your order ID), `Amount` (decimal shekels, e.g., 150.50), and cardholder details nested under `UIValues`: `UIValues.CardOwnerName`, `UIValues.CardOwnerEmail`, `UIValues.CardOwnerPhone`, `UIValues.NumOfPayments`
7. Make a test payment to send sample data to Zapier

Older Cardcom integrations used an `IndicatorUrl` configured in terminal settings that fired a GET with query parameters. That mechanism does not appear in the v11 API. If an existing Zap is built on `IndicatorUrl` and `DealResponse`, it is on the legacy path and should be migrated to `WebHookUrl` and `ResponseCode`.

**Tranzila setup (modern API V2):**
Tranzila has moved to iframe-based API V2 with hosted fields for PCI compliance.

**Unverified, confirm before building:** this skill previously documented a merchant-panel "notification URL" that POSTs `index`, `sum`, `ccno`, `npay`, `contact`, `email` and `phone`. Tranzila's current documentation at `https://docs.tranzila.com/` has no webhook or notification-URL page. Those field names are the legacy redirect/handshake response parameters, i.e. what Tranzila appends when returning the cardholder to your `ok_page`. Before building a Tranzila trigger, confirm in the merchant panel whether a true server-to-server callback exists. If it does not, the workable pattern is a thin intermediary that receives the redirect and forwards its parameters to a Zapier Catch Hook.

