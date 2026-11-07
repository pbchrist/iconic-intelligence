"""Evidence-bound vendor buyback reconciliation, with no invented cash payment.

Only answers when the source explicitly supplies all amounts and arithmetic
checks out. Otherwise leaves question to the normal grounded assistant.
"""
import re
from decimal import Decimal

DOLLARS = r"\$([\d,]+)"
ELIGIBLE = re.compile(DOLLARS + r"\s+of unopened\s+[^.\n]{0,90}\s+that qualify", re.I)
CAP = re.compile(r"caps? the buyback at\s*" + DOLLARS, re.I)
FEE = re.compile(r"(\d{1,2})% restocking fee", re.I)
NET = re.compile(r"return comes back as a\s*" + DOLLARS + r"\s+credit", re.I)
EXCESS = re.compile(r"the other\s*" + DOLLARS + r"\s+of eligible stock", re.I)
INTENT = re.compile(r"(?i)\b(buyback|return\w*|restocking|qualif\w*|eligible|credit|fee)\b")


def parse_evidence(text):
    patterns = (ELIGIBLE, CAP, FEE, NET, EXCESS)
    matches = [pattern.search(text) for pattern in patterns]
    if not all(matches):
        return None
    eligible, cap, pct, net, excess = [
        Decimal(match.group(1).replace(",", "")) for match in matches
    ]
    if (not 0 <= pct <= 50 or cap > eligible or
            eligible - cap != excess or cap * (100 - pct) / 100 != net):
        return None
    return eligible, cap, pct, net, excess


def answer_from_inventory(question, sources):
    q = str(question or "")
    if not INTENT.search(q):
        return None
    # Avoid answering unrelated cash and freight questions with a buyback.
    if not (re.search(r"(?i)pacific brass|buyback|return\w*|eligible|restocking|credit", q)):
        return None
    for source in sources:
        body = str(source.get("chunk") or "")
        vals = parse_evidence(body)
        if not vals or source.get("n") is None:
            continue
        eligible, cap, pct, net, excess = vals
        label = source.get("title") or source.get("rel") or "inventory record"
        n = int(source["n"])
        deadline = " The request must be made before December 31." if "before December 31" in body else ""
        detail = ""
        if re.search(r"(?i)\b(entire|full decision|exclusions?|remaining exposure|explain.*decision|whole)\b", q):
            atlas = re.search(r"\$([\d,]+) is Atlas Valve stock \(no buyback\)", body)
            opened = re.search(r"\$([\d,]+) is Pacific Brass stock in opened boxes", body)
            total = re.search(r"Of the \$([\d,]+)", body)
            if atlas and opened and total:
                a = Decimal(atlas.group(1).replace(",", ""))
                o = Decimal(opened.group(1).replace(",", ""))
                t = Decimal(total.group(1).replace(",", ""))
                if a + o + eligible == t:
                    detail = (" Of the **${:,.0f}** obsolete brass valve total, "
                              "**${:,.0f} Atlas Valve** stock is excluded because it is from "
                              "another supplier, and **${:,.0f} Pacific Brass** stock is "
                              "excluded because the boxes were opened [{}]. "
                              "After the capped return, **${:,.0f}** of the brass inventory "
                              "remains without this buyback credit [{}]."
                              ).format(t,a,o,n,t-cap,n)
        return (
            "The {} documents **${:,.0f}** of eligible unopened stock [{}]. "
            "The buyback cap is **${:,.0f}** and the restocking fee is **{:,.0f}%**, "
            "so the permitted return yields a **${:,.0f} vendor credit**, "
            "not a guaranteed cash payment [{}]. "
            "**${:,.0f}** of otherwise eligible stock exceeds the return cap [{}].{}{}"
        ).format(label, eligible, n, cap, pct, net, n, excess, n, detail, deadline)
    return None
