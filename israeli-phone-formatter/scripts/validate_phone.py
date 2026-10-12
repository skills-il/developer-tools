#!/usr/bin/env python3
"""Validate, format, and convert Israeli phone numbers.

Notes:
- "Valid" here means the number has the SHAPE of an allocated Israeli number
  class. It does not prove the sub-block is assigned, that the line is live, or
  that it reaches a person. M2M and Palestinian ranges are valid but flagged.
- Mobile Number Portability (MNP) began in Israel on 2 December 2007. The carrier
  inferred from the prefix is the *issuing* operator, not necessarily the current one.
- 056 (Ooredoo Palestine, formerly Wataniya) and 059 (Jawwal) are Palestinian
  operators, as are the landline blocks 02-2, 04-2, 08-2 and 09-2.
- 1-700 is a shared-cost number (caller billed as a local call), NOT premium
  rate. Premium rate is 1-900 / 1-901 / 1-902 / 1-919.
- 070, 071, 075 and 078 have no allocation in the MoC table; the pattern rejects them.
- to_e164() produces the canonical digits-only form like '+972523456789'. Store that.
- Input normalisation accepts what real forms and spreadsheets produce: bidi marks,
  Unicode dashes, Arabic-Indic and full-width digits, '+972 (0)' and '+9720',
  surrounding text such as 'Tel:' or 'ext 12', and a leading zero lost in Excel
  (bare digit cells only). Scientific-notation cells are rejected as unrecoverable.
"""

import argparse
import csv
import re
import sys
import unicodedata

PATTERNS = {
    # Mobile: 10 digits, 05R-NXX-XXXX. 050-056, 058, 059 (057 unallocated; 056 / 059 Palestinian, flagged)
    "mobile": r"^05[0-689]\d{7}$",
    # Landline: 9 digits, 0A-NXX-XXXX with A in 2, 3, 4, 8, 9 and N = 2-9
    "landline": r"^0[2-489][2-9]\d{6}$",
    # National (non-geographic) numbers: 10 digits, 07P-NXX-XXXX with N = 2-9.
    # Allocated P values per the MoC table: 072, 073, 074, 076, 077, 079.
    "national": r"^07[2-46-79][2-9]\d{6}$",
    # Toll-free: 1-800, 1-801, and 1-809 (toll-free for international operators)
    "toll_free": r"^180[019]\d{6}$",
    # Shared-cost: 1-700 (local call, split charging)
    "shared_cost": r"^1700\d{6}$",
    # Business call router: 1-599
    "business": r"^1599\d{6}$",
    # Premium rate: 1-900, 1-901, 1-902, and 1-919 (adult services)
    "premium": r"^19(0[0-2]|19)\d{6}$",
    # Other paid voice services: 1-956 entertainment, 1-957 information, 1-200 remote voting, 1-212 polls
    "other_service": r"^1(95[67]|200|212)\d{6}$",
    # Business star numbers: * plus four digits (1222 replaces the star on phones without one)
    "star": r"^(\*|1222)\d{4}$",
    # Emergency and public-service short codes (curated subset, see SHORT_CODE_MAP)
    "short_code": r"^(10[0-6]|110|11[589])$",
}

# Types that are domestic-only: no +972 form is produced for them.
DOMESTIC_ONLY = {"toll_free", "shared_cost", "business", "premium", "other_service", "star", "short_code"}

# Holder of the MAIN ranges of each mobile prefix per the MoC allocation table.
# Subject to MNP -- treat as the issuing operator only.
CARRIER_MAP = {
    "050": "Pelephone",
    "051": "WeCom Mobile",
    "052": "Cellcom",
    "053": "Hot Mobile",
    "054": "Partner Communications",
    "055": "Multi-operator range (sub-blocks held by different MVNOs and operators)",
    "056": "Palestinian operators (Ooredoo Palestine, formerly Wataniya)",
    "058": "Cellcom (originally Golan Telecom's range)",
    "059": "Jawwal (Palestinian operator)",
}

# Prefixes that match the Israeli mobile shape but belong to Palestinian carriers.
NON_ISRAELI_MOBILE_PREFIXES = {"056", "059"}

AREA_MAP = {
    "02": "Jerusalem",
    "03": "Tel Aviv",
    "04": "Haifa and the North",
    "08": "Shfela and the South",
    "09": "Sharon",
}

NATIONAL_CARRIER_MAP = {
    "072": "Partner (main ranges); other operators hold small blocks",
    "073": "Cellcom (main ranges); many smaller operators hold 073-8 blocks",
    "074": "Partner",
    "076": "Bezeq International (076-5) / Bezeq (076-8)",
    "077": "Hot Telecom",
    "079": "Several operators (Widely, Binat, Hallo 015, Cellact, Annatel, 019 Telzar)",
}

SHORT_CODE_MAP = {
    "100": "Police",
    "101": "Magen David Adom (ambulance)",
    "102": "Fire and Rescue",
    "103": "Israel Electric Corporation",
    "104": "Home Front Command",
    "105": "National Child Online Protection center",
    "106": "Municipal call center",
    "110": "Israel Police national information center",
    "115": "Israel Police national disaster center",
    "118": "National welfare emergency center",
    "119": "National Cyber Directorate",
}

# Arabic-Indic and Extended Arabic-Indic digits -> ASCII. Full-width digits are handled by NFKC.
_DIGIT_MAP = {ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")}
_DIGIT_MAP.update({ord(c): str(i) for i, c in enumerate("۰۱۲۳۴۵۶۷۸۹")})


_RUN = re.compile(r"[+*]?\d[\d \t\u00a0\-\u2010-\u2015\u2212./()]*\d|[+*]?\d")


def _canonical_chars(phone: str) -> tuple[str, int]:
    """Pick the longest phone-shaped run, then keep only digits plus a leading '+' or '*'.

    Handles bidi marks, Unicode dashes, Arabic-Indic / full-width digits, and labels
    such as 'Tel:' or 'Mobile 2:' or a trailing 'ext 12'. Also returns how many
    runs look like a whole phone number (7+ digits), to flag cells holding two numbers.
    """
    s = unicodedata.normalize("NFKC", phone).translate(_DIGIT_MAP)
    s = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]", "", s)
    s = s.replace("(0)", "")  # '+972 (0)52...' trunk-zero notation
    runs = _RUN.findall(s)
    if not runs:
        return "", 0
    phone_like = sum(1 for r in runs if len(re.sub(r"\D", "", r)) >= 7)
    best = max(runs, key=lambda r: len(re.sub(r"\D", "", r)))
    lead = best[0] if best[0] in "+*" else ""
    return lead + re.sub(r"\D", "", best), phone_like


def clean_number(phone: str) -> tuple[str, list[str]]:
    """Normalise to local form with leading 0. Returns (cleaned, notes).

    A note starting with UNRECOVERABLE or FOREIGN means the number must be rejected.
    """
    notes = []
    raw = phone.strip()
    if re.fullmatch(r"[+-]?\d+([.,]\d+)?[eE][+-]?\d+", raw):
        notes.append("UNRECOVERABLE: scientific notation, the spreadsheet already lost digits")
        return raw, notes
    s, phone_like = _canonical_chars(raw)
    if phone_like > 1:
        notes.append("MULTIPLE_NUMBERS: the cell holds more than one number; only the longest was kept")
    if s.startswith("+"):
        if not s.startswith("+972"):
            notes.append("FOREIGN: country code is not +972")
            return s, notes
        s = "0" + s[4:]
    elif s.startswith("00972"):
        s = "0" + s[5:]
    elif s.startswith("00") and len(s) > 4:
        notes.append("FOREIGN: international prefix 00 with a country code other than 972")
        return s, notes
    elif s.startswith("972") and len(s) > 9:
        s = "0" + s[3:]
    if s.startswith("00") and len(s) in (10, 11):  # '+9720...' -> '00...' after stripping the code
        s = s[1:]
    # A lost leading zero is only restored for a bare digit cell (the Excel case), never for
    # text that merely contains digits (dates, amounts, references).
    if re.fullmatch(r"\d+", re.sub(r"\s", "", raw)) and re.fullmatch(r"[57]\d{8}|[23489][2-9]\d{6}", s):
        s = "0" + s
        notes.append("LEADING_ZERO_RESTORED: probably lost its leading 0 (typical of Excel); confirm")
    elif re.fullmatch(r"[2-9]\d{6}", s):
        notes.append("LOCAL_7_DIGITS: a landline dialed without its area code; ask for the area code")
    return s, notes


def validate(phone: str) -> dict:
    """Validate an Israeli phone number and return its type and details."""
    cleaned, notes = clean_number(phone)
    if any(n.startswith(("UNRECOVERABLE", "FOREIGN")) for n in notes):
        return {"valid": False, "type": None, "cleaned": cleaned, "notes": notes}
    if cleaned.startswith("1222") and len(cleaned) == 8:
        cleaned = "*" + cleaned[4:]
    for phone_type, pattern in PATTERNS.items():
        if re.match(pattern, cleaned):
            result = {"valid": True, "type": phone_type, "cleaned": cleaned, "notes": notes}
            prefix = cleaned[:3]
            if phone_type == "mobile":
                result["carrier"] = CARRIER_MAP[prefix]
                result["mnp_disclaimer"] = (
                    "Issuing carrier only; live carrier may differ due to MNP (since 2 Dec 2007)."
                )
                if prefix in NON_ISRAELI_MOBILE_PREFIXES:
                    result["non_israeli"] = True
                    result["note"] = "Palestinian operator; not an Israeli consumer mobile number."
                elif cleaned[3] in "01":
                    result["m2m"] = True
                    result["m2m_note"] = (
                        "05X-0 / 05X-1 subscriber numbers are reserved for M2M / IoT SIMs, not people."
                    )
            elif phone_type == "national":
                result["carrier"] = NATIONAL_CARRIER_MAP[prefix]
            elif phone_type == "landline":
                result["region"] = AREA_MAP[cleaned[:2]]
                if cleaned[2] == "2" and cleaned[1] in "2489":
                    result["non_israeli"] = True
                    result["note"] = "0A-2XXXXXX is allocated to Palestinian operators."
            elif phone_type == "short_code":
                result["service"] = SHORT_CODE_MAP[cleaned]
            return result
    return {"valid": False, "type": None, "cleaned": cleaned, "notes": notes}


def to_international(phone: str) -> str | None:
    """Convert to +972 international format (digits only, E.164).

    Returns the canonical form like '+972523456789', or None for invalid and
    domestic-only numbers. Store this form; render hyphens only for display.
    """
    result = validate(phone)
    if not result["valid"] or result["type"] in DOMESTIC_ONLY:
        return None
    return "+972" + result["cleaned"][1:]


def to_e164(phone: str) -> str | None:
    """Alias for to_international(). Digits-only E.164 such as '+972523456789'."""
    return to_international(phone)


def to_local(phone: str) -> str:
    """Convert international format to local (digits only, leading 0)."""
    return clean_number(phone)[0]


def to_display(phone: str) -> str | None:
    """Hyphenated local display form, e.g. 052-3456789, 02-6251111, 1-800-123456."""
    result = validate(phone)
    if not result["valid"]:
        return None
    c = result["cleaned"]
    if result["type"] in ("mobile", "national"):
        return f"{c[:3]}-{c[3:]}"
    if result["type"] == "landline":
        return f"{c[:2]}-{c[2:]}"
    if result["type"] in ("toll_free", "shared_cost", "business", "premium", "other_service"):
        return f"{c[0]}-{c[1:4]}-{c[4:]}"
    return c


def convert(phone: str, fmt: str) -> str | None:
    """'local' gives the hyphenated display form; 'international' / 'e164' give E.164."""
    if fmt == "local":
        return to_display(phone)
    return to_e164(phone)


def iter_input_numbers(path: str | None, column: int):
    """Yield raw numbers from a CSV file (comma, semicolon or tab separated) or stdin.

    `column` is 1-based. A first row whose chosen cell holds no digit is a header and is skipped.
    """
    stream = open(path, newline="", encoding="utf-8-sig") if path else sys.stdin
    try:
        sample = stream.read(4096)
        rest = stream.read()
        text = sample + rest
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        except csv.Error:
            dialect = csv.excel
        for i, row in enumerate(csv.reader(text.splitlines(), dialect)):
            cell = row[column - 1].strip() if len(row) >= column else ""
            if not cell or (i == 0 and not re.search(r"\d", cell)):
                continue
            yield cell
    finally:
        if path:
            stream.close()


def main():
    parser = argparse.ArgumentParser(description="Israeli phone number validator")
    parser.add_argument("--number", "-n", help="Phone number to validate")
    parser.add_argument("--batch", action="store_true",
                        help="Validate many numbers: one per line on stdin, or a column of --input")
    parser.add_argument("--input", "-i", help="CSV file for --batch (comma, semicolon or tab separated)")
    parser.add_argument("--column", "-c", type=int, default=1, help="1-based CSV column holding the number")
    parser.add_argument("--format", choices=["local", "international", "e164"],
                        help="With --number, print only the converted number")
    args = parser.parse_args()
    if args.column < 1:
        parser.error("--column is 1-based and must be >= 1")

    if args.batch:
        valid = invalid = dupes = 0
        seen = set()
        print("input\tstatus\ttype\te164\tnote")
        for phone in iter_input_numbers(args.input, args.column):
            result = validate(phone)
            if result["valid"]:
                valid += 1
            else:
                invalid += 1
            flags = [n.split(":")[0] for n in result["notes"]]
            if result.get("non_israeli"):
                flags.append("PALESTINIAN_CARRIER")
            if result.get("m2m"):
                flags.append("M2M_RANGE")
            if result["valid"] and result["type"] in DOMESTIC_ONLY:
                flags.append("DOMESTIC_ONLY")
            if result["valid"]:
                if result["cleaned"] in seen:
                    flags.append("DUPLICATE")
                    dupes += 1
                seen.add(result["cleaned"])
            restored = any(n.startswith("LEADING_ZERO_RESTORED") for n in result["notes"])
            status = ("VALID_CONFIRM" if restored else "VALID") if result["valid"] else "INVALID"
            print(f"{phone}\t{status}\t"
                  f"{result['type'] or 'unknown'}\t{to_e164(phone) or ''}\t{','.join(flags)}")
        print(f"# valid={valid} invalid={invalid} duplicates={dupes}", file=sys.stderr)
        if valid + invalid == 0:
            print(f"# no rows had a value in column {args.column}", file=sys.stderr)
            sys.exit(2)
        sys.exit(1 if invalid else 0)
    elif args.number:
        result = validate(args.number)
        if not result["valid"]:
            print(f"Invalid: {result['cleaned']}")
            for n in result["notes"]:
                print(f"Note: {n}")
            sys.exit(1)
        if args.format:
            out = convert(args.number, args.format)
            if out is None:
                print(f"No {args.format} form: {result['type']} numbers are domestic-only")
                sys.exit(1)
            print(out)
            return
        restored = any(n.startswith("LEADING_ZERO_RESTORED") for n in result["notes"])
        print(f"Valid{' (needs confirmation)' if restored else ''}: {result['type']}")
        print(f"Cleaned: {result['cleaned']}")
        for key, label in (("carrier", "Carrier"), ("mnp_disclaimer", "Note"), ("note", "Note"),
                           ("m2m_note", "Note"), ("region", "Region"), ("service", "Service")):
            if key in result:
                print(f"{label}: {result[key]}")
        for n in result["notes"]:
            print(f"Note: {n}")
        intl = to_international(args.number)
        print(f"E.164 (international): {intl}" if intl else "E.164: none (domestic-only number)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
