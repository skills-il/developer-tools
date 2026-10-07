# Domain checklist: Make.com scenarios for Israeli business processes

Independent coverage checklist, researched 2026-10-07 from vendor and government sources. It was written without reading the skill, so it can be used to audit the skill for gaps. Each item names the source that makes it core. Figures marked "verify" could not be confirmed against a primary page during this research pass.

## Must cover (core)

### Make platform fundamentals

1. **Credits as the billing unit.** Credits replaced "operations" as the billing term (pricing unchanged). Most modules cost 1 credit per operation; AI modules use dynamic, token-based credit usage and some AI extractor modules cost 2 to 10 credits per operation. Credits and operations are separate metrics: credits track spending, operations count what ran. Source: help.make.com/credits.
2. **Per-plan allotments and plan limits.** Free: 1,000 credits/month, 15-minute minimum schedule interval, 5-minute max execution, 2 active scenarios. Core / Pro / Teams start at 10,000 credits/month, 1-minute minimum interval, 40-minute max execution, unlimited active scenarios. Monthly credits expire at the end of the term; annual plans keep them 12 months. Source: make.com/en/pricing.
3. **Execution time limit.** A scenario running past 40 minutes (5 on Free) fails with ExecutionInterruptedError. Long jobs must be split, chunked, or chained. Source: make.com/en/pricing, Make community and help center on ExecutionInterruptedError.
4. **Webhook (Custom webhook) limits.** Queue size is 667 items per 10,000 licensed credits, up to a 10,000-item maximum per webhook; a full queue rejects new data. Throughput is 300 incoming requests per 10 seconds, after which Make returns 429. A webhook not attached to any scenario for more than 5 days (120 hours) is deactivated automatically and then returns 410 Gone. Source: help.make.com/webhooks.
5. **Webhook response and processing order.** Default responses are 200 (accepted), 400 (queue full), 429 (rate limit). The Webhook response module customises the reply, but placing it mid-scenario can hide downstream errors. Instant webhooks run in parallel by default; enable "Process data in order" when sequence matters (for example payment then refund). Source: help.make.com/webhooks.
6. **Error handlers.** The five handlers and their semantics: Skip ("disregard errors and allow the scenario to process subsequent bundles", formerly labelled Ignore), Retry (stores an incomplete execution and retries, formerly Break), Resume (substitute output and continue), Commit (stop and keep changes), Rollback (stop and revert). The skill must show which handler fits a payment webhook (never Skip a failed invoice creation silently). Source: help.make.com/error-handlers.
7. **Incomplete executions.** Disabled by default; must be switched on in scenario settings ("Store incomplete executions"). Stored count is capped by the organization's usage allowance. Can be retried automatically, resolved manually, or deleted. Source: help.make.com/incomplete-executions.
8. **If-else / Merge versus Router.** If-else runs only the first branch whose condition is true and Merge rejoins the branches into one flow; a Router runs every matching route and its routes cannot be rejoined. If-else and Merge consume operations but no credits. Found under Flow Control, Conditionals. Source: help.make.com release note "If-else and Merge".
9. **Data Store as state and idempotency store.** Use a Data Store keyed on the external transaction ID (Cardcom / Grow / Tranzila deal ID, Morning document ID) to deduplicate retried webhooks and to map IDs across systems. Storage scales with the plan (1 MB per 1,000 credits, 1 MB minimum per store; Free gets 1 MB). Every Data Store needs a data structure. Source: help.make.com data stores and data structures pages (verify exact per-record cap).
10. **Organization time zone.** Schedules and date functions run in the organization's time zone; only owners and admins can change it. For Israeli businesses it must be Asia/Jerusalem, which also handles the Israeli DST switch. Source: help.make.com/manage-time-zones.
11. **Connections and secrets.** Use app connections or keychains rather than pasting API keys into HTTP module fields; HTTP module "Make a request" for vendors without an app. Source: help.make.com HTTP app and connections pages.

### Israeli accounting and tax

12. **Israel Invoices (חשבוניות ישראל) allocation number (מספר הקצאה).** Threshold schedule: 10,000 NIS from 2026-01-01, **5,000 NIS from 2026-06-01**, measured **before VAT**. Without an allocation number the buyer cannot deduct input VAT on that invoice. Applies to tax invoices issued to an osek murshe who will deduct input VAT. The scenario must request the number (via the invoicing platform's SHAAM integration) and store it, and must not treat a missing number as a soft warning. Source: gov.il service "בקשה למספר הקצאה לחשבונית מס" (gov.il/he/service/request-assignment-number-for-tax-invoice; the page returned 403 to automated fetch, so confirm wording manually), Tax Authority publications on the threshold schedule.
13. **Morning (Green Invoice) API.** OAuth 2.0 client-credentials auth (POST to `https://api.morning.co/idp/v1/oauth/token`, 1-hour JWT access token; each environment has its own keys), production base `https://api.greeninvoice.co.il/api/v1` and a separate sandbox, document type codes (300 transaction invoice / חשבון עסקה, 305 tax invoice, 320 tax invoice-receipt, 400 receipt, 330 credit invoice), and the `document/created` webhook. The Make "Morning" app is community-built and community-maintained, so the HTTP module fallback must be documented. Source: greeninvoice.co.il help center (webhook-document-created), Green Invoice API docs, make.com/en/integrations/morning.
14. **iCount.** Native Make app with about 20 modules (18 actions, 2 searches) across documents, clients, expenses, inventory, CRM, time punches; anything else via iCount API v3 and the HTTP module. Source: make.com/en/integrations/icount, iCount API documentation.
15. **VAT reporting periods (monthly vs bimonthly) and mikdamot.** Each osek murshe is assigned a monthly or bimonthly VAT period by the Tax Authority, while income tax advances (מקדמות) are monthly by law, bimonthly only when the advance booklet approves it for a low-turnover business. 2026 deadlines: periodic VAT report and mikdamot by the 15th, withholding (ניכויים) by the 16th, detailed VAT report (דוח מפורט, PCN874) by the 23rd; a deadline falling on Friday, Saturday or Sunday (the Tax Authority treats each as a weekly rest day for these deadlines) moves to the following Monday, and holidays or one-off extensions can push it later, so use the published calendar. Scenarios that bucket invoices or send reminders must read the period from the business's profile rather than hardcode one. Source: Tax Authority 2026 reporting calendar (as republished by efraty.com and capitax.co.il; confirm on gov.il), VAT Law. The VAT threshold separating monthly from bimonthly filers is 1,775,000 NIS for 2026 and 1,805,000 NIS from 1 January 2027 (kolzchut).

### Israeli payment gateways

16. **Cardcom.** Low Profile (hosted page / iframe) flow, the server-to-server callback sent to the `WebHookUrl` passed in each v11 `LowProfile/Create` request (a required field, not a dashboard setting), and confirming the transaction by querying the result endpoint rather than trusting the browser redirect. API v11 docs at secure.cardcom.solutions/Api/v11/Docs. Source: Cardcom API v11 documentation.
17. **Grow (formerly Meshulam).** `notifyUrl` on createPaymentProcess triggers a server-to-server callback; the receiver **must** call `approveTransaction` to acknowledge it. Sandbox at sandbox.meshulam.co.il. Source: developers.grow.business (server-to-server callback, approve-transaction).
18. **Tranzila.** Hosted iframe flow, notify URL callback, API V2 with HMAC-SHA256 auth headers. Source: Tranzila developer docs (verify notify parameter name).
19. **Bit.** Bit is accepted through gateways (Cardcom, Grow, Tranzila and others) rather than as a standalone webhook source for most small businesses; the scenario consumes the gateway's callback and reads the payment-method field. Source: gateway docs listing Bit as a payment method (verify per gateway).
20. **Webhook verification and idempotency for payments.** Re-query the gateway or verify a signature before issuing an invoice, dedupe on transaction ID in a Data Store, and enable "Process data in order". Source: combination of items 5, 9 and the gateway docs above.

### Work management, messaging, ERP

21. **monday.com API-Version header.** Send `API-Version` explicitly (since October 1st, 2026 `2026-10` is current, `2026-07` maintenance and `2027-01` the release candidate; the page's summary header lagged the schedule table after the roll, so read the table). Without the header the current version applies and quarterly releases can break a scenario. Lifecycle: RC 3 months, Current 3 months, Maintenance 6 months. Source: developer.monday.com/api-reference/docs/api-versioning.
22. **monday.com complexity budget and rate limits.** Max 5M complexity points per query; personal API tokens share a combined 10M points per minute (1M on trial, NGO and free accounts); 429 with Retry-After when exhausted. Source: developer.monday.com/api-reference/docs/rate-limits.
23. **monday.com Make app.** Watch Events, Execute a GraphQL Query, column-value modules; Version 1 of the Make monday app is legacy with maintenance ended, so build on Version 2. Source: apps.make.com/monday.
24. **WhatsApp Business Cloud API pricing and the 24-hour window.** Per-message pricing since 2025-07-01 by template category (marketing, utility, authentication); non-template (free-form) messages are free but only inside the 24-hour customer service window opened by the user's last message; utility templates are free inside an open window; outside the window only approved templates may be sent. Click-to-WhatsApp ads open a 72-hour free entry point window. Israel (+972) is a standalone rate-card market. Source: developers.facebook.com WhatsApp pricing documentation.
25. **WhatsApp webhooks.** Verification handshake (hub.challenge with verify token) and message / status webhooks on a Make custom webhook, plus template pre-approval in Hebrew. Source: Meta WhatsApp Cloud API webhooks docs.
26. **Priority ERP REST (OData) API.** OData entity endpoints, Basic auth or Personal Access Token (v19.1+, username = token, password = literal `PAT`), `$filter`/`$expand`, batch, and `$since` for incremental sync. Source: prioritysoftware.github.io REST API docs.
27. **Israeli SMS gateways and the anti-spam law.** HTTP-module integration with Israeli SMS providers (Unicode for Hebrew, alphanumeric sender ID), and Communications Law section 30A: marketing messages require prior consent, a "פרסומת" label, and a working opt-out; transactional messages are distinct. Source: Communications (Telecommunications and Broadcasting) Law section 30A, provider API docs.

### Israeli calendar

28. **Shabbat- and holiday-aware scheduling.** Make's weekly schedule can exclude Saturday but not sunset-to-nightfall windows or Jewish holidays; use a filter or If-else that checks candle-lighting / havdalah times from the Hebcal API (or a Data Store calendar) before sending customer messages, and remember the Israeli workweek is Sunday to Thursday (Friday partial). Source: help.make.com scheduling + time zone pages; Hebcal Shabbat/holiday API documentation.

### AI

29. **Make AI Agents.** Make AI Agent (New) app: available on all plans with Make's AI provider (custom provider connections on paid plans), tools = modules, scenarios (via Call a scenario) and MCP tools, knowledge files for static context, selectable reasoning effort (higher costs more tokens and credits), Reasoning tab for step logs. Source: help.make.com/make-ai-agent-new-app, help.make.com/beta-make-ai-agents.
30. **Make MCP server.** Cloud server at `https://mcp.make.com` (OAuth) or `https://<zone>/mcp/u/<MCP_TOKEN>` / `https://<zone>/mcp` with Bearer token. Only active, on-demand scenarios with defined inputs and outputs are exposed as tools; scenario-run tools on all plans, management tools on paid plans only. Tool-call timeouts: scenario runs 25 s (OAuth) / 40 s (token), management 30 s / 60 s; the scenario keeps running up to 40 minutes and results are fetched by `executionId` (needs `scenarios:read`). Transport: stateless Streamable HTTP. Source: developers.make.com/mcp-server/make-mcp-server.

## Should cover (advanced)

1. **Make API rate limits per plan and Make API usage** for building and deploying scenarios programmatically (scenario blueprints and the scenario-run endpoint). Source: developers.make.com API reference (verify per-plan numbers).
2. **Custom apps on the Make Developer Hub** for an Israeli service with no Make app (connection, base, RPCs, webhooks). Source: developers.make.com custom apps docs.
3. **Scheduled vs instant webhook processing** and "maximum number of results" for batching high-volume gateways. Source: help.make.com/webhooks.
4. **Iterators, aggregators and array functions** for invoice line items, multi-item monday boards and batched SHAAM requests. Source: help.make.com iterator/aggregator pages.
5. **Hebrew text handling**: UTF-8 everywhere, percent-encoding Hebrew in query strings, RTL in WhatsApp templates and PDFs, phone normalisation 05X to +9725X. Source: Meta template guidelines, vendor API docs.
6. **Agreed amounts and currency**: agorot rounding, foreign currency invoices with Bank of Israel representative rate. Source: Bank of Israel exchange-rate API, Green Invoice API currency fields.
7. **Credit notes and refunds flow** (330 credit invoice in Morning, refund webhooks from gateways) and whether a credit invoice needs its own allocation number. Source: Green Invoice docs, Tax Authority Israel Invoices FAQ (verify).
8. **Custom variables and team templates** (Pro / Teams) for reusing VAT rate, allocation threshold and business IDs across scenarios. Source: make.com/en/pricing.
9. **Monitoring**: execution history, full-text log search (Pro+), notification emails on errors, and the scenario auto-deactivation after repeated failures. Source: help.make.com scenario settings (verify the consecutive-error rule).
10. **VAT rate as data, not a constant** (18% since 2025-01-01) so a future rate change is one edit. Source: Tax Authority VAT rate announcement.
11. **MCP management tools security**: least-privilege scopes, separate tokens per client, never exposing management tools to a customer-facing agent. Source: developers.make.com MCP server docs.
12. **monday.com webhooks via Make** (Watch Events) versus polling, and the monday webhook challenge response. Source: developer.monday.com webhooks docs.
13. **Priority ERP form-level permissions and API licensing** (API user must have the forms opened for REST). Source: Priority REST API docs.
14. **Privacy**: Israeli Privacy Protection Law Amendment 13 (in force August 2025) when a scenario copies customer PII between systems and into Data Stores; retention and deletion. Source: Privacy Protection Law, Privacy Protection Authority guidance.

## Out of scope (explicit)

- Full payroll computation (tax brackets, credit points, Bituach Leumi, pension) and payslip generation.
- Computing a VAT return or PCN874 file, or giving tax advice; the skill only routes data and reminds on deadlines.
- Accountant-level decisions on whether an expense is deductible or whether an invoice is fictitious.
- n8n, Zapier, Power Automate, Pipedream, and self-hosted automation engines.
- Building payment pages or handling raw card data (PCI DSS scope); the skill only consumes gateway callbacks.
- Writing Make custom apps in depth beyond pointing to the Developer Hub.
- WhatsApp unofficial / WhatsApp Web automation (whatsmeow, browser bots), which violate Meta terms.
- Bulk marketing SMS or WhatsApp campaigns without consent.
- ERP implementation or customisation of Priority forms and procedures.
- Hebrew calendar computation itself (rely on Hebcal rather than reimplementing).
- Non-Israeli invoicing regimes (EU e-invoicing, US sales tax).

## Authoritative sources

- Make credits: help.make.com/credits
- Make pricing and plan limits: www.make.com/en/pricing
- Make webhooks: help.make.com/webhooks
- Make error handlers: help.make.com/error-handlers
- Make incomplete executions: help.make.com/incomplete-executions
- Make If-else and Merge release note: help.make.com/new-feature-if-else-and-merge
- Make data stores: help.make.com/data-stores
- Make time zones: help.make.com/manage-time-zones
- Make AI Agent (New) app: help.make.com/make-ai-agent-new-app
- Make AI Agents overview: help.make.com/beta-make-ai-agents
- Make MCP server: developers.make.com/mcp-server/make-mcp-server
- Make API run scenario: developers.make.com/api-documentation/api-reference/scenarios/post--scenarios--scenarioid--run
- Make monday.com app: apps.make.com/monday
- Make Morning integration: www.make.com/en/integrations/morning
- Make iCount integration: www.make.com/en/integrations/icount
- monday API versioning: developer.monday.com/api-reference/docs/api-versioning
- monday rate limits: developer.monday.com/api-reference/docs/rate-limits
- WhatsApp Business Platform pricing: developers.facebook.com/documentation/business-messaging/whatsapp/pricing
- Priority REST API: prioritysoftware.github.io/
- Grow server-to-server callback: developers.grow.business/reference/server-response
- Grow approve transaction: developers.grow.business/reference/approve-transaction
- Cardcom API v11: secure.cardcom.solutions/Api/v11/Docs
- Green Invoice webhook document/created: www.greeninvoice.co.il/help-center/webhook-document-created
- gov.il allocation number service: www.gov.il/he/service/request-assignment-number-for-tax-invoice
- 2026 Tax Authority reporting calendar (secondary republication): www.efraty.com/?p=5144
- Hebcal API: www.hebcal.com/home/developer-apis
