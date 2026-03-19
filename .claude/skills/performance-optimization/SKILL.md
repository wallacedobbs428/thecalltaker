---
name: performance-optimization
description: "Optimize web application performance. Use when improving page load times, Core Web Vitals, Lighthouse scores, bundle sizes, rendering performance, or server response times. Covers HTML/CSS/JS optimization, image optimization, caching strategies, CDN configuration, lazy loading, and performance monitoring."
category: performance
---

# Performance Optimization — Web Performance Playbook

Systematically improve web performance through measurement, optimization, and monitoring.

---

## Performance Audit Checklist

Run this before ANY optimization work:

### 1. Measure First
```bash
# Lighthouse CLI audit
npx lighthouse https://yoursite.com --output=json --output-path=./audit.json

# Core Web Vitals
# LCP (Largest Contentful Paint) < 2.5s
# FID (First Input Delay) < 100ms
# CLS (Cumulative Layout Shift) < 0.1
# INP (Interaction to Next Paint) < 200ms
```

### 2. Identify Bottlenecks (Priority Order)
1. **Server response time** (TTFB > 600ms = problem)
2. **Render-blocking resources** (CSS/JS in `<head>`)
3. **Image optimization** (usually the biggest win)
4. **JavaScript bundle size** (> 200KB compressed = problem)
5. **Font loading** (FOUT/FOIT issues)
6. **Third-party scripts** (analytics, chat widgets, ads)

---

## HTML Optimization

### Critical Rendering Path
```html
<!-- Preload critical resources -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/hero.webp" as="image">

<!-- Inline critical CSS (above-the-fold styles) -->
<style>/* Critical CSS here — extract with Critical npm package */</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">

<!-- Defer JavaScript -->
<script defer src="/app.js"></script>
```

### Resource Hints
```html
<!-- DNS prefetch for third-party domains -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//cdn.jsdelivr.net">

<!-- Preconnect for critical third-party origins -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Prefetch next-page resources -->
<link rel="prefetch" href="/pricing.html">
```

---

## Image Optimization

### Format Selection
| Format | Use Case | Savings vs PNG |
|--------|----------|---------------|
| WebP | Photos, general images | 25-35% smaller |
| AVIF | Photos (modern browsers) | 50% smaller |
| SVG | Icons, logos, illustrations | Resolution independent |
| PNG | Screenshots with text | Baseline |

### Responsive Images
```html
<picture>
  <source srcset="/hero.avif" type="image/avif">
  <source srcset="/hero.webp" type="image/webp">
  <img src="/hero.jpg" alt="Hero"
       width="1200" height="600"
       loading="lazy"
       decoding="async">
</picture>

<!-- Responsive srcset -->
<img srcset="/hero-400.webp 400w,
             /hero-800.webp 800w,
             /hero-1200.webp 1200w"
     sizes="(max-width: 768px) 100vw, 50vw"
     src="/hero-800.webp"
     alt="Hero image"
     loading="lazy">
```

### Lazy Loading
- Add `loading="lazy"` to all images below the fold
- NEVER lazy-load the LCP image (hero image)
- Use `decoding="async"` for non-critical images
- Set explicit `width` and `height` to prevent CLS

---

## CSS Optimization

### Critical CSS Extraction
```bash
# Extract critical CSS automatically
npx critical index.html --base ./ --inline --minify > index-optimized.html
```

### Reduce CSS Size
- Remove unused CSS: `npx purgecss --css styles.css --content index.html`
- Minify: `npx csso styles.css --output styles.min.css`
- Use CSS containment: `contain: layout style paint`
- Prefer `transform` and `opacity` for animations (GPU-accelerated)
- Avoid `@import` in CSS (blocks parallel download)

### Font Optimization
```css
/* Use font-display: swap to prevent FOIT */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;
  unicode-range: U+0000-00FF; /* Latin subset only */
}
```

---

## JavaScript Optimization

### Bundle Analysis
```bash
# Analyze bundle size
npx source-map-explorer bundle.js
# or
npx webpack-bundle-analyzer stats.json
```

### Code Splitting
- Split by route (each page loads only its JS)
- Lazy-load below-fold components
- Use dynamic `import()` for non-critical features

### Defer Third-Party Scripts
```html
<!-- Load analytics after page is interactive -->
<script>
  window.addEventListener('load', function() {
    setTimeout(function() {
      var s = document.createElement('script');
      s.src = 'https://analytics.example.com/script.js';
      document.body.appendChild(s);
    }, 3000);
  });
</script>
```

---

## Caching Strategy

### Cache-Control Headers
```
# Static assets (CSS, JS, images) — cache for 1 year
Cache-Control: public, max-age=31536000, immutable

# HTML pages — revalidate every time
Cache-Control: no-cache

# API responses — short cache
Cache-Control: public, max-age=300, stale-while-revalidate=600
```

### Service Worker (Offline + Cache)
```javascript
// Cache static assets on install
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('v1').then(cache =>
      cache.addAll(['/styles.css', '/app.js', '/offline.html'])
    )
  );
});

// Serve from cache, fallback to network
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
```

---

## Performance Budget

Set these limits and enforce in CI:

| Metric | Budget | Tool |
|--------|--------|------|
| Total page weight | < 500KB | Lighthouse |
| JavaScript | < 200KB (compressed) | bundlesize |
| CSS | < 50KB (compressed) | bundlesize |
| LCP | < 2.5s | Web Vitals |
| CLS | < 0.1 | Web Vitals |
| INP | < 200ms | Web Vitals |
| TTFB | < 600ms | Web Vitals |
| Lighthouse Performance | > 90 | Lighthouse CI |

---

## Quick Wins (Do These First)

1. Compress images to WebP (biggest impact for least effort)
2. Add `loading="lazy"` to below-fold images
3. Defer non-critical JS with `defer` attribute
4. Enable gzip/brotli compression on server
5. Set proper Cache-Control headers
6. Preload LCP image and critical fonts
7. Remove unused CSS/JS
8. Add explicit dimensions to images (prevents CLS)
