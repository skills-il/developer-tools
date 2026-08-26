---
name: github-actions-il
description: >-
  CI/CD workflow templates tailored for Israeli development teams, including
  Shabbat/holiday-aware deployment schedules ("shabbat deploy freeze", "hakpaaat
  prisa"), Hebrew Slack/Teams notifications, Israeli compliance checks (IS-5568
  accessibility, Privacy Protection Authority), Monday.com issue sync, and
  reusable composite actions for Israeli startup stacks. Use when user asks to
  "set up CI/CD for Israeli team", "add Shabbat deploy freeze", "configure Hebrew
  notifications in GitHub Actions", "hakpaat prisa beshabbat", "add IS-5568
  check to pipeline", "Israeli compliance CI", or "create workflow for Vercel
  fra1". Supports Israeli work week (Sunday-Thursday) scheduling and Hebrew
  locale awareness. Do NOT use for JFrog Artifactory pipelines (use
  jfrog-devops), general GitHub repository management, non-CI/CD GitHub Actions,
  or Jenkins/CircleCI/GitLab CI configurations.
license: MIT
---

# GitHub Actions לצוותים ישראליים

## הוראות

### שלב 1: בחירת תבנית Workflow מתאימה

התאימו את הצורך של הצוות לתבנית הנכונה. השתמשו בטבלה כנקודת פתיחה והתאימו לפי הסטאק והיעד של הפרויקט.

| צורך של הצוות | תבנית Workflow | כלים ופעולות מרכזיות |
|---------------|----------------|----------------------|
| הקפאת פריסה בשבת/חג | `shabbat-deploy-freeze.yml` | hebcal API, cron schedule, environment protection |
| התראות Slack בעברית | `hebrew-notifications.yml` | Slack Incoming Webhook, RTL payload |
| התראות Teams בעברית | `hebrew-notifications.yml` | Teams Incoming Webhook, Adaptive Card |
| בדיקת נגישות IS-5568 | `compliance-checks.yml` | axe-core, pa11y, כללי IS-5568 |
| בדיקת פרטיות (GDPR-IL) | `compliance-checks.yml` | סורק מותאם, dependency audit |
| סנכרון Monday.com | `monday-sync.yml` | Monday.com GraphQL API |
| פריסה ל-Vercel fra1 | `deploy-vercel.yml` | vercel CLI עם `--regions fra1` |
| Supabase migration CI | `supabase-ci.yml` | supabase CLI, migration diff |
| בדיקת i18n עברית | `i18n-validation.yml` | סקריפט מותאם, JSON schema check |
| תזמון שבוע עבודה ישראלי | כל workflow | Cron בימים א-ה |

אם לצוות יש מספר צרכים, שלבו workflows דרך composite actions מ-`references/workflow-templates.md`.

### שלב 2: הגדרת תזמון מודע לשבת וחגים

צוותים ישראליים צריכים לוחות פריסה שמכבדים שבת (מיום שישי אחר הצהריים עד מוצאי שבת) וחגים. זו לא רק העדפה תרבותית: פריסה בשבת פירושה שאין מי שיטפל בתקלות.

**גישה: hebcal API + Environment Protection Rules**

1. צרו composite action שבודק אם הזמן הנוכחי נמצא בחלון הקפאה:

```yaml
# .github/actions/shabbat-check/action.yml
name: 'Shabbat/Holiday Check'
description: 'Check if current time is during Shabbat or Israeli holiday'
outputs:
  is_frozen:
    description: 'true if deploys should be frozen'
    value: ${{ steps.check.outputs.frozen }}
  reason:
    description: 'Why deploys are frozen'
    value: ${{ steps.check.outputs.reason }}
runs:
  using: 'composite'
  steps:
    - id: check
      shell: bash
      run: |
        # ONE feed covers Shabbat AND holidays. The /shabbat endpoint honours maj=on and
        # returns `holiday` items together with their candle-lighting times, including the
        # EREV entries (Erev Yom Kippur, Erev Sukkot) that the /hebcal feed omits entirely.
        # Ask for TODAY in Israel time: runners are UTC, so a bare `date` is still yesterday
        # between 00:00 and 03:00 Israel time and would miss the chag.
        export TZ=Asia/Jerusalem
        CURL_OK=0
        FEED=$(curl -sf --max-time 10 --retry 2 \
          "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on&maj=on&gy=$(date +%Y)&gm=$(date +%-m)&gd=$(date +%-d)") || CURL_OK=$?

        # Fail CLOSED: a deploy freeze is a safety gate, so an unreachable API means frozen.
        if [ "$CURL_OK" -ne 0 ] || [ -z "$FEED" ]; then
          echo "frozen=true" >> $GITHUB_OUTPUT
          echo "reason=Could not reach hebcal to verify the Shabbat/holiday window; failing closed. Override with force_deploy." >> $GITHUB_OUTPUT
          exit 0
        fi

        # Walk the feed in order, pairing each candle-lighting with the havdalah that follows
        # it, and compare in EPOCH SECONDS. hebcal returns offset-aware times (+03:00 summer,
        # +02:00 winter); comparing those as strings against a UTC clock is wrong by exactly
        # the offset and leaves the gate open for the first hours of every Shabbat.
        # A 200 with an unexpected shape must freeze too: pipefail does not propagate out
        # of the process substitution below, so an empty item list would silently open the gate.
        ITEM_COUNT=$(echo "$FEED" | jq -r '.items | length' 2>/dev/null || echo 0)
        if [ -z "$ITEM_COUNT" ] || [ "$ITEM_COUNT" = "0" ] || [ "$ITEM_COUNT" = "null" ]; then
          echo "frozen=true" >> $GITHUB_OUTPUT
          echo "reason=hebcal returned no calendar items; failing closed. Override with force_deploy." >> $GITHUB_OUTPUT
          exit 0
        fi

        # Rule 1: any FULL yom tov dated today. A feed requested for the chag itself starts
        # that morning, so the previous evening's candle-lighting is outside its range and the
        # window walk below cannot see it. `yomtov: true` marks exactly the days on which work
        # is prohibited (Yom Kippur, Shavuot, both days of Rosh Hashana, Sukkot I, Shmini
        # Atzeret) and is absent on chol hamoed, fast days and Shabbat Shuva.
        TODAY=$(date +%Y-%m-%d)
        YOMTOV=$(echo "$FEED" | jq -r --arg d "$TODAY" '[.items[] | select(.yomtov == true and (.date | startswith($d)))] | first | .title // empty')
        if [ -n "$YOMTOV" ]; then
          # The chag ends at havdalah, not at midnight. If today's closing havdalah has
          # already passed, fall through to rule 2 rather than freezing until 00:00.
          END_TODAY=$(echo "$FEED" | jq -r --arg d "$TODAY" '[.items[] | select(.category=="havdalah" and (.date | startswith($d)))] | first | .date // empty')
          END_EPOCH=""
          [ -n "$END_TODAY" ] && END_EPOCH=$(date -d "$END_TODAY" +%s 2>/dev/null || echo "")
          # No havdalah today, or we could not parse it, means still yom tov: freeze.
          if [ -z "$END_EPOCH" ] || [ "$(date +%s)" -le "$END_EPOCH" ]; then
            echo "frozen=true" >> $GITHUB_OUTPUT
            echo "reason=$YOMTOV (yom tov)" >> $GITHUB_OUTPUT
            exit 0
          fi
        fi

        # Rule 2: inside a candle-lighting to havdalah window (Shabbat, and the evening a chag
        # begins, which is dated the day BEFORE the yom tov and so is not caught by rule 1).
        NOW_EPOCH=$(date +%s)
        FROZEN=false
        REASON=none
        START=""
        LABEL="Shabbat"
        PENDING="Shabbat"

        while IFS=$'\t' read -r CAT WHEN TITLE; do
          case "$CAT" in
            holiday)  PENDING="$TITLE" ;;
            candles)
              # Keep the EARLIEST unclosed candle-lighting. A two-day yom tov (Rosh Hashana,
              # or any chag adjacent to Shabbat) emits TWO candle-lightings before a single
              # havdalah; overwriting here would test only the second night and leave the
              # gate open for the whole of day one.
              if [ -z "$START" ]; then
                START="$WHEN"
                LABEL="$PENDING"
              fi
              ;;
            havdalah)
              EE=$(date -d "$WHEN" +%s)
              if [ -z "$START" ]; then
                # A havdalah with no candle-lighting before it means the window opened
                # before this feed's range started, i.e. we are already inside it. This is
                # the chag-daytime case (querying on Yom Kippur itself returns the closing
                # havdalah but not the previous evening's candles). Freeze.
                if [ "$NOW_EPOCH" -le "$EE" ]; then
                  FROZEN=true
                  REASON="$PENDING (in progress, ends $WHEN)"
                  break
                fi
              else
                SE=$(date -d "$START" +%s)
                if [ "$NOW_EPOCH" -ge "$SE" ] && [ "$NOW_EPOCH" -le "$EE" ]; then
                  FROZEN=true
                  REASON="$LABEL (frozen from $START until $WHEN)"
                  break
                fi
              fi
              START=""
              LABEL="Shabbat"
              PENDING="Shabbat"
              ;;
          esac
        done < <(echo "$FEED" | jq -r '.items[] | [.category, .date, .title] | @tsv')

        echo "frozen=$FROZEN" >> $GITHUB_OUTPUT
        echo "reason=$REASON" >> $GITHUB_OUTPUT
```

2. השתמשו ב-action הזה כשער בתהליך הפריסה:

```yaml
jobs:
  check-deploy-window:
    runs-on: ubuntu-latest
    outputs:
      is_frozen: ${{ steps.shabbat.outputs.is_frozen }}
      reason: ${{ steps.shabbat.outputs.reason }}
    steps:
      - uses: actions/checkout@v7
      - id: shabbat
        uses: ./.github/actions/shabbat-check

  deploy:
    needs: check-deploy-window
    if: needs.check-deploy-window.outputs.is_frozen != 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

3. **מנגנון חירום**: הוסיפו `workflow_dispatch` עם אפשרות לדרוס את ההקפאה:

```yaml
on:
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Override Shabbat/holiday freeze (emergency only)'
        required: false
        type: boolean
        default: false
```

ושנו את התנאי ב-deploy job:

```yaml
if: >
  needs.check-deploy-window.outputs.is_frozen != 'true' ||
  github.event.inputs.force_deploy == 'true'
```

> **הערה:** ה-composite action שלמעלה הוא מימוש העבודה המלא: הוא מזווג כל הדלקת נרות עם ההבדלה שאחריה ומשווה בשניות epoch, הוא מבקש מ-hebcal את התאריך של היום לפי `Asia/Jerusalem` ולא לפי שעון ה-UTC של הראנר, והוא נכשל סגור (fail closed) כש-hebcal לא זמין. הקובץ `references/shabbat-deploy-freeze.md` מוסיף באפר מתכוונן לפני שבת, geonameid לכל עיר, אסטרטגיות לריבוי סביבות ואת workflow החירום. שני דברים שהשער הזה לא מכסה: צומות קטנים וחנוכה/פורים (`min=on`) וימי הזיכרון והעצמאות (`mod=on`). צוותים ישראליים רבים מקפיאים גם ביום הזיכרון; הוסיפו את הפרמטר אם אתם מציינים אותם.

למדריך המלא עם מקרי קצה וטיפול באזורי זמן, עיינו ב-`references/shabbat-deploy-freeze.md`.

### שלב 3: הגדרת התראות בעברית

טקסט עברי ב-webhook payloads דורש טיפול מפורש בכיוון RTL. ל-Slack ול-Teams יש התנהגות שונה.

**Slack (Incoming Webhook):**

```yaml
- name: Notify Slack (Hebrew)
  if: always()
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
    # לעולם אל תשתלו ${{ }} ישירות בתוך run:. GitHub מחליף אותו כטקסט גולמי לפני
    # ש-bash מנתח את השורה, ולכן הודעת קומיט שמכילה גרש הפוך או $(...) תרוץ כקוד
    # ב-job שמחזיק את טוקני הפריסה שלכם. קשרו הקשר לא-מהימן ל-env ואז קראו אותו
    # כמשתנה shell רגיל.
    STATUS: ${{ job.status }}
    REPO: ${{ github.repository }}
    BRANCH: ${{ github.ref_name }}
    ACTOR: ${{ github.actor }}
  run: |

    if [ "$STATUS" = "success" ]; then
      STATUS_HE="הצליח"; COLOR="#36a64f"
    elif [ "$STATUS" = "failure" ]; then
      STATUS_HE="נכשל"; COLOR="#dc3545"
    else
      STATUS_HE="בוטל"; COLOR="#ffc107"
    fi

    RTL=$'\u200F'

    curl -s -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{\"attachments\": [{\"color\": \"$COLOR\", \"blocks\": [{\"type\": \"section\", \"text\": {\"type\": \"mrkdwn\", \"text\": \"${RTL}*פריסה ${STATUS_HE}*\n${RTL}ריפו: \`${REPO}\`\n${RTL}ענף: \`${BRANCH}\`\n${RTL}מפתח: ${ACTOR}\"}}]}]}"
```

נקודות חשובות לעברית ב-Slack:
- הוסיפו את תו ה-RTL mark (U+200F) לפני כל שורה בעברית
- שמות ריפו, ענפים וזיהויים טכניים נשארים באנגלית
- עיצוב mrkdwn של Slack עובד עם טקסט עברי

**Monday.com:**

```yaml
- name: Update Monday.com item
  env:
    MONDAY_TOKEN: ${{ secrets.MONDAY_API_TOKEN }}
    # A fork's branch name is attacker-controlled; bind it rather than interpolating it.
    REF_NAME: ${{ github.ref_name }}
    BOARD_ID: ${{ vars.MONDAY_BOARD_ID }}
  run: |
    ITEM_ID=$(printf '%s' "$REF_NAME" | grep -oP 'MON-\K\d+' || true)
    if [ -n "$ITEM_ID" ]; then
      STATUS_LABEL="${{ job.status == 'success' && 'Deployed' || 'Failed' }}"
      curl -s -X POST "https://api.monday.com/v2" \
        -H "Authorization: $MONDAY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"mutation { change_simple_column_value(item_id: $ITEM_ID, board_id: $BOARD_ID, column_id: \\\"status\\\", value: \\\"$STATUS_LABEL\\\") { id } }\"}"
    fi
```

### שלב 4: הוספת בדיקות תאימות ישראליות

**נגישות IS-5568 (תקן ישראלי)**

תקן IS-5568 הוא תקן הנגישות הישראלי לאתרים, שקיבל תוקף מחייב בתקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות). הוא מאמץ את WCAG בתוספת דרישות לתוכן עברי/RTL. מהדורת WCAG שאליה התקן מפנה השתנתה בין גרסאות של התקן, ולכן ודאו מול מכון התקנים הישראלי מול איזו רמה נמדדת החובה שלכם במקום להניח; סריקה מול WCAG 2.1 AA מקיימת גם 2.0 AA כקבוצה מכילה, ולכן תצורת axe שלמטה עוברת את שלוש קבוצות התגיות.

| דרישת IS-5568 | מקביל ב-WCAG | כלל ישראלי נוסף |
|---------------|--------------|-----------------|
| כיוון טקסט RTL | לא קיים | `dir="rtl"` באלמנט שורש, `lang="he"` תקין |
| תוכן דו-לשוני | 3.1.2 Language of Parts | אטריביוט `lang` מפורש לכל קטע שפה |
| לוגו אתר ממשלתי | לא קיים | קישור להצהרת נגישות gov.il |
| נגישות יצירת קשר | לא קיים | מספר טלפון נגיש (לא תמונה של מספר) |
| נגישות PDF | 1.3.1 | סדר קריאה תקין ומבנה מתויג ב-PDF עברי |

הוספה ל-CI pipeline:

```yaml
accessibility-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
    - uses: actions/setup-node@v7
      with:
        node-version: '24'
    - name: Install accessibility tools
      run: npm install -g @axe-core/cli pa11y-ci

    - name: Build and start
      run: npm run build && npm run start &
    - name: Wait for server
      run: npx wait-on http://localhost:3000 --timeout 60000

    - name: Run axe-core scan
      run: axe http://localhost:3000 --tags wcag2a,wcag2aa,wcag21aa --locale he --exit

    - name: Check RTL and lang (IS-5568)
      run: |
        HTML=$(curl -s http://localhost:3000)
        if ! echo "$HTML" | grep -q 'dir="rtl"'; then
          echo "::error::Missing dir=\"rtl\" (IS-5568)"
          exit 1
        fi
        if ! echo "$HTML" | grep -q 'lang="he"'; then
          echo "::error::Missing lang=\"he\" (IS-5568)"
          exit 1
        fi
```

**בדיקות פרטיות (רשות להגנה על הפרטיות):**

```yaml
privacy-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
    - name: Scan for exposed PII patterns
      run: |
        if grep -rn '[0-9]\{9\}' src/ --include="*.ts" --include="*.tsx" | \
           grep -v 'test\|mock\|spec\|\.d\.ts'; then
          echo "::warning::Potential Israeli ID numbers in source code"
        fi
    - name: Check privacy policy route
      run: |
        if ! find src -name "privacy*" -o -name "פרטיות*" | grep -q .; then
          echo "::warning::No privacy policy page. Israeli PPA requires one."
        fi
```

### שלב 5: פריסה ליעדי ענן מתאימים לישראל

| ספק ענן | אזור מומלץ | חביון יחסי מישראל | הגדרה ב-Actions |
|---------|------------|-------------|-----------------|
| Vercel | fra1 (פרנקפורט) | נמוך | `vercel --regions fra1` |
| AWS | il-central-1 (תל אביב) / eu-west-1 (אירלנד) | הנמוך ביותר / גבוה יותר | `AWS_DEFAULT_REGION` |
| GCP | europe-west1 (בלגיה) / me-west1 (תל אביב) | גבוה יותר / הנמוך ביותר | `GOOGLE_CLOUD_REGION` |
| Cloudflare Workers | אוטומטי (TLV edge) | הנמוך ביותר | לא צריך הגדרת אזור |

עמודת החביון היא דירוג יחסי ולא מדידה: אזור בתוך הארץ עדיף על אזור אירופי, שעדיף על אזור רחוק יותר. מדדו מהמשתמשים שלכם בפועל לפני שנועלים אזור, ושקללו את זה מול העובדה ש-il-central-1 ו-me-west1 מציעים קטלוג שירותים דל יותר מהאזורים האירופיים הוותיקים.

**פריסה ל-Vercel עם fra1:**

```yaml
deploy-vercel:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
    - name: Deploy to Vercel
      env:
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
      run: |
        npx vercel pull --yes --token=$VERCEL_TOKEN
        npx vercel build --token=$VERCEL_TOKEN
        npx vercel deploy --prebuilt --token=$VERCEL_TOKEN --regions fra1
```

**הרשאות טוקן והקשחת אבטחה.** מאז פברואר 2023 ברירת המחדל של `GITHUB_TOKEN` היא **קריאה בלבד**, אז כל job שכותב (תגובה ל-PR, דחיפת commit, יצירת release) חייב להגדיר בלוק `permissions:` מפורש, ואימות OIDC לענן דורש `id-token: write`. הגדירו הרשאות מינימליות לכל job:

```yaml
permissions:
  contents: read          # בסיס בטוח
# הוסיפו רק מה שה-job צריך, למשל:
# pull-requests: write    # לתגובות github-script על PR
# id-token: write         # ל-OIDC ל-AWS/GCP (בלי מפתחות סוד ארוכי-חיים)
```

הקשחות נוספות לריפו של צוות ישראלי:
- **נעצו פעולות צד-שלישי ל-SHA מלא** (`uses: owner/action@<sha>`), לא לתג נייד. תג נייד היה הווקטור בפריצת שרשרת האספקה של tj-actions/changed-files ב-2025. פעולות `actions/*` רשמיות בסיכון נמוך יותר, אבל נעיצה ל-SHA היא הסטנדרט.
- **הפעילו Dependabot לפעולות** (`.github/dependabot.yml` עם `package-ecosystem: "github-actions"`) כדי שהגרסאות הנעוצות יתעדכנו אוטומטית. זו התשובה התחזוקתית להתיישנות.
- **הפעולה `actions/checkout` חוסמת כברירת מחדל checkout של fork תחת `pull_request_target`.** החל מ-v7 (והשינוי גובה לאחור ל-v4/v5/v6) הפעולה דוחה את דפוסי ה-"pwn request" הקלאסיים, כולל `ref: ${{ github.event.pull_request.head.sha }}` ו-`repository: ${{ github.event.pull_request.head.repo.full_name }}`, מפני שה-workflows האלה רצים עם ה-`GITHUB_TOKEN` והסודות של הריפו הבסיסי. הפעולה חושפת `allow-unsafe-pr-checkout: true` כמנגנון יציאה מפורש; התייחסו אליו כמוצא אחרון, והעדיפו את הטריגר `pull_request` יחד עם job מורשה נפרד ב-`workflow_run`. אם workflow ותיק שלכם נכשל פתאום בשלב ה-checkout, זו הסיבה.
- **הגדירו `timeout-minutes` לכל job.** ברירת המחדל היא 360 דקות (שש שעות). זה קריטי כאן במיוחד כי שער השבת מבצע קריאת רשת ל-API חיצוני בנתיב הקריטי של כל פריסה לייצור: `--max-time` מגביל את ה-curl, אבל רק `timeout-minutes` מגביל את ה-job. `timeout-minutes: 10` ל-job של השער ו-30 ל-job של הפריסה הם ערכי פתיחה סבירים.

### שלב 6: תזמון שבוע עבודה ישראלי

שבוע העבודה בישראל הוא ראשון עד חמישי. יום שישי הוא חצי יום (בדרך כלל עד 13:00-14:00). לוחות cron ב-GitHub Actions משתמשים ב-UTC, אז צריך להמיר בהתאם (ישראל היא UTC+2, או UTC+3 בשעון קיץ).

| תזמון (שעון ישראל) | Cron (UTC, חורף) | Cron (UTC, קיץ) | שימוש |
|--------------------|-----------------|-----------------|-------|
| א-ה 09:00 | `0 7 * * 0-4` | `0 6 * * 0-4` | CI בוקר |
| א-ה 17:00 | `0 15 * * 0-4` | `0 14 * * 0-4` | פריסה סוף יום |
| ו 12:00 (קאטאוף חצי יום) | `0 10 * * 5` | `0 9 * * 5` | פריסה אחרונה לפני שבת |
| יומי מלבד שבת | `0 7 * * 0-5` | `0 6 * * 0-5` | ימי חול + שישי בוקר |

**טיפול במעבר שעון קיץ/חורף**: ישראל עוברת לשעון קיץ ביום שישי שלפני יום ראשון האחרון של מרץ, וחוזרת לשעון חורף ביום ראשון האחרון של אוקטובר (27 במרץ ו-25 באוקטובר ב-2026; 26 במרץ ו-31 באוקטובר ב-2027). במקום לתחזק שני cron schedules, השתמשו ב-hebcal API לקביעת ההיסט הנוכחי, או קבלו סטייה של שעה בשבועות המעבר.

### שלב 7: יצירת Composite Actions לשימוש חוזר

בנו ספריית composite actions שמקודדת מוסכמות של סטארטאפים ישראליים. הם נמצאים ב-`.github/actions/` ואפשר לשתף אותם בין ריפואים.

**Hebrew i18n validation action:**

```yaml
# .github/actions/i18n-validate/action.yml
name: 'Validate Hebrew i18n'
description: 'Check that all i18n keys exist in both he and en locales'
inputs:
  locales_dir:
    description: 'Path to locales directory'
    default: 'src/locales'
runs:
  using: 'composite'
  steps:
    - shell: bash
      run: |
        HE_FILE="${{ inputs.locales_dir }}/he.json"
        EN_FILE="${{ inputs.locales_dir }}/en.json"

        if [ ! -f "$HE_FILE" ] || [ ! -f "$EN_FILE" ]; then
          echo "::error::Missing locale files"
          exit 1
        fi

        HE_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$HE_FILE")
        EN_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$EN_FILE")

        MISSING_HE=$(comm -23 <(echo "$EN_KEYS") <(echo "$HE_KEYS"))
        MISSING_EN=$(comm -23 <(echo "$HE_KEYS") <(echo "$EN_KEYS"))

        if [ -n "$MISSING_HE" ]; then
          echo "::error::Keys in en.json missing from he.json:"
          echo "$MISSING_HE"
          exit 1
        fi

        if [ -n "$MISSING_EN" ]; then
          echo "::warning::Keys in he.json missing from en.json:"
          echo "$MISSING_EN"
        fi

        echo "i18n validation passed"
```

לתבניות workflow מלאות, עיינו ב-`references/workflow-templates.md`.

## דוגמאות

### דוגמה 1: הגדרת הקפאת פריסה בשבת

המשתמש אומר: "תוסיף הקפאת פריסה בשבת ל-workflow של הפריסה לפרודקשן"

פעולות:
1. יצירת `.github/actions/shabbat-check/action.yml` עם אינטגרציית hebcal משלב 2
2. הוספת סוד `SLACK_WEBHOOK_URL` לריפו
3. שינוי ה-deploy workflow כך שיהיה תלוי בפלט shabbat-check
4. הוספת `workflow_dispatch` עם `force_deploy` למקרי חירום
5. הוספת התראת Slack בעברית כשהפריסה מוקפאת

תוצאה: פריסות לפרודקשן נעצרות אוטומטית מהדלקת נרות ביום שישי עד מוצאי שבת, עם התראות בעברית ואפשרות חירום לדריסה.

### דוגמה 2: הוספת בדיקות תאימות ישראליות ל-CI

המשתמש אומר: "אנחנו צריכים בדיקות נגישות IS-5568 ב-CI של pull requests"

פעולות:
1. הוספת ה-`accessibility-check` job משלב 4 ל-PR workflow
2. הגדרת axe-core עם WCAG 2.1 AA + locale עברי
3. הוספת בדיקת RTL/lang ספציפית ל-IS-5568
4. הוספת בדיקת privacy policy route
5. הגדרת ה-job כ-required status check ב-branch protection

תוצאה: כל PR נבדק לתאימות IS-5568, תקינות RTL ונוכחות privacy policy. כישלון חוסם merge.

### דוגמה 3: הגדרת התראות Slack בעברית עם סנכרון Monday.com

המשתמש אומר: "תקים התראות פריסה בעברית ב-Slack ועדכון כרטיסי Monday.com"

פעולות:
1. הוסיפו `SLACK_WEBHOOK_URL` ו-`MONDAY_API_TOKEN` כ-secrets בריפו
2. הוסיפו את שלב התראת ה-Slack בעברית משלב 3
3. הוסיפו את שלב עדכון הסטטוס ב-Monday.com, לפי מוסכמת שמות ענפים `feat/MON-{id}-description`
4. הגדירו את שתי ההתראות בבלוק `if: always()` כך שירוצו גם בהצלחה וגם בכישלון

תוצאה: סטטוס הפריסה מופיע ב-Slack עם טקסט עברי RTL, והפריט המתאים ב-Monday.com עובר לסטטוס "Deployed" או "Failed".

### דוגמה 4: סטארטאפ ישראלי, הגדרת CI/CD מלאה

המשתמש אומר: "אנחנו סטארטאפ ישראלי עם Next.js + Supabase + Vercel. תקים לנו את כל ה-CI/CD"

פעולות:
1. יצירת lint/test/build workflow שרץ בימים א-ה
2. הוספת Supabase migration diff check ב-PRs
3. הוספת i18n validation (פריטי he.json / en.json)
4. הוספת IS-5568 accessibility scan ב-PRs
5. יצירת Vercel deploy workflow עם fra1 region
6. הקפאת פריסות פרודקשן בשבת/חג
7. הוספת התראות Slack בעברית לכל שלבי ה-pipeline

תוצאה: CI/CD מלא שמכבד את תרבות העבודה הישראלית, עם בדיקות תאימות, i18n דו-לשוני והקפאת פריסה בשבת.

## משאבים מצורפים

### מסמכי עזר
- `references/workflow-templates.md` -- תבניות YAML מלאות ומוכנות להעתקה ל-CI/CD של סטארטאפים ישראליים: lint-test-deploy, Supabase migration CI, i18n validation, ו-pipeline תאימות ישראלי. עיינו כשמקימים workflows לפרויקט חדש.
- `references/shabbat-deploy-freeze.md` -- מדריך יישום מפורט להקפאת פריסה בשבת וחגים, כולל שימוש ב-hebcal API, מקרי קצה של אזורי זמן, אסטרטגיות מרובות סביבות, ונהלי דריסת חירום. עיינו כשמיישמים או מאתרים באגים במערכת ההקפאה.

## שרתי MCP מומלצים

- **hebcal**: לוח השנה היהודי וזמני שבת. חלופת MCP לקריאה ל-Hebcal HTTP API בתוך composite action, שימושית כשסוכן צריך נתוני חגים בזמן כתיבה או חשיבה על תהליך ולא בזמן ריצה.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| תיעוד GitHub Actions | https://docs.github.com/en/actions | תחביר workflow, לוחות cron, composite actions, environments |
| Hebcal Shabbat API | https://www.hebcal.com/home/developer-apis | זמני שבת, לוח חגים, ערכי geonameid |
| API של Monday.com | https://developer.monday.com/api-reference/docs | סכמת GraphQL, mutations, אימות |
| מכון התקנים הישראלי | https://www.sii.org.il/he/ | תקן IS-5568, הסמכת נגישות |
| אזורי Vercel | https://vercel.com/docs/edge-network/regions | קודי אזור (fra1) וחביון |

## מלכודות נפוצות

- **לוחות cron משתמשים ב-UTC, לא בשעון ישראל.** סוכנים נוטים לכתוב cron schedules בשעון מקומי. ישראל היא UTC+2 (חורף) או UTC+3 (קיץ). `0 9 * * 0-4` ב-cron פירושו 09:00 UTC, שזה 11:00 או 12:00 בישראל. תמיד תמירו.
- **שבוע העבודה בישראל הוא ראשון-חמישי, לא שני-שישי.** סוכנים כותבים `1-5` ל-cron של ימי חול (שני-שישי). לצוותים ישראליים, השתמשו ב-`0-4` (ראשון-חמישי) או `0-5` (ראשון-שישי חצי יום).
- **זמני שבת משתנים כל שבוע ולפי עיר.** סוכנים נוטים לקבע "שישי 18:00" כזמן כניסת שבת. בפועל, הדלקת נרות בערים בישראל נעה בין 15:55 בערך (ירושלים, תחילת-אמצע דצמבר) ל-19:30 בערך (תל אביב, יוני), וירושלים מדליקה כ-20 דקות מוקדם יותר מערי החוף כי היא נוהגת להדליק 40 דקות לפני השקיעה. תמיד השתמשו ב-hebcal API לזמנים מדויקים.
- **שלוש דרכים שבהן סוכן שובר את ההקפאה בשקט בזמן שה-workflow עדיין נראה תקין.** ראשית, hebcal מחזיר זמנים עם היסט (`2026-08-28T18:28:00+03:00`); השוואה לקסיקוגרפית מול `date -u` שגויה בגודל ההיסט ומשאירה את השער פתוח בשעות הראשונות של השבת. המירו את שני הגבולות לשניות epoch עם `date -d`. שנית, `/shabbat` מחזיר כברירת מחדל את סוף השבוע הקרוב, ולכן העבירו `gy`/`gm`/`gd` של היום, מחושבים תחת `TZ=Asia/Jerusalem`: `date` רגיל על ראנר הוא עדיין אתמול בין 00:00 ל-03:00 שעון ישראל. שלישית, חג של יומיים פולט שתי הדלקות נרות לפני הבדלה אחת, ולכן שמרו את המוקדמת שבהן שטרם נסגרה; דריסה שלה בודקת רק את הלילה השני ומאפשרת פריסות לאורך כל היום הראשון של ראש השנה.
- **טקסט עברי ב-YAML צריך סמני RTL.** בלי תו RTL mark (U+200F), טקסט עברי ב-Slack payloads מציג סימני פיסוק במקום הלא נכון. תמיד הוסיפו `\u200F` לפני שורות בעברית.
- **IS-5568 הוא לא רק WCAG 2.1 AA.** סוכנים מתייחסים ל-IS-5568 כמילה נרדפת ל-WCAG. ל-IS-5568 יש דרישות נוספות ספציפיות לישראל סביב תוכן דו-לשוני, לוגואים ממשלתיים ונגישות יצירת קשר.
- **`me-south-1` (בחריין) לא זמין לכל חשבונות AWS.** האזור הזה דורש הפעלה (opt-in). אל תניחו שהוא זמין. חיזרו ל-`eu-west-1` אם המשתמש לא הפעיל אותו.
- **Monday.com API v2 משתמש רק ב-GraphQL.** סוכנים לפעמים מנסים REST endpoints ל-Monday.com. ה-API הוא GraphQL בלבד ב-`https://api.monday.com/v2`.
- **`schedule` event ב-GitHub Actions רץ רק על ה-default branch.** סוכנים מוסיפים scheduled workflows על feature branches ותוהים למה הם לא מופעלים.

## פתרון בעיות

### שגיאה: "Hebcal API returns empty items"
סיבה: פרמטר `geonameid` שגוי, או שטווח התאריכים לא מכיל שבת.
פתרון: השתמשו ב-`geonameid=281184` לירושלים. בדקו על ידי פתיחת `https://www.hebcal.com/shabbat?cfg=json&geonameid=281184` בדפדפן.

### שגיאה: "Hebrew text appears reversed in Slack"
סיבה: חסר תו RTL mark ב-payload. Slack לא מזהה אוטומטית כיוון טקסט.
פתרון: הוסיפו `$'\u200F'` לפני כל שורה בעברית ב-bash, או `\u200F` במחרוזות JSON.

### שגיאה: "Cron schedule fires at wrong time"
סיבה: הלוח נכתב בשעון ישראל במקום UTC.
פתרון: הפחיתו 2 שעות (חורף) או 3 שעות (קיץ) מהשעה הרצויה בישראל. השתמשו ב-`date -u` לאימות.

### שגיאה: "axe-core scan finds no violations but site is not accessible"
סיבה: סריקה אוטומטית מזהה רק חלק קטן מבעיות הנגישות (לרוב מצוטט כשליש בערך). IS-5568 דורש בדיקה ידנית לסדר קריאה, התנהגות קורא מסך וזרימת תוכן דו-לשוני.
פתרון: השתמשו ב-axe-core כבסיס, לא כבדיקה מלאה. הוסיפו סקירת נגישות ידנית כפריט checklist ב-PR.

### שגיאה: "Monday.com mutation returns 'unauthorized'"
סיבה: ל-API token אין הרשאה ללוח היעד, או ש-`board_id` שגוי.
פתרון: ודאו שלטוקן יש הרשאות כתיבה ללוח. בדקו את `MONDAY_BOARD_ID` ב-repository variables. בדקו עם שאילתה פשוטה: `{ boards(ids: [BOARD_ID]) { name } }`.
