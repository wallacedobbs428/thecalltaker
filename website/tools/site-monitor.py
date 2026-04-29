#!/usr/bin/env python3
"""
Site Health Monitor — The Call Taker
Scans local website files for broken links, missing assets, stale references,
theme issues, and form placeholders. Sends ntfy alert on failures.

Usage:
    python3 site-monitor.py          # run all checks (default)
    python3 site-monitor.py check    # run all checks
    python3 site-monitor.py status   # show last run results from log
"""

import os
import sys
import re
import json
import datetime
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/thecalltaker-ops/ops"))
from trusted_ntfy import post_trusted_ntfy

# ── Paths ────────────────────────────────────────────────────────────────────
WEBSITE_ROOT = Path(__file__).resolve().parent.parent  # website/
TOOLS_DIR = WEBSITE_ROOT / "tools"
LOG_FILE = TOOLS_DIR / "site-monitor.log"
DEMO_CONSOLE_JS = WEBSITE_ROOT / "shared" / "demo-console.js"
DEMO_SHOWCASE = WEBSITE_ROOT / "demo-showcase.html"

NTFY_TOPIC = "tct-system-vRsfXQRQ"

# ── Terminal colors ──────────────────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty()

def green(s):  return f"\033[32m{s}\033[0m" if USE_COLOR else s
def red(s):    return f"\033[31m{s}\033[0m" if USE_COLOR else s
def yellow(s): return f"\033[33m{s}\033[0m" if USE_COLOR else s
def bold(s):   return f"\033[1m{s}\033[0m" if USE_COLOR else s
def dim(s):    return f"\033[2m{s}\033[0m" if USE_COLOR else s

PASS_MARK = green("PASS")
FAIL_MARK = red("FAIL")
WARN_MARK = yellow("WARN")

# ── Result tracking ──────────────────────────────────────────────────────────
passes = []
failures = []
warnings = []

def log_pass(category, detail):
    passes.append((category, detail))

def log_fail(category, detail):
    failures.append((category, detail))

def log_warn(category, detail):
    warnings.append((category, detail))


# ═══════════════════════════════════════════════════════════════════════════════
#  CHECK 1: AUDIO / MEDIA
# ═══════════════════════════════════════════════════════════════════════════════

def check_audio_media():
    print(bold("\n=== AUDIO / MEDIA CHECKS ==="))
    MIN_SIZE = 10 * 1024  # 10KB

    # 1a. Parse demo-console.js for audio references
    audio_paths = set()
    if DEMO_CONSOLE_JS.exists():
        content = DEMO_CONSOLE_JS.read_text(errors="replace")
        # Default audio path
        for m in re.finditer(r"""['"](/[^'"]+\.(?:mp3|mp4|wav|ogg|webm))['"]""", content):
            audio_paths.add(m.group(1))
        # data-audio attributes might reference custom paths; check HTML files too
    else:
        log_fail("AUDIO", f"demo-console.js not found at {DEMO_CONSOLE_JS}")
        print(f"  {FAIL_MARK} demo-console.js missing")
        return

    # 1b. Scan all HTML for data-audio attributes
    for html_file in WEBSITE_ROOT.rglob("*.html"):
        text = html_file.read_text(errors="replace")
        for m in re.finditer(r'data-audio\s*=\s*["\']([^"\']+)["\']', text):
            audio_paths.add(m.group(1))

    # 1c. Scan demo-showcase.html for audio/video src references
    if DEMO_SHOWCASE.exists():
        text = DEMO_SHOWCASE.read_text(errors="replace")
        for m in re.finditer(r'(?:src|href)\s*=\s*["\']([^"\']+\.(?:mp3|mp4|wav|ogg|webm|avi|mov))["\']', text):
            path = m.group(1)
            if not path.startswith("http"):
                audio_paths.add(path)
        log_pass("AUDIO", "demo-showcase.html scanned for media references")
    else:
        log_fail("AUDIO", "demo-showcase.html not found")
        print(f"  {FAIL_MARK} demo-showcase.html not found")

    if not audio_paths:
        log_warn("AUDIO", "No audio file references found in demo-console.js or HTML")
        print(f"  {WARN_MARK} No audio file references found")
        return

    for audio_path in sorted(audio_paths):
        # Resolve to disk path
        if audio_path.startswith("/"):
            disk_path = WEBSITE_ROOT / audio_path.lstrip("/")
        else:
            disk_path = WEBSITE_ROOT / audio_path

        if not disk_path.exists():
            log_fail("AUDIO", f"Missing audio file: {audio_path}")
            print(f"  {FAIL_MARK} Missing: {audio_path}")
        elif disk_path.stat().st_size < MIN_SIZE:
            size_kb = disk_path.stat().st_size / 1024
            log_fail("AUDIO", f"Audio file too small ({size_kb:.1f}KB < 10KB): {audio_path}")
            print(f"  {FAIL_MARK} Too small ({size_kb:.1f}KB): {audio_path}")
        else:
            size_kb = disk_path.stat().st_size / 1024
            log_pass("AUDIO", f"OK ({size_kb:.1f}KB): {audio_path}")
            print(f"  {PASS_MARK} {audio_path} ({size_kb:.1f}KB)")


# ═══════════════════════════════════════════════════════════════════════════════
#  CHECK 2: INTERNAL LINKS
# ═══════════════════════════════════════════════════════════════════════════════

def check_internal_links():
    print(bold("\n=== INTERNAL LINK CHECKS ==="))

    # 2a. Critical pages that MUST exist
    critical_pages = [
        "index.html",
        "book.html",
        "pricing.html",
        "calculator.html",
        "signup.html",
        "checkout.html",
        "pilot/index.html",
        "demo-showcase.html",
    ]

    print(dim("  -- Critical pages --"))
    for page in critical_pages:
        disk_path = WEBSITE_ROOT / page
        if disk_path.exists():
            log_pass("LINKS-CRITICAL", f"Critical page exists: {page}")
            print(f"  {PASS_MARK} {page}")
        else:
            log_fail("LINKS-CRITICAL", f"Critical page MISSING: {page}")
            print(f"  {FAIL_MARK} MISSING critical page: {page}")

    # 2b. Scan all HTML for internal href links
    print(dim("  -- Internal link scan --"))
    broken = {}
    checked = set()
    total_links = 0

    # Patterns to skip
    skip_prefixes = ("http://", "https://", "mailto:", "tel:", "sms:", "javascript:", "#", "data:")

    for html_file in sorted(WEBSITE_ROOT.rglob("*.html")):
        rel = html_file.relative_to(WEBSITE_ROOT)
        text = html_file.read_text(errors="replace")

        for m in re.finditer(r'href\s*=\s*["\']([^"\'#\s][^"\']*)["\']', text):
            href = m.group(1).split("#")[0].split("?")[0].strip()
            if not href or any(href.startswith(p) for p in skip_prefixes):
                continue

            total_links += 1

            # Resolve the target path
            if href.startswith("/"):
                target = WEBSITE_ROOT / href.lstrip("/")
            else:
                target = html_file.parent / href

            # Normalize: if it points to a directory, check for index.html
            if not target.suffix:
                target_dir = target if str(target).endswith("/") else target
                target_index = target_dir / "index.html"
                # Accept either the dir existing with index.html, or the exact path
                if target_index.exists():
                    continue
                # Also check if target itself exists as a file
                if target.exists() and target.is_file():
                    continue
                # Try with trailing slash removed
                if not target.exists():
                    cache_key = str(target)
                    if cache_key not in checked:
                        checked.add(cache_key)
                        broken.setdefault(href, []).append(str(rel))
                    continue

            if target.exists():
                continue

            cache_key = str(target)
            if cache_key not in checked:
                checked.add(cache_key)
                broken.setdefault(href, []).append(str(rel))

    if broken:
        for href, sources in sorted(broken.items()):
            source_list = ", ".join(sources[:3])
            extra = f" (+{len(sources)-3} more)" if len(sources) > 3 else ""
            log_fail("LINKS", f"Broken link: {href} (from {source_list}{extra})")
            print(f"  {FAIL_MARK} {href} <- {source_list}{extra}")
    else:
        log_pass("LINKS", f"All {total_links} internal links valid")
        print(f"  {PASS_MARK} All {total_links} internal links valid")


# ═══════════════════════════════════════════════════════════════════════════════
#  CHECK 3: FORM / WEBHOOK PLACEHOLDERS
# ═══════════════════════════════════════════════════════════════════════════════

def check_forms():
    print(bold("\n=== FORM / WEBHOOK CHECKS ==="))
    industries_dir = WEBSITE_ROOT / "industries"
    placeholder_patterns = [
        r"YOUR_WEBHOOK_ID",
        r"YOUR_WEBHOOK",
        r"REPLACE_ME",
        r"TODO",
        r"FIXME",
        r"example\.com/webhook",
        r"placeholder",
    ]
    combined_re = re.compile("|".join(placeholder_patterns), re.IGNORECASE)

    if not industries_dir.exists():
        log_fail("FORMS", "industries/ directory not found")
        print(f"  {FAIL_MARK} industries/ directory not found")
        return

    found_issues = False
    for html_file in sorted(industries_dir.glob("*.html")):
        text = html_file.read_text(errors="replace")
        matches = combined_re.findall(text)
        if matches:
            found_issues = True
            unique = set(m.upper() for m in matches)
            log_fail("FORMS", f"Placeholder text in {html_file.name}: {', '.join(unique)}")
            print(f"  {FAIL_MARK} {html_file.name}: contains {', '.join(unique)}")

    if not found_issues:
        count = len(list(industries_dir.glob("*.html")))
        log_pass("FORMS", f"All {count} industry pages clean of placeholders")
        print(f"  {PASS_MARK} All {count} industry pages clean of placeholders")


# ═══════════════════════════════════════════════════════════════════════════════
#  CHECK 4: JAVASCRIPT FILES
# ═══════════════════════════════════════════════════════════════════════════════

def check_javascript():
    print(bold("\n=== JAVASCRIPT CHECKS ==="))

    # 4a. Required JS/CSS files must exist and be non-empty
    required_files = [
        "shared/ui-dark.js",
        "shared/ui-dark.css",
        "shared/demo-console.js",
        "tct-tracking.js",
    ]

    for rel_path in required_files:
        disk_path = WEBSITE_ROOT / rel_path
        if not disk_path.exists():
            log_fail("JS", f"Required file missing: {rel_path}")
            print(f"  {FAIL_MARK} Missing: {rel_path}")
        elif disk_path.stat().st_size == 0:
            log_fail("JS", f"Required file is empty: {rel_path}")
            print(f"  {FAIL_MARK} Empty: {rel_path}")
        else:
            size_kb = disk_path.stat().st_size / 1024
            log_pass("JS", f"OK ({size_kb:.1f}KB): {rel_path}")
            print(f"  {PASS_MARK} {rel_path} ({size_kb:.1f}KB)")

    # 4b. Scan for outdated ui.css references (should be ui-dark.css)
    print(dim("  -- Outdated ui.css references --"))
    # Match references to ui.css but NOT ui-dark.css
    outdated_re = re.compile(r'''(?:href|src)\s*=\s*['"]([^'"]*(?<![a-z-])ui\.css[^'"]*)['"]\s''', re.IGNORECASE)

    outdated_found = False
    for html_file in sorted(WEBSITE_ROOT.rglob("*.html")):
        text = html_file.read_text(errors="replace")
        # More precise: find ui.css but not ui-dark.css
        for m in re.finditer(r'''(?:href|src)\s*=\s*['"](/shared/ui\.css|shared/ui\.css|\.\.?/shared/ui\.css)['"]''', text):
            rel = html_file.relative_to(WEBSITE_ROOT)
            log_fail("JS", f"Outdated ui.css reference in {rel}: {m.group(1)}")
            print(f"  {FAIL_MARK} Outdated ui.css in {rel}")
            outdated_found = True

    if not outdated_found:
        log_pass("JS", "No outdated ui.css references found")
        print(f"  {PASS_MARK} No outdated ui.css references")


# ═══════════════════════════════════════════════════════════════════════════════
#  CHECK 5: VISUAL / THEME
# ═══════════════════════════════════════════════════════════════════════════════

def check_theme():
    print(bold("\n=== VISUAL / THEME CHECKS ==="))

    # 5a. Check for hardcoded light-theme colors in inline styles
    light_patterns = [
        (re.compile(r'(?:background|background-color)\s*:\s*#fff(?:fff)?\s*[;"\'}\s]', re.IGNORECASE),
         "background: #ffffff"),
        (re.compile(r'(?:background|background-color)\s*:\s*white\s*[;"\'}\s]', re.IGNORECASE),
         "background: white"),
    ]

    print(dim("  -- Light-theme color scan --"))
    light_issues = []
    for html_file in sorted(WEBSITE_ROOT.rglob("*.html")):
        rel = html_file.relative_to(WEBSITE_ROOT)
        text = html_file.read_text(errors="replace")

        # Only scan inline styles and <style> blocks, not regular text content
        # Extract style attributes and style blocks
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', text, re.DOTALL | re.IGNORECASE)
        style_attrs = re.findall(r'style\s*=\s*["\']([^"\']*)["\']', text, re.IGNORECASE)
        scannable = " ".join(style_blocks + style_attrs)

        for pattern, desc in light_patterns:
            if pattern.search(scannable):
                light_issues.append((str(rel), desc))

    if light_issues:
        for filepath, desc in light_issues[:10]:
            log_warn("THEME", f"Light-theme color ({desc}) in {filepath}")
            print(f"  {WARN_MARK} {desc} in {filepath}")
        if len(light_issues) > 10:
            print(f"  {WARN_MARK} ...and {len(light_issues)-10} more")
    else:
        log_pass("THEME", "No hardcoded light-theme background colors found")
        print(f"  {PASS_MARK} No hardcoded light-theme backgrounds")

    # 5b. Verify dark theme-color meta tag
    print(dim("  -- theme-color meta tag --"))
    dark_colors = {"#0a0a0a", "#000000", "#000", "#0f0f0f", "#111111", "#111", "#0d0d0d"}
    missing_theme = []
    has_light_theme = []

    for html_file in sorted(WEBSITE_ROOT.rglob("*.html")):
        rel = html_file.relative_to(WEBSITE_ROOT)
        text = html_file.read_text(errors="replace")

        # Skip non-page HTML (partials, snippets)
        if "<html" not in text.lower() and "<!doctype" not in text.lower():
            continue

        theme_match = re.search(
            r'<meta\s+name\s*=\s*["\']theme-color["\']\s+content\s*=\s*["\']([^"\']+)["\']',
            text, re.IGNORECASE
        )

        if not theme_match:
            missing_theme.append(str(rel))
        else:
            color = theme_match.group(1).strip().lower()
            if color not in dark_colors:
                has_light_theme.append((str(rel), color))

    if missing_theme:
        # Only report first few to avoid noise
        shown = missing_theme[:5]
        for f in shown:
            log_warn("THEME", f"Missing theme-color meta: {f}")
            print(f"  {WARN_MARK} Missing theme-color: {f}")
        if len(missing_theme) > 5:
            count = len(missing_theme) - 5
            print(f"  {WARN_MARK} ...and {count} more files missing theme-color")
            log_warn("THEME", f"{count} more files missing theme-color meta")
    else:
        log_pass("THEME", "All pages have theme-color meta tag")
        print(f"  {PASS_MARK} All pages have theme-color meta")

    if has_light_theme:
        for f, color in has_light_theme:
            log_fail("THEME", f"Light theme-color ({color}) in {f}")
            print(f"  {FAIL_MARK} Light theme-color ({color}) in {f}")
    else:
        if not missing_theme:
            log_pass("THEME", "All theme-color values are dark")
            print(f"  {PASS_MARK} All theme-color values are dark")


# ═══════════════════════════════════════════════════════════════════════════════
#  NTFY ALERT
# ═══════════════════════════════════════════════════════════════════════════════

def send_ntfy_alert(failure_list):
    """Send ntfy alert with failure summary. Only called when there are failures."""
    body_lines = []
    for cat, detail in failure_list[:15]:
        body_lines.append(f"[{cat}] {detail}")
    if len(failure_list) > 15:
        body_lines.append(f"...and {len(failure_list)-15} more failures")

    body = "\n".join(body_lines)
    title = "[SITE-MONITOR] Issues Found"

    try:
        post_trusted_ntfy(
            NTFY_TOPIC,
            title,
            body,
            priority="default",
            tags="warning",
            workflow_key="ntfy:site-monitor",
            evidence={"source": "website/tools/site-monitor.py", "trusted_alert_rule": "ctos_ledger_before_phone_push"},
        )
        print(f"\n  {green('ntfy alert sent')} to {NTFY_TOPIC}")
    except Exception as e:
        print(f"\n  {yellow('ntfy alert failed')}: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  LOG WRITER
# ═══════════════════════════════════════════════════════════════════════════════

def write_log():
    """Append run results to the log file."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"\n{'='*60}", f"Site Monitor Run — {ts}", f"{'='*60}"]

    if failures:
        lines.append(f"\nFAILURES ({len(failures)}):")
        for cat, detail in failures:
            lines.append(f"  FAIL [{cat}] {detail}")

    if warnings:
        lines.append(f"\nWARNINGS ({len(warnings)}):")
        for cat, detail in warnings:
            lines.append(f"  WARN [{cat}] {detail}")

    lines.append(f"\nPASSED ({len(passes)}):")
    for cat, detail in passes:
        lines.append(f"  PASS [{cat}] {detail}")

    lines.append(f"\nSUMMARY: {len(passes)} passed, {len(failures)} failed, {len(warnings)} warnings")
    lines.append("")

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write("\n".join(lines) + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
#  STATUS COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

def show_status():
    """Show the last run results from the log file."""
    if not LOG_FILE.exists():
        print("No log file found. Run 'check' first.")
        sys.exit(0)

    text = LOG_FILE.read_text()
    # Find the last run block
    blocks = text.split("=" * 60)
    if len(blocks) < 3:
        print("No completed runs found in log.")
        sys.exit(0)

    # Last run is the last 3 segments (separator, header+body, separator)
    last_run = ("=" * 60).join(blocks[-3:])
    print(last_run.strip())


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run_checks():
    print(bold("Site Health Monitor — The Call Taker"))
    print(dim(f"Website root: {WEBSITE_ROOT}"))
    print(dim(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))

    check_audio_media()
    check_internal_links()
    check_forms()
    check_javascript()
    check_theme()

    # Summary
    total = len(passes) + len(failures)
    print(bold(f"\n{'='*50}"))
    print(bold("SUMMARY"))
    print(f"  {green(f'{len(passes)} passed')}, {red(f'{len(failures)} failed')}, {yellow(f'{len(warnings)} warnings')}")
    print(f"  Total checks: {total}")

    # Write log
    write_log()
    print(dim(f"  Log: {LOG_FILE}"))

    # Send ntfy if failures
    if failures:
        send_ntfy_alert(failures)
        print(f"\n{red('Site health check FAILED.')}")
        sys.exit(1)
    else:
        print(f"\n{green('All checks passed.')}")
        sys.exit(0)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        run_checks()
    elif cmd == "status":
        show_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: site-monitor.py [check|status]")
        sys.exit(1)


if __name__ == "__main__":
    main()
