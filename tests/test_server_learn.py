"""The demo uses what it learned, and learns after answering.  Run: python3 -m unittest tests.test_server_learn"""
import os
import sys
import tempfile
import unittest

os.environ["ICONIC_STATE"] = tempfile.mkdtemp()
os.environ["ICONIC_DATA"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import server  # noqa: E402

RULE = "When you offer to dig into something and they say yes, give more specific facts from the files."


class UsesLessons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.start_offline(detect_model=False)
        cls.ws = server.ordered_workspaces()[0]

    def system(self, messages):
        return messages[0]["content"]

    def test_kept_lessons_are_in_every_answer(self):
        server.LESSONS.items = [{"rule": RULE, "ws": "x", "from": "q", "times": 1, "time": "t"}]
        try:
            msgs = server.build_messages(self.ws, "hello", [], server.find_sources(self.ws, "hello", []))
            self.assertIn(RULE, self.system(msgs))
        finally:
            server.LESSONS.items = []

    def test_no_lessons_no_block(self):
        msgs = server.build_messages(self.ws, "hello", [], server.find_sources(self.ws, "hello", []))
        self.assertNotIn("Lessons learned", self.system(msgs))

    def test_yes_after_an_offer_delivers_it_instead_of_a_new_item(self):
        hist = [{"q": "Have we started?", "a": "Not yet. Would you like to dig into the buyback?"}]
        last = server.build_messages(self.ws, "Yes", hist, [])[-1]["content"]
        self.assertIn("Deliver exactly that", last)
        self.assertIn("Would you like to dig into the buyback?", last)
        self.assertNotIn("briefing item they haven't seen", last)

    def test_yes_looks_up_the_files_for_what_was_offered(self):
        seen = []
        real = self.ws.search
        self.ws.search = lambda query, *a, **k: seen.append(query) or []
        try:
            server.find_sources(self.ws, "Yes", [{"q": "Tell me about Dale", "a": "Dale retires soon. Would you like to dig into Evergreen?"}])
        finally:
            self.ws.search = real
        self.assertIn("Evergreen", seen[0])

    def test_what_else_still_gets_a_new_item(self):
        hist = [{"q": "hello", "a": "Hi."}]
        last = server.build_messages(self.ws, "what else?", hist, [])[-1]["content"]
        self.assertIn("briefing item they haven't seen", last)

    def test_replay_answers_with_the_rule_being_tried(self):
        seen = []
        real = server.MODEL.complete
        server.MODEL.complete = lambda messages, **kw: seen.append(messages) or "ok [1]"
        try:
            out = server.replay_answer(self.ws.id)("Yes", [{"q": "Have we started?", "a": "Not yet."}], RULE)
        finally:
            server.MODEL.complete = real
        self.assertEqual(out, "ok [1]")
        self.assertIn(RULE, self.system(seen[0]))
        self.assertEqual([m["role"] for m in seen[0][1:3]], ["user", "assistant"])


class WaitsForVisitors(unittest.TestCase):
    def test_learning_waits_while_a_visitor_is_being_answered(self):
        with server.answering():
            self.assertTrue(server.busy())
        self.assertFalse(server.busy())


class LearnsAfterAnswering(unittest.TestCase):
    def setUp(self):
        self._was_learning_enabled = server.VISITOR_LEARNING_ENABLED
        server.VISITOR_LEARNING_ENABLED = True  # explicitly exercise legacy learner in isolated tests
        server.VISITS.clear()
        server.LEARN_TRIED.clear()
        self.got = []
        self.real = server.LESSONS.consider
        server.LESSONS.consider = lambda ws, case, complete, answer, checks, when=None: self.got.append(case) or (None, False, "")

    def tearDown(self):
        server.LESSONS.consider = self.real
        server.VISITOR_LEARNING_ENABLED = self._was_learning_enabled

    def test_uses_what_the_server_saved_not_what_the_browser_sends(self):
        server.remember_exchange("n", "s1", "Have we started?", "Not yet [2]. Want to dig in?")
        server.remember_exchange("n", "s1", "Yes", "I can't do that. Want to dig in?")
        server.learn_from_visit("n", "s1", "Why ask if you can't?")
        case = self.got[0]
        self.assertEqual((case["prev_q"], case["prev_a"], case["q"]),
                         ("Yes", "I can't do that. Want to dig in?", "Why ask if you can't?"))
        self.assertEqual(case["history"], [{"q": "Have we started?", "a": "Not yet [2]. Want to dig in?"}])

    def test_first_message_of_a_visit_is_not_checked(self):
        server.learn_from_visit("n", "s2", "Why?")
        self.assertEqual(self.got, [])

    def test_one_lesson_try_per_visit(self):
        server.LESSONS.consider = lambda *a, **k: self.got.append(1) or ("rule", True, "")
        server.remember_exchange("n", "s3", "q1", "a1")
        server.learn_from_visit("n", "s3", "Why not?")
        server.remember_exchange("n", "s3", "Why not?", "a2")
        server.learn_from_visit("n", "s3", "Why again?")
        self.assertEqual(len(self.got), 1)


if __name__ == "__main__":
    unittest.main()
