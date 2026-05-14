# Shabbat Deploy Freeze Implementation Guide

This reference covers the full implementation of Shabbat and Jewish holiday deploy freezes in GitHub Actions, including timezone handling, multi-environment strategies, edge cases, and emergency overrides.

## How Shabbat Times Work

Shabbat begins at candle lighting time on Friday and ends at havdalah on Saturday night. These times vary by:
- **Week**: Candle lighting ranges from ~16:10 (December) to ~19:45 (June) in Israel
- **City**: Jerusalem lights 40 minutes before sunset, Tel Aviv 20-30 minutes before, Haifa 22 minutes before
- **Custom**: Some communities add extra minutes before candle lighting

There is no fixed time. Do not hardcode "Friday 18:00" or any other static time.

## Hebcal API Reference

The hebcal API provides accurate Shabbat and holiday times for any location.

**Shabbat times endpoint:**
```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid={ID}&M=on
```

Parameters:
- `cfg=json` -- JSON response format
- `geonameid` -- GeoNames ID for the city
- `M=on` -- Include havdalah time

Common Israeli city IDs:

| City | GeoNames ID |
|------|-------------|
| Jerusalem | 281184 |
| Tel Aviv | 293397 |
| Haifa | 294801 |
| Be'er Sheva | 295530 |
| Eilat | 295277 |

**Response structure:**
```json
{
  "title": "Hebcal Jerusalem March 2026",
  "items": [
    {
      "title": "Candle lighting: 5:12pm",
      "date": "2026-03-20T17:12:00+02:00",
      "category": "candles"
    },
    {
      "title": "Parashat Vayakhel",
      "date": "2026-03-21",
      "category": "parashat"
    },
    {
      "title": "Havdalah: 6:26pm",
      "date": "2026-03-21T18:26:00+02:00",
      "category": "havdalah"
    }
  ]
}
```

**Holiday times endpoint:**
```
GET https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&year={YEAR}&month={MONTH}&geo=geoname&geonameid={ID}
```

Parameters:
- `maj=on` -- Major holidays only (Rosh Hashana, Yom Kippur, Sukkot, Pesach, Shavuot)
- `min=on` -- Include minor holidays (Purim, Chanukah, etc.)
- Add `yto=on` for Yom Tov only (days with work restrictions)

## Full Composite Action Implementation

This action handles Shabbat, holidays, and pre-Shabbat Friday buffer:

```yaml
# .github/actions/shabbat-check/action.yml
name: 'Shabbat/Holiday Deploy Freeze Check'
description: 'Determines if deployment should be frozen due to Shabbat or Israeli holidays'
inputs:
  city:
    description: 'Israeli city for Shabbat times'
    default: 'jerusalem'
  pre_shabbat_buffer_minutes:
    description: 'Minutes before candle lighting to start freeze'
    default: '60'
  check_holidays:
    description: 'Also check for Jewish holidays'
    default: 'true'
outputs:
  is_frozen:
    description: 'true if deploys should be frozen'
    value: ${{ steps.check.outputs.frozen }}
  reason:
    description: 'Reason for freeze (Shabbat, holiday name, or none)'
    value: ${{ steps.check.outputs.reason }}
  next_window:
    description: 'When the next deploy window opens (ISO 8601)'
    value: ${{ steps.check.outputs.next_window }}
runs:
  using: 'composite'
  steps:
    - id: resolve-city
      shell: bash
      run: |
        case "${{ inputs.city }}" in
          jerusalem) echo "geonameid=281184" >> $GITHUB_OUTPUT ;;
          tel-aviv|telaviv) echo "geonameid=293397" >> $GITHUB_OUTPUT ;;
          haifa) echo "geonameid=294801" >> $GITHUB_OUTPUT ;;
          beer-sheva|beersheva) echo "geonameid=295530" >> $GITHUB_OUTPUT ;;
          eilat) echo "geonameid=295277" >> $GITHUB_OUTPUT ;;
          *) echo "geonameid=281184" >> $GITHUB_OUTPUT ;;  # Default to Jerusalem
        esac

    - id: check
      shell: bash
      run: |
        GEONAMEID="${{ steps.resolve-city.outputs.geonameid }}"
        BUFFER="${{ inputs.pre_shabbat_buffer_minutes }}"

        # Fetch Shabbat times
        SHABBAT_JSON=$(curl -sf "https://www.hebcal.com/shabbat?cfg=json&geonameid=$GEONAMEID&M=on" || echo '{"items":[]}')

        CANDLE=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="candles") | .date' | head -1)
        HAVDALAH=$(echo "$SHABBAT_JSON" | jq -r '.items[] | select(.category=="havdalah") | .date' | head -1)

        NOW_EPOCH=$(date +%s)

        FROZEN="false"
        REASON="none"
        NEXT_WINDOW=""

        if [ -n "$CANDLE" ] && [ -n "$HAVDALAH" ]; then
          # Convert to epoch for comparison
          CANDLE_EPOCH=$(date -d "$CANDLE" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%S%z" "$CANDLE" +%s 2>/dev/null)
          HAVDALAH_EPOCH=$(date -d "$HAVDALAH" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%S%z" "$HAVDALAH" +%s 2>/dev/null)

          # Apply pre-Shabbat buffer
          FREEZE_START=$((CANDLE_EPOCH - BUFFER * 60))

          if [ "$NOW_EPOCH" -ge "$FREEZE_START" ] && [ "$NOW_EPOCH" -le "$HAVDALAH_EPOCH" ]; then
            FROZEN="true"

            if [ "$NOW_EPOCH" -lt "$CANDLE_EPOCH" ]; then
              REASON="Pre-Shabbat buffer (candle lighting in less than ${BUFFER} minutes)"
            else
              REASON="Shabbat"
            fi

            NEXT_WINDOW=$(date -d "@$HAVDALAH_EPOCH" --iso-8601=seconds 2>/dev/null || date -r "$HAVDALAH_EPOCH" +%Y-%m-%dT%H:%M:%S%z 2>/dev/null)
          fi
        fi

        # Check holidays (if enabled and not already frozen)
        if [ "$FROZEN" = "false" ] && [ "${{ inputs.check_holidays }}" = "true" ]; then
          YEAR=$(date +%Y)
          MONTH=$(date +%-m)
          HOLIDAYS_JSON=$(curl -sf "https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&yto=on&year=$YEAR&month=$MONTH&geo=geoname&geonameid=$GEONAMEID" || echo '{"items":[]}')

          TODAY=$(date +%Y-%m-%d)
          HOLIDAY_TODAY=$(echo "$HOLIDAYS_JSON" | jq -r ".items[] | select(.date | startswith(\"$TODAY\")) | .title" | head -1)

          if [ -n "$HOLIDAY_TODAY" ]; then
            FROZEN="true"
            REASON="Holiday: $HOLIDAY_TODAY"
            # Holidays typically end at the same time as Shabbat (havdalah)
            NEXT_WINDOW="Check hebcal for holiday end time"
          fi
        fi

        echo "frozen=$FROZEN" >> $GITHUB_OUTPUT
        echo "reason=$REASON" >> $GITHUB_OUTPUT
        echo "next_window=$NEXT_WINDOW" >> $GITHUB_OUTPUT

        # Summary for Actions UI
        if [ "$FROZEN" = "true" ]; then
          echo "### Deploy Frozen" >> $GITHUB_STEP_SUMMARY
          echo "**Reason:** $REASON" >> $GITHUB_STEP_SUMMARY
          if [ -n "$NEXT_WINDOW" ]; then
            echo "**Next window:** $NEXT_WINDOW" >> $GITHUB_STEP_SUMMARY
          fi
        else
          echo "### Deploy Window Open" >> $GITHUB_STEP_SUMMARY
          echo "No Shabbat or holiday restrictions at this time." >> $GITHUB_STEP_SUMMARY
        fi
```

## Multi-Environment Strategy

Different environments may have different freeze policies:

| Environment | Freeze Policy | Rationale |
|-------------|---------------|-----------|
| Production | Full freeze (Shabbat + holidays + 60 min buffer) | No one available for incident response |
| Staging | Shabbat only (no buffer) | Lower risk, developers may test Friday afternoon |
| Development | No freeze | Internal only, no user impact |

Implement with environment-specific inputs:

```yaml
jobs:
  check-freeze:
    runs-on: ubuntu-latest
    outputs:
      is_frozen: ${{ steps.check.outputs.is_frozen }}
    steps:
      - uses: actions/checkout@v5
      - id: check
        uses: ./.github/actions/shabbat-check
        with:
          pre_shabbat_buffer_minutes: ${{ github.ref == 'refs/heads/main' && '60' || '0' }}
          check_holidays: ${{ github.ref == 'refs/heads/main' && 'true' || 'false' }}
```

## Emergency Override

For genuine emergencies (production down, security incident), the team needs to deploy during a freeze.

**Override via workflow_dispatch:**

```yaml
on:
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Override Shabbat/holiday freeze (EMERGENCY ONLY)'
        type: boolean
        default: false
      override_reason:
        description: 'Reason for emergency override (required if force_deploy is true)'
        type: string
        required: false
```

**Gate with validation and audit logging:**

```yaml
- name: Validate override
  if: github.event.inputs.force_deploy == 'true'
  run: |
    REASON="${{ github.event.inputs.override_reason }}"
    if [ -z "$REASON" ]; then
      echo "::error::Emergency override requires a reason. Please provide override_reason."
      exit 1
    fi

    echo "### EMERGENCY OVERRIDE" >> $GITHUB_STEP_SUMMARY
    echo "**Override by:** ${{ github.actor }}" >> $GITHUB_STEP_SUMMARY
    echo "**Reason:** $REASON" >> $GITHUB_STEP_SUMMARY
    echo "**Time:** $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $GITHUB_STEP_SUMMARY

- name: Notify team of emergency deploy
  if: github.event.inputs.force_deploy == 'true'
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    RTL=$'\u200F'
    curl -s -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{\"attachments\":[{\"color\":\"#dc3545\",\"blocks\":[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"${RTL}*פריסת חירום בשבת/חג*\n${RTL}מפתח: ${{ github.actor }}\n${RTL}סיבה: ${{ github.event.inputs.override_reason }}\"}}]}]}"
```

## Timezone Edge Cases

### DST Transitions

Israel observes DST (Israel Daylight Time, IDT):
- **Clocks forward**: Last Friday before April 2, at 02:00 (becomes 03:00)
- **Clocks back**: Last Sunday before October, at 02:00 (becomes 01:00)

During the transition weeks, cron schedules shift by 1 hour. The hebcal API always returns times with the correct UTC offset, so the shabbat-check action handles this correctly. Cron-based schedules (like "daily CI run at 09:00 Israel time") will drift by 1 hour during transition weeks.

Mitigation options:
1. **Accept the drift.** For most teams, running the morning CI at 08:00 or 10:00 for one week is fine.
2. **Use two cron entries.** Schedule for both UTC+2 and UTC+3 and add a runtime check to skip the wrong one.
3. **Use the hebcal API at runtime.** Instead of cron, trigger on `push` and check if it is within working hours.

### Erev Shabbat / Friday Afternoon

Many Israeli teams stop work before candle lighting. The `pre_shabbat_buffer_minutes` input handles this:
- 60 minutes (default): Freeze starts 1 hour before candle lighting. Safe for most teams.
- 120 minutes: Conservative, ensures no deploys after ~14:00 in winter.
- 0 minutes: Freeze starts exactly at candle lighting. For teams that work up to the last minute.

### Two-Day Holidays

Some holidays span two days (Rosh Hashana, first two days of Sukkot, first two days of Pesach, last two days of Pesach). When a holiday falls on Thursday-Friday, it extends directly into Shabbat, creating a three-day freeze.

The hebcal API reports each day separately. The current action checks only today's date. For multi-day holidays, the check runs on each day and will correctly freeze on each day independently.

### Yom Kippur

Yom Kippur starts before sunset (like Shabbat) and is the strictest holiday. Deploy freezes should start earlier, ideally by noon on Erev Yom Kippur. Consider adding special handling:

```yaml
# In the holiday check section:
if echo "$HOLIDAY_TODAY" | grep -qi "yom kippur\|erev yom kippur"; then
  FROZEN="true"
  REASON="Yom Kippur (extended freeze)"
fi
```

## Queuing Deploys for After Shabbat

Instead of dropping frozen deploys, queue them for automatic deployment after havdalah:

```yaml
- name: Queue deploy for after Shabbat
  if: steps.shabbat.outputs.is_frozen == 'true'
  uses: peter-evans/repository-dispatch@v4
  with:
    event-type: queued-deploy
    client-payload: |
      {
        "ref": "${{ github.sha }}",
        "queued_by": "${{ github.actor }}",
        "queued_at": "${{ github.event.head_commit.timestamp }}",
        "deploy_after": "${{ steps.shabbat.outputs.next_window }}"
      }
```

Then create a separate workflow that polls for queued deploys:

```yaml
# .github/workflows/process-queued-deploys.yml
name: Process Queued Deploys

on:
  schedule:
    # Check every hour on Saturday evening and Sunday morning (UTC)
    - cron: '0 16-22 * * 6'  # Saturday 18:00-00:00 Israel (winter)
    - cron: '0 5-8 * * 0'    # Sunday morning Israel (winter)

jobs:
  check-queue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - id: shabbat
        uses: ./.github/actions/shabbat-check
      - name: Process queue
        if: steps.shabbat.outputs.is_frozen != 'true'
        run: |
          # Fetch queued deploy events and trigger them
          echo "Processing queued deploys..."
          # Implementation depends on your queue mechanism
```

## Testing the Freeze Locally

Use the `act` CLI to test the shabbat-check action locally:

```bash
# Install act
brew install act

# Test the action with a mock time
act -j check-deploy-window --env TZ=Asia/Jerusalem

# Simulate a Friday evening run
TZ=Asia/Jerusalem faketime '2026-03-20 18:00:00' act -j check-deploy-window
```

Without `act`, test the hebcal API directly:

```bash
# Check current Shabbat times for Jerusalem
curl -s "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on" | jq '.items[] | {category, date, title}'

# Check holidays this month
curl -s "https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&year=2026&month=3&geo=geoname&geonameid=281184" | jq '.items[] | {title, date}'
```
