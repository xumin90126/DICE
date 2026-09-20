"""
ShadowMetricRecord — Shadow Runtime metrics observation.

Phase 6.1-L4: Records Shadow Runtime health metrics — observation
counts, validation counts, trace counts, error counts. These are
purely observational, never used for production routing decisions.

NEVER influences production execution. Always marked SHADOW_ONLY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


@dataclass
class ShadowMetricRecord:
    """Shadow Runtime metric snapshot.

    Records a point-in-time snapshot of Shadow Runtime health and
    activity metrics. L1 records only basic counters:
    observation_count, validation_count, trace_count, error_count.

    Fields:
        metric_id: Unique metric record identifier (UUID)
        timestamp: Metric capture timestamp
        observation_count: Total ShadowObservations captured
        validation_count: Total ShadowValidationResults generated
        trace_count: Total ShadowTraceRecords generated
        error_count: Total errors encountered
        health_status: Health indicator (GREEN/YELLOW/RED)
        shadow_marked: Always True
    """

    # ── Identity ──
    metric_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Timing ──
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ── L1 Basic Counters ──
    observation_count: int = 0
    validation_count: int = 0
    trace_count: int = 0
    error_count: int = 0

    # ── Health ──
    health_status: str = "GREEN"  # GREEN | YELLOW | RED

    # ── Shadow Marker ──
    shadow_marked: bool = True
    shadow_version: str = "1.0"
    origin: str = "composition_shadow_storage"

    # ── Metadata ──
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_operations(self) -> int:
        """Total number of operations (observation + validation + trace)."""
        return self.observation_count + self.validation_count + self.trace_count

    @property
    def error_rate(self) -> float:
        """Error rate as a fraction of total operations."""
        if self.total_operations == 0:
            return 0.0
        return self.error_count / self.total_operations

    def derive_health(self) -> str:
        """Derive health status based on error rate."""
        if self.error_rate > 0.10:
            return "RED"
        if self.error_rate > 0.01:
            return "YELLOW"
        return "GREEN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "timestamp": self.timestamp,
            "observation_count": self.observation_count,
            "validation_count": self.validation_count,
            "trace_count": self.trace_count,
            "error_count": self.error_count,
            "health_status": self.health_status,
            "shadow_marked": self.shadow_marked,
            "shadow_version": self.shadow_version,
            "origin": self.origin,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShadowMetricRecord":
        return cls(
            metric_id=data.get("metric_id", ""),
            timestamp=data.get("timestamp", ""),
            observation_count=data.get("observation_count", 0),
            validation_count=data.get("validation_count", 0),
            trace_count=data.get("trace_count", 0),
            error_count=data.get("error_count", 0),
            health_status=data.get("health_status", "GREEN"),
            shadow_marked=data.get("shadow_marked", True),
            shadow_version=data.get("shadow_version", "1.0"),
            origin=data.get("origin", "composition_shadow_storage"),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"ShadowMetricRecord(id={self.metric_id[:8]}..., "
            f"obs={self.observation_count}, "
            f"val={self.validation_count}, "
            f"trace={self.trace_count}, "
            f"err={self.error_count}, "
            f"health={self.health_status})"
        )