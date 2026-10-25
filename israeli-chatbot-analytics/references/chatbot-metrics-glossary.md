# Chatbot Analytics Metrics Glossary / מילון מונחי אנליטיקת צ'אטבוט

A comprehensive glossary of chatbot analytics metrics with Hebrew translations and industry benchmarks. Every **Benchmark** line below is a general support-chatbot convention with no Israeli sample behind it: use it as a starting bar and replace it with your own baseline after four weeks of data. Use this reference when defining KPIs, building dashboards, or explaining metrics to Hebrew-speaking stakeholders.

## Core Metrics / מדדים מרכזיים

### Resolution Rate / שיעור פתרון
**Definition:** Percentage of conversations where the chatbot successfully resolved the user's issue without human intervention.
**Hebrew:** אחוז השיחות שבהן הצ'אטבוט פתר את הבעיה של המשתמש בלי התערבות אנושית.
**Formula:** `resolved_conversations / total_conversations * 100`
**Benchmark:** Good > 70%, Average 50-70%, Needs improvement < 50%
**Also known as:** Containment rate, automation rate

### First Contact Resolution (FCR) / פתרון במגע ראשון
**Definition:** Percentage of issues resolved in a single conversation session, without the user returning for the same issue.
**Hebrew:** אחוז הבעיות שנפתרו בסשן שיחה אחד, בלי שהמשתמש חזר לאותה בעיה.
**Formula:** `single_session_resolutions / total_resolutions * 100`
**Benchmark:** Good > 65%, Average 45-65%, Needs improvement < 45%

### Escalation Rate / שיעור הסלמה
**Definition:** Percentage of conversations transferred to a human agent.
**Hebrew:** אחוז השיחות שהועברו לנציג אנושי.
**Formula:** `escalated_conversations / total_conversations * 100`
**Benchmark:** Good < 15%, Average 15-30%, Needs improvement > 30%

### Abandonment Rate / שיעור נטישה
**Definition:** Percentage of conversations where the user left before reaching a resolution or escalation.
**Hebrew:** אחוז השיחות שבהן המשתמש עזב לפני שהגיע לפתרון או הסלמה.
**Formula:** `abandoned_conversations / total_conversations * 100`
**Benchmark:** Good < 20%, Average 20-35%, Needs improvement > 35%

### Fallback Rate / שיעור Fallback
**Definition:** Percentage of user messages that the chatbot could not classify into a known intent.
**Hebrew:** אחוז ההודעות שהצ'אטבוט לא הצליח לסווג לכוונה מוכרת.
**Formula:** `fallback_messages / total_user_messages * 100`
**Benchmark:** Good < 10%, Average 10-20%, Needs improvement > 20%

## User Satisfaction Metrics / מדדי שביעות רצון

### CSAT (Customer Satisfaction Score) / ציון שביעות רצון לקוח
**Definition:** Average satisfaction rating from post-chat surveys, typically on a 1-5 scale.
**Hebrew:** ממוצע דירוגי שביעות רצון מסקרים אחרי שיחה, בדרך כלל בסקאלה 1-5.
**Formula:** `sum(ratings) / count(ratings)`
**Benchmark:** Good > 4.0, Average 3.0-4.0, Needs improvement < 3.0

### NPS (Net Promoter Score) / ציון NPS
**Definition:** Measures likelihood of recommending the chatbot. Scale 0-10. Promoters (9-10) minus Detractors (0-6).
**Hebrew:** מודד סבירות להמליץ על הצ'אטבוט. סקאלה 0-10. מקדמים (9-10) פחות מלעיזים (0-6).
**Formula:** `promoters_pct - detractors_pct` (both already expressed as percentages; do not multiply by 100 again)
**Range:** -100 to +100
**Benchmark:** Good > 30, Average 0-30, Needs improvement < 0

### Thumbs Up Ratio / יחס אגודלים למעלה
**Definition:** Percentage of positive thumbs ratings out of all thumbs ratings.
**Hebrew:** אחוז דירוגי האגודל למעלה מתוך כל דירוגי האגודלים.
**Formula:** `thumbs_up / (thumbs_up + thumbs_down) * 100`
**Benchmark:** Good > 80%, Average 60-80%, Needs improvement < 60%

## Conversation Quality Metrics / מדדי איכות שיחה

### Average Session Length / אורך סשן ממוצע
**Definition:** Average number of messages per conversation session.
**Hebrew:** מספר הודעות ממוצע לכל סשן שיחה.
**Formula:** `sum(session_message_counts) / total_sessions`
**Benchmark:** 4-8 messages is ideal. Too short may mean unresolved issues; too long suggests confusion.

### Average Handle Time (AHT) / זמן טיפול ממוצע
**Definition:** Average duration of a conversation from start to end.
**Hebrew:** משך ממוצע של שיחה מתחילתה ועד סופה.
**Formula:** `sum(session_durations) / total_sessions`
**Benchmark:** Varies by domain. E-commerce: 2-5 min, Support: 5-10 min, Complex services: 10-20 min.

### Loop Rate / שיעור לולאות
**Definition:** Percentage of conversations where the bot repeated the same response 3+ times consecutively.
**Hebrew:** אחוז השיחות שבהן הבוט חזר על אותה תגובה 3 פעמים או יותר ברצף.
**Benchmark:** Good < 3%, Needs improvement > 5%

### Conversation Depth at Drop-off / עומק שיחה בנקודת נטישה
**Definition:** The message index at which users most commonly abandon conversations.
**Hebrew:** מיקום ההודעה שבו משתמשים נוטשים בתדירות הגבוהה ביותר.
**Usage:** Identify problematic bot prompts at common drop-off depths.

## Intent Accuracy Metrics / מדדי דיוק כוונות

### Intent Recognition Accuracy / דיוק זיהוי כוונות
**Definition:** Percentage of user messages where the detected intent matches the actual user intent.
**Hebrew:** אחוז ההודעות שבהן הכוונה שזוהתה תואמת את הכוונה האמיתית של המשתמש.
**Formula:** `correct_predictions / total_predictions * 100`
**Benchmark:** Good > 85%, Average 70-85%, Needs improvement < 70%
**Note:** Requires ground truth labels from manual annotation.

### Confidence Distribution / התפלגות רמת ביטחון
**Definition:** Distribution of confidence scores across intent predictions.
**Hebrew:** התפלגות ציוני ביטחון בתחזיות כוונה.
**Usage:** Look for bimodal distributions (many high + many low) as a sign that certain intents need more training data.

### Confusion Rate / שיעור בלבול
**Definition:** For a specific intent pair, the percentage of times intent A was classified as intent B.
**Hebrew:** עבור זוג כוונות ספציפי, אחוז הפעמים שכוונה A סווגה ככוונה B.
**Usage:** Identify intent pairs that need better differentiation.

## Performance Metrics / מדדי ביצועים

### Average Response Time / זמן תגובה ממוצע
**Definition:** Average time between receiving a user message and sending the bot response.
**Hebrew:** זמן ממוצע בין קבלת הודעת משתמש לשליחת תגובת הבוט.
**Benchmark:** Good < 1s, Average 1-3s, Needs improvement > 3s

### P95 Response Time / זמן תגובה P95
**Definition:** 95th percentile response time. 95% of responses are faster than this value.
**Hebrew:** זמן תגובה באחוזון ה-95. 95% מהתגובות מהירות יותר מערך זה.
**Benchmark:** Good < 2s, Average 2-5s, Needs improvement > 5s

### Uptime / זמן פעילות
**Definition:** Percentage of time the chatbot is available and responsive.
**Hebrew:** אחוז הזמן שהצ'אטבוט זמין ומגיב.
**Benchmark:** Target 99.9% or higher.

## Volume Metrics / מדדי נפח

### Conversations Per Day / שיחות ביום
**Definition:** Total number of conversation sessions initiated per day.
**Hebrew:** מספר סשני שיחה שנפתחו ביום.

### Peak Hour / שעת שיא
**Definition:** Hour of day with highest conversation volume.
**Hebrew:** שעה ביום עם נפח השיחות הגבוה ביותר.
**Israeli note:** Typical peaks at 10:00-12:00 and 19:00-22:00 Israel Time.

### Channel Distribution / התפלגות ערוצים
**Definition:** Breakdown of conversations by channel (WhatsApp, Telegram, web, app).
**Hebrew:** פילוח שיחות לפי ערוץ (וואטסאפ, טלגרם, אתר, אפליקציה).
**Israeli note:** WhatsApp is the dominant messaging channel in Israel, so expect it to lead your channel split. We have no sourced figure for its share of chatbot conversations; measure your own rather than quoting a number.

## A/B Testing Metrics / מדדי בדיקות A/B

### Statistical Significance / מובהקות סטטיסטית
**Definition:** Confidence level that observed differences between variants are not due to chance.
**Hebrew:** רמת ביטחון שההבדלים שנצפו בין הווריאנטים לא נובעים ממקריות.
**Standard:** p < 0.05 (95% confidence)
**Israeli note:** Hebrew chatbots often have smaller user bases. Plan for longer test durations (2+ weeks), and expect a larger minimum detectable effect: with less traffic only bigger differences reach significance.

### Minimum Detectable Effect (MDE) / אפקט מינימלי ניתן לגילוי
**Definition:** Smallest difference between variants that the test can reliably detect.
**Hebrew:** ההבדל הקטן ביותר בין ווריאנטים שהבדיקה יכולה לזהות באופן אמין.
**Guideline:** State the baseline and whether the effect is absolute or relative. At 200 impressions per variant with a 50% baseline completion rate, the smallest reliably detectable change is roughly 14 percentage points absolute. At a 10% baseline you need roughly ten times that sample for the same relative sensitivity. Treat "200 impressions per variant" as a floor for running a test at all, not as a sample that can detect small effects.

## Sentiment Metrics / מדדי סנטימנט

### Sentiment Distribution / התפלגות סנטימנט
**Definition:** Breakdown of user messages by detected sentiment (positive, neutral, negative).
**Hebrew:** פילוח הודעות משתמשים לפי סנטימנט שזוהה (חיובי, ניטרלי, שלילי).

### Sentiment Trend / מגמת סנטימנט
**Definition:** Change in average sentiment score over time within a conversation or across conversations.
**Hebrew:** שינוי בציון סנטימנט ממוצע לאורך זמן בתוך שיחה או בין שיחות.
**Usage:** Declining sentiment within a conversation signals user frustration.

### Mixed Language Rate / שיעור שפה מעורבת
**Definition:** Percentage of messages containing both Hebrew and English text.
**Hebrew:** אחוז ההודעות שמכילות טקסט גם בעברית וגם באנגלית.
**Israeli note:** Code-switching is common in Israeli tech-oriented chatbots. We have no sourced baseline for the rate, so measure yours before setting a target.

## Benchmark Summary Table / טבלת סיכום בנצ'מרקים

| Metric / מדד | Good / טוב | Average / ממוצע | Needs Work / לשיפור |
|--------------|-----------|----------------|---------------------|
| Resolution Rate / פתרון | > 70% | 50-70% | < 50% |
| FCR / מגע ראשון | > 65% | 45-65% | < 45% |
| Escalation / הסלמה | < 15% | 15-30% | > 30% |
| Abandonment / נטישה | < 20% | 20-35% | > 35% |
| Fallback Rate | < 10% | 10-20% | > 20% |
| CSAT | > 4.0/5 | 3.0-4.0 | < 3.0 |
| Intent Accuracy / דיוק | > 85% | 70-85% | < 70% |
| Avg Response Time / תגובה | < 1s | 1-3s | > 3s |
| Session Length / אורך | 4-8 msgs | 8-15 msgs | > 15 msgs |
| Loop Rate / לולאות | < 3% | 3-5% | > 5% |


## WhatsApp Business Platform pricing

Many Israeli chatbots run on WhatsApp Cloud API, where send-out cost is a first-class analytics dimension. Meta bills per delivered message (since 1 July 2025), by category and by the recipient's market, and only for messages from the business to the user. Meta changed what is free on **1 October 2026**; a cost model built before then is wrong.

| Category | What it is | Israel list rate, USD, from 1 Oct 2026 |
|----------|-----------|-----------------------------------------|
| Marketing | Template, promotional | $0.0353 |
| Utility | Template, transactional (order updates, reminders) | $0.0053, volume tiers apply |
| Authentication | Template, OTP / identity checks | $0.0053, volume tiers apply |
| Service | Non-template reply inside the 24-hour customer-service window, from a third-party bot or a human | $0.0053 after the free tier |
| Meta Business Agent | Non-template reply generated by Meta's own agent platform (since 1 July 2026) | $2.00 per million tokens, no free messages |

Israel is a standalone market on the rate card, so the figure is public: take it from the rate card linked on the pricing page, and re-pull it every quarter, because Meta may change rates on 1 January, 1 April, 1 July and 1 October.

What is free now, and only this:

1. **Free-entry-point (FEP) window.** When a user messages you from a click-to-WhatsApp ad on the Android or iOS app and you reply inside the customer-service window, that reply is free and opens an FEP window that can stay open up to 7 days. Inside it, marketing, utility, authentication and service messages are all free; Meta Business Agent messages are still charged.
2. **The first 1,000 service messages per business phone number per month.** They do not roll over. From the 1,001st, service messages are charged.

What stopped being free on 1 October 2026: service messages beyond that tier (free since 1 November 2024), and utility templates sent inside an open customer-service window (free since 1 July 2025). A bot that answers inside the service window now has a real per-reply cost once the tier is spent. Two exceptions: Meta's **AI Providers** pricing policy (effective 16 February 2026; Meta's policy page was last updated 15 October 2026) is not affected by the October service-message change and has its own rules, so check whether your bot falls under it; and eligible government and non-profit organisations keep service messages free beyond the tier through 31 December 2027.

**Log the billing record, do not estimate it.** Each delivery status webhook carries a `pricing` object, for example `{"billable": true, "pricing_model": "PMP", "type": "regular", "category": "service"}`. A service message inside the free tier arrives as `"billable": false, "type": "free_customer_service"`; from the 1,001st it becomes `"type": "regular"`. Copy that object onto the outbound message in your log, and the bundled script reports billable and free counts per category and per `type`, and service messages per business phone number per month (an upper bound on what Meta meters against the tier; log one pricing object per message, from the "delivered" status). Count human agents too: Meta defines a service message as any non-template message not powered by Meta Business Agent, whether a third-party AI or "people (like customer service representatives)" sent it, so a handoff spends the same free tier (log the agent's messages with `sender: "agent"`). The free tier resets at midnight in the Messaging account's time zone. Tier progress is not in any webhook; reconcile against the `pricing_analytics` field, which gives per-message pricing breakdowns and tiering information.

**Two operational traps.** Without a payment method on the Messaging account, Meta delivers service messages within the free tier and then stops delivering them, so a bot goes silent mid-month: alert on failed-delivery statuses and on a number approaching 1,000 service messages. And ILS is not one of the 16 billing currencies (USD, AED, ARS, AUD, BRL, CLP, COP, EUR, GBP, IDR, INR, MXN, MYR, PEN, SAR, SGD), and the currency cannot be changed once the account exists, so budgets in shekels carry FX.

**AI Providers.** Under WhatsApp's terms as updated on 15 January 2026, "AI Providers" (providers of LLMs, generative AI platforms or general-purpose AI assistants) may offer general-purpose AI assistants on the platform only where Meta is legally required to permit it, and Israel (+972) is not among the markets Meta lists. A business's own LLM support bot answering its customers is the ordinary case; keep it task-scoped. Since 12 October 2026 the pricing object can also carry a `subtype`; `paid_exempt` marks a service message that is free because the sender is an eligible government or non-profit organisation. Also log `template_category`, a boolean `arrived_via_ctw_ad`, and, on the Marketing Messages API, the max price you set per marketing delivery (Meta then charges that price or lower). Then split CSAT and completion by paid versus free interaction.

## Anti-spam compliance: what to track

Operational tracking for the Section 30A opt-in regime described in SKILL.md.

Practical analytics tracking:

- **Tag every marketing send with its legal basis, `opt_in_basis`**: `written_consent` (express prior consent in writing, Section 30A(b)), `existing_customer` (Section 30A(c), see below), or `service_only` (no marketing may be sent). Record the arrival channel separately (`arrived_via_ctw_ad`): a click-to-WhatsApp ad click, a service conversation or a transactional message is not consent, and a marketing template being free inside the FEP window says nothing about whether it is lawful.
- **Two narrow carve-outs in 30A(b) and (b1), neither for consumer marketing.** The last sentence of 30A(b): "פנייה חד־פעמית מטעם מפרסם לנמען שהוא בית עסק או לנמען לשם קבלת תרומה או תעמולה, באחת הדרכים האמורות בסעיף קטן זה, המהווה הצעה להסכים לקבל דברי פרסומת מטעמו, לא תיחשב הפרה של הוראות סעיף זה" (a one-time approach to a business recipient, or for a donation or propaganda, offering to consent). 30A(b1) lets an amuta or public-benefit company send donation or propaganda e-mail unless the recipient refused.
- **The existing-customer exemption is narrow.** Section 30A(c) allows an advertisement without consent only when all three hold: the recipient gave their details while buying (or negotiating to buy) a product or service and was told they would be used for advertising; they were given a chance to refuse and did not; and the advertisement is for a product or service of a similar kind.
- **Refusals arrive as free text.** Under Section 30A(d)(1) the recipient may refuse at any time, in writing or in the way the advertisement was sent, so a WhatsApp reply of "הסר", "תסירו אותי" or "stop" is a refusal. Detect it as an intent, stop marketing to that user, and confirm; never let it fall to a fallback. The bundled script flags likely opt-out replies for a confirmation step (a keyword screen, not a classifier). Under Section 30A(d)(2), when an ongoing contract for goods or services ends the customer is treated as having refused.
- **Track unsubscribe path success rate.** Under Section 30A(e)(1) an advertisement must state, prominently and without misleading: that it is an advertisement (the word "פרסומת" at the start, or in the subject line of an electronic message); the advertiser's name, address and contact details; and the recipient's right to refuse at any time, with a simple way to do so (for an electronic message, a valid web address for refusal). Section 30A(e)(2) cuts this down for a short message to the advertiser's name and contact details for refusal. Measure time-to-unsubscribe and opt-out success rate as a compliance KPI.
- **Consent is express, prior and in writing.** Section 30A(b) bars an advertisement by fax, automatic dialing system, electronic message or short message without it; consent given by electronic message or in a recorded call counts. Store when and how each opt-in was given next to `opt_in_basis`.
- **Exposure.** Section 30A(j)(1) lets a court award exemplary damages, with no proof of harm, of up to NIS 1,000 per advertisement sent knowingly in breach.
- **Service vs. marketing split.** Run completion-rate and CSAT separately for opt-in marketing flows vs. user-initiated service flows, they behave very differently and combining them masks both.
- Cross-reference: `gws-hebrew-email-automation` and `israeli-telegram-business-bot` cover the same opt-in regime for email and Telegram. Use those skills if you also operate those channels.


## Default alert rules

Set up alerts to catch problems before they affect too many users. Add a minimum-sample guard to every rate rule (for example, skip the window when it holds fewer than 20 sessions): at night or on Shabbat one abandoned session out of two is 50% and would page someone for nothing, and a p95 over fewer than 20 responses is simply the maximum.

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


## Privacy and consent: practical rules

Two provisions of the Privacy Protection Law, both amended by Amendment 13 (in force 14 August 2025), apply directly to a chat-analytics pipeline:

- **Section 11, notice at collection.** A request for personal data to be processed in a database must state whether the person is legally required to give it or it depends on their consent, and what follows if they refuse; the purpose; the controller's name and contact details; who it will be passed to and why; and the rights of access (s.13) and correction (s.14).
- **Section 17B1, privacy protection officer.** Required for public bodies; for data brokers holding data on more than 10,000 people; for a controller or holder whose main activities require ongoing, systematic monitoring of people at significant scale; and for one whose main activity includes processing especially sensitive information at significant scale, the section naming banks, insurers, general hospitals and health funds.

- **Transfer abroad.** Under the Privacy Protection (Transfer of Data to Databases Abroad) Regulations, data from an Israeli database may leave the country only if the destination's law gives equivalent protection or a regulation 2 ground applies, for example the person's consent, or a recipient that undertook by contract to keep the conditions that apply to an Israeli database. Sending transcripts through WhatsApp Cloud API or to a foreign LLM, tracing or analytics vendor is such a transfer; record the ground.
- **Security level and incidents.** The Data Security Regulations assign a security level by schedule: a database that includes medical or mental-health information, financial-situation information, or the other categories in the First Schedule is medium (it drops to basic only if no more than ten people are authorized to access it, or if it holds only such data about the owner's own employees or suppliers for running the business), and the Second Schedule makes it high when it holds data on 100,000 people or more or has more than 100 authorized users. A support transcript store for a health fund, bank or insurer usually falls there. On a severe security incident the database owner must notify the Registrar immediately and report the steps taken.

Practical rules:

- **Consent and notice.** Get consent to store and analyze chat content, and tell users in your privacy notice that conversations are retained and analyzed for quality. Sentiment analysis on user messages is a processing purpose that should be disclosed.
- **Pseudonymize `user_id`.** Do not analyze raw phone numbers, emails, or Teudat Zehut as the identifier. Hash or tokenize `user_id` before it reaches the analytics pipeline, and keep the mapping table separate and access-controlled. Retention and A/B-test bucketing still work on a stable pseudonymous ID.
- **Minimize and redact.** Strip or mask entities you do not need for analytics (ID numbers, full names, card numbers) before storing transcripts. You rarely need the raw PII to measure drop-off or sentiment.
- **Retention limits.** Set an explicit retention window for raw transcripts (for example 90 days) and keep only aggregated metrics long-term. Document the window and delete on schedule.
- **Access control and location.** Restrict who can read raw conversations, log access, and confirm where the data is stored and processed. Note that the Data Security Regulations require access logs for medium and high security databases to be retained for at least 24 months, which is a separate obligation from transcript retention.
