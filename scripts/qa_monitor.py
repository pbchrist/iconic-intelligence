#!/usr/bin/env python3
"""Low-impact scheduled live QA (three rotating public-model questions daily).
The monitor records evidence and opens findings; it never edits production code or prompts.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import qa_bridge
import live_adversarial as live

def selection(count, day):
    n=len(live.TESTS)
    start=(day.toordinal() * 3) % n
    return [live.TESTS[(start+i)%n] for i in range(min(count,n))]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--count",type=int,default=3)
    p.add_argument("--url",default=os.environ.get("ICONIC_QA_URL","https://patrick-beastmaster.tailf32530.ts.net"))
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()
    if a.count<1 or a.count>8:
        p.error("count must be 1 through 8 to protect the production model")
    today=datetime.now().date()
    cases=selection(a.count,today)
    print("Daily QA selection:",", ".join(x[0] for x in cases),flush=True)
    if a.dry_run:
        return 0
    live.BASE=a.url.rstrip("/")
    state=qa_bridge.STATE
    runs=state/"qa-runs"
    qa_bridge.private_dir(runs)
    out=runs/("monitor-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json")
    results=[]
    for name,wid,q in cases:
        started=time.monotonic()
        try:
            item=live.ask(name,wid,q)
        except Exception as err:
            item={"name":name,"workspace":wid,"question":q,"status":"inconclusive",
                  "reason":"request failed: "+str(err)[:200],"checks":{}}
        item["seconds"]=round(time.monotonic()-started,1)
        results.append(item)
        qa_bridge.atomic(out,{"at":qa_bridge.now(),"results":results,"base":live.BASE,"automated":True})
        print(name,item.get("pass",item.get("status")),"elapsed",item["seconds"],flush=True)
    summary=qa_bridge.ingest(out)
    print("QA RECORD",summary,flush=True)
    return 0 if all(x.get("pass") is True for x in results) else 1

if __name__=="__main__":
    sys.exit(main())
