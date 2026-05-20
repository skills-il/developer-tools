---
name: israeli-chatbot-analytics
description: Analyze and optimize Hebrew chatbot performance with conversation flow analytics, Hebrew sentiment analysis, drop-off detection, user satisfaction scoring, A/B testing for response variants, and reporting dashboards. Use when user asks to "analyze chatbot performance", "measure chatbot satisfaction", "track Hebrew bot metrics", "analitika shel tsatbot" (Hebrew transliteration), or needs help with conversation analytics, intent accuracy tracking, or chatbot reporting. Supports Dialogflow, Rasa, and custom bot platforms. Do NOT use for building chatbots (use hebrew-chatbot-builder), Hebrew NLP model training (use hebrew-nlp-toolkit), customer support workflow setup (use israeli-customer-support-automator), or voice bot development (use hebrew-voice-bot-builder).
license: MIT
allowed-tools: Bash(python:*), Bash(pip:*)
compatibility: Requires Python 3.10+. Works with Claude Code, Cursor, Windsurf.
---

# Israeli Chatbot Analytics

Analyze and optimize Hebrew chatbot performance. This skill covers conversation flow analytics, Hebrew-specific sentiment analysis, drop-off detection, user satisfaction scoring, A/B testing for Hebrew response variants, intent recognition accuracy tracking, anomaly alerting, and reporting dashboards. Use it to understand whether your Hebrew chatbot is actually helping users and where to focus improvements.

## Instructions

### Step 1: Collect and Structure Conversation Logs

Before analyzing, ensure conversation data is structured consistently. Each conversation session should include:

```python
# Standard conversation log schema
conversation_log = {
    "session_id": "uuid-string",
    "user_id": "anonymous-or-identified",
    "channel": "whatsapp|telegram|web|app",
    "language": "he",           # Primary language detected
    "started_at": "ISO-8601",
    "ended_at": "ISO-8601",
    "messages": [
        {
            "timestamp": "ISO-8601",
            "sender": "user|bot",
            "text": "שלום, אני צריך עזרה",
            "intent": "greeting",           # Detected intent
            "intent_confidence": 0.92,       # Model confidence
            "entities": [],                  # Extracted entities
            "response_time_ms": 340,         # Bot response latency
        }
    ],
    "outcome": "resolved|escalated|abandoned|unknown",
    "satisfaction_score": null,   # CSAT score if collected
    "metadata": {
        "bot_version": "2.1.0",
        "ab_variant": "formal_he",
    }
}
```

If your platform does not export in this format, write a transformer to normalize logs before analysis. Common platforms and their export formats:

| Platform | Export Method | Format |
|----------|-------------|--------|
| Dialogflow CX | BigQuery export | JSON rows with session context. Use the `he-il` language code on new agents; `iw` is deprecated and frozen for new features (https://docs.cloud.google.com/dialogflow/cx/docs/reference/language). |
| Rasa Pro / CALM | Analytics dashboard + tracker events | Flow-step events (Rasa Pro 3.x with CALM is dialogue-driven, not intent-driven, so legacy intent-accuracy metrics map differently). |
| Rasa Open Source (legacy) | Tracker Store (SQL/Mongo) | Events list per conversation. Rasa OSS entered maintenance mode in 2025, see https://legacy-docs-oss.rasa.com/docs/rasa/. |
| Botpress | Conversation export / DB | JSON. Hebrew is listed as a supported language but full RTL alignment in the default web webchat is still a community-reported gap as of 2026, verify message bubble alignment in your widget before reporting on dialect distribution. |
| Custom bots | Application logs | Varies (normalize to schema above) |
| WhatsApp Cloud API | Webhook logs | Message objects with metadata. See `## WhatsApp Business Platform pricing notes` below for the per-message cost model that started July 2025. |
| ManyChat | Audience + flow exports | CSV/JSON. WhatsApp send-out costs flow through Meta's per-message tariff. |

### Step 2: Conversation Flow Analysis

Analyze session-level metrics to understand overall chatbot health:

Build a `ConversationMetrics` dataclass that tracks `total_sessions`, `completed_sessions`, `escalated_sessions`, `abandoned_sessions`, `session_lengths` (per-session message count), and `session_durations` (seconds). Derive rate properties (`completion_rate`, `escalation_rate`, `abandonment_rate`) as `count / total_sessions`, and `avg_session_length` / `median_session_duration_seconds` from the list fields.

`compute_flow_metrics(conversations)` iterates the structured logs once, increments the right outcome counter (`resolved` / `escalated` / `abandoned`), appends message count and `(ended_at - started_at).total_seconds()`, and returns the metrics object.

**Key benchmarks for Hebrew chatbots (Israeli market, 2025-2026):**

| Metric | Good | Average | Needs Improvement |
|--------|------|---------|-------------------|
| Completion rate | > 70% | 50-70% | < 50% |
| Escalation rate | < 15% | 15-30% | > 30% |
| Abandonment rate | < 20% | 20-35% | > 35% |
| Avg session length | 4-8 messages | 8-15 messages | > 15 messages |
| First-contact resolution | > 65% | 45-65% | < 45% |

### Step 3: Drop-off Point Detection

Identify where users abandon conversations. This reveals UX problems, confusing prompts, or missing capabilities:

`detect_drop_off_points(conversations)` filters to `outcome == "abandoned"` and returns three `Counter.most_common` slices: drop-off by conversation depth (message count), by active intent at drop (walking from the tail to the first message with an intent), and by last bot message (first 80 chars, walking from the tail for the last `sender == "bot"`).

`detect_conversation_loops(conversations, threshold=3)` flags sessions where the bot repeats the same `text` ≥ `threshold` times in a row by scanning the bot-message stream and tracking a consecutive-repeat counter; emit `{session_id, repeated_message, repeat_count, total_messages}` for each looped session.

### Step 4: Hebrew Sentiment Analysis

Hebrew sentiment analysis requires special handling due to morphological complexity, negation patterns, and slang. Use DictaBERT (encoder, classification) or DictaLM 2.0-Instruct (generative, 7B parameters, Mistral-based) for production accuracy, AlephBERT (`onlplab/alephbert-base` from BIU's OnlpLab) as an alternative encoder baseline, or a lexicon-based approach for lightweight analysis. DictaLM 2.0 (released July 2024) is the current state-of-the-art Hebrew LLM from Dicta and ships an instruct variant trained on roughly 200B Hebrew+English tokens with a 2.76 tokens-per-word compression rate, useful when you need a single model to classify sentiment AND summarize the conversation in Hebrew prose for the ops team.

**Using DictaBERT (recommended for production):**

Build `HebrewSentimentAnalyzer` around the `dicta-il/dictabert-sentiment` model (3-class: negative/neutral/positive).

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("dicta-il/dictabert-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("dicta-il/dictabert-sentiment").eval()
```

Wrap `tok(text, return_tensors="pt", truncation=True, max_length=512, padding=True)` + `torch.softmax(model(**inputs).logits, dim=-1)`, then map each probability row to `{label, score, scores}` (label = argmax over `["negative","neutral","positive"]`). Add an `analyze_batch(texts, batch_size=32)` that loops over slices.

**Hebrew-specific sentiment challenges (summary):**

1. **Negation**: "לא" before an adjective flips meaning. "לא רע" (not bad) reads mildly positive in Israeli usage.
2. **Sarcasm and irony**: very common in Israeli communication ("יופי, בדיוק מה שחיכיתי לו" can be deeply negative). DictaBERT handles some of it; fine-tune on domain data for better coverage.
3. **Slang**: evolves fast. "אחלה" / "סבבה" / "בומבה" are positive, "חרא" / "פאדיחה" are negative, "וואלה" is context-dependent.
4. **Mixed Hebrew-English**: users mix English words into Hebrew ("ה-support שלכם גרוע"). Ensure your model or lexicon handles both scripts in one message.

See `references/hebrew-sentiment-guide.md` for the full treatment of these challenges, including the slang lexicon and negation-handling code.

### Step 5: Intent Recognition Accuracy Tracking

Track how well your chatbot understands user requests over time:

Build `IntentAccuracyTracker` to log `(predicted, actual, confidence, timestamp)` per prediction and expose:

- `confusion_matrix()`: 2D `{actual: {predicted: count}}` over the sorted intent universe.
- `misclassification_report(min_count=5)`: top `(actual, predicted)` pairs where `predicted != actual`.
- `low_confidence_intents(threshold=0.6)`: intents whose mean confidence is below `threshold`, with `sample_count` and `below_threshold_pct`.
- `accuracy_trend()`: daily `{date, accuracy, sample_count}` series for plotting (bucket by `timestamp[:10]`).

**How to get ground truth labels:**

- **Manual labeling**: Sample 100-200 conversations per week and have Hebrew-speaking annotators label actual intents. This is the gold standard.
- **Escalation signals**: When a user explicitly corrects the bot ("לא, התכוונתי ל...") or asks for a human agent after a misunderstanding, flag the prior intent as incorrect.
- **Post-chat surveys**: Ask "Did the bot understand what you needed?" and correlate with detected intent.

### Step 6: User Satisfaction Measurement

Combine multiple signals to build a satisfaction score:

```python
@dataclass
class SatisfactionSignals:
    """Combine multiple satisfaction signals into a composite score."""

    # Direct feedback (if available)
    csat_score: float | None = None      # 1-5 scale
    thumbs_rating: str | None = None     # "up" or "down"

    # Behavioral signals
    session_resolved: bool = False
    escalated_to_human: bool = False
    abandoned: bool = False
    repeated_fallbacks: int = 0
    loop_detected: bool = False

    # Sentiment signals
    final_sentiment: str = "neutral"     # positive/neutral/negative
    sentiment_trend: str = "stable"      # improving/stable/declining

    def composite_score(self) -> float:
        """Composite satisfaction (0.0-1.0). If `csat_score` is present, return
        `(csat_score - 1) / 4` directly. Otherwise start at 0.5 (or 0.8/0.2 for
        thumbs up/down), then add: +0.15 resolved, -0.1 escalated, -0.2 abandoned,
        -0.15 repeated_fallbacks>2, -0.2 loop_detected, +/-0.1-0.15 final_sentiment,
        +/-0.05-0.1 sentiment_trend; clamp to [0, 1]."""
        ...
```

Provide `collect_post_chat_survey_he()` that returns a Hebrew post-chat survey: title `"נשמח לשמוע מה חשבת"`, a 1-5 rating on `"עד כמה הצ'אטבוט עזר לך?"`, a yes/no on `"האם הצ'אטבוט הבין את מה שרצית?"`, and an optional open `"רוצה לשתף עוד משהו?"` field. Use `"שלח משוב"` as the submit label.

### Step 7: A/B Testing for Hebrew Response Variants

Test different phrasings, formality levels, and gender handling strategies:

Build `HebrewABTestManager` with three responsibilities:

1. **Register a test.** `create_test(test_id, variants: {name: response_text}, traffic_split=None)`. Default split is uniform across variants. Store `{variants, traffic_split, created_at}` per test_id. Example variants:

```python
{"formal": "שלום וברוכים הבאים. כיצד נוכל לסייע לכם?",
 "casual": "היי! איך אפשר לעזור?",
 "gender_neutral": "שלום! ניתן לבחור מהאפשרויות הבאות:"}
```

2. **Deterministic bucketing.** `assign_variant(test_id, user_id)` hashes `f"{user_id}:{test_id}"` with `hashlib.md5`, maps to a bucket in `[0, 1)`, and walks the cumulative `traffic_split` so the same user always gets the same variant. Use this in `get_response(...)` and increment an `impressions` counter at the same time.

3. **Outcome tracking.** `record_outcome(test_id, variant, completed=False, satisfaction=None, escalated=False)` and `get_test_results(test_id)` returning per-variant `{impressions, completion_rate, avg_satisfaction, escalation_rate}`.

**Common Hebrew A/B test dimensions:**

| Dimension | Variant A | Variant B | What to Measure |
|-----------|-----------|-----------|-----------------|
| Formality | "כיצד נוכל לסייע?" | "איך אפשר לעזור?" | Completion rate |
| Gender | Slash notation ("את/ה") | Gender-neutral ("ניתן ל...") | Satisfaction score |
| Length | Detailed explanation | Short, punchy response | Drop-off rate |
| Emoji usage | With emoji | Without emoji | Engagement |
| Error phrasing | "לא הצלחתי להבין" | "אפשר לנסח אחרת?" | Retry rate |

### Step 8: Performance Dashboards and KPIs

Track these key metrics in your dashboard:

```python
@dataclass
class ChatbotDashboard:
    """Key metrics for chatbot performance dashboard."""

    # Core metrics
    total_conversations: int = 0
    resolution_rate: float = 0.0        # % resolved without escalation
    first_contact_resolution: float = 0.0  # % resolved in first session
    avg_handle_time_seconds: float = 0.0
    escalation_rate: float = 0.0
    abandonment_rate: float = 0.0

    # User satisfaction
    avg_csat: float = 0.0               # 1-5 scale
    nps_score: float = 0.0              # -100 to 100
    thumbs_up_ratio: float = 0.0        # % positive

    # Intent accuracy
    intent_accuracy: float = 0.0        # % correctly classified
    fallback_rate: float = 0.0          # % of messages hitting fallback

    # Performance
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0

    # Volume
    conversations_per_day: float = 0.0
    peak_hour: int = 0                  # 0-23
    busiest_day: str = ""               # "Sunday" etc.

    def to_report_dict(self) -> dict:
        """Group fields into core / satisfaction / accuracy / performance / volume
        sections for reporting (format rates as %, times as ms)."""
        ...
```

Implement `build_dashboard(conversations, period_days=7)` to populate the dataclass:

- Outcome rates from `Counter(c["outcome"])` / `n`.
- `avg_handle_time_seconds` from `(ended_at - started_at).total_seconds()` per session.
- `avg_csat` from `satisfaction_score` where present.
- `avg_response_time_ms` / `p95_response_time_ms` from bot messages with `response_time_ms` (p95 via `sorted_rts[int(len * 0.95)]`).
- `intent_accuracy` = share of user messages with `intent_confidence > 0.7`. `fallback_rate` = share of user messages with `intent == "fallback"`.
- `conversations_per_day = n / period_days`. `peak_hour` and `busiest_day` from `Counter` over `started_at` hour and weekday.

**Israeli traffic patterns to expect:**
- Peak hours are typically 10:00-12:00 and 19:00-22:00 (Israel Time, UTC+2/+3)
- Sunday is the busiest day (first workday of the Israeli week)
- Friday afternoon and Saturday see minimal traffic
- Holiday periods (Rosh Hashana, Pesach, Sukkot) show different patterns

#### Retention and Returning-User Metrics

Session-level metrics tell you how a single conversation went, but not whether the bot earns repeat use. Track these retention dimensions alongside the dashboard above (all require a stable `user_id` across sessions, pseudonymized per the Privacy and Consent section):

For each `user_id`, collect the set of distinct dates with a conversation. Then:

- **D1 return rate** = share whose first-date + 1 day is also in their set.
- **D7 return rate** = share whose first-date + 2..7 days intersects their set.
- **Repeat-contact rate** = share with > 1 distinct date.

- **D1 / D7 return rate**: share of users who start a new conversation the day after, or within a week of, their first contact. D7 is more stable than D1 for low-volume Israeli bots.
- **Repeat-contact rate**: share of users with more than one conversation. On a support bot this can be good (trust) or bad (unresolved issues), so read it with first-contact resolution.

### Step 9: Hebrew-Specific Analytics Challenges

#### RTL Text in Charts and Visualizations

When rendering analytics dashboards that display Hebrew text, handle these RTL issues:

```python
import matplotlib.pyplot as plt
import matplotlib

# Use a font that supports Hebrew
matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Arial", "Heebo"]

# Tip: Use horizontal bar charts so Hebrew labels read naturally on the y-axis.
# For interactive dashboards, Plotly handles RTL better than matplotlib.
# Use font-family "Heebo, Arial, sans-serif" and add extra left margin for labels.
```

#### Hebrew Word Tokenization for Word Clouds

Standard whitespace tokenization does not work well for Hebrew due to prefix particles (ב, ה, ו, ל, מ, כ, ש):

```python
# Standard whitespace tokenization fails for Hebrew due to prefix particles.
# Use YAP (https://github.com/OnlpLab/yap) for production, or strip common prefixes:
HEBREW_PREFIXES = ["ב", "ה", "ו", "ל", "מ", "כ", "ש", "וה", "של", "לה"]

# Strip prefixes only if word is long enough (>3 chars) and remainder >= 2 chars.
# For word clouds: use bidi algorithm to convert Hebrew for display,
# remove stopwords (של, את, על, עם, אני, זה, כי, גם, לא, יש, אין, מה).
# See references/hebrew-sentiment-guide.md for detailed tokenization code.
```

#### Mixed Hebrew-English Query Handling

Israeli users frequently mix languages. Track language distribution and handle accordingly:

```python
import re

def detect_message_language(text: str) -> str:
    """Detect primary language by counting Hebrew vs English characters."""
    hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total = hebrew_chars + english_chars
    if total == 0:
        return "unknown"
    return "he" if hebrew_chars / total >= 0.5 else "en"

# Track mixed-language rate: messages where 20-80% is Hebrew.
# Israeli users frequently code-switch between Hebrew and English.
```

### Step 10: Alerting and Anomaly Detection

Set up alerts to catch problems before they affect too many users:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class AlertRule:
    """Define an alerting rule for chatbot metrics."""
    name: str
    metric: str
    operator: str          # "gt" (greater than), "lt" (less than)
    threshold: float
    window_minutes: int    # Rolling window
    severity: str          # "critical", "warning", "info"
    description_he: str    # Hebrew description for ops team


# Recommended alert rules for Hebrew chatbots
# AlertRule(name, metric, operator, threshold, window_minutes, severity, description_he)
DEFAULT_ALERT_RULES = [
    AlertRule("high_escalation_rate", "escalation_rate", "gt", 0.35, 60, "warning",
              "שיעור הסלמה גבוה מ-35% בשעה האחרונה"),
    AlertRule("satisfaction_drop", "avg_csat", "lt", 3.0, 120, "critical",
              "שביעות רצון ממוצעת ירדה מתחת ל-3.0 בשעתיים האחרונות"),
    AlertRule("high_abandonment", "abandonment_rate", "gt", 0.40, 60, "critical",
              "שיעור נטישה גבוה מ-40% בשעה האחרונה"),
    AlertRule("high_fallback_rate", "fallback_rate", "gt", 0.25, 30, "warning",
              "שיעור fallback גבוה מ-25% בחצי שעה האחרונה"),
    AlertRule("slow_response", "p95_response_time_ms", "gt", 3000, 15, "warning",
              "זמן תגובה P95 חורג מ-3 שניות ברבע השעה האחרון"),
    AlertRule("new_unrecognized_intents", "new_unknown_intents_count", "gt", 20, 60,
              "info", "יותר מ-20 כוונות לא מזוהות חדשות בשעה האחרונה"),
]


```

`AlertManager` wraps the rule list. `check_metrics(current_metrics: dict)` walks every rule, skips when the metric is missing, and triggers when `value > threshold` (op `gt`) or `value < threshold` (op `lt`). Each triggered alert is a dict with `rule_name`, `severity`, `metric`, `current_value`, `threshold`, `description_he`, and `triggered_at`.

### Step 11: Reporting Templates

Generate periodic reports summarizing chatbot performance:

Implement `generate_weekly_report(dashboard, previous_dashboard=None, period_start, period_end)`:

- Helper `trend_arrow(current, previous, higher_is_better)`: returns `(ללא שינוי)` for < 1% delta; otherwise emits `[v] +X.X%` (good direction) or `[!] +X.X%` (bad direction).
- Emit a `# דוח ביצועי צ'אטבוט שבועי` header, period subheader, and a `| מדד | ערך | שינוי מהשבוע הקודם |` markdown table over: שיחות, שיעור פתרון, CSAT, שיעור הסלמה (lower-is-better), שיעור נטישה (lower-is-better), דיוק זיהוי כוונות, זמן תגובה ממוצע (lower-is-better).
- Append a `## תנועה` block with `conversations_per_day`, `peak_hour`, `busiest_day`.

### Step 12: Integration with Chatbot Platforms

#### Dialogflow CX Analytics

Implement `parse_dialogflow_cx_logs(bigquery_rows)` to fold a Dialogflow CX BigQuery export into the standard `conversations` shape.

- Export query: `SELECT * FROM project.dataset.dialogflow_cx_interactions WHERE DATE(request_time) BETWEEN @start AND @end`.
- Group rows by `session_id`. For each session, track min/max `request_time` as `started_at` / `ended_at`.
- For each row, append a user message (`text = query_text`, `intent = matched_intent`, `intent_confidence`) and/or bot message (`text = response_text`). Sort each session's messages by `timestamp`. Set `language = "he"`, `outcome = "unknown"` (derive from flow completion downstream).

#### Rasa Tracker Store Analytics

Note: Rasa Open Source is in maintenance mode. The intent-based tracker-store analytics below apply to existing Rasa OSS deployments; new Rasa builds use CALM (Conversational AI with Language Models), which is dialogue-driven rather than intent-driven, so intent-accuracy metrics map differently there. See the legacy OSS docs at https://legacy-docs-oss.rasa.com/docs/rasa/ for tracker-store details.

Implement `parse_rasa_tracker_events(tracker_events)` to fold a Rasa tracker-store stream into the standard `conversations` shape.

- Query: `SELECT * FROM events WHERE sender_id = @sender_id ORDER BY timestamp`.
- Iterate events. On `session_started`, flush the in-progress session and start a new one. On `user`, append a user message with `intent.name` and `intent.confidence` from `parse_data`. On `bot`, append a bot message with `text`. On `action` with `name == "action_human_handoff"`, set `outcome = "escalated"`. Flush the trailing session at the end.

## WhatsApp Business Platform pricing notes

Many Israeli chatbots run on WhatsApp Cloud API, where send-out cost is a first-class analytics dimension. Pricing changed on July 1, 2025 from a per-conversation model to **per-message billing across 4 categories**:

| Category | Pricing posture | When to use |
|----------|-----------------|-------------|
| Marketing | Highest per-message rate, no volume discount | Promotions, broadcasts, re-engagement |
| Utility | Lower than marketing (typically under $0.03), eligible for volume discounts | Order updates, appointment reminders, account notices triggered by user action |
| Authentication | Lowest non-free tier, eligible for volume discounts | OTP codes for login / payment / 2FA |
| Service | **Free** | Any reply from the business within the 24-hour customer service window (user-initiated session) |

Two free windows worth tracking explicitly in your analytics:

1. **24-hour service window.** When a user sends an inbound message, you can reply with free-form text (no template, no charge) for the next 24 hours. Optimizing analytics for "did we resolve in the service window?" can eliminate a whole template-cost line item for reactive support flows. See https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.
2. **72-hour click-to-WhatsApp / Facebook ad window.** When the user arrives from a click-to-WhatsApp ad or a Facebook Page CTA, all messages (including templates) are free for 72 hours.

Add `template_category` (marketing/utility/authentication/service) and `arrived_via_ctw_ad` boolean to your conversation log schema so finance and product can split CSAT/resolution by paid vs. free interaction. Israeli rates are not published per-country in the public docs, pull your specific Israel rate from the Meta Business Manager pricing tool or your BSP (e.g. Twilio, 360dialog, Vonage) when sizing campaigns.

## Anti-spam compliance (Israel Communications Law, Section 30A)

If your chatbot sends marketing messages (broadcasts, promotional templates on WhatsApp, Telegram campaigns, SMS retargeting), Section 30A of the Communications Law (Telecom and Broadcasts) 5742-1982 applies. The law requires **prior written opt-in consent** before sending advertising messages via SMS, email, fax, robocalls, and, under the 2008 amendment language as interpreted by Israeli courts, electronic communication that includes WhatsApp, Telegram, and similar IM apps. The term "advertisement" is interpreted broadly: any message not purely service-related can be treated as advertising.

Practical analytics tracking:

- **Tag every send as `opt_in_basis`**: "explicit_form" / "ctw_ad_click" / "service_reply" / "transactional". This is your audit trail if a complaint reaches the Ministry of Communications.
- **Track unsubscribe path success rate.** Marketing messages must include the word "advertisement" (פרסומת), the sender's name and address, and a working opt-out path. Measure the time-to-unsubscribe and the success rate of the opt-out flow as a compliance KPI.
- **Service vs. marketing split.** Run completion-rate and CSAT separately for opt-in marketing flows vs. user-initiated service flows, they behave very differently and combining them masks both.
- Cross-reference: `gws-hebrew-email-automation` and `israeli-telegram-business-bot` cover the same opt-in regime for email and Telegram. Use those skills if you also operate those channels.

This is engineering guidance, not legal advice. The maximum statutory damages per unsolicited marketing message are NIS 1,000 without proof of damages, so a misconfigured broadcast to even a few hundred non-consenting users can become a meaningful financial event. Confirm specifics with a privacy lawyer.

## Experimentation platforms for Hebrew chatbots

When you outgrow `HebrewABTestManager` (in-process bucketing, in-memory results) and need real statistical analysis with sequential testing and CUPED variance reduction, the mainstream feature-flag + experimentation platforms all work fine for Hebrew chatbots, none of them care what language your `variant_text` is in. Pick by team and infra fit:

| Platform | Best fit | Notes for Hebrew chatbot teams |
|----------|----------|--------------------------------|
| Statsig | Teams wanting flags + experiments + product analytics in one stack | OpenAI acquired Statsig in 2025 for $1.1B; generous free tier still good for small Israeli bots. |
| LaunchDarkly | Mature enterprise teams needing approvals, audit logs, RBAC | The "safe" enterprise choice; pair with your existing analytics for stats. |
| GrowthBook | Teams with a data warehouse (BigQuery, Snowflake, Postgres) who want stats run against their own data | Open source; does NOT collect event data, so Hebrew transcripts never leave your warehouse, useful for Amendment 13 data-residency posture. |

For Hebrew-specific gotchas, plan on longer test durations (2+ weeks, 200+ impressions per variant), Israeli user bases are smaller and weekly seasonality (Sun-Thu work week) makes 1-week tests unreliable.

## Modern analytics stack notes (GA4 + Mixpanel, 2026)

- **GA4 "AI Assistant" channel.** GA4 now ships a built-in `Channel Group: AI Assistant` (Medium `ai-assistant`) that auto-categorizes traffic from ChatGPT, Gemini, and Claude (Perplexity reportedly included; Google has not formally confirmed). If you embed your bot on a marketing site, this is the easiest way to attribute incoming traffic referred by an LLM to the bot's funnel, no custom regex needed (https://martech.org/ga4-now-tracks-ai-chatbot-traffic-automatically/).
- **Mixpanel Spark + MCP Server.** Mixpanel released Spark (AI query builder) and an MCP server in 2025-2026 that lets Claude / ChatGPT / Cursor query Mixpanel data conversationally. For Hebrew dashboards specifically this matters because you can ask follow-up questions in Hebrew and Spark routes them to the right event/property, useful when the ops team is not fluent in funnel-query UI.

## Examples

### Example 1: Analyze chatbot performance for the past week

User says: "Analyze my Hebrew chatbot logs from the past week and show me where users are dropping off."

Actions:
1. Load conversation logs from the specified time period.
2. Run `compute_flow_metrics()` to get session-level stats.
3. Run `detect_drop_off_points()` to find abandonment patterns.
4. Run `detect_conversation_loops()` to identify stuck users.
5. Generate a summary with actionable recommendations.

Result: Report with completion rate, top drop-off points, looping conversations, and abandonment patterns.

### Example 2: Set up A/B testing for greeting messages

User says: "I want to test whether a formal or casual Hebrew greeting works better."

Actions:
1. Create an A/B test with `HebrewABTestManager.create_test()`.
2. Define variants: formal ("כיצד נוכל לסייע לכם היום?") vs. casual ("היי! מה אפשר לעשות בשבילך?").
3. Configure traffic split (50/50).
4. Integrate with the bot's greeting handler.
5. Set up outcome tracking (completion rate, CSAT, escalation).

Result: Running A/B test with deterministic user assignment and statistical outcome tracking.

### Example 3: Set up anomaly alerting

User says: "Alert me if chatbot satisfaction drops suddenly."

Actions:
1. Configure `AlertManager` with satisfaction and escalation rules.
2. Set up rolling window calculations for recent metrics.
3. Connect alerts to notification channels (Slack, email, PagerDuty).
4. Add Hebrew-language alert descriptions for the ops team.

Result: Real-time monitoring that triggers alerts when CSAT drops below 3.0, escalation rate exceeds 35%, or abandonment spikes above 40%.

### Example 4: Generate a weekly performance report

User says: "Create a Hebrew weekly report for the chatbot team."

Actions:
1. Run `build_dashboard()` for the current and previous weeks.
2. Call `generate_weekly_report()` with both dashboards for trend arrows.
3. Include drop-off analysis and intent accuracy breakdown.
4. Format output in Hebrew with RTL-compatible tables.

Result: A formatted Hebrew report with week-over-week comparisons, trend indicators, and key metrics ready to share with the team.

## Bundled Resources

### Scripts
- `scripts/conversation-analyzer.py` -- Analyze chatbot conversation logs for key metrics (drop-off, sentiment, resolution). Run: `python scripts/conversation-analyzer.py --help`

### References
- `references/chatbot-metrics-glossary.md` -- Glossary of chatbot analytics metrics with Hebrew translations and industry benchmarks. Consult when defining KPIs or explaining metrics to Hebrew-speaking stakeholders.
- `references/hebrew-sentiment-guide.md` -- Guide to Hebrew sentiment analysis challenges including negation, sarcasm, slang, and mixed-language handling. Consult when building or tuning Hebrew sentiment models.

## Gotchas

- Hebrew sentiment analysis requires Israeli-specific training data. Standard English sentiment models misclassify Hebrew sarcasm (very common in Israeli communication) as neutral or positive.
- Israeli chatbot usage peaks on Sunday mornings (start of work week), not Monday. Weekly analytics reports should anchor to Sunday-Thursday.
- Hebrew text analytics must handle prefixed particles (ב-, ל-, כ-, מ-) that change word boundaries. Standard tokenizers trained on English split Hebrew words incorrectly.
- Israeli users frequently code-switch between Hebrew and English within a single chatbot conversation. Analytics tools must handle bilingual sessions, not treat them as two separate languages.

## Privacy and Consent

This skill ingests full conversation transcripts and `user_id` values, and runs sentiment analysis on user messages. Conversation text is personal data and often contains sensitive content (health, finances, complaints). Handle it under Israel's Privacy Protection Law, including Amendment 13 (in force August 2025), which tightened consent, notice, accountability, and data-minimization obligations.

Practical rules:

- **Consent and notice.** Get consent to store and analyze chat content, and tell users in your privacy notice that conversations are retained and analyzed for quality. Sentiment analysis on user messages is a processing purpose that should be disclosed.
- **Pseudonymize `user_id`.** Do not analyze raw phone numbers, emails, or Teudat Zehut as the identifier. Hash or tokenize `user_id` before it reaches the analytics pipeline, and keep the mapping table separate and access-controlled. Retention and A/B-test bucketing still work on a stable pseudonymous ID.
- **Minimize and redact.** Strip or mask entities you do not need for analytics (ID numbers, full names, card numbers) before storing transcripts. You rarely need the raw PII to measure drop-off or sentiment.
- **Retention limits.** Set an explicit retention window for raw transcripts (for example 90 days) and keep only aggregated metrics long-term. Document the window and delete on schedule.
- **Access control and location.** Restrict who can read raw conversations, log access, and confirm where the data is stored and processed.
- This is engineering guidance, not legal advice. Confirm your specific obligations with a privacy professional.

## Recommended MCP Servers

No MCP server is required for this skill. It operates entirely on exported conversation logs (BigQuery exports, Rasa tracker-store dumps, application log files) that you load from disk and analyze locally with the bundled Python script. There is no live API to wrap, so no MCP integration is needed.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Dialogflow CX language reference | https://docs.cloud.google.com/dialogflow/cx/docs/reference/language | Hebrew language code `he-il` (use this on new agents; `iw` is deprecated) |
| Dialogflow CX analytics | https://cloud.google.com/dialogflow/cx/docs/concept/analytics | Built-in conversation analytics, intent metrics |
| Rasa CALM docs | https://rasa.com/docs/learn/concepts/calm/ | Dialogue-driven flows for Rasa Pro 3.x, replaces intent-based design for new builds |
| Rasa OSS documentation (legacy) | https://legacy-docs-oss.rasa.com/docs/rasa/ | Event tracking, tracker stores, custom analytics integrations (maintenance mode) |
| WhatsApp Business Platform pricing | https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing | Per-message rates by country + category (marketing/utility/auth/service), free 24h window rules |
| DictaBERT (Hebrew BERT suite) | https://huggingface.co/dicta-il/dictabert | Pre-trained Hebrew BERT for classification fine-tunes |
| DictaBERT sentiment | https://huggingface.co/dicta-il/dictabert-sentiment | Off-the-shelf Hebrew sentiment classifier (3-class) |
| DictaLM 2.0 Instruct | https://huggingface.co/dicta-il/dictalm2.0-instruct | Generative Hebrew LLM (7B, Mistral-based) for summaries + classification in one call |
| AlephBERT | https://huggingface.co/onlplab/alephbert-base | Alternative Hebrew BERT from BIU OnlpLab |
| HuggingFace Hebrew models | https://huggingface.co/models?language=he | Browse the full Hebrew model catalog |
| Mixpanel help | https://mixpanel.com/help | Funnel analysis, cohort retention for chat flows |
| Matomo analytics | https://matomo.org/docs/ | Self-hosted event tracking, privacy-friendly |
| Israel Privacy Amendment 13 (IAPP) | https://iapp.org/news/a/israel-marks-a-new-era-in-privacy-law-amendment-13-ushers-in-sweeping-reform | Effective Aug 14, 2025: consent, notice, retention limits, deletion mechanisms |
| Section 30A anti-spam guide (DLA Piper) | https://www.dlapiperdataprotection.com/index.html?t=electronic-marketing&c=IL | Opt-in regime for SMS / email / IM marketing in Israel |

## Troubleshooting

- **DictaBERT model not loading**: the `dicta-il/dictabert-sentiment` model needs PyTorch + `transformers` (~500MB). Run `pip install torch transformers`; for CPU-only, install torch from `https://download.pytorch.org/whl/cpu`.
- **Hebrew text appears reversed in charts**: matplotlib has no native RTL. Apply `python-bidi` (`bidi.algorithm.get_display()`) before rendering, or switch to Plotly.
- **Tokenization produces wrong word frequencies**: whitespace splitting ignores Hebrew prefix particles. Use the prefix-stripping tokenizer in Step 9, or the YAP morphological analyzer (https://github.com/OnlpLab/yap) for production.
- **Sentiment scores unreliable for short messages**: messages of 1-3 words lack context ("סבבה" can be positive or neutral). For under 4 words, rely on behavioral signals (continued / escalated / abandoned) instead, combined with satisfaction signals from Step 6.
- **A/B test results not statistically significant**: usually insufficient sample size, common for smaller Israeli user bases. Run at least 2 weeks, aim for 200+ impressions per variant, target p < 0.05.
