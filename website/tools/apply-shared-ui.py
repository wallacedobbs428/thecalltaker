#!/usr/bin/env python3
"""
apply-shared-ui.py — Batch apply shared UI module to all pages.

Handles BOTH Pattern A (site-header, light theme) and Pattern B (header, dark theme).

Usage:
  python3 apply-shared-ui.py              # dry run (report only)
  python3 apply-shared-ui.py --apply      # actually modify files
  python3 apply-shared-ui.py --dark       # dark pages only (dry run)
  python3 apply-shared-ui.py --dark --apply  # dark pages only (apply)
  python3 apply-shared-ui.py --admin --apply # admin/toolkit pages only
  python3 apply-shared-ui.py --all --apply   # everything
  python3 apply-shared-ui.py --apply --strip-css  # also strip inline CSS duplicates
"""
import os, sys, re, glob

WEBSITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Target pages (Pattern A — site-header class, white/light theme) ──
TARGET_PAGES = [
    "index.html",
    "portal.html",
    # Industries (13)
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
    # Blog (40)
    "blog/best-answering-service-dental.html",
    "blog/best-answering-service-electricians.html",
    "blog/best-answering-service-funeral-homes.html",
    "blog/best-answering-service-garage-door.html",
    "blog/best-answering-service-hvac.html",
    "blog/best-answering-service-law-firms.html",
    "blog/best-answering-service-locksmiths.html",
    "blog/best-answering-service-medspa.html",
    "blog/best-answering-service-plumbers.html",
    "blog/best-answering-service-property-management.html",
    "blog/best-answering-service-roofing.html",
    "blog/best-answering-service-towing.html",
    "blog/best-answering-service-vet-clinics.html",
    "blog/dental-front-desk-overflow.html",
    "blog/dental-missed-call-cost.html",
    "blog/electrical-emergency-answering.html",
    "blog/electrical-missed-call-cost.html",
    "blog/funeral-home-compassionate-answering.html",
    "blog/funeral-missed-call-cost.html",
    "blog/garage-door-missed-call-cost.html",
    "blog/garage-door-repair-calls.html",
    "blog/hvac-missed-call-cost.html",
    "blog/hvac-virtual-receptionist-guide.html",
    "blog/law-firm-client-intake.html",
    "blog/legal-missed-call-cost.html",
    "blog/locksmith-emergency-dispatch.html",
    "blog/locksmith-missed-call-cost.html",
    "blog/medspa-booking-calls.html",
    "blog/medspa-missed-call-cost.html",
    "blog/plumbing-emergency-calls.html",
    "blog/plumbing-missed-call-cost.html",
    "blog/property-management-missed-call-cost.html",
    "blog/roofing-missed-call-cost.html",
    "blog/roofing-storm-season-calls.html",
    "blog/tenant-emergency-calls.html",
    "blog/towing-dispatch-answering.html",
    "blog/towing-missed-call-cost.html",
    "blog/vet-after-hours-calls.html",
    "blog/veterinary-missed-call-cost.html",
    # Case Studies (6)
    "case-studies/index.html",
    "case-studies/arctic-air-pros.html",
    "case-studies/palmetto-comfort.html",
    "case-studies/precision-plumbing.html",
    "case-studies/rapid-key-locksmith.html",
    "case-studies/reliable-rooter.html",
    # Onboarding (4)
    "onboarding/checklist.html",
    "onboarding/intake.html",
    "onboarding/live.html",
    "onboarding/next-steps.html",
    # Pilot (1)
    "pilot/index.html",
]

# ── Target pages (Pattern B — .header class, dark theme) ──
DARK_PAGES = [
    "blog.html",
    "blog-ai-vs-answering.html",
    "blog-missed-call-cost.html",
    "calculator.html",
    "compare.html",
    "industries.html",
    "services.html",
    "agency.html",
    "partners.html",
    "signup.html",
    "thank-you.html",
    "privacy.html",
    "terms.html",
    "404.html",
    "your-audit.html",
    "try-funnel/index.html",
    "try-funnel/checkout.html",
    "try-funnel/upgrade.html",
]

# ── Admin + Toolkit pages ──
ADMIN_PAGES = [
    "admin/index.html",
    "admin/bots.html",
    "admin/contacts.html",
    "admin/inbox.html",
    "admin/intake.html",
    "admin/onboarding.html",
    "admin/pipeline.html",
    "admin/reports.html",
    "admin/settings.html",
    "toolkit/index.html",
    "toolkit/call-cheatsheet.html",
    "toolkit/case-studies.html",
    "toolkit/objection-handler.html",
]

# ── Tags ──
CSS_TAG = '<link rel="stylesheet" href="/shared/ui.css">'
JS_TAG  = '<script src="/shared/ui.js" defer></script>'
DARK_CSS_TAG = '<link rel="stylesheet" href="/shared/ui-dark.css">'
DARK_JS_TAG  = '<script src="/shared/ui-dark.js" defer></script>'

# Regex to find the inline <script> block with the "// Sticky header" pattern
INLINE_JS_PATTERN = re.compile(
    r'<script>\s*\n?\s*// Sticky header.*?</script>',
    re.DOTALL
)
INLINE_JS_PATTERN_MINIFIED = re.compile(
    r'<script>\s*//\s*Sticky header.*?</script>',
    re.DOTALL
)

# Pattern B inline JS: script.js contains the mobile menu + sticky header
# We guard it rather than remove it (script.js has other features too)
SCRIPT_JS_GUARD = re.compile(
    r'(<script src="[^"]*script\.js"[^>]*></script>)',
    re.DOTALL
)

# CSS selectors that ui.css now provides — for Phase 3 inline CSS stripping
SHARED_CSS_SELECTORS = [
    '.site-header', '.site-header.scrolled',
    '.header-inner', '.logo',
    '.nav-links', '.nav-links a',
    '.nav-demo',
    '.mobile-toggle', '.mobile-toggle span',
    '.fade-up', '.fade-up.visible',
]


def process_file(rel_path, apply=False, strip_css=False):
    """Process a Pattern A file. Returns (status, messages) tuple."""
    full_path = os.path.join(WEBSITE_DIR, rel_path)
    if not os.path.exists(full_path):
        return "SKIP", [f"File not found: {rel_path}"]

    with open(full_path, 'r', encoding='utf-8') as f:
        original = f.read()

    html = original
    messages = []
    is_index = (rel_path == "index.html")

    # ── CHECK: already has shared ui? ──
    has_css = '/shared/ui.css' in html
    has_js = '/shared/ui.js' in html

    # ── 1. Add CSS link before </head> ──
    if not has_css:
        if '</head>' in html:
            html = html.replace('</head>', CSS_TAG + '\n</head>', 1)
            messages.append("+ Added ui.css link")
        else:
            messages.append("! No </head> found")
    else:
        messages.append("= ui.css already present")

    # ── 2. index.html special handling ──
    if is_index:
        if 'window.__tctUILoaded' not in html:
            for marker in ["(function(){", "(function() {", "(function () {"]:
                idx = html.find(marker)
                if idx != -1:
                    break
            if idx != -1:
                script_open = html.rfind('<script>', 0, idx)
                if script_open != -1:
                    insert_pos = html.find('>', script_open) + 1
                    html = html[:insert_pos] + '\nwindow.__tctUILoaded = true;\n' + html[insert_pos:]
                    messages.append("+ Added __tctUILoaded guard to inline JS")
                else:
                    messages.append("! Could not find <script> before IIFE")
            else:
                messages.append("! Could not find IIFE in index.html")
        else:
            messages.append("= __tctUILoaded already present")
        messages.append("= Skipped ui.js (index.html keeps GSAP JS)")

    else:
        # ── 3. Add JS before </body> ──
        if not has_js:
            if '</body>' in html:
                html = html.replace('</body>', JS_TAG + '\n</body>', 1)
                messages.append("+ Added ui.js script")
            else:
                messages.append("! No </body> found")
        else:
            messages.append("= ui.js already present")

        # ── 4. Remove duplicate inline JS (// Sticky header block) ──
        match = INLINE_JS_PATTERN.search(html)
        if not match:
            match = INLINE_JS_PATTERN_MINIFIED.search(html)
        if match:
            html = html[:match.start()] + html[match.end():]
            html = re.sub(r'\n{3,}', '\n\n', html)
            messages.append("- Removed inline Sticky header JS block")
        else:
            messages.append("= No inline Sticky header JS found")

    # ── 5. Strip duplicate inline CSS (optional) ──
    if strip_css and not is_index:
        stripped_count = 0
        nav_open = re.compile(r'\.nav-links\.open\s*\{[^}]+\}', re.DOTALL)
        if nav_open.search(html):
            html = nav_open.sub('/* [moved to /shared/ui.css] */', html)
            stripped_count += 1
        if stripped_count > 0:
            messages.append(f"- Stripped {stripped_count} duplicate CSS block(s)")

    # ── 6. Verify tracking tags still present ──
    messages.extend(check_tracking(html))

    # ── Write changes ──
    return write_result(full_path, original, html, apply, messages)


def process_dark_file(rel_path, apply=False):
    """Process a Pattern B (dark theme) file. Returns (status, messages) tuple."""
    full_path = os.path.join(WEBSITE_DIR, rel_path)
    if not os.path.exists(full_path):
        return "SKIP", [f"File not found: {rel_path}"]

    with open(full_path, 'r', encoding='utf-8') as f:
        original = f.read()

    html = original
    messages = []

    # ── CHECK: already has dark ui? ──
    has_dark_css = '/shared/ui-dark.css' in html
    has_dark_js = '/shared/ui-dark.js' in html
    # Safety: ensure no Pattern A ui loaded
    has_light_css = '/shared/ui.css' in html
    if has_light_css:
        messages.append("! WARNING: Pattern A ui.css found on dark page — skipping to avoid collision")
        return "SKIP", messages

    # ── 1. Add dark CSS link before </head> ──
    if not has_dark_css:
        if '</head>' in html:
            html = html.replace('</head>', DARK_CSS_TAG + '\n</head>', 1)
            messages.append("+ Added ui-dark.css link")
        else:
            messages.append("! No </head> found")
    else:
        messages.append("= ui-dark.css already present")

    # ── 2. Add dark JS before </body> ──
    if not has_dark_js:
        if '</body>' in html:
            html = html.replace('</body>', DARK_JS_TAG + '\n</body>', 1)
            messages.append("+ Added ui-dark.js script")
        else:
            messages.append("! No </body> found")
    else:
        messages.append("= ui-dark.js already present")

    # ── 3. Guard existing script.js menu code ──
    # script.js has mobile menu + sticky header code that overlaps with ui-dark.js.
    # Add __tctUILoaded guard before script.js loads so it can check the flag.
    if 'script.js' in html and 'window.__tctUILoaded' not in html:
        # Insert guard before script.js tag
        m = SCRIPT_JS_GUARD.search(html)
        if m:
            guard = '<script>if(!window.__tctUILoaded){window.__tctScriptJsOK=true;}</script>\n'
            html = html[:m.start()] + guard + html[m.start():]
            messages.append("+ Added __tctUILoaded guard before script.js")
        else:
            messages.append("= No script.js tag to guard")
    else:
        if 'script.js' not in html:
            messages.append("= No script.js found")
        else:
            messages.append("= __tctUILoaded guard already present")

    # ── 4. Verify tracking tags still present ──
    messages.extend(check_tracking(html))

    return write_result(full_path, original, html, apply, messages)


def process_admin_file(rel_path, apply=False):
    """Process an admin/toolkit file. Returns (status, messages) tuple."""
    full_path = os.path.join(WEBSITE_DIR, rel_path)
    if not os.path.exists(full_path):
        return "SKIP", [f"File not found: {rel_path}"]

    with open(full_path, 'r', encoding='utf-8') as f:
        original = f.read()

    html = original
    messages = []

    has_dark_css = '/shared/ui-dark.css' in html
    has_dark_js = '/shared/ui-dark.js' in html

    # ── 1. Add data-app="admin" to <body> ──
    if 'data-app="admin"' not in html:
        if '<body>' in html:
            html = html.replace('<body>', '<body data-app="admin">', 1)
            messages.append("+ Added data-app=\"admin\" to <body>")
        elif '<body ' in html:
            html = html.replace('<body ', '<body data-app="admin" ', 1)
            messages.append("+ Added data-app=\"admin\" to <body>")
        else:
            messages.append("! No <body> tag found")
    else:
        messages.append("= data-app=\"admin\" already present")

    # ── 2. Add TCT_UI_V2 feature flag ──
    if 'TCT_UI_V2' not in html:
        if '</head>' in html:
            flag = '<script>window.TCT_UI_V2 = true;</script>\n'
            html = html.replace('</head>', flag + DARK_CSS_TAG + '\n</head>', 1)
            messages.append("+ Added TCT_UI_V2 flag + ui-dark.css")
        else:
            messages.append("! No </head> found")
    else:
        messages.append("= TCT_UI_V2 already present")
        if not has_dark_css:
            if '</head>' in html:
                html = html.replace('</head>', DARK_CSS_TAG + '\n</head>', 1)
                messages.append("+ Added ui-dark.css link")

    # ── 3. Add dark JS before </body> ──
    if not has_dark_js:
        if '</body>' in html:
            html = html.replace('</body>', DARK_JS_TAG + '\n</body>', 1)
            messages.append("+ Added ui-dark.js script")
        else:
            messages.append("! No </body> found")
    else:
        messages.append("= ui-dark.js already present")

    return write_result(full_path, original, html, apply, messages)


def check_tracking(html):
    """Check tracking tags are present. Returns list of messages."""
    messages = []
    tracking = []
    if 'AW-17970510102' in html or 'G-29LL5GPBQV' in html:
        tracking.append("gtag")
    if 'tct-tracking' in html:
        tracking.append("tct-tracking")
    if 'fbq(' in html:
        tracking.append("meta-pixel")
    if tracking:
        messages.append(f"  Tracking OK: {', '.join(tracking)}")
    else:
        messages.append("  (No tracking tags — may be intentional)")
    return messages


def write_result(full_path, original, html, apply, messages):
    """Write file if changed. Returns (status, messages)."""
    changed = html != original
    if changed and apply:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return "UPDATED", messages
    elif changed:
        return "WOULD UPDATE", messages
    else:
        return "NO CHANGE", messages


def main():
    apply = '--apply' in sys.argv
    strip_css = '--strip-css' in sys.argv
    dark_only = '--dark' in sys.argv
    admin_only = '--admin' in sys.argv
    run_all = '--all' in sys.argv

    # Determine which page sets to process
    page_sets = []
    if run_all:
        page_sets = [
            ("Pattern A (light)", TARGET_PAGES, process_file),
            ("Pattern B (dark)", DARK_PAGES, process_dark_file),
            ("Admin/Toolkit", ADMIN_PAGES, process_admin_file),
        ]
    elif dark_only:
        page_sets = [("Pattern B (dark)", DARK_PAGES, process_dark_file)]
    elif admin_only:
        page_sets = [("Admin/Toolkit", ADMIN_PAGES, process_admin_file)]
    else:
        page_sets = [("Pattern A (light)", TARGET_PAGES, process_file)]

    mode = "APPLYING" if apply else "DRY RUN"
    total_pages = sum(len(pages) for _, pages, _ in page_sets)

    print(f"\n{'='*60}")
    print(f"  TCT Shared UI Batch Apply — {mode}")
    print(f"  Target: {total_pages} pages across {len(page_sets)} set(s)")
    print(f"{'='*60}\n")

    grand_stats = {"UPDATED": 0, "WOULD UPDATE": 0, "NO CHANGE": 0, "SKIP": 0}

    for set_name, pages, processor in page_sets:
        print(f"\n--- {set_name} ({len(pages)} pages) ---\n")
        for rel_path in pages:
            if processor == process_file:
                status, msgs = processor(rel_path, apply=apply, strip_css=strip_css)
            elif processor == process_admin_file:
                status, msgs = processor(rel_path, apply=apply)
            else:
                status, msgs = processor(rel_path, apply=apply)
            grand_stats[status] = grand_stats.get(status, 0) + 1

            icon = {"UPDATED": "\u2705", "WOULD UPDATE": "\U0001f504", "NO CHANGE": "\u2796", "SKIP": "\u26a0\ufe0f"}.get(status, "?")
            print(f"{icon} [{status}] {rel_path}")
            for m in msgs:
                print(f"    {m}")

    print(f"\n{'='*60}")
    print(f"  Results:")
    for k, v in grand_stats.items():
        if v > 0:
            print(f"    {k}: {v}")
    print(f"{'='*60}\n")

    if not apply and grand_stats.get("WOULD UPDATE", 0) > 0:
        print("  Run with --apply to write changes.\n")


if __name__ == '__main__':
    main()
