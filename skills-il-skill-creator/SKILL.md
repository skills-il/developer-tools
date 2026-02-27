---
name: skills-il-skill-creator
description: >-
  Interactive workflow for creating new skills for the skills-il organization --
  guides through category selection, use case definition, folder scaffolding,
  YAML frontmatter generation with bilingual metadata, instruction writing, Hebrew
  companion creation, and validation. Use when user asks to "create a new skill",
  "scaffold a skill for skills-il", "write a SKILL.md", "contribute a skill",
  "new skill template", or "liztor skill chadash". Enforces skills-il conventions:
  kebab-case naming, Hebrew transliterations, bilingual display_name/display_description,
  progressive disclosure, and validate-skill.sh compliance. Do NOT use for editing
  existing skills, creating skills for non-skills-il platforms, or generic markdown
  file creation.
license: MIT
allowed-tools: 'Bash(python:*) Bash(./scripts/*) WebFetch'
compatibility: >-
  No network required for scaffolding. WebFetch optional for pulling latest
  conventions. Works with Claude Code, Claude.ai, Cursor.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    - skill-creator
    - scaffolding
    - template
    - developer
    - workflow
    - israel
  display_name:
    he: יוצר סקילים skills-il
    en: Skills-IL Skill Creator
  display_description:
    he: >-
      תהליך אינטראקטיבי ליצירת סקילים חדשים לארגון skills-il -- הנחיה לבחירת
      קטגוריה, הגדרת מקרי שימוש, יצירת תיקייה, כתיבת frontmatter דו-לשוני,
      הוראות, קובץ עברי נלווה ואימות. השתמש כשמשתמש מבקש "ליצור skill חדש",
      "תבנית skill", "לתרום skill" או "scaffold skill".
    en: >-
      Interactive workflow for creating new skills for the skills-il organization --
      guides through category selection, use case definition, folder scaffolding,
      YAML frontmatter generation with bilingual metadata, instruction writing, Hebrew
      companion creation, and validation. Use when user asks to "create a new skill",
      "scaffold a skill for skills-il", "write a SKILL.md", "contribute a skill",
      "new skill template", or "liztor skill chadash". Do NOT use for editing
      existing skills or creating skills for non-skills-il platforms.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Skills-IL Skill Creator

## Overview

This skill walks you through creating a production-quality skill for the skills-il organization. It follows Anthropic's Complete Guide to Building Skills and enforces all skills-il conventions.

Every skill you create will include: SKILL.md with validated frontmatter, bilingual metadata (Hebrew + English), step-by-step instructions with tables and code examples, a Hebrew companion file (SKILL_HE.md), and pass all validation checks.

## Instructions

### Step 1: Choose Category Repository

Ask the user which category repo this skill belongs to:

| Category | Repo | Focus Area |
|----------|------|------------|
| Tax & Finance | tax-and-finance | Invoicing, payroll, VAT, payments, pensions |
| Government | government-services | data.gov.il, Bituach Leumi, Rasham, transit |
| Security | security-compliance | Privacy law, cybersecurity, legal research |
| Localization | localization | RTL, Hebrew NLP, OCR, Shabbat scheduling |
| Dev Tools | developer-tools | ID validation, date conversion, phone formatting |
| Communication | communication | SMS, WhatsApp, Monday.com, job market |

If the skill doesn't fit any category, discuss with the user whether it belongs in an existing category or warrants a new repo.

### Step 2: Define Use Cases

CRITICAL: Before writing any code, identify 2-3 concrete use cases.

For each use case, capture:
- **Trigger**: What the user would say (in English AND Hebrew transliteration)
- **Steps**: What multi-step workflow this requires
- **Tools**: Which tools are needed (built-in or MCP)
- **Result**: What success looks like

Example format:
```
Use Case: Validate Israeli e-invoice
Trigger: User says "validate hashbonit electronit" or "check SHAAM allocation"
Steps:
1. Parse invoice fields
2. Validate allocation number format
3. Check against SHAAM rules
Result: Invoice validated with pass/fail report
```

Ask the user to describe their skill idea, then help them extract 2-3 use cases from it. Include Hebrew transliterations for all domain terms (e.g., "payroll" = "tlush maskoret", "invoice" = "hashbonit").

### Step 3: Scaffold the Folder

Run the scaffolding script to create the skill folder structure:

```bash
python scripts/scaffold-skill.py --name <skill-name> --category <category-repo>
```

The script creates:
```
<skill-name>/
├── SKILL.md          # Template with frontmatter skeleton
├── SKILL_HE.md       # Hebrew companion stub
├── scripts/          # For helper scripts
└── references/       # For reference documentation
```

Verify the output:
- Folder name is kebab-case
- No spaces, underscores, or capitals
- Name does not contain "claude" or "anthropic"
- No README.md inside the folder

### Step 4: Write the YAML Frontmatter

Generate the frontmatter following this exact structure:

```yaml
---
name: <skill-name>
description: >-
  [What it does -- one sentence]. Use when user asks to [triggers in English],
  "[Hebrew transliteration 1]", "[Hebrew transliteration 2]", or [more triggers].
  [Key capabilities]. Do NOT use for [anti-triggers] (use [alternative-skill] instead).
license: MIT
allowed-tools: '<tools if needed>'
compatibility: >-
  [Network/system requirements]. Works with Claude Code, Claude.ai, Cursor.
metadata:
  author: skills-il
  version: 1.0.0
  category: <category-repo>
  tags:
    - <tag1>
    - <tag2>
    - israel
  display_name:
    he: "<Hebrew display name>"
    en: <English Display Name>
  display_description:
    he: "<Hebrew description>"
    en: >-
      <English description -- mirrors the main description field>
---
```

**Description rules (CRITICAL):**
- Must follow pattern: `[What it does] + [When to use it] + [Key capabilities] + [Do NOT use for X]`
- Under 1024 characters total
- No XML angle brackets (< >) anywhere in frontmatter
- Include trigger phrases users would actually say
- Include Hebrew transliterations in quotes (e.g., "tlush maskoret")
- End with `Do NOT use for` boundary + cross-reference to related skills

**Allowed-tools patterns:**
- No tools needed: omit the field
- Python scripts: `'Bash(python:*)'`
- Python + web: `'Bash(python:*) WebFetch'`
- Multiple CLI tools: `'Bash(python:*) Bash(curl:*) WebFetch'`
- pip installs: `'Bash(python:*) Bash(pip:*)'`

### Step 5: Write the Instructions Body

Write the SKILL.md body using this structure:

```markdown
# <Skill Display Name>

## Instructions

### Step 1: <First Major Step>
<Clear explanation with tables, code examples>

### Step N: <Next Step>
...

## Examples

### Example 1: <Common Scenario>
User says: "<typical user request>"
Actions:
1. ...
Result: ...

## Bundled Resources

### Scripts
- `scripts/<name>.py` -- <What it does, how to run>. Run: `python scripts/<name>.py --help`

### References
- `references/<name>.md` -- <What it contains>. Consult when <specific situation>.

## Troubleshooting

### Error: "<Error name>"
Cause: <Why>
Solution: <Fix>
```

**Best practices from the Complete Guide:**
- Be specific and actionable: "Run `python scripts/validate.py --input {filename}`" not "Validate the data"
- Use tables for decision matrices, field mappings, comparison data
- Include inline code for algorithms and API calls
- Keep SKILL.md under 5,000 words -- move detailed docs to `references/`
- Reference bundled resources with "Consult when..." guidance
- Include 2-4 examples covering common and edge cases
- Include 2-4 troubleshooting entries for likely errors
- Embed Hebrew terminology inline: "installments (tashlumim)"

**Progressive disclosure:**
- SKILL.md = core instructions (what the agent needs most of the time)
- `references/` = detailed specs, full API docs, edge cases (loaded on demand)
- `scripts/` = executable helpers (run when needed)

### Step 6: Create the Hebrew Companion (SKILL_HE.md)

Create SKILL_HE.md with the same structure but in Hebrew:
- Translate the body instructions to Hebrew
- Keep code blocks, field names, and API references in English
- Use Hebrew-native terminology (not transliterations)
- Maintain the same step numbering and section structure

The Hebrew file uses the same frontmatter as SKILL.md (frontmatter stays in English).

### Step 7: Validate and Prepare for PR

Run the validation script:

```bash
./scripts/validate-skill.sh <skill-name>/SKILL.md
```

The script checks 9 rules:

| # | Rule | Common Fix |
|---|------|-----------|
| 1 | File is exactly `SKILL.md` | Rename if wrong case |
| 2 | Starts with `---` delimiter | Add YAML frontmatter |
| 3 | `name` is kebab-case, matches folder | Fix casing or rename folder |
| 4 | No "claude"/"anthropic" in name | Choose different name |
| 5 | `description` present, under 1024 chars, has trigger phrase, no `<>` | Shorten or add "Use when" |
| 6 | No `<>` in frontmatter | Remove XML angle brackets |
| 7 | Body under 5,000 words | Move content to references/ |
| 8 | No README.md in skill folder | Delete README.md |
| 9 | No hardcoded secrets | Remove API keys, tokens |

After validation passes, review against the quality checklist:
- [ ] Description includes WHAT and WHEN
- [ ] Instructions are specific and actionable
- [ ] Examples cover 2+ real scenarios
- [ ] Troubleshooting covers likely errors
- [ ] Hebrew companion exists and is consistent
- [ ] References are linked with "Consult when..." guidance
- [ ] No security issues (secrets, injection vectors)

## Examples

### Example 1: Create a Government Services Skill

User says: "I want to create a skill for querying Israeli court decisions"

Actions:
1. Category: government-services
2. Use cases: search by case number, search by judge name, search by topic (Hebrew legal terms)
3. Scaffold: `python scripts/scaffold-skill.py --name israeli-court-decisions --category government-services`
4. Frontmatter: name=israeli-court-decisions, triggers include "psakei din", "beit mishpat", "nevo"
5. Instructions: Steps for search types, result parsing, citation format
6. Hebrew: SKILL_HE.md with native legal terminology
7. Validate: `./scripts/validate-skill.sh israeli-court-decisions/SKILL.md`

Result: Complete skill ready for PR to government-services repo.

### Example 2: Create a Developer Tool Skill

User says: "I need a skill that helps format Israeli addresses"

Actions:
1. Category: developer-tools (or government-services for address lookup APIs)
2. Use cases: format for postal mail, validate mikud, normalize city names
3. Scaffold: `python scripts/scaffold-skill.py --name israeli-address-formatter --category developer-tools`
4. Frontmatter: triggers include "format ktovet", "mikud", "address normalization"
5. Instructions: Format rules, mikud lookup, bilingual city names
6. Hebrew: SKILL_HE.md
7. Validate: passes all checks

Result: Address formatting skill with validation and postal format support.

### Example 3: Create a Skill with MCP Integration

User says: "I want to create a skill that uses the israeli-bank-mcp server"

Actions:
1. Category: tax-and-finance
2. Use cases: categorize transactions, detect recurring charges, monthly summary
3. Scaffold: `python scripts/scaffold-skill.py --name israeli-bank-analyzer --category tax-and-finance`
4. Frontmatter: add `mcp-server: israeli-bank-mcp` to metadata, triggers include "nituch tenuot bank"
5. Instructions: MCP tool calls for fetching transactions, categorization logic, summary generation
6. Hebrew: SKILL_HE.md with banking terminology
7. Validate: passes all checks

Result: MCP-enhanced skill that adds workflow intelligence on top of bank data access.

## Bundled Resources

### Scripts
- `scripts/scaffold-skill.py` -- Creates the complete folder structure for a new skills-il skill: SKILL.md template with frontmatter skeleton, SKILL_HE.md stub, scripts/ and references/ directories. Validates name format and prevents overwrites. Run: `python scripts/scaffold-skill.py --help`

### References
- `references/skill-spec.md` -- Complete skills-il SKILL.md specification including all frontmatter fields (required and optional), description-writing formula with good/bad examples, the 5 skill patterns from Anthropic's guide, quality checklist, and validation rules. Consult when writing frontmatter or instructions and you need detailed guidance beyond the steps above.

## Troubleshooting

### Error: "Validation fails on description"
Cause: Description missing trigger phrase or over 1024 characters
Solution: Ensure description includes one of: "Use when", "Use for", "Use if", "When user", "When the user". Check length is under 1024 chars. Remove any `<>` angle brackets.

### Error: "Name doesn't match folder"
Cause: SKILL.md `name` field differs from the folder name
Solution: The `name` field must exactly match the folder name. Both must be kebab-case. Run: `ls -la` to check folder name, compare with `name:` in frontmatter.

### Error: "Body exceeds 5,000 words"
Cause: Too much detail in SKILL.md
Solution: Move detailed documentation to `references/` files. Keep SKILL.md focused on core instructions. Link to references with "Consult `references/filename.md` for..." guidance.

### Error: "Scaffold script fails"
Cause: Folder already exists or invalid name format
Solution: Check if the skill folder already exists. Ensure name is kebab-case only (lowercase letters, numbers, hyphens). No spaces, underscores, or capitals.
