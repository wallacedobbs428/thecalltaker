// ============================================================================
// The Call Taker — GHL Proxy Client
// Drop-in replacement for direct GHL API calls.
// All requests go through the Cloudflare Worker proxy at /api/ghl/*
// ============================================================================

var TCT_PROXY_SECRET = 'REPLACE_WITH_PROXY_SECRET_AFTER_DEPLOY';

/**
 * Proxy a request to GHL through the Cloudflare Worker.
 * @param {string} ghlPath - GHL endpoint path, e.g. '/contacts/' or '/contacts/abc123/notes'
 * @param {object} options - fetch options (method, body, etc.)
 * @returns {Promise<Response>}
 */
function tctGhlFetch(ghlPath, options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['Authorization'] = 'Bearer ' + TCT_PROXY_SECRET;
  options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json';
  // Strip Version header — proxy adds it server-side
  delete options.headers['Version'];
  return fetch('/api/ghl' + ghlPath, options);
}
