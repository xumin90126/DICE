"""
P4 Span — construction engine.

Builds ExperimentalSpan v2 from P1 Atomic Observations + P2 Geometry + P3 Style.
Deterministic, traceable, splittable. No semantic classification.

Algorithm:
  For each page, take observations in source order (reading_order_hint).
  Greedily merge consecutive observations where merge rules say MERGE.
  Each span retains source_observation_ids for reverse traceability.
  Position(x513) and Step(x77) will NOT merge (cross-column gap).
"""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from .span_config import SpanConfig, DEFAULT_CONFIG, REASON_MERGE, REASON_KEEP_SEPARATE, MERGE_REASON_SAME_LINE_CONTIGUOUS, MERGE_REASON_NEXT_LINE_CONTIGUOUS
from .span_observation import ExperimentalSpan, MergeDecision
from .span_rules import decide_merge


def _union_bbox(bboxes: List[List[float]]) -> List[float]:
    if not bboxes:
        return [0.0, 0.0, 0.0, 0.0]
    x0 = min(b[0] for b in bboxes)
    y0 = min(b[1] for b in bboxes)
    x1 = max(b[2] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    return [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]


def _span_id(document_id: str, page: int, first_obs_id: str) -> str:
    return hashlib.sha1(f"span|{document_id}|p{page}|{first_obs_id}".encode()).hexdigest()[:16]


def _reconstruct_text(observations: List[Dict[str, Any]], same_line_groups: List[bool]) -> str:
    """Deterministically reconstruct span text from source observations.
    same_line_groups[i] = True means obs[i] and obs[i+1] are on same line (join with space).
    False means newline."""
    parts = []
    for i, obs in enumerate(observations):
        parts.append(obs.get("text", ""))
    # Join: if same line, use space; if different line, use newline
    result = parts[0] if parts else ""
    for i in range(1, len(parts)):
        if same_line_groups[i - 1]:
            result += " " + parts[i]
        else:
            result += "\n" + parts[i]
    return result


def _dominant_signature(signatures: List[str]) -> Optional[str]:
    if not signatures:
        return None
    c = Counter(signatures)
    return c.most_common(1)[0][0]


def construct_spans(
    observations: List[Dict[str, Any]],
    geometry_relations: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
    style_map: Optional[Dict[str, Dict[str, Any]]] = None,
    cfg: SpanConfig = DEFAULT_CONFIG,
) -> Tuple[List[ExperimentalSpan], List[MergeDecision]]:
    """Construct ExperimentalSpan v2 from observations on a page.

    Args:
        observations: P1 AtomicTextObservation dicts (same page), in source order.
        geometry_relations: P2 PairwiseRelation dicts keyed by (a_id, b_id).
            If None, rules compute geometry from bboxes directly.
        style_map: P3 StyleObservation dicts keyed by source observation_id.
            If None, style facts are unavailable (same_style_signature=False).
        cfg: SpanConfig.

    Returns:
        (spans, decisions) — spans are ExperimentalSpan v2, decisions are
        MergeDecision for every consecutive pair evaluated.
    """
    if not observations:
        return [], []

    # Sort by source order (reading_order_hint, then source_index)
    obs_sorted = sorted(observations, key=lambda o: (
        o.get("reading_order_hint", o.get("source_index", 0)),
        o.get("source_index", 0),
    ))

    if geometry_relations is None:
        geometry_relations = {}
    if style_map is None:
        style_map = {}

    decisions: List[MergeDecision] = []
    spans: List[ExperimentalSpan] = []

    # Greedy merge: start with first observation, try to extend with next
    current_group: List[Dict[str, Any]] = [obs_sorted[0]]
    same_line_flags: List[bool] = []  # flags between current_group members

    for i in range(1, len(obs_sorted)):
        prev = current_group[-1]
        curr = obs_sorted[i]

        # Get geometry relation (prev relative to curr)
        geom_key = (prev["observation_id"], curr["observation_id"])
        geom = geometry_relations.get(geom_key)

        # Get styles
        style_prev = style_map.get(prev["observation_id"])
        style_curr = style_map.get(curr["observation_id"])

        decision = decide_merge(prev, curr, geom, style_prev, style_curr, cfg)
        decisions.append(decision)

        if decision.decision == REASON_MERGE:
            current_group.append(curr)
            same_line_flags.append(decision.same_y_band)
        else:
            # Close current span, start new
            spans.append(_build_span(current_group, same_line_flags, cfg, "contiguous_merge"))
            current_group = [curr]
            same_line_flags = []

    # Close last group
    if current_group:
        method = "single_observation" if len(current_group) == 1 else "contiguous_merge"
        spans.append(_build_span(current_group, same_line_flags, cfg, method))

    return spans, decisions


def _build_span(group: List[Dict[str, Any]], same_line_flags: List[bool],
                cfg: SpanConfig, method: str) -> ExperimentalSpan:
    obs_ids = [o["observation_id"] for o in group]
    obs_types = [o.get("source_type", "") for o in group]
    bboxes = [o["bbox"] for o in group if o.get("bbox")]
    ubbox = _union_bbox(bboxes)
    w = round(ubbox[2] - ubbox[0], 2)
    h = round(ubbox[3] - ubbox[1], 2)
    cx = round((ubbox[0] + ubbox[2]) / 2, 2)
    cy = round((ubbox[1] + ubbox[3]) / 2, 2)

    # Reconstruct text
    text = _reconstruct_text(group, same_line_flags)

    # Style summary: we need style_map but it's not passed here; derive from
    # observations' own style fields if present (P1 span layer has font info)
    # For proper style, caller should pass style-enhanced observations.
    # Here we use whatever style info is on the observation dicts.
    sigs = []
    for o in group:
        # If observation carries style_signature (enriched), use it
        sig = o.get("_style_signature")
        if sig:
            sigs.append(sig)
    dom_sig = _dominant_signature(sigs) if sigs else None

    doc_id = group[0].get("document_id", "")
    pno = group[0].get("page_number", 0)

    # Construction reason: from the merge decisions that formed this span
    # (passed via same_line_flags context — simplified here)
    reason = MERGE_REASON_SAME_LINE_CONTIGUOUS if method == "contiguous_merge" and same_line_flags and all(same_line_flags) else (
        MERGE_REASON_NEXT_LINE_CONTIGUOUS if method == "contiguous_merge" else "SINGLE_OBSERVATION"
    )

    return ExperimentalSpan(
        span_id=_span_id(doc_id, pno, obs_ids[0]),
        document_id=doc_id,
        page_number=pno,
        text=text,
        source_observation_ids=obs_ids,
        source_observation_types=obs_types,
        observation_count=len(group),
        first_observation_id=obs_ids[0],
        last_observation_id=obs_ids[-1],
        bbox=ubbox,
        width=w,
        height=h,
        center_x=cx,
        center_y=cy,
        dominant_style_signature=dom_sig,
        style_count=len(set(sigs)),
        style_signatures=list(dict.fromkeys(sigs)),  # distinct, source order
        construction_method=method,
        construction_version=cfg.construction_version,
        construction_reason=reason,
        merge_decision_trace=[],  # populated by caller if needed
        provenance={
            "source_document": doc_id,
            "source_layers": list(set(obs_types)),
            "construction_config": cfg.construction_version,
        },
    )


def construct_spans_with_trace(
    observations: List[Dict[str, Any]],
    geometry_relations: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
    style_map: Optional[Dict[str, Dict[str, Any]]] = None,
    cfg: SpanConfig = DEFAULT_CONFIG,
) -> Tuple[List[ExperimentalSpan], List[MergeDecision]]:
    """Like construct_spans but attaches decision traces to each span."""
    spans, decisions = construct_spans(observations, geometry_relations, style_map, cfg)
    # Map decisions to spans by observation membership
    dec_by_a = {d.observation_a_id: d for d in decisions}
    for span in spans:
        trace = []
        for oid in span.source_observation_ids:
            if oid in dec_by_a:
                trace.append(dec_by_a[oid].to_dict())
        span.merge_decision_trace = trace
    return spans, decisions


def verify_observation_coverage(spans: List[ExperimentalSpan],
                                observation_ids: List[str]) -> Dict[str, Any]:
    """Verify every observation is assigned to exactly one span (or explicitly excluded)."""
    assigned = []
    for span in spans:
        assigned.extend(span.source_observation_ids)
    assigned_set = set(assigned)
    obs_set = set(observation_ids)

    orphans = obs_set - assigned_set
    duplicates = [oid for oid in assigned if assigned.count(oid) > 1]
    lost = obs_set - assigned_set

    return {
        "total_observations": len(obs_set),
        "assigned": len(assigned_set),
        "orphan_count": len(orphans),
        "orphan_ids": list(orphans)[:10],
        "duplicate_count": len(set(duplicates)),
        "duplicate_ids": list(set(duplicates))[:10],
        "lost_count": len(lost),
        "coverage": round(len(assigned_set) / len(obs_set), 4) if obs_set else 0.0,
        "pass": len(orphans) == 0 and len(duplicates) == 0,
    }


def reconstruct_span_text(span: ExperimentalSpan,
                          observation_map: Dict[str, Dict[str, Any]]) -> str:
    """Reverse traceability: reconstruct span text from source observations."""
    obs = [observation_map[oid] for oid in span.source_observation_ids if oid in observation_map]
    if not obs:
        return ""
    # Use same logic as construction (simplified: join with space if same y)
    result = obs[0].get("text", "")
    for i in range(1, len(obs)):
        bb_a = obs[i - 1].get("bbox", [0, 0, 0, 0])
        bb_b = obs[i].get("bbox", [0, 0, 0, 0])
        same_y = abs((bb_a[1] + bb_a[3]) / 2 - (bb_b[1] + bb_b[3]) / 2) <= 3.0
        result += " " + obs[i].get("text", "") if same_y else "\n" + obs[i].get("text", "")
    return result


__all__ = [
    "construct_spans", "construct_spans_with_trace",
    "verify_observation_coverage", "reconstruct_span_text",
]
