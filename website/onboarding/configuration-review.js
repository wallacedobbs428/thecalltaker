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
  function customerProgress(value) {
    var stages = {
      ENROLLMENT_RECEIVED: ['Enrollment received', 'Your enrollment request is retained. Verification is still pending; call handling is not active.'],
      ENROLLMENT_VERIFIED: ['Enrollment verified', 'Your enrollment is verified. Setup, configuration review, permissions, and testing remain separate before launch.'],
      SETUP_NEEDED: ['Setup needed', 'Complete the protected business questionnaire so the configuration owner can prepare your call flow.'],
      CONFIGURATION_REVIEW: ['Configuration review', 'Your exact business configuration is being prepared or reviewed. Check the current version below before making a service decision.'],
      CUSTOMER_DECISION: ['Your service decisions', 'Review the exact configuration and record each required permission separately. These controls do not change your phone forwarding.'],
      READY_FOR_TESTS: ['Ready for controlled tests', 'The required preparation is ready for controlled testing. This is not permission to route live calls.'],
      READY_FOR_LAUNCH: ['Ready for launch review', 'The launch owner must verify the required test and service authority. Readiness is not active call handling.'],
      BILLING_EXCEPTION: ['Billing needs review', 'A billing condition is holding service eligibility. The billing owner must reconcile it; do not submit another payment or assume service is active.']
    };
    var stage = value.current_service_permitted === true
      ? ['Service active', 'Current service permission is verified. Captured requests and actual notification outcomes remain separate below.']
      : stages[value.customer_stage] || ['Service status not verified', 'Current call handling is not proven. Check the protected status again; historical activation alone does not establish current permission.'];
    var basis = value.service_basis === 'verified_trial' ? 'Verified card-backed trial enrollment, not a payment receipt.'
      : value.service_basis === 'paid' ? 'Verified paid service basis.' : 'Service basis is not verified.';
    var end = typeof value.trial_end === 'string' ? Date.parse(value.trial_end) : NaN;
    return { title: stage[0], detail: stage[1], basis: basis,
      trial: Number.isFinite(end) ? 'Trial ends ' + new Date(end).toLocaleString(undefined,
        { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }) + '. Setup or activation does not restart this schedule.' : null };
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
  var CASE_ACTIONS = ['list', 'read', 'receipt_seen', 'acknowledge', 'qualify_request', 'assign_callback', 'start_callback', 'complete_callback', 'resolve', 'unresolved'];
  var CASE_OUTCOMES = ['information_only', 'quote_requested', 'quote_sent', 'order_progressed', 'customer_helped', 'lost', 'duplicate', 'not_applicable'];
  async function caseRequest(context, configId, action, caseId, fields, fetcher) {
    if (!valid(context, Date.now())) throw Error('protected_access_expired');
    if (!UUID.test(configId) || CASE_ACTIONS.indexOf(action) < 0 || (action !== 'list' && !UUID.test(caseId))) throw Error('exact_customer_request_required');
    fields = fields || {};
    if (Object.keys(fields).some(function (key) { return ['note', 'assignedTo', 'outcome'].indexOf(key) < 0; })) throw Error('unsupported_request_fields');
    if (fields.note !== undefined && (typeof fields.note !== 'string' || new TextEncoder().encode(fields.note).length > 1000)) throw Error('request_note_too_long');
    if (fields.assignedTo !== undefined && (typeof fields.assignedTo !== 'string' || fields.assignedTo.length > 80)) throw Error('callback_owner_invalid');
    if ((action === 'qualify_request' || action === 'unresolved') && (!fields.note || fields.note.trim().length < 3)) throw Error('request_note_required');
    if (action === 'assign_callback' && (!fields.assignedTo || fields.assignedTo.trim().length < 3)) throw Error('callback_owner_required');
    if (action === 'resolve' && CASE_OUTCOMES.indexOf(fields.outcome) < 0) throw Error('supported_disposition_required');
    var body = { action: action, configId: configId, checkoutAttemptId: context.checkoutAttemptId,
      correlationId: context.correlationId, sessionId: context.sessionId, continuationToken: context.continuationToken };
    if (action !== 'list') body.caseId = caseId;
    if (action !== 'list' && action !== 'read') {
      // Identical explicit intent keeps its identity across lost responses and reloads.
      // No token or customer-entered note is persisted in a URL or browser storage.
      var intent = JSON.stringify([configId, caseId, action, fields.note || '', fields.assignedTo || null, fields.outcome || null]);
      var bytes = new Uint8Array(await root.crypto.subtle.digest('SHA-256', new TextEncoder().encode(intent)));
      bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
      var hex = Array.from(bytes.slice(0, 16), function (n) { return n.toString(16).padStart(2, '0'); }).join('');
      body.requestId = hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20);
      Object.assign(body, fields);
    }
    var response = await fetcher(context.apiOrigin + '/api/public/customer-cases', {
      method: 'POST', credentials: 'omit', redirect: 'error', cache: 'no-store', signal: AbortSignal.timeout(10000),
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    var value = await response.json();
    if (!response.ok || !value || value.configuration_id !== configId) throw Error('customer_request_readback_unavailable');
    if (action === 'list') {
      if (!Array.isArray(value.cases) || value.cases.length > 20 || ['BOUNDED_COMPLETE', 'POSSIBLY_MORE'].indexOf(value.coverage) < 0
        || value.cases.some(function (item) { return !item || !UUID.test(item.case_id); })
        || new Set(value.cases.map(function (item) { return item.case_id; })).size !== value.cases.length) throw Error('customer_request_inventory_unverified');
    } else if (value.case_id !== caseId || value.external_actions !== 0) throw Error('customer_request_binding_unverified');
    return value;
  }
  function mountCases(container, context, configId, fetcher) {
    var doc = container.ownerDocument, busy = false;
    function element(tag, text) { var node = doc.createElement(tag); if (text) node.textContent = text; return node; }
    container.replaceChildren();
    var status = element('p', 'Check the requests captured for your business.'); status.setAttribute('role', 'status');
    var refresh = element('button', 'Check customer requests'); refresh.type = 'button';
    var cards = element('div');
    container.append(element('h3', 'Your captured requests'), element('p', 'These controls record your business follow-up only. They do not call or message the caller, change routing, or prove a booking, payment, or recovered revenue.'), refresh, status, cards);
    function render(items) {
      cards.replaceChildren();
      items.forEach(function (item) {
        var captured = typeof item.request_captured_at === 'string' ? Date.parse(item.request_captured_at) : NaN;
        var title = Number.isFinite(captured) ? 'Request received ' + new Date(captured).toLocaleString(undefined,
          { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }) : 'Captured request';
        var card = element('section'); card.append(element('h4', title), element('p', 'Request reference: ' + item.case_id.slice(-8)));
        [['Request status', item.lifecycle_status], ['Notification status', item.notification_status], ['Seen receipt', item.receipt_status],
          ['Acknowledgement', item.acknowledgement_status], ['Callback status', item.follow_up_status],
          ['Business disposition', item.business_outcome_status], ['Owner', item.next_action_owner], ['Next action', item.next_action]]
          .forEach(function (pair) { card.append(element('p', pair[0] + ': ' + display(pair[1]))); });
        var terminal = item.lifecycle_status === 'resolved' || item.lifecycle_status === 'suppressed';
        if (!terminal) {
          var noteLabel = element('label', 'Business follow-up note (do not enter caller contact details)'), note = element('textarea'); note.maxLength = 1000; noteLabel.append(note); card.append(noteLabel);
          function button(title, action, fields) {
            var control = element('button', title); control.type = 'button';
            control.addEventListener('click', async function () {
              if (busy) return; busy = true; refresh.disabled = true;
              var buttons = cards.querySelectorAll('button'); buttons.forEach(function (b) { b.disabled = true; });
              try {
                var submitted = fields();
                await caseRequest(context, configId, action, item.case_id, submitted, fetcher);
                var readback = await caseRequest(context, configId, 'read', item.case_id, {}, fetcher);
                var proven = action === 'receipt_seen' ? readback.receipt_status === 'confirmed_seen'
                  : action === 'acknowledge' ? readback.acknowledgement_status === 'acknowledged'
                    : action === 'assign_callback' ? readback.next_action_owner === 'customer_reported:' + submitted.assignedTo
                      : action === 'start_callback' ? readback.follow_up_status === 'in_progress'
                        : action === 'complete_callback' ? readback.follow_up_status === 'completed'
                          : action === 'resolve' ? readback.lifecycle_status === 'resolved' && readback.business_outcome_status === submitted.outcome
                            : readback.lifecycle_status === 'blocked' && readback.follow_up_status === 'blocked';
                if (!proven) throw Error('customer_report_readback_missing');
                var currentCases = await caseRequest(context, configId, 'list', null, {}, fetcher);
                render(currentCases.cases);
                status.textContent = 'Your report was recorded and independently read back. No caller was contacted. ' + (currentCases.coverage === 'POSSIBLY_MORE' ? 'Only the latest 20 requests are shown; older requests may exist.' : 'The current bounded request list was verified.');
              } catch (_) {
                cards.replaceChildren(); status.textContent = 'This report could not be independently verified. Check customer requests to reconcile the saved state before another action. No automatic retry or caller contact was performed.';
              } finally { busy = false; refresh.disabled = false; }
            }); card.append(control);
          }
          if (['provider_accepted', 'provider_delivered', 'blocked'].indexOf(item.lifecycle_status) >= 0 && item.receipt_status !== 'confirmed_seen') button('I have seen this request', 'receipt_seen', function () { return {}; });
          if (item.receipt_status === 'confirmed_seen' && item.acknowledgement_status !== 'acknowledged') button('Acknowledge this request', 'acknowledge', function () { return {}; });
          if (item.acknowledgement_status === 'acknowledged') {
            if (item.follow_up_status === 'pending') {
              var ownerLabel = element('label', 'Callback owner in your business'), owner = element('input'); owner.type = 'text'; owner.maxLength = 80; ownerLabel.append(owner); card.append(ownerLabel);
              button('Assign callback owner', 'assign_callback', function () { return { assignedTo: owner.value.trim() }; });
            }
            if (item.follow_up_status === 'pending' && typeof item.next_action_owner === 'string' && item.next_action_owner.indexOf('customer_reported:') === 0) button('I started the callback', 'start_callback', function () { return {}; });
            if (item.follow_up_status === 'in_progress') button('I completed the callback', 'complete_callback', function () { return {}; });
            if (item.follow_up_status === 'completed') {
              var dispositionLabel = element('label', 'Business disposition'), disposition = element('select');
              CASE_OUTCOMES.forEach(function (value) { var option = element('option', value.replace(/_/g, ' ')); option.value = value; disposition.append(option); });
              dispositionLabel.append(disposition); card.append(dispositionLabel);
              button('Record disposition', 'resolve', function () { return { outcome: disposition.value }; });
            }
          }
          button('Report an unresolved request', 'unresolved', function () { return { note: note.value.trim() }; });
        }
        cards.append(card);
      });
    }
    async function load() {
      if (busy) return; busy = true; refresh.disabled = true; cards.replaceChildren();
      try { var value = await caseRequest(context, configId, 'list', null, {}, fetcher); render(value.cases);
        status.textContent = value.coverage === 'POSSIBLY_MORE' ? 'Only the latest 20 requests are shown; older requests may exist.' : value.cases.length ? 'Current captured requests verified.' : 'No requests were returned for this bound business. This is not proof that no calls occurred.';
      } catch (_) { status.textContent = 'Customer requests could not be verified. No empty-list or customer outcome is assumed. Refresh this read or recover protected setup access if it expired.'; }
      finally { busy = false; refresh.disabled = false; }
    }
    refresh.addEventListener('click', load);
    return { refresh: load };
  }
  function mount(container, context, options) {
    var doc = container.ownerDocument, fetcher = options && options.fetchImpl || root.fetch.bind(root);
    var current = null, reviewed = false, busy = false;
    container.replaceChildren();
    function element(tag, text) { var e = doc.createElement(tag); if (text) e.textContent = text; return e; }
    var heading = element('h2', 'Review your exact service configuration');
    var intro = element('p', 'Setup answers and payment do not authorize phone changes or go-live. Review the configuration below. Each decision is separate. No forwarding is changed by these controls.');
    var state = element('p', 'Use the button to check the current configuration.'); state.setAttribute('role', 'status');
    var details = element('div'), controls = element('div'), cases = element('div'), progress = element('section');
    progress.setAttribute('aria-label', 'Your service progress');
    var refresh = element('button', 'Check current configuration'); refresh.type = 'button'; refresh.className = 'btn btn-primary';
    container.append(heading, intro, refresh, state, progress, details, controls, cases);
    function showProgress(value) {
      var result = customerProgress(value);
      progress.replaceChildren(element('h3', result.title), element('p', result.detail), element('p', result.basis));
      if (result.trial) progress.append(element('p', result.trial));
    }
    async function load() {
      if (busy) return; busy = true; refresh.disabled = true; cases.replaceChildren(); progress.replaceChildren();
      try {
        var next = await request(context, 'current', null, fetcher);
        showProgress(next);
        if (!next.config_id || !UUID.test(next.config_id) || !/^[a-f0-9]{64}$/.test(next.configuration_sha256)) {
          current = null; details.replaceChildren(); controls.replaceChildren();
          state.textContent = next.state === 'WAITING_CONFIGURATION'
            ? 'Your setup is retained. The configuration owner has not prepared a reviewable version yet. No service was activated.'
            : 'The exact configuration could not be verified. No permission was recorded.';
          return;
        }
        if (!current || current.configuration_sha256 !== next.configuration_sha256 || current.config_id !== next.config_id) reviewed = false;
        current = next; render();
        mountCases(cases, context, next.config_id, fetcher);
        state.textContent = 'Current revision ' + next.version + '. Configuration permission: ' + (next.consent_recorded === true ? 'recorded' : 'not recorded')
          + '. Ongoing service permission: ' + (next.service_authorized === true ? 'recorded' : 'not recorded')
          + '. Customer forwarding confirmation: ' + (next.forwarding_confirmed === true ? 'recorded' : 'not recorded')
          + '. ' + serviceStatus(next);
      } catch (_) { current = null; controls.replaceChildren(); progress.replaceChildren(); state.textContent = valid(context, Date.now())
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
          busy = true; buttons.forEach(function (b) { b.disabled = true; }); refresh.disabled = true; progress.replaceChildren();
          var id = current.config_id, hash = current.configuration_sha256;
          try {
            await request(context, action, id, fetcher);
            var readback = await request(context, 'current', null, fetcher);
            if (readback.config_id !== id || readback.configuration_sha256 !== hash) throw Error('configuration_changed');
            var field = action === 'consent' ? 'consent_recorded' : ['authorize_service', 'revoke_service'].indexOf(action) >= 0 ? 'service_authorized' : 'forwarding_confirmed';
            if (readback[field] !== (action !== 'revoke_service')) throw Error('decision_readback_missing');
            current = readback; render();
            showProgress(readback);
            state.textContent = 'Your exact decision was recorded and independently read back. This does not prove new provider work, call routing or delivery. ' + serviceStatus(readback);
          } catch (_) { current = null; reviewed = false; controls.replaceChildren(); progress.replaceChildren(); state.textContent = 'The decision could not be independently verified. Check the current configuration before trying again; no activation is assumed.'; }
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
  var api = { storageKey: KEY, declaration: DECLARATION, serviceStatus: serviceStatus, customerProgress: customerProgress, valid: valid, stored: stored, recovery: recovery, remember: remember, request: request, mount: mount, caseRequest: caseRequest, mountCases: mountCases };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.TCTCustomerConfigurationReview = api;
})(typeof window !== 'undefined' ? window : globalThis);
