"""
Phase 16.1: Datasheet Extension — Normalization Adapter (Skeleton).

CAND-002 (datasheet EXTEND) Implementation Adapter layer, component 1 of 4.
This module is a STRUCTURE-ONLY skeleton: it defines the interface contract
input type (`DocumentSpan`) and the normalized intermediate type
(`NormalizedDocumentSpan`), plus the adapter class with its method signature.
NO business extraction logic is implemented here — the normalize() body
raises NotImplementedError by design (to be filled in a later phase).

Architecture position (Phase 14.5 Review 1 = B. Implementation Adapter layer):
    This adapter is an OBSERVATIONAL, DECLARATIVE, ZERO-AUTHORITY mapper.
    It turns an externally-supplied `DocumentSpan` (the pipeline input) into a
    normalized observation. It NEVER routes, selects, ranks, scores, decides,
    or executes.

Interface contract (Phase 15 Review 4):
    Input  : DocumentSpan  (factual span description, NOT a decision object)
    Output : NormalizedDocumentSpan  (normalized observation artifact)

Responsibilities:
    IN  : document normalization (read-only, structural/text only, zero semantics)
    OUT : capability selection / document_type routing / ranking / decision

Field whitelist (ALLOWED only):
    document_id / doc_type / span_id / span_text / span_type / page
    normalized_text (normalized text)
FORBIDDEN:
    decision / recommendation / ranking / score / confidence / priority /
    selection / routing / fallback / activation / execution_plan /
    capability_id selection logic

CRITICAL: `doc_type` is FACTUAL METADATA ONLY — it is NEVER used as a
routing signal (Phase 14.5 §2.4: content-driven span→capability, NOT
type-driven type→route). No `if doc_type == "datasheet"` routing may exist.

Invariants enforced by construction on the OUTPUT artifact:
    parent always None              (I-1: no self/cross/recursive invocation)
    shadow_marked always True       (I-2)
    is_hypothetical always True     (I-3)
    origin always "composition_shadow_storage" (I-4)
    production_execution always False (I-5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SpanType(Enum):
    """Declarative span semantic category (Positive Boundary, Phase 14.5 §5.3).

    These describe WHAT KIND of specification content a span carries, purely
    as a fact. They are NOT routing signals and carry no priority or score.

    SPECIFICATION_STATEMENT  — a spec declaration (pore size / dimension /
                               concentration / binding capacity)
    RECOMMENDED_CONDITION    — a recommended condition (temperature / time /
                               formulation / applicable instrument)
    COMPONENT_INFORMATION    — component info (name / quantity / spec)
    SPECIFICATION_TABLE      — a simple spec table (field→value pairs)
    UNKNOWN                  — not classified (a factual "unclassified" state,
                               never a routing decision)
    """

    SPECIFICATION_STATEMENT = "specification_statement"
    RECOMMENDED_CONDITION = "recommended_condition"
    COMPONENT_INFORMATION = "component_information"
    SPECIFICATION_TABLE = "specification_table"
    UNKNOWN = "unknown"


@dataclass
class DocumentSpan:
    """Interface contract INPUT — a factual span-level document description.

    This is the external input to the datasheet extension pipeline. It is a
    NEUTRAL, factual description of one document span. It contains NO
    decision, selection, routing, ranking, score, or priority fields.

    CRITICAL (Phase 14.5 §2.4): `doc_type` is FACTUAL METADATA ONLY. It
    records what kind of document the span came from, but it is NEVER used
    as a routing signal anywhere in this extension. The mapping is
    content-driven (span semantics → capability), not type-driven
    (type → route).

    Fields:
        document_id : source document identifier (fact)
        doc_type    : source document type (factual metadata, NOT routing)
        span_id     : unique span identifier (fact)
        span_text   : raw span text (fact)
        span_type   : SpanType value — declarative semantic category (fact)
        page        : source page number (fact)
    """

    document_id: str = ""
    doc_type: str = ""                 # factual metadata; NEVER a routing signal
    span_id: str = ""
    span_text: str = ""
    span_type: str = ""                # SpanType value (declarative, no priority)
    page: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "doc_type": self.doc_type,
            "span_id": self.span_id,
            "span_text": self.span_text,
            "span_type": self.span_type,
            "page": self.page,
        }


@dataclass
class NormalizedDocumentSpan:
    """Normalization OUTPUT — a read-only normalized observation artifact.

    Produced by NormalizationAdapter.normalize(). It carries the factual span
    fields plus a normalized text representation. It is an OBSERVATION ONLY:
    no decision, selection, routing, ranking, score, or priority.

    Invariants (I-1 ~ I-5) enforced by construction: parent is always None,
    shadow_marked is always True, is_hypothetical is always True, origin is
    always the shadow storage marker, production_execution is always False.

    Fields:
        document_id / doc_type / span_id / span_text / span_type / page :
            preserved factual fields from the source DocumentSpan
        normalized_text : normalized (whitespace/unit-normalized) text — the
            structural/text normalization result (fact, not an extracted value)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
        normalized_at : ISO-8601 timestamp of normalization (fact)
    """

    # ── Preserved factual fields (from DocumentSpan) ──
    document_id: str = ""
    doc_type: str = ""                 # factual metadata; NEVER a routing signal
    span_id: str = ""
    span_text: str = ""
    span_type: str = ""                # SpanType value (declarative, no priority)
    page: int = 0

    # ── Normalization output ──
    normalized_text: str = ""          # structural/text normalization result (fact)

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None       # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    normalized_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "doc_type": self.doc_type,
            "span_id": self.span_id,
            "span_text": self.span_text,
            "span_type": self.span_type,
            "page": self.page,
            "normalized_text": self.normalized_text,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "normalized_at": self.normalized_at,
        }


class NormalizationAdapter:
    """Component 1 of 4 — Document normalization (read-only, structural only).

    Turns an externally-supplied `DocumentSpan` (interface input) into a
    `NormalizedDocumentSpan` (normalized observation). This is a PURE
    OBSERVATION step: it does structural/text normalization only, with ZERO
    semantic interpretation, ZERO routing, ZERO selection, ZERO decision.

    Usage (Human-driven):
        adapter = NormalizationAdapter()
        normalized = adapter.normalize(document_span)

    SKELETON NOTE (Phase 16.1): normalize() raises NotImplementedError.
    The structural/text normalization algorithm is business logic to be
    implemented in a later phase. This class currently provides only the
    signature and the data-model contract.
    """

    def normalize(self, document: DocumentSpan) -> NormalizedDocumentSpan:
        """Normalize a DocumentSpan into a NormalizedDocumentSpan.

        Phase 16.2 — structural/text normalization only: whitespace collapse,
        span-type echo, field preservation. ZERO semantic interpretation,
        ZERO routing, ZERO selection, ZERO extraction of business values.

        Args:
            document: the interface-contract input DocumentSpan (fact).

        Returns:
            NormalizedDocumentSpan (observation artifact, invariants I-1~I-5).
        """
        # Structural/text normalization ONLY: whitespace collapse + field echo.
        # No semantic extraction, no routing, no selection. The invariants
        # (I-1 ~ I-5) are satisfied by construction on the dataclass defaults.
        normalized_text = " ".join(document.span_text.split())
        return NormalizedDocumentSpan(
            document_id=document.document_id,
            doc_type=document.doc_type,          # factual metadata; no routing
            span_id=document.span_id,
            span_text=document.span_text,
            span_type=document.span_type,        # declarative; echoed as fact
            page=document.page,
            normalized_text=normalized_text,
        )


__all__ = [
    "SpanType",
    "DocumentSpan",
    "NormalizedDocumentSpan",
    "NormalizationAdapter",
]
