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


class SearchBestRanking(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self._search, self._page = websearch.search, websearch._page_text
        websearch._page_text = lambda url, terms, **k: ""

        def fake(query, url=None, n=5, timeout=8, extra=None):
            self.calls.append(extra or {})
            if extra:  # news pass: off-topic fresh stories
                return [{"title": "Spokane pho shop opens", "url": "https://n/%d" % i, "snippet": "pho"} for i in range(5)]
            return [{"title": "Dictionary: nacho", "url": "https://d", "snippet": "noun"},
                    {"title": "Best nachos in Seattle", "url": "https://g1", "snippet": "Seattle's top nachos"},
                    {"title": "Seattle nachos guide", "url": "https://g2", "snippet": "best nachos spots"}]
        websearch.search = fake

    def tearDown(self):
        websearch.search, websearch._page_text = self._search, self._page

    def test_evergreen_question_skips_news_and_ranks_matches_first(self):
        res = websearch.search_best("best nachos in Seattle")
        self.assertEqual(self.calls, [{}])
        self.assertEqual(res[0]["url"], "https://g1")
        self.assertNotIn("pho", " ".join(r["title"] for r in res).lower())

    def test_time_sensitive_question_also_gets_news(self):
        websearch.search_best("Seattle news today")
        self.assertEqual(len(self.calls), 2)


if __name__ == "__main__":
    unittest.main()


class LocalQuestionCues(unittest.TestCase):
    def test_local_place_questions_get_considered(self):
        for q in ("who has the best naachoes in seattle", "best tacos near me", "coffee nearby",
                  "who sells copper pipe in Tacoma"):
            self.assertTrue(websearch.likely_needs_web(q), q)

    def test_file_questions_still_skip(self):
        for q in ("What happens if we miss the November 12 Kessler deadline?",
                  "Summarize the Hollis engagement letter"):
            self.assertFalse(websearch.likely_needs_web(q), q)


if __name__ == "__main__":
    unittest.main()
