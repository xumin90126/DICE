"""
Phase 6.1-L2.1: Simulation Data Models — DESIGN_ONLY.

All models carry shadow_marked=True and origin="composition_shadow_storage".
No connection to Runtime Storage, Capability Registry, or Production Database.
"""

from .simulation_request import SimulationRequest
from .simulation_scenario import SimulationScenario
from .simulation_result import SimulationResult
from .simulation_trace_record import SimulationTraceRecord
from .simulation_snapshot import SimulationSnapshot

__all__ = [
    "SimulationRequest",
    "SimulationScenario",
    "SimulationResult",
    "SimulationTraceRecord",
    "SimulationSnapshot",
]