# Measurement Reference (tier semantics + token ladder)

## Context tiers (what loads when)
| Tier | Content | Billed |
|---|---|---|
| metadata | frontmatter name+description | every session, always |
| body | SKILL.md body | on every trigger (incl. false-positives) |
| conditional | references/ templates/ examples/ agents/ | only when read; needs read-conditions to be selective |
| script | scripts/ | ~zero context; executes instead of loading |
| asset | binaries | not context |

Optimization is tier-aware: a token moved from body to conditional is not
deleted — it stops being billed on triggers that don't need it. A token moved
into a script stops being billed at all.

## Token ladder (auto-selected by measure_tokens.py, always disclosed)
1. **api** — Anthropic `count_tokens` endpoint (needs ANTHROPIC_API_KEY).
   Exact for the named Claude model → label `measured`.
2. **tiktoken** — o200k_base. NOT Claude's tokenizer; Anthropic guidance says it
   undercounts Claude tokens ~15–20% on typical text (more on code/non-English).
   The harness reports raw + a Claude-adjusted range (×1.15–×1.25) → label
   `estimated`. Never present the raw tiktoken number as a Claude count.
3. **heuristic** — chars/3.5 cross-checked with words×1.3, wide interval →
   label `estimated (wide bounds)`.

Rung comparisons are invalid across rungs (see benchmark-protocol.md).

## Cost model
`cost_model.py` = input-side context cost only, per scenario (sessions ×
trigger-rate × ref-read-rate), as a RANGE per named model from the dated
pricing snapshot. It does not model output generation, retries, or latency —
those need live runs or stay projected. Cache columns assume the provider's
published multipliers and a stable prefix ≥ the model's cacheable minimum.

## Duplicate detection
Cross-file shared word-8-grams (exact set arithmetic → `measured`). High
overlap is a lead, not a verdict — semantic review decides whether the
duplication is load-bearing (R-01 vs R-10 vs deliberate variants).

Two kinds of overlap are separated out and reported as information, not findings:
- `bilingual_sibling_pairs` — `X-en.md` vs `X.md`, intentional translations.
- `compiled_bundle_pairs` — a file the body itself declares to be the all-in-one
  rendering ("For the complete guide with all rules expanded: `AGENTS.md`").
  Its overlap with each constituent is the reason it ships. Declaration needs
  BOTH the filename and a bundle marker in the same markdown section, and the
  bundle must be the larger side of the pair; an undeclared near-copy is still a
  finding.

## Reachability (the "undiscoverable" flag)
A conditional-tier file is reachable when the **owning** SKILL.md body (a nested
package root governs its own subtree) names it, names a sub-directory of depth ≥ 2
containing it, a bundled script opens it by name, or — **by documented
convention** — the body lists its stem AND shows a concrete `<dir>/<name>.<ext>`
path for that directory. Listing 70 rule stems plus one path example is cheaper
than 70 literal paths; flagging all 70 penalised the better design.
Both guards still bite: a bare `references/` mention is not a pointer (depth
guard), and a stem the body never lists is still flagged.

## What is never context
`artifact` tier: build metadata, human docs, rendered demos, and **runtime
config** — `metadata.json`, plus config-format files under `agents/`, which are
another runtime's manifest. Markdown under `agents/` is a sub-agent prompt and
stays context.

## Trigger surface
Trigger phrasing counts from a literal marker (`use when`, 触发词, `השתמש`) **or**
a semantic construction — `when <gerund>`, `when you/your`, `for <gerund>`. A bare
"when" is ordinary prose and is not accepted. When frontmatter sets
`disable-model-invocation: true` the skill never auto-triggers, so the
trigger-phrasing and negative-boundary checks are suppressed and the reason is
stated in the report's `informational` list.

## Suppressions are always stated
Every check the harness declines to apply appears in `informational` with its
reason. A suppressed finding is never silently dropped — that is how a
false-positive fix is told apart from a blind spot.

## What is NOT measurable statically
Task success · retry counts · instruction adherence · injection resistance ·
latency · reasoning-token spend. These require live runs (live_eval_adapter.py
path) or remain `projected` with cited evidence.
