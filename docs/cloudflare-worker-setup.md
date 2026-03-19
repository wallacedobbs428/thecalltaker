# Cloudflare Worker Setup — Jessica Live Demo
**Deploy the voice demo backend in 15 minutes. Free tier.**

---

## Prerequisites
- Node.js installed (any recent version)
- A free Cloudflare account
- A free ElevenLabs account (10K characters/month free)

---

## Step 1: Get ElevenLabs API Key

1. Go to **elevenlabs.io** → Sign Up (free)
2. Click your profile icon → **API Keys**
3. Click **Create API Key** → name it "jessica-demo"
4. Copy the key — you'll need it in Step 6

---

## Step 2: Install Wrangler CLI

```bash
npm install -g wrangler
```

---

## Step 3: Login to Cloudflare

```bash
wrangler login
```

This opens your browser. Click "Allow" to authorize.

---

## Step 4: Create the Worker Project

```bash
mkdir jessica-demo && cd jessica-demo
```

Copy these files from the repo into this folder:
- `cloudflare/jessica-demo-worker.js` → rename to `src/index.js`
- `cloudflare/wrangler.toml` → copy to root

Your folder should look like:
```
jessica-demo/
├── wrangler.toml
└── src/
    └── index.js
```

Update `wrangler.toml`:
```toml
name = "jessica-demo"
main = "src/index.js"
compatibility_date = "2024-01-01"
```

---

## Step 5: Add Your ElevenLabs API Key as a Secret

```bash
wrangler secret put ELEVENLABS_API_KEY
```

Paste your ElevenLabs API key when prompted. This is encrypted and never visible again.

---

## Step 6: Deploy

```bash
wrangler deploy
```

Output will show your worker URL:
```
Published jessica-demo (1.2s)
  https://jessica-demo.YOUR-SUBDOMAIN.workers.dev
```

---

## Step 7: Test with curl

```bash
curl -X POST https://jessica-demo.YOUR-SUBDOMAIN.workers.dev/demo \
  -H "Content-Type: application/json" \
  -d '{"businessName": "Mike'\''s Plumbing"}' \
  --output test.mp3
```

Play `test.mp3` — you should hear Jessica answer as "Mike's Plumbing".

---

## Step 8: Update the Demo Page

In `website/demo-live.html`, find this line in the `<script>`:

```javascript
var WORKER_URL = 'https://jessica-demo.thecalltaker.workers.dev/demo';
```

Replace with your actual worker URL from Step 6:

```javascript
var WORKER_URL = 'https://jessica-demo.YOUR-SUBDOMAIN.workers.dev/demo';
```

---

## Step 9: Push to GitHub Pages

```bash
git add website/demo-live.html
git commit -m "Update demo page with live worker URL"
git push origin main
```

---

## Step 10: Test Full Flow

1. Visit thecalltaker.com/demo-live on iPhone Safari
2. Type a business name
3. Click "Call My Business Now"
4. Audio should play in ~3 seconds
5. CTA slides in after audio finishes

---

## Troubleshooting

**"Voice service unavailable" error:**
- Check your ElevenLabs API key is correct: `wrangler secret list`
- Check ElevenLabs free tier quota (10K chars/month)
- Check worker logs: `wrangler tail`

**Audio doesn't auto-play on iPhone:**
- iOS blocks auto-play — the play button will appear instead
- User taps play, audio plays. This is expected behavior.

**CORS error in browser console:**
- The worker only allows requests from thecalltaker.com
- For local testing, add `http://localhost:3000` to ALLOWED_ORIGINS in the worker

**Rate limit hit (429):**
- Max 3 demos per IP per hour
- Rate limit resets on worker restart or after 1 hour

---

## Cost

| Service | Free Tier | Cost After |
|---------|-----------|------------|
| Cloudflare Workers | 100K requests/day | $5/mo for 10M |
| ElevenLabs | 10K characters/month | $5/mo for 30K |

At ~200 characters per demo, free tier handles ~50 demos/month.
$5/mo ElevenLabs plan handles ~150 demos/month.

---

## Voice Customization

To change Jessica's voice, update `VOICE_ID` in the worker:

```javascript
const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel
```

Browse voices at **elevenlabs.io/voice-library** and copy the Voice ID.

To change what Jessica says, edit the `buildScript()` function.
