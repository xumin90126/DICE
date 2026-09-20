"""
CapabilityEvaluator — three-dimension validation for capabilities.

Evaluates a Capability across:
    1. Same-document accuracy (does it match legacy results?)
    2. Same-domain different structure (does it handle variants?)
    3. Cross-type transfer (does it truly work across document classes?)

Produces a CapabilityEvaluationReport with quality metrics beyond
simple confidence scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from dice.graph.experience_graph import ExperienceGraph
from dice.runtime.executor import CapabilityExecutor
from dice.runtime.result import CapabilityResult


@dataclass
class SingleEvaluation:
    """Result of evaluating a capability on a single document slice."""
    document_id: str = ""
    slice_id: str = ""
    capability_id: str = ""
    capability_result: Optional[CapabilityResult] = None
    legacy_result: Optional[dict[str, Any]] = None  # for A/B comparison

    # Metrics
    accuracy_match: bool = False               # does capability match legacy?
    evidence_count: int = 0
    evidence_diversity: int = 0                # distinct evidence types
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    is_success: bool = True
    errors: list[str] = field(default_factory=list)


@dataclass
class DimensionReport:
    """Report for one evaluation dimension."""
    dimension: str = ""                        # "same_doc", "same_domain_diff_struct", "cross_type"
    description: str = ""
    evaluations: list[SingleEvaluation] = field(default_factory=list)
    pass_count: int = 0
    fail_count: int = 0
    avg_confidence: float = 0.0
    avg_evidence_count: float = 0.0
    key_findings: list[str] = field(default_factory=list)


@dataclass
class CapabilityEvaluationReport:
    """
    Comprehensive evaluation of a Capability.

    Goes beyond simple confidence to assess:
    - Evidence quantity and diversity
    - Cross-document performance
    - False positive / false negative rates
    - Migration success (does capability truly replace doc_class rules?)
    """
    capability_id: str = ""
    capability_name: str = ""
    dimensions: list[DimensionReport] = field(default_factory=list)

    # Aggregate metrics
    total_documents_tested: int = 0
    total_successes: int = 0
    total_failures: int = 0
    overall_accuracy: float = 0.0             # % where capability ≥ legacy
    avg_confidence: float = 0.0
    avg_evidence_count: float = 0.0
    avg_evidence_diversity: float = 0.0

    # Cross-document metrics
    cross_doc_success_rate: float = 0.0       # success rate across distinct doc classes
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0

    # Migration assessment
    migration_assessment: str = ""            # human-readable verdict
    needs_new_patterns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "total_documents_tested": self.total_documents_tested,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "overall_accuracy": self.overall_accuracy,
            "avg_confidence": self.avg_confidence,
            "avg_evidence_count": self.avg_evidence_count,
            "cross_doc_success_rate": self.cross_doc_success_rate,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
            "migration_assessment": self.migration_assessment,
            "needs_new_patterns": self.needs_new_patterns,
            "recommendations": self.recommendations,
            "dimensions": [
                {
                    "dimension": d.dimension,
                    "pass_count": d.pass_count,
                    "fail_count": d.fail_count,
                    "avg_confidence": d.avg_confidence,
                    "key_findings": d.key_findings,
                }
                for d in self.dimensions
            ],
        }


class CapabilityEvaluator:
    """
    Evaluates a Capability across three dimensions.

    Dimension 1: Same Document
    - Verify capability results match legacy system results
    - Baseline accuracy test

    Dimension 2: Same Domain, Different Structure
    - Same semantic domain but different template/structure
    - Tests whether capability reduces rule adjustment

    Dimension 3: Cross-Type Transfer
    - Same semantic structure appears in different document class
    - Tests TRUE capability reusability (not doc_class-bounded)
    """

    def __init__(self, graph: ExperienceGraph, executor: CapabilityExecutor):
        self.graph = graph
        self.executor = executor

    def evaluate(
        self,
        capability_id: str,
        test_cases: list[dict[str, Any]],
    ) -> CapabilityEvaluationReport:
        """
        Run full 3-dimension evaluation.

        Each test_case dict:
            {
                "dimension": "same_doc" | "same_domain_diff_struct" | "cross_type",
                "document_id": str,
                "slice_id": str,
                "content": str,
                "legacy_result": dict | None,  # for comparison
            }
        """
        cap = self.graph.capabilities.get(capability_id)
        report = CapabilityEvaluationReport(
            capability_id=capability_id,
            capability_name=cap.name if cap else capability_id,
        )

        # Group test cases by dimension
        by_dimension: dict[str, list[dict[str, Any]]] = {}
        for tc in test_cases:
            dim = tc.get("dimension", "same_doc")
            by_dimension.setdefault(dim, []).append(tc)

        for dim_name, cases in by_dimension.items():
            dim_report = self._evaluate_dimension(capability_id, dim_name, cases)
            report.dimensions.append(dim_report)

        # Aggregate
        all_evals = [e for d in report.dimensions for e in d.evaluations]

        report.total_documents_tested = len(all_evals)
        report.total_successes = sum(1 for e in all_evals if e.is_success)
        report.total_failures = sum(1 for e in all_evals if not e.is_success)
        report.overall_accuracy = (
            report.total_successes / report.total_documents_tested
            if report.total_documents_tested > 0 else 0.0
        )
        report.avg_confidence = (
            sum(e.confidence for e in all_evals) / len(all_evals)
            if all_evals else 0.0
        )
        report.avg_evidence_count = (
            sum(e.evidence_count for e in all_evals) / len(all_evals)
            if all_evals else 0.0
        )
        report.avg_evidence_diversity = (
            sum(e.evidence_diversity for e in all_evals) / len(all_evals)
            if all_evals else 0.0
        )

        # Cross-doc success rate (success across distinct document IDs)
        distinct_docs = set(e.document_id for e in all_evals)
        cross_doc_successes = 0
        for doc_id in distinct_docs:
            doc_evals = [e for e in all_evals if e.document_id == doc_id]
            if all(e.is_success for e in doc_evals):
                cross_doc_successes += 1
        report.cross_doc_success_rate = (
            cross_doc_successes / len(distinct_docs) if distinct_docs else 0.0
        )

        # False positive/negative rates
        fp = sum(1 for e in all_evals if e.is_success and e.accuracy_match is False)
        fn = sum(1 for e in all_evals if not e.is_success and e.accuracy_match is True)
        report.false_positive_rate = fp / len(all_evals) if all_evals else 0.0
        report.false_negative_rate = fn / len(all_evals) if all_evals else 0.0

        # Migration assessment
        report.migration_assessment = self._assess_migration(report)
        report.recommendations = self._generate_recommendations(report)

        return report

    def _evaluate_dimension(
        self,
        capability_id: str,
        dim_name: str,
        cases: list[dict[str, Any]],
    ) -> DimensionReport:
        dim_report = DimensionReport(
            dimension=dim_name,
            description=self._dimension_description(dim_name),
        )

        for case in cases:
            eval_result = self._evaluate_single(capability_id, case)
            dim_report.evaluations.append(eval_result)

            if eval_result.is_success:
                dim_report.pass_count += 1
            else:
                dim_report.fail_count += 1

            # Key finding for failures
            if not eval_result.is_success:
                dim_report.key_findings.append(
                    f"{case['document_id']}/{case['slice_id']}: FAILED — "
                    f"{'; '.join(eval_result.errors[:2])}"
                )
            elif not eval_result.accuracy_match and eval_result.legacy_result:
                dim_report.key_findings.append(
                    f"{case['document_id']}/{case['slice_id']}: MISMATCH with legacy — "
                    f"capability_confidence={eval_result.confidence:.2f}"
                )

        if dim_report.evaluations:
            dim_report.avg_confidence = (
                sum(e.confidence for e in dim_report.evaluations)
                / len(dim_report.evaluations)
            )
            dim_report.avg_evidence_count = (
                sum(e.evidence_count for e in dim_report.evaluations)
                / len(dim_report.evaluations)
            )

        # If no failures found, add positive finding
        if dim_report.fail_count == 0:
            dim_report.key_findings.append(
                f"All {dim_report.pass_count} test cases passed for dimension '{dim_name}'"
            )

        return dim_report

    def _evaluate_single(
        self,
        capability_id: str,
        case: dict[str, Any],
    ) -> SingleEvaluation:
        result = self.executor.execute_chapter(
            capability_id=capability_id,
            content=case["content"],
            document_id=case.get("document_id", ""),
            slice_id=case.get("slice_id", ""),
        )

        legacy = case.get("legacy_result")
        accuracy_match = None
        if legacy is not None:
            accuracy_match = self._compare_results(result.result, legacy)

        evidence_types = set(e.evidence_type for e in result.evidence)

        return SingleEvaluation(
            document_id=case.get("document_id", ""),
            slice_id=case.get("slice_id", ""),
            capability_id=capability_id,
            capability_result=result,
            legacy_result=legacy,
            accuracy_match=accuracy_match if legacy is not None else None,
            evidence_count=result.evidence_count,
            evidence_diversity=len(evidence_types),
            confidence=result.confidence,
            execution_time_ms=result.execution_time_ms,
            is_success=result.is_success,
            errors=result.errors,
        )

    def _compare_results(
        self, cap_result: dict[str, Any], legacy_result: dict[str, Any]
    ) -> bool:
        """
        Compare capability result with legacy result.

        Simple comparison: check if component counts are within 20%.
        Future: more sophisticated comparison.
        """
        cap_count = cap_result.get("total_components", 0)
        legacy_count = legacy_result.get("total_components", legacy_result.get("count", 0))

        if legacy_count == 0:
            return cap_count == 0

        ratio = cap_count / legacy_count
        return 0.8 <= ratio <= 1.2

    def _dimension_description(self, dim_name: str) -> str:
        descriptions = {
            "same_doc": "Same document template — verify capability matches legacy",
            "same_domain_diff_struct": "Same domain, different template structure — test adaptability",
            "cross_type": "Different document class — test true reusability",
        }
        return descriptions.get(dim_name, dim_name)

    def _assess_migration(self, report: CapabilityEvaluationReport) -> str:
        """Assess whether capability successfully replaces doc_class rules."""
        if report.total_documents_tested == 0:
            return "No test cases executed. Unable to assess migration."

        if report.cross_doc_success_rate >= 0.75:
            return (
                f"✅ MIGRATION SUCCESSFUL: Capability works across "
                f"{report.cross_doc_success_rate:.0%} of document classes. "
                f"Does NOT depend on doc_class. "
                f"Evidence quality: avg {report.avg_evidence_count:.1f} items/doc."
            )
        elif report.cross_doc_success_rate >= 0.5:
            return (
                f"⚠️ PARTIAL MIGRATION: Capability works for some document classes "
                f"({report.cross_doc_success_rate:.0%}). May need additional patterns "
                f"for remaining cases. Evidence quality: avg {report.avg_evidence_count:.1f} items/doc."
            )
        else:
            return (
                f"❌ MIGRATION FAILED: Capability does not generalize across document classes "
                f"({report.cross_doc_success_rate:.0%}). If capability still depends on doc_class "
                f"for correct operation, the migration design needs revision."
            )

    def _generate_recommendations(self, report: CapabilityEvaluationReport) -> list[str]:
        recs = []
        if report.false_positive_rate > 0.1:
            recs.append("Reduce false positives by tightening detection thresholds")
        if report.false_negative_rate > 0.1:
            recs.append("Reduce false negatives by adding detection signals")
        if report.avg_evidence_count < 2:
            recs.append("Increase evidence collection granularity")
        if report.cross_doc_success_rate < 0.75:
            recs.append("Consider adding cross-document training examples")
        if not recs:
            recs.append("Capability performing well across all dimensions")
        return recs
