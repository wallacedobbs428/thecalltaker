/**
 * The Call Taker first-party, asset-bound buyer event producer.
 *
 * It stays dormant unless every required asset-bound query parameter is
 * present. It sends no PII, raw click ID, contact value, or request body to a
 * third party. The server hashes the session identifier before persistence.
 */
(function (root, document) {
  "use strict";

  var ENDPOINT = "https://call-taker-os.vercel.app/api/public/buyer-event";
  var SCHEMA = "tct.public-buyer-event.v2";
  var SESSION_KEY = "tct_buyer_session_v1";
  var EVENT_KEY_PREFIX = "tct_buyer_event_v1_";
  var TOKEN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
  var ITEM_TOKEN = /^[a-z0-9][a-z0-9_-]{0,127}$/;
  var LOCAL_DATE = /^\d{4}-\d{2}-\d{2}$/;
  var SHA256 = /^[0-9a-f]{64}$/;
  var CHANNELS = ["instagram", "facebook", "email", "direct", "referral"];

  function uuid() {
    if (root.crypto && typeof root.crypto.randomUUID === "function") {
      return root.crypto.randomUUID();
    }
    return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, function (character) {
      var number = Number(character);
      var random = root.crypto.getRandomValues(new Uint8Array(1))[0];
      return (number ^ (random & (15 >> (number / 4)))).toString(16);
    });
  }

  function safeToken(params, key) {
    var value = (params.get(key) || "").trim().toLowerCase();
    return TOKEN.test(value) ? value : "";
  }

  function safeSha(params, key) {
    var value = (params.get(key) || "").trim().toLowerCase();
    return SHA256.test(value) ? value : "";
  }

  function safeItem(params, key) {
    var value = (params.get(key) || "").trim().toLowerCase();
    return ITEM_TOKEN.test(value) ? value : "";
  }

  function safeLocalDate(params, key) {
    var value = (params.get(key) || "").trim();
    if (!LOCAL_DATE.test(value)) return "";
    var parsed = new Date(value + "T12:00:00.000Z");
    return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value
      ? value
      : "";
  }

  function readAttribution() {
    var params = new URLSearchParams(root.location.search);
    var source = safeToken(params, "utm_source");
    var medium = safeToken(params, "utm_medium");
    var campaign = safeToken(params, "utm_campaign");
    var content = safeToken(params, "utm_content");
    var assetSha = safeSha(params, "tct_asset_sha256");
    var publicationSeedSha = safeSha(params, "tct_publication_seed_sha256");
    var localDate = safeLocalDate(params, "tct_local_date");
    var itemId = safeItem(params, "tct_item_id");
    var clickableValue = (params.get("tct_clickable") || "").trim().toLowerCase();
    var destinationClickable = clickableValue === "1" || clickableValue === "true"
      ? true
      : clickableValue === "0" || clickableValue === "false"
        ? false
        : null;
    if (
      CHANNELS.indexOf(source) === -1 ||
      !medium ||
      !campaign ||
      !content ||
      !assetSha ||
      !publicationSeedSha ||
      !localDate ||
      !itemId ||
      destinationClickable === null
    ) return null;
    if ((source === "instagram" || source === "facebook") && medium !== "organic_social") {
      return null;
    }
    return {
      source_channel: source,
      utm_source: source,
      utm_medium: medium,
      utm_campaign: campaign,
      utm_content: content,
      source_asset_sha256: assetSha,
      source_publication_seed_sha256: publicationSeedSha,
      source_platform: source,
      source_local_date: localDate,
      source_item_id: itemId,
      source_destination_clickable: destinationClickable
    };
  }

  function readOrCreateSessionId() {
    var existing = root.sessionStorage.getItem(SESSION_KEY);
    if (existing) return existing;
    var created = uuid();
    root.sessionStorage.setItem(SESSION_KEY, created);
    return created;
  }

  function eventIdentity(eventType) {
    var key = EVENT_KEY_PREFIX + eventType;
    var stored = root.sessionStorage.getItem(key);
    if (stored) {
      try {
        var parsed = JSON.parse(stored);
        if (parsed && parsed.event_id && parsed.occurred_at) return parsed;
      } catch (_) {}
    }
    var created = { event_id: uuid(), occurred_at: new Date().toISOString() };
    root.sessionStorage.setItem(key, JSON.stringify(created));
    return created;
  }

  function diagnostic(name, detail) {
    if (typeof root.dispatchEvent === "function" && typeof root.CustomEvent === "function") {
      root.dispatchEvent(new root.CustomEvent("tct:first-party-attribution", {
        detail: { name: name, authoritative_business_event: false, detail: detail || null }
      }));
    }
  }

  async function sendEvent(eventType, attribution, sessionId, engagementSeconds) {
    var identity = eventIdentity(eventType);
    var body = Object.assign({}, attribution, {
      schema_version: SCHEMA,
      event_id: identity.event_id,
      event_type: eventType,
      session_id: sessionId,
      occurred_at: identity.occurred_at,
      page_path: root.location.pathname || "/",
      engagement_seconds: Math.max(0, Math.floor(engagementSeconds || 0))
    });
    var response = await root.fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "omit",
      keepalive: true
    });
    if (!response.ok) throw new Error("buyer_event_http_" + response.status);
    var result = await response.json();
    if (!result || !result.ok || !result.receipt || result.receipt.receipt_verified !== true) {
      throw new Error("buyer_event_receipt_missing");
    }
    root.sessionStorage.setItem(
      EVENT_KEY_PREFIX + eventType + "_receipt_sha256",
      result.receipt.receipt_sha256
    );
    return result.receipt;
  }

  async function boot() {
    var attribution = readAttribution();
    if (!attribution) {
      diagnostic("inactive_missing_exact_asset_attribution");
      return;
    }
    var sessionId = readOrCreateSessionId();
    var visibleSeconds = 0;
    var pricingReceiptVerified = false;

    try {
      await sendEvent("website_session_started", attribution, sessionId, 0);
    } catch (error) {
      diagnostic("session_receipt_failed", error && error.message);
      return;
    }

    var pricing = document.getElementById("pricing");
    if (pricing && (root.location.hash === "#pricing" || pricing.getBoundingClientRect().top < root.innerHeight)) {
      try {
        await sendEvent("pricing_viewed", attribution, sessionId, visibleSeconds);
        pricingReceiptVerified = true;
      } catch (error) {
        diagnostic("pricing_receipt_failed", error && error.message);
      }
    }

    var timer = root.setInterval(async function () {
      if (document.visibilityState === "visible") visibleSeconds += 1;
      if (visibleSeconds < 30 || !pricingReceiptVerified) return;
      root.clearInterval(timer);
      try {
        await sendEvent("qualified_session", attribution, sessionId, visibleSeconds);
      } catch (error) {
        diagnostic("qualified_session_receipt_failed", error && error.message);
      }
    }, 1000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})(window, document);
