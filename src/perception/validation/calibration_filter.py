"""
Calibration Filter — post-processes P7.1 candidates using Human feedback patterns.

This is a CALIBRATION LAYER, not a P7.1 modification. P7.1 stays frozen.
The filter sits between P7.1 output and ValidationTask creation.

Patterns learned from real Human validation (arxiv_toc Round 1):
  - "1.xxx是一整个标题，这是一个标题的序号部分" → number fragments should merge with title
  - "页面页数标志" → page numbers (right-aligned, numeric) are not headings
  - "数学符号" → math symbols (∗, γ, −, +, ℓ) are not headings
  - "是标题，但是识别不完整，同时标题序号没有加上" → incomplete capture

Calibration rules:
  1. Fragment detection: width < 15pt → likely fragment (number/symbol/page-number)
  2. Row grouping: candidates on same y (±5pt) = fragments of same logical entry
  3. Pure-fragment row filter: if ALL candidates in row are fragments → drop row
  4. Row merge: merge remaining grouped candidates into one unified candidate
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

FRAGMENT_WIDTH_THRESHOLD = 15.0   # pt — candidates narrower than this are fragments
ROW_Y_TOLERANCE = 5.0             # pt — candidates within this y range are same row


def is_fragment(candidate: Dict[str, Any]) -> bool:
    """Detect if a candidate is a fragment (number, symbol, page number)."""
    bbox = candidate.get("geometry", {}).get("bbox", candidate.get("bbox", [0,0,0,0]))
    width = bbox[2] - bbox[0]
    return width < FRAGMENT_WIDTH_THRESHOLD


def group_by_row(candidates: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Group candidates by y-position (same row = fragments of same logical entry)."""
    if not candidates:
        return []

    # Sort by y then x
    sorted_cands = sorted(candidates, key=lambda c: (
        c.get("geometry", {}).get("bbox", c.get("bbox", [0,0,0,0]))[1],
        c.get("geometry", {}).get("bbox", c.get("bbox", [0,0,0,0]))[0],
    ))

    rows: List[List[Dict[str, Any]]] = []
    current_row = [sorted_cands[0]]
    current_y = sorted_cands[0].get("geometry", {}).get("bbox", sorted_cands[0].get("bbox", [0,0,0,0]))[1]

    for c in sorted_cands[1:]:
        y = c.get("geometry", {}).get("bbox", c.get("bbox", [0,0,0,0]))[1]
        if abs(y - current_y) <= ROW_Y_TOLERANCE:
            current_row.append(c)
        else:
            rows.append(current_row)
            current_row = [c]
            current_y = y
    rows.append(current_row)
    return rows


def merge_row(row: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple fragment candidates on the same row into one unified candidate."""
    if len(row) == 1:
        return row[0]

    # Sort by x position (left to right)
    sorted_row = sorted(row, key=lambda c: c.get("geometry", {}).get("bbox", c.get("bbox", [0,0,0,0]))[0])

    # Merge bbox: min x0, min y0, max x1, max y1
    bboxes = [c.get("geometry", {}).get("bbox", c.get("bbox", [0,0,0,0])) for c in sorted_row]
    merged_bbox = [
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    ]

    # Merge span_ids
    all_span_ids = []
    for c in sorted_row:
        all_span_ids.extend(c.get("span_ids", []))

    # Merge text
    texts = []
    for c in sorted_row:
        t = c.get("candidate_text", "")
        if isinstance(t, str) and t.strip():
            texts.append(t.strip())
        elif "text" in c:
            texts.append(c["text"].strip())
    merged_text = " ".join(texts)

    # Use the first candidate as base (highest confidence typically)
    base = sorted_row[0]
    base_type = base.get("hypothesis_type", base.get("observation_type", ""))

    # Generate merged ID
    raw_id = "|".join(sorted(c.get("hypothesis_id", c.get("observation_id", "")) for c in sorted_row))
    merged_id = hashlib.sha1(raw_id.encode()).hexdigest()[:16]

    # Build merged candidate (preserving original structure)
    merged = dict(base)  # shallow copy
    # Always set merged text (both P7.1 format and API format)
    merged["candidate_text"] = merged_text
    if "hypothesis_id" in merged:
        merged["hypothesis_id"] = merged_id
        merged["geometry"] = {
            "bbox": merged_bbox,
            "width": merged_bbox[2] - merged_bbox[0],
            "height": merged_bbox[3] - merged_bbox[1],
            "center_x": (merged_bbox[0] + merged_bbox[2]) / 2,
            "center_y": (merged_bbox[1] + merged_bbox[3]) / 2,
        }
        merged["span_ids"] = all_span_ids
        merged["_merged_from"] = [c.get("hypothesis_id", c.get("observation_id", "")) for c in sorted_row]
        merged["_calibration"] = "merged_row"
    else:
        # API payload format
        merged["observation_id"] = merged_id
        merged["bbox"] = merged_bbox
        merged["span_ids"] = all_span_ids
        merged["_merged_from"] = [c.get("observation_id", "") for c in sorted_row]
        merged["_calibration"] = "merged_row"

    return merged


def calibrate_candidates(candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Apply calibration filter to P7.1 candidates.

    Returns: (calibrated_candidates, calibration_report)
    """
    original_count = len(candidates)

    # Step 1: Group by row
    rows = group_by_row(candidates)

    # Step 2: Filter pure-fragment rows (all candidates are fragments)
    filtered_rows = []
    dropped_fragment_rows = []
    for row in rows:
        all_fragments = all(is_fragment(c) for c in row)
        if all_fragments:
            dropped_fragment_rows.append(row)
        else:
            filtered_rows.append(row)

    # Step 3: Merge remaining rows
    calibrated = []
    for row in filtered_rows:
        merged = merge_row(row)
        calibrated.append(merged)

    # Build report
    fragment_count = sum(1 for c in candidates if is_fragment(c))
    dropped_count = sum(len(r) for r in dropped_fragment_rows)

    report = {
        "original_candidate_count": original_count,
        "calibrated_candidate_count": len(calibrated),
        "fragment_count": fragment_count,
        "fragment_rate": round(fragment_count / original_count * 100, 1) if original_count else 0,
        "dropped_pure_fragment_rows": len(dropped_fragment_rows),
        "dropped_candidates": dropped_count,
        "merged_rows": sum(1 for r in filtered_rows if len(r) > 1),
        "reduction_rate": round((original_count - len(calibrated)) / original_count * 100, 1) if original_count else 0,
        "calibration_method": "row_grouping + fragment_filter + row_merge",
        "patterns_source": "Human validation feedback (arxiv_toc Round 1)",
        "p71_unchanged": True,
    }

    return calibrated, report
