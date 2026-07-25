# Example semantic diff — changelog-writer (balanced)

## Change 1 — R-09 trigger-boundary — kept  ⚠ routing-behavior change
- Original: `description: Writes changelogs.`
- Revised: adds explicit triggers + "Do not use for commit-message authoring…"
- Why: under-specified descriptions both under-trigger (wasted metadata tax)
  and false-fire (body loaded for nothing). Evidence: S-D10 (practitioner).
- Validation: trigger phrases fire, near-miss ("write a commit message") does
  not — reviewer walkthrough [projected]. Rollback: restore old description.

## Change 2 — R-10 consolidate-semantic-overlap — kept (with R-S1 handling)
- Original: two near-duplicate "Style rules" sections, EACH containing the
  secret-handling sentence.
- Revised: one section; the safety sentence preserved verbatim; user sign-off
  for consolidating a repeated safety line recorded in the change log.
- Behavior preserved because: union of both sections' content retained; the
  only dropped text is the repetition itself. Validation: per-merge semantic
  review — no rule appears in only-one variant. Rollback: restore both.

## Change 3 — R-07 stop-conditions — kept
- Original: "Keep searching until you have found everything."
- Revised: scoped to release range, bounded at 20 commits, gap reported.
- Why: unbounded loops are unbounded marginal cost (S-D05/S-D08).
- Validation: "empty range" edge case terminates. Rollback: remove bound.

## Change 4 — R-06 output-contract — kept
- Original: "Be concise."
- Revised: per-entry and total budgets + no-preamble ban.
- Why: output tokens are the expensive side; budgets beat vague brevity
  (S-D01/S-D03). Validation: long release still fits the entry cap.

## Change 5 — R-02 progressive disclosure — kept
- Original: 40-line worked example inline in the body.
- Revised: moved to references/example.md behind a read-condition.
- Why: example needed only when the user wants the full format; body loads on
  every trigger. Validation: pointer + read-condition present; example intact.

## What didn't work
R-14 (dropping the example entirely) skipped — no eval exists to prove the
example doesn't prevent failures; the rule's do_not_apply_when forbids
guessing.
