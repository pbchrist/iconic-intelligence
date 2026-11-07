"""Release guards for the reported 45-case failures and conversation behavior."""
import unittest
from pathlib import Path

import finance_guard
import server

ROOT = Path(__file__).resolve().parents[1]


class FinancialEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.ws = server.WORKSPACES["hollis-reyes"]

    def grounded(self, question, history=None):
        sources = server.find_sources(self.ws, question, history or [])
        return finance_guard.answer_from_ledger(question, sources, history or []), sources

    def test_q3_totals_recover_from_real_source(self):
        answer, sources = self.grounded("What were our Q3 2026 billings and collections?")
        self.assertIn("$1,284,000", answer)
        self.assertIn("$1,027,000", answer)
        self.assertIn("79.98%", answer)
        self.assertIn("2026-q3-billing-report.md", sources[0]["rel"])
        self.assertIn("[1]", answer)

    def test_q3_percent_exact_and_derived(self):
        answer, sources = self.grounded("What percentage of Q3 billings did we collect? Show the math.")
        self.assertIn("79.98%", answer)
        self.assertIn("1,027,000 collected", answer)
        self.assertIn("1,284,000 billed", answer)
        self.assertNotIn("0.800623", answer)

    def test_invented_receivables_total_is_rejected(self):
        answer, _ = self.grounded("So the $257,000 gap is our outstanding A/R?")
        self.assertIn("$257,000", answer)
        self.assertIn("not** a documented accounts-receivable total", answer)
        self.assertIn("aged receivables ledger", answer)

    def test_cash_collected_paraphrase(self):
        answer, _ = self.grounded("How much cash did we collect in Q3?")
        self.assertIn("$1,027,000 collected", answer)

    def test_unsupported_other_period_not_overridden(self):
        answer, _ = self.grounded("What was the Q1 2026 collection rate?")
        self.assertIsNone(answer)

    def test_specific_client_balance_not_replaced_with_firm_wide(self):
        answer, _ = self.grounded("What's the exact outstanding balance for Tidewell?")
        self.assertIsNone(answer)

    def test_hyphenated_cash_collections_paraphrase(self):
        answer, sources = self.grounded("What were third-quarter cash collections?")
        self.assertIn("$1,027,000 collected", answer)
        self.assertTrue(sources[0]["rel"].endswith("2026-q3-billing-report.md"))

    def test_reminder_corrects_wrong_owner(self):
        import deadline_guard
        q = "Draft a two-line reminder to Marco that his Kessler response to Graves Whitlock is due November 12."
        sources = server.find_sources(self.ws, q, [])
        answer = deadline_guard.draft_from_deadline(q, sources)
        self.assertIn("Dana Hollis", answer)
        self.assertIn("not Marco", answer)
        self.assertIn("November 12", answer)
        self.assertIn("operations/2026-11-deadlines.md", sources[0]["rel"])

    def test_buyback_credit_cap_eligible_excess_and_cash(self):
        import buyback_guard
        question = "How much unopened Pacific Brass stock qualifies, the return cap, remaining stock and net credit?"
        w = server.WORKSPACES["northline-supply"]
        sources = server.find_sources(w, question, [])
        result = buyback_guard.answer_from_inventory(question, sources)
        for amount in ("$23,100", "$15,000", "$12,750", "$8,100"):
            self.assertIn(amount, result)
        self.assertIn("not a guaranteed cash payment", result)
        self.assertIn("before December 31", result)

    def test_buyback_guard_rejects_inconsistent_source(self):
        import buyback_guard
        fake = "$23,100 of unopened Pacific Brass valves that qualify, but Pacific Brass caps the buyback at $15,000. At a 15% restocking fee, the return comes back as a $13,000 credit. The other $8,100 of eligible stock."
        self.assertIsNone(buyback_guard.parse_evidence(fake))

    def test_unique_citation_numbers_per_source_document(self):
        w = server.WORKSPACES["northline-supply"]
        sources = server.find_sources(w, "How much Pacific Brass stock qualifies for buyback and net credit?", [])
        self.assertEqual(len({x["rel"] for x in sources}), len(sources))
        self.assertEqual([x["n"] for x in sources], list(range(1, len(sources)+1)))

    def test_missing_billing_document_never_generates_money(self):
        self.assertIsNone(finance_guard.answer_from_ledger(
            "What was Q3 collected?", [{"n": 1, "chunk": "No billing report available."}]))

    def test_qa_source_citations_are_real(self):
        answer, src = self.grounded("How much did we bill and collect Q3 2026?")
        number = int(answer.split("[")[1].split("]")[0])
        chosen = next(x for x in src if x["n"] == number)
        self.assertIn("$1,284,000", chosen["chunk"])
        self.assertIn("$1,027,000", chosen["chunk"])


class PromptAndRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.ws = server.WORKSPACES["hollis-reyes"]

    def test_first_message_never_forces_briefing(self):
        messages = server.build_messages(self.ws, "Write a poem about cats", [],
                                         server.find_sources(self.ws, "Write a poem about cats", []))
        self.assertNotIn("Today's briefing", messages[0]["content"])
        self.assertIn("No unsolicited briefing", messages[-1]["content"])
        self.assertIn("harmless creative requests", messages[0]["content"])

    def test_never_auto_agree_with_false_accounting_premise(self):
        self.assertIn("does NOT by itself establish outstanding accounts receivable",
                      server.SYSTEM_PROMPT)
        self.assertIn("A factual dispute means verify, not capitulate",
                      server.SYSTEM_PROMPT)

    def test_targeted_source_retrieval_does_not_pad_recent_files(self):
        w = server.WORKSPACES["hollis-reyes"]
        original = w.search
        try:
            one = original("What did Briggs v Cascade resolve?")
            self.assertTrue(one)
            w.search = lambda q: one[:1]
            found = server.find_sources(w, "What did Briggs v Cascade resolve?", [])
        finally:
            w.search = original
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["rel"], next(d["rel"] for d in w.docs if d["id"] == one[0][1]["doc"]))

    def test_switcher_has_session_persistence_and_stale_response_guards(self):
        js = (ROOT / "static/app.js").read_text(encoding="utf-8")
        self.assertIn("IconicChatState.save(sessionStorage", js)
        self.assertIn("restoreChat(S.ws)", js)
        self.assertIn("if (requested !== S.ws) return", js)
        self.assertIn("Never erase it", js)
        self.assertIn('<script src="chat-state.js"></script>',
                      (ROOT / "static/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
