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

## Examples

### Example 1: Create a Hebrew Sales Pitch Deck
User says: "Build a 10-slide pitch deck in Hebrew for investors"
Actions:
1. Set up RTL PowerPoint with Heebo/David fonts
2. Create slides: cover, problem, solution, market, product, traction, team, financials, ask, contact
3. Use NIS currency formatting, Israeli market data
4. Apply right-to-left bullet points and text alignment
Result: Professional Hebrew pitch deck with Israeli context

### Example 2: Generate Hebrew Training Presentation
User says: "Create a training presentation in Hebrew for new employees"
Actions:
1. Create RTL presentation with company branding placeholder
2. Structure: welcome, company overview, team structure, policies, tools, Q&A
3. Add speaker notes in Hebrew for each slide
4. Include agenda slide with Hebrew section headers
Result: Hebrew onboarding presentation with speaker notes

## Bundled Resources

### Scripts
- `scripts/pptx_rtl_fixer.py` -- Validates and fixes RTL alignment in PowerPoint files. Run: `python scripts/pptx_rtl_fixer.py --help`

### References
- `references/israeli-business-slides.md` -- Israeli business presentation conventions including common slide structures, Hebrew typography for slides, and cultural norms. Consult when building business or investor presentations for Israeli audiences.

## Troubleshooting

### Error: "Bullet points appear on the wrong side"
Cause: PowerPoint defaults to LTR bullet alignment
Solution: Set paragraph alignment to RIGHT and enable RTL paragraph direction. For `python-pptx`, set `paragraph.alignment = PP_ALIGN.RIGHT`.

### Error: "Charts display Hebrew labels incorrectly"
Cause: Chart text frames default to LTR
Solution: After creating chart data, iterate over all chart text frames and set their paragraph direction to RTL. Hebrew axis labels may need manual font assignment.
