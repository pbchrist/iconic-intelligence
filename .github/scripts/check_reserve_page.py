"""Keep the ICONIC Reserve agent page synchronized with its pinned MCP manifest.

Pages currently publishes a static snapshot of an independently hosted MCP server.
Every change to advertised tool count/names must ship the matching manifest.
Run locally and in the Pages publishing workflow.
"""
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/"agents/reserve/manifest.json").read_text(encoding="utf-8"))
page=(root/"agents/reserve/index.html").read_text(encoding="utf-8")
names=manifest["public_tools"]
listed=re.findall(r'<li><code>(reserve_[a-z0-9_]+)</code><span>',page)

assert names, "No manifest tools"
assert len(names)==len(set(names)), "Duplicate manifest tools"
assert len(listed)==len(set(listed)), "Duplicate page tool names"
assert set(listed)==set(names), f"Page/manifest discrepancy: missing={set(names)-set(listed)}, extra={set(listed)-set(names)}"
assert f"{len(names)} LIVE MCP TOOLS" in page, "Outdated live tool count in hero"
assert f"SEE ALL {len(names)} TOOL SCHEMAS" in page, "Outdated schema call to action"
assert manifest["interfaces"]["remote_mcp"] in page, "Incorrect MCP endpoint"
assert "reserve_sandbox_start" in listed and "reserve_sandbox_evaluate" in listed, "Agent-operated sandbox absent"
assert "automated purchasing is not live" in page.lower(), "Missing plain-language purchase availability disclosure"
assert "A real company Reserve is not available for automatic purchase" in page, "Missing production access boundary"
assert page.index("16 LIVE MCP TOOLS") < page.index("A real company Reserve is not available"), "Lead with working product capabilities"
print(f"RESERVE_PAGE_CHECK_OK: {len(names)} live tools, complete list, correct MCP endpoint and truthful availability")
