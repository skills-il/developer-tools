# Experimentation and Analytics Stack Notes (2026)

Vendor-specific detail for the tooling around the skill. Facts here move faster than
the rest of the skill; re-check any pricing or ownership claim before you act on it.

## Experimentation platforms for Hebrew chatbots

When you outgrow `HebrewABTestManager` (in-process bucketing, in-memory results) and need sequential testing and CUPED variance reduction, the mainstream experimentation platforms all work for Hebrew chatbots; none of them care what language `variant_text` is in. Pick by team and infra fit:

| Platform | Best fit | Notes for Hebrew chatbot teams |
|----------|----------|--------------------------------|
| Statsig | Teams wanting flags + experiments + product analytics in one stack | Ownership moved twice: OpenAI acquired Statsig in September 2025, then on 5 May 2026 the brand, product and customer base transferred to Amplitude while the founding team stayed at OpenAI. Amplitude now maintains the platform, so confirm the current plan and roadmap before committing. |
| LaunchDarkly | Mature enterprise teams needing approvals, audit logs, RBAC | The "safe" enterprise choice; pair with your existing analytics for stats. Its plan structure and per-connection / per-MAU pricing have changed more than once; price it fresh from the vendor rather than from an older quote. |
| GrowthBook | Teams with a data warehouse (BigQuery, Snowflake, Postgres) who want stats run against their own data | Open source; does NOT collect event data, so Hebrew transcripts never leave your warehouse, useful for Amendment 13 data-residency posture. |

Plan on longer tests (2+ weeks, 200+ impressions per variant): Israeli user bases are smaller and the Sun-Thu work week makes 1-week tests unreliable.

## GA4 and Mixpanel notes

- **GA4 "AI Assistant" channel.** GA4 ships a built-in `Channel Group: AI Assistant` that tags qualifying traffic with Medium `ai-assistant` and a reserved `(ai-assistant)` campaign value. Google names ChatGPT, Gemini and Claude as examples and has **not** published the full recognized-referrer list, so do not assume any particular assistant (Perplexity included) is covered: check your own referral report before reporting on it. Traffic arriving with no referrer still lands in Direct, and the classification is not applied retroactively (https://www.searchenginejournal.com/google-analytics-adds-ai-assistant-as-default-channel-group/574974/).
- **Mixpanel Agent (formerly Spark) + MCP Server.** Spark, the AI query builder, is now **Mixpanel Agent** (https://docs.mixpanel.com/docs/mixpanel-agent); the old Spark doc page points there. Mixpanel also ships an MCP server (https://docs.mixpanel.com/docs/mcp) that lets Claude / ChatGPT / Cursor query your Mixpanel data conversationally. For Hebrew dashboards this matters because you can ask follow-up questions in Hebrew and the agent routes them to the right event or property, useful when the ops team is not fluent in the funnel-query UI. If the server does not appear for your project, check your organization's Mixpanel AI settings before concluding it is unavailable.
