# Israeli Phone Prefix Allocation

Source: Ministry of Communications, updated 2025.

## Mobile Prefixes (10 digits total)

| Prefix | Carrier | Notes |
|--------|---------|-------|
| 050 | Pelephone | Original allocation |
| 051 | Azi Communications | Limited allocation |
| 052 | Cellcom | Major carrier |
| 053 | Hot Mobile | Formerly Mirs |
| 054 | Partner (Orange) | Major carrier |
| 055 | Rami Levy / Golan | MVNO allocations |
| 056 | Partner / Home Cellular | Secondary allocations |
| 058 | Golan Telecom | Major MVNO |
| 059 | **Unallocated** | Not in use |

## Landline Area Codes (9 digits total)

| Prefix | Region |
|--------|--------|
| 02 | Jerusalem and surroundings |
| 03 | Tel Aviv, Ramat Gan, central coast |
| 04 | Haifa, Galilee, Golan Heights |
| 08 | Southern Israel, Be'er Sheva, Negev |
| 09 | Sharon region, Netanya, Herzliya |

## VoIP Prefixes (10 digits total)

| Prefix | Carrier |
|--------|---------|
| 072 | Various VoIP providers |
| 073 | Various VoIP providers |
| 074 | Various VoIP providers |
| 076 | Various VoIP providers |
| 077 | Various VoIP providers |

## Special Numbers

| Format | Type | Dialable internationally? |
|--------|------|--------------------------|
| 1-800-XXXXXX | Toll-free | No |
| 1-700-XXXXXX | Premium rate | No |
| *XXXX | Star services | No |
| 100 | Police | No |
| 101 | Magen David Adom | No |
| 102 | Fire department | No |

## Regex Patterns

```python
PATTERNS = {
    "mobile": r"^0(5[0-8])\d{7}$",
    "landline": r"^0([2-4]|[89])\d{7}$",
    "voip": r"^0(7[2-7])\d{7}$",
    "toll_free": r"^1800\d{6}$",
    "premium": r"^1700\d{6}$",
    "star": r"^\*\d{4,6}$",
}
```
