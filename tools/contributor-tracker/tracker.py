#!/usr/bin/env python3
"""
The Call Taker — Contributor Tracking System
Tracks all actions by Wallace and Mills for fair revenue splitting.

Usage:
    calltaker whoami              — Switch active user
    calltaker log "description"   — Log a manual task
    calltaker payday 5000         — Calculate revenue split
    calltaker score               — Show current scores
    calltaker history [n]         — Show last n actions (default 20)
    calltaker backfill            — Backfill from Git history
    calltaker export              — Export activity log as CSV
    calltaker dashboard           — Regenerate dashboard HTML
    calltaker status              — Show system status
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# --- Paths ---
# Resolve base directory relative to this script's location
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_DIR = os.path.dirname(os.path.dirname(_SCRIPT_DIR))  # tools/contributor-tracker -> repo root

# Data lives in ~/thecalltaker-ops/contributor-tracker/ on the Mac,
# falls back to tools/contributor-tracker/data/ for portability
_ops_candidates = [
    os.path.expanduser("~/thecalltaker-ops"),
    "/home/user/thecalltaker-ops",
]
OPS_DIR = os.environ.get("TCT_OPS_DIR", "")
if not OPS_DIR:
    for candidate in _ops_candidates:
        if os.path.isdir(candidate):
            OPS_DIR = candidate
            break
if not OPS_DIR:
    OPS_DIR = os.path.join(_SCRIPT_DIR, "data")  # fallback: store in repo

TRACKER_DIR = os.path.join(OPS_DIR, "contributor-tracker") if "contributor-tracker" not in OPS_DIR else OPS_DIR
ACTIVE_USER_FILE = os.path.join(TRACKER_DIR, "active-user.json")
ACTIVITY_LOG = os.path.join(TRACKER_DIR, "activity-log.json")
SCORES_FILE = os.path.join(TRACKER_DIR, "scores.json")
LEDGER_FILE = os.path.join(TRACKER_DIR, "ledger.json")
DASHBOARD_FILE = os.path.join(TRACKER_DIR, "contributor-dashboard.html")

# --- GitHub username mapping ---
GITHUB_USERS = {
    "wallacedobbs428": "wallace",
    "wallace dobbs": "wallace",
    "wallacemdobbs": "wallace",
    "msnfjsfsfgskgvfyvsyfv": "mills",
    "claude": "wallace",  # Claude sessions default to whoever invoked them
    "noreply@anthropic.com": "wallace",
}

# --- Point weights ---
POINT_WEIGHTS = {
    "commit": 10,
    "new_feature": 25,
    "lead_generated": 2,
    "email_blast": 5,
    "sms_blast": 5,
    "workflow_built": 15,
    "manual_task": 5,
    "file_created": 3,
    "file_modified": 2,
    "service_started": 3,
    "service_stopped": 2,
    "ghl_change": 5,
    "agent_session": 5,
    "n8n_workflow": 15,
    "bug_fix": 8,
    "deployment": 10,
}

WEIGHT_LABELS = {
    "commit": "Code commit",
    "new_feature": "New feature shipped",
    "lead_generated": "Lead generated",
    "email_blast": "Email blast sent",
    "sms_blast": "SMS blast sent",
    "workflow_built": "Workflow built",
    "manual_task": "Manual task",
    "file_created": "File created",
    "file_modified": "File modified",
    "service_started": "Service started",
    "service_stopped": "Service stopped",
    "ghl_change": "GHL change",
    "agent_session": "Agent session",
    "n8n_workflow": "n8n workflow",
    "bug_fix": "Bug fix",
    "deployment": "Deployment",
}


def ensure_dirs():
    os.makedirs(TRACKER_DIR, exist_ok=True)


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    import tempfile
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def get_active_user():
    data = load_json(ACTIVE_USER_FILE)
    return data.get("user")


def set_active_user(user):
    save_json(ACTIVE_USER_FILE, {
        "user": user,
        "set_at": datetime.now().isoformat(),
    })
    print(f"Active user set to: {user}")


def prompt_user():
    print("\nWho is working right now?")
    print("  (1) Wallace")
    print("  (2) Mills")
    choice = input("\nEnter 1 or 2: ").strip()
    if choice == "1":
        set_active_user("wallace")
        return "wallace"
    elif choice == "2":
        set_active_user("mills")
        return "mills"
    else:
        print("Invalid choice. Defaulting to wallace.")
        set_active_user("wallace")
        return "wallace"


def ensure_user():
    user = get_active_user()
    if not user:
        user = prompt_user()
    return user


def load_activities():
    return load_json(ACTIVITY_LOG, [])


def save_activities(activities):
    save_json(ACTIVITY_LOG, activities)


def log_activity(user, action_type, description, points=None, metadata=None):
    if points is None:
        points = POINT_WEIGHTS.get(action_type, 5)
    activities = load_activities()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "type": action_type,
        "description": description,
        "points": points,
    }
    if metadata:
        entry["metadata"] = metadata
    activities.append(entry)
    save_activities(activities)
    return entry


def calculate_scores():
    activities = load_activities()
    scores = {"wallace": 0, "mills": 0}
    counts = {"wallace": {}, "mills": {}}

    for entry in activities:
        user = entry.get("user", "unknown")
        if user not in scores:
            continue
        pts = entry.get("points", 0)
        scores[user] += pts
        atype = entry.get("type", "other")
        counts[user][atype] = counts[user].get(atype, 0) + 1

    total = scores["wallace"] + scores["mills"]
    pct = {
        "wallace": round(scores["wallace"] / total * 100, 1) if total > 0 else 50.0,
        "mills": round(scores["mills"] / total * 100, 1) if total > 0 else 50.0,
    }

    result = {
        "scores": scores,
        "percentages": pct,
        "counts": counts,
        "total_points": total,
        "last_updated": datetime.now().isoformat(),
    }
    save_json(SCORES_FILE, result)
    return result


def get_weekly_breakdown():
    activities = load_activities()
    now = datetime.now()
    weeks = {}

    for entry in activities:
        ts = datetime.fromisoformat(entry["timestamp"])
        week_start = (ts - timedelta(days=ts.weekday())).strftime("%Y-%m-%d")
        if week_start not in weeks:
            weeks[week_start] = {"wallace": 0, "mills": 0, "wallace_items": [], "mills_items": []}
        user = entry.get("user", "unknown")
        if user in ("wallace", "mills"):
            weeks[week_start][user] += entry.get("points", 0)
            weeks[week_start][f"{user}_items"].append({
                "type": entry.get("type"),
                "description": entry.get("description", ""),
                "points": entry.get("points", 0),
            })

    return dict(sorted(weeks.items(), reverse=True))


def backfill_git():
    """Backfill from Git history in both repos."""
    repos = [_REPO_DIR]
    ops_dir_repo = OPS_DIR
    if os.path.isdir(os.path.join(ops_dir_repo, ".git")):
        repos.append(ops_dir_repo)
    existing = load_activities()
    existing_hashes = {e.get("metadata", {}).get("commit_hash") for e in existing if e.get("metadata")}
    new_count = 0

    for repo in repos:
        if not os.path.isdir(repo):
            continue
        try:
            result = subprocess.run(
                ["git", "-C", repo, "log", "--format=%H|%an|%ae|%aI|%s", "--all"],
                capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 4)
                if len(parts) < 5:
                    continue
                commit_hash, author_name, author_email, date, message = parts

                if commit_hash in existing_hashes:
                    continue

                # Detect user from GitHub username or email
                user = None
                for gh_user, mapped in GITHUB_USERS.items():
                    if gh_user.lower() in author_name.lower() or gh_user.lower() in author_email.lower():
                        user = mapped
                        break

                if not user:
                    # Try common patterns
                    name_lower = author_name.lower()
                    email_lower = author_email.lower()
                    if "wallace" in name_lower or "wallacedobbs" in email_lower:
                        user = "wallace"
                    elif "mills" in name_lower or "msnfj" in email_lower:
                        user = "mills"
                    else:
                        user = "wallace"  # Default for older commits

                # Determine if it's a feature or regular commit
                action_type = "commit"
                points = POINT_WEIGHTS["commit"]
                msg_lower = message.lower()
                if any(kw in msg_lower for kw in ["add ", "new ", "create ", "build ", "implement"]):
                    action_type = "new_feature"
                    points = POINT_WEIGHTS["new_feature"]
                elif any(kw in msg_lower for kw in ["fix ", "bug ", "patch ", "hotfix"]):
                    action_type = "bug_fix"
                    points = POINT_WEIGHTS["bug_fix"]

                repo_name = os.path.basename(repo)
                entry = {
                    "timestamp": date,
                    "user": user,
                    "type": action_type,
                    "description": f"[{repo_name}] {message}",
                    "points": points,
                    "metadata": {"commit_hash": commit_hash, "repo": repo_name},
                }
                existing.append(entry)
                existing_hashes.add(commit_hash)
                new_count += 1

        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    # Sort by timestamp
    existing.sort(key=lambda x: x.get("timestamp", ""))
    save_activities(existing)
    return new_count


def cmd_whoami():
    print("\nSwitch active user:")
    prompt_user()


def cmd_log(description):
    user = ensure_user()
    entry = log_activity(user, "manual_task", description)
    print(f"Logged: [{user}] {description} (+{entry['points']} pts)")


def cmd_score():
    result = calculate_scores()
    s = result["scores"]
    p = result["percentages"]

    print("\n" + "=" * 50)
    print("  CONTRIBUTOR SCORES")
    print("=" * 50)
    print(f"\n  Wallace:  {s['wallace']:>6} pts  ({p['wallace']}%)")
    print(f"  Mills:    {s['mills']:>6} pts  ({p['mills']}%)")
    print(f"\n  Total:    {result['total_points']:>6} pts")
    print()

    # Show breakdown by type
    for user in ("wallace", "mills"):
        counts = result["counts"].get(user, {})
        if counts:
            print(f"  {user.title()}'s breakdown:")
            for atype, count in sorted(counts.items(), key=lambda x: -x[1]):
                label = WEIGHT_LABELS.get(atype, atype)
                pts = count * POINT_WEIGHTS.get(atype, 5)
                print(f"    {label}: {count}x = {pts} pts")
            print()


def cmd_payday(amount):
    try:
        amount = float(amount)
    except ValueError:
        print("Error: amount must be a number")
        return

    result = calculate_scores()
    p = result["percentages"]

    wallace_cut = round(amount * p["wallace"] / 100, 2)
    mills_cut = round(amount * p["mills"] / 100, 2)

    print("\n" + "=" * 50)
    print("  PAYDAY CALCULATOR")
    print("=" * 50)
    print(f"\n  Total Revenue:  ${amount:,.2f}")
    print(f"\n  Wallace gets:   ${wallace_cut:,.2f}  ({p['wallace']}%)")
    print(f"  Mills gets:     ${mills_cut:,.2f}  ({p['mills']}%)")
    print()

    # Log to ledger
    ledger = load_json(LEDGER_FILE, [])
    ledger.append({
        "date": datetime.now().isoformat(),
        "total": amount,
        "wallace_amount": wallace_cut,
        "wallace_pct": p["wallace"],
        "mills_amount": mills_cut,
        "mills_pct": p["mills"],
        "total_points_at_time": result["total_points"],
    })
    save_json(LEDGER_FILE, ledger)
    print("  Logged to ledger.json")


def cmd_history(n=20):
    activities = load_activities()
    recent = activities[-n:]
    recent.reverse()

    print(f"\n  Last {min(n, len(recent))} activities:")
    print("  " + "-" * 70)

    for entry in recent:
        ts = entry.get("timestamp", "")[:16].replace("T", " ")
        user = entry.get("user", "?")[:7].ljust(7)
        atype = entry.get("type", "?")[:15].ljust(15)
        desc = entry.get("description", "")[:40]
        pts = entry.get("points", 0)
        print(f"  {ts}  {user}  {atype}  {desc}  +{pts}")

    print()


def cmd_backfill():
    print("Backfilling from Git history...")
    count = backfill_git()
    print(f"Added {count} new entries from Git history.")
    calculate_scores()
    cmd_score()


def cmd_export():
    activities = load_activities()
    csv_path = os.path.join(TRACKER_DIR, "activity-export.csv")
    with open(csv_path, "w") as f:
        f.write("timestamp,user,type,description,points\n")
        for entry in activities:
            desc = entry.get("description", "").replace('"', '""')
            f.write(f'{entry.get("timestamp","")},{entry.get("user","")},{entry.get("type","")},"{desc}",{entry.get("points",0)}\n')
    print(f"Exported {len(activities)} entries to {csv_path}")


def cmd_status():
    user = get_active_user()
    activities = load_activities()
    result = calculate_scores()
    ledger = load_json(LEDGER_FILE, [])

    print("\n" + "=" * 50)
    print("  CONTRIBUTOR TRACKER STATUS")
    print("=" * 50)
    print(f"\n  Active user:     {user or 'not set'}")
    print(f"  Total entries:   {len(activities)}")
    print(f"  Total points:    {result.get('total_points', 0)}")
    print(f"  Paydays logged:  {len(ledger)}")
    print(f"  Wallace:         {result.get('percentages', {}).get('wallace', 0)}%")
    print(f"  Mills:           {result.get('percentages', {}).get('mills', 0)}%")

    if activities:
        last = activities[-1]
        print(f"\n  Last activity:   {last.get('timestamp', '')[:16]}")
        print(f"                   [{last.get('user')}] {last.get('description', '')[:50]}")
    print()


def generate_dashboard():
    """Generate the contributor dashboard HTML."""
    result = calculate_scores()
    activities = load_activities()
    weekly = get_weekly_breakdown()
    ledger = load_json(LEDGER_FILE, [])

    s = result["scores"]
    p = result["percentages"]

    # Build activity rows
    recent = activities[-50:]
    recent.reverse()
    activity_rows = ""
    for entry in recent:
        ts = entry.get("timestamp", "")[:16].replace("T", " ")
        user = entry.get("user", "unknown")
        user_class = "wallace" if user == "wallace" else "mills"
        atype = WEIGHT_LABELS.get(entry.get("type", ""), entry.get("type", ""))
        desc = entry.get("description", "")
        pts = entry.get("points", 0)
        activity_rows += f"""
        <tr>
          <td class="ts">{ts}</td>
          <td><span class="badge {user_class}">{user.title()}</span></td>
          <td>{atype}</td>
          <td class="desc">{desc}</td>
          <td class="pts">+{pts}</td>
        </tr>"""

    # Build weekly rows
    weekly_rows = ""
    for week, data in list(weekly.items())[:8]:
        w_pts = data.get("wallace", 0)
        m_pts = data.get("mills", 0)
        total = w_pts + m_pts
        w_pct = round(w_pts / total * 100) if total > 0 else 50
        m_pct = 100 - w_pct
        weekly_rows += f"""
        <tr>
          <td>{week}</td>
          <td>{w_pts}</td>
          <td>{m_pts}</td>
          <td>
            <div class="bar-container">
              <div class="bar wallace-bar" style="width:{w_pct}%">{w_pct}%</div>
              <div class="bar mills-bar" style="width:{m_pct}%">{m_pct}%</div>
            </div>
          </td>
        </tr>"""

    # Build ledger rows
    ledger_rows = ""
    for entry in reversed(ledger[-10:]):
        d = entry.get("date", "")[:10]
        total = entry.get("total", 0)
        wa = entry.get("wallace_amount", 0)
        wp = entry.get("wallace_pct", 0)
        ma = entry.get("mills_amount", 0)
        mp = entry.get("mills_pct", 0)
        ledger_rows += f"""
        <tr>
          <td>{d}</td>
          <td>${total:,.2f}</td>
          <td>${wa:,.2f} ({wp}%)</td>
          <td>${ma:,.2f} ({mp}%)</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Call Taker — Contributor Dashboard</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0a0a0f; color:#e0e0e0; font-family:'SF Mono',Monaco,monospace; padding:24px; }}
  h1 {{ text-align:center; color:#f97316; font-size:22px; margin-bottom:4px; }}
  .subtitle {{ text-align:center; color:#666; font-size:12px; margin-bottom:32px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; max-width:1100px; margin:0 auto 32px; }}
  .card {{ background:#111118; border:1px solid #1a1a2e; border-radius:12px; padding:24px; }}
  .card h2 {{ color:#888; font-size:13px; text-transform:uppercase; letter-spacing:.1em; margin-bottom:16px; }}
  .big-num {{ font-size:42px; font-weight:800; }}
  .wallace-color {{ color:#f97316; }}
  .mills-color {{ color:#3b82f6; }}
  .pct {{ font-size:18px; color:#666; margin-left:8px; }}

  /* Donut chart */
  .donut-wrap {{ display:flex; align-items:center; justify-content:center; gap:32px; }}
  .donut {{ width:180px; height:180px; border-radius:50%; position:relative;
    background: conic-gradient(#f97316 0% {p['wallace']}%, #3b82f6 {p['wallace']}% 100%);
  }}
  .donut-hole {{ position:absolute; top:30px; left:30px; width:120px; height:120px;
    border-radius:50%; background:#111118; display:flex; flex-direction:column;
    align-items:center; justify-content:center; }}
  .donut-hole .split {{ font-size:20px; font-weight:800; color:#fff; }}
  .donut-hole .label {{ font-size:10px; color:#666; margin-top:2px; }}
  .legend {{ display:flex; flex-direction:column; gap:12px; }}
  .legend-item {{ display:flex; align-items:center; gap:8px; }}
  .legend-dot {{ width:12px; height:12px; border-radius:3px; }}

  /* Suggested split */
  .split-box {{ background:#0f1a0f; border:1px solid #1a3a1a; border-radius:8px; padding:16px; margin-top:16px; text-align:center; }}
  .split-box .title {{ color:#22c55e; font-size:11px; text-transform:uppercase; letter-spacing:.1em; }}
  .split-box .amounts {{ font-size:16px; margin-top:8px; }}

  /* Tables */
  table {{ width:100%; border-collapse:collapse; font-size:12px; }}
  th {{ text-align:left; color:#666; font-size:11px; text-transform:uppercase; letter-spacing:.05em; padding:8px 12px; border-bottom:1px solid #1a1a2e; }}
  td {{ padding:8px 12px; border-bottom:1px solid #0f0f1a; }}
  .ts {{ color:#555; white-space:nowrap; }}
  .desc {{ max-width:250px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .pts {{ color:#22c55e; font-weight:700; text-align:right; }}
  .badge {{ padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; }}
  .badge.wallace {{ background:#f9731622; color:#f97316; }}
  .badge.mills {{ background:#3b82f622; color:#3b82f6; }}

  /* Weekly bars */
  .bar-container {{ display:flex; height:20px; border-radius:4px; overflow:hidden; }}
  .bar {{ display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; color:#fff; min-width:30px; }}
  .wallace-bar {{ background:#f97316; }}
  .mills-bar {{ background:#3b82f6; }}

  .full-width {{ grid-column: 1 / -1; }}
  .scroll-table {{ max-height:400px; overflow-y:auto; }}

  @media (max-width:768px) {{
    .grid {{ grid-template-columns:1fr; }}
    .donut-wrap {{ flex-direction:column; }}
  }}
</style>
</head>
<body>

<h1>Contributor Dashboard</h1>
<p class="subtitle">The Call Taker — Wallace x Mills | Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<div class="grid">

  <!-- Donut Chart -->
  <div class="card">
    <h2>Ownership Split</h2>
    <div class="donut-wrap">
      <div class="donut">
        <div class="donut-hole">
          <div class="split">{p['wallace']}%</div>
          <div class="label">vs {p['mills']}%</div>
        </div>
      </div>
      <div class="legend">
        <div class="legend-item">
          <div class="legend-dot" style="background:#f97316"></div>
          <span class="wallace-color">Wallace — {s['wallace']} pts</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot" style="background:#3b82f6"></div>
          <span class="mills-color">Mills — {s['mills']} pts</span>
        </div>
      </div>
    </div>
    <div class="split-box">
      <div class="title">Suggested Revenue Split</div>
      <div class="amounts">
        <span class="wallace-color">{p['wallace']}% Wallace</span> &nbsp;/&nbsp;
        <span class="mills-color">{p['mills']}% Mills</span>
      </div>
    </div>
  </div>

  <!-- Score Cards -->
  <div class="card">
    <h2>Total Points</h2>
    <div style="margin-bottom:24px">
      <div class="big-num wallace-color">{s['wallace']}</div>
      <div style="color:#666;font-size:12px">Wallace's points</div>
    </div>
    <div>
      <div class="big-num mills-color">{s['mills']}</div>
      <div style="color:#666;font-size:12px">Mills' points</div>
    </div>
    <div style="margin-top:16px;padding-top:16px;border-top:1px solid #1a1a2e">
      <div style="color:#666;font-size:12px">Total: <span style="color:#fff;font-weight:700">{result['total_points']}</span> points across <span style="color:#fff;font-weight:700">{len(activities)}</span> activities</div>
    </div>
  </div>

  <!-- Weekly Breakdown -->
  <div class="card full-width">
    <h2>Weekly Breakdown</h2>
    <table>
      <tr><th>Week</th><th>Wallace</th><th>Mills</th><th>Split</th></tr>
      {weekly_rows}
    </table>
  </div>

  <!-- Payout Ledger -->
  <div class="card full-width">
    <h2>Payout Ledger</h2>
    {"<table><tr><th>Date</th><th>Total</th><th>Wallace</th><th>Mills</th></tr>" + ledger_rows + "</table>" if ledger_rows else '<p style="color:#555">No payouts recorded yet. Use: calltaker payday [AMOUNT]</p>'}
  </div>

  <!-- Activity Log -->
  <div class="card full-width">
    <h2>Recent Activity (Last 50)</h2>
    <div class="scroll-table">
      <table>
        <tr><th>Time</th><th>User</th><th>Type</th><th>Description</th><th>Pts</th></tr>
        {activity_rows}
      </table>
    </div>
  </div>

</div>

<script>
  // Auto-refresh every 5 minutes
  setTimeout(() => location.reload(), 300000);
</script>
</body>
</html>"""

    with open(DASHBOARD_FILE, "w") as f:
        f.write(html)
    print(f"Dashboard generated: {DASHBOARD_FILE}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "whoami":
        cmd_whoami()
    elif cmd == "log":
        if len(sys.argv) < 3:
            print("Usage: calltaker log \"description\"")
            return
        desc = " ".join(sys.argv[2:])
        cmd_log(desc)
    elif cmd == "payday":
        if len(sys.argv) < 3:
            print("Usage: calltaker payday [AMOUNT]")
            return
        cmd_payday(sys.argv[2])
    elif cmd == "score":
        cmd_score()
    elif cmd == "history":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        cmd_history(n)
    elif cmd == "backfill":
        cmd_backfill()
    elif cmd == "export":
        cmd_export()
    elif cmd == "dashboard":
        generate_dashboard()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
