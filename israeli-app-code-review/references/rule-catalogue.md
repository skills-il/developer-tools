# Rule catalogue: israeli-app-code-review

The rules `scripts/il-review-scan.py` applies, for the inline route (chat hosts) and for judging hits. Severity is the default ("by context" means the rule picks high, medium or low from what it matched); SKILL.md Step 4 can move a finding once you know who breaks. Facts behind each rule, with sources, are in SKILL.md Step 3 and in `domain-checklist.md`.

Scope column: `line` rules read one physical line; `tag` rules read a whole markup tag, joined across lines when Prettier puts one prop per line (comments and regex literals are skipped, and joining stops at the next line that opens a tag); `both` rules run in both passes.

A rule with no hits is not evidence that a family is clean. Only the manual read in SKILL.md Step 3 supports a "checked and clean" line.

## RTL and bidi

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `rtl-css-physical-box` | medium | line | Physical left/right box property: lands on the wrong side under dir=rtl. | Use margin-inline-start/end, padding-inline-*, border-inline-* (or marginInlineStart in style objects). | Inside an element forced to dir="ltr"; already paired with a [dir=rtl] override. |
| `rtl-css-physical-inset` | low | line | Physical left/right offset in a stylesheet. | Use inset-inline-start / inset-inline-end unless the element must stay on that physical side. | A toast or badge that must stay on one physical side by design. |
| `rtl-text-align-physical` | medium | line | text-align left/right does not follow direction. | Use text-align: start / end. | Numeric table columns deliberately right-aligned in both directions. |
| `rtl-tailwind-physical` | medium | line | Physical Tailwind utility (variant prefixes such as md: included): lands on the wrong side under dir=rtl. | ml/mr -> ms/me, pl/pr -> ps/pe, text-left/right -> text-start/end, rounded-l -> rounded-s, left/right -> the logical inset utility of your Tailwind version; or pair it with an rtl: override. | Element is dir="ltr" (code, phone). Tokens with rtl:/ltr: for the same property are already skipped. |
| `rtl-tailwind-directional` | low | line | Direction-sensitive Tailwind utility (space-x, translate-x drawer, origin, gradient direction) with no rtl: counterpart in the class list. | Check it under dir=rtl: add rtl:space-x-reverse, rtl:-translate-x-full, or the mirrored origin/gradient, per your Tailwind version's docs. | Direction already handled by a parent or a dir-aware component; check your Tailwind version's docs for space-x behaviour. |
| `rtl-directional-icon` | low | line | Directional icon: forward/back arrows should point the other way in RTL. | Mirror with an rtl: variant, :dir(rtl) { transform: scaleX(-1) }, or swap the icon by direction. Do NOT mirror icons that are not directional (play, check, clock). | Non-directional icons. Import lines and icons already carrying rtl:/ltr: variants, :dir() or scaleX(-1) are skipped. |
| `rtl-input-ltr-content` | medium | tag | Phone/email/URL/ID/company-number input that is not dir="ltr": digits and Latin text reorder inside an RTL form. | Set dir="ltr" on the input itself (keep the label RTL). | The input inherits dir="ltr" from a wrapper. |
| `rtl-bidi-isolation` | low | line | Hebrew string with an interpolated value: numbers, phones, emails or Latin names can spill over and reorder. | Wrap the value in <bdi> (or an element with dir="auto"); in plain strings (SMS, push, email subject) wrap it with U+2068 ... U+2069. | The interpolated value is always Hebrew, or always digits with no adjacent punctuation. |
| `rtl-html-dir-missing` | high | tag | <html> without dir: the page renders LTR. | Set dir="rtl" (and lang="he") on <html> for the Hebrew locale. | dir set at runtime by i18n code (check the rendered HTML). |

## Hebrew text

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `heb-class-missing-finals` | high | line | Explicit Hebrew letter class omits final letters: words ending in them fail. | Use the range \u05D0-\u05EA (it includes the finals) or add the missing letters. | A class that deliberately matches only non-final letters (rare: say why). List/array literals are skipped. |
| `heb-range-no-niqqud` | medium | line | Anchored Hebrew-only validator rejects text with niqqud, geresh or gershayim (names like ז׳קלין, abbreviations like ת״א). | Accept marks [\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7], geresh/gershayim \u05F3\u05F4, apostrophe, hyphen and maqaf, or normalise first. | Input is normalised (marks stripped) before the test. |
| `heb-latin-only-validator` | high | line | Latin-only validator on a name or address: every Hebrew (and Arabic or Russian) name is rejected. JavaScript \w is ASCII-only too. | Accept Hebrew letters and marks (\u05D0-\u05EA plus the mark set), or use a Unicode letter class (\p{L} with the u flag) and validate length instead of script. | A field that is genuinely Latin-only by contract (an English-only username, an IBAN). |
| `heb-ascii-slug` | by context | line | Slug/filename sanitiser that mangles Hebrew titles. | Keep \u05D0-\u05EA and decide what geresh/gershayim become (percent-encode in URLs), or fall back to an id when the slug is empty. | Slug built from an ASCII field (SKU, English title). |
| `heb-collation-no-locale` | low | line | localeCompare without a locale uses the runtime default. | localeCompare(b, 'he') or a shared new Intl.Collator('he'). | Comparing ASCII identifiers. |
| `heb-truncate-codeunits` | low | line | Truncating by code units can split a letter from its niqqud. | Truncate on graphemes: [...new Intl.Segmenter('he', {granularity: 'grapheme'}).segment(s)]. | Text guaranteed unpointed and the cut is display-only. |
| `heb-normalize-strip-maqaf` | medium | line | Mark-stripping range also deletes punctuation inside it (maqaf U+05BE, paseq, sof pasuq, nun hafukha). | Strip only the marks: [\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7] (after NFD if presentation forms may appear). | Code that strips marks AND knowingly drops Hebrew punctuation. |
| `heb-csv-no-bom` | by context | line | CSV export without a UTF-8 BOM: Hebrew headers and names can open as mojibake when the file is double-clicked in Excel. | Python: encoding="utf-8-sig". JavaScript: prepend "\uFEFF" to the CSV text. | Machine-to-machine exports read by a parser, not by Excel. |

## Israeli identifiers and payments

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `id-numeric-storage` | high | line | ID, company number, phone or postal code stored or typed as a number: leading zeros vanish. | Keep it a string (CharField/varchar); validate digits with a regex and pad IDs to 9 before the check digit. | Surrogate database ids. Only ID/company/phone/postal names are matched. |
| `id-number-input` | medium | tag | type=number for an ID, company number, phone or postal code: drops leading zeros, adds spinners, accepts e and -. | Use type="text" (or tel) with inputMode="numeric" and a pattern. | A real quantity field. |
| `id-handrolled-tz` | medium | line | Hand-rolled Teudat Zehut / company-number check: verify padding to 9 digits and the Luhn digit-sum step. | Compare against the reference implementation in israeli-id-validator. Route: israeli-id-validator. | Calls into a shared, tested validator. |
| `id-mikud-five` | medium | line | Five-digit postal code check: Israeli mikud has been seven digits since 2013. | Accept exactly 7 digits (string). | Non-Israeli postal code fields. |
| `id-handrolled-phone` | medium | line | Hand-rolled Israeli phone pattern. | Check prefixes, lengths and +972 handling against israeli-phone-formatter. Route: israeli-phone-formatter. | Pattern that only strips separators. |
| `pay-handrolled-card` | medium | line | Hand-rolled card-number check (Luhn or a length floor written for international cards). | Do not assume every card your Israeli processor accepts passes this check. Confirm the accepted formats in the processor's documentation and let the processor (or its hosted fields) validate. | Client-side hint only, with the processor doing the real validation. |

## Money, numbers, dates

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `fmt-tolocale-no-locale` | medium | line | toLocale*() with no locale: output follows the server or browser default, not he-IL. | Pass 'he-IL' (and timeZone: 'Asia/Jerusalem' for dates). | Server logs meant for developers. |
| `fmt-currency-concat` | medium | line | Shekel amount built by string concatenation: symbol side, separators and bidi marks are left to chance. | new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(amount). | Display of a value already formatted by Intl. |
| `fmt-vat-hardcoded` | by context | line | Hardcoded VAT rate. 17% (in any notation) is outdated (until 31.12.2024); 18% applies from 01.01.2025, and the applicable rate follows the transaction date. | Read the rate from one config/table keyed by effective date; never re-price old invoices with today's constant. | Opacity, easing, scale and version numbers are skipped; check other 0.17/1.18 constants by name. |
| `fmt-price-excl-vat` | medium | line | Price labelled as excluding VAT. On a consumer-facing page this is a risk under the Consumer Protection Law (total price only); on a B2B page it may be intended. | Show the VAT-inclusive total price to consumers; keep net prices for business-only flows and say which one the page is. | B2B pages, quotes and invoices for businesses, where net prices are intended. |
| `fmt-us-date` | medium | line | US month-first date format or en-US locale in Israeli-facing output. | Format with Intl.DateTimeFormat('he-IL', ...) or an explicit dd/MM/yyyy pattern. | A US-locale branch of a bilingual app. |
| `fmt-weekend-sat-sun` | medium | line | Weekend logic that treats Saturday+Sunday as the weekend: in Israel the weekend is Friday+Saturday and Sunday is a working day. | Use a locale table (Intl.Locale 'he-IL' week info, CLDR: firstDay 7, weekend [5,6]) or an explicit Israeli business calendar. | Correct Israeli checks (JS getDay 5/6, Python weekday 4/5) are not flagged; code that models a non-Israeli market. |
| `fmt-business-day-lib` | medium | line | Library business-day helper: date-fns counts Monday to Friday and NumPy's default weekmask is Monday to Friday, so Sunday is skipped and Friday counted. | Pass an Israeli week (NumPy weekmask='1111001', Sunday to Thursday) or use a helper with a configurable weekend and holidays. | A NumPy/pandas call that already passes weekmask '1111001' (Sunday to Thursday) is skipped; calls with an explicit Israeli weekend option elsewhere. |
| `fmt-agorot-units` | low | line | x100 or /100 on a money value: confirm which side uses agorot and which uses shekels. | Name the unit in the variable (amountAgorot) and check the payment provider's API docs for its unit. | Percent arithmetic unrelated to money units. |

## Time zone and scheduling

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `tz-hardcoded-offset` | high | line | Fixed UTC offset for Israel: wrong for part of every year (UTC+2 standard, UTC+3 from the Friday before the last Sunday of March to the last Sunday of October). | Use the IANA zone Asia/Jerusalem (Intl timeZone option, Python zoneinfo, or your date library's zone support). | A fixed offset for another country. Plain durations (TTL, SLA windows) are flagged only next to time-zone words. |
| `tz-pytz-tzinfo` | high | line | pytz zone passed as tzinfo= to a datetime constructor: you get the zone's first (LMT) offset, +02:21 for Asia/Jerusalem. | IL.localize(datetime(...)), or use zoneinfo.ZoneInfo('Asia/Jerusalem') with tzinfo=. | tzinfo=pytz.utc (safe). |
| `tz-naive-today` | medium | line | Naive local date/time: on a UTC server, between midnight Israel time and 02:00 (03:00 in summer) it is still yesterday. | datetime.now(ZoneInfo('Asia/Jerusalem')).date() when the business date is Israeli. | Servers configured to run in Asia/Jerusalem (check the deployment, not the code). |
| `tz-django-utc-date` | medium | line | Django timezone.now() is always UTC when USE_TZ is on, so .date()/strftime() gives the UTC date: from midnight Israel time until 02:00 (03:00 in summer) it is still yesterday. | timezone.localdate() (or localtime(now).strftime) with TIME_ZONE or the activated zone set to Asia/Jerusalem. | Code that deliberately wants the UTC date (storage partitions). |
| `tz-django-utc-setting` | medium | line | Django TIME_ZONE = "UTC": localtime(), localdate() and template dates render in UTC unless a zone is activated per request, so times shown to Israeli users (SMS, emails, pages) are 2 or 3 hours early. | TIME_ZONE = "Asia/Jerusalem" for an Israeli product (storage stays UTC with USE_TZ), or timezone.activate('Asia/Jerusalem') where messages are rendered. | Projects that activate Asia/Jerusalem per request (check middleware) or render times only on the client. |
| `tz-cron-no-zone` | medium | line | Schedule with no time zone: it runs in the scheduler's zone (often UTC), so an Israeli local-time job drifts by 2 or 3 hours. | Set the scheduler's time zone option to Asia/Jerusalem, or keep UTC and document both DST cases. | Interval jobs (hour * or */n) are skipped; scheduler zone set elsewhere (check). |
| `tz-cron-dow` | by context | line | Day-of-week field in a schedule. | Sunday to Thursday per library: system crontab 0-4 (Debian Vixie cron documents no name ranges); node-cron 0-4 or sun-thu; Celery crontab 0-4 (0 = Sunday); APScheduler 3.x day_of_week='sun,mon,tue,wed,thu' or 'mon-thu,sun' (NOT 'sun-thu', which raises ValueError); Quartz SUN-THU or 1-5; Vercel 0-4 (no names). Check the scheduler's own docs. | Celery crontab numbers are not flagged unless 1-5 (Celery uses 0 = Sunday and parses sun-thu); the library is followed across a multi-line call; numeric fields the developer checked against the scheduler's docs. |
| `tz-dst-window` | medium | line | Asia/Jerusalem schedule between 01:00 and 02:59: 02:00-02:59 does not exist on the spring-forward Friday and 01:00-01:59 happens twice on the last Sunday of October. | Move the job out of that window, or schedule in UTC, or confirm how this scheduler handles a skipped and a repeated hour. | Jobs where running twice or not at all is harmless (idempotent cache warmers). |
| `tz-utc-date-key` | medium | line | Calendar date taken from toISOString(): that is the UTC date, so from midnight Israel time until 02:00 (03:00 in summer) it is still yesterday. | new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jerusalem' }).format(d) gives YYYY-MM-DD in Israel time. | Keys meant to be UTC dates (storage partitions). |
| `tz-dst-handrolled` | high | line | Hand-rolled Israeli DST logic: the 2013 rule differs from 2005-2012 (ended before Yom Kippur), so history breaks even if today works. | Delete it and let tzdata (Asia/Jerusalem) decide. | Test fixtures that assert tzdata output. |
| `tz-holiday-literal` | medium | line | Jewish holiday pinned to a Gregorian date: the dates move every year. | Compute from the Hebrew calendar instead of listing Gregorian dates. Route: shabbat-times / idf-date-converter. | Test fixtures; a generated table refreshed from a calendar source. |

## Privacy and consent

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `priv-log-sensitive` | by context | line | Personal data sent to a log, analytics or error tracker. | Log an internal id or a masked value; scrub at the logger, analytics or error-tracker hook. Route: israeli-privacy-shield. | Value masked before the call; `tz` meaning time zone is not matched. |
| `priv-preticked-consent` | medium | both | Marketing consent defaults to true (pre-ticked). The Communications Law ad section requires the recipient's explicit prior consent, so a box the user never ticked is a risk. | Default to false and record the user's own action (time, channel, wording). Whether a consent flow is legally sufficient is not decided by this review. Route: israeli-privacy-shield. | A transactional (non-marketing) setting that happens to be named updates or opt-in (service reminders are not advertising). |

## Accessibility (code level)

| Rule id | Severity | Scope | What it catches | Fix | Usual false positive |
|---|---|---|---|---|---|
| `a11y-html-lang-missing` | high | tag | <html> without lang: screen readers pick the wrong voice for Hebrew. | lang="he" on the Hebrew locale (lang="en" on English). Route: israeli-accessibility-compliance. | lang set at runtime by the framework (check the rendered HTML). |
| `a11y-lang-en-hebrew` | medium | tag | Static lang="en" on <html>: wrong for the Hebrew locale. | Bind lang and dir to the active locale. | English-only pages. |
| `a11y-placeholder-label` | low | tag | Input with a placeholder and no linked label: a placeholder is not a label. | Add <label htmlFor> (or aria-label) in Hebrew. | Input wrapped inside its <label> element. |
| `a11y-arrow-keys-rtl` | medium | line | Arrow-key navigation hard-wired: in RTL, ArrowLeft should move to the NEXT item. | Swap the handlers when the computed direction is rtl. | Handler already reads the computed direction. |
## Manual-only checks (no scanner rule)

- Consumer price display: a consumer-facing page showing prices without VAT (Consumer Protection Law sections 17א and 17ד). Flag as a risk; coverage is for the business and its counsel.
- Day-of-week numbering in schedulers the scanner cannot recognise: confirm each scheduler's numbering in its docs (system crontab, node-cron and Celery 0 = Sunday, APScheduler 3.x 0 = Monday, Quartz 1 = Sunday; name ranges are not portable in system crontab).
- Personal data that reaches a log through a helper function defined elsewhere.
- `dir`/`lang` set by a layout or i18n provider outside the diff.
- A scheduler time zone set in settings (Celery `CELERY_TIMEZONE`, Django `TIME_ZONE`) and used by jobs in other files.
- Model `__str__` or helper output that carries names or IDs into a log line.

## Inline route (no shell)

1. Split the pasted diff by `+++ b/<path>` headers.
2. For each `@@ -a,b +c,d @@` hunk, start a counter at `c`. A `+` line gets the counter and increments it; a context line (leading space) increments it; a `-` line does not.
3. For markup, read each tag from `<` to its closing `>` even when it spans lines, and report it on the line where it opens.
4. Match each `+` line (and each tag) against the rows above for that file type, then continue with SKILL.md Step 2 and Step 3.
