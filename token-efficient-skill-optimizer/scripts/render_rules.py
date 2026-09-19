#!/usr/bin/env python3
"""Render references/rules.md + evidence matrix from rules/rules.yaml, and
cross-check integrity against the research sources file.

The .md files are GENERATED - edit rules.yaml, then re-run this.

Checks (fail -> exit 1):
  * every rule's sources[] ids exist in sources.yaml records
  * every rule has non-empty: rollback, validation_test, mechanism,
    do_not_apply_when; all four risk fields present AND an integer 0-3
  * ids unique; tier in {1,2,3,'S'}

Usage: render_rules.py [--rules rules.yaml] [--sources sources.yaml]
                       [--out-md rules.md] [--out-matrix evidence-matrix.md] [--check-only]
"""

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PROJ = SKILL.parent.parent  # .../token-efficient-skill-optimizer

TIER_TITLES = {
    1: "Tier 1 — apply in every profile (high confidence, low risk)",
    2: "Tier 2 — Balanced/Aggressive, each application test-gated",
    3: "Tier 3 — Aggressive only, explicit opt-in, mandatory benchmark",
    "S": "Safety meta-rules — always on, constrain all other rules",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default=str(SKILL / "rules" / "rules.yaml"))
    # Default to the IN-SKILL index so the citation gate works wherever the
    # skill is installed. Before v1.1.0 this defaulted to a project path that
    # does not exist under ~/.claude/skills/ - the check crashed with
    # FileNotFoundError and gate G-09 was decorative in every installed copy.
    # The project file is still accepted (and preferred when present) because
    # it carries the full records; the index carries only ids/titles/urls.
    in_skill = SKILL / "rules" / "sources-index.yaml"
    project = PROJ / "output" / "research" / "sources.yaml"
    ap.add_argument("--sources",
                    default=str(project if project.exists() else in_skill))
    ap.add_argument("--out-md", default=str(SKILL / "references" / "rules.md"))
    ap.add_argument("--out-matrix",
                    default=str(PROJ / "output" / "research" / "evidence-matrix.md"))
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    reg = yaml.safe_load(Path(args.rules).read_text(encoding="utf-8"))
    rules = reg["rules"]
    src = yaml.safe_load(Path(args.sources).read_text(encoding="utf-8"))
    src_ids = {r["id"] for r in src["records"]}
    src_by_id = {r["id"]: r for r in src["records"]}

    errors = []
    seen = set()
    for r in rules:
        rid = r.get("id", "?")
        if rid in seen:
            errors.append(f"{rid}: duplicate id")
        seen.add(rid)
        if r.get("tier") not in (1, 2, 3, "S"):
            errors.append(f"{rid}: bad tier {r.get('tier')}")
        for field in ("rollback", "validation_test", "mechanism",
                      "do_not_apply_when", "description"):
            if not str(r.get(field, "")).strip():
                errors.append(f"{rid}: empty {field}")
        # Presence is not validity. This used to check `risk not in r` only, so
        # `quality_risk: banana` passed here and the run printed "all required
        # fields non-empty" - true, and useless. A risk score is a 0-3 ordinal
        # that gates which profile may apply a rule; a non-numeric value silently
        # breaks that ordering rather than failing. validate_package.py caught
        # this one, but a gate should not rely on a different gate.
        for risk in ("quality_risk", "safety_risk", "maintainability_risk",
                     "portability_risk"):
            if risk not in r:
                errors.append(f"{rid}: missing {risk}")
            elif not (isinstance(r[risk], int) and 0 <= r[risk] <= 3):
                errors.append(f"{rid}: {risk}={r[risk]!r} is not an integer 0-3")
        for s in r.get("sources", []):
            if s not in src_ids:
                errors.append(f"{rid}: source {s} not in sources.yaml")
        if not r.get("sources"):
            # G-12: a rule may declare itself a constraint - a norm rather than an empirical
            # finding - and then it has nothing to cite.
            #
            # The exemption is enforced HERE as well as in validate_package C02, deliberately.
            # A mutation test found that honouring `rationale_type: constraint` without also
            # requiring `evidence_confidence: not-applicable` lets any empirical rule shed its
            # citations by adding one line. Checking it in only one of the two places would have
            # left that hole open wherever the other check was not run.
            if r.get("rationale_type") != "constraint":
                errors.append(f"{rid}: no sources and no `rationale_type: constraint`")
            elif r.get("evidence_confidence") != "not-applicable":
                errors.append(
                    f"{rid}: declares rationale_type: constraint but still claims "
                    f"evidence_confidence: {r.get('evidence_confidence')!r} - a norm cannot "
                    f"carry an evidence grade")

    if errors:
        print(f"CROSS-CHECK FAIL ({len(errors)}):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"CROSS-CHECK PASS: {len(rules)} rules, all evidence ids resolve, "
          f"all required fields present and well-typed")
    if args.check_only:
        return

    # ---------------- rules.md ----------------
    lines = [
        "# Optimization Rules (generated from rules/rules.yaml — do not edit)",
        "",
        f"Registry version {reg['version']}. Evidence ids resolve in "
        "`output/research/sources.yaml` (project) / `references/research-digest.md` "
        "(installed copy). Priority score formula and tier semantics are documented "
        "in rules.yaml's header.",
        "",
    ]
    for tier in (1, 2, 3, "S"):
        tier_rules = [r for r in rules if r["tier"] == tier]
        if not tier_rules:
            continue
        if tier != "S":
            tier_rules.sort(key=lambda r: -float(r["priority"]["score"]))
        lines.append(f"## {TIER_TITLES[tier]}")
        lines.append("")
        for r in tier_rules:
            p = r["priority"]
            lines += [
                f"### {r['id']} · {r['name']}  (score {p['score']})",
                "",
                r["description"].strip(),
                "",
                f"- **Mechanism:** {r['mechanism']}",
                f"- **Target:** {r['target']}",
                f"- **Apply when:** {r['applies_when']}",
                f"- **Do NOT apply when:** {r['do_not_apply_when']}",
                f"- **Expected benefit:** {r['expected_benefit']}",
                f"- **Risks (0-3):** quality {r['quality_risk']} · safety "
                f"{r['safety_risk']} · maintainability {r['maintainability_risk']}"
                f" · portability {r['portability_risk']}",
                f"- **Evidence:** {', '.join(r['sources'])} "
                f"({r['evidence_confidence']}) · contra: {r['contradicting_evidence']}",
                f"- **Validation:** {r['validation_test']}",
                f"- **Rollback:** {r['rollback']}",
                "",
            ]
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out_md}")

    # ---------------- evidence matrix ----------------
    m = ["# Evidence Matrix — rule × source (generated by render_rules.py)", "",
         "| Rule | Tier | Sources (id · short title · confidence class) |",
         "|---|---|---|"]
    for r in rules:
        cells = []
        for s in r["sources"]:
            rec = src_by_id[s]
            cells.append(f"{s} · {rec['title'][:60]} · "
                         f"{rec.get('source_type', '?')}")
        m.append(f"| {r['id']} {r['name']} | {r['tier']} | {'<br>'.join(cells)} |")
    m += ["", "## Sources never cited by a rule", ""]
    cited = {s for r in rules for s in r["sources"]}
    uncited = sorted(src_ids - cited)
    m.append(", ".join(uncited) if uncited else "(none)")
    m.append("")
    Path(args.out_matrix).write_text("\n".join(m), encoding="utf-8")
    print(f"wrote {args.out_matrix}")


if __name__ == "__main__":
    main()
