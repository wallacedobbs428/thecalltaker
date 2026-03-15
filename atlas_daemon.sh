#!/usr/bin/env bash
# ============================================================
# ATLAS DAEMON — Autonomous Technical Lead & Site Supervisor
# Runs every 4 hours via launchd. Calls Anthropic API (Sonnet)
# to audit thecalltaker.com and log findings to ATLAS_LOG.md.
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$HOME/thecalltaker-ops"
LOG_FILE="$REPO_DIR/ATLAS_LOG.md"
PRIMER_FILE="$REPO_DIR/primer.md"
MODEL="claude-sonnet-4-20250514"
MAX_TOKENS=4096
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_SHORT="$(date '+%Y-%m-%d')"

# ── CREDENTIALS (set these as environment variables) ────────
# export ANTHROPIC_API_KEY="sk-ant-..."
# export TWILIO_ACCOUNT_SID="AC..."
# export TWILIO_AUTH_TOKEN="..."
# export TWILIO_FROM_NUMBER="+1..."
# export WALLACE_PHONE="+16156539004"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-}"
TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-}"
TWILIO_FROM_NUMBER="${TWILIO_FROM_NUMBER:-}"
WALLACE_PHONE="${WALLACE_PHONE:-+16156539004}"

# ── PREFLIGHT CHECKS ───────────────────────────────────────
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "[$TIMESTAMP] ERROR: ANTHROPIC_API_KEY not set. Export it before running."
  echo "  export ANTHROPIC_API_KEY='sk-ant-api03-...'"
  exit 1
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "ATLAS DAEMON starting — run at $TIMESTAMP"

# ── STEP 1: Gather live context ────────────────────────────
log "Gathering context: memory.sh, primer.md, ATLAS_LOG.md"

GIT_CONTEXT=""
if [ -f "$REPO_DIR/memory.sh" ]; then
  GIT_CONTEXT="$(bash "$REPO_DIR/memory.sh" 2>/dev/null || echo '(memory.sh failed)')"
fi

PRIMER_CONTENT=""
if [ -f "$PRIMER_FILE" ]; then
  PRIMER_CONTENT="$(cat "$PRIMER_FILE")"
fi

ATLAS_LOG_CONTENT=""
if [ -f "$LOG_FILE" ]; then
  # Only send last 100 lines to keep token count manageable
  ATLAS_LOG_CONTENT="$(tail -100 "$LOG_FILE")"
fi

# ── STEP 2: Fetch key pages from thecalltaker.com ──────────
log "Fetching key pages from thecalltaker.com"

fetch_page() {
  local url="$1"
  local label="$2"
  local result
  result="$(curl -sL --max-time 15 -o /dev/null -w "URL: %{url_effective}\nHTTP: %{http_code}\nTime: %{time_total}s\nSize: %{size_download} bytes\nRedirects: %{num_redirects}" "$url" 2>/dev/null || echo "FETCH_FAILED")"
  echo "=== $label ($url) ==="
  echo "$result"
  echo ""
}

fetch_headers() {
  local url="$1"
  # Grab title, meta description, viewport from actual HTML
  local html
  html="$(curl -sL --max-time 15 "$url" 2>/dev/null | head -c 8000 || echo "")"
  local title desc viewport
  title="$(echo "$html" | grep -oi '<title>[^<]*</title>' | head -1 || echo "NO_TITLE")"
  desc="$(echo "$html" | grep -oi 'name="description"[^>]*>' | head -1 || echo "NO_META_DESC")"
  viewport="$(echo "$html" | grep -oi 'name="viewport"' | head -1 || echo "NO_VIEWPORT")"
  echo "Title: $title"
  echo "Meta Desc: ${desc:-MISSING}"
  echo "Viewport: ${viewport:-MISSING}"
}

SITE_AUDIT=""

# Core pages
for page in \
  "https://thecalltaker.com/|Homepage" \
  "https://thecalltaker.com/pilot/|Pilot Signup" \
  "https://thecalltaker.com/book.html|Book Demo" \
  "https://thecalltaker.com/try-live.html|Try Live Demo" \
  "https://thecalltaker.com/industries/hvac.html|Industry: HVAC" \
  "https://thecalltaker.com/industries/plumbing.html|Industry: Plumbing" \
  "https://thecalltaker.com/industries/dental.html|Industry: Dental" \
  "https://thecalltaker.com/blog/|Blog Index" \
  "https://thecalltaker.com/case-studies/|Case Studies" \
  "https://thecalltaker.com/calculator.html|ROI Calculator" \
  "https://thecalltaker.com/signup.html|Signup" \
  "https://thecalltaker.com/404.html|404 Page"
do
  url="${page%%|*}"
  label="${page##*|}"
  SITE_AUDIT+="$(fetch_page "$url" "$label")"
  SITE_AUDIT+="$(fetch_headers "$url")"
  SITE_AUDIT+=$'\n\n'
done

# ── STEP 3: Check competitor hero headlines ────────────────
log "Fetching competitor headlines"

fetch_competitor_hero() {
  local url="$1"
  local name="$2"
  local html
  html="$(curl -sL --max-time 15 "$url" 2>/dev/null | head -c 15000 || echo "")"
  local h1 title
  h1="$(echo "$html" | grep -oi '<h1[^>]*>[^<]*</h1>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_H1")"
  title="$(echo "$html" | grep -oi '<title>[^<]*</title>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_TITLE")"
  echo "=== $name ==="
  echo "Title: $title"
  echo "H1: ${h1:-NOT_FOUND}"
  echo ""
}

COMPETITOR_DATA=""
COMPETITOR_DATA+="$(fetch_competitor_hero "https://smith.ai" "Smith.ai")"
COMPETITOR_DATA+="$(fetch_competitor_hero "https://www.ruby.com" "Ruby")"
COMPETITOR_DATA+="$(fetch_competitor_hero "https://www.patlive.com" "PATLive")"

# ── STEP 4: Build the API request ──────────────────────────
log "Building Anthropic API request"

# System prompt — the ATLAS identity
SYSTEM_PROMPT='You are ATLAS — Autonomous Technical Lead & Site Supervisor for thecalltaker.com.

Your job: audit the site health data provided, identify issues, and produce a structured log entry.

RULES:
1. Analyze the HTTP status codes, load times, and meta tag data for every page
2. Flag any page with: HTTP != 200, load time > 3s, missing title, missing meta description, missing viewport
3. Compare competitor headlines to ours — note any messaging we should steal or counter
4. Rate overall site health: GREEN (no issues), YELLOW (warnings only), RED (critical issues)
5. Output ONLY a markdown log entry in this exact format:

## ATLAS Daemon Run — [TIMESTAMP]

### Site Health: [GREEN/YELLOW/RED]

### Page Audit
| Page | HTTP | Load Time | Title | Meta Desc | Viewport | Issues |
|------|------|-----------|-------|-----------|----------|--------|
(one row per page)

### Competitor Headlines
| Competitor | H1 | Title |
|-----------|-----|-------|
(one row per competitor)

### Issues Found
- (list any issues, or "None")

### Actions Taken
- (list any recommended fixes, or "No action needed")

### Critical Alerts
- (anything that needs Wallace notified immediately, or "None")

Be concise. No preamble. Just the markdown.'

# User message — the live context + audit data
USER_MSG="ATLAS daemon run at $TIMESTAMP

--- PRIMER.MD ---
$PRIMER_CONTENT

--- GIT STATE ---
$GIT_CONTEXT

--- RECENT ATLAS LOG (last 100 lines) ---
$ATLAS_LOG_CONTENT

--- SITE AUDIT DATA ---
$SITE_AUDIT

--- COMPETITOR DATA ---
$COMPETITOR_DATA

Analyze all of the above and produce your ATLAS log entry."

# Escape for JSON
SYSTEM_JSON="$(printf '%s' "$SYSTEM_PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
USER_JSON="$(printf '%s' "$USER_MSG" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"

REQUEST_BODY="{
  \"model\": \"$MODEL\",
  \"max_tokens\": $MAX_TOKENS,
  \"system\": $SYSTEM_JSON,
  \"messages\": [{\"role\": \"user\", \"content\": $USER_JSON}]
}"

# ── STEP 5: Call the Anthropic API ──────────────────────────
log "Calling Anthropic API ($MODEL, max_tokens=$MAX_TOKENS)"

API_RESPONSE="$(curl -sS --max-time 120 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$REQUEST_BODY" \
  "https://api.anthropic.com/v1/messages" 2>&1)"

# Extract the text content from the response
ATLAS_OUTPUT="$(echo "$API_RESPONSE" | python3 -c '
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

if [ -z "$ATLAS_OUTPUT" ] || echo "$ATLAS_OUTPUT" | grep -q "^API ERROR\|^PARSE ERROR"; then
  log "ERROR: API call failed — $ATLAS_OUTPUT"
  echo "$API_RESPONSE" | head -20
  exit 1
fi

log "API response received ($(echo "$ATLAS_OUTPUT" | wc -c | tr -d ' ') bytes)"

# ── STEP 6: Append findings to ATLAS_LOG.md ────────────────
log "Writing findings to ATLAS_LOG.md"

{
  echo ""
  echo "---"
  echo ""
  echo "$ATLAS_OUTPUT"
} >> "$LOG_FILE"

# ── STEP 7: Check for critical alerts and text Wallace ─────
CRITICAL_ALERTS="$(echo "$ATLAS_OUTPUT" | sed -n '/### Critical Alerts/,/###/p' | grep -v '###' | grep -v '^$' | grep -vi 'none' || true)"

if [ -n "$CRITICAL_ALERTS" ]; then
  log "CRITICAL ALERT DETECTED — attempting to notify Wallace"

  if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ] && [ -n "$TWILIO_FROM_NUMBER" ]; then
    ALERT_MSG="[ATLAS CRITICAL] $DATE_SHORT — $CRITICAL_ALERTS"
    # Truncate to 1500 chars for SMS
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
    log "WARNING: Twilio credentials not set. Critical alert NOT sent via SMS."
    log "Set: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER"
    log "Alert content: $CRITICAL_ALERTS"
  fi
else
  log "No critical alerts this run."
fi

# ── STEP 8: Commit changes if ATLAS_LOG.md was modified ────
cd "$REPO_DIR"
if git diff --quiet ATLAS_LOG.md 2>/dev/null; then
  log "No changes to ATLAS_LOG.md (unexpected)"
else
  git add ATLAS_LOG.md
  git commit -m "ATLAS daemon: automated site audit $DATE_SHORT $(date '+%H:%M')" --no-verify 2>/dev/null || true
  log "Changes committed to git"
fi

log "ATLAS DAEMON complete. Next run in 4 hours."
echo ""
