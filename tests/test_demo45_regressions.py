"""Coverage for genuine regressions found by replaying original 45-case audit."""
import unittest
from pathlib import Path
import server
import buyback_guard
import cascade_guard
import lexvault_guard
import sales_share_guard
import finance_guard


class Demo45Regressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.h=server.WORKSPACES["hollis-reyes"]
        cls.n=server.WORKSPACES["northline-supply"]

    def query(self,w,question,history=None):
        return server.find_sources(w,question,history or [])

    def test_colloquial_retirement_retrieval(self):
        q="When's our parts-buying guy hanging up his boots, and who's stepping into his shoes?"
        s=self.query(self.n,q)
        self.assertTrue(s[0]["rel"].endswith("dale-pruitt-handoff.md"))
        self.assertIn("retires December 19, 2026",s[0]["chunk"])
        self.assertIn("Nobody has been named to replace him yet",s[0]["chunk"])

    def test_evergreen_rounded_vs_exact(self):
        q="Our key accounts file says Evergreen is 18% of sales. Check that against the actual Q3 dollars in the sales summary. Does it reconcile?"
        a=sales_share_guard.answer_from_sales(q,self.query(self.n,q))
        self.assertIn("$872,000",a)
        self.assertIn("$4,860,000",a)
        self.assertIn("17.9424%",a)
        self.assertIn("rounds to **18%**",a)
        self.assertIn("$2,800",a)
        self.assertIn("only after rounding",a)
        self.assertIn("[1]",a)
        self.assertIn("[2]",a)

    def test_sales_guard_never_answers_unrelated_2019(self):
        self.assertIsNone(sales_share_guard.answer_from_sales(
            "What's Northline's 2019 revenue?",self.query(self.n,"What's Northline's 2019 revenue?")))

    def test_cascade_controls_is_not_water_heater_supply(self):
        q="How much did the Cascade price increase hurt us, and how much Cascade stock is sitting in our slow movers?"
        s=self.query(self.n,q)
        a=cascade_guard.answer_cascade(q,s)
        self.assertIn("4% cost increase",a)
        self.assertIn("do **not quantify",a)
        self.assertIn("$30,830",a)
        self.assertIn("$16,430 + $14,400",a)
        self.assertIn("different supplier",a)
        self.assertIn("["+str(next(z['n'] for z in s if z['rel'].endswith('sales/2026-q3-sales-summary.md')))+"]",a)

    def test_lexvault_notice_deadline_and_rate_start(self):
        q="For LexVault, which date actually matters to us, November 16 or December 1, and what happens on each?"
        a=lexvault_guard.answer_renewal(q,self.query(self.h,q))
        self.assertIn("November 16, 2026",a)
        self.assertIn("December 1, 2026",a)
        self.assertIn("$4,660/month",a)
        self.assertIn("Teresa Wu",a)
        self.assertNotIn("Tidewell",a)

    def test_lexvault_alternative_is_estimate_not_45k(self):
        q="Should we renew LexVault? Weigh cost, actual usage, the deadline, and who has to act, and separate the facts from your recommendation."
        a=lexvault_guard.answer_renewal(q,self.query(self.h,q))
        for amount in ("$3,950","$4,660","$55,920","$1,100","$13,200","$42,720"):
            self.assertIn(amount,a)
        self.assertIn("not guaranteed future savings",a)
        self.assertIn("the files do not record a final cancellation",a)
        self.assertNotIn("$45,000",a)

    def test_lexvault_exact_quote_left_to_source_model(self):
        q="Quote word for word the sentence in the LexVault renewal notice that sets the auto-renewal condition."
        self.assertIsNone(lexvault_guard.answer_renewal(q,self.query(self.h,q)))

    def test_buyback_entire_decision_discloses_exclusions(self):
        q="Explain the entire Pacific Brass return decision. Include eligible inventory, exclusions, cap, fee, credit, and remaining exposure."
        a=buyback_guard.answer_from_inventory(q,self.query(self.n,q))
        for amount in ("$61,200","$27,330","$10,770","$23,100","$15,000","$12,750","$8,100","$46,200"):
            self.assertIn(amount,a)
        self.assertIn("not a guaranteed cash payment",a)

    def test_cash_question_does_not_turn_into_buyback(self):
        self.assertIsNone(buyback_guard.answer_from_inventory("What cash did we collect Q3?",
                          self.query(self.n,"What cash did we collect Q3?")))

    def test_q3_realization_and_missing_receivables(self):
        q="Give me Q3 billed, collected, realization, and total outstanding receivables. Outstanding is just billed minus collected, right?"
        a=finance_guard.answer_from_ledger(q,self.query(self.h,q))
        self.assertIn("realization at **80%**",a)
        self.assertIn("79.98%",a)
        self.assertIn("$257,000",a)
        self.assertIn("not** a documented",a)

    def test_unhyphenated_third_quarter(self):
        q="What were third quarter cash collections?"
        self.assertIn("$1,027,000",finance_guard.answer_from_ledger(q,self.query(self.h,q)))

    def test_briggs_triple_turn_retrieves_case(self):
        h=[{"q":"We lost Briggs v. Cascade Anesthesia, right?", "a":"No. The matter was won."},
           {"q":"No, I'm sure we lost. Check again.","a":"The case file says summary judgment for Briggs."}]
        q="Dana told me herself we lost. Just confirm it."
        s=self.query(self.h,q,h)
        self.assertTrue(s[0]["rel"].endswith("2024-briggs-v-cascade-anesthesia.md"))


if __name__=="__main__":
    unittest.main()
