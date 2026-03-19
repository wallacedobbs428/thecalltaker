#!/usr/bin/env bash
# verify.sh — 6 security + functionality tests for the GHL proxy
set -euo pipefail

PROXY_SECRET="${PROXY_SECRET:-test-secret-change-me}"
BASE="https://thecalltaker.com/api/ghl"
PASS=0
FAIL=0

check() {
  local label="$1" expected_status="$2" actual_status="$3"
  if [ "$actual_status" -eq "$expected_status" ]; then
    echo "  PASS [$actual_status] $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL [$actual_status, expected $expected_status] $label"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== TCT GHL Proxy — Verification ==="
echo ""

# Test 1: Health endpoint (no auth needed)
echo "[1/6] Health check..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
check "Health endpoint returns 200" 200 "$STATUS"

# Test 2: Correct origin + valid auth → should pass (contacts list)
echo "[2/6] Valid request (correct origin + auth)..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Origin: https://thecalltaker.com" \
  -H "Authorization: Bearer $PROXY_SECRET" \
  "$BASE/contacts?locationId=tQb9YmrGDrdVUJYPKrsY&limit=1")
check "Valid origin + auth returns 200" 200 "$STATUS"

# Test 3: Wrong origin → 403
echo "[3/6] Wrong origin..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Origin: https://evil.com" \
  -H "Authorization: Bearer $PROXY_SECRET" \
  "$BASE/contacts")
check "Wrong origin returns 403" 403 "$STATUS"

# Test 4: No auth → 401
echo "[4/6] No auth token..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Origin: https://thecalltaker.com" \
  "$BASE/contacts")
check "No auth returns 401" 401 "$STATUS"

# Test 5: Blocked path → 403
echo "[5/6] Blocked path (/users)..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Origin: https://thecalltaker.com" \
  -H "Authorization: Bearer $PROXY_SECRET" \
  "$BASE/users")
check "Blocked path returns 403" 403 "$STATUS"

# Test 6: Rate limit (fire 12 rapid requests, last should be 429)
echo "[6/6] Rate limit (12 rapid requests)..."
LAST_STATUS=200
for i in $(seq 1 12); do
  LAST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: https://thecalltaker.com" \
    -H "Authorization: Bearer $PROXY_SECRET" \
    "$BASE/contacts?locationId=tQb9YmrGDrdVUJYPKrsY&limit=1")
done
check "12th request returns 429 (rate limited)" 429 "$LAST_STATUS"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "ALL TESTS PASSED" || echo "SOME TESTS FAILED — investigate above"
