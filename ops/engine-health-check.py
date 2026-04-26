#!/usr/bin/env python3
"""
THE CALL TAKER — Engine Health Check
Checks key launchd services, script existence, and state files.
Run: python3 ~/thecalltaker/ops/engine-health-check.py
"""

import subprocess
import os
import json
import time
from datetime import datetime

# Prefer the consolidated ops repo when present.
OPS_DIR = os.path.expanduser("~/thecalltaker-ops/ops")
if not os.path.isdir(OPS_DIR):
    OPS_DIR = os.path.expanduser("~/thecalltaker/ops")

# All services that should be running
SERVICES = {
    "com.thecalltaker.hot-lead-converter": {
        "script": "hot-lead-converter.py",
        "schedule": "Every 15 min",
        "critical": True
    },
    "com.thecalltaker.blast-engine-v2": {
        "script": "blast-engine-v2.py",
        "schedule": "3x daily (9am, 1pm, 5pm)",
        "critical": True
    },
    "com.thecalltaker.outbound-sms": {
        "script": "outbound-sms-engine.py",
        "schedule": "2x daily (10am, 4pm)",
        "critical": True
    },
    "com.thecalltaker.storm-chaser-v2": {
        "script": "storm-chaser-v2.py",
        "schedule": "6x daily",
        "critical": False
    },
    "com.thecalltaker.ops.webhook": {
        "script": "stripe-webhook-handler.py",
        "schedule": "Always-on (KeepAlive)",
        "critical": True
    },
    "com.thecalltaker.payment-reminder": {
        "script": "payment-reminder-engine.py",
        "schedule": "2x daily (9am, 5pm)",
        "critical": False
    },
    "com.thecalltaker.dm-tracker": {
        "script": "dm-tracker.py",
        "schedule": "Daily 8am",
        "critical": False
    },
    "com.thecalltaker.lead-dashboard": {
        "script": "lead-dashboard-api.py",
        "schedule": "Every 10 min",
        "critical": False
    },
    "com.thecalltaker.blast-sms-followup": {
        "script": "blast-sms-followup.py",
        "schedule": "2x daily (11am, 3pm)",
        "critical": False
    },
    "com.thecalltaker.demo-webhook": {
        "script": "demo-booked-webhook.py",
        "schedule": "Always-on (KeepAlive)",
        "critical": True
    },
    "com.thecalltaker.demo-booking-run": {
        "script": "demo-booking-engine.py",
        "schedule": "Every 15 min",
        "critical": True
    },
    "com.thecalltaker.demo-booking-remind": {
        "script": "demo-booking-engine.py",
        "schedule": "Every 30 min",
        "critical": False
    },
}

def check_launchd_status(label):
    """Check if a launchd service is loaded and running."""
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split("\n"):
            if label in line:
                parts = line.split("\t")
                pid = parts[0] if parts[0] != "-" else None
                exit_code = parts[1] if len(parts) > 1 else "?"
                return {"loaded": True, "pid": pid, "exit_code": exit_code}
        return {"loaded": False, "pid": None, "exit_code": None}
    except Exception:
        return {"loaded": False, "pid": None, "exit_code": "error"}

def check_script_exists(script_name):
    """Check if the Python script file exists."""
    path = os.path.join(OPS_DIR, script_name)
    return os.path.exists(path)

def check_state_file(script_name):
    """Check if state file exists and is recent."""
    state_name = script_name.replace(".py", "-state.json")
    path = os.path.join(OPS_DIR, state_name)
    if not os.path.exists(path):
        return {"exists": False, "age_hours": None, "size": 0}
    stat = os.stat(path)
    age_hours = (time.time() - stat.st_mtime) / 3600
    return {"exists": True, "age_hours": round(age_hours, 1), "size": stat.st_size}

def run_health_check():
    """Run full health check across all services."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"  THE CALL TAKER — ENGINE HEALTH CHECK")
    print(f"  {now}")
    print(f"{'='*60}\n")

    total = len(SERVICES)
    healthy = 0
    warnings = 0
    critical_failures = 0
    results = []

    for label, info in SERVICES.items():
        status = check_launchd_status(label)
        script_ok = check_script_exists(info["script"])
        state = check_state_file(info["script"])

        # Determine health
        if not script_ok:
            health = "MISSING"
            icon = "\u274c"
        elif not status["loaded"]:
            health = "NOT LOADED"
            icon = "\u26a0\ufe0f"
        elif status["exit_code"] and status["exit_code"] not in ("0", "-", "?"):
            health = f"EXIT CODE {status['exit_code']}"
            icon = "\u274c"
        elif status["pid"]:
            health = "RUNNING"
            icon = "\u2705"
            healthy += 1
        else:
            health = "LOADED (waiting)"
            icon = "\u2705"
            healthy += 1

        if health in ("MISSING",) or (health.startswith("EXIT") and info["critical"]):
            critical_failures += 1
        elif health in ("NOT LOADED",):
            warnings += 1

        result = {
            "label": label.replace("com.thecalltaker.", ""),
            "health": health,
            "icon": icon,
            "script": info["script"],
            "schedule": info["schedule"],
            "critical": info["critical"],
            "state_exists": state["exists"],
            "state_age": state["age_hours"],
        }
        results.append(result)

        # Print status line
        crit_tag = " [CRITICAL]" if info["critical"] else ""
        state_info = ""
        if state["exists"]:
            state_info = f" | state: {state['age_hours']}h ago"
        print(f"  {icon} {result['label']:30s} {health:20s}{crit_tag}{state_info}")
        print(f"     Schedule: {info['schedule']}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY: {healthy}/{total} healthy | {warnings} warnings | {critical_failures} critical failures")
    print(f"{'='*60}")

    if critical_failures > 0:
        print(f"\n  ACTION REQUIRED: {critical_failures} critical service(s) need attention!")
        print(f"  Run: bash ~/thecalltaker/ops/activate-all-engines.sh")

    # Save report
    report = {
        "timestamp": now,
        "total": total,
        "healthy": healthy,
        "warnings": warnings,
        "critical_failures": critical_failures,
        "services": results
    }
    report_path = os.path.join(OPS_DIR, "health-check-report.json")
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n  Report saved: {report_path}")
    except Exception as e:
        print(f"\n  Could not save report: {e}")

    print()
    return report

if __name__ == "__main__":
    run_health_check()
