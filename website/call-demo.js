(function () {
  'use strict';
  var dialog;
  var trigger;
  function openDemo(event) {
    var link = event.target.closest('a[data-call-demo]');
    if (!link || event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (typeof HTMLDialogElement === 'undefined') return;
    event.preventDefault();
    trigger = link;
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.className = 'call-demo-dialog';
      dialog.setAttribute('aria-labelledby', 'call-demo-title');
      dialog.innerHTML = '<button type="button" class="call-demo-close" aria-label="Close demo number">×</button><p class="call-demo-label">MEET GIDEON</p><h2 id="call-demo-title">Call the demo.</h2><p>Talk with The Call Taker’s AI receptionist. Try asking about a service or leaving a callback request.</p><a class="call-demo-number" href="tel:+16292699697" data-tct-event="cta_intent" data-tct-page="demo" data-tct-cta="Call demo number" data-tct-destination="live_demo_phone">(629) 269-9697</a><p class="call-demo-note">Tap to call from your phone. No form required. This is a demo, not an emergency service.</p>';
      document.body.appendChild(dialog);
      dialog.querySelector('button').addEventListener('click', function () { dialog.close(); });
      dialog.addEventListener('click', function (e) { if(e.target === dialog) { var r=dialog.getBoundingClientRect(); if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) dialog.close(); } });
      dialog.addEventListener('close', function () { if(trigger) trigger.focus(); });
    }
    dialog.showModal();
  }
  document.addEventListener('click', openDemo);
})();
