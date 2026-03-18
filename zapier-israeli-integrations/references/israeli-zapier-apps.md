# Israeli Apps on Zapier: Connection Reference

This reference covers Israeli-origin and Israel-popular apps available on Zapier, including native integrations, webhook-based connections, and API-only workarounds.

## Native Zapier Integrations (Built-In)

These apps have official Zapier integrations with full trigger/action support.

### Green Invoice (Hashbonit Yeruka)

| Property | Value |
|----------|-------|
| Zapier search name | "Green Invoice" |
| Auth type | API Key |
| API key location | Dashboard > Settings > API Integration |
| Supported triggers | New Document Created, New Customer Created, Document Status Changed |
| Supported actions | Create Document, Create Customer, Find Document, Find Customer |
| Document types | Invoice (hashbonit mas), Receipt (kabala), Invoice-Receipt (hashbonit mas kabala), Credit Note (hashbonit zikui), Price Quote (hatzaat mechir), Purchase Order (hazmnat rechisha), Delivery Note (te'udat mishloach) |
| Notes | Most popular Israeli invoicing platform on Zapier. API key does not expire unless regenerated. Free Green Invoice tier has API access limits. |

**Common field mappings for Green Invoice documents:**

| Green Invoice Field | Description | Format |
|---------------------|-------------|--------|
| `type` | Document type code | Integer (see table above) |
| `client.name` | Client name | String (Hebrew OK) |
| `client.emails` | Client email(s) | Array of strings |
| `client.taxId` | Business number (osek murshe) or ID | String, 9 digits |
| `currency` | Currency code | `ILS` for shekels |
| `items[].description` | Line item description | String (Hebrew OK) |
| `items[].unitPrice` | Price per unit in ILS | Number |
| `items[].quantity` | Quantity | Number |
| `vatType` | VAT inclusion | `0` = before VAT, `1` = VAT included |

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

These apps do not have native Zapier integrations. Connect them via "Webhooks by Zapier" (requires Zapier paid plan for catch hooks, or use the free "Webhooks by Zapier" trigger with limitations).

### Cardcom (Kardkom)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Cardcom terminal dashboard > Notifications (hatharot) |
| Payload format | POST with form-encoded data |
| Amount unit | **Agorot** (divide by 100 for ILS) |
| Key fields | `Transaction`, `Amount`, `CardNum`, `NumOfPayments`, `CustomerName`, `Email`, `Phone`, `CustomFields` |
| Installments (tashlumim) | `NumOfPayments` indicates installment count. `FirstPayment` is the first installment amount (in agorot). |
| Test mode | Cardcom sandbox sends test webhooks. Verify `ResponseCode` = `0` for successful transactions. |

**Cardcom response codes:**

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
| Payload format | POST with form-encoded data |
| Amount unit | **ILS** (not agorot, unlike Cardcom) |
| Key fields | `index` (transaction ID), `sum` (amount in ILS), `ccno` (last 4 digits), `npay` (installments), `contact`, `email`, `phone` |
| Notes | Older but still widely used Israeli payment processor. Some merchants use both Cardcom and Tranzila for different terminals. |

### Grow (by Leumi)

| Property | Value |
|----------|-------|
| Connection method | Webhooks by Zapier > Catch Hook |
| Webhook configuration | Grow merchant dashboard > Developer settings |
| Payload format | JSON POST |
| Amount unit | ILS |
| Notes | Payment solution by Bank Leumi. Growing adoption among small businesses. |

### Rivhit (Accounting Software)

| Property | Value |
|----------|-------|
| Connection method | HTTP request via Zapier (Webhooks by Zapier > Custom Request) |
| Auth | API key in Authorization header |
| API base URL | `https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/` |
| Key endpoints | `Document_New`, `Customer_New`, `Customer_List`, `Document_List` |
| Notes | Popular Israeli accounting software. No native Zapier integration. Use outbound HTTP requests from Zapier to create documents. Can also set up Rivhit to call a Zapier webhook on document creation if enabled. |

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

### WhatsApp via Twilio

| Property | Value |
|----------|-------|
| Zapier search name | "Twilio" |
| Auth type | Account SID + Auth Token |
| Action | Send WhatsApp Message |
| Phone format | Must use +972 prefix (drop leading 0) |
| Notes | Not Israeli-specific, but widely used for WhatsApp automation in Israel. Requires Twilio WhatsApp Business approval for production use. |

## Gov.il and Government Services

### Gov.il Forms

| Property | Value |
|----------|-------|
| Connection method | Varies by form. Some support email notifications (use Gmail trigger), others support webhook callbacks. |
| Notes | No unified API. Each ministry/service has its own form system. The most reliable approach is to use email notifications from gov.il forms as Zapier triggers (Gmail > New Email matching specific subject). |

### Bituach Leumi (National Insurance)

| Property | Value |
|----------|-------|
| Connection method | No API. Manual or email-based. |
| Notes | No automation path. Use scheduled reminders for payment deadlines instead. |

### Israel Tax Authority (Rashut HaMisim)

| Property | Value |
|----------|-------|
| Connection method | No direct API for Zapier. |
| Notes | The Shaam system (e-invoicing) has APIs for authorized software, but these are not accessible via Zapier. Use Green Invoice or other authorized invoicing platforms as intermediaries. |

## Field Mapping Quick Reference

Common fields across Israeli payment processors, mapped to Green Invoice document fields:

| Concept | Cardcom Field | Tranzila Field | Green Invoice Field |
|---------|---------------|----------------|---------------------|
| Transaction ID | `Transaction` | `index` | (auto-generated) |
| Amount | `Amount` / 100 | `sum` | `items[].unitPrice` |
| Customer name | `CustomerName` | `contact` | `client.name` |
| Customer email | `Email` | `email` | `client.emails[0]` |
| Customer phone | `Phone` | `phone` | `client.phone` |
| Installments | `NumOfPayments` | `npay` | `payment.installments` |
| Last 4 digits | `CardNum` | `ccno` | (not mapped) |
| Currency | (always ILS) | (always ILS) | `currency: "ILS"` |
