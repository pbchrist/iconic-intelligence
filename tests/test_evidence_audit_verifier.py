"""Verifiable private evidence journaling and bounded business arithmetic."""
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest

from evidence_trace import EvidenceJournal, verify_journal
from evidence_verifier import Quantity, checked_calculation, check_answer


class EvidenceJournalTests(unittest.TestCase):
    def test_private_durable_hash_chain_and_privacy(self):
        with tempfile.TemporaryDirectory() as base:
            j=EvidenceJournal(base,release="testabcdef123")
            j.append("request.accepted",request_id="test-01",
                     prompt_ref=j.ref("confidential customer sales report"),
                     workspace=j.ref("customer-business"),status="accepted")
            j.append("evidence.retrieved",request_id="test-01",
                     source_count=2,sources=[j.ref("file/a"),j.ref("file/b")],
                     retrieval="bm25")
            j.append("verification.completed",request_id="test-01",
                     claim_count=3,verifier_status="needs_review",
                     invalid_citations=[],numeric_warnings=["usd"])
            summary=verify_journal(j.path)
            self.assertEqual(summary["records"],3)
            self.assertEqual(j.verify()[0],3)
            self.assertEqual(Path(j.path).stat().st_mode & 0o777,0o600)
            self.assertEqual(j.secret_path.stat().st_mode & 0o777,0o600)
            contents=j.path.read_text()
            self.assertNotIn("confidential customer sales report",contents)
            self.assertNotIn("customer-business",contents)
            self.assertNotIn("file/a",contents)
            self.assertNotIn("file/b",contents)
            reopened=EvidenceJournal(base,release="testafterrestart")
            self.assertEqual(reopened.sequence,3)
            reopened.append("response.completed",request_id="test-01",result="answered")
            self.assertEqual(verify_journal(j.path)["records"],4)

    def test_rejects_raw_private_data_metadata(self):
        with tempfile.TemporaryDirectory() as base:
            j=EvidenceJournal(base)
            for field,value in (("question","what is our customer margin"),
                                ("body","Private answer"),("password","secret")):
                with self.subTest(field=field),self.assertRaises(ValueError):
                    j.append("request.accepted",**{field:value})
            self.assertFalse(j.path.exists())

    def test_tampering_detected_before_append_or_restart(self):
        with tempfile.TemporaryDirectory() as base:
            j=EvidenceJournal(base)
            j.append("request.accepted",request_id="A")
            j.append("response.completed",request_id="A",result="answered")
            rows=j.path.read_text().splitlines()
            damaged=json.loads(rows[0])
            damaged["request_id"]="B"
            rows[0]=json.dumps(damaged)
            j.path.write_text("\n".join(rows)+"\n")
            with self.assertRaises(ValueError):
                verify_journal(j.path)
            with self.assertRaises(ValueError):
                EvidenceJournal(base)

    def test_broken_line_sequence_detected(self):
        with tempfile.TemporaryDirectory() as base:
            j=EvidenceJournal(base)
            j.append("request.accepted",request_id="A")
            j.append("response.completed",request_id="A")
            j.path.write_text(j.path.read_text().splitlines()[1]+"\n")
            with self.assertRaises(ValueError):
                verify_journal(j.path)


class EvidenceVerifierTests(unittest.TestCase):
    def setUp(self):
        self.sources=[
            {"n":1,"id":41,"title":"Q3 billing","rel":"bill.md",
             "chunk":"Q3 billed $1,284,000 and collected $1,027,000 (80%)."},
            {"n":2,"id":42,"title":"Sales","rel":"sales.md",
             "chunk":"Evergreen Mechanical earned $872,000 on total revenue $4,860,000."},
        ]

    def test_citation_number_validity_not_semantic_truth(self):
        r=check_answer("Our sales were excellent [1].",self.sources)
        self.assertFalse(r["hard_fail"])
        self.assertFalse(r["fully_fact_verified"])
        self.assertEqual(r["status"],"needs_review")

    def test_invalid_citation_hard_fail(self):
        r=check_answer("The company earned $50 [9].",self.sources)
        self.assertTrue(r["hard_fail"])
        self.assertEqual(r["invalid_citations"],[9])

    def test_unsupported_numeric_marked_for_review(self):
        r=check_answer("The made-up estimate is $45,000 [1].",self.sources)
        self.assertIn("usd",r["numeric_warnings"])
        self.assertFalse(r["fully_fact_verified"])

    def test_source_anchored_calculator_supports_unseen_businesses(self):
        inputs={
            "earned":Quantity(Decimal("872000"),42,"$872,000","usd"),
            "total":Quantity(Decimal("4860000"),42,"$4,860,000","usd"),
        }
        result=checked_calculation("(earned / total) * 100",inputs,self.sources,"percent")
        self.assertEqual(result["value"],"17.94238683127572016460905350")
        self.assertEqual(result["source_ids"],[42,42])
        self.assertTrue(result["verified_kind"]=="recomputed_from_source_values")
        self.assertFalse(result["causality_proven"])

    def test_calculator_refuses_invented_values_and_other_tenant_refs(self):
        for inputs in [
            {"amount":Quantity(Decimal("999"),41,"$999","usd")},
            {"amount":Quantity(Decimal("1284000"),43,"$1,284,000","usd")},
            {"amount":Quantity(Decimal("1284000"),41,"$1,284,000 made up","usd")},
        ]:
            with self.assertRaises(ValueError):
                checked_calculation("amount * 2",inputs,self.sources,"usd")

    def test_calculator_rejects_python_execution(self):
        inp={"a":Quantity(Decimal("872000"),42,"$872,000","usd")}
        for expression in (
            "__import__('os').system('echo bad')",
            "a ** 30", "a / 0", "unknown + a",
            "a[0]", "(lambda: a)()", "a * 1.5",
        ):
            with self.subTest(expression=expression),self.assertRaises(
                (ValueError,ZeroDivisionError,TypeError)):
                checked_calculation(expression,inp,self.sources)

    def test_no_source_citation_not_fabricated_pass(self):
        r=check_answer("The revenue is definitely $8 million.",self.sources)
        self.assertFalse(r["fully_fact_verified"])
        self.assertTrue(r["numeric_warnings"])
        self.assertEqual(r["status"],"needs_review")


if __name__=="__main__":
    unittest.main()
