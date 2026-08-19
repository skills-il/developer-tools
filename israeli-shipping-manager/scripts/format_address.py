#!/usr/bin/env python3
"""Validate and format Israeli shipping addresses.

Checks address components against Israeli postal standards:
- Mikud (ZIP) must be exactly 7 digits
- Required fields: street, house number, city, mikud
- Special handling for kibbutz, military, and industrial zone addresses

Every address type is reachable from the command line. Running with no address
fields prints usage and exits 1.

Usage:
    python3 scripts/format_address.py --validate --street "הרצל" --house 42 --city "תל אביב-יפו" --mikud 6120001
    python3 scripts/format_address.py --type kibbutz --settlement "דגניה א" --house 15 --mikud 1512000
    python3 scripts/format_address.py --type military --military-code 01234
    python3 scripts/format_address.py --type po_box --po-box 1234 --city "ירושלים" --mikud 9100001
    python3 scripts/format_address.py --type industrial --street "אזור תעשייה הר טוב" --building 8 --city "בית שמש" --mikud 9906000
    python3 scripts/format_address.py --type no_street --neighbourhood "שכונה 12" --house 5 --city "רהט" --mikud 8546500
    python3 scripts/format_address.py --json address.json
    python3 scripts/format_address.py --help
"""

import sys
import json
import re
import argparse
from typing import Optional


# Mikud leading-digit regions.
#
# Israeli 7-digit mikud codes were allocated broadly NORTH TO SOUTH, with two
# deliberate exceptions: IDF units were given the 0 block, and Jerusalem was
# given the 9 block out of geographic order. An earlier version of this file
# carried a two-digit table that mapped 10-19 to "Jerusalem" and had no entry
# at all for 90-99, which meant every genuine Jerusalem address (9103401,
# 9100701) and every military address was rejected as invalid. The region is
# advisory metadata only and is never a reason to reject a well-formed code.
MIKUD_REGIONS = {
    "0": "IDF military post (דואר צבאי)",
    "1": "Far north (Upper Galilee, Golan, Hula valley)",
    "2": "Galilee and Akko plain",
    "3": "Haifa and Carmel",
    "4": "Sharon",
    "5": "Center (Gush Dan periphery)",
    "6": "Tel Aviv",
    "7": "Center-south and Shfela",
    "8": "Negev and Eilat",
    "9": "Jerusalem and surroundings",
}


def mikud_region(mikud: str) -> str:
    """Return the coarse region for a mikud, or 'Unknown' if it is malformed."""
    return MIKUD_REGIONS.get(mikud[:1], "Unknown") if mikud else "Unknown"


# Address types
ADDRESS_TYPE_STANDARD = "standard"
ADDRESS_TYPE_KIBBUTZ = "kibbutz"
ADDRESS_TYPE_MILITARY = "military"
ADDRESS_TYPE_INDUSTRIAL = "industrial"
ADDRESS_TYPE_PO_BOX = "po_box"
# Localities where houses are addressed by neighbourhood/cluster with no street
# name at all. This is the normal case in recognised Bedouin localities in the
# Negev, parts of East Jerusalem, and freshly-occupied neighbourhoods. Israel
# Post assigns these a mikud regardless. Without this type the validator
# rejected every such address for "missing street".
ADDRESS_TYPE_NO_STREET = "no_street"


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
                "Look up the current code at doar.israelpost.co.il/locatezip"
            )
        return False, (
            f"Mikud '{mikud}' is invalid. Must be exactly 7 digits."
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
    elif addr_type == ADDRESS_TYPE_NO_STREET:
        if "neighbourhood" not in address:
            errors.append(
                "Unnamed-street address requires 'neighbourhood' "
                "(שכונה / אזור) field"
            )
        if "house" not in address:
            errors.append("Missing required field: house number (מספר בית)")
    elif addr_type == ADDRESS_TYPE_INDUSTRIAL:
        # An industrial-zone address is "zone name + building/company", with no
        # house number. Requiring 'house' here made --type industrial
        # unsatisfiable.
        if "street" not in address:
            errors.append("Missing required field: zone name (אזור תעשייה)")
        if "building" not in address and "house" not in address:
            errors.append(
                "Industrial address requires 'building' (or 'house')"
            )
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
    elif addr_type == ADDRESS_TYPE_NO_STREET:
        first_line = normalize_hebrew(address.get("neighbourhood", ""))
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

    # Build second line (city + mikud). A kibbutz address already carries the
    # settlement on the first line, so repeating it here would print it twice.
    city_line = city
    if "mikud" in address:
        city_line = f"{city_line}, {address['mikud']}" if city_line \
            else str(address["mikud"])
    if city_line:
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
    parser.add_argument("--settlement",
                        help="Settlement name (kibbutz / moshav addresses)")
    parser.add_argument("--military-code", dest="military_code",
                        help="IDF military postal number (military addresses)")
    parser.add_argument("--po-box", dest="po_box",
                        help="PO box number (ת.ד.)")
    parser.add_argument("--building",
                        help="Building or company name (industrial-zone addresses)")
    parser.add_argument("--neighbourhood",
                        help="Neighbourhood or cluster name, for localities "
                             "with no street names (--type no_street)")
    parser.add_argument("--type", default="standard",
                        choices=["standard", "kibbutz", "military",
                                 "industrial", "po_box", "no_street"],
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
    elif any([args.street, args.city, args.mikud, args.settlement,
              args.military_code, args.po_box, args.building,
              args.neighbourhood]):
        address = {"type": args.type}
        for field in ("street", "house", "entrance", "floor", "apartment",
                      "city", "mikud", "settlement", "military_code",
                      "po_box", "building", "neighbourhood"):
            value = getattr(args, field)
            if value:
                address[field] = value
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
        if mikud:
            print(f"  Region: {mikud_region(mikud)} (leading digit {mikud[:1]})")
        sys.exit(0)

    # Format and print
    formatted = format_address(address)
    print("Formatted address:")
    print(formatted)


if __name__ == "__main__":
    main()
