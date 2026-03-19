#!/usr/bin/env python3
"""
THE CALL TAKER — Visual QA Bot
Runs before every push. Catches broken pages before they go live.
Usage: python3 scripts/visual-qa.py [--fix]
"""
import os, glob, re, sys

base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
html_files = glob.glob(os.path.join(base, '**/*.html'), recursive=True)
html_files = [f for f in html_files if '.git' not in f and 'node_modules' not in f]

auto_fix = '--fix' in sys.argv

errors = []
warnings = []
fixed = 0

SKIP_FILES = ['googlec25aafc228a65930.html']

for filepath in sorted(html_files):
    rel = filepath.replace(base + '/', '')

    if any(skip in rel for skip in SKIP_FILES):
        continue

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        continue

    if len(content) < 100:
        continue

    original = content

    # 1. Missing viewport meta — CRITICAL (page will not scale on mobile)
    if '<meta name="viewport"' not in content:
        errors.append(f'CRITICAL [{rel}]: missing viewport meta tag')

    # 2. Missing mobile overflow guard
    has_guard = (
        'mobile-guard.css' in content or
        'overflow-x: hidden' in content or
        'overflow-x:hidden' in content
    )
    if not has_guard:
        warnings.append(f'WARN [{rel}]: no mobile overflow guard (add mobile-guard.css)')
        if auto_fix and '</head>' in content:
            inject = '    <link rel="stylesheet" href="/shared/mobile-guard.css">\n'
            content = content.replace('</head>', inject + '</head>', 1)

    # 3. Missing container / max-width (content will stretch full viewport)
    if 'container' not in content and 'max-width' not in content:
        warnings.append(f'WARN [{rel}]: no container or max-width — content may stretch')

    # 4. Placeholder text left in (skip TODO/FIXME in code comments)
    critical_placeholders = ['YOUR_WEBHOOK_ID', 'YOUR_PIXEL_ID', 'lorem ipsum']
    code_placeholders = ['TODO', 'FIXME']
    for ph in critical_placeholders:
        if ph.lower() in content.lower():
            errors.append(f'ERROR [{rel}]: contains placeholder "{ph}"')
    # Strip script/style blocks before checking TODO/FIXME (they're fine in comments)
    html_only = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL|re.IGNORECASE)
    html_only = re.sub(r'<style[^>]*>.*?</style>', '', html_only, flags=re.DOTALL|re.IGNORECASE)
    html_only = re.sub(r'<!--.*?-->', '', html_only, flags=re.DOTALL)
    for ph in code_placeholders:
        if ph in html_only:
            errors.append(f'ERROR [{rel}]: contains "{ph}" in visible HTML')

    # 5. Broken internal links (href to files that don't exist)
    for match in re.finditer(r'href="(/[^"#?]+\.html)"', content):
        linked = match.group(1)
        linked_path = os.path.join(base, linked.lstrip('/'))
        if not os.path.exists(linked_path):
            warnings.append(f'WARN [{rel}]: broken link to {linked}')

    # 6. Images without alt text
    for match in re.finditer(r'<img\s[^>]*>', content):
        tag = match.group(0)
        if 'alt=' not in tag:
            warnings.append(f'WARN [{rel}]: img without alt text')
            break  # One warning per file is enough

    # Write fixes
    if auto_fix and content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed += 1

# Report
print(f'\n{"="*50}')
print(f'  VISUAL QA — {len(html_files)} pages scanned')
print(f'{"="*50}')
print(f'  Errors:   {len(errors)}')
print(f'  Warnings: {len(warnings)}')
if auto_fix:
    print(f'  Fixed:    {fixed}')
print()

if errors:
    print('=== ERRORS (must fix before pushing) ===')
    for e in errors:
        print(f'  {e}')
    print()

if warnings:
    print('=== WARNINGS ===')
    # Show up to 30, group by type
    shown = 0
    for w in warnings:
        if shown >= 40:
            remaining = len(warnings) - shown
            print(f'  ... and {remaining} more warnings')
            break
        print(f'  {w}')
        shown += 1

print()
if errors:
    print('FAIL — fix errors before pushing')
    sys.exit(1)
else:
    print('PASS — no critical issues')
    sys.exit(0)
