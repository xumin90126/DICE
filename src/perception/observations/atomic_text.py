"""
P1 — Atomic Document Perception Foundation.

Atomic Text Observation extractor.

Design principles (frozen for P1):
  - Observations describe ONLY "what was observed" (raw facts).
  - NO semantic classification: no heading / caption / table / formula /
    flowchart / paragraph / evidence / meaning detection.
  - NO high-level rules ("if bold then heading", "if x-distance then table").
  - Provenance preserved: every observation carries source_type + source_index.
  - Independent of CandidateSpan / Frozen 730 Pool / Legacy Generator.
  - Read-only with respect to all frozen objects.

Primary data source: PyMuPDF "dict" span layer (richest: text + bbox + font +
size + flags + line membership). Word layer ("words") used as a natural-atomic
cross-validation. Character ("rawdict"), line ("dict" lines), and block
("blocks") layers also extracted for provenance comparison — block is the
Legacy Generator's sole source and the documented corruption layer.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF — READ-ONLY PDF extraction

# Layer tags (source_type vocabulary)
SOURCE_CHAR = "character"
SOURCE_WORD = "word"
SOURCE_SPAN = "span"
SOURCE_LINE = "line"
SOURCE_BLOCK = "block"

_PYMUPDF_VERSION = ".".join(str(v) for v in fitz.version[:2] if v is not None)


@dataclass
class AtomicTextObservation:
    """One atomic text fact observed on a PDF page.

    Describes ONLY what was observed. Carries NO semantic classification.
    Fields that cannot be reliably obtained are left null rather than guessed.
    """
    observation_id: str           # deterministic id (see _make_obs_id)
    document_id: str              # source document identifier (caller-supplied)
    page_number: int              # 1-based page number
    text: str                     # observed text content (raw, stripped only of trailing whitespace)
    bbox: Optional[List[float]]   # [x0, y0, x1, y1] in PDF points; null if unavailable
    source_type: str              # character / word / span / line / block
    source_index: int             # index within the source layer's emission order on this page
    reading_order_hint: int       # monotonic hint for reading order within (page, source_type)
    font_name: Optional[str]      # font name (span/line layers only; null for word/char/block)
    font_size: Optional[float]    # font size in pt (span/line layers only)
    font_flags: Optional[int]     # PyMuPDF flags bitmask (span/line layers only)
    line_index: Optional[int]     # parent line index in dict (span/line only)
    block_index: Optional[int]    # parent block index in dict (span/line/word via mapping)
    provenance: Dict[str, Any] = field(default_factory=dict)  # extra provenance facts

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def _round_bbox(bb) -> Optional[List[float]]:
    if bb is None:
        return None
    return [round(float(bb[0]), 2), round(float(bb[1]), 2),
            round(float(bb[2]), 2), round(float(bb[3]), 2)]


def _make_obs_id(document_id: str, page: int, source_type: str, source_index: int) -> str:
    raw = f"{document_id}|p{page}|{source_type}|{source_index}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _strip_text(t: str) -> str:
    """Strip only surrounding whitespace; preserve internal structure."""
    return t.strip()


# ── Layer extractors ──────────────────────────────────────────────────────

def _extract_span_observations(page, page_no: int, document_id: str) -> List[AtomicTextObservation]:
    """Extract observations from PyMuPDF 'dict' span layer (PRIMARY).

    A span = a run of same-font/same-size text. Richest layer: carries
    font_name / font_size / font_flags + line/block membership.
    """
    d = page.get_text("dict")
    obs: List[AtomicTextObservation] = []
    order = 0
    span_global = 0
    for bi, b in enumerate(d["blocks"]):
        if "lines" not in b:
            continue
        for li, line in enumerate(b["lines"]):
            for sp in line["spans"]:
                text = _strip_text(sp["text"])
                if not text:
                    continue
                bb = sp.get("bbox")
                obs.append(AtomicTextObservation(
                    observation_id=_make_obs_id(document_id, page_no, SOURCE_SPAN, span_global),
                    document_id=document_id,
                    page_number=page_no,
                    text=text,
                    bbox=_round_bbox(bb),
                    source_type=SOURCE_SPAN,
                    source_index=span_global,
                    reading_order_hint=order,
                    font_name=sp.get("font") or None,
                    font_size=round(float(sp.get("size", 0)), 2) if sp.get("size") else None,
                    font_flags=int(sp.get("flags", 0)) if sp.get("flags") is not None else None,
                    line_index=li,
                    block_index=bi,
                    provenance={"pymupdf_block_no": b.get("number")},
                ))
                order += 1
                span_global += 1
    return obs


def _extract_word_observations(page, page_no: int, document_id: str) -> List[AtomicTextObservation]:
    """Extract observations from PyMuPDF 'words' layer.

    A word = a whitespace-delimited token with its own bbox. Natural atomic
    unit, but carries NO font/size/flags (those are span-layer only).
    """
    words = page.get_text("words")
    # words: (x0, y0, x1, y1, text, block_no, line_no, word_no)
    obs: List[AtomicTextObservation] = []
    for order, w in enumerate(words):
        x0, y0, x1, y1, text, block_no, line_no, word_no = w
        text = _strip_text(text)
        if not text:
            continue
        obs.append(AtomicTextObservation(
            observation_id=_make_obs_id(document_id, page_no, SOURCE_WORD, order),
            document_id=document_id,
            page_number=page_no,
            text=text,
            bbox=[round(float(x0), 2), round(float(y0), 2),
                  round(float(x1), 2), round(float(y1), 2)],
            source_type=SOURCE_WORD,
            source_index=order,
            reading_order_hint=order,
            font_name=None,
            font_size=None,
            font_flags=None,
            line_index=None,
            block_index=int(block_no),
            provenance={"pymupdf_line_no": int(line_no), "pymupdf_word_no": int(word_no)},
        ))
    return obs


def _extract_char_observations(page, page_no: int, document_id: str,
                               max_chars: Optional[int] = None) -> List[AtomicTextObservation]:
    """Extract observations from PyMuPDF 'rawdict' character layer.

    A character = a single glyph with its own bbox. Finest granularity.
    Used for Unicode-preservation validation. Optionally capped for large pages.
    """
    rd = page.get_text("rawdict")
    obs: List[AtomicTextObservation] = []
    order = 0
    char_global = 0
    for bi, b in enumerate(rd["blocks"]):
        if "lines" not in b:
            continue
        for li, line in enumerate(b["lines"]):
            for sp in line["spans"]:
                for ch in sp.get("chars", []):
                    c = ch.get("c", "")
                    if c.strip() == "":
                        continue
                    bb = ch.get("bbox")
                    obs.append(AtomicTextObservation(
                        observation_id=_make_obs_id(document_id, page_no, SOURCE_CHAR, char_global),
                        document_id=document_id,
                        page_number=page_no,
                        text=c,
                        bbox=_round_bbox(bb),
                        source_type=SOURCE_CHAR,
                        source_index=char_global,
                        reading_order_hint=order,
                        font_name=sp.get("font") or None,
                        font_size=round(float(sp.get("size", 0)), 2) if sp.get("size") else None,
                        font_flags=int(sp.get("flags", 0)) if sp.get("flags") is not None else None,
                        line_index=li,
                        block_index=bi,
                        provenance={},
                    ))
                    order += 1
                    char_global += 1
                    if max_chars is not None and char_global >= max_chars:
                        return obs
    return obs


def _extract_line_observations(page, page_no: int, document_id: str) -> List[AtomicTextObservation]:
    """Extract observations from PyMuPDF 'dict' line layer.

    A line = a visual row of spans. text = concatenation of its spans' text.
    """
    d = page.get_text("dict")
    obs: List[AtomicTextObservation] = []
    order = 0
    line_global = 0
    for bi, b in enumerate(d["blocks"]):
        if "lines" not in b:
            continue
        for li, line in enumerate(b["lines"]):
            text = _strip_text("".join(sp["text"] for sp in line["spans"]))
            if not text:
                continue
            bb = line.get("bbox")
            obs.append(AtomicTextObservation(
                observation_id=_make_obs_id(document_id, page_no, SOURCE_LINE, line_global),
                document_id=document_id,
                page_number=page_no,
                text=text,
                bbox=_round_bbox(bb),
                source_type=SOURCE_LINE,
                source_index=line_global,
                reading_order_hint=order,
                font_name=None,
                font_size=None,
                font_flags=None,
                line_index=li,
                block_index=bi,
                provenance={"span_count": len(line["spans"])},
            ))
            order += 1
            line_global += 1
    return obs


def _extract_block_observations(page, page_no: int, document_id: str) -> List[AtomicTextObservation]:
    """Extract observations from PyMuPDF 'blocks' layer (LEGACY / COMPARISON).

    This is the sole source of the Legacy CandidateSpanGenerator. Documented
    corruption layer (e.g. row 104: 'Position' x513 + 'Step' x77 merged into
    one block). Extracted here ONLY for provenance comparison — never used as
    the primary observation source.
    """
    blocks = page.get_text("blocks")
    # blocks: (x0, y0, x1, y1, text, block_no, block_type)
    obs: List[AtomicTextObservation] = []
    for order, b in enumerate(blocks):
        x0, y0, x1, y1, text, block_no, block_type = b
        if block_type != 0:  # skip non-text blocks (images/drawings)
            continue
        text = _strip_text(text)
        if not text:
            continue
        obs.append(AtomicTextObservation(
            observation_id=_make_obs_id(document_id, page_no, SOURCE_BLOCK, order),
            document_id=document_id,
            page_number=page_no,
            text=text,
            bbox=[round(float(x0), 2), round(float(y0), 2),
                  round(float(x1), 2), round(float(y1), 2)],
            source_type=SOURCE_BLOCK,
            source_index=order,
            reading_order_hint=order,
            font_name=None,
            font_size=None,
            font_flags=None,
            line_index=None,
            block_index=int(block_no),
            provenance={"block_type": int(block_type), "line_count": text.count("\n") + 1},
        ))
    return obs


# ── Public API ────────────────────────────────────────────────────────────

def extract_page_observations(page, page_no: int, document_id: str,
                              layers: Optional[List[str]] = None,
                              max_chars: Optional[int] = None
                              ) -> List[AtomicTextObservation]:
    """Extract atomic text observations from one PDF page across layers.

    Args:
        page: fitz.Page (caller owns the doc; extractor never opens/closes it).
        page_no: 1-based page number.
        document_id: source document identifier (caller-supplied fact).
        layers: which layers to extract. None = default set [span, word].
                Full comparison set = [character, word, span, line, block].
        max_chars: cap on character-layer count (None = no cap).

    Returns:
        List of AtomicTextObservation (JSON-serializable via .to_dict()).
    """
    if layers is None:
        layers = [SOURCE_SPAN, SOURCE_WORD]
    obs: List[AtomicTextObservation] = []
    if SOURCE_SPAN in layers:
        obs += _extract_span_observations(page, page_no, document_id)
    if SOURCE_WORD in layers:
        obs += _extract_word_observations(page, page_no, document_id)
    if SOURCE_LINE in layers:
        obs += _extract_line_observations(page, page_no, document_id)
    if SOURCE_BLOCK in layers:
        obs += _extract_block_observations(page, page_no, document_id)
    if SOURCE_CHAR in layers:
        obs += _extract_char_observations(page, page_no, document_id, max_chars=max_chars)
    return obs


def extract_pdf_observations(pdf_path: str, document_id: str,
                             pages: Optional[List[int]] = None,
                             layers: Optional[List[str]] = None,
                             max_chars: Optional[int] = None
                             ) -> List[AtomicTextObservation]:
    """Extract atomic text observations from a PDF (read-only).

    Opens and closes the document internally. Does NOT touch any frozen object.
    """
    doc = fitz.open(pdf_path)
    try:
        target = pages if pages is not None else list(range(1, doc.page_count + 1))
        all_obs: List[AtomicTextObservation] = []
        for pno in target:
            if pno < 1 or pno > doc.page_count:
                continue
            page = doc[pno - 1]
            all_obs += extract_page_observations(
                page, pno, document_id, layers=layers, max_chars=max_chars)
        return all_obs
    finally:
        doc.close()


def observations_to_json(obs: List[AtomicTextObservation], indent: int = 1) -> str:
    """Serialize observations to a stable JSON string."""
    return json.dumps([o.to_dict() for o in obs], ensure_ascii=False, indent=indent)


def pymupdf_version() -> str:
    """Return the PyMuPDF version used for extraction (provenance)."""
    return _PYMUPDF_VERSION


__all__ = [
    "AtomicTextObservation",
    "extract_page_observations",
    "extract_pdf_observations",
    "observations_to_json",
    "pymupdf_version",
    "SOURCE_CHAR", "SOURCE_WORD", "SOURCE_SPAN", "SOURCE_LINE", "SOURCE_BLOCK",
]
