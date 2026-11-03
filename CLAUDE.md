# ICONIC — handoff for Claude Code on beastmaster

You are picking up work from a long cloud session with Patrick Christell (ICONIC, iconic.onl).
This file is the brain transfer. Read it fully before doing anything.

## How Patrick wants to work (important)

- Plain language. Short answers. No jargon, no long explanations unless asked.
- Fast and token-aware. He is often tired and frustrated; don't over-explain or loop.
- Don't change anything when he says "don't do anything" / "just tell me". Answer only.
- Never touch the live site without him saying "go live" / "push to main".
- Previews = a clickable link he can use, never screenshots. Test web apps by using them.
- He never does GitHub UI steps himself; you do merges/pushes.
- Mobile first (QR code from a WAC Magazine print ad), but never nerf desktop.
- One thing at a time is how cruft built up last time: before editing the site, read the whole page top to bottom as a visitor and keep one consistent set of styles.

## What lives where

| Thing | Where |
|---|---|
| Live site iconic.onl | repo `pbchrist/iconic-intelligence`, branch `main`, GitHub Pages via `.github/workflows/pages.yml` |
| Site preview | repo `pbchrist/iconic-preview`, branch `main` → https://pbchrist.github.io/iconic-preview/ (copy the iconic-intelligence tree into it to preview) |
| Site plan / decisions | `PLAN.md` in iconic-intelligence (not deployed) |
| The live demo app ("ICONIC Command") | this folder, `~/iconic-command`, branch `dashboard` of iconic-intelligence |
| Demo sample data | `~/iconic-command-data/` (Hollis & Reyes LLP law firm, Northline Supply Co.) — fictional |
| Demo state (graph, feed, learned links) | `~/iconic-command/state/` or `$ICONIC_STATE` |
| Demo config | `~/.config/iconic-command.env` |
| Demo service | `systemctl --user status iconic-command` ; logs: `journalctl --user -u iconic-command -f` |
| Auto-update | `iconic-command-update.timer` runs `update.sh` every 10 min: hard-resets this folder to `origin/dashboard` and restarts if changed. **Commit and push local edits to `dashboard` or they get wiped.** |
| Public address | https://patrick-beastmaster.tailf32530.ts.net (Tailscale Funnel) → this app |

## The demo (server.py, static/)

- Python stdlib server. BM25 search over the sample files, streams answers (SSE) from a local OpenAI-compatible model (llama.cpp). Strips `<think>`, sends `chat_template_kwargs.enable_thinking:false`.
- The model writes the morning briefing and the Intelligence Graph (wings, entities, facts, hidden-connection "tunnels"), cached in state.
- Learned links: answers citing 2+ files add permanent connections shared by all visitors (`learned.json`). Site shows "N connections from M conversations" live.
- Public mode: rate limits per IP + overall; only sample workspaces.
- Embedded in iconic.onl as an iframe (`?embed=1`); phones open full screen (`?back=1`); `?ws=&q=` auto-asks.
- No web access. Nothing goes to any AI company ("0 bytes sent to AI companies" is true by design).

### Model selection — this broke on Nov 2

`Model.detect()` scans ports 8000–8100 (+5000, 1234, 11434, 30000, 9000) and grabs the first chat model, skipping embedding servers. When Patrick experimented with quantization on the 4060 Ti, the demo latched onto a new non-streaming server ("qwen38-smart", port 8092): replies arrived in one lump after 13–40+ s. Patrick pointed it back to the right model.
**Pin it** so it can't wander: put `ICONIC_LLM_URL=http://127.0.0.1:<port>/v1` (the Qwen 27B on the 3090) in `~/.config/iconic-command.env`, then `systemctl --user restart iconic-command`. `install.sh` now preserves that line on reinstall.
Check: `curl -s localhost:<demo port>/api/status` → `model.endpoint`.

## Site state (live as of Nov 2)

Order: hero ("Own your intelligence. Don't rent it.") → live demo ("Try it on a sample business") → proof (GMC dealership: "He thought his competitor was $800 cheaper. His AI found a $4,472 gap.") → what it does → who it's for (rotating use cases, pause on hover) → how to start ("Your first working agent", taught or built) → free 30-min check → why own it ("The new moat") → compounding 3D animation + live counter → pricing (no numbers, by Patrick's choice; hourly / project / retainer) → bio, tagline "Know more. Move first." → Privacy / Terms pages.
Free one-page guide PDF: `iconic-own-your-ai-guide.pdf`.
Chrome on Tailscale devices: the iframe has `allow="local-network; local-network-access"`; the user must allow "Local network" for the site once.

## Open items

1. **Compounding animation**: Patrick said "something's wrong with it" after the section reorder; not diagnosed (he didn't say what). Ask him what he sees, then fix that one thing.
2. **Demo jump fix** (pushed Nov 2): embedded demo must not scroll the host page after an answer. Verify by asking a question on iconic.onl on desktop.
3. **Optional, not requested**: ask-before-web-search in the demo. If ever built, use self-hosted SearXNG or DuckDuckGo (not Exa/Parallel/Firecrawl, which are AI companies and would make the "0 bytes" label false), show the exact query, ask yes/no, label what left.
4. Offer gaps Patrick has decided on: no prices on the site, no timeline, no guarantee. $150/hr is discussed on calls only.

## Patrick's setup

- beastmaster: RTX 3090 (demo model, Qwen 27B, ~60 tok/s) + RTX 4060 Ti (his quantization experiments; he wants gaming + agents to coexist).
- Hermes agents: `~/.hermes` (Hermbeast) and `~/hermes-instance2` (Hermione); 23 agents total. Hermes web search supports keyless DuckDuckGo and self-hosted SearXNG.
- EGBGMC dealership intel agent (Tony and Kimberly) runs as Hermes jobs here.
