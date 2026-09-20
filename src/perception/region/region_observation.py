"""
P6 Region — RegionObservation schema.

A region is a DERIVED GEOMETRIC organization of P4 spans + P5 column layout.
NOT a semantic classification (no heading/title/table/image/... labels).
Reverse-traceable to span_id via source_span_ids, with decision trace,
provenance, and an explicit coordinate origin.

Hierarchy is bounded (two levels, never arbitrary depth):
  Page Layout
    └─ Major region (PAGE_TOP_REGION / COLUMN_REGION / FULL_WIDTH_REGION /
       PAGE_BOTTOM_REGION / UNKNOWN_REGION)
         └─ Local region (DENSE_REGION / SPARSE_REGION), parent_region_id →
            its COLUMN_REGION.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class RegionObservation:
    """Geometric layout region — a deterministic grouping of spans.

    Every region can answer:
      - WHICH spans compose me?   → source_span_ids / span_ids
      - WHERE am I?               → region_geometry / geometry_summary
      - WHAT geometric facts?     → region_features
      - WHY were they grouped?    → decision_trace
      - HOW certain?              → confidence (geometric, NOT semantic)
      - WHERE in hierarchy?       → parent_region_id (None = major region)
    """

    region_id: str
    document_id: str
    page_number: int
    region_type: str                 # geometric region type (region_config taxonomy)

    span_ids: List[str]              # canonical membership (all spans in region)
    source_span_ids: List[str]       # construction source refs (P4/P5 span ids)

    region_geometry: Dict[str, Any]  # {bbox, width, height, center_x, center_y}
    geometry_summary: Dict[str, Any] # {area, span_count, density, avg_width, avg_height, ...}
    region_features: Dict[str, Any]  # discriminating geometric facts (gaps, column id, ...)

    confidence: str                  # HIGH/MEDIUM/LOW/UNKNOWN
    construction_method: str
    construction_version: str
    decision_trace: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    coord_origin: str = "PDF_TOP_LEFT"
    parent_region_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageRegionSet:
    """All regions for one page (bounded hierarchy: major → local)."""

    page_number: int
    page_width: float
    page_height: float
    coord_origin: str
    regions: List[Dict[str, Any]] = field(default_factory=list)
    region_count: int = 0
    orphan_span_ids: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
