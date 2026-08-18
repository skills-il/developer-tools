#!/usr/bin/env python3
"""Score a described Yad2 buyer/seller interaction against the known Israeli scam playbook.

Deterministic, offline, stdlib-only. It does NOT make a network call or judge an actual
listing. It pattern-matches the text the user pasted (Hebrew or English) against the
high-signal fraud flags from the Israeli Internet Association + Yad2 safety guidance, and
returns a verdict the agent can explain.

Usage:
  python3 scripts/scam_score.py --text "the buyer wants me to pay GLS first via a link"
  echo "שלח צילום מסך של העברה בנקאית וביקש לשלם לשליח" | python3 scripts/scam_score.py
"""

import argparse
import sys

# (label, weight, [substrings]) -- substrings are lowercased before matching.
FLAGS = [
    ("pay_courier_first", 3, ["pay the courier", "pay gls", "pay the shipping", "לשלם לשליח",
                              "לשלם לחברת השילוח", "לשלם למשלוח", "gls"]),
    ("transfer_screenshot", 3, ["transfer screenshot", "screenshot of the transfer", "proof of transfer",
                                "צילום מסך של העברה", "העברה בנקאית", "שלח צילום"]),
    ("phishing_link", 3, ["enter your card", "credit card details", "payment link", "click this link",
                          "לינק", "פרטי אשראי", "כרטיס אשראי", "דואר ישראל", "להזין פרטים"]),
    ("crypto_demand", 3, ["bitcoin", "btc", "crypto", "ביטקוין", "קריפטו"]),
    ("pay_before_seeing", 2, ["pay before", "pay in advance", "pay first", "sight unseen",
                              "before i see", "before seeing", "without seeing",
                              "לשלם מראש", "לשלם לפני", "לפני שראיתי", "לפני שראינו",
                              "לפני שבדקתי", "בלי לראות", "מבלי לראות"]),
    ("remote_shipping", 2, ["ship it", "send it to me", "courier", "abroad", "overseas",
                            "לשלוח", "משלוח", "בחו\"ל", "חו\"ל"]),
    ("off_platform_urgency", 1, ["whatsapp", "urgent", "right now", "i'm a soldier", "relocating",
                                 "וואטסאפ", "דחוף", "חייל", "עוזב", "עכשיו"]),
    ("overpayment", 3, ["overpaid", "paid too much", "refund the difference", "שילמתי יותר",
                        "תחזיר את ההפרש"]),
    ("deposit_to_hold", 4, ["deposit", "holding fee", "to hold it", "reserve it", "מקדמה",
                            "דמי רצינות", "לשמור לי", "לשריין"]),
    ("payment_request", 3, ["payment request", "approve the request", "בקשת תשלום", "תאשר את הבקשה"]),
    ("money_not_received", 3, ["not in my account", "no money in my account", "money never arrived",
                              "לא בחשבון", "אין כסף בחשבון", "הכסף לא נכנס", "לא נכנס לחשבון"]),
    ("too_cheap", 1, ["too good to be true", "way below", "suspiciously cheap", "זול מדי",
                      "מתחת למחיר", "מחיר חשוד"]),
]

HIGH = 6   # >= HIGH -> likely scam
MED = 3    # >= MED  -> suspicious


def score(text: str):
    t = text.lower()
    hits = [(label, w) for (label, w, subs) in FLAGS if any(s in t for s in subs)]
    total = sum(w for _, w in hits)
    if total >= HIGH:
        verdict = "LIKELY_SCAM"
    elif total >= MED:
        verdict = "SUSPICIOUS_SLOW_DOWN"
    else:
        verdict = "NO_STRONG_FLAGS"
    return verdict, total, [label for label, _ in hits]


def main():
    p = argparse.ArgumentParser(description="Score a Yad2 interaction for scam red flags.")
    p.add_argument("--text", help="The interaction text (Hebrew or English). If omitted, reads stdin.")
    args = p.parse_args()
    text = args.text if args.text else sys.stdin.read()
    if not text.strip():
        print("No text provided.", file=sys.stderr)
        sys.exit(1)
    verdict, total, flags = score(text)
    print(f"verdict: {verdict}")
    print(f"score: {total}")
    print(f"flags: {', '.join(flags) if flags else 'none'}")
    print()
    print("Reminder: never pay in advance; meet and inspect; pay at handover in cash or a known app.")
    print("A transfer screenshot is not payment. A courier never needs YOU to pay to send money TO you.")


if __name__ == "__main__":
    main()
