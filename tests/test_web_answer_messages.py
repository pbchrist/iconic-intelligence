"""After the visitor says yes to a web search, the answer must build. Run: python3 -m unittest tests.test_web_answer_messages"""
import os
import sys
import tempfile
import unittest

os.environ["ICONIC_STATE"] = tempfile.mkdtemp()
os.environ["ICONIC_DATA"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import server  # noqa: E402
import websearch  # noqa: E402

RESULTS = [{"title": "Seattle weather today", "url": "https://weather.example/seattle",
            "snippet": "Rain, high of 52F on Tuesday November 10 2026."}]


class WebAnswerBuilds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.ws = server.ordered_workspaces()[0]

    def test_web_results_mixed_with_file_sources_build_messages(self):
        q = "What is the weather in Seattle today?"
        sources = server.find_sources(self.ws, q, [])[:2]
        wtext, wsrc = websearch.as_sources(RESULTS, len(sources) + 1)
        msgs = server.build_messages(self.ws, q, [], sources + wsrc,
                                     "Web results:\n\n" + wtext, {"query": q, "results": 1, "error": ""})
        everything = "\n".join(m["content"] for m in msgs)
        self.assertIn("high of 52F", everything)          # the web result reaches the model
        self.assertIn("weather.example", everything)


if __name__ == "__main__":
    unittest.main()
