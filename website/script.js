/* ============================================
   THE CALL TAKER — Shared JavaScript
   Scroll reveals, FAQ accordion, mobile nav
   ============================================ */

(function () {
  'use strict';

  // --- Sticky Header ---
  const header = document.querySelector('.header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  // --- Mobile Menu ---
  const toggle = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');
  if (toggle && mobileNav) {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('open');
      mobileNav.classList.toggle('open');
      document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
    });
    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        toggle.classList.remove('open');
        mobileNav.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // --- Scroll Reveal (subtle fade-in) ---
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => observer.observe(el));
  }

  // --- FAQ Accordion ---
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const wasOpen = item.classList.contains('open');
      // Close all in same container
      item.parentElement.querySelectorAll('.faq-item.open').forEach(el => el.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  // --- Smooth scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id === '#') return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // --- Active nav link highlighting ---
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a, .mobile-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html') || (currentPage === 'index.html' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // --- Float Widget & Exit Popup ---
  // These functions are called by onclick handlers in the float widget
  // and exit popup HTML injected across all pages.

  window.toggleFloatPanel = function(){
    document.getElementById('float-panel').classList.toggle('open');
  };

  window.requestFloatCallback = function(){
    var phone = document.getElementById('float-phone');
    var company = document.getElementById('float-company');
    if(!phone || !phone.value.trim() || phone.value.trim().length < 7) return;
    var p = phone.value.trim(), c = company ? company.value.trim() : '';
    if(typeof fbq==='function') fbq('track','Lead',{content_name:'Float Callback',content_category:'Callback Request',value:p});
    if(typeof gtag==='function') gtag('event','conversion',{send_to:'AW-17970510102/callback'});
    fetch('https://ntfy.sh/tct-urgent-Hk9UOEZR',{method:'POST',headers:{'Title':'WEBSITE CALLBACK: '+(c||p),'Priority':'urgent','Tags':'rotating_light,phone'},body:'Phone: '+p+'\nCompany: '+c+'\nSource: Floating widget'});
    var btn = phone.parentElement.querySelector('.callback-btn');
    if(btn){btn.textContent='Calling you now!';btn.disabled=true;}
  };

  window.requestExitCallback = function(){
    var phone = document.getElementById('exit-phone');
    var company = document.getElementById('exit-company');
    if(!phone || !phone.value.trim() || phone.value.trim().length < 7) return;
    var p = phone.value.trim(), c = company ? company.value.trim() : '';
    if(typeof fbq==='function') fbq('track','Lead',{content_name:'Exit Intent',content_category:'Callback Request',value:p});
    if(typeof gtag==='function') gtag('event','conversion',{send_to:'AW-17970510102/exit_intent'});
    fetch('https://ntfy.sh/tct-urgent-Hk9UOEZR',{method:'POST',headers:{'Title':'EXIT INTENT: '+(c||p),'Priority':'urgent','Tags':'rotating_light,phone'},body:'Phone: '+p+'\nCompany: '+c+'\nSource: Exit intent popup\nThey were LEAVING and still gave their number!'});
    var popup = document.getElementById('exit-popup');
    if(popup) popup.innerHTML='<div style="text-align:center;padding:40px;color:#fff;"><h3>We\'ll call you right back!</h3></div>';
    setTimeout(function(){if(popup)popup.classList.remove('show');},3000);
  };

  window.closeExitPopup = function(){
    var p = document.getElementById('exit-popup');
    if(p) p.classList.remove('show');
  };

})();
