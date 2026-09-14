const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
const read = f => fs.readFileSync(path.join(root, f), 'utf8');
const pages = ['index.html','pricing.html','faq.html','demo.html','meet-gideon.html','ai-receptionist/index.html','after-hours-answering-service/index.html'];
test('public pages use one exact menu contract without duplicate demo or unavailable channels', () => {
  const template = read('website/shared/site-menu.html').trim();
  for (const page of pages) {
    const html = read('website/' + page);
    assert.ok(html.includes(template), page + ': menu must match shared template');
    assert.equal((html.match(/id="tctSiteMenu"/g) || []).length, 1);
    assert.ok(html.includes('href="/site-menu.css"'));
    assert.ok(html.includes('src="/site-menu.js"'));
    assert.ok(html.includes('src="/call-demo.js"'));
  }
  assert.equal((template.match(/data-call-demo/g) || []).length, 1);
  assert.doesNotMatch(template, /text-us|verification in progress|sms:|lead_capture_open/);
  assert.match(template, /<summary aria-label="Menu">/);
  assert.match(template, /href="\/#features"/);
});
test('menu closes on Escape, outside click and selection; opaque style and deploy assets stay aligned', () => {
  const js = read('website/site-menu.js');
  assert.match(js, /event.key === 'Escape'/);
  assert.match(js, /!menu.contains\(event.target\)/);
  assert.match(js, /summary.focus\(\)/);
  assert.match(read('website/site-menu.css'), /background:#f7f6f2/);
  const deploy = read('.github/workflows/deploy.yml');
  for (const asset of ['site-menu.css','site-menu.js']) {
    assert.ok(deploy.includes(asset));
    assert.ok(deploy.includes('test -f "$CLEAN/' + asset + '"'));
  }
});
