"""
Phase 6.1-L2.1: ResultBuilder — Simulation Logic (Phase C implemented).

Responsibility:
    Build a SimulationResult from engine output. Assembles scenario
    metadata, execution trace, validation flags, and shadow markers
    into a unified result structure.

Input:
    - SimulationScenario (executed)
    - Raw engine output
    - Trace records

Output:
    - SimulationResult (with shadow_marked=True, origin=composition_shadow_storage)

Forbidden:
    - ❌ No Capability Registry access
    - ❌ No Runtime 1-8 modification
    - ❌ No production activation
    - ❌ No composition execution

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import (
    SimulationResult,
    SimulationScenario,
    SimulationTraceRecord,
)


class ResultBuilder:
    """Build SimulationResult from raw engine output (Shadow-only)."""

    _VALID_STATUSES = ("completed", "blocked", "error")

    def __init__(self) -> None:
        self._shadow_marked: bool = True
        self._origin: str = "composition_shadow_storage"

    def build_result(
        self,
        scenario: SimulationScenario,
        engine_output: Dict[str, Any],
        trace_records: List[SimulationTraceRecord],
    ) -> SimulationResult:
        """Build a complete SimulationResult.

        Args:
            scenario:       Executed SimulationScenario
            engine_output:  Raw output from SimulationEngine
            trace_records:  Trace records from TraceAdapter

        Returns:
            SimulationResult with shadow_marked=True,
            origin="composition_shadow_storage"
        """
        # ── Safe degradation on malformed input ──
        if not isinstance(engine_output, dict):
            engine_output = {}
        if trace_records is None:
            trace_records = []

        # ── Status normalization (fallback to "completed") ──
        status = engine_output.get("status", "completed")
        if status not in self._VALID_STATUSES:
            status = "completed"

        # ── Trace id extraction (skip records without a trace_id) ──
        trace_ids = [
            t.trace_id for t in trace_records
            if getattr(t, "trace_id", None)
        ]

        result = SimulationResult(
            scenario_id=getattr(scenario, "scenario_id", ""),
            status=status,
            output=dict(engine_output.get("output", {}) or {}),
            trace_ids=trace_ids,
            risk_factors=list(engine_output.get("risk_factors", []) or []),
            conflicts=list(engine_output.get("conflicts", []) or []),
            estimated_duration_ms=float(
                engine_output.get("estimated_duration_ms", 0.0) or 0.0
            ),
            confidence_score=float(
                engine_output.get("confidence_score", 0.0) or 0.0
            ),
            shadow_marked=self._shadow_marked,
            origin=self._origin,
            metadata=self._assemble_metadata(scenario, engine_output),
        )

        # ── Defensive guard: ResultBuilder output must satisfy shadow
        #    invariants (C2). Force-correct in the (theoretically
        #    unreachable) case markers were not set. ──
        if not self._validate_shadow_markers(result):
            result.shadow_marked = True
            result.origin = "composition_shadow_storage"

        return result

    def _validate_shadow_markers(self, result: SimulationResult) -> bool:
        """Ensure all shadow markers are correctly set (C2).

        Checks:
            - result is not None
            - shadow_marked is True
            - origin is composition_shadow_storage

        Returns:
            True if all shadow markers are compliant.
        """
        if result is None:
            return False
        if not getattr(result, "shadow_marked", False):
            return False
        if getattr(result, "origin", "") != "composition_shadow_storage":
            return False
        return True

    def _assemble_metadata(
        self,
        scenario: SimulationScenario,
        engine_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assemble metadata from scenario and engine output.

        Combines scenario identity (id / name / capabilities) with the
        engine output's key set. Any ``engine_output["metadata"]`` dict is
        merged in last (engine metadata wins over scenario metadata keys).
        """
        if not isinstance(engine_output, dict):
            engine_output = {}

        capabilities = list(getattr(scenario, "capabilities", []) or [])

        meta: Dict[str, Any] = {
            "scenario_id": getattr(scenario, "scenario_id", ""),
            "scenario_name": getattr(scenario, "name", ""),
            "capabilities": capabilities,
            "capability_count": len(capabilities),
            "engine_output_keys": sorted(engine_output.keys()),
        }

        em = engine_output.get("metadata")
        if isinstance(em, dict):
            meta.update(em)

        return meta
