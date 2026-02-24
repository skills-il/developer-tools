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
    python convert_date.py to-gregorian 5786 6 26
    python convert_date.py holidays 2026
    python convert_date.py business-days 2026-03-01 2026-03-31
"""

import argparse
import sys
from datetime import date, timedelta

try:
    from pyluach import dates, hebrewcal
    HAS_PYLUACH = True
except ImportError:
    HAS_PYLUACH = False


# Hebrew month names for fallback display
HEBREW_MONTHS = {
    1: "Nisan", 2: "Iyar", 3: "Sivan", 4: "Tammuz", 5: "Av", 6: "Elul",
    7: "Tishrei", 8: "Cheshvan", 9: "Kislev", 10: "Tevet", 11: "Shevat",
    12: "Adar", 13: "Adar II"
}

# Israeli holidays (Hebrew month, day) -> holiday name
# Month numbering: 7=Tishrei (start of civil year), 1=Nisan (start of religious year)
ISRAELI_HOLIDAYS = {
    (7, 1): "Rosh Hashana (Day 1)",
    (7, 2): "Rosh Hashana (Day 2)",
    (7, 10): "Yom Kippur",
    (7, 15): "Sukkot (Day 1)",
    (7, 16): "Sukkot (Day 2)",
    (7, 17): "Sukkot (Chol HaMoed)",
    (7, 18): "Sukkot (Chol HaMoed)",
    (7, 19): "Sukkot (Chol HaMoed)",
    (7, 20): "Sukkot (Chol HaMoed)",
    (7, 21): "Hoshana Rabba",
    (7, 22): "Simchat Torah",
    (1, 15): "Pesach (Day 1)",
    (1, 16): "Pesach (Chol HaMoed)",
    (1, 17): "Pesach (Chol HaMoed)",
    (1, 18): "Pesach (Chol HaMoed)",
    (1, 19): "Pesach (Chol HaMoed)",
    (1, 20): "Pesach (Chol HaMoed)",
    (1, 21): "Pesach (Day 7)",
    (3, 6): "Shavuot",
    (1, 27): "Yom HaShoah",
    (2, 4): "Yom HaZikaron",
    (2, 5): "Yom HaAtzmaut",
}


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
        hd = dates.HebrewDate(year, month, day)
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


def is_israeli_holiday(greg_date: date) -> tuple:
    """Check if a Gregorian date falls on an Israeli holiday.

    Args:
        greg_date: Python date object

    Returns:
        Tuple of (is_holiday: bool, holiday_name: str or None)
    """
    if not HAS_PYLUACH:
        return (False, None)

    hd = dates.GregorianDate(greg_date.year, greg_date.month, greg_date.day).to_heb()
    key = (hd.month, hd.day)
    if key in ISRAELI_HOLIDAYS:
        return (True, ISRAELI_HOLIDAYS[key])
    return (False, None)


def is_israeli_business_day(greg_date: date) -> bool:
    """Check if a date is an Israeli business day.

    Israeli business week: Sunday-Thursday (Friday half day, Saturday off)
    Also excludes national holidays.

    Args:
        greg_date: Python date object

    Returns:
        True if the date is a business day in Israel
    """
    # Saturday (5) and Friday (4) are not full business days
    if greg_date.weekday() == 5:  # Saturday
        return False

    holiday, _ = is_israeli_holiday(greg_date)
    if holiday:
        return False

    return True


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
    shabbatot = 0

    current = start_date
    while current <= end_date:
        total_days += 1
        if is_shabbat(current):
            shabbatot += 1
        else:
            is_hol, hol_name = is_israeli_holiday(current)
            if is_hol:
                holidays_in_range.append(
                    f"{current.strftime('%Y-%m-%d')} - {hol_name}"
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

    holidays = []
    # Scan the entire Gregorian year day by day
    current = date(greg_year, 1, 1)
    end = date(greg_year, 12, 31)

    while current <= end:
        is_hol, hol_name = is_israeli_holiday(current)
        if is_hol:
            heb = gregorian_to_hebrew(current)
            holidays.append({
                "holiday": hol_name,
                "gregorian": current.isoformat(),
                "hebrew": heb.get("formatted", "N/A"),
                "day_of_week": current.strftime("%A"),
            })
        current += timedelta(days=1)

    return holidays


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
        is_hol, hol_name = is_israeli_holiday(today)
        if is_hol:
            print(f"  (Holiday: {hol_name})")

    elif args.command == "to-hebrew":
        parts = args.date.split('-')
        greg_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
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
            month_name = HEBREW_MONTHS.get(args.month, f"Month {args.month}")
            print(f"Hebrew:    {args.day} {month_name} {args.year}")
            print(f"Gregorian: {greg['display']}")
            print(f"ISO:       {greg['formatted']}")
        else:
            print(f"Error: {greg['error']}")
            print(f"Install: {greg['install']}")

    elif args.command == "holidays":
        holidays = get_holidays_for_year(args.year)
        if holidays and "error" in holidays[0]:
            print(f"Error: {holidays[0]['error']}")
            print(f"Install: {holidays[0]['install']}")
        else:
            print(f"Israeli Holidays in {args.year}:")
            print(f"{'Holiday':<30} {'Gregorian':<14} {'Hebrew':<25} {'Day':<10}")
            print("-" * 80)
            for h in holidays:
                print(f"{h['holiday']:<30} {h['gregorian']:<14} "
                      f"{h['hebrew']:<25} {h['day_of_week']:<10}")

    elif args.command == "business-days":
        start_parts = args.start.split('-')
        end_parts = args.end.split('-')
        start_date = date(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
        end_date = date(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))

        result = count_business_days(start_date, end_date)
        print(f"Period: {result['start']} to {result['end']}")
        print(f"Total days:    {result['total_days']}")
        print(f"Business days: {result['business_days']}")
        print(f"Shabbatot:     {result['shabbatot']}")
        if result['holidays']:
            print(f"Holidays ({len(result['holidays'])}):")
            for h in result['holidays']:
                print(f"  {h}")

    elif args.command == "dual":
        parts = args.date.split('-')
        greg_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        print(format_dual_date(greg_date))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
