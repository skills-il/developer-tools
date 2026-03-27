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

### Elementor

| Property | Value |
|----------|-------|
| Zapier search name | "Elementor" |
| Auth type | API Key |
| Supported triggers | New Form Submission |
| Notes | Israeli-founded WordPress page builder. Form submissions can trigger Zaps for lead capture and invoicing. |

## Webhook-Based Connections (No Native Integration)

These apps do not have native Zapier integrations. Connect them via "Webhooks by Zapier."

### Morning (formerly Green Invoice / Hashbonit Yeruka)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | JWT token in Authorization header (`Bearer <token>`) |
| API base URL | `https://api.greeninvoice.co.il` |
| Dashboard | `https://app.greeninvoice.co.il` |
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
| Webhook configuration | Cardcom terminal dashboard > IndicatorUrl setting |
| Callback method | **GET request with query parameters** (not JSON POST) |
| Amount unit | **Decimal shekels** (e.g., 150.50 = 150.50 ILS). Do NOT divide by 100. |
| Key fields | `InternalDealNumber` (transaction ID), `Amount` (decimal ILS), `CardOwnerName`, `CardOwnerEmail`, `CardOwnerPhone`, `NumOfPayments`, `CardNum` (last 4), `DealResponse` (0=success) |
| Installments (tashlumim) | `NumOfPayments` indicates installment count. `FirstPayment` is the first installment amount (in decimal shekels). |
| Test mode | Cardcom sandbox sends test webhooks. Verify `DealResponse` = `0` for successful transactions. |

**Cardcom response codes (DealResponse):**

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Transaction declined |
| `2` | Contact credit card company |
| `3` | Terminal not found |
| `4` | Transaction error |

### Tranzila

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Tranzila merchant panel > Notification URL |
| Payment integration | API V2 with iframe-based hosted fields (PCI compliant) |
| Callback method | POST with form-encoded data |
| Amount unit | **Decimal ILS** (e.g., 250.00 = 250.00 ILS) |
| Key fields | `index` (transaction ID), `sum` (amount in decimal ILS), `ccno` (last 4 digits), `npay` (installments), `contact`, `email`, `phone` |
| Notes | Widely used Israeli payment processor. Modern API V2 uses hosted fields. The legacy redirect-based ok_page/fail_page approach still works but is deprecated. Supports Bit payments. |

### Grow by Meshulam

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Grow merchant dashboard > Developer settings |
| Callback method | JSON POST |
| Amount unit | **Decimal ILS** |
| Payment methods | Credit cards, Bit, Apple Pay, Google Pay |
| Key fields | `transaction_id`, `amount` (decimal ILS), `payment_method`, `customer_name`, `customer_email`, `customer_phone` |
| Notes | Israeli payment gateway by Meshulam. Growing adoption among small businesses. One of the few gateways with native Bit support. |

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

### Sumit

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Custom Request |
| Auth | API key |
| API format | REST API |
| Amount unit | Decimal ILS |
| Notes | Israeli invoicing and receipts platform. REST API for document creation and management. |

### Rivhit (Accounting Software)

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier (Webhooks by Zapier > Custom Request) |
| Auth | API key in Authorization header |
| API base URL | `https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/` |
| Key endpoints | `Document_New`, `Customer_New`, `Customer_List`, `Document_List` |
| Notes | Popular Israeli accounting software. No native Zapier integration. Use outbound HTTP requests from Zapier to create documents. |

### Priority ERP

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier (Webhooks by Zapier > Custom Request) |
| Auth | Basic Authentication or Token-based |
| API format | OData REST |
| Notes | Enterprise ERP widely used in Israeli mid-market. REST API available on Priority Cloud. On-premise installations may require VPN or IP whitelisting for Zapier access. |

### Hashavshevet (Accounting)

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier |
| Auth | API key |
| Notes | Legacy Israeli accounting software. API availability varies by version. Check with vendor for API access. |

## SMS and Messaging Providers

### InforUMobile (Israeli SMS Gateway)

| Property | Value |
|----------|-------|
| Connection method | HTTP POST via Zapier |
| API endpoint | `https://api.inforu.co.il/SendMessageXml.ashx` |
| Auth | Username/password in XML body |
| Format | XML payload |
| Notes | Popular Israeli SMS provider. Send SMS by constructing XML body in a Zapier webhook action. Hebrew text supported natively. |

### 019 SMS

| Property | Value |
|----------|-------|
| Connection method | HTTP POST via Zapier |
| Auth | API key |
| Notes | Bezeq International SMS API. REST-based. Supports Hebrew. |

### WhatsApp Business via Third-Party Providers

Zapier's native WhatsApp integration can only send messages to yourself (the account holder). It supports 7 prefilled English templates and cannot send custom Hebrew messages to customers. For customer-facing WhatsApp, use one of these third-party providers:

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
| Zapier search name | "Respond.io" |
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
| Notes | The Shaam system (e-invoicing) has APIs for authorized software, but these are not accessible via Zapier. Use Morning or other authorized invoicing platforms as intermediaries. Since January 2026, invoices over 10,000 NIS require Tax Authority allocation numbers (mispar hiktza'a). |

## Field Mapping Quick Reference

Common fields across Israeli payment processors, mapped to Morning document fields. All amounts are in decimal shekels (no conversion needed for any processor).

| Concept | Cardcom Field | Tranzila Field | Grow Field | Morning API Field |
|---------|---------------|----------------|------------|-------------------|
| Transaction ID | `InternalDealNumber` | `index` | `transaction_id` | (auto-generated) |
| Amount (decimal ILS) | `Amount` | `sum` | `amount` | `items[].unitPrice` |
| Customer name | `CardOwnerName` | `contact` | `customer_name` | `client.name` |
| Customer email | `CardOwnerEmail` | `email` | `customer_email` | `client.emails[0]` |
| Customer phone | `CardOwnerPhone` | `phone` | `customer_phone` | `client.phone` |
| Installments | `NumOfPayments` | `npay` | N/A | `payment.installments` |
| Last 4 digits | `CardNum` | `ccno` | N/A | (not mapped) |
| Payment method | (always credit card) | (always credit card) | `payment_method` | N/A |
| Currency | (always ILS) | (always ILS) | (always ILS) | `currency: "ILS"` |
