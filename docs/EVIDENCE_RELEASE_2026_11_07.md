# ICONIC Evidence Engine — audited, reversible release

**Date:** 2026-11-07
**Safe pre-release production SHA:** `fda81ac93e0c2c3756e757a0ba0e4801353a08c1`
**Feature development baseline:** `e3013d38da1e2c23b9dfc49194f850ce776a1cd8`
**Production server:** ICONIC Command on port 8771, using existing local Qwen3.8-27B on port 8082. Do not touch the 3090 model, 4060 Ti failover, production Reserve, customer data, or model weights.

## Release intent

The system needs a general evidence-handling pipeline, **not** an expanding collection of rules hardcoded for individual sample businesses.

This release supplies a **safe, shadow-mode foundation**: general document-author attribution with exact source check; an optional, tenant-scoped local-embeddings retriever; conservative source-reference and numerical checks; private per-claim append-only audit; hourly audit integrity checks; and explicit reversible deployment control.

It **does not** yet provide a universal natural-language entailment verifier, completely generalized business calculation plan execution, trustworthy cross-tenant authorization for arbitrary paying clients, or independently certified 45/45 adversarial answers. No one should claim those capabilities or turn on enforcement until a separate release gate proves them.

## Feature flags and customer-visible impact

| Environment | Intended production value | Effect |
| --- | --- | --- |
| `ICONIC_EVIDENCE_AUDIT` | `1` | Private hash-chained audit of request, retrieval, intent, claim checks, completion and failures |
| `ICONIC_EVIDENCE_MODE` | `shadow` | Log findings **without changing streamed answers** |
| `ICONIC_HYBRID_RETRIEVAL` | `0` | Preserve current BM25 retrieval, leaving semantic retrieval isolated for additional testing |
| `ICONIC_VISITOR_LEARNING` | Existing freeze | Never resume automatic lesson ingestion from user interactions |

The only additional general answer path is source-grounded document author extraction, with a verifiable byline in the cited source. All original six business-specific guards remain for production stability until they can be replaced systematically; no silent wholesale refactor is performed.

## What is logged

The private directory `/home/patrick/.local/state/iconic-command/` contains:

- `evidence-audit-v1.jsonl`: append-only, hash-chained structured events with release SHA, pseudonymous request and session IDs, hashed prompt and document references, retrieval method, operation selected, per-claim citation/numeric findings, completion status, duration and failure class.
- `evidence-audit.key`: private HMAC key for pseudonymous references (0600). **Never commit or disclose this file.**
- `evidence-audit-health.json`: last hourly integrity and completion summary.
- `evidence-release-events.jsonl`: audited manual rollback history (source SHA, destination SHA, resulting health, no customer text).
- `last-known-good.sha`, `blocked-candidate.sha`, `pending-deploy.sha`: existing deployment protection markers.

The existing `conversations.jsonl` and `conversations.md` still contain conversation bodies for private troubleshooting; the new audit is metadata-only and does not duplicate that content. All audit files use 0600 permissions and stay on Beastmaster. Hash chaining **detects record alteration**, but does not prove truth, protect against a privileged administrator rewriting the whole chain, or by itself prevent deletion of a trailing log segment.

Operations are recorded at different stages; a failed append is written as `AUDIT_ERROR` to the service journal, **not** silently marked successful. The hourly monitor fails nonzero on corrupt journals or overdue incompletely logged requests. Retention/rotation and encrypted off-box archival are future operational items; **audit storage remains local and needs disk-space monitoring**.

## Evidence verifier scope

For each answer: extract discrete claims, identify `[n]` citation numbers, reject impossible references, check whether exact quoted phrases occur in their cited text, and flag money/percentage values that do not occur literally in cited evidence. A novel value may be a valid calculation: **flag for review, never silently call it fabricated**. Valid citations are still **not proof of semantic support**. The narrow document-author operation alone can be checked deterministically. A reusable Decimal calculator can recompute explicitly supplied formulas from anchored input spans; it refuses untrusted expressions and inventing values.

`shadow` never buffers or changes streaming answers. `enforce` is experimental and not approved for public service.

## Evidence and tests actually completed

- **134/134** Python tests, including privacy, audit integrity/tampering, safe source references, Decimal calculator, tenant-scoped retrieval fallback, and simulated rollbacks.
- **18/18** targeted live model regressions against isolated staging.
- Full Case 43 cross-tenant browser sequence on **desktop and mobile**, with actual model responses and workspace API.
- A first journal run produced **157 integrity-checked records from 26 requests**; its post-restart continuation and per-claim staging run produced **330 total records over 44 requests with zero incomplete requests**, with claim checks and 0600 permissions.
- Hybrid retrieval heldout (16 new paraphrases) found expected source in top 3: BM25 **12/16**, hybrid **14/16**. **Not good enough for feature enablement.**
- Original 45-case adversarial audit on the old build: **23 pass, 22 fail**. A post-fix replay and partial browser regrade exist, but **not** a complete independent new 45-case factual grade.

These checks support **a shadow-observability release**, not a sweeping claim that the demo is perfectly reliable.

## Rollback strategy — automatic and explicit

The existing `update.sh` tests a candidate before updating the live lightweight web app. It health-checks the service and automatically restores the previous Git commit on failure. That release process does **not restart the Qwen model service**.

The new `scripts/evidence_release_control.py` adds **manual code rollback** guarded by: exact full SHA, clean `dashboard` working tree, ancestor check, explicit `--apply`, 8771 health check, candidate blocking to stop automatic reinstallation, verified last-known-good marker, and private rollback event log. Its six simulated rollback cases pass, including failure restoration.

Before rollback, inspect:

    python3 /home/patrick/iconic-command/scripts/evidence_release_control.py status

Dry-run; substitute the **exact 40-character new production commit**:

    python3 /home/patrick/iconic-command/scripts/evidence_release_control.py rollback \
      --expected-current <EXACT_NEW_40_CHARACTER_COMMIT> \
      --to fda81ac93e0c2c3756e757a0ba0e4801353a08c1

Execute **only if needed**:

    python3 /home/patrick/iconic-command/scripts/evidence_release_control.py rollback --apply \
      --expected-current <EXACT_NEW_40_CHARACTER_COMMIT> \
      --to fda81ac93e0c2c3756e757a0ba0e4801353a08c1

This changes the dashboard's code and restarts only `iconic-command.service`; customer files, audit logs, and LLM service are left alone. The failed new SHA is blocked in the existing deployment system until a different candidate is pushed or an operator explicitly intervenes.

**A manual rollback is not a permanent GitHub branch revert**: later pushes to `dashboard` may introduce a different SHA and update again. Keep the release event and the verified old SHA available.

## Operations after deployment

    # Read-only audit integrity, claim/retrieval counts, failures
    python3 /home/patrick/iconic-command/scripts/evidence_audit_report.py --save

    # Hourly scheduled monitor (user systemd)
    systemctl --user status iconic-evidence-audit-integrity.timer

    # Public demo and model health
    curl -fsS http://127.0.0.1:8771/api/status
    curl -fsS http://127.0.0.1:8082/health

The timer never runs model inference or trains weights. Event artifacts and tests remain local. The audit log and rollback record must never be committed to GitHub.

## Next engineering gates

1. Score all original 45 cases independently, in the exact browser/conversation context, with document-by-document evidence review.
2. Build the **general evidence planner and independent claim-support verifier**, not more vendor/date-specific phrase rules. Require source-span provenance and user-visible uncertainty.
3. Improve hybrid retrieval on truly held-out cross-company prompts, then enable only behind a measured, reversible flag; add tenant authorization at the server boundary before handling real client workspaces.
4. Establish deployment criteria (zero critical failures, measurable citation correctness, correct calculations, no cross-tenant leakage, p95 latency, and rollback rehearsal). Only then deprecate special-purpose guards.

**Truthful status:** auditable, reversible foundation; full generalized intelligence reliability still in development.
