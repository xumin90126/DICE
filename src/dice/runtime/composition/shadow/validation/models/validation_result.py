"""
Phase 6.1-L2.2: ValidationResult — DESIGN_ONLY Data Model.

Aggregated validation outcome carrying per-rule CheckResults. Pure
observation — never triggers actions, corrections, activation, or
execution (C3 Observation Only).

Fields:
    result_id:            Unique result identifier
    request_id:           Associated ValidationRequest ID
    simulation_result_id: Source L2.1 SimulationResult ID
    overall_status:       ValidationStatus (PASS/FAIL/WARN/PARTIAL)
    total_rules:          Total rules executed
    passed_rules:         Rules passed
    failed_rules:         Rules failed
    warned_rules:         Rules warned
    check_results:        List of per-rule CheckResult
    candidate_verdicts:   Per-candidate verdicts {candidate_id: PASS/FAIL/WARN}
    duration_ms:          Total validation duration
    shadow_marked:        Always True
    origin:               Always "composition_shadow_storage"
    is_hypothetical:      Always True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from .validation_request import ValidationStatus


@dataclass
class CheckResult:
    """Single-rule check outcome (sub-structure of ValidationResult)."""

    rule_id: str = ""
    rule_name: str = ""
    rule_type: str = ""
    status: str = "PASS"  # "PASS" | "FAIL" | "WARN"
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_type": self.rule_type,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckResult":
        return cls(
            rule_id=data.get("rule_id", ""),
            rule_name=data.get("rule_name", ""),
            rule_type=data.get("rule_type", ""),
            status=data.get("status", "PASS"),
            message=data.get("message", ""),
            details=data.get("details", {}),
            duration_ms=data.get("duration_ms", 0.0),
        )


@dataclass
class ValidationResult:
    """Aggregated validation result — pure observation, never an action."""

    # ── Identity ──
    result_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: str = ""
    simulation_result_id: str = ""

    # ── Aggregate Outcome ──
    overall_status: ValidationStatus = ValidationStatus.PASS
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    warned_rules: int = 0

    # ── Details ──
    check_results: List[CheckResult] = field(default_factory=list)
    candidate_verdicts: Dict[str, str] = field(default_factory=dict)

    # ── Metrics ──
    duration_ms: float = 0.0

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    shadow_version: str = "1.0"

    # ── Metadata ──
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "request_id": self.request_id,
            "simulation_result_id": self.simulation_result_id,
            "overall_status": self.overall_status.value,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "warned_rules": self.warned_rules,
            "check_results": [c.to_dict() for c in self.check_results],
            "candidate_verdicts": self.candidate_verdicts,
            "duration_ms": self.duration_ms,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        return cls(
            result_id=data.get("result_id", ""),
            request_id=data.get("request_id", ""),
            simulation_result_id=data.get("simulation_result_id", ""),
            overall_status=ValidationStatus(data.get("overall_status", "pass")),
            total_rules=data.get("total_rules", 0),
            passed_rules=data.get("passed_rules", 0),
            failed_rules=data.get("failed_rules", 0),
            warned_rules=data.get("warned_rules", 0),
            check_results=[
                CheckResult.from_dict(c) for c in data.get("check_results", [])
            ],
            candidate_verdicts=data.get("candidate_verdicts", {}),
            duration_ms=data.get("duration_ms", 0.0),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            is_hypothetical=data.get("is_hypothetical", True),
            shadow_version=data.get("shadow_version", "1.0"),
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return (
            f"ValidationResult(id={self.result_id[:8]}..., "
            f"status={self.overall_status.value}, "
            f"rules={self.total_rules}, "
            f"shadow_marked={self.shadow_marked})"
        )
