#!/usr/bin/env python3
"""Israeli ID Number Validator and Test ID Generator.

Validates and generates Israeli identification numbers including:
- Teudat Zehut (personal ID) - 9 digits, Luhn check digit
- Corporate / registered-entity numbers - 9 digits that usually begin with 5,
  where the first two digits usually relate to the type (50-59: government/private/public company,
  Mandate-era/general partnership, partnership, foreign company, cooperative
  society, amuta, endowment). All types share the same check-digit algorithm.

Usage:
    python validate_id.py validate 123456782
    python validate_id.py validate 123456782 --mask     # prints xxxxx6782
    python validate_id.py generate --count 10 --prefix 51
    python validate_id.py identify 515308203
"""

import argparse
import random
import re
import sys


# Characters a human or a spreadsheet legitimately puts INSIDE an ID for legibility.
# Anything else is garbage and must be reported, not silently deleted: stripping
# every non-digit turns "62819482.1" into a VALID teudat zehut, which is worse than
# rejecting it, because the caller never learns the input was malformed.
# Soft hyphen, zero-width space/joiners, word joiner and the BOM are ignored by the bidi algorithm, so they
# cannot change the order in which digits are displayed and are safe to drop too.
SEPARATORS = " -\u2010\u2011\u2013\u2014\u202f\u00a0\u00ad\u200b\u200c\u200d\u2060\ufeff"

# Characters trimmed from the ENDS only: whitespace (including tab), a CSV line
# break, the BOM, and
# the LRM/RLM/ALM marks a Hebrew page or WhatsApp puts around a pasted number.
# Inside the number they stay errors: an interior line break joins two fragments
# into one "ID" (so does a tab, which is a TSV cell boundary), and an interior bidi mark can make the screen show a different
# digit order than the one stored. Bidi overrides and isolates (U+202A-E,
# U+2066-9) are never discarded: "\u202e287654321" displays as 123456782.
EDGE = " \t\u00a0\r\n\u200b\ufeff\u200e\u200f\u061c"


def parse_id(id_number) -> tuple:
    """Classify raw input. Returns (digits_or_None, error_or_None).

    Distinguishes the three things the old normalize_id() collapsed into one:
    an empty field, a malformed string, and a real ID that fails its check digit.
    A caller that cannot tell those apart shows the user the wrong message.
    """
    if id_number is None:
        return None, "empty input: no ID supplied"
    if not isinstance(id_number, str):
        # An int has already lost its leading zeros, so 12345674 would silently
        # become 012345674. Make the caller keep IDs as text end to end.
        return None, f"not a string ({type(id_number).__name__}): pass the ID as text"
    raw = id_number.strip(EDGE)
    if raw.strip() == "":
        return None, "empty input: no ID supplied"

    # Only the documented separators may be discarded.
    stripped = "".join(c for c in raw if c not in SEPARATORS)
    bad = sorted({c for c in stripped if not ("0" <= c <= "9")})
    if bad:
        return None, ("contains characters that are not digits or separators: "
                      + " ".join(repr(c) for c in bad))
    if stripped == "":
        return None, "empty input: separators only, no digits"
    if len(stripped) > 9:
        return None, f"too long: {len(stripped)} digits (an Israeli ID is at most 9)"
    return stripped.zfill(9), None


def normalize_id(id_number: str):
    """Strip separators and left-pad to 9 digits, or return None if malformed.

    Kept for backward compatibility. Prefer parse_id(), which also tells you WHY
    an input was rejected.

    It used to fall back to re.sub(r'[^0-9]', '', ...) for malformed input, which
    meant validate_israeli_id("62819482.1") still returned True through this
    helper even after the CLI had been fixed. Malformed input now yields None,
    never a digit string, so no caller can validate garbage by accident.
    """
    digits, _ = parse_id(id_number)
    return digits


def mask_id(id_str: str) -> str:
    """Mask all but the last 4 characters, e.g. '123456782' -> 'xxxxx6782'."""
    return "x" * max(len(id_str) - 4, 0) + id_str[-4:]


def validate_israeli_id(id_number: str) -> bool:
    """Validate Israeli ID number using the check digit algorithm.

    The algorithm:
    1. Pad to 9 digits with leading zeros
    2. Multiply each digit alternately by 1, 2, 1, 2, ...
    3. If product > 9, sum the digits of the product
    4. Sum all results
    5. Valid if total is divisible by 10

    Args:
        id_number: Israeli ID number (with or without dashes/spaces)

    Returns:
        True if the ID number is valid, False otherwise
    """
    id_str = normalize_id(id_number)

    if id_str is None or not re.fullmatch(r'[0-9]{9}', id_str):
        return False        # malformed input, NOT an invalid ID

    # 000000000 passes the Luhn check (digit sum 0) but is never a real ID. It
    # is a common sentinel/empty-field false positive (an empty string
    # zero-pads straight into it), so reject it explicitly.
    if id_str == '000000000':
        return False

    total = 0
    for i, digit in enumerate(id_str):
        val = int(digit) * ((i % 2) + 1)
        if val > 9:
            val = val // 10 + val % 10
        total += val

    return total % 10 == 0


# Corporate / registered-entity codes. The first two digits USUALLY relate to the
# entity type (the source says "usually"), so this is a likely label, never a rule;
# the check digit is identical to a personal Teudat Zehut.
CORPORATE_PREFIXES = {
    "50": "Government company / pension or provident fund / local committee",
    "51": "Company (Chevra Ba'am / Ltd)",
    "52": "Public company",
    "53": "Mandate-era partnership (Shutafut Mandatorit)",
    "54": "General partnership",
    "55": "Partnership (Shutafut)",
    "56": "Foreign company",
    "57": "Cooperative Society (Aguda Shitufit) / kibbutz",
    "58": "Amuta (Non-profit / Registered Association)",
    "59": "Endowment (Hekdesh), not itself a corporation",
}


PREFIX_CAVEAT = ("Note:  Prefix typing is heuristic. A 9-digit number starting with 5 is "
                 "usually a registered entity, but a personal ID cannot be ruled out by "
                 "prefix alone; only the issuing registry is authoritative.")


def identify_id_type(id_number: str) -> str:
    """Identify the type of Israeli ID based on prefix.

    Prefix typing is a best-effort heuristic: the first two digits of a
    registered-entity number usually relate to its type (codes 50-59), so a
    9-digit number starting with 5 is usually a registered entity.
    A personal Teudat Zehut cannot be reliably typed from its prefix; only the
    issuing registry is authoritative.

    Args:
        id_number: Israeli ID number

    Returns:
        String describing the ID type
    """
    digits, error = parse_id(id_number)
    if error is not None:
        return "Unrecognised (not a well-formed Israeli ID)"
    return CORPORATE_PREFIXES.get(digits[:2], "Teudat Zehut (Personal ID)")


def generate_test_id(prefix: str = "") -> str:
    """Generate a valid Israeli ID number for testing.

    Args:
        prefix: Optional prefix (e.g., '51' for company, '58' for amuta)

    Returns:
        A valid 9-digit Israeli ID number
    """
    if not re.fullmatch(r'[0-9]{0,8}', prefix):
        raise ValueError("prefix must be 0-8 ASCII digits")
    if prefix == '00000000':
        # The only completion is 000000000, which validation rejects; without
        # this guard the re-roll loop below never terminates.
        raise ValueError("an all-zeros prefix can only yield 000000000")

    while True:
        base = prefix + ''.join(
            [str(random.randint(0, 9)) for _ in range(8 - len(prefix))]
        )
        if base != '00000000':
            break

    total = 0
    for i, digit in enumerate(base):
        val = int(digit) * ((i % 2) + 1)
        if val > 9:
            val = val // 10 + val % 10
        total += val

    check = (10 - (total % 10)) % 10
    return base + str(check)


def format_id(id_number: str) -> str:
    """Format an Israeli ID number with standard dashes.

    Args:
        id_number: Raw ID number

    Returns:
        Formatted ID string (e.g., '51-530820-3' for company numbers)
    """
    id_str = normalize_id(id_number)
    if id_str is None:
        return str(id_number)   # malformed: never invent a formatted ID
    id_type = identify_id_type(id_str)

    if id_type.startswith("Teudat Zehut"):
        return id_str
    else:
        # Registered-entity display format XX-XXXXXX-X, applied to 5X-prefixed
        # numbers. This is the heuristic corporate grouping (see identify_id_type);
        # a personal ID starting with 5 would also be grouped this way.
        return f"{id_str[:2]}-{id_str[2:8]}-{id_str[8]}"


def validate_with_details(id_number: str) -> dict:
    """Validate an ID and return detailed results.

    Args:
        id_number: Israeli ID number

    Returns:
        Dictionary with validation results and details
    """
    digits, error = parse_id(id_number)

    if error is not None:
        return {
            "input": id_number,
            "normalized": None,
            "formatted": None,
            "valid": False,
            "type": "Unrecognised (not a well-formed Israeli ID)",
            "error": error,
            "details": [f"Malformed input: {error}"],
        }

    id_str = digits
    result = {
        "input": id_number,
        "normalized": id_str,
        "formatted": format_id(id_str),
        "valid": False,
        "type": identify_id_type(id_str),
        "error": None,
        "details": []
    }

    if id_str == "000000000":
        result["details"].append("Placeholder ID (all zeros): passes Luhn but is never a real ID")
        return result

    # Show step-by-step calculation
    multipliers = []
    products = []
    total = 0
    for i, digit in enumerate(id_str):
        mult = (i % 2) + 1
        val = int(digit) * mult
        original_val = val
        if val > 9:
            val = val // 10 + val % 10
        multipliers.append(mult)
        products.append(val)
        total += val
        result["details"].append(
            f"Digit {i+1}: {digit} x {mult} = {original_val}"
            + (f" -> {val}" if original_val != val else "")
        )

    result["details"].append(f"Sum: {total}")
    result["details"].append(f"Divisible by 10: {total % 10 == 0}")
    result["valid"] = total % 10 == 0

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Israeli ID Number Validator and Generator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an Israeli ID")
    validate_parser.add_argument("id_number", help="ID number to validate")
    validate_parser.add_argument("-v", "--verbose", action="store_true",
                                 help="Show step-by-step calculation")
    validate_parser.add_argument("--mask", action="store_true",
                                 help="Print only the last 4 digits (for logs and CI output)")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate test IDs")
    generate_parser.add_argument("--count", type=int, default=1,
                                  help="Number of IDs to generate (default: 1)")
    generate_parser.add_argument("--prefix", default="",
                                  help="ID prefix (51=company, 58=amuta, 55=partnership)")

    # Identify command
    identify_parser = subparsers.add_parser("identify", help="Identify ID type")
    identify_parser.add_argument("id_number", help="ID number to identify")
    identify_parser.add_argument("--mask", action="store_true",
                                 help="Accepted for symmetry; identify never prints the ID")

    args = parser.parse_args()

    if args.command == "validate":
        if args.verbose and args.mask:
            parser.error("--verbose prints every digit, so it cannot be combined with --mask")
        if args.verbose:
            result = validate_with_details(args.id_number)
            print(f"Input:      {result['input']}")
            if result.get("error"):
                print(f"Type:       {result['type']}")
                print(f"Valid:      False")
                print(f"Error:      {result['error']}")
                sys.exit(2)
            print(f"Normalized: {result['normalized']}")
            print(f"Formatted:  {result['formatted']}")
            print(f"Type:       {result['type']}")
            print(f"Valid:      {result['valid']}")
            print("\nCalculation:")
            for detail in result["details"]:
                print(f"  {detail}")
            # Same exit-code contract as the plain path: 0 valid, 1 check digit.
            sys.exit(0 if result["valid"] else 1)
        else:
            result = validate_with_details(args.id_number)
            if result.get("error"):
                # Exit 2, not 1: "you gave me something that is not an ID" is a
                # different outcome from "this ID fails its check digit", and a
                # caller scripting against this needs to tell them apart.
                print(f"MALFORMED - {result['error']}")
                sys.exit(2)
            status = "VALID" if result["valid"] else "INVALID"
            shown = mask_id(result["normalized"]) if args.mask else result["formatted"]
            print(f"{status} - {result['type']}: {shown}")
            if not result["valid"] and result["details"]:
                reason = result["details"][0]
                if not reason.startswith("Digit "):
                    print(f"  reason: {reason}")
            if result["normalized"][:2] in CORPORATE_PREFIXES:
                print(PREFIX_CAVEAT)
            sys.exit(0 if result["valid"] else 1)

    elif args.command == "generate":
        try:
            generate_test_id(args.prefix)
        except ValueError as e:
            parser.error(f"--prefix: {e}")
        print(f"Generating {args.count} test ID(s)"
              + (f" with prefix '{args.prefix}'" if args.prefix else "") + ":")
        print("WARNING: These are for TESTING ONLY. Do not use as real IDs.\n")
        for i in range(args.count):
            test_id = generate_test_id(args.prefix)
            id_type = identify_id_type(test_id)
            print(f"  {format_id(test_id)}  ({id_type})")

    elif args.command == "identify":
        digits, err = parse_id(args.id_number)
        id_type = identify_id_type(args.id_number)
        is_valid = validate_israeli_id(args.id_number)
        print(f"Type:  {id_type}")
        print(f"Valid: {is_valid}")
        if err is not None:
            print(f"Error: {err}")
            sys.exit(2)
        norm = digits
        if norm[:2] in CORPORATE_PREFIXES:
            print(PREFIX_CAVEAT)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
