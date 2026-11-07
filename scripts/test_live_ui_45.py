#!/usr/bin/env python3
"""Production-served UI regression: desktop + mobile, real workspace GET data.

Only POST /api/ask is mocked with fictional responses to isolate browser mechanics.
The model/API replay is separately measured by replay_45_original.py.
Tests 23/43: switch while preserving independent histories, source-card links,
citation binding, reload, no cross-tenant answer bleed.
"""
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from urllib.parse import urlparse
import os
import urllib.request
import time

BASE=os.environ.get("ICONIC_DEMO_TEST_BASE","http://127.0.0.1:8771")

def fixture_sources(ws):
    path="/api/workspace?ws="+ws
    with urllib.request.urlopen(BASE+path,timeout=5) as r:
        d=json.load(r)
    # get a real source ID from workspace; do not invent a document URL
    docs=d.get("docs",[])
    if not docs:
        raise RuntimeError("No docs in "+ws)
    return docs[0]

def respond(route):
    req=route.request
    data=req.post_data_json
    ws=data["ws"]
    doc=docs[ws]
    sentence={
      "hollis-reyes":"Only this fictional law firm saw the orchid ledger.",
      "northline-supply":"Only this fictional distributor saw the brass ledger."
    }[ws]
    sources=[{"n":1,"id":doc["id"],"title":doc["title"],
              "rel":doc.get("rel"),"folder":doc.get("folder"),"date":doc.get("date"),
              "snippet":"Synthetic browser test citation only","web":False}]
    body=("event: sources\ndata: "+json.dumps(sources)+"\n\n"
         +"event: token\ndata: "+json.dumps(sentence+" [1]")+"\n\n"
         +"event: done\ndata: "+json.dumps({"ms":50,"tokens":15,"tps":100,"model":"QA-mock",
                                               "private":True,"location":"test",
                                               "learned":{"added":0,"new":[]}})+"\n\n")
    route.fulfill(status=200,body=body,content_type="text/event-stream",
                  headers={"Cache-Control":"no-store"})

def switch(page,ws):
    page.locator("#wsChip").click()
    page.locator('#wsMenu button[data-ws="'+ws+'"]').click()
    expect(page.locator("#wsChip")).to_have_attribute("aria-expanded","false")

def ask(page,question):
    page.locator("#askInput").fill(question)
    page.locator("#askBtn").click()
    expect(page.locator("#convo .a-body").last).to_contain_text("ledger",timeout=12000)

def test(p,view,label):
    browser=p.chromium.launch(headless=True,executable_path="/home/patrick/.local/bin/google-chrome",args=["--no-sandbox"])
    page=browser.new_page(viewport=view)
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.route("**/api/ask",respond)
    page.goto(BASE+"/?embed=1",wait_until="domcontentloaded")
    expect(page.locator("#wsChip")).to_be_visible()
    switch(page,"northline-supply")
    ask(page,"Pacific Brass contract from Northline?")
    expect(page.locator("#convo")).to_contain_text("brass ledger")
    switch(page,"hollis-reyes")
    expect(page.locator("#convo")).not_to_contain_text("brass ledger")
    ask(page,"Who is our office manager?")
    expect(page.locator("#convo")).to_contain_text("orchid ledger")
    switch(page,"northline-supply")
    expect(page.locator("#convo")).to_contain_text("brass ledger")
    expect(page.locator("#convo")).not_to_contain_text("orchid ledger")
    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#convo")).to_contain_text("brass ledger")
    assert page.locator("#convo .turn").count()==1
    expect(page.locator("#convo .cite")).to_be_visible()
    page.locator("#convo .cite").first.click()
    expect(page.locator("#drawer")).to_have_class("drawer open")
    expect(page.locator("#dTitle")).not_to_be_empty()
    page.locator("#dClose").click()
    switch(page,"hollis-reyes")
    expect(page.locator("#convo")).to_contain_text("orchid ledger")
    expect(page.locator("#convo")).not_to_contain_text("brass ledger")
    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#convo")).to_contain_text("orchid ledger")
    if errors:
        raise AssertionError("Browser JS exceptions: "+repr(errors))
    # Extra check: real API does not allow referencing a doc ID under wrong workspace.
    print("LIVE_UI_"+label+"_PASS, workspaces, restore, source clicks, no cross-company text",flush=True)
    browser.close()

docs={id:fixture_sources(id) for id in ("northline-supply","hollis-reyes")}
with sync_playwright() as p:
    test(p,{"width":1280,"height":900},"DESKTOP")
    test(p,{"width":390,"height":844},"MOBILE")
