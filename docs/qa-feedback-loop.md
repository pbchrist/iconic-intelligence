# ICONIC: independent QA -> corrections -> permanent tests

## What is automatic

1. Intake: Put independently produced JSON reports in /home/patrick/.local/state/iconic-command/qa-inbox/. Every ten minutes iconic-qa-inbox.timer imports reports into a private ledger, archives original evidence, deduplicates, classifies failures, and queues proposed code changes and candidate lessons. Invalid JSON is quarantined.
2. Persistent evidence: qa-results.jsonl retains attempts, including failures and passing rechecks. qa-pending/ID.json contains the QA question and answer, sources, category, proposed engineering action, and possibly a candidate behavioral lesson. qa-summary.md shows status. These survive Git updates and restarts.
3. Daily live monitoring: iconic-qa-monitor.timer runs three rotating source-grounded adversarial questions once each morning against the public Funnel URL. It archives complete answers and imports results. It does not restart Qwen or deploy modifications.
4. Release protection: Every dashboard GitHub update runs all unit tests, including tests/test_qa_approved.py. Approved evidence must still exist in its real source and be retrieved for the original question. The deployment updater rolls back a release with failed health.
5. Visitor learning: learn.py separately tests visitor-correction behavioral lessons and persists approved rules in lessons.json across restarts.

## Safeguards and review gate

Independent testers are untrusted, and keyword-based graders can produce false alarms. The bridge NEVER executes an incoming script, turns an unreviewed tester recommendation into an instruction, or makes an automated code patch.

- A failed question creates a review item with a proposed repair and possibly a candidate lesson.
- Only operator-reviewed, source-verified regressions become deployment-gating tests. Promote them on an isolated feature branch, not dashboard:
      python3 qa_bridge.py promote CASE_ID --source customers/key-accounts.md --evidence 'January 15, 2027'
- The command checks the source document and current retriever before modifying qa/approved.json.
- Code fixes are made on a branch, verified, and merged through the updater.
- Behavioral candidate lessons must pass the separate learning safety gate and live regression testing before becoming real instructions.
- Close a false alarm only with an auditable explanation:
      python3 qa_bridge.py close CASE_ID --reason 'Verified corrected answer and source on fresh live retest.'

## Submission format for the other model

The other model can submit JSON through its authorized connection to Beastmaster by placing it in the qa-inbox directory. Do not submit plain prose or executable scripts.

    {
      "run_id": "independent-qa-2026-11-06",
      "results": [
        {
          "name": "evergreen-renewal-source",
          "workspace": "northline-supply",
          "question": "When does Evergreen renew?",
          "answer": "Verbatim live answer with citation numbers",
          "status": "fail",
          "expected": "January 15, 2027, citing customers/key-accounts.md",
          "reason": "Citation pointed to the vendor scorecard",
          "sources": [{"n": 2, "rel": "vendors/2026-q3-vendor-scorecard.md"}]
        }
      ]
    }

Status accepts pass, fail, or inconclusive (or a boolean pass). No verdict is INCONCLUSIVE, never silently pass. Up to 250 tests per file, up to 3 MB. The raw intake is on the local machine, not in the public Git repository.

Manual import if needed:
    python3 qa_bridge.py ingest /path/to/results.json

Summary:
    python3 qa_bridge.py report

For a dry-run of tomorrow's rotating monitor:
    python3 scripts/qa_monitor.py --dry-run

## Existing historical results integrated

- Imported the four live QA reports: 26 attempts, 23 distinct cases, 23 latest passes.
- Three earlier FAIL flags were false-negative keyword grading checks: each was examined and rechecked, with a recorded closure reason.
- Four verified, permanent source-grounding regressions: Q3 billing in English and Spanish, Pacific Brass eligible/cap/credit, and Evergreen renewal.
- Full independent testers remain available under scripts/. The daily recurring monitor only runs a lightweight rotating sample.

## Known limits

This is an audited intake and verified-regression pipeline, NOT an unattended AI code-writing agent. Raw results do not automatically become model instructions or arbitrary patches. Unit source checks prove correct evidence appears in retrieval, not that every response will be correct. More extensive adversarial assessments remain necessary.
