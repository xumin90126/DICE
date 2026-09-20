"""
P3 Style — Centralized style threshold configuration.

ALL style thresholds live here. No function may hardcode a threshold
in an if/else. Thresholds describe numeric tolerances only (e.g. when are
two font sizes "the same size"?). They do NOT encode semantic judgments
(no "heading size", no "body size", no "caption size").
"""
from __future__ import annotations

from dataclasses import dataclass
import dataclasses


# ── Font flags bitmask definitions ────────────────────────────────────────
# These bit positions are the PyMuPDF span['flags'] characteristic bits.
# Verified empirically against the test corpus (PyMuPDF 1.26.5):
#   Arial-BoldMT     -> flags=16  (bit4 set)   bold font, confirmed
#   Arial-ItalicMT   -> flags=2   (bit1 set)   italic font, confirmed
#   ArialMT          -> flags=0                regular, confirmed
#   PalatinoLinotype-Bold -> flags=20 (bit4+bit2)
#   SFTT1095 (mono)  -> flags=12  (bit3+bit2)
#   CMR8 (superscript-sized) -> flags=5 (bit0+bit2)
# This mapping is documented, not memorized — see p3 flag audit.

FLAG_SUPERSCRIPT = 1    # bit 0
FLAG_ITALIC = 2         # bit 1
FLAG_SERIFED = 4        # bit 2
FLAG_MONOSPACED = 8     # bit 3
FLAG_BOLD = 16          # bit 4

# Bits beyond 4 are not reliably interpreted in PyMuPDF 1.26.5 for these
# documents; they are preserved as raw_flags but not decoded into named facts.
KNOWN_FLAG_BITS = {
    FLAG_SUPERSCRIPT: "superscript",
    FLAG_ITALIC: "italic",
    FLAG_SERIFED: "serifed",
    FLAG_MONOSPACED: "monospaced",
    FLAG_BOLD: "bold",
}


@dataclass(frozen=True)
class StyleConfig:
    """Centralized style thresholds. Immutable."""

    # When are two font sizes "the same" (for style comparison)?
    font_size_equality_tolerance: float = 0.15
    """Two font_size values are same_font_size if abs diff <= this (pt)."""

    # Font size normalization: round to this many decimals for normalized_font_size
    font_size_normalization_decimals: int = 1

    # Font name normalization: strip these suffixes/patterns for font_family
    # (deterministic string ops only, no semantic guessing)
    # Ordered: compound PyMuPDF variants first, then single suffixes.
    font_family_suffix_patterns: tuple = (
        "-BoldItalic", "-BoldOblique", "-BoldMT",
        "-ItalicMT", "-ObliqueMT",
        "-Bold", "-bold", "-Italic", "-italic", "-Oblique", "-oblique",
        "-Regular", "-Roman", "-MT",
        "-Black", "-Heavy", "-Light", "-Medium",
    )

    # Whether to cross-validate font_name against flags.
    # If True, font_name bold/italic hints are recorded in provenance but
    # the authoritative bold/italic comes from flags ONLY.
    cross_validate_font_name: bool = True

    def with_overrides(self, **kwargs) -> "StyleConfig":
        return dataclasses.replace(self, **kwargs)


DEFAULT_CONFIG = StyleConfig()


def to_dict(cfg: StyleConfig) -> dict:
    return dataclasses.asdict(cfg)
