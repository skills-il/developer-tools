#!/usr/bin/env python3
"""Live-run adapter (BUILT, NOT RUN by default). token-efficient-skill-optimizer.

Bridges this project's tests/cases.jsonl to skill-creator's eval machinery so a
future session (with user-approved API budget) can measure behavioral quality
instead of projecting it. This script only WRITES an evals.json and prints the
instructions; it never calls a model itself.

Discovery order for skill-creator:
  1. ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/
  2. any path matching ~/Library/Application Support/Claude/**/skills/skill-creator
If neither exists, reports "live layer unavailable" and exits 0 (graceful).

Usage:
    live_eval_adapter.py CASES.jsonl --skill-name NAME [--out evals.json]

evals.json schema: see skill-creator references/schemas.md (frozen copy in
sources/skill-creator-schemas/). Fields: skill_name, evals[].{id,prompt,
expected_output,files,expectations}.
"""

import argparse
import glob
import json
import sys
from pathlib import Path


def find_skill_creator():
    home = Path.home()
    fixed = (home / ".claude/plugins/marketplaces/claude-plugins-official/"
             "plugins/skill-creator/skills/skill-creator")
    if (fixed / "SKILL.md").exists():
        return fixed
    for hit in glob.glob(str(home / "Library/Application Support/Claude/"
                             "**/skills/skill-creator/SKILL.md"),
                         recursive=True):
        return Path(hit).parent
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases_jsonl")
    ap.add_argument("--skill-name", required=True)
    ap.add_argument("--out", default="evals.json")
    args = ap.parse_args()

    cases = []
    for line in Path(args.cases_jsonl).read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))

    evals = {
        "skill_name": args.skill_name,
        "evals": [
            {
                "id": i + 1,
                "prompt": c["prompt"],
                "expected_output": c.get("expected_behavior", ""),
                "files": c.get("files", []),
                "expectations": c.get("expectations", []),
            }
            for i, c in enumerate(cases)
        ],
    }
    Path(args.out).write_text(json.dumps(evals, indent=2) + "\n",
                              encoding="utf-8")
    print(f"wrote {args.out} with {len(cases)} evals "
          f"(skill-creator evals.json schema)")

    sc = find_skill_creator()
    if sc is None:
        print("live layer unavailable: skill-creator not found on this machine.")
        print("All behavioral-quality figures must remain labeled [projected].")
        return
    print(f"skill-creator found: {sc}")
    print("To run live (requires user-approved API budget):")
    print(f"  follow {sc}/SKILL.md eval flow with the generated {args.out};")
    print("  aggregate with scripts/aggregate_benchmark.py (mean +/- stddev).")
    print("Numbers from such runs may then be labeled [measured] with a data")
    print("pointer to the benchmark.json produced.")


if __name__ == "__main__":
    main()
