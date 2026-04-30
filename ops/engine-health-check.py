#!/usr/bin/env python3
"""
THE CALL TAKER — Morning System Health Check

Current-source-of-truth diagnostic for the live stack:
  - Production CTOS/app health
  - Public funnel preflight
  - Local booking/payment listeners
  - Critical launchd agents for booking flows
  - Legacy launchd/engine drift (demoted to context, not primary truth)

Run:
  python3 ~/thecalltaker/ops/engine-health-check.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.home() / "thecalltaker"
OPS_REPO = Path.home() / "thecalltaker-ops"
OPS_DIR = OPS_REPO / "ops" if (OPS_REPO / "ops").is_dir() else ROOT / "ops"
REPORT_PATH = OPS_DIR / "health-check-report.json"

APP_HEALTH_URL = "https://thecalltaker.vercel.app/api/health"
STRIPE_WEBHOOK_HEALTH_URL = "http://127.0.0.1:8787/health"
DEMO_WEBHOOK_HEALTH_URL = "http://127.0.0.1:5089/health"

CRITICAL_AGENTS = [
    ("Stripe webhook listener", "com.thecalltaker.ops.webhook"),
    ("Demo webhook listener", "com.thecalltaker.demo-webhook"),
    ("Demo booking run", "com.thecalltaker.demo-booking-run"),
    ("Demo booking reminder", "com.thecalltaker.demo-booking-remind"),
    ("CTOS cold-call planner", "com.thecalltaker.ctos.cold-call-planner"),
    ("CTOS hot-lead converter", "com.thecalltaker.ctos.hot-lead-converter"),
]

LEGACY_SERVICES = {
    "com.thecalltaker.hot-lead-converter": "hot-lead-converter.py",
    "com.thecalltaker.blast-engine-v2": "blast-engine-v2.py",
    "com.thecalltaker.outbound-sms": "outbound-sms-engine.py",
    "com.thecalltaker.storm-chaser-v2": "storm-chaser-v2.py",
    "com.thecalltaker.payment-reminder": "payment-reminder-engine.py",
    "com.thecalltaker.dm-tracker": "dm-tracker.py",
    "com.thecalltaker.lead-dashboard": "lead-dashboard-api.py",
    "com.thecalltaker.blast-sms-followup": "blast-sms-followup.py",
}
OUTREACH_AUDIT_SCRIPT = OPS_REPO / "ops" / "outreach-engine-audit.py"
OUTREACH_AUDIT_REPORT = OPS_REPO / "ops" / "outreach-engine-report.json"
LEGACY_AUDIT_SCRIPT = ROOT / "ops" / "legacy-engine-audit.py"
LEGACY_AUDIT_REPORT = OPS_REPO / "ops" / "legacy-engine-report.json"
NTFY_TRUST_AUDIT_SCRIPT = ROOT / "ops" / "ntfy-trust-audit.py"
NTFY_TRUST_AUDIT_REPORT = OPS_REPO / "ops" / "ntfy-trust-report.json"
NTFY_NOISE_AUDIT_SCRIPT = ROOT / "ops" / "ntfy-noise-recovery-audit.py"
NTFY_NOISE_AUDIT_REPORT = OPS_REPO / "ops" / "ntfy-noise-recovery-report.json"
NTFY_DIRECT_AUDIT_SCRIPT = ROOT / "ops" / "ntfy-direct-send-audit.py"
NTFY_DIRECT_AUDIT_REPORT = OPS_REPO / "ops" / "ntfy-direct-send-report.json"
TELEGRAM_POLLER_AUDIT_SCRIPT = OPS_REPO / "ops" / "telegram-poller-audit.py"
TELEGRAM_POLLER_AUDIT_REPORT = OPS_REPO / "ops" / "telegram-poller-audit-report.json"
PRODUCTION_WORKFORCE = {
    "workflow_events_ok": None,
    "workflow_events_24h": None,
}


def _print_header() -> None:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 60)
    print("  THE CALL TAKER — MORNING SYSTEM HEALTH CHECK")
    print(f"  {now}")
    print("=" * 60 + "\n")


def _check(label: str, ok: bool, detail: str = "", tone: str = "primary") -> dict:
    status = "PASS" if ok else "FAIL"
    icon = "✅" if ok else ("⚠️" if tone == "legacy" else "❌")
    line = f"[{status}] {label}"
    if detail:
        line += f" — {detail}"
    print(f"{icon} {line}")
    return {"label": label, "status": status, "detail": detail, "tone": tone}


def _run(cmd: list[str], timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _launchd_loaded(label: str) -> bool:
    try:
        out = subprocess.check_output(["launchctl", "list"], text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        out = ""
    if label in out:
        return True
    try:
        out = subprocess.check_output(
            ["launchctl", "print", f"gui/{ROOT.stat().st_uid}"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=12,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return label in out


def _http_json(url: str, timeout: float = 5.0) -> tuple[bool, str, dict | None]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(200000).decode("utf-8", errors="replace")
            parsed = json.loads(body) if body else None
            return resp.status == 200, f"HTTP {resp.status}", parsed
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}", None
    except Exception as e:
        return False, str(e)[:200], None


def check_production_app(results: list[dict]) -> bool:
    ok, detail, payload = _http_json(APP_HEALTH_URL, timeout=8.0)
    if ok and isinstance(payload, dict):
        status = payload.get("status", "unknown")
        build_sha = str(payload.get("build_sha", "dev"))[:7]
        crons = payload.get("crons", {})
        stale = []
        if isinstance(crons, dict):
            for cron_name, row in crons.items():
                if isinstance(row, dict) and row.get("stale"):
                    stale.append(cron_name)
        detail = f"status={status} build={build_sha}"
        if stale:
            detail += f" stale={','.join(stale[:3])}"
        workforce = payload.get("workforce", {})
        if isinstance(workforce, dict):
            PRODUCTION_WORKFORCE["workflow_events_ok"] = workforce.get("workflow_events_ok")
            PRODUCTION_WORKFORCE["workflow_events_24h"] = workforce.get("workflow_events_24h")
            if workforce.get("workflow_events_ok") is False:
                detail += " workflow-events=broken"
            elif workforce.get("workflow_events_24h") is not None:
                detail += f" workflow-events-24h={workforce.get('workflow_events_24h')}"
        results.append(_check("Production app health", status == "ok", detail))
        return status == "ok"
    results.append(_check("Production app health", False, detail))
    return False


def check_public_preflight(results: list[dict]) -> bool:
    script = ROOT / "ops" / "ads-preflight.sh"
    proc = _run(["zsh", str(script)], timeout=30.0)
    ok = proc.returncode == 0
    detail = "legacy patterns clean + public pages reachable" if ok else "public preflight failed"
    results.append(_check("Public funnel preflight", ok, detail))
    return ok


def check_local_listener(url: str, label: str, results: list[dict]) -> bool:
    ok, detail, payload = _http_json(url, timeout=3.0)
    if ok and isinstance(payload, dict):
        status = payload.get("status", "ok")
        service = payload.get("service", label)
        detail = f"{service} {status}"
        results.append(_check(label, True, detail))
        return True
    results.append(_check(label, False, detail))
    return False


def check_critical_agents(results: list[dict]) -> tuple[int, int]:
    passed = 0
    total = 0
    for label, plist in CRITICAL_AGENTS:
        total += 1
        ok = _launchd_loaded(plist)
        results.append(_check(label, ok, "loaded in launchctl" if ok else "not loaded"))
        if ok:
            passed += 1
    return passed, total


def check_booking_payment(results: list[dict]) -> bool:
    script = OPS_REPO / "ops" / "booking-payment-health-check.py"
    proc = _run(["python3", str(script)], timeout=45.0)
    ok = proc.returncode == 0
    report_path = OPS_REPO / "reports" / "booking-payment-health.json"
    detail = "8/8 healthy" if ok else "see booking-payment-health.json"
    if report_path.is_file():
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            detail = f"{data.get('passed', '?')}/{data.get('total', '?')} healthy"
        except Exception:
            pass
    results.append(_check("Booking/payment stack", ok, detail))
    return ok


def check_ntfy_trust(results: list[dict]) -> bool:
    if not NTFY_TRUST_AUDIT_SCRIPT.is_file():
        results.append(_check("NTFY trust audit", False, "audit script missing"))
        return False

    proc = _run(["python3", str(NTFY_TRUST_AUDIT_SCRIPT)], timeout=30.0)
    ok = proc.returncode == 0
    detail = "public browser files cannot post directly to ntfy"
    if NTFY_TRUST_AUDIT_REPORT.is_file():
        try:
            data = json.loads(NTFY_TRUST_AUDIT_REPORT.read_text(encoding="utf-8"))
            detail = f"{data.get('violations_total', '?')} browser-side direct posts"
        except Exception:
            detail = "report unreadable"
            ok = False
    results.append(_check("NTFY trust audit", ok, detail))
    return ok


def check_ntfy_noise_recovery(results: list[dict]) -> bool:
    if not NTFY_NOISE_AUDIT_SCRIPT.is_file():
        results.append(_check("NTFY stale-alert recovery audit", False, "audit script missing"))
        return False

    proc = _run(["python3", str(NTFY_NOISE_AUDIT_SCRIPT)], timeout=30.0)
    ok = proc.returncode == 0
    detail = "report missing"
    if NTFY_NOISE_AUDIT_REPORT.is_file():
        try:
            data = json.loads(NTFY_NOISE_AUDIT_REPORT.read_text(encoding="utf-8"))
            detail = (
                f"{data.get('loaded_stale_alert_jobs', '?')} loaded stale-alert jobs, "
                f"{data.get('active_script_risks', '?')} active risky scripts, "
                f"{data.get('installed_stale_alert_plists', '?')} installed retired plists"
            )
        except Exception:
            detail = "report unreadable"
            ok = False
    results.append(_check("NTFY stale-alert recovery audit", ok, detail))
    return ok


def check_ntfy_direct_senders(results: list[dict]) -> bool:
    if not NTFY_DIRECT_AUDIT_SCRIPT.is_file():
        results.append(_check("NTFY direct-send audit", False, "audit script missing"))
        return False

    try:
        proc = _run(["python3", str(NTFY_DIRECT_AUDIT_SCRIPT)], timeout=120.0)
    except subprocess.TimeoutExpired:
        results.append(_check("NTFY direct-send audit", False, "audit timed out"))
        return False
    ok = proc.returncode == 0
    detail = "report missing"
    if NTFY_DIRECT_AUDIT_REPORT.is_file():
        try:
            data = json.loads(NTFY_DIRECT_AUDIT_REPORT.read_text(encoding="utf-8"))
            detail = (
                f"{data.get('active_blocking_total', '?')} loaded direct senders, "
                f"{data.get('launch_agent_findings_total', '?')} launchd findings, "
                f"{data.get('source_untrusted_direct_files_total', '?')} untrusted source files"
            )
        except Exception:
            detail = "report unreadable"
            ok = False
    results.append(_check("NTFY direct-send audit", ok, detail))
    return ok


def check_telegram_poller(results: list[dict]) -> bool:
    if not TELEGRAM_POLLER_AUDIT_SCRIPT.is_file():
        results.append(_check("Telegram poller audit", False, "audit script missing"))
        return False

    proc = _run(["python3", str(TELEGRAM_POLLER_AUDIT_SCRIPT)], timeout=30.0)
    ok = proc.returncode == 0
    detail = "report missing"
    if TELEGRAM_POLLER_AUDIT_REPORT.is_file():
        try:
            data = json.loads(TELEGRAM_POLLER_AUDIT_REPORT.read_text(encoding="utf-8"))
            detail = (
                f"{data.get('loaded_poller_count', '?')}/"
                f"{data.get('expected_loaded_poller_count', '?')} loaded, "
                f"{data.get('fresh_conflict_count', '?')} fresh conflicts, "
                f"{data.get('secret_plist_count', '?')} secret plists"
            )
        except Exception:
            detail = "report unreadable"
            ok = False
    results.append(_check("Telegram poller audit", ok, detail))
    return ok


def check_legacy_drift(results: list[dict]) -> dict:
    if not LEGACY_AUDIT_SCRIPT.is_file():
        results.append(_check("Legacy engine audit", False, "audit script missing", tone="legacy"))
        return {"engines_total": 0, "blocked_legacy_crm": 0, "blocked_stale_path": 0, "loaded_labels_total": 0, "orphan_plists_total": 0}

    _run(["python3", str(LEGACY_AUDIT_SCRIPT)], timeout=30.0)
    if not LEGACY_AUDIT_REPORT.is_file():
        results.append(_check("Legacy engine audit", False, "report missing", tone="legacy"))
        return {"engines_total": 0, "blocked_legacy_crm": 0, "blocked_stale_path": 0, "loaded_labels_total": 0, "orphan_plists_total": 0}

    try:
        data = json.loads(LEGACY_AUDIT_REPORT.read_text(encoding="utf-8"))
    except Exception:
        results.append(_check("Legacy engine audit", False, "report unreadable", tone="legacy"))
        return {"engines_total": 0, "blocked_legacy_crm": 0, "blocked_stale_path": 0, "loaded_labels_total": 0, "orphan_plists_total": 0}

    total = int(data.get("engines_total", 0))
    blocked_legacy = int(data.get("blocked_legacy_crm", 0))
    blocked_path = int(data.get("blocked_stale_path", 0))
    loaded = int(data.get("loaded_labels_total", 0))
    orphan_plists = int(data.get("orphan_plists_total", 0))
    ok = loaded == 0
    detail = (
        f"{total} audited, {blocked_legacy} blocked by legacy CRM, "
        f"{blocked_path} stale path, {loaded} loaded zombies, {orphan_plists} orphan plists"
    )
    results.append(_check("Legacy engine audit", ok, detail, tone="legacy"))
    return data


def check_outreach_engines(results: list[dict]) -> tuple[int, int, int]:
    if not OUTREACH_AUDIT_SCRIPT.is_file():
        results.append(_check("Outreach engine audit", False, "audit script missing"))
        return 0, 0, 0

    _run(["python3", str(OUTREACH_AUDIT_SCRIPT)], timeout=30.0)
    if not OUTREACH_AUDIT_REPORT.is_file():
        results.append(_check("Outreach engine audit", False, "report missing"))
        return 0, 0, 0

    try:
        data = json.loads(OUTREACH_AUDIT_REPORT.read_text(encoding="utf-8"))
    except Exception:
        results.append(_check("Outreach engine audit", False, "report unreadable"))
        return 0, 0, 0

    fresh = int(data.get("active_fresh", 0))
    stale = int(data.get("active_stale", 0))
    missing = int(data.get("active_missing", 0))
    total = int(data.get("active_total", 0))
    ok = stale == 0 and missing == 0 and total > 0
    detail = f"{fresh}/{total} fresh, {stale} stale, {missing} missing"
    results.append(_check("Outreach engine audit", ok, detail))
    return fresh, stale, missing


def write_report(report: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    _print_header()

    results: list[dict] = []
    production_ok = check_production_app(results)
    preflight_ok = check_public_preflight(results)
    stripe_listener_ok = check_local_listener(
        STRIPE_WEBHOOK_HEALTH_URL, "Local Stripe webhook listener", results
    )
    demo_listener_ok = check_local_listener(
        DEMO_WEBHOOK_HEALTH_URL, "Local demo webhook listener", results
    )
    critical_agents_passed, critical_agents_total = check_critical_agents(results)
    booking_ok = check_booking_payment(results)
    ntfy_trust_ok = check_ntfy_trust(results)
    ntfy_noise_ok = check_ntfy_noise_recovery(results)
    ntfy_direct_ok = check_ntfy_direct_senders(results)
    telegram_poller_ok = check_telegram_poller(results)
    outreach_fresh, outreach_stale, outreach_missing = check_outreach_engines(results)
    legacy_report = check_legacy_drift(results)

    core_checks = [
        production_ok,
        preflight_ok,
        stripe_listener_ok,
        demo_listener_ok,
        critical_agents_passed == critical_agents_total,
        booking_ok,
        ntfy_trust_ok,
        ntfy_noise_ok,
        ntfy_direct_ok,
        telegram_poller_ok,
        outreach_stale == 0 and outreach_missing == 0 and outreach_fresh > 0,
    ]
    core_healthy = sum(1 for item in core_checks if item)
    core_total = len(core_checks)

    print("\n" + "=" * 60)
    print(f"  CORE STACK: {core_healthy}/{core_total} healthy")
    print(f"  CRITICAL AGENTS: {critical_agents_passed}/{critical_agents_total} loaded")
    print(
        "  LEGACY AUDIT: "
        f"{legacy_report.get('engines_total', 0)} tracked, "
        f"{legacy_report.get('blocked_legacy_crm', 0)} legacy-CRM blocked, "
        f"{legacy_report.get('blocked_stale_path', 0)} stale-path, "
        f"{legacy_report.get('loaded_labels_total', 0)} loaded zombies"
    )
    print("=" * 60)

    if core_healthy == core_total:
        print("\n  LIVE CALL TAKER STACK IS GREEN.")
    else:
        print("\n  ACTION REQUIRED: one or more current-stack checks are failing.")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_healthy": core_healthy,
        "core_total": core_total,
        "critical_agents_loaded": critical_agents_passed,
        "critical_agents_total": critical_agents_total,
        "outreach_fresh": outreach_fresh,
        "outreach_stale": outreach_stale,
        "outreach_missing": outreach_missing,
        "workflow_events_ok": PRODUCTION_WORKFORCE.get("workflow_events_ok"),
        "workflow_events_24h": PRODUCTION_WORKFORCE.get("workflow_events_24h"),
        "legacy_engines_total": legacy_report.get("engines_total", 0),
        "legacy_blocked_legacy_crm": legacy_report.get("blocked_legacy_crm", 0),
        "legacy_blocked_stale_path": legacy_report.get("blocked_stale_path", 0),
        "legacy_loaded_labels_total": legacy_report.get("loaded_labels_total", 0),
        "legacy_orphan_plists_total": legacy_report.get("orphan_plists_total", 0),
        "checks": results,
    }
    write_report(report)
    print(f"\n  Report saved: {REPORT_PATH}\n")
    return 0 if core_healthy == core_total else 1


if __name__ == "__main__":
    sys.exit(main())
