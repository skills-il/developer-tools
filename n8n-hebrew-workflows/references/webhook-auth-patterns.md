# Webhook Authentication Patterns for n8n

This reference covers HMAC signature verification and JWT claim validation patterns for n8n Webhook nodes processing Israeli payment-gateway and form-submission callbacks. See `SKILL.md` Step 5 for the higher-level decision table on auth modes.

## Auth mode picker

| Mode | Where it lives | When to use it |
|------|---------------|----------------|
| None | Webhook node "Authentication" dropdown | Local testing only; never in production |
| Basic Auth | Generic Credential | Internal/private webhooks behind a VPN |
| Header Auth | Header Auth credential (e.g. `X-API-Key: <token>`) | Default for Israeli SMS callbacks and internal webhooks |
| JWT Auth | JWT credential (HMAC HS256/384/512 or RSA/ECDSA via PEM) | Cross-org integrations where the caller already issues JWTs |

Given the 2026 unauthenticated-webhook CVE history (CVE-2026-21858 file access on 1.x, CVE-2026-27493 expression injection on 1.x and early 2.x), the "None" mode on a publicly-routable webhook is effectively a vulnerability. Pick one of the other three for every payment-gateway flow.

## First: the Israeli payment gateways do NOT send an HMAC

Read this before reaching for a signature check. Cardcom's v11 result object carries **no signature field** of any kind (the spec exposes only `WebHookUrl`), and Grow ships a shared `webhookKey` **inside the body**. Neither is an HMAC. Writing an HMAC verifier for them protects nothing, and a public webhook URL with a static header is forgeable by anyone who learns the URL: a forged POST carrying a plausible `paymentSum` / `asmachta` will make your workflow issue a real tax invoice and burn a real allocation number.

**The verification that actually works for these gateways is a server-side re-read.** Never trust the callback body as the source of truth:

| Gateway | What arrives | What to verify against |
|---|---|---|
| Cardcom | `LowProfileResult` on your `WebHookUrl` | Re-read the transaction server-side by `LowProfileId` / `TranzactionId` and confirm `ResponseCode == 0` and the amount, before issuing any document |
| Grow by Meshulam | `multipart/form-data` POST with `webhookKey`, `asmachta`, `paymentSum` | Compare `webhookKey` against your stored key (constant-time), then re-read via `getPaymentProcessInfo`, then call `approveTransaction` to finalize |
| Tranzila | GET params incl. `Response`, `index`, `sum` | Re-read the transaction by `index`; `Response=000` alone is not proof of origin |

Do all of this **before** creating the invoice, and deduplicate on the gateway's own transaction id so a retried webhook cannot issue a second document.

## HMAC signature verification (for senders that actually sign)

Use this only where the sender genuinely signs its payload, which among the gateways here means custom integrations rather than Cardcom or Grow. n8n has no built-in HMAC verifier, so it goes in a Code node directly after the Webhook. Three things break the naive version:

1. **The item shape.** The Webhook node emits `{ json: { headers, params, query, body } }`. Reading `$input.first().headers` gets `undefined`.
2. **The secret.** `$env` is blocked inside Code nodes by default in n8n 2.x, so `$env.WEBHOOK_HMAC_SECRET` silently yields `undefined` and the comparison runs against a garbage key. Set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` **on the task runner**, or pass the secret in from a preceding credential-bearing node (accepting that it then appears in execution data).
3. **The raw body.** `JSON.stringify(body)` is NOT what the sender signed. Key order, whitespace and unicode escaping all differ, so the HMAC mismatches even when everything else is right. You need the raw bytes; if your n8n version does not expose them, capture them at the reverse proxy.

```javascript
// Requires NODE_FUNCTION_ALLOW_BUILTIN=crypto on the task runner.
const crypto = require('crypto');
const item = $input.first().json;                 // NOT $input.first()
const signature = item.headers['x-signature'];
const raw = item.rawBody ?? JSON.stringify(item.body); // see caveat 3 above
const secret = $env.WEBHOOK_HMAC_SECRET;          // see caveat 2 above
if (!secret) throw new Error('HMAC secret unavailable, refusing to accept the webhook');
const expected = crypto.createHmac('sha256', secret).update(raw).digest('hex');

const a = Buffer.from(signature || '', 'hex');
const b = Buffer.from(expected, 'hex');
if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
  throw new Error('Invalid HMAC signature');
}
return $input.all();
```

Use `crypto.timingSafeEqual`, never `===`. Both Buffers must be the same length or it throws, which the explicit length check handles. Fail closed: if the secret is missing, reject the webhook rather than accepting it.

## JWT claim validation (what n8n does and does not check)

**Expiry IS enforced.** n8n's Webhook JWT Auth calls `jwt.verify(token, secretOrPublicKey, { algorithms: [...] })` from `jsonwebtoken`, which rejects an expired token by default. An earlier version of this reference claimed otherwise; that was wrong. What n8n does NOT check is `iss` and `aud`, because it passes no `issuer` / `audience` options.

So add a claim check only for issuer and audience, and only **after** n8n's own signature verification has run (auth mode JWT Auth). Do not use this as a substitute for signature verification: the snippet below decodes rather than verifies, so on a webhook whose auth mode is None or Header Auth an attacker can mint any payload they like and pass it.

```javascript
// Only valid downstream of the Webhook node's JWT Auth mode, which has
// already verified the signature and the exp claim.
const item = $input.first().json;
const token = item.headers.authorization?.replace(/^Bearer\s+/i, '');
if (!token) throw new Error('Missing token');

const [, payloadB64] = token.split('.');
const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString());

if (payload.iss !== EXPECTED_ISSUER) throw new Error('Bad iss');
// aud may legitimately be an array (RFC 7519), so do not compare with !==
const aud = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
if (!aud.includes(EXPECTED_AUDIENCE)) throw new Error('Bad aud');

return $input.all();
```

`EXPECTED_ISSUER` and `EXPECTED_AUDIENCE` are shown as bare identifiers deliberately: `$env` reads are blocked in Code nodes by default in 2.x, so supply them from a preceding node or unblock env access on the runner. Do not paste `$env.X` here and assume it resolved.

## IP whitelisting

Cardcom and Tranzila require your webhook server's IP to be whitelisted in their dashboards. If self-hosting n8n, use a static IP or configure a reverse proxy with a fixed egress IP.
