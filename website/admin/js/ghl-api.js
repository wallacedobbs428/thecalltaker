// GHL API Utility — The Call Taker Admin
// Single source of truth for all GoHighLevel API calls

var GHL = (function() {
  var BASE = 'https://services.leadconnectorhq.com';
  var KEY = 'pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35';
  var LOCATION = 'tQb9YmrGDrdVUJYPKrsY';
  var V_CONTACTS = '2021-07-28';
  var V_CONVERSATIONS = '2021-04-15';

  var CACHE_TTL = 30000; // 30 seconds

  function headers(version) {
    return {
      'Authorization': 'Bearer ' + KEY,
      'Version': version || V_CONTACTS,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  function cacheKey(key) { return 'ghl_cache_' + key; }

  function getCache(key) {
    try {
      var raw = sessionStorage.getItem(cacheKey(key));
      if (!raw) return null;
      var entry = JSON.parse(raw);
      if (Date.now() - entry.ts > CACHE_TTL) {
        sessionStorage.removeItem(cacheKey(key));
        return null;
      }
      return entry.data;
    } catch(e) { return null; }
  }

  function setCache(key, data) {
    try {
      sessionStorage.setItem(cacheKey(key), JSON.stringify({ ts: Date.now(), data: data }));
    } catch(e) { /* storage full, ignore */ }
  }

  async function request(method, path, body, version) {
    var opts = { method: method, headers: headers(version) };
    if (body) opts.body = JSON.stringify(body);
    var res = await fetch(BASE + path, opts);
    if (res.status === 429) {
      // Rate limited — wait and retry once
      await new Promise(function(r) { setTimeout(r, 5000); });
      res = await fetch(BASE + path, opts);
    }
    if (!res.ok) {
      var errText = await res.text();
      throw new Error('GHL ' + res.status + ': ' + errText);
    }
    return res.json();
  }

  return {
    LOCATION: LOCATION,
    KEY: KEY,
    BASE: BASE,

    // === CONTACTS ===

    listContacts: async function(opts) {
      opts = opts || {};
      var page = opts.page || 1;
      var limit = opts.limit || 20;
      var query = opts.query || '';
      var ck = 'contacts_' + page + '_' + limit + '_' + query;
      if (!opts.noCache) {
        var cached = getCache(ck);
        if (cached) return cached;
      }
      var url = '/contacts/?locationId=' + LOCATION + '&limit=' + limit + '&page=' + page;
      if (query) url += '&query=' + encodeURIComponent(query);
      var data = await request('GET', url);
      setCache(ck, data);
      return data;
    },

    getContact: async function(id) {
      return request('GET', '/contacts/' + id);
    },

    createContact: async function(data) {
      data.locationId = LOCATION;
      return request('POST', '/contacts/', data);
    },

    updateContact: async function(id, data) {
      return request('PUT', '/contacts/' + id, data);
    },

    addTags: async function(contactId, tags) {
      return request('POST', '/contacts/' + contactId + '/tags', { tags: tags });
    },

    removeTags: async function(contactId, tags) {
      // DELETE with body
      var opts = {
        method: 'DELETE',
        headers: headers(),
        body: JSON.stringify({ tags: tags })
      };
      var res = await fetch(BASE + '/contacts/' + contactId + '/tags', opts);
      if (!res.ok) throw new Error('GHL ' + res.status);
      return res.json();
    },

    searchByTag: async function(tag, page) {
      // GHL doesn't have a tag filter param — fetch and filter client-side
      // For now, use query search which searches across fields
      return this.listContacts({ page: page || 1, limit: 100, noCache: true });
    },

    // === CONVERSATIONS ===

    searchConversations: async function(contactId) {
      var url = '/conversations/search?locationId=' + LOCATION;
      if (contactId) url += '&contactId=' + contactId;
      return request('GET', url, null, V_CONVERSATIONS);
    },

    getMessages: async function(conversationId) {
      return request('GET', '/conversations/' + conversationId + '/messages', null, V_CONVERSATIONS);
    },

    sendMessage: async function(opts) {
      // opts: { type: 'SMS'|'Email', contactId, message (SMS), html (Email), subject (Email) }
      var body = { type: opts.type, contactId: opts.contactId };
      if (opts.type === 'Email') {
        body.html = opts.html || opts.message;
        body.subject = opts.subject || '(No Subject)';
      } else {
        body.message = opts.message;
      }
      return request('POST', '/conversations/messages', body, V_CONVERSATIONS);
    },

    // === PIPELINE ===

    getPipelines: async function() {
      var ck = 'pipelines';
      var cached = getCache(ck);
      if (cached) return cached;
      var data = await request('GET', '/opportunities/pipelines?locationId=' + LOCATION);
      setCache(ck, data);
      return data;
    },

    searchOpportunities: async function(pipelineId, page) {
      var url = '/opportunities/search?location_id=' + LOCATION + '&pipeline_id=' + pipelineId;
      if (page) url += '&page=' + page;
      return request('GET', url);
    },

    updateOpportunity: async function(oppId, data) {
      return request('PUT', '/opportunities/' + oppId, data);
    },

    deleteContact: async function(contactId) {
      return request('DELETE', '/contacts/' + contactId);
    },

    // === NOTES ===

    addNote: async function(contactId, body) {
      return request('POST', '/contacts/' + contactId + '/notes', {
        body: body,
        userId: 'g4Ocu4qnhv7O8CrqpDTC'
      });
    },

    // === UTILITY ===

    clearCache: function() {
      Object.keys(sessionStorage).forEach(function(k) {
        if (k.startsWith('ghl_cache_')) sessionStorage.removeItem(k);
      });
    },

    formatPhone: function(phone) {
      if (!phone) return '';
      var digits = phone.replace(/\D/g, '');
      if (digits.length === 11 && digits[0] === '1') digits = digits.slice(1);
      if (digits.length === 10) {
        return '(' + digits.slice(0,3) + ') ' + digits.slice(3,6) + '-' + digits.slice(6);
      }
      return phone;
    },

    formatDate: function(dateStr) {
      if (!dateStr) return '';
      var d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },

    formatDateTime: function(dateStr) {
      if (!dateStr) return '';
      var d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' ' +
             d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    },

    timeAgo: function(dateStr) {
      if (!dateStr) return '';
      var now = Date.now();
      var then = new Date(dateStr).getTime();
      var diff = now - then;
      var mins = Math.floor(diff / 60000);
      if (mins < 1) return 'just now';
      if (mins < 60) return mins + 'm ago';
      var hrs = Math.floor(mins / 60);
      if (hrs < 24) return hrs + 'h ago';
      var days = Math.floor(hrs / 24);
      if (days < 7) return days + 'd ago';
      return GHL.formatDate(dateStr);
    }
  };
})();
