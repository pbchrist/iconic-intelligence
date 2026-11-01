/* ICONIC intelligence graph: a small force layout on a 2D canvas.
   Business at the center, wings around it, entities inside wings, files as small marks.
   Tunnels (hidden connections) glow. Links learned from questions accumulate. */
(() => {
  const COL = { core: '#c9ceff', wing: '#8d98ff', ent: '#e6e8f2', doc: '#6c7390', learned: 'rgba(185,192,255,', tunnel: '#ffd9a1', urgent: '#ff9fba', broken: '#ff9fba', due: '#ffd9a1', active: 'rgba(185,192,255,.35)', expired: 'rgba(120,125,150,.35)' };
  let cv, ctx, W = 0, H = 0, dpr = 1, nodes = [], byId = {}, edges = [], tunnels = [], learned = [], selected = null, onSelect = null, raf = 0, t0 = performance.now(), fit = { s: 1, x: 0, y: 0 }, hover = null, small = false;

  function mount(canvas, cb) {
    cv = canvas; ctx = cv.getContext('2d'); onSelect = cb;
    const ro = new ResizeObserver(resize); ro.observe(cv.parentElement); resize();
    cv.addEventListener('pointerdown', (e) => { const n = pick(e); select(n ? n.id : null, true); });
    cv.addEventListener('pointermove', (e) => { const n = pick(e); hover = n; cv.style.cursor = n ? 'pointer' : 'default'; });
    if (!raf) loop();
  }
  function resize() {
    if (!cv) return; const r = cv.parentElement.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1); W = Math.max(200, r.width); H = Math.max(200, r.height);
    cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + 'px'; cv.style.height = H + 'px';
    small = W < 560; computeFit();
  }
  function pick(e) {
    const r = cv.getBoundingClientRect(), x = (e.clientX - r.left - fit.x) / fit.s, y = (e.clientY - r.top - fit.y) / fit.s;
    let best = null, bd = Infinity;
    for (const n of nodes) { const d = Math.hypot(n.x - x, n.y - y); const hit = (n.r + (small ? 16 : 10)) / Math.sqrt(fit.s); if (d < hit && d < bd) { bd = d; best = n; } }
    return best;
  }

  // ---------- build
  function build(g, opts) {
    const keepPos = {}; nodes.forEach((n) => (keepPos[n.id] = { x: n.x, y: n.y }));
    nodes = []; byId = {}; edges = []; tunnels = []; learned = [];
    const add = (n) => { const k = keepPos[n.id]; Object.assign(n, k || { x: (Math.random() - .5) * 40, y: (Math.random() - .5) * 40 }, { vx: 0, vy: 0 }); nodes.push(n); byId[n.id] = n; return n; };
    add({ id: 'core', kind: 'core', label: opts.name || 'The business', r: 16, fixed: true, x: 0, y: 0 });
    const wings = g.wings || [];
    wings.forEach((w, i) => { const a = (i / Math.max(1, wings.length)) * Math.PI * 2 - Math.PI / 2; const n = add({ id: 'w:' + w.id, kind: 'wing', label: w.label, r: 9, wing: w.id }); if (!keepPos[n.id]) { n.x = Math.cos(a) * 160; n.y = Math.sin(a) * 160; } edges.push({ a: 'core', b: n.id, type: 'tree', L: 150 }); });
    const urgent = new Set(opts.urgentDocs || []);
    const docOwner = {};
    (g.entities || []).forEach((e) => {
      const w = byId['w:' + e.wing]; const n = add({ id: 'e:' + e.id, kind: 'ent', label: e.label, r: 5, wing: e.wing, docs: e.docs || [], ekind: e.kind });
      if (w && !keepPos[n.id]) { n.x = w.x * 1.35 + (Math.random() - .5) * 60; n.y = w.y * 1.35 + (Math.random() - .5) * 60; }
      if (w) edges.push({ a: w.id, b: n.id, type: 'tree', L: 62 });
      (e.docs || []).forEach((d) => { (docOwner[d] = docOwner[d] || []).push(n.id); });
      if ((e.docs || []).some((d) => urgent.has(d))) n.urgent = true;
    });
    (g.docs || []).forEach((d) => {
      const owners = docOwner[d.id] || []; const n = add({ id: 'd:' + d.id, kind: 'doc', label: d.title, r: 3, doc: d.id, urgent: urgent.has(d.id) });
      const o = owners[0] && byId[owners[0]];
      if (o && !keepPos[n.id]) { n.x = o.x * 1.2 + (Math.random() - .5) * 30; n.y = o.y * 1.2 + (Math.random() - .5) * 30; }
      owners.slice(0, 2).forEach((oid) => edges.push({ a: oid, b: n.id, type: 'doc', L: 30 }));
      if (!owners.length) edges.push({ a: 'core', b: n.id, type: 'loose', L: 230 });
    });
    (g.facts || []).forEach((f) => { if (byId['e:' + f.a] && byId['e:' + f.b]) edges.push({ a: 'e:' + f.a, b: 'e:' + f.b, type: 'fact', state: f.state, label: f.label, date: f.date, docs: f.docs, L: 90 }); });
    (g.tunnels || []).forEach((t, i) => { if (byId['e:' + t.a] && byId['e:' + t.b]) tunnels.push({ a: 'e:' + t.a, b: 'e:' + t.b, insight: t.insight, docs: t.docs, i }); });
    (g.learned || []).forEach((l) => { if (byId['d:' + l.a] && byId['d:' + l.b]) learned.push({ a: 'd:' + l.a, b: 'd:' + l.b, n: l.n, last: l.last }); });
    for (let i = 0; i < (Object.keys(keepPos).length ? 60 : 420); i++) step(1);
    computeFit();
  }

  // ---------- physics
  function step(k) {
    const N = nodes.length;
    for (let i = 0; i < N; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < N; j++) {
        const b = nodes[j]; let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + .01;
        const rep = (a.kind === 'doc' && b.kind === 'doc' ? 260 : 1100) / d2; const d = Math.sqrt(d2);
        dx /= d; dy /= d; a.vx += dx * rep; a.vy += dy * rep; b.vx -= dx * rep; b.vy -= dy * rep;
      }
    }
    for (const e of edges) {
      const a = byId[e.a], b = byId[e.b]; if (!a || !b) continue;
      const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1, s = (e.type === 'fact' ? .004 : e.type === 'loose' ? .002 : .02) * (d - e.L);
      a.vx += dx / d * s; a.vy += dy / d * s; b.vx -= dx / d * s; b.vy -= dy / d * s;
    }
    for (const l of learned) { const a = byId[l.a], b = byId[l.b]; if (!a || !b) continue; const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1, s = .0015 * (d - 80); a.vx += dx / d * s; a.vy += dy / d * s; b.vx -= dx / d * s; b.vy -= dy / d * s; }
    for (const n of nodes) { if (n.fixed) { n.x = 0; n.y = 0; continue; } n.vx += -n.x * .0012; n.vy += -n.y * .0012; n.vx *= .82; n.vy *= .82; n.x += n.vx * k; n.y += n.vy * k; }
  }
  function computeFit() {
    if (!nodes.length || !W) return;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    nodes.forEach((n) => { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y); });
    const pad = small ? 34 : 54, s = Math.min((W - pad * 2) / Math.max(1, x1 - x0), (H - pad * 2) / Math.max(1, y1 - y0), 2.2);
    const tx = W / 2 - ((x0 + x1) / 2) * s, ty = H / 2 - ((y0 + y1) / 2) * s;
    fit = fit.s === 1 && !fit.init ? { s, x: tx, y: ty, init: true } : { s: fit.s + (s - fit.s) * .08, x: fit.x + (tx - fit.x) * .08, y: fit.y + (ty - fit.y) * .08, init: true };
  }

  // ---------- draw
  function loop() {
    raf = requestAnimationFrame(loop);
    if (!cv || !cv.offsetParent) return;
    const t = (performance.now() - t0) / 1000;
    step(.35); computeFit();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    ctx.save(); ctx.translate(fit.x, fit.y); ctx.scale(fit.s, fit.s);
    const sel = selected, related = new Set();
    if (sel) { related.add(sel); edges.concat(learned, tunnels).forEach((e) => { if (e.a === sel) related.add(e.b); if (e.b === sel) related.add(e.a); }); }
    const dim = (id) => sel && !related.has(id);
    const lw = 1 / fit.s;
    // learned links
    const now = Date.now() / 1000;
    for (const l of learned) {
      const a = byId[l.a], b = byId[l.b]; if (!a || !b) continue;
      const fresh = Math.max(0, 1 - (now - l.last) / 180), al = Math.min(.55, .12 + l.n * .06) + fresh * .45;
      ctx.strokeStyle = COL.learned + (dim(l.a) && dim(l.b) ? al * .25 : al) + ')'; ctx.lineWidth = (1 + Math.min(3, l.n * .4) + fresh * 2) * lw;
      ctx.beginPath(); ctx.moveTo(a.x, a.y); const mx = (a.x + b.x) / 2 - (b.y - a.y) * .15, my = (a.y + b.y) / 2 + (b.x - a.x) * .15; ctx.quadraticCurveTo(mx, my, b.x, b.y); ctx.stroke();
    }
    // structure and facts
    for (const e of edges) {
      const a = byId[e.a], b = byId[e.b]; if (!a || !b) continue;
      let c = 'rgba(141,152,255,.16)', w = 1;
      if (e.type === 'fact') { c = COL[e.state] || COL.active; w = e.state === 'broken' || e.state === 'due' ? 1.6 : 1; }
      if (e.type === 'doc') c = 'rgba(108,115,144,.25)';
      if (e.type === 'loose') c = 'rgba(108,115,144,.08)';
      if (sel && (e.a === sel || e.b === sel)) { c = e.type === 'fact' ? (COL[e.state] || '#b9c0ff') : 'rgba(185,192,255,.7)'; w = 1.8; }
      else if (sel) c = c.replace(/[\d.]+\)$/, '.05)');
      ctx.strokeStyle = c; ctx.lineWidth = w * lw; ctx.setLineDash(e.state === 'expired' ? [4 * lw, 4 * lw] : []);
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
    ctx.setLineDash([]);
    // tunnels: glowing, animated
    for (const tn of tunnels) {
      const a = byId[tn.a], b = byId[tn.b]; if (!a || !b) continue;
      const on = !sel || sel === tn.a || sel === tn.b || sel === 'tunnel:' + tn.i;
      const mx = (a.x + b.x) / 2 + (a.y - b.y) * .35, my = (a.y + b.y) / 2 + (b.x - a.x) * .35;
      ctx.save(); ctx.shadowColor = 'rgba(255,217,161,.9)'; ctx.shadowBlur = 18; ctx.globalAlpha = on ? .55 + .35 * Math.sin(t * 2.4 + tn.i) : .12;
      ctx.strokeStyle = COL.tunnel; ctx.lineWidth = 2.4 * lw; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.quadraticCurveTo(mx, my, b.x, b.y); ctx.stroke();
      ctx.setLineDash([3 * lw, 9 * lw]); ctx.lineDashOffset = -t * 40 * lw; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.4 * lw; ctx.globalAlpha = on ? .9 : .1; ctx.stroke();
      ctx.restore();
    }
    // nodes
    for (const n of nodes) {
      const isSel = sel === n.id, fade = dim(n.id) ? .22 : 1;
      ctx.globalAlpha = fade;
      if (n.kind === 'core') {
        const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, 46); g.addColorStop(0, 'rgba(201,206,255,.55)'); g.addColorStop(1, 'rgba(82,91,199,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, 46 + Math.sin(t * 1.6) * 3, 0, 7); ctx.fill();
        ctx.fillStyle = '#c9ceff'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.2 * lw; poly(n.x, n.y, n.r, 6, t * .2); ctx.fill(); ctx.stroke();
      } else if (n.kind === 'wing') {
        ctx.fillStyle = 'rgba(94,104,218,.35)'; ctx.strokeStyle = COL.wing; ctx.lineWidth = (isSel ? 2.4 : 1.4) * lw;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 7); ctx.fill(); ctx.stroke();
      } else if (n.kind === 'ent') {
        if (n.urgent) { ctx.fillStyle = 'rgba(255,159,186,' + (.18 + .14 * Math.sin(t * 3)) + ')'; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 7 + Math.sin(t * 3) * 2, 0, 7); ctx.fill(); }
        ctx.fillStyle = n.urgent ? COL.urgent : COL.ent; ctx.beginPath(); ctx.arc(n.x, n.y, isSel ? n.r + 2 : n.r, 0, 7); ctx.fill();
        if (isSel) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5 * lw; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 6, 0, 7); ctx.stroke(); }
      } else {
        ctx.fillStyle = n.urgent ? COL.urgent : COL.doc; const r = isSel ? 4.5 : n.r; ctx.fillRect(n.x - r, n.y - r, r * 2, r * 2);
      }
    }
    ctx.globalAlpha = 1;
    // labels (screen-space font size)
    const fs = (px) => px / fit.s;
    ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    for (const n of nodes) {
      const show = n.kind === 'wing' || n.kind === 'core' || n.id === sel || (hover && hover.id === n.id) || (!small && n.kind === 'ent' && fit.s > .85 && (!sel || related.has(n.id))) || (sel && related.has(n.id) && n.kind !== 'doc');
      if (!show) continue;
      const px = n.kind === 'core' ? 13 : n.kind === 'wing' ? 11.5 : 11;
      ctx.font = `${n.kind === 'ent' || n.kind === 'doc' ? 500 : 700} ${fs(px)}px Inter, -apple-system, Helvetica, Arial, sans-serif`;
      let txt = n.label; if (txt.length > 26 && n.id !== sel) txt = txt.slice(0, 24) + '…';
      if (n.kind === 'wing' || n.kind === 'core') txt = txt.toUpperCase();
      const y = n.y + n.r + fs(5), w = ctx.measureText(txt).width;
      ctx.globalAlpha = dim(n.id) ? .25 : 1;
      ctx.fillStyle = 'rgba(7,9,18,.72)'; ctx.fillRect(n.x - w / 2 - fs(4), y - fs(2), w + fs(8), fs(px + 5));
      ctx.fillStyle = n.kind === 'wing' ? '#b9c0ff' : n.kind === 'core' ? '#fff' : '#e1e3ec'; ctx.fillText(txt, n.x, y);
    }
    ctx.globalAlpha = 1; ctx.restore();
  }
  function poly(x, y, r, k, rot) { ctx.beginPath(); for (let i = 0; i <= k; i++) { const a = rot + (i / k) * Math.PI * 2; i ? ctx.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r) : ctx.moveTo(x + Math.cos(a) * r, y + Math.sin(a) * r); } ctx.closePath(); }

  function select(id, user) {
    selected = id; if (onSelect) onSelect(id ? describe(id) : null, user);
  }
  function describe(id) {
    if (id.startsWith('tunnel:')) { const tn = tunnels[Number(id.slice(7))]; return tn && { kind: 'tunnel', tunnel: tn, a: byId[tn.a], b: byId[tn.b] }; }
    const n = byId[id]; if (!n) return null;
    const facts = edges.filter((e) => e.type === 'fact' && (e.a === id || e.b === id)).map((e) => ({ other: byId[e.a === id ? e.b : e.a], label: e.label, date: e.date, state: e.state, docs: e.docs }));
    const ts = tunnels.filter((t) => t.a === id || t.b === id);
    const docs = n.kind === 'doc' ? [n.doc] : n.kind === 'ent' ? n.docs : nodes.filter((x) => x.kind === 'ent' && x.wing === n.wing).flatMap((x) => x.docs);
    const kids = n.kind === 'wing' ? nodes.filter((x) => x.kind === 'ent' && x.wing === n.wing) : [];
    const lrn = learned.filter((l) => l.a === id || l.b === id).map((l) => ({ other: byId[l.a === id ? l.b : l.a], n: l.n }));
    return { kind: n.kind, node: n, facts, tunnels: ts, docs: [...new Set(docs)], kids, learned: lrn };
  }
  function addLearned(pairs) {
    const now = Date.now() / 1000;
    (pairs || []).forEach(([a, b]) => { const ex = learned.find((l) => l.a === 'd:' + a && l.b === 'd:' + b); if (ex) { ex.n++; ex.last = now; } else if (byId['d:' + a] && byId['d:' + b]) learned.push({ a: 'd:' + a, b: 'd:' + b, n: 1, last: now }); });
  }
  window.IconicGraph = { mount, build, select, addLearned, nodeCount: () => nodes.length, resize };
})();
