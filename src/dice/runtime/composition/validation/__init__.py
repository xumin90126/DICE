"""
Phase 6.0: Composition Validation Engine — package init

STATUS: DESIGN_ONLY
"""

from .composition_validator import (
    CompositionValidationEngine,
    CompositionValidationResult,
    ValidationStage,
    ValidationDimension,
    StageCheckResult,
    ConflictRecord,
    RiskAssessment,
)

__all__ = [
    "CompositionValidationEngine",
    "CompositionValidationResult",
    "ValidationStage",
    "ValidationDimension",
    "StageCheckResult",
    "ConflictRecord",
    "RiskAssessment",
]