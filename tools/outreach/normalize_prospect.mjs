import { scoreProspect } from "./score_prospects.mjs";

export const INTAKE_NO_SEND_MODE = true;
export const IMPORT_STATUSES = Object.freeze({
  NORMALIZED: "normalized",
  REJECTED: "rejected",
});

const REQUIRED_INPUT_FIELDS = ["business_name", "industry", "phone", "website", "city", "state", "source_url"];
const PERSONAL_EMAIL_DOMAINS = new Set([
  "aol.com",
  "gmail.com",
  "hotmail.com",
  "icloud.com",
  "live.com",
  "me.com",
  "msn.com",
  "outlook.com",
  "proton.me",
  "protonmail.com",
  "yahoo.com",
]);

const INDUSTRY_ALIASES = new Map([
  ["air conditioning", "hvac"],
  ["ac", "hvac"],
  ["heating and air", "hvac"],
  ["heating & air", "hvac"],
  ["hvac", "hvac"],
  ["plumber", "plumbing"],
  ["plumbing", "plumbing"],
  ["roofer", "roofing"],
  ["roofing", "roofing"],
  ["restoration", "water damage"],
  ["water damage", "water damage"],
  ["locksmith", "locksmith"],
  ["towing", "towing"],
  ["electrician", "electrical"],
  ["electrical", "electrical"],
  ["garage door", "garage door"],
  ["medical supply", "medical/surgical supply"],
  ["surgical supply", "medical/surgical supply"],
  ["medical/surgical supply", "medical/surgical supply"],
  ["dental", "dental"],
  ["med spa", "med spa"],
  ["clinic", "urgent clinic"],
  ["generic business", "business with phone line"],
  ["business with phone line", "business with phone line"],
]);

const CATEGORY_ALIASES = new Map([
  ["emergency", "emergency_service"],
  ["emergency service", "emergency_service"],
  ["appointment", "appointment_service"],
  ["appointment service", "appointment_service"],
  ["high ticket", "high_ticket_service"],
  ["high ticket service", "high_ticket_service"],
  ["after hours", "after_hours_need"],
  ["recurring call volume", "recurring_call_volume"],
  ["poor answering path", "poor_answering_path"],
  ["business with phone line", "business_with_phone_line"],
  ["generic", "business_with_phone_line"],
  ["bad fit", "bad_fit"],
  ["franchise", "bad_fit"],
]);

function text(value) {
  return String(value ?? "").trim();
}

function lower(value) {
  return text(value).toLowerCase();
}

function includesAny(value, needles) {
  const haystack = lower(value);
  return needles.some((needle) => haystack.includes(needle));
}

function slug(value) {
  return lower(value)
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

export function normalizeIndustry(value) {
  const normalized = lower(value).replace(/\s+/g, " ");
  return INDUSTRY_ALIASES.get(normalized) || normalized || "business with phone line";
}

export function normalizeCategory(value, industry) {
  const normalized = lower(value).replace(/[_-]+/g, " ").replace(/\s+/g, " ");
  if (CATEGORY_ALIASES.has(normalized)) return CATEGORY_ALIASES.get(normalized);

  const normalizedIndustry = normalizeIndustry(industry);
  if (["hvac", "plumbing", "roofing", "water damage", "locksmith", "towing", "electrical", "garage door"].includes(normalizedIndustry)) {
    return "emergency_service";
  }
  if (["medical/surgical supply", "dental", "med spa", "urgent clinic"].includes(normalizedIndustry)) {
    return "appointment_service";
  }
  if (normalizedIndustry === "business with phone line") return "business_with_phone_line";
  return normalized || "business_with_phone_line";
}

export function normalizePhone(value) {
  const raw = text(value);
  if (!raw || raw.toLowerCase() === "unknown") return "unknown";
  const digits = raw.replace(/\D/g, "");
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
  return raw;
}

export function validateBusinessEmail(value) {
  const email = lower(value);
  if (!email || email === "unknown") return { value: "unknown", valid: true, privateLooking: false };
  const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const domain = email.split("@")[1] || "";
  return {
    value: email,
    valid,
    privateLooking: PERSONAL_EMAIL_DOMAINS.has(domain),
  };
}

function usesSafeExampleEmail(email) {
  if (email === "unknown") return true;
  const domain = email.split("@")[1] || "";
  return domain === "example.invalid" || domain.endsWith(".example.invalid");
}

function parseBool(value) {
  if (typeof value === "boolean") return value;
  const normalized = lower(value);
  return ["1", "true", "yes", "y", "high", "visible"].includes(normalized);
}

function missingRequiredFields(raw) {
  return REQUIRED_INPUT_FIELDS.filter((field) => !text(raw[field]));
}

function defaultText(value, fallback = "unknown") {
  return text(value) || fallback;
}

function makeId(raw, industry, city, state) {
  return (
    slug(raw.id) ||
    slug(`${raw.business_name || "prospect"}-${industry}-${city || "unknown"}-${state || "na"}`) ||
    `prospect-${Date.now()}`
  );
}

function buildSignals(raw, industry, category, emailResult) {
  const notes = [
    raw.hours_signal,
    raw.emergency_signal,
    raw.missed_call_risk_notes,
    raw.current_answering_path,
    raw.service_area_notes,
    raw.review_signal,
    raw.ad_spend_signal,
  ].join(" ");

  const emergencyService =
    category === "emergency_service" ||
    includesAny(industry, ["hvac", "plumbing", "roofing", "water damage", "locksmith", "towing", "electrical", "garage door"]) ||
    includesAny(notes, ["emergency", "24 hour", "24/7", "urgent"]);

  const afterHoursNeed = category === "after_hours_need" || includesAny(notes, ["after hours", "night", "weekend", "closed"]);
  const callPathIssue =
    category === "poor_answering_path" ||
    includesAny(raw.current_answering_path, ["voicemail", "missed", "no answer", "unclear", "call back", "cell"]);
  const highValueCall =
    category === "high_ticket_service" ||
    includesAny(industry, ["hvac", "plumbing", "roofing", "water damage", "medical/surgical supply", "garage door"]) ||
    parseBool(raw.high_value_call);
  const nationalFranchise = parseBool(raw.national_franchise) || includesAny(`${raw.business_name} ${raw.compliance_notes}`, ["franchise", "national"]);
  const sensitiveCategory = includesAny(industry, ["medical", "surgical", "dental", "med spa", "clinic"]);
  const missingSources = !text(raw.source_url) || !text(raw.website);

  return {
    owner_reachable: !!text(raw.contact_person) && lower(raw.contact_person) !== "unknown",
    service_area_business: category !== "bad_fit" && !includesAny(industry, ["restaurant", "retail"]),
    right_size: !nationalFranchise && category !== "bad_fit",
    emergency_service: emergencyService,
    after_hours_need: afterHoursNeed || emergencyService,
    seasonal_spike: parseBool(raw.seasonal_spike) || includesAny(industry, ["hvac", "roofing"]),
    website_contact_friction: parseBool(raw.website_contact_friction) || includesAny(raw.missed_call_risk_notes, ["form only", "hard to find", "slow", "friction"]),
    review_pain: parseBool(raw.review_pain) || includesAny(raw.review_signal, ["poor", "mixed", "missed", "complaint"]),
    call_path_issue: callPathIssue,
    high_value_call: highValueCall,
    ad_spend_visible: parseBool(raw.ad_spend_signal) || includesAny(raw.ad_spend_signal, ["ad", "sponsored", "ls a", "lsa"]),
    strong_reviews: parseBool(raw.strong_reviews) || includesAny(raw.review_signal, ["strong", "4.", "5 star", "many reviews"]),
    multiple_crews_or_locations: parseBool(raw.multiple_crews_or_locations) || includesAny(raw.service_area_notes, ["multiple", "crews", "locations", "county"]),
    public_phone_works: normalizePhone(raw.phone) !== "unknown",
    public_email_or_form: emailResult.valid && !emailResult.privateLooking && emailResult.value !== "unknown",
    social_active: parseBool(raw.social_active),
    local_or_strategic_market: !!text(raw.city) && !!text(raw.state),
    clear_proof_angle: !!text(raw.proof_angle) && lower(raw.proof_angle) !== "unknown",
    safe_secret_shopper_angle: callPathIssue || afterHoursNeed,
    demo_preview_fit: category !== "bad_fit",
    fits_after_hours_capture: afterHoursNeed || emergencyService,
    fits_revenue_recovery: callPathIssue || highValueCall || emergencyService,
    fits_operational_infrastructure: includesAny(industry, ["medical", "surgical", "dental", "clinic"]) || parseBool(raw.operational_infrastructure_fit),
    deductions: {
      national_franchise: nationalFranchise,
      strong_existing_solution: parseBool(raw.strong_existing_solution) || includesAny(raw.current_answering_path, ["call center", "answering service"]),
      missing_sources: missingSources,
      sensitive_category: sensitiveCategory,
      terms_risk: parseBool(raw.terms_risk),
      sms_compliance_uncertain: true,
    },
  };
}

export function normalizeProspectInput(raw, options = {}) {
  if (INTAKE_NO_SEND_MODE !== true) {
    throw new Error("Outreach intake must remain no-send.");
  }

  const errors = [];
  const missing = missingRequiredFields(raw);
  missing.forEach((field) => errors.push(`Missing required field: ${field}`));

  const emailResult = validateBusinessEmail(raw.email_if_public);
  if (!emailResult.valid) errors.push("Invalid public business email format.");
  if (emailResult.privateLooking) errors.push("Personal-looking email domains require manual review and are rejected from sample imports.");

  const sampleMode = options.sampleMode !== false;
  const sourceUrl = defaultText(raw.source_url);
  const website = defaultText(raw.website);
  if (sampleMode) {
    if (sourceUrl !== "unknown" && !sourceUrl.includes("example.invalid")) errors.push("Committed sample imports must use example.invalid source URLs.");
    if (website !== "unknown" && !website.includes("example.invalid")) errors.push("Committed sample imports must use example.invalid websites.");
    if (!usesSafeExampleEmail(emailResult.value)) {
      errors.push("Committed sample import emails must use example.invalid.");
    }
  }

  if (errors.length > 0) {
    return {
      accepted: false,
      errors,
      record: {
        ...raw,
        import_status: IMPORT_STATUSES.REJECTED,
        review_required: true,
      },
    };
  }

  const industry = normalizeIndustry(raw.industry);
  const category = normalizeCategory(raw.category, industry);
  const now = options.now || "2026-05-14";
  const city = defaultText(raw.city);
  const state = defaultText(raw.state).toUpperCase();
  const signals = buildSignals(raw, industry, category, emailResult);
  const reviewRequired =
    signals.deductions.sensitive_category ||
    signals.deductions.sms_compliance_uncertain ||
    category === "business_with_phone_line" ||
    category === "bad_fit";

  const normalized = {
    id: makeId(raw, industry, city, state),
    business_name: defaultText(raw.business_name),
    industry,
    category,
    phone: normalizePhone(raw.phone),
    website,
    city,
    state,
    source_url: sourceUrl,
    hours_signal: defaultText(raw.hours_signal, "not researched"),
    emergency_signal: defaultText(raw.emergency_signal, "not researched"),
    missed_call_risk_notes: defaultText(raw.missed_call_risk_notes, "manual review needed"),
    current_answering_path: defaultText(raw.current_answering_path, "unknown"),
    service_area_notes: defaultText(raw.service_area_notes, "not researched"),
    review_signal: defaultText(raw.review_signal, "not researched"),
    ad_spend_signal: defaultText(raw.ad_spend_signal, "not researched"),
    contact_person: defaultText(raw.contact_person),
    contact_role: defaultText(raw.contact_role),
    email_if_public: emailResult.value,
    proof_angle: defaultText(raw.proof_angle, "missed-call revenue recovery"),
    outreach_angle: defaultText(raw.outreach_angle, "missed-call revenue recovery"),
    objection_prediction: defaultText(raw.objection_prediction, "concerned about activation or added workflow"),
    score: null,
    score_category: null,
    next_action: defaultText(raw.next_action, "Review normalized intake, then choose manual no-send next action."),
    owner: "later",
    status: defaultText(raw.status, "research"),
    compliance_notes: [
      defaultText(raw.compliance_notes, "Manual no-send intake only."),
      "No email, SMS, calls, CRM writes, provider writes, or activation from this importer.",
      reviewRequired ? "Manual compliance review required before any outreach." : "Manual review still required before any outreach.",
    ].join(" "),
    last_touch: raw.last_touch ? text(raw.last_touch) : null,
    next_touch: raw.next_touch ? text(raw.next_touch) : null,
    created_at: defaultText(raw.created_at, now),
    updated_at: defaultText(raw.updated_at, now),
    data_source: defaultText(raw.data_source, options.dataSource || "manual_import"),
    import_status: IMPORT_STATUSES.NORMALIZED,
    review_required: reviewRequired,
    signals,
  };

  return {
    accepted: true,
    errors: [],
    record: scoreProspect(normalized),
  };
}
