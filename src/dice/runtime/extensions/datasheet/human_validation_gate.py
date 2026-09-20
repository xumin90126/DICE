"""
Phase 16.8: Datasheet Extension — Human Validation Gate (mock).

CAND-002 (datasheet EXTEND) — UPSTREAM promotion layer.

This module implements the MINIMAL Human Validation Gate that promotes a
CandidateSpan → DocumentSpan. It is a MECHANICAL, zero-authority lift: the
span_type and span_id are taken EXCLUSIVELY from an explicit human annotation
fixture (HumanAnnotation). The gate NEVER infers span_type, NEVER assigns
span_type, NEVER associates a capability.

Position in the data flow (Phase 16.7 Design Review §6):
    CandidateSpan (generator output, zero span_type)
      → HumanValidationGate.promote(candidate, annotation)
      → DocumentSpan (frozen schema, Phase 16.1 normalization_adapter)

CRITICAL BOUNDARY (Phase 16.7 T-1 ~ T-8):
    T-2  span_type owned by Human — the gate only reads the human annotation;
         it NEVER classifies. UNKNOWN is a legal human annotation.
    T-4  promotion is Human-only — the gate performs NO automatic promotion;
         a candidate without a matching annotation is NOT promoted.
    T-6  doc_type is factual metadata (from annotation), zero routing.
    T-1  zero capability association — the gate never touches capability.
    T-7  six authorities ZERO.

Imports: stdlib + same-package relative (DocumentSpan, SpanType).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .candidate_span import CandidateSpan
from .normalization_adapter import DocumentSpan, SpanType


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HumanAnnotation:
    """Explicit HUMAN annotation fixture — the only source of span_type.

    This dataclass models the human decision for ONE candidate span. It is
    the promotion decision record: whether to promote, what span_type the
    human assigns, the span_id, and the factual doc_type.

    Fields:
        candidate_key : the candidate's document_id + page_reference + span
                        text identity (fact; used to match a candidate)
        promote       : True → promote to DocumentSpan; False → discard
        span_type     : SpanType value the HUMAN assigns (UNKNOWN is legal)
        span_id       : human-assigned unique span identifier
        doc_type      : factual source document type metadata (zero routing)
    """

    candidate_key: str = ""
    promote: bool = False
    span_type: str = SpanType.UNKNOWN.value   # human-assigned; UNKNOWN legal
    span_id: str = ""
    doc_type: str = "product_datasheet"       # factual metadata; zero routing


@dataclass
class PromotionResult:
    """Promotion output wrapper — the DocumentSpan (or None) + provenance.

    Carries the promoted DocumentSpan (frozen schema) when promote=True,
    else None. It also records a provenance fact: whether the gate found a
    matching annotation, and the human span_type that was applied. Zero
    capability, zero routing, zero decision beyond the human annotation.
    """

    document_span: Optional[DocumentSpan] = None
    promoted: bool = False
    annotation_key: str = ""
    span_type_applied: str = ""
    promoted_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "promoted": self.promoted,
            "annotation_key": self.annotation_key,
            "span_type_applied": self.span_type_applied,
            "promoted_at": self.promoted_at,
            "document_span": (
                self.document_span.to_dict() if self.document_span else None
            ),
        }


def candidate_key(document_id: str, page_reference: int, span_text: str) -> str:
    """Deterministic candidate identity used to match an annotation (fact)."""
    return f"{document_id}::p{page_reference}::{span_text.strip()}"


class HumanValidationGate:
    """Mechanical, zero-authority CandidateSpan → DocumentSpan promotion.

    The gate is a PURE LIFT: it takes a CandidateSpan and a matching
    HumanAnnotation and constructs a DocumentSpan using the FROZEN schema
    (Phase 16.1). It performs NO classification, NO capability association,
    NO routing, NO automatic promotion.

    Usage (Human-driven):
        gate = HumanValidationGate(annotations=[...])   # human fixture list
        result = gate.promote(candidate)                 # one candidate at a time

    The gate does NOT iterate/choose candidates; the caller drives which
    candidate is presented (zero selection authority in the gate).
    """

    def __init__(self, annotations: Optional[list] = None) -> None:
        # Index annotations by candidate_key for O(1) lookup. This is a
        # READ-ONLY index over the human fixture — NOT a selection/ranking.
        self._annotations: Dict[str, HumanAnnotation] = {}
        if annotations:
            for a in annotations:
                self._annotations[a.candidate_key] = a

    def promote(self, candidate: CandidateSpan) -> PromotionResult:
        """Promote one candidate using its human annotation (if any).

        Args:
            candidate: the CandidateSpan to promote (fact).

        Returns:
            PromotionResult. If no matching annotation exists, or the
            annotation's promote flag is False, `promoted=False` and
            `document_span=None` (the candidate is simply NOT promoted —
            the gate never fabricates a promotion).
        """
        key = candidate_key(
            candidate.document_id, candidate.page_reference, candidate.span_text
        )
        annotation = self._annotations.get(key)
        if annotation is None or not annotation.promote:
            return PromotionResult(
                document_span=None,
                promoted=False,
                annotation_key=key,
                span_type_applied="",
            )

        # span_type comes EXCLUSIVELY from the human annotation (T-2).
        span_type = annotation.span_type
        # position_metadata is DROPPED here (T-3 / B-4): DocumentSpan uses the
        # frozen schema which has no position_metadata field.
        document_span = DocumentSpan(
            document_id=candidate.document_id,
            doc_type=annotation.doc_type,   # factual metadata; zero routing
            span_id=annotation.span_id,
            span_text=candidate.span_text,
            span_type=span_type,
            page=candidate.page_reference,
        )
        return PromotionResult(
            document_span=document_span,
            promoted=True,
            annotation_key=key,
            span_type_applied=span_type,
        )


__all__ = [
    "HumanAnnotation",
    "PromotionResult",
    "HumanValidationGate",
    "candidate_key",
]
