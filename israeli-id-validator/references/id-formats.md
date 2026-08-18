# Israeli ID Number Formats Reference

## Teudat Zehut (Personal ID)

- **Length:** 9 digits (padded with leading zeros if shorter)
- **Prefix:** Any (no fixed prefix for personal IDs)
- **Check digit:** Position 9 (last digit)
- **Issued by:** Ministry of Interior (Misrad HaPnim)
- **Range:** Numbers up to 999999999
- **Notes:** Issued at birth to Israeli citizens and permanent residents

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

## Registered-entity codes (first two digits)

Corporate and registered-entity numbers occupy the 5XX-million block. The number
begins with 5 and the second digit selects the entity type; the check digit is
identical to a personal Teudat Zehut. Only the issuing registry is authoritative,
prefix typing is a heuristic.

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

## Teudat Zehut range note

Personal IDs are assigned sequentially with NO embedded meaning: the digits do
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

## Common Errors

- **Transposed digits:** Swapping two adjacent digits usually breaks validation
- **Missing leading zero:** Short IDs must be zero-padded to 9 digits
- **Confusing entity types:** Using a personal ID where a company number is needed
- **Format vs existence:** Algorithm validates format only, not that the ID was actually issued
