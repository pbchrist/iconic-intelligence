# AGENTS.md — iconic.onl (ICONIC. Managed Intelligence)

Rules for any AI working here (Claude, Hermes, Grok Bot, ChatGPT). Short on purpose.

## What this is

The production website for ICONIC at https://iconic.onl. Static HTML/CSS/JS with a self-hosted Three.js scene and GSAP. No build step.

## Run and check

- Local: `npm start` (serves on `PORT` or 3000), or any static server from the repo root.
- No automated tests. Check by opening the page at desktop and phone widths.
- Publishing: every push to `main` deploys to iconic.onl through `.github/workflows/pages.yml` (GitHub Pages since 2026-10-11). The README's Railway steps are out of date; Railway is gone.

## Where things live

`index.html`, `styles.css`, `mobile-first.css`, `app.js`, `three-scene.js` (the site) · `CHANGELOG.md` (one line per change) · git tags `v1.x-YYYY-MM-DD` / `live-YYYY-MM-DD` (bookmarks) · `docs/DECISIONS.md` · `docs/DONE.md`.

## Hard rules (from README and CHANGELOG)

- Pushing to `main` puts it live. Only when Patrick says it goes live.
- Work on a branch (`staging` or a feature branch). No copy files like `index-v2.html`; git history keeps every version.
- Every change gets a one-line note in `CHANGELOG.md`.
- Keep libraries self-hosted (Three.js, GSAP); the site must not depend on another site.

## Workflow (every task)

1. **Ticket first.** 3–4 lines: what changes, and how we'll know it worked.
2. **Preflight.** Right branch, `git status` clean, no stray local server on the port.
3. **One change = one branch = one PR.** Never push or merge to `main` without Patrick's yes.
4. **Builder doesn't grade its own work.** Proof = the checks in `docs/DONE.md`, confirmed by someone else (QA bot or Patrick).
5. **Lasting decisions** go in `docs/DECISIONS.md`, dated and sourced. A new rule replaces the old one; never stack.
6. **Stop when done.** No bonus refactors, no follow-on audits.
