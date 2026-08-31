"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..");
const workflow = fs.readFileSync(path.join(root, ".github/workflows/deploy.yml"), "utf8");
const home = fs.readFileSync(path.join(root, "website/index.html"), "utf8");
const canonical = fs.readFileSync(path.join(root, "website/tct-funnel-events.js"), "utf8");
const ITEM_ID = "ready_007";
const ASSET_SHA256 = "39a11584815d2f75189849055e5cdc4859d5dbd5a337a8d0f2669c8d57319c57";
const PUBLICATION_SEED_SHA256 = "8bcaf881d4598dce804da777dc76c6f336210cd3fc76d22d37db7bca93821000";
const CORRELATION_ID = "32345678-1234-4123-8123-123456789012";
const TEST_RUN_ID = "42345678-1234-4123-8123-123456789012";

function environment(search, initialAttribution) {
  const storage = new Map();
  const requests = [];
  let uuidCounter = 0;
  if (initialAttribution) storage.set("tct_attribution", JSON.stringify(initialAttribution));
  const anchor = {
    href: "https://thecalltaker.com/card-checkout.html?plan=full247",
    dataset: { tctPage: "homepage", tctPlan: "full247", tctCta: "Start Free Trial", tctDestination: "card_checkout" },
    textContent: "Start Free Trial",
  };
  const body = {
    dataset: {},
    getAttribute(name) {
      if (name === "data-tct-view") return "homepage_view";
      if (name === "data-tct-page") return "homepage";
      return "";
    },
  };
  const document = {
    readyState: "complete",
    body,
    addEventListener() {},
    querySelector() { return null; },
    querySelectorAll(selector) { return selector === "a[data-tct-event],a[data-preserve]" ? [anchor] : []; },
  };
  const window = {
    TCT_FUNNEL_CONFIG: {},
    location: { search, pathname: "/", origin: "https://thecalltaker.com" },
    innerWidth: 1200,
    document,
    URLSearchParams,
    CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init.detail; } },
    dispatchEvent() {},
    crypto: {
      randomUUID() {
        uuidCounter += 1;
        return `00000000-0000-4000-8000-${String(uuidCounter).padStart(12, "0")}`;
      },
    },
    sessionStorage: {
      getItem(key) { return storage.has(key) ? storage.get(key) : null; },
      setItem(key, value) { storage.set(key, String(value)); },
    },
    fetch(url, options) {
      requests.push({ url, options, body: JSON.parse(options.body) });
      return Promise.resolve({ ok: true });
    },
  };
  const context = vm.createContext({ window, document, URL, URLSearchParams, Date, JSON, Object, Math, Uint8Array, CustomEvent: window.CustomEvent });
  return { context, window, storage, requests, anchor };
}

test("one canonical producer is deployed", () => {
  assert.equal(workflow.includes("tct-first-party-attribution.js"), false, "competing event producer is excluded from Pages");
  assert.equal(home.includes("tct-first-party-attribution.js"), false, "homepage uses one producer");
  for (const key of ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "tct_item_id", "tct_asset_sha256", "tct_publication_seed_sha256"]) {
    assert.match(canonical, new RegExp(key));
  }
});

test("valid content attribution survives session, CTA navigation, and event persistence", () => {
  const search = `?utm_source=instagram&utm_medium=organic_social&utm_campaign=${ITEM_ID}&tct_item_id=${ITEM_ID}&tct_asset_sha256=${ASSET_SHA256}&tct_publication_seed_sha256=${PUBLICATION_SEED_SHA256}&correlation_id=${CORRELATION_ID}`;
  const env = environment(search);
  vm.runInContext(canonical, env.context);

  const stored = JSON.parse(env.storage.get("tct_attribution"));
  assert.equal(stored.tct_item_id, ITEM_ID);
  assert.equal(stored.tct_asset_sha256, ASSET_SHA256);
  assert.equal(stored.tct_publication_seed_sha256, PUBLICATION_SEED_SHA256);
  assert.equal(env.storage.get("tct_correlation_id_v1"), CORRELATION_ID);

  const target = new URL(env.anchor.href, "https://thecalltaker.com");
  assert.equal(target.searchParams.get("tct_item_id"), ITEM_ID);
  assert.equal(target.searchParams.get("tct_asset_sha256"), ASSET_SHA256);
  assert.equal(target.searchParams.get("tct_publication_seed_sha256"), PUBLICATION_SEED_SHA256);
  assert.equal(target.searchParams.get("correlation_id"), CORRELATION_ID);

  assert.equal(env.requests.length, 1);
  assert.equal(env.requests[0].body.event_type, "page_view");
  assert.equal(env.requests[0].body.content_key, ITEM_ID);
  assert.equal(env.requests[0].body.source_asset_sha256, ASSET_SHA256);
  assert.equal(env.requests[0].body.source_publication_seed_sha256, PUBLICATION_SEED_SHA256);
  assert.deepEqual(env.requests[0].body.details, {
    cta: "",
    destination: "",
    receipt_role: "",
    content_key: ITEM_ID,
  });
});

test("a controlled attribution run is explicitly tagged and forwarded without touching real attribution state", () => {
  const env = environment(`?tct_attribution_test=${TEST_RUN_ID}`);
  vm.runInContext(canonical, env.context);
  const target = new URL(env.anchor.href, "https://thecalltaker.com");
  assert.equal(target.searchParams.get("tct_attribution_test"), TEST_RUN_ID);
  assert.equal(env.requests[0].body.traffic_kind, "controlled_test");
  assert.equal(env.requests[0].body.test_run_id, TEST_RUN_ID);
  assert.equal(env.requests[0].body.source, "direct");
  assert.equal("email" in env.requests[0].body, false);
});

test("invalid content identifiers fail closed instead of entering session, links, or events", () => {
  const env = environment(
    "?tct_item_id=bad%20item&tct_asset_sha256=not-a-sha&tct_publication_seed_sha256=1234",
    { tct_item_id: "also bad", tct_asset_sha256: "xyz", tct_publication_seed_sha256: "short" },
  );
  vm.runInContext(canonical, env.context);

  const target = new URL(env.anchor.href, "https://thecalltaker.com");
  const stored = JSON.parse(env.storage.get("tct_attribution"));
  for (const key of ["tct_item_id", "tct_asset_sha256", "tct_publication_seed_sha256"]) {
    assert.equal(Object.hasOwn(stored, key), false, `${key} is removed from session`);
    assert.equal(target.searchParams.has(key), false, `${key} is not forwarded`);
  }
  assert.equal(env.requests[0].body.content_key, null);
  assert.equal(env.requests[0].body.source_asset_sha256, null);
  assert.equal(env.requests[0].body.source_publication_seed_sha256, null);
});

test("private or unissued UTM values are never stored, forwarded, or emitted", () => {
  const env = environment("?utm_source=meta&utm_medium=cpc&utm_campaign=owner%40example.com&utm_content=6155551234&utm_term=plumbing%20owner");
  vm.runInContext(canonical, env.context);
  const stored = JSON.parse(env.storage.get("tct_attribution"));
  const target = new URL(env.anchor.href, "https://thecalltaker.com");
  assert.equal(stored.utm_source, "facebook");
  assert.equal(stored.utm_medium, "paid_search");
  for (const key of ["utm_campaign", "utm_content", "utm_term"]) {
    assert.equal(Object.hasOwn(stored, key), false);
    assert.equal(target.searchParams.has(key), false);
    assert.equal(env.requests[0].body[key === "utm_campaign" ? "campaign" : key], null);
  }
  assert.equal(target.searchParams.get("utm_source"), "facebook");
  assert.equal(target.searchParams.get("utm_medium"), "paid_search");
  assert.equal(env.requests[0].body.source, "facebook");
  assert.equal(env.requests[0].body.channel, "paid_search");
});

test("CTA observations are emitted as intent, never provider or activation truth", () => {
  const env = environment("");
  vm.runInContext(canonical, env.context);
  env.window.TCTFunnelEvents.record("pricing_plan_click", env.anchor);
  env.anchor.dataset.tctDestination = "demo";
  env.window.TCTFunnelEvents.record("homepage_cta_click", env.anchor);
  env.window.TCTFunnelEvents.record("demo_preview_rendered_ui", env.anchor);
  env.anchor.dataset.tctCta = "Recorded AI sample completed";
  env.anchor.dataset.tctDestination = "browser_audio";
  env.window.TCTFunnelEvents.record("cta_intent", env.anchor);
  assert.deepEqual(env.requests.map((request) => request.body.event_type), [
    "page_view",
    "checkout_intent_opened",
    "demo_preview_intent",
    "demo_preview_rendered_ui",
    "cta_intent",
  ]);
});

test("durable CTA details are bounded public slugs, not free-form page text", () => {
  assert.match(canonical, /function detailSlug\(value\)/);
  assert.match(canonical, /cta: detailSlug\(payload\.cta\)/);
  assert.match(canonical, /destination: detailSlug\(payload\.destination_type\)/);
});
