/**
 * TCT GHL Proxy Worker — Production
 * Proxies GoHighLevel API calls from thecalltaker.com frontend.
 * Keeps GHL API key server-side. Rate-limited, auth'd, filtered.
 *
 * Env vars (secrets):
 *   GHL_API_KEY   — GHL Bearer token
 *   PROXY_SECRET  — Frontend auth token
 *
 * KV Namespace:
 *   RATE_LIMIT    — IP-based rate limiting store
 */

const GHL_BASE = 'https://services.leadconnectorhq.com';
const GHL_API_VERSION = '2021-07-28';

const ALLOWED_ORIGINS = new Set([
  'https://thecalltaker.com',
  'https://www.thecalltaker.com',
]);

// Regex patterns for allowed GHL paths
const ALLOWED_PATHS = [
  /^\/contacts(\/[a-zA-Z0-9_-]+)?$/,
  /^\/contacts\/[a-zA-Z0-9_-]+\/tags$/,
  /^\/contacts\/[a-zA-Z0-9_-]+\/notes$/,
  /^\/forms\/submit$/,
  /^\/opportunities(\/[a-zA-Z0-9_-]+)?$/,
  /^\/locations(\/[a-zA-Z0-9_-]+)?$/,
  /^\/conversations(\/[a-zA-Z0-9_-]+)?$/,
  /^\/conversations\/[a-zA-Z0-9_-]+\/messages$/,
];

// Fields to strip from GHL responses before returning to client
const SENSITIVE_FIELDS = new Set([
  'apiKey', 'api_key', 'password', 'token', 'secret',
  'accessToken', 'access_token', 'refreshToken', 'refresh_token',
  'privateKey', 'private_key', 'authorization',
]);

const MAX_BODY_SIZE = 1 * 1024 * 1024; // 1MB
const RATE_LIMIT_MAX = 10; // requests per window
const RATE_LIMIT_WINDOW = 60; // seconds
const GHL_TIMEOUT_MS = 10000; // 10 seconds

// ─── Helpers ────────────────────────────────────────────────

function getClientIp(request) {
  return request.headers.get('cf-connecting-ip')
    || request.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
    || '0.0.0.0';
}

function isAllowedOrigin(request) {
  const origin = request.headers.get('origin') || '';
  const referer = request.headers.get('referer') || '';
  if (ALLOWED_ORIGINS.has(origin)) return true;
  for (const allowed of ALLOWED_ORIGINS) {
    if (referer.startsWith(allowed + '/')) return true;
  }
  return false;
}

function isAllowedPath(path) {
  return ALLOWED_PATHS.some(pattern => pattern.test(path));
}

function stripSensitiveFields(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(stripSensitiveFields);
  const cleaned = {};
  for (const [key, value] of Object.entries(obj)) {
    if (SENSITIVE_FIELDS.has(key)) continue;
    cleaned[key] = stripSensitiveFields(value);
  }
  return cleaned;
}

function corsHeaders(request) {
  const origin = request.headers.get('origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.has(origin) ? origin : '';
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}

function jsonResponse(body, status, requestId, request) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Request-Id': requestId,
    ...corsHeaders(request),
  };
  return new Response(JSON.stringify(body), { status, headers });
}

function logRequest(requestId, method, path, status, ip) {
  const ts = new Date().toISOString();
  console.log(JSON.stringify({ ts, requestId, method, path, status, ip }));
}

// ─── Rate Limiter ───────────────────────────────────────────

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
    record = { windowStart: now, count: 1 };
  } else {
    record.count += 1;
  }

  const ttl = RATE_LIMIT_WINDOW - (now - record.windowStart);
  try {
    await kv.put(key, JSON.stringify(record), { expirationTtl: Math.max(ttl, 1) });
  } catch {
    // KV write failure is non-fatal — allow request through
  }

  if (record.count > RATE_LIMIT_MAX) {
    return { allowed: false, retryAfter: ttl };
  }
  return { allowed: true, retryAfter: 0 };
}

// ─── Health Endpoint ────────────────────────────────────────

function handleHealth(requestId, request) {
  return jsonResponse(
    { status: 'ok', service: 'tct-ghl-proxy', timestamp: new Date().toISOString() },
    200, requestId, request,
  );
}

// ─── Main Handler ───────────────────────────────────────────

export default {
  async fetch(request, env) {
    const requestId = crypto.randomUUID();
    const ip = getClientIp(request);
    const url = new URL(request.url);

    // Strip the /api/ghl prefix to get the GHL path
    const ghlPath = url.pathname.replace(/^\/api\/ghl/, '') || '/';
    const method = request.method;

    // ── OPTIONS (CORS preflight) ──
    if (method === 'OPTIONS') {
      logRequest(requestId, method, ghlPath, 204, ip);
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }

    // ── Health check (no auth required) ──
    if (ghlPath === '/health') {
      logRequest(requestId, method, ghlPath, 200, ip);
      return handleHealth(requestId, request);
    }

    // ── Origin check ──
    if (!isAllowedOrigin(request)) {
      logRequest(requestId, method, ghlPath, 403, ip);
      return jsonResponse(
        { error: 'Forbidden', message: 'Origin not allowed' },
        403, requestId, request,
      );
    }

    // ── Auth check ──
    const authHeader = request.headers.get('authorization') || '';
    const token = authHeader.replace(/^Bearer\s+/i, '');
    if (!token || token !== env.PROXY_SECRET) {
      logRequest(requestId, method, ghlPath, 401, ip);
      return jsonResponse(
        { error: 'Unauthorized', message: 'Invalid or missing proxy token' },
        401, requestId, request,
      );
    }

    // ── Path whitelist ──
    if (!isAllowedPath(ghlPath)) {
      logRequest(requestId, method, ghlPath, 403, ip);
      return jsonResponse(
        { error: 'Forbidden', message: 'Path not allowed' },
        403, requestId, request,
      );
    }

    // ── Rate limit ──
    const rl = await checkRateLimit(ip, env.RATE_LIMIT);
    if (!rl.allowed) {
      logRequest(requestId, method, ghlPath, 429, ip);
      return new Response(
        JSON.stringify({ error: 'Too Many Requests', retryAfter: rl.retryAfter }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': String(rl.retryAfter),
            'X-Request-Id': requestId,
            ...corsHeaders(request),
          },
        },
      );
    }

    // ── Body size check ──
    const contentLength = parseInt(request.headers.get('content-length') || '0', 10);
    if (contentLength > MAX_BODY_SIZE) {
      logRequest(requestId, method, ghlPath, 413, ip);
      return jsonResponse(
        { error: 'Payload Too Large', message: `Max body size is ${MAX_BODY_SIZE} bytes` },
        413, requestId, request,
      );
    }

    // ── Build GHL request ──
    const ghlUrl = new URL(ghlPath, GHL_BASE);
    url.searchParams.forEach((v, k) => ghlUrl.searchParams.set(k, v));

    const ghlHeaders = {
      'Authorization': `Bearer ${env.GHL_API_KEY}`,
      'Content-Type': 'application/json',
      'Version': GHL_API_VERSION,
      'User-Agent': 'TheCallTaker-Proxy/1.0',
    };

    const fetchOptions = {
      method,
      headers: ghlHeaders,
    };

    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && request.body) {
      const body = await request.text();
      if (body.length > MAX_BODY_SIZE) {
        logRequest(requestId, method, ghlPath, 413, ip);
        return jsonResponse(
          { error: 'Payload Too Large', message: `Max body size is ${MAX_BODY_SIZE} bytes` },
          413, requestId, request,
        );
      }
      fetchOptions.body = body;
    }

    // ── Proxy to GHL with timeout ──
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), GHL_TIMEOUT_MS);
    fetchOptions.signal = controller.signal;

    let ghlResponse;
    try {
      ghlResponse = await fetch(ghlUrl.toString(), fetchOptions);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        logRequest(requestId, method, ghlPath, 504, ip);
        return jsonResponse(
          { error: 'Gateway Timeout', message: 'GHL API did not respond in time' },
          504, requestId, request,
        );
      }
      logRequest(requestId, method, ghlPath, 502, ip);
      return jsonResponse(
        { error: 'Bad Gateway', message: 'Failed to reach GHL API' },
        502, requestId, request,
      );
    }
    clearTimeout(timeoutId);

    // ── Handle GHL rate limiting ──
    if (ghlResponse.status === 429) {
      const retryAfter = ghlResponse.headers.get('retry-after') || '30';
      logRequest(requestId, method, ghlPath, 429, ip);
      return new Response(
        JSON.stringify({ error: 'Rate Limited', message: 'GHL API rate limit reached. Try again shortly.', retryAfter }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': retryAfter,
            'X-Request-Id': requestId,
            ...corsHeaders(request),
          },
        },
      );
    }

    // ── Parse + sanitize response ──
    let responseBody;
    const contentType = ghlResponse.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
      try {
        const json = await ghlResponse.json();
        responseBody = JSON.stringify(stripSensitiveFields(json));
      } catch {
        responseBody = await ghlResponse.text();
      }
    } else {
      responseBody = await ghlResponse.text();
    }

    logRequest(requestId, method, ghlPath, ghlResponse.status, ip);

    return new Response(responseBody, {
      status: ghlResponse.status,
      headers: {
        'Content-Type': contentType || 'application/json',
        'X-Request-Id': requestId,
        ...corsHeaders(request),
      },
    });
  },
};
