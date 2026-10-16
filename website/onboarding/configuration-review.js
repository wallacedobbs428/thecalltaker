(function (root) {
  'use strict';
  var KEY = 'tct_configuration_continuation_v1';
  var ORIGINS = ['https://call-taker-os.vercel.app', 'https://call-taker-square-sandbox.vercel.app'];
  var DECLARATION = 'I authorize inbound call capture and notifications for this exact configuration while my subscription is active, until I revoke it.';
  var UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
  function display(value) {
    if (Array.isArray(value)) return value.map(display).join('; ');
    if (value && typeof value === 'object') return Object.keys(value).map(function (key) { return key + ': ' + display(value[key]); }).join('; ');
    return typeof value === 'string' || typeof value === 'number' ? String(value) : 'Not recorded';
  }
  function serviceStatus(value) {
    return 'Historical activation: ' + (typeof value.activation_state === 'string' ? value.activation_state : 'not proven')
      + '. Service permitted now: ' + (value.current_service_permitted === true ? 'yes' : 'not proven or held')
      + (typeof value.current_service_hold === 'string' ? '. Hold: ' + value.current_service_hold : '') + '.';
  }
  function valid(context, now) {
    return context && ORIGINS.indexOf(context.apiOrigin) >= 0
      && UUID.test(context.checkoutAttemptId) && UUID.test(context.correlationId) && UUID.test(context.sessionId)
      && /^l4sc1_[A-Za-z0-9_-]{43}$/.test(context.continuationToken)
      && Date.parse(context.expiresAt) > now && Date.parse(context.expiresAt) <= now + 7260000;
  }
  async function request(context, action, configId, fetcher) {
    if (!valid(context, Date.now())) throw Error('protected_access_expired');
    if (['current', 'consent', 'authorize_service', 'revoke_service', 'confirm_forwarding'].indexOf(action) < 0
      || (action !== 'current' && !UUID.test(configId))) throw Error('exact_configuration_required');
    var body = { action: action, checkoutAttemptId: context.checkoutAttemptId,
      correlationId: context.correlationId, sessionId: context.sessionId, continuationToken: context.continuationToken };
    if (action !== 'current') body.configId = configId;
    if (action === 'authorize_service') body.declaration = DECLARATION;
    var response = await fetcher(context.apiOrigin + '/api/public/provisioning-configuration', {
      method: 'POST', credentials: 'omit', redirect: 'error', cache: 'no-store',
      signal: AbortSignal.timeout(10000), headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    var value = await response.json();
    if (!response.ok || !value || typeof value !== 'object' || Array.isArray(value)) throw Error('configuration_readback_unavailable');
    return value;
  }
  function stored(storage) { try { var c = JSON.parse(storage.getItem(KEY) || 'null'); return valid(c, Date.now()) ? c : null; } catch (_) { return null; } }
  function recovery(storage) {
    try { var c = JSON.parse(storage.getItem(KEY) || 'null');
      return c && ORIGINS.indexOf(c.apiOrigin) >= 0 && UUID.test(c.checkoutAttemptId) && UUID.test(c.correlationId) && UUID.test(c.sessionId)
        ? { checkoutAttemptId: c.checkoutAttemptId, correlationId: c.correlationId, sessionId: c.sessionId, apiOrigin: c.apiOrigin, resumeConfiguration: true } : null;
    } catch (_) { return null; }
  }
  function remember(storage, context) {
    if (!valid(context, Date.now())) return false;
    try { storage.setItem(KEY, JSON.stringify(context)); return !!stored(storage); } catch (_) { return false; }
  }
  function mount(container, context, options) {
    var doc = container.ownerDocument, fetcher = options && options.fetchImpl || root.fetch.bind(root);
    var current = null, reviewed = false, busy = false;
    container.replaceChildren();
    function element(tag, text) { var e = doc.createElement(tag); if (text) e.textContent = text; return e; }
    var heading = element('h2', 'Review your exact service configuration');
    var intro = element('p', 'Setup answers and payment do not authorize phone changes or go-live. Review the configuration below. Each decision is separate. No forwarding is changed by these controls.');
    var state = element('p', 'Use the button to check the current configuration.'); state.setAttribute('role', 'status');
    var details = element('div'), controls = element('div');
    var refresh = element('button', 'Check current configuration'); refresh.type = 'button'; refresh.className = 'btn btn-primary';
    container.append(heading, intro, refresh, state, details, controls);
    async function load() {
      if (busy) return; busy = true; refresh.disabled = true;
      try {
        var next = await request(context, 'current', null, fetcher);
        if (!next.config_id || !UUID.test(next.config_id) || !/^[a-f0-9]{64}$/.test(next.configuration_sha256)) {
          current = null; details.replaceChildren(); controls.replaceChildren();
          state.textContent = next.state === 'WAITING_CONFIGURATION'
            ? 'Your setup is retained. The configuration owner has not prepared a reviewable version yet. No service was activated.'
            : 'The exact configuration could not be verified. No permission was recorded.';
          return;
        }
        if (!current || current.configuration_sha256 !== next.configuration_sha256 || current.config_id !== next.config_id) reviewed = false;
        current = next; render();
        state.textContent = 'Current revision ' + next.version + '. Configuration permission: ' + (next.consent_recorded === true ? 'recorded' : 'not recorded')
          + '. Ongoing service permission: ' + (next.service_authorized === true ? 'recorded' : 'not recorded')
          + '. Customer forwarding confirmation: ' + (next.forwarding_confirmed === true ? 'recorded' : 'not recorded')
          + '. ' + serviceStatus(next);
      } catch (_) { current = null; controls.replaceChildren(); state.textContent = valid(context, Date.now())
        ? 'We could not verify the current configuration. No permission or activation is assumed. You may retry this read.'
        : 'Protected access expired. Return to the accepted checkout and use its protected setup-recovery control. No access window was extended here.'; }
      finally { busy = false; refresh.disabled = false; }
    }
    function render() {
      details.replaceChildren(); controls.replaceChildren();
      var definition = current.configuration, setup = definition && definition.setup, operations = definition && definition.operations;
      if (!setup || !operations) { state.textContent = 'The complete service definition is unavailable.'; return; }
      details.append(element('h3', 'Revision ' + current.version + ': ' + String(setup.business_name || 'Your business')));
      var list = element('dl');
      [ ['Hours and timezone', [setup.days_open, setup.open_time, setup.close_time, setup.time_zone]],
        ['Service area', setup.service_area], ['Greeting', operations.greeting], ['Information captured', operations.intake_fields],
        ['Qualification rules', operations.qualification_rules], ['Escalation', operations.escalation_rules],
        ['Notification destinations', operations.notification_destinations], ['Prohibited promises', operations.prohibited_promises],
        ['Forwarding boundary', operations.forwarding_expectation],
        ['Provider resource versions', [current.provider, current.resource_id, current.resource_version, current.response_id, current.response_version]]
      ].forEach(function (pair) { list.append(element('dt', pair[0]), element('dd', display(pair[1]))); });
      details.append(list);
      var label = element('label'), checkbox = element('input'); checkbox.type = 'checkbox'; checkbox.checked = reviewed;
      label.append(checkbox, doc.createTextNode(' I reviewed this exact revision, including its notification destination and limits.'));
      controls.append(label);
      var buttons = [];
      function actionButton(title, action, description) {
        var requiresReview = action !== 'revoke_service';
        controls.append(element('p', description));
        var button = element('button', title); button.type = 'button'; button.className = 'btn btn-primary'; button.disabled = requiresReview && !reviewed;
        button.dataset.reviewRequired = requiresReview ? 'true' : 'false';
        button.addEventListener('click', async function () {
          if ((requiresReview && !reviewed) || busy || !current) return;
          busy = true; buttons.forEach(function (b) { b.disabled = true; }); refresh.disabled = true;
          var id = current.config_id, hash = current.configuration_sha256;
          try {
            await request(context, action, id, fetcher);
            var readback = await request(context, 'current', null, fetcher);
            if (readback.config_id !== id || readback.configuration_sha256 !== hash) throw Error('configuration_changed');
            var field = action === 'consent' ? 'consent_recorded' : ['authorize_service', 'revoke_service'].indexOf(action) >= 0 ? 'service_authorized' : 'forwarding_confirmed';
            if (readback[field] !== (action !== 'revoke_service')) throw Error('decision_readback_missing');
            current = readback; render();
            state.textContent = 'Your exact decision was recorded and independently read back. This does not prove new provider work, call routing or delivery. ' + serviceStatus(readback);
          } catch (_) { current = null; reviewed = false; controls.replaceChildren(); state.textContent = 'The decision could not be independently verified. Check the current configuration before trying again; no activation is assumed.'; }
          finally { busy = false; refresh.disabled = false; }
        });
        buttons.push(button); controls.append(button);
      }
      actionButton('Authorize this configuration', 'consent', 'Permit configuration, controlled testing and publication of these exact provider versions only. This does not change your forwarding or independently activate service.');
      actionButton('Authorize ongoing service', 'authorize_service', DECLARATION);
      if (current.service_authorized === true) actionButton('Withdraw ongoing service permission', 'revoke_service', 'Stop future processing under this service permission. This cannot retract an accepted notification, undo a completed provider operation, or change your phone forwarding.');
      actionButton('Confirm my forwarding setup', 'confirm_forwarding', 'Confirm only after you have configured your own forwarding to ' + String(current.provider_number || 'the reviewed number') + '. The Call Taker still verifies the route and actual service evidence. This button does not change any phone setting.');
      checkbox.addEventListener('change', function () { reviewed = checkbox.checked; buttons.forEach(function (b) { b.disabled = busy || (!reviewed && b.dataset.reviewRequired !== 'false'); }); });
    }
    refresh.addEventListener('click', load);
    return { refresh: load };
  }
  var api = { storageKey: KEY, declaration: DECLARATION, serviceStatus: serviceStatus, valid: valid, stored: stored, recovery: recovery, remember: remember, request: request, mount: mount };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.TCTCustomerConfigurationReview = api;
})(typeof window !== 'undefined' ? window : globalThis);
