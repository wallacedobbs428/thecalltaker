/* ============================================
   COMMAND PALETTE — Cmd+K / Ctrl+K
   Navigation + "Play 15s Demo" action.
   Accessible, reduced-motion safe.
   ============================================ */
(function() {
  'use strict';
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // === Inline styles ===
  var css = document.createElement('style');
  css.textContent = [
    '.cp-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.45);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:none;align-items:flex-start;justify-content:center;padding-top:min(20vh,160px)}',
    '.cp-overlay.open{display:flex}',
    reduced ? '' : '.cp-overlay.open .cp-modal{animation:cpSlideIn .2s cubic-bezier(.16,1,.3,1)}',
    reduced ? '' : '@keyframes cpSlideIn{from{opacity:0;transform:translateY(-12px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}',
    '.cp-modal{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:14px;width:min(480px,90vw);box-shadow:0 16px 48px rgba(0,0,0,.12);overflow:hidden;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif}',
    '.cp-input-wrap{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid rgba(0,0,0,.06)}',
    '.cp-input-wrap svg{width:18px;height:18px;color:#9ca3af;flex-shrink:0}',
    '.cp-input{flex:1;border:none;outline:none;font-size:.95rem;font-family:inherit;color:#111827;background:transparent}',
    '.cp-input::placeholder{color:#9ca3af}',
    '.cp-kbd{font-size:.65rem;font-weight:600;color:#9ca3af;background:rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.06);border-radius:4px;padding:2px 6px;font-family:inherit}',
    '.cp-list{max-height:280px;overflow-y:auto;padding:6px}',
    '.cp-item{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:10px;cursor:pointer;transition:background .1s}',
    '.cp-item:hover,.cp-item.active{background:rgba(0,220,130,.06)}',
    '.cp-item.active{outline:2px solid rgba(0,220,130,.3);outline-offset:-2px}',
    '.cp-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}',
    '.cp-icon svg{width:16px;height:16px}',
    '.cp-icon-nav{background:rgba(30,58,95,.06);color:#1e3a5f}',
    '.cp-icon-action{background:rgba(0,220,130,.08);color:#00dc82}',
    '.cp-label{font-size:.88rem;font-weight:600;color:#111827}',
    '.cp-desc{font-size:.72rem;color:#9ca3af;margin-top:1px}',
    '.cp-footer{display:flex;gap:16px;padding:10px 18px;border-top:1px solid rgba(0,0,0,.04);font-size:.68rem;color:#9ca3af}',
    '.cp-footer span{display:flex;align-items:center;gap:4px}',
    '.cp-footer kbd{font-size:.6rem;font-weight:600;background:rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.06);border-radius:3px;padding:1px 4px;font-family:inherit}'
  ].join('\n');
  document.head.appendChild(css);

  // === Commands ===
  var commands = [
    { id: 'home', type: 'nav', label: 'Home', desc: 'Go to homepage', icon: 'home', href: '/' },
    { id: 'pricing', type: 'nav', label: 'Pricing', desc: 'View plans', icon: 'dollar', href: '/pricing.html' },
    { id: 'demo', type: 'nav', label: 'Demo', desc: 'Hear the AI receptionist', icon: 'play', href: '/demo-showcase.html' },
    { id: 'cases', type: 'nav', label: 'Case Studies', desc: 'Real results from real businesses', icon: 'chart', href: '/case-studies/' },
    { id: 'pilot', type: 'nav', label: 'Start Free Pilot', desc: '14-day free trial', icon: 'rocket', href: '/pilot/' },
    { id: 'book', type: 'nav', label: 'Book a Demo', desc: 'Schedule a 10-min call', icon: 'calendar', href: '/book.html' },
    { id: 'play', type: 'action', label: 'Play 15s Demo', desc: 'Hear the AI handle a call', icon: 'speaker', action: function() {
      var dc = document.querySelector('.dc');
      if (dc) {
        dc.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
        setTimeout(function() {
          if (window.TCT_Console && window.TCT_Console.play) window.TCT_Console.play();
        }, 400);
      } else {
        window.location.href = '/demo-showcase.html';
      }
    }},
    { id: 'call', type: 'action', label: 'Call the AI', desc: '(629) 269-9697 — live 24/7', icon: 'phone', action: function() { window.location.href = 'tel:+16292699697'; }}
  ];

  var icons = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>',
    dollar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    rocket: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    speaker: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11,5 6,9 2,9 2,15 6,15 11,19"/><path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.07"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.11 2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
  };

  // === Build DOM ===
  var overlay = document.createElement('div');
  overlay.className = 'cp-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Command palette');
  overlay.innerHTML = '<div class="cp-modal">' +
    '<div class="cp-input-wrap">' + icons.search +
    '<input class="cp-input" type="text" placeholder="Search pages or actions..." autocomplete="off" role="combobox" aria-expanded="true" aria-controls="cp-list" aria-autocomplete="list">' +
    '<span class="cp-kbd">ESC</span></div>' +
    '<div class="cp-list" id="cp-list" role="listbox"></div>' +
    '<div class="cp-footer"><span><kbd>↑↓</kbd> Navigate</span><span><kbd>↵</kbd> Open</span><span><kbd>ESC</kbd> Close</span></div>' +
    '</div>';
  document.body.appendChild(overlay);

  var input = overlay.querySelector('.cp-input');
  var list = overlay.querySelector('.cp-list');
  var modal = overlay.querySelector('.cp-modal');
  var activeIdx = 0;

  function renderItems(filter) {
    var q = (filter || '').toLowerCase();
    var filtered = commands.filter(function(c) {
      return !q || c.label.toLowerCase().indexOf(q) !== -1 || c.desc.toLowerCase().indexOf(q) !== -1;
    });
    activeIdx = 0;
    list.innerHTML = filtered.map(function(c, i) {
      var cls = c.type === 'action' ? 'cp-icon-action' : 'cp-icon-nav';
      return '<div class="cp-item' + (i === 0 ? ' active' : '') + '" data-id="' + c.id + '" role="option" aria-selected="' + (i === 0) + '">' +
        '<div class="cp-icon ' + cls + '">' + icons[c.icon] + '</div>' +
        '<div><div class="cp-label">' + c.label + '</div><div class="cp-desc">' + c.desc + '</div></div></div>';
    }).join('');
  }

  function getItems() { return list.querySelectorAll('.cp-item'); }

  function setActive(idx) {
    var items = getItems();
    if (!items.length) return;
    activeIdx = ((idx % items.length) + items.length) % items.length;
    items.forEach(function(el, i) {
      el.classList.toggle('active', i === activeIdx);
      el.setAttribute('aria-selected', i === activeIdx);
    });
    items[activeIdx].scrollIntoView({ block: 'nearest' });
  }

  function execute(id) {
    var cmd = commands.filter(function(c) { return c.id === id; })[0];
    if (!cmd) return;
    close();
    if (cmd.action) { cmd.action(); }
    else if (cmd.href) { window.location.href = cmd.href; }
  }

  function open() {
    overlay.classList.add('open');
    input.value = '';
    renderItems('');
    input.focus();
    document.body.style.overflow = 'hidden';
  }

  function close() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  function isOpen() { return overlay.classList.contains('open'); }

  // === Events ===
  // Cmd+K / Ctrl+K
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      isOpen() ? close() : open();
    }
    if (!isOpen()) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive(activeIdx + 1); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActive(activeIdx - 1); }
    if (e.key === 'Enter') {
      e.preventDefault();
      var items = getItems();
      if (items[activeIdx]) execute(items[activeIdx].getAttribute('data-id'));
    }
  });

  // Click outside closes
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) close();
  });

  // Click item
  list.addEventListener('click', function(e) {
    var item = e.target.closest('.cp-item');
    if (item) execute(item.getAttribute('data-id'));
  });

  // Filter on type
  input.addEventListener('input', function() {
    renderItems(this.value);
  });

  // Focus trap inside modal
  modal.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      e.preventDefault();
      input.focus();
    }
  });
})();
