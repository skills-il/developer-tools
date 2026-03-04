---
name: hebrew-presentations
description: >-
  Generate RTL Hebrew PowerPoint presentations with correct bidirectional text,
  Hebrew fonts, and Israeli business formatting conventions. Use when user asks
  about creating Hebrew PowerPoint slides, RTL presentations, Israeli pitch
  decks, startup investor presentations, or Hebrew slide formatting.
  Covers python-pptx RTL configuration, Hebrew font selection, bidirectional
  text handling, and Israeli business conventions.
license: MIT
compatibility: >-
  Requires python-pptx for presentation generation. Works with Claude Code,
  Cursor, GitHub Copilot, Windsurf, OpenCode, Codex.
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
    he: "מצגות בעברית"
    en: "Hebrew Presentations"
  display_description:
    he: >-
      יצירת מצגות PowerPoint בעברית עם תמיכה מלאה ב-RTL וגופנים עבריים
    en: >-
      Generate RTL Hebrew PowerPoint presentations with correct bidirectional
      text, Hebrew fonts, and Israeli business formatting conventions
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Hebrew Presentations

## Instructions

### Step 1: Set Up the Python Environment

Install python-pptx:

```bash
pip install python-pptx
```

### Step 2: Configure RTL at the Presentation Level

Every Hebrew presentation must have RTL direction set at both the slide and text-frame levels. python-pptx does not natively expose RTL properties, so manipulate the XML directly:

```python
def set_paragraph_rtl(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set('algn', 'r')
    pPr.set('rtl', '1')
```

### Step 3: Choose Hebrew Fonts

| Font | Best For | Style |
|------|----------|-------|
| Heebo | Tech/startup | Sans-serif |
| Rubik | Marketing | Rounded sans-serif |
| David | Government/formal | Serif |
| Frank Ruhl Libre | Academic | Serif |

Always set the complex script font (`a:cs`) for Hebrew characters.

### Step 4: Handle Bidirectional Text

Use separate runs for Hebrew and English text. Numbers render LTR automatically within RTL paragraphs.

### Step 5: Israeli Business Conventions

Investor pitch deck structure: Cover, Problem, Solution, Market Size (TAM/SAM/SOM), Business Model, Traction, Team, Competition, Financials, Ask.

Formatting: NIS currency symbol, DD/MM/YYYY dates, comma thousands separators.
