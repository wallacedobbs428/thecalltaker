const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const demo=fs.readFileSync(path.join(__dirname,'../demo.html'),'utf8');
assert.ok(demo.includes('data-tct-event="cta_intent"'));
assert.doesNotMatch(demo, /lead_request_accepted_ui|payment_confirmed|demo_completed|<form/);
