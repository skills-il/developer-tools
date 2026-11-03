#!/usr/bin/env python3
"""
il-review-scan.py: first-pass scanner for Israel-specific defects in a code change.

Reads a unified diff (a file, or stdin) or walks a directory, applies the
pattern rules in RULES below, and prints candidate findings as
file:line, severity, rule id and a one-line explanation.

This is a CANDIDATE generator, not a reviewer:
  * Every hit must be read in context before it goes into a report.
  * A rule with no hits proves nothing. The scanner matches patterns; it does
    not understand data flow, values computed elsewhere, files outside the
    diff, or framework defaults. "Checked and clean" in a report must come
    from the reviewer's own read of the diff, never from this output.

What it does handle:
  * Diff mode scans ADDED lines only, numbered as in the NEW file.
  * Multi-line markup tags (Prettier-style one-prop-per-line JSX) are joined
    from "<tag" to its closing ">" before the tag rules run; the finding is
    reported on the line where the tag opens.
  * Tailwind classes are parsed token by token, so variant prefixes
    (md:, lg:, hover:, group-hover:) are seen; rtl:/ltr: tokens are treated
    as deliberate direction overrides.
  * Git's quoted non-ASCII paths ("b/\\327\\242...") are decoded.

Usage:
    git diff origin/main...HEAD | python3 scripts/il-review-scan.py
    python3 scripts/il-review-scan.py --diff change.patch
    python3 scripts/il-review-scan.py --dir src/
    python3 scripts/il-review-scan.py --diff change.patch --format json
    python3 scripts/il-review-scan.py --list-rules

Exit codes: 0 scan completed (findings or not), 1 --fail-on threshold hit,
2 usage or input error.

Stdlib only. No network.
"""

import argparse
import codecs
import json
import os
import re
import sys

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}

STYLE_EXT = {".css", ".scss", ".sass", ".less", ".styl", ".pcss"}
MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".erb", ".hbs", ".njk", ".liquid", ".js"}  # .js: CRA/Next pages often hold JSX
SCRIPT_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro"}
PY_EXT = {".py"}
CONFIG_EXT = {".yml", ".yaml", ".toml", ".json"}
CODE_EXT = SCRIPT_EXT | PY_EXT | {".rb", ".go", ".java", ".kt", ".cs", ".php", ".swift", ".dart"}
ALL_EXT = STYLE_EXT | MARKUP_EXT | CODE_EXT | CONFIG_EXT

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "out", "coverage", "vendor", "__pycache__", ".venv", "venv"}

FINALS = "\u05da\u05dd\u05df\u05e3\u05e5"  # final kaf, mem, nun, pe, tsadi
HEB_LETTERS = set(chr(c) for c in range(0x05D0, 0x05EB))
HEB_RX = re.compile("[\u05d0-\u05ea]")

# Identifier vocabularies. A bare `tz` is deliberately NOT an ID name in code: in
# date code it almost always means time zone. In a form field name (name="tz")
# it does mean Teudat Zehut, so the markup rules add it back.
ID_NAMES = r"(zehut|teudat|tz_?num\w*|tzNumber|id_?number|idNumber|national_?id|nationalId|israeli_?id|israeliId|passport\w*)"
COMPANY_NAMES = r"(\bhp\b|company_?id|companyId|company_?number|companyNumber|osek\w*|vat_?number|vatNumber|business_?id|businessId)"
PHONE_NAMES = r"(phone\w*|mobile\w*|\btel\b|cellular|cell_?phone)"
POSTAL_NAMES = r"(mikud|zip\w*|postal\w*|postcode)"
DIGIT_STRING_NAMES = "(" + "|".join([ID_NAMES, COMPANY_NAMES, PHONE_NAMES, POSTAL_NAMES]) + ")"
FORM_DIGIT_FIELD = r"[\"'{`]\s*[\"']?(tz|" + DIGIT_STRING_NAMES + r")\w*\s*[\"'}`]"

SENSITIVE_HIGH = (r"(teudat|zehut|tz_?num|tzNumber|idNumber|id_number|nationalId|national_id|israeliId|passport|diagnos|medical"
                  r"|health|clinic|patient|salary|income|iban|bankAccount|bank_account|creditCard|credit_card|cardNumber)")
SENSITIVE_MED = r"(phone|mobile|\btel\b|email|address|fullName|full_name)"
WHOLE_OBJECT = (r"(\.dict\(\)|\.model_dump\(|\.__dict__|\basdict\(|\bvars\(|JSON\.stringify\(|Object\.fromEntries\(|[(,]\s*payload\s*[),]"
                r"|req\.body|request\.(body|data|json)|[(,]\s*formData\s*[),])")
LOG_CALL = (r"(console\.(log|info|warn|error|debug)|\blogger\.\w+\(|\blog\.(info|warn|warning|error|debug|exception)\(|logging\.\w+\(|\bprint\("
            r"|Sentry\.(captureMessage|captureException|setUser|setContext|setExtra|setTag)|\banalytics\.(track|identify)"
            r"|\bgtag\(|mixpanel\.\w+|posthog\.\w+|dataLayer\.push|amplitude\.\w+|\btrackEvent\()")

CRON_STR = re.compile(r"[\"'`]\s*((?:[\d*/,?LW#A-Za-z-]+\s+){4,5}[\d*/,?LW#A-Za-z-]+)\s*[\"'`]")
NUMBERY = re.compile(r"(opacity|alpha|ease|cubic|bezier|scale|duration|version|lineHeight|line-height|letter|rem\b|em\b|px\b|delay|threshold|ratio|zoom|weight)", re.I)

# Context shared with the rules for the file being scanned.
CTX = {"path": "", "file_text": ""}


def ext_of(path):
    return os.path.splitext(path)[1].lower()


# ---------------------------------------------------------------- tag joining

def find_tag_end(text, start):
    """Index of the '>' closing the tag that opens at text[start] ('<'), or -1.
    Skips '>' inside quotes, inside {...} expressions, and the '>' of '=>'."""
    depth, quote, i = 0, None, start + 1
    while i < len(text):
        ch = text[i]
        if not quote and text.startswith("//", i) and text[i - 1] != ":":
            nl = text.find("\n", i)
            if nl == -1:
                return -1
            i = nl + 1
            continue
        if not quote and text.startswith("/*", i):
            close = text.find("*/", i + 2)
            if close == -1:
                return -1
            i = close + 2
            continue
        if not quote and depth > 0 and ch == "/" and re.search(r"[(,=:\[!&|?{};]\s*$|\breturn\s*$", text[:i]):
            j, in_class = i + 1, False  # regex literal: skip to its closing slash
            while j < len(text) and text[j] != "\n":
                c = text[j]
                if c == "\\":
                    j += 2
                    continue
                if c == "[":
                    in_class = True
                elif c == "]":
                    in_class = False
                elif c == "/" and not in_class:
                    break
                j += 1
            i = j + 1
            continue
        if quote:
            if ch == quote and text[i - 1] != "\\":
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        elif ch == ">" and depth == 0 and text[i - 1] != "=":
            return i
        i += 1
    return -1


TAG_OPEN = re.compile(r"<([A-Za-z][\w.-]*)\b")


def extract_tags(lines):
    """lines: list of (lineno, text, added). Yields (lineno, tag_text) for each
    markup tag that touches an added line, joining up to 40 physical lines."""
    n = len(lines)
    for idx, (lineno, text, added) in enumerate(lines):
        for m in TAG_OPEN.finditer(text):
            joined = text[m.start():]
            any_added = added
            end = find_tag_end(joined, 0)
            j = idx
            while end == -1 and j + 1 < n and j - idx < 40:
                if re.match(r"\s*</?[A-Za-z]", lines[j + 1][1]):
                    break  # never bleed into the next element
                j += 1
                joined += "\n" + lines[j][1]
                any_added = any_added or lines[j][2]
                end = find_tag_end(joined, 0)
            tag = joined[: end + 1] if end != -1 else joined
            if any_added:
                yield lineno, tag


# ---------------------------------------------------------------- tailwind

TW_PHYSICAL = re.compile(r"^!?-?(m[lr]|p[lr]|left|right|border-[lr]|rounded-[lr]|rounded-[tb][lr]|scroll-[mp][lr]|inset-[lr])(-|$)"
                         r"|^!?(text-(left|right)|float-(left|right)|clear-(left|right))$")
TW_DIRECTIONAL = re.compile(r"^!?-?(space-x-|translate-x-|origin-(left|right|top-left|top-right|bottom-left|bottom-right)$"
                            r"|bg-gradient-to-(l|r|tl|tr|bl|br)$|bg-linear-to-(l|r|tl|tr|bl|br)$|divide-x)")
CLASS_ATTR = re.compile(r"(className|class|clsx\(|cn\(|cva\(|twMerge\(|tw`|classList)")
QUOTED = re.compile(r"\"([^\"]*)\"|'([^']*)'|`([^`]*)`")


def _tw_tokens(line):
    if not CLASS_ATTR.search(line) and not CTX.get("class_ctx"):
        return []
    out = []
    for m in QUOTED.finditer(line):
        s = next(g for g in m.groups() if g is not None)
        toks = s.split()
        rtl_toks = [t for t in toks if re.search(r"(^|:)(rtl|ltr):|\[dir=", t)]
        for t in toks:
            parts = t.split(":")
            base, variants = parts[-1], parts[:-1]
            if any(v in ("rtl", "ltr") or "dir=" in v for v in variants):
                continue
            out.append((base, t, rtl_toks))
    return out


def _family(base):
    return re.split(r"-", base.lstrip("!-"))[0]


def _mirror_family(fam):
    if fam.endswith("l"):
        return fam[:-1] + "r"
    if fam.endswith("r"):
        return fam[:-1] + "l"
    return {"left": "right", "right": "left"}.get(fam, fam)


def _tw_physical(line):
    hits = []
    for base, tok, rtl_toks in _tw_tokens(line):
        if TW_PHYSICAL.search(base):
            fam = _family(base)
            if any(_family(r.split(":")[-1]) in (fam, _mirror_family(fam)) for r in rtl_toks):
                continue  # paired with an rtl:/ltr: override for the same property
            hits.append(tok)
    return ("utility: " + ", ".join(sorted(set(hits)))) if hits else None


def _tw_directional(line):
    hits = [tok for base, tok, rtl_toks in _tw_tokens(line) if TW_DIRECTIONAL.search(base) and not rtl_toks]
    return ("utility: " + ", ".join(sorted(set(hits)))) if hits else None


# ---------------------------------------------------------------- rule helpers

def _cond(pattern, flags=0, also=None, unless=None, also_path=None):
    rx = re.compile(pattern, flags)
    also_rx = re.compile(also, re.I) if also else None
    unless_rx = re.compile(unless, re.I) if unless else None
    path_rx = re.compile(also_path, re.I) if also_path else None

    def check(line):
        if not rx.search(line):
            return None
        if also_rx and not also_rx.search(line):
            if not (path_rx and path_rx.search(CTX["path"])):
                return None
        if unless_rx and unless_rx.search(line):
            return None
        return True
    return check


def _hebrew_class_problem(line):
    """Explicit Hebrew letter class like [אבגד...] that omits some final forms.
    A bracket body with quotes or commas is a list/array literal, not a regex class."""
    for m in re.finditer(r"\[([^\]]+)\]", line):
        body = m.group(1)
        if re.search(r"[\"',`]", body):
            continue
        if re.search(r"[\u05d0-\u05ea]-[\u05d0-\u05ea]", body) or "\\u05" in body.lower():
            continue
        letters = {ch for ch in body if ch in HEB_LETTERS}
        if len(letters) >= 5:
            missing = [ch for ch in FINALS if ch not in letters]
            if missing:
                return "missing final forms: " + " ".join(missing)
    return None


def _hebrew_range_no_marks(line):
    has_range = re.search(r"\[[^\]]*(\u05d0-\u05ea|\\u05[dD]0-\\u05[eE][aA])[^\]]*\]", line)
    if not has_range:
        return None
    anchored = re.search(r"(/\^|\"\^|'\^|r\"\^|r'\^|\\A|\$/|\$\"|\$')", line)
    accepts_marks = re.search(r"\\u059|\\u05[aAbB]|\\p\{M|\\p\{Mn|\u0591|\u05b0", line)
    accepts_geresh = re.search(r"\\u05[fF][34]|\u05f3|\u05f4|'|\\'", has_range.group(0))
    if anchored and not accepts_marks:
        extra = "" if accepts_geresh else "; also rejects geresh/gershayim and apostrophe"
        return "anchored Hebrew range with no niqqud (U+05B0..U+05C7)" + extra
    return None


def _latin_only_validator(line):
    """Anchored validator that only accepts Latin letters, on a name/address field."""
    if not re.search(r"(/\^|RegExp\(|re\.(compile|match|fullmatch|search)\(|pattern=|\.test\(|\.regex\(|matches\()", line):
        return None
    classes = re.findall(r"\[([^\]]*)\]", line)
    if any(HEB_RX.search(c) or re.search(r"\\u05|\\p\{", c) for c in classes) or re.search(r"\\p\{(L|Letter|Hebrew|Script=Hebrew)", line):
        return None
    latin_class = any(re.search(r"(a-zA-Z|A-Za-z|a-z|A-Z)", c) for c in classes)
    js_word = re.search(r"/\^\[?\\w", line) and ext_of(CTX["path"]) in SCRIPT_EXT
    if not (latin_class or js_word):
        return None
    if re.search(r"(name|first|last|family|given|city|street|address|town|full)", line, re.I):
        return "Latin-only character class on a name or address field"
    return None


def _ascii_slug(line):
    py = ext_of(CTX["path"]) in PY_EXT
    if py and re.search(r"re\.sub\(\s*r?[\"']\[\^\\w", line):
        return ("medium", "Python 3 \\w keeps Hebrew letters but this strips niqqud, geresh and gershayim, so ת״א becomes תא")
    if re.search(r"replace\(\s*/\[\^\\w", line):
        return ("medium", "JavaScript \\w is ASCII-only, so a Hebrew title becomes an empty or colliding slug")
    if re.search(r"replace\(\s*/\[\^\s*a-z0-9|re\.sub\(\s*r?[\"']\[\^a-z0-9|\[\^a-zA-Z0-9", line):
        return ("medium", "ASCII-only allowed set: a Hebrew title becomes an empty or colliding slug")
    return None


def _missing_attr(tag_pat, attr_pat, label):
    rx = re.compile(tag_pat)

    def check(tag):
        if rx.match(tag) and not re.search(attr_pat, tag):
            if "{..." in tag:
                # attributes come from a helper: one LOW "verify", reported by the dir rule only
                return ("low", "attributes spread from a helper; verify the rendered dir and lang") if "dir" in attr_pat else None
            return label
        return None
    return check


def _ltr_input_dir(tag):
    if not re.match(r"<(input|Input|TextField|TextInput)\b", tag):
        return None
    typed = re.search(r"type=[\"'{]*\s*[\"']?(tel|email|url)\b", tag)
    named = re.search(r"\b(name|id|autoComplete|autocomplete)=" + FORM_DIGIT_FIELD, tag, re.I) or \
        re.search(r"\b(name|id|autoComplete|autocomplete)=[\"'{]*\s*[\"']?[\w-]*(email|iban)", tag, re.I)
    if not (typed or named):
        return None
    d = re.search(r"\bdir=[\"'{]*\s*[\"']?(\w+)", tag)
    if not d:
        return "LTR-content field without dir"
    if d.group(1).lower() == "rtl":
        return "LTR-content field forced to dir=\"rtl\""
    return None


def _number_input_for_digit_string(tag):
    if not re.match(r"<(input|Input)\b", tag):
        return None
    if re.search(r"type=[\"'{]*\s*[\"']?number\b", tag) and re.search(r"\b(name|id)=" + FORM_DIGIT_FIELD, tag, re.I):
        return "type=number on a digit string"
    return None


def _placeholder_label(tag):
    if not re.match(r"<(input|Input|textarea)\b", tag) or "placeholder=" not in tag:
        return None
    if re.search(r"aria-label|aria-labelledby|type=[\"']?(hidden|submit|checkbox|radio)", tag):
        return None
    m = re.search(r"\bid=[\"'{]\s*[\"']?([\w-]+)", tag)
    if m and re.search(r"(htmlFor|for)=[\"'{]\s*[\"']?" + re.escape(m.group(1)) + r"\b", CTX["file_text"]):
        return None
    return "placeholder with no linked label"


CONSENT_WORDS = (r"(agree|consent|marketing|newsletter|opt_?in|optIn|subscribe|promo|offers|\bads\b|marketingOk|smsOk|mailing|updates"
                 r"|\u05de\u05d1\u05e6\u05e2\u05d9\u05dd|\u05e2\u05d3\u05db\u05d5\u05e0\u05d9\u05dd|\u05d3\u05d9\u05d5\u05d5\u05e8)")


def _preticked_consent(line):
    if re.search(r"useState(<boolean>)?\(\s*true\s*\)", line) and re.search(CONSENT_WORDS, line, re.I):
        return True
    if re.search(r"(BooleanField|Column\(Boolean)\([^)]*default\s*=\s*True", line) and re.search(CONSENT_WORDS, line, re.I):
        return True
    if re.search(r"\.default\(\s*true\s*\)", line) and re.search(r"(boolean|bool)\(", line) and re.search(CONSENT_WORDS, line, re.I):
        return True
    if re.match(r"<(input|Input|Checkbox)\b", line) and re.search(r"type=[\"']checkbox[\"']|<Checkbox", line) \
            and re.search(r"\b(defaultChecked|checked)(\s|=\{?\s*true\b|/|>|$)", line) and re.search(CONSENT_WORDS, CTX["file_text"], re.I):
        return True
    return None


def _log_sensitive(line):
    if not re.search(LOG_CALL, line):
        return None
    if re.search(SENSITIVE_HIGH, line, re.I):
        return ("high", "ID, health, salary or payment field")
    if re.search(SENSITIVE_MED, line, re.I):
        return ("medium", "contact field")
    if re.search(WHOLE_OBJECT, line, re.I):
        return ("medium", "whole object or request body, which usually carries ID, phone and email")
    return None


def _cron_fields(line):
    m = CRON_STR.search(line)
    if not m:
        return None
    f = m.group(1).split()
    if len(f) == 6:  # seconds-first (Quartz, Spring, some node schedulers)
        f = f[1:]
    if len(f) != 5 or not re.search(r"[\d*]", f[0] + f[1]):
        return None
    return {"minute": f[0], "hour": f[1], "dom": f[2], "month": f[3], "dow": f[4]}


def _cron_without_tz(line):
    if re.search(r"(timeZone|timezone|time_zone|CRON_TZ|TZ=|Asia/Jerusalem|\btz\s*=)", line):
        return None
    vercel = bool(re.search(r"vercel", CTX["path"], re.I))
    if ext_of(CTX["path"]) == ".json" and not vercel:
        return None
    f = _cron_fields(line)
    if f and (vercel or re.search(r"(cron|schedule|Cron|Schedule|every|job|Job|task)", line)):
        if f["hour"] == "*" or f["hour"].startswith("*/"):
            return None  # interval job, wall-clock zone does not matter
        if vercel:
            return "Vercel cron jobs always run in UTC"
        return "cron expression with no time zone on the line"
    if re.search(r"[\"']cron[\"']\s*,", line) and re.search(r"\b(hour|day_of_week)\s*=", line):
        return "APScheduler-style cron job with no timezone argument"
    if re.search(r"@Cron\(", line):
        return "@Cron decorator with no timeZone option on the line"
    return None


APS_DOW_FIX = "APScheduler 3.x: day_of_week='sun,mon,tue,wed,thu' (or 'mon-thu,sun'). Its weekday names run mon..sun, so never use a descending name range here."


def _cron_dow(line):
    f = _cron_fields(line)
    dow = f["dow"] if f else None
    kw = re.search(r"day_of_week\s*=\s*[\"']([^\"']+)[\"']", line)
    if kw:
        dow = kw.group(1)
    if not dow or dow in ("*", "?"):
        return None
    call = CTX.get("sched_call") or ""
    aps = bool(re.search(r"from_crontab|CronTrigger|add_job|scheduled_job|[\"']cron[\"']\s*,", line)) or call in ("from_crontab", "CronTrigger", "add_job", "scheduled_job")
    celery = not aps and (bool(re.search(r"(?<![\w.])crontab\(", line)) or call == "crontab")
    names_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    wrap = re.fullmatch(r"\s*([a-z]{3})\s*-\s*([a-z]{3})\s*", dow.lower())
    if not kw and aps and f:
        wrap = re.fullmatch(r"\s*([a-z]{3})\s*-\s*([a-z]{3})\s*", dow.lower())
    if (kw or (aps and f)) and wrap and not celery and all(x in names_order for x in wrap.groups()):
        a, b = (names_order.index(x) for x in wrap.groups())
        if a > b:
            if aps:
                return ("high", f"APScheduler 3.x orders weekday names mon..sun (0..6) and rejects the wrapping range '{dow}' with ValueError at start-up", APS_DOW_FIX)
            return ("low", f"library not recognised: if this is APScheduler 3.x, '{dow}' raises ValueError at start-up; Celery and node-cron accept it as Sunday to Thursday")
    if re.search(r"\d", dow):
        if celery:
            if dow.replace(" ", "") == "1-5":
                return ("medium", "Celery crontab numbers Sunday as 0, so 1-5 is Monday to Friday; the Israeli work week is 0-4")
            return None  # Celery uses crontab numbering (0 = Sunday); 0-4 is Sunday to Thursday
        if kw and not aps:
            return ("low", f"day_of_week '{dow}' from an unrecognised scheduler: check its numbering (crontab and Celery 0=Sunday, APScheduler 3.x 0=Monday, Quartz 1=Sunday)")
        if aps:
            return ("high", f"APScheduler 3.x numbers 0 as Monday, even in from_crontab, so '{dow}' does not mean what crontab means by it", APS_DOW_FIX)
        if dow.replace(" ", "") == "1-5":
            return ("medium", "1-5 is Monday to Friday in crontab numbering; the Israeli work week is Sunday to Thursday")
        return ("low", f"numeric day-of-week '{dow}': numbering differs by scheduler (crontab 0=Sunday, APScheduler 3.x 0=Monday, Quartz 1=Sunday)")
    if re.search(r"mon-fri", dow, re.I):
        return ("medium", "MON-FRI is not the Israeli work week (Sunday to Thursday)")
    return None


def _dst_window(line):
    zone_in_file = re.search(r"((TIMEZONE|TIME_ZONE|timezone)\s*[:=]\s*|ZoneInfo\(\s*|pytz\.timezone\(\s*)[\"']Asia/Jerusalem", CTX["file_text"])
    if "Asia/Jerusalem" not in line and not (zone_in_file and re.search(r"(crontab\(|cron|schedule|add_job)", line, re.I)):
        return None
    hours = None
    f = _cron_fields(line)
    if f:
        hours = f["hour"]
    kw = re.search(r"\bhour\s*=\s*[\"']?([\d,-]+)", line)
    if kw:
        hours = kw.group(1)
    if not hours or not re.fullmatch(r"[\d,-]+", hours):
        return None
    vals = set()
    for part in hours.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            if a.isdigit() and b.isdigit():
                vals.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            vals.add(int(part))
    if vals & {1, 2}:
        return "Israel-time schedule in the 01:00-02:59 window"
    return None


def _weekend(line):
    """Weekend logic that treats Saturday+Sunday as the weekend.
    Correct Israeli logic (JS getDay 5 and 6; Python weekday 4 and 5) is NOT flagged."""
    js = re.findall(r"getU?T?C?Day\(\)\s*(?:===?|!==?)\s*(\d)|(\d)\s*(?:===?|!==?)\s*\w*\.getU?T?C?Day\(\)|\b(?:day|dow|dayOfWeek)\s*(?:===?|!==?)\s*(\d)\b", line)
    nums = {n for t in js for n in t if n}
    for m in re.finditer(r"\[\s*([0-6](?:\s*,\s*[0-6])*)\s*\]\s*\.includes\(\s*[\w.()]*getU?T?C?Day\(\)", line):
        nums |= set(re.findall(r"\d", m.group(1)))
    if nums:
        if "0" in nums or ("6" in nums and "5" not in nums):
            return "JavaScript day check treats Sunday (0) as a day off or ignores Friday (5)"
        return None
    if re.search(r"weekday\(\)\s*(>=\s*5|>\s*4|==\s*6|in\s*[\(\[{]\s*5\s*,\s*6)", line):
        return "Python weekday() >= 5 is Saturday+Sunday (Monday=0)"
    if re.search(r"isoweekday\(\)\s*(>=\s*6|>\s*5|==\s*7)", line):
        return "isoweekday() 6-7 is Saturday+Sunday"
    if re.search(r"SATURDAY.*SUNDAY|SUNDAY.*SATURDAY", line):
        return "Saturday and Sunday named together as the weekend"
    return None


def _vat_literal(line):
    if NUMBERY.search(line):
        return None
    if re.search(r"(?<![\w.])(0\.17|1\.17)(?![\d])", line):
        return ("high", "17% written as a fraction")
    if re.search(r"(vat|maam|mam)\w*\s*[:=]\s*17\b", line, re.I):
        return ("high", "17 as a percent constant")
    if re.search(r"(?<![\w.])(0\.18|1\.18)(?![\d])", line):
        return ("medium", "18% written as a fraction")
    if re.search(r"(vat|maam|mam|tax_?rate|taxRate)\w*\s*[:=]\s*18\b", line, re.I):
        return ("medium", "18 as a percent constant")
    return None


def _hardcoded_offset(line):
    if re.search(r"[+]0?[23]:00\b|GMT\s*\+\s*[23]\b|UTC\s*\+\s*[23]\b|utcOffset\(\s*(120|180|2|3)\s*\)", line):
        return True
    duration = re.search(r"timedelta\(\s*hours\s*=\s*[23]\s*\)|\+\s*[23]\s*\*\s*(60\s*\*\s*60|3600)|setHours\([^)]*\+\s*[23]\s*\)", line)
    if duration and re.search(r"(now|israel|jerusalem|local|offset|\btz\b|utc|\bil\b|clock|timezone|wall)", line, re.I):
        return True
    return None


def _pytz_tzinfo(line):
    if "pytz" not in CTX["file_text"]:
        return None
    m = re.search(r"\btzinfo\s*=\s*([\w.()\"']+)", line)
    if m and not re.search(r"utc|UTC|timezone\.utc|ZoneInfo", m.group(1)):
        return True
    return None


def _csv_no_bom(line):
    ext = ext_of(CTX["path"])
    heb = bool(HEB_RX.search(CTX["file_text"]))
    if ext in PY_EXT and "csv" in CTX["file_text"]:
        if re.search(r"open\([^)]*[\"']w[\"']", line) and re.search(r"encoding\s*=\s*[\"']utf-?8[\"']", line, re.I):
            return ("medium" if heb else "low", "UTF-8 without BOM")
        if re.search(r"\.to_csv\(", line) and not re.search(r"utf-?8-sig", line, re.I):
            return ("medium" if heb else "low", "to_csv without utf-8-sig")
    if ext in SCRIPT_EXT and re.search(r"text/csv", line) and "\\uFEFF" not in CTX["file_text"] and "\ufeff" not in CTX["file_text"]:
        return ("medium" if heb else "low", "CSV blob without a BOM")
    return None


def _holiday_literal(line):
    names = (r"(rosh.?hashan|yom.?kippur|sukkot|succot|simchat|shavuot|pesach|passover|hanukk?ah|chanuk|purim|"
             r"yom.?ha.?atzmaut|independence.?day|tisha.?b|\u05e8\u05d0\u05e9 \u05d4\u05e9\u05e0\u05d4|\u05d9\u05d5\u05dd \u05db\u05d9\u05e4\u05d5\u05e8|\u05e1\u05d5\u05db\u05d5\u05ea|\u05e9\u05d1\u05d5\u05e2\u05d5\u05ea|\u05e4\u05e1\u05d7|\u05e4\u05d5\u05e8\u05d9\u05dd|\u05d7\u05e0\u05d5\u05db\u05d4)")
    if re.search(names, line, re.I) and re.search(r"\b20\d\d-\d\d-\d\d\b|\b\d{1,2}[./]\d{1,2}[./]20\d\d\b|new Date\(\s*20\d\d|date\(\s*20\d\d", line):
        return "holiday name next to a fixed date literal"
    return None


def _arrow_key(line):
    if re.search(r"\b(key|code)\s*={2,3}\s*[\"']Arrow(Left|Right)[\"']|case\s+[\"']Arrow(Left|Right)[\"']", line):
        return "ArrowLeft/ArrowRight handled without a direction check"
    return None


def _interpolation_next_to_hebrew(line):
    if HEB_RX.search(line) and re.search(r"\$\{[^}]+\}|\{\s*[A-Za-z_$][\w.$]*(\([^)]*\))?\s*\}|%s|%\(\w+\)s", line):
        if not re.search(r"<bdi|dir=[\"']?auto|\\u2068|\u2068|unicode-?[Bb]idi", line):
            return "Hebrew text with interpolated value and no isolation"
    return None


def _business_day_lib(line):
    if re.search(r"\b(addBusinessDays|subBusinessDays|differenceInBusinessDays|isWeekend)\(", line):
        return True
    if re.search(r"busday_(offset|count)\(|is_busday\(|busdaycalendar\(|\bBDay\(|(?<![\w.])BusinessDay\(|CustomBusinessDay\(|bdate_range\(", line):
        wm = re.search(r"weekmask\s*=\s*[\"']([^\"']+)[\"']", line)
        if wm and re.sub(r"\s+", " ", wm.group(1).strip()).lower() in ("1111001", "sun mon tue wed thu", "mon tue wed thu sun"):
            return None  # already Sunday to Thursday
        return "default or non-Israeli weekmask" if wm is None else f"weekmask '{wm.group(1)}' is not Sunday to Thursday"
    return None


def _numeric_id_storage(line):
    names = DIGIT_STRING_NAMES
    if re.search(r"(parseInt|parseFloat|Number|\bint|BigInt)\(\s*[\w.\[\]'\"]*" + names, line, re.I):
        return True
    if re.search(r"\b" + names + r"\s*[?]?\s*:\s*number\b", line, re.I):
        return True
    if re.search(r"\b" + names + r"\w*\s*:\s*(z|yup|Joi)\.(coerce\.)?number\(", line, re.I):
        return True
    if re.search(names + r"\w*\s*=\s*models\.(Big|Positive|PositiveBig|Small)?IntegerField\(", line, re.I):
        return True
    # bare `id: number` only inside a file that is itself an ID validator
    if re.search(r"(^|[/_.-])(tz|zehut|teudat|israeli-?id|id-?valid)", CTX["path"], re.I) and re.search(r"\bid\s*:\s*number\b|int\(\s*id\b", line):
        return True
    return None


# Each rule: id, family, severity ("dynamic" = the check returns (severity, detail)),
# ext, scope ("line" or "tag"), check, msg, fix, route.
RULES = [
    # RTL and bidi
    dict(id="rtl-css-physical-box", family="rtl", severity="medium", ext=STYLE_EXT | MARKUP_EXT | SCRIPT_EXT,
         check=_cond(r"(?<![\w-])(margin|padding|border)-(left|right)\b|\b(margin|padding|border)(Left|Right)\s*:"),
         msg="Physical left/right box property: lands on the wrong side under dir=rtl.",
         fix="Use margin-inline-start/end, padding-inline-*, border-inline-* (or marginInlineStart in style objects)."),
    dict(id="rtl-css-physical-inset", family="rtl", severity="low", ext=STYLE_EXT,
         check=_cond(r"^\s*(left|right)\s*:\s*[^;]+;?"),
         msg="Physical left/right offset in a stylesheet.",
         fix="Use inset-inline-start / inset-inline-end unless the element must stay on that physical side."),
    dict(id="rtl-text-align-physical", family="rtl", severity="medium", ext=STYLE_EXT | MARKUP_EXT | SCRIPT_EXT,
         check=_cond(r"text-align\s*:\s*(left|right)\b|textAlign\s*:\s*[\"'](left|right)[\"']"),
         msg="text-align left/right does not follow direction.",
         fix="Use text-align: start / end."),
    dict(id="rtl-tailwind-physical", family="rtl", severity="medium", ext=MARKUP_EXT | SCRIPT_EXT,
         check=_tw_physical,
         msg="Physical Tailwind utility (variant prefixes such as md: included): lands on the wrong side under dir=rtl.",
         fix="ml/mr -> ms/me, pl/pr -> ps/pe, text-left/right -> text-start/end, rounded-l -> rounded-s, left/right -> the logical inset utility of your Tailwind version; or pair it with an rtl: override."),
    dict(id="rtl-tailwind-directional", family="rtl", severity="low", ext=MARKUP_EXT | SCRIPT_EXT,
         check=_tw_directional,
         msg="Direction-sensitive Tailwind utility (space-x, translate-x drawer, origin, gradient direction) with no rtl: counterpart in the class list.",
         fix="Check it under dir=rtl: add rtl:space-x-reverse, rtl:-translate-x-full, or the mirrored origin/gradient, per your Tailwind version's docs."),
    dict(id="rtl-directional-icon", family="rtl", severity="low", ext=MARKUP_EXT | SCRIPT_EXT,
         check=_cond(r"(Arrow|Chevron|Caret)(Right|Left)\b|arrow-(right|left)|chevron-(right|left)|[\u2190\u2192]", unless=r"^\s*import\b|\b(rtl|ltr):|:dir\(|scaleX\(-1\)"),
         msg="Directional icon: forward/back arrows should point the other way in RTL.",
         fix="Mirror with an rtl: variant, :dir(rtl) { transform: scaleX(-1) }, or swap the icon by direction. Do NOT mirror icons that are not directional (play, check, clock)."),
    dict(id="rtl-input-ltr-content", family="rtl", severity="medium", ext=MARKUP_EXT, scope="tag",
         check=_ltr_input_dir,
         msg="Phone/email/URL/ID/company-number input that is not dir=\"ltr\": digits and Latin text reorder inside an RTL form.",
         fix='Set dir="ltr" on the input itself (keep the label RTL).'),
    dict(id="rtl-bidi-isolation", family="rtl", severity="low", ext=MARKUP_EXT | SCRIPT_EXT | PY_EXT | {".go", ".rb", ".java", ".kt", ".php"},
         check=_interpolation_next_to_hebrew,
         msg="Hebrew string with an interpolated value: numbers, phones, emails or Latin names can spill over and reorder.",
         fix='Wrap the value in <bdi> (or an element with dir="auto"); in plain strings (SMS, push, email subject) wrap it with U+2068 ... U+2069.'),
    dict(id="rtl-html-dir-missing", family="rtl", severity="high", ext=MARKUP_EXT, scope="tag",
         check=_missing_attr(r"<html\b", r"\bdir=", "<html> without dir"),
         msg="<html> without dir: the page renders LTR.",
         fix='Set dir="rtl" (and lang="he") on <html> for the Hebrew locale.'),
    # Hebrew text
    dict(id="heb-class-missing-finals", family="hebrew", severity="high", ext=CODE_EXT | MARKUP_EXT,
         check=_hebrew_class_problem,
         msg="Explicit Hebrew letter class omits final letters: words ending in them fail.",
         fix="Use the range \\u05D0-\\u05EA (it includes the finals) or add the missing letters."),
    dict(id="heb-range-no-niqqud", family="hebrew", severity="medium", ext=CODE_EXT | MARKUP_EXT,
         check=_hebrew_range_no_marks,
         msg="Anchored Hebrew-only validator rejects text with niqqud, geresh or gershayim (names like ז׳קלין, abbreviations like ת״א).",
         fix="Accept marks [\\u0591-\\u05BD\\u05BF\\u05C1\\u05C2\\u05C4\\u05C5\\u05C7], geresh/gershayim \\u05F3\\u05F4, apostrophe, hyphen and maqaf, or normalise first."),
    dict(id="heb-latin-only-validator", family="hebrew", severity="high", ext=CODE_EXT | MARKUP_EXT,
         check=_latin_only_validator,
         msg="Latin-only validator on a name or address: every Hebrew (and Arabic or Russian) name is rejected. JavaScript \\w is ASCII-only too.",
         fix="Accept Hebrew letters and marks (\\u05D0-\\u05EA plus the mark set), or use a Unicode letter class (\\p{L} with the u flag) and validate length instead of script."),
    dict(id="heb-ascii-slug", family="hebrew", severity="dynamic", ext=CODE_EXT,
         check=_ascii_slug,
         msg="Slug/filename sanitiser that mangles Hebrew titles.",
         fix="Keep \\u05D0-\\u05EA and decide what geresh/gershayim become (percent-encode in URLs), or fall back to an id when the slug is empty."),
    dict(id="heb-collation-no-locale", family="hebrew", severity="low", ext=SCRIPT_EXT,
         check=_cond(r"\.localeCompare\(\s*[^,()]+\)"),
         msg="localeCompare without a locale uses the runtime default.",
         fix="localeCompare(b, 'he') or a shared new Intl.Collator('he')."),
    dict(id="heb-truncate-codeunits", family="hebrew", severity="low", ext=SCRIPT_EXT,
         check=_cond(r"\.(substring|substr|slice)\(\s*0\s*,\s*\d+\s*\)", also=r"(name|title|text|desc|label|message|body|summary)"),
         msg="Truncating by code units can split a letter from its niqqud.",
         fix="Truncate on graphemes: [...new Intl.Segmenter('he', {granularity: 'grapheme'}).segment(s)]."),
    dict(id="heb-normalize-strip-maqaf", family="hebrew", severity="medium", ext=CODE_EXT,
         check=_cond(r"\\u0591-\\u05[cC]7|\u0591-\u05c7|\\u05[bB]0-\\u05[cC]7"),
         msg="Mark-stripping range also deletes punctuation inside it (maqaf U+05BE, paseq, sof pasuq, nun hafukha).",
         fix="Strip only the marks: [\\u0591-\\u05BD\\u05BF\\u05C1\\u05C2\\u05C4\\u05C5\\u05C7] (after NFD if presentation forms may appear)."),
    dict(id="heb-csv-no-bom", family="hebrew", severity="dynamic", ext=CODE_EXT,
         check=_csv_no_bom,
         msg="CSV export without a UTF-8 BOM: Hebrew headers and names can open as mojibake when the file is double-clicked in Excel.",
         fix="Python: encoding=\"utf-8-sig\". JavaScript: prepend \"\\uFEFF\" to the CSV text."),
    # Identifiers
    dict(id="id-numeric-storage", family="identifiers", severity="high", ext=CODE_EXT,
         check=_numeric_id_storage,
         msg="ID, company number, phone or postal code stored or typed as a number: leading zeros vanish.",
         fix="Keep it a string (CharField/varchar); validate digits with a regex and pad IDs to 9 before the check digit."),
    dict(id="id-number-input", family="identifiers", severity="medium", ext=MARKUP_EXT, scope="tag",
         check=_number_input_for_digit_string,
         msg="type=number for an ID, company number, phone or postal code: drops leading zeros, adds spinners, accepts e and -.",
         fix='Use type="text" (or tel) with inputMode="numeric" and a pattern.'),
    dict(id="id-handrolled-tz", family="identifiers", severity="medium", ext=CODE_EXT,
         check=_cond(r"(%\s*10\b|\{9\}|length\s*[!=]==?\s*9\b|len\(\w+\)\s*[!=]=\s*9\b)", also=ID_NAMES + "|" + COMPANY_NAMES,
                     also_path=r"(^|[/_.-])(tz|zehut|teudat|israeli-?id|id-?valid)"),
         msg="Hand-rolled Teudat Zehut / company-number check: verify padding to 9 digits and the Luhn digit-sum step.",
         fix="Compare against the reference implementation in israeli-id-validator.", route="israeli-id-validator"),
    dict(id="id-mikud-five", family="identifiers", severity="medium", ext=CODE_EXT | MARKUP_EXT,
         check=_cond(r"(\{5\}|length\s*[!=<>]==?\s*5|maxLength=\{?[\"']?5\b|max_length\s*=\s*5|len\(\w+\)\s*[!=]=\s*5|\.(length|max|min|len)\(\s*5\s*\))", also=r"(mikud|zip|postal|postcode|\u05de\u05d9\u05e7\u05d5\u05d3)"),
         msg="Five-digit postal code check: Israeli mikud has been seven digits since 2013.",
         fix="Accept exactly 7 digits (string)."),
    dict(id="id-handrolled-phone", family="identifiers", severity="medium", ext=CODE_EXT | MARKUP_EXT,
         check=_cond(r"(RegExp\(|/\^|re\.compile|re\.match|pattern=)", also=r"(phone|mobile|\btel\b|cell|\u05d8\u05dc\u05e4\u05d5\u05df|\+?972|\^0?5)"),
         msg="Hand-rolled Israeli phone pattern.",
         fix="Check prefixes, lengths and +972 handling against israeli-phone-formatter.", route="israeli-phone-formatter"),
    dict(id="pay-handrolled-card", family="identifiers", severity="medium", ext=CODE_EXT,
         check=_cond(r"\bluhn\w*\(|isValidCard|validateCard|card\w*\.length\s*[<>=!]+\s*1[3-9]|len\(\s*card\w*\s*\)\s*[<>=!]+\s*1[3-9]", re.I),
         msg="Hand-rolled card-number check (Luhn or a length floor written for international cards).",
         fix="Do not assume every card your Israeli processor accepts passes this check. Confirm the accepted formats in the processor's documentation and let the processor (or its hosted fields) validate."),
    # Money, numbers, dates
    dict(id="fmt-tolocale-no-locale", family="money-dates", severity="medium", ext=SCRIPT_EXT,
         check=_cond(r"\.toLocale(String|DateString|TimeString)\(\s*\)"),
         msg="toLocale*() with no locale: output follows the server or browser default, not he-IL.",
         fix="Pass 'he-IL' (and timeZone: 'Asia/Jerusalem' for dates)."),
    dict(id="fmt-currency-concat", family="money-dates", severity="medium", ext=SCRIPT_EXT | MARKUP_EXT | PY_EXT,
         check=_cond(r"[\"'`]\s*\u20aa\s*[\"'`]?\s*\+|\+\s*[\"'`]\s*\u20aa|\u20aa\s*\$\{|\$\{[^}]+\}\s*\u20aa|\u20aa\s*\{|\}\s*\u20aa|toFixed\(\s*2\s*\)\s*\+|f[\"'].*\{[^}]+:.2f\}\s*\u20aa"),
         msg="Shekel amount built by string concatenation: symbol side, separators and bidi marks are left to chance.",
         fix="new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(amount)."),
    dict(id="fmt-vat-hardcoded", family="money-dates", severity="dynamic", ext=CODE_EXT,
         check=_vat_literal,
         msg="Hardcoded VAT rate. 17% (in any notation) is outdated (until 31.12.2024); 18% applies from 01.01.2025, and the applicable rate follows the transaction date.",
         fix="Read the rate from one config/table keyed by effective date; never re-price old invoices with today's constant."),
    dict(id="fmt-price-excl-vat", family="money-dates", severity="medium", ext=MARKUP_EXT | SCRIPT_EXT,
         check=_cond("(\u05dc\u05e4\u05e0\u05d9|\u05dc\u05d0 \u05db\u05d5\u05dc\u05dc|\u05d1\u05ea\u05d5\u05e1\u05e4\u05ea|\\+)\\s*\u05de\u05e2(\"|\u05f4|&quot;|\\\\\")?\u05de|[Ee]xcl\\.?\\s*VAT|\\b[Ee]x\\.?\\s*VAT|plus VAT|before VAT"),
         msg="Price labelled as excluding VAT. On a consumer-facing page this is a risk under the Consumer Protection Law (total price only); on a B2B page it may be intended.",
         fix="Show the VAT-inclusive total price to consumers; keep net prices for business-only flows and say which one the page is."),
    dict(id="fmt-us-date", family="money-dates", severity="medium", ext=CODE_EXT | MARKUP_EXT,
         check=_cond(r"MM/dd/yyyy|MM/DD/YYYY|%m/%d/%Y|M/d/yyyy|[\"']en-US[\"']"),
         msg="US month-first date format or en-US locale in Israeli-facing output.",
         fix="Format with Intl.DateTimeFormat('he-IL', ...) or an explicit dd/MM/yyyy pattern."),
    dict(id="fmt-weekend-sat-sun", family="money-dates", severity="medium", ext=CODE_EXT,
         check=_weekend,
         msg="Weekend logic that treats Saturday+Sunday as the weekend: in Israel the weekend is Friday+Saturday and Sunday is a working day.",
         fix="Use a locale table (Intl.Locale 'he-IL' week info, CLDR: firstDay 7, weekend [5,6]) or an explicit Israeli business calendar."),
    dict(id="fmt-business-day-lib", family="money-dates", severity="medium", ext=CODE_EXT,
         check=_business_day_lib,
         msg="Library business-day helper: date-fns counts Monday to Friday and NumPy's default weekmask is Monday to Friday, so Sunday is skipped and Friday counted.",
         fix="Pass an Israeli week (NumPy weekmask='1111001', Sunday to Thursday) or use a helper with a configurable weekend and holidays."),
    dict(id="fmt-agorot-units", family="money-dates", severity="low", ext=CODE_EXT,
         check=_cond(r"(\*\s*100\b|/\s*100\b)", also=r"(amount|price|total|sum|agorot|cents|shekel|ils|nis)"),
         msg="x100 or /100 on a money value: confirm which side uses agorot and which uses shekels.",
         fix="Name the unit in the variable (amountAgorot) and check the payment provider's API docs for its unit."),
    # Time zone
    dict(id="tz-hardcoded-offset", family="time", severity="high", ext=CODE_EXT | CONFIG_EXT,
         check=_hardcoded_offset,
         msg="Fixed UTC offset for Israel: wrong for part of every year (UTC+2 standard, UTC+3 from the Friday before the last Sunday of March to the last Sunday of October).",
         fix="Use the IANA zone Asia/Jerusalem (Intl timeZone option, Python zoneinfo, or your date library's zone support)."),
    dict(id="tz-pytz-tzinfo", family="time", severity="high", ext=PY_EXT,
         check=_pytz_tzinfo,
         msg="pytz zone passed as tzinfo= to a datetime constructor: you get the zone's first (LMT) offset, +02:21 for Asia/Jerusalem.",
         fix="IL.localize(datetime(...)), or use zoneinfo.ZoneInfo('Asia/Jerusalem') with tzinfo=."),
    dict(id="tz-naive-today", family="time", severity="medium", ext=PY_EXT,
         check=_cond(r"\bdate\.today\(\)|datetime\.(now|today)\(\s*\)|datetime\.utcnow\(\)"),
         msg="Naive local date/time: on a UTC server, between midnight Israel time and 02:00 (03:00 in summer) it is still yesterday.",
         fix="datetime.now(ZoneInfo('Asia/Jerusalem')).date() when the business date is Israeli."),
    dict(id="tz-django-utc-date", family="time", severity="medium", ext=PY_EXT,
         check=_cond(r"timezone\.now\(\)\s*\.\s*(date\(\)|strftime\(|isoformat\(\)\s*\[)"),
         msg="Django timezone.now() is always UTC when USE_TZ is on, so .date()/strftime() gives the UTC date: from midnight Israel time until 02:00 (03:00 in summer) it is still yesterday.",
         fix="timezone.localdate() (or localtime(now).strftime) with TIME_ZONE or the activated zone set to Asia/Jerusalem."),
    dict(id="tz-django-utc-setting", family="time", severity="medium", ext=PY_EXT,
         check=_cond(r"^\s*TIME_ZONE\s*=\s*[\"']UTC[\"']"),
         msg="Django TIME_ZONE = \"UTC\": localtime(), localdate() and template dates render in UTC unless a zone is activated per request, so times shown to Israeli users (SMS, emails, pages) are 2 or 3 hours early.",
         fix="TIME_ZONE = \"Asia/Jerusalem\" for an Israeli product (storage stays UTC with USE_TZ), or timezone.activate('Asia/Jerusalem') where messages are rendered."),
    dict(id="tz-cron-no-zone", family="time", severity="medium", ext=CODE_EXT | CONFIG_EXT,
         check=_cron_without_tz,
         msg="Schedule with no time zone: it runs in the scheduler's zone (often UTC), so an Israeli local-time job drifts by 2 or 3 hours.",
         fix="Set the scheduler's time zone option to Asia/Jerusalem, or keep UTC and document both DST cases."),
    dict(id="tz-cron-dow", family="time", severity="dynamic", ext=CODE_EXT | CONFIG_EXT,
         check=_cron_dow,
         msg="Day-of-week field in a schedule.",
         fix="Sunday to Thursday per library: system crontab 0-4 (Debian Vixie cron documents no name ranges); node-cron 0-4 or sun-thu; Celery crontab 0-4 (0 = Sunday); APScheduler 3.x day_of_week='sun,mon,tue,wed,thu' or 'mon-thu,sun' (NOT 'sun-thu', which raises ValueError); Quartz SUN-THU or 1-5; Vercel 0-4 (no names). Check the scheduler's own docs."),
    dict(id="tz-dst-window", family="time", severity="medium", ext=CODE_EXT | CONFIG_EXT,
         check=_dst_window,
         msg="Asia/Jerusalem schedule between 01:00 and 02:59: 02:00-02:59 does not exist on the spring-forward Friday and 01:00-01:59 happens twice on the last Sunday of October.",
         fix="Move the job out of that window, or schedule in UTC, or confirm how this scheduler handles a skipped and a repeated hour."),
    dict(id="tz-utc-date-key", family="time", severity="medium", ext=SCRIPT_EXT,
         check=_cond(r"toISOString\(\)\s*\.\s*(slice|substring|substr)\(\s*0\s*,\s*10\s*\)|toISOString\(\)\s*\.\s*split\(\s*[\"']T"),
         msg="Calendar date taken from toISOString(): that is the UTC date, so from midnight Israel time until 02:00 (03:00 in summer) it is still yesterday.",
         fix="new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jerusalem' }).format(d) gives YYYY-MM-DD in Israel time."),
    dict(id="tz-dst-handrolled", family="time", severity="high", ext=CODE_EXT,
         check=_cond(r"(isDST|isDst|is_dst|dstStart|dst_start|dstEnd|lastSunday|last_sunday|isSummerTime)", also=r"(israel|jerusalem|IL\b|il_|dst|summer)"),
         msg="Hand-rolled Israeli DST logic: the 2013 rule differs from 2005-2012 (ended before Yom Kippur), so history breaks even if today works.",
         fix="Delete it and let tzdata (Asia/Jerusalem) decide."),
    dict(id="tz-holiday-literal", family="time", severity="medium", ext=CODE_EXT | CONFIG_EXT,
         check=_holiday_literal,
         msg="Jewish holiday pinned to a Gregorian date: the dates move every year.",
         fix="Compute from the Hebrew calendar instead of listing Gregorian dates.", route="shabbat-times / idf-date-converter"),
    # Privacy
    dict(id="priv-log-sensitive", family="privacy", severity="dynamic", ext=CODE_EXT,
         check=_log_sensitive,
         msg="Personal data sent to a log, analytics or error tracker.",
         fix="Log an internal id or a masked value; scrub at the logger, analytics or error-tracker hook.", route="israeli-privacy-shield"),
    dict(id="priv-preticked-consent", family="privacy", severity="medium", ext=CODE_EXT | MARKUP_EXT, scope="both",
         check=_preticked_consent,
         msg="Marketing consent defaults to true (pre-ticked). The Communications Law ad section requires the recipient's explicit prior consent, so a box the user never ticked is a risk.",
         fix="Default to false and record the user's own action (time, channel, wording). Whether a consent flow is legally sufficient is not decided by this review.", route="israeli-privacy-shield"),
    # Accessibility (code level)
    dict(id="a11y-html-lang-missing", family="a11y", severity="high", ext=MARKUP_EXT, scope="tag",
         check=_missing_attr(r"<html\b", r"\blang=", "<html> without lang"),
         msg="<html> without lang: screen readers pick the wrong voice for Hebrew.",
         fix='lang="he" on the Hebrew locale (lang="en" on English).', route="israeli-accessibility-compliance"),
    dict(id="a11y-lang-en-hebrew", family="a11y", severity="medium", ext=MARKUP_EXT, scope="tag",
         check=_cond(r"<html\b[^>]*lang=[\"']en", unless=r"\{|locale"),
         msg="Static lang=\"en\" on <html>: wrong for the Hebrew locale.",
         fix="Bind lang and dir to the active locale."),
    dict(id="a11y-placeholder-label", family="a11y", severity="low", ext=MARKUP_EXT, scope="tag",
         check=_placeholder_label,
         msg="Input with a placeholder and no linked label: a placeholder is not a label.",
         fix="Add <label htmlFor> (or aria-label) in Hebrew."),
    dict(id="a11y-arrow-keys-rtl", family="a11y", severity="medium", ext=SCRIPT_EXT,
         check=_arrow_key,
         msg="Arrow-key navigation hard-wired: in RTL, ArrowLeft should move to the NEXT item.",
         fix="Swap the handlers when the computed direction is rtl."),
]

BLIND_SPOTS = ("The scanner cannot see: values computed in other files or at runtime, framework defaults "
               "(a layout or i18n provider that sets dir/lang), CSS-in-JS built from variables, consumer price display "
               "(whether shown prices include VAT), data that reaches logs through helper functions, and anything outside the diff.")


def rule_applies(rule, path):
    return ext_of(path) in rule["ext"]


def apply_rule(rule, path, lineno, text, findings):
    try:
        res = rule["check"](text)
    except re.error:
        return
    if not res:
        return
    sev, detail, fix = rule["severity"], "", rule["fix"]
    if isinstance(res, tuple):
        sev, detail = res[0], res[1]
        if len(res) > 2:
            fix = res[2]
    elif isinstance(res, str):
        detail = res
    if sev == "dynamic":
        return
    code = re.sub(r"\s+", " ", text.strip()) if rule.get("scope") == "tag" else text.strip()
    findings.append({
        "file": path, "line": lineno, "rule": rule["id"], "family": rule["family"],
        "severity": sev, "message": rule["msg"] + (f" ({detail})" if detail else ""),
        "fix": fix, "route": rule.get("route"), "code": code[:160],
    })


def scan_file(path, lines, findings):
    """lines: list of (lineno, text, added)."""
    CTX["path"] = path
    CTX["file_text"] = "\n".join(t for _, t, _ in lines)
    line_rules = [r for r in RULES if rule_applies(r, path) and r.get("scope", "line") in ("line", "both")]
    tag_rules = [r for r in RULES if rule_applies(r, path) and r.get("scope") in ("tag", "both")]
    depth = 0  # open cn( / clsx( / cva( / twMerge( / className={ ... spanning lines
    sdepth, scall = 0, ""  # open crontab( / CronTrigger( / add_job( / from_crontab( / scheduled_job( spanning lines
    for lineno, text, added in lines:
        sm = re.search(r"(from_crontab|CronTrigger|add_job|scheduled_job|(?<![\w.])crontab)\(", text)
        if sm and sdepth <= 0:
            scall = sm.group(1)
            sdepth = text[sm.start():].count("(") - text[sm.start():].count(")")
            CTX["sched_call"] = scall
        elif sdepth > 0:
            CTX["sched_call"] = scall
            sdepth += text.count("(") - text.count(")")
        else:
            CTX["sched_call"] = ""
        CTX["class_ctx"] = depth > 0
        m = re.search(r"(\bcn|clsx|cva|twMerge|classNames)\(|className=\{", text)
        seg = text[m.start():] if m else (text if depth > 0 else "")
        if seg:
            depth = max(0, depth + seg.count("(") - seg.count(")"))
        if added and text.strip():
            for r in line_rules:
                apply_rule(r, path, lineno, text, findings)
    CTX["class_ctx"] = False
    CTX["sched_call"] = ""
    if tag_rules:
        for lineno, tag in extract_tags(lines):
            for r in tag_rules:
                apply_rule(r, path, lineno, tag, findings)


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _decode_git_path(target):
    target = target.split("\t")[0]
    if target.startswith('"') and target.endswith('"'):
        raw = codecs.escape_decode(target[1:-1].encode("ascii", "backslashreplace"))[0]
        target = raw.decode("utf-8", errors="replace")
    return target[2:] if target.startswith(("b/", "a/")) else target


def parse_diff(lines):
    files, order = {}, []
    path, new_line = None, 0
    for raw in lines:
        line = raw.rstrip("\n").rstrip("\r")
        if line.startswith("diff --git "):
            path = None
            continue
        if line.startswith("+++ "):
            target = line[4:].strip()
            path = None if target == "/dev/null" else _decode_git_path(target)
            if path and path not in files:
                files[path] = []
                order.append(path)
            continue
        if line.startswith("--- "):
            continue
        m = HUNK.match(line)
        if m:
            new_line = int(m.group(1))
            continue
        if path is None:
            continue
        if line.startswith("+"):
            files[path].append((new_line, line[1:], True))
            new_line += 1
        elif line.startswith("-") or line.startswith("\\"):
            continue
        else:
            files[path].append((new_line, line[1:] if line.startswith(" ") else line, False))
            new_line += 1
    return order, files


def scan_diff(lines):
    findings = []
    order, files = parse_diff(lines)
    for p in order:
        scan_file(p, files[p], findings)
    return findings, order


def scan_dir(root):
    findings, files = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = os.path.join(dirpath, name)
            if ext_of(name) not in ALL_EXT or name.endswith(".min.js") or name in ("package.json", "package-lock.json", "tsconfig.json"):
                continue
            try:
                with open(p, encoding="utf-8") as fh:
                    content = fh.read().split("\n")
            except (UnicodeDecodeError, OSError):
                continue
            rel = os.path.relpath(p, root)
            files.append(rel)
            scan_file(rel, [(i, t, True) for i, t in enumerate(content, 1)], findings)
    return findings, files


def dedupe(findings):
    seen, out = set(), []
    for f in findings:
        k = (f["file"], f["line"], f["rule"])
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def no_candidate_rules(files, findings):
    hit = {f["rule"] for f in findings}
    applicable = [r for r in RULES if any(rule_applies(r, f) for f in files)]
    return [r["id"] for r in applicable if r["id"] not in hit]


def run(lines=None, directory=None):
    """Library entry point used by the tests: returns (findings, files)."""
    findings, files = scan_dir(directory) if directory else scan_diff(lines)
    return dedupe(findings), files


def main():
    ap = argparse.ArgumentParser(description="Scan a unified diff or a directory for Israel-specific defects (RTL, Hebrew, IDs, money/dates, time zone, privacy, a11y). Candidates only: review every hit in context, and never treat a rule with no hits as 'clean'.")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--diff", help="unified diff file (default: read stdin)")
    src.add_argument("--dir", help="directory to scan (all lines, not just changes)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--min-severity", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--fail-on", choices=["low", "medium", "high"], help="exit 1 if any finding at or above this severity")
    ap.add_argument("--list-rules", action="store_true", help="print the rule table and exit")
    a = ap.parse_args()

    if a.list_rules:
        for r in RULES:
            print(f"{r['id']:26} {r['family']:12} {r['severity']:8} {r.get('scope', 'line'):5} {r['msg']}")
        return 0

    if a.dir:
        if not os.path.isdir(a.dir):
            print(f"error: not a directory: {a.dir}", file=sys.stderr)
            return 2
        findings, files = run(directory=a.dir)
    else:
        if a.diff:
            try:
                with open(a.diff, encoding="utf-8") as fh:
                    lines = fh.readlines()
            except OSError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
        else:
            if sys.stdin.isatty():
                print("error: pipe a unified diff on stdin, or pass --diff FILE or --dir PATH", file=sys.stderr)
                return 2
            lines = sys.stdin.readlines()
        if not any(l.startswith(("+++ ", "@@ ")) for l in lines):
            print("error: input does not look like a unified diff (no +++ or @@ lines)", file=sys.stderr)
            return 2
        findings, files = run(lines=lines)

    floor = SEVERITY_ORDER[a.min_severity]
    findings = [f for f in findings if SEVERITY_ORDER[f["severity"]] >= floor]
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["file"], f["line"], f["rule"]))
    quiet = no_candidate_rules(files, findings)

    if a.format == "json":
        print(json.dumps({"files": files, "findings": findings, "rules_with_no_candidates": quiet,
                          "not_a_clean_bill": BLIND_SPOTS}, ensure_ascii=False, indent=2))
    else:
        print(f"Scanned {len(files)} file(s); {len(findings)} candidate finding(s). Review each in context before reporting.\n")
        for f in findings:
            route = f"  -> {f['route']}" if f["route"] else ""
            print(f"{f['file']}:{f['line']}  [{f['severity'].upper()}] {f['rule']} ({f['family']}){route}")
            print(f"    {f['message']}")
            print(f"    code: {f['code']}")
            print(f"    fix:  {f['fix']}")
        print("\nRules with no candidates (NOT a clean bill; read the diff yourself before saying anything is clean):")
        print("  " + (", ".join(quiet) if quiet else "(none)"))
        print("\n" + BLIND_SPOTS)

    if a.fail_on and any(SEVERITY_ORDER[f["severity"]] >= SEVERITY_ORDER[a.fail_on] for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
