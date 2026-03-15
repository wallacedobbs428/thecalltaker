#!/bin/bash
# ═══════════════════════════════════════════
# WATER DAMAGE BOT INSTALLER
# Installs WD-Max + WD-Ben on Mills' machine
# Run once: bash install-wd-bots.sh
# ═══════════════════════════════════════════

WD_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PYTHON="/usr/bin/python3"

echo "Installing Water Damage Bots — WD-Max + WD-Ben"
echo "================================================"
echo ""

chmod +x "$WD_DIR/wd-max-engine.py"
chmod +x "$WD_DIR/wd-ben-engine.py"
mkdir -p "$PLIST_DIR"

# ═══════════════════════════════════════════
# WD-MAX — Reply Catcher (Water Damage)
# ═══════════════════════════════════════════

echo "Setting up WD-Max (Reply Catcher)..."

# ─── Reply Monitor: Every 30 minutes ───
cat > "$PLIST_DIR/com.thecalltaker.wd.max.monitor.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.max.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-max-engine.py</string>
        <string>monitor</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-max-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-max-monitor-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Follow-ups: Daily at 9:00 AM ───
cat > "$PLIST_DIR/com.thecalltaker.wd.max.followup.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.max.followup</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-max-engine.py</string>
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
    <string>${WD_DIR}/wd-max-followup.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-max-followup-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Pipeline: Daily at midnight ───
cat > "$PLIST_DIR/com.thecalltaker.wd.max.pipeline.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.max.pipeline</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-max-engine.py</string>
        <string>pipeline</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-max-pipeline.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-max-pipeline-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Daily Report: 8:30 PM (offset from HVAC Max at 8pm) ───
cat > "$PLIST_DIR/com.thecalltaker.wd.max.report.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.max.report</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-max-engine.py</string>
        <string>report</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-max-report.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-max-report-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

echo "  WD-Max: 4 services configured"

# ═══════════════════════════════════════════
# WD-BEN — Sales Closer (Water Damage)
# ═══════════════════════════════════════════

echo "Setting up WD-Ben (Sales Closer)..."

# ─── Morning Briefing: 7:15 AM (offset from HVAC Ben at 7am) ───
cat > "$PLIST_DIR/com.thecalltaker.wd.ben.morning.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.ben.morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-ben-engine.py</string>
        <string>morning</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-ben-morning.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-ben-morning-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── SMS: Daily at 1:15 PM ───
cat > "$PLIST_DIR/com.thecalltaker.wd.ben.sms.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.ben.sms</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-ben-engine.py</string>
        <string>sms</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>13</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-ben-sms.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-ben-sms-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Re-engagement: Daily at 2:15 PM ───
cat > "$PLIST_DIR/com.thecalltaker.wd.ben.reengage.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.ben.reengage</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-ben-engine.py</string>
        <string>reengage</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>14</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-ben-reengage.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-ben-reengage-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Lead Scoring: Daily at 3:15 PM ───
cat > "$PLIST_DIR/com.thecalltaker.wd.ben.score.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.ben.score</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-ben-engine.py</string>
        <string>score</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>15</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-ben-score.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-ben-score-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# ─── Evening Summary: 9:15 PM ───
cat > "$PLIST_DIR/com.thecalltaker.wd.ben.evening.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.wd.ben.evening</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${WD_DIR}/wd-ben-engine.py</string>
        <string>evening</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${WD_DIR}/wd-ben-evening.log</string>
    <key>StandardErrorPath</key>
    <string>${WD_DIR}/wd-ben-evening-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/usr/local/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

echo "  WD-Ben: 5 services configured"
echo ""

# ═══════════════════════════════════════════
# LOAD INTO LAUNCHD
# ═══════════════════════════════════════════

echo "Loading Water Damage Bots into launchd..."

# Unload old versions if they exist
for svc in monitor followup pipeline report; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.wd.max.$svc.plist" 2>/dev/null
done
for svc in morning sms reengage score evening; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.wd.ben.$svc.plist" 2>/dev/null
done

# Load WD-Max (4 services)
for svc in monitor followup pipeline report; do
    launchctl load "$PLIST_DIR/com.thecalltaker.wd.max.$svc.plist"
done

# Load WD-Ben (5 services)
for svc in morning sms reengage score evening; do
    launchctl load "$PLIST_DIR/com.thecalltaker.wd.ben.$svc.plist"
done

echo ""
echo "═══════════════════════════════════════════"
echo "  WATER DAMAGE BOTS ARE LIVE"
echo "═══════════════════════════════════════════"
echo ""
echo "WD-MAX Schedule (Reply Catcher):"
echo "  - Reply monitor:     Every 30 minutes"
echo "  - Warm follow-ups:   Daily at 9:00 AM"
echo "  - Pipeline manager:  Daily at 12:15 AM"
echo "  - Daily report:      Daily at 8:30 PM"
echo ""
echo "WD-BEN Schedule (Sales Closer):"
echo "  - Morning briefing:  Daily at 7:15 AM"
echo "  - SMS outreach:      Daily at 1:15 PM"
echo "  - Re-engagement:     Daily at 2:15 PM"
echo "  - Lead scoring:      Daily at 3:15 PM"
echo "  - Evening summary:   Daily at 9:15 PM"
echo ""
echo "NOTE: All times offset 15 min from HVAC bots to avoid conflicts."
echo ""
echo "Commands:"
echo "  WD-Max status:  python3 $WD_DIR/wd-max-engine.py status"
echo "  WD-Ben status:  python3 $WD_DIR/wd-ben-engine.py status"
echo "  WD-Max logs:    cat $WD_DIR/wd-max-log.txt"
echo "  WD-Ben logs:    cat $WD_DIR/wd-ben-log.txt"
echo "  Stop all:       bash $WD_DIR/uninstall-wd-bots.sh"
echo ""
echo "Water damage bots — never miss a $5,000+ restoration call."
