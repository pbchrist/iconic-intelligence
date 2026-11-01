#!/usr/bin/env python3
"""Stand-in for a llama.cpp server, for testing ICONIC Command without a GPU.

Speaks the OpenAI-compatible API (/v1/models, streaming /v1/chat/completions).
Answers are built from the sources it is given, so citations line up.
"""
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 18080


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_GET(self):
        body = json.dumps({"data": [{"id": "qwen3-27b-mock"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = req["messages"][-1]["content"]
        if "JSON array" in prompt:
            ids = [int(x) for x in re.findall(r"\[doc (\d+)\]", prompt)]
            titles = re.findall(r"\[doc \d+\] (.+?) \(", prompt)
            items = []
            sev = ["HIGH", "HIGH", "WATCH", "OPP", "NEW"]
            for k in range(min(5, len(ids))):
                items.append({"severity": sev[k], "category": "Mock category", "title": "Development from " + titles[k],
                              "detail": "Detail pulled from document %d with a number: $4,660." % ids[k],
                              "question": "What does %s say?" % titles[k], "doc_ids": [ids[k]]})
            text = "<think>planning the briefing</think>" + json.dumps(items)
        else:
            srcs = re.findall(r"^\[(\d+)\] (.+?) \(", prompt, re.M)
            q = prompt.split("Question:")[-1].strip()
            if srcs:
                parts = ["<think>reading sources</think>Short answer to “%s”: yes, the files cover it [1]." % q, "\n\n"]
                for n, t in srcs[:3]:
                    parts.append("- **%s** has the relevant detail [%s].\n" % (t, n))
                parts.append("\nNext step: check the deadline in the calendar [%s]." % srcs[-1][0])
                text = "".join(parts)
            else:
                text = "The files don't cover that."
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        toks = re.findall(r"\S+\s*|\s+", text)
        for t in toks:
            chunk = {"choices": [{"delta": {"content": t}}]}
            self.wfile.write(("data: " + json.dumps(chunk) + "\n\n").encode())
            self.wfile.flush()
            time.sleep(0.015)
        self.wfile.write(("data: " + json.dumps({"choices": [], "usage": {"completion_tokens": len(toks)}}) + "\n\n").encode())
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True


ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
