#!/usr/bin/env python3
"""Validate and format Israeli shipping addresses.

Checks address components against Israeli postal standards:
- Mikud (ZIP) must be exactly 7 digits
- Required fields: street, house number, city, mikud
- Special handling for kibbutz, military, and industrial zone addresses

Usage:
    python scripts/format_address.py --validate --street "הרצל" --house 42 --city "תל אביב-יפו" --mikud 6120001
    python scripts/format_address.py --json address.json
    python scripts/format_address.py --help
"""

import sys
import json
import re
import argparse
from typing import Optional


# Mikud region prefixes (first 2 digits)
MIKUD_REGIONS = {
    "10": "Jerusalem", "11": "Jerusalem", "12": "Jerusalem",
    "13": "Jerusalem", "14": "Jerusalem", "15": "Jerusalem",
    "16": "Jerusalem", "17": "Jerusalem", "18": "Jerusalem",
    "19": "Jerusalem",
    "20": "North", "21": "North", "22": "North", "23": "North",
    "24": "North", "25": "North", "26": "North", "27": "North",
    "28": "North", "29": "North",
    "30": "Haifa", "31": "Haifa", "32": "Haifa", "33": "Haifa",
    "34": "Haifa", "35": "Haifa", "36": "Haifa", "37": "Haifa",
    "38": "Haifa", "39": "Haifa",
    "40": "Sharon", "41": "Sharon", "42": "Sharon", "43": "Sharon",
    "44": "Sharon", "45": "Sharon", "46": "Sharon", "47": "Sharon",
    "48": "Sharon", "49": "Sharon",
    "50": "Center", "51": "Center", "52": "Center", "53": "Center",
    "54": "Center", "55": "Center", "56": "Center", "57": "Center",
    "58": "Center", "59": "Center",
    "60": "Tel Aviv", "61": "Tel Aviv", "62": "Tel Aviv",
    "63": "Tel Aviv", "64": "Tel Aviv", "65": "Tel Aviv",
    "66": "Tel Aviv", "67": "Tel Aviv", "68": "Tel Aviv",
    "69": "Tel Aviv",
    "70": "South", "71": "South", "72": "South", "73": "South",
    "74": "South", "75": "South", "76": "South", "77": "South",
    "78": "South", "79": "South",
    "80": "Negev", "81": "Negev", "82": "Negev", "83": "Negev",
    "84": "Negev", "85": "Negev", "86": "Negev", "87": "Negev",
    "88": "Negev/Eilat", "89": "Negev/Eilat",
}

# Address types
ADDRESS_TYPE_STANDARD = "standard"
ADDRESS_TYPE_KIBBUTZ = "kibbutz"
ADDRESS_TYPE_MILITARY = "military"
ADDRESS_TYPE_INDUSTRIAL = "industrial"
ADDRESS_TYPE_PO_BOX = "po_box"


def normalize_hebrew(text: str) -> str:
    """Remove niqqud (Hebrew vowel diacritics) and normalize for carrier APIs.

    Strips Unicode combining characters in the Hebrew niqqud range (U+05B0-U+05C7)
    which can cause carrier API matching failures.
    """
    return "".join(
        ch for ch in text
        if not (0x05B0 <= ord(ch) <= 0x05C7)
    )


def validate_mikud(mikud: str) -> tuple[bool, str]:
    """Validate Israeli mikud (ZIP code).

    Args:
        mikud: The mikud string to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not re.match(r"^\d{7}$", mikud):
        if re.match(r"^\d{5}$", mikud):
            return False, (
                f"Mikud '{mikud}' is 5 digits (old format). "
                "All Israeli mikud codes are now 7 digits. "
                "Look up the current code at israelpost.co.il/mikud"
            )
        return False, (
            f"Mikud '{mikud}' is invalid. Must be exactly 7 digits."
        )

    prefix = mikud[:2]
    if prefix not in MIKUD_REGIONS:
        return False, (
            f"Mikud prefix '{prefix}' does not match any known region."
        )

    return True, ""


def validate_address(address: dict) -> list[str]:
    """Validate address components.

    Args:
        address: Dictionary with address fields.

    Returns:
        List of error strings. Empty list means valid.
    """
    errors = []
    addr_type = address.get("type", ADDRESS_TYPE_STANDARD)

    # Military addresses have different requirements
    if addr_type == ADDRESS_TYPE_MILITARY:
        if "military_code" not in address:
            errors.append("Military address requires 'military_code' field")
        return errors

    # PO Box addresses
    if addr_type == ADDRESS_TYPE_PO_BOX:
        if "po_box" not in address:
            errors.append("PO Box address requires 'po_box' field")
        if "city" not in address:
            errors.append("Missing required field: city")
        if "mikud" in address:
            valid, msg = validate_mikud(str(address["mikud"]))
            if not valid:
                errors.append(msg)
        return errors

    # Standard, kibbutz, industrial addresses
    if addr_type == ADDRESS_TYPE_KIBBUTZ:
        if "settlement" not in address:
            errors.append("Kibbutz/Moshav address requires 'settlement' field")
    else:
        if "street" not in address:
            errors.append("Missing required field: street (רחוב)")
        if "house" not in address:
            errors.append("Missing required field: house number (מספר בית)")

    if "city" not in address and addr_type != ADDRESS_TYPE_KIBBUTZ:
        errors.append("Missing required field: city (עיר)")

    if "mikud" not in address:
        errors.append("Missing required field: mikud (מיקוד)")
    else:
        valid, msg = validate_mikud(str(address["mikud"]))
        if not valid:
            errors.append(msg)

    return errors


def format_address(address: dict) -> str:
    """Format address into standard Israeli shipping format.

    Args:
        address: Dictionary with address fields.

    Returns:
        Formatted address string.
    """
    addr_type = address.get("type", ADDRESS_TYPE_STANDARD)
    lines = []

    # Normalize Hebrew text fields to strip niqqud for carrier APIs
    street = normalize_hebrew(address.get("street", ""))
    city = normalize_hebrew(address.get("city", ""))
    settlement = normalize_hebrew(address.get("settlement", ""))

    if addr_type == ADDRESS_TYPE_MILITARY:
        lines.append(f"צה\"ל דואר צבאי {address.get('military_code', '')}")
        return "\n".join(lines)

    if addr_type == ADDRESS_TYPE_PO_BOX:
        lines.append(f"ת.ד. {address.get('po_box', '')}")
        city_line = city
        if "mikud" in address:
            city_line += f", {address['mikud']}"
        lines.append(city_line)
        return "\n".join(lines)

    # Build first line (street/settlement)
    if addr_type == ADDRESS_TYPE_KIBBUTZ:
        first_line = settlement
        if "house" in address:
            first_line += f", בית {address['house']}"
    elif addr_type == ADDRESS_TYPE_INDUSTRIAL:
        first_line = street
        if "building" in address:
            first_line += f", בניין {address['building']}"
    else:
        first_line = f"רחוב {street} {address.get('house', '')}"
        if "entrance" in address:
            first_line += f", כניסה {address['entrance']}"
        if "floor" in address:
            first_line += f", קומה {address['floor']}"
        if "apartment" in address:
            first_line += f", דירה {address['apartment']}"

    lines.append(first_line)

    # Build second line (city + mikud)
    city_line = city or settlement
    if "mikud" in address:
        city_line += f", {address['mikud']}"
    lines.append(city_line)

    return "\n".join(lines)


def main():
    """Main entry point for address formatting."""
    parser = argparse.ArgumentParser(
        description="Validate and format Israeli shipping addresses"
    )
    parser.add_argument("--json", help="Read address from JSON file")
    parser.add_argument("--validate", action="store_true",
                        help="Validate only (no formatted output)")
    parser.add_argument("--street", help="Street name (Hebrew)")
    parser.add_argument("--house", help="House number")
    parser.add_argument("--entrance", help="Entrance (כניסה)")
    parser.add_argument("--floor", help="Floor (קומה)")
    parser.add_argument("--apartment", help="Apartment number (דירה)")
    parser.add_argument("--city", help="City name (Hebrew)")
    parser.add_argument("--mikud", help="Mikud / ZIP code (7 digits)")
    parser.add_argument("--type", default="standard",
                        choices=["standard", "kibbutz", "military",
                                 "industrial", "po_box"],
                        help="Address type")

    args = parser.parse_args()

    # Build address from arguments or JSON
    if args.json:
        try:
            with open(args.json) as f:
                address = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.json}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            sys.exit(1)
    elif args.street or args.city or args.mikud:
        address = {"type": args.type}
        if args.street:
            address["street"] = args.street
        if args.house:
            address["house"] = args.house
        if args.entrance:
            address["entrance"] = args.entrance
        if args.floor:
            address["floor"] = args.floor
        if args.apartment:
            address["apartment"] = args.apartment
        if args.city:
            address["city"] = args.city
        if args.mikud:
            address["mikud"] = args.mikud
    else:
        parser.print_help()
        sys.exit(1)

    # Validate
    errors = validate_address(address)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if args.validate:
        print("VALIDATION PASSED")
        mikud = str(address.get("mikud", ""))
        prefix = mikud[:2]
        region = MIKUD_REGIONS.get(prefix, "Unknown")
        print(f"  Region: {region} (prefix {prefix})")
        sys.exit(0)

    # Format and print
    formatted = format_address(address)
    print("Formatted address:")
    print(formatted)


if __name__ == "__main__":
    main()
