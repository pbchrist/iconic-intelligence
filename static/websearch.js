// Optional add-on: ask before searching the open web. Pairs with websearch.py.
// Delete both files to take it out; app.js works without them.
(() => {
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const css = document.createElement('style');
  css.textContent = `
.web-ask { margin: 14px 0 0 48px; padding: 14px 16px; border: 1px solid var(--line-2); border-radius: 16px; background: rgba(94,104,218,.08); }
.web-ask p { margin: 0 0 6px; color: var(--pearl); font-size: .875rem; line-height: 1.45; }
.web-ask .web-q { display: inline-block; margin: 2px 0 8px; padding: 6px 10px; border-radius: 8px; background: rgba(0,0,0,.3); color: var(--accent-2); font-size: .8125rem; word-break: break-word; }
.web-ask small { display: block; margin-bottom: 12px; color: var(--dim); font-size: .75rem; }
.web-ask .web-btns { display: flex; flex-wrap: wrap; gap: 8px; }
.web-ask .web-yes { border-color: rgba(165,255,196,.35); color: var(--ok); }
.web-note { margin-top: 6px; color: var(--warn); font-size: .75rem; letter-spacing: .06em; }
@media (max-width: 860px) { .web-ask { margin-left: 0; } }`;
  document.head.appendChild(css);

  window.IconicWeb = {
    // Show the exact search and wait for yes / no. Nothing has left the computer at this point.
    offer(turn, query, yes, no) {
      const box = document.createElement('div'); box.className = 'web-ask';
      box.innerHTML = `<p>The files can’t answer this one. It needs the open web. I’d search for:</p>
        <span class="web-q">${esc(query)}</span>
        <small>Nothing has left this computer. If you say yes, only those words go out, to public search engines. No AI company sees them.</small>
        <div class="web-btns"><button type="button" class="next web-yes">Yes, search the web →</button><button type="button" class="next web-no">No, stay in the files</button></div>`;
      const a = turn.querySelector('.a > div:last-child') || turn; a.appendChild(box);
      const done = (fn) => () => { box.querySelectorAll('button').forEach((b) => { b.disabled = true; }); fn(); };
      box.querySelector('.web-yes').addEventListener('click', done(yes));
      box.querySelector('.web-no').addEventListener('click', done(no));
    },
    // Under the answer: say exactly what went out.
    label(metaEl, web) {
      const n = document.createElement('div'); n.className = 'web-note';
      n.textContent = web.error ? `TRIED THE WEB FOR “${web.query}”: ${web.error}` : `SENT TO SEARCH ENGINES: “${web.query}” · ${web.results} RESULT${web.results === 1 ? '' : 'S'}`;
      metaEl.after(n);
    },
  };
})();
