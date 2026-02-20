#!/bin/bash
# ═══════════════════════════════════════════
# MAX v3 INSTALLER — Reply Catcher + Follow-Up Machine
# Run once: bash install-max.sh
# ═══════════════════════════════════════════

MAX_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PYTHON="/usr/bin/python3"

echo "Installing Max v3 — Reply Catcher + Follow-Up Machine"
echo "======================================================"

chmod +x "$MAX_DIR/max-engine.py"
mkdir -p "$PLIST_DIR"

# ─── Reply Monitor: Every 30 minutes ───
cat > "$PLIST_DIR/com.thecalltaker.max.monitor.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.max.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${MAX_DIR}/max-engine.py</string>
        <string>monitor</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${MAX_DIR}/max-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>${MAX_DIR}/max-monitor-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Follow-ups: Daily at 9:00 AM ───
cat > "$PLIST_DIR/com.thecalltaker.max.followup.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.max.followup</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${MAX_DIR}/max-engine.py</string>
        <string>followup</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${MAX_DIR}/max-followup.log</string>
    <key>StandardErrorPath</key>
    <string>${MAX_DIR}/max-followup-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Pipeline: Daily at midnight ───
cat > "$PLIST_DIR/com.thecalltaker.max.pipeline.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.max.pipeline</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${MAX_DIR}/max-engine.py</string>
        <string>pipeline</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${MAX_DIR}/max-pipeline.log</string>
    <key>StandardErrorPath</key>
    <string>${MAX_DIR}/max-pipeline-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Daily Report: 8:00 PM ───
cat > "$PLIST_DIR/com.thecalltaker.max.report.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.max.report</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${MAX_DIR}/max-engine.py</string>
        <string>report</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${MAX_DIR}/max-report.log</string>
    <key>StandardErrorPath</key>
    <string>${MAX_DIR}/max-report-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

echo ""
echo "Loading Max v3 into launchd..."

# Unload old versions (including removed outreach)
for svc in monitor followup outreach pipeline report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.max.$svc.plist" 2>/dev/null
done
# Remove old outreach plist if it exists
rm -f "$PLIST_DIR/com.thecalltaker.max.outreach.plist"

# Load new versions (4 services — no outreach)
for svc in monitor followup pipeline report; do
    launchctl load "$PLIST_DIR/com.thecalltaker.max.$svc.plist"
done

echo ""
echo "MAX v3 IS LIVE. Schedule:"
echo "  - Reply monitor:     Every 30 minutes (replies + demo calls + secret shopper + weather)"
echo "  - Warm follow-ups:   Daily at 9:00 AM"
echo "  - Pipeline manager:  Daily at midnight"
echo "  - Daily report:      Daily at 8:00 PM"
echo ""
echo "REMOVED: Cold outreach (handled by Instantly + blast scripts)"
echo ""
echo "Commands:"
echo "  Status:   python3 $MAX_DIR/max-engine.py status"
echo "  Logs:     cat $MAX_DIR/max-log.txt"
echo "  Stop:     bash $MAX_DIR/uninstall-max.sh"
echo ""
echo "Max v3 — Reply Catcher. Never misses a response."
