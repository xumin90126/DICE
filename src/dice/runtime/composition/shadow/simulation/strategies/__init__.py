"""
Phase 6.1-L2.1: Composition Strategies — DESIGN_ONLY Skeleton.

This package contains the CompositionMock strategy components used by the
Simulation Engine to generate hypothetical CompositionCandidate objects.

Modules:
    composition_mock: CompositionMock + 3 strategies (Simple/Priority/Dependency)
                      + CompositionCandidate data model

All strategy methods raise NotImplementedError — no simulation behavior is
implemented at L2.1. This is a design-only skeleton.

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True (mock output is never applied)
"""

from .composition_mock import (
    CompositionMock,
    CompositionStrategy,
    CompositionCandidate,
    SimpleStrategy,
    PriorityStrategy,
    DependencyStrategy,
)

__all__ = [
    "CompositionMock",
    "CompositionStrategy",
    "CompositionCandidate",
    "SimpleStrategy",
    "PriorityStrategy",
    "DependencyStrategy",
]
