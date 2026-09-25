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
  const navTargets = ['capability', 'dashboard', 'deployment'];
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

  // One storyline threads from the compounding widget through proof, dashboard and the closing demo.
  const ciFrame = $('#ciFrame');
  const signalData = {
    pricing: {
      missionValue: 'competitor', mission: 'Find competitor pricing changes', quote: 'I never know when competitors change their offers.',
      title: 'Competitor pricing that keeps watching.',
      body: 'ICONIC monitors competitor offers and pricing transparency, then carries material changes into recurring executive intelligence instead of waiting for someone to remember to search.',
      watch: 'Offers · advertised pricing · pricing transparency', surface: 'Material competitor moves worth attention', deliver: 'Recurring executive intelligence',
      question: 'Which competitor changed pricing?', answer: 'A primary competitor moved advertised entry pricing down across 11 monitored listings. The pattern is broad enough to look deliberate, so I prepared a response brief with the affected offers and what changed.'
    },
    reviews: {
      missionValue: 'reviews', mission: 'Analyze customer complaints', quote: 'We have hundreds of reviews and nobody is synthesizing them.',
      title: 'Customer signals without the review slog.',
      body: 'ICONIC monitors reviews alongside the rest of the competitive picture so recurring themes can be surfaced without an owner or manager reading hundreds of comments by hand.',
      watch: 'Reviews · complaint themes · service signals', surface: 'Patterns that strengthen enough to deserve attention', deliver: 'Recurring customer-voice intelligence',
      question: 'What are customers complaining about?', answer: 'The strongest complaint cluster is service wait time, followed by communication gaps during handoffs. Positive mentions of staff courtesy remain a useful counter-signal.'
    },
    vendor: {
      missionValue: 'vendor', mission: 'Investigate a vendor risk', quote: 'We notice pricing, inventory or search changes too late.',
      title: 'Inventory and service exposure in the same picture.',
      body: 'The automotive deployment already watches inventory and service alongside competitor movement, so emerging operating exposure can sit in the same executive intelligence stream.',
      watch: 'Inventory · service · operating exposure', surface: 'Changes that could affect availability or response', deliver: 'One recurring executive picture',
      question: 'Where is operating exposure building?', answer: 'Inventory and service signals are tracked beside competitor changes so a developing constraint can be investigated before it becomes a separate fire drill.'
    },
    market: {
      missionValue: 'brief', mission: 'Build an executive morning brief', quote: 'Tell me what changed in my market every Monday morning.',
      title: 'Market visibility that arrives before the meeting.',
      body: 'ICONIC monitors search visibility and competitor movement alongside pricing, reviews and inventory, then condenses what changed into recurring executive intelligence.',
      watch: 'Search visibility · competitors · market movement', surface: 'Changes and gaps worth a closer look', deliver: 'A recurring executive brief',
      question: 'What changed in my market?', answer: 'A local search gap remains under-contested while competitor pricing and offer movement continue to be watched. The point is one brief that says what changed and what deserves attention.'
    }
  };
  let currentSignal = 'pricing';
  let useCaseIndex = 0;
  const signalOrder = ['pricing', 'reviews', 'vendor', 'market'];
  let useCaseTimer = null;

  function renderUseCase(id, { thread = false } = {}) {
    const data = signalData[id] || signalData.pricing;
    useCaseIndex = Math.max(0, signalOrder.indexOf(id));
    $('#useCaseTitle') && ($('#useCaseTitle').textContent = data.title);
    $('#useCaseBody') && ($('#useCaseBody').textContent = data.body);
    $('#useCaseWatch') && ($('#useCaseWatch').textContent = data.watch);
    $('#useCaseSurface') && ($('#useCaseSurface').textContent = data.surface);
    $('#useCaseDeliver') && ($('#useCaseDeliver').textContent = data.deliver);
    $$('.use-case-dots button').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.signal === id)));
    const caseCopy = $('#useCaseCopy');
    if (caseCopy?.animate) caseCopy.animate([{opacity:.35,transform:'translateY(4px)'},{opacity:1,transform:'none'}],{duration:360,easing:'ease-out'});
    if (thread) setSignal(id, { syncWidget: true, resetRotation: true });
  }

  function renderDashboardThread(id) {
    const data = signalData[id] || signalData.pricing;
    const thread = $('.prefill-thread');
    if (!thread) return;
    thread.innerHTML = `<div class="user-message"><div><small>YOU</small><p>${escapeHtml(data.question)}</p></div></div><div class="assistant-message"><span class="sigil">✦</span><div><small>ICONIC INTELLIGENCE</small><p>${escapeHtml(data.answer)}</p></div></div>`;
  }

  function renderProblemThread(id) {
    const data = signalData[id] || signalData.pricing;
    const select = $('#missionSelect');
    if (select) select.value = data.missionValue;
    $$('#problemExamples button').forEach((button) => button.classList.toggle('active', button.dataset.signal === id));
  }

  function setSignal(id, { syncWidget = false, resetRotation = false } = {}) {
    if (!signalData[id]) return;
    currentSignal = id;
    renderUseCase(id);
    renderDashboardThread(id);
    renderProblemThread(id);
    document.documentElement.dataset.iconicSignal = id;
    if (syncWidget && ciFrame?.contentWindow) ciFrame.contentWindow.postMessage({ source: 'iconic-site', type: 'setSignal', id }, '*');
    if (resetRotation) armUseCaseRotation();
  }

  function armUseCaseRotation() {
    clearInterval(useCaseTimer);
    useCaseIndex = Math.max(0, signalOrder.indexOf(currentSignal));
    useCaseTimer = setInterval(() => {
      useCaseIndex = (useCaseIndex + 1) % signalOrder.length;
      renderUseCase(signalOrder[useCaseIndex]);
    }, 6500);
  }
  const useCaseSection = $('.use-case-section');
  useCaseSection?.addEventListener('mouseenter', () => clearInterval(useCaseTimer));
  useCaseSection?.addEventListener('mouseleave', armUseCaseRotation);
  $$('.use-case-dots button').forEach((button) => button.addEventListener('click', () => renderUseCase(button.dataset.signal, { thread: true })));

  $$('#problemExamples button').forEach((button) => button.addEventListener('click', () => {
    const id = button.dataset.signal;
    if (signalData[id]) setSignal(id, { syncWidget: true, resetRotation: true });
    else if (button.dataset.mission && $('#missionSelect')) $('#missionSelect').value = button.dataset.mission;
  }));

  window.addEventListener('message', (event) => {
    const data = event.data || {};
    if (data.source !== 'iconic-compounding') return;
    if (data.type === 'height' && ciFrame && window.innerWidth < 980) {
      const height = Math.max(620, Math.min(Number(data.height) || 0, 2200));
      if (height) ciFrame.style.height = `${height}px`;
    }
    if ((data.type === 'signal' || data.type === 'ready') && data.signal?.id) setSignal(data.signal.id, { resetRotation: true });
  });

  setSignal('pricing');
  armUseCaseRotation();

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
      result: 'Competitor entry pricing moved down. Response brief generated.',
      brief: ['11 monitored listings changed in the same direction.', 'The move appears deliberate rather than inventory noise.', 'Review the affected offers before the next pricing meeting.', 'Keep the competitor set on watch for follow-on changes.']
    },
    reviews: {
      label: 'CUSTOMER VOICE',
      source: '428 reviews + 76 service notes',
      output: '2 complaint clusters',
      result: 'Tuesday wait-time complaints exceed the recent baseline.',
      brief: ['Wait-time complaints are clustering around Tuesdays.', 'Communication handoff complaints are the second strongest theme.', 'Staff courtesy remains a positive counter-signal.', 'Review Tuesday staffing and handoff coverage first.']
    },
    brief: {
      label: 'EXECUTIVE BRIEF',
      source: '7 internal + 18 external feeds',
      output: '5-item brief',
      result: 'Morning brief assembled with risks, opportunities and actions.',
      brief: ['One competitor pricing move deserves attention.', 'Service complaints strengthened around a recurring daypart.', 'A local search gap remains under-contested.', 'No material vendor change requires action this morning.']
    },
    vendor: {
      label: 'VENDOR RISK',
      source: 'Terms, price history + market signals',
      output: '1 emerging risk',
      result: 'Minimum-order change could create peak-demand exposure.',
      brief: ['A supplier changed minimum-order terms.', 'Current exposure is limited at normal demand.', 'Peak-demand inventory could be affected.', 'Compare alternate supplier terms before the next reorder.']
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

    addTrace('01', 'QUESTION', `${mission.label} accepted`);
    await wait(650);
    addTrace('02', 'CONTEXT', `Loaded approved business context + ${mission.source}`);
    await wait(720);
    addTrace('03', 'RESEARCH', 'Checking internal context and monitored external signals');
    await wait(820);
    addTrace('04', 'VERIFY', 'Cross-checking material claims against independent evidence');
    await wait(820);
    addTrace('05', 'POLICY', 'Read-only intelligence task → autonomous execution permitted', 'ok');
    await wait(720);
    addTrace('06', 'RESULT', `${mission.output} · confidence gate passed`, 'ok');
    await wait(650);
    addTrace('07', 'EXEC BRIEF', mission.result, 'ok');

    const vals = result.querySelectorAll('strong');
    vals[0].textContent = 'AUTOMATIC';
    vals[1].textContent = 'AUTO / LOW RISK';
    vals[2].textContent = 'CROSS-CHECKED';
    vals[3].textContent = mission.output.toUpperCase();
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
