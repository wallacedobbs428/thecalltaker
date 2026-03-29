# Demo Audio Replacement Checklist

## Current State (March 6, 2026)
- `demo-call-15s.mp3` is a **PLACEHOLDER** (~1 second of audio at 128kbps, 15.8KB)
- The demo console detects this and enters **SIMULATED DEMO MODE**
- Header shows "Simulated demo" badge (visible, styled with border)
- Time label shows "Press play to preview" → "Playing demo preview" → "Demo complete"
- Playback animates waveform, transcript, summary, booking, and text cards — no audio
- No misleading "real call" language in simulated mode

## To Upgrade to REAL AUDIO MODE
Drop a real MP3 file (>5 seconds) and the console auto-detects it:
- Header badge changes to "Real call audio" (green)
- Time label changes to "Real call recording"
- Play button triggers actual audio playback synced to transcript

### Recording Requirements
- **Format:** MP3, 128kbps or higher, 44.1kHz stereo
- **Duration:** 12-20 seconds (console designed for ~15s)
- **Content:** Real AI call recording — caller asks for service, AI books appointment
- **Quality:** Clean audio, no background noise, no PII (use fake names/numbers)

### Steps
1. Record a call to the demo line: (629) 269-9697
2. Say something like "I need an emergency plumber" or "My AC isn't working"
3. Let the AI respond through booking confirmation (~60s call)
4. Trim to the best 15-second segment
5. Export as MP3 (128kbps, stereo)
6. Name it `demo-call-15s.mp3` and replace this file
7. Test on all 3 pages: index.html, pricing.html, demo-showcase.html
8. Verify the badge changes to "Real call audio" (green)

### Transcript Sync
- After replacing audio, check transcript highlight timing vs real recording
- Timestamps in `demo-console.js` INDUSTRIES data (start/end per line)
- Waveform + output cards animate by percentage, not absolute time — auto-adapt

### Pages Using This Audio
- `/index.html` (homepage — 2 demo consoles)
- `/pricing.html`
- `/demo-showcase.html`

### How Detection Works (demo-console.js)
- Checks audio duration on `loadedmetadata`
- duration < 5s → SIMULATED MODE (badge: "Simulated demo", animated timeline only)
- duration >= 5s → REAL AUDIO MODE (badge: "Real call audio", actual playback)
- File missing/error → SIMULATED MODE (graceful fallback)
- Browser autoplay blocked → falls back to SIMULATED MODE
