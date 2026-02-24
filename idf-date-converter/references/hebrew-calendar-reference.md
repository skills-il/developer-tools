# Hebrew Calendar Reference

## Month Names and Lengths

| Month # | Name | Length (Regular) | Length (Leap Year) |
|---------|------|------------------|--------------------|
| 7 | Tishrei | 30 | 30 |
| 8 | Cheshvan (Marcheshvan) | 29 or 30 | 29 or 30 |
| 9 | Kislev | 30 or 29 | 30 or 29 |
| 10 | Tevet | 29 | 29 |
| 11 | Shevat | 30 | 30 |
| 12 | Adar | 29 | 30 (Adar I) |
| 13 | - | - | 29 (Adar II) |
| 1 | Nisan | 30 | 30 |
| 2 | Iyar | 29 | 29 |
| 3 | Sivan | 30 | 30 |
| 4 | Tammuz | 29 | 29 |
| 5 | Av | 30 | 30 |
| 6 | Elul | 29 | 29 |

Notes:
- Cheshvan can be 29 or 30 days (deficient or full year)
- Kislev can be 30 or 29 days (full or deficient year)
- In leap years, Adar becomes Adar I (30 days) and Adar II (29 days) is added

## Leap Year Cycle

The Hebrew calendar follows a 19-year (Metonic) cycle. Years 3, 6, 8, 11, 14, 17, and 19 of the cycle are leap years.

To determine if a Hebrew year is a leap year:
```
remainder = hebrew_year % 19
leap_years = {0, 3, 6, 8, 11, 14, 17}
is_leap = remainder in leap_years
```

## Gematria (Hebrew Numerals)

| Value | Letter | Name |
|-------|--------|------|
| 1 | Alef | |
| 2 | Bet | |
| 3 | Gimel | |
| 4 | Dalet | |
| 5 | Heh | |
| 6 | Vav | |
| 7 | Zayin | |
| 8 | Chet | |
| 9 | Tet | |
| 10 | Yod | |
| 20 | Kaf | |
| 30 | Lamed | |
| 40 | Mem | |
| 50 | Nun | |
| 60 | Samech | |
| 70 | Ayin | |
| 80 | Peh | |
| 90 | Tzadi | |
| 100 | Kuf | |
| 200 | Resh | |
| 300 | Shin | |
| 400 | Tav | |

Special cases:
- 15 is written as Tet-Vav (9+6) NOT Yod-Heh (to avoid spelling a divine name)
- 16 is written as Tet-Zayin (9+7) NOT Yod-Vav (same reason)
- Years omit the thousands digit: 5786 is written as 786

## Israeli Holiday Calendar

### Days Fully Off Work in Israel

| Holiday | Hebrew Date | Type |
|---------|------------|------|
| Rosh Hashana (Day 1) | 1 Tishrei | National |
| Rosh Hashana (Day 2) | 2 Tishrei | National |
| Yom Kippur | 10 Tishrei | National |
| Sukkot (Day 1) | 15 Tishrei | National |
| Simchat Torah | 22 Tishrei | National |
| Pesach (Day 1) | 15 Nisan | National |
| Pesach (Day 7) | 21 Nisan | National |
| Yom HaAtzmaut | 5 Iyar | National |
| Shavuot | 6 Sivan | National |

### Memorial/Observance Days (Partial or Full Closure)

| Day | Hebrew Date | Notes |
|-----|------------|-------|
| Yom HaShoah | 27 Nisan | Sirens, some closures |
| Yom HaZikaron | 4 Iyar | Sirens, closures |
| Tisha B'Av | 9 Av | Some closures |

### Days With Modified Schedules

| Period | Dates | Notes |
|--------|-------|-------|
| Sukkot Chol HaMoed | 16-21 Tishrei | Reduced hours, some closed |
| Pesach Chol HaMoed | 16-20 Nisan | Reduced hours, some closed |
| Chanukah | 25 Kislev - 2 Tevet | Schools off, businesses open |

## Python Libraries

- **pyluach:** Pure Python Hebrew calendar library (recommended)
  - Install: `pip install pyluach`
  - Docs: https://github.com/simlist/pyluach

- **hebcal:** Hebrew calendar computations
  - Web API: https://www.hebcal.com/home/developer-apis
