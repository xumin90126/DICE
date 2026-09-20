"""
Phase 6.1-L2.1: SimulationSnapshot — DESIGN_ONLY Data Model.

Complete snapshot of a simulation run: request + scenario + result + trace.
Loaded by StorageAdapter for inspection without re-running simulation.

Fields:
    snapshot_id:   Unique snapshot identifier
    request:       Original SimulationRequest
    scenario:      SimulationScenario
    result:        SimulationResult
    trace_records: All SimulationTraceRecords
    shadow_marked: Always True
    origin:        Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Forward references resolved at runtime
from .simulation_request import SimulationRequest
from .simulation_scenario import SimulationScenario
from .simulation_result import SimulationResult
from .simulation_trace_record import SimulationTraceRecord


@dataclass
class SimulationSnapshot:
    """Complete simulation snapshot — inspectable, replayable."""

    # ── Identity ──
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Artifacts ──
    request: Optional[Dict[str, Any]] = None  # Serialized SimulationRequest
    scenario: Optional[Dict[str, Any]] = None  # Serialized SimulationScenario
    result: Optional[Dict[str, Any]] = None    # Serialized SimulationResult
    trace_records: List[Dict[str, Any]] = field(default_factory=list)

    # ── Status ──
    status: str = "created"  # "created" | "in_progress" | "completed" | "error"

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "request": self.request,
            "scenario": self.scenario,
            "result": self.result,
            "trace_records": self.trace_records,
            "status": self.status,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationSnapshot":
        return cls(
            snapshot_id=data.get("snapshot_id", ""),
            request=data.get("request"),
            scenario=data.get("scenario"),
            result=data.get("result"),
            trace_records=data.get("trace_records", []),
            status=data.get("status", "created"),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationSnapshot(id={self.snapshot_id[:8]}..., "
            f"status={self.status}, "
            f"traces={len(self.trace_records)})"
        )