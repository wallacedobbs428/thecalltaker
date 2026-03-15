#!/usr/bin/env python3
"""Fix blog pages: wrap bare h1 + meta-line in a blog-hero container,
fix article-container padding override, and add blog-hero CSS."""
import os, re, glob

WEBSITE = os.path.expanduser("~/Desktop/wallace-hvac/website/website")

BLOG_HERO_CSS = """
  /* ── BLOG HERO ── */
  .blog-hero { padding: 120px 24px 32px; max-width: 1200px; margin: 0 auto; text-align: center; }
  .blog-hero h1 { font-size: clamp(1.6rem,4vw,2.6rem); font-weight: 800; max-width: 800px; margin: 0 auto; line-height: 1.2; color: var(--navy-dark); }
  .blog-hero .meta-line { color: var(--text-muted); font-size: .9rem; margin-top: .75rem; }
  .blog-hero .breadcrumb { font-size: .85rem; color: var(--text-muted); margin-bottom: 1rem; }
  .blog-hero .breadcrumb a { color: var(--text-secondary); text-decoration: none; }
  .blog-hero .breadcrumb a:hover { color: var(--text); }
"""

ok = 0
blog_pages = sorted(glob.glob(os.path.join(WEBSITE, 'blog', '*.html')))
blog_pages = [p for p in blog_pages if not p.endswith('index.html')]

for fp in blog_pages:
    name = os.path.relpath(fp, WEBSITE)
    with open(fp, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = False

    # 1. Add blog-hero CSS before </style> if not already there
    if '.blog-hero' not in html:
        style_end = html.find('</style>')
        if style_end >= 0:
            html = html[:style_end] + BLOG_HERO_CSS + html[style_end:]
            changed = True

    # 2. Fix article-container padding override
    # The shorthand `padding:2.5rem 1.5rem 4rem` overrides the padding-top: 100px
    # Replace with explicit padding values
    html = re.sub(
        r'\.article-container\s*\{[^}]*padding-top:\s*100px[^}]*padding:\s*2\.5rem\s+1\.5rem\s+4rem[^}]*\}',
        '.article-container{max-width:720px;margin:0 auto;padding:2.5rem 1.5rem 4rem}',
        html
    )
    # Also handle case where padding-top wasn't inserted
    html = re.sub(
        r'(\.article-container\s*\{)padding-top:\s*\d+px\s*;',
        r'\1',
        html
    )

    # 3. Wrap bare h1 + meta-line after site-header in blog-hero div
    # Pattern: </header>\n\n<h1>...</h1>\n  <div class="meta-line">...</div>
    if '<div class="blog-hero">' not in html:
        # Match h1 followed by optional meta-line, followed by optional breadcrumb
        pattern = r'(</header>\s*\n\s*)\n*(<(?:div class="breadcrumb"|p class="breadcrumb")[^>]*>.*?</(?:div|p)>\s*\n)?\s*(<h1[^>]*>.*?</h1>\s*\n)\s*(<div class="meta-line"[^>]*>.*?</div>\s*\n)?'

        def wrap_hero(m):
            before = m.group(1)
            breadcrumb = m.group(2) or ''
            h1 = m.group(3)
            meta = m.group(4) or ''
            return f'{before}\n<div class="blog-hero">\n{breadcrumb}{h1}{meta}</div>\n\n'

        new_html = re.sub(pattern, wrap_hero, html, flags=re.DOTALL)
        if new_html != html:
            html = new_html
            changed = True

    # 4. Also handle blog pages where h1 is bare (no breadcrumb or meta)
    # Just make sure any bare h1 right after </header> gets wrapped
    if '<div class="blog-hero">' not in html:
        pattern2 = r'(</header>\s*\n\s*)\n*(<h1[^>]*>.*?</h1>)\s*\n(\s*<div class="meta-line"[^>]*>.*?</div>)?'
        def wrap_hero2(m):
            before = m.group(1)
            h1 = m.group(2)
            meta = m.group(3) or ''
            return f'{before}\n<div class="blog-hero">\n{h1}\n{meta}\n</div>\n\n'
        new_html = re.sub(pattern2, wrap_hero2, html, flags=re.DOTALL)
        if new_html != html:
            html = new_html
            changed = True

    if changed:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  [OK] {name}")
        ok += 1
    else:
        print(f"  [SKIP] {name} (already fixed or no match)")

print(f"\nDone: {ok} fixed")
