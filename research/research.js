/* Research articles: highlight the current section in the side rail and the mobile chip row. */
(() => {
  const links = [...document.querySelectorAll('.rv-rail a[href^="#"], .rv-chipnav a[href^="#"]')];
  if (!links.length) return;
  const ids = [...new Set(links.map((a) => a.getAttribute('href').slice(1)))];
  const chipNav = document.querySelector('.rv-chipnav');
  const docs = document.querySelector('.rv-docs');
  let last = '';
  function update() {
    const line = Math.min(220, window.innerHeight * 0.32);
    let active = '';
    ids.forEach((id) => { const el = document.getElementById(id); if (el && el.getBoundingClientRect().top <= line) active = id; });
    if (docs && docs.getBoundingClientRect().bottom < line) active = '';
    links.forEach((a) => {
      const on = a.getAttribute('href') === '#' + active;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    if (active !== last && chipNav) {
      const chip = chipNav.querySelector('a[href="#' + active + '"]');
      if (chip) chipNav.scrollTo({ left: chip.offsetLeft - 16, behavior: 'smooth' });
      last = active;
    }
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update, { passive: true });
  update();
})();
