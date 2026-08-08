/*
 * The Call Taker funnel event layer.
 * Privacy-safe buyer-path browser telemetry. It contains no lead form values,
 * card data, or provider secrets; durable buyer truth stays server-side.
 */
(function () {
  "use strict";

  var root = window;
  var doc = document;
  var counter = 0;
  var config = root.TCT_FUNNEL_CONFIG || {};
  var endpoint = config.endpoint || "https://call-taker-os.vercel.app/api/public/buyer-event";
  var dryRun = config.dryRun === true;
  var allowGtag = config.allowGtag === true;
  var debug = config.debug === true || /(?:^|[?&])tct_debug=1(?:&|$)/.test(root.location.search);
  var allowedEvents = {
    homepage_view: true,
    homepage_cta_click: true,
    pricing_view: true,
    pricing_plan_click: true,
    card_checkout_view: true,
    checkout_intent_opened: true,
    checkout_intent_submitted: true,
    checkout_request_accepted_ui: true,
    checkout_request_error_ui: true,
    checkout_waiting_ui_shown: true,
    lead_form_started: true,
    follow_up_consent_selected_ui: true,
    lead_request_submitted_ui: true,
    lead_request_accepted_ui: true,
    lead_request_error_ui: true,
    demo_view: true,
    demo_preview_intent: true,
    demo_preview_rendered_ui: true,
    lead_capture_open: true,
    paid_view: true,
    paid_cta_click: true,
    paid_demo_click: true
    ,checkout_continuity_view: true
    ,after_hours_answering_service_view: true
    ,after_hours_call_checklist_view: true
    ,ai_receptionist_view: true
  };

  root.__tctFunnelEvents = root.__tctFunnelEvents || [];

  function uuid() {
    return root.crypto && typeof root.crypto.randomUUID === "function" ? root.crypto.randomUUID() : "10000000-1000-4000-8000-100000000000".replace(/[018]/g, function (character) { var number = Number(character); return (number ^ (root.crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (number / 4)))).toString(16); });
  }

  function sessionValue(key) {
    try {
      var value = root.sessionStorage.getItem(key);
      if (validUuid(value)) return value;
      value = uuid(); root.sessionStorage.setItem(key, value); return value;
    } catch (_) { return uuid(); }
  }

  function validUuid(value) {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value || "");
  }

  function validContentAttribution(name, value) {
    var candidate = (value || "").toString().trim();
    if (name === "tct_item_id") {
      return /^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$/.test(candidate) ? candidate : "";
    }
    if (name === "tct_asset_sha256" || name === "tct_publication_seed_sha256") {
      return /^[a-f0-9]{64}$/i.test(candidate) ? candidate.toLowerCase() : "";
    }
    return "";
  }

  function optionalIssuedSource(value) {
    var candidate = (value || "").toString().trim().toLowerCase();
    var aliases = { "meet-gideon":"website", meet_gideon:"website", homepage:"website", home:"website", demo:"website", pricing:"website", meta:"facebook", fb:"facebook", ig:"instagram", li:"linkedin", newsletter:"email", googleads:"google", google_ads:"google" };
    candidate = aliases[candidate] || candidate;
    return ["bing","content","direct","email","facebook","gideon_demo","google","instagram","linkedin","organic","paid_search","paid_social","partner","referral","social","website","youtube"].indexOf(candidate) >= 0 ? candidate : "";
  }

  function issuedSource(value) {
    return optionalIssuedSource(value) || "direct";
  }

  function issuedChannel(value) {
    var candidate = (value || "").toString().trim().toLowerCase().replace(/[\s-]+/g, "_");
    var aliases = { cpc:"paid_search", ppc:"paid_search", sem:"paid_search", paidsocial:"paid_social" };
    candidate = aliases[candidate] || candidate;
    return ["direct","email","organic","organic_social","paid_search","paid_social","partner","referral","search","social","voice","web"].indexOf(candidate) >= 0 ? candidate : "";
  }

  function issuedSlug(value) {
    var candidate = (value || "").toString().trim().toLowerCase();
    return candidate.length <= 120 && (candidate.match(/[0-9]/g) || []).length <= 6 && /^[a-z][a-z0-9]*(?:[_-][a-z0-9]+)*$/.test(candidate) ? candidate : "";
  }

  function attribution() {
    var stored = {};
    try { stored = JSON.parse(root.sessionStorage.getItem("tct_attribution") || "{}"); } catch (_) {}
    var itemId = validContentAttribution("tct_item_id", getParam("tct_item_id")) || validContentAttribution("tct_item_id", stored.tct_item_id || stored.content_key);
    var assetSha256 = validContentAttribution("tct_asset_sha256", getParam("tct_asset_sha256")) || validContentAttribution("tct_asset_sha256", stored.tct_asset_sha256);
    var publicationSeedSha256 = validContentAttribution("tct_publication_seed_sha256", getParam("tct_publication_seed_sha256")) || validContentAttribution("tct_publication_seed_sha256", stored.tct_publication_seed_sha256);
    return {
      source: issuedSource(getParam("utm_source") || getParam("source") || stored.utm_source || stored.source || "direct"),
      source_param: optionalIssuedSource(getParam("source") || stored.source),
      utm_source: optionalIssuedSource(getParam("utm_source") || stored.utm_source),
      channel: issuedChannel(getParam("utm_medium") || stored.utm_medium),
      campaign: issuedSlug(getParam("utm_campaign") || stored.utm_campaign),
      utm_content: issuedSlug(getParam("utm_content") || stored.utm_content),
      utm_term: issuedSlug(getParam("utm_term") || stored.utm_term),
      content_key: itemId,
      tct_item_id: itemId,
      tct_asset_sha256: assetSha256,
      tct_publication_seed_sha256: publicationSeedSha256
    };
  }

  function captureAttribution() {
    var stored = {};
    try { stored = JSON.parse(root.sessionStorage.getItem("tct_attribution") || "{}"); } catch (_) {}
    var normalizers = { utm_source: optionalIssuedSource, utm_medium: issuedChannel, utm_campaign: issuedSlug, utm_content: issuedSlug, utm_term: issuedSlug };
    Object.keys(normalizers).forEach(function (key) {
      var raw = getParam(key) || stored[key] || "";
      var value = normalizers[key](raw);
      if (value) stored[key] = value;
      else delete stored[key];
    });
    var source = optionalIssuedSource(getParam("source") || stored.source);
    if (source) stored.source = source;
    else delete stored.source;
    ["tct_item_id","tct_asset_sha256","tct_publication_seed_sha256"].forEach(function (key) {
      var value = validContentAttribution(key, getParam(key)) || validContentAttribution(key, stored[key] || (key === "tct_item_id" ? stored.content_key : ""));
      if (value) stored[key] = value;
      else delete stored[key];
    });
    if (stored.tct_item_id) stored.content_key = stored.tct_item_id;
    else delete stored.content_key;
    try { root.sessionStorage.setItem("tct_attribution", JSON.stringify(stored)); } catch (_) {}
    var incomingCorrelation = getParam("correlation_id");
    if (validUuid(incomingCorrelation)) {
      try { root.sessionStorage.setItem("tct_correlation_id_v1", incomingCorrelation); } catch (_) {}
    }
  }

  function canonicalEvent(eventName, payload) {
    if (["homepage_view","demo_view","card_checkout_view","paid_view","checkout_continuity_view","after_hours_answering_service_view","after_hours_call_checklist_view","ai_receptionist_view"].indexOf(eventName) >= 0) return "page_view";
    if (["homepage_cta_click","pricing_plan_click","paid_cta_click","paid_demo_click","lead_capture_open"].indexOf(eventName) >= 0) {
      if (payload && payload.destination_type === "demo") return "demo_preview_intent";
      if (payload && payload.destination_type === "card_checkout") return "checkout_intent_opened";
      return "cta_intent";
    }
    if (eventName === "pricing_view") return "pricing_viewed";
    return eventName;
  }

  function getParam(name) {
    try {
      return new URLSearchParams(root.location.search).get(name) || "";
    } catch (error) {
      return "";
    }
  }

  function deviceHint() {
    var width = root.innerWidth || 0;
    if (width && width < 720) return "mobile";
    if (width && width < 1024) return "tablet";
    return "desktop";
  }

  function scrub(value, fallback) {
    var text = (value || fallback || "").toString().replace(/\s+/g, " ").trim();
    return text.slice(0, 90);
  }

  function detailSlug(value) {
    return scrub(value, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 90);
  }

  function payloadFrom(target, eventName) {
    var dataset = target ? target.dataset || {} : {};
    var page = dataset.tctPage || doc.body.getAttribute("data-tct-page") || root.location.pathname || "/";
    var plan = dataset.tctPlan || getParam("plan") || "";
    var cta = dataset.tctCta || (target && target.textContent ? target.textContent : "");
    var destinationType = dataset.tctDestination || "";
    var source = dataset.tctSource || getParam("source") || getParam("utm_source") || "";

    counter += 1;
    return {
      event_name: eventName,
      page: scrub(page, "/"),
      plan: scrub(plan, ""),
      cta: scrub(cta, ""),
      destination_type: scrub(destinationType, ""),
      source: scrub(source, ""),
      utm_source: scrub(getParam("utm_source"), ""),
      utm_campaign: scrub(getParam("utm_campaign"), ""),
      device_hint: deviceHint(),
      timestamp: new Date().toISOString(),
      session_id: sessionValue("tct_buyer_session_v1"),
      correlation_id: sessionValue("tct_correlation_id_v1"),
      ctos_learning_tag: scrub(dataset.tctLearningTag, ""),
      event_id: uuid()
    };
  }

  function persist(payload) {
    if (dryRun) return;
    var attr = attribution();
    var planMap = { afterhours:"afterhours_97", full247:"recommended_497", custom:"operational_997_plus" };
    var body = {
      event_id: payload.event_id, event_type: payload.event_name, occurred_at: payload.timestamp,
      session_id: payload.session_id, correlation_id: payload.correlation_id, page_path: root.location.pathname || "/",
      source: attr.source, channel: attr.channel || null, campaign: attr.campaign || null, utm_content: attr.utm_content || null, utm_term: attr.utm_term || null,
      plan_key: planMap[payload.plan] || payload.plan || null,
      content_key: attr.tct_item_id || null,
      source_asset_sha256: attr.tct_asset_sha256 || null,
      source_publication_seed_sha256: attr.tct_publication_seed_sha256 || null,
      details: {
        cta: detailSlug(payload.cta),
        destination: detailSlug(payload.destination_type),
        content_key: attr.content_key || ""
      }
    };
    root.fetch(endpoint, { method:"POST", headers:{ "Content-Type":"application/json" }, credentials:"omit", keepalive:true, body:JSON.stringify(body) }).catch(function () {});
  }

  function record(eventName, target) {
    if (!allowedEvents[eventName]) return null;

    var payload = payloadFrom(target || doc.body, eventName);
    payload.event_name = canonicalEvent(eventName, payload);
    root.__tctFunnelEvents.push(payload);
    persist(payload);

    if (allowGtag && typeof root.gtag === "function") {
      root.gtag("event", payload.event_name, {
        event_category: "tct_funnel",
        event_label: payload.cta || payload.page,
        page_path: payload.page,
        plan: payload.plan,
        destination_type: payload.destination_type,
        ctos_learning_tag: payload.ctos_learning_tag
      });
    }

    if (dryRun && debug && root.console && typeof root.console.info === "function") {
      root.console.info("[TCT funnel dry-run]", payload);
    }

    try {
      root.dispatchEvent(new CustomEvent("tct:funnel-event", { detail: payload }));
    } catch (error) {}

    return payload;
  }

  function initPageView() {
    var eventName = doc.body && doc.body.getAttribute("data-tct-view");
    if (eventName) record(eventName, doc.body);

  }

  function initClicks() {
    doc.addEventListener("click", function (event) {
      var target = event.target && event.target.closest ? event.target.closest("[data-tct-event]") : null;
      if (!target) return;
      record(target.getAttribute("data-tct-event"), target);
    }, true);
  }

  function initConsentedLeadForm() {
    var form = doc.querySelector("[data-tct-form='consented-lead']");
    if (!form) return;
    var started = false;
    function start() { if (started) return; started = true; record("lead_form_started", form); }
    form.addEventListener("focusin", start, true);
    form.addEventListener("input", start, true);
  }

  function preservePublicAttributionOnCtas() {
    var attr = attribution();
    var values = {
      source: attr.source_param,
      utm_source: attr.utm_source,
      utm_medium: attr.channel,
      utm_campaign: attr.campaign,
      utm_content: attr.utm_content,
      utm_term: attr.utm_term,
      correlation_id: sessionValue("tct_correlation_id_v1"),
      tct_item_id: attr.tct_item_id,
      tct_asset_sha256: attr.tct_asset_sha256,
      tct_publication_seed_sha256: attr.tct_publication_seed_sha256
    };
    doc.querySelectorAll("a[data-tct-event],a[data-preserve]").forEach(function (link) {
      var target;
      try { target = new URL(link.href, root.location.origin); } catch (_) { return; }
      if (target.origin !== root.location.origin) return;
      Object.keys(values).forEach(function (key) {
        var value = values[key];
        if (value && !target.searchParams.has(key)) target.searchParams.set(key, value.slice(0, 128));
      });
      link.href = target.pathname + target.search + target.hash;
    });
  }

  function init() {
    captureAttribution();
    preservePublicAttributionOnCtas();
    initPageView();
    initClicks();
    initConsentedLeadForm();
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  root.TCTFunnelEvents = {
    record: record,
    getEvents: function () {
      return root.__tctFunnelEvents.slice();
    }
  };
})();
