(function(root){
 'use strict';
 var API='https://ctos.thecalltaker.com/api/public/demo-evaluation';
 var UUID=/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
 function init(){
  var panel=document.getElementById('browser-evaluation');if(!panel)return;
  var access=null,call=null,busy=false;
  var status=panel.querySelector('[data-status]'),result=panel.querySelector('[data-result]');
  var connect=panel.querySelector('[data-connect]'),start=panel.querySelector('[data-start]'),end=panel.querySelector('[data-end]'),refresh=panel.querySelector('[data-refresh]'),next=panel.querySelector('[data-next]');
  function say(message){status.textContent=message;}
  async function request(action){
   if(!access)throw Error('Enter the protected evaluation access supplied to you.');
   var response=await root.fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},credentials:'omit',redirect:'error',cache:'no-store',referrerPolicy:'no-referrer',signal:AbortSignal.timeout(10000),body:JSON.stringify({action:action,prospectId:access.prospectId,capability:access.capability,...(action==='start'?{disclosureAccepted:panel.querySelector('[data-disclosure]').checked}:{})})});
   var value=await response.json();if(!response.ok)throw Error(value.error==='evaluation_submission_unknown_no_retry'?'The provider outcome is uncertain. Do not start another session. The original request needs reconciliation.':value.error==='evaluation_live_usage_held'?'Live evaluation is held. No session was started.':value.error==='evaluation_persistence_or_access_unavailable'?'Access or durable storage is unavailable. No new session is confirmed.':'The request could not complete. Review the original result before trying again.');return value;
  }
  function show(value){
   panel.querySelector('[data-business]').textContent=value.business_name||'Protected business evaluation';result.replaceChildren();
   panel.querySelector('[data-scope]').textContent='One approved session, maximum '+Math.round(Number(value.duration_ms)/1000)+' seconds. The provider force-ends at the limit. Access expires '+new Date(value.expires_at).toLocaleString()+'. Ending access does not retract an already-issued provider token or stop an active session.';
   if(value.intake){['name','callback','reason','business_decision'].forEach(function(key){var p=document.createElement('p');p.textContent=key.replaceAll('_',' ')+': '+(typeof value.intake[key]==='string'?value.intake[key]:'Not captured or not yet verified');result.appendChild(p);});}
   else result.textContent='No analyzed intake is available. An ended session alone is not a useful conversation.';
   next.disabled=!value.analyzed_at;start.disabled=!!value.session_id&&value.state!=='PRE_REQUEST_FAILED';
   say(value.state?'Recorded session state: '+value.state+'.':'Access verified. No session has started.');
  }
  async function once(work){if(busy)return;busy=true;try{await work();}catch(error){say(error.message||'Evaluation unavailable.');}finally{busy=false;}}
  connect.addEventListener('click',function(){once(async function(){
   var parts=panel.querySelector('[data-capability]').value.trim().split('.'),prospectId=parts[0],capability=parts[1];
   if(parts.length!==2||!UUID.test(prospectId)||!/^demo1_[A-Za-z0-9_-]{43}$/.test(capability))throw Error('Enter the protected evaluation access code supplied to you.');
   access={prospectId:prospectId,capability:capability};
   // Memory only: no token in URL, analytics, cookie or browser storage.
   panel.querySelector('[data-capability]').value='';show(await request('read'));refresh.disabled=false;
  });});
  start.addEventListener('click',function(){once(async function(){
   if(!panel.querySelector('[data-disclosure]').checked)throw Error('Read and accept the demonstration scope first.');
   if(call&&call.status!=='ended')return;
   if(!root.navigator.mediaDevices)throw Error('Microphone access requires a supported secure browser.');
   var microphone;try{microphone=await root.navigator.mediaDevices.getUserMedia({audio:true});}catch(_){throw Error('Microphone permission was denied. No provider session was requested.');}
   microphone.getTracks().forEach(function(track){track.stop();});
   var sdk=await import('./demo-voice-sdk.mjs');
   var client=new sdk.RetellClient({key:'ctos-scoped-backend-only',fetch:async function(url,options){
    if(new URL(String(url),'https://api.retellai.com').pathname!=='/v3/create-web-call'||String(options.method).toUpperCase()!=='POST')throw Error('Unsupported provider operation.');
    var value=await request('start');show(value);
    if(!value.connection)throw Error('The original session already exists. Review it; do not create a replacement.');
    return new Response(JSON.stringify(value.connection),{status:201,headers:{'Content-Type':'application/json'}});
   }});
   call=client.createWebCall({agent_id:'server-bound-demo-only',transcript:false,hooks:{onStatus:function(value){say('Browser connection: '+value+'. Canonical outcome is verified separately.');},onEnd:function(){end.disabled=true;say('Browser session ended. Refresh to inspect the provider-verified intake.');},onError:function(){end.disabled=true;say('Connection failed or was interrupted. Refresh the original session; do not start another.');}}});
   start.disabled=true;end.disabled=false;
  });});
  end.addEventListener('click',function(){once(async function(){if(call)await call.end();end.disabled=true;});});
  refresh.addEventListener('click',function(){once(async function(){show(await request('refresh'));});});
  next.addEventListener('click',function(){once(async function(){var value=await request('next_step');if(!value.task_id)throw Error('A sales review was not durably accepted.');say('Your requirements-review request is recorded with the sales owner. No appointment, subscription or live coverage was created.');next.disabled=true;});});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(window);
