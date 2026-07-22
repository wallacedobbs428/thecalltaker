import assert from 'node:assert/strict';

const pages = {
  terms: 'https://thecalltaker.com/terms.html',
  privacy: 'https://thecalltaker.com/privacy.html',
  home: 'https://thecalltaker.com/',
  pricing: 'https://thecalltaker.com/pricing.html',
  checkout: 'https://thecalltaker.com/card-checkout.html',
  setup: 'https://thecalltaker.com/setup.html'
};
const bodies = {};
for (const [name, url] of Object.entries(pages)) {
  const response = await fetch(url, {redirect: 'error'});
  assert.equal(response.status, 200, `${name} is unavailable`);
  bodies[name] = await response.text();
}
const text = (value) => value.replace(/&sect;/g, '§').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ');
for (const phrase of ['does not by itself consent to marketing SMS/MMS', 'separate, clear opt-in', 'Consent is not a condition of purchase']) assert.ok(text(bodies.terms).includes(phrase), `Terms missing: ${phrase}`);
for (const phrase of ['does not by itself consent to marketing SMS/MMS', 'The rule in §2a controls all SMS/MMS messages', 'separate opt-in']) assert.ok(text(bodies.privacy).includes(phrase), `Privacy missing: ${phrase}`);
const tracking = /connect\.facebook\.net|tracking\.thecalltaker\.com|AW-17970510102|fbq\(['"]track|gtag\(['"]event['"],\s*['"]conversion/i;
for (const name of ['home', 'pricing', 'checkout', 'setup']) assert.doesNotMatch(bodies[name], tracking, `${name} emits held paid tracking`);
for (const name of ['checkout', 'setup']) assert.doesNotMatch(bodies[name], /marketing SMS\/MMS/i, `${name} implies marketing-SMS enrollment`);
console.log('live Lane 6 control cycle: PASS');
