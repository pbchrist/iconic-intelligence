"""Optional add-on: ask the visitor before searching the open web.

How it works
  1. When a question looks like it needs the open web (news, prices, weather, laws, public facts),
     the local model writes a short search. The demo shows that exact search and asks yes or no.
     Nothing leaves this computer before the visitor says yes.
  2. On yes, only those search words go to SearXNG running on this computer, which asks the public
     search engines. No AI company is involved. The answer says what was sent.

Turn it off:   ICONIC_WEB_SEARCH=0 in ~/.config/iconic-command.env, then restart.
Take it out:   delete this file and static/websearch.js. server.py and app.js run fine without them.
Settings:      ICONIC_SEARXNG_URL (default http://127.0.0.1:8888)
"""
import json
import os
import re
import urllib.parse
import urllib.request

MAX_QUERY = 80


class WebSearchError(Exception):
    pass


def enabled():
    return os.environ.get("ICONIC_WEB_SEARCH", "1").strip().lower() not in ("0", "false", "no", "off", "")


def searx_url():
    return os.environ.get("ICONIC_SEARXNG_URL", "http://127.0.0.1:8888").rstrip("/")


DECIDE_PROMPT = """You decide whether a question needs a search of the open web.
The visitor is using a demo with the private files of {name}. Those files cover that business: its clients, \
deals, staff, money, deadlines and internal notes. {name} is fictional, so the web knows nothing about it.

Say SEARCH only when a good answer needs current or public facts the files cannot have: news, weather, market \
prices, interest rates, laws and regulations, public facts about real companies, people or places, or events \
after the files were written. Greetings, small talk, and anything about {name} itself need NO search.

Reply with exactly one line:
NO
or
SEARCH: <the search words you would type, at most 8 words, no private names from the files>"""


def parse_decision(text):
    text = re.sub(r"(?s)<think>.*?</think>", "", text or "").strip()
    m = re.match(r"(?i)search\s*:\s*(.+)", text)
    if not m:
        return None
    q = m.group(1).splitlines()[0].strip().strip('"\'“”').strip()
    q = re.sub(r"\s+", " ", q)[:MAX_QUERY].strip()
    return q or None


def decide(question, ws_name, file_titles, complete):
    """Return the search words to offer, or None. `complete(messages, max_tokens, temperature)` -> text."""
    titles = "\n".join("- " + t for t in list(file_titles)[:8]) or "(none matched)"
    msgs = [{"role": "system", "content": DECIDE_PROMPT.format(name=ws_name or "this business")},
            {"role": "user", "content": "Files that matched the question:\n%s\n\nQuestion: %s" % (titles, question[:600])}]
    try:
        return parse_decision(complete(msgs, 30, 0.0))
    except Exception:
        return None


def search(query, url=None, n=5, timeout=8):
    """Send exactly `query` to SearXNG. Returns [{title, url, snippet}]."""
    qs = urllib.parse.urlencode({"q": query[:MAX_QUERY], "format": "json", "safesearch": "1"})
    req = urllib.request.Request("%s/search?%s" % (url or searx_url(), qs), headers={"User-Agent": "ICONIC-Command"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
    except Exception as e:
        raise WebSearchError("The web search didn't answer: %s" % str(e)[:120])
    out = []
    for item in data.get("results") or []:
        if not item.get("url") or not item.get("title"):
            continue
        out.append({"title": str(item["title"])[:160], "url": str(item["url"])[:500],
                    "snippet": re.sub(r"\s+", " ", str(item.get("content") or ""))[:400]})
        if len(out) >= n:
            break
    return out


def as_sources(results, start):
    """Number web results after the file sources. Returns (text for the model, source cards)."""
    sources, parts = [], []
    for k, r in enumerate(results):
        n = start + k
        host = urllib.parse.urlparse(r["url"]).netloc
        sources.append({"n": n, "id": None, "web": True, "title": r["title"], "url": r["url"], "rel": r["url"],
                        "folder": host, "date": "web", "snippet": r["snippet"]})
        parts.append("[%d] %s (web: %s)\n%s" % (n, r["title"], host, r["snippet"]))
    return "\n\n".join(parts), sources
