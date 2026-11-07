"""Real Git rollback simulation; all processes/data remain in disposable tempdirs."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import evidence_release_control as release


def git(*cmd,cwd):
    p=subprocess.run(["git",*cmd],cwd=cwd,capture_output=True,text=True,check=True)
    return p.stdout.strip()


class RollbackReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="iconic-evidence-rollback-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.repo=self.root/"repo"
        self.repo.mkdir()
        self.state=self.root/"state"
        self.state.mkdir()
        git("init","-b","dashboard",cwd=self.repo)
        git("config","user.name","Test",cwd=self.repo)
        git("config","user.email","test@example.invalid",cwd=self.repo)
        marker=self.repo/"server_marker.txt"
        marker.write_text("GOOD_MARKER")
        git("add",".",cwd=self.repo)
        git("commit","-m","good",cwd=self.repo)
        self.good=release.sha(self.repo)
        marker.write_text("BAD_MARKER")
        git("add",".",cwd=self.repo)
        git("commit","-m","candidate",cwd=self.repo)
        self.bad=release.sha(self.repo)
        self.mock=self.root/"systemctl"
        self.mock.write_text("#!/bin/sh\necho \"$@\" >> \""+str(self.root/"restarts.log")+"\"\nexit 0\n")
        self.mock.chmod(0o755)

        repo=self.repo
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                ok=(repo/"server_marker.txt").read_text()=="GOOD_MARKER"
                payload=json.dumps({"model":{"online":ok,"model":"test-qwen"}}).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self,*args):
                pass
        self.srv=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread=threading.Thread(target=self.srv.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.url="http://127.0.0.1:"+str(self.srv.server_address[1])+"/api/status"

    def invoke(self,expected=None,target=None,apply=False):
        return release.rollback(self.repo,self.state,
                                expected or self.bad,target or self.good,
                                self.url,"iconic-command",str(self.mock),apply)

    def test_dry_run_does_not_modify_repo_or_service(self):
        plan=self.invoke(apply=False)
        self.assertEqual(plan["to_sha"],self.good)
        self.assertEqual(release.sha(self.repo),self.bad)
        self.assertFalse((self.root/"restarts.log").exists())

    def test_verified_rollback_blocks_immediate_redeployment(self):
        self.invoke(apply=True)
        self.assertEqual(release.sha(self.repo),self.good)
        self.assertEqual((self.state/"blocked-candidate.sha").read_text().strip(),self.bad)
        self.assertEqual((self.state/"last-known-good.sha").read_text().strip(),self.good)
        self.assertIn("--user restart iconic-command",(self.root/"restarts.log").read_text())
        event=[json.loads(row) for row in (self.state/"evidence-release-events.jsonl").read_text().splitlines()]
        self.assertEqual([e["stage"] for e in event],
                         ["rollback_requested","rollback_verified"])
        self.assertEqual((self.state/"evidence-release-events.jsonl").stat().st_mode & 0o777,0o600)

    def test_dirty_tree_refused_even_with_apply(self):
        (self.repo/"uncommitted.txt").write_text("private change")
        with self.assertRaises(ValueError):
            self.invoke(apply=True)
        self.assertFalse((self.root/"restarts.log").exists())
        self.assertEqual(release.sha(self.repo),self.bad)

    def test_shallow_checkout_only_allows_exact_pinned_rollback(self):
        # Mirror the real updater's shallow Git fetch behavior.
        (self.repo/".git/shallow").write_text(self.bad+"\n")
        (self.state/"pre-evidence-release.sha").write_text(self.good+"\n")
        self.assertEqual(
            release.run(["git","-C",str(self.repo),"rev-parse","--is-shallow-repository"]),
            "true")
        planned=self.invoke(apply=False)
        self.assertEqual(planned["to_sha"],self.good)
        (self.state/"pre-evidence-release.sha").write_text("0"*40+"\n")
        with self.assertRaises(ValueError):
            self.invoke(apply=False)

    def test_stale_expected_commit_refused(self):
        with self.assertRaises(ValueError):
            self.invoke(expected=self.good,apply=True)
        self.assertEqual(release.sha(self.repo),self.bad)

    def test_refuses_branch_name_instead_of_exact_sha(self):
        with self.assertRaises(ValueError):
            self.invoke(target="HEAD",apply=True)

    def test_unhealthy_rollback_restores_original_candidate(self):
        # Start with bad ancestor, healthy head. Reverting to ancestor fails
        # health; rollback script must restore latest healthy code.
        git("reset","--hard",self.good,cwd=self.repo)
        (self.repo/"server_marker.txt").write_text("GOOD_MARKER_B")
        git("add",".",cwd=self.repo)
        git("commit","-m","good-repair",cwd=self.repo)
        newer=release.sha(self.repo)
        (self.repo/"server_marker.txt").write_text("GOOD_MARKER")
        git("add",".",cwd=self.repo)
        git("commit","-m","healthy-current",cwd=self.repo)
        current=release.sha(self.repo)
        # The earlier BAD marker is no longer an ancestor (because of reset).
        # Test a failing target by patching the server marker's good detection:
        # a candidate commit with BAD as ancestor must first be created.
        git("reset","--hard",self.bad,cwd=self.repo)
        (self.repo/"server_marker.txt").write_text("GOOD_MARKER")
        git("add",".",cwd=self.repo)
        git("commit","-m","fixed after bad",cwd=self.repo)
        repaired=release.sha(self.repo)
        with self.assertRaises(RuntimeError):
            release.rollback(self.repo,self.state,repaired,self.bad,self.url,
                             "iconic-command",str(self.mock),apply=True)
        self.assertEqual(release.sha(self.repo),repaired)
        records=[json.loads(l) for l in (self.state/"evidence-release-events.jsonl").read_text().splitlines()]
        self.assertEqual(records[-1]["stage"],"rollback_rejected_restored_original")


if __name__=="__main__":
    unittest.main()
