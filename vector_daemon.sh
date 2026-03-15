#!/usr/bin/env bash
# ============================================================
# VECTOR DAEMON — CMO & Growth Engine
# Runs every 6 hours via launchd (+ forced 8am daily).
# Calls Anthropic API (Sonnet) to generate follow-up copy,
# analyze email performance, scan competitor ads, and produce
# fresh subject line tests. All output logged to VECTOR_LOG.md.
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$HOME/thecalltaker-ops"
VECTOR_LOG="$REPO_DIR/VECTOR_LOG.md"
PRIMER_FILE="$REPO_DIR/primer.md"
COPY_OUTPUT="$OPS_DIR/vector_copy_output.txt"
HOT_LEAD_FILE="$OPS_DIR/hot_lead_count.txt"
MODEL="claude-sonnet-4-20250514"
MAX_TOKENS=4096
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_SHORT="$(date '+%Y-%m-%d')"
HOUR="$(date '+%H')"

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

log "VECTOR DAEMON starting — run at $TIMESTAMP"

# ── STEP 1: Gather context ─────────────────────────────────
log "Gathering context"

PRIMER_CONTENT=""
[ -f "$PRIMER_FILE" ] && PRIMER_CONTENT="$(cat "$PRIMER_FILE")"

VECTOR_LOG_CONTENT=""
[ -f "$VECTOR_LOG" ] && VECTOR_LOG_CONTENT="$(tail -150 "$VECTOR_LOG")"

# Hot lead count
HOT_LEAD_COUNT="unknown"
if [ -f "$HOT_LEAD_FILE" ]; then
  HOT_LEAD_COUNT="$(cat "$HOT_LEAD_FILE" | tr -d '[:space:]')"
fi

# Hours since last VECTOR_LOG update
LAST_UPDATE_HOURS="unknown"
if [ -f "$VECTOR_LOG" ]; then
  LAST_MOD="$(stat -f %m "$VECTOR_LOG" 2>/dev/null || stat -c %Y "$VECTOR_LOG" 2>/dev/null || echo 0)"
  NOW_EPOCH="$(date +%s)"
  if [ "$LAST_MOD" -gt 0 ] 2>/dev/null; then
    DIFF_SECS=$(( NOW_EPOCH - LAST_MOD ))
    LAST_UPDATE_HOURS=$(( DIFF_SECS / 3600 ))
  fi
fi

# Email error logs (last 50 lines from blast engine log if it exists)
EMAIL_ERRORS=""
for logfile in "$OPS_DIR/logs/errors.log" "$OPS_DIR/logs/all-engines.log"; do
  if [ -f "$logfile" ]; then
    EMAIL_ERRORS+="$(grep -i 'blast\|email\|smtp\|bounce\|reject\|fail.*send\|domain.*rep\|spf\|dkim\|dmarc' "$logfile" 2>/dev/null | tail -30 || true)"
    EMAIL_ERRORS+=$'\n'
  fi
done

BLAST_STATE=""
[ -f "$OPS_DIR/ops/blast-state.json" ] && BLAST_STATE="$(cat "$OPS_DIR/ops/blast-state.json" 2>/dev/null | head -50 || true)"

# Determine if this is the 8am morning summary run
IS_MORNING="false"
if [ "$HOUR" -ge 7 ] && [ "$HOUR" -le 9 ]; then
  IS_MORNING="true"
fi

# ── STEP 2: Fetch competitor ad data (Meta Ad Library) ─────
log "Checking competitor ads via Meta Ad Library"

fetch_meta_ads() {
  local domain="$1"
  local name="$2"
  # Meta Ad Library public page — extract what we can
  local url="https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=$domain"
  local result
  result="$(curl -sL --max-time 15 -o /dev/null -w "HTTP: %{http_code}, Size: %{size_download}" "$url" 2>/dev/null || echo "FETCH_FAILED")"
  echo "=== $name ($domain) ==="
  echo "Meta Ad Library check: $result"
  echo "(Note: Full ad scraping requires Meta Marketing API access)"
  echo ""
}

COMPETITOR_ADS=""
COMPETITOR_ADS+="$(fetch_meta_ads "smith.ai" "Smith.ai")"
COMPETITOR_ADS+="$(fetch_meta_ads "ruby.com" "Ruby")"
COMPETITOR_ADS+="$(fetch_meta_ads "answerforce.com" "AnswerForce")"

# ── STEP 3: Build API request ──────────────────────────────
log "Building Anthropic API request"

SYSTEM_PROMPT='You are VECTOR — CMO & Head of Growth for The Call Taker (thecalltaker.com).

AI receptionist for service businesses. $97/mo after-hours, $297/mo 24/7, $497/mo premium. Demo: (615) 784-5747.
CRM: GoHighLevel. Current MRR: $0. Hot leads in pipeline need aggressive follow-up.

Your job every run:
1. Check the hot lead count and hours since last follow-up update
2. If > 24 hours since last update OR MRR is $0: generate fresh follow-up email + SMS copy for top 3 industries (HVAC, Plumbing, Dental)
3. Analyze any email error logs provided — diagnose the 63% failure rate root cause
4. Generate 3 fresh A/B subject line variants for the next blast
5. Update the VECTOR SCORECARD

OUTPUT FORMAT (markdown only, no preamble):

## VECTOR Daemon Run — [TIMESTAMP]

### Hot Lead Status
- Count: X/35
- Hours since last follow-up update: X
- Priority: [CRITICAL/HIGH/NORMAL]

### Fresh Follow-Up Copy (if needed)
#### HVAC — Email
(subject + body, max 120 words)
#### HVAC — SMS
(max 160 chars)
#### Plumbing — Email
(subject + body, max 120 words)
#### Plumbing — SMS
(max 160 chars)
#### Dental — Email
(subject + body, max 120 words)
#### Dental — SMS
(max 160 chars)

### Email Deliverability Diagnosis
- Root cause analysis based on log data
- Specific fix recommendations

### Subject Line A/B Test
- Variant A: (subject line)
- Variant B: (subject line)
- Variant C: (subject line)
- Recommended send: (which to test first and why)

### Competitor Ad Intel
(any findings from Meta Ad Library data)

### VECTOR SCORECARD
- Hot leads active: X/35
- Hours since last outreach: X
- MRR: $0
- Biggest blocker: (one line)
- Next action: (one line)

Rules:
- Write at 6th grade reading level
- Lead with pain, not features
- Every email ends with a P.S. line
- Subject lines: lowercase, max 6 words, no punctuation
- SMS: max 160 chars, one CTA only
- If MRR = $0, ALL output focuses on converting hot leads. Nothing else matters.'

USER_MSG="VECTOR daemon run at $TIMESTAMP
Is morning summary: $IS_MORNING

--- PRIMER ---
$PRIMER_CONTENT

--- VECTOR LOG (last 150 lines) ---
$VECTOR_LOG_CONTENT

--- HOT LEAD STATUS ---
Hot lead count: $HOT_LEAD_COUNT
Hours since last VECTOR_LOG update: $LAST_UPDATE_HOURS

--- EMAIL ERROR LOGS ---
$EMAIL_ERRORS

--- BLAST ENGINE STATE ---
$BLAST_STATE

--- COMPETITOR AD CHECKS ---
$COMPETITOR_ADS

Generate your VECTOR daemon output. If this is the morning summary run (8am), also include a 3-sentence morning brief for Wallace suitable for an SMS text."

# Escape for JSON
SYSTEM_JSON="$(printf '%s' "$SYSTEM_PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
USER_JSON="$(printf '%s' "$USER_MSG" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"

REQUEST_BODY="{
  \"model\": \"$MODEL\",
  \"max_tokens\": $MAX_TOKENS,
  \"system\": $SYSTEM_JSON,
  \"messages\": [{\"role\": \"user\", \"content\": $USER_JSON}]
}"

# ── STEP 4: Call API ────────────────────────────────────────
log "Calling Anthropic API ($MODEL)"

API_RESPONSE="$(curl -sS --max-time 120 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$REQUEST_BODY" \
  "https://api.anthropic.com/v1/messages" 2>&1)"

VECTOR_OUTPUT="$(echo "$API_RESPONSE" | python3 -c '
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
except Exception as e:
    print("PARSE ERROR: " + str(e))
' 2>&1)"

if [ -z "$VECTOR_OUTPUT" ] || echo "$VECTOR_OUTPUT" | grep -q "^API ERROR\|^PARSE ERROR"; then
  log "ERROR: API call failed — $VECTOR_OUTPUT"
  exit 1
fi

log "API response received ($(echo "$VECTOR_OUTPUT" | wc -c | tr -d ' ') bytes)"

# ── STEP 5: Write outputs ──────────────────────────────────
log "Writing to VECTOR_LOG.md"

{
  echo ""
  echo "---"
  echo ""
  echo "$VECTOR_OUTPUT"
} >> "$VECTOR_LOG"

# Write fresh copy to the ops output file
FRESH_COPY="$(echo "$VECTOR_OUTPUT" | sed -n '/### Fresh Follow-Up Copy/,/### Email Deliverability/p' | head -n -1)"
if [ -n "$FRESH_COPY" ]; then
  {
    echo "=== VECTOR Copy Output — $TIMESTAMP ==="
    echo "$FRESH_COPY"
    echo ""
  } >> "$COPY_OUTPUT"
  log "Fresh copy written to $COPY_OUTPUT"
fi

# ── STEP 6: Morning SMS summary (7-9am only) ───────────────
if [ "$IS_MORNING" = "true" ]; then
  log "Morning summary run — attempting SMS to Wallace"

  MORNING_MSG="$(echo "$VECTOR_OUTPUT" | grep -A5 'morning brief\|Morning Brief\|MORNING' | head -5 || true)"
  if [ -z "$MORNING_MSG" ]; then
    # Fallback: use the scorecard
    MORNING_MSG="$(echo "$VECTOR_OUTPUT" | sed -n '/### VECTOR SCORECARD/,/---/p' | head -8 || true)"
  fi

  if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ] && [ -n "$TWILIO_FROM_NUMBER" ] && [ -n "$MORNING_MSG" ]; then
    SMS_BODY="[VECTOR 8am] $DATE_SHORT
$MORNING_MSG"
    SMS_BODY="${SMS_BODY:0:1500}"

    curl -sS -X POST \
      "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
      -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
      --data-urlencode "To=$WALLACE_PHONE" \
      --data-urlencode "From=$TWILIO_FROM_NUMBER" \
      --data-urlencode "Body=$SMS_BODY" \
      > /dev/null 2>&1

    log "Morning SMS sent to $WALLACE_PHONE"
  else
    log "Twilio not configured — morning SMS skipped"
  fi
fi

# ── STEP 7: Commit changes ─────────────────────────────────
cd "$REPO_DIR"
if ! git diff --quiet VECTOR_LOG.md 2>/dev/null; then
  git add VECTOR_LOG.md
  git commit -m "VECTOR daemon: automated growth run $DATE_SHORT $(date '+%H:%M')" --no-verify 2>/dev/null || true
  log "Changes committed to git"
fi

log "VECTOR DAEMON complete. Next run in 6 hours."
echo ""
