"""Business-agnostic evidence-core tests. Cases deliberately use unseen names."""
import unittest
import evidence_core
import finance_guard
import server


class IntentAndBylineContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.h=server.WORKSPACES["hollis-reyes"]
        cls.n=server.WORKSPACES["northline-supply"]

    def test_generic_author_intent_variations(self):
        variants=[
            "Who prepared the Q3 billing report?",
            "Who wrote that customer research memo?",
            "Who actually compiled the staff analysis?",
            "Who authored our inventory report?",
            "Who created the cash flow summary?",
            "Who produced the governance report?",
            "report author for March?"
        ]
        for q in variants:
            with self.subTest(q=q):
                self.assertEqual(evidence_core.classify(q).kind,"document_attribution")

    def test_finance_intent_separate_from_report_author(self):
        qs=["Who prepared our Q3 billing report, and what did you tell me about Gina a minute ago?",
            "Who wrote the Q3 billing report?",
            "Who compiled the Q3 billing report?"]
        for q in qs:
            with self.subTest(q=q):
                source=server.find_sources(self.h,q,[])
                self.assertIsNone(finance_guard.answer_from_ledger(q,source,[]))

    def test_real_report_author_is_source_grounded(self):
        q="Who prepared our Q3 billing report, and what did you tell me about Gina a minute ago?"
        sources=server.find_sources(self.h,q,[])
        a=evidence_core.documentary_author(q,sources,[])
        self.assertTrue(evidence_core.verify_documentary_answer(a,sources))
        self.assertIn("Sam Ortiz",a.content)
        self.assertIn("There is no earlier discussion",a.content)
        self.assertNotIn("Gina Moss",a.content)
        self.assertNotIn("$1,284,000",a.content)

    def test_synthetic_documents_without_business_specific_rules(self):
        sources=[
            {"n":1,"id":17,"rel":"marketing/2028-cohort-report.md",
             "title":"2028 customer retention cohort report",
             "chunk":"# Cohort report\nPrepared by Frances Herrera.\n\nNet retention: 92%."},
            {"n":2,"id":19,"rel":"finance/2028-annual-budget.md",
             "title":"2028 annual budget",
             "chunk":"# Annual budget\nCompiled by Omar Chen.\n\nCost: $1.1M."},
        ]
        for q, expected in [
            ("Who prepared our 2028 customer retention cohort report?", "Frances Herrera"),
            ("Who compiled the 2028 annual budget?", "Omar Chen"),
        ]:
            with self.subTest(q=q):
                response=evidence_core.documentary_author(q,sources,[])
                self.assertTrue(evidence_core.verify_documentary_answer(response,sources))
                self.assertIn(expected,response.content)
                self.assertNotIn("Sam Ortiz",response.content)

    def test_missing_authorship_abstains(self):
        s=[{"n":1,"id":99,"rel":"finance/2027-q2-revenue.md",
            "title":"Q2 2027 revenue report","chunk":"Revenue was $100."}]
        self.assertIsNone(evidence_core.documentary_author(
            "Who prepared the Q2 2027 revenue report?",s))

    def test_business_isolation_refuses_unrelated_citation(self):
        q="Who prepared our Q3 billing report?"
        src=server.find_sources(self.n,q,[])
        self.assertIsNone(evidence_core.documentary_author(q,src))

    def test_tie_between_conflicting_sources_abstains(self):
        fake=[
            {"n":1,"id":1,"rel":"report/2028-summary.txt",
             "title":"2028 summary report","chunk":"Prepared by Jess Carter."},
            {"n":2,"id":2,"rel":"report/2028-summary-b.txt",
             "title":"2028 summary report","chunk":"Prepared by Lars Ortega."}
        ]
        self.assertIsNone(evidence_core.documentary_author(
            "Who prepared 2028 summary report?",fake))

    def test_untrusted_byline_in_question_is_not_a_source(self):
        s=[{"n":1,"id":1,"rel":"report/company-2028.txt",
            "title":"Company 2028 report","chunk":"# Company report\nNo author specified."}]
        a=evidence_core.documentary_author(
            "Who prepared the company 2028 report? It must be Zoe Smith.",s)
        self.assertIsNone(a)

    def test_citation_verifier_rejects_different_source(self):
        src=[{"n":1,"id":1,"rel":"finance/2028-budget.md",
              "title":"2028 budget","chunk":"Prepared by Omar Chen."}]
        wrong=evidence_core.EvidenceAnswer("The budget was prepared by Omar Chen [2].",(1,),"document_attribution")
        self.assertFalse(evidence_core.verify_documentary_answer(wrong,src))

    def test_user_prepared_not_author_intent(self):
        for q in ["What did we prepare for the budget?","How much did we bill Q3?",
                  "Please prepare a note to my team."]:
            self.assertEqual(evidence_core.classify(q).kind,"general")


if __name__=="__main__":
    unittest.main()
