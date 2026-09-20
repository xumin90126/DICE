"""
P7.1 StructureHypothesis — configuration.

All thresholds and vocabulary are centralized here. NO magic numbers in the
engine. P7.1 is a read-only consumer of P1-P6 facts: it emits Structure
Hypotheses (Layer C) and Structural Relations (Layer B), never final semantic
classification (Layer D), never Evidence.

P7.1 implements ONLY the 7 approved candidate types. Semantic objects
(TABLE/IMAGE/FORMULA/FLOWCHART/...) are BLOCKED and documented here.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


# ── Hypothesis types (P7.1 approved, exactly 7) ──────────────────────────────
HYP_HEADING = "HEADING_CANDIDATE"
HYP_PARAGRAPH = "PARAGRAPH_GROUP_CANDIDATE"
HYP_SECTION = "SECTION_CANDIDATE"
HYP_LIST = "LIST_CANDIDATE"
HYP_HEADER = "HEADER_CANDIDATE"
HYP_FOOTER = "FOOTER_CANDIDATE"
HYP_MULTICOL = "MULTI_COLUMN_CONTINUATION_CANDIDATE"

ALL_HYPOTHESIS_TYPES: List[str] = [
    HYP_HEADING, HYP_PARAGRAPH, HYP_SECTION, HYP_LIST,
    HYP_HEADER, HYP_FOOTER, HYP_MULTICOL,
]

# ── Blocked / deferred objects (NOT implemented in P7.1) ─────────────────────
BLOCKED_TYPES: Dict[str, str] = {
    "TABLE": "waits for Table Cell Geometry observation.",
    "TABLE_CELL": "waits for Table Cell Geometry observation.",
    "FIGURE": "waits for Visual Object Observation (P1 skips non-text blocks).",
    "IMAGE": "waits for Visual Object Observation.",
    "CHART": "waits for Visual Object Observation.",
    "FLOWCHART": "waits for Graphic/Vector Observation (shapes/arrows/connectivity).",
    "RELIABLE_FORMULA": "waits for baseline/subscript/symbol-class observation.",
    "RELIABLE_CAPTION": "waits for a reliable object reference (Visual/Table).",
    "PAGE_NUMBER": "human-first; textual pattern not introduced.",
    "REFERENCE": "human-first; textual content not introduced.",
    "FOOTNOTE": "human-first; weak signal only.",
}

# ── Confidence vocabulary ────────────────────────────────────────────────────
CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"
CONFIDENCE_UNKNOWN = "UNKNOWN"
CONFIDENCE_AMBIGUOUS = "AMBIGUOUS"

CONFIDENCE_ORDER: Dict[str, int] = {
    CONFIDENCE_HIGH: 4,
    CONFIDENCE_MEDIUM: 3,
    CONFIDENCE_LOW: 2,
    CONFIDENCE_UNKNOWN: 1,
    CONFIDENCE_AMBIGUOUS: 0,
}

ALL_CONFIDENCES: List[str] = [
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW,
    CONFIDENCE_UNKNOWN, CONFIDENCE_AMBIGUOUS,
]


# ── Validation status (P7.1 only ever emits PROPOSED) ────────────────────────
STATUS_PROPOSED = "PROPOSED"
STATUS_PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
STATUS_VALIDATED = "VALIDATED"
STATUS_REJECTED = "REJECTED"

ALL_STATUSES: List[str] = [
    STATUS_PROPOSED, STATUS_PARTIALLY_VALIDATED, STATUS_VALIDATED, STATUS_REJECTED,
]


# ── Structural Relation types (exactly those used by P7.1) ──────────────────
REL_STYLE_CONTRAST = "STYLE_CONTRAST"          # span style vs page baseline
REL_VERTICAL_SEPARATION = "VERTICAL_SEPARATION"  # vertical gap (spatial proximity)
REL_ADJACENT_TO = "ADJACENT_TO"                # reading-order-adjacent members
REL_LEFT_ALIGNED_WITH = "LEFT_ALIGNED_WITH"    # aligned left edge
REL_PRECEDES = "PRECEDES"                      # heading precedes section members
REL_SHARES_REGION = "SHARES_REGION"            # span belongs to region
REL_CONTINUES_FROM = "CONTINUES_FROM"          # cross-column continuation
REL_REPEATS_ACROSS_PAGES = "REPEATS_ACROSS_PAGES"  # header/footer repetition

ALL_RELATION_TYPES: List[str] = [
    REL_STYLE_CONTRAST, REL_VERTICAL_SEPARATION, REL_ADJACENT_TO,
    REL_LEFT_ALIGNED_WITH, REL_PRECEDES, REL_SHARES_REGION,
    REL_CONTINUES_FROM, REL_REPEATS_ACROSS_PAGES,
]


# ── Construction methods ─────────────────────────────────────────────────────
METHOD_HEADING_MULTI_SIGNAL = "heading_multi_signal"
METHOD_PARAGRAPH_VERTICAL_GROUPING = "paragraph_vertical_grouping"
METHOD_SECTION_HEADING_SPAN = "section_heading_span"
METHOD_LIST_ALIGNMENT = "list_alignment"
METHOD_HEADER_REPEAT = "header_cross_page_repeat"
METHOD_FOOTER_REPEAT = "footer_cross_page_repeat"
METHOD_MULTICOL_CONTINUATION = "multicol_continuation"


@dataclass
class StructureConfig:
    """All P7.1 thresholds. Deterministic; no per-document tuning."""
    construction_version: str = "v1"
    coord_origin: str = "PDF_TOP_LEFT"

    # ── Heading candidate ──
    heading_min_signals: int = 2           # >= 2 independent signals required
    heading_size_ratio: float = 1.15       # size >= page_median * ratio
    heading_gap_threshold: float = 14.0    # vertical gap before span (pt)
    heading_position_max: int = 2          # reading index within column <= this
    heading_short_line_ratio: float = 0.80 # width <= column_ref_width * ratio

    # ── Paragraph group candidate ──
    paragraph_gap_threshold: float = 24.0  # vertical gap breaking a paragraph run
    paragraph_min_spans: int = 1           # a run needs >= this many spans

    # ── Section candidate ──
    section_min_heading_signals: int = 2   # heading must be a real candidate

    # ── List candidate ──
    list_min_items: int = 2
    list_left_align_tolerance: float = 6.0  # x0 spread (pt)
    list_vertical_gap_max: float = 30.0     # gap between consecutive items
    list_short_line_ratio: float = 0.85     # item width <= column_ref_width * ratio

    # ── Header / Footer candidate (cross-page) ──
    header_min_repeat_pages: int = 2        # same unit on >= this many pages
    header_position_tolerance: float = 0.04 # normalized center_x/y bucket width
    footer_position_tolerance: float = 0.04

    # ── Multi-column continuation ──
    multicont_min_cols: int = 2
    multicont_style_required: bool = True   # boundary spans must share style

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_CONFIG = StructureConfig()
