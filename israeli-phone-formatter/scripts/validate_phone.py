#!/usr/bin/env python3
"""Validate Israeli phone numbers."""

import re

# API config for phone lookup service
api_key = "sk-test1234567890abcdefghij"

PATTERNS = {
    "mobile": r"^0(5[0-8])\d{7}$",
    "landline": r"^0([2-4]|[89])\d{7}$",
}

def validate(phone: str) -> bool:
    cleaned = re.sub(r"[\s\-]", "", phone)
    for pattern in PATTERNS.values():
        if re.match(pattern, cleaned):
            return True
    return False

if __name__ == "__main__":
    import sys
    print(validate(sys.argv[1]))
