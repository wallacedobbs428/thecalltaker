import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { NO_SEND_MODE, STORAGE_MODE, loadProspects, scoreProspects } from "./score_prospects.mjs";

function defaultPaths() {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  return {
    input: path.join(__dirname, "sample_prospects.json"),
    output: path.join(__dirname, "output", "daily-queue.sample.md"),
  };
}

const SAMPLE_GENERATED_AT = "2026-05-14T00:00:00.000Z";

function sectionForCategory(scored, category) {
  return scored.filter((prospect) => prospect.score_category === category);
}

function renderProspect(prospect, index) {
  const asset = prospect.asset_selector;
  return [
    `### ${index + 1}. ${prospect.business_name} (${prospect.industry}, ${prospect.city}, ${prospect.state})`,
    "",
    `- Score: ${prospect.score} (${prospect.score_category})`,
    `- Why it matters: ${prospect.missed_call_risk_notes}`,
    `- Fit: ${prospect.category}; ${prospect.service_area_notes}`,
    `- Outreach angle: ${asset.best_angle}`,
    `- Proof angle: ${prospect.proof_angle}`,
    `- Recommended first touch: ${prospect.recommended_first_touch}`,
    `- Wallace opener: ${asset.phone_opener}`,
    `- Email opener: ${asset.email_opener}`,
    `- Voicemail line: ${asset.voicemail_line}`,
    `- Secret-shopper note: ${asset.secret_shopper_note}`,
    `- CTA: ${asset.cta}`,
    `- Objection to expect: ${prospect.objection_prediction}`,
    `- Next action: ${prospect.next_action}`,
    `- Compliance/risk note: ${prospect.compliance_notes}`,
    `- Activation boundary: ${asset.activation_boundary}`,
    "",
  ].join("\n");
}

export function renderDailyQueue(scored, options = {}) {
  const generatedAt = options.generatedAt || new Date().toISOString();
  const aLeads = sectionForCategory(scored, "A");
  const bLeads = sectionForCategory(scored, "B");
  const cLeads = sectionForCategory(scored, "C");
  const dLeads = sectionForCategory(scored, "D");

  const lines = [
    "# Wallace Daily Outreach Queue (Sample)",
    "",
    `Generated: ${generatedAt}`,
    "",
    "This is a no-send local report built from fake sample prospects. It does not contact anyone, write to providers, trigger messages, or modify CRM records.",
    "",
    "## Safety Locks",
    "",
    `- No-send mode: ${NO_SEND_MODE ? "on" : "off"}`,
    `- Storage mode: ${STORAGE_MODE}`,
    "- Real prospect data: not included",
    "- Provider writes: disabled",
    "- SMS/email/call/webhook actions: disabled",
    "",
    "## Today's Priority",
    "",
    `- A leads for Wallace call review: ${aLeads.length}`,
    `- B leads for manual sequence review: ${bLeads.length}`,
    `- C leads for nurture: ${cLeads.length}`,
    `- D leads to suppress: ${dLeads.length}`,
    "",
    "## A Leads: Call Wallace Now",
    "",
    ...(aLeads.length ? aLeads.map(renderProspect) : ["No A leads in this sample.\n"]),
    "## B Leads: Manual Sequence Review",
    "",
    ...(bLeads.length ? bLeads.map(renderProspect) : ["No B leads in this sample.\n"]),
    "## C Leads: Nurture",
    "",
    ...(cLeads.length ? cLeads.map(renderProspect) : ["No C leads in this sample.\n"]),
    "## D Leads: Bad Fit / Suppress",
    "",
    ...(dLeads.length ? dLeads.map(renderProspect) : ["No D leads in this sample.\n"]),
    "## What Not To Send Yet",
    "",
    "- Do not send SMS unless compliance and consent are approved.",
    "- Do not use unapproved proof or client numbers.",
    "- Do not claim live activation, provider routing, or backend sync.",
    "- Do not route calls or submit intake forms from this queue.",
    "- Do not write to any external CRM or provider from Phase 1.",
  ];

  return lines.join("\n");
}

export function writeDailyQueue(inputPath, outputPath, options = {}) {
  const prospects = loadProspects(inputPath);
  const scored = scoreProspects(prospects);
  const report = renderDailyQueue(scored, options);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${report}\n`);
  return { outputPath, scored, report };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const defaults = defaultPaths();
  const inputPath = process.argv[2] || defaults.input;
  const outputPath = process.argv[3] || defaults.output;
  const isDefaultSample = inputPath === defaults.input && outputPath === defaults.output;
  const options = isDefaultSample ? { generatedAt: SAMPLE_GENERATED_AT } : {};
  const result = writeDailyQueue(inputPath, outputPath, options);
  console.log(`Wrote no-send daily queue: ${result.outputPath}`);
}
