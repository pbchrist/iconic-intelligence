# ICONIC Demo — 45-case reliability release, November 7, 2026

**Branch:** `fix/demo-45-audit-2026-11-07`
**Production branch:** `dashboard`
**Prior production commit:** `eec2133`
**Safety requirement:** Keep 3090 Qwen3.8-27B and public Reserve services online. The code in this release only changes ICONIC's lightweight web application and tests. No model weights, trained adapters, automatic visitor learning, or private Reserve data are changed.

## Actual audit basis

The original independent audit is preserved at `/home/patrick/ICONIC-45-test-QA-2026-11-06.md` (tested the older `5c56985` build on Nov 6): **23 of 45 pass, 22 fail, including 20 critical case labels**. We extracted the report's 45 original questions and recorded follow-ups rather than inventing new scenarios. Historical verdicts in the replay files refer to the **old build** and must not be mistaken for verdicts on this release.

**Original-question API replay, production pre-fix:** `/home/patrick/.local/state/iconic-command/qa-runs/demo45-retest-2026-11-07.json`.

**Original-question API replay, isolated candidate:** `/home/patrick/.local/state/iconic-command/qa-runs/demo45-candidate-2026-11-07.json`.

- 45 original test identifiers processed; 43 applicable API cases, 2 browser-only switch cases (23 and 43).
- 56 HTTP POST /api/ask requests; 55 completed model/evidence answers and 1 intended weather-web-consent offer; **zero HTTP or application errors**.
- Latency of completed candidate answers: median **3.12 seconds**, p95 **5.77 seconds**, maximum **8.28 seconds**.
- **Independent post-fix 45-case grade not yet obtained.** The replay validates actual outputs and factual examples, not all original criteria, screenshots, exact citation-card mappings, source trust, or every multi-turn history variant. Do **not** claim “45/45 passed.”
- Additional focused source-grounded 18-question candidate evaluation: **18/18** mechanical checks passed. Raw report in `/home/patrick/.local/state/iconic-command/qa-runs/demo45-targeted-18-2026-11-07.json`. This is not a substitute for independent comprehensive grading.
- **98/98** automated Python tests passed, including 12 new regression tests.
- Both full desktop and mobile headless-browser tests passed against the *staging server with real workspace/document APIs and mocked question POSTs*: transcript isolation across Hollis and Northline, workspace switch, reload persistence, citation clicks opening document cards, no cross-company text. The source-click behavior is browser verified; this is **not** a proof that every model-generated assertion is correct.
- Separate real model + browser weather request showed the consent offer and successful decline without sharing the request with web search.
- Node syntax checks for client scripts passed.

## Corrected defects, with observed evidence

1. **Mobile workspace switching was impossible after choosing a business.** Mobile CSS actively disabled the chip and hid the menu; restored both and retested on a 390×844 headless Chromium viewport.
2. **Retirement phrased colloquially missed its real source.** Source `northline-supply/people/dale-pruitt-handoff.md` says Dale Pruitt retires Dec 19, 2026, no named successor. Lexical retrieval now expands “hanging up his boots / parts-buying guy” to the actual retirement/handoff document; candidate's original case 35 cited that document and gave the correct date.
3. **Citation on a third-turn legal correction drifted to an unrelated file.** Retrieval now carries the three most recent user questions rather than the last one, and system instructions explicitly require revalidation of citation numbers every turn. Candidate original case 41 kept the actual `2024-briggs-v-cascade-anesthesia.md` as source [1] through all three challenges.
4. **Q3 billed-versus-collected arithmetic and the difference from receivables.** The source itself reports 80% realization; calculated collected/billed ratio is 79.98%. The $257,000 difference is **not** the documented total A/R. Fixed paraphrase retrieval for `third quarter` and displayed both distinct metrics when requested.
5. **Pacific Brass return math and exclusions.** When asked for the complete decision, the documented $61,200 obsolete valves = $27,330 other vendor + $10,770 opened Pacific Brass + $23,100 eligible. The $15,000 cap yields a $12,750 **vendor credit** after a 15% fee; $8,100 otherwise eligible excess and $46,200 total brass value remain outside the credited return. No implied cash payment.
6. **Evergreen share was called exactly 18%.** $872,000 / $4,860,000 = **17.9424%**, which *rounds* to the reported 18%. Both the sales summary and key-account listing are properly cited, but the arithmetic is no longer stated as exact.
7. **Confusing two different Cascade vendors.** A four-percent unpassed-on price increase from Cascade Water Heater Supply lacks a documented exact dollar impact. The $30,830 slow-moving inventory belongs to *Cascade Controls*' two HVAC control-board SKUs ($16,430 + $14,400), not water heaters.
8. **LexVault renewal and fabricated savings.** Written notice deadline Nov 16 vs start of $4,660/month renewal Dec 1; historic per-matter $1,100/month estimate annualizes to $13,200 vs $55,920 quoted renewal, giving *$42,720 hypothetical difference*, not $45,000 realized savings. Teresa responsible for notice; meeting decision still deferred; no unrelated legal-withdrawal tangent.
9. **Source drawer privacy between workspaces.** A switched tenant now clears previous drawer contents immediately, and stale document GETs are ignored after a workspace switch.
10. **Yes-followup quality.** When the previous answer did not actually make an offer, a “yes” continues the same business topic instead of pretending a prior offer existed.

These are bounded, explicitly source-grounded responses and retrieval fixes. They are **not general-purpose mathematical proof, citation verification or LLM fine-tuning**. New customer documents need independent validation.

## Test commands

    cd /home/patrick/iconic-command
    python3 -m unittest discover -s tests -q
    node --check static/app.js
    node --check static/chat-state.js
    ICONIC_DEMO_TEST_BASE=http://127.0.0.1:8771 python3 scripts/test_live_ui_45.py
    python3 scripts/reliability_gate.py --base http://127.0.0.1:8771 --out /tmp/iconic-demo45-postdeploy.json

**API replay when independently testing the live system** (uses 56 questions and 45 case records, does not promote lessons):

    python3 scripts/replay_45_original.py --base http://127.0.0.1:8771 \
      --out /home/patrick/.local/state/iconic-command/qa-runs/demo45-new-replay.json

The browser regression intercepts only **question POSTs** to avoid changing model state and uses live GET APIs for business sources. The source status/answer model replay uses the real Qwen endpoint.

## Release gates and outstanding limitations

- Keep live Qwen3.8-27B process PID and port 8082 unchanged; lightweight ICONIC app update may restart port 8771 only.
- Confirm postdeployment model health, workspace browser tests, targeted live regressions, GitHub production branch SHA, and last-known-good deployment SHA.
- The **full independent browser-based 45-case audit remains to be rescored after deployment**, including source-card-by-source-card verification, multiple fresh sessions, and multi-turn cross-tenant transitions. No complete success claim before that.
- The original audit had an hourly limit temporarily raised to allow a long test; retain explicit customer rate limits and avoid leaving broad test bypasses enabled.
- Visitor automatic learning stays frozen by default. QA runs do not train weights or modify instructions.
