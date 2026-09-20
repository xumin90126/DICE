"""
Edge types for the Experience Graph.

12 edge types connecting the core entities:
    Observation → Evidence → Pattern → CapabilityCandidate → Capability
                                                                     ↓
                                                               Implementation
                                                                     ↓
                                                                   Rule

Plus auxiliary edges for Evolution and Fix tracking.

Each edge type has a semantic meaning and enforces valid source/target types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class EdgeType(str, Enum):
    # ── Core Capability Chain ──
    OBSERVED_IN = "OBSERVED_IN"          # Observation → Document
    EVIDENCE_FOR = "EVIDENCE_FOR"        # Evidence → Pattern
    DERIVED_FROM = "DERIVED_FROM"        # Evidence → Observation
    SUPPORTS = "SUPPORTS"                # Pattern → CapabilityCandidate

    # ── Capability Hierarchy ──
    GENERALIZES = "GENERALIZES"          # CapabilityCandidate → Pattern (abstracts from)
    IMPLEMENTS = "IMPLEMENTS"            # Implementation → Capability
    HAS_RULE = "HAS_RULE"                # Implementation → Rule

    # ── Evolution ──
    EVOLVED_FROM = "EVOLVED_FROM"        # Capability v(N+1) → Capability v(N)
    TRIGGERED_BY = "TRIGGERED_BY"        # Evolution → Pattern (what triggered)

    # ── Fix (auxiliary) ──
    FIXED_BY = "FIXED_BY"                # Observation → Fix

    # ── Cross-Reference ──
    APPLIES_TO = "APPLIES_TO"            # Capability → Document (capability applied)
    CONFIRMS = "CONFIRMS"                # Evidence → Pattern (positive support)
    CONTRADICTS = "CONTRADICTS"          # Evidence → Pattern (negative evidence)

    # ── Pattern → Capability linkage (Phase 3.3) ──
    PATTERN_SUPPORTS = "PATTERN_SUPPORTS"  # Pattern → Capability (structural support)


# Valid source→target type mappings per edge type
EDGE_CONSTRAINTS: dict[EdgeType, tuple[str, str]] = {
    EdgeType.OBSERVED_IN:     ("Observation", "Document"),
    EdgeType.EVIDENCE_FOR:    ("Evidence", "Pattern"),
    EdgeType.DERIVED_FROM:    ("Evidence", "Observation"),
    EdgeType.SUPPORTS:        ("Pattern", "CapabilityCandidate"),
    EdgeType.GENERALIZES:     ("CapabilityCandidate", "Pattern"),
    EdgeType.IMPLEMENTS:      ("Implementation", "Capability"),
    EdgeType.HAS_RULE:        ("Implementation", "Rule"),
    EdgeType.EVOLVED_FROM:    ("Capability", "Capability"),
    EdgeType.TRIGGERED_BY:    ("Evolution", "Pattern"),
    EdgeType.FIXED_BY:        ("Observation", "Fix"),
    EdgeType.APPLIES_TO:      ("Capability", "Document"),
    EdgeType.CONFIRMS:        ("Evidence", "Pattern"),
    EdgeType.CONTRADICTS:     ("Evidence", "Pattern"),
    EdgeType.PATTERN_SUPPORTS: ("Pattern", "Capability"),
}


@dataclass
class Edge:
    """A directed edge in the Experience Graph."""
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.EVIDENCE_FOR
    source_type: str = ""                    # runtime type tag of source node
    target_type: str = ""                    # runtime type tag of target node
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def is_valid(self) -> tuple[bool, Optional[str]]:
        """Check if this edge respects type constraints."""
        constraint = EDGE_CONSTRAINTS.get(self.edge_type)
        if constraint is None:
            return False, f"Unknown edge type: {self.edge_type}"
        expected_source, expected_target = constraint
        if self.source_type != expected_source:
            return False, (
                f"Invalid source type '{self.source_type}' for {self.edge_type.value}. "
                f"Expected '{expected_source}'"
            )
        if self.target_type != expected_target:
            return False, (
                f"Invalid target type '{self.target_type}' for {self.edge_type.value}. "
                f"Expected '{expected_target}'"
            )
        return True, None


def get_edge_types_for_source(source_type: str) -> list[EdgeType]:
    """Get all valid outgoing edge types for a given source type."""
    return [
        et for et, (src, _) in EDGE_CONSTRAINTS.items()
        if src == source_type
    ]


def get_edge_types_for_target(target_type: str) -> list[EdgeType]:
    """Get all valid incoming edge types for a given target type."""
    return [
        et for et, (_, tgt) in EDGE_CONSTRAINTS.items()
        if tgt == target_type
    ]
