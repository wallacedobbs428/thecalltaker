import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { renderSmsStyleReport, SMS_STYLE_NO_SEND_MODE, validateSmsCopyStyle } from "../tools/outreach/validate_sms_copy_style.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const templates = JSON.parse(fs.readFileSync(path.join(repoRoot, "tools/outreach/sms_templates.json"), "utf8"));

test("SMS style validator stays no-send", () => {
  assert.equal(SMS_STYLE_NO_SEND_MODE, true);
});

test("current SMS templates pass human texting style guard", () => {
  const report = validateSmsCopyStyle(templates);

  assert.equal(report.send_allowed, false);
  assert.equal(report.pass, true);
  assert.ok(report.scenarios.some((scenario) => scenario.scenario === "cold_candidate" && scenario.cold === true));
});

test("cold SMS rejects polished email phrasing", () => {
  const report = validateSmsCopyStyle({
    cold_candidate: {
      approval_required: true,
      source_required: "cold_sms_provider_approval",
      messages: [
        "Hello Sam, I hope this message finds you well. I am reaching out to see if you would be interested in learning more about our services.",
      ],
    },
  });

  assert.equal(report.pass, false);
  assert.match(report.scenarios[0].messages[0].issues.join(" "), /too polished|too long/);
});

test("cold SMS rejects unsafe live-provider claims", () => {
  const report = validateSmsCopyStyle({
    cold_candidate: {
      approval_required: true,
      source_required: "cold_sms_provider_approval",
      messages: ["hey Sam, your ai is live and call forwarding is active"],
    },
  });

  assert.equal(report.pass, false);
  assert.match(report.scenarios[0].messages[0].issues.join(" "), /unsafe claim/);
});

test("style report keeps compliance boundary visible", () => {
  const markdown = renderSmsStyleReport(validateSmsCopyStyle(templates));

  assert.match(markdown, /SMS Copy Style Report/);
  assert.match(markdown, /Cold SMS remains blocked/);
  assert.match(markdown, /does not send/);
});
