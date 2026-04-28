#!/usr/bin/env python3
"""
LEGACY ENGINE AUDIT

Audits the old pre-CTOS engine family so it cannot silently rot in the
background. This is not the live operating spine. It is a quarantine report
that tells us:
  - which old engines still exist
  - which ones are blocked by legacy CRM assumptions
  - which ones still reference stale local paths
  - whether any related launchd labels are accidentally loaded
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.home() / "thecalltaker"
OPS_REPO = Path.home() / "thecalltaker-ops"
REPORT_PATH = (OPS_REPO / "ops" / "legacy-engine-report.json") if (OPS_REPO / "ops").is_dir() else (ROOT / "ops" / "legacy-engine-report.json")
LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"

ENGINES = [
    {
        "key": "cold-caller-v2",
        "label": "Cold caller v2",
        "path": ROOT / "ops" / "cold-caller-v2.py",
        "launchd_labels": [
            "com.thecalltaker.ops.coldcaller.check",
            "com.thecalltaker.coldcaller.call",
            "com.thecalltaker.coldcaller.check",
        ],
    },
    {
        "key": "hot-lead-converter",
        "label": "Hot lead converter",
        "path": ROOT / "ops" / "hot-lead-converter.py",
        "launchd_labels": [
            "com.thecalltaker.hotlead.sequence",
            "com.thecalltaker.hotlead.check",
        ],
    },
    {
        "key": "blast-engine-v2",
        "label": "Blast engine v2",
        "path": ROOT / "ops" / "blast-engine-v2.py",
        "launchd_labels": ["com.thecalltaker.ralph-loop"],
    },
    {
        "key": "outbound-sms-engine",
        "label": "Outbound SMS engine",
        "path": ROOT / "ops" / "outbound-sms-engine.py",
        "launchd_labels": ["com.thecalltaker.ben.sms"],
    },
    {
        "key": "blast-sms-followup",
        "label": "Blast SMS follow-up",
        "path": ROOT / "ops" / "blast-sms-followup.py",
        "launchd_labels": [],
    },
    {
        "key": "storm-chaser-v2",
        "label": "Storm chaser v2",
        "path": ROOT / "ops" / "storm-chaser-v2.py",
        "launchd_labels": ["com.thecalltaker.prism-storm"],
    },
    {
        "key": "storm-chaser-v3",
        "label": "Storm chaser v3",
        "path": ROOT / "ops" / "storm-chaser-v3.py",
        "launchd_labels": ["com.thecalltaker.atlas-storm"],
    },
    {
        "key": "dm-tracker",
        "label": "DM tracker",
        "path": ROOT / "ops" / "dm-tracker.py",
        "launchd_labels": ["com.thecalltaker.ops.dmtracker"],
    },
    {
        "key": "payment-reminder-engine",
        "label": "Payment reminder engine",
        "path": ROOT / "ops" / "payment-reminder-engine.py",
        "launchd_labels": ["com.thecalltaker.payment-monitor.v2"],
    },
]


def _launchctl_text() -> str:
    try:
        return subprocess.check_output(["launchctl", "list"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def _plist_exists(label: str) -> bool:
    return (LAUNCH_AGENTS / f"{label}.plist").exists()


def audit_engine(row: dict, launchctl_dump: str) -> dict:
    path = row["path"]
    exists = path.exists()
    body = path.read_text(encoding="utf-8", errors="ignore") if exists else ""

    legacy_crm_ref = any(
        token in body
        for token in (
            "TCT_LEGACY_CRM_LOCATION_ID",
            "crm-disabled.invalid",
            "legacy CRM",
        )
    )
    stale_desktop_path_ref = "/Desktop/thecalltaker/" in body

    launchd = []
    for label in row.get("launchd_labels", []):
        launchd.append(
            {
                "label": label,
                "plist_exists": _plist_exists(label),
                "loaded": label in launchctl_dump,
            }
        )

    loaded_labels = [item["label"] for item in launchd if item["loaded"]]
    orphan_plists = [item["label"] for item in launchd if item["plist_exists"] and not item["loaded"]]

    blockers = []
    if legacy_crm_ref:
        blockers.append("legacy-crm")
    if stale_desktop_path_ref:
        blockers.append("stale-path")

    return {
        "key": row["key"],
        "label": row["label"],
        "path": str(path),
        "file_exists": exists,
        "legacy_crm_ref": legacy_crm_ref,
        "stale_desktop_path_ref": stale_desktop_path_ref,
        "launchd": launchd,
        "loaded_labels": loaded_labels,
        "orphan_plists": orphan_plists,
        "blockers": blockers,
        "revive_ready": exists and not blockers,
    }


def main() -> int:
    now = datetime.now(timezone.utc)
    launchctl_dump = _launchctl_text()
    rows = [audit_engine(row, launchctl_dump) for row in ENGINES]

    report = {
        "timestamp": now.isoformat(),
        "engines_total": len(rows),
        "blocked_legacy_crm": sum(1 for row in rows if row["legacy_crm_ref"]),
        "blocked_stale_path": sum(1 for row in rows if row["stale_desktop_path_ref"]),
        "revive_ready_total": sum(1 for row in rows if row["revive_ready"]),
        "loaded_labels_total": sum(len(row["loaded_labels"]) for row in rows),
        "orphan_plists_total": sum(len(row["orphan_plists"]) for row in rows),
        "engines": rows,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
