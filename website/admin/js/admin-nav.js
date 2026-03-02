// Admin Navigation — The Call Taker
// Injects sidebar into every admin page

var AdminNav = (function() {
  var pages = [
    { name: 'Dashboard', href: 'index.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>' },
    { name: 'Contacts', href: 'contacts.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
    { name: 'Inbox', href: 'inbox.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' },
    { name: 'Pipeline', href: 'pipeline.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>' },
    { name: 'Onboarding', href: 'onboarding.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>' },
    { name: 'Intake', href: 'intake.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>' },
    { name: 'Bots', href: 'bots.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>' },
    { name: 'Reports', href: 'reports.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' },
    { name: 'Settings', href: 'settings.html', icon: '<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>' }
  ];

  var currentPage = window.location.pathname.split('/').pop() || 'index.html';

  function render() {
    var sidebar = document.getElementById('admin-sidebar');
    if (!sidebar) return;

    var html = '<div class="sidebar-inner">';
    html += '<div class="sidebar-header">';
    html += '<a href="index.html" class="sidebar-logo">The Call<span>Taker</span></a>';
    html += '<span class="sidebar-label">Admin</span>';
    html += '</div>';
    html += '<nav class="sidebar-nav">';

    pages.forEach(function(p) {
      var active = currentPage === p.href ? ' active' : '';
      html += '<a href="' + p.href + '" class="sidebar-link' + active + '">' + p.icon + '<span>' + p.name + '</span></a>';
    });

    html += '</nav>';
    html += '<div class="sidebar-footer">';
    html += '<button class="dark-toggle" id="dark-toggle"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg> <span id="dark-label">' + (localStorage.getItem('tct_dark_mode') === 'true' ? 'Light Mode' : 'Dark Mode') + '</span></button>';
    html += '<a href="../index.html" class="sidebar-link sidebar-back"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg><span>Back to Site</span></a>';
    html += '<button onclick="AdminAuth.logout()" class="sidebar-link sidebar-logout"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg><span>Logout</span></button>';
    html += '</div>';
    html += '</div>';

    sidebar.innerHTML = html;
  }

  function initMobileToggle() {
    var toggle = document.getElementById('admin-mobile-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function() {
      var sidebar = document.getElementById('admin-sidebar');
      sidebar.classList.toggle('open');
    });
  }

  function initDarkMode() {
    // Apply saved preference
    if (localStorage.getItem('tct_dark_mode') === 'true') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
    // Toggle button
    setTimeout(function() {
      var btn = document.getElementById('dark-toggle');
      if (!btn) return;
      btn.addEventListener('click', function() {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (isDark) {
          document.documentElement.removeAttribute('data-theme');
          localStorage.setItem('tct_dark_mode', 'false');
          document.getElementById('dark-label').textContent = 'Dark Mode';
        } else {
          document.documentElement.setAttribute('data-theme', 'dark');
          localStorage.setItem('tct_dark_mode', 'true');
          document.getElementById('dark-label').textContent = 'Light Mode';
        }
      });
    }, 100);
  }

  // Auto-init when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { render(); initMobileToggle(); initDarkMode(); checkUnread(); });
  } else {
    render();
    initMobileToggle();
    initDarkMode();
    checkUnread();
  }

  // Check for unread messages and add badge to Inbox link
  function checkUnread() {
    if (typeof GHL === 'undefined') return;
    setTimeout(async function() {
      try {
        var data = await GHL.listContacts({ limit: 20 });
        var contacts = data.contacts || [];
        var unreadCount = 0;
        // Check last 5 contacts for inbound messages in last 2 hours
        for (var i = 0; i < Math.min(5, contacts.length); i++) {
          try {
            var convos = await GHL.searchConversations(contacts[i].id);
            var conversations = convos.conversations || [];
            if (conversations.length > 0) {
              var msgs = await GHL.getMessages(conversations[0].id);
              var messages = msgs.messages || msgs.lastMessageBody ? [msgs] : [];
              if (Array.isArray(msgs.messages)) messages = msgs.messages;
              for (var j = messages.length - 1; j >= Math.max(0, messages.length - 3); j--) {
                var m = messages[j];
                if (m && m.direction === 'inbound') {
                  var msgTime = new Date(m.dateAdded).getTime();
                  if (Date.now() - msgTime < 2 * 60 * 60 * 1000) unreadCount++;
                }
              }
            }
          } catch(e) { /* skip */ }
        }
        if (unreadCount > 0) {
          var inboxLink = document.querySelector('.sidebar-link[href="inbox.html"] span');
          if (inboxLink) {
            inboxLink.innerHTML = 'Inbox <span class="sidebar-badge">' + unreadCount + '</span>';
          }
        }
      } catch(e) { /* silent */ }
    }, 2000); // delay to not block page load
  }

  return { render: render, checkUnread: checkUnread };
})();
