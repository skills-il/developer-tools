#!/usr/bin/env python3
"""Validate, format, and convert Israeli phone numbers.

Notes:
- Mobile Number Portability (MNP) has been live in Israel since 2007. The carrier
  inferred from the prefix is the *issuing* carrier, not necessarily the current one.
- 056 (Wataniya) and 059 (Jawwal) are Palestinian territories carriers. They match
  the Israeli mobile shape but are not Israeli consumer mobile numbers.
- For strict E.164 output (WhatsApp, Twilio, libphonenumber), use to_e164() which
  produces digits-only output like '+972521234567'. The hyphenated display form
  '+972-52-123-4567' is for humans only and will fail strict E.164 parsers.
"""

import argparse
import re
import sys

PATTERNS = {
    # Mobile: 10 digits, prefix 050-056, 058, 059 (057 unallocated; 056 = Wataniya, 059 = Jawwal -- Palestinian, flag separately)
    "mobile": r"^0(5[012345689])\d{7}$",
    # Landline: 9 digits, area code 02-04, 08, 09
    "landline": r"^0([2-4]|[89])\d{7}$",
    # Non-geographic / VoIP: 10 digits, prefix 072-079 (077 is Hot, 078 is shared, 079 is Widely et al.)
    "voip": r"^07[2-9]\d{7}$",
    "toll_free": r"^1800\d{6}$",
    "premium": r"^1700\d{6}$",
    "star": r"^\*\d{4,6}$",
}

# Issuing-carrier attribution. Subject to MNP -- treat as historical only.
CARRIER_MAP = {
    "050": "Pelephone",
    "051": "We4G (Xfone)",
    "052": "Cellcom",
    "053": "Hot Mobile (Altice)",
    "054": "Partner Communications",
    "055": "Multi-MVNO (Cellcom, 019 Mobile, Widely, Rami Levy, Cellact, Pelephone)",
    "056": "Wataniya Mobile (Palestinian territories)",
    "058": "Golan (acquired by Cellcom)",
    "059": "Jawwal (Palestinian territories)",
}

# Prefixes that match the Israeli mobile shape but belong to Palestinian carriers.
NON_ISRAELI_MOBILE_PREFIXES = {"056", "059"}

AREA_MAP = {
    "02": "Jerusalem",
    "03": "Tel Aviv",
    "04": "Haifa / North",
    "08": "South / Be'er Sheva",
    "09": "Sharon / Netanya",
}

VOIP_CARRIER_MAP = {
    "072": "Various VoIP / non-geographic providers",
    "073": "Various VoIP / non-geographic providers",
    "074": "Various VoIP / non-geographic providers",
    "076": "Various VoIP / non-geographic providers",
    "077": "Hot (Hot Telecom non-geographic range)",
    "078": "Various VoIP / non-geographic providers",
    "079": "Widely / 019 Mobile / Annatel and other non-geographic providers",
}


def clean_number(phone: str) -> str:
    """Strip formatting and normalize international prefix."""
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)
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
            if phone_type == "mobile":
                if prefix in CARRIER_MAP:
                    result["carrier"] = CARRIER_MAP[prefix]
                    result["mnp_disclaimer"] = (
                        "Issuing carrier only; live carrier may differ due to MNP (since 2007)."
                    )
                if prefix in NON_ISRAELI_MOBILE_PREFIXES:
                    result["non_israeli"] = True
                    result["note"] = (
                        "Palestinian territories carrier; not an Israeli consumer mobile number."
                    )
            elif phone_type == "voip":
                if prefix in VOIP_CARRIER_MAP:
                    result["carrier"] = VOIP_CARRIER_MAP[prefix]
            elif phone_type == "landline":
                area = cleaned[:2]
                if area in AREA_MAP:
                    result["region"] = AREA_MAP[area]
            return result
    return {"valid": False, "type": None, "cleaned": cleaned}


def to_international(phone: str) -> str | None:
    """Convert local number to +972 international format (digits only, E.164-compatible).

    Returns the strict E.164 form like '+972521234567'. For human-readable display,
    apply hyphenation downstream; do not pass the hyphenated form to strict parsers.
    """
    result = validate(phone)
    if not result["valid"] or result["type"] in ("toll_free", "premium", "star"):
        return None
    return "+972" + result["cleaned"][1:]


def to_e164(phone: str) -> str | None:
    """Alias for to_international(). Produces strict E.164 digits-only output.

    Compatible with WhatsApp Business API, Twilio, Vonage, AWS SNS, and
    google-libphonenumber / libphonenumber-js parsers.
    """
    return to_international(phone)


def to_local(phone: str) -> str:
    """Convert international format to local."""
    return clean_number(phone)


def main():
    parser = argparse.ArgumentParser(description="Israeli phone number validator")
    parser.add_argument("--number", "-n", help="Phone number to validate")
    parser.add_argument("--batch", action="store_true", help="Read numbers from stdin")
    parser.add_argument("--format", choices=["local", "international", "e164"], help="Convert to format")
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
            if "mnp_disclaimer" in result:
                print(f"Note: {result['mnp_disclaimer']}")
            if result.get("non_israeli"):
                print(f"Note: {result['note']}")
            if "region" in result:
                print(f"Region: {result['region']}")
            intl = to_international(args.number)
            if intl:
                print(f"E.164 (international): {intl}")
        else:
            print(f"Invalid: {result['cleaned']}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
