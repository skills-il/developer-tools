# Skills-IL SKILL.md Specification

Complete reference for creating skills-il skills. Consult this when writing frontmatter, instructions, or preparing a PR.

## Frontmatter Fields

### Required Fields

| Field | Rules | Example |
|-------|-------|---------|
| `name` | kebab-case, matches folder name, no "claude"/"anthropic" | `israeli-vat-reporting` |
| `description` | Under 1024 chars, no `<>`, must include trigger phrase | See description formula below |

### Optional Fields

| Field | Rules | Example |
|-------|-------|---------|
| `license` | Typically MIT | `MIT` |
| `allowed-tools` | Tool access restrictions | `'Bash(python:*) WebFetch'` |
| `compatibility` | 1-500 chars, environment requirements | `'Requires network access.'` |
| `metadata` | Custom key-value pairs | See metadata section |

### Metadata Structure

```yaml
metadata:
  author: skills-il
  version: 1.0.0
  category: <category-repo-name>
  mcp-server: <server-name>          # Only if skill uses MCP
  tags:
    he:
      - <domain-tag-he>
      - <function-tag-he>
      - ישראל
    en:
      - <domain-tag>
      - <function-tag>
      - israel
  display_name:
    he: "<Hebrew name>"
    en: <English Name>
  display_description:
    he: "<Hebrew description>"
    en: >-
      <English description>
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
```

**Tags rules:**
- Both `he` and `en` arrays are required
- Arrays must be the same length (each English tag has exactly one Hebrew counterpart)
- No empty strings allowed in either array
- Technical terms with no Hebrew equivalent can stay in English in both arrays (e.g., `API`, `MCP`)

## Description Formula

```
[What it does] + [When to use it] + [Key capabilities] + [Do NOT use for X]
```

### Good Descriptions

```yaml
# Specific + actionable + Hebrew triggers + anti-triggers
description: >-
  Validate and format Israeli identification numbers including Teudat Zehut
  (personal ID), company numbers, amuta (non-profit) numbers, and partnership
  numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar
  zehut", company number validation, or needs to implement Israeli ID validation
  in code. Includes check digit algorithm and test ID generation. Do NOT use for
  non-Israeli identification systems.
```

```yaml
# Clear scope + multiple triggers + cross-references
description: >-
  Integrate Tranzila payment processing into Israeli applications -- covers
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
```

## The 5 Skill Patterns

From Anthropic's Complete Guide to Building Skills:

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

The `validate-skill.sh` script checks:

| # | Rule | Regex / Check |
|---|------|---------------|
| 1 | File is exactly `SKILL.md` (case-sensitive) | Filename check |
| 2 | File starts with `---` | First line check |
| 3 | `name` is kebab-case, matches folder | `^[a-z0-9]+(-[a-z0-9]+)*$` |
| 4 | Name has no "claude" or "anthropic" | String contains check |
| 5 | Description: present, under 1024 chars, has trigger, no `<>` | Multiple checks |
| 6 | No `<>` in frontmatter | Angle bracket scan |
| 7 | Body under 5,000 words | Word count |
| 8 | No README.md in skill folder | File existence check |
| 9 | No hardcoded secrets | Patterns: s k - prefix, A K I A prefix, g h p _ prefix, password colon, secret underscore key, api underscore key equals |

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
- [ ] `name` field: kebab-case, matches folder
- [ ] `description` includes WHAT and WHEN
- [ ] No XML tags (`<>`) anywhere in frontmatter
- [ ] Instructions are specific and actionable
- [ ] Error handling / troubleshooting included
- [ ] 2+ examples provided
- [ ] References linked with "Consult when..." guidance
- [ ] Body under 5,000 words
- [ ] No hardcoded secrets
- [ ] SKILL_HE.md exists with consistent structure
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
| Python only | `'Bash(python:*)'` |
| Python + web fetch | `'Bash(python:*) WebFetch'` |
| Python + pip | `'Bash(python:*) Bash(pip:*)'` |
| cURL + Python | `'Bash(curl:*) Bash(python:*) WebFetch'` |
| CLI tool | `'Bash(jf:*) Bash(docker:*)'` |
| OCR | `'Bash(python:*) Bash(pip:*) Bash(tesseract:*)'` |

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

## Progressive Disclosure Levels

1. **Frontmatter (YAML)** -- Always loaded. Decides if skill activates. Keep description tight and trigger-rich.
2. **SKILL.md body** -- Loaded when skill activates. Core instructions, examples, troubleshooting.
3. **Linked files (references/, scripts/)** -- Loaded on demand. Detailed docs, executable code, edge cases.
