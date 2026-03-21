#!/usr/bin/env bash
# ============================================================
# SCOUT DAEMON — Business Intelligence Researcher
# Runs every 4 hours via launchd. Pulls leads from master list,
# scouts them for business intel, and outputs dossiers to
# intelligence/contacts/<slug>.json
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SCOUT_SCRIPT="$REPO_DIR/agents/scout/scout.js"
LEADS_FILE="$REPO_DIR/leads/master-all-industries.json"
INTEL_DIR="$REPO_DIR/intelligence/contacts"
INTEL_INDEX="$REPO_DIR/intelligence/intelligence.json"
SCOUT_STATE="$REPO_DIR/intelligence/scout-state.json"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_SHORT="$(date '+%Y-%m-%d')"
MAX_PER_RUN=5

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] SCOUT_DAEMON: $1"
}

log "SCOUT DAEMON starting — $TIMESTAMP"

# ── Verify node exists ───────────────────────────────────────
if ! command -v node &>/dev/null; then
  log "ERROR: node not found in PATH"
  exit 1
fi

if [ ! -f "$SCOUT_SCRIPT" ]; then
  log "ERROR: scout.js not found at $SCOUT_SCRIPT"
  exit 1
fi

# ── Initialize state ────────────────────────────────────────
mkdir -p "$INTEL_DIR"

if [ ! -f "$SCOUT_STATE" ]; then
  echo '{"cursor": 0, "scouted": [], "runs": 0, "last_run": null}' > "$SCOUT_STATE"
fi

STATE="$(cat "$SCOUT_STATE")"
CURSOR="$(echo "$STATE" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("cursor",0))' 2>/dev/null || echo 0)"
RUNS="$(echo "$STATE" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("runs",0))' 2>/dev/null || echo 0)"

log "State: cursor=$CURSOR, runs=$RUNS"

# ── Load leads ──────────────────────────────────────────────
if [ ! -f "$LEADS_FILE" ]; then
  log "No master leads file found at $LEADS_FILE — running in manual mode only"
  exit 0
fi

TOTAL_LEADS="$(python3 -c "
import json
with open('$LEADS_FILE') as f:
    data = json.load(f)
leads = data if isinstance(data, list) else data.get('leads', [])
print(len(leads))
" 2>/dev/null || echo 0)"

log "Total leads in master list: $TOTAL_LEADS"

if [ "$TOTAL_LEADS" -eq 0 ]; then
  log "No leads to scout"
  exit 0
fi

# ── Scout next batch ────────────────────────────────────────
SCOUTED=0

for i in $(seq 0 $((MAX_PER_RUN - 1))); do
  IDX=$(( (CURSOR + i) % TOTAL_LEADS ))

  # Extract lead data
  LEAD_DATA="$(python3 -c "
import json
with open('$LEADS_FILE') as f:
    data = json.load(f)
leads = data if isinstance(data, list) else data.get('leads', [])
lead = leads[$IDX]
name = lead.get('name', lead.get('business_name', ''))
loc = lead.get('location', lead.get('city', ''))
if lead.get('state'):
    loc = loc + ', ' + lead['state'] if loc else lead['state']
phone = lead.get('phone', '')
website = lead.get('website', lead.get('url', ''))
industry = lead.get('industry', '')
print(json.dumps({'name': name, 'location': loc, 'phone': phone, 'website': website, 'industry': industry}))
" 2>/dev/null)"

  if [ -z "$LEAD_DATA" ]; then
    log "  Skip index $IDX — could not parse lead"
    continue
  fi

  NAME="$(echo "$LEAD_DATA" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["name"])')"
  LOCATION="$(echo "$LEAD_DATA" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["location"])')"
  PHONE="$(echo "$LEAD_DATA" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["phone"])')"
  WEBSITE="$(echo "$LEAD_DATA" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["website"])')"
  INDUSTRY="$(echo "$LEAD_DATA" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["industry"])')"

  if [ -z "$NAME" ]; then
    log "  Skip index $IDX — no business name"
    continue
  fi

  # Check if already scouted
  SLUG="$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')"
  if [ -f "$INTEL_DIR/$SLUG.json" ]; then
    log "  Skip: $NAME (already scouted)"
    continue
  fi

  log "  Scouting ($((i+1))/$MAX_PER_RUN): $NAME"

  # Build args
  ARGS=("$NAME")
  [ -n "$LOCATION" ] && ARGS+=(--location "$LOCATION")
  [ -n "$PHONE" ] && ARGS+=(--phone "$PHONE")
  [ -n "$WEBSITE" ] && ARGS+=(--website "$WEBSITE")
  [ -n "$INDUSTRY" ] && ARGS+=(--industry "$INDUSTRY")

  if node "$SCOUT_SCRIPT" "${ARGS[@]}" 2>&1; then
    SCOUTED=$((SCOUTED + 1))
  else
    log "  ERROR scouting $NAME"
  fi

  # Rate limit — 3 seconds between scouts
  sleep 3
done

# ── Update state ────────────────────────────────────────────
NEW_CURSOR=$(( (CURSOR + MAX_PER_RUN) % TOTAL_LEADS ))
NEW_RUNS=$((RUNS + 1))

python3 -c "
import json
state = json.load(open('$SCOUT_STATE'))
state['cursor'] = $NEW_CURSOR
state['runs'] = $NEW_RUNS
state['last_run'] = '$TIMESTAMP'
state['last_scouted'] = $SCOUTED
with open('$SCOUT_STATE', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null

log "Done. Scouted $SCOUTED businesses. Cursor advanced to $NEW_CURSOR."
log "SCOUT DAEMON complete. Next run in 4 hours."
