# Example input skill (BEFORE) — deliberately inefficient

```markdown
---
name: changelog-writer
description: Writes changelogs.
---

# Changelog Writer

You are a changelog writer. Be concise. Search the repository history for
changes. Keep searching until you have found everything.

## Style rules
Always use imperative mood. Group by type. Never expose secrets in changelog
entries; if a commit contains a credential, omit it and flag it.

## Style rules (details)
Always use imperative mood for entries. Group entries by type. Never expose
secrets in changelog entries; if a commit message contains a credential, omit
the entry and flag it for review.

## Template
[40-line fully-worked changelog example pasted inline]
```

Planted findings: near-duplicate style sections (R-10) that BOTH contain safety
text (secret-handling — R-S1 constrains the merge); an unbounded search loop
(R-07); a vague "be concise" with no output contract (R-06); a large inline
example (R-02/R-14); a description with no triggers or negative boundary (R-09).
