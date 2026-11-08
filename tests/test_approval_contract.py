"""General decision-status evidence tests, including held-out fake operations.

No sample company-specific names or financial constants are in production code.
"""
import unittest
import approval_contract as a
import dialogue_contract
import server


class ApprovalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.workspace=server.WORKSPACES["northline-supply"]

    def test_real_loader_shift_is_pending_not_approved(self):
        question=("Has the 6 a.m. Tuesday loader shift been approved? "
                  "Use the newest record and tell me if older files say something different.")
        sources=server.find_sources(self.workspace,question,[])
        result=a.extract_approval(question,sources)
        self.assertIsNotNone(result)
        self.assertTrue(a.verify_approval(result,sources))
        self.assertEqual(result.status,"pending")
        self.assertIn("No final approval",result.text)
        self.assertIn("to decide by November 7",result.text)
        self.assertIn("Not yet approved",result.text)
        self.assertNotIn("Yes, it has been approved",result.text)

    def test_generic_unseen_newer_approval_supersedes_old_pending(self):
        question="Has the Wednesday packaging shift been approved?"
        sources=[
            {"n":1,"id":55,"date":"2028-01-03","title":"Older operations",
             "rel":"operations/old.md",
             "chunk":"Wednesday packaging shift proposed. Director to decide by January 12."},
            {"n":2,"id":56,"date":"2028-01-14","title":"Newer operations",
             "rel":"operations/new.md",
             "chunk":"Wednesday packaging shift approved by the operations director."}
        ]
        result=a.extract_approval(question,sources)
        self.assertEqual(result.status,"approved")
        self.assertEqual(result.source_number,2)
        self.assertTrue(a.verify_approval(result,sources))

    def test_generic_unseen_newer_pending_overrides_older_proposal(self):
        question="Has the Saturday customer-call schedule been approved? Compare older files."
        sources=[
            {"n":1,"id":71,"date":"2028-03-01","title":"March",
             "rel":"meetings/march.md",
             "chunk":"Saturday customer-call schedule proposed; not yet approved."},
            {"n":2,"id":72,"date":"2028-04-05","title":"April",
             "rel":"meetings/april.md",
             "chunk":"Saturday customer-call schedule is feasible; manager will decide by April 30."},
        ]
        result=a.extract_approval(question,sources)
        self.assertEqual(result.status,"pending")
        self.assertTrue(a.verify_approval(result,sources))
        self.assertIn("not yet approved",result.text.lower())

    def test_same_day_conflicting_approval_abstains(self):
        question="Has the Wednesday packaging shift been approved?"
        sources=[
            {"n":1,"id":1,"date":"2028-06-04","title":"Status A","rel":"a.md",
             "chunk":"Wednesday packaging shift approved by directors."},
            {"n":2,"id":2,"date":"2028-06-04","title":"Status B","rel":"b.md",
             "chunk":"Wednesday packaging shift is not yet approved."}
        ]
        r=a.extract_approval(question,sources)
        self.assertEqual(r.status,"conflicting")
        self.assertFalse(r.verified)

    def test_unrelated_approval_does_not_count(self):
        question="Has the warehouse lighting proposal been approved?"
        sources=[{"n":1,"id":2,"date":"2028-07-04","title":"Operations",
                  "rel":"meeting.md",
                  "chunk":"Holiday bonus package approved by directors."}]
        r=a.extract_approval(question,sources)
        self.assertEqual(r.status,"unverified")
        self.assertFalse(r.verified)

    def test_broad_company_financial_risk_is_general_overview(self):
        for q in ("What's Northline's biggest immediate financial risk?",
                  "What is our biggest operational risk?",
                  "What's the company's top business concern?"):
            self.assertEqual(dialogue_contract.intent(q),"company_overview")
        self.assertNotEqual(dialogue_contract.intent(
            "What's the biggest risk with the Pacific Brass contract?"),
            "company_overview")
        sources=server.find_sources(self.workspace,
            "What's Northline's biggest immediate financial risk?",[])
        self.assertGreater(len(sources),0)
        self.assertTrue(any("slow-movers" in s["rel"] for s in sources))


if __name__=="__main__":
    unittest.main()
