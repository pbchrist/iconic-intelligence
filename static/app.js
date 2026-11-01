(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (n) => Number(n || 0).toLocaleString('en-US');
  const store = { get(k) { try { return localStorage.getItem(k); } catch { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch {} } };

  const S = { ws: store.get('iconic.ws') || '', status: null, workspace: null, feed: null, jobs: [], tab: 'ask', history: [], busy: false, folder: 'all', picked: false, asked: new Set(), revealed: '' };
  const EMBED = /[?&]embed=1/.test(location.search);
  if (EMBED) document.body.classList.add('embed');
  const TITLES = { ask: 'ASK THE BUSINESS', intel: 'INTELLIGENCE', work: 'WORK', knowledge: 'KNOWLEDGE', control: 'CONTROL' };

  // ---------- atmosphere
  addEventListener('pointermove', (e) => { document.documentElement.style.setProperty('--mx', e.clientX + 'px'); document.documentElement.style.setProperty('--my', e.clientY + 'px'); }, { passive: true });
  function tickClock() {
    const d = new Date();
    $('#clock').textContent = d.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }).toUpperCase() + ' · ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }
  tickClock(); setInterval(tickClock, 15000);

  function countUp(el, to, suffix = '') {
    const from = Number(el.dataset.v || 0); el.dataset.v = to;
    if (from === to) { el.textContent = fmt(to) + suffix; return; }
    const t0 = performance.now(), dur = 900;
    const step = (t) => { const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3); el.textContent = fmt(Math.round(from + (to - from) * e)) + suffix; if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }

  async function api(path, opts) { const r = await fetch(path, opts); if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || r.statusText); return r.json(); }

  // ---------- tabs
  function setTab(t) {
    S.tab = t;
    $$('.tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === t));
    $$('.panel').forEach((p) => p.classList.toggle('active', p.id === 'panel-' + t));
    $('#panelTitle').textContent = TITLES[t];
    if (t === 'work') loadJobs();
    if (t === 'intel') loadFeed();
    if (t === 'ask') setTimeout(() => $('#askInput').focus(), 50);
  }
  $$('.tab').forEach((b) => b.addEventListener('click', () => setTab(b.dataset.tab)));

  // ---------- workspace menu
  const chip = $('#wsChip'), menu = $('#wsMenu');
  chip.addEventListener('click', (e) => { e.stopPropagation(); const open = menu.hidden; menu.hidden = !open; chip.setAttribute('aria-expanded', String(open)); });
  document.addEventListener('click', () => { menu.hidden = true; chip.setAttribute('aria-expanded', 'false'); });
  function renderMenu() {
    const list = (S.status && S.status.workspaces) || [];
    const html = list.map((w) => `<button role="option" data-ws="${esc(w.id)}" aria-selected="${w.id === S.ws}"><span class="ws-avatar">${esc(w.initials || '·')}</span><span><strong>${esc(w.name)}</strong><small>${fmt(w.documents)} documents${w.sample ? ' · sample' : ''}</small></span></button>`).join('');
    if (menu.dataset.html === html) return;
    menu.dataset.html = html; menu.innerHTML = html;
    $$('button', menu).forEach((b) => b.addEventListener('click', () => switchWs(b.dataset.ws)));
  }
  function switchWs(id) {
    if (id === S.ws) { S.picked = true; renderHello(); return; }
    S.ws = id; store.set('iconic.ws', id); S.history = []; S.feed = null; S.folder = 'all'; S.picked = true; S.revealed = ''; S.asked = new Set();
    $$('.turn', $('#convo')).forEach((t) => t.remove());
    $('#hello').hidden = false;
    loadWorkspace(); loadFeed();
  }

  // ---------- status
  async function loadStatus() {
    try {
      const s = await api('/api/status'); S.status = s;
      if (!S.ws || !s.workspaces.find((w) => w.id === S.ws)) { S.ws = s.workspaces[0] ? s.workspaces[0].id : ''; }
      const m = s.model;
      $('#healthDot').className = 'dot ' + (m.online ? 'on' : 'off');
      $('#healthText').textContent = m.online ? 'LOCAL MODEL ONLINE' : 'MODEL OFFLINE';
      $('#healthModel').textContent = m.online ? m.model : (m.error || 'Start your model server');
      $('#meterTokens').textContent = fmt(s.tokens) + ' tokens';
      $('#tpsPill').textContent = s.tokens_per_second ? s.tokens_per_second + ' TOK/S' : '—';
      $('#routePill').textContent = m.private ? 'LOCAL' : 'REMOTE';
      $('#outPill').textContent = m.private ? '0 BYTES' : 'CHECK ROUTE';
      $('#cHost').textContent = s.host;
      $('#cModel').textContent = m.online ? m.model : 'Offline';
      $('#cEndpoint').textContent = m.endpoint || '—';
      $('#cPrivate').textContent = m.private ? 'Private. Nothing leaves this network.' : 'Model is not on a private address';
      $('#cTokens').textContent = fmt(s.tokens);
      $('#cQuestions').textContent = fmt(s.questions);
      $('#cTps').textContent = s.tokens_per_second ? s.tokens_per_second + ' tokens/sec' : 'Ask something first';
      const u = s.uptime; $('#cUptime').textContent = u > 86400 ? Math.floor(u / 86400) + ' days' : u > 3600 ? Math.floor(u / 3600) + ' hours' : Math.max(1, Math.floor(u / 60)) + ' min';
      renderMenu();
      if (!S.workspace || S.workspace.id !== S.ws) loadWorkspace();
    } catch (e) { $('#healthDot').className = 'dot off'; $('#healthText').textContent = 'SERVER UNREACHABLE'; }
  }

  // ---------- workspace + knowledge
  async function loadWorkspace() {
    if (!S.ws) return;
    const w = await api('/api/workspace?ws=' + encodeURIComponent(S.ws)); S.workspace = w;
    $('#wsAvatar').textContent = w.initials || '·';
    $('#wsName').textContent = w.name;
    $('#wsTag').textContent = (w.tagline || (w.sample ? 'SAMPLE' : 'WORKSPACE')).toUpperCase();
    $('#cntDocs').textContent = w.documents || '';
    renderHello(); renderKnowledge();
  }

  function greeting() { const h = new Date().getHours(); return h < 12 ? 'Good morning.' : h < 18 ? 'Good afternoon.' : 'Good evening.'; }
  function typeInto(el, text, speed = 14) {
    return new Promise((res) => { let i = 0; const t = setInterval(() => { el.textContent = text.slice(0, ++i); if (i >= text.length) { clearInterval(t); res(); } }, speed); });
  }
  function nextQuestions(n) {
    const items = ((S.feed && S.feed.items) || []).slice().sort((a, b) => ['HIGH', 'WATCH', 'OPP', 'NEW'].indexOf(a.severity) - ['HIGH', 'WATCH', 'OPP', 'NEW'].indexOf(b.severity));
    const qs = items.map((i) => i.question).concat((S.workspace && S.workspace.suggestions) || []);
    return [...new Set(qs)].filter((q) => !S.asked.has(q)).slice(0, n);
  }
  function renderHello() {
    const st = S.status, w = S.workspace; if (!st || !w) return;
    $('#helloKicker').textContent = `LIVE · RUNNING ON ${String(st.location || 'this computer').toUpperCase()}`;
    const list = st.workspaces || [];
    if (!S.picked && list.length > 1) {
      $('#helloTitle').innerHTML = 'Pick a business.<br><em>Watch it think.</em>';
      $('#helloSub').innerHTML = 'Each one is a made-up company with real-looking files. A private AI on this machine has read every page. Choose one and see what it found.';
      $('#pick').innerHTML = list.map((x) => `<button type="button" class="pick-card" data-ws="${esc(x.id)}"><span class="ws-avatar">${esc(x.initials || '·')}</span><span><strong>${esc(x.name)}</strong><small>${esc(x.kind || '')}</small><em>${fmt(x.documents)} files${x.developments ? ` · ${x.developments} things need attention` : ''}</em></span><b>→</b></button>`).join('');
      $$('#pick .pick-card').forEach((b) => b.addEventListener('click', () => switchWs(b.dataset.ws)));
      $('#brief').innerHTML = ''; $('#suggest').innerHTML = ''; $('#dare').hidden = true;
      return;
    }
    $('#pick').innerHTML = '';
    $('#helloTitle').textContent = greeting();
    const items = ((S.feed && S.feed.items) || []).slice().sort((a, b) => ['HIGH', 'WATCH', 'OPP', 'NEW'].indexOf(a.severity) - ['HIGH', 'WATCH', 'OPP', 'NEW'].indexOf(b.severity));
    if (!items.length) {
      $('#helloSub').innerHTML = `I'm reading all <b>${fmt(w.documents)} files</b> for <b>${esc(w.name)}</b> and writing the briefing.`;
      const docs = (w.docs || []).map((d) => d.title);
      $('#brief').innerHTML = `<div class="ticker"><span class="shimmer" id="tick">${esc(docs[0] || '')}</span></div>`;
      let i = 0; clearInterval(S.tickT); S.tickT = setInterval(() => { const t = $('#tick'); if (!t) return clearInterval(S.tickT); t.textContent = docs[++i % docs.length] || ''; }, 420);
      $('#suggest').innerHTML = ''; $('#dare').hidden = false;
      return;
    }
    clearInterval(S.tickT);
    $('#helloSub').innerHTML = `I read all <b>${fmt(w.documents)} files</b> for <b>${esc(w.name)}</b>. Here's what needs attention:`;
    const key = w.id + ':' + (S.feed.generated_at || '');
    const top = items.slice(0, 3);
    if (S.revealed !== key) {
      S.revealed = key;
      $('#brief').innerHTML = top.map((it, i) => `<button type="button" class="brief-card" style="animation-delay:${i * 380}ms" data-q="${esc(it.question)}"><span class="sev ${it.severity}">${it.severity}</span><span><strong data-t="${esc(it.title)}"></strong><small>${esc(it.category)}</small></span><b>SHOW ME →</b></button>`).join('');
      (async () => { for (const el of $$('#brief strong')) { await new Promise((r) => setTimeout(r, 250)); await typeInto(el, el.dataset.t); } })();
      $$('#brief .brief-card').forEach((b) => b.addEventListener('click', () => ask(b.dataset.q)));
    }
    const briefQs = new Set(top.map((t) => t.question));
    const more = nextQuestions(8).filter((q) => !briefQs.has(q)).slice(0, 3);
    $('#suggest').innerHTML = more.map((q) => `<button type="button" data-q="${esc(q)}"><small>TRY</small>${esc(q)}</button>`).join('');
    $$('#suggest button').forEach((b) => b.addEventListener('click', () => ask(b.dataset.q)));
    $('#dare').hidden = false;
  }

  function renderKnowledge() {
    const w = S.workspace; if (!w) return;
    countUp($('#sDocs'), w.documents); countUp($('#sPass'), w.passages); countUp($('#sWords'), w.words);
    $('#sTypes').textContent = (w.types || []).map(([t]) => t.toUpperCase()).join(' · ') || '—';
    $('#kSub').textContent = `Everything ${w.name} has given it. Click any document to read it.`;
    const folders = [['all', w.documents]].concat(w.folders || []);
    $('#folders').innerHTML = folders.map(([f, n]) => `<button class="chip ${S.folder === f ? 'on' : ''}" data-f="${esc(f)}">${esc(f === 'all' ? 'All' : f)} · ${n}</button>`).join('');
    $$('#folders .chip').forEach((b) => b.addEventListener('click', () => { S.folder = b.dataset.f; renderKnowledge(); }));
    const docs = (w.docs || []).filter((d) => S.folder === 'all' || d.folder === S.folder);
    $('#docList').innerHTML = docs.map((d) => `<button class="doc" data-id="${d.id}"><span class="ext">${esc(d.ext)}</span><span><strong>${esc(d.title)}</strong><small>${esc(d.rel)}</small></span><b>${esc(d.date)} · ${fmt(d.words)} WORDS</b></button>`).join('') +
      `<div class="drop">To add knowledge, put files in <code>data/${esc(w.id)}/</code> on this computer. Markdown, text, CSV, HTML, Word and PDF all work. It reads new files within ${S.status ? 20 : 20} seconds.</div>`;
    $$('#docList .doc').forEach((b) => b.addEventListener('click', () => openDoc(Number(b.dataset.id))));
  }

  // ---------- feed
  async function loadFeed() {
    if (!S.ws) return;
    try { S.feed = await api('/api/feed?ws=' + encodeURIComponent(S.ws)); } catch { return; }
    renderFeed(); renderHello();
  }
  function ago(ts) { const s = Math.floor(Date.now() / 1000 - ts); return s < 90 ? 'just now' : s < 3600 ? Math.floor(s / 60) + ' min ago' : s < 86400 ? Math.floor(s / 3600) + ' hr ago' : Math.floor(s / 86400) + ' days ago'; }
  function renderFeed() {
    const f = S.feed || {}, items = f.items || [];
    $('#cntIntel').textContent = items.length || '';
    $('#feedRefresh').disabled = f.status === 'running';
    const online = S.status && S.status.model.online;
    if (f.status === 'running' && !items.length) {
      $('#feedSub').textContent = 'The agent is reading the files now.';
      $('#feed').innerHTML = `<div class="waiting"><div class="orb"></div><p>Reading every document and writing the briefing.</p><small>On a local model this takes under a minute. Nothing leaves this computer.</small></div>`;
      return;
    }
    if (!items.length) {
      $('#feedSub').textContent = f.error ? 'The last briefing failed.' : '—';
      $('#feed').innerHTML = `<div class="waiting"><div class="orb"></div><p>${online ? (f.error ? esc(f.error) : 'The briefing will appear here as soon as the agent has read the files.') : 'The local model is offline. Start it and the briefing writes itself.'}</p></div>`;
      return;
    }
    $('#feedSub').textContent = `${f.status === 'running' ? 'Rewriting now · ' : ''}Written ${ago(f.generated_at)} by ${f.model || 'the local model'}, from ${S.workspace ? S.workspace.documents : ''} documents.`;
    $('#feed').innerHTML = items.map((it, i) => `<article class="item" style="animation-delay:${i * 90}ms"><span class="sev ${it.severity}">${it.severity}</span><div><small>${esc(it.category)}</small><h4>${esc(it.title)}</h4><p>${esc(it.detail)}</p><div class="item-foot">${(it.sources || []).map((s) => `<button class="chip" data-doc="${s.id}">◫ ${esc(s.title)}</button>`).join('')}<button class="ask-this" data-q="${esc(it.question)}">ASK ABOUT THIS →</button></div></div></article>`).join('');
    $$('#feed [data-doc]').forEach((b) => b.addEventListener('click', () => openDoc(Number(b.dataset.doc))));
    $$('#feed .ask-this').forEach((b) => b.addEventListener('click', () => { setTab('ask'); ask(b.dataset.q); }));
  }
  $('#feedRefresh').addEventListener('click', async () => { await api('/api/refresh-feed', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ws: S.ws }) }); S.feed = Object.assign({}, S.feed, { status: 'running' }); renderFeed(); });

  // ---------- jobs
  async function loadJobs() {
    try { const j = await api('/api/jobs'); S.jobs = j.jobs; S.scan = j.scan_seconds; } catch { return; }
    const running = S.jobs.filter((j) => j.status === 'running'), done = S.jobs.filter((j) => j.status !== 'running');
    $('#cntWork').textContent = running.length || '';
    $('#nRunning').textContent = running.length; $('#nDone').textContent = done.length;
    const card = (j) => `<div class="job ${j.status}"><small><span>${esc(j.kind)}${j.ws ? ' · ' + esc(j.ws) : ''}</span><span>${new Date(j.started * 1000).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span></small><strong>${esc(j.title)}</strong>${j.status === 'running' ? '<div class="bar"></div>' : `<p>${esc(j.detail || '')}${j.ms != null ? ' · ' + (j.ms / 1000).toFixed(1) + 's' : ''}</p>`}</div>`;
    $('#colRunning').innerHTML = running.map(card).join('') || '<p class="empty">Idle. Ask something, or add a file, and watch it work.</p>';
    $('#colDone').innerHTML = done.slice(0, 12).map(card).join('') || '<p class="empty">Nothing yet.</p>';
    $('#colAlways').innerHTML = `<div class="job always"><small><span>WATCHER</span><span>EVERY ${S.scan || 20}s</span></small><strong>Watch the folders for new or changed files</strong><p>New files are read and indexed automatically.</p></div><div class="job always"><small><span>AGENT</span><span>ON CHANGE</span></small><strong>Rewrite the intelligence briefing</strong><p>Runs whenever the files change.</p></div><div class="job always"><small><span>ROUTE</span><span>ALWAYS</span></small><strong>Answer questions from the files, with sources</strong><p>Local model only. No per-token cost.</p></div>`;
  }

  // ---------- document drawer
  async function openDoc(id, highlight) {
    const d = await api(`/api/doc?ws=${encodeURIComponent(S.ws)}&id=${id}`);
    $('#dTitle').textContent = d.title;
    $('#dMeta').textContent = `${d.rel.toUpperCase()} · ${d.date} · ${fmt(d.words)} WORDS`;
    let body = esc(d.text);
    if (highlight) {
      const h = esc(highlight.trim()).slice(0, 260);
      const idx = body.indexOf(h.slice(0, 120));
      if (idx >= 0) { const end = body.indexOf(h.slice(-40), idx); const stop = end > idx ? end + Math.min(40, h.length) : idx + h.length; body = body.slice(0, idx) + '<mark id="hit">' + body.slice(idx, stop) + '</mark>' + body.slice(stop); }
    }
    $('#dBody').innerHTML = body;
    $('#drawer').classList.add('open'); $('#drawer').setAttribute('aria-hidden', 'false'); $('#scrim').classList.add('on');
    const hit = $('#hit'); $('#dBody').scrollTop = 0; if (hit) setTimeout(() => hit.scrollIntoView({ block: 'center', behavior: 'smooth' }), 250);
  }
  function closeDoc() { $('#drawer').classList.remove('open'); $('#drawer').setAttribute('aria-hidden', 'true'); $('#scrim').classList.remove('on'); }
  $('#dClose').addEventListener('click', closeDoc); $('#scrim').addEventListener('click', closeDoc);
  addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDoc(); });

  // ---------- answers
  function md(text, sources) {
    const lines = esc(text).split('\n'); let html = '', list = null;
    const inline = (s) => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (m, g) => g.split(',').map((n) => { n = n.trim(); const src = sources.find((x) => String(x.n) === n); return src ? `<button class="cite" data-n="${n}" title="${esc(src.title)}">${n}</button>` : `[${n}]`; }).join(''));
    for (const raw of lines) {
      const l = raw.trim();
      const b = l.match(/^[-*•]\s+(.*)/), o = l.match(/^\d+[.)]\s+(.*)/);
      if (b || o) { const tag = b ? 'ul' : 'ol'; if (list !== tag) { if (list) html += `</${list}>`; html += `<${tag}>`; list = tag; } html += `<li>${inline((b || o)[1])}</li>`; continue; }
      if (list) { html += `</${list}>`; list = null; }
      if (l) html += `<p>${inline(l.replace(/^#+\s*/, ''))}</p>`;
    }
    if (list) html += `</${list}>`;
    return html || '<p></p>';
  }

  async function ask(q) {
    q = (q || '').trim(); if (!q || S.busy || !S.ws) return;
    S.busy = true; S.picked = true; S.asked.add(q); $('#askBtn').disabled = true; $('#askInput').value = '';
    $('#hello').hidden = S.history.length === 0 ? false : $('#hello').hidden;
    const turn = document.createElement('div'); turn.className = 'turn';
    turn.innerHTML = `<div class="q"><p>${esc(q)}</p></div><div class="a"><div class="sigil">✦</div><div><div class="a-label">ICONIC · RUNNING ON ${esc((S.status && S.status.host || 'THIS COMPUTER').toUpperCase())}</div><div class="reading"><span class="shimmer">Searching ${fmt(S.workspace ? S.workspace.documents : 0)} documents…</span></div><div class="a-body streaming" hidden></div><div class="srcs"></div><div class="a-meta"></div><div class="nexts"></div></div></div>`;
    $('#convo').appendChild(turn);
    if (S.history.length === 0) $('#hello').hidden = true;
    const convo = $('#convo'); convo.scrollTop = convo.scrollHeight;
    const reading = $('.reading', turn), bodyEl = $('.a-body', turn), srcEl = $('.srcs', turn), metaEl = $('.a-meta', turn), nextEl = $('.nexts', turn);
    let sources = [], text = '', t0 = performance.now();
    const paint = () => { bodyEl.innerHTML = md(text, sources); $$('.cite', bodyEl).forEach((c) => c.onclick = () => { const s = sources.find((x) => String(x.n) === c.dataset.n); if (s) openDoc(s.id, s.snippet); }); };
    try {
      const res = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ws: S.ws, q, history: S.history.slice(-3) }) });
      if (!res.ok) { const j = await res.json().catch(() => ({})); throw new Error(j.error || 'Request failed'); }
      const reader = res.body.getReader(), dec = new TextDecoder(); let buf = '';
      for (;;) {
        const { value, done } = await reader.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf('\n\n')) >= 0) {
          const block = buf.slice(0, i); buf = buf.slice(i + 2);
          const ev = (block.match(/^event: (.*)$/m) || [])[1], dataLine = (block.match(/^data: (.*)$/m) || [])[1];
          if (!ev || dataLine == null) continue;
          const data = JSON.parse(dataLine);
          if (ev === 'sources') {
            sources = data;
            reading.innerHTML = sources.length ? `<span class="shimmer">Reading ${sources.length} passages from ${new Set(sources.map((s) => s.id)).size} documents…</span>` : '<span class="shimmer">No matching passages. Asking anyway…</span>';
            srcEl.innerHTML = sources.map((s, k) => `<button class="src" style="animation-delay:${k * 70}ms" data-n="${s.n}"><span>${s.n}</span><span><strong>${esc(s.title)}</strong><small>${esc(s.folder)} · ${esc(s.date)}</small></span></button>`).join('');
            $$('.src', srcEl).forEach((b) => b.addEventListener('click', () => { const s = sources.find((x) => String(x.n) === b.dataset.n); openDoc(s.id, s.snippet); }));
          } else if (ev === 'thinking') {
            reading.innerHTML = '<span class="shimmer">Thinking it through…</span>';
          } else if (ev === 'token') {
            if (bodyEl.hidden) { bodyEl.hidden = false; reading.remove(); }
            text += data; paint(); convo.scrollTop = convo.scrollHeight;
          } else if (ev === 'done') {
            bodyEl.classList.remove('streaming'); paint();
            metaEl.innerHTML = `<span>ANSWERED ON ${esc(String(data.location || 'THIS COMPUTER').toUpperCase())} IN ${(data.ms / 1000).toFixed(1)}s</span>${data.tps ? `<span>${data.tps} TOK/S</span>` : ''}<span><b>COST $0.00</b></span>${data.private ? '<span><b>SENT TO NO AI COMPANY</b></span>' : ''}`;
          } else if (ev === 'error') { throw new Error(data); }
        }
      }
      if (!text) throw new Error('The model returned nothing.');
      S.history.push({ q, a: text });
      const cta = (S.status && S.status.cta_url) || '';
      const nq = nextQuestions(2);
      nextEl.innerHTML = nq.map((x) => `<button type="button" class="next" data-q="${esc(x)}">${esc(x)} →</button>`).join('') +
        (cta ? `<a class="next cta-chip" href="${esc(cta)}" target="_blank" rel="noopener">Put this on my files →</a>` : '');
      $$('.next[data-q]', nextEl).forEach((b) => b.addEventListener('click', () => ask(b.dataset.q)));
      if (cta && S.history.length === 3) {
        const card = document.createElement('div'); card.className = 'cta-card';
        card.innerHTML = `<div><small>${S.workspace && S.workspace.sample ? 'THAT WAS A MADE-UP BUSINESS' : 'LIKE WHAT YOU SEE?'}</small><h3>Now picture it on yours.</h3><p>Your files, on a computer in your office. Nothing goes to an AI company, and there's no meter running.</p></div><a href="${esc(cta)}" target="_blank" rel="noopener">BOOK THE FREE 30-MINUTE CHECK →</a>`;
        turn.appendChild(card);
      }
    } catch (e) {
      reading.remove?.(); bodyEl.hidden = false; bodyEl.classList.remove('streaming');
      bodyEl.innerHTML = `<p class="a-err">${esc(e.message)}</p>`;
    } finally {
      S.busy = false; $('#askBtn').disabled = false; bodyEl.classList.remove('streaming');
      convo.scrollTop = convo.scrollHeight; loadStatus();
      if (matchMedia('(pointer: fine)').matches) $('#askInput').focus();
    }
  }
  $('#askForm').addEventListener('submit', (e) => { e.preventDefault(); ask($('#askInput').value); });

  // ---------- loops
  (async () => {
    await loadStatus(); await loadWorkspace().catch(() => {}); await loadFeed(); loadJobs();
    setInterval(loadStatus, 5000);
    setInterval(() => { if (!S.feed || S.feed.status !== 'ready' || S.tab === 'intel') loadFeed(); }, 4000);
    setInterval(() => { loadJobs(); }, 3000);
    setInterval(() => { if (S.workspace) api('/api/workspace?ws=' + encodeURIComponent(S.ws)).then((w) => { if (w.indexed_at !== S.workspace.indexed_at) { S.workspace = w; renderKnowledge(); renderHello(); $('#cntDocs').textContent = w.documents || ''; } }).catch(() => {}); }, 10000);
  })();
})();
