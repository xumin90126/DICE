"""
P7.1 Structural Relation — independent Layer B modeling.

A Structural Relation answers "what structural relationship exists between
two objects?" and is a deterministic geometric/topological fact, NOT a
semantic claim. It is referenced by StructureHypothesis as supporting
evidence, never merged into the hypothesis body.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .structure_config import (
    ALL_RELATION_TYPES, CONFIDENCE_ORDER, CONFIDENCE_UNKNOWN,
)


def _relation_id(document_id: str, page_number: int, relation_type: str,
                 source_id: str, target_id: str) -> str:
    raw = f"{document_id}|p{page_number}|{relation_type}|{source_id}|{target_id}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class StructuralRelation:
    """One structural relation between two objects (span / region / hypothesis).

    Deterministic: relation_id is a stable hash over (doc, page, type, src, tgt).
    """

    relation_id: str
    document_id: str
    page_number: int
    relation_type: str                      # one of ALL_RELATION_TYPES
    source_id: str                          # span_id / region_id / hypothesis_id
    target_id: str                          # span_id / region_id / hypothesis_id
    source_kind: str                        # "span" | "region" | "hypothesis"
    target_kind: str                        # "span" | "region" | "hypothesis"
    supporting_fact_refs: List[Dict[str, Any]] = field(default_factory=list)
    confidence: str = CONFIDENCE_UNKNOWN
    decision_trace: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    coord_origin: str = "PDF_TOP_LEFT"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def min_confidence(*confs: str) -> str:
    """Return the most conservative (lowest) confidence among the given values."""
    best = None
    best_rank = 10 ** 9
    for c in confs:
        if c is None:
            continue
        rank = CONFIDENCE_ORDER.get(c, CONFIDENCE_ORDER[CONFIDENCE_UNKNOWN])
        if rank < best_rank:
            best_rank = rank
            best = c
    return best if best is not None else CONFIDENCE_UNKNOWN
