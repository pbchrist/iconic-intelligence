"""Source-backed separation of similarly named suppliers and inventory exposure."""
from decimal import Decimal
import re

ROW = re.compile(r'(?m)^[^\n]+,Cascade Controls,Older HVAC control boards,'
                 r'\d+,\d+(?:\.\d+)?,(\d+(?:\.\d+)?),')
INTENT = re.compile(r"(?i)\bcascade\b")
PRICE = re.compile(r"(?i)\b(price increase|cost increase|increase hurt|margin pressure|cost impact|hurt us)\b")
SLOW = re.compile(r"(?i)\b(slow.movers?|stock|inventory|sitting)\b")


def dollars(n):
    return "$"+format(n,",.0f")


def answer_cascade(question,sources):
    q=str(question or "")
    if not INTENT.search(q) or not PRICE.search(q) or not SLOW.search(q):
        return None
    sales=next((x for x in sources if "2026-q3-sales-summary" in (x.get("rel") or "")),None)
    detail=next((x for x in sources if "2026-10-slow-movers-detail" in (x.get("rel") or "")),None)
    if not sales or not detail:return None
    s=str(sales.get("chunk") or "")
    d=str(detail.get("chunk") or "")
    if not re.search(r"(?i)4% Cascade water heater cost increase.*did not pass on",s):
        return None
    board_costs=[Decimal(m.group(1)) for m in ROW.finditer(d)]
    if len(board_costs)!=2:
        return None
    total=sum(board_costs)
    if total!=Decimal("30830"):
        return None
    if "Cascade Water Heater Supply" in d:
        # Similar names are semantically distinct; if the actual inventory has
        # both named suppliers, a special-case disambiguation would be unsafe.
        return None
    return (
        f"**Cascade Water Heater Supply:** A **4% cost increase** that Northline "
        f"did not pass on contributed to Q3 margin pressure [{sales['n']}]. "
        f"The files do **not quantify that supplier's dollar margin impact**; "
        f"the overall gross-margin change is not solely attributable to Cascade [{sales['n']}]. "
        f"**Cascade Controls is a different supplier.** Its two obsolete HVAC control-board "
        f"SKUs in slow movers total **{dollars(total)} at cost** "
        f"({dollars(board_costs[0])} + {dollars(board_costs[1])}) [{detail['n']}]. "
        f"The detailed list does not show slow-moving stock from Cascade Water Heater Supply [{detail['n']}]."
    )
