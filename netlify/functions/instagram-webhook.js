"use strict";

const { createRequestContext, log } = require("../lib/observability");

function text(statusCode, body) {
  return {
    statusCode,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
    body: String(body || ""),
  };
}

function json(statusCode, body) {
  return {
    statusCode,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Content-Type, X-Hub-Signature, X-Hub-Signature-256",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    },
    body: JSON.stringify(body),
  };
}

function parseBody(body) {
  try {
    return body ? JSON.parse(body) : {};
  } catch {
    return null;
  }
}

function webhookMetadata(payload, rawBody) {
  const entries = Array.isArray(payload?.entry) ? payload.entry : [];
  const changeCount = entries.reduce((count, entry) => {
    return count + (Array.isArray(entry?.changes) ? entry.changes.length : 0);
  }, 0);
  const messagingCount = entries.reduce((count, entry) => {
    return count + (Array.isArray(entry?.messaging) ? entry.messaging.length : 0);
  }, 0);

  return {
    object: typeof payload?.object === "string" ? payload.object : "",
    bodyBytes: Buffer.byteLength(rawBody || "", "utf8"),
    entryCount: entries.length,
    changeCount,
    messagingCount,
    hasChanges: changeCount > 0,
    hasMessaging: messagingCount > 0,
  };
}

exports.handler = async (event) => {
  const requestContext = createRequestContext(event, "instagram-webhook");

  if (event.httpMethod === "OPTIONS") return json(204, { ok: true });

  if (event.httpMethod === "GET") {
    const query = event.queryStringParameters || {};
    const mode = query["hub.mode"];
    const verifyToken = query["hub.verify_token"];
    const challenge = query["hub.challenge"];
    const expectedToken = process.env.META_VERIFY_TOKEN;

    if (mode === "subscribe" && expectedToken && verifyToken === expectedToken) {
      log("info", "instagram_webhook_verified", Object.assign({}, requestContext, {
        action: "instagram_webhook_verified",
        challengePresent: Boolean(challenge),
      }));
      return text(200, challenge || "");
    }

    log("warn", "instagram_webhook_verify_rejected", Object.assign({}, requestContext, {
      action: "instagram_webhook_verify_rejected",
      mode,
      hasVerifyToken: Boolean(verifyToken),
      envTokenConfigured: Boolean(expectedToken),
      challengePresent: Boolean(challenge),
    }));
    return text(403, "Forbidden");
  }

  if (event.httpMethod === "POST") {
    const payload = parseBody(event.body);
    if (!payload) {
      log("warn", "instagram_webhook_invalid_json", Object.assign({}, requestContext, {
        action: "instagram_webhook_invalid_json",
        bodyBytes: Buffer.byteLength(event.body || "", "utf8"),
      }));
      return json(400, { ok: false, error: "Invalid JSON", request_id: requestContext.request_id });
    }

    log("info", "instagram_webhook_received", Object.assign({}, requestContext, {
      action: "instagram_webhook_received",
      metadata: webhookMetadata(payload, event.body),
    }));

    return json(200, { ok: true, request_id: requestContext.request_id });
  }

  return json(405, { ok: false, error: "Method not allowed", request_id: requestContext.request_id });
};
