#!/bin/bash
# Stop Max from running
PLIST_DIR="$HOME/Library/LaunchAgents"
echo "Stopping Max..."
launchctl unload "$PLIST_DIR/com.thecalltaker.max.monitor.plist" 2>/dev/null
launchctl unload "$PLIST_DIR/com.thecalltaker.max.followup.plist" 2>/dev/null
launchctl unload "$PLIST_DIR/com.thecalltaker.max.pipeline.plist" 2>/dev/null
rm -f "$PLIST_DIR/com.thecalltaker.max."*.plist
echo "Max has been stopped and removed."
