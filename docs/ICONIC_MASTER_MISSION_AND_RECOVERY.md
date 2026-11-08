# ICONIC: Master Mission, Engineering Roadmap, and Total-Loss Recovery Plan

**Project:** ICONIC private business intelligence platform
**Master record:** 2026-11-07
**Status:** Demo live; independent Mac private-state and offline code restore tested; full-model mirroring and complete bare-metal restoration remain open
**Source-of-truth code:** [pbchrist/iconic-intelligence](https://github.com/pbchrist/iconic-intelligence)
**Current verified production release (2026-11-07):** `0b7d6f672b38d410e6616ee6c6b998a6c664af97` on `dashboard`
**Pre-evidence release rollback:** `fda81ac93e0c2c3756e757a0ba0e4801353a08c1`
**Operating principle:** Preserve the live 3090 model and ICONIC demonstration. All significant changes are logged, tested, reversible, and validated before exposure.

---

## Latest production release verification (November 7, 2026)

This section supersedes earlier snapshots and historical 'latest release' statements. The original encrypted cold-rebuild archive remains pinned to its historical 2026-11-07T220404Z snapshot and was NOT silently modified.

- Production code and remote GitHub branch dashboard: SHA **0b7d6f672b38d410e6616ee6c6b998a6c664af97**, clean and verified against upstream.
- Previous known-good rollback: **784d773f0fb0c14239545185b98b87353915be69**. The release was fast-forward deployed using the health-checked web updater. A rollback dry-run passed; rollback itself was not applied.
- Complete engineering and evidence release report: **docs/DEMO_RELIABILITY_ROOTCAUSE_RELEASE_2026_11_07.md**, also present in the production repository at the same relative path.
- Root causes corrected: save previous-turn citation/file mappings across reloads; validate source ID AND relative path within current workspace; quote exact prior-document lines or abstain; detect unsupported claims about financial amounts in a prior citation; avoid irrelevant source padding for focused questions and creative requests; distinguish proposed/feasible/pending from approved using dated evidence; improve broad financial-risk evidence retrieval.
- Verified *after* deployment: **154 automated Python tests**, **18/18 live targeted regression cases**, real source-citation challenge tests, cross-business conversation switch/isolation browser tests, and general desktop/mobile UI tests. Public homepage and demo gateway HTTP 200. Private evidence audit integrity passed with no overdue open requests. Qwen3.8-27B remained online under unchanged PID 2717.
- The original November 6 audit failed 22 of 45 tests. A later API replay covered 45 identifiers (with two browser-only markers) and prompted further fixes. **There has NOT been a new independent 45/45 regrade across all original attempts and exact browser conditions.** Neither operational health nor a targeted test pass proves perfect factual accuracy.
- A fresh encrypted system-rebuild snapshot still needs to include the new production code and documents. The existing older snapshot remains a valid pinned historical recovery artifact, not evidence that the latest app bytes are included.
- Further work: independent full 45-question browser grade, novel holdout questions, generalized claim-to-source entailment, secure production-grade tenant authorization, and independently verified cloud/offsite recovery-key escrow.

---

## 1. The big mission

**Build a private, evidence-driven intelligence system that turns an organization's accumulated experience into a compounding competitive advantage.**

Every business has years of experience, decisions, mistakes, successes, customer relationships, conversations, financial records, and institutional knowledge scattered across people and systems. Much of that knowledge disappears when employees leave or goes unused because nobody can find it when a decision matters.

ICONIC's job is to make that institutional knowledge **usable, verifiable, private, and cumulative**.

A business asks a natural-language question. The system understands its intent, retrieves the appropriate authorized evidence, calculates what can be calculated, distinguishes fact from inference, cites real sources, and says what remains uncertain. When the business acts, Intelligence Reserve captures the decision, the resulting action, the observed outcome, and whether a human operator actually verified that outcome. Over time, this becomes a **private intelligence moat**: the business gains a durable memory of what worked, what failed, and why.

**This is not a chatbot trained to answer our demo questions.** It is an intelligence operating system capable of handling unfamiliar questions for unfamiliar businesses without inventing answers or requiring a new hardcoded exception for every customer.

### What winning looks like

1. A prospective customer can open the public demo and see correct, fast, source-linked answers.
2. A paying business can securely connect *its own* documents, tools, systems, and operational history.
3. The system maintains hard tenant boundaries and never answers one customer's question using another customer's private data.
4. Documents, calculations, and decisions have provenance. Material unsupported claims are flagged, qualified, or withheld.
5. Conversations retain the necessary within-tenant context and remember which actions and decisions were made.
6. Intelligence Reserve compounds independently verified decisions and results, without treating correlation as causation or a proposed action as a completed one.
7. Agents discover and use ICONIC through a properly governed MCP interface and can produce auditable business outcomes.
8. Adversarial testing proves actual improvement; isolated QLoRA training is optional and can never bypass regression gates.
9. The business can operate without its founder at the keyboard; operations can be monitored, recovered, billed, and supported.
10. **If Beastmaster is destroyed tomorrow, ICONIC can be recreated from pinned code, secure backups, model artifacts, configuration, and a tested runbook.**

### Hard constraints

- **No production outage from experiments.** RTX 3090 Qwen3.8-27B remains available for the public demo; RTX 4060 Ti experiments may not hijack its failover service.
- **No fabricated evidence or certainty.** Search hits, citations, estimates, reported outcomes, and operator-verified outcomes are different things.
- **No customer-data leakage or accidental training.** Real tenant data is not automatically incorporated into models or exported to public repositories.
- **No patchwork as product architecture.** One-off guards can temporarily protect high-risk demonstrations, but shared typed operations must eventually replace them.
- **No irreversible deployment.** Every production change has an exact previous Git SHA, preflight testing, an auditable release record, live health checks, and a rollback procedure.
- **No "backup complete" claim without a verified restore path.** GitHub alone cannot restore private SQLite databases, Hermes state, credentials, models, and domain access.

---

## 2. How the whole system fits together

```text
              Business user / paying client / external agent
                                 |
                Authenticated tenant and consent boundary
                                 |
                   ICONIC intelligence engine
             Intent -> retrieval -> evidence -> reasoning
                   -> calculation -> claim verification
                                 |
               Streaming answer with traceable sources
                                 |
           Decisions, proposed actions, actual outcomes
                                 |
                  INTELLIGENCE RESERVE
        Durable institutional memory and operator attestation
                                 |
                Synthetic-only / authorized QA
                                 |
                 ADVERSARIAL HARNESS
          Holdouts, regression gates, proof of improvement
                                 |
               Optional isolated model training
              (QLoRA on 4060 Ti, never blindly)
                                 |
            Comparison -> approval -> controlled release
                                 |
               Monitoring, audit, backup, rollback
```

**ICONIC Intelligence Engine** answers operational questions. **Intelligence Reserve** preserves the business's institutional learning. **MCP** makes capabilities discoverable and callable by other agents with the correct permissions. **Adversarial Harness** tests reliability and generalization. **Training** is a controlled research tool, not the purpose of the business. **Disaster recovery** is part of the product, not an optional housekeeping chore.

---

## 3. What's been completed, in chronological and technical order

### Foundation and infrastructure

- [x] Established Beastmaster as the independently powered Linux AI host: Ubuntu 26.04 LTS, RTX 3090 (24 GB) and RTX 4060 Ti (16 GB), with NVIDIA runtime, systemd services, Tailscale access, and monitoring.
- [x] Deployed live Qwen3.8-27B inference on the 3090 with streaming through the ICONIC web application. Model health is directly checked at `127.0.0.1:8082/health`.
- [x] Established a separate local embeddings service on port 8081 and a 4060 Ti failover/model-experiment service. The 3090 is not restarted for routine QA.
- [x] Built the ICONIC demo on fictional Northline Supply and Hollis & Reyes business data, with separate workspaces, source cards, conversations, browser UI, and the public presentation.
- [x] Published the public website at [iconic.onl](https://iconic.onl/), with the live demo reachable through its public gateway.
- [x] Introduced systemd-controlled service restart, health-checked application updates, last-known-good Git SHA, and a blocked-candidate mechanism for failed releases.

### Hardening from the original 45-question audit

- [x] Ran the original 45-case adversarial audit. The **older build scored 23 PASS and 22 FAIL**, with 20 cases labeled critical. **This is historical, not a new-release grade.**
- [x] Fixed observed problems in the deployed demo: broken mobile workspace switching, missing retirement retrieval, report/document context, Q3 accounting distinctions, return-credit math, rounded-vs-exact revenue share, similarly named vendors, LexVault renewal economics, and stale cross-workspace source drawers.
- [x] Replayed the original 45 case identifiers against the improved server and investigated omitted follow-up turns and browser-only interactions. Not all originally defined conditions have yet received an independent post-release grade.
- [x] Passed 18/18 targeted live reliability checks and desktop/mobile browser regression tests on the repaired demonstration; a set of 98 automated tests passed at that release.
- [x] Preserved the repaired release as `fda81ac`, an explicit known-good rollback reference.

### Building the general intelligence engine

- [x] Documented why six domain-specific answer guards and keyword search cannot scale to real customer data.
- [x] Implemented a **general document-author intent and evidence contract** that works on unfamiliar names and files and validates the cited byline. Verified the full Case 43 browser conversation with real model responses on desktop and mobile.
- [x] Prototyped tenant-scoped **BM25 + local semantic retrieval** with cache invalidation and BM25 fallback. On 16 new paraphrases, the expected document was in the top three **12/16 with keyword search vs 14/16 with hybrid**. **The hybrid feature remains OFF in production.**
- [x] Added a conservative `Decimal` calculation executor for explicitly source-anchored values and safe arithmetic expressions. This is not yet the automatic planner for arbitrary business math.
- [x] Added claim-level citation and numeric preflight checks. They distinguish nonexistent citations, quotations absent from referenced sources, uncited answers, and numbers needing review. **They do not prove that arbitrary model prose is true.**
- [x] Deployed the evidence system in **shadow mode**: user-facing streaming answers are unchanged; findings are recorded.
- [x] Deployed a private, hash-chained, per-request and per-claim audit journal with pseudonymous identifiers, source references, operation type, verifier findings, release SHA, completion status, and duration. The new audit does not duplicate raw customer prompts or documents.
- [x] Enabled an hourly audit-integrity/completion monitor and tested detection of corrupted journal entries and requests without terminal records.
- [x] Passed **135/135 automated tests** on the deployed evidence/rollback foundation and 18/18 targeted live checks; production release `784d773`.
- [x] Tested manual rollback against disposable Git repositories, including rollback failure and restoration of the original build; tested production rollback in **dry-run** mode. Addressed shallow-checkout history ambiguity with exact pinned-SHA verification.
- [x] Verified the production Qwen process remained online during all these experiments and deployments.

### Intelligence Reserve, evaluation, and training

- [x] Implemented Intelligence Reserve's private tenant-isolated ledger with memory, correction/recall, decision/action/outcome history, and operator-verified outcomes. Public agent discovery and private core are separate responsibilities.
- [x] Connected **synthetic-only Reserve scenarios** to the Adversarial Harness using a disposable SQLite database and real Reserve API operations. No private tenant data is included in the synthetic fixture.
- [x] Added score-only handoff from the Harness to Beastmaster Training; it contains failure categories, not customer documents or automatic training authorization.
- [x] Corrected misleading evaluation interpretation: live Qwen3.8-27B's Reserve answers were **2/9 by strict formatting**, while a limited factual-content heuristic found the expected qualifiers in **9/9**. Neither number is a human-certified overall accuracy rate.
- [x] Benchmarked Qwen3-4B Base against existing dealership-v2 and dealership-v3 QLoRA adapters on nine Reserve cases plus the 22-case independent ICONIC holdout. Both adapters failed the no-regression promotion gate and were **not deployed**.
- [x] Merged the Reserve, Harness, and training evaluation integrations into their respective GitHub `main` branches.
- [x] Scheduled a CPU-only daily Reserve synthetic contract check. This does not autonomously train or improve model weights.

### Business and distribution foundations

- [x] Established ICONIC's product narrative around private institutional intelligence and compounding verified results.
- [x] Created an MCP/agent-discovery direction and public agent-facing Reserve entry point.
- [x] Established a prototype paying-client and operator workflow direction (including the dealership pilot).
- [ ] **Not yet established:** independent commercial proof of generalized intelligence accuracy, scalable tenant onboarding, complete Day-30 outcome measurement, automated self-serve trial-to-paid conversion, or broad customer deployment safety.

---

## 4. The current truth: production versus experiment versus unfinished

| Component | Actual status |
| --- | --- |
| Public ICONIC demo / Qwen3.8-27B | **LIVE**, controlled by Beastmaster |
| Latest deployed application | `0b7d6f6`, citation continuity, approval-status verification and focused-retrieval improvements |
| Desktop/mobile switching and source UI | Tested on demo, not a universal quality certificate |
| Historical adversarial 45-case result | 23/45 on older build; **full new independent grade still open** |
| 18 targeted reliability questions | 18/18 on tested release |
| New shared document-attribution operation | Deployed with narrow source verification |
| Hybrid semantic retrieval | Built/tested; **disabled in production** |
| General source claim entailment verification | **Not complete** |
| General business math planner | **Not complete** |
| Real-customer server-side tenant authorization audit | **Not complete** |
| Intelligence Reserve | Working technical-alpha foundation |
| Reserve-to-Harness synthetic integration | Implemented; evaluation-only |
| Existing QLoRA dealership adapters | Rejected for production promotion |
| Per-claim private audit and hourly integrity monitor | Deployed |
| Manual rollback command | Tested and dry-run against production |
| Critical private-state disaster recovery | **VERIFIED ON MAC:** 23 CMS parts, 55 SQLite database restores and checksums, plaintext removed |
| Offline code / system recovery | **VERIFIED ON MAC:** five Git bundles cloned without GitHub |
| Model file mirror | **VERIFIED:** external USB eight-file hash manifest; 3 essential Mac models compared by SHA-256 |
| Recurring encrypted backups | **ENABLED:** external snapshots, Mac off-host sync retries and health checks |
| Cloud-offsite and recovery-key escrow | **NOT FULLY VERIFIED / NOT COMPLETE** |
| Revenue-generating self-serve platform | **Not yet complete** |

**Never substitute HTTP 200, a test fixture pass, or a formatted citation for factual correctness.**

---

## 5. The execution plan, in dependency order

### Phase 0 — Protect the product and create recoverability (P0, immediate)

1. Inventory code repositories, exact commits, services, ports, GPU drivers, model file names/sizes, system configuration, required external accounts, and private mutable data.
2. Keep clean pinned Git commits and independent copies of critical code; put the full disaster-recovery runbook and nonsecret manifest in GitHub.
3. Create encrypted, online-consistent **per-database** snapshots of Reserve, MemPalace, Hermes, Open WebUI, agent-client state, demo audits, secrets, and QLoRA checkpoints. Preserve live systems.
4. Place verified encrypted copies on the attached external drive and on the **separate Mac**, with an encrypted offsite/cloud copy. The decryption key must remain **off Beastmaster**.
5. Back up model files and any local uncommitted improvements separately. A missing model blob is either restored from a verified source/URL/checksum or recovered from the external mirror.
6. Save complete service activation order and fresh-host bootstrap steps; verify archive integrity and decryptability on the Mac.
7. Run a **real clean-environment restore drill**, not just a checksum. Rebuild on a separate machine/container without disturbing production; verify source files, SQLite databases, model loading, and integration smoke tests.
8. Escrow a second copy of the Mac-held **private recovery key** in a secure place controlled by the owner; if both the Mac and its key are lost, encrypted data is unrecoverable.
9. Schedule backups and failure alerts only after one complete, verified manual recovery snapshot; keep recovery media and logs private.

**Initial disaster-recovery objectives:** target RPO ≤ 24 hours for mutable business state and RTO ≤ one working day for the basic demo, contingent on spare hardware/GPUs, network access, and restore drills. These are **targets, not proven SLAs**.

### Phase 1 — Make the existing demo demonstrably reliable (P0)

1. Independently regrade all **45 original cases**, preserving complete original conversation state, browser switching, original source cards, and explicit PASS/FAIL/UNVERIFIED criteria.
2. Create **50+ unseen questions** across new phrasing, cross-file reasoning, multilingual prompts, arithmetic, persuasion pressure, corrections, misleading documents, and cross-tenant access attempts.
3. Instrument answer correctness, citation-source match, numerical correctness, uncertainty, regressions, p50/p95/p99 response latency, failures, and repeated fresh-session consistency.
4. Fix *general mechanisms* rather than adding one custom rule per failed question.
5. Define launch blockers: any verified cross-tenant leak, critical false business outcome, fabricated source, wrong high-stakes arithmetic, persistent availability failure, or irreversible deployment.
6. Retest desktop/mobile and the public website; only release once the evidence supports the claimed level of reliability.

### Phase 2 — Finish the general evidence engine (P1)

1. Replace ad hoc keyword-specific intent gates with explicit typed operations: factual lookup, person/document attribution, comparisons, calculations, deadlines, forecasts, recommendations, and creative requests.
2. Build a retrieval pipeline that combines keyword, semantic search, structured fields, ranking, and source provenance. Require improvement on *untouched* holdouts and a safe latency/fallback budget before enabling hybrid search.
3. Require **source-span evidence**, not merely a document number, for material factual claims.
4. Introduce an independently executed calculation plan: extracted source values → unit/period normalization → Decimal calculations → recomputable result → labeled assumption or estimate.
5. Add a conservative claim-support verifier and abstention policy. If the evidence is missing, conflicting, or inconclusive, say so and ask the right follow-up.
6. Replace client-trusted conversation context with authenticated tenant-scoped server state and corrections where appropriate. Do not allow prior-business chat content to become a new tenant's evidence.
7. Gradually retire the six specialized guards only as the generic replacements pass their old and new holdouts.
8. Keep release feature flags, answer traces, audit coverage, rollback drills, and production failure monitoring.

### Phase 3 — Convert memory into a verifiable intelligence moat (P1)

1. Make Reserve's decision → action → observed outcome → operator attestation a first-class product workflow.
2. Enforce immutable evidence lineage, tenant authorization, corrections, retention, and least-privilege MCP tool access.
3. Show a business what changed since Day 1, Day 7, and Day 30: verified outcomes, uncertainty, cost/benefit, and exactly which claims require validation.
4. Allow agents to propose actions but separate authorization, execution, and verification. Never equate a listing's disappearance with a verified sale.
5. Make tenant-specific institutional knowledge portable, backed up, and exportable to its rightful owner.

### Phase 4 — Prove intelligence improvement (P2)

1. Keep Reserve-generated synthetic holdouts separate from any training examples.
2. Benchmark the untuned base, proposed prompts/tools, retrieval improvements, and optional adapters on the same protected test sets.
3. Train only after proving a persistent generalizable model error. Use the 4060 Ti with a strict production GPU safety budget.
4. Reject adapters that reduce reasoning quality, violate tenant boundaries, lose previously correct answers, or degrade production latency.
5. Promote nothing without independent validation and a rollback target. Model weights do not improve automatically just because the Harness produces failures.

### Phase 5 — Productize and get paid (P1/P2, parallel with reliable core)

1. Deliver secure onboarding: customer-owned data connectors, least-privilege credentials, consent, retention settings, import auditing, and simple source management.
2. Package a clear offer: a private intelligence assessment and recurring verified intelligence/outcome tracking, not vague "AI transformation."
3. Provide business dashboards that explain *what changed, why, evidence, confidence, next recommended action, and tracked outcome*.
4. Make the MCP gateway self-discoverable and safe for agent-to-agent commerce without exposing private tenant state.
5. Integrate accounts, pricing, payments, subscriptions, access control, renewal/offboarding, and clear support responsibilities.
6. Validate with a paying pilot (e.g. dealership intelligence), measure repeatable customer value, then expand to additional industries.

---

## 6. Disaster recovery: assume Beastmaster is physically destroyed

**Disaster scenario:** Power failure, fire, motherboard death, NVMe loss, theft, ransomware, or a catastrophic operator mistake. Assume Beastmaster never boots again. Recreate ICONIC without relying on data stored exclusively on that machine.

### Recovery truth table

| Item | Rebuild source | Independent from Beastmaster? | Gap |
| --- | --- | --- | --- |
| Source code and approved release history | GitHub pinned commits; optional offline Git bundles | Yes, while GitHub remains accessible | Verify access credentials; export bundles |
| Operating system, drivers, Python and service layout | This runbook, sanitized service manifest | Once pushed to GitHub/Mac | Needs full bare-metal restore drill |
| Production and failover GGUF models | 82 GB local model directory; future external mirror | **Not until mirrored and checked** | Copy/checksum all required model weights |
| Reserve, Hermes, MemPalace, customer/agent memory | Encrypted critical-state snapshot | Only once copied off-machine and decrypted/tested | Per-DB snapshots are not cross-system atomic |
| Credentials and service configuration | Encrypted recovery archive | Only with working Mac-held private key | Second key escrow and access-token rotation |
| ICONIC audits and rollback metadata | Encrypted critical-state snapshot, private local journal | Only after verified copy | Schedule and test recovery |
| Public DNS and Tailscale routing | Account owner reconnects and reconfigures | Account-owned, not disk-owned | Document account/permission ownership and reconnect |
| External disk | Attached USB storage | Survives host-only failure if disk survives | Same physical location is **not offsite** |
| Mac encrypted copy / OneDrive sync folder | Separate Mac with FileVault | Survives Beastmaster failure | Cloud sync completion must be confirmed; Mac key needs escrow |

### Actual hardware and storage inventory (2026-11-07)

- Ubuntu **26.04.1 LTS**, current kernel **7.0.0-38-generic**.
- NVIDIA **580.178.04** driver; GPU 0 **RTX 3090 24 GiB**, GPU 1 **RTX 4060 Ti 16 GiB**.
- Approximately 1 TB internal NVMe, current filesystem about 916 GiB with 215 GiB free at inventory time.
- Attached USB volume **/run/media/patrick/2067738214reward**, HFS+, approximately **4.6 TB total and 3.1 TB free** at inventory time.
- MacBook Pro available independently over SSH/Tailscale, roughly **221 GiB free**, FileVault **ON**, OneDrive sync client running.
- Primary model `Qwen3.8-27B-Q4_K_M.gguf`; local embeddings `nomic-embed-text-v1.5.Q8_0.gguf`; separate failover model directory.
- Core user services: `iconic-command`, `iconic-intelligence-reserve`, `iconic-reserve-agent-gateway`, `mempalace`, `hermes-gateway`, `hermes-gateway-2`, `beastmaster-failover`, `brain-embeddings`, `open-webui`.
- Root services include `llama-server-qwen38`, `tailscaled`, Docker, and UPS/NUT services.

### Required repository pins (do not guess versions)

| Component | Repository | Verified commit at inventory |
| --- | --- | --- |
| Live ICONIC demo | `pbchrist/iconic-intelligence` | `0b7d6f672b38d410e6616ee6c6b998a6c664af97` |
| Intelligence Reserve | `pbchrist/iconic-intelligence-reserve` | `e4ea2af` |
| Adversarial Harness | `pbchrist/beastmaster-adversarial-harness` | `6627fb2` |
| Training research | `pbchrist/beastmaster-training` | `976107c` |
| Reserve website source | `pbchrist/iconic-intelligence` additional working tree | `d688338` |

Use the full SHA from the **encrypted recovery manifest**, not abbreviated versions, when cloning a replacement machine. Only approved `dashboard` and `main` releases should be automatically enabled.

### Recovery encryption

A dedicated 4096-bit RSA recovery certificate was generated **on the Mac**, and its public certificate copied to Beastmaster. The Mac-held private key **was not copied to Beastmaster or GitHub**.

- Mac-only private key: `~/.iconic-recovery/keys/iconic-dr-2026-private.pem` (mode 0600; protected by FileVault while the Mac is locked).
- Mac public certificate: `~/.iconic-recovery/keys/iconic-dr-2026-public.crt`.
- Public SHA-256 certificate fingerprint: `62:9A:E3:8B:68:3F:8A:45:9E:58:A3:3D:3D:A4:23:38:02:C0:4D:06:88:26:A4:98:25:E8:96:C9:1D:8C:19:AC`.
- Certificate expiry: **November 4, 2036**. Plan rotation before expiry.
- A test file was successfully encrypted on Beastmaster and decrypted on the Mac.
- **Critical missing safeguard:** The private key does not yet have a separately verified, encrypted offline/password-manager escrow. Do not mistake the presence of encrypted backup files for recoverability if that key is lost.

### The critical-state backup procedure

`scripts/disaster_recovery_backup.py` creates a **separate encrypted archive** of selected private state:

- MemPalace knowledge/index and client palaces.
- Hermes/Hermione state, operational settings, bot/agent configuration, selected workspaces and client-bot homes.
- Reserve live SQLite stores, Open WebUI state, and ICONIC demo conversations/audit records.
- Service units and selected encrypted environment/SSH/GitHub access credentials.
- Existing QLoRA adapter checkpoints and local evaluation state.
- A JSON restore manifest with repository pins and SQLite snapshot file hashes.

SQLite files are copied using the **online SQLite backup API** and validated with `PRAGMA quick_check`; services are not stopped. Cache directories, dependency downloads, earlier backup copies, and explicitly **retired/broken** archive directories are not included. Snapshots of separate live databases are *not* one atomic transaction.

**Restore-format correction:** An initial single 2.97 GB CMS archive passed copying and checksum tests but **could not be decrypted on the Mac**. It must not be used as a restore point. The new version uses split CMS (128 MiB encrypted parts) and passed an end-to-end encryption/decryption rehearsal.

A real backup is now a directory named critical-state-YYYYMMDDTHHMMSSZ containing part-NNNN.cms, SHA256SUMS, manifest.json, and VERIFIED_ON_MAC only after the off-machine tests succeed. Usability requires every part to pass its hash check and the full decrypted compressed stream to pass a Mac-side Zstandard integrity test. A second clean Mac restore validates every SQLite file against its manifest. The Mac's OneDrive sync-folder copy is not proof of completed cloud upload.

Manual invocation on Beastmaster:

```bash
python3 scripts/disaster_recovery_backup_split.py     # dry-run
ionice -c3 nice -n19 python3 scripts/disaster_recovery_backup_split.py --execute
python3 scripts/dr_capture_system.py --execute              # encrypted code/system bundle
ionice -c3 nice -n19 python3 scripts/dr_mirror_models.py --execute
```

A successful message must identify the archive, checksum, verified Mac copy, and successful Mac decrypt/decompress check. A failed run is **not a backup**; retain the last verified archive and investigate.

### Rebuilding from scratch, safely

**Step 1: Replace the host.** Obtain a replacement Ubuntu system with compatible GPUs/RAM and enough NVMe storage for models, dependencies, and databases. Do not rely on the dead host or its local SSD.

**Step 2: Get authenticated access.** Reconnect GitHub, Tailscale, DNS/HTTPS accounts, and the Mac. Use an authorized owner account. Freshly enroll the new machine; do not blindly restore a compromised Tailscale node identity.

**Step 3: Install the platform.** Install Ubuntu 26.04 LTS or a tested compatible replacement, NVIDIA driver and CUDA runtime, Git, Python and venv support, SQLite, OpenSSL, Zstandard, rsync, Docker (if required), and systemd user lingering. Recreate the two-GPU isolation policy before serving models.

**Step 4: Restore pinned source.** Clone the five pinned GitHub repositories and check out the exact full SHAs in `recovery-manifest.json`; inspect local service-specific forks and dependencies before installing. Rebuild llama.cpp and Python/Node environments at recorded versions. Do not run unattended services yet.

**Step 5: Verify the encrypted snapshot.** Obtain the matching `.cms` and `.sha256` from the Mac/OneDrive or external disk. Check SHA-256 and the expected certificate fingerprint. On the **Mac**, decrypt *without copying the private key to the replacement Beastmaster*. Review the archive inventory before extraction.

On the **Mac**, with the actual archive ID substituted, use the independently installed multipart verification and restore drills. The private recovery key remains on the Mac.

```bash
~/.iconic-recovery/verify-recovery-archive.sh critical-state-YYYYMMDDTHHMMSSZ
~/.iconic-recovery/restore-verify.sh critical-state-YYYYMMDDTHHMMSSZ
```

The second command decrypts into a protected temporary Mac directory, checks the manifest and every included SQLite database and SHA-256, and removes the temporary plaintext. Use --keep only for an intentional, authorized real restoration.

**Step 6: Restore private state to a quarantined staging directory.** After inspection, stream the decrypted archive over authenticated SSH to the replacement host or extract it into a Mac-local protected directory, then copy its `home/patrick` subtree using file-permission-preserving `rsync`. **Never untar arbitrary recovered content directly over a running production installation.**

**Step 7: Restore models.** Copy the model mirror from the external disk and verify hashes. Without the model weight files, the saved model service configuration alone cannot serve inference. Restore 3090 production and GPU1 failover separately.

**Step 8: Restore user service definitions and secrets.** Review absolute paths and credentials. Rotate compromised tokens. Activate dependencies in order: storage and networking; 3090 model and embeddings; MemPalace and Reserve; ICONIC app and gateway; secondary Hermes/agents; timers/monitoring. Confirm every tenant store's expected owner and permissions.

**Step 9: Smoke-test locally, then publicly.** Confirm 8082 model health, streaming responses, 8081 embeddings, correct workspace separation, Reserve ledger integrity, source citations, audit journal validation, public HTTPS gateway, 18 targeted regressions and the full 45-case browser evaluation. Record every failure.

**Step 10: Restore public service deliberately.** Point DNS/Tailscale/Funnel to the tested new host only after the smoke tests. Confirm that existing billing/agent clients can connect and that no unauthorized data is exposed.

**Step 11: Re-enable backups and test rollback.** Confirm that the new host produces an encrypted archive, sends it off-host, can be decrypted with the Mac key, and supports a dry-run rollback from its current commit to an actually known-good SHA.

### Explicit disaster-recovery gaps

- **Not yet proven:** a complete restore from an encrypted archive into a clean independent machine.
- **Not yet proven:** all model weights/adapters are mirrored with checked hashes on a physically separate drive or offsite destination.
- **Not yet proven:** OneDrive has actually uploaded a full encrypted backup; a local sync-folder copy is only a partial milestone.
- **Not yet proven:** a secure second copy of the Mac's recovery private key exists.
- **Not yet proven:** automatic daily encrypted backups and restore-alert monitoring across every critical dataset.
- **Known limitation:** cross-database consistency needs an application-coordinated snapshot/restore test.
- **Known limitation:** rebuild credentials may depend on user reauthentication and third-party account ownership.

---

## 7. Logging, release, and rollback standard

Every change needs an issue/mission, a Git branch, an explicit test plan, expected observed results, a recorded release SHA, and a rollback target.

Production auditing records request receipt, tenant pseudonym, prompt hash, retriever and source hashes, selected operation, per-claim verifier finding, latency, completion/failure, and version. The journal is private and integrity-checked hourly. No model training is initiated by audit events.

A deployment is approved only when:

- All selected unit, integration, browser, cross-tenant, and adversarial release gates pass.
- The observed production model and UI remain responsive; GPU0 and required clients stay online.
- The previous code SHA, encrypted data backup, operator controls, and rollback dry-run are verified.
- No critical security or factual finding is silently downgraded to a cosmetic test failure.
- Public output describes exactly what was tested and what remains unverified.

**Rollback:** `python3 scripts/evidence_release_control.py status`, followed by a dry-run `rollback --expected-current <full SHA> --to <full known-good SHA>`, then `--apply` only if a rollback is needed. The application updater's health check has a separate automated fallback. Neither path should restart the 3090 model or delete customer data.

---

## 8. Definition of done

The mission is **not finished** when the demo "usually works."

It is finished as a dependable business platform when:

- The 45 historical cases are independently regraded and no critical failures remain.
- New questions from new businesses perform at a documented, repeatable standard.
- Evidence, arithmetic, citations, tenancy, uncertainty, and conversations meet explicit release gates.
- Verified operator outcomes compound in Intelligence Reserve, and paying customers can measure the value.
- The MCP distribution and billing routes are tested without granting agents unauthorized authority.
- Existing model improvements are independently demonstrated rather than assumed.
- The service can recover from the **total loss of Beastmaster** using independent encrypted backups and a successful timed clean-host restoration drill.
- Every deployment and restoration is documented, auditable, reversible, and repeatable by someone other than the builder.

**North star: a trustworthy, private, compounding business intelligence service that earns money and survives the loss of any single machine.**


---

## 9. Verified disaster-recovery checkpoint (November 7, 2026)

This section supersedes any earlier in-progress descriptions.

### Independently verified

- **Critical private state:** Backup directory critical-state-20261107T215914Z contains **23 separate CMS-encrypted parts**, a SHA-256 checksum list and a recovery manifest. On the Mac, all parts passed hashes, decrypted into a single Zstandard stream, extracted to a private temporary directory, and **all 55 SQLite databases** passed stored SHA-256 comparison and SQLite quick_check. The second complete drill exited code 0 and removed the temporary plaintext.
- **Code and system:** The encrypted system-rebuild-20261107T220404Z.tar.zst.cms kit was decrypted on the Mac. All **five Git repositories were cloned without GitHub**, with commit hashes verified. The system/package inventory and readable root unit files are included; some root-owned NUT settings require separate reconstruction. The reusable **scripts/dr_restore_code.py** bootstrap was subsequently executed on the Mac against the decrypted kit and restored all five repositories with pinned SHA and bundle hash validation, without network access to GitHub.
- **Locations:** The encrypted snapshots are on the external USB drive and on the separately encrypted Mac. Copies also exist in the Mac OneDrive sync folder and passed local checksum verification. **Actual cloud upload completion remains unverified.**
- **Key custody:** The RSA private key exists only on the Mac (FileVault, mode 0600). It must be escrowed securely in a second location. Losing both the Mac and key would make encrypted backups unreadable.
- **Do not use:** The older single-file 2.97 GB CMS artifact critical-state-20261107T214917Z.tar.zst.cms passed checksums but could not be decrypted on the Mac. It is NOT a valid restore point. Use the split archive above.

### Automated backup schedule (installed and enabled)

| Local time, approximate | systemd timer | Purpose |
| --- | --- | --- |
| Daily 02:15 plus up to 10 minutes | iconic-dr-snapshot.timer | Create encrypted on-disk SQLite/critical-state snapshot with no need for Mac to be awake |
| 09:35, 13:35, 17:35, 21:35 plus jitter | iconic-dr-offhost-sync.timer | Send queued ciphertext to Mac; checksum and decrypt-test; place verified ciphertext in OneDrive sync folder |
| 06:05, 12:05, 18:05, 23:05 | iconic-dr-health.timer | Fail if external disk is absent or latest Mac-verified backup is older than 36 hours |

All jobs use low CPU/IO priority, locks, and never restart Qwen, Reserve, Hermes or the demo. First manual health check passed; first recurring daily snapshot has not yet been observed. A timer's existence does NOT guarantee every future backup will succeed. Failure is reported in the private systemd journal.

### Emergency restore commands and tests

On the Mac (substitute the actual timestamped backup ID):

    ~/.iconic-recovery/verify-recovery-archive.sh critical-state-20261107T215914Z
    ~/.iconic-recovery/restore-verify.sh critical-state-20261107T215914Z

The second command creates a private scratch directory, verifies the backup manifest and SQLite databases, and removes decrypted temporary state. For a true restoration, use the explicit --keep option, inspect file permissions, and transfer selected restored state to a clean replacement host over authenticated SSH. **Never copy the private recovery key to Beastmaster or GitHub.**

The reusable offline code bootstrap is available as `scripts/dr_restore_code.py`. After decrypting and extracting the system kit into a clean staging directory, run:

    python3 dr_restore_code.py --bundle-root /protected/path/extracted-system-kit --output /protected/path/new-repos

The bootstrap verifies the encrypted kit's stored Git-bundle checksums and exact pinned commits; it refuses to overwrite an existing nonempty output, and it does not start services or restore credentials. This specific command was executed successfully on the Mac on November 7 and staged all five repositories independently of GitHub.

A replacement host must install the pinned Ubuntu/NVIDIA and service dependencies, restore all five repositories at their recorded SHAs, obtain checksum-verified model weights, restore state and credentials under the correct permissions, reauthorize Tailscale/public routing, and pass model/demo/Reserve/QA tests before serving traffic. The Git-only and SQLite-only drills do not yet establish full service-level recovery.

### Remaining disaster-recovery work

- **P0:** Escrow a second encrypted copy of the private Mac recovery key, with the passphrase saved outside the Mac and Beastmaster; test decryption.
- **P0:** Confirm cloud-side OneDrive upload, quota and retention rather than assuming a local sync-folder copy is offsite.
- **P0:** Finish and checksum the complete external model mirror; keep an independent copy of at least the production Qwen model, embeddings, and failover weights.
- **P1:** Observe and record the first daily timer-driven backup, Mac-offline retry and 36-hour stale-backup alert. The initial manual off-host-sync invocation succeeded on an empty pending queue, and the recovery health service passed; these do not substitute for observing future schedules.
- **P1:** Execute a whole-platform clean-host restore drill with actual model loading and Tailscale/Funnel, not merely restored files.
- **P1:** Establish encrypted archival retention, disk capacity alerts, and cross-service point-in-time consistency.
