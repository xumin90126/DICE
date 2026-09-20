"""
Phase 6.1-L2.2: ValidationReport — DESIGN_ONLY Data Model.

Complete validation report — a self-contained, human-readable artifact
for L4 Governance (reserved) and Human Review. Pure observation output,
never writes back to L2.1 or Production.

Fields:
    report_id:            Unique report identifier
    result_id:            Associated ValidationResult ID
    request_id:           Associated ValidationRequest ID
    simulation_result_id: Source L2.1 SimulationResult ID
    summary:              ReportSummary sub-structure
    rule_results:         Per-rule CheckResults (== ValidationResult.check_results)
    evidence_references:  EvidenceReference list
    recommendations:      Human-review recommendations
    generated_by:         "phase6_1_l22_validator"
    shadow_marked:        Always True
    origin:               Always "composition_shadow_storage"
    is_hypothetical:      Always True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from .validation_result import CheckResult


@dataclass
class ReportSummary:
    """Report summary (sub-structure of ValidationReport)."""

    overall_status: str = "PASS"
    total_candidates: int = 0
    passed_candidates: int = 0
    failed_candidates: int = 0
    rule_pass_rate: float = 0.0
    critical_violations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "total_candidates": self.total_candidates,
            "passed_candidates": self.passed_candidates,
            "failed_candidates": self.failed_candidates,
            "rule_pass_rate": self.rule_pass_rate,
            "critical_violations": self.critical_violations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReportSummary":
        return cls(
            overall_status=data.get("overall_status", "PASS"),
            total_candidates=data.get("total_candidates", 0),
            passed_candidates=data.get("passed_candidates", 0),
            failed_candidates=data.get("failed_candidates", 0),
            rule_pass_rate=data.get("rule_pass_rate", 0.0),
            critical_violations=data.get("critical_violations", 0),
        )


@dataclass
class EvidenceReference:
    """Reference to an evidence source (sub-structure of ValidationReport)."""

    evidence_id: str = ""
    source_type: str = "SNAPSHOT"  # "SNAPSHOT" | "TRACE" | "RESULT"
    source_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_type": self.source_type,
            "source_ref": self.source_ref,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceReference":
        return cls(
            evidence_id=data.get("evidence_id", ""),
            source_type=data.get("source_type", "SNAPSHOT"),
            source_ref=data.get("source_ref", ""),
        )


@dataclass
class ValidationReport:
    """Validation report — self-contained, human-readable shadow artifact."""

    # ── Identity ──
    report_id: str = field(default_factory=lambda: str(uuid4()))
    result_id: str = ""
    request_id: str = ""
    simulation_result_id: str = ""

    # ── Content ──
    summary: ReportSummary = field(default_factory=ReportSummary)
    rule_results: List[CheckResult] = field(default_factory=list)
    evidence_references: List[EvidenceReference] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_by: str = "phase6_1_l22_validator"

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
            "report_id": self.report_id,
            "result_id": self.result_id,
            "request_id": self.request_id,
            "simulation_result_id": self.simulation_result_id,
            "summary": self.summary.to_dict(),
            "rule_results": [c.to_dict() for c in self.rule_results],
            "evidence_references": [r.to_dict() for r in self.evidence_references],
            "recommendations": self.recommendations,
            "generated_by": self.generated_by,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationReport":
        return cls(
            report_id=data.get("report_id", ""),
            result_id=data.get("result_id", ""),
            request_id=data.get("request_id", ""),
            simulation_result_id=data.get("simulation_result_id", ""),
            summary=ReportSummary.from_dict(data.get("summary", {})),
            rule_results=[
                CheckResult.from_dict(c) for c in data.get("rule_results", [])
            ],
            evidence_references=[
                EvidenceReference.from_dict(r)
                for r in data.get("evidence_references", [])
            ],
            recommendations=data.get("recommendations", []),
            generated_by=data.get("generated_by", "phase6_1_l22_validator"),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            is_hypothetical=data.get("is_hypothetical", True),
            shadow_version=data.get("shadow_version", "1.0"),
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return (
            f"ValidationReport(id={self.report_id[:8]}..., "
            f"status={self.summary.overall_status}, "
            f"rules={len(self.rule_results)})"
        )
