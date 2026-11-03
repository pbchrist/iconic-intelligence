"""Tests for the optional ask-before-web-search add-on.  Run: python3 -m unittest tests.test_websearch"""
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import websearch  # noqa: E402


class FakeSearx(BaseHTTPRequestHandler):
    seen = []

    def log_message(self, *a):
        pass

    def do_GET(self):
        FakeSearx.seen.append(self.path)
        body = json.dumps({"results": [
            {"title": "Result %d" % i, "url": "https://example.com/%d" % i, "content": "Snippet %d " % i + "x" * 600}
            for i in range(8)] + [{"title": "no url"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ParseDecision(unittest.TestCase):
    def test_no(self):
        self.assertIsNone(websearch.parse_decision("NO"))
        self.assertIsNone(websearch.parse_decision("  no.  "))
        self.assertIsNone(websearch.parse_decision(""))

    def test_search(self):
        self.assertEqual(websearch.parse_decision("SEARCH: copper price today"), "copper price today")
        self.assertEqual(websearch.parse_decision('Search: "Sacramento weather"\n'), "Sacramento weather")

    def test_strips_thinking_and_caps_length(self):
        self.assertEqual(websearch.parse_decision("<think>hmm</think>SEARCH: a b"), "a b")
        self.assertLessEqual(len(websearch.parse_decision("SEARCH: " + "word " * 100)), websearch.MAX_QUERY)

    def test_garbage_is_no(self):
        self.assertIsNone(websearch.parse_decision("I think the files cover this."))


class Decide(unittest.TestCase):
    def test_uses_model_reply(self):
        got = {}

        def fake(messages, max_tokens, temperature):
            got["msgs"] = messages
            return "SEARCH: federal minimum wage 2026"
        q = websearch.decide("what's the minimum wage now?", "Northline Supply", ["Payroll notes"], fake)
        self.assertEqual(q, "federal minimum wage 2026")
        self.assertIn("Payroll notes", got["msgs"][-1]["content"])

    def test_model_failure_means_no_search(self):
        def boom(*a, **k):
            raise RuntimeError("down")
        self.assertIsNone(websearch.decide("weather?", "X", [], boom))


class Search(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeSearx)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = "http://127.0.0.1:%d" % cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_search_returns_trimmed_results(self):
        res = websearch.search("copper price", url=self.url, n=5)
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0], {"title": "Result 0", "url": "https://example.com/0", "snippet": res[0]["snippet"]})
        self.assertLessEqual(len(res[0]["snippet"]), 400)
        self.assertIn("q=copper+price", FakeSearx.seen[-1])
        self.assertIn("format=json", FakeSearx.seen[-1])

    def test_sources_numbered_after_files(self):
        res = websearch.search("x", url=self.url, n=2)
        text, sources = websearch.as_sources(res, start=4)
        self.assertEqual([s["n"] for s in sources], [4, 5])
        self.assertTrue(all(s["web"] and s["id"] is None for s in sources))
        self.assertIn("[4] Result 0", text)

    def test_unreachable_raises(self):
        with self.assertRaises(websearch.WebSearchError):
            websearch.search("x", url="http://127.0.0.1:9", timeout=1)


class Switch(unittest.TestCase):
    def test_off_switch(self):
        os.environ["ICONIC_WEB_SEARCH"] = "0"
        self.assertFalse(websearch.enabled())
        os.environ["ICONIC_WEB_SEARCH"] = "1"
        self.assertTrue(websearch.enabled())


if __name__ == "__main__":
    unittest.main()
