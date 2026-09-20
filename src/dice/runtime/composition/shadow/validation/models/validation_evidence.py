"""
Phase 6.1-L2.2: ValidationEvidence — DESIGN_ONLY Data Model.

Evidence collected during the validation phase — a read-only copy from
L2.1 Evidence Snapshot + read-only Trace references. Never mutates the
source L2.1 artifacts.

Fields:
    evidence_id:       Unique evidence identifier
    request_id:        Associated ValidationRequest ID
    source_snapshot:   Read-only copy of L2.1 SimulationEvidenceSnapshot
    source_trace_ref:  Read-only Trace reference (trace_id)
    source_result_ref: Read-only Result reference (result_id)
    incomplete:        Whether the evidence is incomplete
    missing_fields:    Missing field names (when incomplete)
    shadow_marked:     Always True
    origin:            Always "composition_shadow_storage"
    is_hypothetical:   Always True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class ValidationEvidence:
    """Validation evidence — read-only copy of shadow source artifacts."""

    # ── Identity ──
    evidence_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: str = ""

    # ── Source (read-only, copied) ──
    source_snapshot: Dict[str, Any] = field(default_factory=dict)
    source_trace_ref: str = ""
    source_result_ref: str = ""

    # ── Completeness ──
    incomplete: bool = False
    missing_fields: List[str] = field(default_factory=list)

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
            "evidence_id": self.evidence_id,
            "request_id": self.request_id,
            "source_snapshot": self.source_snapshot,
            "source_trace_ref": self.source_trace_ref,
            "source_result_ref": self.source_result_ref,
            "incomplete": self.incomplete,
            "missing_fields": self.missing_fields,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationEvidence":
        return cls(
            evidence_id=data.get("evidence_id", ""),
            request_id=data.get("request_id", ""),
            source_snapshot=data.get("source_snapshot", {}),
            source_trace_ref=data.get("source_trace_ref", ""),
            source_result_ref=data.get("source_result_ref", ""),
            incomplete=data.get("incomplete", False),
            missing_fields=data.get("missing_fields", []),
            shadow_marked=data.get("shadow_marked", True),
            origin=data.get("origin", "composition_shadow_storage"),
            is_hypothetical=data.get("is_hypothetical", True),
            shadow_version=data.get("shadow_version", "1.0"),
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return (
            f"ValidationEvidence(id={self.evidence_id[:8]}..., "
            f"request={self.request_id[:8]}..., "
            f"incomplete={self.incomplete})"
        )
