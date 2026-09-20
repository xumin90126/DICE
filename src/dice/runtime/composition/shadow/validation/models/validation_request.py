"""
Phase 6.1-L2.2: ValidationRequest — DESIGN_ONLY Data Model.

Represents a single validation request in the Shadow Validation Layer.
References L2.1 Shadow Simulation Result / Trace / Snapshot by ID only
(read-only reference, never a live pointer).

Fields:
    request_id:            Unique validation request identifier
    simulation_result_id:  Source L2.1 SimulationResult ID (read-only ref)
    observation_id:        Source Observation ID (read-only ref)
    document_id:           Source document identifier
    candidate_count:       Number of candidates to validate
    rule_set_id:           Rule set identifier
    validation_config:     ValidationConfig sub-structure
    status:                ValidationStatus (REQUESTED/ACTIVE/COMPLETED/...)
    shadow_marked:         Always True
    origin:                Always "composition_shadow_storage"
    is_hypothetical:       Always True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class ValidationStatus(Enum):
    """Validation lifecycle + aggregate outcome status."""

    REQUESTED = "requested"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class ValidationConfig:
    """Validation configuration parameters (sub-structure of request)."""

    timeout_ms: int = 10000
    strict_mode: bool = False
    rule_set: str = "default"
    enable_coverage_check: bool = True
    enable_consistency_check: bool = True
    enable_isolation_check: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeout_ms": self.timeout_ms,
            "strict_mode": self.strict_mode,
            "rule_set": self.rule_set,
            "enable_coverage_check": self.enable_coverage_check,
            "enable_consistency_check": self.enable_consistency_check,
            "enable_isolation_check": self.enable_isolation_check,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationConfig":
        return cls(
            timeout_ms=data.get("timeout_ms", 10000),
            strict_mode=data.get("strict_mode", False),
            rule_set=data.get("rule_set", "default"),
            enable_coverage_check=data.get("enable_coverage_check", True),
            enable_consistency_check=data.get("enable_consistency_check", True),
            enable_isolation_check=data.get("enable_isolation_check", True),
        )


@dataclass
class ValidationRequest:
    """Validation request — shadow-only, references L2.1 artifacts by ID."""

    # ── Identity ──
    request_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Source References (read-only, ID-based) ──
    simulation_result_id: str = ""
    observation_id: str = ""
    document_id: str = ""

    # ── Scope ──
    candidate_count: int = 0
    rule_set_id: str = "default"

    # ── Configuration ──
    validation_config: Optional[ValidationConfig] = field(
        default_factory=ValidationConfig
    )

    # ── Status ──
    status: ValidationStatus = ValidationStatus.REQUESTED

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    shadow_version: str = "1.0"

    # ── Metadata ──
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "simulation_result_id": self.simulation_result_id,
            "observation_id": self.observation_id,
            "document_id": self.document_id,
            "candidate_count": self.candidate_count,
            "rule_set_id": self.rule_set_id,
            "validation_config": (
                self.validation_config.to_dict()
                if self.validation_config is not None
                else None
            ),
            "status": self.status.value,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRequest":
        cfg = data.get("validation_config")
        return cls(
            request_id=data.get("request_id", ""),
            simulation_result_id=data.get("simulation_result_id", ""),
            observation_id=data.get("observation_id", ""),
            document_id=data.get("document_id", ""),
            candidate_count=data.get("candidate_count", 0),
            rule_set_id=data.get("rule_set_id", "default"),
            validation_config=(
                ValidationConfig.from_dict(cfg) if cfg else ValidationConfig()
            ),
            status=ValidationStatus(data.get("status", "requested")),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            is_hypothetical=data.get("is_hypothetical", True),
            shadow_version=data.get("shadow_version", "1.0"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def __repr__(self) -> str:
        return (
            f"ValidationRequest(id={self.request_id[:8]}..., "
            f"status={self.status.value}, "
            f"shadow_marked={self.shadow_marked})"
        )
