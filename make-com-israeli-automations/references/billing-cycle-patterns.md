# Israeli Billing Cycle Automation Patterns

Detailed Make.com router configurations for automating Israeli billing cycles. Covers bimonthly VAT, bimonthly advance payments (mikdamot), annual reporting, and payroll schedules.

## Bimonthly VAT Reporting (Doch Du-Hodshi)

Most Israeli businesses with annual revenue above the exemption threshold report VAT bimonthly. The Israel Tax Authority (Rashut HaMisim) requires reporting by the 15th of the month following the period end.

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

### VAT Calculation Pattern

After filtering transactions by period, route into two sub-branches:

| Branch | Document Types | Purpose |
|---|---|---|
| Income (Output VAT) | 305 (Tax Invoice), 320 (Tax Invoice/Receipt) | VAT collected from customers |
| Credits (Reductions) | 330 (Credit Note/Refund) | Reduces VAT for this period |

**Aggregation formula:**

```
Output VAT (mas etzot) = Sum of income amounts * VAT rate
Input VAT (mas tsurot) = Sum of expense amounts * VAT rate
VAT payable = Output VAT - Input VAT
```

Current VAT rate: 18% (as of January 2025).

Use an Array Aggregator module after each branch, with the `amount` field as the aggregation target and `sum` as the function.

### Handling Exempt Transactions

Not all transactions carry VAT. Filter by `vatType` before aggregating:

| vatType | Treatment |
|---|---|
| 0 (Exempt) | Exclude from VAT calculation, include in revenue total |
| 1 (Included) | Extract VAT: `amount - (amount / 1.18)` |
| 2 (Excluded) | Add VAT: `amount * 0.18` |

### Special Cases

**Zero-rated exports:** Services exported to foreign clients are zero-rated (0% VAT). These appear in the revenue total but not in VAT calculations. Filter by `currency != "ILS"` or by a specific export flag.

**Mixed transactions:** Some businesses have both VAT-liable and exempt activities. Use a secondary router to split these before aggregation.

**Credit notes:** Credit notes (type 330) reduce the VAT for the period they are issued in, not the period of the original invoice.

## Bimonthly Advance Tax Payments (Mikdamot)

Self-employed individuals (atzma'im) and some companies pay bimonthly advance tax (mikdamot mas) based on projected annual income. Mikdamot follow the same bimonthly periods as VAT reporting.

### Bimonthly Calendar

| Period | Months | Payment Due | Make.com Trigger Date |
|---|---|---|---|
| 1 | January - February | March 15-19 | March 1 |
| 2 | March - April | May 15-19 | May 1 |
| 3 | May - June | July 15-19 | July 1 |
| 4 | July - August | September 15-19 | September 1 |
| 5 | September - October | November 15-19 | November 1 |
| 6 | November - December | January 15-19 | January 1 |

### Router Configuration

**Period detection formula:**

Use the same formula as VAT period detection:

```
ceil(formatDate(now; "M") / 2)
```

Returns 1-6 for the current bimonthly period.

**Filter expression for bimonthly transactions:**

```
formatDate(item.date; "M") >= ((period - 1) * 2 + 1)
AND formatDate(item.date; "M") <= (period * 2)
AND formatDate(item.date; "YYYY") = formatDate(now; "YYYY")
```

### Advance Payment Calculation

The advance payment is typically a percentage of revenue set by the Tax Authority:

1. Fetch total revenue for the bimonthly period
2. Apply the advance percentage (set individually by the Tax Authority, commonly 5-15% for new businesses)
3. Subtract any tax deducted at source (nikui mas bamakor) during the period

The formula: `Advance payment = (Period revenue * advance rate) - Tax withheld`

Store the advance rate in a Make.com Data Store or Set Variable module, since it varies per business and is updated annually.

## Annual Reporting

### Key Annual Dates

| Deadline | Report | Trigger Configuration |
|---|---|---|
| January 31 | Annual payroll summary (106) | January 1 |
| March 31 | 856 form (payments to suppliers) | March 1 |
| April 30 | Annual income tax return (online filing) | April 1 |
| May 31+ | Annual income tax return (accountant filing) | May 1 |
| June 30 | Annual VAT summary | June 1 |

### Year-End Aggregation Scenario

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

Add a validation step that compares `sum(bimonthly totals)` with `annual total` and flags differences above 1%.

## Payroll Cycle Patterns (Sekher)

Israeli payroll runs monthly, with several recurring obligations:

### Monthly Payroll Schedule

| Day of Month | Action | Automation |
|---|---|---|
| 1st-9th | Previous month's pay processed | Watch for payroll file from HR system |
| 10th | Social Security (Bituach Leumi) payment | Aggregate and prepare payment summary |
| 15th | Tax withholding (nikui mas) deposit | Generate withholding report |
| Last day | Salary bank transfer | Trigger payroll file generation |

### Router for Payroll Components

| Component | Employer Rate | Employee Rate | Notes |
|---|---|---|---|
| Bituach Leumi (national insurance) | 4.51% (up to threshold) / 7.60% (above) | 1.04% (up to threshold) / 7.00% (above) | 2026: reduced rate up to 7,703 NIS, full rate from there to the 51,910 NIS ceiling |
| Bituach Briut (health insurance) | N/A (employee only) | 3.23% (up to threshold) / 5.17% (above) | Health insurance is deducted from the employee ONLY, employers pay no health share. Same 7,703 NIS reduced/full threshold |
| Pension (mandatory) | 6.5% benefits + 6% severance (pitzuim) = 12.5% | 6.0% | Mandatory pension Extension Order: total 18.5% of salary (employee 6% + employer 6.5% benefits + employer 6% severance), up to the insurable ceiling |
| Education Fund (keren hishtalmut) | 7.5% of salary | 2.5% of salary | Optional, common benefit |
| Income Tax | N/A | Progressive brackets | Use the annual income-tax brackets (madregot mas) from the Tax Authority |

Note: these are the 2026 salaried-employee rates (verified against btl.gov.il). Bituach Leumi / Briut rates, the reduced-rate threshold (7,703 NIS in 2026), and the income ceiling (51,910 NIS in 2026) change annually. Always verify against the Bituach Leumi and Tax Authority websites for the current year's values.

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

When a filing deadline (e.g., VAT report due the 15th) falls on Shabbat or a holiday, it is typically extended to the next business day. Build a deadline resolution function:

1. Set target date to the 15th
2. Check if it falls on Shabbat (day = 6): push to Sunday (day = 0)
3. Check if it falls on a holiday via Hebcal: push to the next non-holiday day
4. Use this resolved date for reminder notifications and report triggers

## Make.com Data Store for Period Tracking

Create a Make.com Data Store to track which billing periods have been processed:

**Data Store Fields:**

| Field | Type | Purpose |
|---|---|---|
| `period_type` | Text | `vat_bimonthly`, `advance_bimonthly`, `annual` |
| `period_key` | Text | e.g., `2026-P1`, `2026-P2`, `2026` |
| `status` | Text | `pending`, `processing`, `completed`, `filed` |
| `total_income` | Number | Aggregated income for the period |
| `total_expenses` | Number | Aggregated expenses for the period |
| `vat_payable` | Number | Calculated VAT due |
| `processed_at` | Date | When the scenario last ran |
| `filed_at` | Date | When the report was filed (manual entry) |

Use "Search records" at the start of each scenario run to check if the current period has already been processed. This prevents duplicate processing if a scenario runs more than once.
