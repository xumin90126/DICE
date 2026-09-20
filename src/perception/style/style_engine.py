"""
P3 Style — computation engine.

Extracts pure style facts from P1 AtomicTextObservation.
NO semantic classification. Bold/italic come from flags bits (authoritative),
NOT from font-name guessing or size/position heuristics.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from .style_config import (
    StyleConfig, DEFAULT_CONFIG,
    FLAG_BOLD, FLAG_ITALIC, FLAG_SUPERSCRIPT, FLAG_SERIFED, FLAG_MONOSPACED,
    KNOWN_FLAG_BITS,
)
from .style_observation import StyleObservation, StyleComparison


# ── Flag decoding (authoritative — from bits, not font name) ──────────────

def decode_flags(raw_flags: Optional[int], cfg: StyleConfig = DEFAULT_CONFIG) -> Dict[str, Optional[bool]]:
    """Decode raw font flags bitmask into named style facts.

    Authoritative source: the flag BITS, not font-name guessing.
    Returns null for facts not reliably encoded in PyMuPDF 1.26.5 span flags
    (underline, subscript).
    """
    if raw_flags is None:
        return {
            "bold": None, "italic": None, "underline": None,
            "superscript": None, "subscript": None,
        }
    return {
        "bold": bool(raw_flags & FLAG_BOLD),
        "italic": bool(raw_flags & FLAG_ITALIC),
        # underline: PyMuPDF 1.26.5 span flags do NOT encode underline.
        # (underline is a text decoration, not a font characteristic.)
        "underline": None,
        "superscript": bool(raw_flags & FLAG_SUPERSCRIPT),
        # subscript: PyMuPDF 1.26.5 does not reliably encode subscript in span flags.
        "subscript": None,
    }


# ── Font family normalization (deterministic string ops) ──────────────────

def normalize_font_family(font_name: Optional[str], cfg: StyleConfig = DEFAULT_CONFIG) -> Optional[str]:
    """Normalize font name to family via deterministic suffix stripping.

    No semantic guessing. Just removes known style suffixes to derive a
    family name. Returns null if font_name is null.
    """
    if font_name is None:
        return None
    fam = font_name
    # Iteratively strip known style suffixes (handles compounds like
    # "Arial-BoldMT" -> "Arial-Bold" -> "Arial", "PalatinoLinotype-Bold" -> "PalatinoLinotype")
    changed = True
    while changed:
        changed = False
        for suffix in sorted(cfg.font_family_suffix_patterns, key=len, reverse=True):
            if fam.endswith(suffix) and len(fam) > len(suffix):
                fam = fam[: -len(suffix)]
                changed = True
    # If nothing left after stripping, return original
    return fam if fam else font_name


# ── Style signature ───────────────────────────────────────────────────────

def compute_style_signature(font_family: Optional[str],
                            normalized_size: Optional[float],
                            bold: Optional[bool],
                            italic: Optional[bool],
                            underline: Optional[bool],
                            superscript: Optional[bool],
                            subscript: Optional[bool]) -> str:
    """Deterministic style signature. No text/bbox/semantics.

    Format: "family|size|b|i|u|sup|sub"
    null values rendered as '-' for stability.
    """
    def _v(x) -> str:
        if x is None:
            return "-"
        if isinstance(x, bool):
            return "1" if x else "0"
        return str(x)
    return "|".join([
        _v(font_family),
        _v(normalized_size),
        _v(bold),
        _v(italic),
        _v(underline),
        _v(superscript),
        _v(subscript),
    ])


# ── Style observation extraction ──────────────────────────────────────────

def extract_style(obs, cfg: StyleConfig = DEFAULT_CONFIG) -> StyleObservation:
    """Extract a StyleObservation from one P1 AtomicTextObservation dict.

    `obs` must have: observation_id, document_id, page_number, source_type,
    and (from span/char layers) font_name, font_size, font_flags in its fields.
    Word/line/block layer observations lack font info → those fields are null.
    """
    font_name = obs.get("font_name")
    raw_size = obs.get("font_size")
    raw_flags = obs.get("font_flags")

    font_family = normalize_font_family(font_name, cfg)
    normalized_size = (round(float(raw_size), cfg.font_size_normalization_decimals)
                       if raw_size is not None else None)
    decoded = decode_flags(raw_flags, cfg)

    sig = compute_style_signature(
        font_family, normalized_size,
        decoded["bold"], decoded["italic"], decoded["underline"],
        decoded["superscript"], decoded["subscript"],
    )

    # cross-validation provenance (non-authoritative, recorded only)
    xval = {}
    if cfg.cross_validate_font_name and font_name:
        name_hints = []
        if any(x in font_name for x in ("Bold", "bold")):
            name_hints.append("name_suggests_bold")
        if any(x in font_name for x in ("Italic", "Oblique", "italic", "oblique")):
            name_hints.append("name_suggests_italic")
        if any(x in font_name for x in ("Black", "Heavy")):
            name_hints.append("name_suggests_heavy_weight")
        if name_hints:
            xval["font_name_hints"] = name_hints
            # flag-vs-name discrepancy note (fact, not a correction)
            if decoded["bold"] is False and any("bold" in h or "heavy" in h for h in name_hints):
                xval["flag_name_bold_discrepancy"] = True

    return StyleObservation(
        observation_id=_style_obs_id(obs["observation_id"]),
        document_id=obs["document_id"],
        page_number=obs["page_number"],
        source_observation_id=obs["observation_id"],
        source_type=obs.get("source_type", ""),
        font_name=font_name,
        font_family=font_family,
        raw_font_size=raw_size,
        normalized_font_size=normalized_size,
        raw_font_flags=raw_flags,
        bold=decoded["bold"],
        italic=decoded["italic"],
        underline=decoded["underline"],
        superscript=decoded["superscript"],
        subscript=decoded["subscript"],
        style_signature=sig,
        provenance={
            "config": "StyleConfig",
            "source_layer": obs.get("source_type"),
            "source_index": obs.get("source_index"),
            **xval,
        },
    )


def _style_obs_id(source_obs_id: str) -> str:
    return hashlib.sha1(f"style|{source_obs_id}".encode("utf-8")).hexdigest()[:16]


# ── Style comparison ──────────────────────────────────────────────────────

def compare_styles(a: StyleObservation, b: StyleObservation,
                   cfg: StyleConfig = DEFAULT_CONFIG) -> StyleComparison:
    """Deterministic style comparison of A vs B. Pure facts, no semantics."""
    same_font = (a.font_name is not None and b.font_name is not None
                 and a.font_name == b.font_name)
    same_family = (a.font_family is not None and b.font_family is not None
                   and a.font_family == b.font_family)
    same_size = (a.normalized_font_size is not None and b.normalized_font_size is not None
                 and abs(a.normalized_font_size - b.normalized_font_size)
                     <= cfg.font_size_equality_tolerance)
    same_bold = _same_nullable_bool(a.bold, b.bold)
    same_italic = _same_nullable_bool(a.italic, b.italic)
    same_underline = _same_nullable_bool(a.underline, b.underline)
    same_sig = a.style_signature == b.style_signature

    size_delta = None
    if a.normalized_font_size is not None and b.normalized_font_size is not None:
        size_delta = round(a.normalized_font_size - b.normalized_font_size, 2)

    # aggregate difference (fact, not semantic)
    if same_sig:
        diff = "identical"
    elif (same_font or same_family) and same_bold and same_italic and not same_size:
        diff = "size_diff"
    elif not (same_font or same_family):
        diff = "font_diff"
    elif same_family and not (same_bold and same_italic):
        diff = "style_diff"
    elif a.font_name is None or b.font_name is None:
        diff = "incomparable"
    else:
        diff = "style_diff"

    return StyleComparison(
        comparison_id=hashlib.sha1(
            f"{a.observation_id}>{b.observation_id}".encode()).hexdigest()[:16],
        document_id=a.document_id,
        page_number=a.page_number,
        observation_a_id=a.observation_id,
        observation_b_id=b.observation_id,
        same_font=same_font,
        same_font_family=same_family,
        same_font_size=same_size,
        same_bold=same_bold,
        same_italic=same_italic,
        same_underline=same_underline,
        same_style_signature=same_sig,
        font_size_delta=size_delta,
        style_difference=diff,
        provenance={"config": "StyleConfig"},
    )


def _same_nullable_bool(a: Optional[bool], b: Optional[bool]) -> bool:
    """True if both are equal (including both None). False if differ. False if one is None."""
    if a is None or b is None:
        return a is None and b is None
    return a == b


def extract_page_styles(observations, cfg: StyleConfig = DEFAULT_CONFIG) -> List[StyleObservation]:
    """Extract style observations for all observations on a page."""
    return [extract_style(o, cfg) for o in observations]


__all__ = [
    "decode_flags", "normalize_font_family", "compute_style_signature",
    "extract_style", "compare_styles", "extract_page_styles",
]
