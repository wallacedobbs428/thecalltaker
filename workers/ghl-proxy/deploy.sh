#!/usr/bin/env bash
# deploy.sh — Deploy TCT GHL Proxy Worker to Cloudflare
# Run from: workers/ghl-proxy/
set -euo pipefail

echo "=== TCT GHL Proxy — Deploy ==="

# 1. Create KV namespace for rate limiting
echo "[1/7] Creating KV namespace..."
KV_OUTPUT=$(wrangler kv:namespace create RATE_LIMIT 2>&1)
echo "$KV_OUTPUT"
KV_ID=$(echo "$KV_OUTPUT" | grep -oP 'id = "\K[^"]+' || true)
if [ -n "$KV_ID" ]; then
  echo "  → KV ID: $KV_ID"
  sed -i "s/{ binding = \"RATE_LIMIT\", id = \"\" }/{ binding = \"RATE_LIMIT\", id = \"$KV_ID\" }/" wrangler.toml
  echo "  → Updated wrangler.toml with KV ID"
else
  echo "  → KV namespace may already exist. Check wrangler.toml manually."
fi

# 2. Set GHL API key (interactive prompt)
echo ""
echo "[2/7] Setting GHL_API_KEY secret..."
echo "  Paste your GHL API key when prompted:"
wrangler secret put GHL_API_KEY

# 3. Set proxy auth secret
echo ""
echo "[3/7] Setting PROXY_SECRET..."
echo "  Paste a strong random token (frontend uses this to auth):"
wrangler secret put PROXY_SECRET

# 4. Deploy worker
echo ""
echo "[4/7] Deploying worker..."
wrangler deploy

# 5. Verify deployment
echo ""
echo "[5/7] Verifying deployment..."
wrangler deployments list 2>&1 | head -10

# 6. Quick health check
echo ""
echo "[6/7] Health check..."
curl -s "https://thecalltaker.com/api/ghl/health" | python3 -m json.tool 2>/dev/null || echo "  (Health endpoint may take a moment to propagate)"

# 7. Security scan — ensure no exposed keys in source
echo ""
echo "[7/7] Security scan — checking for exposed keys..."
EXPOSED=$(grep -rn "pit-\|org_e0d7\|1884b87d" worker.js wrangler.toml 2>/dev/null | wc -l)
if [ "$EXPOSED" -gt 0 ]; then
  echo "  !! WARNING: Found $EXPOSED exposed key references. Fix before going live!"
  grep -rn "pit-\|org_e0d7\|1884b87d" worker.js wrangler.toml 2>/dev/null
  exit 1
else
  echo "  ✓ Zero exposed keys in worker source"
fi

echo ""
echo "=== Deploy complete ==="
echo "Proxy live at: https://thecalltaker.com/api/ghl/*"
echo "Health check:  https://thecalltaker.com/api/ghl/health"
