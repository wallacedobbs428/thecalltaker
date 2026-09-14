const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../website/card-checkout.html'),'utf8');
test('checkout shares the public ivory and emerald identity with motion opt-out',()=>{
  assert.match(html,/color-scheme:light/);
  assert.match(html,/--bg:#f7f6f2/);
  assert.match(html,/--green:#287251/);
  assert.match(html,/animation:none!important/);
  assert.match(html,/input,select \{ font-size:16px; min-height:54px; \}/);
  assert.match(html,/The Call<span>Taker<\/span>/);
});
