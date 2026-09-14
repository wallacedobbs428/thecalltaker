const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(require('node:path').join(__dirname, '../website/pricing.html'), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).find(s => s.includes('var plans ='));

for (const reduced of [false, true]) test(`plan buttons and image navigate to exact card; reduced motion=${reduced}`, () => {
  const keys = ['afterhours', 'full247', 'custom'];
  const nodes = {};
  function node(attrs = {}) { return {attrs, handlers:{}, style:{}, classList:{add(){},remove(){}},
    setAttribute(k,v){this.attrs[k]=v;}, getAttribute(k){return this.attrs[k];},
    addEventListener(k,f){this.handlers[k]=f;}, focus(options){this.focused=options;},
    scrollIntoView(options){this.scrolled=options;} }; }
  for (const id of ['pricingPlanTag','pricingPlanHeadline','pricingPlanCopy','pricingPlanImage','pricingPlanVisual',...keys.map(k=>'plan-'+k)]) nodes[id]=node();
  nodes.pricingPlanVisual.attrs.href='#plan-afterhours';
  const buttons=keys.map(k=>node({'data-plan-visual':k}));
  vm.runInNewContext(script, {document:{getElementById:id=>nodes[id],querySelectorAll:s=>s==='.plan-switch-option'?buttons:[]},window:{matchMedia:()=>({matches:reduced}),setTimeout:f=>f()}});
  keys.forEach((key,i)=>{
    assert.match(html,new RegExp('id="plan-'+key+'" tabindex="-1"'));
    buttons[i].handlers.click();
    assert.equal(nodes['plan-'+key].scrolled.behavior,reduced?'instant':'smooth');
    assert.equal(nodes['plan-'+key].focused.preventScroll,true);
    assert.equal(nodes.pricingPlanVisual.attrs.href,'#plan-'+key);
    nodes['plan-'+key].scrolled=null;
    let prevented=false;
    nodes.pricingPlanVisual.handlers.click({button:0,preventDefault(){prevented=true;}});
    assert.equal(prevented,true);
    assert.equal(nodes['plan-'+key].scrolled.block,'start');
  });
  assert.match(html,/<a class="plan-visual[^>]*href="#plan-afterhours"/);
});
