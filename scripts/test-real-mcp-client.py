#!/usr/bin/env python3
"""External MCP SDK smoke, business execution and NO-CHARGE buyer-readiness test.

Runs from GitHub's unaffiliated network. Fictional/public inputs only.
NEVER submits a payment request or calls order/payment-creating tools.
Problem-first organic search is checked in a separate workflow job.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen
from mcp.client import Client

BASE = "https://patrick-beastmaster.tailf32530.ts.net"
SITE = "https://iconic.onl"
OFFER = "dataset-diff-report"
REQUIRED = {
    "marketplace": {
        "marketplace_describe", "marketplace_list_offers", "marketplace_quote",
        "marketplace_preflight", "marketplace_mpp_purchase_instructions",
        "marketplace_prepare_mpp_checkout", "marketplace_reconcile_synthetic",
        "marketplace_analyze_public_inventory", "marketplace_find_agents",
        "marketplace_agent_profile",
    },
    "reserve": {
        "reserve_describe", "reserve_assess", "reserve_demo",
        "reserve_sandbox_start", "reserve_pass_status",
    },
}

def get_json(url):
    with urlopen(Request(url, headers={"User-Agent": "ICONIC-independent-test/2.0"}), timeout=15) as r:
        data = json.load(r)
    assert isinstance(data, dict), f"Expected JSON object: {url}"
    return data

def explain(error):
    if isinstance(error, BaseExceptionGroup):
        return "; ".join(explain(inner) for inner in error.exceptions)
    return f"{type(error).__name__}: {error}"

async def invoke(client, name, params):
    result = await client.call_tool(name, params)
    assert not result.is_error, f"{name} returned an MCP error: {result}"
    blocks = [b.text for b in result.content if isinstance(getattr(b, "text", None), str)]
    data = json.loads(blocks[0]) if blocks else getattr(result, "structured_content", None)
    assert isinstance(data, dict) and not data.get("error"), f"{name}: {data}"
    return data

async def contract(client, service):
    listed = (await client.list_tools()).tools
    names = {tool.name for tool in listed}
    assert len(names) == len(listed), f"{service}: duplicate tools"
    assert REQUIRED[service] <= names, f"{service}: missing capabilities {sorted(REQUIRED[service] - names)}"
    for tool in listed:
        assert tool.description and isinstance(tool.input_schema, dict), f"{service}: missing metadata {tool.name}"
    manifest = await asyncio.to_thread(get_json, f"{SITE}/agents/{service}/manifest.json")
    advertised = set(manifest["tools" if service == "marketplace" else "public_tools"])
    # Compare capabilities with what agents are told, not a hardcoded 16/17/27 count.
    assert names == advertised, (
        f"{service} discovery metadata drift: "
        f"advertised_but_missing={sorted(advertised - names)} "
        f"live_but_unadvertised={sorted(names - advertised)}"
    )
    assert await invoke(client, f"{service}_describe", {})
    print(f"PASS {service}: {len(names)} described tools, public manifest parity", flush=True)

async def marketplace(client):
    sample = {"previous": [{"id": "alpha", "value": 100}, {"id": "beta", "value": 50}],
              "current": [{"id": "alpha", "value": 80}, {"id": "gamma", "value": 70}],
              "synthetic_only": True}
    result = await invoke(client, "marketplace_reconcile_synthetic", sample)
    assert result["new_only"] == ["gamma"] and result["missing_from_current"] == ["beta"]
    assert result["changes"] == [{"id": "alpha", "from": 100, "to": 80, "delta": -20}]
    assert any("not evidence of sale" in t.lower() for t in result["limitations"])
    print("PASS marketplace: fictional reconciliation, no false sale inference", flush=True)

    public = {"public_request": {"authorized_public_data": True,
              "snapshot_before": {"label": "PUBLIC_TEST_DAY1", "rows": [
                  {"stock_id": f"STK-{i}", "price_cents": 3000000 + i * 10000} for i in range(3)]},
              "snapshot_after": {"label": "PUBLIC_TEST_DAY2", "rows": [
                  {"stock_id": f"STK-{i}", "price_cents": 2900000 + i * 10000} for i in range(3)]}}}
    preview = await invoke(client, "marketplace_analyze_public_inventory", public)
    assert preview["amount_charged_cents"] == 0
    assert preview["pricing_signals"]["signals"][0]["delta_cents"] == -100000
    assert preview["independent_checks"]["pricing"]["checks_passed"] == 5
    print("PASS marketplace: no-charge public pricing analysis", flush=True)

    directory = await invoke(client, "marketplace_find_agents",
                             {"capability": "public-inventory-pricing", "limit": 10})
    assert directory["status"] in ("CURATED_DIRECTORY_EMPTY", "OPERATOR_CURATED_LOCAL_DIRECTORY")
    if directory.get("count", 0):
        identity = directory["agents"][0]["agent_id"]
        profile = await invoke(client, "marketplace_agent_profile", {"agent_id": identity})
        assert profile["agent"]["agent_id"] == identity
        assert profile["reputation_claim"] == "UNVERIFIED_OFFCHAIN_EVALUATOR_SIGNALS_NOT_ERC8004"
    print("PASS marketplace: read-only agent directory", flush=True)

    live = await asyncio.to_thread(get_json, f"{BASE}/mpp-catalog/offers")
    offer = next((x for x in live["offers"]
                  if x["offer_id"] == OFFER and x["purchasable"] is True), None)
    assert offer, f"{OFFER} is not purchasable on the live authoritative catalog"
    price = offer["approved_price_cents"]
    assert type(price) is int and price > 0 and "MPP_STRIPE_SPT" in offer["payment_options"]

    listed = await invoke(client, "marketplace_list_offers", {})
    assert OFFER in {x["offer_id"] for x in listed["offers"]}
    quote = await invoke(client, "marketplace_quote", {"offer_id": OFFER})
    assert quote["payment_ready"] is True and quote["approved_price_cents"] == price
    assert quote["human_buyer_approval_required"] is True

    summary = "Reconcile two fictional inventory snapshots and report exact differences."
    preflight = await invoke(client, "marketplace_preflight",
                             {"offer_id": OFFER, "workflow_summary": summary})
    assert preflight["analysis_type"] == "STATIC_PREFLIGHT_NOT_A_PAID_DELIVERABLE"
    instructions = await invoke(client, "marketplace_mpp_purchase_instructions", {"offer_id": OFFER})
    expected_url = f"{BASE}/mpp-catalog/offers/{OFFER}/purchase"
    assert instructions["purchasable"] is True
    assert instructions["approved_price_cents"] == price
    assert instructions["method"] == "POST" and instructions["purchase_url"] == expected_url

    # Simulated buyer approval applies ONLY to the read-only preparation helper.
    # The fictional request body is validated locally then discarded. No POST,
    # wallet token, real authorization, order creation, settlement or delivery.
    prepared = await invoke(client, "marketplace_prepare_mpp_checkout", {
        "offer_id": OFFER, "scope_summary": summary,
        "contact_email": "ci-buyer@example.invalid",
        "buyer_authorized": True, "nonconfidential_only": True,
        "join_key": "id",
        "datasets_before": [{"id": "fake-a", "value": 100}],
        "datasets_after": [{"id": "fake-a", "value": 80}],
    })
    assert prepared["charged"] is False and prepared["amount_cents"] == price
    assert prepared["method"] == "POST"
    exact_bytes = prepared["exact_json_body"].encode("utf-8")
    body = json.loads(exact_bytes)
    assert body["offer_id"] == OFFER and body["buyer_authorized"] is True
    assert body["nonconfidential_only"] is True
    assert body["contact_email"] == "ci-buyer@example.invalid"
    assert body["datasets"]["before"] == [{"id": "fake-a", "value": 100}]
    assert body["datasets"]["after"] == [{"id": "fake-a", "value": 80}]
    dest = urlsplit(prepared["purchase_url"])
    assert dest.scheme == "https" and dest.netloc == urlsplit(BASE).netloc
    assert dest.path == urlsplit(expected_url).path
    assert parse_qs(dest.query).get("sha256") == [hashlib.sha256(exact_bytes).hexdigest()]
    print("PASS checkout: live purchasable offer, price, quote, preflight and exact SHA256-bound request prepared; NOT SUBMITTED, NOT PAID", flush=True)

async def reserve(client):
    fictional = {"business_type": "Fictional auto dealership",
                 "problem": "Fictional competitor pricing changes need evidence verification",
                 "systems": ["fictional inventory", "synthetic price history"],
                 "recurring_workflow": "Daily synthetic inventory delta review",
                 "measurable_outcome": "Count of verified price changes with evidence"}
    report = await invoke(client, "reserve_assess", fictional)
    assert report["transaction"]["amount_charged_cents"] == 0
    assert report["transaction"]["payment_status"] == "NOT_REQUIRED"
    assert report["brief_for_human"]["indicative_price"]["can_purchase_now"] is False
    assert fictional["recurring_workflow"] in json.dumps(report)
    demo = await invoke(client, "reserve_demo", {})
    assert demo["mode"] == "EPHEMERAL_SYNTHETIC_NO_CUSTOMER_DATA"
    assert demo["source_memory"] and demo["outcome_reported"]
    print("PASS reserve: fictional assessment plus ephemeral outcome-ledger demo, $0 charged", flush=True)

async def verify(service):
    url = f"{BASE}/{service}/mcp"
    print(f"TEST {service}: {url}", flush=True)
    async with Client(url) as client:
        print(f"CONNECTED {service}: protocol {client.protocol_version}", flush=True)
        await contract(client, service)
        if service == "marketplace":
            await marketplace(client)
        else:
            await reserve(client)

async def main():
    failed = []
    for service in ("marketplace", "reserve"):
        try:
            await asyncio.wait_for(verify(service), timeout=75)
        except Exception as error:
            print(f"FAIL {service}: {explain(error)}", flush=True)
            failed.append(service)
    if failed:
        print(f"RESULT FAIL: {', '.join(failed)}", flush=True)
        return 1
    print("RESULT PASS: remote SDK, published discovery contract, useful tools, no-charge checkout preparation", flush=True)
    print("NOT PROVEN HERE: organic search, paid settlement, or paid fulfillment", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
