"""
ShadowValidationResult — Shadow Validator output.

Phase 6.1-L3: Validates ShadowCompositionCandidate across 5 dimensions.
Checks isolation, production impact, trace completeness, governance
compliance, and rollback capability.

NEVER blocks production. NEVER triggers approval chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ValidationDimension(Enum):
    """Five validation dimensions for shadow composition candidates."""
    ISOLATION = "isolation"                     # Data isolation
    NO_PRODUCTION_IMPACT = "no_production_impact"  # Zero production side effects
    TRACE_COMPLETENESS = "trace_completeness"     # Full traceability
    GOVERNANCE_COMPLIANCE = "governance_compliance"  # Governance rules
    ROLLBACK_CAPABILITY = "rollback_capability"    # Rollback readiness


class ValidationStatus(Enum):
    """Per-dimension or overall validation status."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class Violation:
    """A single validation violation found during checking."""
    violation_type: str = ""
    severity: str = "LOW"  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    description: str = ""
    dimension: str = ""


@dataclass
class DimensionResult:
    """Result of a single validation dimension check."""
    dimension: str = ""
    status: str = "PASS"  # "PASS" | "WARNING" | "FAIL"
    score: float = 0.0
    details: str = ""
    violations: List[Violation] = field(default_factory=list)


@dataclass
class ShadowValidationResult:
    """Complete validation result for a shadow composition candidate.

    Fields:
        validation_id: Unique validation record identifier
        candidate_id: Associated ShadowCompositionCandidate ID
        timestamp: Validation completion timestamp
        overall_status: Overall validation status (PASS/WARNING/FAIL)
        dimension_results: Per-dimension validation results (5 dimensions)
        governance_check: Governance compliance check result
        validation_summary: Human-readable summary
        shadow_marked: Always True
    """

    # ── Identity ──
    validation_id: str = field(default_factory=lambda: str(uuid4()))
    candidate_id: str = ""

    # ── Timing ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ── Overall Status ──
    overall_status: str = "PASS"  # "PASS" | "WARNING" | "FAIL"

    # ── Dimension Results ──
    dimension_results: List[DimensionResult] = field(default_factory=list)

    # ── Governance Check ──
    governance_check: Optional[Dict[str, Any]] = None

    # ── Summary ──
    validation_summary: str = ""

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed_dimensions(self) -> int:
        """Count of PASS dimensions."""
        return sum(1 for d in self.dimension_results if d.status == "PASS")

    @property
    def warning_dimensions(self) -> int:
        """Count of WARNING dimensions."""
        return sum(1 for d in self.dimension_results if d.status == "WARNING")

    @property
    def failed_dimensions(self) -> int:
        """Count of FAIL dimensions."""
        return sum(1 for d in self.dimension_results if d.status == "FAIL")

    @property
    def total_violations(self) -> int:
        """Total number of violations across all dimensions."""
        return sum(len(d.violations) for d in self.dimension_results)

    @property
    def critical_violations(self) -> int:
        """Count of CRITICAL severity violations."""
        return sum(
            1 for d in self.dimension_results
            for v in d.violations
            if v.severity == "CRITICAL"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "candidate_id": self.candidate_id,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status,
            "dimension_results": [
                {
                    "dimension": d.dimension,
                    "status": d.status,
                    "score": d.score,
                    "details": d.details,
                    "violations": [
                        {
                            "violation_type": v.violation_type,
                            "severity": v.severity,
                            "description": v.description,
                            "dimension": v.dimension,
                        }
                        for v in d.violations
                    ],
                }
                for d in self.dimension_results
            ],
            "governance_check": self.governance_check,
            "validation_summary": self.validation_summary,
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShadowValidationResult":
        result = cls(
            validation_id=data.get("validation_id", ""),
            candidate_id=data.get("candidate_id", ""),
            timestamp=data.get("timestamp", ""),
            overall_status=data.get("overall_status", "PASS"),
            validation_summary=data.get("validation_summary", ""),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            metadata=data.get("metadata", {}),
            governance_check=data.get("governance_check"),
        )
        result.dimension_results = [
            DimensionResult(
                dimension=d.get("dimension", ""),
                status=d.get("status", "PASS"),
                score=d.get("score", 0.0),
                details=d.get("details", ""),
                violations=[
                    Violation(
                        violation_type=v.get("violation_type", ""),
                        severity=v.get("severity", "LOW"),
                        description=v.get("description", ""),
                        dimension=v.get("dimension", ""),
                    )
                    for v in d.get("violations", [])
                ],
            )
            for d in data.get("dimension_results", [])
        ]
        return result

    def __repr__(self) -> str:
        return (
            f"ShadowValidationResult(id={self.validation_id[:8]}..., "
            f"candidate={self.candidate_id[:8]}..., "
            f"status={self.overall_status}, "
            f"dims={self.passed_dimensions}P/{self.warning_dimensions}W/"
            f"{self.failed_dimensions}F, "
            f"violations={self.total_violations})"
        )