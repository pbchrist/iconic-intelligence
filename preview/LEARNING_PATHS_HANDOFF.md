# ICONIC AI Training — Branching Navigator Design Handoff

**Location:** [Preview homepage](https://iconic.onl/preview/#training) and [AI training](https://iconic.onl/preview/services/ai-training/#curriculum)  
**Implementation commit:** `b724c09b98d2eb26bb9b0d1f06ba3bf2fef5b1ea`  
**Status:** Functional first pass, awaiting presentation polish.

## Intent

**Primary mode of access is a branching narrative**, like choosing actions in a game. Start with the customer's need rather than a numbered course list or ascending technical difficulty.

The first question is **"What do you want AI to do?"** Visitors pick one of five directions:

1. I don't know where to start.
2. I want my own private AI.
3. I already use AI, but want better results.
4. I want AI to handle work for me.
5. I want to build something.

Each choice leads to a second, more specific question and then to a **practical starting point**: a recommendation, a short lab and links to relevant skills. Users can go back or restart. Homepage choices may skip the first question using the `?start=` parameter.

A second view, **BROWSE ALL 439 SKILLS**, exposes the *complete* competency list in 29 subject groups. Users can search, filter by subject and difficulty, expand or collapse groups, and download the public CSV. The inventory is not hidden behind the quiz.

## Files

- `preview/index.html` — homepage's five starting choices, **TRY MINE** hero button, and **RUNNING ON MY LOCAL AI** demo eyebrow.
- `preview/services/ai-training/index.html` — markup for both the pathfinder and the full 439-skill inventory.
- `preview/learning-paths.js` — branching decision graph (6 question nodes, 15 outcomes), back/restart/view toggles and inventory filtering.
- `preview/learning-paths.css` — base styling and responsive behavior; safe target for design polish.
- `preview/skill-inventory.csv` — downloadable competency names and labels for all 439 skills.
- `preview/offers.css` — existing offers and service styles; avoid breaking the shared page design.

## Content and UX guardrails

- Make the branching choice feel delightful and clear. It is **not** an intimidating quiz, aptitude test, certification or conversion trap.
- No sign-in, no prerequisite purchase and no user-data collection to explore.
- Preserve all 15 outcome paths, with a specific actionable first lab and direct links to matching skills.
- Keep **Back**, **Start Over**, keyboard focus, button accessibility, visible focus indication, and reduced-motion support.
- Keep the full 439-skill catalog available on demand without forcing anyone to finish the decision tree.
- Preserve the customer distinction: **a packaged local model can be easy to set up**, while choosing a sufficiently intelligent model via real-world benchmarks, speed/quality tradeoffs, and reliable production infrastructure can be harder.
- Do not resurrect "How deep do you want to go?" or sell people on complexity.
- Preserve existing `$249`, `$1,000`, `$3,000` training prices, `$1,000` Evaluation, Build by invitation, live demo integration, and Calendly behavior.
- Website is still a **preview** at `/preview/`; do not replace main homepage or change AI inference services.

## Source inventory

The complete master inventory and course-building metadata live in the private `pbchrist/agent-native-suite/docs/curriculum/` directory. The public catalog intentionally includes **skill descriptions, module and difficulty only**, without internal customer/project proof notes.

## Verification

- The GitHub `gh-pages` publishing branch contains all site files.
- The main page and the beginning of the interactive branching interface were confirmed in a public live browser session.
- The 439 HTML rows, 29 groups, navigation handlers, filters and downloadable CSV were checked at source level; the external browser run did **not** finish full interaction testing before its run budget was exhausted.
- Next QA: click a two-step path through to a result; test Back/Restart; filter inventory by keyword and level; test mobile narrow width; verify CSV download.

**Goal for design polish:** Make the branch choices feel like an approachable interactive exploration of possibilities, not a chart of technical course levels. Preserve the real content and functionality, improve the experience.
