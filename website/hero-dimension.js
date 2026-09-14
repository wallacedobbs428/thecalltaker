/* One frame per scroll, no perpetual rendering loop and no network requests. */
(function () {
  'use strict';
  var scene = document.querySelector('.call-sculpture');
  if (!scene) return;
  var button = scene.querySelector('.sculpture-motion');
  var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  var paused = false;
  var visible = true;
  var frame = 0;
  function enabled() { return !paused && !preference.matches && visible && !document.hidden; }
  function draw() {
    frame = 0;
    if (!enabled()) return;
    var box = scene.getBoundingClientRect();
    var progress = Math.max(-1, Math.min(1, (window.innerHeight / 2 - box.top - box.height / 2) / window.innerHeight));
    scene.style.setProperty('--scene-turn', (progress * 65).toFixed(2) + 'deg');
    scene.style.setProperty('--scene-lift', (progress * -28).toFixed(2) + 'px');
  }
  function schedule() { if (enabled() && !frame) frame = window.requestAnimationFrame(draw); }
  function sync() {
    scene.classList.toggle('is-moving', enabled());
    button.hidden = preference.matches;
    button.textContent = paused ? 'Resume motion' : 'Pause motion';
    button.setAttribute('aria-pressed', String(paused));
    if (!enabled() && frame) { window.cancelAnimationFrame(frame); frame = 0; }
    schedule();
  }
  button.addEventListener('click', function () { paused = !paused; sync(); });
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  document.addEventListener('visibilitychange', sync);
  preference.addEventListener('change', sync);
  if ('IntersectionObserver' in window) new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    sync();
  }).observe(scene);
  sync();
})();
