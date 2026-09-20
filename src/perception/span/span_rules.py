"""
P4 Span — merge decision rules.

Rules are based ONLY on P1/P2/P3 facts (geometry, style, source order).
NO semantic classification. NO text-content rules. NO case-specific patches.

Each decision produces a geometric reason traceable to facts.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .span_config import (
    SpanConfig, DEFAULT_CONFIG,
    REASON_MERGE, REASON_KEEP_SEPARATE,
    MERGE_REASON_SAME_LINE_CONTIGUOUS, MERGE_REASON_NEXT_LINE_CONTIGUOUS,
    SEPARATE_REASON_LARGE_HORIZONTAL_GAP, SEPARATE_REASON_CROSS_COLUMN_GAP,
    SEPARATE_REASON_LARGE_VERTICAL_GAP, SEPARATE_REASON_PAGE_BOUNDARY,
    SEPARATE_REASON_STYLE_BREAK, SEPARATE_REASON_NOT_ADJACENT,
    SEPARATE_REASON_NO_OVERLAP,
)
from .span_observation import MergeDecision


def decide_merge(
    obs_a: Dict[str, Any],
    obs_b: Dict[str, Any],
    geom_ab: Optional[Dict[str, Any]],   # P2 PairwiseRelation dict (A relative to B)
    style_a: Optional[Dict[str, Any]],   # P3 StyleObservation dict
    style_b: Optional[Dict[str, Any]],
    cfg: SpanConfig = DEFAULT_CONFIG,
) -> MergeDecision:
    """Decide whether observation A and B (in source/reading order) should merge.

    A is BEFORE B in source order (reading_order_hint or source_index).
    Decision is based on geometric + style facts only.
    """
    bb_a = obs_a.get("bbox")
    bb_b = obs_b.get("bbox")
    if bb_a is None or bb_b is None:
        return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     SEPARATE_REASON_NO_OVERLAP, "missing bbox")

    # Extract facts from P2 geometry relation (A relative to B)
    if geom_ab is not None:
        h_dist = geom_ab.get("horizontal_distance", 0.0)
        v_dist = geom_ab.get("vertical_distance", 0.0)
        h_overlap = geom_ab.get("horizontal_overlap", 0.0)
        v_overlap = geom_ab.get("vertical_overlap", 0.0)
        same_y = geom_ab.get("same_y_band", False)
        same_x = geom_ab.get("same_x_band", False)
    else:
        # compute directly from bboxes (fallback)
        h_overlap = max(0.0, min(bb_a[2], bb_b[2]) - max(bb_a[0], bb_b[0]))
        v_overlap = max(0.0, min(bb_a[3], bb_b[3]) - max(bb_a[1], bb_b[1]))
        h_dist = max(0.0, max(bb_b[0] - bb_a[2], bb_a[0] - bb_b[2])) if bb_b[0] > bb_a[2] else max(0.0, bb_b[0] - bb_a[2]) if bb_b[0] > bb_a[2] else 0.0
        v_dist = max(0.0, bb_b[1] - bb_a[3]) if bb_b[1] > bb_a[3] else 0.0
        ca_y = (bb_a[1] + bb_a[3]) / 2
        cb_y = (bb_b[1] + bb_b[3]) / 2
        same_y = abs(ca_y - cb_y) <= cfg.same_line_tolerance
        ca_x = (bb_a[0] + bb_a[2]) / 2
        cb_x = (bb_b[0] + bb_b[2]) / 2
        same_x = abs(ca_x - cb_x) <= cfg.same_line_tolerance

    same_page = obs_a.get("page_number") == obs_b.get("page_number")

    # style facts
    sig_a = style_a.get("style_signature") if style_a else None
    sig_b = style_b.get("style_signature") if style_b else None
    same_sig = (sig_a is not None and sig_b is not None and sig_a == sig_b)
    style_diff = None
    if style_a and style_b:
        style_diff = style_a.get("style_difference") if "style_difference" in style_a else None

    # source order adjacency (A immediately before B in source_index within same source_type)
    sa_idx = obs_a.get("source_index", -1)
    sb_idx = obs_b.get("source_index", -1)
    same_source = obs_a.get("source_type") == obs_b.get("source_type")
    source_adjacent = same_source and (sb_idx == sa_idx + 1)

    # ── Decision logic (geometric, ordered by blocking conditions) ──

    # 1. Page boundary: never cross pages (ordinary spans)
    if not same_page:
        return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     SEPARATE_REASON_PAGE_BOUNDARY,
                     f"page {obs_a.get('page_number')} != {obs_b.get('page_number')}")

    # 2. Same y-band (same line) → check horizontal contiguity
    if same_y:
        if h_dist > cfg.cross_column_gap_threshold:
            # large horizontal gap on same line → cross-column, keep separate
            return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                         SEPARATE_REASON_CROSS_COLUMN_GAP,
                         f"h_dist={h_dist:.1f} > {cfg.cross_column_gap_threshold}")
        if h_dist > cfg.max_horizontal_gap:
            return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                         SEPARATE_REASON_LARGE_HORIZONTAL_GAP,
                         f"h_dist={h_dist:.1f} > {cfg.max_horizontal_gap}")
        # same line, small gap → merge (if source adjacent or x-contiguous)
        if h_overlap > cfg.overlap_tolerance or h_dist <= cfg.max_horizontal_gap:
            return _merge(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                          MERGE_REASON_SAME_LINE_CONTIGUOUS,
                          f"same_y, h_dist={h_dist:.1f} <= {cfg.max_horizontal_gap}")
        return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     SEPARATE_REASON_LARGE_HORIZONTAL_GAP,
                     f"h_dist={h_dist:.1f}")

    # 3. Different y-band (different lines) → check vertical contiguity
    if v_dist > cfg.max_vertical_gap:
        return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     SEPARATE_REASON_LARGE_VERTICAL_GAP,
                     f"v_dist={v_dist:.1f} > {cfg.max_vertical_gap}")

    # vertically close: check if A is above B with x-overlap (same column flow)
    if v_dist <= cfg.max_vertical_gap and h_overlap > cfg.overlap_tolerance:
        # A above B, x-overlapping → likely next line in same text flow
        return _merge(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                      MERGE_REASON_NEXT_LINE_CONTIGUOUS,
                      f"v_dist={v_dist:.1f}, h_overlap={h_overlap:.1f}")

    # vertically close but no x-overlap → different columns, keep separate
    if v_dist <= cfg.max_vertical_gap and h_overlap <= cfg.overlap_tolerance:
        return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     SEPARATE_REASON_CROSS_COLUMN_GAP,
                     f"v_close={v_dist:.1f} but h_overlap={h_overlap:.1f}")

    return _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                 SEPARATE_REASON_NOT_ADJACENT, "no contiguity condition met")


def _merge(obs_a, obs_b, geom_ab, style_a, style_b, cfg, reason, detail):
    return _decision(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     REASON_MERGE, reason, detail)

def _keep(obs_a, obs_b, geom_ab, style_a, style_b, cfg, reason, detail):
    return _decision(obs_a, obs_b, geom_ab, style_a, style_b, cfg,
                     REASON_KEEP_SEPARATE, reason, detail)

def _decision(obs_a, obs_b, geom_ab, style_a, style_b, cfg, decision, reason, detail):
    if geom_ab is not None:
        h_dist = geom_ab.get("horizontal_distance", 0.0)
        v_dist = geom_ab.get("vertical_distance", 0.0)
        h_overlap = geom_ab.get("horizontal_overlap", 0.0)
        v_overlap = geom_ab.get("vertical_overlap", 0.0)
        same_y = geom_ab.get("same_y_band", False)
        same_x = geom_ab.get("same_x_band", False)
    else:
        bb_a, bb_b = obs_a["bbox"], obs_b["bbox"]
        h_overlap = max(0.0, min(bb_a[2], bb_b[2]) - max(bb_a[0], bb_b[0]))
        v_overlap = max(0.0, min(bb_a[3], bb_b[3]) - max(bb_a[1], bb_b[1]))
        h_dist = max(0.0, bb_b[0] - bb_a[2]) if bb_b[0] > bb_a[2] else 0.0
        v_dist = max(0.0, bb_b[1] - bb_a[3]) if bb_b[1] > bb_a[3] else 0.0
        same_y = abs((bb_a[1]+bb_a[3])/2 - (bb_b[1]+bb_b[3])/2) <= cfg.same_line_tolerance
        same_x = abs((bb_a[0]+bb_a[2])/2 - (bb_b[0]+bb_b[2])/2) <= cfg.same_line_tolerance

    same_page = obs_a.get("page_number") == obs_b.get("page_number")
    sig_a = style_a.get("style_signature") if style_a else None
    sig_b = style_b.get("style_signature") if style_b else None
    same_sig = sig_a is not None and sig_b is not None and sig_a == sig_b

    return MergeDecision(
        observation_a_id=obs_a.get("observation_id", ""),
        observation_b_id=obs_b.get("observation_id", ""),
        same_y_band=same_y,
        same_x_band=same_x,
        horizontal_distance=round(h_dist, 2),
        vertical_distance=round(v_dist, 2),
        horizontal_overlap=round(h_overlap, 2),
        vertical_overlap=round(v_overlap, 2),
        same_page=same_page,
        same_style_signature=same_sig,
        style_difference=style_a.get("style_difference") if style_a and "style_difference" in style_a else None,
        source_order_adjacent=(obs_a.get("source_type") == obs_b.get("source_type")
                                and obs_b.get("source_index", -1) == obs_a.get("source_index", -2) + 1),
        decision=decision,
        reason=reason,
        facts_summary={"detail": detail, "config_version": cfg.construction_version},
    )
