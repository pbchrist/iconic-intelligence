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
from concurrent.futures import ThreadPoolExecutor

MAX_QUERY = 80

# Cheap first check so ordinary questions about the files never pay for an extra model call.
WEB_CUES = re.compile(r"(?i)\b(today|tonight|tomorrow|yesterday|this (week|weekend|month|year)|right now|currently|current|"
                      r"latest|news|score|game|playing|schedule|weather|forecast|price of|stock|market|rate|rates|"
                      r"interest|inflation|election|law|laws|regulation|ruling|court ruled|who (is|won|was)|when (is|does|did)|"
                      r"where (is|can)|how much (is|does)|movie|movies|restaurant|open now|traffic|seahawks|mariners|"
                      r"kraken|sounders|nfl|nba|mlb|20[2-3][0-9])\b")


def likely_needs_web(question):
    return bool(WEB_CUES.search(question or ""))


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

Today is {today}. If the question is about now (today, tonight, this week, latest), put the date or "today" in the \
search words so the results are current, for example "Seahawks game tonight November 2 2026".

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


def decide(question, ws_name, file_titles, complete, today=""):
    """Return the search words to offer, or None. `complete(messages, max_tokens, temperature)` -> text."""
    titles = "\n".join("- " + t for t in list(file_titles)[:8]) or "(none matched)"
    msgs = [{"role": "system", "content": DECIDE_PROMPT.format(name=ws_name or "this business", today=today or "unknown")},
            {"role": "user", "content": "Files that matched the question:\n%s\n\nQuestion: %s" % (titles, question[:600])}]
    try:
        return parse_decision(complete(msgs, 30, 0.0))
    except Exception:
        return None


def search(query, url=None, n=5, timeout=8, extra=None):
    """Send exactly `query` to SearXNG. Returns [{title, url, snippet}]."""
    params = {"q": query[:MAX_QUERY], "format": "json", "safesearch": "1"}
    params.update(extra or {})
    qs = urllib.parse.urlencode(params)
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
        parts.append("[%d] %s (web: %s)\n%s%s" % (n, r["title"], host, r["snippet"],
                                                 ("\nFrom the page: " + r["page"]) if r.get("page") else ""))
    return "\n\n".join(parts), sources


def _page_text(url, terms, timeout=5, limit=1400):
    """Read one result page and keep the part that mentions the search words."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ICONIC demo)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if "html" not in (r.headers.get("Content-Type") or "html"):
                return ""
            raw = r.read(600000).decode("utf-8", "replace")
    except Exception:
        return ""
    raw = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", raw))
    text = re.sub(r"&nbsp;|&#160;", " ", text).strip()
    low, best = text.lower(), 0
    for t in terms:
        i = low.find(t)
        if i > 0:
            best = max(0, i - 300)
            break
    return text[best:best + limit]


def search_best(query, url=None, n=5):
    """General results plus fresh news, then read the top pages so the model sees real content, not just blurbs."""
    out, seen = [], set()
    for extra in ({"categories": "news", "time_range": "week"}, {}):
        try:
            got = search(query, url, n, extra=extra)
        except WebSearchError:
            if extra:
                continue
            if not out:
                raise
            got = []
        for r in got:
            if r["url"] not in seen:
                seen.add(r["url"]); out.append(r)
    out = out[:n]
    terms = [w.lower() for w in re.findall(r"[A-Za-z0-9]{4,}", query)][:4]
    with ThreadPoolExecutor(3) as ex:
        texts = list(ex.map(lambda r: _page_text(r["url"], terms), out[:3]))
    for r, t in zip(out, texts):
        if t:
            r["page"] = t
    return out
