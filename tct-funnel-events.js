/*
 * The Call Taker funnel event layer.
 * Deploy-gated dry-run script: captures only buyer-path event metadata in memory.
 * No PII, cookies, storage, external endpoints, provider calls, or Square mutation.
 */
(function () {
  "use strict";

  var root = window;
  var doc = document;
  var counter = 0;
  var config = root.TCT_FUNNEL_CONFIG || {};
  var dryRun = config.dryRun !== false;
  var allowGtag = config.allowGtag === true;
  var debug = config.debug === true || /(?:^|[?&])tct_debug=1(?:&|$)/.test(root.location.search);
  var allowedEvents = {
    homepage_view: true,
    homepage_cta_click: true,
    pricing_view: true,
    pricing_plan_click: true,
    precheckout_view: true,
    precheckout_plan_detected: true,
    square_outbound_click: true,
    setup_view: true,
    setup_form_started: true,
    setup_form_submitted: true,
    setup_confirmation_view: true,
    demo_view: true,
    demo_preview_built: true,
    lead_capture_open: true,
    demo_call_tap: true,
    text_us_tap: true,
    paid_view: true,
    paid_cta_click: true,
    paid_demo_click: true
  };

  root.__tctFunnelEvents = root.__tctFunnelEvents || [];

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
      session_placeholder: "",
      ctos_learning_tag: scrub(dataset.tctLearningTag, ""),
      event_id: "tct_" + Date.now().toString(36) + "_" + counter
    };
  }

  function record(eventName, target) {
    if (!allowedEvents[eventName]) return null;

    var payload = payloadFrom(target || doc.body, eventName);
    root.__tctFunnelEvents.push(payload);

    if (allowGtag && typeof root.gtag === "function") {
      root.gtag("event", eventName, {
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

    if (eventName === "precheckout_view") {
      record("precheckout_plan_detected", doc.body);
    }
  }

  function initClicks() {
    doc.addEventListener("click", function (event) {
      var target = event.target && event.target.closest ? event.target.closest("[data-tct-event]") : null;
      if (!target) return;
      record(target.getAttribute("data-tct-event"), target);
    }, true);
  }

  function initSetupForm() {
    var form = doc.querySelector("[data-tct-form='setup']");
    if (!form) return;

    var started = false;
    function start() {
      if (started) return;
      started = true;
      record(form.getAttribute("data-tct-event-start") || "setup_form_started", form);
    }

    form.addEventListener("focusin", start, true);
    form.addEventListener("input", start, true);
    form.addEventListener("submit", function () {
      record(form.getAttribute("data-tct-event-submit") || "setup_form_submitted", form);
    }, true);
  }

  function init() {
    initPageView();
    initClicks();
    initSetupForm();
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
