const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const page = name => readFileSync(join(__dirname, '..', name), 'utf8');

test('buyers can distinguish call capture from the business decision and plan coverage', () => {
  assert.match(page('index.html'), /Choose after-hours or broader call coverage/);
  const pricing = page('pricing.html');
  assert.match(pricing, /approved greeting, collects the caller's name, callback number, and reason for calling/);
  assert.match(pricing, /Your team decides the next step/);
  assert.match(pricing, /Included minutes and overage rates are not listed here/);
  assert.match(pricing, /Tool connections require feasibility review and an agreed scope/);
  assert.match(pricing, /No unlisted overage or custom-scope charge is added without disclosure and agreement/);
});

test('public offer keeps the existing card, trial, renewal, and separate custom quote boundaries', () => {
  const pricing = page('pricing.html');
  assert.match(pricing, /Card required/);
  for (const price of [97, 497]) assert.ok(pricing.includes(`$0 today for 14 days; then $${price}/month`));
  assert.ok(pricing.includes('$0 today for 14 days; then $997 base/month; custom scope quoted separately'));
  assert.match(pricing, /canceled before renewal/);
  assert.match(page('terms.html'), /No unlisted overage or custom-scope charge is added without disclosure and agreement/);
});

test('clarity copy preserves verified billing and human-reviewed launch rather than promising activation', () => {
  const pricing = page('pricing.html');
  assert.match(pricing, /verified signed Square confirmation/);
  assert.match(pricing, /submission or redirect alone does not confirm enrollment or activate call handling/);
  assert.match(pricing, /call flow, forwarding, notification path, and test calls with you before launch/);
  assert.match(pricing, /href="\/terms\.html"/);
  for (const plan of ['afterhours', 'full247', 'custom']) {
    assert.ok(pricing.includes(`/card-checkout.html?plan=${plan}`));
    assert.ok(pricing.includes(`data-tct-plan="${plan}"`));
  }
});
