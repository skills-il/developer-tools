# Zap Templates for Israeli Businesses

Ready-to-use Zap configurations for common Israeli business workflows. Each template includes the trigger, action chain, field mappings, and notes on customization.

Israeli payment processors (Cardcom, Tranzila, Grow, Morning) send amounts in decimal units of the transaction currency, never agorot, so check the currency before treating a value as ILS. Gateway amounts INCLUDE VAT, and the Invoice Reform threshold is measured before VAT.

**One phone normaliser for every template** (Israeli numbers only; leave a number with another country code alone):

```javascript
let d = (inputData.phone || '').replace(/\D/g, '').replace(/^00/, '');
if (d.startsWith('972')) d = d.slice(3);
d = d.replace(/^0/, '');
const phone = d ? '+972' + d : '';
```

**One Hebrew cleaner** (strips RLM/LRM, embeddings, isolates, ALM and zero-width characters):

```javascript
const clean = s => (s || '').replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u061C\u200B-\u200D\u2060\uFEFF]/g, '').trim();
```

**One Morning search loop** for Templates 4, 7 and 9. A search page holds 25 documents by default and the spec documents no maximum, so page through `pages` inside a Code by Zapier step (Zapier's Code docs use `await fetch(url, {method: 'POST', body: JSON.stringify(data), ...})`). Map `token` from the Morning token step; never paste the client secret into code. Zapier's own guidance prefers API by Zapier over `fetch` for authenticated calls; this loop holds no credential (the one-hour token is mapped in), but if your account has API by Zapier, use it instead. A whole-year search can run into Code by Zapier's run-time limit, so split a long range by quarter.

```javascript
async function searchAll(token, filter) {
  const docs = [];
  let page = 1, pages = 1, total = 0;
  do {
    const r = await fetch('https://api.greeninvoice.co.il/api/v1/documents/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify({ ...filter, page, pageSize: 25 })
    });
    if (!r.ok) throw new Error('Morning search failed: HTTP ' + r.status);
    const body = await r.json();
    docs.push(...(body.items || []));
    pages = body.pages || 1;
    total = body.total || 0;
    page++;
  } while (page <= pages);
  if (docs.length < total) throw new Error(`only ${docs.length} of ${total} documents came back`);
  return docs;
}
```

A document in a foreign currency converts to ILS with its `currencyRate`; when that optional field is missing, derive it from `amountLocal / amount`:

```javascript
const rateOf = d => d.currencyRate || (d.amountLocal && d.amount ? d.amountLocal / d.amount : 1);
```

## Template 1: Cardcom Payment to Morning Receipt

**Use case:** Auto-generate a tax invoice/receipt in Morning (formerly Green Invoice) when a customer pays through Cardcom.

**Before building it:** skip the Zap if the payment page is a Morning payment form (Morning issues the document itself through its clearing plugin) or if your `CreateLowProfile` request sends a `Document` object (Cardcom creates its own document and the callback's `DocumentInfo` is filled). Either way a Zap would issue a second tax invoice for the same sale. An osek patur issues 400, not 320.

**Zap steps:**

| Step | App | Event | Configuration | Tasks |
|------|-----|-------|---------------|-------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Pass the URL as `WebHookUrl` on each `CreateLowProfile` request; put the order ID and a secret in `ReturnValue` | 0 |
| 2. Filter | Filter by Zapier | Only Continue If | `ResponseCode` = 0; `Operation` is `ChargeOnly` or `ChargeAndCreateToken`; `TranzactionInfo Amount` exists and > 0; `TranzactionInfo IsRefund` is not true; `TranzactionInfo CoinId` = 1; `ReturnValue` contains your secret | 0 |
| 3. Re-fetch | Webhooks by Zapier | Custom Request | POST `https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult`, JSON `{"TerminalNumber":..., "ApiName":"...", "LowProfileId":"<from step 1>"}`. Map everything below from THIS response, which a forged callback cannot fake | 1 |
| 3b. Filter | Filter by Zapier | Only Continue If | Repeat on the step 3 response: `ResponseCode` = 0, `TranzactionInfo Amount` > 0, `IsRefund` not true, `CoinId` = 1. If the callback and the real result disagree, this stops a zero-value document | 0 |
| 4. Dedupe | Zapier Tables, then Filter | Find Record, then Only Continue If | Look up `TranzactionId`, then continue only if the search found nothing | 0 |
| 5. Date | Formatter by Zapier | Date/Time > Format | Input: step 3 `TranzactionInfo CreateDate` (the charge time, not the run time, so a held or replayed run keeps its VAT period), To Format `YYYY-MM-DD`, timezone `Asia/Jerusalem`. Check on a test payload whether `CreateDate` already is Israel time; if so do not shift it again | 0 |
| 6. Token | Webhooks by Zapier | Custom Request | POST `https://api.morning.co/idp/v1/oauth/token`, Data `{"grant_type":"client_credentials","client_id":"...","client_secret":"..."}`, header `Content-Type: application/json` | 1 |
| 7. Body | Code by Zapier | Run JavaScript | Build the JSON with `JSON.stringify` (code below) | 1 |
| 8. Create | Webhooks by Zapier | Custom Request | POST `https://api.greeninvoice.co.il/api/v1/documents`, Data = step 7 `body`, headers `Content-Type: application/json` and `Authorization: Bearer <step 6 accessToken>` | 1 |
| 9. Log | Zapier Tables | Create Record | `TranzactionId`, Morning `id` and `number`, so step 4 sees it next time | 0 |
| 10. Allocation | Delay by Zapier, then Custom Request | Delay For, then GET | B2B over the threshold only: wait, then GET `/documents/{id}` and read `allocationNumber`; alert yourself if it is missing or the create response's `taxAuthorityConfirmationLastError` is not 0 | 1 |

About 5 tasks per payment, so Professional's 750 cover roughly 150 payments a month (past that, pay-per-task billing or held runs). There is no separate email step: Morning emails the document link to every address in `client.emails`.

**Body code (step 7).** Map the inputs from step 3: `name` = `UIValues CardOwnerName`, `email` = `UIValues CardOwnerEmail`, `amount` = `TranzactionInfo Amount`, `last4` = `TranzactionInfo Last4CardDigitsString`, `payments` = `TranzactionInfo NumberOfPayments`, `first` = `TranzactionInfo FirstPaymentAmount`, `date` = step 5, and `taxId` = the buyer's ח.פ. if your checkout collected one.

```javascript
const amount = Number(inputData.amount);
const n = Number(inputData.payments) || 1;
const clean = s => (s || '').replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u061C\u200B-\u200D\u2060\uFEFF]/g, '').trim();
const client = { name: clean(inputData.name), emails: inputData.email ? [inputData.email] : [] };
if (inputData.taxId) client.taxId = inputData.taxId.replace(/\D/g, '');
const pay = { date: inputData.date, type: 3, price: amount, currency: 'ILS',
              cardNum: inputData.last4, numPayments: n, dealType: n > 1 ? 2 : 1 };
if (n > 1 && inputData.first) pay.firstPayment = Number(inputData.first);
const body = {
  type: 320, lang: 'he', currency: 'ILS', vatType: 0, client,
  income: [{ description: 'תשלום עבור שירות', quantity: 1, price: amount, currency: 'ILS', vatType: 1 }],
  payment: [pay]
};
output = [{ body: JSON.stringify(body) }];
```

`JSON.stringify` escapes the ASCII quote in names like `כהן בע"מ`; typing mapped fields into a JSON Data box does not, and the request 400s for exactly those customers.

**Morning API field reference (step 7):**

| Morning API Field | Value | Notes |
|-------------------|-------|-------|
| `type` | `320` | חשבונית מס/קבלה, the tax invoice the customer deducts input VAT against and the document an allocation number attaches to |
| `lang` | `he` | **Required**, and the most often omitted |
| `currency` | `ILS` | **Required**. The Filter admits only `CoinId` 1 (ILS) |
| `vatType` | `0` | **Required** at document level, a DIFFERENT enum: `0` default for the business type, `1` **exempt**, `2` mixed |
| `client.name` / `client.emails` | cardholder name / `[email]` | Morning sends the document link to `client.emails` |
| `client.taxId` | buyer's ח.פ. / osek number | Needed for a B2B invoice above the threshold to get an allocation number |
| `income[]` | one row | Each row requires `description`, `quantity`, `price`, `currency`, `vatType`; row `vatType: 1` = price includes VAT |
| `payment[]` | one row | Each row requires `date`, `type`, `price`, `currency`. `type: 3` is credit card; `cardNum` takes the last 4 digits; `dealType` 1 standard, 2 payments; `numPayments` 1-36; `firstPayment` the first installment. `price` equals the income total |

**Customization options:**
- Branch with Paths on "`taxId` present AND pre-VAT amount over the threshold variable" before step 10; a consumer sale needs no allocation number.
- Send the customer the document on WhatsApp too: a WhatsApp Business `Send Template Message` after step 8, with a template variable for the create response's `url.he`, and the phone from `UIValues CardOwnerPhone` (filled only when the payment page sets `UIDefinition.IsCardOwnerPhoneRequired`) through the normaliser above.
- A refund (`IsRefund` true) needs a 330 credit note against the original document, not this Zap.
- The body records a credit card (`type: 3`). If the same page also offers Bit or PayPal, run one test payment of each and look at `ExternalPaymentVector` and `TranzactionInfo`; map Morning payment `type` 10 (payment app) or 5 (PayPal) for those, or send them to a separate path. Morning's `dealType` also has 3 (Credit) for a קרדיט deal, which the code above labels 2.
- A sale your accountant treats as zero-rated (an exported service, a foreign client) must not take this path: the body always extracts 18% from the price.

---

## Template 2: Morning to Zapier Tables Bookkeeping Log

**Use case:** Automatically log every new Morning document to a Zapier Table for bookkeeping. (Alternative: use Google Sheets if the accountant needs direct spreadsheet access.)

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Webhooks by Zapier | Catch Hook | Subscribe the Catch Hook URL to Morning's `document/created` webhook |
| 2. Filter | Filter by Zapier | Only Continue If | Document type is 305 (Invoice), 320 (Invoice-Receipt) or 330 (Credit Note), OR type is 400 (Receipt) and `businessType` is 3 (עוסק פטור). An osek murshe's 400 for a 305 already logged is the same sale with no VAT line, so logging it would count that revenue twice; an osek patur issues only 400s, so for it they are the revenue. Store amounts as absolute values with the Document Type column, and subtract 330 rows when you total (the sign on a real 330 payload is not documented) |
| 3. Format | Code by Zapier | Run JavaScript | `subtotal: Math.abs(Number(inputData.subtotal)).toFixed(2), vat: Math.abs(Number(inputData.vat ?? 0)).toFixed(2), total: Math.abs(Number(inputData.total)).toFixed(2)`, with `vat` mapped from `tax[0].total`. The payload has no `amount`, and `tax` carries a VAT line only when VAT applies, hence the 0 default. Do not use Numbers > Format Number: Zapier's docs say it "cannot round or pad numbers" |
| 4. Action | Zapier Tables | Create Record | Map fields to columns |

**Zapier Tables columns and mapping (Step 4):**

| Column | Source | Notes |
|--------|--------|-------|
| Date | Step 1: `date` | Already `YYYY-MM-DD`; keep it. Zapier Tables accepts only `MM/DD/YYYY`, `YYYY-MM-DD` or `YYYY-MM-DDhh:mm:ssZ`, so a DD/MM/YYYY value is misread as month-first. Use DD/MM/YYYY only in human-facing text |
| Document Number | Step 1: `number` | e.g., "1001" |
| Document Type | Step 1: `type` | Map code: 305=Invoice, 320=Invoice-Receipt, 330=Credit Note (subtract), 400=Receipt (osek patur only) |
| Client Name | Step 1: `recipient.name` | The `document/created` payload calls the client `recipient`, not `client` |
| Amount Before VAT | Step 3: `subtotal` | "Document total before VAT" in the webhook schema |
| VAT Amount | Step 3: `vat` | From `tax[0].total`; `tax` is an array of tax lines, and the VAT line carries `rate` (e.g. 0.18) and `total` |
| Currency / Rate | Step 1: `currency`, `foreignCurrencyRate` | Amounts are in the document currency; the rate is present only when that is not ILS, so a USD row is not an ILS figure |
| Total Amount | Step 3: `total` | Includes VAT |
| Payment Status | `GET /documents/{id}`, field `status` | Not in the webhook payload. Codes: 0 open, 1 closed, 2 manually closed, 3 cancelling, 4 cancelled |
| VAT Period | Step 1: derive from date | e.g., "Jan-Feb 2026" |
| Allocation Number | Step 1: `allocationNumber` | Present on the `document/created` payload when one was assigned, and omitted otherwise (Morning omits empty fields rather than sending null). Never read it from the create-document response. Required for invoices > 5,000 NIS before VAT since Jun 2026 |

**Securing the hook:** configure the Morning webhook with a secret, and Morning signs every delivery with an `x-webhook-signature` header (HMAC-SHA256 of the body) that a Code step can check. Morning also deactivates a webhook after 15 failed deliveries, so a Zap that was off for a while may need the webhook re-enabled.

**VAT period derivation:**
Use Formatter > Date/Time to extract the month number, then use a Lookup Table:
- Months 1-2: "Jan-Feb" (ינואר-פברואר)
- Months 3-4: "Mar-Apr" (מרץ-אפריל)
- Months 5-6: "May-Jun" (מאי-יוני)
- Months 7-8: "Jul-Aug" (יולי-אוגוסט)
- Months 9-10: "Sep-Oct" (ספטמבר-אוקטובר)
- Months 11-12: "Nov-Dec" (נובמבר-דצמבר)

---

## Template 3: E-Commerce Order to Invoice + Email Confirmation

**Use case:** When an order comes in from Shopify or WooCommerce, create a Morning document and send an email confirmation in Hebrew.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Shopify | New Order | Or WooCommerce > New Order |
| 2. Format | Code by Zapier | Run JavaScript | Clean Hebrew text and format phone number |
| 3a. Token | Webhooks by Zapier | Custom Request | Morning token, as Template 1 step 6 |
| 3b. Body | Code by Zapier | Run JavaScript | Build the 320 body with `JSON.stringify`, as Template 1 step 7 |
| 3c. Create | Webhooks by Zapier | Custom Request | POST `/documents` with the step 3b string |
| 4. Action | Gmail | Send Email | Hebrew RTL confirmation email |
| 5. Action | Monday.com | Create Item | Track order in board |

**Phone formatting and Hebrew text cleaning (Step 2):**

```javascript
// the shared normaliser and cleaner from the top of this file
let d = (inputData.phone || '').replace(/\D/g, '').replace(/^00/, '');
if (d.startsWith('972')) d = d.slice(3);
d = d.replace(/^0/, '');
const phone = d ? '+972' + d : '';
const name = (inputData.name || '').replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u061C\u200B-\u200D\u2060\uFEFF]/g, '').trim();
output = [{phone, name}];
```

**Note on WhatsApp:** use the **WhatsApp Business** app (not "WhatsApp Notifications", which only messages your own number). A proactive order confirmation falls outside the 24-hour customer-service window, so it needs a Meta-approved Hebrew template. Inside that window, `Send Freeform Message` sends arbitrary Hebrew.

---

## Template 4: Freelancer Monthly Invoice Reminder

**Use case:** Send monthly reminders to a freelancer (atzmai) about unpaid invoices and upcoming tax deadlines.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Every Month | Day: 1st of month |
| 2. Action | Webhooks by Zapier | Custom Request | Morning token step (Template 1 step 6) |
| 3. Action | Code by Zapier | Run JavaScript | Search loop plus open-balance sum (code below) |
| 4. Filter | Filter by Zapier | Only Continue If | Step 3 `count` is greater than 0 |
| 5. Action | Gmail | Send Email | Summary to self or accountant |

**Open-balance code (Step 3).** Paste `searchAll` and `rateOf` from the top of this file above it. The filter has no `fromDate`: a date window drops exactly the oldest, most overdue invoices. The `type` filter keeps out open quotes (10) and orders (100), which are not debts.

```javascript
const docs = await searchAll(inputData.token, { type: [305, 300, 20], status: [0] });
let total = 0;
for (const d of docs) {
  // amountOpened exists only on payment-request documents (type 20), in the document currency;
  // other open documents owe their full total, and amountLocal is already ILS
  const owed = d.amountOpened != null ? Number(d.amountOpened) * rateOf(d)
                                      : Number(d.amountLocal ?? d.amount * rateOf(d));
  total += owed || 0;
}
output = [{ count: docs.length, total: total.toFixed(2) }];
```

A partly paid invoice still shows its full amount here, because Morning reports a remaining balance only on payment requests.

**Email template (Step 5):**

Subject: "סיכום חשבוניות פתוחות - {{current_month}} {{current_year}}"

```html
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <h2>סיכום חשבוניות פתוחות</h2>
  <p>נכון ל-{{date}}, יש לך {{count}} חשבוניות שטרם שולמו:</p>
  <p><strong>סה"כ חוב פתוח: {{total}} ש"ח</strong></p>
  <hr>
  <p><em>תזכורת: מועד דיווח מע"מ הבא - {{next_vat_deadline}}</em></p>
</div>
```

---

## Template 5: Form Submission to CRM + Email Follow-up

**Use case:** Capture leads from a Hebrew form and automatically add to CRM with email follow-up.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Typeform | New Response | Or Google Forms or Wix Forms. Elementor has no Zapier app; its Pro Forms push to Zapier via a WordPress-side webhook, so use Catch Hook for those. |
| 2. Format | Code by Zapier | Run JavaScript | Clean Hebrew text and format phone |
| 3. Action | Monday.com | Create Item | Add lead to "Leads" board |
| 4. Action | Gmail | Send Email | Hebrew RTL welcome email |
| 5. Action | Delay by Zapier | Delay For | Wait 3 days (Schedule by Zapier is trigger-only and cannot be used as an action step) |
| 6. Action | Gmail | Send Email | Follow-up email |

**Hebrew text cleaning (Step 2):**

```javascript
// the shared normaliser and cleaner from the top of this file
let d = (inputData.phone || '').replace(/\D/g, '').replace(/^00/, '');
if (d.startsWith('972')) d = d.slice(3);
d = d.replace(/^0/, '');
const phone = d ? '+972' + d : '';
const name = (inputData.name || '').replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u061C\u200B-\u200D\u2060\uFEFF]/g, '').trim();
output = [{phone, name}];
```

**Monday.com board setup (Step 3):**

| Column | Type | Mapping |
|--------|------|---------|
| Name | Text | Lead's full name from form |
| Status | Status | "New Lead" (ליד חדש) |
| Phone | Phone | Formatted +972 number |
| Email | Email | From form |
| Source | Text | Form name/platform |
| Date | Date | Submission date |

**Note:** For a WhatsApp greeting, use the **WhatsApp Business** app's `Send Template Message` with a Meta-approved Hebrew template. Do not use "WhatsApp Notifications", which only messages your own number.

---

## Template 6: Expense Receipt Categorization

**Use case:** Automatically categorize expense receipts from email and log them for tax deduction purposes.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Gmail | New Email | Match subject or body containing "קבלה", "חשבונית", "receipt" |
| 2. Format | Formatter by Zapier | Text > Extract Pattern | Extract amount using regex |
| 3. Action | Code by Zapier | Run JavaScript | Categorize by sender |
| 4. Action | Zapier Tables | Create Record | Log to expenses table |

**Categorization logic (Step 3).** Match the sender's DOMAIN against a map, not keywords against the whole address: a keyword like `paz` matches a person called Paz, `hot` matches every `hotmail.com` sender, and a word boundary misses `hotmobile.co.il`. The entries below are examples; build the map from the domains your own receipts actually come from, since vendors bill from several.

```javascript
// accept both "invoice@bezeq.co.il" and "Bezeq <invoice@bezeq.co.il>"
// map Gmail's bare sender address (From Email), not the display name; if only a
// "Name <addr>" string is available, take the LAST <...> so a display name such as
// "<invoice@bezeq.co.il>" <scam@evil.example> cannot pose as the vendor
const raw = (inputData.sender_email || '').toLowerCase();
const addr = ([...raw.matchAll(/<([^>]+)>/g)].pop() || [, raw])[1];
const m = addr.match(/@([a-z0-9.-]+)\s*$/);
const domain = m ? m[1] : '';

const domains = {   // examples: replace with your vendors' real sender domains
  'bezeq.co.il': 'telecom', 'partner.co.il': 'telecom', 'cellcom.co.il': 'telecom',
  'paz.co.il': 'fuel', 'delek.co.il': 'fuel',
  'google.com': 'software', 'github.com': 'software', 'wolt.com': 'meals'
};

const hit = Object.keys(domains).find(k => domain === k || domain.endsWith('.' + k));
output = [{ category: hit ? domains[hit] : 'other' }];   // 'other' goes to a person for review
```

Subjects are deliberately not matched: Hebrew brand words are also first names and ordinary words (פז, מבזק), so a subject match reintroduces the false positives the domain map removes.

**Zapier Tables columns (Step 4):**

| Column | Source |
|--------|--------|
| Date | Email received date |
| Sender | Email sender |
| Subject | Email subject |
| Amount | Step 2 extracted amount |
| Category | Step 3 category output |
| Tax Deductible | Dropdown based on category |
| VAT Period | Derived from date |
| Notes | (empty, for manual annotation) |

---

## Template 7: Bimonthly VAT Period Summary

**Use case:** Automatically compile and send a VAT period summary at the end of each bimonthly period.

**Zap steps:**

| Step | App | Event | Configuration |
|------|-----|-------|---------------|
| 1. Trigger | Schedule by Zapier | Specific months | March, May, July, September, November, January on the 10th |
| 2. Action | Webhooks by Zapier | Custom Request | Morning token step (Template 1 step 6) |
| 3. Action | Code by Zapier | Run JavaScript | Search loop plus totals for the previous 2 months (code below) |
| 4. Action | Gmail | Send Email | Summary to accountant |
| 5. Action | Zapier Tables | Create Record | Archive period summary |

**Calculation logic (Step 3).** Paste `searchAll` and `rateOf` from the top of this file above it. Map `fromDate` / `toDate` (`YYYY-MM-DD`) for the period, and `patur` = `true` for an osek patur, whose 400 receipts are its revenue (with no VAT).

```javascript
const docs = await searchAll(inputData.token, { fromDate: inputData.fromDate, toDate: inputData.toDate });
let totalRevenue = 0, totalVAT = 0, invoiceCount = 0, receiptCount = 0;
const creditNotes = [];

for (const doc of docs) {
  // every document dated in the period counts, whatever its status today: an invoice
  // cancelled after the period closed still belongs to this period, and its 330 to the next
  const rate = rateOf(doc);
  const grossIls = Number(doc.amountLocal ?? doc.amount * rate);
  const vatIls = (doc.vat || 0) * rate;               // vat is not a required field
  if (doc.type === 305 || doc.type === 320) {
    totalRevenue += grossIls - vatIls;                // amount INCLUDES VAT
    totalVAT += vatIls;
    invoiceCount++;
  } else if (doc.type === 330) {
    totalRevenue -= Math.abs(grossIls) - Math.abs(vatIls);   // credit note dated in this period
    totalVAT -= Math.abs(vatIls);
    creditNotes.push(`${doc.number}: ${Math.abs(grossIls).toFixed(2)}`);
  } else if (doc.type === 400) {
    receiptCount++;
    if (/^(true|1|yes|כן)$/i.test(String(inputData.patur || '').trim())) totalRevenue += grossIls;   // osek patur: receipts are the turnover
  }
}

output = [{
  totalRevenue: totalRevenue.toFixed(2),
  totalVAT: totalVAT.toFixed(2),
  totalWithVAT: (totalRevenue + totalVAT).toFixed(2),
  invoiceCount, receiptCount,
  creditNotes: creditNotes.join(', ')
}];
```

For an osek murshe only 305, 320 and 330 enter the totals: a 400 receipt documents a payment against an invoice already counted. For an osek patur (`patur` = `true`) the 400s are the revenue. Each document counts in the period of its own date, so a credit note reduces the period it is dated in, which is how a cancellation after the period closed is reported. Revenue is converted with each document's rate, so USD and EUR invoices land in ILS. The figures are by document date; a business whose VAT falls due on receipt should confirm the basis with its accountant.

**Accountant email template (Step 4):**

Subject: "סיכום תקופת מע"מ {{period}} {{year}}"

```html
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <h2>סיכום תקופת מע"מ</h2>
  <table border="1" cellpadding="8" style="border-collapse: collapse; direction: rtl;">
    <tr><td>תקופה</td><td>{{period}}</td></tr>
    <tr><td>מספר חשבוניות</td><td>{{invoiceCount}}</td></tr>
    <tr><td>מספר קבלות</td><td>{{receiptCount}}</td></tr>
    <tr><td>חשבוניות זיכוי (קוזזו)</td><td>{{creditNotes}}</td></tr>
    <tr><td>סה"כ הכנסות (לפני מע"מ)</td><td>{{totalRevenue}} ש"ח</td></tr>
    <tr><td>סה"כ מע"מ</td><td>{{totalVAT}} ש"ח</td></tr>
    <tr><td>סה"כ כולל מע"מ</td><td>{{totalWithVAT}} ש"ח</td></tr>
  </table>
  <p><em>תזכורת: מועד הדיווח לתקופה זו - {{deadlineDate}} (קראו אותו מטבלת המועדים השנתית, אל תקבעו את ה-15 בקוד)</em></p>
  <p><em>דוח זה נוצר אוטומטית. נא לאמת מול הנתונים במערכת.</em></p>
</div>
```

---

## Template 8: Multi-Channel Payment Consolidation

**Use case:** Consolidate payments from multiple Israeli processors (Cardcom, Tranzila, Grow, Morning direct) into a single Zapier Table.

**Implementation:** Create 4 separate Zaps, all writing to the same Zapier Table. All processors send decimal amounts, never agorot.

**Every Zap first dedupes:** Zapier Tables > Find Record on the Reference column, then a Filter that continues only if nothing was found. A retried delivery or a manual replay otherwise logs the payment twice.

**Zap A: Cardcom payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Cardcom `WebHookUrl` JSON POST callback)
2. Filter, re-fetch and second Filter exactly as Template 1 steps 2, 3 and 3b, except that `CoinId` is mapped into the Currency column rather than required to be 1
3. Action: Zapier Tables > Create Record

**Zap B: Tranzila payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Tranzila Notify URL, form-encoded POST)
2. Filter: `Response` = `000` (or `0`). Check how a refund arrives on one test refund before trusting the sign of `sum`
3. Action: Zapier Tables > Create Record

**Zap C: Grow by Meshulam payments**
1. Trigger: Webhooks by Zapier > Catch Hook (Grow Webhooks service, JSON; enabled through Grow support)
2. Filter: `webhookKey` equals your account's key
3. Action: Zapier Tables > Create Record

**Zap D: Morning direct payments**
1. Trigger: Webhooks by Zapier > Catch Hook subscribed to Morning's `payment/received` webhook
2. Write `transactions[].gatewayTransactionId` into a Gateway Reference column. A Morning payment page clears through gateways such as Cardcom (`transactions[].gateway`, e.g. `cardcom`); if the same gateway account also feeds Zap A or C, have every Zap's dedupe look up both Reference and Gateway Reference, and confirm on one test payment that Morning's `gatewayTransactionId` equals the gateway's own ID, which no document states
3. Action: Zapier Tables > Create Record

**Dates.** Write each row's date as `YYYY-MM-DD` in `Asia/Jerusalem` (Formatter > Date/Time, To Timezone `Asia/Jerusalem`). Zapier's receive time is UTC, so a payment at 00:30 Israel time on 1 March would otherwise land on 28 February, in the previous VAT period. Use the vendor's own timestamp where there is one, and set Formatter's From Format to match it: Grow's `paymentDate` is day-first with a two-digit year (`14/10/21` in Grow's example), and Tables would misread it month-first.

**Shared Zapier Tables columns:**

| Column | Cardcom v11 Source | Tranzila Notify Source | Grow Webhook Source | Morning `payment/received` Source |
|--------|---------------|-----------------|-------------|----------------|
| Date | `TranzactionInfo.CreateDate`, converted | Receive time, converted to `Asia/Jerusalem` | `paymentDate`, converted from `DD/MM/YY` | `transactions[].createdAt` (Unix ms), converted |
| Source | Static: "Cardcom" | Static: "Tranzila" | Static: "Grow" | Static: "Morning" |
| Amount (incl. VAT) | `TranzactionInfo.Amount` | `sum` | `paymentSum` | `total` |
| Currency | `TranzactionInfo.CoinId` (1 = ILS, 2 = USD) | `currency` (1 = ILS) | not verified, check a test payload | `transactions[].currency` |
| Customer | `UIValues.CardOwnerName` | `contact` (echoed request parameter) | `fullName` | `payer.name` |
| Reference | `TranzactionId` | `ConfirmationCode` | `transactionCode` | `id` |
| Payment Method | Static: "Credit Card" | Static: "Credit Card" | `transactionType` | `channel` |
| Installments | `UIValues.NumOfPayments` | not verified | `paymentsNum` | `transactions[].installments` |

Keep a Currency column rather than heading the amount "ILS": Cardcom can charge in USD, and Morning reports each transaction's own currency. Tranzila and Grow field names come from those vendors' own docs (see `israeli-zapier-apps.md`); map from one real test payload before going live.

---

## Template 9: Freelancer End-of-Year Summary

**Use case:** "I need a Zap that compiles my annual invoice summary for tax filing."

1. Trigger: Schedule by Zapier, January
2. Action: Morning token step
3. Action: Code by Zapier, the Template 7 code with `fromDate` / `toDate` covering the whole previous year (if it hits the run-time limit, run it once per quarter and add the four results), with `patur` = `true` for an osek patur, whose receipts are its whole turnover
4. Action: Gmail, RTL summary to the accountant
5. Action: Zapier Tables, archive the annual summary

Do not encode the filing deadline in the Zap: it is announced annually and moves (for tax year 2025 it was 31.5.2026 for individuals not filing online, 30.6.2026 for those filing online, and 30.7.2026 for companies). Withholding at source and expenses are not in Morning's income documents, so the accountant supplies those.

## Zap pattern index (relocated from SKILL.md Step 1)

Match the Israeli business need to the correct Zap architecture.

| Business Need | Zap Trigger | Action Chain | Israeli Apps |
|---------------|-------------|--------------|--------------|
| Auto-receipt after payment | Cardcom/Tranzila webhook | Parse payment -> Create Morning doc -> Email customer | Cardcom, Morning |
| Invoice-to-bookkeeping sync | Morning new document webhook | Map fields -> Create entry in Zapier Tables or accounting tool -> Tag VAT period | Morning, Zapier Tables |
| Payment reminder (freelancer) | Schedule trigger (monthly) | Query unpaid invoices -> Filter overdue -> Send Hebrew reminder | Morning, email/SMS provider |
| E-commerce order processing | WooCommerce/Shopify new order | Create invoice in Morning -> Send email confirmation -> Update Monday.com board | Morning, Monday.com |
| WhatsApp order confirmation | Payment webhook | Format Hebrew message -> Send approved template | WhatsApp Business (or InforUMobile, Twilio) |
| Lead capture with CRM | Form submission (Typeform, Google Forms) | Extract Hebrew name -> Create CRM contact -> Send email follow-up | Monday.com, HubSpot |
| Multi-gateway consolidation | Multiple webhooks (Cardcom, Tranzila, Grow) | Normalize amounts -> Log to unified Zapier Table | Cardcom, Tranzila, Grow |

