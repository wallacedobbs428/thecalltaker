#!/bin/bash
# ===================================================
# SAM INSTALLER — 24/7 Customer Success Team Member
# Run once: bash install-sam.sh
# ===================================================

SAM_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PYTHON="/usr/bin/python3"

echo "Installing Sam — The Call Taker's 24/7 Customer Success Team Member"
echo "===================================================================="

chmod +x "$SAM_DIR/sam-engine.py"
mkdir -p "$PLIST_DIR"

# --- Support Monitor: Every 15 minutes ---
cat > "$PLIST_DIR/com.thecalltaker.sam.support.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.sam.support</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SAM_DIR}/sam-engine.py</string>
        <string>support</string>
    </array>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${SAM_DIR}/sam-support.log</string>
    <key>StandardErrorPath</key>
    <string>${SAM_DIR}/sam-support-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# --- Health Scoring: Daily at 6:00 AM ---
cat > "$PLIST_DIR/com.thecalltaker.sam.health.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.sam.health</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SAM_DIR}/sam-engine.py</string>
        <string>health</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${SAM_DIR}/sam-health.log</string>
    <key>StandardErrorPath</key>
    <string>${SAM_DIR}/sam-health-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# --- Milestone Check-ins: Daily at 8:00 AM ---
cat > "$PLIST_DIR/com.thecalltaker.sam.checkin.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.sam.checkin</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SAM_DIR}/sam-engine.py</string>
        <string>checkin</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${SAM_DIR}/sam-checkin.log</string>
    <key>StandardErrorPath</key>
    <string>${SAM_DIR}/sam-checkin-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# --- Referral Requests: Daily at 11:00 AM (alerts Wallace to call, email fallback after 48h) ---
cat > "$PLIST_DIR/com.thecalltaker.sam.referral.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.sam.referral</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SAM_DIR}/sam-engine.py</string>
        <string>referral</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>11</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${SAM_DIR}/sam-referral.log</string>
    <key>StandardErrorPath</key>
    <string>${SAM_DIR}/sam-referral-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# --- Daily Report: 7:00 PM ---
cat > "$PLIST_DIR/com.thecalltaker.sam.report.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.sam.report</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SAM_DIR}/sam-engine.py</string>
        <string>report</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${SAM_DIR}/sam-report.log</string>
    <key>StandardErrorPath</key>
    <string>${SAM_DIR}/sam-report-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

echo ""
echo "Loading Sam into launchd..."

# Unload old versions if they exist
for svc in support health checkin referral report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.sam.$svc.plist" 2>/dev/null
done

# Load new versions
for svc in support health checkin referral report; do
    launchctl load "$PLIST_DIR/com.thecalltaker.sam.$svc.plist"
done

echo ""
echo "SAM IS LIVE. Schedule:"
echo "  - Support monitor:    Every 15 minutes (starting now)"
echo "  - Health scoring:     Daily at 6:00 AM"
echo "  - Milestone check-ins: Daily at 8:00 AM"
echo "  - Referral requests:  Daily at 11:00 AM (alerts Wallace, email fallback after 48h)"
echo "  - Daily report:       Daily at 7:00 PM"
echo ""
echo "Commands:"
echo "  Status:   python3 $SAM_DIR/sam-engine.py status"
echo "  Logs:     cat $SAM_DIR/sam-log.txt"
echo "  Stop:     bash $SAM_DIR/uninstall-sam.sh"
echo ""
echo "Sam takes care of your customers. Sam never sleeps."
