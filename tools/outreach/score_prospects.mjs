import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const NO_SEND_MODE = true;
export const STORAGE_MODE = "local-files-only";

export const REQUIRED_FIELDS = [
  "id",
  "business_name",
  "industry",
  "category",
  "phone",
  "website",
  "city",
  "state",
  "source_url",
  "hours_signal",
  "emergency_signal",
  "missed_call_risk_notes",
  "current_answering_path",
  "service_area_notes",
  "review_signal",
  "ad_spend_signal",
  "contact_person",
  "contact_role",
  "email_if_public",
  "proof_angle",
  "outreach_angle",
  "objection_prediction",
  "score",
  "score_category",
  "next_action",
  "owner",
  "status",
  "compliance_notes",
  "last_touch",
  "next_touch",
  "created_at",
  "updated_at",
  "signals",
];

const REQUIRED_SIGNAL_FIELDS = [
  "owner_reachable",
  "service_area_business",
  "right_size",
  "emergency_service",
  "after_hours_need",
  "seasonal_spike",
  "website_contact_friction",
  "review_pain",
  "call_path_issue",
  "high_value_call",
  "ad_spend_visible",
  "strong_reviews",
  "multiple_crews_or_locations",
  "public_phone_works",
  "public_email_or_form",
  "social_active",
  "local_or_strategic_market",
  "clear_proof_angle",
  "safe_secret_shopper_angle",
  "demo_preview_fit",
  "fits_after_hours_capture",
  "fits_revenue_recovery",
  "fits_operational_infrastructure",
  "deductions",
];

const REQUIRED_DEDUCTION_FIELDS = [
  "national_franchise",
  "strong_existing_solution",
  "missing_sources",
  "sensitive_category",
  "terms_risk",
  "sms_compliance_uncertain",
];

const PRIMARY_INDUSTRIES = new Set([
  "hvac",
  "plumbing",
  "roofing",
  "water damage",
  "locksmith",
  "towing",
  "electrical",
  "garage door",
]);

const SECONDARY_INDUSTRIES = new Set([
  "dental",
  "med spa",
  "urgent clinic",
  "medical/surgical supply",
  "medical supply",
  "surgical supply",
  "property management",
]);

function boolScore(value, points) {
  return value ? points : 0;
}

function industryFit(industry) {
  const normalized = String(industry || "").toLowerCase();
  if (PRIMARY_INDUSTRIES.has(normalized)) return 10;
  if (SECONDARY_INDUSTRIES.has(normalized)) return 7;
  if (normalized.includes("service") || normalized.includes("appointment")) return 4;
  return 0;
}

function categoryFor(score, prospect) {
  const deductions = prospect.signals.deductions;
  if (deductions.terms_risk || score < 40) return "D";
  if (score >= 80) return "A";
  if (score >= 60) return "B";
  return "C";
}

function ownerForCategory(category) {
  if (category === "A") return "Wallace";
  if (category === "B") return "system";
  return "later";
}

function statusForCategory(category, currentStatus) {
  if (category === "A") return "call_needed";
  if (category === "B") return currentStatus === "research" ? "ready" : currentStatus;
  if (category === "C") return "nurture";
  return "lost";
}

export function assertNoSendMode() {
  if (NO_SEND_MODE !== true || STORAGE_MODE !== "local-files-only") {
    throw new Error("Outreach command center must remain no-send and local-only.");
  }
}

export function validateProspect(prospect) {
  const errors = [];

  REQUIRED_FIELDS.forEach((field) => {
    if (!Object.prototype.hasOwnProperty.call(prospect, field)) {
      errors.push(`Missing required field: ${field}`);
    }
  });

  if (prospect.signals && typeof prospect.signals === "object") {
    REQUIRED_SIGNAL_FIELDS.forEach((field) => {
      if (!Object.prototype.hasOwnProperty.call(prospect.signals, field)) {
        errors.push(`Missing required signal: ${field}`);
      }
    });

    if (prospect.signals.deductions && typeof prospect.signals.deductions === "object") {
      REQUIRED_DEDUCTION_FIELDS.forEach((field) => {
        if (!Object.prototype.hasOwnProperty.call(prospect.signals.deductions, field)) {
          errors.push(`Missing required deduction: ${field}`);
        }
      });
    }
  } else {
    errors.push("Missing required field: signals");
  }

  if (prospect.source_url && !String(prospect.source_url).startsWith("https://example.invalid/")) {
    errors.push("Sample prospects must use example.invalid source URLs.");
  }

  if (prospect.website && !String(prospect.website).startsWith("https://example.invalid/")) {
    errors.push("Sample prospects must use example.invalid websites.");
  }

  if (prospect.email_if_public && prospect.email_if_public !== "unknown" && !String(prospect.email_if_public).endsWith("@example.invalid")) {
    errors.push("Sample prospect emails must use example.invalid or unknown.");
  }

  return errors;
}

export function scoreProspect(prospect) {
  assertNoSendMode();

  const s = prospect.signals;
  const d = s.deductions;
  const disqualified = d.terms_risk;

  let score = 0;

  score += industryFit(prospect.industry);
  score += boolScore(s.owner_reachable, 8);
  score += boolScore(s.service_area_business, 6);
  score += boolScore(s.right_size, 6);

  score += boolScore(s.emergency_service || s.after_hours_need, 8);
  score += boolScore(s.seasonal_spike, 5);
  score += boolScore(s.website_contact_friction, 5);
  score += boolScore(s.review_pain, 5);
  score += boolScore(s.call_path_issue, 2);

  score += boolScore(s.high_value_call, 8);
  score += boolScore(s.ad_spend_visible, 5);
  score += boolScore(s.strong_reviews, 4);
  score += boolScore(s.multiple_crews_or_locations, 3);

  score += boolScore(s.public_phone_works, 4);
  score += boolScore(s.owner_reachable, 4);
  score += boolScore(s.public_email_or_form, 3);
  score += boolScore(s.social_active, 2);
  score += boolScore(s.local_or_strategic_market, 2);

  score += boolScore(s.clear_proof_angle, 4);
  score += boolScore(s.safe_secret_shopper_angle, 3);
  score += boolScore(s.demo_preview_fit, 3);

  score += boolScore(s.fits_after_hours_capture, 3);
  score += boolScore(s.fits_revenue_recovery, 3);
  score += boolScore(s.fits_operational_infrastructure, 2);

  score -= boolScore(d.national_franchise, 20);
  score -= boolScore(d.strong_existing_solution, 15);
  score -= boolScore(d.missing_sources, 10);
  score -= boolScore(d.sensitive_category, 8);

  if (disqualified) score = 0;
  score = Math.max(0, Math.min(100, score));

  const score_category = categoryFor(score, prospect);

  return {
    ...prospect,
    score,
    score_category,
    owner: ownerForCategory(score_category),
    status: statusForCategory(score_category, prospect.status),
    recommended_first_touch: recommendedFirstTouch(prospect, score_category),
    asset_selector: assetSelector(prospect, score_category),
  };
}

export function recommendedFirstTouch(prospect, category) {
  if (category === "A") {
    return "Wallace manual call with call sheet. Do not automate.";
  }
  if (category === "B") {
    return "Manual email draft review using the 5-touch missed-call sequence.";
  }
  if (category === "C") {
    return "Nurture with education or re-research during a seasonal trigger.";
  }
  return "Do not contact. Record bad-fit reason.";
}

export function assetSelector(prospect, category) {
  const company = prospect.business_name;
  const angle = prospect.outreach_angle || "missed-call capture";
  const boundary = "Nothing is live until backend sync, provider routing, and activation are reviewed and verified.";
  const cta = category === "A" ? "call Wallace" : category === "B" ? "demo preview" : category === "C" ? "nurture" : "do not contact";

  return {
    best_angle: angle,
    best_channel: category === "A" ? "phone" : category === "B" ? "email" : category === "C" ? "education" : "none",
    best_sequence: category === "A" ? "Wallace hot-lead call sheet" : category === "B" ? "5-touch cold email sequence" : category === "C" ? "seasonal nurture" : "suppression",
    email_opener: `Quick question: what happens when someone calls ${company} after hours or while your team is already busy?`,
    phone_opener: `Hi, this is Wallace with The Call Taker. I was looking at ${company}'s public call path and had a quick question about missed-call capture.`,
    voicemail_line: `Hi, this is Wallace with The Call Taker. I had a quick note about ${company}'s after-hours call path. Nothing gets activated without review.`,
    secret_shopper_note: prospect.signals.safe_secret_shopper_angle
      ? `Use neutral wording: we checked the public call path and saw ${prospect.current_answering_path}.`
      : "Do not use a secret-shopper angle yet.",
    cta,
    activation_boundary: boundary,
    do_not_send_yet: category !== "A" && category !== "B",
  };
}

export function scoreProspects(prospects) {
  const validationErrors = [];

  prospects.forEach((prospect, index) => {
    const errors = validateProspect(prospect);
    errors.forEach((error) => validationErrors.push({ index, id: prospect.id || null, error }));
  });

  if (validationErrors.length > 0) {
    const details = validationErrors.map((item) => `${item.id || `row-${item.index}`}: ${item.error}`).join("\n");
    throw new Error(`Prospect validation failed:\n${details}`);
  }

  return prospects.map(scoreProspect).sort((a, b) => b.score - a.score || a.business_name.localeCompare(b.business_name));
}

export function loadProspects(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function summarize(scored) {
  const counts = { A: 0, B: 0, C: 0, D: 0 };
  scored.forEach((prospect) => {
    counts[prospect.score_category] += 1;
  });

  return {
    no_send_mode: NO_SEND_MODE,
    storage_mode: STORAGE_MODE,
    total: scored.length,
    categories: counts,
    top: scored.slice(0, 5).map((prospect) => ({
      id: prospect.id,
      business_name: prospect.business_name,
      industry: prospect.industry,
      score: prospect.score,
      score_category: prospect.score_category,
      next_action: prospect.next_action,
      recommended_first_touch: prospect.recommended_first_touch,
    })),
  };
}

function defaultInputPath() {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  return path.join(__dirname, "sample_prospects.json");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const inputPath = process.argv[2] || defaultInputPath();
  const prospects = loadProspects(inputPath);
  const scored = scoreProspects(prospects);
  console.log(JSON.stringify(summarize(scored), null, 2));
}
