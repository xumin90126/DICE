"""
Capability Matcher — Observation → Registry → Ranking → Candidates.

Phase 4.1: Replaces selector.py's if/else-based capability selection
with a pure observation-driven matching pipeline.

Architecture:
    DocumentObservation
            │
            ▼
    CapabilityMatcher.match()
            │
            ├── 1. Extract structural signals from observation
            ├── 2. Query CapabilityRegistry.list_active()
            ├── 3. RankingModel.score() each capability
            ├── 4. Sort by composite score descending
            └── 5. Return ranked MatchCandidate list

CRITICAL DESIGN:
    - Matcher reads ONLY from CapabilityRegistry (not ExperienceGraph)
    - Matcher input is DocumentObservation (not doc_class)
    - Matcher output is a RANKED LIST (not a single capability)
    - Fallback: returns MatchCandidate with score=0 when no capability
      scores above threshold (never errors, never calls legacy handler)
    - ZERO if/else on pattern_id, doc_class, product_id, filename
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from dice.graph.nodes import (
    Capability, DocumentObservation, MatchCandidate,
    CapabilityStatus,
)
from dice.registry import CapabilityRegistry
from dice.runtime.ranking import RankingModel, RankingWeights, DEFAULT_WEIGHTS


# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class MatcherConfig:
    """
    Configuration for the CapabilityMatcher.

    Attributes:
        min_score_threshold: minimum composite score to consider a
            capability "applicable" (below this = fallback territory)
        top_k: maximum number of candidates to return
        include_low_confidence: if True, include all candidates even
            below threshold (with score warnings)
        ranking_weights: weight vector for the ranking formula
    """
    min_score_threshold: float = 0.25
    top_k: int = 5
    include_low_confidence: bool = True
    ranking_weights: RankingWeights = field(default_factory=lambda: DEFAULT_WEIGHTS)


DEFAULT_CONFIG = MatcherConfig()


# ═══════════════════════════════════════════════════════════════════════════
# Match Result
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class MatchResult:
    """
    Complete result of a matching operation.

    Contains:
    - The ranked candidate list
    - Whether any capability scored above threshold
    - Diagnostics for debugging
    """
    candidates: list[MatchCandidate] = field(default_factory=list)
    observation_id: str = ""
    total_capabilities_considered: int = 0
    has_high_confidence_match: bool = False
    best_score: float = 0.0
    best_capability_id: str = ""
    diagnostics: list[str] = field(default_factory=list)
    timestamp: str = ""

    def top_candidate(self) -> Optional[MatchCandidate]:
        """Return the highest-scoring candidate."""
        return self.candidates[0] if self.candidates else None

    def applicable_candidates(
        self, threshold: Optional[float] = None
    ) -> list[MatchCandidate]:
        """Return candidates above the score threshold."""
        t = threshold if threshold is not None else DEFAULT_CONFIG.min_score_threshold
        return [c for c in self.candidates if c.score >= t]

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "total_considered": self.total_capabilities_considered,
            "has_high_confidence": self.has_high_confidence_match,
            "best_score": round(self.best_score, 4),
            "best_capability": self.best_capability_id,
            "candidates": [c.to_dict() for c in self.candidates],
            "diagnostics": self.diagnostics,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Observation Builder
# ═══════════════════════════════════════════════════════════════════════════


class ObservationBuilder:
    """
    Builds DocumentObservation from raw content — extracting structural
    signals WITHOUT any domain vocabulary dependency.

    This is a pure structural analyzer. It identifies:
    - Table structures (collapsed or intact)
    - List/key-value patterns
    - Numeric density
    - Element type presence (name/quantity/unit/catalog)

    It does NOT know about biochemistry, IFUs, or any domain.
    """

    @staticmethod
    def from_content(
        content: str,
        document_id: str = "",
        slice_id: str = "",
        observation_id: str = "",
        pattern_scores: Optional[dict[str, float]] = None,
    ) -> DocumentObservation:
        """
        Build a DocumentObservation from raw text content.

        Args:
            content: the text to observe
            document_id: source document (traceability only)
            slice_id: source slice (traceability only)
            observation_id: optional ID (auto-generated if empty)
            pattern_scores: optional pre-computed pattern scores from
                structural detectors (L1/L3)

        Returns:
            DocumentObservation with all structural signals populated.
        """
        import re
        from datetime import datetime, timezone

        # Basic metrics
        lines = [l for l in content.split("\n") if l.strip()]
        content_len = len(content)

        obs = DocumentObservation(
            id=observation_id or f"OBS-{document_id}-{slice_id}" if document_id else f"OBS-{hash(content) % 100000:05d}",
            document_id=document_id,
            slice_id=slice_id,
            content_snippet=content[:500],
            content_length=content_len,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        if not content.strip():
            return obs

        # ── Structure signals ──
        obs.line_count = len(lines)
        obs.avg_line_length = (
            sum(len(l) for l in lines) / len(lines) if lines else 0.0
        )

        # Table structure detection
        obs.has_table_structure = ObservationBuilder._detect_table_structure(content, lines)
        obs.has_collapsed_table = ObservationBuilder._detect_collapsed_table(content)

        # List structure detection
        obs.has_list_structure = ObservationBuilder._detect_list_structure(content)

        # Key-value pair detection
        obs.has_key_value_pairs = ObservationBuilder._detect_key_value_pairs(content)

        # Phase 5.5: Markdown table detection (|---| format)
        obs.has_markdown_table = ObservationBuilder._detect_markdown_table(content, lines)

        # Phase 5.5: Consecutive numbered list detection (1. 2. 3. ...)
        obs.has_numbered_list = ObservationBuilder._detect_numbered_list(content)

        # Numeric density
        obs.has_numeric_density_high = ObservationBuilder._detect_numeric_density(content)

        # Header lines
        obs.header_section_count = ObservationBuilder._count_header_lines(lines)

        # ── Element type detection ──
        obs.detected_element_types = ObservationBuilder._detect_element_types(content)

        # ── Pattern signals ──
        if pattern_scores:
            obs.pattern_match_scores = dict(pattern_scores)
            obs.detected_pattern_ids = list(pattern_scores.keys())
        else:
            # Auto-detect patterns based on structural signals
            obs.detected_pattern_ids = ObservationBuilder._infer_patterns(obs, content)

        # ── Content quality ──
        words = content.split()
        obs.unique_token_ratio = (
            len(set(w.lower() for w in words)) / len(words) if words else 0.0
        )
        obs.noise_ratio = ObservationBuilder._estimate_noise(content)

        return obs

    # ──────────────────────── Structural Detectors ────────────────────────

    @staticmethod
    def _detect_table_structure(content: str, lines: list[str]) -> bool:
        """Check for tabular/columnar structure."""
        import re
        # Multi-space column separators (>2 spaces between words on multiple lines)
        columnar_lines = sum(
            1 for l in lines
            if len(re.findall(r'\S+\s{2,}\S+', l)) >= 2
        )
        # Tab characters
        has_tabs = '\t' in content
        return columnar_lines >= 2 or has_tabs

    @staticmethod
    def _detect_markdown_table(content: str, lines: list[str]) -> bool:
        """
        Detect Markdown table format: |---| separator row + | col delimiters.

        Phase 5.5: Previously invisible to table detection (which only recognized
        multi-space and tab-separated formats). Fixes the S05 false positive.
        """
        import re
        # Must have a separator row: |---|----| etc.
        has_separator = any(
            re.match(r'^\|[\s\-:]+\|', l) for l in lines
        )
        if not has_separator:
            return False
        # Must have at least 2 data rows with | delimiters
        pipe_rows = sum(
            1 for l in lines
            if l.count('|') >= 2
        )
        return pipe_rows >= 3  # header + separator + >=1 data row

    @staticmethod
    def _detect_collapsed_table(content: str) -> bool:
        """
        Detect word-smashed table artifacts — typical of PDF extraction
        where table cells get concatenated without delimiters.
        """
        import re
        signals = 0

        # "1 × 250 μL" style quantity expressions
        if re.search(r'\d+\s*(?:×|x)\s*\d+', content):
            signals += 1

        # Quantity-unit pairs (e.g., "250 μL", "5 mg")
        if len(re.findall(r'\d+\s*(?:μL|mL|mg|μg|ng|g|L|mM|μM|mM|U/μL)', content)) >= 3:
            signals += 1

        # Catalog number patterns
        if len(re.findall(r'\b[A-Z]{2,4}\d{4,8}\b', content)) >= 2:
            signals += 1

        # Long unbroken strings (collapsed table rows)
        long_segments = [seg for seg in content.split('\n') if len(seg) > 200]
        if long_segments:
            signals += 1

        return signals >= 2

    @staticmethod
    def _detect_list_structure(content: str) -> bool:
        """Check for bulleted or enumerated list patterns."""
        import re
        lines = content.split('\n')
        bullet_lines = sum(
            1 for l in lines
            if re.match(r'^\s*(?:[-•*]|\d+[.)]\s)', l)
        )
        return bullet_lines >= 2

    @staticmethod
    def _detect_numbered_list(content: str) -> bool:
        """
        Detect CONSECUTIVE numbered list (at least 3 sequential numbers).

        Phase 5.5: Distinguishes true numbered lists (1. 2. 3.) from scattered
        numbered items. Used together with domain markers to separate safety
        warnings from procedure steps.

        Returns True only when >=3 lines form a consecutive sequence.
        """
        import re
        lines = content.split('\n')
        numbers = []
        for l in lines:
            m = re.match(r'^\s*(\d+)[.)]\s', l)
            if m:
                numbers.append(int(m.group(1)))
        # Check for consecutive sequence: at least 3 numbers in sequence
        if len(numbers) < 3:
            return False
        consecutive = 1
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                consecutive += 1
                if consecutive >= 3:
                    return True
            else:
                consecutive = 1
        return False

    @staticmethod
    def _has_safety_markers(content: str) -> bool:
        """
        Check for safety/warning/caution domain markers.

        Phase 5.5: Used with has_numbered_list to distinguish safety warnings
        from procedure steps. Pure domain vocabulary check — kept separate
        from structure detection to maintain structure/domain separation.
        """
        import re
        safety_terms = (
            r'warning|caution|danger|hazard|precaution|safety|'
            r'harmful|toxic|irritant|avoid\b|protective|biosafety|'
            r'hazardous|flammable|corrosive|biohazard|'
            r'警告|注意|危险|安全|小心|避免|防护'
        )
        return bool(re.search(safety_terms, content, re.IGNORECASE))

    @staticmethod
    def _detect_key_value_pairs(content: str) -> bool:
        """Check for Label: Value or Label = Value patterns."""
        import re
        pairs = len(re.findall(r'\b[A-Z][a-zA-Z\s]{2,20}:\s*\S', content))
        return pairs >= 2

    @staticmethod
    def _detect_numeric_density(content: str) -> bool:
        """Check if numbers make up a high proportion of tokens."""
        import re
        tokens = content.split()
        if not tokens:
            return False
        numeric = sum(1 for t in tokens if re.match(r'^[\d.,]+%?$', t))
        return (numeric / len(tokens)) > 0.15  # >15% numeric tokens

    @staticmethod
    def _count_header_lines(lines: list[str]) -> int:
        """Count lines that look like section headers."""
        import re
        count = 0
        for l in lines:
            # ALL CAPS short lines
            if l.isupper() and 3 < len(l) < 80:
                count += 1
            # Numbered headers like "1. Introduction" or "Section 2:"
            elif re.match(r'^\d+[\.\)]\s+[A-Z]', l):
                count += 1
        return count

    # ──────────────────────── Element Type Detection ────────────────────────

    @staticmethod
    def _detect_element_types(content: str) -> dict[str, int]:
        """
        Detect presence of structural element types in content.

        These are STRUCTURAL categories (name, quantity, unit, catalog_number),
        NOT domain-specific terms. The detection uses universal structural
        patterns that work across domains.
        """
        import re

        types = {}

        # NAME: capitalized multi-word phrases (likely proper names)
        # Detected as "Aaa Bbb" or "Aaa Bbb Ccc" patterns
        name_candidates = re.findall(
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', content
        )
        types["name"] = len(set(name_candidates))

        # QUANTITY: numeric values (with optional decimal and unit context)
        quantities = re.findall(
            r'\b(\d+(?:\.\d+)?)\s*(?:μL|mL|mg|μg|ng|g|L|mM|μM|mM|U|U/μL|ng/μL|%|℃|°C|min|s|h)?\b',
            content
        )
        types["quantity"] = len(quantities)

        # UNIT: measurement units
        units = re.findall(
            r'\b(μL|mL|mg|μg|ng|g|L|mM|μM|mM|U/μL|ng/μL|%)\b',
            content
        )
        types["unit"] = len(units)

        # CATALOG NUMBER: alphanumeric ID patterns
        catalog = re.findall(
            r'\b([A-Z]{2,5}[-\s]?\d{4,8}(?:[-\s]\d+)?)\b', content
        )
        types["catalog_number"] = len(catalog)

        # COUNT: discrete count indicators
        counts = re.findall(
            r'\b(\d+)\s*(?:pcs|tubes|strips|wells|plates|columns|tips)\b',
            content, re.IGNORECASE
        )
        types["count"] = len(counts)

        # VOLUME: volume-specific patterns
        volumes = re.findall(
            r'\b(\d+(?:\.\d+)?)\s*(?:μL|mL|L)\b', content
        )
        types["volume"] = len(volumes)

        # CONCENTRATION: concentration-specific patterns
        concentrations = re.findall(
            r'\b(\d+(?:\.\d+)?)\s*(?:mM|μM|ng/μL|mg/mL|μg/μL|%)\b', content
        )
        types["concentration"] = len(concentrations)

        # TEMPERATURE: temperature patterns (storage condition signal)
        temps = re.findall(
            r'\b(-?\d+(?:\.\d+)?)\s*(?:℃|°C|degrees?\s*C)\b', content
        )
        types["temperature"] = len(temps)

        # TEMPERATURE_RANGE: range-connected temperatures
        temp_ranges = re.findall(
            r'(-?\d+(?:\.\d+)?)\s*(?:-|to|~)\s*(-?\d+(?:\.\d+)?)\s*(?:℃|°C)',
            content
        )
        types["temperature_range"] = len(temp_ranges)

        # TIME: time duration expressions
        times = re.findall(
            r'\b(\d+(?:\.\d+)?)\s*(?:min|minute|hour|hr|day|sec|second|s)\b',
            content, re.IGNORECASE
        )
        types["time"] = len(times)

        return types

    # ──────────────────────── Pattern Inference ────────────────────────

    @staticmethod
    def _infer_patterns(obs: DocumentObservation, content: str = "") -> list[str]:
        """
        Infer which structural pattern IDs are likely active based on
        the observation's signals.

        This is a GENERAL structural inference — NOT based on any
        domain vocabulary or pattern-specific if/else.

        Patterns are identified by their STRUCTURAL characteristics only.

        Phase 5.1a: Extended from 3 to 7 patterns (v2 + Batch 1).
        Phase 5.5: Added numbered_list + safety_markers path for PAT-SAFETY-WARNINGS.
        """
        patterns = []

        # ── PAT-COMP-TABLE-COLLAPSE: collapsed table + high element density ──
        if obs.has_collapsed_table and obs.detected_element_types.get("name", 0) >= 3:
            patterns.append("PAT-COMP-TABLE-COLLAPSE")
            obs.pattern_match_scores["PAT-COMP-TABLE-COLLAPSE"] = min(
                1.0,
                0.5
                + 0.1 * min(5, obs.detected_element_types.get("name", 0))
                + 0.1 * min(5, obs.detected_element_types.get("quantity", 0))
            )

        # ── PAT-COMP-NAME-DENSITY: high ratio of name-type tokens ──
        if obs.detected_element_types.get("name", 0) >= 5:
            patterns.append("PAT-COMP-NAME-DENSITY")
            obs.pattern_match_scores["PAT-COMP-NAME-DENSITY"] = min(
                1.0,
                0.4 + 0.05 * min(12, obs.detected_element_types.get("name", 0))
            )

        # ── PAT-COMP-QUANTITY-PAIRING: both quantities and names present ──
        if (
            obs.detected_element_types.get("quantity", 0) >= 2
            and obs.detected_element_types.get("name", 0) >= 2
        ):
            patterns.append("PAT-COMP-QUANTITY-PAIRING")
            obs.pattern_match_scores["PAT-COMP-QUANTITY-PAIRING"] = min(
                1.0,
                0.4
                + 0.1 * min(5, obs.detected_element_types.get("quantity", 0))
                + 0.05 * min(10, obs.detected_element_types.get("name", 0))
            )

        # ── PAT-TABLE-COLLAPSE-STRUCT: strong collapsed table evidence ──
        # Distinct from PAT-COMP-TABLE-COLLAPSE: requires HIGH quantity count
        # (collapsed table with many data points, not a few scattered values)
        if obs.has_collapsed_table and obs.detected_element_types.get("quantity", 0) >= 5:
            patterns.append("PAT-TABLE-COLLAPSE-STRUCT")
            obs.pattern_match_scores["PAT-TABLE-COLLAPSE-STRUCT"] = min(
                1.0,
                0.40
                + 0.08 * min(8, obs.detected_element_types.get("quantity", 0))
                + 0.04 * min(15, obs.detected_element_types.get("unit", 0))
            )

        # ── PAT-ANCHOR-DRIVEN-EXTRACT: pervasive key-value structure ──
        # Requires LONG key-value-formatted content (not just 2 incidental pairs).
        # The key-value ratio (line_count >= 15) filters short incidental content.
        if obs.has_key_value_pairs and obs.line_count >= 15 and not obs.has_collapsed_table:
            patterns.append("PAT-ANCHOR-DRIVEN-EXTRACT")
            obs.pattern_match_scores["PAT-ANCHOR-DRIVEN-EXTRACT"] = min(
                1.0,
                0.35
                + 0.12 * (1.0 if obs.has_key_value_pairs else 0.0)
                + 0.03 * min(20, obs.line_count)
            )

        # ── PAT-COLUMNAR-ALIGNMENT: strong table structure WITHOUT collapse ──
        # Requires table structure AND enough lines to form real columns
        if obs.has_table_structure and not obs.has_collapsed_table and obs.line_count >= 8:
            patterns.append("PAT-COLUMNAR-ALIGNMENT")
            obs.pattern_match_scores["PAT-COLUMNAR-ALIGNMENT"] = min(
                1.0,
                0.35
                + 0.12 * (1.0 if obs.has_table_structure else 0.0)
                + 0.03 * min(20, obs.line_count)
            )

        # ── PAT-NAME-QUANTITY-TRIPLE: name + quantity proximity ──
        # Requires BOTH names and quantities present, with high numeric density
        if (obs.has_numeric_density_high
                and obs.detected_element_types.get("quantity", 0) >= 5
                and obs.detected_element_types.get("name", 0) >= 3):
            patterns.append("PAT-NAME-QUANTITY-TRIPLE")
            obs.pattern_match_scores["PAT-NAME-QUANTITY-TRIPLE"] = min(
                1.0,
                0.35
                + 0.10 * min(8, obs.detected_element_types.get("quantity", 0))
                + 0.05 * min(12, obs.detected_element_types.get("name", 0))
            )

        # ═══════════════════════════════════════════════════════════════
        # Batch 2: Content Type Detection Patterns (Phase 5.1b)
        # ═══════════════════════════════════════════════════════════════

        # ── PAT-STORAGE-CONDITIONS: temperature patterns + key-value pairs ──
        if obs.detected_element_types.get("temperature", 0) >= 1:
            patterns.append("PAT-STORAGE-CONDITIONS")
            obs.pattern_match_scores["PAT-STORAGE-CONDITIONS"] = min(
                1.0,
                0.30
                + 0.15 * min(5, obs.detected_element_types.get("temperature", 0))
                + 0.10 * (1.0 if obs.has_key_value_pairs else 0.0)
                + 0.05 * min(10, obs.detected_element_types.get("concentration", 0))
            )

        # ── PAT-SAFETY-WARNINGS: high header density + (key-value OR numbered safety list) ──
        # Phase 5.5: Added numbered_list + safety_markers path. Numbered list ALONE
        # does NOT trigger safety — must also have domain safety markers to avoid
        # misclassifying procedure steps as safety warnings.
        safety_num_trigger = (
            obs.has_numbered_list
            and content
            and ObservationBuilder._has_safety_markers(content)
        )
        if obs.header_section_count >= 2 and (obs.has_key_value_pairs or safety_num_trigger):
            patterns.append("PAT-SAFETY-WARNINGS")
            obs.pattern_match_scores["PAT-SAFETY-WARNINGS"] = min(
                1.0,
                0.25
                + 0.15 * min(6, obs.header_section_count)
                + 0.10 * (1.0 if obs.has_list_structure else 0.0)
                + 0.10 * (1.0 if obs.has_numbered_list else 0.0)
            )

        # ── PAT-TROUBLESHOOT-QA: list structure + moderate headers ──
        if obs.has_list_structure and obs.header_section_count >= 1:
            patterns.append("PAT-TROUBLESHOOT-QA")
            obs.pattern_match_scores["PAT-TROUBLESHOOT-QA"] = min(
                1.0,
                0.25
                + 0.15 * (1.0 if obs.has_list_structure else 0.0)
                + 0.10 * min(5, obs.header_section_count)
            )

        # ── PAT-PROCEDURE-STEPS: numbered list structure + many lines ──
        if obs.has_list_structure and obs.line_count >= 12:
            patterns.append("PAT-PROCEDURE-STEPS")
            obs.pattern_match_scores["PAT-PROCEDURE-STEPS"] = min(
                1.0,
                0.25
                + 0.12 * (1.0 if obs.has_list_structure else 0.0)
                + 0.03 * min(25, obs.line_count)
            )

        # ── PAT-MATERIALS-LIST: moderate numeric density + name elements ──
        if (obs.detected_element_types.get("name", 0) >= 2
                and obs.detected_element_types.get("count", 0) >= 1):
            patterns.append("PAT-MATERIALS-LIST")
            obs.pattern_match_scores["PAT-MATERIALS-LIST"] = min(
                1.0,
                0.25
                + 0.10 * min(8, obs.detected_element_types.get("name", 0))
                + 0.10 * min(5, obs.detected_element_types.get("count", 0))
                + 0.05 * (1.0 if obs.has_list_structure else 0.0)
            )

        # ═══════════════════════════════════════════════════════════════
        # Batch 3: Validation & Composition Patterns (Phase 5.1c)
        # ═══════════════════════════════════════════════════════════════

        # ── PAT-TEMP-RANGE: temperature range patterns ──
        # Requires BOTH single temps and range-connected temps (2+ temps, 1+ range).
        # Thresholded to avoid triggering on a single temp mention.
        if (obs.detected_element_types.get("temperature", 0) >= 2
                and obs.detected_element_types.get("temperature_range", 0) >= 1):
            patterns.append("PAT-TEMP-RANGE")
            obs.pattern_match_scores["PAT-TEMP-RANGE"] = min(
                1.0,
                0.25
                + 0.15 * min(4, obs.detected_element_types.get("temperature", 0))
                + 0.20 * min(3, obs.detected_element_types.get("temperature_range", 0))
                + 0.10 * (1.0 if obs.has_key_value_pairs else 0.0)
            )

        # ── PAT-TIME-SPEC: time specification density ──
        # Requires 2+ time expressions AND structured content (list or many lines).
        if (obs.detected_element_types.get("time", 0) >= 2
                and (obs.has_list_structure or obs.line_count >= 10)):
            patterns.append("PAT-TIME-SPEC")
            obs.pattern_match_scores["PAT-TIME-SPEC"] = min(
                1.0,
                0.25
                + 0.12 * min(8, obs.detected_element_types.get("time", 0))
                + 0.10 * (1.0 if obs.has_list_structure else 0.0)
                + 0.03 * min(20, obs.line_count)
            )

        # ── PAT-CATALOG-NUMBER: pure catalog listing ──
        # Requires HIGH catalog density (≥4) AND explicit exclusion of collapsed
        # table structure to avoid competing with CAP-COMP-TABLE.
        if (obs.detected_element_types.get("catalog_number", 0) >= 4
                and not obs.has_collapsed_table):
            patterns.append("PAT-CATALOG-NUMBER")
            obs.pattern_match_scores["PAT-CATALOG-NUMBER"] = min(
                1.0,
                0.25
                + 0.08 * min(10, obs.detected_element_types.get("catalog_number", 0))
                + 0.10 * (1.0 if obs.has_list_structure else 0.0)
            )

        # ── PAT-QUANTITY-INTEGRITY: multi-dimensional quantity diversity ──
        # Requires volume (≥2), concentration (≥2), AND count (≥1) elements.
        # High total quantity count (≥8) signals enough data for validation.
        if (obs.detected_element_types.get("volume", 0) >= 2
                and obs.detected_element_types.get("concentration", 0) >= 2
                and obs.detected_element_types.get("count", 0) >= 1
                and obs.detected_element_types.get("quantity", 0) >= 8):
            patterns.append("PAT-QUANTITY-INTEGRITY")
            obs.pattern_match_scores["PAT-QUANTITY-INTEGRITY"] = min(
                1.0,
                0.25
                + 0.10 * min(6, obs.detected_element_types.get("volume", 0))
                + 0.10 * min(6, obs.detected_element_types.get("concentration", 0))
                + 0.05 * min(10, obs.detected_element_types.get("count", 0))
            )

        # ── PAT-UNIT-DIVERSITY: multiple unit types detected ──
        # Requires 4+ unit elements AND diverse unit context (concentration or volume).
        if (obs.detected_element_types.get("unit", 0) >= 4
                and (obs.detected_element_types.get("concentration", 0) >= 2
                     or obs.detected_element_types.get("volume", 0) >= 2)):
            patterns.append("PAT-UNIT-DIVERSITY")
            obs.pattern_match_scores["PAT-UNIT-DIVERSITY"] = min(
                1.0,
                0.25
                + 0.08 * min(10, obs.detected_element_types.get("unit", 0))
                + 0.10 * (1.0 if obs.detected_element_types.get("concentration", 0) >= 2 else 0.0)
                + 0.07 * (1.0 if obs.detected_element_types.get("volume", 0) >= 2 else 0.0)
            )

        # ── PAT-TABLE-CLASSIFY: intact non-collapsed table structure ──
        # Requires explicit table structure WITHOUT collapse, headers, and column-type diversity.
        if (obs.has_table_structure
                and not obs.has_collapsed_table
                and obs.header_section_count >= 1
                and obs.line_count >= 6):
            patterns.append("PAT-TABLE-CLASSIFY")
            obs.pattern_match_scores["PAT-TABLE-CLASSIFY"] = min(
                1.0,
                0.25
                + 0.15 * (1.0 if obs.has_table_structure else 0.0)
                + 0.10 * min(4, obs.header_section_count)
                + 0.03 * min(20, obs.line_count)
            )

        # ═══════════════════════════════════════════════════════════════
        # Phase 5.2: Discrimination-Test Patterns (shared signal overlap)
        # ═══════════════════════════════════════════════════════════════

        # ── PAT-TABLE-BASIC-STRUCT: lower-threshold version of collapsed table ──
        # Intentionally overlaps with PAT-TABLE-COLLAPSE-STRUCT.
        if obs.has_collapsed_table and obs.detected_element_types.get("quantity", 0) >= 3:
            patterns.append("PAT-TABLE-BASIC-STRUCT")
            obs.pattern_match_scores["PAT-TABLE-BASIC-STRUCT"] = min(
                1.0,
                0.20
                + 0.06 * min(10, obs.detected_element_types.get("quantity", 0))
                + 0.04 * min(15, obs.detected_element_types.get("unit", 0))
            )

        # ── PAT-PARAMETER-LIST: lower-threshold key-value detector ──
        # Overlaps with PAT-ANCHOR-DRIVEN-EXTRACT.
        if obs.has_key_value_pairs:
            patterns.append("PAT-PARAMETER-LIST")
            obs.pattern_match_scores["PAT-PARAMETER-LIST"] = min(
                1.0,
                0.20
                + 0.15 * (1.0 if obs.has_key_value_pairs else 0.0)
                + 0.02 * min(20, obs.line_count)
            )

        # ── PAT-STORAGE-LONG-TERM: storage specialization ──
        # Overlaps with PAT-STORAGE-CONDITIONS.
        if (obs.detected_element_types.get("temperature", 0) >= 1
                and obs.has_key_value_pairs):
            patterns.append("PAT-STORAGE-LONG-TERM")
            obs.pattern_match_scores["PAT-STORAGE-LONG-TERM"] = min(
                1.0,
                0.20
                + 0.15 * min(4, obs.detected_element_types.get("temperature", 0))
                + 0.10 * (1.0 if obs.has_key_value_pairs else 0.0)
            )

        # ── PAT-WARNING-EXTRACT: warning extraction specialization ──
        # Overlaps with PAT-SAFETY-WARNINGS.
        if obs.header_section_count >= 1:
            patterns.append("PAT-WARNING-EXTRACT")
            obs.pattern_match_scores["PAT-WARNING-EXTRACT"] = min(
                1.0,
                0.20
                + 0.08 * min(6, obs.header_section_count)
                + 0.05 * min(10, obs.line_count)
            )

        # ── PAT-STEP-COUNT: step counting specialization ──
        # Overlaps with PAT-PROCEDURE-STEPS.
        if obs.has_list_structure and obs.line_count >= 5:
            patterns.append("PAT-STEP-COUNT")
            obs.pattern_match_scores["PAT-STEP-COUNT"] = min(
                1.0,
                0.20
                + 0.10 * (1.0 if obs.has_list_structure else 0.0)
                + 0.03 * min(20, obs.line_count)
            )

        return patterns

    # ──────────────────────── Quality ────────────────────────

    @staticmethod
    def _estimate_noise(content: str) -> float:
        """Estimate noise proportion (non-content characters)."""
        import re
        if not content:
            return 0.0
        # Noise: standalone numbers, special chars, very short fragments
        tokens = content.split()
        if not tokens:
            return 0.0
        noise_tokens = sum(
            1 for t in tokens
            if re.match(r'^[\d\W]+$', t) or len(t) <= 1
        )
        return noise_tokens / len(tokens)


# ═══════════════════════════════════════════════════════════════════════════
# CapabilityMatcher
# ═══════════════════════════════════════════════════════════════════════════


class CapabilityMatcher:
    """
    Matches DocumentObservations to Capabilities via the Registry.

    The core entry point of the Capability Operating System's matching
    layer. Replaces the old selector.py's manual if/else logic with
    a unified observation → ranking pipeline.

    Usage:
        registry = CapabilityRegistry()
        # ... bootstrap capabilities into registry ...
        matcher = CapabilityMatcher(registry)

        obs = ObservationBuilder.from_content(
            content="1. T4 DNA Ligase  5 U/μL  250 units  ...",
            document_id="DC201-C1",
            slice_id="04_components",
        )
        result = matcher.match(obs)

        # Get best candidate
        best = result.top_candidate()
        if best and best.score > 0.5:
            print(f"Using {best.capability_name} (score={best.score:.2f})")

        # Or iterate all candidates
        for c in result.candidates:
            print(f"  {c.capability_name}: {c.score:.3f}")
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        config: Optional[MatcherConfig] = None,
    ):
        self.registry = registry
        self.config = config or DEFAULT_CONFIG
        self.ranking_model = RankingModel(weights=self.config.ranking_weights)

    # ──────────────────────── Public API ────────────────────────

    def match(self, observation: DocumentObservation) -> MatchResult:
        """
        Match an observation against all active capabilities.

        Pipeline:
            1. Query registry for all active capabilities
            2. Score each capability against the observation
            3. Rank by composite score descending
            4. Return MatchResult with full diagnostics

        Returns:
            MatchResult with ranked candidates. If no capability scores
            above threshold, the result will indicate low confidence but
            still contain the full ranking — never errors out.
        """
        from datetime import datetime, timezone

        active_caps = self.registry.list_active()

        if not active_caps:
            return MatchResult(
                observation_id=observation.id,
                total_capabilities_considered=0,
                diagnostics=["No active capabilities registered in Registry"],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Rank all active capabilities
        candidates = self.ranking_model.rank(observation, active_caps)

        # Apply top_k limit
        candidates = candidates[:self.config.top_k]

        # Filter low-confidence if configured
        if not self.config.include_low_confidence:
            candidates = [
                c for c in candidates
                if c.score >= self.config.min_score_threshold
            ]

        # Determine match quality
        best = candidates[0] if candidates else None
        has_high = (
            best is not None and best.score >= self.config.min_score_threshold
        )

        diagnostics = []
        if not has_high:
            diagnostics.append(
                f"No capability scored above threshold "
                f"({self.config.min_score_threshold}). Best: "
                f"{best.capability_name if best else 'N/A'} "
                f"({best.score:.3f})" if best else "N/A"
            )
            diagnostics.append(
                "Returning ranked candidates for caller decision (fallback: "
                "use best candidate or mark as unknown)"
            )
        else:
            diagnostics.append(
                f"High-confidence match: {best.capability_name} "
                f"(score={best.score:.3f})"
            )

        return MatchResult(
            candidates=candidates,
            observation_id=observation.id,
            total_capabilities_considered=len(active_caps),
            has_high_confidence_match=has_high,
            best_score=best.score if best else 0.0,
            best_capability_id=best.capability_id if best else "",
            diagnostics=diagnostics,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def explain_match(
        self,
        observation: DocumentObservation,
    ) -> dict[str, Any]:
        """
        Full Capability Selection Trace — decomposable, explainable output.

        Returns a complete trace of why each capability was scored as it was,
        enabling debugging and audit of the matching decision.

        Output structure:
        {
            "observation_features": {...},
            "candidates": [
                {
                    "capability_id": "...",
                    "capability_name": "...",
                    "score": 0.85,
                    "score_breakdown": {
                        "pattern_match": 0.90,
                        "evidence_quality": 0.75,
                        "historical_success": 0.95,
                        "cross_domain": 0.80,
                        "failure_penalty": 0.05,
                    },
                    "formula": "0.35*0.90 + 0.25*0.75 + 0.20*0.95 + 0.10*0.80 - 0.10*0.05 = 0.85",
                    "evidence": {
                        "matched_patterns": [...],
                        "matched_elements": [...],
                    },
                },
                ...
            ],
            "selected_capability": "CAP-COMP-TABLE",
            "selection_rationale": "Highest composite score (0.85) driven by...",
        }

        This is a BLACK-BOX-FREE output: every score component is visible
        and the formula used to combine them is explicit.
        """
        active_caps = self.registry.list_active()
        if not active_caps:
            return {
                "observation_features": observation.to_summary(),
                "candidates": [],
                "selected_capability": None,
                "selection_rationale": "No active capabilities registered",
            }

        # Score all
        candidates = self.ranking_model.rank(observation, active_caps)
        candidates = candidates[:self.config.top_k]

        # Build trace for each candidate
        candidate_traces = []
        for c in candidates:
            cap = self.registry.get(c.capability_id)
            formula_parts = []

            if self.config.ranking_weights.pattern_match > 0:
                formula_parts.append(
                    f"{self.config.ranking_weights.pattern_match}*{c.pattern_match_score:.2f}"
                )
            if self.config.ranking_weights.evidence_quality > 0:
                formula_parts.append(
                    f"{self.config.ranking_weights.evidence_quality}*{c.evidence_quality_score:.2f}"
                )
            if self.config.ranking_weights.historical_success > 0:
                formula_parts.append(
                    f"{self.config.ranking_weights.historical_success}*{c.historical_success_score:.2f}"
                )
            if self.config.ranking_weights.cross_domain > 0:
                formula_parts.append(
                    f"{self.config.ranking_weights.cross_domain}*{c.cross_domain_score:.2f}"
                )

            positive = " + ".join(formula_parts)
            weight_sum = sum([
                self.config.ranking_weights.pattern_match,
                self.config.ranking_weights.evidence_quality,
                self.config.ranking_weights.historical_success,
                self.config.ranking_weights.cross_domain,
            ])
            if weight_sum > 0 and weight_sum != 1.0:
                positive_expr = f"({positive}) / {weight_sum:.2f}"
            else:
                positive_expr = positive

            if self.config.ranking_weights.failure_penalty > 0 and c.failure_penalty > 0.001:
                formula = (
                    f"{positive_expr} "
                    f"- {c.failure_penalty:.3f} "
                    f"= {c.score:.3f}"
                )
            else:
                formula = f"{positive_expr} = {c.score:.3f}"

            candidate_traces.append({
                "capability_id": c.capability_id,
                "capability_name": c.capability_name,
                "score": round(c.score, 4),
                "score_breakdown": {
                    "pattern_match": round(c.pattern_match_score, 4),
                    "evidence_quality": round(c.evidence_quality_score, 4),
                    "historical_success": round(c.historical_success_score, 4),
                    "cross_domain": round(c.cross_domain_score, 4),
                    "failure_penalty": round(c.failure_penalty, 4),
                },
                "formula": formula,
                "evidence": {
                    "matched_patterns": c.matched_patterns,
                    "matched_element_types": c.matched_element_types,
                    "evidence_summary": c.evidence_summary,
                },
                "capability_metadata": {
                    "version": c.capability_version,
                    "status": c.capability_status,
                    "execution_count": cap.execution_count if cap else 0,
                    "success_rate": cap.cross_doc_success_rate if cap else 0.0,
                    "documents_tested": len(cap.documents_tested) if cap else 0,
                } if cap else {},
            })

        # Best candidate rationale
        best = candidates[0] if candidates else None
        if best and best.score >= self.config.min_score_threshold:
            rationale = (
                f"Selected '{best.capability_name}' (score={best.score:.3f}) — "
                f"highest composite score. "
                f"Driven by: pattern_match={best.pattern_match_score:.2f}, "
                f"historical_success={best.historical_success_score:.2f}. "
                f"Threshold: {self.config.min_score_threshold}"
            )
        elif best:
            rationale = (
                f"No capability above threshold ({self.config.min_score_threshold}). "
                f"Best candidate: '{best.capability_name}' (score={best.score:.3f}) — "
                f"below threshold. Caller should treat as uncertain/unknown."
            )
        else:
            rationale = "No candidates available."

        return {
            "observation_features": observation.to_summary(),
            "ranking_weights": {
                "pattern_match": self.config.ranking_weights.pattern_match,
                "evidence_quality": self.config.ranking_weights.evidence_quality,
                "historical_success": self.config.ranking_weights.historical_success,
                "cross_domain": self.config.ranking_weights.cross_domain,
                "failure_penalty": self.config.ranking_weights.failure_penalty,
            },
            "candidates": candidate_traces,
            "selected_capability": best.capability_id if best else None,
            "selection_rationale": rationale,
        }

    def match_content(
        self,
        content: str,
        document_id: str = "",
        slice_id: str = "",
        pattern_scores: Optional[dict[str, float]] = None,
    ) -> MatchResult:
        """
        Convenience method: build observation from raw content, then match.

        This is the most common entry point for pipeline integration.
        """
        obs = ObservationBuilder.from_content(
            content=content,
            document_id=document_id,
            slice_id=slice_id,
            pattern_scores=pattern_scores,
        )
        return self.match(obs)
