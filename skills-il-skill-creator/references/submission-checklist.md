# Submission Checklist: Links, Validator, GitHub Verification

Mechanical detail behind Steps 9.5, 10 and 10.5 of the skill. Consult it when a link check, the validator, or the submission scorecard reports a failure.

## Contents

1. Link validation (Step 9.5)
2. What validate-skill.sh checks (Step 10)
3. GitHub Verification signals (Step 10.5)

## 1. Link validation (Step 9.5)

Extract every URL from every file in the skill folder, including `scripts/` and `references/`:

```bash
grep -rEoh 'https?://[^ )>"'\'']+' <skill-name>/ | sort -u > /tmp/<skill-name>-urls.txt
```

Check each one:

```bash
while IFS= read -r url; do
  status=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$url" 2>/dev/null)
  [ "$status" != "200" ] && echo "[$status] $url"
done < /tmp/<skill-name>-urls.txt
```

No output means every link returned 200. Otherwise:

| HTTP status | Action |
|---|---|
| 301 / 302 | Replace the URL with the final redirect destination |
| 403 | Often bot-blocking, common on gov.il and kolzchut. Open it in a real browser. If the page renders, keep the link |
| 404 | Broken. Find the current URL or remove the link |
| 5xx | Retry once. If it still fails, note it and recheck before submitting |
| Timeout / DNS failure | If the domain no longer resolves, remove every reference to it |

A 200 is not proof you reached the right page. Some sites answer 200 with an empty shell or a homepage redirect, so confirm the page actually contains what the skill cites.

Pay special attention to `.gov.il` URLs (government sites restructure often), `.co.il` startup domains, and the Reference Links table, which is the most visible set of links.

## 2. What validate-skill.sh checks (Step 10)

Run it from the **repo root**, not from inside the skill folder. In a category repo the script lives at `scripts/validate-skill.sh`, a different directory from your skill's own `scripts/`. In your own repo, download it first:

```bash
mkdir -p scripts && curl -sL https://raw.githubusercontent.com/skills-il/developer-tools/master/scripts/validate-skill.sh -o scripts/validate-skill.sh && chmod +x scripts/validate-skill.sh
```

```bash
cd <category-repo>
./scripts/validate-skill.sh <skill-name>/SKILL.md
```

### Errors (block CI)

| Check | Common fix |
|---|---|
| File is named exactly `SKILL.md` | Fix the case |
| File starts with `---` | Add YAML frontmatter |
| Frontmatter parses as YAML, in SKILL.md and in SKILL_HE.md if it has frontmatter | Most often a plain one-line description containing `: `. Use the folded `>-` style, wrap the value in single quotes, or reword the colon to a comma. Needs PyYAML installed locally; without it the check is skipped with a NOTICE |
| `name` is kebab-case and matches the folder | Fix the name or rename the folder |
| No "claude" or "anthropic" in `name` | Choose another name |
| `description` present, at most 1023 characters counted WITH any surrounding YAML quotes, includes a trigger phrase, no angle brackets | Shorten it. Aim for 950 or fewer |
| No angle brackets anywhere in frontmatter | Remove them |
| SKILL.md body at most 5,000 words | Move detail to `references/` |
| A sibling `SKILL_HE.md` exists | Create it. Without it the Hebrew page silently shows the English body |
| No untranslated English section headings in SKILL_HE.md, outside code fences. Only a fixed list is checked: Instructions, Examples, Bundled Resources, Scripts, References, Recommended MCP Servers, Gotchas, Reference Links, Troubleshooting | Translate them. Check other headings yourself (for example `## Overview`, `## Legal notice`) |
| No README.md inside the skill folder | Delete it |
| No hardcoded secrets anywhere in the skill folder | Remove keys and tokens |

### Warnings (do not block, fix anyway)

| Check | Why |
|---|---|
| SKILL_HE.md body at most 5,000 words | Same cap as English. Expected to become an error |
| SKILL_HE.md has the same number of `##` / `###` headings as SKILL.md | A mismatch usually means a fix landed in one language only |

The validator is structural only: an untouched scaffold, still full of TODO placeholders, passes it. It never validates metadata.json (only the secrets scan touches it) and does not check for Gotchas, Reference Links, tags, or the author. Before submitting, `grep -rn TODO <skill-name>/` must print nothing, and no `[...]` template placeholder (such as `[triggers]`) may remain.

Trigger phrases the description check accepts (case-insensitive): `use when`, `use for`, `use if`, `when user`, `when the user`.

## 3. GitHub Verification signals (Step 10.5)

The submission form runs a live scorecard against your repo. All 5 Critical signals must pass for approval.

| # | Signal | Quick setup |
|---|---|---|
| 1 | `spec_compliant` | Install GitHub CLI 2.90.0 or later and run `gh skill publish --dry-run` in your repo. Fix every error it reports. `gh skill` is in public preview |
| 2 | `secret_scanning` | Repo Settings, Code security and analysis: enable **Secret scanning** and **Push protection** |
| 3 | `code_scanning` | Same page, under **Code scanning**: **Set up**, then **Default** |
| 4 | `signed_release` | Add `.github/workflows/release.yml` that runs `actions/attest-build-provenance@v4` on `tags: ['v*']` (or call `skills-il/release-workflow@v1` as a reusable workflow), then push a `v1.0.0` tag |
| 5 | `license_spdx` | Add a `LICENSE` file at the repo root with a recognized SPDX license (MIT is standard) |

For an MCP server `spec_compliant` does not apply, since `gh skill` validates SKILL.md only. The other four still do.

Full copy-paste steps: https://agentskills.co.il/en/guides/github-verification-checklist
