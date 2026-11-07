#!/usr/bin/env python3
"""Explicit, audited rollback of the ICONIC web process only.

Example (DO NOT run until an evidence-engine release is deployed):
 python3 scripts/evidence_release_control.py status
 python3 scripts/evidence_release_control.py rollback --apply \
    --expected-current <full-candidate-sha> --to <full-known-good-sha>

Guardrails: clean dashboard branch, exact source HEAD, ancestor target, one
protected service restart, health check, candidate blocking, rollback audit.
Never touches GPU servers, QLoRA, Reserve tenant data or conversation logs.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

DEFAULT_REPO = Path("/home/patrick/iconic-command")
DEFAULT_STATE = Path("/home/patrick/.local/state/iconic-command")
DEFAULT_HEALTH = "http://127.0.0.1:8771/api/status"


def run(argv,cwd=None,check=True):
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=35)
    if check and p.returncode:
        raise RuntimeError("Command failed (no secret output shown): "+repr(argv[:2]))
    return p.stdout.strip() if check else p.returncode


def sha(repo,ref="HEAD"):
    return run(["git","-C",str(repo),"rev-parse","--verify",ref+"^{commit}"])


def clean(repo):
    return not run(["git","-C",str(repo),"status","--porcelain"])


def file_atomic(path,txt):
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_name(target.name+".new")
    fd=os.open(temp,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    try:
        os.write(fd,txt.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temp,target)


def note(state,stage,**fields):
    path=Path(state)/"evidence-release-events.jsonl"
    record={"when_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "stage":stage,"schema":"iconic-evidence-release-event-v1",**fields}
    fd=os.open(path,os.O_CREAT|os.O_APPEND|os.O_WRONLY,0o600)
    try:
        os.fchmod(fd,0o600)
        os.write(fd,(json.dumps(record,sort_keys=True)+"\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def health(url):
    with urlopen(url,timeout=4) as r:
        result=json.load(r)
    if result.get("model",{}).get("online") is not True:
        raise RuntimeError("Demo model is reported offline")
    if not result["model"].get("model"):
        raise RuntimeError("Model name missing")
    return True


def restart(service,systemctl="systemctl"):
    run([systemctl,"--user","restart",service])


def validate(repo,current,target,expected):
    if not re.fullmatch(r"[0-9a-f]{40}", expected) or expected != current:
        raise ValueError("Rollback requires the exact current full 40-digit SHA")
    if not clean(repo):
        raise ValueError("Refusing rollback: deployment tree is dirty")
    branch=run(["git","-C",str(repo),"symbolic-ref","--short","HEAD"])
    if branch!="dashboard":
        raise ValueError("Refusing rollback outside dashboard")
    if current!=sha(repo,expected):
        raise ValueError("Expected-current SHA does not match current code")
    if current==target:
        raise ValueError("No rollback needed")
    if run(["git","-C",str(repo),"merge-base","--is-ancestor",target,current],check=False)!=0:
        raise ValueError("Rollback target must be ancestor of current deployment")


def rollback(repo,state,expected,target,health_url,service,systemctl,apply=False):
    repo=Path(repo).resolve()
    state=Path(state).resolve()
    state.mkdir(parents=True,exist_ok=True)
    current=sha(repo)
    if not re.fullmatch(r"[0-9a-f]{40}", target):
        raise ValueError("Rollback target must be an exact full 40-digit SHA")
    wanted=sha(repo,target)
    validate(repo,current,wanted,expected)
    plan={"from_sha":current,"to_sha":wanted,"service":service,
          "model_service_restart":False,"private_state_delete":False,
          "will_block_redeployment_of":current}
    if not apply:
        print(json.dumps({"DRY_RUN":True,**plan},indent=2))
        return plan
    # Only execute upon explicit --apply. The auto-updater sees this blocked
    # candidate and will not immediately replace the manually restored build.
    note(state,"rollback_requested",**plan)
    file_atomic(state/"blocked-candidate.sha",current+"\n")
    try:
        run(["git","-C",str(repo),"reset","--hard",wanted])
        restart(service,systemctl)
        health(health_url)
        file_atomic(state/"last-known-good.sha",wanted+"\n")
        run(["git","-C",str(repo),"update-ref","refs/iconic/last-known-good",wanted])
    except Exception as exc:
        # Restore original code on a failed rollback; preserve a human-readable
        # failure record and do not declare recovery without health confirmation.
        try:
            run(["git","-C",str(repo),"reset","--hard",current])
            restart(service,systemctl)
            health(health_url)
            note(state,"rollback_rejected_restored_original",reason=type(exc).__name__,
                 from_sha=current,to_sha=wanted)
        except Exception as restore:
            note(state,"rollback_and_restore_failed",reason=type(restore).__name__,
                 from_sha=current,to_sha=wanted)
        raise
    note(state,"rollback_verified",**plan,health="online")
    print(json.dumps({"ROLLBACK_VERIFIED":True,**plan},indent=2))
    return plan


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",type=Path,default=DEFAULT_REPO)
    p.add_argument("--state",type=Path,default=DEFAULT_STATE)
    p.add_argument("--health-url",default=DEFAULT_HEALTH)
    p.add_argument("--service",default="iconic-command")
    p.add_argument("--systemctl",default="systemctl")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("status")
    r=sub.add_parser("rollback")
    r.add_argument("--apply",action="store_true")
    r.add_argument("--expected-current",required=True)
    r.add_argument("--to",required=True)
    args=p.parse_args()
    if args.command=="status":
        current=sha(args.repo)
        recorded=Path(args.state)/"last-known-good.sha"
        print(json.dumps({"current_sha":current,
            "last_known_good":recorded.read_text().strip() if recorded.is_file() else None,
            "rollback_is_explicit":True,
            "audit_log":str(args.state/"evidence-release-events.jsonl"),
            "public_data_untouched":True},indent=2))
        return
    rollback(args.repo,args.state,args.expected_current,args.to,
             args.health_url,args.service,args.systemctl,args.apply)


if __name__=="__main__":
    main()
