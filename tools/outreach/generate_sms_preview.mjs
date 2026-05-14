import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SMS_PREVIEW_NO_SEND_MODE = true;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const statusPath = path.join(__dirname, "sms_approval_status.json");
const templatesPath = path.join(__dirname, "sms_templates.json");
const outputPath = path.join(__dirname, "output", "sms-preview.sample.md");

function usage() {
  return `The Call Taker no-send SMS preview generator

Usage:
  node tools/outreach/generate_sms_preview.mjs --scenario after_demo --prospect-json '{"first_name":"Sam","company":"Example HVAC","call_path_note":"after-hours voicemail"}'
  node tools/outreach/generate_sms_preview.mjs --scenario cold_candidate --prospect tools/outreach/sms_preview_sample.json

Options:
  --scenario <name>       Template key from sms_templates.json.
  --prospect-json <json>  Prospect fields for merge tags.
  --prospect <path>       Local JSON prospect file.
  --output <path>         Markdown output path.
  --help                  Show help.

This command only writes a local review preview. It never sends SMS.
`;
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") args.help = true;
    else if (arg === "--scenario") args.scenario = argv[++index];
    else if (arg === "--prospect-json") args.prospectJson = argv[++index];
    else if (arg === "--prospect") args.prospect = argv[++index];
    else if (arg === "--output") args.output = argv[++index];
    else throw new Error(`Unknown option: ${arg}`);
  }
  return args;
}

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function merge(message, prospect) {
  return message.replace(/\{([a-z_]+)\}/g, (_, key) => {
    const value = prospect[key];
    if (value === undefined || value === null || String(value).trim() === "") return `[${key}]`;
    return String(value).trim();
  });
}

function approvalGate(status, template) {
  if (!template.approval_required) return "review_only";
  if (status.status === "approved" && status.provider_submission.provider_approval_verified === true) return "approved_review_required";
  return "blocked_provider_approval_required";
}

export function generateSmsPreview({ scenario, prospect, status, templates }) {
  if (SMS_PREVIEW_NO_SEND_MODE !== true || status.no_send_mode !== true) {
    throw new Error("SMS preview tooling must remain no-send.");
  }
  const template = templates[scenario];
  if (!template) throw new Error(`Unknown SMS scenario: ${scenario}`);

  const gate = approvalGate(status, template);
  const messages = template.messages.map((message) => merge(message, prospect));
  return {
    scenario,
    gate,
    send_allowed: false,
    no_send_mode: SMS_PREVIEW_NO_SEND_MODE,
    source_required: template.source_required,
    prospect,
    messages,
  };
}

export function renderSmsPreview(preview) {
  const messages = preview.messages.map((message, index) => `${index + 1}. ${message}`).join("\n\n");
  return `# SMS Preview

Status: no-send review only
Scenario: ${preview.scenario}
Gate: ${preview.gate}
Send allowed: no
Source required: ${preview.source_required}

## Prospect

- First name: ${preview.prospect.first_name || "unknown"}
- Company: ${preview.prospect.company || "unknown"}
- Industry: ${preview.prospect.industry || "unknown"}
- Call-path note: ${preview.prospect.call_path_note || "unknown"}

## Draft Messages

${messages}

## Operator Boundary

This file is for Wallace review only. It does not send SMS, write provider records, upload contacts, or start an automation.
`;
}

export function writeSmsPreview({ scenario, prospect, destination = outputPath }) {
  const status = loadJson(statusPath);
  const templates = loadJson(templatesPath);
  const preview = generateSmsPreview({ scenario, prospect, status, templates });
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, renderSmsPreview(preview));
  return { output: destination, scenario, gate: preview.gate, send_allowed: false };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
  } else {
    if (!args.scenario) throw new Error("--scenario is required.");
    if (!args.prospectJson && !args.prospect) throw new Error("--prospect-json or --prospect is required.");
    const prospect = args.prospectJson ? JSON.parse(args.prospectJson) : loadJson(args.prospect);
    const result = writeSmsPreview({ scenario: args.scenario, prospect, destination: args.output || outputPath });
    console.log(JSON.stringify(result, null, 2));
  }
}
