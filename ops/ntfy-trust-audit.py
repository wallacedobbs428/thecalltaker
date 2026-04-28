#!/usr/bin/env python3
"""
NTFY TRUST AUDIT

Fails when public browser files can post directly to ntfy.sh. Phone alerts must
come from trusted server-side paths after a lead/action is saved.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.home() / "thecalltaker"
OPS_REPO = Path.home() / "thecalltaker-ops"
REPORT_PATH = (
    OPS_REPO / "ops" / "ntfy-trust-report.json"
    if (OPS_REPO / "ops").is_dir()
    else ROOT / "ops" / "ntfy-trust-report.json"
)

PUBLIC_SUFFIXES = {".html", ".js"}
SKIP_PARTS = {
    ".git",
    "node_modules",
    "docs",
}

DIRECT_NTFY_POST_RE = re.compile(
    r"fetch\s*\(\s*['\"]https://ntfy\.sh/|fetch\s*\(\s*`https://ntfy\.sh/",
    re.IGNORECASE,
)

SERVER_ALLOWED = {
    "netlify/functions/public-lead.js",
}


def should_scan(path: Path) -> bool:
    if path.suffix not in PUBLIC_SUFFIXES:
        return False
    rel = path.relative_to(ROOT)
    if any(part in SKIP_PARTS for part in rel.parts):
        return False
    if rel.as_posix() in SERVER_ALLOWED:
        return False
    return True


def main() -> int:
    violations = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in DIRECT_NTFY_POST_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            violations.append(
                {
                    "path": str(path),
                    "line": line,
                    "detail": "browser-side direct ntfy post",
                }
            )

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ok": not violations,
        "violations_total": len(violations),
        "violations": violations,
        "policy": "Public browser files must not post directly to ntfy.sh.",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())

