const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../onboarding/configuration-review');
const configId = '10000000-0000-4000-8000-000000000004', caseId = '10000000-0000-4000-8000-000000000005';
const context = () => ({checkoutAttemptId:'10000000-0000-4000-8000-000000000001',correlationId:'10000000-0000-4000-8000-000000000002',sessionId:'10000000-0000-4000-8000-000000000003',apiOrigin:'https://call-taker-os.vercel.app',continuationToken:'l4sc1_'+'a'.repeat(43),expiresAt:new Date(Date.now()+3600000).toISOString()});
const item = overrides => ({case_id:caseId,lifecycle_status:'provider_delivered',notification_status:'provider_delivered',receipt_status:'unconfirmed',acknowledgement_status:'not_acknowledged',follow_up_status:'not_started',next_action_owner:'ClientDelivery',next_action:'Business reviews request',...overrides});
const inventory = cases => ({configuration_id:configId,cases,coverage:'BOUNDED_COMPLETE'});
function dom() {
  const doc = {createElement:tag=>new Element(tag), createTextNode:text=>({textContent:text})};
  class Element {
    constructor(tag) { this.tagName=tag;this.ownerDocument=doc;this.children=[];this.listeners={};this.dataset={};this.value='';this.textContent=''; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children=nodes; }
    setAttribute(key,value) { this[key]=value; }
    addEventListener(type,fn) { this.listeners[type]=fn; }
    querySelectorAll(tag) { return this.children.flatMap(child=>child instanceof Element?[...(child.tagName===tag?[child]:[]),...child.querySelectorAll(tag)]:[]); }
    async click() { assert.notEqual(this.disabled,true);await this.listeners.click(); }
  }
  return new Element('main');
}
const text = node => node.textContent+(node.children||[]).map(text).join(' ');
const button = (root,title) => root.querySelectorAll('button').find(node=>node.textContent===title);

test('case API uses body-only customer binding, no case ID for bounded list, and stable write identity after lost acknowledgement',async()=>{
  const sent=[];const fetcher=async(url,options)=>{
    assert.equal(url,context().apiOrigin+'/api/public/customer-cases');assert.ok(!url.includes('l4sc1_'));
    assert.equal(options.credentials,'omit');assert.equal(options.redirect,'error');assert.equal(options.method,'POST');
    const body=JSON.parse(options.body);sent.push(body);
    return Response.json(body.action==='list'?inventory([]):{...item(),configuration_id:configId,external_actions:0});
  };
  await api.caseRequest(context(),configId,'list',null,{},fetcher);
  assert.equal(sent[0].caseId,undefined);assert.equal(sent[0].requestId,undefined);
  await api.caseRequest(context(),configId,'assign_callback',caseId,{assignedTo:'Office team'},fetcher);
  await api.caseRequest(context(),configId,'assign_callback',caseId,{assignedTo:'Office team'},fetcher);
  assert.equal(sent[1].requestId,sent[2].requestId);
  await api.caseRequest(context(),configId,'assign_callback',caseId,{assignedTo:'Different team'},fetcher);
  assert.notEqual(sent[1].requestId,sent[3].requestId);
  assert.equal(sent[1].continuationToken,context().continuationToken);
  assert.equal(sent[1].owner_user_id,undefined);
});
test('expired access, invalid IDs, unsupported intent and oversized UTF-8 notes make no request',async()=>{
  let calls=0;const fetcher=async()=>{calls++;throw Error('no');};
  await assert.rejects(api.caseRequest({...context(),expiresAt:new Date(0).toISOString()},configId,'list',null,{},fetcher));
  await assert.rejects(api.caseRequest(context(),configId,'send',caseId,{},fetcher));
  await assert.rejects(api.caseRequest(context(),configId,'read','wrong',{},fetcher));
  await assert.rejects(api.caseRequest(context(),configId,'unresolved',caseId,{note:'é'.repeat(501)},fetcher));
  await assert.rejects(api.caseRequest(context(),configId,'assign_callback',caseId,{assignedTo:'x'},fetcher));
  await assert.rejects(api.caseRequest(context(),configId,'resolve',caseId,{outcome:'revenue_recovered'},fetcher));
  assert.equal(calls,0);
});
test('foreign or over-cap inventory fails closed rather than showing empty or another customer',async()=>{
  for(const value of [{...inventory([]),configuration_id:caseId},inventory(Array.from({length:21},()=>item())),inventory([{case_id:'bad'}])]) {
    await assert.rejects(api.caseRequest(context(),configId,'list',null,{},async()=>Response.json(value)));
  }
});
test('customer sees captured request and explicit seen action performs write then independent read and list, never contact',async()=>{
  const root=dom(),events=[];let seen=false;
  const fetcher=async(_url,options)=>{const body=JSON.parse(options.body);events.push(body.action);
    if(body.action==='receipt_seen')seen=true;
    const current=item({receipt_status:seen?'confirmed_seen':'unconfirmed'});
    return Response.json(body.action==='list'?inventory([current]):{...current,configuration_id:configId,external_actions:0});};
  api.mountCases(root,context(),configId,fetcher);
  assert.deepEqual(events,[]);await button(root,'Check customer requests').click();
  assert.match(text(root),/Request 10000000/);assert.match(text(root),/Notification status: provider_delivered/);
  assert.equal(button(root,'Acknowledge this request'),undefined);
  await button(root,'I have seen this request').click();
  assert.deepEqual(events,['list','receipt_seen','read','list']);
  assert.ok(button(root,'Acknowledge this request'));assert.match(text(root),/No caller was contacted/);
});
test('unverified write readback hides actions until a fresh reconciliation, without automatic replay',async()=>{
  const root=dom(),events=[];
  const fetcher=async(_url,options)=>{const action=JSON.parse(options.body).action;events.push(action);
    return Response.json(action==='list'?inventory([item()]):{...item(),configuration_id:configId,external_actions:0});};
  api.mountCases(root,context(),configId,fetcher);await button(root,'Check customer requests').click();await button(root,'I have seen this request').click();
  assert.deepEqual(events,['list','receipt_seen','read']);assert.equal(button(root,'I have seen this request'),undefined);
  assert.match(text(root),/could not be independently verified/);
  await button(root,'Check customer requests').click();assert.deepEqual(events,['list','receipt_seen','read','list']);
});
test('callback and disposition controls follow actual reported stages; terminal cases expose no writes',async()=>{
  for(const [state,present,absent] of [
    [item({acknowledgement_status:'acknowledged',follow_up_status:'pending',next_action_owner:'customer_reported:Office'}),'I started the callback','Record disposition'],
    [item({acknowledgement_status:'acknowledged',follow_up_status:'in_progress'}),'I completed the callback','Assign callback owner'],
    [item({acknowledgement_status:'acknowledged',follow_up_status:'completed'}),'Record disposition','Assign callback owner'],
    [item({lifecycle_status:'resolved'}),null,'Report an unresolved request']]) {
    const root=dom();api.mountCases(root,context(),configId,async()=>Response.json(inventory([state])));await button(root,'Check customer requests').click();
    if(present)assert.ok(button(root,present));assert.equal(button(root,absent),undefined);
  }
});
test('request controls appear only after an exact configuration is loaded, without automatic inventory or writes',async()=>{
  const root=dom(),events=[];
  const fetcher=async(url,options)=>{events.push({url,action:JSON.parse(options.body).action});return Response.json({config_id:configId,configuration_sha256:'a'.repeat(64),version:1,configuration:{setup:{business_name:'Synthetic business'},operations:{}}});};
  const mounted=api.mount(root,context(),{fetchImpl:fetcher});assert.equal(button(root,'Check customer requests'),undefined);
  await mounted.refresh();assert.ok(button(root,'Check customer requests'));
  assert.equal(events.length,1);assert.equal(events[0].action,'current');assert.match(events[0].url,/provisioning-configuration$/);
});
test('possibly-more inventory is labeled bounded and empty inventory does not prove no calls',async()=>{
  for(const [value,expected] of [[{...inventory([item()]),coverage:'POSSIBLY_MORE'},/older requests may exist/],[inventory([]),/not proof that no calls occurred/]]) {
    const root=dom();api.mountCases(root,context(),configId,async()=>Response.json(value));await button(root,'Check customer requests').click();assert.match(text(root),expected);
  }
});
