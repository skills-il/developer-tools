#!/usr/bin/env python3
"""Scaffold a new skills-il skill folder with correct structure and templates.

Creates the complete folder structure for a new skill:
  <skill-name>/
  ├── SKILL.md          # Template with frontmatter skeleton
  ├── SKILL_HE.md       # Hebrew companion stub
  ├── scripts/          # For helper scripts
  └── references/       # For reference documentation

Usage:
  python scripts/scaffold-skill.py --name my-skill --category developer-tools
  python scripts/scaffold-skill.py --name my-skill --category tax-and-finance --author "My Name"
  python scripts/scaffold-skill.py --help
"""

import argparse
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
]

KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

FORBIDDEN_NAMES = ["claude", "anthropic"]

SKILL_MD_TEMPLATE = """---
name: {name}
description: >-
  TODO: [What it does]. Use when user asks to [triggers], "[Hebrew transliteration]",
  or [scenarios]. [Key capabilities]. Do NOT use for [anti-triggers].
license: MIT
allowed-tools: ''
compatibility: >-
  TODO: [Requirements]. Works with Claude Code, Claude.ai, Cursor.
metadata:
  author: {author}
  version: 1.0.0
  category: {category}
  tags:
    he:
      - TODO
      - ישראל
    en:
      - TODO
      - israel
  display_name:
    he: "TODO: Hebrew display name"
    en: TODO English Display Name
  display_description:
    he: "TODO: Hebrew description"
    en: >-
      TODO: English description (mirrors the main description field)
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
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
- `scripts/TODO.py` -- TODO: What it does. Run: `python scripts/TODO.py --help`

### References
- `references/TODO.md` -- TODO: What it contains. Consult when TODO.

## Troubleshooting

### Error: "TODO"
Cause: TODO
Solution: TODO
"""

SKILL_HE_TEMPLATE = """---
name: {name}
description: >-
  TODO: [What it does]. Use when user asks to [triggers], "[Hebrew transliteration]",
  or [scenarios]. [Key capabilities]. Do NOT use for [anti-triggers].
license: MIT
metadata:
  author: {author}
  version: 1.0.0
  category: {category}
---

# TODO: Hebrew Skill Name

## הוראות

### שלב 1: TODO
TODO: הוראות ברורות בעברית.

## דוגמאות

### דוגמה 1: TODO
המשתמש אומר: "TODO"
פעולות:
1. TODO
תוצאה: TODO

## משאבים מצורפים

### סקריפטים
- `scripts/TODO.py` -- TODO

### מסמכי עזר
- `references/TODO.md` -- TODO

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

    for forbidden in FORBIDDEN_NAMES:
        if forbidden in name.lower():
            errors.append(
                f"Name '{name}' contains forbidden word '{forbidden}'. "
                "Skill names cannot include 'claude' or 'anthropic'."
            )

    return errors


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

    # Create .gitkeep files for empty dirs
    (skill_dir / "scripts" / ".gitkeep").touch()
    (skill_dir / "references" / ".gitkeep").touch()

    print(f"Skill '{name}' scaffolded at: {skill_dir}")
    print()
    print("Created files:")
    print(f"  {skill_dir}/SKILL.md          -- Fill in frontmatter and instructions")
    print(f"  {skill_dir}/SKILL_HE.md       -- Fill in Hebrew companion")
    print(f"  {skill_dir}/scripts/          -- Add helper scripts")
    print(f"  {skill_dir}/references/       -- Add reference documentation")
    print()
    print("Next steps:")
    print("  1. Edit SKILL.md -- replace all TODO placeholders")
    print("  2. Write instructions with tables, code examples, and Hebrew terms")
    print("  3. Translate to Hebrew in SKILL_HE.md")
    print(f"  4. Validate: ./scripts/validate-skill.sh {name}/SKILL.md")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new skills-il skill folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --name israeli-court-decisions --category government-services\n"
            "  %(prog)s --name hebrew-spell-checker --category localization --author 'My Name'\n"
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
        default="skills-il",
        help="Author name for metadata (default: skills-il)",
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Base directory to create skill in (default: current directory)",
    )

    args = parser.parse_args()

    # Validate
    errors = validate_name(args.name) + validate_category(args.category)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    scaffold(args.name, args.category, args.author, args.dir)


if __name__ == "__main__":
    main()
