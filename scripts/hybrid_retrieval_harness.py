#!/usr/bin/env python3
"""Offline, read-only hybrid-retrieval benchmark over fictional demo workspaces.

Compare plain BM25 with BM25 + local Nomic dense embeddings on novel paraphrases.
This is NOT active in the live demo, nor a foundation for real-tenant auth.
Runs against localhost:8081 embeddings only; never calls Qwen production LLM.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

EMBED_ENDPOINT="http://127.0.0.1:8081/v1/embeddings"
MODEL="/home/patrick/models/nomic-embed-text-v1.5.Q8_0.gguf"
OUT=Path("/home/patrick/.local/state/iconic-command/qa-runs/hybrid-retrieval-holdout.json")
# Non-original paraphrases, never used to train/rewrite data.
CASES=[
    ("hollis-reyes","Which employee assembled the quarterly fee and cash report?","billing/2026-q3-billing-report.md"),
    ("hollis-reyes","When must our firm stop automatic renewal of the document hosting subscription?","vendors/2026-10-lexvault-renewal.md"),
    ("hollis-reyes","Where do we find the result of our employee discrimination win?","matters/2024-briggs-v-cascade-anesthesia.md"),
    ("hollis-reyes","Whose desk is the Graves Whitlock reply on?","operations/2026-11-deadlines.md"),
    ("hollis-reyes","What record lists the elderly unpaid Tidewell debt?","billing/2026-q3-billing-report.md"),
    ("hollis-reyes","What did the partners decide about the expensive storage platform?","meetings/2026-10-28-partner-meeting.md"),
    ("hollis-reyes","Where is the decline in associate hours documented?","billing/2026-q3-billing-report.md"),
    ("northline-supply","When is the buyer finally calling it a career?","people/dale-pruitt-handoff.md"),
    ("northline-supply","Which file explains the new shipping minimum from our brass supplier?","vendors/2026-10-pacific-brass-terms.md"),
    ("northline-supply","Where did the September copper supply failure delay a contractor's work?","vendors/2026-q3-vendor-scorecard.md"),
    ("northline-supply","Has Ray actually decided about the very early loading shift?","meetings/2026-10-30-leadership-meeting.md"),
    ("northline-supply","How much cash is trapped in aging HVAC circuit boards?","inventory/2026-10-slow-movers-detail.csv"),
    ("northline-supply","Which catalog contains goods untouched for six months?","inventory/2026-10-slow-movers.md"),
    ("northline-supply","Which supplier price hike hurt margins last quarter?","sales/2026-q3-sales-summary.md"),
    ("northline-supply","What source names our largest customers and their sales totals?","sales/2026-q3-sales-summary.md"),
    ("northline-supply","Who prepared the slow inventory aging list?","inventory/2026-10-slow-movers.md"),
]


def embed(inputs):
    req=Request(EMBED_ENDPOINT,method="POST",
        data=json.dumps({"model":MODEL,"input":inputs}).encode(),
        headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=35) as resp: body=json.load(resp)
    data=sorted(body["data"],key=lambda x:x["index"])
    vec=[item["embedding"] for item in data]
    if len(vec)!=len(inputs) or len({len(x) for x in vec})!=1:
        raise ValueError("embedding returned an invalid shape")
    return vec


def cosine(a,b):
    return sum(x*y for x,y in zip(a,b))/max(1e-12,math.sqrt(sum(v*v for v in a))*math.sqrt(sum(v*v for v in b)))


def lexical_rank(w,q):
    hits=w.search(q,k=1000,per_doc=1000)
    byid={}
    for i,(score,chunk) in enumerate(hits):
        byid.setdefault(chunk["doc"],(score,i+1))
    return byid


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    server.start_offline(detect_model=False)
    results=[]
    for wid in ("hollis-reyes","northline-supply"):
        w=server.WORKSPACES[wid]
        # Bound to a small documented sample set. Embedding text is local-only.
        corpus=[w.docs[c["doc"]]["title"]+"\n"+w.docs[c["doc"]]["rel"]+"\n"+c["text"] for c in w.chunks]
        queries=[q for ws,q,expected in CASES if ws==wid]
        vectors=embed(["search_document: "+t for t in corpus]+
                      ["search_query: "+q for q in queries])
        cv=vectors[:len(corpus)]
        qv=vectors[len(corpus):]
        for question,vector in zip(queries,qv):
            expected=next(e for ws,q,e in CASES if ws==wid and q==question)
            lex=lexical_rank(w,question)
            semantic={}
            for c,v in zip(w.chunks,cv):
                sim=cosine(v,vector)
                semantic[c["doc"]]=max(sim,semantic.get(c["doc"],-1))
            sem_ids=sorted(semantic,key=lambda id:-semantic[id])
            sem_ranks={id:i+1 for i,id in enumerate(sem_ids)}
            # Reciprocal rank fusion: lexical scores for exact terms, semantic
            # ranks for paraphrases. Bounded to docs in selected workspace.
            scores={}
            for doc in w.docs:
                id=doc["id"]
                scores[id] = 1/(60+sem_ranks[id])
                if id in lex:
                    scores[id] += 1/(60+lex[id][1])
            bm_ids=sorted(lex,key=lambda id:(-lex[id][0],lex[id][1]))
            hybrid_ids=sorted(scores,key=lambda id:-scores[id])
            sem_ids=sem_ids[:]
            def names(ids):
                return [w.docs[id]["rel"] for id in ids[:3]]
            results.append({
                "workspace":wid,"query":question,"expected_doc":expected,
                "bm25_top3":names(bm_ids),"dense_top3":names(sem_ids),
                "hybrid_top3":names(hybrid_ids),
                "bm25_hit3":expected in names(bm_ids),
                "dense_hit3":expected in names(sem_ids),
                "hybrid_hit3":expected in names(hybrid_ids),
                "bm25_hit1":names(bm_ids)[:1]==[expected],
                "dense_hit1":names(sem_ids)[:1]==[expected],
                "hybrid_hit1":names(hybrid_ids)[:1]==[expected],
            })
    summary={
       "schema":"hybrid-retrieval-holdout-v1","cases":len(results),
       "bm25_hit3":sum(x["bm25_hit3"] for x in results),
       "dense_hit3":sum(x["dense_hit3"] for x in results),
       "hybrid_hit3":sum(x["hybrid_hit3"] for x in results),
       "bm25_hit1":sum(x["bm25_hit1"] for x in results),
       "dense_hit1":sum(x["dense_hit1"] for x in results),
       "hybrid_hit1":sum(x["hybrid_hit1"] for x in results),
       "no_model_answers_scored":True,
       "no_production_changes":True,
       "all_data_from_fictional_demo_workspaces":True,
       "results":results,
    }
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(summary,indent=2)+"\n")
    args.output.chmod(0o600)
    print("RETRIEVAL_HOLDOUT_RESULTS",json.dumps({k:v for k,v in summary.items() if k!="results"},indent=2),flush=True)
    for r in results:
        print("CASE",r["workspace"],repr(r["query"]), "BM",r["bm25_hit3"],"DENSE",r["dense_hit3"],"HYBRID",r["hybrid_hit3"],flush=True)
    print("LOCAL_FILE",args.output)


if __name__=="__main__":
    main()
