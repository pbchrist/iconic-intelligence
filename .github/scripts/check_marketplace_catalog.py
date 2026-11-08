"""Verify published marketplace discovery matches its static seven-offer contract."""
import json
from pathlib import Path
from html.parser import HTMLParser
root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/"agents/marketplace/manifest.json").read_text())
offers=json.loads((root/"agents/marketplace/offers.json").read_text())
assert manifest["offer_count"]==7 and len(manifest["offer_ids"])==7
assert len(manifest["tools"])==9
assert {o["offer_id"] for o in offers["offers"]}==set(manifest["offer_ids"])
assert all(o["approved_price_cents"] is None and not o["purchasable"]
           for o in offers["offers"]), "Static catalog must not invent payable prices"
assert manifest["checkout_enabled"] is False
assert manifest["canonical_manifest"]=="https://iconic.onl/agents/marketplace/manifest.json"
assert manifest["remote_mcp_url"]=="https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp"
page=(root/"agents/marketplace/index.html").read_text()
HTMLParser().feed(page)
for name in ("Talent Mapping","Market Watch","Data Reconciliation","Code Assurance",
             "Agent Assurance","Infrastructure Audit","Agent Integration"):
    assert name in page,name
assert "Paid checkout is not yet enabled" in page
for path in ("llms.txt","llms-full.txt","ai/agent-evaluation.md"):
    text=(root/path).read_text()
    assert "https://iconic.onl/agents/marketplace/" in text,path
    assert manifest["remote_mcp_url"] in text,path
print("MARKETPLACE_SITE_CONSISTENCY_OK",manifest["offer_count"],"offers",len(manifest["tools"]),"MCP tools, checkout OFF")
