"""Regression tests for the Nov 7 local inference route mixup."""
import os
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import server


class RouteRegression(unittest.TestCase):
    def test_explicit_endpoint_is_only_discovery_candidate(self):
        with patch.object(server, 'LLM_URL', 'http://127.0.0.1:8097/v1'):
            m = server.Model()
            self.assertFalse(m.detect())
            self.assertFalse(m.online)
            self.assertNotEqual(m.url, 'http://127.0.0.1:8092/v1')

    def test_wrong_model_on_live_smart_stack_is_rejected(self):
        with patch.object(server, 'LLM_URL', 'http://127.0.0.1:8092/v1'), patch.object(server,'LLM_MODEL','/home/patrick/models/Qwen3.8-27B-Q4_K_M.gguf'):
            m = server.Model()
            self.assertFalse(m.detect())
            self.assertFalse(m.online)

    def test_cloud_is_hermes_codex_and_tool_free(self):
        from subprocess import CompletedProcess
        with patch.object(server.subprocess, 'run', return_value=CompletedProcess([], 0, 'OK\n', '')) as call:
            self.assertEqual(server.cloud_reply([{'role': 'user', 'content': 'hello'}]), 'OK')
            args = call.call_args.args[0]
            self.assertIn('gpt-5.6-sol', args)
            self.assertIn('openai-codex', args)
            self.assertIn('--safe-mode', args)

if __name__ == '__main__':
    unittest.main()
