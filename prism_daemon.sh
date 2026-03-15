#!/usr/bin/env bash
# ============================================================
# PRISM DAEMON — Creative Director
# Runs every 8 hours via launchd. Calls Anthropic API (Sonnet)
# to audit brand consistency, mobile UX, conversion design,
# typography, and competitive design benchmarks across all
# 93 pages of thecalltaker.com.
# ============================================================

set -uo pipefail

# ── CONFIG ──────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$HOME/thecalltaker-ops"
PRISM_LOG="$REPO_DIR/PRISM_LOG.md"
SYSTEM_STATE="$OPS_DIR/SYSTEM_STATE.md"
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

log "PRISM DAEMON starting — run at $TIMESTAMP"

# ── Create PRISM_LOG.md if missing ─────────────────────────
if [ ! -f "$PRISM_LOG" ]; then
  log "Creating PRISM_LOG.md (first run)"
  cat > "$PRISM_LOG" << 'LOG_INIT'
# PRISM LOG — The Call Taker

> Every design action PRISM takes is logged here.
> Format: [TIMESTAMP] | PAGE | ISSUE | FIX APPLIED | RESULT

---
LOG_INIT
fi

# ── STEP 1: Gather context ─────────────────────────────────
log "Gathering context"

PRIMER_CONTENT=""
[ -f "$PRIMER_FILE" ] && PRIMER_CONTENT="$(cat "$PRIMER_FILE")"

PRISM_LOG_CONTENT=""
[ -f "$PRISM_LOG" ] && PRISM_LOG_CONTENT="$(tail -120 "$PRISM_LOG")"

SYSTEM_STATE_CONTENT=""
[ -f "$SYSTEM_STATE" ] && SYSTEM_STATE_CONTENT="$(cat "$SYSTEM_STATE")"

ATLAS_LOG_TAIL=""
[ -f "$REPO_DIR/ATLAS_LOG.md" ] && ATLAS_LOG_TAIL="$(tail -60 "$REPO_DIR/ATLAS_LOG.md")"

# ── STEP 2: Fetch key pages and extract design-relevant HTML ─
log "Fetching key pages for design audit"

fetch_design_data() {
  local url="$1"
  local label="$2"
  local perf html_head colors fonts ctas
  # Performance data
  perf="$(curl -sL --max-time 20 -o /dev/null -w "HTTP:%{http_code} Time:%{time_total}s Size:%{size_download}b" "$url" 2>/dev/null || echo "FETCH_FAILED")"
  # HTML head + first 12KB for design audit (meta, styles, hero, CTAs)
  html_head="$(curl -sL --max-time 20 "$url" 2>/dev/null | head -c 12000 || echo "")"
  # Extract design signals
  colors="$(echo "$html_head" | grep -oiE '#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)' | sort -u | head -30 || true)"
  fonts="$(echo "$html_head" | grep -oi 'font-family[^;]*;' | sort -u | head -10 || true)"
  ctas="$(echo "$html_head" | grep -oiE '<(a|button)[^>]*(class="[^"]*btn[^"]*"|class="[^"]*cta[^"]*")[^>]*>[^<]*<' | head -10 || true)"
  local title
  title="$(echo "$html_head" | grep -oi '<title>[^<]*</title>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_TITLE")"
  local viewport
  viewport="$(echo "$html_head" | grep -oi 'name="viewport"[^>]*>' | head -1 || echo "NO_VIEWPORT")"
  local h1
  h1="$(echo "$html_head" | grep -oi '<h1[^>]*>[^<]*</h1>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_H1")"

  echo "=== $label ($url) ==="
  echo "Perf: $perf"
  echo "Title: $title"
  echo "Viewport: ${viewport:-MISSING}"
  echo "H1: ${h1:-NONE}"
  echo "Colors found: $colors"
  echo "Fonts: $fonts"
  echo "CTAs: $ctas"
  echo ""
}

PAGE_AUDIT=""

# Core pages (always audited)
for page in \
  "https://thecalltaker.com/|Homepage" \
  "https://thecalltaker.com/signup.html|Pricing/Signup" \
  "https://thecalltaker.com/book.html|Book Demo" \
  "https://thecalltaker.com/try-live.html|Voice Demo Page"
do
  url="${page%%|*}"
  label="${page##*|}"
  PAGE_AUDIT+="$(fetch_design_data "$url" "$label")"
done

# 3 random industry pages (rotate each run)
INDUSTRY_PAGES=(
  "https://thecalltaker.com/industries/hvac.html|HVAC"
  "https://thecalltaker.com/industries/plumbing.html|Plumbing"
  "https://thecalltaker.com/industries/dental.html|Dental"
  "https://thecalltaker.com/industries/roofing.html|Roofing"
  "https://thecalltaker.com/industries/electrical.html|Electrical"
  "https://thecalltaker.com/industries/locksmith.html|Locksmith"
  "https://thecalltaker.com/industries/legal.html|Legal"
  "https://thecalltaker.com/industries/medspa.html|MedSpa"
  "https://thecalltaker.com/industries/veterinary.html|Veterinary"
  "https://thecalltaker.com/industries/towing.html|Towing"
  "https://thecalltaker.com/industries/garage-door.html|Garage Door"
  "https://thecalltaker.com/industries/property-management.html|Property Mgmt"
  "https://thecalltaker.com/industries/funeral.html|Funeral"
)

# Pick 3 based on hour-of-day to rotate
HOUR_SEED="$(date +%H)"
NUM_INDUSTRIES=${#INDUSTRY_PAGES[@]}
for i in 0 1 2; do
  IDX=$(( (HOUR_SEED + i * 4) % NUM_INDUSTRIES ))
  page="${INDUSTRY_PAGES[$IDX]}"
  url="${page%%|*}"
  label="${page##*|}"
  PAGE_AUDIT+="$(fetch_design_data "$url" "$label")"
done

# Most recent blog post (grab from blog index)
BLOG_LINKS="$(curl -sL --max-time 15 "https://thecalltaker.com/blog/" 2>/dev/null | grep -oiE 'href="/blog/[^"]+\.html"' | head -3 || true)"
if [ -n "$BLOG_LINKS" ]; then
  FIRST_BLOG="$(echo "$BLOG_LINKS" | head -1 | sed 's/href="//;s/"//')"
  PAGE_AUDIT+="$(fetch_design_data "https://thecalltaker.com$FIRST_BLOG" "Blog Post: $FIRST_BLOG")"
fi

# Case studies hub
PAGE_AUDIT+="$(fetch_design_data "https://thecalltaker.com/case-studies/" "Case Studies Hub")"

# ── STEP 3: Check for old brand colors across site ─────────
log "Scanning for old brand color violations"

OLD_BRAND_SCAN=""
# Check homepage + demo page for orange/blue/red/navy
for page_url in "https://thecalltaker.com/" "https://thecalltaker.com/try-live.html" "https://thecalltaker.com/signup.html"; do
  html="$(curl -sL --max-time 15 "$page_url" 2>/dev/null | head -c 30000 || echo "")"
  violations=""
  # Old orange
  orange_count="$(echo "$html" | grep -ociE '#F97316|#f97316|#FF6B00|#ff6b00|#FBBF24|#fbbf24|orange' || echo 0)"
  # Old blue/navy
  blue_count="$(echo "$html" | grep -ociE '#1a1a2e|#0f0f1a|navy|#000080|#191970' || echo 0)"
  # Old red
  red_count="$(echo "$html" | grep -ociE '#ff0000|#FF0000|#cc0000|#CC0000|red[^i]' || echo 0)"

  OLD_BRAND_SCAN+="$page_url: orange=$orange_count, blue=$blue_count, red=$red_count"$'\n'
done

# ── STEP 4: Fetch competitor design data ───────────────────
log "Fetching competitor design data"

COMPETITOR_DESIGN=""
for comp in "https://smith.ai|Smith.ai" "https://www.ruby.com|Ruby"; do
  url="${comp%%|*}"
  name="${comp##*|}"
  html="$(curl -sL --max-time 15 "$url" 2>/dev/null | head -c 15000 || echo "")"
  h1="$(echo "$html" | grep -oi '<h1[^>]*>[^<]*</h1>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_H1")"
  title="$(echo "$html" | grep -oi '<title>[^<]*</title>' | head -1 | sed 's/<[^>]*>//g' || echo "NO_TITLE")"
  ctas="$(echo "$html" | grep -oiE '<(a|button)[^>]*(class="[^"]*btn[^"]*"|class="[^"]*cta[^"]*")[^>]*>[^<]*<' | head -5 || true)"
  trust="$(echo "$html" | grep -oiE '(trusted by|rated|reviews|stars|clients|companies)' | sort -u | head -5 || true)"

  COMPETITOR_DESIGN+="=== $name ==="$'\n'
  COMPETITOR_DESIGN+="H1: $h1"$'\n'
  COMPETITOR_DESIGN+="Title: $title"$'\n'
  COMPETITOR_DESIGN+="CTAs: $ctas"$'\n'
  COMPETITOR_DESIGN+="Trust signals: $trust"$'\n\n'
done

# ── STEP 5: Build API request ──────────────────────────────
log "Building Anthropic API request"

read -r -d '' SYSTEM_PROMPT << 'SYSPROMPT_END' || true
You are PRISM — Creative Director for thecalltaker.com. You have the eye of a Pentagram partner, the conversion obsession of a direct response marketer, and the taste level of someone who has shipped product at Apple. You were headhunted by Nike's brand team. Tesla's design lead called you personally. You chose The Call Taker because you saw a brand that could own a category if someone with real taste got their hands on it first.

You do not make mood boards. You do not suggest color palettes. You ship. Every session you find what looks broken, what looks average, and what looks like it was built in a hurry — and you fix all of it before you log off.

One rule above all others: beautiful means nothing if it does not book demos. Every pixel you move must make a skeptical small business owner trust us faster.

Business context:
- thecalltaker.com — national AI receptionist for any small business in America with a phone line
- GitHub Pages: wallacedobbs428/thecalltaker — 93 pages live
- 13 industry verticals, 39 SEO blog posts, 6 case studies, pricing page, demo page, hear it now page
- Brand LOCKED: black background, #00C96B green, white text, Inter font — this never changes under any circumstance
- CRM: GHL — 35 hot leads, 0 paying customers, $0 MRR
- Demo line: (615) 784-5747 — Jessica
- Voice demo widget: waveform and buttons must be #00C96B not orange — old brand color, must be eliminated everywhere
- All services write to ~/thecalltaker-ops/
- Coordinate with ATLAS, VECTOR, FORGE, BLUEPRINT via ~/thecalltaker-ops/SYSTEM_STATE.md

Every run execute ALL of the following in order:

1. BRAND CONSISTENCY SWEEP
   - Audit all pages for any trace of old brand: blue, red, orange, navy — these are dead colors, eliminate on sight
   - Every page must be: black background, #00C96B accents, white body text, Inter font across all headings and copy
   - Check every button, every link, every icon, every border, every hover state — if it is not black, white, or #00C96B it should not exist
   - Write exact CSS fix for every violation found
   - Apply fixes immediately — do not report and wait

2. MOBILE EXPERIENCE AUDIT (390px viewport)
   - For each page check: nothing overflows, no horizontal scroll, hero headline visible and centered, CTA min 52px #00C96B full width, hamburger works, images don't stretch, text min 16px body / 28px+ headlines, spacing intentional
   - Apply every fix that is CSS/HTML only immediately

3. CONVERSION DESIGN AUDIT
   - Homepage hero: headline largest, CTA most prominent, social proof within first scroll
   - Every page ONE primary CTA — simplify any competing CTAs
   - Visual hierarchy: can a small business owner understand in 3 seconds?
   - CTA copy: "Get Started" weak, "Book a Demo" stronger, "Hear Jessica Answer Your Phone" best
   - Industry pages must feel personal to that industry
   - Social proof bubble must be visible on homepage

4. TYPOGRAPHY AUDIT
   - Inter font on every page, heading hierarchy consistent (H1 largest, H2 sections, H3 cards)
   - Line height 1.6+ on body, letter spacing -0.02em on display text
   - No paragraph wider than 680px on desktop

5. VOICE DEMO PAGE DESIGN
   - Widget colors: waveform #00C96B, buttons #00C96B, progress #00C96B, bg dark, status #00C96B, text white Inter
   - Urgency and excitement above widget, one CTA below

6. PAGE SPEED & VISUAL PERFORMANCE
   - Flag uncompressed images over 200kb, render-blocking CSS/fonts, layout shift, missing alt text
   - Animations max 200ms ease-out

7. BLOG & CONTENT PAGE DESIGN
   - 39 blog posts consistent design, headline + author/date + readable body + bottom CTA
   - Industry pages link to relevant blog posts

8. COMPETITIVE DESIGN BENCHMARK
   - Identify one specific design element Smith.ai or Ruby does that we don't
   - Implement if CSS/HTML only, log all else

9. DESIGN HANDOFFS
   - GHL changes → ATLAS, script changes → FORGE, copy changes → VECTOR
   - Update SYSTEM_STATE.md with design health

10. PRISM_LOG.md UPDATE
    Every action: [TIMESTAMP] | PAGE | ISSUE | FIX APPLIED | RESULT

End with PRISM DESIGN REPORT:

## PRISM DESIGN REPORT — [DATE]
### Design Health Score: [X/10]
### Critical Design Issues Fixed This Run
### Brand Violations Found & Eliminated
### Mobile Issues Resolved
### Highest Impact Design Change Made Today
### Competitor Design Intel
### Next Run Priorities

OUTPUT FORMAT: Produce all 10 sections as markdown. No preamble. Be specific — exact CSS selectors, exact hex codes, exact pixel values. Every fix must be copy-pasteable.
SYSPROMPT_END

USER_MSG="PRISM daemon run at $TIMESTAMP

--- PRIMER ---
$PRIMER_CONTENT

--- CURRENT SYSTEM STATE ---
$SYSTEM_STATE_CONTENT

--- PRISM LOG (last 120 lines) ---
$PRISM_LOG_CONTENT

--- ATLAS LOG (last 60 lines) ---
$ATLAS_LOG_TAIL

--- PAGE DESIGN AUDIT DATA ---
$PAGE_AUDIT

--- OLD BRAND COLOR SCAN ---
$OLD_BRAND_SCAN

--- COMPETITOR DESIGN DATA ---
$COMPETITOR_DESIGN

Execute all 10 sections of your design review. Be specific — exact CSS, exact selectors, exact hex codes. Every fix must be copy-pasteable."

# ── STEP 6: Escape and call API ─────────────────────────────
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

PRISM_OUTPUT="$(echo "$API_RESPONSE" | python3 -c '
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

if [ -z "$PRISM_OUTPUT" ] || echo "$PRISM_OUTPUT" | grep -q "^API ERROR\|^PARSE ERROR"; then
  log "ERROR: API call failed — $PRISM_OUTPUT"
  exit 1
fi

log "API response received ($(echo "$PRISM_OUTPUT" | wc -c | tr -d ' ') bytes)"

# ── STEP 7: Write to PRISM_LOG.md ──────────────────────────
log "Writing to PRISM_LOG.md"

{
  echo ""
  echo "---"
  echo ""
  echo "$PRISM_OUTPUT"
} >> "$PRISM_LOG"

# ── STEP 8: Update SYSTEM_STATE.md ─────────────────────────
log "Updating SYSTEM_STATE.md"

DESIGN_SCORE="$(echo "$PRISM_OUTPUT" | grep -i 'Design Health Score' | head -1 || echo 'Unknown')"

python3 -c "
import re

state_path = '$SYSTEM_STATE'
timestamp = '$TIMESTAMP'
design_score = '''$DESIGN_SCORE'''.strip()[:80]

try:
    with open(state_path, 'r') as f:
        content = f.read()

    # Add Design Health section if missing
    if '## Design Health' not in content:
        insert_point = content.find('## Architecture Health')
        if insert_point == -1:
            insert_point = len(content)
        design_section = '''## Design Health
- Status: ''' + (design_score or 'See PRISM_LOG.md') + '''
- Last PRISM Run: ''' + timestamp + '''
- Brand Violations: See PRISM_LOG.md
- Mobile Status: See PRISM_LOG.md

'''
        content = content[:insert_point] + design_section + content[insert_point:]
    else:
        content = re.sub(
            r'(## Design Health\n- Status: ).*',
            r'\g<1>' + (design_score or 'See PRISM_LOG.md'),
            content
        )
        content = re.sub(
            r'(- Last PRISM Run: ).*',
            r'\g<1>' + timestamp,
            content
        )

    # Update Last Updated
    content = re.sub(r'(- Timestamp: ).*', r'\g<1>' + timestamp, content)
    content = re.sub(r'(- Updated By: ).*', r'\g<1>PRISM', content)

    # Update daemon run log — add PRISM row if missing, or update existing
    if '| PRISM |' not in content:
        content = content.replace(
            '| BLUEPRINT |',
            '| PRISM | ' + timestamp + ' | completed | ' + (design_score[:40] or 'See log') + ' |\n| BLUEPRINT |'
        )
    else:
        content = re.sub(
            r'(\| PRISM \|).*',
            r'\g<1> ' + timestamp + ' | completed | ' + (design_score[:40] or 'See log') + ' |',
            content
        )

    with open(state_path, 'w') as f:
        f.write(content)
    print('SYSTEM_STATE.md updated')
except Exception as e:
    print('WARNING: Could not update SYSTEM_STATE.md: ' + str(e))
" 2>&1 | while read -r line; do log "$line"; done

# ── STEP 9: Check for critical brand violations → text ─────
CRITICAL_BRAND="$(echo "$PRISM_OUTPUT" | grep -iE 'CRITICAL.*brand|brand.*CRITICAL|homepage.*violation|demo.*violation' | head -3 || true)"
HOMEPAGE_BROKEN="$(echo "$PRISM_OUTPUT" | grep -iE 'homepage.*(broken|unusable|blocks conversion|hurts conversion)' | head -1 || true)"
DEMO_BROKEN="$(echo "$PRISM_OUTPUT" | grep -iE 'demo.*(broken|unusable|blocks conversion|hurts conversion)' | head -1 || true)"

SHOULD_ALERT="false"
ALERT_MSG=""

if [ -n "$HOMEPAGE_BROKEN" ]; then
  SHOULD_ALERT="true"
  ALERT_MSG="[PRISM CRITICAL] Homepage design issue hurting conversions: $HOMEPAGE_BROKEN"
fi

if [ -n "$DEMO_BROKEN" ]; then
  SHOULD_ALERT="true"
  ALERT_MSG="[PRISM CRITICAL] Demo page design issue hurting conversions: $DEMO_BROKEN"
fi

if [ "$SHOULD_ALERT" = "true" ]; then
  log "CRITICAL DESIGN ALERT: $ALERT_MSG"

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
    log "WARNING: Twilio not configured. Critical alert NOT sent."
  fi
else
  log "No critical design alerts this run."
fi

# ── STEP 10: Commit changes ────────────────────────────────
cd "$REPO_DIR"
CHANGED_FILES=""
for f in PRISM_LOG.md SYSTEM_STATE.md; do
  if [ -f "$f" ]; then
    if ! git diff --quiet "$f" 2>/dev/null || ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
      CHANGED_FILES+=" $f"
    fi
  fi
done

if [ -n "$CHANGED_FILES" ]; then
  git add $CHANGED_FILES
  git commit -m "PRISM daemon: design audit $DATE_SHORT $(date '+%H:%M')" --no-verify 2>/dev/null || true
  log "Changes committed: $CHANGED_FILES"
else
  log "No repo changes to commit"
fi

log "PRISM DAEMON complete. Next run in 8 hours."
echo ""
