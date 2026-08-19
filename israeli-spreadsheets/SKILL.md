---
name: israeli-spreadsheets
description: Generate Excel and Google Sheets spreadsheets with Israeli tax calculations, VAT, NIS formatting, RTL setup, and Hebrew-labeled financial templates. Use when user asks about Israeli tax spreadsheets, NIS-formatted Excel files, VAT calculations, salary slip templates, arnona estimators, common Hebrew formulas, or Israeli accounting worksheets. Covers 2026 tax brackets (after the 2026 bracket widening), Bituach Leumi rates, and openpyxl RTL configuration. Do not use for filing actual tax returns, legal tax advice, or generic spreadsheets without an Israeli context.
license: MIT
compatibility: Requires openpyxl for Excel generation (Google Sheets needs no install). Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Antigravity, Gemini CLI.
---


# Israeli Spreadsheets

## Instructions

### Step 1: Set Up Python Environment

Install openpyxl:

```bash
pip install openpyxl
```

### Step 2: Israeli Financial Constants

- VAT rate: 18% (raised from 17% on 2025-01-01). A rise to 19% was floated at the Finance Ministry but not enacted: the 2026 state budget contains no such increase.
- Tax brackets 2026 (after the 2026 bracket widening): 10% up to 84,120 NIS, 14% up to 120,720, 20% up to 228,000, 31% up to 301,200, 35% up to 560,280, then 47% on every additional shekel. The 20% and 31% bands were widened on 1 January 2026; the other thresholds were carried over from 2025 (frozen through 2027).
- There is no statutory 50% bracket. The official table stops at 47%. The 50% figure comes from adding the Section 121B(a) surtax of 3% on taxable income above 721,560 NIS, which gives 50% effective on personal-exertion income. Section 121B(a1) adds a FURTHER 2% on capital-source income above the same threshold, so investment income above it reaches 5% of surtax, not 3%. Label these as surtax, not as brackets, or a sheet will apply the capital limb to salary.
- Credit point value: 2,904 NIS/year (242 NIS/month). Entitlement is 2.25 points for a male Israeli resident and 2.75 for a female Israeli resident (the extra half point for a woman). Using 2.25 for everyone understates a woman's credit by 1,452 NIS/year.
- Bituach Leumi (employee, resident aged 18 to retirement age): 1.04% up to the reduced-collection step of 7,703 NIS/month, 7.00% above it up to the 51,910 NIS/month maximum insurable income; income above that is not insurable
- Health tax (employee, same category): 3.23% up to 7,703 NIS/month, 5.17% above
- Those two lines are ONE ROW of the official table. The employee rate varies by
  age, pension status and disability status, and for several categories it is
  ZERO. See "Step 2.5: the full employee rate table" below before generating any
  payroll sheet.

### Step 2.5: The Full Employee Bituach Leumi / Health Tax Table

The single 1.04% / 7.00% row above applies ONLY to an Israeli resident aged 18
to retirement age. The official Bituach Leumi table (the "לעובדים שכירים" rates
page) publishes a combined EMPLOYEE percentage for every category below. Several
are zero. Applying the standard row to a working pensioner or an under-18
employee over-deducts the entire employee contribution.

Combined employee rate (Bituach Leumi + health tax), reduced band up to 7,703
NIS/month | full band from there to 51,910 NIS/month:

| Employee category | Reduced | Full |
|---|---|---|
| Resident aged 18 to retirement age (the standard row) | 4.27% | 12.17% |
| Controlling shareholder in a closely-held company, 18 to retirement age | 4.25% | 11.96% |
| Man or woman above the old-age-pension eligibility age (70), or first became resident above 62 | 3.23% | 5.17% |
| Controlling shareholder, same category | 3.23% | 5.17% |
| Below retirement age, first became resident above 62 | 3.60% | 7.45% |
| Woman between retirement age and the male retirement age, first became resident above 62 | 3.28% | 5.52% |
| Between male retirement age and eligibility age, first became resident above 62 | 3.26% | 5.31% |
| Recipient of a work-disability or general-disability pension with an annual certificate | 3.23% | 5.17% |
| Controlling shareholder, same category | 3.23% | 5.17% |
| Woman between retirement age and male retirement age, not receiving an old-age pension | 3.95% | 10.24% |
| Men and women aged 67 to 70 not receiving an old-age pension | 3.93% | 10.03% |
| Controlling shareholder, same category | 3.93% | 10.03% |
| Under 18 | 0% | 0% |
| Controlling shareholder under 18 | 0% | 0% |
| Receiving an old-age pension (working pensioner) | 0% | 0% |
| Controlling shareholder, working pensioner | 0% | 0% |
| Soldier in regular service, organ donor, foreign resident from a treaty state | 1.04% | 7.00% |
| Controlling shareholder, same category | 1.02% | 6.79% |

Notes:
- The employer rate varies too, from 4.51% / 7.6% for the standard row down to
  0.61% / 2.12% for an under-18 employee or a working pensioner.
- The official page splits Bituach Leumi from health tax only for the standard
  row (1.04% / 7.00% and 3.23% / 5.17%). For the other categories it publishes
  the combined employee figure, which is what this table carries.
- Ask which category the employee falls into before generating a payroll sheet.
  Do not silently default to the standard row.

### Step 3: Tax Calculation Functions

Progressive (marginal) tax calculation with credit point deduction. Use Python Decimal for precision.

### Step 4: Formatted Workbooks

Set `ws.sheet_view.rightToLeft = True` for RTL sheets. NIS format: '#,##0.00 "₪"'

### Step 5: Templates

The bundled `scripts/generate_spreadsheet.py` produces three RTL Hebrew templates via `--template {invoice,salary,arnona} --output FILE.xlsx`:

- **Invoice (Heshbonit Mas)**: Business/customer details, item table, subtotal, 18% VAT, total
- **Salary slip (Tlush Maskoret)**: earnings, gross total, deductions and net
  pay, all as live formulas. The income-tax line uses the MONTHLY
  personal-exertion bracket grid and subtracts both the credit points and the
  Section 45A credit (35% of the employee-side pension deposit) from the tax
  owed, otherwise the withheld amount is overstated. The credit points, the
  Bituach Leumi and health-tax rates, the collection bands and the pension and
  keren hishtalmut rates are all INPUT cells, so the sheet can be set to the
  employee's actual category from the Step 2.5 table rather than defaulting to
  the standard row.
- **Arnona estimator**: builds the calculation structure (it is not a per-city rate table). It does NOT ship
  per-city rates, because a single number per city cannot be right. Each
  municipality publishes a `צו הארנונה` for the year with tariffs **per sqm per
  YEAR**, stratified by zone, building type and area band. Tel Aviv's 2026 order
  alone has 5 zones times 6 residential building types, running from 46.64 to
  139.60 NIS per sqm per year. Read the tariff for the specific property out of
  the municipality's order and enter it as an input.

### Step 6: Google Sheets (RTL and ILS)

Many users work in Google Sheets rather than Excel. For Hebrew worksheets:

- Turn on right-to-left sheet direction (a per-tab setting, reachable from the Format menu and from the toolbar RTL toggle). This flips column order so Hebrew reads naturally. It is per-tab: a newly added tab reverts to left-to-right.
- Set the spreadsheet locale via **File > Settings > Locale > Israel** so dates parse as DD/MM/YYYY and currency defaults to NIS.
- Format currency cells with **Format > Number > Custom number format** using `#,##0.00 ₪` (or apply the built-in ILS currency format from the locale).
- For live exchange rates, use `GOOGLEFINANCE`, for example `=GOOGLEFINANCE("CURRENCY:USDILS")` returns USD-to-ILS. Multiply a USD amount by this to convert to shekels.
- Google Sheets has no `openpyxl`-style API, build templates by hand or with Apps Script. The tax constants and VAT logic in this skill apply identically.
- Gemini-powered helpers: **enhanced Smart Fill with Gemini** (it surfaces
  itself as a live suggestion while you type rather than sitting behind an
  Insert menu item; the toggle lives under Tools > Suggestion controls) and the
  in-cell `=AI("prompt", range)` formula, which Google's function list also
  documents under the alias `Gemini()`. `=AI()` is a Google Workspace with
  Gemini feature, so it is tier-gated and usage-limited; a sheet full of `=AI()`
  calls will hit caps. Treat its output as a draft: an Israeli payroll or
  invoice line still needs the deterministic VAT and tax-bracket math, not an
  LLM guess.

### Step 6.5: Common Israeli Formulas

Reusable formulas that match the constants above. They work identically in Excel and Google Sheets unless noted.

**VAT (18%) inside one cell:**

```
Net to gross:                  =A1*1.18
Gross to net:                  =A1/1.18
VAT amount on a VAT-inclusive price: =A1-A1/1.18    (or =A1*0.18/1.18)
VAT amount on a VAT-exclusive price: =A1*0.18
```

**NIS currency format string (Excel custom format, symbol after the number per Israeli convention):**

```
#,##0.00 [$₪-40D]
```

The shorter `#,##0.00 "₪"` form also works and is what the bundled script uses.
Excel's `[$symbol-locale]` token expects a hexadecimal LCID, not a BCP-47 tag, so
the portable locale-tagged form is `[$₪-40D]` (0x040D is Hebrew-Israel). Newer
Excel builds may accept and normalise `[$₪-he-IL]` in the UI, but that literal
string is not portable through openpyxl or older builds.

**Progressive income tax (2026 brackets, annual income in A1, residents only) -- Google Sheets / Excel 365:**

```
=LET(inc, A1, credit, 2.25*2904,
  MAX(0,
    MIN(inc,84120)*0.10
    + MAX(0, MIN(inc,120720)-84120)*0.14
    + MAX(0, MIN(inc,228000)-120720)*0.20
    + MAX(0, MIN(inc,301200)-228000)*0.31
    + MAX(0, MIN(inc,560280)-301200)*0.35
    + MAX(0, MIN(inc,721560)-560280)*0.47
    + MAX(0, inc-721560)*0.50
    - credit))
```

The last two terms are NOT brackets. The statutory ladder ends at 47% above
560,280. `MAX(0, MIN(inc,721560)-560280)*0.47` plus `MAX(0, inc-721560)*0.50`
is 47% throughout plus the Section 121B(a) 3% surtax above 721,560, which is
correct ONLY for personal-exertion income (yegia ishit). For capital-source
income add Section 121B(a1)'s further 2%, giving 0.52 on the last term.

This ladder is also for personal-exertion income only. The Tax Authority
publishes a SEPARATE table for non-exertion income (rent, investment, most
passive income): 31% up to 301,200 NIS/year, 35% up to 560,280, then 47%. There
is no 10% / 14% / 20% band at all. Applying the ladder above to rental income
understates the tax substantially.

The `LET` helper keeps the formula readable and runs once instead of repeating `A1` seven times. For older Excel versions, expand `LET` into separate cells.

**Bituach Leumi + health tax (employee side, monthly salary in A1):**

```
Bituach Leumi:  =MIN(A1,7703)*0.0104 + MAX(0, MIN(A1,51910)-7703)*0.07
Health tax:     =MIN(A1,7703)*0.0323 + MAX(0, MIN(A1,51910)-7703)*0.0517
```

Income above the 51,910 NIS/month maximum insurable income is not insurable, so both formulas cap at that figure.

**Hebrew day of week from a Gregorian date in A1 (locale-aware):**

```
=TEXT(A1,"dddd")
```

Returns "ראשון", "שני", etc., when the workbook locale is he-IL. Outside an Israeli locale, fall back to `=CHOOSE(WEEKDAY(A1,1),"ראשון","שני","שלישי","רביעי","חמישי","שישי","שבת")`.

**Israeli holidays via Hebcal:** Hebcal does not have a direct spreadsheet function. Pick the geonameid deliberately: Jerusalem is 281184 and Tel Aviv is 293397, and they differ in candle-lighting offsets, so a sheet labelled for one city while querying the other emits wrong times. Either:
- Export a year-range CSV from `hebcal.com` (Yom Tov + minor holidays + parashat hashavua) and `VLOOKUP` against the Gregorian date column, or
- In Google Sheets, drive a Hebcal REST call from Apps Script (`UrlFetchApp.fetch('https://www.hebcal.com/hebcal?cfg=json&year=2026&maj=on&geo=geoname&geonameid=281184')` (281184 is Jerusalem; 293397 is Tel Aviv)) and write the result to a hidden sheet. The `hebcal` MCP server (listed in Step 7) is the cleanest path when an agent is driving the workbook.

### Step 7: Recommended MCP Servers

When building financial spreadsheets, these MCP servers from the directory provide live data so figures stay current:

- **boi-exchange**: Bank of Israel exchange rates, use for any spreadsheet that converts foreign currency to NIS or tracks the representative rate.
- **hebcal**: Hebrew/Jewish calendar dates, use when a worksheet needs Hebrew dates (e.g., a Hebrew-dated invoice) or must skip Shabbat and holidays.

**Hebrew/Jewish date handling:** openpyxl writes only Gregorian dates. To show a Hebrew date (e.g., "כ״ה אדר תשפ״ו") alongside the Gregorian one, compute it via the `hebcal` MCP or a library like `pyluach`, then write it as a text string in its own cell. Do not try to format a Gregorian date cell as Hebrew, the conversion has to happen before the value reaches the sheet.

## Examples

### Example 1: Create an Israeli Payroll Calculator
User says: "Build a payroll Excel sheet for an Israeli employee"
Actions:
1. Create RTL workbook with Hebrew headers
2. Add income tax brackets (2026 rates: 10%, 14%, 20% to 228K, 31% to 301.2K, 35%, then 47% on every additional shekel), and the Section 121B surtax as a SEPARATE line above 721,560 NIS
3. Calculate Bituach Leumi (employee 1.04% up to 7,703 NIS, 7% from there to 51,910), health tax (3.23% / 5.17% on the same bands)
4. Include pension (6.0% employee + 6.5% employer, plus 6.0% severance by employer) and keren hishtalmut
5. Apply Section 45a tax credit (35% of employee-side pension deposit) against the income tax line
6. Format all amounts as NIS with Hebrew labels
Result: Complete Israeli payroll calculator with net salary computation that reflects the 45a pension credit

### Example 2: Generate Israeli Invoice Template
User says: "Create a tax invoice template in Hebrew with VAT calculation"
Actions:
1. Set up RTL Excel with Hebrew column headers
2. Add business details fields (osek murshe number, address)
3. Include line items with quantity, unit price, subtotal
4. Calculate 18% VAT, display total in NIS
5. Add invoice number and Hebrew date fields
Result: VAT-compliant Hebrew invoice spreadsheet template

## Bundled Resources

### Scripts
- `scripts/generate_spreadsheet.py` -- Generates ready-to-use RTL Hebrew Excel templates with Israeli tax constants and NIS formatting baked in. Three templates: `invoice` (heshbonit mas with 18% VAT line), `salary` (tlush maskoret with earnings and deductions), `arnona` (annual and bi-monthly arnona calculator; the per-sqm tariff is a user input, not a shipped constant). Run: `python scripts/generate_spreadsheet.py --template {invoice,salary,arnona} --output FILE.xlsx`. Requires `openpyxl`.

### References
- `references/israeli-tax-rates.md` -- Israeli income tax brackets, Bituach Leumi and health tax rates, VAT rate, pension requirements, minimum wage, and common financial constants. Consult when building any financial calculations for Israeli context.

## Gotchas

- Hebrew text in spreadsheets requires RTL cell alignment. Default LTR alignment causes Hebrew to display incorrectly, with punctuation and numbers appearing on the wrong side.
- Israeli date format in spreadsheets is DD/MM/YYYY, not MM/DD/YYYY. Excel and Google Sheets may auto-parse "01/03/2026" as January 3rd (US) instead of March 1st (Israeli). Always set locale to Hebrew (Israel).
- NIS currency formatting places the symbol after the number, not before it (US-style). Both `₪` and the abbreviation `ש"ח` are acceptable in Israel. This skill and the bundled script standardize on `#,##0.00 ₪` (symbol after the number). Pick one convention and use it consistently across the whole workbook, do not mix `₪` and `ש"ח` in the same sheet.
- Israeli tax calculations in spreadsheets must account for VAT at 18%. Agents may hardcode older VAT rates (17%) from pre-2025 training data.
- 2026 income tax brackets are NOT the same as 2025. Chapter C of the Economic Efficiency Law 2026 widened the 20% and 31% bands effective 1 January 2026 (20% now to 228,000 NIS/yr; 31% to 301,200 NIS/yr; the 35% floor moved up to 301,201). Older payroll templates copied from 2024-2025 sources will overstate the tax for middle-income employees.
- Sorting Hebrew text depends on the collation of the Excel build and its system locale, and Hebrew final-form letters (ך ם ן ף ץ) sort by codepoint rather than beside their base letters unless the collation handles them. For Hebrew name lists, verify the order by eye rather than trusting the sort, or sort in Google Sheets. There is no published error rate for this; treat any specific percentage you see quoted as unsourced.
- Merged cells in an RTL Excel sheet sometimes "flip" their alignment when the file is opened by an Excel build with a non-Israeli system locale: the merged span renders in the wrong direction even though `rightToLeft` is set. Avoid merged cells across rows in RTL workbooks; use centered text in a wider unmerged column instead.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Israeli Tax Authority | https://www.gov.il/en/departments/israel_tax_authority | Income tax brackets, credit points, VAT rate |
| Bituach Leumi | https://www.btl.gov.il/English%20Homepage/Pages/default.aspx | Social security and health tax rates |
| openpyxl Documentation | https://openpyxl.readthedocs.io/en/stable/ | Writing XLSX files with formatting from Python |
| Bank of Israel | https://www.boi.org.il/en/ | Exchange rates, monetary policy, CPI for indexation |
| Excel RTL Worksheet (Microsoft Learn) | https://learn.microsoft.com/en-us/office/vba/api/excel.worksheet.displayrighttoleft | Sheet direction and RTL rendering |

## Troubleshooting

### Error: "NIS symbol appears on wrong side of number"
Cause: Excel locale not set for Hebrew/Israel
Solution: Use format string `#,##0.00 ₪` (symbol after number) for Israeli convention, or set the workbook locale to he-IL.

### Error: "Hebrew column headers display as question marks"
Cause: Workbook not saved with UTF-8 encoding or font doesn't support Hebrew
Solution: Ensure the workbook uses a Unicode-compatible font (like David, Heebo, or Arial). When using openpyxl, Hebrew strings are automatically UTF-8 encoded.
