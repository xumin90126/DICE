"""
P2 Geometry — Centralized threshold configuration.

ALL geometry thresholds live here. No function may hardcode a threshold
in an if/else. Every threshold is documented, configurable, and traceable.

These thresholds describe GEOMETRIC facts only (when do two bboxes count as
"same y band"?). They do NOT encode semantic judgments (no "paragraph gap",
no "table row", no "heading size").
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeometryConfig:
    """Centralized geometry thresholds. Immutable; pass a modified copy to override."""

    # ── Band tolerances (when are two observations in the same y/x band?) ──
    y_band_tolerance: float = 3.0
    """Two observations are in the same_y_band if their y-centers differ by <= this (pt)."""

    x_band_tolerance: float = 3.0
    """Two observations are in the same_x_band if their x-centers differ by <= this (pt)."""

    # ── Alignment tolerances (when are edges "aligned"?) ──
    alignment_tolerance: float = 2.0
    """Two edges are aligned if their coordinates differ by <= this (pt)."""

    # ── Overlap tolerance (below this, overlap counts as 0) ──
    overlap_tolerance: float = 0.5
    """Overlap values below this (pt or ratio) are treated as 0 (numeric noise)."""

    # ── Distance thresholds (for grouping facts, NOT semantic classification) ──
    horizontal_distance_threshold: float = 12.0
    """Reference gap for x_gap facts (e.g. multi-column same-y detection). NOT a paragraph rule."""

    vertical_distance_threshold: float = 12.0
    """Reference gap for y_gap facts. NOT a paragraph/heading rule."""

    # ── IoU threshold (below this, IoU counts as 0) ──
    iou_tolerance: float = 0.001

    # ── Containment (what fraction of inner must be inside outer?) ──
    containment_ratio_threshold: float = 0.95
    """B is CONTAINED_BY A if >= this fraction of B's area is inside A."""

    def with_overrides(self, **kwargs) -> "GeometryConfig":
        """Return a new config with the given thresholds overridden."""
        import dataclasses
        return dataclasses.replace(self, **kwargs)


# Default singleton — functions accept this when none provided
DEFAULT_CONFIG = GeometryConfig()

# Direction relation vocabulary (geometric, not semantic)
REL_LEFT_OF = "LEFT_OF"
REL_RIGHT_OF = "RIGHT_OF"
REL_ABOVE = "ABOVE"
REL_BELOW = "BELOW"
REL_OVERLAPPING = "OVERLAPPING"
REL_CONTAINED_BY = "CONTAINED_BY"
REL_CONTAINS = "CONTAINS"
REL_SAME_POSITION = "SAME_POSITION"

ALL_RELATIONS = [
    REL_LEFT_OF, REL_RIGHT_OF, REL_ABOVE, REL_BELOW,
    REL_OVERLAPPING, REL_CONTAINED_BY, REL_CONTAINS, REL_SAME_POSITION,
]

# Symmetry map: if A REL B, then B SYM(A) where SYM is:
SYMMETRIC_RELATIONS = {
    REL_OVERLAPPING: REL_OVERLAPPING,
    REL_SAME_POSITION: REL_SAME_POSITION,
}
INVERSE_RELATIONS = {
    REL_LEFT_OF: REL_RIGHT_OF,
    REL_RIGHT_OF: REL_LEFT_OF,
    REL_ABOVE: REL_BELOW,
    REL_BELOW: REL_ABOVE,
    REL_CONTAINED_BY: REL_CONTAINS,
    REL_CONTAINS: REL_CONTAINED_BY,
}


def to_dict(cfg: GeometryConfig) -> dict:
    import dataclasses
    return dataclasses.asdict(cfg)
