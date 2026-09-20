"""
Phase 6.1-L2.2: ValidationReportBuilder — Logic (Phase D implemented).

Assembles a self-contained ValidationReport from a ValidationResult.
Pure observation output — never writes back to L2.1, never touches
Production.

Phase D implements ``build_report()`` + supporting read-only helpers
(4 logical steps):
    1. Summary assembly       (overall_status / candidate counts /
                               rule_pass_rate / critical_violations)
    2. rule_results mapping   (== result.check_results, read-only)
    3. evidence_references    (read-only ID presentation, C-D4)
    4. recommendations        (human-provided passthrough, never generated)

This module enforces:
    C-DI1  Report Is Presentation Only   — formatting / mapping / aggregation /
                                           reference presentation only
    C-DI2  Semantic Preservation         — Evidence → Assessment → Finding →
                                           Summary; never Assessment → Approval
    C-DI3  No New Intelligence           — no evaluator / rule / scoring /
                                           confidence / severity calculation
    C-DI4  Reference Integrity           — read-only ID references, never writes
                                           SimulationResult / Trace / Storage
    C-DI5  Observation Contract          — shadow_marked / origin / is_hypothetical
    C-DI6  Runtime Separation            — never calls Production / Simulation /
                                           Capability Runtime

Data chain (C-DI2):
    ValidationResult → ValidationReport (read-only observation)

Forbidden:
    - ❌ evaluation / rule execution / decision making
    - ❌ generating recommendation / action from assessment (C-D2)
    - ❌ new evaluator / rule / scoring / confidence / severity logic
    - ❌ approval / rejection / activation / decision fields or semantics
    - ❌ Production / Registry / Runtime / Storage access
    - ❌ ValidationReport / ReportSummary / EvidenceReference model changes

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True
"""

from __future__ import annotations

from typing import List

from .models import (
    EvidenceReference,
    ReportSummary,
    ValidationReport,
    ValidationResult,
)


class ValidationReportBuilder:
    """Report assembler (Shadow-only, Phase D implemented)."""

    SHADOW_ORIGIN: str = "composition_shadow_storage"
    GENERATED_BY: str = "phase6_1_l22_validator"

    def __init__(self) -> None:
        self._initialized: bool = True

    # ── Public behavior method ──

    def build_report(
        self,
        result: ValidationResult,
        evidence_references: List[EvidenceReference],
        recommendations: List[str] = None,
    ) -> ValidationReport:
        """Assemble a self-contained ValidationReport from a result.

        Four logical steps (read-only, never raises):
            1. Summary assembly (overall_status + candidate counts +
               rule_pass_rate + critical_violations).
            2. rule_results mapping (== result.check_results).
            3. evidence_references assembly (read-only ID presentation).
            4. recommendations passthrough + forced shadow markers.

        Safe degradation:
            - ``result is None`` → empty ValidationReport (zero counts).
            - non-list ``evidence_references`` / ``recommendations`` →
              normalized to [] (never raises).

        Args:
            result: ValidationResult produced by ValidationExecutor.
            evidence_references: Evidence references for traceability.
            recommendations: Optional human-provided recommendations
                (passthrough only, never generated from assessment).

        Returns:
            ValidationReport (self-contained, shadow_marked=True).
        """
        if result is None:
            return self._empty_report()

        # Step 1: summary assembly.
        summary = self._build_summary(result)

        # Step 2: rule_results mapping (read-only reference passthrough).
        rule_results = list(getattr(result, "check_results", []) or [])

        # Step 3: evidence_references assembly (read-only ID presentation).
        evidence_refs = self._assemble_evidence_refs(evidence_references)

        # Step 4: recommendations passthrough + forced shadow markers.
        return ValidationReport(
            result_id=getattr(result, "result_id", "") or "",
            request_id=getattr(result, "request_id", "") or "",
            simulation_result_id=getattr(result, "simulation_result_id", "") or "",
            summary=summary,
            rule_results=rule_results,
            evidence_references=evidence_refs,
            recommendations=self._normalize_recommendations(recommendations),
            generated_by=self.GENERATED_BY,
            shadow_marked=True,
            origin=self.SHADOW_ORIGIN,
            is_hypothetical=True,
        )

    # ── Summary construction (S-1~S-6) ──

    def _build_summary(self, result: ValidationResult) -> ReportSummary:
        """Construct ReportSummary from a ValidationResult (S-1~S-6)."""
        verdicts = getattr(result, "candidate_verdicts", {}) or {}
        total_candidates = len(verdicts)
        passed_candidates = sum(
            1 for v in verdicts.values() if str(v).upper() == "PASS"
        )
        failed_candidates = sum(
            1 for v in verdicts.values() if str(v).upper() == "FAIL"
        )

        total_rules = getattr(result, "total_rules", 0) or 0
        passed_rules = getattr(result, "passed_rules", 0) or 0
        rule_pass_rate = (passed_rules / total_rules) if total_rules else 0.0

        critical_violations = self._count_critical_violations(
            getattr(result, "check_results", []) or []
        )

        return ReportSummary(
            overall_status=self._status_value(
                getattr(result, "overall_status", None)
            ),
            total_candidates=total_candidates,
            passed_candidates=passed_candidates,
            failed_candidates=failed_candidates,
            rule_pass_rate=rule_pass_rate,
            critical_violations=critical_violations,
        )

    # ── Evidence reference assembly (C-D4) ──

    def _assemble_evidence_refs(
        self,
        evidence_references,
    ) -> List[EvidenceReference]:
        """Assemble read-only evidence references (C-D4, pure passthrough).

        Passthrough of provided EvidenceReference instances only. None or
        non-list input degrades to an empty list (never derives new
        references, never writes back).
        """
        if not isinstance(evidence_references, (list, tuple)):
            return []
        return [
            r for r in evidence_references if isinstance(r, EvidenceReference)
        ]

    # ── Pure helpers ──

    @staticmethod
    def _normalize_recommendations(recommendations) -> List[str]:
        """Normalize recommendations to a list of strings (passthrough only)."""
        if not isinstance(recommendations, (list, tuple)):
            return []
        return [r for r in recommendations if isinstance(r, str)]

    @staticmethod
    def _status_value(status) -> str:
        """Normalize a ValidationStatus (enum) to its string value."""
        if status is None:
            return "PASS"
        if hasattr(status, "value"):
            return str(status.value)
        return str(status)

    @staticmethod
    def _count_critical_violations(check_results) -> int:
        """Count FAIL check_results whose declared severity is critical (S-6)."""
        count = 0
        for c in check_results:
            if getattr(c, "status", "") != "FAIL":
                continue
            details = getattr(c, "details", {}) or {}
            if isinstance(details, dict) and details.get("severity") == "critical":
                count += 1
        return count

    def _empty_report(self) -> ValidationReport:
        """Empty ValidationReport (zero counts, empty lists)."""
        return ValidationReport(
            summary=ReportSummary(),
            rule_results=[],
            evidence_references=[],
            recommendations=[],
            generated_by=self.GENERATED_BY,
            shadow_marked=True,
            origin=self.SHADOW_ORIGIN,
            is_hypothetical=True,
        )

    def __repr__(self) -> str:
        return (
            f"ValidationReportBuilder(initialized={self._initialized}, "
            f"status=IMPLEMENTED_PHASE_D)"
        )
