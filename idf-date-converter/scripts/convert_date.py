#!/usr/bin/env python3
"""Hebrew-Gregorian Date Converter for Israeli applications.

Converts between Hebrew (Jewish) calendar and Gregorian dates, looks up
Israeli holidays, formats dual dates for Israeli documents, and calculates
Israeli business days.

Requirements:
    pip install pyluach

Usage:
    python convert_date.py today
    python convert_date.py to-hebrew 2026-02-24
    python convert_date.py to-gregorian 5786 12 7      # 7 Adar 5786 (month 12 = Adar)
    python convert_date.py holidays 2026
    python convert_date.py business-days 2026-03-01 2026-03-31

Two-tier holiday model:
    Statutory rest days (the days on which Israeli workplaces close by law) are
    excluded from business-day counts. Observances such as Purim,
    Yom HaZikaron, Chol HaMoed and the public fasts are ordinary working days in
    law, so they are reported in the range but not deducted. Yom HaShoah,
    Yom HaZikaron and Yom HaAtzmaut are subject to legislated day-of-week
    displacement, which this script applies rather than hard-coding 27 Nisan /
    4 Iyar / 5 Iyar.
"""

import argparse
import sys
from datetime import date, timedelta

try:
    from pyluach import dates, hebrewcal
    HAS_PYLUACH = True
except ImportError:
    HAS_PYLUACH = False


# Hebrew month names for fallback display.
# Month 12 is plain Adar in a regular year but Adar I in a leap year, so it can
# only be named once the year is known -- see hebrew_month_name().
HEBREW_MONTHS = {
    1: "Nisan", 2: "Iyar", 3: "Sivan", 4: "Tammuz", 5: "Av", 6: "Elul",
    7: "Tishrei", 8: "Cheshvan", 9: "Kislev", 10: "Tevet", 11: "Shevat",
    12: "Adar", 13: "Adar II"
}


def is_hebrew_leap_year(year: int) -> bool:
    """Return True if a Hebrew year is a leap year (13 months) in the Metonic cycle."""
    return year % 19 in {0, 3, 6, 8, 11, 14, 17}


def hebrew_month_name(year: int, month: int) -> str:
    """Name a Hebrew month, disambiguating Adar / Adar I by leap-year status.

    Month 12 is plain Adar in a regular year and Adar I in a leap year. Naming it
    "Adar" unconditionally puts the answer a full month away from the intended
    date, because Purim and the other Adar observances fall in Adar II.
    """
    if month == 12 and is_hebrew_leap_year(year):
        return "Adar I"
    return HEBREW_MONTHS.get(month, f"Month {month}")

# Israeli holidays, split by legal effect.
# Month numbering: 7=Tishrei (start of civil year), 1=Nisan (start of religious year).
#
# STATUTORY_REST_DAYS are the days on which Israeli workplaces, banks and public
# transport close by law -- the only days deducted from a business-day count.
STATUTORY_REST_DAYS = {
    (7, 1): "Rosh Hashana (Day 1)",
    (7, 2): "Rosh Hashana (Day 2)",
    (7, 10): "Yom Kippur",
    (7, 15): "Sukkot (Day 1)",
    (7, 22): "Shmini Atzeret / Simchat Torah",
    (1, 15): "Pesach (Day 1)",
    (1, 21): "Pesach (Day 7)",
    (3, 6): "Shavuot",
    # Yom HaAtzmaut is a rest day too, but its date is displaced by weekday and
    # so is resolved in displaced_national_days() rather than keyed here.
}

# OBSERVANCES are marked and reported but remain working days in law
# (Chol HaMoed and Purim run reduced hours; the public fasts are full workdays).
OBSERVANCES = {
    (7, 16): "Sukkot (Chol HaMoed)",
    (7, 17): "Sukkot (Chol HaMoed)",
    (7, 18): "Sukkot (Chol HaMoed)",
    (7, 19): "Sukkot (Chol HaMoed)",
    (7, 20): "Sukkot (Chol HaMoed)",
    (1, 16): "Pesach (Chol HaMoed)",
    (1, 17): "Pesach (Chol HaMoed)",
    (1, 18): "Pesach (Chol HaMoed)",
    (1, 19): "Pesach (Chol HaMoed)",
    (1, 20): "Pesach (Chol HaMoed)",
    (11, 15): "Tu B'Shvat",
    (2, 18): "Lag BaOmer",
}

# Adar observances are keyed separately: in a leap year they fall in Adar II
# (month 13), not in Adar I (month 12).
ADAR_OBSERVANCES = {
    14: "Purim",
    15: "Shushan Purim (the operative Purim in Jerusalem and other walled cities)",
}

# Erev chag: shortened working days. Banks, government offices, courts and most
# employers close around midday, and Erev Pesach is a near-total closure after
# midday. They are working days, so they are not deducted, but a business-day
# count that does not surface them will over-state available hours.
EREV_CHAG = {
    (6, 29): "Erev Rosh Hashana",
    (7, 9): "Erev Yom Kippur",
    (7, 14): "Erev Sukkot",
    (7, 21): "Erev Simchat Torah (Hoshana Rabba)",
    (1, 14): "Erev Pesach (also Ta'anit Bechorot)",
    (1, 20): "Erev Pesach VII",
    (3, 5): "Erev Shavuot",
}


def _chanukah_days(heb_year: int) -> dict:
    """Map the Chanukah days of a Hebrew year to their labels.

    Chanukah runs 25 Kislev to 2 or 3 Tevet depending on whether Kislev has 29 or
    30 days that year, so the tail is derived by walking forward from 25 Kislev
    rather than assumed.
    """
    if not HAS_PYLUACH:
        return {}
    out = {}
    start = dates.HebrewDate(heb_year, 9, 25)
    for offset in range(8):
        d = (start + offset)
        out[(d.month, d.day)] = f"Chanukah (Day {offset + 1})"
    return out


def postponed_fasts(heb_year: int) -> dict:
    """Resolve the public fasts of a Hebrew year, applying the nidcheh rules.

    A fast is never observed on Shabbat, so four of the five move when they land
    on one, and they do not all move in the same direction:

    * Tzom Gedaliah (3 Tishrei), 17 Tammuz and Tisha B'Av (9 Av) are POSTPONED to
      the following Sunday when they fall on Shabbat.
    * Ta'anit Esther (13 Adar, or 13 Adar II in a leap year) is brought FORWARD to
      the preceding Thursday (11 Adar), because it must precede Purim.
    * Asara B'Tevet (10 Tevet) can fall on a Friday but never on Shabbat, so it
      never moves.

    Hard-coding the nominal dates puts Ta'anit Esther two days late and the
    postponed fasts a day early in any year where the fast lands on Shabbat.

    Returns a dict of {datetime.date: label}.
    """
    if not HAS_PYLUACH:
        return {}

    adar = 13 if is_hebrew_leap_year(heb_year) else 12
    out = {}

    for month, day, label in (
        (7, 3, "Fast of Gedaliah"),
        (4, 17, "Fast of 17 Tammuz"),
        (5, 9, "Tisha B'Av"),
        (10, 10, "Fast of 10 Tevet"),
    ):
        d = dates.HebrewDate(heb_year, month, day).to_pydate()
        if d.weekday() == 5:  # Shabbat -> postponed to Sunday
            d += timedelta(days=1)
        out[d] = label

    esther = dates.HebrewDate(heb_year, adar, 13).to_pydate()
    if esther.weekday() == 5:  # Shabbat -> brought forward to Thursday 11 Adar
        esther -= timedelta(days=2)
    out[esther] = "Fast of Esther (Ta'anit Esther)"

    return out


# The modern state days did not always exist, and the displacement rules that
# move them were adopted later still. Applying today's rules to a historical year
# silently invents observances and shifts real ones. Effective years:
#   Yom HaAtzmaut         enshrined in law as a state holiday      1949
#   Friday/Saturday displacement of Yom HaAtzmaut decided          1951
#   Monday postponement of Yom HaAtzmaut in force                  2004
#   Yom HaZikaron         27 Nisan... 4 Iyar established by council 1951,
#                         enacted into law                          1963
#   Yom HaShoah           27 Nisan set by Knesset resolution        1951
YOM_HAATZMAUT_FROM = 1949
YOM_HAZIKARON_FROM = 1951
YOM_HASHOAH_FROM = 1951
FRI_SAT_DISPLACEMENT_FROM = 1951
MONDAY_POSTPONEMENT_FROM = 2004

# Later state days and observances, each with the Gregorian year it began.
# All are working days; none is a statutory rest day.
# Yitzhak Rabin Memorial Day (12 Cheshvan) and Sigd (29 Cheshvan) are
# deliberately NOT emitted. Both carry their own date rules that this script
# does not model, and hard-coding the nominal Hebrew date disagreed with Hebcal
# in several of the years tested. Omitting them is preferable to emitting a
# confident wrong date; look them up directly when they matter.
MODERN_STATE_DAYS = [
    (2, 28, "Yom Yerushalayim", 1968),
    (1, 10, "Yom HaAliyah", 2016),
]


def displaced_national_days(heb_year: int) -> dict:
    """Resolve Yom HaShoah, Yom HaZikaron and Yom HaAtzmaut for a Hebrew year.

    The Knesset legislated day-of-week displacement to avoid Shabbat desecration,
    so the nominal 27 Nisan / 4 Iyar / 5 Iyar dates are wrong in most years:

    * Yom HaAtzmaut (nominally 5 Iyar) moves up to Thursday when 5 Iyar falls on
      a Friday (-> 4 Iyar) or Saturday (-> 3 Iyar), and is postponed to Tuesday
      (6 Iyar) when 5 Iyar falls on a Monday. 5 Iyar can fall only on Monday,
      Wednesday, Friday or Saturday, and Wednesday is the only undisplaced case.
    * Yom HaZikaron is always the day immediately preceding Yom HaAtzmaut.
    * Yom HaShoah (nominally 27 Nisan) moves back to Thursday 26 Nisan when it
      falls on a Friday, and forward to Monday 28 Nisan when it falls on a Sunday.

    Returns a dict of {datetime.date: label}.
    """
    if not HAS_PYLUACH:
        return {}

    out = {}

    iyar5 = dates.HebrewDate(heb_year, 2, 5).to_pydate()
    civil = iyar5.year
    weekday = iyar5.weekday()  # Mon=0 ... Fri=4, Sat=5, Sun=6
    atzmaut = iyar5
    if weekday == 4 and civil >= FRI_SAT_DISPLACEMENT_FROM:
        atzmaut = iyar5 - timedelta(days=1)   # Friday -> Thursday (4 Iyar)
    elif weekday == 5 and civil >= FRI_SAT_DISPLACEMENT_FROM:
        atzmaut = iyar5 - timedelta(days=2)   # Saturday -> Thursday (3 Iyar)
    elif weekday == 0 and civil >= MONDAY_POSTPONEMENT_FROM:
        atzmaut = iyar5 + timedelta(days=1)   # Monday -> Tuesday (6 Iyar)

    if civil >= YOM_HAATZMAUT_FROM:
        out[atzmaut] = "Yom HaAtzmaut"
    if civil >= YOM_HAZIKARON_FROM:
        out[atzmaut - timedelta(days=1)] = "Yom HaZikaron"

    nisan27 = dates.HebrewDate(heb_year, 1, 27).to_pydate()
    if nisan27.year >= YOM_HASHOAH_FROM:
        # The year the Friday/Sunday displacement of Yom HaShoah itself took
        # effect is not established here, so it is applied throughout. Treat
        # mid-century Yom HaShoah dates as approximate.
        if nisan27.weekday() == 4:      # Friday -> Thursday (26 Nisan)
            shoah = nisan27 - timedelta(days=1)
        elif nisan27.weekday() == 6:    # Sunday -> Monday (28 Nisan)
            shoah = nisan27 + timedelta(days=1)
        else:
            shoah = nisan27
        out[shoah] = "Yom HaShoah"

    for month, day, label, from_year in MODERN_STATE_DAYS:
        d = dates.HebrewDate(heb_year, month, day).to_pydate()
        if d.year >= from_year:
            out.setdefault(d, label)

    return out


def gregorian_to_hebrew(greg_date: date) -> dict:
    """Convert a Gregorian date to Hebrew date.

    Args:
        greg_date: Python date object

    Returns:
        Dictionary with Hebrew date components
    """
    if HAS_PYLUACH:
        gd = dates.GregorianDate(greg_date.year, greg_date.month, greg_date.day)
        hd = gd.to_heb()
        return {
            "year": hd.year,
            "month": hd.month,
            "day": hd.day,
            "month_name": hd.month_name(),
            "formatted": f"{hd.day} {hd.month_name()} {hd.year}",
        }
    else:
        print("WARNING: pyluach not installed. Install with: pip install pyluach",
              file=sys.stderr)
        return {
            "error": "pyluach not installed",
            "install": "pip install pyluach"
        }


def hebrew_to_gregorian(year: int, month: int, day: int) -> dict:
    """Convert a Hebrew date to Gregorian.

    Args:
        year: Hebrew year (e.g., 5786)
        month: Hebrew month (7=Tishrei, 1=Nisan, etc.)
        day: Day of month

    Returns:
        Dictionary with Gregorian date components
    """
    if HAS_PYLUACH:
        try:
            hd = dates.HebrewDate(year, month, day)
        except ValueError as exc:
            hint = ""
            if month == 13 and not is_hebrew_leap_year(year):
                hint = (f" Hebrew year {year} is not a leap year, so it has no "
                        f"Adar II (month 13); use month 12 for Adar.")
            msg = hint.strip() if hint else f"{exc}"
            print(f"Error: {msg}", file=sys.stderr)
            sys.exit(2)
        gd = hd.to_greg()
        return {
            "year": gd.year,
            "month": gd.month,
            "day": gd.day,
            "formatted": f"{gd.year}-{gd.month:02d}-{gd.day:02d}",
            "display": f"{gd.day} {date(gd.year, gd.month, gd.day).strftime('%B')} {gd.year}",
        }
    else:
        print("WARNING: pyluach not installed. Install with: pip install pyluach",
              file=sys.stderr)
        return {"error": "pyluach not installed", "install": "pip install pyluach"}


def format_dual_date(greg_date: date) -> str:
    """Format a date as dual Gregorian/Hebrew for Israeli documents.

    Args:
        greg_date: Python date object

    Returns:
        Formatted dual date string
    """
    heb = gregorian_to_hebrew(greg_date)
    if "error" in heb:
        return f"{greg_date.strftime('%d %B %Y')} (Hebrew date unavailable - install pyluach)"

    greg_str = greg_date.strftime("%d %B %Y")
    heb_str = heb["formatted"]
    return f"{greg_str} / {heb_str}"


def is_shabbat(greg_date: date) -> bool:
    """Check if a date falls on Shabbat (Saturday).

    Args:
        greg_date: Python date object

    Returns:
        True if the date is Shabbat
    """
    return greg_date.weekday() == 5  # Saturday


def classify_israeli_day(greg_date: date) -> tuple:
    """Classify a Gregorian date against the Israeli holiday calendar.

    Args:
        greg_date: Python date object

    Returns:
        Tuple of (kind, label) where kind is "rest" (statutory day of rest),
        "erev" (a shortened working day before a festival), "observance"
        (marked but a full working day), or None.
    """
    if not HAS_PYLUACH:
        return (None, None)

    hd = dates.GregorianDate(greg_date.year, greg_date.month, greg_date.day).to_heb()
    key = (hd.month, hd.day)

    fasts = postponed_fasts(hd.year)
    if greg_date in fasts:
        return ("observance", fasts[greg_date])

    displaced = displaced_national_days(hd.year)
    if greg_date in displaced:
        label = displaced[greg_date]
        # Yom HaAtzmaut is a statutory rest day; every other day here is a
        # marked but ordinary working day.
        return ("rest" if label == "Yom HaAtzmaut" else "observance", label)

    if key in STATUTORY_REST_DAYS:
        return ("rest", STATUTORY_REST_DAYS[key])

    # Adar observances live in Adar II (month 13) in a leap year, Adar (12) otherwise.
    adar_month = 13 if is_hebrew_leap_year(hd.year) else 12
    if hd.month == adar_month and hd.day in ADAR_OBSERVANCES:
        return ("observance", ADAR_OBSERVANCES[hd.day])

    chanukah = _chanukah_days(hd.year)
    if key in chanukah:
        return ("observance", chanukah[key])

    if key in OBSERVANCES:
        return ("observance", OBSERVANCES[key])

    if key in EREV_CHAG:
        return ("erev", EREV_CHAG[key])

    return (None, None)


def is_israeli_holiday(greg_date: date) -> tuple:
    """Check whether a date is a statutory Israeli day of rest.

    Args:
        greg_date: Python date object

    Returns:
        Tuple of (is_rest_day: bool, holiday_name: str or None). Observances such
        as Purim, Yom HaZikaron and the public fasts return False here because
        they are working days in law; use classify_israeli_day() to see them.
    """
    kind, label = classify_israeli_day(greg_date)
    if kind == "rest":
        return (True, label)
    return (False, None)


def is_israeli_business_day(greg_date: date) -> bool:
    """Check if a date is an Israeli business day.

    Israeli business week: Sunday-Thursday, with Friday a half day in many
    sectors and Saturday (Shabbat) the statutory day of rest. Friday is counted
    as a business day here because it is a working day in law; deduct it yourself
    if your sector closes on Fridays.

    Args:
        greg_date: Python date object

    Returns:
        True if the date is a business day in Israel
    """
    if greg_date.weekday() == 5:  # Saturday
        return False

    holiday, _ = is_israeli_holiday(greg_date)
    return not holiday


def count_business_days(start_date: date, end_date: date) -> dict:
    """Count Israeli business days between two dates.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        Dictionary with count and details
    """
    total_days = 0
    business_days = 0
    holidays_in_range = []
    observances_in_range = []
    erev_in_range = []
    shabbatot = 0

    current = start_date
    while current <= end_date:
        total_days += 1
        kind, label = classify_israeli_day(current)
        if kind == "observance":
            observances_in_range.append(
                f"{current.strftime('%Y-%m-%d')} - {label} (working day)"
            )
        elif kind == "erev":
            erev_in_range.append(
                f"{current.strftime('%Y-%m-%d')} - {label} (shortened working day)"
            )
        elif kind == "rest" and is_shabbat(current):
            # Report it even though Shabbat already excludes it, otherwise a
            # festival landing on Shabbat silently vanishes from the summary.
            holidays_in_range.append(
                f"{current.strftime('%Y-%m-%d')} - {label} (falls on Shabbat)"
            )
        if is_shabbat(current):
            shabbatot += 1
        elif kind == "rest":
            holidays_in_range.append(
                f"{current.strftime('%Y-%m-%d')} - {label}"
            )
        else:
            business_days += 1
        current += timedelta(days=1)

    return {
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "total_days": total_days,
        "business_days": business_days,
        "shabbatot": shabbatot,
        "holidays": holidays_in_range,
        "observances": observances_in_range,
        "erev_chag": erev_in_range,
    }


def get_holidays_for_year(greg_year: int) -> list:
    """Get approximate Gregorian dates for Israeli holidays in a given year.

    Args:
        greg_year: Gregorian year

    Returns:
        List of dictionaries with holiday info
    """
    if not HAS_PYLUACH:
        return [{"error": "pyluach not installed", "install": "pip install pyluach"}]

    if not 1 <= greg_year <= 9999:
        return [{"error": f"year {greg_year} is out of range (1-9999)"}]

    holidays = []
    # Scan the entire Gregorian year day by day
    current = date(greg_year, 1, 1)
    end = date(greg_year, 12, 31)

    while current <= end:
        kind, label = classify_israeli_day(current)
        if kind:
            heb = gregorian_to_hebrew(current)
            holidays.append({
                "holiday": label,
                "kind": {"rest": "rest day",
                         "erev": "half day"}.get(kind, "working day"),
                "gregorian": current.isoformat(),
                "hebrew": heb.get("formatted", "N/A"),
                "day_of_week": current.strftime("%A"),
            })
        current += timedelta(days=1)

    return holidays


def parse_iso_date(text: str) -> date:
    """Parse a YYYY-MM-DD string, exiting with a readable message on bad input."""
    try:
        return date.fromisoformat(text.strip())
    except ValueError:
        print(f"Error: '{text}' is not a valid date. Expected YYYY-MM-DD, "
              f"for example 2026-02-24.", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="Hebrew-Gregorian Date Converter for Israeli Applications"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Today command
    subparsers.add_parser("today", help="Show today's date in both calendars")

    # To Hebrew command
    to_heb = subparsers.add_parser("to-hebrew", help="Convert Gregorian to Hebrew")
    to_heb.add_argument("date", help="Gregorian date (YYYY-MM-DD)")

    # To Gregorian command
    to_greg = subparsers.add_parser("to-gregorian", help="Convert Hebrew to Gregorian")
    to_greg.add_argument("year", type=int, help="Hebrew year (e.g., 5786)")
    to_greg.add_argument("month", type=int, help="Hebrew month (7=Tishrei, 1=Nisan)")
    to_greg.add_argument("day", type=int, help="Day of month")

    # Holidays command
    holidays_parser = subparsers.add_parser("holidays",
                                             help="List Israeli holidays for a year")
    holidays_parser.add_argument("year", type=int, help="Gregorian year")

    # Business days command
    bdays = subparsers.add_parser("business-days",
                                   help="Count Israeli business days between dates")
    bdays.add_argument("start", help="Start date (YYYY-MM-DD)")
    bdays.add_argument("end", help="End date (YYYY-MM-DD)")

    # Dual date command
    dual = subparsers.add_parser("dual", help="Format dual date for Israeli documents")
    dual.add_argument("date", help="Gregorian date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "today":
        today = date.today()
        heb = gregorian_to_hebrew(today)
        print(f"Gregorian: {today.strftime('%A, %d %B %Y')}")
        if "error" not in heb:
            print(f"Hebrew:    {heb['formatted']}")
            print(f"\nDual format: {format_dual_date(today)}")
        else:
            print(f"Hebrew:    Install pyluach: {heb['install']}")

        is_bday = is_israeli_business_day(today)
        print(f"\nIsraeli business day: {'Yes' if is_bday else 'No'}")
        if is_shabbat(today):
            print("  (Shabbat)")
        kind, label = classify_israeli_day(today)
        if kind == "rest":
            print(f"  (Statutory rest day: {label})")
        elif kind == "erev":
            print(f"  ({label} - a shortened working day)")
        elif kind == "observance":
            print(f"  ({label} - a working day)")
        print("\nNote: the Hebrew date shown is the daytime date. After sunset "
              "the Hebrew date is one day later.")

    elif args.command == "to-hebrew":
        greg_date = parse_iso_date(args.date)
        heb = gregorian_to_hebrew(greg_date)
        if "error" not in heb:
            print(f"Gregorian: {greg_date.strftime('%d %B %Y')}")
            print(f"Hebrew:    {heb['formatted']}")
            print(f"\nDual format: {format_dual_date(greg_date)}")
        else:
            print(f"Error: {heb['error']}")
            print(f"Install: {heb['install']}")

    elif args.command == "to-gregorian":
        greg = hebrew_to_gregorian(args.year, args.month, args.day)
        if "error" not in greg:
            month_name = hebrew_month_name(args.year, args.month)
            print(f"Hebrew:    {args.day} {month_name} {args.year}")
            print(f"Gregorian: {greg['display']}")
            print(f"ISO:       {greg['formatted']}")
        else:
            print(f"Error: {greg['error']}")
            print(f"Install: {greg['install']}")

    elif args.command == "holidays":
        holidays = get_holidays_for_year(args.year)
        if holidays and "error" in holidays[0]:
            print(f"Error: {holidays[0]['error']}", file=sys.stderr)
            if "install" in holidays[0]:
                print(f"Install: {holidays[0]['install']}", file=sys.stderr)
            sys.exit(2)
        else:
            print(f"Israeli Holidays in {args.year}:")
            print(f"{'Holiday':<32} {'Gregorian':<12} {'Hebrew':<22} "
                  f"{'Day':<10} {'Status':<12}")
            print("-" * 92)
            for h in holidays:
                print(f"{h['holiday']:<32} {h['gregorian']:<12} "
                      f"{h['hebrew']:<22} {h['day_of_week']:<10} {h['kind']:<12}")

    elif args.command == "business-days":
        start_date = parse_iso_date(args.start)
        end_date = parse_iso_date(args.end)
        if end_date < start_date:
            print("Error: end date is before start date.", file=sys.stderr)
            sys.exit(2)

        result = count_business_days(start_date, end_date)
        print(f"Period: {result['start']} to {result['end']}")
        print(f"Total days:    {result['total_days']}")
        print(f"Business days: {result['business_days']}")
        print(f"Shabbatot:     {result['shabbatot']}")
        if result['holidays']:
            print(f"Statutory rest days ({len(result['holidays'])}):")
            for h in result['holidays']:
                print(f"  {h}")
        if result['observances']:
            print(f"Observances, not deducted ({len(result['observances'])}):")
            for h in result['observances']:
                print(f"  {h}")
        if result['erev_chag']:
            print(f"Erev chag, not deducted ({len(result['erev_chag'])}):")
            for h in result['erev_chag']:
                print(f"  {h}")

    elif args.command == "dual":
        print(format_dual_date(parse_iso_date(args.date)))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
