"""
Phase 6.1-L2.2: Validation Layer — Shadow Validation Skeleton (DESIGN_ONLY).

This package contains the skeleton interfaces for the Shadow Validation
Layer. All methods raise NotImplementedError — no logic is implemented
at L2.2 skeleton stage.

Modules:
    validation_engine:          Orchestrates validation flow
    evidence_collector:         Read-only evidence collection from L2.1
    validation_contract:        Contract-driven input/output validation
    validation_executor:        Read-only rule execution (observation only)
    validation_report_builder:  Self-contained report assembly

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True (observations are never applied)
"""

from .validation_engine import ValidationEngine
from .evidence_collector import EvidenceCollector
from .validation_contract import ValidationContract
from .validation_executor import ValidationExecutor
from .validation_report_builder import ValidationReportBuilder

__all__ = [
    "ValidationEngine",
    "EvidenceCollector",
    "ValidationContract",
    "ValidationExecutor",
    "ValidationReportBuilder",
]
