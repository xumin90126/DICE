"""
P6 Region — Centralized region configuration.

ALL thresholds live here. No magic numbers in if/else. No document-specific
tuning. No case-specific branches (no if-document-id, no if-text-content).
Geometry-driven region construction ONLY.

Region taxonomy = geometric / layout facts ONLY. No semantic labels.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import dataclasses


# ─────────────────────────────────────────────────────────────────────────────
# Region taxonomy (geometric ONLY — no heading/title/body/caption/table/image/
# formula/flowchart/page_number/header/footer, or any other semantic role).
# ─────────────────────────────────────────────────────────────────────────────
REGION_TYPE_PAGE_TOP = "PAGE_TOP_REGION"        # geometric top band (full-width spans)
REGION_TYPE_PAGE_BOTTOM = "PAGE_BOTTOM_REGION"  # geometric bottom band
REGION_TYPE_FULL_WIDTH = "FULL_WIDTH_REGION"    # full-width spans in middle
REGION_TYPE_COLUMN = "COLUMN_REGION"            # P5 column group (geometric x-stripe)
REGION_TYPE_DENSE = "DENSE_REGION"              # dense connected span cluster
REGION_TYPE_SPARSE = "SPARSE_REGION"            # sparse / isolated spans
REGION_TYPE_UNKNOWN = "UNKNOWN_REGION"          # cannot reliably assign geometrically

ALL_REGION_TYPES = [
    REGION_TYPE_PAGE_TOP, REGION_TYPE_PAGE_BOTTOM, REGION_TYPE_FULL_WIDTH,
    REGION_TYPE_COLUMN, REGION_TYPE_DENSE, REGION_TYPE_SPARSE, REGION_TYPE_UNKNOWN,
]

# ─────────────────────────────────────────────────────────────────────────────
# Deleted taxonomy members (documented, principled):
#   - TEXT_REGION:  requires semantic "text vs non-text" knowledge. P1 provides
#     ONLY text spans (atomic_text.py skips non-text blocks), so "TEXT_REGION"
#     is either trivially-everything or a semantic label, and it collides with
#     DENSE_REGION. Not a strict geometric fact → deleted.
#   - VISUAL_REGION: requires identifying a visual object (image/figure/table).
#     P1 explicitly SKIPS non-text blocks (images/drawings), so no visual-object
#     geometric facts exist in P1–P5. A "void" is absence-of-text, not a visual
#     object, and "这是 Image" is forbidden. → deleted. Large gaps are recorded
#     as geometric facts in decision_trace and deferred to P7.
# ─────────────────────────────────────────────────────────────────────────────

# Construction methods (geometric)
METHOD_TOP_BAND = "top_band"
METHOD_BOTTOM_BAND = "bottom_band"
METHOD_FULL_WIDTH = "full_width"
METHOD_COLUMN_GROUP = "column_group"
METHOD_DENSITY_CLUSTER_DENSE = "density_cluster_dense"
METHOD_DENSITY_CLUSTER_SPARSE = "density_cluster_sparse"
METHOD_UNASSIGNABLE = "unassigned"

# Confidence (geometric construction confidence, NOT semantic classification)
CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"
CONFIDENCE_UNKNOWN = "UNKNOWN"

# Coordinate origin (explicit; never implicit)
COORD_ORIGIN_PDF_TOP_LEFT = "PDF_TOP_LEFT"

# Decision-trace rules (geometric)
RULE_TOP_BAND = "FULL_WIDTH_IN_TOP_BAND"
RULE_BOTTOM_BAND = "FULL_WIDTH_IN_BOTTOM_BAND"
RULE_FULL_WIDTH = "FULL_WIDTH_MIDDLE"
RULE_COLUMN_GROUP = "P5_COLUMN_GROUP_MEMBERSHIP"
RULE_DENSE_CLUSTER = "VERTICAL_CONTIGUITY_DENSE"
RULE_SPARSE_CLUSTER = "ISOLATED_SPARSE"
RULE_UNASSIGNABLE = "UNASSIGNABLE_AMBIGUOUS"


@dataclass(frozen=True)
class RegionConfig:
    """Centralized, immutable, configurable region thresholds."""

    # ── Local density clustering (within a COLUMN_REGION) ──
    dense_gap_threshold: float = 18.0
    """Max vertical gap (pt) between two reading-order-consecutive spans to
    remain in the SAME dense block. Beyond this → block boundary."""

    min_dense_span_count: int = 3
    """A connected block with >= this many spans is DENSE; fewer → SPARSE."""

    density_area_unit: float = 10000.0
    """Area unit (pt²) for density normalization (spans per 10000 pt²)."""

    sparse_confidence_high_gap: float = 40.0
    """If an isolated span's gap to its nearest neighbor >= this (pt), its
    SPARSE classification is HIGH confidence (clearly isolated)."""

    # ── Construction ──
    construction_version: str = "v1"

    def with_overrides(self, **kwargs) -> "RegionConfig":
        return dataclasses.replace(self, **kwargs)


DEFAULT_CONFIG = RegionConfig()


def to_dict(cfg: RegionConfig) -> dict:
    return dataclasses.asdict(cfg)
