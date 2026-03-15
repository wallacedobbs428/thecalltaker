---
name: ui-ux-pro-max
description: "Produce elite, agency-tier UI/UX with real design system architecture. Use when building any web UI, app, dashboard, landing page, component, or artifact. Triggers on: build/redesign requests, 'make it look good/premium/clean/modern/sleek', React/HTML/CSS/Tailwind work, or any frontend output. Goes beyond visual polish — maps user journeys, builds design token systems, handles all 5 interaction states, includes dark/light mode, WCAG AA accessibility, physics-based motion, and performance-conscious code."
category: frontend
---

# UI/UX Pro Max — Elite Frontend Design System

Build agency-tier interfaces with real UX thinking, design system architecture, and production-grade polish. Every output is mobile-first, accessible, performant, dark/light mode ready, and built with composable components.

**Output format:** Single-file unless explicitly asked otherwise. React (.jsx) for interactive apps, pure HTML/CSS/JS for static content.

---

## Phase 0 — UX Audit (ALWAYS do this first)

Before writing ANY code, produce a brief UX audit as a comment block at the top of the file. This is non-negotiable.

```
<!--
  ╔══════════════════════════════════════════╗
  ║         UX AUDIT — [Component Name]      ║
  ╠══════════════════════════════════════════╣
  ║ PRIMARY ACTION: [What the user came to do]
  ║ SECONDARY ACTIONS: [Supporting tasks]
  ║ USER JOURNEY: [Entry → Key steps → Exit]
  ║ FRICTION POINTS: [What could go wrong]
  ║ HIERARCHY: [Visual priority order]
  ║ EMPTY STATES: [What shows when no data]
  ║ ERROR STATES: [What shows when things break]
  ║ SUCCESS STATES: [What shows when it works]
  ╚══════════════════════════════════════════╝
-->
```

Map the user journey BEFORE touching layout. Identify:
- What is the ONE thing the user should do? (Primary CTA)
- What competes for attention and shouldn't? (Noise reduction)
- Where will users get confused? (Friction audit)
- What happens when the page is empty, loading, broken, or full? (State mapping)

---

## Phase 1 — Design Token System

Every output MUST begin with a CSS custom property layer. No magic numbers anywhere in the code.

### Required Token Categories

```css
:root {
  /* ─── COLOR SYSTEM ─── */
  /* Semantic colors — NEVER use raw hex in components */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #f1f3f5;
  --color-bg-elevated: #ffffff;
  --color-bg-overlay: rgba(0, 0, 0, 0.5);

  --color-text-primary: #1a1a2e;
  --color-text-secondary: #4a5568;
  --color-text-tertiary: #a0aec0;
  --color-text-inverse: #ffffff;
  --color-text-link: #3182ce;

  --color-brand-primary: #3182ce;
  --color-brand-primary-hover: #2c5282;
  --color-brand-primary-active: #2b6cb0;
  --color-brand-secondary: #38b2ac;
  --color-brand-accent: #ed8936;

  --color-semantic-success: #38a169;
  --color-semantic-warning: #d69e2e;
  --color-semantic-error: #e53e3e;
  --color-semantic-info: #3182ce;

  --color-border-default: #e2e8f0;
  --color-border-strong: #cbd5e0;
  --color-border-focus: #3182ce;

  /* ─── SPACING SCALE (4px base grid) ─── */
  --space-1: 4px;    /* Tight */
  --space-2: 8px;    /* Compact */
  --space-3: 12px;   /* Default gap */
  --space-4: 16px;   /* Standard */
  --space-5: 20px;   /* Comfortable */
  --space-6: 24px;   /* Spacious */
  --space-8: 32px;   /* Section gap */
  --space-10: 40px;  /* Block gap */
  --space-12: 48px;  /* Large section */
  --space-16: 64px;  /* Hero spacing */
  --space-20: 80px;  /* Page section */
  --space-24: 96px;  /* Major section */

  /* ─── TYPE SCALE (1.25 ratio — Major Third) ─── */
  --text-xs: 0.75rem;     /* 12px — Captions */
  --text-sm: 0.875rem;    /* 14px — Small body */
  --text-base: 1rem;      /* 16px — Body */
  --text-lg: 1.125rem;    /* 18px — Lead text */
  --text-xl: 1.25rem;     /* 20px — Subheading */
  --text-2xl: 1.5rem;     /* 24px — H4 */
  --text-3xl: 1.875rem;   /* 30px — H3 */
  --text-4xl: 2.25rem;    /* 36px — H2 */
  --text-5xl: 3rem;       /* 48px — H1 */
  --text-6xl: 3.75rem;    /* 60px — Display */

  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;

  /* ─── BORDER RADIUS ─── */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;

  /* ─── SHADOW SYSTEM ─── */
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04);
  --shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.15);
  --shadow-inner: inset 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-focus: 0 0 0 3px rgba(49, 130, 206, 0.4);

  /* ─── Z-INDEX SCALE ─── */
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-popover: 500;
  --z-toast: 600;
  --z-tooltip: 700;

  /* ─── TRANSITIONS ─── */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);     /* General UI */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);             /* Exit animations */
  --ease-out: cubic-bezier(0, 0, 0.2, 1);            /* Enter animations */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy/playful */
  --ease-elastic: cubic-bezier(0.68, -0.55, 0.27, 1.55); /* Overshoot */

  --duration-instant: 75ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-slower: 600ms;

  /* ─── LAYOUT ─── */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1440px;
}
```

### Dark Mode Tokens (REQUIRED)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #0f1117;
    --color-bg-secondary: #1a1d2e;
    --color-bg-tertiary: #252836;
    --color-bg-elevated: #1e2130;

    --color-text-primary: #e2e8f0;
    --color-text-secondary: #a0aec0;
    --color-text-tertiary: #718096;
    --color-text-inverse: #1a1a2e;

    --color-border-default: #2d3748;
    --color-border-strong: #4a5568;

    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.4);
  }
}

/* Manual toggle support */
[data-theme="dark"] {
  /* Same dark values as above */
  --color-bg-primary: #0f1117;
  --color-bg-secondary: #1a1d2e;
  --color-bg-tertiary: #252836;
  --color-bg-elevated: #1e2130;
  --color-text-primary: #e2e8f0;
  --color-text-secondary: #a0aec0;
  --color-text-tertiary: #718096;
  --color-text-inverse: #1a1a2e;
  --color-border-default: #2d3748;
  --color-border-strong: #4a5568;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.4);
}
```

### No-Flash Dark Mode Script (place in `<head>`)

```html
<script>
  (function() {
    var theme = localStorage.getItem('theme');
    if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
</script>
```

---

## Phase 2 — Component Architecture

Structure every output with named, documented component sections — even in single-file outputs.

### Component Comment Format

```html
<!-- ═══════════════════════════════════════
     COMPONENT: NavigationBar
     PURPOSE: Primary site navigation with mobile hamburger
     STATES: default, scrolled, mobile-open
     BREAKPOINTS: mobile-first, expands at 768px
     ═══════════════════════════════════════ -->
```

### Component Naming Convention
- Semantic HTML elements first (`<nav>`, `<main>`, `<aside>`, `<article>`, `<section>`)
- BEM-inspired class naming: `.component`, `.component__element`, `.component--modifier`
- State classes: `.is-active`, `.is-loading`, `.is-disabled`, `.is-error`, `.is-success`

### Required Component States

Every interactive element MUST have all 5 states styled:

```css
/* ─── BUTTON: All 5 States ─── */
.btn {
  background: var(--color-brand-primary);
  color: var(--color-text-inverse);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
  position: relative;
  overflow: hidden;
}

/* 1. HOVER */
.btn:hover {
  background: var(--color-brand-primary-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* 2. FOCUS (keyboard accessibility) */
.btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}

/* 3. ACTIVE (pressed) */
.btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: var(--shadow-xs);
}

/* 4. LOADING */
.btn.is-loading {
  pointer-events: none;
  opacity: 0.8;
}
.btn.is-loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* 5. DISABLED */
.btn:disabled, .btn.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## Phase 3 — Motion Language

### Motion Principles
1. **GPU-only properties** — ONLY animate `transform` and `opacity`. Never animate `width`, `height`, `top`, `left`, `margin`, `padding`, `border`, or `box-shadow` directly (box-shadow can use a pseudo-element with opacity).
2. **Meaningful motion** — Every animation communicates something: entry direction shows origin, exit direction shows destination, scale shows importance.
3. **Choreographed sequences** — Elements enter in a deliberate order using stagger delays, not all at once.
4. **Reduced motion respect** — Always include `prefers-reduced-motion` override.

### State Transition Choreography

```css
/* ─── Skeleton → Loaded transition ─── */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 25%,
    var(--color-bg-secondary) 50%,
    var(--color-bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton.is-loaded {
  animation: fadeIn var(--duration-normal) var(--ease-out) forwards;
}

/* ─── Enter animations (staggered) ─── */
.stagger-enter > * {
  opacity: 0;
  transform: translateY(12px);
  animation: slideUp var(--duration-slow) var(--ease-out) forwards;
}

.stagger-enter > *:nth-child(1) { animation-delay: 0ms; }
.stagger-enter > *:nth-child(2) { animation-delay: 80ms; }
.stagger-enter > *:nth-child(3) { animation-delay: 160ms; }
.stagger-enter > *:nth-child(4) { animation-delay: 240ms; }
.stagger-enter > *:nth-child(5) { animation-delay: 320ms; }
.stagger-enter > *:nth-child(6) { animation-delay: 400ms; }

@keyframes slideUp {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ─── Spring-feel overshoot for interactive elements ─── */
.spring-pop {
  transition: transform var(--duration-normal) var(--ease-spring);
}
.spring-pop:hover {
  transform: scale(1.05);
}
.spring-pop:active {
  transform: scale(0.95);
  transition-duration: var(--duration-instant);
}

/* ─── Scroll-driven fade-in (Intersection Observer) ─── */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity var(--duration-slow) var(--ease-out),
              transform var(--duration-slow) var(--ease-out);
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Scroll Reveal JavaScript (lightweight)

```javascript
// Intersection Observer for scroll-driven reveals
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target); // Fire once
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

### Reduced Motion Override (REQUIRED)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .skeleton { animation: none; }
  .reveal { opacity: 1; transform: none; }
  .stagger-enter > * { opacity: 1; transform: none; animation: none; }
}
```

---

## Phase 4 — Responsive Architecture

### Mobile-First Breakpoint System

```css
/* ─── Base: 375px (mobile) — write all base styles here ─── */

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }

/* Wide */
@media (min-width: 1440px) { }
```

### Layout Patterns

```css
/* ─── Responsive grid: 1 → 2 → 3 columns ─── */
.grid-auto {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-6);
}

@media (min-width: 768px) {
  .grid-auto { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid-auto { grid-template-columns: repeat(3, 1fr); }
}

/* ─── Container with auto margins ─── */
.container {
  width: 100%;
  max-width: var(--container-xl);
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 768px) {
  .container { padding-inline: var(--space-8); }
}

@media (min-width: 1440px) {
  .container { padding-inline: var(--space-12); }
}
```

### Touch Targets

```css
/* Minimum 44x44px touch targets on mobile */
@media (pointer: coarse) {
  button, a, input, select, textarea, [role="button"] {
    min-height: 44px;
    min-width: 44px;
  }
}
```

---

## Phase 5 — Accessibility (WCAG AA Minimum)

### Required for Every Output

1. **Semantic HTML** — Use `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<footer>`. Never use `<div>` where a semantic element works.

2. **ARIA attributes** — Every interactive element:
   ```html
   <button aria-label="Close dialog" aria-expanded="false">
   <nav aria-label="Main navigation">
   <div role="alert" aria-live="polite">
   <dialog aria-modal="true" aria-labelledby="dialog-title">
   ```

3. **Focus management**:
   ```css
   /* Visible focus ring for keyboard users */
   :focus-visible {
     outline: 2px solid var(--color-border-focus);
     outline-offset: 2px;
   }

   /* Remove focus ring for mouse users */
   :focus:not(:focus-visible) {
     outline: none;
   }
   ```

4. **Color contrast** — Minimum ratios:
   - Normal text: 4.5:1 against background
   - Large text (18px+ or 14px+ bold): 3:1
   - UI components/icons: 3:1
   - Never rely on color alone to convey information

5. **Keyboard navigation** — All functionality must be operable via keyboard:
   - Tab order follows visual order
   - Escape closes modals/dropdowns
   - Arrow keys navigate within grouped controls
   - Enter/Space activates buttons

6. **Screen reader text**:
   ```css
   .sr-only {
     position: absolute;
     width: 1px;
     height: 1px;
     padding: 0;
     margin: -1px;
     overflow: hidden;
     clip: rect(0, 0, 0, 0);
     white-space: nowrap;
     border-width: 0;
   }
   ```

7. **Skip link** (for page-level outputs):
   ```html
   <a href="#main-content" class="skip-link">Skip to main content</a>
   ```
   ```css
   .skip-link {
     position: absolute;
     top: -100%;
     left: var(--space-4);
     z-index: var(--z-tooltip);
     padding: var(--space-2) var(--space-4);
     background: var(--color-brand-primary);
     color: var(--color-text-inverse);
     border-radius: var(--radius-md);
     transition: top var(--duration-fast) var(--ease-out);
   }
   .skip-link:focus {
     top: var(--space-4);
   }
   ```

---

## Phase 6 — Performance Rules

### Hard Rules
1. **GPU-composited animations ONLY** — `transform` and `opacity`. Never animate layout-triggering properties.
2. **No layout thrash** — Never read then write DOM geometry in a loop. Batch reads, then batch writes.
3. **`will-change` sparingly** — Only on elements about to animate, remove after.
4. **Lazy load images** — Always use `loading="lazy"` and `decoding="async"` on images below the fold.
5. **`font-display: swap`** — Never let custom fonts block rendering.
6. **No render-blocking JS** — Use `defer` or `type="module"` on all scripts.
7. **Critical CSS inline** — For landing pages, inline above-the-fold CSS.
8. **Image sizing** — Always set explicit `width` and `height` attributes to prevent layout shift (CLS).

```html
<img src="hero.jpg" alt="Dashboard preview" width="1200" height="800"
     loading="lazy" decoding="async">
```

```css
@font-face {
  font-family: 'Inter';
  src: url('inter.woff2') format('woff2');
  font-display: swap;
}
```

---

## Phase 7 — Microcopy Standards

### Rules
1. **NEVER use "Lorem ipsum"** — Write real, contextually appropriate text.
2. **NEVER use generic placeholders** like "Button text", "Title here", "Description goes here."
3. **Write action-oriented CTAs** — "Start free trial" not "Submit". "See your results" not "Click here."
4. **Microcopy communicates state:**
   - Empty state: "No projects yet. Create your first one to get started."
   - Loading: "Pulling your latest data..."
   - Error: "Something went wrong loading your projects. Try refreshing the page."
   - Success: "Project created! You're ready to start building."
5. **Use sentence case** for UI text (not Title Case or ALL CAPS).
6. **Be specific** — "Save 3 hours per week" not "Save time."

### Placeholder Data Examples

```javascript
// Use realistic sample data
const sampleUsers = [
  { name: 'Sarah Chen', role: 'Product Designer', avatar: '👩‍🎨' },
  { name: 'Marcus Johnson', role: 'Frontend Engineer', avatar: '👨‍💻' },
  { name: 'Priya Sharma', role: 'Marketing Lead', avatar: '👩‍💼' },
];

const sampleMetrics = [
  { label: 'Active users', value: '2,847', change: '+12.3%', trend: 'up' },
  { label: 'Revenue', value: '$48,290', change: '+8.1%', trend: 'up' },
  { label: 'Bounce rate', value: '32.4%', change: '-2.7%', trend: 'down' },
];
```

---

## Output Checklist

Before delivering ANY UI output, verify:

| # | Check | Required |
|---|-------|----------|
| 1 | UX audit comment block at top | Always |
| 2 | CSS custom property design tokens | Always |
| 3 | Dark mode via `prefers-color-scheme` + `[data-theme]` | Always |
| 4 | No-flash dark mode `<script>` in `<head>` | Page-level only |
| 5 | Named component sections with comment headers | Always |
| 6 | All 5 interaction states (hover, focus, active, loading, disabled) | All interactive elements |
| 7 | Mobile-first CSS (base=375px, breakpoints at 768/1024/1440) | Always |
| 8 | `prefers-reduced-motion` override | When animations present |
| 9 | Semantic HTML (`<nav>`, `<main>`, `<section>`, etc.) | Always |
| 10 | ARIA labels on interactive elements | Always |
| 11 | Focus-visible styles | Always |
| 12 | 44px minimum touch targets on mobile | Always |
| 13 | `loading="lazy"` on below-fold images | When images present |
| 14 | No magic numbers — all values from tokens | Always |
| 15 | No Lorem ipsum — real microcopy | Always |
| 16 | GPU-only animations (`transform`/`opacity`) | When animations present |
| 17 | `font-display: swap` on custom fonts | When custom fonts used |
| 18 | Skip link for page-level outputs | Full pages only |
| 19 | Screen reader `.sr-only` utility available | Always |
| 20 | Color contrast meets WCAG AA (4.5:1 text, 3:1 UI) | Always |

---

## Known Pitfalls

1. **Flash of unstyled dark mode** — If you forget the no-flash `<script>` in the `<head>`, users on dark mode will see a white flash on every page load. Always include it.

2. **Animating box-shadow directly** — This triggers paint on every frame. Instead, animate a `::before` pseudo-element's `opacity` with the shadow pre-applied.

3. **Forgetting `:focus-visible`** — Using `:focus` alone shows focus rings on mouse click. Always use `:focus-visible` for keyboard-only focus indication, with `:focus:not(:focus-visible)` to suppress mouse rings.

4. **Magic number spacing** — `padding: 13px 27px` is a red flag. Every value should trace back to a design token. If 13px is needed, it's a sign the grid isn't right.

5. **Desktop-first CSS** — Writing `max-width` media queries instead of `min-width` leads to override cascades and specificity wars. Always start mobile, build up.

6. **Missing empty states** — A list with 0 items should never show a blank void. Design the empty state with an illustration, message, and CTA.

7. **Color-only status indicators** — Red/green for error/success fails for colorblind users. Always pair color with an icon, text, or pattern.

8. **`z-index: 99999`** — Use the z-index scale from tokens. If you need 99999, the stacking context is broken.

9. **Non-composited animations on scroll** — `position: sticky` + `box-shadow` change on scroll = jank. Use `transform` and `opacity` changes triggered by Intersection Observer instead.

10. **Forgetting `prefers-reduced-motion`** — Vestibular disorders are real. Always provide the reduced-motion media query that kills all animation.

11. **Images without dimensions** — Missing `width`/`height` on `<img>` tags causes layout shift (bad CLS score). Always set explicit dimensions.

12. **Touch targets under 44px** — Buttons that are fine with a mouse cursor are impossible to tap accurately on mobile. Enforce minimum touch targets.

---

## Quick Reference

| Concept | Token/Pattern |
|---------|--------------|
| Spacing | `--space-{1-24}` (4px grid) |
| Type | `--text-{xs-6xl}` (Major Third scale) |
| Color | `--color-{bg/text/brand/semantic/border}-{name}` |
| Shadow | `--shadow-{xs-2xl/inner/focus}` |
| Radius | `--radius-{sm-full}` |
| Z-index | `--z-{base/dropdown/sticky/overlay/modal/popover/toast/tooltip}` |
| Easing | `--ease-{default/in/out/spring/elastic}` |
| Duration | `--duration-{instant/fast/normal/slow/slower}` |
| Breakpoints | 375px (base) → 768px → 1024px → 1440px |
| Touch target | 44x44px minimum |
| Contrast | 4.5:1 text, 3:1 UI components |
| Animation | `transform` + `opacity` ONLY |
