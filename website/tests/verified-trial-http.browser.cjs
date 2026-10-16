// Called only by the isolated real-handler/SQL acceptance runner. The fixture
// owns synthetic enrollment/provider boundaries and supplies a body-only
// customer capability. This driver never reads owner credentials or profiles.
const assert = require('node:assert/strict');
const {createServer} = require('node:http');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
exports.run = async function run(fixture) {
  if (!/^ctos_owner_away_integration_[a-f0-9]+$/.test(process.env.CTOS_BUYER_TEST_DATABASE || '') || !process.env.PLAYWRIGHT_MODULE) throw Error('isolated_real_database_runtime_required');
  assert.equal(typeof fixture.handle, 'function');assert.equal(typeof fixture.readback, 'function');
  const {chromium} = require(process.env.PLAYWRIGHT_MODULE), context = fixture.context;
  const expectedOrigin = context.apiOrigin === 'https://call-taker-square-sandbox.vercel.app'
    ? 'https://call-taker-square-sandbox-checkout.vercel.app' : 'https://thecalltaker.com';
  const requests = [], denied = [];let browser;
  const server = createServer(async (req,res) => {
    res.setHeader('Cache-Control','no-store');
    try {
      if (req.url === '/' && req.method === 'GET') {
        res.setHeader('Content-Type','text/html');
        const safeContext = JSON.stringify(context).replace(/</g,'\\u003c');
        res.end('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Isolated verified trial review</title><style>body{font:16px system-ui;max-width:750px;margin:24px auto;padding:15px}button{padding:12px;margin:8px 4px}dd{margin-left:0}p{line-height:1.5}</style></head><body><p>ISOLATED real application-handler and database acceptance. No live providers.</p><main id="review"></main><script src="/review.js"></script><script>TCTCustomerConfigurationReview.mount(document.getElementById("review"),'+safeContext+',{fetchImpl:(url,options)=>{if(url!=='+JSON.stringify(context.apiOrigin+'/api/public/provisioning-configuration')+')throw Error("unexpected_network");return fetch("/api/public/provisioning-configuration",options);}});</script></body></html>');return;
      }
      if (req.url === '/review.js' && req.method === 'GET') {res.setHeader('Content-Type','application/javascript');res.end(readFileSync(join(__dirname,'../onboarding/configuration-review.js')));return;}
      if (req.url !== '/api/public/provisioning-configuration' || req.method !== 'POST') {res.writeHead(404);res.end();return;}
      let body='';for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>4096){res.writeHead(413);res.end();return;}}
      requests.push(JSON.parse(body).action);
      const response=await fixture.handle(new Request(context.apiOrigin+req.url,{method:'POST',headers:{origin:expectedOrigin,'content-type':'application/json','x-forwarded-for':'192.0.2.212'},body}));
      res.writeHead(response.status,{'Content-Type':'application/json'});res.end(await response.text());
    } catch (_) {res.writeHead(503,{'Content-Type':'application/json'});res.end('{"error":"isolated_handler_failed"}');}
  });
  try {
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const origin='http://127.0.0.1:'+server.address().port;
    browser=await chromium.launch({headless:true});
    const isolated=await browser.newContext({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});
    await isolated.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();denied.push('external_denied');return route.abort();});
    const page=await isolated.newPage();await page.goto(origin);
    await page.getByRole('button',{name:'Check current configuration',exact:true}).click();
    await page.getByText('Verified card-backed trial enrollment, not a payment receipt.',{exact:true}).waitFor();
    await page.getByRole('checkbox').check();
    for(const title of ['Authorize this configuration','Authorize ongoing service','Confirm my forwarding setup']){
      await page.getByRole('button',{name:title,exact:true}).click();
      await page.waitForFunction(label=>Array.from(document.querySelectorAll('button')).some(button=>button.textContent===label&&button.disabled===false),title);
    }
    await page.getByText(/Your exact decision was recorded and independently read back/).waitFor();
    assert.equal(await page.getByRole('heading',{name:'Service active',exact:true}).count(),0,'customer decisions alone cannot activate service');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    assert.deepEqual(requests,['current','consent','current','authorize_service','current','confirm_forwarding','current']);
    const proof=await fixture.readback();
    assert.equal(proof.admission_basis,'VERIFIED_TRIAL');assert.equal(proof.payment_receipts,0);
    assert.equal(proof.configuration_id,fixture.configId);
    assert.equal(proof.customer_resource_decisions,1);assert.equal(proof.customer_service_decisions,1);assert.equal(proof.customer_forwarding_decisions,1);
    assert.notEqual(proof.activation_state,'ACTIVATED','browser permissions do not replace controlled tests and internal launch authority');
    if(process.env.CTOS_SCREENSHOT_DIR)await page.screenshot({path:join(process.env.CTOS_SCREENSHOT_DIR,'ctos-verified-trial-real-http-mobile.png'),fullPage:true});
    console.log(JSON.stringify({kind:'verified_trial_browser_http',viewport:'390x844',actualHandlerRequests:requests.length,independentDatabaseReadback:proof,externalRequests:denied.length,ownerProfileUsed:false,serviceActivationClaimed:false}));
  } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
};
