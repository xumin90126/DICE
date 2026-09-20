"""
System Loop — thin orchestrator for the complete Capability OS cycle.

Phase 4.5: Ties together the full System Loop:
    Observation → Matching → Execution → Experience → Evaluation → Proposal

This is NOT an Agent. It does NOT do autonomous planning, self-modification,
or automatic learning. It is a pipeline orchestrator that sequences the
existing components.

Architecture:
    SystemLoop
        │
        ├── ObservationBuilder     ← content → DocumentObservation
        ├── CapabilityMatcher      ← observation → MatchResult
        ├── ExecutionRuntime       ← match + content → ExecutionExperiences
        │       │
        │       └── FeedbackLoop   ← auto via executor (writes to ExperienceGraph)
        │               │
        │               └── EvidenceView
        │
        ├── EvolutionEngine        ← evidence_view → EvolutionReport
        │       │
        │       └── EvolutionProposals (draft)
        │
        └── SystemLoopResult       ← collected artifacts

CRITICAL DESIGN:
    1. NOT an Agent — no autonomous planning, no self-modification
    2. Pipelines only — sequences existing components
    3. Evaluation is explicit (call evaluate()) — not automatic
    4. No auto-registration or auto-application of proposals
    5. Agent/Application are FUTURE consumers, not part of this system
    6. The loop produces ARTIFACTS (proposals, reports) — not actions

Usage:
    registry = CapabilityRegistry()
    loop = SystemLoop(registry)

    # Run a single document through the loop
    result = loop.run(content, "DC201-C1", "04_components")

    # Inspect results
    print(result.match.matched_capabilities)
    for exp in result.experiences:
        print(f"{exp.capability_name}: {'✓' if exp.success else '✗'}")

    # Evaluate (explicit call)
    report = loop.evaluate()
    print(report.summary)
    for proposal in report.actionable_proposals:
        print(f"[draft] {proposal.rationale[:100]}")
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.graph.nodes import DocumentObservation
from dice.registry import CapabilityRegistry
from dice.evidence import EvidenceView
from dice.evolution import EvolutionEngine, EvolutionReport, EvolutionProposal
from dice.runtime.matching import (
    CapabilityMatcher, ObservationBuilder, MatchResult, MatcherConfig,
)
from dice.runtime.execution import ExecutionRuntime, RuntimeConfig
from dice.runtime.experience.execution_models import ExecutionExperience
from dice.runtime.experience.feedback_loop import (
    FeedbackLoop, FeedbackResult, HealthReport,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# System Loop Result
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class SystemLoopResult:
    """
    Complete result of one System Loop cycle.

    Contains all artifacts produced by the cycle:
    Observation → Matching → Execution → Feedback → (optional) Evaluation.

    This is a DATA CONTAINER — not an action, not a plan, not a decision.
    """

    cycle_id: str = ""
    document_id: str = ""
    slice_id: str = ""

    # ── Pipeline artifacts ──
    observation: Optional[DocumentObservation] = None
    match_result: Optional[MatchResult] = None
    experiences: list[ExecutionExperience] = field(default_factory=list)
    feedback_result: Optional[FeedbackResult] = None

    # ── Optional evaluation (explicit call only) ──
    evolution_report: Optional[EvolutionReport] = None

    # ── Metadata ──
    cycle_started_at: str = field(default_factory=_now)
    cycle_completed_at: str = ""
    errors: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.cycle_id:
            self.cycle_id = _uid("CYCLE-")

    @property
    def success(self) -> bool:
        """Was the cycle free of errors?"""
        return len(self.errors) == 0

    @property
    def total_experiences(self) -> int:
        """Total execution experiences produced."""
        return len(self.experiences)

    @property
    def successful_experiences(self) -> int:
        """Number of successful executions."""
        return sum(1 for e in self.experiences if e.success)

    @property
    def failed_experiences(self) -> int:
        """Number of failed executions."""
        return sum(1 for e in self.experiences if not e.success)

    @property
    def has_evaluation(self) -> bool:
        """Was evaluation performed?"""
        return self.evolution_report is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "observation": (
                self.observation.to_dict() if self.observation else None
            ),
            "match_result": (
                self.match_result.to_dict() if self.match_result else None
            ),
            "experiences_count": len(self.experiences),
            "experiences": [e.to_dict() for e in self.experiences],
            "feedback_result": (
                {
                    "experiences_processed": self.feedback_result.experiences_processed,
                    "evidence_nodes_produced": self.feedback_result.evidence_nodes_produced,
                    "proposals_generated": len(self.feedback_result.proposals),
                }
                if self.feedback_result else None
            ),
            "evolution_report": (
                self.evolution_report.to_dict()
                if self.evolution_report else None
            ),
            "cycle_started_at": self.cycle_started_at,
            "cycle_completed_at": self.cycle_completed_at,
            "errors": self.errors,
        }


# ═══════════════════════════════════════════════════════════════════════════
# System Loop Configuration
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class SystemLoopConfig:
    """
    Configuration for the SystemLoop.

    Attributes:
        storage_dir: where feedback/evidence data is persisted
        enable_feedback: if True, auto-feed execution experiences to FeedbackLoop
        enable_evaluation: if True, auto-evaluate after run (NOT recommended —
            evaluation should be explicit to avoid automatic proposal generation)
        matcher_config: configuration for the CapabilityMatcher
        runtime_config: configuration for the ExecutionRuntime
    """
    storage_dir: str = "dice_output/system_loop"
    enable_feedback: bool = True
    enable_auto_evaluation: bool = False  # SAFETY: default OFF
    matcher_config: Optional[MatcherConfig] = None
    runtime_config: Optional[RuntimeConfig] = None


DEFAULT_LOOP_CONFIG = SystemLoopConfig()


# ═══════════════════════════════════════════════════════════════════════════
# System Loop
# ═══════════════════════════════════════════════════════════════════════════


class SystemLoop:
    """
    Thin orchestrator for the complete Capability Operating System cycle.

    Sequences the pipeline:
        Observation → Matching → Execution → Experience → (Evaluation)

    This is NOT an Agent:
        - No autonomous planning
        - No self-modification
        - No automatic learning
        - No internal goal system
        - No decision-making

    It is a PIPELINE ORCHESTRATOR:
        - Takes content → produces artifacts
        - Evaluation is explicit (call evaluate())
        - Proposals are draft, never auto-applied
        - All components are stateless relative to the loop

    Usage:
        loop = SystemLoop(registry)

        # Single document
        result = loop.run(content, "DC201-C1", "04_components")

        # Batch
        results = loop.run_batch([
            (content1, "DC201-C1", "04_components"),
            (content2, "DC201-C1", "05_principles"),
        ])

        # Explicit evaluation
        report = loop.evaluate()
        print(report.summary)
        for prop in report.actionable_proposals:
            print(f"→ {prop.id}: {prop.rationale[:80]}")
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        config: Optional[SystemLoopConfig] = None,
    ):
        """
        Initialize the SystemLoop.

        Args:
            registry: CapabilityRegistry with registered capabilities
            config: SystemLoop configuration
        """
        self._registry = registry
        self._config = config or DEFAULT_LOOP_CONFIG

        # ── Pipeline components ──

        # Matcher: Observation → ranked capability candidates
        self._matcher = CapabilityMatcher(
            registry=registry,
            config=self._config.matcher_config or MatcherConfig(),
        )

        # Runtime: MatchResult + content → ExecutionExperiences
        self._runtime = ExecutionRuntime(
            registry=registry,
            config=self._config.runtime_config or RuntimeConfig(),
        )

        # Feedback Loop: ExecutionExperiences → Evidence → Health
        self._feedback_loop = FeedbackLoop(
            registry=registry,
            storage_dir=self._config.storage_dir,
        )

        # Wire feedback into runtime
        self._runtime.set_feedback_loop(self._feedback_loop)

        # Evolution Engine: EvidenceView → EvolutionReport
        self._evolution_engine = EvolutionEngine()

        # ── Cycle tracking ──
        self._cycle_results: list[SystemLoopResult] = []

    # ═══════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINTS
    # ═══════════════════════════════════════════════════════════════════

    def run(
        self,
        content: str,
        document_id: str = "",
        slice_id: str = "",
    ) -> SystemLoopResult:
        """
        Run a single document/slice through the complete System Loop.

        Pipeline:
            1. Observation: parse content → DocumentObservation
            2. Matching: match observation → ranked candidates
            3. Execution: each matched capability → ExecutionExperience
            4. Feedback: each experience → Evidence + Health (auto)

        Evaluation is NOT automatic — call evaluate() separately.

        Args:
            content: Text content of the document/slice
            document_id: Source document identifier (traceability only)
            slice_id: Source slice identifier (traceability only)

        Returns:
            SystemLoopResult with all artifacts
        """
        result = SystemLoopResult(
            document_id=document_id,
            slice_id=slice_id,
        )

        # ── Step 1: Observation ──
        observation = ObservationBuilder.from_content(
            content, document_id, slice_id
        )
        result.observation = observation

        # ── Step 2: Matching ──
        match_result = self._matcher.match(observation)
        result.match_result = match_result

        # ── Step 3: Execution ──
        # Delegate to ExecutionRuntime — it does its own matching + execution.
        # The SystemLoop tracks the match result but does NOT select capabilities;
        # the Runtime resolves the best candidate from the Observation via its
        # internal CapabilityMatcher and executes it.
        if match_result and len(match_result.candidates) > 0:
            exec_result = self._runtime.execute(
                observation,
                content=content,
            )
            if exec_result and exec_result.experience:
                result.experiences.append(exec_result.experience)

        # ── Step 4: Feedback (auto if enabled) ──
        if self._config.enable_feedback and result.experiences:
            feedback_result = self._feedback_loop.process_batch(
                result.experiences
            )
            result.feedback_result = feedback_result

        # ── Step 5: Auto-evaluation (if enabled — OFF by default) ──
        if self._config.enable_auto_evaluation:
            result.evolution_report = self.evaluate()

        result.cycle_completed_at = _now()
        self._cycle_results.append(result)

        return result

    def run_batch(
        self,
        documents: list[tuple[str, str, str]],  # (content, doc_id, slice_id)
    ) -> list[SystemLoopResult]:
        """
        Run multiple documents through the System Loop.

        Each document runs the full pipeline independently.
        Feedback accumulates across all documents.

        Args:
            documents: List of (content, document_id, slice_id) tuples

        Returns:
            List of SystemLoopResult, one per document
        """
        results: list[SystemLoopResult] = []

        for content, doc_id, slice_id in documents:
            result = self.run(content, doc_id, slice_id)
            results.append(result)

        return results

    def evaluate(self) -> EvolutionReport:
        """
        EXPLICIT evaluation of all accumulated evidence.

        This is NEVER called automatically. It must be explicitly invoked
        by an external actor (human, application, or future Agent).

        Reads from the FeedbackLoop's EvidenceView and produces an
        EvolutionReport with gaps, degradations, coverage gaps,
        and draft EvolutionProposals.

        Returns:
            EvolutionReport containing all findings and proposals (draft)
        """
        evidence_view = self.evidence_view

        # Collect health reports from feedback loop
        health_reports: dict[str, HealthReport] = {}
        # (health reports are computed on-demand by FeedbackLoop.get_health())

        report = self._evolution_engine.evaluate(
            evidence_view=evidence_view,
            registry=self._registry,
            health_reports=health_reports,
        )

        return report

    # ═══════════════════════════════════════════════════════════════════
    # ACCESSORS
    # ═══════════════════════════════════════════════════════════════════

    @property
    def evidence_view(self) -> EvidenceView:
        """Access the EvidenceView (accumulated evidence)."""
        return self._feedback_loop.evidence_view

    @property
    def total_evidence(self) -> int:
        """Total evidence nodes accumulated."""
        return self.evidence_view.total()

    @property
    def total_experiences(self) -> int:
        """Total execution experiences accumulated across all cycles."""
        return sum(r.total_experiences for r in self._cycle_results)

    @property
    def total_cycles(self) -> int:
        """Total System Loop cycles executed."""
        return len(self._cycle_results)

    def get_cycle(self, cycle_id: str) -> Optional[SystemLoopResult]:
        """Get a specific cycle result by ID."""
        for r in self._cycle_results:
            if r.cycle_id == cycle_id:
                return r
        return None

    def get_cycles_for_document(
        self, document_id: str
    ) -> list[SystemLoopResult]:
        """Get all cycle results for a specific document."""
        return [r for r in self._cycle_results if r.document_id == document_id]

    def get_health(self, capability_id: str) -> HealthReport:
        """Get the latest health report for a capability."""
        return self._feedback_loop.get_health(capability_id)

    def get_proposals(
        self, capability_id: str = ""
    ) -> list[EvolutionProposal]:
        """Get evolution proposals from the feedback loop."""
        return self._feedback_loop.get_proposals(capability_id)

    def submit_proposal(self, proposal_id: str) -> bool:
        """
        Submit a draft proposal for validation.

        This is an EXPLICIT action — never automatic.
        Moves proposal from draft → proposed.
        """
        return self._feedback_loop.submit_proposal(proposal_id)

    # ═══════════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════════

    def stats(self) -> dict[str, Any]:
        """Get aggregate statistics across all cycles."""
        all_experiences: list[ExecutionExperience] = []
        for r in self._cycle_results:
            all_experiences.extend(r.experiences)

        cap_stats: dict[str, dict[str, int]] = {}
        for exp in all_experiences:
            cid = exp.capability_id or "unknown"
            if cid not in cap_stats:
                cap_stats[cid] = {"total": 0, "success": 0, "failure": 0}
            cap_stats[cid]["total"] += 1
            if exp.success:
                cap_stats[cid]["success"] += 1
            else:
                cap_stats[cid]["failure"] += 1

        return {
            "total_cycles": self.total_cycles,
            "total_experiences": self.total_experiences,
            "total_evidence": self.total_evidence,
            "successful_experiences": sum(
                1 for e in all_experiences if e.success
            ),
            "failed_experiences": sum(
                1 for e in all_experiences if not e.success
            ),
            "per_capability_stats": cap_stats,
        }

    # ═══════════════════════════════════════════════════════════════════
    # MAINTENANCE
    # ═══════════════════════════════════════════════════════════════════

    def clear(self) -> None:
        """Reset all accumulated state (for testing)."""
        self._cycle_results.clear()
        self._feedback_loop.clear()

    def shutdown(self) -> None:
        """Clean shutdown — persist any pending state."""
        # Currently all persistence is real-time (each write flushes)
        pass
