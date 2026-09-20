"""
P7.1 StructureHypothesis engine.

Deterministically constructs Structural Relations (Layer B) + Structure
Hypotheses (Layer C) from P1-P6 facts. READ-ONLY consumer: no PDF re-parsing,
no span/region/reading-order reconstruction, no semantic classification.

Implements ONLY the 7 approved candidate types. Every hypothesis is a
CANDIDATE (status PROPOSED), never a final structure, never Evidence.

Architecture gate (enforced by construction):
    Multiple independent signals + Structural Relation + deterministic rule
        -> StructureHypothesis
    NO single-signal shortcut (bold -> heading, top_region -> header, ...).
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from .structure_config import (
    StructureConfig, DEFAULT_CONFIG,
    HYP_HEADING, HYP_PARAGRAPH, HYP_SECTION, HYP_LIST,
    HYP_HEADER, HYP_FOOTER, HYP_MULTICOL,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW,
    CONFIDENCE_UNKNOWN, CONFIDENCE_AMBIGUOUS,
    METHOD_HEADING_MULTI_SIGNAL, METHOD_PARAGRAPH_VERTICAL_GROUPING,
    METHOD_SECTION_HEADING_SPAN, METHOD_LIST_ALIGNMENT,
    METHOD_HEADER_REPEAT, METHOD_FOOTER_REPEAT, METHOD_MULTICOL_CONTINUATION,
    REL_STYLE_CONTRAST, REL_VERTICAL_SEPARATION, REL_ADJACENT_TO,
    REL_LEFT_ALIGNED_WITH, REL_PRECEDES, REL_SHARES_REGION,
    REL_CONTINUES_FROM, REL_REPEATS_ACROSS_PAGES,
)
from .structure_relation import StructuralRelation, min_confidence, _relation_id
from .structure_hypothesis import (
    StructureHypothesis, PageStructureBundle, _hypothesis_id,
)


# ── small helpers ────────────────────────────────────────────────────────────

def _style_parts(sig: Optional[str]) -> Optional[Dict[str, Any]]:
    """Parse a P4 dominant_style_signature 'family|size|b|i|u|sup|sub'."""
    if not sig:
        return None
    p = sig.split("|")
    if len(p) < 7:
        return None
    size = None
    try:
        size = float(p[1])
    except (ValueError, TypeError):
        size = None
    return {
        "family": p[0],
        "size": size,
        "bold": True if p[2] == "1" else (False if p[2] == "0" else None),
        "italic": True if p[3] == "1" else (False if p[3] == "0" else None),
        "sig": sig,
    }


def _median(vals: List[float]) -> Optional[float]:
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _bbox_union(span_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    x0 = min(s["bbox"][0] for s in span_list)
    y0 = min(s["bbox"][1] for s in span_list)
    x1 = max(s["bbox"][2] for s in span_list)
    y1 = max(s["bbox"][3] for s in span_list)
    return {
        "bbox": [x0, y0, x1, y1],
        "width": x1 - x0,
        "height": y1 - y0,
        "center_x": (x0 + x1) / 2.0,
        "center_y": (y0 + y1) / 2.0,
    }


def _x_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return max(a["bbox"][0], b["bbox"][0]) < min(a["bbox"][2], b["bbox"][2])


def _span_upstream_conf(sid: str, ro_by_span: Dict, region_by_span: Dict) -> str:
    confs = []
    ro = ro_by_span.get(sid)
    if ro and ro.get("confidence"):
        confs.append(ro["confidence"])
    for r in region_by_span.get(sid, []):
        if r.get("confidence"):
            confs.append(r["confidence"])
    return min_confidence(*confs) if confs else CONFIDENCE_UNKNOWN


def _make_fact_ref(ref_type: str, ref_id: str, fact: str) -> Dict[str, Any]:
    return {"ref_type": ref_type, "ref_id": ref_id, "fact": fact}


# ── Heading ──────────────────────────────────────────────────────────────────

def _detect_headings(spans, ro_by_span, region_by_span, layout, cfg,
                     page_w, page_h, doc_id, pno, rels) -> List[StructureHypothesis]:
    """Heading candidate via >= heading_min_signals INDEPENDENT signals."""
    sizes = [sp["size"] for sp in (_style_parts(s.get("dominant_style_signature")) for s in spans)
             if sp and sp["size"] is not None]
    median_size = _median(sizes)
    bolds = [sp["bold"] for sp in (_style_parts(s.get("dominant_style_signature")) for s in spans)
             if sp is not None and sp["bold"] is not None]
    bold_majority = (sum(1 for b in bolds if b) > len(bolds) / 2) if bolds else False

    # column reference width per column_group_id
    col_ref_width = defaultdict(float)
    for s in spans:
        ro = ro_by_span.get(s["span_id"], {})
        cg = ro.get("column_group_id")
        col_ref_width[cg] = max(col_ref_width[cg], s["bbox"][2] - s["bbox"][0])

    # reading index within column group
    col_pos = {}  # sid -> position index within its column group (sorted by reading order)
    col_members = defaultdict(list)
    for s in spans:
        ro = ro_by_span.get(s["span_id"], {})
        col_members[ro.get("column_group_id")].append(s)
    for cg, members in col_members.items():
        members_sorted = sorted(members, key=lambda s: ro_by_span.get(s["span_id"], {}).get("reading_order_index", 0))
        for i, s in enumerate(members_sorted):
            col_pos[s["span_id"]] = i

    out: List[StructureHypothesis] = []
    for s in spans:
        sid = s["span_id"]
        ro = ro_by_span.get(sid, {})
        sp = _style_parts(s.get("dominant_style_signature"))
        width = s["bbox"][2] - s["bbox"][0]
        signals: Dict[str, Dict[str, Any]] = {}

        # signal 1: style contrast (size vs page median OR bold vs page majority)
        if sp is not None:
            size_contrast = (sp["size"] is not None and median_size is not None
                             and sp["size"] >= median_size * cfg.heading_size_ratio)
            bold_contrast = (sp["bold"] is True and not bold_majority)
            if size_contrast or bold_contrast:
                signals["style_contrast"] = {
                    "size": sp["size"], "page_median_size": median_size,
                    "size_contrast": bool(size_contrast),
                    "bold": sp["bold"], "bold_contrast": bool(bold_contrast),
                }

        # signal 2: spatial separation (vertical gap before, within x-overlap)
        prev_id = ro.get("previous_span_id")
        prev = next((x for x in spans if x["span_id"] == prev_id), None) if prev_id else None
        if prev is not None and _x_overlap(prev, s):
            gap = s["bbox"][1] - prev["bbox"][3]
            if gap > cfg.heading_gap_threshold:
                signals["spatial_separation"] = {"gap_before": gap,
                                                 "prev_span_id": prev_id,
                                                 "threshold": cfg.heading_gap_threshold}

        # signal 3: reading position (first in its column group)
        if col_pos.get(sid) == 0 and ro.get("column_group_id") is not None:
            signals["reading_position"] = {"column_group_id": ro.get("column_group_id"),
                                           "position_in_column": 0}

        # signal 4: short line (relative to column reference width)
        cg = ro.get("column_group_id")
        refw = col_ref_width.get(cg) or page_w
        if refw and width <= refw * cfg.heading_short_line_ratio:
            signals["short_line"] = {"width": width, "column_ref_width": refw,
                                     "ratio": cfg.heading_short_line_ratio}

        if len(signals) < cfg.heading_min_signals:
            continue

        # structural confidence from independent-signal count
        if len(signals) >= 4:
            struct_conf = CONFIDENCE_HIGH
        elif len(signals) == 3:
            struct_conf = CONFIDENCE_MEDIUM
        else:
            struct_conf = CONFIDENCE_LOW

        upstream = _span_upstream_conf(sid, ro_by_span, region_by_span)
        conf = min_confidence(upstream, struct_conf)

        # relations
        rel_ids: List[str] = []
        if "style_contrast" in signals:
            r = StructuralRelation(_relation_id(doc_id, pno, REL_STYLE_CONTRAST, sid, "page_baseline"),
                                   doc_id, pno, REL_STYLE_CONTRAST, sid, "page_baseline",
                                   "span", "baseline",
                                   [_make_fact_ref("span", sid, "dominant_style_signature")],
                                   conf, [{"signal": "style_contrast", "facts": signals["style_contrast"]}],
                                   {"coord_origin": cfg.coord_origin})
            rels.append(r.to_dict()); rel_ids.append(r.relation_id)
        if "spatial_separation" in signals:
            r = StructuralRelation(_relation_id(doc_id, pno, REL_VERTICAL_SEPARATION, prev_id, sid),
                                   doc_id, pno, REL_VERTICAL_SEPARATION, prev_id, sid,
                                   "span", "span",
                                   [_make_fact_ref("span", sid, "bbox"),
                                    _make_fact_ref("span", prev_id, "bbox")],
                                   conf, [{"signal": "spatial_separation", "facts": signals["spatial_separation"]}],
                                   {"coord_origin": cfg.coord_origin})
            rels.append(r.to_dict()); rel_ids.append(r.relation_id)

        region_ids = [r["region_id"] for r in region_by_span.get(sid, [])]
        fact_refs = [_make_fact_ref("span", sid, "dominant_style_signature"),
                     _make_fact_ref("span", sid, "bbox")]
        for rid in region_ids:
            fact_refs.append(_make_fact_ref("region", rid, "region_type"))

        trace = [
            {"step": "input", "span_ids": [sid], "region_ids": region_ids},
            {"step": "signals", "collected": list(signals.keys()),
             "count": len(signals), "required": cfg.heading_min_signals,
             "details": signals},
            {"step": "decision", "reason": ">=2 independent signals -> HEADING_CANDIDATE",
             "why_not_final": "structure is a candidate; semantic role deferred to validation"},
            {"step": "confidence", "structural": struct_conf,
             "upstream": upstream, "final": conf,
             "note": "downstream cannot exceed min(upstream, structural)"},
        ]

        h = StructureHypothesis(
            hypothesis_id=_hypothesis_id(doc_id, pno, HYP_HEADING, [sid]),
            document_id=doc_id, page_number=pno, hypothesis_type=HYP_HEADING,
            span_ids=[sid], region_ids=region_ids,
            supporting_relation_ids=rel_ids, supporting_fact_refs=fact_refs,
            geometry=_bbox_union([s]), confidence=conf,
            construction_method=METHOD_HEADING_MULTI_SIGNAL,
            construction_version=cfg.construction_version,
            decision_trace=trace,
            provenance={"source_layers": ["P3_style", "P4_span", "P5_order", "P6_region"],
                        "upstream_confidence": upstream},
            coord_origin=cfg.coord_origin,
        )
        out.append(h)
    return out


# ── Paragraph grouping ───────────────────────────────────────────────────────

def _detect_paragraphs(spans, ro_by_span, region_by_span, layout, cfg,
                       page_w, page_h, doc_id, pno, rels) -> List[StructureHypothesis]:
    """Paragraph-like grouping = reading-order-contiguous span run with small
    vertical gaps, within one column. Reference-only; never merges text (unlike C1)."""
    col_members = defaultdict(list)
    for s in spans:
        ro = ro_by_span.get(s["span_id"], {})
        if ro.get("column_group_id") is not None:
            col_members[ro["column_group_id"]].append(s)

    out: List[StructureHypothesis] = []
    for cg, members in col_members.items():
        members = sorted(members, key=lambda s: ro_by_span.get(s["span_id"], {}).get("reading_order_index", 0))
        if not members:
            continue
        runs: List[List[Dict]] = []
        cur = [members[0]]
        for i in range(1, len(members)):
            prev, s = members[i - 1], members[i]
            gap = s["bbox"][1] - prev["bbox"][3]
            if gap <= cfg.paragraph_gap_threshold:
                cur.append(s)
            else:
                runs.append(cur); cur = [s]
        runs.append(cur)

        for run in runs:
            if len(run) < cfg.paragraph_min_spans:
                continue
            # upstream conf = min over members
            upstream = min_confidence(*[_span_upstream_conf(s["span_id"], ro_by_span, region_by_span)
                                        for s in run])
            # structural: gap uniformity -> HIGH if all gaps well within threshold
            gaps = []
            for i in range(1, len(run)):
                gaps.append(run[i]["bbox"][1] - run[i - 1]["bbox"][3])
            if gaps and max(gaps) <= cfg.paragraph_gap_threshold * 0.5:
                struct_conf = CONFIDENCE_HIGH
            elif gaps and max(gaps) <= cfg.paragraph_gap_threshold:
                struct_conf = CONFIDENCE_MEDIUM
            else:
                struct_conf = CONFIDENCE_LOW
            conf = min_confidence(upstream, struct_conf)

            sids = [s["span_id"] for s in run]
            # adjacency relations
            rel_ids = []
            for a, b in zip(run, run[1:]):
                r = StructuralRelation(_relation_id(doc_id, pno, REL_ADJACENT_TO, a["span_id"], b["span_id"]),
                                       doc_id, pno, REL_ADJACENT_TO, a["span_id"], b["span_id"],
                                       "span", "span",
                                       [_make_fact_ref("span", a["span_id"], "bbox"),
                                        _make_fact_ref("span", b["span_id"], "bbox")],
                                       conf, [{"gap": b["bbox"][1] - a["bbox"][3]}],
                                       {"coord_origin": cfg.coord_origin})
                rels.append(r.to_dict()); rel_ids.append(r.relation_id)
            # shares-region relation with the containing region
            region_ids = []
            for sid in sids:
                for r in region_by_span.get(sid, []):
                    if r["region_id"] not in region_ids:
                        region_ids.append(r["region_id"])
            if region_ids:
                r = StructuralRelation(_relation_id(doc_id, pno, REL_SHARES_REGION, sids[0], region_ids[0]),
                                       doc_id, pno, REL_SHARES_REGION, sids[0], region_ids[0],
                                       "span", "region",
                                       [_make_fact_ref("region", region_ids[0], "span_ids")],
                                       conf, [], {"coord_origin": cfg.coord_origin})
                rels.append(r.to_dict()); rel_ids.append(r.relation_id)

            fact_refs = [_make_fact_ref("span", sid, "bbox") for sid in sids]
            fact_refs += [_make_fact_ref("region", rid, "region_type") for rid in region_ids]
            trace = [
                {"step": "input", "span_ids": sids, "region_ids": region_ids,
                 "column_group_id": cg},
                {"step": "gaps", "vertical_gaps": gaps, "threshold": cfg.paragraph_gap_threshold},
                {"step": "decision", "reason": "reading-order-contiguous vertical run -> PARAGRAPH_GROUP_CANDIDATE",
                 "why_not_final": "grouping only; no text merge; no paragraph semantics"},
                {"step": "confidence", "structural": struct_conf, "upstream": upstream, "final": conf},
            ]
            h = StructureHypothesis(
                hypothesis_id=_hypothesis_id(doc_id, pno, HYP_PARAGRAPH, sids),
                document_id=doc_id, page_number=pno, hypothesis_type=HYP_PARAGRAPH,
                span_ids=sids, region_ids=region_ids,
                supporting_relation_ids=rel_ids, supporting_fact_refs=fact_refs,
                geometry=_bbox_union(run), confidence=conf,
                construction_method=METHOD_PARAGRAPH_VERTICAL_GROUPING,
                construction_version=cfg.construction_version,
                decision_trace=trace,
                provenance={"source_layers": ["P4_span", "P5_order", "P6_region"],
                            "distinct_from_C1": "reference grouping, no text reconstruction"},
                coord_origin=cfg.coord_origin,
            )
            out.append(h)
    return out


# ── Section ──────────────────────────────────────────────────────────────────

def _detect_sections(headings, spans, ro_by_span, region_by_span, layout, cfg,
                     page_w, page_h, doc_id, pno, rels) -> List[StructureHypothesis]:
    """Section candidate = a heading candidate + following reading-order span run
    until the next heading. No level (no H1/H2/H3)."""
    if not headings:
        return []
    # heading -> first reading index of its span
    def head_idx(h):
        idxs = [ro_by_span.get(sid, {}).get("reading_order_index", 10**9) for sid in h.span_ids]
        return min(idxs) if idxs else 10**9
    heads = sorted(headings, key=head_idx)
    ordered = [o["span_id"] for o in sorted(
        [ro_by_span[s["span_id"]] for s in spans if s["span_id"] in ro_by_span],
        key=lambda o: o["reading_order_index"])]

    out: List[StructureHypothesis] = []
    for i, h in enumerate(heads):
        start = head_idx(h)
        end = head_idx(heads[i + 1]) if i + 1 < len(heads) else 10**9
        members = [sid for sid in ordered if start <= ro_by_span.get(sid, {}).get("reading_order_index", 10**9) < end]
        if not members:
            continue
        heading_sid = h.span_ids[0]
        members_minus_heading = [sid for sid in members if sid != heading_sid]
        upstream = min_confidence(h.confidence, _span_upstream_conf(heading_sid, ro_by_span, region_by_span))
        struct_conf = CONFIDENCE_MEDIUM if len(members_minus_heading) >= 1 else CONFIDENCE_LOW
        conf = min_confidence(upstream, struct_conf)

        region_ids = []
        for sid in members:
            for r in region_by_span.get(sid, []):
                if r["region_id"] not in region_ids:
                    region_ids.append(r["region_id"])

        # precedes relation: heading precedes each member
        rel_ids = []
        r = StructuralRelation(_relation_id(doc_id, pno, REL_PRECEDES, heading_sid, heading_sid + "#section"),
                               doc_id, pno, REL_PRECEDES, heading_sid, "section_members",
                               "span", "section",
                               [_make_fact_ref("span", heading_sid, "bbox")],
                               conf, [{"heading_reading_index": start,
                                       "next_heading_index": end if end != 10**9 else None}],
                               {"coord_origin": cfg.coord_origin})
        rels.append(r.to_dict()); rel_ids.append(r.relation_id)

        fact_refs = [_make_fact_ref("span", heading_sid, "bbox")]
        fact_refs.append({"ref_type": "hypothesis", "ref_id": h.hypothesis_id, "fact": "HEADING_CANDIDATE"})
        for rid in region_ids:
            fact_refs.append(_make_fact_ref("region", rid, "region_type"))

        trace = [
            {"step": "input", "heading_span_id": heading_sid,
             "heading_hypothesis_id": h.hypothesis_id,
             "member_span_ids": members_minus_heading},
            {"step": "decision", "reason": "heading + following spans until next heading -> SECTION_CANDIDATE",
             "why_no_level": "heading level (H1/H2) is semantic; deferred to validation"},
            {"step": "confidence", "structural": struct_conf, "upstream": upstream, "final": conf},
        ]
        out.append(StructureHypothesis(
            hypothesis_id=_hypothesis_id(doc_id, pno, HYP_SECTION, members),
            document_id=doc_id, page_number=pno, hypothesis_type=HYP_SECTION,
            span_ids=members, region_ids=region_ids,
            supporting_relation_ids=rel_ids, supporting_fact_refs=fact_refs,
            geometry=_bbox_union([s for s in spans if s["span_id"] in members]),
            confidence=conf,
            construction_method=METHOD_SECTION_HEADING_SPAN,
            construction_version=cfg.construction_version,
            decision_trace=trace,
            provenance={"source_layers": ["P4_span", "P5_order", "P6_region", "P7_heading"],
                        "heading_hypothesis_id": h.hypothesis_id},
            coord_origin=cfg.coord_origin,
        ))
    return out


# ── List ─────────────────────────────────────────────────────────────────────

def _detect_lists(spans, ro_by_span, region_by_span, layout, cfg,
                  page_w, page_h, doc_id, pno, rels) -> List[StructureHypothesis]:
    """List candidate = consecutive run of left-aligned, style-consistent, short
    lines. No bullet/numbering text semantics."""
    col_members = defaultdict(list)
    for s in spans:
        ro = ro_by_span.get(s["span_id"], {})
        if ro.get("column_group_id") is not None:
            col_members[ro["column_group_id"]].append(s)

    out: List[StructureHypothesis] = []
    for cg, members in col_members.items():
        members = sorted(members, key=lambda s: ro_by_span.get(s["span_id"], {}).get("reading_order_index", 0))
        refw = max((m["bbox"][2] - m["bbox"][0]) for m in members) if members else page_w
        # greedy: accumulate a run while items satisfy list-item predicate
        i = 0
        while i < len(members):
            run = [members[i]]
            j = i + 1
            while j < len(members):
                a, b = members[j - 1], members[j]
                same_left = abs(a["bbox"][0] - b["bbox"][0]) <= cfg.list_left_align_tolerance
                gap_ok = (b["bbox"][1] - a["bbox"][3]) <= cfg.list_vertical_gap_max
                style_ok = (a.get("dominant_style_signature") == b.get("dominant_style_signature"))
                short_ok = ((b["bbox"][2] - b["bbox"][0]) <= refw * cfg.list_short_line_ratio
                            and (a["bbox"][2] - a["bbox"][0]) <= refw * cfg.list_short_line_ratio)
                if same_left and gap_ok and style_ok and short_ok:
                    run.append(b); j += 1
                else:
                    break
            if len(run) >= cfg.list_min_items:
                sids = [s["span_id"] for s in run]
                upstream = min_confidence(*[_span_upstream_conf(sid, ro_by_span, region_by_span) for sid in sids])
                x0s = [s["bbox"][0] for s in run]
                align_tight = (max(x0s) - min(x0s)) <= cfg.list_left_align_tolerance * 0.5
                struct_conf = CONFIDENCE_HIGH if (align_tight and len(run) >= 3) else CONFIDENCE_MEDIUM
                conf = min_confidence(upstream, struct_conf)

                region_ids = []
                for sid in sids:
                    for r in region_by_span.get(sid, []):
                        if r["region_id"] not in region_ids:
                            region_ids.append(r["region_id"])

                rel_ids = []
                for a, b in zip(run, run[1:]):
                    r = StructuralRelation(_relation_id(doc_id, pno, REL_LEFT_ALIGNED_WITH, a["span_id"], b["span_id"]),
                                           doc_id, pno, REL_LEFT_ALIGNED_WITH, a["span_id"], b["span_id"],
                                           "span", "span",
                                           [_make_fact_ref("span", a["span_id"], "bbox"),
                                            _make_fact_ref("span", b["span_id"], "bbox")],
                                           conf, [{"x0_delta": b["bbox"][0] - a["bbox"][0]}],
                                           {"coord_origin": cfg.coord_origin})
                    rels.append(r.to_dict()); rel_ids.append(r.relation_id)

                fact_refs = [_make_fact_ref("span", sid, "bbox") for sid in sids]
                fact_refs += [_make_fact_ref("span", sid, "dominant_style_signature") for sid in sids]
                trace = [
                    {"step": "input", "span_ids": sids, "column_group_id": cg},
                    {"step": "signals", "left_aligned": True, "x0_spread": max(x0s) - min(x0s),
                     "style_consistent": True, "item_count": len(run)},
                    {"step": "decision", "reason": "repeated left-alignment + sequential order + style consistency -> LIST_CANDIDATE",
                     "why_not_final": "no numbering/bullet semantics; candidate only"},
                    {"step": "confidence", "structural": struct_conf, "upstream": upstream, "final": conf},
                ]
                out.append(StructureHypothesis(
                    hypothesis_id=_hypothesis_id(doc_id, pno, HYP_LIST, sids),
                    document_id=doc_id, page_number=pno, hypothesis_type=HYP_LIST,
                    span_ids=sids, region_ids=region_ids,
                    supporting_relation_ids=rel_ids, supporting_fact_refs=fact_refs,
                    geometry=_bbox_union(run), confidence=conf,
                    construction_method=METHOD_LIST_ALIGNMENT,
                    construction_version=cfg.construction_version,
                    decision_trace=trace,
                    provenance={"source_layers": ["P4_span", "P5_order", "P6_region"]},
                    coord_origin=cfg.coord_origin,
                ))
                i = j
            else:
                i += 1
    return out


# ── Multi-column continuation ────────────────────────────────────────────────

def _detect_multicol(spans, ro_by_span, region_by_span, layout, cfg,
                     page_w, page_h, doc_id, pno, rels) -> List[StructureHypothesis]:
    """Continuation candidate = reading-order adjacency across two adjacent column
    groups with style continuity. Hypothesis only; never merges/modifies spans."""
    cols = sorted(layout.get("column_groups", []), key=lambda c: c.get("center_x", 0))
    if len(cols) < cfg.multicont_min_cols:
        return []
    out: List[StructureHypothesis] = []
    for a, b in zip(cols, cols[1:]):
        am = [s for s in spans if s["span_id"] in a.get("member_span_ids", [])]
        bm = [s for s in spans if s["span_id"] in b.get("member_span_ids", [])]
        if not am or not bm:
            continue
        am = sorted(am, key=lambda s: ro_by_span.get(s["span_id"], {}).get("reading_order_index", 0))
        bm = sorted(bm, key=lambda s: ro_by_span.get(s["span_id"], {}).get("reading_order_index", 0))
        a_last, b_first = am[-1], bm[0]
        a_ro = ro_by_span.get(a_last["span_id"], {})
        b_ro = ro_by_span.get(b_first["span_id"], {})
        signals = {}
        # signal 1: reading-order link (a_last.next == b_first)
        if a_ro.get("next_span_id") == b_first["span_id"]:
            signals["order_link"] = {"a_last": a_last["span_id"], "b_first": b_first["span_id"]}
        # signal 2: style continuity
        if a_last.get("dominant_style_signature") == b_first.get("dominant_style_signature") and \
           a_last.get("dominant_style_signature") is not None:
            signals["style_continuity"] = {"sig": a_last.get("dominant_style_signature")}
        # signal 3: spatial continuity (a_last near column bottom, b_first near column top)
        a_span_ys = [s["bbox"][3] for s in am]; b_span_ys = [s["bbox"][1] for s in bm]
        a_bottom_gap = max(a_span_ys) - a_last["bbox"][3]
        b_top_gap = b_first["bbox"][1] - min(b_span_ys)
        if a_bottom_gap <= cfg.paragraph_gap_threshold and b_top_gap <= cfg.paragraph_gap_threshold:
            signals["spatial_continuity"] = {"a_bottom_gap": a_bottom_gap, "b_top_gap": b_top_gap}

        required = 2 + (1 if cfg.multicont_style_required else 0)
        if len(signals) < 2 or (cfg.multicont_style_required and "style_continuity" not in signals):
            continue

        sids = [a_last["span_id"], b_first["span_id"]]
        upstream = min_confidence(_span_upstream_conf(a_last["span_id"], ro_by_span, region_by_span),
                                  _span_upstream_conf(b_first["span_id"], ro_by_span, region_by_span))
        struct_conf = CONFIDENCE_MEDIUM if len(signals) >= 3 else CONFIDENCE_LOW
        conf = min_confidence(upstream, struct_conf)

        rel_ids = []
        r = StructuralRelation(_relation_id(doc_id, pno, REL_CONTINUES_FROM, a_last["span_id"], b_first["span_id"]),
                               doc_id, pno, REL_CONTINUES_FROM, a_last["span_id"], b_first["span_id"],
                               "span", "span",
                               [_make_fact_ref("span", a_last["span_id"], "bbox"),
                                _make_fact_ref("span", b_first["span_id"], "bbox")],
                               conf, [{"signals": list(signals.keys())}],
                               {"coord_origin": cfg.coord_origin})
        rels.append(r.to_dict()); rel_ids.append(r.relation_id)

        region_ids = []
        for r_ in region_by_span.get(a_last["span_id"], []):
            region_ids.append(r_["region_id"])
        for r_ in region_by_span.get(b_first["span_id"], []):
            region_ids.append(r_["region_id"])
        region_ids = list(dict.fromkeys(region_ids))

        trace = [
            {"step": "input", "column_a_id": a.get("column_group_id"),
             "column_b_id": b.get("column_group_id"),
             "boundary_spans": sids},
            {"step": "signals", "collected": list(signals.keys()), "details": signals},
            {"step": "decision", "reason": "cross-column reading-order adjacency + style continuity -> MULTI_COLUMN_CONTINUATION_CANDIDATE",
             "why_not_final": "no span/order modification; hypothesis only"},
            {"step": "confidence", "structural": struct_conf, "upstream": upstream, "final": conf},
        ]
        out.append(StructureHypothesis(
            hypothesis_id=_hypothesis_id(doc_id, pno, HYP_MULTICOL, sids),
            document_id=doc_id, page_number=pno, hypothesis_type=HYP_MULTICOL,
            span_ids=sids, region_ids=region_ids,
            supporting_relation_ids=rel_ids,
            supporting_fact_refs=[_make_fact_ref("span", sid, "bbox") for sid in sids],
            geometry=_bbox_union([a_last, b_first]), confidence=conf,
            construction_method=METHOD_MULTICOL_CONTINUATION,
            construction_version=cfg.construction_version,
            decision_trace=trace,
            provenance={"source_layers": ["P4_span", "P5_order", "P6_region"]},
            coord_origin=cfg.coord_origin,
        ))
    return out


# ── Cross-page header / footer repeat ────────────────────────────────────────

def _repeat_key(s, page_w, page_h, cfg, zone):
    cx = (s["bbox"][0] + s["bbox"][2]) / 2.0
    cy = (s["bbox"][1] + s["bbox"][3]) / 2.0
    tol = cfg.header_position_tolerance if zone == "top" else cfg.footer_position_tolerance
    bx = int(round((cx / page_w) / tol))
    by = int(round((cy / page_h) / tol))
    text_h = hashlib.sha1((s.get("text") or "").strip().encode("utf-8")).hexdigest()[:12]
    return f"{bx}|{by}|{text_h}"


def compute_cross_page_repeats(pages_data: List[Dict[str, Any]], cfg: StructureConfig = DEFAULT_CONFIG):
    """Detect HEADER_CANDIDATE / FOOTER_CANDIDATE from repetition of the same
    unit (position bucket + text identity) across >= header_min_repeat_pages.

    pages_data: [{page_number, page_w, page_h, top_spans, bottom_spans}]
    Returns list of StructureHypothesis (one per occurrence page).
    """
    from .structure_config import STATUS_PROPOSED
    top_map = defaultdict(list)
    bottom_map = defaultdict(list)
    for pg in pages_data:
        doc_id = pg["document_id"]
        for s in pg.get("top_spans", []):
            key = _repeat_key(s, pg["page_w"], pg["page_h"], cfg, "top")
            top_map[key].append((pg["page_number"], s))
        for s in pg.get("bottom_spans", []):
            key = _repeat_key(s, pg["page_w"], pg["page_h"], cfg, "bottom")
            bottom_map[key].append((pg["page_number"], s))

    out: List[StructureHypothesis] = []
    all_rels: List[Dict[str, Any]] = []

    def emit(zone_map, zone_label, hyp_type, method, doc_id):
        for key, occurrences in zone_map.items():
            if len(occurrences) < cfg.header_min_repeat_pages:
                continue
            pages = sorted({p for p, _ in occurrences})
            for pno, s in occurrences:
                upstream = CONFIDENCE_HIGH  # cross-page repetition is strong geometric evidence
                struct_conf = CONFIDENCE_MEDIUM if len(pages) >= 3 else CONFIDENCE_LOW
                conf = min_confidence(upstream, struct_conf)
                rel_ids = []
                # repeats-across-pages relation to every other occurrence
                for p2, s2 in occurrences:
                    if p2 == pno:
                        continue
                    r = StructuralRelation(_relation_id(doc_id, pno, REL_REPEATS_ACROSS_PAGES, s["span_id"], s2["span_id"]),
                                           doc_id, pno, REL_REPEATS_ACROSS_PAGES, s["span_id"], s2["span_id"],
                                           "span", "span",
                                           [_make_fact_ref("span", s["span_id"], "bbox"),
                                            _make_fact_ref("span", s2["span_id"], "bbox")],
                                           conf, [{"repeat_pages": pages}],
                                           {"coord_origin": cfg.coord_origin})
                    all_rels.append(r.to_dict()); rel_ids.append(r.relation_id)
                fact_refs = [_make_fact_ref("span", s["span_id"], "bbox"),
                             _make_fact_ref("span", s["span_id"], "text")]
                trace = [
                    {"step": "input", "span_id": s["span_id"], "zone": zone_label,
                     "repeat_pages": pages},
                    {"step": "decision",
                     "reason": f"same unit repeats at {zone_label} across pages {pages} -> {hyp_type}",
                     "why_not_final": "repetition is evidence, not a semantic header/footer claim"},
                    {"step": "confidence", "structural": struct_conf, "upstream": upstream, "final": conf},
                ]
                out.append(StructureHypothesis(
                    hypothesis_id=_hypothesis_id(doc_id, pno, hyp_type, [s["span_id"]]),
                    document_id=doc_id, page_number=pno, hypothesis_type=hyp_type,
                    span_ids=[s["span_id"]], region_ids=[],
                    supporting_relation_ids=rel_ids, supporting_fact_refs=fact_refs,
                    geometry=_bbox_union([s]), confidence=conf,
                    construction_method=method,
                    construction_version=cfg.construction_version,
                    decision_trace=trace,
                    provenance={"source_layers": ["P1_text", "P4_span", "P5_order", "P6_region"],
                                "cross_page_evidence": True,
                                "repeat_pages": pages},
                    coord_origin=cfg.coord_origin,
                ))
    emit(top_map, "top", HYP_HEADER, METHOD_HEADER_REPEAT,
         pages_data[0]["document_id"] if pages_data else "UNKNOWN")
    emit(bottom_map, "bottom", HYP_FOOTER, METHOD_FOOTER_REPEAT,
         pages_data[0]["document_id"] if pages_data else "UNKNOWN")
    return out, all_rels


# ── Page-level entry ─────────────────────────────────────────────────────────

def compute_page_structure(spans: List[Dict[str, Any]],
                           reading_order: Dict[str, Any],
                           layout: Dict[str, Any],
                           regions: Dict[str, Any],
                           cfg: StructureConfig = DEFAULT_CONFIG) -> PageStructureBundle:
    """Main per-page engine: heading / paragraph / section / list / multi-column.

    Note: HEADER/FOOTER candidates are cross-page and handled separately by
    compute_cross_page_repeats (multi-page repetition evidence is required).
    """
    if not spans:
        return PageStructureBundle(document_id="UNKNOWN", page_number=0,
                                   page_width=0.0, page_height=0.0,
                                   coord_origin=cfg.coord_origin)
    doc_id = spans[0]["document_id"]
    pno = spans[0]["page_number"]
    page_w = layout.get("page_width") or 0.0
    page_h = layout.get("page_height") or 0.0

    ro_by_span = {o["span_id"]: o for o in reading_order.get("observations", [])}
    region_by_span: Dict[str, List[Dict]] = defaultdict(list)
    for r in regions.get("regions", []):
        for sid in r.get("span_ids", []):
            region_by_span[sid].append(r)

    rels: List[Dict[str, Any]] = []
    hypotheses: List[StructureHypothesis] = []

    headings = _detect_headings(spans, ro_by_span, region_by_span, layout, cfg,
                                page_w, page_h, doc_id, pno, rels)
    hypotheses.extend(headings)
    hypotheses.extend(_detect_paragraphs(spans, ro_by_span, region_by_span, layout, cfg,
                                         page_w, page_h, doc_id, pno, rels))
    hypotheses.extend(_detect_lists(spans, ro_by_span, region_by_span, layout, cfg,
                                    page_w, page_h, doc_id, pno, rels))
    hypotheses.extend(_detect_multicol(spans, ro_by_span, region_by_span, layout, cfg,
                                       page_w, page_h, doc_id, pno, rels))
    hypotheses.extend(_detect_sections(headings, spans, ro_by_span, region_by_span, layout, cfg,
                                       page_w, page_h, doc_id, pno, rels))

    # dedupe by hypothesis_id
    seen = {}
    for h in hypotheses:
        seen.setdefault(h.hypothesis_id, h)
    unique = list(seen.values())

    return PageStructureBundle(
        document_id=doc_id, page_number=pno,
        page_width=page_w, page_height=page_h, coord_origin=cfg.coord_origin,
        hypotheses=[h.to_dict() for h in unique],
        relations=rels,
        provenance={"source_layers": ["P1_atomic", "P2_geometry", "P3_style",
                                      "P4_span", "P5_reading_order", "P6_region"],
                    "engine": "structure_engine", "version": cfg.construction_version},
    )
