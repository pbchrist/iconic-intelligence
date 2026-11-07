"""Approved, source-grounded external QA assertions; required by every deployment."""
import json
from pathlib import Path
import unittest
import server

ROOT = Path(__file__).resolve().parents[1]

class ApprovedQAAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)

    def test_approved_cases_use_documented_evidence_and_retrieve_it(self):
        cases = json.loads((ROOT / "qa/approved.json").read_text())["cases"]
        self.assertGreaterEqual(len(cases), 4)
        seen = set()
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                workspace = case["workspace"]
                w = server.WORKSPACES[workspace]
                file = (ROOT/"data"/workspace/case["source_rel"]).resolve()
                self.assertTrue(file.is_relative_to((ROOT/"data"/workspace).resolve()))
                text = file.read_text(encoding="utf-8")
                self.assertTrue(case["evidence"])
                for excerpt in case["evidence"]:
                    self.assertIn(excerpt, text, "The source no longer proves this test")
                matches = [s for s in server.find_sources(w, case["question"], [])
                           if s["rel"]==case["source_rel"] and
                           all(x in s["chunk"] for x in case["evidence"])]
                self.assertTrue(matches, "Relevant source missing or its qualifying passage not retrieved")
                if case.get("require_first"):
                    self.assertEqual(matches[0]["n"], 1)
