#!/usr/bin/env bash
# start-all-loops.sh — Start all 4 Claude Code monitoring loops
# Usage: bash start-all-loops.sh
#
# Starts:
#   /loop 5m  /oracle-scanner    — Score and tag hot leads
#   /loop 15m /outreach-engine   — Draft and send outreach
#   /loop 5m  /payment-monitor   — Track payments, escalate stalls
#   /loop 30m /health-monitor    — System health checks
#
# Install: cp start-all-loops.sh ~/thecalltaker-ops/start-all-loops.sh

set -euo pipefail

LOG_DIR="${HOME}/thecalltaker-ops/logs"
mkdir -p "$LOG_DIR"

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[$TS] Starting all 4 monitoring loops..." | tee -a "$LOG_DIR/loops.log"

echo ""
echo "=== The Call Taker — Loop Activation ==="
echo ""
echo "Run these commands in your Claude Code session:"
echo ""
echo "  /loop 5m /oracle-scanner"
echo "  /loop 15m /outreach-engine"
echo "  /loop 5m /payment-monitor"
echo "  /loop 30m /health-monitor"
echo ""
echo "Or activate each one at a time with:"
echo ""
echo "  /oracle-scanner     (one-time scan)"
echo "  /outreach-engine    (one-time outreach run)"
echo "  /payment-monitor    (one-time payment check)"
echo "  /health-monitor     (one-time health check)"
echo ""
echo "=== Loop Descriptions ==="
echo ""
echo "oracle-scanner (5m):  Scores oracle-hot leads 1-100, tags 90+ as oracle-critical"
echo "outreach-engine (15m): Drafts personalized email+SMS for uncontacted critical leads"
echo "payment-monitor (5m): Tracks payment-pending, escalates stalls, celebrates conversions"
echo "health-monitor (30m): Checks services, proxy, Bland.ai, intel freshness, error rates"
echo ""
echo "[$TS] All loop commands printed. Paste them into Claude Code to activate." | tee -a "$LOG_DIR/loops.log"
