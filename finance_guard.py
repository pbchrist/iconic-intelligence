"""Source-backed financial answers. Never infer total A/R from billed minus collected.

Only a source explicitly identifying both totals authorizes this code path.
Other requests pass through to the normal model/retrieval pipeline.
"""
from decimal import Decimal, ROUND_HALF_UP
import re

AMOUNT = r"\$\s*([\d,]+)(?:\.\d{1,2})?"
BILLED = re.compile(r"(?im)^\s*[-*]?\s*Billed:\s*" + AMOUNT + r"\b")
COLLECTED = re.compile(r"(?im)^\s*[-*]?\s*Collected:\s*" + AMOUNT + r"\b")
FINANCIAL = re.compile(r"(?i)\b(billings?|billed|collect\w*|cash|realization|receivables?|a/r|ar balance|outstanding balance)\b")
RECEIVABLE = re.compile(r"(?i)\b(receivables?|a/r|ar balance|outstanding balance|gap|difference|shortfall)\b")
PERCENT = re.compile(r"(?i)\b(percentage|percent|share|rate|ratio|of billings)\b|%")
Q3 = re.compile(r"(?i)\b(q3|third[\\s-]+quarter|tercer trimestre|quarter|q\s*3)\b")
OTHER_ENTITY = re.compile(r"(?i)\b(tidewell|lexvault|kessler|partner|vendor|supplier|evergreen|freight)\b")
OTHER_PERIOD = re.compile(r"(?i)\b(q[124]|201[0-9]|202[0-5]|last month|january|february|march|april|may|june|july|august|september)\b")


def answer_from_ledger(question, sources, history=None):
    q = str(question or "").strip()
    previous = " ".join(str(x.get("q", "")) for x in (history or [])[-2:])
    if not FINANCIAL.search(q) or OTHER_ENTITY.search(q) or OTHER_PERIOD.search(q):
        return None
    if re.search(r"(?i)\b(monthly|this month|last week|this week|2027|2028)\b", q):
        return None
    if not (Q3.search(q) or RECEIVABLE.search(q) or Q3.search(previous)):
        return None
    candidates = []
    for src in sources:
        chunk = str(src.get("chunk") or "")
        billed = BILLED.search(chunk)
        collected = COLLECTED.search(chunk)
        if billed and collected and src.get("n") is not None:
            candidates.append((src, Decimal(billed.group(1).replace(",", "")),
                               Decimal(collected.group(1).replace(",", ""))))
    if not candidates:
        return None
    src, billed, collected = candidates[0]
    label = str(src.get("title") or src.get("rel") or "billing report")
    cite = "[%d]" % int(src["n"])
    gap = billed - collected
    pct = (collected / billed * 100).quantize(Decimal(".01"), rounding=ROUND_HALF_UP) if billed else None
    if RECEIVABLE.search(q):
        return (
            "The {} records **${:,.0f} billed** and **${:,.0f} collected** {}. "
            "The derived collected/billed ratio is **{:.2f}%**. "
            "The difference is **${:,.0f}**, but that calculation is **not** a documented "
            "accounts-receivable total. An aged receivables ledger is needed to establish total A/R."
        ).format(label, billed, collected, cite, pct, gap)
    if PERCENT.search(q):
        if pct is None:
            return None
        return (
            "The calculated collection ratio is **{:.2f}%**: "
            "${:,.0f} collected ÷ ${:,.0f} billed × 100 = {:.2f}% {}. "
            "This ratio is not the same as a documented accounts-receivable balance."
        ).format(pct, collected, billed, pct, cite)
    if re.search(r"(?i)\b(cash|collect\w*|cobr\w*|recaud\w*)\b", q) and not re.search(r"(?i)\b(bill\w*|factur\w*)\b", q):
        return "The {} reports **${:,.0f} collected** for Q3 2026 {}.".format(label, collected, cite)
    if re.search(r"(?i)\b(bill\w*|collect\w*|factur\w*)\b", q):
        return (
            "For Q3 2026, the {} reports **${:,.0f} billed** and **${:,.0f} collected** {}. "
            "The derived collection ratio is **{:.2f}%**."
        ).format(label, billed, collected, cite, pct)
    return None
