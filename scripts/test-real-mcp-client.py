#!/usr/bin/env python3
"""Real external-network MCP SDK integration test.
Run from a public GitHub-hosted Actions runner, not inside user's tailnet.
No customer data, checkout, or persistent writes.
"""
import asyncio
import json
import sys
from mcp.client import Client

SERVICES = {
    "marketplace": {
        "url": "https://patrick-beastmaster.tailf32530.ts.net/marketplace/mcp",
        "expected_count": 17,
        "describe": "marketplace_describe",
    },
    "reserve": {
        "url": "https://patrick-beastmaster.tailf32530.ts.net/reserve/mcp",
        "expected_count": 16,
        "describe": "reserve_describe",
    },
}

async def verify(name, config):
    print(f"TEST {name} remote={config['url']}", flush=True)
    async with Client(config["url"]) as client:
        print(f"CONNECTED {name} protocol={client.protocol_version}", flush=True)
        tools = (await client.list_tools()).tools
        names = {tool.name for tool in tools}
        print(f"TOOLS {name} count={len(names)} names={sorted(names)}", flush=True)
        assert len(names) == config["expected_count"], f"Expected {config['expected_count']} tools, got {len(names)}"
        assert config["describe"] in names
        for tool in tools:
            assert tool.description and isinstance(tool.input_schema, dict), f"{tool.name} lacks readable tool metadata"
        result = await client.call_tool(config["describe"], {})
        print(f"CALLED {name} {config['describe']} is_error={result.is_error} blocks={len(result.content)}", flush=True)
        assert not result.is_error, f"Tool reported failure: {result}"
        assert result.content or result.structured_content, "Tool returned no usable content"
        # Exercise useful synthetic business outcomes, not only metadata or connectivity.
        if name == "marketplace":
            fixture = {
                "previous": [{"id": "alpha", "value": 100}, {"id": "beta", "value": 50}],
                "current": [{"id": "alpha", "value": 80}, {"id": "gamma", "value": 70}],
                "synthetic_only": True,
            }
            result = await client.call_tool("marketplace_reconcile_synthetic", fixture)
            assert not result.is_error, f"Synthetic reconciliation error: {result}"
            report = json.loads(result.content[0].text)
            assert report["new_only"] == ["gamma"], report
            assert report["missing_from_current"] == ["beta"], report
            assert report["changes"] == [{"id": "alpha", "from": 100, "to": 80, "delta": -20}], report
            assert any("not evidence of sale" in text.lower() for text in report["limitations"])
            print("PASS marketplace: correct added/missing/delta reconciliation and no-sale-inference guard", flush=True)
            public={"public_request":{"authorized_public_data":True,
                    "snapshot_before":{"label":"PUBLIC_TEST_DAY1","rows":[
                        {"stock_id":f"STK-{i}","price_cents":3000000+i*10000}
                        for i in range(3)]},
                    "snapshot_after":{"label":"PUBLIC_TEST_DAY2","rows":[
                        {"stock_id":f"STK-{i}","price_cents":2900000+i*10000}
                        for i in range(3)]}}}
            tested=await client.call_tool("marketplace_analyze_public_inventory",public)
            assert not tested.is_error,tested
            verdict=json.loads(tested.content[0].text)
            assert verdict["amount_charged_cents"]==0
            assert verdict["pricing_signals"]["signals"][0]["delta_cents"]==-100000
            assert verdict["independent_checks"]["pricing"]["checks_passed"]==5
            print("PASS marketplace: no-charge evidence-based pricing signals; 3 identical changes independently checked",flush=True)
            matches=await client.call_tool("marketplace_find_agents",{
                "capability":"public-inventory-pricing","limit":10})
            assert not matches.is_error,matches
            found=json.loads(matches.content[0].text)
            assert found.get("status") in (
                "CURATED_DIRECTORY_EMPTY","OPERATOR_CURATED_LOCAL_DIRECTORY"), found
            if found.get("count",0)>0:
                ident=found["agents"][0]["agent_id"]
                record=await client.call_tool("marketplace_agent_profile",{"agent_id":ident})
                assert not record.is_error,record
                doc=json.loads(record.content[0].text)
                assert doc["agent"]["agent_id"]==ident
                assert doc["reputation_claim"]=="UNVERIFIED_OFFCHAIN_EVALUATOR_SIGNALS_NOT_ERC8004"
            print("PASS marketplace: operator-published read-only agent directory, zero payment",flush=True)


        if name == "reserve":
            fictional = {
                "business_type": "Fictional auto dealership",
                "problem": "Fictional competitor pricing changes need evidence verification",
                "systems": ["fictional inventory", "synthetic price history"],
                "recurring_workflow": "Daily synthetic inventory delta review",
                "measurable_outcome": "Count of verified price changes with evidence",
            }
            result = await client.call_tool("reserve_assess", fictional)
            assert not result.is_error, f"Reserve assessment error: {result}"
            report = json.loads(result.content[0].text)
            assert report["transaction"]["amount_charged_cents"] == 0, report["transaction"]
            assert report["transaction"]["payment_status"] == "NOT_REQUIRED", report["transaction"]
            assert report["brief_for_human"]["indicative_price"]["can_purchase_now"] is False
            assert "Daily synthetic inventory delta review" in json.dumps(report)
            print("PASS reserve: fictional assessment produced a bounded recommendation at $0, no paid plan", flush=True)
        # Critically do not call any tools capable of initiating a checkout.
        print(f"PASS {name}: initialized, inspected metadata, invoked safe read-only describe", flush=True)

async def main():
    failed = []
    for name, config in SERVICES.items():
        try:
            await asyncio.wait_for(verify(name, config), timeout=45)
        except Exception as error:
            print(f"FAIL {name}: {type(error).__name__}: {error}", flush=True)
            failed.append(name)
    if failed:
        print(f"RESULT FAIL: {', '.join(failed)}", flush=True)
        sys.exit(1)
    print("RESULT PASS: both servers remotely usable with official independent Python MCP client", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
