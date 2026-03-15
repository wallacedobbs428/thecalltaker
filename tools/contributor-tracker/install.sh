#!/bin/bash
# Install the 'calltaker' CLI command

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TRACKER="$SCRIPT_DIR/tracker.py"

# Create ~/thecalltaker-ops/contributor-tracker/ directory
mkdir -p ~/thecalltaker-ops/contributor-tracker

# Create the calltaker command
BINDIR="/usr/local/bin"
if [ ! -w "$BINDIR" ]; then
    BINDIR="$HOME/.local/bin"
    mkdir -p "$BINDIR"
fi

cat > "$BINDIR/calltaker" << EOF
#!/bin/bash
python3 "$TRACKER" "\$@"
EOF

chmod +x "$BINDIR/calltaker"
chmod +x "$TRACKER"

echo "Installed: calltaker command"
echo "Location: $BINDIR/calltaker"
echo ""
echo "Commands:"
echo "  calltaker whoami          — Set active user"
echo "  calltaker log \"task\"      — Log a manual task"
echo "  calltaker payday 5000    — Calculate revenue split"
echo "  calltaker score           — Show current scores"
echo "  calltaker history         — Show recent activity"
echo "  calltaker backfill        — Import Git history"
echo "  calltaker dashboard       — Generate HTML dashboard"
echo "  calltaker export          — Export to CSV"
echo "  calltaker status          — System status"
echo ""
echo "Run 'calltaker backfill' first to import Git history!"
