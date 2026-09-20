"""
Phase 6.1-L2.1: StorageAdapter — Simulation Logic (Phase E implemented).

Responsibility:
    Persist and load simulation artifacts to/from composition_shadow_storage.
    All simulation data is isolated from production storage.

Input:
    - SimulationHandle / simulation_id
    - SimulationResult / SimulationScenario / SimulationTraceRecord

Output:
    - Persisted artifacts in composition_shadow_storage
    - Loaded artifacts from composition_shadow_storage

Forbidden:
    - ❌ No production storage access (no disk / no external DB)
    - ❌ No Capability Registry access
    - ❌ No Runtime 1-8 modification
    - ❌ No cross-namespace data leak

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - Storage is ephemeral (in-memory) to prevent accidental persistence
      in production paths.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import (
    SimulationResult,
    SimulationScenario,
    SimulationTraceRecord,
    SimulationSnapshot,
)
from .simulation_engine import SimulationHandle


class StorageAdapter:
    """Persist/load simulation artifacts in shadow storage (Phase E)."""

    STORAGE_ROOT: str = "composition_shadow_storage"
    SIMULATION_PREFIX: str = "simulation/"
    TRACE_PREFIX: str = "simulation/traces/"
    TRACE_NAMESPACE: str = "composition_shadow_simulation"

    def __init__(self) -> None:
        self._base_path: str = f"{self.STORAGE_ROOT}/{self.SIMULATION_PREFIX}"
        # ── In-memory shadow-only stores (never written to disk / DB) ──
        self._simulations: Dict[str, Dict[str, Any]] = {}
        self._traces: Dict[str, Dict[str, Any]] = {}

    def save_simulation(
        self,
        handle: SimulationHandle,
        result: SimulationResult,
        trace_records: List[SimulationTraceRecord],
    ) -> bool:
        """Persist a complete simulation run.

        Builds a serialized SimulationSnapshot from the handle, result, and
        trace records, then stores it under the shadow simulation namespace.
        Every persisted artifact carries shadow_marked=True and
        origin=composition_shadow_storage (C2).

        Args:
            handle:        SimulationHandle (provides simulation_id)
            result:        SimulationResult to persist
            trace_records: Trace records to persist

        Returns:
            True if saved successfully (False on isolation failure)
        """
        # ── Isolation guard: never write if storage is not shadow-only ──
        if not self._verify_isolation():
            return False

        # ── Safe degradation on malformed input ──
        if result is None:
            result = SimulationResult()
        if trace_records is None:
            trace_records = []
        trace_records = [
            t for t in trace_records if isinstance(t, SimulationTraceRecord)
        ]

        simulation_id = getattr(handle, "simulation_id", "") or ""
        if not simulation_id:
            return False

        # ── Serialize result / trace (pure data, shadow-marked) ──
        result_dict = result.to_dict()
        trace_dicts = [
            t.to_dict() for t in trace_records
            if getattr(t, "shadow_marked", False)
        ]

        snapshot = SimulationSnapshot(
            result=result_dict,
            trace_records=trace_dicts,
            status="completed",
            shadow_marked=True,
            origin="composition_shadow_storage",
        )

        # ── Defensive guard (C2) ──
        snapshot.shadow_marked = True
        snapshot.origin = "composition_shadow_storage"

        self._simulations[simulation_id] = snapshot.to_dict()
        return True

    def save_trace(self, trace: SimulationTraceRecord) -> str:
        """Persist a single SimulationTraceRecord to shadow trace storage.

        Args:
            trace: SimulationTraceRecord to persist

        Returns:
            str — trace storage key (shadow-only namespace)
        """
        # ── Isolation guard ──
        if not self._verify_isolation():
            return ""

        # ── Safe degradation on malformed input ──
        if trace is None:
            return ""

        # ── Enforce shadow namespace invariant (C2) ──
        trace.namespace = self.TRACE_NAMESPACE
        trace.shadow_marked = True
        trace.origin = "composition_shadow_storage"

        key = self._build_trace_key(trace)
        self._traces[key] = trace.to_dict()
        return key

    def load_simulation(
        self, simulation_id: str
    ) -> Optional[SimulationSnapshot]:
        """Load a complete simulation snapshot from storage.

        Args:
            simulation_id: Unique simulation identifier

        Returns:
            SimulationSnapshot or None
        """
        # ── Isolation guard ──
        if not self._verify_isolation():
            return None

        data = self._simulations.get(simulation_id or "")
        if data is None:
            return None

        snapshot = SimulationSnapshot.from_dict(data)
        # ── Defensive guard (C2): force shadow markers on load ──
        snapshot.shadow_marked = True
        snapshot.origin = "composition_shadow_storage"
        return snapshot

    def _build_storage_path(self, simulation_id: str) -> str:
        """Construct the shadow storage path for a simulation artifact.

        The path lives under composition_shadow_storage/simulation/ and is
        never under any production path.
        """
        sid = simulation_id or ""
        return f"{self._base_path}{sid}"

    def _verify_isolation(self) -> bool:
        """Confirm storage is isolated from production.

        Checks:
            - storage root is composition_shadow_storage
            - simulation prefix is simulation/
            - the composed base path contains no production reference

        Returns:
            True when all isolation invariants hold.
        """
        if self.STORAGE_ROOT != "composition_shadow_storage":
            return False
        if self.SIMULATION_PREFIX != "simulation/":
            return False
        if "production" in self._base_path.lower():
            return False
        return True

    def _build_trace_key(self, trace: SimulationTraceRecord) -> str:
        """Construct a shadow-only storage key for a trace record.

        Uses the trace's trace_id under the shadow trace prefix. Falls back
        to a synthetic key if trace_id is empty (safe degradation).
        """
        trace_id = getattr(trace, "trace_id", "") or ""
        if not trace_id:
            simulation_id = getattr(trace, "simulation_id", "") or ""
            seq = getattr(trace, "sequence_number", 0)
            trace_id = f"unnamed-{simulation_id}-{seq}"
        return f"{self.STORAGE_ROOT}/{self.TRACE_PREFIX}{trace_id}"
