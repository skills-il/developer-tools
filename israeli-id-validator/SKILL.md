---
name: israeli-id-validator
description: >-
  Validate and format Israeli identification numbers including Teudat Zehut
  (personal ID), company numbers, amuta (non-profit) numbers, and partnership
  numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar
  zehut", company number validation, or needs to implement Israeli ID validation
  in code. Includes check digit algorithm and test ID generation. Do NOT use for
  non-Israeli identification systems.
license: MIT
allowed-tools: 'Bash(python:*)'
compatibility: 'No network required. Works with Claude Code, Claude.ai, Cursor.'
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    - validation
    - id
    - teudat-zehut
    - developer
    - israel
  display_name:
    he: מאמת תעודת זהות
    en: Israeli Id Validator
  display_description:
    he: 'אימות מספרי תעודת זהות, ח"פ ומספרי רישום חברות'
    en: >-
      Validate and format Israeli identification numbers including Teudat Zehut
      (personal ID), company numbers, amuta (non-profit) numbers, and
      partnership numbers. Use when user asks to validate Israeli ID, "teudat
      zehut", "mispar zehut", company number validation, or needs to implement
      Israeli ID validation in code. Includes check digit algorithm and test ID
      generation. Do NOT use for non-Israeli identification systems.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
    - openclaw
---

# Israeli ID Validator

## Instructions

### Step 1: Identify ID Type
| Type | Prefix | Length | Example |
|------|--------|--------|---------|
| Teudat Zehut | Any | 9 digits | 123456782 |
| Company (Ltd) | 51 | 9 digits | 51-530820-1 |
| Amuta (Non-profit) | 58 | 9 digits | 58-012345-6 |
| Partnership | 55 | 9 digits | 55-012345-6 |

### Step 2: Validate Using Check Digit Algorithm
The Israeli ID check digit algorithm (applies to all types):

```python
def validate_israeli_id(id_number: str) -> bool:
    """Validate Israeli ID number (TZ, company, amuta, etc.)"""
    # Remove dashes and spaces, pad to 9 digits
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    if len(id_str) != 9 or not id_str.isdigit():
        return False

    total = 0
    for i, digit in enumerate(id_str):
        val = int(digit) * ((i % 2) + 1)  # Multiply by 1 or 2 alternately
        if val > 9:
            val = val // 10 + val % 10     # Sum digits if > 9
        total += val

    return total % 10 == 0
```

### Step 3: Provide Result
For valid IDs: Confirm valid, identify type by prefix
For invalid IDs: Report invalid, show which check failed, suggest common errors:
- Transposed digits
- Missing/extra digit
- Incorrect check digit

### Step 4: Generate Test IDs (Development Use)
For development and testing, generate valid test IDs:

```python
def generate_test_id(prefix: str = "") -> str:
    """Generate a valid Israeli ID number for testing."""
    import random
    base = prefix + ''.join([str(random.randint(0, 9)) for _ in range(8 - len(prefix))])
    # Calculate check digit
    total = 0
    for i, digit in enumerate(base):
        val = int(digit) * ((i % 2) + 1)
        if val > 9:
            val = val // 10 + val % 10
        total += val
    check = (10 - (total % 10)) % 10
    return base + str(check)
```

CAVEAT: Generated IDs are for testing only. Never use random IDs as real identification.

## Examples

### Example 1: Validate TZ
User says: "Is 123456782 a valid Israeli ID?"
Result: Run algorithm, report valid/invalid with explanation.

### Example 2: Code Implementation
User says: "I need Israeli ID validation in JavaScript"
Result: Provide equivalent algorithm in JavaScript.

### Example 3: Generate Test Data
User says: "I need 10 valid test company numbers"
Result: Generate 10 valid IDs with 51- prefix for testing.

## Bundled Resources

### Scripts
- `scripts/validate_id.py` — Validates, identifies, formats, and generates Israeli ID numbers (Teudat Zehut, company, amuta, partnership). Supports verbose mode showing step-by-step check digit calculation, batch test ID generation with prefix control, and type identification from any ID number. Run: `python scripts/validate_id.py --help`

### References
- `references/id-formats.md` — Specification of all Israeli ID number formats including Teudat Zehut, company (51-prefix), amuta (58-prefix), partnership (55-prefix), and cooperative society (57-prefix) with issuing authorities, format patterns, the Luhn-variant check digit algorithm with a worked example, and common validation errors. Consult when implementing validation logic or debugging check digit failures.

## Troubleshooting

### Error: "ID appears valid but isn't recognized"
Cause: Check digit passes but the ID isn't issued
Solution: The algorithm only validates FORMAT, not existence. Verifying if an ID is actually issued requires Tax Authority or Interior Ministry systems.
