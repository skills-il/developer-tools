# Israeli Billing Cycle Automation Patterns

Detailed Make.com router configurations for automating Israeli billing cycles. Covers VAT periods, advance income-tax payments (mikdamot, monthly by default), annual reporting, and payroll schedules.

## Bimonthly VAT Reporting (Doch Du-Hodshi)

An osek murshe reports VAT every two months when turnover in the determining year is up to 1,775,000 NIS (2026; 1,805,000 NIS from 1 January 2027) and monthly above it; an osek patur files only an annual declaration, by 31 January. Reports are due by the 15th of the month after the period. Online filers who are not detailed reporters may file and pay up to the 19th (18:30 on the Tax Authority site). The calendar below is the bimonthly case; a monthly filer uses the same logic with one-month periods.

### VAT Period Calendar

| Period | Months | Report Due | Payment Due | Make.com Trigger Date |
|---|---|---|---|---|
| 1 | January - February | March 15 | March 15 | March 1 |
| 2 | March - April | May 15 | May 15 | May 1 |
| 3 | May - June | July 15 | July 15 | July 1 |
| 4 | July - August | September 15 | September 15 | September 1 |
| 5 | September - October | November 15 | November 15 | November 1 |
| 6 | November - December | January 15 | January 15 | January 1 |

Set the Make.com scheduled trigger to run on the 1st of the reporting month. This gives 14 days to review the automated summary before the filing deadline.

### Router Configuration for VAT Periods

Build a 6-branch Router where each branch filters transactions for a specific bimonthly period.

**Branch filter expressions:**

Branch 1 (Jan-Feb):
```
formatDate(item.date; "M") >= 1
AND formatDate(item.date; "M") <= 2
AND formatDate(item.date; "YYYY") = formatDate(now; "YYYY")
```

Branch 2 (Mar-Apr):
```
formatDate(item.date; "M") >= 3
AND formatDate(item.date; "M") <= 4
AND formatDate(item.date; "YYYY") = formatDate(now; "YYYY")
```

Apply the same pattern for remaining branches (5-6, 7-8, 9-10, 11-12).

**Dynamic period detection (alternative):**

Instead of 6 fixed branches, use a single formula to detect the current VAT period:

```
ceil(formatDate(now; "M") / 2)
```

This returns 1 for Jan-Feb, 2 for Mar-Apr, through 6 for Nov-Dec. Use this value to dynamically set date ranges:

- Period start month: `(period - 1) * 2 + 1`
- Period end month: `period * 2`

### Period Summary for the Accountant (not a VAT computation)

After filtering by period, aggregate what Morning already computed instead of recomputing VAT:

| Branch | Document types | What to sum |
|---|---|---|
| Income | 305 (tax invoice), 320 (tax invoice / receipt) | each document's `subtotal` (before VAT) and its VAT amount as Morning returns it |
| Credits | 330 (credit invoice) | the same fields, as reductions |

Morning's document payload carries `subtotal`, a `tax` array and `total` (see the `document/created` sample in Morning's help center), so the summary never multiplies by a hardcoded VAT rate. Group documents whose document-level `vatType` is 1 (exempt) separately, so they appear in turnover with no VAT.

Hand the totals to the business's accountant. Input-VAT deductibility, zero-rated exports and mixed exempt activity are their determination; this reference does not compute a VAT liability.

## Advance Tax Payments (Mikdamot)

By law, self-employed advance income-tax payments are MONTHLY: report the previous month's turnover (excluding VAT) and pay by the 15th. The assessing officer may approve a low-turnover business to report and pay every two months, on the 15th, and only a business whose advance booklet (פנקס מקדמות) shows that approval may do so. Paying through the Tax Authority website extends the deadline to the 19th at 18:30. Do not infer the mikdamot frequency from the VAT frequency: read it from the booklet and store it per business.

### Router Configuration

**Period detection:** for a monthly payer the period is the previous calendar month (`formatDate(addMonths(now; -1); "YYYY-MM")`). For an approved bimonthly payer, reuse the VAT formula `ceil(formatDate(now; "M") / 2)`, which returns 1-6.

**Filter expression for bimonthly transactions:**

```
formatDate(item.date; "M") >= ((period - 1) * 2 + 1)
AND formatDate(item.date; "M") <= (period * 2)
AND formatDate(item.date; "YYYY") = formatDate(now; "YYYY")
```

### Advance Payment Calculation

1. Fetch total turnover for the period, excluding VAT (the rate applies to income, not profit)
2. Multiply by the advance rate printed in the booklet (set per business by the assessing officer, and changeable on request)
3. If clients withheld tax at source (ניכוי במקור), confirm with the business's accountant how it is credited before netting it off; this reference does not assert a netting rule

Store the advance rate in a Make.com Data Store or Set Variable module, since it varies per business and can change.

## Annual Reporting

### Key Annual Dates

| Deadline | Report | Trigger Configuration |
|---|---|---|
| January 18 | Form 126 employer wage reconciliation, covering January to December of the PRECEDING year | January 1 |
| July 18 | Form 126 employer wage reconciliation, covering January to June of the SAME year | July 1 |

Other annual deadlines (the annual employee pay certificate, the annual report on payments to suppliers, the annual income-tax return and its yearly extensions) are published by the Tax Authority each year. They are deliberately not hardcoded here: read the current year's dates and store them in a Data Store.

Form 126 is filed at three points, not two. Bituach Leumi states the schedule as
`עד 18 ביולי בכל שנה` for January to June of that year, `עד 18 בינואר בכל שנה` for January
to December of the preceding year, and `עד 30 באפריל בכל שנה` for the preceding tax year,
the last being the extension under section 166 of the Income Tax Ordinance, which
constitutes the final reconciliation approved by the employer's accountant. Note the day is
the **18th**, not the end of the month, which is where a scenario scheduled on a
month-end pattern will silently miss it.

### Year-End Aggregation Scenario

Make caps a single scenario run at 40 minutes on paid plans and 5 minutes on Free, so a full-year Morning search can be cut off. Run one month per execution and accumulate into a Data Store instead of fetching the whole year at once.

Build a scenario that runs on January 1 and produces a full-year summary:

1. **Trigger:** Scheduled for January 1
2. **Morning Search:** Fetch all documents for the previous year (`fromDate: YYYY-01-01`, `toDate: YYYY-12-31`)
3. **Iterator:** Process each document
4. **Router (4 branches):**
   - Branch 1: Tax Invoices (type 305) -> sum for total revenue
   - Branch 2: Credit Notes (type 330) -> sum for deductions
   - Branch 3: Receipts (type 400) -> sum for payments received
   - Branch 4: Expenses -> sum for deductible expenses
5. **Array Aggregators:** One per branch
6. **Output:** Google Sheets row or email with annual summary

### Annual Reconciliation

Compare the sum of 6 bimonthly VAT reports against the annual total. Discrepancies can arise from:
- Timing differences (invoice in December, payment in January)
- Credit notes applied across periods
- Currency conversion differences for export transactions

Add a validation step that compares `sum(bimonthly totals)` with `annual total` and flags differences above a tolerance you set.

## Payroll Cycle Patterns (Sekher)

Israeli payroll runs monthly, with several recurring obligations:

### Monthly Payroll Schedule

| Day of Month | Action | Automation |
|---|---|---|
| 1st-9th | Previous month's pay processed | Watch for payroll file from HR system |
| 15th | Social Security (Bituach Leumi) payment, employer AND employee shares, via Tofes 102 | Aggregate and prepare the payment summary. Due by the 15th of the month after the salary month. Withheld employee contributions not transferred within 40 days of the statutory pay date are a criminal offence. |
| 16th | Income-tax withholding (ניכויים) report and payment | Generate withholding report. The Tax Authority's 2026 calendar puts withholding on the 16th, not the 15th. For filing deadlines only, the Tax Authority treats Friday, Saturday and Sunday as weekly rest days (one per religion), so a deadline on any of them moves to the following Monday (see "Combining Deadline Awareness with Shabbat" below) |
| Last day | Salary bank transfer | Trigger payroll file generation |

### Payroll Rates (deliberately not tabulated here)

Bituach Leumi, health-insurance and pension rates, the reduced-rate threshold and the income ceiling all change every January, and no scenario in this skill computes them. Do not hardcode them in a Make scenario from memory: take the current year's figures from btl.gov.il, or use the `israeli-payroll-calculator` skill, and store them in a Data Store so one January update fixes every scenario.

## Shabbat and Holiday Scheduling

### Weekly Schedule Template

For any scenario that should respect Israeli business hours:

| Day | Make.com Day Number | Allowed Hours | Notes |
|---|---|---|---|
| Sunday (yom rishon) | 0 | 09:00 - 18:00 | First business day |
| Monday (yom sheni) | 1 | 09:00 - 18:00 | |
| Tuesday (yom shlishi) | 2 | 09:00 - 18:00 | |
| Wednesday (yom revi'i) | 3 | 09:00 - 18:00 | |
| Thursday (yom hamishi) | 4 | 09:00 - 18:00 | Last full business day |
| Friday (yom shishi) | 5 | 09:00 - 13:00 | Half day, ends before Shabbat |
| Saturday (Shabbat) | 6 | NONE | Do not run |

### Make.com Filter for Business Hours

Place this filter as the first module after the trigger:

```
formatDate(now; "d") >= 0
AND formatDate(now; "d") <= 4
AND formatDate(now; "H") >= 9
AND formatDate(now; "H") < 18
```

For Friday inclusion, use an OR branch:
```
(formatDate(now; "d") >= 0 AND formatDate(now; "d") <= 4 AND formatDate(now; "H") >= 9 AND formatDate(now; "H") < 18)
OR
(formatDate(now; "d") = 5 AND formatDate(now; "H") >= 9 AND formatDate(now; "H") < 13)
```

### Israeli Holiday Handling

**Recommended:** Use the Hebcal community module on Make.com (`apps.make.com/hebcal-ryuwr8`). No API key required. It handles Shabbat and holiday detection natively.

**Alternative (HTTP module):** Use the Hebcal REST API:

```
https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=now&maj=on&geo=pos&latitude=32.0853&longitude=34.7818
```

Parse the JSON response for entries where `date` matches today and `category` is `"holiday"`.

**Major holidays that block business operations:**

| Holiday | Typical Months | Duration |
|---|---|---|
| Rosh Hashana | September-October | 2 days |
| Yom Kippur | September-October | 1 day |
| Sukkot | September-October | 7 days (first and last are full holidays) |
| Pesach | March-April | 7 days (first and last are full holidays) |
| Shavuot | May-June | 1 day |
| Yom Ha'atzmaut | April-May | 1 day |

**Chol HaMoed (intermediate days):** Some businesses operate on reduced hours during Chol HaMoed (intermediate days of Sukkot and Pesach). For B2B automations, treat these as half-days similar to Friday.

### Combining Deadline Awareness with Shabbat

The Tax Authority's rule, as stated in its 2026 reporting calendar: when a statutory 15th / 16th / 23rd deadline falls on a weekly rest day "according to the filer's religion", meaning Friday, Saturday or Sunday, the report and payment move to the next business day after the rest day, and the Tax Authority's computer system (שע"מ) records the moved date as the Monday. This is specific to these filing deadlines: Sunday is still an ordinary business day for scheduling and business hours (table above). Build a deadline resolution function:

1. Set the target date (15th for VAT and mikdamot, 16th for withholding, 23rd for the detailed VAT report)
2. If it falls on Friday, Saturday or Sunday (`formatDate(date; "d")` returns 5, 6 or 0), move it to the following Monday; a holiday or an ad-hoc extension can push it later
3. Treat the Tax Authority's published calendar for the year as the primary source (it carries holidays and one-off extensions); Hebcal is only a fallback check
4. Use the resolved date for reminders and report triggers

## Make.com Data Store for Period Tracking

Create a Make.com Data Store to track which billing periods have been processed:

**Data Store Fields:**

| Field | Type | Purpose |
|---|---|---|
| `period_type` | Text | `vat_bimonthly` or `vat_monthly`, `advance_monthly` (or `advance_bimonthly` when the booklet approves it), `annual` |
| `period_key` | Text | e.g., `2026-P1`, `2026-P2`, `2026` |
| `status` | Text | `pending`, `processing`, `completed`, `filed` |
| `total_income` | Number | Aggregated income for the period |
| `total_expenses` | Number | Aggregated expenses for the period |
| `vat_total` | Number | Sum of the VAT amounts Morning returned (for the accountant) |
| `processed_at` | Date | When the scenario last ran |
| `filed_at` | Date | When the report was filed (manual entry) |

Use "Search records" at the start of each scenario run to check if the current period has already been processed. This prevents duplicate processing if a scenario runs more than once.

## Refunds and Chargebacks

Every payment-to-invoice scenario needs the reverse path. When a gateway reports a refund, create a Morning 330 (credit invoice) linked to the original document through `linkedDocumentIds` with `linkType` `cancel` ("Document cancels another"), and deduplicate on the gateway's refund or transaction ID exactly as for the original payment. Without it a refunded sale keeps an uncancelled tax invoice.
