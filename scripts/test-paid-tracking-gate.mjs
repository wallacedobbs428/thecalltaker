import assert from 'node:assert/strict';
import fs from 'node:fs';
for (const page of ['website/index.html', 'website/pricing.html', 'website/card-checkout.html', 'website/setup.html']) {
  const text = fs.readFileSync(page, 'utf8');
  assert.doesNotMatch(text, /connect\.facebook\.net|tracking\.thecalltaker\.com|AW-17970510102|fbq\(['"]track|gtag\(['"]event['"],\s*['"]conversion/i, `${page} must not emit paid conversion tracking`);
}
console.log('paid tracking gate: PASS');
