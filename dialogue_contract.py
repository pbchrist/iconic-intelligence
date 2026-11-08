"""Shared conversational intent and evidence continuity contracts.

No customer-specific business constants. Client-side source mappings are
treated as untrusted hints and resolved exclusively against the currently
selected workspace's indexed documents.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

CREATIVE_REQUEST = re.compile(
    r"(?i)^\s*(?:(?:please|can you|could you|would you|hey|just)\s+)*"
    r"(?:write|compose|create|make|tell me|give me|draft)\b"
)
CREATIVE_FORMAT = re.compile(
    r"(?i)\b(poem|haiku|limerick|rhyme|fictional story|bedtime story|"
    r"joke|riddle|fairy tale|tongue twister)\b"
)
BUSINESS_SOURCE_QUALIFIER = re.compile(
    r"(?i)\b(?:based on|using|cite|reference|according to|"
    r"from|about)\s+(?:our|the company's|company|business|"
    r"this company's|those|these)\b|"
    r"\b(?:document|report|ledger|invoice|vendor|customer|"
    r"client|financial|internal file|contract|sourcing)\b"
)
PREVIOUS_SOURCE = re.compile(
    r"(?i)\b(?:source|citation|file|document|card)\s*"
    r"(?:#\s*(\d{1,3})|\[\s*(\d{1,3})\s*\]|(\d{1,3}))"
)


def _source_number(hit):
    return int(next(part for part in hit.groups() if part))
TOPIC_ANCHOR = re.compile(
    r"(?i)\b(?:about|regarding|concerning|with|for)\s+"
    r"(?!us\b|our\s+company\b|the\s+business\b)"
    r"\w[\w'-]+"
)
GENERAL_RISK_REQUEST = re.compile(
    r"(?i)\b(?:biggest|largest|top|main|primary|most pressing)\b"
    r".{0,65}\b(?:risk|problem|issue|priority|concern)\b"
)
BROAD_BUSINESS = re.compile(
    r"(?i)^\s*(?:what(?:'s| is)\s+(?:happening|going on|new|urgent|important|"
    r"our biggest risk|worth knowing)|what\s+should\s+(?:i|we)\s+"
    r"(?:know|focus on|prioritize)|give me\s+(?:an?\s+)?"
    r"(?:overview|summary|briefing)|any(?:thing)?\s+(?:new|urgent))"
    r"(?:\s+(?:at|in|for)\s+(?:the\s+)?(?:business|company|firm))?\s*[?!.,]*\s*$"
)


def intent(question):
    """Return a generic task label based on request semantics, not tenant names."""
    q = str(question or "").strip()
    if CREATIVE_REQUEST.search(q) and CREATIVE_FORMAT.search(q) and not BUSINESS_SOURCE_QUALIFIER.search(q):
        return "creative"
    if PREVIOUS_SOURCE.search(q):
        return "prior_source_challenge"
    if (BROAD_BUSINESS.search(q) or GENERAL_RISK_REQUEST.search(q)) and not TOPIC_ANCHOR.search(q):
        return "company_overview"
    return "business_query"


def previous_source(number, history, workspace):
    """Resolve a *previous* response's source label against current tenant.

    Returns the doc record if exact (id AND rel) match; otherwise None.
    Never follow supplied URLs, paths or tenant IDs from untrusted history.
    """
    if not isinstance(history,list):
        return None
    with workspace.lock:
        own_docs={(int(d["id"]),str(d["rel"])):d for d in workspace.docs}
    # An unqualified "source [n]" means the *most recent response*, never
    # an older response whose own [n] happens to differ.
    for record in history[-1:]:
        if not isinstance(record,dict):
            continue
        sources=record.get("sources") or []
        if not isinstance(sources,list):
            continue
        for s in sources[:24]:
            if not isinstance(s,dict):
                continue
            try:
                n=int(s.get("n"))
                id=int(s.get("id"))
            except (ValueError,TypeError,OverflowError):
                continue
            if n==number:
                return own_docs.get((id,str(s.get("rel") or "")))
    return None


def referenced_prior_document(question,history,workspace):
    found=PREVIOUS_SOURCE.search(str(question or ""))
    if not found:
        return None
    return previous_source(_source_number(found),history,workspace)


def recent_source_mapping(question,history,workspace,current_sources):
    found=PREVIOUS_SOURCE.search(str(question or ""))
    if not found:
        return ""
    n=_source_number(found)
    old=previous_source(n,history,workspace)
    if old is None:
        return ("The visitor refers to a prior source number ["+str(n)+"], but its "
                "earlier source-card mapping is unavailable or not in this workspace. "
                "Do NOT guess its identity or claim to have checked it. "
                "Ask the visitor to open the earlier source card or identify the document.")
    new=next((src for src in current_sources if src.get("id")==old["id"] and
              src.get("rel")==old["rel"]),None)
    if new:
        return ("PREVIOUS SOURCE REFERENCE: The visitor's prior source ["+
                str(n)+"] was the authorized document '"+old["title"]+
                "' ("+old["rel"]+"). The SAME document is now source ["+
                str(new["n"])+"]. Verify the particular claim against its contents; "
                "cite the CURRENT number, not the older one. If the precise claim "
                "is absent, say so.")
    return ("The prior source ["+str(n)+"] resolves to '"+old["title"]+
            "' but was not included in the current evidence. Do not infer its contents.")


# A source-number challenge is a typed evidence operation, not a generative
# prompt. A prior [2] is a label in an *earlier* response, not an invitation
# for the model to pick the latest source [2] at random.
_CITATION = re.compile(r"\[(\d{1,3})\]")
_TOKEN = re.compile(r"[a-z][a-z0-9'-]{2,}|\$[\d,]+|\d+(?:\.\d+)?%")
_NONFACT_WORDS = {
    "the","and","that","this","your","from","what","where","which","show",
    "give","cited","cite","source","sourced","document","file","answer",
    "previous","citation","number","exact","sentence","claim","support",
    "quote","line","please","they","them","was","were","for","have","with",
    "about","there","these","those","then","than","into","upon","said",
    "rate","number","amount","percent","according","actually","says",
}


@dataclass(frozen=True)
class PriorSourceProof:
    text: str
    source_id: int | None
    source_number: int | None
    excerpt: str
    verified: bool


def _fact_tokens(text):
    return {t.strip("'") for t in _TOKEN.findall(str(text).casefold())
            if t not in _NONFACT_WORDS}


def _cited_claim(previous_answer, number):
    """Retrieve the sentence/paragraph preceding this precise prior citation."""
    previous_answer=str(previous_answer or "")
    candidates=[]
    for hit in _CITATION.finditer(previous_answer):
        if int(hit.group(1))!=number:
            continue
        before=previous_answer[:hit.start()]
        start=max(before.rfind("\n\n"),before.rfind(".\n"),before.rfind(". "),before.rfind("! "))
        fragment=before[start+2:].strip(" \n:-*")
        if len(fragment)<15:
            fragment=before[-420:].strip()
        candidates.append(fragment[-600:])
    return candidates[-1] if candidates else ""


def verify_prior_source_proof(proof,sources,workspace):
    if not isinstance(proof,PriorSourceProof) or not proof.verified:
        return False
    if not proof.excerpt or proof.source_id is None or proof.source_number is None:
        return False
    matching=next((x for x in sources
                   if x.get("id")==proof.source_id and x.get("n")==proof.source_number),None)
    if not matching:
        return False
    with workspace.lock:
        document=next((d for d in workspace.docs
                       if d["id"]==proof.source_id and d["rel"]==matching.get("rel")),None)
    return bool(document and proof.excerpt in document["text"]
                and ("["+str(proof.source_number)+"]") in proof.text)


def answer_prior_source(question,history,workspace,current_sources):
    """Return an exact authorized source excerpt or a transparent abstention.

    The source has to be the document named in the *previous turn's* citation
    mapping, independently verified against the selected workspace index.
    The previous answer's claim is used for ranking excerpts, not as evidence.
    """
    mark=PREVIOUS_SOURCE.search(str(question or ""))
    if not mark:
        return None
    n=_source_number(mark)
    own=previous_source(n,history,workspace)
    if own is None:
        return PriorSourceProof(
            "I can't verify what source #"+str(n)+" referred to in the previous "
            "answer because its original source-card mapping isn't available "
            "in this business's conversation. Please open that source card "
            "or identify the document.",
            None,None,"",False)
    current=next((s for s in current_sources
                  if s.get("id")==own["id"] and s.get("rel")==own["rel"]),None)
    if current is None:
        return PriorSourceProof(
            "The prior source #"+str(n)+" was '"+str(own["title"])+
            "', but I can't retrieve its text in the current evidence set. "
            "I won't guess what it says.",
            None,None,"",False)
    # A visitor may specifically challenge whether this prior source supports
    # a quoted amount or percentage that belongs to a DIFFERENT document.
    # Check the requested figure against the actual file before selecting
    # any other row and accidentally appearing to substantiate it.
    requested_numbers = re.findall(
        r"\$\s*[\d,]+(?:\.\d+)?|\b\d+(?:\.\d+)?%",
        str(question or ""))
    source_digits = re.sub(r"[,\s]", "",str(own.get("text") or ""))
    absent=[x for x in requested_numbers
            if re.sub(r"[,\s]","",x) not in source_digits]
    if absent:
        # Find a genuine alternate document from the previous *same-business*
        # source list. Do not fabricate a new citation in this answer.
        alternative=""
        prior=history[-1].get("sources") if history and isinstance(history[-1],dict) else []
        with workspace.lock:
            owned={(d["id"],d["rel"]):d for d in workspace.docs}
        for raw in prior if isinstance(prior,list) else []:
            if not isinstance(raw,dict):
                continue
            try:
                key=(int(raw.get("id")),str(raw.get("rel")))
                old_num=int(raw.get("n"))
            except (TypeError,ValueError):
                continue
            other=owned.get(key)
            if other and other["id"]!=own["id"] and all(
                    re.sub(r"[,\s]","",x) in
                    re.sub(r"[,\s]","",other["text"]) for x in absent):
                alternative=(" The requested number instead appears in '"+
                             str(other["title"])+"' (previous source #"+
                             str(old_num)+").")
                break
        return PriorSourceProof(
            "The previous source #"+str(n)+" was '"+str(own["title"])+
            "'. It does **not** contain the requested figure "+
            ", ".join(absent)+"; I cannot quote that figure from this source."+
            alternative,None,None,"",False)
    before=history[-1].get("a","") if history and isinstance(history[-1],dict) else ""
    claim=_cited_claim(before,n)
    if not claim:
        return PriorSourceProof(
            "The previous answer did not contain a citation #"+str(n)+" "
            "that I can match to a specific claim. The source card maps to "
            "'"+str(own["title"])+"', but I cannot claim it supports "
            "a statement without identifying that statement.",
            None,None,"",False)
    facts=_fact_tokens(claim)
    cited_numbers={x for x in facts if x[0].isdigit() or x[0]=="$"}
    options=[]
    for raw in str(own.get("text") or "").splitlines():
        line=raw.strip()
        if not line or len(line)>700 or re.fullmatch(r"[-| :]+",line):
            continue
        own_terms=_fact_tokens(line)
        common=facts & own_terms
        common_numerics=cited_numbers & own_terms
        score=len(common)*2+len(common_numerics)*9
        if score>0:
            options.append((score,len(common),len(common_numerics),line))
    options.sort(key=lambda x:(-x[0],-x[2],-x[1],len(x[3])))
    best=options[0] if options else None
    # If a challenged amount/percentage cannot be found in a passage, showing
    # an unrelated row would give the appearance of support without substance.
    supported=(best is not None and best[1]>=2 and
               (not cited_numbers or best[2]>=1))
    if not supported:
        return PriorSourceProof(
            "The earlier source #"+str(n)+" was '"+str(own["title"])+
            "', now numbered ["+str(current["n"])+"]. I cannot find a "
            "matching passage in that document that substantiates the "
            "specific claim from my previous answer. That citation should "
            "not be treated as verified.",
            None,None,"",False)
    excerpt=best[3]
    number=int(current["n"])
    answer=("The prior source #"+str(n)+" was **"+str(own["title"])+
            "**. It is source ["+str(number)+"] in this answer.\n\n"+
            "The relevant text in that document reads:\n\n"+
            '“'+excerpt+'” ['+str(number)+']\n\n'+
            "That is the exact passage. It does not, by itself, verify "
            "any other claims from the previous answer.")
    return PriorSourceProof(answer,int(own["id"]),number,excerpt,True)
