import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SMS_STYLE_NO_SEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultTemplatesPath = path.join(__dirname, "sms_templates.json");
const defaultOutputPath = path.join(__dirname, "output", "sms-style-report.sample.md");

const coldScenarios = new Set(["cold_candidate", "hvac_variant"]);
const polishedPhrases = [
  "I hope this message finds you well",
  "I am reaching out",
  "Please let me know if you would be interested",
  "We would love the opportunity",
  "Thank you for your time",
  "Sincerely",
];
const unsafeClaims = [
  "your ai is live",
  "call forwarding is active",
  "guaranteed booked jobs",
  "calling you now",
  "provider routing is active",
  "answering every call",
];

function usage() {
  return `The Call Taker SMS copy style validator

Usage:
  node tools/outreach/validate_sms_copy_style.mjs
  node tools/outreach/validate_sms_copy_style.mjs --templates tools/outreach/sms_templates.json --output tools/outreach/output/sms-style-report.sample.md

Checks local draft templates only. It never sends SMS or calls providers.
`;
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--templates") args.templates = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return {
    templates: args.templates || defaultTemplatesPath,
    output: args.output || defaultOutputPath,
    help: args.help === true,
  };
}

function countSentences(message) {
  return (message.match(/[.!?]/g) || []).length;
}

function hasHumanTextingSignal(message) {
  return /(^|\s)(hey|yep|quick|btw|all good|last one|last text|want|that right)\b/i.test(message) || /[a-z]/.test(message[0] || "");
}

function validateMessage(message, { cold }) {
  const issues = [];
  const lower = message.toLowerCase();
  const words = message.trim().split(/\s+/).filter(Boolean);

  unsafeClaims.forEach((claim) => {
    if (lower.includes(claim)) issues.push(`unsafe claim: ${claim}`);
  });

  polishedPhrases.forEach((phrase) => {
    if (lower.includes(phrase.toLowerCase())) issues.push(`too polished: ${phrase}`);
  });

  if (words.length > 32) issues.push("too long for a human-feeling SMS draft");
  if (countSentences(message) > 3) issues.push("too many polished sentence breaks");
  if (cold && !hasHumanTextingSignal(message)) issues.push("cold SMS needs a human texting signal");
  if (cold && /^[A-Z][a-z]+,/.test(message)) issues.push("cold SMS starts like formal email");

  return issues;
}

export function validateSmsCopyStyle(templates) {
  if (SMS_STYLE_NO_SEND_MODE !== true) {
    throw new Error("SMS style validator must remain no-send.");
  }

  const scenarios = Object.entries(templates).map(([scenario, template]) => {
    const cold = coldScenarios.has(scenario) || template.source_required === "cold_sms_provider_approval";
    const messages = (template.messages || []).map((message, index) => ({
      index: index + 1,
      message,
      issues: validateMessage(message, { cold }),
    }));

    return {
      scenario,
      cold,
      approval_required: template.approval_required === true,
      pass: messages.every((message) => message.issues.length === 0),
      messages,
    };
  });

  return {
    generated_at: "2026-05-14T00:00:00.000Z",
    no_send_mode: SMS_STYLE_NO_SEND_MODE,
    send_allowed: false,
    scenarios,
    pass: scenarios.every((scenario) => scenario.pass),
  };
}

export function renderSmsStyleReport(report) {
  const lines = [
    "# SMS Copy Style Report",
    "",
    "Status: local draft review only. No SMS sending, provider upload, or automation is enabled.",
    "",
    `Overall pass: ${report.pass ? "yes" : "no"}`,
    "",
  ];

  report.scenarios.forEach((scenario) => {
    lines.push(`## ${scenario.scenario}`);
    lines.push("");
    lines.push(`- Cold/compliance-gated: ${scenario.cold ? "yes" : "no"}`);
    lines.push(`- Approval required: ${scenario.approval_required ? "yes" : "no"}`);
    lines.push(`- Style pass: ${scenario.pass ? "yes" : "no"}`);
    lines.push("");
    scenario.messages.forEach((message) => {
      lines.push(`${message.index}. ${message.message}`);
      lines.push(`   - Issues: ${message.issues.length ? message.issues.join("; ") : "none"}`);
    });
    lines.push("");
  });

  lines.push("## Boundary", "");
  lines.push("- Cold SMS remains blocked until compliance and provider approval are verified.");
  lines.push("- Keep draft texts human: short, direct, a little imperfect, and not email-polished.");
  lines.push("- This validator does not send, post, upload contacts, call providers, or trigger automations.");
  lines.push("");
  return lines.join("\n");
}

export function writeSmsStyleReport({ templatesPath = defaultTemplatesPath, outputPath = defaultOutputPath } = {}) {
  const templates = JSON.parse(fs.readFileSync(templatesPath, "utf8"));
  const report = validateSmsCopyStyle(templates);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, renderSmsStyleReport(report));
  return {
    output: outputPath,
    pass: report.pass,
    no_send_mode: SMS_STYLE_NO_SEND_MODE,
    send_allowed: false,
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    console.log(JSON.stringify(writeSmsStyleReport({ templatesPath: args.templates, outputPath: args.output }), null, 2));
  }
}
