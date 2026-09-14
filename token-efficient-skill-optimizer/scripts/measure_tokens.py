#!/usr/bin/env python3
"""Deterministic token/cost measurement for Agent Skills and prompt packages.

Part of the token-efficient-skill-optimizer. Extends the tier model of
token_audit.py (Anthropic anthropic-skills plugin, token-efficient-skill-builder)
with: a real-tokenizer ladder, per-file tier classification, duplicate-content
detection, and mandatory honesty labels on every number.

HONESTY CONTRACT (enforced by validate_report.py downstream):
  * bytes / lines / words            -> label "measured"  (exact, deterministic)
  * tokens via Anthropic count-tokens API -> "measured"   (exact for the named model)
  * tokens via tiktoken o200k_base   -> "estimated"       (tiktoken UNDERCOUNTS Claude
        tokens by ~15-20% on typical text per Anthropic guidance; we report the raw
        count AND a Claude-adjusted range raw*1.15 .. raw*1.25)
  * tokens via chars/words heuristic -> "estimated (wide bounds)"

Determinism: file walk is sorted, JSON uses sort_keys, no timestamps are emitted
unless --stamp is passed. Two runs on the same input are byte-identical.

Usage:
    python measure_tokens.py <skill_dir_or_file> [--json OUT.json]
        [--method auto|api|tiktoken|heuristic] [--model claude-opus-4-8] [--stamp]

Exit codes: 0 ok, 1 usage error, 2 target not found.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- tier model
# Tier semantics (context-loading cost classes):
#   metadata     - frontmatter name+description: loaded EVERY session
#   body         - SKILL.md body: loaded on trigger
#   conditional  - references/, templates/, examples/, agents/, docs: loaded on demand
#   script       - scripts/: executed, ~zero context cost unless the model reads it
TIER_BY_DIR = {
    "references": "conditional",
    "templates": "conditional",
    "examples": "conditional",
    "agents": "conditional",
    "docs": "conditional",
    "rules": "conditional",
    "config": "conditional",
    "tests": "conditional",
    "scripts": "script",
    "assets": "asset",
}

TEXT_EXT = {".md", ".txt", ".yaml", ".yml", ".json", ".jsonl", ".py", ".sh",
            ".js", ".ts", ".csv", ".xml", ".html", ".toml", ".cfg", ""}

# Text files that are NOT model context: dependency/build metadata, human-facing
# docs, and rendered demo artifacts. Counting these as "conditional context"
# inflates the context surface and produces bogus "undiscoverable" flags.
# (Found 2026-07-24 auditing a real skill: 28 of 31 flags were this false
# positive, and the conditional tier was overstated ~3x.)
NON_CONTEXT_DIRS = {"demos", "demo", "dist", "build", "coverage", "screenshots"}
NON_CONTEXT_FILE = re.compile(
    r"^(package(-lock)?\.json|readme(\.[a-z]{2})?\.md|license.*|changelog.*|"
    r"version|tsconfig\.json|requirements\.txt|pyproject\.toml|makefile|"
    r"test-prompts\.json|\.?eslintrc.*|\.gitignore|provenance\.md|"
    r"metadata\.json|"
    r"contributing\.md|codeowners|notice)$", re.I)

# Runtime-config files: shipped so some OTHER runtime can register, label or
# gate the skill. They are never loaded into model context, so counting them as
# conditional context both inflates the surface and produces an "undiscoverable"
# flag for a file nothing is ever meant to open. (Measured 2026-07-25 on
# mattpocock/improve-codebase-architecture: agents/openai.yaml is 166 B of
# display_name + allow_implicit_invocation, and was 1 of that skill's 3 flags.)
# Scoped to CONFIG extensions on purpose: a Markdown brief under agents/ is a
# sub-agent prompt, which IS model context and must stay flaggable.
RUNTIME_CONFIG_DIRS = {"agents", ".agents"}
RUNTIME_CONFIG_EXT = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}

# Language-suffixed sibling files (README.en.md vs README.md, c1-demo-en.html vs
# c1-demo.html) are intentional translations, not redundancy to remove.
LANG_SUFFIX = re.compile(r"[-_.](en|zh|cn|tw|he|ja|ko|fr|es|de|pt|ru|ar)(?=\.|$)",
                         re.I)

NGRAM_N = 8            # word n-gram size for duplicate detection
NGRAM_REPORT_MIN = 20  # report file pairs sharing at least this many distinct n-grams

# A compiled bundle is a file the BODY ITSELF declares to be the everything-in-
# one-file rendering of the package ("For the complete guide with all rules
# expanded: `AGENTS.md`"). Its overlap with each constituent is the whole point
# of shipping it, and the reader chooses one or the other - it is documented,
# intentional duplication, not waste. Reporting it as duplication was 72 of
# vercel/react-best-practices' 144 findings (2026-07-25).
BUNDLE_MARKERS = (
    # English
    "compiled", "compilation", "bundle", "bundled", "concatenat",
    "single file", "single document", "all-in-one", "all in one",
    "complete guide", "complete document", "complete reference",
    "complete version", "full guide", "full document", "full reference",
    "full text", "full version", "combined document", "combined guide",
    "unabridged", "everything in one", "all rules expanded", "fully expanded",
    "expanded in full",
    # Chinese
    "完整文档", "完整版", "合并", "汇总", "全文",
    # Hebrew
    "מסמך מלא", "גרסה מלאה", "מאוחד", "מקובץ",
)
# Chars either side of the filename mention that count as "the same context".
# A window rather than a paragraph because the declaration is routinely split
# across a heading and its first line ("## Full Compiled Document" / "For the
# complete guide ...: `AGENTS.md`") - paragraph splitting misses exactly that.
# The window never crosses a markdown heading: the next `## ...` starts a new
# subject, and letting it bleed backwards declared two ordinary rule files
# bundles on the first real run of this check (2026-07-25).
BUNDLE_WINDOW = 300
ATX_HEADING_RE = re.compile(r"^#{1,6}[ \t]", re.M)
# A pair is bundle-vs-constituent only if the bundle is the LARGER side and it
# really absorbed the other file. Both halves matter: without the size test a
# small file that merely mentions the word "compiled" would excuse its own
# duplication, and without the ratio test two unrelated files sharing boilerplate
# would be laundered as "compilation overlap".
BUNDLE_CONSTITUENT_MIN_RATIO = 0.20

# tiktoken->Claude adjustment range. Basis: Anthropic's token-counting guidance
# states tiktoken undercounts Claude tokens by ~15-20% on typical text (more on
# code / non-English). Claude_estimate ~= tiktoken * [1.15, 1.25].
CLAUDE_ADJ_LOW = 1.15
CLAUDE_ADJ_HIGH = 1.25


def classify_tier(rel):
    """Tier for a text file, honouring the artifact-vs-context distinction."""
    parts = Path(rel).parts
    top = parts[0] if len(parts) > 1 else ""
    # match a non-context dir at ANY depth: assets/demos/ and demos/ are both
    # rendered artifacts. Top-level-only matching left nested copies classified
    # as context (found auditing this package's own test fixtures).
    if any(part.lower() in NON_CONTEXT_DIRS for part in parts[:-1]):
        return "artifact"
    if NON_CONTEXT_FILE.match(Path(rel).name):
        return "artifact"
    # A config-format file inside an agents/ directory is another runtime's
    # manifest, not context. Markdown there is deliberately NOT caught.
    if (any(part.lower() in RUNTIME_CONFIG_DIRS for part in parts[:-1])
            and Path(rel).suffix.lower() in RUNTIME_CONFIG_EXT):
        return "artifact"
    # Executables are script tier wherever they live (data/_sync_all.py is a
    # tool, not context) - they cost context only if the model reads them.
    if Path(rel).suffix.lower() in (".py", ".js", ".mjs", ".sh", ".ts"):
        return "script"
    return TIER_BY_DIR.get(top, "conditional")


def parse_frontmatter(text):
    """Return (frontmatter_text, body_text). Empty frontmatter if none."""
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
    if not m:
        return "", text
    return m.group(1), m.group(2)


# ------------------------------------------------------------ token counting
class TokenCounter:
    """Ladder: api (measured) > tiktoken (estimated) > heuristic (estimated)."""

    def __init__(self, method, model):
        self.model = model
        self.method = None
        self.label = None
        self._enc = None
        if method in ("auto", "api") and os.environ.get("ANTHROPIC_API_KEY"):
            self.method = "api"
            self.label = (
                f"measured (Anthropic count-tokens API, model {model})")
        if self.method is None and method in ("auto", "tiktoken", "api"):
            try:
                import tiktoken  # noqa: deferred import so heuristic path has no dep
                self._enc = tiktoken.get_encoding("o200k_base")
                self.method = "tiktoken"
                self.label = (
                    "estimated (tiktoken o200k_base; tiktoken undercounts Claude "
                    f"tokens ~15-20%, Claude-adjusted range = raw x{CLAUDE_ADJ_LOW}"
                    f"..x{CLAUDE_ADJ_HIGH})")
            except ImportError:
                pass
        if self.method is None:
            self.method = "heuristic"
            self.label = ("estimated (heuristic chars/3.5 cross-checked with "
                          "words*1.3; wide bounds)")

    def count(self, text):
        """Return dict with raw count + claude_range (low, high)."""
        if self.method == "api":
            n = self._count_api(text)
            return {"raw": n, "claude_low": n, "claude_high": n}
        if self.method == "tiktoken":
            n = len(self._enc.encode(text, disallowed_special=()))
            return {"raw": n,
                    "claude_low": round(n * CLAUDE_ADJ_LOW),
                    "claude_high": round(n * CLAUDE_ADJ_HIGH)}
        by_chars = max(1, round(len(text) / 3.5))
        by_words = max(1, round(len(text.split()) * 1.3))
        lo, hi = sorted((by_chars, by_words))
        return {"raw": round((lo + hi) / 2),
                "claude_low": round(lo * 0.8), "claude_high": round(hi * 1.4)}

    def _count_api(self, text):
        import urllib.request
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages/count_tokens",
            data=json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": text or " "}],
            }).encode(),
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            })
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["input_tokens"]


# ------------------------------------------------------- duplicate detection
def word_ngrams(text, n=NGRAM_N):
    words = re.findall(r"\w+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _lang_normalized(path):
    """Path with any language suffix stripped: README.en.md -> README.md."""
    return LANG_SUFFIX.sub("", path)


def _sections(text):
    """Split markdown at ATX headings -> [section_text].

    The heading line stays with the section it introduces, because the
    declaration routinely lives in the heading ("## Full Compiled Document").
    """
    starts = sorted({0} | {m.start() for m in ATX_HEADING_RE.finditer(text)})
    return [text[s:(starts[i + 1] if i + 1 < len(starts) else len(text))]
            for i, s in enumerate(starts)]


def declared_bundles(body, candidates):
    """Context files the body itself declares to be a compiled/complete bundle.

    Detection is deliberately two-sided: the file's NAME must appear in the
    body AND a bundle marker must appear near that mention, in the same
    markdown section. A marker alone ("this skill compiles a report") declares
    nothing; a bare filename mention is just a pointer.

    Filenames are MASKED (same length, so offsets survive) before the marker
    search: `rules/bundle-barrel-imports.md` contains the literal marker word
    "bundle", and without masking a rule file declared itself a bundle - which
    then quietly re-listed its own overlap as a real duplicate.
    """
    bases = sorted({os.path.basename(r) for r in candidates if os.path.basename(r)},
                   key=len, reverse=True)
    out = set()
    for section in _sections(body):
        masked = section
        for b in bases:
            masked = masked.replace(b, " " * len(b))
        low = masked.lower()
        for rel in candidates:
            base = os.path.basename(rel)
            if rel in out or not base:
                continue
            for m in re.finditer(re.escape(base), section):
                window = low[max(0, m.start() - BUNDLE_WINDOW):
                             m.end() + BUNDLE_WINDOW]
                if any(k in window for k in BUNDLE_MARKERS):
                    out.add(rel)
                    break
    return out


def duplicate_pairs(file_texts, bundles=frozenset()):
    """Cross-file shared word-8-gram report. [measured] - exact set math.

    Returns (real_duplicates, bilingual_sibling_pairs, compiled_bundle_pairs).
    Language-suffixed siblings are reported separately: they are intentional
    translations, and listing them as duplication produced 9 of the top-12
    findings on a real bilingual skill (2026-07-24). `bundles` (see
    declared_bundles) is the same idea one level up: a documented compiled
    rendering of the package overlaps every constituent BY DESIGN, so those
    pairs are reported informationally instead of as findings.

    Callers pass CONTEXT files only. Duplication inside artifacts (demo HTML,
    build metadata) costs zero context tokens, so reporting it as an
    optimization finding is noise - it was 427 of 437 pairs on that same skill.
    """
    grams = {p: word_ngrams(t) for p, t in file_texts.items()}
    out, siblings, bundled = [], [], []
    paths = sorted(grams)
    for i, a in enumerate(paths):
        for b in paths[i + 1:]:
            shared = grams[a] & grams[b]
            if len(shared) < NGRAM_REPORT_MIN:
                continue
            smaller = min(len(grams[a]), len(grams[b])) or 1
            ratio = round(len(shared) / smaller, 3)
            rec = {"file_a": a, "file_b": b,
                   "shared_8grams": len(shared),
                   "overlap_ratio_of_smaller": ratio}
            # bundle-vs-constituent: the declared bundle is the bigger side and
            # has really absorbed the other file.
            big, small = (a, b) if len(grams[a]) >= len(grams[b]) else (b, a)
            if (big in bundles and small not in bundles
                    and len(grams[big]) > len(grams[small])
                    and ratio >= BUNDLE_CONSTITUENT_MIN_RATIO):
                rec["bundle"] = big
                bundled.append(rec)
            elif _lang_normalized(a) == _lang_normalized(b):
                siblings.append(rec)
            else:
                out.append(rec)
    key = lambda d: -d["shared_8grams"]
    return (sorted(out, key=key), sorted(siblings, key=key),
            sorted(bundled, key=key))


# ----------------------------------------------------------- structural flags
# Flag heuristics adapted from token_audit.py (token-efficient-skill-builder).
#
# Multilingual by necessity: English-only lists mis-flagged a Chinese skill
# whose description carried both triggers and an exclusion (2026-07-24).
# Skills are written in the author's language; the heuristics must follow.
TRIGGER_MARKERS = (
    # English
    "use when", "use this", "use whenever", "use for", "use it when",
    "use any time", "trigger",
    # Chinese
    "触发词", "触发", "使用场景", "何时使用", "适用于", "用于", "用来",
    # Hebrew
    "השתמש", "לשימוש", "מתי", "כאשר", "טריגר",
)
NEGATIVE_BOUNDARY_MARKERS = (
    # English
    "do not use", "don't use", "not for", "except when", "do not apply",
    "avoid using", "not suitable",
    # Chinese
    "不适用", "不要用", "不用于", "不适合", "不支持", "除外", "并非",
    # Hebrew
    "אל תשתמש", "אין להשתמש", "לא מיועד", "לא לשימוש", "לא מתאים",
)
# Read-conditions: the paragraph tells the model WHEN to open the reference.
READ_CONDITION_RE = re.compile(
    r"\b(when(ever)?|only|if|unless|before|after|first)\b"   # English
    r"|详见|参见|必读|先读|先看|见\s|时|需要|若|如果|当"        # Chinese
    r"|כאשר|רק\s|אם\s|לפני|בעת|במקרה",                       # Hebrew
    re.I)

# Trigger phrasing stated semantically instead of with a marker word. "...when
# building new UI or reshaping an existing one" IS the trigger; the literal list
# above just happened to match how the first sample of skills was worded
# (anthropics/frontend-design, 2026-07-25).
# Deliberately narrow: a bare "when" anywhere in the description is NOT
# accepted - it is ordinary prose ("choices that matter when reviewed").
# Only when/for + a gerund, or when + you/your.
TRIGGER_GERUND_RE = re.compile(r"\b(?:when|for)\s+([a-z]{3,}ing)\b", re.I)
TRIGGER_WHEN_YOU_RE = re.compile(r"\bwhen\s+your?\b", re.I)
# -ing words that are not gerunds. Without this, "Do not use for anything real"
# would read as trigger phrasing - the stop-list is what keeps the rule from
# collapsing into "contains the word for".
NON_GERUND_ING = {
    "anything", "everything", "nothing", "something", "thing", "things",
    "during", "string", "strings", "king", "kings", "ring", "rings", "spring",
    "morning", "evening", "ceiling", "sibling", "siblings", "wing", "wings",
    "being", "bring", "sing", "swing", "sterling", "engineering",
}

# A concrete pointer names a real file. Generic path-convention prose
# ("paths look like references/xxx.md") is not a pointer and must not be flagged.
CONCRETE_REF_RE = re.compile(r"references/(?!x{2,}|<|\*|\.\.\.)[\w.-]+\.\w+")

# Convention-based reachability (FP-1). A body that lists 70 rule STEMS and then
# documents the path shape once ("rules/async-parallel.md") has told the model
# everything it needs to open rules/advanced-init-once.md. That is MORE token-
# efficient than 70 literal paths, so flagging all 70 penalised the better
# design: 68 of vercel/react-best-practices' 72 flags (2026-07-25).
# Both halves are required, and neither is the depth guard:
#   * the stem must appear in the body as a whole token, and
#   * the body must show a real <dir>/<name>.<ext> path for THAT directory.
# The depth guard (bare directory mentions must be depth >= 2) is untouched -
# a body saying only "references/" still shows no <dir>/<file>.<ext> pattern and
# still rescues nothing.
MIN_CONVENTION_STEM = 3   # 1-2 char stems collide with ordinary prose


def _dir_path_convention(directory, body):
    """True if `body` shows a concrete `<directory>/<name>.<ext>` path."""
    if not directory:
        return False          # a root-level file has no directory convention
    return bool(re.search(re.escape(directory) + r"/[A-Za-z0-9_.\-]+\.[A-Za-z0-9]+",
                          body))


def _stem_named(stem, body):
    """True if `stem` appears in `body` as a whole token.

    Substring matching would make `rerender-memo` rescue `rerender-memo-with-
    default-value` and vice versa; the boundary class includes `-` and `_` so a
    stem only matches its own listing.
    """
    if len(stem) < MIN_CONVENTION_STEM:
        return False
    return bool(re.search(r"(?<![A-Za-z0-9_-])" + re.escape(stem)
                          + r"(?![A-Za-z0-9_-])", body))


def has_trigger_phrasing(desc):
    """Literal marker OR a semantic when/for construction."""
    if any(h in desc.lower() for h in TRIGGER_MARKERS):
        return True
    if TRIGGER_WHEN_YOU_RE.search(desc):
        return True
    return any(m.group(1).lower() not in NON_GERUND_ING
               for m in TRIGGER_GERUND_RE.finditer(desc))


def nested_package_root(rel, nested_roots):
    """Deepest ancestor of `rel` that carries its own SKILL.md ('' if none).

    A sub-directory with a SKILL.md is a package in its own right (a skills
    directory under batch audit, a vendored sub-skill, a bundled fixture
    package). Reachability inside it is that manifest's business, not the outer
    one's.
    """
    parent = os.path.dirname(rel)
    while parent:
        if parent in nested_roots:
            return parent
        parent = os.path.dirname(parent)
    return ""


def structural_flags(name, desc, body, ref_texts, script_blob="",
                     nested_bodies=None, auto_invocation=True):
    """Return (flags, notes). `notes` explains every suppression, per run."""
    nested_bodies = nested_bodies or {}
    flags, notes = [], []
    if not desc:
        flags.append("CRITICAL: no frontmatter description - skill cannot trigger")
    else:
        if len(desc) > 1024:
            flags.append(f"description {len(desc)} chars > 1024 spec limit")
        low = desc.lower()
        # A skill with disable-model-invocation: true never auto-triggers - the
        # author turned that off on purpose. Its description is a menu label for
        # explicit invocation, so "no trigger phrasing" and "no negative
        # boundary" describe a surface that does not exist. Both were 2 of the 3
        # flags on mattpocock/improve-codebase-architecture (2026-07-25).
        # The 1024-char spec limit and the missing-description check still
        # apply: those are about the manifest, not about triggering.
        if not auto_invocation:
            notes.append(
                "trigger-phrasing and negative-boundary checks suppressed: "
                "frontmatter sets disable-model-invocation: true, so this skill "
                "never auto-triggers and its description is not a trigger "
                "surface (it is a label for explicit invocation)")
        else:
            if not has_trigger_phrasing(desc):
                flags.append("description lacks explicit trigger phrasing")
            if not any(h in low for h in NEGATIVE_BOUNDARY_MARKERS):
                flags.append(
                    "description lacks a negative boundary ('Do not use for...')")
    body_lines = body.splitlines()
    if len(body_lines) > 500:
        flags.append(f"body {len(body_lines)} lines > 500 - extract to references/")
    big_blocks = [b for b in re.findall(r"```[^\n]*\n(.*?)```", body, re.DOTALL)
                  if len(b.splitlines()) > 15]
    if big_blocks:
        flags.append(f"{len(big_blocks)} code block(s) >15 lines in body - move to scripts/")
    for para in re.split(r"\n\s*\n", body):
        if CONCRETE_REF_RE.search(para) and not READ_CONDITION_RE.search(para):
            flags.append("a references/ pointer has no read-condition ('read only when...')")
            break
    by_convention = []
    for rel, rtext in sorted(ref_texts.items()):
        # Which manifest is this file discovered through? A file under a nested
        # package root is reached via THAT package's SKILL.md; judging it
        # against the outer body reports every nested package's own references
        # as undiscoverable (5 of 5 flags when this tool was pointed at its own
        # package - 100% false positives, 2026-07-25). Paths are re-based on the
        # owning root so the body's own relative pointers match.
        pkg = nested_package_root(rel, nested_bodies)
        inner = rel[len(pkg) + 1:] if pkg else rel
        if pkg and inner == "SKILL.md":
            continue          # a package's own manifest IS the entry point
        scope_body = nested_bodies[pkg] if pkg else body
        # Discoverable if the body names the file, OR names a parent directory
        # (a body that says "ls data/stacks/" makes everything under it
        # discoverable at runtime - flagging each file is a false positive).
        # Only SUB-directories count as pointers. The conventional top-level
        # container ("references/") appears in nearly every body, so accepting
        # depth-1 dirs marks every file discoverable and silently hides real
        # unreachable-capability findings (caught by regression, 2026-07-24).
        # Depth is measured from the OWNING package root, so the guard bites
        # identically in the outer package and in every nested one.
        parent = os.path.dirname(inner)
        dirs_named = []
        while parent.count(os.sep) >= 1:      # depth >= 2, e.g. data/stacks
            dirs_named.append(parent.replace(os.sep, "/") + "/")
            parent = os.path.dirname(parent)
        base = os.path.basename(rel)
        # A language-suffixed sibling (an "-en" twin beside the referenced
        # original) is reached through the SAME pointer: the pair is one
        # intentional translation, which this tool already models as such in
        # duplicate_pairs(). Only the counterpart's name is carried in prose.
        # NB: no real filename appears in this comment on purpose - this file is
        # part of the script blob, so naming one would silently mark it
        # reachable and hollow out the very check below.
        names = {base, _lang_normalized(base)}
        # Reachable via prose, via a sub-directory pointer, or programmatically
        # from a bundled script (a data file a script opens by name is reached
        # through the script's interface, not by the model reading the body).
        if (any(n in scope_body for n in names)
                or any(d in scope_body for d in dirs_named)
                or any(n in script_blob for n in names)):
            continue
        # Reachable by documented convention: the body lists this file's STEM
        # and shows a concrete path for its directory. See MIN_CONVENTION_STEM
        # and _dir_path_convention - this ADDS a rescue path, it does not
        # loosen the depth guard above (a bare "references/" mention shows no
        # <dir>/<file>.<ext> path and rescues nothing).
        stem = Path(inner).stem
        if (_dir_path_convention(os.path.dirname(inner).replace(os.sep, "/"),
                                 scope_body)
                and any(_stem_named(s, scope_body)
                        for s in {stem, _lang_normalized(stem)})):
            by_convention.append(rel)
            continue
        flags.append(f"{rel} not referenced from SKILL.md body or any bundled "
                     f"script - likely undiscoverable (verify: dynamic access "
                     f"cannot be detected statically)")
    if by_convention:
        shown = ", ".join(by_convention[:4])
        more = (f" (+{len(by_convention) - 4} more)"
                if len(by_convention) > 4 else "")
        notes.append(
            f"{len(by_convention)} conditional file(s) reachable by documented "
            f"convention - the body lists the stem and shows a "
            f"<dir>/<name>.<ext> path for the directory, so they are NOT "
            f"flagged undiscoverable: {shown}{more}")
    return flags, notes


# --------------------------------------------------------------------- main
def measure(target, method, model):
    target = Path(target).resolve()
    if not target.exists():
        print(f"ERROR: {target} not found", file=sys.stderr)
        sys.exit(2)

    counter = TokenCounter(method, model)
    files = []          # per-file records
    file_texts = {}     # rel path -> text (for dup detection)
    fm_name = fm_desc = ""
    body_text = ""
    ref_texts = {}
    nested_bodies = {}  # dir rel-path -> body of the SKILL.md it carries
    auto_invocation = True   # frontmatter disable-model-invocation: true flips it

    if target.is_file():
        paths = [target]
        root = target.parent
    else:
        root = target
        paths = sorted(p for p in target.rglob("*")
                       if p.is_file() and not any(
                           part.startswith(".") or part in ("venv", "__pycache__",
                                                            "node_modules", "_archive")
                           for part in p.relative_to(target).parts))

    for p in paths:
        rel = str(p.relative_to(root)) if p != root else p.name
        if p.suffix.lower() not in TEXT_EXT:
            files.append({"path": rel, "tier": "asset", "bytes": p.stat().st_size,
                          "note": "binary/unknown ext - bytes only [measured]"})
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        top = p.relative_to(root).parts[0] if p != root and len(p.relative_to(root).parts) > 1 else ""
        if p.name == "SKILL.md" and top == "":
            fm, body = parse_frontmatter(text)
            body_text = body
            fm_name = (re.search(r"^name:\s*(.+)$", fm, re.M) or [None, ""])[1].strip()
            # `[\w-]+:` not `\w+:` - the next key is routinely HYPHENATED
            # (disable-model-invocation, allowed-tools), and a `\w+`-only
            # terminator swallowed it into the description: the measured
            # description then carried "disable-model-invocation: true" as
            # prose, inflating its length and offering marker words the author
            # never wrote. Indented continuation lines of a YAML block scalar
            # still do not match, so multi-line descriptions are unaffected.
            dm = re.search(r"^description:\s*(.+?)(?=^[\w-]+:|\Z)", fm,
                           re.M | re.DOTALL)
            fm_desc = re.sub(r"\s+", " ", dm.group(1)).strip() if dm else ""
            auto_invocation = not re.search(
                r"^disable-model-invocation:\s*[\"']?(true|yes)[\"']?\s*$",
                fm, re.M | re.I)
            for part_name, part_text, tier in (
                    ("SKILL.md#frontmatter", fm, "metadata"),
                    ("SKILL.md#body", body, "body")):
                t = counter.count(part_text)
                files.append({
                    "path": part_name, "tier": tier,
                    "bytes": len(part_text.encode("utf-8")),
                    "lines": len(part_text.splitlines()),
                    "words": len(part_text.split()),
                    "tokens_raw": t["raw"],
                    "tokens_claude_low": t["claude_low"],
                    "tokens_claude_high": t["claude_high"],
                })
            file_texts["SKILL.md"] = text
            continue
        if p.name == "SKILL.md":
            # A SKILL.md below the root marks a nested package: it, not the
            # outer manifest, governs discovery of everything beneath it.
            nested_bodies[os.path.dirname(rel)] = parse_frontmatter(text)[1]
        tier = classify_tier(rel)
        t = counter.count(text)
        files.append({
            "path": rel, "tier": tier,
            "bytes": len(text.encode("utf-8")),
            "lines": len(text.splitlines()),
            "words": len(text.split()),
            "tokens_raw": t["raw"],
            "tokens_claude_low": t["claude_low"],
            "tokens_claude_high": t["claude_high"],
        })
        file_texts[rel] = text
        # Only true conditional-context files can be "undiscoverable"; build
        # metadata, human docs and demo artifacts are classified 'artifact'
        # by classify_tier() and never reach this flag.
        if tier == "conditional":
            ref_texts[rel] = text

    # Everything a bundled script could open by name (any executable-ish file
    # anywhere in the package, not just scripts/).
    script_blob = "\n".join(
        t for p, t in file_texts.items()
        if Path(p).suffix.lower() in (".py", ".js", ".mjs", ".sh", ".ts"))

    # Duplication only matters where it is billed: context tiers.
    context_tiers = {f["path"] for f in files
                     if f.get("tier") in ("body", "conditional")}
    context_texts = {p: t for p, t in file_texts.items()
                     if p in context_tiers or p == "SKILL.md"}
    bundles = declared_bundles(body_text,
                               [p for p in context_texts if p != "SKILL.md"])
    dups, sibs, bundle_pairs = duplicate_pairs(context_texts, bundles)

    def tier_sum(tier, key):
        return sum(f.get(key, 0) for f in files if f.get("tier") == tier)

    totals = {}
    for tier in ("metadata", "body", "conditional", "script", "artifact",
                 "asset"):
        totals[tier] = {
            "files": sum(1 for f in files if f.get("tier") == tier),
            "bytes": tier_sum(tier, "bytes"),
            "tokens_raw": tier_sum(tier, "tokens_raw"),
            "tokens_claude_low": tier_sum(tier, "tokens_claude_low"),
            "tokens_claude_high": tier_sum(tier, "tokens_claude_high"),
        }

    flags, informational = structural_flags(
        fm_name, fm_desc, body_text, ref_texts, script_blob, nested_bodies,
        auto_invocation)

    # The compiled-bundle finding is downgraded to an informational line, never
    # dropped silently: the reader still learns the bundle exists and what it
    # costs, and can still decide to stop shipping it.
    for b in sorted(bundles):
        n = sum(1 for d in bundle_pairs if d.get("bundle") == b)
        if n:
            informational.append(
                f"{b} is declared in SKILL.md as a compiled/complete bundle; "
                f"{n} pair(s) against its constituents are reported as "
                f"compiled_bundle_pairs, not as duplication findings "
                f"(intentional, documented duplication - the reader loads the "
                f"bundle OR the parts, never both)")
    runtime_cfg = sorted(
        f["path"] for f in files
        if f.get("tier") == "artifact"
        and (NON_CONTEXT_FILE.match(os.path.basename(f["path"]))
             or (Path(f["path"]).suffix.lower() in RUNTIME_CONFIG_EXT
                 and any(part.lower() in RUNTIME_CONFIG_DIRS
                         for part in Path(f["path"]).parts[:-1]))))
    if runtime_cfg:
        informational.append(
            f"{len(runtime_cfg)} file(s) classified 'artifact' (shipped, but "
            f"never loaded into model context - build/runtime metadata): "
            + ", ".join(runtime_cfg[:6])
            + (f" (+{len(runtime_cfg) - 6} more)" if len(runtime_cfg) > 6 else ""))

    report = {
        "target": str(target),
        "token_method": counter.method,
        "token_label": counter.label,
        "structural_label": "measured (exact bytes/lines/words)",
        "model_for_api_method": model,
        "files": files,
        "tier_totals": totals,
        "duplicates": dups,
        "bilingual_sibling_pairs": sibs,
        "compiled_bundle_pairs": bundle_pairs,
        "declared_bundles": sorted(bundles),
        "flags": flags,
        "informational": informational,
        "notes": [
            "metadata tier is loaded in EVERY session; body on trigger; "
            "conditional on demand; scripts execute at ~zero context cost.",
            "'artifact' = text that is NOT model context (build metadata, human "
            "docs, rendered demos). Excluded from the context surface and from "
            "the undiscoverable-reference flag.",
            "bilingual_sibling_pairs are intentional translations, not "
            "duplication to remove.",
            "compiled_bundle_pairs are a documented all-in-one rendering vs. "
            "its constituents - overlap is the point, not waste.",
            "'informational' explains every suppression this run applied; a "
            "suppressed check is never silently dropped.",
            "latency: not measured; any latency statement derived from this "
            "report must be labeled projected.",
        ],
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--method", default="auto",
                    choices=["auto", "api", "tiktoken", "heuristic"])
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--stamp", action="store_true",
                    help="include a run timestamp (breaks byte-determinism)")
    args = ap.parse_args()

    report = measure(args.target, args.method, args.model)
    if args.stamp:
        import datetime
        report["generated_at"] = datetime.datetime.now(
            datetime.timezone.utc).isoformat()

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # human summary
    w = 72
    print("=" * w)
    print(f"TOKEN MEASUREMENT: {report['target']}")
    print(f"method: {report['token_method']} -> {report['token_label']}")
    print("=" * w)
    for tier in ("metadata", "body", "conditional", "script", "artifact",
                 "asset"):
        t = report["tier_totals"][tier]
        if not t["files"]:
            continue
        rng = (f"{t['tokens_claude_low']}-{t['tokens_claude_high']}"
               if t["tokens_claude_low"] != t["tokens_claude_high"]
               else str(t["tokens_claude_low"]))
        print(f"  {tier:<12} {t['files']:>3} files  {t['bytes']:>8} B  "
              f"~{rng} tokens [{'measured' if report['token_method'] == 'api' else 'estimated'}]")
    if report["duplicates"]:
        print(f"\nDUPLICATE CONTENT ({len(report['duplicates'])} pair(s), "
              f"shared {NGRAM_N}-word grams) [measured]:")
        for d in report["duplicates"][:10]:
            print(f"  {d['file_a']} <-> {d['file_b']}: {d['shared_8grams']} "
                  f"({d['overlap_ratio_of_smaller']:.0%} of smaller)")
    if report["bilingual_sibling_pairs"]:
        print(f"\nBILINGUAL SIBLINGS ({len(report['bilingual_sibling_pairs'])} "
              f"pair(s)) - intentional translations, NOT duplication [measured]")
    if report["compiled_bundle_pairs"]:
        print(f"\nCOMPILED BUNDLE ({len(report['compiled_bundle_pairs'])} "
              f"pair(s) vs. {', '.join(report['declared_bundles'])}) - "
              f"documented all-in-one rendering, NOT duplication [measured]")
    if report["flags"]:
        print(f"\nFLAGS ({len(report['flags'])}):")
        for i, fl in enumerate(report["flags"], 1):
            print(f"  {i}. {fl}")
    if report["informational"]:
        print(f"\nINFORMATIONAL ({len(report['informational'])}) - not findings:")
        for i, nt in enumerate(report["informational"], 1):
            print(f"  {i}. {nt}")
    if args.json_out:
        print(f"\nJSON written: {args.json_out}")


if __name__ == "__main__":
    main()
