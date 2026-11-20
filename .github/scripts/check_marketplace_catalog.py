"""Validate the nine-offer public catalog, purchase boundaries, and the visible page layout.

This is a metadata/HTML check only. It does not initiate checkout or exercise payment rails.
"""
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / "agents/marketplace/manifest.json").read_text())
catalog = json.loads((ROOT / "agents/marketplace/offers.json").read_text())
offers = {o["offer_id"]: o for o in catalog["offers"]}

ACTIVE = {
    "dataset-diff-report": 2900,
    "selection-test": 4900,
    "reserve-pass": 1900,
}
CUSTOM = {
    "agent-reliability-evidence-audit",
    "agent-readiness",
    "code-risk-review",
    "ai-feasibility",
    "competitor-change-brief",
    "role-talent-map",
}

assert manifest["offer_count"] == catalog["offer_count"] == len(offers) == 9
assert manifest["original_specialist_offer_count"] == 7
assert manifest["purchasable_offer_count"] == len(ACTIVE) == 3
assert set(manifest["purchasable_offer_ids"]) == set(ACTIVE)
assert set(manifest["offer_ids"]) == set(offers) == set(ACTIVE) | CUSTOM
assert manifest["checkout_enabled"] is True
assert manifest["canonical_manifest"] == "https://iconic.onl/agents/marketplace/manifest.json"
assert manifest["remote_mcp_url"] == "https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp"
assert manifest["tool_count"] == len(manifest["tools"]) == 17

for offer_id, cents in ACTIVE.items():
    offer = offers[offer_id]
    assert offer["purchasable"] is True, offer_id
    assert offer["approved_price_cents"] == cents, offer_id
    assert offer["fulfillment_available"] is True, offer_id
for offer_id in CUSTOM:
    offer = offers[offer_id]
    assert offer["purchasable"] is False, offer_id
    assert offer["fulfillment_available"] is False, offer_id


class CatalogHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section = None
        self.live_cards = 0
        self.custom_cards = 0
        self.inline_checkout_cards = 0
        self.inquiry_links = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("id") in {"offers", "custom"}:
            self.section = a["id"]
        if tag == "article":
            classes = a.get("class", "").split()
            if self.section == "offers" and "product" in classes:
                self.live_cards += 1
            elif self.section == "custom" and "product" in classes:
                self.custom_cards += 1
            if a.get("data-automated-checkout") == "true":
                self.inline_checkout_cards += 1
        if tag == "a" and self.section == "custom" and "inquiry-action" in a.get("class", "").split():
            self.inquiry_links += 1

    def handle_endtag(self, tag):
        if tag == "section":
            self.section = None


page = (ROOT / "agents/marketplace/index.html").read_text()
HTMLParser().feed(page)
parsed = CatalogHTML()
parsed.feed(page)
assert (parsed.live_cards, parsed.custom_cards) == (3, 6), (parsed.live_cards, parsed.custom_cards)
assert parsed.inline_checkout_cards == 1
assert parsed.inquiry_links == 6
assert "The six custom engagements cannot be purchased online" not in page  # old wording removed
hub = (ROOT / "agents/index.html").read_text()
assert 'id="reserve"' in hub and 'id="offers"' in hub and 'id="custom"' in hub
assert "Three purchasable products · Six custom services." in hub
assert hub.count('class="product"') == 3
assert hub.count('class="product custom-product"') == 6

buy_js = (ROOT / "agents/marketplace/buy.js").read_text()
assert "'.product[data-automated-checkout=" in buy_js
assert 'selection-test' in offers and 'reserve-pass' in offers
reserve_css = (ROOT / "agents/reserve/reserve.css").read_text()
assert "repeat(auto-fit, minmax(min(100%, 245px), 1fr))" in reserve_css
assert "white-space: nowrap" in reserve_css

for ref in ("llms.txt", "llms-full.txt", "ai/agent-evaluation.md"):
    text = (ROOT / ref).read_text()
    assert "https://iconic.onl/agents/marketplace/" in text, ref
    assert manifest["remote_mcp_url"] in text, ref

print("MARKETPLACE_SITE_CONSISTENCY_OK", len(offers), "offers", len(ACTIVE), "purchasable", len(CUSTOM), "custom")
