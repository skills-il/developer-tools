# Shabbat-Aware Scheduling Patterns for n8n

Pre-built patterns for n8n workflows that need to respect Shabbat and Jewish holidays.

## Core Concept

n8n's built-in Schedule Trigger node has no concept of Shabbat or Jewish holidays. The solution is a two-node pattern at the start of every scheduled workflow:

1. **Schedule Trigger** fires on schedule
2. **Shabbat Gate** (HTTP Request + Code) checks if it is currently Shabbat or a holiday, and stops the workflow if so

This pattern is appended to the beginning of every schedule-triggered workflow. It adds ~500ms latency per check (one API call to Hebcal).

## Pattern 1: Weekly Business Workflow (Sunday-Thursday)

For workflows that should run during Israeli business days only.

**Schedule Trigger cron expression:** `0 9 * * 0-4` (9:00 AM, Sunday through Thursday)

Israeli business week is Sunday (0) through Thursday (4), so this cron never fires on Shabbat itself.

**That is not the same as "no gate needed", and treating it that way is how a workflow runs on Yom Kippur.** Six of Israel's eight yom tov days in 2026 fall inside Sunday-to-Thursday: Pesach I (Thu 2 Apr), Pesach VII (Wed 8 Apr), Rosh Hashana II (Sun 13 Sep), Yom Kippur (Mon 21 Sep), and the surrounding erev days. A weekday cron therefore still needs the holiday gate from Pattern 3. Excluding Friday and Saturday only removes Shabbat, and Shabbat is the minority of the problem.

Note also that the cron is interpreted in the instance timezone. With `GENERIC_TIMEZONE=Asia/Jerusalem` set as the skill requires, `0 9` means 09:00 Israel time. Do not carry over UTC-based cron expressions from a tutorial.

## Pattern 2: Daily Workflow with Shabbat Gate

For workflows that run every day but must pause during Shabbat.

**Schedule Trigger cron expression:** `0 */3 * * *` (every 3 hours)

**Shabbat Gate Code Node:**

**Two bugs to avoid, both of which let the workflow run when it must not.**

*Bug 1: taking the first `candles` and the first `havdalah` and assuming they bracket a period.* They often do not. When the request is made DURING a chag, Hebcal returns that chag's `havdalah` first and the NEXT festival's `candles` days later, so the "interval" runs backwards and `now >= start && now <= end` can never be true. Verified against the live API: on Yom Kippur, `/shabbat?geonameid=293397&gy=2026&gm=9&gd=21` returns `havdalah 2026-09-21T19:15+03:00` BEFORE `candles 2026-09-25T18:13+03:00`. A naive gate lets the workflow run on Yom Kippur. Pair each `candles` with the FIRST `havdalah` that comes after it, and reject any pair that is not ordered.

*Bug 2: failing open.* If Hebcal is unreachable, WAF-blocked, or returns a changed shape, `items` is missing and a `proceed with caution` fallback sends customer messages during Shabbat. A gate whose failure mode is "run anyway" is not a gate. **Fail closed**, and use a cached value if you have one.

```javascript
// Runs after the HTTP Request to the Hebcal /shabbat endpoint.
const now = new Date();
const items = $input.first().json?.items;

// FAIL CLOSED: no usable calendar data means we do not know, so we do not run.
if (!Array.isArray(items) || items.length === 0) {
  return [];   // optionally: fall back to a cached window before giving up
}

// Pair each candle-lighting with the first havdalah AFTER it.
const events = items
  .filter(i => i.category === 'candles' || i.category === 'havdalah')
  .map(i => ({ cat: i.category, at: new Date(i.date) }))
  .sort((a, b) => a.at - b.at);

let inRest = false;
for (let k = 0; k < events.length - 1; k++) {
  if (events[k].cat === 'candles' && events[k + 1].cat === 'havdalah') {
    if (now >= events[k].at && now <= events[k + 1].at) { inRest = true; break; }
  }
}

// A havdalah with no preceding candles in the window means the rest period
// started before the data we were given. Treat "now is before the first
// havdalah" as still resting.
if (!inRest && events.length && events[0].cat === 'havdalah' && now <= events[0].at) {
  inRest = true;
}

return inRest ? [] : $input.all();
```

This covers Shabbat and any yom tov that Hebcal brackets with candles/havdalah. It does not by itself cover a chag day that the `/shabbat` window does not reach; for that add Pattern 3.

**Hebcal HTTP Request node configuration:**

```
Method: GET
URL: https://www.hebcal.com/shabbat
Query Parameters:
  cfg: json
  geonameid: 293397  (Tel Aviv, change per your location)
  M: on
```

## Pattern 3: Holiday-Aware Scheduling

For workflows that must also pause on Jewish holidays (Yom Tov).

**Extended Code Node (replaces the basic Shabbat gate):**

Two further traps live in this pattern specifically.

*The date must be computed in Israel time, not UTC.* `now.toISOString().split('T')[0]` is a UTC date, so between midnight and 03:00 Israel time it yields YESTERDAY, and the gate reads the wrong day on every chag night. Use `Intl.DateTimeFormat` with `timeZone: 'Asia/Jerusalem'`.

*A yom tov date-equality test cannot express erev chag.* Hebcal returns yomtov entries as bare dates (`"2026-09-21"`) with no start time, but the chag actually begins at candle lighting the previous evening. Matching only on today's date leaves the entire erev-chag evening unprotected. Treat the evening of the preceding day as blocked once candle-lighting time has passed, which the corrected Pattern 2 gate handles when the `/shabbat` window reaches the chag.

```javascript
const now = new Date();
const shabbatItems = $('Shabbat Check').first().json?.items;
const holidayItems = $('Holiday Check').first().json?.items;

// FAIL CLOSED on either source.
if (!Array.isArray(shabbatItems) || !Array.isArray(holidayItems)) return [];

// 1. Candle-lighting / havdalah window: the paired scan from Pattern 2.
const ev = shabbatItems
  .filter(i => i.category === 'candles' || i.category === 'havdalah')
  .map(i => ({ cat: i.category, at: new Date(i.date) }))
  .sort((a, b) => a.at - b.at);
for (let k = 0; k < ev.length - 1; k++) {
  if (ev[k].cat === 'candles' && ev[k + 1].cat === 'havdalah'
      && now >= ev[k].at && now <= ev[k + 1].at) return [];
}
if (ev.length && ev[0].cat === 'havdalah' && now <= ev[0].at) return [];

// 2. Yom tov by Israel-local date, plus the evening before.
const ilDate = d => new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Jerusalem', year: 'numeric', month: '2-digit', day: '2-digit',
}).format(d);

const today = ilDate(now);
const tomorrow = ilDate(new Date(now.getTime() + 86400000));
// hourCycle 'h23' matters: with the default some engines render midnight as
// '24', and Number('24') >= 16 would over-block the 00:00 hour.
const ilHour = Number(new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Asia/Jerusalem', hour: '2-digit', hourCycle: 'h23',
}).format(now));

const isYomTov = holidayItems.some(i => i.yomtov === true && i.date.startsWith(today));
// Erev chag. 16:00 is a deliberately conservative cutoff, not a halachic time:
// the earliest Israeli candle lighting is around 16:00 in December. Prefer the
// exact candle-lighting time from the /shabbat response whenever it covers the
// chag, and fall back to this only when it does not.
const isErevYomTov = ilHour >= 16 &&
  holidayItems.some(i => i.yomtov === true && i.date.startsWith(tomorrow));

if (isYomTov || isErevYomTov) return [];

return $input.all();
```

**Do not silently DROP the work.** `return []` ends the branch, so an invoice send or a customer notification that arrives during Shabbat is lost, not delayed. For anything a customer is waiting on, write the items to `$getWorkflowStaticData('global')` or a database instead, and drain that queue from a separate post-havdalah workflow. "It was Shabbat so the customer never got their invoice" is a data-loss bug wearing a compliance costume.

**Beyond yom tov.** Hebcal also returns fast days (Tisha B'Av, Tzom Gedaliah, with `Fast begins` / `Fast ends` zmanim items), Yom HaZikaron and Yom HaAtzmaut, and chol hamoed. None of these are `yomtov: true`, so the gate above ignores them, which is usually correct for chol hamoed and usually wrong for Tisha B'Av and the national days. Decide per workflow rather than inheriting the default.

**Holiday HTTP Request node configuration:**

```
Method: GET
URL: https://www.hebcal.com/hebcal
Query Parameters:
  v: 1
  cfg: json
  year: now
  month: x
  maj: on
  mod: on
  i: on
```

Two parameters are load-bearing and both fail silently if you get them wrong:

- **`month: x`, not `month: now`.** `now` is not a valid value for this parameter. Hebcal returns HTTP 200 with `"items": []`, the `.some(...)` check below evaluates false, and the workflow runs on Yom Kippur with no error raised anywhere. `x` returns the whole year; a numeric month also works.
- **`i: on` selects the Israel schedule.** Without it Hebcal serves the Diaspora calendar (`"title": "Hebcal Diaspora 2026"`), which reports 13 yomtov days for 2026 against Israel's 8. Passing an Israeli `geonameid` has the same effect.

Verify with the response `title`: it must read `Hebcal Israel <year>` or `Hebcal <city> <year>`, never `Hebcal Diaspora <year>`.

**Workflow structure:**
```
Schedule Trigger -> [Shabbat Check HTTP] -> [Holiday Check HTTP] -> [Gate Code] -> rest of workflow
                    (parallel)              (parallel)
```

Optimization: Run both HTTP requests in parallel using n8n's split/merge pattern, then feed both results into the Gate Code node.

## Pattern 4: Friday Early Cutoff

For workflows that should stop before Shabbat on Friday (e.g., stop processing orders 2 hours before candle lighting).

```javascript
const now = new Date();
const items = $input.first().json?.items;

// FAIL CLOSED: without the calendar we cannot know how close we are to candle lighting.
if (!Array.isArray(items)) return [];

// The NEXT candle lighting, not merely the first item in the array. On a chag
// the first candles entry can be days away while a rest period is already open,
// so run the Pattern 2 gate first and use this only as the pre-cutoff.
const next = items
  .filter(i => i.category === 'candles')
  .map(i => new Date(i.date))
  .filter(d => d > now)
  .sort((a, b) => a - b)[0];

if (!next) return [];                 // no upcoming candle lighting in the window: fail closed

const cutoff = new Date(next.getTime() - 2 * 60 * 60 * 1000);
return now >= cutoff ? [] : $input.all();
```

Use case: E-commerce order processing that should not start new fulfillment workflows close to Shabbat, because they cannot be completed before candle lighting.

## Pattern 5: Post-Shabbat Resume

For workflows that should run as soon as Shabbat ends (e.g., send queued notifications after havdalah).

**Schedule Trigger cron expression:** `*/15 17-20 * * 6` (every 15 minutes, 5-8 PM on Saturday)

```javascript
const now = new Date();
const data = $input.first().json;

// The MOST RECENT havdalah that has already passed, not the first in the array:
// on a chag the array can open with a havdalah days ahead of now.
const shabbatEnd = (data.items ?? [])
  .filter(i => i.category === 'havdalah')
  .map(i => new Date(i.date))
  .filter(d => d <= now)
  .sort((a, b) => b - a)[0];

if (shabbatEnd) {
  // Only proceed if we are within 30 minutes after havdalah
  const window = new Date(shabbatEnd.getTime() + 30 * 60 * 1000);

  if (now >= shabbatEnd && now <= window) {
    return $input.all(); // Shabbat just ended, process queued items
  }
}

return []; // Not the right time
```

## Pattern 6: Monthly with Holiday Offset

For workflows that run on a specific day each month but shift when that day falls on Shabbat or a holiday.

Two things this pattern must NOT do, both of which an earlier version of it did: use the naive
`items.find('candles')` / `items.find('havdalah')` pair (broken on a chag, see Bug 1 above), and
compute the day-of-month from the server clock rather than Israel time.

```javascript
const now = new Date();
const targetDay = 1;                     // 1st of each month
const items = $input.first().json?.items;

// FAIL CLOSED: no calendar data means we do not know whether it is Shabbat.
if (!Array.isArray(items) || items.length === 0) return [];

// Day of month in Israel time, not server time.
const ilParts = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Jerusalem', year: 'numeric', month: '2-digit', day: '2-digit',
}).format(now).split('-');
const currentDay = Number(ilParts[2]);

// Same paired forward scan as Pattern 2. Do not shortcut it.
const ev = items
  .filter(i => i.category === 'candles' || i.category === 'havdalah')
  .map(i => ({ cat: i.category, at: new Date(i.date) }))
  .sort((a, b) => a.at - b.at);

let resting = false;
for (let k = 0; k < ev.length - 1; k++) {
  if (ev[k].cat === 'candles' && ev[k + 1].cat === 'havdalah'
      && now >= ev[k].at && now <= ev[k + 1].at) { resting = true; break; }
}
if (!resting && ev.length && ev[0].cat === 'havdalah' && now <= ev[0].at) resting = true;

if (resting) return [];                                  // never run during the rest period

// Run on the target day, or on the first following day once the rest period has passed.
if (currentDay >= targetDay && currentDay <= targetDay + 2) return $input.all();
return [];
```

The postponement window here is deliberately crude (up to two days). If the exact "first working day
on or after the 1st" matters, persist a `lastRunMonth` marker in `$getWorkflowStaticData('global')`
and check it rather than inferring from the date, otherwise a three-day chag block will skip the
month entirely.

## Caching Shabbat Data

To avoid calling Hebcal on every schedule trigger tick, cache the weekly Shabbat times:

```javascript
const staticData = $getWorkflowStaticData('global');
const now = Date.now();
const ONE_DAY = 24 * 60 * 60 * 1000;

if (staticData.shabbatData && staticData.fetchedAt > now - ONE_DAY) {
  // Use cached data
  return [{ json: staticData.shabbatData }];
}

// Fetch fresh data (pass to next HTTP Request node)
return $input.all();
```

After the HTTP Request, store the result:

```javascript
const staticData = $getWorkflowStaticData('global');
staticData.shabbatData = $input.first().json;
staticData.fetchedAt = Date.now();
return $input.all();
```

## Major Jewish Holidays Reference

Holidays where `yomtov: true` on the **Israel** schedule (work restrictions apply, treat like Shabbat):

| Holiday | Hebrew | Typical Month | Yom Tov days |
|---------|--------|---------------|--------------|
| Pesach | פסח | March-April | 2 (Pesach I and Pesach VII) |
| Shavuot | שבועות | May-June | 1 |
| Rosh Hashana | ראש השנה | September-October | 2 |
| Yom Kippur | יום כיפור | September-October | 1 |
| Sukkot | סוכות | September-October | 1 (Sukkot I) |
| Shmini Atzeret | שמיני עצרת | September-October | 1 |

Eight yomtov days per year. In Israel, Simchat Torah falls on Shmini Atzeret (one day, one row), so do not count it separately; the second days of Pesach, Shavuot and Sukkot are Diaspora-only and are ordinary working days here. If your query returns Pesach II, Pesach VIII, Shavuot II, Sukkot II or a standalone Simchat Torah, you are reading the Diaspora calendar and are missing `i=on`.

## Common Mistakes

1. **Using fixed Shabbat times.** Shabbat timing varies by 1+ hour throughout the year in Israel (earliest candle lighting ~4:00 PM in December, latest ~7:45 PM in June). Always use the Hebcal API for current times.

2. **Forgetting Erev holidays.** Some holidays start at sundown the day before (like Shabbat). If your workflow runs Friday afternoon, it needs to check both Shabbat and any holiday that starts Friday night.

3. **Not handling DST transitions.** Israel switches to summer time (IDT, UTC+3) on the Friday before the last Sunday of March, and back to winter time (IST, UTC+2) on the last Sunday of October. A schedule trigger at "9 AM" will fire at a different UTC time after the transition. Ensure `GENERIC_TIMEZONE=Asia/Jerusalem` is set so n8n handles this automatically.

4. **Hardcoding a single city.** If your business serves customers across Israel, candle lighting times can differ by 10+ minutes between cities. Jerusalem is especially different due to the tradition of lighting 40 minutes before sunset (vs 18 minutes in most cities, 30 minutes in Haifa and Zikhron Ya'akov). Choose the earliest candle lighting time among your relevant cities for the safest cutoff.

5. **Ignoring Chol HaMoed.** The intermediate days of Sukkot and Pesach (Chol HaMoed) are not full Yom Tov, but many Israeli businesses operate on reduced hours. If your workflow involves customer-facing operations, consider pausing or reducing frequency during Chol HaMoed as well.
