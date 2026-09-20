"""
Ranking Weight Adaptation — adaptive weight tuning from Feedback Loop signals.

Phase 4.3: The Ranking Model's weights can be tuned based on accumulated
Feedback evidence. This is NOT automatic code modification — it's a
derived recommendation that requires explicit opt-in.

Architecture:
    EvidenceView (from FeedbackLoop)
            │
            ▼
    RankingAdaptation.analyze(feedback_data)
            │
            ▼
    WeightRecommendation                         ← suggestion, NOT auto-apply
            │
            ▼
    RankingModel.update_weights(recommendation)  ← explicit user action

CRITICAL DESIGN:
    1. Weight adaptation is RECOMMENDATION, not automation
    2. No auto-modification of RankingModel weights
    3. Derived from EvidenceView — not from direct Registry access
    4. Produces WeightRecommendation with full traceability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.ranking import RankingWeights
from dice.runtime.experience.feedback_loop import HealthReport


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# WeightRecommendation
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class WeightRecommendation:
    """
    A recommendation for adjusting RankingModel weights based on feedback.

    This is a pure observation → suggestion. Does NOT auto-apply.
    The RankingModel.update_weights() method is called explicitly.

    Trace fields:
        source_health_report: which HealthReport triggered this
        evidence_observed: what evidence patterns led to this recommendation
    """

    capability_id: str = ""

    # ── Current vs recommended ──
    current_weights: RankingWeights = field(default_factory=RankingWeights)
    recommended_weights: RankingWeights = field(default_factory=RankingWeights)

    # ── Per-dimension deltas ──
    weight_deltas: dict[str, float] = field(default_factory=dict)
    # {"pattern_match": +0.05, "failure_penalty": +0.10, ...}

    # ── Rationale (why this recommendation) ──
    rationale: str = ""

    # ── Source trace ──
    source_health_report: Optional[HealthReport] = None
    evidence_observed: dict[str, Any] = field(default_factory=dict)
    # {"high_failure_rate": True, "degrading_trend": True, ...}

    # ── Metadata ──
    generated_at: str = field(default_factory=_now)
    applied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "weight_deltas": self.weight_deltas,
            "rationale": self.rationale,
            "evidence_observed": self.evidence_observed,
            "applied": self.applied,
            "generated_at": self.generated_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# RankingAdaptation
# ═══════════════════════════════════════════════════════════════════════════


class RankingAdaptation:
    """
    Analyzes Feedback Loop data to recommend Ranking weight adjustments.

    Principles:
    - OBSERVATION → RECOMMENDATION (not observation → action)
    - Higher failure rates → increase failure_penalty weight
    - Degrading trend → increase historical_success weight
    - Low evidence quality → increase evidence_quality weight
    - High cross-domain variance → increase cross_domain weight

    All deltas are bounded: max ±0.15 per dimension, not exceeding [0.05, 0.50].
    """

    # ── Tuning bounds ──
    MIN_WEIGHT = 0.05
    MAX_WEIGHT = 0.50
    MAX_DELTA = 0.15

    # ── Signal → weight dimension mapping ──
    # When we observe signal X, which weight dimension should be adjusted?
    SIGNAL_TO_DIMENSION: dict[str, str] = {
        "high_failure_rate": "failure_penalty",
        "performance_degrading": "historical_success",
        "confidence_drop": "evidence_quality",
        "recurring_failure_pattern": "pattern_match",
    }

    def analyze(
        self,
        health: HealthReport,
        current_weights: Optional[RankingWeights] = None,
    ) -> Optional[WeightRecommendation]:
        """
        Analyze health data and produce a WeightRecommendation.

        Returns None if no adjustment is warranted (healthy capability).
        """
        current_weights = current_weights or RankingWeights()
        deltas: dict[str, float] = {}
        evidence_observed: dict[str, bool] = {}

        # ── Signal → delta mapping ──
        for signal in health.signals:
            dim = self.SIGNAL_TO_DIMENSION.get(signal.signal_type)
            if dim is None:
                continue

            if signal.signal_type == "high_failure_rate":
                if signal.severity == "critical":
                    deltas[dim] = deltas.get(dim, 0.0) + 0.10  # stronger penalty
                    evidence_observed["high_failure_rate_critical"] = True
                else:
                    deltas[dim] = deltas.get(dim, 0.0) + 0.05
                    evidence_observed["high_failure_rate_warning"] = True

            elif signal.signal_type == "performance_degrading":
                deltas[dim] = deltas.get(dim, 0.0) + 0.08  # trust history more
                evidence_observed["performance_degrading"] = True

            elif signal.signal_type == "confidence_drop":
                deltas[dim] = deltas.get(dim, 0.0) + 0.07  # rely more on evidence quality
                evidence_observed["confidence_drop"] = True

            elif signal.signal_type == "recurring_failure_pattern":
                deltas[dim] = deltas.get(dim, 0.0) + 0.05  # stricter pattern match
                evidence_observed["recurring_failure_pattern"] = True

        if not deltas:
            return None

        # ── Build recommended weights ──
        recommended = RankingWeights(
            pattern_match=current_weights.pattern_match,
            evidence_quality=current_weights.evidence_quality,
            historical_success=current_weights.historical_success,
            cross_domain=current_weights.cross_domain,
            failure_penalty=current_weights.failure_penalty,
        )

        # Apply deltas with bounds
        clamped_deltas: dict[str, float] = {}
        for dim, delta in deltas.items():
            delta = max(-self.MAX_DELTA, min(self.MAX_DELTA, delta))
            current_val = getattr(current_weights, dim)
            new_val = current_val + delta
            new_val = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_val))
            setattr(recommended, dim, round(new_val, 4))
            clamped_deltas[dim] = round(delta, 4)

        # ── Build rationale ──
        rationale_parts = []
        for sig_type, dim in self.SIGNAL_TO_DIMENSION.items():
            if dim in clamped_deltas:
                delta = clamped_deltas[dim]
                direction = "increase" if delta > 0 else "decrease"
                rationale_parts.append(
                    f"{direction} {dim} by {abs(delta):.3f} "
                    f"(observed: {sig_type})"
                )

        return WeightRecommendation(
            capability_id=health.capability_id,
            current_weights=current_weights,
            recommended_weights=recommended,
            weight_deltas=clamped_deltas,
            rationale="; ".join(rationale_parts),
            source_health_report=health,
            evidence_observed=evidence_observed,
        )

    def should_update(
        self, recommendation: WeightRecommendation
    ) -> bool:
        """
        Should this recommendation be applied?
        
        Guard: only recommend update if the delta is significant.
        Minor adjustments (<0.03 per dimension) are noise.
        """
        if recommendation is None:
            return False
        max_delta = max(abs(d) for d in recommendation.weight_deltas.values())
        return max_delta >= 0.03


# ═══════════════════════════════════════════════════════════════════════════
# RankingModel integration method
# ═══════════════════════════════════════════════════════════════════════════


def apply_weight_recommendation(
    ranking_model: Any,         # RankingModel
    recommendation: WeightRecommendation,
) -> bool:
    """
    Apply a WeightRecommendation to a RankingModel.

    This is an EXPLICIT action — not called automatically from the Feedback Loop.
    Must be called by the orchestrator/user after reviewing the recommendation.

    Returns True if weights were updated.
    """
    if recommendation is None:
        return False

    adapter = RankingAdaptation()
    if not adapter.should_update(recommendation):
        return False

    ranking_model.weights = recommendation.recommended_weights
    recommendation.applied = True
    return True
