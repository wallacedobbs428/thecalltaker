# Demo Audio Replacement Checklist

## Current State
- `demo-call-15s.mp3` is a **PLACEHOLDER** (~1 second of audio at 128kbps, 15.8KB)
- The demo console detects this and shows "Simulated demo (real recording coming soon)"
- Playback falls back to the simulated timeline animation (works fine without real audio)

## To Replace With Real Recording

### Requirements
- **Format:** MP3, 128kbps or higher, 44.1kHz stereo
- **Duration:** 12-20 seconds (the console is designed for ~15s)
- **Content:** Real AI call recording — caller asks for service, AI answers, books appointment
- **Quality:** Clean audio, no background noise, no PII (use fake names/numbers)

### Steps
1. Record a call to the demo line: (615) 784-5747
2. Say something like "I need an emergency plumber" or "My AC isn't working"
3. Let the AI respond through booking confirmation (~60s call)
4. Trim to the best 15-second segment showing:
   - Caller states problem
   - AI responds naturally
   - AI starts booking
5. Export as MP3 (128kbps, stereo)
6. Name it `demo-call-15s.mp3` and replace this file
7. Test on all 3 pages: index.html, pricing.html, demo-showcase.html
8. Verify the sim-label changes to "Demo audio loaded" (green text)

### Transcript Sync
- After replacing the audio, check that transcript highlight timing matches the real recording
- Transcript timestamps are in `demo-console.js` INDUSTRIES data (start/end per line)
- If timing is off, adjust the `start` and `end` values to match the real audio segments
- The waveform and output cards animate based on playback percentage, not absolute time — they auto-adapt

### Pages Using This Audio
- `/index.html` (homepage demo console)
- `/pricing.html` (pricing page demo)
- `/demo-showcase.html` (dedicated demo page)

### How Detection Works
- `demo-console.js` checks audio duration on `loadedmetadata`
- If duration < 5 seconds: shows "Simulated demo (real recording coming soon)"
- If duration >= 5 seconds: shows "Demo audio loaded" in green
- If file missing/error: shows "Using simulated demo"
