"""Execution Runtime — Shadow Adapter (Phase 2 Step 5)."""

from dice.runtime.execution.shadow_adapter import (
    ExecutionRuntimeShadowAdapter,
    ExecutionPlanShadowResult,
    ExecutionShadowBatchResult,
    CAPABILITY_ACTION_MAP,
    load_capability_activation_results,
    load_shadow_evidence,
)

__all__ = [
    "ExecutionRuntimeShadowAdapter",
    "ExecutionPlanShadowResult",
    "ExecutionShadowBatchResult",
    "CAPABILITY_ACTION_MAP",
    "load_capability_activation_results",
    "load_shadow_evidence",
]