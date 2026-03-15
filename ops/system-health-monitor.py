#!/usr/bin/env python3
"""
THE CALL TAKER — System-Wide Health Monitor (Component 8)
==========================================================
Checks health of every outreach component every 30 minutes.
Writes status to ~/thecalltaker/ops/system-health.json.
Sends SMS + ntfy SYSTEM alert if any component goes RED.

Commands:
  check   — Run a single health check pass and write results
  watch   — Continuous 30-minute loop (blocks; use launchd instead)
  status  — Print current system-health.json to terminal
  test    — Send a test ntfy + SMS alert to confirm alerting works

Schedule: Every 30 minutes via launchd
"""

import sys
import os
import json
import time
import logging
import requests
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────

OPS_DIR          = os.path.expanduser("~/thecalltaker/ops")
HEALTH_FILE      = os.path.join(OPS_DIR, "system-health.json")
ERROR_LOG_FILE   = os.path.join(OPS_DIR, "errors.json")
LOG_FILE         = os.path.join(OPS_DIR, "system-health.log")

# ─── GHL / Notification Config ───────────────────────────────────────────────

GHL_API_KEY      = os.environ.get("TCT_GHL_API_KEY",      "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35")
GHL_LOCATION_ID  = os.environ.get("TCT_GHL_LOCATION_ID",  "tQb9YmrGDrdVUJYPKrsY")
GHL_BASE_URL     = "https://services.leadconnectorhq.com"
WALLACE_GHL_ID   = "DtKLG28VzgUb6q3brILD"
WALLACE_PHONE    = "+16156539004"

NTFY_SYSTEM      = "tct-system-vRsfXQRQ"
NTFY_URGENT      = "tct-urgent-Hk9UOEZR"
NTFY_BASE        = "https://ntfy.sh"

# ─── Component Definitions ───────────────────────────────────────────────────
#
# Each component maps to either:
#   - A heartbeat file (timestamp written on every successful run), OR
#   - A state JSON file with a stats.last_run ISO timestamp field
#
# interval_minutes: how often the component SHOULD run
# check_type: "heartbeat" | "state_last_run"
# file: absolute path to the file we inspect

COMPONENTS = {
    "hot-lead-converter": {
        "display_name": "Hot Lead Converter",
        "version": "v2",
        "interval_minutes": 15,
        "check_type": "heartbeat",
        "file": os.path.join(OPS_DIR, "hot-lead-converter.heartbeat"),
        "critical": True,
        "description": "5-touch hot lead follow-up machine",
    },
    "storm-chaser": {
        "display_name": "Storm Chaser",
        "version": "v3",
        "interval_minutes": 360,          # 6 hours
        "check_type": "state_last_run",
        "file": os.path.join(OPS_DIR, "storm-chaser-state.json"),
        "critical": False,
        "description": "Weather-triggered urgency outreach",
    },
    "blast-engine": {
        "display_name": "Blast Engine",
        "version": "v3",
        "interval_minutes": 480,          # 8 hours (3x daily)
        "check_type": "state_last_run",
        "file": os.path.join(OPS_DIR, "blast-engine-state.json"),
        "critical": True,
        "description": "Cold email with A/B testing + warmup ramp",
    },
    "cold-caller": {
        "display_name": "Cold Caller",
        "version": "v2",
        "interval_minutes": 300,          # 5 hours (2x daily)
        "check_type": "state_last_run",
        "file": os.path.join(OPS_DIR, "cold-caller-state.json"),
        "critical": True,
        "description": "Bland.ai outbound calling engine",
    },
    "speed-to-lead": {
        "display_name": "Speed-to-Lead",
        "version": "v2",
        "interval_minutes": 1,            # every minute
        "check_type": "heartbeat",
        "file": os.path.join(OPS_DIR, "speed-to-lead.heartbeat"),
        "critical": True,
        "description": "Hot-signal detector + instant SMS/ntfy",
    },
    "dm-outreach": {
        "display_name": "DM Outreach",
        "version": "v2",
        "interval_minutes": 1440,         # 24 hours
        "check_type": "state_last_run",
        "file": os.path.join(OPS_DIR, "dm-tracker-state.json"),
        "critical": False,
        "description": "Instagram / social DM sequence engine",
    },
    "lead-quality": {
        "display_name": "Lead Quality Engine",
        "version": "v1",
        "interval_minutes": 1440,         # 24 hours
        "check_type": "state_last_run",
        "file": os.path.join(OPS_DIR, "lead-quality-state.json"),
        "critical": False,
        "description": "Scores and enriches incoming leads",
    },
}

# ─── Logging Setup ────────────────────────────────────────────────────────────

os.makedirs(OPS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("system-health-monitor")

# ─── Helper: Read ISO timestamp from state JSON ───────────────────────────────

def _read_state_last_run(state_file: str) -> datetime | None:
    """Return the last_run datetime from a state JSON, or None if unreadable."""
    if not os.path.exists(state_file):
        return None
    try:
        with open(state_file, "r") as f:
            data = json.load(f)
        # Support nested stats.last_run or top-level last_run
        raw = None
        if isinstance(data.get("stats"), dict):
            raw = data["stats"].get("last_run")
        if raw is None:
            raw = data.get("last_run")
        if raw is None:
            return None
        return datetime.fromisoformat(raw)
    except Exception:
        return None

# ─── Helper: Read heartbeat file mtime ───────────────────────────────────────

def _read_heartbeat_mtime(heartbeat_file: str) -> datetime | None:
    """Return the mtime of the heartbeat file as a datetime, or None."""
    if not os.path.exists(heartbeat_file):
        return None
    try:
        mtime = os.path.getmtime(heartbeat_file)
        return datetime.fromtimestamp(mtime)
    except Exception:
        return None

# ─── Core: Evaluate one component ────────────────────────────────────────────

STATUS_GREEN  = "green"
STATUS_YELLOW = "yellow"
STATUS_RED    = "red"


def check_component(key: str, cfg: dict) -> dict:
    """
    Returns a status dict for a single component.
    {
      "key": str,
      "display_name": str,
      "version": str,
      "status": "green"|"yellow"|"red",
      "status_label": "HEALTHY"|"DEGRADED"|"DOWN",
      "last_run": ISO str | None,
      "age_minutes": float | None,
      "interval_minutes": int,
      "message": str,
      "critical": bool,
      "description": str,
    }
    """
    interval = cfg["interval_minutes"]

    # Determine the last-run timestamp
    last_run_dt: datetime | None = None
    file_exists = os.path.exists(cfg["file"])

    if cfg["check_type"] == "heartbeat":
        last_run_dt = _read_heartbeat_mtime(cfg["file"])
    elif cfg["check_type"] == "state_last_run":
        last_run_dt = _read_state_last_run(cfg["file"])
        # Fallback: use file mtime if last_run key not found but file exists
        if last_run_dt is None and file_exists:
            try:
                mtime = os.path.getmtime(cfg["file"])
                last_run_dt = datetime.fromtimestamp(mtime)
            except Exception:
                pass

    now = datetime.now()

    if last_run_dt is None:
        # File missing entirely or completely unreadable
        status = STATUS_RED
        status_label = "DOWN"
        age_minutes = None
        if not file_exists:
            message = "No heartbeat/state file found — never ran or path wrong"
        else:
            message = "File exists but last_run timestamp unreadable"
    else:
        age_minutes = (now - last_run_dt).total_seconds() / 60

        if age_minutes <= interval:
            status = STATUS_GREEN
            status_label = "HEALTHY"
            message = f"Ran {_fmt_age(age_minutes)} ago (within {_fmt_interval(interval)} window)"
        elif age_minutes <= interval * 2:
            status = STATUS_YELLOW
            status_label = "DEGRADED"
            message = f"Overdue — last ran {_fmt_age(age_minutes)} ago (expected every {_fmt_interval(interval)})"
        else:
            status = STATUS_RED
            status_label = "DOWN"
            message = f"No run in {_fmt_age(age_minutes)} — threshold {_fmt_interval(interval * 2)} exceeded"

    return {
        "key": key,
        "display_name": cfg["display_name"],
        "version": cfg["version"],
        "status": status,
        "status_label": status_label,
        "last_run": last_run_dt.isoformat() if last_run_dt else None,
        "age_minutes": round(age_minutes, 1) if age_minutes is not None else None,
        "interval_minutes": interval,
        "message": message,
        "critical": cfg["critical"],
        "description": cfg["description"],
    }


def _fmt_age(minutes: float) -> str:
    """Human-readable age string."""
    if minutes < 1:
        return f"{int(minutes * 60)}s"
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def _fmt_interval(minutes: int) -> str:
    """Human-readable interval string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)}h"
    return f"{hours / 24:.0f}d"

# ─── Error Log ────────────────────────────────────────────────────────────────

def log_error(service: str, message: str):
    """Append an error entry to errors.json (keeps last 100 entries)."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "service": service,
        "message": message,
    }
    log.error(f"[{service}] {message}")

    errors = []
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE, "r") as f:
                errors = json.load(f)
            if not isinstance(errors, list):
                errors = []
        except Exception:
            errors = []

    errors.append(entry)
    errors = errors[-100:]  # keep last 100

    try:
        tmp = ERROR_LOG_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(errors, f, indent=2)
        os.replace(tmp, ERROR_LOG_FILE)
    except Exception as e:
        log.error(f"Could not write errors.json: {e}")

# ─── GHL SMS ──────────────────────────────────────────────────────────────────

def _ghl_headers() -> dict:
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-04-15",
        "User-Agent": "TheCallTaker-HealthMonitor/1.0",
    }


def send_sms_to_wallace(message: str) -> bool:
    """Send an SMS to Wallace via GHL conversations API."""
    url = f"{GHL_BASE_URL}/conversations/messages"
    payload = {
        "type": "SMS",
        "contactId": WALLACE_GHL_ID,
        "message": message,
        "locationId": GHL_LOCATION_ID,
    }
    for attempt in range(3):
        try:
            r = requests.post(url, headers=_ghl_headers(), json=payload, timeout=15)
            if r.status_code in (200, 201):
                log.info(f"SMS sent to Wallace: {message[:60]}...")
                return True
            elif r.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"GHL rate-limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                log.error(f"GHL SMS failed {r.status_code}: {r.text[:200]}")
                break
        except Exception as e:
            log.error(f"GHL SMS exception attempt {attempt + 1}: {e}")
            if attempt < 2:
                time.sleep(5)
    return False


def send_ntfy(topic: str, title: str, message: str, priority: str = "high") -> bool:
    """Send an ntfy notification."""
    url = f"{NTFY_BASE}/{topic}"
    headers = {
        "Title": title[:250],
        "Priority": priority,
        "Content-Type": "text/plain",
    }
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, data=message.encode("utf-8"), timeout=10)
            if r.status_code == 200:
                log.info(f"ntfy sent [{topic}]: {title}")
                return True
            else:
                log.warning(f"ntfy {r.status_code} attempt {attempt + 1}")
        except Exception as e:
            log.warning(f"ntfy exception attempt {attempt + 1}: {e}")
            if attempt < 2:
                time.sleep(3)
    return False

# ─── Alerting ─────────────────────────────────────────────────────────────────

# Track which components we've already alerted on in this run
# (Across runs, we only re-alert if the component recovers then fails again —
#  managed via the "alerted" flag in system-health.json)

def fire_red_alerts(red_components: list[dict], previous_health: dict):
    """
    Fire SMS + ntfy for components that are newly RED.
    'Newly RED' = currently red AND was not already red in previous_health
    (so we don't spam on every 30-min check).
    """
    prev_statuses = {
        c["key"]: c["status"]
        for c in previous_health.get("components", [])
    }

    newly_red = [
        c for c in red_components
        if prev_statuses.get(c["key"]) != STATUS_RED
    ]

    if not newly_red:
        log.info("Red components exist but already alerted — skipping repeat alerts")
        return

    names = ", ".join(c["display_name"] for c in newly_red)
    critical_any = any(c["critical"] for c in newly_red)

    sms_msg = (
        f"[SYSTEM ALERT] {len(newly_red)} outreach engine(s) DOWN: {names}. "
        f"Check ~/thecalltaker/ops/system-health.json"
    )

    ntfy_title = f"[CRITICAL] {len(newly_red)} Engine(s) DOWN" if critical_any else f"[HIGH] {len(newly_red)} Engine(s) DOWN"
    ntfy_body = "\n".join(
        f"- {c['display_name']}: {c['message']}"
        for c in newly_red
    )
    ntfy_body += f"\n\nCheck: ~/thecalltaker/ops/system-health.json"
    ntfy_priority = "urgent" if critical_any else "high"

    send_sms_to_wallace(sms_msg)
    send_ntfy(NTFY_SYSTEM, ntfy_title, ntfy_body, ntfy_priority)

    for c in newly_red:
        log_error(c["display_name"], c["message"])

# ─── State I/O ────────────────────────────────────────────────────────────────

def _load_previous_health() -> dict:
    if not os.path.exists(HEALTH_FILE):
        return {}
    try:
        with open(HEALTH_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_health(data: dict):
    tmp = HEALTH_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, HEALTH_FILE)
    except Exception as e:
        log.error(f"Could not write system-health.json: {e}")

# ─── Aggregate Stats from State Files ────────────────────────────────────────

def _safe_int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _read_today_stats() -> dict:
    """
    Best-effort read of today's send counts from each engine's state file.
    Keys: emails_sent, sms_sent, calls_made, dms_generated, leads_scored
    """
    today = datetime.now().date().isoformat()
    stats = {
        "emails_sent": 0,
        "sms_sent": 0,
        "calls_made": 0,
        "dms_generated": 0,
        "leads_scored": 0,
    }

    # Blast engine
    blast_state = os.path.join(OPS_DIR, "blast-engine-state.json")
    if os.path.exists(blast_state):
        try:
            with open(blast_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            # Try daily_sent first, fall back to total_sent
            stats["emails_sent"] += _safe_int(s.get("daily_sent") or s.get("total_sent", 0))
        except Exception:
            pass

    # Outbound SMS engine
    sms_state = os.path.join(OPS_DIR, "outbound-sms-state.json")
    if os.path.exists(sms_state):
        try:
            with open(sms_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["sms_sent"] += _safe_int(s.get("daily_sent") or s.get("total_sent", 0))
        except Exception:
            pass

    # Blast SMS followup
    sms_followup_state = os.path.join(OPS_DIR, "blast-sms-followup-state.json")
    if os.path.exists(sms_followup_state):
        try:
            with open(sms_followup_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["sms_sent"] += _safe_int(s.get("daily_sent") or s.get("total_sent", 0))
        except Exception:
            pass

    # Hot lead converter SMS touches
    hlc_state = os.path.join(OPS_DIR, "hot-lead-converter-state.json")
    if os.path.exists(hlc_state):
        try:
            with open(hlc_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["sms_sent"] += _safe_int(s.get("sms_sent", 0))
            stats["emails_sent"] += _safe_int(s.get("emails_sent", 0))
        except Exception:
            pass

    # Cold caller
    cold_state = os.path.join(OPS_DIR, "cold-caller-state.json")
    if os.path.exists(cold_state):
        try:
            with open(cold_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["calls_made"] += _safe_int(s.get("daily_calls") or s.get("total_calls", 0))
        except Exception:
            pass

    # DM tracker
    dm_state = os.path.join(OPS_DIR, "dm-tracker-state.json")
    if os.path.exists(dm_state):
        try:
            with open(dm_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["dms_generated"] += _safe_int(s.get("daily_sent") or s.get("total_sent", 0))
        except Exception:
            pass

    # Lead quality
    lq_state = os.path.join(OPS_DIR, "lead-quality-state.json")
    if os.path.exists(lq_state):
        try:
            with open(lq_state) as f:
                d = json.load(f)
            s = d.get("stats", {})
            stats["leads_scored"] += _safe_int(s.get("daily_scored") or s.get("total_scored", 0))
        except Exception:
            pass

    return stats

# ─── Main Check ───────────────────────────────────────────────────────────────

def run_check() -> dict:
    """Run a full health check and write results to system-health.json."""
    log.info("Starting health check...")
    previous = _load_previous_health()

    component_results = []
    red = []
    yellow = []
    green = []

    for key, cfg in COMPONENTS.items():
        result = check_component(key, cfg)
        component_results.append(result)

        if result["status"] == STATUS_RED:
            red.append(result)
        elif result["status"] == STATUS_YELLOW:
            yellow.append(result)
        else:
            green.append(result)

        log.info(
            f"  {result['display_name']:25s} {result['status_label']:8s} "
            f"{'('+_fmt_age(result['age_minutes'])+' ago)' if result['age_minutes'] is not None else '(no data)'}"
        )

    today_stats = _read_today_stats()

    # Load recent errors for embedding in health file
    recent_errors = []
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE) as f:
                all_errors = json.load(f)
            recent_errors = all_errors[-10:] if isinstance(all_errors, list) else []
        except Exception:
            pass

    health_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total": len(component_results),
            "green": len(green),
            "yellow": len(yellow),
            "red": len(red),
            "overall_status": (
                STATUS_RED    if red    else
                STATUS_YELLOW if yellow else
                STATUS_GREEN
            ),
        },
        "today_stats": today_stats,
        "components": component_results,
        "recent_errors": recent_errors,
    }

    _write_health(health_data)
    log.info(
        f"Health check complete: {len(green)} healthy, "
        f"{len(yellow)} degraded, {len(red)} down"
    )

    # Fire alerts for newly-red components
    if red:
        fire_red_alerts(red, previous)

    return health_data

# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_check():
    """Single health check pass."""
    data = run_check()
    summary = data["summary"]
    print(f"\nSystem Health: {summary['overall_status'].upper()}")
    print(f"  Green: {summary['green']}  Yellow: {summary['yellow']}  Red: {summary['red']}")
    print(f"  Results written to: {HEALTH_FILE}")
    if summary["red"] > 0:
        print(f"\n  RED COMPONENTS:")
        for c in data["components"]:
            if c["status"] == STATUS_RED:
                print(f"    - {c['display_name']}: {c['message']}")


def cmd_watch():
    """Continuous 30-minute loop."""
    log.info("Starting watch mode (30-minute interval). Ctrl+C to stop.")
    while True:
        try:
            run_check()
        except Exception as e:
            log.error(f"Health check loop error: {e}")
            log_error("system-health-monitor", str(e))
        log.info("Sleeping 30 minutes until next check...")
        time.sleep(30 * 60)


def cmd_status():
    """Print current system-health.json to terminal."""
    if not os.path.exists(HEALTH_FILE):
        print(f"No health data found at {HEALTH_FILE}")
        print("Run:  python3 system-health-monitor.py check")
        return

    with open(HEALTH_FILE) as f:
        data = json.load(f)

    gen = data.get("generated_at", "unknown")
    summary = data.get("summary", {})
    stats = data.get("today_stats", {})
    components = data.get("components", [])
    errors = data.get("recent_errors", [])

    STATUS_SYMBOL = {STATUS_GREEN: "[G]", STATUS_YELLOW: "[Y]", STATUS_RED: "[R]"}

    print(f"\n{'='*58}")
    print(f"  THE CALL TAKER — OUTREACH COMMAND CENTER")
    print(f"  Generated: {gen[:16]}")
    print(f"  Overall:   {summary.get('overall_status', '?').upper()}")
    print(f"{'='*58}\n")

    for c in components:
        sym = STATUS_SYMBOL.get(c["status"], "[?]")
        age_str = f"{_fmt_age(c['age_minutes'])} ago" if c["age_minutes"] is not None else "no data"
        crit = " [CRITICAL]" if c["critical"] else ""
        print(f"  {sym} {c['display_name']+' '+c['version']:30s} {c['status_label']:8s}  {age_str}{crit}")

    print(f"\n  -- TODAY'S STATS --")
    print(f"  Emails: {stats.get('emails_sent', 0)}  "
          f"SMS: {stats.get('sms_sent', 0)}  "
          f"Calls: {stats.get('calls_made', 0)}  "
          f"DMs: {stats.get('dms_generated', 0)}  "
          f"Leads Scored: {stats.get('leads_scored', 0)}")

    if errors:
        print(f"\n  -- RECENT ERRORS (last {len(errors)}) --")
        for e in errors[-5:]:
            ts = e.get("timestamp", "")[:16]
            svc = e.get("service", "?")
            msg = e.get("message", "")[:60]
            print(f"  [{ts}] {svc}: {msg}")

    print(f"\n  Green: {summary.get('green', 0)}  "
          f"Yellow: {summary.get('yellow', 0)}  "
          f"Red: {summary.get('red', 0)}")
    print(f"{'='*58}\n")


def cmd_test():
    """Send a test SMS + ntfy to confirm alerting works."""
    msg = "[TEST] system-health-monitor alerting is working correctly. Ignore this message."
    print("Sending test SMS to Wallace...")
    ok_sms = send_sms_to_wallace(msg)
    print(f"  SMS: {'OK' if ok_sms else 'FAILED'}")

    print("Sending test ntfy to SYSTEM topic...")
    ok_ntfy = send_ntfy(NTFY_SYSTEM, "[TEST] Health Monitor", msg, priority="low")
    print(f"  ntfy: {'OK' if ok_ntfy else 'FAILED'}")

    if ok_sms and ok_ntfy:
        print("\nTest passed. Both channels working.")
    else:
        print("\nTest FAILED on one or more channels. Check logs.")

# ─── Entrypoint ───────────────────────────────────────────────────────────────

COMMANDS = {
    "check":  cmd_check,
    "watch":  cmd_watch,
    "status": cmd_status,
    "test":   cmd_test,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    try:
        COMMANDS[cmd]()
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    except Exception as e:
        log.critical(f"Unhandled exception in '{cmd}': {e}")
        log.critical(traceback.format_exc())
        log_error("system-health-monitor", f"Unhandled exception in '{cmd}': {e}")
        sys.exit(1)
