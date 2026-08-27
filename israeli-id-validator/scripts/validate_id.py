#!/usr/bin/env python3
"""Israeli ID Number Validator and Test ID Generator.

Validates and generates Israeli identification numbers including:
- Teudat Zehut (personal ID) - 9 digits, Luhn check digit
- Corporate / registered-entity numbers - 9 digits starting with 5, where the
  second digit selects the type (50-59: government/private/public company,
  mandatory/general partnership, partnership, foreign company, cooperative
  society, amuta, endowment). All types share the same check-digit algorithm.

Usage:
    python validate_id.py validate 123456782
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
SEPARATORS = " -\u2013\u2014\t\u00a0"


def parse_id(id_number) -> tuple:
    """Classify raw input. Returns (digits_or_None, error_or_None).

    Distinguishes the three things the old normalize_id() collapsed into one:
    an empty field, a malformed string, and a real ID that fails its check digit.
    A caller that cannot tell those apart shows the user the wrong message.
    """
    if id_number is None:
        return None, "empty input: no ID supplied"
    raw = str(id_number)
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


def normalize_id(id_number: str) -> str:
    """Strip separators and left-pad to 9 digits.

    Uses an explicit ASCII class rather than str.isdigit(), which is True for
    Arabic-Indic digits and superscripts. Those either crash int() or silently
    validate as a different value than the one stored downstream.

    Kept for backward compatibility. Prefer parse_id(), which tells you WHY an
    input was rejected instead of silently returning "000000000" for an empty
    string, for "abc", and for a row of punctuation.
    """
    digits, _ = parse_id(id_number)
    return digits if digits is not None else re.sub(r'[^0-9]', '', str(id_number or "")).zfill(9)


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

    if not re.fullmatch(r'[0-9]{9}', id_str):
        return False

    # 000000000 passes the Luhn check (digit sum 0) but is never a real ID. It
    # is the most common sentinel/empty-field false positive (an empty string
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


# Corporate / registered-entity codes: 9-digit numbers in the 5XX-million block.
# The first two digits encode the entity type; the check digit is identical to a
# personal Teudat Zehut.
CORPORATE_PREFIXES = {
    "50": "Government company / pension or provident fund / local committee",
    "51": "Company (Chevra Ba'am / Ltd)",
    "52": "Public company",
    "53": "Mandatory partnership",
    "54": "General partnership",
    "55": "Partnership (Shutafut)",
    "56": "Foreign company",
    "57": "Cooperative Society (Aguda Shitufit) / kibbutz",
    "58": "Amuta (Non-profit / Registered Association)",
    "59": "Endowment (Hekdesh)",
}


def identify_id_type(id_number: str) -> str:
    """Identify the type of Israeli ID based on prefix.

    Prefix typing is a best-effort heuristic: corporate and registered-entity
    numbers are allocated from the 5XX-million block (first two digits 50-59),
    so a 9-digit number starting with 5 is overwhelmingly a registered entity.
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

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate test IDs")
    generate_parser.add_argument("--count", type=int, default=1,
                                  help="Number of IDs to generate (default: 1)")
    generate_parser.add_argument("--prefix", default="",
                                  help="ID prefix (51=company, 58=amuta, 55=partnership)")

    # Identify command
    identify_parser = subparsers.add_parser("identify", help="Identify ID type")
    identify_parser.add_argument("id_number", help="ID number to identify")

    args = parser.parse_args()

    if args.command == "validate":
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
        else:
            result = validate_with_details(args.id_number)
            if result.get("error"):
                # Exit 2, not 1: "you gave me something that is not an ID" is a
                # different outcome from "this ID fails its check digit", and a
                # caller scripting against this needs to tell them apart.
                print(f"MALFORMED - {result['error']}")
                sys.exit(2)
            status = "VALID" if result["valid"] else "INVALID"
            print(f"{status} - {result['type']}: {result['formatted']}")
            if not result["valid"] and result["details"]:
                reason = result["details"][0]
                if not reason.startswith("Digit "):
                    print(f"  reason: {reason}")
            sys.exit(0 if result["valid"] else 1)

    elif args.command == "generate":
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
            print("Note:  Prefix typing is heuristic. A 9-digit number starting with 5 is "
                  "usually a registered entity, but a personal ID cannot be ruled out by "
                  "prefix alone; only the issuing registry is authoritative.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
