"""
Phase 6.1-L2.1: SimulationTraceRecord — DESIGN_ONLY Data Model.

Shadow trace record for simulation execution steps.
Separate namespace from production trace storage to prevent pollution.

Fields:
    trace_id:      Unique trace identifier
    simulation_id: Associated simulation ID
    namespace:     Always "composition_shadow_simulation"
    event_type:    Type of simulation event
    event_data:    Event payload
    shadow_marked: Always True
    origin:        Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class SimulationTraceRecord:
    """Shadow trace record — simulation execution step."""

    # ── Identity ──
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    simulation_id: str = ""

    # ── Namespace ──
    namespace: str = "composition_shadow_simulation"

    # ── Event ──
    event_type: str = ""  # e.g., "engine.start", "scenario.create", "result.build"
    event_data: Dict[str, Any] = field(default_factory=dict)

    # ── Sequence ──
    sequence_number: int = 0

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "simulation_id": self.simulation_id,
            "namespace": self.namespace,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "sequence_number": self.sequence_number,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationTraceRecord":
        return cls(
            trace_id=data.get("trace_id", ""),
            simulation_id=data.get("simulation_id", ""),
            namespace=data.get("namespace", "composition_shadow_simulation"),
            event_type=data.get("event_type", ""),
            event_data=data.get("event_data", {}),
            sequence_number=data.get("sequence_number", 0),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            timestamp=data.get("timestamp", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationTraceRecord(id={self.trace_id[:8]}..., "
            f"sim={self.simulation_id[:8]}..., "
            f"event={self.event_type}, "
            f"ns={self.namespace})"
        )