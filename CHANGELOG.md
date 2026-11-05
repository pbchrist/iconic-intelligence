# ICONIC website (iconic.onl) — change log

Newest first. One line per change: what changed and why.
Live: https://iconic.onl/ · Test version: Railway staging (branch `staging`).


## 2026-11-04
- Reserve becomes machine-first: the default agent URL now returns a structured service contract; seven public MCP tools support catalog → $0 quote → free assessment → direct deliverable. The human UI moved to /reserve/agents/ui. Updated the static product page and AI reference manifest.
- Added ICONIC Intelligence Reserve as a canonical agent-discoverable product under /agents/reserve/, with machine-readable manifest, free public MCP assessment and synthetic demo, tracked in sitemap/llms/AI evaluation and linked from the homepage. The private customer Reserve remains authenticated and isolated; paid tiers are not live.
- New top of the page: "Own your intelligence. Compound your advantage." Says plainly that everyone rents the same AI and the edge is what your business knows, then "Build your own private intelligence moat" (styled like the demo's "Pick a business. Watch it think.") right above the buttons. Patrick's wording.
- Made the AI files easy to find: sitemap now lists llms.txt, llms-full.txt and the /ai pages; robots.txt points AI assistants to them; added the Bing IndexNow key file so new pages can be announced right away. No visible change.
- Rewrote the AI discovery files to lead with proof (the $4,472 dealership gap, 23 agents, the live demo) in the site's own words; cut the disclaimers to a short accuracy list; put back the 23-agents line and the 'static site, no login, don't act on someone's behalf' notes. Still no visible page changed.
- Added the AI discovery files for AI assistants: a new llms.txt, llms-full.txt and six reference pages under /ai/. Plain text files only; no visible page changed. Fixed the package's section links (#who, #demo, #why didn't exist) and pointed booking at the Calendly link.
- New bio photo (white jacket, checked shirt) replaces the tuxedo photo.
- Bio replaced with Patrick's own words (film → technical recruiting → private AI → ICONIC); no dealership, no name-dropping.
- Removed: "trained on the dealership's own data" (now "built on"), the "Who checks it" line on every business type, and the "Private doesn't mean cut off" note (not every setup needs cloud AI).
- Free check list: merged "where data goes" and "what is exposed" into one item; new item "Whether a self-hosted AI is right for you"; same added to the check description lower on the page and in llms.txt.
- Free check list: "where to draw the line" is now optional ("If you also want to use cloud AI"); last item now "What bespoke agents built on your own data could do" (built on, not trained on: no fine-tuning claims).
- Removed the "Worth knowing first / The plain answers, before you book" box: it talked people out of booking and promised a remote-support setup Patrick never confirmed. Same two claims removed from llms.txt.

## 2026-11-03
- Link previews (texts, LinkedIn, etc.) now show the ICONIC star icon (the square logo from the browser tab) instead of Patrick's photo: added a share image and told previews to use it.

## 2026-11-01
- (branch compound-tie) Animation follows the business picked in the demo (law firm or supply company), works even without 3D; live counter moved below the picture on phones; demo section headline smaller on phones (rem, capped to the screen).

- (branch compound-tie) Compounding animation now tells Northline Supply's real stories, ends with "Watch the live AI do this" which asks the live demo, and shows the live demo's connection count, adding rings as it grows. The compounding section links back with the live count.

- Live demo now loads directly and reveals when the demo says it is ready; if it never does, a direct link and the booking button show instead.

- Added "Try it live" section after the hero: embeds ICONIC Command from the demo machine, with an honest offline fallback and booking link. Hero link now "TRY IT LIVE".

- Added version tags to the stylesheet and script links so returning visitors get the new files, not stale cached ones.
- Revised the pitch around private AI and agents: no meter, no rate limits, models no one can change on you. Named Sam Altman in the quote. Added the Fable shutdown as a "More →" detail, an agent row and a plain-English rule for each use case, a Proof section (dealer case study, 23 agents, the rig), the Learn-it ladder, where to draw the line between private and cloud, and fixed the remote-access wording. Nav: "How it compounds" became "Proof". Plan and open items: PLAN.md.
## 2026-10-31 (draft, not live)
- Rebuilt the page around the private AI offer: a private AI on the client's own computer, learn it or have it done, free 30-minute check. Kept the compounding story. Removed the dealer-first use cases, the demo dashboard and the experiment demo. Added llms.txt and structured data.
- Added the "own your intelligence" pitch, a "why own it" section quoting Sam Altman (Cheeky Pint, Oct 29, 2026), and five toggleable use cases: law, wealth, real estate, owner-run, accounting.
- Added the free 30-minute check offer right after the hero, a booking button after the proof and at the end, a reassurance line under each, and a pinned booking button on phones. Rewrote the proof in plain English, including why it is not 100 out of 100.
- Reordered: free check, then why own it, who it is for, what memory gets you, then the compounding story.
- Phones with larger text settings: big headings now shrink to fit the screen, and in the compounding story the words sit below the animation instead of on top of it. Tested at 100% to 175% text size.

## 2026-10-11
- Moved hosting from Railway (free trial ending) to GitHub Pages, free, like the other sites. Also makes www.iconic.onl work. Site content unchanged.

## 2026-10-08
- Added this change log and the bookmark `live-2026-10-08` for what iconic.onl serves today. Nothing on the site changed.

## 2026-09-25 (`v1.3-2026-09-25`)
- Repaired the desktop hero and the compounding section layout.
- Finished the WAC use cases, the private-hosting message and a QA pass.
- Applied the Sep 24 handoff: the compounding story runs through the page.
- Self-hosted the 3D library so the visuals don't depend on another site.
- Reframed the sales story around proof that compounds, with one-problem call to action.

## 2026-09-24 (`v1.2-2026-09-24`)
- Fixed in-page navigation and where links land.
- Tightened positioning, proof, type and engagement speed; restored SEES KNOWS MOVES type.
- Revised the deployment-model message and phone navigation.

## Earlier
- `v1.1`: the live ICONIC 1.1 frozen as the starting point.
