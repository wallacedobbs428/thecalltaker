#!/bin/bash
# Stop all Ben services
PLIST_DIR="$HOME/Library/LaunchAgents"
echo "Stopping Ben v2..."
for svc in morning outreach sms reengage score evening; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.ben.$svc.plist" 2>/dev/null
done
rm -f "$PLIST_DIR/com.thecalltaker.ben."*.plist
echo "Ben has been stopped and removed."
