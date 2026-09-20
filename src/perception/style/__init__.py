# Style observations (P3)
from .style_config import (
    StyleConfig, DEFAULT_CONFIG, to_dict,
    FLAG_BOLD, FLAG_ITALIC, FLAG_SUPERSCRIPT, FLAG_SERIFED, FLAG_MONOSPACED,
    KNOWN_FLAG_BITS,
)
from .style_observation import StyleObservation, StyleComparison
from .style_engine import (
    decode_flags, normalize_font_family, compute_style_signature,
    extract_style, compare_styles, extract_page_styles,
)
