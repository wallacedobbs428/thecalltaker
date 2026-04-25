#!/bin/zsh
set -euo pipefail

ROOT="${1:-/Users/moneymaker99/thecalltaker/website}"

if [[ ! -d "$ROOT" ]]; then
  echo "missing website root: $ROOT" >&2
  exit 1
fi

LAUNCH_PAGES=(
  "$ROOT/index.html"
  "$ROOT/signup.html"
  "$ROOT/pilot/index.html"
  "$ROOT/calculator.html"
  "$ROOT/try-live.html"
  "$ROOT/start.html"
  "$ROOT/pay.html"
)

PATTERN_NAMES=(
  "legacy_ghl_domain"
  "legacy_ghl_api"
  "legacy_private_key"
  "old_demo_e164"
  "old_demo_plain"
)

PATTERNS=(
  "leadconnectorhq"
  "rest\\.gohighlevel"
  "pit-"
  "\\+16157845747"
  "6157845747|\\(615\\) 784-5747"
)

exit_code=0

for i in {1..5}; do
  name="${PATTERN_NAMES[$i]}"
  pattern="${PATTERNS[$i]}"
  if rg -n "$pattern" "${LAUNCH_PAGES[@]}" >/tmp/tct_audit_match.txt 2>/dev/null; then
    echo "FAIL [$name]"
    cat /tmp/tct_audit_match.txt
    echo
    exit_code=1
  else
    echo "PASS [$name]"
  fi
done

echo
echo "Checked pages:"
printf ' - %s\n' "${LAUNCH_PAGES[@]}"

exit "$exit_code"
