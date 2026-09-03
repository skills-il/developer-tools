# SUMIT payments: PCI-safe tokenization, charging, recurring, hosted pages

Consult this when implementing any charging path. The guiding rule: raw card details must never reach your server. SUMIT tokenizes in the browser, and your server only ever handles a single-use token.

## The tokenization flow

```
Browser  --card fields-->  payments.js (SUMIT, client side)
payments.js  --tokenize (public key)-->  SUMIT Vault
SUMIT Vault  --og-token (single use)-->  Browser
Browser  --og-token-->  Your server
Your server  --charge (secret key + SingleUseToken)-->  SUMIT /billing/payments/charge/
```

## Step 1: load payments.js and bind the form

```html
<script src="https://app.sumit.co.il/scripts/payments.js"></script>
<script>
  OfficeGuy.Payments.BindFormSubmit({
    CompanyID: YOUR_COMPANY_ID,
    APIPublicKey: 'YOUR_PUBLIC_KEY'
  });
</script>
```

Build an HTML form with `data-og` attributes. On submit, payments.js tokenizes and injects a hidden `og-token` field:

```html
<form id="payment-form" action="/checkout" method="post">
  <input data-og="cardnumber" maxlength="20" />
  <input data-og="expirationmonth" placeholder="mm" />
  <input data-og="expirationyear" placeholder="yyyy" />
  <input data-og="cvv" maxlength="4" />
  <input data-og="citizenid" placeholder="ID" />
  <button type="submit">Pay</button>
</form>
```

## Step 2: charge on the server

`POST /billing/payments/charge/` with the secret key and the `SingleUseToken` you received:

```json
{
  "Credentials": { "CompanyID": 0, "APIKey": "..." },
  "Customer": { "Name": "...", "EmailAddress": "..." },
  "SingleUseToken": "og-token-from-frontend",
  "Items": [ { "Quantity": 1, "UnitPrice": 99.9, "Description": "..." } ],
  "VATIncluded": true,
  "SendDocumentByEmail": true
}
```

Useful charge fields:
- `AuthoriseOnly`: validate without actually charging (issues a draft). Good for tests.
- `AutoCapture` and `AuthorizeAmount`: two-step authorize then capture.
- `Payments_Count`, `Payments_Credit`: installments.
- `PreventDocumentCreation`: charge without issuing a document.
- `MerchantNumber`: a specific terminal.

Response `Data` includes `Payment.ID`, `Payment.AuthNumber`, `Payment.PaymentMethod.CreditCard_Token` (for future charges), `DocumentID`, `DocumentNumber`, `DocumentDownloadURL`.

## Direct JSON tokenization (custom UI)

If you build your own UI, tokenize directly with the public key via `POST /creditguy/vault/tokenizesingleusejson/`:

```json
{
  "Credentials": { "CompanyID": 0, "APIPublicKey": "..." },
  "CardNumber": "____", "ExpirationMonth": 12, "ExpirationYear": 2030,
  "CVV": "___", "CitizenID": "_________"
}
```

Returns `Data.SingleUseToken`.

## Saved cards (charge again later)

- `POST /billing/paymentmethods/setforcustomer/` stores a method on a customer (pass `SingleUseToken` or a `PaymentMethod` with a token).
- `POST /billing/paymentmethods/getforcustomer/` returns the masked method plus token.
- `POST /billing/paymentmethods/remove/` removes it.

## Recurring billing

`POST /billing/recurring/charge/` charges now and creates a standing order. Recurring-specific fields:
- `Items[].Item.Duration_Months` (1 = monthly) or `Duration_Days`.
- `Items[].Recurrence` (e.g. 12 for a year of monthly charges).
- `Items[].Date_Start` (first charge date).
- `DocumentType` (the document issued per charge).
- `OnlyDocument` (issue documents without charging).

## Hosted payment page (lowest PCI burden)

`POST /billing/payments/beginredirect/` returns a hosted page URL so SUMIT hosts the card form entirely. Key fields:
- `RedirectURL`, `CancelRedirectURL`: where to send the user after success or cancel.
- `ExternalIdentifier`: your reference for matching and dedup.
- `MaximumPayments`, `ExpirationHours`, `Theme`, `Language`.
- `IPNURL`: a server-to-server notification of the payment result. This is the webhook for hosted-page charges.
- `PreventSavingPaymentMethod`.

## Testing

- Use `AuthoriseOnly: true` to exercise the charge path without real money (issues a draft).
- The developers help center provides test cards for integration testing.
- The free tier allows up to 10 documents per month at no cost.

## Security notes

- The secret `APIKey` is server-side only. The browser may only see `APIPublicKey`.
- Keep an `ExternalIdentifier` per charge and check `payments/list` before re-charging to avoid duplicates on retry.
- Add backoff and retry on `TechnicalError`. Never retry on `BusinessError`; fix the input instead.
