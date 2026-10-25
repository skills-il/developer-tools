---
name: israeli-chatbot-analytics
description: Analyze and optimize Hebrew chatbot performance with conversation flow analytics, Hebrew sentiment analysis, drop-off detection, user satisfaction scoring, A/B testing for response variants, and reporting dashboards. Use when user asks to "analyze chatbot performance", "measure chatbot satisfaction", "track Hebrew bot metrics", "analitika shel tsatbot" (Hebrew transliteration), or needs help with conversation analytics, intent accuracy tracking, or chatbot reporting. Supports Dialogflow, Rasa, and custom bot platforms. Do NOT use for building chatbots (use hebrew-chatbot-builder), Hebrew NLP model training (use hebrew-nlp-toolkit), customer support workflow setup (use israeli-customer-support-automator), or voice bot development (use hebrew-voice-bot-builder).
license: MIT
allowed-tools: Bash(python3:*), Bash(pip:*)
compatibility: Requires Python 3.11+ for the bundled script (standard library only). Step 4 sentiment additionally needs torch + transformers.
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
            "sender": "user|bot|agent",     # agent = a human who took over
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

Two fields in that schema carry every headline number in this skill, and neither one arrives in an export. Define both explicitly before you compute anything.

**Deriving `outcome` (do this first).** Completion, escalation, abandonment, drop-off, the satisfaction composite and cost per resolved conversation all key off this label. Platform exports do not contain it: the Dialogflow CX parser writes `unknown`, and a WhatsApp webhook stream has no outcome concept at all. Run the analyzer without deriving it and you get a dashboard of zeros. Write the rule down and version it:

| Outcome | Derive from |
|---------|-------------|
| `escalated` | A handoff event fired (Rasa `action_human_handoff`, a live-agent transfer, a ticket created) |
| `resolved` | Your goal event fired (order placed, appointment booked, form submitted), OR the user hit a terminal positive intent, OR CSAT >= 4 |
| `abandoned` | Session closed by the inactivity timeout below with no goal event and no handoff |
| `unknown` | Everything else. Report the share explicitly; a large `unknown` bucket invalidates every rate above it |

Never take an `outcome` the bot writes about itself ("flow completed") as an outcome. That is the bot's own belief, and treating it as ground truth is the same error as reading `high_confidence_rate` as `intent_accuracy` (Step 8).

**Defining the session boundary.** The Dialogflow CX BigQuery export has one row per turn: take the session from `conversation_name` and its start and end from the first and last `request_time`. On WhatsApp Cloud API, the dominant Israeli channel, there is no session object at all, only a flat webhook stream. You must cut it yourself with an inactivity timeout, and **the timeout you pick mechanically sets your abandonment rate and average handle time**. A user who replies the next morning is one long resolved session under a 24-hour cut and one abandoned session plus a new one under a 30-minute cut. Both numbers get quoted to management. Pick one (30 minutes is a reasonable default for support), write it into the log-normalization step, and never change it without restating the history. The WhatsApp 24-hour customer-service window and the free-entry-point window (up to 7 days) are BILLING windows: do not reuse them as conversation boundaries.

If your platform exports a different shape, normalize it first. The export method and format for Conversational Agents (Dialogflow CX), Rasa Pro / CALM, Rasa Open Source, Botpress, WhatsApp Cloud API, ManyChat and custom bots, with the Hebrew language-code caveat, are in `references/platform-integrations.md`.

### Step 2: Conversation Flow Analysis

Analyze session-level metrics to understand overall chatbot health:

`compute_flow_metrics(conversations)` makes one pass, counting sessions per outcome (`resolved` / `escalated` / `abandoned`) and collecting message counts and `(ended_at - started_at).total_seconds()`. Rates are `count / total_sessions`, with `unknown` sessions left in the denominator; also report the average session length and the median duration.

**Industry benchmarks for support chatbots (apply with judgment to Hebrew bots):**

These are general support-chatbot targets with no Israeli sample behind them. Use them as a starting bar and replace each row with your own baseline after four weeks of data.

| Metric | Good | Average | Needs Improvement |
|--------|------|---------|-------------------|
| Completion rate | > 70% | 50-70% | < 50% |
| Escalation rate | < 15% | 15-30% | > 30% |
| Abandonment rate | < 20% | 20-35% | > 35% |
| Avg session length | 4-8 messages | 8-15 messages | > 15 messages |
| First-contact resolution | > 65% | 45-65% | < 45% |

**Measure what happens after an escalation.** `escalation_rate` on its own rewards a bot that is hard to escape. For every escalated session also track the queue wait from handoff to the first human reply, whether the agent received the transcript (an agent whose first message re-asks for an ID or order number the user already gave did not), the human resolution rate, and the bounce-back rate (handed back to the bot, or escalated again within 24 hours). A falling escalation rate alongside rising bounce-backs or repeat contacts is a bot that deflects, not one that resolves.

### Step 3: Drop-off Point Detection

Identify where users abandon. This reveals UX problems, confusing prompts, or missing capabilities:

`detect_drop_off_points(conversations)` filters to `outcome == "abandoned"` and returns three `Counter.most_common` slices: drop-off by conversation depth (message count), by active intent at drop (walking from the tail to the first message that carries an intent), and by last bot message (first 100 chars, walking from the tail for the last `sender == "bot"`).

Keep `fallback` in the by-intent bucket. Fallback-then-abandon is the most common real drop-off pattern, so filtering it out empties the report for exactly the sessions you most need to see.

`detect_conversation_loops(conversations, threshold=3)` flags sessions where the bot repeats the same `text` ≥ `threshold` times in a row by scanning the bot-message stream and tracking a consecutive-repeat counter; emit `{session_id, repeated_message, repeat_count, total_messages}` for each looped session.

### Step 4: Hebrew Sentiment Analysis

Hebrew sentiment analysis requires special handling due to morphological complexity, negation patterns, and slang. Use DictaBERT (encoder, classification) for production sentiment scoring, AlephBERT (`onlplab/alephbert-base` from the ONLP Lab at Bar-Ilan University) as an alternative encoder baseline, or a lexicon-based approach for lightweight analysis. When you need one model to classify sentiment AND summarize the conversation in Hebrew prose for the ops team, use Dicta-LM 3.0 (February 2026), the current Hebrew model family from Dicta, with a 65k native context: 24B (adapted from Mistral-Small-3.1), 12B (from NVIDIA Nemotron Nano V2) and 1.7B (from Qwen3-1.7B). The chat variants are not named alike, so copy the exact repo id: `DictaLM-3.0-1.7B-Instruct` and `-1.7B-Thinking`, `DictaLM-3.0-Nemotron-12B-Instruct`, and for 24B only `DictaLM-3.0-24B-Thinking` (there is no 24B Instruct). The 1.7B Instruct is the practical choice for per-message classification at volume; the 24B Thinking for offline summarization. DictaLM 2.0 (2024, 7B, based on Mistral-7B) is the previous generation and still works, but new builds should start on 3.0.

**Using DictaBERT (recommended for production).** The simplest path is `pipeline("sentiment-analysis", model="dicta-il/dictabert-sentiment")`, which resolves the label names off the model config for you. If you drive the model directly for batching control, wrap `AutoTokenizer` + `AutoModelForSequenceClassification`, tokenize with `truncation=True, max_length=512, padding=True`, softmax the logits, and map each row through `id2label`.

CRITICAL: read the label names from `model.config.id2label`, never from a hardcoded list. Label order is model metadata, not a convention, and it is not alphabetical. For `dicta-il/dictabert-sentiment` it is `{0: "Positive", 1: "Negative", 2: "Neutral"}`. A version of this skill that hardcoded `["negative","neutral","positive"]` was wrong at every index and reported every frustration spike as a satisfaction spike.

Full code, batching wrapper and the lexicon fallback: `references/hebrew-sentiment-guide.md`.

**Hebrew-specific sentiment challenges.** "לא רע" reads mildly positive in Israeli usage; sarcasm ("יופי, בדיוק מה שחיכיתי לו") is common and deeply negative; slang moves fast ("וואלה" is context-dependent); and users mix scripts in one message ("ה-support שלכם גרוע"). Negation handling, the slang lexicon and its token-boundary lookup rule: `references/hebrew-sentiment-guide.md`.

### Step 5: Intent Recognition Accuracy Tracking

Track how well your chatbot understands user requests over time:

Build `IntentAccuracyTracker` to log `(predicted, actual, confidence, timestamp)` per prediction and expose:

- `confusion_matrix()`: 2D `{actual: {predicted: count}}` over the sorted intent universe.
- `misclassification_report(min_count=5)`: top `(actual, predicted)` pairs where `predicted != actual`.
- `low_confidence_intents(threshold=0.6)`: intents whose mean confidence is below `threshold`, with `sample_count` and `below_threshold_pct`.
- `accuracy_trend()`: daily `{date, accuracy, sample_count}` series for plotting (bucket by `timestamp[:10]`).

**How to get ground truth labels.** Sample 100-200 conversations a week and have Hebrew-speaking annotators label the actual intent; this is the gold standard. Supplement it with escalation signals (a user correcting the bot, "לא, התכוונתי ל...", or asking for a human right after a misunderstanding, flags the prior intent as wrong) and post-chat surveys asking "Did the bot understand what you needed?" correlated with the detected intent.

### Step 6: User Satisfaction Measurement

Combine multiple signals to build a satisfaction score:

Build a `SatisfactionSignals` dataclass carrying direct feedback (`csat_score` 1-5, `thumbs_rating` "up"/"down"), behavioural signals (`session_resolved`, `escalated_to_human`, `abandoned`, `repeated_fallbacks`, `loop_detected`) and sentiment signals (`final_sentiment` positive/neutral/negative, `sentiment_trend` improving/stable/declining).

Its `composite_score() -> float` returns 0.0-1.0. If `csat_score` is present, return `(csat_score - 1) / 4` directly and stop. Otherwise start at 0.5 (or 0.8 / 0.2 for thumbs up / down), then apply: +0.15 resolved, -0.1 escalated, -0.2 abandoned, -0.15 if `repeated_fallbacks > 2`, -0.2 loop detected, +/-0.1-0.15 for `final_sentiment`, +/-0.05-0.1 for `sentiment_trend`; clamp to [0, 1].

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

**Common Hebrew A/B test dimensions.** Formality ("כיצד נוכל לסייע?" vs "איך אפשר לעזור?") against completion rate; gender handling (slash notation "את/ה" vs gender-neutral "ניתן ל...") against satisfaction; response length against drop-off; emoji use against engagement; and error phrasing ("לא הצלחתי להבין" vs "אפשר לנסח אחרת?") against retry rate.

### Step 8: Performance Dashboards and KPIs

Build a `ChatbotDashboard` dataclass grouping the fields below, plus a `to_report_dict()` that renders them by section (rates as %, times as ms):

| Group | Fields |
|-------|--------|
| Core | `total_conversations`, `resolution_rate`, `first_contact_resolution`, `avg_handle_time_seconds`, `escalation_rate`, `abandonment_rate` |
| Satisfaction | `avg_csat` (1-5), `nps_score` (-100..100), `thumbs_up_ratio` |
| Intent quality | `high_confidence_rate`, `intent_accuracy` (`float \| None`, needs labelled data), `fallback_rate` |
| Performance | `avg_response_time_ms`, `p95_response_time_ms` |
| Volume | `conversations_per_day`, `peak_hour` (0-23), `busiest_day` |

Implement `build_dashboard(conversations, period_days=7)` to populate the dataclass:

- Outcome rates from `Counter(c["outcome"])` / `n`.
- `avg_handle_time_seconds` from `(ended_at - started_at).total_seconds()` per session.
- `avg_csat` from `satisfaction_score` where present.
- `avg_response_time_ms` / `p95_response_time_ms` from bot messages with `response_time_ms` (p95 by nearest rank, `sorted_rts[math.ceil(0.95 * n) - 1]`).
- `high_confidence_rate` = share of user messages with `intent_confidence > 0.7`. `fallback_rate` = share of user messages with `intent == "fallback"`.
- `intent_accuracy` stays `None` unless you have ground-truth labels. Populate it only from `IntentAccuracyTracker` (Step 5) and render `n/a` otherwise. Model confidence is not accuracy: a confident but wrong classifier scores 100% on confidence and can be wrong on every prediction, and this is the number most likely to be quoted to management.
- `conversations_per_day = n / period_days`. `peak_hour` and `busiest_day` from `Counter` over `started_at` hour and weekday.

**Israeli traffic patterns to expect.** These follow from the Sun-Thu work week and are working assumptions, not a measured dataset. Confirm each against your own logs before building a staffing or alerting rule on it.
- Convert timestamps to Israel time (Asia/Jerusalem) before bucketing by hour or weekday. BigQuery exports are UTC, so without the conversion a session that opened at 01:30 on Sunday in Israel lands on Saturday night.
- Peak hours are typically 10:00-12:00 and 19:00-22:00 (Israel Time, UTC+2/+3)
- Sunday is the busiest day (first workday of the Israeli week)
- Friday afternoon and Saturday see minimal traffic
- Holiday periods (Rosh Hashana, Pesach, Sukkot) show different patterns

#### Retention and Returning-User Metrics

Session-level metrics tell you how a single conversation went, but not whether the bot earns repeat use. Track these retention dimensions alongside the dashboard above (all require a stable `user_id` across sessions, pseudonymized per the Privacy and Consent section):

For each `user_id`, collect the set of distinct Israel-local dates with a conversation, then compute: **D1 return rate** (first date + 1 day is also in the set), **D7 return rate** (any of first date + 2..7 days is in the set, more stable than D1 at Israeli volumes), and **repeat-contact rate** (more than one distinct date). Count a user toward D1 or D7 only when their window ends on or before the last day in the log, or users first seen in the last week drag D7 toward zero. On a support bot a high repeat rate can mean trust or unresolved issues, so always read it next to first-contact resolution. The bundled script computes all three.

### Step 9: Hebrew-Specific Analytics Challenges

#### RTL Text in Charts and Visualizations

When rendering analytics dashboards that display Hebrew text, handle these RTL issues:

Set `matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Arial", "Heebo"]` so Hebrew glyphs render at all, then apply `bidi.algorithm.get_display()` (the `python-bidi` package) to every label before drawing, because matplotlib has no native RTL. Prefer horizontal bar charts so Hebrew labels sit on the y-axis and read naturally. For interactive dashboards Plotly handles RTL better than matplotlib: use `font-family: "Heebo, Arial, sans-serif"` and add extra inline-start margin for the labels.

#### Hebrew Word Tokenization for Word Clouds

Whitespace tokenization fails on Hebrew because of the prefix particles (ב, ה, ו, ל, מ, כ, ש). Use the YAP morphological analyzer (https://github.com/OnlpLab/yap) in production, or strip common prefixes, only when the word is longer than 3 characters and the remainder is at least 2. For word clouds, run the bidi algorithm before rendering and drop stopwords (של, את, על, עם, אני, זה, כי, גם, לא, יש, אין, מה). Full tokenizer code: `references/hebrew-sentiment-guide.md`.

#### Mixed Hebrew-English Query Handling

Israeli users code-switch constantly, so classify per message and track the mix. Count Hebrew characters (`[\u0590-\u05FF]`) against Latin ones (`[a-zA-Z]`): no letters at all is `unknown` and must NOT count toward the denominator; otherwise `he` when Hebrew is at least half the letters, `en` below that. Track the code-switching rate separately as the share of classifiable messages that are 20-80% Hebrew. That band overlaps the primary-language buckets on purpose: a message can be both Hebrew and code-switched. Treating them as three exclusive buckets is what made an earlier version of the bundled script disagree with this rule on the same log.

### Step 10: Alerting and Anomaly Detection

Define an `AlertRule` dataclass with `name`, `metric`, `operator` (`"gt"` / `"lt"`), `threshold`, `window_minutes`, `severity` (`critical` / `warning` / `info`) and `description_he`, the Hebrew text the ops team will actually read. The three that catch the most real incidents are `satisfaction_drop` (`avg_csat` lt 3.0 over 120 min, critical), `high_abandonment` (`abandonment_rate` gt 0.40 over 60 min, critical) and `high_fallback_rate` (`fallback_rate` gt 0.25 over 30 min, warning). The full six-rule starting set with Hebrew descriptions is in `references/chatbot-metrics-glossary.md`.

These thresholds are starting bars, not benchmarks: replace each with your own baseline after four weeks of data. They also assume a dialogue-managed bot. On an LLM bot the `slow_response` p95 rule at 3 seconds fires permanently and gets muted, taking the real latency signal with it, so swap it for the time-to-first-token rule in `references/llm-bot-observability.md`.

`AlertManager` wraps the rule list. `check_metrics(current_metrics: dict)` walks every rule, skips when the metric is missing, and triggers when `value > threshold` (op `gt`) or `value < threshold` (op `lt`). Each triggered alert is a dict with `rule_name`, `severity`, `metric`, `current_value`, `threshold`, `description_he`, and `triggered_at`.

### Step 11: Reporting Templates

Generate periodic reports summarizing chatbot performance:

Implement `generate_weekly_report(dashboard, previous_dashboard=None, period_start, period_end)`:

- Helper `trend_arrow(current, previous, higher_is_better)`: returns `(ללא שינוי)` for < 1% delta; otherwise emits `[v] +X.X%` (good direction) or `[!] +X.X%` (bad direction).
- Emit a `# דוח ביצועי צ'אטבוט שבועי` header, period subheader, and a `| מדד | ערך | שינוי מהשבוע הקודם |` markdown table over: שיחות, שיעור פתרון, CSAT, שיעור הסלמה (lower-is-better), שיעור נטישה (lower-is-better), שיעור ניבויים בביטחון גבוה, זמן תגובה ממוצע (lower-is-better). Render a `דיוק זיהוי כוונות` row only when labelled data produced a real `intent_accuracy`.
- Append a `## תנועה` block with `conversations_per_day`, `peak_hour`, `busiest_day`.

### Step 12: Integration with Chatbot Platforms

Each platform exports conversations in its own shape; normalize every one of them to the Step 1 schema and the metrics above run unchanged. Parser recipes for the Conversational Agents (Dialogflow CX) BigQuery export and the Rasa tracker store, plus the Hebrew language-code and Rasa-version caveats, are in `references/platform-integrations.md`. Botpress, ManyChat, WhatsApp webhook logs and custom bots have no canonical export shape and must be mapped by hand.

## WhatsApp Business Platform pricing notes

Meta changed what is free on 1 October 2026, so any cost model built before then is wrong. Service messages, including a human agent's replies, are now charged after the first 1,000 per business phone number per month, and utility templates inside an open customer-service window are charged again. Messages inside a free-entry-point (FEP) window, opened by a click-to-WhatsApp ad, stay free for up to 7 days. Without a payment method on the account, service replies simply stop being delivered after the free 1,000, so alert on failed deliveries. Israel is a standalone market on the rate card, so its rate is public: pull it each quarter. Log the `pricing` object (`billable`, `category`, `type`) from each message's delivered-status webhook rather than estimating cost; the bundled script counts it by category, by type and per number per month. Rates, the AI Providers rules (Israel is not a listed market) and the fields to log: `references/chatbot-metrics-glossary.md`.

## Anti-spam compliance (Israel Communications Law, Section 30A)

If your chatbot sends marketing messages (WhatsApp promotional templates, Telegram campaigns, SMS), Section 30A of the Communications Law (Telecom and Broadcasts), 5742-1982 requires the recipient's **express prior consent, in writing**, before sending an advertisement by electronic message or short message. Neither statutory definition names a channel, so plan as if WhatsApp and Telegram broadcasts are in scope. A click on a click-to-WhatsApp ad, or an earlier service chat, is not consent: being free inside the FEP window does not make a marketing template lawful. For consumers, the only exception is Section 30A(c), for a customer who gave their details while buying, was told they would get advertising and given a chance to refuse, and is offered something similar. Log `opt_in_basis` as `written_consent`, `existing_customer` or `service_only`. A reply such as "הסר" or "stop" is a refusal (Section 30A(d)(1)): route it to a confirmation step, never to a fallback; the bundled script flags likely ones. Labelling rules and the SMS carve-out: `references/chatbot-metrics-glossary.md`.

This is engineering guidance, not legal advice. A court may award exemplary damages, with no proof of harm, of up to NIS 1,000 for each advertisement sent knowingly in breach (Section 30A(j)(1)), so one misconfigured broadcast can be a six-figure exposure. Confirm your position with a lawyer.

## Experimentation and analytics stack

`HebrewABTestManager` (Step 7) does in-process bucketing with in-memory results. For sequential testing or CUPED variance reduction, move to Statsig, LaunchDarkly or GrowthBook: none of them care what language `variant_text` is in, and GrowthBook is the one that never ingests your event data, so Hebrew transcripts stay in your own warehouse. Plan on 2+ weeks and 200+ impressions per variant; Israeli user bases are small and the Sun-Thu week makes one-week tests unreliable.

On the analytics side, Google's definition of the GA4 `AI Assistant` channel (Medium `ai-assistant`) does not name Claude or Perplexity among its examples, so check your referral report before relying on it, and Mixpanel's AI query builder is now **Mixpanel Agent**, with an MCP server. Ownership, pricing and naming detail (Statsig changed hands twice in 2025-2026): `references/analytics-stack-notes.md`.

## LLM and RAG bot observability

If your bot generates answers with an LLM rather than matching intents, Steps 5 and 8 measure the wrong things: there is no intent label to score, no fallback to count, and a fluent wrong answer registers as a completed session. The session-level metrics (drop-off, escalation, CSAT, retention) still apply unchanged; what you add on top is groundedness, retrieval hit rate, tool-call success rate, and cost per **resolved** conversation. Log retrieved chunk ids against the ids the answer cited. This is a citation-compliance canary, not groundedness. See `references/llm-bot-observability.md`.

An LLM-as-judge scorer is the standard fallback where you have no ground truth, but calibrate it against Hebrew-speaking human annotators before quoting its output as accuracy, and run it on a weekly sample rather than on every turn. The Step 8 warning about confidence being mistaken for accuracy applies to judge scores with equal force.

Field-level schema additions, the four metrics to build first, judge-calibration procedure, OpenTelemetry GenAI tracing conventions and the LLM-specific alert rules: `references/llm-bot-observability.md`.

## Examples

### Example 1: Analyze chatbot performance for the past week

"Analyze my Hebrew chatbot logs from the past week and show me where users are dropping off."

Load the period's logs, run `compute_flow_metrics()`, `detect_drop_off_points()` and `detect_conversation_loops()`, then summarize completion rate, top drop-off points and looping sessions with actionable recommendations.

### Example 2: Set up A/B testing for greeting messages

"I want to test whether a formal or casual Hebrew greeting works better."

Create the test with `HebrewABTestManager.create_test()`, variants formal ("כיצד נוכל לסייע לכם היום?") vs. casual ("היי! מה אפשר לעשות בשבילך?"), 50/50 split, wire it into the greeting handler, and track completion rate, CSAT and escalation per variant.

### Example 3: Set up anomaly alerting

"Alert me if chatbot satisfaction drops suddenly."

Configure `AlertManager` with the satisfaction and escalation rules, compute metrics over rolling windows, route alerts to Slack / email / PagerDuty, and keep the Hebrew `description_he` text for the ops team.

### Example 4: Generate a weekly performance report

"Create a Hebrew weekly report for the chatbot team."

Run `build_dashboard()` for the current and previous week, pass both to `generate_weekly_report()` for trend arrows, and add drop-off and intent breakdowns. Output is RTL-compatible Hebrew markdown.

## Bundled Resources

### Scripts
- `scripts/conversation-analyzer.py` -- Pure standard library, no pip install. Computes outcome rates (including the unknown-outcome share it warns on), drop-off points, conversation loops, intent confidence, response-time percentiles, Israel-time traffic patterns, D1/D7/repeat-contact retention, Hebrew/English code-switching, WhatsApp billable counts when messages carry the `pricing` object, likely opt-out replies for manual review (a triage aid, not a legal determination), and sessions with a gap over the inactivity timeout. Tolerates media messages with no text. It does NOT compute sentiment: that needs the DictaBERT path in Step 4. Run: `python3 scripts/conversation-analyzer.py --help`

### References
- `references/chatbot-metrics-glossary.md` -- Glossary of chatbot analytics metrics with Hebrew translations and industry benchmarks. Consult when defining KPIs or explaining metrics to Hebrew-speaking stakeholders.
- `references/analytics-stack-notes.md` -- Vendor detail for the experimentation and analytics stack (Statsig / LaunchDarkly / GrowthBook, GA4 AI Assistant channel, Mixpanel Agent and MCP). Consult before picking or pricing a tool.
- `references/platform-integrations.md` -- Parser recipes folding each vendor's conversation export (Conversational Agents / Dialogflow CX BigQuery, Rasa tracker store) into the standard schema. Consult when onboarding logs from a new platform.
- `references/llm-bot-observability.md` -- Measurement layer for LLM-backed and RAG chatbots: log-schema additions, groundedness and retrieval metrics, LLM-as-judge calibration, tracing, and LLM-specific alert rules. Consult when the bot generates answers instead of matching intents.
- `references/hebrew-sentiment-guide.md` -- Guide to Hebrew sentiment analysis challenges including negation, sarcasm, slang, and mixed-language handling. Consult when building or tuning Hebrew sentiment models.

## Gotchas

- Hebrew sentiment analysis requires Israeli-specific training data. Standard English sentiment models misclassify Hebrew sarcasm (very common in Israeli communication) as neutral or positive.
- Israeli chatbot usage peaks on Sunday mornings (start of work week), not Monday. Weekly analytics reports should anchor to Sunday-Thursday.
- Hebrew text analytics must handle prefixed particles (ב-, ל-, כ-, מ-) that change word boundaries. Standard tokenizers trained on English split Hebrew words incorrectly.
- Israeli users frequently code-switch between Hebrew and English within a single chatbot conversation. Analytics tools must handle bilingual sessions, not treat them as two separate languages.

## Privacy and Consent

This skill ingests full conversation transcripts and `user_id` values, and runs sentiment analysis on user messages. Conversation text is personal data and often contains sensitive content (health, finances, complaints). Handle it under Israel's Privacy Protection Law as amended by Amendment 13 (in force 14 August 2025). Section 11 sets what the notice must say when you collect the data (list sentiment analysis among the purposes); Section 17B1 requires a privacy protection officer where the main activity includes processing especially sensitive information at significant scale, naming banks, insurers, general hospitals and health funds. Sending transcripts to Meta's servers or to a foreign LLM or analytics vendor is a transfer abroad, allowed only on a ground in the Transfer Regulations (for example the person's consent, or a contractual undertaking by the recipient). A severe security incident must be reported to the Registrar immediately.

Practical rules, and each provision in full, in `references/chatbot-metrics-glossary.md`: pseudonymize `user_id` before it reaches the pipeline; mask entities you do not need (ID numbers, names, card numbers); set a retention window for raw transcripts (for example 90 days) and keep aggregates long-term; restrict and log access (the Data Security Regulations keep access logs of medium and high security databases for at least 24 months, separate from transcript retention).

- This is engineering guidance, not legal advice. Confirm your specific obligations with a privacy professional.

## Recommended MCP Servers

None is required: the skill analyzes exported logs locally with the bundled script. If your metrics already live in Mixpanel, its MCP server lets the agent query them, which is optional.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Conversational Agents (Dialogflow CX) language reference | https://docs.cloud.google.com/dialogflow/cx/docs/reference/language | Hebrew language code `he-il`; the table lists `Hebrew (deprecated) iw` with fewer supported features |
| Dialogflow CX analytics | https://docs.cloud.google.com/dialogflow/cx/docs/concept/analytics | Built-in conversation analytics, intent metrics |
| Rasa CALM docs | https://rasa.com/docs/learn/concepts/calm/ | Dialogue-driven flows for Rasa Pro, replaces intent-based design for new builds |
| Rasa OSS documentation (legacy) | https://legacy-docs-oss.rasa.com/docs/rasa/ | Event tracking, tracker stores, custom analytics integrations (maintenance mode) |
| WhatsApp Business Platform pricing | https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing | Israel rate card row, the 1 October 2026 changes, FEP window, monthly free service tier, Meta Business Agent |
| DictaBERT (Hebrew BERT suite) | https://huggingface.co/dicta-il/dictabert | Pre-trained Hebrew BERT for classification fine-tunes |
| DictaBERT sentiment | https://huggingface.co/dicta-il/dictabert-sentiment | Off-the-shelf Hebrew sentiment classifier (3-class) |
| Dicta-LM 3.0 (technical report) | https://arxiv.org/abs/2602.02104 | Current Hebrew model family (24B / 12B / 1.7B, 65k context, tool-calling chat variants) |
| DictaLM 2.0 Instruct (previous generation) | https://huggingface.co/dicta-il/dictalm2.0-instruct | Generative Hebrew LLM (7B, Mistral-based); superseded by Dicta-LM 3.0 |
| AlephBERT | https://huggingface.co/onlplab/alephbert-base | Alternative Hebrew BERT from BIU OnlpLab |
| GA4 default channel group (Google) | https://support.google.com/analytics/answer/9756891 | AI Assistant channel: Medium `ai-assistant`, the `(ai-assistant)` campaign value, which assistants Google names |
| Mixpanel Agent (formerly Spark) | https://docs.mixpanel.com/docs/mixpanel-agent | Current name and capabilities of the AI query builder |
| OpenTelemetry GenAI semantic conventions | https://github.com/open-telemetry/semantic-conventions-genai | Span attribute names for model, token counts and tool calls when tracing an LLM bot |
| Privacy Protection Law, consolidated Hebrew text | https://he.wikisource.org/wiki/חוק_הגנת_הפרטיות | Section 11 notice contents, Section 17B1 privacy-officer duty |
| Communications Law, Section 30A (consolidated Hebrew text) | https://he.wikisource.org/wiki/חוק_התקשורת_(בזק_ושידורים) | Consent, the required labelling, the SMS carve-out, and the NIS 1,000 exemplary-damages cap |
| Israel Privacy Amendment 13 (IAPP) | https://iapp.org/news/a/israel-marks-a-new-era-in-privacy-law-amendment-13-ushers-in-sweeping-reform | Effective Aug 14, 2025: consent, notice, retention limits, deletion mechanisms |

## Troubleshooting

- **DictaBERT model not loading**: the `dicta-il/dictabert-sentiment` model needs PyTorch + `transformers`. Run `pip install torch transformers` (known to work on the transformers 5.x line; pin whichever version you have actually tested); for CPU-only, install torch from `https://download.pytorch.org/whl/cpu`.
- **Sentiment labels look inverted**: you hardcoded a label list. Read `model.config.id2label` instead. For `dicta-il/dictabert-sentiment` it is `{0: "Positive", 1: "Negative", 2: "Neutral"}`.
- **Timestamps parse to nothing on older Python**: `datetime.fromisoformat` only handles the full ISO-8601 range, including a trailing `Z`, from Python 3.11. On 3.10 (end of life since 2026-10-01) the parse fails and durations and traffic patterns come back empty. Use Python 3.11 or newer.
- **Peak day shows Saturday on a Sunday-heavy bot**: the timestamps are UTC and were bucketed without converting to Israel time. The bundled script converts any timestamp that carries an offset or `Z`; one with no offset is assumed to be Israel time and counted in the report.
- **Hebrew text appears reversed in charts**: matplotlib has no native RTL. Apply `python-bidi` (`bidi.algorithm.get_display()`) before rendering, or switch to Plotly.
- **Tokenization produces wrong word frequencies**: whitespace splitting ignores Hebrew prefix particles. Use the prefix-stripping tokenizer in Step 9, or the YAP morphological analyzer (https://github.com/OnlpLab/yap) for production.
- **Sentiment scores unreliable for short messages**: 1-3 word messages lack context ("סבבה" can be positive or neutral). Under 4 words, rely on behavioral signals (continued / escalated / abandoned) plus the Step 6 satisfaction signals.
- **A/B test results not statistically significant**: usually too small a sample, common for Israeli user bases. Run at least 2 weeks, 200+ impressions per variant, target p < 0.05.
