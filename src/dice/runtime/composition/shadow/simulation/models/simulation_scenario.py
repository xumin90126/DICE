"""
Phase 6.1-L2.1: SimulationScenario — DESIGN_ONLY Data Model.

Defines the parameters, constraints, and expected behaviors for
a simulation run. Built by ScenarioManager from a SimulationRequest.

Fields:
    scenario_id:   Unique scenario identifier
    name:          Human-readable scenario name
    capabilities:  List of capability identifiers to simulate
    constraints:   Simulation constraints (timeout, risk limits, etc.)
    expected:      Expected behavior patterns
    parameters:    Resolved scenario parameters
    shadow_marked: Always True
    origin:        Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class SimulationScenario:
    """Simulation scenario — full parameter set for a simulation run."""

    # ── Identity ──
    scenario_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""

    # ── Capabilities ──
    capabilities: List[str] = field(default_factory=list)

    # ── Constraints ──
    constraints: Dict[str, Any] = field(default_factory=dict)

    # ── Expected Behavior ──
    expected: Dict[str, Any] = field(default_factory=dict)

    # ── Parameters ──
    parameters: Dict[str, Any] = field(default_factory=dict)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "constraints": self.constraints,
            "expected": self.expected,
            "parameters": self.parameters,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationScenario":
        return cls(
            scenario_id=data.get("scenario_id", ""),
            name=data.get("name", ""),
            capabilities=data.get("capabilities", []),
            constraints=data.get("constraints", {}),
            expected=data.get("expected", {}),
            parameters=data.get("parameters", {}),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            created_at=data.get("created_at", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationScenario(id={self.scenario_id[:8]}..., "
            f"name={self.name}, "
            f"capabilities={len(self.capabilities)}, "
            f"shadow_marked={self.shadow_marked})"
        )