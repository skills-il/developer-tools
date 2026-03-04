---
name: israeli-spreadsheets
description: >-
  Generate Excel spreadsheets with Israeli tax calculations, VAT, NIS
  formatting, and Hebrew-labeled financial templates. Use when user asks
  about Israeli tax spreadsheets, NIS-formatted Excel files, VAT calculations,
  salary slip templates, arnona estimators, or Israeli accounting worksheets.
  Covers 2025 tax brackets, Bituach Leumi rates, and openpyxl RTL configuration.
license: MIT
compatibility: >-
  Requires openpyxl for Excel generation. Works with Claude Code, Cursor,
  GitHub Copilot, Windsurf, OpenCode, Codex.
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
    he: "גיליונות ישראליים"
    en: "Israeli Spreadsheets"
  display_description:
    he: >-
      יצירת גיליונות Excel עם חישובי מס, מע"מ ועיצוב פיננסי ישראלי
    en: >-
      Generate Excel spreadsheets with Israeli tax calculations, VAT, NIS
      formatting, and Hebrew-labeled financial templates
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Israeli Spreadsheets

## Instructions

### Step 1: Set Up Python Environment

Install openpyxl:

```bash
pip install openpyxl
```

### Step 2: Israeli Financial Constants

- VAT rate: 17% (2025)
- Tax brackets 2025: 10% up to 84,120 NIS, 14% up to 120,720, 20% up to 193,800, 31% up to 269,280, 35% up to 560,280, 47% up to 721,560, 50% above
- Credit point value: 2,904 NIS/year, 2.25 points for residents
- Bituach Leumi: 0.4% (low) / 7% (high)
- Health tax: 3.1% (low) / 5% (high)

### Step 3: Tax Calculation Functions

Progressive (marginal) tax calculation with credit point deduction. Use Python Decimal for precision.

### Step 4: Formatted Workbooks

Set `ws.sheet_view.rightToLeft = True` for RTL sheets. NIS format: '#,##0.00 "₪"'

### Step 5: Templates

- **Invoice (Heshbonit Mas)**: Business/customer details, item table, subtotal, 17% VAT, total
- **Salary slip (Tlush Maskoret)**: Earnings, deductions (income tax, Bituach Leumi, health tax, pension, keren hishtalmut), net pay
- **Arnona estimator**: Rates by city (Tel Aviv 55.80, Jerusalem 40.50, Haifa 33.20, Beer Sheva 27.90, Netanya 43.10 per sqm/bi-monthly)
