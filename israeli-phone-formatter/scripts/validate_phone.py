#!/usr/bin/env python3
"""Validate, format, and convert Israeli phone numbers."""

import argparse
import re
import sys

PATTERNS = {
    "mobile": r"^0(5[0-8])\d{7}$",
    "landline": r"^0([2-4]|[89])\d{7}$",
    "voip": r"^0(7[2-7])\d{7}$",
    "toll_free": r"^1800\d{6}$",
    "premium": r"^1700\d{6}$",
    "star": r"^\*\d{4,6}$",
}

CARRIER_MAP = {
    "050": "Pelephone",
    "051": "Azi Communications",
    "052": "Cellcom",
    "053": "Hot Mobile",
    "054": "Partner",
    "055": "Rami Levy / Golan",
    "056": "Partner / Home Cellular",
    "058": "Golan Telecom",
}

AREA_MAP = {
    "02": "Jerusalem",
    "03": "Tel Aviv",
    "04": "Haifa / North",
    "08": "South / Be'er Sheva",
    "09": "Sharon / Netanya",
}


def clean_number(phone: str) -> str:
    """Strip formatting and normalize international prefix."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if cleaned.startswith("+972"):
        cleaned = "0" + cleaned[4:]
    elif cleaned.startswith("972") and len(cleaned) > 9:
        cleaned = "0" + cleaned[3:]
    return cleaned


def validate(phone: str) -> dict:
    """Validate an Israeli phone number and return its type and details."""
    cleaned = clean_number(phone)
    for phone_type, pattern in PATTERNS.items():
        if re.match(pattern, cleaned):
            result = {"valid": True, "type": phone_type, "cleaned": cleaned}
            prefix = cleaned[:3]
            if phone_type == "mobile" and prefix in CARRIER_MAP:
                result["carrier"] = CARRIER_MAP[prefix]
            elif phone_type == "landline":
                area = cleaned[:2]
                if area in AREA_MAP:
                    result["region"] = AREA_MAP[area]
            return result
    return {"valid": False, "type": None, "cleaned": cleaned}


def to_international(phone: str) -> str | None:
    """Convert local number to +972 international format."""
    result = validate(phone)
    if not result["valid"] or result["type"] in ("toll_free", "premium", "star"):
        return None
    return "+972" + result["cleaned"][1:]


def to_local(phone: str) -> str:
    """Convert international format to local."""
    return clean_number(phone)


def main():
    parser = argparse.ArgumentParser(description="Israeli phone number validator")
    parser.add_argument("--number", "-n", help="Phone number to validate")
    parser.add_argument("--batch", action="store_true", help="Read numbers from stdin")
    parser.add_argument("--format", choices=["local", "international"], help="Convert to format")
    args = parser.parse_args()

    if args.batch:
        for line in sys.stdin:
            phone = line.strip()
            if not phone:
                continue
            result = validate(phone)
            status = "VALID" if result["valid"] else "INVALID"
            print(f"{phone}\t{status}\t{result['type'] or 'unknown'}")
    elif args.number:
        result = validate(args.number)
        if result["valid"]:
            print(f"Valid: {result['type']}")
            print(f"Cleaned: {result['cleaned']}")
            if "carrier" in result:
                print(f"Carrier: {result['carrier']}")
            if "region" in result:
                print(f"Region: {result['region']}")
            intl = to_international(args.number)
            if intl:
                print(f"International: {intl}")
        else:
            print(f"Invalid: {result['cleaned']}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
