/* ICONIC style guide page. Every word, token and rule on the page comes from /style-guide.yaml,
   so the page and the YAML cannot disagree. Swatches are painted with the live CSS tokens and
   compared to the YAML hex; type specimens show the size they actually render at. */
(function () {
  var status = document.getElementById('sgStatus');
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function get(obj, path) { return path.split('.').reduce(function (o, k) { return o == null ? o : o[k]; }, obj); }
  function norm(v) { return String(v || '').toLowerCase().replace(/\s+/g, '').replace(/0\./g, '.'); }

  function doDont(target, d, extra) {
    if (!target || !d) return;
    var wrap = el('div', 'sg-dd');
    var a = el('div', 'sg-do'); a.appendChild(el('h4', null, 'Do'));
    var ul = el('ul'); (d.do || []).forEach(function (t) { ul.appendChild(el('li', null, esc(t))); }); a.appendChild(ul);
    var b = el('div', 'sg-dont'); b.appendChild(el('h4', null, 'Don\'t'));
    var ul2 = el('ul'); (d.dont || []).forEach(function (t) { ul2.appendChild(el('li', null, esc(t))); }); b.appendChild(ul2);
    if (extra) target.appendChild(extra);
    wrap.appendChild(a); wrap.appendChild(b); target.appendChild(wrap);
  }

  function render(g) {
    // Plain text slots.
    document.querySelectorAll('[data-yaml]').forEach(function (n) { var v = get(g, n.getAttribute('data-yaml')); if (v != null) n.textContent = v; });
    document.getElementById('sgUpdated').textContent = 'UPDATED ' + g.meta.updated;

    // Logo, color, type, imagery do/don't.
    doDont(document.querySelector('[data-dodont="logo"]'), g.logo);
    doDont(document.querySelector('[data-dodont="colors"]'), g.colors);
    doDont(document.querySelector('[data-dodont="type"]'), g.type);
    doDont(document.querySelector('[data-dodont="imagery"]'), g.imagery);

    // Color swatches, painted with the live token and checked against the YAML.
    var root = getComputedStyle(document.documentElement), bad = 0;
    var sw = document.getElementById('sgSwatches');
    g.colors.tokens.forEach(function (t) {
      var live = root.getPropertyValue(t.name).trim();
      var ok = norm(live) === norm(t.hex);
      if (!ok) bad++;
      var card = el('div', 'sg-swatch');
      var chip = el('div', 'sg-chip'); chip.style.setProperty('--sw', 'var(' + t.name + ')');
      card.appendChild(chip);
      card.appendChild(el('div', 'sg-swatch-text',
        '<strong>' + esc(t.name) + '</strong><code>' + esc(t.hex) + '</code><p>' + esc(t.role) + '</p>' +
        (ok ? '<span class="sg-ok">Matches the live CSS</span>' : '<span class="sg-bad">Live CSS says ' + esc(live || 'nothing') + '</span>')));
      sw.appendChild(card);
    });
    var also = document.getElementById('sgAlso');
    g.colors.also_in_use.forEach(function (t) {
      var card = el('div', 'sg-swatch');
      var chip = el('div', 'sg-chip'); chip.style.setProperty('--sw', t.hex);
      card.appendChild(chip);
      card.appendChild(el('div', 'sg-swatch-text', '<code>' + esc(t.hex) + '</code><p>' + esc(t.where) + '</p>'));
      also.appendChild(card);
    });

    // Type families and specimens.
    var fam = document.getElementById('sgFamilies');
    g.type.families.forEach(function (f) {
      var c = el('div', 'sg-family sg-family-' + f.name.toLowerCase());
      c.appendChild(el('div', 'sg-family-sample', 'Aa'));
      c.appendChild(el('div', 'sg-family-text', '<strong>' + esc(f.name) + '</strong><code>' + esc(f.stack) + '</code><p>' + esc(f.use) + (f.note ? ' ' + esc(f.note) : '') + '</p>'));
      fam.appendChild(c);
    });
    g.type.scale.forEach(function (t) {
      var spec = document.querySelector('.sg-spec[data-type="' + t.id + '"]'); if (!spec) return;
      var s = spec.querySelector('[data-sample]'); s.innerHTML = t.sample; // samples are trusted markup from our own YAML
      var meta = el('div', 'sg-spec-meta');
      meta.innerHTML = '<strong>' + esc(t.name) + '</strong><code>' + esc(t.class) + '</code><span>' + esc(t.family) + ' · ' + esc(t.weight) + ' · ' + esc(t.size) + '</span>' +
        '<span class="sg-measured" data-measure></span>' + (t.note ? '<p>' + esc(t.note) + '</p>' : '');
      spec.insertBefore(meta, spec.firstChild);
    });

    // Components: name, class, use, do and don't beside each live example.
    g.components.forEach(function (c) {
      var box = document.querySelector('.sg-comp[data-component="' + c.id + '"]'); if (!box) return;
      var side = el('div', 'sg-comp-text');
      side.innerHTML = '<h3>' + esc(c.name) + '</h3><code>' + esc(c.class) + '</code><p>' + esc(c.use) + '</p>';
      doDont(side, c);
      box.appendChild(side);
    });

    // Layout.
    var sp = g.spacing, dl = document.getElementById('sgSpacing');
    [['Container', sp.container], ['Phone gutter', sp.gutter_phone], ['Grid', sp.grid], ['Section rhythm', sp.section_rhythm], ['Borders', sp.borders],
     ['Breakpoints', Object.keys(sp.breakpoints).filter(function (k) { return k !== 'check_widths'; }).map(function (k) { return k.replace('_', ' ') + ': ' + sp.breakpoints[k]; }).join(' · ')],
     ['Always check at', sp.breakpoints.check_widths.join('px and ') + 'px']].forEach(function (r) {
      dl.appendChild(el('dt', null, esc(r[0]))); dl.appendChild(el('dd', null, esc(r[1])));
    });
    var rad = document.getElementById('sgRadii');
    sp.radius.forEach(function (r) {
      var b = el('div', 'sg-radius'); var box = el('div', 'sg-radius-box'); box.style.setProperty('--r', r.value);
      b.appendChild(box); b.appendChild(el('p', null, '<strong>' + esc(r.value) + '</strong>' + esc(r.what))); rad.appendChild(b);
    });

    // Imagery captions.
    document.querySelectorAll('[data-imagery]').forEach(function (n) { var it = g.imagery.items[+n.getAttribute('data-imagery')]; if (it) n.innerHTML = '<strong>' + esc(it.name) + '</strong> ' + esc(it.use); });

    // Voice.
    var v = document.getElementById('sgVoice');
    g.voice.rules.forEach(function (r) {
      var row = el('div', 'sg-voice-row');
      row.innerHTML = '<h4>' + esc(r.rule) + '</h4><p class="sg-v-do"><b>Do</b>' + esc(r.do) + '</p><p class="sg-v-dont"><b>Don\'t</b>' + esc(r.dont) + '</p>';
      v.appendChild(row);
    });
    function list(id, items) { var u = document.getElementById(id); items.forEach(function (t) { u.appendChild(el('li', null, esc(t))); }); }
    list('sgButtons', g.voice.buttons.rules);
    list('sgAudience', [g.audience.reader, g.audience.job_of_every_page, g.audience.one_idea]);
    list('sgCode', g.code_rules);
    list('sgOpen', g.open_questions);

    measure();
    status.textContent = bad ? (bad + ' color token(s) in style-guide.yaml no longer match the live CSS. See the red labels below.') : 'Built from style-guide.yaml (updated ' + g.meta.updated + '). All ' + g.colors.tokens.length + ' color tokens match the live CSS.';
    if (bad) status.classList.add('sg-bad');
  }

  function measure() {
    document.querySelectorAll('.sg-spec').forEach(function (spec) {
      var s = spec.querySelector('[data-sample]'), m = spec.querySelector('[data-measure]'); if (!s || !m) return;
      var cs = getComputedStyle(s);
      m.textContent = 'On this screen: ' + Math.round(parseFloat(cs.fontSize)) + 'px, weight ' + cs.fontWeight + (cs.fontStyle === 'italic' ? ', italic' : '');
    });
  }
  window.addEventListener('resize', function () { clearTimeout(measure.t); measure.t = setTimeout(measure, 150); });

  fetch('/style-guide.yaml', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
    .then(function (txt) { render(window.jsyaml.load(txt)); })
    .catch(function (e) { status.textContent = 'Could not load style-guide.yaml (' + e.message + '). Open it directly: /style-guide.yaml'; status.classList.add('sg-bad'); });
})();
