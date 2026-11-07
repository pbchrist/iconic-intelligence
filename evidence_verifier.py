"""Conservative evidence checks and reproducible arithmetic for ICONIC.

These checks verify *references and calculable structure*, not general
natural-language entailment. Never label model prose "fact verified" merely
because a source ID exists. Results distinguish clear failures from questions
requiring human / stronger independent verification.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from decimal import Decimal, DivisionByZero, InvalidOperation
import hashlib
import re

CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
MONEY = re.compile(r"(?<![\w])\$\s*([\d,]+(?:\.\d+)?)")
PERCENT = re.compile(r"(?<![\w])([\d,]+(?:\.\d+)?)\s*%")
EXACT_NUM = re.compile(r"(?<![\w])\d[\d,]*(?:\.\d+)?(?![\w])")
SMALL_NON_EVIDENCE = {"0", "1", "2", "3", "4", "5"}
ALLOWED_EXPR = (ast.Add, ast.Sub, ast.Mult, ast.Div)


@dataclass(frozen=True)
class Quantity:
    value: Decimal
    source_id: object
    source_span: str
    unit: str


def _number(value):
    if isinstance(value, float):
        # Refuse float uncertainty in auditable calculations.
        raise TypeError("Use decimal strings, integers or Decimal values")
    if isinstance(value, bool):
        raise TypeError("Bool cannot represent a business quantity")
    return Decimal(str(value).replace(",", ""))


def checked_calculation(expression, inputs, sources, output_unit=""):
    """Execute a constrained expression with a source-backed input ledger.

    inputs: {symbol: Quantity}. The source span must exist verbatim in its
    matching provided evidence chunk and contain the stated numeric value.
    Returns exact Decimal value + evidence lineage, never an unearned ROI claim.
    """
    if not isinstance(inputs, dict) or not 1 <= len(inputs) <= 20:
        raise ValueError("Invalid calculation inputs")
    catalog = {s.get("id"):s for s in sources}
    resolved = {}
    used = set()
    for symbol, qty in inputs.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,30}", symbol):
            raise ValueError("Invalid calculation symbol")
        if not isinstance(qty, Quantity) or qty.source_id not in catalog:
            raise ValueError("Unattributed calculation quantity")
        full = str(catalog[qty.source_id].get("chunk") or "")
        span = str(qty.source_span)
        if not span or span not in full:
            raise ValueError("Quantity span is absent from cited source")
        n = _number(qty.value)
        candidates = [Decimal(v.replace(",", "")) for v in EXACT_NUM.findall(span)]
        if n not in candidates:
            raise ValueError("Quantity value is not recorded in the evidence span")
        resolved[symbol] = n
    node = ast.parse(expression, mode="eval")
    def calc(n, depth=0):
        if depth > 20:
            raise ValueError("Calculation too deeply nested")
        if isinstance(n, ast.Expression):return calc(n.body, depth+1)
        if isinstance(n, ast.Name):
            if n.id not in resolved:
                raise ValueError("Unknown evidence variable")
            used.add(n.id)
            return resolved[n.id]
        if isinstance(n, ast.Constant):
            if isinstance(n.value, int) and 0 < n.value <= 100:
                return Decimal(n.value)
            raise ValueError("Only small positive integer scaling constants are permitted")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ALLOWED_EXPR):
            left, right=calc(n.left,depth+1),calc(n.right,depth+1)
            if isinstance(n.op, ast.Add):return left+right
            if isinstance(n.op, ast.Sub):return left-right
            if isinstance(n.op, ast.Mult):return left*right
            if isinstance(n.op, ast.Div):
                if right==0:raise ValueError("Division by zero")
                return left/right
        raise ValueError("Unsafe or unsupported formula expression")
    result = calc(node)
    if not result.is_finite():
        raise ValueError("Non-finite business calculation")
    return {
        "value": str(result),
        "unit": str(output_unit)[:40],
        "expression": expression,
        "source_ids": [qty.source_id for symbol,qty in inputs.items() if symbol in used],
        "variables": {symbol:str(inputs[symbol].value) for symbol in sorted(used)},
        "verified_kind": "recomputed_from_source_values",
        "causality_proven": False,
        "future_outcome_proven": False,
    }



CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+(?=(?:[*#]|[A-Z]))|\n+")
QUOTED = re.compile(r'["“]([^"”]{6,300})["”]')


def check_claims(answer, sources):
    """Conservative per-claim reference checks, not semantic entailment."""
    catalog={int(src["n"]):src for src in sources if isinstance(src.get("n"),int)}
    result=[]
    for piece in CLAIM_SPLIT.split(str(answer or "")):
        segment=piece.strip(" \t-*#")
        if not segment:
            continue
        ids=[int(n) for cite in CITATION.finditer(segment)
             for n in re.findall(r"\d+",cite.group(1))]
        valid=[n for n in ids if n in catalog]
        invalid=[n for n in ids if n not in catalog]
        evidence="\n".join(str(catalog[n].get("chunk") or "") for n in valid)
        prose=CITATION.sub("",segment)
        quotes=[q.strip() for q in QUOTED.findall(prose)]
        matching=[q for q in quotes if q.casefold() in evidence.casefold()]
        warnings=[]
        nums={_number(x) for x in EXACT_NUM.findall(evidence)}
        for rx,kind in ((MONEY,"usd"),(PERCENT,"percent")):
            for match in rx.finditer(prose):
                if _number(match.group(1)) not in nums:
                    warnings.append(kind)
        if invalid:state="invalid_citation"
        elif not valid:state="no_source_reference"
        elif quotes and len(matching)!=len(quotes):state="unmatched_quotation"
        elif warnings:state="numeric_not_literal_in_cited_source"
        elif matching:state="quoted_span_present_meaning_unverified"
        else:state="cited_semantics_unverified"
        result.append({"text":segment,"claim_index":len(result)+1,
                       "source_numbers":sorted(set(ids)),
                       "status":state,"quote_count":len(quotes),
                       "quotes_matched":len(matching),"numeric_warnings":warnings})
    return result


def check_answer(answer, sources, operation="model"):
    """Count citation validity and unresolved material-number support.

    Citation IDs are *not* semantic fact verification; valid references earn
    candidate_support only. If uncertain we return needs_review, not pass.
    """
    body=str(answer or "")
    source_by_number = {int(s["n"]):s for s in sources if isinstance(s.get("n"),int)}
    valid = []
    invalid = []
    for match in CITATION.finditer(body):
        for n in re.findall(r"\d+", match.group(1)):
            target = int(n)
            (valid if target in source_by_number else invalid).append(target)
    # Parse numeric literals from model text, excluding those inside citation
    # brackets. Some can be calculations not literally present in source text.
    stripped = CITATION.sub("", body)
    numeric_warnings = []
    material = [(m.group(0), m.group(1), "usd") for m in MONEY.finditer(stripped)]
    material += [(m.group(0), m.group(1), "percent") for m in PERCENT.finditer(stripped)]
    corpus = "\n".join(str(s.get("chunk") or "") for s in sources)
    source_nums = {_number(x) for x in EXACT_NUM.findall(corpus)}
    for label, value, unit in material:
        if _number(value) not in source_nums:
            # This may be an independently computed arithmetic result or
            # a model-invented figure. Mark for review; never auto-certify.
            numeric_warnings.append(unit)
    claims = check_claims(answer,sources)
    numeric_warnings = sorted(set(numeric_warnings+
        [w for c in claims for w in c["numeric_warnings"]]))
    has_sources = bool(source_by_number)
    cited = bool(valid)
    hard_fail = bool(invalid)
    needs_review = (bool(numeric_warnings) or
                    (has_sources and not cited) or
                    bool(valid) or
                    (operation=="model" and bool(material)))
    if hard_fail:
        status = "invalid_citation"
    elif operation=="verified_byline" and not numeric_warnings and cited:
        status = "verified_narrow_operation"
    elif needs_review:
        status = "needs_review"
    else:
        status = "uncited_or_nonfactual"
    return {
        "status": status,
        "hard_fail": hard_fail,
        "invalid_citations": sorted(set(invalid)),
        "valid_citation_count": len(valid),
        "candidate_source_count": len({n for n in valid}),
        "material_numeric_count": len(material),
        "numeric_warnings": numeric_warnings,
        "claim_count":len(claims),
        "claims":claims,
        "fully_fact_verified": status == "verified_narrow_operation",
        "semantic_entailment_checked": False,
        "label": "reference-and-numeric-preflight-not-semantic-certification",
    }
