# ICONIC Demo: Root-Cause Reliability Release

**Date:** November 7, 2026
**Release type:** Fixed production-facing browser and evidence-routing defects, no model or customer-data mutation
**Branch:** `fix/demo-reliability-root-causes-2026-11-07`
**Pre-release production SHA:** `784d773f0fb0c14239545185b98b87353915be69`

## What was actually wrong

The old 45-question audit found 22 failed cases in the November 6 build. Later releases fixed many factual and browser problems but **did not independently regrade the full original 45 under their exact conditions**. Running an API request successfully does not establish factual correctness.

One important root cause was still present even in the November 7 patched release: a chat answer stored only `q` and `a` in the next turn's history. The UI kept source cards separately, but the server had **no binding between a prior answer's citation [2] and its actual file**. Asking *"Show me what source [2] supports"* could therefore generate a quotation from the *current response's* unrelated [2]. A desktop browser run initially looked good; a mobile run reproduced this exact error. That early candidate was discarded. This is why evaluating across browser sizes matters.

A second root cause: unrelated recent documents could be padded into focused requests, and unrelated company documents appeared as source cards for a harmless four-line cat poem.

## Fixes in this release

### 1. Citation continuity becomes part of conversation state

- The UI saves a bounded list of citation metadata per response: source number, document ID, relative source path and title. It persists across browser reloads using the existing **workspace-scoped session storage**.
- The server treats the supplied metadata as **untrusted**. Both document ID and relative path must match a document indexed in the *currently selected workspace*. It will not resolve a Northline document under Hollis.
- An unqualified "source [n]" question refers to the **immediately preceding** response, never an older turn whose reused number means something different.
- Old conversations without source metadata are handled with explicit uncertainty rather than a fabricated citation.
- The source number from the **previous** answer is rendered as plain text (`source #2`), not a clickable `[2]` that would accidentally open a different document. The current source number alone is cited.

### 2. Exact source challenges are deterministic

A typed evidence operation now resolves the prior citation and checks the actual tenant-authorized file. It attempts to locate a matching exact line from the document using the prior cited claim, returning the **literal source excerpt** with only that challenged document shown as a card.

If the document cannot be resolved or the relevant claim is not supported, ICONIC says it cannot verify that claim. It must **not** ask Qwen to invent a plausible explanation of what the file says.

The bounded excerpt matcher recognizes monetary and percentage values and applies no hardcoded business names, model answers or customer-specific dollar figures.

This is **not a general semantic proof checker**; other business claims and citations still require independent verification.

### 3. Source retrieval is proportional to intent

- Creative-only requests such as cat poems, haikus, jokes and fictional stories use **no business files, source cards or prior business-chat context**.
- Source-grounded creative requests (for example, "write a poem using our vendor documents") remain able to retrieve files.
- Only genuine company-wide overview questions pad context with broad recent documents. A focused question about a vendor, contract or customer no longer gets unrelated recent documents as filler.
- Source challenges show the single challenged document, not six sources that might falsely imply corroboration.

### 4. Evaluation tools now retain source continuity

`scripts/replay_45_original.py` includes prior source IDs and relative paths in replay histories. Its console output clearly labels **historical** verdicts as `OLD_FAIL` / `OLD_PASS`, not new grades.

The actual original-question replay stores all 45 case identifiers in local private JSON. Cases 23 and 43 require real browser handling and cannot be scored from API-only simulation.

### 4. General decision-status reasoning guards against unearned approval

The full original-question API replay revealed a **genuine new candidate regression**: ICONIC claimed that a 6 a.m. loader shift had been approved even while quoting a newer record saying Ray was still to decide. This was an unacceptable business-status hallucination, so the first candidate was not deployed.

The new business-agnostic `approval_contract.py` now distinguishes explicit approval, rejection, pending decisions, and conflicting evidence by comparing relevant source passages and document dates. "Doable", "proposed", and "decide by" cannot be promoted into documented approval. It quotes the exact status evidence; ties between conflicting same-day records cause abstention. Tests also cover fabricated unseen business scenarios involving genuinely approved changes, proposals, later reversals, and unrelated documents. The actual original case 38 now returns **"No final approval is documented"** and cites both pending newest and unapproved older records.

### 5. Broad cross-file financial-risk questions are now routed correctly

The original-question replay exposed an unintended side-effect of removing source padding: the company-wide question "What's the biggest immediate financial risk?" had been treated as a focused lookup with zero evidence. A general intent classifier now recognizes "biggest/top/main risk/concern" as a company overview (except when scoped to a specific contract, vendor, or project), retrieves multiple sources, and qualifies the ranking as judgment. In the next isolated live replay, the answer correctly mentioned $186,400 in slow-moving inventory and compared documented vendor/competitor pressures rather than falsely saying there was no financial evidence.

### 6. Fraudulent source-number reassignment is explicitly corrected

Source challenges now accept `source [2]`, `source #2`, and `source 2`. If a user asks for a specific money amount or percentage allegedly in an earlier source, the operation checks **that exact prior authorized document** for the figure before attempting to quote any passage. If absent, it reports the mismatch and can identify the actual other cited document where the amount does appear. In the original Case 40, it correctly said that vendor scorecard source #2 **does not contain $7,030**, which is in the Pacific Brass terms (previous source #1). It never invents a quote or pretends the scorecard supports the figure.

## Actual verification

- **154 Python automated tests** passed, including typed evidence contracts, tenant-validated citations, unknown-source abstention, and prior-citation mismatch detection.
- Node regression proves source mappings survive reload/storage serialization and remain distinct across Northline and Hollis.
- **18/18 live targeted regressions** passed on isolated staging.
- Full original **case 43** browser conversation passed on desktop and mobile: Northline Gina Moss conversation, reload, author attribution, switch to Hollis, Sam Ortiz byline, and no Northline history leakage.
- New **actual model and browser citation challenge** passed on desktop (1280px) and mobile (390px), including reload, exact vendor-scorecard row, one relevant source card, unrelated business poem with no sources, and cross-workspace abstention.
- The complete final candidate passed the real-source citation browser test on **both desktop and mobile** and the general UI browser regression on **both sizes**, using live workspace APIs and actual Qwen for the citation challenge.
- Original high-risk cases **20, 21, 38, 40** were retested in complete corresponding real Qwen API conversations with source mapping: case 20 quoted the scorecard, case 21 retrieved business financial risk instead of claiming no documents, case 38 identified pending approval, and case 40 rejected the incorrect $7,030 source.
- Additional original-question replays on the revised stage cover historical cases 20, 21, 38 and 40, with exact source mappings and real Qwen answers. The first broad 45-case API replay exposed the approval-status regression, which was corrected and retested before release. All 45 original identifiers have been replayed as API cases/browser-only markers, but a complete independent after-release factual and browser grade across the original 91 attempt rows remains outstanding; do not claim 45/45.
- Additional original-question replays and independent scoring are recorded separately. Treat an HTTP success or regex match as a **technical check**, not independent universal factual verification.

## Safe deployment contract

- Keep Qwen3.8-27B on the RTX 3090 running unchanged, keep local embeddings/model failover/Reserve online.
- Release via existing health-checked `iconic-command-update.service`, restarting only the lightweight ICONIC web service.
- Record pre-release SHA `784d773f0fb0c14239545185b98b87353915be69` and verify exact branch fast-forward before deployment.
- Production remains with `ICONIC_EVIDENCE_MODE=shadow`, `ICONIC_HYBRID_RETRIEVAL=0`, `ICONIC_VISITOR_LEARNING=0` and private evidence auditing enabled.
- After deployment, verify public homepage/embedded demo, production Qwen PID and health, mobile/desktop browser tests, targeted regression suite, and a manual rollback dry-run.
- Use `scripts/evidence_release_control.py rollback --expected-current <new full SHA> --to 784d773f0fb0c14239545185b98b87353915be69` as an initial dry-run. `--apply` only if production is failing. The known-good exact SHA is preserved; no database deletion or model restart is part of rollback.

## Remaining work

This is a **real, general correction of source continuity**, not a guarantee of everlasting correctness.

- Independently grade all 45 original cases under the original complete browser and multi-turn conditions, including every fresh-session attempt, cited source support and business arithmetic.
- Maintain 50+ truly novel holdouts, ensuring modifications improve unfamiliar phrasing rather than only these demonstrations.
- Replace more domain-specific guards with typed evidence plans and a complete claim-to-source entailment checker, while retaining strict no-regression gates.
- Harden server-authenticated tenant state before loading any real customer workspaces beyond the current fictional demos.
- Monitor production responses and private audit integrity without automatically promoting instructions, weights, or unchecked fixes.
