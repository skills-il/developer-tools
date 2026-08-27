# n8n Version Migration: 2.x Security Line, 3.0 Readiness, Israeli Hosting

Companion to `SKILL.md` Step 6. Everything here is version-sensitive; re-check the npm
dist-tags (`https://registry.npmjs.org/-/package/n8n/dist-tags`) and the advisory feed
(`https://api.github.com/advisories?ecosystem=npm&affects=n8n`) before trusting a pin.

## n8n 2.x Security Patches and Breaking Changes

n8n 2.0 shipped in December 2025; current stable is 2.36.7 as of August 2026 (beta on 2.37.x, new minor most weeks). Pin a specific tag in production, never `n8nio/n8n:latest`.

**CRITICAL security patch (pin >= 2.32.1).** Three CRITICAL vulnerabilities were disclosed 2026-05-14 and patched in 2.22.1:

| CVE | GHSA | Impact |
|-----|------|--------|
| CVE-2026-44789 | GHSA-c8xv-5998-g76h | HTTP Request node pagination prototype pollution **to RCE** |
| CVE-2026-44790 | GHSA-57g9-58c2-xjg3 | Arbitrary file read via Git node |
| CVE-2026-44791 | GHSA-wrwr-h859-xh2r | XML node prototype pollution patch bypass |

CVE-2026-44789 sits on this skill's critical path: every Israeli integration here is an HTTP Request node. Further HIGH-severity fixes landed through 2.31.5 and 2.32.1 (credential exfiltration via shared workflows, cross-tenant credential takeover, expression sandbox escapes), so **2.32.1 is the practical minimum**. No advisory published since patches above 2.32.1, so the floor is unchanged; 2.36.7 is the current stable and is what you should actually run.

Two earlier issues are often cited and frequently misdescribed:

- **CVE-2026-21858 ("Ni8mare", CVSS 10.0), published 2026-01-07** is unauthenticated **file access** via improper webhook request handling, not RCE. It affects 1.65.0 through 1.120.x only and was patched in 1.121.0. **The 2.x line was never affected**, so it is not a reason to pin any 2.x version.
- **CVE-2026-27493 (CVSS 9.5) + CVE-2026-27577 (CVSS 9.4), published 2026-02-25** are the pair that motivates the 2.10.1 floor: unauthenticated expression injection via Form nodes plus an expression sandbox escape to RCE, affecting <1.123.22, 2.0.0-2.9.2 and 2.10.0, patched in 1.123.22 / 2.9.3 / 2.10.1. That floor is now superseded by the 2.32.1 requirement above.

Any public Webhook node (every payment-gateway workflow in this skill) widens the exposure of all of these.

Key n8n 2.0 changes affecting Israeli workflows:

| Change | Impact | Action |
|--------|--------|--------|
| Code-node `$env` access blocked by default | Every `$env.BANK_PASS` / `$env.WEBHOOK_HMAC_SECRET` read returns nothing | Set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` on the runner, or pass the secret in from a preceding node. NOT the credential store: the Code node declares none |
| `require()` restricted in Code nodes | `require('crypto')` and `require('israeli-bank-scrapers')` both fail | Set `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL` |
| Execute Command node disabled by default | Bank-scraper workflows using Execute Command break | Use Code node, or re-enable via `NODES_EXCLUDE` |
| Save/Publish model | Workflows must be explicitly published | Publish after import or creation |
| Task runner isolation for Code nodes | Code runs in isolated sandboxes | Set the module vars on the **runner**, not the main container |
| Python Code node rebuilt on task runners | Pyodide-based Python removed; native Python needs runners in external mode | Set up external-mode task runners, or use JavaScript |
| MySQL/MariaDB support removed | Cannot use them as n8n backend DB | Migrate to PostgreSQL or SQLite |

**Code node module access.** n8n disables `require()` for external modules unless the variable is set, and this skill needs both:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

Without the first, the HMAC webhook verifier in `references/webhook-auth-patterns.md` throws on `require('crypto')`. Without the second, the bank-scraper Code node throws on `require('israeli-bank-scrapers')`. **If task runners are enabled (the default in 2.0), set these on the task runner, not on the main n8n container** or they have no effect.

**Code node secrets.** `N8N_BLOCK_ENV_ACCESS_IN_NODE` defaults to `true` in 2.x, so `$env.*` inside a Code node returns nothing. The credential store cannot substitute, because the Code node's node description declares no credentials, so there is no `$credentials` there. Either set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` on the task runner, pass the secret in from a preceding credential-bearing node (accepting that it lands in execution data), or use external secrets on enterprise.

To re-enable Execute Command, override `NODES_EXCLUDE` so it no longer contains `n8n-nodes-base.executeCommand` (empty list works), then restart n8n:

```
NODES_EXCLUDE="[]"
```

There is no `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE` variable (a common hallucination). Enabling Execute Command lets anyone with workflow edit access run arbitrary shell, so use only in trusted single-user deployments. Code nodes remain the recommended path.

## Preparing for n8n 3.0 (October 2026)

n8n 3.0 is scheduled for October 2026 and its breaking-changes page is already published. Four items hit this skill directly:

- **Self-hosting will require Docker.** `npm` / `npx n8n` installs will no longer be supported, so the Compose file below becomes the only supported shape.
- **The Function, Function Item and Item Lists nodes are removed.** Older Israeli workflows built before the Code node will not import. Migrate Function to Code, and Item Lists to Split Out / Aggregate / Sort / Limit / Remove Duplicates / Summarize.
- **The `$getPairedItem` expression helper is removed.** Use `pairedItem` or `$("<node name>").item`.
- **AI Agent node v1 is removed**, along with the SQL, Conversational, OpenAI Functions, Plan-and-Execute and ReAct agent modes. Everything in Step 7 should be built on the current Tools Agent, not on a legacy mode.

Also removed: workflow import from URL in the editor, and the Compression node limits drop sharply. Audit for these before upgrading, not after.

## Israeli Cloud Options

| Provider | Data Residency | Notes |
|----------|---------------|-------|
| AWS (il-central-1) | Israel (Tel Aviv) | Full Docker support, region GA |
| Azure (Israel Central) | Israel | `israelcentral` region |
| Google Cloud (me-west1) | Israel (Tel Aviv) | Launched 2022 |
| Kamatera | Israel (Petah Tikva) | VPS + Docker, Israeli company, NIS billing |
| ActiveCloud / HQserv / MedOne | Israel | VPS + Docker, Hebrew support |

Israel's Privacy Protection Authority (PPA) does not mandate that all data stay in Israel, but restricts transfers to countries without adequate data protection. For workflows processing PII (teudat zehut, bank, medical), choose an Israeli DC or verify destination adequacy on the PPA's approved list.



## Docker Compose for Self-Hosted n8n

```yaml
services:
  n8n:
    # Must be >= 2.32.1 for the CVE-2026-44789/44790/44791 critical chain. 2.36.7 is current stable.
    image: n8nio/n8n:2.36.7
    restart: unless-stopped
    ports: ["5678:5678"]
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
```

Notes:
- n8n 1.0+ uses built-in user management; old `N8N_BASIC_AUTH_*` vars are removed. n8n prompts for an owner account on first launch.
- Set both `GENERIC_TIMEZONE=Asia/Jerusalem` AND `TZ=Asia/Jerusalem`. Without these, Schedule Trigger nodes default to UTC and Shabbat calculations drift 2-3 hours. Israeli DST runs Friday-before-last-Sunday-of-March through last Sunday of October.
- Never run `:latest` in production after the 2026 CVE chain. Pin the tag and update via controlled redeploy.
- If Code nodes need `require()` or `$env`, add `NODE_FUNCTION_ALLOW_BUILTIN`, `NODE_FUNCTION_ALLOW_EXTERNAL` and (only if needed) `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` to the task-runner service rather than here.



---

# גרסאות n8n: קו האבטחה של 2.x, היערכות ל-3.0, ואירוח בישראל

## שינויים משמעותיים ב-n8n 2.0 (דצמבר 2025) + עדכוני אבטחה (2026)

גרסה n8n 2.0 שוחררה בדצמבר 2025; הגרסה היציבה הנוכחית היא 2.36.7 נכון לאוגוסט 2026 (בטא על 2.37.x, עם minor חדש כמעט כל שבוע). נעלו תג ספציפי בפרודקשן במקום `n8nio/n8n:latest`.

**טלאי אבטחה קריטי, חובה לעבור ל-2.32.1 לפחות.** שלוש חולשות ברמת CRITICAL פורסמו ב-14.5.2026 ותוקנו ב-2.22.1:

| CVE | GHSA | השפעה |
|-----|------|-------|
| CVE-2026-44789 | GHSA-c8xv-5998-g76h | זיהום prototype במנגנון ה-pagination של HTTP Request node, שמוביל ל-RCE |
| CVE-2026-44790 | GHSA-57g9-58c2-xjg3 | קריאת קבצים שרירותית דרך צומת Git |
| CVE-2026-44791 | GHSA-wrwr-h859-xh2r | עקיפת הטלאי לזיהום prototype בצומת XML |

חולשת CVE-2026-44789 נמצאת בדיוק על הנתיב הקריטי של הסקיל הזה, מפני שכל אינטגרציה ישראלית כאן היא HTTP Request node. תיקונים נוספים ברמת HIGH נחתו לאורך 2.31.5 ו-2.32.1 (דליפת credentials דרך workflows משותפים, השתלטות על credentials בין דיירים, ובריחה מארגז החול של הביטויים), ולכן **2.32.1 היא רצפת המינימום המעשית** ו-2.36.7 היא הגרסה היציבה הנוכחית.

שתי חולשות מוקדמות יותר מצוטטות הרבה ולרוב מתוארות לא נכון:

- **חולשת CVE-2026-21858 ("Ni8mare", CVSS 10.0), שפורסמה ב-7.1.2026,** היא **גישה לקבצים** ללא אימות דרך טיפול שגוי בבקשות webhook, ולא RCE. היא נוגעת לגרסאות 1.65.0 עד 1.120.x בלבד ותוקנה ב-1.121.0. **קו 2.x מעולם לא היה פגיע**, ולכן היא אינה סיבה לנעול גרסת 2.x כלשהי.
- **חולשות CVE-2026-27493 (CVSS 9.5) ו-CVE-2026-27577 (CVSS 9.4), שפורסמו ב-25.2.2026,** הן הצמד שממנו נגזרה רצפת 2.10.1: הזרקת ביטויים ללא אימות דרך צמתי Form, ובריחה מארגז החול של הביטויים עד כדי RCE. הן נוגעות לגרסאות 1.123.22>, 2.0.0 עד 2.9.2, ו-2.10.0, ותוקנו ב-1.123.22 / 2.9.3 / 2.10.1. הרצפה הזו מוחלפת כעת בדרישת 2.32.1.

כל Webhook ציבורי (כל זרימת תשלום בסקיל הזה חושפת אחד) מרחיב את החשיפה לכל אלה. נעלו את התג ב-`docker-compose.yml` ועקבו אחרי פיד האבטחה של n8n.

n8n 2.0 הביא שינויים משמעותיים שמשפיעים על תהליכים ישראליים:

| שינוי | השפעה | פעולה נדרשת |
|-------|-------|------------|
| גישה ל-`$env` מתוך Code node חסומה כברירת מחדל | כל קריאת `$env.BANK_PASS` או `$env.WEBHOOK_HMAC_SECRET` מחזירה ריק | הגדרת `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` על ה-runner, או העברת הסוד מצומת קודם. לא credential store: ל-Code node אין כזה |
| שימוש ב-`require()` מוגבל ב-Code nodes | גם `require('crypto')` וגם `require('israeli-bank-scrapers')` נכשלים | הגדרת `NODE_FUNCTION_ALLOW_BUILTIN` ו-`NODE_FUNCTION_ALLOW_EXTERNAL` |
| Execute Command node מושבת כברירת מחדל | תהליכי סריקת בנקים שמשתמשים ב-Execute Command ישברו | מעבר ל-Code node (שלב 2), או הפעלה מחדש דרך משתנה הסביבה `NODES_EXCLUDE` (ראו למטה) |
| מודל שמירה/פרסום | תהליכים חייבים להתפרסם מפורשות כדי לפעול | פרסום תהליכים אחרי ייבוא או יצירה |
| בידוד task runner ל-Code nodes | Code nodes רצים ב-sandbox מבודד | הגדרת משתני המודולים על ה-**task runner**, לא על הקונטיינר הראשי |
| צומת Python נבנה מחדש על task runners | Python מבוסס Pyodide הוסר, Python נייטיב דורש runners במצב external | הקמת task runners במצב external, או שימוש ב-JavaScript |
| הסרת תמיכה ב-MySQL/MariaDB | לא אפשר להשתמש ב-MySQL/MariaDB כ-DB backend | מעבר ל-PostgreSQL (מומלץ) או SQLite |

**גישה למודולים ב-Code node.** מנגנון `require()` למודולים חיצוניים מושבת ב-n8n אלא אם המשתנה מוגדר, והסקיל הזה זקוק לשניהם:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

בלי הראשון, מאמת ה-HMAC ב-`references/webhook-auth-patterns.md` זורק שגיאה על `require('crypto')`. בלי השני, ה-Code node של סריקת הבנק זורק שגיאה על `require('israeli-bank-scrapers')`. **אם task runners פעילים (ברירת המחדל ב-2.0), מגדירים את המשתנים על ה-task runner ולא על הקונטיינר הראשי של n8n**, אחרת אין להם שום השפעה.

**סודות ב-Code node.** המשתנה `N8N_BLOCK_ENV_ACCESS_IN_NODE` מוגדר כ-`true` כברירת מחדל ב-2.x, ולכן `$env.*` בתוך Code node מחזיר ריק. עדיף להעביר את סודות הבנק וה-HMAC ל-credential store, וזו גם ההמלצה של n8n עצמה בתיעוד השינוי. מגדירים `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` רק אם חייבים לשמר את דפוס ה-`$env`.

ב-n8n 2.0, צומת Execute Command (וגם Local File Trigger) נוסף לרשימת `NODES_EXCLUDE` של ברירת המחדל, ולכן הוא נעלם מלוח הצמתים. כדי להפעיל מחדש את Execute Command, דורסים את `NODES_EXCLUDE` כך שלא יכיל את `n8n-nodes-base.executeCommand`, הדריסה הפשוטה ביותר היא רשימה ריקה, ואז מפעילים מחדש את n8n:
```
NODES_EXCLUDE="[]"
```
לפי תיעוד השינויים של n8n 2.0 זה המנגנון הנתמך, אין משתנה `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE`. הפעלת Execute Command מאפשרת לכל מי שיש לו הרשאת עריכת workflow להריץ פקודות shell שרירותיות, אז עשו זאת רק בסביבות מהימנות וחד-משתמש. הגישה המומלצת נשארת מעבר ל-Code nodes.

## אפשרויות ענן ישראליות

| ספק | מיקום נתונים | תמיכה ב-n8n | הערות |
|-----|-------------|-------------|-------|
| AWS (il-central-1) | ישראל (תל אביב) | Docker מלא | אזור מלא זמין |
| Azure (Israel Central) | ישראל | Docker מלא | אזור israelcentral |
| Google Cloud (me-west1) | ישראל (תל אביב) | Docker מלא | הושק 2022 |
| Kamatera | ישראל (פתח תקווה) | VPS עם Docker | חברה ישראלית, חיוב בשקלים |
| ActiveCloud / HQserv / MedOne | ישראל | VPS עם Docker | חברות ישראליות, תמיכה מקומית בעברית |

**ציות לרגולציית מיקום נתונים:** הרשות להגנת הפרטיות (PPA) לא דורשת שכל המידע יישאר בישראל. היא מגבילה העברת מידע אישי למדינות ללא הגנה מספקת, או דורשת אמצעי הגנה נוספים (כמו סעיפים חוזיים). לתהליכים שמעבדים מידע אישי (תעודות זהות, פרטי בנק, מידע רפואי), יש לבחור ספק עם מרכז נתונים בישראל או לוודא שמדינת היעד ברשימה המאושרת של הרשות.

## Docker Compose לאירוח עצמי

```yaml
services:
  n8n:
    # נועלים תג ספציפי. אסור :latest בפרודקשן.
    # חייב להיות לפחות 2.32.1 כדי להיות מטולא נגד שרשרת CVE-2026-44789/44790/44791.
    image: n8nio/n8n:2.36.7
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Asia/Jerusalem
      - TZ=Asia/Jerusalem
      # מומלץ: רוטציה של מפתח ההצפנה רק דרך תהליך המיגרציה המתועד.
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**הערות:**
- n8n 1.0 ומעלה משתמש בניהול משתמשים מובנה (אימייל + סיסמה). משתני הסביבה הישנים `N8N_BASIC_AUTH_*` הוסרו. בהפעלה ראשונה, n8n מבקש ליצור חשבון בעלים.
- `version: '3.8'` לא מופיע כי הוא מיושן ב-Docker Compose V2.
- **קריטי:** חובה להגדיר `GENERIC_TIMEZONE=Asia/Jerusalem` ו-`TZ=Asia/Jerusalem`. בלי זה, כל ה-Schedule Trigger nodes רצים לפי UTC, וחישובי שבת יהיו מוזזים ב-2-3 שעות (ישראל ב-UTC+2 בחורף, UTC+3 בקיץ). שעון קיץ בישראל מתחיל ביום שישי שלפני יום ראשון האחרון של מרץ ומסתיים ביום ראשון האחרון של אוקטובר.



---
