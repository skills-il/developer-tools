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

This handles the simple case. Israeli business week is Sunday (0) through Thursday (4). Friday and Saturday are excluded by the cron itself, so no Shabbat check is needed for the standard work week.

**When to add a Shabbat gate on top of this:** When the workflow runs on Friday (before Shabbat) or needs to account for holidays that fall on weekdays.

## Pattern 2: Daily Workflow with Shabbat Gate

For workflows that run every day but must pause during Shabbat.

**Schedule Trigger cron expression:** `0 */3 * * *` (every 3 hours)

**Shabbat Gate Code Node:**

```javascript
// Runs after HTTP Request to Hebcal shabbat endpoint
const now = new Date();
const data = $input.first().json;

const candles = data.items?.find(i => i.category === 'candles');
const havdalah = data.items?.find(i => i.category === 'havdalah');

if (!candles || !havdalah) {
  // No Shabbat data available (unlikely), proceed with caution
  return $input.all();
}

const shabbatStart = new Date(candles.date);
const shabbatEnd = new Date(havdalah.date);

if (now >= shabbatStart && now <= shabbatEnd) {
  // Currently Shabbat, stop workflow
  return [];
}

// Not Shabbat, continue
return $input.all();
```

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

```javascript
const now = new Date();
const shabbatData = $('Shabbat Check').first().json;
const holidayData = $('Holiday Check').first().json;

// Check Shabbat
const candles = shabbatData.items?.find(i => i.category === 'candles');
const havdalah = shabbatData.items?.find(i => i.category === 'havdalah');

if (candles && havdalah) {
  const shabbatStart = new Date(candles.date);
  const shabbatEnd = new Date(havdalah.date);
  if (now >= shabbatStart && now <= shabbatEnd) {
    return [];
  }
}

// Check holidays (Yom Tov)
if (holidayData.items) {
  const today = now.toISOString().split('T')[0];
  const isYomTov = holidayData.items.some(item =>
    item.yomtov === true && item.date.startsWith(today)
  );
  if (isYomTov) {
    return [];
  }
}

return $input.all();
```

**Holiday HTTP Request node configuration:**

```
Method: GET
URL: https://www.hebcal.com/hebcal
Query Parameters:
  v: 1
  cfg: json
  year: now
  month: now
  maj: on
  mod: on
```

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
const data = $input.first().json;

const candles = data.items?.find(i => i.category === 'candles');

if (candles) {
  const candleLighting = new Date(candles.date);
  // Stop 2 hours before candle lighting
  const cutoff = new Date(candleLighting.getTime() - 2 * 60 * 60 * 1000);

  if (now >= cutoff) {
    return [];
  }
}

return $input.all();
```

Use case: E-commerce order processing that should not start new fulfillment workflows close to Shabbat, because they cannot be completed before candle lighting.

## Pattern 5: Post-Shabbat Resume

For workflows that should run as soon as Shabbat ends (e.g., send queued notifications after havdalah).

**Schedule Trigger cron expression:** `*/15 17-20 * * 6` (every 15 minutes, 5-8 PM on Saturday)

```javascript
const now = new Date();
const data = $input.first().json;

const havdalah = data.items?.find(i => i.category === 'havdalah');

if (havdalah) {
  const shabbatEnd = new Date(havdalah.date);
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

```javascript
const now = new Date();
const targetDay = 1; // 1st of each month
const currentDay = now.getDate();

// Check if today is the target day or a postponed run
const shabbatData = $input.first().json;
const candles = shabbatData.items?.find(i => i.category === 'candles');
const havdalah = shabbatData.items?.find(i => i.category === 'havdalah');

let isShabbat = false;
if (candles && havdalah) {
  const start = new Date(candles.date);
  const end = new Date(havdalah.date);
  isShabbat = now >= start && now <= end;
}

if (currentDay === targetDay && !isShabbat) {
  return $input.all(); // Run on target day if not Shabbat
}

if (currentDay === targetDay + 1 || currentDay === targetDay + 2) {
  // Check if the target day was Shabbat/holiday and this is the first valid day
  // This requires checking the previous days, which is more complex
  // Simplified: run on the next valid day after target
  if (!isShabbat) {
    return $input.all();
  }
}

return []; // Not time to run
```

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

Holidays where `yomtov: true` (work restrictions apply, treat like Shabbat):

| Holiday | Hebrew | Typical Month | Duration (Yom Tov days) |
|---------|--------|---------------|------------------------|
| Rosh Hashana | ראש השנה | September-October | 2 days |
| Yom Kippur | יום כיפור | September-October | 1 day |
| Sukkot | סוכות | September-October | 2 days (1st and 8th) |
| Simchat Torah | שמחת תורה | October | 1 day |
| Pesach | פסח | March-April | 2 days (1st-2nd and 7th) |
| Shavuot | שבועות | May-June | 1 day |

Note: Israeli holidays follow Israel schedule (not diaspora), so Sukkot and Pesach have fewer Yom Tov days than outside Israel.

## Common Mistakes

1. **Using fixed Shabbat times.** Shabbat timing varies by 1+ hour throughout the year in Israel (earliest candle lighting ~4:00 PM in December, latest ~7:45 PM in June). Always use the Hebcal API for current times.

2. **Forgetting Erev holidays.** Some holidays start at sundown the day before (like Shabbat). If your workflow runs Friday afternoon, it needs to check both Shabbat and any holiday that starts Friday night.

3. **Not handling DST transitions.** Israel switches to summer time (IDT, UTC+3) on the Friday before the last Sunday of March, and back to winter time (IST, UTC+2) on the last Sunday of October. A schedule trigger at "9 AM" will fire at a different UTC time after the transition. Ensure `GENERIC_TIMEZONE=Asia/Jerusalem` is set so n8n handles this automatically.

4. **Hardcoding a single city.** If your business serves customers across Israel, candle lighting times can differ by 10+ minutes between cities. Jerusalem is especially different due to the tradition of lighting 40 minutes before sunset (vs 18 minutes in most cities, 30 minutes in Haifa and Zikhron Ya'akov). Choose the earliest candle lighting time among your relevant cities for the safest cutoff.

5. **Ignoring Chol HaMoed.** The intermediate days of Sukkot and Pesach (Chol HaMoed) are not full Yom Tov, but many Israeli businesses operate on reduced hours. If your workflow involves customer-facing operations, consider pausing or reducing frequency during Chol HaMoed as well.
