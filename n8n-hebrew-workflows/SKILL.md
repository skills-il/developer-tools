---
name: n8n-hebrew-workflows
description: Build n8n 2.x automation workflows (stable 2.36) with Israeli API integrations including Morning (Green Invoice), EZCount, israeli-bank-scrapers, data.gov.il, SMS gateways, Cardcom v11, Tranzila v2, Grow by Meshulam. Use when user asks to "create n8n workflow for Israeli business", "connect Morning to n8n", "automate hashbonit", "Shabbat-aware schedule trigger", "n8n AI agent", or integrate Israeli payment gateways. Covers Hebrew data handling, NIS formatting, Hebcal scheduling, n8n 2.x security patches (CVE-2026-44789 chain), AI Agent nodes with LangChain + RAG, MCP Client Tool and MCP Server Trigger, Israel Invoice Reform 2026 (allocation numbers, 5,000 NIS threshold from June 2026). Do NOT use for invoice management outside an n8n workflow (use green-invoice-il), general n8n tutorials without Israeli context, or Hebrew NLP (use hebrew-nlp-toolkit).
license: MIT
allowed-tools: Bash(n8n:*) Bash(curl:*) Bash(node:*) Bash(npx:*) Bash(docker:*)
compatibility: Requires n8n 2.32.1 or later (patches the CVE-2026-44789/44790/44791 chain); current stable 2.36.7. Node.js 22.22.2+ for israeli-bank-scrapers. Docker recommended for self-hosting. Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Gemini CLI.
---

# n8n Hebrew Workflows

## Instructions

### Step 1: Identify the Automation Pattern

Scheduled flows start with a Schedule Trigger and MUST add the Shabbat/holiday gate (Step 4). Event-driven flows (payment confirmations, form submissions) start with a Webhook trigger. Add a Code node early when Hebrew text needs encoding or RTL handling (Step 3), and an AI Agent node for categorization or summarization (Step 7). Field references for every Israeli service named here are in `references/israeli-api-endpoints.md`.

### Step 2: Connect Israeli APIs in n8n

#### Morning (formerly Green Invoice) API

Morning ("hashbonit yeruka" / חשבונית ירוקה) uses API key + secret to obtain a JWT token (NOT OAuth2). Configure HTTP Request:

```
POST https://api.greeninvoice.co.il/api/v1/account/token
Body: { "id": "{{$env.GREEN_INVOICE_API_KEY}}", "secret": "{{$env.GREEN_INVOICE_API_SECRET}}" }
```

The response carries a JWT valid for 60 minutes; pass it on as `Authorization: Bearer {{$json.token}}`.

**Israel Invoice Reform 2026 (threshold step-down):** Tax invoices over the threshold require an allocation number (mispar haktza'a) from the Tax Authority. The threshold drops mid-year:

| Effective | Threshold |
|-----------|-----------|
| Jan 1, 2026 | 10,000 NIS |
| **Jun 1, 2026 onwards** | **5,000 NIS** |

The regime began May 2024 (25,000 NIS), then 20,000 from January 2025, so a workflow touching historical invoices must test each one against the threshold in force on ITS OWN date. Full schedule in `references/israeli-api-endpoints.md`.

**Two separate rules govern this, and conflating them is the classic error.** The SELLER's duty is s.47(א2)(1), arising only on the buyer's demand and not on a zero-rated transaction: "ובעסקה שסכומה, בלא המס, עולה על הסכום האמור בסעיף 38(א1), חייב הוא לעשות כן לפי דרישת הקונה; הוראות סעיף קטן זה יחולו לעניין חשבונית מס שהוצאה בשל עסקה שהמס שחל לגביה אינו בשיעור אפס". The BUYER's loss of the input-VAT deduction is s.38(א1), with NO buyer-request condition: "לא יותר ניכוי מס התשומות הכלול בחשבונית מס שסכומה, בלא המס, עולה על 5,000 שקלים חדשים (מינואר 2026 ועד מאי 2026: 10,000 שקלים חדשים) ושאינה כוללת מספר שהקצה לה המנהל". So never treat "the buyer never asked" as a pass. Note `עולה על` (EXCEEDS): an invoice exactly on 5,000 is outside the rule, so use `>`, not `>=`.

**The threshold is measured BEFORE VAT.** Compare it against Morning's `amount` field, NOT `totalAmount`. At 18% VAT the two differ by a 900 NIS band around the 5,000 NIS line, so comparing the wrong field misclassifies invoices in that range.

Build the threshold as a configurable variable, not a hardcoded number. **Amounts are decimal shekels, not agorot:** `price: 50` means 50 NIS.

Creating and delivering a document is ONE call: no endpoint emails an existing document, so delivery is a property of creation, via `emailContent` and `attachment` on `POST /api/v1/documents`. **Morning's API reference is a JS-only app returning HTTP 200 for every path, so the exact body shape is not verified in this skill.** Do not invent field names or assume they match EZCount's: read `https://www.greeninvoice.co.il/api-docs` in a browser first, and treat a document created without an allocation number as needing human intervention, not a retry.

Common Morning endpoints:

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/api/v1/documents/search` | POST | Search invoices by date range, client, status |
| `/api/v1/documents` | POST | Create new invoice/receipt |
| `/api/v1/clients/search` | POST | Look up client by name or osek number |
| `/api/v1/documents/payments/search` | POST | Fetch payment records for reconciliation |
| `/api/v1/businesses/me` | GET | Get current business info |

Document type codes: 10 (price quote), 305 (tax invoice), 320 (tax invoice + receipt), 330 (credit note), 400 (receipt). Full endpoint details and response schemas are in `references/israeli-api-endpoints.md`.

#### EZCount (EasyCount) API

EZCount is a common Morning alternative. REST + JSON, authenticated with `api_key` + `api_email` in the body (not Bearer, not OAuth).

```
POST https://api.ezcount.co.il/api/createDoc
Body: { "api_key": "...", "api_email": "...", "developer_email": "you@example.com",
        "type": 320, "customer_name": "שם הלקוח", "customer_email": "client@example.com",
        "item": [{ "details": "שירותי ייעוץ", "amount": 1, "price": 500, "vat_type": "INC" }] }
```

Document type codes match the Tax Authority numbering used by Morning (305/320/330/400). Amounts are decimal shekels; `vat_type` is `PRE` (price before VAT) by default, `INC` for VAT-inclusive.

**The EZCount allocation hold is an HTTP 417, not a retryable field.** Their docs: "When the document is waiting for the Tax Authority allocation number we will return status `417`." There is no `allocation_status` field and retrying never clears it. On 417 the docs give four options: skip the allocation number, cancel the document, file a further objection, or reverse charge (re-issue at zero-rate VAT so the buyer self-invoices). Branch on the 417, surface the Tax Authority message, and let a human choose, since three of the four have tax consequences. Rate limit: 250 requests per 10 seconds, sequential not parallel.

EZCount and Morning produce the same legal output; pick by whichever suite the user already runs.

#### israeli-bank-scrapers via Code Node

`israeli-bank-scrapers` is a Node.js **library, not a CLI**, so it runs inside a Code node via `createScraper()`. Requires Node.js >= 22.22.2. Three things gate it, in the order they bite: `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` **on the task runner** so `require()` resolves; a working secret route (see the note below, "use the credential store" does not work from a Code node); and the correct per-bank credential keys. The key is `password`, never `userPassword`, and the first field differs per bank (`userCode` for Hapoalim, `username` for Leumi/Mizrahi/Max, `id` + `num` for Discount/Mercantile, `id` + `card6Digits` for Isracard/Amex). Read `SCRAPERS[companyId].loginFields` rather than assuming a shape.

**The secret route needs a deliberate choice, because "pull it from the credential store" is not implementable inside a Code node.** The Code node declares no credentials, so there is no `$credentials` there, and `$env` is separately blocked by default in 2.x. The three real options are: set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` on the task runner and keep `$env`; pass the secret in from a preceding credential-bearing node, accepting that it lands in execution data; or use external secrets on enterprise.

**Cloudflare blocking (2026):** bot detection blocks headless browsers on Amex and Isracard. The maintained fork `@sergienko4/israeli-bank-scrapers` works around it with Camoufox.

**Consider whether scraping is the right route at all.** This pattern stores the customer's live bank login so a headless browser can sign in as them, which sits badly against most Israeli bank terms on credential sharing. The licensed alternative under חוק שירות מידע פיננסי (Open Banking) exists and is the defensible path for anything client-facing. Working sample code, the full `CompanyTypes` list and the per-bank login-field table are in `references/israeli-api-endpoints.md`.

#### data.gov.il CKAN API

```
GET https://data.gov.il/api/3/action/datastore_search?resource_id=<guid>&q=<term>&limit=100
```

Useful resource IDs: Non-Profit Registry (`be5b7935-3922-45d4-9638-08871b17ec95`) for registered amutot; trade statistics by HS code (various IDs). The API returns Hebrew field names; use a Code node to normalize keys to English before downstream processing.

#### WhatsApp Business Cloud

n8n ships first-class nodes: **`n8n-nodes-base.whatsApp`** ("WhatsApp Business Cloud", typeVersion 1.1, credential `whatsAppApi`) for sending, and **`n8n-nodes-base.whatsAppTrigger`** for inbound. Operations: Send, Send Template, Send and Wait for Response.

Two Meta rules break these workflows. **The 24-hour customer service window:** a user messaging or calling you opens a 24-hour window in which free-form messages deliver; outside it only a pre-approved template will, and a scheduled workflow fires outside it by definition, so it must use Send Template. **Templates need prior approval** in one of three categories, Marketing, Utility or Authentication, so approve early. Pricing is per delivered message (conversation pricing ended July 1, 2025), so a fan-out loop costs per item.

#### Israeli SMS Gateways

| Gateway | Host | Auth | Best For |
|---------|------|------|----------|
| 019 Telzar | `019sms.co.il` | Bearer token, or username + password | Bulk marketing, transactional |
| InforUMobile | `capi.inforu.co.il` | Bearer token (IP allowlist enforced) | OTP, transactional |
| Nexmo/Vonage IL | `rest.nexmo.com` | API key + secret | International + local |

**019 returns HTTP 200 even when the send fails.** An auth failure comes back as `200 {"status":3,"message":"Username or password is incorrect..."}`, so a default HTTP Request node treats it as success and the workflow continues with no SMS delivered. Enable **Always Output Data** and branch on `$json.status` (0 = sent) with an IF node, never on the HTTP status code. InforUMobile additionally enforces an IP allowlist on top of the token, so whitelist your n8n egress IP there as well as at Cardcom and Tranzila.

Phone numbers must be international format `972XXXXXXXXX` (drop the leading 0), and normalization must VALIDATE rather than just reformat: an Israeli landline prefix (02/03/04/08/09, 072-077) and a 1-800 or *NNNN number cannot receive SMS at all, so a blind `0` to `972` swap silently mangles them. Request bodies, per-gateway field names and a normalizer that checks the prefix are in `references/israeli-api-endpoints.md`.

#### Three Israeli Rules That Gate the Whole Workflow

**1. Not every business may issue a tax invoice.** An עוסק פטור may not issue a חשבונית מס (305 / 320) and may not charge VAT at all; they issue a קבלה or חשבונית עסקה. Ask the VAT status before choosing a document type and never hardcode 305/320. Zero-rated cases (exports, services to a foreign resident) and the Eilat exemption also move the rate, so `vat_type` is a per-transaction decision. Numbering is sequential and immutable, a mistaken invoice is cancelled with a credit note (330) and never deleted, and the document is kept seven years, so persist the PDF rather than an expiring link.

**2. Automated commercial messaging is regulated.** s.30א of the Communications Law (תיקון 40) governs every SMS and WhatsApp send this skill can build. s.30א(ב) requires **explicit prior written consent** before you send at all. s.30א(י)(1) allows damages with no proof of damage of up to **1,000 NIS per message received in breach**, which is exactly the exposure of a bulk loop. Meta's 24-hour window is a platform rule, not the legal one, and clearing it does not clear consent.

The labelling requirement is channel-specific and routinely got wrong. The general rule, s.30א(ה)(1)(א), requires the word `פרסומת` at the START of the message. But s.30א(ה)(2) is an SMS carve-out: an advertisement sent by SMS states **only** the advertiser's name and the contact route for a refusal notice ("יציין בדבר הפרסומת רק את שמו ואת דרכי יצירת הקשר עמו לצורך מתן הודעת סירוב"). Do not bolt a `פרסומת` prefix onto an SMS template on the assumption that the general rule applies.

**3. The data these workflows touch is regulated personal data.** Teudat zehut from a payment callback, live bank credentials and transaction descriptions piped into a third-party LLM all fall under the Privacy Protection Law as amended (Amendment 13, in force August 2025). Minimise what you persist, treat the Google Sheet as a regulated database with a retention rule, and do not send identifiable customer data to a foreign model without a lawful basis.

### Step 3: Handle Hebrew Data in n8n Nodes

Code nodes process strings as UTF-8, so Hebrew works natively. Problems arise at boundaries: CSV exports need UTF-8-BOM or Excel reads them as ANSI, HTTP Request responses need an explicit UTF-8 response encoding, email bodies need `<div dir="rtl">`, data.gov.il returns Hebrew JSON keys that should be normalized in a Code node, and string length must use `Array.from(str).length` rather than `.length`. Legacy Israeli bank and accounting exports are often Windows-1255 rather than UTF-8, which BOM advice does not fix, and customer-supplied names can carry bidi control characters that visually reorder an amount on a rendered invoice.

Format currency with `Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' })`. Israeli documents use DD/MM/YYYY: Morning returns ISO 8601, but government datasets return DD/MM/YYYY strings, so parse explicitly rather than trusting `new Date(s)`. Parsing helpers, a Hebrew month map and a prefix-validating phone normalizer are in `references/israeli-api-endpoints.md`.

### Step 4: Shabbat-Aware Scheduling

Business workflows in Israel must not run during Shabbat (Friday sundown to Saturday sundown) and Jewish holidays. n8n's Schedule Trigger has no native support, so add a check node at the start of every scheduled workflow.

**Architecture:** Schedule Trigger -> HTTP Request (Hebcal) -> IF (is Shabbat?) -> Continue or Stop

```
GET https://www.hebcal.com/shabbat?cfg=json&geonameid=293397&M=on
```

`geonameid=293397` is Tel Aviv; Jerusalem is 281184, Haifa 294801, Beer Sheva 295530. Candle lighting is 40 minutes before sunset in Jerusalem, 30 in Haifa and Zikhron Ya'akov, 18 elsewhere, so the geonameid is load-bearing. Code node to gate the workflow:

```javascript
const now = new Date();
const items = $input.first().json?.items;
// FAIL CLOSED: if we cannot read the calendar we do not know, so we do not run.
if (!Array.isArray(items) || items.length === 0) return [];

// Pair each candle-lighting with the FIRST havdalah after it. Taking
// items.find('candles') and items.find('havdalah') is wrong: asked ON a chag,
// Hebcal returns that chag's havdalah BEFORE the next festival's candles, so
// the range test is unsatisfiable and the workflow runs on Yom Kippur.
const ev = items.filter(i => i.category === 'candles' || i.category === 'havdalah')
  .map(i => ({ cat: i.category, at: new Date(i.date) }))
  .sort((a, b) => a.at - b.at);

for (let k = 0; k < ev.length - 1; k++) {
  if (ev[k].cat === 'candles' && ev[k + 1].cat === 'havdalah'
      && now >= ev[k].at && now <= ev[k + 1].at) return [];
}
if (ev.length && ev[0].cat === 'havdalah' && now <= ev[0].at) return [];
return $input.all();
```

**Do not silently drop the work.** `return []` ends the branch, so an invoice or customer notification due during Shabbat is lost rather than delayed. For anything a customer is waiting on, queue the items (workflow static data or a table) and drain them from a separate post-havdalah workflow.

For Jewish holidays, query `https://www.hebcal.com/hebcal?v=1&cfg=json&year=now&month=x&maj=on&mod=on&i=on` and filter for `yomtov: true`. Both query parameters are load-bearing and both fail silently. `month=now` is not valid: it returns HTTP 200 with `"items": []`, so the gate never fires. Without `i=on` Hebcal serves the Diaspora calendar, 13 yomtov days for 2026 against Israel's 8, halting the business on five ordinary working days. A weekday-only cron does NOT remove the need for this gate: six of Israel's eight 2026 yomtov days fall Sunday to Thursday, Yom Kippur among them. `references/shabbat-cron-patterns.md` carries the corrected patterns, the Israel-local date handling erev chag needs, and the fast-day and chol-hamoed cases this gate ignores.

### Step 5: Israeli Payment Gateway Webhooks

Three gateways cover almost all Israeli card traffic, each delivering its callback differently. Full field tables, base paths and the Bit flow are in `references/israeli-api-endpoints.md`; what decides correctness is here.

| Gateway | Callback shape | Success test | Dedup key |
|---|---|---|---|
| Cardcom v11 | POST `LowProfileResult` to your `WebHookUrl` | **`ResponseCode == 0`** | `TranzactionId` |
| Tranzila | GET query parameters | `Response == '000'` | `index` |
| Grow by Meshulam | POST `multipart/form-data` (not JSON) | `webhookKey` matches your stored key, then re-read | `asmachta` |

**`ReturnValue` is not a Cardcom status field.** Cardcom's own v11 spec calls it "A string of data to save on the transaction, usually send your unique order Id, you will get it back in the WebHook URL". It is your pass-through, echoed back. Branching on it approves declined payments. There is no `DealResponse` field in v11 at all, and `InternalDealNumber` / `CardOwnerID` / `NumOfPayments` are legacy classic-API names absent from the result object, so a dedup key built on `InternalDealNumber` is always `undefined` and the duplicate-invoice guard never fires. The teudat zehut and installment count live under `TranzactionInfo` as `CardOwnerIdentityNumber` and `NumberOfPayments`.

**Never issue a document straight off the callback body.** The webhook URL is public and none of these three gateways signs its payload, so a forged POST with a plausible amount makes your workflow issue a real tax invoice and burn a real allocation number. Re-read the transaction server-side first (Cardcom by `TranzactionId`, Grow via `getPaymentProcessInfo`, Tranzila by `index`), confirm the amount, then issue. Grow additionally needs `approveTransaction` to finalize.

Bit is not a standalone API: it is reached through Tranzila v2 (`bit: true` on the payment page) or through Grow with Bit enabled, arriving in the same webhook flow with a different `transactionType`.

#### Webhook Authentication

n8n's Webhook node supports four auth modes: None, Basic Auth, Header Auth, JWT Auth. Given the 2026 unauthenticated-webhook CVE history, "None" on a publicly-routable webhook is effectively a vulnerability. But for the three Israeli gateways above, transport auth is not the real control: none of them signs its payload, so the server-side re-read is what actually protects you. n8n's JWT Auth does verify the signature and the `exp` claim, but not `iss` or `aud`. `references/webhook-auth-patterns.md` has the working snippets and the raw-body caveat that breaks naive HMAC checks.

**IP whitelisting:** Cardcom and Tranzila require your webhook IP to be whitelisted. Self-hosting means a static IP or a fixed-egress reverse proxy.

### Step 6: Self-Hosting Considerations

#### n8n 2.x Security Line and Version Pinning

n8n 2.0 shipped in December 2025; current stable is 2.36.7 as of August 2026. **Pin >= 2.32.1** and never `n8nio/n8n:latest`. Three CRITICAL vulnerabilities (CVE-2026-44789 HTTP Request node prototype pollution to RCE, CVE-2026-44790 Git node arbitrary file read, CVE-2026-44791 XML node patch bypass) were disclosed 2026-05-14 and fixed in 2.22.1; HIGH-severity credential-exfiltration and sandbox-escape fixes landed through 2.31.5 and 2.32.1. CVE-2026-44789 sits on this skill's critical path, since every Israeli integration here is an HTTP Request node, and every payment-gateway workflow adds a public Webhook node.

Two settings from the 2.0 breaking changes gate this skill's code, and with task runners on (the 2.0 default) both belong on the **runner**, not the main container:

```
NODE_FUNCTION_ALLOW_BUILTIN=crypto
NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers
```

`N8N_BLOCK_ENV_ACCESS_IN_NODE` also defaults to `true` in 2.x, so `$env.*` inside a Code node silently returns nothing. The credential store is NOT the answer here, because the Code node declares no credentials; pick one of the three routes in Step 2.

**n8n 3.0 lands October 2026** and removes self-hosted npm installs (Docker only), the Function / Function Item / Item Lists nodes, the `$getPairedItem` helper, and AI Agent node v1 with all its legacy agent modes. Build Step 7 on the current Tools Agent.

See `references/n8n-version-migration.md` for the full CVE history, the 2.0 breaking-change table, the Execute Command re-enable path, the complete 3.0 list, and Israeli data-residency hosting options.

#### Self-Hosting Settings That Matter in Israel

Set **both** `GENERIC_TIMEZONE=Asia/Jerusalem` and `TZ=Asia/Jerusalem`. Without them Schedule Trigger nodes run on UTC and Shabbat calculations drift 2-3 hours; Israeli DST runs from the Friday before the last Sunday of March to the last Sunday of October. Set a stable `N8N_ENCRYPTION_KEY` so the credential store survives restarts, pin the image tag, and put the Code-node module variables on the task-runner service. A ready Compose file and the Israeli data-residency hosting table are in `references/n8n-version-migration.md`.

### Step 7: n8n AI Agent Nodes for Israeli Workflows

n8n 2.x ships native LangChain integration (the "Advanced AI" node group): Tools Agent, memory nodes, Vector Store nodes (Pinecone, Qdrant, Supabase pgvector) for RAG, and Model nodes for OpenAI, Anthropic and local models via Ollama. Build on the **Tools Agent**: n8n 3.0 removes AI Agent node v1 along with the SQL, Conversational, OpenAI Functions, Plan-and-Execute and ReAct modes.

**Do not hardcode a model name from a tutorial.** The current Anthropic Chat Model node resolves its model list from the Anthropic API at runtime rather than from a fixed dropdown, so the list moves without an n8n release. Choose by requirement (a mid-tier frontier model for Hebrew classification, the strongest available for long Hebrew legal text, the lowest-latency in the family for real-time chat, a local multilingual model on an Israeli VPS when PII must stay in Israel), then take what the node offers today. For RAG over Hebrew corpora use a multilingual embedding model (Cohere `embed-multilingual-v3.0` or OpenAI `text-embedding-3-large`); `text-embedding-ada-002` is weak on Hebrew. Note that piping customer transaction descriptions into a foreign model is a privacy decision, not just a quality one.

**n8n MCP nodes.** The MCP Client Tool (`@n8n/n8n-nodes-langchain.mcpClientTool`) attaches as a sub-node so an AI Agent can call tools on an external MCP server, for example agentskills.co.il's `hebcal`, `israeli-bank` and `data-gov-il` servers. The MCP Server Trigger (`@n8n/n8n-nodes-langchain.mcpTrigger`) exposes an n8n workflow itself as an MCP tool for Claude Desktop, Cursor or Windsurf to invoke; from typeVersion 2 it also offers n8n User Auth (OAuth2). There is no `toolMcp` node: that name is a common hallucination and n8n rejects a workflow JSON using it. A worked Hebrew transaction-categorizer example is in `references/n8n-workflow-authoring.md`.

### Step 8: Platform Choice, Workflow JSON, and Credentials

Choose n8n over Make.com or Zapier when you need self-hosting for Israeli data residency, unlimited automations, or full code access for Israeli API quirks. None of the three ships built-in Israeli API nodes, so the work is HTTP Request and Code nodes either way; n8n is the only one you can host in an Israeli region.

Workflows are JSON: a `nodes` array (each with a unique `name` used as the connection key, a `type` such as `n8n-nodes-base.httpRequest`, a `typeVersion`, `parameters` and `position`) and a `connections` object keyed by source node name. Import via `POST /api/v1/workflows`, then **publish** before it runs. Pin the CURRENT `typeVersion` for each node rather than copying an old number from a tutorial; the Schedule Trigger, for example, is on 1.4 while most samples still show 1.2.

Secrets live in n8n's encrypted credential store, never inline in workflow JSON, with one exception that matters here: the Code node has no credentials, so bank and HMAC secrets need one of the routes described in Step 2. Morning has no native credential either, so chain an HTTP Request to `/account/token` and pass `Authorization: Bearer {{token}}` onward, refreshing per execution since the JWT expires after 60 minutes.

`references/n8n-workflow-authoring.md` has the full comparison table, a complete workflow JSON sample, and the per-service credential setup.

## Examples

### Example 1: Morning invoice reconciliation, weekday mornings

"Every morning, pull yesterday's Morning invoices and flag any still unpaid."

Schedule Trigger on `0 9 * * 0-4` (09:00 Israel time, since `GENERIC_TIMEZONE` is set) into the Step 4 holiday gate, since six of 2026's eight yomtov days fall inside that cron. Then HTTP Request to `/api/v1/account/token` for the JWT, HTTP Request to `/api/v1/documents/search` with `Authorization: Bearer {{$json.token}}` filtering `fromDate`/`toDate` to yesterday and `type` to 305/320, an IF node branching on payment status, and an SMS or Send Email node with the Hebrew body wrapped in `<div dir="rtl">`.

### Example 2: Bank transactions to a Google Sheet, holiday-aware

"Scrape my business account nightly and append new transactions to a sheet, but skip Shabbat and holidays."

Schedule Trigger, then the Hebcal request and the paired-scan gate from Step 4 (fail closed), then a Code node running `israeli-bank-scrapers` via `createScraper()` with a real secret route, then a Code node normalizing Hebrew descriptions and DD/MM/YYYY dates, then Google Sheets Append. Add a separate Error Trigger workflow, because an unattended scrape that throws simply stops with no notification.

## Recommended MCP Servers

- **hebcal**: Hebrew/Jewish calendar and Shabbat times, alternative to calling Hebcal HTTP in every workflow.
- **israeli-bank**: Israeli bank account data; lets an agent pull transactions without running `israeli-bank-scrapers` in a Code node.
- **data-gov-il**: Israeli government open data (CKAN), query registries without hand-building HTTP Request nodes.

## Reference Links

| Source | URL |
|--------|-----|
| n8n Documentation | https://docs.n8n.io/ |
| n8n 2.0 Breaking Changes | https://docs.n8n.io/changelog/v20-breaking-changes |
| n8n Enable Modules in Code Node | https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-modules-in-code-node |
| n8n Block Access to Nodes | https://docs.n8n.io/hosting/securing/blocking-nodes/ |
| Morning (Green Invoice) API | https://www.greeninvoice.co.il/api-docs |
| Hebcal API | https://www.hebcal.com/home/developer-apis |
| data.gov.il CKAN API | https://data.gov.il/api/3/action/help_show?name=datastore_search_sql |

## Gotchas

- **Agents pin `:latest` or a stale 2.1x/2.2x tag.** 2.21.4 alone carries 68 published advisories, three of them CRITICAL (the CVE-2026-44789/44790/44791 chain, fixed in 2.22.1), plus HIGH-severity credential-exfiltration fixes through 2.32.1. Any public Webhook node widens the exposure. Pin >= 2.32.1; current stable is 2.36.7.
- **Agents write `@n8n/n8n-nodes-langchain.toolMcp` for the MCP Client Tool.** No such node exists. The types are `mcpClientTool` and `mcpTrigger`.
- **Agents send a free-form WhatsApp message from a scheduled workflow.** Meta's 24-hour customer service window has closed by then, so only an approved template delivers. Use Send Template, and get the template approved before the workflow ships.
- **Agents retry an EZCount 417 as if it were a transient error.** 417 means the Tax Authority has not allocated a number; retrying never clears it. There is no `allocation_status` field. Branch on the 417 and surface the four documented options.
- **Agents read secrets with `$env` inside Code nodes.** Blocked by default in 2.x, so the read silently yields nothing and the node fails on an undefined value. But the credential store is not the fix (the Code node has none); pick one of the three routes in Step 2.
- **Agents call `require()` in a Code node without allowlisting the module.** `require('crypto')` needs `NODE_FUNCTION_ALLOW_BUILTIN=crypto`; `require('israeli-bank-scrapers')` needs `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers`. With task runners on (the 2.0 default) both go on the runner, not the main container.
- **Agents default to UTC for schedule triggers.** Israel uses `Asia/Jerusalem`; DST runs from the Friday before the last Sunday of March to the last Sunday of October. Set `GENERIC_TIMEZONE` and re-verify after each DST change.
- **Agents assume VAT is included.** Israeli invoices often show amounts before VAT (lifnei maam). Morning returns both `amount` (before VAT) and `totalAmount` (with VAT). Current VAT is 18% (2026).
- **Agents hardcode one candle-lighting time.** It varies by city (Jerusalem 40 min before sunset, Haifa and Zikhron Ya'akov 30, Tel Aviv and elsewhere 18), so a fixed time runs during Shabbat somewhere.
- **Agents branch a Cardcom webhook on `ReturnValue`.** It is your own order id echoed back, not a status. Use `ResponseCode == 0`, and dedup on `TranzactionId`, not the non-existent `InternalDealNumber`.
- **Agents build the Shabbat gate with `items.find('candles')` and `items.find('havdalah')`.** Asked on a chag, Hebcal returns that chag's havdalah BEFORE the next festival's candles, so the range test can never be true and the workflow runs on Yom Kippur. Pair each candles with the next havdalah, and fail closed when the calendar is unreadable.
- **Agents tell the user to put Code-node secrets in the credential store.** The Code node has no credentials. Unblock `$env` on the runner, or pass the secret in from a preceding node.
- **Agents issue an invoice directly from a payment webhook body.** The URL is public and none of the Israeli gateways signs its payload. Re-read the transaction server-side first.
- **Agents hardcode document type 305/320.** An osek patur may not issue a tax invoice or charge VAT at all. Ask the VAT status first.
- **Agents build an SMS or WhatsApp fan-out with no consent check or opt-out.** תיקון 40 לחוק התקשורת carries statutory damages up to 1,000 NIS per message with no proof of damage.
- **Invoice Reform 2026 threshold drops June 1, 2026.** Invoices over the threshold (10K NIS through May 31, 5K NIS from June 1) created via API require allocation numbers. Measured **before VAT**, so compare against Morning's `amount`, not `totalAmount`. Make it a workflow variable. The statute says `עולה על` (exceeds), so use `>`, not `>=`, and never gate on whether the buyer asked: s.38(א1) blocks the buyer's deduction regardless.
- **Agents build the Hebcal holiday gate with `month=now` and no `i=on`.** `month=now` returns an empty `items` array with HTTP 200, so the gate never fires; omitting `i=on` returns the Diaspora calendar (13 yomtov days for 2026 against Israel's 8). Use `month=x&i=on`.
- **Agents trust the HTTP status from Israeli SMS gateways.** 019 returns HTTP 200 with `status: 3` on auth failure. Branch on the body field, not the status code.
- **Agents assume one webhook equals one payment.** All three gateways retry. Deduplicate on `TranzactionId` / `index` / `asmachta` before creating a document, or a retry issues a duplicate invoice and burns a second allocation number.
- **n8n editor keyboard shortcuts break under Hebrew layout.** The canvas reads `e.key` rather than `e.code`, so `Ctrl+C` yields `e.key = 'ב'`. Switch to English input while editing. n8n issue #12569.
- **n8n's expression editor has no RTL support.** Hebrew renders left-to-right. Store long Hebrew literals in static workflow data and reference them by name.
- **Unattended workflows fail silently without an Error Trigger.** A scheduled scrape that throws just stops. Add a separate Error Trigger workflow that alerts. Enable per-node Retry On Fail for transient failures, but never on the Shabbat gate: a retry that eventually returns empty data must fail closed.

## Bundled Resources

### References
- `references/israeli-api-endpoints.md` -- Israeli API endpoint reference (Morning, data.gov.il, SMS gateways, payment gateways, Hebcal).
- `references/shabbat-cron-patterns.md` -- Pre-built Shabbat-aware scheduling patterns with Hebcal integration.
- `references/webhook-auth-patterns.md` -- HMAC signature verification + JWT claim validation Code-node snippets.
- `references/n8n-version-migration.md` -- full CVE history, the 2.0 breaking-change table, the complete 3.0 removal list, Israeli hosting options.
- `references/n8n-workflow-authoring.md` -- platform choice, workflow JSON shape, credential setup, AI-agent detail, extended troubleshooting.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Morning API returns 401 | JWT expired (60 min TTL) | Refresh the token at the start of every execution; cache it in `$getWorkflowStaticData('global')` with a timestamp and refresh past 55 min |
| Hebrew garbled in CSV export | Missing UTF-8 BOM, so Excel reads ANSI | Set Spreadsheet File encoding to UTF-8-BOM |
| Cardcom callbacks never arrive | URL not publicly reachable, or IP not whitelisted | Public HTTPS with valid SSL, `WEBHOOK_URL` matching the public host, n8n's IP whitelisted in the Cardcom dashboard |
| Schedule Trigger runs during Shabbat | Server timezone is UTC, or the gate paired the wrong candles/havdalah (see Step 4) | Set `GENERIC_TIMEZONE` and `TZ`, then log `new Date().toString()` in a Code node to confirm; use the paired-scan gate |
| israeli-bank-scrapers fails in a Code node | `require()` blocked, secrets undefined, or wrong per-bank credential keys | Set `NODE_FUNCTION_ALLOW_EXTERNAL` **on the task runner**, pick a working secret route (Step 2), and read `SCRAPERS[companyId].loginFields` |
| Cloudflare blocks Amex/Isracard scraping | Bot detection on headless browsers | Use the maintained `@sergienko4/israeli-bank-scrapers` fork (Camoufox) |

Longer diagnoses, including the runner-image dependencies and memory floor for Chromium, are in `references/n8n-workflow-authoring.md`.
