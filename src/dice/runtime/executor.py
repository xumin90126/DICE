"""
CapabilityExecutor — the core runtime engine.

Phase 3.0: Three-Layer Unified Execution Chain.
    Document → L1 Structure Detection → L2 Semantic Evidence → L3 Structure Extraction

Executes a registered Capability against document content WITHOUT any
doc_class parameter. The entire flow is driven by:
    1. L1: Structure detection (does content have the target structure?)
    2. L2: Semantic evidence (vocabulary enhancement, boosts confidence only)
    3. L3: Structure extraction (quantity-anchor-based, vocabulary-independent)

Strategy routing:
    Case A: L1✓ + L2 sufficient  → L2-enhanced semantic extraction
    Case B: L1✓ + L2 insufficient → pure L3 structural extraction
    Case C: L1✗ → reject/uncertain

CRITICAL CONSTRAINT: execute_chapter() does NOT accept doc_class.
The Capability determines applicability through structure detection, not
through document type taxonomy.
"""

from __future__ import annotations

import re
import time
from typing import Any, Optional

from dice.graph.experience_graph import ExperienceGraph
from dice.graph.nodes import Capability, Implementation, Rule, Pattern
from dice.runtime.result import CapabilityResult, EvidenceItem
from dice.runtime.selector import CapabilitySelector
from dice.runtime.layers import ThreeLayerRuntime, LayerTrace
from dice.models import SourceRef


class CapabilityExecutor:
    """
    Executes a Capability against document content.

    Phase 3.0: Uses ThreeLayerRuntime for CAP-COMP-TABLE.
    Phase 2 legacy path retained for other capabilities.

    Usage:
        graph = ExperienceGraph(...)  # pre-loaded with registered capabilities
        executor = CapabilityExecutor(graph)
        result = executor.execute_chapter(
            capability_id="CAP-COMP-TABLE",
            content=section_text,
            document_id="DC201-C1",
            slice_id="04_components",
        )
    """

    def __init__(
        self,
        graph: ExperienceGraph,
        feedback_loop: Optional[Any] = None,   # FeedbackLoop (Phase 4.3)
    ):
        self.graph = graph
        self.selector = CapabilitySelector(graph)
        self._layer_runtime: Optional[ThreeLayerRuntime] = None
        self._feedback_loop = feedback_loop
        self._ranking_model: Optional[Any] = None  # RankingModel, set via set_ranking_model()

    def _get_layer_runtime(self) -> ThreeLayerRuntime:
        """Lazy-initialize the three-layer runtime with vocabulary from graph."""
        if self._layer_runtime is None:
            vocabulary = {}
            cap = self.graph.capabilities.get("CAP-COMP-TABLE")
            if cap and "vocabulary" in cap.scope:
                vocabulary = cap.scope["vocabulary"]
            self._layer_runtime = ThreeLayerRuntime(vocabulary=vocabulary)
        return self._layer_runtime

    def set_ranking_model(self, model: Any) -> None:
        """Set the RankingModel for confidence tracking (Phase 4.3)."""
        self._ranking_model = model

    # ═══════════════════════════════════════════════════════════════
    # MAIN ENTRY POINTS
    # ═══════════════════════════════════════════════════════════════

    def execute_chapter(
        self,
        capability_id: str,
        content: str,
        document_id: str = "",
        slice_id: str = "",
    ) -> CapabilityResult:
        """
        Execute a Capability against chapter content.

        NO doc_class parameter. The Capability determines applicability
        through pattern matching on the content itself.

        Phase 3.0: For CAP-COMP-TABLE, uses three-layer runtime (L1→L2→L3).
        Other capabilities use the Phase 2 legacy path.

        Phase 4.3: If feedback_loop is configured, automatically records
        feedback after execution via _record_feedback().

        Args:
            capability_id: Which capability to execute (e.g. "CAP-COMP-TABLE")
            content: The text content to analyze
            document_id: Source document identifier (for traceability)
            slice_id: Source slice identifier (for traceability)

        Returns:
            CapabilityResult with extracted data, evidence, layer analysis, and diagnosis.
        """
        # Phase 3.0: Three-layer path for CAP-COMP-TABLE
        if capability_id == "CAP-COMP-TABLE":
            result = self._execute_three_layer(capability_id, content, document_id, slice_id)
        else:
            # Phase 2: Legacy path for other capabilities
            result = self._execute_legacy(capability_id, content, document_id, slice_id)

        # Phase 4.3: Record feedback (if loop is configured)
        self._record_feedback(result, capability_id, document_id, slice_id)

        return result

    # ═══════════════════════════════════════════════════════════════
    # PHASE 3.0: THREE-LAYER EXECUTION (CAP-COMP-TABLE)
    # ═══════════════════════════════════════════════════════════════

    def _execute_three_layer(
        self,
        capability_id: str,
        content: str,
        document_id: str,
        slice_id: str,
    ) -> CapabilityResult:
        """Execute using ThreeLayerRuntime: L1 → L2 → L3."""
        start_time = time.time()

        cap = self.graph.capabilities.get(capability_id)
        if cap is None:
            return self._error_result(
                capability_id, f"Capability '{capability_id}' not found"
            )

        # Re-initialize runtime to pick up latest vocabulary
        self._layer_runtime = None
        runtime = self._get_layer_runtime()

        # Execute three-layer chain
        trace = runtime.execute(content, document_id, slice_id)

        # Build CapabilityResult from trace
        result_dict = ThreeLayerRuntime.trace_to_capability_result(
            trace,
            capability_id=capability_id,
            capability_name=cap.name,
            implementation_version="3.0",
        )

        # Convert to CapabilityResult dataclass
        result = CapabilityResult(
            capability_id=result_dict["capability_id"],
            capability_name=result_dict["capability_name"],
            implementation_version=result_dict["implementation_version"],
            result=result_dict["result"],
            confidence=result_dict["confidence"],
            confidence_breakdown=result_dict["confidence_breakdown"],
            reasoning_layer=result_dict["reasoning_layer"],
            strategy_case=result_dict["strategy_case"],
            layer_contributions=result_dict["layer_contributions"],
            diagnosis=result_dict["diagnosis"],
            document_id=document_id,
            slice_id=slice_id,
            is_success=result_dict["is_success"],
            warnings=result_dict.get("warnings", []),
            errors=result_dict.get("errors", []),
            pattern_ids_used=cap.pattern_ids,
            pattern_match_details={
                pid: {"matched": True, "score": trace.l1_result.score}
                for pid in cap.pattern_ids
            },
        )

        result.execution_time_ms = (time.time() - start_time) * 1000

        # Add evidence items from extracted components
        for i, comp in enumerate(trace.components):
            result.add_evidence(EvidenceItem(
                id=f"EVD-COMP-{document_id}-{i+1:03d}",
                evidence_type="component_extracted",
                description=f"L3 extracted: {comp.get('name', '?')} = {comp.get('quantity', '?')} {comp.get('unit', '?')}",
                source=SourceRef(
                    source_document=document_id,
                    source_slice=slice_id,
                ) if document_id else None,
                content_snippet=content[max(0, comp.get('source_position', 0) - 30):comp.get('source_position', 0) + 80],
                extraction=comp,
                confidence=round(trace.extraction_quality, 4),
                match_type="structural" if trace.strategy_case == "B" else "semantic",
            ))

        return result

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: LEGACY EXECUTION (for non-CAP-COMP-TABLE capabilities)
    # ═══════════════════════════════════════════════════════════════

    def _execute_legacy(
        self,
        capability_id: str,
        content: str,
        document_id: str,
        slice_id: str,
    ) -> CapabilityResult:
        """Phase 2 legacy execution path."""
        start_time = time.time()

        cap = self.graph.capabilities.get(capability_id)
        if cap is None:
            return self._error_result(
                capability_id, f"Capability '{capability_id}' not found"
            )

        # 1. Select & verify
        selection = self.selector.select(capability_id, content)
        if selection.confidence < 0.1:
            return CapabilityResult(
                capability_id=capability_id,
                capability_name=cap.name,
                result={"matched": False},
                confidence=selection.confidence,
                diagnosis=(
                    f"Content does not match capability '{cap.name}' patterns. "
                    f"Matched {len(selection.matched_patterns)}/{len(cap.pattern_ids)} patterns. "
                    f"Reasons: {'; '.join(selection.reasons)}"
                ),
                pattern_ids_used=selection.matched_patterns,
                document_id=document_id,
                slice_id=slice_id,
            )

        # 2. Select implementation
        impl = self._select_implementation(cap, content)
        if impl is None:
            return self._error_result(
                capability_id,
                f"No suitable implementation found for content patterns"
            )

        # 3. Execute
        result = CapabilityResult(
            capability_id=cap.id,
            capability_name=cap.name,
            implementation_version=f"{impl.id} v{impl.version}",
            pattern_ids_used=selection.matched_patterns,
            pattern_match_details={
                pid: {"matched": pid in selection.matched_patterns}
                for pid in cap.pattern_ids
            },
            document_id=document_id,
            slice_id=slice_id,
        )

        try:
            extracted, evidence = self._execute_implementation(impl, content, document_id, slice_id)
            result.result = extracted
            for ev in evidence:
                result.add_evidence(ev)
            result.confidence_breakdown = {
                "pattern_match": selection.confidence,
                "extraction_quality": self._extraction_quality(evidence),
                "completeness": self._completeness_score(extracted),
            }
            result.confidence = (
                result.confidence_breakdown["pattern_match"] * 0.3
                + result.confidence_breakdown["extraction_quality"] * 0.4
                + result.confidence_breakdown["completeness"] * 0.3
            )
            result.diagnosis = self._build_diagnosis(result, cap, impl)
        except Exception as e:
            result.add_error(f"Execution error: {e}")
            result.is_success = False
            result.diagnosis = f"Execution failed: {e}"

        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    # ═══════════════════════════════════════════════════════════════
    # IMPLEMENTATION SELECTION — based on CONTENT, not doc_class
    # ═══════════════════════════════════════════════════════════════

    def _select_implementation(
        self, cap: Capability, content: str
    ) -> Optional[Implementation]:
        """
        Select the best implementation strategy based on CONTENT characteristics.

        This is the KEY design point: we analyze the CONTENT to determine
        which strategy to use, NOT which doc_class the document belongs to.

        For ComponentsTableUnderstanding:
        - If content shows table collapse patterns → use anchor_split strategy
        - If content shows high vocabulary density → use density strategy
        """
        impls = self.graph.get_implementations_for_capability(cap.id)
        if not impls:
            return None

        if len(impls) == 1:
            return impls[0]

        # Score each implementation against content
        scored = []
        for impl in impls:
            score = self._score_implementation_fit(impl, content)
            scored.append((score, impl))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _score_implementation_fit(
        self, impl: Implementation, content: str
    ) -> float:
        """Score how well an implementation fits the content."""
        score = 0.5  # base

        strategy = impl.strategy.lower()
        config = impl.config

        # Anchor strategy: check for table collapse signs
        if "anchor" in strategy:
            # Count potential anchors (component names from vocabulary)
            anchor_count = self._count_vocabulary_matches(content)
            if anchor_count >= 5:
                score += 0.3
            elif anchor_count >= 3:
                score += 0.15

            # Check for text collapse indicators
            if self._has_table_collapse_indicators(content):
                score += 0.2

        # Density strategy: check vocabulary density
        if "density" in strategy:
            density = self._compute_vocabulary_density(content)
            threshold = config.get("density_threshold", 0.3)
            if density > threshold * 1.5:
                score += 0.3
            elif density > threshold:
                score += 0.15

        return min(1.0, score)

    # ═══════════════════════════════════════════════════════════════
    # EXECUTION
    # ═══════════════════════════════════════════════════════════════

    def _execute_implementation(
        self,
        impl: Implementation,
        content: str,
        document_id: str,
        slice_id: str,
    ) -> tuple[dict[str, Any], list[EvidenceItem]]:
        """
        Execute the selected implementation strategy.

        Returns (extracted_data, evidence_items).
        """
        strategy = impl.strategy.lower()
        cap = self.graph.capabilities.get(impl.capability_id)
        vocab = cap.scope.get("vocabulary", {}) if cap else {}
        quantity_patterns = cap.scope.get("quantity_patterns", []) if cap else []

        if "anchor" in strategy:
            return self._execute_anchor_strategy(content, vocab, quantity_patterns, document_id, slice_id)
        elif "density" in strategy:
            return self._execute_density_strategy(content, vocab, quantity_patterns, document_id, slice_id)
        else:
            return {"components": [], "total_components": 0}, []

    def _execute_anchor_strategy(
        self,
        content: str,
        vocabulary: dict[str, list[str]],
        quantity_patterns: list[str],
        document_id: str,
        slice_id: str,
    ) -> tuple[dict[str, Any], list[EvidenceItem]]:
        """
        Anchor split strategy: use component vocabulary as anchors to
        split collapsed table text into individual component entries.
        """
        evidence_items = []
        components = []

        # Build flat anchor list with priorities
        all_anchors = []
        for category, terms in vocabulary.items():
            for term in terms:
                all_anchors.append((term, category))

        # Find anchor positions in content
        anchor_positions = []
        content_lower = content.lower()
        for term, category in all_anchors:
            term_lower = term.lower()
            pos = 0
            while True:
                idx = content_lower.find(term_lower, pos)
                if idx == -1:
                    break
                anchor_positions.append((idx, term, category))
                pos = idx + len(term)

        # Sort by position
        anchor_positions.sort(key=lambda x: x[0])

        # Deduplicate overlapping anchors (keep first at each position)
        deduped = []
        last_end = -100
        for idx, term, category in anchor_positions:
            if idx >= last_end:
                deduped.append((idx, term, category))
                last_end = idx + len(term)

        # Extract component entries between anchors
        for i, (start_pos, anchor_term, category) in enumerate(deduped):
            if i < len(deduped) - 1:
                segment = content[start_pos:deduped[i + 1][0]].strip()
            else:
                segment = content[start_pos:].strip()

            # Parse component entry
            comp = self._parse_component_entry(anchor_term, segment, quantity_patterns, category)
            components.append(comp)

            evidence_items.append(EvidenceItem(
                id=f"EVD-COMP-{document_id}-{len(components):03d}",
                evidence_type="component_identified",
                description=f"Identified component '{anchor_term}' via anchor matching (category: {category})",
                source=SourceRef(
                    source_document=document_id,
                    source_slice=slice_id,
                ),
                content_snippet=segment[:200],
                extraction=comp,
                confidence=0.8,
                match_type="exact",
            ))

        # Check for missing anchors (components not detected)
        missing = self._detect_missing_components(content, vocabulary, deduped)

        return {
            "components": components,
            "total_components": len(components),
            "covered_components": len(components),
            "missing_count": len(missing),
            "missing_hints": missing[:5],
            "coverage_ratio": 1.0 if len(deduped) == 0 else len(components) / len(deduped),
            "strategy_used": "anchor_split",
            "anchor_count": len(deduped),
        }, evidence_items

    def _execute_density_strategy(
        self,
        content: str,
        vocabulary: dict[str, list[str]],
        quantity_patterns: list[str],
        document_id: str,
        slice_id: str,
    ) -> tuple[dict[str, Any], list[EvidenceItem]]:
        """
        Density strategy: line-by-line extraction based on vocabulary density.
        """
        evidence_items = []
        components = []

        # Split into lines/segments
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        # Merge short lines with neighbors (table cell fragments)
        segments = self._merge_short_lines(lines)

        for i, segment in enumerate(segments):
            comp = self._extract_component_from_segment(segment, vocabulary, quantity_patterns)
            if comp and comp.get("name"):
                components.append(comp)
                evidence_items.append(EvidenceItem(
                    id=f"EVD-COMP-{document_id}-{len(components):03d}",
                    evidence_type="component_identified",
                    description=f"Extracted component '{comp['name']}' via density scanning",
                    source=SourceRef(
                        source_document=document_id,
                        source_slice=slice_id,
                    ),
                    content_snippet=segment[:200],
                    extraction=comp,
                    confidence=0.6,
                    match_type="fuzzy",
                ))

        return {
            "components": components,
            "total_components": len(components),
            "covered_components": len(components),
            "missing_count": 0,
            "missing_hints": [],
            "coverage_ratio": 1.0,
            "strategy_used": "density_scan",
            "segments_processed": len(segments),
        }, evidence_items

    # ═══════════════════════════════════════════════════════════════
    # PARSING HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _parse_component_entry(
        self,
        name: str,
        segment: str,
        quantity_patterns: list[str],
        category: str = "",
    ) -> dict[str, Any]:
        """Parse a single component entry from an anchor-bounded segment."""
        comp = {
            "name": name,
            "category": category,
            "quantity": "",
            "unit": "",
            "catalog_number": "",
            "function": "",
        }

        # Extract quantity
        for pat in quantity_patterns:
            m = re.search(pat, segment, re.IGNORECASE)
            if m:
                groups = m.groups()
                if len(groups) >= 2:
                    try:
                        num = float(groups[0])
                        unit = groups[1] if len(groups) > 1 else ""
                        comp["quantity"] = str(num)
                        comp["unit"] = unit
                    except ValueError:
                        comp["quantity"] = groups[0]
                elif len(groups) == 1:
                    comp["quantity"] = groups[0]
                break

        # Extract catalog number (alphanumeric pattern, 6-15 chars)
        cat_match = re.search(r'\b([A-Z]{2,4}\d{4,8}|\d{6,12})\b', segment)
        if cat_match:
            comp["catalog_number"] = cat_match.group(0)

        return comp

    def _extract_component_from_segment(
        self,
        segment: str,
        vocabulary: dict[str, list[str]],
        quantity_patterns: list[str],
    ) -> Optional[dict[str, Any]]:
        """Extract a component from a text segment using vocabulary matching."""
        # Try to find a known component name in the segment
        segment_lower = segment.lower()
        best_match = None
        best_len = 0

        for category, terms in vocabulary.items():
            for term in terms:
                term_lower = term.lower()
                if term_lower in segment_lower and len(term) > best_len:
                    best_match = (term, category)
                    best_len = len(term)

        if best_match is None:
            return None

        name, category = best_match
        return self._parse_component_entry(name, segment, quantity_patterns, category)

    def _merge_short_lines(self, lines: list[str], min_len: int = 20) -> list[str]:
        """Merge short lines (table cell fragments) with neighbors."""
        if not lines:
            return []
        merged = []
        buffer = ""
        for line in lines:
            if len(line) < min_len and buffer:
                buffer += " " + line
            elif len(line) < min_len:
                buffer = line
            else:
                if buffer:
                    merged.append(buffer)
                    buffer = ""
                merged.append(line)
        if buffer:
            merged.append(buffer)
        return merged

    # ═══════════════════════════════════════════════════════════════
    # DETECTION / SCORING HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _count_vocabulary_matches(self, content: str) -> int:
        """Count how many vocabulary terms appear in content."""
        cap = self.graph.capabilities.get("CAP-COMP-TABLE")
        if not cap:
            return 0
        vocab = cap.scope.get("vocabulary", {})
        content_lower = content.lower()
        count = 0
        for terms in vocab.values():
            for term in terms:
                if term.lower() in content_lower:
                    count += 1
        return count

    def _compute_vocabulary_density(self, content: str) -> float:
        """Compute the ratio of vocabulary words to total words."""
        words = content.split()
        if not words:
            return 0.0
        match_count = self._count_vocabulary_matches(content)
        return match_count / len(words)

    def _has_table_collapse_indicators(self, content: str) -> bool:
        """Check for signs of table text collapse."""
        indicators = [
            # Multiple component-like terms in close proximity
            self._count_vocabulary_matches(content) >= 3,
            # Quantity patterns present
            bool(re.search(r'\d+\s*(?:μL|mL|mg|μg|ng|g|L)', content)),
            # Catalog number patterns present
            bool(re.search(r'\b[A-Z]{2,4}\d{4,8}\b', content)),
            # Tab or multiple-space separators (column artifacts)
            bool(re.search(r'\t| {3,}', content)),
        ]
        return sum(indicators) >= 2

    def _detect_missing_components(
        self,
        content: str,
        vocabulary: dict[str, list[str]],
        found_anchors: list[tuple[int, str, str]],
    ) -> list[str]:
        """Detect vocabulary terms in content that weren't captured as anchors."""
        found_terms = {term.lower() for _, term, _ in found_anchors}
        missing = []
        content_lower = content.lower()
        for terms in vocabulary.values():
            for term in terms:
                term_lower = term.lower()
                if term_lower in content_lower and term_lower not in found_terms:
                    missing.append(term)
        return missing

    # ═══════════════════════════════════════════════════════════════
    # QUALITY METRICS
    # ═══════════════════════════════════════════════════════════════

    def _compute_confidence(
        self, evidence: list[EvidenceItem], pattern_score: float
    ) -> float:
        """Compute overall confidence from evidence and pattern match."""
        if not evidence:
            return pattern_score * 0.5
        avg_ev_confidence = sum(e.confidence for e in evidence) / len(evidence)
        return (pattern_score * 0.4 + avg_ev_confidence * 0.6)

    def _extraction_quality(self, evidence: list[EvidenceItem]) -> float:
        """Quality score based on extraction completeness."""
        if not evidence:
            return 0.0
        complete = sum(
            1 for e in evidence
            if e.extraction.get("quantity") and e.extraction.get("unit")
        )
        return complete / len(evidence)

    def _completeness_score(self, extracted: dict[str, Any]) -> float:
        """How complete is the extraction relative to what was found."""
        total = extracted.get("total_components", 0)
        missing = extracted.get("missing_count", 0)
        if total + missing == 0:
            return 0.0
        return total / (total + missing)

    def _build_diagnosis(
        self,
        result: CapabilityResult,
        cap: Capability,
        impl: Implementation,
    ) -> str:
        """Build human-readable diagnosis of the execution."""
        parts = [
            f"Capability '{cap.name}' executed using '{impl.name}' strategy.",
            f"Strategy: {impl.strategy[:120]}.",
            f"Patterns matched: {len(result.pattern_ids_used)}/{len(cap.pattern_ids)}.",
            f"Evidence collected: {result.evidence_count} items.",
        ]
        if "total_components" in result.result:
            parts.append(
                f"Components extracted: {result.result['total_components']}, "
                f"missing hints: {result.result.get('missing_count', 0)}."
            )
        if result.warnings:
            parts.append(f"Warnings: {'; '.join(result.warnings)}.")
        if result.errors:
            parts.append(f"Errors: {'; '.join(result.errors)}.")
        parts.append(f"Overall confidence: {result.confidence:.2f}.")
        return " ".join(parts)

    def _error_result(self, capability_id: str, message: str) -> CapabilityResult:
        return CapabilityResult(
            capability_id=capability_id,
            is_success=False,
            diagnosis=message,
            errors=[message],
        )

    # ═══════════════════════════════════════════════════════════════
    # PHASE 4.3: FEEDBACK LOOP INTEGRATION
    # ═══════════════════════════════════════════════════════════════

    def _record_feedback(
        self,
        result: CapabilityResult,
        capability_id: str,
        document_id: str,
        slice_id: str,
    ) -> None:
        """
        Record execution feedback via FeedbackLoop (Phase 4.3).

        Creates an ExecutionExperience from the CapabilityResult and feeds
        it to FeedbackLoop.process(). The FeedbackLoop then:
        1. Persists the experience
        2. Produces Evidence nodes
        3. Routes to EvidenceView (for Registry to consume)

        This is a NON-BLOCKING side effect — failures here don't affect
        the CapabilityResult returned to the caller.
        """
        if self._feedback_loop is None:
            return

        try:
            from dice.runtime.experience.execution_models import ExecutionExperience

            # Get pre-execution confidence from RankingModel if available
            confidence_before = 0.5  # neutral default
            cap = self.graph.capabilities.get(capability_id)
            if cap:
                # Use capability's cross_doc_success_rate as prior confidence
                if cap.execution_count > 0:
                    confidence_before = cap.cross_doc_success_rate
                else:
                    confidence_before = 0.5

            # Build observation summary for traceability
            observation_summary = {
                "content_length": len(getattr(result, 'result', {}).get('components', [])),
                "patterns_matched": len(result.pattern_ids_used),
                "evidence_count": result.evidence_count,
            }

            # Build input evidence from matched patterns
            input_evidence = {
                "matched_patterns": result.pattern_ids_used,
                "match_score": result.confidence,
            }

            cap_name = cap.name if cap else capability_id

            experience = ExecutionExperience.from_execution(
                capability_id=capability_id,
                capability_name=cap_name,
                observation_id=f"OBS-{document_id}-{slice_id}",
                observation_summary=observation_summary,
                match_result=None,  # MatchResult not available in direct execute_chapter path
                capability_result=result,
                execution_strategy_used=result.strategy_case or "legacy",
                execution_time_ms=result.execution_time_ms,
                document_id=document_id,
                slice_id=slice_id,
                confidence_before=confidence_before,
            )

            # Feed to FeedbackLoop (produces Evidence, routes to EvidenceView)
            self._feedback_loop.process(experience)

        except Exception:
            # Feedback recording is best-effort — never crash execution
            pass

    def has_feedback_loop(self) -> bool:
        """Check if FeedbackLoop is configured."""
        return self._feedback_loop is not None
