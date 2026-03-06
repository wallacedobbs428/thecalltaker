/* Share Demo Module — auto-injects a "Share this demo" button + toast */
(function(){
  // Determine industry from page context
  var ind = '';
  var tag = document.querySelector('.tag, .cs-card-tag, [data-industry]');
  if(tag){
    var t = (tag.getAttribute('data-industry') || tag.textContent || '').toLowerCase();
    if(t.indexOf('hvac')!==-1) ind='hvac';
    else if(t.indexOf('plumb')!==-1) ind='plumbing';
    else if(t.indexOf('locksmith')!==-1) ind='locksmith';
    else if(t.indexOf('dental')!==-1) ind='dental';
    else if(t.indexOf('legal')!==-1) ind='legal';
    else if(t.indexOf('medspa')!==-1||t.indexOf('med spa')!==-1) ind='medspa';
    else if(t.indexOf('roof')!==-1) ind='roofing';
    else if(t.indexOf('electr')!==-1) ind='electrical';
    else if(t.indexOf('tow')!==-1) ind='towing';
    else if(t.indexOf('vet')!==-1) ind='veterinary';
    else if(t.indexOf('property')!==-1) ind='property-management';
    else if(t.indexOf('garage')!==-1) ind='garage-door';
    else if(t.indexOf('funeral')!==-1) ind='funeral';
  }

  // Build share URL
  var base = window.location.origin + '/demo-showcase';
  var url = ind ? base + '?industry=' + ind + '&autoplay=1' : base + '?autoplay=1';

  // Inject CSS
  var style = document.createElement('style');
  style.textContent = '.sd-wrap{text-align:center;margin:24px 0 0}.sd-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;border:1px solid var(--border,#e5e7eb);background:var(--off-white,#f9fafb);color:var(--text-secondary,#4b5563);font-size:.8rem;font-weight:600;font-family:inherit;cursor:pointer;transition:all .2s}.sd-btn:hover{border-color:var(--orange,#ea580c);color:var(--orange,#ea580c)}.sd-btn svg{width:14px;height:14px}.sd-toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);background:#111827;color:#fff;padding:8px 20px;border-radius:8px;font-size:.82rem;font-weight:600;opacity:0;transition:all .3s ease;pointer-events:none;z-index:9999}.sd-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}';
  document.head.appendChild(style);

  // Create toast
  var toast = document.createElement('div');
  toast.className = 'sd-toast';
  toast.textContent = 'Link copied!';
  document.body.appendChild(toast);

  // Create share button
  function createBtn(){
    var wrap = document.createElement('div');
    wrap.className = 'sd-wrap';
    var btn = document.createElement('button');
    btn.className = 'sd-btn';
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Share this demo';
    btn.addEventListener('click', function(){
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(url).then(showToast).catch(fallbackCopy);
      } else {
        fallbackCopy();
      }
    });
    wrap.appendChild(btn);
    return wrap;
  }

  function fallbackCopy(){
    var ta = document.createElement('textarea');
    ta.value = url;
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    try{ document.execCommand('copy'); showToast(); } catch(e){}
    document.body.removeChild(ta);
  }

  function showToast(){
    toast.classList.add('show');
    setTimeout(function(){ toast.classList.remove('show'); }, 2000);
    if (typeof gtag === 'function') gtag('event', 'share_link_copied', { event_category: 'engagement', industry: ind || 'unknown', url: url });
  }

  // Inject into case study pages — after .cs-cta
  var cta = document.querySelector('.cs-cta');
  if(cta) cta.appendChild(createBtn());

  // Inject into demo-showcase — after .call-cta or .demo-console-wrap
  var callCta = document.querySelector('.call-cta');
  if(callCta) callCta.appendChild(createBtn());
})();
