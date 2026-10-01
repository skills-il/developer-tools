# Changelog — token-efficient-skill-optimizer

## 1.2.1 — 2026-07-25

Test coverage only. No rule, mode, or output-contract change.

**Six `negative-trigger` cases (`T-31`–`T-36`) added to `tests/cases.jsonl`** — the split
goes 20 → 26, the pool floor 40 → 46. Every existing case asked *given that the skill fired,
did it behave?* None asked **should it have fired at all?** That is this package's own R-09
defect class: `T-07` flags a missing negative boundary in *other people's* frontmatter while
carrying no case for its own. Each new row names a distinct false-fire surface rather than
rewording one probe — lexical collision on "token" (auth credentials) and on
"optimize"/"cost" (runtime rendering, infrastructure spend), the two exclusions named in the
description (one-off wording help, authoring a new skill), and subject-matter overlap with no
artifact to audit.

**Deliberately no harmful-target row.** `H-07` owns that behaviour in the sealed holdout;
authoring a development twin after reading it would convert the holdout into training data.

**Two mechanical guards, because the six cases alone would be theatre.** Model-graded cases
cannot see the thing they depend on: the frontmatter clause that makes not-firing possible.
`description states a negative boundary (R-09)` and `description names positive triggers
(R-09)` fail the build if an optimization deletes `Do NOT use for…` or the quoted trigger
phrases to save ~40 tokens — exactly the edit G-08 exists to flag, now enforced on this
package rather than only on its targets. Without them all six cases would stay green while
the behaviour silently broke.

All four new assertions were **mutation-verified**: deleting a case, duplicating a prompt,
stripping `Do NOT use`, and stripping the quoted triggers each produced the specific expected
FAIL. Suite 100 → 104. The three load-bearing names are pinned in `REQUIRED_TESTS`.

**Honest limit, stated in `tests/README.md` and not papered over:** these cases test the
skill's behaviour once it is already in context. Whether the *host* loads it at all is decided
upstream from the description, and nothing inside the package can observe that — it needs the
agent in the loop. The guards cover the precondition, not the routing decision.

Prompted by the Skills IL catalog submission ([skills-il/developer-tools#27]
(https://github.com/skills-il/developer-tools/pull/27)), whose checklist item "verified
doesn't trigger on unrelated topics" was the first reviewer to ask for evidence rather than a
claim — and could not be ticked honestly.

## 1.2.0 — 2026-07-25

Round-2 research applied. Full evidence base and reasoning:
`research-2026-07-25/DOSSIER.md` (31 academic works + 8 institutional resources, all
verified against primary pages).

**Two behaviour changes, each in its own commit so it can be reverted alone:**

- **R-02 progressive-disclosure demoted from Tier 1 to Tier 2.** It no longer fires
  automatically under the `conservative` profile. Its only quantitative vendor support
  turned out to state 98.7% with no model, no benchmark, no methodology and no trial
  count, while this project's own measurement found relocated material read 8/8 times
  against a 74% break-even — turning a correctly measured −17.2% into +2.3% *more*
  expensive. It now requires a stated read-rate estimate and reports
  `[behavior-dependent]`.
- **`[reported]`, a sixth label**, for a number a cited source reports about its own
  experiment. The other five are all claims about the target; none could express
  someone else's measurement, and the old convention of calling those `[projected]`
  conflated a third party's result with our inference. Requires a source id.

**Evidence corrections.** Three rules cited sources that resolved but did not support
them (R-01, R-10, R-S4), and two safety rules rested on rationales nothing supported.
R-S1's "redundancy is defense in depth" is replaced by measured unpredictability —
shortening a safety prompt raised harmful compliance 20%→55% on one model while on two
others the same prompt bought 0pp and quintupled false refusals. R-S2's warrant moves
from instructional to architectural: under adaptive attack all eight published defenses
exceed 50% ASR, including the two that amount to telling a model "this is data".

**11 new rules** (R-24…R-34) covering structural-edit validation, evaluation sizing and
judge hygiene, example-pruning conditioned on model capability, the R-14↔R-05 cache
conflict, a cache-minimum guard, tokenizer portability, and output-side cost.

**Two new gates.** G-11 citation-support (coverage reported at 15/37, not asserted) and
G-12 constraint rules. New `layer:`, `source_claims:`, `conflicts_with:` fields.

97 tests (was 89), 6 of them mutations. 10/10 package checks.


## 1.0.0 — 2026-07-24

Initial release.

- 27-rule evidence-backed registry (Tiers 1/2/3 + safety meta-rules), every rule
  cited to a 42-source verified-primary research base (DEEP tier, collected
  2026-07-24).
- Measurement harness: measure_tokens.py (3-rung token ladder + tier model +
  duplicate detection, deterministic), cost_model.py (range-based, dated pricing
  snapshot 2026-07-24 for Anthropic + OpenAI), validate_report.py (mechanical
  measured/estimated/projected label enforcement).
- 8 operating modes; 3 profiles; 10 release gates.
- Test suite: 30 behavioral cases + 8 independently-authored holdout cases +
  deterministic runner (run_tests.py).
- Pilot benchmark: ARS deep-research skill (frozen copy), Apply/Balanced —
  results in the project repo's output/benchmarks/.

## 1.0.1 — 2026-07-24

Harness accuracy pass, driven by the first run against a real 29-skill portfolio.
66% of v1 flags were false positives; all seven causes fixed.

- Multilingual heuristics (EN/ZH/HE) for trigger phrasing, negative boundaries,
  and read-conditions. A Chinese skill was mis-flagged for both.
- New `artifact` tier: text that is not model context (demos/, dist/, package*.json,
  README*, LICENSE, CHANGELOG, PROVENANCE.md). Excluded from the context surface
  and from reachability flags.
- Executables (.py/.js/.mjs/.sh/.ts) are script tier in any directory.
- Bilingual sibling files (X-en.md vs X.md) reported separately from duplication.
- Duplicate detection scoped to context tiers only.
- Reachability now also satisfied by a bundled script naming the file, or by a
  sub-directory pointer; flag reworded as a heuristic requiring verification.
- validate_report.py: latency units only count next to a digit; data-pointer
  paths no longer swallow the opening backtick.

## 1.0.2 — 2026-07-24

Test hardening, found by running the optimizer on itself. The v1.0.1 harness
fixes had shipped with no coverage: the suite was schema-only and would have
stayed green if any of them regressed.

- Suite 18 -> 44 tests. Five behavioral fixtures (zh-skill, he-skill,
  artifact-skill, bilingual-skill, script-reach-skill) pin each harness
  behavior; added validator edge cases and a cost_model smoke test.
- The two regression assertions that caught the v1.0.1 near-miss (an
  over-correction that silently suppressed every reachability finding) are
  now permanent tests instead of ad-hoc shell checks.
- Verified by mutation testing, not by passing: 16/16 deliberate breakages
  are caught. Four rounds of mutation found four tests that proved nothing.
- Harness fix: NON_CONTEXT_DIRS now matches at any depth, so a nested
  `.../demos/` is an artifact rather than context.

## 1.1.0 — 2026-07-25

First public release. Merges the strongest ideas from an independently-built
second implementation of this same skill, commissioned from the same brief.
Six adoptions, seven documented rejections. Several changes ADD tokens; that is
the correct trade under the stated priority order and is published as a cost.

**Defect fix — the reason this release exists.** `render_rules.py` defaulted
`--sources` to a project-relative path, so in an installed copy the citation
cross-check died with `FileNotFoundError`. Gate G-09 "no fabricated sources"
was decorative in every installed copy — precisely where the skill runs. The
package now ships `rules/sources-index.yaml` and the gate resolves standalone.
Verified from an orphan copy with no parent project.

- `validate_package.py`: the ten release gates are now mechanically enforced
  (required paths, rule schema, citation integrity, test hygiene, hardcoded
  gate booleans, safety tier present in every profile, secret scan, version
  consistency, dated pricing). 10/10, mutation-verified.
- Paired A/B evaluation harness: `eval_runner.py` + `eval_report.py` — seeded
  randomized schedule, provenance hashing, optional metrics defaulting to
  `None` never `0`, bootstrap CI that returns null below 5 paired observations,
  and `higher_token_cases` as a first-class output.
- Savings taxonomy widened from three labels to five, adding
  `[cache-dependent]` and `[behavior-dependent]`. A saving that exists only on
  a cache hit is a billing effect, not a token reduction.
- Effective-dated pricing: rows carry `effective_start` / `effective_end`, and
  the cost model refuses an out-of-window row by name instead of silently
  costing with a superseded rate.
- Tests split four ways — 20 development, 8 safety, 12 injection (each with a
  named vector), 8 sealed holdout. Safety and injection rows are all
  `critical: true`, so "zero critical failures" is computable. Suite 44 -> 74,
  30 mutations, 30 caught (23 from the split work, 7 from the nested-package
  harness fix below).
- Apply now enumerates the target's behavioral contract as `C-01`, `C-02`, …
  before planning edits. **Shipped unproven** — observed in only 2 of 24
  evaluated outputs.
- Harness fix: a subdirectory containing its own `SKILL.md` is treated as a
  nested package root, so its references resolve against that file. Pointed at
  its own package the harness previously emitted five reachability flags, all
  false positives; now zero, with genuinely unreachable files still flagged.
- `requirements.txt` added; tiktoken marked optional with its absence explained.

**Not established.** The paired evaluation returned no quality verdict — one
arm reconstructed stand-in targets while the other declined to, a divergence
caused by guidance issued mid-run rather than by any change under test. Both
versions passed 16/16 critical cases. See `docs/RESULTS.md`.

## 1.1.1 — 2026-07-25

Fixes a defect introduced by 1.1.0 itself.

**Four files shipped in 1.1.0 were unreachable from the body.** `SKILL.md` enumerates
what the package contains, and the 1.1.0 release added files without updating that
list — so `scripts/eval_runner.py`, `scripts/eval_report.py`,
`scripts/validate_package.py`, and `rules/sources-index.yaml` were installed but
invisible to the model. The paired A/B harness was 1.1.0's headline capability and
could not be discovered; `sources-index.yaml` is the file that fixed 1.1.0's own
headline defect.

This is the same failure class this skill flags in other people's packages: not waste
you can delete, but a capability you believe you shipped that the model can never
reach. The harness did not catch it because its reachability check covers context
files and scripts are a separate tier — the practical consequence is identical.

- `SKILL.md`: the four names added to `## Bundled resources`, each with the clause a
  reader needs to know when to reach for it. **Costs +103 to +111 tokens on the
  trigger path (+4.7%) [estimated]** — measured, not guessed; the first draft of this
  entry claimed "roughly 30" and the harness disproved it. Published as a cost:
  wiring in an undiscoverable reference always adds tokens on every invocation, and
  is still correct, because the alternative is silent capability loss.
- **New guard test**: every file under `scripts/`, `config/`, `rules/`, `templates/`,
  `references/`, and `examples/` must be named somewhere in `SKILL.md`. It failed on
  all four files before the fix and names the offenders in its failure message.
  Mutation-verified. Suite 74 -> 75.
- `tests/README.md` rewritten for the four-way split — it still described 30 cases in
  one file and never mentioned `safety.jsonl` or `injection.jsonl`.
- CHANGELOG 1.1.0 corrected: the suite went 44 -> 74 with 30 mutations, not 44 -> 68
  with 23. The entry had contradicted its own harness-fix bullet three lines below.

## 1.1.2 — 2026-07-25

Harness accuracy pass #2, driven by running the tool against three of the most-
installed public Claude skills (vercel-labs/react-best-practices,
anthropics/frontend-design, mattpocock/improve-codebase-architecture). It emitted
**149 findings of which ~2 were actionable**. Five false-positive classes, all
fixed, all mutation-verified.

- **Convention-based reachability (69 of the 149).** A body that lists 70 rule
  *stems* and documents the path shape once (`rules/async-parallel.md`) has told
  the model how to open every one of them — and doing it that way costs fewer
  tokens than 70 literal paths, so the old behavior penalised the better design. A
  file is now reachable when its stem appears in the body as a whole token AND the
  body shows a concrete `<dir>/<name>.<ext>` path for its directory. Both guards
  survive: the depth guard (a bare `references/` is not a pointer) is untouched,
  and `rules/_sections.md` / `rules/_template.md` — whose stems the body never
  lists — are still flagged.
- **Documented compiled bundles (72 pairs).** `AGENTS.md` overlaps every rule file
  85–95% and the body says so ("## Full Compiled Document"). Those pairs move to
  `compiled_bundle_pairs` (informational). Declaration requires the filename AND a
  bundle marker in the same markdown section, with filenames masked first —
  `bundle-barrel-imports.md` contains the literal word "bundle" and declared
  itself a bundle on the first run of the check.
- **`disable-model-invocation: true`.** The author turned auto-trigger off; the
  trigger-phrasing and negative-boundary checks describe a surface that does not
  exist. Both suppressed, reason stated in `informational`.
- **Semantic trigger phrasing.** "…when building new UI or reshaping an existing
  one" IS a trigger. `when <gerund>`, `when you/your` and `for <gerund>` now
  count. A bare "when" does not, and a stop-list keeps "for anything" from
  reading as a gerund.
- **Runtime config misclassified as context.** `metadata.json` and config-format
  files under `agents/` are shipped for another runtime and never loaded into
  context. Now `artifact` tier. Markdown under `agents/` is a sub-agent prompt and
  deliberately stays context — excusing the whole directory would trade one
  false-positive class for a blind spot.
- **New report keys**: `informational` (every suppression, with its reason — a
  suppressed check is never silently dropped), `compiled_bundle_pairs`,
  `declared_bundles`. Both printed by the CLI.
- Adjacent fix: the frontmatter description terminator was `^\w+:`, which cannot
  match a HYPHENATED next key, so `disable-model-invocation: true` was being
  swallowed into the measured description. Now `^[\w-]+:`; indented YAML block
  scalars are unaffected.
- Result on the three targets: react-best-practices 144 → 3 findings,
  frontend-design 2 → 1, improve-codebase-architecture 3 → 0. Every genuine
  finding survives: both missing negative boundaries, and both unreferenced
  scaffold files.
- **13 new tests** over 5 new fixture packages, plus 17 mutations run (`M1`–`M17`,
  all caught, including 2 that re-assert the pre-existing depth guard and
  nested-package-root logic). One new test — "an undeclared overlapping pair is
  still a duplication finding" — was **not** covered by the first 16 mutations and
  had never been seen to fail; `M17` was added to break it. Suite 75 → 88.

## 1.1.3 — 2026-07-25

Two gates that could pass while proving nothing. Found by contrast with an
external review of an unrelated project, which named the first defect there.

**The suite did not fail closed.** The aggregate was computed purely from the
tests that happened to run — `len(RESULTS)`. Delete a test, rename it, or let
an exception skip an entire block, and the suite printed a smaller "N/N passed"
and exited 0. Verified rather than theorised: neutralising 21 assertions
produced `== 67/67 passed ==` with exit code 0. A green result that cannot
distinguish "everything passed" from "most of it never ran" is not a gate, and
this package's entire claim is that its tests discriminate.

- New `REQUIRED_TESTS` inventory: 18 name substrings covering the honesty gate,
  registry and package integrity, the four behavioural splits and their
  invariants, both historical near-miss regressions, the cost model, and the
  eval harness. Any one missing fails the run and names itself.
- Deliberately name substrings rather than a count floor. A count only catches
  deletion; it cannot catch a mandatory test being renamed into something that
  no longer asserts what it claimed.
- **The first version of this guard was itself broken, and mutation testing
  caught it.** It reported missing tests through `t()` — the same function the
  mutation suppressed — so a run could print FAIL CLOSED and still exit 0. The
  guard now reports and exits independently of `RESULTS`. A guard that depends
  on the mechanism it polices is not a guard.
- Mutation-verified three ways: suppress a subset of tests, rename a mandatory
  test, suppress every test. All three now exit 1; the clean tree still exits 0
  at 88/88.

**`render_rules.py` checked presence, not validity.** All four risk fields were
checked with `risk not in r`, so `quality_risk: banana` passed and the run
printed "all required fields non-empty" — true, and useless. A risk score is a
0-3 ordinal that gates which profile may apply a rule; a non-numeric value
silently breaks that ordering instead of failing. Now type- and range-checked,
and the success message says "present and well-typed" rather than overstating.
`validate_package.py` already caught this case, but a gate should not depend on
a different gate to be correct.

## 1.1.4 — 2026-07-25

The release gate could not see a *new* safety failure. Found by an independent
review of this repository (Codex under `os/codex-bridge`, verified by Claude);
the finding and the two it was ranked against are recorded in
`output/audits/REVIEW_v1.1.3_codex_2026-07-25.md` in the project repo.

**The safety gate compared counts, not identities.**

```python
new_critical = max(0, cand_crit - base_crit)   # before
```

Baseline critically fails case A; the candidate fixes A and critically fails
case B. Both totals are 1, so `new_critical` was 0 and `safety_gate` reported
**pass** while a brand-new safety regression shipped. The gate that exists to
stop a safety-weakening optimization was blind exactly where the risk is
highest: a candidate that *trades* one safety failure for another.

- The gate now compares the **sets** of `(case_id, trial)` pairs that failed
  critically, and fails on any identity present in the candidate and absent
  from the baseline — regardless of totals. Counts are still reported, because
  they are informative, but they no longer decide anything.
- **Fail-closed on an unpaired failure.** A case the candidate fails critically
  and the baseline has no record for counts as new: nothing shows it was
  pre-existing, so it is not assumed to be.
- `release_gate` gained `new_critical_cases` and `fixed_critical_cases`, and the
  text report names both. Counts alone hid the swap; naming the cases is what
  makes the gate auditable — and `fixed_critical_cases` means a genuine
  improvement is still visible rather than being silently netted out.
- `tests/…` — new `REQUIRED_TESTS` entry and a regression test whose fixture has
  **equal** critical-failure totals on both sides, which is precisely what a
  count-based gate cannot distinguish from no regression. **Verified by
  mutation, both directions:** reverting the gate to `max(0, cand - base)` makes
  the new test fail with `gate='pass'`; deleting the test makes the run print
  `FAIL CLOSED` and name it. 89/89 with the fix, 88/89 with the mutation.

Not addressed in this patch, and still open — from the same review: numeric
Markdown table rows bypass the honesty gate (a table is this package's own
report shape); `eval_report.py` hard-codes `[measured]` on every metric line
including `n == 0`; one existing file under `## Harness data` authorizes every
`[measured]` claim in a document; and tier classification marks any `README.md`
as a free artifact even when `SKILL.md` instructs the model to read it.
