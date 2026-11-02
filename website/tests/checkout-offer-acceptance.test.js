const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const html = readFileSync(require.resolve('../card-checkout.html'), 'utf8');
test('actual new checkout POST binds the displayed approved offer version without activating proposed entitlements', () => {
  const helper = html.match(/function offeredCheckoutVersion\(planKey\) \{[\s\S]*?\n      \}/)[0];
  const version = runInNewContext(helper + ';offeredCheckoutVersion("afterhours")');
  assert.equal(version, 'ctos.standard-service-offer.self-service.v2');
  assert.equal(runInNewContext(helper + ';offeredCheckoutVersion("custom")'), 'ctos.standard-service-offer.v1');
  const expression = html.match(/body:JSON\.stringify\((\{ plan:key, sourceId:token\.token,[^\n]+? website:'' \})\)/)[1];
  const body = runInNewContext('(' + expression + ')', {key:'afterhours',token:{token:'synthetic-card-token'},requestIdentity:{idempotencyKey:'synthetic-request',correlationId:'synthetic-correlation',sessionId:'synthetic-session',acceptedOfferVersion:version},form:{dataset:{offerVersion:version}},attribution:()=>({source:'isolated-test'}),fields:Array.from({length:7},()=>({value:'synthetic'})),billingPostalCode:'37027'});
  assert.equal(body.acceptedOfferVersion, version);
  assert.equal(body.consentToStoreCard, true);
  assert.equal(body.trialMinutes, undefined);
  assert.equal(body.billingConfirmed, undefined);
  assert.equal(body.clientActive, undefined);
  assert.ok(!version.includes('proposal'));
});
