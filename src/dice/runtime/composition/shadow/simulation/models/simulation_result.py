"""
Phase 6.1-L2.1: SimulationResult — DESIGN_ONLY Data Model.

Complete simulation outcome. Built by ResultBuilder from engine output
and trace records. Never triggers real Capability execution.

Fields:
    result_id:       Unique result identifier
    scenario_id:     Associated SimulationScenario ID
    status:          "completed" | "blocked" | "error"
    output:          Simulated output structure
    trace_ids:       List of associated trace record IDs
    shadow_marked:   Always True
    origin:          Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class SimulationResult:
    """Simulation result — shadow outcome, never applied."""

    # ── Identity ──
    result_id: str = field(default_factory=lambda: str(uuid4()))
    scenario_id: str = ""

    # ── Status ──
    status: str = "completed"  # "completed" | "blocked" | "error"

    # ── Output ──
    output: Dict[str, Any] = field(default_factory=dict)

    # ── Trace ──
    trace_ids: List[str] = field(default_factory=list)

    # ── Risk Assessment ──
    risk_factors: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metrics ──
    estimated_duration_ms: float = 0.0
    confidence_score: float = 0.0

    # ── Metadata ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "scenario_id": self.scenario_id,
            "status": self.status,
            "output": self.output,
            "trace_ids": self.trace_ids,
            "risk_factors": self.risk_factors,
            "conflicts": self.conflicts,
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "estimated_duration_ms": self.estimated_duration_ms,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationResult":
        return cls(
            result_id=data.get("result_id", ""),
            scenario_id=data.get("scenario_id", ""),
            status=data.get("status", "completed"),
            output=data.get("output", {}),
            trace_ids=data.get("trace_ids", []),
            risk_factors=data.get("risk_factors", []),
            conflicts=data.get("conflicts", []),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            estimated_duration_ms=data.get("estimated_duration_ms", 0.0),
            confidence_score=data.get("confidence_score", 0.0),
            timestamp=data.get("timestamp", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationResult(id={self.result_id[:8]}..., "
            f"status={self.status}, "
            f"shadow_marked={self.shadow_marked})"
        )