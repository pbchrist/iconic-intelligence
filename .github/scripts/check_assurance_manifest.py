"""Check canonical Agent Assurance catalog matches current MCP service contract.

Local pre-publication check. Do not pretend a public page proves paid order.
"""
from pathlib import Path
import json
from urllib.request import urlopen

root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/"agents/assurance/manifest.json").read_text(encoding="utf-8"))
assert manifest["offer_id"]=="agent-reliability-evidence-audit"
assert len(manifest["tools"])==7 and len(set(manifest["tools"]))==7
assert manifest["price"]["live_payment_enabled"] is True
assert manifest["price"]["payment_ready"] is True
assert manifest["price"]["checkout_channel"] == "marketplace"
assert manifest["price"]["standalone_checkout_enabled"] is False
assert manifest["price"]["marketplace_offer"]["approved_price_cents"] == 150000
assert manifest["price"]["marketplace_offer"]["purchasable"] is True
assert manifest["price"]["buyer_checkout_page_url"].startswith("https://iconic.onl/agents/marketplace/?offer=")
assert manifest["remote_mcp_url"]=="https://patrick-beastmaster.tailf32530.ts.net/assurance/mcp"
for relative in ("llms.txt","llms-full.txt","ai/agent-evaluation.md"):
    content=(root/relative).read_text(encoding="utf-8")
    assert "https://iconic.onl/agents/assurance/manifest.json" in content
    assert manifest["remote_mcp_url"] in content
for name in manifest["tools"]:
    assert name in (root/"ai/agent-evaluation.md").read_text()
print("AGENT_ASSURANCE_MANIFEST_LOCAL_CHECK_OK",len(manifest["tools"]),"tools; live payments via canonical Marketplace")
