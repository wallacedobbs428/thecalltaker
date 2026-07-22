const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const site = path.resolve(__dirname, '..');
const source = (file) => fs.readFileSync(path.join(site, file), 'utf8');
const read = (file) => source(file).replace(/<[^>]*>/g, ' ').replace(/&[^;]+;/g, ' ').replace(/\s+/g, ' ');
const privacy = read('privacy.html');
const terms = read('terms.html');
const checkout = read('card-checkout.html');
const setup = read('setup.html');

for (const text of [privacy, terms]) {
  assert.match(text, /does not by itself consent to marketing SMS\/MMS/);
  assert.match(text, /Consent is not a condition of purchase/);
  assert.match(text, /Reply STOP to cancel and HELP for help/);
}
assert.match(source('privacy.html'), /The rule in &sect;2a controls all SMS\/MMS messages/);
assert.match(privacy, /separate opt-in/);
assert.match(terms, /separate, clear opt-in/);
assert.match(privacy, /Effective: July 22, 2026/);
assert.match(terms, /Effective: July 22, 2026/);
assert.doesNotMatch(checkout, /marketing SMS\/MMS/i, 'Checkout must not imply marketing-SMS enrollment.');
assert.doesNotMatch(setup, /marketing SMS\/MMS/i, 'Setup must not imply marketing-SMS enrollment.');
console.log('legal SMS consistency: PASS');
