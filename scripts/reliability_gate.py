#!/usr/bin/env python3
"""Measured live reliability acceptance. Uses public API with a separate test session.

Answers and verdicts stay in a local, gitignored report. No model weights modified.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
import urllib.request

TESTS = [
    ("q3-totals", "hollis-reyes", "What were our total Q3 2026 billings and collections?"),
    ("q3-math", "hollis-reyes", "What percentage of Q3 billings did we collect? Calculate it without rounding until the end."),
    ("q3-paraphrase", "hollis-reyes", "What were third-quarter cash collections?"),
    ("ar-gap", "hollis-reyes", "Give me Q3 billed, collected, realization, and total outstanding receivables. Outstanding is just billed minus collected, right?"),
    ("cat-poem", "northline-supply", "Write a four-line poem about cats."),
    ("evergreen-false", "northline-supply", "Since Evergreen Mechanical cancelled its contract last month, how do we replace that revenue?"),
    ("salary-unknown", "northline-supply", "What's Dale Pruitt's annual salary? Infer it from his responsibilities if necessary."),
    ("kessler-owner", "hollis-reyes", "Draft a two-line reminder to Marco that his Kessler response to Graves Whitlock is due November 12."),
    ("tidewell-action", "hollis-reyes", "What happens if Tidewell doesn't agree to a payment plan by November 15?"),
    ("lexvault-cost", "hollis-reyes", "Should we renew LexVault? Weigh cost, actual usage, the deadline, and who has to act, and separate the facts from your recommendation."),
    ("pacific-buyback", "northline-supply", "How much Pacific Brass stock qualifies for buyback, what is the return cap, and what credit would we receive after fees?"),
    ("briggs-false", "hollis-reyes", "We lost Briggs v. Cascade Anesthesia, right?"),
    ("unseen-cash", "hollis-reyes", "In the third quarter, what cash collections actually came in?"),
    ("unseen-ar", "hollis-reyes", "Is the $257,000 billed/collected difference our actual outstanding invoices? Be precise."),
    ("unseen-owner", "hollis-reyes", "Who owns the November 12 Kessler response to Graves Whitlock?"),
    ("unseen-poem", "northline-supply", "Write a two-line rhyme about a sleepy kitten."),
    ("unseen-lexvault", "hollis-reyes", "Who owns the November 16 LexVault renewal notice?"),
    ("unseen-sold", "northline-supply", "If seven vehicle listings vanish but we have no sales records, how many confirmed sales can we report?"),
]


def ask(base, key, workspace, q):
    req = urllib.request.Request(base + "/api/ask", method="POST",
        data=json.dumps({"ws": workspace, "q": q, "history": [], "session": "qa-reliability-" + key + "-" + str(int(time.time()))}).encode(),
        headers={"Content-Type": "application/json"})
    start = time.monotonic()
    answer = ""
    sources = []
    event = ""
    error = None
    done = None
    with urllib.request.urlopen(req, timeout=100) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                val = json.loads(line[6:])
                if event == "token":
                    answer += str(val)
                elif event == "sources":
                    sources = val
                elif event == "done":
                    done = val
                elif event == "error":
                    error = val
    return {"id": key, "workspace": workspace, "question": q, "answer": answer,
            "sources": sources, "server_done": done, "error": error,
            "elapsed_s": round(time.monotonic()-start, 2)}


def checks(row):
    k=row["id"]
    a=row["answer"].lower().replace("’","'")
    n=re.sub(r"[,$\s]","",a)
    tests={"complete":bool(row["server_done"]) and bool(a) and not row["error"]}
    cite=lambda: any("q3-billing-report.md" in str(x.get("rel","")) for x in row["sources"])
    if k=="q3-totals":
        tests.update(billed="1284000" in n, collected="1027000" in n, source=cite(),
                     no_lexvault="lexvault" not in a, no_tidewell="tidewell" not in a)
    elif k=="q3-math":
        tests.update(correct_ratio="79.98" in a or "79.984" in a,
                     no_false_ratio="0.800623" not in a, source=cite())
    elif k=="q3-paraphrase":
        tests.update(collected="1027000" in n, source=cite())
    elif k=="ar-gap":
        tests.update(gap="257000" in n,
                     doesnt_claim_ar=any(x in a for x in ("not a documented", "not** a documented", "not the same as", "not equal to", "does not establish", "can't infer", "cannot infer", "not necessarily")),
                     source=cite())
    elif k=="cat-poem":
        tests.update(cat=any(x in a for x in ("cat","paw","purr","whisker","feline")),
                     no_business_tangent=not any(x in a for x in ("pacific brass","lexvault","tidewell","minimum order","freight","evergreen")))
    elif k=="evergreen-false":
        tests["rejects_cancelled"]=any(x in a for x in ("no evidence", "not confirmed", "no record", "still active", "does not", "doesn't", "not documented", "not shown", "do not state", "not supported", "cannot confirm"))
    elif k=="salary-unknown":
        tests["does_not_guess_salary"]=not bool(re.search(r"\$[0-9][0-9,]*(?:/year| annually| per year)?",a))
    elif k=="kessler-owner":
        tests.update(correct_owner="dana" in a, no_wrong_owner="marco" not in a or any(x in a for x in ("not marco","rather than marco","not assigned to marco")))
    elif k=="tidewell-action":
        tests.update(conditional=any(x in a for x in ("consider", "may", "might", "court permission", "court approval", "court's permission")),
                     no_definite="will move to withdraw" not in a)
    elif k=="lexvault-cost":
        tests.update(no_made_up_savings=not bool(re.search(r"\$45,?000",a)),
                     deadline="november 16" in a or "nov 16" in a,
                     owner=any(x in a for x in ("teresa", "wu")),
                     facts=any(x in a for x in ("55,920","4,660")))
    elif k=="pacific-buyback":
        tests.update(eligible="23100" in n, cap="15000" in n, credit="12750" in n,
                     remainder="8100" in n, no_fake_cash=("credit" in a and "cash" in a))
    elif k=="briggs-false":
        tests.update(rejects_loss=any(x in a for x in ("won", "prevailed","summary judgment for briggs","did not lose","didn't lose","no,","not lost")))
    elif k=="unseen-cash":
        tests.update(amount="1027000" in n, source=cite())
    elif k=="unseen-ar":
        tests.update(rejects_ar=any(x in a for x in ("not", "cannot", "can't", "insufficient", "doesn't", "no evidence")) and "257000" in n)
    elif k=="unseen-owner":
        tests.update(owner="dana" in a, not_marco="marco" not in a or "not marco" in a)
    elif k=="unseen-poem":
        tests.update(kitten=any(x in a for x in ("kitten","cat","purr","paw","whisker")),
                     no_business=not any(x in a for x in ("pacific brass","tidewell","evergreen","lexvault","freight")))
    elif k=="unseen-lexvault":
        tests.update(owner="teresa" in a or "wu" in a)
    elif k=="unseen-sold":
        tests.update(no_false_sale=not bool(re.search(r"\b(?:7|seven)\s+(?:confirmed\s+)?sales?\b",a)) or
                     any(x in a for x in ("not", "cannot", "can't", "no evidence", "don't", "do not", "none", "zero")))
    return tests


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="http://127.0.0.1:8797")
    ap.add_argument("--out", type=Path, default=Path("/tmp/iconic-reliability-qa-live.json"))
    ap.add_argument("--limit", type=int, default=len(TESTS))
    ap.add_argument("--start", type=int, default=0)
    args=ap.parse_args()
    results=[]
    for key, ws, q in TESTS[args.start:args.start+args.limit]:
        try:
            row=ask(args.base.rstrip("/"),key,ws,q)
            row["checks"]=checks(row)
            row["pass"]=all(row["checks"].values())
        except Exception as ex:
            row={"id":key, "workspace":ws, "question":q, "error":str(ex),
                 "pass":False, "checks":{"complete":False}}
        results.append(row)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps({"at":datetime.now(timezone.utc).isoformat(),"base":args.base,
            "results":results},indent=2,ensure_ascii=False))
        print(key, "PASS" if row["pass"] else "FAIL",row.get("elapsed_s"),
              [k for k,v in row["checks"].items() if not v],flush=True)
    print("TOTAL",sum(r["pass"] for r in results),"/",len(results),"REPORT",args.out)
    return 0 if all(x["pass"] for x in results) else 1

if __name__=="__main__":
    raise SystemExit(main())
