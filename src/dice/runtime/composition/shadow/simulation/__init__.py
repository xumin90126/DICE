"""
Phase 6.1-L2.1: Simulation Layer — Simulation Core Skeleton (DESIGN_ONLY).

This package contains the skeleton interfaces for the Simulation Layer.
All methods raise NotImplementedError — no logic is implemented at L2.1.

Modules:
    simulation_engine: Orchestrates simulation lifecycle
    scenario_manager: Creates and validates simulation scenarios
    result_builder:    Builds SimulationResult from engine output
    trace_adapter:     Creates SimulationTraceRecord + EvidenceSnapshot
    storage_adapter:   Persists/loads simulation artifacts
    strategies:        CompositionMock (Simple/Priority/Dependency strategies)

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True (mock output is never applied)
"""

from .simulation_engine import SimulationEngine, SimulationHandle
from .scenario_manager import ScenarioManager
from .result_builder import ResultBuilder
from .trace_adapter import TraceAdapter, SimulationEvidenceSnapshot
from .storage_adapter import StorageAdapter
from .strategies import (
    CompositionMock,
    CompositionStrategy,
    CompositionCandidate,
    SimpleStrategy,
    PriorityStrategy,
    DependencyStrategy,
)

__all__ = [
    "SimulationEngine",
    "SimulationHandle",
    "ScenarioManager",
    "ResultBuilder",
    "TraceAdapter",
    "SimulationEvidenceSnapshot",
    "StorageAdapter",
    "CompositionMock",
    "CompositionStrategy",
    "CompositionCandidate",
    "SimpleStrategy",
    "PriorityStrategy",
    "DependencyStrategy",
]
