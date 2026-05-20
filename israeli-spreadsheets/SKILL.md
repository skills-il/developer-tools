---
name: israeli-spreadsheets
description: Generate Excel and Google Sheets spreadsheets with Israeli tax calculations, VAT, NIS formatting, RTL setup, and Hebrew-labeled financial templates. Use when user asks about Israeli tax spreadsheets, NIS-formatted Excel files, VAT calculations, salary slip templates, arnona estimators, common Hebrew formulas, or Israeli accounting worksheets. Covers 2026 tax brackets (post Amendment 288), Bituach Leumi rates, and openpyxl RTL configuration.
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

- VAT rate: 18% (raised from 17% on 2025-01-01, held at 18% through the 2026 budget; the proposed 19% hike was dropped)
- Tax brackets 2026 (post Amendment 288): 10% up to 84,120 NIS, 14% up to 120,720, 20% up to 228,000, 31% up to 301,200, 35% up to 560,280, 47% up to 721,560, 50% above. The 20% and 31% bands were widened on 1 January 2026; the other thresholds were carried over from 2025 (frozen through 2027).
- Credit point value: 2,904 NIS/year (242 NIS/month), 2.25 points for residents
- Bituach Leumi (employee): 0.40% up to 7,122 NIS/month, 7.00% from 7,123 up to the 49,030 NIS/month ceiling; income above the ceiling is not insurable
- Health tax (employee): 3.10% up to 7,122 NIS/month, 5.00% above

### Step 3: Tax Calculation Functions

Progressive (marginal) tax calculation with credit point deduction. Use Python Decimal for precision.

### Step 4: Formatted Workbooks

Set `ws.sheet_view.rightToLeft = True` for RTL sheets. NIS format: '#,##0.00 "₪"'

### Step 5: Templates

The bundled `scripts/generate_spreadsheet.py` produces three RTL Hebrew templates via `--template {invoice,salary,arnona} --output FILE.xlsx`:

- **Invoice (Heshbonit Mas)**: Business/customer details, item table, subtotal, 18% VAT, total
- **Salary slip (Tlush Maskoret)**: Earnings, deductions (income tax, Bituach Leumi, health tax, pension, keren hishtalmut), net pay. For the "income tax" line, subtract the Section 45a pension credit (35% of the employee-side pension deposit, subject to annual ceilings) from the progressive tax owed, otherwise the withheld amount will be overstated.
- **Arnona estimator**: Rates by city (Tel Aviv 55.80, Jerusalem 40.50, Haifa 33.20, Beer Sheva 27.90, Netanya 43.10 per sqm/bi-monthly)

### Step 6: Google Sheets (RTL and ILS)

Many users work in Google Sheets rather than Excel. For Hebrew worksheets:

- Set sheet direction via **Sheet > Right-to-left** (or the toolbar RTL toggle). This flips column order so Hebrew reads naturally.
- Set the spreadsheet locale via **File > Settings > Locale > Israel** so dates parse as DD/MM/YYYY and currency defaults to NIS.
- Format currency cells with **Format > Number > Custom number format** using `#,##0.00 ₪` (or apply the built-in ILS currency format from the locale).
- For live exchange rates, use `GOOGLEFINANCE`, for example `=GOOGLEFINANCE("CURRENCY:USDILS")` returns USD-to-ILS. Multiply a USD amount by this to convert to shekels.
- Google Sheets has no `openpyxl`-style API, build templates by hand or with Apps Script. The tax constants and VAT logic in this skill apply identically.
- Gemini-powered helpers: the **Insert > Smart fill** menu and the in-cell `=AI("prompt", range)` formula (rolled out to most Workspace tiers during 2026) can categorize Hebrew text, summarize columns, or draft a formula from a natural-language description. Treat `=AI()` output as a draft: an Israeli payroll or invoice line still needs the deterministic VAT and tax-bracket math, not an LLM guess.

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
#,##0.00 [$₪-he-IL]
```

The shorter `#,##0.00 "₪"` form also works; the `[$₪-he-IL]` variant carries the Hebrew/Israel locale tag so the symbol survives a re-save by a user whose Excel runs in another locale.

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

The `LET` helper keeps the formula readable and runs once instead of repeating `A1` seven times. For older Excel versions, expand `LET` into separate cells.

**Bituach Leumi + health tax (employee side, monthly salary in A1):**

```
Bituach Leumi:  =MIN(A1,7122)*0.004 + MAX(0, MIN(A1,49030)-7122)*0.07
Health tax:     =MIN(A1,7122)*0.031 + MAX(0, MIN(A1,49030)-7122)*0.05
```

Income above the 49,030 NIS/month ceiling is not insurable, so both formulas cap at that figure.

**Hebrew day of week from a Gregorian date in A1 (locale-aware):**

```
=TEXT(A1,"dddd")
```

Returns "ראשון", "שני", etc., when the workbook locale is he-IL. Outside an Israeli locale, fall back to `=CHOOSE(WEEKDAY(A1,1),"ראשון","שני","שלישי","רביעי","חמישי","שישי","שבת")`.

**Israeli holidays via Hebcal:** Hebcal does not have a direct spreadsheet function. Either:
- Export a year-range CSV from `hebcal.com` (Yom Tov + minor holidays + parashat hashavua) and `VLOOKUP` against the Gregorian date column, or
- In Google Sheets, drive a Hebcal REST call from Apps Script (`UrlFetchApp.fetch('https://www.hebcal.com/hebcal?cfg=json&year=2026&maj=on&geo=geoname&geonameid=293397')`) and write the result to a hidden sheet. The `hebcal` MCP server (listed in Step 7) is the cleanest path when an agent is driving the workbook.

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
2. Add income tax brackets (2026 rates after Amendment 288: 10%, 14%, 20% to 228K, 31% to 301.2K, 35%, 47%, 50%)
3. Calculate Bituach Leumi (0.4%/7% employee-side thresholds), health tax (3.1%/5%)
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
- `scripts/generate_spreadsheet.py` -- Generates ready-to-use RTL Hebrew Excel templates with Israeli tax constants and NIS formatting baked in. Three templates: `invoice` (heshbonit mas with 18% VAT line), `salary` (tlush maskoret with earnings and deductions), `arnona` (per-city rate calculator with bi-monthly and annual formulas). Run: `python scripts/generate_spreadsheet.py --template {invoice,salary,arnona} --output FILE.xlsx`. Requires `openpyxl`.

### References
- `references/israeli-tax-rates.md` -- Israeli income tax brackets, Bituach Leumi and health tax rates, VAT rate, pension requirements, minimum wage, and common financial constants. Consult when building any financial calculations for Israeli context.

## Gotchas

- Hebrew text in spreadsheets requires RTL cell alignment. Default LTR alignment causes Hebrew to display incorrectly, with punctuation and numbers appearing on the wrong side.
- Israeli date format in spreadsheets is DD/MM/YYYY, not MM/DD/YYYY. Excel and Google Sheets may auto-parse "01/03/2026" as January 3rd (US) instead of March 1st (Israeli). Always set locale to Hebrew (Israel).
- NIS currency formatting places the symbol after the number, not before it (US-style). Both `₪` and the abbreviation `ש"ח` are acceptable in Israel. This skill and the bundled script standardize on `#,##0.00 ₪` (symbol after the number). Pick one convention and use it consistently across the whole workbook, do not mix `₪` and `ש"ח` in the same sheet.
- Israeli tax calculations in spreadsheets must account for VAT at 18%. Agents may hardcode older VAT rates (17%) from pre-2025 training data.
- 2026 income tax brackets are NOT the same as 2025. Amendment 288 widened the 20% and 31% bands effective 1 January 2026 (20% now to 228,000 NIS/yr; 31% to 301,200 NIS/yr; the 35% floor moved up to 301,201). Older payroll templates copied from 2024-2025 sources will overstate the tax for middle-income employees.
- Excel's SORT and the column header sort on Hebrew text matches the first letter only on some builds; subsequent letters fall back to Unicode codepoint order, which is not the Hebrew alphabetical order. For Hebrew names lists, expect ~5-10% misordering and verify by eye, or sort in Google Sheets which uses a Unicode collation that handles Hebrew correctly.
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
