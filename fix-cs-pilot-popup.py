#!/usr/bin/env python3
"""
Fix remaining pages that still use the old dark theme:
1. tct-tracking.js popup → warm/light styling
2. Case study pages (6) → warm theme header/footer/colors
3. Pilot page → warm theme header/footer/colors
"""
import os, re, glob

WEBSITE = os.path.expanduser("~/Desktop/wallace-hvac/website/website")

# ── Homepage CSS variables (source of truth) ──
ROOT_VARS = """:root {
  --white: #ffffff;
  --off-white: #f9fafb;
  --light: #f3f4f6;
  --border: #e5e7eb;
  --text: #111827;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --navy: #1e3a5f;
  --navy-dark: #0f2440;
  --blue: #2563eb;
  --blue-light: #eff6ff;
  --orange: #ea580c;
  --orange-hover: #c2410c;
  --orange-light: #fff7ed;
  --green: #059669;
  --green-light: #ecfdf5;
  --star: #f59e0b;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
  --shadow: 0 4px 6px -1px rgba(0,0,0,.07), 0 2px 4px -2px rgba(0,0,0,.05);
  --shadow-lg: 0 10px 25px -3px rgba(0,0,0,.08), 0 4px 6px -4px rgba(0,0,0,.03);
  --shadow-xl: 0 20px 50px -12px rgba(0,0,0,.12);
  --radius: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  /* backwards compat with old var names */
  --text-1: #111827;
  --text-2: #4b5563;
  --text-3: #9ca3af;
  --surface: #f3f4f6;
  --surface-hover: #e5e7eb;
  --green-dim: #ecfdf5;
  --green-glow: rgba(5,150,105,.15);
}"""

# ── Shared CSS for header, footer, nav, body reset ──
SHARED_CSS = """
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--text); background: var(--white); line-height: 1.6; -webkit-font-smoothing: antialiased; font-size: 17px; }
img { max-width: 100%; height: auto; display: block; }
a { color: inherit; text-decoration: none; }
.container, .wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

/* HEADER */
.site-header { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: rgba(255,255,255,.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid transparent; transition: border-color .3s, box-shadow .3s; }
.site-header.scrolled { border-bottom-color: var(--border); box-shadow: var(--shadow-sm); }
.header-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; height: 72px; }
.logo { font-size: 1.25rem; font-weight: 800; color: var(--navy); letter-spacing: -.02em; text-decoration: none; }
.logo span { color: var(--orange); }
.nav-links { display: flex; align-items: center; gap: 32px; list-style: none; }
.nav-links a { font-size: .9rem; font-weight: 500; color: var(--text-secondary); text-decoration: none; transition: color .2s; }
.nav-links a:hover { color: var(--text); }
.nav-demo { font-weight: 700 !important; color: var(--navy) !important; letter-spacing: -.01em; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-family: inherit; font-weight: 700; border: none; cursor: pointer; text-decoration: none; transition: all .2s; line-height: 1; }
.btn-primary { background: var(--orange); color: var(--white); padding: 14px 28px; border-radius: var(--radius-full); font-size: .95rem; }
.btn-primary:hover { background: var(--orange-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(234,88,12,.3); text-decoration: none; color: var(--white); }
.btn-outline { background: transparent; color: var(--navy); padding: 14px 28px; border-radius: var(--radius-full); font-size: .95rem; border: 2px solid var(--border); }
.btn-outline:hover { border-color: var(--navy); background: var(--off-white); text-decoration: none; }
.btn-sm { padding: 10px 20px; font-size: .85rem; }
.btn-lg { padding: 16px 32px; font-size: 1rem; }
.mobile-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
.mobile-toggle span { display: block; width: 24px; height: 2px; background: var(--text); margin: 5px 0; transition: .3s; }

/* SECTION */
.section { padding: 80px 0; }

/* FOOTER */
.site-footer { background: var(--off-white); border-top: 1px solid var(--border); padding: 48px 0 32px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.footer-brand .logo { display: inline-block; margin-bottom: 12px; }
.footer-brand p { font-size: .9rem; color: var(--text-secondary); line-height: 1.6; max-width: 280px; }
.footer-col h4 { font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--text-muted); margin-bottom: 16px; }
.footer-col a { display: block; font-size: .9rem; color: var(--text-secondary); padding: 4px 0; transition: color .2s; text-decoration: none; }
.footer-col a:hover { color: var(--text); }
.footer-bottom { border-top: 1px solid var(--border); padding-top: 24px; display: flex; align-items: center; justify-content: space-between; }
.footer-bottom p { font-size: .82rem; color: var(--text-muted); }

/* FAQ */
.faq-item { border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 8px; overflow: hidden; }
.faq-question { width: 100%; padding: 16px 20px; background: var(--white); border: none; text-align: left; font-size: .95rem; font-weight: 600; color: var(--text); cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-family: inherit; }
.faq-question:hover { background: var(--off-white); }
.faq-icon { width: 20px; height: 20px; flex-shrink: 0; color: var(--text-muted); transition: transform .3s; }
.faq-item.open .faq-icon { transform: rotate(45deg); }
.faq-answer { max-height: 0; overflow: hidden; transition: max-height .3s ease; }
.faq-item.open .faq-answer { max-height: 500px; }
.faq-answer-inner { padding: 0 20px 16px; font-size: .9rem; color: var(--text-secondary); line-height: 1.7; }

/* FADE */
.fade-up { opacity: 0; transform: translateY(30px); transition: opacity .6s ease, transform .6s ease; }
.fade-up.visible { opacity: 1; transform: translateY(0); }

/* RESPONSIVE */
@media (max-width: 1024px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 768px) {
  body { font-size: 16px; }
  .nav-links { display: none; }
  .mobile-toggle { display: block; }
  .nav-links.open { display: flex; flex-direction: column; position: absolute; top: 72px; left: 0; right: 0; background: var(--white); border-bottom: 1px solid var(--border); padding: 24px; gap: 16px; box-shadow: var(--shadow-lg); z-index: 999; }
  .footer-grid { grid-template-columns: 1fr; gap: 32px; }
  .footer-bottom { flex-direction: column; gap: 12px; text-align: center; }
}
"""


def make_header(prefix):
    return f'''<header class="site-header" id="header">
  <div class="header-inner">
    <a href="{prefix}index.html" class="logo">The Call<span>Taker</span></a>
    <ul class="nav-links" id="nav">
      <li><a href="{prefix}index.html#how-it-works">How It Works</a></li>
      <li><a href="{prefix}index.html#pricing">Pricing</a></li>
      <li><a href="{prefix}case-studies/">Case Studies</a></li>
      <li><a href="tel:+16157845747" class="nav-demo">Demo: (615) 784-5747</a></li>
      <li><a href="{prefix}pilot/" class="btn btn-primary btn-sm">Try Free for 14 Days</a></li>
    </ul>
    <button class="mobile-toggle" id="menuBtn" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>'''


def make_footer(prefix):
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{prefix}index.html" class="logo">The Call<span>Taker</span></a>
        <p>AI receptionist for service businesses. Answers every call, books every job, never takes a day off.</p>
      </div>
      <div class="footer-col">
        <h4>Product</h4>
        <a href="{prefix}index.html#how-it-works">How It Works</a>
        <a href="{prefix}index.html#pricing">Pricing</a>
        <a href="{prefix}industries/">Industries</a>
        <a href="{prefix}pilot/">Start Free Pilot</a>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <a href="{prefix}case-studies/">Case Studies</a>
        <a href="{prefix}book.html">Book a Demo</a>
        <a href="{prefix}blog/">Blog</a>
        <a href="{prefix}agency.html">Agencies</a>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <a href="tel:+16157845747">(615) 784-5747</a>
        <a href="mailto:wallace@thecalltaker.com">wallace@thecalltaker.com</a>
        <a href="{prefix}privacy.html">Privacy Policy</a>
        <a href="{prefix}terms.html">Terms of Service</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 The Call Taker. All rights reserved.</p>
      <p>Nashville, TN</p>
    </div>
  </div>
</footer>'''


INLINE_JS = '''<script>
// Sticky header
var h=document.getElementById('header');
if(h)window.addEventListener('scroll',function(){h.classList.toggle('scrolled',window.scrollY>20);});
// Mobile menu
var mb=document.getElementById('menuBtn'),nv=document.getElementById('nav');
if(mb&&nv){mb.addEventListener('click',function(){nv.classList.toggle('open');});}
if(nv)document.querySelectorAll('#nav a').forEach(function(a){a.addEventListener('click',function(){nv.classList.remove('open');});});
// Fade-in
var obs=new IntersectionObserver(function(e){e.forEach(function(en){if(en.isIntersecting){en.target.classList.add('visible');obs.unobserve(en.target);}});},{threshold:0.1,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.fade-up').forEach(function(el){obs.observe(el);});
// FAQ accordion
document.querySelectorAll('.faq-question').forEach(function(btn){btn.addEventListener('click',function(){var item=this.parentElement;var wasOpen=item.classList.contains('open');item.parentElement.querySelectorAll('.faq-item.open').forEach(function(el){el.classList.remove('open');});if(!wasOpen)item.classList.add('open');});});
</script>'''


def transform_cs_css(css):
    """Transform case study / pilot page CSS from dark to warm theme."""

    # ── Backgrounds ──
    css = css.replace('background: #000;', 'background: var(--white);')
    css = css.replace('background:#000;', 'background: var(--white);')
    css = css.replace('background: #000}', 'background: var(--white)}')
    css = css.replace('background:#000}', 'background: var(--white)}')
    css = css.replace("background: #111;", "background: var(--white);")
    css = css.replace("background:#111;", "background: var(--white);")

    # Hero glow — make very subtle on light
    css = re.sub(
        r"background:\s*radial-gradient\(ellipse,\s*var\(--green-glow\)\s*0%,\s*transparent\s*70%\)",
        "background: radial-gradient(ellipse, rgba(5,150,105,.06) 0%, transparent 70%)",
        css
    )

    # ── Heading colors: #fff → navy ──
    css = re.sub(r'(\.cs-hero h1\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)
    css = re.sub(r'(\.cs-content h2\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)
    css = re.sub(r'(\.cs-card h3\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)
    css = re.sub(r'(\.cs-cta h3\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)

    # Stat numbers: green → navy
    css = re.sub(r'(\.stat \.num\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--navy-dark)', css)
    css = re.sub(r'(\.agg-item \.n\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--navy-dark)', css)
    css = re.sub(r'(\.cs-card-stat \.n\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--navy-dark)', css)

    # Card hover glow: green → orange
    css = css.replace('rgba(0,220,130,0.25)', 'rgba(234,88,12,0.2)')
    css = css.replace('rgba(0,220,130,0.06)', 'rgba(234,88,12,0.06)')

    # CTA/quote boxes: green tint → subtle warm
    css = css.replace('rgba(0,220,130,0.03)', 'rgba(5,150,105,0.04)')
    css = css.replace('rgba(0,220,130,0.02)', 'rgba(5,150,105,0.03)')
    css = css.replace('rgba(0,220,130,0.15)', 'rgba(5,150,105,0.12)')

    # Tag border
    css = css.replace('rgba(0,220,130,0.06)', 'rgba(5,150,105,0.06)')

    # Step num: green bg → orange
    css = re.sub(
        r'(\.step-num\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#000',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    # Step time color
    css = re.sub(r'(\.step-card \.time\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--orange)', css)

    # Form focus border
    css = re.sub(r'(\.field [^{]*:focus\s*\{[^}]*?)border-color:\s*var\(--green\)', r'\1border-color: var(--orange)', css)

    # Form input bg
    css = css.replace('background: rgba(255,255,255,0.03);', 'background: var(--white);')
    css = css.replace('background:rgba(255,255,255,0.03);', 'background: var(--white);')

    # Select option dark bg
    css = re.sub(r'option\s*\{\s*background:\s*#111', 'option { background: var(--white)', css)

    # Pilot hero headline
    css = re.sub(r'(\.hero-headline\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)

    # Pilot form card heading
    css = re.sub(r'(\.pilot-form-card h2\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)

    # Pilot social proof numbers
    css = re.sub(r'(\.proof-item \.val\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)

    # Step card heading
    css = re.sub(r'(\.step-card h3\s*\{[^}]*?)color:\s*#fff', r'\1color: var(--navy-dark)', css)

    # ── Remaining #00dc82 → #059669 ──
    css = css.replace('#00dc82', '#059669')

    # ── Quote card attribution ──
    css = re.sub(r'(\.quote-card \.attribution\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--orange)', css)

    # Success icon border
    css = css.replace('rgba(0,220,130,0.1)', 'rgba(5,150,105,0.08)')
    css = css.replace('rgba(0,220,130,0.3)', 'rgba(5,150,105,0.2)')

    # Timeline dot
    css = re.sub(r'(\.tl-dot\s*\{[^}]*?)background:\s*var\(--green\)', r'\1background: var(--orange)', css)
    css = re.sub(r'(\.tl-day\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--orange)', css)

    return css


def process_page(filepath):
    """Process a case study or pilot page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    prefix = "../"

    # 1. Remove styles.css link
    html = re.sub(r'<link\s+rel="stylesheet"\s+href="[^"]*styles\.css"\s*/?>\s*\n?', '', html)

    # 2. Inject :root + shared CSS at start of <style>
    style_match = re.search(r'(<style>)\s*\n?', html)
    if style_match:
        inject = f'<style>\n{ROOT_VARS}\n{SHARED_CSS}\n'
        html = html[:style_match.start()] + inject + html[style_match.end():]

    # 3. Transform inline CSS
    style_start = html.find('<style>')
    style_end = html.find('</style>')
    if style_start >= 0 and style_end > style_start:
        css_block = html[style_start+7:style_end]
        css_block = transform_cs_css(css_block)
        html = html[:style_start+7] + css_block + html[style_end:]

    # 4. Fix inline style attributes: color:#fff → dark
    # Only in the body content, not in CSS
    body_start = html.find('<body')
    if body_start >= 0:
        body_html = html[body_start:]
        # Fix style="...color: #fff..." → color: var(--navy-dark) in headings/strong
        body_html = re.sub(r'(style="[^"]*?)color:\s*#fff', r'\1color: var(--navy-dark)', body_html)
        # Fix style="...color: var(--text-3)..." → keep (text-3 is redefined)
        # Fix style="...color: var(--green)..." → keep (green is redefined to #059669)
        # Fix border references
        body_html = body_html.replace('border-left:1px solid var(--border);', 'border-left:1px solid var(--border);')
        html = html[:body_start] + body_html

    # 5. Replace header
    html = re.sub(
        r'<header\s+class="header"[^>]*>.*?</header>\s*',
        '', html, flags=re.DOTALL
    )
    # Remove old mobile-nav
    html = re.sub(
        r'<nav\s+class="mobile-nav"[^>]*>.*?</nav>\s*',
        '', html, flags=re.DOTALL
    )
    # Remove old sticky-mobile-bar
    html = re.sub(
        r'<div\s+class="sticky-mobile-bar"[^>]*>.*?</div>\s*',
        '', html, flags=re.DOTALL
    )

    # Insert new header after <body>
    body_match = re.search(r'(<body[^>]*>)\s*\n?', html)
    if body_match:
        new_header = make_header(prefix)
        html = html[:body_match.end()] + '\n\n' + new_header + '\n\n' + html[body_match.end():]

    # 6. Replace footer
    html = re.sub(
        r'<footer\s+class="footer"[^>]*>.*?</footer>\s*',
        '', html, flags=re.DOTALL
    )
    new_footer = make_footer(prefix)
    body_close = html.rfind('</body>')
    if body_close >= 0:
        html = html[:body_close] + '\n' + new_footer + '\n\n' + html[body_close:]

    # 7. Replace scripts
    html = re.sub(r'<script\s+src="[^"]*script\.js"\s*>\s*</script>\s*\n?', '', html)
    html = re.sub(r'<script\s+src="[^"]*tct-tracking\.js"\s*>\s*</script>\s*\n?', '', html)
    body_close = html.rfind('</body>')
    if body_close >= 0:
        html = html[:body_close] + INLINE_JS + '\n' + html[body_close:]

    # 8. Re-add tct-tracking.js in head
    if 'tct-tracking' not in html:
        head_close = html.find('</head>')
        if head_close >= 0:
            html = html[:head_close] + '<script src="../tct-tracking.js"></script>\n' + html[head_close:]

    # 9. Change btn-green to btn-primary
    html = html.replace('class="btn btn-green btn-lg"', 'class="btn btn-primary"')
    html = html.replace('class="btn btn-green"', 'class="btn btn-primary"')

    # 10. Clean up blank lines
    html = re.sub(r'\n{4,}', '\n\n\n', html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


def fix_popup():
    """Fix tct-tracking.js popup colors from dark/blue to warm/light."""
    fp = os.path.join(WEBSITE, 'tct-tracking.js')
    with open(fp, 'r', encoding='utf-8') as f:
        js = f.read()

    # Modal background: dark blue → white
    js = js.replace("background: #1a1a2e;", "background: #ffffff;")

    # Modal border: blue → subtle gray
    js = js.replace("border: 1px solid rgba(67,97,238,0.3);", "border: 1px solid rgba(0,0,0,0.08);")

    # Modal shadow: heavy dark → lighter
    js = js.replace("box-shadow: 0 25px 60px rgba(0,0,0,0.5);", "box-shadow: 0 25px 60px rgba(0,0,0,0.15);")

    # Overlay: slightly lighter
    js = js.replace("background: rgba(0,0,0,0.7);", "background: rgba(0,0,0,0.5);")

    # Close button color
    js = js.replace("color: #aaa; font-size: 28px;", "color: #9ca3af; font-size: 28px;")
    js = js.replace("#tct-popup-close:hover { color: #fff; }", "#tct-popup-close:hover { color: #111827; }")

    # Heading color
    js = js.replace("color: #fff;' +\n      '  font-size: 24px;", "color: #111827;' +\n      '  font-size: 24px;")

    # Subhead color
    js = js.replace("color: #ccc;", "color: #4b5563;")

    # Input styling: dark bg → light
    js = js.replace("background: #16213e;", "background: #f9fafb;")
    js = js.replace("border: 1px solid rgba(67,97,238,0.3);' +", "border: 1px solid #e5e7eb;' +")
    js = js.replace("color: #fff;' +\n      '  font-size: 15px;", "color: #111827;' +\n      '  font-size: 15px;")

    # Placeholder color
    js = js.replace("color: #777; }", "color: #9ca3af; }")

    # Focus border: blue → orange
    js = js.replace("border-color: #4361ee;", "border-color: #ea580c;")

    # Select default color
    js = js.replace("color: #777;' +\n      '  cursor: pointer;", "color: #9ca3af;' +\n      '  cursor: pointer;")

    # Select arrow SVG color
    js = js.replace("stroke=\\'%23777\\'", "stroke=\\'%239ca3af\\'")

    # Selected select color
    js = js.replace("select.tct-selected { color: #fff; }", "select.tct-selected { color: #111827; }")

    # Submit button: green → orange
    js = js.replace("background: #27ae60;' +\n      '  color: #fff;", "background: #ea580c;' +\n      '  color: #fff;")
    js = js.replace("background: #2ecc71;", "background: #c2410c;")

    # Disabled button
    js = js.replace("background: #555;", "background: #d1d5db;")

    # Success checkmark color
    js = js.replace("color: #27ae60;' +\n      '  margin-bottom: 16px;", "color: #059669;' +\n      '  margin-bottom: 16px;")

    # Success heading
    js = js.replace("'#tct-popup-success h3 {' +\n      '  color: #fff;", "'#tct-popup-success h3 {' +\n      '  color: #111827;")

    # Success body text
    js = js.replace("'#tct-popup-success p {' +\n      '  color: #aaa;", "'#tct-popup-success p {' +\n      '  color: #4b5563;")

    # Error color: update to consistent red
    js = js.replace("color: #e74c3c;", "color: #ef4444;")

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(js)
    print("  [OK] tct-tracking.js popup → warm theme")


def main():
    print("=== Fixing remaining dark-themed pages ===\n")

    # 1. Fix popup
    print("1. Fixing tct-tracking.js popup...")
    fix_popup()
    print()

    # 2. Fix case study pages
    cs_pages = sorted(glob.glob(os.path.join(WEBSITE, 'case-studies', '*.html')))
    print(f"2. Fixing {len(cs_pages)} case study pages...")
    for fp in cs_pages:
        name = os.path.relpath(fp, WEBSITE)
        try:
            process_page(fp)
            print(f"  [OK] {name}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
    print()

    # 3. Fix pilot page
    pilot_page = os.path.join(WEBSITE, 'pilot', 'index.html')
    print("3. Fixing pilot page...")
    if os.path.exists(pilot_page):
        try:
            process_page(pilot_page)
            print(f"  [OK] pilot/index.html")
        except Exception as e:
            print(f"  [ERR] pilot/index.html: {e}")
    else:
        print("  [SKIP] pilot/index.html not found")

    print("\nDone!")


if __name__ == '__main__':
    main()
