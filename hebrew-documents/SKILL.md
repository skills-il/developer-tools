---
name: hebrew-documents
description: >-
  Generate RTL Hebrew Word documents with correct bidirectional text, Hebrew
  typography, and Israeli document formatting standards. Use when user asks
  about creating Hebrew Word documents, RTL document formatting, Israeli
  government forms, formal Hebrew letters, or teudat zehut templates.
  Covers python-docx RTL configuration, Hebrew fonts, Israeli address and
  date formats, and government form conventions.
license: MIT
compatibility: >-
  Requires python-docx for document generation. Works with Claude Code,
  Cursor, GitHub Copilot, Windsurf, OpenCode, Codex.
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
    he: "מסמכים בעברית"
    en: "Hebrew Documents"
  display_description:
    he: >-
      יצירת מסמכי Word בעברית עם תמיכה ב-RTL, טפסים ישראליים ותבניות מקצועיות
    en: >-
      Generate RTL Hebrew Word documents with correct bidirectional text,
      Hebrew typography, and Israeli document formatting standards
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Hebrew Documents

## Instructions

### Step 1: Set Up Python Environment

Install python-docx:

```bash
pip install python-docx
```

### Step 2: Configure Document for RTL Hebrew

Set default document direction to RTL with Hebrew fonts (David, Heebo). Use the `w:bidi` XML element on paragraphs and `w:rFonts` with `w:cs` for complex script fonts.

### Step 3: Israeli Document Formatting

- Page setup: A4 (21x29.7cm), 2.5cm margins
- Dates: DD/MM/YYYY or Hebrew month names
- Addresses: street + number, city, mikud (7-digit postal code)
- Phone: 05X-XXX-XXXX format

### Step 4: Common Templates

**Formal letter**: Date, recipient (lekavod), subject (haniddon), greeting (shalom rav), body, closing (bekavod rav), signature.

**Contract**: Title (centered), parties section, numbered clauses, signature blocks.

### Step 5: RTL Tables

Add `w:bidiVisual` to table properties. Reverse column order in data arrays for correct RTL display.

### Step 6: Government Form Conventions

- Teudat Zehut: 9-digit format
- Standard declaration text
- Signature and date blocks
