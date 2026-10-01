# Shabbat Deploy Freeze Implementation Guide

This reference covers the full implementation of Shabbat and Jewish holiday deploy freezes in GitHub Actions, including timezone handling, multi-environment strategies, edge cases, and emergency overrides.

## How Shabbat Times Work

Shabbat begins at candle lighting time on Friday and ends at havdalah on Saturday night. These times vary by:
- **Week**: Candle lighting ranges from about 15:55 (Jerusalem, early-to-mid December) to about 19:30 (Tel Aviv, June). Jerusalem lights roughly 20 minutes earlier than Tel Aviv, about 10 earlier than Haifa.
- **City**: hebcal's defaults are 18 minutes before sundown, 40 for Jerusalem and 30 for Haifa (and Zikhron Ya'akov); Tel Aviv uses the 18-minute default
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
- `M=on` -- havdalah at nightfall (tzeit hakochavim) rather than a fixed number of minutes after sundown

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

**Holidays come from the same endpoint.** Add `maj=on` and pass `gy`/`gm`/`gd` for today and `/shabbat` returns `holiday` items (including the erev entries such as Erev Yom Kippur) together with the candle-lighting and havdalah that bound each chag. Each full yom tov carries `yomtov: true`; chol hamoed, fast days and Shabbat Shuva do not. One call therefore covers Shabbat and holidays, which is what the action below relies on. The month-wide `/hebcal` endpoint lists the same holidays (erev entries included) and is handy for browsing a calendar, but the gate only needs the few days around today, which `/shabbat` returns in one small response with the candle-lighting and havdalah times already attached.

## Full Composite Action Implementation

This is the SKILL.md Step 2 gate with two inputs added: a city and a pre-Shabbat buffer. The freeze logic is identical (single `/shabbat?maj=on` feed for TODAY in `Asia/Jerusalem`, epoch-second comparison, earliest unclosed candle-lighting, `yomtov` rule for a chag already in progress, fail closed on any error), so the two files cannot drift apart again. If you change one, change both.

```yaml
# .github/actions/shabbat-check/action.yml
name: 'Shabbat/Holiday Deploy Freeze Check'
description: 'Determines if deployment should be frozen due to Shabbat or Israeli holidays'
inputs:
  city:
    description: 'Israeli city for Shabbat times (jerusalem, tel-aviv, haifa, beer-sheva, eilat)'
    default: 'jerusalem'
  pre_shabbat_buffer_minutes:
    description: 'Minutes before candle lighting to start the freeze'
    default: '60'
outputs:
  is_frozen:
    description: 'true if deploys should be frozen'
    value: ${{ steps.check.outputs.frozen }}
  reason:
    description: 'Reason for freeze (Shabbat, holiday name, or none)'
    value: ${{ steps.check.outputs.reason }}
  next_window:
    description: 'When the current freeze ends (havdalah, ISO 8601), empty if not frozen'
    value: ${{ steps.check.outputs.next_window }}
runs:
  using: 'composite'
  steps:
    - id: check
      shell: bash
      env:
        CITY: ${{ inputs.city }}
        BUFFER: ${{ inputs.pre_shabbat_buffer_minutes }}
      run: |
        case "$CITY" in
          tel-aviv|telaviv) GEONAMEID=293397 ;;
          haifa) GEONAMEID=294801 ;;
          beer-sheva|beersheva) GEONAMEID=295530 ;;
          eilat) GEONAMEID=295277 ;;
          *) GEONAMEID=281184 ;;  # Jerusalem: the earliest candle-lighting, so the safest default
        esac
        case "$BUFFER" in ''|*[!0-9]*) BUFFER=60 ;; esac

        freeze() {
          { echo "frozen=true"; echo "reason=$1"; echo "next_window=$2"; } >> "$GITHUB_OUTPUT"
          { echo "### Deploy Frozen"; echo "**Reason:** $1"; } >> "$GITHUB_STEP_SUMMARY"
          exit 0
        }

        # Today in Israel time: runners are UTC, so a bare `date` is still yesterday
        # between 00:00 and 03:00 Israel time and would miss the chag.
        export TZ=Asia/Jerusalem
        CURL_OK=0
        FEED=$(curl -sf --max-time 10 --retry 2 \
          "https://www.hebcal.com/shabbat?cfg=json&geonameid=$GEONAMEID&M=on&maj=on&gy=$(date +%Y)&gm=$(date +%-m)&gd=$(date +%-d)") || CURL_OK=$?

        # Fail CLOSED on an outage AND on a 200 with an unexpected shape.
        if [ "$CURL_OK" -ne 0 ] || [ -z "$FEED" ]; then
          freeze "Could not reach hebcal; failing closed. Override with force_deploy." ""
        fi
        # A real feed always has a candle-lighting or a havdalah (not always both: the week
        # before Rosh Hashana returns only the two candle-lightings), so require one of them.
        ITEM_COUNT=$(echo "$FEED" | jq -r '[.items[]? | select(.category=="candles" or .category=="havdalah")] | length' 2>/dev/null || echo 0)
        if [ -z "$ITEM_COUNT" ] || [ "$ITEM_COUNT" = "0" ] || [ "$ITEM_COUNT" = "null" ]; then
          freeze "hebcal returned no calendar items; failing closed. Override with force_deploy." ""
        fi

        NOW_EPOCH=$(date +%s)
        TODAY=$(date +%Y-%m-%d)

        # Rule 1: a full yom tov dated today, until today's closing havdalah.
        YOMTOV=$(echo "$FEED" | jq -r --arg d "$TODAY" '[.items[] | select(.yomtov == true and (.date | startswith($d)))] | first | .title // empty')
        if [ -n "$YOMTOV" ]; then
          END_TODAY=$(echo "$FEED" | jq -r --arg d "$TODAY" '[.items[] | select(.category=="havdalah" and (.date | startswith($d)))] | first | .date // empty')
          END_EPOCH=""
          [ -n "$END_TODAY" ] && END_EPOCH=$(date -d "$END_TODAY" +%s 2>/dev/null || echo "")
          if [ -z "$END_EPOCH" ] || [ "$NOW_EPOCH" -le "$END_EPOCH" ]; then
            freeze "$YOMTOV (yom tov)" "$END_TODAY"
          fi
        fi

        # Rule 2: inside [candle-lighting minus buffer, havdalah], keeping the EARLIEST
        # unclosed candle-lighting so a two-day chag is frozen from its first evening.
        START=""; LABEL="Shabbat"; PENDING="Shabbat"
        while IFS=$'\t' read -r CAT WHEN TITLE; do
          case "$CAT" in
            holiday) PENDING="$TITLE" ;;
            candles) if [ -z "$START" ]; then START="$WHEN"; LABEL="$PENDING"; fi ;;
            havdalah)
              EE=$(date -d "$WHEN" +%s)
              if [ -z "$START" ]; then
                # Window opened before this feed's range: already inside it.
                [ "$NOW_EPOCH" -le "$EE" ] && freeze "$PENDING (in progress)" "$WHEN"
              else
                SE=$(date -d "$START" +%s)
                if [ "$NOW_EPOCH" -ge $((SE - BUFFER * 60)) ] && [ "$NOW_EPOCH" -le "$EE" ]; then
                  if [ "$NOW_EPOCH" -lt "$SE" ]; then
                    freeze "Pre-$LABEL buffer (candle lighting at $START)" "$WHEN"
                  fi
                  freeze "$LABEL" "$WHEN"
                fi
              fi
              START=""; LABEL="Shabbat"; PENDING="Shabbat"
              ;;
          esac
        done < <(echo "$FEED" | jq -r '.items[] | [.category, .date, .title] | @tsv')

        # A candle-lighting with no havdalah after it: the window runs past the feed's range.
        if [ -n "$START" ] && [ "$NOW_EPOCH" -ge $(( $(date -d "$START" +%s) - BUFFER * 60 )) ]; then
          freeze "$LABEL (from $START, end not in feed)" ""
        fi

        { echo "frozen=false"; echo "reason=none"; echo "next_window="; } >> "$GITHUB_OUTPUT"
        { echo "### Deploy Window Open"; echo "No Shabbat or holiday restrictions at this time."; } >> "$GITHUB_STEP_SUMMARY"
```

## Multi-Environment Strategy

Different environments may have different freeze policies:

| Environment | Freeze Policy | Rationale |
|-------------|---------------|-----------|
| Production | Shabbat + holidays + 60 min buffer | No one available for incident response |
| Staging | Shabbat + holidays, no buffer | Lower risk, developers may test Friday afternoon |
| Development | No freeze | Internal only, no user impact |

Implement with environment-specific inputs:

```yaml
jobs:
  check-freeze:
    runs-on: ubuntu-latest
    outputs:
      is_frozen: ${{ steps.check.outputs.is_frozen }}
    steps:
      - uses: actions/checkout@v7
      - id: check
        uses: ./.github/actions/shabbat-check
        with:
          pre_shabbat_buffer_minutes: ${{ github.ref == 'refs/heads/main' && '60' || '0' }}
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
  env:
    # workflow_dispatch free text. Bind it; do not interpolate it into the script.
    REASON: ${{ github.event.inputs.override_reason }}
    ACTOR: ${{ github.actor }}
  run: |
    if [ -z "$REASON" ]; then
      echo "::error::Emergency override requires a reason. Please provide override_reason."
      exit 1
    fi

    echo "### EMERGENCY OVERRIDE" >> $GITHUB_STEP_SUMMARY
    echo "**Override by:** $ACTOR" >> $GITHUB_STEP_SUMMARY
    echo "**Reason:** $REASON" >> $GITHUB_STEP_SUMMARY
    echo "**Time:** $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $GITHUB_STEP_SUMMARY

- name: Notify team of emergency deploy
  if: github.event.inputs.force_deploy == 'true'
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
    ACTOR: ${{ github.actor }}
    REASON: ${{ github.event.inputs.override_reason }}
  run: |
    RTL=$'\u200F'
    # jq builds the JSON so a quote or newline in the reason cannot break the payload.
    jq -n --arg rtl "$RTL" --arg actor "$ACTOR" --arg reason "$REASON" \
      '{attachments:[{color:"#dc3545",blocks:[{type:"section",text:{type:"mrkdwn",
        text:($rtl+"*פריסת חירום בשבת/חג*\n"+$rtl+"מפתח: "+$actor+"\n"+$rtl+"סיבה: "+$reason)}}]}]}' \
      | curl -s -X POST "$SLACK_WEBHOOK" -H 'Content-Type: application/json' -d @-
```

## Timezone Edge Cases

### DST Transitions

Israel observes DST (Israel Daylight Time, IDT):
- **Clocks forward**: The Friday before the last Sunday of March, 27 Mar 2026 and 26 Mar 2027, at 02:00 (becomes 03:00)
- **Clocks back**: Last Sunday **of** October, at 02:00 (becomes 01:00), 25 Oct 2026 and 31 Oct 2027

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

In Israel only Rosh Hashana is a two-day yom tov; Sukkot, Shmini Atzeret, Pesach and Shavuot are one day each (the second days are a diaspora custom). A chag can still sit next to Shabbat, for example Rosh Hashana on Thursday and Friday running straight into Shabbat, which makes a three-day freeze.

Either way the feed emits more than one candle-lighting before a single havdalah. The action keeps the EARLIEST unclosed candle-lighting, so the freeze starts on the first evening. An implementation that overwrites it on each candles item tests only the last night and deploys freely through day one.

### Yom Kippur

Yom Kippur starts at candle lighting like any yom tov, and the action freezes from then until havdalah. Many teams want a longer lead time before it. `pre_shabbat_buffer_minutes` applies to every window, Shabbat included, so either set it to the lead time you want everywhere, or cover the erev-Yom-Kippur afternoon with a one-off manual hold (for example disabling the deploy workflow, or a required reviewer on the `production` environment). Do not match on holiday titles to special-case it: titles are display strings and change with transliteration.

## Catching Up After Shabbat

A frozen push is not lost, it is just not deployed yet. The reliable catch-up is to re-run the REAL pipeline after havdalah, so lint, tests, build and the gate all run again: a commit whose tests failed must not ship unattended on Saturday night. (A `repository_dispatch` "queue" fires immediately, during Shabbat; it is not a queue.)

```yaml
# .github/workflows/post-shabbat-catchup.yml
name: Post-Shabbat catch-up

on:
  schedule:
    # Saturday 19:00 UTC = 21:00 Israel winter / 22:00 summer. The latest havdalah in
    # Israel is about 20:35 IDT, so this is after havdalah all year.
    - cron: '0 19 * * 6'

jobs:
  redispatch:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions:
      actions: write   # needed to dispatch another workflow
    steps:
      # workflow_dispatch is one of the two events a GITHUB_TOKEN may trigger.
      - env:
          GH_TOKEN: ${{ github.token }}
        run: gh workflow run ci-cd.yml --repo "$GITHUB_REPOSITORY" --ref main
```

This re-runs Template 1 (`ci-cd.yml`) on `main`; its own gate still applies, so a Saturday night that is also erev chag, or a chag running from Saturday into Sunday, stays frozen. Re-run the pipeline by hand once that ends, or after a chag that ends on a weekday. It redeploys `main` even when nothing was frozen that week, which is harmless because a deploy of the same commit is idempotent.

## Testing the Freeze Locally

`act` runs each step inside a Docker container, so wrapping it in `faketime` changes the host clock, not the container's, and the test silently uses the real time. Test the gate's `run:` script directly instead, with stub `date` and `curl` commands first on `PATH`:

```bash
# fakebin/date: everything except `date -d ...` answers as if it were $FAKE_NOW
cat > fakebin/date <<'EOF'
#!/bin/bash
for a in "$@"; do case "$a" in -d|-d*|--date*) exec /usr/bin/date "$@";; esac; done
exec /usr/bin/date -d "@$FAKE_NOW" "$@"
EOF
chmod +x fakebin/date

# Friday 2026-03-20 18:00 Israel time, with the step's script saved as gate.sh
FAKE_NOW=$(TZ=Asia/Jerusalem date -d '2026-03-20 18:00' +%s) \
  GITHUB_OUTPUT=/dev/stdout GITHUB_STEP_SUMMARY=/dev/null \
  PATH="$PWD/fakebin:$PATH" bash -eo pipefail gate.sh
```

Point a stub `curl` at a saved response (or make it `exit 7`) to test the fail-closed paths. Use GNU `date` (Linux, or `gdate` on macOS).

Without a harness, check the hebcal feed directly:
```bash
# Check current Shabbat times for Jerusalem
curl -s "https://www.hebcal.com/shabbat?cfg=json&geonameid=281184&M=on" | jq '.items[] | {category, date, title}'

# Check holidays this month
curl -s "https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&year=2026&month=3&geo=geoname&geonameid=281184" | jq '.items[] | {title, date}'
```
