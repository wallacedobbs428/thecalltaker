const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,'../..',p),'utf8');
test('evaluation is separate from enrollment, analytics and the retained call-in path',()=>{
 const page=read('website/demo-evaluation.html'),js=read('website/shared/demo-evaluation.js');
 assert.match(page,/does not forward your number/);assert.match(page,/not live business coverage/);assert.match(page,/enrollment-based trial/);
 assert.doesNotMatch(page,/tct-tracking|tct-funnel|googletagmanager|meta-pixel|<form|type="email"|type="tel"/);
 assert.match(page,/<meta name="referrer" content="no-referrer">/);assert.match(page,/data-capability type="password"/);
 assert.doesNotMatch(js,/localStorage|sessionStorage|history\.|location\.|innerHTML|create-phone-call|square-trial/);
 assert.match(js,/textContent/);assert.match(js,/transcript:false/);assert.match(js,/disclosureAccepted/);assert.match(js,/getUserMedia/);
 assert.match(read('website/demo.html'),/tct-tracking.js/);assert.match(read('website/demo.html'),/demo-evaluation.html/);
});
test('pinned SDK is a first-party build artifact, not an unrestricted widget',()=>{
 const pkg=JSON.parse(read('tools/demo-evaluation-sdk/package.json')),workflow=read('.github/workflows/deploy.yml');
 assert.equal(pkg.dependencies['retell-client-js-sdk'],'3.0.2');assert.match(workflow,/npm ci --ignore-scripts --prefix tools\/demo-evaluation-sdk/);
 assert.match(workflow,/demo-evaluation.html/);assert.match(workflow,/demo-voice-sdk.mjs/);assert.doesNotMatch(read('website/shared/demo-evaluation.js'),/public_key_|api_key_|transcript:true/);
});
