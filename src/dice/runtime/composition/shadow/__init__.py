"""
Phase 6.1: Shadow Runtime Layer — Read-Only Composition Observation

======================================================================
STATUS: L1_IMPLEMENTING — Observer + Storage logic only.
======================================================================

Shadow Runtime is a read-only sidecar that observes production Runtime
outputs, simulates composition candidates, validates them, and generates
traces — but NEVER executes, activates, or modifies production state.

Core Principle:
    Shadow = Read-only Observation + Simulation + Validation + Trace
    Shadow ≠ Execution
    Shadow ≠ Activation
    Shadow ≠ Production
    Shadow ≠ Registry Modification

L1 (Phase 6.1-L1): Observer + Shadow Storage
    ✅ ShadowObserver.capture_observation()
    ✅ ShadowObserver.capture_batch()
    ✅ ShadowStorage.store() / load() / list_records() / clear()
    ✅ Data Models (7 entities)

L2-L4 (Phase 6.1-L2/L3/L4): NOT YET IMPLEMENTED
    ⏸️ CompositionSimulator
    ⏸️ ShadowValidator
    ⏸️ ShadowTracer
    ⏸️ ShadowMetrics
    ⏸️ GovernanceChecker

Frozen Baseline:
    Registry: 21 🔒
    Runtime Layer 1-8: unchanged 🔒
    Production Execution: false 🛑
"""

__version__ = "6.1.0-l1"
__status__ = "L1_IMPLEMENTING"
__layer__ = 9

# ── L1: Observer + Storage (implemented) ──
from .shadow_runtime import ShadowObserver
from .shadow_storage import ShadowStorage

# ── Models (all implemented) ──
from .models import (
    ShadowObservation,
    ShadowCompositionCandidate,
    ShadowExecutionSimulation,
    ShadowValidationResult,
    ValidationDimension,
    ValidationStatus,
    DimensionResult,
    Violation,
    ShadowTraceRecord,
    TracePhase,
    TraceStatus,
    StageRecord,
    ShadowGovernanceCheck,
    GovernanceStatus,
    ShadowMetricRecord,
)

__all__ = [
    # L1: Runtime
    "ShadowObserver",
    "ShadowStorage",
    # Models
    "ShadowObservation",
    "ShadowCompositionCandidate",
    "ShadowExecutionSimulation",
    "ShadowValidationResult",
    "ValidationDimension",
    "ValidationStatus",
    "DimensionResult",
    "Violation",
    "ShadowTraceRecord",
    "TracePhase",
    "TraceStatus",
    "StageRecord",
    "ShadowGovernanceCheck",
    "GovernanceStatus",
    "ShadowMetricRecord",
]