---
name: israeli-id-validator
description: Validate and format Israeli identification numbers including Teudat Zehut (personal ID), company numbers, amuta (non-profit) numbers, and partnership numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar zehut", company number validation, or needs to implement Israeli ID validation in code. Includes check digit algorithm and test ID generation. Do NOT use for non-Israeli identification systems.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. Works with Claude Code, Claude.ai, Cursor.
version: 1.1.2
---

# Israeli ID Validator

## Instructions

### Step 1: Identify ID Type
| Type | Prefix | Length | Example | Notes |
|------|--------|--------|---------|-------|
| Teudat Zehut (personal ID) | none (cannot be inferred) | 9 digits | 123456782 | Assigned sequentially; the digits encode NO birth date, age, or residency status |
| Corporate / registered entity | first digit 5 | 9 digits | 51-530820-3 | Lives in the 5XX-million block; the number begins with 5 and the second digit selects the entity type (codes 50-59, see next table). Same check digit as a personal ID |

Corporate and registered-entity codes (first two digits):

| Prefix | Entity |
|--------|--------|
| 50 | Government company, pension/provident fund, or local committee |
| 51 | Private company (Chevra Ba'am / Ltd) |
| 52 | Public company |
| 53 | Mandatory partnership |
| 54 | General partnership |
| 55 | Partnership (Shutafut) |
| 56 | Foreign company |
| 57 | Cooperative society (Aguda Shitufit) / kibbutz |
| 58 | Amuta (non-profit) / public-benefit company |
| 59 | Endowment (Hekdesh) |

Prefix-based typing is a heuristic: a 9-digit number starting with 5 is overwhelmingly a registered entity (corporate numbers are allocated from the 5XX block), but only the issuing registry is authoritative. A personal Teudat Zehut cannot be typed from its prefix.

### Step 2: Validate Using Check Digit Algorithm
The Israeli ID check digit algorithm (applies to all types):

```python
def validate_israeli_id(id_number: str) -> bool:
    """Validate Israeli ID number (TZ, company, amuta, etc.)"""
    # Remove dashes and spaces, pad to 9 digits
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    if len(id_str) != 9 or not id_str.isdigit():
        return False

    if id_str == '000000000':   # passes Luhn but is never a real ID
        return False

    total = 0
    for i, digit in enumerate(id_str):
        # Position counting from left: odd positions (0,2,4,6,8) multiply by 1
        # Even positions (1,3,5,7) multiply by 2
        weight = 1 if i % 2 == 0 else 2
        val = int(digit) * weight
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
        weight = 1 if i % 2 == 0 else 2
        val = int(digit) * weight
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
- `scripts/validate_id.py` , Validates, identifies, formats, and generates Israeli ID numbers (Teudat Zehut, company, amuta, partnership). Supports verbose mode showing step-by-step check digit calculation, batch test ID generation with prefix control, and type identification from any ID number. Run: `python scripts/validate_id.py --help`

### References
- `references/id-formats.md` , Specification of all Israeli ID number formats including Teudat Zehut, company (51-prefix), amuta (58-prefix), partnership (55-prefix), and cooperative society (57-prefix) with issuing authorities, format patterns, the Luhn-variant check digit algorithm with a worked example, and common validation errors. Consult when implementing validation logic or debugging check digit failures.

## Reference Links

- [Misrad HaPnim, ID numbering page (gov.il)](https://www.gov.il/he/departments/topics/identity_card) , Official Ministry of Interior page on Teudat Zehut issuance, structure, and renewal.
- [ICA Companies Registrar (justice.gov.il)](https://ica.justice.gov.il/) , Lookup for company (51), amuta (58), partnership (55), and cooperative society (57) numbers.
- [Kolzchut, "תעודות זהות, דרכונים ותעודות מעבר"](https://www.kolzchut.org.il/he/תעודות_זהות,_דרכונים_ותעודות_מעבר) , Citizen-rights wiki hub for identity cards, passports, and travel documents, covering eligibility, replacement, and number ranges.
- [Privacy Protection Law, Amendment 13 (IAPP analysis)](https://iapp.org/news/a/israel-marks-a-new-era-in-privacy-law-amendment-13-ushers-in-sweeping-reform) , 2025 amendment tightening consent, breach-notification, and PII handling rules. In force 14 August 2025.

## Gotchas

- Israeli ID numbers (Teudat Zehut) are exactly 9 digits with a Luhn (mod 10) check digit. Agents may generate random 9-digit numbers that fail the check digit validation.
- Israeli ID numbers with fewer than 9 digits must be left-padded with zeros. An ID like "12345678" is actually "012345678". Agents may strip leading zeros and break validation.
- Israeli ID numbers are NOT date-encoded. They are assigned sequentially; you cannot infer birth date, age, birth year, or residency status from the digits. Agents trained on US SSN-style intuition often invent this assumption.
- Do not type or reject a personal ID by its leading-digit range. There is no documented citizen-status encoding in the number (the common "native vs resident vs foreign-worker by range" split is folklore). Every personal ID passes the same Luhn check regardless of its first digit; treat them all as plain 9-digit IDs.
- PII / privacy logging: never log unredacted Israeli IDs in application logs, error messages, telemetry, or analytics events. Israel's Privacy Protection Law Amendment 13 (in force 14 August 2025) tightens consent and breach-notification rules. When displaying an ID to a non-authorized context (debug UI, support tooling, customer-facing receipt), mask the middle digits, e.g. `123****82`. Hash or tokenize before persisting in non-essential stores.
- Israeli military IDs (mispar ishi) use a different format than civilian IDs and should not be validated with the same algorithm.
- `000000000` passes the Luhn check (its digit sum is 0, divisible by 10) but is never a real ID. It is the most common sentinel / empty-field false positive: an empty string or a numeric-default column zero-pads straight into it. Reject all-zeros explicitly before trusting a "valid" result.
- Do not reject a personal ID by its leading digit. There is no documented "temporary resident vs permanent" prefix for the 9-digit Luhn-checked Teudat Zehut; validate the format only and pad with `zfill(9)` rather than filtering by range.

## Troubleshooting

### Error: "ID appears valid but isn't recognized"
Cause: Check digit passes but the ID isn't issued
Solution: The algorithm only validates FORMAT, not existence. Verifying if an ID is actually issued requires Tax Authority or Interior Ministry systems.

### Error: "ID fails validation after a range/prefix filter"
Cause: An upstream filter is rejecting IDs by leading-digit range (e.g. treating a given first digit as "not a personal ID"), or the check digit is failing because the ID was stored as 8 digits with the leading zero dropped.
Solution: Every personal ID uses the same 9-digit Luhn check regardless of leading digit, and there is no reliable status-by-range mapping. Re-pad with leading zeros (`zfill(9)`) before validating, and remove any leading-digit range whitelist. Note that a 9-digit number starting with 5 is usually a registered entity, not a personal ID.

### Error: "Length mismatch / leading-zero stripped"
Cause: Spreadsheet, JSON parser, or numeric column dropped the leading zero (e.g., `012345678` stored as integer becomes `12345678`).
Solution: Always store IDs as strings. On read, left-pad to 9 with `zfill(9)` (Python) / `padStart(9, '0')` (JS) before running the check. Reject only after re-padding.

### Error: "Invalid input, dashes or spaces in ID"
Cause: User pasted a formatted company or amuta number such as `51-530820-3` or `58 012345 3`.
Solution: Strip all non-digit characters (`re.sub(r'\D', '', id)`) before length checks. Both human-formatted and raw-digit forms must validate identically.

### Error: "9-digit input but algorithm fails"
Cause: Common cause is a transposition or single-digit typo in the body of the ID, not the check digit itself. Other causes: copy-paste from a Hebrew RTL source where digit order was reversed, or the value is a military `mispar ishi` (which does not share the civilian Luhn algorithm).
Solution: Ask the user to retype the ID from the source document. If it still fails and the user insists it is correct, suggest an out-of-band verification with the issuing registry; do not "fix" check digits silently.
