## 2026-11-24 — Selection Test page: clearer for directory partners
- Columns and claims now name the exact models (OpenAI GPT-4.1 mini, Anthropic Claude Haiku 4.5, Google Gemini 2.5 Flash) instead of "ChatGPT/Claude/Gemini". Other rivals are grey and "no tool" squares are hollow so they can't be mixed up. New section near the top for directories: "Your listings get skipped. Now you can show them why."

## 2026-11-24 — Selection Test page: real ChatGPT, Claude and Gemini results
- Ran the full test on GPT-4.1 mini, Claude Haiku 4.5 and Gemini 2.5 Flash (750 requests, $3.59, no errors, 4 rivals agreed by all three AIs). Replaced the local-model grid with the 300-request grid: the tool got 10, one rival 169 (ChatGPT 0 of 100). Repeat run: 13. After rewriting its two descriptions: 7 became 18 on 10 unseen requests, 11 gained, none lost.

## 2026-11-24 — Selection Test page: the real test grid, plainer words
- Added the grid: all 48 real requests from the November 23 test, one square each, colored by which tool the AI used (green = the tool tested: 3; top rival: 31). Plus the before-and-after grid for the rewrite (2 became 6).
- Headline now "Does the AI pick your tool?" Rewrote the rest in plain words. Added the test that was stopped because only two fair rivals existed.

## 2026-11-24 — Selection Test page rewritten in plain words, with real results
- New headline "Listed isn't picked." Says plainly what the test does: count how often an AI picks your tool against real rivals, show who wins and why, rewrite the descriptions, test again.
- Real numbers from November testing: a web-search tool picked 3 times out of 48 (top rival 31); after rewriting its descriptions, 2 picks became 6 on new requests; only 6 of 10 tools that claim to read web pages can do it directly; six real tool calls to Microsoft, Twilio, AWS and Context7 all answered on topic.
- Cut the stack of warnings to one honest line. Old slogan "Own your intelligence" replaced in the footer.

## 2026-11-24 — Homepage no longer sends people to the agent pages
- Took "For agents" and "MCP" out of the menus, removed the "Already running an agent swarm?" section, and removed the four agent links from the footer (homepage and preview). Patrick: business visitors were landing on pages that looked like a different company.
- Agent pages now say only what is really for sale today ($29 Data Discrepancy Report, $19 Reserve Pass). Removed the false "seven offers support checkout" lines and the internal notes ("checkout unavailable", "payment processor remains off", "not yet verified"). Other offers now read "coming soon".
- Same correction in llms.txt, llms-full.txt and the Selection Test entry in offers.json, so AI tools are told the truth too.

## 2026-11-24 — Preview: homepage that matches the WAC magazine ad

- New preview at /preview/ (not the homepage). Opens with the ad's words: "Move first. Put AI to work inside your business without handing over the keys." Then "I'll teach you AI" in three steps (training from $249, $1,000 evaluation, build by invitation), the dealership proof, "Who holds the keys?" and the demo.
- Cut from the preview to reduce clutter: the compounding animation, the "their servers, their rules" news strip, the research list and the agents box. The AIpocalypse section moved lower. All of these stay on the live homepage until Patrick approves.
- Added the knight from the WAC ad (the original art from Patrick's ad folder, no words on it) beside "Move first." on wide screens and under the buttons on phones. Its edges fade into the page.
- Same space above and below the knight on phones, tablets and computers (it had much more space below).
- Why: the ad's QR code lands on the homepage, which didn't say what the ad says. Preview has no visitor counter and is hidden from search engines.

## 2026-11-16 — Branching AI training navigator and complete skill browser

- Replaced homepage training ladder with outcome-led choices that open a branching, keyboard-operable navigator on the AI training page.
- The navigator asks what the visitor needs, then a second question, then offers an actionable route, lab, and links to relevant skills. Back and Start Over work without collecting user data.
- Added the complete 439-competency, 29-module inventory, with keyword search, module and difficulty filters, expand/collapse and downloadable public CSV (skill names only, no private client proof notes).
- Changed the hero demo button from "WATCH ONE THINK" to "TRY MINE", and its small demo label from "RUNNING ON ONE BOX" to "RUNNING ON MY LOCAL AI".
- Training, evaluation, build pricing, existing booking links and live inference endpoints unchanged.

## 2026-11-16 — Reframe preview training around clarity and model fit

- Homepage heading now asks what the customer's AI should actually do, replacing the intimidating "how deep" framing.
- Five outcome-led learning paths replace six ascending technical levels; all 29 original subject areas remain accessible.
- Basic private AI setup is explicitly introductory, while reasoning-quality-versus-speed benchmarking and production infrastructure are distinct, advanced work.
- Added the ownership-versus-rented-AI conflict to the main hero within roughly the original paragraph length (53 to 51 words).
- Prices, Calendly booking destinations, and the other service offerings remain unchanged.

## 2026-11-16 — Added competency-based AI training to /preview/

- Preview homepage now shows six learner levels, from everyday AI use through private AI infrastructure and system architecture.
- AI training service page now maps 29 training areas to expandable learning levels and example labs, using the 439-competency master in pbchrist/agent-native-suite/docs/curriculum/.
- Training copy includes Hermes, memory, RAG, MCP, GitHub, local inference, NVIDIA/CUDA and Linux rather than only general chatbot skills.
- All prices, Calendly links, evaluation offer and build positioning retained.

## 2026-11-16 — Restore original sales pages after off-topic change
- Undo the unrelated offer-funnel edits from the previous conversation turn; preserve the standalone x402 pay-per-crawl adapter and site discovery.

## 2026-11-16 — x402 pay-per-crawl edge adapter (code only; not active)
- Add ops/pay-per-crawl Cloudflare Worker and 13 passing tests: opt-in 402 for training crawlers on research pages; preserve visitors, AI search and discovery endpoints. Current GitHub Pages/Namecheap hosting has no edge proxy, so the adapter is not deployed; no wallet, API credentials, or DNS changed.

## 2026-11-10 — ICONIC Reserve connect page (staging, not live)
- One page at /agents/reserve/ in the homepage design: hero with copyable MCP endpoint and live server status, quickstart for Claude (No sign in), Claude Code, Cursor, VS Code and other clients, all 16 tools loaded live from the server's schemas.json, an in-page free assessment and synthetic demo against the real public API, the seven Marketplace services as tiles (buying through the existing checkout), permissions, FAQ. Homepage gets a short "For your AI agents" section near the bottom plus a nav and footer link; the agent directory card and llms.txt point to it; the Marketplace page is restyled in the site design with its checkout code unchanged. The in-page live test needs the allowlisted-CORS change on the public Reserve gateway (pending approval).

## 2026-11-09 — Agent discovery proof and submission readiness
- Verified official MCP Registry Marketplace v0.1.1 and Reserve v0.2.0 publication, live 14/16 public tools, corrected checkout-discovery messaging, and deployed a separate read-only A2A gateway with canonical Agent Card. Real GitHub-hosted official MCP client integration and fictional Marketplace reconciliation/Reserve $0 assessment passed, including post-metadata-change regression; all 30 MCP tools now publish titles/read-only/destructive hints. Continuous external tests run every six hours (discovery/A2A) and daily (real MCP SDK). Full evidence, known limitations, application status and the required **prove → secure → submit** order are recorded in [docs/agent-directory-submissions.md](docs/agent-directory-submissions.md). Autonomous model tool choice, organic discovery, settled SPT purchase→report delivery and ChatGPT/Claude/Google approvals remain unverified. No homepage visual changes, customer-data access or real charges.

## 2026-11-07 — Agent marketplace
- Added canonical ICONIC agent-native marketplace: seven existing business product contracts, nine live MCP tools, free bounded preflight/synthetic dataset reconciliation and unpaid order requests. Paid checkout remains disabled and prices are unapproved proposals. Added machine-readable discovery, offers, homepage/AI docs/sitemap references.\n\n## 2026-11-07
- Added canonical machine-readable Agent Assurance offer and public seven-tool MCP references. Free preflight and unpaid scoped intake are working; paid checkout stays disabled. Corrected stale Reserve tool-count copy in AI reference files.

# ICONIC website (iconic.onl) — change log

Newest first. One line per change: what changed and why.

## 2026-11-08
- Add Google Analytics 4 measurement (G-0G5007D0F7) to public HTML pages, count confirmed Calendly bookings without personal data, and update privacy disclosure; exclude embedded calculator to avoid duplicate page counts.

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
