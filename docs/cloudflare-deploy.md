# Jessica Demo Worker — Cloudflare Deployment

## Prerequisites
- Cloudflare account (free tier works)
- ElevenLabs API key (from elevenlabs.io → Profile → API Keys)
- `wrangler` CLI installed (`npm install -g wrangler`)

## Steps

### 1. Login to Cloudflare
```bash
cd ~/Desktop/thecalltaker/cloudflare/
wrangler login
```
This opens a browser. Authorize wrangler with your Cloudflare account.

### 2. Create KV Namespace (for rate limiting)
```bash
wrangler kv:namespace create "DEMO_KV"
```
Copy the `id` from the output and replace `REPLACE_WITH_KV_ID` in `wrangler.toml`.

### 3. Set ElevenLabs API Key
```bash
wrangler secret put ELEVENLABS_API_KEY
```
Paste your ElevenLabs API key when prompted.

### 4. Deploy
```bash
wrangler deploy
```

### 5. Get Deployed URL
After deploy, wrangler prints the worker URL. Format:
```
https://jessica-demo.<your-account>.workers.dev
```

### 6. Update demo-live.html
In `website/demo-live.html`, find this line:
```javascript
var WORKER_URL = 'https://jessica-demo.thecalltaker.workers.dev';
```
Replace with the actual deployed URL if it differs.

### 7. Push to GitHub
```bash
cd ~/Desktop/thecalltaker/
git add website/demo-live.html
git commit -m "Add Jessica browser audio demo"
git push
```

## Testing
1. Open demo-live.html in browser
2. Type a business name
3. Click "Call My Business Now"
4. Audio should play Jessica greeting in ~3 seconds
5. After audio ends, CTA slides in

## Rate Limits
- 3 demos per IP per hour (enforced by KV)
- After limit: shows message to call demo line instead

## Costs
- Cloudflare Workers: Free tier = 100K requests/day
- ElevenLabs: ~$0.001 per demo (Flash v2.5 pricing)
- KV: Free tier = 100K reads/day, 1K writes/day
