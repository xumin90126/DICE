"""
ExperienceGraph — the central graph data structure.

Manages nodes and edges with type-safe queries and serialization.
This is the runtime representation of the capability evolution graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from dice.graph.nodes import (
    Observation, Evidence, Pattern, CapabilityCandidate,
    Capability, Implementation, Rule, Evolution, Fix,
)
from dice.graph.edges import Edge, EdgeType, EDGE_CONSTRAINTS


@dataclass
class ExperienceGraph:
    """
    The central graph storing all DICE entities and their relationships.

    Key queries:
    - get_evidence_for_pattern(pattern_id) → list[Evidence]
    - get_capability_lineage(capability_id) → list[Capability] (supersede chain)
    - find_applicable_capabilities(document_context) → list[Capability]
    """

    # ── Node Storage (by type) ──
    observations: dict[str, Observation] = field(default_factory=dict)
    evidences: dict[str, Evidence] = field(default_factory=dict)
    patterns: dict[str, Pattern] = field(default_factory=dict)
    candidates: dict[str, CapabilityCandidate] = field(default_factory=dict)
    capabilities: dict[str, Capability] = field(default_factory=dict)
    implementations: dict[str, Implementation] = field(default_factory=dict)
    rules: dict[str, Rule] = field(default_factory=dict)
    evolutions: dict[str, Evolution] = field(default_factory=dict)
    fixes: dict[str, Fix] = field(default_factory=dict)
    documents: dict[str, Any] = field(default_factory=dict)   # placeholder for document nodes

    # ── Edge Storage ──
    edges: list[Edge] = field(default_factory=list)

    # ── Metadata ──
    name: str = "experience_graph"
    version: str = "1.0"

    # ────────────────────────── Node Management ──────────────────────────

    def add_observation(self, obs: Observation) -> None:
        self.observations[obs.id] = obs

    def add_evidence(self, evd: Evidence) -> None:
        self.evidences[evd.id] = evd

    def add_pattern(self, pat: Pattern) -> None:
        self.patterns[pat.id] = pat

    def add_candidate(self, cand: CapabilityCandidate) -> None:
        self.candidates[cand.id] = cand

    def add_capability(self, cap: Capability) -> None:
        self.capabilities[cap.id] = cap

    def add_implementation(self, impl: Implementation) -> None:
        self.implementations[impl.id] = impl

    def add_rule(self, rule: Rule) -> None:
        self.rules[rule.id] = rule

    def add_evolution(self, evo: Evolution) -> None:
        self.evolutions[evo.id] = evo

    def add_fix(self, fix: Fix) -> None:
        self.fixes[fix.id] = fix

    def add_document(self, doc_id: str, doc_data: dict[str, Any]) -> None:
        self.documents[doc_id] = doc_data

    # ────────────────────────── Edge Management ──────────────────────────

    def add_edge(self, edge: Edge) -> tuple[bool, Optional[str]]:
        """Add an edge, validating type constraints. Returns (success, error)."""
        valid, err = edge.is_valid()
        if not valid:
            return False, err
        self.edges.append(edge)
        return True, None

    def add_edges(self, edges: list[Edge]) -> list[str]:
        """Batch add edges, returning errors for invalid ones."""
        errors = []
        for edge in edges:
            ok, err = self.add_edge(edge)
            if not ok:
                errors.append(f"{edge.id}: {err}")
        return errors

    # ────────────────────────── Queries ──────────────────────────

    def get_edges_by_type(self, edge_type: EdgeType) -> list[Edge]:
        return [e for e in self.edges if e.edge_type == edge_type]

    def get_outgoing(self, source_id: str, edge_type: Optional[EdgeType] = None) -> list[Edge]:
        results = [e for e in self.edges if e.source_id == source_id]
        if edge_type:
            results = [e for e in results if e.edge_type == edge_type]
        return results

    def get_incoming(self, target_id: str, edge_type: Optional[EdgeType] = None) -> list[Edge]:
        results = [e for e in self.edges if e.target_id == target_id]
        if edge_type:
            results = [e for e in results if e.edge_type == edge_type]
        return results

    def get_evidence_for_pattern(self, pattern_id: str) -> list[Evidence]:
        """Get all evidence supporting a specific pattern."""
        evidence_edges = self.get_incoming(pattern_id, EdgeType.EVIDENCE_FOR)
        return [
            self.evidences[e.source_id]
            for e in evidence_edges
            if e.source_id in self.evidences
        ]

    def get_patterns_for_capability(self, capability_id: str) -> list[Pattern]:
        """Get patterns associated with a capability via candidates."""
        cap = self.capabilities.get(capability_id)
        if not cap:
            return []
        patterns = []
        for pat_id in cap.pattern_ids:
            if pat_id in self.patterns:
                patterns.append(self.patterns[pat_id])
        return patterns

    def get_capability_lineage(self, capability_id: str) -> list[Capability]:
        """Trace the supersede chain (EVOLVED_FROM) for a capability."""
        lineage = []
        current_id = capability_id
        visited = set()
        while current_id and current_id not in visited:
            visited.add(current_id)
            cap = self.capabilities.get(current_id)
            if cap:
                lineage.append(cap)
                current_id = cap.previous_version_id
            else:
                break
        return lineage

    def get_implementations_for_capability(self, capability_id: str) -> list[Implementation]:
        impl_edges = self.get_incoming(capability_id, EdgeType.IMPLEMENTS)
        return [
            self.implementations[e.source_id]
            for e in impl_edges
            if e.source_id in self.implementations
        ]

    # ────────────────────────── Statistics ──────────────────────────

    def node_count(self) -> int:
        return (
            len(self.observations)
            + len(self.evidences)
            + len(self.patterns)
            + len(self.candidates)
            + len(self.capabilities)
            + len(self.implementations)
            + len(self.rules)
            + len(self.evolutions)
            + len(self.fixes)
        )

    def edge_count(self) -> int:
        return len(self.edges)

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "nodes": {
                "observations": len(self.observations),
                "evidences": len(self.evidences),
                "patterns": len(self.patterns),
                "candidates": len(self.candidates),
                "capabilities": len(self.capabilities),
                "implementations": len(self.implementations),
                "rules": len(self.rules),
                "evolutions": len(self.evolutions),
                "fixes": len(self.fixes),
            },
            "edges": self.edge_count(),
            "edge_types": {
                et.value: len(self.get_edges_by_type(et))
                for et in EdgeType
            },
            "verified_patterns": sum(
                1 for p in self.patterns.values()
                if p.status.value == "verified"
            ),
            "active_capabilities": sum(
                1 for c in self.capabilities.values()
                if c.status.value in ("beta", "active")
            ),
        }

    # ────────────────────────── Serialization ──────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Full serialization of graph state."""
        return {
            "meta": {
                "name": self.name,
                "version": self.version,
                "summary": self.summary(),
            },
            "nodes": {
                "observations": [asdict(o) for o in self.observations.values()],
                "evidences": [asdict(e) for e in self.evidences.values()],
                "patterns": [p.to_dict() for p in self.patterns.values()],
                "candidates": [asdict(c) for c in self.candidates.values()],
                "capabilities": [c.to_dict() for c in self.capabilities.values()],
                "implementations": [asdict(i) for i in self.implementations.values()],
                "rules": [asdict(r) for r in self.rules.values()],
                "evolutions": [asdict(ev) for ev in self.evolutions.values()],
                "fixes": [asdict(f) for f in self.fixes.values()],
            },
            "edges": [
                {
                    "id": e.id,
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "edge_type": e.edge_type.value,
                    "source_type": e.source_type,
                    "target_type": e.target_type,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
        }
