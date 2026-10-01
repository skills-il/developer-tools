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

Match the team's need to a workflow template, then adapt it to the stack.

| Israeli Dev Need | Workflow Template | Key Actions / Tools |
|-----------------|-------------------|---------------------|
| Shabbat/holiday deploy freeze | `shabbat-deploy-freeze.yml` | hebcal API, cron schedule, environment protection rules |
| Hebrew Slack notifications | `hebrew-notifications.yml` | Slack Incoming Webhook, RTL text payload |
| Hebrew Teams notifications | `hebrew-notifications.yml` | Teams Workflows webhook, Adaptive Card |
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
        # ONE feed covers Shabbat AND holidays. The /shabbat endpoint honours maj=on and
        # returns `holiday` items together with their candle-lighting times, including the
        # EREV entries (Erev Yom Kippur, Erev Sukkot), so one small call has everything.
        # Pass TODAY in Israel time explicitly: runners are UTC, so a bare `date` is still
        # yesterday between 00:00 and 03:00 Israel time and would miss the chag.
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
        # A real feed always has a candle-lighting or a havdalah (not always both: the week
        # before Rosh Hashana returns only the two candle-lightings), so require one of them.
        ITEM_COUNT=$(echo "$FEED" | jq -r '[.items[]? | select(.category=="candles" or .category=="havdalah")] | length' 2>/dev/null || echo 0)
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

        # A candle-lighting with no havdalah after it in this feed: the window runs past the
        # feed's range. If it has started, we are inside it, so freeze.
        if [ "$FROZEN" = false ] && [ -n "$START" ] && [ "$NOW_EPOCH" -ge "$(date -d "$START" +%s)" ]; then
          FROZEN=true
          REASON="$LABEL (from $START, end not in feed)"
        fi

        echo "frozen=$FROZEN" >> $GITHUB_OUTPUT
        echo "reason=$REASON" >> $GITHUB_OUTPUT
```

2. Use this action as a gate in deployment workflows:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    environment: production   # holds the prod secrets; see the note below
    steps:
      - uses: actions/checkout@v7
      # The gate runs INSIDE the environment-protected job, i.e. after any approval wait.
      - id: shabbat
        uses: ./.github/actions/shabbat-check
      - id: deploy
        # == 'false', not != 'true': a crashed or empty gate must stay closed.
        if: steps.shabbat.outputs.is_frozen == 'false'
        run: echo "Deploying..."
      - name: Notify frozen
        if: steps.shabbat.outputs.is_frozen == 'true'
        env:
          # The reason carries a title from hebcal's response; bind it, never ${{ }} it.
          FREEZE_REASON: ${{ steps.shabbat.outputs.reason }}
        run: |
          echo "Deploy frozen: $FREEZE_REASON"   # send it to Slack, see Step 3
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

Then change the deploy step condition (explicit `success()` stops GitHub adding an implicit one, so the override still works when the gate step crashed):

```yaml
if: >
  (success() && steps.shabbat.outputs.is_frozen == 'false') ||
  (github.event_name == 'workflow_dispatch' && inputs.force_deploy)
```

> **Note:** `references/shabbat-deploy-freeze.md` has the same gate plus a configurable pre-Shabbat buffer and per-city geonameids, multi-environment strategies and the emergency-override workflow. Not covered: minor fasts and Chanukah/Purim (`min=on`) and Yom HaZikaron/Yom HaAtzmaut (`mod=on`). Many Israeli teams also freeze on Yom HaZikaron; add the parameter if you do.

**Why `environment: production`.** An `if:` is just YAML, so anyone who can open a PR can edit it. Put the production secrets on a deployment environment instead, and add a deployment-branch rule so only `main` can use it. Plan limits: on Free, environment secrets work only in public repos; required reviewers are public-only on Free, Pro and Team; deployment-branch rules work on private repos with Pro or Team. Keep the gate inside that job: a gate in an earlier job can say "open" at 13:00 while an approval clicked at 18:30 deploys into Shabbat.

For the full implementation guide with edge cases and timezone handling, consult `references/shabbat-deploy-freeze.md`. To share one gate across many repos instead of copying it into each, use the reusable workflow in `references/workflow-templates.md` (Template 6).

### Step 3: Configure Hebrew Notifications

Hebrew text in webhook payloads requires explicit RTL handling. Slack and Teams handle this differently.

**Slack (Incoming Webhook):**

```yaml
- name: Notify Slack (Hebrew)
  if: always()
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
    # NEVER interpolate ${{ }} directly into a run: script. GitHub substitutes it as raw
    # text BEFORE bash parses the line, so a commit message containing a backtick or
    # $(...) executes in a job that holds your deploy tokens. Bind untrusted context to
    # env vars, then read them as ordinary shell variables.
    STATUS: ${{ job.status }}
    REPO: ${{ github.repository }}
    BRANCH: ${{ github.ref_name }}
    RAW_COMMIT_MSG: ${{ github.event.head_commit.message }}
    ACTOR: ${{ github.actor }}
  run: |
    COMMIT_MSG=$(printf '%s' "$RAW_COMMIT_MSG" | head -1)

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

    # jq escapes quotes and newlines, so a commit message cannot break the JSON.
    jq -n --arg color "$COLOR" --arg rtl "$RTL" --arg emoji "$EMOJI" --arg st "$STATUS_HE" \
          --arg repo "$REPO" --arg branch "$BRANCH" --arg msg "$COMMIT_MSG" --arg actor "$ACTOR" \
      '{attachments:[{color:$color,blocks:[{type:"section",text:{type:"mrkdwn",
        text:($emoji+" "+$rtl+"*פריסה "+$st+"*\n"+$rtl+"ריפו: `"+$repo+"`\n"+$rtl+"ענף: `"+$branch+"`\n"+$rtl+"קומיט: "+$msg+"\n"+$rtl+"מפתח: "+$actor)}}]}]}' \
      | curl -s -X POST "$SLACK_WEBHOOK" -H 'Content-Type: application/json' -d @-
```

Prefix each Hebrew line with U+200F and keep repo and branch names in English; mrkdwn (`*bold*`, `` `code` ``) works fine with Hebrew.

**Teams (Adaptive Card):** `TEAMS_WEBHOOK_URL` must come from the Teams **Workflows** app (template "Send webhook alerts to a channel"). Office 365 Connector incoming webhooks stopped working in May 2026; a connector URL now fails, so replace it rather than debugging the payload. Workflows accepts the same `attachments` envelope:

```yaml
- name: Notify Teams (Hebrew)
  if: always()
  env:
    TEAMS_WEBHOOK: ${{ secrets.TEAMS_WEBHOOK_URL }}
    STATUS: ${{ job.status }}
    REPO: ${{ github.repository }}
    BRANCH: ${{ github.ref_name }}
    ACTOR: ${{ github.actor }}
  run: |
    case "$STATUS" in
      success) STATUS_HE="הצליחה" ;;
      failure) STATUS_HE="נכשלה" ;;
      *)       STATUS_HE="בוטלה" ;;
    esac

    jq -n --arg st "$STATUS_HE" --arg repo "$REPO" --arg branch "$BRANCH" --arg actor "$ACTOR" \
      '{type:"message",attachments:[{contentType:"application/vnd.microsoft.card.adaptive",
        content:{type:"AdaptiveCard",version:"1.5",rtl:true,body:[
          {type:"TextBlock",text:("פריסה "+$st),weight:"Bolder",size:"Medium"},
          {type:"FactSet",facts:[{title:"ריפו",value:$repo},{title:"ענף",value:$branch},{title:"מפתח",value:$actor}]}]}}]}' \
      | curl -s -X POST "$TEAMS_WEBHOOK" -H 'Content-Type: application/json' -d @-
```

**Monday.com status update:**

```yaml
- name: Update Monday.com item
  env:
    MONDAY_TOKEN: ${{ secrets.MONDAY_API_TOKEN }}
    # A fork's branch name is attacker-controlled; bind it rather than interpolating it.
    REF_NAME: ${{ github.ref_name }}
    BOARD_ID: ${{ vars.MONDAY_BOARD_ID }}
  run: |
    # Extract Monday.com item ID from branch name or commit message
    # Convention: branch names like "feat/MON-12345-feature-name"
    ITEM_ID=$(printf '%s' "$REF_NAME" | grep -oP 'MON-\K\d+' || true)

    if [ -n "$ITEM_ID" ]; then
      STATUS_LABEL="${{ job.status == 'success' && 'Deployed' || 'Failed' }}"

      curl -s -X POST "https://api.monday.com/v2" \
        -H "Authorization: $MONDAY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"mutation { change_simple_column_value(item_id: $ITEM_ID, board_id: $BOARD_ID, column_id: \\\"status\\\", value: \\\"$STATUS_LABEL\\\") { id } }\"}"
    fi
```

### Step 4: Add Israeli Compliance Checks

**IS-5568 Accessibility (Israeli Standard)**

IS-5568 is the Israeli web-accessibility standard made binding by the Equal Rights for Persons with Disabilities (accessibility of a service) regulations. It adopts WCAG with additional requirements for Hebrew/RTL content. The WCAG edition it points at has moved between revisions of the standard, so confirm the level your obligation is assessed against with the Standards Institution of Israel rather than assuming; scanning against WCAG 2.1 AA satisfies 2.0 AA as a superset, which is why the axe configuration below passes the 2.0 and 2.1 A/AA tag sets. `@axe-core/cli` has no locale option; the RTL/lang step below covers Hebrew. Key differences from WCAG alone:

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
    - uses: actions/checkout@v7
    - uses: actions/setup-node@v7
      with:
        node-version: '24'

    - run: npm ci
    - run: npm run build
    - name: Start server in the background
      run: npm run start &
    - name: Wait for server
      run: npx wait-on http://localhost:3000 --timeout 60000

    - name: Run axe-core scan
      run: |
        # The runner's ChromeDriver matches its Chrome; chromedriver@latest may not.
        npx @axe-core/cli http://localhost:3000 \
          --chromedriver-path "$CHROMEWEBDRIVER/chromedriver" \
          --tags wcag2a,wcag2aa,wcag21a,wcag21aa \
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
    - uses: actions/checkout@v7

    - name: Scan for exposed PII patterns
      run: |
        # Any 9-digit run. No check-digit validation, so expect false positives;
        # treat hits as a prompt for review, not as detected PII.
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

| Cloud Provider | Recommended Region | Relative latency from Israel | GitHub Actions Setup |
|---------------|-------------------|---------------|---------------------|
| Vercel | fra1 (Frankfurt) | low | `vercel --regions fra1` |
| AWS | il-central-1 (Tel Aviv) or eu-west-1 (Ireland) | lowest / higher | Set `AWS_DEFAULT_REGION` |
| GCP | europe-west1 (Belgium) or me-west1 (Tel Aviv) | higher / lowest | Set `GOOGLE_CLOUD_REGION` |
| Cloudflare Workers | Automatic (TLV edge) | lowest | No region config needed |
| DigitalOcean | fra1 (Frankfurt) | low | `doctl apps create --region fra` |

The latency column is a relative ranking, not a measurement. Measure from your own users, and weigh in-country regions against their thinner service catalogue.

**Vercel deployment with fra1 pinning:**

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
        # pull defaults to the DEVELOPMENT environment; name production explicitly.
        npx vercel pull --yes --environment=production --token=$VERCEL_TOKEN
        npx vercel build --prod --token=$VERCEL_TOKEN
        npx vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN --regions fra1
```

**Turn off Vercel's own Git deploys for `main`, or the freeze does nothing.** A project connected through Vercel's Git integration deploys every push by itself, outside GitHub Actions. Add `"git": {"deploymentEnabled": {"main": false}}` to `vercel.json` so production ships only from the gated workflow.

**AWS deployment with region selection:**

```yaml
deploy-aws:
  runs-on: ubuntu-latest
  permissions:
    id-token: write   # REQUIRED for OIDC role assumption; without it the action fails with "Unable to get OIDC token"
    contents: read
  env:
    AWS_DEFAULT_REGION: il-central-1  # AWS Tel Aviv. Opt-in region: enable it on the account first, or use eu-west-1
  steps:
    - uses: aws-actions/configure-aws-credentials@v6
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    # ... deployment steps
```

**Token permissions and security hardening.** Since February 2023 new organizations and repos get a **read-only** default `GITHUB_TOKEN` (older repos may still default to read/write; check Settings > Actions), so any job that writes (commenting on a PR, pushing a commit, creating a release) must declare an explicit `permissions:` block, and OIDC cloud auth (above) requires `id-token: write`. Set least-privilege permissions per job:

```yaml
permissions:
  contents: read          # safe baseline
# add only what a job needs, for example:
# pull-requests: write    # for github-script PR comments
# id-token: write         # for OIDC to AWS/GCP (no long-lived secret keys)
```

Additional hardening for an Israeli team's repos:
- **Pin third-party actions to a full commit SHA** (`uses: owner/action@<40-char-sha>`), not a moving tag. A moving tag was the vector in the 2025 tj-actions/changed-files supply-chain compromise. First-party `actions/*` are lower risk, but SHA-pinning is the standard.
- **Enable Dependabot for actions** (`.github/dependabot.yml` with `package-ecosystem: "github-actions"`) so pinned versions stay current automatically. This is the maintenance answer to action staleness.
- **`actions/checkout` refuses fork checkouts under `pull_request_target` by default.** From v7 (and backported to v4/v5/v6) the action rejects the classic "pwn request" patterns, including `ref: ${{ github.event.pull_request.head.sha }}` and `repository: ${{ github.event.pull_request.head.repo.full_name }}`, because those workflows run with the base repo's `GITHUB_TOKEN` and secrets. The action exposes `allow-unsafe-pr-checkout: true` as an explicit opt-out; treat it as a last resort, and prefer the `pull_request` trigger plus a separate privileged `workflow_run` job. If an older workflow of yours suddenly fails at the checkout step, this is why.
- **Set `timeout-minutes` on every job.** The default is 360 (six hours). It matters here specifically because the Shabbat gate makes a network call to a third-party API on the critical path of every production deploy: `--max-time` bounds the curl, but only `timeout-minutes` bounds the job. `timeout-minutes: 10` on the gate job and 30 on a deploy job are sane starting points.

### Step 6: Configure Israeli Work Week Scheduling

Israeli work week is Sunday through Thursday. Friday is a half-day (typically until 13:00-14:00). Cron schedules in GitHub Actions use UTC, so convert accordingly (Israel is UTC+2, or UTC+3 during DST).

**Common Israeli cron patterns (UTC times):**

| Schedule (Israel time) | Cron (UTC, winter) | Cron (UTC, summer) | Use case |
|------------------------|--------------------|--------------------|----------|
| Sun-Thu 09:00 | `0 7 * * 0-4` | `0 6 * * 0-4` | Morning CI run |
| Sun-Thu 17:00 | `0 15 * * 0-4` | `0 14 * * 0-4` | End-of-day deploy |
| Fri 12:00 (half-day cutoff) | `0 10 * * 5` | `0 9 * * 5` | Last Friday deploy |
| Daily except Shabbat | `0 7 * * 0-5` | `0 6 * * 0-5` | Weekday + Friday morning |

**Handling DST transitions**: Israel enters DST on the Friday before the last Sunday of March, and returns to standard time on the last Sunday of October (27 Mar and 25 Oct in 2026; 26 Mar and 31 Oct in 2027). Either accept a 1-hour drift in those weeks or check the offset at runtime.

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

Good candidates: the Shabbat gate from Step 2, the Hebrew Slack notifier from Step 3, and an i18n check that fails a PR when `he.json` is missing keys present in `en.json` (Template 3 in the references file does this with `jq paths(scalars)` and `comm`). Pin cross-repo actions to a full SHA, and prefer a reusable workflow (Template 6) when the same job is copied into many repos.

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
2. Configure axe-core with the WCAG 2.0/2.1 A and AA tags
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
6. Gate production deploys on Shabbat/holiday check, and set `git.deploymentEnabled.main: false` in `vercel.json`
7. Add Hebrew Slack notifications for all pipeline stages

Result: Complete CI/CD pipeline respecting Israeli work culture, with compliance checks, bilingual i18n validation, and Shabbat-aware production deploys.

## Bundled Resources

### References
- `references/workflow-templates.md` -- Complete, copy-paste-ready YAML workflow templates for Israeli startup CI/CD: lint-test-deploy, Supabase migration CI, i18n validation, and full Israeli compliance pipeline. Consult when setting up a new project's workflows from scratch.
- `references/shabbat-deploy-freeze.md` -- Detailed implementation guide for Shabbat and holiday deploy freezes, including hebcal API usage, timezone edge cases, multi-environment strategies, and emergency override procedures. Consult when implementing or debugging the deploy freeze system.

## Recommended MCP Servers

- **hebcal**: Jewish calendar and Shabbat times, for an agent that needs holiday data while authoring a workflow (the workflow itself still calls the HTTP API).

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
- **Shabbat times vary weekly and by city.** Agents tend to hardcode "Friday 18:00" as Shabbat start. In reality, candle lighting across Israeli cities runs from about 15:55 (Jerusalem, early-to-mid December) to about 19:30 (Tel Aviv, June), and Jerusalem lights roughly 20 minutes earlier than Tel Aviv because it keeps a 40-minute-before-sunset custom (Haifa uses 30). Always use the hebcal API for accurate times.
- **Three ways an agent silently breaks the freeze while the workflow still looks correct.** First, hebcal returns offset-aware times (`2026-08-28T18:28:00+03:00`); comparing that lexicographically against `date -u` is wrong by the offset and leaves the gate open for the first hours of Shabbat. Convert both bounds to epoch seconds with `date -d`. Second, pass `gy`/`gm`/`gd` for today computed under `TZ=Asia/Jerusalem`, so "today" means Israel's today: a runner's bare `date` is still yesterday between 00:00 and 03:00 Israel time. Third, a two-day yom tov emits TWO candle-lightings before a single havdalah, so keep the EARLIEST unclosed one; overwriting it tests only the second night and deploys run through the whole of Rosh Hashana day one.
- **Hebrew text in YAML needs RTL markers.** Without the RTL mark character (U+200F), Hebrew text in Slack payloads renders with punctuation in the wrong position. Always prefix Hebrew lines with `\u200F`.
- **IS-5568 is not just WCAG 2.1 AA.** Agents treat IS-5568 as a synonym for WCAG. IS-5568 has additional Israeli-specific requirements around bilingual content, government logos, and contact accessibility.
- **`il-central-1` (Tel Aviv) is an opt-in AWS region.** It is disabled on an account until someone enables it, so a workflow that assumes it fails at the credentials or API call. Confirm it is enabled, or fall back to `eu-west-1`.
- **`ubuntu-latest` moves to Ubuntu 26.04 between 2026-10-19 and 2026-11-19.** A deploy job that worked yesterday can break mid-rollout with no change in the repo. Pin `ubuntu-24.04` on production jobs and move deliberately. On 26.04, `/tmp` is a RAM-backed tmpfs with a per-user quota of about 7.8 GB, so large builds writing there fail with "disk quota exceeded".
- **Node 20 is gone from the runners (removed 2026-09-23).** An action whose `action.yml` still says `using: node20` is now run on Node 24, and `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` no longer brings Node 20 back. If such an action breaks, that is why; bump it to a release built for `node24`.
- **`pnpm/action-setup` fails when `version:` and `packageManager` disagree.** `version: 9` beside `"packageManager": "pnpm@9.15.0"` is a mismatch and aborts with "Multiple versions of pnpm specified". Omit `version:` when `package.json` declares `packageManager`.
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
Solution: Subtract 2 hours (winter) or 3 hours (summer) from the desired Israel time, and accept a 1-hour drift around DST changes or add a runtime check.

### Error: "axe-core scan finds no violations but site is not accessible"
Cause: Automated scanning catches only a minority of accessibility issues (commonly cited as roughly a third). IS-5568 requires manual testing for reading order, screen reader behavior, and bilingual content flow.
Solution: Use axe-core as a baseline, not a complete check. Add manual accessibility review as a PR checklist item alongside the automated scan.

### Error: "Monday.com mutation returns 'unauthorized'"
Cause: The API token does not have permission for the target board, or the `board_id` is wrong.
Solution: Verify the token has write access to the board. Check `MONDAY_BOARD_ID` in repository variables. Test with a simple query first: `{ boards(ids: [BOARD_ID]) { name } }`.