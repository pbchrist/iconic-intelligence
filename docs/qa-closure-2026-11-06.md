# ICONIC Command | November 6, 2026 adversarial QA closure

## Deployment
- Production: Beastmaster, ICONIC Command on port 8771 behind Tailscale Funnel.
- Local model: Qwen3.8-27B at 127.0.0.1:8082, independently pinned.
- Repository: pbchrist/iconic-intelligence, deployed from dashboard.
- The updater includes tested post-release health checks and automatic rollback.

## Live adversarial verification
- 58 automated unit tests passed.
- 23 distinct live adversarial questions were run against the public Funnel URL across Northline Supply Co. and Hollis & Reyes LLP.
- 20/23 passed their initial automated graders. Three false negatives due to narrow word matching were inspected against the actual answer text, then asked again with corrected graders, and passed.
- Eight priority checks: bilingual Q3 totals, Pacific Brass eligible stock/cap/net credit, Evergreen renewal and contract false premise, bar-sanction false premise, instruction-reveal attempt, password request and cross-company data leak.
- Fifteen expanded checks: fabricated firings, unsupported historical revenue and salary, cross-company leakage, arithmetic, invented court verdict, partner billing granularity, SSN, Spanish business-risk reply and harmless poem.
- Business source totals verified: Q3 billed $1,284,000 and collected $1,027,000; eligible Pacific Brass stock $23,100, cap $15,000, net credit $12,750; Evergreen renewal January 15, 2027.
- Raw outputs persisted under the application state directory as qa-live-2026-11-06.json and qa-live-extended-2026-11-06.json, with corrected rechecks in qa-live-recheck-2026-11-06.json and qa-live-extended-recheck-2026-11-06.json.
- Repeatable scripts: scripts/live_adversarial.py and scripts/live_adversarial_extended.py.

## Automatic rollback verification
An isolated repository and simulated health endpoint in scripts/test_rollback_integration.py:
1. Installed a release that passed unit tests but failed startup health.
2. Restored last-known-good SHA and service health.
3. Blocked the failed candidate from being retried.
4. Accepted and health-verified a subsequent good candidate.

All four stages passed in isolation. Actual production deployment also logged a successful health-verified new release and saved the last-known-good SHA outside the repository. The live Qwen model was not restarted. The ICONIC web application was restarted briefly during deployment.

## Scope limits
These tests cover the stated cases, not every possible answer, prompt injection, citation or workload. Phone accessibility and sustained concurrency tests from the exploratory audit were not included.
