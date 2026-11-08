#!/usr/bin/env python3
"""Replay original 45-case adversarial QA against live ICONIC's read-only ask API.

Prompts extracted verbatim from preserved 2026-11-06 independent report.
No production code, model, or weight changes; distinct qa-* session IDs;
auto-learning disabled by server.
UI-only cases 23 and 43 are handled by browser separately.
Results remain private and untracked. Mechanical heuristic verdicts MUST NOT
be misrepresented as an independent 45-case pass score.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

DEFAULT_REPORT=Path("/home/patrick/ICONIC-45-test-QA-2026-11-06.md")
DEFAULT_VERDICTS=Path("/home/patrick/.local/state/iconic-command/qa45-case-verdicts-2026-11-06.json")
OUT=Path("/home/patrick/.local/state/iconic-command/qa-runs/demo45-retest-2026-11-07.json")

def original_cases(path):
    text=path.read_text(encoding="utf-8")
    segments=re.split(r"(?m)^### Test (\d\d)\s*$",text)
    answer=[]
    for i in range(1,len(segments),2):
        n=int(segments[i])
        block=segments[i+1]
        wm=re.search(r"(?m)^Workspace:\s*(.+)",block)
        ws=(wm.group(1) if wm else "").strip()
        questions=re.findall(r"Question \(verbatim\):\s*```text\s*\n(.*?)\n```",block,flags=re.S)
        questions=[q.strip() for q in questions if q.strip()]
        if not questions or not ws: raise ValueError("missing original case "+str(n))
        answer.append({"case":n,"ws":ws,"questions":questions})
    if len(answer)!=45 or sorted(x["case"] for x in answer)!=list(range(1,46)):
        raise AssertionError("Original report should contain all 45 cases")
    return answer

def question(base, ws, prompt, history, session):
    data=json.dumps({"ws":ws,"q":prompt,"history":history,"session":session}).encode()
    req=urllib.request.Request(base+"/api/ask",data=data,method="POST",
        headers={"Content-Type":"application/json"})
    start=time.monotonic()
    output={"q":prompt,"ws":ws,"answer":"","sources":[],"web_offer":None,
            "done":None,"error":None,"http_status":200}
    try:
        with urllib.request.urlopen(req,timeout=115) as resp:
            output["http_status"]=resp.status
            event=None
            for raw in resp:
                line=raw.decode("utf-8","replace").strip()
                if line.startswith("event: "):
                    event=line[7:]
                elif line.startswith("data: "):
                    try: val=json.loads(line[6:])
                    except ValueError: continue
                    if event=="token":output["answer"]+=str(val)
                    elif event=="sources": output["sources"]=val
                    elif event=="web_offer":output["web_offer"]=val
                    elif event=="done":output["done"]=val
                    elif event=="error":output["error"]=val
    except urllib.error.HTTPError as exc:
        output["http_status"]=exc.code
        output["error"]=str(exc.read(500),encoding="utf-8",errors="replace")
    except Exception as exc:
        output["error"]=str(exc)
    output["elapsed_s"]=round(time.monotonic()-start,2)
    output["source_refs"]=[{"n":s.get("n"),"id":s.get("id"),
                            "rel":s.get("rel"),"title":s.get("title")}
                           for s in output["sources"]]
    output.pop("sources",None)
    return output

# Preserve original multi-turn sequences where relevant to failures.
def prompts(c):
    n=c["case"]
    qs=c["questions"]
    if n==23 or n==43: return [] # UI browser tests, no API stand-in
    if n==17: return qs[:1] # case 18 shares exact same original answer
    if n in (3,): return [("What were our total Q3 2026 billings and collections?","setup"),(qs[0],"target")]
    if n in (20,): return [("Where does the $7,030 freight number come from, and how does the vendor scorecard rate Pacific Brass?","setup"),(qs[0],"target")]
    if n in (21,22,37,40,41,42): return [(q,"step") for q in qs[:min(3,len(qs))]]
    if n==24: return [(q,"paraphrase") for q in qs[:3]]
    return [(qs[0],"primary")]

def run_case(case,base,now):
    n=case["case"];ws=case["ws"]
    if "," in ws: ws=ws.split(",")[0].strip()
    sequence=prompts(case)
    if n==23 or n==43: return {"case":n,"kind":"browser_only","steps":[]}
    if n==17 and isinstance(sequence[0],str):
        sequence=[(sequence[0],"primary")]
    history=[]
    outputs=[]
    for idx,(q,mode) in enumerate(sequence,1):
        result=question(base,ws,q,history,f"qa-demo45-{n:02d}-{now}"[:64])
        result["step"]=idx
        result["mode"]=mode
        outputs.append(result)
        if result["answer"] and not result["error"]:
            history.append({"q":q,"a":result["answer"],
                            "sources":result["source_refs"]})
            history=history[-5:]
        if result["error"] or result["http_status"]>=400:
            break
    return {"case":n,"kind":"api_live","workspace":ws,"steps":outputs}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base",default="http://127.0.0.1:8771")
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--start",type=int,default=1)
    p.add_argument("--end",type=int,default=45)
    args=p.parse_args()
    cases=original_cases(DEFAULT_REPORT)
    baseline=json.loads(DEFAULT_VERDICTS.read_text())["results"]
    prev={}
    if args.out.is_file():
        old=json.loads(args.out.read_text(encoding="utf-8"))
        prev={r["case"]:r for r in old.get("results",[])}
        if old.get("source_sha256")!=hashlib.sha256(DEFAULT_REPORT.read_bytes()).hexdigest():
            raise ValueError("Old results from different report")
    runid=str(int(time.time()))
    for c in cases:
        n=c["case"]
        if n<args.start or n>args.end or n in prev:continue
        row=run_case(c,args.base,runid)
        row["original_verdict"]=baseline[n-1]["verdict"]
        row["original_severity"]=baseline[n-1]["severity"]
        row["original_issue"]=baseline[n-1]["reason"]
        prev[n]=row
        results=sorted(prev.values(),key=lambda r:r["case"])
        data={"schema":"iconic-demo45-live-replay-v1",
              "source_sha256":hashlib.sha256(DEFAULT_REPORT.read_bytes()).hexdigest(),
              "base":args.base,"original_cases":45,
              "scope":"API replays + separately required UI tests; no automated independent verdict",
              "results":results}
        args.out.parent.mkdir(parents=True,exist_ok=True)
        tmp=args.out.with_suffix(".tmp")
        tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        tmp.chmod(0o600)
        tmp.replace(args.out)
        steps=row.get("steps",[])
        short_answer=(steps[-1]["answer"][:82] if steps else "BROWSER_ONLY").replace("\n"," ")
        errs=[s.get("error") for s in steps if s.get("error")]
        print(f"CASE {n:02d}/45 OLD_{row['original_verdict']:4} -> returned {len(steps)} steps; "
              f"error={str(errs)[:60]} elapsed={sum(s.get('elapsed_s',0) for s in steps):.1f}s :: {short_answer}",
              flush=True)
    print("API_REPLAY_COMPLETED",len(prev),"/45","REPORT",args.out,flush=True)
if __name__=="__main__":main()
