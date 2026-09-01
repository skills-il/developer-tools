# Platform Log Ingestion

How to fold each vendor's conversation export into the standard `conversations`
shape defined in Step 1 of the skill. Every parser below produces the same schema,
so the Step 2-11 metrics run unchanged whichever platform the bot is on.

## Conversational Agents (Dialogflow CX) BigQuery export

`parse_dialogflow_cx_logs(bigquery_rows)`:

- Export query:
  `SELECT * FROM project.dataset.dialogflow_cx_interactions WHERE DATE(request_time) BETWEEN @start AND @end`
- Group rows by `session_id`. For each session, track min/max `request_time` as
  `started_at` / `ended_at`.
- For each row append a user message (`text = query_text`, `intent = matched_intent`,
  `intent_confidence`) and/or a bot message (`text = response_text`).
- Sort each session's messages by `timestamp`. Set `language = "he"` and
  `outcome = "unknown"`; derive the real outcome from flow completion downstream.

Use the `he-il` language code on new agents. The language reference lists `iw` as
`Hebrew (deprecated)` with reduced feature coverage. The standalone Dialogflow CX
console was retired on 2025-10-31 and the product is now Conversational Agents,
though API and documentation paths still use `dialogflow/cx`. Bare
`cloud.google.com/dialogflow/...` doc URLs now redirect to `docs.cloud.google.com`.

Reference: https://docs.cloud.google.com/dialogflow/cx/docs/reference/language

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
have no canonical export shape. Normalize them by hand to the Step 1 schema; the
only fields the metrics actually require are `session_id`, `started_at`,
`ended_at`, `outcome`, and the per-message `sender` / `text` / `timestamp`
(plus `intent` and `intent_confidence` where the platform supplies them).
