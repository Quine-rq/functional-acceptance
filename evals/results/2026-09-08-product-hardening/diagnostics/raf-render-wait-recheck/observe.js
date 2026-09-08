(() => {
  const events = [];
  function safePath(value) {
    if (!value) return null;
    try {
      const url = new URL(value, location.href);
      if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !['18741','18742'].includes(url.port)) return '[outside-loopback-omitted]';
      const detail = url.searchParams.get('details');
      return url.pathname + (detail && /^[0-9]+$/.test(detail) ? '?details=' + detail : '');
    } catch { return '[unparseable-omitted]'; }
  }
  function state() {
    const f = document.querySelector('turbo-frame#details-modal');
    const dropdowns = [...document.querySelectorAll('ld-confirm-dropdown')];
    const confirm = dropdowns.flatMap(d => [...d.querySelectorAll('button')]).find(b => b.textContent.trim() === 'Confirm');
    return {url_path: safePath(location.href), document_preview: document.documentElement?.hasAttribute('data-turbo-preview') || false, document_aria_busy: document.documentElement?.getAttribute('aria-busy') === 'true', frame_present: !!f, frame_complete: !!f?.complete, complete_attribute: !!f?.hasAttribute('complete'), busy: !!f?.hasAttribute('busy'), aria_busy: f?.getAttribute('aria-busy') === 'true', dropdown_count: dropdowns.length, confirm_present: !!confirm, confirm_visible: !!confirm && !!(confirm.offsetWidth || confirm.offsetHeight || confirm.getClientRects().length)};
  }
  function record(kind, extra = {}) {
    events.push({time_ms: performance.timeOrigin + performance.now(), kind, ...extra, state: state()});
  }
  window.__readonlyProbe = {events, state, mark: name => record('action', {name})};
  for (const name of ['turbo:before-cache', 'turbo:frame-render', 'turbo:frame-load', 'turbo:before-visit', 'turbo:render', 'turbo:load']) {
    document.addEventListener(name, event => {
      if (name.startsWith('turbo:frame-') && event.target?.id !== 'details-modal') return;
      record(name, {phase: 'dispatch', detail_url_path: safePath(event.detail?.url)});
      queueMicrotask(() => record(name, {phase: 'after-dispatch', detail_url_path: safePath(event.detail?.url)}));
    }, true);
  }
  const observer = new MutationObserver(records => {
    for (const change of records) {
      if (change.type === 'attributes' && change.target.matches?.('turbo-frame#details-modal')) {
        record('frame.attribute', {attribute: change.attributeName});
      }
      for (const [name, nodes] of [['dropdown.added', change.addedNodes], ['dropdown.removed', change.removedNodes]]) {
        for (const node of nodes || []) {
          const count = Number(!!node.matches?.('ld-confirm-dropdown')) + (node.querySelectorAll?.('ld-confirm-dropdown').length || 0);
          if (count) record(name, {count});
        }
      }
    }
  });
  observer.observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['complete', 'busy', 'aria-busy']});

  let injectionUsed = false;
  document.addEventListener('turbo:frame-load', event => {
    if (injectionUsed || event.target?.id !== 'details-modal' || !event.target.querySelector('ld-details-modal[data-bookmark-id="14"]')) return;
    injectionUsed = true;
    const originalRAF = window.requestAnimationFrame;
    const originalCancel = window.cancelAnimationFrame;
    let matched = false;
    let passedThrough = 0;
    const target = {bundle_sha256: 'b3bd8d18e0e05750a2440bf6b33ebdb3769422a134bbc7db5d13c342fb0b85f9', line: 19, start_column: 11228, end_column: 11258, callback_source: '()=>e()'};
    function safeStack() {
      return (new Error().stack || '').split('\n').flatMap(line => {
        const m = line.match(/\(?((?:http:\/\/127\.0\.0\.1:18741)\/[^\s)]+):([0-9]+):([0-9]+)\)?$/);
        if (!m) return [];
        try {
          const url = new URL(m[1]);
          if (url.hostname !== '127.0.0.1' || url.port !== '18741' || !url.pathname.endsWith('/bundle.js')) return [];
          return [{source_path: url.pathname, line: Number(m[2]), column: Number(m[3]), function_name: line.slice(0,line.indexOf(m[1])).replace(/^\s*at\s*/,'').replace(/\($/,'').trim()}];
        } catch { return []; }
      });
    }
    record('injection.armed', {delay_ms: 150, target_callsite: target});
    function wrappedRAF(callback) {
      const source = String(callback);
      const stack = safeStack();
      const callsite = stack.find(frame => frame.line === target.line && frame.column >= target.start_column && frame.column <= target.end_column);
      if (source !== target.callback_source || !callsite) {
        passedThrough += 1;
        record('injection.passthrough', {candidate_number: passedThrough, callback_source: source === target.callback_source ? source : '[nonmatching callback body omitted]', registration_stack: stack});
        return originalRAF.call(window, callback);
      }
      matched = true;
      window.requestAnimationFrame = originalRAF;
      record('injection.matched', {delay_ms: 150, callback_source: source, matched_callsite: callsite, registration_stack: stack, passed_through: passedThrough, raf_restored: window.requestAnimationFrame === originalRAF});
      let timer = null;
      let delivered = false;
      const restoreCancel = () => {
        if (window.cancelAnimationFrame === pairedCancel) window.cancelAnimationFrame = originalCancel;
      };
      const handle = originalRAF.call(window, timestamp => {
        record('injection.original_callback_due', {raf_timestamp: timestamp});
        timer = setTimeout(() => {
          delivered = true;
          restoreCancel();
          record('injection.delivered', {delay_ms: 150, raf_restored: window.requestAnimationFrame === originalRAF, cancel_restored: window.cancelAnimationFrame === originalCancel});
          callback.call(window, timestamp);
        }, 150);
      });
      function pairedCancel(request) {
        if (request === handle && !delivered) {
          if (timer !== null) clearTimeout(timer);
          restoreCancel();
          record('injection.cancelled', {cancel_restored: window.cancelAnimationFrame === originalCancel});
        }
        return originalCancel.call(window, request);
      }
      window.cancelAnimationFrame = pairedCancel;
      return handle;
    }
    window.requestAnimationFrame = wrappedRAF;
    window.__readonlyProbe.restoreInjection = () => {
      if (window.requestAnimationFrame === wrappedRAF) {
        window.requestAnimationFrame = originalRAF;
        record('injection.unmatched_restored', {matched, passed_through: passedThrough, raf_restored: true});
      }
    };
  }, true);

})();
