"""
CapabilitySelector — selects which Capability to apply for given content.

Phase 2: Manual selection (caller specifies capability_id).
Future: Automatic selection based on Document Observation → Pattern Match.

The selector interface decouples "which capability to use" from
"how to execute it", enabling future auto-selection without changing
the executor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from dice.graph.experience_graph import ExperienceGraph
from dice.graph.nodes import Capability, Pattern, PatternStatus


@dataclass
class SelectionResult:
    """Result of capability selection for a piece of content."""
    capability_id: str = ""
    capability_name: str = ""
    confidence: float = 0.0              # how well does this capability match
    matched_patterns: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)


@dataclass
class CapabilitySelector:
    """
    Selects capabilities for content analysis.

    Phase 2: Manual mode — caller provides capability_id directly.
    Future: Auto mode — scores all registered capabilities against content.
    """

    graph: ExperienceGraph

    def select(self, capability_id: str, content: Optional[str] = None) -> SelectionResult:
        """
        Select a capability by ID (manual mode).

        If content is provided, also performs a lightweight pattern match
        to verify the capability is applicable and compute confidence.
        """
        cap = self.graph.capabilities.get(capability_id)
        if cap is None:
            return SelectionResult(
                capability_id=capability_id,
                confidence=0.0,
                reasons=[f"Capability '{capability_id}' not found in graph"],
            )

        result = SelectionResult(
            capability_id=cap.id,
            capability_name=cap.name,
        )

        if content:
            # Lightweight pattern match — verify applicability
            match_result = self._match_patterns(cap, content)
            result.matched_patterns = match_result["matched"]
            result.confidence = match_result["score"]
            result.reasons = match_result["reasons"]

            if result.confidence < 0.2:
                result.alternatives = self._find_alternatives(content, exclude=capability_id)

        return result

    def _match_patterns(
        self, cap: Capability, content: str
    ) -> dict[str, Any]:
        """
        Lightweight pattern matching — check if content matches the
        capability's detection patterns.

        This is a simplified version for Phase 2. Future phases will
        have more sophisticated matching (embedding similarity, etc.).
        """
        matched = []
        total_score = 0.0
        reasons = []

        for pat_id in cap.pattern_ids:
            pat = self.graph.patterns.get(pat_id)
            if pat is None:
                continue

            pat_score = self._match_single_pattern(pat, content)
            if pat_score > 0.3:
                matched.append(pat_id)
                total_score += pat_score
                reasons.append(
                    f"Pattern '{pat.name}' matched (score={pat_score:.2f}): {pat.description[:80]}"
                )

        if matched:
            avg_score = total_score / len(matched)
        else:
            avg_score = 0.0
            reasons.append("No patterns matched above threshold")

        return {"matched": matched, "score": avg_score, "reasons": reasons}

    # ═══ Content signal detectors — evaluate actual content characteristics ═══

    def _get_vocabulary(self) -> dict[str, list[str]]:
        """Get component vocabulary from the registered capability."""
        cap = self.graph.capabilities.get("CAP-COMP-TABLE")
        if cap and "vocabulary" in cap.scope:
            return cap.scope["vocabulary"]
        return {}

    def _get_quantity_patterns(self) -> list[str]:
        """Get quantity regex patterns from the registered capability."""
        cap = self.graph.capabilities.get("CAP-COMP-TABLE")
        if cap and "quantity_patterns" in cap.scope:
            return cap.scope["quantity_patterns"]
        return []

    def _count_content_signals(self, content: str) -> dict[str, Any]:
        """
        Extract concrete content signals — vocabulary hits, quantity patterns,
        catalog numbers, table collapse artifacts.
        Returns counts and boolean indicators for each signal type.
        """
        import re
        content_lower = content.lower()
        signals = {}

        # 1. Component vocabulary hit count
        vocab = self._get_vocabulary()
        vocab_hits = 0
        for terms in vocab.values():
            for term in terms:
                if term.lower() in content_lower:
                    vocab_hits += 1
        signals["vocabulary_hits"] = vocab_hits

        # 2. Quantity/unit pattern matches
        qty_patterns = self._get_quantity_patterns()
        qty_matches = 0
        for pat in qty_patterns:
            qty_matches += len(re.findall(pat, content, re.IGNORECASE))
        signals["quantity_matches"] = qty_matches

        # 3. Catalog number pattern matches
        cat_pattern = r'\b([A-Z]{2,4}\d{4,8}|\d{6,12})\b'
        cat_matches = len(re.findall(cat_pattern, content))
        signals["catalog_matches"] = cat_matches

        # 4. Table collapse indicators
        tab_indicators = 0
        if re.search(r'\t| {4,}', content):            # column artifacts
            tab_indicators += 1
        if re.search(r'\d+\s*(?:×|x)\s*\d+', content): # "1 × 250 μL"
            tab_indicators += 1
        if re.search(r'\d+\s*(?:pcs|tubes|strips)', content_lower):
            tab_indicators += 1
        signals["table_collapse_indicators"] = tab_indicators

        # 5. Component name density
        words = content.split()
        if words:
            signals["vocabulary_density"] = vocab_hits / len(words)
        else:
            signals["vocabulary_density"] = 0.0

        # 6. Line count (multiple entries = component list)
        lines = [l for l in content.split('\n') if l.strip()]
        signals["line_count"] = len(lines)

        return signals

    def _match_single_pattern(self, pattern: Pattern, content: str) -> float:
        """
        Score how well a single pattern matches the content.

        Evaluates actual content STRUCTURAL characteristics (vocabulary hits,
        quantity patterns, table collapse artifacts) rather than naive keyword
        overlap on signal description text.
        """
        sig = self._count_content_signals(content)

        # ── PAT-COMP-TABLE-COLLAPSE: table collapse pattern ──
        if pattern.id == "PAT-COMP-TABLE-COLLAPSE":
            score = 0.0
            checks = 0

            # Signal: component vocabulary hits ≥ 3
            checks += 1
            if sig["vocabulary_hits"] >= 5:
                score += 1.0
            elif sig["vocabulary_hits"] >= 3:
                score += 0.6
            elif sig["vocabulary_hits"] >= 1:
                score += 0.2

            # Signal: quantity patterns present
            checks += 1
            if sig["quantity_matches"] >= 5:
                score += 1.0
            elif sig["quantity_matches"] >= 2:
                score += 0.6
            elif sig["quantity_matches"] >= 1:
                score += 0.3

            # Signal: catalog numbers present
            checks += 1
            if sig["catalog_matches"] >= 2:
                score += 1.0
            elif sig["catalog_matches"] >= 1:
                score += 0.5

            # Signal: table collapse indicators
            checks += 1
            if sig["table_collapse_indicators"] >= 2:
                score += 1.0
            elif sig["table_collapse_indicators"] >= 1:
                score += 0.5

            # Signal: vocabulary density > threshold
            checks += 1
            if sig["vocabulary_density"] > 0.08:
                score += 1.0
            elif sig["vocabulary_density"] > 0.04:
                score += 0.5
            elif sig["vocabulary_density"] > 0.02:
                score += 0.2

            return score / checks if checks > 0 else 0.0

        # ── PAT-COMP-NAME-DENSITY: vocabulary density pattern ──
        if pattern.id == "PAT-COMP-NAME-DENSITY":
            score = 0.0
            checks = 0

            # Signal: vocabulary density ≥ 30%
            checks += 1
            if sig["vocabulary_density"] >= 0.3:
                score += 1.0
            elif sig["vocabulary_density"] >= 0.1:
                score += 0.5
            elif sig["vocabulary_density"] >= 0.05:
                score += 0.2

            # Signal: multiple lines (list-like)
            checks += 1
            if sig["line_count"] >= 5:
                score += 1.0
            elif sig["line_count"] >= 3:
                score += 0.5

            # Signal: vocabulary hits
            checks += 1
            if sig["vocabulary_hits"] >= 5:
                score += 1.0
            elif sig["vocabulary_hits"] >= 2:
                score += 0.5

            return score / checks if checks > 0 else 0.0

        # ── PAT-COMP-QUANTITY-PAIRING: component-quantity pairing ──
        if pattern.id == "PAT-COMP-QUANTITY-PAIRING":
            score = 0.0
            checks = 0

            # Signal: quantity patterns present
            checks += 1
            if sig["quantity_matches"] >= 5:
                score += 1.0
            elif sig["quantity_matches"] >= 2:
                score += 0.6
            elif sig["quantity_matches"] >= 1:
                score += 0.3

            # Signal: vocabulary hits (component names to pair with)
            checks += 1
            if sig["vocabulary_hits"] >= 5:
                score += 1.0
            elif sig["vocabulary_hits"] >= 2:
                score += 0.5

            # Signal: pairing consistency (ratio of qty to vocab hits)
            checks += 1
            if sig["vocabulary_hits"] > 0:
                pairing_ratio = sig["quantity_matches"] / sig["vocabulary_hits"]
            else:
                pairing_ratio = 0.0
            if pairing_ratio >= 0.6:
                score += 1.0
            elif pairing_ratio >= 0.3:
                score += 0.5

            # Signal: line consistency
            checks += 1
            if sig["line_count"] >= 4:
                score += 1.0
            elif sig["line_count"] >= 2:
                score += 0.5

            return score / checks if checks > 0 else 0.0

        # ── Fallback: generic keyword overlap (for unknown patterns) ──
        content_lower = content.lower()
        all_indicators = pattern.detection_signals + pattern.structural_indicators + pattern.content_indicators
        total = len(all_indicators)
        if total == 0:
            return 0.0

        matches = 0
        for indicator in all_indicators:
            words = indicator.lower().split()
            if not words:
                continue
            word_matches = sum(1 for w in words if len(w) > 3 and w in content_lower)
            if word_matches > 0:
                matches += min(1.0, word_matches / len(words))

        return matches / total if total > 0 else 0.0

    def _find_alternatives(
        self, content: str, exclude: str
    ) -> list[str]:
        """Find alternative capabilities that might match better."""
        alternatives = []
        for cap_id, cap in self.graph.capabilities.items():
            if cap_id == exclude:
                continue
            match = self._match_patterns(cap, content)
            if match["score"] > 0.2:
                alternatives.append(cap_id)
        return alternatives

    def list_registered(self) -> list[dict[str, Any]]:
        """List all registered capabilities with their status."""
        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status.value,
                "maturity": c.maturity.value,
                "patterns": c.pattern_ids,
                "implementations": c.implementation_ids,
                "documents_tested": len(c.documents_tested),
                "cross_doc_success_rate": c.cross_doc_success_rate,
            }
            for c in self.graph.capabilities.values()
        ]
