"""
P5 Reading Order — observation schema.

ReadingOrderObservation = geometric reading-order interpretation of a P4
ExperimentalSpan. Derived, NOT a copy. Reverse-traceable to span_id.
No semantic classification (no is_header / is_body / heading_level).
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ColumnGroup:
    """A geometric column group (NOT a semantic 'body column')."""
    column_group_id: str
    page_number: int
    member_span_ids: List[str]
    center_x: float              # representative x center of the group
    x_min: float
    x_max: float
    span_count: int
    confidence: str              # HIGH/MEDIUM/LOW/UNKNOWN
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageColumnLayout:
    """Column layout for one page (geometric partition)."""
    page_number: int
    column_groups: List[Dict[str, Any]]   # ordered left→right by center_x
    column_count: int
    page_width: float
    page_height: float
    top_region_span_ids: List[str]        # full-width spans in top region
    bottom_region_span_ids: List[str]     # full-width spans in bottom region
    full_width_span_ids: List[str]        # full-width spans NOT in top/bottom
    column_region_span_ids: List[str]     # spans assigned to column groups
    ambiguous_span_ids: List[str]
    confidence: str
    x_projection: Dict[str, Any]          # density histogram + gaps
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReadingOrderObservation:
    """Reading-order interpretation of ONE P4 span. Pure geometric facts."""
    observation_id: str
    document_id: str
    page_number: int

    span_id: str
    source_span_index: int

    # column assignment (geometric only)
    column_group_id: Optional[str]      # null if top/bottom region or ambiguous
    page_region: str                    # TOP/BOTTOM/COLUMN/FULL_WIDTH/UNKNOWN

    # reading order
    reading_order_index: int            # 0-based within page
    previous_span_id: Optional[str]
    next_span_id: Optional[str]

    # geometry summary (from span, not copied wholesale)
    bbox: List[float]
    center_x: float
    center_y: float
    width: float
    height: float

    # order justification
    order_reason: str                   # geometric ORDER_* reason
    order_facts: Dict[str, Any]         # numeric facts backing the decision
    horizontal_relation: Optional[str]
    vertical_relation: Optional[str]
    column_relation: Optional[str]
    confidence: str                     # HIGH/MEDIUM/LOW/UNKNOWN

    # provenance
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReadingOrderDecisionTrace:
    """One pairwise order decision between span A and B."""
    span_a_id: str
    span_b_id: str
    same_column_group: bool
    a_above_b: bool
    a_center_y: float
    b_center_y: float
    a_center_x: float
    b_center_x: float
    vertical_gap: float
    horizontal_overlap: float
    decision: str                       # "A_BEFORE_B" | "B_BEFORE_A" | "AMBIGUOUS"
    reason: str                         # ORDER_* reason
    facts_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageReadingOrder:
    """Reading order for one page."""
    page_number: int
    ordered_span_ids: List[str]
    observations: List[Dict[str, Any]]
    decision_traces: List[Dict[str, Any]]
    confidence: str
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
