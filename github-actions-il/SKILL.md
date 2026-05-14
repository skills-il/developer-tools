---
name: github-actions-il
description: CI/CD workflow templates tailored for Israeli development teams, including Shabbat/holiday-aware deployment schedules ("shabbat deploy freeze", "hakpaaat prisa"), Hebrew Slack/Teams notifications, Israeli compliance checks (IS-5568 accessibility, Privacy Protection Authority), Monday.com issue sync, and reusable composite actions for Israeli startup stacks. Use when user asks to "set up CI/CD for Israeli team", "add Shabbat deploy freeze", "configure Hebrew notifications in GitHub Actions", "hakpaat prisa beshabbat", "add IS-5568 check to pipeline", "Israeli compliance CI", or "create workflow for Vercel fra1". Supports Israeli work week (Sunday-Thursday) scheduling and Hebrew locale awareness. Do NOT use for JFrog Artifactory pipelines (use jfrog-devops), general GitHub repository management, non-CI/CD GitHub Actions, or Jenkins/CircleCI/GitLab CI configurations.
license: MIT
allowed-tools: Bash(gh:*) Bash(git:*) Bash(curl:*) Bash(node:*) Bash(act:*)
compatibility: Requires GitHub repository with Actions enabled. GitHub CLI (gh) recommended for workflow management. act CLI optional for local workflow testing. Works with any GitHub-hosted or self-hosted runner.
---

# GitHub Actions for Israeli Teams

## Instructions

### Step 1: Choose the Right Workflow Pattern

Match the team's need to the appropriate workflow template. Use this table as a starting point, then customize based on the project's stack and deployment target.

| Israeli Dev Need | Workflow Template | Key Actions / Tools |
|-----------------|-------------------|---------------------|
| Shabbat/holiday deploy freeze | `shabbat-deploy-freeze.yml` | hebcal API, cron schedule, environment protection rules |
| Hebrew Slack notifications | `hebrew-notifications.yml` | Slack Incoming Webhook, RTL text payload |
| Hebrew Teams notifications | `hebrew-notifications.yml` | Teams Incoming Webhook, Adaptive Card with RTL |
| IS-5568 accessibility check | `compliance-checks.yml` | axe-core, pa11y, custom IS-5568 rules |
| Privacy compliance (GDPR-IL) | `compliance-checks.yml` | custom scanner, dependency audit |
| Monday.com issue sync | `monday-sync.yml` | Monday.com GraphQL API |
| Vercel fra1 deployment | `deploy-vercel.yml` | vercel CLI with `--regions fra1` |
| Supabase migration CI | `supabase-ci.yml` | supabase CLI, migration diff |
| Hebrew i18n validation | `i18n-validation.yml` | custom script, JSON/YAML schema check |
| Israeli work week scheduling | Any workflow | Cron with Sun-Thu schedule |

If the team has multiple needs, compose workflows by reusing composite actions from `references/workflow-templates.md`.

### Step 2: Set Up Shabbat/Holiday-Aware Scheduling

Israeli teams need deployment schedules that respect Shabbat (Friday afternoon through Saturday night) and Jewish holidays. This is not just cultural preference; deploying during Shabbat means no one is available to respond to incidents.

**Approach: Hebcal API + Environment Protection Rules**

1. Create a reusable workflow that checks whether the current time falls within a freeze window:

```yaml
# .github/actions/shabbat-check/action.yml
name: 'Shabbat/Holiday Check'
description: 'Check if current time is during Shabbat or Israeli holiday'
outputs:
  is_frozen:
    description: 'true if deploys should be frozen'
    value: ${{ steps.check.outputs.frozen }}
  reason:
    description: 'Why deploys are frozen (e.g., Shabbat, Yom Kippur)'
    value: ${{ steps.check.outputs.reason }}
runs:
  using: 'composite'
  steps:
    - id: check
      shell: bash
      run: |
        # Fetch Shabbat times for Israel (Jerusalem)
        SHABBAT_JSON=$(curl -s "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on")

        # Extract candle lighting and havdalah times
        CANDLE=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="candles") | .date')
        HAVDALAH=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="havdalah") | .date')

        NOW=$(date -u +%Y-%m-%dT%H:%M:%S)

        if [[ "$NOW" > "$CANDLE" && "$NOW" < "$HAVDALAH" ]]; then
          echo "frozen=true" >> $GITHUB_OUTPUT
          echo "reason=Shabbat (candle lighting: $CANDLE)" >> $GITHUB_OUTPUT
        else
          # Check holidays
          MONTH=$(date +%Y-%m)
          HOLIDAYS=$(curl -s "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&maj=on")
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

2. Use this action as a gate in deployment workflows:

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

  notify-frozen:
    needs: check-deploy-window
    if: needs.check-deploy-window.outputs.is_frozen == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Deploy frozen: ${{ needs.check-deploy-window.outputs.reason }}"
          # Send notification (see Step 3)
```

3. **Emergency override**: Add a `workflow_dispatch` input for overriding the freeze:

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

Then modify the deploy job condition:

```yaml
if: >
  needs.check-deploy-window.outputs.is_frozen != 'true' ||
  github.event.inputs.force_deploy == 'true'
```

> **Note:** The inline bash in the composite action above is illustrative. Its `[[ "$NOW" > "$CANDLE" ]]` lexical string comparison is fragile, it works only when both timestamps share the same timezone offset and string format, and it breaks across DST transitions and date rollovers. The canonical, correct implementation in `references/shabbat-deploy-freeze.md` converts every timestamp to epoch seconds before comparing and adds a configurable pre-Shabbat buffer. Use the reference implementation in real workflows.

For the full implementation guide with edge cases and timezone handling, consult `references/shabbat-deploy-freeze.md`.

### Step 3: Configure Hebrew Notifications

Hebrew text in webhook payloads requires explicit RTL handling. Slack and Teams handle this differently.

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
    COMMIT_MSG=$(echo "${{ github.event.head_commit.message }}" | head -1)
    ACTOR="${{ github.actor }}"

    if [ "$STATUS" = "success" ]; then
      EMOJI=":white_check_mark:"
      STATUS_HE="הצליח"
      COLOR="#36a64f"
    elif [ "$STATUS" = "failure" ]; then
      EMOJI=":x:"
      STATUS_HE="נכשל"
      COLOR="#dc3545"
    else
      EMOJI=":warning:"
      STATUS_HE="בוטל"
      COLOR="#ffc107"
    fi

    # RTL marker ensures Hebrew renders correctly in Slack
    RTL=$'\u200F'

    curl -s -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d @- <<EOF
    {
      "attachments": [{
        "color": "$COLOR",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "$EMOJI ${RTL}*פריסה ${STATUS_HE}*\n${RTL}ריפו: \`${REPO}\`\n${RTL}ענף: \`${BRANCH}\`\n${RTL}קומיט: ${COMMIT_MSG}\n${RTL}מפתח: ${ACTOR}"
            }
          }
        ]
      }]
    }
    EOF
```

**Key points for Hebrew in Slack:**
- Prefix Hebrew lines with the RTL mark character (U+200F) to force correct display
- Keep repository names, branch names, and technical identifiers in English (no translation needed)
- Slack mrkdwn formatting (`*bold*`, `` `code` ``) works fine with Hebrew text

**Teams (Adaptive Card):**

```yaml
- name: Notify Teams (Hebrew)
  if: always()
  env:
    TEAMS_WEBHOOK: ${{ secrets.TEAMS_WEBHOOK_URL }}
  run: |
    STATUS="${{ job.status }}"
    # ... same status mapping as Slack ...

    curl -s -X POST "$TEAMS_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d @- <<EOF
    {
      "type": "message",
      "attachments": [{
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
          "type": "AdaptiveCard",
          "version": "1.4",
          "body": [
            {
              "type": "TextBlock",
              "text": "פריסה ${STATUS_HE}",
              "weight": "Bolder",
              "size": "Medium"
            },
            {
              "type": "FactSet",
              "facts": [
                {"title": "ריפו", "value": "${REPO}"},
                {"title": "ענף", "value": "${BRANCH}"},
                {"title": "מפתח", "value": "${ACTOR}"}
              ]
            }
          ]
        }
      }]
    }
    EOF
```

**Monday.com status update:**

```yaml
- name: Update Monday.com item
  env:
    MONDAY_TOKEN: ${{ secrets.MONDAY_API_TOKEN }}
  run: |
    # Extract Monday.com item ID from branch name or commit message
    # Convention: branch names like "feat/MON-12345-feature-name"
    ITEM_ID=$(echo "${{ github.ref_name }}" | grep -oP 'MON-\K\d+' || true)

    if [ -n "$ITEM_ID" ]; then
      STATUS_LABEL="${{ job.status == 'success' && 'Deployed' || 'Failed' }}"

      curl -s -X POST "https://api.monday.com/v2" \
        -H "Authorization: Bearer $MONDAY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"mutation { change_simple_column_value(item_id: $ITEM_ID, board_id: ${{ vars.MONDAY_BOARD_ID }}, column_id: \\\"status\\\", value: \\\"$STATUS_LABEL\\\") { id } }\"}"
    fi
```

### Step 4: Add Israeli Compliance Checks

**IS-5568 Accessibility (Israeli Standard)**

IS-5568 is the Israeli accessibility standard, based on WCAG 2.1 AA with additional requirements for Hebrew/RTL content. Key differences from WCAG alone:

| IS-5568 Requirement | WCAG Equivalent | Additional Israeli Rule |
|---------------------|-----------------|------------------------|
| RTL text direction | N/A | `dir="rtl"` on root element, proper `lang="he"` |
| Bilingual content | 3.1.2 Language of Parts | Each language section must have explicit `lang` attribute |
| Government site logo | N/A | Must link to gov.il accessibility statement |
| Contact accessibility | N/A | Accessible phone number format (no images of numbers) |
| PDF accessibility | 1.3.1 Info and Relationships | Hebrew PDFs must have proper reading order and tagged structure |

Add to your CI pipeline:

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

    - name: Build project
      run: npm run build && npm run start &
      # Wait for server to be ready
    - name: Wait for server
      run: npx wait-on http://localhost:3000 --timeout 60000

    - name: Run axe-core scan
      run: |
        axe http://localhost:3000 \
          --tags wcag2a,wcag2aa,wcag21aa \
          --locale he \
          --exit

    - name: Check RTL and lang attributes (IS-5568 specific)
      run: |
        # Verify root element has dir="rtl" and lang="he"
        HTML=$(curl -s http://localhost:3000)

        if ! echo "$HTML" | grep -q 'dir="rtl"'; then
          echo "::error::Missing dir=\"rtl\" on root element (IS-5568 requirement)"
          exit 1
        fi

        if ! echo "$HTML" | grep -q 'lang="he"'; then
          echo "::error::Missing lang=\"he\" attribute (IS-5568 requirement)"
          exit 1
        fi

        echo "IS-5568 RTL/lang checks passed"
```

**Privacy Protection Authority (PPA) compliance checks:**

The Israeli Privacy Protection Authority (Rashut HaHagana al HaPratiut) requires specific handling of personal data. Add these automated checks:

```yaml
privacy-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v5

    - name: Scan for exposed PII patterns
      run: |
        # Israeli ID number pattern (9 digits with Luhn check)
        if grep -rn '[0-9]\{9\}' src/ --include="*.ts" --include="*.tsx" | \
           grep -v 'test\|mock\|spec\|\.d\.ts'; then
          echo "::warning::Potential Israeli ID numbers found in source code. Verify these are not real PII."
        fi

    - name: Check for privacy policy route
      run: |
        # Israeli law requires accessible privacy policy
        if ! find src -name "privacy*" -o -name "פרטיות*" | grep -q .; then
          echo "::warning::No privacy policy page detected. Israeli PPA requires one."
        fi

    - name: Audit dependencies for data collection
      run: |
        # Flag known analytics/tracking packages that may need PPA disclosure
        TRACKERS="google-analytics|segment|mixpanel|amplitude|hotjar|fullstory"
        if grep -E "$TRACKERS" package.json; then
          echo "::notice::Analytics dependencies detected. Ensure PPA-compliant consent banner is implemented."
        fi
```

### Step 5: Deploy to Israeli-Friendly Cloud Targets

Israeli projects should deploy to regions with low latency to Israel. Here are the recommended targets and how to configure them in workflows.

| Cloud Provider | Recommended Region | Latency to IL | GitHub Actions Setup |
|---------------|-------------------|---------------|---------------------|
| Vercel | fra1 (Frankfurt) | ~30ms | `vercel --regions fra1` |
| AWS | eu-west-1 (Ireland) or me-south-1 (Bahrain) | ~40ms / ~20ms | Set `AWS_DEFAULT_REGION` |
| GCP | europe-west1 (Belgium) or me-west1 (Tel Aviv) | ~35ms / ~5ms | Set `GOOGLE_CLOUD_REGION` |
| Cloudflare Workers | Automatic (TLV edge) | ~5ms | No region config needed |
| DigitalOcean | fra1 (Frankfurt) | ~30ms | `doctl apps create --region fra` |

**Vercel deployment with fra1 pinning:**

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

**AWS deployment with region selection:**

```yaml
deploy-aws:
  runs-on: ubuntu-latest
  env:
    AWS_DEFAULT_REGION: eu-west-1  # Or me-south-1 for Bahrain
  steps:
    - uses: aws-actions/configure-aws-credentials@v5
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    # ... deployment steps
```

### Step 6: Configure Israeli Work Week Scheduling

Israeli work week is Sunday through Thursday. Friday is a half-day (typically until 13:00-14:00). Cron schedules in GitHub Actions use UTC, so convert accordingly (Israel is UTC+2, or UTC+3 during DST).

**Common Israeli cron patterns (UTC times):**

| Schedule (Israel time) | Cron (UTC, winter) | Cron (UTC, summer) | Use case |
|------------------------|--------------------|--------------------|----------|
| Sun-Thu 09:00 | `0 7 * * 0-4` | `0 6 * * 0-4` | Morning CI run |
| Sun-Thu 17:00 | `0 15 * * 0-4` | `0 14 * * 0-4` | End-of-day deploy |
| Fri 12:00 (half-day cutoff) | `0 10 * * 5` | `0 9 * * 5` | Last Friday deploy |
| Daily except Shabbat | `0 7 * * 0-5` | `0 6 * * 0-5` | Weekday + Friday morning |

**Handling DST transitions**: Israel switches to DST on the last Friday before April 2, and back on the last Sunday before October. Rather than maintaining two cron schedules, use the hebcal API to determine the current UTC offset dynamically, or accept a 1-hour drift during transition weeks.

```yaml
on:
  schedule:
    # Sunday-Thursday at 09:00 Israel time (winter UTC+2)
    - cron: '0 7 * * 0-4'
    # Friday at 12:00 Israel time (last deploy before Shabbat)
    - cron: '0 10 * * 5'
```

### Step 7: Create Reusable Composite Actions

Build a library of composite actions that encode Israeli startup conventions. These live in `.github/actions/` and can be shared across repositories.

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
          echo "::error::Missing locale files. Expected $HE_FILE and $EN_FILE"
          exit 1
        fi

        # Extract keys from both files
        HE_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$HE_FILE")
        EN_KEYS=$(jq -r '[paths(scalars)] | map(join(".")) | sort[]' "$EN_FILE")

        # Find missing keys
        MISSING_HE=$(comm -23 <(echo "$EN_KEYS") <(echo "$HE_KEYS"))
        MISSING_EN=$(comm -23 <(echo "$HE_KEYS") <(echo "$EN_KEYS"))

        if [ -n "$MISSING_HE" ]; then
          echo "::error::Keys in en.json missing from he.json:"
          echo "$MISSING_HE" | while read key; do
            echo "  - $key"
          done
          exit 1
        fi

        if [ -n "$MISSING_EN" ]; then
          echo "::warning::Keys in he.json missing from en.json:"
          echo "$MISSING_EN"
        fi

        echo "i18n validation passed"
```

For complete workflow YAML templates, consult `references/workflow-templates.md`.

## Examples

### Example 1: Set Up Shabbat-Aware Deployment

User says: "Add a Shabbat deploy freeze to our production deployment workflow"

Actions:
1. Create `.github/actions/shabbat-check/action.yml` with the hebcal integration from Step 2
2. Add the `SLACK_WEBHOOK_URL` secret to the repository
3. Modify the existing deploy workflow to gate on the shabbat-check output
4. Add `workflow_dispatch` with `force_deploy` input for emergencies
5. Add Hebrew Slack notification for frozen deploys

Result: Production deploys automatically pause from candle lighting Friday through havdalah Saturday, with Hebrew notifications explaining the freeze and an emergency override option.

### Example 2: Add Israeli Compliance to CI Pipeline

User says: "We need IS-5568 accessibility checks in our pull request CI"

Actions:
1. Add the `accessibility-check` job from Step 4 to the PR workflow
2. Configure axe-core with WCAG 2.1 AA + Hebrew locale
3. Add the RTL/lang attribute check specific to IS-5568
4. Add the privacy policy route check
5. Set the job as a required status check in branch protection rules

Result: Every PR is checked for IS-5568 compliance, RTL correctness, and privacy policy presence. Failures block merge.

### Example 3: Configure Hebrew Slack Notifications with Monday.com Sync

User says: "Set up Hebrew deploy notifications in Slack and update Monday.com tickets"

Actions:
1. Add `SLACK_WEBHOOK_URL` and `MONDAY_API_TOKEN` as repository secrets
2. Add the Hebrew Slack notification step from Step 3
3. Add the Monday.com status update step, using branch naming convention `feat/MON-{id}-description`
4. Configure both notifications in the `if: always()` block so they fire on success and failure

Result: Deploy status appears in Slack with RTL Hebrew text, and the corresponding Monday.com item moves to "Deployed" or "Failed" status.

### Example 4: Israeli Startup Full CI/CD Setup

User says: "We're an Israeli startup using Next.js + Supabase + Vercel. Set up our entire CI/CD."

Actions:
1. Create lint/test/build workflow running on Sunday-Thursday schedule
2. Add Supabase migration diff check on PRs
3. Add Hebrew i18n validation (he.json / en.json key parity)
4. Add IS-5568 accessibility scan on PRs
5. Create Vercel deploy workflow with fra1 region pinning
6. Gate production deploys on Shabbat/holiday check
7. Add Hebrew Slack notifications for all pipeline stages

Result: Complete CI/CD pipeline respecting Israeli work culture, with compliance checks, bilingual i18n validation, and Shabbat-aware production deploys.

## Bundled Resources

### References
- `references/workflow-templates.md` -- Complete, copy-paste-ready YAML workflow templates for Israeli startup CI/CD: lint-test-deploy, Supabase migration CI, i18n validation, and full Israeli compliance pipeline. Consult when setting up a new project's workflows from scratch.
- `references/shabbat-deploy-freeze.md` -- Detailed implementation guide for Shabbat and holiday deploy freezes, including hebcal API usage, timezone edge cases, multi-environment strategies, and emergency override procedures. Consult when implementing or debugging the deploy freeze system.

## Recommended MCP Servers

- **hebcal**: Hebrew/Jewish calendar and Shabbat times. An MCP alternative to calling the Hebcal HTTP API inside a composite action, useful when an agent needs holiday data while authoring or reasoning about a workflow rather than at runtime.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| GitHub Actions Documentation | https://docs.github.com/en/actions | Workflow syntax, cron schedules, composite actions, environments |
| Hebcal Shabbat API | https://www.hebcal.com/home/developer-apis | Shabbat times, holiday calendar, geonameid values |
| Monday.com API | https://developer.monday.com/api-reference/docs | GraphQL schema, mutations, authentication |
| Standards Institution of Israel | https://www.sii.org.il/en/ | IS-5568 standard, accessibility certification |
| Vercel Regions | https://vercel.com/docs/edge-network/regions | Region codes (fra1) and latency reference |

## Gotchas

- **Cron schedules use UTC, not Israel time.** Agents default to writing cron schedules in local time. Israel is UTC+2 (winter) or UTC+3 (summer/DST). A `0 9 * * 0-4` cron means 09:00 UTC, which is 11:00 or 12:00 in Israel. Always convert.
- **Israeli work week is Sunday-Thursday, not Monday-Friday.** Agents consistently write `1-5` for weekday cron (Monday-Friday). For Israeli teams, use `0-4` (Sunday-Thursday) or `0-5` (Sunday-Friday half-day).
- **Shabbat times vary weekly and by city.** Agents tend to hardcode "Friday 18:00" as Shabbat start. In reality, candle lighting ranges from ~16:10 in winter to ~19:45 in summer. Always use the hebcal API for accurate times.
- **Hebrew text in YAML needs RTL markers.** Without the RTL mark character (U+200F), Hebrew text in Slack payloads renders with punctuation in the wrong position. Always prefix Hebrew lines with `\u200F`.
- **IS-5568 is not just WCAG 2.1 AA.** Agents treat IS-5568 as a synonym for WCAG. IS-5568 has additional Israeli-specific requirements around bilingual content, government logos, and contact accessibility.
- **`me-south-1` (Bahrain) is NOT available to all AWS accounts.** This region requires opt-in activation. Do not assume it is available. Fall back to `eu-west-1` if the user has not explicitly enabled it.
- **Monday.com API v2 uses GraphQL only.** Agents sometimes try REST endpoints for Monday.com. The API is exclusively GraphQL at `https://api.monday.com/v2`.
- **GitHub Actions `schedule` event runs on the default branch only.** Agents sometimes add scheduled workflows on feature branches and wonder why they do not trigger.

## Troubleshooting

### Error: "Hebcal API returns empty items"
Cause: The `geonameid` parameter is wrong, or the date range has no Shabbat (edge case in query timing).
Solution: Use `geonameid=281184` for Jerusalem. Verify by opening `https://www.hebcal.com/shabbat?cfg=json&geonameid=281184` in a browser. If items are empty, check that the request is not cached from a previous week.

### Error: "Hebrew text appears reversed in Slack"
Cause: Missing RTL mark character in the payload. Slack does not auto-detect text direction.
Solution: Prefix every Hebrew line with `$'\u200F'` in bash, or `\u200F` in JSON strings. Test by sending a simple Hebrew message to the webhook first.

### Error: "Cron schedule fires at wrong time"
Cause: Schedule written in Israel time instead of UTC.
Solution: Subtract 2 hours (winter) or 3 hours (summer) from the desired Israel time. Use `date -u` to verify current UTC time. For DST-proof scheduling, accept the 1-hour drift or add a runtime check.

### Error: "axe-core scan finds no violations but site is not accessible"
Cause: Automated scanning catches only ~30% of accessibility issues. IS-5568 requires manual testing for reading order, screen reader behavior, and bilingual content flow.
Solution: Use axe-core as a baseline, not a complete check. Add manual accessibility review as a PR checklist item alongside the automated scan.

### Error: "Monday.com mutation returns 'unauthorized'"
Cause: The API token does not have permission for the target board, or the `board_id` is wrong.
Solution: Verify the token has write access to the board. Check `MONDAY_BOARD_ID` in repository variables. Test with a simple query first: `{ boards(ids: [BOARD_ID]) { name } }`.