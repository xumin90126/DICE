"""
Phase 6.1-L2.1: TraceAdapter — Simulation Logic (Phase D implemented).

Responsibility:
    Create SimulationTraceRecord objects that link simulation execution
    back to the Shadow Trace namespace. Also generates SimulationEvidenceSnapshot
    (before/after evidence comparison). Ensures trace separation from
    production trace storage.

Input:
    - SimulationHandle / SimulationResult
    - Engine events (step-by-step execution log)

Output:
    - List[SimulationTraceRecord] (shadow namespace)
    - SimulationEvidenceSnapshot (hypothetical, shadow-only)

Forbidden:
    - ❌ No production trace storage
    - ❌ No Capability Registry access
    - ❌ No trace pollution (separate namespace)
    - ❌ No Runtime 1-8 modification
    - ❌ No Observation modification

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

from .models import SimulationResult, SimulationTraceRecord
from .simulation_engine import SimulationHandle


@dataclass
class SimulationEvidenceSnapshot:
    """Evidence snapshot — before/after evidence comparison (shadow-only).

    Captures the evidence state before simulation (from Observation) and
    the candidate count after simulation (from Result), without modifying
    either source. Never written to production storage.

    Fields:
        snapshot_id:     Unique snapshot identifier
        observation_id:  Source observation identifier
        evidence_before: Evidence count before simulation (from Observation)
        evidence_after:  Candidate count after simulation (from Result)
        match_count:     Number of matched capabilities
        coverage_ratio:  Coverage ratio (matched / total), 0.0 ~ 1.0
        shadow_marked:   Always True
        origin:          Always "composition_shadow_storage"
    """

    # ── Identity ──
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    observation_id: str = ""

    # ── Before / After ──
    evidence_before: int = 0
    evidence_after: int = 0
    match_count: int = 0
    coverage_ratio: float = 0.0

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize snapshot to a plain dict (pure data, no behavior)."""
        return {
            "snapshot_id": self.snapshot_id,
            "observation_id": self.observation_id,
            "evidence_before": self.evidence_before,
            "evidence_after": self.evidence_after,
            "match_count": self.match_count,
            "coverage_ratio": self.coverage_ratio,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationEvidenceSnapshot":
        """Deserialize snapshot from a plain dict (pure data, no behavior)."""
        return cls(
            snapshot_id=data.get("snapshot_id", ""),
            observation_id=data.get("observation_id", ""),
            evidence_before=data.get("evidence_before", 0),
            evidence_after=data.get("evidence_after", 0),
            match_count=data.get("match_count", 0),
            coverage_ratio=data.get("coverage_ratio", 0.0),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationEvidenceSnapshot(id={self.snapshot_id[:8]}..., "
            f"obs={self.observation_id[:8]}..., "
            f"before={self.evidence_before}, after={self.evidence_after})"
        )


class TraceAdapter:
    """Create simulation trace records in shadow namespace. DESIGN_ONLY at L2.1."""

    TRACE_NAMESPACE: str = "composition_shadow_simulation"

    def __init__(self) -> None:
        self._namespace: str = self.TRACE_NAMESPACE

    def create_trace(
        self,
        handle: SimulationHandle,
        events: List[Dict[str, Any]],
    ) -> List[SimulationTraceRecord]:
        """Generate trace records for a simulation run.

        Maps the raw engine event log to shadow trace records, then enforces
        the shadow namespace invariant on every record (C2). Any record that
        fails namespace validation is force-corrected to the shadow namespace
        (this is a defensive guard on a theoretically-unreachable path).

        Args:
            handle: SimulationHandle of the completed simulation
            events: Step-by-step engine event log

        Returns:
            List of SimulationTraceRecord (shadow namespace only)
        """
        records = self._map_events_to_records(handle, events)

        for record in records:
            if not self._ensure_namespace(record):
                # Defensive guard (C2): never let a non-shadow record escape.
                record.namespace = self._namespace
                record.shadow_marked = True
                record.origin = "composition_shadow_storage"

        return records

    def generate_evidence_snapshot(
        self,
        observation_id: str,
        result: SimulationResult,
    ) -> SimulationEvidenceSnapshot:
        """Generate a before/after evidence snapshot (hypothetical, shadow-only).

        The snapshot is built from the simulation result's "after" side only.
        The source Observation is referenced read-only by id (its content is
        never read or modified). Derived metrics:
            evidence_after = number of trace ids on the result
            match_count    = number of matched capabilities (from result output)
            coverage_ratio = match_count / evidence_after (clamped 0.0..1.0)

        Args:
            observation_id: Source observation identifier (read-only reference)
            result:         SimulationResult used for the "after" side

        Returns:
            SimulationEvidenceSnapshot (shadow_marked=True, origin=shadow storage)
        """
        # ── Safe degradation on malformed input ──
        if result is None:
            result = SimulationResult()

        # ── After side: trace ids = evidence count after simulation ──
        trace_ids = list(getattr(result, "trace_ids", []) or [])
        evidence_after = len(trace_ids)

        # ── Matched capabilities (from result output) ──
        output = getattr(result, "output", {}) or {}
        if not isinstance(output, dict):
            output = {}
        matches = output.get("matched_capabilities", [])
        if not isinstance(matches, list):
            matches = []
        # Keep only non-empty string capability ids.
        matches = [m for m in matches if isinstance(m, str) and m]
        match_count = len(matches)

        # ── Coverage ratio (clamped 0.0 .. 1.0) ──
        coverage_ratio = 0.0
        if evidence_after > 0:
            coverage_ratio = match_count / evidence_after
        coverage_ratio = max(0.0, min(1.0, coverage_ratio))

        snapshot = SimulationEvidenceSnapshot(
            observation_id=observation_id or "",
            evidence_before=0,
            evidence_after=evidence_after,
            match_count=match_count,
            coverage_ratio=coverage_ratio,
            shadow_marked=True,
            origin="composition_shadow_storage",
        )

        # ── Defensive guard (C2) ──
        if not snapshot.shadow_marked:
            snapshot.shadow_marked = True
        if snapshot.origin != "composition_shadow_storage":
            snapshot.origin = "composition_shadow_storage"

        return snapshot

    def _ensure_namespace(self, record: SimulationTraceRecord) -> bool:
        """Verify trace record is in the shadow namespace.

        Checks:
            - record is not None
            - shadow_marked is True (C2)
            - namespace equals the shadow trace namespace
            - origin is composition_shadow_storage (C2)

        Returns:
            True if the record is fully compliant with shadow namespace.
        """
        if record is None:
            return False
        if not getattr(record, "shadow_marked", False):
            return False
        if getattr(record, "namespace", "") != self._namespace:
            return False
        if getattr(record, "origin", "") != "composition_shadow_storage":
            return False
        return True

    def _map_events_to_records(
        self, handle: SimulationHandle, events: List[Dict[str, Any]]
    ) -> List[SimulationTraceRecord]:
        """Convert raw engine events to trace records.

        Each event is mapped to a SimulationTraceRecord with an increasing
        sequence number. Malformed (non-dict) events are skipped; non-dict
        event_data is discarded. All records are born in the shadow namespace.

        Args:
            handle: SimulationHandle (provides simulation_id)
            events: Step-by-step engine event log

        Returns:
            List of SimulationTraceRecord (shadow namespace only)
        """
        if events is None:
            events = []

        simulation_id = getattr(handle, "simulation_id", "") or ""

        records: List[SimulationTraceRecord] = []
        for seq, event in enumerate(events):
            # Skip malformed (non-dict) events.
            if not isinstance(event, dict):
                continue

            event_type = event.get("event_type", "")
            raw_data = event.get("event_data", {})
            event_data = dict(raw_data) if isinstance(raw_data, dict) else {}

            seq_num = event.get("sequence_number", seq)
            try:
                seq_num = int(seq_num)
            except (TypeError, ValueError):
                seq_num = seq

            record = SimulationTraceRecord(
                simulation_id=simulation_id,
                namespace=self._namespace,
                event_type=event_type,
                event_data=event_data,
                sequence_number=seq_num,
                shadow_marked=True,
                origin="composition_shadow_storage",
            )
            records.append(record)

        return records
