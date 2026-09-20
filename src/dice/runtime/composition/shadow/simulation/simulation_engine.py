"""
Phase 6.1-L2.1: SimulationEngine — Simulation Logic (Phase F implemented).

Responsibility:
    Orchestrate the simulation lifecycle — create, run, and collect results.
    The engine coordinates ScenarioManager, CompositionMock, TraceAdapter,
    ResultBuilder, and StorageAdapter inside the Shadow Simulation namespace.

    This is pure shadow orchestration — it NEVER executes a capability,
    NEVER reads the Capability Registry, and NEVER produces a production or
    runtime result. All outputs are hypothetical shadow artifacts.

Input:
    - SimulationRequest: User intent and scope definition

Output:
    - SimulationHandle (from create_simulation)
    - SimulationResult (from collect_result, shadow_marked=True)

Forbidden:
    - ❌ No Capability Registry access
    - ❌ No Runtime 1-8 modification
    - ❌ No production execution
    - ❌ No activation paths
    - ❌ No composition execution (Phase 6.2)
    - ❌ No governance / metrics decision logic

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True (results are never applied)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import SimulationRequest, SimulationResult, SimulationScenario


class SimulationEngine:
    """Orchestrate simulation lifecycle (Shadow-only, Phase F implemented)."""

    def __init__(self) -> None:
        self._initialized: bool = False

        # ── Lazy imports break the circular dependency: trace_adapter imports
        #    SimulationHandle from this module, so the engine defers its adapter
        #    imports until after this module finishes loading. ──
        from .scenario_manager import ScenarioManager
        from .result_builder import ResultBuilder
        from .trace_adapter import TraceAdapter
        from .storage_adapter import StorageAdapter
        from .strategies import CompositionMock

        self._scenario_manager = ScenarioManager()
        self._result_builder = ResultBuilder()
        self._trace_adapter = TraceAdapter()
        self._storage_adapter = StorageAdapter()
        self._composition_mock = CompositionMock()

        # ── In-memory shadow-only registry: simulation_id → artifact ──
        self._scenarios: Dict[str, SimulationScenario] = {}
        self._results: Dict[str, SimulationResult] = {}

    def create_simulation(
        self, request: SimulationRequest
    ) -> Optional["SimulationHandle"]:
        """Create a new simulation from a SimulationRequest.

        Validates the request (C2 shadow invariants + typing), then builds a
        SimulationScenario via ScenarioManager. On success, mints a
        SimulationHandle keyed by a fresh simulation_id and records the
        scenario in the shadow-only in-memory registry.

        Args:
            request: Describes what to simulate

        Returns:
            SimulationHandle or None (if request invalid / scenario build fails)
        """
        # ── Safe degradation on malformed input ──
        if not self._validate_request(request):
            return None

        # ── Build the shadow scenario via ScenarioManager ──
        scenario = self._scenario_manager.create_scenario(request)
        if scenario is None:
            return None

        # ── Mint a handle + register scenario (shadow-only, in-memory) ──
        handle = SimulationHandle(str(uuid4()))
        self._scenarios[handle.simulation_id] = scenario
        return handle

    def run_simulation(self, handle: "SimulationHandle") -> None:
        """Execute a simulation (pure shadow, no side-effects).

        Composes hypothetical candidates from the registered scenario, maps
        engine events to shadow trace records, builds a SimulationResult, and
        persists the complete run to shadow storage. The handle's status is
        advanced to "completed" on success or "error" on safe degradation.

        Args:
            handle: Previously created SimulationHandle
        """
        # ── Safe degradation on missing / unknown handle ──
        if handle is None:
            return
        scenario = self._scenarios.get(handle.simulation_id)
        if scenario is None:
            handle.status = "error"
            return

        # ── 1. Compose hypothetical candidates (never applied) ──
        strategy = self._composition_mock._select_strategy(scenario)
        candidates = self._composition_mock.compose(scenario, strategy)

        matched_capabilities: List[str] = []
        for candidate in candidates:
            for cap in candidate.capability_ids:
                if cap not in matched_capabilities:
                    matched_capabilities.append(cap)

        # ── 2. Assemble raw engine output (hypothetical metadata) ──
        engine_output: Dict[str, Any] = {
            "status": "completed",
            "output": {
                "matched_capabilities": matched_capabilities,
                "candidate_count": len(candidates),
            },
            "confidence_score": 1.0 if matched_capabilities else 0.0,
            "estimated_duration_ms": 0.0,
            "metadata": {
                "is_hypothetical": True,
                "strategy": strategy,
                "candidate_count": len(candidates),
            },
        }

        # ── 3. Map engine events → shadow trace records ──
        events: List[Dict[str, Any]] = [
            {
                "event_type": "engine.start",
                "event_data": {"simulation_id": handle.simulation_id},
            },
            {
                "event_type": "scenario.compose",
                "event_data": {"strategy": strategy},
            },
            {
                "event_type": "result.build",
                "event_data": {"status": "completed"},
            },
        ]
        trace_records = self._trace_adapter.create_trace(handle, events)

        # ── 4. Build the shadow result ──
        result = self._result_builder.build_result(
            scenario, engine_output, trace_records
        )

        # ── Defensive guard (C2) ──
        result.shadow_marked = True
        result.origin = "composition_shadow_storage"

        # ── 5. Persist + register (shadow-only) ──
        self._results[handle.simulation_id] = result
        self._storage_adapter.save_simulation(handle, result, trace_records)

        handle.status = "completed"

    def collect_result(self, handle: "SimulationHandle") -> SimulationResult:
        """Collect the outcome of a completed simulation.

        Retrieves the in-memory result, falling back to shadow storage when
        the in-memory registry does not hold it. On unknown handle, returns a
        fresh shadow SimulationResult (safe degradation, never raises).

        Args:
            handle: SimulationHandle from create_simulation or run_simulation

        Returns:
            SimulationResult with shadow_marked=True,
            origin="composition_shadow_storage"
        """
        result: Optional[SimulationResult] = None

        if handle is not None:
            result = self._results.get(handle.simulation_id)

        # ── Fallback: load from shadow storage ──
        if result is None and handle is not None:
            snapshot = self._storage_adapter.load_simulation(
                handle.simulation_id
            )
            if snapshot is not None and snapshot.result is not None:
                result = SimulationResult.from_dict(snapshot.result)

        # ── Safe degradation on unknown handle ──
        if result is None:
            result = SimulationResult()

        # ── Defensive guard (C2): force shadow markers on output ──
        result.shadow_marked = True
        result.origin = "composition_shadow_storage"
        return result

    def _validate_request(self, request: SimulationRequest) -> bool:
        """Validate SimulationRequest meets minimum shadow requirements.

        Checks:
            - request is a SimulationRequest instance
            - shadow_marked is True (C2)
            - origin is composition_shadow_storage (C2)
            - intent is a non-empty string
            - scope / parameters are dicts when present

        Returns:
            True if the request passes all validations.
        """
        if request is None:
            return False
        if not isinstance(request, SimulationRequest):
            return False
        if not getattr(request, "shadow_marked", False):
            return False
        if getattr(request, "origin", "") != "composition_shadow_storage":
            return False
        intent = getattr(request, "intent", "")
        if not isinstance(intent, str) or not intent:
            return False
        scope = getattr(request, "scope", None)
        if scope is not None and not isinstance(scope, dict):
            return False
        parameters = getattr(request, "parameters", None)
        if parameters is not None and not isinstance(parameters, dict):
            return False
        return True


class SimulationHandle:
    """Lightweight handle pointing to an in-progress or completed simulation.

    All simulation data resides in composition_shadow_storage.
    """

    def __init__(self, simulation_id: str) -> None:
        self.simulation_id: str = simulation_id
        self.status: str = "created"
        self._storage_key: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"SimulationHandle(id={self.simulation_id[:8]}..., "
            f"status={self.status})"
        )
