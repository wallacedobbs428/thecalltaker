---
name: shadcn-ui
description: "Build modern UI components with shadcn/ui patterns, Tailwind CSS, and Radix primitives. Use when creating accessible, composable UI components, design systems, or when the user wants polished, production-ready interface elements. Covers component patterns, dark mode, animations, and accessibility."
category: frontend
---

# shadcn/ui — Modern Component Patterns

Build accessible, composable UI components using Tailwind CSS utility patterns inspired by shadcn/ui.

---

## Core Design Tokens

```css
:root {
  /* Colors — HSL for easy theme switching */
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  --card: 0 0% 100%;
  --card-foreground: 0 0% 3.9%;
  --primary: 24 95% 53%;          /* Orange for The Call Taker */
  --primary-foreground: 0 0% 100%;
  --secondary: 0 0% 96.1%;
  --secondary-foreground: 0 0% 9%;
  --muted: 0 0% 96.1%;
  --muted-foreground: 0 0% 45.1%;
  --accent: 0 0% 96.1%;
  --accent-foreground: 0 0% 9%;
  --destructive: 0 84.2% 60.2%;
  --border: 0 0% 89.8%;
  --ring: 24 95% 53%;
  --radius: 0.5rem;
}

.dark {
  --background: 0 0% 3.9%;
  --foreground: 0 0% 98%;
  --card: 0 0% 3.9%;
  --card-foreground: 0 0% 98%;
  --primary: 24 95% 53%;
  --primary-foreground: 0 0% 100%;
  --secondary: 0 0% 14.9%;
  --secondary-foreground: 0 0% 98%;
  --muted: 0 0% 14.9%;
  --muted-foreground: 0 0% 63.9%;
  --border: 0 0% 14.9%;
}
```

---

## Component Patterns

### Button Variants
```html
<!-- Primary -->
<button class="inline-flex items-center justify-center rounded-md text-sm font-medium
  bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]
  hover:bg-[hsl(var(--primary))]/90 h-10 px-4 py-2
  transition-colors focus-visible:outline-none focus-visible:ring-2
  focus-visible:ring-[hsl(var(--ring))] disabled:pointer-events-none disabled:opacity-50">
  Start Free Pilot
</button>

<!-- Secondary / Outline -->
<button class="inline-flex items-center justify-center rounded-md text-sm font-medium
  border border-[hsl(var(--border))] bg-transparent
  hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--accent-foreground))]
  h-10 px-4 py-2 transition-colors">
  Learn More
</button>

<!-- Ghost -->
<button class="inline-flex items-center justify-center rounded-md text-sm font-medium
  hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--accent-foreground))]
  h-10 px-4 py-2 transition-colors">
  Cancel
</button>
```

### Card
```html
<div class="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))]
  text-[hsl(var(--card-foreground))] shadow-sm">
  <div class="flex flex-col space-y-1.5 p-6">
    <h3 class="text-2xl font-semibold leading-none tracking-tight">Pro Plan</h3>
    <p class="text-sm text-[hsl(var(--muted-foreground))]">24/7 AI receptionist</p>
  </div>
  <div class="p-6 pt-0">
    <p class="text-4xl font-bold">$297<span class="text-sm font-normal text-[hsl(var(--muted-foreground))]">/mo</span></p>
  </div>
  <div class="flex items-center p-6 pt-0">
    <button class="w-full rounded-md bg-[hsl(var(--primary))] text-white h-10 px-4">
      Get Started
    </button>
  </div>
</div>
```

### Badge
```html
<!-- Default -->
<span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold
  transition-colors border-transparent bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
  New
</span>

<!-- Outline -->
<span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold
  text-[hsl(var(--foreground))]">
  HVAC
</span>

<!-- Success -->
<span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold
  border-transparent bg-green-500/10 text-green-500">
  Active
</span>
```

### Input
```html
<div class="space-y-2">
  <label class="text-sm font-medium leading-none" for="email">Email</label>
  <input type="email" id="email" placeholder="john@company.com"
    class="flex h-10 w-full rounded-md border border-[hsl(var(--border))]
    bg-[hsl(var(--background))] px-3 py-2 text-sm
    placeholder:text-[hsl(var(--muted-foreground))]
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]
    disabled:cursor-not-allowed disabled:opacity-50">
</div>
```

### Dialog/Modal
```html
<div class="fixed inset-0 z-50 bg-black/80" id="overlay"></div>
<div class="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%]
  border border-[hsl(var(--border))] bg-[hsl(var(--background))] p-6 shadow-lg rounded-lg"
  role="dialog" aria-modal="true">
  <div class="flex flex-col space-y-1.5 text-center sm:text-left">
    <h2 class="text-lg font-semibold">Start Your Free Pilot</h2>
    <p class="text-sm text-[hsl(var(--muted-foreground))]">14 days free, no credit card.</p>
  </div>
  <div class="mt-4">
    <!-- Form content -->
  </div>
  <div class="mt-6 flex justify-end space-x-2">
    <button class="rounded-md border px-4 py-2 text-sm" onclick="closeDialog()">Cancel</button>
    <button class="rounded-md bg-[hsl(var(--primary))] text-white px-4 py-2 text-sm">Submit</button>
  </div>
</div>
```

---

## Accessibility Checklist

Every component must have:
- [ ] Proper `role` attributes (dialog, button, etc.)
- [ ] `aria-label` or `aria-labelledby` for non-text elements
- [ ] `aria-expanded` for toggleable elements
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus management (trap focus in modals)
- [ ] Color contrast ratio >= 4.5:1
- [ ] `disabled` state styling
- [ ] Screen reader announcements for dynamic content

---

## Animation Patterns

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Scale in (for modals) */
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-in { animation: fadeIn 0.2s ease-out; }
.animate-slide-up { animation: slideUp 0.3s ease-out; }
.animate-scale-in { animation: scaleIn 0.2s ease-out; }
```
