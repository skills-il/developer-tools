# Refresh Evidence Protocol

Precondition: live web access. Without it, state that the evidence base cannot
be considered current and STOP. Never silently reuse a stale snapshot as
current; never "refresh" from memory.

## 1. Pricing snapshot (config/provider-cost-profiles.yaml)
- Fetch the official Anthropic pricing page and OpenAI pricing page (URLs in
  the file's snapshot block).
- Record rates VERBATIM with the new snapshot_date; null for unpublished
  values — never derive or guess a rate.
- If model lineups changed (new/retired models), update rows; keep api_model_id
  null until the API id is confirmed by an official source.
- Note in CHANGELOG.md: old date → new date, material rate changes.

## 2. Provider behavior
Re-check cache multipliers, TTLs, minimum cacheable prefix sizes, batch
discounts — these gate rules R-05/R-15's arithmetic.

## 3. Research base
- For each rule, check its sources' status: preprint → published? retracted?
  superseded? Update evidence_confidence accordingly in rules/rules.yaml.
- Sweep for major new results in the ten clusters (list in the project's
  research-report.md §1); add records to sources.yaml with the full field set
  and verified-primary status (fetch the primary page; title+authors must match).
- Re-run `scripts/render_rules.py` (regenerates rules.md + evidence matrix,
  cross-checks ids).

## 4. Version bump
Any rule-registry or pricing change bumps VERSION (minor for additions,
patch for pricing-only) with a CHANGELOG.md entry.
