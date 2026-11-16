# ICONIC Outreach Intelligence — isolated prototype (2026-11-16)

**Status:** working proof of concept. **Not deployed to iconic.onl.** The production site, payment systems, Reserve, and production models were not changed.

## Try it

Open `index.html` directly in a modern browser, or serve this directory statically. Click **Load fictional example**, select a prospect, inspect the evidence/score, edit its message, approve for export, and export the CSV or audit JSON.

The entire UI, styling and evaluation engine are self-contained in `index.html`. No server, API key, database, cloud model, or external service is required.

## What works

- Import CSV of authorized contacts (up to 5,000 rows, 5 MB) with quoting and header aliases.
- Suppression gates: explicit DNC, previously contacted, duplicate email, invalid syntax, missing identity, custom excluded terms.
- Transparent role + vertical + source URL + timestamp scoring. This is **not a purchase probability**.
- Conservative, editable draft generation based on source supplied by the user and simple greeting/sign-off writing preferences.
- Human review states, invalidate approval on editing, export only approved **UNSENT** drafts; also export a JSON audit.
- Source URLs are displayed as provided. They are not independently verified or fetched.
- CSV formula injection escaped on export.

## Schema

```csv
company,contact_name,title,email,industry,event_name,evidence_url,evidence_date,do_not_contact,prior_contact,context
```

Alternative field names for some columns are supported in code. Dates should be ISO dates.

## Not implemented

Actual lead discovery, web research, verified mailbox deliverability, third-party enrichment, intent prediction, LLM personalization, email/CRM sending, outcome tracking, tenant separation, or paid fulfillment. Do not market it as a production Signalyze competitor.

## Tests / next build

Run `node --test tests/engine.test.mjs` from this directory. The exact self-contained published HTML passed **9/9 Node regression tests on November 16, 2026** covering CSV parsing, suppression, duplicate blocking, honest syntax-only status, source-backed draft gating, URL safety, CSV formula escaping, and style rules. A headless Chrome smoke test on the authorized Mac also passed: five fictional records evaluated, three eligible/two blocked, selection and approval worked, editing after approval revoked approval, and no JS exceptions were observed. This does not prove full production readiness.

Next step: add authorized lead-data connectors, verified-source retrieval, independent email verification, opt-out synchronization, strict tenant isolation, real model-assisted drafts, permissioned send workflow, and outcome measurement. Keep private customer data out of the public website.

## Release boundary

This repository publishes iconic.onl from `main`. The feature branch containing this prototype is non-production. Do **not** merge to `main` without separate approval and functional browser checks.
