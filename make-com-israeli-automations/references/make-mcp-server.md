# Make.com MCP Server Reference

Make.com runs a hosted MCP server that lets AI agents (Claude Code, Cursor, GitHub Copilot, and other MCP clients) call your Make scenarios as tools. This turns an Israeli business automation you have already built (a Morning invoice creator, a bimonthly VAT summary, an iCount expense logger) into a tool an agent can invoke directly.

Consult this file when wiring an Israeli automation scenario into an agent via the Make MCP server.

## Connection methods

| Method | Endpoint | Notes |
|---|---|---|
| OAuth (default) | `https://mcp.make.com` | Consent flow picks the organization and scopes. Nothing to store. |
| MCP token | `https://<MAKE_ZONE>/mcp/u/<MCP_TOKEN>` | Generate the token in Make profile, API access tab, Add token. `<MAKE_ZONE>` is your hosting zone (e.g. `eu1.make.com`, `eu2.make.com`, `us1.make.com`). |

Claude Code configuration (OAuth):

```json
{
  "mcpServers": {
    "make": { "type": "http", "url": "https://mcp.make.com" }
  }
}
```

Claude Code configuration (MCP token):

```json
{
  "mcpServers": {
    "make": { "type": "http", "url": "https://<MAKE_ZONE>/mcp/u/<MCP_TOKEN>" }
  }
}
```

Treat MCP tokens as secrets. Never commit them to version control.

## Scopes

| Scope | What it allows | Plans |
|---|---|---|
| Scenario run ("Run your scenarios" / token `mcp:use`) | View and run active on-demand scenarios | All plans |
| Management | View and modify scenarios, connections, webhooks, data stores | Paid plans only |

## Making a scenario appear as a tool

For an Israeli automation scenario to show up as an MCP tool:

1. Set the scenario to **active** status.
2. Set scheduling to **on-demand** (not scheduled, not instant-trigger).
3. Select the appropriate scope (`mcp:use` for tokens, "Run your scenarios" for OAuth).
4. Configure **scenario inputs**, which become the tool parameters (e.g. `client_name`, `amount`, `vat_period`).
5. Configure **scenario outputs**, which become the tool return values.
6. Write a detailed **scenario description**. Hebrew descriptions work, but the description is what the agent reads to decide when to call the tool, so make it specific.

A scenario that satisfies only one of conditions 1 and 2 will never appear in the tool list, regardless of how its inputs and outputs are configured.

## Israeli use cases

| Scenario exposed as a tool | What the agent can do |
|---|---|
| Create Morning document | Create a tax invoice or receipt on request, with the allocation-number check enforced inside the scenario |
| Bimonthly VAT summary | Pull the current period's VAT totals on demand |
| iCount expense logger | Log a Hebrew expense description to iCount |
| WhatsApp Hebrew notification | Send a templated Hebrew message to a customer |

## Timeouts

Scenario-run tools time out at 25s on OAuth and 40s on token transports. Israeli billing scenarios that aggregate a full VAT period can exceed this. When a run times out, the response includes an `executionId`, and the scenario keeps running in Make for up to 40 minutes. Poll for the result with `executions_get` using that ID. For long scenarios, switch from `https://mcp.make.com` to a zone-specific URL (`https://<MAKE_ZONE>/mcp/<TRANSPORT>`) to get the longer token timeouts.

## Worked example: expose a Morning invoice scenario as an MCP tool

User says: "I have a Make.com scenario that creates Morning invoices. Make it callable from Claude Code."

1. Open the scenario in Make.com and set it to active status with on-demand scheduling.
2. Define scenario inputs: `client_name`, `amount`, `document_type` (these become the tool parameters).
3. Define scenario outputs: `document_id`, `document_url` (these become the tool return values).
4. Write a detailed scenario description in the scenario settings so the agent knows when to call it.
5. Connect Claude Code to the Make MCP server: add `{"mcpServers":{"make":{"type":"http","url":"https://mcp.make.com"}}}` and complete the OAuth consent, selecting the "Run your scenarios" scope.
6. The scenario now appears as a tool, and the agent can create Morning invoices on request.

Result: Claude Code invokes the Morning invoice scenario directly as an MCP tool, with the scenario's built-in allocation-number check still enforced server-side.

## Reference Links

| Source | URL | What to Check |
|---|---|---|
| Make MCP server docs | https://developers.make.com/mcp-server | Endpoint URLs, auth methods, scopes, scenario-as-tool requirements |
