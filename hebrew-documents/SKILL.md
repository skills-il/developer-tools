---
name: hebrew-documents
description: >-
  Generate RTL Hebrew Word documents (DOCX) with correct bidirectional text,
  Hebrew typography, and Israeli formatting standards. Use when user asks to
  create a Hebrew document, "mismach b'ivrit", build an Israeli contract
  template, generate Hebrew forms, or produce DOCX files for Israeli
  organizations. Handles section numbering, Hebrew date formatting, Israeli
  address layout, and mixed-direction content. Do NOT use for PDF generation or
  HTML documents.
license: MIT
allowed-tools: 'Bash(python:*) Edit Write Read'
compatibility: 'Requires python-docx (pip install python-docx). Works with Claude Code.'
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - מסמך
      - עברית
      - RTL
      - Word
      - טפסים
    en:
      - document
      - hebrew
      - rtl
      - word
      - forms
  display_name:
    he: מסמכים בעברית
    en: Hebrew Documents
  display_description:
    he: יצירת מסמכי Word בעברית עם תמיכה ב-RTL, טפסים ישראליים ותבניות מקצועיות
    en: >-
      Generate RTL Hebrew Word documents with correct bidirectional text,
      Hebrew typography, and Israeli document formatting standards.
---

# Hebrew Documents

## Instructions

### Step 1: Set Up the Python Environment

Install the required library:

```bash
pip install python-docx
```

Import the necessary modules:

```python
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
```

### Step 2: Configure the Document for RTL Hebrew

Set the default document direction to RTL and configure Hebrew fonts:

```python
def create_hebrew_document():
    """Create a new Word document configured for Hebrew RTL text."""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'David'
    font.size = Pt(12)

    # Set complex script font (for Hebrew characters)
    rPr = style.element.get_or_add_rPr()
    cs_font = OxmlElement('w:rFonts')
    cs_font.set(qn('w:cs'), 'David')
    rPr.append(cs_font)

    # Set document-level RTL
    sectPr = doc.sections[0]._sectPr
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')

    return doc
```

**Set paragraph direction to RTL:**

```python
def set_paragraph_rtl(paragraph):
    """Configure a paragraph for right-to-left text direction."""
    pPr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
```

### Step 3: Use Israeli Document Formatting Standards

**Page setup for Israeli A4 standard:**

```python
def setup_israeli_page(doc):
    """Configure page settings for Israeli A4 documents."""
    section = doc.sections[0]
    section.page_width = Cm(21.0)   # A4 width
    section.page_height = Cm(29.7)  # A4 height
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.0)
```

**Hebrew date formatting:**

```python
import datetime

HEBREW_MONTHS = [
    'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
    'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
]

def format_hebrew_date(date=None):
    """Format a date in Israeli style: day month_name year."""
    if date is None:
        date = datetime.date.today()
    month_name = HEBREW_MONTHS[date.month - 1]
    return f'{date.day} {month_name} {date.year}'
    # Example output: "15 ינואר 2025"

def format_hebrew_date_numeric(date=None):
    """Format a date in Israeli numeric style: DD/MM/YYYY."""
    if date is None:
        date = datetime.date.today()
    return date.strftime('%d/%m/%Y')
```

**Israeli address format:**

```python
def format_israeli_address(street, number, city, postal_code=None):
    """Format an address in Israeli convention (street+number, city, postal)."""
    address = f'{street} {number}, {city}'
    if postal_code:
        address += f', מיקוד {postal_code}'
    return address
    # Example: "רוטשילד 1, תל אביב, מיקוד 6688101"
```

### Step 4: Build Common Israeli Document Templates

**Formal letter template:**

```python
def create_formal_letter(doc, sender, recipient, subject, body_paragraphs):
    """Create a formal Hebrew letter following Israeli business conventions."""
    setup_israeli_page(doc)

    # Date (top-right in RTL)
    date_p = doc.add_paragraph(format_hebrew_date())
    set_paragraph_rtl(date_p)

    # Recipient
    to_p = doc.add_paragraph(f'לכבוד: {recipient}')
    set_paragraph_rtl(to_p)
    to_p.runs[0].bold = True

    # Subject line
    subject_p = doc.add_paragraph(f'הנדון: {subject}')
    set_paragraph_rtl(subject_p)
    subject_p.runs[0].bold = True
    subject_p.runs[0].underline = True

    # Salutation
    greeting = doc.add_paragraph('שלום רב,')
    set_paragraph_rtl(greeting)

    # Body
    for text in body_paragraphs:
        p = doc.add_paragraph(text)
        set_paragraph_rtl(p)

    # Closing
    closing = doc.add_paragraph('בכבוד רב,')
    set_paragraph_rtl(closing)

    signature = doc.add_paragraph(sender)
    set_paragraph_rtl(signature)
```

**Contract template with numbered sections:**

```python
def create_contract_template(doc, title, parties, sections):
    """Create a Hebrew contract with numbered sections."""
    setup_israeli_page(doc)

    # Title
    title_p = doc.add_heading(title, level=0)
    set_paragraph_rtl(title_p)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Parties section
    parties_p = doc.add_paragraph()
    set_paragraph_rtl(parties_p)
    run = parties_p.add_run('הצדדים להסכם:')
    run.bold = True

    for i, party in enumerate(parties, 1):
        p = doc.add_paragraph(f'{i}. {party}')
        set_paragraph_rtl(p)

    # Numbered sections
    for i, (section_title, section_body) in enumerate(sections, 1):
        heading = doc.add_heading(f'{i}. {section_title}', level=2)
        set_paragraph_rtl(heading)

        for clause in section_body:
            p = doc.add_paragraph(clause)
            set_paragraph_rtl(p)
```

### Step 5: Handle Tables in RTL Documents

```python
def create_rtl_table(doc, headers, rows):
    """Create an RTL table with Hebrew headers and data."""
    # Reverse column order for RTL display
    headers_rtl = list(reversed(headers))
    rows_rtl = [list(reversed(row)) for row in rows]

    table = doc.add_table(rows=1 + len(rows_rtl), cols=len(headers_rtl))
    table.style = 'Table Grid'

    # Set table direction to RTL
    tblPr = table._tbl.tblPr
    bidi = OxmlElement('w:bidiVisual')
    bidi.set(qn('w:val'), '1')
    tblPr.append(bidi)

    # Headers
    for j, header in enumerate(headers_rtl):
        cell = table.rows[0].cells[j]
        cell.text = header
        for p in cell.paragraphs:
            set_paragraph_rtl(p)
            for run in p.runs:
                run.bold = True

    # Data rows
    for i, row in enumerate(rows_rtl):
        for j, value in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(value)
            for p in cell.paragraphs:
                set_paragraph_rtl(p)
```

### Step 6: Israeli Government Form Conventions

When generating documents that follow Israeli government form standards:

**Tofes (Form) numbering:** Israeli government forms use a numbering system (e.g., Form 101 for employee tax declaration, Form 106 for annual tax summary). Reference the form number in the document header.

**Required fields in official documents:**
- Teudat Zehut number (9-digit ID): always formatted as XXX-XXXXXXX or 9 consecutive digits
- Full Hebrew name (shem prati + shem mishpacha)
- Date of birth in DD/MM/YYYY format
- Israeli address with postal code (mikud, 7 digits)
- Telephone number in 05X-XXXXXXX format

**Signatures and declarations:**
- Signature line: underscore line with "Chatima" (signature) label below
- Date line next to the signature
- "I declare that all details are correct" (Ani matzir/a ki kol ha-pratim nehonim) standard text

```python
def add_signature_block(doc, signer_name=''):
    """Add an Israeli-standard signature block."""
    # Date and signature on same line
    p = doc.add_paragraph()
    set_paragraph_rtl(p)

    p.add_run('תאריך: ________________    ')
    p.add_run('חתימה: ________________')

    if signer_name:
        name_p = doc.add_paragraph(f'שם: {signer_name}')
        set_paragraph_rtl(name_p)

    # Declaration
    decl = doc.add_paragraph(
        'אני מצהיר/ה בזאת כי כל הפרטים המפורטים לעיל הם נכונים ומדויקים.'
    )
    set_paragraph_rtl(decl)
    decl.runs[0].font.size = Pt(10)
```

### Step 7: Export and Verify

```python
def save_document(doc, filename='document.docx'):
    """Save the document with verification checklist."""
    doc.save(filename)
    print(f'Document saved: {filename}')
    print('Verification checklist:')
    print('  1. Open in Word or LibreOffice Writer')
    print('  2. Verify Hebrew text direction is right-to-left')
    print('  3. Check paragraph alignment (should be right-aligned)')
    print('  4. Confirm table column order matches RTL layout')
    print('  5. Verify dates are in DD/MM/YYYY format')
    print('  6. Check mixed Hebrew/English text renders correctly')
```

## Examples

### Example 1: Employment Contract
**Input**: "Create a Hebrew employment contract template"
**Output**: A DOCX file with RTL layout containing: contract title, parties section, employment terms (position, start date, salary in NIS, working hours per Israeli labor law), confidentiality clause, termination terms, and signature blocks for employer and employee. All dates in Israeli format, amounts in NIS.

### Example 2: Government-Style Form
**Input**: "Generate a Hebrew form similar to Tax Form 101"
**Output**: A DOCX with labeled fields for personal details (Teudat Zehut, name, address, date of birth), employer details, tax-related declarations, and signature/date block. RTL layout with proper field formatting.

### Example 3: Business Proposal
**Input**: "Create a Hebrew business proposal document for a consulting engagement"
**Output**: A multi-section DOCX with cover page, executive summary, scope of work, timeline, pricing table (in NIS), terms and conditions, and signature page. Professional David font, proper heading hierarchy.

## Troubleshooting

- **Issue**: Hebrew text appears left-aligned in the generated document
  **Solution**: Ensure `w:bidi` element with `val='1'` is set on each paragraph's properties. Also set `WD_ALIGN_PARAGRAPH.RIGHT` for explicit right alignment.

- **Issue**: Table columns are in wrong order (LTR instead of RTL)
  **Solution**: Add the `w:bidiVisual` element to the table properties. Also reverse the column order in your data arrays before populating the table.

- **Issue**: Font renders Latin characters for Hebrew text
  **Solution**: Set the complex script font (`w:rFonts` with `w:cs` attribute) in addition to the regular font. Hebrew uses the complex script font family in Word.

- **Issue**: Numbered lists count from left instead of right
  **Solution**: Apply RTL direction to the list paragraph. In python-docx, manually set the `w:bidi` property on each numbered paragraph.

- **Issue**: Mixed content (Hebrew + English + numbers) displays out of order
  **Solution**: The Unicode Bidirectional Algorithm handles most cases automatically. Ensure the base paragraph direction is RTL. For edge cases, use Unicode control characters: RLM (U+200F) and LRM (U+200E).
