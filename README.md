# ICONIC. Managed Intelligence

Production website for ICONIC.

## Deployment model

- `main` = production. Every push to `main` publishes to iconic.onl through GitHub Pages (`.github/workflows/pages.yml`), since 2026-10-11. Railway is no longer used.
- `staging` = working branch (there is no hosted staging preview)
- `iconic.onl` is the production custom domain

## Local run

```bash
npm start
```

The local server (`server.js`) uses `PORT` when provided and otherwise listens on 3000. It is only for local checks; production is static on GitHub Pages.

## Making a change

Same habits as every Patrick site (ICONIC OS skill `web-build-release`):

1. Work on `staging`. Don't make copies like `index-v2.html`; every saved change is kept in GitHub history.
2. Save with a one-line note and add the same line to `CHANGELOG.md`.
3. Check it locally with `npm start` (there is no hosted staging preview).
4. Only when Patrick says it goes live: promote the tested `staging` to `main`; GitHub Pages puts `main` on iconic.onl within a few minutes. Then check iconic.onl.

## Agent-ready files

These sit in the site root and go out with the GitHub Pages publish. They describe the public site only. They do not include a price. The price on the page is still Patrick's placeholder.

- `llms.txt` is a plain-text brief for agents. Linked from the home page with `<link rel="alternate" type="text/plain" href="/llms.txt">`.
- `webmcp.js` registers three WebMCP tools when the browser has `document.modelContext` or `navigator.modelContext`: `describe_service`, `get_contact`, and `request_a_report`. No polyfill is loaded. The script makes no network calls. `request_a_report` only opens a pre-filled `mailto:` for the visitor to send. Nothing is sent by the page.
- The JSON-LD in `index.html` is the same public facts: organization, Patrick, the report, and the site.
- `robots.txt` allows the public site and points at the sitemap.
- `sitemap.xml` lists the home page, with `lastmod` set to the day this copy was updated (2026-10-28), not a guessed merge date.

What is true, and what these files are allowed to say: the market history and the tools stay on hardware Patrick runs. Reports are written with Claude, from public listing data. Nothing goes out until he approves it. Do not write that the whole product runs on a local stack, or that nothing touches a cloud.

An origin-trial token for WebMCP is not in the page. Until Patrick registers iconic.onl, the tools show up only in browsers with the WebMCP testing flag on.

## Bookmarks

Versions that matter get a bookmark (a git tag): `v1.1`, `v1.2-2026-09-24`, `v1.3-2026-09-25`, `live-2026-10-08`.
Name new ones `v1.4-YYYY-MM-DD` or `live-YYYY-MM-DD`. To see one: `git checkout <bookmark>` or browse it on GitHub.
