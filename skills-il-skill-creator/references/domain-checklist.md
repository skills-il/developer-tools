# Domain Checklist: Agent Skill Authoring

Canonical coverage list for a skill that teaches contributors how to author agent skills for skills-il. Use it as the coverage anchor when reviewing or extending this guide.

## Must cover (core)

| Item | Why it is core | Source |
|---|---|---|
| YAML frontmatter with `name` + `description` | The two required fields; a skill without them does not load | [Anthropic skill structure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| Description as the triggering mechanism (WHAT + WHEN + anti-trigger) | The agent selects among many skills using the description alone, before reading the body | Anthropic best-practices, "Writing effective descriptions" |
| Description written in third person, at most 1023 chars including YAML quotes (spec max 1024) | Injected into the system prompt; inconsistent POV degrades discovery. The skills-il validator caps at 1023 because Gemini Spark rejects a description at the 1024 boundary | Anthropic best-practices; [Agent Skills spec](https://agentskills.io/specification); skills-il `validate-skill.sh` |
| `name` at most 64 chars, no leading, trailing, or consecutive hyphens | Upstream spec constraint; a longer name is not spec-compliant | [Agent Skills spec](https://agentskills.io/specification) |
| Progressive disclosure: SKILL.md body under 500 lines, overflow into `references/` | Body loads whenever the skill triggers; oversized bodies crowd out context | Anthropic best-practices, "Progressive disclosure patterns" |
| Conciseness / token economy: do not explain what the agent already knows | The context window is shared with the system prompt, history, and other skills | Anthropic best-practices, "Concise is key" |
| Degrees of freedom matched to task fragility | Over-constraining flexible tasks makes skills brittle; under-constraining fragile ones makes them dangerous | Anthropic best-practices, "Set appropriate degrees of freedom" |
| Baseline before authoring: run the task without the skill and document real failures | Prevents writing a skill that restates what the model already does correctly | Anthropic best-practices, "Build evaluations first" |
| Concrete, realistic examples (2+ scenarios) | Examples communicate desired style and depth better than description alone | Anthropic best-practices, "Examples pattern" |
| Bundled resources: `scripts/` (executed) vs `references/` (read) with explicit "consult when" guidance | Agents need to know whether to run or read a bundled file | Anthropic best-practices, "Runtime environment" |
| Gotchas section describing agent failure modes (not user errors) | Highest-signal content for agent behavior quality | skills-il convention |
| Bilingual parity: SKILL_HE.md mirrors SKILL.md heading structure | skills-il is Hebrew-first; divergent structure means Hebrew users get a different skill | skills-il convention |
| `metadata.json` with nested `tags.he` / `tags.en`, `display_name`, `supported_agents` | Claude Desktop rejects a `metadata` key in SKILL.md frontmatter; sync reads metadata.json | skills-il convention |
| Fact-grounding: verify domain facts against official sources before writing | A skill with a wrong rate or form number is worse than no skill | skills-il convention |
| Reference Links table (3-6 official source URLs) | Makes the skill's factual basis inspectable and re-verifiable | skills-il convention |
| Validation via `validate-skill.sh` before submission, run from the category-repo root, including the YAML-parse and SKILL_HE.md checks | Structural errors block CI | skills-il `validate-skill.sh` |
| Regulated-domain screen: no licensed-profession title in the name; a legal notice right after the H1 when the skill emits a work product | Israeli professional-exclusivity statutes reserve some acts and titles; the directory renders the notice above the fold | skills-il convention |
| `author` is a real GitHub login | The directory builds the creator link and avatar from it; anything else renders broken | skills-il convention |
| `supported_agents` lists only agents that can run the happy path | Upload platforms cannot be assumed to run bundled scripts; a declaration with no working path is broken by construction | skills-il convention |
| kebab-case folder naming matching the skill `name` | Sync pipeline resolves skills by folder slug | skills-il convention |

## Should cover (advanced)

| Item | Why it matters | Source |
|---|---|---|
| Avoid time-sensitive phrasing ("before August 2025, use...") | Such content silently becomes wrong | Anthropic best-practices, "Avoid time-sensitive information" |
| Keep reference links one level deep from SKILL.md | Nested references get partially read | Anthropic best-practices, "Avoid deeply nested references" |
| Table of contents for reference files over ~100 lines | Lets the agent see full scope on a partial read | Anthropic best-practices |
| Consistent terminology throughout | Mixed synonyms degrade instruction-following | Anthropic best-practices |
| Scripts should handle errors, not punt to the agent | Pre-made scripts are more reliable than generated code | Anthropic best-practices, "Solve, don't punt" |
| Recommended MCP Servers pairing where a relevant MCP exists | Upgrades a knowledge-only skill toward tool-backed | skills-il convention |
| Link validation before submission | Broken links erode trust and trip the fact-check pipeline | skills-il convention |
| Pre-submission GitHub verification setup | Feeds the trust scorecard on the public listing | skills-il convention |

## Out of scope (explicit)

Re-examined 2026-10-01. Each row still holds: a contributor would not ordinarily ask to operate these, and none has become something a contributor can do from this guide.

| Item | Rationale |
|---|---|
| Automated eval harnesses and benchmark scoring | Contributor-facing skill. Contributors establish a baseline manually (Step 3) rather than operating tooling. |
| `evidence.json` authoring | Generated during directory intake, not by the contributor. The grounding requirement is met through Step 4 fact-checking plus the Reference Links table. |
| Publishing, database seeding, cache revalidation, trust scoring | Directory operations, not contributor scope. |
| Security scanning | Runs automatically in category-repo CI. |

## Authoritative sources

| Source | URL | What to check |
|---|---|---|
| Anthropic skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Core principles, structure, progressive disclosure, degrees of freedom |
| Agent Skills specification | https://agentskills.io/specification | Supported frontmatter fields, limits |
| Claude Code skills documentation | https://code.claude.com/docs/en/skills | Skill loading and directory conventions |
