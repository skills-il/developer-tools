---
name: sumit-api-integration
description: >-
  Integrate the SUMIT (formerly OfficeGuy) REST API into applications for
  Israeli invoicing, accounting, and business automation. Use when user asks to
  connect to SUMIT, "samit", "officeguy", create an invoice via SUMIT, "hashbonit",
  charge a credit card, "slikat ashrai", pull income or expense reports, "shaivat
  dohot", manage customers, or set up SUMIT webhooks. Covers authentication
  (CompanyID + APIKey), document creation (23 document types), tokenized card
  charging, recurring billing, expense ingestion, data retrieval, and Triggers/IPN
  webhooks. Do NOT use for Green Invoice/Morning (use green-invoice), Tranzila (use
  tranzila-payment-gateway), or SHAAM e-invoice allocation (use israeli-e-invoice).
license: MIT
allowed-tools: 'Bash(python:*) Bash(curl:*)'
compatibility: >-
  No SDK required, uses plain HTTP/JSON over stdlib. Requires network access to
  api.sumit.co.il. Works with Claude Code, Claude.ai, Cursor.
---

# SUMIT API Integration

## Overview

SUMIT (formerly OfficeGuy) is an Israeli cloud business-management platform: invoicing, credit-card charging, recurring billing, CRM, and expense capture. This skill covers the public REST API at `https://api.sumit.co.il`, which exposes 84 operations across 27 modules.

Two facts shape every call:
1. **Every endpoint is `POST`** with a JSON body, even reads (list/get). There is no GET/PUT/DELETE per resource.
2. **Authentication is a `Credentials` object inside the JSON body** (`CompanyID` + `APIKey`), not an HTTP header.

## Instructions

### Step 1: Obtain credentials

From the SUMIT dashboard: Settings, then API keys. You need three values, stored as environment variables (never hardcode them):

| Value | Env var | Where it goes |
|-------|---------|---------------|
| Company ID | `SUMIT_COMPANY_ID` | every request body |
| API key (secret) | `SUMIT_API_KEY` | server-side requests only |
| API public key | `SUMIT_API_PUBLIC_KEY` | browser tokenization only |

The secret `APIKey` must never reach the browser. The public key is the only credential allowed client-side.

### Step 2: Make an authenticated call

Base URL: `https://api.sumit.co.il`. Path pattern: `/<controller>/<action>/`. Send `Content-Type: application/json`. Optional `Content-Language: he-IL` sets the response language.

Every response uses one envelope:

| Field | Meaning |
|-------|---------|
| `Status` | `Success` (0), `BusinessError` (1), `TechnicalError` (2) |
| `UserErrorMessage` | user-facing error text |
| `TechnicalErrorDetails` | technical detail for support |
| `Data` | the operation-specific payload |

Critical: HTTP 200 can still carry `BusinessError`. Always check `Status`, not just the HTTP code. Use the bundled `scripts/sumit_client.py` as the single call wrapper. See `references/api-endpoints.md` for the full operation map.

### Step 3: Create a document (invoice / receipt)

`POST /accounting/documents/create/`. Pick a `Type` from the 23 document types (see `references/document-types-and-enums.md`). Common: `InvoiceAndReceipt` (1), `Invoice` (0), `Receipt` (2), `PriceQuotation` (12).

```json
{
  "Credentials": { "CompanyID": 0, "APIKey": "..." },
  "Details": {
    "Type": "InvoiceAndReceipt",
    "Customer": { "Name": "...", "EmailAddress": "...", "SearchMode": "EmailAddress" },
    "Description": "...", "Language": "Hebrew", "Currency": "ILS"
  },
  "Items":   [ { "Quantity": 1, "UnitPrice": 1000, "Description": "..." } ],
  "Payments":[ { "Amount": 1180, "Details_BankTransfer": {} } ],
  "VATIncluded": false, "VATRate": 18
}
```

Response `Data`: `DocumentID`, `DocumentNumber`, `CustomerID`, `DocumentDownloadURL`. `SearchMode` enables upsert (create-or-find), avoiding duplicate customers.

### Step 4: Charge a credit card (PCI-safe tokenization)

Card details must never touch your server. The flow:
1. Browser loads `https://app.sumit.co.il/scripts/payments.js`.
2. `OfficeGuy.Payments.BindFormSubmit({ CompanyID, APIPublicKey })` tokenizes the card and injects `og-token`.
3. Send `og-token` to your server, then call `POST /billing/payments/charge/` with `SingleUseToken`.

`charge` charges and issues an invoice in one call. Key fields: `SingleUseToken`, `Items[]`, `VATIncluded`, `SendDocumentByEmail`, `AuthoriseOnly` (validate without charging, good for testing). Full flow in `references/payments-and-tokenization.md`.

### Step 5: Recurring billing

`POST /billing/recurring/charge/` charges and creates a standing order. Set `Items[].Item.Duration_Months` (1 = monthly), `Items[].Recurrence` (e.g. 12), `Items[].Date_Start`. Manage with `recurring/listforcustomer`, `recurring/update`, `recurring/cancel`. Store a card token via `billing/paymentmethods/setforcustomer` for repeat charges.

### Step 6: Capture expenses

`POST /accounting/documents/addexpense/` pushes a supplier expense with a Base64 file (`ExpenseFile`), `Supplier`, `Lines[]`, and `Payments[]`. To pull expenses that SUMIT captured automatically (via its WhatsApp/email AI capture), call `documents/list` with expense `DocumentTypes`: `ExpenseInvoice` (16), `ExpenseInvoiceReceipt` (15), `ExpenseReceipt` (17).

### Step 7: Retrieve data (reports)

All reads are `POST`, all paginated (`Paging.PageSize` 10 to 1000):

| Goal | Endpoint |
|------|----------|
| List documents | `/accounting/documents/list/` |
| Document detail | `/accounting/documents/getdetails/` |
| Document PDF | `/accounting/documents/getpdf/` |
| List payments | `/billing/payments/list/` |
| Customer debt | `/accounting/documents/getdebt/` , `/getdebtreport/` |
| List customers | `/crm/data/listentities/` (Folder=Customers, LoadProperties=true) |

### Step 8: Receive data in real time (webhooks)

Two push channels:
1. **Triggers**: `POST /triggers/triggers/subscribe/` with `URL`, `Folder`, `TriggerType` (`CreateOrUpdate` / `Create` / `Update` / `Archive` / `Delete`). Fires on entity changes.
2. **IPN**: pass `IPNURL` to `/billing/payments/beginredirect/` to get a server-to-server notification of a payment result.

Verify the request origin, return HTTP 200 fast, then process asynchronously and idempotently.

## Examples

### Example 1: Issue a tax invoice-receipt
User says: "create a hashbonit mas-kabala for 1000 plus VAT to a client by email".
Actions:
1. Build the `documents/create` body with `Type: InvoiceAndReceipt`, `Items[].UnitPrice: 1000`, `VATIncluded: false`, `VATRate: 18`.
2. Call via `scripts/sumit_client.py`.
3. Read `Data.DocumentNumber` and `Data.DocumentDownloadURL`.
Result: invoice issued, PDF link returned.

### Example 2: Charge a saved card monthly
User says: "set up a 99 NIS monthly slikat ashrai".
Actions:
1. Tokenize once with payments.js to get `og-token`.
2. Call `recurring/charge` with `SingleUseToken`, `Duration_Months: 1`, `Recurrence: 12`.
Result: standing order created, first invoice issued.

### Example 3: Pull this month's expenses
User says: "shaivat dohot of this month's hotzaot".
Actions:
1. Call `documents/list` with `DocumentTypes: ["ExpenseInvoice","ExpenseInvoiceReceipt","ExpenseReceipt"]` and a `DateFrom`/`DateTo` range.
2. Page through with `Paging`.
Result: list of expense documents for the period.

## Bundled Resources

### Scripts
- `scripts/sumit_client.py` -- Zero-dependency (stdlib) SUMIT API client and CLI: wraps the `Credentials` envelope, posts JSON, and raises on non-Success `Status`. Run: `python scripts/sumit_client.py --help`

### References
- `references/api-endpoints.md` -- The full map of all 84 operations across 27 modules with paths and one-line purpose. Consult when you need an endpoint not covered in the steps above.
- `references/document-types-and-enums.md` -- All 23 document types, payment types, currencies, search modes, and the response-status enum. Consult when choosing a `Type` or decoding an enum value.
- `references/payments-and-tokenization.md` -- The full PCI-safe charging flow, payments.js setup, saved cards, recurring billing, and hosted payment pages. Consult when implementing any charging path.

## Reference Links

Official sources for verifying and updating the information in this skill:

| Source | URL | What to Check |
|--------|-----|---------------|
| SUMIT API (Swagger) | https://app.sumit.co.il/help/developers/swagger/index.html | Live endpoint list, request/response schemas |
| SUMIT OpenAPI spec | https://app.sumit.co.il/swagger/v1/swagger.json | Raw machine-readable spec |
| SUMIT developers help center | https://help.sumit.co.il/he/collections/3333669 | Integration guides, testing, API keys |
| Payments JavaScript API | https://help.sumit.co.il/he/articles/5893615-payments-javascript-api | Tokenization, BindFormSubmit, test cards |

## Gotchas

- Every operation is `POST`, including all reads. There is no REST verb per resource; a "delete entity" is `POST /crm/data/deleteentity/`.
- `Credentials` lives in the JSON body, not in an `Authorization` header.
- HTTP 200 does not mean success. Check the `Status` field on every response.
- The secret `APIKey` must stay server-side. Only `APIPublicKey` may appear in the browser.
- `ResponseLanguage` in request bodies is deprecated; use the `Content-Language` header instead.

## Troubleshooting

### Error: response has Status "BusinessError"
Cause: a logical problem (missing customer name, declined card, validation failure).
Solution: show `UserErrorMessage` to the user. Do not retry blindly; fix the input first.

### Error: response has Status "TechnicalError"
Cause: a transient or system fault on the SUMIT side.
Solution: log `TechnicalErrorDetails`, retry with backoff, and report the detail to SUMIT support if it persists.

### Error: card charge fails with no token
Cause: the server received raw card fields instead of a `SingleUseToken`.
Solution: tokenize in the browser with payments.js first; the server should only ever see `og-token`.
