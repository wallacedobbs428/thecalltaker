/**
 * Gideon Demo — Cloudflare Worker
 * Proxies ElevenLabs TTS API for live voice demo on thecalltaker.com
 *
 * Endpoint: POST /demo
 * Body: { "businessName": "Mike's Plumbing" }
 * Returns: audio/mpeg stream
 *
 * Secrets: ELEVENLABS_API_KEY (set via `wrangler secret put ELEVENLABS_API_KEY`)
 */

const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel — warm, professional female
const MODEL_ID = "eleven_flash_v2_5";
const ALLOWED_ORIGINS = [
  "https://thecalltaker.com",
  "https://www.thecalltaker.com",
  "http://localhost:3000",
  "http://127.0.0.1:3000",
];

// In-memory rate limit store (resets on worker restart, good enough for free tier)
const rateLimit = new Map();
const RATE_LIMIT_MAX = 3;
const RATE_LIMIT_WINDOW = 60 * 60 * 1000; // 1 hour

function getCorsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimit.get(ip);
  if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW) {
    rateLimit.set(ip, { windowStart: now, count: 1 });
    return true;
  }
  if (entry.count >= RATE_LIMIT_MAX) {
    return false;
  }
  entry.count++;
  return true;
}

function sanitizeBusinessName(name) {
  if (!name || typeof name !== "string") return null;
  // Strip anything that isn't letters, numbers, spaces, apostrophes, hyphens, ampersands, periods
  let clean = name.replace(/[^a-zA-Z0-9\s'&.\-]/g, "").trim();
  if (clean.length === 0) return null;
  if (clean.length > 50) clean = clean.substring(0, 50);
  return clean;
}

function buildScript(businessName) {
  return `Thank you for calling ${businessName}, this is Gideon! We're so glad you reached out. I can help you schedule an appointment, answer questions about our services, or connect you with the right person. What can I help you with today?`;
}

export default {
  async fetch(request, env) {
    const cors = getCorsHeaders(request);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // Only accept POST to /demo
    const url = new URL(request.url);
    if (url.pathname !== "/demo" || request.method !== "POST") {
      return new Response(
        JSON.stringify({ error: "Not found. POST /demo with { businessName }" }),
        { status: 404, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    // Rate limit by IP
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (!checkRateLimit(ip)) {
      return new Response(
        JSON.stringify({ error: "Rate limit exceeded. Max 3 demos per hour." }),
        { status: 429, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    // Parse and validate body
    let body;
    try {
      body = await request.json();
    } catch {
      return new Response(
        JSON.stringify({ error: "Invalid JSON body" }),
        { status: 400, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    const businessName = sanitizeBusinessName(body.businessName);
    if (!businessName) {
      return new Response(
        JSON.stringify({ error: "Business name is required (letters, numbers, max 50 chars)" }),
        { status: 400, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    // Check for API key
    if (!env.ELEVENLABS_API_KEY) {
      return new Response(
        JSON.stringify({ error: "Server configuration error" }),
        { status: 500, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    // Call ElevenLabs TTS API
    const script = buildScript(businessName);
    let elevenLabsRes;
    try {
      elevenLabsRes = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "xi-api-key": env.ELEVENLABS_API_KEY,
          },
          body: JSON.stringify({
            text: script,
            model_id: MODEL_ID,
            voice_settings: {
              stability: 0.6,
              similarity_boost: 0.85,
              style: 0.3,
              use_speaker_boost: true,
            },
            output_format: "mp3_44100_128",
          }),
        }
      );
    } catch (err) {
      console.error("ElevenLabs fetch error:", err.message);
      return new Response(
        JSON.stringify({ error: "Voice service unavailable. Try again in a moment." }),
        { status: 502, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    if (!elevenLabsRes.ok) {
      const errText = await elevenLabsRes.text().catch(() => "unknown");
      console.error(`ElevenLabs ${elevenLabsRes.status}: ${errText}`);
      return new Response(
        JSON.stringify({ error: "Voice generation failed. Try again." }),
        { status: 502, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

    // Stream audio back to client
    console.log(`Demo generated: "${businessName}" from ${ip.substring(0, 8)}***`);
    return new Response(elevenLabsRes.body, {
      status: 200,
      headers: {
        ...cors,
        "Content-Type": "audio/mpeg",
        "Cache-Control": "no-store",
      },
    });
  },
};
