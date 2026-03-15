#!/bin/bash
# ═══════════════════════════════════════════
# WATER DAMAGE BOT UNINSTALLER
# Stops all WD-Max + WD-Ben services
# Run: bash uninstall-wd-bots.sh
# ═══════════════════════════════════════════

PLIST_DIR="$HOME/Library/LaunchAgents"

echo "Stopping Water Damage Bots..."

# Stop WD-Max services
for svc in monitor followup pipeline report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.wd.max.$svc.plist" 2>/dev/null
done

# Stop WD-Ben services
for svc in morning sms reengage score evening; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.wd.ben.$svc.plist" 2>/dev/null
done

# Remove plist files
rm -f "$PLIST_DIR/com.thecalltaker.wd.max."*.plist
rm -f "$PLIST_DIR/com.thecalltaker.wd.ben."*.plist

echo "Water Damage Bots have been stopped and removed."
echo ""
echo "To reinstall: bash $(cd "$(dirname "$0")" && pwd)/install-wd-bots.sh"
