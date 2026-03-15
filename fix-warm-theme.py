#!/usr/bin/env python3
"""
Transform all industry + blog pages from dark theme to warm/light theme
matching the homepage (index.html) design system.

Homepage: white bg, orange CTAs, navy headings, green accents, Inter font
Current pages: black bg, neon green CTAs, white text — WRONG
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
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

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
.mobile-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
.mobile-toggle span { display: block; width: 24px; height: 2px; background: var(--text); margin: 5px 0; transition: .3s; }

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


def transform_css(css):
    """Transform dark-theme inline CSS to warm/light theme."""

    # ── BACKGROUNDS ──
    # Hero dark gradient → white with subtle green tint
    css = re.sub(
        r'background:\s*linear-gradient\(135deg,\s*#000\s+0%\s*,\s*rgba\(0,220,130,[^)]+\)\s*100%\)',
        'background: linear-gradient(135deg, var(--white) 0%, rgba(5,150,105,.03) 100%)',
        css
    )
    # Dark bg with green tint
    css = re.sub(
        r"background:\s*linear-gradient\(135deg,\s*rgba\(0,220,130,[^)]+\)\s*,\s*#000\)",
        "background: linear-gradient(135deg, rgba(5,150,105,.03), var(--white))",
        css
    )
    # ROI card gradient
    css = re.sub(
        r"background:\s*linear-gradient\(135deg,\s*rgba\(0,220,130,[^)]+\)\s*,\s*rgba\(233,69,96,[^)]+\)\)",
        "background: linear-gradient(135deg, var(--green-light), var(--off-white))",
        css
    )
    # CTA box gradient
    css = re.sub(
        r"background:\s*linear-gradient\(135deg,\s*rgba\(0,220,130,[^)]+\)\s*,\s*rgba\(0,220,130,[^)]+\)\)",
        "background: linear-gradient(135deg, var(--orange-light), var(--off-white))",
        css
    )
    # Radial glow bg → very subtle
    css = re.sub(
        r"background:\s*radial-gradient\(circle,\s*rgba\(0,220,130,[^)]+\)\s*0%\s*,\s*transparent\s*50%\)",
        "background: radial-gradient(circle, rgba(5,150,105,.02) 0%, transparent 50%)",
        css
    )
    # background:#000 → white (standalone, not in gradients)
    css = re.sub(r'background:\s*#000\b(?![\d])', 'background: var(--white)', css)

    # ── REMOVE DARK EFFECTS ──
    # Text shadows with green glow
    css = re.sub(r';?\s*text-shadow:\s*0\s+0\s+\d+px\s+(?:var\(--green-glow\)|rgba\(0,220,130[^)]*\)|rgba\(5,150,105[^)]*\))', '', css)
    # Remove pulse animation
    css = re.sub(r';?\s*animation:\s*pulse\s+[\d.]+s\s+infinite', '', css)
    css = re.sub(r'@keyframes\s+pulse\s*\{[^}]*\{[^}]*\}[^}]*\{[^}]*\}\s*\}', '', css)
    # Remove heroGlow animation
    css = re.sub(r'@keyframes\s+heroGlow\s*\{[^}]*\{[^}]*\}[^}]*\{[^}]*\}\s*\}', '', css)
    # Remove backdrop-filter on cards (not needed on light)
    css = re.sub(r';?\s*backdrop-filter:\s*blur\(\d+px\)', '', css)

    # ── GREEN → ORANGE for CTAs/buttons ──
    # .hero-cta button
    css = re.sub(
        r'(\.hero-cta\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    css = re.sub(
        r'(\.hero-cta:hover\s*\{[^}]*?)background:\s*#00b86e',
        r'\1background: var(--orange-hover)',
        css
    )
    # .pricing-btn.primary
    css = re.sub(
        r'(\.pricing-btn\.primary\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    css = re.sub(
        r'(\.pricing-btn\.primary:hover\s*\{[^}]*?)background:\s*#00b86e',
        r'\1background: var(--orange-hover)',
        css
    )
    # .pricing-btn.secondary
    css = re.sub(
        r'(\.pricing-btn\.secondary\s*\{[^}]*?)color:\s*var\(--green\)\s*;\s*border:\s*2px\s+solid\s+var\(--green\)',
        r'\1color: var(--orange); border: 2px solid var(--orange)',
        css
    )
    css = re.sub(
        r'(\.pricing-btn\.secondary:hover\s*\{[^}]*?)background:\s*rgba\(0,220,130,[^)]+\)',
        r'\1background: var(--orange-light)',
        css
    )
    # .btn-submit
    css = re.sub(
        r'(\.btn-submit\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    css = re.sub(
        r'(\.btn-submit:hover\s*\{[^}]*?)background:\s*#00b86e',
        r'\1background: var(--orange-hover)',
        css
    )
    # .cta-btn
    css = re.sub(
        r'(\.cta-btn\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    # .pricing-badge
    css = re.sub(
        r'(\.pricing-badge\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    # .step-num (step numbers)
    css = re.sub(
        r'(\.step-num\s*\{[^}]*?)background:\s*var\(--green\)\s*;\s*color:\s*#fff',
        r'\1background: var(--orange); color: var(--white)',
        css
    )
    # Step card top border
    css = css.replace('border-top:3px solid var(--green)', 'border-top:3px solid var(--orange)')
    # Featured pricing card border
    css = re.sub(
        r'(\.pricing-card\.featured\s*\{[^}]*?)border-color:\s*var\(--green\)',
        r'\1border-color: var(--orange)',
        css
    )
    # CTA box border
    css = re.sub(r'border:\s*2px\s+solid\s+var\(--green\)', 'border: 2px solid var(--orange)', css)
    # Callout left border
    css = css.replace('border-left:4px solid var(--green)', 'border-left:4px solid var(--orange)')
    # Pain card left border — keep red (#ef4444) or make orange
    # (keeping red for pain points is good UX contrast)

    # ── GREEN → NAVY for price/stat numbers ──
    css = re.sub(
        r'(\.pricing-price\s*\{[^}]*?)color:\s*var\(--green\)',
        r'\1color: var(--navy-dark)',
        css
    )
    css = re.sub(
        r'(\.stat-num\s*\{[^}]*?)color:\s*var\(--green\)',
        r'\1color: var(--navy-dark)',
        css
    )

    # ── GREEN → BLUE for links ──
    css = re.sub(r'(\.scroll-link\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--blue)', css)
    css = re.sub(r'(\.related\s+a\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--blue)', css)
    css = re.sub(r'(\.footer\s+a\s*\{[^}]*?)color:\s*var\(--green\)', r'\1color: var(--blue)', css)

    # ── GREEN → NAVY for article headings ──
    css = re.sub(
        r'(\.article-container\s+h2\s*\{[^}]*?)color:\s*var\(--green\)',
        r'\1color: var(--navy)',
        css
    )

    # ── REMAINING GREEN RGBA ──
    css = re.sub(r'rgba\(0,220,130,\s*\.4\)', 'rgba(234,88,12,.3)', css)
    css = re.sub(r'rgba\(0,220,130,\s*\.5\)', 'rgba(234,88,12,.35)', css)
    css = re.sub(r'rgba\(0,220,130,\s*\.6\)', 'rgba(234,88,12,.4)', css)
    css = re.sub(r'rgba\(0,220,130,\s*\.\d+\)', 'rgba(5,150,105,.06)', css)
    css = re.sub(r'rgba\(233,69,96,\s*\.2\)', 'rgba(239,68,68,.1)', css)

    # ── BOX SHADOWS ──
    css = css.replace('box-shadow:0 8px 32px rgba(0,0,0,.3)', 'box-shadow: var(--shadow-lg)')
    css = css.replace('box-shadow:0 12px 40px rgba(0,0,0,.4)', 'box-shadow: var(--shadow-xl)')
    css = re.sub(r'box-shadow:\s*0\s+0\s+25px\s+var\(--green-glow\)', 'box-shadow: var(--shadow-lg)', css)
    css = re.sub(r'box-shadow:\s*0\s+0\s+30px\s+rgba\(0,220,130,[^)]+\)', 'box-shadow: var(--shadow-lg)', css)
    css = re.sub(r'box-shadow:\s*0\s+0\s+12px\s+var\(--green-glow\)', 'box-shadow: var(--shadow-sm)', css)

    # ── FORM FOCUS ──
    css = re.sub(
        r'border-color:\s*var\(--green\)\s*;\s*box-shadow:\s*0\s+0\s+0\s+3px\s+var\(--green-glow\)',
        'border-color: var(--orange); box-shadow: 0 0 0 3px rgba(234,88,12,.12)',
        css
    )
    # Form input bg
    css = css.replace('background:rgba(255,255,255,.05)', 'background: var(--white)')
    # Select option bg
    css = re.sub(r'option\s*\{\s*background:\s*(?:#000|var\(--white\))', 'option{background: var(--white)', css)

    # ── TESTIMONIAL QUOTE ──
    css = re.sub(r"(content:\s*['\"]\\201C['\"];[^}]*?)color:\s*var\(--green\)", r"\1color: var(--orange)", css)
    # Author avatar gradient
    css = css.replace('background:linear-gradient(135deg,var(--green),#ef4444)', 'background: linear-gradient(135deg, var(--orange), var(--navy))')

    # ── PHONE COLOR ──
    css = re.sub(r'(\.cta-phone\s*\{[^}]*?)color:\s*#f5a623', r'\1color: var(--navy)', css)

    # ── HERO PADDING for fixed header ──
    css = re.sub(r'(\.hero\s*\{[^}]*?)padding-top:\s*120px', r'\1padding-top: 140px', css)
    # Article container padding
    css = re.sub(r'(\.article-container\s*\{[^}]*?)padding-top:\s*80px', r'\1padding-top: 100px', css)

    # ── STRAGGLER HEX CODES ──
    css = css.replace('#00dc82', '#059669')
    css = css.replace('#00b86e', 'var(--orange-hover)')

    # ── CLEAN UP REMAINING var(--green) → var(--green) is fine (now #059669) ──
    # The :root redefines --green to #059669, so existing var(--green) for
    # accents/checkmarks/stat colors will automatically be the muted green.

    return css


def process_page(filepath):
    """Process a single industry or blog page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Determine prefix for relative URLs
    # industries/foo.html → "../"
    # blog/foo.html → "../"
    prefix = "../"

    # ── 1. REMOVE styles.css link ──
    html = re.sub(r'<link\s+rel="stylesheet"\s+href="[^"]*styles\.css"\s*/?>\s*\n?', '', html)

    # ── 2. INJECT :root + shared CSS at start of <style> ──
    style_match = re.search(r'(<style>)\s*\n?', html)
    if style_match:
        inject = f'<style>\n{ROOT_VARS}\n{SHARED_CSS}\n'
        html = html[:style_match.start()] + inject + html[style_match.end():]

    # ── 3. TRANSFORM inline CSS colors ──
    style_start = html.find('<style>')
    style_end = html.find('</style>')
    if style_start >= 0 and style_end > style_start:
        css_block = html[style_start+7:style_end]
        css_block = transform_css(css_block)
        html = html[:style_start+7] + css_block + html[style_end:]

    # ── 4. REPLACE HEADER ──
    # Remove old header (multiple patterns)
    # Pattern A: <header class="header">...</header>
    html = re.sub(
        r'<header\s+class="header"[^>]*>.*?</header>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    # Pattern B: <header class="site-header" ... (shouldn't exist yet, but safe)
    # Don't remove if we just injected it

    # Remove old mobile-nav
    html = re.sub(
        r'<nav\s+class="mobile-nav"[^>]*>.*?</nav>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # Remove old sticky-mobile-bar
    html = re.sub(
        r'<div\s+class="sticky-mobile-bar"[^>]*>.*?</div>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # Insert new header after <body>
    body_match = re.search(r'(<body[^>]*>)\s*\n?', html)
    if body_match:
        new_header = make_header(prefix)
        html = html[:body_match.end()] + '\n\n' + new_header + '\n\n' + html[body_match.end():]

    # ── 5. REPLACE FOOTER ──
    # Remove old footer patterns
    html = re.sub(
        r'<footer\s+class="footer"[^>]*>.*?</footer>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # Insert new footer before closing scripts / </body>
    new_footer = make_footer(prefix)

    # Find where to insert: before </body> or before final scripts
    body_close = html.rfind('</body>')
    if body_close >= 0:
        html = html[:body_close] + '\n' + new_footer + '\n\n' + html[body_close:]

    # ── 6. REPLACE SCRIPTS ──
    # Remove old script.js and tct-tracking.js script tags at bottom
    html = re.sub(r'<script\s+src="[^"]*script\.js"\s*>\s*</script>\s*\n?', '', html)
    html = re.sub(r'<script\s+src="[^"]*tct-tracking\.js"\s*>\s*</script>\s*\n?', '', html)

    # Add inline JS before </body>
    body_close = html.rfind('</body>')
    if body_close >= 0:
        html = html[:body_close] + INLINE_JS + '\n' + html[body_close:]

    # ── 7. Keep tracking in <head> ──
    # tct-tracking.js in <head> — re-add if it was there
    if 'tct-tracking' not in html:
        head_close = html.find('</head>')
        if head_close >= 0:
            html = html[:head_close] + '<script src="../tct-tracking.js"></script>\n' + html[head_close:]

    # ── 8. Ensure Google Ads tag is present ──
    if 'AW-17970510102' not in html:
        head_close = html.find('</head>')
        if head_close >= 0:
            tag = '<script async src="https://www.googletagmanager.com/gtag/js?id=AW-17970510102"></script>\n<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag(\'js\',new Date());gtag(\'config\',\'AW-17970510102\');</script>\n'
            html = html[:head_close] + tag + html[head_close:]

    # ── 9. Fix blog pages: bare h1/meta after removed header ──
    # Some blog pages had h1 inside the old <header> that got removed.
    # The content h1 should be in the article body, which is fine.

    # ── 10. Clean up extra blank lines ──
    html = re.sub(r'\n{4,}', '\n\n\n', html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return True


def main():
    # Collect all industry + blog pages
    industry_pages = sorted(glob.glob(os.path.join(WEBSITE, 'industries', '*.html')))
    blog_pages = sorted(glob.glob(os.path.join(WEBSITE, 'blog', '*.html')))

    # Exclude index pages (hub pages) — they may have different structure
    industry_pages = [p for p in industry_pages if not p.endswith('index.html')]
    blog_pages = [p for p in blog_pages if not p.endswith('index.html')]

    all_pages = industry_pages + blog_pages
    print(f"Processing {len(industry_pages)} industry + {len(blog_pages)} blog = {len(all_pages)} pages")
    print()

    ok = 0
    errors = []
    for fp in all_pages:
        name = os.path.relpath(fp, WEBSITE)
        try:
            process_page(fp)
            print(f"  [OK] {name}")
            ok += 1
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
            errors.append((name, str(e)))

    print(f"\nDone: {ok} OK, {len(errors)} errors")
    if errors:
        for name, err in errors:
            print(f"  - {name}: {err}")


if __name__ == '__main__':
    main()
