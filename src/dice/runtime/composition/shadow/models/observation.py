"""
ShadowObservation — Production Runtime output snapshot.

Captured by ShadowObserver, contains a read-only snapshot of Evidence
and Capability Match results from the production Runtime (Layer 1-8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class EvidenceSnapshot:
    """A read-only snapshot of a single EvidenceResult from production."""
    evidence_id: str = ""
    evidence_type: str = ""
    span_text: str = ""
    confidence: float = 0.0
    source_capability: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityMatchSnapshot:
    """A read-only snapshot of a CapabilityMatchResult from production."""
    capability_id: str = ""
    capability_name: str = ""
    match_score: float = 0.0
    matched_patterns: List[str] = field(default_factory=list)
    execution_decision: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShadowObservation:
    """Production Runtime output snapshot captured by ShadowObserver.

    This is the immutable input to the Shadow pipeline. It records WHAT
    the production Runtime saw, without modifying or filtering it.

    Fields:
        observation_id: Unique observation identifier (UUID)
        document_id: Source document identifier
        document_type: Document type (e.g. "IFU", "SOP")
        timestamp: Capture timestamp (ISO 8601)
        production_trace_id: Corresponding production Trace ID (for cross-reference)
        evidence_results: Read-only snapshots of EvidenceResult outputs
        capability_matches: Read-only snapshots of CapabilityMatchResult outputs
        shadow_marked: Always True — marks this as SHADOW_ONLY
    """

    # ── Identity ──
    observation_id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    document_type: str = ""

    # ── Timing ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    production_trace_id: Optional[str] = None

    # ── Production Snapshots (read-only) ──
    evidence_results: List[EvidenceSnapshot] = field(default_factory=list)
    capability_matches: List[CapabilityMatchSnapshot] = field(default_factory=list)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def evidence_count(self) -> int:
        """Number of captured evidence snapshots."""
        return len(self.evidence_results)

    @property
    def match_count(self) -> int:
        """Number of captured capability match snapshots."""
        return len(self.capability_matches)

    @property
    def matched_capability_ids(self) -> List[str]:
        """Unique capability IDs found in matches."""
        return list({m.capability_id for m in self.capability_matches
                     if m.capability_id})

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            "observation_id": self.observation_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "timestamp": self.timestamp,
            "production_trace_id": self.production_trace_id,
            "evidence_results": [
                {
                    "evidence_id": e.evidence_id,
                    "evidence_type": e.evidence_type,
                    "span_text": e.span_text,
                    "confidence": e.confidence,
                    "source_capability": e.source_capability,
                    "metadata": e.metadata,
                }
                for e in self.evidence_results
            ],
            "capability_matches": [
                {
                    "capability_id": m.capability_id,
                    "capability_name": m.capability_name,
                    "match_score": m.match_score,
                    "matched_patterns": m.matched_patterns,
                    "execution_decision": m.execution_decision,
                    "metadata": m.metadata,
                }
                for m in self.capability_matches
            ],
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShadowObservation":
        """Deserialize from dictionary."""
        obs = cls(
            observation_id=data.get("observation_id", ""),
            document_id=data.get("document_id", ""),
            document_type=data.get("document_type", ""),
            timestamp=data.get("timestamp", ""),
            production_trace_id=data.get("production_trace_id"),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            metadata=data.get("metadata", {}),
        )
        obs.evidence_results = [
            EvidenceSnapshot(
                evidence_id=e.get("evidence_id", ""),
                evidence_type=e.get("evidence_type", ""),
                span_text=e.get("span_text", ""),
                confidence=e.get("confidence", 0.0),
                source_capability=e.get("source_capability", ""),
                metadata=e.get("metadata", {}),
            )
            for e in data.get("evidence_results", [])
        ]
        obs.capability_matches = [
            CapabilityMatchSnapshot(
                capability_id=m.get("capability_id", ""),
                capability_name=m.get("capability_name", ""),
                match_score=m.get("match_score", 0.0),
                matched_patterns=m.get("matched_patterns", []),
                execution_decision=m.get("execution_decision", ""),
                metadata=m.get("metadata", {}),
            )
            for m in data.get("capability_matches", [])
        ]
        return obs

    def __repr__(self) -> str:
        return (
            f"ShadowObservation(id={self.observation_id[:8]}..., "
            f"doc={self.document_id}, "
            f"evidence={self.evidence_count}, "
            f"matches={self.match_count}, "
            f"shadow_marked={self.shadow_marked})"
        )