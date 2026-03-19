#!/usr/bin/env bash
# notify.sh — Reusable ntfy.sh alert function for The Call Taker
# Usage: ./notify.sh "TITLE" "MESSAGE" "priority"
# Priority: low, default, high, urgent
#
# Routes to correct ntfy topic based on priority:
#   urgent → tct-urgent-Hk9UOEZR
#   high   → tct-urgent-Hk9UOEZR
#   default→ tct-sales-63uYsIT9
#   low    → tct-activity-cn1Aqa85
#   system → tct-system-vRsfXQRQ
#
# Install: cp notify.sh ~/thecalltaker-ops/notify.sh && chmod +x ~/thecalltaker-ops/notify.sh

set -euo pipefail

TITLE="${1:-Alert}"
MESSAGE="${2:-No message provided}"
PRIORITY="${3:-default}"

# Topic routing
case "$PRIORITY" in
  urgent)  TOPIC="tct-urgent-Hk9UOEZR"; NTFY_PRIORITY="urgent" ;;
  high)    TOPIC="tct-urgent-Hk9UOEZR"; NTFY_PRIORITY="high" ;;
  default) TOPIC="tct-sales-63uYsIT9";  NTFY_PRIORITY="default" ;;
  low)     TOPIC="tct-activity-cn1Aqa85"; NTFY_PRIORITY="low" ;;
  system)  TOPIC="tct-system-vRsfXQRQ";  NTFY_PRIORITY="default" ;;
  *)       TOPIC="tct-sales-63uYsIT9";  NTFY_PRIORITY="default" ;;
esac

# Sanitize headers (strip newlines, limit length)
SAFE_TITLE=$(echo "$TITLE" | tr '\n' ' ' | cut -c1-200)
SAFE_MESSAGE=$(echo "$MESSAGE" | tr '\n' ' ' | cut -c1-4000)

# Send with retry (3 attempts)
SENT=0
for ATTEMPT in 1 2 3; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 10 \
    -H "Title: $SAFE_TITLE" \
    -H "Priority: $NTFY_PRIORITY" \
    -H "Tags: thecalltaker" \
    -d "$SAFE_MESSAGE" \
    "https://ntfy.sh/$TOPIC" 2>/dev/null) || HTTP_CODE=0

  if [ "$HTTP_CODE" -eq 200 ]; then
    SENT=1
    break
  fi

  if [ "$ATTEMPT" -lt 3 ]; then
    sleep $((ATTEMPT * 2))
  fi
done

# Log the notification
LOG_DIR="${HOME}/thecalltaker-ops/logs"
mkdir -p "$LOG_DIR"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$SENT" -eq 1 ]; then
  echo "[$TS] SENT topic=$TOPIC priority=$NTFY_PRIORITY title=\"$SAFE_TITLE\"" >> "$LOG_DIR/notify.log"
else
  echo "[$TS] FAILED topic=$TOPIC priority=$NTFY_PRIORITY title=\"$SAFE_TITLE\" (http=$HTTP_CODE)" >> "$LOG_DIR/notify.log"
  exit 1
fi
