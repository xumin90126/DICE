"""
Evolution Engine — bridges Evidence accumulation to EvolutionProposal generation.

Phase 4.5: Completes the System Loop evaluation step:
    Observation → Matching → Execution → Experience → Evaluation → Proposal

This is the EVALUATION layer — reads Evidence from EvidenceView and produces
EvolutionReports containing GapCandidates, DegradationAlerts, CoverageGaps,
and EvolutionProposals. ALL output is descriptive observation, NOT prescription.

Architecture:
    EvidenceView (from Phase 4.3)
            │
            ▼
    EvolutionEngine.evaluate()
            │
            ├── analyze_gaps()        ← missing patterns, vocabulary, sections
            ├── detect_degradation()   ← declining capability health
            ├── analyze_coverage()     ← unserved document sections
            └── analyze_cross_capability() ← patterns spanning capabilities
            │
            ▼
    EvolutionReport                     ← descriptive, NOT prescriptive
            │
            ▼
    generate_proposals()               ← draft EvolutionProposals
            │
            ▼
    EvolutionProposal[]                 ← source traces, lifecycle managed

CRITICAL DESIGN:
    1. EvolutionEngine ONLY reads — never modifies Registry or Capability
    2. EvolutionReport is DESCRIPTIVE — "detected X", NOT "should add Y"
    3. All proposals start as draft — Validation Gate required for promotion
    4. Every proposal references source evidence/experience IDs
    5. NO Agent concepts, NO autonomous planning, NO automatic learning
    6. NO auto-registration of new Capabilities
    7. Evolution must always go: draft → proposed → validated → applied/rejected

BOUNDARIES (Capability Operating System):
    - Evolution Engine evaluates evidence, does not create capabilities
    - Proposals are OBSERVATIONS about capability gaps, not prescriptions
    - Zero auto-application — explicit validation gate required
    - Agent/Application are FUTURE consumers, not part of this system
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence import EvidenceView, EvidenceType, Evidence
from dice.runtime.experience.feedback_loop import (
    EvolutionProposal, EnhancementSignal, HealthReport,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Gap Candidate
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class GapCandidate:
    """
    A detected gap in the capability landscape.

    DESCRIPTIVE ONLY — says "pattern X has no matching capability",
    NOT "create capability for pattern X".

    Gap types:
        pattern_unmatched    — structural pattern detected but no capability handles it
        vocabulary_missing   — terms consistently appearing in failures, not in any vocabulary
        section_unserved     — document section type with zero capability matches
        cross_domain_failure — capability succeeds on domain A but fails on domain B
        strategy_mismatch    — capability exists but strategy doesn't fit observed content
    """

    gap_id: str = ""
    gap_type: str = ""              # one of the above
    description: str = ""           # observed phenomenon, NOT prescription

    # ── Source trace ──
    evidence_ids: list[str] = field(default_factory=list)
    experience_ids: list[str] = field(default_factory=list)

    # ── Context ──
    severity: str = "info"          # "info", "warning", "critical"
    observed_in_documents: list[str] = field(default_factory=list)
    observed_in_slices: list[str] = field(default_factory=list)
    observed_frequency: int = 0

    # ── Detail ──
    affected_capability_ids: list[str] = field(default_factory=list)
    pattern_signature: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

    # ── Metadata ──
    detected_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.gap_id:
            self.gap_id = _uid("GAP-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type,
            "description": self.description,
            "evidence_ids": self.evidence_ids[:10],
            "experience_ids": self.experience_ids[:10],
            "severity": self.severity,
            "observed_in_documents": self.observed_in_documents[:10],
            "observed_in_slices": self.observed_in_slices[:10],
            "observed_frequency": self.observed_frequency,
            "affected_capability_ids": self.affected_capability_ids,
            "pattern_signature": self.pattern_signature,
            "confidence": round(self.confidence, 4),
            "detected_at": self.detected_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Degradation Alert
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class DegradationAlert:
    """
    Detected degradation in an existing Capability's performance.

    DESCRIPTIVE ONLY — says "success rate dropped from 85% to 40%",
    NOT "fix the implementation".

    Degradation types:
        success_rate_drop    — success rate declined significantly
        confidence_decline   — average execution confidence trending down
        coverage_shrink      — capability covers fewer sections than before
        failure_rate_spike   — sudden increase in failure count
        pattern_match_decay  — pattern match rate declining
    """

    alert_id: str = ""
    capability_id: str = ""
    capability_name: str = ""
    degradation_type: str = ""      # one of the above
    description: str = ""           # observed phenomenon

    # ── Source trace ──
    evidence_ids: list[str] = field(default_factory=list)

    # ── Metrics ──
    severity: str = "info"
    metric_name: str = ""
    metric_before: float = 0.0
    metric_after: float = 0.0
    delta: float = 0.0

    # ── Context ──
    observation_window: str = ""    # e.g. "last 20 executions"
    total_executions_in_window: int = 0

    # ── Metadata ──
    detected_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = _uid("DEG-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "degradation_type": self.degradation_type,
            "description": self.description,
            "evidence_ids": self.evidence_ids[:10],
            "severity": self.severity,
            "metric_name": self.metric_name,
            "metric_before": round(self.metric_before, 4),
            "metric_after": round(self.metric_after, 4),
            "delta": round(self.delta, 4),
            "observation_window": self.observation_window,
            "total_executions_in_window": self.total_executions_in_window,
            "detected_at": self.detected_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Coverage Gap
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CoverageGap:
    """
    A content pattern or section type not covered by any registered Capability.

    DESCRIPTIVE ONLY — says "section type 'warnings_and_precautions' appears
    in 3 documents with no matching capability", NOT "register a warnings handler".

    Coverage gap types:
        section_unserved      — document section type has zero matching capabilities
        pattern_orphan        — structural pattern detected but no capability registered
        domain_uncovered      — entire document type has no capabilities
    """

    gap_id: str = ""
    gap_type: str = ""              # one of the above
    description: str = ""

    # ── What is uncovered ──
    uncovered_pattern: str = ""     # e.g. section name, pattern signature
    uncovered_signature: dict[str, Any] = field(default_factory=dict)

    # ── Source trace ──
    evidence_ids: list[str] = field(default_factory=list)
    experience_ids: list[str] = field(default_factory=list)

    # ── Context ──
    observed_in_documents: list[str] = field(default_factory=list)
    observed_count: int = 0
    severity: str = "info"

    # ── Nearby capabilities (what DOES exist nearby) ──
    nearby_capability_ids: list[str] = field(default_factory=list)

    # ── Metadata ──
    detected_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.gap_id:
            self.gap_id = _uid("COV-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type,
            "description": self.description,
            "uncovered_pattern": self.uncovered_pattern,
            "uncovered_signature": self.uncovered_signature,
            "evidence_ids": self.evidence_ids[:10],
            "experience_ids": self.experience_ids[:10],
            "observed_in_documents": self.observed_in_documents[:10],
            "observed_count": self.observed_count,
            "severity": self.severity,
            "nearby_capability_ids": self.nearby_capability_ids,
            "detected_at": self.detected_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Cross-Capability Insight
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CrossCapabilityInsight:
    """
    An insight that spans multiple capabilities.

    DESCRIPTIVE ONLY — says "capabilities A and B both fail on domain X
    with similar vocabulary gaps", NOT "merge A and B".

    Insight types:
        shared_vocabulary_gap   — same missing terms across multiple capabilities
        shared_failure_domain   — multiple caps fail on same document type
        complementary_coverage  — caps A and B cover disjoint sections of same doc
        conflicting_overlap     — caps A and B claim to handle same pattern differently
    """

    insight_id: str = ""
    insight_type: str = ""
    description: str = ""

    # ── Source trace ──
    evidence_ids: list[str] = field(default_factory=list)
    experience_ids: list[str] = field(default_factory=list)

    # ── Affected capabilities ──
    capability_ids: list[str] = field(default_factory=list)

    # ── Detail ──
    shared_evidence: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"

    # ── Metadata ──
    detected_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.insight_id:
            self.insight_id = _uid("CCI-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "insight_type": self.insight_type,
            "description": self.description,
            "evidence_ids": self.evidence_ids[:10],
            "experience_ids": self.experience_ids[:10],
            "capability_ids": self.capability_ids,
            "shared_evidence": self.shared_evidence,
            "severity": self.severity,
            "detected_at": self.detected_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Evolution Report
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionReport:
    """
    Complete evaluation report from the Evolution Engine.

    This is the OUTPUT of the evaluation step. It contains ALL detected
    observations — gaps, degradations, coverage issues, cross-capability
    insights — and derived EvolutionProposals.

    The report is DESCRIPTIVE, not prescriptive. It describes what was
    observed, not what should be done.

    Usage:
        engine = EvolutionEngine()
        report = engine.evaluate(evidence_view, registry)

        # Inspect findings
        for gap in report.gaps:
            print(f"Gap: {gap.description}")
        for alert in report.degradations:
            print(f"Degradation: {alert.description}")

        # Review proposals
        for proposal in report.proposals:
            if proposal.status == "draft":
                proposal.submit()  # manual action
    """

    report_id: str = ""
    title: str = "Evolution Report"

    # ── Findings (observations, NOT prescriptions) ──
    gaps: list[GapCandidate] = field(default_factory=list)
    degradations: list[DegradationAlert] = field(default_factory=list)
    coverage_gaps: list[CoverageGap] = field(default_factory=list)
    cross_capability_insights: list[CrossCapabilityInsight] = field(default_factory=list)

    # ── Derived proposals (all start as draft) ──
    proposals: list[EvolutionProposal] = field(default_factory=list)

    # ── Statistics ──
    total_evidence_analyzed: int = 0
    total_capabilities_evaluated: int = 0
    evidence_window_start: str = ""
    evidence_window_end: str = ""

    # ── Summary ──
    summary: str = ""

    # ── Metadata ──
    generated_at: str = field(default_factory=_now)
    engine_version: str = "4.5"

    def __post_init__(self):
        if not self.report_id:
            self.report_id = _uid("EVO-RPT-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "title": self.title,
            "gaps": [g.to_dict() for g in self.gaps],
            "degradations": [d.to_dict() for d in self.degradations],
            "coverage_gaps": [c.to_dict() for c in self.coverage_gaps],
            "cross_capability_insights": [c.to_dict() for c in self.cross_capability_insights],
            "proposals": [p.to_dict() for p in self.proposals],
            "total_evidence_analyzed": self.total_evidence_analyzed,
            "total_capabilities_evaluated": self.total_capabilities_evaluated,
            "evidence_window_start": self.evidence_window_start,
            "evidence_window_end": self.evidence_window_end,
            "summary": self.summary,
            "generated_at": self.generated_at,
            "engine_version": self.engine_version,
        }

    @property
    def total_findings(self) -> int:
        """Total number of observations (not including proposals)."""
        return (
            len(self.gaps)
            + len(self.degradations)
            + len(self.coverage_gaps)
            + len(self.cross_capability_insights)
        )

    @property
    def has_actionable_observations(self) -> bool:
        """Are there any warning-or-critical findings?"""
        return any(
            o.severity in ("warning", "critical")
            for observations in [
                self.gaps,
                self.degradations,
                self.coverage_gaps,
                self.cross_capability_insights,
            ]
            for o in observations
        )

    @property
    def draft_proposals(self) -> list[EvolutionProposal]:
        """Proposals still in draft status."""
        return [p for p in self.proposals if p.status == "draft"]

    @property
    def actionable_proposals(self) -> list[EvolutionProposal]:
        """Proposals ready for submission (draft status)."""
        return self.draft_proposals


# ═══════════════════════════════════════════════════════════════════════════
# Evolution Engine
# ═══════════════════════════════════════════════════════════════════════════


class EvolutionEngine:
    """
    Evaluates accumulated Evidence to produce EvolutionReports.

    This is the EVALUATION step in the System Loop. It reads from
    EvidenceView and CapabilityRegistry and produces descriptive
    EvolutionReports containing:

    - GapCandidates: patterns/sections/vocabulary with no capability
    - DegradationAlerts: existing capabilities showing decline
    - CoverageGaps: content types not served by any capability
    - CrossCapabilityInsights: patterns spanning multiple capabilities
    - EvolutionProposals: derived from the above (draft status)

    CONSTRAINTS:
        - READ-ONLY: never modifies Registry, Capability, or Evidence
        - DESCRIPTIVE: all output describes what was OBSERVED
        - PROPOSALS ONLY: never auto-applies, never auto-registers
        - SOURCE TRACE: all findings reference evidence/experience IDs
        - NO AGENT: no autonomous planning, no self-modification

    Usage:
        engine = EvolutionEngine()
        report = engine.evaluate(evidence_view, registry)

        # Review gaps
        for gap in report.gaps:
            print(f"[{gap.severity}] {gap.gap_type}: {gap.description}")

        # Review proposals
        for prop in report.proposals:
            print(f"[{prop.status}] {prop.proposal_type}: {prop.rationale[:100]}")

        # Submit for validation (external action)
        for prop in report.actionable_proposals:
            if review_approves(prop):
                prop.submit()
    """

    def __init__(self):
        self._last_report: Optional[EvolutionReport] = None

    # ═══════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════

    def evaluate(
        self,
        evidence_view: EvidenceView,
        registry: Any = None,       # CapabilityRegistry, optional
        health_reports: Optional[dict[str, HealthReport]] = None,
    ) -> EvolutionReport:
        """
        Evaluate all accumulated evidence and produce an EvolutionReport.

        Args:
            evidence_view: EvidenceView with accumulated evidence
            registry: CapabilityRegistry for capability lookup (optional)
            health_reports: Pre-computed HealthReports per capability (optional)

        Returns:
            EvolutionReport with all findings and proposals
        """
        total_evidence = evidence_view.total()

        report = EvolutionReport(
            total_evidence_analyzed=total_evidence,
        )

        if total_evidence == 0:
            report.summary = "No evidence accumulated — nothing to evaluate."
            self._last_report = report
            return report

        # Determine evidence time window
        all_evidence = evidence_view._all
        if all_evidence:
            timestamps = sorted(e.produced_at for e in all_evidence)
            report.evidence_window_start = timestamps[0]
            report.evidence_window_end = timestamps[-1]

        # ── Step 1: Analyze gaps ──
        report.gaps = self.analyze_gaps(evidence_view, registry)

        # ── Step 2: Detect degradation ──
        report.degradations = self.detect_degradation(
            evidence_view, registry, health_reports
        )

        # ── Step 3: Analyze coverage ──
        report.coverage_gaps = self.analyze_coverage(evidence_view, registry)

        # ── Step 4: Cross-capability analysis ──
        report.cross_capability_insights = self.analyze_cross_capability(
            evidence_view, registry
        )

        # ── Step 5: Count capabilities ──
        report.total_capabilities_evaluated = self._count_capabilities(evidence_view)

        # ── Step 6: Generate proposals ──
        report.proposals = self.generate_proposals(report)

        # ── Step 7: Build summary ──
        report.summary = self._build_summary(report)

        self._last_report = report
        return report

    # ═══════════════════════════════════════════════════════════════════
    # GAP ANALYSIS
    # ═══════════════════════════════════════════════════════════════════

    def analyze_gaps(
        self,
        evidence_view: EvidenceView,
        registry: Any = None,
    ) -> list[GapCandidate]:
        """
        Analyze evidence for capability gaps.

        Looks for:
        - Patterns in failures that suggest missing capabilities
        - Vocabulary terms consistently appearing in failures
        - Strategy mismatches (capability exists but doesn't fit)

        Returns descriptive GapCandidates — NOT prescriptions.
        """
        gaps: list[GapCandidate] = []

        # ── Gap type 1: Pattern mismatch → possible missing capability ──
        mismatches = evidence_view.by_type(EvidenceType.PATTERN_MISMATCH)
        if mismatches:
            # Group by document to find persistent mismatches
            by_doc: dict[str, list[Evidence]] = {}
            for evd in mismatches:
                by_doc.setdefault(evd.document_id, []).append(evd)

            for doc_id, doc_evds in by_doc.items():
                if len(doc_evds) >= 2:  # Multiple mismatches in same document
                    gap = GapCandidate(
                        gap_type="pattern_unmatched",
                        description=(
                            f"Multiple pattern mismatches detected in document "
                            f"'{doc_id}' — {len(doc_evds)} patterns have no "
                            f"matching capability registered"
                        ),
                        evidence_ids=[e.id for e in doc_evds],
                        experience_ids=list(set(
                            e.experience_id for e in doc_evds if e.experience_id
                        )),
                        observed_in_documents=[doc_id],
                        observed_in_slices=list(set(
                            e.slice_id for e in doc_evds if e.slice_id
                        )),
                        observed_frequency=len(doc_evds),
                        severity="warning" if len(doc_evds) >= 5 else "info",
                        confidence=min(0.9, 0.4 + 0.1 * len(doc_evds)),
                    )
                    gaps.append(gap)

        # ── Gap type 2: Execution failures → vocabulary/structure gaps ──
        failures = evidence_view.by_type(EvidenceType.EXECUTION_FAILURE)
        if failures:
            # Group by capability to find persistent failures
            by_cap: dict[str, list[Evidence]] = {}
            for f in failures:
                by_cap.setdefault(f.capability_id, []).append(f)

            for cap_id, cap_failures in by_cap.items():
                if len(cap_failures) >= 3:
                    # Extract failure reasons
                    reasons: dict[str, int] = {}
                    for f in cap_failures:
                        reason = f.payload.get("failure_reason", "unknown")
                        reasons[reason] = reasons.get(reason, 0) + 1

                    top_reason = max(reasons, key=reasons.get)
                    top_count = reasons[top_reason]

                    if top_count >= 2:
                        gap = GapCandidate(
                            gap_type="strategy_mismatch",
                            description=(
                                f"Capability '{cap_id}' has {len(cap_failures)} failures. "
                                f"Top reason '{top_reason[:80]}' occurred {top_count} times"
                            ),
                            evidence_ids=[f.id for f in cap_failures],
                            experience_ids=list(set(
                                f.experience_id for f in cap_failures if f.experience_id
                            )),
                            affected_capability_ids=[cap_id],
                            observed_frequency=len(cap_failures),
                            severity="critical" if len(cap_failures) >= 10 else (
                                "warning" if len(cap_failures) >= 5 else "info"
                            ),
                            confidence=0.85,
                            pattern_signature={
                                "failure_count": len(cap_failures),
                                "top_failure_reason": top_reason,
                                "top_failure_count": top_count,
                            },
                        )
                        gaps.append(gap)

        # ── Gap type 3: Component missing → vocabulary gap ──
        missing_components = evidence_view.by_type(EvidenceType.COMPONENT_MISSING)
        if missing_components:
            # Group by document
            by_doc: dict[str, list[Evidence]] = {}
            for evd in missing_components:
                by_doc.setdefault(evd.document_id, []).append(evd)

            for doc_id, doc_evds in by_doc.items():
                total_missing = sum(
                    e.payload.get("missing_count", 1) for e in doc_evds
                )
                if total_missing >= 3:
                    gap = GapCandidate(
                        gap_type="vocabulary_missing",
                        description=(
                            f"Document '{doc_id}' has {total_missing} components "
                            f"not recognized by any capability — possible "
                            f"vocabulary gap in component extraction"
                        ),
                        evidence_ids=[e.id for e in doc_evds],
                        experience_ids=list(set(
                            e.experience_id for e in doc_evds if e.experience_id
                        )),
                        observed_in_documents=[doc_id],
                        observed_frequency=total_missing,
                        severity="warning",
                        confidence=0.75,
                    )
                    gaps.append(gap)

        return gaps

    # ═══════════════════════════════════════════════════════════════════
    # DEGRADATION DETECTION
    # ═══════════════════════════════════════════════════════════════════

    def detect_degradation(
        self,
        evidence_view: EvidenceView,
        registry: Any = None,
        health_reports: Optional[dict[str, HealthReport]] = None,
    ) -> list[DegradationAlert]:
        """
        Detect capability degradation from evidence.

        Analyzes success rates, confidence trends, and failure patterns
        to identify capabilities that are declining.

        Returns descriptive DegradationAlerts — NOT prescriptions.
        """
        alerts: list[DegradationAlert] = []

        # Collect all unique capability IDs
        cap_ids: set[str] = set()
        for evd_type in [
            EvidenceType.EXECUTION_SUCCESS,
            EvidenceType.EXECUTION_FAILURE,
        ]:
            for evd in evidence_view.by_type(evd_type):
                if evd.capability_id:
                    cap_ids.add(evd.capability_id)

        for cap_id in cap_ids:
            success_count, total, rate = evidence_view.success_rate(cap_id)

            if total < 3:
                continue  # Not enough data

            # ── Degradation type 1: Low success rate ──
            if rate < 0.5 and total >= 5:
                alerts.append(DegradationAlert(
                    capability_id=cap_id,
                    degradation_type="success_rate_drop",
                    description=(
                        f"Capability '{cap_id}' success rate is {rate:.1%} "
                        f"({success_count}/{total}) — below 50% threshold"
                    ),
                    evidence_ids=[
                        e.id for e in evidence_view.by_type(
                            EvidenceType.EXECUTION_FAILURE, cap_id
                        )
                    ] + [
                        e.id for e in evidence_view.by_type(
                            EvidenceType.EXECUTION_SUCCESS, cap_id
                        )
                    ],
                    severity="critical" if rate < 0.25 else "warning",
                    metric_name="success_rate",
                    metric_before=1.0,   # ideal baseline
                    metric_after=rate,
                    delta=rate - 1.0,
                    observation_window=f"last {total} executions",
                    total_executions_in_window=total,
                ))

            # ── Degradation type 2: Confidence decline ──
            confidence_evds = evidence_view.by_type(
                EvidenceType.CONFIDENCE_CHANGE, cap_id
            )
            if confidence_evds:
                # Check if recent confidence is trending down
                sorted_evds = sorted(
                    confidence_evds, key=lambda e: e.produced_at
                )
                recent = sorted_evds[-5:] if len(sorted_evds) >= 5 else sorted_evds
                avg_delta = sum(
                    e.payload.get("delta", 0) for e in recent
                ) / len(recent) if recent else 0

                if avg_delta < -0.05:  # Significant negative trend
                    alerts.append(DegradationAlert(
                        capability_id=cap_id,
                        degradation_type="confidence_decline",
                        description=(
                            f"Capability '{cap_id}' confidence trending down "
                            f"(avg delta: {avg_delta:+.4f} over last {len(recent)} executions)"
                        ),
                        evidence_ids=[e.id for e in recent],
                        severity="warning" if avg_delta < -0.1 else "info",
                        metric_name="confidence",
                        metric_before=recent[0].payload.get("confidence_before", 0) if recent else 0,
                        metric_after=recent[-1].payload.get("confidence_after", 0) if recent else 0,
                        delta=avg_delta,
                        observation_window=f"last {len(recent)} confidence changes",
                        total_executions_in_window=len(recent),
                    ))

            # ── Degradation type 3: Failure rate spike ──
            failures = evidence_view.by_type(
                EvidenceType.EXECUTION_FAILURE, cap_id
            )
            if failures and total >= 10:
                # Check if recent failures are concentrated
                recent_failures = [
                    f for f in failures
                    if f.produced_at >= sorted_evds[-1].produced_at
                ] if confidence_evds else failures[-3:]

                if len(recent_failures) >= 3 and len(recent_failures) / total > 0.5:
                    alerts.append(DegradationAlert(
                        capability_id=cap_id,
                        degradation_type="failure_rate_spike",
                        description=(
                            f"Capability '{cap_id}': {len(recent_failures)} recent "
                            f"failures ({len(recent_failures)/total:.0%} of total) — "
                            f"possible failure rate spike"
                        ),
                        evidence_ids=[f.id for f in recent_failures],
                        severity="warning",
                        metric_name="failure_rate",
                        metric_before=0.0,
                        metric_after=len(recent_failures) / total,
                        delta=len(recent_failures) / total,
                        observation_window=f"recent vs total {total} executions",
                        total_executions_in_window=len(recent_failures),
                    ))

        return alerts

    # ═══════════════════════════════════════════════════════════════════
    # COVERAGE ANALYSIS
    # ═══════════════════════════════════════════════════════════════════

    def analyze_coverage(
        self,
        evidence_view: EvidenceView,
        registry: Any = None,
    ) -> list[CoverageGap]:
        """
        Analyze evidence for coverage gaps — content patterns not served
        by any registered capability.

        Looks for:
        - Slices/documents with zero successful executions
        - Patterns that appear in evidence but have no matching capability
        - Validation failures suggesting unserved content types

        Returns descriptive CoverageGaps — NOT prescriptions.
        """
        gaps: list[CoverageGap] = []

        # ── Coverage gap type 1: Validation failures on specific documents ──
        validation_failures = evidence_view.by_type(EvidenceType.VALIDATION_FAILED)
        if validation_failures:
            by_doc: dict[str, list[Evidence]] = {}
            for evd in validation_failures:
                by_doc.setdefault(evd.document_id, []).append(evd)

            for doc_id, doc_evds in by_doc.items():
                if len(doc_evds) >= 2:
                    gap = CoverageGap(
                        gap_type="section_unserved",
                        description=(
                            f"Document '{doc_id}' has {len(doc_evds)} validation "
                            f"failures — sections may not be covered by any "
                            f"registered capability"
                        ),
                        uncovered_pattern=f"validation_failures_in_{doc_id}",
                        evidence_ids=[e.id for e in doc_evds],
                        experience_ids=list(set(
                            e.experience_id for e in doc_evds if e.experience_id
                        )),
                        observed_in_documents=[doc_id],
                        observed_count=len(doc_evds),
                        severity="warning" if len(doc_evds) >= 4 else "info",
                    )
                    gaps.append(gap)

        # ── Coverage gap type 2: Documents with zero success evidence ──
        success_evds = evidence_view.by_type(EvidenceType.EXECUTION_SUCCESS)
        docs_with_success: set[str] = set()
        docs_all: set[str] = set()

        for evd in success_evds:
            if evd.document_id:
                docs_with_success.add(evd.document_id)

        for evd_type in [
            EvidenceType.EXECUTION_SUCCESS,
            EvidenceType.EXECUTION_FAILURE,
        ]:
            for evd in evidence_view.by_type(evd_type):
                if evd.document_id:
                    docs_all.add(evd.document_id)

        docs_without_success = docs_all - docs_with_success
        for doc_id in docs_without_success:
            doc_failures = [
                e for e in evidence_view.by_type(EvidenceType.EXECUTION_FAILURE)
                if e.document_id == doc_id
            ]
            if doc_failures:
                gap = CoverageGap(
                    gap_type="domain_uncovered",
                    description=(
                        f"Document '{doc_id}' has zero successful executions "
                        f"({len(doc_failures)} failures) — possible unserved "
                        f"document domain"
                    ),
                    uncovered_pattern=f"domain_{doc_id}",
                    evidence_ids=[e.id for e in doc_failures],
                    experience_ids=list(set(
                        e.experience_id for e in doc_failures if e.experience_id
                    )),
                    observed_in_documents=[doc_id],
                    observed_count=len(doc_failures),
                    severity="warning",
                )
                gaps.append(gap)

        return gaps

    # ═══════════════════════════════════════════════════════════════════
    # CROSS-CAPABILITY ANALYSIS
    # ═══════════════════════════════════════════════════════════════════

    def analyze_cross_capability(
        self,
        evidence_view: EvidenceView,
        registry: Any = None,
    ) -> list[CrossCapabilityInsight]:
        """
        Analyze evidence for patterns that span multiple capabilities.

        Looks for:
        - Shared failure domains (same document fails for multiple caps)
        - Shared vocabulary gaps across capabilities
        - Complementary coverage patterns

        Returns descriptive CrossCapabilityInsights — NOT prescriptions.
        """
        insights: list[CrossCapabilityInsight] = []

        # ── Insight type 1: Shared failure domain ──
        failures = evidence_view.by_type(EvidenceType.EXECUTION_FAILURE)
        if len(failures) >= 3:
            # Group by document
            by_doc: dict[str, list[Evidence]] = {}
            for evd in failures:
                by_doc.setdefault(evd.document_id, []).append(evd)

            for doc_id, doc_evds in by_doc.items():
                affected_caps = set(e.capability_id for e in doc_evds)
                if len(affected_caps) >= 2:
                    insight = CrossCapabilityInsight(
                        insight_type="shared_failure_domain",
                        description=(
                            f"Document '{doc_id}' causes failures across "
                            f"{len(affected_caps)} capabilities: "
                            f"{', '.join(list(affected_caps)[:3])}"
                        ),
                        evidence_ids=[e.id for e in doc_evds],
                        experience_ids=list(set(
                            e.experience_id for e in doc_evds if e.experience_id
                        )),
                        capability_ids=list(affected_caps),
                        severity="warning" if len(affected_caps) >= 3 else "info",
                        shared_evidence={
                            "document_id": doc_id,
                            "failure_count": len(doc_evds),
                            "affected_capabilities": list(affected_caps),
                        },
                    )
                    insights.append(insight)

        # ── Insight type 2: Complementary coverage ──
        # Two capabilities covering disjoint sections of the same document type
        success_evds = evidence_view.by_type(EvidenceType.EXECUTION_SUCCESS)
        if len(success_evds) >= 4:
            by_doc: dict[str, dict[str, list[Evidence]]] = {}
            for evd in success_evds:
                doc = evd.document_id
                cap = evd.capability_id
                if doc and cap:
                    by_doc.setdefault(doc, {}).setdefault(cap, []).append(evd)

            for doc_id, cap_evds in by_doc.items():
                if len(cap_evds) >= 2:
                    cap_ids = list(cap_evds.keys())
                    # Check if they cover different slices
                    slices_covered: dict[str, set[str]] = {}
                    for cap_id, evds in cap_evds.items():
                        slices_covered[cap_id] = set(
                            e.slice_id for e in evds if e.slice_id
                        )

                    # If slices are disjoint, they're complementary
                    all_slices: set[str] = set()
                    for slices in slices_covered.values():
                        all_slices.update(slices)

                    if len(all_slices) > max(len(s) for s in slices_covered.values()):
                        insight = CrossCapabilityInsight(
                            insight_type="complementary_coverage",
                            description=(
                                f"Capabilities {', '.join(cap_ids[:3])} provide "
                                f"complementary coverage of document '{doc_id}' "
                                f"({len(all_slices)} total slices)"
                            ),
                            evidence_ids=[
                                e.id for evds in cap_evds.values() for e in evds
                            ],
                            capability_ids=cap_ids,
                            severity="info",
                            shared_evidence={
                                "document_id": doc_id,
                                "total_slices": len(all_slices),
                                "capability_slices": {
                                    cid: len(s) for cid, s in slices_covered.items()
                                },
                            },
                        )
                        insights.append(insight)

        return insights

    # ═══════════════════════════════════════════════════════════════════
    # PROPOSAL GENERATION
    # ═══════════════════════════════════════════════════════════════════

    def generate_proposals(
        self, report: EvolutionReport
    ) -> list[EvolutionProposal]:
        """
        Generate EvolutionProposals from the evaluated findings.

        Each finding (gap, degradation, coverage gap, insight) can spawn
        an EvolutionProposal. All proposals start as DRAFT — never auto-applied.

        Proposals reference source evidence/experience for full traceability.

        Returns list of EvolutionProposals (all in draft status).
        """
        proposals: list[EvolutionProposal] = []

        # ── From gaps ──
        for gap in report.gaps:
            if gap.severity in ("warning", "critical"):
                proposal_type = self._map_gap_type_to_proposal_type(gap.gap_type)
                signal = EnhancementSignal(
                    signal_type=gap.gap_type,
                    severity=gap.severity,
                    description=gap.description,
                    evidence={
                        "gap_id": gap.gap_id,
                        "observed_frequency": gap.observed_frequency,
                    },
                )

                proposal = EvolutionProposal(
                    capability_id=(
                        gap.affected_capability_ids[0]
                        if gap.affected_capability_ids else "unknown"
                    ),
                    proposal_type=proposal_type,
                    trigger_signals=[signal],
                    trigger_experience_ids=gap.experience_ids,
                    trigger_evidence_ids=gap.evidence_ids,
                    observed_phenomenon={
                        "observation": gap.gap_type,
                        "gap_id": gap.gap_id,
                        "observed_frequency": gap.observed_frequency,
                        "observed_in_documents": gap.observed_in_documents[:5],
                        "confidence": gap.confidence,
                    },
                    rationale=(
                        f"Gap detected: {gap.description}. "
                        f"Observed {gap.observed_frequency} times across "
                        f"{len(gap.observed_in_documents)} document(s)."
                    ),
                    validation_required=self._determine_validation_requirements(
                        gap.severity, gap.gap_type
                    ),
                )
                proposals.append(proposal)

        # ── From degradations ──
        for alert in report.degradations:
            if alert.severity in ("warning", "critical"):
                signal = EnhancementSignal(
                    signal_type=alert.degradation_type,
                    severity=alert.severity,
                    description=alert.description,
                    evidence={
                        "alert_id": alert.alert_id,
                        "metric_name": alert.metric_name,
                        "metric_before": alert.metric_before,
                        "metric_after": alert.metric_after,
                        "delta": alert.delta,
                    },
                )

                proposal = EvolutionProposal(
                    capability_id=alert.capability_id,
                    capability_name=alert.capability_name,
                    proposal_type="performance_degradation",
                    trigger_signals=[signal],
                    trigger_experience_ids=[],
                    trigger_evidence_ids=alert.evidence_ids,
                    observed_phenomenon={
                        "observation": alert.degradation_type,
                        "alert_id": alert.alert_id,
                        "metric_name": alert.metric_name,
                        "metric_before": alert.metric_before,
                        "metric_after": alert.metric_after,
                        "delta": alert.delta,
                    },
                    rationale=(
                        f"Degradation detected: {alert.description}. "
                        f"Metric '{alert.metric_name}' changed from "
                        f"{alert.metric_before:.4f} to {alert.metric_after:.4f} "
                        f"(delta: {alert.delta:+.4f})."
                    ),
                    validation_required=[
                        "degradation_root_cause_analysis",
                        "regression_guard",
                        "cross_document_check",
                    ],
                )
                proposals.append(proposal)

        # ── From coverage gaps ──
        for cov_gap in report.coverage_gaps:
            if cov_gap.severity in ("warning", "critical"):
                signal = EnhancementSignal(
                    signal_type="coverage_gap",
                    severity=cov_gap.severity,
                    description=cov_gap.description,
                    evidence={
                        "gap_id": cov_gap.gap_id,
                        "uncovered_pattern": cov_gap.uncovered_pattern,
                        "observed_count": cov_gap.observed_count,
                    },
                )

                proposal = EvolutionProposal(
                    capability_id="unknown",
                    proposal_type="pattern_coverage_gap",
                    trigger_signals=[signal],
                    trigger_experience_ids=cov_gap.experience_ids,
                    trigger_evidence_ids=cov_gap.evidence_ids,
                    observed_phenomenon={
                        "observation": "coverage_gap",
                        "gap_id": cov_gap.gap_id,
                        "uncovered_pattern": cov_gap.uncovered_pattern,
                        "observed_in_documents": cov_gap.observed_in_documents[:5],
                        "observed_count": cov_gap.observed_count,
                    },
                    rationale=(
                        f"Coverage gap detected: {cov_gap.description}. "
                        f"Pattern '{cov_gap.uncovered_pattern}' observed in "
                        f"{len(cov_gap.observed_in_documents)} document(s)."
                    ),
                    validation_required=[
                        "pattern_existence_verification",
                        "capability_conflict_check",
                        "cross_document_check",
                    ],
                )
                proposals.append(proposal)

        # ── From cross-capability insights ──
        for insight in report.cross_capability_insights:
            if insight.severity in ("warning", "critical"):
                signal = EnhancementSignal(
                    signal_type=insight.insight_type,
                    severity=insight.severity,
                    description=insight.description,
                    evidence={
                        "insight_id": insight.insight_id,
                        "capability_ids": insight.capability_ids,
                    },
                )

                proposal = EvolutionProposal(
                    capability_id=(
                        insight.capability_ids[0]
                        if insight.capability_ids else "unknown"
                    ),
                    proposal_type="cross_capability_insight",
                    trigger_signals=[signal],
                    trigger_experience_ids=insight.experience_ids,
                    trigger_evidence_ids=insight.evidence_ids,
                    observed_phenomenon={
                        "observation": insight.insight_type,
                        "insight_id": insight.insight_id,
                        "capability_ids": insight.capability_ids,
                    },
                    rationale=(
                        f"Cross-capability insight: {insight.description}"
                    ),
                    validation_required=[
                        "cross_capability_compatibility_check",
                        "regression_guard",
                    ],
                )
                proposals.append(proposal)

        return proposals

    # ═══════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _map_gap_type_to_proposal_type(gap_type: str) -> str:
        """Map GapCandidate types to EvolutionProposal types."""
        mapping = {
            "pattern_unmatched": "pattern_coverage_gap",
            "vocabulary_missing": "vocabulary_gap_observed",
            "section_unserved": "pattern_coverage_gap",
            "cross_domain_failure": "scope_boundary_uncertain",
            "strategy_mismatch": "implementation_strategy_mismatch",
        }
        return mapping.get(gap_type, "pattern_coverage_gap")

    @staticmethod
    def _determine_validation_requirements(
        severity: str, gap_type: str
    ) -> list[str]:
        """Determine validation requirements based on severity and gap type."""
        requirements = ["cross_document_check"]

        if severity == "critical":
            requirements.append("regression_guard")
            requirements.append("success_rate_threshold")

        if gap_type == "pattern_unmatched":
            requirements.append("pattern_existence_verification")
        elif gap_type == "vocabulary_missing":
            requirements.append("vocabulary_frequency_validation")
        elif gap_type == "strategy_mismatch":
            requirements.append("strategy_compatibility_check")

        return requirements

    @staticmethod
    def _count_capabilities(evidence_view: EvidenceView) -> int:
        """Count unique capability IDs in evidence."""
        cap_ids: set[str] = set()
        for evd in evidence_view._all:
            if evd.capability_id and evd.capability_id != "unknown":
                cap_ids.add(evd.capability_id)
        return len(cap_ids)

    @staticmethod
    def _build_summary(report: EvolutionReport) -> str:
        """Build a human-readable summary of the EvolutionReport."""
        parts: list[str] = []

        total_findings = report.total_findings
        critical_count = sum(
            1 for o in (
                report.gaps + report.degradations +
                report.coverage_gaps + report.cross_capability_insights
            )
            if o.severity == "critical"
        )
        warning_count = sum(
            1 for o in (
                report.gaps + report.degradations +
                report.coverage_gaps + report.cross_capability_insights
            )
            if o.severity == "warning"
        )

        parts.append(
            f"Evolution Report: {total_findings} findings "
            f"({critical_count} critical, {warning_count} warning) "
            f"from {report.total_evidence_analyzed} evidence nodes "
            f"across {report.total_capabilities_evaluated} capabilities."
        )

        if report.gaps:
            parts.append(
                f"Gaps: {len(report.gaps)} detected "
                f"({', '.join(g.gap_type for g in report.gaps[:3])})"
            )

        if report.degradations:
            parts.append(
                f"Degradations: {len(report.degradations)} detected "
                f"({', '.join(d.capability_id for d in report.degradations[:3])})"
            )

        if report.coverage_gaps:
            parts.append(
                f"Coverage gaps: {len(report.coverage_gaps)} detected"
            )

        if report.cross_capability_insights:
            parts.append(
                f"Cross-capability insights: "
                f"{len(report.cross_capability_insights)} detected"
            )

        parts.append(
            f"Proposals: {len(report.proposals)} generated (all draft)"
        )

        return " | ".join(parts)

    # ═══════════════════════════════════════════════════════════════════
    # QUERY
    # ═══════════════════════════════════════════════════════════════════

    @property
    def last_report(self) -> Optional[EvolutionReport]:
        """Get the last generated report."""
        return self._last_report
