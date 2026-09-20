"""
P2 Geometry — computation engine.

Pure geometric computation over P1 AtomicTextObservation.
NO semantic classification. Every output is traceable to a source observation.

Computes:
  - SingleObservationGeometry: derived bbox facts (width/height/center/page-relative)
    + band/alignment/cluster/projection membership facts.
  - PairwiseRelation: A-relative-to-B direction + distance + overlap + IoU + alignment + band.

Symmetry is enforced: for every (A,B) relation, the engine guarantees the
(B,A) relation is the geometric inverse (LEFT_OF<->RIGHT_OF, ABOVE<->BELOW,
CONTAINED_BY<->CONTAINS, OVERLAPPING/SAME_POSITION symmetric).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Tuple

from .geometry_config import (
    GeometryConfig, DEFAULT_CONFIG,
    REL_LEFT_OF, REL_RIGHT_OF, REL_ABOVE, REL_BELOW,
    REL_OVERLAPPING, REL_CONTAINED_BY, REL_CONTAINS, REL_SAME_POSITION,
)
from .geometry_observation import (
    SingleObservationGeometry, PairwiseRelation, PageGeometryBundle,
)


# ── Primitive bbox math (no thresholds) ───────────────────────────────────

def _bbox_area(bb) -> float:
    x0, y0, x1, y1 = bb
    w = x1 - x0
    h = y1 - y0
    return w * h if w > 0 and h > 0 else 0.0


def _intersection(bb_a, bb_b) -> Tuple[float, float, float, float]:
    """Return (ix0, iy0, ix1, iy1) of intersection; degenerate if no overlap."""
    ix0 = max(bb_a[0], bb_b[0])
    iy0 = max(bb_a[1], bb_b[1])
    ix1 = min(bb_a[2], bb_b[2])
    iy1 = min(bb_a[3], bb_b[3])
    return ix0, iy0, ix1, iy1


def _overlap_len(a_lo, a_hi, b_lo, b_hi) -> float:
    """1D overlap length (>=0)."""
    lo = max(a_lo, b_lo)
    hi = min(a_hi, b_hi)
    return max(0.0, hi - lo)


def _gap_len(a_lo, a_hi, b_lo, b_hi) -> float:
    """1D gap length between two intervals (>=0; 0 if overlapping)."""
    if a_hi < b_lo:
        return b_lo - a_hi
    if b_hi < a_lo:
        return a_lo - b_hi
    return 0.0


def _iou(bb_a, bb_b) -> float:
    ix0, iy0, ix1, iy1 = _intersection(bb_a, bb_b)
    iw = max(0.0, ix1 - ix0)
    ih = max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = _bbox_area(bb_a) + _bbox_area(bb_b) - inter
    if union <= 0:
        return 0.0
    return inter / union


def _containment_ratio(inner, outer) -> float:
    """Fraction of inner's area inside outer."""
    ix0, iy0, ix1, iy1 = _intersection(inner, outer)
    iw = max(0.0, ix1 - ix0)
    ih = max(0.0, iy1 - iy0)
    inter = iw * ih
    inner_area = _bbox_area(inner)
    if inner_area <= 0:
        return 0.0
    return inter / inner_area


# ── Pairwise direction ────────────────────────────────────────────────────

def _direction(bb_a, bb_b, cfg: GeometryConfig) -> str:
    """Geometric direction of A relative to B.

    Priority: SAME_POSITION > CONTAINED_BY/CONTAINS > OVERLAPPING > LEFT/RIGHT/ABOVE/BELOW.
    All based on geometry only.
    """
    iou = _iou(bb_a, bb_b)
    if iou >= 1.0 - cfg.iou_tolerance:
        return REL_SAME_POSITION

    # containment (one bbox almost fully inside the other)
    a_in_b = _containment_ratio(bb_a, bb_b)
    b_in_a = _containment_ratio(bb_b, bb_a)
    if a_in_b >= cfg.containment_ratio_threshold:
        return REL_CONTAINED_BY
    if b_in_a >= cfg.containment_ratio_threshold:
        return REL_CONTAINS

    # overlap (any area overlap beyond tolerance)
    ix0, iy0, ix1, iy1 = _intersection(bb_a, bb_b)
    iw = max(0.0, ix1 - ix0)
    ih = max(0.0, iy1 - iy0)
    if iw > cfg.overlap_tolerance and ih > cfg.overlap_tolerance:
        return REL_OVERLAPPING

    # disjoint: decide by dominant axis.
    # Only reach here if the 2D overlap area is at or below tolerance.
    # But the bboxes may still touch/overlap on ONE axis (edge kiss). If both
    # axes have zero gap (bboxes intersect in both dims, area just tiny), treat
    # as OVERLAPPING to preserve symmetry (LEFT/RIGHT needs a real x gap).
    h_gap = _gap_len(bb_a[0], bb_a[2], bb_b[0], bb_b[2])
    v_gap = _gap_len(bb_a[1], bb_a[3], bb_b[1], bb_b[3])
    if h_gap <= 0.0 and v_gap <= 0.0:
        # bboxes intersect in both axes but area below tolerance → edge kiss
        return REL_OVERLAPPING
    # there is a real gap on at least one axis → disjoint
    if h_gap >= v_gap:
        # horizontal-dominant gap: A is left or right of B
        if bb_a[2] <= bb_b[0]:
            return REL_LEFT_OF
        return REL_RIGHT_OF
    else:
        if bb_a[3] <= bb_b[1]:
            return REL_ABOVE
        return REL_BELOW


# ── Alignment booleans ────────────────────────────────────────────────────

def _aligned(a_val: float, b_val: float, tol: float) -> bool:
    return abs(a_val - b_val) <= tol


# ── Relation id ───────────────────────────────────────────────────────────

def _relation_id(a_id: str, b_id: str) -> str:
    raw = f"{a_id}>{b_id}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


# ── Pairwise relation computation ─────────────────────────────────────────

def compute_pairwise(a, b, cfg: GeometryConfig = DEFAULT_CONFIG) -> PairwiseRelation:
    """Compute the geometric relation of observation A relative to observation B.

    `a` and `b` are P1 AtomicTextObservation dicts (must have bbox + observation_id).
    """
    bb_a = a["bbox"]
    bb_b = b["bbox"]
    if bb_a is None or bb_b is None:
        raise ValueError("pairwise relation requires both observations to have bbox")

    h_overlap = _overlap_len(bb_a[0], bb_a[2], bb_b[0], bb_b[2])
    v_overlap = _overlap_len(bb_a[1], bb_a[3], bb_b[1], bb_b[3])
    h_dist = _gap_len(bb_a[0], bb_a[2], bb_b[0], bb_b[2])
    v_dist = _gap_len(bb_a[1], bb_a[3], bb_b[1], bb_b[3])
    overlap_area = (h_overlap * v_overlap
                    if h_overlap > cfg.overlap_tolerance and v_overlap > cfg.overlap_tolerance
                    else 0.0)
    iou = _iou(bb_a, bb_b)
    if iou < cfg.iou_tolerance:
        iou = 0.0

    ca_x = (bb_a[0] + bb_a[2]) / 2
    ca_y = (bb_a[1] + bb_a[3]) / 2
    cb_x = (bb_b[0] + bb_b[2]) / 2
    cb_y = (bb_b[1] + bb_b[3]) / 2

    direction = _direction(bb_a, bb_b, cfg)

    return PairwiseRelation(
        relation_id=_relation_id(a["observation_id"], b["observation_id"]),
        document_id=a["document_id"],
        page_number=a["page_number"],
        observation_a_id=a["observation_id"],
        observation_b_id=b["observation_id"],
        direction=direction,
        horizontal_distance=round(h_dist, 2),
        vertical_distance=round(v_dist, 2),
        horizontal_overlap=round(h_overlap, 2),
        vertical_overlap=round(v_overlap, 2),
        bbox_overlap_area=round(overlap_area, 2),
        iou=round(iou, 4),
        left_alignment=_aligned(bb_a[0], bb_b[0], cfg.alignment_tolerance),
        right_alignment=_aligned(bb_a[2], bb_b[2], cfg.alignment_tolerance),
        top_alignment=_aligned(bb_a[1], bb_b[1], cfg.alignment_tolerance),
        bottom_alignment=_aligned(bb_a[3], bb_b[3], cfg.alignment_tolerance),
        center_alignment=_aligned(ca_x, cb_x, cfg.alignment_tolerance)
                           and _aligned(ca_y, cb_y, cfg.alignment_tolerance),
        same_y_band=abs(ca_y - cb_y) <= cfg.y_band_tolerance,
        same_x_band=abs(ca_x - cb_x) <= cfg.x_band_tolerance,
        provenance={
            "config": "GeometryConfig",
            "source_layer_a": a.get("source_type"),
            "source_layer_b": b.get("source_type"),
        },
    )


# ── Symmetry verification ─────────────────────────────────────────────────

from .geometry_config import INVERSE_RELATIONS, SYMMETRIC_RELATIONS


def expected_inverse(direction: str) -> str:
    """The geometrically-required inverse direction."""
    if direction in SYMMETRIC_RELATIONS:
        return SYMMETRIC_RELATIONS[direction]
    return INVERSE_RELATIONS.get(direction, direction)


def verify_symmetry(rel_ab: PairwiseRelation, rel_ba: PairwiseRelation) -> bool:
    """Check that (B,A) is the geometric inverse of (A,B)."""
    expected = expected_inverse(rel_ab.direction)
    return rel_ba.direction == expected


# ── Single-observation derived geometry ───────────────────────────────────

def compute_single(obs, page_width=None, page_height=None,
                   cfg: GeometryConfig = DEFAULT_CONFIG) -> SingleObservationGeometry:
    """Compute derived geometry for one observation (no pairwise)."""
    bb = obs["bbox"]
    if bb is None:
        raise ValueError("observation requires bbox")
    x0, y0, x1, y1 = bb
    width = x1 - x0
    height = y1 - y0
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    norm_x = round(cx / page_width, 4) if page_width else None
    norm_y = round(cy / page_height, 4) if page_height else None
    return SingleObservationGeometry(
        observation_id=obs["observation_id"],
        document_id=obs["document_id"],
        page_number=obs["page_number"],
        bbox=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
        width=round(width, 2),
        height=round(height, 2),
        center_x=round(cx, 2),
        center_y=round(cy, 2),
        page_width=round(page_width, 2) if page_width else None,
        page_height=round(page_height, 2) if page_height else None,
        normalized_x=norm_x,
        normalized_y=norm_y,
        provenance={"source_type": obs.get("source_type"), "source_index": obs.get("source_index")},
    )


# ── Page bundle: single + pairwise + band/alignment groups ────────────────

def compute_page_bundle(observations, page_width=None, page_height=None,
                        cfg: GeometryConfig = DEFAULT_CONFIG,
                        max_pairwise: Optional[int] = None) -> PageGeometryBundle:
    """Compute all geometry facts for one page's observations.

    Args:
        observations: list of P1 AtomicTextObservation dicts (same page).
        page_width/page_height: page dimensions (for normalized coords).
        cfg: threshold config.
        max_pairwise: cap on pairwise relations (None = all pairs; for large pages
            set a cap to keep output tractable — relations are still geometric facts).
    """
    obs_with_bbox = [o for o in observations if o.get("bbox") is not None]
    doc_id = obs_with_bbox[0]["document_id"] if obs_with_bbox else ""
    pno = obs_with_bbox[0]["page_number"] if obs_with_bbox else 0

    # 1. single geometries
    singles = [compute_single(o, page_width, page_height, cfg) for o in obs_with_bbox]

    # 2. pairwise relations (all ordered pairs A!=B)
    relations: List[PairwiseRelation] = []
    n = len(obs_with_bbox)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            relations.append(compute_pairwise(obs_with_bbox[i], obs_with_bbox[j], cfg))
            if max_pairwise is not None and len(relations) >= max_pairwise:
                break
        if max_pairwise is not None and len(relations) >= max_pairwise:
            break

    # 3. band / alignment / cluster / projection membership (populate singles)
    _populate_group_facts(singles, relations, cfg)

    from .geometry_config import to_dict as _cfg_dict
    return PageGeometryBundle(
        document_id=doc_id,
        page_number=pno,
        page_width=round(page_width, 2) if page_width else None,
        page_height=round(page_height, 2) if page_height else None,
        config_snapshot=_cfg_dict(cfg),
        single_geometries=[s.to_dict() for s in singles],
        pairwise_relations=[r.to_dict() for r in relations],
    )


def _populate_group_facts(singles: List[SingleObservationGeometry],
                          relations: List[PairwiseRelation],
                          cfg: GeometryConfig):
    """Populate band/alignment/cluster/projection membership lists on each single."""
    by_id = {s.observation_id: s for s in singles}
    for s in singles:
        s.same_y_band_members = []
        s.same_x_band_members = []
        s.left_alignment_group = []
        s.right_alignment_group = []
        s.top_alignment_group = []
        s.bottom_alignment_group = []
        s.center_alignment_group = []
        s.spatial_cluster_members = []
        s.x_projection_overlap_count = 0

    for r in relations:
        a = by_id.get(r.observation_a_id)
        if a is None:
            continue
        b_id = r.observation_b_id
        if r.same_y_band:
            a.same_y_band_members.append(b_id)
        if r.same_x_band:
            a.same_x_band_members.append(b_id)
        if r.left_alignment:
            a.left_alignment_group.append(b_id)
        if r.right_alignment:
            a.right_alignment_group.append(b_id)
        if r.top_alignment:
            a.top_alignment_group.append(b_id)
        if r.bottom_alignment:
            a.bottom_alignment_group.append(b_id)
        if r.center_alignment:
            a.center_alignment_group.append(b_id)
        # spatial cluster: vertical distance within threshold (y-proximity fact)
        if r.vertical_distance <= cfg.vertical_distance_threshold and r.vertical_distance >= 0:
            a.spatial_cluster_members.append(b_id)
        # x-projection overlap: horizontal_overlap > 0 means x-ranges overlap
        if r.horizontal_overlap > cfg.overlap_tolerance:
            a.x_projection_overlap_count += 1


__all__ = [
    "compute_single", "compute_pairwise", "compute_page_bundle",
    "verify_symmetry", "expected_inverse",
]
