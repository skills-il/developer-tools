# n8n Workflow Authoring: Platform Choice, JSON Shape, Credentials

Companion to `SKILL.md` Steps 8-10.

## When to Use n8n vs Alternatives

| Criteria | n8n | Make.com | Zapier |
|----------|-----|----------|--------|
| Self-hosting (data residency) | Yes (Docker) | No | No |
| Israeli API nodes | None built-in, use HTTP/Code | Some community | Very few |
| Workflow limit | Unlimited (self-hosted) | Plan-based | Plan-based |
| Code execution | Full JS/Python | Limited JS | Limited |
| AI Agent nodes | 70+ AI, MCP support | AI features | AI features |
| Hebrew UI | No | Partial | No |

Choose n8n for Israeli data residency, unlimited automations, or full code access for Israeli API quirks (Hebrew encoding, phone formatting, VAT, allocation numbers).

## Workflow JSON Import/Export

n8n workflows are JSON documents. Agents building them programmatically need the shape:

```json
{
  "name": "Morning daily reconciliation",
  "nodes": [{
    "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 6 * * 0-4" }] } },
    "name": "Schedule Trigger", "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2, "position": [240, 300]
  }],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get Token", "type": "main", "index": 0 }]] }
  }
}
```

- **`nodes`**: each has unique `name` (used as connection key), `type` (e.g. `n8n-nodes-base.httpRequest`), `typeVersion` (must match a version n8n supports), `parameters`, and `position`.
- **`connections`**: keyed by source node name, mapping `main` output to an array of arrays of `{ node, type, index }` targets (double array allows multiple outputs, e.g. IF branches).
- Export via `GET /api/v1/workflows/{id}`, import via `POST /api/v1/workflows`. After importing into n8n 2.0 you must **publish** before it runs.

## Credentials Setup for Israeli APIs

n8n stores secrets in its encrypted credential store, never inline in workflow JSON:

- **Morning (Green Invoice) JWT**: no native credential. Chain HTTP Request nodes; the first calls `/account/token`, later nodes send `Authorization: Bearer {{token}}` via Header Auth or an expression. Token expires after 60 minutes, so refresh per execution.
- **Israeli SMS gateways (019, InforUMobile)**: Header Auth credential, name `Authorization`, value `Bearer <token>`.
- **Payment gateways (Cardcom, Tranzila, Grow)**: store merchant IDs / API keys as Generic Credential, referenced via `{{$credentials.fieldName}}`. Grow's `multipart/form-data` requests still pull secrets from the credential.
- For self-hosted n8n, set a stable `N8N_ENCRYPTION_KEY` so the credential store survives restarts.



---

# n8n AI Agent Nodes for Israeli Workflows

n8n 2.x ships native LangChain integration (the "Advanced AI" node group): 70+ AI nodes including Tools Agent, Conversational Agent, Memory (Window/Summary Buffer), Vector Store nodes (Pinecone, Qdrant, Supabase pgvector for RAG), and Model nodes for OpenAI, Anthropic and local models via Ollama.

**Do not hardcode a model name from a tutorial.** The current Anthropic Chat Model node resolves its model list dynamically from the Anthropic API at runtime rather than from a fixed dropdown, so the list moves without an n8n release. Pick by requirement, then take whatever the node offers today:

| Use case | How to choose | Why |
|----------|---------------|-----|
| Hebrew transaction categorization | Current mid-tier frontier model (the node's own default is the newest Sonnet) | Strong Hebrew at low cost; the task is classification, not reasoning |
| Hebrew document summarization | Current top-tier model | Long Hebrew legal text rewards reasoning depth |
| Real-time Hebrew chat | Lowest-latency model in the same family | Short Hebrew turns are latency-bound, not quality-bound |
| On-prem / data residency | Ollama with a multilingual local model on an Israeli VPS | PII stays in Israel; acceptable for categorization |

**RAG with Israeli content:** Connect a Vector Store node (Pinecone, Qdrant, Supabase pgvector) to an AI Agent. Use a multilingual embedding model that handles Hebrew (Cohere `embed-multilingual-v3.0` or OpenAI `text-embedding-3-large`); `text-embedding-ada-002` is weak on Hebrew.

**Example: AI bank transaction categorizer.** Schedule -> Code (bank scraper) -> AI Agent (categorize) -> Google Sheets:

```javascript
return $input.all().map(item => ({ json: {
  date: item.json.date, description: item.json.description, amount: item.json.chargedAmount,
  prompt: `Categorize this Israeli bank transaction. Transaction: "${item.json.description}" for ${item.json.chargedAmount} NIS on ${item.json.date}.
Categories: הכנסות, שכר, ספקים, מע"מ, ביטוח לאומי, שכירות, הוצאות משרד, אחר.
Respond with ONLY the Hebrew category name.`
}}));
```

## n8n MCP nodes

- **MCP Client Tool** (`@n8n/n8n-nodes-langchain.mcpClientTool`): attach as a sub-node so an AI Agent can call tools on an external MCP server (e.g. agentskills.co.il's `hebcal`, `israeli-bank`, `data-gov-il` servers).
- **MCP Server Trigger** (`@n8n/n8n-nodes-langchain.mcpTrigger`): exposes an n8n workflow itself as an MCP tool, so external clients (Claude Desktop, Cursor, Windsurf, custom GPTs) can discover and invoke your Morning-invoice-lookup or bank-scraper workflow. From typeVersion 2 it also offers n8n User Auth (OAuth2).

There is no `toolMcp` node. That name is a common hallucination and n8n rejects a workflow JSON that uses it.



---

# Troubleshooting (full detail, moved from SKILL.md)

## Troubleshooting detail

### Morning (Green Invoice) API returns 401 Unauthorized
JWT expired (60 min TTL). Add a token refresh step at the start of every execution. Store the token in `$getWorkflowStaticData('global')` with a timestamp and refresh if older than 55 min.

### Hebrew text appears garbled in CSV export
Missing UTF-8 BOM, so Excel reads it as ANSI. Prepend `'﻿'` to CSV content, or set Spreadsheet File encoding to UTF-8-BOM.

### Webhook not receiving Cardcom callbacks
Cardcom needs the callback URL publicly accessible with valid SSL. Use nginx/Caddy + Let's Encrypt. Ensure `WEBHOOK_URL` matches the public URL. Whitelist n8n's IP in the Cardcom dashboard.

### Schedule Trigger runs during Shabbat despite Hebcal check
Server timezone is UTC, not Asia/Jerusalem. Verify `GENERIC_TIMEZONE=Asia/Jerusalem`, restart n8n, and log `new Date().toString()` in a Code node to confirm.

### israeli-bank-scrapers fails in Code node
Three separate causes, in the order they bite:

1. `require()` is blocked. Set `NODE_FUNCTION_ALLOW_EXTERNAL=israeli-bank-scrapers` **on the task runner** (n8n 2.0 enables runners by default, and the variable has no effect on the main container in that setup).
2. Credentials come back undefined. `$env` is blocked inside Code nodes in 2.x (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`). Pull them from the credential store instead.
3. Wrong credential keys. The key is `password`, not `userPassword`, and the first field is per-bank (`userCode` for Hapoalim). See the login-fields table in Step 2.

Also install the package and its Puppeteer/Playwright dependency in the runner image, and give the container >= 1GB memory for Chromium. Execute Command (legacy approach) is disabled by default in 2.0.

### Cloudflare blocks bank scraper for Amex/Isracard
Switch to the maintained fork: `npm install @sergienko4/israeli-bank-scrapers` (uses Camoufox).


---

# בחירת פלטפורמה, מבנה JSON ו-credentials (הועבר מ-SKILL.md שלבים 8-10)

## שלב 8: מתי להשתמש ב-n8n לעומת חלופות

| קריטריון | n8n | Make.com | Zapier |
|----------|-----|----------|--------|
| אירוח עצמי (מיקום נתונים) | כן (Docker, כל ענן) | לא (SaaS בלבד) | לא (SaaS בלבד) |
| צמתי API ישראליים | אין מובנים, HTTP/Code | קצת מהקהילה | מעט מאוד |
| מגבלת תהליכים | ללא הגבלה (אירוח עצמי) | לפי תוכנית | לפי תוכנית |
| הרצת קוד | Code nodes מלאים (JS/Python) | JS מוגבל | מוגבל |
| צמתי AI Agent | 70+ צמתי AI, תמיכה ב-MCP | יכולות AI | יכולות AI |
| מחיר (אירוח עצמי) | חינם (קוד פתוח) | לא רלוונטי | לא רלוונטי |
| ממשק בעברית | לא (אנגלית בלבד) | חלקי | לא |
| מתאים ל | מפתחים שצריכים שליטה מלאה, מיקום נתונים, אוטומציות ללא הגבלה | משתמשים לא טכניים שרוצים בונה ויזואלי | אינטגרציות פשוטות, משתמשים לא טכניים |

בחרו n8n כש: צריכים אירוח עצמי למיקום נתוני ישראל, אוטומציות ללא הגבלה, גישה מלאה לקוד לטיפול ב-API ישראליים (קידוד עברית, פורמט טלפונים, חישובי מע"מ), או יכולות AI Agent עם הקשר ישראלי.

## שלב 9: ייבוא וייצוא של workflow כ-JSON

תהליכי n8n הם מסמכי JSON. סוכנים שבונים תהליכים בצורה פרוגרמטית (במקום ללחוץ בממשק) חייבים להבין את המבנה:

```json
{
  "name": "Morning daily reconciliation",
  "nodes": [
    {
      "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 6 * * 0-4" }] } },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [240, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Get Token", "type": "main", "index": 0 }]] }
  }
}
```

מבנה עיקרי:
- **`nodes`**: מערך של אובייקטי צמתים. לכל אחד `name` (ייחודי, משמש כמפתח חיבור), `type` (למשל `n8n-nodes-base.httpRequest`), `typeVersion` (חייב להתאים לגרסה ש-n8n תומך בה, אחרת הייבוא נכשל), `parameters` (הגדרות הצומת) ו-`position` (קואורדינטות `[x, y]`).
- **`connections`**: אובייקט שממופתח לפי `name` של צומת המקור, וממפה פלט (`main`) למערך של מערכים של יעדים `{ node, type, index }`. המערך הכפול מאפשר פלטים מרובים (למשל ענפי צומת IF).
- ייצוא דרך הממשק ("Download") או `GET /api/v1/workflows/{id}`; ייבוא דרך "Import from File" או `POST /api/v1/workflows`. אחרי ייבוא ל-n8n 2.0 חובה לפרסם את התהליך לפני שהוא רץ. ערכי `typeVersion` משתנים בין גרסאות, לכן בנו JSON מול גרסת n8n ידועה.

## שלב 10: הגדרת credentials ל-API ישראליים

n8n שומר סודות ב-credential store מוצפן, לעולם לא בתוך ה-workflow JSON:

- **JWT של Morning (חשבונית ירוקה)**: אין credential מובנה. משרשרים HTTP Request nodes, הראשון קורא ל-`/account/token` עם ה-API key וה-secret, הצמתים הבאים שולחים `Authorization: Bearer {{token}}` דרך **Header Auth** או ביטוי. הטוקן פג אחרי 60 דקות, אז מרעננים בכל הרצה במקום לשמור אותו לטווח ארוך.
- **שערי SMS ישראליים (019, InforUMobile)**: יוצרים credential מסוג **Header Auth**, שם `Authorization`, ערך `Bearer <token>`, ומצרפים ל-HTTP Request node.
- **שערי תשלום (Cardcom, Tranzila, Grow)**: שומרים מזהי סוחר / מפתחות API כערכי **Generic Credential** שמופנים דרך `{{$credentials.fieldName}}`. בקשות ה-`multipart/form-data` של Grow עדיין שולפות סודות מה-credential, לא מגוף הצומת.
- באירוח עצמי, הגדירו `N8N_ENCRYPTION_KEY` יציב כדי שה-credential store יישאר ניתן לפענוח בין הפעלות מחדש.



---

# צמתי AI Agent לתהליכים ישראליים (הועבר מ-SKILL.md שלב 7)

## שלב 7: צמתי AI Agent של n8n לתהליכים ישראליים

n8n 2.x מגיע עם אינטגרציית LangChain מובנית (קבוצת הצמתים "Advanced AI"). מעל 70 צמתי AI: Tools Agent, Conversational Agent, צמתי זיכרון (Window Buffer, Summary Buffer), צמתי Vector Store ל-RAG (Pinecone, Qdrant, Supabase pgvector), וצמתי Model עבור OpenAI, Anthropic ומודלים מקומיים דרך Ollama.

**אל תקבעו שם מודל קשיח מתוך מדריך כלשהו.** צומת Anthropic Chat Model הנוכחי מושך את רשימת המודלים שלו מה-API של Anthropic בזמן ריצה ולא מרשימה נעולה, ולכן הרשימה זזה בלי גרסה חדשה של n8n. בחרו לפי הדרישה, וקחו את מה שהצומת מציע היום:

**בחירת מודל לתוכן ישראלי:**

| שימוש | מודל מומלץ | למה |
|-------|-----------|------|
| סיווג תנועות בעברית | מודל frontier מדרג הביניים (ברירת המחדל של הצומת היא ה-Sonnet החדש ביותר) | עברית טובה בעלות נמוכה; המשימה היא סיווג ולא הסקה |
| סיכום מסמכים עברית (PDF ארוכים) | המודל החזק ביותר הזמין | טקסט משפטי עברי ארוך מרוויח מעומק הסקה |
| צ'אט עברית בזמן אמת | המודל בעל הלטנסי הנמוך ביותר באותה משפחה | תורות עברית קצרות תחומות בלטנסי ולא באיכות |
| On-prem / מיקום נתונים בארץ | Ollama (Llama 3.1, Qwen 2.5) על VPS ישראלי | שומר PII בארץ; העברית של Llama 3.1 סבירה לסיווג, חלשה ליצירה |

**RAG על תוכן ישראלי (צמתי Vector Store):** מחברים צומת Vector Store (Pinecone, Qdrant או Supabase pgvector) ל-AI Agent כדי לבצע retrieval על קורפוסים בעברית (היסטוריית חשבוניות, PDF של חוקי מס, יומני צ'אט לקוחות). השתמשו במודל embedding רב-לשוני שמטפל בעברית (Cohere `embed-multilingual-v3.0` או OpenAI `text-embedding-3-large`); ברירת המחדל `text-embedding-ada-002` חלשה בעברית לעומת שפות בכתב לטיני.

**דוגמה: סיווג אוטומטי של תנועות בנק עם AI**

ארכיטקטורה: Schedule Trigger -> Code (סריקת בנק) -> AI Agent (סיווג) -> Google Sheets

```javascript
// Code node: הכנת תנועות לסיווג AI
const transactions = $input.all().map(item => ({
  json: {
    date: item.json.date,
    description: item.json.description,
    amount: item.json.chargedAmount,
    prompt: `סווג את תנועת הבנק הישראלית הזו למטרות הנהלת חשבונות.
תנועה: "${item.json.description}" על סך ${item.json.chargedAmount} ש"ח בתאריך ${item.json.date}.
קטגוריות: הכנסות, שכר, ספקים, מע"מ, ביטוח לאומי, שכירות, הוצאות משרד, אחר.
השב עם שם הקטגוריה בלבד.`
  }
}));
return transactions;
```

מחברים את הפלט של ה-Code node ל-AI Agent node (Tools Agent) שמוגדר עם ה-LLM המועדף. הסוכן מסווג כל תנועה לפי התיאור העברי וקטגוריות ההוצאות הישראליות המוכרות.

**אינטגרציית MCP ב-n8n (שני צמתים):** n8n 2.x מגיע עם שני צמתי MCP מובנים:

- **MCP Client Tool** (`@n8n/n8n-nodes-langchain.mcpClientTool`): מתחבר כצומת משנה ל-AI Agent כך שהסוכן יקרא לכלים שחשופים בשרת MCP חיצוני. שימושי לחיבור שרתי MCP מ-agentskills.co.il כמו `hebcal`, `israeli-bank` או `data-gov-il` לסוכנים שלכם.
- **MCP Server Trigger**: חושף תהליך n8n כשלעצמו ככלי MCP. לקוחות AI חיצוניים (Claude Desktop, Cursor, Windsurf, GPT מותאמים) יכולים לגלות ולהפעיל את התהליך כאילו הוא כלי native. שימושי לעטיפת תהליך חיפוש חשבוניות Morning או סורק בנק כך שכל עוזר AI במשרד יוכל להפעיל אותו לפי דרישה.

ביחד הצמתים האלה הופכים את n8n גם למארח כלים וגם לצרכן כלים בסטאק סוכני מבוסס MCP.



---

# פתרון בעיות (פירוט מלא, הועבר מ-SKILL.md)

## פתרון בעיות

## שגיאה: "Morning API מחזיר 401 Unauthorized"
סיבה: ה-JWT token פג תוקף. לטוקנים של Morning יש TTL של 60 דקות.
פתרון: הוספת שלב רענון טוקן בתחילת כל הרצת תהליך. שמירת הטוקן ב-static data של n8n (`$getWorkflowStaticData('global')`) עם חותמת זמן, ורענון אם עבר יותר מ-55 דקות.

## שגיאה: "טקסט עברי מופיע משובש בייצוא CSV"
סיבה: ה-CSV חסר BOM (Byte Order Mark) של UTF-8, אז Excel מפרש אותו כ-ANSI.
פתרון: ב-Code node שמכין נתוני CSV, מוסיפים BOM בתחילה: `'\uFEFF' + csvContent`. לחלופין, מגדירים את אפשרות ה-encoding של Spreadsheet File node ל-UTF-8-BOM.

## שגיאה: "Webhook לא מקבל callbacks מ-Cardcom"
סיבה: Cardcom דורש שה-callback URL יהיה נגיש מהאינטרנט עם תעודת SSL תקינה. n8n באירוח עצמי מאחורי firewall לא יקבל callbacks.
פתרון: שימוש ב-reverse proxy (nginx, Caddy) עם SSL של Let's Encrypt. וידוא שמשתנה הסביבה `WEBHOOK_URL` תואם ל-URL הציבורי. הוספת ה-IP של n8n לרשימה המורשית בלוח הבקרה של Cardcom.

## שגיאה: "Schedule Trigger רץ בשבת למרות בדיקת Hebcal"
סיבה: אזור הזמן של שרת n8n מוגדר ל-UTC במקום Asia/Jerusalem, כך שהשוואת זמני שבת מוסטת ב-2-3 שעות.
פתרון: וידוא `GENERIC_TIMEZONE=Asia/Jerusalem` במשתני הסביבה של n8n. הפעלה מחדש של n8n אחרי שינוי הגדרות אזור זמן. בדיקה על ידי הדפסת `new Date().toString()` ב-Code node.

## שגיאה: "israeli-bank-scrapers נכשל ב-Code node"
סיבה: ב-n8n 2.0, Code nodes רצים ב-task runner מבודד. חבילת `israeli-bank-scrapers` והתלויות שלה (Puppeteer/Playwright) עשויות לא להיות זמינות ב-sandbox.
פתרון: התקנת `israeli-bank-scrapers` כחבילת npm שנגישה ל-task runner של n8n. וידוא שה-Docker container של n8n מקצה מספיק זיכרון (לפחות 1GB) ל-Chromium.

## שגיאה: "Cloudflare חוסם סורק בנקים עבור אמקס/ישראכרט"
סיבה: מתחילת 2026, Cloudflare חוסם דפדפנים headless באתרים פיננסיים ישראליים מסוימים.
פתרון: מעבר לפורק המתוחזק `@sergienko4/israeli-bank-scrapers` שמשתמש ב-Camoufox לעקיפת חסימת Cloudflare. התקנה: `npm install @sergienko4/israeli-bank-scrapers`.
