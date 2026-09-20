"""
P2 Geometry — GeometryObservation schema.

Two observation shapes:
  1. SingleObservationGeometry — derived geometry for ONE AtomicTextObservation
     (width/height/center/page_position/band-membership facts).
  2. PairwiseRelation — geometric relation between TWO observations
     (distance/overlap/IoU/direction/alignment).

Both are pure GEOMETRIC FACTS. No semantic classification
(no is_heading / is_table / is_column / is_paragraph).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SingleObservationGeometry:
    """Derived geometry for one AtomicTextObservation (pure facts)."""

    observation_id: str
    document_id: str
    page_number: int

    # bbox (copied from source for self-containment)
    bbox: List[float]  # [x0, y0, x1, y1]

    # derived geometry
    width: float
    height: float
    center_x: float
    center_y: float

    # page-relative geometry (requires page dimensions; null if unknown)
    page_width: Optional[float]
    page_height: Optional[float]
    normalized_x: Optional[float]   # center_x / page_width
    normalized_y: Optional[float]   # center_y / page_height

    # band facts (computed against ALL observations on the page; populated by engine)
    # These are lists of observation_ids that share the band, NOT semantic groups.
    same_y_band_members: List[str] = field(default_factory=list)
    same_x_band_members: List[str] = field(default_factory=list)

    # alignment-group facts (observation_ids sharing an aligned edge)
    left_alignment_group: List[str] = field(default_factory=list)
    right_alignment_group: List[str] = field(default_factory=list)
    top_alignment_group: List[str] = field(default_factory=list)
    bottom_alignment_group: List[str] = field(default_factory=list)
    center_alignment_group: List[str] = field(default_factory=list)

    # spatial-cluster fact (observation_ids within vertical_distance_threshold in y)
    spatial_cluster_members: List[str] = field(default_factory=list)

    # x-projection density fact (count of observations whose x-range overlaps this obs's x-range)
    x_projection_overlap_count: int = 0

    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PairwiseRelation:
    """Geometric relation of observation A relative to observation B (pure facts)."""

    relation_id: str
    document_id: str
    page_number: int

    observation_a_id: str
    observation_b_id: str

    # direction relation (one of REL_*)
    direction: str

    # distances
    horizontal_distance: float   # >= 0; gap in x (0 if overlapping in x)
    vertical_distance: float     # >= 0; gap in y (0 if overlapping in y)

    # overlaps
    horizontal_overlap: float    # >= 0; overlap length in x (0 if no x-overlap)
    vertical_overlap: float      # >= 0; overlap length in y (0 if no y-overlap)
    bbox_overlap_area: float     # horizontal_overlap * vertical_overlap (0 if no overlap)
    iou: float                   # intersection / union (0 if no overlap)

    # alignment facts (booleans)
    left_alignment: bool
    right_alignment: bool
    top_alignment: bool
    bottom_alignment: bool
    center_alignment: bool

    # band facts
    same_y_band: bool
    same_x_band: bool

    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageGeometryBundle:
    """All geometry facts for one page: single-obs geometries + pairwise relations."""
    document_id: str
    page_number: int
    page_width: Optional[float]
    page_height: Optional[float]
    config_snapshot: Dict[str, Any]
    single_geometries: List[Dict[str, Any]] = field(default_factory=list)
    pairwise_relations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
