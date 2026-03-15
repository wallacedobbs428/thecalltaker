#!/usr/bin/env python3
"""Fix all industry and blog pages to match homepage design system.

Transforms:
1. Adds favicon, Inter font, styles.css import
2. Fixes Google Ads tag (replaces placeholder)
3. Replaces blue/red inline CSS colors with green design system
4. Replaces old header with proper header-inner structure
5. Replaces old footer with proper footer-inner structure
6. Adds mobile-nav, sticky-mobile-bar, script.js, tct-tracking.js
"""

import os
import re
import glob

WEBSITE = os.path.expanduser("~/Desktop/wallace-hvac/website/website")

# ═══════════════════════════════════════════════════════
# SHARED HTML COMPONENTS
# ═══════════════════════════════════════════════════════

PHONE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.82.36 1.63.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c1.18.34 1.99.58 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'

GTAG = '<script async src="https://www.googletagmanager.com/gtag/js?id=AW-17970510102"></script>\n<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag(\'js\',new Date());gtag(\'config\',\'AW-17970510102\');</script>'

def make_head_imports(prefix="../"):
    return f'''<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}styles.css">'''

def make_header(prefix="../"):
    return f'''<header class="header">
  <div class="header-inner">
    <a href="{prefix}index.html" class="logo">
      <div class="logo-icon">{PHONE_SVG}</div>
      The Call <span>Taker</span>
    </a>
    <nav class="nav">
      <a href="{prefix}index.html">Home</a>
      <a href="{prefix}services.html">Services</a>
      <a href="{prefix}index.html#pricing">Pricing</a>
      <a href="{prefix}book.html">Demo</a>
    </nav>
    <a href="{prefix}book.html" class="header-cta">Book a Demo</a>
    <button class="menu-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
  </div>
</header>

<nav class="mobile-nav">
  <a href="{prefix}index.html">Home</a>
  <a href="{prefix}services.html">Services</a>
  <a href="{prefix}index.html#pricing">Pricing</a>
  <a href="{prefix}book.html">Demo</a>
  <a href="{prefix}book.html" class="btn btn-primary btn-lg">Book a Demo</a>
</nav>'''

def make_footer(prefix="../"):
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{prefix}index.html" class="logo">
          <div class="logo-icon">{PHONE_SVG}</div>
          The Call <span>Taker</span>
        </a>
        <p>AI receptionist for service businesses.</p>
      </div>
      <div class="footer-links">
        <a href="{prefix}index.html">Home</a>
        <a href="{prefix}services.html">Services</a>
        <a href="{prefix}book.html">Demo</a>
        <a href="{prefix}calculator.html">Calculator</a>
        <a href="{prefix}privacy.html">Privacy Policy</a>
        <a href="{prefix}terms.html">Terms of Service</a>
        <a href="mailto:wallacemdobbs@icloud.com">Contact</a>
        <a href="https://www.instagram.com/thecalltaker" target="_blank" rel="noopener noreferrer">Instagram</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 The Call Taker. All rights reserved.</span>
      <span>The Call Taker &middot; Brentwood, TN &middot; <a href="mailto:wallacemdobbs@icloud.com" style="color:var(--text-3);">wallacemdobbs@icloud.com</a></span>
    </div>
  </div>
</footer>

<div class="sticky-mobile-bar">
  <a href="tel:+16157845747"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.82.36 1.63.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c1.18.34 1.99.58 2.81.7A2 2 0 0 1 22 16.92z"/></svg>Hear AI Live</a>
  <a href="{prefix}book.html" style="border-left:1px solid var(--border);"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>Book Demo</a>
</div>

<script src="{prefix}script.js"></script>
<script src="{prefix}tct-tracking.js"></script>'''


# ═══════════════════════════════════════════════════════
# CSS COLOR TRANSFORMATION
# ═══════════════════════════════════════════════════════

def fix_css_colors(css):
    """Replace blue/red color scheme with green design system colors."""

    # Order matters — do var() replacements before hex replacements
    replacements = [
        # var() references → design system equivalents
        ('var(--bg-dark)', '#000'),
        ('var(--bg-darker)', '#000'),
        ('var(--bg-card)', 'var(--surface)'),
        ('var(--primary-blue-light)', 'var(--green)'),
        ('var(--primary-blue-dark)', '#00b86e'),
        ('var(--primary-blue)', 'var(--green)'),
        ('var(--red-accent)', '#ef4444'),
        ('var(--gold)', '#f5a623'),
        ('var(--text-primary)', 'var(--text-1)'),
        ('var(--text-secondary)', 'var(--text-2)'),
        ('var(--text-muted)', 'var(--text-3)'),
        ('var(--glow)', 'var(--green-glow)'),
        ('var(--shadow)', '0 8px 32px rgba(0,0,0,.3)'),

        # Hex color replacements
        ('#1a1a2e', '#000'),
        ('#0f0f23', '#000'),
        ('#16213e', 'rgba(0,220,130,0.05)'),
        ('#1a1a3e', 'rgba(0,220,130,0.03)'),
        ('#0f3460', 'rgba(0,220,130,0.08)'),
        ('#4361ee', 'var(--green)'),
        ('#3451d1', '#00b86e'),
        ('#3a56d4', '#00b86e'),
        ('#6b83f2', 'var(--green)'),
        ('#27ae60', 'var(--green)'),
        ('#219a52', '#00b86e'),

        # rgba color replacements
        ('rgba(67,97,238,', 'rgba(0,220,130,'),
        ('rgba(39,174,96,', 'rgba(0,220,130,'),

        # Font family
        ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif",
         "'Inter',-apple-system,BlinkMacSystemFont,sans-serif"),
        ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif",
         "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"),
        ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
         "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"),
    ]

    for old, new in replacements:
        css = css.replace(old, new)

    # Remove :root block (styles.css provides the variables)
    css = re.sub(r':root\s*\{[^}]+\}', '', css)

    # Remove global reset (styles.css provides it)
    css = re.sub(r'\*\s*\{[^}]*margin\s*:\s*0[^}]*box-sizing\s*:\s*border-box[^}]*\}', '', css)
    css = re.sub(r'\*,\s*\*::before,\s*\*::after\s*\{[^}]*box-sizing[^}]*\}', '', css)

    # Remove body rule (styles.css provides it) - but keep it simple
    css = re.sub(r'body\s*\{[^}]+\}', '', css)

    # Remove generic link rule (styles.css provides it)
    css = re.sub(r'(?<!\.)a\s*\{[^}]+\}\s*a:hover\s*\{[^}]+\}', '', css)

    # Fix hero gradient specifically
    css = css.replace(
        'linear-gradient(135deg,#000 0%,rgba(0,220,130,0.08) 50%,var(--green) 100%)',
        'linear-gradient(135deg,#000 0%,rgba(0,220,130,0.08) 100%)'
    )

    # Clean up multiple blank lines
    css = re.sub(r'\n\s*\n\s*\n', '\n\n', css)

    return css.strip()


# ═══════════════════════════════════════════════════════
# FILE PROCESSING
# ═══════════════════════════════════════════════════════

def process_industry_page(filepath):
    """Fix an industry page to match homepage design."""
    with open(filepath, 'r') as f:
        html = f.read()

    # 1. Fix tracking tags
    # Replace placeholder Google tag
    html = re.sub(
        r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-XXXXXXXXXX"></script>\s*<script src="/tct-tracking\.js"></script>',
        '',  # Remove — we'll add proper ones at bottom
        html
    )
    html = re.sub(
        r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-XXXXXXXXXX"></script>',
        '',
        html
    )
    html = re.sub(r'<script src="/tct-tracking\.js"></script>', '', html)

    # 2. Add proper head imports (before <style>)
    if 'styles.css' not in html:
        # Add favicon, Inter font, styles.css before <style>
        gtag_and_imports = GTAG + '\n' + make_head_imports("../")
        html = html.replace('<style>', gtag_and_imports + '\n<style>', 1)

    # 3. Fix inline CSS colors
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if style_match:
        old_css = style_match.group(1)
        new_css = fix_css_colors(old_css)
        html = html.replace(f'<style>{old_css}</style>', f'<style>\n{new_css}\n</style>')

    # 4. Replace old header — industry pages have no header, content starts with .hero div
    # Insert proper header + mobile-nav after <body>
    header_html = make_header("../")
    html = re.sub(
        r'<body>\s*\n*',
        f'<body>\n\n{header_html}\n\n',
        html,
        count=1
    )

    # 5. Replace old footer
    footer_html = make_footer("../")
    # Industry pages have: <div class="footer">...</div> then <script>...</script></body>
    html = re.sub(
        r'<div class="footer">.*?</div>\s*(<script>.*?</script>\s*)?</body>',
        f'{footer_html}\n</body>',
        html,
        flags=re.DOTALL
    )

    # 6. Add padding-top to hero for fixed header
    if '.ind-hero' not in html and 'padding-top:' not in html.split('.hero')[1][:200] if '.hero' in html else True:
        # Add extra padding to hero to account for fixed header
        html = html.replace(
            '.hero{',
            '.hero{padding-top:120px;',
            1
        )

    with open(filepath, 'w') as f:
        f.write(html)

    return True


def process_blog_page(filepath):
    """Fix a blog page to match homepage design."""
    with open(filepath, 'r') as f:
        html = f.read()

    # 1. Fix tracking tags
    html = re.sub(
        r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-XXXXXXXXXX"></script>\s*'
        r'(<script>\s*window\.dataLayer.*?</script>\s*)?'
        r'(<script src="/tct-tracking\.js"></script>)?',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(r'<script src="/tct-tracking\.js"></script>', '', html)

    # 2. Add proper head imports
    if 'styles.css' not in html:
        gtag_and_imports = GTAG + '\n' + make_head_imports("../")
        html = html.replace('<style>', gtag_and_imports + '\n<style>', 1)

    # 3. Fix inline CSS colors
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if style_match:
        old_css = style_match.group(1)
        new_css = fix_css_colors(old_css)
        html = html.replace(f'<style>{old_css}</style>', f'<style>\n{new_css}\n</style>')

    # 4. Replace header
    # Blog pages have various header patterns:
    # Pattern A (old): <div class="header">...</div>
    # Pattern B (newer): <header class="header"><div class="header-inner">...</div></header>

    header_html = make_header("../")

    # Remove old header patterns
    # Pattern B: <header class="header">...<div class="header-inner">...</div>...</header>
    html = re.sub(
        r'<header class="header">.*?</header>',
        '',
        html,
        flags=re.DOTALL
    )
    # Pattern A: <div class="header">...</div>
    html = re.sub(
        r'<div class="header">.*?</div>\s*(?=<)',
        '',
        html,
        flags=re.DOTALL,
        count=1
    )

    # Insert proper header after <body>
    html = re.sub(
        r'<body>\s*\n*',
        f'<body>\n\n{header_html}\n\n',
        html,
        count=1
    )

    # 5. Replace footer
    footer_html = make_footer("../")
    # Blog pages have: <div class="footer">...</div></body>
    html = re.sub(
        r'<div class="footer">.*?</div>\s*</body>',
        f'{footer_html}\n</body>',
        html,
        flags=re.DOTALL
    )
    # Also handle <footer class="footer"> pattern
    html = re.sub(
        r'<footer[^>]*>.*?</footer>\s*</body>',
        f'{footer_html}\n</body>',
        html,
        flags=re.DOTALL
    )

    # 6. Remove duplicate script tags if any
    html = re.sub(r'(<script src="../script\.js"></script>\s*){2,}', '<script src="../script.js"></script>\n', html)
    html = re.sub(r'(<script src="../tct-tracking\.js"></script>\s*){2,}', '<script src="../tct-tracking.js"></script>\n', html)

    # 7. Ensure blog header/article have padding for fixed nav
    # Add top padding to first content section
    if '.blog-hero' not in html and '.article-container' in html:
        html = html.replace(
            '.article-container{',
            '.article-container{padding-top:80px;',
            1
        )

    with open(filepath, 'w') as f:
        f.write(html)

    return True


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    # Industry pages
    industry_dir = os.path.join(WEBSITE, "industries")
    industry_files = sorted(glob.glob(os.path.join(industry_dir, "*.html")))

    print(f"=== INDUSTRY PAGES ({len(industry_files)}) ===")
    for f in industry_files:
        name = os.path.basename(f)
        try:
            process_industry_page(f)
            print(f"  [OK] {name}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")

    # Blog pages
    blog_dir = os.path.join(WEBSITE, "blog")
    blog_files = sorted(glob.glob(os.path.join(blog_dir, "*.html")))

    print(f"\n=== BLOG PAGES ({len(blog_files)}) ===")
    for f in blog_files:
        name = os.path.basename(f)
        try:
            process_blog_page(f)
            print(f"  [OK] {name}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")

    print(f"\nDone. Processed {len(industry_files)} industry + {len(blog_files)} blog = {len(industry_files) + len(blog_files)} pages.")


if __name__ == "__main__":
    main()
