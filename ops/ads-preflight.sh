#!/bin/zsh
set -euo pipefail

PAGES=(
  "https://thecalltaker.com/"
  "https://thecalltaker.com/signup.html"
  "https://thecalltaker.com/pilot/"
  "https://thecalltaker.com/calculator.html"
  "https://thecalltaker.com/try-live.html"
  "https://thecalltaker.com/start.html"
  "https://thecalltaker.com/pay.html"
)

FAIL=0

echo "== App Health =="
curl -L -sS https://thecalltaker.vercel.app/api/health | rg '"status":"ok"' >/dev/null && echo "PASS app health" || { echo "FAIL app health"; FAIL=1; }

echo
echo "== Public Pages =="
for page in "${PAGES[@]}"; do
  echo "-- $page"
  body="$(curl -sS "$page")"
  if [[ -z "$body" ]]; then
    echo "FAIL empty body"
    FAIL=1
    continue
  fi
  echo "$body" | rg "leadconnectorhq|rest\\.gohighlevel|pit-|\\(615\\) 784-5747|\\+16157845747" >/dev/null && {
    echo "FAIL legacy pattern found"
    FAIL=1
  } || echo "PASS legacy patterns clean"
done

exit "$FAIL"
