"""
Phase 6.0: Composition Planner — package init

STATUS: DESIGN_ONLY
"""

from .composition_planner import (
    CompositionPlanner,
    CompositionStrategy,
    CompositionRule,
    CompositeCapabilityProposal,
    PlannerOutput,
)

__all__ = [
    "CompositionPlanner",
    "CompositionStrategy",
    "CompositionRule",
    "CompositeCapabilityProposal",
    "PlannerOutput",
]