// ============================================================================
// The Call Taker — GHL API Proxy Worker (Production)
// Cloudflare Worker that proxies GHL API calls so the API key never touches
// the browser. Rate-limited, origin-locked, endpoint-restricted.
// ============================================================================

// ── CONFIG ──────────────────────────────────────────────────────────────────

const GHL_BASE = 'https://services.leadconnectorhq.com';
const GHL_LOCATION_ID = 'tQb9YmrGDrdVUJYPKrsY';

const ALLOWED_ORIGINS = new Set([
  'https://thecalltaker.com',
  'https://www.thecalltaker.com',
]);

// Endpoint allowlist — regex patterns matched against the proxied path.
// Only these GHL routes are reachable through the proxy.
const ALLOWED_ENDPOINTS = [
  /^\/contacts\/?$/,                          // POST /contacts/
  /^\/contacts\/[a-zA-Z0-9]+\/notes\/?$/,    // POST /contacts/{id}/notes
  /^\/contacts\/[a-zA-Z0-9]+\/tags\/?$/,     // POST /contacts/{id}/tags
  /^\/contacts\/[a-zA-Z0-9]+\/?$/,           // GET  /contacts/{id}
  /^\/forms\/submit\/?$/,                     // POST /forms/submit
  /^\/opportunities\/?$/,                     // POST /opportunities/
  /^\/opportunities\/[a-zA-Z0-9]+\/?$/,      // GET  /opportunities/{id}
];

const RATE_LIMIT_MAX   = 10;          // requests per window
const RATE_LIMIT_WINDOW = 60;         // seconds
const MAX_BODY_SIZE    = 1_048_576;   // 1 MB
const GHL_TIMEOUT_MS   = 10_000;      // 10 s

// Fields stripped from GHL responses before returning to client
const SENSITIVE_FIELDS = new Set([
  'apiKey', 'api_key', 'token', 'accessToken', 'access_token',
  'refreshToken', 'refresh_token', 'secret', 'password',
  'stripeCustomerId', 'stripe_customer_id',
]);

// ── HELPERS ─────────────────────────────────────────────────────────────────

function requestId() {
  return crypto.randomUUID();
}

function jsonResponse(body, status, reqId, origin) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Request-Id': reqId,
    'X-Powered-By': 'tct-ghl-proxy',
  };
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
    headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
    headers['Access-Control-Max-Age'] = '86400';
  }
  return new Response(JSON.stringify(body), { status, headers });
}

/** Recursively strip sensitive keys from an object */
function sanitize(obj) {
  if (Array.isArray(obj)) return obj.map(sanitize);
  if (obj && typeof obj === 'object') {
    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
      if (SENSITIVE_FIELDS.has(key)) continue;
      cleaned[key] = sanitize(value);
    }
    return cleaned;
  }
  return obj;
}

/** Get the real client IP from Cloudflare headers */
function clientIp(request) {
  return request.headers.get('CF-Connecting-IP') || 'unknown';
}

// ── RATE LIMITER (KV-backed) ────────────────────────────────────────────────

async function checkRateLimit(ip, kv) {
  const key = `rl:${ip}`;
  const now = Math.floor(Date.now() / 1000);

  let record;
  try {
    const raw = await kv.get(key);
    record = raw ? JSON.parse(raw) : null;
  } catch {
    record = null;
  }

  if (!record || now - record.windowStart >= RATE_LIMIT_WINDOW) {
    // New window
    record = { windowStart: now, count: 1 };
  } else {
    record.count += 1;
  }

  const ttl = RATE_LIMIT_WINDOW - (now - record.windowStart);

  try {
    await kv.put(key, JSON.stringify(record), { expirationTtl: Math.max(ttl, 1) });
  } catch {
    // KV write failure — allow the request (fail open for availability)
  }

  return {
    allowed: record.count <= RATE_LIMIT_MAX,
    remaining: Math.max(0, RATE_LIMIT_MAX - record.count),
    resetIn: ttl,
  };
}

// ── ENDPOINT VALIDATION ─────────────────────────────────────────────────────

function isAllowedEndpoint(path) {
  return ALLOWED_ENDPOINTS.some(re => re.test(path));
}

// ── MAIN HANDLER ────────────────────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const reqId = requestId();
    const origin = request.headers.get('Origin') || '';

    // ── CORS preflight ────────────────────────────────────────────────────
    if (request.method === 'OPTIONS') {
      if (!ALLOWED_ORIGINS.has(origin)) {
        return jsonResponse({ error: 'Forbidden origin' }, 403, reqId, null);
      }
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': origin,
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          'Access-Control-Max-Age': '86400',
          'X-Request-Id': reqId,
        },
      });
    }

    // ── Origin check ──────────────────────────────────────────────────────
    // Allow requests with no Origin header (server-to-server, curl testing)
    // but block requests from wrong origins (other websites)
    if (origin && !ALLOWED_ORIGINS.has(origin)) {
      console.log(JSON.stringify({
        reqId, event: 'blocked_origin', origin, ip: clientIp(request),
      }));
      return jsonResponse({ error: 'Forbidden origin' }, 403, reqId, null);
    }

    // ── Proxy secret auth ─────────────────────────────────────────────────
    const authHeader = request.headers.get('Authorization') || '';
    const token = authHeader.replace(/^Bearer\s+/i, '');
    if (!token || token !== env.PROXY_SECRET) {
      console.log(JSON.stringify({
        reqId, event: 'auth_failed', ip: clientIp(request),
      }));
      return jsonResponse({ error: 'Unauthorized' }, 401, reqId, origin);
    }

    // ── Rate limiting ─────────────────────────────────────────────────────
    const ip = clientIp(request);
    const rl = await checkRateLimit(ip, env.RATE_LIMIT);
    if (!rl.allowed) {
      console.log(JSON.stringify({
        reqId, event: 'rate_limited', ip,
      }));
      return jsonResponse(
        { error: 'Rate limit exceeded', retryAfter: rl.resetIn },
        429, reqId, origin,
      );
    }

    // ── Parse proxy path ──────────────────────────────────────────────────
    const url = new URL(request.url);
    // Strip the /api/ghl prefix to get the GHL endpoint path
    const ghlPath = url.pathname.replace(/^\/api\/ghl/, '') || '/';

    if (!isAllowedEndpoint(ghlPath)) {
      console.log(JSON.stringify({
        reqId, event: 'blocked_endpoint', path: ghlPath, ip,
      }));
      return jsonResponse({ error: 'Endpoint not allowed' }, 403, reqId, origin);
    }

    // ── Body size check ───────────────────────────────────────────────────
    const contentLength = parseInt(request.headers.get('Content-Length') || '0', 10);
    if (contentLength > MAX_BODY_SIZE) {
      return jsonResponse({ error: 'Request body too large' }, 413, reqId, origin);
    }

    // Read body (if any) for size verification
    let bodyText = null;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        bodyText = await request.text();
        if (bodyText.length > MAX_BODY_SIZE) {
          return jsonResponse({ error: 'Request body too large' }, 413, reqId, origin);
        }
      } catch {
        return jsonResponse({ error: 'Failed to read request body' }, 400, reqId, origin);
      }
    }

    // ── Build GHL request ─────────────────────────────────────────────────
    const ghlUrl = `${GHL_BASE}${ghlPath}${url.search}`;
    const ghlHeaders = {
      'Authorization': `Bearer ${env.GHL_API_KEY}`,
      'Version': '2021-07-28',
      'Content-Type': 'application/json',
      'User-Agent': 'TheCallTaker-Proxy/1.0',
    };

    // ── Fetch with timeout ────────────────────────────────────────────────
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), GHL_TIMEOUT_MS);

    let ghlResponse;
    try {
      ghlResponse = await fetch(ghlUrl, {
        method: request.method,
        headers: ghlHeaders,
        body: bodyText,
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timeout);
      if (err.name === 'AbortError') {
        console.log(JSON.stringify({
          reqId, event: 'timeout', path: ghlPath, ip,
        }));
        return jsonResponse({ error: 'Gateway timeout' }, 504, reqId, origin);
      }
      console.log(JSON.stringify({
        reqId, event: 'fetch_error', path: ghlPath, error: err.message, ip,
      }));
      return jsonResponse({ error: 'Bad gateway' }, 502, reqId, origin);
    }
    clearTimeout(timeout);

    // ── Handle GHL rate limiting ──────────────────────────────────────────
    if (ghlResponse.status === 429) {
      console.log(JSON.stringify({
        reqId, event: 'ghl_rate_limited', path: ghlPath, ip,
      }));
      return jsonResponse(
        { error: 'Service temporarily unavailable — please retry in 30 seconds' },
        429, reqId, origin,
      );
    }

    // ── Handle GHL auth errors (don't leak key details) ───────────────────
    if (ghlResponse.status === 401) {
      console.log(JSON.stringify({
        reqId, event: 'ghl_auth_error', path: ghlPath, status: 401,
      }));
      return jsonResponse(
        { error: 'Upstream authentication failed' },
        502, reqId, origin,
      );
    }

    // ── Sanitize and return GHL response ──────────────────────────────────
    let responseBody;
    const responseText = await ghlResponse.text();
    try {
      const parsed = JSON.parse(responseText);
      responseBody = JSON.stringify(sanitize(parsed));
    } catch {
      // Non-JSON response — return as-is (e.g. 204 No Content)
      responseBody = responseText;
    }

    // ── Log (never log keys or bodies) ────────────────────────────────────
    console.log(JSON.stringify({
      reqId,
      event: 'proxy_success',
      method: request.method,
      path: ghlPath,
      status: ghlResponse.status,
      ip,
      rateRemaining: rl.remaining,
    }));

    // ── Build response headers ────────────────────────────────────────────
    const responseHeaders = {
      'Content-Type': ghlResponse.headers.get('Content-Type') || 'application/json',
      'X-Request-Id': reqId,
      'X-RateLimit-Remaining': String(rl.remaining),
      'X-Powered-By': 'tct-ghl-proxy',
    };
    if (origin && ALLOWED_ORIGINS.has(origin)) {
      responseHeaders['Access-Control-Allow-Origin'] = origin;
      responseHeaders['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
      responseHeaders['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
    }

    return new Response(responseBody, {
      status: ghlResponse.status,
      headers: responseHeaders,
    });
  },
};
