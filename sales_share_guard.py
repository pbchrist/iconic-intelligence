"""Evidence-backed Q3 sales-share arithmetic. Never turn rounding into exact equality."""
from decimal import Decimal, ROUND_HALF_UP
import re

SUMMARY = re.compile(r"(?im)^\s*[-*]\s*Revenue:\s*\$\s*([\d,.]+)\s*(million|thousand)?\b")
TOP = re.compile(r"(?im)^\s*Top accounts by Q3 sales:\s*(.*)$")
NAME_VALUE = re.compile(r"([A-Z][A-Za-z&.' -]+?)\s+\$([\d,]+)\s*\((\d+(?:\.\d+)?)% of sales\)")
LISTED = re.compile(r"(?im)^\s*\d+\.\s*([^:]+):\s*(\d+(?:\.\d+)?)% of sales")
INTENT = re.compile(r"(?i)\b(reconcil\w*|calculat\w*|percent\w*|percentage\w*|share\w*|actual)\b")


def answer_from_sales(question, sources):
    q=str(question or "")
    if not INTENT.search(q) or not re.search(r"(?i)\b(q3|sales|revenue|accounts|evergreen)\b",q):
        return None
    summaries=[]
    accounts=[]
    for src in sources:
        text=str(src.get("chunk") or "")
        rev=SUMMARY.search(text)
        top=TOP.search(text)
        if rev and top:
            mval=Decimal(rev.group(1).replace(",",""))
            unit=(rev.group(2) or "").lower()
            total=mval*(1000000 if unit=="million" else 1000 if unit=="thousand" else 1)
            summaries.append((src,total,[(m.group(1).strip(),Decimal(m.group(2).replace(",","")),Decimal(m.group(3))) for m in NAME_VALUE.finditer(top.group(1))]))
        if "key-accounts" in (src.get("rel") or "").lower() or "key accounts" in (src.get("title") or "").lower():
            accounts.extend((src,m.group(1).strip(),Decimal(m.group(2))) for m in LISTED.finditer(text))
    for src,total,rows in summaries:
        for account,sales,listed_percent in rows:
            if account.casefold() not in q.casefold() and account.split()[0].casefold() not in q.casefold():
                continue
            matching=[(doc,percent) for doc,name,percent in accounts if name.casefold()==account.casefold()]
            if not matching or total <= 0:
                return None
            doc,key_pct=matching[0]
            ratio=sales/total*100
            rounded=ratio.quantize(Decimal("1"),rounding=ROUND_HALF_UP)
            if rounded != listed_percent or rounded != key_pct:
                return (
                    "The two sources do not reconcile: {} is listed at {:.0f}% in the sales summary [{}] "
                    "and {:.0f}% in the key-account file [{}], but the actual ratio is {:.2f}% "
                    "(${:,.0f} ÷ ${:,.0f} × 100)."
                ).format(account,listed_percent,src["n"],key_pct,doc["n"],
                         ratio,sales,total)
            difference = sales - (listed_percent/100*total)
            return (
                "**They reconcile only after rounding, not as an exact percentage.** "
                "{} had **${:,.0f}** in Q3 sales out of **${:,.0f}** total revenue [{}]. "
                "${:,.0f} ÷ ${:,.0f} × 100 = **{:.4f}%**, which rounds to **{:.0f}%**. "
                "Both the sales summary [{}] and key-accounts file [{}] report {:.0f}%; "
                "the exact share is lower by {:.2f} percentage points (${:,.0f} below an exact {:.0f}% of total revenue)."
            ).format(account,sales,total,src["n"],sales,total,ratio,rounded,
                     src["n"],doc["n"],listed_percent,listed_percent-ratio,abs(difference),listed_percent)
    return None
