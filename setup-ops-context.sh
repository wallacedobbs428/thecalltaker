#!/bin/bash
# ═══════════════════════════════════════════════════════════
# SETUP SCRIPT — Deploy CONTEXT.md + CLAUDE.md header to ops repo
# Run this ONCE on your Mac to set up the ops repo identity
# ═══════════════════════════════════════════════════════════

OPS_DIR="$HOME/thecalltaker-ops"
WEBSITE_DIR="$HOME/Desktop/thecalltaker"

echo "════════════════════════════════"
echo " Setting up repo identity files"
echo "════════════════════════════════"

# --- Step 1: Copy CONTEXT.md to ops repo ---
if [ -d "$OPS_DIR" ]; then
  cp "$WEBSITE_DIR/ops-context-staging/CONTEXT.md" "$OPS_DIR/CONTEXT.md"
  echo " Copied CONTEXT.md to $OPS_DIR/"
else
  echo " ERROR: $OPS_DIR does not exist"
  exit 1
fi

# --- Step 2: Add header to ops CLAUDE.md if not already present ---
if [ -f "$OPS_DIR/CLAUDE.md" ]; then
  if ! grep -q "REPO IDENTITY" "$OPS_DIR/CLAUDE.md"; then
    HEADER=$(cat "$WEBSITE_DIR/ops-context-staging/CLAUDE-HEADER.md")
    EXISTING=$(cat "$OPS_DIR/CLAUDE.md")
    echo "$HEADER" > "$OPS_DIR/CLAUDE.md"
    echo "---" >> "$OPS_DIR/CLAUDE.md"
    echo "" >> "$OPS_DIR/CLAUDE.md"
    echo "$EXISTING" >> "$OPS_DIR/CLAUDE.md"
    echo " Added repo identity header to $OPS_DIR/CLAUDE.md"
  else
    echo " $OPS_DIR/CLAUDE.md already has repo identity header"
  fi
else
  cp "$WEBSITE_DIR/ops-context-staging/CLAUDE-HEADER.md" "$OPS_DIR/CLAUDE.md"
  echo " Created new CLAUDE.md in $OPS_DIR/"
fi

# --- Step 3: Add repo check to ops primer.md ---
if [ -f "$OPS_DIR/primer.md" ]; then
  if ! grep -q "ALWAYS CONFIRM REPO" "$OPS_DIR/primer.md"; then
    HEADER="## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours.

---

"
    EXISTING=$(cat "$OPS_DIR/primer.md")
    echo "$HEADER$EXISTING" > "$OPS_DIR/primer.md"
    echo " Added repo check to $OPS_DIR/primer.md"
  else
    echo " $OPS_DIR/primer.md already has repo check"
  fi
else
  echo "## ALWAYS CONFIRM REPO AT SESSION START
Run: bash ~/whereami.sh
Confirm you are in the correct repo before touching any files. Wrong repo = wasted hours." > "$OPS_DIR/primer.md"
  echo " Created primer.md in $OPS_DIR/"
fi

# --- Step 4: Install whereami.sh to home directory ---
cp "$WEBSITE_DIR/whereami.sh" "$HOME/whereami.sh"
chmod +x "$HOME/whereami.sh"
echo " Installed ~/whereami.sh"

echo ""
echo "════════════════════════════════"
echo " DONE. Both repos are now tagged."
echo " Run: bash ~/whereami.sh"
echo "════════════════════════════════"
