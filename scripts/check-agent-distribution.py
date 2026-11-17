#!/usr/bin/env python3
"""Check genuine published distribution endpoints; no search-ranking theater.

The official MCP Registry does NAME-SUBSTRING filtering only. Its "search"
endpoint cannot establish semantic, problem-first discovery. This check only
proves that both versioned ICONIC listings are active, publicly retrievable
and point at the independently tested MCP endpoints. It does not claim that
ChatGPT/Claude list ICONIC, that an agent chooses it, or that a payment settles.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

BASE = "https://registry.modelcontextprotocol.io/v0.1/servers/"
DOMAIN = "iconic.onl"
SERVICES = {
    "marketplace": {
        "registry_name": "io.github.pbchrist/iconic-agent-marketplace",
        "mcp_url": "https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp",
        "manifest": "https://iconic.onl/agents/marketplace/manifest.json",
    },
    "reserve": {
        "registry_name": "io.github.pbchrist/iconic-intelligence-reserve",
        "mcp_url": "https://patrick-beastmaster.tailf32530.ts.net/reserve/mcp",
        "manifest": "https://iconic.onl/agents/reserve/manifest.json",
    },
}


def fetch(url):
    req = Request(url, headers={"User-Agent": "ICONIC-agent-distribution-contract/1.0"})
    with urlopen(req, timeout=15) as response:
        return response.read(200000)


def verify(label, config):
    name = config["registry_name"]
    url = BASE + quote(name, safe="") + "/versions/latest"
    record = json.loads(fetch(url))
    server = record["server"]
    meta = record["_meta"]["io.modelcontextprotocol.registry/official"]
    assert server["name"] == name, f"{label}: wrong name"
    assert meta["status"] == "active", f"{label}: Registry status {meta['status']}"
    assert meta["isLatest"] is True, f"{label}: not the latest version"
    assert len(server.get("description", "").strip()) >= 30, f"{label}: no useful description"
    assert server.get("title", "").strip(), f"{label}: missing title"
    assert any(r.get("type") == "streamable-http" and r.get("url") == config["mcp_url"]
               for r in server.get("remotes", [])), f"{label}: registry points to wrong MCP URL"
    homepage = server.get("websiteUrl", "")
    assert urlparse(homepage).hostname == DOMAIN, f"{label}: website on unexpected domain"
    fetch(homepage)
    manifest = json.loads(fetch(config["manifest"]))
    assert (manifest["remote_mcp_url"] if label == "marketplace"
            else manifest["interfaces"]["remote_mcp"]) == config["mcp_url"], (
                f"{label}: live advertised remote differs from registered remote"
            )
    return {
        "service": label,
        "registry_name": name,
        "registry_version": server["version"],
        "status": meta["status"],
        "website_url": homepage,
        "mcp_url": config["mcp_url"],
        "pass": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="distribution-evidence.json")
    args = parser.parse_args()
    results = []
    for label, config in SERVICES.items():
        try:
            row = verify(label, config)
            print(f"PASS {label}: published {row['registry_version']} active, public endpoint correct", flush=True)
        except Exception as exc:
            row = {"service": label, "pass": False, "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL {label}: {row['error']}", flush=True)
        results.append(row)
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Official registry presence, active latest-version metadata, reachable website, manifest parity",
        "official_registry_search_limitation": "Search is substring-only on server NAME, not descriptions or capabilities",
        "not_tested": [
            "Unprompted selection by ChatGPT/Claude or third-party agents",
            "Placement in ChatGPT or Claude app directories",
            "Real-money settlement and delivery",
        ],
        "results": results,
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print("RESULT", "PASS" if all(x["pass"] for x in results) else "FAIL", flush=True)
    return 0 if all(x["pass"] for x in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
