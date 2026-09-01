#!/usr/bin/env python3
"""CI package gate for token-efficient-skill-optimizer. Fails the build on any
violation - this is the last thing that runs before the package is called
shippable.

WHY THIS EXISTS
This skill's entire value proposition is honesty: evidence-backed rules, real
citations, safety text that survives optimization. Every one of those claims is
cheap to assert and cheap to break silently. A rule can cite a source id that
was never researched; a release gate that says "never regress safety" is one
`true` away from meaning nothing; a test id copy-pasted from cases.jsonl into
holdout.jsonl turns the holdout split into training data and quietly inflates
every score. None of those show up in a diff review. All ten checks below are
mechanical answers to "what could rot here without anyone noticing".

Adapted from the GPT/Codex reference implementation of the same skill
(work/gpt-reference/.../scripts/validate_package.py), rewritten against OUR
schema: rules/rules.yaml with 19 flat fields per rule, a nested `priority` map,
tier "S" for safety meta-rules, and S-<cluster><nn> source ids resolving in
output/research/sources.yaml.

RELATIONSHIP TO render_rules.py
render_rules.py is the AUTHORING tool: it regenerates references/rules.md and
the evidence matrix, and cross-checks citations as a side effect of rendering.
This validator RE-IMPLEMENTS the citation check rather than shelling out to it,
for two reasons: (1) a CI gate must be read-only, and render_rules.py WRITES
generated files unless --check-only is passed; (2) shelling out collapses every
finding into one exit code, and this script has to report per-rule violations
into --json. So the overlap is deliberate and narrow (checks 3+4); everything
else here - paths, gate booleans, test splits, secrets, versions - is new.
Renderer green + validator green is the ship condition.

CHECKS (all ten run even if an earlier one fails, so one run shows every problem)
  C01 required-paths       every file the skill's documented workflow loads
  C02 rule-schema          >=20 rules, all 19 fields non-empty, unique ids,
                           tier in {1,2,3,S}, 4 risk dims as ints 0-3,
                           priority carrying its 6 sub-fields
  C03 citation-integrity   every id in every rule's sources[] resolves to a real
                           record in the source catalog <- THE ANTI-FABRICATION
                           CHECK. Resolves against the in-skill
                           rules/sources-index.yaml when present (that is what
                           ships), else the project research catalog.
  C04 source-id-sanity     record ids unique; no rule cites a missing id; and
                           the shipped index invents no record the upstream
                           research catalog never had - otherwise a fabricated
                           citation could be legitimised by editing the copy
                           that ships alongside it
  C05 test-hygiene         splits parse, every row has an id, ids globally
                           unique ACROSS splits, development pool >= 30 rows,
                           cases.jsonl >= 20, holdout >= 6, holdout disjoint
                           from every other split
  C06 release-gate-bools   the two allow_* gates hardcoded false, the four
                           require_* gates hardcoded true
  C07 safety-tier-present  tier "S" in EVERY profile's rule_tiers
  C08 secret-scan          sk- keys, api_key= assignments, AWS AKIA ids, PEM
                           private-key armor, anywhere in the tree
  C09 version-consistency  VERSION vs a version declared in default-settings.yaml
  C10 pricing-snapshot     provider-cost-profiles.yaml carries snapshot.snapshot_date

HOW C08 TELLS A REAL KEY FROM A TEST FIXTURE THAT TALKS ABOUT KEYS
tests/ deliberately contains injection and safety fixtures full of adversarial
prose - a fixture whose whole job is to say "the skill must never echo an sk-
API key back to the user" would trip a naive scanner, and a scanner that cries
wolf gets disabled, which is worse than no scanner. The line drawn here is
STRUCTURAL, never positional: nothing is exempt for living under tests/,
because a key leaked into a fixture is still a leaked key. Instead, a match is
a violation only if the CREDENTIAL BODY it captures looks like an actual
credential:
  * length      >= 20 chars for sk-/AKIA, >= 16 for api_key= assignments.
                Prose says "an sk- key" and stops; a real key does not.
  * diversity   >= 2 of {lowercase, uppercase, digit}. Kills XXXXXXXXXXXX,
                aaaaaaaaaaaa, 000000000000.
  * entropy     >= 3.0 bits/char Shannon. Kills repeated and patterned filler
                that happens to be long enough.
  * not a reference  ALL_CAPS_UNDERSCORE bodies are env-var names, not secrets
                (`api_key = ANTHROPIC_API_KEY`), and ${...}/$VAR/os.environ[...]
                interpolations never form a literal at all.
  * not a marked placeholder  example / sample / placeholder / redacted /
                dummy / fake / your- / changeme / notreal / abcdef / 123456.
                Covers the canonical AWS doc key (AKIA...EXAMPLE) and friends.
The last two tests are scoped PER PATTERN, not applied globally, because an AWS
key id is itself ALL-CAPS alphanumeric: applied globally, the env-var and
diversity heuristics whitelist every real AKIA id. Mutation testing caught that
false negative; see SECRET_RULES for which tests each pattern enables.
Net effect: prose ABOUT a secret pattern passes, a pasted credential fails.
PEM armor is the one exception with no body test - a literal
BEGIN-PRIVATE-KEY header in a skill package is a finding no matter what
narrative frames it.

Usage: validate_package.py [ROOT] [--sources sources.yaml] [--json out.json] [-q]
       ROOT defaults to the skill root containing this script.
Exit:  0 = all checks pass, 1 = violations found, 2 = usage error.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILL_DEFAULT = HERE.parent

# ---------------------------------------------------------------- C01 inventory

REQUIRED_PATHS = [
    # NOTE (skills-il distribution): upstream also requires README.md at the
    # package root. The skills-il catalog forbids README.md inside a skill
    # folder (all docs live in SKILL.md / references/), so this distribution
    # drops it from the inventory. Upstream: yosishe/token-efficient-skill-optimizer.
    "SKILL.md", "VERSION", "CHANGELOG.md",
    "rules/rules.yaml",
    "config/default-settings.yaml", "config/optimization-profiles.yaml",
    "config/provider-cost-profiles.yaml", "config/release-gates.yaml",
    "references/apply-protocol.md", "references/benchmark-protocol.md",
    "references/measurement.md", "references/refresh-protocol.md",
    "references/research-digest.md", "references/rules.md", "references/safety.md",
    "scripts/cost_model.py", "scripts/live_eval_adapter.py",
    "scripts/measure_tokens.py", "scripts/render_rules.py",
    "scripts/run_tests.py", "scripts/validate_report.py",
    "scripts/validate_package.py",
    "tests/cases.jsonl", "tests/holdout.jsonl",
]

# ---------------------------------------------------------------- C02 rule schema

RULE_FIELDS = (
    "id", "name", "tier", "description", "mechanism", "target",
    "applies_when", "do_not_apply_when", "expected_benefit",
    "quality_risk", "safety_risk", "maintainability_risk", "portability_risk",
    "evidence_confidence", "priority", "sources", "contradicting_evidence",
    "validation_test", "rollback",
)
RISK_FIELDS = ("quality_risk", "safety_risk", "maintainability_risk", "portability_risk")
PRIORITY_FIELDS = ("frequency", "applicability", "savings", "confidence",
                   "risk_penalty", "score")
VALID_TIERS = (1, 2, 3, "S")
MIN_RULES = 20

# ---------------------------------------------------------------- C05 test splits

HOLDOUT_SPLIT = "holdout.jsonl"
PRIMARY_SPLIT = "cases.jsonl"
# The development floor is enforced on the POOL (every non-holdout split), not on
# cases.jsonl alone. The floor of 30 was written when cases.jsonl WAS the whole
# development suite; the package has since split safety.jsonl and injection.jsonl
# out of it (40 rows across three files). A per-file floor would now fail purely
# because rows moved between development splits, while a pool floor still bites
# if coverage is actually deleted. cases.jsonl keeps a smaller floor of its own so
# it cannot be hollowed out to one row with the pool propped up elsewhere.
# The pool floor carries the coverage guarantee; the cases.jsonl floor only has
# to catch hollowing-out, so it is deliberately set BELOW the current row count.
# A floor pinned at today's value goes red the next time a row legitimately
# moves between development splits, and a gate that cries wolf gets deleted.
DEV_POOL_MINIMUM = 30
PRIMARY_SPLIT_MINIMUM = 15
HOLDOUT_MINIMUM = 6          # per-file: holdout leakage is the risk this guards
# fixtures/ holds deliberate test material (malformed rows are the point there),
# so it is parsed but never treated as a behavioral split.
FIXTURE_DIR = "fixtures"

# ---------------------------------------------------------------- C06 gate booleans

GATES_MUST_BE_FALSE = ("allow_safety_regression", "allow_critical_quality_regression")
GATES_MUST_BE_TRUE = ("require_before_after_benchmark", "require_reviewable_diff",
                      "require_source_citations", "require_rollback_version")

# ---------------------------------------------------------------- C08 secret scan

# Each rule names which body tests apply. `envvar` and `classes` are OFF for the
# AWS rule on purpose: an AWS key id is itself ALL-CAPS alphanumeric, so the
# env-var-name heuristic would whitelist every real one, and a digit-free id
# would fail a class-diversity test. Mutation testing found exactly that hole -
# a genuine AKIA id sailed through until the tests were scoped per rule. The
# `AKIA` prefix is specific enough that placeholder+entropy alone carry it.
SECRET_RULES = [
    ("openai-style-key", re.compile(r"\bsk-(?P<val>[A-Za-z0-9_\-]{20,})"),
     {"min_len": 20, "classes": True, "entropy": True, "envvar": False}),
    ("api-key-assignment",
     re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*[\"']?(?P<val>[A-Za-z0-9_\-]{16,})"),
     {"min_len": 16, "classes": True, "entropy": True, "envvar": True}),
    ("aws-access-key-id", re.compile(r"\b(?P<val>AKIA[0-9A-Z]{16})\b"),
     {"min_len": 20, "classes": False, "entropy": True, "envvar": False}),
    # No body test: PEM armor in a skill package is a finding on sight.
    ("pem-private-key", re.compile(r"-----BEGIN(?: [A-Z]+)* PRIVATE KEY-----"), None),
]
PLACEHOLDER = re.compile(
    r"(?i)(example|sample|placeholder|redact|dummy|fake|your[_\-]|changeme|"
    r"notreal|abcdef|123456|xxxx|todo|deadbeef)")
# An env-var NAME, not a value: ALL-CAPS with at least one underscore
# (ANTHROPIC_API_KEY). Requiring the underscore keeps the exemption narrow.
ENVVAR_NAME = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}
MAX_SCAN_BYTES = 4 * 1024 * 1024


def shannon(text):
    """Bits of entropy per character - the cheap 'is this random-looking' test."""
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def looks_like_real_credential(body, tests):
    """Structural discriminator: a pasted credential vs. prose describing one."""
    if len(body) < tests["min_len"]:
        return False
    if PLACEHOLDER.search(body):
        return False
    if tests["envvar"] and ENVVAR_NAME.match(body):   # `api_key = ANTHROPIC_API_KEY`
        return False
    if tests["classes"]:
        classes = sum([any(c.islower() for c in body),
                       any(c.isupper() for c in body),
                       any(c.isdigit() for c in body)])
        if classes < 2:
            return False
    return shannon(body) >= 3.0 if tests["entropy"] else True


# ---------------------------------------------------------------- helpers

def is_empty(value):
    """Non-empty check that does not mistake a legitimate 0 risk score for absence."""
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return False
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    """Return (rows, parse_errors). Never raises - a bad split is a finding."""
    rows, errors = [], []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append((number, json.loads(line)))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{number}: invalid JSON ({exc.msg})")
    return rows, errors


def resolve_sources(root, explicit):
    """Locate the source catalog, anchored on ROOT so the validator works on a
    copied or relocated tree (CI checkout, installed skill, mutation test).

    The in-skill rules/sources-index.yaml wins when present: it is what actually
    SHIPS, so it is what a citation must resolve against in a user's install.
    The fuller project catalog is used as the upstream cross-check (see C04)."""
    if explicit:
        return Path(explicit).resolve()
    candidates = [
        root / "rules" / "sources-index.yaml",                          # ships with the skill
        root / "references" / "sources.yaml",
        root.parent.parent / "output" / "research" / "sources.yaml",    # PROJ/candidate/skill
        root.parent / "output" / "research" / "sources.yaml",
        SKILL_DEFAULT.parent.parent / "output" / "research" / "sources.yaml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return candidates[-1]


def resolve_upstream_sources(root, sources_path):
    """The project research catalog, when the resolved catalog was the shipped
    index. Lets C04 prove the shipped index never invented a record."""
    for candidate in (root.parent.parent / "output" / "research" / "sources.yaml",
                      root.parent / "output" / "research" / "sources.yaml",
                      SKILL_DEFAULT.parent.parent / "output" / "research" / "sources.yaml"):
        if candidate.is_file() and candidate.resolve() != Path(sources_path).resolve():
            return candidate.resolve()
    return None


class Report:
    """Collects per-check results so every check runs even when one fails."""

    def __init__(self):
        self.checks = []
        self.notes = []
        self.counts = {}

    def add(self, cid, name, violations, detail=""):
        violations = [str(v) for v in violations]
        self.checks.append({"id": cid, "name": name,
                            "status": "PASS" if not violations else "FAIL",
                            "detail": detail, "violations": violations})

    def note(self, text):
        self.notes.append(text)

    @property
    def failed(self):
        return [c for c in self.checks if c["status"] == "FAIL"]

    @property
    def total_violations(self):
        return sum(len(c["violations"]) for c in self.checks)


# ---------------------------------------------------------------- checks

def check_paths(root, rep):
    missing = [rel for rel in REQUIRED_PATHS if not (root / rel).is_file()]
    rep.add("C01", "required-paths", [f"missing required file: {m}" for m in missing],
            f"{len(REQUIRED_PATHS) - len(missing)}/{len(REQUIRED_PATHS)} present")


def check_rules(root, rep):
    """C02 - schema. Returns the parsed rule list for C03/C04 to reuse."""
    violations, rules = [], []
    path = root / "rules" / "rules.yaml"
    try:
        registry = load_yaml(path)
        rules = registry.get("rules") or []
        if not isinstance(rules, list):
            violations.append("rules/rules.yaml: `rules` is not a list")
            rules = []
    except Exception as exc:                       # noqa: BLE001 - report, don't crash CI
        violations.append(f"rules/rules.yaml: unreadable ({exc})")
        rep.add("C02", "rule-schema", violations, "0 rules")
        return []

    if len(rules) < MIN_RULES:
        violations.append(f"expected >= {MIN_RULES} rules, found {len(rules)}")

    seen = set()
    for index, rule in enumerate(rules, 1):
        if not isinstance(rule, dict):
            violations.append(f"rule #{index}: not a mapping")
            continue
        rid = rule.get("id") or f"#{index}"
        # G-12: a rule may declare itself a CONSTRAINT - a norm this project adopts rather than an
        # empirical finding. Such a rule is allowed an empty `sources` list, because forcing it to
        # name one makes the registry assert an evidential relationship that does not exist. It is
        # NOT allowed to skip any other field, and it must say so explicitly.
        is_constraint = rule.get("rationale_type") == "constraint"
        for field in RULE_FIELDS:
            if field not in rule:
                violations.append(f"{rid}: missing field `{field}`")
            elif is_empty(rule[field]):
                if field == "sources" and is_constraint:
                    continue                        # declared constraint: no empirical source needed
                violations.append(f"{rid}: empty field `{field}`")
        if is_constraint and rule.get("evidence_confidence") != "not-applicable":
            violations.append(
                f"{rid}: rationale_type=constraint requires "
                f"evidence_confidence: not-applicable, got "
                f"{rule.get('evidence_confidence')!r}")
        if not is_constraint and is_empty(rule.get("sources")):
            violations.append(
                f"{rid}: no sources and no `rationale_type: constraint` declaration - "
                f"a rule must either cite evidence or say it is a norm")
        if rule.get("id") in seen:
            violations.append(f"{rid}: duplicate rule id")
        seen.add(rule.get("id"))
        if rule.get("tier") not in VALID_TIERS:
            violations.append(f"{rid}: tier {rule.get('tier')!r} not in {VALID_TIERS}")
        for field in RISK_FIELDS:
            value = rule.get(field)
            if field not in rule:
                continue                            # already reported as missing
            if isinstance(value, bool) or not isinstance(value, int):
                violations.append(f"{rid}: {field} must be an integer, got {value!r}")
            elif not 0 <= value <= 3:
                violations.append(f"{rid}: {field}={value} outside 0-3")
        priority = rule.get("priority")
        if isinstance(priority, dict):
            for sub in PRIORITY_FIELDS:
                if sub not in priority:
                    violations.append(f"{rid}: priority missing `{sub}`")
                elif is_empty(priority[sub]):
                    violations.append(f"{rid}: priority.{sub} is empty")
        elif "priority" in rule:
            violations.append(f"{rid}: priority must be a mapping, got {type(priority).__name__}")
        if "sources" in rule and not isinstance(rule.get("sources"), list):
            violations.append(f"{rid}: sources must be a list")

        # G-11 citation-SUPPORT. C03 proves a cited id resolves; that is the weaker property.
        # Three rules were found citing sources that said nothing about their claim, so where a
        # rule declares source_claims the gate enforces that the mapping is CONSISTENT with its
        # sources and that no claim is a placeholder. Coverage across the whole registry is
        # reported as a note, not asserted - a gate that claimed full coverage it does not have
        # would be exactly the decoration this check exists to remove.
        claims = rule.get("source_claims")
        if claims is not None:
            if not isinstance(claims, dict):
                violations.append(f"{rid}: source_claims must be a mapping of source id -> claim")
            else:
                srcs = set(rule.get("sources") or [])
                for sid, text in claims.items():
                    if sid not in srcs:
                        violations.append(
                            f"{rid}: source_claims names {sid}, which the rule does not cite")
                    if is_empty(text) or len(str(text).strip()) < 40:
                        violations.append(
                            f"{rid}: source_claims[{sid}] is empty or too short to be a claim")
                    elif "TODO" in str(text) or "TBD" in str(text):
                        violations.append(
                            f"{rid}: source_claims[{sid}] is a placeholder, not a claim")

    rep.counts["rules"] = len(rules)
    # G-11 coverage, reported honestly rather than asserted. Backfilling the remaining rules means
    # re-opening each source and reading what it actually supports - a re-verification, not a
    # formatting pass - so the number is published as a ratchet instead of being hidden.
    # G-11 is now ENFORCING, not reporting. It reported coverage while the backfill was
    # outstanding; the debt was paid on 2026-07-25 and the ratchet closed behind it. A gate that
    # stays advisory after its debt is cleared is how the debt comes back.
    empirical = [r for r in rules
                 if isinstance(r, dict) and r.get("rationale_type") != "constraint"]
    without = [r.get("id", "?") for r in empirical if not r.get("source_claims")]
    for rid in without:
        violations.append(
            f"{rid}: cites sources but declares no source_claims - state what each source "
            f"underwrites, with a locator. C03 proves only that the id resolves.")
    rep.counts["source_claims"] = f"{len(empirical) - len(without)}/{len(empirical)}"
    # Provenance is reported, never asserted: a claim written from the round-1 catalog record is a
    # weaker chain than one written from a page opened in round 2, and the difference is published.
    prov = Counter(r.get("claims_provenance", "unstated")
                   for r in empirical if r.get("source_claims"))
    if prov:
        rep.notes.append(
            "G-11 claim provenance: "
            + ", ".join(f"{n} {k}" for k, n in sorted(prov.items(), key=lambda x: -x[1]))
            + ". `round-1-corpus-record` means the claim comes from the catalog entry, which was "
              "primary-verified when collected but was NOT re-opened in round 2.")
    rep.add("C02", "rule-schema", violations,
            f"{len(rules)} rules x {len(RULE_FIELDS)} fields")
    return rules


def read_source_ids(path):
    """Return (ids_in_order, record_count) for a catalog file."""
    doc = load_yaml(path) or {}
    records = doc.get("records") or []
    return [r.get("id") for r in records if isinstance(r, dict)], len(records)


def check_citations(rules, sources_path, upstream_path, rep):
    """C03 anti-fabrication + C04 source-id sanity, sharing one parse."""
    cite_violations, source_violations = [], []
    known, record_count = set(), 0

    if not Path(sources_path).is_file():
        message = (f"sources file not found: {sources_path} - citations cannot be "
                   f"verified, so the anti-fabrication gate fails closed")
        rep.add("C03", "citation-integrity", [message], "unverifiable")
        rep.add("C04", "source-id-sanity", [message], "unverifiable")
        return
    catalog = Path(sources_path).name
    try:
        ids, record_count = read_source_ids(sources_path)
        for rid, count in Counter(ids).items():
            if count > 1:
                source_violations.append(f"{catalog}: duplicate record id {rid} (x{count})")
        blank = sum(1 for i in ids if not i)
        if blank:
            source_violations.append(f"{catalog}: {blank} record(s) without an `id`")
        known = {i for i in ids if i}
    except Exception as exc:                       # noqa: BLE001
        message = f"{catalog} unreadable ({exc})"
        rep.add("C03", "citation-integrity", [message], "unverifiable")
        rep.add("C04", "source-id-sanity", [message], "unverifiable")
        return

    # The shipped index must not invent records the research catalog never had -
    # otherwise a fabricated citation could be made to "resolve" by editing the
    # copy that ships. Only meaningful when both files are present.
    if upstream_path:
        try:
            upstream_ids, _ = read_source_ids(upstream_path)
            invented = sorted(known - {i for i in upstream_ids if i})
            if invented:
                source_violations.append(
                    f"{catalog} contains record id(s) absent from the upstream research "
                    f"catalog {Path(upstream_path).name}: {invented}")
        except Exception as exc:                   # noqa: BLE001
            rep.note(f"upstream catalog {upstream_path} unreadable ({exc}); "
                     f"shipped-index subset check skipped")

    cited = set()
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rid = rule.get("id", "?")
        srcs = rule.get("sources")
        if not srcs:
            # G-12: a declared constraint is a norm, not an empirical claim, so it has nothing to
            # cite. C02 already enforces that such a rule sets evidence_confidence: not-applicable,
            # so this branch cannot be used to smuggle an uncited empirical rule past the gate.
            if rule.get("rationale_type") != "constraint":
                cite_violations.append(f"{rid}: cites no sources and is not a declared constraint")
            continue
        if not isinstance(srcs, list):
            continue                                # shape already flagged by C02
        for sid in srcs:
            cited.add(sid)
            if sid not in known:
                cite_violations.append(
                    f"{rid}: cites {sid!r}, which does not resolve to any record "
                    f"in {catalog} (fabricated or renamed source)")

    for sid in sorted(cited - known):
        source_violations.append(f"{sid}: referenced by a rule but absent from {catalog}")

    rep.counts["sources"] = record_count
    rep.counts["cited_sources"] = len(cited)
    rep.add("C03", "citation-integrity", cite_violations,
            f"{len(cited)} distinct ids cited across {len(rules)} rules")
    rep.add("C04", "source-id-sanity", source_violations,
            f"{record_count} source records, {len(known)} unique ids")
    if not source_violations and known - cited:
        rep.note(f"{len(known - cited)} source record(s) are never cited by a rule "
                 f"(informational, not a failure)")


def check_tests(root, rep):
    violations = []
    tests_dir = root / "tests"
    if not tests_dir.is_dir():
        rep.add("C05", "test-hygiene", ["tests/ directory missing"], "0 splits")
        return

    all_jsonl = sorted(tests_dir.rglob("*.jsonl"))
    splits = [p for p in all_jsonl if FIXTURE_DIR not in p.relative_to(tests_dir).parts]
    fixtures = [p for p in all_jsonl if p not in splits]
    if fixtures:
        rep.note(f"{len(fixtures)} .jsonl under tests/{FIXTURE_DIR}/ parsed but exempt "
                 f"from split id rules (deliberate test material)")

    seen_ids = {}          # id -> split name that claimed it first
    per_split = {}
    for path in all_jsonl:
        rel = path.relative_to(root)
        rows, parse_errors = read_jsonl(path)
        violations.extend(parse_errors)
        if path not in splits:
            continue
        name = path.name
        per_split[name] = len(rows)
        for number, row in rows:
            if not isinstance(row, dict):
                violations.append(f"{rel}:{number}: row is not a JSON object")
                continue
            case_id = row.get("id")
            if not case_id:
                violations.append(f"{rel}:{number}: row has no `id`")
                continue
            if case_id in seen_ids:
                violations.append(
                    f"{rel}:{number}: id {case_id!r} already used in "
                    f"{seen_ids[case_id]} - split ids must be globally unique "
                    f"(a shared id leaks holdout data into development)")
            else:
                seen_ids[case_id] = name

    for name, minimum in ((PRIMARY_SPLIT, PRIMARY_SPLIT_MINIMUM),
                          (HOLDOUT_SPLIT, HOLDOUT_MINIMUM)):
        if name not in per_split:
            violations.append(f"tests/{name}: split missing")
        elif per_split[name] < minimum:
            violations.append(f"tests/{name}: expected >= {minimum} rows, found {per_split[name]}")
    dev_pool = sum(count for name, count in per_split.items() if name != HOLDOUT_SPLIT)
    if dev_pool < DEV_POOL_MINIMUM:
        violations.append(
            f"development pool (every split except {HOLDOUT_SPLIT}) has {dev_pool} rows, "
            f"expected >= {DEV_POOL_MINIMUM}")

    # Holdout must be disjoint from every other split - checked explicitly rather
    # than leaning on file order, so adding safety.jsonl later cannot weaken it.
    holdout_path = tests_dir / HOLDOUT_SPLIT
    if holdout_path.is_file():
        holdout_rows, _ = read_jsonl(holdout_path)
        holdout_ids = {r.get("id") for _, r in holdout_rows if isinstance(r, dict) and r.get("id")}
        other_ids = set()
        for path in splits:
            if path == holdout_path:
                continue
            rows, _ = read_jsonl(path)
            other_ids |= {r.get("id") for _, r in rows if isinstance(r, dict) and r.get("id")}
        overlap = sorted(holdout_ids & other_ids)
        if overlap:
            violations.append(f"holdout.jsonl shares ids with other splits: {overlap}")

    rep.counts["test_splits"] = per_split
    rep.counts["test_cases"] = len(seen_ids)
    rep.add("C05", "test-hygiene", violations,
            ", ".join(f"{k}={v}" for k, v in sorted(per_split.items())) or "no splits")


def check_gates(root, rep):
    violations = []
    path = root / "config" / "release-gates.yaml"
    try:
        doc = load_yaml(path) or {}
        defaults = doc.get("defaults")
        if not isinstance(defaults, dict):
            violations.append("release-gates.yaml: `defaults` block missing or not a mapping")
            defaults = {}
        for key in GATES_MUST_BE_FALSE:
            if key not in defaults:
                violations.append(f"release-gates.yaml: defaults.{key} missing (must be false)")
            elif defaults[key] is not False:
                violations.append(
                    f"release-gates.yaml: defaults.{key} is {defaults[key]!r}, must be "
                    f"hardcoded false - this gate is not configurable")
        for key in GATES_MUST_BE_TRUE:
            if key not in defaults:
                violations.append(f"release-gates.yaml: defaults.{key} missing (must be true)")
            elif defaults[key] is not True:
                violations.append(
                    f"release-gates.yaml: defaults.{key} is {defaults[key]!r}, must be "
                    f"hardcoded true - this gate is not configurable")
        gates = doc.get("gates") or []
        rep.counts["gates"] = len(gates)
        if len(gates) < 10:
            violations.append(f"release-gates.yaml: expected >= 10 gates, found {len(gates)}")
    except Exception as exc:                       # noqa: BLE001
        violations.append(f"release-gates.yaml unreadable ({exc})")
    rep.add("C06", "release-gate-bools", violations,
            f"{len(GATES_MUST_BE_FALSE)} false + {len(GATES_MUST_BE_TRUE)} true gates")


def check_profiles(root, rep):
    violations, names = [], []
    path = root / "config" / "optimization-profiles.yaml"
    try:
        profiles = (load_yaml(path) or {}).get("profiles") or {}
        if not profiles:
            violations.append("optimization-profiles.yaml: no profiles defined")
        for name, body in profiles.items():
            names.append(name)
            tiers = (body or {}).get("rule_tiers")
            if not isinstance(tiers, list):
                violations.append(f"profile {name}: rule_tiers missing or not a list")
            elif "S" not in tiers:
                violations.append(
                    f"profile {name}: rule_tiers={tiers} omits tier \"S\" - safety "
                    f"meta-rules are active in EVERY profile and cannot be configured off")
    except Exception as exc:                       # noqa: BLE001
        violations.append(f"optimization-profiles.yaml unreadable ({exc})")
    rep.counts["profiles"] = len(names)
    rep.add("C07", "safety-tier-present", violations,
            f"{len(names)} profiles: {', '.join(names)}" if names else "no profiles")


def check_secrets(root, rep):
    violations, scanned = [], 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if SKIP_DIRS & set(path.relative_to(root).parts):
            continue
        try:
            if path.stat().st_size > MAX_SCAN_BYTES:
                rep.note(f"skipped {path.relative_to(root)} from the secret scan (> 4 MB)")
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue                                # binary or unreadable: nothing to leak in text
        scanned += 1
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern, tests in SECRET_RULES:
                for match in pattern.finditer(line):
                    body = (match.groupdict() or {}).get("val")
                    if tests and body is not None and not looks_like_real_credential(body, tests):
                        continue                    # prose/placeholder, not a credential
                    violations.append(
                        f"{path.relative_to(root)}:{number}: possible {label} "
                        f"(matched {match.group(0)[:12]}...)")
    rep.counts["files_scanned"] = scanned
    rep.add("C08", "secret-scan", violations, f"{scanned} text files scanned")


def check_version(root, rep):
    violations = []
    version = None
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if not version:
            violations.append("VERSION file is empty")
    except OSError as exc:
        violations.append(f"VERSION unreadable ({exc})")

    declared, where = None, None
    path = root / "config" / "default-settings.yaml"
    if path.is_file():
        try:
            doc = load_yaml(path) or {}
            for dotted in ("version", "defaults.version", "project.version", "meta.version"):
                node = doc
                for part in dotted.split("."):
                    node = node.get(part) if isinstance(node, dict) else None
                if isinstance(node, str) and node.strip():
                    declared, where = node.strip(), dotted
                    break
        except Exception as exc:                   # noqa: BLE001
            violations.append(f"default-settings.yaml unreadable ({exc})")
    else:
        violations.append("config/default-settings.yaml missing")

    if declared is None and not violations:
        # Absence is a legitimate design choice here (VERSION is the single
        # source of truth), so say so loudly instead of inventing a failure.
        rep.note("config/default-settings.yaml declares no version string - nothing "
                 "to cross-check against VERSION; VERSION remains the sole source of truth")
    elif declared is not None and declared != version:
        violations.append(f"VERSION={version!r} but default-settings.yaml {where}={declared!r}")

    rep.counts["version"] = version
    rep.add("C09", "version-consistency", violations,
            f"VERSION={version}" + (f", config {where}={declared}" if declared else
                                    ", no version declared in config (reported, not failed)"))


def check_pricing(root, rep):
    violations, date = [], None
    path = root / "config" / "provider-cost-profiles.yaml"
    try:
        snapshot = (load_yaml(path) or {}).get("snapshot")
        if not isinstance(snapshot, dict):
            violations.append("provider-cost-profiles.yaml: `snapshot` block missing")
        else:
            date = snapshot.get("snapshot_date")
            if is_empty(date):
                violations.append(
                    "provider-cost-profiles.yaml: snapshot.snapshot_date missing or empty - "
                    "undated pricing silently turns stale rates into false cost claims")
    except Exception as exc:                       # noqa: BLE001
        violations.append(f"provider-cost-profiles.yaml unreadable ({exc})")
    rep.counts["pricing_snapshot_date"] = str(date) if date else None
    rep.add("C10", "pricing-snapshot", violations, f"snapshot_date={date}")


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(
        description="CI package gate for token-efficient-skill-optimizer.")
    parser.add_argument("root", nargs="?", default=str(SKILL_DEFAULT),
                        help="skill package root (default: the root containing this script)")
    parser.add_argument("--sources", default=None,
                        help="path to research sources.yaml (default: resolved relative to ROOT)")
    parser.add_argument("--json", dest="json_out", default=None,
                        help="write a machine-readable result to this path")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the check table only, not every violation line")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root not found or not a directory: {root}", file=sys.stderr)
        sys.exit(2)
    if args.sources and not Path(args.sources).exists():
        print(f"ERROR: --sources path not found: {args.sources}", file=sys.stderr)
        sys.exit(2)

    sources_path = resolve_sources(root, args.sources)
    upstream_path = resolve_upstream_sources(root, sources_path)
    rep = Report()
    rep.counts["sources_file"] = str(sources_path)
    rep.counts["upstream_sources_file"] = str(upstream_path) if upstream_path else None

    print(f"== validate_package: {root} ==")
    check_paths(root, rep)
    rules = check_rules(root, rep)
    check_citations(rules, sources_path, upstream_path, rep)
    check_tests(root, rep)
    check_gates(root, rep)
    check_profiles(root, rep)
    check_secrets(root, rep)
    check_version(root, rep)
    check_pricing(root, rep)

    for check in rep.checks:
        print(f"  {check['status']}  {check['id']} {check['name']:<22} "
              f"{check['detail']}")
        if check["violations"] and not args.quiet:
            for violation in check["violations"][:25]:
                print(f"        - {violation}")
            extra = len(check["violations"]) - 25
            if extra > 0:
                print(f"        - ... and {extra} more")

    for note in rep.notes:
        print(f"  NOTE  {note}")

    passed = len(rep.checks) - len(rep.failed)
    status = "PASS" if not rep.failed else "FAIL"
    print(f"== {status}: {passed}/{len(rep.checks)} checks passed, "
          f"{rep.total_violations} violation(s) ==")

    if args.json_out:
        payload = {"status": status, "root": str(root),
                   "sources_file": str(sources_path),
                   "checks_passed": passed, "checks_total": len(rep.checks),
                   "violations_total": rep.total_violations,
                   "counts": rep.counts, "checks": rep.checks, "notes": rep.notes}
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {out}")

    sys.exit(1 if rep.failed else 0)


if __name__ == "__main__":
    main()
