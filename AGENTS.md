# ICONIC public website — agent instructions

**READ FIRST:** [Canonical operational handoff and next $1 live-purchase test](https://github.com/pbchrist/agent-native-suite/blob/main/START_HERE.md). Seven ICONIC services are now marked purchasable in the live MPP catalog. Live payment *challenges* were verified, but no successful settled live SPT transaction and report delivery has yet been observed. Do not misstate that distinction.

The website in this repository is the static GitHub Pages site `iconic.onl`, **not** the live payment backend. The source of truth for live price and payable state is `https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog/offers` (separate `pbchrist/agent-commerce-lab`). Static `agents/marketplace/offers.json` and `manifest.json` must agree with the live API.

**Next step:** after identifying an authorized buyer agent with a valid, $1-limited Stripe SPT wallet, coordinate a *temporary* $1 price for `dataset-diff-report` across backend approvals and public catalog, run the actual transaction and report retrieval, restore $29, and document verified Stripe evidence. Do not change merchant prices or charge anyone just to write docs.

Keep `agents/marketplace/terms.html`, `/refunds/`, `llms.txt`, `llms-full.txt`, sitemap and discoverability truthful. Production deploy uses GitHub Pages; verify the published site after pushing. Never leak financial credentials or private customer data. Preserve existing live demo and other products.
