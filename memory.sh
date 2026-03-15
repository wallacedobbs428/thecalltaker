#!/usr/bin/env bash
# memory.sh — Git context injector for Claude Code sessions
# Run at session start to get full repo state snapshot

set -euo pipefail
cd "$(dirname "$0")"

divider="══════════════════════════════════════"

section() {
  echo ""
  echo "$divider"
  echo " $1"
  echo "$divider"
}

section "BRANCH"
git branch --show-current

section "RECENT COMMITS (last 10)"
git log --oneline --format="%h %ad %an: %s" --date=short -10

section "GIT STATUS"
git status --short || echo "(clean)"

section "STAGED CHANGES (diff --stat)"
git diff --cached --stat 2>/dev/null || echo "(nothing staged)"

section "UNSTAGED CHANGES (diff)"
git diff 2>/dev/null || echo "(no unstaged changes)"

section "STASHES"
git stash list 2>/dev/null || echo "(no stashes)"

section "UPSTREAM SYNC"
branch=$(git branch --show-current)
upstream=$(git rev-parse --abbrev-ref "@{upstream}" 2>/dev/null || echo "")
if [ -z "$upstream" ]; then
  echo "No upstream set for $branch"
else
  ahead=$(git rev-list --count "$upstream..HEAD" 2>/dev/null || echo 0)
  behind=$(git rev-list --count "HEAD..$upstream" 2>/dev/null || echo 0)
  echo "$branch vs $upstream: ${ahead} ahead, ${behind} behind"
fi

section "LOCAL BRANCHES (with last commit date)"
git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)' 2>/dev/null

echo ""
echo "$divider"
echo " END — $(date '+%Y-%m-%d %H:%M:%S')"
echo "$divider"
