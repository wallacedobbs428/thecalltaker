const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "..", "tct-first-party-attribution.js"),
  "utf8",
);
const ASSET = "39a11584815d2f75189849055e5cdc4859d5dbd5a337a8d0f2669c8d57319c57";
const CAPTION = "65ea056299a6dfeda7e6f0754b0f1e392eb633c6a723c8045d6f65627b172f55";
const LOCAL_DATE = "2026-07-15";
const ITEM_ID = "ready_007";
function seed(platform) {
  return crypto.createHash("sha256").update(JSON.stringify({
    asset_sha256: ASSET,
    item_id: ITEM_ID,
    local_date: LOCAL_DATE,
    source_platform: platform,
  })).digest("hex");
}

function environment(search) {
  const storage = new Map();
  const requests = [];
  const diagnostics = [];
  let intervalCallback = null;
  let uuidCounter = 0;
  const document = {
    readyState: "complete",
    visibilityState: "visible",
    addEventListener() {},
    getElementById(id) {
      return id === "pricing" ? { getBoundingClientRect: () => ({ top: 20 }) } : null;
    },
  };
  const window = {
    location: { search, pathname: "/", hash: "#pricing" },
    innerHeight: 900,
    document,
    URLSearchParams,
    CustomEvent: class CustomEvent {
      constructor(name, init) { this.name = name; this.detail = init.detail; }
    },
    dispatchEvent(event) { diagnostics.push(event.detail); },
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
    async fetch(url, options) {
      const body = JSON.parse(options.body);
      requests.push({ url, options, body });
      return {
        ok: true,
        status: 201,
        async json() {
          return {
            ok: true,
            receipt: {
              event_type: body.event_type,
              receipt_verified: true,
              receipt_sha256: body.event_type.padEnd(64, "0").slice(0, 64),
            },
          };
        },
      };
    },
    setInterval(callback) { intervalCallback = callback; return 1; },
    clearInterval() {},
  };
  const context = vm.createContext({ window, document, URLSearchParams, Date, JSON, Object, Math, Uint8Array });
  return { context, requests, diagnostics, storage, getInterval: () => intervalCallback };
}

async function flush() {
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));
}

test("stays dormant when exact asset-bound attribution is absent", async () => {
  const env = environment(`?utm_source=instagram&utm_medium=organic_social&utm_campaign=ready_007&utm_content=39a11584&tct_asset_sha256=${ASSET}&tct_local_date=${LOCAL_DATE}&tct_item_id=${ITEM_ID}&tct_clickable=0`);
  vm.runInContext(source, env.context);
  await flush();
  assert.equal(env.requests.length, 0);
  assert.equal(env.diagnostics[0].name, "inactive_missing_exact_asset_attribution");
});

test("emits ordered PII-free session, pricing, and qualified requests", async () => {
  const search = `?utm_source=instagram&utm_medium=organic_social&utm_campaign=ready_007&utm_content=39a11584&tct_asset_sha256=${ASSET}&tct_publication_seed_sha256=${seed("instagram")}&tct_local_date=${LOCAL_DATE}&tct_item_id=${ITEM_ID}&tct_clickable=0`;
  const env = environment(search);
  vm.runInContext(source, env.context);
  await flush();
  assert.deepEqual(env.requests.map((item) => item.body.event_type), [
    "website_session_started",
    "pricing_viewed",
  ]);
  const interval = env.getInterval();
  assert.equal(typeof interval, "function");
  for (let index = 0; index < 29; index += 1) await interval();
  await interval();
  await flush();
  assert.deepEqual(env.requests.map((item) => item.body.event_type), [
    "website_session_started",
    "pricing_viewed",
    "qualified_session",
  ]);
  assert.equal(env.requests[2].body.engagement_seconds, 30);
  for (const request of env.requests) {
    assert.equal(request.url, "https://call-taker-os.vercel.app/api/public/buyer-event");
    assert.equal(request.options.credentials, "omit");
    assert.equal(request.options.keepalive, true);
    assert.equal("email" in request.body, false);
    assert.equal("phone" in request.body, false);
    assert.equal("name" in request.body, false);
    assert.equal("fbclid" in request.body, false);
    assert.equal("gclid" in request.body, false);
    assert.equal(request.body.schema_version, "tct.public-buyer-event.v2");
    assert.equal(request.body.source_platform, "instagram");
    assert.equal(request.body.source_destination_clickable, false);
    assert.equal(request.body.source_publication_seed_sha256, seed("instagram"));
    assert.equal("source_caption_sha256" in request.body, false);
    assert.equal("source_publication_receipt_sha256" in request.body, false);
  }
});

test("uses platform-specific sources and preserves the actual click surface", async () => {
  const facebook = environment(`?utm_source=facebook&utm_medium=organic_social&utm_campaign=ready_007&utm_content=39a11584&tct_asset_sha256=${ASSET}&tct_publication_seed_sha256=${seed("facebook")}&tct_local_date=${LOCAL_DATE}&tct_item_id=${ITEM_ID}&tct_clickable=1`);
  vm.runInContext(source, facebook.context);
  await flush();
  assert.equal(facebook.requests.length, 2);
  assert.equal(facebook.requests[0].body.source_platform, "facebook");
  assert.equal(facebook.requests[0].body.source_destination_clickable, true);

  const aggregate = environment(`?utm_source=meta_organic&utm_medium=organic_social&utm_campaign=ready_007&utm_content=39a11584&tct_asset_sha256=${ASSET}&tct_publication_seed_sha256=${seed("instagram")}&tct_local_date=${LOCAL_DATE}&tct_item_id=${ITEM_ID}&tct_clickable=0`);
  vm.runInContext(source, aggregate.context);
  await flush();
  assert.equal(aggregate.requests.length, 0);
  assert.equal(aggregate.diagnostics[0].name, "inactive_missing_exact_asset_attribution");
});
