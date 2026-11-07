"""Untrusted independent reports must never become trusted prompts or executable code."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import qa_bridge as qb

class QABridge(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        s=Path(self.temp.name)/"state"
        for key,value in {"STATE":s,"INBOX":s/"qa-inbox","ARCHIVE":s/"qa-processed",
                          "REJECTED":s/"qa-rejected","PENDING":s/"qa-pending",
                          "LEDGER":s/"qa-results.jsonl","INDEX":s/"qa-imports.json",
                          "APPROVED":Path(self.temp.name)/"approved.json"}.items():
            p=patch.object(qb,key,value);p.start();self.addCleanup(p.stop)
        self.s=s

    def write(self,rows):
        p=Path(self.temp.name)/"report.json"
        p.write_text(json.dumps({"results":rows}))
        return p

    def sample(self,**extra):
        return dict({"name":"external_test", "question":"When does the customer agreement renew?",
                     "workspace":"northline-supply", "answer":"wrong citation [2]", "pass":False},**extra)

    def test_failed_report_stages_action_without_touching_prompts(self):
        r=qb.ingest(self.write([self.sample()]))
        self.assertEqual((r["failures"],r["cases"]),(1,1))
        findings=list(qb.PENDING.glob("*.json"))
        self.assertEqual(len(findings),1)
        finding=json.loads(findings[0].read_text())
        self.assertEqual(finding["status"],"needs_review")
        self.assertIn("Unverified QA text",finding["caution"])
        self.assertFalse(qb.APPROVED.exists())

    def test_reimport_deduplicates_and_records_retest_without_silent_closure(self):
        p=self.write([self.sample()])
        qb.ingest(p)
        self.assertTrue(qb.ingest(p)["duplicate"])
        p=self.write([self.sample(**{"pass":True})])
        qb.ingest(p)
        self.assertEqual(len(qb.LEDGER.read_text().splitlines()),2)
        item=json.loads(next(qb.PENDING.glob("*.json")).read_text())
        self.assertEqual(item["status"],"retested_pass_needs_review")

    def test_missing_verdict_is_not_an_automatic_pass(self):
        x=self.sample();x.pop("pass")
        r=qb.ingest(self.write([x]))
        self.assertEqual(r["inconclusive"],1)
        self.assertEqual(r["passes"],0)

    def test_inbox_consumes_valid_and_quarantines_invalid_reports(self):
        qb.INBOX.mkdir(parents=True)
        self.write([self.sample()]).replace(qb.INBOX/"good.json")
        (qb.INBOX/"bad.json").write_text('{"results":"not list"}')
        qb.scan_inbox()
        self.assertFalse(list(qb.INBOX.glob("*.json")))
        self.assertTrue(list(qb.REJECTED.glob("*.invalid")))
        self.assertEqual(len(qb.LEDGER.read_text().splitlines()),1)

    def test_rejects_missing_questions_oversize_and_bad_shapes(self):
        for rows in ([{"pass":True}],[],["hello"]):
            with self.assertRaises(ValueError):qb.ingest(self.write(rows))

    def test_source_promotion_requires_actual_documentary_evidence(self):
        r=qb.ingest(self.write([self.sample()]))
        cid=json.loads(qb.LEDGER.read_text().splitlines()[0])["id"]
        with self.assertRaises(ValueError):
            qb.promote(cid,"customers/key-accounts.md",["The moon is made of cheese"])
        with self.assertRaises(ValueError):
            qb.promote(cid,"../../.config/iconic-command.env",["secret"])
        self.assertFalse(qb.APPROVED.exists())

if __name__=="__main__":unittest.main()
