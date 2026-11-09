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
