# Israeli ID Number Formats Reference

## Teudat Zehut (Personal ID)

- **Length:** 9 digits (padded with leading zeros if shorter)
- **Prefix:** Any (no fixed prefix for personal IDs)
- **Check digit:** Position 9 (last digit)
- **Issued by:** Population and Immigration Authority (Ministry of Interior)
- **Range:** Numbers up to 999999999

## Company Number (Chevra Ba'am / Ltd)

- **Length:** 9 digits
- **Prefix:** 51 (private company). Registered entities span the whole 50-59 block, see "Registered-entity codes" below; keying only on "51" wrongly rejects public (52), government (50), and foreign (56) companies.
- **Format:** 51-XXXXXX-C (where C is check digit)
- **Issued by:** Companies Registrar (Rasham HaChavarot)
- **Registry:** ica.justice.gov.il

## Amuta Number (Non-profit / Registered Association)

- **Length:** 9 digits
- **Prefix:** 58
- **Format:** 58-XXXXXX-C
- **Issued by:** Registrar of Amutot
- **Registry:** ica.justice.gov.il

## Partnership Number (Shutafut)

- **Length:** 9 digits
- **Prefix:** 55
- **Format:** 55-XXXXXX-C
- **Issued by:** Registrar of Partnerships

## Cooperative Society (Aguda Shitufit)

- **Length:** 9 digits
- **Prefix:** 57
- **Format:** 57-XXXXXX-C
- **Supervised by:** Registrar of Cooperative Societies, not the Corporations Authority, so the companies search may not find a real 57-number

## Registered-entity codes (first two digits)

The first two digits of a registered-entity number usually relate to the entity
type (the source says "usually", and every listed code begins with 5); the check digit is
identical to a personal Teudat Zehut. Only the issuing registry is authoritative,
prefix typing is a heuristic.

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

## Teudat Zehut range note

Personal IDs carry NO embedded meaning: the digits do
not encode birth date, age, or residency status, and there is no documented
"native vs resident vs foreign-worker by number range" mapping (that split is
folklore). A personal ID therefore cannot be typed from its prefix.

## Check Digit Algorithm

All Israeli ID types use the same Luhn-variant algorithm:

1. Take the 9-digit number (pad with leading zeros if needed)
2. Multiply each digit by alternating weights: 1, 2, 1, 2, 1, 2, 1, 2, 1
3. If any product exceeds 9, replace it with the sum of its digits
4. Sum all the results
5. The number is valid if the sum is divisible by 10

### Worked Example: 123456782

```
Digit:      1  2  3  4  5  6  7  8  2
Weight:     1  2  1  2  1  2  1  2  1
Product:    1  4  3  8  5 12  7 16  2
Adjusted:   1  4  3  8  5  3  7  7  2
Sum: 1 + 4 + 3 + 8 + 5 + 3 + 7 + 7 + 2 = 40
40 % 10 = 0 -> VALID
```

## Golden test vectors

Every row was produced by running `scripts/validate_id.py validate` and checked
against an independently written JavaScript port (`javascript.md`). Use them as
fixtures in any reimplementation: a port that disagrees on any row is wrong.

| Input | Expected | Exit code | Why |
|-------|----------|-----------|-----|
| `123456782` | valid | 0 | Worked example above, sum 40 |
| `123456781` | invalid | 1 | Check digit off by one |
| `213456782` | invalid | 1 | First two digits transposed, sum 39 |
| `012345674` | valid | 0 | Leading zero, sum 30 |
| `12345674` | valid | 0 | Same ID with the zero dropped, pads to `012345674` |
| `18` | valid | 0 | Pads to `000000018` |
| `51-530820-3` | valid | 0 | Formatted company number |
| `51-530820-1` | invalid | 1 | Same company number, wrong check digit |
| `000000000` | invalid | 1 | Passes the checksum, rejected as a placeholder |
| `0` | invalid | 1 | Pads to `000000000` |
| `0000000018` | malformed | 2 | 10 digits, too long to be an ID |
| `62819482.1` | malformed | 2 | `.` is not a separator |
| (empty) | malformed | 2 | Nothing to validate |
| `١٢٣٤٥٦٧٨٢` | malformed | 2 | Arabic-Indic digits, not ASCII |
| `123456782` preceded by U+200F (RLM) | valid | 0 | An LRM/RLM at the edge is trimmed |
| `1234` U+200F `56782` | malformed | 2 | An LRM/RLM inside the number is not discarded |
| `123456782` followed by CR LF | valid | 0 | A line break at either end, e.g. from a CSV export, is trimmed |
| `1234` LF `5678 2` | malformed | 2 | A line break INSIDE the number is not a separator |
| `1234` TAB `5678 2` | malformed | 2 | Nor is a tab, which is a cell boundary in pasted TSV |
| U+202E then `287654321` | malformed | 2 | A bidi override is never discarded: it would display as `123456782` |
| U+202E then `12345674` | malformed | 2 | Would display as `47654321` |
| `1234` U+202E `56` U+202C `782` | malformed | 2 | Would display as `123465782` |
| `1234` U+00AD `56782` | valid | 0 | Soft hyphen is an invisible no-op mark |
| `1234` U+2060 `56782` | valid | 0 | Word joiner is an invisible no-op mark |
| `287654321` | valid | 0 | `123456782` reversed. The weights read the same both ways, so a reversed 9-digit ID ALWAYS passes |

## Common Errors

- **Transposed digits:** Swapping two adjacent digits usually breaks validation
- **Reversed digits (e.g. from a visual-order PDF, OCR or an older system):** NOT caught. The weights 1,2,1,2,1,2,1,2,1 are a palindrome, so a full 9-digit ID read backwards still passes; only a reversed 8-digit ID (leading zero dropped) usually fails
- **Missing leading zero:** Short IDs must be zero-padded to 9 digits
- **Confusing entity types:** Using a personal ID where a company number is needed
- **Format vs existence:** Algorithm validates format only, not that the ID was actually issued
