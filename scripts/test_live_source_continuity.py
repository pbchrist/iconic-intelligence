#!/usr/bin/env python3
"""Real browser/model regression for source continuity, privacy and creative mode.

Tests actual Qwen on the untouched 3090 through isolated ICONIC staging.
No mock /api/ask requests, no model changes, no production deploy.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

BASE=os.environ.get("ICONIC_DEMO_TEST_BASE","http://127.0.0.1:8797")
OUT=Path(os.environ.get("ICONIC_RELIABILITY_BROWSER_OUT",
    "/tmp/iconic-reliability-rootcause-browser-2026-11-07.json"))


def switch(page,wid,name):
    page.locator("#wsChip").click()
    page.locator('#wsMenu [data-ws="'+wid+'"]').click()
    expect(page.locator("#wsName")).to_contain_text(name,timeout=13000)


def ask(page,q):
    old=page.locator("#convo .turn").count()
    page.locator("#askInput").fill(q)
    page.locator("#askBtn").click()
    expect(page.locator("#convo .turn")).to_have_count(old+1,timeout=22000)
    expect(page.locator("#askBtn")).to_be_enabled(timeout=60000)
    last=page.locator("#convo .turn").last
    answer=last.locator(".a-body").inner_text()
    refs=[]
    for item in last.locator(".src").all():
        refs.append({"n":int(item.get_attribute("data-n")),
                     "title":item.locator("strong").inner_text()})
    print("ASK",repr(q),"ANSWER",answer[:180].replace("\n"," | "),
          "SOURCES",refs[:5],flush=True)
    return {"question":q,"answer":answer,"source_cards":refs}


result=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,
        executable_path="/home/patrick/.local/bin/google-chrome",
        args=["--no-sandbox"])
    for width,height in [(1280,850),(390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height})
        js_errors=[]
        page.on("pageerror",lambda e:js_errors.append(str(e)))
        page.goto(BASE+"/?embed=1",wait_until="domcontentloaded",timeout=18000)
        expect(page.locator("#wsChip")).to_be_visible(timeout=16000)
        switch(page,"northline-supply","Northline")
        first=ask(page,
            "Where does the $7,030 freight estimate come from, "
            "and how does the vendor scorecard rate Pacific Brass?")
        card=next((x for x in first["source_cards"]
                   if "scorecard" in x["title"].lower()),None)
        assert card is not None, "Initial source card missing vendor scorecard"
        # Actual source label persists across a full browser reload.
        page.reload(wait_until="domcontentloaded",timeout=18000)
        expect(page.locator("#convo .turn")).to_have_count(1,timeout=15000)
        challenge="You cited source ["+str(card["n"])+"]. Show the exact supporting sentence in that source."
        follow=ask(page,challenge)
        assert any("scorecard" in x["title"].lower() for x in follow["source_cards"]),follow
        assert "97%" in follow["answer"] and "3%" in follow["answer"],follow
        assert "$7,030" not in follow["answer"] or "freight" in follow["answer"]
        # Harmless creative prompt is NOT business intelligence: no source cards.
        creative=ask(page,"Write a four-line poem about cats.")
        assert len(creative["source_cards"])==0,creative
        assert "Pacific Brass" not in creative["answer"],creative
        assert len([line for line in creative["answer"].splitlines() if line.strip()])>=4,creative
        switch(page,"hollis-reyes","Hollis")
        expect(page.locator("#convo .turn")).to_have_count(0,timeout=12000)
        missing=ask(page,challenge)
        assert len(missing["source_cards"])==0,missing
        assert "97%" not in missing["answer"] and "Pacific Brass" not in missing["answer"],missing
        assert not js_errors,js_errors
        result.append({"viewport":width,"initial":first,"after_reload":follow,
                       "creative":creative,"cross_workspace_challenge":missing,
                       "script_errors":js_errors,"pass":True})
        print("REAL_SOURCE_CONTINUITY_BROWSER_PASS",width,flush=True)
        page.close()
    browser.close()
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({"schema":"iconic-real-source-continuity-v1",
                           "url":BASE,"results":result},indent=2)+"\n")
OUT.chmod(0o600)
print("SAVED",OUT,flush=True)
