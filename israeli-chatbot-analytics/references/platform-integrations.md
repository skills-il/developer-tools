# Platform Log Ingestion

How to fold each vendor's conversation export into the standard `conversations`
shape defined in Step 1 of the skill. Every parser below produces the same schema,
so the Step 2-11 metrics run unchanged whichever platform the bot is on.

## Export method by platform

| Platform | Export Method | Format |
|----------|-------------|--------|
| Conversational Agents (formerly Dialogflow CX) | BigQuery export | One row per turn, session in `conversation_name`. Use the `he-il` language code on new agents; the language reference lists `iw` as `Hebrew (deprecated)` with reduced feature coverage (https://docs.cloud.google.com/dialogflow/cx/docs/reference/language). The Dialogflow CX console was deprecated on 2025-10-31 and users are routed to the Conversational Agents console; the API and doc paths still use `dialogflow/cx`. |
| Rasa Pro / CALM | Analytics dashboard + tracker events | Flow-step events (Rasa Pro with CALM is dialogue-driven, not intent-driven, so legacy intent-accuracy metrics map differently). |
| Rasa Open Source (legacy) | Tracker Store (SQL/Mongo) | Events list per conversation. Rasa Open Source is in maintenance mode (https://github.com/RasaHQ/rasa); legacy OSS docs at https://legacy-docs-oss.rasa.com/docs/rasa/. |
| Botpress | Conversation export / DB | JSON. We have not verified Hebrew support or RTL alignment in the default web webchat, so check message-bubble alignment in your own widget before reporting on it. |
| Custom bots | Application logs | Varies (normalize to schema above) |
| WhatsApp Cloud API | Webhook logs | Message objects with metadata. See the WhatsApp pricing notes in SKILL.md and `chatbot-metrics-glossary.md` for the per-message cost model. |
| ManyChat | Audience + flow exports | CSV/JSON. WhatsApp send-out costs flow through Meta's per-message tariff. |

## Conversational Agents (Dialogflow CX) BigQuery export

`parse_dialogflow_cx_logs(bigquery_rows)`:

- The export table (Google suggests `dialogflow_bigquery_export_data`) has one row
  per conversational turn with columns `project_id`, `agent_id`,
  `conversation_name`, `turn_position`, `request_time`, `language_code`, `request`
  (JSON), `response` (JSON), `partial_responses`, `derived_data`,
  `conversation_signals` and `bot_answer_feedback`. There is no `session_id` column.
- Export query:
  `SELECT * FROM your_dataset.dialogflow_bigquery_export_data WHERE DATE(request_time) BETWEEN @start AND @end ORDER BY conversation_name, turn_position`
- Group rows by `conversation_name` (the session resource name); use it as
  `session_id`. Take `started_at` / `ended_at` from the min/max `request_time`.
- The user text, the matched intent and its confidence live inside the `response`
  JSON, in the detect-intent response's `queryResult`: `text`, `match.intent.displayName`
  and `match.confidence`; the bot's reply is in `queryResult.responseMessages[].text.text`.
  Check the paths against one exported row before trusting them: a turn that was not
  typed text (an event, a DTMF digit) fills a different field than `text`.
- Sort each session's messages by `turn_position`. Set `language = "he"` and
  `outcome = "unknown"`; derive the real outcome downstream (Step 1).

Use the `he-il` language code on new agents. The language reference lists `iw` as
`Hebrew (deprecated)` with reduced feature coverage. The Dialogflow CX console
was deprecated on 2025-10-31, with users routed to the Conversational Agents console,
though API and documentation paths still use `dialogflow/cx`. Bare
`cloud.google.com/dialogflow/...` doc URLs now redirect to `docs.cloud.google.com`.

References: https://docs.cloud.google.com/dialogflow/cx/docs/reference/language and
https://docs.cloud.google.com/dialogflow/cx/docs/concept/export-bq (export schema)

## Rasa tracker store

Rasa Open Source is in maintenance mode; the intent-based analytics below apply to
existing Rasa OSS deployments. New Rasa builds use CALM (Conversational AI with
Language Models), which is dialogue-driven rather than intent-driven, so
intent-accuracy metrics do not map across. If your bot runs on CALM, measure it with
`references/llm-bot-observability.md` rather than with Step 5.

`parse_rasa_tracker_events(tracker_events)`:

- Query: `SELECT * FROM events WHERE sender_id = @sender_id ORDER BY timestamp`
- Iterate events. On `session_started`, flush the in-progress session and start a
  new one. On `user`, append a user message with `intent.name` and
  `intent.confidence` from `parse_data`. On `bot`, append a bot message with `text`.
  On `action` with `name == "action_human_handoff"`, set `outcome = "escalated"`.
  Flush the trailing session at the end.

Reference: https://legacy-docs-oss.rasa.com/docs/rasa/ (legacy OSS tracker-store
docs) and https://rasa.com/docs/learn/concepts/calm/ (CALM).

## Everything else

Botpress, ManyChat, WhatsApp Cloud API webhook logs and custom application logs
have no canonical export shape. A WhatsApp webhook stream has no session at all:
sort each user's messages by time and start a new session after the Step 1
inactivity timeout (the bundled script flags sessions that still contain a longer
gap, via `--session-timeout-minutes`). Normalize them by hand to the Step 1 schema; the
only fields the metrics actually require are `session_id`, `started_at`,
`ended_at`, `outcome`, and the per-message `sender` / `text` / `timestamp`
(plus `intent` and `intent_confidence` where the platform supplies them).
