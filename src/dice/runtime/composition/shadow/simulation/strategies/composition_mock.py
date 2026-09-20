"""
Phase 6.1-L2.1: CompositionMock — Simulation Logic (Phase A implemented).

Responsibility:
    Mock the Composition Planner inside the Simulation Engine. Generate
    hypothetical CompositionCandidate objects from a SimulationScenario
    using one of three composition strategies (Simple / Priority / Dependency).

    This is a *mock* — it NEVER invokes the real Layer 9 planner, NEVER
    reads the Capability Registry for execution, and NEVER produces a plan
    that can be activated.

Input:
    - SimulationScenario (built by ScenarioManager)

Output:
    - list[CompositionCandidate] (hypothetical, shadow-only)

Forbidden:
    - ❌ No Capability Registry access
    - ❌ No Runtime 1-8 modification
    - ❌ No production execution
    - ❌ No activation paths
    - ❌ No composition execution (Phase 6.2)

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True (mock output is never applied)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

from ..models import SimulationScenario


class CompositionStrategy:
    """Strategy identifiers for composition mocking."""

    SIMPLE: str = "simple"
    PRIORITY: str = "priority"
    DEPENDENCY: str = "dependency"

    ALL: List[str] = [SIMPLE, PRIORITY, DEPENDENCY]


@dataclass
class CompositionCandidate:
    """Hypothetical composition candidate — shadow-only, never applied.

    Fields:
        candidate_id:     Unique candidate identifier
        capability_ids:   Ordered capability identifier list
        composition_type: sequential | parallel | hierarchical
        score:            Candidate score (0.0 ~ 1.0)
        dependency_path:  Dependency path description
        shadow_marked:    Always True
        is_hypothetical:  Always True
        origin:           Always "composition_shadow_storage"
    """

    # ── Identity ──
    candidate_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Composition ──
    capability_ids: List[str] = field(default_factory=list)
    composition_type: str = ""  # "sequential" | "parallel" | "hierarchical"
    score: float = 0.0
    dependency_path: List[str] = field(default_factory=list)

    # ── Shadow Marker ──
    shadow_marked: bool = True
    is_hypothetical: bool = True
    origin: str = "composition_shadow_storage"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize candidate to a plain dict (pure data, no behavior)."""
        return {
            "candidate_id": self.candidate_id,
            "capability_ids": self.capability_ids,
            "composition_type": self.composition_type,
            "score": self.score,
            "dependency_path": self.dependency_path,
            "shadow_marked": self.shadow_marked,
            "is_hypothetical": self.is_hypothetical,
            "origin": self.origin,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositionCandidate":
        """Deserialize candidate from a plain dict (pure data, no behavior)."""
        return cls(
            candidate_id=data.get("candidate_id", ""),
            capability_ids=data.get("capability_ids", []),
            composition_type=data.get("composition_type", ""),
            score=data.get("score", 0.0),
            dependency_path=data.get("dependency_path", []),
            shadow_marked=data.get("shadow_marked", True),
            is_hypothetical=data.get("is_hypothetical", True),
            origin=data.get("origin", "composition_shadow_storage"),
        )

    def __repr__(self) -> str:
        return (
            f"CompositionCandidate(id={self.candidate_id[:8]}..., "
            f"caps={len(self.capability_ids)}, "
            f"type={self.composition_type}, "
            f"hypothetical={self.is_hypothetical})"
        )


def _score(n: int) -> float:
    """Deterministic hypothetical score in [0.0, 1.0] for n capabilities.

    Purely illustrative — never used for ranking/activation.
    """
    if n <= 0:
        return 0.0
    return round(min(1.0, 0.5 + 0.05 * n), 2)


def _build_candidate(
    capability_ids: List[str],
    composition_type: str,
    dependency_path: List[str],
) -> CompositionCandidate:
    """Construct a shadow-only hypothetical candidate."""
    return CompositionCandidate(
        capability_ids=list(capability_ids),
        composition_type=composition_type,
        score=_score(len(capability_ids)),
        dependency_path=list(dependency_path),
        shadow_marked=True,
        is_hypothetical=True,
        origin="composition_shadow_storage",
    )


class CompositionMock:
    """Mock composition planner. Phase A logic implemented (Shadow-only)."""

    def __init__(self) -> None:
        self._shadow_marked: bool = True
        self._origin: str = "composition_shadow_storage"
        self._strategies: Dict[str, Any] = {}

    def compose(
        self, scenario: SimulationScenario, strategy: str
    ) -> List[CompositionCandidate]:
        """Generate hypothetical composition candidates for a scenario.

        Args:
            scenario: SimulationScenario to compose
            strategy: One of CompositionStrategy.SIMPLE/PRIORITY/DEPENDENCY.
                Any unrecognized value falls back to ``_select_strategy``.

        Returns:
            list[CompositionCandidate] (hypothetical, shadow-only)
        """
        if strategy not in CompositionStrategy.ALL:
            strategy = self._select_strategy(scenario)

        if strategy == CompositionStrategy.SIMPLE:
            return SimpleStrategy().build_plan(scenario)
        if strategy == CompositionStrategy.PRIORITY:
            return PriorityStrategy().build_plan(scenario)
        return DependencyStrategy().build_plan(scenario)

    def _select_strategy(self, scenario: SimulationScenario) -> str:
        """Select a fallback strategy based on scenario characteristics.

        Heuristic (by capability count):
            < 5   → simple      (linear order is sufficient)
            5-15  → priority    (priority ordering matters)
            > 15  → dependency  (dependency graph needed)
        """
        n = len(scenario.capabilities)
        if n < 5:
            return CompositionStrategy.SIMPLE
        if n <= 15:
            return CompositionStrategy.PRIORITY
        return CompositionStrategy.DEPENDENCY


class SimpleStrategy:
    """Linear composition by input (dependency) order."""

    def build_plan(
        self, scenario: SimulationScenario
    ) -> List[CompositionCandidate]:
        """Build a single linear (sequential) candidate in input order."""
        caps = list(scenario.capabilities)
        if not caps:
            return []
        return [
            _build_candidate(
                capability_ids=caps,
                composition_type="sequential",
                dependency_path=caps,
            )
        ]


class PriorityStrategy:
    """Priority-ordered composition (parallel)."""

    def build_plan(
        self, scenario: SimulationScenario
    ) -> List[CompositionCandidate]:
        """Build a single parallel candidate ordered by declared priority.

        Priority is read from ``scenario.parameters["priority"]``, a mapping
        of capability id → int (lower = higher priority). Capabilities without
        a declared priority default to 0 (highest) and keep input order.
        """
        caps = list(scenario.capabilities)
        if not caps:
            return []

        priority_map: Dict[str, int] = scenario.parameters.get("priority", {})
        if not isinstance(priority_map, dict):
            priority_map = {}

        # Stable sort: higher declared priority (smaller int) first.
        ordered = sorted(
            caps,
            key=lambda c: priority_map.get(c, 0),
        )
        return [
            _build_candidate(
                capability_ids=ordered,
                composition_type="parallel",
                dependency_path=[],
            )
        ]


class DependencyStrategy:
    """Dependency-graph-exact composition (hierarchical)."""

    def build_plan(
        self, scenario: SimulationScenario
    ) -> List[CompositionCandidate]:
        """Build a hierarchical candidate via topological ordering.

        Dependencies are read from ``scenario.parameters["dependencies"]``, a
        mapping of capability id → list of prerequisite capability ids.

        Circular dependency detection: if a cycle is found, returns an empty
        plan (safe degradation, no exception escapes the shadow boundary).
        """
        caps = list(scenario.capabilities)
        if not caps:
            return []

        deps: Dict[str, List[str]] = scenario.parameters.get("dependencies", {})
        if not isinstance(deps, dict):
            deps = {}
        for k, v in deps.items():
            deps[k] = [x for x in v if x in caps]

        # Topological sort (Kahn's algorithm) with cycle detection.
        indegree: Dict[str, int] = {c: 0 for c in caps}
        for c, prereqs in deps.items():
            if c in indegree:
                for p in prereqs:
                    if p in indegree:
                        indegree[c] += 1

        from collections import deque

        queue = deque([c for c in caps if indegree[c] == 0])
        ordered: List[str] = []
        while queue:
            node = queue.popleft()
            ordered.append(node)
            for c in caps:
                if node in deps.get(c, []):
                    indegree[c] -= 1
                    if indegree[c] == 0:
                        queue.append(c)

        # Cycle detected → safe degradation.
        if len(ordered) != len(caps):
            return []

        return [
            _build_candidate(
                capability_ids=ordered,
                composition_type="hierarchical",
                dependency_path=ordered,
            )
        ]
