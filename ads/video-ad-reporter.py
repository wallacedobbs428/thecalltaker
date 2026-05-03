#!/usr/bin/env python3
"""
The Call Taker — Video Ad Performance Reporter
Daily 9am report: video vs image ad performance, hook analysis, cost metrics.

Usage:
    python3 video-ad-reporter.py report   — Generate daily performance report
    python3 video-ad-reporter.py status   — Show current state
    python3 video-ad-reporter.py compare  — Video vs image ad comparison

Designed to integrate with Meta Ads API when connected.
Until then, operates on manually-entered data in state file.

State: ~/thecalltaker/ads/video-ad-state.json
Output: ntfy SALES topic + JSON report
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
ADS_DIR = Path.home() / "thecalltaker" / "ads"
STATE_FILE = ADS_DIR / "video-ad-state.json"
REPORTS_DIR = ADS_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ntfy config (matches tct_common.py topics)
NTFY_SALES = "tct-sales-63uYsIT9"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "video_ads": [],
        "image_ads": [],
        "daily_reports": [],
        "last_report": None,
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def add_sample_data(state):
    """Add sample structure for manual data entry."""
    if not state["video_ads"]:
        state["video_ads"] = [
            {
                "id": "video_001",
                "script": 1,
                "name": "The Missed Call — Roofing",
                "vertical": "roofing",
                "format": "reels",
                "status": "pending_creative",
                "created": datetime.now().isoformat(),
                "metrics": {
                    "impressions": 0,
                    "reach": 0,
                    "three_second_views": 0,
                    "thruplay": 0,
                    "clicks": 0,
                    "leads": 0,
                    "spend": 0.0,
                    "thumb_stop_rate": 0.0,
                    "cpl": 0.0,
                    "ctr": 0.0,
                    "cost_per_thruplay": 0.0,
                },
            },
            {
                "id": "video_002",
                "script": 2,
                "name": "Side by Side — HVAC",
                "vertical": "hvac",
                "format": "reels",
                "status": "pending_creative",
                "created": datetime.now().isoformat(),
                "metrics": {
                    "impressions": 0,
                    "reach": 0,
                    "three_second_views": 0,
                    "thruplay": 0,
                    "clicks": 0,
                    "leads": 0,
                    "spend": 0.0,
                    "thumb_stop_rate": 0.0,
                    "cpl": 0.0,
                    "ctr": 0.0,
                    "cost_per_thruplay": 0.0,
                },
            },
        ]
    return state


def calculate_metrics(ad):
    """Calculate derived metrics from raw numbers."""
    m = ad["metrics"]
    if m["impressions"] > 0:
        m["thumb_stop_rate"] = round(
            (m["three_second_views"] / m["impressions"]) * 100, 2
        )
        m["ctr"] = round((m["clicks"] / m["impressions"]) * 100, 2)
    if m["leads"] > 0:
        m["cpl"] = round(m["spend"] / m["leads"], 2)
    if m["thruplay"] > 0:
        m["cost_per_thruplay"] = round(m["spend"] / m["thruplay"], 2)
    return ad


def generate_report(state):
    """Generate daily performance report."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Calculate metrics for all ads
    video_ads = [calculate_metrics(ad) for ad in state["video_ads"]]
    image_ads = [calculate_metrics(ad) for ad in state["image_ads"]]

    # Aggregate video metrics
    video_total = {
        "impressions": sum(a["metrics"]["impressions"] for a in video_ads),
        "leads": sum(a["metrics"]["leads"] for a in video_ads),
        "spend": sum(a["metrics"]["spend"] for a in video_ads),
        "thruplay": sum(a["metrics"]["thruplay"] for a in video_ads),
    }

    # Aggregate image metrics
    image_total = {
        "impressions": sum(a["metrics"]["impressions"] for a in image_ads),
        "leads": sum(a["metrics"]["leads"] for a in image_ads),
        "spend": sum(a["metrics"]["spend"] for a in image_ads),
    }

    # Best performing hook (highest thumb-stop rate)
    best_hook = None
    if video_ads:
        active = [a for a in video_ads if a["metrics"]["impressions"] > 0]
        if active:
            best_hook = max(active, key=lambda a: a["metrics"]["thumb_stop_rate"])

    # Best CPL
    best_cpl = None
    all_ads = video_ads + image_ads
    leads_ads = [a for a in all_ads if a["metrics"]["leads"] > 0]
    if leads_ads:
        best_cpl = min(leads_ads, key=lambda a: a["metrics"]["cpl"])

    report = {
        "date": today,
        "video_ads_count": len(video_ads),
        "image_ads_count": len(image_ads),
        "video_totals": video_total,
        "image_totals": image_total,
        "video_avg_cpl": (
            round(video_total["spend"] / video_total["leads"], 2)
            if video_total["leads"] > 0
            else None
        ),
        "image_avg_cpl": (
            round(image_total["spend"] / image_total["leads"], 2)
            if image_total["leads"] > 0
            else None
        ),
        "best_hook": (
            {
                "name": best_hook["name"],
                "thumb_stop_rate": best_hook["metrics"]["thumb_stop_rate"],
            }
            if best_hook
            else None
        ),
        "best_cpl_ad": (
            {"name": best_cpl["name"], "cpl": best_cpl["metrics"]["cpl"]}
            if best_cpl
            else None
        ),
        "by_vertical": {},
    }

    # Group by vertical
    for ad in video_ads:
        v = ad["vertical"]
        if v not in report["by_vertical"]:
            report["by_vertical"][v] = {
                "impressions": 0,
                "leads": 0,
                "spend": 0,
            }
        report["by_vertical"][v]["impressions"] += ad["metrics"]["impressions"]
        report["by_vertical"][v]["leads"] += ad["metrics"]["leads"]
        report["by_vertical"][v]["spend"] += ad["metrics"]["spend"]

    # Save report
    report_file = REPORTS_DIR / f"video-report-{today}.json"
    report_file.write_text(json.dumps(report, indent=2))

    state["daily_reports"].append(today)
    state["last_report"] = today
    save_state(state)

    return report


def format_report_ntfy(report):
    """Format report for ntfy notification."""
    lines = [f"VIDEO AD REPORT — {report['date']}", ""]

    if report["video_totals"]["impressions"] > 0:
        vt = report["video_totals"]
        lines.append(f"VIDEO: {vt['impressions']:,} imp → {vt['leads']} leads")
        if report["video_avg_cpl"]:
            lines.append(f"  CPL: ${report['video_avg_cpl']}")
    else:
        lines.append("VIDEO: No data yet (pending creative)")

    if report["image_totals"]["impressions"] > 0:
        it = report["image_totals"]
        lines.append(f"IMAGE: {it['impressions']:,} imp → {it['leads']} leads")
        if report["image_avg_cpl"]:
            lines.append(f"  CPL: ${report['image_avg_cpl']}")

    if report["best_hook"]:
        lines.append(
            f"\nBEST HOOK: {report['best_hook']['name']}"
            f" ({report['best_hook']['thumb_stop_rate']}% thumb-stop)"
        )

    if report["best_cpl_ad"]:
        lines.append(
            f"BEST CPL: {report['best_cpl_ad']['name']}"
            f" (${report['best_cpl_ad']['cpl']})"
        )

    if report["by_vertical"]:
        lines.append("\nBY VERTICAL:")
        for v, data in report["by_vertical"].items():
            cpl = (
                f"${data['spend'] / data['leads']:.0f}"
                if data["leads"] > 0
                else "N/A"
            )
            lines.append(f"  {v}: {data['leads']} leads, CPL {cpl}")

    return "\n".join(lines)


def send_ntfy(message, title="Video Ad Report"):
    """Send to trusted ntfy SALES topic."""
    try:
        sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))
        from trusted_ntfy import post_trusted_ntfy
        post_trusted_ntfy(
            NTFY_SALES,
            title,
            message,
            tags="bar_chart,video_camera",
            workflow_key="legacy-singleton:video-ad-reporter",
        )
        print(f"  → Queued trusted ntfy/{NTFY_SALES}")
    except Exception as e:
        print(f"  → trusted ntfy suppressed: {e}")


def cmd_report():
    state = load_state()
    state = add_sample_data(state)
    save_state(state)

    report = generate_report(state)
    message = format_report_ntfy(report)
    print(message)
    send_ntfy(message)
    print(f"\nReport saved: {REPORTS_DIR}/video-report-{report['date']}.json")


def cmd_status():
    state = load_state()
    print("VIDEO AD STATUS")
    print(f"  Video ads tracked: {len(state['video_ads'])}")
    print(f"  Image ads tracked: {len(state['image_ads'])}")
    print(f"  Last report: {state.get('last_report', 'Never')}")
    print(f"  Reports generated: {len(state.get('daily_reports', []))}")

    if state["video_ads"]:
        print("\nVIDEO ADS:")
        for ad in state["video_ads"]:
            m = ad["metrics"]
            status = ad.get("status", "unknown")
            print(f"  [{status}] {ad['name']}")
            if m["impressions"] > 0:
                print(
                    f"    {m['impressions']:,} imp | {m['leads']} leads"
                    f" | ${m['spend']:.2f} spend"
                )


def cmd_compare():
    state = load_state()
    video_ads = state.get("video_ads", [])
    image_ads = state.get("image_ads", [])

    print("VIDEO vs IMAGE — HEAD TO HEAD")
    print("=" * 50)

    v_leads = sum(a["metrics"]["leads"] for a in video_ads)
    i_leads = sum(a["metrics"]["leads"] for a in image_ads)
    v_spend = sum(a["metrics"]["spend"] for a in video_ads)
    i_spend = sum(a["metrics"]["spend"] for a in image_ads)

    print(f"{'Metric':<25} {'Video':>10} {'Image':>10}")
    print("-" * 50)
    print(f"{'Ads running':<25} {len(video_ads):>10} {len(image_ads):>10}")
    print(
        f"{'Total impressions':<25} "
        f"{sum(a['metrics']['impressions'] for a in video_ads):>10,} "
        f"{sum(a['metrics']['impressions'] for a in image_ads):>10,}"
    )
    print(f"{'Total leads':<25} {v_leads:>10} {i_leads:>10}")
    print(f"{'Total spend':<25} {'$' + f'{v_spend:.2f}':>10} {'$' + f'{i_spend:.2f}':>10}")

    v_cpl = f"${v_spend / v_leads:.2f}" if v_leads > 0 else "N/A"
    i_cpl = f"${i_spend / i_leads:.2f}" if i_leads > 0 else "N/A"
    print(f"{'Avg CPL':<25} {v_cpl:>10} {i_cpl:>10}")

    winner = "TBD"
    if v_leads > 0 and i_leads > 0:
        if (v_spend / v_leads) < (i_spend / i_leads):
            winner = "VIDEO wins on CPL"
        else:
            winner = "IMAGE wins on CPL"

    print(f"\nVerdict: {winner}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    commands = {
        "report": cmd_report,
        "status": cmd_status,
        "compare": cmd_compare,
    }
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands)}")
