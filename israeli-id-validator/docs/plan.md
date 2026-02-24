# Israeli ID Validator Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a skill for validating Israeli identification numbers — Teudat Zehut, company numbers, and other Israeli ID formats.

**Architecture:** Document/Asset Creation skill (Category 1). Embeds validation algorithms and ID format knowledge. Includes a Python validation script.

**Tech Stack:** SKILL.md, Python validation scripts.

---

## Research

### Israeli ID Types
- **Teudat Zehut (TZ):** 9-digit personal ID with Luhn-like check digit
- **Company Number (Chevra):** 51-XXXXXXX-C (9 digits)
- **Amuta Number:** 58-XXXXXXX-C
- **Partnership Number:** 55-XXXXXXX-C
- **Osek Morsheh Number:** Same as TZ for individuals, or company number

### TZ Validation Algorithm
1. Pad to 9 digits with leading zeros
2. Multiply each digit alternately by 1, 2, 1, 2, 1, 2, 1, 2, 1
3. If product > 9, sum the digits of the product (e.g., 18 -> 1+8=9)
4. Sum all results
5. Valid if total is divisible by 10

### Use Cases
1. **Validate TZ** — Check if an Israeli ID number is valid
2. **Validate company number** — Check corporate entity numbers
3. **Format ID** — Pad and format Israeli IDs correctly
4. **Explain algorithm** — Teach the validation algorithm
5. **Generate test IDs** — Create valid test IDs for development

---

## Build Steps

### Task 1: Create SKILL.md

```markdown
---
name: israeli-id-validator
description: >-
  Validate and format Israeli identification numbers including Teudat Zehut
  (personal ID), company numbers, amuta (non-profit) numbers, and partnership
  numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar
  zehut", company number validation, or needs to implement Israeli ID
  validation in code. Includes check digit algorithm and test ID generation.
  Do NOT use for non-Israeli identification systems.
license: MIT
allowed-tools: "Bash(python:*)"
compatibility: "No network required. Works with Claude Code, Claude.ai, Cursor."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [validation, id, teudat-zehut, developer, israel]
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

## Troubleshooting

### Error: "ID appears valid but isn't recognized"
Cause: Check digit passes but the ID isn't issued
Solution: The algorithm only validates FORMAT, not existence. Verifying if an ID is actually issued requires Tax Authority or Interior Ministry systems.
```
