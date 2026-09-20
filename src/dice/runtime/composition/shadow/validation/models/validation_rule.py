"""
Phase 6.1-L2.2: ValidationRule — DESIGN_ONLY Data Model.

Defines a single validation rule (read-only rule definition, NOT an
execution result). Rules are contract-driven (C4) and carry a Purpose
and a declared check logic description (plain text, never code).

Fields:
    rule_id:       Unique rule identifier
    rule_name:     Human-readable rule name
    rule_type:     RuleType (ISOLATION/COVERAGE/CONSISTENCY/BOUNDARY)
    description:   Rule description (Purpose)
    severity:      RuleSeverity (CRITICAL/WARNING/INFO)
    target:        Validation target (candidate/scenario/metadata)
    check_logic:   Plain-text check logic description (not code)
    enabled:       Whether the rule is enabled
    params:        Rule parameters (thresholds etc.)
    shadow_marked: Always True
    origin:        Always "composition_shadow_storage"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class RuleType(Enum):
    """Validation rule types (contract-driven dimensions)."""

    ISOLATION = "isolation"
    COVERAGE = "coverage"
    CONSISTENCY = "consistency"
    BOUNDARY = "boundary"


class RuleSeverity(Enum):
    """Validation rule severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """Validation rule — read-only definition, never an execution result."""

    # ── Identity ──
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    rule_name: str = ""

    # ── Classification ──
    rule_type: RuleType = RuleType.ISOLATION
    description: str = ""
    severity: RuleSeverity = RuleSeverity.CRITICAL
    target: str = "candidate"

    # ── Logic Declaration (plain text, never code) ──
    check_logic: str = ""

    # ── State ──
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    shadow_version: str = "1.0"

    # ── Metadata ──
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_type": self.rule_type.value,
            "description": self.description,
            "severity": self.severity.value,
            "target": self.target,
            "check_logic": self.check_logic,
            "enabled": self.enabled,
            "params": self.params,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "shadow_version": self.shadow_version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRule":
        return cls(
            rule_id=data.get("rule_id", ""),
            rule_name=data.get("rule_name", ""),
            rule_type=RuleType(data.get("rule_type", "isolation")),
            description=data.get("description", ""),
            severity=RuleSeverity(data.get("severity", "critical")),
            target=data.get("target", "candidate"),
            check_logic=data.get("check_logic", ""),
            enabled=data.get("enabled", True),
            params=data.get("params", {}),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            shadow_version=data.get("shadow_version", "1.0"),
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return (
            f"ValidationRule(id={self.rule_id[:8]}..., "
            f"name={self.rule_name}, "
            f"type={self.rule_type.value}, "
            f"severity={self.severity.value})"
        )
