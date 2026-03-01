// Admin Authentication — The Call Taker
// Password gate for /admin/ pages

var AdminAuth = (function() {
  var SESSION_KEY = 'tct_admin_auth';
  var PASSWORD = 'tctadmin';

  return {
    isAuthenticated: function() {
      return sessionStorage.getItem(SESSION_KEY) === 'true';
    },

    authenticate: function(pw) {
      if (pw === PASSWORD) {
        sessionStorage.setItem(SESSION_KEY, 'true');
        return true;
      }
      return false;
    },

    logout: function() {
      sessionStorage.removeItem(SESSION_KEY);
      window.location.href = 'index.html';
    },

    // Call on every page except index.html — redirects if not authenticated
    requireAuth: function() {
      if (!this.isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
      }
      return true;
    }
  };
})();
