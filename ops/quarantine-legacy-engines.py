#!/usr/bin/env python3
"""
QUARANTINE LEGACY ENGINES

Unloads the old legacy-engine launchd jobs that are still hanging around even
though the engines themselves are blocked by legacy CRM assumptions.

This is intentionally narrow. It only touches the known dead engine family that
is audited by legacy-engine-audit.py.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


HOME = Path.home()
LAUNCH_AGENTS = HOME / "Library" / "LaunchAgents"

LABELS = [
    "com.thecalltaker.ops.coldcaller.check",
    "com.thecalltaker.hotlead.sequence",
    "com.thecalltaker.hotlead.check",
    "com.thecalltaker.ralph-loop",
    "com.thecalltaker.ben.sms",
    "com.thecalltaker.prism-storm",
    "com.thecalltaker.atlas-storm",
    "com.thecalltaker.ops.dmtracker",
    "com.thecalltaker.payment-monitor.v2",
]


def run(label: str) -> dict:
    plist = LAUNCH_AGENTS / f"{label}.plist"
    attempts = [
        ["launchctl", "bootout", f"gui/{os_getuid()}/{label}"],
        ["launchctl", "unload", str(plist)],
    ]
    last_error = ""
    for cmd in attempts:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except Exception as exc:
            last_error = str(exc)
            continue
        if proc.returncode == 0:
            return {"label": label, "ok": True, "command": cmd, "detail": "unloaded"}
        last_error = (proc.stderr or proc.stdout or "").strip()[:300]
    return {
        "label": label,
        "ok": False,
        "plist_exists": plist.exists(),
        "detail": last_error or "unable to unload",
    }


def os_getuid() -> int:
    import os

    return os.getuid()


def main() -> int:
    rows = [run(label) for label in LABELS]
    print(json.dumps({"rows": rows}, indent=2))
    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
