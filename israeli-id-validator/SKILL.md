---
name: israeli-id-validator
description: Validate and format Israeli identification numbers including Teudat Zehut (personal ID), company numbers, amuta (non-profit) numbers, and partnership numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar zehut", company number validation, or needs to implement Israeli ID validation in code. Includes check digit algorithm and test ID generation. Do NOT use for non-Israeli identification systems.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. The bundled script needs Python 3.
---

# Israeli ID Validator

## Instructions

### Step 1: Identify ID Type
| Type | Prefix | Length | Example | Notes |
|------|--------|--------|---------|-------|
| Teudat Zehut (personal ID) | none (cannot be inferred) | 9 digits | 123456782 | The digits encode NO birth date, age, or residency status |
| Corporate / registered entity | usually begins with 5 | 9 digits | 51-530820-3 | The first two digits usually relate to the entity type (codes 50-59, see next table), a likely label, not a rule. Same check digit as a personal ID |

Corporate and registered-entity codes (first two digits):

| Prefix | Entity |
|--------|--------|
| 50 | Government company, pension/provident fund, or local committee |
| 51 | Private company (Chevra Ba'am / Ltd) |
| 52 | Public company |
| 53 | Mandate-era partnership (Shutafut Mandatorit, from the British Mandate period) |
| 54 | General partnership |
| 55 | Partnership (Shutafut) |
| 56 | Foreign company |
| 57 | Cooperative society (Aguda Shitufit) / kibbutz |
| 58 | Amuta (non-profit) / public-benefit company |
| 59 | Endowment (Hekdesh), not itself a corporation |

Prefix-based typing is a heuristic: a 9-digit number starting with 5 is usually a registered entity (the source says the first two digits "usually" relate to the entity type, and every listed code begins with 5), but only the issuing registry is authoritative. Never REJECT a number, or decide which field it belongs in, because of its prefix: use the prefix only to label a number the user already said is a company number. A personal Teudat Zehut cannot be typed from its prefix.

### Step 2: Validate Using Check Digit Algorithm
The Israeli ID check digit algorithm (applies to all types):

```python
import re


def validate_israeli_id(id_number: str) -> bool:
    """Validate Israeli ID number (TZ, company, amuta, etc.)"""
    # Discard ONLY the separators a human or a spreadsheet legitimately puts
    # inside an ID. Do NOT strip every non-digit: that silently turns
    # "62819482.1" into the VALID id 628194821, and turns "", "abc" and a row
    # of punctuation into "000000000". A validator that accepts garbage is
    # worse than one that rejects a real ID, because nobody finds out.
    # Do NOT gate on str.isdigit() either: it is True for Arabic-Indic digits
    # and superscripts, which either crash int() or validate as another value.
    # For the REASON (empty / malformed / bad check digit) use parse_id() in
    # scripts/validate_id.py; this compact version only answers yes or no.
    if not isinstance(id_number, str):
        return False        # an int has already lost its leading zeros
    # Trim whitespace, a CSV line break, the BOM and LRM/RLM/ALM at the ENDS only.
    # Inside the number a line break or bidi mark stays an error: bidi controls
    # can make the screen show different digits from the ones stored.
    EDGE = " \t\u00a0\r\n\u200b\ufeff\u200e\u200f\u061c"
    SEPARATORS = " -\u2010\u2011\u2013\u2014\u202f\u00a0\u00ad\u200b\u200c\u200d\u2060\ufeff"
    stripped = ''.join(c for c in id_number.strip(EDGE) if c not in SEPARATORS)

    if stripped == '' or not re.fullmatch(r'[0-9]{1,9}', stripped):
        return False        # malformed input, NOT an invalid ID

    id_str = stripped.zfill(9)

    if id_str == '000000000':   # passes Luhn but is never a real ID
        return False

    total = 0
    for i, digit in enumerate(id_str):
        # 1-based odd positions (indices 0,2,4,6,8) multiply by 1
        # 1-based even positions (indices 1,3,5,7) multiply by 2
        weight = 1 if i % 2 == 0 else 2
        val = int(digit) * weight
        if val > 9:
            val = val // 10 + val % 10     # Sum digits if > 9
        total += val

    return total % 10 == 0
```

### Step 3: Provide Result
For valid IDs: say the number passes the check digit (a well-formed number, not proof that it was issued or belongs to the person), and give the prefix-based type as a likely label only
For invalid IDs: Report invalid, show which check failed, suggest common errors:
- Transposed digits
- Missing/extra digit
- Incorrect check digit

### Step 4: Generate Test IDs (Development Use)
For development and testing, generate valid test IDs:

```python
def generate_test_id(prefix: str = "") -> str:
    """Generate a valid Israeli ID number for testing."""
    import random, re
    if not re.fullmatch(r'[0-9]{0,8}', prefix):
        raise ValueError("prefix must be 0-8 ASCII digits")   # else an 11-digit "ID"
    if prefix == '00000000':
        raise ValueError("an all-zeros prefix can only yield 000000000")
    while True:
        base = prefix + ''.join(str(random.randint(0, 9)) for _ in range(8 - len(prefix)))
        if base != '00000000':      # would yield 000000000, which validation rejects
            break
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

CAVEAT: Generated IDs are for testing only. Never use random IDs as real identification. A generated number that passes the check digit can still be a real person's issued ID; the generator has no way to know, so keep generated numbers out of anything a human or a third party sees (see Gotchas).

## Examples

### Example 1: Validate TZ
User says: "Is 123456782 a valid Israeli ID?"
Result: Run algorithm, report valid/invalid with explanation.

### Example 2: Code Implementation
User says: "I need Israeli ID validation in JavaScript"
Result: Use the tested port in `references/javascript.md` (it keeps the ID a string, pads with `padStart(9, '0')`, accepts only named separators and ASCII `[0-9]`), and run the golden vectors from `references/id-formats.md` as unit tests. Do not free-hand a port: dropping leading zeros through `Number()` and stripping with `\D` are the two ways JavaScript versions usually break.

### Example 3: Generate Test Data
User says: "I need 10 valid test company numbers"
Result: Generate 10 valid IDs with 51- prefix for testing.

## Bundled Resources

### Scripts
- `scripts/validate_id.py` , Validates, identifies, formats, and generates Israeli ID numbers (Teudat Zehut, company, amuta, partnership). Supports verbose mode showing step-by-step check digit calculation, batch test ID generation with prefix control, and type identification from any ID number. Exit codes: 0 valid, 1 well-formed but failing the check digit, 2 malformed input. `validate --mask` prints only the last 4 digits, for logs and CI output. Run: `python scripts/validate_id.py --help`

### References
- `references/id-formats.md` , Specification of all Israeli ID number formats including Teudat Zehut, registered entities (the whole 50-59 block: company, public company, partnership, cooperative society, amuta, endowment) with issuing authorities, format patterns, the Luhn-variant check digit algorithm with a worked example, a table of golden test vectors (valid, transposed, off-by-one, all-zeros, dropped leading zero, malformed), and common validation errors. Consult when implementing validation logic or debugging check digit failures.
- `references/javascript.md` , A JavaScript port cross-checked against the Python script, plus the ways JavaScript ports usually break. Use it whenever the user needs browser or Node validation.

## Reference Links

- [Population and Immigration Authority, "Request an identity card" (gov.il)](https://www.gov.il/he/service/biometric_smart_id_request) , Official service page for applying for a Teudat Zehut. The former topic page (`/he/departments/topics/identity_card`) now returns a 404.
- [Corporations Authority online registry (justice.gov.il)](https://ica.justice.gov.il/) , Lookup for companies, partnerships and amutot. Cooperative societies (prefix 57) are supervised by a separate Registrar of Cooperative Societies, so a real 57-number may not be found here.
- [Kolzchut, "תעודות זהות, דרכונים ותעודות מעבר"](https://www.kolzchut.org.il/he/תעודות_זהות,_דרכונים_ותעודות_מעבר) , Citizen-rights wiki hub for identity cards, passports, and travel documents, covering how to obtain and replace them.
- [Privacy Protection Law, Amendment 13 (law.co.il analysis)](https://www.law.co.il/news/2025/08/14/ppa-is-updating-its-guidelines-following-amendment-13/) , 2025 amendment making comprehensive changes to the Privacy Protection Law. In force 14 August 2025.

## Gotchas

- Israeli ID numbers (Teudat Zehut) are exactly 9 digits with a Luhn (mod 10) check digit. Agents may generate random 9-digit numbers that fail the check digit validation.
- Israeli ID numbers with fewer than 9 digits must be left-padded with zeros. An ID like "12345678" is actually "012345678". Agents may strip leading zeros and break validation.
- Israeli ID numbers are NOT date-encoded. You cannot infer birth date, age, birth year, or residency status from the digits. Agents trained on US SSN-style intuition often invent this assumption.
- Do not type or reject a personal ID by its leading-digit range. There is no documented citizen-status encoding in the number (the common "native vs resident vs foreign-worker by range" split is folklore). Every personal ID passes the same Luhn check regardless of its first digit; treat them all as plain 9-digit IDs.
- PII / privacy logging: never log unredacted Israeli IDs in application logs, error messages, telemetry, or analytics events. Israel's Privacy Protection Law was comprehensively amended by Amendment 13 (in force 14 August 2025), and a severe security incident must be reported to the Privacy Protection Authority immediately (see next item). When displaying an ID to a non-authorized context (debug UI, support tooling, customer-facing receipt), mask down to the last 4 digits at most, e.g. `xxxxx6782`. Before persisting in non-essential stores, use HMAC-SHA256 with a secret pepper held outside the database, or a tokenization vault. A plain unkeyed hash of an ID is not protection: the whole keyspace is under 10^9 and a check digit cuts it further, so the entire table is reversible by brute force in seconds.
- **Privacy compliance beyond code hygiene is out of scope here.** The Privacy Protection Authority is enforcing Amendment 13: in July 2026 it imposed its first monetary sanction since the amendment took effect (256,000 NIS after the statutory reductions, on a health fund) for failing to report a severe security incident to the Authority immediately, as the Information Security Regulations require, and it stated that the duty arises when the incident becomes known. A database of ID numbers is likely to fall under those regulations. For the compliance programme itself (security levels, incident reporting, whether you must appoint a privacy protection officer) use the `israeli-privacy-shield` skill and confirm with counsel; this validator covers only the code-level rules above.
- A sole trader's business number is not a 5x registered-entity number: the osek number on an osek patur certificate is usually the owner's personal 9-digit Teudat Zehut (5x numbers are given on registration with the Corporations Authority). A "business number" field that accepts only 5x numbers therefore rejects sole traders. Accept both shapes wherever you ask for a business number; both pass the same check digit.
- The IDF personal number (mispar ishi) is a separate, IDF-issued identifier and is out of scope for this skill. Do not run it through the civilian check-digit algorithm: this skill documents no check digit for it, so a pass or fail result would be meaningless.
- `000000000` passes the Luhn check (its digit sum is 0, divisible by 10) but is never a real ID. It is a common sentinel / empty-field false positive: an empty string or a numeric-default column zero-pads straight into it. Reject all-zeros explicitly before trusting a "valid" result.
- **Stripping every non-digit before validating is the bug that produces false positives.** It is the natural-looking one-liner, and it makes `62819482.1` validate as `628194821`. Discard a named separator set only, and treat anything else as malformed input rather than deleting it. This is the difference between a validator and a filter.
- **A reversed ID still passes the check digit.** The weights 1,2,1,2,1,2,1,2,1 read the same in both directions, so a 9-digit ID whose digits were reversed (for example a number taken from a visual-order PDF, OCR or an older system) ALWAYS validates: `287654321` is `123456782` backwards and passes. Only a reversed 8-digit value (leading zero dropped) usually fails. The check digit cannot catch reversal, so compare the number with what the user sees or typed, and never treat VALID as proof that the digit order is right. For the same reason never discard bidi override or isolate characters (U+202A to U+202E, U+2066 to U+2069): `"\u202e287654321"` displays on screen as 123456782 while storing 287654321.
- **An Israeli ID is at most 9 digits, so reject longer input rather than letting it fail the checksum.** `0000000018` is not "an invalid ID", it is not an ID at all, and telling the user their ID is invalid sends them looking for a typo that is not there.
- **A generated test ID can be a real person's ID.** Passing the check digit says nothing about whether the number was issued, and the generator cannot know. Never let generated numbers reach seed data that leaves the developer's machine, staging emails, screenshots, documentation or demo tenants. Where a fixture must be shown to people, use the published example `123456782` or a number that deliberately FAILS the check digit.
- **Your own CLI output is a log.** A full ID printed to a terminal lands in shell history and CI logs. Use `scripts/validate_id.py validate --mask`, which prints only the last 4 digits; `--verbose` prints every digit and refuses to combine with `--mask`.

## Troubleshooting

### Error: "ID appears valid but isn't recognized"
Cause: Check digit passes but the ID isn't issued
Solution: The algorithm only validates FORMAT, not existence. Only the issuing registry can say whether a number was issued: for companies, partnerships and amutot, the Corporations Authority search in Reference Links. This skill documents no public lookup for personal IDs.

### Error: "ID fails validation after a range/prefix filter"
Cause: An upstream filter is rejecting IDs by leading-digit range (e.g. treating a given first digit as "not a personal ID"), or the check digit is failing because the ID was stored as 8 digits with the leading zero dropped.
Solution: Every personal ID uses the same 9-digit Luhn check regardless of leading digit, and there is no reliable status-by-range mapping. Re-pad with leading zeros (`zfill(9)`) before validating, and remove any leading-digit range whitelist. Note that a 9-digit number starting with 5 is usually a registered entity, not a personal ID.

### Error: "Length mismatch / leading-zero stripped"
Cause: Spreadsheet, JSON parser, or numeric column dropped the leading zero (e.g., `012345678` stored as integer becomes `12345678`).
Solution: Always store IDs as strings. On read, left-pad to 9 with `zfill(9)` (Python) / `padStart(9, '0')` (JS) before running the check. Reject only after re-padding.

### Error: "Invalid input, dashes or spaces in ID"
Cause: User pasted a formatted company or amuta number such as `51-530820-3` or `58 012345 3`.
Solution: Discard only the separator characters (space, the hyphens and dashes, non-breaking and narrow no-break space, zero-width characters), and trim whitespace, tabs, line breaks and LRM/RLM marks at the ENDS only (a tab or line break inside the number is malformed), before the length check, then `zfill(9)`. Both the human-formatted and the raw-digit form must validate identically.

**Do not strip every non-digit.** `re.sub(r'[^0-9]', '', id)` looks like the same thing and is not: it deletes the offending characters instead of reporting them, so `62819482.1` becomes the **valid** ID `628194821`, and `""`, `"abc"` and `"!!!!!!!!!"` all become `000000000`. Use an explicit separator set, and reject anything else as malformed. Do not use `\d` or `str.isdigit()` for the digit test either: in Python both match Arabic-Indic digits, so `re.sub(r'\D', '', id)` lets them through to `int()`.

### Error: "Cannot tell an empty field from a bad ID"
Cause: The validator returns a single boolean, so "the user left this blank", "the user typed letters" and "this ID fails its check digit" all arrive as `False`, and the form shows the wrong message.
Solution: Return the reason, not just the verdict. `scripts/validate_id.py` distinguishes the three with exit codes: **0** valid, **1** a well-formed ID that fails its check digit, **2** malformed input, with the reason on stdout (`MALFORMED - too long: 10 digits`, `MALFORMED - empty input`, `MALFORMED - contains characters that are not digits or separators: '.'`). Script the exit code, not the text.

### Error: "9-digit input but algorithm fails"
Cause: Common cause is a transposition or single-digit typo in the body of the ID, not the check digit itself. Another cause: the value is a military `mispar ishi`, which is a separate IDF identifier this skill documents no check digit for (see Gotchas), so a failure says nothing about it.
Solution: Ask the user to retype the ID from the source document. If it still fails and the user insists it is correct, suggest an out-of-band verification with the issuing registry; do not "fix" check digits silently.
