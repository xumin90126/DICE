"""
P7.1 StructureHypothesis — Layer C schema.

A StructureHypothesis is a CANDIDATE ("this MIGHT be a heading / paragraph /
section / list / header / footer / multi-column continuation"), NOT a final
structure fact. It carries full reverse traceability:

    Hypothesis -> Relation -> Span/Region -> Observation (P1-P6)

and never asserts is_* = true. Status stays PROPOSED until Human Validation.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .structure_config import (
    STATUS_PROPOSED, CONFIDENCE_UNKNOWN, ALL_HYPOTHESIS_TYPES,
)


def _hypothesis_id(document_id: str, page_number: int, hypothesis_type: str,
                   source_ids: List[str]) -> str:
    sorted_ids = ",".join(sorted(source_ids))
    raw = f"{document_id}|p{page_number}|{hypothesis_type}|{sorted_ids}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class StructureHypothesis:
    """One structure candidate. Read-only consumer of P1-P6 facts."""

    hypothesis_id: str
    document_id: str
    page_number: int
    hypothesis_type: str                # one of ALL_HYPOTHESIS_TYPES

    # ── Source references (reverse traceability) ──
    span_ids: List[str] = field(default_factory=list)
    region_ids: List[str] = field(default_factory=list)
    supporting_relation_ids: List[str] = field(default_factory=list)
    supporting_fact_refs: List[Dict[str, Any]] = field(default_factory=list)
    # each fact ref: {"ref_type": "span"|"region"|"reading_order",
    #                 "ref_id": ..., "fact": "<field name>"}

    # ── Geometry summary (union of member spans; derived, not semantic) ──
    geometry: Dict[str, Any] = field(default_factory=dict)

    confidence: str = CONFIDENCE_UNKNOWN
    status: str = STATUS_PROPOSED          # P7.1 never leaves PROPOSED

    construction_method: str = ""
    construction_version: str = "v1"

    decision_trace: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    coord_origin: str = "PDF_TOP_LEFT"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageStructureBundle:
    """All structure hypotheses + relations for one page."""

    document_id: str
    page_number: int
    page_width: float
    page_height: float
    coord_origin: str
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
