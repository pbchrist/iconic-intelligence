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
  const navTargets = ['proof', 'brief', 'pricing', 'start'];
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

  // Compounding signal thread + independent cross-industry use-case rotator.
  const ciFrame = $('#ciFrame');
  const signalData = {
    pricing: { missionValue:'competitor', quote:'I hear about a competitor move from a client.', question:'Which competitor changed pricing?', answer:'A primary competitor moved advertised entry pricing down across the listings being watched. The pattern is broad enough to look deliberate, so a response brief is ready.' },
    reviews: { missionValue:'reviews', quote:'We have a pile of client comments and nobody reads them as one picture.', question:'What are customers complaining about?', answer:'The strongest complaint cluster is service wait time, then gaps when a job changes hands. Courtesy still shows up as a counter-signal.' },
    vendor: { missionValue:'vendor', quote:'We notice a market or supplier change too late.', question:'Where is exposure building?', answer:'Supplier and market changes sit on the same watch-list, so a developing constraint shows up before it becomes a separate fire drill.' },
    market: { missionValue:'brief', quote:'Tell me what changed in my market every Monday morning.', question:'What changed in my market?', answer:'The Monday brief says what changed, why it matters here, and what deserves attention this week.' }
  };
  const useCases = {
    live: { kicker:'LIVE PROOF · AUTOMOTIVE', client:'A NORTHERN CALIFORNIA AUTO DEALERSHIP', title:'A Monday report the GM reads.', body:'A Sacramento-area dealership runs an always-on assistant and a Monday market report. The general manager reads it every week.', resultLabel:'WHAT IS LIVE', result:'An always-on assistant, and a Monday market report the general manager reads every week.', watchLabel:'RUNS', watch:'An assistant that stays on', surfaceLabel:'SENDS', surface:'A Monday market report', deliverLabel:'READS', deliver:'The general manager, every week' },
    legal: { kicker:'THE OFFER · LAW FIRMS', client:'MANAGING PARTNERS · 5 TO 40 LAWYERS', title:'Monday, before someone else moves.', body:'A Monday Market Brief for managing partners of firms with 5 to 40 lawyers in Seattle and on the Eastside. What changed, why it matters to your clients, and what is worth doing this week.', resultLabel:'EVERY MONDAY', result:'A written brief your team can run. A person sends anything that goes to a client.', watchLabel:'WATCHES', watch:'The market a partner has to know', surfaceLabel:'TIES TO', surface:'Your clients or matters', deliverLabel:'DELIVERS', deliver:'One brief, every Monday' },
    wealth: { kicker:'ALSO FOR · WEALTH MANAGERS', client:'ADVISORS', title:'The same Monday habit.', body:'Wealth managers get the same setup: private hardware, a written policy, and a team taught to run it. The brief is there before the client asks.', resultLabel:'THE SETUP', result:'Private hardware, a written policy, and your team taught to run it.', watchLabel:'FOR', watch:'Advisors whose clients will ask', surfaceLabel:'BRINGS', surface:'What changed, before the meeting', deliverLabel:'KEEPS', deliver:'The work on your hardware' },
    owners: { kicker:'ALSO FOR · OWNERS', client:'WAC MEMBERS', title:'Start in the room you are already in.', body:'The first conversations are with Washington Athletic Club members: attorneys, wealth managers, and business owners.', resultLabel:'WHERE IT STARTS', result:'A conversation, then a fixed-price setup when a Monday brief fits.', watchLabel:'WHO', watch:'Attorneys, wealth managers, owners', surfaceLabel:'WHERE', surface:'Washington Athletic Club members', deliverLabel:'NEXT', deliver:'A conversation, then a setup when it fits' }
  };
  const caseOrder = ['live','legal','wealth','owners'];
  let caseIndex = 0;
  let currentSignal = 'pricing';

  function renderUseCase(id) {
    const d = useCases[id] || useCases.live;
    caseIndex = Math.max(0, caseOrder.indexOf(id));
    $('#useCaseKicker') && ($('#useCaseKicker').textContent = d.kicker);
    $('#useCaseClient') && ($('#useCaseClient').textContent = d.client);
    $('#useCaseTitle') && ($('#useCaseTitle').textContent = d.title);
    $('#useCaseBody') && ($('#useCaseBody').textContent = d.body);
    $('#useCaseResult') && ($('#useCaseResult').innerHTML = `<strong>${escapeHtml(d.resultLabel || 'OUTPUT')}</strong> ${escapeHtml(d.result)}`);
    $('#useCaseWatchLabel') && ($('#useCaseWatchLabel').textContent = d.watchLabel || 'WATCHES');
    $('#useCaseSurfaceLabel') && ($('#useCaseSurfaceLabel').textContent = d.surfaceLabel || 'SURFACES');
    $('#useCaseDeliverLabel') && ($('#useCaseDeliverLabel').textContent = d.deliverLabel || 'DELIVERS');
    $('#useCaseWatch') && ($('#useCaseWatch').textContent = d.watch);
    $('#useCaseSurface') && ($('#useCaseSurface').textContent = d.surface);
    $('#useCaseDeliver') && ($('#useCaseDeliver').textContent = d.deliver);
    $$('.use-case-dots button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.case === id)));
    const copy = $('#useCaseCopy');
    if (copy?.animate) copy.animate([{opacity:.34,transform:'translateY(5px)'},{opacity:1,transform:'none'}],{duration:360,easing:'ease-out'});
  }
  $$('.use-case-dots button').forEach((b) => b.addEventListener('click', () => { renderUseCase(b.dataset.case); }));
  renderUseCase(caseOrder[0]);

  function renderDashboardThread(id) {
    const d = signalData[id] || signalData.pricing;
    const thread = $('.prefill-thread');
    if (!thread) return;
    thread.innerHTML = `<div class="user-message"><div><small>YOU</small><p>${escapeHtml(d.question)}</p></div></div><div class="assistant-message"><span class="sigil">✦</span><div><small>ICONIC INTELLIGENCE</small><p>${escapeHtml(d.answer)}</p></div></div>`;
  }
  function renderProblemThread(id) {
    const d = signalData[id] || signalData.pricing;
    const select = $('#missionSelect');
    if (select) select.value = d.missionValue;
    $$('#problemExamples button').forEach((button) => button.classList.toggle('active', button.dataset.signal === id));
  }
  function setSignal(id, { syncWidget = false } = {}) {
    if (!signalData[id]) return;
    currentSignal = id;
    renderDashboardThread(id);
    renderProblemThread(id);
    document.documentElement.dataset.iconicSignal = id;
    if (syncWidget && ciFrame?.contentWindow) ciFrame.contentWindow.postMessage({ source:'iconic-site', type:'setSignal', id }, '*');
  }
  $$('#problemExamples button').forEach((button) => button.addEventListener('click', () => {
    const id = button.dataset.signal;
    if (signalData[id]) setSignal(id, { syncWidget:true });
    else if (button.dataset.mission && $('#missionSelect')) $('#missionSelect').value = button.dataset.mission;
  }));
  window.addEventListener('message', (event) => {
    const data = event.data || {};
    if (data.source !== 'iconic-compounding') return;
    if (data.type === 'height' && ciFrame && window.innerWidth < 980) {
      const height = Math.max(620, Math.min(Number(data.height) || 0, 2200));
      if (height) ciFrame.style.height = `${height}px`;
    }
    if ((data.type === 'signal' || data.type === 'ready') && data.signal?.id) setSignal(data.signal.id);
  });
  setSignal('pricing');

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
      match: /monday/i,
      text: 'Three things: what changed, which clients or matters it touches, and what can wait.'
    },
    {
      match: /worried|risk|week/i,
      text: 'Two things to look at. A competitor moved advertised entry pricing, and service complaints are clustering on one weekday. Margin first, then staffing.'
    },
    {
      match: /competitor|pricing|price/i,
      text: 'One primary competitor changed advertised entry pricing. The move looks deliberate. A response brief is ready.'
    },
    {
      match: /customer|complain|review/i,
      text: 'The strongest complaint cluster is service wait time, then gaps when work changes hands. Courtesy still shows up as a counter-signal.'
    },
    {
      match: /missing|opportun|what else/i,
      text: 'Clients are already asking a question competitors answer thinly. The brief names that question once it has been checked.'
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
      source: 'watched listings + offer pages',
      output: 'Pricing moves',
      result: 'Competitor entry pricing moved. A response brief is ready.',
      brief: ['Watched listings moved in the same direction.', 'The move looks deliberate.', 'A person reviews the affected offers before any price change.', 'The competitor set stays on the watch-list.']
    },
    reviews: {
      label: 'CUSTOMER VOICE',
      source: 'reviews + service notes',
      output: 'Complaint clusters',
      result: 'Wait-time complaints are the strongest cluster.',
      brief: ['Wait-time complaints cluster on one weekday.', 'Handoff complaints are the second theme.', 'Courtesy still shows up as a counter-signal.', 'A person looks at staffing and handoffs before acting.']
    },
    brief: {
      label: 'MONDAY BRIEF',
      source: 'internal notes + market watch',
      output: 'Monday brief',
      result: 'What changed, why it matters, and what can wait.',
      brief: ['What changed: one competitor pricing move.', 'Why it matters: it touches offers you still advertise.', 'What can wait: no vendor change needs a decision today.', 'A person decides what goes out.']
    },
    vendor: {
      label: 'VENDOR RISK',
      source: 'terms + market notes',
      output: 'Terms change',
      result: 'A terms change that can matter at peak demand.',
      brief: ['A supplier changed minimum-order terms.', 'Exposure looks limited at normal demand.', 'Peak demand is where it can matter.', 'Compare a backup before the next order. A person decides.']
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
