"""
Shadow Evidence Runtime Layer — Phase 2 Step 2.

Pilot 1 validated architecture, migrated to production as SHADOW mode.
Reads documents in parallel with the existing pipeline, outputs EvidenceResult
without affecting Capability Matching, Execution Runtime, or Evolution.

Shadow Mode:
    - No production output modification
    - No Capability Matching influence
    - No Execution Runtime interference
    - No Evolution modification
    - Independent evidence extraction + validation

Architecture:
    Document (text)
        │
        ├──→ Existing Pipeline (unchanged)
        │
        └──→ Shadow Evidence Runtime
                │
                ├── CombinedEvidenceExtractor
                ├── SpanRoleValidator
                ├── EvidenceTypeClassifier
                └── CapabilityIndependentValidator
                        │
                        ▼
                EvidenceResult[] → shadow_evidence.json
"""

from dice.runtime.evidence.shadow_adapter import (
    EvidenceRuntimeShadowAdapter,
    ShadowEvidenceResult,
    ShadowRunResult,
)
from dice.runtime.evidence.shadow_evaluator import (
    ShadowComparisonEngine,
    ComparisonReport,
    GateResult,
)
from dice.runtime.evidence.evolution_adapter import (
    EvidenceEvolutionAdapter,
    ShadowEvolutionCandidate,
    ShadowEvolutionMetrics,
    BeforeAfterSimulation,
    ShadowProposalType,
    load_shadow_evidence,
)

__all__ = [
    # Shadow Runtime (Phase 2 Step 2)
    "EvidenceRuntimeShadowAdapter",
    "ShadowEvidenceResult",
    "ShadowRunResult",
    "ShadowComparisonEngine",
    "ComparisonReport",
    "GateResult",
    # Evolution Adapter (Phase 2 Step 3)
    "EvidenceEvolutionAdapter",
    "ShadowEvolutionCandidate",
    "ShadowEvolutionMetrics",
    "BeforeAfterSimulation",
    "ShadowProposalType",
    "load_shadow_evidence",
]