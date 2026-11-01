/* ICONIC intelligence graph.
   Opens quiet: the business and its main areas. Then one hidden connection draws itself in gold.
   Gold means only one thing: a connection no single file states. Lavender lines are links
   learned from visitors' questions. Everything else stays out of the way until tapped. */
(() => {
  let cv, ctx, W = 0, H = 0, dpr = 1, small = false;
  let nodes = [], byId = {}, edges = [], tunnels = [], learned = [];
  let selected = null, expanded = null, story = -1, storyT0 = 0, hover = null, onSelect = null, raf = 0;
  let fit = { s: 1, x: 0, y: 0, init: false };
  const t0 = performance.now();
  const GOLD = '#ffd9a1', LAV = 'rgba(185,192,255,', WING = '#8d98ff';

  function mount(canvas, cb) {
    cv = canvas; ctx = cv.getContext('2d'); onSelect = cb;
    new ResizeObserver(resize).observe(cv.parentElement); resize();
    cv.addEventListener('pointerdown', (e) => tap(pick(e)));
    cv.addEventListener('pointermove', (e) => { hover = pick(e); cv.style.cursor = hover ? 'pointer' : 'default'; });
    if (!raf) loop();
  }
  function resize() {
    if (!cv) return; const r = cv.parentElement.getBoundingClientRect();
    const leg = cv.parentElement.querySelector('.glegend'), legH = leg && getComputedStyle(leg).position === 'static' ? leg.offsetHeight : 0;
    dpr = Math.min(2, window.devicePixelRatio || 1); W = Math.max(200, r.width); H = Math.max(160, r.height - legH);
    cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + 'px'; cv.style.height = H + 'px';
    small = W < 560; fit.init = false;
  }
  const rootPx = () => parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;

  // ---------- what is on screen right now
  function storyTunnel() { return story >= 0 ? tunnels[story] : null; }
  function visible(n) {
    if (n.kind === 'core' || n.kind === 'wing') return true;
    const st = storyTunnel();
    if (st && (n.id === st.a || n.id === st.b)) return true;
    if (n.id === selected) return true;
    if (n.kind === 'ent') {
      if (expanded && n.wing === expanded) return true;
      if (selected && edges.some((e) => e.type === 'fact' && ((e.a === selected && e.b === n.id) || (e.b === selected && e.a === n.id)))) return true;
      return false;
    }
    if (n.kind === 'doc') {
      if (selected && byId[selected] && byId[selected].kind === 'ent' && (byId[selected].docs || []).includes(n.doc)) return true;
      return learned.some((l) => l.a === n.id || l.b === n.id);
    }
    return false;
  }
  function pick(e) {
    const r = cv.getBoundingClientRect(), x = (e.clientX - r.left - fit.x) / fit.s, y = (e.clientY - r.top - fit.y) / fit.s;
    let best = null, bd = Infinity;
    for (const n of nodes) { if (!visible(n)) continue; const d = Math.hypot(n.x - x, n.y - y), hit = (n.r + (small ? 22 : 14)) / fit.s; if (d < hit && d < bd) { bd = d; best = n; } }
    return best;
  }
  function tap(n) {
    if (!n) { selected = null; expanded = null; onSelect && onSelect(null); return; }
    if (n.kind === 'wing') { expanded = expanded === n.wing ? null : n.wing; selected = n.id; }
    else selected = n.id;
    onSelect && onSelect(describe(n.id), true);
  }

  // ---------- build
  function build(g, opts) {
    const fresh = opts.fresh, keep = {};
    if (!fresh) nodes.forEach((n) => (keep[n.id] = { x: n.x, y: n.y }));
    nodes = []; byId = {}; edges = []; tunnels = []; learned = [];
    if (fresh) { selected = null; expanded = null; story = -1; fit.init = false; }
    const add = (n) => { Object.assign(n, keep[n.id] || {}, { vx: 0, vy: 0 }); if (n.x == null) { n.x = (Math.random() - .5) * 40; n.y = (Math.random() - .5) * 40; } nodes.push(n); byId[n.id] = n; return n; };
    add({ id: 'core', kind: 'core', label: opts.name || 'The business', r: 14, fixed: true, x: 0, y: 0 });
    const wings = g.wings || [];
    wings.forEach((w, i) => {
      const a = (i / Math.max(1, wings.length)) * Math.PI * 2 - Math.PI / 2;
      const n = add({ id: 'w:' + w.id, kind: 'wing', label: w.label, r: 8, wing: w.id });
      if (!keep[n.id]) { n.x = Math.cos(a) * 150; n.y = Math.sin(a) * 150; }
      edges.push({ a: 'core', b: n.id, type: 'tree', L: 145 });
    });
    const docOwner = {};
    (g.entities || []).forEach((e) => {
      const w = byId['w:' + e.wing];
      const n = add({ id: 'e:' + e.id, kind: 'ent', label: e.label, r: 5, wing: e.wing, docs: e.docs || [], ekind: e.kind });
      if (w && !keep[n.id]) { n.x = w.x * 1.45 + (Math.random() - .5) * 50; n.y = w.y * 1.45 + (Math.random() - .5) * 50; }
      if (w) edges.push({ a: w.id, b: n.id, type: 'tree', L: 64 });
      (e.docs || []).forEach((d) => (docOwner[d] = docOwner[d] || []).push(n.id));
    });
    (g.docs || []).forEach((d) => {
      const owners = docOwner[d.id] || [];
      const n = add({ id: 'd:' + d.id, kind: 'doc', label: d.title, r: 3, doc: d.id });
      const o = owners[0] && byId[owners[0]];
      if (o && !keep[n.id]) { n.x = o.x * 1.15 + (Math.random() - .5) * 26; n.y = o.y * 1.15 + (Math.random() - .5) * 26; }
      owners.slice(0, 2).forEach((oid) => edges.push({ a: oid, b: n.id, type: 'doc', L: 30 }));
      if (!owners.length) edges.push({ a: 'core', b: n.id, type: 'loose', L: 220 });
    });
    (g.facts || []).forEach((f) => { if (byId['e:' + f.a] && byId['e:' + f.b]) edges.push({ a: 'e:' + f.a, b: 'e:' + f.b, type: 'fact', state: f.state, label: f.label, date: f.date, docs: f.docs, L: 95 }); });
    (g.tunnels || []).forEach((t, i) => { if (byId['e:' + t.a] && byId['e:' + t.b]) tunnels.push({ a: 'e:' + t.a, b: 'e:' + t.b, insight: t.insight, docs: t.docs, i }); });
    (g.learned || []).forEach((l) => { if (byId['d:' + l.a] && byId['d:' + l.b]) learned.push({ a: 'd:' + l.a, b: 'd:' + l.b, n: l.n, last: l.last }); });
    for (let i = 0; i < (Object.keys(keep).length ? 40 : 450); i++) step(1);
  }

  // ---------- physics (all nodes, so positions stay put when things appear)
  function step(k) {
    const N = nodes.length;
    for (let i = 0; i < N; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < N; j++) {
        const b = nodes[j]; let dx = a.x - b.x, dy = a.y - b.y; const d2 = dx * dx + dy * dy + .01, d = Math.sqrt(d2);
        const rep = (a.kind === 'doc' && b.kind === 'doc' ? 240 : 1200) / d2; dx /= d; dy /= d;
        a.vx += dx * rep; a.vy += dy * rep; b.vx -= dx * rep; b.vy -= dy * rep;
      }
    }
    for (const e of edges) {
      const a = byId[e.a], b = byId[e.b]; if (!a || !b) continue;
      const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1, s = (e.type === 'fact' ? .003 : e.type === 'loose' ? .002 : .02) * (d - e.L);
      a.vx += dx / d * s; a.vy += dy / d * s; b.vx -= dx / d * s; b.vy -= dy / d * s;
    }
    for (const n of nodes) { if (n.fixed) { n.x = 0; n.y = 0; continue; } n.vx += -n.x * .0012; n.vy += -n.y * .0012; n.vx *= .8; n.vy *= .8; n.x += n.vx * k; n.y += n.vy * k; }
  }
  function computeFit() {
    const vis = nodes.filter(visible); if (!vis.length || !W) return;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    vis.forEach((n) => { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y); });
    const padX = small ? 70 : 110, padY = small ? 46 : 64;
    const s = Math.min((W - padX * 2) / Math.max(120, x1 - x0), (H - padY * 2) / Math.max(120, y1 - y0), 2.4);
    const tx = W / 2 - ((x0 + x1) / 2) * s, ty = H / 2 - ((y0 + y1) / 2) * s;
    if (!fit.init) fit = { s, x: tx, y: ty, init: true };
    else { fit.s += (s - fit.s) * .06; fit.x += (tx - fit.x) * .06; fit.y += (ty - fit.y) * .06; }
  }

  // ---------- drawing
  function curve(a, b, bend) { return { mx: (a.x + b.x) / 2 + (a.y - b.y) * bend, my: (a.y + b.y) / 2 + (b.x - a.x) * bend }; }
  function qpt(a, c, b, t) { const u = 1 - t; return { x: u * u * a.x + 2 * u * t * c.mx + t * t * b.x, y: u * u * a.y + 2 * u * t * c.my + t * t * b.y }; }

  function loop() {
    raf = requestAnimationFrame(loop);
    if (!cv || !cv.offsetParent) return;
    const t = (performance.now() - t0) / 1000;
    step(.3); computeFit();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    ctx.save(); ctx.translate(fit.x, fit.y); ctx.scale(fit.s, fit.s);
    const lw = 1 / fit.s, st = storyTunnel(), focus = new Set();
    if (st) { focus.add(st.a); focus.add(st.b); focus.add('w:' + byId[st.a].wing); focus.add('w:' + byId[st.b].wing); }
    if (selected) focus.add(selected);
    const quiet = (id) => (st || selected) && !focus.has(id);

    // structure: thin, quiet
    for (const e of edges) {
      const a = byId[e.a], b = byId[e.b]; if (!a || !b || !visible(a) || !visible(b)) continue;
      if (e.type === 'loose') continue;
      let c = 'rgba(141,152,255,.18)', w = 1;
      if (e.type === 'fact') { if (!(selected && (e.a === selected || e.b === selected))) continue; c = 'rgba(230,232,242,.55)'; w = 1.3; }
      if (e.type === 'doc') c = 'rgba(141,152,255,.22)';
      if (quiet(e.a) && quiet(e.b)) c = 'rgba(141,152,255,.07)';
      ctx.strokeStyle = c; ctx.lineWidth = w * lw; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
    // learned from visitors' questions: lavender
    const now = Date.now() / 1000;
    for (const l of learned) {
      const a = byId[l.a], b = byId[l.b]; if (!a || !b) continue;
      const fresh = Math.max(0, 1 - (now - l.last) / 240), al = Math.min(.5, .16 + l.n * .05) * (st ? .55 : 1) + fresh * .5;
      const c = curve(a, b, .18);
      ctx.strokeStyle = LAV + al + ')'; ctx.lineWidth = (1 + Math.min(2, l.n * .3) + fresh * 2) * lw;
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.quadraticCurveTo(c.mx, c.my, b.x, b.y); ctx.stroke();
    }
    // the hidden connection, drawn live
    if (st) {
      const a = byId[st.a], b = byId[st.b], c = curve(a, b, .32);
      const p = Math.min(1, Math.max(0, (performance.now() - storyT0 - 450) / 1500)), ease = 1 - Math.pow(1 - p, 3);
      ctx.save(); ctx.shadowColor = 'rgba(255,217,161,.95)'; ctx.shadowBlur = 22; ctx.strokeStyle = GOLD; ctx.lineCap = 'round';
      ctx.lineWidth = (3 + (p >= 1 ? Math.sin(t * 2.6) * .8 : 0)) * lw; ctx.beginPath(); ctx.moveTo(a.x, a.y);
      const steps = 48; for (let i = 1; i <= Math.ceil(steps * ease); i++) { const q = qpt(a, c, b, Math.min(ease, i / steps)); ctx.lineTo(q.x, q.y); }
      ctx.stroke();
      if (p < 1) { const h = qpt(a, c, b, ease); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(h.x, h.y, 4 * lw, 0, 7); ctx.fill(); }
      ctx.restore();
    }
    // nodes
    for (const n of nodes) {
      if (!visible(n)) continue;
      const isFocus = focus.has(n.id), fade = quiet(n.id) ? .35 : 1, isStoryEnd = st && (n.id === st.a || n.id === st.b);
      ctx.globalAlpha = fade;
      if (n.kind === 'core') {
        const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 52); g.addColorStop(0, 'rgba(201,206,255,.5)'); g.addColorStop(1, 'rgba(82,91,199,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, 52 + Math.sin(t * 1.5) * 3, 0, 7); ctx.fill();
        ctx.fillStyle = '#c9ceff'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.2 * lw; poly(n.x, n.y, n.r, 6, t * .15); ctx.fill(); ctx.stroke();
      } else if (n.kind === 'wing') {
        const open = expanded === n.wing;
        ctx.fillStyle = open || isFocus ? 'rgba(94,104,218,.6)' : 'rgba(94,104,218,.3)'; ctx.strokeStyle = WING; ctx.lineWidth = (open ? 2.4 : 1.4) * lw;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 7); ctx.fill(); ctx.stroke();
      } else if (n.kind === 'ent') {
        if (isStoryEnd) { ctx.fillStyle = 'rgba(255,217,161,' + (.22 + .12 * Math.sin(t * 3)) + ')'; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 9, 0, 7); ctx.fill(); }
        ctx.fillStyle = isStoryEnd ? GOLD : '#e6e8f2'; ctx.beginPath(); ctx.arc(n.x, n.y, n.id === selected ? n.r + 2 : n.r, 0, 7); ctx.fill();
        if (n.id === selected) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5 * lw; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 6, 0, 7); ctx.stroke(); }
      } else {
        ctx.fillStyle = 'rgba(185,192,255,.75)'; const r = n.id === selected ? 4.5 : n.r; ctx.fillRect(n.x - r, n.y - r, r * 2, r * 2);
      }
    }
    ctx.globalAlpha = 1;
    labels(st, focus, quiet);
    ctx.restore();
  }

  // labels in screen space, never overlapping: most important first, skip any that would collide
  function labels(st, focus, quiet) {
    const R = rootPx(), placed = [];
    const items = nodes.filter((n) => visible(n) && n.kind !== 'doc' || n.id === selected).map((n) => {
      const pr = (st && (n.id === st.a || n.id === st.b)) ? 0 : n.id === selected ? 1 : n.kind === 'core' ? 2 : n.kind === 'wing' ? (focus.has(n.id) ? 3 : 4) : 5;
      return { n, pr };
    }).sort((a, b) => a.pr - b.pr);
    ctx.save(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.textBaseline = 'top'; ctx.textAlign = 'center';
    for (const { n, pr } of items) {
      const px = (pr === 0 ? 1 : n.kind === 'core' ? .95 : n.kind === 'wing' ? .78 : .85) * R * (small ? .92 : 1);
      ctx.font = `${n.kind === 'ent' && pr !== 0 ? 500 : 700} ${px}px Inter, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif`;
      let txt = n.kind === 'wing' || n.kind === 'core' ? n.label.toUpperCase() : n.label;
      const max = small ? 15 : 22; if (txt.length > max && pr > 1) txt = txt.slice(0, max - 1) + '…';
      const sx = n.x * fit.s + fit.x, sy = n.y * fit.s + fit.y + (n.r * fit.s) + 6;
      const w = ctx.measureText(txt).width + 12, h = px + 8;
      let box = { x: Math.max(4, Math.min(W - w - 4, sx - w / 2)), y: sy, w, h };
      if (box.y + h > H - 4) box.y = sy - n.r * fit.s * 2 - h - 10;
      const hit = (b) => placed.some((p) => b.x < p.x + p.w && b.x + b.w > p.x && b.y < p.y + p.h && b.y + b.h > p.y);
      if (hit(box)) { const up = { ...box, y: sy - n.r * fit.s * 2 - h - 10 }; if (!hit(up)) box = up; else if (pr > 1) continue; }
      placed.push(box);
      ctx.globalAlpha = quiet(n.id) && pr > 1 ? .45 : 1;
      ctx.fillStyle = pr === 0 ? 'rgba(40,30,10,.88)' : 'rgba(7,9,18,.82)'; roundRect(box.x, box.y, box.w, box.h, 6); ctx.fill();
      if (pr === 0) { ctx.strokeStyle = 'rgba(255,217,161,.6)'; ctx.lineWidth = 1; ctx.stroke(); }
      ctx.fillStyle = pr === 0 ? GOLD : n.kind === 'wing' ? '#c3c8ff' : '#fff';
      ctx.fillText(txt, box.x + box.w / 2, box.y + 4);
    }
    ctx.restore();
  }
  function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function poly(x, y, r, k, rot) { ctx.beginPath(); for (let i = 0; i <= k; i++) { const a = rot + (i / k) * Math.PI * 2; i ? ctx.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r) : ctx.moveTo(x + Math.cos(a) * r, y + Math.sin(a) * r); } ctx.closePath(); }

  // ---------- details for the side panel
  function describe(id) {
    const n = byId[id]; if (!n) return null;
    const facts = edges.filter((e) => e.type === 'fact' && (e.a === id || e.b === id)).map((e) => ({ other: byId[e.a === id ? e.b : e.a], label: e.label, date: e.date, state: e.state }));
    const ts = tunnels.filter((t) => t.a === id || t.b === id);
    const kids = n.kind === 'wing' ? nodes.filter((x) => x.kind === 'ent' && x.wing === n.wing) : [];
    const docs = n.kind === 'doc' ? [n.doc] : n.kind === 'ent' ? n.docs : kids.flatMap((x) => x.docs);
    const lrn = learned.filter((l) => l.a === id || l.b === id).length;
    return { kind: n.kind, node: n, facts, tunnels: ts, docs: [...new Set(docs)], kids, learned: lrn };
  }

  function setStory(i) {
    if (!tunnels.length) { story = -1; return null; }
    story = ((i % tunnels.length) + tunnels.length) % tunnels.length; storyT0 = performance.now(); selected = null; expanded = null; fit.init = fit.init && true;
    const tn = tunnels[story];
    return { i: story, total: tunnels.length, a: byId[tn.a].label, b: byId[tn.b].label, insight: tn.insight, docs: tn.docs };
  }
  function addLearned(pairs) {
    const now = Date.now() / 1000;
    (pairs || []).forEach(([a, b]) => { const ex = learned.find((l) => l.a === 'd:' + a && l.b === 'd:' + b); if (ex) { ex.n++; ex.last = now; } else if (byId['d:' + a] && byId['d:' + b]) learned.push({ a: 'd:' + a, b: 'd:' + b, n: 1, last: now }); });
  }
  window.IconicGraph = { mount, build, setStory, addLearned, resize, nodeCount: () => nodes.length, tunnelCount: () => tunnels.length, clearSelection: () => tap(null) };
})();
