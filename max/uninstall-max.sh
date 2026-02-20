#!/bin/bash
# Stop all Max services
PLIST_DIR="$HOME/Library/LaunchAgents"
echo "Stopping Max v3..."
for svc in monitor followup outreach pipeline report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.max.$svc.plist" 2>/dev/null
done
rm -f "$PLIST_DIR/com.thecalltaker.max."*.plist
echo "Max has been stopped and removed."
