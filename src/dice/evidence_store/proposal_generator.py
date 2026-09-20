"""
Phase 6.3 Evolution Proposal Generator.

Generates human-reviewable EvolutionProposal documents from validator-approved
EvolutionDecisions. This module NEVER:

    - Modifies CapabilityRegistry
    - Creates or registers new Capabilities
    - Auto-applies any changes
    - Updates EvolutionCandidate status

All output is a PRESCRIPTIVE proposal that requires human review before action.

Pipeline:
    EvolutionObserver.analyze()
        → list[EvolutionCandidate]
    CandidateConsolidator.consolidate()
        → merged candidates
    EvolutionValidator.validate_batch()
        → list[EvolutionDecision]
    ProposalGenerator.generate_batch()
        → list[EvolutionProposal]   ← THIS MODULE

Design:
    ProposalGenerator.generate(decision, candidate, store)
        → maps decision + evidence metrics → recommended_action
        → produces EvolutionProposal

    reject decisions → None (no proposal generated)
    review decisions → proposal with human_review_status="pending_review"
    approve_for_human → proposal with human_review_status="pending_review"

Recommended action classification:
    ┌─────────────────────┬──────────────────────────────────────────┐
    │ Decision Level      │ Action Logic                             │
    ├─────────────────────┼──────────────────────────────────────────┤
    │ approve_for_human   │ overlap ≤2 → add_new_capability_candidate│
    │                     │ overlap 3-4 → extend_vocabulary          │
    │                     │ overlap ≥5 → extend_existing_cap_pattern │
    │                     │ failures≥3  → improve_detector           │
    ├─────────────────────┼──────────────────────────────────────────┤
    │ review              │ overlap ≥5 → extend_existing_cap_pattern │
    │                     │ overlap 3-4 → extend_vocabulary          │
    │                     │ overlap ≤2 → add_new_capability_candidate│
    │                     │ failures≥3  → improve_detector           │
    └─────────────────────┴──────────────────────────────────────────┘

    When multiple conditions are true, priority is:
        improve_detector > add_new_capability_candidate >
        extend_vocabulary > extend_existing_capability_pattern
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence_store.models import (
    EvolutionCandidate,
    EvolutionDecision,
    EvolutionProposal,
    EvidenceSummary,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Action classification thresholds
# ═══════════════════════════════════════════════════════════════════════════

OVERLAP_TRUE_GAP = 2           # ≤2 = true gap, no existing capability covers this
OVERLAP_MODERATE = 5           # 3-4 = moderate overlap, vocabulary gap
                               # ≥5 = well-covered, extend existing
FAILURE_IMPROVE_DETECTOR = 3   # ≥3 repeated failures → improve_detector


class ProposalGenerator:
    """
    Generates EvolutionProposals from EvolutionDecisions.

    Each proposal is a human-reviewable document that describes a recommended
    capability evolution action based on the evidence gathered through the
    Observation → Match → Observe → Validate pipeline.

    Usage:
        generator = ProposalGenerator()
        proposals = generator.generate_batch(decisions, candidates, store)

        for p in proposals:
            print(f"[{p.recommended_action}] {p.rationale[:120]}")
            print(f"  Status: {p.human_review_status}")
            print(f"  Confidence: {p.confidence:.2f}")
    """

    def generate(
        self,
        decision: EvolutionDecision,
        candidate: Optional[EvolutionCandidate] = None,
        *,
        review_level: str = "",
    ) -> Optional[EvolutionProposal]:
        """
        Generate a proposal from a single EvolutionDecision.

        Args:
            decision: EvolutionDecision from EvolutionValidator
            candidate: Original EvolutionCandidate (optional, for metadata)
            review_level: Phase 6.10 — risk-based routing hint.
                "AUTO_REVIEW" | "HUMAN_REVIEW" | "ARCHITECTURE_REVIEW"
                Default "" → falls through to EvolutionProposal default (HUMAN_REVIEW).

        Returns:
            EvolutionProposal if decision warrants one, None for reject.
        """
        # ── Reject decisions produce no proposal ──
        if decision.decision == "reject":
            return None

        # ── Extract evidence ──
        summary = decision.evidence_summary
        if isinstance(summary, EvidenceSummary):
            pass  # already correct type
        elif isinstance(summary, dict):
            summary = EvidenceSummary(
                occurrence_frequency=summary.get("occurrence_frequency", 0),
                document_spread=summary.get("document_spread", 0),
                repeated_failure_count=summary.get("repeated_failure_count", 0),
                existing_capability_overlap=summary.get(
                    "existing_capability_overlap", 0
                ),
                estimated_impact=summary.get("estimated_impact", 0.0),
            )

        # ── Classify recommended action ──
        action, rationale = self._classify_action(decision, summary)

        # ── Compute proposal confidence ──
        confidence = self._compute_confidence(decision, summary, action)

        # ── Assemble proposal ──
        gap_type = candidate.gap_type if candidate else ""
        candidate_id = candidate.id if candidate else ""

        kwargs: dict[str, Any] = {
            "proposal_id": _uid("PROP-"),
            "source_candidate_id": candidate_id,
            "source_decision_id": decision.candidate_id,
            "gap_type": gap_type,
            "evidence_summary": summary,
            "recommended_action": action,
            "confidence": confidence,
            "rationale": rationale,
            "human_review_status": "pending_review",
        }
        # Phase 6.10: set review_level if provided, otherwise dataclass default
        if review_level:
            kwargs["review_level"] = review_level

        return EvolutionProposal(**kwargs)

    def generate_batch(
        self,
        decisions: list[EvolutionDecision],
        candidates: Optional[list[EvolutionCandidate]] = None,
        *,
        review_level: str = "",
    ) -> list[EvolutionProposal]:
        """
        Generate proposals for a batch of decisions.

        Builds a candidate lookup map for efficient candidate→proposal linking.

        Args:
            decisions: List of EvolutionDecisions from validator
            candidates: Original EvolutionCandidates for metadata linking
            review_level: Phase 6.10 — risk-based routing hint. Passed through
                to every generated proposal. Default "" → dataclass default.

        Returns:
            List of EvolutionProposals (one per non-reject decision).
        """
        # Build candidate lookup: candidate_id → candidate
        cand_map: dict[str, EvolutionCandidate] = {}
        if candidates:
            for c in candidates:
                cand_map[c.id] = c

        proposals: list[EvolutionProposal] = []
        for d in decisions:
            c = cand_map.get(d.candidate_id) if d.candidate_id else None
            prop = self.generate(d, c, review_level=review_level)
            if prop is not None:
                proposals.append(prop)

        return proposals

    # ═══════════════════════════════════════════════════════════════════
    # Action Classification
    # ═══════════════════════════════════════════════════════════════════

    def _classify_action(
        self,
        decision: EvolutionDecision,
        summary: EvidenceSummary,
    ) -> tuple[str, str]:
        """
        Map evidence metrics to the most appropriate recommended action.

        Priority order (higher priority actions take precedence when multiple
        conditions are met):
            1. improve_detector        — repeated failures indicate detection gap
            2. add_new_capability_candidate — clean gap, no existing coverage
            3. extend_vocabulary       — moderate overlap, vocabulary missing
            4. extend_existing_capability_pattern — well-covered, extend pattern

        Returns:
            (recommended_action, rationale)
        """
        overlap = summary.existing_capability_overlap
        failures = summary.repeated_failure_count
        freq = summary.occurrence_frequency
        spread = summary.document_spread
        impact = summary.estimated_impact

        # ── Priority 1: improve_detector ──
        # Repeated validation failures across documents suggest the detection
        # pipeline itself may need improvement, not a new capability gap.
        if failures >= FAILURE_IMPROVE_DETECTOR:
            return (
                "improve_detector",
                (
                    f"Repeated validation failures detected: {failures} failures "
                    f"across {spread} document(s). This pattern suggests the "
                    f"detection pipeline may not be recognizing content that "
                    f"existing capabilities could handle. Consider improving "
                    f"detector heuristics before designing a new capability. "
                    f"(freq={freq}, spread={spread}, impact={impact:.1f})"
                ),
            )

        # ── Priority 2: add_new_capability_candidate ──
        # Clean gap: few to no existing capabilities overlap with this pattern.
        # This is a genuinely new domain that deserves a capability candidate.
        if overlap <= OVERLAP_TRUE_GAP:
            conf_qualifier = "strongly" if decision.decision == "approve_for_human" else "moderately"
            return (
                "add_new_capability_candidate",
                (
                    f"Clean capability gap detected: only {overlap} existing "
                    f"capabilit{'y' if overlap == 1 else 'ies'} overlap with "
                    f"this recurring pattern ({freq} records, {spread} documents, "
                    f"impact={impact:.1f}). This is {conf_qualifier} indicative of "
                    f"a genuinely new domain that warrants a new capability "
                    f"candidate. Human review should define the capability's "
                    f"scope, extraction rules, and validation constraints."
                ),
            )

        # ── Priority 3: extend_vocabulary ──
        # Moderate overlap: existing capabilities partially match, but
        # domain-specific vocabulary is missing.
        if overlap < OVERLAP_MODERATE:
            return (
                "extend_vocabulary",
                (
                    f"Moderate capability overlap detected: {overlap} existing "
                    f"capabilities partially cover this pattern ({freq} records, "
                    f"{spread} documents, impact={impact:.1f}). The structural "
                    f"pattern may be recognized but domain-specific vocabulary "
                    f"is missing. Consider extending the vocabulary/parameter "
                    f"constraints of overlapping capabilities before creating "
                    f"a new capability."
                ),
            )

        # ── Priority 4: extend_existing_capability_pattern ──
        # Well-covered: many existing capabilities overlap with this pattern.
        # The pattern itself is recognized; extend an existing capability.
        return (
            "extend_existing_capability_pattern",
            (
                f"Existing capability coverage detected: {overlap} capabilities "
                f"overlap with this pattern ({freq} records, {spread} documents, "
                f"impact={impact:.1f}). The pattern is already well-covered by "
                f"existing capabilities — new gap may be a variation or edge case. "
                f"Consider extending an existing capability's pattern matching "
                f"or extraction rules to cover this variation, rather than "
                f"creating a new capability."
            ),
        )

    # ═══════════════════════════════════════════════════════════════════
    # Confidence Estimation
    # ═══════════════════════════════════════════════════════════════════

    def _compute_confidence(
        self,
        decision: EvolutionDecision,
        summary: EvidenceSummary,
        action: str,
    ) -> float:
        """
        Estimate the generator's confidence in this recommendation.

        Factors:
            - Validator confidence (base weight)
            - Evidence strength (frequency + spread)
            - Action-specific modifiers (new capability = higher bar, but
              when evidence is strong it's high confidence)

        Returns:
            Confidence score 0-1.
        """
        base = decision.confidence

        # ── Evidence strength modifier ──
        # Higher frequency + wider spread → higher confidence
        freq = summary.occurrence_frequency
        spread = summary.document_spread
        evidence_strength = min(1.0, (freq / 50.0) * 0.3 + (spread / 10.0) * 0.2)

        # ── Action-specific modifier ──
        action_mod = {
            "add_new_capability_candidate": 0.05,      # slight boost for clean gaps
            "extend_vocabulary": 0.0,                   # neutral
            "extend_existing_capability_pattern": -0.05, # slight discount (may not need action)
            "improve_detector": -0.02,                   # slight discount (uncertain root cause)
        }.get(action, 0.0)

        return round(min(0.95, base + evidence_strength + action_mod), 4)


# ═══════════════════════════════════════════════════════════════════════════
# Convenience: one-shot generate
# ═══════════════════════════════════════════════════════════════════════════


def generate_proposals(
    decisions: list[EvolutionDecision],
    candidates: Optional[list[EvolutionCandidate]] = None,
) -> dict[str, Any]:
    """
    One-shot: generate proposals from a batch of decisions.

    Returns:
        {
            "total_decisions": N,
            "rejected": R,             # decisions that produced no proposal
            "proposals_generated": P,
            "by_action": {
                "add_new_capability_candidate": A,
                "extend_vocabulary": V,
                "extend_existing_capability_pattern": E,
                "improve_detector": D,
            },
            "proposals": [EvolutionProposal.to_dict(), ...],
        }
    """
    generator = ProposalGenerator()
    proposals = generator.generate_batch(decisions, candidates)

    by_action: dict[str, int] = {
        "add_new_capability_candidate": 0,
        "extend_vocabulary": 0,
        "extend_existing_capability_pattern": 0,
        "improve_detector": 0,
    }
    for p in proposals:
        if p.recommended_action in by_action:
            by_action[p.recommended_action] += 1

    rejected = len(decisions) - len(proposals)

    return {
        "total_decisions": len(decisions),
        "rejected": rejected,
        "proposals_generated": len(proposals),
        "by_action": by_action,
        "proposals": [p.to_dict() for p in proposals],
    }
