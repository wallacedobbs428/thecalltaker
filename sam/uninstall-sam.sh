#!/bin/bash
# Stop Sam from running
PLIST_DIR="$HOME/Library/LaunchAgents"
echo "Stopping Sam..."
for svc in support health checkin referral report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.sam.$svc.plist" 2>/dev/null
done
rm -f "$PLIST_DIR/com.thecalltaker.sam."*.plist
echo "Sam has been stopped and removed."
