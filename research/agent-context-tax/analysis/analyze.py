"""Step 2: compute every figure in the paper from jobs.csv. Writes results.json.

Definitions
- job: one Hermes session (all model rows for it summed).
- step: one call to the model (api_call_count).
- fresh input: input tokens the provider did not serve from cache.
- cached input: input tokens re-sent from earlier steps and served from cache.
- read = fresh + cached + cache_write; written = output tokens.
- Helper calls (source == "tool": single internal lookups, no tool use) are
  counted in coverage but excluded from job statistics.

Run: python3 analyze.py
"""
import csv
import json
import math
import statistics as st
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CODEX_FIX = datetime(2026, 9, 18, tzinfo=timezone.utc).timestamp()  # hermes-agent 1c362700b3
COMPRESSION_THRESHOLD_TOKENS = 100_000  # ~/.hermes/config.yaml compression.threshold_tokens
BINS = [(1, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 10**9)]


def day(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).date().isoformat()


def loglog_slope(points):
    pts = [(math.log(x), math.log(y)) for x, y in points if x > 0 and y > 0]
    if len(pts) < 10:
        return None
    mx = st.mean(p[0] for p in pts)
    my = st.mean(p[1] for p in pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx == 0:
        return None
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
    ss_tot = sum((p[1] - my) ** 2 for p in pts)
    ss_res = sum((p[1] - (my + b * (p[0] - mx))) ** 2 for p in pts)
    return {"slope": round(b, 2), "r2": round(1 - ss_res / ss_tot, 2), "n": len(pts)}


def main() -> None:
    rows = list(csv.DictReader((HERE / "jobs.csv").open()))
    for r in rows:
        for k in ("steps", "fresh_input", "cached_input", "cache_write", "output", "reasoning", "first_seen"):
            r[k] = int(r[k])

    # ---- double-count check on Codex rows before/after the 2026-09-18 fix ----
    def codex(pre):
        s = [r for r in rows if r["provider"] == "openai-codex" and r["cached_input"] > 0
             and ((r["first_seen"] < CODEX_FIX) == pre)]
        return {"rows": len(s),
                "rows_fresh_ge_cached": sum(r["fresh_input"] >= r["cached_input"] for r in s),
                "fresh_to_cached": round(sum(r["fresh_input"] for r in s) / sum(r["cached_input"] for r in s), 3)}

    # ---- aggregate to jobs ----
    jobs = defaultdict(lambda: {"steps": 0, "fresh": 0, "cached": 0, "cwrite": 0, "out": 0, "first": 1e20})
    for r in rows:
        j = jobs[r["job"]]
        j["bot"], j["source"] = r["bot"], r["source"]
        j["steps"] += r["steps"]
        j["fresh"] += r["fresh_input"]
        j["cached"] += r["cached_input"]
        j["cwrite"] += r["cache_write"]
        j["out"] += r["output"]
        j["first"] = min(j["first"], r["first_seen"])
    for j in jobs.values():
        j["read"] = j["fresh"] + j["cached"] + j["cwrite"]

    alljobs = list(jobs.values())
    helpers = [j for j in alljobs if j["source"] == "tool"]
    work = [j for j in alljobs if j["source"] != "tool"]

    def totals(js):
        t = {k: sum(j[k] for j in js) for k in ("steps", "fresh", "cached", "cwrite", "out", "read")}
        t["jobs"] = len(js)
        t["read_per_written"] = round(t["read"] / t["out"], 1)
        t["fresh_per_written"] = round((t["fresh"] + t["cwrite"]) / t["out"], 1)
        t["cached_share_of_read_pct"] = round(100 * t["cached"] / t["read"], 1)
        t["written_share_of_all_pct"] = round(100 * t["out"] / (t["read"] + t["out"]), 2)
        return t

    coverage = {}
    for bot in sorted({j["bot"] for j in alljobs}):
        bj = [j for j in alljobs if j["bot"] == bot]
        coverage[bot] = {"jobs": len(bj), "helper_calls": sum(j["source"] == "tool" for j in bj),
                         "from": day(min(j["first"] for j in bj)), "to": day(max(j["first"] for j in bj)),
                         "steps": sum(j["steps"] for j in bj)}

    # ---- length bins (work jobs) ----
    W = totals(work)
    bins = []
    for a, b in BINS:
        s = [j for j in work if a <= j["steps"] <= b]
        bins.append({
            "label": f"{a}-{b}" if b < 10**9 else f"{a}+",
            "jobs": len(s),
            "jobs_pct": round(100 * len(s) / len(work), 1),
            "median_read_per_step": round(st.median(j["read"] / j["steps"] for j in s)),
            "read_per_written": round(sum(j["read"] for j in s) / sum(j["out"] for j in s), 1),
            "read_share_pct": round(100 * sum(j["read"] for j in s) / W["read"], 1),
            "median_read_per_job": round(st.median(j["read"] for j in s)),
        })

    long_jobs = [j for j in work if j["steps"] >= 16]
    ranked = sorted(work, key=lambda j: j["read"], reverse=True)
    top10 = ranked[: max(1, len(ranked) // 10)]

    # ---- growth: total read vs steps, log-log ----
    pts = lambda js: [(j["steps"], j["read"]) for j in js]
    slopes = {
        "all_work_jobs": loglog_slope(pts(work)),
        "work_jobs_1_to_15_steps": loglog_slope(pts([j for j in work if j["steps"] <= 15])),
        "work_jobs_16plus_steps": loglog_slope(pts(long_jobs)),
        "by_source": {s: loglog_slope(pts([j for j in work if j["source"] == s]))
                      for s in sorted({j["source"] for j in work})},
        "by_bot": {b: loglog_slope(pts([j for j in work if j["bot"] == b]))
                   for b in sorted({j["bot"] for j in work})},
    }

    # ---- one-step vs long job comparison (median per job) ----
    short = [j for j in work if j["steps"] <= 3]
    results = {
        "coverage": coverage,
        "rows": len(rows),
        "jobs_total": len(alljobs),
        "helper_calls_excluded": len(helpers),
        "work": W,
        "helpers": totals(helpers),
        "all_including_helpers": totals(alljobs),
        "bins": bins,
        "long_jobs_16plus": {
            "jobs": len(long_jobs),
            "jobs_pct": round(100 * len(long_jobs) / len(work), 1),
            "read_share_pct": round(100 * sum(j["read"] for j in long_jobs) / W["read"], 1),
            "written_share_pct": round(100 * sum(j["out"] for j in long_jobs) / W["out"], 1),
        },
        "top10pct_jobs_read_share_pct": round(100 * sum(j["read"] for j in top10) / W["read"], 1),
        "median_read_per_job_short_vs_32plus": {
            "short_1_3": round(st.median(j["read"] for j in short)),
            "long_32plus": round(st.median(j["read"] for j in work if j["steps"] >= 32)),
        },
        "slopes": slopes,
        "derived": {
            "reading_multiplier_when_steps_double": round(2 ** slopes["all_work_jobs"]["slope"], 1),
            "median_job_read_32plus_over_1_3": round(
                st.median(j["read"] for j in work if j["steps"] >= 32) / st.median(j["read"] for j in short), 0),
            "read_per_step_16_31_over_1_3": round(bins[3]["median_read_per_step"] / bins[0]["median_read_per_step"], 1),
            "read_per_written_64plus_over_1_3": round(bins[5]["read_per_written"] / bins[0]["read_per_written"], 1),
        },
        "compression_threshold_tokens": COMPRESSION_THRESHOLD_TOKENS,
        "codex_double_count_check": {"before_fix": codex(True), "after_fix": codex(False)},
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
