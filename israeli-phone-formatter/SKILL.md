---
name: israeli-phone-formatter
description: Validate, format, and convert Israeli phone numbers between local and international (+972) formats. Use when user asks to validate Israeli phone number, format phone for SMS or WhatsApp, convert to +972, check phone prefix, or implement Israeli phone input validation in code. Handles mobile (050-058), landline (02-09), non-geographic / VoIP (072-079), toll-free (1-800), and star-service numbers, and emits strict E.164 output for libphonenumber and WhatsApp Business API. Do NOT use for non-Israeli phone systems or general telecom questions.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. Works with Claude Code, Claude.ai, Cursor.
version: 1.2.0
---

# Israeli Phone Formatter

## Instructions

### Step 1: Identify Phone Number Type

| Type | Prefixes | Total Digits | Example (local) |
|------|----------|-------------|-----------------|
| Mobile | 050, 051, 052, 053, 054, 055, 058 | 10 | 052-1234567 |
| Mobile (Palestinian, flag) | 056 (Wataniya), 059 (Jawwal) | 10 | 059-1234567 |
| Landline | 02-04, 08-09 | 9 | 02-6251111 |
| Non-geographic / VoIP | 072, 073, 074, 076, 077, 078, 079 | 10 | 077-1234567 |
| Toll-free | 1-800 | 10 | 1-800-123456 |
| Premium | 1-700 | 10 | 1-700-123456 |
| Star service | *XXXX | 5-7 | *2421 |

For the full prefix allocation table per carrier, consult `references/prefix-allocation.md`.

### Step 2: Validate the Number

Run `python scripts/validate_phone.py --number {input}` to validate format and identify type.

If validating manually, apply these rules:
1. Strip all whitespace, hyphens, parentheses, and dots
2. Convert international prefix: `+972` or `972` becomes leading `0`
3. Match against known prefix patterns
4. Verify digit count (mobile / non-geographic = 10, landline = 9)

Common validation errors:
- **Wrong digit count**: Mobile numbers must be exactly 10 digits with the `0` prefix
- **Palestinian carriers slipping through**: 056 (Wataniya) and 059 (Jawwal) match the Israeli mobile shape but are Palestinian territories carriers. Flag them when business logic requires an Israeli SIM.
- **078 or 079 rejected as invalid**: Older regex patterns like `0(7[2-7])` reject both 078 (multiple VoIP providers) and 079 (Widely, 019 Mobile, Annatel). Use `07[2-9]` instead.
- **Missing leading zero**: Local numbers always start with `0` (except toll-free and star)

### Step 3: Format or Convert

**Local to international (strict E.164 for WhatsApp, Twilio, libphonenumber):**
1. Remove leading `0`
2. Prepend `+972`
3. Output **digits only**, no separators
4. Example: `052-1234567` becomes `+972521234567`

A hyphenated form like `+972-52-123-4567` is for human display only. Pass it to strict E.164 parsers (`google-libphonenumber`, `libphonenumber-js`, WhatsApp Business API, AWS SNS) and they will reject it. Store the canonical no-separator form and only render the hyphenated form in UI.

**International to local:**
1. Replace `+972` (or `972`) with `0`
2. Example: `+972-2-625-1111` becomes `02-6251111`

**Important:** Toll-free (1-800), premium (1-700), and star (*) numbers cannot be dialed internationally.

### Step 4: Generate Code

When the user needs validation in code, provide a function using regex patterns from `references/prefix-allocation.md`. Include:
- Input sanitization (strip formatting characters: spaces, hyphens, parens, dots)
- International prefix normalization
- Type detection by prefix
- Digit count verification per type
- Strict E.164 emitter (digits only) alongside the hyphenated display form
- For maximum interop, recommend `google-libphonenumber` (Python) or `libphonenumber-js` (JS); they handle MNP-aware metadata, region inference, and E.164 output natively. Use this skill's regex patterns for lightweight validation when adding the dependency is overkill.

### Step 5: Account for Mobile Number Portability (MNP)

Israel has had full mobile number portability since 2007. The prefix in a mobile number reflects the **issuing** carrier, not the active SIM provider. Do not bill, route SMS, or gate features on prefix-derived carrier inference. For live carrier identification use an HLR lookup or the operator's CNAM / portability lookup. Always surface this caveat when the user asks "which carrier owns 052?"

## Examples

### Example 1: Validate a Mobile Number
User says: "Is 052-1234567 a valid Israeli phone number?"
Actions:
1. Strip formatting: `0521234567`
2. Match prefix `052` = mobile (issued by Cellcom; live carrier may differ due to MNP)
3. Verify 10 digits total
Result: Valid Israeli mobile number (originally issued by Cellcom). E.164: +972521234567

### Example 2: Convert to International
User says: "Convert 02-6251111 to international format"
Actions:
1. Strip formatting: `026251111`
2. Match prefix `02` = Jerusalem landline
3. Drop leading `0`, prepend `+972`
Result: +972-2-625-1111 for display, or `+97226251111` for E.164 / WhatsApp

### Example 3: Batch Validation
User says: "Validate this list of phone numbers for my CRM import"
Actions:
1. Run `python scripts/validate_phone.py --batch --input contacts.csv`
2. Report valid / invalid counts with specific errors per row, including 056 / 059 flagged as non-Israeli
Result: Summary table with validation status per number

## Bundled Resources

### Scripts
- `scripts/validate_phone.py` -- Validates, formats, and converts Israeli phone numbers. Supports single number validation, batch CSV processing, format conversion between local and international, and strict E.164 output. Run: `python scripts/validate_phone.py --help`

### References
- `references/prefix-allocation.md` -- Complete Israeli phone prefix allocation table per Ministry of Communications, including issuing-carrier attribution for mobile prefixes (050-058 plus Palestinian 056 / 059), area codes for landlines, non-geographic ranges (072-079), MNP disclaimer, and E.164 / libphonenumber compatibility guidance.

## Recommended MCP Servers

No Israeli-telecom-specific MCP server is currently in the directory. For general phone-number parsing, the `libphonenumber-js` library (called from agent code) is the most widely-relied-on source of truth and matches what WhatsApp Business API, Twilio, and major messaging SDKs expect.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Telephone numbers in Israel (Wikipedia) | https://en.wikipedia.org/wiki/Telephone_numbers_in_Israel | Current prefix allocation, carrier assignments, area codes |
| Israeli Ministry of Communications (moc.gov.il) | https://www.gov.il/en/departments/ministry_of_communications | Official numbering plan changes and regulatory updates |
| libphonenumber (Google) | https://github.com/google/libphonenumber | Canonical E.164 validation rules used across major messaging SDKs |
| libphonenumber-js (npm) | https://www.npmjs.com/package/libphonenumber-js | JavaScript port commonly used in frontend phone-input components |

## Gotchas

- Israeli mobile numbers are 10 digits (05X-XXXXXXX) while landlines are 9 digits (0X-XXXXXXX). Agents may apply a single validation length for all Israeli numbers.
- When converting to international format (+972), the leading zero must be dropped: 052-1234567 becomes +972521234567, not +9720521234567. Agents frequently include the extra zero.
- WhatsApp Business API, Twilio, and libphonenumber require strict E.164 (digits only, no hyphens). The display form `+972-52-123-4567` will fail validation. Store digits-only and render hyphens only for humans.
- Mobile Number Portability has been live since 2007. The prefix indicates the original issuer, not the current carrier. Do not infer the active SIM from `052`, `054`, etc.
- 056 and 059 match the Israeli mobile shape but are Palestinian carriers (Wataniya, Jawwal). For Israeli-resident business logic, flag them separately rather than treating them as Israeli mobile numbers.
- 055 is a multi-MVNO range (Cellcom, 019 Mobile, Widely, Rami Levy, Cellact, Pelephone all issue 055 numbers); do not pin it to a single carrier.
- Israeli special numbers (police 100, ambulance 101, fire 102) are short codes that should not be formatted with country codes or area codes.
- 077 is a Hot Telecom non-geographic range (not a generic VoIP catch-all). 078 and 079 are commonly used by other VoIP / non-geographic providers (Widely, 019 Mobile, Annatel) and are both frequently missed by older `0(7[2-7])` regexes.
- Israeli area codes changed historically (02 for Jerusalem, 03 for Tel Aviv, 04 for Haifa, 08 for south, 09 for Sharon). Agents may use outdated area code mappings.
- Allocated Israeli mobile prefixes are 050, 051, 052, 053, 054, 055, 058, plus 056 and 059 for Palestinian carriers. 057 remains unallocated.

## Troubleshooting

### Error: "Valid prefix but wrong digit count"
Cause: Mixing up mobile (10 digits) and landline (9 digits) lengths
Solution: Mobile / non-geographic numbers always have 10 digits including the `0`. Landlines have 9. Count digits after stripping all formatting.

### Error: "078 or 079 rejected as invalid"
Cause: The regex `0(7[2-7])` excludes both 078 and 079, which are real allocations (Widely, 019 Mobile, Annatel and others).
Solution: Use `07[2-9]` for the non-geographic class. The bundled `validate_phone.py` already has this fix.

### Error: "Number starts with 05 but prefix not recognized"
Cause: Not all 05X prefixes are allocated to Israeli consumer mobile (057 is unused; 056 / 059 are Palestinian).
Solution: Check `references/prefix-allocation.md`. Israeli consumer mobile: 050, 051, 052, 053, 054, 055, 058. Palestinian (flag separately): 056, 059.

### Error: "Cannot convert toll-free to international"
Cause: 1-800 and 1-700 numbers are domestic-only
Solution: These numbers have no international equivalent. If the user needs international reach, suggest providing a standard landline or mobile number instead.

### Error: "WhatsApp / Twilio rejects +972-52-123-4567"
Cause: Hyphenated form is not strict E.164; downstream parsers want digits only.
Solution: Strip separators before sending. Use `validate_phone.to_e164()` or `phonenumbers.format_number(num, PhoneNumberFormat.E164)` to produce `+972521234567`.
