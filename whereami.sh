#!/bin/bash
CURRENT=$(pwd)
echo "════════════════════════════════"
echo " CURRENT DIRECTORY: $CURRENT"
echo "════════════════════════════════"

if [[ "$CURRENT" == *"thecalltaker-ops"* ]]; then
  echo " YOU ARE IN: OPS REPO"
  echo " Purpose: Agents, daemons, launchd, logs"
  echo " Build agents here"
elif [[ "$CURRENT" == *"thecalltaker"* ]]; then
  echo " YOU ARE IN: WEBSITE REPO"
  echo " Purpose: HTML, CSS, GitHub Pages only"
  echo " Build website here"
else
  echo " UNKNOWN REPO"
  echo " Website: ~/Desktop/thecalltaker/"
  echo " Ops:     ~/thecalltaker-ops/"
fi
echo "════════════════════════════════"
