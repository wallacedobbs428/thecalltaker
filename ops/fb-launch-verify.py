#!/usr/bin/env python3
"""
Facebook Lead Ads Launch Verification — The Call Taker
Checks all pre-launch requirements and outputs a report.
Usage: python3 ops/fb-launch-verify.py
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = REPO_ROOT / "website"
OUTPUT_FILE = REPO_ROOT / "docs" / "launch-verification-report.md"

results = []


def check(name, passed, detail="", fix=""):
    status = "PASS" if passed else "FAIL"
    results.append({"name": name, "status": status, "detail": detail, "fix": fix})
    icon = "+" if passed else "!"
    print(f"  [{icon}] {name}: {status}" + (f" — {detail}" if detail else ""))


def run():
    print("Facebook Lead Ads Launch Verification")
    print("=" * 50)
    print()

    # 1. Check Meta Pixel on all HTML files
    print("1. META PIXEL")
    html_files = list(WEBSITE_DIR.rglob("*.html"))
    has_pixel = 0
    missing_pixel = []
    for f in html_files:
        rel = f.relative_to(REPO_ROOT)
        if 'dashboard/' in str(rel) or 'reports/' in str(rel):
            continue
        content = f.read_text(errors='ignore')
        if 'fbevents.js' in content:
            has_pixel += 1
        elif '</head>' in content:
            missing_pixel.append(str(rel))

    check(
        "Meta Pixel present in HTML files",
        len(missing_pixel) == 0,
        f"{has_pixel} pages have pixel, {len(missing_pixel)} missing",
        f"Run: python3 ops/inject-meta-pixel.py\nMissing: {', '.join(missing_pixel[:5])}" if missing_pixel else ""
    )

    # Check for YOUR_PIXEL_ID placeholder
    placeholder_count = 0
    for f in html_files:
        content = f.read_text(errors='ignore')
        if 'YOUR_PIXEL_ID' in content:
            placeholder_count += 1
    check(
        "Pixel ID replaced (not placeholder)",
        placeholder_count == 0,
        f"{placeholder_count} files still have YOUR_PIXEL_ID placeholder" if placeholder_count else "All pixel IDs set",
        "Replace YOUR_PIXEL_ID with your actual Pixel ID from Meta Events Manager → Data Sources → Web → Pixel ID"
    )

    # 2. Check Lead event on thank-you page
    print("\n2. LEAD EVENT TRACKING")
    thankyou = WEBSITE_DIR / "thank-you.html"
    if thankyou.exists():
        content = thankyou.read_text(errors='ignore')
        check(
            "Lead event on thank-you.html",
            "fbq('track', 'Lead')" in content,
            fix="Add <script>fbq('track', 'Lead');</script> before </body> in thank-you.html"
        )
    else:
        check("thank-you.html exists", False, fix="Create website/thank-you.html")

    # 3. Check demo.html exists
    print("\n3. KEY PAGES")
    demo = WEBSITE_DIR / "demo.html"
    check("demo.html exists", demo.exists(), fix="Create website/demo.html")

    book = WEBSITE_DIR / "book.html"
    check("book.html exists", book.exists(), fix="Create website/book.html")

    privacy = WEBSITE_DIR / "privacy.html"
    check("privacy.html exists", privacy.exists(), fix="Required for Lead Form privacy policy link")

    # 4. Check ad copy exists
    print("\n4. AD COPY")
    ad_copy = REPO_ROOT / "docs" / "fb-ads-final-copy.md"
    check("fb-ads-final-copy.md exists", ad_copy.exists(), fix="Create docs/fb-ads-final-copy.md")

    if ad_copy.exists():
        copy_content = ad_copy.read_text()
        banned = []
        # Check for banned words (case-insensitive, whole word)
        for word in [" AI ", "guaranteed", "never miss"]:
            # Only check in the ad copy sections, not compliance notes
            sections = copy_content.split("## Compliance Notes")[0] if "## Compliance Notes" in copy_content else copy_content
            if re.search(re.escape(word), sections, re.IGNORECASE):
                banned.append(word.strip())
        check(
            "No banned phrases in ad copy",
            len(banned) == 0,
            f"Found: {banned}" if banned else "Clean",
            "Remove or replace banned phrases per Meta Ads policy"
        )

    # 5. Check setup guide exists
    print("\n5. SETUP DOCS")
    setup_guide = REPO_ROOT / "docs" / "fb-ads-manager-setup.md"
    check("fb-ads-manager-setup.md exists", setup_guide.exists())

    # 6. Check inject script exists
    print("\n6. SCRIPTS")
    inject = REPO_ROOT / "ops" / "inject-meta-pixel.py"
    check("inject-meta-pixel.py exists", inject.exists())

    # Summary
    print("\n" + "=" * 50)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"RESULTS: {passed} PASS / {failed} FAIL / {len(results)} total")

    if failed == 0:
        print("\nALL CHECKS PASSED — Ready to launch!")
    else:
        print(f"\n{failed} ISSUE(S) NEED FIXING before launch.")

    # Write report
    write_report(passed, failed)


def write_report(passed, failed):
    lines = []
    lines.append("# FB Lead Ads Launch Verification Report")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"## Summary: {passed} PASS / {failed} FAIL")
    lines.append("")

    if failed > 0:
        lines.append("## Failures (Fix These First)")
        lines.append("")
        for r in results:
            if r["status"] == "FAIL":
                lines.append(f"### FAIL: {r['name']}")
                if r["detail"]:
                    lines.append(f"- Detail: {r['detail']}")
                if r["fix"]:
                    lines.append(f"- **Fix:** {r['fix']}")
                lines.append("")

    lines.append("## All Checks")
    lines.append("")
    for r in results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        lines.append(f"- **[{icon}]** {r['name']}" + (f" — {r['detail']}" if r['detail'] else ""))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"\nReport: {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
