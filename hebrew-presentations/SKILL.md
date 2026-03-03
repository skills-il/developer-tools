---
name: hebrew-presentations
description: >-
  Generate RTL Hebrew PowerPoint (PPTX) presentations with correct bidirectional
  text layout, Hebrew fonts, and Israeli business conventions. Use when user asks
  to create a Hebrew presentation, "matzget b'ivrit", investor pitch deck in
  Hebrew, build RTL slides, or generate PPTX files for Israeli audiences.
  Handles font embedding, mixed Hebrew-English content, and LTR number rendering
  within RTL paragraphs. Do NOT use for Google Slides or Keynote formats.
license: MIT
allowed-tools: 'Bash(python:*) Edit Write Read'
compatibility: 'Requires python-pptx (pip install python-pptx). Works with Claude Code.'
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - מצגת
      - עברית
      - RTL
      - PowerPoint
      - עסקים
    en:
      - presentation
      - hebrew
      - rtl
      - powerpoint
      - business
  display_name:
    he: מצגות בעברית
    en: Hebrew Presentations
  display_description:
    he: יצירת מצגות PowerPoint בעברית עם תמיכה מלאה ב-RTL וגופנים עבריים
    en: >-
      Generate RTL Hebrew PowerPoint presentations with correct bidirectional
      text, Hebrew fonts, and Israeli business formatting conventions.
---

# Hebrew Presentations

## Instructions

### Step 1: Set Up the Python Environment

Install the required library:

```bash
pip install python-pptx
```

Import the necessary modules in your Python script:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
import copy
```

### Step 2: Configure RTL at the Presentation Level

Every Hebrew presentation must have RTL direction set at both the slide and text-frame levels. python-pptx does not natively expose RTL properties, so you must manipulate the XML directly.

**Set paragraph direction to RTL:**

```python
def set_paragraph_rtl(paragraph):
    """Set a paragraph's text direction to right-to-left."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set('algn', 'r')  # Right-align text
    pPr.set('rtl', '1')   # Enable RTL direction
```

**Set text frame direction:**

```python
def set_textframe_rtl(text_frame):
    """Configure an entire text frame for RTL layout."""
    txBody = text_frame._txBody
    bodyPr = txBody.find(qn('a:bodyPr'))
    if bodyPr is None:
        bodyPr = txBody.makeelement(qn('a:bodyPr'), {})
        txBody.insert(0, bodyPr)
    bodyPr.set('rtlCol', '1')  # RTL column order
    # Set all paragraphs to RTL
    for paragraph in text_frame.paragraphs:
        set_paragraph_rtl(paragraph)
```

### Step 3: Choose Appropriate Hebrew Fonts

Use fonts that render Hebrew correctly and are commonly available:

| Font | Best For | Style | Notes |
|------|----------|-------|-------|
| Heebo | Modern tech/startup | Sans-serif | Google Font, excellent screen rendering |
| Rubik | Marketing/creative | Sans-serif, rounded | Google Font, friendly appearance |
| David | Government/formal | Serif | Pre-installed on Windows Hebrew editions |
| Frank Ruhl Libre | Academic/editorial | Serif | Google Font, elegant body text |
| Miriam | General purpose | Sans-serif | Pre-installed on Windows Hebrew editions |
| Assistant | UI/product design | Sans-serif | Google Font, clean and modern |

**Applying a Hebrew font:**

```python
def set_hebrew_font(run, font_name='Heebo', size_pt=18):
    """Apply a Hebrew font to a text run with proper fallback."""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    # Set complex script font (Hebrew falls under complex scripts in OOXML)
    rPr = run._r.get_or_add_rPr()
    cs_font = rPr.makeelement(qn('a:cs'), {})
    cs_font.set('typeface', font_name)
    rPr.append(cs_font)
```

The complex script font (`a:cs`) is critical. PowerPoint uses this font family for Hebrew, Arabic, and other complex script languages. Without it, Hebrew text may fall back to a default Latin font.

### Step 4: Handle Bidirectional (Bidi) Text

Hebrew presentations frequently mix Hebrew and English text, numbers, and special characters. Follow these rules:

**Numbers in Hebrew text:** Numbers are always rendered LTR, even within RTL paragraphs. PowerPoint handles this automatically if RTL is properly set at the paragraph level.

**Mixed Hebrew-English content:** When a paragraph contains both Hebrew and English:
1. Set the paragraph to RTL (the dominant direction)
2. Use separate runs for Hebrew and English text segments
3. Apply the appropriate font to each run

```python
def add_bidi_text(text_frame, hebrew_text, english_text=''):
    """Add mixed Hebrew/English text to a text frame."""
    set_textframe_rtl(text_frame)
    p = text_frame.paragraphs[0]
    set_paragraph_rtl(p)

    # Hebrew run
    run_he = p.add_run()
    run_he.text = hebrew_text
    set_hebrew_font(run_he, 'Heebo', 18)

    if english_text:
        # English run
        run_en = p.add_run()
        run_en.text = f' {english_text} '
        run_en.font.name = 'Inter'
        run_en.font.size = Pt(18)
```

### Step 5: Follow Israeli Business Presentation Conventions

**Investor pitch deck structure (Israeli VC standard):**
1. Cover slide: company name (Hebrew + English), logo, tagline
2. Problem: the pain point, Israeli market data
3. Solution: what you build, product screenshots
4. Market size: TAM/SAM/SOM with Israeli + global figures (use NIS and USD)
5. Business model: revenue streams, pricing in NIS
6. Traction: metrics, growth charts, Israeli customer logos
7. Team: founders with IDF/8200 background if relevant, academic credentials
8. Competition: competitive matrix
9. Financial projections: 3-5 year forecast in NIS, optionally USD
10. Ask: funding amount in NIS/USD, use of funds

**Formatting conventions for Israeli presentations:**
- Currency: use the shekel symbol before the number, e.g., 50,000 (with the NIS symbol)
- Dates: DD/MM/YYYY (Israeli standard), or Hebrew month names
- Phone numbers: format as 05X-XXX-XXXX or +972-5X-XXX-XXXX
- Percentages: number followed by % sign (rendered correctly in RTL)
- Large numbers: use comma as thousands separator (1,000,000)

### Step 6: Create Slide Layouts for Common Use Cases

**Title slide:**

```python
def create_title_slide(prs, title_he, subtitle_he):
    """Create an RTL Hebrew title slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[0])

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title_he
    set_textframe_rtl(title_shape.text_frame)
    for run in title_shape.text_frame.paragraphs[0].runs:
        set_hebrew_font(run, 'Heebo', 36)

    # Subtitle
    subtitle_shape = slide.placeholders[1]
    subtitle_shape.text = subtitle_he
    set_textframe_rtl(subtitle_shape.text_frame)
    for run in subtitle_shape.text_frame.paragraphs[0].runs:
        set_hebrew_font(run, 'Heebo', 20)

    return slide
```

**Bullet list slide:**

```python
def create_bullet_slide(prs, title_he, bullets_he):
    """Create a slide with RTL Hebrew bullet points."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title_he
    set_textframe_rtl(title_shape.text_frame)

    # Bullets
    body = slide.placeholders[1]
    tf = body.text_frame
    tf.clear()
    set_textframe_rtl(tf)

    for i, bullet in enumerate(bullets_he):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = bullet
        set_paragraph_rtl(p)
        set_hebrew_font(p.runs[0], 'Heebo', 18)
        p.level = 0

    return slide
```

### Step 7: Export and Verify

```python
def save_presentation(prs, filename='presentation.pptx'):
    """Save the presentation and provide verification instructions."""
    prs.save(filename)
    print(f'Presentation saved: {filename}')
    print('Verification checklist:')
    print('  1. Open in PowerPoint or LibreOffice Impress')
    print('  2. Check that Hebrew text reads right-to-left')
    print('  3. Verify bullet points align to the right')
    print('  4. Confirm numbers within Hebrew text display correctly')
    print('  5. Test mixed Hebrew/English paragraphs')
```

## Examples

### Example 1: Startup Pitch Deck
**Input**: "Create a Hebrew investor pitch deck for a fintech startup"
**Output**: A 10-slide PPTX with RTL Hebrew layout covering all standard Israeli VC pitch sections: cover, problem, solution, market, business model, traction, team, competition, financials, and ask. All text in Heebo font, numbers in NIS format, dates in DD/MM/YYYY.

### Example 2: Corporate Report
**Input**: "Build a quarterly report presentation in Hebrew with charts"
**Output**: A multi-slide PPTX with Hebrew titles, RTL bullet summaries, and placeholder chart descriptions. Financial figures formatted with shekel symbol and thousands separators.

### Example 3: Educational Slides
**Input**: "Create Hebrew training slides about cybersecurity basics"
**Output**: A slide deck with Hebrew headings, RTL-aligned content, bullet points with technical terms (mixed Hebrew/English where needed), and step-by-step instructions.

## Troubleshooting

- **Issue**: Hebrew text appears reversed or garbled in the PPTX file
  **Solution**: Ensure both `rtl='1'` on the paragraph and `rtlCol='1'` on the bodyPr are set. Both are required for correct rendering.

- **Issue**: Numbers display in wrong order within Hebrew sentences
  **Solution**: Numbers are naturally LTR. If they appear wrong, verify the paragraph RTL flag is set correctly. Do not reverse number strings manually.

- **Issue**: Fonts fall back to Times New Roman or Arial for Hebrew characters
  **Solution**: Set the complex script font using the `a:cs` element. Without it, PowerPoint uses the Latin font family, which may not support Hebrew glyphs.

- **Issue**: Bullet points align to the left instead of right
  **Solution**: Set both paragraph alignment to right (`algn='r'`) and RTL direction (`rtl='1'`). Also check that the text frame has `rtlCol='1'` on its bodyPr.

- **Issue**: Mixed Hebrew/English text wraps incorrectly
  **Solution**: Use separate runs for Hebrew and English text segments within the same paragraph. Apply the appropriate font to each run independently.
