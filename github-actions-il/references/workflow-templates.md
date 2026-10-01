# Reusable Workflow Templates for Israeli Teams

This reference contains complete, copy-paste-ready GitHub Actions workflow YAML templates designed for Israeli development teams. Each template encodes Israeli-specific conventions: Sunday-Thursday scheduling, Shabbat awareness, Hebrew notifications, and regional deployment targets.

## Template 1: Lint, Test, Deploy (Israeli Startup Stack)

A standard CI/CD pipeline for Israeli startups using Node.js. Runs on Israeli work days, deploys to Vercel fra1, and sends Hebrew Slack notifications.

**Before using it with Vercel:** if the project is connected through Vercel's Git integration, Vercel deploys every push to `main` by itself and the Shabbat gate below never sees it. Add `"git": {"deploymentEnabled": {"main": false}}` to `vercel.json` so production ships only from this workflow.

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
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Bypass the Shabbat/holiday freeze (production incidents only)'
        type: boolean
        default: false
      override_reason:
        description: 'Why the freeze is being bypassed (recorded in the run summary)'
        type: string

concurrency:
  # cancel-in-progress is right for CI on a branch and WRONG for a deploy: cancelling a
  # half-finished production rollout is worse than queueing behind it. Keyed on the event
  # so a push-triggered deploy is never killed by the next push.
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      # pnpm BEFORE setup-node, so setup-node's `cache: pnpm` can find the store.
      # No `version:` here: the action reads `packageManager` from package.json. Setting
      # both to different strings ("9" vs "pnpm@9.15.0") fails the step with
      # "Multiple versions of pnpm specified". Add `version:` only if package.json has
      # no packageManager field.
      - uses: pnpm/action-setup@v6

      # Node 24 is supported until 2028-04-30 (Maintenance from 2026-10-20). Node 26
      # becomes LTS on 2026-10-28; move to it once your dependencies support it.
      - uses: actions/setup-node@v7
        with:
          node-version: '24'
          cache: pnpm

      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test

  build:
    needs: lint-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v6
      - uses: actions/setup-node@v7
        with:
          node-version: '24'
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm build

  deploy-preview:
    if: github.event_name == 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write   # required for the github-script PR comment below (newer repos default GITHUB_TOKEN to read-only)
    steps:
      - uses: actions/checkout@v7
      - name: Deploy Preview to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npx vercel pull --yes --environment=preview --token=$VERCEL_TOKEN
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
    # workflow_dispatch must be allowed through, otherwise the force_deploy input added
    # above is unreachable and an hebcal outage hard-blocks production with no escape.
    if: github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')
    needs: build
    # Pin the image on the production path: ubuntu-latest moves to 26.04 between
    # 2026-10-19 and 2026-11-19. Move this line deliberately after testing on 26.04.
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    # A deployment environment holds the production secrets and can carry deployment-branch
    # rules, which a job-level if: cannot: anyone can edit an if: in a PR.
    environment: production
    steps:
      - uses: actions/checkout@v7

      - id: shabbat
        uses: ./.github/actions/shabbat-check

      - name: Deploy to Vercel Production
        id: deploy
        # NOT always(): if the gate step crashes it never writes its output, is_frozen is
        # empty, and always() would let '' != 'true' deploy during Shabbat. success() keeps
        # a crashed gate blocking; the explicit force_deploy arm is the documented escape.
        if: |
          (success() && steps.shabbat.outputs.is_frozen == 'false')
          || (github.event_name == 'workflow_dispatch' && inputs.force_deploy)
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          # pull defaults to the DEVELOPMENT environment; name production explicitly.
          npx vercel pull --yes --environment=production --token=$VERCEL_TOKEN
          npx vercel build --prod --token=$VERCEL_TOKEN
          npx vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN --regions fra1

      - name: Notify Slack
        # Only when the deploy step actually ran. job.status stays 'success' when the
        # deploy was SKIPPED by the freeze, which would announce a deploy that never happened.
        if: always() && steps.deploy.outcome != 'skipped'
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
          # Untrusted context is bound here, never interpolated into the run: script.
          STATUS: ${{ steps.deploy.outcome }}
          RAW_COMMIT_MSG: ${{ github.event.head_commit.message }}
          ACTOR: ${{ github.actor }}
        run: |
          if [ "$STATUS" = "success" ]; then
            STATUS_HE="הצליחה"; COLOR="#36a64f"
          else
            STATUS_HE="נכשלה"; COLOR="#dc3545"
          fi
          RTL=$'\u200F'
          # Build the payload with jq so Hebrew, quotes and newlines are escaped correctly,
          # and so untrusted context never reaches the shell as raw text. RAW_COMMIT_MSG and
          # ACTOR are bound in the step's env: block, never interpolated into this script.
          jq -n --arg color "$COLOR" --arg status "$STATUS_HE" \
                  --arg msg "$(printf '%s' "$RAW_COMMIT_MSG" | head -1)" --arg actor "$ACTOR" --arg rtl "$RTL" \
              '{attachments:[{color:$color,blocks:[{type:"section",text:{type:"mrkdwn",
                text:($rtl+"*פריסה לפרודקשן "+$status+"*\n"+$rtl+"קומיט: "+$msg+"\n"+$rtl+"מפתח: "+$actor)}}]}]}' \
              | curl -s -X POST "$SLACK_WEBHOOK" -H 'Content-Type: application/json' -d @-

      - name: Notify frozen
        # Also when the gate step itself failed: then nothing was deployed and no other
        # message would go out.
        if: always() && (steps.shabbat.outputs.is_frozen == 'true' || steps.shabbat.outcome == 'failure')
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
          REASON: ${{ steps.shabbat.outputs.reason }}
        run: |
          REASON="${REASON:-the Shabbat gate step failed}"
          RTL=$'\u200F'
          # Nothing in this template queues the deploy, so the message must not promise that
          # it will resume by itself. Say what actually has to happen.
          jq -n --arg rtl "$RTL" --arg reason "$REASON" \
            '{attachments:[{color:"#ffc107",blocks:[{type:"section",text:{type:"mrkdwn",
              text:($rtl+"*פריסה הוקפאה*\n"+$rtl+"סיבה: "+$reason+"\n"+$rtl+"הריצו את ה-workflow מחדש אחרי צאת השבת/החג, או השתמשו ב-workflow_dispatch עם force_deploy במקרה תקלה בייצור")}}]}]}' \
            | curl -s -X POST "$SLACK_WEBHOOK" -H 'Content-Type: application/json' -d @-
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
      - uses: actions/checkout@v7

      - uses: supabase/setup-cli@v3
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
      - uses: actions/checkout@v7

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
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: '24'

      - run: npm ci
      - run: npm run build

      - name: Start server
        run: npm run start &
      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: axe-core WCAG 2.0/2.1 A+AA scan
        run: |
          # Use the runner's ChromeDriver, which matches its Chrome; the CLI otherwise
          # pulls chromedriver@latest, which can be a major version ahead.
          npx @axe-core/cli http://localhost:3000 \
            --chromedriver-path "$CHROMEWEBDRIVER/chromedriver" \
            --tags wcag2a,wcag2aa,wcag21a,wcag21aa \
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
      - uses: actions/checkout@v7

      - name: Scan for PII patterns
        run: |
          # Any 9-digit run. No check-digit validation, so expect false positives
          # (timestamps, phone numbers); this is a prompt for review, not a detector.
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
      - uses: actions/checkout@v7

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
        run: npm audit --omit=dev --audit-level=high
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
        env:
          # A PR title and a fork's branch name are attacker-controlled free text. Bind them
          # here; interpolating ${{ }} into the script below would run a title containing
          # $(...) as code, in a job that holds MONDAY_TOKEN.
          REF: ${{ github.head_ref || github.ref_name }}
          TITLE: ${{ github.event.pull_request.title || github.event.issue.title }}
        run: |
          # Try branch name first (PRs), then issue title

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
        env:
          EVENT: ${{ github.event_name }}
          ACTION: ${{ github.event.action }}
          MERGED: ${{ github.event.pull_request.merged }}
        run: |

          if [ "$EVENT" = "pull_request" ]; then
            case "$ACTION" in
              opened|reopened|ready_for_review) STATUS="In Review" ;;
              closed)
                if [ "$MERGED" = "true" ]; then
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

## Template 6: Org-Wide Shabbat Gate (Reusable Workflow)

Vendoring `.github/actions/shabbat-check` into every repo means every copy has to be fixed separately when the gate changes. Keep one copy in a central repo (here `your-org/ci-workflows`, holding the action from `references/shabbat-deploy-freeze.md`, the version WITH the `pre_shabbat_buffer_minutes` input, under `.github/actions/shabbat-check/`) and call it as a reusable workflow. If that repo is private, share it under its Settings > Actions > General > Access ("Accessible from repositories in the organization"), or the callers cannot resolve it.

```yaml
# your-org/ci-workflows/.github/workflows/shabbat-gate.yml
name: Shabbat gate

on:
  workflow_call:
    inputs:
      pre_shabbat_buffer_minutes:
        type: string
        default: '60'
    outputs:
      is_frozen:
        description: 'true if deploys should be frozen'
        value: ${{ jobs.gate.outputs.is_frozen }}
      reason:
        description: 'Why'
        value: ${{ jobs.gate.outputs.reason }}

jobs:
  gate:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    outputs:
      is_frozen: ${{ steps.check.outputs.is_frozen }}
      reason: ${{ steps.check.outputs.reason }}
    steps:
      # Pin to a full commit SHA, as the callers below pin this workflow; a moving ref lets
      # anyone with write access to ci-workflows change the production gate everywhere.
      - id: check
        uses: your-org/ci-workflows/.github/actions/shabbat-check@<40-char-sha>
        with:
          pre_shabbat_buffer_minutes: ${{ inputs.pre_shabbat_buffer_minutes }}
```

In each product repo:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Bypass the Shabbat/holiday freeze (production incidents only)'
        type: boolean
        default: false

jobs:
  gate:
    uses: your-org/ci-workflows/.github/workflows/shabbat-gate.yml@<40-char-sha>

  deploy:
    needs: gate
    # !cancelled() so the force_deploy arm still works when the gate job FAILED (always()
    # would also run it after someone cancels the run); the normal arm demands an
    # explicit 'false', so a crashed or empty gate stays closed.
    if: >-
      !cancelled() && (
        (needs.gate.result == 'success' && needs.gate.outputs.is_frozen == 'false')
        || (github.event_name == 'workflow_dispatch' && inputs.force_deploy)
      )
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    environment: production
    steps:
      # Re-check INSIDE the environment-protected job. The gate job above ran before any
      # approval wait; an approval clicked hours later must not deploy into Shabbat.
      - id: recheck
        uses: your-org/ci-workflows/.github/actions/shabbat-check@<40-char-sha>
        with:
          pre_shabbat_buffer_minutes: '60'   # keep equal to the gate job's buffer
      - uses: actions/checkout@v7
      - if: >-
          (success() && steps.recheck.outputs.is_frozen == 'false')
          || (github.event_name == 'workflow_dispatch' && inputs.force_deploy)
        run: echo "Deploying..."
```

The `gate` job still earns its place: when it reports frozen, the deploy job is skipped before it ever asks for an approval.

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
