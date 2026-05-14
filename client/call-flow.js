(function(root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.TCTCallFlow = factory();
  }
})(typeof window !== "undefined" ? window : globalThis, function() {
  var STORAGE_KEY = "tct_call_setup_v1";
  var SCHEMA_VERSION = 2;
  var COMPLETION_COMPLETE = "complete";
  var COMPLETION_INCOMPLETE = "incomplete";
  var PROVIDER_STATUS_NOT_CONFIGURED = "not-configured";
  var FIELD_LABELS = {
    businessName: "Business name",
    industry: "Industry",
    location: "Location",
    weekdayHours: "Weekday hours",
    saturdayHours: "Saturday hours",
    sundayHours: "Sunday hours",
    services: "Services",
    serviceArea: "Service area",
    greeting: "Phone greeting",
    forwardNumber: "Emergency forward number",
  };

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

  function formSetupFromContract(setup) {
    var data = setup || {};
    var business = data.business || {};
    var hours = data.hours || {};
    var services = data.services || {};
    var callHandling = data.callHandling || {};

    return {
      businessName: clean(business.name || data.businessName),
      industry: clean(business.industry || data.industry),
      location: clean(business.location || data.location),
      weekdayHours: clean(hours.weekday || data.weekdayHours),
      saturdayHours: clean(hours.saturday || data.saturdayHours),
      sundayHours: clean(hours.sunday || data.sundayHours),
      services: clean(Array.isArray(services.offered) ? services.offered.join(", ") : data.services),
      serviceArea: clean(services.serviceArea || data.serviceArea),
      greeting: clean(callHandling.greeting || data.greeting),
      forwardNumber: normalizePhone(callHandling.emergencyForwardNumber || data.forwardNumber),
    };
  }

  function validateFormSetup(setup) {
    var errors = {};
    [1, 2, 3, 4].forEach(function(step) {
      var stepErrors = validateStep(step, setup);
      Object.keys(stepErrors).forEach(function(key) {
        errors[key] = stepErrors[key];
      });
    });
    return errors;
  }

  function missingItems(errors) {
    return Object.keys(errors || {}).map(function(key) {
      return {
        key: key,
        label: FIELD_LABELS[key] || key,
        message: errors[key],
      };
    });
  }

  function splitServices(value) {
    return clean(value)
      .split(",")
      .map(clean)
      .filter(Boolean);
  }

  function serializeSetup(input, existing, options) {
    var now = new Date().toISOString();
    var opts = options || {};
    var form = formSetupFromContract(input);
    var errors = validateFormSetup(form);
    var prior = existing || {};
    var meta = prior.meta || {};

    return {
      schemaVersion: SCHEMA_VERSION,
      setupCompletion: hasErrors(errors) ? COMPLETION_INCOMPLETE : COMPLETION_COMPLETE,
      business: {
        name: form.businessName,
        industry: form.industry,
        location: form.location,
      },
      hours: {
        weekday: form.weekdayHours,
        saturday: form.saturdayHours,
        sunday: form.sundayHours,
      },
      services: {
        offered: splitServices(form.services),
        serviceArea: form.serviceArea,
      },
      callHandling: {
        greeting: form.greeting,
        emergencyForwardNumber: form.forwardNumber,
      },
      activation: {
        liveProviderConfigured: false,
        providerStatus: PROVIDER_STATUS_NOT_CONFIGURED,
      },
      meta: {
        savedAt: meta.savedAt || prior.savedAt || now,
        updatedAt: opts.preserveMeta ? (meta.updatedAt || prior.updatedAt || now) : now,
        storage: "local-only",
      },
    };
  }

  function buildSetup(input, existing, options) {
    return serializeSetup(input, existing, options);
  }

  function validateSetup(setup) {
    return validateFormSetup(formSetupFromContract(setup));
  }

  function saveSetup(storage, setup) {
    var existing = loadSetup(storage);
    var normalized = serializeSetup(setup, existing);
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
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      return serializeSetup(parsed, parsed, { preserveMeta: true });
    } catch (error) {
      return null;
    }
  }

  function resetSetup(storage) {
    if (storage && typeof storage.removeItem === "function") {
      storage.removeItem(STORAGE_KEY);
    }
  }

  function createLocalSetupStore(storage) {
    return {
      load: function() {
        return loadSetup(storage);
      },
      save: function(setup) {
        return saveSetup(storage, setup);
      },
      reset: function() {
        resetSetup(storage);
      },
    };
  }

  /*
   * Future backend persistence boundary.
   *
   * This adapter intentionally does not call CTOS, Supabase, GHL, Voice AI,
   * SMS, email, webhooks, phone routing, or any provider. A real implementation
   * must live behind an authenticated server endpoint and must decide how to:
   * - persist the serialized schema v2 setup contract
   * - associate it with a verified client/account identity
   * - validate the contract again server-side
   * - queue or perform provider-specific setup with explicit operator approval
   * - return provider status without implying live phone activation before it exists
   */
  function createBackendPersistenceAdapter() {
    return {
      providerStatus: PROVIDER_STATUS_NOT_CONFIGURED,
      persist: function(setup) {
        return {
          ok: false,
          skipped: true,
          providerStatus: PROVIDER_STATUS_NOT_CONFIGURED,
          liveProviderConfigured: false,
          reason: "No backend persistence adapter is configured. Setup remains local-only.",
          setup: serializeSetup(setup, setup, { preserveMeta: true }),
        };
      },
    };
  }

  function dashboardState(setup) {
    var serialized = setup ? serializeSetup(setup, setup, { preserveMeta: true }) : null;
    var errors = serialized ? validateSetup(serialized) : { setup: "No call setup has been saved." };
    var items = missingItems(errors);
    var complete = Boolean(serialized) && serialized.setupCompletion === COMPLETION_COMPLETE && items.length === 0;
    var form = formSetupFromContract(setup);
    return {
      complete: complete,
      statusLabel: complete ? "SETUP COMPLETE" : "SETUP NEEDS ATTENTION",
      statusTone: complete ? "complete" : "pending",
      setupCompletion: complete ? COMPLETION_COMPLETE : COMPLETION_INCOMPLETE,
      providerStatus: serialized ? serialized.activation.providerStatus : PROVIDER_STATUS_NOT_CONFIGURED,
      liveProviderConfigured: false,
      businessName: complete ? form.businessName : "Client",
      greeting: complete ? form.greeting : "Complete onboarding before Gideon starts answering with a custom greeting.",
      weekdayHours: complete ? form.weekdayHours : "Not configured",
      saturdayHours: complete ? form.saturdayHours : "Not configured",
      sundayHours: complete ? form.sundayHours : "Not configured",
      afterHours: complete
        ? (form.forwardNumber ? "Preference: forward urgent calls to " + form.forwardNumber : "Preference: take message and send summary")
        : "Not configured until setup is complete",
      errors: errors,
      missingItems: items,
      setup: serialized,
    };
  }

  return {
    STORAGE_KEY: STORAGE_KEY,
    SCHEMA_VERSION: SCHEMA_VERSION,
    clean: clean,
    normalizePhone: normalizePhone,
    formSetupFromContract: formSetupFromContract,
    serializeSetup: serializeSetup,
    buildSetup: buildSetup,
    validateStep: validateStep,
    validateSetup: validateSetup,
    saveSetup: saveSetup,
    loadSetup: loadSetup,
    resetSetup: resetSetup,
    createLocalSetupStore: createLocalSetupStore,
    createBackendPersistenceAdapter: createBackendPersistenceAdapter,
    dashboardState: dashboardState,
  };
});
