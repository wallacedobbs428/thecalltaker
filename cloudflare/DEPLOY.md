# GHL API Proxy — 4-Step Deploy

## Prerequisites
- Cloudflare account (free tier is fine)
- thecalltaker.com DNS already on Cloudflare (orange cloud / Proxied)
- Node.js installed

## Step 1 — Install Wrangler + Login
```bash
npm install -g wrangler
wrangler login
```
Opens browser. Authorize. Done.

## Step 2 — Set secrets (use echo -n to avoid trailing newline corruption)
```bash
cd ~/Desktop/thecalltaker/cloudflare

echo -n 'pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35' | wrangler secret put GHL_API_KEY

PROXY=$(openssl rand -hex 32)
echo "$PROXY" > ~/proxy-secret.txt
cat ~/proxy-secret.txt
echo -n "$PROXY" | wrangler secret put PROXY_SECRET
```
**Save the PROXY_SECRET value** — you'll need it for the frontend in Step 4.

## Step 3 — Deploy
```bash
wrangler deploy
```
Routes are in `wrangler.toml` — they bind automatically. No dashboard step needed.

Verify secrets exist:
```bash
wrangler secret list
```
Must show both `GHL_API_KEY` and `PROXY_SECRET`.

### Verify with curl (wait 30 seconds after deploy)
```bash
# Test 1 — Health check (no auth needed, confirms Worker is alive)
curl -i https://thecalltaker.com/api/ghl/health

# Test 2 — Wrong origin blocked (403)
curl -i -H "Origin: https://evil.com" \
  https://thecalltaker.com/api/ghl/contacts/ -X POST

# Test 3 — No auth rejected (401)
curl -i -H "Origin: https://thecalltaker.com" \
  https://thecalltaker.com/api/ghl/contacts/ -X POST

# Test 4 — Valid auth hits GHL (replace YOUR_PROXY_SECRET)
curl -i -H "Authorization: Bearer YOUR_PROXY_SECRET" \
  -H "Content-Type: application/json" \
  "https://thecalltaker.com/api/ghl/contacts/?locationId=tQb9YmrGDrdVUJYPKrsY&limit=1"

# Test 5 — Disallowed endpoint blocked (403)
curl -i -H "Authorization: Bearer YOUR_PROXY_SECRET" \
  https://thecalltaker.com/api/ghl/users/
```
All 5 must pass before Step 4.

## Step 4 — Update frontend
Edit `website/shared/tct-ghl-proxy.js` — replace `REPLACE_WITH_PROXY_SECRET_AFTER_DEPLOY` with the value from `~/proxy-secret.txt`.

Commit + push to main. Then:
```bash
rm ~/proxy-secret.txt
```

## Monitoring
Cloudflare Dashboard → Workers & Pages → tct-ghl-proxy → Logs
Free tier: 100,000 requests/day. You'll use ~500-2,000/day.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Health returns GitHub Pages HTML | Route not bound | Check `wrangler.toml` routes are uncommented, redeploy |
| Every request returns 401 | Trailing newline in PROXY_SECRET | `wrangler secret delete PROXY_SECRET` then re-put with `echo -n` |
| GHL returns 401 (via proxy 502) | Bad GHL_API_KEY | Re-put with `echo -n 'key' \| wrangler secret put GHL_API_KEY` |
| Worker threw exception | Missing env var or bug | Check Workers dashboard → Logs |
| CORS errors in browser | Origin mismatch | Verify request comes from thecalltaker.com, not localhost |
| 429 from proxy | >10 req/min from same IP | Normal — wait 60s |
| 429 from GHL | GHL rate limiting upstream | Wait 30s |
| 404 on /api/ghl/* | DNS not Proxied (orange cloud) | Cloudflare DNS → toggle to Proxied |
| 504 Gateway Timeout | GHL took >10s | Retry. Check GHL status page |
| 403 Endpoint not allowed | Path not in allowlist | Add regex to ALLOWED_ENDPOINTS in worker.js |

## Day 2 Improvements (after core is live)

### KV-backed rate limiting (when you outgrow free tier)
Create KV namespace and switch from in-memory to KV:
```bash
wrangler kv:namespace create RATE_LIMIT
```
Uncomment the `[[kv_namespaces]]` block in `wrangler.toml`, paste the ID, and update `checkRateLimit()` in `worker.js` to use `env.RATE_LIMIT` KV store.

### KV Cache for Contact Lookups
Cache GET /contacts/{id} responses for 60s to reduce GHL API calls.

### Webhook Signature Validation
Verify HMAC-SHA256 on inbound GHL webhooks.
