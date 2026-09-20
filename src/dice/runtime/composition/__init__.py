"""
Phase 6.0: Layer 9 — Capability Composition Layer (SKELETON)

======================================================================
STATUS: DESIGN_ONLY — no runtime logic, no production execution.
======================================================================

This module provides the architecture skeleton for Capability Composition,
the 9th governance layer in the Capability OS architecture.

Layers 1-8 (FROZEN):
    L1: Evidence Runtime
    L2: Capability Runtime
    L3: Execution Runtime
    L4: Approval Layer
    L5: Activation Boundary
    L6: Production Guardrail
    L7: Permission Check
    L8: Trial Runtime

Layer 9 (this module — SKELETON):
    Dependency Graph → Composition Planner → Validation Engine → Composite Governance
                                                            └→ Composite Execution Plan

Key Design Principle:
    Layer 9 NEVER bypasses Layers 1-8. All composite actions must pass
    through the full governance chain: Approval → Activation → Guardrail → Permission.

Phase 6.0 Deliverables (current):
    ✅ Directory structure
    ✅ Interface definitions
    ✅ Data model schemas (dataclass placeholders)
    ✅ NOT_IMPLEMENTED stubs
    ❌ No runtime logic
    ❌ No composition execution
    ❌ No production activation

Phase 6.1+ (future):
    ⏸️ Shadow Composition Runtime
    ⏸️ Controlled Composite Trial
    ⏸️ Limited Activation
    ⏸️ Production Readiness
"""

__version__ = "6.0.0-skeleton"
__status__ = "DESIGN_ONLY"
__layer__ = 9

# Sub-modules (all DESIGN_ONLY)
from .graph import CapabilityDependencyGraph
from .planner import CompositionPlanner
from .execution import CompositeExecutionPlan
from .validation import CompositionValidationEngine
from .governance import CompositeGovernance

__all__ = [
    "CapabilityDependencyGraph",
    "CompositionPlanner",
    "CompositeExecutionPlan",
    "CompositionValidationEngine",
    "CompositeGovernance",
]