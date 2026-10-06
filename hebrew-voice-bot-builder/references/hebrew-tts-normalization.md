# Hebrew Text Normalization Before TTS

Hebrew TTS engines read raw text the way it is written, so an IVR prompt built
from data ("your appointment is with 054-1234567 and a price in shekels") is where most
audible defects come from. Normalize in application code, before the text
reaches the TTS call. On Google's Chirp 3 HD voices, the `[pause]` markup tags
("Pause control") are listed as unavailable for `he-il`. Punctuation still
shapes pauses, which is why the helper below puts a comma between digit groups.
SSML on Chirp 3 HD (including `<break>`) is in Preview and works only for
synchronous requests, not streaming, so a streamed Hebrew prompt gets its
pauses from punctuation alone.

## What to normalize

| Input | Problem | Normalize to |
|-------|---------|--------------|
| Phone number `054-1234567` | Read as one large number | Single digits, grouped as prefix, 3, 4 however the number is written: `אפס חמש ארבע, אחת שתיים שלוש, ...` |
| 9-digit Teudat Zehut | Same | Single digits, grouped in threes. Order numbers and 8-digit IDs stored as integers need your own rule (pad IDs with `zfill(9)`, read order numbers by field) |
| `<amount> ₪`, `₪<amount>`, `<amount> ש"ח` | Symbol or acronym read letter by letter or skipped; separators and agorot misread | Whole shekels without separators, then agorot in words (`שקל אחד`, `שני שקלים`, `אגורה אחת`, `שתי אגורות` for 1 and 2) |
| Acronyms with gershayim (`ת"ז`, `קופ"ח`) | Spelled out or mangled | Full words from your own dictionary |
| Dates and times (`12/03`, `14:30`) | Ambiguous order, read as a fraction or a ratio | Words, in the order your callers expect. The helper below does NOT touch dates and times; add your own rule |
| Ambiguous unvocalized words | Wrong reading (e.g. a name) | Add niqqud or a phonetic respelling for that word only |

Digits read one by one use the feminine counting forms (`אחת`, `שתיים`), which is
how Israelis read phone numbers aloud. Numbers that count a noun must agree with
its gender (`שני שקלים`, `שתי דקות`), and engines differ in how they read a bare
numeral, so listen to each engine's output for your real prompts.

## Helper

The helper covers phone numbers (0X, 05X, 07X and +972 forms), 9-digit IDs,
shekel amounts and gershayim acronyms. Dates and times, and service numbers
such as 1-700, 1-800 and star numbers, are yours to add. It makes one pass over the text, so
an amount it has already rewritten is never re-read as an ID or a phone number.

```python
import re

DIGITS = ["אפס", "אחת", "שתיים", "שלוש", "ארבע", "חמש", "שש", "שבע", "שמונה", "תשע"]

# Expansions you control. Extend with the acronyms your prompts actually use.
ACRONYMS = {
    'ת"ז': "תעודת זהות",
    'קופ"ח': "קופת חולים",
}

# A full amount: 150,000 / 1,500.50 / 12.50 / 7. Only "." is a decimal point,
# with at most 2 digits (agorot); anything else is left as written. An amount
# never starts with 0, so a phone number or an ID can never be read as a price.
_N = r"(?:0|[1-9]\d{0,2}(?:,\d{3})+|[1-9]\d*)(?:\.\d{1,2})?"
_CUR = r'(?:₪|ש"ח)'
# One horizontal space (also NBSP). Never a newline: two lines are two fields.
_SP = r"[ \u00a0\u202f]"
# Digit lookarounds instead of \b: Python counts Hebrew letters as word
# characters, so \b fails on 'ל0541234567'.
_START = r"(?<!\d)(?<!\d[.,])"
_END = r"(?!\d|[.,]\d)"
# An amount is not followed by more digits, a separator and digits, a hyphen
# and digits (a range or a phone number glued to it), or a closing symbol.
_AEND = rf"(?!\d|[.,]\d|-\d|{_SP}?{_CUR}(?!{_SP}?\d))"
# No symbol glued in front of a suffix amount ('₪150 ₪' is not '150 ₪').
_NOCUR = r'(?<!₪)(?<!ש"ח)'
_PATTERN = re.compile(
    # The side the symbol is glued to decides: '4521 ₪150' and '150₪ 4521'
    # are clear. With a number on BOTH sides ('4521 ₪ 150', '4521₪150') the
    # helper cannot tell which one is the price, so it leaves the text as
    # written, unless the next number is itself a suffix amount ('150 ₪ 20 ₪').
    rf"{_START}{_CUR}(?P<pre>{_N}){_AEND}"                     # ₪150
    rf"|{_START}(?<!\d{_SP}){_CUR}{_SP}(?P<pre2>{_N}){_AEND}"  # ₪ 150
    rf"|{_START}{_NOCUR}(?P<suf>{_N}){_CUR}(?!\d)"             # 150₪
    rf"|{_START}{_NOCUR}(?P<suf2>{_N}){_SP}{_CUR}"             # 150 ₪
    rf"(?:(?!{_SP}?\d)|(?={_SP}{_N}{_SP}?{_CUR}(?!\d)))"
    # Phones: 05X and 07X have a 3-digit prefix (10 digits), landlines
    # 02/03/04/08/09 a 2-digit one (9 digits). Accepts +972, spaces, hyphens.
    rf"|{_START}(?:\+972[- ]?|0)(?P<p>[57]\d|[2-489])[- ]?(?P<r>\d{{3}}[- ]?\d{{4}}){_END}"
    rf"|{_START}(?P<id>\d{{9}}){_END}"                          # Teudat Zehut
)
# Bidi marks that ICU/Babel put around currency (e.g. '150,000.00\u00a0\u200f₪').
_BIDI_CHARS = "\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069"
_BIDI = re.compile(f"[{_BIDI_CHARS}]+")
# A mark between a digit and a symbol or another digit was the only separator
# there ('4521\u200f₪150'). Everywhere else (a Hebrew prefix before an isolated
# number, as Fluent writes it) the mark is simply removed.
_BIDI_GAP = re.compile(rf'(?<=\d)[{_BIDI_CHARS}]+(?=₪|ש"ח|\d)')


def _digits(s: str, groups=(3, 3, 3)) -> str:
    """Read digits one by one, pausing (comma) between groups."""
    d = [DIGITS[int(c)] for c in s if c.isdigit()]
    out, i = [], 0
    for size in groups:
        if i < len(d):
            out.append(" ".join(d[i:i + size]))
            i += size
    if i < len(d):
        out.append(" ".join(d[i:]))
    return ", ".join(out)


def _shekels(n: str) -> str:
    """'150,000' -> '150000 שקלים', '12.50' -> '12 שקלים ו-50 אגורות'."""
    whole, _, frac = n.replace(",", "").partition(".")
    whole = whole.lstrip("0") or "0"
    agorot = int((frac + "00")[:2]) if frac else 0
    parts = []
    if whole != "0" or not agorot:
        parts.append({"1": "שקל אחד", "2": "שני שקלים"}.get(whole, f"{whole} שקלים"))
    if agorot:
        parts.append({1: "אגורה אחת", 2: "שתי אגורות"}.get(agorot, f"{agorot} אגורות"))
    if len(parts) == 2:
        joiner = " ו" if agorot in (1, 2) else " ו-"
        return parts[0] + joiner + parts[1]
    return parts[0]


def _replace(m) -> str:
    amount = m.group("pre") or m.group("pre2") or m.group("suf") or m.group("suf2")
    if amount:
        return _shekels(amount)
    if m.group("p"):
        prefix = "0" + m.group("p")
        return _digits(prefix + m.group("r"), (len(prefix), 3, 4))
    return _digits(m.group("id"))


def normalize_he_for_tts(text: str) -> str:
    text = _BIDI.sub("", _BIDI_GAP.sub(" ", text))
    # Accept both the ASCII quote and the Hebrew gershayim (״).
    text = text.replace("״", '"')
    for short, full in ACRONYMS.items():
        text = text.replace(short, full)
    return _PATTERN.sub(_replace, text)
```

Examples (each one is a case in `scripts/test_hebrew_tts_normalization.py`):

```python
normalize_he_for_tts("חזרו אלינו ב-054-1234567")
# 'חזרו אלינו ב-אפס חמש ארבע, אחת שתיים שלוש, ארבע חמש שש שבע'
normalize_he_for_tts("התקשרו ל0721234567")
# 'התקשרו לאפס שבע שתיים, אחת שתיים שלוש, ארבע חמש שש שבע'
# Amounts, symbol before or after, with or without separators and agorot:
#   1 and 2 whole shekels    -> 'שקל אחד', 'שני שקלים'
#   thousands separators     -> the whole number without commas, then 'שקלים'
#   a decimal part           -> '... שקלים ו-<agorot> אגורות' ('אגורה אחת', 'שתי אגורות')
#   less than one shekel     -> agorot only
# The test script has the exact input and output for every one of these.
normalize_he_for_tts('מספר ת"ז 123456782')
# 'מספר תעודת זהות אחת שתיים שלוש, ארבע חמש שש, שבע שמונה שתיים'
```

Only `.` is read as a decimal point, with at most two digits: a European-style
`1,50 ₪` or `1.500 ₪` is left as written, so format amounts before they reach
the prompt. Apart from a lone 0 (as in 0.50), an amount never starts
with 0, so a phone number or an ID that starts with 0 is never read as a price.

Which number the symbol belongs to is decided by the side it is glued to. When
a number sits on both sides of the symbol with only a space between (an order
number, then the symbol, a space and the amount; or the amount, a space, the
symbol, then a quantity), or with no space on either side, the helper cannot tell which one is the price and leaves that text as
written. A "space" here is one space or NBSP on the same line; a line break
always separates two fields. When the next number carries its own symbol
(the amount, the symbol, then another amount and symbol) both are read as
amounts, even if the first number is really an order number or an ID. The fix belongs in the template: glue the symbol
to the amount, or put a word between the two numbers (`<amount> ₪ ב-12 תשלומים`).
A digit followed by a comma or period right before a prefix symbol, and a
prefix amount followed by a hyphen and digits (a price range, or a phone
number), are also left as written, so the output never merges into one larger
number. A range with the symbol after it is read as the range, then `שקלים`. A minus sign is not
read: phrase a refund or credit in words in the template. Keep the dictionary
and the patterns in your codebase, and add a test for each prompt template so a
new data shape (an extension number, a date) does not reach callers
unnormalized. Run the bundled tests with
`python3 scripts/test_hebrew_tts_normalization.py`.
