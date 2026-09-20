"""
Phase 6.1-L2.2: Validation Data Models — DESIGN_ONLY.

All models carry shadow_marked=True, origin="composition_shadow_storage",
and is_hypothetical=True. No connection to Runtime Storage, Capability
Registry, or Production Database.
"""

from .validation_request import ValidationRequest, ValidationConfig, ValidationStatus
from .validation_rule import ValidationRule, RuleType, RuleSeverity
from .validation_evidence import ValidationEvidence
from .validation_result import ValidationResult, CheckResult
from .validation_report import (
    ValidationReport,
    ReportSummary,
    EvidenceReference,
)

__all__ = [
    "ValidationRequest",
    "ValidationConfig",
    "ValidationStatus",
    "ValidationRule",
    "RuleType",
    "RuleSeverity",
    "ValidationEvidence",
    "ValidationResult",
    "CheckResult",
    "ValidationReport",
    "ReportSummary",
    "EvidenceReference",
]
