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
        "expected_count": 14,
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
