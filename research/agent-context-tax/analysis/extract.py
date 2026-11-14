"""Step 1: pull per-job token counts out of the Hermes agent databases (read-only).

Writes jobs.csv: one row per (session, model) usage record. Holds counts only:
no message text, no prompts, no session ids, no client names.

Run: python3 extract.py   (paths below are the Hermes homes on the Beastmaster box)
"""
import csv
import sqlite3
from pathlib import Path

HOME = Path.home()
SOURCES = {
    # label used in the paper -> Hermes state database
    "operator": HOME / ".hermes/state.db",
    "client_bot_1": HOME / "hermes-instance2/client-bots/egbgmc/home/state.db",
    "client_bot_2": HOME / "hermes-instance2/client-bots/ubc/home/state.db",
}
OUT = Path(__file__).with_name("jobs.csv")

QUERY = """
SELECT u.session_id, s.source, u.billing_provider, u.model, u.api_call_count,
       u.input_tokens, u.cache_read_tokens, u.cache_write_tokens, u.output_tokens,
       u.reasoning_tokens, u.first_seen, s.parent_session_id IS NOT NULL
FROM session_model_usage u JOIN sessions s ON s.id = u.session_id
WHERE u.api_call_count > 0
"""

FIELDS = ["job", "bot", "source", "provider", "model", "steps", "fresh_input", "cached_input",
          "cache_write", "output", "reasoning", "first_seen", "is_child"]


def model_family(model: str) -> str:
    m = model.lower()
    if "qwen" in m:
        return "qwen-27b-local"
    return m.rsplit("/", 1)[-1]


def main() -> None:
    rows = []
    job_ids: dict = {}  # anonymous job number per (bot, session); real ids are not written
    for bot, path in SOURCES.items():
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        for r in con.execute(QUERY):
            sid, src, prov, model, steps, fin, cread, cwrite, out, reas, first, child = r
            job = job_ids.setdefault((bot, sid), len(job_ids) + 1)
            rows.append([job, bot, src, prov, model_family(model or "unknown"), steps,
                         fin, cread, cwrite, out, reas or 0, round(first or 0), int(child)])
        con.close()
    rows.sort(key=lambda r: (r[11], r[0]))
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT.name}")


if __name__ == "__main__":
    main()
