"""
Phase 30: CAP-TABLE-CELL-SEGMENT — L1 Structural Table Capability (package).

This __init__.py is a PACKAGE-EXPORT-ONLY module. Its sole responsibility is
to re-export the cell observation model and the deterministic segmenter so
downstream (Human-driven) callers can import them cleanly.

EXPLICIT NON-GOALS (Phase 30 boundary):
    - NO automatic capability registration
    - NO import of bootstrap / registry / capability_loader
    - NO registry modification
    - NO runtime wiring
    - NO automatic invocation
    - NO side effects on import

Importing this package performs ZERO mutation, ZERO registration, ZERO
authority acquisition. It only binds names for the structural cell model
and segmenter.
"""

from .models import (
    SegmentationResult,
    TableCellObservation,
)
from .segmenter import (
    TableCellSegmenter,
)

__all__ = [
    "TableCellObservation",
    "SegmentationResult",
    "TableCellSegmenter",
]
