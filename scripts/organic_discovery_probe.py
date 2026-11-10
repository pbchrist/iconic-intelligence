#!/usr/bin/env python3
"""Problem-first public search discoverability probe. Read-only; no payment.

The queries intentionally do not include ICONIC, its URL or its repository.
A search result is not proof that an unaffiliated agent would install/use an MCP.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

QUERIES = [
    "MCP agent service reconcile two inventory snapshots detect price changes",
    "AI agent tool public vehicle inventory pricing pattern evidence report",
    "MCP service private verified business decision outcome memory",
]
CONTROL = "ICONIC agent marketplace MCP data reconciliation"
TARGET_DOMAINS = {"iconic.onl", "www.iconic.onl",
                  "patrick-beastmaster.tailf32530.ts.net"}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ICONIC-independent-discovery-audit/1.0)"}


def search(query, maximum=10):
    url = "https://www.bing.com/search?" + urlencode({"q": query, "format": "rss"})
    with urlopen(Request(url, headers=HEADERS), timeout=12) as response:
        payload = response.read(200000)
    root = ET.fromstring(payload)
    items = []
    for i, el in enumerate(root.findall("./channel/item")[:maximum], 1):
        link = (el.findtext("link") or "").strip()
        domain = (urlsplit(link).hostname or "").lower()
        items.append({
            "rank": i,
            "title": (el.findtext("title") or "")[:140],
            "domain": domain,
            "url": link,
            "iconic_match": domain in TARGET_DOMAINS,
        })
    if not items:
        raise RuntimeError("Search provider returned zero RSS items; cannot score as absent")
    return items


def audit():
    probes = []
    for query in QUERIES + [CONTROL]:
        try:
            items = search(query)
            matches = [r["rank"] for r in items if r["iconic_match"]]
            probes.append({
                "query": query,
                "control": query == CONTROL,
                "status": "SEARCH_RESULTS_RETURNED",
                "result_count": len(items),
                "iconic_rank": min(matches) if matches else None,
                "top_domains": [x["domain"] for x in items[:5]],
            })
        except Exception as exc:
            probes.append({"query": query, "control": query == CONTROL,
                           "status": "UNSCORED_PROVIDER_ERROR",
                           "error": str(exc)[:180]})
    unbranded = [r for r in probes if not r["control"]]
    scored = [r for r in unbranded if r["status"] == "SEARCH_RESULTS_RETURNED"]
    hits = sum(r["iconic_rank"] is not None for r in scored)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Bing RSS, first ten results per exact problem-only query",
        "query_treatment": "Unbranded except a separately labeled branded control",
        "scored_queries": len(scored),
        "unbranded_queries_with_iconic_in_top_ten": hits,
        "probes": probes,
        "limitations": [
            "One search provider and a small set of queries, not a ranking benchmark",
            "Search listing does not prove an LLM autonomously discovered or selected the service",
            "A missing result does not prove the service is unindexed everywhere",
            "No payment, MCP installation, or customer-data submission was attempted",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Write machine-readable results to this path")
    options = parser.parse_args()
    report = audit()
    raw = json.dumps(report, indent=2, ensure_ascii=False)
    if options.output:
        from pathlib import Path
        Path(options.output).write_text(raw + "\n")
    print(raw)
