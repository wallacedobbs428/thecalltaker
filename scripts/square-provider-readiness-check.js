#!/usr/bin/env node
"use strict";

const REQUIRED_ENV = [
  "SQUARE_ACCESS_TOKEN",
  "SQUARE_LOCATION_ID",
  "SQUARE_ENVIRONMENT"
];

function parseArgs(argv) {
  const options = { json: false, help: false, envFile: null };
  for (const arg of argv) {
    if (arg === "--json") options.json = true;
    else if (arg.startsWith("--env-file=")) options.envFile = arg.slice("--env-file=".length);
    else if (arg === "--help" || arg === "-h") options.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return options;
}

function parseEnvFileContent(content) {
  const parsed = {};
  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const match = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    const key = match[1];
    let value = match[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    parsed[key] = value;
  }
  return parsed;
}

function envWithOptionalFile(baseEnv, envFile) {
  const fs = require("fs");
  const path = require("path");
  const env = { ...baseEnv };
  const report = {
    env_file_requested: Boolean(envFile),
    env_file_loaded: false,
    env_file_error: null
  };

  if (!envFile) return { env, report };

  try {
    const parsed = parseEnvFileContent(fs.readFileSync(path.resolve(process.cwd(), envFile), "utf8"));
    for (const [key, value] of Object.entries(parsed)) {
      if (!env[key]) env[key] = value;
    }
    report.env_file_loaded = true;
  } catch (error) {
    report.env_file_error = error.message;
  }
  return { env, report };
}

function buildReport(env, envFileReport = null) {
  const vars = REQUIRED_ENV.map((name) => ({
    name,
    present: Boolean(env[name]),
    secret_value_printed: false
  }));
  const missing = vars.filter((item) => !item.present).map((item) => item.name);
  const environmentPresent = Boolean(env.SQUARE_ENVIRONMENT);
  const environmentValid = ["production", "sandbox"].includes(env.SQUARE_ENVIRONMENT || "");

  return {
    generated_at: new Date().toISOString(),
    mode: "square_provider_readiness_check",
    status: missing.length === 0 && environmentValid
      ? "ready_for_read_only_diagnostic"
      : "blocked_missing_square_env",
    env: {
      vars,
      missing,
      all_present: missing.length === 0,
      square_environment_present: environmentPresent,
      square_environment_valid: environmentValid
    },
    env_file: envFileReport || {
      env_file_requested: false,
      env_file_loaded: false,
      env_file_error: null
    },
    secret_values_printed: false,
    provider_call_attempted: false,
    provider_mutation_attempted: false,
    payment_or_charge_attempted: false,
    next_agent_action: missing.length === 0 && environmentValid
      ? "Run node scripts/square-checkout-diagnose.js --json."
      : "Set SQUARE_ACCESS_TOKEN, SQUARE_LOCATION_ID, and SQUARE_ENVIRONMENT=production or sandbox, then rerun this readiness check."
  };
}

function printHelp() {
  console.log(`Square provider readiness check

Usage:
  node scripts/square-provider-readiness-check.js [--json] [--env-file=<path>]

This script checks env var presence only. It does not call Square and never prints secret values.`);
}

function printHuman(report) {
  console.log("Square Provider Readiness Check");
  console.log(`Status: ${report.status}`);
  console.log(`Secret values printed: ${report.secret_values_printed}`);
  console.log(`Provider call attempted: ${report.provider_call_attempted}`);
  console.log(`Provider mutation attempted: ${report.provider_mutation_attempted}`);
  console.log(`Payment or charge attempted: ${report.payment_or_charge_attempted}`);
  for (const item of report.env.vars) {
    console.log(`- ${item.name}: ${item.present ? "present" : "missing"}`);
  }
  console.log(`- SQUARE_ENVIRONMENT valid: ${report.env.square_environment_valid}`);
  console.log(`Next agent action: ${report.next_agent_action}`);
}

if (require.main === module) {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (options.help) {
      printHelp();
    } else {
      const envLoad = envWithOptionalFile(process.env, options.envFile);
      const report = buildReport(envLoad.env, envLoad.report);
      if (options.json) console.log(JSON.stringify(report, null, 2));
      else printHuman(report);
    }
  } catch (error) {
    console.error(`square-provider-readiness-check failed: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  parseArgs,
  parseEnvFileContent,
  envWithOptionalFile,
  buildReport
};
