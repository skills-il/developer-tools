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
  version: 1.2.0
  category: developer-tools
  tags:
    he:
      - יוצר-סקילים
      - פיגומים
      - תבנית
      - מפתחים
      - תהליך-עבודה
      - ישראל
    en:
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
    - openclaw
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
| Food & Dining | food-and-dining | Restaurants, recipes, kashrut, delivery |
| Legal Tech | legal-tech | Contracts, legal research, compliance |
| Marketing & Growth | marketing-growth | SEO, social media, ads, email campaigns, ASO |
| Education | education | Learning platforms, tutoring, academic tools |
| Health Services | health-services | HMOs, pharmacy, medical records, appointments |

If the skill doesn't fit any category, discuss with the user whether it belongs in an existing category or warrants a new repo.

### Step 2: Collect Creator Information (MUST ASK)

Before proceeding, you MUST ask the user for their creator details. These are required for submitting the skill to the Skills IL directory.

Ask the user:

> "What is your name? This will be displayed as the skill creator on the Skills IL directory. Your GitHub username is fine too."

Wait for the user's response and store their answer as `creator_name`.

Then ask:

> "What is your email address? This is required so we can notify you when your skill is published, featured, or if we need to contact you about updates. It will not be displayed publicly."

Wait for the user's response and store their answer as `creator_email`.

**Rules:**
- `creator_name` is required. Default to the GitHub username if the user prefers not to provide their full name.
- `creator_email` is **required** and must be a valid email address. Do NOT proceed without it.
- Store both values -- they will be used in the `metadata.author` field and when submitting to the directory.
- If the user declines to provide an email, explain that it is mandatory for the submission process and they will not receive notifications about their skill without it.

### Step 3: Define Use Cases

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

### Step 4: Fact-Check Domain Information

Before writing any content, verify the key facts your skill will reference. This is especially important for skills dealing with Israeli laws, regulations, government services, financial rules, or healthcare policies, as these change frequently.

**What to verify:**
- Legal thresholds and limits (e.g., small claims court limit, tax brackets, age limits)
- Government processes and forms (e.g., filing procedures, required documents)
- Institutional names and contact details (e.g., phone numbers, websites, addresses)
- Pricing and fees (e.g., copayments, filing fees, service costs)
- Recent law changes that may have taken effect this year

**How to verify:**
- Search official Israeli government sources (gov.il, Knesset, Bituach Leumi)
- Check current-year dates in your searches (laws and thresholds change annually)
- Cross-reference at least 2 sources for critical facts like monetary limits or legal requirements
- Note the verification date so the skill can be updated when facts change

**What to record:**
For each key fact, note: the fact, the source, and the date verified. Include these as inline references in your SKILL.md instructions (e.g., "NIS 38,900 as of January 2025").

Do NOT skip this step. A skill with outdated or incorrect facts (wrong tax rate, expired law, wrong phone number) is worse than no skill at all.

### Step 5: Scaffold the Folder

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

### Step 6: Write the YAML Frontmatter

Generate the frontmatter following this exact structure. Use the `creator_name` collected in Step 2 for the `author` field:

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
  author: <creator_name from Step 2>
  version: 1.0.0
  category: <category-repo>
  tags:
    he:
      - <tag1-he>
      - <tag2-he>
      - ישראל
    en:
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
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
    # - openclaw          # Only add if skill is verified as OpenClaw-compatible
---
```

**Supported agents:** Include all standard agents (claude-code through codex) by default. If the skill relies on agent-specific features (e.g., MCP tools only available in Claude Code), remove agents that cannot support it and document why in the `compatibility` field.

**OpenClaw compatibility (MUST ASK):** Before finalizing the frontmatter, ask the user:

> "Is this skill compatible with OpenClaw? OpenClaw is an open-source AI coding agent. Only mark as compatible if the skill does not depend on Claude-specific features (e.g., Claude MCP tools, Anthropic-specific APIs). Should I add `openclaw` to supported_agents?"

- If the user confirms **yes**: uncomment `openclaw` in the `supported_agents` list
- If the user says **no** or is unsure: leave it commented out
- Do NOT assume compatibility -- always ask explicitly

**Bilingual tags (MUST ASK):** After defining the English tags, ask the user:

> "Please provide Hebrew translations for each tag. Tags must have matching `he` and `en` arrays (same length). For example, if your English tags are `[invoicing, tax, israel]`, the Hebrew tags should be `[invoices, taxes, israel]`. What are the Hebrew equivalents for your tags?"

- Both `he` and `en` arrays are **required** -- no tag may be left untranslated
- Arrays must be the **same length** (each English tag has exactly one Hebrew counterpart)
- No empty strings allowed in either array
- Technical terms that have no Hebrew equivalent can stay in English in both arrays (e.g., `API`, `MCP`)

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

### Step 7: Write the Instructions Body

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

### Step 8: Create References and Scripts

Every skill should include reference files and helper scripts. These are not optional extras; they make the difference between a thin skill and a production-quality one.

**References (`references/` directory):**

Create 2-3 reference files that contain detailed information too long for SKILL.md. Common patterns:

| Pattern | Example | When to use |
|---------|---------|-------------|
| Directory/listing | `hospital-directory.md`, `crisis-hotlines-directory.md` | Skill covers a domain with many institutions, services, or contacts |
| Detailed guide | `fair-rental-law-summary.md`, `ivf-process-detailed.md` | A process or law needs more detail than fits in instructions |
| Glossary | `hebrew-rental-glossary.md` | Skill uses domain-specific Hebrew terminology (50+ terms) |
| Checklist | `contract-checklist.md`, `evidence-guide.md` | Users need a step-by-step verification or preparation list |
| Comparison table | `universities-comparison.md`, `city-rental-guide.md` | Users need to compare options across multiple dimensions |
| Template | `demand-letter-template.md` | Users need a starting point for a document or form |

Each reference file should:
- Be under 3,000 words
- Use markdown with clear headers and tables
- Include Hebrew terms in parentheses
- Be linked from SKILL.md with "Consult when..." guidance

**Scripts (`scripts/` directory):**

Create 1-2 Python helper scripts for calculations or data lookups. Common patterns:

| Pattern | Example | When to use |
|---------|---------|-------------|
| Calculator | `sekher-calculator.py`, `filing-fee-calculator.py` | Skill involves formulas, tax calculations, or fee estimation |
| Coverage checker | `fertility-coverage-checker.py` | Skill involves eligibility rules based on multiple criteria |
| Cost estimator | `therapy-cost-estimator.py`, `rental-budget-calculator.py` | Users need to compare costs across options |
| Index/adjustment | `rent-index-calculator.py` | Skill involves CPI-linked values or time-based adjustments |

Each script should:
- Use `#!/usr/bin/env python3` shebang
- Include argparse with `--help`
- Have a clear docstring explaining usage
- Use stdlib only (no external dependencies)
- Include input validation with clear error messages
- Print results in clean, formatted output

**Update SKILL.md:** Add a `## Bundled Resources` section (before `## Troubleshooting`) listing all references and scripts with "Consult when..." guidance.

**Update SKILL_HE.md:** Add a matching `## משאבים מצורפים` section with Hebrew descriptions.

### Step 9: Create the Hebrew Companion (SKILL_HE.md)

Create SKILL_HE.md with the same structure but in Hebrew:
- Translate the body instructions to Hebrew
- Keep code blocks, field names, and API references in English
- Use Hebrew-native terminology (not transliterations)
- Maintain the same step numbering and section structure

The Hebrew file uses the same frontmatter as SKILL.md (frontmatter stays in English).

### Step 10: Validate and Prepare for Submission

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
- [ ] Domain facts verified against official sources (Step 4)
- [ ] Description includes WHAT and WHEN
- [ ] Instructions are specific and actionable
- [ ] Examples cover 2+ real scenarios
- [ ] Troubleshooting covers likely errors
- [ ] Hebrew companion exists and section structure matches SKILL.md 1:1
- [ ] At least 2 reference files in `references/` with "Consult when..." guidance
- [ ] At least 1 helper script in `scripts/` with argparse and `--help`
- [ ] No security issues (secrets, injection vectors)
- [ ] `supported_agents` list is accurate (all compatible agents included)
- [ ] `metadata.tags` has both `he` and `en` arrays of equal length with no empty strings
- [ ] `creator_name` and `creator_email` collected from user (Step 2)

### Step 11: Submit or Deploy

After validation passes, the next step depends on your role:

**For community contributors (most users):**

Submit your skill through the website at https://agentskills.co.il/en/submit (Hebrew: /he/submit).

1. Choose submission type: "Existing Repository" (if you pushed your skill to a GitHub repo) or "Proposal" (if you want the skills-il team to create the repo)
2. Fill in the form with: your GitHub repo URL, creator name, and creator email (from Step 2)
3. The skills-il team will review your submission, run security analysis, and publish it if it passes

**For skills-il org admins:**

Deploy directly to the category repo and database:

1. Clone the category repo: `gh repo clone skills-il/<category-repo>`
2. Copy your skill folder into the repo
3. Commit and push to master:
   ```bash
   git add <skill-name>/
   git commit -m "feat: add <skill-name> skill"
   git push origin master
   ```
4. Wait for the Security Scan CI to pass (check with `gh run list --repo skills-il/<category-repo> --limit 1`)
5. Insert into Supabase using the sync pipeline or direct SQL insert
6. Verify the skill appears on the live site (ISR cache refreshes within ~5 minutes)

The `github_url` in the database must point to the skill folder, not the repo root:
`https://github.com/skills-il/<category-repo>/tree/master/<skill-name>`

## Examples

### Example 1: Create a Government Services Skill

User says: "I want to create a skill for querying Israeli court decisions"

Actions:
1. Category: government-services
2. Creator info: Ask for name and email
3. Use cases: search by case number, search by judge name, search by topic (Hebrew legal terms)
4. Fact-check: Verify court system structure, Nevo access methods, citation formats via official sources
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-court-decisions --category government-services`
6. Frontmatter: name=israeli-court-decisions, author=creator_name, triggers include "psakei din", "beit mishpat", "nevo"
7. Instructions: Steps for search types, result parsing, citation format
8. References: `references/court-hierarchy.md` (court levels), `references/citation-format.md` (Israeli legal citation rules)
9. Hebrew: SKILL_HE.md with native legal terminology
10. Validate: `./scripts/validate-skill.sh israeli-court-decisions/SKILL.md`
11. Submit via https://agentskills.co.il/en/submit

Result: Complete skill ready for the Skills IL directory.

### Example 2: Create a Developer Tool Skill

User says: "I need a skill that helps format Israeli addresses"

Actions:
1. Category: developer-tools (or government-services for address lookup APIs)
2. Creator info: Ask for name and email
3. Use cases: format for postal mail, validate mikud, normalize city names
4. Fact-check: Verify mikud format rules, Israel Post API availability, city name mappings
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-address-formatter --category developer-tools`
6. Frontmatter: triggers include "format ktovet", "mikud", "address normalization"
7. Instructions: Format rules, mikud lookup, bilingual city names
8. References: `references/mikud-format.md`; Scripts: `scripts/mikud-validator.py`
9. Hebrew: SKILL_HE.md
10. Validate: passes all checks
11. Submit via https://agentskills.co.il/en/submit

Result: Address formatting skill with validation and postal format support.

### Example 3: Create a Skill with MCP Integration

User says: "I want to create a skill that uses the israeli-bank-mcp server"

Actions:
1. Category: tax-and-finance
2. Creator info: Ask for name and email
3. Use cases: categorize transactions, detect recurring charges, monthly summary
4. Fact-check: Verify Israeli bank API patterns, transaction category standards
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-bank-analyzer --category tax-and-finance`
6. Frontmatter: add `mcp-server: israeli-bank-mcp` to metadata, triggers include "nituch tenuot bank"
7. Instructions: MCP tool calls for fetching transactions, categorization logic, summary generation
8. References: `references/bank-api-reference.md`; Scripts: `scripts/transaction-categorizer.py`
9. Hebrew: SKILL_HE.md with banking terminology
10. Validate: passes all checks
11. Submit via https://agentskills.co.il/en/submit

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
