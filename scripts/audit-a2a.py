#!/usr/bin/env python3
"""Live, no-charge A2A interoperability smoke test. Does not initiate payment."""
import json
from urllib.request import Request, urlopen

CANONICAL = "https://iconic.onl/.well-known/agent-card.json"
REMOTE = "https://patrick-beastmaster.tailf32530.ts.net/a2a"

def get(url):
    with urlopen(url, timeout=12) as response:
        return json.load(response)

def rpc(method, params, request_id=1):
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}).encode()
    with urlopen(Request(REMOTE + "/", data=data, headers={"Content-Type": "application/json"}), timeout=12) as response:
        return json.load(response)

def main():
    card = get(CANONICAL)
    assert card["url"] == REMOTE, "Canonical card URL does not match deployed endpoint"
    assert card["preferredTransport"] == "JSONRPC"
    assert card["protocolVersion"] == "0.3.0"
    assert get(REMOTE + "/healthz")["ok"]
    live_card = get(REMOTE + "/.well-known/agent-card.json")
    assert live_card == card, "Canonical card differs from live service card"
    request = {"message": {"role": "user", "parts": [{"kind": "text", "text": "Show the seven business services"}]}}
    answer = rpc("message/send", request)
    task = answer["result"]
    assert task["kind"] == "task" and task["status"]["state"] == "completed"
    assert "7 specialist offers" in task["artifacts"][0]["parts"][0]["text"]
    followup = rpc("tasks/get", {"id": task["id"]}, 2)
    assert followup["result"]["id"] == task["id"]
    assert rpc("purchase", {}, 3)["error"]["code"] == -32601
    assert rpc("message/send", {"message": {"role": "user", "parts": [{"kind": "file", "file": {}}]}}, 4)["error"]["code"] == -32602
    print("A2A PASS: canonical/live card parity, health, message/send, tasks/get, no purchase, reject file inputs")

if __name__ == "__main__":
    main()
