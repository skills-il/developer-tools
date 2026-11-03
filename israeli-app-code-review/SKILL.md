---
name: israeli-app-code-review
description: "Reviews a PR, diff or files of an app for Israeli users and returns a prioritized report of Israel-specific defects (severity, file and line, who breaks, the fix) plus a checked-and-clean list, catching what generic reviewers miss. Use when asked to review a PR or diff for Israeli users, RTL or Hebrew bugs, \"code review le-RTL\", or \"bdikat kod le-ivrit\". Covers RTL and bidi, Hebrew regex and normalisation, Teudat Zehut, phone and mikud fields, ILS and VAT, the Sunday to Thursday week, Asia/Jerusalem DST and cron, IDs or health data in logs, lang and labels. A bundled scanner gives line-accurate candidates. Do NOT use for building RTL from scratch (hebrew-rtl-best-practices), security review (israeli-appsec-scanner), full accessibility audit (israeli-accessibility-compliance), privacy compliance (israeli-privacy-shield), writing ID or phone validators (israeli-id-validator, israeli-phone-formatter), or general code review."
license: MIT
allowed-tools: Bash(python3:*) Bash(git:*) Read Grep
compatibility: "Python 3 for the optional scanner, no network. Chat-only hosts (Claude.ai, ChatGPT, Manus, Grok, Claude Desktop without a shell) and Gemini Spark use the inline route: the user pastes the diff and the agent applies references/rule-catalogue.md line by line."
---

# Israeli App Code Review

## Problem

A change can pass every test and every generic code review and still ship a checkout form that rejects Hebrew names, a phone field that renders backwards, a cron job that fires an hour late every summer, a VAT constant from 2024, or a log line that writes Teudat Zehut numbers next to clinic names. Reviewers outside Israel do not look for these, and most linters cannot see them. This skill reviews the change for exactly that class of defect and hands back a report a developer can act on line by line.

## What you need from the user

1. **The change.** One of: a PR (number or URL, and the agent has `git`/`gh`), a unified diff (`git diff main...HEAD`), or a set of files or a directory. On a chat host, ask the user to paste the diff. If they paste whole files instead, review them as files and say the report covers the whole file, not only the change.
2. **Who uses it.** Ask only if it is not obvious from the code: is the UI Hebrew-first, bilingual, or English with Israeli users? Is it consumer-facing (B2C) or business-only? Does it handle money, scheduling, IDs, health data or marketing messages? The answers decide which families matter most.
3. **Stack hints**, if visible: Tailwind version, the scheduler library, the logger and error tracker, the payment processor.

If the diff is larger than you can review carefully, say so and review the files that touch UI, money, dates, schedulers, validators, exports and logging first. List what you did not review.

## Instructions

### Step 1: Get candidates from the scanner, then read the diff yourself

Shell hosts:

```bash
git diff origin/main...HEAD | python3 scripts/il-review-scan.py
python3 scripts/il-review-scan.py --diff change.patch --format json
python3 scripts/il-review-scan.py --dir src/        # whole files, not just the change
```

In diff mode the scanner reads only ADDED lines and numbers them as in the NEW file, so `file:line` points at the right place in the PR. It joins multi-line JSX/HTML tags (one prop per line, comments inside `{}` skipped) before checking inputs, checkboxes and `<html>`, including JSX in `.js` files, and reads Tailwind variants (`md:pl-8`, `hover:ml-2`) and multi-line `cn(...)` class lists, treating `rtl:`/`ltr:` tokens as deliberate overrides.

**What the scanner cannot see**, and why its output never decides "clean": values computed in other files or at runtime, a layout or i18n provider that sets `dir`/`lang` outside the diff, CSS-in-JS built from variables, whether consumer-facing prices include VAT, personal data that reaches a log through a helper, and anything not in the diff. Its "rules with no candidates" line means "no pattern matched", nothing more.

Chat hosts and Gemini Spark: do the same pass by hand. Walk every added line against `references/rule-catalogue.md` and note `file:line` using the `+c` number in each `@@ -a,b +c,d @@` hunk header, counting only `+` and context lines.

Check: the scanner exits 2 if the input is not a unified diff. Ask for `git diff` output or the files.

### Step 2: Remove false positives in context

Open the surrounding code and drop or downgrade hits that do not hurt an Israeli user:

| Hit | Keep it when | Drop it when |
|-----|--------------|--------------|
| Physical CSS/Tailwind (`ml-*`, `margin-left`, `text-left`) | The component renders in the Hebrew UI | It is inside an element forced `dir="ltr"` (code block, phone field) |
| Directional icon | It means forward/back/next/previous | It is not directional (play, external link, check) |
| `0.18` / `1.17` | It multiplies a price | It is an opacity, an easing curve, a version |
| Bidi isolation | The value can be Latin, digits, a phone, an email or a URL | The value is always Hebrew text |
| Cron without zone | The job is meant to run at an Israeli local time | The scheduler's zone is set elsewhere (check where) |
| Logged field | The value reaches a log, analytics or error tracker | It is a variable name only and the value is masked first |

Check: every remaining item must name the user who breaks ("a customer whose ID starts with 0", "anyone on the Hebrew UI", "every order placed on a Sunday"). If you cannot name one, it is not a finding.

### Step 3: Read the diff for what patterns cannot see

Go through the diff family by family. This read, not the scanner, is what the "checked and clean" list reports on. The facts each check depends on are here; per-rule detail, fixes and usual false positives are in `references/rule-catalogue.md`.

**RTL and bidi**
- `margin-inline-start` maps to left or right by direction and `text-align: start` is left in LTR and right in RTL (MDN). Tailwind ships `ms-*`/`me-*`, `ps-*`/`pe-*`, `text-start`/`text-end` and `rtl:`/`ltr:` variants; the current docs name the logical inset utilities `inset-s-*`/`inset-e-*`, so check the installed version before naming a class. Look at responsive and state variants too, and at direction-sensitive utilities (`space-x-*`, a `translate-x-full` drawer, `origin-left`, gradient direction).
- An element with no `dir` inherits from its parent, and omitting `dir` does not turn on auto detection (MDN). If the layout is not in the diff, write "verify", not a finding.
- User input or external data needs `dir="auto"` or `<bdi>` (MDN). Numbers, phone numbers, email addresses and file names next to Hebrew spill over (W3C). In plain strings (SMS, push, email subject) wrap the value in U+2068 FIRST STRONG ISOLATE ... U+2069 POP DIRECTIONAL ISOLATE.
- Phone, email, URL, ID and company-number inputs need `dir="ltr"` on the input itself; `dir="rtl"` on a phone field is the same bug. `type="number"` is wrong for digit strings such as postal codes (MDN) and drops leading zeros.
- In an RTL interface forward arrows point left (Android guide). Arrow-key handlers on sliders and tabs must swap ArrowLeft and ArrowRight under RTL.

**Hebrew text**
- Letters are U+05D0 to U+05EA, a range that already includes the five final forms (U+05DA, U+05DD, U+05DF, U+05E3, U+05E5). Explicit letter lists like `[אבגד...ת]` usually forget them.
- Latin-only validators are the commonest checkout bug: `/^[a-zA-Z\s'-]+$/` on a name or address rejects every Hebrew name, and JavaScript `\w` matches only basic Latin letters, digits and underscore (MDN). Python 3 `\w` matches Unicode word characters, so in Python the same pattern keeps Hebrew letters.
- Niqqud runs U+05B0 to U+05C7 and cantillation U+0591 to U+05AF. An anchored `^[א-ת ]+$` rejects pointed text, geresh U+05F3, gershayim U+05F4 (ז׳קלין, ת״א), the ASCII apostrophe and the hyphen. A Python slug built with `re.sub(r"[^\w\s-]", "", title)` keeps the letters but strips gershayim, so ת״א becomes the word תא.
- Stripping marks with `[֑-ׇ]` also deletes punctuation inside that range, such as maqaf U+05BE. Strip `[֑-ׇֽֿׁׂׅׄ]`, after NFD when text may come from PDFs with presentation forms.
- Sorting needs `Intl.Collator('he')` or `localeCompare(b, 'he')`. Truncation should use `Intl.Segmenter` graphemes so a letter keeps its niqqud.
- CSV exports with Hebrew headers: write a UTF-8 BOM (Python `utf-8-sig`, which writes the BOM as a signature that helps detect the encoding; JavaScript `"﻿" + csv`). A Microsoft Q&A answer gives the BOM as the way to make Microsoft software recognise the file as UTF-8, which is how an accountant double-clicking the export in Excel sees Hebrew instead of mojibake.

**Israeli identifiers and payments**
- Teudat Zehut: nine digits, the last a Luhn check digit. Keep it a string, pad to nine, sum the digits of a doubled value above 9. Company numbers (ח.פ.) use the same check-digit rules, so the same string, padding and `dir="ltr"` points apply to `hp`/`companyId` fields. Point to `israeli-id-validator` for the reference implementation instead of rewriting it in the review.
- Phone: hand-rolled regexes and `+972` conversion go to `israeli-phone-formatter`. In review, flag the UI side (dir, input type, numeric storage).
- Mikud: seven digits since 1 February 2013. `maxLength={5}` or `\d{5}` rejects every valid code.
- Card numbers: a hand-rolled Luhn or length check written for international cards is a risk. Do not assert which local cards it rejects; tell the developer to confirm accepted formats in the payment processor's documentation and let the processor validate.

**Money, prices, numbers and dates**
- `toLocaleString()` / `toLocaleDateString()` without a locale use the runtime default (MDN). `Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' })` needs the currency passed (no default, MDN); its output contains U+200F marks, so compare tests against the formatter's own output.
- VAT is 18% from 01.01.2025 and was 17% until 31.12.2024 (Kol Zchut). A constant in a component is a maintainability defect even when right, and a live pricing bug when it is 17%, whether written `0.17`, `1.17` or `VAT_PERCENT = 17`. Re-pricing or crediting an OLD invoice must use the rate of the transaction date.
- Consumer price display: the Consumer Protection Law defines the total price to include VAT and compulsory payments (section 17א), and section 17ד bars publishing or quoting a price to a consumer unless it is the total price only, in Israeli currency. A consumer-facing page that shows net unit prices and adds VAT only at the end is a risk to flag; whether a page or a B2B flow is covered is for the business and its counsel, not this review.
- Agorot vs shekels: any `* 100` or `/ 100` between the UI and a payment provider is a possible 100x error; confirm the unit in the provider's docs.
- Dates: `MM/DD/YYYY` or a forced `en-US` shows month-first dates. `Intl.DateTimeFormat('he-IL')` is day-first.
- Week: CLDR has the Israeli week starting Sunday and the weekend on Friday and Saturday. In browsers that ship it, `new Intl.Locale('he-IL').getWeekInfo()` returns `firstDay: 7, weekend: [5, 6]`; some runtimes expose it as the `weekInfo` property instead (Node 20 does), so use `loc.getWeekInfo?.() ?? loc.weekInfo`. Library helpers assume Saturday+Sunday: date-fns `addBusinessDays` counts Monday to Friday and its `isWeekend` is Saturday or Sunday; NumPy's default weekmask is `'1111100'` (Monday to Friday). For Sunday to Thursday pass NumPy `weekmask='1111001'`. Whether Friday is a short business day is a product decision; ask.

**Time zone and scheduling**
- Standard time is UTC+2 (Time Determination Law, Section 2). DST is UTC+3 from the Friday before the last Sunday of March at 02:00 until the last Sunday of October at 02:00 (Section 3, the 2013 rule); from 2005 to 2012 it ended before Yom Kippur instead (tzdata). Any fixed `+02:00`, `GMT+2` or `Date.now() + 2 * 3600 * 1000` used as "Israel time" is wrong for part of every year. The fix is always the IANA zone `Asia/Jerusalem`.
- `Intl.DateTimeFormat` without `timeZone` uses the runtime's zone (MDN). Python `date.today()` is the server's local date. On a UTC server both, like `toISOString().slice(0, 10)`, give yesterday's date between midnight Israel time and 02:00 (03:00 in summer).
- pytz: passing a pytz zone as `tzinfo=` to the `datetime` constructor does not work for many zones (pytz README); for Asia/Jerusalem it yields the LMT offset `+02:21`. Use `IL.localize(...)` or `zoneinfo.ZoneInfo`.
- Django: `timezone.now()` is always UTC when `USE_TZ` is on, so `timezone.now().date()` is the UTC date; `timezone.localdate()` converts to the current zone, which is `TIME_ZONE` unless a zone is activated per request. `TIME_ZONE = "UTC"` on an Israeli product therefore renders SMS and email times 2 or 3 hours early.
- Scheduler zones: GitHub Actions schedules run in UTC unless a timezone is given; Vercel cron always runs in UTC; node-cron and APScheduler take a timezone option; Celery beat usually gets its zone from settings (`CELERY_TIMEZONE`), not from the job line, so read the settings file.
- Day-of-week numbering is NOT universal: crontab and node-cron use 0 or 7 for Sunday, Celery `crontab(day_of_week=...)` uses 0 for Sunday (so `0-4` is already Sunday to Thursday there), APScheduler 3.x treats 0 as Monday even in `from_crontab`, Quartz numbers Sunday as 1. Identify the library before judging a number, then give the Sunday to Thursday fix in that library's own form: system crontab `0-4` (Debian's Vixie cron documents that ranges or lists of names are not allowed, while cronie allows them, so numbers are the portable form); node-cron `0-4` or `sun-thu`; Celery `crontab(day_of_week="0-4")` (it also parses `"sun-thu"` as Sunday to Thursday); APScheduler 3.x `day_of_week="sun,mon,tue,wed,thu"` or `"mon-thu,sun"`, never `"sun-thu"`, because its names run mon..sun and the wrapping range raises `ValueError` at start-up (verified on APScheduler 3.11.0); Quartz `SUN-THU` or `1-5`; Vercel `0-4` (no names). Check the scheduler's own docs.
- After moving a job to Asia/Jerusalem (on the job or in settings): 02:00-02:59 does not exist on the spring-forward Friday and 01:00-01:59 happens twice on the last Sunday of October. APScheduler warns such periods may run more or less often; node-cron runs the repeated hour once. Nightly billing at 02:00 is the usual victim.
- Hardcoded Gregorian dates for Rosh Hashana, Pesach and the rest are wrong next year; route the data to `shabbat-times` or `idf-date-converter`.

**Privacy and marketing consent**
- Under the Privacy Protection Law an identification number makes a record personal data, and health status and salary or financial activity are "data of special sensitivity". Amendment 13 has been in force since 14 August 2025 and that category drives sanctions, DPO and notification duties (Privacy Protection Authority). Use this as background only: do not state in the report which duty applies to the user's organisation.
- Code-level risk: an ID, phone, email, clinic, diagnosis, salary or bank detail, or a whole request/order object (`payload.dict()`, `JSON.stringify(req.body)`), passed to a logger, analytics or an error tracker's user/context.
- Marketing consent: the Communications Law advertising section requires the recipient's explicit prior consent for ads by SMS, electronic message, fax or autodialer. A marketing checkbox that defaults to checked (`useState(true)`, `defaultChecked`, `default=True`) is a risk to flag; route the consent question to `israeli-privacy-shield`.

**Accessibility (code level only)**
- Regulation 35a of the Accessibility for Service Regulations requires internet services to follow Israeli Standard 5568 at level AA (applications are under regulation 35c). Secondary sources disagree on which WCAG version part 1 maps to and part 2 (documents) cites WCAG 2.0, so state no WCAG version for part 1.
- Flag only what the diff shows: `<html>` without `lang="he"` (screen readers choose pronunciation from `lang`, MDN), a static `lang="en"` on a Hebrew page, placeholder-only inputs, labels not linked to inputs, RTL arrow-key handling. The full audit and statement are `israeli-accessibility-compliance`.

### Step 4: Rank

| Severity | Use when |
|----------|----------|
| High | Wrong money, wrong time, rejected valid users, or personal data leaving the app. Ship-blocker. |
| Medium | Visible breakage for the Hebrew UI or a class of users, a defect that breaks on a known date, or a legal-risk pattern to route (VAT-exclusive consumer prices, pre-ticked consent). |
| Low | Polish, or risk that depends on data you cannot see. |

Merge duplicates: five physical classes in one component are one finding with five line numbers.

### Step 5: Write the report

Use the template in Output. Every finding has a `file:line`, who breaks, and a concrete fix. "Checked and clean" lists only families you READ in Step 3 and found nothing in, never a family the scanner was merely silent on. For privacy and accessibility write "no code-level pattern found in the diff", never "clean" or "compliant".

## Output

```markdown
**Israel-specific review: <PR title or branch>**

Scope: <N files, M added lines> | Reviewed with: scanner + manual read | Not reviewed: <files skipped>

**High**
1. **<short title>** `path/file.tsx:14`
   Breaks for: <who, when>
   Why: <one or two sentences with the rule>
   Fix: <code or exact change>

**Medium** ...

**Low** ...

**Checked and clean** (from the manual read, not the scanner)
- RTL root (dir/lang): <clean | not in diff, verify the layout>
- Hebrew regex and normalisation: <clean | n/a>
- Privacy: no code-level pattern found in the diff
- Accessibility: no code-level pattern found in the diff

**Not determinable from the diff**
- <facts the change depends on but does not show, e.g. whether stored prices include VAT>

**Out of scope / routed**
- Privacy-law and accessibility-regulation compliance: not determined by this review (israeli-privacy-shield / israeli-accessibility-compliance)
- Security: not reviewed (israeli-appsec-scanner)
- <Hebrew PDF invoices, HTML email rendering, legacy windows-1255 files: not reviewed, if present>
```

## Examples

Both diffs ship as `scripts/fixtures/example1-checkout.diff` and `scripts/fixtures/example2-scheduler.diff`; `python3 scripts/test_il_review_scan.py` reproduces the candidate counts below.

### Example 1: React + Tailwind checkout form

User says: "Review this PR, it adds the checkout form for our Israeli store." The diff adds `src/components/CheckoutForm.tsx` (VAT constant `0.17`, a `console.log` of `form.idNumber` and `form.phone`, Tailwind `text-left`/`mr-2`/`pl-3`/`ml-auto`, ID/phone/zip inputs, a shekel string, `toLocaleDateString()`, a `ChevronRight` "continue" button) and `src/lib/tz.ts` (`isValidTz(id: number)` with weights 1,2 and no digit sum).

The scanner returns 22 candidates. Step 2 keeps them; Step 3 adds the missing Luhn digit-sum and the unlinked label. Report:

```markdown
**Israel-specific review: feat/checkout-form**

Scope: 2 files, 32 added lines | Reviewed with: scanner + manual read

**High**
1. **VAT constant is the 2024 rate** `src/components/CheckoutForm.tsx:6`
   Breaks for: every order. 0.17 charges 17%; the rate has been 18% since 01.01.2025.
   Fix: read the rate from one config table keyed by effective date.
2. **Teudat Zehut and phone written to the console** `CheckoutForm.tsx:14`
   Breaks for: every customer: an ID number makes this personal data, and console output is often collected by logging tools.
   Fix: delete the line, or log an order id only.
3. **ID typed as number** `src/lib/tz.ts:1-2`
   Breaks for: anyone whose ID starts with 0: `String(id)` has 8 digits and line 3 rejects it.
   Fix: `id: string`, strip separators, `padStart(9, "0")`.
4. **Check digit computed without the digit sum** `src/lib/tz.ts:6`
   Breaks for: most valid IDs: Luhn sums the digits of a doubled value above 9 (14 -> 5).
   Fix: `let d = n * w; if (d > 9) d -= 9;`. Compare with israeli-id-validator.

**Medium**
5. **Physical Tailwind classes** `CheckoutForm.tsx:19, 20, 21, 22, 26, 27`: `text-start`, `me-2`, `ps-3`, `ms-auto`, `ms-1`.
6. **LTR fields without dir** `CheckoutForm.tsx:21, 22, 23`: digits and cursor jump in the RTL form. Fix: `dir="ltr"`.
7. **type="number" on the ID field** `CheckoutForm.tsx:21`: leading zeros lost. Fix: `type="text" inputMode="numeric"`.
8. **Five-digit postal code** `CheckoutForm.tsx:23`: mikud is seven digits. Fix: `maxLength={7}`, exactly 7 digits.
9. **Shekel amount by concatenation** `CheckoutForm.tsx:24`. Fix: `Intl.NumberFormat("he-IL", { style: "currency", currency: "ILS" })`.
10. **Date in the browser default locale** `CheckoutForm.tsx:25`. Fix: `toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" })`.

**Low**
11. **"Continue" chevron points right** `CheckoutForm.tsx:27`. Fix: `rtl:rotate-180` or ChevronLeft in Hebrew.
12. **Latin first name next to Hebrew** `CheckoutForm.tsx:24`. Fix: `<bdi>{user.firstName}</bdi>`.
13. **Labels** `CheckoutForm.tsx:20, 22, 23`: label not linked to the ID input; phone and mikud have placeholders only.

**Checked and clean** (manual read)
- Hebrew regex and normalisation: no Hebrew patterns in the change.
- Time zone and scheduling: no date arithmetic or cron in the change.
- Root dir/lang: layout not in the diff, verify `<html lang="he" dir="rtl">`.

**Not determinable from the diff**
- Whether `i.price` is net. If catalogue prices already include VAT, `CheckoutForm.tsx:11` applies it twice; if they are net, consumer pages must still show VAT-inclusive prices.

**Out of scope / routed**
- Privacy-law and accessibility-regulation compliance: not determined by this review (israeli-privacy-shield / israeli-accessibility-compliance)
- Security (payment handling): not reviewed (israeli-appsec-scanner)
```

### Example 2: Node scheduler for appointment reminders

User says: "Check this cron job before we merge, it sends SMS reminders to clinic patients." The diff adds `server/jobs/reminders.js`: a 2026 holiday list, `israelNow()` as `Date.now() + 2 * 60 * 60 * 1000`, a weekend check `day !== 0 && day !== 6` on a `toISOString()` date, `cron.schedule("0 7 * * 1-5", ...)` commented "09:00 Israel time", a `logger.info` with the patient's phone, Teudat Zehut and clinic, a Hebrew SMS template, and an SLA deadline built with `.toISOString().replace("Z", "+02:00")`.

The scanner returns 9 candidates; all survive review. Report:

```markdown
**Israel-specific review: reminders job**

Scope: 1 file, 26 added lines | Reviewed with: scanner + manual read

**High**
1. **Patient ID, phone and clinic in the application log** `server/jobs/reminders.js:22`
   Breaks for: every patient. An ID next to a clinic name can reveal health context, and health data is a special-sensitivity category under the Privacy Protection Law. Classifying this database is for israeli-privacy-shield.
   Fix: `logger.info("reminder sent", { appointmentId: a.id })`.
2. **"Israel now" by adding two hours** `reminders.js:8`
   Breaks for: every run between the Friday before the last Sunday of March and the last Sunday of October (UTC+3), and it creates a fake instant later code treats as real.
   Fix: keep `new Date()`; format with `timeZone: "Asia/Jerusalem"` where a local value is needed.
3. **UTC time relabelled as +02:00** `reminders.js:28`
   Breaks for: every SLA deadline: replacing `Z` does not shift the clock reading, so the string names an instant exactly 2 hours earlier than the real deadline in every season. In summer the offset shown is also not Israel's.
   Fix: return the ISO UTC string, or format in Asia/Jerusalem with the zone's real offset.

**Medium**
4. **Cron in the server zone, "09:00 Israel" only in winter** `reminders.js:17`
   Fix: `cron.schedule("0 9 * * sun-thu", job, { timezone: "Asia/Jerusalem" })` (node-cron accepts names; with numbers it uses 0 for Sunday).
5. **Monday to Friday schedule and Saturday/Sunday weekend check** `reminders.js:13, 17`
   Breaks for: Sunday appointments (no reminder) and Friday (reminders on the weekend). Ask whether the clinics work Fridays.
6. **Holiday dates hardcoded for one year** `reminders.js:5`: wrong from 2027. Fix: compute from the Hebrew calendar (shabbat-times / idf-date-converter).
7. **Date key from toISOString()** `reminders.js:13`: runs between midnight and 02:00/03:00 Israel time see yesterday. Fix: `Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d)`.

**Low**
8. **Clinic name and time inside a Hebrew SMS** `reminders.js:23`: wrap each value in U+2068 ... U+2069.

**Checked and clean** (manual read)
- RTL/CSS, Hebrew regex, identifiers, money: not present in the change.
- DST window: the job runs at 09:00, outside 01:00-02:59.

**Out of scope / routed**
- Privacy-law compliance (logging policy, database classification): not determined by this review (israeli-privacy-shield)
```

## Bundled Resources

### Scripts
- `scripts/il-review-scan.py`: stdlib-only scanner for unified diffs (stdin or `--diff`) or directories (`--dir`). Joins multi-line tags, parses Tailwind variants, decodes git's quoted non-ASCII paths; `--format json`, `--min-severity`, `--fail-on` for CI, `--list-rules`. Run: `python3 scripts/il-review-scan.py --help`
- `scripts/test_il_review_scan.py`: regression tests over `scripts/fixtures/` (both examples plus checkout, Python service and false-positive fixtures). Run after changing any rule.

### References
- `references/rule-catalogue.md`: every rule id with what it catches, the fix and its usual false positives, plus the inline route for chat hosts. Consult when unsure whether a hit is real.
- `references/domain-checklist.md`: the coverage contract with sources and the known-bad figures. Consult before signing off "checked and clean".

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Time Determination Law (Hebrew Wikisource) | https://he.wikisource.org/wiki/חוק_קביעת_הזמן | The DST rule in section 3 |
| Kol Zchut, VAT | https://www.kolzchut.org.il/he/מס_ערך_מוסף_(מע%22מ) | Current VAT rate and its effective date |
| Consumer Protection Law (Hebrew Wikisource) | https://he.wikisource.org/wiki/חוק_הגנת_הצרכן | Sections 17א and 17ד on total price |
| Privacy Protection Authority, Amendment 13 guidance | https://www.gov.il/BlobFolder/legalinfo/the_board_role/en/Role_of_the_Board.pdf | In-force date and the special-sensitivity category |
| Accessibility for Service Regulations | https://he.wikisource.org/wiki/תקנות_שוויון_זכויות_לאנשים_עם_מוגבלות_(התאמות_נגישות_לשירות) | Regulation 35a level and scope |
| APScheduler 3.x cron trigger | https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html | Weekday numbering and DST behaviour |

## Gotchas

- Agents report "checked and clean" for every rule the scanner was silent on. The scanner is pattern-based; only the manual read of Step 3 supports a clean line.
- Agents treat `[א-ת]` as "missing the final letters". It does not miss them: U+05D0 to U+05EA contains them. The real bugs are explicit letter lists, Latin-only validators, and validators that reject niqqud and geresh.
- Agents "fix" a hardcoded `+02:00` by changing it to `+03:00`, or by adding a DST check. The only fix is the IANA zone.
- Agents give `0-4` as the universal Sunday to Thursday cron fix, or flag every `0-4` as wrong. It is right in system crontab, node-cron and Celery, Monday to Friday in APScheduler 3.x, and wrong in Quartz. Names do not rescue it either: `sun-thu` crashes APScheduler 3.x and is not documented for Debian's crontab. Identify the library (follow the call across lines: a Celery `crontab(` or an APScheduler `add_job(` often spans several) and use its own form.
- Agents rewrite the Teudat Zehut, phone or card validator inside the review. Report the defect and route it (israeli-id-validator, israeli-phone-formatter, the payment processor's docs).

## Troubleshooting

### Scanner prints "input does not look like a unified diff"
Cause: the input has no `+++` or `@@` lines (a pasted PR page, a `git log`, or a file).
Solution: run `git diff base...head > change.patch`, or use `--dir` to scan files.

### Line numbers do not match the PR view
Cause (verified on our fixtures): the diff was generated against a different base than the PR, or with `--word-diff`/`--color`. The scanner counts from the `+c` value of each hunk header.
Solution: regenerate with `git diff --no-color origin/main...HEAD`.

### A file with a Hebrew name is missing from the scan
Cause: the file's extension is not one the scanner reads (the list is `ALL_EXT` near the top of the script). Git's quoted non-ASCII paths (`"b/\327\242..."`) are decoded, so a Hebrew file name alone is not the cause.
Solution: review that file by hand with references/rule-catalogue.md, or add its extension to the rule families that apply.
