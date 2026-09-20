"""P7.1 StructureHypothesis — exported public surface."""
from __future__ import annotations

from .structure_config import (
    StructureConfig, DEFAULT_CONFIG, ALL_HYPOTHESIS_TYPES,
    ALL_RELATION_TYPES, ALL_STATUSES, ALL_CONFIDENCES, BLOCKED_TYPES,
    HYP_HEADING, HYP_PARAGRAPH, HYP_SECTION, HYP_LIST,
    HYP_HEADER, HYP_FOOTER, HYP_MULTICOL,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW,
    CONFIDENCE_UNKNOWN, CONFIDENCE_AMBIGUOUS,
)
from .structure_relation import StructuralRelation, min_confidence, _relation_id
from .structure_hypothesis import StructureHypothesis, PageStructureBundle, _hypothesis_id
from .structure_engine import (
    compute_page_structure,
    compute_cross_page_repeats,
)

__all__ = [
    "StructureConfig", "DEFAULT_CONFIG",
    "ALL_HYPOTHESIS_TYPES", "ALL_RELATION_TYPES", "ALL_STATUSES", "ALL_CONFIDENCES", "BLOCKED_TYPES",
    "HYP_HEADING", "HYP_PARAGRAPH", "HYP_SECTION", "HYP_LIST",
    "HYP_HEADER", "HYP_FOOTER", "HYP_MULTICOL",
    "CONFIDENCE_HIGH", "CONFIDENCE_MEDIUM", "CONFIDENCE_LOW",
    "CONFIDENCE_UNKNOWN", "CONFIDENCE_AMBIGUOUS",
    "StructuralRelation", "min_confidence", "_relation_id",
    "StructureHypothesis", "PageStructureBundle", "_hypothesis_id",
    "compute_page_structure", "compute_cross_page_repeats",
]
