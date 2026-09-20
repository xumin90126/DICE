"""
P5 Reading Order Engine — geometric reading-order construction.

Algorithm per page:
  1. Build PageColumnLayout (column groups + top/bottom/full-width regions).
  2. Order spans:
     - TOP_PAGE_REGION spans (full-width, top) first, top→bottom
     - COLUMN_REGION spans: per column group left→right, each top→bottom
     - FULL_WIDTH_REGION (middle) — inserted in column order by y
     - BOTTOM_PAGE_REGION last, top→bottom
     - AMBIGUOUS spans: appended with LOW confidence, reason AMBIGUOUS
  3. Produce ReadingOrderObservation per span + pairwise decision traces.

No semantic classification. Deterministic. Reverse-traceable to span_id.
"""
from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Optional, Tuple

from .reading_order_config import (
    ReadingOrderConfig, DEFAULT_CONFIG,
    ORDER_SAME_COLUMN_VERTICAL, ORDER_COLUMN_GROUP_SEQUENCE,
    ORDER_TOP_REGION_BEFORE_COLUMNS, ORDER_BOTTOM_REGION_AFTER_COLUMNS,
    ORDER_SINGLE_COLUMN_TOP_DOWN, ORDER_PAGE_BOUNDARY, ORDER_AMBIGUOUS,
    ORDER_SINGLE_SPAN,
    COLUMN_CONFIDENCE_HIGH, COLUMN_CONFIDENCE_MEDIUM, COLUMN_CONFIDENCE_LOW,
    COLUMN_CONFIDENCE_UNKNOWN,
    PAGE_REGION_TOP, PAGE_REGION_BOTTOM, PAGE_REGION_COLUMN,
    PAGE_REGION_FULL_WIDTH, PAGE_REGION_UNKNOWN,
)
from .reading_order_observation import (
    ReadingOrderObservation, ReadingOrderDecisionTrace, PageReadingOrder, PageColumnLayout,
)
from .column_geometry import build_page_layout


def _cy(s): return (s["bbox"][1] + s["bbox"][3]) / 2.0
def _cx(s): return (s["bbox"][0] + s["bbox"][2]) / 2.0
def _w(s):  return s["bbox"][2] - s["bbox"][0]
def _h(s):  return s["bbox"][3] - s["bbox"][1]


def compute_page_reading_order(spans: List[Dict[str, Any]],
                               page_width: float, page_height: float,
                               cfg: ReadingOrderConfig = DEFAULT_CONFIG
                               ) -> Tuple[PageReadingOrder, PageColumnLayout]:
    """Compute reading order for one page's spans."""
    if not spans:
        empty = PageReadingOrder(page_number=0, ordered_span_ids=[], observations=[],
                                 decision_traces=[], confidence=COLUMN_CONFIDENCE_UNKNOWN)
        return empty, PageColumnLayout(
            page_number=0, column_groups=[], column_count=0,
            page_width=page_width, page_height=page_height,
            top_region_span_ids=[], bottom_region_span_ids=[],
            full_width_span_ids=[], column_region_span_ids=[], ambiguous_span_ids=[],
            confidence=COLUMN_CONFIDENCE_UNKNOWN, x_projection={})

    layout = build_page_layout(spans, page_width, page_height, cfg)

    # Build span lookup
    span_by_id = {s["span_id"]: s for s in spans}

    # region buckets
    top_ids = layout.top_region_span_ids
    bot_ids = layout.bottom_region_span_ids
    col_ids = set(layout.column_region_span_ids)
    full_ids = layout.full_width_span_ids or []
    ambig_ids = layout.ambiguous_span_ids

    # column group membership
    col_of = {}
    for g in layout.column_groups:
        for sid in g["member_span_ids"]:
            col_of[sid] = g["column_group_id"]

    # ── Build ordered sequence ──
    ordered: List[str] = []
    order_reasons: Dict[str, str] = {}

    # 1. Top region (top→bottom, left→right within line)
    top_sorted = sorted(top_ids, key=lambda sid: (_cy(span_by_id[sid]), _cx(span_by_id[sid])))
    for sid in top_sorted:
        ordered.append(sid)
        order_reasons[sid] = ORDER_TOP_REGION_BEFORE_COLUMNS

    # 2. Column regions: left→right by group center_x, each top→bottom (then left→right)
    col_groups_sorted = sorted(layout.column_groups, key=lambda g: g["center_x"])
    prev_col_id = None
    for g in col_groups_sorted:
        members = [sid for sid in g["member_span_ids"] if sid in col_ids]
        members_sorted = sorted(members, key=lambda sid: (_cy(span_by_id[sid]), _cx(span_by_id[sid])))
        for sid in members_sorted:
            ordered.append(sid)
            if prev_col_id is not None and g["column_group_id"] != prev_col_id:
                order_reasons[sid] = ORDER_COLUMN_GROUP_SEQUENCE
            else:
                order_reasons[sid] = ORDER_SAME_COLUMN_VERTICAL
        prev_col_id = g["column_group_id"]

    # 3. Full-width middle spans (insert by y among column flow)
    full_sorted = sorted(full_ids, key=lambda sid: (_cy(span_by_id[sid]), _cx(span_by_id[sid])))
    # Insert full-width spans at correct y position: rebuild ordered list
    # Simpler: append full-width spans after columns if they are mid-page;
    # but for correctness, merge by y into the column sequence region.
    # We do a stable merge: treat full-width as their own implicit group by y.
    if full_sorted:
        merged = []
        col_part = ordered[len(top_sorted):]  # column part
        # interleave by y
        i = 0
        for fid in full_sorted:
            fy = _cy(span_by_id[fid])
            while i < len(col_part) and _cy(span_by_id[col_part[i]]) < fy:
                merged.append(col_part[i]); i += 1
            merged.append(fid)
            order_reasons[fid] = ORDER_SINGLE_COLUMN_TOP_DOWN
        merged.extend(col_part[i:])
        ordered = ordered[:len(top_sorted)] + merged

    # 4. Bottom region (top→bottom, left→right)
    bot_sorted = sorted(bot_ids, key=lambda sid: (_cy(span_by_id[sid]), _cx(span_by_id[sid])))
    for sid in bot_sorted:
        ordered.append(sid)
        order_reasons[sid] = ORDER_BOTTOM_REGION_AFTER_COLUMNS

    # 5. Ambiguous spans: append, low confidence
    for sid in ambig_ids:
        if sid not in ordered:
            ordered.append(sid)
            order_reasons[sid] = ORDER_AMBIGUOUS

    # Single-span page
    if len(ordered) == 1:
        order_reasons[ordered[0]] = ORDER_SINGLE_SPAN

    # Deduplicate (preserve first occurrence), ensure no span lost
    seen = set()
    deduped = []
    for sid in ordered:
        if sid not in seen:
            seen.add(sid); deduped.append(sid)
    # add any span not yet placed (defensive — should not happen)
    for s in spans:
        if s["span_id"] not in seen:
            deduped.append(s["span_id"])
            order_reasons[s["span_id"]] = ORDER_AMBIGUOUS
    ordered = deduped

    # ── Build observations + traces ──
    observations = []
    for idx, sid in enumerate(ordered):
        s = span_by_id[sid]
        prev_sid = ordered[idx - 1] if idx > 0 else None
        next_sid = ordered[idx + 1] if idx < len(ordered) - 1 else None
        cgid = col_of.get(sid)
        region = _region_of(sid, layout)
        conf = _span_confidence(sid, layout, cfg)
        obs = ReadingOrderObservation(
            observation_id=hashlib.sha1(f"ro|{sid}".encode()).hexdigest()[:16],
            document_id=s.get("document_id", ""),
            page_number=s.get("page_number", 0),
            span_id=sid,
            source_span_index=idx,
            column_group_id=cgid,
            page_region=region,
            reading_order_index=idx,
            previous_span_id=prev_sid,
            next_span_id=next_sid,
            bbox=s["bbox"],
            center_x=round(_cx(s), 2),
            center_y=round(_cy(s), 2),
            width=round(_w(s), 2),
            height=round(_h(s), 2),
            order_reason=order_reasons.get(sid, ORDER_AMBIGUOUS),
            order_facts=_order_facts(s, prev_sid, next_sid, span_by_id, layout, cfg),
            horizontal_relation=_hrel(s, prev_sid, span_by_id) if prev_sid else None,
            vertical_relation=_vrel(s, prev_sid, span_by_id) if prev_sid else None,
            column_relation=_crel(sid, prev_sid, col_of) if prev_sid else None,
            confidence=conf,
            provenance={"source_span_id": sid,
                        "source_observation_ids": s.get("source_observation_ids", []),
                        "source_layers": s.get("source_observation_types", [])},
        )
        observations.append(obs.to_dict())

    # Pairwise traces between consecutive
    traces = []
    ambiguous_decisions = 0
    for i in range(len(ordered) - 1):
        a, b = span_by_id[ordered[i]], span_by_id[ordered[i + 1]]
        same_col = col_of.get(ordered[i]) is not None and col_of.get(ordered[i]) == col_of.get(ordered[i + 1])
        a_above_b = _cy(a) < _cy(b)
        vgap = round(abs(_cy(b) - _cy(a)), 2)
        hov = round(max(0.0, min(a["bbox"][2], b["bbox"][2]) - max(a["bbox"][0], b["bbox"][0])), 2)
        # overlap ratio (intersection / min area) for ambiguity
        ix = max(0.0, min(a["bbox"][2], b["bbox"][2]) - max(a["bbox"][0], b["bbox"][0]))
        iy = max(0.0, min(a["bbox"][3], b["bbox"][3]) - max(a["bbox"][1], b["bbox"][1]))
        inter = ix * iy
        area_a = max(1e-6, _w(a) * _h(a)); area_b = max(1e-6, _w(b) * _h(b))
        overlap_ratio = inter / min(area_a, area_b)
        overlapping = overlap_ratio >= cfg.overlap_ambiguity_threshold

        decision = "A_BEFORE_B" if (a_above_b or (not same_col and _cx(a) < _cx(b))) else "AMBIGUOUS"
        reason = order_reasons.get(ordered[i + 1], ORDER_AMBIGUOUS)
        if overlapping:
            decision = "AMBIGUOUS"
            reason = ORDER_AMBIGUOUS
            ambiguous_decisions += 1
        traces.append(ReadingOrderDecisionTrace(
            span_a_id=ordered[i], span_b_id=ordered[i + 1],
            same_column_group=same_col,
            a_above_b=a_above_b,
            a_center_y=round(_cy(a), 2), b_center_y=round(_cy(b), 2),
            a_center_x=round(_cx(a), 2), b_center_x=round(_cx(b), 2),
            vertical_gap=vgap, horizontal_overlap=hov,
            decision=decision, reason=reason,
            facts_summary={"same_col": same_col, "a_above_b": a_above_b,
                           "overlap_ratio": round(overlap_ratio, 3)},
        ).to_dict())

    page_conf = layout.confidence
    # degrade page confidence if many overlapping (ambiguous) decisions
    n_trace = len(traces)
    if n_trace > 0 and ambiguous_decisions / n_trace >= 0.5:
        page_conf = COLUMN_CONFIDENCE_LOW
    pro = PageReadingOrder(
        page_number=spans[0].get("page_number", 0),
        ordered_span_ids=ordered,
        observations=observations,
        decision_traces=traces,
        confidence=page_conf,
        provenance={"config_version": cfg.construction_version,
                    "column_count": layout.column_count,
                    "ambiguous_decision_ratio": round(ambiguous_decisions / n_trace, 4) if n_trace else 0.0},
    )
    return pro, layout


def _region_of(sid, layout) -> str:
    if sid in layout.top_region_span_ids: return PAGE_REGION_TOP
    if sid in layout.bottom_region_span_ids: return PAGE_REGION_BOTTOM
    if sid in (layout.full_width_span_ids or []): return PAGE_REGION_FULL_WIDTH
    if sid in layout.column_region_span_ids: return PAGE_REGION_COLUMN
    if sid in layout.ambiguous_span_ids: return PAGE_REGION_UNKNOWN
    return PAGE_REGION_COLUMN


def _span_confidence(sid, layout, cfg) -> str:
    if sid in layout.ambiguous_span_ids: return COLUMN_CONFIDENCE_LOW
    gconf_map = {g["column_group_id"]: g["confidence"] for g in layout.column_groups}
    # find which group
    for g in layout.column_groups:
        if sid in g["member_span_ids"]:
            return g["confidence"]
    if layout.confidence == COLUMN_CONFIDENCE_HIGH: return COLUMN_CONFIDENCE_HIGH
    if layout.confidence == COLUMN_CONFIDENCE_MEDIUM: return COLUMN_CONFIDENCE_MEDIUM
    return COLUMN_CONFIDENCE_MEDIUM


def _order_facts(s, prev_sid, next_sid, span_by_id, layout, cfg) -> Dict[str, Any]:
    facts = {"span_center_y": round(_cy(s), 2), "span_center_x": round(_cx(s), 2)}
    if prev_sid:
        p = span_by_id[prev_sid]
        facts["prev_center_y"] = round(_cy(p), 2)
        facts["prev_center_x"] = round(_cx(p), 2)
        facts["vertical_gap_from_prev"] = round(_cy(s) - _cy(p), 2)
        facts["horizontal_overlap_with_prev"] = round(max(0.0, min(s["bbox"][2], p["bbox"][2]) - max(s["bbox"][0], p["bbox"][0])), 2)
    return facts


def _hrel(s, prev, span_by_id) -> str:
    if prev is None: return "NONE"
    p = span_by_id[prev]
    if _cx(s) < _cx(p) - 5: return "RIGHT_TO_LEFT"
    if _cx(s) > _cx(p) + 5: return "LEFT_TO_RIGHT"
    return "SAME_X"


def _vrel(s, prev, span_by_id) -> str:
    if prev is None: return "NONE"
    p = span_by_id[prev]
    if _cy(s) < _cy(p) - 1: return "ABOVE"
    if _cy(s) > _cy(p) + 1: return "BELOW"
    return "SAME_Y"


def _crel(sid, prev_sid, col_of) -> Optional[str]:
    if prev_sid is None: return None
    a, b = col_of.get(sid), col_of.get(prev_sid)
    if a is None or b is None: return "DIFFERENT_REGION"
    if a == b: return "SAME_COLUMN"
    return "DIFFERENT_COLUMN"


def verify_reading_order_coverage(page_ro: PageReadingOrder,
                                  span_ids: List[str]) -> Dict[str, Any]:
    ordered = set(page_ro.ordered_span_ids)
    given = set(span_ids)
    orphans = given - ordered
    dups = [sid for sid in page_ro.ordered_span_ids if page_ro.ordered_span_ids.count(sid) > 1]
    return {
        "total_spans": len(given),
        "ordered": len(ordered),
        "orphan_count": len(orphans),
        "orphan_ids": list(orphans)[:10],
        "duplicate_count": len(set(dups)),
        "coverage": round(len(ordered & given) / len(given), 4) if given else 0.0,
        "pass": len(orphans) == 0 and len(dups) == 0,
    }


__all__ = ["compute_page_reading_order", "verify_reading_order_coverage"]
