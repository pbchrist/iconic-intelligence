#!/usr/bin/env python3
"""Verify ICONIC private audit integrity and summarize coverage, no raw prompts.

Can be run by a low-priority systemd user timer independently of model inference.
Exit nonzero on corrupt records, missing journal, or incomplete requests older
than the configured grace interval. No private payload appears on stdout.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import evidence_trace

DEFAULT_STATE=Path("/home/patrick/.local/state/iconic-command")


def audit_report(path, max_pending_minutes=15):
    integrity=evidence_trace.verify_journal(path)
    path=Path(path)
    stages=Counter()
    verification=Counter()
    releases=Counter()
    requests=defaultdict(lambda: {"start":None,"end":None})
    now=datetime.now(timezone.utc)
    with path.open(encoding="utf-8") as fp:
        for raw in fp:
            x=json.loads(raw)
            stages[x["stage"]]+=1
            releases[x.get("release","unknown")]+=1
            rid=x.get("request_id")
            if not rid:
                continue
            if x["stage"]=="request.accepted":
                requests[rid]["start"]=x["time_utc"]
            if x["stage"] in ("response.completed","response.failed"):
                requests[rid]["end"]=x["stage"]
            if x["stage"]=="verification.completed":
                verification[x.get("verifier_status","unknown")]+=1
    aged=[]
    for key,row in requests.items():
        if row["end"] is not None:
            continue
        if row["start"]:
            age=(now-datetime.fromisoformat(row["start"])).total_seconds()/60
            if age>max_pending_minutes:
                aged.append(key)
    coverage=sum(row["end"] is not None for row in requests.values())
    accepted=stages["request.accepted"]
    return {
        "schema":"iconic-evidence-audit-health-v1",
        "generated_utc":now.isoformat(timespec="seconds"),
        "integrity":"pass",
        "records":integrity["records"],
        "last_hash":integrity["last_hash"],
        "accepted_requests":accepted,
        "completed_or_failed_requests":coverage,
        "open_requests":len(requests)-coverage,
        "overdue_open_request_count":len(aged),
        "response_failures":stages["response.failed"],
        "claim_checks":stages["verification.claim"],
        "full_answer_checks":stages["verification.completed"],
        "verifier_status_counts":dict(sorted(verification.items())),
        "stage_counts":dict(sorted(stages.items())),
        "release_counts":dict(sorted(releases.items())),
        "sensitive_payloads_included":False,
        "status":"pass" if not aged else "pending_request_alert",
    }


def save_private(path, data):
    dest=Path(path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_name(dest.name+".tmp")
    fd=os.open(tmp,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    try:
        os.write(fd,(json.dumps(data,indent=2,sort_keys=True)+"\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp,dest)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state",type=Path,default=DEFAULT_STATE)
    p.add_argument("--save",action="store_true")
    p.add_argument("--max-pending-minutes",type=int,default=15)
    args=p.parse_args()
    path=args.state/"evidence-audit-v1.jsonl"
    try:
        summary=audit_report(path,args.max_pending_minutes)
    except Exception as exc:
        print("AUDIT_INTEGRITY_FAILURE",type(exc).__name__,file=sys.stderr)
        sys.exit(2)
    if args.save:
        save_private(args.state/"evidence-audit-health.json",summary)
    print(json.dumps(summary,indent=2,sort_keys=True))
    if summary["status"]!="pass":
        sys.exit(1)


if __name__=="__main__":
    main()
