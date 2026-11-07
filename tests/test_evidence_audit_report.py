"""Audit-monitor verification: every accepted request needs a terminal event."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import evidence_audit_report as report
import evidence_trace


class AuditHealthTests(unittest.TestCase):
    def test_successful_private_audit_report(self):
        with tempfile.TemporaryDirectory() as root:
            j=evidence_trace.EvidenceJournal(root)
            j.append("request.accepted",request_id="one",status="accepted")
            j.append("verification.claim",request_id="one",reason="cited_semantics_unverified",
                     claim_ref=j.ref("private question"),claim_index=1)
            j.append("verification.completed",request_id="one",
                     verifier_status="needs_review",claim_count=1)
            j.append("response.completed",request_id="one",result="answered")
            outcome=report.audit_report(j.path)
            self.assertEqual(outcome["accepted_requests"],1)
            self.assertEqual(outcome["completed_or_failed_requests"],1)
            self.assertEqual(outcome["claim_checks"],1)
            self.assertEqual(outcome["status"],"pass")
            path=Path(root)/"health.json"
            report.save_private(path,outcome)
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            self.assertNotIn("private question",path.read_text())

    def test_stale_incomplete_request_alerted(self):
        with tempfile.TemporaryDirectory() as root:
            j=evidence_trace.EvidenceJournal(root)
            j.append("request.accepted",request_id="unfinished",status="accepted")
            x=report.audit_report(j.path,max_pending_minutes=-1)
            self.assertEqual(x["status"],"pending_request_alert")
            self.assertEqual(x["overdue_open_request_count"],1)

    def test_hash_chain_damage_detected_by_monitor(self):
        with tempfile.TemporaryDirectory() as root:
            j=evidence_trace.EvidenceJournal(root)
            j.append("request.accepted",request_id="one")
            j.append("response.completed",request_id="one")
            with j.path.open("a") as f:f.write("{}\n")
            with self.assertRaises(ValueError):
                report.audit_report(j.path)


if __name__=="__main__":
    unittest.main()
