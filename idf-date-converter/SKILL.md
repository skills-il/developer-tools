---
name: idf-date-converter
description: Convert between Hebrew (Jewish) calendar and Gregorian dates, look up Israeli holidays, format dual dates for Israeli documents, and calculate Israeli business days. Use when user asks about Hebrew dates, "luach ivri", Jewish calendar, Israeli holidays, "chagim", Shabbat times, or needs dual-date formatting for Israeli forms. Do NOT use for Islamic Hijri calendar or non-Israeli holiday calendars.
license: MIT
allowed-tools: Bash(python:*) Bash(pip:*)
compatibility: Python with hebcal or pyluach library recommended. Works without network.
version: 1.1.0
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

### Israeli Holidays and Fast Days, Gregorian projection for 2026
All projections are calendar-year 2026. Where a Hebrew month spans two Hebrew years (Tishrei rolls into the next Hebrew year), the row gives the Hebrew year that the holiday actually falls in.

| Holiday / Fast | Hebrew Date | Gregorian 2026 (approx) | Hebrew Year |
|----------------|-------------|-------------------------|-------------|
| Tu B'Shvat | 15 Shvat | Feb 2 | 5786 |
| Fast of Esther (Ta'anit Esther) | 13 Adar | Mar 4 | 5786 |
| Purim | 14 Adar | Mar 5 | 5786 |
| Pesach | 15-21 Nisan | Apr 1-7 | 5786 |
| Yom HaShoah | 27 Nisan | Apr 13 | 5786 |
| Yom HaZikaron | 4 Iyar | Apr 20 | 5786 |
| Yom HaAtzmaut | 5 Iyar | Apr 21 | 5786 |
| Lag BaOmer | 18 Iyar | May 4 | 5786 |
| Shavuot | 6 Sivan | May 21 | 5786 |
| Fast of 17 Tammuz (Shiv'a Asar B'Tammuz) | 17 Tammuz | Jul 2 | 5786 |
| Tisha B'Av (9 Av) | 9 Av | Jul 23 | 5786 |
| Rosh Hashana | 1-2 Tishrei | Sep 12-13 | 5787 |
| Fast of Gedaliah (Tzom Gedaliah) | 3 Tishrei | Sep 14 | 5787 |
| Yom Kippur | 10 Tishrei | Sep 21 | 5787 |
| Sukkot | 15-21 Tishrei | Sep 26 - Oct 2 | 5787 |
| Simchat Torah | 22 Tishrei | Oct 3 | 5787 |
| Chanukah (5787) | 25 Kislev - 2 Tevet | Dec 4-12, 2026 | 5787 |
| Fast of 10 Tevet (Asarah B'Tevet) | 10 Tevet | Dec 19 | 5787 |

Note on Chanukah: the Hebrew year 5786 Chanukah began evening 14 Dec 2025 and ended 22 Dec 2025, so it falls outside calendar year 2026. The next Chanukah (5787) begins evening 4 Dec 2026 and ends 12 Dec 2026. The table shows the 5787 occurrence because that is the one that lands in 2026.

### Yom HaZikaron / Yom HaAtzmaut displacement rules
The Knesset legislated displacement of Yom HaZikaron and Yom HaAtzmaut to avoid Shabbat desecration. Apply these rules before printing dates:
- If 5 Iyar falls on **Friday or Saturday**, Yom HaAtzmaut moves **earlier** to Thursday (4 Iyar or 3 Iyar). Yom HaZikaron moves with it.
- If 5 Iyar falls on **Monday**, Yom HaAtzmaut moves **later** to Tuesday (6 Iyar) so Yom HaZikaron does not start on Saturday night ceremonies that border Shabbat.
- If 5 Iyar falls on Sunday, Tuesday, or Wednesday, no displacement.
- Yom HaShoah (27 Nisan) is similarly displaced: if it falls on Friday it moves to Thursday (26 Nisan); if it falls on Sunday it moves to Monday (28 Nisan).

In 2026, 5 Iyar falls on Tuesday (Apr 21), so no displacement. Always re-check via `pyluach` or hebcal for other years.

## Examples

### Example 1: Simple Conversion
User says: "What's today's Hebrew date?"
Result: "24 February 2026 = 26 Adar I 5786"

### Example 2: Holiday Lookup
User says: "When is Pesach 2026?"
Result: "Pesach begins evening of March 31, 2026 (15 Nisan 5786). First seder: April 1. Last day: April 7."

### Example 3: Business Days
User says: "How many business days between March 1 and March 31, 2026?"
Result: Count excluding Shabbatot, noting if any holidays fall in the range (Purim on March 5).

## Bundled Resources

### Scripts
- `scripts/convert_date.py` , Converts between Hebrew and Gregorian calendars, formats dual dates for Israeli documents, lists Israeli holidays for any year, and counts Israeli business days between date ranges (excluding Shabbatot and holidays). Requires `pyluach` library. Run: `python scripts/convert_date.py --help`

### References
- `references/hebrew-calendar-reference.md` , Complete Hebrew calendar reference covering month names and variable lengths, the 19-year Metonic leap year cycle, gematria (Hebrew numeral) conversion table with special cases, Israeli holiday calendar with work-off days versus partial-closure days, and recommended Python libraries (pyluach, hebcal). Consult when handling leap year edge cases, formatting Hebrew numerals, or determining which holidays affect business day calculations.

## Gotchas

- Hebrew calendar dates have variable month lengths (29 or 30 days) and leap years add an entire month (Adar II). Agents may assume fixed month lengths or Gregorian leap year rules.
- Israeli official documents use Hebrew dates (e.g., "כ"ה באדר תשפ"ו") while business documents use Gregorian DD/MM/YYYY. Agents may not know which format to use for which context.
- Jewish holidays move relative to the Gregorian calendar each year. Agents with static training data may cite incorrect dates for Rosh Hashana, Pesach, etc. in the current year.
- The Hebrew year starts in Tishrei (September/October), not January. Agents may miscalculate Hebrew year boundaries when converting dates near the Gregorian new year.
- Yom HaZikaron, Yom HaAtzmaut, and Yom HaShoah are subject to legislated day-of-week displacement to avoid Shabbat conflicts. Static lookup tables that hard-code "5 Iyar" without checking the day of week will print wrong dates roughly half the time. Always run the displacement rules above.
- Chanukah usually straddles two Gregorian years (late Dec into early Jan). When labeling a Gregorian year column, pick the Hebrew year whose 25 Kislev actually lands inside that Gregorian year. Mixing 5786 and 5787 dates in the same row is a common mistake.

## Troubleshooting

### Error: "Incorrect Hebrew date"
Cause: Hebrew months vary in length; leap year months confusing
Solution: Verify with hebcal.com. Adar I/II only exist in leap years. Current year (5786) leap status affects dates.
