"""
Capability Runtime — Phase 2 Step 4.

Shadow adapter for Evidence → Capability integration.
Maintains the Evidence Runtime / Capability Runtime orthogonality:
- Evidence Runtime answers: "What evidence exists in the document?"
- Capability Runtime answers: "Which capability should handle this evidence?"

Package contents:
    shadow_adapter.py — CapabilityRuntimeShadowAdapter + CapabilityActivationTrace
"""

from dice.runtime.capability.shadow_adapter import (
    CapabilityRuntimeShadowAdapter,
    CapabilityActivationShadowResult,
    CapabilityActivationTrace,
    EVIDENCE_TO_SIGNALS,
)

__all__ = [
    "CapabilityRuntimeShadowAdapter",
    "CapabilityActivationShadowResult",
    "CapabilityActivationTrace",
    "EVIDENCE_TO_SIGNALS",
]