"""
Ranking Model — pure mathematical scoring for Capability candidates.

Phase 4.1: Replaces selector.py's per-pattern if/else branches with
a unified scoring function driven solely by observation signals and
capability metadata from the Registry.

CRITICAL DESIGN:
    1. ZERO pattern_id hardcoding (no `if pattern_id == "PAT-X"`)
    2. ZERO doc_class / product_id / filename checks
    3. All scores computed from OBSERVATION + REGISTRY fields
    4. Composite formula with configurable weight vector

Scoring formula:
    score = w1 * pattern_match
          + w2 * evidence_quality
          + w3 * historical_success
          + w4 * cross_domain_transfer
          - w5 * failure_rate

Weights are CONFIGURABLE, not hardcoded. Default weights favor
pattern matching and historical success equally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from dice.graph.nodes import Capability, DocumentObservation, MatchCandidate


# ═══════════════════════════════════════════════════════════════════════════
# Ranking Configuration
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class RankingWeights:
    """
    Configurable weight vector for the ranking formula.

    All weights are 0.0–1.0. They do NOT need to sum to 1.0 —
    the normalization happens in the composite score.
    """
    pattern_match: float = 0.35
    evidence_quality: float = 0.25
    historical_success: float = 0.20
    cross_domain: float = 0.10
    failure_penalty: float = 0.10    # deducted from total

    def validate(self) -> bool:
        """All weights must be non-negative."""
        return all(w >= 0 for w in [
            self.pattern_match, self.evidence_quality,
            self.historical_success, self.cross_domain, self.failure_penalty,
        ])


# Default weights — balanced between structural and empirical signals
DEFAULT_WEIGHTS = RankingWeights()


# ═══════════════════════════════════════════════════════════════════════════
# Ranking Model
# ═══════════════════════════════════════════════════════════════════════════


class RankingModel:
    """
    Scores a Capability against a DocumentObservation to produce a
    ranked MatchCandidate.

    Pure mathematical scoring — no if/else based on pattern IDs,
    doc_class, product_id, or any hardcoded taxonomy.

    Usage:
        model = RankingModel(weights=DEFAULT_WEIGHTS)
        candidate = model.score(observation, capability)
        # or batch:
        candidates = model.rank(observation, [cap1, cap2, ...])
    """

    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    # ──────────────────────── Public API ────────────────────────

    def score(
        self,
        observation: DocumentObservation,
        capability: Capability,
    ) -> MatchCandidate:
        """
        Score a single capability against an observation.

        Returns a MatchCandidate with full score breakdown.
        """
        pattern_match = self._compute_pattern_match(observation, capability)
        evidence_quality = self._compute_evidence_quality(observation, capability)
        historical_success = self._compute_historical_success(capability)
        cross_domain = self._compute_cross_domain(capability)
        failure_penalty = self._compute_failure_penalty(capability)

        # Weighted composite
        w = self.weights
        composite = (
            w.pattern_match * pattern_match
            + w.evidence_quality * evidence_quality
            + w.historical_success * historical_success
            + w.cross_domain * cross_domain
            - w.failure_penalty * failure_penalty
        )

        # Normalize to [0, 1] — weights may not sum to 1.0
        weight_sum = (
            w.pattern_match + w.evidence_quality
            + w.historical_success + w.cross_domain
        )
        if weight_sum > 0:
            # Failure penalty already subtracted; normalize the positive part
            positive = (
                w.pattern_match * pattern_match
                + w.evidence_quality * evidence_quality
                + w.historical_success * historical_success
                + w.cross_domain * cross_domain
            )
            normalized = max(0.0, positive / weight_sum - failure_penalty)
        else:
            normalized = max(0.0, composite)

        # Collect matched evidence
        matched_patterns = [
            pid for pid in capability.pattern_ids
            if pid in observation.detected_pattern_ids
        ]
        matched_elements = [
            et for et in observation.detected_element_types
            if observation.detected_element_types[et] > 0
        ]

        return MatchCandidate(
            capability_id=capability.id,
            capability_name=capability.name,
            score=round(normalized, 4),
            pattern_match_score=round(pattern_match, 4),
            evidence_quality_score=round(evidence_quality, 4),
            historical_success_score=round(historical_success, 4),
            cross_domain_score=round(cross_domain, 4),
            failure_penalty=round(failure_penalty, 4),
            matched_patterns=matched_patterns,
            matched_element_types=matched_elements,
            evidence_summary=(
                f"Matched {len(matched_patterns)}/{len(capability.pattern_ids)} patterns, "
                f"historical success={historical_success:.2f}"
            ),
            capability_version=capability.version,
            capability_status=capability.status.value,
        )

    def rank(
        self,
        observation: DocumentObservation,
        capabilities: list[Capability],
    ) -> list[MatchCandidate]:
        """
        Score and rank all capabilities against an observation.

        Returns list sorted by composite score descending.
        Always includes ALL capabilities — even low-scoring ones —
        so the caller can make informed decisions about fallback.
        """
        candidates = [
            self.score(observation, cap) for cap in capabilities
        ]
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    # ──────────────────────── Scoring Dimensions ────────────────────────

    def _compute_pattern_match(
        self,
        observation: DocumentObservation,
        capability: Capability,
    ) -> float:
        """
        Pattern Match Score: how well does the observation's structural
        signals align with the capability's registered patterns?

        Computed from:
        1. Overlap between observation.detected_pattern_ids and
           capability.pattern_ids
        2. Observation's per-pattern confidence scores
        3. Structural element type alignment

        NO per-pattern hardcoding. Each pattern contributes equally
        based on its match confidence.
        """
        if not capability.pattern_ids:
            return 0.0

        matched_count = 0
        total_confidence = 0.0

        for pid in capability.pattern_ids:
            if pid in observation.detected_pattern_ids:
                matched_count += 1
                total_confidence += observation.pattern_match_scores.get(pid, 0.5)

        # Coverage: BINARY — 1.0 if ANY pattern matched, 0.0 if none.
        #
        # Phase 5.2 fix: pattern COUNT must not determine ranking.
        # Shared patterns (same pattern_id on multiple capabilities)
        # must not inflate a capability's score over another.
        #
        # Reasoning: having 2 patterns (1 shared + 1 exclusive) should
        # not outrank a capability with 1 pattern purely because the
        # count is higher. The QUALITY of the match (avg_confidence)
        # and the capability's track record (evidence/history/cross-domain)
        # are the proper discriminators.
        coverage = 1.0 if matched_count > 0 else 0.0

        # Average confidence of matched patterns
        avg_confidence = (
            total_confidence / matched_count if matched_count > 0 else 0.0
        )

        # Structural element alignment bonus
        element_bonus = self._element_type_alignment(observation, capability)

        # Composite: coverage × avg_confidence + element bonus
        return min(1.0, coverage * 0.6 + avg_confidence * 0.3 + element_bonus * 0.1)

    def _compute_evidence_quality(
        self,
        observation: DocumentObservation,
        capability: Capability,
    ) -> float:
        """
        Evidence Quality Score: how strongly does the observation's
        content evidence support this capability?

        Based on:
        1. Element type coverage (does observation contain the element
           types this capability expects?)
        2. Evidence requirements satisfaction
        3. Content length sufficiency

        Uses capability.evidence_requirements and
        capability.input_schema for expectations.
        """
        score = 0.5  # neutral baseline

        # Check evidence_requirements from capability
        reqs = capability.evidence_requirements
        if reqs:
            checks_passed = 0
            total_checks = 0

            # Min content length check
            total_checks += 1
            min_len = reqs.get("min_content_length", 0)
            if observation.content_length >= min_len:
                checks_passed += 1
                score += 0.1
            elif min_len > 0:
                score -= 0.1

            # Min pattern matches check
            total_checks += 1
            min_patterns = reqs.get("min_pattern_matches", 0)
            matched = sum(
                1 for pid in capability.pattern_ids
                if pid in observation.detected_pattern_ids
            )
            if matched >= min_patterns:
                checks_passed += 1
                score += 0.1
            elif min_patterns > 0:
                score -= 0.1

            # Element type requirements
            required_types = reqs.get("required_element_types", [])
            if required_types:
                total_checks += 1
                present = sum(
                    1 for et in required_types
                    if observation.detected_element_types.get(et, 0) > 0
                )
                if present >= len(required_types):
                    checks_passed += 1
                    score += 0.15
                elif present > 0:
                    score += 0.05

        # Content length bonus: more content → more evidence potential
        if observation.content_length > 200:
            score = min(1.0, score + 0.05)
        if observation.content_length > 1000:
            score = min(1.0, score + 0.05)

        # Element density bonus
        total_elements = sum(observation.detected_element_types.values())
        if total_elements > 5:
            score = min(1.0, score + 0.05)
        if total_elements > 20:
            score = min(1.0, score + 0.05)

        return max(0.0, min(1.0, score))

    def _compute_historical_success(self, capability: Capability) -> float:
        """
        Historical Success: how well has this capability performed in the past?

        Uses capability.execution_count and capability.cross_doc_success_rate
        from the Registry. These are updated by the Feedback Loop (Phase 4.3).

        Cold start: capabilities with no execution history get a neutral 0.5.
        """
        if capability.execution_count == 0:
            return 0.5  # neutral baseline for new capabilities

        # Success rate weighted by execution count (more executions = more trust)
        success_rate = capability.cross_doc_success_rate

        # Confidence in the success rate increases with sample size
        # Using a simple logarithmic trust factor
        import math
        trust_factor = min(1.0, math.log(capability.execution_count + 1) / math.log(11))
        # trust_factor reaches 1.0 at ~10 executions

        return success_rate * 0.8 + 0.2 * trust_factor

    def _compute_cross_domain(self, capability: Capability) -> float:
        """
        Cross-Domain Transfer: how well does this capability generalize?

        Based on:
        1. Number of distinct documents tested
        2. Maturity score (auto-computed from evidence diversity)
        3. Cross-doc success rate stability

        Capabilities tested on many documents across different contexts
        score higher than single-document specialists.
        """
        doc_count = len(capability.documents_tested)

        if doc_count == 0:
            return 0.3  # unproven baseline

        # Document diversity bonus
        if doc_count >= 10:
            diversity = 1.0
        elif doc_count >= 5:
            diversity = 0.7
        elif doc_count >= 2:
            diversity = 0.4
        else:
            diversity = 0.2

        # Maturity contribution
        maturity = capability.maturity_score  # 0.0–1.0, auto-computed

        return diversity * 0.5 + maturity * 0.5

    def _compute_failure_penalty(self, capability: Capability) -> float:
        """
        Failure Penalty: how much to penalize based on past failures.

        High failure rate → high penalty.
        Recent failures (last_execution_at) weigh more than old ones.

        Returns 0.0–1.0 where 1.0 = severe penalty.
        """
        if capability.execution_count == 0:
            return 0.0

        failure_rate = (
            capability.failure_count / capability.execution_count
            if capability.execution_count > 0 else 0.0
        )

        # If very few executions and all failed → severe penalty
        if capability.execution_count <= 3 and failure_rate >= 0.5:
            return min(1.0, failure_rate * 1.5)

        # Standard: failure rate weighted by confidence in the statistic
        import math
        confidence = min(1.0, math.log(capability.execution_count + 1) / math.log(11))
        return failure_rate * confidence

    # ──────────────────────── Helpers ────────────────────────

    def _element_type_alignment(
        self,
        observation: DocumentObservation,
        capability: Capability,
    ) -> float:
        """
        How well do the observation's detected element types align with
        the capability's expected input schema?

        Uses capability.input_schema to determine expected element types,
        and observation.detected_element_types for actual presence.
        """
        expected_fields = capability.input_schema.get("fields", [])
        if not expected_fields:
            return 0.0

        # Map input_schema fields to element types
        field_to_element = {
            "content": "name",
            "structure_features": None,  # structural, not element-based
            "components": "name",
            "quantities": "quantity",
            "units": "unit",
            "catalog_numbers": "catalog_number",
        }

        relevant_types = set()
        for field in expected_fields:
            elem_type = field_to_element.get(field)
            if elem_type:
                relevant_types.add(elem_type)

        if not relevant_types:
            return 0.0

        present = sum(
            1 for et in relevant_types
            if observation.detected_element_types.get(et, 0) > 0
        )

        return present / len(relevant_types)
