# ICONIC. Managed Intelligence

Production website for ICONIC.

## Deployment model

- `main` = production candidate / production
- `staging` = live staging branch
- Railway serves the site with `npm start`
- `iconic.onl` is the production custom domain

## Local run

```bash
npm start
```

The server uses `PORT` when provided and otherwise listens on 3000.

## Making a change

Same habits as every Patrick site (ICONIC OS skill `web-build-release`):

1. Work on `staging`. Don't make copies like `index-v2.html`; every saved change is kept in GitHub history.
2. Save with a one-line note and add the same line to `CHANGELOG.md`.
3. Check the Railway staging link (the practice run for this site).
4. Only when Patrick says it goes live: promote the tested `staging` to `main`; Railway puts `main` on iconic.onl. Then check iconic.onl.

## Bookmarks

Versions that matter get a bookmark (a git tag): `v1.1`, `v1.2-2026-09-24`, `v1.3-2026-09-25`, `live-2026-10-08`.
Name new ones `v1.4-YYYY-MM-DD` or `live-YYYY-MM-DD`. To see one: `git checkout <bookmark>` or browse it on GitHub.
