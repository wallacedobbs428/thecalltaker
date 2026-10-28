const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {calculate}=require('../website/missed-call-worksheet');
const base={missed:30,answered:60,qualified:50,closed:25,contribution:200,cost:97};
test('contribution scenario applies qualification, conversion and actual cost without promising a return',()=>{
 assert.deepEqual(calculate(base),{jobs:2.25,beforeCost:450,afterCost:353});
 assert.deepEqual(calculate({...base,closed:0}),{jobs:0,beforeCost:0,afterCost:-97});
 for(const invalid of [NaN,Infinity,-1,101])assert.equal(calculate({...base,answered:invalid}),null);
 assert.equal(calculate({...base,cost:Infinity}),null);
 assert.equal(calculate({...base,missed:'30'}),null);
});
test('new general resources have canonical links, accurate public identity, menu, and deploy coverage',()=>{
 const read=f=>fs.readFileSync(path.join(__dirname,'../',f),'utf8');
 const deploy=read('.github/workflows/deploy.yml'),sitemap=read('website/sitemap.xml'),menu=read('website/shared/site-menu.html').trim();
 for(const file of ['about.html','resources.html','answering-service-comparison.html','call-handling-guide.html','call-flow-example.html']){
  const html=read('website/'+file);assert.ok(html.includes(menu),file);
  assert.ok(html.includes('rel="canonical" href="https://thecalltaker.com/'+file+'"'),file);
  assert.ok(sitemap.includes('https://thecalltaker.com/'+file));assert.ok(deploy.includes(file));
  assert.ok(html.includes('thecalltakerservice@gmail.com'));
  for(const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)){
   const data=JSON.parse(match[1]);assert.ok(data['@graph'].find(x=>x['@type']==='Organization').logo.url);
  }
 }
 assert.match(read('website/call-flow-example.html'),/not a recording, live test, customer testimonial or measured outcome/);
 assert.doesNotMatch(read('website/missed-call-worksheet.js'),/fetch\(|sendBeacon|localStorage|sessionStorage/);
});
