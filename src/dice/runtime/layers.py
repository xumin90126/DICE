"""
Three-Layer Capability Runtime Engine.

Unified execution chain:
    Document → L1 Structure Detection → L2 Semantic Evidence → L3 Structure Extraction

L1: Structure Detection
    - Document structure, table collapse, information region localization
    - Output: structure signals (boolean + confidence)

L2: Semantic Evidence Layer  
    - Known knowledge enhancement, domain evidence matching
    - CRITICAL: L2 can only ENHANCE confidence, NEVER determine capability
    - Output: vocabulary boost (0.0-1.0)

L3: Structure Extraction Layer
    - Name → quantity → unit → relationship extraction
    - Uses QUANTITY PATTERNS as anchors (NOT vocabulary)
    - Works on ANY domain without knowing component names
    - Core principle: L3 structural understanding > L2 vocabulary knowledge

Three execution strategies:
    Case A: L2 evidence sufficient → L2-enhanced semantic extraction
    Case B: L2 insufficient → fallback to pure L3 structural extraction
    Case C: Both conflict or low confidence → uncertain state
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LayerResult:
    """Output from a single layer execution."""
    layer: str = ""                     # "L1" | "L2" | "L3"
    activated: bool = False             # Did this layer produce output?
    score: float = 0.0                  # Contribution score (0.0-1.0)
    confidence: float = 0.0             # Layer's own confidence
    description: str = ""               # Human-readable
    data: dict[str, Any] = field(default_factory=dict)  # Layer-specific data


@dataclass
class LayerTrace:
    """Complete three-layer execution trace."""
    document_id: str = ""
    slice_id: str = ""
    content_length: int = 0

    # Per-layer results
    l1_result: LayerResult = field(default_factory=lambda: LayerResult(layer="L1"))
    l2_result: LayerResult = field(default_factory=lambda: LayerResult(layer="L2"))
    l3_result: LayerResult = field(default_factory=lambda: LayerResult(layer="L3"))

    # Strategy decision
    strategy_case: str = ""             # "A" | "B" | "C"
    primary_layer: str = ""             # "L1_STRUCTURE" | "L2_SEMANTIC" | "L3_STRUCTURAL" | "UNCERTAIN"
    l2_sufficient: bool = False

    # Extraction result
    components: list[dict[str, Any]] = field(default_factory=list)
    total_extracted: int = 0
    extraction_quality: float = 0.0     # ratio of complete extractions

    def layer_contributions(self) -> dict[str, Any]:
        """Layer contribution analysis for the unified CapabilityResult."""
        return {
            "L1": {
                "activated": self.l1_result.activated,
                "score": round(self.l1_result.score, 4),
                "description": self.l1_result.description[:120],
            },
            "L2": {
                "activated": self.l2_result.activated,
                "score": round(self.l2_result.score, 4),
                "description": self.l2_result.description[:120],
            },
            "L3": {
                "activated": self.l3_result.activated,
                "score": round(self.l3_result.score, 4),
                "description": self.l3_result.description[:120],
            },
            "primary_layer": self.primary_layer,
            "strategy_case": self.strategy_case,
            "l2_sufficient": self.l2_sufficient,
        }


# ═══════════════════════════════════════════════════════════════════════════
# QUANTITY / STRUCTURAL PATTERNS (L3-REQUIRED)
# ═══════════════════════════════════════════════════════════════════════════

# Quantity+unit patterns for IFU component tables
QUANTITY_UNIT_PATTERNS = [
    # "250 μL" / "1.5 mL" / "10 mg" / "50 μg" / "100 ng" / "2 g"
    re.compile(r'(\d+(?:[,.]\d+)?)\s*(μL|mL|mg|μg|ng|g|L|U|μM|mM|M|pmol|nmol|μmol|mmol)', re.IGNORECASE),
    # "1 × 250 μL"
    re.compile(r'(\d+)\s*[×x]\s*(\d+(?:[,.]\d+)?)\s*(μL|mL|mg|μg|ng|g|L)', re.IGNORECASE),
    # "250 μL/tube" or "1.5 mL/vial"
    re.compile(r'(\d+(?:[,.]\d+)?)\s*(μL|mL|mg|μg|ng|g|L)\s*[/]\s*(tube|vial|bottle|strip|plate|bag)', re.IGNORECASE),
    # "100 reactions" / "50 preps" / "24 samples"
    re.compile(r'(\d+(?:[,.]\d+)?)\s*(reactions?|preps?|samples?|tests?|rxns?)', re.IGNORECASE),
    # "10 mM" / "1 M" (concentration)
    re.compile(r'(\d+(?:[,.]\d+)?)\s*(mM|μM|nM|M)\b', re.IGNORECASE),
    # "1 tube" / "2 bottles" / "1 strip" (unit-only)
    re.compile(r'(\d+)\s*(tubes?|bottles?|strips?|plates?|vials?|bags?|columns?|caps?)', re.IGNORECASE),
]

# Catalog number patterns
CATALOG_PATTERNS = [
    re.compile(r'\b([A-Z]{2,4}\d{4,8})\b'),       # "AB1234" / "DC201"
    re.compile(r'\b(\d{6,12})\b'),                   # "123456"
    re.compile(r'\b(\d{3}-\d{3,4}-\d{3,4})\b'),     # "123-456-789"
    re.compile(r'\b(Cat[.#]\s*\d+)\b', re.IGNORECASE),        # "Cat. 12345"
    re.compile(r'\b(Catalog\s*[#№]\s*\d+)\b', re.IGNORECASE), # "Catalog # 12345"
]

# Storage condition patterns (for negative detection)
STORAGE_PATTERNS = [
    re.compile(r'\bstore\s+at\b', re.IGNORECASE),
    re.compile(r'\bstorage\s+(condition|temperature|buffer)\b', re.IGNORECASE),
    re.compile(r'\b[-−]?\d+°C\b'),
    re.compile(r'\bprotect\s+from\s+light\b', re.IGNORECASE),
    re.compile(r'\bshelf\s+life\b', re.IGNORECASE),
]


# ═══════════════════════════════════════════════════════════════════════════
# L1: STRUCTURE DETECTION
# ═══════════════════════════════════════════════════════════════════════════

class StructureDetector:
    """
    L1: Detect document structure characteristics.

    Responsibilities:
    - Detect component table structure (collapsed text, multi-entry layout)
    - Identify table collapse indicators
    - Locate information regions
    - Output: does this content contain a component table?

    Does NOT use vocabulary — only structural signals.
    """

    @staticmethod
    def detect(content: str) -> LayerResult:
        """Run L1 structure detection on content."""
        sig = StructureDetector._extract_signals(content)

        # Score computation
        score = StructureDetector._compute_structure_score(sig)
        activated = score >= 0.25  # threshold for "yes, this has component table structure"

        descriptions = []
        if sig.get("table_collapse_indicators", 0) >= 2:
            descriptions.append(f"Table collapse detected ({sig['table_collapse_indicators']} indicators)")
        if sig.get("quantity_matches", 0) >= 3:
            descriptions.append(f"Multiple quantity patterns ({sig['quantity_matches']} matches)")
        if sig.get("catalog_matches", 0) >= 1:
            descriptions.append(f"Catalog numbers present ({sig['catalog_matches']})")
        if sig.get("line_count", 0) >= 5:
            descriptions.append(f"Multi-line structure ({sig['line_count']} lines)")

        description = "; ".join(descriptions) if descriptions else "No structure signals detected"

        return LayerResult(
            layer="L1",
            activated=activated,
            score=round(score, 4),
            confidence=round(score, 4),
            description=description,
            data={
                "signals": sig,
                "threshold_met": activated,
                "threshold": 0.25,
            },
        )

    @staticmethod
    def _extract_signals(content: str) -> dict[str, Any]:
        """Extract raw structure signals from content."""
        content_lower = content.lower()
        signals = {}

        # Count quantity/unit matches
        qty_matches = 0
        for pat in QUANTITY_UNIT_PATTERNS:
            qty_matches += len(pat.findall(content))
        signals["quantity_matches"] = qty_matches

        # Count catalog number matches
        cat_matches = 0
        for pat in CATALOG_PATTERNS:
            cat_matches += len(pat.findall(content))
        signals["catalog_matches"] = cat_matches

        # Count storage condition mentions (negative signal)
        storage_matches = 0
        for pat in STORAGE_PATTERNS:
            storage_matches += len(pat.findall(content))
        signals["storage_matches"] = storage_matches

        # Table collapse indicators
        tab_indicators = 0
        if re.search(r'\t| {4,}', content):            # column artifacts
            tab_indicators += 1
        if re.search(r'\d+\s*[×x]\s*\d+', content):   # "1 × 250 μL"
            tab_indicators += 1
        if re.search(r'\d+\s*(?:pcs|tubes|strips|vials|bottles)', content_lower):
            tab_indicators += 1
        if re.search(r'[A-Z]{2,4}\d{4,8}', content):  # catalog-like patterns
            tab_indicators += 1
        if re.search(r'\d+(?:[,.]\d+)?\s*(?:μL|mL|mg|μg|ng|g)', content):
            tab_indicators += 1  # quantity+unit pair
        signals["table_collapse_indicators"] = tab_indicators

        # Line count
        lines = [l for l in content.split('\n') if l.strip()]
        signals["line_count"] = len(lines)

        # Word count
        words = content.split()
        signals["word_count"] = len(words)

        # Average line length (indicates collapsed text if very long)
        if lines:
            avg_line_len = sum(len(l) for l in lines) / len(lines)
            signals["avg_line_length"] = round(avg_line_len, 1)
        else:
            signals["avg_line_length"] = 0

        # Quantity density (quantities per word)
        if words:
            signals["quantity_density"] = round(qty_matches / len(words), 4)
        else:
            signals["quantity_density"] = 0.0

        return signals

    @staticmethod
    def _compute_structure_score(sig: dict[str, Any]) -> float:
        """Compute structure detection score from signals."""
        score = 0.0
        checks = 0

        # Quantity matches: strong positive signal
        checks += 1
        qty = sig.get("quantity_matches", 0)
        if qty >= 8:
            score += 1.0
        elif qty >= 5:
            score += 0.8
        elif qty >= 3:
            score += 0.5
        elif qty >= 1:
            score += 0.2

        # Table collapse indicators
        checks += 1
        tab = sig.get("table_collapse_indicators", 0)
        if tab >= 3:
            score += 1.0
        elif tab >= 2:
            score += 0.7
        elif tab >= 1:
            score += 0.35

        # Catalog numbers
        checks += 1
        cat = sig.get("catalog_matches", 0)
        if cat >= 2:
            score += 1.0
        elif cat >= 1:
            score += 0.5

        # Line count (component lists have multiple lines)
        checks += 1
        lines = sig.get("line_count", 0)
        if lines >= 8:
            score += 1.0
        elif lines >= 5:
            score += 0.7
        elif lines >= 3:
            score += 0.4

        # Quantity density (collapsed tables have high density)
        checks += 1
        density = sig.get("quantity_density", 0)
        if density > 0.1:
            score += 1.0
        elif density > 0.05:
            score += 0.7
        elif density > 0.02:
            score += 0.4
        elif density > 0.005:
            score += 0.2

        # Negative signal: storage conditions indicate NOT a component table
        checks += 1
        storage = sig.get("storage_matches", 0)
        if storage >= 3:
            score -= 0.4
        elif storage >= 1:
            score -= 0.2

        return max(0.0, min(1.0, score / checks))


# ═══════════════════════════════════════════════════════════════════════════
# L2: SEMANTIC EVIDENCE LAYER
# ═══════════════════════════════════════════════════════════════════════════

class SemanticEvidenceLayer:
    """
    L2: Semantic evidence matching.

    CRITICAL CONSTRAINT: L2 can only ENHANCE confidence, NEVER determine
    capability. The core judgment comes from L1 (structure) + L3 (extraction).

    Responsibilities:
    - Match known vocabulary terms against content
    - Compute vocabulary density and coverage
    - Provide confidence boost for matched terms
    - Flag missing vocabulary (knowledge gaps)
    """

    @staticmethod
    def evaluate(
        content: str,
        vocabulary: dict[str, list[str]],
    ) -> LayerResult:
        """Evaluate semantic evidence in content."""
        if not vocabulary:
            return LayerResult(
                layer="L2",
                activated=False,
                score=0.0,
                confidence=0.0,
                description="No vocabulary loaded — L2 inactive",
            )

        content_lower = content.lower()

        # Count vocabulary matches by category
        category_hits = {}
        total_terms = 0
        total_hits = 0
        all_matched = []
        all_unmatched = []

        for category, terms in vocabulary.items():
            if not terms:
                continue
            hits = 0
            for term in terms:
                total_terms += 1
                if term.lower() in content_lower:
                    hits += 1
                    all_matched.append({"term": term, "category": category})
                else:
                    all_unmatched.append({"term": term, "category": category})
            category_hits[category] = hits
            total_hits += hits

        # Vocabulary density
        words = content.split()
        if words and total_terms > 0:
            vocab_density = total_hits / len(words)
        else:
            vocab_density = 0.0

        # Coverage ratio: what % of known terms appear?
        if total_terms > 0:
            coverage = total_hits / total_terms
        else:
            coverage = 0.0

        # Sufficiency threshold: L2 is "sufficient" if ≥ 30% of terms matched
        # AND vocabulary density > 0.02
        sufficient = coverage >= 0.3 and vocab_density > 0.02

        # Score: combination of coverage and density
        score = (coverage * 0.6 + min(1.0, vocab_density * 10) * 0.4)

        activated = total_hits > 0

        if total_hits == 0:
            description = f"L2 inactive: 0/{total_terms} vocabulary terms matched"
        elif sufficient:
            description = (
                f"L2 sufficient: {total_hits}/{total_terms} terms matched "
                f"(coverage={coverage:.1%}, density={vocab_density:.3f})"
            )
        else:
            description = (
                f"L2 insufficient: {total_hits}/{total_terms} terms matched "
                f"(coverage={coverage:.1%}, density={vocab_density:.3f})"
            )

        return LayerResult(
            layer="L2",
            activated=activated,
            score=round(score, 4),
            confidence=round(coverage, 4),
            description=description,
            data={
                "total_terms": total_terms,
                "total_hits": total_hits,
                "coverage": round(coverage, 4),
                "vocabulary_density": round(vocab_density, 4),
                "sufficient": sufficient,
                "matched_terms": all_matched[:20],       # top 20
                "unmatched_terms": all_unmatched[:20],   # top 20
                "category_hits": category_hits,
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# L3: STRUCTURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

class StructureExtractor:
    """
    L3: Pure structural extraction.

    Uses QUANTITY+UNIT patterns as anchors — does NOT require vocabulary.
    Works on ANY domain without knowing component names.

    Algorithm:
        1. Find all quantity+unit positions in content
        2. For each quantity position, extract the preceding name segment
        3. Pair name → quantity → unit → catalog_number
        4. This works regardless of domain because it's purely structural

    Core principle: L3 structural understanding > L2 vocabulary knowledge.
    """

    @staticmethod
    def extract(
        content: str,
        vocabulary: Optional[dict[str, list[str]]] = None,
    ) -> tuple[list[dict[str, Any]], LayerResult]:
        """
        Extract components using pure structural analysis.

        Args:
            content: Text content to analyze
            vocabulary: Optional vocabulary for name enhancement (L2 boost)

        Returns:
            (components_list, layer_result)
        """
        # Step 1: Find all quantity anchors
        anchors = StructureExtractor._find_quantity_anchors(content)
        if not anchors:
            return [], LayerResult(
                layer="L3",
                activated=False,
                score=0.0,
                confidence=0.0,
                description="No quantity anchors found — cannot extract structurally",
            )

        # Step 2: For each anchor, extract the preceding name segment
        components = []
        for i, anchor in enumerate(anchors):
            name = StructureExtractor._extract_preceding_name(
                content, anchor, anchors, i
            )
            catalog = StructureExtractor._extract_nearby_catalog(
                content, anchor["start"], anchor["end"]
            )

            comp = {
                "name": name.strip() if name else f"Component_{i+1}",
                "quantity": str(anchor["quantity"]),
                "unit": anchor["unit"],
                "catalog_number": catalog,
                "source_position": anchor["start"],
            }
            # Enhance with vocabulary if available
            if vocabulary:
                enhanced = StructureExtractor._enhance_with_vocabulary(comp, vocabulary)
                comp["name"] = enhanced.get("name", comp["name"])
                comp["category"] = enhanced.get("category", "")

            components.append(comp)

        # Step 3: Deduplicate (same component detected multiple times)
        components = StructureExtractor._deduplicate_components(components)

        # Quality metrics
        complete = sum(
            1 for c in components
            if c.get("name") and c.get("quantity") and c.get("unit")
        )
        quality = complete / len(components) if components else 0.0

        # Confidence: based on extraction quality and anchor count
        confidence = quality * 0.6 + min(1.0, len(anchors) / 10) * 0.4

        return components, LayerResult(
            layer="L3",
            activated=True,
            score=round(quality, 4),
            confidence=round(confidence, 4),
            description=(
                f"L3 extracted {len(components)} components via {len(anchors)} quantity anchors, "
                f"quality={quality:.1%} ({complete}/{len(components)} complete)"
            ),
            data={
                "anchor_count": len(anchors),
                "components_extracted": len(components),
                "complete_extractions": complete,
                "extraction_quality": round(quality, 4),
            },
        )

    @staticmethod
    def _find_quantity_anchors(content: str) -> list[dict[str, Any]]:
        """
        Find all quantity+unit positions in content.

        Returns list of {start, end, quantity, unit, match_text}.
        Deduplicated by position (first match wins).
        """
        positions = []

        for pat in QUANTITY_UNIT_PATTERNS:
            for m in pat.finditer(content):
                start = m.start()
                end = m.end()

                # Check for overlap with existing anchors
                overlap = False
                for existing in positions:
                    if abs(start - existing["start"]) < 15:
                        overlap = True
                        break

                if overlap:
                    continue

                groups = m.groups()
                # Determine quantity and unit from groups
                if len(groups) >= 2:
                    # Try: "1 × 250 μL" → quantity="250", unit="μL"
                    if len(groups) >= 3 and groups[1] and groups[2]:
                        try:
                            float(groups[1])
                            quantity = groups[1]
                            unit = groups[2]
                        except ValueError:
                            quantity = groups[0]
                            unit = groups[1]
                    else:
                        quantity = groups[0]
                        unit = groups[1]
                else:
                    quantity = groups[0]
                    unit = ""

                # Clean unit
                unit = unit.strip().rstrip('/')

                positions.append({
                    "start": start,
                    "end": end,
                    "quantity": quantity,
                    "unit": unit,
                    "match_text": m.group(0),
                })

        # Sort by position
        positions.sort(key=lambda x: x["start"])
        return positions

    @staticmethod
    def _extract_preceding_name(
        content: str,
        anchor: dict[str, Any],
        all_anchors: list[dict[str, Any]],
        anchor_index: int,
    ) -> str:
        """
        Extract the component name that precedes a quantity anchor.

        Strategy:
        - Look backward from the anchor position
        - Find the boundary: previous anchor end OR start of content OR sentence boundary
        - Extract the text segment before the quantity as the name
        - Clean: remove trailing numbers, punctuation, non-name fragments
        """
        anchor_start = anchor["start"]

        # Determine left boundary
        if anchor_index > 0:
            prev_end = all_anchors[anchor_index - 1]["end"]
            # Take text between previous anchor and this anchor
            name_segment = content[prev_end:anchor_start]
        else:
            # First anchor: take text from start up to this anchor
            name_segment = content[:anchor_start]

        name_segment = name_segment.strip()

        # Clean the name segment
        name = StructureExtractor._clean_name_segment(name_segment)

        # If name is too short, expand backward from anchor
        if len(name) < 3 and anchor_index == 0:
            # Take last ~60 chars before anchor as potential name
            start = max(0, anchor_start - 80)
            name_segment = content[start:anchor_start]
            name = StructureExtractor._clean_name_segment(name_segment)

        return name

    @staticmethod
    def _clean_name_segment(segment: str) -> str:
        """Clean a text segment to extract the component name."""
        if not segment:
            return ""

        # Remove trailing punctuation and whitespace
        segment = segment.strip().rstrip('.,;:+-()[]{}\\/ ')

        # Remove leading punctuation
        segment = segment.lstrip('.,;:+-()[]{}\\/ ')

        # If multiple lines, take the last non-empty line (closest to quantity)
        lines = [l.strip() for l in segment.split('\n') if l.strip()]
        if not lines:
            return ""

        # Take the last meaningful line
        name = lines[-1]

        # Remove common non-name artifacts
        # - Trailing numbers not part of name
        name = re.sub(r'\s+\d+\s*$', '', name)
        # - Trailing "x" or "×" (multiplication symbol)
        name = re.sub(r'\s*[×xX]\s*$', '', name)
        # - Trailing catalog numbers
        name = re.sub(r'\s+[A-Z]{2,4}\d{4,8}\s*$', '', name)

        # If name starts with lowercase and is short, might be a fragment
        # Try to include more context
        if len(name) < 5 and len(lines) >= 2:
            name = lines[-2] + " " + name

        return name.strip()

    @staticmethod
    def _extract_nearby_catalog(content: str, anchor_start: int, anchor_end: int) -> str:
        """Extract catalog number near a quantity anchor."""
        # Search in a window around the anchor (±100 chars)
        window_start = max(0, anchor_start - 100)
        window_end = min(len(content), anchor_end + 100)
        window = content[window_start:window_end]

        for pat in CATALOG_PATTERNS:
            match = pat.search(window)
            if match:
                return match.group(0)

        return ""

    @staticmethod
    def _enhance_with_vocabulary(
        comp: dict[str, Any],
        vocabulary: dict[str, list[str]],
    ) -> dict[str, Any]:
        """Enhance extracted component with vocabulary knowledge."""
        name_lower = comp["name"].lower()

        for category, terms in vocabulary.items():
            for term in terms:
                term_lower = term.lower()
                if term_lower in name_lower:
                    # Vocabulary term found in extracted name — enhance
                    comp["name"] = term  # Use canonical name from vocabulary
                    comp["category"] = category
                    return comp

        return comp

    @staticmethod
    def _deduplicate_components(
        components: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove duplicate component entries (same name, same quantity)."""
        seen = set()
        deduped = []
        for comp in components:
            key = (comp.get("name", ""), comp.get("quantity", ""), comp.get("unit", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(comp)
        return deduped


# ═══════════════════════════════════════════════════════════════════════════
# THREE-LAYER RUNTIME ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class ThreeLayerRuntime:
    """
    Unified three-layer capability execution engine.

    Execution chain:
        1. L1 Structure Detection — does content have component table structure?
        2. L2 Semantic Evidence — do we have vocabulary coverage?
        3. L3 Structure Extraction — extract components structurally

    Strategy routing:
        Case A: L1✓ + L2 sufficient → L2-enhanced L3 extraction
        Case B: L1✓ + L2 insufficient → pure L3 structural extraction
        Case C: L1✗ OR L1 ambiguous → reject or uncertain
    """

    def __init__(self, vocabulary: Optional[dict[str, list[str]]] = None):
        """
        Initialize the three-layer runtime.

        Args:
            vocabulary: Optional component vocabulary for L2 enhancement.
                       If None or empty, L2 will be inactive (pure L3 mode).
        """
        self.vocabulary = vocabulary or {}
        self.l1_detector = StructureDetector()
        self.l3_extractor = StructureExtractor()

    def execute(self, content: str, document_id: str = "", slice_id: str = "") -> LayerTrace:
        """
        Execute the full three-layer chain on content.

        Args:
            content: Text content to analyze
            document_id: Source document identifier (traceability)
            slice_id: Source slice identifier (traceability)

        Returns:
            LayerTrace with complete execution trace and results.
        """
        trace = LayerTrace(
            document_id=document_id,
            slice_id=slice_id,
            content_length=len(content),
        )

        # ── L1: Structure Detection ──
        trace.l1_result = self.l1_detector.detect(content)

        if not trace.l1_result.activated:
            # L1 says "no" — content doesn't have component table structure
            trace.strategy_case = "C"
            trace.primary_layer = "L1_STRUCTURE"
            trace.l2_result = LayerResult(
                layer="L2", activated=False, score=0.0, confidence=0.0,
                description="L1 rejected — L2 skipped",
            )
            trace.l3_result = LayerResult(
                layer="L3", activated=False, score=0.0, confidence=0.0,
                description="L1 rejected — L3 skipped",
            )
            return trace

        # ── L2: Semantic Evidence ──
        trace.l2_result = SemanticEvidenceLayer.evaluate(content, self.vocabulary)

        l2_sufficient = trace.l2_result.data.get("sufficient", False)
        trace.l2_sufficient = l2_sufficient

        # ── L3: Structure Extraction ──
        components, trace.l3_result = self.l3_extractor.extract(content, self.vocabulary)
        trace.components = components
        trace.total_extracted = len(components)

        # Compute extraction quality
        if components:
            complete = sum(
                1 for c in components
                if c.get("name") and c.get("quantity") and c.get("unit")
            )
            trace.extraction_quality = complete / len(components)
        else:
            trace.extraction_quality = 0.0

        # ── Strategy Decision ──
        if l2_sufficient:
            # Case A: L2 evidence sufficient → semantic-enhanced extraction
            trace.strategy_case = "A"
            trace.primary_layer = "L2_SEMANTIC"
        elif trace.l3_result.activated and trace.extraction_quality >= 0.3:
            # Case B: L2 insufficient → fallback to pure L3
            trace.strategy_case = "B"
            trace.primary_layer = "L3_STRUCTURAL"
        else:
            # Case C: uncertain — L1 said yes but extraction quality is low
            trace.strategy_case = "C"
            trace.primary_layer = "UNCERTAIN"

        return trace

    @staticmethod
    def trace_to_capability_result(
        trace: LayerTrace,
        capability_id: str = "CAP-COMP-TABLE",
        capability_name: str = "ComponentsTableUnderstanding",
        implementation_version: str = "3.0",
    ) -> dict[str, Any]:
        """
        Convert a LayerTrace to the unified CapabilityResult format.

        This is a bridge function — the actual CapabilityResult dataclass
        is in result.py. This produces the dict that maps to its fields.
        """
        # Compute overall confidence
        if trace.strategy_case == "A":
            # L2-enhanced: confidence = L1 * 0.25 + L2 * 0.35 + L3 * 0.40
            overall_conf = (
                trace.l1_result.confidence * 0.25
                + trace.l2_result.confidence * 0.35
                + trace.l3_result.confidence * 0.40
            )
        elif trace.strategy_case == "B":
            # L3 fallback: confidence = L1 * 0.30 + L3 * 0.70
            overall_conf = (
                trace.l1_result.confidence * 0.30
                + trace.l3_result.confidence * 0.70
            )
        else:
            # Uncertain
            overall_conf = trace.l1_result.confidence * 0.3

        # Build diagnosis
        diagnosis_parts = []
        diagnosis_parts.append(f"L1: {trace.l1_result.description}.")
        diagnosis_parts.append(f"L2: {trace.l2_result.description}.")
        diagnosis_parts.append(f"L3: {trace.l3_result.description}.")
        diagnosis_parts.append(
            f"Strategy: Case {trace.strategy_case} "
            f"(primary={trace.primary_layer})."
        )
        diagnosis_parts.append(
            f"Components: {trace.total_extracted} extracted, "
            f"quality={trace.extraction_quality:.1%}."
        )
        diagnosis_parts.append(f"Overall confidence: {overall_conf:.2f}.")

        return {
            "capability_id": capability_id,
            "capability_name": capability_name,
            "implementation_version": implementation_version,
            "result": {
                "components": trace.components,
                "total_components": trace.total_extracted,
                "extraction_quality": round(trace.extraction_quality, 4),
                "strategy_used": trace.primary_layer,
                "strategy_case": trace.strategy_case,
            },
            "confidence": round(overall_conf, 4),
            "confidence_breakdown": {
                "L1_structure": round(trace.l1_result.confidence, 4),
                "L2_semantic": round(trace.l2_result.confidence, 4),
                "L3_extraction": round(trace.l3_result.confidence, 4),
            },
            "reasoning_layer": trace.primary_layer,
            "strategy_case": trace.strategy_case,
            "layer_contributions": trace.layer_contributions(),
            "diagnosis": " ".join(diagnosis_parts),
            "document_id": trace.document_id,
            "slice_id": trace.slice_id,
            "is_success": trace.strategy_case != "C",
            "warnings": _generate_warnings(trace),
            "errors": [] if trace.strategy_case != "C" else [
                f"Content rejected by L1 (score={trace.l1_result.score:.2f})"
                if not trace.l1_result.activated
                else f"Low extraction quality (quality={trace.extraction_quality:.2f})"
            ],
        }


def _generate_warnings(trace: LayerTrace) -> list[str]:
    """Generate warnings from layer trace."""
    warnings = []
    if trace.strategy_case == "B":
        warnings.append(
            f"L2 vocabulary insufficient ({trace.l2_result.data.get('coverage', 0):.0%} coverage) "
            f"— using pure structural extraction (L3)"
        )
    if trace.strategy_case == "C":
        warnings.append("Content failed all strategies — result is uncertain")
    if trace.l2_result.activated and not trace.l2_sufficient:
        unmatched = trace.l2_result.data.get("unmatched_terms", [])
        if unmatched:
            sample = [u["term"] for u in unmatched[:5]]
            warnings.append(f"Vocabulary gaps detected: {', '.join(sample)}...")
    return warnings


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════

def create_runtime(vocabulary: Optional[dict[str, list[str]]] = None) -> ThreeLayerRuntime:
    """Create a ThreeLayerRuntime with optional vocabulary."""
    return ThreeLayerRuntime(vocabulary=vocabulary)
