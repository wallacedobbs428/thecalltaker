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
    const setMenuOpen = (open) => {
      toggle.classList.toggle('open', open);
      mobileNav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      document.body.style.overflow = open ? 'hidden' : '';
    };
    toggle.setAttribute('aria-expanded', 'false');
    toggle.addEventListener('click', () => {
      setMenuOpen(!mobileNav.classList.contains('open'));
    });
    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => setMenuOpen(false));
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') setMenuOpen(false);
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

  // --- Removed floating callback widget handlers ---
  // Keep safe no-op globals so legacy cached handlers fail without provider sends.

  window.toggleFloatPanel = function(){
    return false;
  };

  window.requestFloatCallback = function(){
    return false;
  };

  window.requestExitCallback = function(){
    return false;
  };

  window.closeExitPopup = function(){
    var p = document.getElementById('exit-popup');
    if(p) p.classList.remove('show');
  };

})();
