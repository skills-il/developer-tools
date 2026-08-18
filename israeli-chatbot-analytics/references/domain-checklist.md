# Domain Coverage Checklist: Israeli Chatbot Analytics

Coverage contract for this skill. Each row states whether the skill covers the topic, and where. Rows marked "Out of scope (explicit)" must be re-litigated on every update: if a user would plausibly ask for it, or it became capturable since the last review, promote it.

Last reviewed: 2026-08-02 (v1.3.0).

## Measurement surface

| Topic | Status | Where |
|-------|--------|-------|
| Conversation log schema normalization | Covered | SKILL.md Step 1 |
| Session-level flow metrics (completion, escalation, abandonment) | Covered | Step 2 |
| Drop-off point detection, including fallback-driven drop-off | Covered | Step 3, scripts/conversation-analyzer.py |
| Conversation loop detection | Covered | Step 3, script |
| Intent recognition accuracy with ground-truth labels | Covered | Step 5 |
| Confidence distribution vs. accuracy (kept distinct) | Covered | Step 5, Step 8 |
| Satisfaction scoring (CSAT, thumbs, behavioral composite) | Covered | Step 6 |
| Retention and returning-user metrics (D1, D7, repeat contact) | Covered | Step 8 |
| Response-time percentiles (P50/P95/P99) | Covered | Step 8, script |
| Traffic patterns adjusted for the Israeli work week | Covered | Step 8, Gotchas |
| A/B testing with deterministic bucketing | Covered | Step 7 |
| Alerting and anomaly rules with Hebrew operator text | Covered | Step 10 |
| Weekly reporting template in Hebrew | Covered | Step 11 |

## Hebrew-specific handling

| Topic | Status | Where |
|-------|--------|-------|
| Sentiment model selection for Hebrew | Covered | Step 4, references/hebrew-sentiment-guide.md |
| Reading sentiment labels from model config rather than a literal | Covered | Step 4, Troubleshooting |
| Negation patterns, including the Israeli reading of "לא רע" | Covered | hebrew-sentiment-guide.md |
| Sarcasm and irony detection heuristics | Covered | hebrew-sentiment-guide.md |
| Slang and Arabic loanword lexicon | Covered | hebrew-sentiment-guide.md |
| Context-dependent idioms kept out of the fixed-score lexicon | Covered | hebrew-sentiment-guide.md ambiguous table |
| Prefix-particle tokenization for word frequency | Covered | Step 9 |
| Mixed Hebrew-English code-switching detection | Covered | Step 9, script |
| RTL rendering in charts | Covered | Step 9, Troubleshooting |

## Platform integrations

| Topic | Status | Where |
|-------|--------|-------|
| Conversational Agents (formerly Dialogflow CX) BigQuery export | Covered | Step 1, Step 12 |
| Rasa tracker store (Rasa Open Source, legacy) | Covered | Step 12 |
| Rasa Pro CALM, and why intent KPIs do not transfer | Noted, not implemented | Step 12 preamble |
| WhatsApp Cloud API cost dimensions | Covered | WhatsApp pricing section |
| Botpress, ManyChat, custom bots | Noted | Step 1 platform table |

## Compliance

| Topic | Status | Where |
|-------|--------|-------|
| Privacy Protection Law Amendment 13 obligations | Covered | Privacy and Consent |
| Pseudonymization of user_id before analytics | Covered | Privacy and Consent |
| Transcript retention windows | Covered | Privacy and Consent |
| Anti-spam opt-in regime for marketing sends | Covered, hedged | Anti-spam compliance section |

## Out of scope (explicit)

Re-litigate every one of these on the next update.

| Topic | Why out of scope | Re-open when |
|-------|------------------|--------------|
| Building the chatbot itself | Separate skill (hebrew-chatbot-builder) | Never; routing note is correct |
| Training or fine-tuning Hebrew NLP models | Separate skill (hebrew-nlp-toolkit) | Never; routing note is correct |
| Voice bot analytics (ASR word error rate, barge-in, turn latency) | Not covered at all | A user asks about Hebrew voice bots; Rasa Pro and Conversational Agents both ship voice, so this gap is closing |
| LLM and RAG bot observability: groundedness, hallucination rate, LLM-as-judge evals, tracing, cost per conversation, tool-call success rate | Deferred, see optimization-log.json | Next cycle. This is the largest known gap and is already logged as the top deferred item |
| Statistical test implementation (sequential testing, CUPED) | Skill points to Statsig / LaunchDarkly / GrowthBook instead of implementing | A user needs an in-process significance calculation and cannot adopt a platform |
| Per-country WhatsApp rate cards | Meta does not publish Israel rates publicly | Meta publishes per-country rates, or a BSP publishes a citable Israel rate |
| Multi-bot or portfolio-level analytics | Single-bot scope by design | A user runs several bots and needs cross-bot comparison |
