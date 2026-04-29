#!/usr/bin/env python3
"""
Audit direct NTFY send paths across local repos and launchd.

The browser trust audit catches public-page posts. This audit catches the
other failure class: local scripts or launchd jobs that can push phone alerts
without going through CTOS/trusted alert evidence first.
"""

from __future__ import annotations

import json
import plistlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOME = Path.home()
ROOTS = [
    HOME / "thecalltaker",
    HOME / "thecalltaker-ops",
    HOME / "wallace-revenue-machine",
]
LAUNCH_AGENTS = HOME / "Library" / "LaunchAgents"
OPS_REPO = HOME / "thecalltaker-ops"
REPORT_PATH = OPS_REPO / "ops" / "ntfy-direct-send-report.json"

SKIP_PARTS = {
    ".git",
    ".next",
    "node_modules",
    "dist",
    "build",
    "logs",
    "shared/chroma_db",
}
SKIP_SUFFIXES = {
    ".json",
    ".jsonl",
    ".csv",
    ".log",
    ".sqlite",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
}
SCAN_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".sh",
    ".html",
    ".plist",
    ".txt",
}

DIRECT_PATTERNS = [
    re.compile(r"https://ntfy\.sh(?:/|['\"])", re.IGNORECASE),
    re.compile(r"hostname\s*:\s*['\"]ntfy\.sh['\"]", re.IGNORECASE),
    re.compile(r"curl\b.*ntfy\.sh", re.IGNORECASE),
]

TRUSTED_MARKERS = (
    "post_trusted_ntfy",
    "recordTrustedAlert",
    "ntfy_standard(",
    "trusted_alert_rule",
)

CENTRAL_ALLOWED_FILES = {
    str(OPS_REPO / "ops" / "trusted_ntfy.py"),
    str(OPS_REPO / "ops" / "tct_common.py"),
}


def is_skipped(path: Path) -> bool:
    rel_parts = set(path.parts)
    if rel_parts & SKIP_PARTS:
        return True
    if any(skip in path.as_posix() for skip in ("/shared/chroma_db/", "/node_modules/", "/.next/")):
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    if path.suffix.lower() and path.suffix.lower() not in SCAN_SUFFIXES:
        return True
    return False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def find_direct_lines(text: str) -> list[int]:
    lines: list[int] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in DIRECT_PATTERNS):
            lines.append(idx)
    return lines


def trusted_source(path: Path, text: str) -> bool:
    if str(path) in CENTRAL_ALLOWED_FILES:
        return True
    return any(marker in text for marker in TRUSTED_MARKERS)


def launchctl_labels() -> set[str]:
    try:
        proc = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=12)
    except Exception:
        proc = None
    labels: set[str] = set()
    if proc and proc.returncode == 0 and proc.stdout.strip():
        for line in proc.stdout.splitlines():
            parts = line.split()
            if parts:
                labels.add(parts[-1])
    if labels:
        return labels

    # Python children can get an empty/rc=1 launchctl list in some Codex
    # sessions. The GUI bootstrap print stays readable and has the same labels.
    try:
        proc = subprocess.run(
            ["launchctl", "print", f"gui/{HOME.stat().st_uid}"],
            capture_output=True,
            text=True,
            timeout=12,
        )
    except Exception:
        return labels
    for line in proc.stdout.splitlines():
        if "com.thecalltaker." not in line:
            continue
        parts = line.split()
        if parts:
            labels.add(parts[-1])
    return labels


def plist_payload(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            payload = plistlib.load(handle)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def plist_program_path(args: Any) -> str | None:
    if not isinstance(args, list):
        return None
    for item in args[1:]:
        value = str(item)
        if value.startswith(str(HOME)) and Path(value).suffix in SCAN_SUFFIXES:
            return value
    return None


def scan_sources() -> dict[str, dict[str, Any]]:
    findings: dict[str, dict[str, Any]] = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or is_skipped(path):
                continue
            text = read_text(path)
            if not text:
                continue
            lines = find_direct_lines(text)
            if not lines:
                continue
            findings[str(path)] = {
                "path": str(path),
                "relative_path": path.relative_to(HOME).as_posix() if path.is_relative_to(HOME) else str(path),
                "direct_lines": lines[:50],
                "direct_line_count": len(lines),
                "trusted_path": trusted_source(path, text),
            }
    return findings


def scan_launch_agents(source_findings: dict[str, dict[str, Any]], loaded: set[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not LAUNCH_AGENTS.is_dir():
        return findings
    for path in sorted(LAUNCH_AGENTS.glob("**/com.thecalltaker*.plist")):
        payload = plist_payload(path)
        label = str(payload.get("Label") or path.stem)
        args = payload.get("ProgramArguments") or []
        args_text = " ".join(str(arg) for arg in args) if isinstance(args, list) else str(args)
        text = f"{args_text}\n{read_text(path)}"
        direct_lines = find_direct_lines(text)
        program = plist_program_path(args)
        program_finding = source_findings.get(program or "")
        loaded_now = label in loaded

        direct_plist = bool(direct_lines)
        direct_program = bool(program_finding and not program_finding.get("trusted_path"))
        trusted_program = bool(program_finding and program_finding.get("trusted_path"))
        if not (direct_plist or direct_program or trusted_program):
            continue

        severity = "info"
        blocking = False
        if loaded_now and (direct_plist or direct_program):
            severity = "active_direct_sender"
            blocking = True
        elif direct_plist or direct_program:
            severity = "installed_direct_sender"
        elif trusted_program:
            severity = "trusted_sender"

        findings.append(
            {
                "label": label,
                "path": str(path),
                "loaded": loaded_now,
                "severity": severity,
                "blocking": blocking,
                "direct_plist_lines": direct_lines[:25],
                "program": program,
                "program_direct": direct_program,
                "program_trusted": trusted_program,
            }
        )
    return findings


def main() -> int:
    source_findings = scan_sources()
    loaded = launchctl_labels()
    launch_findings = scan_launch_agents(source_findings, loaded)
    active_blocking = [row for row in launch_findings if row.get("blocking")]

    untrusted_sources = [
        row for row in source_findings.values() if not row.get("trusted_path")
    ]
    trusted_sources = [
        row for row in source_findings.values() if row.get("trusted_path")
    ]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ok": not active_blocking,
        "policy": "Loaded launchd jobs must not post directly to ntfy.sh unless they go through CTOS/trusted alert evidence.",
        "active_blocking_total": len(active_blocking),
        "launch_agent_findings_total": len(launch_findings),
        "source_direct_files_total": len(source_findings),
        "source_untrusted_direct_files_total": len(untrusted_sources),
        "source_trusted_direct_files_total": len(trusted_sources),
        "active_blocking": active_blocking,
        "launch_agent_findings": launch_findings,
        "top_untrusted_sources": sorted(
            untrusted_sources,
            key=lambda row: (row.get("direct_line_count", 0), row.get("relative_path", "")),
            reverse=True,
        )[:100],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "timestamp": report["timestamp"],
                "ok": report["ok"],
                "active_blocking_total": report["active_blocking_total"],
                "launch_agent_findings_total": report["launch_agent_findings_total"],
                "source_untrusted_direct_files_total": report["source_untrusted_direct_files_total"],
                "source_trusted_direct_files_total": report["source_trusted_direct_files_total"],
                "report_path": str(REPORT_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
