"""
Composition Engine — candidate composition generation and evaluation.

Phase 4.4: Discovers potential Capability compositions from execution data
and produces scored CompositionProposals. Does NOT auto-register new Capabilities.

Architecture:
    ExecutionExperiences + CapabilityGraph
            │
            ▼
    CompositionEngine.analyze_co_occurrence()
            │
            ▼
    CompositionCandidate[]              ← scored, with source trace
            │
            ▼
    CompositionProposal                 ← draft → proposed → validated → applied/rejected
            │
            ▼
    Validation Gate                     ← external, NOT auto
            │
            ▼
    CapabilityRegistry.register()       ← explicit, after validation

CRITICAL DESIGN:
    1. Composition Engine ONLY generates Candidate Compositions
    2. Candidates MUST reference existing Capabilities and Evidence
    3. Scored on compatibility / coverage / risk (three dimensions)
    4. Output: CompositionProposal (same lifecycle as EvolutionProposal)
    5. NEVER auto-register new Capabilities
    6. New Composed Capabilities MUST pass Validation Gate

BOUNDARIES (Capability Operating System):
    - Composition is candidate GENERATION, not capability CREATION
    - Proposals are OBSERVATIONS about co-occurrence, not prescriptions
    - Zero auto-registration — Registration requires explicit action after validation
    - Experience → Evidence → Proposal → Validation → Production (preserved)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.experience.feedback_loop import EvolutionProposal
from dice.runtime.experience.execution_models import ExecutionExperience


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Composition Types
# ═══════════════════════════════════════════════════════════════════════════


class CompositionType:
    """
    Types of capability composition.

    PIPELINE: Cap A's output feeds Cap B's input (sequential)
        Example: ComponentsTableHandler → QuantityNormalizer

    PARALLEL: Multiple caps applied to same content independently
        Example: ComponentsExtraction + WarningsExtraction (both on same page)

    CONDITIONAL: Cap B is applied only if Cap A succeeds/fails
        Example: ComponentsTableHandler → if_missing → FreeTextComponentExtractor

    COVERAGE: Caps cover different sections of the same document type
        Example: ComponentsTableHandler (section 06) + StorageHandler (section 11)
                 + PrincipleHandler (section 05)
    """

    PIPELINE = "pipeline"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    COVERAGE = "coverage"

    ALL = [PIPELINE, PARALLEL, CONDITIONAL, COVERAGE]

    @classmethod
    def description(cls, comp_type: str) -> str:
        return {
            cls.PIPELINE: "Sequential: output of one feeds input of another",
            cls.PARALLEL: "Independent: multiple caps applied to same content",
            cls.CONDITIONAL: "Fallback: second cap applied only when first fails",
            cls.COVERAGE: "Sectional: caps cover different sections of same doc",
        }.get(comp_type, "Unknown")


# ═══════════════════════════════════════════════════════════════════════════
# Composition Candidate
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CompositionCandidate:
    """
    A CANDIDATE composition of existing Capabilities.

    This is a SUGGESTION — not a registered Capability. It describes
    a potential composition pattern observed in execution data.

    MUST reference existing capabilities and evidence. Cannot exist
    without source trace.
    """

    id: str = ""

    # ── What is being composed ──
    composed_capability_ids: list[str] = field(default_factory=list)
    composition_type: str = ""          # one of CompositionType

    # ── Description ──
    name: str = ""                      # suggested name for the composed capability
    description: str = ""               # what this composition achieves

    # ── Trigger ──
    # When should this composition be considered?
    trigger_condition: dict[str, Any] = field(default_factory=dict)
    # e.g. for COVERAGE:
    #   {"document_has_sections": ["05_principle", "06_components", "11_storage"]}
    # for PIPELINE:
    #   {"first_capability_output": "components", "second_capability_input": "components_raw"}
    # for CONDITIONAL:
    #   {"primary_capability": "CAP-COMP-TABLE", "fallback_condition": "coverage_ratio < 0.5"}

    # ── Source trace (MANDATORY) ──
    source_capability_ids: list[str] = field(default_factory=list)   # which caps were analyzed
    source_experience_ids: list[str] = field(default_factory=list)   # which experiences show this pattern
    source_evidence_ids: list[str] = field(default_factory=list)     # which evidence supports this

    # ── Co-occurrence data ──
    document_overlap: list[str] = field(default_factory=list)        # docs where caps co-occur
    co_occurrence_count: int = 0                                      # how many docs
    co_occurrence_frequency: float = 0.0                              # relative frequency

    # ── Three-dimensional scoring ──
    compatibility_score: float = 0.0    # how well do caps work together? (schema compatibility)
    coverage_score: float = 0.0         # how much document surface does this cover?
    risk_score: float = 0.0             # what could go wrong? (higher = riskier)
    composite_score: float = 0.0        # weighted aggregate: compat*0.4 + coverage*0.4 - risk*0.2

    # ── Score breakdown ──
    score_breakdown: dict[str, Any] = field(default_factory=dict)

    # ── Metadata ──
    generated_at: str = field(default_factory=_now)
    generator_signature: str = "composition_engine_v1"

    def __post_init__(self):
        if not self.id:
            self.id = _uid("COMP-CAND-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "composition_type": self.composition_type,
            "composed_capability_ids": self.composed_capability_ids,
            "trigger_condition": self.trigger_condition,
            # Scores
            "compatibility_score": round(self.compatibility_score, 4),
            "coverage_score": round(self.coverage_score, 4),
            "risk_score": round(self.risk_score, 4),
            "composite_score": round(self.composite_score, 4),
            "score_breakdown": self.score_breakdown,
            # Source trace
            "source_capability_count": len(self.source_capability_ids),
            "source_experience_count": len(self.source_experience_ids),
            "source_evidence_count": len(self.source_evidence_ids),
            # Co-occurrence
            "document_overlap_count": len(self.document_overlap),
            "co_occurrence_count": self.co_occurrence_count,
            "co_occurrence_frequency": round(self.co_occurrence_frequency, 4),
            # Metadata
            "generated_at": self.generated_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Composition Proposal
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CompositionProposal:
    """
    A formal proposal for a new composed Capability.

    Wraps a CompositionCandidate with a lifecycle status. Follows
    the same lifecycle as EvolutionProposal:
        draft → proposed → validated → applied | rejected

    The system CANNOT auto-register a composed Capability. The proposal
    must pass through Validation Gate, and registration is an explicit
    external action.

    Source trace includes the candidate, trigger experiences, and evidence —
    full provenance chain preserved from observation to proposal.
    """

    id: str = ""

    # ── Core ──
    candidate: Optional[CompositionCandidate] = None
    proposal_type: str = "composition"   # always "composition" for now

    # ── Source trace (preserved from candidate) ──
    trigger_experience_ids: list[str] = field(default_factory=list)
    trigger_evidence_ids: list[str] = field(default_factory=list)
    source_capability_ids: list[str] = field(default_factory=list)

    # ── Rationale (why this composition is warranted) ──
    rationale: str = ""

    # ── Validation requirements ──
    validation_required: list[str] = field(default_factory=list)
    # e.g. ["schema_compatibility", "regression_guard", "cross_document_check",
    #       "output_quality_threshold"]
    validation_results: list[dict[str, Any]] = field(default_factory=list)

    # ── Status ──
    status: str = "draft"       # "draft" → "proposed" → "validated" → "applied" | "rejected"

    # ── Metadata ──
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    created_by: str = "composition_engine"
    notes: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = _uid("COMP-PROP-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "candidate": self.candidate.to_dict() if self.candidate else None,
            "proposal_type": self.proposal_type,
            "trigger_experience_count": len(self.trigger_experience_ids),
            "trigger_evidence_count": len(self.trigger_evidence_ids),
            "rationale": self.rationale[:500],
            "validation_required": self.validation_required,
            "validation_results": self.validation_results,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
        }

    # ── Lifecycle (same as EvolutionProposal) ──

    def submit(self) -> None:
        """Submit for validation (status: draft → proposed)."""
        if self.status == "draft":
            self.status = "proposed"
            self.updated_at = _now()
            self.notes.append(f"[{_now()}] Submitted for validation")

    def validate(self, results: list[dict[str, Any]]) -> None:
        """Record validation results (called by Validation Gate only)."""
        if self.status != "proposed":
            return
        self.validation_results = results
        all_passed = all(r.get("passed", False) for r in results)
        self.status = "validated" if all_passed else "rejected"
        self.updated_at = _now()
        self.notes.append(
            f"[{_now()}] Validation {'passed' if all_passed else 'failed'}: "
            f"{len([r for r in results if r.get('passed')])}/{len(results)} gates"
        )

    def mark_applied(self) -> None:
        """Mark as applied (external registration completed)."""
        self.status = "applied"
        self.updated_at = _now()
        self.notes.append(f"[{_now()}] Composition registered as new Capability")

    def mark_rejected(self, reason: str = "") -> None:
        """Reject the proposal."""
        self.status = "rejected"
        self.updated_at = _now()
        if reason:
            self.notes.append(f"[{_now()}] Rejected: {reason}")

    def can_be_promoted(self) -> bool:
        """Can this proposal move to 'proposed'?"""
        return self.status == "draft"

    def needs_validation(self) -> bool:
        """Does this proposal still need validation?"""
        return self.status in ("draft", "proposed")


# ═══════════════════════════════════════════════════════════════════════════
# Composition Scoring
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CompositionScore:
    """Detailed score breakdown for a composition candidate."""

    # ── Compatibility (0-1): how well do capabilities work together? ──
    compatibility: float = 0.0
    schema_overlap: float = 0.0            # do input/output schemas align?
    pattern_compatibility: float = 0.0     # do detection patterns conflict?
    strategy_compatibility: float = 0.0    # can execution strategies coexist?
    compatibility_detail: str = ""

    # ── Coverage (0-1): how much document surface does this cover? ──
    coverage: float = 0.0
    document_coverage_ratio: float = 0.0   # % of documents where caps co-occur
    section_coverage_count: int = 0        # # of distinct sections covered
    element_type_coverage: float = 0.0     # % of element types covered
    coverage_detail: str = ""

    # ── Risk (0-1): what could go wrong? (higher = riskier) ──
    risk: float = 0.0
    conflict_risk: float = 0.0             # probability of schema/pattern conflict
    overlap_risk: float = 0.0              # risk of overlapping extraction (duplicates)
    failure_cascade_risk: float = 0.0      # risk of pipeline failure propagation
    maturity_risk: float = 0.0             # risk from low-maturity components
    risk_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "compatibility": round(self.compatibility, 4),
            "schema_overlap": round(self.schema_overlap, 4),
            "pattern_compatibility": round(self.pattern_compatibility, 4),
            "strategy_compatibility": round(self.strategy_compatibility, 4),
            "compatibility_detail": self.compatibility_detail,
            "coverage": round(self.coverage, 4),
            "document_coverage_ratio": round(self.document_coverage_ratio, 4),
            "section_coverage_count": self.section_coverage_count,
            "coverage_detail": self.coverage_detail,
            "risk": round(self.risk, 4),
            "conflict_risk": round(self.conflict_risk, 4),
            "overlap_risk": round(self.overlap_risk, 4),
            "failure_cascade_risk": round(self.failure_cascade_risk, 4),
            "maturity_risk": round(self.maturity_risk, 4),
            "risk_detail": self.risk_detail,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Composition Engine
# ═══════════════════════════════════════════════════════════════════════════


class CompositionEngine:
    """
    Discovers and scores potential Capability compositions.

    The engine analyzes ExecutionExperience data to identify capabilities
    that frequently co-occur on the same documents or have complementary
    patterns. It generates CompositionCandidates with full source trace
    and dimensional scoring.

    DOES NOT:
    - Auto-register new Capabilities
    - Modify existing Capabilities
    - Create Implementation code
    - Auto-apply proposals

    DOES:
    - Analyze co-occurrence patterns
    - Generate scored candidates
    - Create CompositionProposals (status: draft)
    - Provide validation requirements
    """

    # ── Scoring weights ──
    COMPATIBILITY_WEIGHT = 0.4
    COVERAGE_WEIGHT = 0.4
    RISK_WEIGHT = 0.2

    # ── Minimum thresholds for candidate generation ──
    MIN_CO_OCCURRENCE = 2               # caps must co-occur on at least N docs
    MIN_COMPOSITE_SCORE = 0.3           # minimum composite score to generate proposal

    def __init__(self):
        self._candidates: list[CompositionCandidate] = []
        self._proposals: list[CompositionProposal] = []

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS: Co-occurrence Detection
    # ═══════════════════════════════════════════════════════════════════

    def analyze_co_occurrence(
        self,
        experiences: list[ExecutionExperience],
        capabilities: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Analyze which capabilities co-occur on the same documents.

        For each pair of capabilities, count how many documents they
        both appear on. This is the raw signal for composition.

        Returns list of co-occurrence records:
            [{
                "cap_ids": ["CAP-A", "CAP-B"],
                "co_occurrence_count": 5,
                "documents": ["DOC-001", "DOC-002", ...],
                "frequency": 0.25,
            }, ...]
        """
        # doc_id → set of capability_ids used on that doc
        doc_cap_map: dict[str, set[str]] = {}

        for exp in experiences:
            if not exp.document_id or not exp.capability_id:
                continue
            if exp.capability_id == "unknown":
                continue
            if exp.document_id not in doc_cap_map:
                doc_cap_map[exp.document_id] = set()
            doc_cap_map[exp.document_id].add(exp.capability_id)

        # Count co-occurrences for each pair
        co_occurrence: dict[tuple[str, ...], dict[str, Any]] = {}
        total_docs = len(doc_cap_map)

        for doc_id, cap_ids in doc_cap_map.items():
            if len(cap_ids) < 2:
                continue
            sorted_ids = sorted(cap_ids)
            # Generate all pairs
            for i in range(len(sorted_ids)):
                for j in range(i + 1, len(sorted_ids)):
                    pair = (sorted_ids[i], sorted_ids[j])
                    if pair not in co_occurrence:
                        co_occurrence[pair] = {
                            "cap_ids": list(pair),
                            "co_occurrence_count": 0,
                            "documents": [],
                        }
                    co_occurrence[pair]["co_occurrence_count"] += 1
                    co_occurrence[pair]["documents"].append(doc_id)

        # Compute frequency
        for record in co_occurrence.values():
            record["frequency"] = (
                record["co_occurrence_count"] / total_docs
                if total_docs > 0 else 0.0
            )

        # Filter by minimum co-occurrence
        result = [
            r for r in co_occurrence.values()
            if r["co_occurrence_count"] >= self.MIN_CO_OCCURRENCE
        ]
        result.sort(key=lambda r: r["co_occurrence_count"], reverse=True)
        return result

    # ═══════════════════════════════════════════════════════════════════
    # GENERATION: Candidate Creation
    # ═══════════════════════════════════════════════════════════════════

    def generate_candidates(
        self,
        co_occurrences: list[dict[str, Any]],
        capabilities: dict[str, Any],
        experiences: list[ExecutionExperience],
    ) -> list[CompositionCandidate]:
        """
        Generate CompositionCandidates from co-occurrence data.

        For each co-occurrence pair, determines the likely composition
        type and scores the candidate.

        Args:
            co_occurrences: from analyze_co_occurrence()
            capabilities: dict[capability_id → Capability]
            experiences: all execution experiences (for source trace)

        Returns:
            List of scored CompositionCandidates.
        """
        candidates: list[CompositionCandidate] = []

        for co in co_occurrences:
            cap_ids = co["cap_ids"]
            if len(cap_ids) < 2:
                continue

            # Look up capability objects
            caps = [capabilities.get(cid) for cid in cap_ids]
            caps = [c for c in caps if c is not None]
            if len(caps) < 2:
                continue

            # Collect relevant experiences for source trace
            relevant_exps = [
                e for e in experiences
                if e.capability_id in cap_ids
                and e.document_id in co["documents"]
            ]

            # Determine composition type
            comp_type = self._determine_composition_type(caps, relevant_exps)

            # Generate candidate
            candidate = self._build_candidate(
                cap_ids=cap_ids,
                caps=caps,
                comp_type=comp_type,
                co_data=co,
                experiences=relevant_exps,
            )

            # Score the candidate
            self._score_candidate(candidate, caps, experiences)

            # Only include if score meets threshold
            if candidate.composite_score >= self.MIN_COMPOSITE_SCORE:
                candidates.append(candidate)

        # Sort by composite score
        candidates.sort(key=lambda c: c.composite_score, reverse=True)
        self._candidates = list(candidates)  # store copy
        return list(candidates)  # return copy (caller-safe)

    def _determine_composition_type(
        self,
        caps: list[Any],
        experiences: list[ExecutionExperience],
    ) -> str:
        """
        Determine the most likely composition type for a set of capabilities.

        Priority order (higher priority checked first):
        1. Has failures → CONDITIONAL (fallback pattern)
        2. Same layer + same slice → PARALLEL
        3. Same layer + different slices → COVERAGE
        4. Different layers → PIPELINE
        5. Default → COVERAGE
        """
        layers = set()
        slices_used: set[str] = set()
        has_failures = False

        for cap in caps:
            layer = getattr(cap, 'layer', '')
            if layer:
                layers.add(layer)
        for exp in experiences:
            if exp.slice_id:
                slices_used.add(exp.slice_id)
            if not exp.success:
                has_failures = True

        # Priority 1: Failures → CONDITIONAL
        if has_failures:
            return CompositionType.CONDITIONAL

        # Priority 2: Same slice → PARALLEL
        if len(slices_used) <= 1 and len(caps) >= 2:
            return CompositionType.PARALLEL

        # Priority 3: Same layer → COVERAGE
        if len(layers) == 1:
            return CompositionType.COVERAGE

        # Priority 4: Different layers → PIPELINE
        if len(layers) > 1:
            return CompositionType.PIPELINE

        return CompositionType.COVERAGE

    def _build_candidate(
        self,
        cap_ids: list[str],
        caps: list[Any],
        comp_type: str,
        co_data: dict[str, Any],
        experiences: list[ExecutionExperience],
    ) -> CompositionCandidate:
        """Build a CompositionCandidate from co-occurrence data."""

        cap_names = [getattr(c, 'name', cid) for cid, c in zip(cap_ids, caps)]
        name = " + ".join(cap_names[:3])
        if len(cap_names) > 3:
            name += f" (+{len(cap_names) - 3} more)"

        description = (
            f"Composed capability combining {', '.join(cap_names[:3])} "
            f"({comp_type}). Observed co-occurring on "
            f"{co_data['co_occurrence_count']} document(s)."
        )

        # Collect source evidence from experiences
        evidence_ids: list[str] = []
        experience_ids: list[str] = []
        for exp in experiences:
            if exp.id:
                experience_ids.append(exp.id)
            # Extract evidence IDs from result summary
            if hasattr(exp, 'result_summary') and exp.result_summary:
                evd_list = exp.result_summary.get('evidence_ids', [])
                evidence_ids.extend(evd_list)

        # Build trigger condition based on composition type
        trigger_condition: dict[str, Any] = {"composition_type": comp_type}
        if comp_type == CompositionType.COVERAGE:
            trigger_condition["document_has_capabilities"] = cap_ids
        elif comp_type == CompositionType.PIPELINE:
            trigger_condition["first_capability"] = cap_ids[0]
            trigger_condition["subsequent_capabilities"] = cap_ids[1:]
        elif comp_type == CompositionType.PARALLEL:
            trigger_condition["co_occurring_capabilities"] = cap_ids
        elif comp_type == CompositionType.CONDITIONAL:
            trigger_condition["primary_capability"] = cap_ids[0]
            trigger_condition["fallback_capabilities"] = cap_ids[1:]

        return CompositionCandidate(
            composed_capability_ids=list(cap_ids),
            composition_type=comp_type,
            name=name,
            description=description,
            trigger_condition=trigger_condition,
            source_capability_ids=list(cap_ids),
            source_experience_ids=experience_ids,
            source_evidence_ids=list(set(evidence_ids)),
            document_overlap=list(co_data["documents"]),
            co_occurrence_count=co_data["co_occurrence_count"],
            co_occurrence_frequency=co_data.get("frequency", 0.0),
        )

    # ═══════════════════════════════════════════════════════════════════
    # SCORING: Three-dimensional evaluation
    # ═══════════════════════════════════════════════════════════════════

    def _score_candidate(
        self,
        candidate: CompositionCandidate,
        caps: list[Any],
        experiences: list[ExecutionExperience],
    ) -> None:
        """Score a candidate on compatibility, coverage, and risk."""
        score = CompositionScore()

        # ── Compatibility ──
        score = self._score_compatibility(score, caps)

        # ── Coverage ──
        score = self._score_coverage(score, candidate, caps, experiences)

        # ── Risk ──
        score = self._score_risk(score, caps, experiences)

        # ── Composite ──
        candidate.compatibility_score = score.compatibility
        candidate.coverage_score = score.coverage
        candidate.risk_score = score.risk
        candidate.composite_score = round(
            score.compatibility * self.COMPATIBILITY_WEIGHT
            + score.coverage * self.COVERAGE_WEIGHT
            - score.risk * self.RISK_WEIGHT,
            4,
        )
        candidate.composite_score = max(0.0, min(1.0, candidate.composite_score))
        candidate.score_breakdown = score.to_dict()

    def _score_compatibility(
        self, score: CompositionScore, caps: list[Any]
    ) -> CompositionScore:
        """Score how well capabilities work together."""
        if len(caps) < 2:
            score.compatibility = 0.5
            score.compatibility_detail = "Single capability — no compatibility to assess"
            return score

        # Schema overlap: do input/output schemas align?
        schemas_match = 0
        total_pairs = 0
        for i in range(len(caps)):
            for j in range(i + 1, len(caps)):
                total_pairs += 1
                cap_a = caps[i]
                cap_b = caps[j]

                # Check if cap_a's output contains fields cap_b's input expects
                a_output = set(getattr(cap_a, 'output_schema', {}).get('fields', []))
                b_input = set(getattr(cap_b, 'input_schema', {}).get('fields', []))
                if a_output and b_input:
                    overlap = len(a_output & b_input)
                    if overlap > 0:
                        schemas_match += 1
                elif not a_output or not b_input:
                    # If no schema defined, neutral (0.5)
                    schemas_match += 0.5

        score.schema_overlap = (
            schemas_match / total_pairs if total_pairs > 0 else 0.5
        )

        # Pattern compatibility: do patterns conflict?
        all_patterns: set[str] = set()
        pattern_conflicts = 0
        for cap in caps:
            patterns = set(getattr(cap, 'pattern_ids', []))
            conflicts = all_patterns & patterns
            if conflicts:
                pattern_conflicts += len(conflicts)
            all_patterns.update(patterns)
        score.pattern_compatibility = (
            1.0 - min(1.0, pattern_conflicts / max(1, len(all_patterns)))
        )

        # Strategy compatibility: same layer → compatible
        layers = [getattr(c, 'layer', '') for c in caps if getattr(c, 'layer', '')]
        if len(set(layers)) <= 1:
            score.strategy_compatibility = 0.9  # same layer = compatible
        else:
            score.strategy_compatibility = 0.6  # different layers = caution

        score.compatibility = round(
            score.schema_overlap * 0.4
            + score.pattern_compatibility * 0.3
            + score.strategy_compatibility * 0.3,
            4,
        )
        score.compatibility_detail = (
            f"Schema overlap={score.schema_overlap:.2f}, "
            f"pattern compat={score.pattern_compatibility:.2f}, "
            f"strategy compat={score.strategy_compatibility:.2f}"
        )
        return score

    def _score_coverage(
        self,
        score: CompositionScore,
        candidate: CompositionCandidate,
        caps: list[Any],
        experiences: list[ExecutionExperience],
    ) -> CompositionScore:
        """Score how much document surface this composition covers."""

        # Document coverage: % of docs where ALL caps in the composition appear
        doc_cap_map: dict[str, set[str]] = {}
        for exp in experiences:
            if exp.document_id and exp.capability_id:
                if exp.document_id not in doc_cap_map:
                    doc_cap_map[exp.document_id] = set()
                doc_cap_map[exp.document_id].add(exp.capability_id)

        if not doc_cap_map:
            score.coverage = 0.0
            score.coverage_detail = "No execution data"
            return score

        target_ids = set(candidate.composed_capability_ids)
        covered_docs = sum(
            1 for caps_in_doc in doc_cap_map.values()
            if target_ids.issubset(caps_in_doc)
        )
        score.document_coverage_ratio = (
            covered_docs / len(doc_cap_map) if doc_cap_map else 0.0
        )

        # Section coverage: how many distinct sections
        sections: set[str] = set()
        for exp in experiences:
            if exp.capability_id in target_ids and exp.slice_id:
                sections.add(exp.slice_id)
        score.section_coverage_count = len(sections)

        # Element type coverage: from capability output schemas
        all_output_elements: set[str] = set()
        for cap in caps:
            output_fields = getattr(cap, 'output_schema', {}).get('fields', [])
            all_output_elements.update(output_fields)
        score.element_type_coverage = min(1.0, len(all_output_elements) / 10.0)

        score.coverage = round(
            score.document_coverage_ratio * 0.5
            + min(1.0, score.section_coverage_count / 5.0) * 0.3
            + score.element_type_coverage * 0.2,
            4,
        )
        score.coverage_detail = (
            f"Doc ratio={score.document_coverage_ratio:.2f}, "
            f"sections={score.section_coverage_count}, "
            f"element types={len(all_output_elements)}"
        )
        return score

    def _score_risk(
        self,
        score: CompositionScore,
        caps: list[Any],
        experiences: list[ExecutionExperience],
    ) -> CompositionScore:
        """Score what could go wrong with this composition."""

        # Conflict risk: overlapping extraction targets
        all_output_fields: list[str] = []
        for cap in caps:
            fields = getattr(cap, 'output_schema', {}).get('fields', [])
            all_output_fields.extend(fields)
        unique_fields = set(all_output_fields)
        if len(all_output_fields) > 0:
            score.conflict_risk = (
                1.0 - len(unique_fields) / len(all_output_fields)
            )
        else:
            score.conflict_risk = 0.3  # unknown

        # Overlap risk: same document, same slice → duplicate extraction risk
        slice_map: dict[str, int] = {}
        for exp in experiences:
            if exp.slice_id:
                slice_map[exp.slice_id] = slice_map.get(exp.slice_id, 0) + 1
        if slice_map:
            max_overlap = max(slice_map.values())
            score.overlap_risk = min(1.0, max_overlap / 5.0)
        else:
            score.overlap_risk = 0.0

        # Failure cascade risk: if any cap has low success rate
        failure_rates = []
        for cap in caps:
            rate = getattr(cap, 'cross_doc_success_rate', 1.0)
            failure_rates.append(1.0 - rate)
        score.failure_cascade_risk = (
            sum(failure_rates) / len(failure_rates)
            if failure_rates else 0.0
        )

        # Maturity risk: low-maturity components are riskier
        maturity_scores = [
            getattr(c, 'maturity_score', 0.5) for c in caps
        ]
        score.maturity_risk = (
            1.0 - sum(maturity_scores) / len(maturity_scores)
            if maturity_scores else 0.5
        )

        score.risk = round(
            score.conflict_risk * 0.3
            + score.overlap_risk * 0.2
            + score.failure_cascade_risk * 0.3
            + score.maturity_risk * 0.2,
            4,
        )
        score.risk_detail = (
            f"Conflict={score.conflict_risk:.2f}, "
            f"overlap={score.overlap_risk:.2f}, "
            f"cascade={score.failure_cascade_risk:.2f}, "
            f"maturity={score.maturity_risk:.2f}"
        )
        return score

    # ═══════════════════════════════════════════════════════════════════
    # PROPOSAL: From Candidate to Proposal
    # ═══════════════════════════════════════════════════════════════════

    def create_proposal(
        self, candidate: CompositionCandidate
    ) -> CompositionProposal:
        """
        Create a CompositionProposal from a candidate.

        The proposal starts as "draft" — it CANNOT be auto-registered.
        Must go through: draft → proposed → validated → applied
        (or rejected at any stage after proposed).
        """
        # Determine validation requirements based on composition type
        validation_req = ["regression_guard", "cross_document_check"]

        if candidate.composition_type == CompositionType.PIPELINE:
            validation_req.extend([
                "pipeline_output_compatibility",
                "pipeline_error_propagation_check",
            ])
        elif candidate.composition_type == CompositionType.PARALLEL:
            validation_req.extend([
                "parallel_overlap_check",
                "parallel_conflict_detection",
            ])
        elif candidate.composition_type == CompositionType.CONDITIONAL:
            validation_req.extend([
                "fallback_trigger_validation",
                "conditional_coverage_gap_check",
            ])
        elif candidate.composition_type == CompositionType.COVERAGE:
            validation_req.extend([
                "section_boundary_validation",
                "coverage_completeness_check",
            ])

        if candidate.risk_score > 0.5:
            validation_req.append("elevated_risk_review")

        proposal = CompositionProposal(
            candidate=candidate,
            trigger_experience_ids=candidate.source_experience_ids,
            trigger_evidence_ids=candidate.source_evidence_ids,
            source_capability_ids=candidate.source_capability_ids,
            rationale=(
                f"Capabilities {', '.join(candidate.composed_capability_ids[:3])} "
                f"co-occur on {candidate.co_occurrence_count} document(s) "
                f"({candidate.co_occurrence_frequency:.1%} frequency). "
                f"Composition type: {candidate.composition_type}. "
                f"Scores: compat={candidate.compatibility_score:.2f}, "
                f"coverage={candidate.coverage_score:.2f}, "
                f"risk={candidate.risk_score:.2f}."
            ),
            validation_required=validation_req,
        )

        self._proposals.append(proposal)
        return proposal

    def create_proposals_for_candidates(
        self, candidates: list[CompositionCandidate] | None = None
    ) -> list[CompositionProposal]:
        """Create proposals for all candidates (or specified subset)."""
        targets = candidates or self._candidates
        proposals = []
        for c in targets:
            proposals.append(self.create_proposal(c))
        return proposals

    # ═══════════════════════════════════════════════════════════════════
    # FULL PIPELINE
    # ═══════════════════════════════════════════════════════════════════

    def run(
        self,
        experiences: list[ExecutionExperience],
        capabilities: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run the full composition pipeline: analyze → generate → score → propose.

        Returns a summary dict with all candidates and proposals.
        Does NOT register anything.
        """
        # Step 1: Analyze co-occurrence
        co_occurrences = self.analyze_co_occurrence(experiences, capabilities)

        # Step 2-3: Generate and score candidates
        candidates = self.generate_candidates(co_occurrences, capabilities, experiences)

        # Step 4: Create proposals
        proposals = self.create_proposals_for_candidates(candidates)

        return {
            "co_occurrence_pairs": len(co_occurrences),
            "candidates_generated": len(candidates),
            "proposals_created": len(proposals),
            "candidates": [c.to_dict() for c in candidates],
            "proposals": [p.to_dict() for p in proposals],
            "generated_at": _now(),
        }

    # ═══════════════════════════════════════════════════════════════════
    # QUERY
    # ═══════════════════════════════════════════════════════════════════

    def get_candidates(self) -> list[CompositionCandidate]:
        """Get all generated candidates."""
        return list(self._candidates)

    def get_proposals(self) -> list[CompositionProposal]:
        """Get all created proposals."""
        return list(self._proposals)

    def get_proposal(self, proposal_id: str) -> Optional[CompositionProposal]:
        """Get a specific proposal by ID."""
        for p in self._proposals:
            if p.id == proposal_id:
                return p
        return None

    def clear(self) -> None:
        """Reset all state."""
        self._candidates.clear()
        self._proposals.clear()
