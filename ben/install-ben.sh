#!/bin/bash
# ═══════════════════════════════════════════
# BEN INSTALLER — Senior Sales Closer, 24/7
# Run once: bash install-ben.sh
# ═══════════════════════════════════════════

BEN_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PYTHON="/usr/bin/python3"

echo "Installing Ben — The Call Taker's Senior Sales Closer"
echo "======================================================"

chmod +x "$BEN_DIR/ben-engine.py"
mkdir -p "$PLIST_DIR"

# ─── Morning Briefing: 7:00 AM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.morning.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>morning</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-morning.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

# ─── Cold Outreach (ROI angle): 11:00 AM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.outreach.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.outreach</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>outreach</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-outreach.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

# ─── SMS Outreach: 1:00 PM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.sms.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.sms</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>sms</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-sms.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

# ─── Re-engagement: 2:00 PM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.reengage.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.reengage</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>reengage</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-reengage.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

# ─── Lead Scoring: 3:00 PM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.score.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.score</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>score</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-score.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

# ─── Evening Summary: 9:00 PM ───
cat > "$PLIST_DIR/com.thecalltaker.ben.evening.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thecalltaker.ben.evening</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${BEN_DIR}/ben-engine.py</string>
        <string>evening</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>${BEN_DIR}/ben-evening.log</string>
    <key>StandardErrorPath</key><string>${BEN_DIR}/ben-error.log</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/usr/bin:/usr/local/bin:/bin</string></dict>
</dict>
</plist>
PLIST

echo ""
echo "Loading Ben into launchd..."

for svc in morning outreach sms reengage score evening; do
    launchctl unload "$PLIST_DIR/com.thecalltaker.ben.$svc.plist" 2>/dev/null
done

for svc in morning outreach sms reengage score evening; do
    launchctl load "$PLIST_DIR/com.thecalltaker.ben.$svc.plist"
done

echo ""
echo "BEN IS LIVE. Schedule:"
echo "  7:00 AM  — Morning briefing to Wallace"
echo "  11:00 AM — Cold outreach (ROI/competition angles)"
echo "  1:00 PM  — SMS blasts (when A2P approves)"
echo "  2:00 PM  — Re-engage Max's cold leads"
echo "  3:00 PM  — Score all leads, flag hot ones"
echo "  9:00 PM  — Evening summary + tomorrow's plan"
echo ""
echo "Ben is online. The team grows stronger."
