# Meta Instagram Webhook Verification

## Route

`GET /api/webhooks/instagram`

`POST /api/webhooks/instagram`

## Safe Browser Test

Open:

```text
https://thecalltaker.com/api/webhooks/instagram?hub.mode=subscribe&hub.verify_token=calltaker_ig_webhook_2026_wallace&hub.challenge=test123
```

Expected response:

```text
test123
```

## Environment

The deployed serverless runtime must have:

```text
META_VERIFY_TOKEN=calltaker_ig_webhook_2026_wallace
```

## Production Hosting Note

As of 2026-05-30, `thecalltaker.com` resolves to GitHub Pages. GitHub Pages cannot run Netlify Functions or any dynamic webhook route, so this route will not work on production until `thecalltaker.com` is served by Netlify, Vercel, Cloudflare Workers, or another runtime that can execute the webhook handler.

The local implementation is in:

```text
netlify/functions/instagram-webhook.js
```

The Netlify rewrite is:

```text
/api/webhooks/instagram -> /.netlify/functions/instagram-webhook
```
