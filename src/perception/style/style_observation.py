"""
P3 Style — StyleObservation schema.

Pure style facts extracted from P1 AtomicTextObservation provenance.
NO semantic classification (no is_heading / is_title / is_body / is_caption /
is_table_header / heading_level / semantic_role / region_type / column_id).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StyleObservation:
    """Style facts for one AtomicTextObservation. Pure facts, no semantics."""

    observation_id: str
    document_id: str
    page_number: int
    source_observation_id: str     # P1 AtomicTextObservation.observation_id
    source_type: str               # P1 source layer (span/word/etc.)

    # ── Font facts (from P1 provenance / span layer) ──
    font_name: Optional[str]       # raw font name (null if P1 source had none, e.g. word layer)
    font_family: Optional[str]     # normalized family (deterministic suffix strip; null if no font_name)
    raw_font_size: Optional[float] # original size value (null if unavailable)
    normalized_font_size: Optional[float]  # rounded to config decimals (null if no raw_font_size)
    raw_font_flags: Optional[int]  # original flags bitmask (null if unavailable)

    # ── Decoded style facts (from flags bits — authoritative) ──
    bold: Optional[bool]           # flags bit 4; null if flags unavailable
    italic: Optional[bool]         # flags bit 1; null if flags unavailable
    underline: Optional[bool]      # null — PyMuPDF span flags do not encode underline in 1.26.5
    superscript: Optional[bool]    # flags bit 0; null if flags unavailable
    subscript: Optional[bool]      # null — not reliably encoded in PyMuPDF 1.26.5 span flags

    # ── Style signature (deterministic, no text/bbox/semantics) ──
    style_signature: str           # "font_family|size|bold|italic|underline|superscript|subscript"

    # ── Provenance ──
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StyleComparison:
    """Deterministic style comparison between two observations. Pure facts."""

    comparison_id: str
    document_id: str
    page_number: int

    observation_a_id: str
    observation_b_id: str

    # same-style facts (booleans)
    same_font: bool
    same_font_family: bool
    same_font_size: bool
    same_bold: bool
    same_italic: bool
    same_underline: bool
    same_style_signature: bool

    # numeric delta
    font_size_delta: Optional[float]   # a.size - b.size (null if either missing)

    # aggregate
    style_difference: str   # "identical" | "size_diff" | "font_diff" | "style_diff" | "incomparable"

    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
