"""
System Suggestion Translator — maps P7.1 hypothesis signals to plain language.

This is PRESENTATION logic only. It translates existing P7.1 output (hypothesis_type,
confidence, signals) into human-readable suggestion text. It does NOT:
- modify candidate generation
- add new heuristics
- make decisions
- use domain knowledge the system doesn't have

Anti-confirmation-bias rules:
- Always "系统建议" (suggestion), never "正确答案是" (correct answer is)
- LOW confidence → "系统无法确定" + show possible interpretations
- Never induce Human to accept system answer
"""
from __future__ import annotations

from typing import Any, Dict, List


# ── Signal → plain language mapping ──────────────────────────────────────────
SIGNAL_PLAIN = {
    "style_contrast": "文字样式（粗体或字号）与周围正文不同",
    "short_line": "文字行较短，不像完整段落",
    "spatial_separation": "与上下文内容有明显间距",
    "reading_position": "位于阅读顺序的特殊位置",
    "left_aligned": "与页面左侧对齐",
    "repeats_across_pages": "在多页中重复出现",
}

# ── Hypothesis type → plain language ─────────────────────────────────────────
TYPE_PLAIN = {
    "HEADING_CANDIDATE": "标题",
    "PARAGRAPH_GROUP_CANDIDATE": "段落组",
    "SECTION_CANDIDATE": "章节",
    "LIST_CANDIDATE": "列表",
    "HEADER_CANDIDATE": "页眉",
    "FOOTER_CANDIDATE": "页脚",
    "MULTI_COLUMN_CONTINUATION_CANDIDATE": "多栏续接内容",
}

# Possible alternative interpretations for ambiguous candidates
TYPE_ALTERNATIVES = {
    "HEADING_CANDIDATE": ["正文章节标题", "目录或引用内容", "表格标签", "页眉页脚"],
}


def generate_suggestion(observation: Dict[str, Any]) -> Dict[str, str]:
    """Generate plain-language system suggestion from a P7.1 hypothesis.

    Returns: {suggestion_text, reasoning_text, confidence_display, alternatives}
    """
    htype = observation.get("hypothesis_type", "UNKNOWN")
    conf = observation.get("confidence", "UNKNOWN")
    type_plain = TYPE_PLAIN.get(htype, htype.replace("_CANDIDATE", "").lower())

    # Extract signals from decision_trace
    signals = []
    for step in observation.get("decision_trace", []):
        if step.get("step") == "signals":
            signals = step.get("collected", [])

    # Build reasoning from signals
    reasons = [SIGNAL_PLAIN.get(s, s) for s in signals if s in SIGNAL_PLAIN]
    if reasons:
        reasoning = "判断依据：" + "；".join(reasons) + "。"
    else:
        reasoning = "判断依据：基于页面排版特征。"

    # Suggestion text based on confidence (anti-confirmation-bias)
    if conf == "HIGH":
        suggestion = f"系统建议：这可能是一个{type_plain}。"
        alternatives = []
    elif conf == "MEDIUM":
        suggestion = f"系统建议：这可能是一个{type_plain}，但系统不是完全确定。"
        alternatives = []
    elif conf == "LOW":
        suggestion = f"系统无法确定，建议人工判断。"
        alts = TYPE_ALTERNATIVES.get(htype, [])
        if alts:
            alternatives = alts
        else:
            alternatives = []
    else:  # UNKNOWN / AMBIGUOUS
        suggestion = f"系统无法确定，建议人工判断。"
        alternatives = TYPE_ALTERNATIVES.get(htype, [])

    # Confidence display (simplified for Human — no internal jargon)
    if conf == "HIGH":
        confidence_display = "系统较有信心"
    elif conf == "MEDIUM":
        confidence_display = "系统有一定信心"
    elif conf == "LOW":
        confidence_display = "系统信心较低"
    else:
        confidence_display = "系统无法确定"

    return {
        "suggestion_text": suggestion,
        "reasoning_text": reasoning,
        "confidence_display": confidence_display,
        "alternatives": alternatives,
    }


def build_candidate_payload(observation: Dict[str, Any],
                            span_text_lookup: Dict[str, str],
                            page_image_url: str,
                            page_width: float,
                            page_height: float,
                            index: int,
                            total: int) -> Dict[str, Any]:
    """Build the JSON payload for one candidate to send to the web UI.

    Contains ONLY what Human needs to see. Internal fields (hypothesis_id etc.)
    are included for audit but not displayed.
    """
    sug = generate_suggestion(observation)
    span_ids = observation.get("span_ids", [])
    texts = [span_text_lookup.get(sid, "") for sid in span_ids]
    bbox = observation.get("geometry", {}).get("bbox", [0, 0, 0, 0])

    return {
        # Human-visible (display)
        "index": index,
        "total": total,
        "candidate_text": " ".join(t for t in texts if t),
        "suggestion_text": sug["suggestion_text"],
        "reasoning_text": sug["reasoning_text"],
        "confidence_display": sug["confidence_display"],
        "alternatives": sug["alternatives"],
        "page_number": observation.get("page_number", 1),
        "bbox": bbox,
        "page_image_url": page_image_url,
        "page_width": page_width,
        "page_height": page_height,

        # Internal (for audit, NOT displayed to Human)
        "observation_id": observation.get("hypothesis_id", ""),
        "observation_type": observation.get("hypothesis_type", ""),
        "confidence": observation.get("confidence", ""),
        "span_ids": span_ids,
    }
