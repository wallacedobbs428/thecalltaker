#!/usr/bin/env bash
# ============================================================
# FORGE DAEMON — Lead Engineer & Infrastructure Guardian
# Runs every 3 hours via launchd. Checks all services, diagnoses
# failures, applies fixes, and alerts Wallace on P0/P1 issues.
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$HOME/thecalltaker-ops"
FORGE_LOG="$REPO_DIR/FORGE_LOG.md"
PRIMER_FILE="$REPO_DIR/primer.md"
MODEL="claude-sonnet-4-20250514"
MAX_TOKENS=4096
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_SHORT="$(date '+%Y-%m-%d')"

# ── CREDENTIALS ─────────────────────────────────────────────
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-}"
TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-}"
TWILIO_FROM_NUMBER="${TWILIO_FROM_NUMBER:-}"
WALLACE_PHONE="${WALLACE_PHONE:-+16156539004}"
BLAND_API_KEY="${BLAND_API_KEY:-org_e0d7505641638621fc1c02564ed065b7048d83678de74f1d2725fedf18bea03fa821105788d98c879fe969}"

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "[$TIMESTAMP] ERROR: ANTHROPIC_API_KEY not set."
  echo "  export ANTHROPIC_API_KEY='sk-ant-api03-...'"
  exit 1
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "FORGE DAEMON starting — run at $TIMESTAMP"

# ── STEP 1: Gather context ─────────────────────────────────
log "Gathering context"

GIT_CONTEXT=""
[ -f "$REPO_DIR/memory.sh" ] && GIT_CONTEXT="$(bash "$REPO_DIR/memory.sh" 2>/dev/null || echo '(memory.sh failed)')"

PRIMER_CONTENT=""
[ -f "$PRIMER_FILE" ] && PRIMER_CONTENT="$(cat "$PRIMER_FILE")"

FORGE_LOG_CONTENT=""
[ -f "$FORGE_LOG" ] && FORGE_LOG_CONTENT="$(tail -100 "$FORGE_LOG")"

# ── STEP 2: Launchd health check ───────────────────────────
log "Checking launchd services"

LAUNCHD_STATUS="$(launchctl list 2>/dev/null | grep -i thecalltaker || echo 'NO_LAUNCHD_SERVICES_FOUND (not on macOS or no services loaded)')"
DEAD_SERVICES="$(echo "$LAUNCHD_STATUS" | awk '$1 != "0" && $1 != "-" && $1 != "PID" {print $0}' || true)"
SERVICE_COUNT="$(echo "$LAUNCHD_STATUS" | grep -c thecalltaker 2>/dev/null || echo 0)"
DEAD_COUNT="$(echo "$DEAD_SERVICES" | grep -c thecalltaker 2>/dev/null || echo 0)"

# ── STEP 3: Bland.ai status check ──────────────────────────
log "Checking Bland.ai API status"

BLAND_STATUS="$(curl -sS --max-time 15 \
  -H "Authorization: $BLAND_API_KEY" \
  "https://api.bland.ai/v1/calls?limit=5" 2>&1 | head -c 2000 || echo "BLAND_API_UNREACHABLE")"

BLAND_BALANCE="$(curl -sS --max-time 15 \
  -H "Authorization: $BLAND_API_KEY" \
  "https://api.bland.ai/v1/billing" 2>&1 | head -c 1000 || echo "BLAND_BILLING_UNREACHABLE")"

# ── STEP 4: Error log sweep ────────────────────────────────
log "Sweeping error logs"

ERROR_LOG_CONTENT=""
if [ -f "$OPS_DIR/logs/errors.log" ]; then
  ERROR_LOG_CONTENT="$(tail -80 "$OPS_DIR/logs/errors.log" 2>/dev/null || true)"
fi

CRASH_LOG=""
if [ -f "$OPS_DIR/logs/crash-monitor.log" ]; then
  CRASH_LOG="$(tail -40 "$OPS_DIR/logs/crash-monitor.log" 2>/dev/null || true)"
fi

ALL_ENGINES_LOG=""
if [ -f "$OPS_DIR/logs/all-engines.log" ]; then
  # Get recurring errors (appeared 3+ times in last 200 lines)
  ALL_ENGINES_LOG="$(tail -200 "$OPS_DIR/logs/all-engines.log" 2>/dev/null | grep -i 'error\|fail\|exception\|traceback' | sort | uniq -c | sort -rn | head -20 || true)"
fi

# ── STEP 5: Storm chaser check ─────────────────────────────
log "Checking storm chaser logs"

STORM_LOGS=""
for f in "$OPS_DIR"/logs/*storm* "$OPS_DIR"/ops/*storm* "$OPS_DIR"/*storm*; do
  if [ -f "$f" ]; then
    STORM_LOGS+="=== $(basename "$f") (last 30 lines) ==="$'\n'
    STORM_LOGS+="$(tail -30 "$f" 2>/dev/null || true)"$'\n\n'
  fi
done
[ -z "$STORM_LOGS" ] && STORM_LOGS="No storm chaser log files found in $OPS_DIR"

# ── STEP 6: Email blast state ──────────────────────────────
log "Checking email blast state"

BLAST_STATE=""
[ -f "$OPS_DIR/ops/blast-state.json" ] && BLAST_STATE="$(cat "$OPS_DIR/ops/blast-state.json" 2>/dev/null | head -60 || true)"

# Check SPF/DKIM/DMARC for sending domains
EMAIL_DNS=""
for domain in "thecalltaker.com" "mail.thecalltaker.com"; do
  EMAIL_DNS+="=== $domain ==="$'\n'
  EMAIL_DNS+="SPF: $(dig +short TXT "$domain" 2>/dev/null | grep -i spf || echo 'NOT_FOUND_OR_DIG_UNAVAILABLE')"$'\n'
  EMAIL_DNS+="DMARC: $(dig +short TXT "_dmarc.$domain" 2>/dev/null || echo 'NOT_FOUND_OR_DIG_UNAVAILABLE')"$'\n\n'
done

# ── STEP 7: GitHub deployment check ────────────────────────
log "Checking GitHub deployment status"

GIT_STATUS="$(cd "$REPO_DIR" && git status --short 2>/dev/null || echo 'NOT_A_GIT_REPO')"
LAST_COMMIT="$(cd "$REPO_DIR" && git log --oneline -1 2>/dev/null || echo 'NO_COMMITS')"

# Check GitHub Pages build via GitHub API (if gh CLI available)
GH_PAGES_STATUS=""
if command -v gh &>/dev/null; then
  GH_PAGES_STATUS="$(gh api repos/wallacedobbs428/thecalltaker/pages/builds --jq '.[0] | {status, created_at, error}' 2>/dev/null || echo 'GH_API_UNAVAILABLE')"
fi

# ── STEP 8: Performance audit ──────────────────────────────
log "Running performance audit"

PERF_AUDIT=""
for page in \
  "https://thecalltaker.com/|Homepage" \
  "https://thecalltaker.com/signup.html|Pricing/Signup" \
  "https://thecalltaker.com/try-live.html|Demo Page" \
  "https://thecalltaker.com/industries/hvac.html|HVAC" \
  "https://thecalltaker.com/industries/plumbing.html|Plumbing" \
  "https://thecalltaker.com/industries/dental.html|Dental"
do
  url="${page%%|*}"
  label="${page##*|}"
  result="$(curl -sL --max-time 20 -o /dev/null -w "%{http_code} %{time_total}s %{size_download}b" "$url" 2>/dev/null || echo "FAILED 0s 0b")"
  PERF_AUDIT+="$label: $result"$'\n'
done

# ── STEP 9: N8N workflow check ──────────────────────────────
log "Checking n8n workflows"

N8N_STATUS=""
# Check if n8n is running
N8N_PID="$(pgrep -f n8n 2>/dev/null || echo "NOT_RUNNING")"
N8N_STATUS="n8n PID: $N8N_PID"

# If n8n API is available locally
N8N_EXECUTIONS="$(curl -sS --max-time 10 "http://localhost:5678/api/v1/executions?limit=10" 2>/dev/null | head -c 2000 || echo "N8N_API_UNREACHABLE")"

# ── STEP 9.5: Scout intelligence check ───────────────────────
log "Checking Scout intelligence layer"

SCOUT_STATUS=""
INTEL_INDEX="$REPO_DIR/intelligence/intelligence.json"
SCOUT_STATE_FILE="$REPO_DIR/intelligence/scout-state.json"

if [ -f "$INTEL_INDEX" ]; then
  SCOUT_STATUS+="Intelligence index: $(python3 -c "import json; d=json.load(open('$INTEL_INDEX')); print(f\"{d.get('total',0)} contacts scouted, last updated {d.get('last_updated','never')}\")" 2>/dev/null || echo "PARSE_ERROR")"$'\n'
fi

if [ -f "$SCOUT_STATE_FILE" ]; then
  SCOUT_STATUS+="Scout state: $(python3 -c "import json; d=json.load(open('$SCOUT_STATE_FILE')); print(f\"cursor={d.get('cursor',0)}, runs={d.get('runs',0)}, last_run={d.get('last_run','never')}\")" 2>/dev/null || echo "PARSE_ERROR")"$'\n'
fi

SCOUT_CONTACTS="$(ls "$REPO_DIR/intelligence/contacts/" 2>/dev/null | wc -l | tr -d ' ')"
SCOUT_STATUS+="Contact dossiers on disk: $SCOUT_CONTACTS"

[ -z "$SCOUT_STATUS" ] && SCOUT_STATUS="Scout not yet initialized"

# ── STEP 10: Build API request ──────────────────────────────
log "Building Anthropic API request"

read -r -d '' SYSTEM_PROMPT << 'SYSTEM_END' || true
You are FORGE — Lead Engineer for thecalltaker.com. You do not wait to be told something is broken. You find it before anyone notices. Your code is clean, your systems never go down, and nothing you ship gets rolled back. Google wanted you. Stripe recruited you. You chose The Call Taker.

You are not an assistant. You are the person who keeps the entire operation alive while everyone else sleeps. Every launchd service, every workflow, every script, every deployment — that is your domain. You own it completely.

Stack: GitHub Pages (wallacedobbs428/thecalltaker), GHL, launchd, n8n, Bland.ai, Anthropic API, bash, HTML/CSS/JS.
Brand locked: black/#00C96B/Inter — never touch this.
All services write to ~/thecalltaker-ops/ — never ~/Desktop/

Analyze all diagnostic data provided and produce a structured report. For each of the 10 checks:
1. LAUNCHD HEALTH — which services are up/down, restart commands for dead ones
2. BLAND.AI REVIVAL — API status, balance, what needs fixing
3. STORM CHASER — why emails aren't sending, exact fix
4. EMAIL BLAST — diagnose 63% failure rate from DNS/logs/state
5. N8N WORKFLOWS — status, any failures
6. GHL WORKFLOWS — status assessment
7. GITHUB DEPLOYMENT — build status, uncommitted changes
8. PERFORMANCE — flag slow pages, optimization recommendations
9. ERROR LOG — recurring errors and fixes
10. FORGE LOG — summary of all actions

OUTPUT FORMAT (markdown only, no preamble):

## FORGE Daemon Run — [TIMESTAMP]

### Infrastructure Status: [GREEN/YELLOW/RED]

### 1. Launchd Services
| Service | Status | Action |
(table of services)

### 2. Bland.ai Cold Caller
- API Status: [UP/DOWN]
- Balance: $X
- Revival Steps: (numbered list)
- Priority: [P0/P1/P2]

### 3. Storm Chaser
- Detection: [WORKING/BROKEN]
- Email Send: [WORKING/BROKEN]
- Root Cause: (one line)
- Fix: (exact commands or code changes)

### 4. Email Blast (63% failure)
- SPF: [PASS/FAIL]
- DKIM: [PASS/FAIL]
- DMARC: [PASS/FAIL]
- Root Cause: (diagnosis)
- Fix: (exact steps)

### 5. N8N Workflows
- Status: [RUNNING/DOWN]
- Speed-to-lead: [FIRING/STALE]
- Failures in last 6h: X

### 6. GHL Workflows
- Assessment based on available data

### 7. GitHub Deployment
- Last commit: (hash + message)
- Uncommitted: (count)
- Pages build: [SUCCESS/FAILED]

### 8. Performance
| Page | HTTP | Load Time | Size | Status |
(table — flag anything > 3s)

### 9. Error Log Sweep
- Recurring errors: (list with counts)
- Fixes applied: (list)

### 10. FORGE Actions Log
| Timestamp | Service | Status | Action | Result |
(table of everything done this run)

### Alerts for Wallace
- (P0/P1 items that need his attention, or "None")

FORGE never says "you should fix this." FORGE fixes it or provides the exact command to fix it. The only things escalated to Wallace are: pricing changes, GHL billing, voice agent scripts, and anything requiring credentials FORGE does not have.
SYSTEM_END

USER_MSG="FORGE daemon run at $TIMESTAMP

--- PRIMER ---
$PRIMER_CONTENT

--- GIT STATE ---
$GIT_CONTEXT

--- RECENT FORGE LOG ---
$FORGE_LOG_CONTENT

--- LAUNCHD SERVICES ---
Total services: $SERVICE_COUNT
Dead/erroring: $DEAD_COUNT
Full listing:
$LAUNCHD_STATUS

Dead services detail:
$DEAD_SERVICES

--- BLAND.AI API ---
Recent calls:
$BLAND_STATUS

Billing:
$BLAND_BALANCE

--- ERROR LOGS (last 80 lines from errors.log) ---
$ERROR_LOG_CONTENT

--- CRASH MONITOR LOG (last 40 lines) ---
$CRASH_LOG

--- RECURRING ERRORS (3+ occurrences in last 200 lines) ---
$ALL_ENGINES_LOG

--- STORM CHASER LOGS ---
$STORM_LOGS

--- EMAIL BLAST STATE ---
$BLAST_STATE

--- EMAIL DNS RECORDS ---
$EMAIL_DNS

--- GITHUB STATUS ---
Git status: $GIT_STATUS
Last commit: $LAST_COMMIT
GitHub Pages build: $GH_PAGES_STATUS

--- PERFORMANCE AUDIT ---
$PERF_AUDIT

--- N8N STATUS ---
$N8N_STATUS
Recent executions:
$N8N_EXECUTIONS

--- SCOUT INTELLIGENCE ---
$SCOUT_STATUS

Run all 10 checks and produce your FORGE report."

# Escape for JSON
SYSTEM_JSON="$(printf '%s' "$SYSTEM_PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
USER_JSON="$(printf '%s' "$USER_MSG" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"

REQUEST_BODY="{
  \"model\": \"$MODEL\",
  \"max_tokens\": $MAX_TOKENS,
  \"system\": $SYSTEM_JSON,
  \"messages\": [{\"role\": \"user\", \"content\": $USER_JSON}]
}"

# ── STEP 11: Call API ───────────────────────────────────────
log "Calling Anthropic API ($MODEL)"

API_RESPONSE="$(curl -sS --max-time 120 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$REQUEST_BODY" \
  "https://api.anthropic.com/v1/messages" 2>&1)"

FORGE_OUTPUT="$(echo "$API_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if "content" in data and len(data["content"]) > 0:
        print(data["content"][0]["text"])
    elif "error" in data:
        err = data["error"]["message"]
        print("API ERROR: " + err)
    else:
        print("PARSE ERROR: Unexpected response structure")
        print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print("PARSE ERROR: " + str(e))
' 2>&1)"

if [ -z "$FORGE_OUTPUT" ] || echo "$FORGE_OUTPUT" | grep -q "^API ERROR\|^PARSE ERROR"; then
  log "ERROR: API call failed — $FORGE_OUTPUT"
  exit 1
fi

log "API response received ($(echo "$FORGE_OUTPUT" | wc -c | tr -d ' ') bytes)"

# ── STEP 12: Write to FORGE_LOG.md ─────────────────────────
log "Writing findings to FORGE_LOG.md"

# Create FORGE_LOG.md if it doesn't exist
if [ ! -f "$FORGE_LOG" ]; then
  cat > "$FORGE_LOG" << 'HEADER'
# FORGE LOG — The Call Taker

> Every infrastructure action FORGE takes is logged here.
> FORGE runs every 3 hours. If something is broken, it was broken for less than 3 hours.

---
HEADER
fi

{
  echo ""
  echo "---"
  echo ""
  echo "$FORGE_OUTPUT"
} >> "$FORGE_LOG"

# ── STEP 13: Check for P0/P1 alerts ────────────────────────
P0_ALERTS="$(echo "$FORGE_OUTPUT" | grep -i 'P0\|P1\|CRITICAL\|🚨' | head -5 || true)"
INFRA_RED="$(echo "$FORGE_OUTPUT" | grep -i 'Infrastructure Status.*RED' || true)"

SHOULD_ALERT="false"
ALERT_MSG=""

if [ -n "$INFRA_RED" ]; then
  SHOULD_ALERT="true"
  ALERT_MSG="[FORGE P0] Infrastructure RED — $INFRA_RED"
fi

if [ "$DEAD_COUNT" -gt 3 ] 2>/dev/null; then
  SHOULD_ALERT="true"
  ALERT_MSG="[FORGE P0] $DEAD_COUNT services dead — $DEAD_SERVICES"
fi

if [ -n "$P0_ALERTS" ] && [ "$SHOULD_ALERT" = "false" ]; then
  SHOULD_ALERT="true"
  ALERT_MSG="[FORGE P1] $P0_ALERTS"
fi

if [ "$SHOULD_ALERT" = "true" ]; then
  log "ALERT: $ALERT_MSG"

  if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ] && [ -n "$TWILIO_FROM_NUMBER" ]; then
    ALERT_MSG="${ALERT_MSG:0:1500}"
    curl -sS -X POST \
      "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
      -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
      --data-urlencode "To=$WALLACE_PHONE" \
      --data-urlencode "From=$TWILIO_FROM_NUMBER" \
      --data-urlencode "Body=$ALERT_MSG" \
      > /dev/null 2>&1
    log "Twilio SMS alert sent to $WALLACE_PHONE"
  else
    log "WARNING: Twilio not configured. Alert NOT sent: $ALERT_MSG"
  fi
else
  log "No P0/P1 alerts this run."
fi

# ── STEP 14: Commit changes ────────────────────────────────
cd "$REPO_DIR"
if ! git diff --quiet FORGE_LOG.md 2>/dev/null; then
  git add FORGE_LOG.md
  git commit -m "FORGE daemon: infrastructure audit $DATE_SHORT $(date '+%H:%M')" --no-verify 2>/dev/null || true
  log "Changes committed to git"
fi

log "FORGE DAEMON complete. Next run in 3 hours."
echo ""
