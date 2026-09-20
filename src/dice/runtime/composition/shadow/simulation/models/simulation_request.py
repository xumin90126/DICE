"""
Phase 6.1-L2.1: SimulationRequest — DESIGN_ONLY Data Model.

Represents the user intent and scope definition for a simulation.
Carried into ScenarioManager to build a SimulationScenario.

Fields:
    request_id:    Unique request identifier
    intent:        What to simulate ("composition" | "execution" | "validation")
    scope:         Scope definition (capabilities, documents, context)
    parameters:    Additional simulation parameters
    shadow_marked: Always True
    origin:        Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class SimulationRequest:
    """Simulation request — user intent and scope (shadow-only)."""

    # ── Identity ──
    request_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Intent ──
    intent: str = "composition"  # "composition" | "execution" | "validation"
    scope: Dict[str, Any] = field(default_factory=dict)
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
            "request_id": self.request_id,
            "intent": self.intent,
            "scope": self.scope,
            "parameters": self.parameters,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationRequest":
        return cls(
            request_id=data.get("request_id", ""),
            intent=data.get("intent", "composition"),
            scope=data.get("scope", {}),
            parameters=data.get("parameters", {}),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            created_at=data.get("created_at", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"SimulationRequest(id={self.request_id[:8]}..., "
            f"intent={self.intent}, "
            f"shadow_marked={self.shadow_marked})"
        )