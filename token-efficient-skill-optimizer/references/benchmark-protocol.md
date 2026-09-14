# Benchmark Protocol (Benchmark + Validate modes)

## Equivalence requirements
Compare like with like: same file set boundaries, same measurement method rung
(never compare an api-counted "before" with a tiktoken "after"), same
tokenizer, same pricing snapshot. State all four in the report header.

## Static layer (always available)
1. measure_tokens.py on before AND after (same flags) → two JSONs.
2. Deltas per tier (metadata / body / conditional) in bytes [measured] and
   tokens [estimated or measured per the rung used].
3. cost_model.py on both, same scenario parameters → cost ranges [estimated,
   pricing snapshot dated].
4. Per-rule attribution from the Apply change log → ablation table (which rules
   carried the savings; which saved nothing; which were rolled back).

## Report shape (templates/benchmark-report.md)
Three separated sections — never mixed:
- **Measured** — structural deltas, duplicate-pair counts, (api-rung token
  counts if a key was used). Every line has a data pointer.
- **Estimated** — tokenizer-approximated token deltas; cost ranges from the
  pricing snapshot.
- **Projected** — quality/latency/task-success statements derived from rule
  evidence, cited by S-id, with confidence class. No exceptions: without live
  runs, quality claims are projected.
Plus the mandatory **"What didn't work"** section: rules applied with ~zero
benefit, rules rolled back, findings deliberately skipped and why.

## Live layer (optional, off by default)
Requires the user's explicit budget approval. `scripts/live_eval_adapter.py`
emits a skill-creator-compatible evals.json from tests/cases.jsonl; run via
skill-creator's eval flow with N≥3 runs per configuration, aggregate mean ±
stddev. Only then may task-success/quality deltas be labeled [measured], with a
pointer to the benchmark.json. Cases where the optimized version uses MORE
tokens but succeeds more often are reported as such — end-to-end cost per
successful task is the deciding metric, not prompt size.

## Acceptance framing
An optimization "succeeded" only if: meaningful median reduction in footprint or
cost [at its honest label], no gate failures, no safety-case regressions, and
the report passes validate_report.py. If the target was already efficient, say
so — "no meaningful savings available" is a valid, reportable outcome.
