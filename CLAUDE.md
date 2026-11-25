# iconic.onl — standing rules (read before any change)

@AGENTS.md

These are Patrick's standing instructions. **His newest instruction wins.** When he changes his mind, edit this file in the same commit as the change, replacing the old rule rather than adding a conflicting one.

## Styling
- One design system. All font sizes, colors and spacing come from shared CSS custom properties (tokens) in the shared stylesheet. Do not introduce new font-size, color or spacing values.
- No per-page `<style>` blocks and no inline `style=""` for anything visual. Fix the shared stylesheet instead of patching a page.
- Change the system, not the instance: a sitewide look change is made once, in the stylesheet.
- Known debt (2026-11-17): 4 stylesheets (styles.css, mobile-first.css overriding it, offers.css, learning-paths.css), ~121 distinct font-size declarations, 14 of 33 pages with their own `<style>`. Consolidation is NOT yet approved; do not start it unasked. Don't make it worse.

## Process
- Do only what Patrick asked. A question or complaint is not a request for work.
- The site is live: pushing to `main` publishes iconic.onl. Design or layout changes go to a preview first (e.g. /preview/) and reach the root only after Patrick approves. Factual fixes he asked for (prices, copy) may go straight to main.
- Pushing to main rebuilds gh-pages with rsync --delete: port any gh-pages-only commits first.
- Rollback: branch `rollback/pre-golive-2026-11-18` (site before the 2026-11-18 preview went live); older: `rollback/pre-launch-2026-11-17`; old homepage at /classic/.

## Copy and offers (as of 2026-11-17)
- Hero: "Own your intelligence. Compound your advantage." Keep the "AIpocalypse is coming" section.
- Prices: Evaluation $1,000; Training $249 workshop / $1,000 private / $3,000 team (flat, no tax added); Builds from $10,000, by invitation. No small single-agent offer.
- Plain words. No "magic" or "genius". The $4,472 figure is a measured price gap, not revenue recovered.
- The homepage and preview do not link to the agent pages (/agents/…) — no menu item, section or footer link (Patrick, 2026-11-24: they confused business visitors). The agent pages stay up for AI tools via sitemap, llms.txt and manifests.
- Agent pages state only what the live catalog says is for sale (check `/mpp-catalog/offers`); no internal status notes ("checkout unavailable", "not yet verified") on public pages.
