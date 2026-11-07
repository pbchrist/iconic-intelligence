"""Business-agnostic intent + documentary evidence contracts.

A single shared intent gate prevents a numeric/report keyword from hijacking
a person/attribution question. Documentary authorship is extracted from cited
source text, never an assumed staff roster or hard-coded business. This is an
isolated foundation for a general evidence pipeline, NOT a universal fact
verifier and NOT an automatic deployment approval.
"""
from dataclasses import dataclass
import re

AUTHOR_INTENT = re.compile(
    r"(?i)\b(?:"
    r"who\s+(?:actually\s+)?(?:prepared|wrote|authored|compiled|created|produced|assembled)"
    r"|(?:report|document|memo|summary|spreadsheet|statement)\s+(?:author|preparer|writer)"
    r"|(?:prepared|written|authored|compiled)\s+by\s+whom"
    r")\b"
)
BYLINE = re.compile(
    r"(?im)^\s*(?:Prepared|Written|Authored|Compiled|Created)\s+by:\s*"
    r"([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})\.?\s*$"
    r"|^\s*(?:Prepared|Written|Authored|Compiled|Created)\s+by\s+"
    r"([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})\.?\s*$"
)
WORD = re.compile(r"[A-Za-z0-9]+")
IGNORE = frozenset("""who our was were is the a an and what tell did me about
minute ago of for from please report document summary author preparer
prepared wrote written created compiled produced authored by which
their this that his her its to in into with at as""".split())


@dataclass(frozen=True)
class Intent:
    kind: str
    needs_sources: bool = True


@dataclass(frozen=True)
class EvidenceAnswer:
    content: str
    source_ids: tuple
    operation: str


def classify(question):
    q = str(question or "").strip()
    if AUTHOR_INTENT.search(q):
        return Intent("document_attribution")
    return Intent("general")


def terms(text):
    return {v.casefold() for v in WORD.findall(str(text or "")) if v.casefold() not in IGNORE}


def documentary_author(question, sources, history=None):
    """Answer any byline question from its cited document, without known names.

    Requires a plausible question/document match; refuse to extrapolate a
    byline from a different retrieved document. A report with no author stays
    unknown and the main model can answer cautiously.
    """
    if classify(question).kind != "document_attribution":
        return None
    main_question = re.split(r"(?i)\s*,?\s+and\s+what\s+did\s+(?:you|we)\s+", question, maxsplit=1)[0]
    qterms = terms(main_question)
    candidates = []
    for src in sources:
        if src.get("n") is None or not src.get("chunk"):
            continue
        # Only match byline from the exact retrieved evidence, not user text.
        byline = BYLINE.search(str(src["chunk"]))
        if not byline:
            continue
        author = (byline.group(1) or byline.group(2) or "").strip().rstrip(".")
        title = str(src.get("title") or src.get("rel") or "").strip()
        title_tokens = terms(title + " " + str(src.get("rel") or "").replace("-", " "))
        overlap = qterms & title_tokens
        # A report term alone is too broad to attribute a particular person.
        if not overlap:
            continue
        score = 3 * len(overlap) + len(qterms & terms(src.get("chunk","")[:150]))
        candidates.append((score, src, title, author))
    if not candidates:
        return None
    candidates.sort(key=lambda t: (-t[0], int(t[1]["n"])))
    best = candidates[0]
    if len(candidates)>1 and best[0] == candidates[1][0] and best[3] != candidates[1][3]:
        # Two equally relevant competing bylines: abstain from a false certainty.
        return None
    _, src, title, author = best
    n = int(src["n"])
    result = "The **{}** was prepared by **{}** [{}].".format(title, author, n)
    # This form of follow-up explicitly asks for recollection. All history is
    # tenant-scoped by the web client; never invent another workspace's chats.
    if re.search(r"(?i)\bwhat\s+did\s+(?:you|we)\s+(?:tell|say)\b", str(question)):
        hist = " ".join(str(h.get("q",""))+" "+str(h.get("a","")) for h in (history or [])[-3:])
        if not hist.strip():
            result += " There is no earlier discussion of that topic in this business's conversation."
    return EvidenceAnswer(result, (src.get("id"),), "document_attribution")


def verify_documentary_answer(answer, sources):
    """Machine-check the narrow extracted-byline claim; not arbitrary LLM prose."""
    if not isinstance(answer,EvidenceAnswer) or answer.operation!="document_attribution":
        return False
    refs={int(s["n"]):s for s in sources if s.get("n") is not None}
    ids={s.get("id") for s in sources}
    if not set(answer.source_ids).issubset(ids):
        return False
    cites={int(x) for x in re.findall(r"\[(\d+)\]",answer.content)}
    if len(cites)!=1 or not cites.issubset(refs):
        return False
    source=refs[next(iter(cites))]
    match=BYLINE.search(str(source.get("chunk","")))
    return bool(match and (match.group(1) or match.group(2)).strip().rstrip(".") in answer.content)
