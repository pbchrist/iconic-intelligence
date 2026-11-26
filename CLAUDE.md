# iconic.onl — standing rules (read before any change)

@AGENTS.md

These are Patrick's standing instructions. **His newest instruction wins.** When he changes his mind, edit this file in the same commit as the change, replacing the old rule rather than adding a conflicting one.

## Styling
- **Read [style-guide.yaml](style-guide.yaml) before any copy or design change.** It is the machine-readable style guide (logo, color, type, components, spacing, imagery, voice) and the single source: the visual guide at /preview/style-guide/ is rendered from it, and [STYLE_GUIDE.md](STYLE_GUIDE.md) is the same rules as text. If they disagree, the YAML wins. After changing color tokens, run `python3 scripts/check-style-guide.py`.
- One design system. All font sizes, colors and spacing come from shared CSS custom properties (tokens) in the shared stylesheet. Do not introduce new font-size, color or spacing values.
- No per-page `<style>` blocks and no inline `style=""` for anything visual. Fix the shared stylesheet instead of patching a page.
- Change the system, not the instance: a sitewide look change is made once, in the stylesheet.
- Known debt (2026-11-17): 4 stylesheets (styles.css, mobile-first.css overriding it, offers.css, learning-paths.css), ~121 distinct font-size declarations, 14 of 33 pages with their own `<style>`. Consolidation is NOT yet approved; do not start it unasked. Don't make it worse.

## Process
- Do only what Patrick asked. A question or complaint is not a request for work.
- The site is live: pushing to `main` publishes iconic.onl. Design or layout changes go to a preview first (e.g. /preview/) and reach the root only after Patrick approves. Factual fixes he asked for (prices, copy) may go straight to main.
- Pushing to main rebuilds gh-pages with rsync --delete: port any gh-pages-only commits first.
- Rollback: branch `rollback/pre-first-fix-2026-11-24` / tag `live-2026-11-24-before-first-fix` (homepage before the First Fix went live); `rollback/pre-golive-2026-11-18` (site before the 2026-11-18 preview went live); older: `rollback/pre-launch-2026-11-17`; old homepage at /classic/.

## Copy and offers (as of 2026-11-17)
- Homepage (live 2026-11-24, from the approved /preview/): hero "Move first." with the WAC-ad knight, then The First Fix ($1,000, one problem, one agreed result), dealership proof, training/build/ongoing, "Who holds the keys?", demo. Workshops line under the hero buttons. The AIpocalypse lives on /aipocalypse/ and the homepage links to it.
- The full AIpocalypse + "AI you own" argument also lives at /aipocalypse/ (2026-11-24, copied word for word from the homepage). The /preview/ homepage links to it instead of carrying it. When the preview goes live, the homepage keeps a link to /aipocalypse/; never drop that content.
- Prices: The First Fix $1,000 (homepage lead offer); Evaluation $1,000 (whole-business review, /services/evaluation/); Training $249 workshop / $1,000 private / $3,000 team (flat, no tax added); Builds from $10,000, by invitation. No small single-agent offer.
- Plain words. No "magic" or "genius". The $4,472 figure is a measured price gap, not revenue recovered.
- The homepage and preview do not link to the agent pages (/agents/…) — no menu item, section or footer link (Patrick, 2026-11-24: they confused business visitors). The agent pages stay up for AI tools via sitemap, llms.txt and manifests.
- Agent pages state only what the live catalog says is for sale (check `/mpp-catalog/offers`); no internal status notes ("checkout unavailable", "not yet verified") on public pages.
