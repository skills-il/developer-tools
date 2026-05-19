# Israeli Phone Prefix Allocation

Source: Ministry of Communications, updated 2025.

## Mobile Number Portability (MNP) Disclaimer

Since 2007 Israel has full mobile number portability. The prefix in a mobile number reflects the **original** carrier the number was issued under, not the current carrier the subscriber uses. Treat the carrier column below as historical/issuer attribution only. For billing, routing, or compliance use cases that depend on the live carrier, query an HLR lookup or the operator's CNAM/portability service. Do not rely on the prefix to infer the active SIM provider.

## Mobile Prefixes (10 digits total)

| Prefix | Issuing Carrier | Notes |
|--------|-----------------|-------|
| 050 | Pelephone | Original allocation |
| 051 | We4G (Xfone) | Limited allocation |
| 052 | Cellcom | Major carrier |
| 053 | Hot Mobile (Altice) | |
| 054 | Partner Communications | Major carrier |
| 055 | Multi-MVNO | Cellcom, 019 Mobile, Widely, Rami Levy, Cellact, Pelephone all issue 055 ranges |
| 056 | Wataniya Mobile | Palestinian territories carrier; **not an Israeli consumer mobile** -- flag separately |
| 058 | Golan (acquired by Cellcom) | Operates as a Cellcom brand |
| 059 | Jawwal | Palestinian territories carrier; **not an Israeli consumer mobile** -- flag separately |

## Landline Area Codes (9 digits total)

| Prefix | Region |
|--------|--------|
| 02 | Jerusalem and surroundings |
| 03 | Tel Aviv, Ramat Gan, central coast |
| 04 | Haifa, Galilee, Golan Heights |
| 08 | Southern Israel, Be'er Sheva, Negev |
| 09 | Sharon region, Netanya, Herzliya |

## Non-Geographic Prefixes (10 digits total)

| Prefix | Carrier / Notes |
|--------|-----------------|
| 072 | Various VoIP and non-geographic providers |
| 073 | Various VoIP and non-geographic providers |
| 074 | Various VoIP and non-geographic providers |
| 076 | Various VoIP and non-geographic providers |
| 077 | Hot (Hot Telecom non-geographic range) |
| 078 | Various VoIP and non-geographic providers |
| 079 | Widely, 019 Mobile, Annatel and other non-geographic providers |

## Special Numbers

| Format | Type | Dialable internationally? |
|--------|------|--------------------------|
| 1-800-XXXXXX | Toll-free | No |
| 1-700-XXXXXX | Premium rate | No |
| *XXXX | Star services | No |
| 100 | Police | No |
| 101 | Magen David Adom | No |
| 102 | Fire department | No |

## E.164 Format Guidance (WhatsApp, SMS APIs, libphonenumber)

WhatsApp Business API, Twilio, Vonage, AWS SNS, and any consumer of `google-libphonenumber` / `libphonenumber-js` require strict E.164: a leading `+`, country code, subscriber number, and **no** spaces, hyphens, parentheses, or dots. Total length 8-15 digits.

For Israeli numbers, the canonical E.164 form is:

```
+972521234567       (mobile, from local 052-1234567)
+97226251111        (Jerusalem landline, from local 02-625-1111)
+972771234567       (077 non-geographic, from local 077-1234567)
```

A formatted display value such as `+972-52-123-4567` is **not** valid E.164 and will be rejected by strict parsers. Keep one canonical column for storage/transport (no separators) and only render the hyphenated form for human display.

For interoperability tests, use:

```python
import phonenumbers  # google's libphonenumber port
num = phonenumbers.parse("0521234567", "IL")
phonenumbers.is_valid_number(num)  # True
phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)  # "+972521234567"
```

## Regex Patterns

```python
PATTERNS = {
    # Mobile: 10 digits, prefix 050-056, 058, 059 (057 unallocated; 056 = Wataniya, 059 = Jawwal -- Palestinian, flag separately)
    "mobile": r"^0(5[012345689])\d{7}$",
    # Landline: 9 digits, area code 02-04, 08, 09
    "landline": r"^0([2-4]|[89])\d{7}$",
    # Non-geographic / VoIP: 10 digits, prefix 072-079
    "voip": r"^07[2-9]\d{7}$",
    "toll_free": r"^1800\d{6}$",
    "premium": r"^1700\d{6}$",
    "star": r"^\*\d{4,6}$",
}
```

Note: 059 (Jawwal) and 056 (Wataniya) match the mobile shape but should be flagged as Palestinian carriers, not Israeli consumer mobile numbers, when business logic depends on Israeli SIM ownership.
