(() => {
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // Mobile navigation
  const menuToggle = $('#menuToggle');
  const mobileNav = $('#mobileNav');
  if (menuToggle && mobileNav) {
    const closeMenu = () => { mobileNav.hidden = true; menuToggle.setAttribute('aria-expanded', 'false'); };
    menuToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const opening = mobileNav.hidden;
      mobileNav.hidden = !opening;
      menuToggle.setAttribute('aria-expanded', String(opening));
    });
    $$('a', mobileNav).forEach((link) => link.addEventListener('click', closeMenu));
    window.addEventListener('scroll', closeMenu, { passive: true });
    document.addEventListener('pointerdown', (event) => {
      if (!mobileNav.hidden && !mobileNav.contains(event.target) && !menuToggle.contains(event.target)) closeMenu();
    });
    window.addEventListener('resize', () => { if (window.innerWidth >= 900) closeMenu(); }, { passive: true });
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
  const navTargets = ['how', 'running', 'demo'];
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
    ask: 'ASK THE SAMPLE DESK',
    intelligence: 'SAMPLE FINDINGS',
    work: 'SAMPLE QUEUE',
    knowledge: 'SAMPLE MEMORY',
    control: 'WHERE I STAY IN IT'
  };
  function openDashboardTab(tab, shouldScroll = false) {
    const button = $(`.dash-tab[data-tab="${tab}"]`);
    if (!button) return;
    $$('.dash-tab').forEach((b) => b.classList.toggle('active', b === button));
    $$('.dash-panel').forEach((panel) => panel.classList.toggle('active', panel.id === `panel-${tab}`));
    $('#dashTitle').textContent = tabTitles[tab] || tab.toUpperCase();
    if (shouldScroll) $('#demo')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  window.__ICONIC_OPEN_DASHBOARD_TAB__ = openDashboardTab;
  $$('.dash-tab').forEach((button) => button.addEventListener('click', () => openDashboardTab(button.dataset.tab)));

  const mapAction = $('#mapAction');
  mapAction?.addEventListener('click', () => openDashboardTab(mapAction.dataset.tab || 'ask', true));

  // Demo Ask intelligence. Price questions about the offer get a straight answer.
  const offerPriceAnswer = 'I quote the price on a 20-minute call, once I know your market. Email patrick@iconic.onl or call 206-773-8214.';
  function isOfferPriceQuestion(prompt) {
    const p = prompt.trim().toLowerCase();
    const aboutLots = /\b(rival|competitor|lot|truck|vin|inventory|listing)s?\b/.test(p);
    const aboutOffer = /\b(how much|what do you charge|what does (?:this|it|a report|iconic) cost|your (?:price|fee|fees|rate|pricing)|iconic(?:'s)? (?:price|cost|fee)|cost to (?:start|hire)|do you charge|retainer|what(?:'s| is) (?:the |your )?(?:price|cost|fee))\b/.test(p)
      || /^(?:what(?:'s| is) )?(?:the )?(?:price|pricing|cost|fee|fees)\??$/.test(p);
    if (aboutLots && !/\b(you charge|your (?:price|fee)|iconic|this cost|a report cost)\b/.test(p)) return false;
    return aboutOffer;
  }
  const responses = [
    {
      match: /worried|worry|risk|week/i,
      text: 'Sample only. I would look for a rival sticker that moved on a like-for-like truck. You would see that in the Monday, Wednesday or Friday morning report, and none goes out until I approve it.'
    },
    {
      match: /where|source|quote|number come|trace/i,
      text: 'Sample only. A real number points to the dated listing or page it came from.'
    },
    {
      match: /rival|competitor|price|pricing|sticker|truck/i,
      text: 'Sample only. I would name the rival, the truck and the sticker. Like for like means the same year, model, trim, cab, drive and engine, with sticker prices within $1,000. None of that goes out until I approve it.'
    }
  ];

  function answerPrompt(prompt) {
    const conversation = $('#askConversation');
    const suggestionBox = $('.suggestions', conversation);
    if (suggestionBox) suggestionBox.style.display = 'none';

    const user = document.createElement('div');
    user.className = 'user-message';
    user.innerHTML = `<div><small>You</small><p>${escapeHtml(prompt)}</p></div>`;
    conversation.appendChild(user);

    const thinking = document.createElement('div');
    thinking.className = 'assistant-message';
    thinking.innerHTML = `<span class="sigil">✦</span><div><small>ICONIC</small><p>One moment.</p></div>`;
    conversation.appendChild(thinking);
    conversation.scrollTop = conversation.scrollHeight;

    const text = isOfferPriceQuestion(prompt)
      ? offerPriceAnswer
      : (responses.find((r) => r.match.test(prompt))?.text
        || 'This box only knows the sample desk. For your store, email patrick@iconic.onl with your business, your top three competitors, and what you wish you knew every Monday.');
    window.setTimeout(() => {
      thinking.querySelector('p').textContent = text;
      conversation.scrollTop = conversation.scrollHeight;
    }, 400);
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
    price: {
      label: 'RIVAL STICKER',
      result: 'Sample: a like-for-like sticker moved. This is not a client report.',
      brief: [
        'Sample only. This is not a client report.',
        'A like-for-like truck is the same year, model, trim, cab, drive and engine.',
        'Sticker prices have to sit within $1,000 of each other.',
        'A real number would point to the dated listing or page it came from.',
        'None of it goes out until I approve it.'
      ]
    },
    source: {
      label: 'WHERE A NUMBER COMES FROM',
      result: 'Sample: the number points at a dated public page.',
      brief: [
        'Sample only.',
        'Every number in a briefing points to the dated listing or page it came from.',
        'None goes out until I approve it.'
      ]
    },
    morning: {
      label: 'MORNING REPORT',
      result: 'Sample: Monday, Wednesday and Friday mornings.',
      brief: [
        'Sample only.',
        'The live report goes out on Monday, Wednesday and Friday mornings.',
        'Every morning it reads the rivals\' Sierra 1500 lots: each truck, price, trim and VIN.',
        'None goes out until I approve it.'
      ]
    },
    ask: {
      label: 'A QUESTION',
      result: 'Sample: the bot can take a question. The report still waits for approval.',
      brief: [
        'Sample only.',
        'Between reports, they can text questions to a private Telegram bot.',
        'The report is separate, and I approve it before it goes out.',
        'For a price, use Start with your market and email patrick@iconic.onl.'
      ]
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
    const sampleBrief = $('#sampleBrief');
    const sampleBriefLines = $('#sampleBriefLines');
    const runButton = $('#runExperiment');

    runButton.disabled = true;
    trace.innerHTML = '';
    status.className = 'running';
    status.innerHTML = '<i></i> RUNNING';
    [...result.children].forEach((d) => d.querySelector('strong').textContent = '…');
    if (sampleBrief) sampleBrief.hidden = true;
    if (sampleBriefLines) sampleBriefLines.innerHTML = '';

    addTrace('01', 'QUESTION', `${mission.label} — sample`);
    await wait(420);
    addTrace('02', 'LOTS', 'Read the sample snapshots. Not a client file.');
    await wait(420);
    addTrace('03', 'COMPARE', 'Like for like: year, model, trim, cab, drive, engine. Stickers within $1,000.');
    await wait(420);
    addTrace('04', 'SOURCE', 'A real number would point to the dated listing or page it came from.');
    await wait(420);
    addTrace('05', 'APPROVAL', 'None goes out until I approve it.', 'ok');
    await wait(360);
    addTrace('06', 'BRIEF', mission.result, 'ok');

    const vals = result.querySelectorAll('strong');
    vals[0].textContent = 'SAMPLE';
    vals[1].textContent = 'MY READ';
    vals[2].textContent = 'NOT LIVE';
    vals[3].textContent = 'SAMPLE BRIEF';
    if (sampleBriefLines) sampleBriefLines.innerHTML = mission.brief.map((line) => `<p>${escapeHtml(line)}</p>`).join('');
    if (sampleBrief) sampleBrief.hidden = false;
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
    dpr = 1;
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
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) requestAnimationFrame(fallbackFrame);
  window.__ICONIC_STOP_FALLBACK__ = () => { fallbackRunning = false; ctx.clearRect(0, 0, width, height); };

  function escapeHtml(value) {
    return value.replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#039;', '"':'&quot;' }[char]));
  }
})();
