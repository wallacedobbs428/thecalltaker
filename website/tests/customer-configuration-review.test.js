const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const api = require('../onboarding/configuration-review');
const context = () => ({checkoutAttemptId:'10000000-0000-4000-8000-000000000001',correlationId:'10000000-0000-4000-8000-000000000002',sessionId:'10000000-0000-4000-8000-000000000003',apiOrigin:'https://call-taker-os.vercel.app',continuationToken:'l4sc1_'+'a'.repeat(43),expiresAt:new Date(Date.now()+3600000).toISOString()});
const configId='10000000-0000-4000-8000-000000000004';
test('historical activation never implies current service permission after withdrawal or revocation',()=>{
  const status=api.serviceStatus({activation_state:'ACTIVATED',current_service_permitted:false,current_service_hold:'SERVICE_NOT_CURRENT_OR_AUTHORIZED'});
  assert.match(status,/Historical activation: ACTIVATED/);assert.match(status,/Service permitted now: not proven or held/);
  assert.match(status,/Hold: SERVICE_NOT_CURRENT_OR_AUTHORIZED/);
  assert.match(api.serviceStatus({activation_state:'ACTIVATED'}),/Service permitted now: not proven or held/);
  assert.match(api.serviceStatus({activation_state:'ACTIVATED',current_service_permitted:true}),/Service permitted now: yes/);
});
test('configuration actions keep exact capability in POST body only, no cookies, redirect or provider mutation',async()=>{
  let count=0;
  for(const action of ['current','consent','authorize_service','revoke_service','confirm_forwarding']) {
    const c=context();
    await api.request(c,action,configId,async(url,options)=>{
      count++;assert.equal(url,c.apiOrigin+'/api/public/provisioning-configuration');
      assert.equal(options.method,'POST');assert.equal(options.credentials,'omit');assert.equal(options.redirect,'error');
      const b=JSON.parse(options.body);assert.equal(b.continuationToken,c.continuationToken);
      assert.equal(b.checkoutAttemptId,c.checkoutAttemptId);assert.equal(b.sessionId,c.sessionId);
      assert.equal(b.configId,action==='current'?undefined:configId);
      assert.equal(b.declaration,action==='authorize_service'?api.declaration:undefined);
      assert.equal(b.owner_user_id,undefined);assert.equal(b.approved,undefined);
      return Response.json({state:'WAITING_CONFIGURATION'});
    });
  } assert.equal(count,5);
});
test('expired, foreign-origin, wrong capability and unbound actions make no request',async()=>{
  let calls=0;const fetcher=async()=>{calls++;throw Error('denied');};
  for(const bad of [{...context(),apiOrigin:'https://untrusted.invalid'}, {...context(),expiresAt:new Date(Date.now()-1).toISOString()}, {...context(),continuationToken:'invalid'}]) {
    await assert.rejects(api.request(bad,'current',null,fetcher));
  }
  await assert.rejects(api.request(context(),'consent','wrong-customer',fetcher));
  await assert.rejects(api.request(context(),'activate',configId,fetcher));
  assert.equal(calls,0);
});
test('retained access never extends expiry; expired context exposes only recovery binding, not token',()=>{
  const data=new Map(),storage={getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)};
  const c=context();assert.equal(api.remember(storage,c),true);assert.equal(api.stored(storage).expiresAt,c.expiresAt);
  c.expiresAt=new Date(Date.now()-1000).toISOString();storage.setItem(api.storageKey,JSON.stringify(c));
  assert.equal(api.stored(storage),null);assert.equal(api.remember(storage,c),false);
  const recovery=api.recovery(storage);assert.equal(recovery.sessionId,c.sessionId);assert.equal(recovery.resumeConfiguration,true);
  assert.equal(recovery.continuationToken,undefined);assert.equal(recovery.expiresAt,undefined);
});
test('current setup surface mounts consent review only after durable questionnaire receipt',()=>{
  const html=readFileSync(require.resolve('../onboarding/intake.html'),'utf8');
  assert.ok(html.indexOf('configuration-review.js')<html.indexOf('// BEGIN checkout-bound setup questionnaire'));
  assert.ok(html.indexOf("result.providerActionPerformed !== false")<html.indexOf('.remember(sessionStorage, context)',html.indexOf("result.providerActionPerformed !== false")));
  assert.match(html,/resumeConfiguration/);assert.match(html,/review\.mount\(form, savedReview\)/);
});
test('canonical release artifact includes the exact customer review script',()=>{
  const workflow=readFileSync(require.resolve('../../.github/workflows/deploy.yml'),'utf8');
  assert.ok(workflow.includes('cp -p website/onboarding/configuration-review.js "$CLEAN/onboarding/configuration-review.js"'));
  assert.ok(workflow.includes('test -f "$CLEAN/onboarding/configuration-review.js"'));
});
test('newly accepted checkout or its legitimate recovery takes priority over an older saved review',()=>{
  const html=readFileSync(require.resolve('../onboarding/intake.html'),'utf8');
  assert.match(html,/if \(savedReview && !freshContext && !freshRecovery\)/);
  assert.match(html,/if \(reviewRecovery && !freshContext && !freshRecovery\)/);
  assert.match(html,/context = freshContext;/);
  assert.match(html,/var recoveryBinding = freshRecovery;/);
});
