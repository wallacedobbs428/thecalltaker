import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { importProspects, IMPORT_NO_SEND_MODE, parseCsv } from "../tools/outreach/import_prospects.mjs";
import {
  INTAKE_NO_SEND_MODE,
  normalizeCategory,
  normalizeIndustry,
  normalizePhone,
  normalizeProspectInput,
} from "../tools/outreach/normalize_prospect.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const csvPath = path.join(repoRoot, "tools/outreach/example_import.csv");
const jsonPath = path.join(repoRoot, "tools/outreach/example_import.json");

function tempPrivateDir() {
  const parent = path.join(repoRoot, "tools/outreach/private");
  fs.mkdirSync(parent, { recursive: true });
  return fs.mkdtempSync(path.join(parent, "test-run-"));
}

function baseRecord(overrides = {}) {
  return {
    business_name: "Example Service Co",
    industry: "hvac",
    category: "emergency service",
    phone: "555-010-1212",
    website: "https://example.invalid/example-service",
    city: "Huntsville",
    state: "AL",
    source_url: "https://example.invalid/sources/example-service",
    hours_signal: "after hours listed",
    emergency_signal: "emergency repair",
    missed_call_risk_notes: "calls may hit voicemail",
    current_answering_path: "voicemail after close",
    service_area_notes: "multi-county service area",
    review_signal: "strong reviews",
    ad_spend_signal: "sponsored local result",
    contact_person: "Alex Owner",
    contact_role: "Owner",
    email_if_public: "alex@example.invalid",
    proof_angle: "after-hours revenue recovery",
    outreach_angle: "missed-call capture",
    objection_prediction: "worried about activation",
    ...overrides,
  };
}

test("intake importer stays no-send", () => {
  assert.equal(IMPORT_NO_SEND_MODE, true);
  assert.equal(INTAKE_NO_SEND_MODE, true);
});

test("CSV import normalizes and scores accepted records", () => {
  const records = parseCsv(fs.readFileSync(csvPath, "utf8"));
  const results = importProspects(records, { dataSource: csvPath, sampleMode: true });
  const accepted = results.filter((result) => result.accepted).map((result) => result.record);
  const rejected = results.filter((result) => !result.accepted);

  assert.ok(accepted.length >= 5);
  assert.ok(rejected.length >= 1);
  assert.ok(accepted.some((prospect) => prospect.industry === "hvac" && prospect.score_category === "A"));
  assert.ok(accepted.some((prospect) => prospect.category === "business_with_phone_line"));
  assert.ok(accepted.every((prospect) => prospect.import_status === "normalized"));
});

test("JSON import handles high-fit and generic phone-line prospects", () => {
  const records = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
  const results = importProspects(records, { dataSource: jsonPath, sampleMode: true });
  const accepted = results.filter((result) => result.accepted).map((result) => result.record);
  const rejected = results.filter((result) => !result.accepted);

  const roof = accepted.find((prospect) => prospect.industry === "roofing");
  const generic = accepted.find((prospect) => prospect.category === "business_with_phone_line");

  assert.ok(roof);
  assert.ok(generic);
  assert.ok(roof.score > generic.score);
  assert.ok(rejected.some((result) => result.errors.includes("Missing required field: phone")));
});

test("single prospect normalization maps fields into the scoring contract", () => {
  const result = normalizeProspectInput(baseRecord({ industry: "plumber", phone: "(555) 010-3434" }));

  assert.equal(result.accepted, true);
  assert.equal(result.record.industry, "plumbing");
  assert.equal(result.record.category, "emergency_service");
  assert.equal(result.record.phone, "+15550103434");
  assert.equal(result.record.provider_write_enabled, undefined);
  assert.ok(result.record.score >= 80);
});

test("missing required fields reject before scoring", () => {
  const result = normalizeProspectInput(baseRecord({ business_name: "" }));

  assert.equal(result.accepted, false);
  assert.ok(result.errors.includes("Missing required field: business_name"));
  assert.equal(result.record.import_status, "rejected");
});

test("generic phone-line business is eligible but lower priority", () => {
  const generic = normalizeProspectInput(
    baseRecord({
      business_name: "Generic Phone Line Example",
      industry: "generic business",
      category: "business with phone line",
      emergency_signal: "none known",
      missed_call_risk_notes: "missed-call value not proven",
      current_answering_path: "unknown",
      contact_person: "unknown",
      email_if_public: "unknown",
      ad_spend_signal: "not researched",
      review_signal: "not researched",
    }),
  ).record;

  const highFit = normalizeProspectInput(baseRecord()).record;

  assert.equal(generic.category, "business_with_phone_line");
  assert.ok(highFit.score > generic.score);
});

test("bad-fit franchise is suppressed", () => {
  const result = normalizeProspectInput(
    baseRecord({
      business_name: "National Franchise Example",
      industry: "restaurant",
      category: "bad fit",
      national_franchise: "true",
      current_answering_path: "national call center",
      email_if_public: "unknown",
    }),
  );

  assert.equal(result.accepted, true);
  assert.equal(result.record.score_category, "D");
  assert.equal(result.record.status, "lost");
});

test("private-looking and invalid emails are rejected from sample intake", () => {
  const privateEmail = normalizeProspectInput(baseRecord({ email_if_public: "owner@gmail.com" }));
  const invalidEmail = normalizeProspectInput(baseRecord({ email_if_public: "owner.example.invalid" }));

  assert.equal(privateEmail.accepted, false);
  assert.ok(privateEmail.errors.some((error) => error.includes("Personal-looking email")));
  assert.equal(invalidEmail.accepted, false);
  assert.ok(invalidEmail.errors.includes("Invalid public business email format."));
});

test("normalization helpers support broad phone-line classification", () => {
  assert.equal(normalizeIndustry("Heating & Air"), "hvac");
  assert.equal(normalizeCategory("business with phone line", "generic business"), "business_with_phone_line");
  assert.equal(normalizePhone("555.010.4545"), "+15550104545");
});

test("committed import examples contain only fake safe domains", () => {
  const files = [csvPath, jsonPath];
  files.forEach((file) => {
    const content = fs.readFileSync(file, "utf8");
    const domains = Array.from(content.matchAll(/[a-z0-9.-]+\.[a-z]{2,}/gi)).map((match) => match[0].toLowerCase());
    domains.forEach((domain) => {
      assert.ok(domain === "example.invalid" || domain.endsWith(".example.invalid"), `${domain} should be fake`);
    });
  });
});

test("private-local normalization can preview real researched domains without sample rejection", () => {
  const result = normalizeProspectInput(
    baseRecord({
      business_name: "Private Local Prospect",
      website: "https://private-local-prospect.test",
      source_url: "https://private-local-source.test/listing",
      email_if_public: "owner@private-local-prospect.test",
    }),
    { sampleMode: false, dataSource: "tools/outreach/private/prospects.csv" },
  );

  assert.equal(result.accepted, true);
  assert.equal(result.record.website, "https://private-local-prospect.test");
  assert.equal(result.record.email_if_public, "owner@private-local-prospect.test");
});

test("private-local CLI writes ignored local output", async () => {
  const privateDir = tempPrivateDir();
  const inputPath = path.join(privateDir, "prospects.csv");
  const outputPath = path.join(privateDir, "preview.md");
  fs.writeFileSync(
    inputPath,
    [
      "business_name,industry,category,phone,website,city,state,source_url,email_if_public,hours_signal,emergency_signal,missed_call_risk_notes,current_answering_path,service_area_notes,review_signal,ad_spend_signal,contact_person,contact_role,proof_angle,outreach_angle,objection_prediction",
      "Private Local HVAC,hvac,emergency service,5550101212,https://private-local-hvac.test,Huntsville,AL,https://private-local-source.test,owner@private-local-hvac.test,after hours listed,emergency repair,calls may hit voicemail,voicemail after close,local service,strong reviews,not researched,Pat Owner,Owner,missed-call recovery,after-hours capture,worried about setup",
    ].join("\n"),
  );

  const { spawnSync } = await import("node:child_process");
  const result = spawnSync(
    process.execPath,
    [
      path.join(repoRoot, "tools/outreach/import_prospects.mjs"),
      "--input",
      inputPath,
      "--private-local",
      "--dry-run",
      "--output",
      outputPath,
    ],
    { encoding: "utf8" },
  );

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /"accepted": 1/);
  assert.ok(fs.existsSync(outputPath));
  assert.match(fs.readFileSync(outputPath, "utf8"), /Private Local HVAC/);
});
