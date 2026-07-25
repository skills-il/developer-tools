#!/usr/bin/env python3
"""Honesty gate for optimizer reports. token-efficient-skill-optimizer.

Scans a markdown report for quantitative savings/cost/latency claims and FAILS if:
  1. a claim line lacks one of the five savings labels, or
  2. a [measured] claim has no data pointer - either "data:" + an existing path
     on the same line, or a "## Harness data" section listing >= 1 existing path.

SAVINGS TAXONOMY (5 categories; the last two adopted from the GPT/Codex
reference implementation, 2026-07-25 - they name failure modes the original
three could not express):
  [measured]           observed by an identified tool or eval run; needs a pointer
  [estimated]          computed via a disclosed approximation (e.g. tiktoken rung)
  [projected]          expected from rule evidence, not observed on this target
  [cache-dependent]    realized only on a cache HIT; evaporates on a cold prefix
                       or after a TTL lapse. Not a token reduction at all - a
                       billing effect. Must never be summed with [measured].
  [behavior-dependent] realized only if the model/user actually takes the assumed
                       path (triggers the skill, reads the reference, stops early).
                       Depends on behavior we did not measure.
  [reported]           a number a CITED SOURCE reports about ITS OWN experiment.
                       Needs a source id, ideally with a locator. Added 2026-07-25
                       because the other five labels are all claims about the target
                       being optimized, and none of them can express "this paper
                       measured 20x on GSM8K". The registry's old convention was to
                       call such figures [projected], which collapses two different
                       things: a third party's measurement (has an author, a venue,
                       a sample) and our inference onto your skill (has neither).

Reporting a cache-dependent or behavior-dependent figure as [measured] is the
exact "estimates dressed as measurements" failure this gate exists to block.

A "claim line" = a line outside fenced code blocks containing a digit AND at
least one cost keyword (token/tokens/cost/$/USD/saving/reduction/latency/ms/sec
/calls/retries). Lines inside code fences, table separator rows, and lines
tagged <!-- no-claim --> are exempt.

Usage: validate_report.py REPORT.md [REPORT2.md ...] [--root PROJECT_ROOT]
Exit: 0 = pass, 1 = violations found, 2 = usage error.
"""

import argparse
import re
import sys
from pathlib import Path

# Latency units only count when attached to a number ("43 sec", "120ms") -
# a bare "sec"/"ms" matches ordinary prose ("Second finding", "systems").
KEYWORDS = re.compile(
    r"(tokens?\b|cost|\$|\bUSD\b|savings?\b|reduction|latency|"
    r"\d\s*(ms|sec(onds?)?)\b|calls\b|retr(y|ies)\b|per[- ]mtok)", re.I)
# label may open on the claim line and close on a later line (long parentheticals)
LABEL = re.compile(
    r"[\[\(](measured|estimated|projected|cache-dependent|behavior-dependent|reported|"
    r"not modeled|not measured)", re.I)
# [reported] is a THIRD PARTY's number about THEIR experiment. Like [measured] it must be
# traceable, but to a source and locator rather than to a data file - "S-R05 Fig. 1", not
# "data: run.json". A [reported] claim with no source id is the same failure as a [measured]
# claim with no data pointer: a number the reader cannot check.
REPORTED = re.compile(r"[\[\(]reported\b[^\]\)]*[\]\)]", re.I)
SOURCE_PTR = re.compile(r"\bS-[A-Z]\d{2}\b|\bsource:\s*\S+", re.I)
# "cache-dependent"/"behaviour" must not be read as a bare [measured] claim, so
# require the word to start the label rather than merely appear inside it.
MEASURED = re.compile(r"[\[\(]measured\b[^\]\)]*[\]\)]", re.I)
DATA_PTR = re.compile(r"data:\s*(\S+)")
NO_CLAIM = "<!-- no-claim -->"


def check(path, root):
    text = Path(path).read_text(encoding="utf-8")
    violations = []
    in_fence = False

    # collect harness-data section paths
    harness_ok = False
    m = re.search(r"^##\s*Harness data\s*$(.*?)(?=^##\s|\Z)", text,
                  re.M | re.DOTALL)
    if m:
        # exclude backticks/quotes from the path itself - a greedy \S+ used to
        # swallow the opening backtick and every pointer failed to resolve
        for cand in re.findall(r"[`'\"\s]([^\s`'\"]+\.(?:json|jsonl|csv|yaml|txt))\b",
                               m.group(1)):
            if (root / cand).exists() or Path(cand).exists():
                harness_ok = True
                break

    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or NO_CLAIM in line:
            continue
        if re.fullmatch(r"\|[\s\-:|]+\|", s):   # md table separator row
            continue
        if not (any(c.isdigit() for c in s) and KEYWORDS.search(s)):
            continue
        if not LABEL.search(s):
            violations.append((i, "quantitative claim without "
                               "[measured]/[estimated]/[projected] label", s))
            continue
        if MEASURED.search(s):
            dm = DATA_PTR.search(s)
            ptr_ok = bool(dm and ((root / dm.group(1)).exists()
                                  or Path(dm.group(1)).exists()))
            if not (ptr_ok or harness_ok):
                violations.append((i, "[measured] claim without a data pointer "
                                   "(inline 'data: <path>' or a '## Harness "
                                   "data' section with an existing file)", s))
        if REPORTED.search(s) and not SOURCE_PTR.search(s):
            violations.append((i, "[reported] claim without a source id "
                               "(needs an S-xxx id, ideally with a locator - it is "
                               "someone else's result and must be traceable to them)", s))
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="+")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    failed = False
    for rp in args.reports:
        if not Path(rp).exists():
            print(f"ERROR: {rp} not found", file=sys.stderr)
            sys.exit(2)
        v = check(rp, root)
        if v:
            failed = True
            print(f"FAIL {rp}: {len(v)} violation(s)")
            for line_no, why, snippet in v:
                print(f"  L{line_no}: {why}")
                print(f"    | {snippet[:110]}")
        else:
            print(f"PASS {rp}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
