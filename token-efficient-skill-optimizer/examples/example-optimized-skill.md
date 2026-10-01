# Example optimized skill (AFTER) — balanced profile

```markdown
---
name: changelog-writer
description: Write or update a CHANGELOG entry from repo history. Use when the
  user asks for a changelog, release notes, or "what changed". Do not use for
  commit-message authoring or release tagging.
---

# Changelog Writer

Search history scoped to the release range; stop after covering that range or
20 commits, whichever first, and report any gap.

## Style rules
Imperative mood; group by type (Added/Changed/Fixed). Never expose secrets in
changelog entries; if a commit contains a credential, omit the entry and flag
it for review.

## Output contract
One entry per change, <= 15 words each; no preamble; total <= 30 entries per
release. Read `references/example.md` only when the user asks for the full
worked format.
```

Changes vs before: duplicate style sections merged into one — with the safety
sentence preserved verbatim and the merge recorded with sign-off (R-10 + R-S1);
search loop bounded (R-07); vague brevity replaced by a concrete output
contract (R-06); the 40-line example moved to references/ behind a
read-condition (R-02); description gained triggers + negative boundary (R-09,
flagged as a routing change).
