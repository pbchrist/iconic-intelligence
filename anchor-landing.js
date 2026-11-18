// Lands section links (#live, #proof, ...) with the section's heading just below the fixed header,
// and keeps it there while late content above it (fonts, live counters) finishes loading.
(function () {
  var GAP = 24;
  function header() { return document.querySelector('.site-header'); }
  // Layout position, ignoring reveal animations that shift elements with transforms.
  function docTop(el) { var y = 0; while (el) { y += el.offsetTop; el = el.offsetParent; } return y; }
  function land(id, smooth) {
    var t = document.getElementById(id); if (!t || id === 'top') return false;
    var k = t.querySelector('.section-kicker, h2') || t;
    var h = header(); var hb = h ? h.getBoundingClientRect().bottom : 0;
    var y = docTop(k) - hb - GAP;
    window.scrollTo({ top: Math.max(0, y), behavior: smooth ? 'smooth' : 'instant' });
    return true;
  }
  var userMoved = false;
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (ev) {
    window.addEventListener(ev, function () { userMoved = true; }, { passive: true, once: true });
  });
  function holdOnHash() {
    var id = decodeURIComponent(location.hash.slice(1)); if (!id || !document.getElementById(id)) return;
    land(id, false);
    // Late content above the target (fonts, the live counter, the browser's own jump) can move it; hold it in place
    // for a few seconds unless the visitor starts scrolling.
    var until = Date.now() + 8000;
    (function hold() { if (userMoved || Date.now() > until) return; land(id, false); setTimeout(hold, 120); })();
  }
  if (location.hash) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    if (document.readyState === 'complete') holdOnHash(); else window.addEventListener('load', holdOnHash);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!userMoved && location.hash) land(decodeURIComponent(location.hash.slice(1)), false); });
  }
  window.addEventListener('hashchange', function () { var id = decodeURIComponent(location.hash.slice(1)); if (id) land(id, false); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="#"]'); if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin || u.pathname !== location.pathname || !u.hash) return;
    var id = decodeURIComponent(u.hash.slice(1));
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (land(id, !reduce)) { e.preventDefault(); history.pushState(null, '', u.hash); }
  });
})();
