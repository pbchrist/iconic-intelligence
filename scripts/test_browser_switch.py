#!/usr/bin/env python3
"""Headless browser test: workspace transcripts survive switching and reloads.

All APIs are stubbed; no production model, visitor, data, or network requests.
"""
import contextlib
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
WSS = [
    {"id": "hollis-reyes", "name": "Hollis & Reyes LLP", "initials": "H", "documents": 1, "sample": True, "kind": "legal"},
    {"id": "northline-supply", "name": "Northline Supply Co.", "initials": "N", "documents": 1, "sample": True, "kind": "distribution"},
]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def serve():
    handler = functools.partial(Quiet, directory=str(STATIC))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def fulfill(route):
    req = route.request
    path = urlsplit(req.url).path
    params = parse_qs(urlsplit(req.url).query)
    ws = params.get("ws", ["hollis-reyes"])[0]
    if path == "/api/status":
        body = {
            "model": {"online": True, "model": "Qwen3.8-27B", "private": True},
            "workspaces": WSS, "location": "mock host", "owner": "tester", "cta_url": "",
            "public": True, "tokens": 0, "questions": 0, "learned": {}, "tokens_per_second": 55,
            "uptime": 123, "now": time.time(), "web_search": False,
        }
    elif path == "/api/workspace":
        w = next((x for x in WSS if x["id"] == ws), WSS[0])
        body = dict(w, tagline="Sandbox", docs=[], folders=[], suggestions=[], words=0,
                    passages=0, indexed_at=1)
    elif path == "/api/feed":
        body = {"status": "ready", "items": [], "generated_at": time.time(), "model": "fixture"}
    elif path == "/api/graph":
        body = {"status": "ready", "entities": [], "tunnels": [], "totals": {"here": 0, "conversations": 0}}
    elif path == "/api/doc":
        body = {"title": "Mock source", "rel": "facts.md", "date": "2026-11-06", "words": 10,
                "text": "Mock evidence for the current workspace."}
    elif path == "/api/ask":
        data = req.post_data_json
        who = data["ws"]
        msg = "Source-grounded answer for " + who + ": " + data["q"] + " [1]"
        srcs = [{"n": 1, "id": 1, "rel": "facts.md", "folder": "general", "date": "2026-11-06",
                 "title": "Mock source", "snippet": "Mock evidence", "web": False}]
        result = {"ms": 150, "tps": 42, "location": "mock host", "private": True, "learned": {"new": [], "added": 0}}
        payload = ("event: sources\ndata: " + json.dumps(srcs) + "\n\n" +
                   "event: token\ndata: " + json.dumps(msg) + "\n\n" +
                   "event: done\ndata: " + json.dumps(result) + "\n\n")
        return route.fulfill(status=200, body=payload, content_type="text/event-stream",
                             headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-store"})
    else:
        return route.fulfill(status=404, body="{}")
    route.fulfill(status=200, body=json.dumps(body), content_type="application/json")


def send(page, text):
    page.locator("#askInput").fill(text)
    page.locator("#askBtn").click()
    expect(page.locator("#convo .a-body").last).to_contain_text(text, timeout=8000)


def select(page, workspace):
    page.locator("#wsChip").click()
    page.locator('#wsMenu button[data-ws="' + workspace + '"]').click()
    expect(page.locator("#wsName")).to_have_text(next(x["name"] for x in WSS if x["id"] == workspace))


def test():
    srv = serve()
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path="/home/patrick/.local/bin/google-chrome",
                                        args=["--no-sandbox"])
            page = browser.new_page()
            page.set_default_timeout(6000)
            errors = []
            page.on("pageerror", lambda ex: errors.append(str(ex)))
            page.route("**/api/**", fulfill)
            page.goto("http://127.0.0.1:" + str(srv.server_port) + "/", wait_until="domcontentloaded")
            expect(page.locator("#wsName")).to_have_text("Hollis & Reyes LLP")
            select(page, "hollis-reyes")
            send(page, "Hollis question one")
            assert page.locator("#convo .turn").count() == 1
            select(page, "northline-supply")
            assert page.locator("#convo .turn").count() == 0
            send(page, "Northline question one")
            select(page, "hollis-reyes")
            expect(page.locator("#convo")).to_contain_text("Hollis question one")
            assert "Northline question one" not in page.locator("#convo").inner_text()
            page.reload(wait_until="domcontentloaded")
            expect(page.locator("#wsName")).to_have_text("Hollis & Reyes LLP")
            expect(page.locator("#convo")).to_contain_text("Hollis question one")
            expect(page.locator("#convo .cite").first).to_be_visible()
            page.locator("#convo .cite").first.click()
            expect(page.locator("#drawer")).to_have_class("drawer open")
            page.locator("#dClose").click()
            select(page, "northline-supply")
            expect(page.locator("#convo")).to_contain_text("Northline question one")
            assert "Hollis question one" not in page.locator("#convo").inner_text()
            print("BROWSER_PASS: two workspaces; switch, reload, source clicks and transcript isolation")
            if errors:
                raise AssertionError("Browser JS errors: " + repr(errors[:5]))
            browser.close()
    finally:
        srv.shutdown()
        srv.server_close()


if __name__ == "__main__":
    test()
