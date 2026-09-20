"""
P5 Column Geometry — pure geometric column detection via vertical projection.

Detects column groups from the vertical coverage profile of span BBOXES.
A column gap = a vertical white stripe (x-range where NO span bbox overlaps,
i.e. coverage == 0) wider than column_gap_threshold, spanning the text height.

This is robust to span width variation (full-width titles don't split columns
because their bbox fills the gap; narrow table cells don't create fake columns
because they leave no fully-empty vertical stripe).

Supports 1/2/3+/uneven/asymmetric columns. Outputs LOW_CONFIDENCE/UNKNOWN when
geometry is unclear rather than forcing a column count.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .reading_order_config import (
    ReadingOrderConfig, DEFAULT_CONFIG,
    COLUMN_CONFIDENCE_HIGH, COLUMN_CONFIDENCE_MEDIUM, COLUMN_CONFIDENCE_LOW,
    COLUMN_CONFIDENCE_UNKNOWN,
    PAGE_REGION_TOP, PAGE_REGION_BOTTOM, PAGE_REGION_COLUMN,
    PAGE_REGION_FULL_WIDTH,
)
from .reading_order_observation import ColumnGroup, PageColumnLayout


def _cx(s): return (s["bbox"][0] + s["bbox"][2]) / 2.0
def _cy(s): return (s["bbox"][1] + s["bbox"][3]) / 2.0
def _w(s):  return s["bbox"][2] - s["bbox"][0]
def _h(s):  return s["bbox"][3] - s["bbox"][1]


def _column_body_spans(spans: List[Dict[str, Any]], page_width: float,
                       cfg: ReadingOrderConfig) -> List[Dict[str, Any]]:
    """Exclude full-width spans (headers/titles/footers) from column detection.

    A full-width span spans all columns, so its bbox fills the column gap and
    would hide the white-stripe boundary. Column structure is detected from
    column-body spans only.
    """
    full_w = page_width * cfg.full_width_ratio
    return [s for s in spans if _w(s) < full_w]


def compute_x_projection(spans: List[Dict[str, Any]],
                         page_width: float,
                         cfg: ReadingOrderConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Vertical coverage profile: for each x-bin, count column-body spans whose
    bbox overlaps that bin (full-width spans excluded — they span all columns)."""
    if page_width <= 0 or not spans:
        return {"bins": [], "bin_size": cfg.column_x_bin_size, "page_width": page_width,
                "populated_bins": [], "gap_regions": []}
    body = _column_body_spans(spans, page_width, cfg)
    if not body:
        # all spans full-width → single region
        nbins = max(1, int(page_width / cfg.column_x_bin_size) + 1)
        return {"bins": [], "bin_size": cfg.column_x_bin_size, "page_width": page_width,
                "populated_bins": [], "gap_regions": []}
    nbins = max(1, int(page_width / cfg.column_x_bin_size) + 1)
    counts = [0] * nbins
    for s in body:
        x0, x1 = s["bbox"][0], s["bbox"][2]
        bi0 = max(0, int(x0 / cfg.column_x_bin_size))
        bi1 = min(nbins - 1, int(x1 / cfg.column_x_bin_size))
        for bi in range(bi0, bi1 + 1):
            counts[bi] += 1
    bins = [{"index": i, "x_start": round(i * cfg.column_x_bin_size, 1),
             "count": counts[i]} for i in range(nbins)]
    # populated bins = coverage > 0 (any span overlaps)
    populated = [i for i, c in enumerate(counts) if c > 0]

    # gap regions: contiguous runs of ZERO-coverage bins between populated bins
    gaps = []
    if populated:
        for i in range(len(populated) - 1):
            a, b = populated[i], populated[i + 1]
            if b - a > 1:
                gap_start = (a + 1) * cfg.column_x_bin_size
                gap_end = b * cfg.column_x_bin_size
                gap_width = gap_end - gap_start
                if gap_width >= cfg.column_gap_threshold:
                    gaps.append({"from_bin": a, "to_bin": b,
                                 "x_start": round(gap_start, 1),
                                 "x_end": round(gap_end, 1),
                                 "width": round(gap_width, 1)})
    return {"bins": bins, "bin_size": cfg.column_x_bin_size,
            "page_width": page_width, "populated_bins": populated,
            "gap_regions": gaps}


def detect_column_groups(spans: List[Dict[str, Any]],
                         page_width: float,
                         page_height: float,
                         cfg: ReadingOrderConfig = DEFAULT_CONFIG) -> Tuple[List[ColumnGroup], Dict[str, Any]]:
    """Detect geometric column groups from vertical white-stripe gaps.

    Returns (column_groups, x_projection). column_groups ordered left→right.
    A column group is a contiguous x-region of span bboxes separated from the
    next region by a zero-coverage vertical stripe >= column_gap_threshold.
    """
    proj = compute_x_projection(spans, page_width, cfg)
    gaps = proj["gap_regions"]
    body = _column_body_spans(spans, page_width, cfg)

    if not gaps:
        # No clean vertical stripe → single column (whole page)
        groups = [_make_group(body, 0, 0.0, page_width, cfg)]
        if groups and groups[0].span_count == 0:
            groups = []
        return groups, proj

    # Build x-regions separated by gaps
    regions = []
    first_pop = proj["populated_bins"][0]
    x_lo = first_pop * cfg.column_x_bin_size
    for g in gaps:
        regions.append((x_lo, g["x_start"]))
        x_lo = g["x_end"]
    regions.append((x_lo, (proj["populated_bins"][-1] + 1) * cfg.column_x_bin_size))

    groups: List[ColumnGroup] = []
    for gi, (x_lo, x_hi) in enumerate(regions):
        # assign column-body spans whose bbox CENTER falls in region
        members = [s for s in body if x_lo <= _cx(s) <= x_hi]
        g = _make_group(members, gi, x_lo, x_hi, cfg)
        if g is not None:
            groups.append(g)

    groups.sort(key=lambda g: g.center_x)

    # Merge tiny groups (margin elements like page numbers) into nearest
    # sufficiently-populated group. A group with fewer than min_column_span_count
    # spans is not a real column.
    large = [g for g in groups if g.span_count >= cfg.min_column_span_count]
    tiny = [g for g in groups if g.span_count < cfg.min_column_span_count]
    if large:
        for tg in tiny:
            nearest = min(large, key=lambda m: abs(m.center_x - tg.center_x))
            nearest.member_span_ids = nearest.member_span_ids + tg.member_span_ids
            nearest.span_count = len(nearest.member_span_ids)
            members = [s for s in spans if s["span_id"] in nearest.member_span_ids]
            if members:
                nearest.center_x = round(sum(_cx(s) for s in members) / len(members), 2)
                nearest.x_min = round(min(s["bbox"][0] for s in members), 2)
                nearest.x_max = round(max(s["bbox"][2] for s in members), 2)
        groups = large
    else:
        # no large groups: keep all tiny groups as-is (degenerate case)
        groups = groups
    groups.sort(key=lambda g: g.center_x)
    for i, g in enumerate(groups):
        g.column_group_id = f"col_{i}"
    return groups, proj


def _make_group(members, gi, x_lo, x_hi, cfg):
    if not members:
        return None
    cxs = [_cx(s) for s in members]
    return ColumnGroup(
        column_group_id=f"col_{gi}",
        page_number=members[0].get("page_number", 0),
        member_span_ids=[s["span_id"] for s in members],
        center_x=round(sum(cxs) / len(cxs), 2),
        x_min=round(min(s["bbox"][0] for s in members), 2),
        x_max=round(max(s["bbox"][2] for s in members), 2),
        span_count=len(members),
        confidence=COLUMN_CONFIDENCE_HIGH,
        provenance={"region": (round(x_lo, 1), round(x_hi, 1))},
    )


def classify_page_regions(spans: List[Dict[str, Any]],
                          page_width: float, page_height: float,
                          groups: List[ColumnGroup],
                          cfg: ReadingOrderConfig = DEFAULT_CONFIG) -> Dict[str, List[str]]:
    """Classify spans into top/bottom/full-width/column regions (geometric only)."""
    top_ids, bottom_ids, column_ids, full_ids, ambig_ids = [], [], [], [], []
    top_y = page_height * cfg.top_region_ratio
    bottom_y = page_height * (1.0 - cfg.bottom_region_ratio)
    full_w = page_width * cfg.full_width_ratio

    col_ranges = [(g.x_min, g.x_max) for g in groups]

    for s in spans:
        cy = _cy(s)
        w = _w(s)
        sid = s["span_id"]
        # full-width spans (spans whole columns)
        if w >= full_w:
            if cy <= top_y:
                top_ids.append(sid); continue
            if cy >= bottom_y:
                bottom_ids.append(sid); continue
            full_ids.append(sid); continue
        # column membership by center_x within a group's x-range
        if col_ranges:
            assigned = False
            for g in groups:
                if g.x_min - cfg.column_x_tolerance <= _cx(s) <= g.x_max + cfg.column_x_tolerance:
                    column_ids.append(sid); assigned = True; break
            if assigned:
                continue
            # not in any column group → ambiguous (but if only 1 group, still assign)
            if len(groups) == 1:
                column_ids.append(sid); continue
            ambig_ids.append(sid); continue
        # no groups → single column
        column_ids.append(sid)
    return {
        PAGE_REGION_TOP: top_ids,
        PAGE_REGION_BOTTOM: bottom_ids,
        PAGE_REGION_COLUMN: column_ids,
        PAGE_REGION_FULL_WIDTH: full_ids,
        "AMBIGUOUS": ambig_ids,
    }


def _y_overlap(a, b) -> float:
    return max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def detect_row_alignment(spans: List[Dict[str, Any]],
                         groups: List[ColumnGroup],
                         cfg: ReadingOrderConfig = DEFAULT_CONFIG) -> float:
    """Measure row-alignment between adjacent column groups.

    Returns ratio in [0,1]: fraction of spans in the left column of each
    adjacent pair that have a y-overlapping span in the right column.
    High ratio → row-aligned layout (TOC / key-value / table), where
    column-major reading order is AMBIGUOUS.
    """
    if len(groups) < 2:
        return 0.0
    by_id = {s["span_id"]: s for s in spans}
    ratios = []
    for i in range(len(groups) - 1):
        left_ids = groups[i].member_span_ids
        right_ids = set(groups[i + 1].member_span_ids)
        if not left_ids:
            continue
        left_spans = [by_id[sid] for sid in left_ids if sid in by_id]
        right_spans = [by_id[sid] for sid in right_ids if sid in by_id]
        if not left_spans or not right_spans:
            continue
        overlap_count = 0
        for ls in left_spans:
            lb = ls["bbox"]
            if any(_y_overlap(lb, rs["bbox"]) > 0 for rs in right_spans):
                overlap_count += 1
        ratios.append(overlap_count / len(left_spans))
    return round(sum(ratios) / len(ratios), 4) if ratios else 0.0


def build_page_layout(spans: List[Dict[str, Any]],
                      page_width: float, page_height: float,
                      cfg: ReadingOrderConfig = DEFAULT_CONFIG) -> PageColumnLayout:
    """Build full PageColumnLayout for one page."""
    groups, proj = detect_column_groups(spans, page_width, page_height, cfg)
    regions = classify_page_regions(spans, page_width, page_height, groups, cfg)

    # confidence
    ncols = len(groups)
    if ncols >= 2:
        # multi-column confidence based on gap clarity
        gap_widths = [g["width"] for g in proj.get("gap_regions", [])]
        clear = all(w >= cfg.column_gap_threshold for w in gap_widths) if gap_widths else False
        page_conf = COLUMN_CONFIDENCE_HIGH if clear else COLUMN_CONFIDENCE_MEDIUM
    elif ncols == 1:
        # single column: HIGH if most spans are in column region and not ambiguous
        total = len(spans)
        col_frac = len(regions[PAGE_REGION_COLUMN]) / total if total else 0
        page_conf = COLUMN_CONFIDENCE_HIGH if col_frac >= 0.5 else COLUMN_CONFIDENCE_MEDIUM
    else:
        page_conf = COLUMN_CONFIDENCE_UNKNOWN

    if regions["AMBIGUOUS"]:
        if len(regions["AMBIGUOUS"]) > len(spans) * 0.3:
            page_conf = COLUMN_CONFIDENCE_LOW

    # row_alignment_ratio is recorded as a FACT (not used to force ambiguity —
    # column-major reading is the deterministic default per task §9/§11).
    row_ratio = detect_row_alignment(spans, groups, cfg) if groups else 0.0

    return PageColumnLayout(
        page_number=spans[0].get("page_number", 0) if spans else 0,
        column_groups=[g.to_dict() for g in groups],
        column_count=ncols,
        page_width=page_width,
        page_height=page_height,
        top_region_span_ids=regions[PAGE_REGION_TOP],
        bottom_region_span_ids=regions[PAGE_REGION_BOTTOM],
        full_width_span_ids=regions[PAGE_REGION_FULL_WIDTH],
        column_region_span_ids=regions[PAGE_REGION_COLUMN],
        ambiguous_span_ids=regions["AMBIGUOUS"],
        confidence=page_conf,
        x_projection=proj,
        provenance={"config_version": cfg.construction_version,
                    "row_alignment_ratio": row_ratio},
    )


__all__ = ["detect_column_groups", "compute_x_projection",
           "classify_page_regions", "build_page_layout"]
