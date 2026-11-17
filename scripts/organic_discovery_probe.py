#!/usr/bin/env python3
"""Read-only, problem-first independent discovery probe.

Searches do NOT contain the target brand/URL/repository; branded queries are
separate controls. This tests discoverability in public search and the official
MCP Registry, not actual autonomous LLM selection or a completed purchase.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import sys
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

QUERIES = [
    "MCP agent service reconcile two inventory snapshots detect price changes",
    "AI agent tool public vehicle inventory pricing pattern evidence report",
    "MCP service private verified business decision outcome memory",
]
BING_CONTROL = "ICONIC agent marketplace MCP data reconciliation"
REGISTRY_TERMS = ["inventory", "reconciliation", "verified outcomes", "business decisions"]
REGISTRY_CONTROL = "io.github.pbchrist"
REGISTRY_API = "https://registry.modelcontextprotocol.io/v0.1/servers"
TARGET_DOMAINS = {"iconic.onl", "www.iconic.onl", "patrick-beastmaster.tailf32530.ts.net"}
TARGET_SERVERS = {
    "io.github.pbchrist/iconic-agent-marketplace",
    "io.github.pbchrist/iconic-intelligence-reserve",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ICONIC-independent-discovery-audit/2.0)"}

def retrieve(url):
    with urlopen(Request(url, headers=HEADERS), timeout=12) as response:
        return response.read(250000)

def bing_search(query, maximum=10):
    url = "https://www.bing.com/search?" + urlencode({"q": query, "format": "rss"})
    root = ET.fromstring(retrieve(url))
    results = []
    for rank, el in enumerate(root.findall("./channel/item")[:maximum], 1):
        link = (el.findtext("link") or "").strip()
        domain = (urlsplit(link).hostname or "").lower()
        results.append({"rank": rank, "domain": domain, "iconic_match": domain in TARGET_DOMAINS})
    if not results:
        raise RuntimeError("Bing returned no RSS results; cannot score as absent")
    return results

def registry_search(term, maximum=10):
    url = REGISTRY_API + "?" + urlencode({"search": term, "limit": maximum})
    response = json.loads(retrieve(url))
    if not isinstance(response.get("servers"), list):
        raise ValueError("Registry response lacked servers array")
    return [
        {"rank": rank, "name": item.get("server", {}).get("name", ""),
         "iconic_match": item.get("server", {}).get("name", "") in TARGET_SERVERS}
        for rank, item in enumerate(response["servers"][:maximum], 1)
    ]

def probe(source, query, control):
    try:
        matches = (bing_search if source == "bing" else registry_search)(query)
        ranks = [item["rank"] for item in matches if item["iconic_match"]]
        return {
            "query": query, "control": control, "status": "SEARCH_RESULTS_RETURNED",
            "result_count": len(matches), "iconic_rank": min(ranks) if ranks else None,
            "top_domains" if source == "bing" else "top_server_names":
                [item.get("domain", item.get("name", "")) for item in matches[:5]],
        }
    except Exception as exc:
        return {"query": query, "control": control, "status": "UNSCORED_PROVIDER_ERROR",
                "error": str(exc)[:200]}

def summarize(probes):
    unbranded = [p for p in probes if not p["control"]]
    scored = [p for p in unbranded if p["status"] == "SEARCH_RESULTS_RETURNED"]
    return {
        "scored_queries": len(scored),
        "unbranded_top_ten_hits": sum(p["iconic_rank"] is not None for p in scored),
        "branded_control_found": any(
            p["control"] and p.get("iconic_rank") is not None for p in probes),
        "probes": probes,
    }

def audit():
    bing = summarize([probe("bing", q, False) for q in QUERIES]
                     + [probe("bing", BING_CONTROL, True)])
    registry = summarize([probe("registry", q, False) for q in REGISTRY_TERMS]
                         + [probe("registry", REGISTRY_CONTROL, True)])
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": "First 10 unbranded results, Bing RSS and official MCP Registry search",
        "query_treatment": "Problem-first searches unbranded; separate labeled controls",
        "scored_queries": bing["scored_queries"],
        "unbranded_queries_with_iconic_in_top_ten": bing["unbranded_top_ten_hits"],
        "bing": bing, "official_mcp_registry": registry,
        "limitations": [
            "Search-provider results depend on exact query and date",
            "Registry search is not a guarantee of LLM attention or selection",
            "A missing result does not mean the server is unregistered or unusable",
            "No payment, agent wallet, customer information or paid fulfillment involved",
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Write machine-readable results to this path")
    parser.add_argument("--require-hit", action="store_true",
                        help="Fail unless an unbranded query finds ICONIC in either search channel")
    options = parser.parse_args()
    report = audit()
    raw = json.dumps(report, indent=2, ensure_ascii=False)
    if options.output:
        from pathlib import Path
        Path(options.output).write_text(raw + "\n")
    print(raw)
    if options.require_hit:
        bing = report["bing"]
        registry = report["official_mcp_registry"]
        total_scored = bing["scored_queries"] + registry["scored_queries"]
        total_hits = bing["unbranded_top_ten_hits"] + registry["unbranded_top_ten_hits"]
        if total_scored == 0:
            print("RESULT FAIL: neither search channel could score a query", file=sys.stderr)
            sys.exit(1)
        if total_hits == 0:
            print("RESULT FAIL: zero unbranded top-ten ICONIC hits in Bing or official MCP Registry", file=sys.stderr)
            sys.exit(1)
        print("RESULT PASS: at least one unbranded top-ten result; still not proof of LLM selection")
