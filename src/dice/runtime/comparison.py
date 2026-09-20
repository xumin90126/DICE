"""
Legacy vs Capability A/B comparison framework.

Runs both the old doc_class-based handler and the new Capability-based
executor on the same content, then compares:
    - Accuracy (do they agree?)
    - Evidence quality (which is more traceable?)
    - Cross-document performance (which works on more document types?)

Keeps the old handler path intact — this is a comparison tool, not a replacement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Callable

from dice.graph.experience_graph import ExperienceGraph
from dice.runtime.executor import CapabilityExecutor
from dice.runtime.result import CapabilityResult


@dataclass
class ComparisonRow:
    """Single A/B comparison row for one document slice."""
    document_id: str = ""
    slice_id: str = ""
    doc_class: str = ""                    # legacy's doc_class (for reference only)

    # Legacy execution
    legacy_success: bool = False
    legacy_result: dict[str, Any] = field(default_factory=dict)
    legacy_component_count: int = 0

    # Capability execution
    capability_success: bool = False
    capability_result: Optional[CapabilityResult] = None
    capability_component_count: int = 0
    capability_confidence: float = 0.0
    capability_evidence_count: int = 0

    # Comparison
    agreement: bool = False                # do results agree?
    coverage_ratio: float = 0.0            # cap_count / legacy_count
    verdict: str = ""                      # "match", "capability_better", "legacy_better", "both_failed"


@dataclass
class ComparisonReport:
    """Full A/B comparison report."""
    capability_id: str = ""
    capability_name: str = ""
    rows: list[ComparisonRow] = field(default_factory=list)

    # Summary
    total_tests: int = 0
    legacy_success_count: int = 0
    capability_success_count: int = 0
    agreement_count: int = 0
    capability_better_count: int = 0
    legacy_better_count: int = 0
    both_failed_count: int = 0

    # Cross-document
    distinct_doc_classes: int = 0
    capability_cross_doc_success: int = 0  # # of distinct doc_classes where capability succeeded

    # Quality comparison
    avg_legacy_components: float = 0.0
    avg_capability_components: float = 0.0
    avg_capability_confidence: float = 0.0
    avg_capability_evidence: float = 0.0

    # Verdict
    overall_verdict: str = ""
    key_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "total_tests": self.total_tests,
            "legacy_success_count": self.legacy_success_count,
            "capability_success_count": self.capability_success_count,
            "agreement_count": self.agreement_count,
            "capability_better_count": self.capability_better_count,
            "legacy_better_count": self.legacy_better_count,
            "both_failed_count": self.both_failed_count,
            "distinct_doc_classes": self.distinct_doc_classes,
            "capability_cross_doc_success": self.capability_cross_doc_success,
            "avg_capability_confidence": self.avg_capability_confidence,
            "avg_capability_evidence": self.avg_capability_evidence,
            "overall_verdict": self.overall_verdict,
            "rows": [
                {
                    "document_id": r.document_id,
                    "doc_class": r.doc_class,
                    "verdict": r.verdict,
                    "legacy_count": r.legacy_component_count,
                    "capability_count": r.capability_component_count,
                    "coverage_ratio": r.coverage_ratio,
                }
                for r in self.rows
            ],
        }


class LegacyComparison:
    """
    Runs A/B comparison between legacy handler and Capability executor.

    Usage:
        def legacy_handler(content, doc_class) -> dict:
            # Old way: doc_class-based handler
            return {"components": [...], "count": 9}

        comparison = LegacyComparison(graph, legacy_handler)
        report = comparison.run("CAP-COMP-TABLE", test_cases)
    """

    def __init__(
        self,
        graph: ExperienceGraph,
        legacy_handler: Optional[Callable] = None,
    ):
        self.graph = graph
        self.executor = CapabilityExecutor(graph)
        self.legacy_handler = legacy_handler  # legacy handler function

    def run(
        self,
        capability_id: str,
        test_cases: list[dict[str, Any]],
    ) -> ComparisonReport:
        """
        Run A/B comparison on all test cases.

        test_cases: list of {
            "document_id": str,
            "slice_id": str,
            "content": str,
            "doc_class": str,        # for legacy handler only
        }
        """
        cap = self.graph.capabilities.get(capability_id)
        report = ComparisonReport(
            capability_id=capability_id,
            capability_name=cap.name if cap else capability_id,
        )

        for case in test_cases:
            row = self._compare_single(capability_id, case)
            report.rows.append(row)

        self._summarize(report)
        return report

    def _compare_single(
        self,
        capability_id: str,
        case: dict[str, Any],
    ) -> ComparisonRow:
        content = case["content"]
        doc_id = case.get("document_id", "")
        slice_id = case.get("slice_id", "")
        doc_class = case.get("doc_class", "")

        row = ComparisonRow(
            document_id=doc_id,
            slice_id=slice_id,
            doc_class=doc_class,
        )

        # Run LEGACY handler
        if self.legacy_handler:
            try:
                legacy_result = self.legacy_handler(content, doc_class)
                row.legacy_success = True
                row.legacy_result = legacy_result
                row.legacy_component_count = legacy_result.get("total_components", legacy_result.get("count", 0))
            except Exception as e:
                row.legacy_success = False
                row.legacy_result = {"error": str(e)}

        # Run CAPABILITY executor (NO doc_class!)
        cap_result = self.executor.execute_chapter(
            capability_id=capability_id,
            content=content,
            document_id=doc_id,
            slice_id=slice_id,
        )
        row.capability_result = cap_result
        row.capability_success = cap_result.is_success
        row.capability_component_count = cap_result.result.get("total_components", 0)
        row.capability_confidence = cap_result.confidence
        row.capability_evidence_count = cap_result.evidence_count

        # Determine verdict
        if not row.legacy_success and not row.capability_success:
            row.verdict = "both_failed"
        elif not row.capability_success:
            row.verdict = "legacy_better"
        elif not row.legacy_success:
            row.verdict = "capability_better"
        else:
            # Both succeeded — compare
            if row.legacy_component_count == 0:
                row.coverage_ratio = 1.0 if row.capability_component_count == 0 else 0.0
            else:
                row.coverage_ratio = row.capability_component_count / row.legacy_component_count

            if 0.8 <= row.coverage_ratio <= 1.25:
                row.agreement = True
                row.verdict = "match"
            elif row.coverage_ratio > 1.25:
                row.agreement = False
                row.verdict = "capability_better"  # found MORE components
            else:
                row.agreement = False
                row.verdict = "legacy_better"      # found fewer

        return row

    def _summarize(self, report: ComparisonReport) -> None:
        report.total_tests = len(report.rows)
        report.legacy_success_count = sum(1 for r in report.rows if r.legacy_success)
        report.capability_success_count = sum(1 for r in report.rows if r.capability_success)
        report.agreement_count = sum(1 for r in report.rows if r.agreement)
        report.capability_better_count = sum(1 for r in report.rows if r.verdict == "capability_better")
        report.legacy_better_count = sum(1 for r in report.rows if r.verdict == "legacy_better")
        report.both_failed_count = sum(1 for r in report.rows if r.verdict == "both_failed")

        # Cross-document
        distinct_classes = set(r.doc_class for r in report.rows if r.doc_class)
        report.distinct_doc_classes = len(distinct_classes)
        report.capability_cross_doc_success = sum(
            1 for dc in distinct_classes
            if any(r.doc_class == dc and r.capability_success for r in report.rows)
        )

        # Averages
        legacy_counts = [r.legacy_component_count for r in report.rows if r.legacy_success]
        cap_counts = [r.capability_component_count for r in report.rows if r.capability_success]
        report.avg_legacy_components = sum(legacy_counts) / len(legacy_counts) if legacy_counts else 0
        report.avg_capability_components = sum(cap_counts) / len(cap_counts) if cap_counts else 0

        confidences = [r.capability_confidence for r in report.rows if r.capability_success]
        report.avg_capability_confidence = sum(confidences) / len(confidences) if confidences else 0

        evidences = [r.capability_evidence_count for r in report.rows if r.capability_success]
        report.avg_capability_evidence = sum(evidences) / len(evidences) if evidences else 0

        # Key findings
        if report.capability_cross_doc_success == report.distinct_doc_classes:
            report.key_findings.append(
                f"✅ Capability succeeded across ALL {report.distinct_doc_classes} document classes — "
                f"true cross-document transfer achieved."
            )
        else:
            report.key_findings.append(
                f"Capability succeeded in {report.capability_cross_doc_success}/{report.distinct_doc_classes} "
                f"document classes."
            )

        if report.capability_better_count > report.legacy_better_count:
            report.key_findings.append(
                f"Capability outperformed legacy in {report.capability_better_count} cases "
                f"(vs {report.legacy_better_count} legacy-better)."
            )

        # Overall verdict
        if report.capability_cross_doc_success == report.distinct_doc_classes and report.capability_success_count == report.total_tests:
            report.overall_verdict = (
                "✅ CAPABILITY > DOCUMENT TYPE RULE — Capability successfully replaces "
                "doc_class-dependent rules with truly reusable pattern-based analysis."
            )
        elif report.capability_success_count >= report.legacy_success_count:
            report.overall_verdict = (
                "⚠️ Capability shows promise but needs refinement for some document classes."
            )
        else:
            report.overall_verdict = (
                "❌ Capability underperforms legacy — migration design needs revision."
            )
