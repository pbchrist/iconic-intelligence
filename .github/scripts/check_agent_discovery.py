#!/usr/bin/env python3
"""Offline guardrails for ICONIC's public agent discovery pages."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/agents/": "agents/index.html",
    "/agents/data-reconciliation/": "agents/data-reconciliation/index.html",
    "/agents/assurance/": "agents/assurance/index.html",
}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"a", "link"}:
            value = dict(attrs).get("href")
            if value:
                self.urls.append(value)

def local_path(url: str) -> Path | None:
    if not url.startswith("/") or url.startswith("//"):
        return None
    path = urlsplit(url).path.lstrip("/")
    if not path or path.endswith("/"):
        path += "index.html"
    return ROOT / path

def check() -> None:
    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = {el.text for el in sitemap.iter(f"{namespace}loc")}
    for url_path, relative_file in PAGES.items():
        page = ROOT / relative_file
        html = page.read_text(encoding="utf-8")
        canonical = f"https://iconic.onl{url_path}"
        assert canonical in locs, f"Missing sitemap entry: {canonical}"
        assert f'<link rel="canonical" href="{canonical}">' in html, f"Missing canonical: {relative_file}"
        assert '<meta name="description"' in html, f"Missing description: {relative_file}"
        assert '<h1>' in html, f"Missing H1: {relative_file}"
        scripts = re.findall(r'<script type="application/ld[+]json">(.*?)</script>', html, re.S)
        assert scripts, f"Missing JSON-LD: {relative_file}"
        for script in scripts:
            data = json.loads(script)
            assert data["@context"] == "https://schema.org"
        parser = Links()
        parser.feed(html)
        for url in parser.urls:
            local = local_path(url)
            if local is not None:
                assert local.is_file(), f"Broken local link {url} in {relative_file}"
    hub = (ROOT / "agents/index.html").read_text(encoding="utf-8")
    assert "Paid checkout for the seven-service marketplace is not enabled" not in hub, "Stale Marketplace checkout claim in hub"
    assert "Seven Marketplace offers now support authorized checkout" in hub, "Marketplace checkout status missing from hub"
    for path in PAGES:
        assert f'href="{path}"' in hub or path == "/agents/", f"Hub missing {path}"
    for page in ("agents/data-reconciliation/index.html", "agents/assurance/index.html"):
        text = (ROOT / page).read_text(encoding="utf-8").lower()
        assert "not yet" in text or "not currently" in text, f"Missing payment disclaimer: {page}"
    for path in PAGES:
        assert f"https://iconic.onl{path}" in (ROOT / "llms.txt").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "agents/marketplace/manifest.json").read_text(encoding="utf-8"))
    assert manifest["checkout_enabled"] is True, "Marketplace checkout state unexpectedly changed"
    assert manifest["tool_count"] == len(manifest["tools"]) == 15, "Marketplace tool count mismatch"
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    marketplace_section = llms.split("## ICONIC Agent-Native Marketplace", 1)[1].split("\\n## ", 1)[0]
    assert "NOT yet purchasable" not in marketplace_section, "Marketplace llms.txt incorrectly says not purchasable"
    assert "Paid Stripe checkout is disabled" not in marketplace_section, "Marketplace llms.txt incorrectly says checkout disabled"
    print("Agent discovery checks passed: sitemap, canonical, JSON-LD, links, claims, llms.")

if __name__ == "__main__":
    check()
