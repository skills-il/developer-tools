# Domain Coverage Checklist: israeli-app-code-review

Generated: 2026-11-02, revised 2026-11-03 after expert, judge and legal review. Aggregator sweep: W3C Internationalization articles (inline bidi markup), MDN reference index for CSS logical properties and the Intl API, the Unicode Hebrew block charts, IANA tzdata `asia` (Israel section), CLDR week data, Kol Zchut (VAT), Hebrew Wikisource statute texts (Time Determination Law, Accessibility for Service Regulations), and the Privacy Protection Authority publications on gov.il.

Scope: reviewing a CHANGE (pull request, diff, or a set of files) in an app that serves Israeli users, for defects that are specific to Israeli users. Not a general code review, not a security review, not a full accessibility or privacy audit.

## Must cover (core)

### RTL and bidi
- [ ] Physical CSS box properties (`margin-left/right`, `padding-left/right`, `left:`/`right:`, `border-left/right`, `border-*-radius` corners) where the logical property is meant. Source: MDN margin-inline-start, MDN logical properties guide. Why core: every physical side is on the wrong side in `dir="rtl"`.
- [ ] `text-align: left|right` instead of `start|end`. Source: MDN text-align (`start` maps to left in LTR and right in RTL).
- [ ] Tailwind physical utilities, including behind responsive and state variants (`md:pl-8`, `hover:ml-2`) (`ml-*`, `mr-*`, `pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`, `text-right`, `rounded-l-*`, `border-l-*`), plus direction-sensitive ones (`space-x-*`, `translate-x-*` drawers, `origin-left`, gradient direction), where `ms-*`/`me-*`/`ps-*`/`pe-*`/`text-start`/`text-end` and the `rtl:`/`ltr:` variants exist. Source: tailwindcss.com docs margin, padding, text-align, states pages.
- [ ] Inset utilities named per the installed Tailwind version (current docs name `inset-s-*`/`inset-e-*`). Source: tailwindcss.com top-right-bottom-left page. Version-dependent, so check the project's installed version.
- [ ] Missing `dir` on `<html>`, and missing `lang="he"`. Source: MDN dir (no `dir` means inherit from parent; omitting `dir` does not enable auto detection), MDN lang (assistive technology pronunciation).
- [ ] User-generated or external text rendered without bidi isolation (`<bdi>`, `dir="auto"`, `unicode-bidi: isolate`). Source: MDN bdi, MDN dir (`auto` for unknown-direction data), MDN unicode-bidi.
- [ ] Spillover: a number, phone, email, URL or Latin brand name next to Hebrew renders in the wrong order. Source: W3C inline bidi markup article (spillover effects; phone numbers, email addresses, file names).
- [ ] Phone, email, URL, ID and company-number inputs inside an RTL form without `dir="ltr"` (or with `dir="rtl"`), including multi-line JSX tags, and `type="number"` used for phone, ID or postal code. Source: MDN input number (not for postal codes or values that only consist of digits), MDN input tel (no automatic format validation).
- [ ] Directional icons (forward/back arrows, chevrons) that should mirror. Source: Android developer guide on layout mirroring ("forward arrows pointing to the left").
- [ ] Keyboard arrow-key handling on carousels/sliders/tabs that assumes ArrowRight means "next". (structural, how to reason) Derived from the mirroring rule above.

### Hebrew text handling
- [ ] Explicit Hebrew letter classes that omit the five final forms (ך ם ן ף ץ). Source: Unicode chart U+0590 (finals are separate code points).
- [ ] `[א-ת]` / `א-ת` validators that reject niqqud (points U+05B0 to U+05C7) and cantillation (U+0591 to U+05AF), and geresh/gershayim (U+05F3, U+05F4) used in names and abbreviations. Source: Unicode chart U+0590.
- [ ] Search normalisation that does not strip marks (NFD, then drop U+0591 to U+05C7) and does not fold finals to base letters when the feature is fuzzy search. Source: MDN String.prototype.normalize, Unicode chart.
- [ ] Presentation forms (U+FB1D to U+FB4F) pasted from PDFs. Source: Unicode chart U+FB00.
- [ ] Collation: `localeCompare` / `Intl.Collator` without `he`. Source: MDN Intl.Collator.
- [ ] Truncation by code-unit length cuts a letter from its niqqud; use grapheme segmentation. Source: MDN Intl.Segmenter.
- [ ] Latin-only validators on names and addresses (`[a-zA-Z]`, JavaScript `\w`) reject every Hebrew name. Source: MDN character classes (JS `\w` is basic Latin), Python re docs (Python 3 `\w` is Unicode).
- [ ] Slugs/filenames: JavaScript ASCII-only regexes erase Hebrew titles; Python `[^\w\s-]` keeps letters but strips niqqud and gershayim. Source: same two docs.
- [ ] CSV exports with Hebrew headers written without a UTF-8 BOM. Source: Python codecs (utf-8-sig BOM as an encoding signature), Microsoft Q&A answer (BOM makes Microsoft software recognise UTF-8).

### Israeli identifiers (route depth to sibling skills)
- [ ] Teudat Zehut: nine digits, Luhn check digit; stored as a string (leading zeros), padded before the check. Source: Wikipedia Israeli identity card. Route algorithm detail to `israeli-id-validator`.
- [ ] Company numbers (ח.פ.) use the same check-digit rules as the ID number, so the same string/padding/dir points apply to `hp`/`companyId` fields. Source: Hebrew Wikipedia, תאגיד. Route to `israeli-id-validator`.
- [ ] Card numbers: hand-rolled Luhn or length checks written for international cards. No primary source was found for which local cards fail them, so the review routes the question to the payment processor's documentation instead of asserting it.
- [ ] Phone numbers: hand-rolled regexes and E.164 conversion. Route to `israeli-phone-formatter`.
- [ ] Mikud is seven digits since 2013; five-digit validators reject valid codes. Source: Wikipedia Postal codes in Israel.

### Money, numbers, dates
- [ ] `toLocaleString()` / `toLocaleDateString()` with no locale uses the runtime default. Source: MDN Number.toLocaleString.
- [ ] ILS via `Intl.NumberFormat('he-IL', {style:'currency', currency:'ILS'})`; currency has no default and must be passed. Source: MDN Intl.NumberFormat constructor.
- [ ] Hardcoded VAT rate. Current rate 18% from 01.01.2025; 17% until 31.12.2024. Source: Kol Zchut VAT page.
- [ ] Temporal (C.1a): re-computing VAT on a 2024 document with today's constant is wrong; the rate follows the transaction date. Source: Kol Zchut VAT page (the two date-bounded rates).
- [ ] Agorot vs shekel unit confusion between the UI and the payment provider API (100x). (structural) Check the provider's API docs.
- [ ] Day-first dates; hand-built `MM/DD/YYYY`. (structural, verify by running `Intl.DateTimeFormat('he-IL')`)
- [ ] Week: first day Sunday, weekend Friday and Saturday. Source: CLDR weekData (IL firstDay sun, weekendStart fri, weekendEnd sat); MDN Intl.Locale getWeekInfo (some runtimes, Node 20 included, expose it as the `weekInfo` property).
- [ ] Business-day libraries that assume Saturday+Sunday: date-fns `addBusinessDays` (Monday to Friday) and `isWeekend`; NumPy busday default weekmask `'1111100'`. Source: date-fns source on unpkg, NumPy docs.
- [ ] Consumer price display: total price includes VAT (Consumer Protection Law section 17א) and section 17ד bars quoting a price to a consumer other than the total price in Israeli currency. Flag as a risk on consumer-facing pages; coverage is not decided by the review. Source: Hebrew Wikisource.

### Time zone
- [ ] Current DST rule: from the Friday before the last Sunday of March at 02:00 to the last Sunday of October at 02:00, UTC+3; standard time UTC+2. Source: Time Determination Law section 3 (Hebrew Wikisource), IANA tzdata `Rule Zion 2013 max`.
- [ ] Temporal (C.1a): the current rule dates from 2013; 2005 to 2012 used a different end date (before Yom Kippur). Code that re-implements DST arithmetic is wrong for historical timestamps. Source: tzdata `asia` comments and rules.
- [ ] Hardcoded `+02:00` / `+03:00` / `GMT+2` / `timedelta(hours=2)`. Source: same.
- [ ] Cron and schedulers running in UTC or server-local time while the business rule is Israel local time. Source: MDN DateTimeFormat timeZone (default is the runtime's time zone); GitHub Actions docs (UTC by default, optional IANA timezone); Vercel docs (always UTC, no day names); node-cron README (timezone option).
- [ ] Day-of-week numbering differs by scheduler: system crontab and node-cron 0 or 7 = Sunday (name ranges are not allowed in Debian's Vixie cron, allowed in cronie and node-cron), Celery crontab 0 = Sunday (Celery docs), APScheduler 3.x 0 = Monday even in from_crontab, Quartz 1 = Sunday. Fix in the library's own form: APScheduler 3.x needs `sun,mon,tue,wed,thu` (a `sun-thu` range raises ValueError, verified locally on 3.11.0). Source: node-cron README, APScheduler 3.x docs, Quartz tutorial, Celery docs.
- [ ] DST gap and overlap after moving a job to Asia/Jerusalem: 02:00-02:59 missing on the spring-forward Friday, 01:00-01:59 repeated on the last Sunday of October. Source: Time Determination Law section 3 (both switches at 02:00), APScheduler 3.x DST warning, node-cron README (repeated hour runs once).
- [ ] Django: `timezone.now()` is always UTC with USE_TZ, so `.date()`/`strftime` give the UTC date; `TIME_ZONE = "UTC"` renders local times in UTC unless a zone is activated. Source: Django utils and time-zone docs.
- [ ] Python: pytz zone passed as `tzinfo=` yields the LMT offset (+02:21); naive `date.today()` / `datetime.now()` is the server's local date. Source: pytz README, tzdata Asia/Jerusalem LMT line, Python datetime docs.
- [ ] Hardcoded Jewish holiday dates. Route to `shabbat-times` / `idf-date-converter`. (structural)

### Privacy
- [ ] Teudat Zehut, phone, email, health, salary or financial data written to logs, analytics or error trackers. Source: Privacy Protection Law unofficial translation (identification number makes data personal data; health status and salary/financial activity are data of special sensitivity).
- [ ] Amendment 13 in force 14 August 2025; the special-sensitivity category drives sanctions, DPO appointment and notification duties. Source: PPA guidance on the board's role (English PDF).
- [ ] Whole objects logged (`payload.dict()`, `JSON.stringify(req.body)`), not only named fields. (structural)
- [ ] Marketing consent defaulting to checked. Communications Law section 30א requires explicit prior consent for ads by SMS, electronic message, fax or autodialer. Source: Hebrew Wikisource. Flag as a risk and route.
- [ ] Route the compliance programme to `israeli-privacy-shield`; report privacy as "no code-level pattern found", never "clean".

### Accessibility (code level only)
- [ ] Regulation 35a requires the IS 5568 guidelines at level AA for internet services (apps handled under 35c). Source: Accessibility for Service Regulations on Hebrew Wikisource.
- [ ] Missing `lang`, inputs with placeholder but no label, arrow-key semantics in RTL widgets. Source: MDN lang.
- [ ] Route full audit and accessibility statement to `israeli-accessibility-compliance`.

## Should cover (advanced / edge cases)
- [ ] `:dir()` selector and `scaleX(-1)` for mirroring icons in CSS. Source: MDN.
- [ ] RLM (U+200F) in `Intl.NumberFormat('he-IL')` currency output breaks naive string comparison in tests. (verify by running; output observed in Node 2026-11-02)
- [ ] Hebrew PDF invoices (bidi shaping), Hebrew HTML email rendering, legacy windows-1255 files: listed as "not reviewed" when present; no rule. (structural)
- [ ] Git's quoted non-ASCII paths in diffs are decoded by the scanner. (structural)
- [ ] WCAG version behind IS 5568 part 1 is reported inconsistently in secondary sources; part 2 (documents) cites WCAG 2.0. Do not assert a version for part 1; point to the SII standard page.

## Out of scope (explicit, with rationale)
- Designing or implementing RTL from scratch: `hebrew-rtl-best-practices`.
- OWASP/security review (injection, auth, secrets): `israeli-appsec-scanner`.
- Full accessibility audit and accessibility statement: `israeli-accessibility-compliance`.
- Privacy compliance programme (DPO, database registration, policies): `israeli-privacy-shield`.
- Writing ID or phone validators: `israeli-id-validator`, `israeli-phone-formatter`.
- Holiday and Shabbat calendar data: `shabbat-times`, `idf-date-converter`.
- General code review unrelated to Israeli users.

## Known bad figures
- "Israel DST ends before Yom Kippur": true only for 2005 to 2012; since 2013 it ends on the last Sunday of October.
- VAT 17%: outdated since 01.01.2025.
- Five-digit mikud: superseded by seven digits in 2013.
- "0-4 is Sunday to Thursday in any cron": false for APScheduler 3.x (Monday to Friday) and Quartz; true for system crontab, node-cron and Celery (Celery also accepts "sun-thu").
- "Relabelling a UTC string as +02:00 is 2 hours off in winter and 3 in summer": the instant is always exactly 2 hours early; only the displayed offset is additionally wrong in summer.

## Authoritative sources
- https://he.wikisource.org/wiki/חוק_קביעת_הזמן (DST rule, section 3)
- https://raw.githubusercontent.com/eggert/tz/main/asia (Israel rules, history)
- https://www.kolzchut.org.il/he/מס_ערך_מוסף_(מע%22מ) (VAT rate and date)
- https://www.gov.il/BlobFolder/legalinfo/the_board_role/en/Role_of_the_Board.pdf (Amendment 13 in-force date)
- https://www.gov.il/BlobFolder/legalinfo/legislation/en/Protection-of-Privacy-Law57411981unofficialtranslatioup.pdf (definitions)
- https://he.wikisource.org/wiki/תקנות_שוויון_זכויות_לאנשים_עם_מוגבלות_(התאמות_נגישות_לשירות) (regulation 35a)
- https://www.unicode.org/charts/PDF/U0590.pdf, https://www.unicode.org/charts/PDF/UFB00.pdf
- https://he.wikisource.org/wiki/חוק_הגנת_הצרכן (sections 17א, 17ד)
- https://he.wikisource.org/wiki/חוק_התקשורת_(בזק_ושידורים) (section 30א)
- https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html (weekday numbering, DST)
- MDN, Python, NumPy, date-fns, pytz, GitHub, Vercel and node-cron pages listed in evidence.json
