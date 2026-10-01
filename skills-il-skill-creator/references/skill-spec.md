# Skills-IL SKILL.md Specification

Complete reference for creating skills-il skills. Consult this when writing frontmatter, instructions, or preparing a PR.

## Contents

1. Frontmatter Fields (including metadata.json and Supported Agents)
2. Description Formula
3. The 5 Skill Patterns
4. Validation Rules
5. Quality Checklist
6. Allowed-Tools Patterns
7. Reference and Script Patterns
8. Category Repos
9. Progressive Disclosure Levels

## Frontmatter Fields

### Required Fields

| Field | Rules | Example |
|-------|-------|---------|
| `name` | kebab-case, at most 64 chars, no leading, trailing, or consecutive hyphens, matches folder name, no "claude"/"anthropic" | `israeli-vat-reporting` |
| `description` | At most 1023 chars counted with any YAML quotes (the spec allows 1024; skills-il enforces 1023 for Gemini Spark), third person, no `<>`, must include trigger phrase | See description formula below |

### Optional Fields

| Field | Rules | Example |
|-------|-------|---------|
| `license` | Typically MIT | `MIT` |
| `allowed-tools` | Space-separated pre-approved tools. Experimental in the spec, support varies by agent | `'Bash(python3:*) WebFetch'` |
| `compatibility` | 1-500 chars, environment requirements | `'Requires network access.'` |

**Do NOT put a `metadata:` key in the SKILL.md frontmatter.** Claude Desktop rejects it. All enriched metadata lives in a separate `metadata.json` file alongside SKILL.md.

### metadata.json Structure

All enriched metadata goes in `metadata.json` (same folder as SKILL.md), NOT in the YAML frontmatter:

```json
{
  "author": "<GitHub login>",
  "version": "1.0.0",
  "category": "<category-repo-name>",
  "tags": {
    "he": ["<domain-tag-he>", "<function-tag-he>", "ישראל"],
    "en": ["<domain-tag>", "<function-tag>", "israel"]
  },
  "display_name": {
    "he": "<Hebrew name>",
    "en": "<English Name>"
  },
  "display_description": {
    "he": "<Hebrew description>",
    "en": "<English description>"
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

`author` must be a real GitHub login. The directory builds the creator link (`github.com/<author>`) and avatar (`github.com/<author>.png`) from it, so a full name or brand renders broken. Only skills authored by the skills-il team use `skills-il`.

### Supported Agents

Valid `supported_agents` slugs, grouped by what the agent can do with a skill's bundled scripts:

| Tier | Slugs | Runs `python3 scripts/...`? |
|---|---|---|
| Terminal agents | `claude-code`, `cursor`, `github-copilot`, `windsurf`, `opencode`, `codex`, `openclaw`, `antigravity`, `gemini-cli`, `grok-build` | Yes |
| Desktop, web and upload platforms | `claude-desktop`, `claude-ai`, `chatgpt`, `manus`, `grok` | Do not assume it. Any execution happens in the platform's own sandbox, if at all. Give a route that works without running the script (`claude-desktop` can also use a local MCP server) |
| Gemini Spark | `gemini-spark` | Yes, but scripts cannot make network requests |

Declare an agent only if the skill's happy path works on it. A skill whose only data path is a bundled script is broken on an upload platform by construction, however good the instructions are. Either add an alternative route for that tier or leave the agent out.

**Gemini Spark** installs the same ZIP through its Skills upload. In the directory's experience three limits matter: the uploader rejects binary files, bundled scripts cannot make network requests (so a Spark-declared skill needs a non-network path), and it rejects a description sitting at the 1024 limit, which is why the validator caps at 1023 including quotes.

If the skill recommends an MCP server, add a `## Recommended MCP Servers` section to the SKILL.md body (the old `mcp-server` frontmatter key is no longer used).

**Tags rules:**
- Both `he` and `en` arrays are required
- Arrays must be the same length (each English tag has exactly one Hebrew counterpart)
- No empty strings allowed in either array
- Technical terms with no Hebrew equivalent can stay in English in both arrays (e.g., `API`, `MCP`)

## Description Formula

```
[What it does] + [When to use it] + [Key capabilities] + [Do NOT use for X]
```

Write it in the third person ("Validates...", "Integrates..."). It is injected into the agent's system prompt, so "I can help you..." or "You can use this to..." reads as a shift in point of view and degrades discovery. Aim for 950 characters or fewer. In a regulated domain, open with the short legal clause ("Not legal advice.") so it survives truncation.

### Good Descriptions

```yaml
# Specific + actionable + Hebrew triggers + anti-triggers
description: >-
  Validates and formats Israeli identification numbers including Teudat Zehut
  (personal ID), company numbers, amuta (non-profit) numbers, and partnership
  numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar
  zehut", company number validation, or needs to implement Israeli ID validation
  in code. Includes check digit algorithm and test ID generation. Do NOT use for
  non-Israeli identification systems.
```

```yaml
# Clear scope + multiple triggers + cross-references
description: >-
  Integrates Tranzila payment processing into Israeli applications, covering
  iframe payments, tokenization, installments (tashlumim), refunds, 3D Secure,
  and Bit wallet. Use when user asks to accept payments via Tranzila, "slikat
  ashrai", handle tashlumim, or mentions "Tranzila". Do NOT use for Cardcom
  integration (use cardcom-payment-gateway).
```

### Bad Descriptions

```yaml
# Too vague -- no triggers, no scope
description: Helps with Israeli things.

# Missing triggers -- won't activate
description: Creates sophisticated multi-page documentation systems.

# Too technical -- no user triggers
description: Implements the Israeli ID check digit algorithm with Luhn-variant validation.

# Wrong point of view -- first/second person instead of third
description: I can help you validate Israeli ID numbers. Use when you need to check a teudat zehut.
```

## The 5 Skill Patterns

From Anthropic's "The Complete Guide to Building Skills for Claude" (https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf):

### Pattern 1: Sequential Workflow Orchestration
**Use when**: Multi-step processes in specific order.
- Explicit step ordering
- Dependencies between steps
- Validation at each stage
- Rollback instructions for failures

### Pattern 2: Multi-MCP Coordination
**Use when**: Workflows spanning multiple services.
- Clear phase separation
- Data passing between MCPs
- Validation before moving to next phase
- Centralized error handling

### Pattern 3: Iterative Refinement
**Use when**: Output quality improves with iteration.
- Quality check after initial draft
- Refinement loop addressing issues
- Re-validate until threshold met
- Finalization step

### Pattern 4: Context-Aware Tool Selection
**Use when**: Same outcome, different tools depending on context.
- Clear decision criteria
- Fallback options
- Transparency about choices

### Pattern 5: Domain-Specific Intelligence
**Use when**: Skill adds specialized knowledge beyond tool access.
- Domain expertise embedded in logic
- Compliance before action
- Comprehensive documentation
- Clear governance

## Validation Rules

The current rule table, split into errors and warnings and including the YAML-parse and SKILL_HE.md checks, is in `references/submission-checklist.md`. Run the validator from the category-repo root. The upstream `skills-ref validate` tool checks spec compliance only, not the skills-il rules.

### Trigger Phrase Patterns

Description must contain at least one of:
- `use when`
- `use for`
- `use if`
- `when user`
- `when the user`

(Case-insensitive matching)

## Quality Checklist

### Before Submission
- [ ] 2-3 concrete use cases identified
- [ ] Creator name and email collected
- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, at most 64 chars, matches folder
- [ ] `description` includes WHAT and WHEN, third person, 1023 chars or fewer including quotes
- [ ] No XML tags (`<>`) anywhere in frontmatter
- [ ] Instructions are specific and actionable
- [ ] Error handling / troubleshooting included
- [ ] 2+ examples provided
- [ ] References linked with "Consult when..." guidance
- [ ] Body under 5,000 words
- [ ] No hardcoded secrets
- [ ] SKILL_HE.md exists, headings translated, same heading count as SKILL.md
- [ ] Gotchas describe agent failure modes, not user errors
- [ ] Regulated domain? Legal notice right after the H1 in both files
- [ ] `author` is a real GitHub login
- [ ] Bilingual `display_name` and `display_description` in metadata
- [ ] `metadata.tags` has both `he` and `en` arrays of equal length with no empty strings
- [ ] `supported_agents` list is accurate

### After Submission
- [ ] validate-skill.sh passes
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass

## Allowed-Tools Patterns

| Scenario | Value |
|----------|-------|
| No tools needed | Omit field |
| Python only | `'Bash(python3:*)'` |
| Python + web fetch | `'Bash(python3:*) WebFetch'` |
| Python + pip | `'Bash(python3:*) Bash(pip:*)'` |
| cURL + Python | `'Bash(curl:*) Bash(python3:*) WebFetch'` |
| CLI tool | `'Bash(jf:*) Bash(docker:*)'` |
| OCR | `'Bash(python3:*) Bash(pip:*) Bash(tesseract:*)'` |

## Reference and Script Patterns

### Reference files

| Pattern | Example | When to use |
|---------|---------|-------------|
| Directory/listing | `hospital-directory.md`, `crisis-hotlines-directory.md` | Skill covers a domain with many institutions, services, or contacts |
| Detailed guide | `fair-rental-law-summary.md`, `ivf-process-detailed.md` | A process or law needs more detail than fits in instructions |
| Glossary | `hebrew-rental-glossary.md` | Skill uses domain-specific Hebrew terminology (50+ terms) |
| Checklist | `contract-checklist.md`, `evidence-guide.md` | Users need a step-by-step verification or preparation list |
| Comparison table | `universities-comparison.md`, `city-rental-guide.md` | Users need to compare options across multiple dimensions |
| Template | `demand-letter-template.md` | Users need a starting point for a document or form |

### Helper scripts

| Pattern | Example | When to use |
|---------|---------|-------------|
| Calculator | `sekher-calculator.py`, `filing-fee-calculator.py` | Skill involves formulas, tax calculations, or fee estimation |
| Coverage checker | `fertility-coverage-checker.py` | Skill involves eligibility rules based on multiple criteria |
| Cost estimator | `therapy-cost-estimator.py`, `rental-budget-calculator.py` | Users need to compare costs across options |
| Index/adjustment | `rent-index-calculator.py` | Skill involves CPI-linked values or time-based adjustments |

## Category Repos

| Repo | Focus |
|------|-------|
| tax-and-finance | Invoicing, payroll, VAT, payments, pensions |
| government-services | data.gov.il, Bituach Leumi, transit, elections |
| security-compliance | Privacy law, cybersecurity, legal research |
| localization | RTL, Hebrew NLP, OCR, Shabbat scheduling |
| developer-tools | ID validation, dates, phones, DevOps |
| communication | SMS, WhatsApp, Monday.com, job market |
| food-and-dining | Restaurants, recipes, kashrut, delivery |
| legal-tech | Contracts, legal research, compliance |
| education | Learning platforms, tutoring, academic tools |
| health-services | HMOs, pharmacy, medical records, appointments |
| marketing-growth | SEO, social media, ads, email campaigns, ASO |
| accounting | Bookkeeping, financial reporting, audit, accountant tooling |
| travel | Trip planning, flights, destinations, travel rights |

## Progressive Disclosure Levels

1. **Frontmatter (YAML)** -- Always loaded. Decides if skill activates. Keep description tight and trigger-rich.
2. **SKILL.md body** -- Loaded when skill activates. Core instructions, examples, troubleshooting.
3. **Linked files (references/, scripts/, assets/)** -- Loaded on demand. Detailed docs, executable code, templates and data files, edge cases. Keep links one level deep from SKILL.md.
