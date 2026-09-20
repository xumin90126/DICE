"""
ShadowExecutionSimulation — Simulated execution result (never applied).

Phase 6.1-L2: Used by CompositionSimulator to represent the outcome
of a simulated execution — WHAT WOULD happen if the composition
were actually executed. Never triggers real Capability execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class ShadowExecutionSimulation:
    """A simulated execution outcome — WHAT WOULD happen.

    This is a pure simulation artifact. It represents the expected
    result of executing a composition candidate, but NEVER triggers
    actual Capability execution.

    Fields:
        simulation_id: Unique simulation identifier
        candidate_id: Associated ShadowCompositionCandidate ID
        status: Simulation status ("completed" | "blocked" | "error")
        simulated_output: What the execution would produce
        estimated_duration_ms: Estimated execution duration
        risk_factors: Identified risk factors
        conflicts: Detected conflicts between capabilities
        shadow_marked: Always True
    """

    # ── Identity ──
    simulation_id: str = field(default_factory=lambda: str(uuid4()))
    candidate_id: str = ""

    # ── Simulation Result ──
    status: str = "completed"  # "completed" | "blocked" | "error"
    simulated_output: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_ms: float = 0.0

    # ── Risk Assessment ──
    risk_factors: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "candidate_id": self.candidate_id,
            "status": self.status,
            "simulated_output": self.simulated_output,
            "estimated_duration_ms": self.estimated_duration_ms,
            "risk_factors": self.risk_factors,
            "conflicts": self.conflicts,
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShadowExecutionSimulation":
        return cls(
            simulation_id=data.get("simulation_id", ""),
            candidate_id=data.get("candidate_id", ""),
            status=data.get("status", "completed"),
            simulated_output=data.get("simulated_output", {}),
            estimated_duration_ms=data.get("estimated_duration_ms", 0.0),
            risk_factors=data.get("risk_factors", []),
            conflicts=data.get("conflicts", []),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            timestamp=data.get("timestamp", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"ShadowExecutionSimulation(id={self.simulation_id[:8]}..., "
            f"candidate={self.candidate_id[:8]}..., "
            f"status={self.status}, "
            f"shadow_marked={self.shadow_marked})"
        )