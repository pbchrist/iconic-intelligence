#!/usr/bin/env python3
"""Read-only ICONIC discovery contract audit. No checkout or customer data."""
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SITE = "https://iconic.onl"
REGISTRY = "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.pbchrist"
SERVICES = {
    "reserve": "https://patrick-beastmaster.tailf32530.ts.net/reserve/mcp",
    "marketplace": "https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp",
}
failures = []

def get(url):
    with urlopen(Request(url, headers={"User-Agent": "ICONIC-contract-audit/1.0"}), timeout=12) as response:
        return response.read().decode("utf-8")

def check(label, action):
    try:
        result = action()
        print("PASS", label, f"({len(result)} chars)" if isinstance(result, str) else "")
        return result
    except Exception as exc:
        failures.append(f"{label}: {exc}")
        print("FAIL", label, str(exc))
        return None

def mcp(url, method, params):
    request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    with urlopen(Request(url, data=json.dumps(request).encode(), method="POST",
                         headers={"Content-Type": "application/json",
                                  "Accept": "application/json, text/event-stream"}),
                 timeout=12) as response:
        result = json.load(response)
    if result.get("error") or result.get("result", {}).get("isError"):
        raise ValueError(str(result.get("error") or result["result"]))
    return result["result"]

def assert_true(value, message):
    if not value:
        raise AssertionError(message)
    return value

llms = check("llms.txt", lambda: get(SITE + "/llms.txt"))
check("robots.txt", lambda: get(SITE + "/robots.txt"))
check("sitemap.xml", lambda: get(SITE + "/sitemap.xml"))
reserve = check("Reserve manifest", lambda: json.loads(get(SITE + "/agents/reserve/manifest.json")))
market = check("Marketplace manifest", lambda: json.loads(get(SITE + "/agents/marketplace/manifest.json")))
for name, url in SERVICES.items():
    result = check(name + " MCP tools/list", lambda u=url: mcp(u, "tools/list", {}))
    if result:
        print("INFO", name, "tool_count", len(result.get("tools", [])))
        manifest = reserve if name == "reserve" else market
        advertised = set(manifest.get("public_tools" if name == "reserve" else "tools", [])) if manifest else set()
        actual = {tool["name"] for tool in result.get("tools", [])}
        check(name + " manifest tool parity",
              lambda a=advertised, b=actual: assert_true(a == b, f"advertised={sorted(a)} actual={sorted(b)}"))
if llms and market:
    # Only flag contradictions when statements explicitly concern Marketplace.
    section = llms.split("## ICONIC Agent-Native Marketplace", 1)
    if len(section) > 1:
        marketplace_section = section[1].split("\n## ", 1)[0]
        live = bool(market.get("checkout_enabled"))
        disabled = bool(re.search(r"NOT yet purchasable|Paid Stripe checkout is disabled|All approved prices are null",
                                  marketplace_section, re.I))
        check("Marketplace commercial state consistency",
              lambda: assert_true(not (live and disabled),
                                  "Marketplace manifest says checkout enabled, but llms.txt says disabled"))
    else:
        print("INFO", "Marketplace section not present in llms.txt; no state claim made")
if reserve:
    live_pass = check(
        "Live Reserve Pass merchant catalog",
        lambda: json.loads(get("https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog/offers/reserve-pass"))
    )
    if live_pass:
        check("Reserve Pass published paid boundaries",
              lambda: assert_true(
                  reserve.get("paid_plans_live") is True
                  and (reserve.get("paid_offer") or {}).get("offer_id") == "reserve-pass"
                  and (reserve.get("paid_offer") or {}).get("price_cents") == live_pass.get("approved_price_cents")
                  and live_pass.get("purchasable") is True
                  and live_pass.get("human_approval_required") is True
                  and not any("checkout" in n or "purchase" in n for n in reserve.get("public_tools", [])),
                  "Reserve manifest, live pass price/availability, human approval, or safe MCP boundary disagree"
              ))
registry = check("Official MCP Registry search", lambda: json.loads(get(REGISTRY)))
if registry:
    names = sorted({entry.get("server", {}).get("name", "") for entry in registry.get("servers", [])})
    print("INFO registry_names", json.dumps(names))
    check("Reserve Registry listing",
          lambda: assert_true(any("pbchrist/iconic-intelligence-reserve" in n for n in names),
                              "Reserve missing from queried Registry page"))
    check("Marketplace Registry listing",
          lambda: assert_true(any("pbchrist/iconic-agent-marketplace" in n for n in names),
                              "Marketplace missing from queried Registry page"))
print("RESULT", len(failures), "failures")
sys.exit(1 if failures else 0)
