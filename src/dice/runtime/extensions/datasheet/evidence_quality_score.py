"""
Phase 16.8: Datasheet Extension — Evidence Quality Score (EQS).

CAND-002 (datasheet EXTEND) — Evidence Validation Layer.

This module introduces the Evidence Quality Score (EQS) as a VALIDATION
METADATA record ONLY. EQS measures, as OBSERVATION FACTS, four fixed
dimensions of evidence quality:

    EQS = source_completeness
        + span_completeness
        + extraction_completeness
        + boundary_compliance

EQS lives EXCLUSIVELY inside MappingEvidence.validation_metadata. It is a
PURE FACT RECORD (integers 0..4), carrying ZERO authority:

    - NO ranking        — EQS never orders/sorts candidates or evidence
    - NO choosing       — EQS never selects a candidate or span
    - NO selecting      — EQS never selects a capability
    - NO routing        — EQS never routes a document_type
    - NO decision       — EQS never decides promotion or execution

The function is a PURE FUNCTION of already-produced observation artifacts
(DocumentSpan + ExtractedFact). It reads facts and records facts; it mutates
nothing and influences nothing downstream.

Dimension definitions (deterministic, falsifiable):
    source_completeness    : document_id non-empty AND span_id non-empty
                             (source traceability present)
    span_completeness      : span_text non-empty after strip
                             (text/span integrity present)
    extraction_completeness: fact.attribute_name non-empty
                             (a deterministic fact was extracted)
    boundary_compliance    : 1 when the fact is HONEST relative to the span:
                               - UNKNOWN / empty span_type → fact MUST be
                                 empty (no fabrication across the boundary)
                               - declared span_type → fact may be empty or
                                 non-empty (both honest; empty = "no
                                 extractable content", non-empty = success)

Imports: stdlib + same-package relative (DocumentSpan, ExtractedFact, SpanType).
"""

from __future__ import annotations

from typing import Any, Dict

from .extraction_adapter import ExtractedFact
from .normalization_adapter import DocumentSpan, SpanType


def _boundary_compliance(document_span: DocumentSpan, fact: ExtractedFact) -> int:
    """Deterministic boundary honesty check (fact, NOT a decision).

    Returns 1 if the extracted fact is HONEST relative to the span's declared
    semantic category; 0 if it fabricates content across a boundary.

    Rules:
        - span_type UNKNOWN / empty → the deterministic extraction MUST have
          produced an empty fact (attribute_name == ""). A non-empty fact here
          would mean fabrication across the boundary → 0.
        - span_type declared (spec/recommended/component/table) → both empty
          and non-empty facts are honest → 1.
    """
    span_type = document_span.span_type
    is_unknown = span_type in ("", SpanType.UNKNOWN.value)
    if is_unknown:
        return 1 if fact.attribute_name == "" else 0
    return 1


def compute_evidence_quality(document_span: DocumentSpan,
                             fact: ExtractedFact) -> Dict[str, Any]:
    """Compute the four EQS dimensions as pure observation facts.

    PURE FUNCTION: reads facts from the already-produced DocumentSpan and
    ExtractedFact, returns a plain dict of integer facts (0..4 total). It
    does NOT rank, choose, select, route, or decide. It mutates nothing.

    Args:
        document_span: the promoted DocumentSpan (frozen schema fact).
        fact: the extracted fact (pipeline component 3 output, fact).

    Returns:
        A dict with the four fixed dimension names plus `eqs_total` (0..4).
        This dict is intended to be stored verbatim inside
        MappingEvidence.validation_metadata["evidence_quality_score"].
    """
    source_completeness = 1 if (document_span.document_id and document_span.span_id) else 0
    span_completeness = 1 if bool(document_span.span_text.strip()) else 0
    extraction_completeness = 1 if bool(fact.attribute_name) else 0
    boundary_compliance = _boundary_compliance(document_span, fact)

    eqs_total = (
        source_completeness
        + span_completeness
        + extraction_completeness
        + boundary_compliance
    )

    return {
        "source_completeness": source_completeness,
        "span_completeness": span_completeness,
        "extraction_completeness": extraction_completeness,
        "boundary_compliance": boundary_compliance,
        "eqs_total": eqs_total,
        "eqs_note": "observation-only quality record; zero ranking/selection/routing/decision",
    }


__all__ = [
    "compute_evidence_quality",
]
