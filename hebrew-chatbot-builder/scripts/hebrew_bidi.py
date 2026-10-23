"""
Fix line direction in Hebrew bot replies for WhatsApp and Telegram.

A chat app that picks direction per line takes it from the first strong
character on that line (Unicode UAX #9 rules P1-P3: a line break starts a new
paragraph; bullets, most emoji, digits and punctuation are not strong, while
flag emoji are strong left-to-right). Telegram Desktop does exactly this, and
the same symptom has been reported in WhatsApp: a Hebrew line that opens with
an English word, even after "- " or an emoji, renders left-to-right with its
punctuation moved to the wrong end. A bot cannot set `dir` on a chat message
the way a web widget can, and an LLM reply can start any line with English, so
the fix has to run on the final text.

fix_line_direction() inserts RIGHT-TO-LEFT MARK (U+200F) into each such line.
Rules, each one load-bearing:
- Only Hebrew replies are touched. In an English reply, a line like
  "Your order from רמי לוי is on the way" is meant to stay left-to-right, so
  by default the reply counts as Hebrew when its Hebrew letters are at least
  half its Latin letters (code, inline code and URLs excluded). A technical Hebrew answer
  can be Latin-heavy, so when you know the conversation language, pass
  hebrew_reply=True or False instead of relying on the guess.
- Hebrew inside a URL does not count, so a bare link with a Hebrew path is
  not flipped.
- The mark goes at the start of the WORD that holds the line's first strong
  character, after skipping a leading quote or list marker ("> ", "**>",
  "- ", "* ", "1. ", "\\- "). Not at column 0, because Telegram MarkdownV2
  rejects a quote whose ">" is not first and a list marker must stay first to
  be parsed. Not right before the letter either, because that splits "/start",
  "@user", "#tag", a MarkdownV2 escape like "\\[" or an HTML entity like
  "&quot;" from what follows, which kills the command, mention or escape.
- Lines inside ``` code fences, and lines that carry a fence, are left alone,
  so no hidden character ends up in code a user copies.
- Idempotent: an RLM is itself a strong RTL character.

When to call it: on the final text, BEFORE you split into chunks or truncate to
a platform limit (it adds one character per fixed line), and BEFORE you compute
Telegram message entity offsets if you send entities= instead of a parse mode.
With parse_mode="HTML", code is in <pre>, not ``` fences, so run it before
wrapping code in <pre>.

Usage:
  from hebrew_bidi import fix_line_direction
  text = fix_line_direction(text)                 # auto-detect reply language
  text = fix_line_direction(text, hebrew_reply=True)

  python hebrew_bidi.py --test     # run the built-in checks
"""

from __future__ import annotations

import re
import sys
import unicodedata

RLM = "‏"
_FENCE = "```"
_URL = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+(?:\.[\w-]+)+/\S*")
_INLINE_CODE = re.compile(r"`[^`\n]*`")
# Leading block markup that must stay at column 0: quotes, then a list marker.
_PREFIX = re.compile(r"^\s*(?:(?:\*\*)?>\s*)?(?:(?:[-*\u2022]|\\-|\d+[.)]|\d+\\\.)\s+)?")


def _is_hebrew(ch: str) -> bool:
    return "֐" <= ch <= "׿" or "יִ" <= ch <= "ﭏ"


def _is_latin(ch: str) -> bool:
    return ch.isalpha() and unicodedata.bidirectional(ch) == "L"


def _letters(text: str) -> tuple[int, int]:
    """(Hebrew letters, Latin letters), ignoring URLs and inline code."""
    text = _URL.sub(" ", _INLINE_CODE.sub(" ", text))
    return sum(map(_is_hebrew, text)), sum(map(_is_latin, text))


def _insert_at(line: str) -> int | None:
    """Where to put the RLM, or None if the line needs nothing."""
    for i, ch in enumerate(line):
        cls = unicodedata.bidirectional(ch)
        if cls in ("R", "AL"):
            return None  # already starts right-to-left
        if cls == "L":
            start = _PREFIX.match(line).end()
            if i < start:  # a strong character inside the marker itself
                return 0
            space = max(line.rfind(" ", start, i), line.rfind("\t", start, i))
            return space + 1 if space >= 0 else start
    return None


def fix_line_direction(text: str, hebrew_reply: bool | None = None) -> str:
    """Insert RLM into Hebrew lines whose first strong character is LTR."""
    lines = text.split("\n")
    if hebrew_reply is None:
        prose, in_code = [], False
        for line in lines:
            if not in_code and _FENCE not in line:
                prose.append(line)
            if line.count(_FENCE) % 2:
                in_code = not in_code
        he, lat = _letters("\n".join(prose))
        hebrew_reply = he > 0 and 2 * he >= lat
    if not hebrew_reply:
        return text

    out, in_code = [], False
    for line in lines:
        fences = line.count(_FENCE)
        if not in_code and not fences and _letters(line)[0]:
            pos = _insert_at(line)
            if pos is not None:
                line = line[:pos] + RLM + line[pos:]
        if fences % 2:
            in_code = not in_code
        out.append(line)
    return "\n".join(out)


def _self_test() -> None:
    R = RLM
    cases = [
        # (input, expected, hebrew_reply)
        ("Python היא שפה נוחה.", R + "Python היא שפה נוחה.", None),
        ("- Python היא שפה נוחה.", "- " + R + "Python היא שפה נוחה.", None),
        ("\\- Python היא שפה", "\\- " + R + "Python היא שפה", True),
        ("🚀 API של וואטסאפ", "🚀 " + R + "API של וואטסאפ", None),
        ("🇮🇱 שלום לכולם", R + "🇮🇱 שלום לכולם", None),  # flags are strong L
        ("> Python מעולה", "> " + R + "Python מעולה", True),
        ("**>Bot API חדש", "**>" + R + "Bot API חדש", True),
        ("*Python* היא שפה", R + "*Python* היא שפה", None),
        ("`npm` מתקין חבילות", R + "`npm` מתקין חבילות", None),
        ("/start - התחלה", R + "/start - התחלה", True),  # command stays whole
        ("@dana_bot יעזור לכם", R + "@dana_bot יעזור לכם", True),
        ("\\[1\\] Python מצוין", "\\[1\\] " + R + "Python מצוין", True),
        ("&quot;React&quot; היא ספרייה", R + "&quot;React&quot; היא ספרייה", True),
        ("1. React או Vue? בחרו אחד", "1. " + R + "React או Vue? בחרו אחד", None),
        ("שלום, Python עובד.", "שלום, Python עובד.", None),
        (R + "Python כבר מתוקן", R + "Python כבר מתוקן", None),
        ("הנה ההבדלים:\n- React מהיר יותר\n- Vue פשוט יותר",
         "הנה ההבדלים:\n- " + R + "React מהיר יותר\n- " + R + "Vue פשוט יותר", None),
        # Hebrew reply with an English-only line: that line stays LTR
        ("הנה הדוגמה:\nHello world", "הנה הדוגמה:\nHello world", None),
        # English replies with Hebrew names: untouched
        ("Your order from רמי לוי is on the way.",
         "Your order from רמי לוי is on the way.", None),
        ("Pickup at the mall, gate 3. Ask for דיזנגוף סנטר at the desk.",
         "Pickup at the mall, gate 3. Ask for דיזנגוף סנטר at the desk.", None),
        # Hebrew only inside a URL, with or without a scheme: untouched
        ("מידע נוסף:\nwww.example.org/he/דמי_אבטלה",
         "מידע נוסף:\nwww.example.org/he/דמי_אבטלה", None),
        ("מידע נוסף:\nexample.org/he/דמי_אבטלה",
         "מידע נוסף:\nexample.org/he/דמי_אבטלה", None),
        # inline code does not count as Latin prose for the language guess
        ("הריצו `docker compose up -d --build --force-recreate` ואז Compose יעלה",
         "הריצו `docker compose up -d --build --force-recreate` ואז Compose יעלה", None),
        ("Compose מרים את `docker compose up -d --build --force-recreate`",
         R + "Compose מרים את `docker compose up -d --build --force-recreate`", None),
        # code fences, including a fence glued to prose
        ("הנה הקוד:\n```python\nprint('שלום')  # Python\n```\nNode גם עובד",
         "הנה הקוד:\n```python\nprint('שלום')  # Python\n```\n" + R + "Node גם עובד", None),
        ("הנה: ```python\nx = 'Python שלום'\n```\nGo גם",
         "הנה: ```python\nx = 'Python שלום'\n```\n" + R + "Go גם", None),
        ("Your order from רמי לוי", R + "Your order from רמי לוי", True),
        ("Python היא", "Python היא", False),
        ("", "", None),
    ]
    failed = 0
    for given, expected, flag in cases:
        got = fix_line_direction(given, flag)
        if got != expected:
            failed += 1
            print(f"FAIL: {given!r}\n  expected {expected!r}\n  got      {got!r}")
        if fix_line_direction(got, flag) != got:
            failed += 1
            print(f"FAIL (not idempotent): {given!r}")
    print("all checks passed" if not failed else f"{failed} check(s) failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    if "--test" in sys.argv:
        _self_test()
    else:
        print(fix_line_direction(sys.stdin.read()), end="")
