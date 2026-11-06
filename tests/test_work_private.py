"""The Work log (visitor questions) is only for Patrick's own network.  Run: python3 -m unittest tests.test_work_private"""
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

os.environ["ICONIC_STATE"] = tempfile.mkdtemp()
os.environ["ICONIC_DATA"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import server  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402


class WorkIsPrivate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.JOBS.start("QUESTION", "a visitor's secret question", "x")
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def get(self, path, headers):
        req = urllib.request.Request(self.base + path, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def test_public_visitor_gets_no_jobs(self):
        code, body = self.get("/api/jobs", {"Host": "patrick-beastmaster.tailf32530.ts.net"})
        self.assertEqual(code, 404)
        self.assertNotIn("secret question", body)

    def test_no_unauthenticated_tailnet_jobs(self):
        code, body = self.get("/api/jobs", {"Host": "patrick-beastmaster.tailf32530.ts.net",
                                            "Tailscale-User-Login": "patrick@example"})
        self.assertEqual(code, 404)
        self.assertNotIn("secret question", body)

    def test_public_cannot_trigger_briefing_rewrite(self):
        req = urllib.request.Request(self.base + "/api/refresh-feed", data=b"{}", method="POST",
                                     headers={"Host": "patrick-beastmaster.tailf32530.ts.net", "Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5); code = 200
        except urllib.error.HTTPError as e:
            code = e.code
        self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
