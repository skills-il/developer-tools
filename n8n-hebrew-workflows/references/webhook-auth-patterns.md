# Webhook Authentication Patterns for n8n

This reference covers HMAC signature verification and JWT claim validation patterns for n8n Webhook nodes processing Israeli payment-gateway and form-submission callbacks. See `SKILL.md` Step 5 for the higher-level decision table on auth modes.

## Auth mode picker

| Mode | Where it lives | When to use it |
|------|---------------|----------------|
| None | Webhook node "Authentication" dropdown | Local testing only; never in production |
| Basic Auth | Generic Credential | Internal/private webhooks behind a VPN |
| Header Auth | Header Auth credential (e.g. `X-API-Key: <token>`) | Default for Israeli SMS callbacks and internal webhooks |
| JWT Auth | JWT credential (HMAC HS256/384/512 or RSA/ECDSA via PEM) | Cross-org integrations where the caller already issues JWTs |

After CVE-2026-21858 (Ni8mare), the "None" mode on a publicly-routable webhook is effectively a vulnerability. Pick one of the other three for every payment-gateway flow.

## HMAC signature verification (Cardcom, Grow, custom integrations)

n8n does NOT have a built-in HMAC verifier. Implement it in a Code node directly after the Webhook:

```javascript
const crypto = require('crypto');
const signature = $input.first().headers['x-signature']; // or x-cardcom-signature etc.
const rawBody = JSON.stringify($input.first().body); // or $input.first().rawBody if exposed
const secret = $env.WEBHOOK_HMAC_SECRET;
const expected = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');

// Timing-safe compare to avoid signature leak via response timing
const a = Buffer.from(signature || '', 'hex');
const b = Buffer.from(expected, 'hex');
if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
  throw new Error('Invalid HMAC signature');
}
return $input.all();
```

Notes:
- Use `crypto.timingSafeEqual`, not `===`, to avoid leaking the signature via response-time differences.
- Both Buffers must be the same length, otherwise `timingSafeEqual` throws; the explicit length check handles that.
- If `$input.first().rawBody` is not exposed in your n8n version, capturing the raw body may require a small middleware or reverse-proxy header (e.g. nginx `mirror`).

## JWT claim validation (caveat)

n8n's JWT Auth credential validates the signature but does NOT auto-check `exp`, `iss`, or `aud` claims. If you need claim validation, decode the token in a Code node and verify each claim explicitly:

```javascript
const token = $input.first().headers.authorization?.replace(/^Bearer\s+/i, '');
if (!token) throw new Error('Missing token');

const [, payloadB64] = token.split('.');
const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString());

const now = Math.floor(Date.now() / 1000);
if (payload.exp && payload.exp < now) throw new Error('Token expired');
if (payload.iss !== $env.EXPECTED_ISSUER) throw new Error('Bad iss');
if (payload.aud !== $env.EXPECTED_AUDIENCE) throw new Error('Bad aud');

return $input.all();
```

Without this step, an expired token will still pass through n8n's JWT Auth.

## IP whitelisting

Cardcom and Tranzila require your webhook server's IP to be whitelisted in their dashboards. If self-hosting n8n, use a static IP or configure a reverse proxy with a fixed egress IP.
