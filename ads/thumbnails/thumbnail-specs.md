# Video Ad Thumbnail Specs — The Call Taker

> Every video ad needs a scroll-stopping thumbnail.
> These are the 5 thumbnail concepts for the 5 video scripts.

---

## Universal Specs

- **Reels thumbnail:** 1080x1920px (9:16)
- **Feed thumbnail:** 1080x1080px (1:1)
- **Hook font:** Inter Black, white, drop shadow `2px 2px 8px rgba(0,0,0,0.8)`
- **Stat font:** Inter ExtraBold, colored (#ef4444 for pain, #00dc82 for gain)
- **Max text:** 5 words
- **No logo** on thumbnail — Facebook shows brand name already
- **Human faces increase CTR 30%** — use when possible

---

## Thumbnail 1 — "The Missed Call" (Script 1)

**Visual:** Dark bedroom scene. iPhone screen glowing with "Missed Call" notification. The only light source is the phone — cinematic, moody.

**Text overlay:**
- Main: `"$1,200 Gone"` — Inter Black, 80px, `#ef4444` (red)
- Sub: `"...or booked while you slept"` — Inter SemiBold, 36px, `#00dc82` (green)

**Color treatment:** High contrast. Warm phone glow on cool blue-black room. Slight vignette.

**AI generation prompt:** "Photorealistic close-up of iPhone screen showing 'Missed Call' notification on a dark wooden nightstand in a dim bedroom at night. Phone glow illuminating the scene. Cinematic lighting, shallow depth of field, 9:16 aspect ratio."

---

## Thumbnail 2 — "Side by Side" (Script 2)

**Visual:** Hard vertical split. LEFT: dark/red-tinted phone showing "Voicemail." RIGHT: bright/green-tinted phone showing "Appointment Booked."

**Text overlay:**
- LEFT: `"$350 Lost"` — Inter Black, 64px, `#ef4444` (red)
- RIGHT: `"$350 Booked"` — Inter Black, 64px, `#00dc82` (green)
- Divider: thin white line down the center

**Color treatment:** Strong red/green color grading split. Left is desaturated and dark, right is vibrant.

**AI generation prompt:** "Split screen comparison, left side dark red-tinted phone showing voicemail screen, right side bright green-tinted phone showing appointment confirmation. Hard vertical line divide. Clean professional look, 9:16 aspect ratio."

---

## Thumbnail 3 — "The Owner's Night" (Script 3)

**Visual:** Close-up of a sleeping person's face in bed. Phone on nightstand shows "3 Missed Calls" with notification badges stacking.

**Text overlay:**
- Main: `"$2,400 Gone"` — Inter Black, 80px, white with red glow
- Sub: `"Before your alarm went off"` — Inter SemiBold, 32px, `#a3a3a3`

**Color treatment:** Cool blue night tones. Phone screen creates warm accent. Cinematic depth of field.

**Alt concept:** Morning version — smiling person with phone showing "$2,400 Booked" and green accent glow.

**AI generation prompt:** "Person sleeping in bed at night, phone on nightstand glowing with multiple notifications. Dark bedroom, moonlight through window. Cinematic, moody. 9:16 aspect ratio."

---

## Thumbnail 4 — "Try It Right Now" (Script 4)

**Visual:** Wallace (or similar young person) pointing at phone camera. Raw, authentic selfie-style shot. Phone held up showing the demo line number. High energy facial expression.

**Text overlay:**
- Main: `"I'm 16. Call This."` — Inter Black, 72px, white
- Phone number: `"(615) 784-5747"` — Inter Black, 56px, `#00dc82` on dark pill

**Color treatment:** Raw, slightly warm. NO professional color grading — the amateur feel IS the appeal. Natural lighting.

**Production note:** This should be an actual photo of Wallace, not AI-generated. Authenticity is the entire appeal of this script.

---

## Thumbnail 5 — "What $97 Buys" (Script 5)

**Visual:** Grid layout (2x2) showing 4 underwhelming things $97 buys: a dinner plate, a gas pump, Netflix on a TV, a stack of business cards. Each item has a red "X" through it. Center of the grid: `"$97"` in massive green text.

**Text overlay:**
- Center: `"$97"` — Inter Black, 120px, `#00dc82` (green)
- Below center: `"730 HOURS"` — Inter ExtraBold, 56px, white
- Red X marks: on each grid item

**Color treatment:** Dark background. Grid items slightly desaturated. Green `$97` is the brightest element — eye goes there first.

**AI generation prompt:** "Flat lay grid of 4 items on dark background: restaurant dinner plate, gas pump nozzle, Netflix screen, stack of business cards. Each item has a red X overlay. Center of frame is empty for text overlay. Clean product photography style, 1:1 aspect ratio."

---

## Canva/Figma Template Spec

For each thumbnail, create a template with:

```
Layer 1: Background image (AI-generated or stock)
Layer 2: Color overlay/grade
Layer 3: Vignette (radial gradient, transparent center, black edges)
Layer 4: Main text (hook)
Layer 5: Sub text (stat or CTA)
Layer 6: Phone number pill (if applicable)
```

### Text Safe Zones (9:16)
```
Top:    120px from edge (app UI)
Bottom: 200px from edge (Instagram nav)
Left:   40px padding
Right:  40px padding
```

### Export Settings
- Format: PNG (for upload to Meta Ads)
- Quality: Maximum
- Color space: sRGB
