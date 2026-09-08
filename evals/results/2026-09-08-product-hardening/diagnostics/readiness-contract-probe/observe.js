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
})();
