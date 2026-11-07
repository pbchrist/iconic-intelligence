# ICONIC reliability release: evidence-first answers and preserved conversations

**Date:** November 6, 2026 (PST). **Branch:** fix/reliability-evidence-switch-2026-11-06.

## Why this exists

An independent 45-case browser QA report on the previous demo found 23 passes, 22 failures (20 categorized critical by that reviewer). The earlier narrower 23-question audit was insufficient to establish reliability. The independent report also has unresolved source-card maps and reproduction gaps. Treat the 45-case labels as independent findings, not as a claim that every root cause is verified.

This release prioritizes factual correctness, citation provenance, not hallucinating A/R or automatic legal actions, and preservation of separate business conversation histories. Production model weights and visitor lesson learning are untouched. The previous rollback of contaminated lessons remains effective.

## Implemented

- Financial evidence path (finance_guard.py): If one explicit primary document gives billed and collected totals, use decimal math and that document's actual citation. The Q3 billed/collected pair of $1,284,000/$1,027,000 yields 79.98% collected. A $257,000 arithmetic gap is NOT a documented accounts-receivable total. It explicitly requests a receivables ledger rather than inventing its balance. Also handles hyphenated third-quarter collection paraphrases. Other periods and company-specific requests are not silently replaced.
- Vendor-return evidence path (buyback_guard.py): Only when all five numbers exist in one real source and reconcile, distinguish $23,100 eligible Pacific Brass inventory, $15,000 cap, 15% fee, $12,750 vendor credit, and $8,100 eligible-but-excluded excess. Never describe the credit as guaranteed cash.
- Deadline ownership (deadline_guard.py): For explicitly dated reminder requests, match an authoritative deadline line and its parenthesized owner. Correct a visitor who names the wrong person; never send a message or claim an action occurred.
- Grounding and citations (server.py): Focused retrieval is not padded with unrelated recent files. Duplicate passages of the same document now have a single source marker within a response. Instructions require claim-to-document specificity, exact qualifiers, and no unrelated briefing or invented recommendation on ordinary questions. No whole-response LLM citation certification is claimed.
- Conversation switching (static/app.js, static/chat-state.js): Separate per-business transcripts in browser sessionStorage, restore on reload, rebind saved citation links, and ignore stale asynchronous workspace/feed/document responses. This is tab-local session persistence, not cross-device sync.
- No change to Qwen weights, production model process, or automatic visitor-learning freeze. The isolated QA candidate uses the existing live model endpoint.

## Release measurements and gates

A test run on the existing production build with twelve focused prompts from the independent 45-case report passed 3/12 under the automated mechanical checks. An isolated candidate build passed 12/12 on those prompts and 6/6 additional phrasings, before the last two deterministic refinements. The final candidate rerun passed 18/18 (12 original focused and 6 unseen questions). The 86 automated unit tests and real headless Chromium switch/reload/citation-click test passed. Raw comparison outputs are stored locally in /tmp/iconic-reliability-baseline.json, /tmp/iconic-reliability-candidate-v2.json, /tmp/iconic-reliability-unseen.json, and /tmp/iconic-reliability-final-candidate.json. This is targeted smoke/regression coverage, NOT a complete rerun of all 45 browser scenarios.

Some checks use mechanical phrase matching, which can produce grader errors. The tests verify critical exact figures and avoid obvious unsupported claims; they do not certify every sentence of the generated text.

Unit acceptance:
    python3 -m unittest discover -s tests -q

Browser isolation acceptance:
    python3 scripts/test_browser_switch.py

Live-model checks without restarting Qwen:
    python3 scripts/reliability_gate.py --base http://127.0.0.1:8797

## Remaining work / explicit boundaries

1. Have the independent other model rerun all 45 browser scenarios against the new commit, including complete switch histories, opened source cards and repeated failing questions. The original 45-case score is NOT replaced by this focused test set.
2. Any unresolved citation failure needs actual source-card verification. A correct source number alone is not a guarantee that the answer's claim is supported.
3. Add a general-purpose verified computation service for financial tables beyond Q3 billings and vendor credit. Do not train on the test-set examples; maintain separate synthetic holdouts.
4. Automatic behavioral lesson promotion stays disabled. Test sessions must never write global instructions.

The existing updater tests code before deployment, restarts only the lightweight web server, checks live health, and rolls back failures. It never restarts the 3090 Qwen inference process.
