"""
P4 Span — ExperimentalSpan v2 schema.

A span is a DERIVED ORGANIZATION of Atomic Observations (P1).
It is NOT a copy of P1/P2/P3 fields — it carries summaries + full provenance
for reverse traceability. Every span can be split back to its source
observations via source_observation_ids.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentalSpan:
    """Experimental Span v2 — organization of atomic observations.

    Observation = source of truth. Span = derived organization.
    Every span can answer: "which Atomic Observations compose me?"
    """

    span_id: str
    document_id: str
    page_number: int

    # ── Text (deterministically reconstructed from source observations) ──
    text: str

    # ── Source observation provenance (reverse traceability) ──
    source_observation_ids: List[str]
    source_observation_types: List[str]
    observation_count: int
    first_observation_id: str
    last_observation_id: str

    # ── Geometry summary (derived, not copied) ──
    bbox: List[float]          # union bbox of all source observations
    width: float
    height: float
    center_x: float
    center_y: float

    # ── Style summary (derived) ──
    dominant_style_signature: Optional[str]   # most frequent signature
    style_count: int                          # distinct signatures
    style_signatures: List[str]               # all distinct, in source order

    # ── Construction info ──
    construction_method: str                  # e.g. "contiguous_merge" | "single_observation"
    construction_version: str
    construction_reason: str                  # geometric reason (MERGE_REASON_* / SEPARATE_REASON_*)
    merge_decision_trace: List[Dict[str, Any]] = field(default_factory=list)
    # each trace entry: {pair, facts, decision, reason}

    # ── Provenance ──
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MergeDecision:
    """One pairwise merge decision between observation A and B."""
    observation_a_id: str
    observation_b_id: str
    # facts used
    same_y_band: bool
    same_x_band: bool
    horizontal_distance: float
    vertical_distance: float
    horizontal_overlap: float
    vertical_overlap: float
    same_page: bool
    same_style_signature: bool
    style_difference: Optional[str]
    source_order_adjacent: bool
    # decision
    decision: str       # MERGE | KEEP_SEPARATE
    reason: str         # geometric reason
    # trace
    facts_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
