#!/bin/bash
# ═══════════════════════════════════════════════════════════
# FIX LAUNCHD PATHS — Replace old wallace-hvac paths
# Run on your Mac: bash ~/Desktop/thecalltaker/tools/fix-launchd-paths.sh
# ═══════════════════════════════════════════════════════════

PLIST_DIR="$HOME/Library/LaunchAgents"
OLD_PATH="/Users/moneymaker99/Desktop/wallace-hvac"
NEW_PATH="/Users/moneymaker99/thecalltaker-ops"

echo "🔧 Fixing launchd plist paths..."
echo "   Old: $OLD_PATH"
echo "   New: $NEW_PATH"
echo ""

FIXED=0
SKIPPED=0

for plist in "$PLIST_DIR"/com.thecalltaker.*.plist; do
    [ -f "$plist" ] || continue
    name=$(basename "$plist")

    if grep -q "$OLD_PATH" "$plist"; then
        # Unload first
        launchctl unload "$plist" 2>/dev/null

        # Fix the path
        sed -i '' "s|$OLD_PATH|$NEW_PATH|g" "$plist"

        # Also fix Desktop/thecalltaker references to thecalltaker-ops for engine scripts
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/max/|/Users/moneymaker99/thecalltaker-ops/max/|g" "$plist"
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/ben/|/Users/moneymaker99/thecalltaker-ops/ben/|g" "$plist"
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/sam/|/Users/moneymaker99/thecalltaker-ops/sam/|g" "$plist"
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/donny/|/Users/moneymaker99/thecalltaker-ops/donny/|g" "$plist"
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/ops/|/Users/moneymaker99/thecalltaker-ops/ops/|g" "$plist"
        sed -i '' "s|/Users/moneymaker99/Desktop/thecalltaker/pilot/|/Users/moneymaker99/thecalltaker-ops/pilot/|g" "$plist"

        # Reload
        launchctl load "$plist"

        echo "   ✅ Fixed + reloaded: $name"
        FIXED=$((FIXED + 1))
    else
        echo "   ⏭  Already correct: $name"
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "Done: $FIXED fixed, $SKIPPED already correct"
echo ""
echo "Verify with: launchctl list | grep thecalltaker"
