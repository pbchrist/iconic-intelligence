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
  const navTargets = ['own', 'uses', 'proof', 'ways'];
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

  // The compounding widget reports its height so it fits on small screens.
  const ciFrame = $('#ciFrame');
  window.addEventListener('message', (event) => {
    const data = event.data || {};
    if (data.source !== 'iconic-compounding') return;
    if (data.type === 'height' && ciFrame) {
      const height = Math.max(400, Math.min(Number(data.height) || 0, 3000));
      if (height) ciFrame.style.height = `${height}px`;
    }
  });

  // Who it's for: five use cases, toggled by the buttons and rotated slowly.
  const useCases = {
    law: { client:'LAW FIRM', title:'Every matter the firm has handled, in one place it controls.', body:'Briefs, contracts, research and correspondence from every matter, searchable in plain English on a computer inside the firm.', ask:'“Have we argued this before, and how did it go?”', holds:'Matters · briefs · contracts · research · correspondence', why:'Client confidences never leave the firm.', runs:'A Monday brief on every open matter, deadline alerts, and first drafts from the firm\'s own past work.', more:'The American Bar Association\'s Formal Opinion 512 (July 2024) says lawyers using AI must protect client confidences, understand the tools they use, and in some cases get the client\'s informed consent before putting client information into one. A system inside the firm makes that much simpler.', check:'A lawyer reviews anything that matters.' },
    wealth: { client:'WEALTH MANAGEMENT', title:'Know the whole client before the meeting starts.', body:'Meeting notes, plans, account reviews and years of letters and emails, kept together so the advisor walks in knowing everything the firm knows.', ask:'“What has this client told us about risk and family over the last three years?”', holds:'Meeting notes · plans · reviews · correspondence', why:'Client finances and family details stay in your office.', runs:'A brief on every client before each meeting, alerts when a client\'s situation changes, and draft follow-up letters in the advisor\'s voice.', more:'The SEC\'s Regulation S-P requires firms to protect customer information, and since its 2024 update, to be ready to detect, respond to and notify clients of a breach. Every outside service holding client data is one more place to watch.', check:'The advisor reviews anything sent to a client.' },
    realestate: { client:'REAL ESTATE', title:'Your deal history is your edge. Keep it.', body:'Every deal, lease, comp, inspection and negotiation note, so the next negotiation starts with everything you learned from the last ones.', ask:'“What did we give up on the last three leases like this one?”', holds:'Deals · leases · comps · inspections · negotiation notes', why:'Your terms and your counterparties stay private.', runs:'A weekly read on new listings and comps in your markets, lease-date reminders, and first drafts of offers built from your past deals.', more:'There\'s no single rule here. It\'s leverage: what you paid, what you gave up and who you dealt with is exactly what the other side of the table would love to know. Once it\'s uploaded, someone else\'s terms of service decide what happens to it.', check:'The broker reviews anything that matters.' },
    owner: { client:'OWNER-RUN COMPANY', title:'Twenty years of how the business works, kept by the business.', body:'Customers, vendors, pricing, contracts and procedures, including what the people who retired or moved on used to know.', ask:'“What did we pay this vendor last year, and what did they promise?”', holds:'Customers · vendors · pricing · contracts · procedures', why:'How your business runs is not anyone else\'s data.', runs:'A Monday summary of the business, alerts when a vendor\'s prices change, and answers to the questions only the old-timers used to know.', more:'No regulator required. Your pricing, vendor terms and customer list are the business. Once they\'re in someone else\'s system, their terms of service decide what happens to them.', check:'You decide what it can see and who can ask it.' },
    accounting: { client:'ACCOUNTING FIRM', title:'Every client year, one question away.', body:'Returns, workpapers, client letters and the decisions made along the way, so the firm can see what it decided for a client and why.', ask:'“What did we decide for this client on this issue two years ago, and why?”', holds:'Returns · workpapers · client letters · prior-year decisions', why:'Taxpayer information stays on your own computer.', runs:'Deadline tracking across every client, a first pass on workpapers, and draft client letters built from prior years\' decisions.', more:'Federal tax law (Internal Revenue Code section 7216) puts strict limits on a tax preparer disclosing or using a client\'s return information without written consent, including sending it to outside services. A system on the firm\'s own computer keeps it in the firm.', check:'A CPA reviews anything that matters.' }
  };
  const caseOrder = Object.keys(useCases);
  let caseIndex = 0, caseTimer = null;
  const setText = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };
  function renderUseCase(id) {
    const d = useCases[id]; if (!d) return;
    caseIndex = caseOrder.indexOf(id);
    setText('useCaseClient', d.client); setText('useCaseTitle', d.title); setText('useCaseBody', d.body);
    setText('useCaseAsk', d.ask); setText('useCaseHolds', d.holds); setText('useCaseWhy', d.why); setText('useCaseRuns', d.runs); setText('useCaseMore', d.more); setText('useCaseCheck', d.check);
    $$('.use-case-dots button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.case === id)));
    const copy = $('#useCaseCopy');
    if (copy?.animate) copy.animate([{ opacity:.34, transform:'translateY(5px)' }, { opacity:1, transform:'none' }], { duration:360, easing:'ease-out' });
  }
  function armRotation() {
    clearInterval(caseTimer);
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    caseTimer = setInterval(() => renderUseCase(caseOrder[(caseIndex + 1) % caseOrder.length]), 7000);
  }
  $$('.use-case-dots button').forEach((b) => b.addEventListener('click', () => { renderUseCase(b.dataset.case); clearInterval(caseTimer); }));
  if ($('#useCaseCopy')) armRotation();

  // Phones: a slim "book" button pinned to the bottom, shown once the hero is passed,
  // hidden while either free-check offer block is on screen.
  const sticky = $('#stickyCta');
  if (sticky && 'IntersectionObserver' in window) {
    const watched = ['.hero', '#check', '#start', '#contact'].map((sel) => $(sel)).filter(Boolean);
    const visible = new Set();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => e.isIntersecting ? visible.add(e.target) : visible.delete(e.target));
      const show = visible.size === 0;
      sticky.classList.toggle('show', show);
      sticky.setAttribute('aria-hidden', String(!show));
      sticky.tabIndex = show ? 0 : -1;
    }, { threshold: 0.05 });
    watched.forEach((el) => io.observe(el));
  }

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
