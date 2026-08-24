---
name: idf-date-converter
description: Convert between Hebrew (Jewish) calendar and Gregorian dates, look up Israeli holidays, format dual dates for Israeli documents, and calculate Israeli business days. Use when user asks about Hebrew dates, "luach ivri", Jewish calendar, Israeli holidays, "chagim", Shabbat times, or needs dual-date formatting for Israeli forms. Do NOT use for Islamic Hijri calendar or non-Israeli holiday calendars.
license: MIT
allowed-tools: Bash(python:*) Bash(pip:*)
compatibility: Python with hebcal or pyluach library recommended. Works without network.
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
| Shabbat times | Candle lighting / havdalah for a city (see Step 7) |

### Step 2: Date Conversion
Use Python conversion:

```python
# Using pyluach library
from pyluach import dates, hebrewcal

# Gregorian to Hebrew
greg_date = dates.GregorianDate(2026, 2, 24)
heb_date = greg_date.to_heb()
print(f"{heb_date.day} {heb_date.month_name()} {heb_date.year}")

# Hebrew to Gregorian (always verify the resulting date by round-tripping)
heb_date = dates.HebrewDate(5786, 11, 15)  # 15 Shvat 5786 (Tu B'Shvat). pyluach numbers months from Nisan=1, so Shvat=11
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
24 February 2026 / 7 Adar 5786
```
(5786 is a regular Hebrew year, not a leap year, so there is only one Adar, with no Adar I / Adar II. Always run pyluach to confirm a dual-date string before printing it.)

### Step 5: Israeli Business Days
Israeli business week: Sunday through Thursday (many sectors work a half-day Friday).

Not every day people call a "holiday" is a day off, and the distinction changes the count. Split them into two tiers:

| Tier | Days | Effect on a business-day count |
|------|------|-------------------------------|
| Statutory rest days | Rosh Hashana (2 days), Yom Kippur, Sukkot day 1, Shmini Atzeret / Simchat Torah, Pesach day 1, Pesach day 7, Shavuot, Yom HaAtzmaut | Deduct. These are the days on which Israeli workplaces, banks and public transport close by law |
| Observances | Purim, Shushan Purim, Yom HaZikaron, Yom HaShoah, Yom Yerushalayim, Yom HaAliyah, Rabin Memorial Day, Sigd, Chol HaMoed, Chanukah, Tu B'Shvat, Lag BaOmer, all public fasts | Report but do NOT deduct. Workplaces generally stay open, though hours are often reduced |
| Erev chag | Erev Rosh Hashana, Erev Yom Kippur, Erev Sukkot, Hoshana Rabba, Erev Pesach, Erev Pesach VII, Erev Shavuot | Report as HALF days. Banks, government offices and courts close around midday, and Erev Pesach is a near-total closure after midday. Deduct half a day if your count is hours-based |

Shabbat (Friday sunset to Saturday sunset) is always excluded. Election days are excluded when declared.

The script reports Yom Yerushalayim and Yom HaAliyah but deliberately omits Rabin Memorial Day and Sigd, whose date rules it does not model; look those two up directly.

Note that in Jerusalem and other historically walled cities the operative Purim is **Shushan Purim (15 Adar)**, not 14 Adar: that is the day schools and many workplaces close.

`scripts/convert_date.py business-days <start> <end>` implements exactly this split, and lists observances separately from the deducted rest days so you can apply your own sector's convention.

### Step 6: The Hebrew Day Starts at Sunset
A Hebrew date does not run midnight to midnight. It begins at sunset (shkia) on the preceding Gregorian evening and ends at nightfall (tzeit hakochavim) the next. Every library in this space, pyluach included, converts the DAYTIME date: `GregorianDate(2026, 2, 24).to_heb()` returns 7 Adar 5786, which is correct from sunrise on 24 February until sunset that evening, and wrong for the hours after it.

This matters whenever the answer is time-sensitive rather than merely calendrical:

- **After sunset, add one day.** A user asking "what is today's Hebrew date?" at 20:00 on 24 February 2026 wants 8 Adar, not 7 Adar. Ask for or infer the local time before answering, and say which convention you used.
- **Yahrzeit, bar mitzvah and legal-document dates** are reckoned from the Hebrew date at the actual hour of the event. A birth at 23:00 falls on the NEXT Hebrew day.
- **Holidays begin the evening before.** "Yom Kippur is 21 September 2026" means the fast starts at sunset on 20 September. The skill's tables give the Gregorian day the holiday's daytime falls on, which is the standard convention, not the evening it starts.
- **Do not compute sunset yourself.** It is location-dependent and needs a solar library or an API. Use hebcal's zmanim endpoint with a geonameid, or state that the answer assumes daytime.

The bundled script deliberately does not guess: it reports the daytime Hebrew date. Adjust for the evening yourself when the question is time-of-day sensitive.

### Step 7: Shabbat and Chag Times
Candle lighting and havdalah are solar, not calendrical, so they cannot be derived from a date conversion. Do not compute or estimate them. Query Hebcal's Shabbat endpoint with the city's geonameid:

```
https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on
```

Common Israeli geonameids: Jerusalem 281184, Tel Aviv 293397, Haifa 294801, Beersheba 295530.

Two conventions that produce most of the errors in this area:
- **The candle-lighting offset is not uniform.** Hebcal defaults to 18 minutes before sundown, but 40 minutes for Jerusalem and 30 for Haifa and Zikhron Ya'akov, matching local custom. Override with `b=<minutes>` only if the user names a different custom. Never assume 18 minutes nationwide.
- **Havdalah has several conventions** (`M=on` uses nightfall by solar depression; the alternative is a fixed number of minutes after sunset via `m=<minutes>`). State which you used.

The same endpoint returns erev chag candle lighting for Rosh Hashana, Yom Kippur, Sukkot, Shmini Atzeret, Simchat Torah, Pesach and Shavuot.

### Israeli Holidays and Fast Days, Gregorian projection for 2026
All projections are calendar-year 2026. Where a Hebrew month spans two Hebrew years (Tishrei rolls into the next Hebrew year), the row gives the Hebrew year that the holiday actually falls in.

| Holiday / Fast | Hebrew Date | Gregorian 2026 (approx) | Hebrew Year |
|----------------|-------------|-------------------------|-------------|
| Tu B'Shvat | 15 Shvat | Feb 2 | 5786 |
| Fast of Esther (Ta'anit Esther) | 13 Adar | Mar 2 | 5786 |
| Purim | 14 Adar | Mar 3 | 5786 |
| Shushan Purim | 15 Adar | Mar 4 | 5786 |
| Pesach | 15-21 Nisan | Apr 2-8 | 5786 |
| Yom HaShoah | 27 Nisan | Apr 14 | 5786 |
| Yom HaZikaron | 4 Iyar | Apr 21 | 5786 |
| Yom HaAtzmaut | 5 Iyar | Apr 22 | 5786 |
| Lag BaOmer | 18 Iyar | May 5 | 5786 |
| Shavuot | 6 Sivan | May 22 | 5786 |
| Fast of 17 Tammuz (Shiv'a Asar B'Tammuz) | 17 Tammuz | Jul 2 | 5786 |
| Tisha B'Av (9 Av) | 9 Av | Jul 23 | 5786 |
| Rosh Hashana | 1-2 Tishrei | Sep 12-13 | 5787 |
| Fast of Gedaliah (Tzom Gedaliah) | 3 Tishrei | Sep 14 | 5787 |
| Yom Kippur | 10 Tishrei | Sep 21 | 5787 |
| Sukkot | 15-21 Tishrei | Sep 26 - Oct 2 | 5787 |
| Simchat Torah | 22 Tishrei | Oct 3 | 5787 |
| Chanukah (5787) | 25 Kislev - 2 Tevet | Dec 5-12, 2026 | 5787 |
| Fast of 10 Tevet (Asarah B'Tevet) | 10 Tevet | Dec 20 | 5787 |

Note on Chanukah: the 5787 occurrence begins on the evening of 4 Dec 2026 (kindling the first candle) and the first full Gregorian day is 5 Dec 2026 (25 Kislev). It ends 12 Dec 2026 (2 Tevet). The table shows the 5787 occurrence because that is the one that lands in calendar year 2026.

Always verify these dates with pyluach before using them in production. The corrected dates above were regenerated in v2.0.0 after the initial 2026 projection table shipped with off-by-one errors on roughly half the entries.

### Yom HaZikaron / Yom HaAtzmaut displacement rules
The Knesset legislated displacement of Yom HaZikaron and Yom HaAtzmaut to avoid Shabbat desecration. Apply these rules before printing dates:
- If 5 Iyar falls on **Friday or Saturday**, Yom HaAtzmaut moves **earlier** to Thursday (4 Iyar or 3 Iyar). Yom HaZikaron moves with it.
- If 5 Iyar falls on **Monday**, Yom HaAtzmaut moves **later** to Tuesday (6 Iyar) so Yom HaZikaron does not start on Saturday night ceremonies that border Shabbat.
- 5 Iyar can only fall on a Monday, Wednesday, Friday or Saturday. If it falls on a Wednesday, no displacement applies.
- Yom HaShoah (27 Nisan) is similarly displaced: if it falls on Friday it moves to Thursday (26 Nisan); if it falls on Sunday it moves to Monday (28 Nisan).

**These rules have effective dates, and applying them to a historical year is a silent error.** Yom HaAtzmaut became a state holiday in law in 1949; the Friday/Saturday displacement was decided in 1951; the Monday postponement has only been in force **since 2004**. Yom HaZikaron dates from 1951 (enacted into law 1963) and Yom HaShoah's 27 Nisan from the 1951 Knesset resolution. Converting a date from the 1950s to the 1990s with today's rules moves Yom HaAtzmaut a day in every pre-2004 Monday year, and emits all three days for years before they existed. `scripts/convert_date.py` gates each rule on its own effective year.

In 2026, 5 Iyar falls on Wednesday (Apr 22), so no displacement. Displacement IS due in 6 of the 10 years from 2026 to 2035 (2028, 2029, 2031, 2032, 2034, 2035), so a lookup table built without these rules is wrong more often than it is right. `scripts/convert_date.py` applies them.

### Fast day postponement (nidcheh)
A public fast is never observed on Shabbat, and the four movable fasts do not all move in the same direction:
- **Tzom Gedaliah (3 Tishrei), 17 Tammuz, and Tisha B'Av (9 Av)** are POSTPONED to the following Sunday when they fall on Shabbat.
- **Ta'anit Esther (13 Adar)** is brought FORWARD to the preceding Thursday (11 Adar), because it has to precede Purim.
- **Asara B'Tevet (10 Tevet)** can fall on a Friday but never on Shabbat, so it never moves.

In a leap year, Ta'anit Esther, Purim and Shushan Purim fall in **Adar II** (pyluach month 13), not Adar I (month 12). Passing month 12 for Purim in a leap year returns a date a full month early.

## Examples

### Example 1: Simple Conversion
User says: "What's today's Hebrew date?"
Result: "24 February 2026 = 7 Adar 5786" (5786 is a regular year, so there is one Adar and no Adar I / Adar II)

### Example 2: Holiday Lookup
User says: "When is Pesach 2026?"
Result: "Pesach begins evening of April 1, 2026 (15 Nisan 5786). First seder: April 2. Last day in Israel: April 8."

### Example 3: Business Days
User says: "How many business days between March 1 and March 31, 2026?"
Result: Count excluding Shabbatot, noting if any holidays fall in the range (Purim on March 3, Shushan Purim on March 4).

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

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Hebcal Jewish calendar | https://www.hebcal.com | Authoritative holiday dates; set the Israel schedule for Israeli observance |
| Hebcal developer API | https://www.hebcal.com/home/developer-apis | REST endpoints for holiday tables, date conversion, and zmanim (sunset) |
| pyluach | https://github.com/simlist/pyluach | Reference Python implementation; month numbering and leap-year handling |
| Yom HaAtzmaut displacement | https://en.wikipedia.org/wiki/Yom_Ha%27atzmaut | The 1951 and 2004 displacement decisions |
| Hebrew numerals | https://en.wikipedia.org/wiki/Hebrew_numerals | Gematria table and the 15 / 16 exceptions |

## Troubleshooting

### Error: "Incorrect Hebrew date"
Cause: Hebrew months vary in length; leap year months confusing
Solution: Verify with hebcal.com. Adar I/II only exist in leap years. Current year (5786) leap status affects dates.

### Error: converted date is off by exactly one month around Purim
Cause: In a leap year pyluach numbers Adar I as month 12 and Adar II as month 13, and month 12 is where a caller instinctively looks for "Adar". Purim is in Adar II.
Solution: Branch on leap-year status before picking the month number: `13 if year % 19 in {0,3,6,8,11,14,17} else 12`. `convert_date.py to-gregorian` labels month 12 of a leap year as "Adar I" so the mistake is visible in the output rather than silent.

### Error: converted date is off by exactly one day
Cause: Almost always the Hebrew day boundary (see Step 6). The library returned the daytime date and the question was about an evening, or vice versa. Verified NOT to be a leap-year or month-length issue when the offset is exactly one day and reproducible across dates.
Solution: Establish the local time of the event. After sunset, add one day to the library's answer.
