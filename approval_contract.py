"""Business-independent approval and decision-status evidence operation.

'Feasible', 'proposed' and 'a decision is due' are NOT an approval.
Classifies only explicit, relevant documentary statements, ordered by their
document dates, with exact quoted provenance. If evidence is ambiguous,
return uncertainty rather than pretending an action was approved.
"""
from dataclasses import dataclass
from datetime import date
import re

_APPROVAL_ASK = re.compile(
    r"(?i)\b(?:approved|approval|signed\s*off|sign[- ]off|authorized|"
    r"green[- ]lit|greenlight|go[- ]ahead|given\s+the\s+go[- ]ahead|"
    r"decided\s+on|final\s+decision)\b"
)
_GO = re.compile(
    r"(?i)\b(?:approved|signed\s*off|authorized|green[- ]lit|"
    r"greenlight|gave\s+(?:it|the\s+\w+)\s+the\s+go[- ]ahead)\b"
)
_NO = re.compile(
    r"(?i)\b(?:not\s+(?:yet\s+)?approved|never\s+approved|"
    r"approval\s+(?:has\s+)?not\s+been\s+granted|"
    r"not\s+authorized|declined|rejected|denied)\b"
)
_PENDING = re.compile(
    r"(?i)\b(?:to\s+decide\s+by|will\s+decide|awaiting|"
    r"pending|under\s+consideration|still\s+under\s+review|"
    r"not\s+yet\s+decided|final\s+sign[- ]off\s+pending|"
    r"decision\s+(?:is\s+)?(?:due|expected)|proposed)\b"
)
_WORD = re.compile(r"[a-z][a-z0-9'-]{2,}")
_IGNORED = frozenset("""has have did was were the our their your this that
with about from already yet its what newest latest older record records
use tell file document source who which whether something different
approved approval authorization authorize decision sign signed off
final status business company person been made does says show me if
when is it a in on for to of by and than whether change""".split())


@dataclass(frozen=True)
class ApprovalResult:
    text: str
    status: str
    source_id: int | None
    source_number: int | None
    exact_quote: str
    verified: bool


def is_status_question(question):
    return bool(_APPROVAL_ASK.search(str(question or "")))


def words(text):
    return {w for w in _WORD.findall(str(text or "").lower()) if w not in _IGNORED}


def classification(line):
    if _NO.search(line):
        return "not_approved"
    if _PENDING.search(line):
        return "pending"
    if _GO.search(line):
        # "Could be approved" and "approval is possible" are speculation.
        if re.search(r"(?i)\b(?:could|may|might|potentially|possibly|"
                     r"if\b.{0,45}\bapproved)\b",line):
            return "unknown"
        return "approved"
    return "unknown"


def extract_approval(question,sources):
    if not is_status_question(question):
        return None
    topics=words(question)
    candidates=[]
    for src in sources:
        n=src.get("n")
        if not isinstance(n,int):
            continue
        doc_date=str(src.get("date") or "")
        for raw in str(src.get("chunk") or "").splitlines():
            line=raw.strip()
            if not line or len(line)>700 or re.fullmatch(r"[-| :]+",line):
                continue
            state=classification(line)
            if state=="unknown":
                continue
            shared=words(line) & topics
            if len(shared)<2:
                continue
            # Statement must be about the requested action, not some other
            # unrelated approval in the same meeting.
            score=len(shared)
            candidates.append((doc_date,score,int(n),src["id"],state,line))
    if not candidates:
        return ApprovalResult(
            "I cannot confirm an approval from the available records. "
            "No relevant, explicit approval decision was found. Feasibility, "
            "a proposal, or a decision deadline is not proof of approval.",
            "unverified",None,None,"",False)
    # First prioritize the subject of the question, then the date on which
    # a source was written. A later explicit decision supersedes old proposals.
    topical=max(c[1] for c in candidates)
    relevant=[c for c in candidates if c[1]>=max(2,topical-1)]
    newest=max(c[0] for c in relevant)
    latest=[c for c in relevant if c[0]==newest]
    # Ambiguity among equally current relevant records cannot be resolved
    # safely by picking whichever line happens to be listed last.
    states={c[4] for c in latest}
    if len(states)>1:
        return ApprovalResult(
            "The latest relevant records conflict on approval status. "
            "I cannot confirm that the action was approved without a "
            "subsequent decision record.",
            "conflicting",None,None,"",False)
    latest.sort(key=lambda c:(-c[1],c[2]))
    chosen=latest[0]
    date_label=chosen[0] or "the most recent record"
    line=chosen[5]
    number=chosen[2]
    if chosen[4]=="approved":
        headline="**Approved in the latest documented record.** "
    elif chosen[4]=="not_approved":
        headline="**Not approved in the latest documented record.** "
    else:
        headline="**No final approval is documented.** "
    body=(headline+"The relevant record dated "+date_label+
          " states: “"+line+"” ["+str(number)+"]. ")
    if chosen[4]=="pending":
        body+=("That describes a pending decision, not completed approval. "
               "A deadline for deciding does not establish that a decision occurred.")
    elif chosen[4]=="not_approved":
        body+="The source explicitly rules out treating the proposal as approved."
    else:
        body+="This is a documented approval, not merely a statement of feasibility."
    if re.search(r"(?i)\b(?:older|earlier|previous|different)\b",str(question)):
        older=[c for c in relevant if c[0]<newest and c[4] in
               ("pending","not_approved","approved")]
        older.sort(key=lambda c:(-int(c[0].replace("-","")) if
                                 c[0].replace("-","").isdigit() else 0,
                                 -c[1],c[2]))
        if older:
            entry=older[0]
            body+=(" An earlier record dated "+str(entry[0])+
                   " said: “"+entry[5]+"” ["+str(entry[2])+"].")
    return ApprovalResult(body,chosen[4],chosen[3],number,line,True)


def verify_approval(result,sources):
    if not isinstance(result,ApprovalResult) or not result.verified:
        return False
    match=next((s for s in sources
                if s.get("id")==result.source_id and
                   s.get("n")==result.source_number),None)
    return bool(match and result.exact_quote in str(match.get("chunk") or "")
                and ("["+str(result.source_number)+"]") in result.text)
