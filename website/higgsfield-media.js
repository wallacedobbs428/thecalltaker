(function() {
  var slots = Array.prototype.slice.call(document.querySelectorAll('[data-higgsfield-slot]'));
  function failClosed(slot) {
    slot.replaceChildren();
    slot.hidden = true;
    slot.classList.remove('is-approved');
    var container = slot.closest('[data-higgsfield-container]');
    if (container) container.classList.remove('has-approved-higgsfield');
  }
  slots.forEach(failClosed);
  if (!slots.length) return;

  fetch('/assets/higgsfield/approved-assets.json', { cache: 'no-store' })
    .then(function(response) {
      if (!response.ok) throw new Error('Higgsfield manifest unavailable');
      return response.json();
    })
    .then(function(manifest) {
      if (manifest.schema_version !== 'tct_higgsfield_website_asset_manifest.v1') return;
      var assets = Array.isArray(manifest.assets) ? manifest.assets : [];
      var bindings = Array.isArray(manifest.slots) ? manifest.slots : [];

      slots.forEach(function(slot) {
        var binding = bindings.find(function(item) { return item.slot_id === slot.dataset.higgsfieldSlot; });
        var asset = binding && binding.asset_id ? assets.find(function(item) { return item.asset_id === binding.asset_id; }) : null;
        var src = asset && typeof asset.website_src === 'string' ? asset.website_src : '';
        var approved = asset && asset.approval_status === 'approved';
        var originOk = asset && asset.origin === 'higgsfield';
        var qaOk = asset && asset.qa_status === 'pass';
        var familyOk = asset && binding && asset.capability_family === binding.capability_family && asset.capability_family === slot.dataset.capabilityFamily;
        var hashOk = asset && /^[a-f0-9]{64}$/i.test(asset.sha256 || '');
        var srcOk = /^\/assets\/higgsfield\/published\/[a-z0-9._-]+\.(mp4|webm)$/i.test(src);
        if (!approved || !originOk || !qaOk || !familyOk || !hashOk || !srcOk) {
          failClosed(slot);
          return;
        }

        var video = document.createElement('video');
        video.src = src;
        video.playsInline = true;
        video.preload = 'metadata';
        video.setAttribute('aria-label', asset.accessible_label || 'Higgsfield-produced visual');
        if (binding.playback === 'controls') {
          video.controls = true;
        } else {
          video.autoplay = true;
          video.muted = true;
          video.loop = true;
        }
        video.addEventListener('error', function() { failClosed(slot); });
        slot.replaceChildren(video);
        slot.hidden = false;
        slot.classList.add('is-approved');
        var container = slot.closest('[data-higgsfield-container]');
        if (container) container.classList.add('has-approved-higgsfield');
      });
    })
    .catch(function() { slots.forEach(failClosed); });
})();
