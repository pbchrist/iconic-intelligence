# ICONIC: safety rollback of adversarially acquired lessons

Date: November 6, 2026 Pacific.

## Reason

Independent adversarial tests were allowed to act like visitor corrections, and the small automated lesson gate accepted guidance that could pressure the assistant to agree with false premises. Observed lessons included suggestions to explain why an event happened even if the event was not supported, and to state an exact date when a user insists a cancellation occurred.

This is a prompt-level risk, not a change to Qwen3.8-27B weights.

## Remediation

- Quarantine four lessons created during the November 6 QA period, including false-firing and forced-cancellation-date guidance. Restore six previously retained November 3 conversational lessons for the moment.
- Preserve original ten-lesson JSON in local private state for audit and rollback. Quarantined lessons no longer appear in the production prompt.
- Default ICONIC_VISITOR_LEARNING=0. No visitor automatically adds new global instructions while the freeze is in effect.
- If the switch is deliberately enabled later, refuse learning from QA/test/eval/adversarial/benchmark session prefixes as a secondary safeguard.
- Preserve all stored conversations, source documents, QA results and regression tests. Do not restart the Qwen inference process or modify weights.
- Deploy through normal branch/test/update process with last-known-good app rollback.

## Limits

The change reduces a demonstrated contamination risk. It does not prove the lessons caused the 45-question audit failures. Other retrieval, arithmetic, citation and UI issues still require testing. The six November 3 lessons are not proven universally safe, so automated learning stays frozen.
