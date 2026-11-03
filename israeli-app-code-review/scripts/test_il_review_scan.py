#!/usr/bin/env python3
"""Regression tests for il-review-scan.py against the shipped fixtures.

Run: python3 scripts/test_il_review_scan.py   (exit 0 = all pass)

Each fixture lists findings that MUST appear (file, line, rule[, severity]) and
findings that must NOT appear (known false positives fixed in round 2).
The two example fixtures reproduce the counts quoted in SKILL.md.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("scan", os.path.join(HERE, "il-review-scan.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

CASES = {
    "example1-checkout.diff": {
        "count": 22,
        "must": [
            ("src/components/CheckoutForm.tsx", 6, "fmt-vat-hardcoded", "high"),
            ("src/components/CheckoutForm.tsx", 14, "priv-log-sensitive", "high"),
            ("src/lib/tz.ts", 1, "id-numeric-storage", "high"),
            ("src/components/CheckoutForm.tsx", 21, "id-number-input", "medium"),
            ("src/components/CheckoutForm.tsx", 23, "id-mikud-five", "medium"),
            ("src/components/CheckoutForm.tsx", 27, "rtl-directional-icon", "low"),
        ],
        "must_not": [
            ("src/components/CheckoutForm.tsx", 3, "rtl-directional-icon"),   # import line
            ("src/components/CheckoutForm.tsx", 23, "rtl-bidi-isolation"),    # maxLength={5}
        ],
    },
    "example2-scheduler.diff": {
        "count": 9,
        "must": [
            ("server/jobs/reminders.js", 8, "tz-hardcoded-offset", "high"),
            ("server/jobs/reminders.js", 22, "priv-log-sensitive", "high"),
            ("server/jobs/reminders.js", 28, "tz-hardcoded-offset", "high"),
            ("server/jobs/reminders.js", 17, "tz-cron-dow", "medium"),
            ("server/jobs/reminders.js", 17, "tz-cron-no-zone", "medium"),
            ("server/jobs/reminders.js", 13, "tz-utc-date-key", "medium"),
        ],
        "must_not": [("server/jobs/reminders.js", 11, "fmt-business-day-lib")],
    },
    "regress-fe.diff": {
        "must": [
            ("src/app/checkout/CheckoutPage.tsx", 5, "fmt-vat-hardcoded", "high"),     # MAAM_PERCENT = 17
            ("src/app/checkout/CheckoutPage.tsx", 9, "fmt-vat-hardcoded", "high"),     # net * 1.17
            ("src/app/checkout/CheckoutPage.tsx", 10, "fmt-business-day-lib", None),
            ("src/app/checkout/CheckoutPage.tsx", 11, "priv-preticked-consent", None),
            ("src/app/checkout/CheckoutPage.tsx", 14, "heb-latin-only-validator", "high"),
            ("src/app/checkout/CheckoutPage.tsx", 15, "pay-handrolled-card", None),
            ("src/app/checkout/CheckoutPage.tsx", 21, "rtl-tailwind-physical", None),  # md:pl-8 lg:text-left
            ("src/app/checkout/CheckoutPage.tsx", 22, "rtl-tailwind-directional", None),
            ("src/app/checkout/CheckoutPage.tsx", 33, "id-number-input", None),        # multi-line tag
            ("src/app/checkout/CheckoutPage.tsx", 33, "rtl-input-ltr-content", None),
            ("src/app/checkout/CheckoutPage.tsx", 40, "rtl-input-ltr-content", None),  # dir="rtl"
            ("src/app/checkout/CheckoutPage.tsx", 40, "a11y-placeholder-label", None), # id but no label
            ("src/app/checkout/CheckoutPage.tsx", 42, "id-number-input", None),        # name="hp"
            ("src/app/checkout/CheckoutPage.tsx", 43, "rtl-tailwind-physical", None),  # sm:mr-4
            ("src/app/checkout/CheckoutPage.tsx", 52, "rtl-tailwind-directional", None),
            ("src/app/layout.tsx", 11, "rtl-html-dir-missing", None),
        ],
        "must_not": [
            ("src/app/layout.tsx", 11, "a11y-html-lang-missing"),   # lang on the next line
            ("src/app/checkout/CheckoutPage.tsx", 1, "rtl-directional-icon"),
        ],
    },
    "regress-be.diff": {
        "must": [
            ("orders/service.py", 46, "tz-pytz-tzinfo", "high"),
            ("orders/service.py", 47, "tz-naive-today", None),
            ("orders/service.py", 48, "fmt-vat-hardcoded", None),
            ("orders/service.py", 50, "priv-log-sensitive", None),   # payload.dict()
            ("orders/service.py", 59, "fmt-vat-hardcoded", None),    # Decimal("1.18")
            ("orders/service.py", 62, "heb-csv-no-bom", None),
            ("orders/service.py", 69, "rtl-bidi-isolation", None),
            ("orders/service.py", 72, "heb-ascii-slug", None),
            ("orders/service.py", 74, "tz-cron-dow", "high"),        # APScheduler from_crontab 0-4
            ("orders/service.py", 75, "tz-cron-no-zone", None),
            ("orders/service.py", 75, "tz-cron-dow", "high"),        # APScheduler day_of_week="sun-thu" raises ValueError
            ("orders/service.py", 78, "id-numeric-storage", "high"),
        ],
        "must_not": [
            ("orders/service.py", 51, "priv-log-sensitive"),   # tz = time zone
            ("orders/service.py", 54, "id-handrolled-tz"),     # order.id % 10
            ("orders/service.py", 64, "heb-class-missing-finals"),  # list literal
            ("orders/service.py", 79, "id-numeric-storage"),   # quantity IntegerField
        ],
    },
    "regress-t.diff": {
        "must": [("src/x.ts", 2, "fmt-vat-hardcoded", "high"), ("src/x.ts", 3, "fmt-vat-hardcoded", "high")],
        "must_not": [("src/x.ts", 1, "heb-class-missing-finals"), ("src/x.ts", 4, "fmt-weekend-sat-sun")],
    },
    "regress2-apos.diff": {
        "must": [
            ("src/components/ContactForm.tsx", 4, "rtl-input-ltr-content", None),   # email, apostrophe in a // comment
            ("src/components/ContactForm.tsx", 4, "a11y-placeholder-label", None),
            ("src/components/ContactForm.tsx", 13, "id-number-input", None),
        ],
        "must_not": [("src/components/ContactForm.tsx", 4, "id-number-input")],
    },
    "regress2-django-celery.diff": {
        "must": [
            ("clinic/settings.py", 43, "tz-django-utc-setting", None),
            ("clinic/settings.py", 51, "tz-dst-window", None),             # zone set in settings, hour=2
            ("appointments/tasks.py", 15, "tz-django-utc-date", None),
            ("appointments/tasks.py", 36, "tz-django-utc-date", None),
            ("appointments/tasks.py", 28, "priv-log-sensitive", "high"),
            ("appointments/models.py", 10, "id-numeric-storage", "high"),
        ],
        "must_not": [("clinic/settings.py", 49, "tz-cron-dow")],          # Celery 0-4 is Sunday to Thursday
    },
    "regress2-next-action.diff": {
        "must": [
            ("app/[locale]/checkout/actions.ts", 11, "heb-latin-only-validator", "high"),  # Hebrew error message
            ("app/[locale]/checkout/actions.ts", 12, "id-numeric-storage", None),          # z.coerce.number()
            ("app/[locale]/checkout/actions.ts", 14, "id-mikud-five", None),               # .length(5)
            ("app/[locale]/checkout/actions.ts", 16, "priv-preticked-consent", None),      # zod default(true)
            ("app/[locale]/checkout/actions.ts", 31, "fmt-weekend-sat-sun", None),         # [0, 6].includes
            ("app/[locale]/checkout/CheckoutForm.tsx", 33, "priv-preticked-consent", None),# multi-line checkbox
            ("app/[locale]/checkout/CheckoutForm.tsx", 11, "fmt-price-excl-vat", None),
            ("app/[locale]/checkout/CheckoutForm.tsx", 15, "id-number-input", None),
        ],
        "must_not": [],
    },
    "regress2-stress.diff": {
        "must": [
            ("src/components/PhoneField.tsx", 4, "rtl-input-ltr-content", None),
            ("src/components/PhoneField.tsx", 21, "rtl-input-ltr-content", None),   # {/* don't ... */} inside the tag
            ("src/components/PhoneField.tsx", 30, "rtl-tailwind-physical", None),   # multi-line cn(
            ("src/components/PhoneField.tsx", 34, "priv-preticked-consent", None),
            ("src/pages/Checkout.js", 4, "id-number-input", None),                  # JSX in .js
            ("app/layout.tsx", 6, "rtl-html-dir-missing", "low"),                   # spread attrs: one LOW verify
        ],
        "must_not": [("app/layout.tsx", 6, "a11y-html-lang-missing"), ("src/components/PhoneField.tsx", 43, "id-number-input")],
    },
    "regress2-heb.diff": {
        "must": [("src/\u05e2.ts", 1, "fmt-vat-hardcoded", "high"), ("src/\u05e2.ts", 2, "fmt-weekend-sat-sun", None)],
        "must_not": [],
    },
    "regress3-aps-weekmask.diff": {
        "must": [
            ("jobs.py", 3, "tz-cron-dow", "high"),            # sun-thu crashes APScheduler 3.x
            ("jobs.py", 6, "fmt-business-day-lib", None),     # default Mon-Fri weekmask
            ("jobs.py", 7, "fmt-business-day-lib", None),     # explicit Mon-Fri weekmask
        ],
        "must_not": [
            ("jobs.py", 4, "tz-cron-dow"),                    # sun,mon,tue,wed,thu is correct
            ("jobs.py", 5, "tz-cron-dow"),                    # mon-thu,sun is correct
            ("jobs.py", 8, "fmt-business-day-lib"),           # weekmask 1111001 is already Sun-Thu
            ("jobs.py", 9, "tz-cron-dow"),                    # Celery 0-4 is Sun-Thu
        ],
    },
    "regress3-fe.diff": {
        "must": [
            ("app/checkout/CheckoutForm.tsx", 38, "rtl-input-ltr-content", None),   # zip: no dir
            ("app/checkout/CheckoutForm.tsx", 43, "rtl-tailwind-physical", None),
            ("app/checkout/actions.ts", 32, "priv-log-sensitive", "high"),
        ],
        "must_not": [
            ("app/checkout/CheckoutForm.tsx", 59, "rtl-directional-icon"),         # already rtl:/ltr: handled
            ("app/checkout/CheckoutForm.tsx", 12, "id-number-input"),              # name field, comment + regex in tag
            ("app/checkout/CheckoutForm.tsx", 46, "priv-preticked-consent"),       # unchecked checkbox
        ],
    },
    "regress3-fe2.diff": {
        "must": [
            ("src/Contact.tsx", 6, "rtl-input-ltr-content", None),
            ("src/Contact.tsx", 22, "id-number-input", None),
            ("src/Contact.tsx", 24, "priv-preticked-consent", None),
        ],
        "must_not": [("src/Contact.tsx", 12, "id-number-input"), ("src/Contact.tsx", 12, "priv-preticked-consent")],
    },
    "regress3-fe3.diff": {
        "must": [
            ("src/Contact.tsx", 6, "rtl-input-ltr-content", None),      # comment between attributes
            ("src/Contact.tsx", 6, "a11y-placeholder-label", None),
            ("src/Contact.tsx", 13, "id-number-input", None),
        ],
        "must_not": [("src/Contact.tsx", 6, "id-number-input")],
    },
    "regress3-be.diff": {
        "must": [
            ("svc/scheduler.py", 11, "tz-cron-dow", "high"),   # from_crontab("... sun-thu") crashes
            ("svc/scheduler.py", 12, "tz-cron-dow", "high"),   # from_crontab 0-4 is Mon-Fri
            ("svc/scheduler.py", 16, "tz-cron-dow", "high"),   # multi-line add_job day_of_week="0-4"
            ("clinic/settings.py", 23, "tz-cron-dow", "medium"),  # Celery 1-5 is Mon-Fri
        ],
        "must_not": [
            ("clinic/settings.py", 18, "tz-cron-dow"),         # multi-line Celery crontab(sun-thu) is Sun-Thu
            ("clinic/settings.py", 27, "tz-cron-dow"),         # Celery 0-4
            ("svc/scheduler.py", 10, "tz-cron-dow"),           # sun,mon,tue,wed,thu
        ],
    },
    "regress2-vercel.diff": {
        "must": [("vercel.json", 2, "tz-cron-no-zone", None)],
        "must_not": [],
    },
}


def main():
    failures = 0
    for name, case in CASES.items():
        with open(os.path.join(HERE, "fixtures", name), encoding="utf-8") as fh:
            findings, _ = scan.run(lines=fh.readlines())
        got = {(f["file"], f["line"], f["rule"]): f["severity"] for f in findings}
        for fpath, line, rule, sev in case.get("must", []):
            k = (fpath, line, rule)
            if k not in got:
                print(f"FAIL {name}: missing {k}")
                failures += 1
            elif sev and got[k] != sev:
                print(f"FAIL {name}: {k} severity {got[k]} != {sev}")
                failures += 1
        for fpath, line, rule in case.get("must_not", []):
            if (fpath, line, rule) in got:
                print(f"FAIL {name}: false positive {(fpath, line, rule)}")
                failures += 1
        if "count" in case and len(findings) != case["count"]:
            print(f"FAIL {name}: {len(findings)} findings, expected {case['count']}")
            failures += 1
    # APScheduler findings must print the APScheduler form of the fix, never a sun-thu range
    for name in ("regress3-aps-weekmask.diff", "regress-be.diff", "regress3-be.diff"):
        with open(os.path.join(HERE, "fixtures", name), encoding="utf-8") as fh:
            findings, _ = scan.run(lines=fh.readlines())
        aps = [f for f in findings if f["rule"] == "tz-cron-dow" and "APScheduler" in f["message"]]
        if not aps:
            print(f"FAIL {name}: no APScheduler tz-cron-dow finding")
            failures += 1
        for f in aps:
            if "sun-thu" in f["fix"].lower() or "sun,mon,tue,wed,thu" not in f["fix"]:
                print(f"FAIL {name}:{f['line']}: APScheduler fix text is wrong: {f['fix']}")
                failures += 1
    print("all tests passed" if not failures else f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
