(function () {
  'use strict';
  var menu = document.getElementById('tctSiteMenu');
  if (!menu) return;
  var summary = menu.querySelector('summary');
  function close(restoreFocus) {
    if (!menu.open) return;
    menu.open = false;
    if (restoreFocus) summary.focus();
  }
  menu.querySelectorAll('nav a').forEach(function (link) {
    var path = new URL(link.href, location.href).pathname;
    if (path === location.pathname && !link.hash) link.setAttribute('aria-current', 'page');
    link.addEventListener('click', function () {
      // Keep the demo trigger mounted/visible until the delegated dialog handler runs.
      if (link.hasAttribute('data-call-demo')) summary.focus();
      close(false);
    });
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && menu.open) { event.preventDefault(); close(true); }
  });
  document.addEventListener('click', function (event) {
    if (!menu.contains(event.target)) close(false);
  });
  document.addEventListener('focusin', function (event) {
    if (!menu.contains(event.target)) close(false);
  });
})();
