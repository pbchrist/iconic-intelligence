#!/usr/bin/env python3
"""ICONIC Command: a private intelligence dashboard.

Point it at folders of documents and a local model (llama.cpp, Ollama or any
OpenAI-compatible server). It indexes the files, answers questions from them
with citations, writes an intelligence feed, and logs every job it runs.

Standard library only. Python 3.8+.
"""
import html
import ipaddress
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")
DATA = os.path.expanduser(os.environ.get("ICONIC_DATA", os.path.join(ROOT, "data")))
STATE = os.path.expanduser(os.environ.get("ICONIC_STATE", os.path.join(ROOT, "state")))
HOST = os.environ.get("ICONIC_HOST", "0.0.0.0")
PORT = int(os.environ.get("ICONIC_PORT", "8770"))
LLM_URL = os.environ.get("ICONIC_LLM_URL", "").rstrip("/")
LLM_MODEL = os.environ.get("ICONIC_LLM_MODEL", "")
LLM_KEY = os.environ.get("ICONIC_LLM_KEY", "")
RATE_PER_HOUR = int(os.environ.get("ICONIC_RATE_PER_HOUR", "40"))
SCAN_SECONDS = int(os.environ.get("ICONIC_SCAN_SECONDS", "20"))
TEXT_EXT = {".md", ".markdown", ".txt", ".csv", ".tsv", ".json", ".log", ".html", ".htm", ".eml"}
STARTED = time.time()
os.makedirs(STATE, exist_ok=True)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- text extraction

def read_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in TEXT_EXT:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            if ext in (".html", ".htm"):
                raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
                raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            return raw
        if ext == ".docx":
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", "replace")
            xml = re.sub(r"</w:p>", "\n\n", xml)
            return html.unescape(re.sub(r"<[^>]+>", "", xml))
        if ext == ".pdf" and shutil.which("pdftotext"):
            out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, timeout=60)
            return out.stdout.decode("utf-8", "replace")
    except Exception as e:  # unreadable file: skip it, note why
        log("skip", path, e)
    return None


def title_of(path, text):
    for line in text.splitlines()[:12]:
        m = re.match(r"^\s*#\s+(.+)", line)
        if m:
            return m.group(1).strip()
        m = re.match(r"(?i)^\s*title:\s*(.+)", line)
        if m:
            return m.group(1).strip()
    name = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"[-_]+", " ", name).strip().title()


def date_of(text, mtime):
    m = re.search(r"(?im)^\s*\**date\**:\s*\**\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text[:1500])
    if m:
        return m.group(1)
    return time.strftime("%Y-%m-%d", time.localtime(mtime))


WORD = re.compile(r"[a-z0-9$%][a-z0-9$%.'-]*[a-z0-9%]|[a-z0-9]")
STOP = set("""a an and are as at be been but by can could did do does for from had has have he her his how i if in into
is it its me my no not of on or our she so than that the their them then there these they this to was we were what
when where which who why will with would you your about any all also just more most some such tell us""".split())


def terms(text):
    out = []
    for w in WORD.findall(text.lower()):
        w = w.strip(".'-")
        if not w or w in STOP:
            continue
        if len(w) > 4 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def chunk(text, size=900, overlap=150):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        while len(p) > size * 1.6:  # very long paragraph: hard split
            head, p = p[:size], p[size - overlap:]
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(head)
        if len(cur) + len(p) + 2 > size and cur:
            chunks.append(cur)
            tail = cur[-overlap:]
            cur = tail + "\n\n" + p if len(cur) > size else p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur:
        chunks.append(cur)
    return chunks or [text[:size]]


# ---------------------------------------------------------------- workspaces + index

class Workspace:
    def __init__(self, wid, path):
        self.id = wid
        self.path = path
        self.meta = {}
        self.docs = []      # dicts: id, title, rel, folder, ext, date, words, text
        self.chunks = []    # dicts: doc, i, text, tf, len
        self.df = Counter()
        self.avglen = 1.0
        self.signature = ""
        self.indexed_at = 0
        self.lock = threading.Lock()

    def load_meta(self):
        meta = {"name": self.id.replace("-", " ").title(), "kind": "", "initials": self.id[:1].upper(),
                "tagline": "", "suggestions": [], "sample": False}
        mp = os.path.join(self.path, "workspace.json")
        if os.path.exists(mp):
            try:
                with open(mp, encoding="utf-8") as f:
                    meta.update(json.load(f))
            except Exception as e:
                log("bad workspace.json", mp, e)
        self.meta = meta

    def files(self):
        out = []
        for base, dirs, names in os.walk(self.path):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for n in sorted(names):
                if n.startswith(".") or n == "workspace.json":
                    continue
                ext = os.path.splitext(n)[1].lower()
                if ext in TEXT_EXT or ext in (".docx", ".pdf"):
                    p = os.path.join(base, n)
                    st = os.stat(p)
                    out.append((p, st.st_mtime, st.st_size))
        return out

    def current_signature(self):
        return "|".join("%s:%d:%d" % (os.path.relpath(p, self.path), m, s) for p, m, s in self.files())

    def reindex(self):
        self.load_meta()
        files = self.files()
        docs, chunks, df = [], [], Counter()
        for p, mtime, size in files:
            text = read_text(p)
            if not text or not text.strip():
                continue
            rel = os.path.relpath(p, self.path)
            folder = os.path.dirname(rel) or "general"
            d = {"id": len(docs), "title": title_of(p, text), "rel": rel, "folder": folder,
                 "ext": os.path.splitext(p)[1].lower().lstrip("."), "date": date_of(text, mtime),
                 "words": len(text.split()), "text": text, "mtime": mtime}
            docs.append(d)
            for i, c in enumerate(chunk(text)):
                t = terms(d["title"] + " " + d["folder"] + " " + c)
                tf = Counter(t)
                chunks.append({"doc": d["id"], "i": i, "text": c, "tf": tf, "len": len(t) or 1})
                df.update(tf.keys())
        with self.lock:
            self.docs, self.chunks, self.df = docs, chunks, df
            self.avglen = (sum(c["len"] for c in chunks) / len(chunks)) if chunks else 1.0
            self.signature = "|".join("%s:%d:%d" % (os.path.relpath(p, self.path), m, s) for p, m, s in files)
            self.indexed_at = time.time()
        return len(docs), len(chunks)

    def search(self, query, k=6, per_doc=2):
        q = terms(query)
        with self.lock:
            chunks, df, avg, n = self.chunks, self.df, self.avglen, max(1, len(self.chunks))
        if not chunks:
            return []
        k1, b = 1.4, 0.75
        scored = []
        qset = Counter(q)
        for c in chunks:
            s = 0.0
            for t, qn in qset.items():
                f = c["tf"].get(t)
                if not f:
                    continue
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += qn * idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * c["len"] / avg))
            if s > 0:
                scored.append((s, c))
        scored.sort(key=lambda x: -x[0])
        out, seen = [], Counter()
        for s, c in scored:
            if seen[c["doc"]] >= per_doc:
                continue
            seen[c["doc"]] += 1
            out.append((s, c))
            if len(out) >= k:
                break
        return out

    def summary(self):
        with self.lock:
            docs = list(self.docs)
            n_chunks = len(self.chunks)
        folders = Counter(d["folder"] for d in docs)
        types = Counter(d["ext"] for d in docs)
        return {
            "id": self.id, **{k: self.meta.get(k) for k in ("name", "kind", "initials", "tagline", "suggestions", "sample")},
            "documents": len(docs), "passages": n_chunks, "words": sum(d["words"] for d in docs),
            "folders": folders.most_common(), "types": types.most_common(), "indexed_at": self.indexed_at,
            "docs": [{k: d[k] for k in ("id", "title", "rel", "folder", "ext", "date", "words")}
                     for d in sorted(docs, key=lambda d: d["date"], reverse=True)],
        }


WORKSPACES = {}
WS_LOCK = threading.Lock()


def discover():
    os.makedirs(DATA, exist_ok=True)
    found = {}
    for name in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, name)
        if os.path.isdir(p) and not name.startswith("."):
            found[name] = WORKSPACES.get(name) or Workspace(name, p)
    with WS_LOCK:
        WORKSPACES.clear()
        WORKSPACES.update(found)
    return found


def ordered_workspaces():
    with WS_LOCK:
        ws = list(WORKSPACES.values())
    # real workspaces first, samples after
    return sorted(ws, key=lambda w: (bool(w.meta.get("sample")), w.meta.get("order", 99), w.id))


# ---------------------------------------------------------------- jobs + telemetry

class Jobs:
    def __init__(self):
        self.lock = threading.Lock()
        self.items = deque(maxlen=60)
        self.seq = 0
        self.tokens = 0
        self.questions = 0
        self.gen_seconds = 0.0
        self.bytes_out_external = 0

    def start(self, kind, title, ws=""):
        with self.lock:
            self.seq += 1
            j = {"id": self.seq, "kind": kind, "title": title, "ws": ws, "status": "running",
                 "started": time.time(), "ms": None, "detail": ""}
            self.items.appendleft(j)
            return j

    def finish(self, j, status="done", detail=""):
        with self.lock:
            j["status"] = status
            j["ms"] = int((time.time() - j["started"]) * 1000)
            j["detail"] = detail

    def add_tokens(self, n, secs):
        with self.lock:
            self.tokens += n
            self.gen_seconds += secs

    def snapshot(self):
        with self.lock:
            return [dict(j) for j in self.items]


JOBS = Jobs()


# ---------------------------------------------------------------- model client

class Model:
    def __init__(self):
        self.url = LLM_URL
        self.model = LLM_MODEL
        self.online = False
        self.last_check = 0
        self.error = ""
        self.lock = threading.Lock()

    def _req(self, path, body=None, timeout=10):
        url = self.url + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
        req.add_header("Content-Type", "application/json")
        if LLM_KEY:
            req.add_header("Authorization", "Bearer " + LLM_KEY)
        return urllib.request.urlopen(req, timeout=timeout)

    EMBED = re.compile(r"(?i)embed|nomic|bge|\be5[-_]|minilm|rerank|gte-")

    def detect(self):
        """Find a chat model. Skips embedding-only servers. Scans common local ports."""
        ports = list(range(8000, 8101)) + [5000, 1234, 11434, 30000, 9000]
        candidates = ([LLM_URL] if LLM_URL else []) + ["http://127.0.0.1:%d/v1" % p for p in ports]
        if self.url and self.url not in candidates[:1]:
            candidates.insert(0, self.url)
        seen, skipped = set(), []
        for base in candidates:
            if base in seen:
                continue
            seen.add(base)
            try:
                with urllib.request.urlopen(base + "/models", timeout=1.5) as r:
                    j = json.load(r)
            except Exception:
                continue
            ids = [m.get("id") or m.get("name") for m in (j.get("data") or j.get("models") or [])]
            ids = [i for i in ids if i]
            chat = [i for i in ids if not self.EMBED.search(i)]
            if ids and not chat:
                skipped.append("%s (embeddings only)" % urlparse(base).netloc)
                continue
            with self.lock:
                self.url = base
                self.model = LLM_MODEL or (chat[0] if chat else "local-model")
                self.online, self.error, self.last_check = True, "", time.time()
            return True
        with self.lock:
            self.online, self.last_check = False, time.time()
            self.error = "No chat model is running" + ("; found only " + ", ".join(skipped) if skipped else "")
        return False

    def is_private(self):
        try:
            host = urlparse(self.url).hostname or ""
            ip = ipaddress.ip_address(socket.gethostbyname(host))
            return ip.is_loopback or ip.is_private or ip in ipaddress.ip_network("100.64.0.0/10")
        except Exception:
            return False

    def status(self):
        if time.time() - self.last_check > 15:
            self.detect()
        return {"online": self.online, "model": self.model, "endpoint": urlparse(self.url).netloc if self.url else "",
                "private": self.is_private() if self.url else True, "error": self.error}

    def stream(self, messages, max_tokens=700, temperature=0.2):
        """Yield ('token', text) / ('thinking', None) / ('usage', n)."""
        if not self.online and not self.detect():
            raise RuntimeError(self.error or "Model offline")
        body = {"model": self.model, "messages": messages, "stream": True, "temperature": temperature,
                "max_tokens": max_tokens, "stream_options": {"include_usage": True},
                "chat_template_kwargs": {"enable_thinking": False}}
        try:
            resp = self._req("/chat/completions", body, timeout=300)
        except urllib.error.HTTPError as e:
            if e.code == 400:  # some servers reject extra fields: retry plain
                for k in ("stream_options", "chat_template_kwargs"):
                    body.pop(k, None)
                resp = self._req("/chat/completions", body, timeout=300)
            else:
                raise
        in_think, buf = False, ""
        with resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    j = json.loads(payload)
                except ValueError:
                    continue
                if j.get("usage") and j["usage"].get("completion_tokens"):
                    yield ("usage", j["usage"]["completion_tokens"])
                for ch in j.get("choices") or []:
                    delta = ch.get("delta") or {}
                    if delta.get("reasoning_content"):
                        yield ("thinking", None)
                    piece = delta.get("content") or ""
                    if not piece:
                        continue
                    buf += piece
                    # strip <think>...</think> blocks emitted inline
                    out = ""
                    while buf:
                        if in_think:
                            end = buf.find("</think>")
                            if end < 0:
                                buf = buf[-8:]
                                break
                            buf, in_think = buf[end + 8:], False
                        else:
                            start = buf.find("<think>")
                            if start < 0:
                                keep = 7 if "<" in buf[-7:] else 0
                                out += buf[:len(buf) - keep] if keep else buf
                                buf = buf[len(buf) - keep:] if keep else ""
                                break
                            out += buf[:start]
                            buf, in_think = buf[start + 7:], True
                            yield ("thinking", None)
                    if out:
                        yield ("token", out)
        if buf and not in_think:
            yield ("token", buf)

    def complete(self, messages, max_tokens=1200, temperature=0.3):
        text, n, t0 = "", 0, time.time()
        for kind, val in self.stream(messages, max_tokens, temperature):
            if kind == "token":
                text += val
                n += 1
            elif kind == "usage":
                n = val
        JOBS.add_tokens(n, time.time() - t0)
        return text


MODEL = Model()


# ---------------------------------------------------------------- feed (agent-written)

FEED = {}            # ws id -> {"signature", "items", "generated_at", "status", "error"}
FEED_LOCK = threading.Lock()


def feed_path(wid):
    return os.path.join(STATE, "feed-%s.json" % re.sub(r"[^a-z0-9_-]", "", wid.lower()))


def load_feed_cache():
    for w in ordered_workspaces():
        p = feed_path(w.id)
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    FEED[w.id] = json.load(f)
            except Exception:
                pass


def parse_items(text, ws):
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("model did not return a list")
    raw = json.loads(m.group(0))
    titles = {d["id"]: d["title"] for d in ws.docs}
    items = []
    for it in raw[:6]:
        if not isinstance(it, dict) or not it.get("title"):
            continue
        sev = str(it.get("severity", "NEW")).upper()
        if sev not in ("HIGH", "WATCH", "OPP", "NEW"):
            sev = "NEW"
        ids = [int(x) for x in (it.get("doc_ids") or it.get("docs") or []) if str(x).isdigit() and int(x) in titles]
        items.append({"severity": sev, "category": str(it.get("category", "")).upper()[:28],
                      "title": str(it["title"])[:140], "detail": str(it.get("detail", ""))[:320],
                      "question": str(it.get("question") or it["title"])[:200],
                      "sources": [{"id": i, "title": titles[i]} for i in ids[:4]]})
    if not items:
        raise ValueError("no usable items")
    return items


def build_feed(ws, force=False):
    sig = ws.signature
    with FEED_LOCK:
        cur = FEED.get(ws.id) or {}
        if not force and cur.get("signature") == sig and cur.get("items"):
            return
        if cur.get("status") == "running":
            return
        FEED[ws.id] = dict(cur, status="running", error="")
    job = JOBS.start("BRIEFING", "Morning briefing for %s" % ws.meta.get("name", ws.id), ws.id)
    try:
        docs = sorted(ws.docs, key=lambda d: d["date"], reverse=True)
        budget, parts = 14000, []
        for d in docs:
            body = re.sub(r"\s+", " ", d["text"])[:900]
            part = "[doc %d] %s (%s, %s)\n%s" % (d["id"], d["title"], d["folder"], d["date"], body)
            if budget - len(part) < 0:
                break
            budget -= len(part)
            parts.append(part)
        today = time.strftime("%A, %B %d, %Y")
        messages = [
            {"role": "system", "content": "You are the intelligence agent for %s. Today is %s. You read the business's "
             "own documents and flag what the owner should know. Be specific: names, numbers, dates. Never invent facts "
             "that are not in the documents." % (ws.meta.get("name"), today)},
            {"role": "user", "content": "Documents:\n\n" + "\n\n".join(parts) + "\n\nWrite the 4 or 5 most important "
             "developments as a JSON array. Each item: {\"severity\": \"HIGH\"|\"WATCH\"|\"OPP\"|\"NEW\", \"category\": "
             "two or three words, \"title\": one specific sentence under 14 words, \"detail\": one or two sentences "
             "with the numbers and the deadline or next step, \"question\": the follow-up question the owner would ask, "
             "\"doc_ids\": [numbers of the documents it comes from]}. HIGH = money or a deadline at risk; WATCH = a "
             "pattern to keep an eye on; OPP = an opportunity. Output only the JSON array."},
        ]
        text = MODEL.complete(messages, max_tokens=1400, temperature=0.2)
        items = parse_items(text, ws)
        data = {"signature": sig, "items": items, "generated_at": time.time(), "status": "ready", "error": "",
                "model": MODEL.model}
        with FEED_LOCK:
            FEED[ws.id] = data
        with open(feed_path(ws.id), "w", encoding="utf-8") as f:
            json.dump(data, f)
        JOBS.finish(job, "done", "%d developments from %d documents" % (len(items), len(parts)))
    except Exception as e:
        with FEED_LOCK:
            FEED[ws.id] = dict(FEED.get(ws.id) or {}, status="error", error=str(e)[:200])
        JOBS.finish(job, "failed", str(e)[:160])
        log("briefing failed", ws.id, e)


# ---------------------------------------------------------------- background watcher

def watcher():
    first = True
    while True:
        try:
            discover()
            for ws in ordered_workspaces():
                sig = ws.current_signature()
                if sig != ws.signature or first:
                    job = JOBS.start("INDEX", "Read the %s files" % ws.id, ws.id)
                    n_docs, n_chunks = ws.reindex()
                    JOBS.finish(job, "done", "%d documents · %d passages" % (n_docs, n_chunks))
            if MODEL.online or MODEL.detect():
                for ws in ordered_workspaces():
                    if ws.docs:
                        build_feed(ws)
        except Exception as e:
            log("watcher error", e)
        first = False
        time.sleep(SCAN_SECONDS)


# ---------------------------------------------------------------- rate limiting

HITS = defaultdict(deque)


def allowed(ip):
    try:
        a = ipaddress.ip_address(ip)
        if a.is_loopback or a.is_private or a in ipaddress.ip_network("100.64.0.0/10"):
            return True  # your own network is unlimited
    except ValueError:
        pass
    q, now = HITS[ip], time.time()
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= RATE_PER_HOUR:
        return False
    q.append(now)
    return True


# ---------------------------------------------------------------- HTTP

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "application/javascript",
        ".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp", ".ico": "image/x-icon",
        ".json": "application/json"}


class Handler(BaseHTTPRequestHandler):
    server_version = "ICONIC"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def client_ip(self):
        fwd = self.headers.get("CF-Connecting-IP") or self.headers.get("X-Forwarded-For", "")
        return (fwd.split(",")[0].strip() if fwd else "") or self.client_address[0]

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def ws(self, qs):
        wid = (qs.get("ws") or [""])[0]
        with WS_LOCK:
            if wid in WORKSPACES:
                return WORKSPACES[wid]
        lst = ordered_workspaces()
        return lst[0] if lst else None

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        try:
            if u.path == "/api/status":
                return self.send_json(self.status())
            if u.path == "/api/workspace":
                w = self.ws(qs)
                if not w:
                    return self.send_json({"error": "no workspaces"}, 404)
                return self.send_json(w.summary())
            if u.path == "/api/feed":
                w = self.ws(qs)
                f = FEED.get(w.id) if w else None
                return self.send_json(f or {"status": "waiting", "items": []})
            if u.path == "/api/jobs":
                return self.send_json({"jobs": JOBS.snapshot(), "scan_seconds": SCAN_SECONDS})
            if u.path == "/api/doc":
                w = self.ws(qs)
                i = int((qs.get("id") or ["-1"])[0])
                with w.lock:
                    d = next((d for d in w.docs if d["id"] == i), None)
                if not d:
                    return self.send_json({"error": "not found"}, 404)
                return self.send_json({k: d[k] for k in ("id", "title", "rel", "folder", "ext", "date", "words", "text")})
            return self.static(u.path)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(min(n, 200000)) or b"{}")
        except ValueError:
            return self.send_json({"error": "bad json"}, 400)
        if u.path == "/api/ask":
            return self.ask(body)
        if u.path == "/api/refresh-feed":
            w = self.ws({"ws": [body.get("ws", "")]})
            if w:
                threading.Thread(target=build_feed, args=(w, True), daemon=True).start()
            return self.send_json({"ok": True})
        self.send_json({"error": "not found"}, 404)

    def status(self):
        m = MODEL.status()
        tps = (JOBS.tokens / JOBS.gen_seconds) if JOBS.gen_seconds else 0
        return {"model": m, "workspaces": [{"id": w.id, "name": w.meta.get("name"), "kind": w.meta.get("kind"),
                                            "initials": w.meta.get("initials"), "sample": w.meta.get("sample"),
                                            "documents": len(w.docs)} for w in ordered_workspaces()],
                "tokens": JOBS.tokens, "questions": JOBS.questions, "tokens_per_second": round(tps, 1),
                "cost": 0, "bytes_external": 0 if m["private"] else None, "uptime": int(time.time() - STARTED),
                "host": socket.gethostname(), "now": time.time()}

    def static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        full = os.path.realpath(os.path.join(STATIC, path.lstrip("/")))
        if not full.startswith(os.path.realpath(STATIC)) or not os.path.isfile(full):
            full = os.path.join(STATIC, "index.html")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(os.path.splitext(full)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def sse(self, event, data):
        self.wfile.write(("event: %s\ndata: %s\n\n" % (event, json.dumps(data))).encode())
        self.wfile.flush()

    def ask(self, body):
        q = str(body.get("q", "")).strip()[:600]
        w = self.ws({"ws": [body.get("ws", "")]})
        if not q or not w:
            return self.send_json({"error": "Ask a question."}, 400)
        if not allowed(self.client_ip()):
            return self.send_json({"error": "That's the limit for this hour. Book the free check to keep going."}, 429)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        job = JOBS.start("QUESTION", q[:90], w.id)
        t0 = time.time()
        try:
            hits = w.search(q + " " + " ".join(h.get("q", "") for h in (body.get("history") or [])[-1:]))
            with w.lock:
                docs = {d["id"]: d for d in w.docs}
                first_chunk = {}
                for c in w.chunks:
                    first_chunk.setdefault(c["doc"], c)
            # Broad questions ("what should I worry about?") match few words; widen to the newest files.
            broad = re.search(r"(?i)\b(worr|concern|missing|priorit|urgent|attention|overview|summar|happening|"
                              r"this week|today|going on|should i know|risks?)\b", q)
            if len(hits) < 4 or broad:
                have = {c["doc"] for _, c in hits}
                for d in sorted(docs.values(), key=lambda d: d["date"], reverse=True):
                    if len(hits) >= 7:
                        break
                    if d["id"] not in have and d["id"] in first_chunk:
                        hits.append((0, first_chunk[d["id"]]))
                        have.add(d["id"])
            sources = []
            for n, (score, c) in enumerate(hits, 1):
                d = docs[c["doc"]]
                sources.append({"n": n, "id": d["id"], "title": d["title"], "rel": d["rel"], "folder": d["folder"],
                                "date": d["date"], "snippet": c["text"][:420], "chunk": c["text"]})
            self.sse("sources", [{k: s[k] for k in ("n", "id", "title", "rel", "folder", "date", "snippet")}
                                 for s in sources])
            ctx = "\n\n".join("[%d] %s (%s, %s)\n%s" % (s["n"], s["title"], s["rel"], s["date"], s["chunk"])
                              for s in sources) or "(no matching documents)"
            meta = w.meta
            messages = [{"role": "system", "content":
                         "You are ICONIC, the private AI for %s%s. It runs on the business's own computer. "
                         "Today is %s. Answer from the numbered sources only. Put the answer first, in plain English, "
                         "under 160 words. Cite every fact with its source number in square brackets, like [2]. Use "
                         "short bullet points only when listing several items. If the sources do not contain the "
                         "answer, say exactly what is missing and which document would have it. Never make up names, "
                         "numbers or dates." % (meta.get("name"), (", " + meta["kind"]) if meta.get("kind") else "",
                                                time.strftime("%A, %B %d, %Y"))}]
            for h in (body.get("history") or [])[-3:]:
                if h.get("q") and h.get("a"):
                    messages.append({"role": "user", "content": str(h["q"])[:600]})
                    messages.append({"role": "assistant", "content": str(h["a"])[:1500]})
            messages.append({"role": "user", "content": "Sources:\n\n%s\n\nQuestion: %s" % (ctx, q)})
            n_tok, first = 0, None
            for kind, val in MODEL.stream(messages):
                if kind == "token":
                    if first is None:
                        first = time.time()
                    n_tok += 1
                    self.sse("token", val)
                elif kind == "thinking":
                    self.sse("thinking", True)
                elif kind == "usage":
                    n_tok = val
            secs = time.time() - (first or t0)
            JOBS.add_tokens(n_tok, secs)
            with JOBS.lock:
                JOBS.questions += 1
            done = {"ms": int((time.time() - t0) * 1000), "tokens": n_tok,
                    "tps": round(n_tok / secs, 1) if secs > 0 else 0, "model": MODEL.model,
                    "private": MODEL.is_private(), "cost": 0}
            self.sse("done", done)
            JOBS.finish(job, "done", "%d sources · %d tokens · %.1fs" % (len(sources), n_tok, done["ms"] / 1000))
        except (BrokenPipeError, ConnectionResetError):
            JOBS.finish(job, "failed", "Visitor left")
        except Exception as e:
            log("ask failed", e)
            JOBS.finish(job, "failed", str(e)[:160])
            try:
                self.sse("error", "The local model didn't answer: %s" % str(e)[:200])
            except Exception:
                pass


def main():
    discover()
    for ws in ordered_workspaces():
        ws.load_meta()
    load_feed_cache()
    MODEL.detect()
    log("model:", MODEL.model if MODEL.online else "not found", MODEL.url)
    threading.Thread(target=watcher, daemon=True).start()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    log("ICONIC Command on http://%s:%d  data=%s" % (HOST, PORT, DATA))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
