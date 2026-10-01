#!/usr/bin/env python3
"""Scaffold a new skills-il skill folder with correct structure and templates.

Creates the complete folder structure for a new skill:
  <skill-name>/
  ├── SKILL.md          # Template with minimal frontmatter, Gotchas and Reference Links stubs
  ├── SKILL_HE.md       # Hebrew companion stub
  ├── metadata.json     # All enriched metadata (Claude Desktop rejects it in frontmatter)
  ├── scripts/          # For helper scripts
  └── references/       # For reference documentation

Run it from the directory the new skill folder should be created in (your repo
root, or the category repo root), or pass --dir.

Usage:
  python3 <path-to>/scaffold-skill.py --name my-skill --category developer-tools --author my-github-login
  python3 <path-to>/scaffold-skill.py --name my-skill --category tax-and-finance --author my-github-login --dir ../my-repo
  python3 <path-to>/scaffold-skill.py --help
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

VALID_CATEGORIES = [
    "tax-and-finance",
    "government-services",
    "security-compliance",
    "localization",
    "developer-tools",
    "communication",
    "food-and-dining",
    "legal-tech",
    "education",
    "health-services",
    "marketing-growth",
    "accounting",
    "travel",
]

KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Agent Skills specification: name is 1-64 characters.
MAX_NAME_LENGTH = 64

FORBIDDEN_NAMES = ["claude", "anthropic"]

# GitHub login rules: 1-39 alphanumerics or single hyphens, no leading or
# trailing hyphen. The directory builds the creator link and avatar from it.
GITHUB_LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
RESERVED_AUTHORS = ["skills-il"]

SKILL_MD_TEMPLATE = """---
name: {name}
description: >-
  TODO: [Third-person verb: Validates/Calculates...] [what it does]. Use when user
  asks to [triggers], "[Hebrew transliteration]", or [scenarios]. [Key capabilities].
  Do NOT use for [anti-triggers].
license: MIT
compatibility: >-
  TODO: [Requirements, or delete this field]. Keep it consistent with supported_agents in metadata.json.
---

# TODO: Skill Display Name

## Instructions

### Step 1: TODO
TODO: Clear, actionable instructions.

## Examples

### Example 1: TODO
User says: "TODO"
Actions:
1. TODO
Result: TODO

## Bundled Resources

### Scripts
- `scripts/TODO.py` -- TODO: What it does. Run: `python3 scripts/TODO.py --help`

### References
- `references/TODO.md` -- TODO: What it contains. Consult when TODO.

## Gotchas

- TODO: An agent failure mode (not a user error) observed in your baseline run.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| TODO | TODO | TODO |

## Troubleshooting

### Error: "TODO"
Cause: TODO
Solution: TODO
"""

SKILL_HE_TEMPLATE = """---
name: {name}
description: >-
  TODO: [Third-person verb: Validates/Calculates...] [what it does]. Use when user
  asks to [triggers], "[Hebrew transliteration]", or [scenarios]. [Key capabilities].
  Do NOT use for [anti-triggers].
license: MIT
---

# שם הסקיל בעברית (TODO)

## הוראות

### שלב 1: TODO
הוראות ברורות בעברית (TODO).

## דוגמאות

### דוגמה 1: TODO
המשתמש אומר: "TODO"
פעולות:
1. TODO
תוצאה: TODO

## משאבים מצורפים

### סקריפטים
- הסקריפט `scripts/TODO.py` (TODO)

### מסמכי עזר
- הקובץ `references/TODO.md` (TODO)

## מלכודות נפוצות

- כשל שהסוכן נופל בו, לא טעות של המשתמש (TODO).

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| TODO | TODO | TODO |

## פתרון בעיות

### שגיאה: "TODO"
סיבה: TODO
פתרון: TODO
"""


def validate_name(name: str) -> list[str]:
    """Validate skill name and return list of errors."""
    errors = []

    if not KEBAB_CASE_PATTERN.match(name):
        errors.append(
            f"Name '{name}' is not kebab-case. "
            "Use only lowercase letters, numbers, and hyphens."
        )

    if len(name) > MAX_NAME_LENGTH:
        errors.append(
            f"Name '{name}' is {len(name)} characters. "
            f"The Agent Skills specification allows at most {MAX_NAME_LENGTH}."
        )

    for forbidden in FORBIDDEN_NAMES:
        if forbidden in name.lower():
            errors.append(
                f"Name '{name}' contains forbidden word '{forbidden}'. "
                "Skill names cannot include 'claude' or 'anthropic'."
            )

    return errors


def validate_author(author: str) -> list[str]:
    """Validate the author is shaped like a GitHub login and is not reserved."""
    if not GITHUB_LOGIN_PATTERN.match(author):
        return [
            f"Author '{author}' is not a GitHub login. Use your GitHub username "
            "(letters, digits, single hyphens), not a full name or brand."
        ]
    if author.lower() in RESERVED_AUTHORS:
        return [
            f"Author '{author}' is reserved for skills authored by the skills-il "
            "team. Use your own GitHub username."
        ]
    return []


def validate_category(category: str) -> list[str]:
    """Validate category and return list of errors."""
    if category not in VALID_CATEGORIES:
        return [
            f"Category '{category}' is not valid. "
            f"Choose from: {', '.join(VALID_CATEGORIES)}"
        ]
    return []


def scaffold(name: str, category: str, author: str, base_dir: str) -> None:
    """Create the skill folder structure with templates."""
    skill_dir = Path(base_dir) / name

    if skill_dir.exists():
        print(f"Error: Folder '{skill_dir}' already exists.", file=sys.stderr)
        sys.exit(1)

    # Create directories
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()

    # Create SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        name=name, category=category, author=author
    )
    (skill_dir / "SKILL.md").write_text(skill_md.lstrip())

    # Create SKILL_HE.md
    skill_he = SKILL_HE_TEMPLATE.format(
        name=name, category=category, author=author
    )
    (skill_dir / "SKILL_HE.md").write_text(skill_he.lstrip())

    # Create metadata.json (all enriched metadata lives here, NOT in SKILL.md
    # frontmatter, because Claude Desktop rejects the metadata key in YAML).
    metadata = {
        "author": author,
        "version": "1.0.0",
        "category": category,
        "tags": {
            "he": ["TODO", "ישראל"],
            "en": ["TODO", "israel"],
        },
        "display_name": {
            "he": "TODO: Hebrew display name",
            "en": "TODO English Display Name",
        },
        "display_description": {
            "he": "TODO: Hebrew description",
            "en": "TODO: English description (mirrors the main description field)",
        },
        "supported_agents": [
            "claude-code",
            "cursor",
            "github-copilot",
            "windsurf",
            "opencode",
            "codex",
            "gemini-cli",
        ],
    }
    (skill_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    )

    # Create .gitkeep files for empty dirs
    (skill_dir / "scripts" / ".gitkeep").touch()
    (skill_dir / "references" / ".gitkeep").touch()

    print(f"Skill '{name}' scaffolded at: {skill_dir}")
    print()
    print("Created files:")
    print(f"  {skill_dir}/SKILL.md          -- Fill in frontmatter and instructions")
    print(f"  {skill_dir}/SKILL_HE.md       -- Fill in Hebrew companion")
    print(f"  {skill_dir}/metadata.json     -- Fill in tags, display names, agents")
    print(f"  {skill_dir}/scripts/          -- Add helper scripts")
    print(f"  {skill_dir}/references/       -- Add reference documentation")
    print()
    print("Next steps:")
    print("  1. Edit SKILL.md -- replace all TODO placeholders (keep frontmatter minimal)")
    print("     Regulated domain? See Step 4.5: '## Legal notice' in SKILL.md and")
    print("     '## הבהרה משפטית' in SKILL_HE.md, right after the H1.")
    print("  2. Edit metadata.json -- fill in tags (he/en), display names, supported_agents")
    print("  3. Write instructions with tables, code examples, and Hebrew terms")
    print("  4. Translate to Hebrew in SKILL_HE.md")
    print(f"  5. Validate: ./scripts/validate-skill.sh {name}/SKILL.md (structural only)")
    print(f"  6. Before submitting: grep -rn TODO {name}/ must print nothing")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new skills-il skill folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --name israeli-court-decisions --category government-services --author my-github-login\n"
            "  %(prog)s --name hebrew-spell-checker --category localization --author my-github-login\n"
        ),
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Skill name in kebab-case (must match folder name)",
    )
    parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
        help="Category repository",
    )
    parser.add_argument(
        "--author",
        required=True,
        help=(
            "Your GitHub username for metadata.json. Must be a real GitHub "
            "account: the directory builds the creator link and avatar from it."
        ),
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Base directory to create skill in (default: current directory)",
    )

    args = parser.parse_args()

    # Validate
    errors = (
        validate_name(args.name)
        + validate_category(args.category)
        + validate_author(args.author)
    )
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    scaffold(args.name, args.category, args.author, args.dir)


if __name__ == "__main__":
    main()
