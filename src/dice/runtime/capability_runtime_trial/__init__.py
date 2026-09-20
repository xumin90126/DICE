"""Phase 16.20: Capability Runtime Trial package (Declaration-driven Runner).

Capability Runtime Trial — Declaration-driven Boundary Evaluation.

This package hosts the minimal, Human-driven, read-only verification that a
Registered Capability can be consumed through the Capability Runtime boundary
(Phase 16.14) WITHOUT acquiring any authority. The boundary evaluation is
Declaration-driven (Phase 16.20): capability-specific boundary facts live in
the Capability Definition's boundary serialization, read as a frozen
projection — never hardcoded in this package.

This __init__.py is a PACKAGE-EXPORT-ONLY module. Its sole responsibility is
to re-export the data-model contracts, the Observation output model, the
declaration-driven boundary evaluation, and the Trial Runner so Human-driven
callers can import them cleanly.

EXPLICIT NON-GOALS:
    - NO automatic capability registration
    - NO import of bootstrap / registry
    - NO registry mutation
    - NO side effects on import
    - NO selection / routing / planning / execution / decision / retry /
      fallback / score / ranking
    - NO capability-specific semantic identifier in the evaluation path

Importing this package performs ZERO mutation, ZERO registration, ZERO
authority acquisition. It only binds names.
"""

from .models import (
    BoundaryEvaluationReport,
    BoundaryStatus,
    CapabilityRuntimeRequest,
)
from .observation import (
    CapabilityRuntimeObservation,
)
from .boundary_evaluation import (
    BoundaryDeclarationReader,
    CapabilityBoundaryProjection,
    GenericBoundaryEvaluator,
)
from .trial_runner import (
    CapabilityRuntimeTrialRunner,
)

__all__ = [
    # Request & boundary models (Step 1 Skeleton)
    "BoundaryStatus",
    "CapabilityRuntimeRequest",
    "BoundaryEvaluationReport",
    # Observation output model (Step 2 Component Wiring)
    "CapabilityRuntimeObservation",
    # Declaration-driven boundary evaluation (Phase 16.20)
    "CapabilityBoundaryProjection",
    "BoundaryDeclarationReader",
    "GenericBoundaryEvaluator",
    # Trial Runner (Declaration-driven, Phase 16.20)
    "CapabilityRuntimeTrialRunner",
]
