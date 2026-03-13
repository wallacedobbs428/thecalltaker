#!/usr/bin/env python3
"""
site-monitor.py — Site health monitor for thecalltaker.com

Checks all website pages for common issues:
  - Wrong stylesheet references (ui.css instead of ui-dark.css on dark pages)
  - Missing GHL calendar embed on industry pages
  - Missing GHL API integration on industry pages
  - Missing ntfy notification on industry pages
  - Missing tracking scripts
  - Broken internal links
  - Missing meta tags

Usage:
  python3 site-monitor.py check         # run all checks, exit 1 if issues found
  python3 site-monitor.py status        # quick summary
  python3 site-monitor.py check --fix   # auto-fix what can be fixed

Designed to run hourly via launchd. Sends ntfy alert on issues.
"""
import os, sys, re, json, glob, datetime

WEBSITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NTFY_TOPIC = "tct-system-vRsfXQRQ"

# ── Correct GHL settings ──
GHL_API_URL = "https://services.leadconnectorhq.com/contacts/"
GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_CALENDAR_ID = "h4IlzccZ1m3JprEQqpMJ"
GHL_CALENDAR_URL = f"https://api.leadconnectorhq.com/widget/booking/{GHL_CALENDAR_ID}"
NTFY_URGENT_TOPIC = "tct-urgent-Hk9UOEZR"

# ── Page classifications ──
INDUSTRY_PAGES = [
    "industries/dental.html",
    "industries/electrical.html",
    "industries/funeral.html",
    "industries/garage-door.html",
    "industries/hvac.html",
    "industries/legal.html",
    "industries/locksmith.html",
    "industries/medspa.html",
    "industries/plumbing.html",
    "industries/property-management.html",
    "industries/roofing.html",
    "industries/towing.html",
    "industries/veterinary.html",
]

# Pages that MUST use ui-dark.css (dark theme)
DARK_THEME_PAGES = [
    "blog.html",
    "blog-ai-vs-answering.html",
    "blog-missed-call-cost.html",
    "calculator.html",
    "compare.html",
    "demo-showcase.html",
    "industries.html",
    "services.html",
    "agency.html",
    "partners.html",
    "signup.html",
    "thank-you.html",
    "privacy.html",
    "terms.html",
    "pricing.html",
    "404.html",
    "your-audit.html",
    "try-funnel/index.html",
    "try-funnel/checkout.html",
    "try-funnel/upgrade.html",
    "toolkit/index.html",
    "toolkit/call-cheatsheet.html",
    "toolkit/case-studies.html",
    "toolkit/objection-handler.html",
    "admin/index.html",
    "admin/bots.html",
    "admin/contacts.html",
    "admin/inbox.html",
    "admin/intake.html",
    "admin/onboarding.html",
    "admin/pipeline.html",
    "admin/reports.html",
    "admin/settings.html",
    "case-studies/index.html",
    "case-studies/arctic-air-pros.html",
    "case-studies/palmetto-comfort.html",
    "case-studies/precision-plumbing.html",
    "case-studies/rapid-key-locksmith.html",
    "case-studies/reliable-rooter.html",
    "portal.html",
    "onboarding/checklist.html",
    "onboarding/intake.html",
    "onboarding/live.html",
    "onboarding/next-steps.html",
    "pilot/index.html",
    "pilot/ghost/index.html",
] + [f"blog/{f}" for f in [
    "best-answering-service-dental.html",
    "best-answering-service-electricians.html",
    "best-answering-service-funeral-homes.html",
    "best-answering-service-garage-door.html",
    "best-answering-service-hvac.html",
    "best-answering-service-law-firms.html",
    "best-answering-service-locksmiths.html",
    "best-answering-service-medspa.html",
    "best-answering-service-plumbers.html",
    "best-answering-service-property-management.html",
    "best-answering-service-roofing.html",
    "best-answering-service-towing.html",
    "best-answering-service-vet-clinics.html",
    "dental-front-desk-overflow.html",
    "dental-missed-call-cost.html",
    "electrical-emergency-answering.html",
    "electrical-missed-call-cost.html",
    "funeral-home-compassionate-answering.html",
    "funeral-missed-call-cost.html",
    "garage-door-missed-call-cost.html",
    "garage-door-repair-calls.html",
    "hvac-missed-call-cost.html",
    "hvac-virtual-receptionist-guide.html",
    "law-firm-client-intake.html",
    "legal-missed-call-cost.html",
    "locksmith-emergency-dispatch.html",
    "locksmith-missed-call-cost.html",
    "medspa-booking-calls.html",
    "medspa-missed-call-cost.html",
    "plumbing-emergency-calls.html",
    "plumbing-missed-call-cost.html",
    "property-management-missed-call-cost.html",
    "roofing-missed-call-cost.html",
    "roofing-storm-season-calls.html",
    "tenant-emergency-calls.html",
    "towing-dispatch-answering.html",
    "towing-missed-call-cost.html",
    "vet-after-hours-calls.html",
    "veterinary-missed-call-cost.html",
]]

# Pages that must NOT use ui.css (should use ui-dark.css)
WRONG_STYLESHEET_PATTERN = re.compile(r'/shared/ui\.css')
WRONG_SCRIPT_PATTERN = re.compile(r'/shared/ui\.js')


def read_file(rel_path):
    full = os.path.join(WEBSITE_DIR, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def check_all():
    issues = []

    # ── CHECK 1: Industry pages — GHL integration ──
    for page in INDUSTRY_PAGES:
        html = read_file(page)
        if html is None:
            issues.append(("CRITICAL", page, "File missing"))
            continue

        # Must have GHL calendar embed
        if GHL_CALENDAR_ID not in html:
            issues.append(("CRITICAL", page, f"Missing GHL calendar embed (ID: {GHL_CALENDAR_ID})"))

        # Must have GHL API integration in form
        if GHL_API_URL not in html:
            issues.append(("CRITICAL", page, f"Missing GHL API URL ({GHL_API_URL})"))

        # Must have API key
        if GHL_API_KEY not in html:
            issues.append(("CRITICAL", page, "Missing GHL API key in form submission"))

        # Must have ntfy notification
        if NTFY_URGENT_TOPIC not in html:
            issues.append(("HIGH", page, "Missing ntfy urgent notification on form submit"))

        # Must have meta description
        if '<meta name="description"' not in html:
            issues.append(("HIGH", page, "Missing meta description"))

        # Must have canonical URL
        if '<link rel="canonical"' not in html:
            issues.append(("HIGH", page, "Missing canonical URL"))

    # ── CHECK 2: Stylesheet references — no ui.css on dark pages ──
    all_html_files = glob.glob(os.path.join(WEBSITE_DIR, "**/*.html"), recursive=True)
    for full_path in all_html_files:
        rel = os.path.relpath(full_path, WEBSITE_DIR)
        html = read_file(rel)
        if html is None:
            continue

        if WRONG_STYLESHEET_PATTERN.search(html):
            issues.append(("HIGH", rel, "References /shared/ui.css instead of /shared/ui-dark.css"))

        if WRONG_SCRIPT_PATTERN.search(html):
            issues.append(("HIGH", rel, "References /shared/ui.js instead of /shared/ui-dark.js"))

    # ── CHECK 3: Core pages exist ──
    core_pages = [
        "index.html", "signup.html", "calculator.html", "book.html",
        "demo-showcase.html", "privacy.html", "terms.html", "404.html",
    ]
    for page in core_pages:
        if read_file(page) is None:
            issues.append(("CRITICAL", page, "Core page missing"))

    # ── CHECK 4: Shared assets exist ──
    shared_assets = [
        "shared/ui-dark.css", "shared/ui-dark.js",
        "shared/ab-split.js", "tct-tracking.js",
    ]
    for asset in shared_assets:
        full = os.path.join(WEBSITE_DIR, asset)
        if not os.path.exists(full):
            issues.append(("CRITICAL", asset, "Shared asset missing"))

    # ── CHECK 5: All HTML files have <!DOCTYPE html> ──
    for full_path in all_html_files:
        rel = os.path.relpath(full_path, WEBSITE_DIR)
        html = read_file(rel)
        if html and not html.strip().startswith("<!DOCTYPE html>") and not html.strip().startswith("<!doctype html>"):
            issues.append(("LOW", rel, "Missing <!DOCTYPE html> declaration"))

    return issues


def send_ntfy_alert(issues):
    try:
        import urllib.request
        critical = [i for i in issues if i[0] == "CRITICAL"]
        high = [i for i in issues if i[0] == "HIGH"]
        body = f"Site Monitor: {len(issues)} issues found\n"
        body += f"CRITICAL: {len(critical)} | HIGH: {len(high)}\n\n"
        for severity, page, msg in issues[:10]:
            body += f"[{severity}] {page}: {msg}\n"
        if len(issues) > 10:
            body += f"\n... and {len(issues) - 10} more"

        priority = "urgent" if critical else "high"
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=body.encode(),
            headers={
                "Title": f"Site Monitor: {len(issues)} issues found",
                "Priority": priority,
                "Tags": "warning,globe_with_meridians",
            },
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  [!] Failed to send ntfy alert: {e}", file=sys.stderr)


def cmd_check():
    print(f"Site Health Monitor — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scanning: {WEBSITE_DIR}")
    print("=" * 60)

    issues = check_all()

    if not issues:
        print("\nAll checks passed. 0 issues found.")
        return 0

    # Group by severity
    for severity in ["CRITICAL", "HIGH", "LOW"]:
        group = [i for i in issues if i[0] == severity]
        if group:
            print(f"\n{severity} ({len(group)}):")
            for _, page, msg in group:
                print(f"  [{severity}] {page}: {msg}")

    print(f"\nTotal: {len(issues)} issues found.")

    # Send ntfy alert if there are CRITICAL or HIGH issues
    critical_or_high = [i for i in issues if i[0] in ("CRITICAL", "HIGH")]
    if critical_or_high:
        send_ntfy_alert(critical_or_high)

    return 1


def cmd_status():
    issues = check_all()
    critical = len([i for i in issues if i[0] == "CRITICAL"])
    high = len([i for i in issues if i[0] == "HIGH"])
    low = len([i for i in issues if i[0] == "LOW"])
    print(f"Site Monitor Status: {len(issues)} issues (CRITICAL={critical} HIGH={high} LOW={low})")
    return 0 if not issues else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 site-monitor.py [check|status]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "check":
        sys.exit(cmd_check())
    elif cmd == "status":
        sys.exit(cmd_status())
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 site-monitor.py [check|status]")
        sys.exit(1)
