#!/bin/bash
# ============================================
# THE CALL TAKER — Engine Activation Script
# Copies all plists to LaunchAgents and loads them
# Run: bash ~/thecalltaker/ops/activate-all-engines.sh
# ============================================

set -e

PLIST_DIR="$HOME/thecalltaker/ops"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  THE CALL TAKER — Engine Activation"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# All plist files to activate
PLISTS=(
    "com.thecalltaker.hot-lead-converter"
    "com.thecalltaker.blast-engine-v2"
    "com.thecalltaker.outbound-sms"
    "com.thecalltaker.storm-chaser-v2"
    "com.thecalltaker.stripe-webhook"
    "com.thecalltaker.payment-reminder"
    "com.thecalltaker.dm-tracker"
    "com.thecalltaker.lead-dashboard"
    "com.thecalltaker.blast-sms-followup"
    "com.thecalltaker.demo-webhook"
    "com.thecalltaker.post-payment-onboarding"
)

LOADED=0
FAILED=0

for LABEL in "${PLISTS[@]}"; do
    PLIST_FILE="$PLIST_DIR/$LABEL.plist"
    DEST_FILE="$LAUNCH_DIR/$LABEL.plist"

    if [ ! -f "$PLIST_FILE" ]; then
        echo -e "${RED}[MISSING]${NC} $LABEL — plist not found"
        ((FAILED++))
        continue
    fi

    # Unload if already loaded (ignore errors)
    launchctl unload "$DEST_FILE" 2>/dev/null || true

    # Copy to LaunchAgents
    cp "$PLIST_FILE" "$DEST_FILE"

    # Load the service
    if launchctl load "$DEST_FILE" 2>/dev/null; then
        echo -e "${GREEN}[LOADED]${NC} $LABEL"
        ((LOADED++))
    else
        echo -e "${RED}[FAILED]${NC} $LABEL — launchctl load failed"
        ((FAILED++))
    fi
done

echo ""
echo "============================================"
echo "  Results: $LOADED loaded, $FAILED failed"
echo "============================================"
echo ""

# Run health check
echo "Running health check..."
echo ""
python3 "$HOME/thecalltaker/ops/engine-health-check.py" 2>/dev/null || echo "Health check script not found — run it separately"
