// Explicit isolated browser acceptance. Uses an already-installed Playwright
// module and fresh browser context, never an owner's profile or cookies.
// Configuration actions below use the labeled synthetic UI fixture, NOT DB proof.
const assert = require('node:assert/strict');
const {createServer} = require('node:http');
const {readFileSync} = require('node:fs');
const {resolve, extname, join} = require('node:path');
const {spawn} = require('node:child_process');
if (process.env.CTOS_ISOLATED_BROWSER_FIXTURE !== 'true' || !process.env.PLAYWRIGHT_MODULE) throw Error('explicit_isolated_browser_runtime_required');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE);
const site = resolve(__dirname, '..');
const fixture = spawn(process.execPath, [join(__dirname, 'customer-configuration.browser.js')], {env: {...process.env, CTOS_ISOLATED_BROWSER_FIXTURE:'true'}, stdio:['ignore','pipe','pipe']});
let browser;
const server = createServer((req,res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const file = resolve(site, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!file.startsWith(site + '/')) { res.writeHead(403);res.end();return; }
    res.setHeader('Content-Type', ({'.html':'text/html','.js':'application/javascript','.css':'text/css','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml'})[extname(file)] || 'application/octet-stream');
    res.end(readFileSync(file));
  } catch (_) { res.writeHead(404);res.end(); }
});
(async () => {
  await new Promise((resolveReady,reject) => {
    fixture.stdout.once('data', resolveReady);fixture.once('error',reject);
    fixture.once('exit', code=>reject(Error('isolated_fixture_unavailable:' + code)));
  });
  await new Promise(resolveReady=>server.listen(0,'127.0.0.1',resolveReady));
  const origin = 'http://127.0.0.1:' + server.address().port, fixtureOrigin = 'http://127.0.0.1:56789';
  browser = await chromium.launch({headless:true});
  const results = [];
  for (const width of [390,1280]) {
    const context = await browser.newContext({viewport:{width,height:844},isMobile:width===390,deviceScaleFactor:1});
    let deniedExternalRequests = 0;
    await context.route('**/*', route => {
      if ([origin,fixtureOrigin].includes(new URL(route.request().url()).origin)) return route.continue();
      deniedExternalRequests++;return route.abort();
    });
    const page = await context.newPage();
    await page.goto(origin + '/pricing.html',{waitUntil:'networkidle'});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'pricing overflow');
    assert.match(await page.getByText('Your trial follows the Square enrollment schedule.',{exact:false}).innerText(), /Setup and launch do not restart it/);
    if (width===390 && process.env.CTOS_SCREENSHOT_DIR) await page.screenshot({path:join(process.env.CTOS_SCREENSHOT_DIR,'ctos-pricing-mobile.png'),fullPage:true});
    await page.getByRole('link',{name:'Read the service and billing terms',exact:true}).click();await page.waitForURL('**/terms.html');
    await page.goto(origin + '/');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'homepage overflow');
    if (width===390 && process.env.CTOS_SCREENSHOT_DIR) await page.screenshot({path:join(process.env.CTOS_SCREENSHOT_DIR,'ctos-homepage-mobile.png')});
    await page.goto(fixtureOrigin);
    await page.getByRole('button',{name:'Check current configuration',exact:true}).click();
    await page.getByRole('checkbox').check();
    for (const title of ['Authorize this configuration','Authorize ongoing service','Confirm my forwarding setup']) await page.getByRole('button',{name:title,exact:true}).click();
    assert.match(await page.locator('[role=status]').first().innerText(), /Service permitted now: not proven or held/);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'configuration overflow');
    const evidence = await (await page.request.get(fixtureOrigin+'/fixture-state')).json();
    assert.equal(evidence.providerActions,0);
    if (width===390 && process.env.CTOS_SCREENSHOT_DIR) await page.screenshot({path:join(process.env.CTOS_SCREENSHOT_DIR,'ctos-configuration-mobile.png'),fullPage:true});
    results.push({width,overflow:false,termsLink:true,configurationInteractions:'PASS_SYNTHETIC_UI_ONLY',deniedExternalRequests,providerActions:0});
    await context.close();
  }
  console.log(JSON.stringify({results,liveFormsSubmitted:0,databaseProof:false,ownerBrowserProfileUsed:false}));
})().catch(error=>{console.error(error.message);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();server.close();fixture.kill('SIGTERM');});
