---
name: israeli-phone-formatter
description: "Validate, format, and convert Israeli phone numbers between local and international (+972) formats. Use when user asks to validate Israeli phone number, format phone for SMS, convert to +972, check phone prefix, or implement Israeli phone input validation in code. Handles mobile (050-058), landline (02-09), VoIP (072-077), toll-free (1-800), and star-service numbers. Do NOT use for non-Israeli phone systems or general telecom questions."
license: MIT
allowed-tools: "Bash(python:*)"
compatibility: "No network required. Works with Claude Code, Claude.ai, Cursor."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [phone, validation, formatting, telecom, israel]
---

# Israeli Phone Formatter

## Instructions

### Step 1: Identify Phone Number Type

| Type | Prefixes | Total Digits | Example (local) |
|------|----------|-------------|-----------------|
| Mobile | 050-058 | 10 | 052-1234567 |
| Landline | 02-04, 08-09 | 9 | 02-6251111 |
| VoIP | 072-077 | 10 | 077-1234567 |
| Toll-free | 1-800 | 10 | 1-800-123456 |
| Premium | 1-700 | 10 | 1-700-123456 |
| Star service | *XXXX | 5-7 | *2421 |

For the full prefix allocation table per carrier, consult `references/prefix-allocation.md`.

### Step 2: Validate the Number

Run `python scripts/validate_phone.py --number {input}` to validate format and identify type.

If validating manually, apply these rules:
1. Strip all whitespace, hyphens, and parentheses
2. Convert international prefix: `+972` or `972` becomes leading `0`
3. Match against known prefix patterns
4. Verify digit count (mobile/VoIP = 10, landline = 9)

Common validation errors:
- **Wrong digit count**: Mobile numbers must be exactly 10 digits with the `0` prefix
- **Unallocated prefix**: `059` is not currently assigned to any carrier
- **Missing leading zero**: Local numbers always start with `0` (except toll-free and star)

### Step 3: Format or Convert

**Local to international:**
1. Remove leading `0`
2. Prepend `+972`
3. Example: `052-1234567` becomes `+972-52-123-4567`

**International to local:**
1. Replace `+972` (or `972`) with `0`
2. Example: `+972-2-625-1111` becomes `02-6251111`

**Important:** Toll-free (1-800), premium (1-700), and star (*) numbers cannot be dialed internationally.

### Step 4: Generate Code

When the user needs validation in code, provide a function using regex patterns from `references/prefix-allocation.md`. Include:
- Input sanitization (strip formatting characters)
- International prefix normalization
- Type detection by prefix
- Digit count verification per type

## Examples

### Example 1: Validate a Mobile Number
User says: "Is 052-1234567 a valid Israeli phone number?"
Actions:
1. Strip formatting: `0521234567`
2. Match prefix `052` = mobile (Cellcom)
3. Verify 10 digits total
Result: Valid Israeli mobile number (Cellcom). International: +972-52-123-4567

### Example 2: Convert to International
User says: "Convert 02-6251111 to international format"
Actions:
1. Strip formatting: `026251111`
2. Match prefix `02` = Jerusalem landline
3. Drop leading `0`, prepend `+972`
Result: +972-2-625-1111 (Jerusalem landline)

### Example 3: Batch Validation
User says: "Validate this list of phone numbers for my CRM import"
Actions:
1. Run `python scripts/validate_phone.py --batch --input contacts.csv`
2. Report valid/invalid counts with specific errors per row
Result: Summary table with validation status per number

## Bundled Resources

### Scripts
- `scripts/validate_phone.py` -- Validates, formats, and converts Israeli phone numbers. Supports single number validation, batch CSV processing, and format conversion between local and international. Run: `python scripts/validate_phone.py --help`

### References
- `references/prefix-allocation.md` -- Complete Israeli phone prefix allocation table per Ministry of Communications, including carrier assignments for mobile prefixes (050-058), area codes for landlines, VoIP ranges, and special service numbers. Consult when implementing validation or identifying carriers.

## Troubleshooting

### Error: "Valid prefix but wrong digit count"
Cause: Mixing up mobile (10 digits) and landline (9 digits) lengths
Solution: Mobile/VoIP numbers always have 10 digits including the `0`. Landlines have 9. Count digits after stripping all formatting.

### Error: "Number starts with 05 but prefix not recognized"
Cause: Not all 05X prefixes are allocated. 059 is currently unused.
Solution: Check `references/prefix-allocation.md` for current allocations. Allocated mobile: 050, 051, 052, 053, 054, 055, 056, 058.

### Error: "Cannot convert toll-free to international"
Cause: 1-800 and 1-700 numbers are domestic-only
Solution: These numbers have no international equivalent. If the user needs international reach, suggest providing a standard landline or mobile number instead.
