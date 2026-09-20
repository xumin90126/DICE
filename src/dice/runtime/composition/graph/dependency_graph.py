"""
Phase 6.0: Capability Dependency Graph — Skeleton

Design Artifact 1: Models dependency relationships between Capabilities.
Used by CompositionPlanner to determine valid composition candidates.

STATUS: DESIGN_ONLY
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

__all__ = [
    "DependencyType",
    "CapabilityNode",
    "CapabilityRelation",
    "CapabilityDependencyGraph",
]

# ═══════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════


class DependencyType(Enum):
    """Types of dependency between capabilities."""

    REQUIRES = "requires"          # A must execute before B
    CONFLICTS = "conflicts"         # A and B cannot coexist
    ENHANCES = "enhances"           # A improves B's output
    ALTERNATIVE = "alternative"     # A can replace B
    COMPOSES_WITH = "composes_with" # A and B can be composed together


# ═══════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CapabilityNode:
    """A node in the dependency graph representing a Capability."""

    capability_id: str
    name: str = ""
    version: str = "1.0.0"
    dependencies: Set[str] = field(default_factory=set)    # capability_ids this depends on
    dependents: Set[str] = field(default_factory=set)       # capability_ids that depend on this
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityRelation:
    """A directed edge between two CapabilityNodes."""

    source: str                      # source capability_id
    target: str                      # target capability_id
    relation_type: DependencyType = DependencyType.REQUIRES
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityDependencyGraph:
    """The complete dependency graph of all registered Capabilities.

    Phase 6.0: Schema definition only. Graph is empty until Phase 6.1.
    """

    nodes: Dict[str, CapabilityNode] = field(default_factory=dict)
    relations: List[CapabilityRelation] = field(default_factory=list)
    version: str = "6.0.0-skeleton"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ═══════════════════════════════════════════════════════════════════════
    # Interface Contract (NOT_IMPLEMENTED)
    # ═══════════════════════════════════════════════════════════════════════

    def add_node(self, capability_id: str, name: str = "", **kwargs) -> None:
        """Add a capability node to the graph.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        Phase 6.1+: Build from CapabilityRegistry.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. add_node() will be implemented in Phase 6.1 "
            "to build graph from CapabilityRegistry."
        )

    def add_relation(
        self,
        source: str,
        target: str,
        relation_type: DependencyType = DependencyType.REQUIRES,
        **kwargs,
    ) -> None:
        """Add a relation between two capability nodes.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. add_relation() will be implemented in Phase 6.1."
        )

    def query_dependencies(self, capability_id: str) -> List[CapabilityRelation]:
        """Query all dependencies for a given capability.

        Returns:
            List of relations where the capability is the source.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. query_dependencies() will be implemented in Phase 6.1."
        )

    def query_dependents(self, capability_id: str) -> List[CapabilityRelation]:
        """Query all capabilities that depend on the given capability.

        Returns:
            List of relations where the capability is the target.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. query_dependents() will be implemented in Phase 6.1."
        )

    def detect_conflict(
        self, capability_ids: List[str]
    ) -> List[CapabilityRelation]:
        """Detect conflicts among a set of capabilities.

        Returns:
            List of conflicting relations (CONFLICTS type).

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. detect_conflict() will be implemented in Phase 6.1."
        )

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in the graph.

        Returns:
            List of cycles, each cycle is a list of capability_ids.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. detect_cycles() will be implemented in Phase 6.1."
        )

    def get_composition_candidates(
        self, capability_ids: List[str]
    ) -> List[List[str]]:
        """Find valid composition candidates that include the given capabilities.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. get_composition_candidates() will be implemented in Phase 6.1."
        )

    def export_graph(self) -> Dict[str, Any]:
        """Export the graph as a serializable dictionary.

        Phase 6.0: NOT_IMPLEMENTED — placeholder only.
        """
        raise NotImplementedError(
            "Phase 6.0: DESIGN_ONLY. export_graph() will be implemented in Phase 6.1."
        )

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return (
            f"CapabilityDependencyGraph(nodes={len(self.nodes)}, "
            f"relations={len(self.relations)}, status=DESIGN_ONLY)"
        )