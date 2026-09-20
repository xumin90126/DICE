"""
P5 Reading Order — Centralized configuration.

ALL thresholds live here. No magic numbers in if/else. No document-specific
tuning. Geometry-driven column detection + reading order.
"""
from __future__ import annotations
from dataclasses import dataclass
import dataclasses


# ── Order reasons (geometric, NOT semantic) ──
ORDER_SAME_COLUMN_VERTICAL = "SAME_COLUMN_VERTICAL_ORDER"       # same column, A above B
ORDER_COLUMN_GROUP_SEQUENCE = "COLUMN_GROUP_SEQUENCE"           # col group 0 before col group 1
ORDER_TOP_REGION_BEFORE_COLUMNS = "TOP_REGION_BEFORE_COLUMN_REGION"
ORDER_BOTTOM_REGION_AFTER_COLUMNS = "BOTTOM_REGION_AFTER_COLUMN_REGION"
ORDER_SINGLE_COLUMN_TOP_DOWN = "SINGLE_COLUMN_TOP_DOWN"
ORDER_PAGE_BOUNDARY = "PAGE_BOUNDARY"
ORDER_AMBIGUOUS = "AMBIGUOUS"
ORDER_SINGLE_SPAN = "SINGLE_SPAN"

# Column confidence
COLUMN_CONFIDENCE_HIGH = "HIGH"
COLUMN_CONFIDENCE_MEDIUM = "MEDIUM"
COLUMN_CONFIDENCE_LOW = "LOW"
COLUMN_CONFIDENCE_UNKNOWN = "UNKNOWN"

# Page regions (geometric only, NOT semantic header/footer)
PAGE_REGION_TOP = "TOP_PAGE_REGION"
PAGE_REGION_BOTTOM = "BOTTOM_PAGE_REGION"
PAGE_REGION_COLUMN = "COLUMN_REGION"
PAGE_REGION_FULL_WIDTH = "FULL_WIDTH_REGION"
PAGE_REGION_UNKNOWN = "UNKNOWN_PAGE_REGION"


@dataclass(frozen=True)
class ReadingOrderConfig:
    """Centralized, immutable, configurable thresholds."""

    # ── Column detection (x-projection) ──
    column_gap_threshold: float = 25.0
    """Min horizontal gap (pt) in span centers to separate two column groups.
    A vertical white stripe wider than this between two x-density clusters
    indicates a column boundary."""

    column_density_threshold: int = 2
    """Min number of spans whose center_x falls in an x-bin to count it as
    a populated column region (density). Below this the bin is 'empty'."""

    column_x_bin_size: float = 5.0
    """x-projection bin width (pt) for density histogram."""

    # ── Vertical region detection (top/bottom full-width regions) ──
    top_region_ratio: float = 0.20
    """Spans whose center_y is in the top `top_region_ratio` of the page AND
    span width > full_width_ratio*page_width are TOP_PAGE_REGION candidates."""

    bottom_region_ratio: float = 0.20
    """Analogous for bottom."""

    full_width_ratio: float = 0.60
    """A span is 'full-width' if its width >= full_width_ratio * page_width."""

    # ── Same-column membership ──
    column_x_tolerance: float = 12.0
    """Two spans are in the same column group if their center_x differ by
    <= this (pt). Used to assign spans to detected column centers."""

    min_column_span_count: int = 3
    """A detected column group with fewer spans than this is treated as a
    margin element (e.g. page number) and merged into the nearest group,
    not a real column."""

    # ── Vertical ordering ──
    vertical_order_tolerance: float = 1.0
    """y-tolerance for declaring A strictly above B (center_y diff > this)."""

    # ── Gaps ──
    large_vertical_gap: float = 30.0
    """Vertical gap beyond which we note a large gap (does not break column
    membership but recorded in order_facts)."""

    # ── Overlap ──
    overlap_tolerance: float = 0.5

    # ── Confidence ──
    confidence_threshold_high: float = 0.75
    confidence_threshold_medium: float = 0.50
    """High if >=0.75, Medium if >=0.50, Low if <0.50, Unknown if uncomputable."""

    # ── Ambiguity ──
    ambiguous_column_overlap_ratio: float = 0.40
    """If a span's x-extent overlaps two column groups by more than this ratio
    on both sides, mark its column assignment AMBIGUOUS."""

    row_alignment_threshold: float = 0.60
    """If >= this fraction of spans in one column have a y-overlapping span in
    an adjacent column, the layout is row-aligned (e.g. table of contents,
    key-value pairs). Recorded as a fact (row_alignment_ratio); column-major
    reading remains the deterministic default per task §9/§11."""

    overlap_ambiguity_threshold: float = 0.60
    """If two consecutive spans in reading order have bbox overlap ratio
    (intersection / min-area) >= this, their relative order is AMBIGUOUS."""

    construction_version: str = "v1"

    def with_overrides(self, **kwargs) -> "ReadingOrderConfig":
        return dataclasses.replace(self, **kwargs)


DEFAULT_CONFIG = ReadingOrderConfig()


def to_dict(cfg: ReadingOrderConfig) -> dict:
    return dataclasses.asdict(cfg)
