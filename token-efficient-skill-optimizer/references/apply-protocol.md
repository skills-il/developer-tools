# Apply Protocol (required procedure for the Apply mode)

## 0. Freeze
Copy the target to a frozen baseline directory (never edit the original in
place). Record its measure_tokens.py JSON as the "before".

## 1. Classify
Span-classify the target per `safety.md`. Output of this step: a list of spans
with classes; `safety` spans frozen.

## 1b. Enumerate the behavioral contract (contract IDs)
Before planning any edit, write down what the target is REQUIRED to do, one
numbered item per obligation, as `C-01`, `C-02`, … Cover at minimum:

- required outputs and their shape
- safety / authorization / refusal behavior
- tools used, side effects, retry and stopping behavior
- domain rules the user relies on
- memory, retrieval, example, and model assumptions
- explicit user constraints
- known failure modes it already handles

**A change that alters a contract item is not "mere compression."** Every change
record must name the contract IDs it touches; a change touching a `safety`-class
contract item requires the user's explicit sign-off recorded in the log, and a
change that would remove a contract item is rejected, not negotiated.

This step is cheap and it is the difference between optimizing a skill and
quietly redefining it. Adopted from the GPT/Codex reference implementation
(2026-07-25), whose §6B assigns contract IDs for exactly this reason.

## 2. Plan
Filter `rules.md` by active profile; order by priority score. For each
applicable rule, note the finding it addresses (from Analyze) and its
validation test.

## 3. Apply one rule at a time
For each rule application:
1. Edit the working copy for THIS rule only.
2. Append a JSONL record to the change log (`pilot-log.jsonl` shape):
   `{"seq": N, "rule": "R-XX", "files": [...], "spans": "...",
     "before_tokens_est": [lo, hi], "after_tokens_est": [lo, hi],
     "status": "applied"}` (token figures from re-running measure_tokens).
3. Write the per-change semantic-diff record (`templates/semantic-diff.md`
   shape): original text → revised text → why → rule id → evidence ids →
   expected impact (labeled) → risks → validation performed → verdict
   kept / modified / rolled-back.
4. Run the rule's validation test. Fail → roll back this change, set
   `"status": "rolled_back"`, keep the record (failed optimizations are
   reported, not hidden — R-S4).

## 4. Interaction ordering
When rules conflict, precedence: safety meta-rules > cache alignment (R-05) >
structure moves (R-02/R-04) > text-level edits (R-01/R-10) > aggressive
compression (R-21+). Rationale: a byte-stable prefix is worth more than a
slightly smaller unstable one (evidence S-C01/S-C02); text edits inside a block
that is about to move are wasted work.

## 5. Re-measure and gate
Run measure_tokens.py on the optimized copy (the "after"); run
`validate_report.py` on the emitted report; check `config/release-gates.yaml`.
Any gate failure blocks delivery — report the failure instead.

## 6. Deliverables of one Apply run
optimized copy · change-log JSONL · semantic-diff document · before/after
measurement JSONs · a summary that flags any trigger/description change
separately (routing behavior changed — needs user attention).
