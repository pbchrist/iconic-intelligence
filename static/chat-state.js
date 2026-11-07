/* Per-tab workspace history. Keeps private demo chats separate and restores on reload. */
(function (root) {
  'use strict';
  const PREFIX = 'iconic.chat.v1.';
  const MAX_HISTORY = 20;
  const MAX_HTML_BYTES = 180000;
  function clean(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const history = Array.isArray(raw.history) ? raw.history.slice(-MAX_HISTORY)
      .filter((x) => x && typeof x.q === 'string' && typeof x.a === 'string')
      .map((x) => ({ q: x.q.slice(0, 600), a: x.a.slice(0, 12000) })) : [];
    const html = typeof raw.html === 'string' && raw.html.length <= MAX_HTML_BYTES ? raw.html : '';
    const sources = raw.sources && typeof raw.sources === 'object' && !Array.isArray(raw.sources) ? raw.sources : {};
    return { history, html, sources, answers: Math.max(0, Math.min(10000, Number(raw.answers) || 0)), picked: !!raw.picked };
  }
  function load(storage, workspace) {
    if (!storage || !/^[a-z0-9_-]{1,60}$/i.test(workspace || '')) return null;
    try {
      const raw = storage.getItem(PREFIX + workspace);
      return raw ? clean(JSON.parse(raw)) : null;
    } catch { return null; }
  }
  function save(storage, workspace, state) {
    if (!storage || !/^[a-z0-9_-]{1,60}$/i.test(workspace || '')) return false;
    const payload = clean(state);
    if (!payload) return false;
    try { storage.setItem(PREFIX + workspace, JSON.stringify(payload)); return true; }
    catch { return false; }
  }
  const api = { load, save, clean };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.IconicChatState = api;
})(typeof window === 'undefined' ? globalThis : window);
