# ICONIC agent distribution: readiness, test evidence and submissions

**Operational log: 2026-11-09.** This file is the authoritative *public-discovery and platform-submission* record. Cross-repository execution handoff: [`agent-native-suite/START_HERE.md`](https://github.com/pbchrist/agent-native-suite/blob/main/START_HERE.md). Payment implementation and buyer tests belong to `pbchrist/agent-commerce-lab`; Reserve service code belongs to `pbchrist/iconic-intelligence-reserve`. Do not confuse protocol interoperability, organic discovery, platform approval or real payment settlement.

## Product and public endpoints

| Component | Canonical endpoint | Status (verified 2026-11-09) |
| --- | --- | --- |
| Agent directory | https://iconic.onl/agents/ | Published; Marketplace checkout text corrected |
| Marketplace page | https://iconic.onl/agents/marketplace/ | Seven fixed-price specialist offers; buyer-authorized checkout and human-reviewed fulfillment |
| Marketplace manifest | https://iconic.onl/agents/marketplace/manifest.json | Reports checkout enabled and 15 tools (externally verified November 10) |
| Marketplace remote MCP | https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp | Public Streamable HTTP, 15 tools verified via independent SDK |
| Reserve page/manifest | https://iconic.onl/agents/reserve/ · https://iconic.onl/agents/reserve/manifest.json | Free public assessment and synthetic sandbox, paid Reserve plans disabled, 16 tools |
| Reserve remote MCP | https://patrick-beastmaster.tailf32530.ts.net/reserve/mcp | Public Streamable HTTP, 16 tools |
| A2A discovery card | https://iconic.onl/.well-known/agent-card.json | Published and parity checked against live server card |
| A2A read-only service | https://patrick-beastmaster.tailf32530.ts.net/a2a | Separate public JSON-RPC `message/send` and `tasks/get`; NOT a payment gateway |
| Marketplace official MCP Registry | https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.pbchrist/iconic-agent-marketplace | Published v0.1.1 (latest at verification) |
| Reserve official MCP Registry | https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.pbchrist/iconic-intelligence-reserve | Published v0.2.0 (latest at verification) |

**Commercial boundary:** Marketplace's merchant-approved prices/Stripe MPP SPT entry point and human Stripe Checkout are live, but an actual **settled live SPT payment, verified order, and buyer-retrieved paid deliverable have not been proven end to end**. An HTTP 402 challenge, checkout link, or test-mode event is not a settled purchase. Reserve is a distinct free-only public service. Never blur the two. No agent may spend money without explicitly authorized buyer authority.

## Verified test evidence and exact scope

| Gate | Result | Evidence / what was actually established |
| --- | --- | --- |
| MCP Registry publication | **PASS** | [Marketplace OIDC publisher run 42686652885](https://github.com/pbchrist/iconic-intelligence/actions/runs/42686652885); official Registry API showed v0.1.1 latest. Reserve existing v0.2.0 listing verified. |
| Website/manifests/tool parity | **PASS** | [Discovery audit 42690795367](https://github.com/pbchrist/iconic-intelligence/actions/runs/42690795367), `scripts/audit-agent-discovery.py`, `.github/scripts/check_agent_discovery.py`. Checks homepage-independent discovery files, Marketplace and Reserve public manifests and 14/16 advertised live tools. |
| A2A public discovery and smoke interoperability | **PASS (limited scope)** | [A2A audit 42695747430](https://github.com/pbchrist/iconic-intelligence/actions/runs/42695747430), `scripts/audit-a2a.py`; canonical vs live card parity, public health, `message/send`, `tasks/get`, rejection of unsupported purchase and file inputs. Gateway source [agent-commerce-lab/a2a_gateway.py](https://github.com/pbchrist/agent-commerce-lab/blob/main/a2a_gateway.py). This is not exhaustive third-party A2A SDK certification. |
| External real MCP client access | **PASS** | [Official Python MCP SDK 2.3.0 GitHub-hosted run 42705959633](https://github.com/pbchrist/iconic-intelligence/actions/runs/42705959633), using a GitHub runner outside the user's Tailscale network: connected to both services without tailnet credentials, negotiated MCP protocol 2025-11-25, listed 14 Marketplace and 16 Reserve tools, successfully invoked read-only `marketplace_describe` and `reserve_describe`. |
| Useful fictional workflows | **PASS (two fixtures)** | [Run 42706294724](https://github.com/pbchrist/iconic-intelligence/actions/runs/42706294724). `marketplace_reconcile_synthetic`: previous alpha=100,beta=50; current alpha=80,gamma=70; correctly found new gamma, missing beta and alpha delta -20; explicit **disappearance ≠ sale** limitation. `reserve_assess`: fictional dealership, bounded pilot recommendation, `amount_charged_cents=0`, `payment_status=NOT_REQUIRED`, `can_purchase_now=false`. No production client data. |
| Tool review metadata | **PASS** | 14 Marketplace and 16 Reserve live MCP tools now have explicit titles, `readOnlyHint` and `destructiveHint`. Source commits [Marketplace 583d40c](https://github.com/pbchrist/agent-commerce-lab/commit/583d40c491f8e39f07fcdcf1e68391abe4551865) and [Reserve eba029c](https://github.com/pbchrist/iconic-intelligence-reserve/commit/eba029ca9699c9ee389c657316cadfd43188a8fb). Tools which can initiate payment/order writes are classified conservatively. |
| Regression after metadata redeploy | **PASS** | [Independent SDK run 42707217771](https://github.com/pbchrist/iconic-intelligence/actions/runs/42707217771). Both public servers and fictional workflow assertions still pass after service update. A2A and existing model/demo services were checked running. |
| Live model selects and invokes ICONIC MCP tools | **PASS (3 narrow synthetic cases)** | The existing Qwen3.8-27B at Beastmaster port 8082 received two real MCP tool schemas, chose the appropriate tool itself, then the harness executed the real read-only MCP call and checked output deterministically. Inventory-basic, inventory-price-field, and Reserve-fit all passed (3/3). [Harness code](https://github.com/pbchrist/beastmaster-adversarial-harness/blob/main/scripts/iconic_mcp_tool_selection.py) · [Results and limitations](https://github.com/pbchrist/beastmaster-adversarial-harness/blob/main/MCP_TOOL_SELECTION_EVALUATION.md). This tests preconfigured tool choice, **not** organic agent discovery. |
| Unprompted third-party agent finds ICONIC by business problem alone | **NOT PROVEN** | Registry appearance is listing/publication, not proof of search ranking, model recall, tool installation or customer adoption. |
| Negative/abuse, multi-client and payment lifecycle | **PARTIAL / NOT COMPLETE** | Read-only MCP and limited A2A rejection cases passed. No full adversarial suite or successful settled, authorized MPP SPT purchase → payment verification → report delivery → replay protection. Do not charge or expose secrets to close a checklist. |
| Independent directory approvals | **NOT VERIFIED** | No confirmed ChatGPT/Anthropic/Google directory approval. Google application reportedly submitted earlier; its current status needs verification from account/platform. Glama inclusion and PulseMCP status not independently verified as of this log. |

## Correct order of operations — PROVE, THEN DISTRIBUTE

1. **Protocol transport and correctness (done for the tested scope).** A public GitHub-hosted MCP client must connect, enumerate tools, invoke nonmutating tools, and assert real synthetic outputs. Keep daily real-client and six-hour discovery/A2A audits green.
2. **AI tool-selection evaluation (FIRST 3 CASES COMPLETE; expand next).** Actual Qwen was offered the two live read-only MCP tool schemas and correctly chose, invoked, and generated verifiable outputs for three fictional cases. Next expand into blinded, negative, ambiguous, injection, and multi-tool tasks, report error and abstention rates, and separately evaluate tool choice from *organic discovery*. Source and first scores: [Beastmaster harness](https://github.com/pbchrist/beastmaster-adversarial-harness/blob/main/MCP_TOOL_SELECTION_EVALUATION.md).
3. **Adversarial/safety gate.** Test invalid/missing arguments, private data refusal, prompt injection attempts, read/write annotations, rate limiting, replay/idempotency, and service isolation using only controlled nonconfidential fixtures. Do not touch production customer records or the 24/7 Qwen/3090 demo.
4. **Commerce gate (explicit buyer authority required for a real charge).** Verify price/offer/terms consistency, buyer-scoped SPT permissions, authorized limited spend, Stripe-confirmed settlement, ledger, deterministic report, private retrieval, retry/no double charge, and restore agreed nominal price after any controlled temporary experiment. Live $1 experiment requires specific spending approval; no assistant should infer it.
5. **Independent discovery and adoption tests.** On unprimed external agents, ask for help with problems ICONIC actually solves, without mentioning ICONIC or giving its URL. Record result including findability, cited listing, connection, tool invocation and usefulness. Keep *manually installed MCP tool access* separate from *organic platform discovery*.
6. **Distribute once gates are credible.** Official MCP Registry is already published; pursue Glama and other accurate indexes, test as ChatGPT custom app and Claude connector, submit through official platform review flows, and check Google's prior application. Reuse verified evidence and service metadata. Do not submit claims of unproven AI selection, customer outcomes or settled payments.

### Practical submission matrix

- **Official MCP Registry:** DONE for Marketplace and Reserve. Publication uses [`.github/workflows/publish-mcp-registry.yml`](https://github.com/pbchrist/iconic-intelligence/blob/main/.github/workflows/publish-mcp-registry.yml), and versioned `registry/marketplace-server.json`. A published name does **not** imply ChatGPT or Claude users automatically receive the service.
- **Glama / third-party indexes:** check whether the current Registry listing is indexed; claim or suggest server only where platform policy allows, and retest its published metadata. Never assume automatic pickup.
- **ChatGPT app submission:** configure/test as a real supported ChatGPT app with the required app/connector metadata, user-facing test cases, privacy/terms/support and tool safety review. Submission and approval are separate from MCP Registry publication. The account owner may have to review or explicitly submit.
- **Anthropic/Claude connector directory:** test integration and real tool selection in Claude, then prepare/submit according to official connector requirements, if eligible. Do not mark submitted without a confirmation record.
- **Google:** previously reported Connected Apps application; verify status before duplicating. A2A card publication alone is not an accepted Gemini integration or directory listing.
- **PulseMCP:** previous research indicated new submissions paused; recheck current status rather than asserting availability.
- **A2A:** Public JSON-RPC discovery is deployed; do not claim complete protocol conformance or broad third-party compatibility without an independent SDK/client test.

### Submission content (reuse; no invented capabilities)

**Name:** ICONIC — Business Intelligence & Agent Assurance  
**Provider:** ICONIC · https://iconic.onl · **Contact:** patrick@iconic.onl  
**Short description:** Evaluate business workflows, reconcile fictional data, assess agent reliability and explore seven human-authorized specialist services.  
**Long description:** ICONIC helps businesses evaluate and improve AI-powered operations. Agents can inspect seven service offerings, run safe synthetic previews, request scope, and prepare authorized checkout for fixed-price work. Human-reviewed services are not instant. No confidential records should be sent to public demonstration tools. A separate free Intelligence Reserve assessment helps businesses evaluate knowledge retention and outcome tracking.

### Safety and owner actions

- Public evaluation input is fictional or nonconfidential only. No automatic access to private customer data or production memory.
- No payment without explicit buyer authorization and approved payment instrument. A 402 challenge is not a charge.
- No guaranteed revenue, inventory sales, causal uplift, or independently verified customer outcome from previews.
- Privacy https://iconic.onl/privacy.html · Terms https://iconic.onl/terms.html · Marketplace terms https://iconic.onl/agents/marketplace/terms.html · Refunds https://iconic.onl/refunds/
- **No owner click needed to maintain tests, repair metadata, or prepare a submission packet.** Owner interaction is reserved for a real identity/terms acceptance, permission/authorization, platform-account submission, or actual expenditure, when genuinely required and explicitly identified.
- **Production safety:** do not change homepage appearance, restart the Qwen/3090 demo, disrupt 4060/Cyberpunk, expose secrets, or touch customer-private records.

### Runnable test evidence

- Every 6 hours: `.github/workflows/audit-agent-discovery.yml` runs public website/Registry/MCP contract and A2A smoke checks.
- Daily and on demand: `.github/workflows/real-mcp-client.yml` installs pinned official MCP SDK and runs `scripts/test-real-mcp-client.py` from an outside GitHub-hosted runner.
- Run current tests manually under **Actions**; verify the logs before marking work complete. A passing CI run is evidence of *its exact assertions*, not blanket agent interoperability or product-market fit.

**Bottom line:** the correct order is external real-client proof → useful synthetic product proof → genuine model-driven tool selection and safety/commerce proof → independent discovery → additional directory submissions. The first two and a narrow 3/3 genuine model-selection baseline are now verified within tested scope. Broad model reliability, organic discovery, full safety/commerce, and third-party acceptance gates remain open.


## 2026-11-10 live deployment and independent evidence

- Source: [commerce implementation d64a0f8](https://github.com/pbchrist/agent-commerce-lab/commit/d64a0f8) and [public discovery 87c781e](https://github.com/pbchrist/iconic-intelligence/commit/87c781e).
- GitHub-hosted external official MCP SDK passed 15 Marketplace and 16 Reserve tools, actual read-only synthetic reconciliation, new fictional public-priced-stock pattern analysis, and $0 Reserve fit assessment: [run 42885988608](https://github.com/pbchrist/iconic-intelligence/actions/runs/42885988608).
- Public manifests, live tool-list parity, Registry listings, A2A and offline site references passed: [run 42885993830](https://github.com/pbchrist/iconic-intelligence/actions/runs/42885993830).
- Site GitHub Pages publishing passed [run 42885779888](https://github.com/pbchrist/iconic-intelligence/actions/runs/42885779888). External Mac connected to both updated MCP endpoints, exercised public pricing pattern detection on three fictional stock IDs, checked 13 reconciliation and five pricing checks, and verified Assurance's standalone/live Marketplace price distinctions.
- No paid Stripe SPT settlement/delivery, real-customer improvement, cross-system production Reserve integration, or organic AI discovery has been established. Search-only baseline: 0 of 3 unbranded Bing queries returned ICONIC in top ten; [reproducible sample](organic-discovery-sample-2026-11-10.json).

## 2026-11-10 additive pricing-pattern release

marketplace_analyze_public_inventory is a read-only, bounded MCP preview taking explicitly authorized **nonconfidential publicly advertised** stock IDs and prices in two supplied snapshots (up to 100 rows each). It does not query private VIN/DMS systems, retain inputs, claim that missing vehicles sold, or infer competitors' algorithms. Arithmetic, fleet-wide identical-delta groups, duplicates and ambiguity are independently rederived. The paid dataset-diff-report public-inventory test worker now includes a separate independently verified pricing-pattern finding after a signed test-mode payment event.

The standalone Assurance service remains a distinct intake/ledger and must explicitly point to the canonical Marketplace MPP offer when available; do not imply that standalone checkout being disabled makes the Marketplace offer unavailable. No real Stripe charge is authorized by this release. Historical 14-tool SDK results above remain historically accurate; obtain a new third-party 15-tool SDK result before claiming the upgraded endpoint is independently proven. Organic discovery from problem-only prompts remains unproven until separately measured.

## 2026-11-10 live checkout handoff — separate legacy processor remains off

Agent Assurance is payable through the existing live Marketplace Stripe-hosted Checkout or Stripe MPP SPT, at the Marketplace's approved $1,500 buyer total. Its separate legacy Stripe processor is deliberately not activated because it has no configured live payment link/API key and would create a competing order ledger. The public Assurance MCP reports live Marketplace payment availability and its authorized checkout tool redirects the human buyer to https://iconic.onl/agents/marketplace/?offer=agent-reliability-evidence-audit#offers . The Marketplace webpage opens that product's existing secure Stripe-buy form without automatically submitting or charging anything. The buyer explicitly enters nonconfidential scope/contact, authorizes spending, then the central Marketplace gateway creates the actual Stripe Checkout session and subsequently verifies payment. Agents can instead use the published Marketplace MCP SPT purchase instructions and tools. Assurance scope-intake access tokens must never be treated as Marketplace payment receipts, and the buyer must retain the newly issued Marketplace order capability for fulfillment. An unattended paid audit is not claimed.
