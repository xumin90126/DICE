"""
Phase 30: CAP-TABLE-CELL-SEGMENT — L1 Structural Table Capability (models).

This module defines the SIX-FIELD output data model of the first L1
STRUCTURAL table capability. It is the implementation artifact of Phase 30
(IMPLEMENTATION AUTHORIZED, following Phase 28 Contract Freeze + Phase 29
Registration Review).

Position in the data flow (Phase 27 F-2 = Independent Evidence acquisition):
    CandidateSpan (block-level observation, from CandidateSpanGenerator)
      → [Human confirms table_region_reference]
      → TableCellSegmenter.segment  → list[TableCellObservation]
      → (downstream Human-driven consumption; NOT auto-wired)

CRITICAL BOUNDARY (Phase 28 Contract Freeze):
    - Output carries EXACTLY six structural fields:
        table_region_reference / cell_id / row_index / column_index /
        raw_text / bbox
    - FORBIDDEN fields (never present by construction):
        value / normalized_value / unit / product / property / relation /
        confidence / semantic_label / fact / attribute_name
    - ZERO semantic association: no header interpretation, no column-meaning
      inference, no row matching, no cell joining, no fact generation.

Invariants enforced by construction on the OUTPUT artifact (I-1 ~ I-5):
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TableCellObservation:
    """L1 structural cell observation — SIX-FIELD contract (Phase 28).

    Produced by TableCellSegmenter.segment(). Each observation records ONE
    cell recovered from a merged table block, using ONLY structural facts.
    It is a FACTUAL structural observation, NOT a fact (value), NOT a
    selection, NOT a decision, NOT an execution plan.

    SIX-FIELD CONTRACT (Phase 28 §Output):
        table_region_reference : Human-confirmed table region identity (fact)
        cell_id                : deterministic cell identity (fact)
        row_index              : 0-based row index (fact)
        column_index           : 0-based column index (fact)
        raw_text               : raw cell text (fact; NOT a value/unit)
        bbox                   : geometric extent [x0, y0, x1, y1] (fact)

    FORBIDDEN fields (never present by construction):
        value / normalized_value / unit / product / property / relation /
        confidence / semantic_label / fact / attribute_name

    The `raw_text` field is the RAW substring of the merged block for this
    cell. It is NOT interpreted: the segmenter never extracts a value or
    unit from it, never classifies it, never associates it with any
    component name. What the text MEANS is owned by Human (L2 semantic).
    """

    # ── Six structural fields ──
    table_region_reference: str = ""
    cell_id: str = ""
    row_index: int = 0
    column_index: int = 0
    raw_text: str = ""
    bbox: List[float] = field(default_factory=list)

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    segmented_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_region_reference": self.table_region_reference,
            "cell_id": self.cell_id,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "raw_text": self.raw_text,
            "bbox": list(self.bbox),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "segmented_at": self.segmented_at,
        }


@dataclass
class SegmentationResult:
    """Segmenter output wrapper — cell list + structural provenance facts.

    Carries ONLY the recovered cell observations plus a design-time-fixed
    provenance record (region reference / row count / source block info).
    Zero semantic fields, zero classification, zero authority.
    """

    cells: List[TableCellObservation] = field(default_factory=list)
    table_region_reference: str = ""
    row_count: int = 0
    column_index: int = 0
    segmented_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_region_reference": self.table_region_reference,
            "row_count": self.row_count,
            "column_index": self.column_index,
            "segmented_at": self.segmented_at,
            "cell_count": len(self.cells),
            "cells": [c.to_dict() for c in self.cells],
        }


__all__ = [
    "TableCellObservation",
    "SegmentationResult",
]
