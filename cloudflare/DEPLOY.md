# GHL API Proxy — 5-Minute Deploy

## Prerequisites
- Cloudflare account (free tier is fine)
- thecalltaker.com DNS already on Cloudflare
- Node.js installed

## Step 1 — Install Wrangler
```bash
npm install -g wrangler
```

## Step 2 — Login
```bash
wrangler login
```
Opens browser. Authorize. Done.

## Step 3 — Create KV namespace
```bash
cd ~/Desktop/thecalltaker/cloudflare
wrangler kv:namespace create RATE_LIMIT
```
Copy the returned `id` value and paste it into `wrangler.toml` replacing `PASTE_KV_NAMESPACE_ID_HERE`.

## Step 4 — Set secrets
```bash
wrangler secret put GHL_API_KEY
# Paste: pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35

wrangler secret put PROXY_SECRET
# Generate one: openssl rand -hex 32
# Paste the generated value. Save this — frontend needs it.
```

## Step 5 — Deploy
```bash
wrangler deploy
```

## Step 6 — Add route in Cloudflare dashboard
1. Go to **Cloudflare Dashboard → thecalltaker.com → Workers Routes**
2. Click **Add Route**
3. Route pattern: `thecalltaker.com/api/ghl/*`
4. Worker: `tct-ghl-proxy`
5. Click **Save**
6. Repeat for `www.thecalltaker.com/api/ghl/*`

## Step 7 — Test
```bash
# Should return 401 (no auth)
curl -s https://thecalltaker.com/api/ghl/contacts/ | jq

# Should return 403 (blocked endpoint)
curl -s -H "Authorization: Bearer YOUR_PROXY_SECRET" \
  https://thecalltaker.com/api/ghl/users/ | jq

# Should proxy to GHL successfully
curl -s -H "Authorization: Bearer YOUR_PROXY_SECRET" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"firstName":"Test","email":"test@example.com","phone":"+16155551234","locationId":"tQb9YmrGDrdVUJYPKrsY","tags":["test-proxy"]}' \
  https://thecalltaker.com/api/ghl/contacts/ | jq
```

## Frontend PROXY_SECRET
After generating the PROXY_SECRET, update `website/shared/tct-ghl-proxy.js` with the value.
The secret is a proxy auth token — not the GHL key. It's safe to ship in frontend code.
It only authorizes calls to YOUR proxy, which is already origin-locked and rate-limited.

## Monitoring
Cloudflare Dashboard → Workers & Pages → tct-ghl-proxy → Logs
Free tier: 100,000 requests/day. You'll use ~500-2000/day.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| Worker threw exception | Bug in worker.js or missing env var | Check Workers dashboard logs |
| CORS not working | Origin mismatch or missing route | Verify route pattern + allowed origins |
| GHL returns 401 | Bad or expired GHL_API_KEY | `wrangler secret put GHL_API_KEY` with fresh key |
| 429 from proxy | >10 req/min from same IP | Normal — wait 60s. Raise limit if needed |
| 429 from GHL | GHL rate limiting upstream | Wait 30s. Check GHL API usage dashboard |
| 404 on /api/ghl/* | Route not bound to worker | Add route in Cloudflare dashboard (Step 6) |
| 504 Gateway Timeout | GHL took >10s to respond | Retry. If persistent, check GHL status page |
| 403 Endpoint not allowed | Path not in allowlist | Add pattern to ALLOWED_ENDPOINTS in worker.js |

## Day 2 Improvements (after core is live)

### KV Cache for Contact Lookups
Add to worker.js after successful GHL response for GET /contacts/{id}:
```js
if (request.method === 'GET' && ghlPath.match(/^\/contacts\/[a-zA-Z0-9]+\/?$/)) {
  ctx.waitUntil(env.RATE_LIMIT.put(`cache:${ghlPath}`, responseBody, { expirationTtl: 60 }));
}
```
Check cache before proxying:
```js
const cached = await env.RATE_LIMIT.get(`cache:${ghlPath}`);
if (cached && request.method === 'GET') return new Response(cached, { status: 200, headers: responseHeaders });
```

### Webhook Signature Validation
For GHL inbound webhooks, verify HMAC-SHA256:
```js
const signature = request.headers.get('X-GHL-Signature');
const body = await request.text();
const expected = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(body));
```

### Multi-Location Support
Replace hardcoded LOCATION_ID with a KV lookup:
```js
const locationMap = JSON.parse(await env.RATE_LIMIT.get('locations') || '{}');
```
