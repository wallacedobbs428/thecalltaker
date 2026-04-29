#!/usr/bin/env python3
"""
Audit stale NTFY/down-alert recovery risks.

This catches the class of issue where an old launchd monitor watches retired
heartbeat files and sends "ENGINE DOWN" phone alerts even though CTOS is healthy.

Run:
  python3 ~/thecalltaker/ops/ntfy-noise-recovery-audit.py
"""

from __future__ import annotations

import json
import plistlib
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


HOME = Path.home()
LAUNCH_AGENTS = HOME / "Library" / "LaunchAgents"
OPS_REPO = HOME / "thecalltaker-ops"
REPORT_PATH = OPS_REPO / "ops" / "ntfy-noise-recovery-report.json"

RETIRED_MONITOR_PATHS = {
    str(OPS_REPO / "ops" / "health-monitor.py"),
    str(OPS_REPO / "scripts" / "health-monitor.py"),
}
RETIRED_LABELS = {
    "com.thecalltaker.health.check",
    "com.thecalltaker.health.report",
    "com.thecalltaker.health.monitor",
}
DOWN_ALERT_PATTERNS = (
    "ENGINE DOWN",
    "last heartbeat",
    "health-monitor.py check",
    "health-monitor.py report",
)


def launchctl_labels() -> set[str]:
    try:
        proc = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=12)
    except Exception:
        return set()
    labels: set[str] = set()
    for line in proc.stdout.splitlines():
        parts = line.split()
        if parts:
            labels.add(parts[-1])
    return labels


def plist_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def plist_payload(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = plistlib.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def list_launch_agent_risks(loaded: set[str]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for path in sorted(LAUNCH_AGENTS.glob("com.thecalltaker*.plist")):
        payload = plist_payload(path)
        label = str(payload.get("Label") or path.stem)
        args = payload.get("ProgramArguments") or []
        args_text = " ".join(str(arg) for arg in args) if isinstance(args, list) else str(args)
        text = plist_text(path)
        haystack = f"{label}\n{args_text}\n{text}"
        retired_path = any(retired in haystack for retired in RETIRED_MONITOR_PATHS)
        retired_label = label in RETIRED_LABELS
        down_pattern = any(pattern in haystack for pattern in DOWN_ALERT_PATTERNS)
        if not (retired_path or retired_label or down_pattern):
            continue
        risks.append(
            {
                "label": label,
                "path": str(path),
                "loaded": label in loaded,
                "retired_label": retired_label,
                "retired_monitor_path": retired_path,
                "down_alert_pattern": down_pattern,
                "program_arguments": args if isinstance(args, list) else [],
            }
        )
    return risks


def recent_engine_down_lines() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    log_dir = OPS_REPO / "logs"
    cutoff = datetime.now().astimezone() - timedelta(hours=24)
    for path in sorted(log_dir.glob("*.log")):
        try:
            if datetime.fromtimestamp(path.stat().st_mtime).astimezone() < cutoff:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for line in lines[-500:]:
            if "ENGINE DOWN" not in line:
                continue
            out.append({"path": str(path), "line": line[-500:]})
    return out[-25:]


def script_risks() -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for path in [OPS_REPO / "ops" / "health-monitor.py", OPS_REPO / "scripts" / "health-monitor.py"]:
        text = plist_text(path)
        if not text:
            risks.append({"path": str(path), "status": "missing", "risk": "unknown"})
            continue
        has_down_code = "ENGINE DOWN" in text and "NTFY" in text.upper()
        inert = "Deprecated" in text and "no checks, reloads, or NTFY alerts" in text
        empty_engines = "ENGINES = {}" in text
        risks.append(
            {
                "path": str(path),
                "status": "present",
                "has_down_alert_code": has_down_code,
                "inert": inert,
                "empty_engines": empty_engines,
                "risk": "blocked" if inert or empty_engines else ("active_code" if has_down_code else "none"),
            }
        )
    return risks


def main() -> int:
    loaded = launchctl_labels()
    launch_risks = list_launch_agent_risks(loaded)
    loaded_risks = [row for row in launch_risks if row["loaded"]]
    scripts = script_risks()
    active_script_risks = [row for row in scripts if row.get("risk") == "active_code"]
    history = recent_engine_down_lines()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ok": not loaded_risks and not active_script_risks,
        "loaded_stale_alert_jobs": len(loaded_risks),
        "installed_stale_alert_plists": len(launch_risks),
        "active_script_risks": len(active_script_risks),
        "recent_engine_down_log_lines": len(history),
        "launch_agent_risks": launch_risks,
        "script_risks": scripts,
        "recent_engine_down_history": history,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
