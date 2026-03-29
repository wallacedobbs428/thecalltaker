# Spline.design Research — The Call Taker Website Redesign

> Research completed Feb 27, 2026. Brutally honest assessment for a two-person team shipping fast.

---

## STEP 1: WHAT IS SPLINE AND WHAT CAN WE DO WITH IT

### What does Spline actually output?

**Web Exports (embedding):**
- **Public URL** — hosted on `my.spline.design/...`, embed via iframe
- **`<spline-viewer>`** — web component, loaded via CDN script tag (no build step)
- **Code Export** — Vanilla JS, React, Next.js, Three.js, react-three-fiber (.zip files)

**3D Model Exports:**
- GLTF/GLB (free plan)
- USDZ (Apple AR — Pro plan only, $25/mo)
- STL (3D printing — Pro plan only)

**Other:** Image sequences (JPG/PNG), native iOS/Android embeds

### Can Spline scenes be embedded on a static HTML site (GitHub Pages)?

**YES. Two methods:**

**Method A: iframe (simplest, free plan)**
```html
<iframe src="https://my.spline.design/YOUR-SCENE-ID/"
        frameborder="0" width="100%" height="500px"></iframe>
```

**Method B: `<spline-viewer>` web component (recommended, free plan)**
```html
<script type="module" src="https://unpkg.com/@splinetool/viewer/build/spline-viewer.js"></script>
<spline-viewer url="https://prod.spline.design/YOUR-SCENE/scene.splinecode"></spline-viewer>
```

Both work on GitHub Pages. No server-side rendering needed.

**Free plan caveat:** Both show a "Built in Spline" watermark. Removing it = $15/mo (Starter plan).

### Can Spline scenes be embedded in React/Next.js?

**YES.** Dedicated packages exist:
```jsx
import Spline from '@splinetool/react-spline';       // React
import Spline from '@splinetool/react-spline/next';  // Next.js (SSR support)
```

### What's the Spline web player? Bundle size?

| Package | Minified | Gzipped | What it is |
|---------|----------|---------|-----------|
| `@splinetool/runtime` | 1.92 MB | 546 KB | Core engine (Vanilla JS) |
| `@splinetool/react-spline` | 3.9 KB | 1.9 KB | React wrapper (+ runtime as dep) |
| `@splinetool/viewer` | 2.24 MB | 631 KB | `<spline-viewer>` web component |
| `@splinetool/loader` | 834 KB | 225 KB | Three.js loader |

**For comparison:** React itself is ~45 KB gzipped. The Spline runtime is **12x heavier than React.**

Scene files (`.splinecode`) add additional weight on top — varies by complexity (textures, geometry).

### Does Spline have an API or CLI?

**No official REST API. No CLI.** You cannot create scenes programmatically.

What exists:
- **Runtime API** — JavaScript control of exported scenes (find objects, trigger animations, change properties)
- **Real-time API** — Spline scenes calling YOUR APIs (triggered by in-scene events)
- **MCP Server** (community/experimental) — `aydinfer/spline-mcp-server` on GitHub. Lets AI agents create/modify objects through MCP protocol. Experimental.

### Can Claude Code create Spline scenes?

**NO.** Scenes MUST be designed in the Spline web editor (or desktop app).

Claude Code CAN:
- Write all embed code (iframe, viewer, React components)
- Write JavaScript that controls exported scenes (position, rotation, animation triggers)
- Build scroll-driven interactions around Spline scenes
- Handle the entire website layout around the 3D elements

### npm Package Ecosystem

| Package | Weekly Downloads | Version | Purpose |
|---------|-----------------|---------|---------|
| `@splinetool/runtime` | ~190K | 1.12.61 | Core rendering engine |
| `@splinetool/react-spline` | ~92K | 4.1.0 | React/Next.js component |
| `@splinetool/viewer` | ~25K | 1.12.61 | Web component (`<spline-viewer>`) |
| `@splinetool/loader` | ~2.4K | 1.12.61 | Three.js scene loader |
| `@splinetool/r3f-spline` | ~500 | 1.0.2 | React Three Fiber hook (stale) |

**JavaScript interaction is FULL:**
```javascript
// Find and manipulate objects
const cube = spline.findObjectByName('Cube');
cube.position.x = 100;
cube.scale.y = 2;

// Trigger animations defined in Spline editor
spline.emitEvent('mouseHover', 'Cube');
spline.emitEventReverse('mouseHover', 'Cube');

// Listen for events
spline.addEventListener('mouseDown', (e) => {
  console.log('Clicked:', e.target.name);
});

// Camera control
spline.setZoom(1.5);
```

Supported events: `mouseDown`, `mouseUp`, `mouseHover`, `keyDown`, `keyUp`, `start`, `lookAt`, `follow`, `scroll`, `collision`

### Spline Pricing

| Feature | Free | Starter ($15/mo) | Professional ($25/mo) |
|---------|------|-------------------|----------------------|
| Web exports | With watermark | No watermark | No watermark |
| Code exports (React/JS) | NO | NO | YES |
| GLTF/GLB export | YES | YES | YES |
| Remove branding | NO | YES | YES |
| AI credits | None | None | 2000/mo |

**Bottom line:** Free plan works for testing. $15/mo removes watermark. $25/mo for code exports (React, Vanilla JS downloads).

---

## STEP 2: WHAT CLAUDE CODE CAN AUTOMATE vs WHAT'S MANUAL

### CLAUDE CODE HANDLES (100% automated):

| Task | How |
|------|-----|
| Embedding Spline scenes into the site | Write iframe / `<spline-viewer>` / React component code |
| Swapping/updating scene URLs | Find-and-replace in HTML/JS |
| Building entire website layout | HTML, CSS, JavaScript |
| Scroll-triggered animations around scenes | GSAP ScrollTrigger + Spline runtime API |
| Click/hover interactions with scenes | `spline.emitEvent()` via runtime API |
| Lazy-loading scenes for performance | IntersectionObserver + dynamic import |
| Mobile responsive layout around scenes | CSS media queries, container sizing |
| All non-3D page elements | Headers, pricing cards, testimonials, forms, CTAs |
| Performance optimization | Gzip, lazy load, intrinsic dimensions, code splitting |
| Integration with GSAP/Lottie/CSS animations | Full code control |

### WALLACE HANDLES (in the Spline editor):

| Task | Why |
|------|-----|
| Designing the actual 3D scenes/models | No API to create scenes programmatically |
| Setting up lighting, camera angles, materials | Visual design decisions |
| Creating animations within Spline | Timeline/state machine is in the editor |
| Naming objects for JS interaction | Claude needs `findObjectByName('Phone')` targets |
| Setting up scroll events in the editor | Spline's scroll event system is editor-based |
| Exporting/publishing scenes | Click "Export" in Spline editor |
| Choosing geometry quality for export | Performance vs visual tradeoff |

### THE SPLIT:

> **Wallace:** Design 1-2 scenes in Spline (2-4 hours in the editor)
> **Claude Code:** Build the entire website around those scenes (layout, animations, interactions, mobile, performance)

---

## STEP 3: FEASIBILITY FOR OUR SITE

### 1. Can we keep GitHub Pages?

**YES.** Spline works perfectly on static HTML. No server needed. Our GitHub Pages setup works fine.

### 2. Will Spline make the site too slow on mobile?

**It CAN if we're not careful.** Real data:

| Metric | Without Spline | With Spline (unoptimized) | With Spline (optimized) |
|--------|---------------|---------------------------|------------------------|
| Lighthouse Score | 90+ | 30-40 | 80-90 |
| First Load | < 1s | 6.5s | 1.2s |
| Time to Interactive | < 1s | 5.3s | 0.8s |
| JS Payload | ~50 KB | ~2.5 MB+ | ~546 KB (gzipped, lazy) |

**The key is lazy-loading.** One case study went from Lighthouse 30 to 90 just by lazy-loading Spline assets with IntersectionObserver.

### 3. Performance impact summary

- Runtime JS: **546 KB gzipped** (heavy but manageable with lazy load)
- Scene files: **varies** (keep scenes simple = small files)
- CPU time: A simple scene consumed **17.9 seconds of CPU** on desktop
- CLS risk: Canvas loading can push content around (fix with intrinsic dimensions)
- Battery drain on mobile: Yes, WebGL + continuous rendering is battery-hungry

### 4. Do Spline embeds work on mobile browsers?

**YES.** Spline uses WebGL, supported on Safari iOS 15.6+, Chrome Mobile, all modern browsers.

**BUT:** Older/budget phones (2-3 years old) will stutter. Complex scenes cause jank and battery drain. Must test on real devices.

### 5. Best Spline websites (SaaS/service businesses)

| Website | Industry | How They Use Spline |
|---------|----------|-------------------|
| **Scale AI** (scale.com) | Enterprise AI ($13B+) | 3D brand elements throughout site |
| **Resend** (resend.com) | Developer email API | Interactive 3D visuals, subtle depth |
| **Polaroid I-2** (polaroid.com) | Consumer electronics | Full 3D product showcase, rotate/zoom |
| **Lu.ma** (lu.ma) | Event management SaaS | Product UI animations, light/dark modes |
| **Alloy** (runalloy.com) | B2B integrations API | 3D brand elements and visual identity |
| **Fortra** (fortra.com) | Enterprise cybersecurity | 3D content for AI defense platform |
| **Forbes Legacy Pass** | Media/NFT | Interactive 3D NFT card showcase |
| **Oscilar** | Fintech risk platform | Abstract 3D hero branding |
| **Ori Scan** (KOJI Global) | Dental technology | 3D product exploration (relevant — service biz!) |

**Common pattern:** 80%+ of successful sites use Spline in the **hero section only**. One high-impact element, not scattered throughout.

---

## STEP 4: RECOMMENDATION

## OPTION C: HYBRID (RECOMMENDED)

**Use Spline for ONE hero element. Build everything else with code.**

This is the right answer for a two-person team shipping fast. Here's why:

### Why NOT Option A (Full Spline):
- Multiple Spline embeds = slow mobile performance
- Wallace would need to spend 10-20 hours learning Spline AND designing multiple scenes
- You're selling to locksmith and HVAC owners. They care about "does this work?" not "wow nice 3D"
- Every hour in Spline is an hour not closing deals

### Why NOT Option B (Skip Spline entirely):
- A single 3D hero element IS a meaningful differentiator
- It makes thecalltaker.com look like a $50K website instead of a template
- Locksmith/HVAC owners compare you to competitors — first impression matters
- Spline is legitimately easy to learn for one simple scene

### THE HYBRID PLAN:

#### What Wallace builds in Spline (2-3 hours):
**ONE scene:** A 3D phone/device that shows "incoming call" animation → phone answers → shows the AI conversation flowing. Think: a floating iPhone with a pulsing call screen.

Why a phone:
- Instantly communicates "we answer your calls"
- Every locksmith/HVAC owner understands a ringing phone
- Simple to build (one object + one animation)
- High impact, low complexity

**Design tips for the scene:**
- Keep it LOW POLY (less geometry = faster load)
- Compress textures
- Use "Performance" quality on export
- Name the phone object (e.g., "Phone") so Claude can trigger animations via JS
- Set up a scroll event so the phone rotates as users scroll
- Export via Public URL or download `.splinecode`

#### What Claude Code builds (everything else):

**Premium animations WITHOUT Spline:**

| Element | Tool | Performance Cost |
|---------|------|-----------------|
| Scroll-triggered section reveals | GSAP ScrollTrigger | ~30 KB (tiny) |
| Number counters (calls answered, revenue saved) | GSAP + CSS | ~0 KB extra |
| Floating/parallax background elements | CSS transforms + GSAP | ~0 KB extra |
| Card hover effects (3D tilt) | CSS `perspective` + `transform3d` | 0 KB |
| Smooth page transitions | GSAP | Already loaded |
| Gradient animations (hero background) | CSS `@keyframes` | 0 KB |
| Text reveal animations | GSAP SplitText or CSS | Minimal |
| Testimonial carousel with 3D flip | CSS 3D transforms | 0 KB |
| CTA button micro-animations | CSS transitions | 0 KB |

**Total JS for all non-Spline animations: ~30 KB** (GSAP core). Compare to Spline's 546 KB per scene.

**The full page structure:**

```
HERO SECTION
├── Left: Headline + subheadline + CTA button
├── Right: Spline 3D phone scene (lazy-loaded)
└── Background: CSS gradient animation

SOCIAL PROOF BAR
├── "500+ calls answered" counter (GSAP)
├── Industry logos
└── Star ratings

HOW IT WORKS (3 steps)
├── Step cards with CSS 3D hover tilt
├── GSAP scroll-triggered reveal
└── Icons or Lottie micro-animations

PRICING SECTION
├── Locksmith Basic ($197) / Pro ($297)
├── Card hover effects (CSS perspective)
├── "Subscribe Now" → Stripe Checkout
└── GSAP entrance animation

DEMO SECTION
├── "Call our demo line" CTA
├── Phone number: (629) 269-9697
├── Audio waveform animation (CSS/Canvas)
└── GSAP scroll-triggered

TESTIMONIALS
├── 3D card flip carousel (CSS transforms)
├── Real case study quotes
└── Star ratings

FOOTER + CTA
├── Final "Get Started" CTA
├── Sticky bottom bar on mobile
└── Links to industry pages
```

### Tech Stack:
- **HTML/CSS/JS** — static files on GitHub Pages (no change)
- **GSAP** (30 KB) — scroll animations, number counters, reveals
- **Spline Viewer** (546 KB, lazy-loaded) — ONE hero scene only
- **CSS 3D transforms** — card effects, hover states (0 KB)
- **No React, no build step, no bundler** — keeps it simple

### Performance Budget:
| Asset | Size (gzipped) | Load Strategy |
|-------|----------------|---------------|
| HTML + CSS | ~30 KB | Immediate |
| GSAP | ~30 KB | Immediate |
| Spline Viewer + Scene | ~600-800 KB | Lazy (IntersectionObserver) |
| Images | ~200 KB | Lazy |
| **Total** | **~900 KB - 1.1 MB** | Staggered |

With lazy-loading, initial page load stays under 100 KB. Spline loads only when hero scrolls into view (or on desktop, after DOM ready). Mobile Lighthouse should stay 80+.

### What Wallace needs to do:
1. Go to spline.design and create a free account (10 min)
2. Watch one tutorial on making a simple object + animation (30 min)
3. Build ONE phone scene with a call animation (1-2 hours)
4. Export as Public URL or download `.splinecode`
5. Give Claude the URL → Claude handles everything else

### What Claude Code does:
1. Builds the entire website layout (HTML/CSS)
2. Adds GSAP scroll animations throughout
3. Embeds the Spline scene in the hero (lazy-loaded)
4. Wires up JS interaction (hover effects, scroll-driven rotation)
5. Builds the pricing page with Stripe Checkout links
6. Optimizes for mobile (responsive, performance, CLS prevention)
7. Deploys to GitHub Pages

### Alternative if Wallace doesn't want to learn Spline:

Skip the 3D phone entirely. Use GSAP + CSS to build a **premium animated hero** instead:
- Floating phone mockup (2D image with parallax + shadow)
- Animated "call incoming" overlay (CSS animations)
- Pulsing ring effect (CSS keyframes)
- Text typewriter effect showing AI conversation

This gets 80% of the visual impact with 0% Spline learning curve. Claude Code builds it all.

---

## ALTERNATIVES REFERENCE (if we go full code-only)

| Tool | Size | Best For | Code-Only? |
|------|------|----------|-----------|
| **GSAP + ScrollTrigger** | 30 KB | Scroll animations, parallax, reveals | YES |
| **CSS 3D transforms** | 0 KB | Card tilts, flips, perspective effects | YES |
| **Lottie** | 60-250 KB | 2D vector animations, icons | Runtime yes, creation needs After Effects |
| **Rive** | 2-25 KB per animation | Interactive micro-animations | Runtime yes, creation needs Rive editor |
| **Three.js** | 150 KB+ | Full custom 3D (overkill for us) | YES |
| **CSS `@keyframes`** | 0 KB | Gradients, pulsing, floating | YES |

**Sites that look premium WITHOUT Spline:** Linear.app, Stripe.com, Vercel.com — all use GSAP + CSS primarily.

---

## FINAL VERDICT

**Go hybrid (Option C).** One Spline scene in the hero, GSAP + CSS everywhere else.

But if you're in a rush to ship: skip Spline entirely, go full GSAP + CSS, and add a Spline hero later when you have time. The GSAP-only version will still look better than 95% of locksmith/HVAC websites.

**Your competition isn't Stripe.com — it's Bob's HVAC with a GoDaddy template.** Even basic GSAP animations will blow them away.

---

*Sources: Spline docs, npmjs.com, Bundlephobia, Envato Tuts+, DEV Community performance case studies, Spline official customers page, Aircada Three.js comparison, Callstack Lottie vs Rive analysis*
