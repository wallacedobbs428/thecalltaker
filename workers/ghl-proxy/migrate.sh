#!/usr/bin/env bash
# migrate.sh — Migrate all HTML files from direct GHL API calls to proxy
# Run from repo root: bash workers/ghl-proxy/migrate.sh
set -euo pipefail

echo "=== Migrating GHL API calls to proxy ==="

WEBSITE_DIR="website"
PROXY_SECRET="${PROXY_SECRET:-YOUR_PROXY_SECRET_HERE}"

if [ ! -d "$WEBSITE_DIR" ]; then
  echo "ERROR: Run from repo root (directory 'website/' not found)"
  exit 1
fi

# Count files that reference direct GHL API
BEFORE=$(grep -rl "services\.leadconnectorhq\.com" "$WEBSITE_DIR" --include="*.html" 2>/dev/null | wc -l)
echo "Files with direct GHL calls: $BEFORE"

if [ "$BEFORE" -eq 0 ]; then
  echo "No direct GHL API calls found. Already migrated or none exist."
  exit 0
fi

# Replace direct GHL API URLs with proxy path
# FROM: https://services.leadconnectorhq.com/contacts/...
# TO:   /api/ghl/contacts/...
find "$WEBSITE_DIR" -name "*.html" -exec sed -i \
  "s|https://services\.leadconnectorhq\.com|/api/ghl|g" {} +

echo "Replaced GHL base URLs in HTML files."

# Also replace any fetch calls that pass the GHL key directly in headers
# This catches: 'Authorization': 'Bearer pit-...'
# Replace with proxy auth header
find "$WEBSITE_DIR" -name "*.html" -exec sed -i \
  "s|'Bearer pit-[^']*'|'Bearer ' + TCT_PROXY_TOKEN|g" {} +

find "$WEBSITE_DIR" -name "*.html" -exec sed -i \
  "s|\"Bearer pit-[^\"]*\"|'Bearer ' + TCT_PROXY_TOKEN|g" {} +

AFTER=$(grep -rl "services\.leadconnectorhq\.com" "$WEBSITE_DIR" --include="*.html" 2>/dev/null | wc -l)
echo ""
echo "=== Migration complete ==="
echo "Before: $BEFORE files with direct GHL calls"
echo "After:  $AFTER files with direct GHL calls"
echo ""
echo "IMPORTANT: Add this to each page's <script> before GHL fetch calls:"
echo "  const TCT_PROXY_TOKEN = 'YOUR_PROXY_SECRET';"
echo ""
echo "Then search for any remaining 'pit-' references:"
echo "  grep -rn 'pit-' $WEBSITE_DIR --include='*.html' | head -20"
