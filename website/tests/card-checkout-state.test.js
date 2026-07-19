const assert = require('node:assert/strict');
const test = require('node:test');
const checkout = require('../card-checkout-state.js');

const validIdentity = {
  givenName: 'Test',
  familyName: 'Buyer',
  email: 'buyer@example.com',
  phone: '(629) 269-9697',
  cardholderName: 'Test Buyer'
};
const validCardFields = {cardNumber:true,expirationDate:true,cvv:true};

test('checkout remains disabled until every identity, consent, mount, and card gate passes', () => {
  const ready = {cardMounted:true,cardFields:validCardFields,identity:validIdentity,consent:true,submitting:false};
  assert.equal(checkout.checkoutReady(ready), true);
  assert.equal(checkout.checkoutReady({...ready,cardMounted:false}), false);
  assert.equal(checkout.checkoutReady({...ready,cardFields:{...validCardFields,cvv:false}}), false);
  assert.equal(checkout.checkoutReady({...ready,identity:{...validIdentity,email:'invalid'}}), false);
  assert.equal(checkout.checkoutReady({...ready,identity:{...validIdentity,phone:'629-269'}}), false);
  assert.equal(checkout.checkoutReady({...ready,consent:false}), false);
  assert.equal(checkout.checkoutReady({...ready,submitting:true}), false);
});

test('Square field events independently establish and revoke complete card validity', () => {
  let fields = {};
  for (const field of checkout.REQUIRED_CARD_FIELDS) {
    fields = checkout.recordCardEvent(fields, {detail:{field,currentState:{isCompletelyValid:true}}});
  }
  assert.equal(checkout.cardReady(fields), true);
  fields = checkout.recordCardEvent(fields, {field:'cvv',currentState:{isCompletelyValid:false}});
  assert.equal(checkout.cardReady(fields), false);
});

test('the checkout page loads the gate and exposes reachable legal links', () => {
  const fs = require('node:fs');
  const html = fs.readFileSync(new URL('../card-checkout.html', `file://${__dirname}/`), 'utf8');
  const workflow = fs.readFileSync(new URL('../../.github/workflows/deploy.yml', `file://${__dirname}/`), 'utf8');
  assert.match(html, /<script src="\/card-checkout-state\.js"><\/script>/);
  assert.match(html, /href="\/terms\.html"/);
  assert.match(html, /href="\/privacy\.html"/);
  assert.match(html, /TCTCheckoutState\.checkoutReady/);
  assert.doesNotMatch(html, /card\.attach\('#square-card'\);button\.disabled=false/);
  assert.match(workflow, /card-checkout\.html card-checkout-state\.js signup\.html/);
});
