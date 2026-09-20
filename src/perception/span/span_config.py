"""
P4 Span — Centralized span construction configuration.

ALL span construction thresholds live here. No function may hardcode a
threshold in an if/else. No case-specific patches (no if-document-id, no
if-text-content). Thresholds describe geometric/numeric merge criteria only.
"""
from __future__ import annotations

from dataclasses import dataclass
import dataclasses


# Merge decision reasons (geometric, NOT semantic)
REASON_MERGE = "MERGE"
REASON_KEEP_SEPARATE = "KEEP_SEPARATE"

# Why merge (from facts):
MERGE_REASON_SAME_LINE_CONTIGUOUS = "SAME_LINE_CONTIGUOUS"
MERGE_REASON_NEXT_LINE_CONTIGUOUS = "NEXT_LINE_CONTIGUOUS"
MERGE_REASON_SINGLE_OBSERVATION = "SINGLE_OBSERVATION"

# Why keep separate (from facts):
SEPARATE_REASON_LARGE_HORIZONTAL_GAP = "LARGE_HORIZONTAL_GAP"
SEPARATE_REASON_CROSS_COLUMN_GAP = "CROSS_COLUMN_GAP"
SEPARATE_REASON_LARGE_VERTICAL_GAP = "LARGE_VERTICAL_GAP"
SEPARATE_REASON_PAGE_BOUNDARY = "PAGE_BOUNDARY"
SEPARATE_REASON_STYLE_BREAK = "STYLE_BREAK"
SEPARATE_REASON_NOT_ADJACENT = "NOT_ADJACENT"
SEPARATE_REASON_NO_OVERLAP = "NO_OVERLAP"


@dataclass(frozen=True)
class SpanConfig:
    """Centralized span construction thresholds. Immutable, configurable."""

    # ── Horizontal gap (same-line merge) ──
    max_horizontal_gap: float = 8.0
    """Max x-gap (pt) to merge two same-y-band observations into one span.
    Beyond this, they are kept separate (LARGE_HORIZONTAL_GAP)."""

    # ── Vertical gap (next-line merge) ──
    max_vertical_gap: float = 14.0
    """Max y-gap (pt) to consider two observations as vertically contiguous
    (potential next-line). Beyond this → LARGE_VERTICAL_GAP."""

    # ── Same-line tolerance (y-band for "same line") ──
    same_line_tolerance: float = 3.0
    """Two observations are on the same line if y-center diff <= this (pt).
    Delegates to P2 y_band_tolerance concept but independent config."""

    # ── Style transition ──
    style_transition_tolerance: float = 0.0
    """How many style facts may differ before recording a STYLE_BREAK.
    0 = any style signature difference is a break (conservative).
    A non-zero value allows e.g. same font but different size to still merge
    if other contiguity facts hold, but records the transition."""

    # ── Cross-column detection (geometric, NOT column_id) ──
    cross_column_gap_threshold: float = 30.0
    """If two same-y-band observations have horizontal_distance > this,
    they are kept separate as CROSS_COLUMN_GAP. This is a geometric gap
    fact, not a column semantic classification."""

    # ── Overlap tolerance ──
    overlap_tolerance: float = 0.5
    """Overlap below this treated as 0."""

    # ── Page boundary ──
    page_boundary_policy: str = "BLOCK_CROSS_PAGE"
    """Span construction does not cross page boundaries for ordinary spans.
    A span belongs to exactly one page."""

    # ── Construction version ──
    construction_version: str = "v2"

    def with_overrides(self, **kwargs) -> "SpanConfig":
        return dataclasses.replace(self, **kwargs)


DEFAULT_CONFIG = SpanConfig()


def to_dict(cfg: SpanConfig) -> dict:
    return dataclasses.asdict(cfg)
