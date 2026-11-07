"""Regression checks from the November 6 adversarial audit."""
import unittest
from unittest.mock import patch
import server


class SecurityRegressions(unittest.TestCase):
    def handler(self, headers=None, peer="127.0.0.1"):
        h = object.__new__(server.Handler)
        h.headers = headers or {}
        h.client_address = (peer, 12345)
        return h

    def test_forwarded_header_does_not_change_rate_limit_identity(self):
        h = self.handler({"X-Forwarded-For": "8.8.8.8"})
        self.assertEqual(h.client_ip(), "127.0.0.1")

    def test_public_status_hides_internal_model_endpoint_and_hostname(self):
        h = self.handler({"Host": "example.ts.net", "X-Forwarded-For": "8.8.8.8"})
        with patch.object(server.MODEL, "status", return_value={"online": True, "private": True, "endpoint": "127.0.0.1:8082"}):
            d = h.status()
        self.assertNotIn("endpoint", d["model"])
        self.assertEqual(d["host"], "private machine")

    def test_local_requests_are_public_without_authentication(self):
        self.assertTrue(self.handler().is_public())

    def test_recovery_routes_removed(self):
        import inspect
        src = inspect.getsource(server.Handler.do_GET)
        self.assertNotIn('u.path == "/api/conversations"', src)
        self.assertNotIn('u.path == "/api/recover-slots"', src)

    def test_funnel_sessions_get_separate_rate_limit_buckets(self):
        server.HITS.pop("session:test-u1", None)
        server.HITS.pop("session:test-u2", None)
        server.HITS.pop("ip:127.0.0.1", None)
        self.assertTrue(server.allowed("127.0.0.1", True, "test-u1"))
        self.assertTrue(server.allowed("127.0.0.1", True, "test-u2"))
        self.assertIn("session:test-u1", server.HITS)
        self.assertIn("session:test-u2", server.HITS)
        self.assertNotIn("ip:127.0.0.1", server.HITS)

    def test_refresh_has_limit(self):
        server.HITS.pop("refresh:test-refresh", None)
        self.assertTrue(server.allowed_refresh("test-refresh"))
        self.assertTrue(server.allowed_refresh("test-refresh"))
        self.assertFalse(server.allowed_refresh("test-refresh"))

    def test_billing_and_buyback_answering_instructions(self):
        s = server.SYSTEM_PROMPT
        self.assertIn("language of the visitor", s)
        self.assertIn("caps", s)
        self.assertIn("Cite the document", s)


if __name__ == "__main__":
    unittest.main()

class BillingRetrievalRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.w = server.WORKSPACES["hollis-reyes"]

    def test_english_billing_question_prioritizes_report(self):
        sources = server.find_sources(self.w, "How much did the firm bill in Q3?", [])
        self.assertTrue(sources[0]["rel"].endswith("2026-q3-billing-report.md"))

    def test_spanish_billing_question_prioritizes_same_report(self):
        sources = server.find_sources(self.w, "¿Cuánto facturó el despacho en el tercer trimestre?", [])
        self.assertTrue(sources[0]["rel"].endswith("2026-q3-billing-report.md"))

    def test_truthful_instruction_disclosure_refusal(self):
        self.assertIn("Never claim no instructions exist", server.SYSTEM_PROMPT)

class SourceGroundingRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)

    def test_evergreen_renewal_uses_key_accounts_document(self):
        w=server.WORKSPACES["northline-supply"]
        docs=server.find_sources(w,"Since we lost the Evergreen contract last month, what now? When does it renew?",[])
        self.assertTrue(any(s["rel"]=="customers/key-accounts.md" and "January 15, 2027" in s["chunk"] for s in docs))

    def test_buyback_caps_and_credit_are_in_retrieved_source(self):
        w=server.WORKSPACES["northline-supply"]
        docs=server.find_sources(w,"How much Pacific Brass stock qualifies for buyback, what is the return cap, and credit?",[])
        self.assertTrue(any("2026-10-slow-movers.md" in s["rel"] and all(x in s["chunk"] for x in ("$23,100","$15,000","$12,750")) for s in docs))
