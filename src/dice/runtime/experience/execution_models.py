"""
ExecutionExperience + ExecutionResult — feedback assets from execution.

Phase 4.2: Every Capability execution produces an ExecutionExperience that
feeds into the Feedback Loop, which updates Capability confidence/ranking
in the Registry.

CRITICAL DESIGN:
    - Experience is GENERATED, not manually created
    - Experience changes confidence/ranking, NOT capability code
    - Each experience is immutable once recorded
    - Experience is the INPUT to Feedback Loop, not the output
    - THIS IS FEEDBACK DATA, not a rule store
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.result import CapabilityResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# ExecutionExperience
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionExperience:
    """
    Immutable record of a single Capability execution.

    This is FEEDBACK DATA — not a rule, not a mapping, not executable code.
    The Feedback Loop (Phase 4.3) consumes this to update Capability metadata
    in the Registry. The experience itself never modifies capability behavior.

    Fields:
        id: unique experience ID
        capability_id: which capability was executed
        observation_id: which observation triggered execution
        observation_summary: compact summary of observation features
        input_evidence: what patterns/element types were detected
        execution_strategy_used: which Implementation strategy was used
        result_summary: key results (component count, coverage, etc.)
        success: whether execution succeeded
        failure_reason: why it failed (if success=False)
        validation: validation results
        confidence_before/after: capability confidence before/after
        execution_time_ms: how long it took
        document_id / slice_id: traceability only (NOT routing)
    """
    id: str = ""
    capability_id: str = ""
    capability_name: str = ""
    observation_id: str = ""

    observation_summary: dict[str, Any] = field(default_factory=dict)
    input_evidence: dict[str, Any] = field(default_factory=dict)
    execution_strategy_used: str = ""
    result_summary: dict[str, Any] = field(default_factory=dict)

    success: bool = True
    failure_reason: str = ""

    validation: dict[str, Any] = field(default_factory=dict)

    confidence_before: float = 0.0
    confidence_after: float = 0.0
    confidence_delta: float = 0.0

    execution_time_ms: float = 0.0
    document_id: str = ""
    slice_id: str = ""
    timestamp: str = field(default_factory=_now)

    @classmethod
    def from_execution(
        cls,
        capability_id: str,
        capability_name: str,
        observation_id: str,
        observation_summary: dict[str, Any],
        match_result: Any,  # MatchResult (avoid circular import)
        capability_result: Optional[CapabilityResult],
        execution_strategy_used: str,
        execution_time_ms: float,
        document_id: str = "",
        slice_id: str = "",
        confidence_before: float = 0.0,
    ) -> "ExecutionExperience":
        """Factory: create from a completed execution (success or failure)."""
        success = (
            capability_result.is_success
            if capability_result else False
        )

        best_candidate = match_result.top_candidate() if match_result else None
        input_evidence = {
            "matched_patterns": best_candidate.matched_patterns if best_candidate else [],
            "matched_element_types": best_candidate.matched_element_types if best_candidate else [],
            "match_score": round(best_candidate.score, 4) if best_candidate else 0.0,
        }

        result_summary = {}
        if capability_result:
            result_summary = {
                "confidence": round(capability_result.confidence, 4),
                "evidence_count": capability_result.evidence_count,
                "strategy_case": capability_result.strategy_case,
                "reasoning_layer": capability_result.reasoning_layer,
            }
            if "total_components" in capability_result.result:
                result_summary["components_extracted"] = (
                    capability_result.result["total_components"]
                )
            if "coverage_ratio" in capability_result.result:
                result_summary["coverage_ratio"] = round(
                    capability_result.result["coverage_ratio"], 3
                )
            if "missing_count" in capability_result.result:
                result_summary["missing_count"] = (
                    capability_result.result["missing_count"]
                )

        validation = {
            "gates_passed": 0,
            "total_gates": 3,
            "warnings": capability_result.warnings if capability_result else [],
            "errors": capability_result.errors if capability_result else [],
        }
        if capability_result:
            if input_evidence["matched_patterns"]:
                validation["gates_passed"] += 1
            if capability_result.evidence_count > 0:
                validation["gates_passed"] += 1
            if capability_result.result:
                validation["gates_passed"] += 1

        failure_reason = ""
        if not success:
            if capability_result and capability_result.errors:
                failure_reason = "; ".join(capability_result.errors)
            elif capability_result and capability_result.diagnosis:
                failure_reason = capability_result.diagnosis
            elif not input_evidence["matched_patterns"]:
                failure_reason = "No patterns matched content structure"
            else:
                failure_reason = "Unknown failure"

        confidence_after_val = (
            capability_result.confidence if capability_result else 0.0
        )

        import uuid
        exp_id = f"EXP-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

        return cls(
            id=exp_id,
            capability_id=capability_id,
            capability_name=capability_name,
            observation_id=observation_id,
            observation_summary=observation_summary,
            input_evidence=input_evidence,
            execution_strategy_used=execution_strategy_used,
            result_summary=result_summary,
            success=success,
            failure_reason=failure_reason,
            validation=validation,
            confidence_before=round(confidence_before, 4),
            confidence_after=round(confidence_after_val, 4),
            confidence_delta=round(confidence_after_val - confidence_before, 4),
            execution_time_ms=round(execution_time_ms, 2),
            document_id=document_id,
            slice_id=slice_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "observation_id": self.observation_id,
            "observation_summary": self.observation_summary,
            "input_evidence": self.input_evidence,
            "execution_strategy_used": self.execution_strategy_used,
            "result_summary": self.result_summary,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "validation": self.validation,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "confidence_delta": self.confidence_delta,
            "execution_time_ms": self.execution_time_ms,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "timestamp": self.timestamp,
        }

    def is_significant(self) -> bool:
        """
        Is this experience worth retaining for learning?

        Significant if:
        - It's a failure (we learn from failures)
        - Confidence changed significantly (>0.1)
        """
        if not self.success:
            return True
        if abs(self.confidence_delta) > 0.1:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# ExecutionResult
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionResult:
    """
    Complete output of a single execute(observation) call.

    Wraps MatchResult + CapabilityResult + ExecutionExperience into
    a unified output. Replaces the old bare-CapabilityResult pattern.

    NO doc_class, product_id, or filename fields — only traceability IDs.
    """
    observation_id: str = ""
    document_id: str = ""
    slice_id: str = ""

    match_result: Optional[Any] = None       # MatchResult
    capability_result: Optional[CapabilityResult] = None
    experience: Optional[ExecutionExperience] = None

    success: bool = False
    diagnostics: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=_now)
    execution_time_ms: float = 0.0

    @property
    def has_capability_match(self) -> bool:
        if self.match_result is None:
            return False
        return self.match_result.has_high_confidence_match

    @property
    def selected_capability_id(self) -> str:
        if self.match_result and self.match_result.top_candidate():
            return self.match_result.top_candidate().capability_id
        if self.capability_result:
            return self.capability_result.capability_id
        return ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "success": self.success,
            "selected_capability_id": self.selected_capability_id,
            "match_result": (
                self.match_result.to_dict() if self.match_result else None
            ),
            "capability_result": (
                self.capability_result.to_dict()
                if self.capability_result else None
            ),
            "experience": (
                self.experience.to_dict() if self.experience else None
            ),
            "diagnostics": self.diagnostics,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "timestamp": self.timestamp,
        }
