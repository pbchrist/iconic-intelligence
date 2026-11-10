/* ICONIC Reserve page: copy buttons, tabs, section tracking, live tool list and live tests.
 * Every result shown comes from the public Reserve gateway. The page holds no credentials.
 * Analytics events carry only the kind of action and whether it worked, never what was typed.
 */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const script = document.currentScript || $('script[data-gateway]');
  let GATEWAY = (script && script.dataset.gateway || '').replace(/\/$/, '');
  // Local checks only: allow pointing the page at a local gateway.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) {
    const override = new URLSearchParams(location.search).get('gateway');
    if (override && /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/.*)?$/.test(override)) GATEWAY = override.replace(/\/$/, '');
  }
  const track = (name, params) => { try { if (typeof window.gtag === 'function') window.gtag('event', name, params || {}); } catch (e) {} };
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>'"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));

  /* ---------- Copy buttons ---------- */
  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
      document.body.appendChild(ta); ta.select();
      let ok = false; try { ok = document.execCommand('copy'); } catch (err) {}
      ta.remove(); return ok;
    }
  }
  document.addEventListener('click', async (event) => {
    const btn = event.target.closest('.rv-copy');
    if (!btn) return;
    let text = btn.dataset.copy;
    if (!text && btn.dataset.copyFrom === 'prev') { const pre = btn.previousElementSibling; text = pre ? pre.textContent : ''; }
    if (!text) return;
    const ok = await copyText(text.trim());
    const label = btn.textContent;
    btn.textContent = ok ? 'Copied' : 'Press ⌘C';
    btn.classList.toggle('is-done', ok);
    let live = $('#rvCopyLive');
    if (!live) { live = document.createElement('div'); live.id = 'rvCopyLive'; live.className = 'rv-sr'; live.setAttribute('aria-live', 'polite'); document.body.appendChild(live); }
    live.textContent = ok ? 'Copied to clipboard' : 'Copy failed. Select the text and copy it manually.';
    track('reserve_copy', { item: btn.getAttribute('aria-label') || 'copy' });
    clearTimeout(btn._t);
    btn._t = setTimeout(() => { btn.textContent = label === 'Copied' || label === 'Press ⌘C' ? 'Copy' : label; btn.classList.remove('is-done'); }, 1800);
  });

  /* ---------- Tabs (ARIA tablist, arrow keys) ---------- */
  $$('[role="tablist"]').forEach((list) => {
    const tabs = $$('[role="tab"]', list);
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        const panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(tab, false));
      tab.addEventListener('keydown', (e) => {
        let next = null;
        if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') next = tabs[0];
        else if (e.key === 'End') next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
  });

  /* ---------- Section tracking for header nav, rail and chips ---------- */
  const sectionIds = ['overview', 'quickstart', 'tools', 'try', 'services', 'privacy', 'faq'];
  const navLinks = $$('.nav a[href^="#"], .rv-rail a[href^="#"], .rv-chipnav a[href^="#"]');
  const chipNav = $('.rv-chipnav');
  let lastActive = '';
  function updateActive() {
    const line = Math.min(220, window.innerHeight * 0.32);
    let active = '';
    sectionIds.forEach((id) => {
      const el = document.getElementById(id); if (!el) return;
      const r = el.getBoundingClientRect();
      if (r.top <= line) active = id;
    });
    const docs = $('.rv-docs');
    if (docs && docs.getBoundingClientRect().bottom < line) active = '';
    navLinks.forEach((a) => {
      const on = a.getAttribute('href') === '#' + active;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    if (active !== lastActive && chipNav) {
      const chip = $('a[href="#' + active + '"]', chipNav);
      if (chip) chipNav.scrollTo({ left: chip.offsetLeft - 16, behavior: 'smooth' });
      lastActive = active;
    }
  }
  window.addEventListener('scroll', updateActive, { passive: true });
  window.addEventListener('resize', updateActive, { passive: true });
  updateActive();

  /* ---------- Network helper ---------- */
  async function call(path, options = {}, timeoutMs = 15000) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    const started = performance.now();
    try {
      const res = await fetch(GATEWAY + path, { ...options, signal: ctrl.signal, cache: 'no-store', credentials: 'omit', mode: 'cors' });
      const ms = Math.round(performance.now() - started);
      let data = null;
      try { data = await res.json(); } catch (e) { data = null; }
      return { ok: res.ok, status: res.status, data, ms };
    } catch (err) {
      return { ok: false, status: 0, data: null, ms: Math.round(performance.now() - started), error: err && err.name === 'AbortError' ? 'timeout' : 'network' };
    } finally { clearTimeout(timer); }
  }
  function errorHtml(r) {
    let title = 'Something went wrong', body = 'The server answered with an error. Nothing was charged and nothing was stored.';
    if (!navigator.onLine) { title = 'You are offline'; body = 'Reconnect to the internet and try again.'; }
    else if (r.error === 'timeout') { title = 'The server took too long'; body = 'No answer within 15 seconds. It runs on one machine in Seattle; try again in a moment.'; }
    else if (r.status === 0) { title = 'Couldn\'t reach the Reserve server'; body = 'Your browser couldn\'t get a response. The server may be restarting, or a network or browser setting is blocking it. Your agent can still connect with the endpoint above.'; }
    else if (r.status === 429) { title = 'Rate limit reached'; body = 'This server limits how often each visitor can run tests. Wait a minute and try again.'; }
    else if (r.status === 400 && r.data && r.data.detail) { title = 'The server rejected the input'; body = r.data.detail; }
    else if (r.status === 413) { title = 'Too much text'; body = 'Shorten your answers and try again.'; }
    else if (r.status) { body = 'HTTP ' + r.status + '. ' + body; }
    return '<div class="rv-error" role="alert"><strong>' + esc(title) + '</strong>' + esc(body) + '</div>';
  }
  const setPill = (el, state, text) => { if (!el) return; el.dataset.state = state; const s = el.querySelector('span'); if (s) s.textContent = text; };

  /* ---------- Live tool list + status ---------- */
  const typeOf = (p) => {
    if (!p) return 'any';
    if (p.type === 'array') return (p.items && p.items.type ? p.items.type : 'any') + '[]';
    if (p.type) return p.type;
    if (Array.isArray(p.anyOf)) return p.anyOf.map((x) => x.type === 'array' ? (x.items && x.items.type || 'any') + '[]' : x.type).filter((t) => t && t !== 'null').join(' | ') + ' (optional)';
    return 'any';
  };
  function renderTools(doc, source) {
    const tools = Array.isArray(doc && doc.tools) ? doc.tools : [];
    const groups = [
      { title: 'Discover & assess', note: 'Read-only', items: tools.filter((t) => !/^reserve_sandbox_/.test(t.name)) },
      { title: 'Your agent\'s sandbox', note: 'Fictional data · 1 hour', items: tools.filter((t) => /^reserve_sandbox_/.test(t.name)) }
    ];
    const wrap = $('#toolGroups');
    wrap.innerHTML = groups.map((g) => '<div class="rv-tool-group"><header><h3>' + esc(g.title) + '</h3><span>' + g.items.length + ' TOOLS · ' + esc(g.note.toUpperCase()) + '</span></header>' +
      g.items.map((t) => {
        const props = (t.input_schema && t.input_schema.properties) || {};
        const req = new Set((t.input_schema && t.input_schema.required) || []);
        const keys = Object.keys(props);
        const params = keys.length ? keys.map((k) => '<div><dt>' + esc(k) + '</dt><dd>' + esc(typeOf(props[k])) + (req.has(k) ? ' · <b>required</b>' : '') + '</dd></div>').join('') : '<div class="rv-none">No arguments.</div>';
        return '<details class="rv-tool"><summary><code>' + esc(t.name) + '</code><span>' + esc(t.description || '') + '</span><i>' + (keys.length ? keys.length + (keys.length === 1 ? ' ARG' : ' ARGS') : 'NO ARGS') + '</i></summary><dl class="rv-params">' + params + '</dl></details>';
      }).join('') + '</div>').join('');
    const when = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    $('#toolMeta').innerHTML = source === 'live'
      ? '<span class="rv-badge live">LIVE FROM SERVER</span><span>' + tools.length + ' tools, loaded at ' + esc(when) + ' from <a href="' + esc(GATEWAY) + '/agents/schemas.json" class="rv-link">schemas.json</a></span>'
      : '<span class="rv-badge synthetic">SAVED COPY · ' + esc(doc.snapshot_taken || '') + '</span><span>The live server didn\'t answer, so this is the last published list. <a href="https://patrick-beastmaster.tailf32530.ts.net/reserve/agents/schemas.json">Open the live file</a></span>';
    return tools.length;
  }
  async function loadTools() {
    const statusPill = $('#statusPill'), tryPill = $('#tryPill');
    const r = await call('/agents/schemas.json', {}, 10000);
    if (r.ok && r.data && Array.isArray(r.data.tools)) {
      const n = renderTools(r.data, 'live');
      $('#statTools').textContent = String(n);
      setPill(statusPill, 'ok', 'ONLINE');
      setPill(tryPill, 'ok', 'SERVER ONLINE');
      $('#statusNote').textContent = 'Checked just now: the server answered with ' + n + ' tools and a ' + r.ms + ' ms round trip.';
      return;
    }
    setPill(statusPill, 'err', navigator.onLine ? 'NO ANSWER' : 'OFFLINE');
    setPill(tryPill, 'err', navigator.onLine ? 'SERVER NOT ANSWERING' : 'YOU ARE OFFLINE');
    $('#statTools').textContent = '16 (saved)';
    $('#statusNote').textContent = navigator.onLine
      ? 'Your browser couldn\'t reach the live server just now. Agents connect directly, so this check can fail while the endpoint still works.'
      : 'You are offline.';
    try {
      const snap = await fetch('/agents/reserve/tools-snapshot.json', { cache: 'no-store' }).then((x) => x.json());
      renderTools(snap, 'snapshot');
    } catch (e) { $('#toolMeta').textContent = 'The tool list could not be loaded.'; }
  }
  loadTools();

  /* ---------- Free assessment ---------- */
  const examples = {
    dealer: { business_type: 'Independent auto dealership', systems: 'Inventory, Pricing history, Sales records', problem: 'We reprice used trucks every week but can\'t tell which price moves actually sold them faster.', recurring_workflow: 'Weekly competitor pricing review', measurable_outcome: 'Days to sale and front-end gross per vehicle', existing_memory: false, sensitive_data: false },
    law: { business_type: 'Employment litigation firm, 20 lawyers', systems: 'Matter management, Brief bank, Billing', problem: 'Associates rebuild arguments from scratch because nobody can find how similar motions turned out.', recurring_workflow: 'Monday review of open matters and motion strategy', measurable_outcome: 'Motion outcomes and hours spent per brief', existing_memory: true, sensitive_data: true },
    accounting: { business_type: 'Owner-run accounting firm, 14 people', systems: 'Tax software, Client workpapers, Engagement letters', problem: 'We give the same planning advice every year with no record of which advice actually saved clients money.', recurring_workflow: 'Quarterly tax planning review per client', measurable_outcome: 'Estimated tax saved versus prior year', existing_memory: false, sensitive_data: true }
  };
  const form = $('#assessForm');
  $$('.rv-example').forEach((b) => b.addEventListener('click', () => {
    const ex = examples[b.dataset.example]; if (!ex || !form) return;
    Object.entries(ex).forEach(([k, v]) => { const el = form.elements[k]; if (!el) return; if (el.type === 'checkbox') el.checked = v; else el.value = v; el.removeAttribute('aria-invalid'); });
    track('reserve_example', { example: b.dataset.example });
  }));

  const limits = { business_type: 100, problem: 800, recurring_workflow: 500, measurable_outcome: 300 };
  function readForm() {
    const f = form.elements, errors = [];
    const body = {};
    Object.keys(limits).forEach((k) => {
      const v = f[k].value.trim();
      f[k].removeAttribute('aria-invalid');
      if (!v) { errors.push(f[k]); } else if (v.length > limits[k]) { errors.push(f[k]); }
      body[k] = v;
    });
    const systems = [...new Set(f.systems.value.split(',').map((s) => s.trim()).filter(Boolean))];
    f.systems.removeAttribute('aria-invalid');
    if (systems.length < 1 || systems.length > 8 || systems.some((s) => s.length > 90)) errors.push(f.systems);
    body.systems = systems;
    body.existing_memory = !!f.existing_memory.checked;
    body.sensitive_data = !!f.sensitive_data.checked;
    return { body, errors };
  }
  const human = {
    PILOT_CANDIDATE: 'A good fit for a first pilot.',
    PILOT_CANDIDATE_PRIVATE_DEPLOYMENT: 'A fit, on a private deployment only.',
    NOT_A_FIT: 'Not a fit yet.'
  };
  function list(items) { return '<ul>' + (items || []).map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul>'; }
  function renderAssessment(d, ms) {
    const brief = d.brief_for_human || {}, pilot = d.recommended_first_pilot || {}, tx = d.transaction || {};
    const no = d.fit_status === 'NOT_A_FIT';
    let html = '<div class="rv-out"><div class="rv-out-head">' +
      '<div class="rv-meta"><span class="rv-badge live">LIVE RESPONSE</span><span>' + esc(ms) + ' ms</span><span>status <code>' + esc(tx.status || '') + '</code></span><span>charged <code>$' + esc(((tx.amount_charged_cents || 0) / 100).toFixed(2)) + '</code></span><span>id <code>' + esc(tx.transaction_id || '') + '</code></span></div>' +
      '<p class="rv-verdict' + (no ? ' no' : '') + '">' + esc(human[d.fit_status] || d.fit_status) + '</p>' +
      '<p class="rv-small" style="margin:0">' + esc(brief.headline || '') + ' <code>' + esc(d.fit_status) + '</code></p></div><div class="rv-out-grid">';
    html += '<section><h4>' + (no ? 'What\'s missing' : 'Why') + '</h4>' + list(d.fit_reasons) + '</section>';
    html += '<section><h4>Recommended next step</h4><p>' + esc(brief.recommended_action || d.suggested_next_step || '') + '</p></section>';
    if (!no) {
      html += '<section class="rv-span"><h4>Your first pilot</h4><dl>' +
        [['Workflow', pilot.workflow], ['Measure', pilot.outcome_metric], ['Start from', (pilot.sources || []).join(', ')], ['Baseline first', pilot.baseline], ['How it\'s verified', pilot.verification], ['How we prove it helps', pilot.comparison]]
          .filter((x) => x[1]).map((x) => '<div><dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd></div>').join('') + '</dl></section>';
    }
    html += '<section><h4>Controls before any real data</h4>' + list(d.required_controls) + '</section>';
    html += '<section><h4>What a person must approve</h4>' + list(brief.human_authorization_required) + '</section>';
    html += '<section class="rv-span"><h4>Data handling</h4><p>' + esc(brief.private_data_handling || '') + ' ' + esc(d.not_collected || '') + ' Retention: <code>' + esc(tx.record_retention || '') + '</code>.</p></section>';
    html += '</div><details class="rv-raw"><summary>Raw JSON from the server</summary><pre>' + esc(JSON.stringify(d, null, 2)) + '</pre></details></div>';
    return html;
  }
  if (form) form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#assessBtn'), out = $('#assessOut');
    if (btn.getAttribute('aria-busy') === 'true') return;
    const { body, errors } = readForm();
    if (errors.length) {
      errors.forEach((el) => el.setAttribute('aria-invalid', 'true'));
      errors[0].focus();
      out.innerHTML = '<div class="rv-error" role="alert"><strong>Fill in every field</strong>Each answer needs a few words. "Where the history lives" takes 1 to 8 items, separated by commas.</div>';
      return;
    }
    btn.setAttribute('aria-busy', 'true'); btn.textContent = 'ASSESSING…';
    out.innerHTML = '';
    const r = await call('/agents/evaluate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    btn.removeAttribute('aria-busy'); btn.textContent = 'RUN FREE ASSESSMENT';
    if (r.ok && r.data && r.data.transaction && r.data.fit_status) {
      out.innerHTML = renderAssessment(r.data, r.ms);
      track('reserve_try', { kind: 'assessment', outcome: 'ok' });
    } else {
      out.innerHTML = errorHtml(r);
      track('reserve_try', { kind: 'assessment', outcome: 'error', status: r.status });
    }
    out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  /* ---------- Synthetic demo ---------- */
  function renderDemo(d, ms) {
    const before = d.before_authorized_verification || {}, after = d.after_authorized_verification || {};
    const chain = (after.chains || [])[0] || {};
    const action = (chain.actions || [])[0] || {};
    const outcome = (action.outcomes || [])[0] || {};
    const mem = (d.source_memory || []).find((m) => m.type === 'memory') || {};
    const out = d.outcome_reported || {};
    let html = '<div class="rv-out"><div class="rv-out-head">' +
      '<div class="rv-meta"><span class="rv-badge synthetic">SYNTHETIC · FICTIONAL DATA</span><span class="rv-badge live">LIVE ENGINE</span><span>' + esc(ms) + ' ms</span><span>mode <code>' + esc(d.mode || '') + '</code></span></div>' +
      '<p class="rv-verdict">One decision, traced from evidence to verified outcome.</p>' +
      '<p class="rv-small" style="margin:0">' + esc(d.execution || '') + '</p></div><div class="rv-out-grid">';
    html += '<section class="rv-span"><h4>The chain the Reserve recorded</h4><ol class="rv-chain">' +
      '<li class="done"><b>Evidence</b><span>' + esc(mem.content || '') + '</span><small>' + esc(mem.source_ref || '') + '</small></li>' +
      '<li class="done"><b>Decision</b><span>' + esc(chain.recommendation || d.recommendation || '') + '</span><small>baseline: ' + esc(chain.baseline || '') + '</small></li>' +
      '<li class="done"><b>Action</b><span>' + esc(action.summary || d.observed_action || '') + '</span><small>' + esc(action.evidence_ref || '') + '</small></li>' +
      '<li class="done"><b>Outcome</b><span>' + esc(outcome.metric || out.metric || '') + ': ' + esc(outcome.metric_value != null ? outcome.metric_value : out.value) + ' ' + esc(outcome.metric_unit || out.unit || '') + (outcome.baseline_value != null ? ', against a baseline of ' + esc(outcome.baseline_value) : '') + '</span><small>' + esc(outcome.evidence_ref || '') + '</small></li>' +
      '<li class="done"><b>Verified</b><span>By a separate reviewer key, not the agent that made the call.</span><small>' + esc(outcome.verification_status || '') + ' · ' + esc(outcome.verification_method || '') + '</small></li>' +
      '</ol></section>';
    html += '<section class="rv-span"><h4>Before vs. after verification</h4><div class="rv-compare">' +
      '<div><small>Before</small><strong>' + esc(before.operator_verified != null ? before.operator_verified : '–') + ' / ' + esc(before.outcome_records_examined != null ? before.outcome_records_examined : '–') + '</strong><span>outcomes verified · ' + esc(before.reported_only || 0) + ' reported only</span></div>' +
      '<div><small>After</small><strong>' + esc(after.operator_verified != null ? after.operator_verified : '–') + ' / ' + esc(after.outcome_records_examined != null ? after.outcome_records_examined : '–') + '</strong><span>outcomes verified · causal claim: ' + esc(String(after.causal_claim)) + '</span></div>' +
      '</div></section>';
    html += '<section class="rv-span"><h4>Read this before quoting it</h4><p>' + esc(d.verification_caveat || '') + '</p></section>';
    html += '</div><details class="rv-raw"><summary>Raw JSON from the server</summary><pre>' + esc(JSON.stringify(d, null, 2)) + '</pre></details></div>';
    return html;
  }
  const demoBtn = $('#demoBtn');
  if (demoBtn) demoBtn.addEventListener('click', async () => {
    const out = $('#demoOut');
    if (demoBtn.getAttribute('aria-busy') === 'true') return;
    demoBtn.setAttribute('aria-busy', 'true'); demoBtn.textContent = 'RUNNING…';
    out.innerHTML = '';
    const r = await call('/agents/demo');
    demoBtn.removeAttribute('aria-busy'); demoBtn.textContent = 'RUN IT AGAIN';
    if (r.ok && r.data && r.data.mode) {
      out.innerHTML = renderDemo(r.data, r.ms);
      track('reserve_try', { kind: 'demo', outcome: 'ok' });
    } else {
      out.innerHTML = errorHtml(r);
      track('reserve_try', { kind: 'demo', outcome: 'error', status: r.status });
    }
  });
})();
