const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=f=>fs.readFileSync(path.join(__dirname,'../website',f),'utf8');
test('call demo links open the shared number popup with a direct-page fallback',()=>{
 const home=read('index.html'), js=read('call-demo.js'), demo=read('demo.html');
 assert.ok((home.match(/data-call-demo/g)||[]).length>=10);
 assert.ok(home.includes('href="/demo.html#call-demo"'));
 assert.ok(js.includes('href="tel:+16292699697"'));
 assert.ok(demo.includes('href="tel:+16292699697"'));
 assert.ok(js.includes('cta_intent'));
 assert.ok(js.includes('live_demo_phone'));
 assert.doesNotMatch(home, /Request a human demo/);
 assert.doesNotMatch(demo, /<form|<input/);
 assert.doesNotMatch(js, /getUserMedia|AudioContext|MediaRecorder/);
});
