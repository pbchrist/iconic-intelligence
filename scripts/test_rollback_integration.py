#!/usr/bin/env python3
"""End-to-end simulated bad release; run without touching the live service."""
import http.server, json, os, pathlib, subprocess, tempfile, threading
from functools import partial

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "update.sh"

def run(*args, cwd=None, env=None):
    p = subprocess.run(list(args), cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=90)
    if p.returncode:
        raise RuntimeError("%s returned %s:\n%s" % (args,p.returncode,p.stderr))
    return p.stdout.strip()

def main():
    with tempfile.TemporaryDirectory(prefix="iconic-rollback-test-") as temp:
        root = pathlib.Path(temp)
        seed=root/"seed"
        seed.mkdir()
        bare=root/"bare.git"
        live=root/"live"
        home=root/"home"
        (home/".config").mkdir(parents=True)
        (home/".local/state/iconic-command").mkdir(parents=True)
        env=os.environ.copy()
        env["HOME"]=str(home)
        mock=root/"bin"
        mock.mkdir()
        (mock/"systemctl").write_text("#!/bin/sh\nexit 0\n")
        (mock/"systemctl").chmod(0o755)
        env["PATH"]=str(mock)+":"+env["PATH"]
        run("git","init","--bare","--initial-branch=dashboard",str(bare))
        run("git","init","--initial-branch=dashboard",str(seed))
        run("git","config","user.name","QA",cwd=seed)
        run("git","config","user.email","qa@example.test",cwd=seed)
        (seed/"tests").mkdir()
        (seed/"tests/test_dummy.py").write_text("import unittest\nclass TestX(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
        (seed/"update.sh").write_bytes(SCRIPT.read_bytes())
        (seed/"server.py").write_text("GOOD_MARKER = True\n")
        run("git","add",".",cwd=seed)
        run("git","commit","-m","known-good",cwd=seed)
        good=run("git","rev-parse","HEAD",cwd=seed)
        run("git","remote","add","origin",str(bare),cwd=seed)
        run("git","push","-u","origin","dashboard",cwd=seed)
        run("git","clone","--branch","dashboard",str(bare),str(live))
        (seed/"server.py").write_text("BAD_MARKER = True\n")
        run("git","add",".",cwd=seed)
        run("git","commit","-m","bad-candidate-that-passes-unit-tests",cwd=seed)
        bad=run("git","rev-parse","HEAD",cwd=seed)
        run("git","push",cwd=seed)

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                valid="GOOD_MARKER" in (live/"server.py").read_text()
                data=json.dumps({"model":{"online":valid,"model":"test-model"}}).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def log_message(self,*args): pass
        srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        threading.Thread(target=srv.serve_forever,daemon=True).start()
        env["ICONIC_UPDATE_HEALTH_URL"]="http://127.0.0.1:%s/api/status"%srv.server_address[1]
        cmd=["sh",str(live/"update.sh")]
        try:
            proc=subprocess.run(cmd, env=env, cwd=live, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True,timeout=65)
            print("BAD RELEASE EXIT:",proc.returncode)
            print("BAD RELEASE LOG:",proc.stderr[-850:])
            assert proc.returncode != 0, "bad candidate should fail"
            assert run("git","rev-parse","HEAD",cwd=live)==good, "rollback must restore good SHA"
            state=home/".local/state/iconic-command"
            assert (state/"blocked-candidate.sha").read_text().strip()==bad
            assert not (state/"pending-deploy.sha").exists()
            second=subprocess.run(cmd,env=env,cwd=live,text=True,capture_output=True,timeout=15)
            assert second.returncode != 0 and "skipping previously failed" in second.stderr
            (seed/"server.py").write_text("GOOD_MARKER = True\nREVISED = True\n")
            run("git","add",".",cwd=seed)
            run("git","commit","-m","new-healthy-candidate",cwd=seed)
            new=run("git","rev-parse","HEAD",cwd=seed)
            run("git","push",cwd=seed)
            third=subprocess.run(cmd,env=env,cwd=live,text=True,capture_output=True,timeout=35)
            print("HEALTHY RELEASE EXIT:",third.returncode)
            print("HEALTHY RELEASE LOG:",third.stderr[-650:])
            assert third.returncode==0,third.stderr
            assert run("git","rev-parse","HEAD",cwd=live)==new
            assert (state/"last-known-good.sha").read_text().strip()==new
            assert not (state/"blocked-candidate.sha").exists()
            assert not (state/"pending-deploy.sha").exists()
            print("PASS: bad release rolled back; repeated bad SHA blocked; newer healthy release deployed")
        finally:
            srv.shutdown()

if __name__=="__main__":main()
