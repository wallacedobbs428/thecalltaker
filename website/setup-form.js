(function (root) {
  "use strict";

  var PLAN_OPTIONS = [
    "$97 After-Hours Capture",
    "$497 Revenue Recovery System",
    "$997+ Operational Infrastructure"
  ];

  var REQUIRED_FIELDS = [
    "plan_purchased",
    "business_name",
    "owner_name",
    "business_phone",
    "owner_cell",
    "summary_email",
    "business_hours",
    "after_hours_rules",
    "services_offered",
    "service_area",
    "emergency_rules",
    "transfer_number",
    "callback_rules",
    "ai_greeting_preference",
    "authorized_to_configure_forwarding"
  ];

  var OPTIONAL_FIELDS = [
    "square_checkout_reference",
    "square_order_id",
    "square_payment_id",
    "payment_verification_status",
    "summary_sms_number",
    "setup_guide_sms_recipient",
    "appointment_booking_rules",
    "phone_provider",
    "current_forwarding_status",
    "preferred_go_live_time",
    "what_ai_should_never_say",
    "special_notes",
    "source_url",
    "submitted_at"
  ];

  var PAYMENT_STATUSES = [
    "paid_verified",
    "paid_unverified",
    "unknown",
    "not_applicable"
  ];

  function trim(value) {
    return String(value == null ? "" : value).trim();
  }

  function emptyToNull(value) {
    var trimmed = trim(value);
    return trimmed ? trimmed : null;
  }

  function normalizeBoolean(value) {
    if (value === true) return true;
    if (value === false) return false;
    var normalized = trim(value).toLowerCase();
    return normalized === "true" || normalized === "on" || normalized === "yes" || normalized === "1";
  }

  function normalizePlan(value) {
    var raw = trim(value);
    var lower = raw.toLowerCase();

    if (PLAN_OPTIONS.indexOf(raw) !== -1) return raw;
    if (lower.indexOf("97") !== -1 || lower.indexOf("after") !== -1) return PLAN_OPTIONS[0];
    if (lower.indexOf("497") !== -1 || lower.indexOf("revenue") !== -1 || lower.indexOf("24/7") !== -1 || lower.indexOf("full247") !== -1 || lower.indexOf("starter") !== -1) return PLAN_OPTIONS[1];
    if (lower.indexOf("997") !== -1 || lower.indexOf("operational") !== -1 || lower.indexOf("custom") !== -1 || lower.indexOf("premium") !== -1 || lower.indexOf("pro") !== -1) return PLAN_OPTIONS[2];

    return raw;
  }

  function planFromQuery(search) {
    var params = new URLSearchParams(search || "");
    var plan = params.get("plan") || params.get("tier") || "";
    return normalizePlan(plan) || PLAN_OPTIONS[1];
  }

  function paymentStatusFromInput(value) {
    var status = trim(value);
    if (PAYMENT_STATUSES.indexOf(status) !== -1) return status;
    return "paid_unverified";
  }

  function phoneIsUsable(value) {
    var digits = trim(value).replace(/\D/g, "");
    return digits.length >= 10;
  }

  function emailIsUsable(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trim(value));
  }

  function makeSetupPacketId(payload) {
    var date = trim(payload.submitted_at).slice(0, 10) || new Date().toISOString().slice(0, 10);
    var business = trim(payload.business_name)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 40);
    return [date, business || "business", "setup-packet"].join("-");
  }

  function buildPayloadFromObject(input, sourceUrl, now) {
    var data = input || {};
    var url = sourceUrl || data.source_url || "";
    var params = new URLSearchParams(url.indexOf("?") === -1 ? "" : url.split("?")[1]);
    var submittedAt = data.submitted_at || now || new Date().toISOString();

    return {
      plan_purchased: normalizePlan(data.plan_purchased || planFromQuery(params.toString())),
      business_name: trim(data.business_name),
      owner_name: trim(data.owner_name),
      business_phone: trim(data.business_phone),
      owner_cell: trim(data.owner_cell),
      summary_email: trim(data.summary_email),
      business_hours: trim(data.business_hours),
      after_hours_rules: trim(data.after_hours_rules),
      services_offered: trim(data.services_offered),
      service_area: trim(data.service_area),
      emergency_rules: trim(data.emergency_rules),
      transfer_number: trim(data.transfer_number),
      callback_rules: trim(data.callback_rules),
      ai_greeting_preference: trim(data.ai_greeting_preference),
      authorized_to_configure_forwarding: normalizeBoolean(data.authorized_to_configure_forwarding),
      square_checkout_reference: emptyToNull(data.square_checkout_reference || params.get("checkout") || params.get("reference")),
      square_order_id: emptyToNull(data.square_order_id || params.get("orderId") || params.get("order_id")),
      square_payment_id: emptyToNull(data.square_payment_id || params.get("paymentId") || params.get("payment_id")),
      payment_verification_status: paymentStatusFromInput(data.payment_verification_status),
      summary_sms_number: emptyToNull(data.summary_sms_number),
      setup_guide_sms_recipient: emptyToNull(data.setup_guide_sms_recipient),
      appointment_booking_rules: emptyToNull(data.appointment_booking_rules),
      phone_provider: emptyToNull(data.phone_provider),
      current_forwarding_status: emptyToNull(data.current_forwarding_status),
      preferred_go_live_time: emptyToNull(data.preferred_go_live_time),
      what_ai_should_never_say: emptyToNull(data.what_ai_should_never_say),
      special_notes: emptyToNull(data.special_notes),
      source_url: url,
      submitted_at: submittedAt
    };
  }

  function buildPayloadFromForm(form, sourceUrl) {
    var data = {};
    var fields = new FormData(form);
    fields.forEach(function (value, key) {
      data[key] = value;
    });
    data.authorized_to_configure_forwarding = fields.has("authorized_to_configure_forwarding");
    return buildPayloadFromObject(data, sourceUrl || root.location.href);
  }

  function validatePayload(payload) {
    var missing = [];
    var errors = [];

    REQUIRED_FIELDS.forEach(function (field) {
      var value = payload[field];
      if (field === "authorized_to_configure_forwarding") {
        if (value !== true) missing.push(field);
      } else if (!trim(value)) {
        missing.push(field);
      }
    });

    if (payload.plan_purchased && PLAN_OPTIONS.indexOf(payload.plan_purchased) === -1) {
      errors.push({ field: "plan_purchased", message: "Choose one of the listed plans." });
    }
    if (payload.summary_email && !emailIsUsable(payload.summary_email)) {
      errors.push({ field: "summary_email", message: "Use a real email address for setup summaries." });
    }
    ["business_phone", "owner_cell", "transfer_number", "summary_sms_number", "setup_guide_sms_recipient"].forEach(function (field) {
      if (payload[field] && !phoneIsUsable(payload[field])) {
        errors.push({ field: field, message: "Use a phone number with at least 10 digits." });
      }
    });
    if (payload.payment_verification_status && PAYMENT_STATUSES.indexOf(payload.payment_verification_status) === -1) {
      errors.push({ field: "payment_verification_status", message: "Payment verification status is not recognized." });
    }

    return {
      valid: missing.length === 0 && errors.length === 0,
      missing_fields: missing,
      errors: errors
    };
  }

  function deriveSetupResponse(payload) {
    var validation = validatePayload(payload);
    var forwardingStatus = trim(payload.current_forwarding_status).toLowerCase();
    var provider = trim(payload.phone_provider).toLowerCase();
    var needsForwardingHelp = !provider || provider.indexOf("not sure") !== -1 || !forwardingStatus || forwardingStatus.indexOf("not sure") !== -1;
    var status = needsForwardingHelp ? "forwarding_instructions_needed" : "ready_for_configuration";

    if (!validation.valid) {
      return {
        success: false,
        status: "needs_missing_required_fields",
        missing_fields: validation.missing_fields,
        errors: validation.errors,
        setup_packet_id: null,
        setup_readiness_score: 0
      };
    }

    return {
      success: true,
      status: status,
      missing_fields: [],
      errors: [],
      setup_packet_id: makeSetupPacketId(payload),
      setup_readiness_score: needsForwardingHelp ? 82 : 100,
      payment_verification_status: payload.payment_verification_status
    };
  }

  function markInvalidFields(form, validation) {
    var invalid = validation.missing_fields.concat(validation.errors.map(function (item) { return item.field; }));
    Array.prototype.forEach.call(form.querySelectorAll("[name]"), function (field) {
      field.classList.toggle("is-invalid", invalid.indexOf(field.name) !== -1);
    });
  }

  function showFormMessage(message, type) {
    var target = root.document && root.document.querySelector("[data-setup-form-message]");
    if (!target) return;
    target.textContent = message;
    target.dataset.state = type || "info";
    target.hidden = false;
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function initPlanSelection() {
    if (!root.document) return;
    var select = root.document.querySelector("[name='plan_purchased']");
    if (!select) return;
    var plan = planFromQuery(root.location.search);
    if (PLAN_OPTIONS.indexOf(plan) !== -1) {
      select.value = plan;
    }
  }

  function initSetupForm() {
    if (!root.document) return;
    initPlanSelection();

    var form = root.document.getElementById("tct-setup-form");
    if (!form) return;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var payload = buildPayloadFromForm(form, root.location.href);
      var validation = validatePayload(payload);
      markInvalidFields(form, validation);

      if (!validation.valid) {
        showFormMessage("A few setup details are missing. Fill the highlighted fields so we can build the packet cleanly.", "error");
        return;
      }

      var response = deriveSetupResponse(payload);
      try {
        root.sessionStorage.setItem("tct_setup_payload", JSON.stringify(payload));
        root.sessionStorage.setItem("tct_setup_receipt", JSON.stringify(response));
      } catch (error) {
        // Private browsing can block storage; the confirmation page still works from the URL.
      }

      var next = "setup-confirmation.html?status=" + encodeURIComponent(response.status) +
        "&packet=" + encodeURIComponent(response.setup_packet_id);
      root.location.assign(next);
    });
  }

  function initConfirmationPage() {
    if (!root.document) return;
    var packetTarget = root.document.querySelector("[data-setup-packet-id]");
    var statusTarget = root.document.querySelector("[data-setup-status]");
    var params = new URLSearchParams(root.location.search || "");
    var receipt = null;

    try {
      receipt = JSON.parse(root.sessionStorage.getItem("tct_setup_receipt") || "null");
    } catch (error) {
      receipt = null;
    }

    var packet = (receipt && receipt.setup_packet_id) || params.get("packet") || "setup packet";
    var status = (receipt && receipt.status) || params.get("status") || "received";

    if (packetTarget) packetTarget.textContent = packet;
    if (statusTarget) {
      statusTarget.textContent = status === "forwarding_instructions_needed"
        ? "Forwarding details may need one extra confirmation step."
        : "Your packet has the core setup details.";
    }
  }

  var api = {
    PLAN_OPTIONS: PLAN_OPTIONS,
    REQUIRED_FIELDS: REQUIRED_FIELDS,
    OPTIONAL_FIELDS: OPTIONAL_FIELDS,
    buildPayloadFromObject: buildPayloadFromObject,
    buildPayloadFromForm: buildPayloadFromForm,
    validatePayload: validatePayload,
    deriveSetupResponse: deriveSetupResponse,
    planFromQuery: planFromQuery,
    initSetupForm: initSetupForm,
    initConfirmationPage: initConfirmationPage
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }

  root.TCTSetupForm = api;
})(typeof window !== "undefined" ? window : globalThis);
