const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const demo=fs.readFileSync(path.join(__dirname,'../website/demo.html'),'utf8');
assert.ok(demo.includes('href="tel:+16292699697"'));
assert.ok(demo.includes('No form required'));
assert.doesNotMatch(demo, /<audio|<form|demo_preview_rendered_ui/);
assert.ok(fs.statSync(path.join(__dirname,'../website/assets/demo/demo-call-15s.mp3')).size>200000,'historical sample remains preserved, not presented as the call-in demo');
