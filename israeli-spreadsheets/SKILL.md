---
name: israeli-spreadsheets
description: >-
  Generate Excel (XLSX) spreadsheets with Israeli financial data, tax
  calculations, and Hebrew formatting. Use when user asks to create an Israeli
  tax spreadsheet, "gliyon nitunim", VAT calculator, arnona estimator, salary
  slip template, or any Excel file with Israeli financial conventions. Handles
  NIS currency formatting, Israeli tax brackets, VAT calculations at 17%, Bank
  of Israel interest rates, and RTL Hebrew column headers. Do NOT use for Google
  Sheets or CSV files.
license: MIT
allowed-tools: 'Bash(python:*) Edit Write Read'
compatibility: 'Requires openpyxl (pip install openpyxl). Works with Claude Code.'
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
      Generate Excel spreadsheets with Israeli tax calculations, VAT,
      NIS formatting, and Hebrew-labeled financial templates.
---

# Israeli Spreadsheets

## Instructions

### Step 1: Set Up the Python Environment

Install the required library:

```bash
pip install openpyxl
```

Import the necessary modules:

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, numbers
from openpyxl.utils import get_column_letter
from decimal import Decimal, ROUND_HALF_UP
```

### Step 2: Configure Israeli Financial Constants

Always use the current official rates. These values should be verified before use:

```python
# Israeli VAT rate (as of 2025)
VAT_RATE = Decimal('0.17')  # 17%

# Israeli income tax brackets for 2025 (annual, in NIS)
# Based on Israel Tax Authority published brackets
TAX_BRACKETS_2025 = [
    (Decimal('84120'),   Decimal('0.10')),   # Up to 84,120 NIS: 10%
    (Decimal('120720'),  Decimal('0.14')),   # 84,121 - 120,720: 14%
    (Decimal('193800'),  Decimal('0.20')),   # 120,721 - 193,800: 20%
    (Decimal('269280'),  Decimal('0.31')),   # 193,801 - 269,280: 31%
    (Decimal('560280'),  Decimal('0.35')),   # 269,281 - 560,280: 35%
    (Decimal('721560'),  Decimal('0.47')),   # 560,281 - 721,560: 47%
    (None,               Decimal('0.50')),   # Over 721,560: 50%
]

# National Insurance (Bituach Leumi) rates for employees (2025)
BITUACH_LEUMI_RATE_LOW = Decimal('0.004')   # Up to 60% of average wage
BITUACH_LEUMI_RATE_HIGH = Decimal('0.07')   # Above 60% of average wage
HEALTH_TAX_RATE_LOW = Decimal('0.031')      # Up to 60% of average wage
HEALTH_TAX_RATE_HIGH = Decimal('0.05')      # Above 60% of average wage

# Credit points (nekudat zikui) value for 2025
CREDIT_POINT_VALUE = Decimal('2904')  # Monthly: 242 NIS
CREDIT_POINTS_RESIDENT = Decimal('2.25')  # Israeli resident base

# NIS number formatting
NIS_FORMAT = '#,##0.00 "₪"'
NIS_FORMAT_NO_DECIMAL = '#,##0 "₪"'
PERCENT_FORMAT = '0.00%'
```

### Step 3: Implement Israeli Tax Calculation Functions

**Income tax calculation:**

```python
def calculate_income_tax(annual_income):
    """Calculate Israeli income tax for a given annual income."""
    income = Decimal(str(annual_income))
    tax = Decimal('0')
    previous_bracket = Decimal('0')

    for bracket_limit, rate in TAX_BRACKETS_2025:
        if bracket_limit is None:
            # Top bracket, no limit
            taxable = income - previous_bracket
            tax += taxable * rate
            break
        elif income <= bracket_limit:
            taxable = income - previous_bracket
            tax += taxable * rate
            break
        else:
            taxable = bracket_limit - previous_bracket
            tax += taxable * rate
            previous_bracket = bracket_limit

    # Apply credit points (resident)
    annual_credit = CREDIT_POINT_VALUE * CREDIT_POINTS_RESIDENT
    tax = max(Decimal('0'), tax - annual_credit)

    return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

**VAT calculations:**

```python
def add_vat(amount):
    """Add 17% VAT to an amount."""
    amount = Decimal(str(amount))
    return (amount * (1 + VAT_RATE)).quantize(Decimal('0.01'))

def extract_vat(total_with_vat):
    """Extract VAT from a VAT-inclusive amount."""
    total = Decimal(str(total_with_vat))
    before_vat = (total / (1 + VAT_RATE)).quantize(Decimal('0.01'))
    vat_amount = total - before_vat
    return before_vat, vat_amount

def vat_amount(before_vat):
    """Calculate the VAT amount on a pre-VAT amount."""
    amount = Decimal(str(before_vat))
    return (amount * VAT_RATE).quantize(Decimal('0.01'))
```

### Step 4: Create Formatted Excel Workbooks

**Hebrew-styled workbook setup:**

```python
def create_israeli_workbook(title='Sheet1'):
    """Create an Excel workbook with Israeli formatting defaults."""
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.sheet_view.rightToLeft = True  # RTL sheet direction

    return wb, ws

def style_header_row(ws, row=1, num_cols=5):
    """Style the header row with Hebrew-appropriate formatting."""
    header_font = Font(name='Heebo', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79',
                              fill_type='solid')
    header_align = Alignment(horizontal='right', vertical='center',
                             wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
```

### Step 5: Build Common Israeli Financial Templates

**Invoice template (Heshbonit Mas):**

```python
def create_invoice_template(wb, ws):
    """Create an Israeli tax invoice (Heshbonit Mas) template."""
    # Header
    ws.merge_cells('A1:F1')
    ws['A1'] = 'חשבונית מס'
    ws['A1'].font = Font(name='Heebo', size=18, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    # Business details
    ws['A3'] = 'שם העסק:'
    ws['A4'] = 'ח.פ./ע.מ.:'
    ws['A5'] = 'כתובת:'
    ws['A6'] = 'טלפון:'

    # Invoice details
    ws['D3'] = 'מספר חשבונית:'
    ws['D4'] = 'תאריך:'
    ws['D5'] = 'תנאי תשלום:'

    # Customer details
    ws['A8'] = 'לכבוד:'
    ws['A9'] = 'ח.פ./ע.מ.:'
    ws['A10'] = 'כתובת:'

    # Items table
    headers = ['סה"כ', 'מחיר יחידה', 'כמות', 'תיאור', 'מס"ד']
    row = 12
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = Font(name='Heebo', size=11, bold=True)

    # Totals section
    ws.cell(row=22, column=4, value='סכום לפני מע"מ:')
    ws.cell(row=23, column=4, value='מע"מ (17%):')
    ws.cell(row=24, column=4, value='סה"כ לתשלום:')

    # Format currency cells
    for r in range(22, 25):
        ws.cell(row=r, column=5).number_format = NIS_FORMAT

    # Set column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 8

    # Set RTL
    for row_cells in ws.iter_rows(min_row=1, max_row=25):
        for cell in row_cells:
            cell.alignment = Alignment(horizontal='right')
```

**Salary slip (Tlush Maskoret):**

```python
def create_salary_slip(wb, ws, employee_data):
    """Create an Israeli salary slip template."""
    ws.merge_cells('A1:F1')
    ws['A1'] = 'תלוש משכורת'
    ws['A1'].font = Font(name='Heebo', size=16, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    # Employee details
    details = [
        ('שם העובד/ת:', employee_data.get('name', '')),
        ('ת.ז.:', employee_data.get('id', '')),
        ('חודש שכר:', employee_data.get('month', '')),
        ('תאריך תחילת עבודה:', employee_data.get('start_date', '')),
    ]

    for i, (label, value) in enumerate(details, 3):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        ws.cell(row=i, column=2, value=value)

    # Earnings section
    row = 8
    ws.cell(row=row, column=1, value='תשלומים').font = Font(bold=True, size=12)
    earnings = [
        ('שכר בסיס', 'base_salary'),
        ('שעות נוספות', 'overtime'),
        ('בונוס', 'bonus'),
        ('החזר הוצאות', 'expenses'),
    ]
    for i, (label, key) in enumerate(earnings, row + 1):
        ws.cell(row=i, column=1, value=label)
        val = employee_data.get(key, 0)
        cell = ws.cell(row=i, column=2, value=float(val))
        cell.number_format = NIS_FORMAT

    # Deductions section
    row = 14
    ws.cell(row=row, column=1, value='ניכויים').font = Font(bold=True, size=12)
    deductions = [
        ('מס הכנסה', 'income_tax'),
        ('ביטוח לאומי', 'bituach_leumi'),
        ('מס בריאות', 'health_tax'),
        ('קרן פנסיה (עובד)', 'pension_employee'),
        ('קרן השתלמות (עובד)', 'hishtalmut_employee'),
    ]
    for i, (label, key) in enumerate(deductions, row + 1):
        ws.cell(row=i, column=1, value=label)
        val = employee_data.get(key, 0)
        cell = ws.cell(row=i, column=2, value=float(val))
        cell.number_format = NIS_FORMAT

    # Net salary
    row = 21
    ws.cell(row=row, column=1, value='שכר נטו').font = Font(bold=True, size=13)
    net_cell = ws.cell(row=row, column=2)
    net_cell.number_format = NIS_FORMAT
    net_cell.font = Font(bold=True, size=13)
```

**Arnona (municipal tax) estimator:**

```python
# Arnona rates vary by city and property type
# These are approximate residential rates per square meter per 2 months
ARNONA_RATES_2025 = {
    'tel-aviv': {
        'residential': Decimal('55.80'),
        'commercial': Decimal('198.00'),
    },
    'jerusalem': {
        'residential': Decimal('40.50'),
        'commercial': Decimal('155.00'),
    },
    'haifa': {
        'residential': Decimal('33.20'),
        'commercial': Decimal('128.00'),
    },
    'beer-sheva': {
        'residential': Decimal('27.90'),
        'commercial': Decimal('95.00'),
    },
    'netanya': {
        'residential': Decimal('43.10'),
        'commercial': Decimal('165.00'),
    },
}

def estimate_arnona(city, property_type, sqm):
    """Estimate bi-monthly arnona payment."""
    city_key = city.lower().replace(' ', '-')
    if city_key not in ARNONA_RATES_2025:
        raise ValueError(f'City not found: {city}. Available: {list(ARNONA_RATES_2025.keys())}')

    rate = ARNONA_RATES_2025[city_key][property_type]
    bimonthly = (rate * Decimal(str(sqm))).quantize(Decimal('0.01'))
    annual = bimonthly * 6  # 6 bi-monthly periods per year

    return {
        'bimonthly': bimonthly,
        'annual': annual,
        'rate_per_sqm': rate,
    }
```

### Step 6: Apply NIS Number Formatting

```python
def format_nis_cell(cell, include_decimals=True):
    """Apply NIS (shekel) formatting to a cell."""
    if include_decimals:
        cell.number_format = NIS_FORMAT
    else:
        cell.number_format = NIS_FORMAT_NO_DECIMAL

def format_percent_cell(cell):
    """Apply percentage formatting to a cell."""
    cell.number_format = PERCENT_FORMAT

def add_nis_summary_row(ws, row, label_col, value_col, label, formula):
    """Add a formatted summary row with NIS total."""
    ws.cell(row=row, column=label_col, value=label).font = Font(bold=True)
    total_cell = ws.cell(row=row, column=value_col)
    total_cell.value = formula
    total_cell.number_format = NIS_FORMAT
    total_cell.font = Font(bold=True)
```

### Step 7: Export and Verify

```python
def save_workbook(wb, filename='spreadsheet.xlsx'):
    """Save the workbook with verification instructions."""
    wb.save(filename)
    print(f'Workbook saved: {filename}')
    print('Verification checklist:')
    print('  1. Open in Excel or LibreOffice Calc')
    print('  2. Verify sheet direction is right-to-left')
    print('  3. Check NIS currency formatting displays correctly')
    print('  4. Verify tax calculations match expected results')
    print('  5. Confirm formulas reference correct cells')
    print('  6. Test with sample data for edge cases')
```

## Examples

### Example 1: VAT Invoice
**Input**: "Create an Israeli tax invoice (heshbonit mas) in Excel"
**Output**: An XLSX file with RTL layout, business and customer detail sections, itemized product/service table, subtotal, 17% VAT calculation, and grand total. All amounts in NIS format. Column headers in Hebrew.

### Example 2: Annual Tax Estimator
**Input**: "Build a spreadsheet to estimate my Israeli income tax for 2025"
**Output**: An XLSX with input cells for annual income, tax bracket breakdown table showing the 2025 rates (10%, 14%, 20%, 31%, 35%, 47%, 50%), calculated tax per bracket, credit point deductions, Bituach Leumi, health tax, and final net income. All with Hebrew labels.

### Example 3: Salary Calculator
**Input**: "Create a salary slip template in Hebrew with all Israeli deductions"
**Output**: An XLSX salary slip with earnings section (base salary, overtime, bonus), deductions section (income tax, Bituach Leumi, health tax, pension, keren hishtalmut), employer contributions, and net pay calculation. Formatted with Hebrew labels and NIS amounts.

### Example 4: Arnona Estimator
**Input**: "Build an arnona calculator for different Israeli cities"
**Output**: An XLSX with a city selection dropdown, property size input, rate tables for major cities (Tel Aviv, Jerusalem, Haifa, Beer Sheva, Netanya), bi-monthly and annual payment calculations.

## Troubleshooting

- **Issue**: Sheet displays left-to-right instead of right-to-left
  **Solution**: Set `ws.sheet_view.rightToLeft = True` on the worksheet. This controls the visual direction of columns and scrolling.

- **Issue**: NIS symbol not displaying correctly
  **Solution**: Use the Unicode shekel sign in the format string. Ensure the font supports the shekel symbol. Try the format `'#,##0.00 "₪"'` with the actual Unicode character.

- **Issue**: Tax bracket calculations show wrong results
  **Solution**: Verify that tax brackets are applied progressively (marginal rates, not flat). Each bracket only applies to the portion of income within that bracket's range.

- **Issue**: Decimal precision errors in financial calculations
  **Solution**: Use Python's `Decimal` type instead of `float` for all monetary calculations. Set rounding to `ROUND_HALF_UP` to match Israeli accounting standards.

- **Issue**: Hebrew column headers display garbled text
  **Solution**: openpyxl handles Unicode natively. Ensure your Python file is saved as UTF-8. If headers still appear wrong, explicitly set the font to one that supports Hebrew (e.g., Heebo, David).
