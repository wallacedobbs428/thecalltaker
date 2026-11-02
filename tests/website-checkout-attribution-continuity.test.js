'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '../website/card-checkout.html'), 'utf8');
const identity = html.match(/\/\/ BEGIN checkout request identity([\s\S]*?)\/\/ END checkout request identity/)[1];
const attribution = html.slice(html.indexOf('      function validContentAttribution('), html.indexOf('      function showPending('));
const PENDING = 'tct_pending_checkout_v1';
const A = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const B = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const SESSION = 'cccccccc-cccc-4ccc-8ccc-cccccccccccc';
const CHECKOUT = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd';
const query = '?plan=full247&correlation_id=' + A + '&utm_source=email&utm_medium=email&utm_campaign=canonical-one-email-pilot';
const plain = value => JSON.parse(JSON.stringify(value));
function storage(initial = {}, options = {}) {
  const values = new Map(Object.entries(initial));
  return { values, getItem(k) { if (options.readThrows) throw Error('blocked'); return values.has(k) ? values.get(k) : null; },
    setItem(k, v) { if (options.writeThrows) throw Error('blocked'); if (options.dropWrites) return;
      if (options.omitAttribution && k === PENDING) { const o = JSON.parse(v); delete o.attribution; v = JSON.stringify(o); }
      values.set(k, String(v)); } };
}
function harness(search = query, initial = {}, options = {}) {
  const store = storage(initial, options); let count = 0;
  const window = { location: { search }, crypto: { randomUUID() { return '10000000-1000-4000-8000-' + String(++count).padStart(12, '0'); } } };
  const context = vm.createContext({ window, URLSearchParams, key: new URLSearchParams(search).get('plan') || 'full247', PENDING_CHECKOUT_KEY: PENDING, sessionStorage: store });
  vm.runInContext(identity + attribution, context);
  return { window, store, context, request() { return plain(vm.runInContext('checkoutRequestIdentity()', context)); }, get issued() { return count; } };
}
test('exact incoming email company survives absent tracker and stale global correlation', () => {
  const h = harness(query, { tct_correlation_id_v1: B, tct_buyer_session_v1: SESSION });
  const r = h.request();
  assert.equal(r.correlationId, A); assert.equal(r.sessionId, SESSION); assert.equal(r.version, 2);
  assert.equal(r.attribution.campaign, 'canonical-one-email-pilot'); assert.equal(r.attribution.channel, 'email');
  assert.deepEqual(JSON.parse(h.store.values.get(PENDING)), r); assert.equal(h.issued, 1);
});
test('explicit company link cannot inherit content or campaign from an unrelated visit', () => {
  const h = harness('?plan=full247&correlation_id=' + A, { tct_correlation_id_v1: B,
    tct_attribution: JSON.stringify({ utm_source: 'instagram', utm_medium: 'organic_social', utm_campaign: 'older-campaign', tct_item_id: 'old-item', tct_asset_sha256: 'f'.repeat(64) }) });
  const r = h.request();
  assert.equal(r.correlationId, A); assert.equal(r.attribution.campaign, ''); assert.equal(r.attribution.content_key, '');
  assert.equal(r.attribution.source_asset_sha256, ''); assert.equal(r.attribution.source, 'website');
});
test('direct navigation retains valid existing first party session/correlation and sanitized metadata', () => {
  const h = harness('?plan=full247', { tct_correlation_id_v1: A, tct_buyer_session_v1: SESSION,
    tct_attribution: JSON.stringify({ utm_source: 'email', utm_medium: 'email', utm_campaign: 'canonical-one-email-pilot', email: 'private@example.invalid', card: 'never-copy' }) });
  const r = h.request(); assert.equal(r.correlationId, A); assert.equal(r.sessionId, SESSION);
  assert.equal(r.attribution.campaign, 'canonical-one-email-pilot'); assert.equal(JSON.stringify(r).includes('private@'), false);
  assert.equal(JSON.stringify(r).includes('never-copy'), false);
});
test('lost-response retry and reload retain the original snapshot despite query and tracker changes', () => {
  const h = harness(); const first = h.request();
  h.window.location.search = '?plan=full247&utm_source=instagram&utm_campaign=later-visit';
  h.store.setItem('tct_correlation_id_v1', B); h.store.setItem('tct_buyer_session_v1', SESSION);
  h.store.setItem('tct_attribution', JSON.stringify({ utm_source: 'facebook', utm_campaign: 'changed' }));
  assert.deepEqual(h.request(), first);
  const reload = harness(h.window.location.search, Object.fromEntries(h.store.values));
  assert.deepEqual(reload.request(), first); assert.equal(reload.issued, 0);
});
test('another explicit company or plan holds without replacing a potentially accepted monetary request', () => {
  const h = harness(); const first = h.request(); const before = h.store.values.get(PENDING); const issued = h.issued;
  h.window.location.search = '?plan=full247&correlation_id=' + B;
  assert.throws(() => h.request(), /original checkout link/); assert.equal(h.store.values.get(PENDING), before); assert.equal(h.issued, issued);
  const other = harness(query, { [PENDING]: JSON.stringify({ ...first, plan: 'afterhours' }) });
  assert.throws(() => other.request(), /another plan/); assert.equal(other.issued, 0);
});
test('duplicate, empty and malformed explicit correlations never fall back to a fresh monetary identity', () => {
  for (const q of ['correlation_id=', 'correlation_id=bad', 'correlation_id=' + A + '&correlation_id=' + B, 'correlation_id=' + A + '&correlation_id=' + A]) {
    const h = harness('?plan=full247&' + q); assert.throws(() => h.request(), /original pricing link/); assert.equal(h.issued, 0); assert.equal(h.store.values.has(PENDING), false);
  }
  assert.equal(harness(query.replace(A, A.toUpperCase())).request().correlationId, A);
});
test('unreadable/malformed existing storage and legacy uncertain identities require recovery, with zero regenerated IDs', () => {
  const legacy = { version: 1, plan: 'full247', idempotencyKey: 'legacy-request-001', correlationId: A, sessionId: SESSION };
  for (const raw of ['{', 'null', '[]', '"oops"', JSON.stringify(legacy)]) {
    const h = harness(query, { [PENDING]: raw }); assert.throws(() => h.request(), /recover|recovery/); assert.equal(h.issued, 0); assert.equal(h.store.values.get(PENDING), raw);
  }
  const h = harness(query, {}, { readThrows: true }); assert.throws(() => h.request(), /recover/); assert.equal(h.issued, 0);
});
test('failed, silently discarded or partially persisted snapshots stop before returning a submission identity', () => {
  for (const opts of [{ writeThrows: true }, { dropWrites: true }, { omitAttribution: true }]) {
    const h = harness(query, {}, opts); assert.throws(() => h.request(), /session storage/);
  }
});
test('snapshot unknown fields, missing normalized fields and malformed values cannot reach a retry', () => {
  const valid = harness().request();
  for (const mutate of [r => { r.attribution.email = 'never-copy@example.invalid'; }, r => { delete r.attribution.channel; }, r => { r.attribution.source = 'https://bad.invalid'; }, r => { r.attribution.source_asset_sha256 = 'bad'; }, r => { r.attribution = []; }, r => { r.version = 999; }]) {
    const r = plain(valid); mutate(r); const h = harness(query, { [PENDING]: JSON.stringify(r) }); assert.throws(() => h.request(), /recovery/); assert.equal(h.issued, 0);
  }
});

// Execute the full actual inline form handler with fake Square and HTTP. There
// is no browser, provider SDK load or outbound network in this fixture.
async function formHarness(options = {}) {
  const store = storage(options.initial); const elements = new Map(); const posts = []; const assigns = []; let tokenizations = 0;
  function element(id) {
    if (!elements.has(id)) elements.set(id, { id, value: 'Synthetic', checked: true, dataset: { offerVersion: 'synthetic' }, disabled: false,
      textContent: '', innerHTML: '', listeners: {}, setAttribute() {}, checkValidity() { return true; },
      addEventListener(name, cb) { this.listeners[name] = cb; } });
    return elements.get(id);
  }
  const document = { title: '', getElementById: element, createElement() { return {}; }, head: { appendChild(script) { script.onload(); } } };
  let count = 0;
  const window = { location: { hostname: 'thecalltaker.com', search: options.search || query, assign(v) { assigns.push(v); }, replace() {} },
    crypto: { randomUUID() { return '10000000-1000-4000-8000-' + String(++count).padStart(12, '0'); } },
    Square: { payments() { return { async card() { return { async attach() {}, async tokenize() { tokenizations++; return { status: 'OK', token: 'synthetic-card-token', details: { billing: { postalCode: '00000' } } }; } }; } }; } } };
  const fetch = async (url, init = {}) => {
    if (init.method === 'POST') {
      assert.match(url, /\/api\/public\/square-trial$/); const body = JSON.parse(init.body); posts.push(body);
      if (options.dropResponse) throw Error('synthetic lost response');
      return { ok: true, async json() { return { ok: true, status: 'payment_pending', checkoutAttemptId: CHECKOUT, correlationId: body.correlationId }; } };
    }
    if (url.includes('square-checkout-status')) return { ok: true, async json() { return { status: 'payment_pending' }; } };
    assert.match(url, /\/api\/public\/square-trial$/);
    return { ok: true, async json() { return { applicationId: 'synthetic', locationId: 'synthetic', webPaymentsSdkUrl: 'https://web.squarecdn.com/v1/square.js' }; } };
  };
  const script = Array.from(html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi), m => m[1]).find(s => s.includes('var SANDBOX_CHECKOUT_HOST'));
  vm.runInNewContext(script, { document, window, URLSearchParams, sessionStorage: store, fetch, encodeURIComponent });
  for (let i = 0; i < 5; i++) await new Promise(resolve => setImmediate(resolve));
  return { store, window, elements, posts, assigns, get tokenizations() { return tokenizations; }, async submit() { await element('form').listeners.submit({ preventDefault() {} }); } };
}
test('full form submits frozen attribution, retains it after acceptance, and never stores card or buyer form fields', async () => {
  const h = await formHarness(); await h.submit(); assert.equal(h.posts.length, 1); assert.equal(h.posts[0].correlationId, A);
  const saved = JSON.parse(h.store.values.get(PENDING)); assert.equal(saved.version, 2); assert.equal(saved.checkoutAttemptId, CHECKOUT);
  assert.deepEqual(saved.attribution, h.posts[0].attribution); assert.equal(saved.attribution.source, 'email');
  assert.equal(saved.sourceId, undefined); assert.equal(saved.businessName, undefined); assert.equal(JSON.stringify(saved).includes('synthetic-card-token'), false);
});
test('full form uses original snapshot after lost response and holds conflicting links before card tokenization', async () => {
  const h = await formHarness({ dropResponse: true }); await h.submit();
  const first = h.posts[0]; h.window.location.search = '?plan=full247&utm_source=facebook&utm_campaign=later';
  await h.submit(); assert.equal(h.posts.length, 2); assert.deepEqual(h.posts[1].attribution, first.attribution);
  assert.equal(h.posts[1].idempotencyKey, first.idempotencyKey); assert.equal(h.posts[1].correlationId, A);
  h.window.location.search = '?plan=full247&correlation_id=' + B; await h.submit();
  assert.equal(h.posts.length, 2); assert.equal(h.tokenizations, 2); assert.match(h.elements.get('msg').textContent, /original checkout link/);
});
test('accepted legacy checkouts keep existing status/setup recovery without resubmitting a trial', async () => {
  const h = await formHarness({ initial: { [PENDING]: JSON.stringify({ version: 1, plan: 'full247', idempotencyKey: 'legacy-request-001', correlationId: A, sessionId: SESSION, checkoutAttemptId: CHECKOUT, state: 'payment_pending' }) } });
  assert.match(h.elements.get('shell').innerHTML, /Resume setup questionnaire/); assert.equal(h.posts.length, 0); assert.equal(h.tokenizations, 0);
  assert.equal(JSON.parse(h.store.values.get(PENDING)).checkoutAttemptId, CHECKOUT);
});

test('actual pricing CTA and canonical producer carry the same email company into all three checkout plans', () => {
  const pricing = fs.readFileSync(path.join(__dirname, '../website/pricing.html'), 'utf8');
  const producer = fs.readFileSync(path.join(__dirname, '../website/tct-funnel-events.js'), 'utf8');
  for (const plan of ['afterhours', 'full247', 'custom']) {
    const href = pricing.match(new RegExp('href="(/card-checkout\\.html\\?plan=' + plan + ')"'))[1];
    const anchor = { href: 'https://thecalltaker.com' + href };
    const shared = storage(); let count = 0;
    const document = { readyState: 'complete', body: null, addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return [anchor]; } };
    const window = { TCT_FUNNEL_CONFIG: { dryRun: true }, location: { search: query, pathname: '/pricing', origin: 'https://thecalltaker.com' },
      sessionStorage: shared, crypto: { randomUUID() { return '10000000-1000-4000-8000-' + String(++count).padStart(12, '0'); } } };
    vm.runInNewContext(producer, { window, document, URL, URLSearchParams });
    const target = new URL(anchor.href, window.location.origin);
    assert.equal(target.searchParams.get('correlation_id'), A); assert.equal(target.searchParams.get('plan'), plan);
    const checkout = harness(target.search, Object.fromEntries(shared.values)).request();
    assert.equal(checkout.correlationId, A); assert.equal(checkout.attribution.campaign, 'canonical-one-email-pilot'); assert.equal(checkout.plan, plan);
  }
});

test('pricing inline email handoff works before/without tracking, then a late producer cannot mix prior-company content', () => {
  const pricing = fs.readFileSync(path.join(__dirname, '../website/pricing.html'), 'utf8');
  const navigation = pricing.split('// BEGIN issued email checkout navigation')[1].split('// END issued email checkout navigation')[0];
  const producer = fs.readFileSync(path.join(__dirname, '../website/tct-funnel-events.js'), 'utf8');
  for (const prettyUrls of [false, true]) for (const lateTracker of [false, true]) {
    const anchors = Array.from(pricing.matchAll(/href="(\/card-checkout\.html\?plan=[^"]+)"/g), m => ({ href: 'https://thecalltaker.com' + (prettyUrls ? m[1].replace('/card-checkout.html?', '/card-checkout?') : m[1]) }));
    assert.equal(anchors.length, 4);
    const foreign = { href: 'https://other.invalid/card-checkout.html?plan=full247' };
    const bound = { href: 'https://thecalltaker.com/card-checkout.html?plan=full247&correlation_id=' + B };
    const unknown = { href: 'https://thecalltaker.com/card-checkout.html?plan=unknown' };
    const shared = storage({ tct_correlation_id_v1: B, tct_buyer_session_v1: SESSION, tct_attribution: JSON.stringify({ utm_source: 'instagram', tct_item_id: 'old-company-item', tct_asset_sha256: 'f'.repeat(64) }) });
    const document = { readyState: 'complete', body: null, addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return anchors.concat([foreign, bound, unknown]); } };
    const window = { TCT_FUNNEL_CONFIG: { dryRun: true }, location: { search: query, pathname: '/pricing', origin: 'https://thecalltaker.com' }, sessionStorage: shared,
      crypto: { randomUUID() { throw Error('existing buyer session should be retained'); } } };
    const context = vm.createContext({ window, document, URL, URLSearchParams });
    vm.runInContext(navigation, context);
    for (const anchor of anchors) assert.equal(new URL(anchor.href, window.location.origin).searchParams.get('correlation_id'), A);
    assert.equal(new URL(foreign.href).searchParams.has('correlation_id'), false);
    assert.equal(new URL(bound.href).searchParams.get('correlation_id'), B);
    assert.equal(new URL(unknown.href).searchParams.has('correlation_id'), false);
    if (lateTracker) {
      // Restrict the canonical selector to actual unbound pricing CTAs. It
      // remains the sole event producer; dryRun prohibits network/analytics.
      document.querySelectorAll = () => anchors;
      vm.runInContext(producer, context);
      assert.equal(shared.getItem('tct_buyer_session_v1'), SESSION);
    }
    for (const anchor of anchors) {
      const request = harness(new URL(anchor.href, window.location.origin).search, Object.fromEntries(shared.values)).request();
      assert.equal(request.correlationId, A); assert.equal(request.attribution.source, 'email');
      assert.equal(request.attribution.campaign, 'canonical-one-email-pilot'); assert.equal(request.attribution.content_key, ''); assert.equal(request.attribution.source_asset_sha256, '');
    }
  }
});
test('canonical producer retains same-company continuation metadata and pending monetary identity', () => {
  const producer = fs.readFileSync(path.join(__dirname, '../website/tct-funnel-events.js'), 'utf8');
  const original = harness().request();
  for (const incoming of [A, B]) {
    const shared = storage({ [PENDING]: JSON.stringify(original), tct_correlation_id_v1: A, tct_buyer_session_v1: SESSION,
      tct_attribution: JSON.stringify({ utm_source: 'email', utm_medium: 'email', utm_campaign: 'prior-campaign', tct_item_id: 'retained-item' }) });
    const window = { TCT_FUNNEL_CONFIG: { dryRun: true }, location: { search: '?correlation_id=' + incoming, pathname: '/pricing', origin: 'https://thecalltaker.com' }, sessionStorage: shared };
    const document = { readyState: 'complete', body: null, addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; } };
    vm.runInNewContext(producer, { window, document, URL, URLSearchParams });
    const captured = JSON.parse(shared.getItem('tct_attribution'));
    assert.equal(captured.tct_item_id, incoming === A ? 'retained-item' : undefined);
    assert.equal(shared.getItem(PENDING), JSON.stringify(original)); assert.equal(shared.getItem('tct_buyer_session_v1'), SESSION);
  }
});


test('offer acceptance stays bound to the original request across reloads and retries', () => {
  const first = harness().request();
  assert.equal(first.acceptedOfferVersion, 'ctos.standard-service-offer.self-service.v2');
  for (const version of ['ctos.standard-service-offer.v1', undefined]) {
    const original = { ...first, acceptedOfferVersion: version };
    const h = harness(query, { [PENDING]: JSON.stringify(original) });
    assert.deepEqual(h.request(), plain(original));
    assert.equal(h.issued, 0);
  }
  const invalid = { ...first, acceptedOfferVersion: 'unsupported' };
  assert.throws(() => harness(query, { [PENDING]: JSON.stringify(invalid) }).request(), /recovery/);
  assert.equal(harness('?plan=custom').request().acceptedOfferVersion, 'ctos.standard-service-offer.v1');
});


test('automated onboarding email is a separate opt-in that survives accepted and uncertain checkout retries', async () => {
  const h = await formHarness({ dropResponse: true });
  h.elements.get('preferred').value = 'email';
  h.elements.get('automated-email-consent').checked = true;
  await h.submit();
  assert.equal(h.posts[0].acceptedCorrespondenceVersion, 'ctos.onboarding-correspondence.v2');
  assert.equal(h.posts[0].consentToAutomatedEmail, true);
  h.elements.get('automated-email-consent').checked = false;
  h.elements.get('preferred').value = 'phone';
  await h.submit();
  assert.equal(h.posts[1].acceptedCorrespondenceVersion, h.posts[0].acceptedCorrespondenceVersion);
  assert.equal(h.posts[1].consentToAutomatedEmail, true);
  assert.equal(h.posts[1].preferredContactMethod, 'email');
  const accepted = await formHarness();
  accepted.elements.get('preferred').value = 'email';
  accepted.elements.get('automated-email-consent').checked = true;
  await accepted.submit();
  const retained = JSON.parse(accepted.store.values.get(PENDING));
  assert.equal(retained.acceptedCorrespondenceVersion, 'ctos.onboarding-correspondence.v2');
  assert.equal(retained.consentToAutomatedEmail, true);
});

test('a legacy or declined checkout cannot gain automated-email consent on retry', async () => {
  const old = await formHarness({ dropResponse: true });
  old.elements.get('preferred').value = 'email';
  old.elements.get('automated-email-consent').checked = false;
  await old.submit();
  old.elements.get('automated-email-consent').checked = true;
  await old.submit();
  assert.equal(old.posts[0].acceptedCorrespondenceVersion, undefined);
  assert.equal(old.posts[1].acceptedCorrespondenceVersion, undefined);
  const pending = JSON.parse(old.store.values.get(PENDING));
  pending.acceptedCorrespondenceVersion = 'ctos.onboarding-correspondence.v1';
  const malformed = harness(query, { [PENDING]: JSON.stringify(pending) });
  assert.throws(() => malformed.request(), /recovery/);
});

// A current checkbox must never rewrite an earlier accepted declaration.
test('original v1 automated-email consent remains v1 after the AI-reply release', () => {
  const original = {...harness(query).request(), acceptedCorrespondenceVersion:'ctos.onboarding-correspondence.v1', consentToAutomatedEmail:true};
  const h=harness(query,{[PENDING]:JSON.stringify(original)});
  assert.equal(h.request().acceptedCorrespondenceVersion,'ctos.onboarding-correspondence.v1');
  assert.equal(h.issued,0);
});
