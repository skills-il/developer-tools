---
name: israeli-spreadsheets
description: Generate Excel spreadsheets with Israeli tax calculations, VAT, NIS formatting, and Hebrew-labeled financial templates. Use when user asks about Israeli tax spreadsheets, NIS-formatted Excel files, VAT calculations, salary slip templates, arnona estimators, or Israeli accounting worksheets. Covers 2025 tax brackets, Bituach Leumi rates, and openpyxl RTL configuration.
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

- VAT rate: 18% (2025)
- Tax brackets 2025: 10% up to 84,120 NIS, 14% up to 120,720, 20% up to 193,800, 31% up to 269,280, 35% up to 560,280, 47% up to 721,560, 50% above
- Credit point value: 2,904 NIS/year, 2.25 points for residents
- Bituach Leumi: 0.4% (low) / 7% (high)
- Health tax: 3.1% (low) / 5% (high)

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
2. Add income tax brackets (2025 rates: 10%-50%)
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
