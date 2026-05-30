"use strict";

const crypto = require("crypto");

const SENSITIVE_KEY = /(authorization|cookie|token|secret|api[_-]?key|password|card|payment|email|phone|first[_-]?name|last[_-]?name|full[_-]?name|customer[_-]?name|contact[_-]?name|company|business|message|notes|address)/i;
const TOKEN_RE = /(Bearer\s+[A-Za-z0-9._-]+|sk_(live|test)_[A-Za-z0-9]+|pk_(live|test)_[A-Za-z0-9]+|[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,})/g;
const EMAIL_RE = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;
const PHONE_RE = /(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}/g;

function id() {
  return crypto.randomBytes(16).toString("hex");
}

function environment() {
  return process.env.SENTRY_ENVIRONMENT || process.env.CONTEXT || process.env.NODE_ENV || "production";
}

function scrubString(value) {
  return String(value || "")
    .replace(TOKEN_RE, "[redacted-token]")
    .replace(EMAIL_RE, "[redacted-email]")
    .replace(PHONE_RE, "[redacted-phone]")
    .slice(0, 500);
}

function sanitize(value, depth, key) {
  if (key && SENSITIVE_KEY.test(key)) return "[redacted]";
  if (value === null || value === undefined) return value;
  if (typeof value === "string") return scrubString(value);
  if (typeof value === "number" || typeof value === "boolean") return value;
  if (value instanceof Error) {
    return { name: scrubString(value.name || "Error"), message: scrubString(value.message || "") };
  }
  if (depth <= 0) return "[object]";
  if (Array.isArray(value)) return value.slice(0, 10).map((item) => sanitize(item, depth - 1));
  if (typeof value === "object") {
    return Object.keys(value).slice(0, 25).reduce((out, childKey) => {
      out[childKey] = sanitize(value[childKey], depth - 1, childKey);
      return out;
    }, {});
  }
  return scrubString(value);
}

function safeUrl(input) {
  try {
    const parsed = new URL(input || "/", "https://thecalltaker.com");
    return parsed.origin + parsed.pathname;
  } catch {
    return "/";
  }
}

function createRequestContext(event, functionName) {
  const headers = event.headers || {};
  const requestId =
    headers["x-nf-request-id"] ||
    headers["x-request-id"] ||
    headers["client-request-id"] ||
    id();
  const route = safeUrl(event.rawUrl || event.path || "/").replace(/^https:\/\/thecalltaker\.com/, "");
  return {
    function_name: functionName,
    route,
    method: event.httpMethod || "UNKNOWN",
    request_id: requestId,
    environment: environment()
  };
}

function log(level, action, context) {
  const entry = Object.assign(
    {
      timestamp: new Date().toISOString(),
      level: level || "info",
      action: action || "event",
      environment: environment()
    },
    sanitize(context || {}, 3)
  );
  const line = JSON.stringify(entry);
  if (level === "error") console.error(line);
  else if (level === "warn") console.warn(line);
  else console.log(line);
  return entry;
}

function sentryEnabled() {
  return process.env.TCT_OBSERVABILITY_ENABLED !== "false" && Boolean(process.env.SENTRY_DSN);
}

function sentryEnvelopeUrl(dsn) {
  const parsed = new URL(dsn);
  const projectId = parsed.pathname.split("/").filter(Boolean).pop();
  if (!projectId) throw new Error("Invalid Sentry DSN");
  const basePath = parsed.pathname.replace(new RegExp("/?" + projectId + "/?$"), "");
  return `${parsed.protocol}//${parsed.host}${basePath}/api/${projectId}/envelope/`;
}

async function sendSentryEvent(payload) {
  if (!sentryEnabled()) return false;
  const dsn = process.env.SENTRY_DSN;
  const endpoint = sentryEnvelopeUrl(dsn);
  const envelope = [
    JSON.stringify({ dsn, sent_at: new Date().toISOString() }),
    JSON.stringify({ type: "event" }),
    JSON.stringify(payload)
  ].join("\n");

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-sentry-envelope" },
    body: envelope
  });
  return response.ok;
}

async function captureException(error, context) {
  const safeContext = sanitize(context || {}, 3);
  log("error", safeContext.action || "function_exception", Object.assign({}, safeContext, { error }));

  try {
    const eventId = id();
    await sendSentryEvent({
      event_id: eventId,
      timestamp: Date.now() / 1000,
      platform: "node",
      logger: "netlify.function",
      level: "error",
      environment: environment(),
      release: process.env.SENTRY_RELEASE || undefined,
      transaction: safeContext.function_name || safeContext.route || "netlify-function",
      tags: {
        function_name: safeContext.function_name || "",
        route: safeContext.route || "",
        request_id: safeContext.request_id || "",
        action: safeContext.action || "function_exception"
      },
      request: {
        method: safeContext.method || "",
        url: safeContext.route || ""
      },
      exception: {
        values: [
          {
            type: scrubString(error && error.name ? error.name : "Error"),
            value: scrubString(error && error.message ? error.message : String(error || "Unknown error"))
          }
        ]
      },
      extra: safeContext
    });
  } catch (sendError) {
    log("warn", "sentry_capture_failed", {
      action: "sentry_capture_failed",
      reason: sendError instanceof Error ? sendError.message : String(sendError),
      request_id: safeContext.request_id || ""
    });
  }
}

async function captureMessage(message, level, context) {
  const safeContext = sanitize(context || {}, 3);
  log(level || "info", safeContext.action || "function_message", safeContext);
  try {
    await sendSentryEvent({
      event_id: id(),
      timestamp: Date.now() / 1000,
      platform: "node",
      logger: "netlify.function",
      level: level || "info",
      environment: environment(),
      release: process.env.SENTRY_RELEASE || undefined,
      message: scrubString(message),
      tags: {
        function_name: safeContext.function_name || "",
        route: safeContext.route || "",
        request_id: safeContext.request_id || "",
        action: safeContext.action || "function_message"
      },
      extra: safeContext
    });
  } catch (sendError) {
    log("warn", "sentry_capture_failed", {
      action: "sentry_capture_failed",
      reason: sendError instanceof Error ? sendError.message : String(sendError),
      request_id: safeContext.request_id || ""
    });
  }
}

module.exports = {
  captureException,
  captureMessage,
  createRequestContext,
  log,
  sanitize,
  safeUrl
};
