---
name: health-monitor
description: "System health monitor checking launchd services, GHL proxy, Bland.ai quotas, and intelligence freshness. Use when checking system health or via /loop 30m /health-monitor for continuous monitoring."
user-invokable: true
---

# Health Monitor — System Health Loop

You are a system health monitor. Every run, you check all critical services, APIs, and data freshness, then report status and alert on any issues.

## Run Instructions

### Step 1: Check Launchd Services

Check the 30 critical launchd services are running:

```bash
# Get all thecalltaker services and their status
launchctl list 2>/dev/null | grep "com.thecalltaker" | while read pid status label; do
  if [ "$pid" = "-" ] || [ "$status" != "0" ]; then
    echo "DOWN: $label (pid=$pid, status=$status)"
  else
    echo "OK: $label (pid=$pid)"
  fi
done
```

Critical services (alert URGENT if any are down):
- `com.thecalltaker.max.monitor`
- `com.thecalltaker.donny.speed`
- `com.thecalltaker.demo.pilot-text`
- `com.thecalltaker.demo.call-track`
- `com.thecalltaker.demo.escalate`
- `com.thecalltaker.ops.notification-hub`
- `com.thecalltaker.ops.speed-alert`

Non-critical services (alert HIGH if down):
- All other `com.thecalltaker.*` services

### Step 2: Check GHL Proxy

```bash
PROXY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
  "https://thecalltaker.com/api/ghl/health" 2>/dev/null)
```

- 200 → OK
- Any other → Alert:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "PROXY DOWN: GHL proxy returning $PROXY_STATUS" \
  "thecalltaker.com/api/ghl/health returned $PROXY_STATUS. Frontend GHL calls may be failing." \
  "high"
```

### Step 3: Check Bland.ai Call Count

```bash
# Read today's call count from daily report or blast state
CALLS_TODAY=$(python3 -c "
import json, os
state_file = os.path.expanduser('~/thecalltaker-ops/ops/blast-state.json')
try:
    with open(state_file) as f:
        state = json.load(f)
    print(state.get('daily_calls', 0))
except:
    print(-1)
")
```

- If `CALLS_TODAY >= 80` → Warning (approaching 100 cap)
- If `CALLS_TODAY >= 100` → Alert (cap reached)
- If `CALLS_TODAY == -1` → Could not read state (log warning)

Alert if approaching cap:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "BLAND.AI: $CALLS_TODAY/100 calls today" \
  "Approaching daily call limit. $((100 - CALLS_TODAY)) calls remaining." \
  "high"
```

### Step 4: Check Intelligence Freshness

```bash
INTEL_FILE="$HOME/thecalltaker-ops/shared/intelligence.json"
if [ -f "$INTEL_FILE" ]; then
  MODIFIED=$(stat -f %m "$INTEL_FILE" 2>/dev/null || stat -c %Y "$INTEL_FILE" 2>/dev/null)
  NOW=$(date +%s)
  AGE_MIN=$(( (NOW - MODIFIED) / 60 ))
  if [ "$AGE_MIN" -gt 10 ]; then
    echo "STALE: intelligence.json is ${AGE_MIN}m old (threshold: 10m)"
  else
    echo "OK: intelligence.json is ${AGE_MIN}m old"
  fi
else
  echo "MISSING: intelligence.json not found"
fi
```

Alert if stale > 30 minutes:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "INTEL STALE: intelligence.json is ${AGE_MIN}m old" \
  "Intelligence file hasn't been updated in ${AGE_MIN} minutes. Pipeline may be stuck." \
  "default"
```

### Step 5: Check Key Log Files for Errors

```bash
# Count errors in last 30 minutes across all engine logs
RECENT_ERRORS=$(find ~/thecalltaker-ops/logs/ -name "*.log" -newer <(date -d '30 minutes ago' +%s 2>/dev/null || echo /dev/null) -exec grep -c "ERROR\|CRITICAL" {} + 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}')
```

If `RECENT_ERRORS > 10` → Alert:
```bash
bash ~/thecalltaker-ops/notify.sh \
  "ERROR SPIKE: $RECENT_ERRORS errors in last 30m" \
  "Check ~/thecalltaker-ops/logs/errors.log for details." \
  "high"
```

### Step 6: Write Health Report

Write to `~/thecalltaker-ops/system-health.json`:

```json
{
  "timestamp": "2026-03-19T15:30:00Z",
  "status": "healthy|degraded|critical",
  "services": {
    "total": 30,
    "running": 28,
    "down": ["com.thecalltaker.toolcosts"],
    "critical_down": []
  },
  "proxy": {
    "status": 200,
    "healthy": true
  },
  "bland_ai": {
    "calls_today": 45,
    "cap": 100,
    "remaining": 55
  },
  "intelligence": {
    "age_minutes": 5,
    "fresh": true
  },
  "errors": {
    "last_30m": 2,
    "spike": false
  },
  "loops": {
    "oracle_scanner": "2026-03-19T15:25:00Z",
    "outreach_engine": "2026-03-19T15:15:00Z",
    "payment_monitor": "2026-03-19T15:25:00Z",
    "health_monitor": "2026-03-19T15:30:00Z"
  }
}
```

Overall status:
- `healthy` — everything green
- `degraded` — non-critical issues (stale intel, non-critical service down)
- `critical` — critical service down, proxy down, or error spike

### Step 7: Log Run

Append to `~/thecalltaker-ops/logs/health-monitor.log`:
```
[2026-03-19T15:30:00Z] RUN: Status=healthy. Services: 28/30 running. Proxy: 200. Bland.ai: 45/100. Intel: 5m old. Errors: 2 (30m).
```

## Idempotency

- Read-only checks — no state mutations except writing health report
- Alerts use ntfy dedupe (30-min window) — won't spam for same issue
- Safe to run every 30 minutes without side effects

## Error Handling

- launchctl not available (Linux) → Skip service check, note in report
- Proxy unreachable → Report as critical, alert
- State files missing → Report as "unknown" for that component
- Log directory missing → Create it
