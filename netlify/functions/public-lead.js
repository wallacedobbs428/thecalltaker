"use strict";

const DEFAULT_ORIGIN = "https://thecalltaker.com";
const DEFAULT_CTOS_LEAD_URL = "https://thecalltaker.vercel.app/api/public/lead";

function json(statusCode, body) {
  return {
    statusCode,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Methods": "POST,OPTIONS",
    },
    body: JSON.stringify(body),
  };
}

function normalizePhone(value) {
  const digits = String(value || "").replace(/\D/g, "");
  if (!digits) return "";
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
  return value;
}

function parseBody(body) {
  try {
    return body ? JSON.parse(body) : {};
  } catch {
    return null;
  }
}

function collectLead(payload) {
  const firstName = payload.firstName || payload.name?.split(" ")[0] || "";
  const lastName =
    payload.lastName ||
    payload.name?.split(" ").slice(1).join(" ") ||
    "";
  const company =
    payload.company ||
    payload.companyName ||
    payload.business_name ||
    payload.businessName ||
    "";

  return {
    firstName,
    lastName,
    company,
    email: payload.email || "",
    phone: normalizePhone(payload.phone || payload.callbackPhone || ""),
    source: payload.source || payload.kind || "website",
    page: payload.page || payload.path || "",
    tags: Array.isArray(payload.tags) ? payload.tags : [],
    notes: payload.notes || payload.message || "",
    utm: {
      source: payload.utm_source || "",
      medium: payload.utm_medium || "",
      campaign: payload.utm_campaign || "",
      term: payload.utm_term || "",
      content: payload.utm_content || "",
    },
  };
}

async function postNtfy(topic, title, body, priority, tags) {
  if (!topic) return;
  console.warn("Direct ntfy suppressed in legacy Netlify intake", { title, priority, tags, bodyBytes: body.length });
}

async function forwardToCtos(lead, payload, origin) {
  const endpoint =
    process.env.CTOS_PUBLIC_LEAD_URL ||
    process.env.PUBLIC_LEAD_FORWARD_URL ||
    DEFAULT_CTOS_LEAD_URL;

  const body = {
    firstName: lead.firstName,
    lastName: lead.lastName,
    email: lead.email,
    phone: lead.phone,
    company: lead.company,
    source: lead.source,
    page: lead.page,
    tags: lead.tags,
    notes: lead.notes,
    industry: payload.industry || payload.category || payload.vertical || "",
    utm_source: payload.utm_source || "",
    utm_medium: payload.utm_medium || "",
    utm_campaign: payload.utm_campaign || "",
    utm_term: payload.utm_term || "",
    utm_content: payload.utm_content || "",
  };

  const headers = {
    "Content-Type": "application/json",
    "X-Forwarded-Origin": origin || DEFAULT_ORIGIN,
  };

  if (process.env.CTOS_PUBLIC_LEAD_TOKEN) {
    headers.Authorization = `Bearer ${process.env.CTOS_PUBLIC_LEAD_TOKEN}`;
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`CTOS intake failed (${response.status}): ${detail}`);
  }

  return response.json();
}

exports.handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return json(204, { ok: true });
  if (event.httpMethod !== "POST") return json(405, { error: "Method not allowed" });

  const payload = parseBody(event.body);
  if (!payload) return json(400, { error: "Invalid JSON body" });
  if (payload.website || payload.company_website || payload.honeypot) {
    return json(202, { ok: true });
  }

  const lead = collectLead(payload);
  if (!lead.phone && !lead.email) {
    return json(400, { error: "Phone or email is required" });
  }

  const origin = event.headers.origin || DEFAULT_ORIGIN;
  const pageUrl = lead.page ? `${origin}${lead.page}` : origin;
  const body = [
    `Source: ${lead.source}`,
    `Page: ${pageUrl}`,
    `Name: ${[lead.firstName, lead.lastName].filter(Boolean).join(" ") || "N/A"}`,
    `Company: ${lead.company || "N/A"}`,
    `Phone: ${lead.phone || "N/A"}`,
    `Email: ${lead.email || "N/A"}`,
    `Tags: ${lead.tags.join(", ") || "none"}`,
    lead.notes ? `Notes: ${lead.notes}` : "",
  ].filter(Boolean).join("\n");

  const urgentTopic = process.env.TCT_NTFY_URGENT_TOPIC || "tct-urgent-Hk9UOEZR";
  const salesTopic = process.env.TCT_NTFY_SALES_TOPIC || "tct-xK9mW4vR7pLd";

  try {
    const forwarded = await forwardToCtos(lead, payload, origin);
    return json(200, {
      ok: true,
      forwarded: true,
      id: forwarded?.id || null,
      template_key: forwarded?.template_key || null,
    });
  } catch (error) {
    try {
      await Promise.all([
        postNtfy(urgentTopic, `Lead Intake Forward Failure: ${lead.company || lead.phone || "New lead"}`, body, "urgent", "warning,phone"),
        postNtfy(salesTopic, `Lead Intake Forward Failure: ${lead.company || lead.phone || "New lead"}`, body, "high", "warning"),
      ]);
    } catch {}
    return json(502, { error: "Lead forwarding failed", detail: String(error) });
  }
};
