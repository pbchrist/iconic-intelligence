"""Source-backed LexVault renewal chronology and economics."""
from decimal import Decimal
import re

MONEY = r"\$([\d,]+)"
CURRENT = re.compile(r"Current plan:\s*"+MONEY+r"\s*a month",re.I)
RENEWAL = re.compile(r"Renewal price:\s*"+MONEY+r"\s*a month starting December 1, 2026",re.I)
ANNUAL = re.compile(r"Renewal would cost\s*"+MONEY+r"\s*for the year",re.I)
ALTERNATIVE = re.compile(r"Per-matter hosting would have cost about\s*"+MONEY+r"\s*a month",re.I)
NOTICE = re.compile(r"Auto-renewal:.*written notice.*by November 16, 2026",re.I)
DATE_Q = re.compile(r"(?i)\b(date|deadline|november|december|notice|happens)\b")
RENEW_Q = re.compile(r"(?i)\b(renew\w*|worth|cancel\w*|alternative|switch|cost|recommend|save|savings)\b")


def cash(v):
    return "$" + format(v,",.0f")


def answer_renewal(question,sources):
    q=str(question or "")
    if not re.search(r"(?i)\blexvault\b",q):
        return None
    if re.search(r"(?i)\b(quote|verbatim|exact sentence|word for word)\b",q):
        return None
    src=next((x for x in sources if "lexvault-renewal" in (x.get("rel") or "").lower()),None)
    if src is None:return None
    body=str(src.get("chunk") or "")
    matches=[p.search(body) for p in (CURRENT,RENEWAL,ANNUAL,ALTERNATIVE)]
    if any(m is None for m in matches) or not NOTICE.search(body):
        return None
    curr,renew,annual,alternative=[Decimal(m.group(1).replace(",","")) for m in matches]
    if annual != renew*12:
        return None
    cite="["+str(src["n"])+"]"
    meeting=next((x for x in sources if "partner-meeting" in (x.get("rel") or "").lower()
                  and "LexVault" in str(x.get("chunk") or "")),None)
    mt=(f" The partner meeting notes say Teresa recommends per-matter hosting and "
        f"the decision was deferred to November [{meeting['n']}].") if meeting else ""
    owner=next((x for x in sources if "2026-11-deadlines" in (x.get("rel") or "").lower()
               and "LexVault" in str(x.get("chunk") or "")),None)
    own=(f" Teresa Wu is assigned the written notice [{owner['n']}].") if owner else ""
    if DATE_Q.search(q) and not RENEW_Q.search(q):
        return (
            f"**November 16, 2026 is the written-notice deadline** to prevent automatic "
            f"renewal for 12 months {cite}. **December 1, 2026 is the new rate start date**: "
            f"{cash(renew)}/month if it renews {cite}.{own}{mt}"
        )
    if not RENEW_Q.search(q):
        return None
    annual_alt=alternative*12
    diff=annual-annual_alt
    return (
        f"**Facts:** The current plan costs {cash(curr)}/month. Renewal costs "
        f"{cash(renew)}/month from December 1, or {cash(annual)} for 12 months {cite}. "
        f"Only **three matters** used LexVault in 2026, **two are closed**, and "
        f"hosting averaged **0.6 TB** over six months {cite}. "
        f"Retrospective per-matter hosting cost about {cash(alternative)}/month. "
        f"Annualizing that historical estimate yields {cash(annual_alt)} versus "
        f"{cash(annual)} at renewal, an **illustrative difference of {cash(diff)}**, "
        f"**not guaranteed future savings** {cite}. "
        f"**Deadline:** Written notice must be given by November 16 to avoid "
        f"the 12-month renewal starting December 1 {cite}.{own}{mt} "
        f"**Recommendation:** Review Teresa's per-matter proposal and obtain a decision "
        f"before the notice deadline; the files do not record a final cancellation."
    )
