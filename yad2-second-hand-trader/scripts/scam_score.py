#!/usr/bin/env python3
"""Flag known Yad2 scam wording in a described buyer/seller interaction.

Deterministic, offline, stdlib-only. It does NOT make a network call or judge an actual
listing. It looks for high-signal phrases from the Israeli Internet Association + Yad2
safety guidance in the text the user pasted (Hebrew or English).

This is a keyword helper. It misses scams phrased in other words, so the red-flag tables in
SKILL.md are always the real check. NO_KEYWORD_MATCH never means the deal is safe.

Usage:
  python3 scripts/scam_score.py --text "the buyer wants me to pay GLS first via a link"
  echo "שלח צילום מסך של העברה בנקאית וביקש לשלם לשליח" | python3 scripts/scam_score.py
"""

import argparse
import re
import sys

# (label, weight, regex). Text is lowercased before matching.
FLAGS = [
    ("pay_courier_first", 3, r"pay the courier|pay gls|pay the shipping|לשלם לשליח|לשלם לחברת השילוח|לשלם למשלוח|(?:pay|לשלם).{0,25}gls"),
    ("transfer_screenshot", 3, r"transfer screenshot|screenshot of the transfer|proof of transfer|צילום מסך של העברה|צילום של העברה|אישור העברה"),
    ("phishing_link", 3, r"(?:link|לינק|קישור).{0,40}(?:pay|receive|credit|card|לתשלום|לקבלת (?:ה)?(?:תשלום|כסף|זיכוי)|לקבל (?:את )?(?:הכסף|התשלום)|זיכוי|אשראי|לשלם)"
                         r"|(?:pay|payment|לשלם|תשלום).{0,30}(?:link|לינק|קישור)"
                         r"|enter your card|credit card details|cvv|מספר כרטיס|פרטי אשראי|פרטי כרטיס|להזין פרטים|דואר ישראל"),
    ("crypto_demand", 3, r"bitcoin|\bbtc\b|crypto|ביטקוין|קריפטו"),
    ("pay_before_seeing", 2, r"pay before|pay in advance|pay first|sight unseen|before i see|before seeing|without seeing"
                             r"|לשלם מראש|לשלם לפני|לפני שראיתי|לפני שראינו|לפני שבדקתי|בלי לראות|מבלי לראות"),
    ("remote_shipping", 2, r"ship it|send it to me|courier|abroad|overseas|משלוח|בחו\"ל|חו\"ל"),
    ("off_platform_urgency", 1, r"whatsapp|urgent|right now|i'm a soldier|relocating|וואטסאפ|דחוף|חייל|עוזב|עכשיו"),
    ("overpayment", 3, r"overpaid|paid too much|refund the difference|שילמתי יותר|תחזיר את ההפרש|תחזיר לי \d"),
    ("deposit_to_hold", 4, r"deposit|holding fee|to hold it|reserve it|keep it for you|מקדמה|דמי רצינות|לשריין|אשמור לך"),
    ("payment_request", 3, r"payment request|approve the request|בקשת (?:ה)?תשלום|(?:תאשר|לאשר).{0,15}(?:בקשה|הבקשה)"),
    ("money_not_received", 3, r"not in my account|no money in my account|money never arrived|לא בחשבון|אין כסף בחשבון|הכסף לא נכנס|לא נכנס לחשבון"),
    ("verification_code", 6, r"verification code|sms code|one[- ]time code|\d[- ]digit code"
                             r"|code (?:you|i) (?:just )?(?:got|received) (?:by|via|in) (?:sms|text)"
                             r"|קוד אימות|קוד האימות|קוד בן \d|קיבלת.{0,10}sms.{0,10}קוד|הקוד שקיבלתי? ב(?:-)?(?:sms|הודעה)"),
    ("too_cheap", 1, r"too good to be true|way below|suspiciously cheap|זול מדי|מתחת למחיר|מחיר חשוד"),
]

HIGH = 6   # >= HIGH -> likely scam
MED = 3    # >= MED  -> suspicious

# "no deposit, no courier" describes the safe deal, and a deposit after inspecting is normal.
# The negation must directly govern the keyword, so "not meeting, send a deposit" still fires.
NEGATABLE = {"deposit_to_hold", "remote_shipping"}
NEGATED = re.compile(r"(?:\bno need for|\bno|\bwithout|don't need|לא צריך|לא ביקשו(?: ממני)?|בלי|ללא|אין צורך ב)\s*(?:a |an |any )?$")
AFTER_INSPECTING = re.compile(r"after (?:seeing|i saw|inspect)|saw it (?:yesterday|in person|at your)|אחרי ש(?:ראיתי|בדקתי)|ראיתי אצלך|(?<!לא )(?<![א-ת])בדקתי")


def fires(t: str, label: str, pattern: str) -> bool:
    for m in re.finditer(pattern, t):
        if label in NEGATABLE:
            if NEGATED.search(t[max(0, m.start() - 22):m.start()]):
                continue
            if AFTER_INSPECTING.search(t[max(0, m.start() - 45):m.start()]):
                continue
        return True
    return False


def score(text: str):
    t = text.lower()
    hits = [(label, w) for (label, w, pattern) in FLAGS if fires(t, label, pattern)]
    total = sum(w for _, w in hits)
    if total >= HIGH:
        verdict = "LIKELY_SCAM"
    elif total >= MED:
        verdict = "SUSPICIOUS_SLOW_DOWN"
    else:
        verdict = "NO_KEYWORD_MATCH"
    return verdict, total, [label for label, _ in hits]


def main():
    p = argparse.ArgumentParser(description="Flag Yad2 scam wording. A keyword helper, not a clearance.")
    p.add_argument("--text", help="The interaction text (Hebrew or English). If omitted, reads stdin.")
    args = p.parse_args()
    text = args.text if args.text else sys.stdin.read()
    if not text.strip():
        print("No text provided.", file=sys.stderr)
        sys.exit(1)
    verdict, total, flags = score(text)
    print(f"signal: {verdict}")
    print(f"score: {total}")
    print(f"flags: {', '.join(flags) if flags else 'none'}")
    print()
    if verdict == "NO_KEYWORD_MATCH":
        print("This is NOT a clean result. Keywords miss scams, so check the red-flag tables in SKILL.md.")
    else:
        print("This is a keyword hit, not a finding about anyone. Confirm it against the red-flag tables in SKILL.md.")
    print("Never pay in advance; meet and inspect; pay at handover in cash or a known app.")
    print("A transfer screenshot is not payment. A courier never needs YOU to pay to send money TO you.")
    print("Never send anyone a code you received by SMS.")


if __name__ == "__main__":
    main()
