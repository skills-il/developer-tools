# LLM and RAG Chatbot Observability

Steps 2-11 of the skill measure a **dialogue-managed** bot: a fixed intent or flow
graph, where "did it understand?" is answered by an intent label and "did it work?"
by a completion flag. An LLM-backed bot (a RAG assistant, a tool-calling agent, a
Dicta-LM or GPT wrapper over your knowledge base) breaks both assumptions. There is
no intent label to score, and a fluent wrong answer scores as a completed session.

This file is the measurement layer that sits on top of the session metrics, not a
replacement for them. Drop-off, escalation, CSAT, retention and the Hebrew handling
in Step 9 all still apply unchanged.

## What changes when the bot is an LLM

| Step-5/8 metric | Why it stops working | What replaces it |
|---|---|---|
| `intent_accuracy` | No classifier, no label | Answer correctness against a labelled question set |
| `fallback_rate` | The model never falls back; it answers anyway | Refusal rate + groundedness rate |
| `high_confidence_rate` | No calibrated confidence to read | Retrieval score distribution + citation coverage |
| `avg_handle_time_seconds` | Dominated by token generation, not user thinking | Time-to-first-token and total latency, tracked separately |
| Cost per conversation | Was zero-ish per turn | Real, variable, and the top operational risk |

## Fields to add to the conversation log schema

Extend the Step 1 schema with a per-assistant-message block. Nothing here is
Hebrew-specific; it is what makes the rest of this file computable.

```python
llm_turn = {
    "model": "dicta-il/DictaLM-3.0-1.7B-Instruct",  # or the vendor model id
    "temperature": 0.0,

    # Version keys. Step 1 carries a session-level bot_version, which is the
    # wrong granularity here: an LLM bot's prompt and its index change several
    # times a week, independently of each other and of the deploy. Without
    # these, a groundedness or cost regression cannot be attributed to
    # anything, and the alert rules at the end of this file fire with nothing
    # to point at.
    "prompt_version": "",           # or system_prompt_hash
    "retriever_version": "",
    "index_snapshot_id": "",
    "chunking_config": "",

    "prompt_tokens": 0,
    "cached_prompt_tokens": 0,      # see Cost, below; 0 is not the same as absent
    "cache_hit": False,
    "completion_tokens": 0,
    "cost_usd": 0.0,                # compute from the vendor rate card, do not guess
    "time_to_first_token_ms": 0,
    "total_latency_ms": 0,

    "rewritten_query": "",          # the query actually sent to the retriever
    "is_follow_up_turn": False,
    "retrieved_chunk_ids": [],      # RAG only; empty list means no retrieval ran
    "retrieval_scores": [],         # parallel to retrieved_chunk_ids
    "citations_emitted": [],        # chunk ids the answer actually cited
    "tool_calls": [],               # [{"name":..., "ok": bool, "latency_ms": int}]
    "refused": False,
    "refusal_justified": None,      # None until a human labels it; see Guardrails
    "safety_flags": [],
}
```

`retrieved_chunk_ids` vs `citations_emitted` is worth logging, but be precise about
what it measures, because it is easy to oversell. It is a **citation-compliance and
retrieval-hygiene canary**, not a hallucination measurement:

- It cannot see the dominant RAG failure, an answer that cites a chunk and then
  contradicts or over-extrapolates from it. Citation is not entailment.
- Retrieved 10, cited 1 is the healthy top-k case. That is retrieval precision.
  Define the number you actually track, and write the formula down: the useful
  one is the share of answers that asserted something factual while
  `citations_emitted` was empty, NOT `len(cited)/len(retrieved)`.
- Deciding "asserted something factual" needs a classifier or a judge, so the
  fully honest version is not judge-free. What IS judge-free is the raw
  empty-citation rate segmented by turn type, and its week-over-week movement.
- A prompt edit that breaks citation formatting spikes this metric with no
  change in hallucination at all. Check the prompt version before the retriever.

Use it to decide when to look. Do not report it as groundedness.

## The four metrics worth building first

1. **Groundedness**, measured on a sample by a judge or human as the share of
   answers whose every factual sentence maps to a retrieved chunk. Report this
   under the name "groundedness" and nothing else. Separately, and continuously,
   track the **empty-citation rate** (`len(citations_emitted) == 0`) as the cheap
   canary described above. Reporting the canary under the groundedness name is
   the same trap as reporting `high_confidence_rate` as `intent_accuracy` in
   Step 8, and it will be quoted to management the same way.
2. **Retrieval hit rate.** Share of turns where at least one retrieved chunk scored
   above your relevance floor. A collapsing hit rate on Hebrew queries is usually an
   embedding problem, not a model problem, and it precedes a CSAT drop by days.
3. **Tool-call success rate.** Share of `tool_calls` with `ok == True`, split by
   tool name. Broken tools present to the user as vague, evasive answers rather
   than as errors, so this never surfaces in completion rate.
4. **Cost per resolved conversation.** Total `cost_usd` over sessions with
   `outcome == "resolved"`. Cost per *session* flatters a bot that gives up early;
   cost per *resolved* session is the number that survives a budget review.

Track refusal rate alongside these. A rising refusal rate with flat CSAT usually
means a prompt change made the bot over-cautious, and users are silently leaving.

## Latency, and why the Step 10 rule does not transfer

`DEFAULT_ALERT_RULES` carries `slow_response` at p95 response time above 3,000 ms.
An LLM bot doing retrieval plus generation routinely exceeds that, so the rule
fires on day one, gets muted, and takes the real latency signal with it. Replace it:

- **Alert on p95 `time_to_first_token_ms`.** Once you stream, TTFT is what maps to
  perceived responsiveness. Under about a second reads as live; one to three
  seconds is tolerable behind a typing indicator.
- **Keep `total_latency_ms` as a verbosity and cost signal**, not a health one. It
  tracks answer length more than it tracks anything being wrong.
- If you do NOT stream, TTFT and total latency are the same number and the whole
  wait is dead air. Streaming is the cheapest perceived-latency fix available.

Set the actual thresholds from four weeks of your own data, as everywhere else here.

## Cost, and the lever the cost metric exists to pull

Naming cost the top operational risk is only useful if you also measure the main
mitigation. Two levers, both invisible unless you log for them:

- **Prompt caching.** A large stable Hebrew system prompt plus retrieved context is
  exactly the cacheable prefix, and it is usually the single largest saving
  available. `cached_prompt_tokens` and `cache_hit` in the schema above make cache
  hit rate computable. Without them, a prompt edit that reorders the prefix and
  silently destroys every cache hit shows up only as a cost line going up.
- **Semantic response caching** on repeated Hebrew FAQ queries. Measure hit rate
  and, separately, staleness complaints; a cache that serves a superseded answer
  is a correctness bug wearing a cost-saving hat.

Report **cost per resolved conversation** and **cache hit rate** side by side. Cost
per resolved conversation alone rewards a cache that returns fast wrong answers.

## Multi-turn retrieval

A collapsing retrieval hit rate on Hebrew queries is not always an embedding
problem, and reaching for a re-embedding of the corpus first is the expensive
mistake. In a multi-turn conversation the usual cause is an un-rewritten follow-up:
"וכמה זה עולה?" or "ומה לגבי עצמאי?" carries almost no retrievable content on its
own and will miss against any embedding model, however good.

The fix is query rewriting (condense the history into a standalone query) before
retrieval. The measurement is retrieval hit rate **split by `is_follow_up_turn`**.
If first-turn hit rate is healthy and follow-up hit rate is not, the bug is in
query construction, not in the index. Log `rewritten_query` so you can read what
the retriever actually saw rather than what the user typed.

## The offline evaluation set (build this before any of the above)

Everything above is online measurement: it tells you something regressed after
users hit it. The thing that stops a regression shipping is a frozen offline set
you run on every prompt edit, retriever swap, chunk-size change and model upgrade.

- **Size and shape.** 50-200 Hebrew items, each a question plus the expected
  answer plus the expected source chunk. Cover the real question mix, not the
  easy cases.
- **Build it from the data this skill already surfaces.** Your drop-off
  transcripts (Step 3) and escalated sessions (Step 2) are exactly the questions
  the bot handles worst, which is exactly what the set should contain. Sampling
  only resolved sessions produces a set that always passes.
- **Freeze it.** Editing the set after seeing a score is testing on the training
  data, and it makes week-over-week numbers incomparable. Version it, and when
  you must add cases, add them as a new version and re-baseline.
- **Gate on it.** Run it in CI on every prompt or index change, with a stated
  pass threshold, before deploy. A set you run manually after an incident is a
  post-mortem tool, not a regression gate.
- **Split it** the way Step 7 splits an A/B test: hold back roughly 30% you never
  tune against, or you will optimize the prompt to the set rather than to users.

## LLM-as-judge evaluation, and its limits

For answer quality with no ground-truth label, a judge model scoring
`(question, retrieved_context, answer)` on correctness, groundedness and helpfulness
is the standard approach. Three constraints specific to Hebrew bots:

- **Judge in Hebrew, on Hebrew.** A judge prompted in English scoring Hebrew answers
  drifts toward rewarding formal register over correctness. Prompt the judge in
  Hebrew and give it Hebrew few-shot examples.
- **Calibrate against humans before trusting it.** Have Hebrew-speaking annotators
  score 100 conversations, then measure judge-human agreement. Below rough agreement
  the judge is a random number generator with a decimal point, and it will be quoted
  to management as if it were accuracy. This is the same trap as `intent_accuracy`
  vs `high_confidence_rate` in Step 8.
- **A judge is a sampling instrument, not a monitor.** Run it on a weekly sample,
  not on every turn: on every turn it doubles your token bill and adds latency.
  Use the deterministic metrics above for alerting.

## Tracing

Per-turn traces (prompt, retrieved chunks, tool calls, response) are what let you
answer "why did it say that?" for a specific complaint. Any OpenTelemetry-compatible
tracing backend works; the GenAI semantic conventions define the span attribute names
for model, token counts and tool calls, so instrument to those rather than inventing
your own attribute keys and you can change backend later.

The GenAI conventions moved out of the main OpenTelemetry semconv site in 2026 and are
now maintained at https://github.com/open-telemetry/semantic-conventions-genai; the old
`opentelemetry.io/docs/specs/semconv/gen-ai/` pages carry a "moved" banner and are no
longer updated, so read the repository rather than the site.

## Privacy note

Traces and judge evaluations copy full conversation text into a second system.
Everything in the skill's Privacy and Consent section applies to that copy too:
pseudonymize `user_id` before it reaches the tracing backend, apply the same
retention window, and confirm where the tracing vendor stores and processes the
data before sending Hebrew transcripts to it.

## Guardrails: refusal rate is not enough

`refused` and `safety_flags` are declared in the schema above, and refusal rate on
its own cannot answer the question it exists to answer. Three splits matter,
particularly for bots handling Israeli health, finance and government content:

- **Justified vs false refusal.** An undifferentiated refusal rate cannot tell
  "we got safer" from "we got useless". Label a sample by hand (`refusal_justified`)
  the same way you label the eval set, and track the false-refusal rate.
- **Prompt-injection and jailbreak attempt rate.** This is a security KPI, not a
  quality one. It belongs on the alert list and on a different dashboard.
- **PII in output.** A RAG bot that surfaces another user's record from an
  under-filtered index is an Amendment 13 incident, not a quality regression.
  Scan outputs for ID numbers and other identifiers and alert on any hit, not on
  a rate. See the Privacy note above and the skill's Privacy and Consent section.

## Alert rules to add

Extend `DEFAULT_ALERT_RULES` (Step 10) with the LLM-specific ones:

| Rule | Metric | Trigger | Severity |
|---|---|---|---|
| `retrieval_miss_spike` | `retrieval_hit_rate` | `lt` your floor over 60 min | warning |
| `tool_failure_spike` | `tool_success_rate` | `lt` your floor over 30 min | critical |
| `cost_per_conversation_spike` | `cost_per_resolved_usd` | `gt` your budget line over 24 h | warning |
| `refusal_spike` | `refusal_rate` | `gt` your baseline over 60 min | warning |
| `slow_first_token` | p95 `time_to_first_token_ms` | `gt` your TTFT budget over 15 min | warning |
| `cache_hit_collapse` | `cache_hit_rate` | `lt` your baseline over 60 min | warning |
| `pii_in_output` | count of PII detections | `gt` 0, any window | critical |

Set each threshold from four weeks of your own data. The industry-benchmark caveat
in Step 2 applies with more force here: there is no published Hebrew baseline for
any of these.
