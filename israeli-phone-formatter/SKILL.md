---
name: israeli-phone-formatter
description: Validate, format, and convert Israeli phone numbers between local and international (+972) formats. Use when user asks to validate Israeli phone number, format phone for SMS or WhatsApp, convert to +972, check phone prefix, or implement Israeli phone input validation in code. Handles mobile (050-055, 058, plus Palestinian 056/059), landline (02, 03, 04, 08, 09), non-geographic (072-074, 076, 077, 079), toll-free (1-800), shared-cost 1-700, premium 1-900, and star-service numbers, and emits strict E.164 output for libphonenumber and WhatsApp Business API. Do NOT use for non-Israeli phone systems or general telecom questions.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. Works with Claude Code, Claude.ai, Cursor.
---

# Israeli Phone Formatter

## Instructions

### Step 1: Identify Phone Number Type

| Type | Prefixes | Total Digits | Example (local) |
|------|----------|-------------|-----------------|
| Mobile | 050, 051, 052, 053, 054, 055, 058 | 10 | 052-3456789 |
| Mobile (Palestinian, flag) | 056 (Ooredoo Palestine, formerly Wataniya), 059 (Jawwal) | 10 | 059-2345678 |
| Landline | 02, 03, 04, 08, 09 | 9 | 02-6251111 |
| Non-geographic (national) | 072, 073, 074, 076, 077, 079 | 10 | 077-2345678 |
| Toll-free | 1-800, 1-801 (1-809 for international operators) | 10 | 1-800-123456 |
| Shared-cost | 1-700 (caller billed as a local call) | 10 | 1-700-123456 |
| Business call router | 1-599 | 10 | 1-599-123456 |
| Premium rate | 1-900, 1-901, 1-902, 1-919 | 10 | 1-900-123456 |
| Star business number | *XXXX | 5 | *2421 |

The structure comes from the Ministry of Communications numbering plan: geographic numbers are `0A-NXX-XXXX`, mobile `05R-NXX-XXXX`, national `07P-NXX-XXXX` with P = 2-9, and the first subscriber digit N is 2-9. In mobile ranges N = 0-1 is reserved for M2M / IoT SIMs. For the per-prefix allocation, consult `references/prefix-allocation.md`.

### Step 2: Validate the Number

Run `python scripts/validate_phone.py --number {input}` to validate format and identify type.

If validating manually, apply these rules:
1. Normalise: NFKC (full-width digits), Arabic-Indic digits to ASCII, drop bidi marks (U+200E / U+200F, inserted by Hebrew RTL apps on copy), every dash variant, slashes, parentheses, dots, spaces and surrounding text such as `Tel:`
2. Convert international prefix: `+972`, `00972` or `972` becomes leading `0`; also drop a trunk zero written after the code (`+972 (0)52...`, `+9720 52...`)
3. A bare-digit cell of 9 digits starting with 5 or 7, or 8 digits starting with 2, 3, 4, 8 or 9, has probably lost its leading 0 (Excel does this to numeric cells). Restore it but mark it for confirmation, since an ID or company number has the same shape; never restore when the input has other characters (dates, amounts). A cell like `5.23457E+08` has lost digits: reject it as unrecoverable. A 7-digit number is a landline dialed without its area code: ask for the area code
4. Match against known prefix patterns
5. Verify digit count (mobile / non-geographic = 10, landline = 9) and that the first subscriber digit is 2-9

"Valid" means the number has the shape of an allocated class. It does not prove the sub-block is assigned, the line is live, or that it reaches a person (M2M and Palestinian ranges are valid but flagged). For signups, confirm with an OTP; for sub-block precision, use libphonenumber.

Common validation errors:
- **Wrong digit count**: Mobile numbers must be exactly 10 digits with the `0` prefix
- **Palestinian ranges slipping through**: 056 and 059 match the Israeli mobile shape, and the landline blocks 02-2, 04-2, 08-2 and 09-2 (`0A-2XXXXXX`) are allocated to Palestinian operators. Flag them when business logic requires an Israeli line.
- **1-700 treated as premium**: 1-700 is shared-cost (the caller pays a local-call rate). Premium rate is 1-900 / 1-901 / 1-902 / 1-919.
- **Accepting unallocated 07X**: 070, 071, 075 and 078 have no allocation in the current MoC table. A loose `07\d` regex accepts them; use `07[2-46-79]`.
- **Missing leading zero**: Local numbers always start with `0` (except service numbers starting with `1` and star numbers)

### Step 3: Format or Convert

**Local to international (E.164, the canonical storage form):**
1. Remove leading `0`
2. Prepend `+972`
3. Output **digits only**, no separators
4. Example: `052-3456789` becomes `+972523456789`

Store the digits-only E.164 form and render hyphens only in UI. `libphonenumber` parsing tolerates separators, and the WhatsApp Cloud API accepts `+`, hyphens, parentheses and spaces, but WhatsApp needs the `+` and country code: without the `+`, Meta prepends the business number's own country code, so the message can be misdelivered. Never send a local `05X` number to WhatsApp.

**International to local:**
1. Replace `+972` (or `972`) with `0`
2. Example: `+972-2-625-1111` becomes `02-6251111`

**Important:** 1-XXX service numbers (toll-free, 1-700, 1-599, premium), star numbers and short codes are domestic-only. Do not emit a +972 form for them; most are not reachable from abroad.

### Step 4: Generate Code

When the user needs validation in code, provide a function using regex patterns from `references/prefix-allocation.md`. Include:
- Input sanitization (the Step 2 normalisation: Unicode digits, bidi marks, dash variants, surrounding text)
- International prefix normalization, including `+972 (0)` and a lost leading 0
- Type detection by prefix
- Digit count verification per type
- Strict E.164 emitter (digits only) alongside the hyphenated display form
- For maximum interop, recommend `google-libphonenumber` (Python) or `libphonenumber-js` (JS); they handle region inference, sub-block metadata, and E.164 output natively. Use this skill's regex patterns for lightweight validation when adding the dependency is overkill. Their metadata can lag or lead the MoC table (libphonenumber still accepts a few 071 / 078 blocks), so for an authoritative answer check the MoC allocation dataset.

### Step 5: Account for Mobile Number Portability (MNP)

Number portability in Israel began on 2 December 2007. The prefix in a mobile number reflects the **issuing** operator, not the active SIM provider. Do not bill, route SMS, or gate features on prefix-derived carrier inference. For live carrier identification use an HLR lookup or the operator's portability lookup. Always surface this caveat when the user asks "which carrier owns 052?"

## Examples

### Example 1: Validate a Mobile Number
User says: "Is 052-3456789 a valid Israeli phone number?"
Actions:
1. Strip formatting: `0523456789`
2. Match prefix `052` = mobile (issued by Cellcom; live carrier may differ due to MNP)
3. Verify 10 digits total and first subscriber digit `3` (2-9, a person's number, not M2M)
Result: Valid Israeli mobile number (originally issued by Cellcom). E.164: +972523456789

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
1. Run `python scripts/validate_phone.py --batch --input contacts.csv --column 2` (comma, semicolon or tab separated; a header row is skipped)
2. Report valid / invalid counts with the type and E.164 per row, plus the note column: `LEADING_ZERO_RESTORED` (status `VALID_CONFIRM`, confirm before import), `MULTIPLE_NUMBERS` (a second number in the cell was dropped), `UNRECOVERABLE`, `LOCAL_7_DIGITS`, `DUPLICATE`, `FOREIGN`, `PALESTINIAN_CARRIER`, `M2M_RANGE`, or `DOMESTIC_ONLY`. Do not delete `FOREIGN` rows: they may be real contacts abroad
Result: Tab-separated table per number; the script exits 1 if any row is invalid

## Bundled Resources

### Scripts
- `scripts/validate_phone.py` -- Validates, formats, and converts Israeli phone numbers. Supports single number validation, batch processing (stdin or `--input` CSV with `--column`), input normalisation, `--format local|international|e164` conversion, and E.164 output. Run: `python scripts/validate_phone.py --help`

### References
- `references/prefix-allocation.md` -- Israeli prefix allocation per the Ministry of Communications table, including issuing-operator attribution for mobile prefixes (050-055, 058 plus Palestinian 056 / 059), M2M blocks, landline area codes, non-geographic ranges (072-074, 076, 077, 079), service numbers (1-800, 1-700, 1-599, premium), short codes, MNP disclaimer, and E.164 / libphonenumber guidance.

## Recommended MCP Servers

No Israeli-telecom-specific MCP server is currently in the directory. For general phone-number parsing, the `libphonenumber-js` library (called from agent code) is the most widely-relied-on source of truth and produces the E.164 form that messaging APIs expect.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| MoC numbering plan (Feb 2023, edition 4, Hebrew) | https://www.gov.il/BlobFolder/policy/number_policy/en/The_numbering_plan-02-2023.pdf | Number structure (0A, 05R, 07P), digit rules, MNP start date, star numbers |
| MoC number allocations (data.gov.il) | https://data.gov.il/dataset/israel-numbering-plan | Which operator holds each range, M2M blocks, Palestinian ranges |
| MoC service and short numbers (data.gov.il) | https://data.gov.il/dataset/israel-dialing-plan | 1-800 / 1-700 / 1-599 / 1-900 meaning, emergency short codes |
| Telephone numbers in Israel (Wikipedia) | https://en.wikipedia.org/wiki/Telephone_numbers_in_Israel | Operator brand names and history |
| libphonenumber (Google) | https://github.com/google/libphonenumber | Canonical E.164 validation rules used across major messaging SDKs |
| libphonenumber-js (npm) | https://www.npmjs.com/package/libphonenumber-js | JavaScript port commonly used in frontend phone-input components |

## Gotchas

- Israeli mobile numbers are 10 digits (05X-XXXXXXX) while landlines are 9 digits (0X-XXXXXXX). Agents may apply a single validation length for all Israeli numbers.
- When converting to international format (+972), the leading zero must be dropped: 052-3456789 becomes +972523456789, not +9720523456789. Agents frequently include the extra zero.
- WhatsApp needs the `+` and country code. Sent without the `+`, Meta prepends the business number's own country code, so a number sent as `0523456789` or `523456789` from a non-Israeli business account can be undelivered or misdelivered. Always send `+972...`.
- Mobile Number Portability has been live since December 2007. The prefix indicates the original issuer, not the current carrier. Do not infer the active SIM from `052`, `054`, etc.
- 1-700 is NOT premium rate. Agents label it premium by analogy with other countries; in Israel it is a shared-cost number and premium rate lives on 1-900 / 1-901 / 1-902 / 1-919.
- 055 is a multi-operator range split into sub-blocks (019 Telzar, Rami Levy, Cellcom, Cellact, Annatel, Widely, Pelephone and several smaller operators); do not pin it to a single carrier.
- Mobile numbers whose fourth digit is 0 or 1 (e.g. 052-1XXXXXX, 054-0XXXXXX) are M2M / IoT ranges. The common placeholder 052-1234567 is one of them, so do not use it as a "typical person's number" example.
- Israeli emergency numbers (police 100, ambulance 101, fire 102) are short codes that should not be formatted with country codes or area codes.
- Allocated Israeli mobile prefixes are 050, 051, 052, 053, 054, 055, 058, plus 056 and 059 for Palestinian carriers. 057 has no allocation (Hot Mobile moved from 057 to 053 in 2014).

## Troubleshooting

### Error: "Valid prefix but wrong digit count"
Cause: Mixing up mobile (10 digits) and landline (9 digits) lengths, or a spreadsheet dropped the leading 0
Solution: Mobile / non-geographic numbers always have 10 digits including the `0`. Landlines have 9. Count digits after normalising; a 9-digit `5XXXXXXXX` is a mobile number missing its 0. A 7-digit number is a local landline dialed without its area code: the script flags it `LOCAL_7_DIGITS`; ask for the area code rather than reject silently.

### Error: "071 or 078 number rejected"
Cause: Neither prefix has an allocation in the current MoC table (071 is also outside the plan's 07P range, P = 2-9). Older versions of this skill, and libphonenumber, accept some 071 / 078 blocks.
Solution: Treat the number as unverified rather than valid. If the user insists it is live, check the data.gov.il allocation dataset, which the MoC updates as new ranges are assigned.

### Error: "Number starts with 05 but prefix not recognized"
Cause: Not all 05X prefixes are allocated to Israeli consumer mobile (057 is unused; 056 / 059 are Palestinian).
Solution: Check `references/prefix-allocation.md`. Israeli consumer mobile: 050, 051, 052, 053, 054, 055, 058. Palestinian (flag separately): 056, 059.

### Error: "Cannot convert toll-free to international"
Cause: 1-800, 1-700, 1-599 and premium numbers are domestic service numbers
Solution: These numbers have no international equivalent. If the user needs international reach, suggest providing a standard landline or mobile number instead.

### Error: "WhatsApp message went to the wrong number or was not delivered"
Cause: The number was sent without the `+` and country code, so WhatsApp prepended the business account's own country code.
Solution: Send the E.164 form from `validate_phone.to_e164()` or `phonenumbers.format_number(num, PhoneNumberFormat.E164)`, e.g. `+972523456789`.
