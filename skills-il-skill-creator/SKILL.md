---
name: skills-il-skill-creator
description: Interactive workflow for creating new skills for the skills-il organization. Guides through category selection, use case definition, folder scaffolding, metadata.json generation with bilingual metadata, instruction writing, Hebrew companion creation, and validation. Use when user asks to create a new skill, scaffold a skill for skills-il, write a SKILL.md, contribute a skill, new skill template, or liztor skill chadash. Enforces skills-il conventions (kebab-case naming, Hebrew transliterations, bilingual display names, progressive disclosure, validate-skill.sh compliance). Do NOT use for editing existing skills, creating skills for non-skills-il platforms, or generic markdown file creation.
license: MIT
allowed-tools: 'Bash(python3:*) Bash(curl:*) Bash(./scripts/*) WebFetch'
compatibility: No network required for scaffolding. WebFetch optional for pulling latest conventions. Needs a terminal agent that can run Python 3 (Claude Code, Cursor, Codex and similar).
---

# Skills-IL Skill Creator

## Overview

This skill walks you through creating a production-quality skill for the skills-il organization. It follows Anthropic's Complete Guide to Building Skills and enforces all skills-il conventions.

Every skill you create will include SKILL.md, a Hebrew companion (SKILL_HE.md), bilingual metadata.json, and will pass validation.

## Instructions

### Step 1: Choose Category Repository

Ask the user which of the 13 category repos this skill belongs to: tax-and-finance, government-services, security-compliance, localization, developer-tools, communication, food-and-dining, legal-tech, marketing-growth, education, health-services, accounting, or travel. Each repo's focus area is in `references/skill-spec.md`.

If the skill doesn't fit any category, discuss with the user whether it belongs in an existing category or warrants a new repo.

### Step 2: Collect Creator Information (MUST ASK)

Before proceeding, you MUST ask the user for their creator details. These are required for submitting the skill to the Skills IL directory.

Ask the user:

> "What is your GitHub username? It becomes the `author` of the skill, and the directory builds your creator link and avatar from it."

Wait for the user's response and store their answer as `creator_name`.

Then ask:

> "What is your email address? This is required so we can notify you when your skill is published, featured, or if we need to contact you about updates. It will not be displayed publicly."

Wait for the user's response and store their answer as `creator_email`.

**Rules:**
- `creator_name` is required and must be a real GitHub login, not a full name, brand, or pen name. The directory links to `github.com/<author>` and loads the avatar from `github.com/<author>.png`, so anything that is not an account renders as a broken link and a missing image. Check it before using it: `curl -sL -o /dev/null -w '%{http_code}' https://github.com/<author>.png` must print `200` (a missing account prints `404`).
- `creator_email` is **required** and must be a valid email address. Do NOT proceed without it.
- Store both values. `creator_name` goes into the `author` field of `metadata.json`; both are entered on the submission form.
- If the user declines, explain that the email is mandatory for submission.

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

**Record a baseline now, before anything is scaffolded.** Give one use case to an agent that does NOT have the skill and write down three lines: the task you gave it, which agent you used, and exactly where it failed (wrong figure, missed step, invented form number). Everything the skill later says should fix something on that list. If the agent already gets every use case right, stop here: the skill would only restate what the model knows.

### Step 4: Fact-Check Domain Information

Before writing any content, verify the key facts your skill will reference. This is especially important for skills dealing with Israeli laws, regulations, government services, financial rules, or healthcare policies, as these change frequently.

**What to verify:** legal thresholds and limits, government processes and form numbers, institutional names and contact details, prices and fees, and any law change that took effect this year.

**How to verify:** use official sources (gov.il, the Knesset, Bituach Leumi), search with the current year, and cross-check critical figures (money amounts, legal requirements) against at least 2 sources.

**What to record:** for each key fact, the fact, the source, and the date verified. State the effective date next to the value in SKILL.md (for example, an amount followed by "as of January 2025").

Do NOT skip this step. A skill with outdated or incorrect facts (wrong tax rate, expired law, wrong phone number) is worse than no skill at all.

### Step 4.5: Regulated-Domain Screen (decide before scaffolding)

Some acts and titles in Israel are reserved to licensed professionals (lawyers, accountants and tax advisors, property appraisers, investment and pension advisors, physicians, psychologists, and others). A skill can trespass in two independent ways, so ask both questions now:

1. **Does the name or description use a licensed profession's title or activity noun** ("appraisal", "advisor", "shamai", "yoetz mas", "orech din")? If so, rename. No disclaimer fixes a name that holds the skill out as the professional.
2. **Does the skill emit a work product reserved to one of those professions** about the user's own situation, for example a valuation, a contract, will, pleading or other legal document drafted for the user, a legal opinion, a tax filing or tax opinion, an investment or pension recommendation, a diagnosis? Explaining how a process works is information. An invoice generator or a CV writer emits documents, but none reserved to a profession, so this question does not catch them.

If either answer is yes:

- Add a `## Legal notice` section to SKILL.md and a `## הבהרה משפטית` section to SKILL_HE.md, **immediately after the H1**. Say what the skill is (an AI-operated information tool, and free if it is), that no licensed professional reviews the output, what the output is NOT in the profession's own terms and what it IS instead (general information, a statistical indication), which professional steps it does not perform, that it may be wrong, that it must not be filed, relied on as evidence, or presented as the professional's work, and that it is not a substitute for advice tailored to the user's circumstances. The directory renders this section above the fold.
- Open the SKILL.md `description` and both `display_description` values in metadata.json with a short, profession-specific clause such as "Not legal advice." / "אינו ייעוץ משפטי.", so it survives truncation in search results and cards.
- Prefer emitting the principles and arguments the user drafts from over emitting the finished instrument. A skill that outputs a ready-to-file objection letter is harder to defend than one that gives the user the points to write it.

Not sure? Say so on the submission form. The directory's intake review checks this and asks for changes before publishing.

### Step 5: Scaffold the Folder

**Where the skill lives:** either your own public GitHub repo (the usual route, submitted as "Existing Repository" in Step 11), or a fork of the category repo opened as a pull request. In your own repo, download the validator once so Step 10 can run: `mkdir -p scripts && curl -sL https://raw.githubusercontent.com/skills-il/developer-tools/master/scripts/validate-skill.sh -o scripts/validate-skill.sh && chmod +x scripts/validate-skill.sh`.

From that repo's root, run this skill's scaffolding script (`--author` is required and must be your GitHub username):

```bash
python3 <path-to-skills-il-skill-creator>/scripts/scaffold-skill.py --name <skill-name> --category <category-repo> --author <github-login>
```

The script creates (SKILL.md and SKILL_HE.md come with Gotchas and Reference Links stubs):
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
- Name is at most 64 characters, with no leading, trailing, or consecutive hyphens (Agent Skills specification)
- No README.md inside the skill folder (skill folders must not contain README.md)
- The **repo-level README.md** (at the root of your repo or the category repo) must be written in **English**. This is required because the repo is public on GitHub and the README serves as the entry point for international developers and AI agents. Hebrew content belongs in SKILL_HE.md files inside skill folders, not in the repo README.

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
  [Network/system requirements, consistent with supported_agents].
---
```

Do NOT add `metadata:`, `version:`, `tags:`, `display_name:`, `display_description:`, `author:`, `category:`, or `supported_agents:` to the frontmatter. Claude Desktop rejects them.

**metadata.json (in the same skill folder, alongside SKILL.md)** holds `author` (your GitHub username from Step 2), `version` (start at `1.0.0`), `category`, `tags` as equal-length `he` / `en` arrays, `display_name` and `display_description` as `{he, en}` objects, and `supported_agents`. The scaffold writes a filled-in skeleton; the full annotated example is in `references/skill-spec.md`.

**Supported agents:** list only agents that can actually run the skill's happy path. The scaffold defaults to seven terminal agents that can run bundled scripts. Do not assume desktop, web and upload platforms (`claude-desktop`, `claude-ai`, `chatgpt`, `manus`, `grok`) can run a step like `python3 scripts/x.py`; add one only if the skill has a route that works there. `gemini-spark` runs scripts but without network access. The full slug list, the capability tiers, and the Gemini Spark constraints are in `references/skill-spec.md`. Document any deliberate exclusion in `compatibility`.

**Project style rules (apply to every skill file):**

- **No em dashes (U+2014) or en dashes (U+2013)** in any skill file. Use commas, parentheses, periods, "to" for ranges, or the ASCII hyphen.
- **All 13 category repos use `master`**, not `main`, and a skill's GitHub URL includes the full folder path: `https://github.com/skills-il/<repo>/tree/master/<slug>`.

**Bilingual tags (MUST ASK):** After defining the English tags, ask the user:

> "Please provide a Hebrew translation for each tag. What are the Hebrew equivalents?"

Both arrays are required, must be the same length (one Hebrew tag per English tag), and may not contain empty strings. Technical terms with no Hebrew equivalent (`API`, `MCP`) stay in English in both.

**Description rules (CRITICAL):**
- Must follow pattern: `[What it does] + [When to use it] + [Key capabilities] + [Do NOT use for X]`
- Written in the third person ("Validates Israeli ID numbers..."), never "I can help you" or "You can use this". The description is injected into the agent's system prompt, and a shifting point of view hurts discovery.
- At most 1023 characters, counted WITH any surrounding YAML quotes; aim for 950 or fewer. The spec allows 1024, but Gemini Spark rejects a description sitting at the limit, and the validator enforces 1023. In a plain one-line value, a colon followed by a space breaks YAML parsing. Use the folded `>-` style (as the scaffold does), or quote the value (2 more characters), or reword the colon to a comma.
- No XML angle brackets (< >) anywhere in frontmatter
- Include trigger phrases users would actually say
- Include Hebrew transliterations in quotes (e.g., "tlush maskoret")
- End with `Do NOT use for` boundary + cross-reference to related skills

**Allowed-tools:** omit the field when no tools are needed; otherwise use a quoted, space-separated list such as `'Bash(python3:*) WebFetch'`. More patterns are in `references/skill-spec.md`. The field is experimental in the spec and not every agent honors it.

### Step 6.5: Authoring Principles (apply while writing Steps 7-8)

These principles decide whether a skill actually improves agent behavior or just adds tokens. Apply them while writing the body, not as a cleanup pass afterwards.

**1. Write only against the baseline.** Every section should fix a failure you recorded in Step 3. A paragraph that fixes nothing on that list is a candidate for deletion.

**2. Be concise: the context window is shared.** Every word competes with the conversation and with every other loaded skill. Assume the agent is already competent, so do not explain what JSON is, how HTTP works, or how to write a loop. Challenge each paragraph with "does this earn its place?" and cut it if the answer is no. Upstream guidance is under 500 lines and roughly 5,000 tokens for the body; the skills-il validator hard-fails at 5,000 words, which is a looser bound (Hebrew in particular costs more tokens per word). Aim for the upstream numbers and move the rest to `references/` (Step 8).

**3. Match freedom to fragility.** How specific you should be depends on how badly the task breaks when done differently.

| Task shape | Freedom | How to write it |
|---|---|---|
| Many valid approaches (reviewing content, drafting copy) | High | State the goal and the decision criteria, let the agent pick the route |
| A preferred pattern exists (report formatting, data shaping) | Medium | Give a template or a parameterized example to adapt |
| Fragile, order-dependent, or irreversible (migrations, filings, payments) | Low | Give the exact command or sequence, and say explicitly not to deviate |

Over-constraining a high-freedom task makes the skill brittle. Under-constraining a fragile one makes it dangerous.

**4. Depth over count in examples.** Step 7 requires at least two examples; within that budget prefer complete, realistic, runnable ones over fill-in-the-blank templates. Prefer real Israeli values (an actual form number, a real municipality, a realistic salary) over `<placeholder>` tokens.

**5. Write so the skill stays true and readable.**
- Avoid phrasing that silently expires ("the new rule", "before next year"). State the effective date with the value instead.
- Keep references one level deep: SKILL.md links to `references/x.md`, and that file does not send the agent on to a third file.
- Give any reference file over about 100 lines a short table of contents, so an agent that reads only the top still sees its full scope.
- Pick one term per concept and use it everywhere. Switching between synonyms makes the agent wonder whether they mean different things.

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
- `scripts/<name>.py` -- <What it does, how to run>. Run: `python3 scripts/<name>.py --help`

### References
- `references/<name>.md` -- <What it contains>. Consult when <specific situation>.

## Gotchas

- <Agent failure mode, not a user error: something an agent following this skill gets wrong>
- <A domain assumption that looks reasonable but is false>
- <A field, format, or edge case agents routinely miss>

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| <Official source> | <https URL> | <What to verify there> |

## Troubleshooting

### Error: "<Error name>"
Cause: <Why>
Solution: <Fix>
```

**Gotchas are agent failure modes, not user errors.** "The agent computes VAT on the gross amount" belongs there; "the user forgot their password" does not. They are the highest-signal lines in a skill, so draw them from the failures you recorded in Step 3.

**Troubleshooting causes must be verified.** An agent that hits the symptom will repeat the stated cause to the user as a diagnosis. If a cause is a guess, say so in the row.

**Body rules** (size and specificity are covered in Step 6.5):
- Use tables for decision matrices, field mappings, comparison data
- Reference bundled resources with "Consult when..." guidance
- Include 2-4 examples and 2-4 troubleshooting entries
- Embed Hebrew terminology inline: "installments (tashlumim)"

### Step 8: Create References and Scripts

Every skill should include reference files and helper scripts. They make the difference between a thin skill and a production-quality one.

- **References:** create 2-3 files in `references/` for detail too long for SKILL.md (directories, detailed guides, glossaries, checklists, comparison tables, templates). Keep each under 3,000 words, use headers and tables, include Hebrew terms in parentheses, and link each from SKILL.md with "Consult when..." guidance.
- **Scripts:** create 1-2 Python helpers in `scripts/` for calculations or lookups. Use a `#!/usr/bin/env python3` shebang, argparse with `--help`, a usage docstring, stdlib only, input validation with clear errors, and clean output. A script should handle its own errors rather than punting them to the agent.

Common reference and script patterns, with example filenames, are in `references/skill-spec.md`.

**Update SKILL.md:** Add a `## Bundled Resources` section (before `## Troubleshooting`) listing all references and scripts with "Consult when..." guidance.

**Update SKILL_HE.md:** Add a matching `## משאבים מצורפים` section with Hebrew descriptions.

**Recommended MCP Servers (when one exists):** if a published MCP server in the directory supplies data or actions your instructions rely on, add a `## Recommended MCP Servers` table (`| MCP | What It Adds |`, linking to its directory page) after `## Bundled Resources`, and a matching `## שרתי MCP מומלצים` in SKILL_HE.md. Do not use the retired `mcp-server` frontmatter key.

### Step 8.5: Add Reference Links Section

Every skill MUST include a `## Reference Links` section (after `## Recommended MCP Servers` or `## Bundled Resources`, before `## Troubleshooting`) with a table of official source URLs used to verify the skill's domain-specific facts.

Use the table shape from the Step 7 template (`| Source | URL | What to Check |`).

**Guidelines:**
- Include 3-6 authoritative links (government sites, official API docs, legal databases)
- Each link should have a "What to Check" column explaining what to verify there
- Prefer `.gov.il`, `.org.il`, and institutional sources over blogs
- Include at least one English-language source when available
- The Hebrew companion must have a matching `## קישורי עזר` section

These links let users, and anyone updating the skill later, re-verify every claim against its source.

### Step 9: Create the Hebrew Companion (SKILL_HE.md)

Create SKILL_HE.md with the same structure but in Hebrew:
- Translate the body instructions to Hebrew
- Keep code blocks, field names, and API references in English
- Use Hebrew-native terminology (not transliterations)
- Maintain the same step numbering and section structure, and translate every section heading (the validator catches common ones such as `## Examples` or `## Gotchas`, but not all, so also check `## Overview` and `## Legal notice` yourself)

The Hebrew file uses the same frontmatter as SKILL.md (frontmatter stays in English).

### Step 9.5: Validate All Links (MANDATORY)

Before running the validator, verify that every URL in the skill actually resolves.

Extract every URL from every file in the skill folder (including `scripts/` and `references/`) and check that each returns HTTP 200. The two commands, and what to do for each non-200 status, are in `references/submission-checklist.md`. Give extra attention to `.gov.il` URLs, `.co.il` startup domains, and the Reference Links table. A 403 is often bot-blocking: open the page in a browser before calling it broken.

**Do NOT proceed to Step 10 with broken links.** Fix every broken URL first.

### Step 10: Validate and Prepare for Submission

Run the validator from the **repo root** (it lives at the repo's `scripts/validate-skill.sh`, not in your skill's own `scripts/` folder):

```bash
./scripts/validate-skill.sh <skill-name>/SKILL.md
```

It needs PyYAML (`pip install pyyaml`); without it the YAML check is skipped with a NOTICE and CI may still reject the skill. Beyond the naming, description, word-count, README and secrets checks, it also fails on frontmatter that does not parse as YAML, a description over 1023 characters including quotes, a missing `SKILL_HE.md`, and untranslated English headings in `SKILL_HE.md`. It warns when the Hebrew body exceeds 5,000 words or its heading count differs from SKILL.md. The full rule table with fixes is in `references/submission-checklist.md`.

**The validator is structural only.** An untouched scaffold passes it. Before submitting, `grep -rn TODO <skill-name>/` must print nothing, no `[...]` template placeholder may remain, and every item below is a manual check:
- [ ] Baseline recorded, and every section fixes an observed failure (Step 3)
- [ ] Domain facts verified against official sources (Step 4)
- [ ] Regulated-domain screen done; if it applies, a Legal notice section sits right after the H1 in both files (Step 4.5)
- [ ] All URLs return HTTP 200 (Step 9.5)
- [ ] Description includes WHAT and WHEN, is in the third person, and is 1023 characters or fewer including quotes
- [ ] Gotchas describe agent failure modes, not user errors
- [ ] Instructions are specific and actionable
- [ ] Examples cover 2+ real scenarios
- [ ] Troubleshooting covers likely errors
- [ ] Reference Links section with 3-6 verified official source URLs
- [ ] Hebrew companion exists and section structure matches SKILL.md 1:1 (including `## קישורי עזר`)
- [ ] At least 2 reference files in `references/` with "Consult when..." guidance
- [ ] At least 1 helper script in `scripts/` with argparse and `--help`
- [ ] No security issues (secrets, injection vectors)
- [ ] `supported_agents` includes only agents whose happy path works, and `compatibility` agrees with it
- [ ] `metadata.version` is set (e.g., 1.0.0)
- [ ] `metadata.tags` has both `he` and `en` arrays of equal length with no empty strings
- [ ] `creator_name` and `creator_email` collected from user (Step 2), and `author` is a real GitHub login
- [ ] Repo-level README.md is written in English (not Hebrew)

### Step 10.5: Pre-Submission GitHub Verification Setup

The submission form runs a live GitHub Verification scorecard against your repo, so set the signals up before you submit.

The five Critical signals are `spec_compliant` (run `gh skill publish --dry-run`, GitHub CLI 2.90.0 or later), `secret_scanning`, `code_scanning`, `signed_release` (a tag-triggered release workflow with build-provenance attestation), and `license_spdx` (a root `LICENSE` file). A quick-setup row for each is in `references/submission-checklist.md`; full copy-paste steps are in the [GitHub Verification checklist guide](https://agentskills.co.il/en/guides/github-verification-checklist). For an MCP server, `spec_compliant` does not apply.

Approval is refused unless all five pass; the rejection email names the failing signals.

### Step 11: Submit Your Skill

After validation passes, submit your skill through the [submission page](https://agentskills.co.il/en/submit).

1. Choose submission type: "Existing Repository" (if you pushed your skill to a GitHub repo) or "Proposal" (if you want the skills-il team to create the repo)
2. Fill in the form with: your GitHub repo URL, creator name, and creator email (from Step 2)
3. The form fetches your SKILL.md and shows pass/fail for each Critical signal. Fix any failure per Step 10.5 and re-submit.
4. The skills-il team will review your submission, run security analysis, and publish it if it passes

## Examples

### Example 1: Create a Government Services Skill

User says: "I want to create a skill for querying Israeli court decisions"

Actions:
1. Category: government-services
2. Creator info: Ask for GitHub username and email
3. Use cases: search by case number, search by judge name, search by topic (Hebrew legal terms)
4. Fact-check: Verify court system structure, Nevo access methods, citation formats via official sources. Regulated-domain screen: finding and citing published rulings explains the law, so no notice is needed unless the skill starts assessing the user's own case
5. Scaffold: `python3 <path-to-skills-il-skill-creator>/scripts/scaffold-skill.py --name israeli-court-decisions --category government-services --author <github-login>`
6. Frontmatter: name=israeli-court-decisions, author=creator_name, triggers include "psakei din", "beit mishpat", "nevo"
7. Instructions: Steps for search types, result parsing, citation format
8. References: `references/court-hierarchy.md` (court levels), `references/citation-format.md` (Israeli legal citation rules)
9. Hebrew: SKILL_HE.md with native legal terminology
10. Validate: `./scripts/validate-skill.sh israeli-court-decisions/SKILL.md`
11. Submit via the [submission page](https://agentskills.co.il/en/submit)

Result: Complete skill ready for the Skills IL directory.

### Example 2: Create a Developer Tool Skill

User says: "I need a skill that helps format Israeli addresses"

Actions: category developer-tools (or government-services if it centers on address lookup APIs); ask for GitHub username and email; use cases are postal formatting, mikud validation, and city-name normalization; verify mikud format rules and Israel Post API availability; scaffold with `python3 <path-to-skills-il-skill-creator>/scripts/scaffold-skill.py --name israeli-address-formatter --category developer-tools --author <github-login>`; triggers include "format ktovet" and "mikud"; add `references/mikud-format.md` and `scripts/mikud-validator.py`; write SKILL_HE.md; validate; submit.

Result: Address formatting skill with validation and postal format support.

### Example 3: Create a Skill with MCP Integration

User says: "I want to create a skill that uses the israeli-bank-mcp server"

Actions: category tax-and-finance; ask for GitHub username and email; use cases are transaction categorization, recurring-charge detection, and a monthly summary; scaffold `israeli-bank-analyzer` with `--author <github-login>`; add `## Recommended MCP Servers` to SKILL.md and `## שרתי MCP מומלצים` to SKILL_HE.md, both pointing to `israeli-bank-mcp`; instructions cover the MCP tool calls, categorization logic, and summary; add `references/bank-api-reference.md` and `scripts/transaction-categorizer.py`; validate; submit.

Result: MCP-enhanced skill that adds workflow intelligence on top of bank data access.

## Bundled Resources

### Scripts
- `scripts/scaffold-skill.py` -- Creates the complete folder structure for a new skills-il skill: SKILL.md with minimal frontmatter plus Gotchas and Reference Links stubs, a SKILL_HE.md stub with Hebrew headings, metadata.json (enriched metadata, `--author` is your GitHub login), and scripts/ and references/ directories. Validates name (kebab-case, at most 64 characters) and category, and prevents overwrites. Run: `python3 scripts/scaffold-skill.py --help`

### References
- `references/skill-spec.md` -- Complete skills-il SKILL.md specification including all frontmatter fields (required and optional), description-writing formula with good/bad examples, the 5 skill patterns from Anthropic's guide, quality checklist, and validation rules. Consult when writing frontmatter or instructions and you need detailed guidance beyond the steps above, or when choosing `supported_agents`.
- `references/submission-checklist.md` -- Link-check commands and status actions, the full validate-skill.sh rule table, and the five GitHub Verification signals. Consult when a link check, the validator, or the submission scorecard fails.
- `references/domain-checklist.md` -- What a complete skill-authoring guide must cover, with sources. Consult when reviewing or extending this skill.

## Gotchas

- Enriched metadata lives in `metadata.json`, NOT in SKILL.md frontmatter. Claude Desktop rejects a `metadata:` key in YAML frontmatter. Agents trained on older skills (or an old scaffold template) may put `version`, `tags`, `display_name`, and `supported_agents` in the frontmatter, which breaks the skill.
- `metadata.json` tags use a bilingual `tags.he` / `tags.en` structure of equal length. Agents may flatten the tags into a single array.
- Hebrew content in SKILL_HE.md must never appear inside code blocks (```) because code blocks do not support RTL rendering. Use plain text or bullet lists for Hebrew content.
- The skill description field has a dual purpose: it serves as both the YAML frontmatter description and the trigger text for agent matching. Agents may write a generic description that fails to trigger on relevant user queries.
- `metadata.json` must include `version`, `category`, bilingual `tags`, `display_name`, `display_description`, and `supported_agents`. Agents may omit required fields like `supported_agents` or `display_name`.
- Agents treat 1024 as the description limit because the spec says so. The validator stops at 1023 counted with the YAML quotes, so a quoted 1023-character value already fails.
- Agents fill `author` with the contributor's full name. It must be a GitHub login, or the creator link and avatar break.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Agent Skills specification | https://agentskills.io/specification | Frontmatter fields and limits (name, description, compatibility) |
| Anthropic skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Conciseness, degrees of freedom, progressive disclosure, evaluation-first |
| The Complete Guide to Building Skills for Claude (Anthropic, PDF) | https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf | The five skill patterns summarized in `references/skill-spec.md` |
| skills-il validator | https://github.com/skills-il/developer-tools/blob/master/scripts/validate-skill.sh | The exact checks CI runs, including the 1023 limit and the SKILL_HE.md rules |
| gh skill publish manual | https://cli.github.com/manual/gh_skill_publish | The `--dry-run` validation behind the `spec_compliant` signal |
| GitHub Verification checklist | https://agentskills.co.il/en/guides/github-verification-checklist | Setup steps for the five Critical signals |

## Troubleshooting

### Error: "Validation fails on description"
Cause: Description missing a trigger phrase, longer than 1023 characters including YAML quotes, or containing angle brackets
Solution: Ensure description includes one of: "Use when", "Use for", "Use if", "When user", "When the user". Shorten to 1023 characters or fewer counting the quotes (aim for 950). Remove any `<>` angle brackets.

### Error: "frontmatter is not valid YAML"
Cause: Almost always a plain one-line description that contains a colon followed by a space, which YAML reads as a nested key
Solution: Switch the description to the folded `>-` style, wrap it in single quotes (doubling any single quote inside it), or reword the colon to a comma. The check runs on SKILL_HE.md frontmatter too.

### Error: "missing sibling SKILL_HE.md" or "untranslated English heading(s)"
Cause: The Hebrew companion is absent, or it kept English section headings such as `## Examples` outside a code block
Solution: Create SKILL_HE.md, and translate every section heading (for example `## דוגמאות`, `## מלכודות נפוצות`, `## קישורי עזר`). Headings inside code fences are ignored.

### Error: "Name doesn't match folder"
Cause: SKILL.md `name` field differs from the folder name
Solution: The `name` field must exactly match the folder name. Both must be kebab-case. Run: `ls -la` to check folder name, compare with `name:` in frontmatter.

### Error: "Body exceeds 5,000 words"
Cause: Too much detail in SKILL.md
Solution: Move detailed documentation to `references/` files. Keep SKILL.md focused on core instructions. Link to references with "Consult `references/filename.md` for..." guidance.

### Error: "Scaffold script fails"
Cause: Folder already exists or invalid name format
Solution: Check if the skill folder already exists. Ensure name is kebab-case only (lowercase letters, numbers, hyphens). No spaces, underscores, or capitals.
