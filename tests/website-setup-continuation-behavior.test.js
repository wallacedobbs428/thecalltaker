"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const CHECKOUT_ID = "10000000-1000-4000-8000-100000000001";
const CORRELATION_ID = "20000000-2000-4000-8000-200000000002";
const SESSION_ID = "30000000-3000-4000-8000-300000000003";
const SUBMISSION_UUID = "40000000-4000-4000-8000-400000000004";
const RECEIPT_ID = "50000000-5000-4000-8000-500000000005";
const CONTINUATION_TOKEN = `l4sc1_${"A".repeat(43)}`;
const API_ORIGIN = "https://call-taker-os.vercel.app";

function inlineScript(html, marker) {
  const scripts = Array.from(html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi), (match) => match[1]);
  const script = scripts.find((candidate) => candidate.includes(marker));
  assert.ok(script, `inline script containing ${marker} is present`);
  return script;
}

function storageHarness(initial = {}) {
  const values = new Map(Object.entries(initial).map(([key, value]) => [key, String(value)]));
  const writes = [];
  const removals = [];
  return {
    values,
    writes,
    removals,
    api: {
      getItem(key) { return values.has(key) ? values.get(key) : null; },
      setItem(key, value) {
        const text = String(value);
        values.set(key, text);
        writes.push({ key, value: text });
      },
      removeItem(key) {
        values.delete(key);
        removals.push(key);
      },
    },
  };
}

function fakeElement(id, value = "") {
  const classes = new Set();
  const attributes = new Map();
  const listeners = new Map();
  return {
    id,
    value,
    checked: false,
    disabled: false,
    textContent: "",
    innerHTML: "",
    required: false,
    style: {},
    _listeners: listeners,
    addEventListener(type, listener) {
      const current = listeners.get(type) || [];
      current.push(listener);
      listeners.set(type, current);
    },
    setAttribute(name, nextValue) { attributes.set(name, String(nextValue)); },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    checkValidity() { return true; },
    reportValidity() {},
    querySelectorAll() { return []; },
    closest() { return null; },
    classList: {
      add(...names) { names.forEach((name) => classes.add(name)); },
      remove(...names) { names.forEach((name) => classes.delete(name)); },
      toggle(name, force) {
        const enabled = force === undefined ? !classes.has(name) : Boolean(force);
        if (enabled) classes.add(name);
        else classes.delete(name);
        return enabled;
      },
      contains(name) { return classes.has(name); },
    },
  };
}

function futureExpiry() {
  return new Date(Date.now() + 60 * 60 * 1000).toISOString();
}

function continuation(overrides = {}) {
  return {
    checkoutAttemptId: CHECKOUT_ID,
    correlationId: CORRELATION_ID,
    continuationToken: CONTINUATION_TOKEN,
    expiresAt: futureExpiry(),
    submitPath: "/api/public/setup-questionnaire",
    reissuePath: "/api/public/setup-continuation",
    status: "setup_questionnaire_available",
    paymentStatus: "payment_pending",
    billingConfirmed: false,
    moneyMoved: false,
    clientActive: false,
    requiresHumanReview: true,
    providerActionPerformed: false,
    ...overrides,
  };
}

function response(body, ok = true) {
  return { ok, async json() { return body; } };
}

async function settleUntil(predicate, message) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (predicate()) return;
    await new Promise((resolve) => setImmediate(resolve));
  }
  assert.fail(message);
}

function checkoutHarness(recoveredContinuation) {
  const checkout = read("website/card-checkout.html");
  const script = inlineScript(checkout, "var SANDBOX_CHECKOUT_HOST");
  const pending = {
    version: 1,
    plan: "full247",
    idempotencyKey: "checkout-request-0001",
    correlationId: CORRELATION_ID,
    sessionId: SESSION_ID,
    checkoutAttemptId: CHECKOUT_ID,
    state: "payment_pending",
  };
  const session = storageHarness({ tct_pending_checkout_v1: JSON.stringify(pending) });
  const local = storageHarness();
  const elements = new Map();
  const ids = [
    "form", "planName", "planDetail", "heroTerms", "renewalAmount", "scopeTerms", "business", "first",
    "last", "email", "phone", "preferred", "holder", "card", "consent", "submit", "msg", "shell",
  ];
  ids.forEach((id) => elements.set(id, fakeElement(id)));
  const form = elements.get("form");
  form.setAttribute("data-tct-plan", "");
  const calls = [];
  const assigned = [];
  const replaced = [];
  const document = {
    title: "",
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, fakeElement(id));
      return elements.get(id);
    },
    createElement() { return fakeElement("script"); },
    head: { appendChild() {} },
  };
  const window = {
    location: {
      hostname: "www.thecalltaker.com",
      search: "?plan=full247",
      assign(value) { assigned.push(value); },
      replace(value) { replaced.push(value); },
    },
    crypto: { randomUUID() { return SUBMISSION_UUID; } },
    setInterval() { return 1; },
    clearInterval() {},
  };
  const fetch = async (url, init = {}) => {
    calls.push({ url: String(url), init });
    if (String(url).includes("/api/public/square-checkout-status")) {
      return response({ status: "payment_pending" });
    }
    if (String(url) === `${API_ORIGIN}/api/public/setup-continuation`) {
      return response({ ok: true, setupContinuation: recoveredContinuation });
    }
    throw new Error(`unexpected provider-free test URL: ${url}`);
  };
  const context = vm.createContext({
    URLSearchParams,
    document,
    encodeURIComponent,
    fetch,
    localStorage: local.api,
    sessionStorage: session.api,
    window,
  });
  vm.runInContext(script, context, { filename: "website/card-checkout.html" });
  return { assigned, calls, elements, local, replaced, session };
}

function intakeHarness(recoveredContinuation) {
  const intake = read("website/onboarding/intake.html");
  const script = inlineScript(intake, "BEGIN checkout-bound setup questionnaire");
  const expired = {
    version: 1,
    checkoutAttemptId: CHECKOUT_ID,
    correlationId: CORRELATION_ID,
    sessionId: SESSION_ID,
    continuationToken: `l4sc1_${"E".repeat(43)}`,
    expiresAt: new Date(Date.now() - 60 * 1000).toISOString(),
    submitPath: "/api/public/setup-questionnaire",
    apiOrigin: API_ORIGIN,
    state: "setup_continuation_issued",
  };
  const session = storageHarness({ tct_setup_continuation_v1: JSON.stringify(expired) });
  const local = storageHarness();
  const values = {
    businessName: "Example HVAC",
    industry: "hvac",
    openTime: "8:00 AM",
    closeTime: "5:00 PM",
    serviceArea: "Middle Tennessee",
    businessPhone: "6155550100",
    emergencyOnCall: "no",
    techName: "",
    techPhone: "",
    callbackTime: "Within 15 min",
    givePricing: "no",
    pricingInfo: "",
    currentHandling: "Voicemail",
    monthlyVolume: "50-100",
    aiName: "",
    specialInstructions: "",
  };
  const elements = new Map();
  for (const [id, value] of Object.entries(values)) elements.set(id, fakeElement(id, value));
  for (const id of ["intakeForm", "submitBtn", "setupGate", "formErrorBanner", "emergencyToggle", "emergencyFields", "pricingToggle", "pricingFields"]) {
    if (!elements.has(id)) elements.set(id, fakeElement(id));
  }
  elements.get("submitBtn").disabled = true;
  const form = elements.get("intakeForm");
  form.querySelectorAll = (selector) => {
    if (selector === '[name="days"]:checked') return [{ value: "Monday" }, { value: "Tuesday" }];
    if (selector === '[name="services"]:checked') return [];
    return [];
  };
  form.checkValidity = () => true;
  const calls = [];
  const assigned = [];
  const replaced = [];
  const fetch = async (url, init = {}) => {
    calls.push({ url: String(url), init });
    if (String(url) === `${API_ORIGIN}/api/public/setup-continuation`) {
      return response({ ok: true, setupContinuation: recoveredContinuation });
    }
    if (String(url) === `${API_ORIGIN}/api/public/setup-questionnaire`) {
      return response({
        status: "setup_received_pending_human_review",
        checkoutAttemptId: CHECKOUT_ID,
        correlationId: CORRELATION_ID,
        billingConfirmed: false,
        moneyMoved: false,
        clientActive: false,
        requiresHumanReview: true,
        providerActionPerformed: false,
        questionnaireReceiptId: RECEIPT_ID,
      });
    }
    throw new Error(`unexpected provider-free test URL: ${url}`);
  };
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, fakeElement(id));
      return elements.get(id);
    },
  };
  const window = {
    crypto: { randomUUID() { return SUBMISSION_UUID; } },
    location: {
      assign(value) { assigned.push(value); },
      replace(value) { replaced.push(value); },
    },
  };
  const context = vm.createContext({
    document,
    fetch,
    Intl,
    localStorage: local.api,
    sessionStorage: session.api,
    window,
  });
  vm.runInContext(script, context, { filename: "website/onboarding/intake.html" });
  return { assigned, calls, elements, expired, form, local, replaced, session };
}

function requestBody(call) {
  return JSON.parse(call.init.body);
}

test("checkout Resume posts the payment-free binding, stores only a valid continuation in-session, and redirects cleanly", async () => {
  const harness = checkoutHarness(continuation());
  const resume = harness.elements.get("resume-setup")._listeners.get("click")[0];
  await resume();

  const recovery = harness.calls.find((call) => call.url.endsWith("/api/public/setup-continuation"));
  assert.ok(recovery, "Resume calls the canonical setup-continuation route");
  assert.equal(recovery.init.method, "POST");
  assert.deepEqual(requestBody(recovery), {
    checkoutAttemptId: CHECKOUT_ID,
    correlationId: CORRELATION_ID,
    sessionId: SESSION_ID,
    website: "",
  });

  const stored = JSON.parse(harness.session.values.get("tct_setup_continuation_v1"));
  assert.equal(stored.continuationToken, CONTINUATION_TOKEN);
  assert.equal(stored.checkoutAttemptId, CHECKOUT_ID);
  assert.equal(stored.correlationId, CORRELATION_ID);
  assert.equal(stored.sessionId, SESSION_ID);
  assert.equal(stored.apiOrigin, API_ORIGIN);
  assert.equal(harness.local.values.size, 0, "continuation never reaches localStorage");
  assert.deepEqual(harness.assigned, ["/onboarding/intake.html#setup"]);
  assert.equal(harness.assigned[0].includes(CONTINUATION_TOKEN), false, "redirect contains no bearer token");
  assert.deepEqual(harness.replaced, []);
});

for (const scenario of [
  ["billing claim", { billingConfirmed: true }],
  ["provider-action claim", { providerActionPerformed: true }],
]) {
  test(`checkout Resume rejects a ${scenario[0]} and does not redirect`, async () => {
    const harness = checkoutHarness(continuation(scenario[1]));
    const resume = harness.elements.get("resume-setup")._listeners.get("click")[0];
    await resume();

    assert.equal(harness.session.values.has("tct_setup_continuation_v1"), false);
    assert.deepEqual(harness.assigned, []);
    assert.deepEqual(harness.replaced, []);
    assert.equal(harness.elements.get("resume-setup").disabled, false, "safe retry remains available");
    assert.match(harness.elements.get("pending-status").textContent, /could not verify a protected setup handoff/i);
  });
}

test("intake refreshes an expired context and submits with a checkout-scoped identity", async () => {
  const harness = intakeHarness(continuation());
  await settleUntil(() => harness.elements.get("submitBtn").disabled === false, "expired intake did not recover");

  const recovery = harness.calls.find((call) => call.url.endsWith("/api/public/setup-continuation"));
  assert.ok(recovery, "expired intake calls the canonical recovery route");
  assert.deepEqual(requestBody(recovery), {
    checkoutAttemptId: CHECKOUT_ID,
    correlationId: CORRELATION_ID,
    sessionId: SESSION_ID,
    website: "",
  });

  const refreshed = JSON.parse(harness.session.values.get("tct_setup_continuation_v1"));
  assert.equal(refreshed.continuationToken, CONTINUATION_TOKEN, "expired token is replaced");
  assert.notEqual(refreshed.continuationToken, harness.expired.continuationToken);
  const identityStorageKey = `tct_setup_submission_idempotency_v1:${CHECKOUT_ID}`;
  const expectedIdentity = `setup:${CHECKOUT_ID}:${SUBMISSION_UUID}`;
  assert.equal(harness.session.values.get(identityStorageKey), expectedIdentity);

  const submit = harness.form._listeners.get("submit")[0];
  await submit({ preventDefault() {} });
  const questionnaire = harness.calls.find((call) => call.url.endsWith("/api/public/setup-questionnaire"));
  assert.ok(questionnaire, "recovered context can submit to the questionnaire route");
  const body = requestBody(questionnaire);
  assert.equal(body.submissionIdempotencyKey, expectedIdentity);
  assert.equal(body.checkoutAttemptId, CHECKOUT_ID);
  assert.equal(body.correlationId, CORRELATION_ID);
  assert.equal(body.sessionId, SESSION_ID);
  assert.equal(body.continuationToken, CONTINUATION_TOKEN);
  assert.equal(body.website, "");
  assert.equal(Object.hasOwn(body, "plan"), false);
  assert.equal(Object.hasOwn(body, "sourceId"), false);
  assert.equal(Object.hasOwn(body, "paymentMethod"), false);
  assert.deepEqual(harness.assigned, []);
  assert.deepEqual(harness.replaced, []);
  assert.equal(harness.local.values.size, 0);
});

for (const scenario of [
  ["mismatched binding", { correlationId: "60000000-6000-4000-8000-600000000006" }],
  ["provider-action claim", { providerActionPerformed: true }],
  ["money-movement claim", { moneyMoved: true }],
]) {
  test(`intake keeps ${scenario[0]} recovery blocked and performs no redirect`, async () => {
    const harness = intakeHarness(continuation(scenario[1]));
    await settleUntil(
      () => /could not be refreshed/i.test(harness.elements.get("setupGate").innerHTML),
      `${scenario[0]} recovery did not settle into a blocked state`,
    );

    assert.equal(harness.elements.get("submitBtn").disabled, true);
    assert.equal(harness.calls.filter((call) => call.url.endsWith("/api/public/setup-questionnaire")).length, 0);
    assert.deepEqual(harness.assigned, []);
    assert.deepEqual(harness.replaced, []);
    assert.equal(
      JSON.parse(harness.session.values.get("tct_setup_continuation_v1")).continuationToken,
      harness.expired.continuationToken,
      "invalid recovery cannot replace the expired context",
    );
  });
}
