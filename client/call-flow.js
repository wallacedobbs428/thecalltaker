(function(root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.TCTCallFlow = factory();
  }
})(typeof window !== "undefined" ? window : globalThis, function() {
  var STORAGE_KEY = "tct_call_setup_v1";

  function clean(value) {
    return String(value || "").trim().replace(/\s+/g, " ");
  }

  function normalizePhone(value) {
    var digits = String(value || "").replace(/\D/g, "");
    if (!digits) return "";
    if (digits.length === 10) return "+1" + digits;
    if (digits.length === 11 && digits.charAt(0) === "1") return "+" + digits;
    return clean(value);
  }

  function phoneLooksUsable(value) {
    var digits = String(value || "").replace(/\D/g, "");
    return !digits || digits.length === 10 || (digits.length === 11 && digits.charAt(0) === "1");
  }

  function validateStep(step, setup) {
    var errors = {};
    var data = setup || {};

    if (step === 1) {
      if (!clean(data.businessName)) errors.businessName = "Business name is required.";
      if (!clean(data.industry)) errors.industry = "Choose an industry.";
      if (!clean(data.location)) errors.location = "City and state are required.";
    }

    if (step === 2) {
      if (!clean(data.weekdayHours)) errors.weekdayHours = "Weekday hours are required.";
      if (!clean(data.saturdayHours)) errors.saturdayHours = "Saturday hours are required. Use Closed if needed.";
      if (!clean(data.sundayHours)) errors.sundayHours = "Sunday hours are required. Use Closed if needed.";
    }

    if (step === 3) {
      if (!clean(data.services)) errors.services = "List the services callers can ask about.";
      if (!clean(data.serviceArea)) errors.serviceArea = "Service area is required.";
    }

    if (step === 4) {
      if (!clean(data.greeting)) errors.greeting = "Greeting is required.";
      if (data.forwardNumber && !phoneLooksUsable(data.forwardNumber)) {
        errors.forwardNumber = "Enter a 10 digit US number or leave it blank.";
      }
    }

    return errors;
  }

  function hasErrors(errors) {
    return Object.keys(errors || {}).length > 0;
  }

  function normalizeSetup(setup) {
    var data = setup || {};
    return {
      businessName: clean(data.businessName),
      industry: clean(data.industry),
      location: clean(data.location),
      weekdayHours: clean(data.weekdayHours),
      saturdayHours: clean(data.saturdayHours),
      sundayHours: clean(data.sundayHours),
      services: clean(data.services),
      serviceArea: clean(data.serviceArea),
      greeting: clean(data.greeting),
      forwardNumber: normalizePhone(data.forwardNumber),
      savedAt: data.savedAt || new Date().toISOString(),
    };
  }

  function validateSetup(setup) {
    var errors = {};
    [1, 2, 3, 4].forEach(function(step) {
      var stepErrors = validateStep(step, setup);
      Object.keys(stepErrors).forEach(function(key) {
        errors[key] = stepErrors[key];
      });
    });
    return errors;
  }

  function saveSetup(storage, setup) {
    var normalized = normalizeSetup(setup);
    var errors = validateSetup(normalized);
    if (hasErrors(errors)) {
      return { ok: false, errors: errors, setup: normalized };
    }
    storage.setItem(STORAGE_KEY, JSON.stringify(normalized));
    return { ok: true, errors: {}, setup: normalized };
  }

  function loadSetup(storage) {
    try {
      var raw = storage.getItem(STORAGE_KEY);
      return raw ? normalizeSetup(JSON.parse(raw)) : null;
    } catch (error) {
      return null;
    }
  }

  function dashboardState(setup) {
    var errors = setup ? validateSetup(setup) : { setup: "No call setup has been saved." };
    var complete = !hasErrors(errors);
    return {
      complete: complete,
      statusLabel: complete ? "GIDEON IS READY" : "SETUP NEEDS ATTENTION",
      statusTone: complete ? "live" : "pending",
      businessName: complete ? setup.businessName : "Client",
      greeting: complete ? setup.greeting : "Complete onboarding before Gideon starts answering with a custom greeting.",
      weekdayHours: complete ? setup.weekdayHours : "Not configured",
      saturdayHours: complete ? setup.saturdayHours : "Not configured",
      sundayHours: complete ? setup.sundayHours : "Not configured",
      afterHours: complete
        ? (setup.forwardNumber ? "Forward urgent calls to " + setup.forwardNumber : "Take message and send summary")
        : "Blocked until setup is complete",
      errors: errors,
    };
  }

  return {
    STORAGE_KEY: STORAGE_KEY,
    clean: clean,
    normalizePhone: normalizePhone,
    validateStep: validateStep,
    validateSetup: validateSetup,
    saveSetup: saveSetup,
    loadSetup: loadSetup,
    dashboardState: dashboardState,
  };
});
