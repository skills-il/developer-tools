---
name: israeli-spreadsheets
description: >-
  Generate Excel spreadsheets with Israeli tax calculations, VAT, NIS formatting,
  and Hebrew-labeled financial templates. Use when user asks about Israeli tax spreadsheets,
  NIS-formatted Excel files, VAT calculations, salary slip templates, arnona estimators,
  or Israeli accounting worksheets. Covers 2025 tax brackets, Bituach Leumi rates,
  and openpyxl RTL configuration.
license: MIT
compatibility: >-
  Requires openpyxl for Excel generation. Works with Claude Code, Cursor, GitHub Copilot,
  Windsurf, OpenCode, Codex.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
    - אקסל
    - מס
    - מע"מ
    - שקלים
    - חשבונאות
    en:
    - excel
    - tax
    - vat
    - shekel
    - accounting
  display_name:
    he: גיליונות ישראליים
    en: Israeli Spreadsheets
  display_description:
    he: יצירת גיליונות Excel עם חישובי מס, מע"מ ועיצוב פיננסי ישראלי
    en: >-
      Generate Excel spreadsheets with Israeli tax calculations, VAT, NIS formatting,
      and Hebrew-labeled financial templates. Use when user asks about Israeli tax
      spreadsheets, NIS-formatted Excel files, VAT calculations, salary slip templates,
      arnona estimators, or Israeli accounting worksheets. Covers 2025 tax brackets,
      Bituach Leumi rates, and openpyxl RTL configuration.
  supported_agents:
  - claude-code
  - cursor
  - github-copilot
  - windsurf
  - opencode
  - codex
  - antigravity
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

- **Invoice (Heshbonit Mas)**: Business/customer details, item table, subtotal, 18% VAT, total
- **Salary slip (Tlush Maskoret)**: Earnings, deductions (income tax, Bituach Leumi, health tax, pension, keren hishtalmut), net pay
- **Arnona estimator**: Rates by city (Tel Aviv 55.80, Jerusalem 40.50, Haifa 33.20, Beer Sheva 27.90, Netanya 43.10 per sqm/bi-monthly)

## Examples

### Example 1: Create an Israeli Payroll Calculator
User says: "Build a payroll Excel sheet for an Israeli employee"
Actions:
1. Create RTL workbook with Hebrew headers
2. Add income tax brackets (2024 rates: 10%-50%)
3. Calculate Bituach Leumi (3.5%/12% thresholds), health tax (3.1%/5%)
4. Include pension (6.5% employee + 6.5% employer) and keren hishtalmut
5. Format all amounts as NIS with Hebrew labels
Result: Complete Israeli payroll calculator with net salary computation

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
- `scripts/shekel_formatter.py` -- Formats Excel cells with Israeli currency, date, and number conventions. Run: `python scripts/shekel_formatter.py --help`

### References
- `references/israeli-tax-rates.md` -- Current Israeli tax brackets, Bituach Leumi rates, VAT rate, pension requirements, and common financial constants. Consult when building any financial calculations for Israeli context.

## Troubleshooting

### Error: "NIS symbol appears on wrong side of number"
Cause: Excel locale not set for Hebrew/Israel
Solution: Use format string `#,##0.00 ₪` (symbol after number) for Israeli convention, or set the workbook locale to he-IL.

### Error: "Hebrew column headers display as question marks"
Cause: Workbook not saved with UTF-8 encoding or font doesn't support Hebrew
Solution: Ensure the workbook uses a Unicode-compatible font (like David, Heebo, or Arial). When using openpyxl, Hebrew strings are automatically UTF-8 encoded.
