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
    "gideon_answer_mode",
    "business_hours",
    "business_default_open_time",
    "business_default_close_time",
    "business_timezone",
    "services_offered",
    "service_area",
    "emergency_rules",
    "urgent_action_preference",
    "summary_destination",
    "phone_provider",
    "current_forwarding_status",
    "forwarding_ability",
    "what_ai_should_never_say",
    "authorized_to_configure_forwarding"
  ];

  var OPTIONAL_FIELDS = [
    "square_checkout_reference",
    "square_order_id",
    "square_payment_id",
    "payment_verification_status",
    "summary_sms_number",
    "setup_guide_sms_recipient",
    "transfer_number",
    "after_hours_rules",
    "callback_rules",
    "appointment_booking_rules",
    "ai_greeting_preference",
    "preferred_go_live_time",
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

  var ANSWER_MODE_OPTIONS = [
    "after-hours",
    "overflow",
    "all calls",
    "not sure"
  ];

  var URGENT_ACTION_OPTIONS = [
    "transfer",
    "text/call the owner",
    "summarize only",
    "not sure"
  ];

  var FORWARDING_ABILITY_OPTIONS = [
    "yes",
    "no",
    "not sure"
  ];

  var BUSINESS_TIMEZONE_OPTIONS = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Phoenix",
    "America/Los_Angeles",
    "America/Anchorage",
    "Pacific/Honolulu"
  ];

  var SETUP_PACKET_ENDPOINT = "https://call-taker-os.vercel.app/api/public/setup-intake";

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
    return normalizePlan(plan);
  }

  function trialReceiptFromQuery(search) {
    var params = new URLSearchParams(search || "");
    var receipt = trim(params.get("receipt"));
    return params.get("trial") === "started" && /^[a-f0-9]{64}$/i.test(receipt) ? receipt.toLowerCase() : "";
  }

  function setupBindingToken(hash) {
    var params = new URLSearchParams(String(hash || "").replace(/^#/, ""));
    var token = trim(params.get("binding"));
    if (!token) {
      try { token = trim(root.sessionStorage && root.sessionStorage.getItem("tct_setup_binding")); } catch (error) { token = ""; }
    }
    return /^v1\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(token) ? token : "";
  }

  function paymentStatusFromInput(value) {
    var status = trim(value);
    if (PAYMENT_STATUSES.indexOf(status) !== -1) return status;
    return "paid_unverified";
  }

  function normalizeOption(value, options) {
    var raw = trim(value);
    var lower = raw.toLowerCase();
    for (var index = 0; index < options.length; index += 1) {
      if (options[index].toLowerCase() === lower) return options[index];
    }
    return raw;
  }

  function phoneIsUsable(value) {
    var digits = trim(value).replace(/\D/g, "");
    return digits.length >= 10;
  }

  function emailIsUsable(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trim(value));
  }

  function timeIsUsable(value) {
    return /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(trim(value));
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
    var answerMode = normalizeOption(data.gideon_answer_mode, ANSWER_MODE_OPTIONS);
    var urgentAction = normalizeOption(data.urgent_action_preference, URGENT_ACTION_OPTIONS);
    var forwardingAbility = normalizeOption(data.forwarding_ability, FORWARDING_ABILITY_OPTIONS);
    var selectedPhoneProvider = trim(data.phone_provider);
    var resolvedPhoneProvider = selectedPhoneProvider === "Other / not listed"
      ? trim(data.phone_provider_other)
      : selectedPhoneProvider;

    return {
      plan_purchased: normalizePlan(data.plan_purchased || planFromQuery(params.toString())),
      business_name: trim(data.business_name),
      owner_name: trim(data.owner_name),
      business_phone: trim(data.business_phone),
      owner_cell: trim(data.owner_cell),
      summary_email: trim(data.summary_email),
      gideon_answer_mode: answerMode,
      business_hours: trim(data.business_hours),
      business_default_open_time: trim(data.business_default_open_time),
      business_default_close_time: trim(data.business_default_close_time),
      business_timezone: normalizeOption(data.business_timezone, BUSINESS_TIMEZONE_OPTIONS),
      after_hours_rules: emptyToNull(data.after_hours_rules) || (answerMode ? "Answer mode: " + answerMode : ""),
      services_offered: trim(data.services_offered),
      service_area: trim(data.service_area),
      emergency_rules: trim(data.emergency_rules),
      transfer_number: trim(data.transfer_number),
      urgent_action_preference: urgentAction,
      callback_rules: emptyToNull(data.callback_rules) || (urgentAction ? "Urgent action preference: " + urgentAction : ""),
      summary_destination: trim(data.summary_destination),
      ai_greeting_preference: trim(data.ai_greeting_preference),
      forwarding_ability: forwardingAbility,
      authorized_to_configure_forwarding: normalizeBoolean(data.authorized_to_configure_forwarding),
      square_checkout_reference: emptyToNull(data.square_checkout_reference || trialReceiptFromQuery(params.toString())),
      square_order_id: emptyToNull(data.square_order_id || params.get("orderId") || params.get("order_id")),
      square_payment_id: emptyToNull(data.square_payment_id || params.get("paymentId") || params.get("payment_id")),
      payment_verification_status: paymentStatusFromInput(data.payment_verification_status),
      summary_sms_number: emptyToNull(data.summary_sms_number),
      setup_guide_sms_recipient: emptyToNull(data.setup_guide_sms_recipient),
      appointment_booking_rules: emptyToNull(data.appointment_booking_rules),
      phone_provider: emptyToNull(resolvedPhoneProvider),
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

  function prefillCheckoutContact() {
    if (!root.document) return;
    var contact = null;
    try { contact = JSON.parse(root.sessionStorage.getItem("tct_checkout_contact") || "null"); } catch (error) { contact = null; }
    if (!contact) return;
    ["owner_name", "summary_email", "owner_cell"].forEach(function (fieldName) {
      var field = root.document.querySelector("[name='" + fieldName + "']");
      if (field && !field.value && contact[fieldName]) field.value = trim(contact[fieldName]);
    });
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
    if (payload.business_default_open_time && !timeIsUsable(payload.business_default_open_time)) {
      errors.push({ field: "business_default_open_time", message: "Use a valid default opening time." });
    }
    if (payload.business_default_close_time && !timeIsUsable(payload.business_default_close_time)) {
      errors.push({ field: "business_default_close_time", message: "Use a valid default closing time." });
    }
    if (
      timeIsUsable(payload.business_default_open_time) &&
      timeIsUsable(payload.business_default_close_time) &&
      payload.business_default_open_time === payload.business_default_close_time
    ) {
      errors.push({ field: "business_default_close_time", message: "Default opening and closing times must be different." });
    }
    if (payload.business_timezone && BUSINESS_TIMEZONE_OPTIONS.indexOf(payload.business_timezone) === -1) {
      errors.push({ field: "business_timezone", message: "Choose a listed IANA business timezone." });
    }
    ["business_phone", "owner_cell", "transfer_number", "summary_sms_number", "setup_guide_sms_recipient"].forEach(function (field) {
      if (payload[field] && !phoneIsUsable(payload[field])) {
        errors.push({ field: field, message: "Use a phone number with at least 10 digits." });
      }
    });
    if (payload.payment_verification_status && PAYMENT_STATUSES.indexOf(payload.payment_verification_status) === -1) {
      errors.push({ field: "payment_verification_status", message: "Payment verification status is not recognized." });
    }
    if (payload.gideon_answer_mode && ANSWER_MODE_OPTIONS.indexOf(payload.gideon_answer_mode) === -1) {
      errors.push({ field: "gideon_answer_mode", message: "Choose when Gideon should answer." });
    }
    if (payload.urgent_action_preference && URGENT_ACTION_OPTIONS.indexOf(payload.urgent_action_preference) === -1) {
      errors.push({ field: "urgent_action_preference", message: "Choose what should happen with urgent calls." });
    }
    if (payload.forwarding_ability && FORWARDING_ABILITY_OPTIONS.indexOf(payload.forwarding_ability) === -1) {
      errors.push({ field: "forwarding_ability", message: "Choose whether you can forward calls." });
    }
    if (payload.urgent_action_preference === "transfer" && !payload.transfer_number) {
      errors.push({ field: "transfer_number", message: "Add the phone number Gideon should use for urgent transfers." });
    }

    return {
      valid: missing.length === 0 && errors.length === 0,
      missing_fields: missing,
      errors: errors
    };
  }

  function deriveSetupResponse(payload) {
    var validation = validatePayload(payload);
    var plan = trim(payload.plan_purchased).toLowerCase();
    var isCustomPlan = plan.indexOf("997") !== -1 || plan.indexOf("operational") !== -1 || plan.indexOf("custom") !== -1;
    var forwardingHelpNeeded = payload.forwarding_ability === "no" || payload.forwarding_ability === "not sure";
    var status = isCustomPlan ? "manual_review_needed" : (forwardingHelpNeeded ? "setup_help_needed" : "internal_build_ready");

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
      setup_readiness_score: isCustomPlan ? 90 : (forwardingHelpNeeded ? 95 : 100),
      forwarding_help_needed: forwardingHelpNeeded,
      payment_verification_status: payload.payment_verification_status
    };
  }

  function buildSetupNotes(payload, response) {
    return [
      "Setup packet ID: " + response.setup_packet_id,
      "Plan: " + payload.plan_purchased,
      "Payment verification: " + payload.payment_verification_status,
      "Business: " + payload.business_name,
      "Best contact: " + payload.owner_name,
      "Business phone: " + payload.business_phone,
      "Best setup mobile: " + payload.owner_cell,
      "Summary destination: " + payload.summary_destination,
      "When Gideon should answer: " + payload.gideon_answer_mode,
      "Business hours: " + payload.business_hours,
      "Default open time: " + payload.business_default_open_time,
      "Default close time: " + payload.business_default_close_time,
      "Business timezone: " + payload.business_timezone,
      "After-hours rules: " + payload.after_hours_rules,
      "Top call types: " + payload.services_offered,
      "Service area: " + payload.service_area,
      "Urgent/emergency definition: " + payload.emergency_rules,
      "Urgent action preference: " + payload.urgent_action_preference,
      "Derived urgent action detail: " + payload.callback_rules,
      "Forwarding ability: " + payload.forwarding_ability,
      "Hard do-not-say/do-not-promise rules: " + payload.what_ai_should_never_say,
      "Source URL: " + payload.source_url
    ].join("\n");
  }

  function buildSetupLeadPayload(payload, response) {
    var nameParts = trim(payload.owner_name).split(/\s+/).filter(Boolean);
    return {
      kind: "website_setup_packet",
      source: "website_setup_form",
      page: "/setup.html",
      firstName: nameParts[0] || "",
      lastName: nameParts.slice(1).join(" "),
      name: payload.owner_name,
      company: payload.business_name,
      companyName: payload.business_name,
      business_name: payload.business_name,
      email: payload.summary_email,
      phone: payload.owner_cell || payload.business_phone,
      tags: [
        "website_setup_packet",
        "buyer_path",
        "plan:" + payload.plan_purchased.replace(/[^a-z0-9]+/gi, "_").toLowerCase(),
        "answer_mode:" + payload.gideon_answer_mode.replace(/[^a-z0-9]+/gi, "_").toLowerCase(),
        "forwarding:" + payload.forwarding_ability.replace(/[^a-z0-9]+/gi, "_").toLowerCase()
      ],
      notes: buildSetupNotes(payload, response),
      setup_packet_id: response.setup_packet_id,
      setup_status: response.status,
      setup_readiness_score: response.setup_readiness_score,
      setup_packet: payload,
      payment_verification_status: payload.payment_verification_status,
      submitted_at: payload.submitted_at,
      setup_binding_token: setupBindingToken(root.location && root.location.hash)
    };
  }

  function submitSetupPacket(payload, response) {
    if (!root.fetch) {
      return Promise.resolve({
        ok: false,
        forwarded: false,
        reason: "fetch_unavailable"
      });
    }

    return root.fetch(SETUP_PACKET_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildSetupLeadPayload(payload, response))
    }).then(function (httpResponse) {
      if (!httpResponse.ok) {
        throw new Error("setup_packet_intake_failed_" + httpResponse.status);
      }
      return httpResponse.json().catch(function () {
        return {};
      });
    }).then(function (body) {
      return {
        ok: true,
        forwarded: body.forwarded === true,
        id: body.id || null,
        template_key: body.template_key || null
      };
    });
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
    var field = root.document.querySelector("[name='plan_purchased']");
    var display = root.document.getElementById("planPurchasedDisplay");
    var receiptField = root.document.querySelector("[name='square_checkout_reference']");
    if (!field) return;
    var plan = planFromQuery(root.location.search);
    var receipt = trialReceiptFromQuery(root.location.search);
    field.value = PLAN_OPTIONS.indexOf(plan) !== -1 ? plan : "";
    if (receiptField) receiptField.value = receipt;
    if (display) {
      display.querySelector("strong").textContent = field.value || "Checkout confirmation required";
      display.classList.toggle("setup-access-blocked", !field.value || !receipt);
    }
  }

  function initSetupForm() {
    if (!root.document) return;
    prefillCheckoutContact();
    initPlanSelection();

    var form = root.document.getElementById("tct-setup-form");
    if (!form) return;
    var purchasedPlan = planFromQuery(root.location.search);
    var trialReceipt = trialReceiptFromQuery(root.location.search);
    var bindingToken = setupBindingToken(root.location.hash);
    if (PLAN_OPTIONS.indexOf(purchasedPlan) === -1 || !trialReceipt || !bindingToken) {
      var submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;
      showFormMessage("A signed checkout confirmation is required before setup. Return to pricing and complete the exact plan checkout; setup will open automatically after Square confirms enrollment.", "error");
      return;
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (form.dataset.submitting === "true") return;

      var payload = buildPayloadFromForm(form, root.location.href);
      var validation = validatePayload(payload);
      markInvalidFields(form, validation);

      if (!validation.valid) {
        showFormMessage("A few required setup answers are missing. Fill the highlighted fields so the internal build can start cleanly.", "error");
        return;
      }

      form.dataset.submitting = "true";
      showFormMessage("Sending your setup questions...", "info");
      var response = deriveSetupResponse(payload);

      submitSetupPacket(payload, response).then(function (intake) {
        if (!intake.ok) throw new Error(intake.reason || "setup_packet_intake_failed");
        response.intake_status = "ctos_packet_received";
        response.intake_id = intake.id || null;
        response.intake_forwarded = intake.forwarded === true;
      }).then(function () {
        try {
          root.sessionStorage.setItem("tct_setup_payload", JSON.stringify(payload));
          root.sessionStorage.setItem("tct_setup_receipt", JSON.stringify(response));
          root.sessionStorage.removeItem("tct_setup_binding");
          root.sessionStorage.removeItem("tct_checkout_contact");
        } catch (error) {
          // Private browsing can block storage; the confirmation page still works from the URL.
        }

        var next = "setup-confirmation.html?status=" + encodeURIComponent(response.status) +
          "&packet=" + encodeURIComponent(response.setup_packet_id) +
          "&intake=" + encodeURIComponent(response.intake_status || "manual_followup_required");
        if (response.intake_id) {
          next += "&intake_id=" + encodeURIComponent(response.intake_id);
        }
        root.location.assign(next);
      }).catch(function () {
        form.dataset.submitting = "false";
        showFormMessage("Your setup answers are still here, but the secure intake did not confirm receipt. Do not start another checkout. Please retry this setup submission or contact support.", "error");
      });
    });
  }

  function initConfirmationPage() {
    if (!root.document) return;
    var packetTarget = root.document.querySelector("[data-setup-packet-id]");
    var statusTarget = root.document.querySelector("[data-setup-status]");
    var intakeTarget = root.document.querySelector("[data-setup-intake-status]");
    var params = new URLSearchParams(root.location.search || "");
    var receipt = null;

    try {
      receipt = JSON.parse(root.sessionStorage.getItem("tct_setup_receipt") || "null");
    } catch (error) {
      receipt = null;
    }

    var packet = (receipt && receipt.setup_packet_id) || params.get("packet") || "setup packet";
    var status = (receipt && receipt.status) || params.get("status") || "received";
    var intakeStatus = (receipt && receipt.intake_status) || params.get("intake") || "manual_followup_required";

    if (packetTarget) packetTarget.textContent = packet;
    if (statusTarget) {
      statusTarget.textContent = status === "manual_review_needed"
        ? "Your custom setup has the core details and may get manual review before the internal build."
        : (status === "setup_help_needed"
          ? "Your setup questions have the core details. We may send forwarding instructions or walk you through setup."
          : "Your setup questions have the core details needed for the internal build.");
    }
    if (intakeTarget) {
      intakeTarget.textContent = intakeStatus === "ctos_packet_received"
        ? "Setup packet received by The Call Taker."
        : "If we do not text you shortly, use the Text Us button below with your packet ID.";
    }
  }

  var api = {
    PLAN_OPTIONS: PLAN_OPTIONS,
    REQUIRED_FIELDS: REQUIRED_FIELDS,
    OPTIONAL_FIELDS: OPTIONAL_FIELDS,
    ANSWER_MODE_OPTIONS: ANSWER_MODE_OPTIONS,
    URGENT_ACTION_OPTIONS: URGENT_ACTION_OPTIONS,
    FORWARDING_ABILITY_OPTIONS: FORWARDING_ABILITY_OPTIONS,
    BUSINESS_TIMEZONE_OPTIONS: BUSINESS_TIMEZONE_OPTIONS,
    buildPayloadFromObject: buildPayloadFromObject,
    buildPayloadFromForm: buildPayloadFromForm,
    buildSetupLeadPayload: buildSetupLeadPayload,
    validatePayload: validatePayload,
    deriveSetupResponse: deriveSetupResponse,
    submitSetupPacket: submitSetupPacket,
    planFromQuery: planFromQuery,
    trialReceiptFromQuery: trialReceiptFromQuery,
    setupBindingToken: setupBindingToken,
    initSetupForm: initSetupForm,
    initConfirmationPage: initConfirmationPage
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }

  root.TCTSetupForm = api;
})(typeof window !== "undefined" ? window : globalThis);
