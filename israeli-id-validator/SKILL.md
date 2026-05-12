---
name: israeli-id-validator
description: Validate and format Israeli identification numbers including Teudat Zehut (personal ID), company numbers, amuta (non-profit) numbers, and partnership numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar zehut", company number validation, or needs to implement Israeli ID validation in code. Includes check digit algorithm and test ID generation. Do NOT use for non-Israeli identification systems.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. Works with Claude Code, Claude.ai, Cursor.
version: 1.1.0
---

# Israeli ID Validator

## Instructions

### Step 1: Identify ID Type
| Type | Prefix | Length | Example | Notes |
|------|--------|--------|---------|-------|
| Teudat Zehut (native-born) | 100-499 millions | 9 digits | 123456782 | Sequential, NOT date-encoded |
| Teudat Zehut (resident / temporary / foreign worker) | 500-899 millions | 9 digits | 612345678 | Issued to permanent residents, temp residents, foreign workers (3xx range commonly seen for foreign workers) |
| Company (Ltd) | 51 | 9 digits | 51-530820-1 | Issued by Companies Registrar |
| Partnership | 55 | 9 digits | 55-012345-6 | Issued by Registrar of Partnerships |
| Cooperative Society (Aguda Shitufit) | 57 | 9 digits | 57-012345-6 | Issued by Cooperative Societies Registrar |
| Amuta (Non-profit) | 58 | 9 digits | 58-012345-6 | Issued by Registrar of Amutot |

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
- [Privacy Protection Law, Amendment 13 (Knesset)](https://main.knesset.gov.il/Activity/Legislation/Laws/Pages/LawPrimary.aspx?lawitemid=2207011) , 2025 amendment tightening consent, breach-notification, and PII handling rules. In force August 2025.

## Gotchas

- Israeli ID numbers (Teudat Zehut) are exactly 9 digits with a Luhn (mod 10) check digit. Agents may generate random 9-digit numbers that fail the check digit validation.
- Israeli ID numbers with fewer than 9 digits must be left-padded with zeros. An ID like "12345678" is actually "012345678". Agents may strip leading zeros and break validation.
- Israeli ID numbers are NOT date-encoded. Numbers in the 100-499 million range are assigned sequentially to native-born citizens; you cannot infer birth date, age, or birth year from the digits. Agents trained on US SSN-style intuition often invent this assumption.
- Foreign-worker IDs commonly land in the 3xx-million sub-range of the 500-899 million resident block. Agents may flag them as "non-Israeli" or strip them entirely. They pass the same Luhn check; treat them like any other 9-digit ID.
- PII / privacy logging: never log unredacted Israeli IDs in application logs, error messages, telemetry, or analytics events. Israel's Privacy Protection Law Amendment 13 (in force August 2025) tightens consent and breach-notification rules. When displaying an ID to a non-authorized context (debug UI, support tooling, customer-facing receipt), mask the middle digits, e.g. `123****82`. Hash or tokenize before persisting in non-essential stores.
- Israeli military IDs (mispar ishi) use a different format than civilian IDs and should not be validated with the same algorithm.
- Israeli temporary resident IDs start with specific digit patterns. Agents may reject valid temporary IDs because they do not match permanent ID patterns.

## Troubleshooting

### Error: "ID appears valid but isn't recognized"
Cause: Check digit passes but the ID isn't issued
Solution: The algorithm only validates FORMAT, not existence. Verifying if an ID is actually issued requires Tax Authority or Interior Ministry systems.

### Error: "Foreign worker ID fails validation"
Cause: Agent or upstream filter is rejecting IDs in the 5xx-8xx range as "not Israeli", or the check digit is failing because the ID was stored as 8 digits with the leading digit dropped.
Solution: Foreign-worker and temporary-resident IDs use the same 9-digit Luhn check as native-born IDs. Re-pad with leading zeros (`zfill(9)`) before validating, and remove any prefix-range whitelist that excludes the 500-899 million block.

### Error: "Length mismatch / leading-zero stripped"
Cause: Spreadsheet, JSON parser, or numeric column dropped the leading zero (e.g., `012345678` stored as integer becomes `12345678`).
Solution: Always store IDs as strings. On read, left-pad to 9 with `zfill(9)` (Python) / `padStart(9, '0')` (JS) before running the check. Reject only after re-padding.

### Error: "Invalid input, dashes or spaces in ID"
Cause: User pasted a formatted company or amuta number such as `51-530820-1` or `58 012345 6`.
Solution: Strip all non-digit characters (`re.sub(r'\D', '', id)`) before length checks. Both human-formatted and raw-digit forms must validate identically.

### Error: "9-digit input but algorithm fails"
Cause: Common cause is a transposition or single-digit typo in the body of the ID, not the check digit itself. Other causes: copy-paste from a Hebrew RTL source where digit order was reversed, or the value is a military `mispar ishi` (which does not share the civilian Luhn algorithm).
Solution: Ask the user to retype the ID from the source document. If it still fails and the user insists it is correct, suggest an out-of-band verification with the issuing registry; do not "fix" check digits silently.
