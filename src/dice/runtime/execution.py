"""
ExecutionRuntime — unified Capability execution engine.

Phase 4.2: Replaces CapabilityExecutor.execute_chapter() with a unified
Observation-driven execution pipeline that generates ExecutionExperience
for every execution.

Architecture:
    DocumentObservation
            │
            ▼
    CapabilityMatcher.match()
            │
            ▼
    MatchResult (ranked candidates)
            │
            ▼
    select best candidate
            │
            ▼
    CapabilityRegistry.get(capability_id)
            │
            ▼
    resolve execution strategy (from Capability + Implementation)
            │
            ▼
    execute strategy (delegated to strategy handler)
            │
            ▼
    CapabilityResult + ExecutionExperience
            │
            ▼
    Feedback Loop (Phase 4.3)

CRITICAL DESIGN:
    1. UNIFIED entry: execute(observation, content) — NOT execute_chapter()
    2. ZERO capability_id hardcoding — execution strategy resolved from Capability
    3. EVERY execution produces an ExecutionExperience (success OR failure)
    4. Runtime knows NOTHING about business rules — only strategy dispatch
    5. Legacy path available as strategy handler, NOT as primary path
    6. ZERO doc_class / product_id / filename in any execution path
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from dice.graph.nodes import (
    Capability, Implementation, DocumentObservation,
    CapabilityStatus,
)
from dice.registry import CapabilityRegistry
from dice.runtime.matching import (
    CapabilityMatcher, ObservationBuilder, MatchResult, MatcherConfig,
)
from dice.runtime.ranking import RankingModel, RankingWeights, DEFAULT_WEIGHTS
from dice.runtime.result import CapabilityResult, EvidenceItem
from dice.runtime.experience.execution_models import (
    ExecutionExperience, ExecutionResult,
)
from dice.models import SourceRef


# ═══════════════════════════════════════════════════════════════════════════
# Strategy Handler Type
# ═══════════════════════════════════════════════════════════════════════════

# A strategy handler takes (content, capability, implementation, context)
# and returns a CapabilityResult.
StrategyHandler = Callable[
    [str, Capability, Implementation, dict[str, Any]],
    CapabilityResult,
]


# ═══════════════════════════════════════════════════════════════════════════
# ExecutionRuntime
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class RuntimeConfig:
    """
    Configuration for the ExecutionRuntime.

    Attributes:
        min_match_score: minimum score to consider a capability applicable
        enable_experience_generation: if True, produce ExecutionExperience
        fallback_to_legacy: if True, fall back to legacy executor when no
            capability matches (temporary — will be removed)
        legacy_fallback_capability_id: capability_id for legacy fallback
            (only used when match_result has no candidates)
        ranking_weights: weights for the ranking formula
    """
    min_match_score: float = 0.25
    enable_experience_generation: bool = True
    fallback_to_legacy: bool = True
    legacy_fallback_capability_id: str = "CAP-COMP-TABLE"
    ranking_weights: RankingWeights = field(default_factory=lambda: DEFAULT_WEIGHTS)


DEFAULT_RUNTIME_CONFIG = RuntimeConfig()


class ExecutionRuntime:
    """
    Unified Capability Execution Runtime.

    This is THE entry point for all Capability execution. It replaces
    the old CapabilityExecutor.execute_chapter() with a clean pipeline:

        Observation → Matcher → Registry → Strategy → Result → Experience

    Usage:
        registry = CapabilityRegistry()
        runtime = ExecutionRuntime(registry)

        # Build observation from content
        obs = ObservationBuilder.from_content(content, doc_id, slice_id)

        # Execute
        result = runtime.execute(obs, content=content)

        # Inspect
        if result.success:
            print(result.capability_result.result)
        print(result.experience.to_dict())
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        config: Optional[RuntimeConfig] = None,
    ):
        """
        Initialize the ExecutionRuntime.

        Args:
            registry: the authoritative CapabilityRegistry
            config: optional runtime configuration
        """
        self.registry = registry
        self.config = config or DEFAULT_RUNTIME_CONFIG

        # Matcher — queries registry for active capabilities
        self.matcher = CapabilityMatcher(
            registry=registry,
            config=MatcherConfig(
                min_score_threshold=self.config.min_match_score,
                ranking_weights=self.config.ranking_weights,
            ),
        )

        # Strategy handler registry — maps strategy names to execution functions
        # Strategies are registered externally (not hardcoded in Runtime)
        self._strategy_handlers: dict[str, StrategyHandler] = {}

        # Legacy executor reference (for fallback)
        self._legacy_executor: Optional[Any] = None

        # Experience log (in-memory buffer, flushed to Feedback Loop in Phase 4.3)
        self._experience_log: list[ExecutionExperience] = []

        # Feedback Loop integration (Phase 4.5: wired by SystemLoop)
        self._feedback_loop: Optional[Any] = None

    def set_feedback_loop(self, feedback_loop: Any) -> None:
        """
        Wire in a FeedbackLoop for auto-recording ExecutionExperiences.

        Phase 4.5: The SystemLoop calls this to complete the
        Execution → Experience → FeedbackLoop chain. Without this,
        experiences are buffered in _experience_log only.
        """
        self._feedback_loop = feedback_loop

    # ═══════════════════════════════════════════════════════════════════
    # Strategy Registration
    # ═══════════════════════════════════════════════════════════════════

    def register_strategy(self, name: str, handler: StrategyHandler) -> None:
        """
        Register an execution strategy handler.

        This is how the Runtime learns about execution strategies WITHOUT
        hardcoding capability-specific logic. Strategies are registered
        at bootstrap time and selected at runtime based on the Capability's
        implementation strategy field.

        Args:
            name: strategy name (matches Implementation.strategy)
            handler: callable that executes the strategy
        """
        self._strategy_handlers[name.lower()] = handler

    def list_strategies(self) -> list[str]:
        """List all registered strategy names."""
        return list(self._strategy_handlers.keys())

    def set_legacy_executor(self, executor: Any) -> None:
        """
        Set a legacy CapabilityExecutor for fallback.

        Used ONLY when no capability matches the observation. The legacy
        path is temporary — it will be removed once all capabilities are
        registered in the new system.
        """
        self._legacy_executor = executor

    # ═══════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════

    def execute(
        self,
        observation: DocumentObservation,
        content: str = "",
        document_id: str = "",
        slice_id: str = "",
    ) -> ExecutionResult:
        """
        Execute capabilities against a document observation.

        This is THE unified entry point. It replaces execute_chapter(),
        execute_doc_class(), execute_handler(), and all other entry points.

        Flow:
            1. Match observation against all active capabilities
            2. Select best candidate (or fallback)
            3. Resolve execution strategy from Capability + Implementation
            4. Execute strategy (delegated to handler)
            5. Generate ExecutionExperience
            6. Return unified ExecutionResult

        Args:
            observation: DocumentObservation describing content structure
            content: full text content (if not already in observation)
            document_id: source document (traceability only)
            slice_id: source slice (traceability only)

        Returns:
            ExecutionResult wrapping match + capability result + experience
        """
        start_time = time.time()
        diagnostics: list[str] = []

        # Resolve content and IDs
        content = content or observation.content_snippet
        doc_id = document_id or observation.document_id
        slice_id = slice_id or observation.slice_id

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Match observation against all capabilities
        # ═══════════════════════════════════════════════════════════
        match_result = self.matcher.match(observation)
        diagnostics.append(
            f"Matched against {match_result.total_capabilities_considered} "
            f"active capabilities, best_score={match_result.best_score:.4f}"
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Select best candidate or fallback
        # ═══════════════════════════════════════════════════════════
        best_candidate = match_result.top_candidate()

        if best_candidate is None or best_candidate.score < self.config.min_match_score:
            # No capability matches — fallback or return uncertain result
            diagnostics.append(
                "No capability scored above threshold — "
                f"best_score={match_result.best_score:.4f} < "
                f"threshold={self.config.min_match_score}"
            )
            return self._handle_no_match(
                observation, content, match_result, doc_id, slice_id,
                start_time, diagnostics,
            )

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Get Capability from Registry
        # ═══════════════════════════════════════════════════════════
        cap = self.registry.get(best_candidate.capability_id)
        if cap is None:
            diagnostics.append(
                f"Capability '{best_candidate.capability_id}' not in registry"
            )
            return self._handle_no_match(
                observation, content, match_result, doc_id, slice_id,
                start_time, diagnostics,
            )

        if not cap.is_active():
            diagnostics.append(
                f"Capability '{cap.id}' is {cap.status.value}, not active"
            )
            return self._handle_no_match(
                observation, content, match_result, doc_id, slice_id,
                start_time, diagnostics,
            )

        confidence_before = cap.cross_doc_success_rate

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Resolve and execute strategy
        # ═══════════════════════════════════════════════════════════
        capability_result = self._execute_capability(
            cap, content, doc_id, slice_id, diagnostics,
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Update Capability stats in Registry
        # ═══════════════════════════════════════════════════════════
        cap.record_execution(capability_result.is_success, doc_id)

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Generate ExecutionExperience
        # ═══════════════════════════════════════════════════════════
        execution_time_ms = (time.time() - start_time) * 1000

        experience = None
        if self.config.enable_experience_generation:
            experience = ExecutionExperience.from_execution(
                capability_id=cap.id,
                capability_name=cap.name,
                observation_id=observation.id,
                observation_summary=observation.to_summary(),
                match_result=match_result,
                capability_result=capability_result,
                execution_strategy_used=capability_result.implementation_version or "unknown",
                execution_time_ms=execution_time_ms,
                document_id=doc_id,
                slice_id=slice_id,
                confidence_before=confidence_before,
            )
            self._experience_log.append(experience)

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Return unified ExecutionResult
        # ═══════════════════════════════════════════════════════════
        diagnostics.append(
            f"Execution complete: success={capability_result.is_success}, "
            f"confidence={capability_result.confidence:.4f}, "
            f"evidence_count={capability_result.evidence_count}"
        )

        return ExecutionResult(
            observation_id=observation.id,
            document_id=doc_id,
            slice_id=slice_id,
            match_result=match_result,
            capability_result=capability_result,
            experience=experience,
            success=capability_result.is_success,
            diagnostics=diagnostics,
            execution_time_ms=execution_time_ms,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Strategy Execution
    # ═══════════════════════════════════════════════════════════════════

    def _execute_capability(
        self,
        cap: Capability,
        content: str,
        document_id: str,
        slice_id: str,
        diagnostics: list[str],
    ) -> CapabilityResult:
        """
        Execute a Capability by resolving its implementation strategy.

        The Runtime does NOT know what each strategy does — it only
        knows that strategies exist and how to dispatch to them.

        Strategy resolution order:
        1. Look at cap.execution_strategy (declarative description)
        2. Select the best Implementation for the content
        3. Dispatch to registered strategy handler
        4. If no handler registered, create a generic result
        """
        # Select the best implementation for this content
        impl = self._select_implementation(cap, content)

        if impl is None:
            return self._make_result(
                cap=cap,
                success=False,
                document_id=document_id,
                slice_id=slice_id,
                diagnosis=f"No implementation found for capability '{cap.name}'",
                errors=[f"No implementation for '{cap.id}'"],
            )

        strategy_name = impl.strategy.lower().strip()
        diagnostics.append(
            f"Selected strategy '{strategy_name}' via implementation '{impl.name}'"
        )

        # Check if we have a registered handler for this strategy
        handler = self._strategy_handlers.get(strategy_name)
        if handler is not None:
            # Delegate to registered strategy handler
            context = {
                "document_id": document_id,
                "slice_id": slice_id,
                "diagnostics": diagnostics,
            }
            try:
                result = handler(content, cap, impl, context)
                result.capability_id = cap.id
                result.capability_name = cap.name
                result.implementation_version = f"{impl.name} v{impl.version}"
                result.document_id = document_id
                result.slice_id = slice_id
                return result
            except Exception as e:
                diagnostics.append(f"Strategy handler error: {e}")
                return self._make_result(
                    cap=cap,
                    success=False,
                    document_id=document_id,
                    slice_id=slice_id,
                    diagnosis=f"Strategy '{strategy_name}' execution failed: {e}",
                    errors=[str(e)],
                )

        # No handler registered — generic extraction attempt
        diagnostics.append(
            f"No handler registered for strategy '{strategy_name}' — "
            f"using generic extraction"
        )
        return self._execute_generic(cap, impl, content, document_id, slice_id)

    # ═══════════════════════════════════════════════════════════════════
    # Implementation Selection
    # ═══════════════════════════════════════════════════════════════════

    def _select_implementation(
        self, cap: Capability, content: str
    ) -> Optional[Implementation]:
        """
        Select the best Implementation for the content.

        Strategy is selected based on the Capability's own Implementation
        objects — the Runtime has no opinion about which strategy is
        better for which content type.
        """
        # Use the Registry to get implementations
        impls = self.registry.get_implementations(cap)
        if not impls:
            # Fallback: create a synthetic implementation from capability
            return Implementation(
                id=f"IMPL-{cap.id}-DEFAULT",
                capability_id=cap.id,
                name=f"{cap.name} Default",
                strategy=cap.execution_strategy or "generic",
                version=cap.version,
            )

        if len(impls) == 1:
            return impls[0]

        # Score each implementation's fit against the content
        # (based on content characteristics, NOT doc_class)
        scored = []
        for impl in impls:
            fit_score = self._score_implementation_content_fit(impl, cap, content)
            scored.append((fit_score, impl))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _score_implementation_content_fit(
        self, impl: Implementation, cap: Capability, content: str
    ) -> float:
        """
        Score implementation fit against content characteristics.

        CRITICAL: Does NOT know about strategy names ("anchor", "density").
        Instead reads content_signal requirements from impl.config. The
        Capability/Implementation describes what signals matter; the
        Runtime computes them generically.

        Supported signals (defined in impl.config["content_signals"]):
        - "vocabulary_presence": counts vocabulary terms from cap.scope
        - "numeric_density": ratio of numbers to total words
        - "line_count": number of non-empty lines
        """
        import re
        score = 0.5

        # Read which content signals this implementation cares about
        signal_specs = impl.config.get("content_signals", [])
        if not signal_specs:
            return score  # No signals configured → neutral score

        for spec in signal_specs:
            signal_name = spec if isinstance(spec, str) else spec.get("name", "")
            threshold = spec.get("threshold", 0.5) if isinstance(spec, dict) else 0.5
            weight = spec.get("weight", 0.25) if isinstance(spec, dict) else 0.25

            signal_value = 0.0

            if signal_name == "vocabulary_presence":
                signal_value = self._compute_vocabulary_presence(cap, content)
                # Normalize: >5 terms = 1.0, >3 = 0.6, >0 = 0.2
                if signal_value >= 5:
                    signal_value = 1.0
                elif signal_value >= 3:
                    signal_value = 0.6
                elif signal_value > 0:
                    signal_value = 0.2

            elif signal_name == "numeric_density":
                words = content.split()
                if words:
                    numbers = len(re.findall(r'\d+(?:\.\d+)?', content))
                    signal_value = numbers / len(words)
                    # Normalize: density above threshold → bonus
                    if signal_value >= threshold * 2:
                        signal_value = 1.0
                    elif signal_value >= threshold:
                        signal_value = 0.5

            elif signal_name == "line_count":
                lines = [l for l in content.split('\n') if l.strip()]
                signal_value = float(len(lines))
                if signal_value >= threshold * 2:
                    signal_value = 1.0
                elif signal_value >= threshold:
                    signal_value = 0.5

            score += weight * signal_value

        return min(1.0, score)

    def _compute_vocabulary_presence(
        self, cap: Capability, content: str
    ) -> float:
        """Count how many vocabulary terms appear in content."""
        vocab = cap.scope.get("vocabulary", {})
        if not vocab:
            return 0.0
        content_lower = content.lower()
        count = 0
        for terms in vocab.values():
            for term in terms:
                if term.lower() in content_lower:
                    count += 1
        return float(count)

    # ═══════════════════════════════════════════════════════════════════
    # Generic Execution (fallback when no strategy handler)
    # ═══════════════════════════════════════════════════════════════════

    def _execute_generic(
        self,
        cap: Capability,
        impl: Implementation,
        content: str,
        document_id: str,
        slice_id: str,
    ) -> CapabilityResult:
        """Generic execution when no strategy handler is registered."""
        import re

        result = CapabilityResult(
            capability_id=cap.id,
            capability_name=cap.name,
            implementation_version=f"{impl.name} v{impl.version}",
            document_id=document_id,
            slice_id=slice_id,
            diagnosis=f"Generic execution via '{impl.strategy}' strategy",
        )

        # Attempt basic pattern-based extraction
        pattern_ids = cap.pattern_ids
        if pattern_ids:
            result.pattern_ids_used = pattern_ids

        # Look for evidence requirements
        evidence_reqs = cap.evidence_requirements or {}
        min_matches = evidence_reqs.get("min_pattern_matches", 1)

        # Extract from content using vocabulary if present
        vocab = cap.scope.get("vocabulary", {})
        if vocab:
            content_lower = content.lower()
            for category, terms in vocab.items():
                for term in terms:
                    if term.lower() in content_lower:
                        result.add_evidence(EvidenceItem(
                            id=f"EVD-GEN-{len(result.evidence)}",
                            evidence_type="term_matched",
                            description=f"Found '{term}' ({category})",
                            confidence=0.5,
                            match_type="exact",
                        ))

        # Compute confidence
        if result.evidence_count >= min_matches:
            result.confidence = min(0.5, result.evidence_count * 0.1)
            result.is_success = True
        else:
            result.confidence = 0.1
            result.is_success = False
            result.add_error(
                f"Insufficient evidence: {result.evidence_count} < {min_matches}"
            )

        return result

    # ═══════════════════════════════════════════════════════════════════
    # No-Match Handling
    # ═══════════════════════════════════════════════════════════════════

    def _handle_no_match(
        self,
        observation: DocumentObservation,
        content: str,
        match_result: MatchResult,
        document_id: str,
        slice_id: str,
        start_time: float,
        diagnostics: list[str],
    ) -> ExecutionResult:
        """
        Handle case where no capability matched the observation.

        Produces:
        - An ExecutionResult with success=False
        - An ExecutionExperience recording the non-match
        - Optionally, a fallback through the legacy executor
        """
        execution_time_ms = (time.time() - start_time) * 1000

        # Try legacy fallback
        capability_result = None
        if self.config.fallback_to_legacy and self._legacy_executor:
            # Use the best candidate's capability_id if available,
            # otherwise use the configurable default
            legacy_cap_id = (
                match_result.best_capability_id
                or getattr(self.config, "legacy_fallback_capability_id", "")
            )
            if legacy_cap_id:
                diagnostics.append(f"Attempting legacy fallback via '{legacy_cap_id}'...")
                try:
                    capability_result = self._legacy_executor.execute_chapter(
                        capability_id=legacy_cap_id,
                        content=content,
                        document_id=document_id,
                        slice_id=slice_id,
                    )
                    diagnostics.append(f"Legacy fallback succeeded")
                except Exception as e:
                    diagnostics.append(f"Legacy fallback failed: {e}")
            else:
                diagnostics.append("No legacy capability_id available — skipping fallback")

        # Generate experience for the non-match
        experience = None
        if self.config.enable_experience_generation:
            # Create a minimal experience recording the non-match
            experience = ExecutionExperience(
                id=f"EXP-NOMATCH-{document_id}-{slice_id}",
                capability_id="unknown",
                capability_name="Unknown",
                observation_id=observation.id,
                observation_summary=observation.to_summary(),
                input_evidence={
                    "matched_patterns": [],
                    "matched_element_types": [],
                    "match_score": 0.0,
                },
                execution_strategy_used="none",
                result_summary={
                    "matched": False,
                    "best_candidate_score": round(match_result.best_score, 4),
                    "capabilities_considered": match_result.total_capabilities_considered,
                },
                success=False,
                failure_reason=(
                    f"No capability scored above threshold "
                    f"({match_result.best_score:.4f} < {self.config.min_match_score})"
                ),
                validation={
                    "gates_passed": 0,
                    "total_gates": 3,
                    "warnings": [],
                    "errors": ["no_capability_match"],
                },
                confidence_before=0.0,
                confidence_after=0.0,
                confidence_delta=0.0,
                execution_time_ms=execution_time_ms,
                document_id=document_id,
                slice_id=slice_id,
            )
            self._experience_log.append(experience)

        return ExecutionResult(
            observation_id=observation.id,
            document_id=document_id,
            slice_id=slice_id,
            match_result=match_result,
            capability_result=capability_result,
            experience=experience,
            success=False,
            diagnostics=diagnostics,
            execution_time_ms=execution_time_ms,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════

    def _make_result(
        self,
        cap: Capability,
        success: bool,
        document_id: str,
        slice_id: str,
        diagnosis: str = "",
        errors: list[str] = None,
    ) -> CapabilityResult:
        """Create a CapabilityResult with minimal fields."""
        result = CapabilityResult(
            capability_id=cap.id,
            capability_name=cap.name,
            document_id=document_id,
            slice_id=slice_id,
            is_success=success,
            diagnosis=diagnosis or ("Success" if success else "Failed"),
            pattern_ids_used=cap.pattern_ids,
        )
        if errors:
            for e in errors:
                result.add_error(e)
        return result

    def get_experience_log(self) -> list[ExecutionExperience]:
        """Return all experiences generated since runtime creation."""
        return list(self._experience_log)

    def clear_experience_log(self) -> None:
        """Clear the in-memory experience buffer."""
        self._experience_log.clear()


# ═══════════════════════════════════════════════════════════════════════════
# Pre-built Strategy Handlers
# ═══════════════════════════════════════════════════════════════════════════


def make_anchor_split_handler(
    legacy_executor: Any = None,
) -> StrategyHandler:
    """
    Create an anchor-split strategy handler.

    Uses legacy executor's internal methods if available, otherwise
    does basic anchor-based extraction.
    """
    def handler(
        content: str,
        cap: Capability,
        impl: Implementation,
        context: dict[str, Any],
    ) -> CapabilityResult:
        document_id = context.get("document_id", "")
        slice_id = context.get("slice_id", "")

        # If legacy executor is available, delegate
        if legacy_executor:
            return legacy_executor.execute_chapter(
                capability_id=cap.id,
                content=content,
                document_id=document_id,
                slice_id=slice_id,
            )

        # Basic anchor extraction
        result = CapabilityResult(
            capability_id=cap.id,
            capability_name=cap.name,
            implementation_version=f"{impl.name} v{impl.version}",
            document_id=document_id,
            slice_id=slice_id,
            diagnosis=f"Basic anchor-split via '{impl.strategy}'",
            pattern_ids_used=cap.pattern_ids,
        )

        import re
        vocab = cap.scope.get("vocabulary", {})
        if not vocab:
            result.add_error("No vocabulary in capability scope")
            result.is_success = False
            return result

        content_lower = content.lower()
        for category, terms in vocab.items():
            for term in terms:
                if term.lower() in content_lower:
                    result.add_evidence(EvidenceItem(
                        id=f"EVD-ANC-{len(result.evidence)}",
                        evidence_type="anchor_matched",
                        description=f"Anchor '{term}' found ({category})",
                        confidence=0.6,
                        match_type="exact",
                    ))

        result.confidence = min(0.7, result.evidence_count * 0.1)
        result.is_success = result.evidence_count > 0
        return result

    return handler


def make_generic_extraction_handler() -> StrategyHandler:
    """Create a generic extraction strategy handler."""
    def handler(
        content: str,
        cap: Capability,
        impl: Implementation,
        context: dict[str, Any],
    ) -> CapabilityResult:
        document_id = context.get("document_id", "")
        slice_id = context.get("slice_id", "")

        result = CapabilityResult(
            capability_id=cap.id,
            capability_name=cap.name,
            implementation_version=f"{impl.name} v{impl.version}",
            document_id=document_id,
            slice_id=slice_id,
            diagnosis=f"Generic extraction via '{impl.strategy}'",
            pattern_ids_used=cap.pattern_ids,
        )

        # Just record that we attempted
        result.confidence = 0.3
        result.is_success = True
        result.add_evidence(EvidenceItem(
            id=f"EVD-GEN-001",
            evidence_type="generic_execution",
            description=f"Generic execution for '{cap.name}' — no specialized handler",
            confidence=0.3,
            match_type="inferred",
        ))

        return result

    return handler
