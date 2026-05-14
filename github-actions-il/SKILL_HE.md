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
        SHABBAT_JSON=$(curl -s "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on")
        CANDLE=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="candles") | .date')
        HAVDALAH=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="havdalah") | .date')
        NOW=$(date -u +%Y-%m-%dT%H:%M:%S)

        if [[ "$NOW" > "$CANDLE" && "$NOW" < "$HAVDALAH" ]]; then
          echo "frozen=true" >> $GITHUB_OUTPUT
          echo "reason=Shabbat (candle lighting: $CANDLE)" >> $GITHUB_OUTPUT
        else
          HOLIDAYS=$(curl -s "https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&year=$(date +%Y)&month=$(date +%-m)&geo=geoname&geonameid=281184")
          HOLIDAY_TODAY=$(echo "$HOLIDAYS" | jq -r ".items[] | select(.date | startswith(\"$(date +%Y-%m-%d)\")) | .title" | head -1)
          if [[ -n "$HOLIDAY_TODAY" ]]; then
            echo "frozen=true" >> $GITHUB_OUTPUT
            echo "reason=Holiday: $HOLIDAY_TODAY" >> $GITHUB_OUTPUT
          else
            echo "frozen=false" >> $GITHUB_OUTPUT
            echo "reason=none" >> $GITHUB_OUTPUT
          fi
        fi
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
      - uses: actions/checkout@v5
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

> **הערה:** ה-bash המוטמע ב-composite action שלמעלה הוא להמחשה בלבד. ההשוואה הלקסיקלית של מחרוזות `[[ "$NOW" > "$CANDLE" ]]` שבירה, היא עובדת רק כששני ה-timestamps חולקים אותו היסט אזור זמן ואותו פורמט מחרוזת, והיא נשברת במעברי שעון קיץ/חורף ובמעבר תאריך. המימוש הקנוני והנכון ב-`references/shabbat-deploy-freeze.md` ממיר כל timestamp לשניות epoch לפני ההשוואה ומוסיף buffer מתוכנן לפני שבת. השתמשו במימוש הייחוס בתהליכים אמיתיים.

למדריך המלא עם מקרי קצה וטיפול באזורי זמן, עיינו ב-`references/shabbat-deploy-freeze.md`.

### שלב 3: הגדרת התראות בעברית

טקסט עברי ב-webhook payloads דורש טיפול מפורש בכיוון RTL. ל-Slack ול-Teams יש התנהגות שונה.

**Slack (Incoming Webhook):**

```yaml
- name: Notify Slack (Hebrew)
  if: always()
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    STATUS="${{ job.status }}"
    REPO="${{ github.repository }}"
    BRANCH="${{ github.ref_name }}"
    ACTOR="${{ github.actor }}"

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
  run: |
    ITEM_ID=$(echo "${{ github.ref_name }}" | grep -oP 'MON-\K\d+' || true)
    if [ -n "$ITEM_ID" ]; then
      STATUS_LABEL="${{ job.status == 'success' && 'Deployed' || 'Failed' }}"
      curl -s -X POST "https://api.monday.com/v2" \
        -H "Authorization: $MONDAY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"mutation { change_simple_column_value(item_id: $ITEM_ID, board_id: ${{ vars.MONDAY_BOARD_ID }}, column_id: \\\"status\\\", value: \\\"$STATUS_LABEL\\\") { id } }\"}"
    fi
```

### שלב 4: הוספת בדיקות תאימות ישראליות

**נגישות IS-5568 (תקן ישראלי)**

IS-5568 הוא תקן הנגישות הישראלי, מבוסס על WCAG 2.1 AA עם דרישות נוספות לתוכן עברי/RTL.

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
    - uses: actions/checkout@v5
    - uses: actions/setup-node@v5
      with:
        node-version: '22'
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
    - uses: actions/checkout@v5
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

| ספק ענן | אזור מומלץ | חביון לישראל | הגדרה ב-Actions |
|---------|------------|-------------|-----------------|
| Vercel | fra1 (פרנקפורט) | כ-30ms | `vercel --regions fra1` |
| AWS | eu-west-1 (אירלנד) / me-south-1 (בחריין) | כ-40ms / כ-20ms | `AWS_DEFAULT_REGION` |
| GCP | europe-west1 (בלגיה) / me-west1 (תל אביב) | כ-35ms / כ-5ms | `GOOGLE_CLOUD_REGION` |
| Cloudflare Workers | אוטומטי (TLV edge) | כ-5ms | לא צריך הגדרת אזור |

**פריסה ל-Vercel עם fra1:**

```yaml
deploy-vercel:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v5
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

### שלב 6: תזמון שבוע עבודה ישראלי

שבוע העבודה בישראל הוא ראשון עד חמישי. יום שישי הוא חצי יום (בדרך כלל עד 13:00-14:00). לוחות cron ב-GitHub Actions משתמשים ב-UTC, אז צריך להמיר בהתאם (ישראל היא UTC+2, או UTC+3 בשעון קיץ).

| תזמון (שעון ישראל) | Cron (UTC, חורף) | Cron (UTC, קיץ) | שימוש |
|--------------------|-----------------|-----------------|-------|
| א-ה 09:00 | `0 7 * * 0-4` | `0 6 * * 0-4` | CI בוקר |
| א-ה 17:00 | `0 15 * * 0-4` | `0 14 * * 0-4` | פריסה סוף יום |
| ו 12:00 (קאטאוף חצי יום) | `0 10 * * 5` | `0 9 * * 5` | פריסה אחרונה לפני שבת |
| יומי מלבד שבת | `0 7 * * 0-5` | `0 6 * * 0-5` | ימי חול + שישי בוקר |

**טיפול במעבר שעון קיץ/חורף**: ישראל עוברת לשעון קיץ ביום שישי האחרון לפני 2 באפריל, ובחזרה ביום ראשון האחרון לפני אוקטובר. במקום לתחזק שני cron schedules, השתמשו ב-hebcal API לקביעת ההיסט הנוכחי, או קבלו סטייה של שעה בשבועות המעבר.

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

### דוגמה 3: סטארטאפ ישראלי, הגדרת CI/CD מלאה

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
- **זמני שבת משתנים כל שבוע ולפי עיר.** סוכנים נוטים לקבע "שישי 18:00" כזמן כניסת שבת. בפועל, הדלקת נרות נעה בין 16:10 בחורף ל-19:45 בקיץ. תמיד השתמשו ב-hebcal API לזמנים מדויקים.
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
סיבה: סריקה אוטומטית מזהה רק כ-30% מבעיות הנגישות. IS-5568 דורש בדיקה ידנית לסדר קריאה, התנהגות קורא מסך וזרימת תוכן דו-לשוני.
פתרון: השתמשו ב-axe-core כבסיס, לא כבדיקה מלאה. הוסיפו סקירת נגישות ידנית כפריט checklist ב-PR.

### שגיאה: "Monday.com mutation returns 'unauthorized'"
סיבה: ל-API token אין הרשאה ללוח היעד, או ש-`board_id` שגוי.
פתרון: ודאו שלטוקן יש הרשאות כתיבה ללוח. בדקו את `MONDAY_BOARD_ID` ב-repository variables. בדקו עם שאילתה פשוטה: `{ boards(ids: [BOARD_ID]) { name } }`.
