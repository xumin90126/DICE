"""
Phase 6.1 Evidence Store — Match-level evidence data models.

Independent from dice/evidence.py (which handles execution-level evidence).
This module records matching pipeline outputs: what was observed, what was
matched, and what was missing.

DESIGN:
    MatchRecord captures a single CapabilityMatcher.match() invocation result.
    EvolutionCandidate is the observer's OUTPUT — a detected pattern of gaps,
    NOT a registered Capability and NOT an auto-created entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# MatchRecord — a single matching event snapshot
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class MatchRecord:
    """
    A single evidence record capturing one Observation → Match invocation.

    This is the UNIT of the Phase 6.1 Evidence Store. Each record captures:
    - WHERE: document/slice source
    - WHAT: structural observation signals
    - HOW: which capabilities matched with what confidence
    - RESULT: validation outcome and failure reason (if any)

    Records are IMMUTABLE once created. The store accumulates them.
    The observer scans them for evolution signals.
    """

    id: str = ""

    # ── Source ──
    document_id: str = ""
    slice_id: str = ""
    content_snippet: str = ""          # first 300 chars, for human reference

    # ── Observation signals (from DocumentObservation) ──
    line_count: int = 0
    structure_flags: dict[str, bool] = field(default_factory=dict)
    # e.g. {"has_table_structure": True, "has_numbered_list": True, ...}
    element_types: dict[str, int] = field(default_factory=dict)
    # e.g. {"name": 5, "quantity": 3, "unit": 2}
    detected_patterns: list[str] = field(default_factory=list)
    pattern_scores: dict[str, float] = field(default_factory=dict)

    # ── Matching result ──
    matched_capabilities: list[dict[str, Any]] = field(default_factory=list)
    # [{"capability_id": "CAP-COMP-TABLE", "score": 0.83, "rank": 1}, ...]
    top_capability_id: str = ""
    top_capability_score: float = 0.0
    total_candidates_above_threshold: int = 0
    max_match_score: float = 0.0       # highest score among all candidates

    # ── Validation ──
    validation_result: str = ""         # "pass" | "fail" | "pending" | ""
    failure_reason: str = ""            # why it failed, if applicable

    # ── Gap signals (what was detected but UNMATCHED) ──
    unmatched_signals: list[str] = field(default_factory=list)
    # Patterns or element types that had NO capability match

    # ── Metadata ──
    timestamp: str = field(default_factory=_now)
    pipeline_version: str = ""          # e.g. "phase5.5"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "content_snippet": self.content_snippet[:300],
            "line_count": self.line_count,
            "structure_flags": dict(self.structure_flags),
            "element_types": dict(self.element_types),
            "detected_patterns": list(self.detected_patterns),
            "pattern_scores": dict(self.pattern_scores),
            "matched_capabilities": self.matched_capabilities[:10],
            "top_capability_id": self.top_capability_id,
            "top_capability_score": round(self.top_capability_score, 4),
            "total_candidates_above_threshold": self.total_candidates_above_threshold,
            "max_match_score": round(self.max_match_score, 4),
            "validation_result": self.validation_result,
            "failure_reason": self.failure_reason[:500],
            "unmatched_signals": self.unmatched_signals,
            "timestamp": self.timestamp,
            "pipeline_version": self.pipeline_version,
        }

    @property
    def is_low_confidence(self) -> bool:
        """True when the top match score is below 0.3."""
        return self.top_capability_score < 0.3

    @property
    def has_unmatched_signals(self) -> bool:
        """True when patterns were detected but had no matching capability."""
        return len(self.unmatched_signals) > 0

    @property
    def is_failure(self) -> bool:
        """True when validation result is 'fail'."""
        return self.validation_result == "fail"


# ═══════════════════════════════════════════════════════════════════════════
# EvolutionCandidate — detected potential gap (observer OUTPUT)
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionCandidate:
    """
    A detected pattern in the Evidence Store that suggests a capability gap.

    This is the OUTPUT of EvolutionObserver.analyze(). It DESCRIBES what was
    detected — it does NOT prescribe changes and does NOT modify Registry.

    Gap types:
        unmatched_signals      — patterns detected with zero capability match
        low_confidence         — consistently low match scores across records
        repeated_failure       — same validation failure across ≥3 records
        potential_capability_gap — recurring structural pattern with no handler

    CRITICAL: EvolutionCandidate.status is ALWAYS "draft".
    Never auto-promoted. Never auto-registered. Human/validation gate required.
    """

    id: str = ""
    gap_type: str = ""                  # one of the above
    description: str = ""

    # ── Evidence trace ──
    record_ids: list[str] = field(default_factory=list)
    # Which MatchRecord IDs support this candidate

    # ── Pattern signature ──
    # The recurring structural pattern that defines this gap.
    # Stored as structure_flags + element_types + detected_patterns cluster.
    pattern_signature: dict[str, Any] = field(default_factory=dict)

    # ── Statistics ──
    frequency: int = 0                  # how many records show this pattern
    first_seen_at: str = ""
    last_seen_at: str = ""
    avg_confidence: float = 0.0         # average top score across records
    common_elements: list[str] = field(default_factory=list)
    # e.g. ["name", "quantity", "unit"] — most frequent element types

    # ── Recommendations (DESCRIPTIVE, not prescriptive) ──
    suggested_direction: str = ""
    # e.g. "Consider a table-like extraction capability for this structure"

    # ── Status (always draft, never auto-applied) ──
    status: str = "draft"               # "draft" | "reviewed" | "rejected"
    confidence: float = 0.0             # how confident the observer is (0-1)

    # ── Metadata ──
    detected_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "gap_type": self.gap_type,
            "description": self.description,
            "record_ids": self.record_ids[:20],
            "pattern_signature": self.pattern_signature,
            "frequency": self.frequency,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "avg_confidence": round(self.avg_confidence, 4),
            "common_elements": self.common_elements[:10],
            "suggested_direction": self.suggested_direction,
            "status": self.status,
            "confidence": round(self.confidence, 4),
            "detected_at": self.detected_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EvolutionDecision — validator output for EvolutionCandidate
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionDecision:
    """
    Validator's decision on whether an EvolutionCandidate warrants human review.

    This is the OUTPUT of EvolutionValidator.validate(). It PRESCRIBES an action
    (reject / review / approve_for_human) but NEVER:

        - Modifies CapabilityRegistry
        - Creates or registers new Capabilities
        - Auto-applies any changes
        - Updates EvolutionCandidate status

    The decision is based on evidence quality metrics computed from the
    candidate + the underlying MatchEvidenceStore records.

    Decision levels:
        reject            — insufficient evidence; discard
        review            — enough evidence to warrant human inspection
        approve_for_human — strong signal; escalate for manual capability design
    """

    candidate_id: str = ""
    decision: str = ""                      # "reject" | "review" | "approve_for_human"
    confidence: float = 0.0                 # validator's confidence in this decision (0-1)
    evidence_summary: "EvidenceSummary | dict[str, Any]" = \
        field(default_factory=lambda: EvidenceSummary())
    reason: str = ""
    evaluated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        es = self.evidence_summary
        if isinstance(es, EvidenceSummary):
            es = es.to_dict()
        return {
            "candidate_id": self.candidate_id,
            "decision": self.decision,
            "confidence": round(self.confidence, 4),
            "evidence_summary": es,
            "reason": self.reason,
            "evaluated_at": self.evaluated_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EvidenceSummary — five evaluation metrics for validation
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvidenceSummary:
    """
    Five quantitative metrics used by EvolutionValidator to assess
    whether a candidate warrants human attention.

    Metrics:
        occurrence_frequency     — total records supporting this candidate
        document_spread          — number of distinct document_ids
        repeated_failure_count   — records with validation_result="fail"
        existing_capability_overlap — # capabilities that could theoretically
                                      handle this pattern (0 = true gap)
        estimated_impact         — frequency × document_spread heuristic
    """

    occurrence_frequency: int = 0
    document_spread: int = 0
    repeated_failure_count: int = 0
    existing_capability_overlap: int = 0
    estimated_impact: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "occurrence_frequency": self.occurrence_frequency,
            "document_spread": self.document_spread,
            "repeated_failure_count": self.repeated_failure_count,
            "existing_capability_overlap": self.existing_capability_overlap,
            "estimated_impact": round(self.estimated_impact, 1),
        }


# ═══════════════════════════════════════════════════════════════════════════
# EvolutionProposal — human-reviewable capability evolution proposal
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionProposal:
    """
    A human-reviewable proposal for capability evolution, generated from
    validator-approved EvolutionDecisions.

    This is the OUTPUT of ProposalGenerator.generate(). It DESCRIBES a
    recommended evolution action but NEVER:

        - Modifies CapabilityRegistry
        - Creates or registers new Capabilities
        - Auto-applies any changes
        - Updates EvolutionCandidate status

    Human review is required before any action is taken.

    Recommended action types:
        extend_existing_capability_pattern — high overlap; extend an existing pattern
        extend_vocabulary                    — moderate overlap; add domain vocabulary
        add_new_capability_candidate         — low overlap; true new capability gap
        improve_detector                     — repeated failures; improve detection logic

    human_review_status lifecycle:
        pending_review → approved | rejected → (if approved) → implemented

    review_level (Phase 6.10):
        Controls which review tier is required before action can be taken:
            AUTO_REVIEW       — LOW risk, safe extension; light-touch review
            HUMAN_REVIEW      — MEDIUM risk, vocabulary/detection changes
            ARCHITECTURE_REVIEW — HIGH risk, new capability or registry impact
        Default HUMAN_REVIEW for backward compatibility.
    """

    proposal_id: str = ""
    source_candidate_id: str = ""         # → EvolutionCandidate.id
    source_decision_id: str = ""          # → EvolutionDecision.candidate_id
    gap_type: str = ""
    evidence_summary: "EvidenceSummary | dict[str, Any]" = \
        field(default_factory=lambda: EvidenceSummary())
    recommended_action: str = ""          # one of the four actions
    confidence: float = 0.0               # generator's confidence in this recommendation
    rationale: str = ""                   # why this action was recommended
    human_review_status: str = "pending_review"
    review_level: str = "HUMAN_REVIEW"    # Phase 6.10: AUTO_REVIEW | HUMAN_REVIEW | ARCHITECTURE_REVIEW
    generated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        es = self.evidence_summary
        if isinstance(es, EvidenceSummary):
            es = es.to_dict()
        return {
            "proposal_id": self.proposal_id,
            "source_candidate_id": self.source_candidate_id,
            "source_decision_id": self.source_decision_id,
            "gap_type": self.gap_type,
            "evidence_summary": es,
            "recommended_action": self.recommended_action,
            "confidence": round(self.confidence, 4),
            "rationale": self.rationale,
            "human_review_status": self.human_review_status,
            "review_level": self.review_level,
            "generated_at": self.generated_at,
        }

    @property
    def requires_human_review(self) -> bool:
        """True while the proposal is pending human review."""
        return self.human_review_status == "pending_review"

    @property
    def is_actionable(self) -> bool:
        """True when the proposal has been approved and is ready to implement."""
        return self.human_review_status == "approved"
