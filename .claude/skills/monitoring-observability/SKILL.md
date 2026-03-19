---
name: monitoring-observability
description: "Design and implement monitoring, alerting, and observability systems. Use when setting up health checks, log aggregation, metrics dashboards, alert routing, uptime monitoring, or debugging production issues. Covers structured logging, health endpoints, metric collection, alert fatigue prevention, and incident response."
category: infrastructure
---

# Monitoring & Observability

Build reliable monitoring that catches real problems and avoids alert fatigue.

---

## The 3 Pillars

### 1. Logs — What Happened
Structured, searchable records of events.

```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "engine": getattr(record, 'engine', 'unknown'),
            "command": getattr(record, 'command', ''),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["error"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

**Log levels:**
- `DEBUG` — Verbose tracing (never in production logs)
- `INFO` — Normal operations (email sent, lead scored)
- `WARNING` — Recoverable issues (API retry, rate limited)
- `ERROR` — Failed operations (API 500, state corruption)
- `CRITICAL` — System failure (engine crash, service down)

### 2. Metrics — How Much / How Fast
Numeric measurements over time.

```python
# Metric types
metrics = {
    "emails_sent": 0,        # Counter — only goes up
    "api_latency_ms": [],    # Histogram — distribution
    "active_pilots": 3,      # Gauge — current value
    "queue_depth": 47,       # Gauge — current value
}

# Daily metrics file
def save_daily_metrics(metrics_dict):
    date = datetime.now().strftime("%Y-%m-%d")
    path = f"logs/metrics/{date}.json"
    with open(path, 'w') as f:
        json.dump({
            "date": date,
            "collected_at": datetime.now().isoformat(),
            **metrics_dict
        }, f, indent=2)
```

### 3. Alerts — What Needs Attention
Notifications when metrics cross thresholds.

**Alert priority matrix:**

| Severity | Response Time | Channel | Example |
|----------|--------------|---------|---------|
| CRITICAL | < 5 min | Push + SMS | Engine crash, payment failure |
| HIGH | < 1 hour | Push notification | Hot lead, demo call |
| MEDIUM | Same day | Daily digest | Low send volume, high bounce |
| LOW | Next review | Dashboard only | Minor API errors, slow responses |

---

## Health Check Pattern

Every service should expose a health check:

```python
def health_check():
    """Returns health status with component details."""
    checks = {
        "state_file": check_state_file(),
        "ghl_api": check_ghl_api(),
        "last_run": check_last_run(),
        "error_rate": check_error_rate(),
    }

    status = "green"
    for name, check in checks.items():
        if check["status"] == "red":
            status = "red"
            break
        elif check["status"] == "yellow":
            status = "yellow"

    return {
        "service": "max-engine",
        "status": status,  # green/yellow/red
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
    }

def check_state_file():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        age = time.time() - os.path.getmtime(STATE_FILE)
        if age > 7200:  # 2 hours
            return {"status": "yellow", "message": f"State file {age/3600:.1f}h old"}
        return {"status": "green", "message": "OK"}
    except Exception as e:
        return {"status": "red", "message": str(e)}

def check_ghl_api():
    try:
        start = time.time()
        resp = ghl_get("/contacts?limit=1")
        latency = (time.time() - start) * 1000
        if latency > 5000:
            return {"status": "yellow", "message": f"Slow: {latency:.0f}ms"}
        return {"status": "green", "message": f"{latency:.0f}ms"}
    except Exception as e:
        return {"status": "red", "message": str(e)}
```

---

## Heartbeat Monitoring

For launchd services that run on schedules:

```python
def write_heartbeat(service_name):
    """Write heartbeat file after successful run."""
    path = f"logs/{service_name}.heartbeat"
    with open(path, 'w') as f:
        json.dump({
            "service": service_name,
            "last_run": datetime.now().isoformat(),
            "status": "ok",
            "pid": os.getpid(),
        }, f)

def check_heartbeat(service_name, max_age_minutes=60):
    """Check if a service has run recently."""
    path = f"logs/{service_name}.heartbeat"
    if not os.path.exists(path):
        return {"status": "red", "message": "No heartbeat file"}

    age = time.time() - os.path.getmtime(path)
    if age > max_age_minutes * 60:
        return {"status": "red", "message": f"Last heartbeat {age/60:.0f}m ago"}
    return {"status": "green", "message": f"Last heartbeat {age/60:.0f}m ago"}
```

---

## Alert Fatigue Prevention

### Deduplication
```python
# Don't send same alert within window
DEDUPE_WINDOW = 1800  # 30 minutes
_recent_alerts = {}

def should_alert(key):
    now = time.time()
    if key in _recent_alerts and now - _recent_alerts[key] < DEDUPE_WINDOW:
        return False
    _recent_alerts[key] = now
    return True
```

### Alert Escalation
```python
def escalate(issue_key, severity="medium"):
    """Escalate if issue persists."""
    state = load_state()
    issue = state.get("open_issues", {}).get(issue_key, {})

    if not issue:
        # First occurrence — log, don't alert
        state.setdefault("open_issues", {})[issue_key] = {
            "first_seen": datetime.now().isoformat(),
            "count": 1,
            "severity": severity,
        }
    else:
        issue["count"] += 1
        if issue["count"] >= 3 and severity == "medium":
            # 3 consecutive failures — escalate
            send_alert(issue_key, severity="high")
        elif issue["count"] >= 5:
            # 5 failures — critical
            send_alert(issue_key, severity="critical")

    save_state(state)
```

### Quiet Hours
```python
def in_quiet_hours():
    """Don't send non-critical alerts 10pm-7am."""
    hour = datetime.now().hour
    return hour >= 22 or hour < 7

def smart_alert(message, severity):
    if severity == "critical":
        send_now(message)  # Always send critical
    elif in_quiet_hours():
        queue_for_morning(message)  # Buffer non-critical
    else:
        send_now(message)
```

---

## Dashboard Metrics

Key metrics to display:

```python
DASHBOARD_METRICS = {
    # Business metrics
    "mrr": {"type": "gauge", "unit": "$"},
    "active_pilots": {"type": "gauge", "unit": "count"},
    "demo_calls_today": {"type": "counter", "unit": "count"},
    "leads_generated_today": {"type": "counter", "unit": "count"},

    # System metrics
    "api_calls_today": {"type": "counter", "unit": "count"},
    "api_error_rate": {"type": "gauge", "unit": "%"},
    "emails_sent_today": {"type": "counter", "unit": "count"},
    "sms_sent_today": {"type": "counter", "unit": "count"},

    # Health metrics
    "engines_healthy": {"type": "gauge", "unit": "count"},
    "services_running": {"type": "gauge", "unit": "count"},
    "last_crash": {"type": "timestamp", "unit": ""},
    "uptime_pct": {"type": "gauge", "unit": "%"},
}
```

---

## Incident Response Checklist

When an alert fires:

1. **Acknowledge** — Note the time, check if it's a real issue or false positive
2. **Assess scope** — One service or cascade? Affecting customers?
3. **Mitigate** — Restart service, rollback change, disable feature
4. **Investigate** — Check logs, state files, recent deployments
5. **Fix** — Apply root cause fix
6. **Verify** — Confirm service is healthy, check downstream
7. **Document** — Postmortem: what happened, why, how to prevent
