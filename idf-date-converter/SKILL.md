---
name: idf-date-converter
description: >-
  Convert between Hebrew (Jewish) calendar and Gregorian dates, look up
  Israeli holidays, format dual dates for Israeli documents, and calculate
  Israeli business days. Use when user asks about Hebrew dates, "luach ivri",
  Jewish calendar, Israeli holidays, "chagim", Shabbat times, or needs
  dual-date formatting for Israeli forms. Do NOT use for Islamic Hijri
  calendar or non-Israeli holiday calendars.
license: MIT
allowed-tools: "Bash(python:*) Bash(pip:*)"
compatibility: "Python with hebcal or pyluach library recommended. Works without network."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [calendar, hebrew-date, holidays, shabbat, conversion, israel]
---

# IDF Date Converter

## Instructions

### Step 1: Identify the Request
| Request | Action |
|---------|--------|
| Convert specific date | Gregorian to Hebrew or Hebrew to Gregorian conversion |
| When is holiday X? | Look up holiday in Hebrew calendar |
| Format for document | Dual date string in Hebrew + Gregorian |
| Business days | Count excluding Shabbat + holidays |
| Shabbat times | Candle lighting / havdalah for city |

### Step 2: Date Conversion
Use Python conversion:

```python
# Using pyluach library
from pyluach import dates, hebrewcal

# Gregorian to Hebrew
greg_date = dates.GregorianDate(2026, 2, 24)
heb_date = greg_date.to_heb()
print(f"{heb_date.day} {heb_date.month_name()} {heb_date.year}")

# Hebrew to Gregorian
heb_date = dates.HebrewDate(5786, 6, 26)  # 26 Adar 5786
greg_date = heb_date.to_greg()
print(f"{greg_date.day}/{greg_date.month}/{greg_date.year}")
```

### Step 3: Hebrew Numeral Formatting
Hebrew dates use gematria (letter-number system):
- Units: alef=1, bet=2, gimel=3, ... tet=9
- Tens: yod=10, kaf=20, lamed=30, ... tzadi=90
- Hundreds: kuf=100, resh=200, shin=300, tav=400
- Special: 15 = tet-vav (not yod-heh), 16 = tet-zayin (not yod-vav)
- Year: Omit thousands (5786 written as tav-shin-peh-vav = 786)

### Step 4: Dual Date Formatting
For Israeli documents:
```
24 February 2026 / 26 Adar I 5786
```

### Step 5: Israeli Business Days
Israeli business week: Sunday through Thursday (some work half-day Friday)
Non-working days:
- Every Shabbat (Friday sunset to Saturday sunset)
- All major holidays (see holiday table)
- Election days (when applicable)

```python
def is_israeli_business_day(greg_date):
    """Check if a date is an Israeli business day."""
    # Saturday = 5 in Python's weekday() (0=Monday)
    if greg_date.weekday() == 5:  # Saturday
        return False
    # Check if it's a holiday
    heb = dates.GregorianDate(greg_date.year, greg_date.month, greg_date.day).to_heb()
    # Check against holiday list
    return not is_israeli_holiday(heb)
```

### Israeli Holidays (Fixed Hebrew Dates)
| Holiday | Hebrew Date | 2026 Gregorian (approx) |
|---------|------------|------------------------|
| Rosh Hashana | 1-2 Tishrei | Sep 12-13 |
| Yom Kippur | 10 Tishrei | Sep 21 |
| Sukkot | 15-21 Tishrei | Sep 26 - Oct 2 |
| Simchat Torah | 22 Tishrei | Oct 3 |
| Chanukah | 25 Kislev - 2 Tevet | Dec 5-12 |
| Purim | 14 Adar | Mar 17 |
| Pesach | 15-21 Nisan | Apr 2-8 |
| Yom HaShoah | 27 Nisan | Apr 14 |
| Yom HaZikaron | 4 Iyar | Apr 21 |
| Yom HaAtzmaut | 5 Iyar | Apr 22 |
| Shavuot | 6 Sivan | May 22 |

## Examples

### Example 1: Simple Conversion
User says: "What's today's Hebrew date?"
Result: "24 February 2026 = 26 Adar I 5786"

### Example 2: Holiday Lookup
User says: "When is Pesach 2026?"
Result: "Pesach begins evening of April 1, 2026 (15 Nisan 5786). First seder: April 1. Last day: April 8."

### Example 3: Business Days
User says: "How many business days between March 1 and March 31, 2026?"
Result: Count excluding Shabbatot, noting if any holidays fall in the range (Purim on March 17).

## Bundled Resources

### Scripts
- `scripts/convert_date.py` — Converts between Hebrew and Gregorian calendars, formats dual dates for Israeli documents, lists Israeli holidays for any year, and counts Israeli business days between date ranges (excluding Shabbatot and holidays). Requires `pyluach` library. Run: `python scripts/convert_date.py --help`

### References
- `references/hebrew-calendar-reference.md` — Complete Hebrew calendar reference covering month names and variable lengths, the 19-year Metonic leap year cycle, gematria (Hebrew numeral) conversion table with special cases, Israeli holiday calendar with work-off days versus partial-closure days, and recommended Python libraries (pyluach, hebcal). Consult when handling leap year edge cases, formatting Hebrew numerals, or determining which holidays affect business day calculations.

## Troubleshooting

### Error: "Incorrect Hebrew date"
Cause: Hebrew months vary in length; leap year months confusing
Solution: Verify with hebcal.com. Adar I/II only exist in leap years. Current year (5786) leap status affects dates.
