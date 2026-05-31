#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const https = require("https");
const crypto = require("crypto");

const SQUARE_VERSION = "2026-05-20";
const BAD_97_LINK = "https://square.link/u/2hfmRPY7";
const OLD_497_LINK = "https://square.link/u/S305ewBr";
const OLD_997_LINK = "https://square.link/u/OpwWF9Sa";
const FORBIDDEN_REDIRECTS = [
  "https://thecalltaker.com/client/onboarding.html",
  "/client/onboarding.html"
];
const REQUIRED_ENV = [
  "SQUARE_ACCESS_TOKEN",
  "SQUARE_LOCATION_ID",
  "SQUARE_ENVIRONMENT"
];
const PRICING_FILES = [
  "website/pricing.html",
  "pricing.html"
];
const DEFAULT_REQUEST_DIR = "ctos/integrations";
const PLAN_CONFIGS = {
  "97": {
    key: "97",
    label: "$97 After-Hours Capture",
    current_url: BAD_97_LINK,
    expected_initial_amount_cents: 0,
    expected_monthly_amount_cents: 9700,
    identity_pattern: /after[- ]hours|after hours|after-hours capture/i,
    request_file: "ctos/integrations/square-97-create-payment-link-request.json"
  },
  "497": {
    key: "497",
    label: "$497 24/7 Call Coverage",
    current_url: OLD_497_LINK,
    expected_initial_amount_cents: 0,
    expected_monthly_amount_cents: 49700,
    identity_pattern: /24\/7|full 24|call coverage|revenue recovery/i,
    request_file: "ctos/integrations/square-497-create-payment-link-request.json"
  },
  "997": {
    key: "997",
    label: "$997 Premium Concierge Priority Setup",
    current_url: OLD_997_LINK,
    expected_initial_amount_cents: 0,
    expected_monthly_amount_cents: 99700,
    identity_pattern: /premium|concierge|priority|operational infrastructure|custom call coverage/i,
    request_file: "ctos/integrations/square-997-create-payment-link-request.json"
  }
};

function parseArgs(argv) {
  const options = {
    json: false,
    createPlanLinks: [],
    createAllPlanLinks: false,
    confirmProviderWrite: false,
    installPricingHref: false,
    requestFile: null,
    requestDir: DEFAULT_REQUEST_DIR,
    envFile: null,
    help: false
  };

  for (const arg of argv) {
    if (arg === "--json") options.json = true;
    else if (arg === "--create-97-link") options.createPlanLinks.push("97");
    else if (arg.startsWith("--create-plan-link=")) options.createPlanLinks.push(arg.slice("--create-plan-link=".length));
    else if (arg.startsWith("--create-plan-links=")) {
      options.createPlanLinks.push(...arg.slice("--create-plan-links=".length).split(",").map((item) => item.trim()).filter(Boolean));
    } else if (arg === "--create-all-plan-links") options.createAllPlanLinks = true;
    else if (arg === "--confirm-provider-write") options.confirmProviderWrite = true;
    else if (arg === "--install-pricing-href") options.installPricingHref = true;
    else if (arg.startsWith("--request-file=")) options.requestFile = arg.slice("--request-file=".length);
    else if (arg.startsWith("--request-dir=")) options.requestDir = arg.slice("--request-dir=".length);
    else if (arg.startsWith("--env-file=")) options.envFile = arg.slice("--env-file=".length);
    else if (arg === "--help" || arg === "-h") options.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }

  options.createPlanLinks = Array.from(new Set(options.createPlanLinks));
  for (const planKey of options.createPlanLinks) {
    if (!PLAN_CONFIGS[planKey]) throw new Error(`Unknown plan key for creation: ${planKey}`);
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
  const env = { ...baseEnv };
  const report = {
    env_file_requested: Boolean(envFile),
    env_file_loaded: false,
    env_file_error: null
  };

  if (!envFile) return { env, report };

  try {
    const resolved = path.resolve(process.cwd(), envFile);
    const parsed = parseEnvFileContent(fs.readFileSync(resolved, "utf8"));
    for (const [key, value] of Object.entries(parsed)) {
      if (!env[key]) env[key] = value;
    }
    report.env_file_loaded = true;
  } catch (error) {
    report.env_file_error = error.message;
  }

  return { env, report };
}

function envReport(env) {
  const vars = REQUIRED_ENV.map((name) => ({
    name,
    present: Boolean(env[name]),
    secret_value_printed: false
  }));
  const missing = vars.filter((item) => !item.present).map((item) => item.name);
  return {
    vars,
    missing,
    all_present: missing.length === 0,
    square_environment: env.SQUARE_ENVIRONMENT || null,
    square_environment_valid: ["production", "sandbox"].includes(env.SQUARE_ENVIRONMENT || "")
  };
}

function squareHost(environment) {
  if (environment === "production") return "connect.squareup.com";
  if (environment === "sandbox") return "connect.squareupsandbox.com";
  return null;
}

function safeSquareErrors(data) {
  if (!data || !Array.isArray(data.errors)) return [];
  return data.errors.map((error) => ({
    category: error.category,
    code: error.code,
    detail: error.detail,
    field: error.field
  }));
}

function squareRequest(env, method, apiPath, body) {
  const host = squareHost(env.SQUARE_ENVIRONMENT);
  if (!host) throw new Error("SQUARE_ENVIRONMENT must be production or sandbox.");

  const requestBody = body ? JSON.stringify(body) : null;
  const headers = {
    "Square-Version": SQUARE_VERSION,
    "Authorization": `Bearer ${env.SQUARE_ACCESS_TOKEN}`,
    "Content-Type": "application/json"
  };
  if (requestBody) headers["Content-Length"] = Buffer.byteLength(requestBody);

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: host,
      method,
      path: apiPath,
      headers,
      timeout: 20000
    }, (res) => {
      let raw = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => { raw += chunk; });
      res.on("end", () => {
        let data = null;
        try {
          data = raw ? JSON.parse(raw) : null;
        } catch (error) {
          return reject(new Error(`Square returned non-JSON response with HTTP ${res.statusCode}.`));
        }
        if (res.statusCode < 200 || res.statusCode >= 300) {
          const err = new Error(`Square API request failed with HTTP ${res.statusCode}.`);
          err.statusCode = res.statusCode;
          err.squareErrors = safeSquareErrors(data);
          return reject(err);
        }
        resolve(data || {});
      });
    });

    req.on("timeout", () => {
      req.destroy(new Error("Square API request timed out."));
    });
    req.on("error", reject);
    if (requestBody) req.write(requestBody);
    req.end();
  });
}

async function capability(id, fn) {
  try {
    const data = await fn();
    return { id, status: "ok", data };
  } catch (error) {
    return {
      id,
      status: "blocked_or_failed",
      http_status: error.statusCode || null,
      square_errors: error.squareErrors || [],
      message: error.message
    };
  }
}

function summarizePaymentLink(link) {
  if (!link) return null;
  return {
    id: link.id || null,
    url: link.url || null,
    long_url: link.long_url || null,
    order_id: link.order_id || null,
    version: link.version || null,
    checkout_redirect_url: link.checkout_options && link.checkout_options.redirect_url
      ? link.checkout_options.redirect_url
      : null,
    created_at: link.created_at || null,
    updated_at: link.updated_at || null
  };
}

function linkLooksLike97Candidate(link) {
  const text = JSON.stringify({
    id: link.id,
    url: link.url,
    long_url: link.long_url,
    description: link.description,
    payment_note: link.payment_note,
    order_id: link.order_id
  }).toLowerCase();
  return link.url !== BAD_97_LINK && (
    text.includes("after-hours") ||
    text.includes("after hours") ||
    text.includes("97") ||
    text.includes("9700")
  );
}

function linkLooksLikePlanCandidate(link, planConfig) {
  const text = JSON.stringify({
    id: link.id,
    url: link.url,
    long_url: link.long_url,
    description: link.description,
    payment_note: link.payment_note,
    order_id: link.order_id
  });
  return link.url !== planConfig.current_url && (
    planConfig.identity_pattern.test(text) ||
    text.includes(String(planConfig.expected_monthly_amount_cents))
  );
}

function collectMoneyAmounts(value, out = []) {
  if (!value || typeof value !== "object") return out;
  if (Object.prototype.hasOwnProperty.call(value, "amount") && Number.isFinite(Number(value.amount))) {
    out.push(Number(value.amount));
  }
  for (const nested of Object.values(value)) {
    if (nested && typeof nested === "object") collectMoneyAmounts(nested, out);
  }
  return out;
}

function collectLocationIds(value, out = []) {
  if (!value || typeof value !== "object") return out;
  if (typeof value.location_id === "string") out.push(value.location_id);
  for (const nested of Object.values(value)) {
    if (nested && typeof nested === "object") collectLocationIds(nested, out);
  }
  return out;
}

function validateCreatePayload(payload, locationId, planConfig) {
  const serialized = JSON.stringify(payload);
  const lower = serialized.toLowerCase();
  const reasons = [];

  for (const forbidden of FORBIDDEN_REDIRECTS) {
    if (lower.includes(forbidden.toLowerCase())) {
      reasons.push(`request payload contains forbidden redirect: ${forbidden}`);
    }
  }

  if (!payload || typeof payload !== "object") {
    reasons.push("request payload must be a JSON object");
  } else {
    if (!payload.quick_pay && !payload.order) {
      reasons.push("request payload must include quick_pay or order");
    }

    const locationIds = collectLocationIds(payload);
    if (!locationIds.includes(locationId)) {
      reasons.push("request payload must include SQUARE_LOCATION_ID as a location_id");
    }

    const amounts = collectMoneyAmounts(payload);
    const metadata = payload._ctos_metadata || payload.ctos_metadata || payload.provider_repair_metadata || {};
    const expectedMonthlyAmount = Number(metadata.expected_monthly_amount_cents);
    if (!amounts.includes(planConfig.expected_initial_amount_cents)) {
      reasons.push(`request payload must include safe initial checkout price ${planConfig.expected_initial_amount_cents} cents for ${planConfig.label}`);
    }
    if (expectedMonthlyAmount !== planConfig.expected_monthly_amount_cents && !amounts.includes(planConfig.expected_monthly_amount_cents)) {
      reasons.push(`request payload must include expected monthly price data ${planConfig.expected_monthly_amount_cents} cents for ${planConfig.label}`);
    }

    if (!planConfig.identity_pattern.test(serialized)) {
      reasons.push(`request payload must identify the ${planConfig.label} offer`);
    }
  }

  return {
    valid: reasons.length === 0,
    reasons
  };
}

function requestFileForPlan(options, planKey) {
  if (options.requestFile) return options.requestFile;
  if (options.requestDir && options.requestDir !== DEFAULT_REQUEST_DIR) {
    return path.join(options.requestDir, `square-${planKey}-create-payment-link-request.json`);
  }
  return PLAN_CONFIGS[planKey].request_file;
}

function injectEnvPlaceholders(value, env) {
  if (Array.isArray(value)) return value.map((item) => injectEnvPlaceholders(item, env));
  if (value && typeof value === "object") {
    const next = {};
    for (const [key, nested] of Object.entries(value)) {
      next[key] = injectEnvPlaceholders(nested, env);
    }
    return next;
  }
  if (value === "__SQUARE_LOCATION_ID__") return env.SQUARE_LOCATION_ID;
  return value;
}

function squareCreatePayload(payload) {
  const clean = JSON.parse(JSON.stringify(payload));
  delete clean._ctos_metadata;
  delete clean.ctos_metadata;
  delete clean.provider_repair_metadata;
  return clean;
}

function loadCreatePayload(requestFile, env, planConfig) {
  if (!requestFile) {
    return {
      ok: false,
      reason: `missing CreatePaymentLink request file for ${planConfig.label}`
    };
  }
  const resolved = path.resolve(process.cwd(), requestFile);
  const payload = injectEnvPlaceholders(JSON.parse(fs.readFileSync(resolved, "utf8")), env);
  const validation = validateCreatePayload(payload, env.SQUARE_LOCATION_ID, planConfig);
  if (!validation.valid) {
    return {
      ok: false,
      reason: "request file failed provider-safety validation",
      validation_errors: validation.reasons,
      request_file: requestFile
    };
  }
  if (!payload.idempotency_key) {
    payload.idempotency_key = crypto
      .createHash("sha256")
      .update(`${requestFile}:${planConfig.current_url}:${planConfig.expected_monthly_amount_cents}`)
      .digest("hex")
      .slice(0, 32);
  }
  return {
    ok: true,
    payload: squareCreatePayload(payload),
    request_file: requestFile
  };
}

function replacePlanHrefs(newLinksByPlan) {
  const changed = [];
  for (const file of PRICING_FILES) {
    const absolute = path.resolve(process.cwd(), file);
    let next = fs.readFileSync(absolute, "utf8");
    let fileChanged = false;
    for (const [planKey, newUrl] of Object.entries(newLinksByPlan)) {
      const planConfig = PLAN_CONFIGS[planKey];
      if (!/^https:\/\/(square\.link\/u\/|checkout\.square\.site\/)/.test(newUrl)) {
        throw new Error(`Refusing to install a non-Square checkout URL for ${planConfig.label}.`);
      }
      const escaped = planConfig.current_url.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const count = (next.match(new RegExp(escaped, "g")) || []).length;
      if (count !== 1) {
        throw new Error(`Expected exactly one ${planConfig.label} href in ${file}; found ${count}.`);
      }
      next = next.replace(planConfig.current_url, newUrl);
      fileChanged = true;
    }
    if (fileChanged) {
      fs.writeFileSync(absolute, next);
      changed.push(file);
    }
  }
  return changed;
}

async function diagnose(options, env) {
  const report = {
    generated_at: new Date().toISOString(),
    mode: "square_checkout_diagnose",
    current_bad_97_link: BAD_97_LINK,
    current_plan_links: Object.fromEntries(Object.entries(PLAN_CONFIGS).map(([key, value]) => [key, value.current_url])),
    env: envReport(env),
    env_file: options.envFileReport || {
      env_file_requested: false,
      env_file_loaded: false,
      env_file_error: null
    },
    secret_values_printed: false,
    provider_inspection_attempted: false,
    provider_write_requested: false,
    provider_mutation_attempted: false,
    payment_or_charge_attempted: false,
    customer_message_attempted: false,
    deploy_attempted: false,
    capabilities: {},
    findings: [],
    next_agent_action: null,
    new_97_link: null,
    new_plan_links: {},
    files_changed: []
  };

  if (!report.env.all_present || !report.env.square_environment_valid) {
    report.status = "blocked_missing_or_invalid_env";
    report.next_agent_action = "Provide SQUARE_ACCESS_TOKEN, SQUARE_LOCATION_ID, and SQUARE_ENVIRONMENT=production or sandbox, then rerun node scripts/square-checkout-diagnose.js --json or pass --env-file=<path>.";
    return report;
  }

  report.provider_inspection_attempted = true;

  const paymentLinksCap = await capability("list_payment_links", () =>
    squareRequest(env, "GET", "/v2/online-checkout/payment-links?limit=100")
  );
  report.capabilities.list_payment_links = {
    status: paymentLinksCap.status,
    http_status: paymentLinksCap.http_status || null,
    square_errors: paymentLinksCap.square_errors || []
  };

  const links = paymentLinksCap.status === "ok" && Array.isArray(paymentLinksCap.data.payment_links)
    ? paymentLinksCap.data.payment_links
    : [];
  report.payment_links = {
    count: links.length,
    current_bad_97_link: summarizePaymentLink(links.find((link) => link.url === BAD_97_LINK || link.long_url === BAD_97_LINK)),
    current_plan_links: Object.fromEntries(Object.entries(PLAN_CONFIGS).map(([planKey, planConfig]) => [
      planKey,
      summarizePaymentLink(links.find((link) => link.url === planConfig.current_url || link.long_url === planConfig.current_url))
    ])),
    candidate_97_replacements: links.filter(linkLooksLike97Candidate).slice(0, 5).map(summarizePaymentLink),
    candidate_plan_replacements: Object.fromEntries(Object.entries(PLAN_CONFIGS).map(([planKey, planConfig]) => [
      planKey,
      links.filter((link) => linkLooksLikePlanCandidate(link, planConfig)).slice(0, 5).map(summarizePaymentLink)
    ]))
  };

  const catalogCap = await capability("list_catalog_items", () =>
    squareRequest(env, "GET", "/v2/catalog/list?types=ITEM,ITEM_VARIATION,SUBSCRIPTION_PLAN,SUBSCRIPTION_PLAN_VARIATION")
  );
  report.capabilities.list_catalog_items = {
    status: catalogCap.status,
    http_status: catalogCap.http_status || null,
    square_errors: catalogCap.square_errors || []
  };
  if (catalogCap.status === "ok" && Array.isArray(catalogCap.data.objects)) {
    report.catalog = {
      object_count: catalogCap.data.objects.length,
      possible_after_hours_objects: catalogCap.data.objects
        .filter((object) => JSON.stringify(object).toLowerCase().includes("after-hours") || JSON.stringify(object).toLowerCase().includes("after hours"))
        .slice(0, 5)
        .map((object) => ({ type: object.type, id: object.id, present_at_all_locations: object.present_at_all_locations || false }))
    };
  }

  const orderIds = Array.from(new Set(links.map((link) => link.order_id).filter(Boolean))).slice(0, 10);
  if (orderIds.length) {
    const ordersCap = await capability("batch_retrieve_orders", () =>
      squareRequest(env, "POST", "/v2/orders/batch-retrieve", {
        location_id: env.SQUARE_LOCATION_ID,
        order_ids: orderIds
      })
    );
    report.capabilities.batch_retrieve_orders = {
      status: ordersCap.status,
      http_status: ordersCap.http_status || null,
      square_errors: ordersCap.square_errors || []
    };
    if (ordersCap.status === "ok" && Array.isArray(ordersCap.data.orders)) {
      report.orders = {
        inspected_count: ordersCap.data.orders.length,
        summaries: ordersCap.data.orders.slice(0, 10).map((order) => ({
          id: order.id,
          state: order.state || null,
          total_money: order.total_money || null,
          line_item_count: Array.isArray(order.line_items) ? order.line_items.length : 0
        }))
      };
    }
  } else {
    report.capabilities.batch_retrieve_orders = {
      status: "not_attempted_no_order_ids"
    };
  }

  const canCreate = report.capabilities.list_payment_links.status === "ok";
  const plansToCreate = options.createAllPlanLinks
    ? Object.keys(PLAN_CONFIGS)
    : options.createPlanLinks;

  if (!plansToCreate.length) {
    report.status = "read_only_complete";
    report.next_agent_action = canCreate
      ? "Review read-only findings. If no active replacement exists, prepare exact CreatePaymentLink request files and rerun with guarded create flags."
      : "Fix Square API permission/access errors, then rerun read-only diagnosis.";
    return report;
  }

  report.provider_write_requested = true;

  if (env.SQUARE_PROVIDER_WRITE_APPROVED !== "true" || !options.confirmProviderWrite) {
    report.status = "blocked_write_not_approved";
    report.next_agent_action = "Set SQUARE_PROVIDER_WRITE_APPROVED=true and pass --confirm-provider-write only after the exact provider write is approved.";
    return report;
  }

  report.provider_mutation_attempted = true;
  report.create_payload_status = {};

  for (const planKey of plansToCreate) {
    const planConfig = PLAN_CONFIGS[planKey];
    const requestFile = requestFileForPlan(options, planKey);
    const createPayload = loadCreatePayload(requestFile, env, planConfig);
    report.create_payload_status[planKey] = {
      ok: createPayload.ok,
      request_file: createPayload.request_file || requestFile,
      validation_errors: createPayload.validation_errors || []
    };
    if (!createPayload.ok) {
      report.status = "blocked_missing_or_invalid_create_payload";
      report.next_agent_action = `Provide a validated CreatePaymentLink request JSON for ${planConfig.label}.`;
      return report;
    }

    const capabilityId = `create_${planKey}_payment_link`;
    const createCap = await capability(capabilityId, () =>
      squareRequest(env, "POST", "/v2/online-checkout/payment-links", createPayload.payload)
    );
    report.capabilities[capabilityId] = {
      status: createCap.status,
      http_status: createCap.http_status || null,
      square_errors: createCap.square_errors || []
    };

    if (createCap.status !== "ok") {
      report.status = "blocked_create_failed";
      report.next_agent_action = `Resolve Square CreatePaymentLink errors for ${planConfig.label}, then rerun guarded creation.`;
      return report;
    }

    const newUrl = createCap.data.payment_link && (createCap.data.payment_link.url || createCap.data.payment_link.long_url);
    if (!newUrl) {
      report.status = "blocked_create_returned_no_url";
      report.next_agent_action = `Inspect Square response for ${planConfig.label}; no link URL was returned.`;
      return report;
    }

    report.new_plan_links[planKey] = newUrl;
    if (planKey === "97") report.new_97_link = newUrl;
  }

  if (options.installPricingHref) {
    report.files_changed = replacePlanHrefs(report.new_plan_links);
  }

  report.status = options.installPricingHref ? "created_and_installed" : "created_not_installed";
  report.next_agent_action = options.installPricingHref
    ? "Run pricing checkout static validation and hand all three plan buttons to Right QA."
    : "Verify the new Square URLs directly, then rerun with --install-pricing-href or replace only the pricing hrefs.";
  return report;
}

function printHelp() {
  console.log(`Square checkout diagnose

Usage:
  node scripts/square-checkout-diagnose.js [--json]
  node scripts/square-checkout-diagnose.js --json --env-file=<file>
  node scripts/square-checkout-diagnose.js --json --create-all-plan-links --confirm-provider-write [--request-dir=ctos/integrations] [--install-pricing-href]
  node scripts/square-checkout-diagnose.js --json --create-plan-link=97 --confirm-provider-write --request-file=<file> [--install-pricing-href]

Safe defaults:
  - Missing env exits safely before any Square API request.
  - Default mode is read-only inspection.
  - Provider creation requires SQUARE_PROVIDER_WRITE_APPROVED=true and explicit create flags.
  - Secret values are never printed.`);
}

function printHuman(report) {
  console.log("Square Checkout Diagnose");
  console.log(`Status: ${report.status}`);
  console.log(`Secret values printed: ${report.secret_values_printed}`);
  console.log(`Provider inspection attempted: ${report.provider_inspection_attempted}`);
  console.log(`Provider write requested: ${report.provider_write_requested}`);
  console.log(`Provider mutation attempted: ${report.provider_mutation_attempted}`);
  console.log(`Payment or charge attempted: ${report.payment_or_charge_attempted}`);
  console.log("Env:");
  for (const item of report.env.vars) {
    console.log(`- ${item.name}: ${item.present ? "present" : "missing"}`);
  }
  if (report.env.square_environment) {
    console.log(`- SQUARE_ENVIRONMENT valid: ${report.env.square_environment_valid}`);
  }
  if (report.payment_links) {
    console.log(`Payment links visible: ${report.payment_links.count}`);
    console.log(`Current bad $97 link visible: ${report.payment_links.current_bad_97_link ? "yes" : "no"}`);
    console.log(`Candidate replacement links: ${report.payment_links.candidate_97_replacements.length}`);
  }
  if (Object.keys(report.new_plan_links || {}).length) {
    for (const [planKey, url] of Object.entries(report.new_plan_links)) {
      console.log(`New ${PLAN_CONFIGS[planKey].label} link: ${url}`);
    }
  }
  if (report.new_97_link) {
    console.log(`New $97 link: ${report.new_97_link}`);
  }
  if (report.files_changed.length) {
    console.log(`Files changed: ${report.files_changed.join(", ")}`);
  }
  console.log(`Next agent action: ${report.next_agent_action}`);
}

if (require.main === module) {
  (async () => {
    try {
      const options = parseArgs(process.argv.slice(2));
      if (options.help) {
        printHelp();
        return;
      }
      const envLoad = envWithOptionalFile(process.env, options.envFile);
      options.envFileReport = envLoad.report;
      const report = await diagnose(options, envLoad.env);
      if (options.json) {
        console.log(JSON.stringify(report, null, 2));
      } else {
        printHuman(report);
      }
    } catch (error) {
      console.error(`square-checkout-diagnose failed: ${error.message}`);
      process.exitCode = 1;
    }
  })();
}

module.exports = {
  parseArgs,
  parseEnvFileContent,
  envWithOptionalFile,
  envReport,
  validateCreatePayload,
  PLAN_CONFIGS,
  diagnose
};
