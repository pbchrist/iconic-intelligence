# ICONIC website: working plan

The single place where decisions, status and next steps for iconic.onl live.
Start every session on this site by reading this file and `CHANGELOG.md`.
Last updated: 2026-11-01.

## Where things stand

| What | Where |
|---|---|
| Live site | https://iconic.onl, published from **repo `pbchrist/iconic-intelligence`**, branch `main`, by `.github/workflows/pages.yml` |
| Old copy | repo `pbchrist/iconic-preview` is NOT what iconic.onl serves. Don't deploy from it. |
| Revised version, not live | branch `staging` |
| Clickable preview of the Nov 1 revision | https://claude.ai/artifact/7VxfexkHbT9vVVrZTQ2mbD (private to Patrick) |
| Rollback point | branch `rollback-live-2026-11-01`, exactly what iconic.onl served on Nov 1 |

- On Nov 1, iconic.onl had the Calendly booking buttons, but they had never been saved to GitHub. They are saved now (commit `0e38f45`). Never deploy from an old copy without checking the live site first.
- Going live = Patrick says "go live", then the change goes onto `main` of `iconic-intelligence`.
- Nov 1 revision went live from `iconic-intelligence` main. Rollback = previous commit `0c7c524` (the Calendly version).

## How Patrick wants this work done

- Revise inside the current structure. No re-architecture. On Oct 31 a layout change broke heading sizing and text wrapping.
- Every preview is a link he can click and use. No screenshots.
- Test interactive things by using them, not by taking pictures.
- Agents do every GitHub step: merges, pushes, branches.
- He records video on his phone and uses Loom.

## The pitch (decided)

- **Bedrock:** own your intelligence, don't rent it. The print ad says "Private by design."
- **What he sells:** your own AI stack, not a filing cabinet. Private models, a memory of the business, and agents that do real work. A knowledge store on its own is too narrow.
- **Two ways in:** learn it (he teaches, from whatever rung you're on: run a model locally → connect your files → build agents → know where to draw the line between local and frontier models), or have it done.
- **Training is ongoing.** He trains the system continuously, so monthly care is the main product, not maintenance.
- **Why local:**
  - No meter: billions of tokens for the cost of the computer and the power.
  - No rate limits.
  - Vendors change, restrict, reprice and withdraw models.
  - Hybrid is the smart setup: private work stays local, public work can use frontier models.
- **The Fable facts, as verified:**
  - Anthropic pulled Fable 5 and Mythos 5 from June 12 to July 1, 2026 to comply with U.S. export controls.
  - Afterwards, Fable moved off the $20 plans to pay-per-use credits. It is still on the API and the top-tier plans.
  - It was never API-only.
- **Agents are central.** Patrick runs 23 agents across his business and clients', with gateways to phone and chat.
- **The audience is multi-vertical:** law, wealth, real estate, owner-run, accounting. It is not just lawyers.
- **No model fine-tuning.** Keep tuning out of the pitch.

## Done on `staging` (Nov 1)

- **Hero:** private AI and agents, no meter. Proof chips: files stay / no meter / agents do the work.
- **Free check:** adds "where to draw the line."
- **Why own it:**
  - Sam Altman named, with date and podcast (Cheeky Pint, Oct 29, 2026). No link to the episode was found.
  - Cards: KEPT / STEADY / NO METER.
  - Fable story behind a "More →" expander, with sources.
- **Who it's for:**
  - New "ITS AGENTS RUN" row for each vertical.
  - A plain-English rule with "More →" for each vertical: ABA Formal Opinion 512 for law, SEC Reg S-P for wealth, IRC §7216 for accounting. Real estate and owner-run say there is no rule; it's about leverage.
- **What it does:** KNOWS / WORKS / STAYS.
- **New Proof section:**
  - GMC dealership case study: 20 reports, 20 of 22 trucks cheaper by an average of $4,472, the pricing error caught, the check down from 30 minutes to 3, "Exceptional."
  - 23 agents; one desktop with 40 GB of graphics memory running Qwen 27B (~71 tokens a second, 131k context); $0 per token.
  - Patrick confirmed the case study figures and the quote are fine to publish.
- **Two ways in:** the Learn-it ladder, plus a note on private vs cloud.
- **Remote access wording is fixed:** care runs over an encrypted connection the client can switch off; Patrick maintains the software, not the files. **Patrick should confirm this matches how he'll set it up.**
- **Nav:** "How it compounds" became "Proof."
- **Founder line:** now mentions 23 agents and the dealership.
- Tested at widths from 320 to 1920 px and at 150% text size. No overflow.

## Still open: the offer (needs Patrick's numbers)

From the first best-in-class review. None of these can be written without his answers.

1. **Price anchor:** "Setup from $X · care from $Y/mo."
2. **Hardware answer:** what computer the client buys and roughly what it costs.
3. **Guarantee,** or decide to have none.
4. **Timeline,** framed as "first agent doing real work within X of the hardware arriving." The earlier "two weeks" was a made-up example, not a real number.
5. **Founder section higher on the page.** Can be done without input.
6. **Named deliverable for the free check,** for example a one-page AI exposure report. Only if he'll actually produce it.
7. **Something for visitors not ready to book,** for example a one-page PDF in exchange for an email.

## Demo: the live dashboard

**Built Nov 1: ICONIC Command** (branch `dashboard` of this repo). Real, not a mockup. Answers from the local model with sources, a briefing the model writes, a live job log, knowledge stats and a control panel, plus two fictional sample workspaces (Hollis & Reyes LLP, Northline Supply Co.). Install or update on Beastmaster with:
`curl -fsSL https://raw.githubusercontent.com/pbchrist/iconic-intelligence/dashboard/install.sh | bash`
It runs on port 8770, and files go in `~/iconic-command-data/<workspace>/`. Patrick decided: no video, people use the real thing, and nobody uploads their own files. Still open: whether to put it on the public internet, for example with Tailscale Funnel.

**Nov 1, later:** the demo is live on iconic.onl under the hero ("Try it live"), at the public address https://patrick-beastmaster.tailf32530.ts.net.
- **Intelligence Graph:** the model maps each business MemPalace-style: wings, entities, facts with dates and states, and glowing "hidden connections" (tunnels) with a one-line insight.
- **Shared learning:** every answer that cites two or more files adds permanent connections, shared by all visitors. The counters show connections and conversations.
- **Answers:** the first two show sources and suggestions, then it stays clean. "show sources" brings them back. No "I can't" and no disclaimers.
- **Phones first:** the embed is built for the QR code traffic.
- **Self-updating:** Beastmaster checks the `dashboard` branch every 10 minutes.
- **The 3D compounding animation** uses Northline's real numbers. "Watch the live AI do this ↑" asks the demo, and a live connection counter adds rings.
- On Patrick's own devices (on Tailscale), Chrome blocks the embed, so he sees an "Open the demo" button. Public visitors are unaffected.

### Earlier notes

- **What exists:** `http://100.73.250.50:8769/#dashboard`, on beastmaster, reachable over Tailscale only.
  - "Live concept // Executive control surface" with tabs: Ask / Intelligence / Work / Knowledge / Control.
  - **It is a mockup.** The answers are canned, there is no model behind it, and the feed data is invented. Typed questions get a generic non-answer, or nothing.
  - Strong copy worth reusing: "The model is a component. The system is the product." The Control tab shows "2 decisions need a human" and routing work by need between local and frontier models.
- **Patrick's direction:** make it real, and then a separate demo isn't needed.
- **Plan:**
  1. Put the dashboard code in a GitHub repo (it currently lives only on beastmaster).
  2. Connect Ask to local Qwen through llama.cpp's OpenAI-compatible server.
  3. Fill the Intelligence feed from real EGBGMC report output.
  4. Load Knowledge with a synthetic law-firm folder of about 20 documents. Never real client files.
  5. Use it live on free-check calls.
  6. Decide whether to make it public, for example behind a Cloudflare tunnel with per-visitor limits and nothing private reachable.
  7. Record a 60–90 second Loom of the real thing for visitors who won't click.
- **Loom script:**
  - 0:00 pull the network cable (it's private)
  - 0:15 ask an unrehearsed question and show the cited files (it knows your business)
  - 0:50 the brief arriving by phone (it works while you sleep)
  - 1:20 "no meter; the check is free"
