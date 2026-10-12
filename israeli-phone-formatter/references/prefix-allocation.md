# Israeli Phone Prefix Allocation

Sources: Ministry of Communications numbering plan (edition 4, February 2023) and the MoC allocation datasets on data.gov.il (`israel-numbering-plan`, updated September 2026; `israel-dialing-plan`, updated August 2025). Re-check the datasets before relying on a sub-block: the MoC assigns new ranges between plan editions. The data.gov.il dataset pages can refuse scripted fetches; the same data is served by the CKAN API, e.g. `https://data.gov.il/api/3/action/datastore_search?resource_id=caa80822-5880-4bbf-808a-06d7f53c4ae5&limit=5000` (allocations) and `resource_id=f5e57cec-4af9-488e-94b5-53f948a3cec3` (service numbers and short codes).

## Number Structure (numbering plan section 2.1.2)

| Class | Pattern | Digits incl. leading 0 | Rule |
|-------|---------|------------------------|------|
| Geographic | `0A-NXX-XXXX` | 9 | A in 2, 3, 4, 8, 9; N = 2-9 |
| Mobile | `05R-NXX-XXXX` | 10 | N = 2-9; N = 0-1 only for M2M service |
| National (non-geographic) | `07P-NXX-XXXX` | 10 | P = 2-9; N = 2-9 |
| Service area | `1SYZ-WWWWWW` | 10 | 1-800, 1-700, 1-599, 1-900 and others |
| Star business number | `*XXXX` | 5 | Star plus four digits; 1222 replaces the star on phones without one |

Within a geographic dialing area (and, for 07X numbers, within the same network) a number can be dialed with its 7 subscriber digits only (`NXX-XXXX`). A form that receives 7 digits should ask for the area code rather than reject the number.

## Mobile Number Portability (MNP) Disclaimer

Number portability in Israel began on 2 December 2007. The prefix in a mobile number reflects the **original** operator the number was issued under, not the current carrier the subscriber uses. Treat the carrier column below as issuer attribution only. For billing, routing, or compliance use cases that depend on the live carrier, query an HLR lookup or the operator's portability service.

## Mobile Prefixes (10 digits total)

| Prefix | Holder per MoC table | Notes |
|--------|----------------------|-------|
| 050 | Pelephone | 050-1 is an M2M block |
| 051 | WeCom Mobile | 051-2, 051-5, 051-6 |
| 052 | Cellcom | 052-1 is an M2M block |
| 053 | Hot Mobile | Hot Mobile used 057 until it moved to 053 in November 2014 |
| 054 | Partner Communications | 054-0 and 054-1 are M2M blocks |
| 055 | Multi-operator | Sub-blocks held by 019 Telzar, Rami Levy, Cellcom, Cellact, Annatel, Widely, Pelephone, Paycall, Maskyoo, Merkaziya, Xphone 018, Voicenter and others; 055-16 to 055-19 are M2M |
| 056 | Palestinian operators | Ooredoo Palestine (formerly Wataniya); **not an Israeli consumer mobile**, flag separately |
| 058 | Cellcom | Originally Golan Telecom's range; 058-0 and 058-1 are M2M blocks |
| 059 | Jawwal | Palestinian operator; **not an Israeli consumer mobile**, flag separately |

057 has no allocation.

The MoC table also lists a separate IoT / M2M numbering class under NDC 13 (for example `13-02XXXXXX`, Partner), used for device SIMs rather than people. This skill does not validate it.

## Landline Area Codes (9 digits total)

| Prefix | Dialing area (numbering plan wording) |
|--------|---------------------------------------|
| 02 | Jerusalem |
| 03 | Tel Aviv |
| 04 | Haifa and the North |
| 08 | Shfela and the South |
| 09 | Sharon |

The blocks 02-2, 04-2, 08-2 and 09-2 (`0A-2XXXXXX`) are allocated to Palestinian operators. Geographic ranges are held by Bezeq and by many other licensed operators (Hot, Partner, Cellcom, VoIP providers), so the area code says nothing about the operator.

## Non-Geographic (National) Prefixes (10 digits total)

| Prefix | Holders per MoC table |
|--------|-----------------------|
| 072 | Partner (072-2, 072-3); small blocks for other operators |
| 073 | Cellcom (073-2, 073-3, 073-7); many smaller operators in 073-8 |
| 074 | Partner (074-7) |
| 076 | Bezeq International (076-5), Bezeq (076-8) |
| 077 | Hot Telecom |
| 079 | Widely (079-2), Binat (079-3), Hallo 015 (079-4 to 079-6), Cellact (079-7), Annatel (079-8), 019 Telzar (079-9) |

070, 071, 075 and 078 have no allocation in the current table. libphonenumber still lists some 071 and 078 blocks, taken from older ITU and Wikipedia data.

## Service Numbers (domestic only)

| Format | Meaning per MoC dialing-plan table |
|--------|-----------------------------------|
| 1-800-XXXXXX, 1-801-XXXXXX | Toll-free ("מספרי חינם") |
| 1-809-XXXXXX | Toll-free for international operators |
| 1-700-XXXXXX | Shared cost: local call, split charging ("שיחה מקומית - חיוב מפוצל") |
| 1-599-XXXXXX | Business call router ("נתב שיחות עסקי") |
| 1-900, 1-901, 1-902-XXXXXX | Premium service at premium rate |
| 1-919-XXXXXX | Premium, adult services |
| 1-956, 1-957-XXXXXX | Voice entertainment / voice information |
| 1-200, 1-212-XXXXXX | Televoting / public polls |
| *XXXX | Star business number |

## Short Codes

| Code | Service |
|------|---------|
| 100 | Police |
| 101 | Magen David Adom |
| 102 | Fire and Rescue |
| 103 | Israel Electric Corporation |
| 104 | Home Front Command |
| 105 | National child online protection center |
| 106 | Municipal call center (107-109 are slated for cancellation) |
| 110 | Israel Police national information center |
| 112 | Listed by the MoC as a future joint emergency center (not accepted by the bundled script) |
| 115 | Israel Police national disaster center |
| 118 | National welfare emergency center |
| 119 | National Cyber Directorate |

## E.164 Format Guidance (WhatsApp, SMS APIs, libphonenumber)

Store one canonical E.164 value: a leading `+`, the country code 972, the number without its leading 0, and no separators. `libphonenumber` parsing tolerates separators, and the WhatsApp Cloud API accepts `+`, hyphens, parentheses and spaces in send requests, but WhatsApp needs the `+` and country code: if the `+` is omitted, Meta prepends the business phone number's own country code, which can leave the message undelivered or misdelivered.

For Israeli numbers, the canonical E.164 form is:

```
+972523456789       (mobile, from local 052-3456789)
+97226251111        (Jerusalem landline, from local 02-625-1111)
+972772345678       (077 non-geographic, from local 077-2345678)
```

A display value such as `+972-52-345-6789` is not the canonical E.164 string. Keep one canonical column for storage and transport (no separators) and render the hyphenated form only for humans.

For interoperability tests, use:

```python
import phonenumbers  # google's libphonenumber port
num = phonenumbers.parse("0523456789", "IL")
phonenumbers.is_valid_number(num)  # True
phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)  # "+972523456789"
```

## Regex Patterns

```python
PATTERNS = {
    # Mobile: 10 digits, 050-056, 058, 059 (057 unallocated; 056 / 059 Palestinian, flag separately)
    "mobile": r"^05[0-689]\d{7}$",
    # Landline: 9 digits, area code 02-04, 08, 09, first subscriber digit 2-9
    "landline": r"^0[2-489][2-9]\d{6}$",
    # National (non-geographic): 10 digits, 072-074, 076, 077, 079, first subscriber digit 2-9
    "national": r"^07[2-46-79][2-9]\d{6}$",
    "toll_free": r"^180[019]\d{6}$",
    "shared_cost": r"^1700\d{6}$",
    "business": r"^1599\d{6}$",
    "premium": r"^19(0[0-2]|19)\d{6}$",
    "other_service": r"^1(95[67]|200|212)\d{6}$",
    "star": r"^(\*|1222)\d{4}$",
}
```

Normalise before matching: Unicode digits to ASCII, drop bidi marks, dash variants, slashes and surrounding text, convert `+972`, `00972`, `+972 (0)` and `+9720` to a leading 0, and restore a leading 0 probably lost in a spreadsheet (bare-digit cells only: 9 digits starting 5 or 7, 8 digits starting 2, 3, 4, 8 or 9), marking it for confirmation. Reject scientific-notation cells such as `5.23457E+08`: the digits are already gone. After a mobile match, treat a fourth digit of 0 or 1 as an M2M / IoT number, and 056 / 059 as Palestinian carriers. After a landline match, treat `0A-2` (A = 2, 4, 8, 9) as a Palestinian operator range.
