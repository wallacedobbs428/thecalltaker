#!/usr/bin/env python3
"""
LEAD DASHBOARD API — The Call Taker
=====================================
Aggregates data from all engine state files and generates a real-time
dashboard JSON + static HTML dashboard page.

Commands:
  generate  — Generate dashboard-data.json + lead-dashboard.html
  status    — Show quick summary

Schedule: Every 10 min via launchd
"""

import sys
import os
import json
from datetime import datetime

OPS_DIR = os.path.expanduser("~/thecalltaker/ops")

STATE_FILES = {
    "blast": os.path.join(OPS_DIR, "blast-engine-state.json"),
    "outbound_sms": os.path.join(OPS_DIR, "outbound-sms-state.json"),
    "hot_lead": os.path.join(OPS_DIR, "hot-lead-converter-state.json"),
    "payment_reminder": os.path.join(OPS_DIR, "payment-reminder-state.json"),
    "sms_followup": os.path.join(OPS_DIR, "blast-sms-followup-state.json"),
    "dm_tracker": os.path.join(OPS_DIR, "dm-tracker-state.json"),
    "stripe": os.path.join(OPS_DIR, "stripe-webhook-state.json"),
}

OUTPUT_JSON = os.path.join(OPS_DIR, "lead-dashboard-data.json")
OUTPUT_HTML = os.path.expanduser("~/thecalltaker/website/admin/lead-dashboard.html")


def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def cmd_generate():
    now = datetime.now()
    data = {"generated_at": now.isoformat(), "engines": {}}

    # Blast Engine
    blast = load_json(STATE_FILES["blast"])
    blast_stats = blast.get("stats", {})
    data["engines"]["blast"] = {
        "name": "Cold Email Blast",
        "total_sent": blast_stats.get("total_sent", 0),
        "total_failed": blast_stats.get("total_failed", 0),
        "total_invalid": blast_stats.get("total_invalid", 0),
        "subject_a_sent": blast_stats.get("subject_a_sent", 0),
        "subject_b_sent": blast_stats.get("subject_b_sent", 0),
        "total_runs": blast_stats.get("total_runs", 0),
        "success_rate": round(blast_stats.get("total_sent", 0) / max(blast_stats.get("total_sent", 0) + blast_stats.get("total_failed", 0), 1) * 100),
    }

    # Outbound SMS
    sms = load_json(STATE_FILES["outbound_sms"])
    sms_stats = sms.get("stats", {})
    sms_enrolled = sms.get("enrolled", {})
    active_sms = sum(1 for e in sms_enrolled.values() if not e.get("replied") and len(e.get("touches_sent", [])) < 3)
    data["engines"]["outbound_sms"] = {
        "name": "Outbound SMS",
        "total_enrolled": sms_stats.get("total_enrolled", 0),
        "total_sms_sent": sms_stats.get("total_sms_sent", 0),
        "active_sequences": active_sms,
        "total_runs": sms_stats.get("total_runs", 0),
    }

    # Hot Lead Converter
    hlc = load_json(STATE_FILES["hot_lead"])
    hlc_stats = hlc.get("stats", {})
    hlc_enrolled = hlc.get("enrolled", {})
    active_hlc = sum(1 for e in hlc_enrolled.values() if not e.get("converted") and not e.get("booked") and len(e.get("touches_sent", [])) < 5)
    converted_hlc = sum(1 for e in hlc_enrolled.values() if e.get("converted") or e.get("booked"))
    data["engines"]["hot_lead"] = {
        "name": "Hot Lead Converter",
        "total_enrolled": hlc_stats.get("total_enrolled", 0),
        "active_sequences": active_hlc,
        "converted": converted_hlc,
        "total_touches": hlc_stats.get("total_touches_sent", 0),
        "total_runs": hlc_stats.get("total_runs", 0),
    }

    # Payment Reminder
    pr = load_json(STATE_FILES["payment_reminder"])
    pr_stats = pr.get("stats", {})
    data["engines"]["payment_reminder"] = {
        "name": "Payment Reminder",
        "total_reminders": pr_stats.get("total_reminders", 0),
        "total_runs": pr_stats.get("total_runs", 0),
    }

    # SMS Follow-up
    sf = load_json(STATE_FILES["sms_followup"])
    sf_stats = sf.get("stats", {})
    data["engines"]["sms_followup"] = {
        "name": "Blast SMS Follow-Up",
        "total_sms": sf_stats.get("total_sms", 0),
        "total_runs": sf_stats.get("total_runs", 0),
    }

    # DM Tracker
    dm = load_json(STATE_FILES["dm_tracker"])
    dm_stats = dm.get("stats", {})
    data["engines"]["dm_tracker"] = {
        "name": "DM Outreach",
        "linkedin_sent": dm_stats.get("linkedin_sent", 0),
        "linkedin_replied": dm_stats.get("linkedin_replied", 0),
        "instagram_sent": dm_stats.get("instagram_sent", 0),
        "instagram_replied": dm_stats.get("instagram_replied", 0),
        "demos_booked": dm_stats.get("demos_booked", 0),
    }

    # Stripe
    stripe = load_json(STATE_FILES["stripe"])
    data["engines"]["stripe"] = {
        "name": "Stripe Payments",
        "total_revenue": stripe.get("total_revenue", 0),
        "total_customers": stripe.get("total_customers", 0),
        "mrr": stripe.get("mrr", 0),
    }

    # Summary
    data["summary"] = {
        "total_emails_sent": blast_stats.get("total_sent", 0),
        "total_sms_sent": sms_stats.get("total_sms_sent", 0) + sf_stats.get("total_sms", 0),
        "total_leads_active": active_sms + active_hlc,
        "total_converted": converted_hlc,
        "total_revenue": stripe.get("total_revenue", 0),
        "mrr": stripe.get("mrr", 0),
        "total_dms_sent": dm_stats.get("linkedin_sent", 0) + dm_stats.get("instagram_sent", 0),
    }

    # Save JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)

    # Generate HTML dashboard
    generate_html(data)

    print(f"Dashboard generated: {OUTPUT_JSON}")
    print(f"HTML: {OUTPUT_HTML}")


def generate_html(data):
    s = data.get("summary", {})
    engines = data.get("engines", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lead Dashboard — The Call Taker</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#0a0a0a;color:#fff;padding:24px;min-height:100vh}}
.header{{text-align:center;margin-bottom:32px}}
.header h1{{font-size:1.8rem;font-weight:800;letter-spacing:-.02em}}
.header h1 span{{color:#00dc82}}
.header p{{color:#71717a;margin-top:4px;font-size:.85rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px}}
.stat-card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;text-align:center}}
.stat-card .value{{font-size:2rem;font-weight:800;color:#00dc82}}
.stat-card .label{{font-size:.8rem;color:#a1a1aa;margin-top:4px;text-transform:uppercase;letter-spacing:.05em}}
.engines{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}
.engine{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px}}
.engine h3{{font-size:1rem;font-weight:700;margin-bottom:12px;color:#fff}}
.engine h3::before{{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#00dc82;margin-right:8px}}
.engine .row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:.85rem}}
.engine .row .k{{color:#a1a1aa}}.engine .row .v{{font-weight:600;color:#fff}}
.engine .row:last-child{{border-bottom:none}}
.revenue{{color:#00dc82 !important;font-size:1.1rem !important}}
.footer{{text-align:center;margin-top:32px;color:#52525b;font-size:.75rem}}
</style>
</head>
<body>
<div class="header">
<h1>The Call <span>Taker</span> — Lead Dashboard</h1>
<p>Last updated: {data.get('generated_at','')[:19].replace('T',' ')}</p>
</div>

<div class="grid">
<div class="stat-card"><div class="value">{s.get('total_emails_sent',0)}</div><div class="label">Emails Sent</div></div>
<div class="stat-card"><div class="value">{s.get('total_sms_sent',0)}</div><div class="label">SMS Sent</div></div>
<div class="stat-card"><div class="value">{s.get('total_dms_sent',0)}</div><div class="label">DMs Sent</div></div>
<div class="stat-card"><div class="value">{s.get('total_leads_active',0)}</div><div class="label">Active Leads</div></div>
<div class="stat-card"><div class="value">{s.get('total_converted',0)}</div><div class="label">Converted</div></div>
<div class="stat-card"><div class="value revenue">${s.get('mrr',0):,.0f}</div><div class="label">MRR</div></div>
</div>

<div class="engines">"""

    # Blast
    b = engines.get("blast", {})
    html += f"""<div class="engine"><h3>Cold Email Blast</h3>
<div class="row"><span class="k">Sent</span><span class="v">{b.get('total_sent',0)}</span></div>
<div class="row"><span class="k">Failed</span><span class="v">{b.get('total_failed',0)}</span></div>
<div class="row"><span class="k">Invalid</span><span class="v">{b.get('total_invalid',0)}</span></div>
<div class="row"><span class="k">Success Rate</span><span class="v">{b.get('success_rate',0)}%</span></div>
<div class="row"><span class="k">Subject A</span><span class="v">{b.get('subject_a_sent',0)}</span></div>
<div class="row"><span class="k">Subject B</span><span class="v">{b.get('subject_b_sent',0)}</span></div>
<div class="row"><span class="k">Runs</span><span class="v">{b.get('total_runs',0)}</span></div>
</div>"""

    # Outbound SMS
    o = engines.get("outbound_sms", {})
    html += f"""<div class="engine"><h3>Outbound SMS</h3>
<div class="row"><span class="k">Enrolled</span><span class="v">{o.get('total_enrolled',0)}</span></div>
<div class="row"><span class="k">SMS Sent</span><span class="v">{o.get('total_sms_sent',0)}</span></div>
<div class="row"><span class="k">Active Sequences</span><span class="v">{o.get('active_sequences',0)}</span></div>
<div class="row"><span class="k">Runs</span><span class="v">{o.get('total_runs',0)}</span></div>
</div>"""

    # Hot Lead
    h = engines.get("hot_lead", {})
    html += f"""<div class="engine"><h3>Hot Lead Converter</h3>
<div class="row"><span class="k">Enrolled</span><span class="v">{h.get('total_enrolled',0)}</span></div>
<div class="row"><span class="k">Active</span><span class="v">{h.get('active_sequences',0)}</span></div>
<div class="row"><span class="k">Converted</span><span class="v">{h.get('converted',0)}</span></div>
<div class="row"><span class="k">Touches Sent</span><span class="v">{h.get('total_touches',0)}</span></div>
<div class="row"><span class="k">Runs</span><span class="v">{h.get('total_runs',0)}</span></div>
</div>"""

    # DM Tracker
    d = engines.get("dm_tracker", {})
    html += f"""<div class="engine"><h3>DM Outreach</h3>
<div class="row"><span class="k">LinkedIn Sent</span><span class="v">{d.get('linkedin_sent',0)}</span></div>
<div class="row"><span class="k">LinkedIn Replied</span><span class="v">{d.get('linkedin_replied',0)}</span></div>
<div class="row"><span class="k">Instagram Sent</span><span class="v">{d.get('instagram_sent',0)}</span></div>
<div class="row"><span class="k">Instagram Replied</span><span class="v">{d.get('instagram_replied',0)}</span></div>
<div class="row"><span class="k">Demos Booked</span><span class="v">{d.get('demos_booked',0)}</span></div>
</div>"""

    # Stripe
    st = engines.get("stripe", {})
    html += f"""<div class="engine"><h3>Stripe Payments</h3>
<div class="row"><span class="k">Revenue</span><span class="v revenue">${st.get('total_revenue',0):,.0f}</span></div>
<div class="row"><span class="k">MRR</span><span class="v revenue">${st.get('mrr',0):,.0f}</span></div>
<div class="row"><span class="k">Customers</span><span class="v">{st.get('total_customers',0)}</span></div>
</div>"""

    # Follow-ups
    sf = engines.get("sms_followup", {})
    pr = engines.get("payment_reminder", {})
    html += f"""<div class="engine"><h3>Follow-Ups</h3>
<div class="row"><span class="k">Blast SMS Follow-Up</span><span class="v">{sf.get('total_sms',0)} sent</span></div>
<div class="row"><span class="k">Payment Reminders</span><span class="v">{pr.get('total_reminders',0)} sent</span></div>
</div>"""

    html += """</div>
<div class="footer">The Call Taker — Lead Dashboard — Auto-refreshes every 10 min</div>
<script>setTimeout(()=>location.reload(),600000);</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)


def cmd_status():
    data = load_json(OUTPUT_JSON)
    s = data.get("summary", {})
    print(f"\nDashboard: {s.get('total_emails_sent',0)} emails | {s.get('total_sms_sent',0)} SMS | "
          f"{s.get('total_leads_active',0)} active | {s.get('total_converted',0)} converted | "
          f"MRR: ${s.get('mrr',0):,.0f}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lead-dashboard-api.py <generate|status>")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "generate":
        cmd_generate()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown: {cmd}")
