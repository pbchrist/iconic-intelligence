#!/usr/bin/env python3
"""ICONIC QA intake: audit independent results, queue actionable findings, gate source-grounded regressions.

NO test result can edit production code or become a model instruction automatically.
Untrusted reports stay in a private state directory; approved assertions live in Git.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import subprocess
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
STATE = Path(os.environ.get("ICONIC_STATE", str(Path.home()/".local/state/iconic-command")))
INBOX = STATE / "qa-inbox"
ARCHIVE = STATE / "qa-processed"
REJECTED = STATE / "qa-rejected"
PENDING = STATE / "qa-pending"
LEDGER = STATE / "qa-results.jsonl"
INDEX = STATE / "qa-imports.json"
APPROVED = ROOT / "qa/approved.json"
MAX_REPORT = 3_000_000
MAX_CASES = 250
FIXES = {
    "citation": "Inspect cited source text and add a source-grounded citation regression; do not fix using a prompt alone.",
    "retrieval": "Verify source documents, repair retrieval/ranking, and approve a source-grounding regression.",
    "numbers": "Reconcile eligible amount, cap, fee, actual credit, and financial evidence; add numeric acceptance assertions.",
    "context": "Reproduce across sequential turns and workspace switches; add a multi-turn behavioral regression.",
    "isolation": "Review workspace routing and block cross-tenant retrieval; add a tenant-isolation regression.",
    "security": "Review injection/security handling and add a security regression before proposing deployment.",
    "unknown": "Reproduce the result, inspect actual sources, and specify a trustworthy acceptance criterion.",
}
LESSON_CANDIDATES = {
    "citation": "Verify each cited factual claim against the source document that supports it.",
    "retrieval": "Use relevant retrieved evidence before claiming that requested business information is unavailable.",
    "numbers": "Distinguish amounts eligible for a transaction from contractual limits and net financial outcomes.",
    "context": "Answer the most recent follow-up directly while preserving the current conversation topic.",
    "isolation": None,
    "security": None,
    "unknown": None,
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600) if path.is_relative_to(STATE) else None
    os.replace(tmp, path)


def private_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)


def getjson(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def lock():
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "qa-bridge.lock").open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def label(item):
    # Missing verdict must never silently become a pass.
    if type(item.get("pass")) is bool:
        return "pass" if item["pass"] else "fail"
    v = str(item.get("status") or item.get("verdict") or item.get("result") or "").strip().lower()
    if v in ("passed", "pass", "ok", "success"):
        return "pass"
    if v in ("failed", "fail", "critical", "error"):
        return "fail"
    return "inconclusive"


def category(item):
    text = " ".join(str(item.get(k, "")) for k in ("name", "question", "reason", "failure", "category")).lower()
    if any(x in text for x in ("cross_tenant", "cross-leak", "cross_company", "workspace isolation", "leakage", "other company")):
        return "isolation"
    if any(x in text for x in ("injection", "password", "secret", "system prompt", "ssn", "social security")):
        return "security"
    if any(x in text for x in ("citation", "cited", "wrong source", "document-source")):
        return "citation"
    if any(x in text for x in ("buyback", "inventory", "fee", "math", "arithmetic", "calculation", "salary", "billing percentage")):
        return "numbers"
    if any(x in text for x in ("follow-up", "followup", "conversation", "switch", "history", "yes", "pronoun")):
        return "context"
    if any(x in text for x in ("billing", "collection", "evergreen", "renewal", "retriev", "source", "spanish")):
        return "retrieval"
    return "unknown"


def clean(item):
    if not isinstance(item, dict):
        raise ValueError("each result must be a JSON object")
    question = str(item.get("question") or item.get("prompt") or "").strip()[:1200]
    ws = str(item.get("workspace") or item.get("ws") or "").strip()[:96]
    if not question or not ws:
        raise ValueError("each result needs question and workspace")
    # Identifier deliberately excludes the grading verdict: successive retries share identity.
    cid = hashlib.sha256((ws + "\0" + question.casefold()).encode()).hexdigest()[:18]
    sources = item.get("sources") if isinstance(item.get("sources"), list) else []
    return {"id":cid, "name":str(item.get("name") or item.get("id") or "")[:120],
            "workspace":ws, "question":question,
            "answer":str(item.get("answer") or item.get("actual") or "")[:12000],
            "expected":str(item.get("expected") or item.get("expectation") or "")[:1500],
            "reason":str(item.get("reason") or item.get("failure") or "")[:1500],
            "verdict":label(item), "category":category(item),
            "checks":item.get("checks") if isinstance(item.get("checks"), dict) else {},
            "sources":[{"rel":str(x.get("rel") or "")[:300], "n":x.get("n")}
                       for x in sources[:20] if isinstance(x, dict)]}


def ingest(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_REPORT:
        raise ValueError("not a regular JSON report under 3MB")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    obj = json.loads(raw)
    rows = obj.get("results", obj.get("tests")) if isinstance(obj, dict) else None
    if not isinstance(rows, list) or len(rows) == 0 or len(rows) > MAX_CASES:
        raise ValueError("report needs 1-250 entries in results[] or tests[]")
    cases = [clean(row) for row in rows]  # reject the entire report if any row cannot be trusted
    with lock():
        seen = getjson(INDEX, {})
        if digest in seen:
            return dict(seen[digest], duplicate=True)
        private_dir(ARCHIVE)
        private_dir(PENDING)
        (ARCHIVE / (digest[:20] + ".json")).write_bytes(raw)
        os.chmod(ARCHIVE / (digest[:20] + ".json"), 0o600)
        ts = now()
        with LEDGER.open("a", encoding="utf-8") as output:
            for row in cases:
                entry = dict(row, imported_at=ts, report=digest[:20])
                output.write(json.dumps(entry, ensure_ascii=False) + "\n")
                pending = PENDING / (row["id"] + ".json")
                if row["verdict"] != "pass":
                    proposal = {"id":row["id"], "status":"needs_review", "first_seen":ts,
                                "last_seen":ts, "verdict":row["verdict"], "category":row["category"],
                                "workspace":row["workspace"], "question":row["question"],
                                "answer":row["answer"], "expected":row["expected"],
                                "reason":row["reason"], "sources":row["sources"],
                                "recommended_fix":FIXES[row["category"]],
                                "candidate_lesson":LESSON_CANDIDATES[row["category"]],
                                "caution":"Unverified QA text: do not use in prompts or deploy as code."}
                    if pending.exists():
                        old = getjson(pending, {})
                        proposal["first_seen"] = old.get("first_seen", ts)
                    atomic(pending, proposal)
                elif pending.exists():
                    old = getjson(pending, {})
                    if old.get("status") != "closed":
                        old.update(status="retested_pass_needs_review", last_retest=ts)
                        atomic(pending, old)
        os.chmod(LEDGER, 0o600)
        result = {"imported_at":ts,"report":digest[:20],"cases":len(cases),
                  "passes":sum(r["verdict"]=="pass" for r in cases),
                  "failures":sum(r["verdict"]=="fail" for r in cases),
                  "inconclusive":sum(r["verdict"]=="inconclusive" for r in cases)}
        seen[digest]=result
        atomic(INDEX, seen)
        summarize()
        return result


def summarize():
    entries = [json.loads(s) for s in LEDGER.read_text(encoding="utf-8").splitlines() if s.strip()] if LEDGER.exists() else []
    recent = {}
    for row in entries:
        recent[row["id"]]=row
    pending = [getjson(p, {}) for p in sorted(PENDING.glob("*.json"))]
    open_cases = [p for p in pending if p.get("status") != "closed"]
    lines=["# ICONIC QA intake", "", "Generated " + now(), "",
           "- Recorded attempts: %d" % len(entries),
           "- Distinct question identities: %d" % len(recent),
           "- Latest graded passes: %d" % sum(x["verdict"]=="pass" for x in recent.values()),
           "- Latest graded failures: %d" % sum(x["verdict"]=="fail" for x in recent.values()),
           "- Open findings (including retest-only closures pending review): %d" % len(open_cases), "",
           "## Pending fixes", ""]
    for p in open_cases[:100]:
        lines.append("- %s | %s | %s | %s" % (p["id"],p["status"],p["category"],p["question"][:140].replace("\n"," ")))
    STATE.mkdir(parents=True, exist_ok=True)
    tmp = STATE / "qa-summary.md.tmp"
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, STATE / "qa-summary.md")
    return "\n".join(lines[:9])


def scan_inbox():
    private_dir(INBOX)
    for item in sorted(INBOX.glob("*.json")):
        try:
            result=ingest(item)
            private_dir(ARCHIVE)
            item.unlink()
            print("INGESTED",item.name,result)
        except Exception as exc:
            private_dir(REJECTED)
            if item.is_symlink():
                item.unlink()
            else:
                shutil.move(str(item), str(REJECTED / (item.name + ".invalid")))
            print("REJECTED",item.name,str(exc),file=sys.stderr)


def promote(case_id, source, evidence, top=False):
    """Promote reviewer-specified, file-verified assertions into permanent deployment tests.
    This must run in an isolated working branch; never invoked during inbox scanning.
    """
    if not evidence or len(evidence)>8 or any(len(x)>300 or not x for x in evidence):
        raise ValueError("provide 1-8 exact pieces of documentary evidence")
    with lock():
        if not LEDGER.exists():
            raise ValueError("no QA results imported yet")
        candidates = [json.loads(s) for s in LEDGER.read_text(encoding="utf-8").splitlines() if s.strip()]
        case = next((r for r in reversed(candidates) if r["id"]==case_id),None)
        if not case:
            raise ValueError("case ID not found in ledger")
        workspace = case["workspace"]
        base = (ROOT/"data"/workspace).resolve()
        real = (base/source).resolve()
        if not real.is_relative_to(base) or not real.is_file():
            raise ValueError("evidence must be a file inside the chosen sample workspace")
        content = real.read_text(encoding="utf-8")
        if any(text not in content for text in evidence):
            raise ValueError("a proposed evidence value was not actually found in the source file")
        # Test the actual retrieval path before adding this assertion.
        os.environ["ICONIC_DATA"]=str(ROOT/"data")
        import server
        server.start_offline(detect_model=False)
        sources=server.find_sources(server.WORKSPACES[workspace],case["question"],[])
        matched=[s for s in sources if s["rel"]==source and all(x in s["chunk"] for x in evidence)]
        if not matched or (top and matched[0]["n"]!=1):
            raise ValueError("retrieval does not currently meet the proposed acceptance criterion")
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT,
                                text=True, capture_output=True, check=True).stdout.strip()
        if branch in ("dashboard", "main", "master", ""):
            raise ValueError("approve source cases in an isolated feature branch, not production")
        approved = getjson(APPROVED, {"cases":[]})
        entry={"id":case_id,"workspace":workspace,"question":case["question"],
               "source_rel":source,"evidence":evidence,"require_first":bool(top),"reviewed_at":now()}
        approved["cases"]=[r for r in approved["cases"] if r["id"]!=case_id]+[entry]
        atomic(APPROVED,approved)
        pending=PENDING/(case_id+".json")
        if pending.exists():
            obj=getjson(pending,{})
            obj.update(status="source_regression_approved",reviewed_at=now())
            atomic(pending,obj)
        print("PROMOTED SOURCE REGRESSION",case_id,"->",APPROVED)


def close(case_id, why):
    if len(why)<12:
        raise ValueError("provide a meaningful reason for closing the finding")
    with lock():
        pending=PENDING/(case_id+".json")
        if not pending.exists():
            raise ValueError("no pending item with this ID")
        obj=getjson(pending,{})
        obj.update(status="closed",closed_at=now(),closure_reason=why[:1000])
        atomic(pending,obj)
        summarize()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    a=sub.add_parser("ingest",help="Record an independent QA JSON report locally and triage failures");a.add_argument("file")
    sub.add_parser("scan-inbox",help="Consume JSON reports dropped into the local QA inbox")
    sub.add_parser("report",help="Summarize attempted cases and queued findings")
    a=sub.add_parser("promote",help="Approve a source-verified failure as a deployment regression");a.add_argument("id");a.add_argument("--source",required=True);a.add_argument("--evidence",action="append",required=True);a.add_argument("--first",action="store_true")
    a=sub.add_parser("close",help="Close a reviewed finding with an explicit recorded explanation");a.add_argument("id");a.add_argument("--reason",required=True)
    args=parser.parse_args()
    try:
        if args.command=="ingest":print(json.dumps(ingest(args.file),indent=2))
        elif args.command=="scan-inbox":scan_inbox()
        elif args.command=="report":print(summarize())
        elif args.command=="promote":promote(args.id,args.source,args.evidence,args.first)
        elif args.command=="close":close(args.id,args.reason)
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
        parser.exit(2,"QA bridge error: %s\n"%e)

if __name__=="__main__":main()
