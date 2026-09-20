"""
ShadowGovernanceCheck — Governance observation for Shadow pipeline.

Phase 6.1-L4: Records governance and boundary compliance checks for
the Shadow pipeline itself. Verifies that Shadow operations remain
read-only, isolated, and non-production.

NEVER triggers real approval chain. NEVER activates capabilities.
Always marked SHADOW_ONLY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class GovernanceStatus(Enum):
    """Overall governance compliance status."""
    COMPLIANT = "COMPLIANT"           # All checks passed
    NON_COMPLIANT = "NON_COMPLIANT"   # Violations detected
    NEEDS_REVIEW = "NEEDS_REVIEW"     # Requires human review


@dataclass
class BoundaryViolation:
    """A single boundary violation detected during governance check.

    Fields:
        violation_type: Type of violation
        severity: Severity level (LOW/MEDIUM/HIGH/CRITICAL)
        description: Human-readable description
        stack_trace: Debug stack trace (optional)
    """
    violation_type: str = ""  # PRODUCTION_WRITE | PRODUCTION_READ | REGISTRY_MODIFY | RUNTIME_MODIFY | EXECUTION_ATTEMPT | PERMISSION_ESCALATION
    severity: str = "LOW"     # LOW | MEDIUM | HIGH | CRITICAL
    description: str = ""
    stack_trace: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_type": self.violation_type,
            "severity": self.severity,
            "description": self.description,
            "stack_trace": self.stack_trace,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoundaryViolation":
        return cls(
            violation_type=data.get("violation_type", ""),
            severity=data.get("severity", "LOW"),
            description=data.get("description", ""),
            stack_trace=data.get("stack_trace", ""),
        )


@dataclass
class StorageAudit:
    """Storage namespace audit information."""
    storage_namespace: str = "composition_shadow_storage"
    total_records: int = 0
    production_cross_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "storage_namespace": self.storage_namespace,
            "total_records": self.total_records,
            "production_cross_refs": self.production_cross_refs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StorageAudit":
        return cls(
            storage_namespace=data.get("storage_namespace", "composition_shadow_storage"),
            total_records=data.get("total_records", 0),
            production_cross_refs=data.get("production_cross_refs", []),
        )


@dataclass
class ShadowGovernanceCheck:
    """Governance observation for a Shadow pipeline execution.

    Records what governance checks were performed, any boundary violations
    detected, and the isolation status of the Shadow storage.

    Fields:
        governance_id: Unique governance record identifier (UUID)
        pipeline_id: Associated pipeline run ID
        timestamp: Check completion timestamp
        boundary_violations: Detected boundary violations (empty = clean)
        isolation_status: Storage isolation status
        storage_audit: Storage namespace audit info
        shadow_marked: Always True
    """

    # ── Identity ──
    governance_id: str = field(default_factory=lambda: str(uuid4()))
    pipeline_id: str = ""

    # ── Timing ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ── Boundary Violations ──
    boundary_violations: List[BoundaryViolation] = field(default_factory=list)

    # ── Isolation Status ──
    isolation_status: str = "ISOLATED"  # ISOLATED | WARNING | CONTAMINATED

    # ── Storage Audit ──
    storage_audit: StorageAudit = field(default_factory=StorageAudit)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def violation_count(self) -> int:
        """Total number of boundary violations."""
        return len(self.boundary_violations)

    @property
    def critical_violations(self) -> int:
        """Count of CRITICAL severity violations."""
        return sum(1 for v in self.boundary_violations if v.severity == "CRITICAL")

    @property
    def is_contaminated(self) -> bool:
        """True if isolation status is CONTAMINATED."""
        return self.isolation_status == "CONTAMINATED"

    @property
    def governance_status(self) -> str:
        """Derived governance status based on violations."""
        if self.critical_violations > 0:
            return "NON_COMPLIANT"
        if self.violation_count > 0:
            return "NEEDS_REVIEW"
        if self.is_contaminated:
            return "NON_COMPLIANT"
        return "COMPLIANT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "governance_id": self.governance_id,
            "pipeline_id": self.pipeline_id,
            "timestamp": self.timestamp,
            "boundary_violations": [v.to_dict() for v in self.boundary_violations],
            "isolation_status": self.isolation_status,
            "storage_audit": self.storage_audit.to_dict(),
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShadowGovernanceCheck":
        check = cls(
            governance_id=data.get("governance_id", ""),
            pipeline_id=data.get("pipeline_id", ""),
            timestamp=data.get("timestamp", ""),
            isolation_status=data.get("isolation_status", "ISOLATED"),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            metadata=data.get("metadata", {}),
        )
        check.boundary_violations = [
            BoundaryViolation.from_dict(v)
            for v in data.get("boundary_violations", [])
        ]
        sa = data.get("storage_audit")
        if sa:
            check.storage_audit = StorageAudit.from_dict(sa)
        return check

    def __repr__(self) -> str:
        return (
            f"ShadowGovernanceCheck(id={self.governance_id[:8]}..., "
            f"violations={self.violation_count}, "
            f"status={self.governance_status}, "
            f"isolation={self.isolation_status})"
        )