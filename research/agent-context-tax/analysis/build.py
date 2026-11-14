"""Step 3: fill page.template.html with figures from results.json -> ../index.html.

Every number on the published page is inserted here from results.json; the template
holds no figures of its own. The build fails if any ${placeholder} is left unfilled.

Run: python3 build.py
"""
import html
import json
import re
from pathlib import Path
from string import Template

HERE = Path(__file__).parent
R = json.loads((HERE / "results.json").read_text())

READ_COLOR = "#7480ec"   # validated (dataviz validate_palette.js, dark, surface #080912)
JOBS_COLOR = "#b98445"


def n(x):
    return f"{x:,}"


def m(x):
    return f"{x / 1e9:,.2f} billion" if x >= 1e9 else f"{x / 1e6:,.1f} million"


def k(x):
    return f"{x / 1e3:,.1f}K"


def bar(label, pct, color, text, title):
    return (f'<div class="ct-bar" title="{html.escape(title)}"><span class="ct-key">{label}</span>'
            f'<span class="ct-track"><span class="ct-fill" style="width:{pct:.2f}%;background:{color}"></span></span>'
            f'<span class="ct-val">{text}</span></div>')


def chart_share():
    rows = []
    for b in R["bins"]:
        rows.append(
            f'<div class="ct-group"><div class="ct-cat">{b["label"]} steps</div>'
            + bar("Jobs", b["jobs_pct"] / 40 * 100, JOBS_COLOR, f'{b["jobs_pct"]}%',
                  f'{b["label"]} steps: {n(b["jobs"])} jobs, {b["jobs_pct"]}% of all jobs')
            + bar("Reading", b["read_share_pct"] / 40 * 100, READ_COLOR, f'{b["read_share_pct"]}%',
                  f'{b["label"]} steps: {b["read_share_pct"]}% of all tokens read')
            + "</div>")
    return "\n".join(rows)


def chart_per_step():
    top = 100_000
    rows = []
    for b in R["bins"]:
        v = b["median_read_per_step"]
        rows.append(
            f'<div class="ct-group ct-single"><div class="ct-cat">{b["label"]} steps</div>'
            + bar("", v / top * 100, READ_COLOR, k(v),
                  f'{b["label"]} steps: median {n(v)} tokens read per step')
            + "</div>")
    return "\n".join(rows)


def bin_rows():
    return "\n".join(
        f'<tr><td>{b["label"]}</td><td>{n(b["jobs"])} ({b["jobs_pct"]}%)</td><td>{n(b["median_read_per_job"])}</td>'
        f'<td>{n(b["median_read_per_step"])}</td><td>{b["read_per_written"]} : 1</td><td>{b["read_share_pct"]}%</td></tr>'
        for b in R["bins"])


def slope_rows():
    names = {"cli": "Hands-on sessions (terminal)", "subagent": "Sub-agents spawned by another agent",
             "cron": "Scheduled jobs", "oneshot": "One-shot tasks", "telegram": "Chat (Telegram)",
             "api_server": "API requests"}
    out = []
    for src, label in names.items():
        s = R["slopes"]["by_source"].get(src)
        if s:
            out.append(f'<tr><td>{label}</td><td>{n(s["n"])}</td><td>{s["slope"]}</td><td>{s["r2"]}</td></tr>')
    bots = {"operator": "Operator agent", "client_bot_1": "Client reporting agent A",
            "client_bot_2": "Client reporting agent B"}
    for b, label in bots.items():
        s = R["slopes"]["by_bot"][b]
        out.append(f'<tr><td>{label}</td><td>{n(s["n"])}</td><td>{s["slope"]}</td><td>{s["r2"]}</td></tr>')
    return "\n".join(out)


def coverage_rows():
    bots = {"operator": "Operator agent (general business work)", "client_bot_1": "Client reporting agent A",
            "client_bot_2": "Client reporting agent B"}
    out = []
    for b, label in bots.items():
        c = R["coverage"][b]
        out.append(f'<tr><td>{label}</td><td>{c["from"]} → {c["to"]}</td><td>{n(c["jobs"] - c["helper_calls"])}</td>'
                   f'<td>{n(c["helper_calls"])}</td><td>{n(c["steps"])}</td></tr>')
    return "\n".join(out)


W, D, L, S = R["work"], R["derived"], R["long_jobs_16plus"], R["slopes"]
b = {x["label"]: x for x in R["bins"]}
cov = R["coverage"]
values = {
    "jobs": n(W["jobs"]), "steps": n(W["steps"]), "rows": n(R["rows"]),
    "jobs_total": n(R["jobs_total"]), "helpers": n(R["helper_calls_excluded"]),
    "ratio": f'{W["read_per_written"]:g}', "ratio_round": f'{round(W["read_per_written"])}',
    "fresh_ratio": f'{W["fresh_per_written"]:g}', "cached_pct": f'{W["cached_share_of_read_pct"]:g}',
    "written_pct": f'{W["written_share_of_all_pct"]:g}',
    "read_m": m(W["read"]), "fresh_m": m(W["fresh"]), "cached_m": m(W["cached"]), "out_m": m(W["out"]),
    "out_per_step": n(round(W["out"] / W["steps"])),
    "read_b": f'{W["read"] / 1e9:.2f}',
    "all_ratio": f'{R["all_including_helpers"]["read_per_written"]:g}',
    "double": f'{D["reading_multiplier_when_steps_double"]:g}',
    "slope": f'{S["all_work_jobs"]["slope"]:g}', "r2": f'{S["all_work_jobs"]["r2"]:g}',
    "slope_short": f'{S["work_jobs_1_to_15_steps"]["slope"]:g}', "slope_long": f'{S["work_jobs_16plus_steps"]["slope"]:g}',
    "long_jobs": n(L["jobs"]), "long_jobs_pct": f'{L["jobs_pct"]:g}', "long_read_pct": f'{L["read_share_pct"]:g}',
    "long_written_pct": f'{L["written_share_pct"]:g}', "top10_pct": f'{R["top10pct_jobs_read_share_pct"]:g}',
    "ps_short": n(b["1-3"]["median_read_per_step"]), "ps_16": n(b["16-31"]["median_read_per_step"]),
    "ps_32": n(b["32-63"]["median_read_per_step"]), "ps_64": n(b["64+"]["median_read_per_step"]),
    "short_jobs_pct": f'{b["1-3"]["jobs_pct"]:g}', "short_read_pct": f'{b["1-3"]["read_share_pct"]:g}',
    "ps_climb": f'{D["read_per_step_16_31_over_1_3"]:g}',
    "rw_short": f'{b["1-3"]["read_per_written"]:g}', "rw_64": f'{b["64+"]["read_per_written"]:g}',
    "rw_climb": f'{D["read_per_written_64plus_over_1_3"]:g}',
    "job_short": n(R["median_read_per_job_short_vs_32plus"]["short_1_3"]),
    "job_long": n(R["median_read_per_job_short_vs_32plus"]["long_32plus"]),
    "job_climb": f'{D["median_job_read_32plus_over_1_3"]:g}',
    "compress": n(R["compression_threshold_tokens"]),
    "pre_fix": f'{R["codex_double_count_check"]["before_fix"]["fresh_to_cached"]:g}',
    "post_fix": f'{R["codex_double_count_check"]["after_fix"]["fresh_to_cached"]:g}',
    "date_from": min(c["from"] for c in cov.values()), "date_to": max(c["to"] for c in cov.values()),
    "chart_share": chart_share(), "chart_per_step": chart_per_step(),
    "bin_rows": bin_rows(), "slope_rows": slope_rows(), "coverage_rows": coverage_rows(),
    "read_color": READ_COLOR, "jobs_color": JOBS_COLOR,
}

page = Template((HERE / "page.template.html").read_text()).substitute(values)
left = re.findall(r"\$\{\w+\}", page)
assert not left, f"unfilled: {left}"
(HERE.parent / "index.html").write_text(page)
print(f"wrote index.html ({len(page):,} bytes)")
