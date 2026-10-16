// Isolated UI fixture. Synthetic readbacks only, not application/DB proof.
const {createServer}=require('node:http');
const {readFileSync}=require('node:fs');
const {join}=require('node:path');
if(process.env.CTOS_ISOLATED_BROWSER_FIXTURE!=='true')throw Error('isolated_fixture_required');
const context={checkoutAttemptId:'10000000-0000-4000-8000-000000000001',correlationId:'10000000-0000-4000-8000-000000000002',sessionId:'10000000-0000-4000-8000-000000000003',apiOrigin:'https://call-taker-os.vercel.app',continuationToken:'l4sc1_'+'a'.repeat(43),expiresAt:new Date(Date.now()+3600000).toISOString()};
const current={config_id:'10000000-0000-4000-8000-000000000004',version:2,configuration_sha256:'a'.repeat(64),provider:'retell',resource_id:'isolated-agent',resource_version:7,response_id:'isolated-llm',response_version:4,provider_number:'+12025550199',activation_state:'NOT_ACTIVATED',consent_recorded:false,service_authorized:false,forwarding_confirmed:false,
configuration:{setup:{business_name:'Isolated Repairs',days_open:['Monday'],open_time:'09:00 AM',close_time:'05:00 PM',time_zone:'America/Chicago',service_area:'Synthetic fixture'},operations:{greeting:'How can I help with your call?',intake_fields:['name','callback','request'],qualification_rules:['Record requests only'],escalation_rules:['Business reviews callbacks'],notification_destinations:['owner@example.invalid'],prohibited_promises:['No emergency dispatch or guaranteed booking'],forwarding_expectation:'CUSTOMER_MANAGED_NOT_APPLIED'}}};
const events=[];
const server=createServer(async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(req.url==='/'){
    res.setHeader('Content-Type','text/html');
    res.end('<!doctype html><html><head><title>Isolated customer configuration review</title><style>body{font:16px system-ui;max-width:750px;margin:24px auto;padding:15px}button{padding:12px;margin:8px 4px}dt{font-weight:bold;margin-top:12px}dd{margin-left:0}p{line-height:1.5}</style></head><body><p>ISOLATED UI FIXTURE. No provider or production access.</p><main id="review"></main><script src="/review.js"></script><script>TCTCustomerConfigurationReview.mount(document.getElementById("review"),'+JSON.stringify(context)+',{fetchImpl:(url,options)=>{if(url!=="https://call-taker-os.vercel.app/api/public/provisioning-configuration")throw Error("unexpected_network");return fetch("/fixture-api",options);}});</script></body></html>');return;
  }
  if(req.url==='/review.js'){res.setHeader('Content-Type','application/javascript');res.end(readFileSync(join(__dirname,'../onboarding/configuration-review.js')));return;}
  res.setHeader('Content-Type','application/json');
  if(req.url==='/fixture-state'){res.end(JSON.stringify({events,providerActions:0}));return;}
  if(req.url!=='/fixture-api'||req.method!=='POST'){res.writeHead(404);res.end('{}');return;}
  let raw='';for await(const c of req){raw+=c;if(raw.length>4096){res.writeHead(413);res.end('{}');return;}}
  const b=JSON.parse(raw);if(b.continuationToken!==context.continuationToken){res.writeHead(403);res.end('{}');return;}
  events.push(b.action);
  if(b.action==='current'){res.end(JSON.stringify(current));return;}
  if(b.configId!==current.config_id){res.writeHead(409);res.end('{}');return;}
  const field={consent:'consent_recorded',authorize_service:'service_authorized',confirm_forwarding:'forwarding_confirmed'}[b.action];
  if(!field){res.writeHead(400);res.end('{}');return;}
  current[field]=true;res.end(JSON.stringify({outcome:'RECORDED'}));
});
server.listen(56789,'127.0.0.1',()=>console.log(JSON.stringify({isolatedUrl:'http://127.0.0.1:56789',realProviderRequests:0})));
