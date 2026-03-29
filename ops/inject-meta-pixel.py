#!/usr/bin/env python3
"""
Meta Pixel Injector — The Call Taker
Adds Meta Pixel code to <head> of every HTML file in website/.
Also adds fbq('track', 'Lead') to thank-you/confirmation pages.
Usage: python3 ops/inject-meta-pixel.py [--dry-run]
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = REPO_ROOT / "website"
DRY_RUN = "--dry-run" in sys.argv

PIXEL_CODE = """<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '2129562004253413');
fbq('track', 'PageView');
</script>
<noscript>
<img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=2129562004253413&ev=PageView&noscript=1"/>
</noscript>
<!-- End Meta Pixel Code -->"""

LEAD_EVENT = "\n<script>fbq('track', 'Lead');</script>"

# Pages that should fire Lead event
LEAD_PAGES = ["thank-you.html", "thank-you-demo.html"]


def inject_pixel(filepath):
    html = filepath.read_text(errors='ignore')

    # Skip if pixel already present
    if 'fbevents.js' in html:
        return "SKIP_EXISTS"

    # Skip non-HTML files that might have .html extension but are empty/broken
    if '</head>' not in html:
        return "SKIP_NO_HEAD"

    # Inject pixel before </head>
    html = html.replace('</head>', PIXEL_CODE + '\n</head>', 1)

    # Add Lead event to thank-you pages
    if filepath.name in LEAD_PAGES and "fbq('track', 'Lead')" not in html:
        # Add before </body>
        if '</body>' in html:
            html = html.replace('</body>', LEAD_EVENT + '\n</body>', 1)

    if not DRY_RUN:
        filepath.write_text(html)
    return "UPDATED"


def run():
    html_files = sorted(WEBSITE_DIR.rglob("*.html"))
    updated = 0
    skipped_exists = 0
    skipped_no_head = 0
    errors = 0

    for f in html_files:
        # Skip dashboard and non-deployed files
        rel = f.relative_to(REPO_ROOT)
        if 'dashboard/' in str(rel) or 'reports/' in str(rel):
            continue

        try:
            result = inject_pixel(f)
            if result == "UPDATED":
                print(f"  UPDATED: {rel}")
                updated += 1
            elif result == "SKIP_EXISTS":
                skipped_exists += 1
            elif result == "SKIP_NO_HEAD":
                skipped_no_head += 1
        except Exception as e:
            print(f"  ERROR: {rel} — {e}")
            errors += 1

    print(f"\nDone.")
    print(f"  Updated: {updated}")
    print(f"  Already had pixel: {skipped_exists}")
    print(f"  No <head> tag: {skipped_no_head}")
    print(f"  Errors: {errors}")
    print(f"  Total HTML files: {len(html_files)}")
    if DRY_RUN:
        print("(Dry run — no files modified)")


if __name__ == "__main__":
    print("Meta Pixel Injector — The Call Taker")
    print("=" * 50)
    if DRY_RUN:
        print("MODE: Dry run")
    print()
    run()
