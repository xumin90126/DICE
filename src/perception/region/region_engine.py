"""
P6 Region Engine — deterministic geometric region construction.

Inputs (READ-ONLY):
  - P4 spans  (list of span dicts: span_id, bbox, document_id, page_number,
               source_observation_ids, source_observation_types, ...)
  - P5 column layout (dict: top/bottom/full-width/ambiguous span buckets +
               column_groups with member_span_ids)
  - P5 reading order (dict: span_id -> reading_order_index)

Algorithm per page (deterministic, no ML, no keyword, no case-specific branch):
  1. MAJOR regions — map P5 geometric buckets 1:1:
       top_region_span_ids   → PAGE_TOP_REGION
       each column group     → COLUMN_REGION (per column)
       full_width_span_ids   → FULL_WIDTH_REGION
       bottom_region_span_ids→ PAGE_BOTTOM_REGION
       ambiguous_span_ids    → UNKNOWN_REGION
     (any span not in any bucket is defensively put in UNKNOWN_REGION.)
  2. LOCAL regions — within each COLUMN_REGION, cluster member spans by vertical
     contiguity in reading order:
       connected block (vertical gap <= dense_gap_threshold)
         → span_count >= min_dense_span_count  ⇒ DENSE_REGION
         → span_count <  min_dense_span_count  ⇒ SPARSE_REGION
       parent_region_id = the COLUMN_REGION's region_id.
  3. Every region carries full provenance + decision_trace + confidence +
     explicit coord_origin.

No semantic interpretation. No reverse modification of spans / P5.
Deterministic: region_id is a sha1 over (document, page, type, sorted span ids).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from .region_config import (
    RegionConfig, DEFAULT_CONFIG,
    REGION_TYPE_PAGE_TOP, REGION_TYPE_PAGE_BOTTOM, REGION_TYPE_FULL_WIDTH,
    REGION_TYPE_COLUMN, REGION_TYPE_DENSE, REGION_TYPE_SPARSE, REGION_TYPE_UNKNOWN,
    METHOD_TOP_BAND, METHOD_BOTTOM_BAND, METHOD_FULL_WIDTH, METHOD_COLUMN_GROUP,
    METHOD_DENSITY_CLUSTER_DENSE, METHOD_DENSITY_CLUSTER_SPARSE, METHOD_UNASSIGNABLE,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW, CONFIDENCE_UNKNOWN,
    COORD_ORIGIN_PDF_TOP_LEFT,
    RULE_TOP_BAND, RULE_BOTTOM_BAND, RULE_FULL_WIDTH, RULE_COLUMN_GROUP,
    RULE_DENSE_CLUSTER, RULE_SPARSE_CLUSTER, RULE_UNASSIGNABLE,
)
from .region_observation import RegionObservation, PageRegionSet


def _cx(s): return (s["bbox"][0] + s["bbox"][2]) / 2.0
def _cy(s): return (s["bbox"][1] + s["bbox"][3]) / 2.0
def _w(s):  return s["bbox"][2] - s["bbox"][0]
def _h(s):  return s["bbox"][3] - s["bbox"][1]


_CONF_ORDER = {CONFIDENCE_HIGH: 3, CONFIDENCE_MEDIUM: 2, CONFIDENCE_LOW: 1, CONFIDENCE_UNKNOWN: 0}


def _min_conf(a: str, b: str) -> str:
    """Return the more conservative (lower) of two confidence levels."""
    return a if _CONF_ORDER.get(a, 1) <= _CONF_ORDER.get(b, 1) else b


def _bbox_union(spans: List[Dict[str, Any]]) -> List[float]:
    x0 = min(s["bbox"][0] for s in spans)
    y0 = min(s["bbox"][1] for s in spans)
    x1 = max(s["bbox"][2] for s in spans)
    y1 = max(s["bbox"][3] for s in spans)
    return [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]


def _region_id(document_id: str, page_number: int, region_type: str,
               span_ids: List[str]) -> str:
    key = f"{document_id}|{page_number}|{region_type}|{','.join(sorted(span_ids))}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def _geometry(bbox: List[float]) -> Dict[str, Any]:
    w = round(bbox[2] - bbox[0], 2)
    h = round(bbox[3] - bbox[1], 2)
    return {
        "bbox": bbox,
        "width": w,
        "height": h,
        "center_x": round(bbox[0] + w / 2.0, 2),
        "center_y": round(bbox[1] + h / 2.0, 2),
    }


def _summary(bbox: List[float], span_ids: List[str], spans: List[Dict[str, Any]],
             cfg: RegionConfig) -> Dict[str, Any]:
    area = max(1e-6, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
    n = len(span_ids)
    widths = [_w(s) for s in spans]
    heights = [_h(s) for s in spans]
    return {
        "area": round(area, 2),
        "span_count": n,
        "density": round(n * cfg.density_area_unit / area, 4),
        "avg_width": round(sum(widths) / n, 2) if n else 0.0,
        "avg_height": round(sum(heights) / n, 2) if n else 0.0,
        "x_span": round(bbox[2] - bbox[0], 2),
        "y_span": round(bbox[3] - bbox[1], 2),
    }


def _span_provenance(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reverse traceability to P1 observations through the P4 spans."""
    obs_ids: List[str] = []
    obs_types: List[str] = []
    for s in spans:
        for oid in s.get("source_observation_ids", []):
            obs_ids.append(oid)
        for ot in s.get("source_observation_types", []):
            if ot not in obs_types:
                obs_types.append(ot)
    return {
        "source_span_ids": [s["span_id"] for s in spans],
        "source_observation_ids": obs_ids,
        "source_observation_types": obs_types,
    }


def _make_region(document_id, page_number, region_type, span_ids, spans,
                 cfg, construction_method, features, trace, confidence,
                 parent_region_id=None) -> RegionObservation:
    bbox = _bbox_union(spans)
    return RegionObservation(
        region_id=_region_id(document_id, page_number, region_type, span_ids),
        document_id=document_id,
        page_number=page_number,
        region_type=region_type,
        span_ids=sorted(span_ids),
        source_span_ids=sorted(span_ids),
        region_geometry=_geometry(bbox),
        geometry_summary=_summary(bbox, span_ids, spans, cfg),
        region_features=features,
        confidence=confidence,
        construction_method=construction_method,
        construction_version=cfg.construction_version,
        decision_trace=trace,
        provenance=_span_provenance(spans),
        coord_origin=COORD_ORIGIN_PDF_TOP_LEFT,
        parent_region_id=parent_region_id,
    )


def _cluster_by_vertical_contiguity(member_spans: List[Dict[str, Any]],
                                    span_order: Dict[str, int],
                                    cfg: RegionConfig):
    """Cluster spans (in reading order) into connected blocks by vertical
    contiguity. Returns (blocks, boundary_gaps) where boundary_gaps[i] is the
    vertical gap between block[i-1] and block[i] (None for the first block)."""
    if not member_spans:
        return [], []
    ordered = sorted(member_spans,
                     key=lambda s: (span_order.get(s["span_id"], 10**9), _cy(s), _cx(s)))
    blocks: List[List[Dict[str, Any]]] = []
    boundary_gaps: List[Optional[float]] = [None]
    current = [ordered[0]]
    for s in ordered[1:]:
        gap = s["bbox"][1] - current[-1]["bbox"][3]   # next.y0 - prev.y1
        if gap <= cfg.dense_gap_threshold:
            current.append(s)
        else:
            blocks.append(current)
            boundary_gaps.append(round(gap, 2))
            current = [s]
    blocks.append(current)
    # boundary_gaps length == len(blocks); boundary_gaps[0] is None
    return blocks, boundary_gaps


def _local_confidence(block: List[Dict[str, Any]], region_type: str,
                      isolation_gap: Optional[float], cfg: RegionConfig) -> str:
    if region_type == REGION_TYPE_DENSE:
        # clearly dense: all internal gaps well within the dense threshold
        internal_gaps = []
        for i in range(len(block) - 1):
            internal_gaps.append(block[i + 1]["bbox"][1] - block[i]["bbox"][3])
        max_gap = max(internal_gaps) if internal_gaps else 0.0
        return CONFIDENCE_HIGH if max_gap <= cfg.dense_gap_threshold / 2.0 else CONFIDENCE_MEDIUM
    # SPARSE
    if isolation_gap is not None and isolation_gap >= cfg.sparse_confidence_high_gap:
        return CONFIDENCE_HIGH
    return CONFIDENCE_MEDIUM


def compute_page_regions(spans: List[Dict[str, Any]],
                         page_width: float,
                         page_height: float,
                         layout: Dict[str, Any],
                         span_order: Dict[str, int],
                         cfg: RegionConfig = DEFAULT_CONFIG,
                         page_confidence: Optional[str] = None) -> PageRegionSet:
    """Construct all geometric regions for one page. Read-only inputs.

    page_confidence: the reading-order confidence (P5 PageReadingOrder.confidence),
    which already incorporates overlap ambiguity. It is the baseline geometric
    certainty and is min()'d with column/local confidence so that overlap
    ambiguity propagates to region confidence (not just column detection)."""
    span_by_id = {s["span_id"]: s for s in spans}
    all_span_ids = [s["span_id"] for s in spans]
    document_id = spans[0].get("document_id", "") if spans else ""
    page_number = spans[0].get("page_number", 0) if spans else layout.get("page_number", 0)

    top_ids = list(layout.get("top_region_span_ids") or [])
    bottom_ids = list(layout.get("bottom_region_span_ids") or [])
    full_ids = list(layout.get("full_width_span_ids") or [])
    ambig_ids = list(layout.get("ambiguous_span_ids") or [])
    column_groups = list(layout.get("column_groups") or [])

    # column membership from column groups (authoritative after P5 merge)
    col_of: Dict[str, str] = {}
    col_members: Dict[str, List[str]] = {}
    for g in column_groups:
        members = [sid for sid in g.get("member_span_ids", []) if sid in span_by_id]
        col_members[g["column_group_id"]] = members
        for sid in members:
            col_of[sid] = g["column_group_id"]

    assigned = set(top_ids) | set(bottom_ids) | set(full_ids) | set(ambig_ids) | set(col_of.keys())
    orphans = [sid for sid in all_span_ids if sid not in assigned]
    if orphans:
        ambig_ids = ambig_ids + orphans

    page_conf = page_confidence or layout.get("confidence", CONFIDENCE_MEDIUM)
    regions: List[Dict[str, Any]] = []

    # ── 1. PAGE_TOP_REGION ──
    if top_ids:
        tids = [sid for sid in top_ids if sid in span_by_id]
        r = _make_region(document_id, page_number, REGION_TYPE_PAGE_TOP, tids,
                         [span_by_id[s] for s in tids], cfg, METHOD_TOP_BAND,
                         {"full_width_band": "top"},
                         [{"rule": RULE_TOP_BAND,
                           "facts": {"span_count": len(tids),
                                     "inherited_from_p5": "top_region_span_ids"}}],
                         page_conf)
        regions.append(r.to_dict())

    # ── 2. COLUMN_REGION + local regions ──
    col_groups_sorted = sorted(column_groups, key=lambda g: g.get("center_x", 0.0))
    for g in col_groups_sorted:
        members = [sid for sid in g.get("member_span_ids", []) if sid in span_by_id]
        if not members:
            continue
        col_region = _make_region(
            document_id, page_number, REGION_TYPE_COLUMN, members,
            [span_by_id[s] for s in members], cfg, METHOD_COLUMN_GROUP,
            {"column_group_id": g.get("column_group_id"),
             "column_center_x": g.get("center_x"),
             "column_x_min": g.get("x_min"),
             "column_x_max": g.get("x_max")},
            [{"rule": RULE_COLUMN_GROUP,
              "facts": {"span_count": len(members),
                        "column_group_id": g.get("column_group_id"),
                        "column_center_x": g.get("center_x"),
                        "inherited_from_p5": "column_groups.member_span_ids"}}],
            _min_conf(page_conf, g.get("confidence", page_conf)))
        regions.append(col_region.to_dict())

        # local density clustering within this column
        member_spans = [span_by_id[s] for s in members]
        blocks, boundary_gaps = _cluster_by_vertical_contiguity(member_spans, span_order, cfg)
        for bi, block in enumerate(blocks):
            if not block:
                continue
            btype = REGION_TYPE_DENSE if len(block) >= cfg.min_dense_span_count else REGION_TYPE_SPARSE
            method = METHOD_DENSITY_CLUSTER_DENSE if btype == REGION_TYPE_DENSE else METHOD_DENSITY_CLUSTER_SPARSE
            rule = RULE_DENSE_CLUSTER if btype == REGION_TYPE_DENSE else RULE_SPARSE_CLUSTER
            # isolation = min(leading gap, trailing gap) to adjacent blocks
            lead = boundary_gaps[bi] if bi < len(boundary_gaps) else None
            trail = boundary_gaps[bi + 1] if bi + 1 < len(boundary_gaps) else None
            iso_candidates = [x for x in (lead, trail) if x is not None]
            isolation = min(iso_candidates) if iso_candidates else None
            conf = _min_conf(page_conf, _local_confidence(block, btype, isolation, cfg))
            block_ids = [s["span_id"] for s in block]
            local = _make_region(
                document_id, page_number, btype, block_ids, block, cfg, method,
                {"parent_column_group_id": g.get("column_group_id"),
                 "block_index_in_column": bi,
                 "leading_gap": lead, "trailing_gap": trail},
                [{"rule": rule,
                  "facts": {"span_count": len(block_ids),
                            "parent_column_group_id": g.get("column_group_id"),
                            "dense_gap_threshold": cfg.dense_gap_threshold,
                            "min_dense_span_count": cfg.min_dense_span_count,
                            "leading_gap": lead, "trailing_gap": trail}}],
                conf, parent_region_id=col_region.region_id)
            regions.append(local.to_dict())

    # ── 3. FULL_WIDTH_REGION ──
    if full_ids:
        fids = [sid for sid in full_ids if sid in span_by_id]
        r = _make_region(document_id, page_number, REGION_TYPE_FULL_WIDTH, fids,
                         [span_by_id[s] for s in fids], cfg, METHOD_FULL_WIDTH,
                         {"full_width_band": "middle"},
                         [{"rule": RULE_FULL_WIDTH,
                           "facts": {"span_count": len(fids),
                                     "inherited_from_p5": "full_width_span_ids"}}],
                         page_conf)
        regions.append(r.to_dict())

    # ── 4. PAGE_BOTTOM_REGION ──
    if bottom_ids:
        bids = [sid for sid in bottom_ids if sid in span_by_id]
        r = _make_region(document_id, page_number, REGION_TYPE_PAGE_BOTTOM, bids,
                         [span_by_id[s] for s in bids], cfg, METHOD_BOTTOM_BAND,
                         {"full_width_band": "bottom"},
                         [{"rule": RULE_BOTTOM_BAND,
                           "facts": {"span_count": len(bids),
                                     "inherited_from_p5": "bottom_region_span_ids"}}],
                         page_conf)
        regions.append(r.to_dict())

    # ── 5. UNKNOWN_REGION ──
    if ambig_ids:
        aids = sorted({sid for sid in ambig_ids if sid in span_by_id})
        if aids:
            r = _make_region(document_id, page_number, REGION_TYPE_UNKNOWN, aids,
                             [span_by_id[s] for s in aids], cfg, METHOD_UNASSIGNABLE,
                             {"reason": "ambiguous column membership or unassigned"},
                             [{"rule": RULE_UNASSIGNABLE,
                               "facts": {"span_count": len(aids),
                                         "reason": "no reliable geometric assignment"}}],
                             CONFIDENCE_LOW)
            regions.append(r.to_dict())

    return PageRegionSet(
        page_number=page_number,
        page_width=round(page_width, 2),
        page_height=round(page_height, 2),
        coord_origin=COORD_ORIGIN_PDF_TOP_LEFT,
        regions=regions,
        region_count=len(regions),
        orphan_span_ids=sorted(orphans),
        provenance={"config_version": cfg.construction_version,
                    "source_p5_confidence": page_conf,
                    "column_count": layout.get("column_count")},
    )


def verify_region_coverage(page_regions: PageRegionSet,
                           all_span_ids: List[str]) -> Dict[str, Any]:
    """Validate region coverage at the LEAF level (no double-count across
    hierarchy). A leaf region = a region that is NOT anyone's parent."""
    region_by_id = {r["region_id"]: r for r in page_regions.regions}
    parent_ids = {r.get("parent_region_id") for r in page_regions.regions
                  if r.get("parent_region_id")}
    leaf_regions = [r for r in page_regions.regions if r["region_id"] not in parent_ids]

    leaf_span_counter: Dict[str, int] = {}
    for r in leaf_regions:
        for sid in r["span_ids"]:
            leaf_span_counter[sid] = leaf_span_counter.get(sid, 0) + 1

    assigned = set(leaf_span_counter)
    given = set(all_span_ids)
    orphans = [sid for sid in all_span_ids if sid not in assigned]
    dups = [sid for sid, c in leaf_span_counter.items() if c > 1]

    # hierarchy validity: every parent's span_ids == union of its children's span_ids
    children_of: Dict[str, List[str]] = {}
    for r in page_regions.regions:
        if r.get("parent_region_id"):
            children_of.setdefault(r["parent_region_id"], []).extend(r["span_ids"])
    hierarchy_ok = True
    for r in page_regions.regions:
        kids = children_of.get(r["region_id"])
        if kids is not None:
            if sorted(set(kids)) != sorted(r["span_ids"]):
                hierarchy_ok = False

    return {
        "total_spans": len(given),
        "total_regions": len(page_regions.regions),
        "leaf_regions": len(leaf_regions),
        "span_assignment_count": len(assigned),
        "orphan_span_count": len(orphans),
        "orphan_ids": orphans[:10],
        "duplicate_span_assignment_count": len(dups),
        "duplicate_ids": dups[:10],
        "nested_region_count": len(parent_ids),
        "hierarchy_valid": hierarchy_ok,
        "coverage": round(len(assigned & given) / len(given), 4) if given else 0.0,
        "pass": len(orphans) == 0 and len(dups) == 0 and hierarchy_ok,
    }


__all__ = ["compute_page_regions", "verify_region_coverage"]
