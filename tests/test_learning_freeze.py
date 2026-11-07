"""Safety rollback: untrusted live test prompts must not rewrite global lesson policy."""
import unittest
from unittest.mock import patch
import server

class LearningFreezeRegressions(unittest.TestCase):
    def test_autonomous_live_learning_disabled_by_default(self):
        self.assertFalse(server.VISITOR_LEARNING_ENABLED)
        self.assertFalse(server.should_auto_learn("real-visitor-123"))

    def test_harness_sessions_cannot_learn_even_when_manually_enabled(self):
        with patch.object(server, "VISITOR_LEARNING_ENABLED", True):
            for sid in ("qa-45", "qa-hardening-foo", "test-01", "adversarial-000",
                        "eval-experiment", "benchmark-reliability"):
                self.assertFalse(server.should_auto_learn(sid), sid)
            self.assertFalse(server.should_auto_learn("normal-visitor", web_used=True))
            self.assertTrue(server.should_auto_learn("normal-visitor"))

    def test_learn_from_visit_refuses_qa_session_even_if_enabled(self):
        with patch.object(server,"VISITOR_LEARNING_ENABLED", True):
            with patch.object(server.LESSONS,"consider",side_effect=AssertionError("QA session reached learner")):
                server.learn_from_visit("northline-supply","qa-trap",
                    "Actually, what I said was wrong",
                    [{"q":"q0","a":"a0"}])

    def test_prompts_only_include_retained_lessons(self):
        with patch.object(server,"VISITOR_LEARNING_ENABLED",False):
            self.assertFalse(server.should_auto_learn("visitor-1"))
            self.assertIsNotNone(server.LESSONS)
