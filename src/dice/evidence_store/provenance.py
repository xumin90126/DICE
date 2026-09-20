"""
Phase 6.10 Pattern Provenance Resolver — classifies patterns by origin.

Determines whether a pattern signal is:
    - production          — genuine business capability pattern
    - candidate           — legitimate candidate awaiting verification
    - discrimination-test — Phase 5.2 test instrumentation
    - validation-only     — validation/internal-use pattern
    - unknown             — cannot classify

DESIGN: Resolver is READ-ONLY. It classifies but NEVER:
    - Modifies CapabilityRegistry
    - Modifies match results
    - Modifies pattern mapping
    - Produces evolution actions

Usage:
    resolver = ProvenanceResolver()
    prov = resolver.resolve(pattern_id, pattern_data)
    # prov = "production" | "discrimination-test" | ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PatternProvenance(str, Enum):
    """Origin classification for pattern signals."""
    PRODUCTION = "production"
    CANDIDATE = "candidate"
    DISCRIMINATION_TEST = "discrimination-test"
    VALIDATION_ONLY = "validation-only"
    UNKNOWN = "unknown"


@dataclass
class ProvenanceResult:
    """Result of provenance classification for a pattern."""
    pattern_id: str = ""
    provenance: PatternProvenance = PatternProvenance.UNKNOWN
    classification_rule: str = ""       # which rule determined the classification
    metadata: dict[str, Any] = field(default_factory=dict)
    # Evidence used for the determination
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_count: int = 0
    status: str = ""                    # PatternStatus value as string


class ProvenanceResolver:
    """
    Resolves pattern provenance — where a pattern came from and
    whether it should participate in evolution.

    PROVENANCE CLASSIFICATION RULES (ordered by priority):

    1. discrimination-test:
       - "discrimination-test" in tags
       - OR (confidence < 0.4 AND evidence_count == 0 AND "discrimination-test" in tags)

    2. validation-only:
       - "validation-only" in tags
       - OR tags contain "validation-internal"

    3. production:
       - status == "verified" or status == "active" or status == "stable"
       - AND confidence >= 0.4
       - AND evidence_count > 0
       - AND NOT in (discrimination-test, validation-only)

    4. candidate:
       - status == "candidate"
       - AND NOT in (discrimination-test, validation-only)
       - AND confidence > 0.3
       - OR evidence_count > 0

    5. unknown:
       - Everything else

    EVOLUTION ELIGIBILITY:
        - production → eligible for evolution candidate generation
        - candidate → eligible (with review)
        - discrimination-test → IGNORED (never enters evolution)
        - validation-only → IGNORED (never enters evolution)
        - unknown → eligible but flagged for HUMAN_REVIEW

    Usage:
        resolver = ProvenanceResolver()

        # From dict (e.g. bootstrap pattern data)
        result = resolver.resolve_from_dict("PAT-PARAMETER-LIST", {
            "confidence": 0.35,
            "evidence_count": 0,
            "tags": ["discrimination-test"],
        })

        # From Pattern object
        result = resolver.resolve_from_pattern(pattern)

        # Check evolution eligibility
        if resolver.is_eligible_for_evolution(result):
            candidates.append(...)
        else:
            ignored.append(resolver.ignore_reason(result))
    """

    # ── Classification thresholds ──
    DISCRIMINATION_CONFIDENCE_MAX = 0.4
    PRODUCTION_CONFIDENCE_MIN = 0.4

    def resolve(self, pattern_id: str, **kwargs: Any) -> ProvenanceResult:
        """
        Resolve provenance from keyword arguments.

        Args:
            pattern_id: Pattern identifier (e.g. "PAT-PARAMETER-LIST")
            **kwargs: Pattern metadata fields
                - tags: list[str]
                - confidence: float
                - evidence_count: int
                - status: str

        Returns:
            ProvenanceResult with classification.
        """
        tags = kwargs.get("tags", []) or []
        if isinstance(tags, str):
            tags = [tags]
        confidence = float(kwargs.get("confidence", 0.0))
        evidence_count = int(kwargs.get("evidence_count", 0))
        status = str(kwargs.get("status", ""))

        return self._classify(
            pattern_id=pattern_id,
            tags=tags,
            confidence=confidence,
            evidence_count=evidence_count,
            status=status,
        )

    def resolve_from_dict(
        self, pattern_id: str, data: dict[str, Any]
    ) -> ProvenanceResult:
        """Resolve provenance from a dictionary of pattern metadata."""
        return self.resolve(
            pattern_id=pattern_id,
            tags=data.get("tags", []),
            confidence=data.get("confidence", 0.0),
            evidence_count=data.get("evidence_count", 0),
            status=data.get("status", ""),
        )

    def resolve_from_pattern(self, pattern: Any) -> ProvenanceResult:
        """
        Resolve provenance from a Pattern object.

        Args:
            pattern: Pattern dataclass (from dice.graph.nodes)
                Must have: id, tags, confidence, evidence_count, status
        """
        tags = getattr(pattern, "tags", []) or []
        confidence = float(getattr(pattern, "confidence", 0.0))
        evidence_count = int(getattr(pattern, "evidence_count", 0))
        status = str(getattr(pattern, "status", ""))
        # Handle enum status
        if hasattr(status, "value"):
            status = status.value

        return self._classify(
            pattern_id=getattr(pattern, "id", ""),
            tags=tags,
            confidence=confidence,
            evidence_count=evidence_count,
            status=status,
        )

    def _classify(
        self,
        pattern_id: str,
        tags: list[str],
        confidence: float,
        evidence_count: int,
        status: str,
    ) -> ProvenanceResult:
        """
        Core classification logic.
        Rules apply in priority order — first match wins.
        """
        tags_lower = [t.lower() for t in tags]

        # ── Rule 1: Discrimination-test ──
        if "discrimination-test" in tags_lower:
            return ProvenanceResult(
                pattern_id=pattern_id,
                provenance=PatternProvenance.DISCRIMINATION_TEST,
                classification_rule=(
                    "discrimination-test tag detected — Phase 5.2 test "
                    "instrumentation, intentionally designed to overlap "
                    "with production patterns. NOT a real capability gap."
                ),
                metadata={
                    "tags": tags,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                },
                tags=tags,
                confidence=confidence,
                evidence_count=evidence_count,
                status=status,
            )

        # ── Secondary discrimination check: low confidence + zero evidence ──
        if (
            confidence < self.DISCRIMINATION_CONFIDENCE_MAX
            and evidence_count == 0
        ):
            return ProvenanceResult(
                pattern_id=pattern_id,
                provenance=PatternProvenance.DISCRIMINATION_TEST,
                classification_rule=(
                    f"Low confidence ({confidence}) + zero evidence_count "
                    f"— classified as discrimination-test. Patterns with "
                    f"confidence < {self.DISCRIMINATION_CONFIDENCE_MAX} "
                    f"and no supporting evidence are likely test instrumentation."
                ),
                metadata={
                    "tags": tags,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                },
                tags=tags,
                confidence=confidence,
                evidence_count=evidence_count,
                status=status,
            )

        # ── Rule 2: Validation-only ──
        if "validation-only" in tags_lower or "validation-internal" in tags_lower:
            return ProvenanceResult(
                pattern_id=pattern_id,
                provenance=PatternProvenance.VALIDATION_ONLY,
                classification_rule=(
                    "validation-only tag detected — internal validation "
                    "pattern, not a business capability gap."
                ),
                metadata={
                    "tags": tags,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                },
                tags=tags,
                confidence=confidence,
                evidence_count=evidence_count,
                status=status,
            )

        # ── Rule 3: Production ──
        is_production_status = status.lower() in (
            "verified", "active", "stable", "beta"
        )
        if (
            is_production_status
            and confidence >= self.PRODUCTION_CONFIDENCE_MIN
            and evidence_count > 0
        ):
            return ProvenanceResult(
                pattern_id=pattern_id,
                provenance=PatternProvenance.PRODUCTION,
                classification_rule=(
                    f"Production pattern: status={status}, "
                    f"confidence={confidence}, evidence_count={evidence_count}. "
                    f"Meets production criteria (status in verified/active/stable/beta, "
                    f"confidence >= {self.PRODUCTION_CONFIDENCE_MIN}, evidence > 0)."
                ),
                metadata={
                    "tags": tags,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                },
                tags=tags,
                confidence=confidence,
                evidence_count=evidence_count,
                status=status,
            )

        # ── Rule 4: Candidate ──
        is_candidate_status = status.lower() in ("candidate", "proposed")
        if (
            is_candidate_status
            and (confidence > 0.3 or evidence_count > 0)
        ):
            return ProvenanceResult(
                pattern_id=pattern_id,
                provenance=PatternProvenance.CANDIDATE,
                classification_rule=(
                    f"Candidate pattern: status={status}, "
                    f"confidence={confidence}, evidence_count={evidence_count}. "
                    f"Legitimate candidate — eligible for evolution with review."
                ),
                metadata={
                    "tags": tags,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                },
                tags=tags,
                confidence=confidence,
                evidence_count=evidence_count,
                status=status,
            )

        # ── Rule 5: Unknown ──
        return ProvenanceResult(
            pattern_id=pattern_id,
            provenance=PatternProvenance.UNKNOWN,
            classification_rule=(
                f"Cannot classify: status={status}, "
                f"confidence={confidence}, evidence_count={evidence_count}, "
                f"tags={tags}. Does not match any known provenance rule. "
                f"Flagged for human review."
            ),
            metadata={
                "tags": tags,
                "confidence": confidence,
                "evidence_count": evidence_count,
            },
            tags=tags,
            confidence=confidence,
            evidence_count=evidence_count,
            status=status,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Evolution Eligibility
    # ═══════════════════════════════════════════════════════════════════

    _ELIGIBLE_PROVENANCES = frozenset({
        PatternProvenance.PRODUCTION,
        PatternProvenance.CANDIDATE,
        PatternProvenance.UNKNOWN,  # eligible but flagged for human review
    })

    def is_eligible_for_evolution(self, result: ProvenanceResult) -> bool:
        """
        Check whether a pattern should participate in evolution.

        Returns False for discrimination-test and validation-only patterns.
        These patterns should still be recorded in the Evidence Store but
        should NOT generate EvolutionCandidates or participate in consolidation.
        """
        return result.provenance in self._ELIGIBLE_PROVENANCES

    def ignore_reason(self, result: ProvenanceResult) -> dict[str, Any]:
        """
        Generate an ignored-signal record for a pattern that was
        excluded from evolution.

        Returns a dict suitable for logging/audit:
            {
                "pattern_id": "PAT-PARAMETER-LIST",
                "ignored_reason": "expected validation signal",
                "provenance": "discrimination-test",
                "classification_rule": "...",
            }
        """
        reason_map = {
            PatternProvenance.DISCRIMINATION_TEST: "expected validation signal",
            PatternProvenance.VALIDATION_ONLY: "internal validation signal",
            PatternProvenance.UNKNOWN: "unknown provenance",
        }
        return {
            "pattern_id": result.pattern_id,
            "ignored_reason": reason_map.get(
                result.provenance, "not eligible for evolution"
            ),
            "provenance": result.provenance.value,
            "classification_rule": result.classification_rule,
        }

    # ═══════════════════════════════════════════════════════════════════
    # Batch resolve
    # ═══════════════════════════════════════════════════════════════════

    def resolve_from_pattern_map(
        self, pattern_map: dict[str, dict[str, Any]]
    ) -> dict[str, ProvenanceResult]:
        """
        Batch-resolve all patterns from a pattern_id → metadata dict.

        Args:
            pattern_map: {pattern_id: {confidence, evidence_count, tags, status}}

        Returns:
            {pattern_id: ProvenanceResult}
        """
        return {
            pid: self.resolve_from_dict(pid, data)
            for pid, data in pattern_map.items()
        }

    def get_eligible_patterns(
        self, patterns: list[Any]
    ) -> list[Any]:
        """
        Filter a list of Pattern objects to only those eligible for evolution.

        Args:
            patterns: List of Pattern objects

        Returns:
            Patterns where is_eligible_for_evolution is True.
        """
        eligible = []
        for p in patterns:
            result = self.resolve_from_pattern(p)
            if self.is_eligible_for_evolution(result):
                eligible.append(p)
        return eligible
