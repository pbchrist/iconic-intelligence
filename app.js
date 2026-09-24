(() => {
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // Mobile navigation
  const menuToggle = $('#menuToggle');
  const mobileNav = $('#mobileNav');
  if (menuToggle && mobileNav) {
    const closeMenu = () => { mobileNav.hidden = true; menuToggle.setAttribute('aria-expanded', 'false'); };
    menuToggle.addEventListener('click', () => {
      const opening = mobileNav.hidden;
      mobileNav.hidden = !opening;
      menuToggle.setAttribute('aria-expanded', String(opening));
    });
    $$('a', mobileNav).forEach((link) => link.addEventListener('click', closeMenu));
  }

  // Cursor light
  window.addEventListener('pointermove', (e) => {
    root.style.setProperty('--mx', `${e.clientX}px`);
    root.style.setProperty('--my', `${e.clientY}px`);
  }, { passive: true });

  // Reveal on scroll
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  $$('[data-reveal]').forEach((el, i) => {
    el.style.transitionDelay = `${Math.min((i % 5) * 45, 180)}ms`;
    revealObserver.observe(el);
  });

  // Header state
  const header = $('.site-header');
  const onScroll = () => {
    header.style.background = window.scrollY > 80 ? 'rgba(7, 9, 18, .84)' : 'rgba(7, 9, 18, .66)';
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Deterministic primary-nav state: nothing is active at the top.
  const navTargets = ['capability', 'dashboard', 'models', 'deployment', 'contact'];
  const navLinks = $$('.nav a[href^="#"]');
  const updateNavState = () => {
    if (window.scrollY < 180) {
      navLinks.forEach((link) => link.classList.remove('active'));
      return;
    }
    const line = Math.min(160, window.innerHeight * 0.28);
    let activeId = '';
    navTargets.forEach((id) => {
      const section = document.getElementById(id);
      if (!section) return;
      const rect = section.getBoundingClientRect();
      if (rect.top <= line && rect.bottom > line) activeId = id;
    });
    navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${activeId}`));
  };
  window.addEventListener('scroll', updateNavState, { passive: true });
  window.addEventListener('resize', updateNavState, { passive: true });
  updateNavState();

  // Dashboard tabs
  const tabTitles = {
    ask: 'ASK THE COMPANY INTELLIGENCE',
    intelligence: 'INTELLIGENCE FEED',
    work: 'WORK QUEUE',
    knowledge: 'BUSINESS KNOWLEDGE',
    control: 'CONTROL PLANE'
  };
  function openDashboardTab(tab, shouldScroll = false) {
    const button = $(`.dash-tab[data-tab="${tab}"]`);
    if (!button) return;
    $$('.dash-tab').forEach((b) => b.classList.toggle('active', b === button));
    $$('.dash-panel').forEach((panel) => panel.classList.toggle('active', panel.id === `panel-${tab}`));
    $('#dashTitle').textContent = tabTitles[tab] || tab.toUpperCase();
    if (shouldScroll) $('#dashboard')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  window.__ICONIC_OPEN_DASHBOARD_TAB__ = openDashboardTab;
  $$('.dash-tab').forEach((button) => button.addEventListener('click', () => openDashboardTab(button.dataset.tab)));

  const mapAction = $('#mapAction');
  mapAction?.addEventListener('click', () => openDashboardTab(mapAction.dataset.tab || 'ask', true));

  // Demo Ask intelligence
  const responses = [
    {
      match: /worried|risk|week/i,
      text: 'Two things deserve attention. First, a competitor cut advertised entry pricing across 11 listings this morning. Second, service wait-time complaints are clustering on Tuesdays. I would inspect margin exposure first, then staffing patterns.'
    },
    {
      match: /competitor|pricing|price/i,
      text: 'One primary competitor changed pricing. The median advertised entry price moved down 6.2% across the monitored set. The change is broad enough to look deliberate rather than inventory noise. I have a response brief ready.'
    },
    {
      match: /customer|complain|review/i,
      text: 'The strongest complaint cluster is service wait time, followed by communication gaps during handoffs. Tuesday mentions are now materially above the eight-week baseline. Positive mentions of staff courtesy remain strong.'
    },
    {
      match: /missing|opportun|what else/i,
      text: 'You may be underestimating a search opportunity. Competitors are weak on a high-intent category that has visible demand but poor local answers. I would test a dedicated offer page and measure qualified inbound response.'
    }
  ];

  function answerPrompt(prompt) {
    const conversation = $('#askConversation');
    const suggestionBox = $('.suggestions', conversation);
    if (suggestionBox) suggestionBox.style.display = 'none';

    const user = document.createElement('div');
    user.className = 'user-message';
    user.innerHTML = `<div><small>YOU</small><p>${escapeHtml(prompt)}</p></div>`;
    conversation.appendChild(user);

    const thinking = document.createElement('div');
    thinking.className = 'assistant-message';
    thinking.innerHTML = `<span class="sigil">✦</span><div><small>ICONIC INTELLIGENCE</small><p>Checking monitored signals, approved context and active procedures…</p></div>`;
    conversation.appendChild(thinking);
    conversation.scrollTop = conversation.scrollHeight;

    const found = responses.find((r) => r.match.test(prompt));
    const text = found?.text || 'I would treat that as an investigation rather than guess. I would identify the approved internal sources, search the relevant external signals, compare against the company baseline, and return the strongest findings with provenance and confidence.';
    window.setTimeout(() => {
      thinking.querySelector('p').textContent = text;
      conversation.scrollTop = conversation.scrollHeight;
    }, 650);
  }

  $$('.suggestions button').forEach((b) => b.addEventListener('click', () => answerPrompt(b.dataset.prompt)));
  $('#askForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = $('#askInput');
    const value = input.value.trim();
    if (!value) return;
    answerPrompt(value);
    input.value = '';
  });

  // Experiment lab
  const missions = {
    competitor: {
      label: 'COMPETITOR PRICING',
      source: '11 monitored listings + 4 offer pages',
      output: '3 material changes',
      result: 'Competitor entry pricing moved down. Response brief generated.'
    },
    reviews: {
      label: 'CUSTOMER VOICE',
      source: '428 reviews + 76 service notes',
      output: '2 complaint clusters',
      result: 'Tuesday wait-time complaints exceed the recent baseline.'
    },
    brief: {
      label: 'EXECUTIVE BRIEF',
      source: '7 internal + 18 external feeds',
      output: '5-item brief',
      result: 'Morning brief assembled with risks, opportunities and actions.'
    },
    vendor: {
      label: 'VENDOR RISK',
      source: 'Terms, price history + market signals',
      output: '1 emerging risk',
      result: 'Minimum-order change could create peak-demand exposure.'
    }
  };

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  function addTrace(time, step, detail, kind = '') {
    const trace = $('#traceOutput');
    const line = document.createElement('div');
    line.className = `trace-line ${kind}`;
    line.innerHTML = `<span class="time">${time}</span><span class="step">${step}</span><span class="detail">${detail}</span>`;
    trace.appendChild(line);
    trace.scrollTop = trace.scrollHeight;
  }

  $('#runExperiment').addEventListener('click', async () => {
    const mission = missions[$('#missionSelect').value];
    const trace = $('#traceOutput');
    const status = $('#labStatus');
    const result = $('#labResult');
    const runButton = $('#runExperiment');

    runButton.disabled = true;
    trace.innerHTML = '';
    status.className = 'running';
    status.innerHTML = '<i></i> RUNNING';
    [...result.children].forEach((d) => d.querySelector('strong').textContent = '…');

    addTrace('00:00.000', 'QUESTION', `${mission.label} accepted`);
    await wait(220);
    addTrace('00:00.021', 'CONTEXT', `Loaded approved business context + ${mission.source}`);
    await wait(280);
    addTrace('00:00.084', 'RESEARCH', 'Checking internal context and monitored external signals');
    await wait(320);
    addTrace('00:00.327', 'VERIFY', 'Cross-checking material claims against independent evidence');
    await wait(320);
    addTrace('00:00.691', 'POLICY', 'Read-only intelligence task → autonomous execution permitted', 'ok');
    await wait(280);
    addTrace('00:00.931', 'RESULT', `${mission.output} · confidence gate passed`, 'ok');
    await wait(220);
    addTrace('00:01.144', 'EXEC BRIEF', mission.result, 'ok');

    const vals = result.querySelectorAll('strong');
    vals[0].textContent = 'AUTOMATIC';
    vals[1].textContent = 'AUTO / LOW RISK';
    vals[2].textContent = 'CROSS-CHECKED';
    vals[3].textContent = mission.output.toUpperCase();
    status.className = 'done';
    status.innerHTML = '<i></i> COMPLETE';
    runButton.disabled = false;
  });

  // Basic 2D fallback field so the site still looks alive if Three.js cannot load.
  // three-scene.js replaces this renderer when the remote module is available.
  const canvas = $('#field');
  const ctx = canvas.getContext('2d');
  let width = 0, height = 0, dpr = 1;
  let fallbackRunning = true;
  const particles = Array.from({ length: 110 }, () => ({
    x: Math.random(), y: Math.random(), z: Math.random(),
    vx: (Math.random() - .5) * .00007, vy: (Math.random() - .5) * .00005
  }));

  function resizeCanvas() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.7);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas, { passive: true });

  function fallbackFrame() {
    if (!fallbackRunning) return;
    ctx.clearRect(0, 0, width, height);
    const gx = width * .72, gy = height * .46;
    const grd = ctx.createRadialGradient(gx, gy, 0, gx, gy, Math.max(width, height) * .45);
    grd.addColorStop(0, 'rgba(82, 91, 199, .10)');
    grd.addColorStop(1, 'rgba(7, 9, 18, 0)');
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, width, height);

    particles.forEach((p) => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > 1) p.vx *= -1;
      if (p.y < 0 || p.y > 1) p.vy *= -1;
      const x = p.x * width, y = p.y * height;
      const r = .7 + p.z * 1.2;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(185, 192, 255, ${.08 + p.z * .22})`;
      ctx.fill();
    });
    requestAnimationFrame(fallbackFrame);
  }
  requestAnimationFrame(fallbackFrame);
  window.__ICONIC_STOP_FALLBACK__ = () => { fallbackRunning = false; ctx.clearRect(0, 0, width, height); };

  function escapeHtml(value) {
    return value.replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#039;', '"':'&quot;' }[char]));
  }
})();
