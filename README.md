# ICONIC Command

A private intelligence dashboard that runs on your own computer, next to your local model.

- **Ask**: plain-English questions, answered by your local model from your own files, with numbered sources you can open.
- **Intelligence**: a briefing the model writes from the files, rewritten whenever they change.
- **Work**: the real log of every job it runs.
- **Knowledge**: everything it has read.
- **Control**: where it runs, what it costs ($0 per token), and how work is routed.

## Install (on the model machine)

```bash
curl -fsSL https://raw.githubusercontent.com/pbchrist/iconic-intelligence/dashboard/install.sh | bash
```

Run the same command again to update. Your files and settings are kept.

## Files

One folder per business in `~/iconic-command-data/`. Each folder can have a `workspace.json` (name, description, suggested questions). Markdown, text, CSV, JSON, HTML, Word (.docx) and PDF (with `pdftotext`) are read. New or changed files are picked up within 20 seconds.

Two fictional sample workspaces ship with it: Hollis & Reyes LLP (a law firm) and Northline Supply Co. (an owner-run distributor).

## Settings

`~/.config/iconic-command.env`

| Setting | Default |
|---|---|
| `ICONIC_LLM_URL` | auto-detects llama.cpp, Ollama, LM Studio or vLLM on localhost |
| `ICONIC_LLM_MODEL` | first model the server lists |
| `ICONIC_PORT` | 8770 |
| `ICONIC_RATE_PER_HOUR` | 40 questions per visitor per hour from public addresses; your own network is unlimited |

After changing settings: `systemctl --user restart iconic-command`

## How it works

Python standard library only, no packages to install. Files are split into passages and ranked with BM25. The best passages go to the model with the question, and the answer streams back with citations. Model calls go only to the address in `ICONIC_LLM_URL`.

To test without a GPU: `python3 tests/mock_llm.py 18080`, then `ICONIC_LLM_URL=http://127.0.0.1:18080/v1 python3 server.py`.

## Optional: ask before searching the web

`websearch.py` + `static/websearch.js`. When a question needs the open web (news, prices, weather, laws), the local model writes a short search, the demo shows those exact words and asks yes or no. Only on yes do those words go to SearXNG on this computer (`ICONIC_SEARXNG_URL`, default `http://127.0.0.1:8888`), which asks public search engines. No AI company is involved; the answer shows what was sent.

- Turn off: `ICONIC_WEB_SEARCH=0` in the settings file, then restart.
- Take out: delete `websearch.py` and `static/websearch.js`. Nothing else needs changing.
- Tests: `python3 -m unittest tests.test_websearch`
