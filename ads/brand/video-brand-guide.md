# The Call Taker — Video Ad Brand Guide

> Last updated: 2026-03-18
> Standard: Every frame must feel like Apple made it for a startup.

---

## 1. Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary Background | `#0a0a0a` | All dark scenes, overlays, lower thirds |
| Primary Accent | `#00dc82` | CTAs, stat numbers, highlight text, progress bars |
| Secondary Accent | `#00a8ff` | Supporting info, secondary badges, trust elements |
| Danger/Pain | `#ef4444` | Missed call stats, money lost, negative contrast |
| Text Primary | `#ffffff` | Headlines, hook text, hero copy |
| Text Secondary | `#a3a3a3` | Subtext, descriptions, fine print |
| Pure Black | `#000000` | Letterboxing, fade-ins, backgrounds |

### Color Rules
- Pain/problem scenes: lean into `#ef4444` (red) tones
- Solution/result scenes: transition to `#00dc82` (green)
- Never use both red and green simultaneously — always sequential contrast
- Green glow: `0 0 40px rgba(0,220,130,0.3)` on key elements

---

## 2. Typography

| Element | Font | Weight | Size (1080px wide) |
|---------|------|--------|---------------------|
| Hook Text (sec 0-3) | Inter | 900 (Black) | 80-96px |
| Stat Numbers | Inter | 800 (ExtraBold) | 72-80px |
| Body/Subtitle | Inter | 600 (SemiBold) | 48-56px |
| Caption Text | Inter | 700 (Bold) | 40-44px |
| Fine Print / Labels | Inter | 500 (Medium) | 32-36px |
| CTA Button Text | Inter | 800 (ExtraBold) | 52-60px |

### Typography Rules
- ALL text overlays must have a **black shadow** or **dark backdrop blur** for readability
- Text shadow: `2px 2px 8px rgba(0,0,0,0.8)` minimum
- Stat numbers always in `#00dc82` or `#ef4444` (never white)
- Hook text: centered, full width, max 6 words
- Never use more than 2 text elements on screen simultaneously

---

## 3. Text Overlay Positioning

### 9:16 Vertical (1080x1920 — Reels/Stories)

```
┌──────────────────────┐
│                      │  ← Safe zone top (120px from top)
│                      │     App UI covers this area
│                      │
│    ┌──────────┐      │
│    │ HOOK TEXT │      │  ← Center-aligned, y: 400-600px
│    │  80-96px │      │
│    └──────────┘      │
│                      │
│                      │
│    ┌──────────┐      │
│    │STAT/BODY │      │  ← Lower third, y: 1200-1400px
│    │ 48-72px  │      │
│    └──────────┘      │
│                      │
│    ┌──────────┐      │
│    │   CTA    │      │  ← CTA bar, y: 1600-1720px
│    │ FULL BAR │      │     80px tall, full width - 40px padding
│    └──────────┘      │
│                      │  ← Bottom safe zone (200px from bottom)
│                      │     Instagram nav covers this
└──────────────────────┘
```

### 1:1 Square (1080x1080 — Feed)

```
┌──────────────────────┐
│                      │
│    ┌──────────┐      │
│    │ HOOK TEXT │      │  ← Upper third, y: 180-320px
│    └──────────┘      │
│                      │
│    [MAIN VISUAL]     │  ← Center, 500x500 area
│                      │
│    ┌──────────┐      │
│    │STAT/BODY │      │  ← Lower third, y: 760-880px
│    └──────────┘      │
│                      │
│    ┌──────────┐      │
│    │   CTA    │      │  ← Bottom bar, y: 940-1020px
│    └──────────┘      │
└──────────────────────┘
```

---

## 4. Caption Style (Alex Hormozi Method)

### Word-by-Word Highlight
- Captions appear at bottom center (safe zone above Instagram nav)
- Background: semi-transparent black pill (`rgba(0,0,0,0.7)`, `border-radius: 8px`)
- Font: Inter Bold, 44px, white
- **Active word** highlighted in `#00dc82` (green) — bold + scale 1.15x
- 3-4 words visible at a time, current word pops
- Timing: synced to voiceover, 0.1s ahead of audio for readability

### Caption Rules
- Always ON — 85% of mobile users watch without sound
- Position: 160px above bottom edge (above Instagram nav)
- Max width: 80% of frame width
- Line break at natural pauses — never mid-word

---

## 5. Video Structure Template

### The Perfect 30-Second Ad

| Second | Element | Visual | Audio |
|--------|---------|--------|-------|
| 0-1 | **BLACK + TEXT** | Pure black, single stat/question fades in | Silence or single sound effect |
| 1-3 | **HOOK** | Pattern interrupt visual (phone ringing, notification) | Hook sound (ding, ring, buzz) |
| 3-8 | **AGITATE** | Show the pain — missed call, empty desk, voicemail | Tense music builds, VO describes pain |
| 8-15 | **SOLUTION** | Gideon answering, appointment being booked | Music shifts positive, VO introduces product |
| 15-22 | **PROOF** | Stats on screen, before/after comparison | VO delivers numbers, music peaks |
| 22-27 | **OFFER** | Demo line number, pilot offer, pricing | VO: "Call this number right now" |
| 27-30 | **CTA** | Full-screen CTA bar, phone number, button | Music fades, VO: final directive |

---

## 6. Transition Style

- **Cut speed:** Fast cuts (0.5-1.5s per scene in hook, 2-4s in body)
- **Transition type:** Hard cuts only in first 5 seconds (urgency). Smooth crossfades in body.
- **Zoom:** Subtle 5-10% slow zoom on static scenes (Ken Burns effect)
- **Text animation:** Fade-up from bottom (0.3s ease-out). Never slide from sides.
- **Number counters:** Animate counting up (e.g., $0 → $1,200) over 1.5 seconds
- **Color transition:** Scene shifts from red-tinted (problem) → green-tinted (solution)

---

## 7. Music Direction

| Section | Genre | BPM | Energy |
|---------|-------|-----|--------|
| Hook (0-3s) | Silence / single SFX | — | Tension |
| Pain (3-8s) | Dark electronic / lo-fi tension | 80-100 | Building |
| Solution (8-20s) | Upbeat electronic / modern corporate | 110-130 | Rising |
| CTA (20-30s) | Peak energy then fade | 120-130 | Resolving |

### Music Rules
- **Royalty-free only** — use Artlist, Epidemic Sound, or Pixabay
- Music volume at 30% when voiceover is speaking
- Music peaks at visual transitions (sync cuts to beat)
- Fade out music at 25 seconds — last 5 seconds voice + CTA only
- No lyrics — instrumental only

---

## 8. Sound Effects Library

| SFX | Usage | Timing |
|-----|-------|--------|
| Phone ring (iPhone default) | Hook — missed call scenario | Second 0-2 |
| Notification ding | Gideon booking appointment | Solution reveal |
| Cash register "ka-ching" | Revenue stat reveal | Proof section |
| Whoosh | Text overlay entrance | Every text animation |
| Click/tap | CTA button appearance | Second 27 |
| Subtle bass drop | Stat number reveal | Pain numbers |

---

## 9. Logo & Branding Placement

### Rules
- **Logo NEVER appears in first 3 seconds** — hook must be brand-neutral
- Logo: bottom-right corner, 10% opacity watermark during body (seconds 5-25)
- Logo: full opacity, centered, final 3 seconds with CTA
- Logo format: "The Call Taker" wordmark in Inter Bold, white
- Accent dot: green `#00dc82` dot after "Taker"

### Demo Line Number
- Phone number: `(629) 269-9697`
- Always displayed in Inter Black, 72px minimum
- Green background bar (`#00dc82`) with black text for maximum contrast
- Appears at second 22 and stays through end
- On Reels: include "Tap to Call" text for mobile users

---

## 10. Thumbnail System

### Structure
Every video ad thumbnail follows this template:

```
┌──────────────────────┐
│                      │
│   [EMOTIONAL IMAGE]  │  ← Phone screen, frustrated face, or contrast
│                      │
│   ┌──────────────┐   │
│   │  HOOK TEXT   │   │  ← 3-5 words, Inter Black, white + shadow
│   │  (max 5 words)│   │
│   └──────────────┘   │
│                      │
│   ┌──────────────┐   │
│   │ $STAT in     │   │  ← Dollar amount or percentage in green/red
│   │ GREEN or RED │   │
│   └──────────────┘   │
│                      │
└──────────────────────┘
```

### Thumbnail Rules
- High contrast: dark background, bright text
- Human faces increase CTR 30% — use when possible
- Red/green color coding: red for pain, green for gain
- Text: maximum 5 words on thumbnail
- No logo on thumbnail (Facebook already shows brand name)

---

## 11. Platform Export Specs

| Platform | Aspect | Resolution | Length | File Size |
|----------|--------|------------|--------|-----------|
| Reels / Stories | 9:16 | 1080x1920 | 15-30s | <100MB |
| Feed | 1:1 | 1080x1080 | 15-30s | <100MB |
| Feed (landscape) | 16:9 | 1920x1080 | 15-60s | <100MB |
| TikTok | 9:16 | 1080x1920 | 15-60s | <287MB |

### Export Settings
- Codec: H.264
- Frame rate: 30fps (24fps acceptable for cinematic feel)
- Bitrate: 10-15 Mbps for 1080p
- Audio: AAC, 128kbps stereo
- Color space: sRGB

---

## 12. File Naming Convention

```
tct-{vertical}-{script}-v{version}-{format}-{date}.mp4

Examples:
tct-roofing-missed-call-v1-reels-2026-03-18.mp4
tct-hvac-side-by-side-v2-feed-2026-03-18.mp4
tct-universal-try-it-v1-reels-2026-03-18.mp4
```

---

## Quick Reference Card

```
COLORS:    Black #0a0a0a | Green #00dc82 | Red #ef4444 | White #ffffff
FONT:      Inter — Black for hooks, ExtraBold for stats, Bold for captions
HOOK:      Under 3 seconds. No logo. Pattern interrupt.
CAPTIONS:  Always on. Word-by-word green highlight. Bottom center.
MUSIC:     Royalty-free. 30% under VO. Fade at 25s.
CTA:       Green bar, black text, phone number, seconds 22-30.
LOGO:      Never first 3s. Watermark during body. Full at end.
EXPORT:    H.264, 30fps, 10-15Mbps, AAC 128kbps
```
