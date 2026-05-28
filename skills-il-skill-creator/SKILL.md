---
name: skills-il-skill-creator
description: Interactive workflow for creating new skills for the skills-il organization. Guides through category selection, use case definition, folder scaffolding, metadata.json generation with bilingual metadata, instruction writing, Hebrew companion creation, and validation. Use when user asks to create a new skill, scaffold a skill for skills-il, write a SKILL.md, contribute a skill, new skill template, or liztor skill chadash. Enforces skills-il conventions (kebab-case naming, Hebrew transliterations, bilingual display names, progressive disclosure, validate-skill.sh compliance). Do NOT use for editing existing skills, creating skills for non-skills-il platforms, or generic markdown file creation.
license: MIT
allowed-tools: Bash(python:*) Bash(./scripts/*) WebFetch
compatibility: No network required for scaffolding. WebFetch optional for pulling latest conventions. Works with Claude Code, Claude.ai, Cursor.
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
| Accounting | accounting | Bookkeeping, financial reporting, audit, accountant tooling |

All 12 category repos use `master` as their default branch (not `main`). The full path format for `github_url` is `https://github.com/skills-il/<repo>/tree/master/<slug>`.

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
For each key fact, note: the fact, the source, and the date verified. Include these as inline references in your SKILL.md instructions, always with the effective date (for example, an amount followed by "as of January 2025").

Do NOT skip this step. A skill with outdated or incorrect facts (wrong tax rate, expired law, wrong phone number) is worse than no skill at all.

### Step 5: Scaffold the Folder

Run the scaffolding script to create the skill folder structure:

```bash
python scripts/scaffold-skill.py --name <skill-name> --category <category-repo>
```

The script creates:
```
<skill-name>/
├── SKILL.md          # Minimal frontmatter (name, description, license)
├── SKILL_HE.md       # Hebrew companion stub
├── metadata.json     # Enriched metadata (tags, display names, agents)
├── scripts/          # For helper scripts
└── references/       # For reference documentation
```

Verify the output:
- Folder name is kebab-case
- No spaces, underscores, or capitals
- Name does not contain "claude" or "anthropic"
- No README.md inside the skill folder (skill folders must not contain README.md)
- The **repo-level README.md** (at the root of the category repo) must be written in **English**. This is required because the repo is public on GitHub and the README serves as the entry point for international developers and AI agents. Hebrew content belongs in SKILL_HE.md files inside skill folders, not in the repo README.

### Step 6: Write the YAML Frontmatter and metadata.json

**CRITICAL: Skills-il splits metadata across two files.** Claude Desktop rejects the `metadata` key inside SKILL.md frontmatter, so all enriched metadata lives in a separate `metadata.json` file. The SKILL.md frontmatter is intentionally minimal.

**SKILL.md frontmatter (only these 3-5 fields):**

```yaml
---
name: <skill-name>
description: >-
  [What it does -- one sentence]. Use when user asks to [triggers in English],
  "[Hebrew transliteration 1]", "[Hebrew transliteration 2]", or [more triggers].
  [Key capabilities]. Do NOT use for [anti-triggers] (use [alternative-skill] instead).
license: MIT
allowed-tools: '<tools if needed>'      # optional, only when scripts call CLI tools
compatibility: >-                         # optional
  [Network/system requirements]. Works with Claude Code, Claude.ai, Cursor.
---
```

Do NOT add `metadata:`, `version:`, `tags:`, `display_name:`, `display_description:`, `author:`, `category:`, or `supported_agents:` to the frontmatter. Claude Desktop rejects them.

**metadata.json (in the same skill folder, alongside SKILL.md):**

```json
{
  "author": "<creator_name from Step 2>",
  "version": "1.0.0",
  "category": "<category-repo>",
  "tags": {
    "he": ["<tag1-he>", "<tag2-he>", "ישראל"],
    "en": ["<tag1>", "<tag2>", "israel"]
  },
  "display_name": {
    "he": "<Hebrew display name>",
    "en": "<English Display Name>"
  },
  "display_description": {
    "he": "<Hebrew description>",
    "en": "<English description, mirrors the main description field>"
  },
  "supported_agents": [
    "claude-code",
    "cursor",
    "github-copilot",
    "windsurf",
    "opencode",
    "codex",
    "gemini-cli"
  ]
}
```

**Supported agents:** Include all standard agents (claude-code, cursor, github-copilot, windsurf, opencode, codex, gemini-cli) by default. If the skill relies on agent-specific features (e.g., MCP tools only available in Claude Code), remove agents that cannot support it and document why in the `compatibility` field. Add `antigravity` only if the skill is verified as Antigravity-compatible.

**Project style rules (apply to every skill file):**

- **No em dashes (U+2014) or en dashes (U+2013)** anywhere in SKILL.md, SKILL_HE.md, metadata.json, references, or scripts. Replace with commas, parentheses, periods, or "to" for ranges. Use the regular ASCII hyphen-minus instead.
- **All 12 category repos use `master`**, not `main`, as the default branch.
- **`github_url` format must include the full path to the skill folder**, not just the repo root: `https://github.com/skills-il/<repo>/tree/master/<slug>`.

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

## Gotchas

- SKILL.md frontmatter uses YAML with specific nested structure (metadata.tags.he/en arrays). Agents may flatten the tags into a single array instead of using the bilingual he/en structure.
- Hebrew content in SKILL_HE.md must never appear inside code blocks (```) because code blocks do not support RTL rendering. Use plain text or bullet lists for Hebrew content.
- The skill description field has a dual purpose: it serves as both the YAML frontmatter description and the trigger text for agent matching. Agents may write a generic description that fails to trigger on relevant user queries.
- Skills must validate with the skills-il schema (name, description, license, metadata with version/category/tags). Agents may omit required fields like supported_agents or display_name.

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

### Step 8.5: Add Reference Links Section

Every skill MUST include a `## Reference Links` section (after `## Recommended MCP Servers` or `## Bundled Resources`, before `## Troubleshooting`) with a table of official source URLs used to verify the skill's domain-specific facts.

**Format:**
```markdown
## Reference Links

Official sources for verifying and updating the information in this skill:

| Source | URL | What to Check |
|--------|-----|---------------|
| Israeli Tax Authority | https://www.gov.il/he/departments/israel_tax_authority | Tax rates, forms, circulars |
| Kolzchut | https://www.kolzchut.org.il | Rights, entitlements, eligibility |
```

**Guidelines:**
- Include 3-6 authoritative links (government sites, official API docs, legal databases)
- Each link should have a "What to Check" column explaining what to verify there
- Prefer `.gov.il`, `.org.il`, and institutional sources over blogs
- Include at least one English-language source when available
- The Hebrew companion must have a matching `## קישורי עזר` section

**Why this matters:**
- Users can independently verify claims
- The fact-check pipeline uses these URLs for automated validation
- It builds trust by showing the skill's information is grounded in official sources

### Step 9: Create the Hebrew Companion (SKILL_HE.md)

Create SKILL_HE.md with the same structure but in Hebrew:
- Translate the body instructions to Hebrew
- Keep code blocks, field names, and API references in English
- Use Hebrew-native terminology (not transliterations)
- Maintain the same step numbering and section structure

The Hebrew file uses the same frontmatter as SKILL.md (frontmatter stays in English).

### Step 9.5: Validate All Links (MANDATORY)

Before running the validation script, verify that every URL in the skill content actually resolves. Broken links in published skills erode trust and cause the automated fact-check pipeline to flag false positives.

**Step 1: Extract all URLs** from all skill files:
```bash
grep -rEoh 'https?://[^ )>"'\'']+' <skill-name>/ | sort -u > /tmp/<skill-name>-urls.txt
cat /tmp/<skill-name>-urls.txt
```

**Step 2: Check each URL returns HTTP 200:**
```bash
while IFS= read -r url; do
  status=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$url" 2>/dev/null)
  [ "$status" != "200" ] && echo "[$status] $url"
done < /tmp/<skill-name>-urls.txt
```

If no output, all links are valid. If any lines appear, fix them:

| HTTP Status | Action |
|-------------|--------|
| 301/302 | Update URL to the final redirect destination |
| 403 | May be geo-blocked or bot-blocked. Verify manually in a browser. If it works in a browser, keep it |
| 404 | **BROKEN** -- find the correct URL via WebSearch, or remove the link |
| 5xx | Retry once. If still failing, the service may be down temporarily. Note it |
| Timeout / DNS failure | **BROKEN** -- the domain may no longer exist. Remove all references to this URL |

**Pay special attention to:**
- `.gov.il` URLs (Israeli government sites restructure frequently)
- Israeli startup domains (`.co.il`) that may have gone offline
- Reference Links table entries (Step 8.5) -- these are the most visible links to users

**Do NOT proceed to Step 10 with broken links.** Fix every broken URL first.

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
- [ ] All URLs return HTTP 200 (Step 9.5)
- [ ] Description includes WHAT and WHEN
- [ ] Instructions are specific and actionable
- [ ] Examples cover 2+ real scenarios
- [ ] Troubleshooting covers likely errors
- [ ] Reference Links section with 3-6 verified official source URLs
- [ ] Hebrew companion exists and section structure matches SKILL.md 1:1 (including `## קישורי עזר`)
- [ ] At least 2 reference files in `references/` with "Consult when..." guidance
- [ ] At least 1 helper script in `scripts/` with argparse and `--help`
- [ ] No security issues (secrets, injection vectors)
- [ ] `supported_agents` list is accurate (all compatible agents included)
- [ ] `metadata.version` is set (e.g., 1.0.0)
- [ ] `metadata.tags` has both `he` and `en` arrays of equal length with no empty strings
- [ ] `creator_name` and `creator_email` collected from user (Step 2)
- [ ] Repo-level README.md is written in English (not Hebrew)

### Step 10.5: Pre-Submission GitHub Verification Setup

The submission form runs a live GitHub Verification scorecard against your repo before you can submit. The 5 Critical signals must pass for the skills-il team to approve. Set them up now (about 15 minutes total) so you don't bounce at submit time.

| # | Signal | Quick Setup |
|---|--------|-------------|
| 1 | `spec_compliant` | Install `gh` CLI 2.90.0+, then run `gh skill publish --dry-run path/to/your-skill` locally and fix any errors |
| 2 | `secret_scanning` | Repo → Settings → Code security and analysis → enable **Secret scanning** + **Push protection** |
| 3 | `code_scanning` | Same Settings page → under **Code scanning** click **Set up** → **Default** |
| 4 | `signed_release` | Add `.github/workflows/release.yml` that uses `actions/attest-build-provenance@v4` on `tags: ['v*']` (or use `skills-il/release-workflow@v1` as a reusable workflow), then push a `v1.0.0` tag |
| 5 | `license_spdx` | Add a `LICENSE` file at the repo root with a recognized SPDX license (use GitHub's "Choose a license template"; MIT is the standard) |

**For MCPs the `spec_compliant` row is N/A** (the `gh skill` CLI validates SKILL.md only, not MCP servers). The other 4 still apply.

**Copy-paste setup steps for each signal**, with full YAML snippets and screenshots, are in the [GitHub Verification checklist guide](https://agentskills.co.il/en/guides/github-verification-checklist). When in doubt, follow that guide.

**Skip this step at your own risk:** the admin approval gate refuses approval unless `critical_all_pass` is true. The rejection email will tell you which signals failed and link back to this guide.

### Step 11: Submit Your Skill

After validation passes, submit your skill through the [submission page](https://agentskills.co.il/en/submit).

1. Choose submission type: "Existing Repository" (if you pushed your skill to a GitHub repo) or "Proposal" (if you want the skills-il team to create the repo)
2. Fill in the form with: your GitHub repo URL, creator name, and creator email (from Step 2)
3. **The form will fetch your SKILL.md and run a live GitHub Verification scorecard.** You'll see pass/fail for each of the 5 Critical signals. If any fail, fix them per Step 10.5 and re-submit.
4. The skills-il team will review your submission, run security analysis, and publish it if it passes

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
11. Submit via the [submission page](https://agentskills.co.il/en/submit)

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
11. Submit via the [submission page](https://agentskills.co.il/en/submit)

Result: Address formatting skill with validation and postal format support.

### Example 3: Create a Skill with MCP Integration

User says: "I want to create a skill that uses the israeli-bank-mcp server"

Actions:
1. Category: tax-and-finance
2. Creator info: Ask for name and email
3. Use cases: categorize transactions, detect recurring charges, monthly summary
4. Fact-check: Verify Israeli bank API patterns, transaction category standards
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-bank-analyzer --category tax-and-finance`
6. metadata.json: include the relevant Recommended MCP Servers section in SKILL.md (and `## שרתי MCP מומלצים` in SKILL_HE.md) pointing to `israeli-bank-mcp`. Description triggers include "nituch tenuot bank"
7. Instructions: MCP tool calls for fetching transactions, categorization logic, summary generation
8. References: `references/bank-api-reference.md`; Scripts: `scripts/transaction-categorizer.py`
9. Hebrew: SKILL_HE.md with banking terminology
10. Validate: passes all checks
11. Submit via the [submission page](https://agentskills.co.il/en/submit)

Result: MCP-enhanced skill that adds workflow intelligence on top of bank data access.

## Bundled Resources

### Scripts
- `scripts/scaffold-skill.py` -- Creates the complete folder structure for a new skills-il skill: SKILL.md with minimal frontmatter, SKILL_HE.md stub, metadata.json (enriched metadata), and scripts/ and references/ directories. Validates name and category and prevents overwrites. Run: `python scripts/scaffold-skill.py --help`

### References
- `references/skill-spec.md` -- Complete skills-il SKILL.md specification including all frontmatter fields (required and optional), description-writing formula with good/bad examples, the 5 skill patterns from Anthropic's guide, quality checklist, and validation rules. Consult when writing frontmatter or instructions and you need detailed guidance beyond the steps above.

## Gotchas

- Enriched metadata lives in `metadata.json`, NOT in SKILL.md frontmatter. Claude Desktop rejects a `metadata:` key in YAML frontmatter. Agents trained on older skills (or an old scaffold template) may put `version`, `tags`, `display_name`, and `supported_agents` in the frontmatter, which breaks the skill.
- `metadata.json` tags use a bilingual `tags.he` / `tags.en` structure of equal length. Agents may flatten the tags into a single array.
- Hebrew content in SKILL_HE.md must never appear inside code blocks (```) because code blocks do not support RTL rendering. Use plain text or bullet lists for Hebrew content.
- The skill description field has a dual purpose: it serves as both the YAML frontmatter description and the trigger text for agent matching. Agents may write a generic description that fails to trigger on relevant user queries.
- `metadata.json` must include `version`, `category`, bilingual `tags`, `display_name`, `display_description`, and `supported_agents`. Agents may omit required fields like `supported_agents` or `display_name`.

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
