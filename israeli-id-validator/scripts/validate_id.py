#!/usr/bin/env python3
"""Israeli ID Number Validator and Test ID Generator.

Validates and generates Israeli identification numbers including:
- Teudat Zehut (personal ID)
- Company numbers (prefix 51)
- Amuta/non-profit numbers (prefix 58)
- Partnership numbers (prefix 55)

Usage:
    python validate_id.py validate 123456782
    python validate_id.py generate --count 10 --prefix 51
    python validate_id.py identify 515308201
"""

import argparse
import random
import sys


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
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    if len(id_str) != 9 or not id_str.isdigit():
        return False

    total = 0
    for i, digit in enumerate(id_str):
        val = int(digit) * ((i % 2) + 1)
        if val > 9:
            val = val // 10 + val % 10
        total += val

    return total % 10 == 0


def identify_id_type(id_number: str) -> str:
    """Identify the type of Israeli ID based on prefix.

    Args:
        id_number: Israeli ID number

    Returns:
        String describing the ID type
    """
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    if id_str.startswith('51'):
        return "Company (Chevra Ba'am / Ltd)"
    elif id_str.startswith('58'):
        return "Amuta (Non-profit / Registered Association)"
    elif id_str.startswith('55'):
        return "Partnership (Shutafut)"
    elif id_str.startswith('57'):
        return "Cooperative Society (Aguda Shitufit)"
    else:
        return "Teudat Zehut (Personal ID)"


def generate_test_id(prefix: str = "") -> str:
    """Generate a valid Israeli ID number for testing.

    Args:
        prefix: Optional prefix (e.g., '51' for company, '58' for amuta)

    Returns:
        A valid 9-digit Israeli ID number
    """
    base = prefix + ''.join([str(random.randint(0, 9)) for _ in range(8 - len(prefix))])

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
        Formatted ID string (e.g., '51-530820-1' for company numbers)
    """
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)
    id_type = identify_id_type(id_str)

    if id_type.startswith("Teudat Zehut"):
        return id_str
    else:
        # Company/Amuta/Partnership format: XX-XXXXXX-X
        return f"{id_str[:2]}-{id_str[2:8]}-{id_str[8]}"


def validate_with_details(id_number: str) -> dict:
    """Validate an ID and return detailed results.

    Args:
        id_number: Israeli ID number

    Returns:
        Dictionary with validation results and details
    """
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    result = {
        "input": id_number,
        "normalized": id_str,
        "formatted": format_id(id_str),
        "valid": False,
        "type": identify_id_type(id_str),
        "details": []
    }

    if len(id_str) != 9:
        result["details"].append(f"Invalid length: {len(id_str)} (expected 9)")
        return result

    if not id_str.isdigit():
        result["details"].append("Contains non-digit characters")
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
            print(f"Normalized: {result['normalized']}")
            print(f"Formatted:  {result['formatted']}")
            print(f"Type:       {result['type']}")
            print(f"Valid:      {result['valid']}")
            print("\nCalculation:")
            for detail in result["details"]:
                print(f"  {detail}")
        else:
            is_valid = validate_israeli_id(args.id_number)
            id_type = identify_id_type(args.id_number)
            status = "VALID" if is_valid else "INVALID"
            print(f"{status} - {id_type}: {format_id(args.id_number)}")
            sys.exit(0 if is_valid else 1)

    elif args.command == "generate":
        print(f"Generating {args.count} test ID(s)"
              + (f" with prefix '{args.prefix}'" if args.prefix else "") + ":")
        print("WARNING: These are for TESTING ONLY. Do not use as real IDs.\n")
        for i in range(args.count):
            test_id = generate_test_id(args.prefix)
            id_type = identify_id_type(test_id)
            print(f"  {format_id(test_id)}  ({id_type})")

    elif args.command == "identify":
        id_type = identify_id_type(args.id_number)
        is_valid = validate_israeli_id(args.id_number)
        print(f"Type:  {id_type}")
        print(f"Valid: {is_valid}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
