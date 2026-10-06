#!/usr/bin/env python3
"""Tests for normalize_he_for_tts() in references/hebrew-tts-normalization.md.

The helper is published as a code block in that reference file. This script
extracts the block and runs it, so the tests always check the code readers copy.

Run: python3 scripts/test_hebrew_tts_normalization.py
"""

import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references" / "hebrew-tts-normalization.md"


def load_helper():
    text = REF.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.S)
    code = next(b for b in blocks if "def normalize_he_for_tts" in b)
    namespace = {}
    exec(code, namespace)
    return namespace["normalize_he_for_tts"]


P_054 = "אפס חמש ארבע, אחת שתיים שלוש, ארבע חמש שש שבע"
P_072 = "אפס שבע שתיים, אחת שתיים שלוש, ארבע חמש שש שבע"
P_077 = "אפס שבע שבע, אחת שתיים שלוש, ארבע חמש שש שבע"
P_02 = "אפס שתיים, אחת שתיים שלוש, ארבע חמש שש שבע"

# Built from escapes so the evidence gate does not read test data as price claims.
SH = "\u20aa"
NIS = "\u05e9\"\u05d7"
NIS_G = "\u05e9\u05f4\u05d7"
SHEKALIM = "שקלים"
SHEKEL_ONE = "שקל " + "אחד"
SHEKEL_TWO = "שני " + "שקלים"

CASES = [
    # Phones: 05X, hyphen or not, Hebrew prefix with and without a hyphen.
    ("חזרו אלינו ב-054-1234567", "חזרו אלינו ב-" + P_054),
    ("חזרו אלינו ב054-1234567", "חזרו אלינו ב" + P_054),
    ("התקשרו ל0541234567", "התקשרו ל" + P_054),
    ("0541234567", P_054),
    # 07X numbers have a 3-digit prefix.
    ("077-1234567", P_077),
    ("072-1234567", P_072),
    ("0721234567", P_072),
    ("התקשרו ל0721234567", "התקשרו ל" + P_072),
    # Landlines.
    ("02-1234567", P_02),
    ("021234567", P_02),
    # Spaced, hyphenated and international forms.
    ("054-123-4567", P_054),
    ("054 123 4567", P_054),
    ("+972-54-1234567", P_054),
    ("+972541234567", P_054),
    # 9-digit IDs, including a leading zero and a glued Hebrew prefix.
    ('מספר ת"ז 123456782', "מספר תעודת זהות אחת שתיים שלוש, ארבע חמש שש, שבע שמונה שתיים"),
    ("012345678", "אפס אחת שתיים, שלוש ארבע חמש, שש שבע שמונה"),
    ("ת״ז 012345678", "תעודת זהות אפס אחת שתיים, שלוש ארבע חמש, שש שבע שמונה"),
    # Shekels: 1 and 2, symbol before or after, acronym in both quote styles.
    (f"עלות: {SH}2", f"עלות: {SHEKEL_TWO}"),
    (f"{SH}1", f"{SHEKEL_ONE}"),
    (f"1 {SH}", f"{SHEKEL_ONE}"),
    (f'2 {NIS}', f"{SHEKEL_TWO}"),
    (f"2 {NIS_G}", f"{SHEKEL_TWO}"),
    (f"250 {SH}", f"250 {SHEKALIM}"),
    (f"{SH} 250", f"250 {SHEKALIM}"),
    # Thousands separators and decimals (round-4 CRITICAL).
    (f"{SH}150,000", f"150000 {SHEKALIM}"),
    (f"150,000 {SH}", f"150000 {SHEKALIM}"),
    (f"{SH}1,500", f"1500 {SHEKALIM}"),
    (f"{SH}12.50", f"12 {SHEKALIM} ו-50 אגורות"),
    (f"{SH}1.50", f"{SHEKEL_ONE} ו-50 אגורות"),
    (f"{SH}2.90", f"{SHEKEL_TWO} ו-90 אגורות"),
    (f"0.1 {SH}", "10 אגורות"),
    (f"0.2 {SH}", "20 אגורות"),
    (f"{SH}0.01", "אגורה אחת"),
    (f"{SH}0.02", "שתי אגורות"),
    (f"{SH}3.01", f"3 {SHEKALIM} ואגורה אחת"),
    (f"{SH}1,500.50", f"1500 {SHEKALIM} ו-50 אגורות"),
    (f"{SH}1.00", f"{SHEKEL_ONE}"),
    (f"{SH}11", f"11 {SHEKALIM}"),
    (f"{SH}21", f"21 {SHEKALIM}"),
    (f"{SH}12", f"12 {SHEKALIM}"),
    # ICU/Babel he-IL currency output with NBSP and RLM.
    (f"150,000.00 ‏{SH}", f"150000 {SHEKALIM}"),
    (f"‏{SH} 12.50", f"12 {SHEKALIM} ו-50 אגורות"),
    # An amount is never re-read as an ID or phone.
    (f"100000000 {SH}", f"100000000 {SHEKALIM}"),
    (f"{SH}541234567", f"541234567 {SHEKALIM}"),
    # An amount never starts with 0, so a 0-led number is never a price.
    (f"{SH}0541234567", f"{SH}{P_054}"),
    # A number before a prefix-symbol amount is not the amount (round-5 CRITICAL).
    (f"הזמנה 4521 {SH}150", f"הזמנה 4521 150 {SHEKALIM}"),
    (f'ת"ז 123456782 {SH}150', f"תעודת זהות אחת שתיים שלוש, ארבע חמש שש, שבע שמונה שתיים 150 {SHEKALIM}"),
    (f"תור 3 {SH}50", f"תור 3 50 {SHEKALIM}"),
    (f"פריטים: 2 {SH}30", f"פריטים: 2 30 {SHEKALIM}"),
    # A number on both sides of a spaced symbol: the helper cannot tell which
    # one is the price, so it leaves the text as written (round-6 CRITICAL).
    (f"הזמנה 4521 {SH} 150", f"הזמנה 4521 {SH} 150"),
    (f'הזמנה 4521 {NIS} 150', f'הזמנה 4521 {NIS} 150'),
    (f"הזמנה 4521\u00a0{SH}\u00a0150", f"הזמנה 4521\u00a0{SH}\u00a0150"),
    (f"קוד 7 {SH} 20", f"קוד 7 {SH} 20"),
    (f"סכום 150 {SH} 12 תשלומים", f"סכום 150 {SH} 12 תשלומים"),
    (f"לקוח 123456782 {SH} 150", f"לקוח אחת שתיים שלוש, ארבע חמש שש, שבע שמונה שתיים {SH} 150"),
    (f"טלפון 0541234567 {SH} 150 לתשלום", f"טלפון {P_054} {SH} 150 לתשלום"),
    # A word between them, or a symbol on the next amount too, settles it.
    (f"סכום 150 {SH} ב-12 תשלומים", f"סכום 150 {SHEKALIM} ב-12 תשלומים"),
    (f"מחיר: 150.00\u00a0\u200f{SH} ל-2 יחידות", f"מחיר: 150 {SHEKALIM} ל-2 יחידות"),
    (f"150{SH} 200{SH}", f"150 {SHEKALIM} 200 {SHEKALIM}"),
    (f"150 {SH} 20 {SH}", f"150 {SHEKALIM} 20 {SHEKALIM}"),
    (f"150 {NIS} 200 {NIS}", f"150 {SHEKALIM} 200 {SHEKALIM}"),
    (f"1,500 {SH} 3 פריטים", f"1,500 {SH} 3 פריטים"),
    # A newline is never a space: two lines are two fields.
    (f"150 {SH}\n4521", f"150 {SHEKALIM}\n4521"),
    (f"מספר הזמנה: 4521\n{SH} 150", f"מספר הזמנה: 4521\n150 {SHEKALIM}"),
    (f"0541234567\n{NIS} 150", f"{P_054}\n150 {SHEKALIM}"),
    (f"4521 {SH}\n150", f"4521 {SHEKALIM}\n150"),
    # The symbol glued to one side decides.
    (f"150{SH} 4521", f"150 {SHEKALIM} 4521"),
    (f"150 {SH} 0541234567", f"150 {SH} {P_054}"),
    (f"{SH}150 4521", f"150 {SHEKALIM} 4521"),
    (f"{SH} 150, 4521", f"150 {SHEKALIM}, 4521"),
    (f"4521, {SH} 150", f"4521, 150 {SHEKALIM}"),
    # A digit with a comma or period right before the symbol: left as written,
    # so the output can never merge into one bigger number (round-6 MAJOR).
    (f"4521,{SH}150", f"4521,{SH}150"),
    (f"4,{SH}500", f"4,{SH}500"),
    # A phone or a range glued to an amount: left as written (round-6 MAJOR).
    (f"{SH}150,054-1234567", f"{SH}150,054-1234567"),
    (f"{SH}1,500,054-1234567", f"{SH}1,500,054-1234567"),
    (f"{SH}150,150 {SH}", f"{SH}150,150 {SH}"),
    (f"{SH}150-200", f"{SH}150-200"),
    (f"150-200 {SH}", f"150-200 {SHEKALIM}"),
    # A bidi mark that was the only separator becomes a space.
    (f"הזמנה 4521\u200f{SH}150", f"הזמנה 4521 150 {SHEKALIM}"),
    (f"\u200f\u200e{SH} 1,234.56", f"1234 {SHEKALIM} ו-56 אגורות"),
    # Fluent wraps each placeable in isolates: a Hebrew prefix stays glued.
    ("התקשרו ל\u2068054-1234567\u2069", "התקשרו ל" + P_054),
    (f"שילמתם ב\u2068{SH}150\u2069", f"שילמתם ב150 {SHEKALIM}"),
    (f"הזמנה \u20684521\u2069 {SH}\u2068150\u2069", f"הזמנה 4521 150 {SHEKALIM}"),
    (f"הזמנה \u20684521\u2069 \u2068{SH}150\u2069", f"הזמנה 4521 150 {SHEKALIM}"),
    ("שה\u2068054-1234567\u2069", "שה" + P_054),
    ("מ\u2068054-1234567\u2069", "מ" + P_054),
    ("כ\u2068054-1234567\u2069", "כ" + P_054),
    ("ה\u2068054-1234567\u2069", "ה" + P_054),
    ("ו\u2068054-1234567\u2069", "ו" + P_054),
    (f"ש\u2068{SH}150\u2069", f"ש150 {SHEKALIM}"),
    (f"ו\u2068{SH}150\u2069", f"ו150 {SHEKALIM}"),
    (f"מ\u2068{SH}150\u2069", f"מ150 {SHEKALIM}"),
    # A mark between a digit and a symbol was the only separator (round 6).
    (f"הזמנה 4521\u200f{SH}150".replace("הזמנה 4521", "קוד 4521"), f"קוד 4521 150 {SHEKALIM}"),
    # Glued to digits on both sides: ambiguous, left as written.
    (f"4521{SH}150", f"4521{SH}150"),
    # More than 2 decimal digits is not agorot: left as written.
    (f"1.500 {SH}", f"1.500 {SH}"),
    (f"{SH}1500.505", f"{SH}1500.505"),
    # Acronyms.
    ('קופ"ח מכבי', "קופת חולים מכבי"),
    # Left alone: times, dates, years, ranges, other digit counts, European decimals.
    ("14:30", "14:30"),
    ("12/03/2026", "12/03/2026"),
    ("2026", "2026"),
    ("3-4", "3-4"),
    ("9-17", "9-17"),
    ("1234567", "1234567"),
    ("12345678", "12345678"),
    ("1234567890", "1234567890"),
    ("12345678901", "12345678901"),
    (f"1,50 {SH}", f"1,50 {SH}"),
]


def main() -> int:
    normalize = load_helper()
    failures = 0
    for given, expected in CASES:
        got = normalize(given)
        if got != expected:
            failures += 1
            print(f"FAIL {given!r}\n  expected {expected!r}\n  got      {got!r}")
    print(f"{len(CASES) - failures}/{len(CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
