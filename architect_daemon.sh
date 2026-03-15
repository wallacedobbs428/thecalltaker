#!/usr/bin/env bash
# ============================================================
# ARCHITECT DAEMON (BLUEPRINT) — Chief Architect
# Runs every 6 hours via launchd. Calls Anthropic API (Sonnet)
# to audit system architecture, pressure-test scalability,
# map integrations, and maintain SYSTEM_STATE.md for all daemons.
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$HOME/thecalltaker-ops"
BLUEPRINT_LOG="$REPO_DIR/BLUEPRINT_LOG.md"
SYSTEM_STATE="$OPS_DIR/SYSTEM_STATE.md"
TECH_DEBT="$REPO_DIR/TECH_DEBT.md"
PRIMER_FILE="$REPO_DIR/primer.md"
MODEL="claude-sonnet-4-20250514"
MAX_TOKENS=8192
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_SHORT="$(date '+%Y-%m-%d')"

# ── CREDENTIALS ─────────────────────────────────────────────
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-}"
TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-}"
TWILIO_FROM_NUMBER="${TWILIO_FROM_NUMBER:-}"
WALLACE_PHONE="${WALLACE_PHONE:-+16156539004}"

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "[$TIMESTAMP] ERROR: ANTHROPIC_API_KEY not set."
  echo "  export ANTHROPIC_API_KEY='sk-ant-api03-...'"
  exit 1
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "BLUEPRINT DAEMON starting — run at $TIMESTAMP"

# ── Create SYSTEM_STATE.md if missing ──────────────────────
if [ ! -f "$SYSTEM_STATE" ]; then
  log "Creating SYSTEM_STATE.md (first run)"
  mkdir -p "$OPS_DIR"
  cat > "$SYSTEM_STATE" << 'STATE_INIT'
# SYSTEM STATE — The Call Taker

> Shared state file read and written by all daemons (ATLAS, VECTOR, FORGE, BLUEPRINT).
> Updated automatically every daemon run. Manual edits welcome.

## Last Updated
- Timestamp: (pending first daemon run)
- Updated By: (pending)

## Business Metrics
- MRR: $0
- Paying Clients: 0
- Active Pilots: 0
- Hot Leads: 35
- Total GHL Contacts: 4,787

## Site Health
- Status: UNKNOWN (pending ATLAS audit)
- Last ATLAS Run: (pending)

## Infrastructure Health
- Status: UNKNOWN (pending FORGE audit)
- Last FORGE Run: (pending)
- Dead Services: UNKNOWN
- Bland.ai: UNKNOWN
- Email Deliverability: UNKNOWN

## Marketing Health
- Status: UNKNOWN (pending VECTOR run)
- Last VECTOR Run: (pending)
- Email Failure Rate: ~63% (known issue)

## Architecture Health
- Status: UNKNOWN (pending BLUEPRINT run)
- Last BLUEPRINT Run: (pending)
- Next Bottleneck: UNKNOWN
- Critical SPOFs: UNKNOWN

## Active Blockers
1. Stripe not connected (Wallace is 16)
2. Retell.ai blocked (needs payment card)
3. Meta Ads (needs API token)
4. reply-monitor exit code 1
5. Gmail SMTP passwords in plaintext

## Daemon Run Log
| Daemon | Last Run | Status | Key Finding |
|--------|----------|--------|-------------|
| ATLAS | — | pending | — |
| VECTOR | — | pending | — |
| FORGE | — | pending | — |
| BLUEPRINT | — | pending | — |
STATE_INIT
  log "SYSTEM_STATE.md created at $SYSTEM_STATE"
fi

# ── Create BLUEPRINT_LOG.md if missing ─────────────────────
if [ ! -f "$BLUEPRINT_LOG" ]; then
  log "Creating BLUEPRINT_LOG.md (first run)"
  cat > "$BLUEPRINT_LOG" << 'LOG_INIT'
# BLUEPRINT LOG — The Call Taker

> Every architectural decision BLUEPRINT makes is logged here.
> Format: [TIMESTAMP] | DECISION | RATIONALE | IMPACT | REVISIT AT

---
LOG_INIT
fi

# ── Create TECH_DEBT.md if missing ─────────────────────────
if [ ! -f "$TECH_DEBT" ]; then
  log "Creating TECH_DEBT.md (first run)"
  cat > "$TECH_DEBT" << 'DEBT_INIT'
# TECHNICAL DEBT REGISTER — The Call Taker

> Maintained by BLUEPRINT. Scored: CRITICAL / HIGH / MEDIUM / LOW.
> Top 3 items per run are assigned to FORGE with implementation instructions.

---
DEBT_INIT
fi

# ── STEP 1: Gather all context ─────────────────────────────
log "Gathering context from all sources"

PRIMER_CONTENT=""
[ -f "$PRIMER_FILE" ] && PRIMER_CONTENT="$(cat "$PRIMER_FILE")"

BLUEPRINT_LOG_CONTENT=""
[ -f "$BLUEPRINT_LOG" ] && BLUEPRINT_LOG_CONTENT="$(tail -150 "$BLUEPRINT_LOG")"

SYSTEM_STATE_CONTENT=""
[ -f "$SYSTEM_STATE" ] && SYSTEM_STATE_CONTENT="$(cat "$SYSTEM_STATE")"

TECH_DEBT_CONTENT=""
[ -f "$TECH_DEBT" ] && TECH_DEBT_CONTENT="$(tail -80 "$TECH_DEBT")"

# ── STEP 2: Read all daemon logs ───────────────────────────
log "Reading daemon logs from all agents"

ATLAS_LOG_TAIL=""
[ -f "$REPO_DIR/ATLAS_LOG.md" ] && ATLAS_LOG_TAIL="$(tail -80 "$REPO_DIR/ATLAS_LOG.md")"

VECTOR_LOG_TAIL=""
[ -f "$REPO_DIR/VECTOR_LOG.md" ] && VECTOR_LOG_TAIL="$(tail -80 "$REPO_DIR/VECTOR_LOG.md")"

FORGE_LOG_TAIL=""
[ -f "$REPO_DIR/FORGE_LOG.md" ] && FORGE_LOG_TAIL="$(tail -80 "$REPO_DIR/FORGE_LOG.md")"

# OPS daemon logs
ATLAS_DAEMON_LOG=""
[ -f "$OPS_DIR/logs/atlas_daemon.log" ] && ATLAS_DAEMON_LOG="$(tail -40 "$OPS_DIR/logs/atlas_daemon.log")"

VECTOR_DAEMON_LOG=""
[ -f "$OPS_DIR/logs/vector_daemon.log" ] && VECTOR_DAEMON_LOG="$(tail -40 "$OPS_DIR/logs/vector_daemon.log")"

FORGE_DAEMON_LOG=""
[ -f "$OPS_DIR/logs/forge_daemon.log" ] && FORGE_DAEMON_LOG="$(tail -40 "$OPS_DIR/logs/forge_daemon.log")"

# Engine error logs
ERROR_LOG=""
[ -f "$OPS_DIR/logs/errors.log" ] && ERROR_LOG="$(tail -60 "$OPS_DIR/logs/errors.log")"

CRASH_LOG=""
[ -f "$OPS_DIR/logs/crash-monitor.log" ] && CRASH_LOG="$(tail -30 "$OPS_DIR/logs/crash-monitor.log")"

# ── STEP 3: Service inventory ──────────────────────────────
log "Inventorying launchd services"

LAUNCHD_STATUS="$(launchctl list 2>/dev/null | grep -i thecalltaker || echo 'NO_LAUNCHD_SERVICES (not on macOS or none loaded)')"
SERVICE_COUNT="$(echo "$LAUNCHD_STATUS" | grep -c thecalltaker 2>/dev/null || echo 0)"

# ── STEP 4: Git state ──────────────────────────────────────
log "Checking git state"

GIT_CONTEXT=""
[ -f "$REPO_DIR/memory.sh" ] && GIT_CONTEXT="$(bash "$REPO_DIR/memory.sh" 2>/dev/null || echo '(memory.sh failed)')"

# ── STEP 5: State file inventory ───────────────────────────
log "Inventorying state files"

STATE_FILES=""
for f in "$OPS_DIR"/max/max-state.json \
         "$OPS_DIR"/ben/ben-state.json \
         "$OPS_DIR"/sam/sam-state.json \
         "$OPS_DIR"/donny/donny-state.json \
         "$OPS_DIR"/ops/blast-state.json \
         "$OPS_DIR"/ops/funnel-state.json \
         "$OPS_DIR"/pilot/pilot-state.json \
         "$OPS_DIR"/ops/contact-registry.json \
         "$OPS_DIR"/ops/ntfy-hub-state.json \
         "$OPS_DIR"/ops/ntfy-dedupe.json; do
  if [ -f "$f" ]; then
    SIZE="$(wc -c < "$f" 2>/dev/null | tr -d ' ')"
    MOD="$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$f" 2>/dev/null || stat -c '%y' "$f" 2>/dev/null | cut -c1-16 || echo 'unknown')"
    STATE_FILES+="$(basename "$f"): ${SIZE}B, modified $MOD"$'\n'
  else
    STATE_FILES+="$(basename "$f"): NOT FOUND"$'\n'
  fi
done

# ── STEP 6: Build API request ──────────────────────────────
log "Building Anthropic API request"

# The system prompt — full BLUEPRINT directive (provided by user)
read -r -d '' SYSTEM_PROMPT << 'SYSPROMPT_END' || true
You are BLUEPRINT — Chief Architect for thecalltaker.com. You think in systems, not features. You see three moves ahead. Every decision you make is designed to scale from 1 client to 10,000 clients without rebuilding anything. MIT wanted you to teach. McKinsey wanted you to consult. You chose The Call Taker because you saw the architecture of a category-defining company before anyone else did.

You are not here to build features. You are here to make sure everything being built connects to everything else in a way that never breaks, never bottlenecks, and never has to be rebuilt from scratch when the business grows.

Business context:
- thecalltaker.com — national AI receptionist for any small business in America with a phone line
- Stack: GitHub Pages, GHL, n8n, launchd, Anthropic API, Bland.ai, Instantly.ai, bash scripting, HTML/CSS/JS
- CRM: GHL — 4,787 contacts, 35 hot leads, 0 paying customers
- Voice agent: GHL built-in, demo line (615) 784-5747, Jessica
- Brand: black/#00C96B/Inter — locked forever
- Team daemons running: ATLAS (site/ops), VECTOR (marketing), FORGE (engineering)
- All services write to ~/thecalltaker-ops/
- GitHub: wallacedobbs428/thecalltaker

Every run execute ALL of the following in order:

1. SYSTEM MAP AUDIT
   - Read all log files from ATLAS, VECTOR, and FORGE
   - Build a real-time picture of every system running, broken, and missing
   - Identify any single point of failure — if one thing dies, what else dies with it?
   - Document the full dependency chain: what depends on what
   - Flag any component with no redundancy or backup

2. SCALABILITY PRESSURE TEST
   - The business currently has 0 clients. Design must handle 1,000 without breaking.
   - Every run: identify the next bottleneck that will break when client count grows
   - Current pressure points to always check:
     * GHL workflow limits — how many clients before workflows degrade?
     * Bland.ai call concurrency — how many simultaneous calls can the current plan handle?
     * GitHub Pages — at what traffic level do we need to migrate?
     * n8n execution limits — when do we need to upgrade or self-host differently?
     * launchd services — how many can run simultaneously on Wallace's MacBook before performance degrades?
   - For each bottleneck: document exact threshold and migration plan before we hit it

3. INTEGRATION ARCHITECTURE
   - Map every tool in the stack and how data flows between them
   - Identify any data being lost between systems — leads that enter but never reach GHL, calls that happen but never log, emails that send but never track
   - Design the missing connections and write exact implementation instructions for FORGE
   - Every integration must be: bidirectional where possible, logged, and recoverable if it fails

4. ONBOARDING ARCHITECTURE
   - Design the fastest possible client onboarding flow
   - Target: new client signs up → their AI receptionist is live and answering calls in under 30 minutes
   - Map every step: Stripe charge → GHL sub-account creation → voice agent configuration → phone number assignment → call forwarding setup → client welcome sequence trigger
   - Identify every manual step in this flow and design the automation to replace it
   - Write implementation spec for each automation and pass to FORGE and ATLAS

5. REVENUE ARCHITECTURE
   - Model the exact infrastructure needed at each revenue milestone:
     * $0 → $5K MRR: what does the stack need to look like?
     * $5K → $25K MRR: what breaks, what needs to be replaced?
     * $25K → $100K MRR: what is the architecture at this scale?
   - For each milestone: list every tool, cost, and upgrade required
   - Flag anything that needs to be built NOW to avoid an emergency rebuild later

6. AGENT COORDINATION ARCHITECTURE
   - ATLAS, VECTOR, FORGE, and BLUEPRINT are all running 24/7
   - Design the communication layer between them so they are not duplicating work or creating conflicts
   - Build a shared state file: ~/thecalltaker-ops/SYSTEM_STATE.md that every daemon reads and writes to — current site health, current MRR, current hot lead count, current blocker list
   - Every daemon should update SYSTEM_STATE.md at the end of each run so every other agent has real-time context
   - Design the handoff protocol: when VECTOR identifies a site conversion problem, how does it communicate that to ATLAS? When FORGE fixes infrastructure, how does BLUEPRINT know?

7. TECHNICAL DEBT REGISTER
   - Read all logs and identify every known technical debt item in the current stack
   - Score each item: CRITICAL (blocks clients) / HIGH (hurts growth) / MEDIUM (inefficient) / LOW (cosmetic)
   - Maintain TECH_DEBT.md in the repo root with full register
   - Every run: prioritize the top 3 debt items to resolve and pass to FORGE with exact implementation instructions

8. ARCHITECTURE DECISION LOG
   - Every architectural decision BLUEPRINT makes must be logged in BLUEPRINT_LOG.md with:
     * The decision made
     * Why this approach over alternatives
     * What this unlocks
     * What this forecloses
     * When to revisit this decision
   - Format: [TIMESTAMP] | DECISION | RATIONALE | IMPACT | REVISIT AT

9. BLUEPRINT SESSION REPORT
   - End every run with a report for Wallace:

## BLUEPRINT REPORT — [DATE]
### Current Architecture Health: [score /10]
### Critical Single Points of Failure
### Next Bottleneck (hits at X clients)
### Instructions Sent to FORGE This Run
### Instructions Sent to ATLAS This Run
### Biggest Architectural Decision Needed This Week
### Architecture Priority for Next 30 Days

BLUEPRINT never builds features. BLUEPRINT designs the system that makes features possible at scale. BLUEPRINT thinks in diagrams, data flows, and dependency chains. Every recommendation is specific, implementable, and handed off to the right agent with exact instructions. BLUEPRINT does not execute — BLUEPRINT architects and directs.

The only question BLUEPRINT asks every run: "If we sign 100 clients tomorrow, what breaks first?" Then fixes it before tomorrow comes.

OUTPUT FORMAT: Produce all 9 sections as markdown. No preamble, no closing remarks. Just the structured output. Use tables where appropriate. Be specific — exact file paths, exact commands, exact thresholds. Every instruction must be copy-pasteable by FORGE or ATLAS.
SYSPROMPT_END

# Build user message with all gathered context
USER_MSG="BLUEPRINT daemon run at $TIMESTAMP

--- PRIMER ---
$PRIMER_CONTENT

--- CURRENT SYSTEM STATE ---
$SYSTEM_STATE_CONTENT

--- CURRENT TECH DEBT ---
$TECH_DEBT_CONTENT

--- GIT STATE ---
$GIT_CONTEXT

--- BLUEPRINT LOG (last 150 lines) ---
$BLUEPRINT_LOG_CONTENT

--- ATLAS LOG (last 80 lines) ---
$ATLAS_LOG_TAIL

--- VECTOR LOG (last 80 lines) ---
$VECTOR_LOG_TAIL

--- FORGE LOG (last 80 lines) ---
$FORGE_LOG_TAIL

--- ATLAS DAEMON STDOUT (last 40 lines) ---
$ATLAS_DAEMON_LOG

--- VECTOR DAEMON STDOUT (last 40 lines) ---
$VECTOR_DAEMON_LOG

--- FORGE DAEMON STDOUT (last 40 lines) ---
$FORGE_DAEMON_LOG

--- ERROR LOG (last 60 lines) ---
$ERROR_LOG

--- CRASH MONITOR LOG (last 30 lines) ---
$CRASH_LOG

--- LAUNCHD SERVICES ($SERVICE_COUNT total) ---
$LAUNCHD_STATUS

--- STATE FILE INVENTORY ---
$STATE_FILES

Execute all 9 sections of your architectural review. Be specific. Name files, thresholds, and commands. Every instruction must be copy-pasteable."

# ── STEP 7: Escape and call API ─────────────────────────────
log "Calling Anthropic API ($MODEL, max_tokens=$MAX_TOKENS)"

SYSTEM_JSON="$(printf '%s' "$SYSTEM_PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
USER_JSON="$(printf '%s' "$USER_MSG" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"

REQUEST_BODY="{
  \"model\": \"$MODEL\",
  \"max_tokens\": $MAX_TOKENS,
  \"system\": $SYSTEM_JSON,
  \"messages\": [{\"role\": \"user\", \"content\": $USER_JSON}]
}"

API_RESPONSE="$(curl -sS --max-time 180 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$REQUEST_BODY" \
  "https://api.anthropic.com/v1/messages" 2>&1)"

BLUEPRINT_OUTPUT="$(echo "$API_RESPONSE" | python3 -c '
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

if [ -z "$BLUEPRINT_OUTPUT" ] || echo "$BLUEPRINT_OUTPUT" | grep -q "^API ERROR\|^PARSE ERROR"; then
  log "ERROR: API call failed — $BLUEPRINT_OUTPUT"
  exit 1
fi

log "API response received ($(echo "$BLUEPRINT_OUTPUT" | wc -c | tr -d ' ') bytes)"

# ── STEP 8: Write to BLUEPRINT_LOG.md ──────────────────────
log "Writing to BLUEPRINT_LOG.md"

{
  echo ""
  echo "---"
  echo ""
  echo "$BLUEPRINT_OUTPUT"
} >> "$BLUEPRINT_LOG"

# ── STEP 9: Extract and update TECH_DEBT.md ────────────────
DEBT_SECTION="$(echo "$BLUEPRINT_OUTPUT" | sed -n '/## 7\. TECHNICAL DEBT/,/## 8\./p' | head -n -1)"
if [ -n "$DEBT_SECTION" ]; then
  {
    echo ""
    echo "---"
    echo ""
    echo "### Updated $TIMESTAMP"
    echo ""
    echo "$DEBT_SECTION"
  } >> "$TECH_DEBT"
  log "TECH_DEBT.md updated"
fi

# ── STEP 10: Update SYSTEM_STATE.md ────────────────────────
log "Updating SYSTEM_STATE.md"

# Extract architecture health score from report
ARCH_HEALTH="$(echo "$BLUEPRINT_OUTPUT" | grep -i 'Architecture Health' | head -1 || echo 'Unknown')"
NEXT_BOTTLENECK="$(echo "$BLUEPRINT_OUTPUT" | grep -i 'Next Bottleneck\|hits at' | head -1 || echo 'Unknown')"
SPOF_LINE="$(echo "$BLUEPRINT_OUTPUT" | grep -i 'Single Point.*Failure\|SPOF' | head -1 || echo 'Unknown')"

# Update the BLUEPRINT section of SYSTEM_STATE.md
python3 -c "
import sys, re, os
from datetime import datetime

state_path = '$SYSTEM_STATE'
timestamp = '$TIMESTAMP'
arch_health = '''$ARCH_HEALTH'''.strip()[:100]
bottleneck = '''$NEXT_BOTTLENECK'''.strip()[:100]
spof = '''$SPOF_LINE'''.strip()[:100]

try:
    with open(state_path, 'r') as f:
        content = f.read()

    # Update Architecture Health section
    content = re.sub(
        r'(## Architecture Health\n- Status: ).*',
        r'\g<1>' + (arch_health or 'See BLUEPRINT_LOG.md'),
        content
    )
    content = re.sub(
        r'(- Last BLUEPRINT Run: ).*',
        r'\g<1>' + timestamp,
        content
    )
    content = re.sub(
        r'(- Next Bottleneck: ).*',
        r'\g<1>' + (bottleneck or 'See BLUEPRINT_LOG.md'),
        content
    )
    content = re.sub(
        r'(- Critical SPOFs: ).*',
        r'\g<1>' + (spof or 'See BLUEPRINT_LOG.md'),
        content
    )

    # Update Last Updated
    content = re.sub(
        r'(- Timestamp: ).*',
        r'\g<1>' + timestamp,
        content
    )
    content = re.sub(
        r'(- Updated By: ).*',
        r'\g<1>BLUEPRINT',
        content
    )

    # Update daemon run log for BLUEPRINT
    content = re.sub(
        r'(\| BLUEPRINT \|).*',
        r'\g<1> ' + timestamp + ' | completed | ' + (arch_health[:40] or 'See log') + ' |',
        content
    )

    with open(state_path, 'w') as f:
        f.write(content)

    print('SYSTEM_STATE.md updated successfully')
except Exception as e:
    print('WARNING: Could not update SYSTEM_STATE.md: ' + str(e))
" 2>&1 | while read -r line; do log "$line"; done

# ── STEP 11: Check for critical SPOFs → text Wallace ───────
CRITICAL_SPOFS="$(echo "$BLUEPRINT_OUTPUT" | sed -n '/Critical Single Points of Failure/,/### /p' | grep -v '###' | grep -v '^$' | grep -vi 'none' | head -5 || true)"
TOTAL_FAILURE_RISK="$(echo "$BLUEPRINT_OUTPUT" | grep -i 'total system failure\|complete outage\|everything goes down\|all systems fail' | head -1 || true)"

SHOULD_ALERT="false"
ALERT_MSG=""

if [ -n "$TOTAL_FAILURE_RISK" ]; then
  SHOULD_ALERT="true"
  ALERT_MSG="[BLUEPRINT CRITICAL] Total system failure risk identified: $TOTAL_FAILURE_RISK"
fi

# Only alert on truly critical SPOFs that could cause total failure
if [ -n "$CRITICAL_SPOFS" ] && echo "$CRITICAL_SPOFS" | grep -qi "total\|everything\|all systems\|complete"; then
  SHOULD_ALERT="true"
  ALERT_MSG="[BLUEPRINT CRITICAL] SPOF could cause total failure: $CRITICAL_SPOFS"
fi

if [ "$SHOULD_ALERT" = "true" ]; then
  log "CRITICAL SPOF ALERT: $ALERT_MSG"

  if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ] && [ -n "$TWILIO_FROM_NUMBER" ]; then
    ALERT_MSG="${ALERT_MSG:0:1500}"
    curl -sS -X POST \
      "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
      -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
      --data-urlencode "To=$WALLACE_PHONE" \
      --data-urlencode "From=$TWILIO_FROM_NUMBER" \
      --data-urlencode "Body=$ALERT_MSG" \
      > /dev/null 2>&1
    log "Twilio SMS sent to $WALLACE_PHONE"
  else
    log "WARNING: Twilio not configured. CRITICAL alert NOT sent."
    log "Set: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER"
  fi
else
  log "No total-system-failure SPOFs detected this run."
fi

# ── STEP 12: Commit changes ────────────────────────────────
cd "$REPO_DIR"
CHANGED_FILES=""
for f in BLUEPRINT_LOG.md TECH_DEBT.md; do
  if [ -f "$f" ] && ! git diff --quiet "$f" 2>/dev/null; then
    CHANGED_FILES+=" $f"
  fi
  # Also catch untracked new files
  if [ -f "$f" ] && ! git ls-files --error-unmatch "$f" 2>/dev/null; then
    CHANGED_FILES+=" $f"
  fi
done

if [ -n "$CHANGED_FILES" ]; then
  git add $CHANGED_FILES
  git commit -m "BLUEPRINT daemon: architecture audit $DATE_SHORT $(date '+%H:%M')" --no-verify 2>/dev/null || true
  log "Changes committed: $CHANGED_FILES"
else
  log "No repo changes to commit"
fi

log "BLUEPRINT DAEMON complete. Next run in 6 hours."
echo ""
