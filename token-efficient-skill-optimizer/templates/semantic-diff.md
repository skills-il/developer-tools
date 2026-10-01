# Semantic Diff — <target> (<date>, profile <name>)

One record per change, in application order. Status ∈ kept / modified / rolled-back.

---
## Change <N> — <R-XX rule name> — <status>
- **Files/spans:**
- **Original:**
  > <verbatim or tight excerpt>
- **Revised:**
  > <verbatim or "removed; canonical copy at <path>">
- **Why (mechanism):** <one line + rule id>
- **Evidence:** <S-ids + confidence class>
- **Expected impact:** <tokens/cost with label>
- **Risks considered:** <quality/safety/maintainability + why acceptable>
- **Behavior preserved because:** <argument; for safety-adjacent spans, explicit>
- **Validation performed:** <test + result>
- **Rollback:** <how to undo this one change>
