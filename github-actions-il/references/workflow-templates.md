# Reusable Workflow Templates for Israeli Teams

This reference contains complete, copy-paste-ready GitHub Actions workflow YAML templates designed for Israeli development teams. Each template encodes Israeli-specific conventions: Sunday-Thursday scheduling, Shabbat awareness, Hebrew notifications, and regional deployment targets.

## Template 1: Lint, Test, Deploy (Israeli Startup Stack)

A standard CI/CD pipeline for Israeli startups using Node.js. Runs on Israeli work days, deploys to Vercel fra1, and sends Hebrew Slack notifications.

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Sunday-Thursday at 09:00 Israel time (UTC+2 winter)
    - cron: '0 7 * * 0-4'

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-node@v5
        with:
          node-version: '22'

      - uses: pnpm/action-setup@v6
        with:
          version: 9

      - name: Get pnpm store directory
        shell: bash
        run: echo "STORE_PATH=$(pnpm store path --silent)" >> $GITHUB_ENV

      - uses: actions/cache@v5
        with:
          path: ${{ env.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: ${{ runner.os }}-pnpm-store-

      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test

  build:
    needs: lint-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: '22'
      - uses: pnpm/action-setup@v6
        with:
          version: 9
      - run: pnpm install --frozen-lockfile
      - run: pnpm build

  deploy-preview:
    if: github.event_name == 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - name: Deploy Preview to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npx vercel pull --yes --token=$VERCEL_TOKEN
          npx vercel build --token=$VERCEL_TOKEN
          PREVIEW_URL=$(npx vercel deploy --prebuilt --token=$VERCEL_TOKEN --regions fra1)
          echo "PREVIEW_URL=$PREVIEW_URL" >> $GITHUB_ENV

      - name: Comment PR with preview URL
        uses: actions/github-script@v9
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `\u200F**תצוגה מקדימה מוכנה:** ${process.env.PREVIEW_URL}`
            })

  deploy-production:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - id: shabbat
        uses: ./.github/actions/shabbat-check

      - name: Deploy to Vercel Production
        if: steps.shabbat.outputs.is_frozen != 'true'
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          npx vercel pull --yes --token=$VERCEL_TOKEN
          npx vercel build --prod --token=$VERCEL_TOKEN
          npx vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN --regions fra1

      - name: Notify Slack
        if: always()
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          STATUS="${{ job.status }}"
          if [ "$STATUS" = "success" ]; then
            STATUS_HE="הצליחה"; COLOR="#36a64f"
          else
            STATUS_HE="נכשלה"; COLOR="#dc3545"
          fi
          RTL=$'\u200F'
          curl -s -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"attachments\":[{\"color\":\"$COLOR\",\"blocks\":[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"${RTL}*פריסה לפרודקשן ${STATUS_HE}*\n${RTL}קומיט: ${{ github.event.head_commit.message }}\n${RTL}מפתח: ${{ github.actor }}\"}}]}]}"

      - name: Notify frozen
        if: steps.shabbat.outputs.is_frozen == 'true'
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          RTL=$'\u200F'
          curl -s -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"attachments\":[{\"color\":\"#ffc107\",\"blocks\":[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"${RTL}*פריסה הוקפאה*\n${RTL}סיבה: ${{ steps.shabbat.outputs.reason }}\n${RTL}הפריסה תתבצע אוטומטית אחרי מוצאי שבת/חג\"}}]}]}"
```

## Template 2: Supabase Migration CI

Validates Supabase migrations on PRs, runs migration diff checks, and ensures type safety.

```yaml
# .github/workflows/supabase-ci.yml
name: Supabase Migration CI

on:
  pull_request:
    paths:
      - 'supabase/migrations/**'
      - 'supabase/functions/**'

jobs:
  migration-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: supabase/setup-cli@v2
        with:
          version: latest

      - name: Start Supabase local
        run: supabase start

      - name: Verify migrations apply cleanly
        run: supabase db reset

      - name: Generate types and check for drift
        run: |
          supabase gen types typescript --local > supabase/types.ts
          if ! git diff --quiet supabase/types.ts; then
            echo "::error::TypeScript types are out of date. Run 'supabase gen types typescript --local > supabase/types.ts' and commit."
            git diff supabase/types.ts
            exit 1
          fi

      - name: Check migration naming convention
        run: |
          # Verify migration files follow timestamp_description.sql pattern
          for file in supabase/migrations/*.sql; do
            basename=$(basename "$file")
            if ! echo "$basename" | grep -qP '^\d{14}_[a-z_]+\.sql$'; then
              echo "::error::Migration $basename does not follow naming convention: YYYYMMDDHHMMSS_description.sql"
              exit 1
            fi
          done

      - name: Lint SQL migrations
        run: |
          for file in supabase/migrations/*.sql; do
            # Check for destructive operations without IF EXISTS
            if grep -qP 'DROP\s+(TABLE|COLUMN|INDEX)' "$file" && ! grep -qP 'IF EXISTS' "$file"; then
              echo "::warning::$file contains DROP without IF EXISTS"
            fi
          done

      - name: Stop Supabase
        if: always()
        run: supabase stop
```

## Template 3: Hebrew i18n Validation

Ensures parity between Hebrew and English locale files. Catches missing translations before they reach production.

```yaml
# .github/workflows/i18n-validation.yml
name: i18n Validation

on:
  pull_request:
    paths:
      - 'src/locales/**'
      - 'src/messages/**'
      - 'src/dictionaries/**'

jobs:
  validate-i18n:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Find locale files
        id: find-locales
        run: |
          # Support multiple common i18n directory structures
          for dir in src/locales src/messages src/dictionaries public/locales; do
            if [ -d "$dir" ]; then
              echo "locales_dir=$dir" >> $GITHUB_OUTPUT
              break
            fi
          done

      - name: Validate key parity
        run: |
          DIR="${{ steps.find-locales.outputs.locales_dir }}"
          HE="$DIR/he.json"
          EN="$DIR/en.json"

          if [ ! -f "$HE" ] || [ ! -f "$EN" ]; then
            echo "::error::Missing he.json or en.json in $DIR"
            exit 1
          fi

          HE_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$HE")
          EN_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$EN")

          MISSING_HE=$(comm -23 <(echo "$EN_KEYS") <(echo "$HE_KEYS"))
          MISSING_EN=$(comm -23 <(echo "$HE_KEYS") <(echo "$EN_KEYS"))

          EXIT_CODE=0

          if [ -n "$MISSING_HE" ]; then
            echo "::error::Keys in en.json missing from he.json:"
            echo "$MISSING_HE" | while read key; do
              echo "  - $key"
            done
            EXIT_CODE=1
          fi

          if [ -n "$MISSING_EN" ]; then
            echo "::warning::Keys in he.json missing from en.json (may be intentional):"
            echo "$MISSING_EN" | while read key; do
              echo "  - $key"
            done
          fi

          exit $EXIT_CODE

      - name: Check for empty translation values
        run: |
          DIR="${{ steps.find-locales.outputs.locales_dir }}"
          for lang in he en; do
            FILE="$DIR/$lang.json"
            EMPTY=$(jq -r '[paths(strings) as $p | {key: ($p | join(".")), val: getpath($p)} | select(.val == "")] | .[].key' "$FILE")
            if [ -n "$EMPTY" ]; then
              echo "::warning::Empty values in $lang.json:"
              echo "$EMPTY"
            fi
          done

      - name: Validate no Hebrew in code blocks (SKILL files)
        run: |
          # Check SKILL_HE.md for Hebrew text inside code blocks (breaks RTL rendering)
          if [ -f "SKILL_HE.md" ]; then
            IN_CODE=false
            LINE_NUM=0
            while IFS= read -r line; do
              LINE_NUM=$((LINE_NUM + 1))
              if echo "$line" | grep -q '```'; then
                if [ "$IN_CODE" = false ]; then
                  IN_CODE=true
                else
                  IN_CODE=false
                fi
              elif [ "$IN_CODE" = true ]; then
                if echo "$line" | grep -qP '[\u0590-\u05FF]'; then
                  echo "::warning file=SKILL_HE.md,line=$LINE_NUM::Hebrew text inside code block (will render LTR)"
                fi
              fi
            done < SKILL_HE.md
          fi
```

## Template 4: Israeli Compliance Pipeline

Combines IS-5568 accessibility, privacy checks, and security scanning into one workflow.

```yaml
# .github/workflows/compliance.yml
name: Israeli Compliance

on:
  pull_request:
    branches: [main]
  schedule:
    # Weekly scan on Sunday at 08:00 Israel time (UTC+2)
    - cron: '0 6 * * 0'

jobs:
  accessibility:
    name: IS-5568 Accessibility
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: '22'

      - run: npm ci
      - run: npm run build

      - name: Start server
        run: npm run start &
      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: axe-core WCAG 2.1 AA scan
        run: |
          npx @axe-core/cli http://localhost:3000 \
            --tags wcag2a,wcag2aa,wcag21aa \
            --exit

      - name: IS-5568 specific checks
        run: |
          HTML=$(curl -s http://localhost:3000)

          # Check dir="rtl"
          if ! echo "$HTML" | grep -q 'dir="rtl"'; then
            echo "::error::Missing dir=\"rtl\" on root element"
            exit 1
          fi

          # Check lang="he"
          if ! echo "$HTML" | grep -q 'lang="he"'; then
            echo "::error::Missing lang=\"he\" attribute"
            exit 1
          fi

          # Check for skip navigation link
          if ! echo "$HTML" | grep -qiE 'skip.*(nav|content|main)|דילוג.*תוכן'; then
            echo "::warning::No skip-to-content link detected (IS-5568 recommended)"
          fi

          # Check for accessibility statement link
          if ! echo "$HTML" | grep -qiE 'accessibility|נגישות'; then
            echo "::warning::No accessibility statement link detected (IS-5568 required for government sites)"
          fi

          echo "IS-5568 checks completed"

  privacy:
    name: Privacy (PPA) Compliance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Scan for PII patterns
        run: |
          # Israeli ID number pattern (9 digits)
          PII_HITS=$(grep -rn '[0-9]\{9\}' src/ --include="*.ts" --include="*.tsx" --include="*.js" \
            | grep -v 'test\|mock\|spec\|\.d\.ts\|node_modules' || true)

          if [ -n "$PII_HITS" ]; then
            echo "::warning::Potential Israeli ID numbers found. Review these matches:"
            echo "$PII_HITS"
          fi

      - name: Check consent mechanisms
        run: |
          # Look for cookie consent / privacy banner
          CONSENT=$(grep -rl 'cookie.*consent\|privacy.*banner\|gdpr\|consent.*manager' src/ || true)
          if [ -z "$CONSENT" ]; then
            echo "::warning::No cookie consent mechanism detected. Israeli PPA requires informed consent for data collection."
          fi

      - name: Audit tracking dependencies
        run: |
          TRACKERS="google-analytics|@segment|mixpanel|amplitude|hotjar|fullstory|heap"
          FOUND=$(grep -E "$TRACKERS" package.json || true)
          if [ -n "$FOUND" ]; then
            echo "::notice::Analytics dependencies detected. Verify PPA-compliant consent is implemented:"
            echo "$FOUND"
          fi

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Check for exposed secrets
        run: |
          # Common Israeli service API key patterns
          PATTERNS="sk_live|pk_live|SUPABASE_SERVICE_ROLE|RESEND_API_KEY|MONDAY_API_TOKEN"
          HITS=$(grep -rn "$PATTERNS" src/ --include="*.ts" --include="*.tsx" --include="*.js" \
            | grep -v '\.env\|\.example\|process\.env\|secrets\.\|vars\.' || true)

          if [ -n "$HITS" ]; then
            echo "::error::Potential exposed secrets found:"
            echo "$HITS"
            exit 1
          fi

      - name: npm audit
        run: npm audit --production --audit-level=high
        continue-on-error: true
```

## Template 5: Monday.com Sync Workflow

Syncs GitHub issue and PR status with Monday.com boards. Uses branch naming convention `feat/MON-{item_id}-description`.

```yaml
# .github/workflows/monday-sync.yml
name: Monday.com Sync

on:
  pull_request:
    types: [opened, closed, reopened, ready_for_review]
  issues:
    types: [opened, closed, reopened]

jobs:
  sync-monday:
    runs-on: ubuntu-latest
    env:
      MONDAY_TOKEN: ${{ secrets.MONDAY_API_TOKEN }}
      MONDAY_BOARD_ID: ${{ vars.MONDAY_BOARD_ID }}
    steps:
      - name: Extract Monday.com item ID
        id: extract
        run: |
          # Try branch name first (PRs), then issue title
          REF="${{ github.head_ref || github.ref_name }}"
          TITLE="${{ github.event.pull_request.title || github.event.issue.title }}"

          ITEM_ID=$(echo "$REF" | grep -oP 'MON-\K\d+' || echo "$TITLE" | grep -oP 'MON-\K\d+' || true)

          if [ -n "$ITEM_ID" ]; then
            echo "item_id=$ITEM_ID" >> $GITHUB_OUTPUT
            echo "found=true" >> $GITHUB_OUTPUT
          else
            echo "found=false" >> $GITHUB_OUTPUT
          fi

      - name: Determine status
        if: steps.extract.outputs.found == 'true'
        id: status
        run: |
          EVENT="${{ github.event_name }}"
          ACTION="${{ github.event.action }}"

          if [ "$EVENT" = "pull_request" ]; then
            case "$ACTION" in
              opened|reopened|ready_for_review) STATUS="In Review" ;;
              closed)
                if [ "${{ github.event.pull_request.merged }}" = "true" ]; then
                  STATUS="Done"
                else
                  STATUS="Working on it"
                fi
                ;;
            esac
          elif [ "$EVENT" = "issues" ]; then
            case "$ACTION" in
              opened|reopened) STATUS="Working on it" ;;
              closed) STATUS="Done" ;;
            esac
          fi

          echo "status=$STATUS" >> $GITHUB_OUTPUT

      - name: Update Monday.com
        if: steps.extract.outputs.found == 'true'
        run: |
          ITEM_ID="${{ steps.extract.outputs.item_id }}"
          STATUS="${{ steps.status.outputs.status }}"

          curl -s -X POST "https://api.monday.com/v2" \
            -H "Authorization: $MONDAY_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"mutation { change_simple_column_value(item_id: $ITEM_ID, board_id: $MONDAY_BOARD_ID, column_id: \\\"status\\\", value: \\\"$STATUS\\\") { id } }\"}"

          echo "Updated Monday.com item $ITEM_ID to '$STATUS'"
```

## Secrets and Variables Checklist

Before using these templates, configure these repository secrets and variables:

| Type | Name | Required By | Description |
|------|------|-------------|-------------|
| Secret | `VERCEL_TOKEN` | Template 1 | Vercel deployment token |
| Secret | `VERCEL_ORG_ID` | Template 1 | Vercel organization ID |
| Secret | `VERCEL_PROJECT_ID` | Template 1 | Vercel project ID |
| Secret | `SLACK_WEBHOOK_URL` | Templates 1, 4 | Slack Incoming Webhook URL |
| Secret | `MONDAY_API_TOKEN` | Template 5 | Monday.com API v2 token |
| Variable | `MONDAY_BOARD_ID` | Template 5 | Monday.com board ID |
| Secret | `SUPABASE_ACCESS_TOKEN` | Template 2 | Supabase CLI access token |
| Secret | `AWS_ROLE_ARN` | AWS deploys | AWS IAM role for OIDC |

Store secrets via: `gh secret set SECRET_NAME --body "value"`
Store variables via: `gh variable set VAR_NAME --body "value"`
