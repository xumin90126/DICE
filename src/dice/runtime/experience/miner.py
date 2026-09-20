"""
Experience Miner — extracts reusable knowledge from historical success cases.

Three mining operations:
    A. Evidence Pattern Mining:
       Extracts structured evidence patterns from successful extractions.
       NOT just vocabulary words — captures semantic_type, context,
       surrounding_pattern (the full context package).

    B. Recognition Pattern Mining:
       Discovers structural regularities across documents.
       e.g. "component tables consistently have name → quantity → catalog# structure"

    C. Failure Contrast Mining:
       Compares success vs failure cases to identify MISSING evidence.
       What vocabulary, patterns, or signals do failures lack?

Key constraint: Mining output is DESCRIPTIVE knowledge (patterns, vocabulary),
NOT procedural rules (no if-else, no doc_class branching).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

from dice.runtime.experience.importer import ExperienceCase, ExperienceImporter


# ═══════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class EvidencePattern:
    """
    A mined evidence pattern — semantic understanding of vocabulary
    in context.

    Example: "T4 DNA Ligase" is not just a string; it's:
        semantic_type: reagent_name (enzyme)
        context: component_table
        surrounding_pattern:
            precedes: ["quantity", "catalog_number"]
            structural_role: "key_reagent"
    """
    pattern_id: str = ""
    semantic_type: str = ""            # e.g. "reagent_name", "buffer_name", "kit_name"
    context: str = "component_table"   # where this pattern appears
    token: str = ""                    # the actual vocabulary token
    category: str = ""                 # vocabulary category
    surrounding_pattern: dict[str, Any] = field(default_factory=dict)
    # e.g. {"precedes": ["quantity"], "follows": ["step_number"], "peers": [...]}

    # Evidence strength
    source_count: int = 0              # how many documents support this
    source_documents: list[str] = field(default_factory=list)
    confidence: float = 0.0

    # Discovery metadata
    discovered_from: str = ""          # "success_cases" | "failure_contrast" | "cross_doc"
    notes: str = ""


@dataclass
class RecognitionPattern:
    """
    A mined structural recognition pattern.

    Describes WHAT a component table looks like structurally,
    discovered by comparing multiple successful cases.
    """
    pattern_id: str = ""
    pattern_name: str = ""
    pattern_type: str = ""             # "column_structure", "vocabulary_density", "quantity_pairing"
    description: str = ""

    # Structural constraints (discovered, not hardcoded)
    constraints: list[str] = field(default_factory=list)
    # e.g. ["has_name_column", "has_quantity_column", "has_identifier_column"]

    # Content characteristics
    typical_vocabulary_categories: list[str] = field(default_factory=list)
    typical_density_range: tuple[float, float] = (0.0, 0.0)
    typical_entry_count_range: tuple[int, int] = (0, 0)

    # Evidence
    source_count: int = 0
    source_documents: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class FailureContrast:
    """
    Diagnostic comparison between success and failure cases.

    Answers: what evidence do success cases have that failure cases lack?
    """
    contrast_id: str = ""
    failure_document_id: str = ""
    failure_case_id: str = ""

    # What the failure lacks
    missing_vocabulary: list[str] = field(default_factory=list)
    # e.g. ["T4 DNA Ligase", "DTT", "PMSF"]

    missing_vocabulary_categories: list[str] = field(default_factory=list)
    # e.g. ["biochemical_reagents"]

    # Structural differences
    structure_diff: dict[str, Any] = field(default_factory=dict)
    # e.g. {"success_has": ["quantity_column"], "failure_has": ["name_only"]}

    # Comparison metrics
    success_avg_vocab_hits: float = 0.0
    failure_vocab_hits: float = 0.0
    vocab_coverage_ratio: float = 0.0   # failure / success average

    # Root cause
    root_cause: str = ""               # "vocabulary_gap" | "structural_mismatch" | "density_below_threshold"
    recommendation: str = ""

    confidence: float = 0.0


@dataclass
class MiningResult:
    """Complete output of Experience Mining on a set of cases."""
    capability_id: str = "CAP-COMP-TABLE"

    # A. Evidence Patterns
    evidence_patterns: list[EvidencePattern] = field(default_factory=list)
    new_evidence_pattern_count: int = 0

    # B. Recognition Patterns
    recognition_patterns: list[RecognitionPattern] = field(default_factory=list)
    new_recognition_pattern_count: int = 0

    # C. Failure Contrasts
    failure_contrasts: list[FailureContrast] = field(default_factory=list)

    # Summary
    total_cases_analyzed: int = 0
    success_cases: int = 0
    partial_cases: int = 0
    failure_cases: int = 0

    # Knowledge gap analysis
    vocabulary_gaps: dict[str, list[str]] = field(default_factory=dict)
    # category → missing terms
    missing_categories: list[str] = field(default_factory=list)
    knowledge_deficit_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "total_cases_analyzed": self.total_cases_analyzed,
            "success_cases": self.success_cases,
            "partial_cases": self.partial_cases,
            "failure_cases": self.failure_cases,
            "new_evidence_pattern_count": self.new_evidence_pattern_count,
            "new_recognition_pattern_count": self.new_recognition_pattern_count,
            "failure_contrast_count": len(self.failure_contrasts),
            "vocabulary_gaps": self.vocabulary_gaps,
            "missing_categories": self.missing_categories,
            "knowledge_deficit_summary": self.knowledge_deficit_summary,
            "evidence_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "semantic_type": p.semantic_type,
                    "token": p.token,
                    "category": p.category,
                    "source_count": p.source_count,
                    "confidence": p.confidence,
                }
                for p in self.evidence_patterns
            ],
            "recognition_patterns": [
                {
                    "pattern_id": rp.pattern_id,
                    "pattern_name": rp.pattern_name,
                    "pattern_type": rp.pattern_type,
                    "constraints": rp.constraints,
                    "source_count": rp.source_count,
                    "confidence": rp.confidence,
                }
                for rp in self.recognition_patterns
            ],
            "failure_contrasts": [
                {
                    "failure_document_id": fc.failure_document_id,
                    "missing_vocabulary": fc.missing_vocabulary[:10],
                    "root_cause": fc.root_cause,
                    "recommendation": fc.recommendation,
                }
                for fc in self.failure_contrasts
            ],
        }


# ═══════════════════════════════════════════════════════════════════
# MINER
# ═══════════════════════════════════════════════════════════════════

class ExperienceMiner:
    """
    Analyzes historical experience cases to extract reusable knowledge.

    Three-stage pipeline:
        1. Mine Evidence Patterns from success cases
        2. Mine Recognition Patterns from structural analysis
        3. Contrast failures against successes to find gaps
    """

    # ── Built-in vocabulary for context analysis ──
    _SEMANTIC_TYPE_PATTERNS = {
        "enzyme_reagent": [
            r"(?i)\b\w+ase\b",             # RNase, DNase, Proteinase, Lysozyme
            r"(?i)\b\w+polymerase\b",      # DNA Polymerase, Taq Polymerase
            r"(?i)\b\w+ligase\b",          # T4 DNA Ligase
            r"(?i)\b\w+transcriptase\b",   # Reverse Transcriptase
            r"(?i)\b\w+nuclease\b",        # Endonuclease, Exonuclease
            r"(?i)\b\w+inhibit\w+\b",     # RNase Inhibitor, Protease Inhibitor
        ],
        "buffer_solution": [
            r"(?i)\b\w*buffer\b",
            r"(?i)\b\w*solution\b",
            r"(?i)\bTE\b|\bTAE\b|\bTBE\b|\bPBS\b",
            r"(?i)\bTris[-\s]?HCl\b",
        ],
        "nucleic_acid": [
            r"(?i)\b[cdg]?DNA\b",
            r"(?i)\bRNA\b",
            r"(?i)\b\d*mer\b",            # primer, 20-mer
            r"(?i)\bprimer\b|\bprobe\b|\boligo\b",
            r"(?i)\b\d*NTP\b",            # dNTP, dATP, dCTP, dGTP, dTTP
            r"(?i)\badapter\b|\bindex\b|\bbarcode\b",
        ],
        "purification_media": [
            r"(?i)\bmagnetic\s*bead",
            r"(?i)\b\w*column\b",
            r"(?i)\b\w*membrane\b",
            r"(?i)\b\w*resin\b",
            r"(?i)\bdynabead",
        ],
        "consumable": [
            r"(?i)\btube\b|\bplate\b|\bstrip\b",
            r"(?i)\btip\b|\bglove\b|\bsyringe\b",
        ],
        "instrument": [
            r"(?i)\b\w*cycler\b",
            r"(?i)\bcentrifuge\b|\bvortex\b|\bshaker\b",
            r"(?i)\b\w*meter\b|\bqubit\b|\bbioanalyzer\b",
        ],
        "chemical": [
            r"(?i)\bethanol\b|\bisopropanol\b",
            r"(?i)\bDTT\b|\bDMSO\b|\bEDTA\b",
            r"(?i)\bPMSF\b|\bSDS\b",
        ],
    }

    def __init__(self, importer: ExperienceImporter):
        self.importer = importer
        self.current_vocabulary: dict[str, list[str]] = {}

    def set_vocabulary(self, vocab: dict[str, list[str]]) -> None:
        """Set the current vocabulary for gap analysis."""
        self.current_vocabulary = vocab

    # ═══════════════════════════════════════════════════════════
    # MAIN MINING PIPELINE
    # ═══════════════════════════════════════════════════════════

    def mine(
        self,
        vocabulary: Optional[dict[str, list[str]]] = None,
    ) -> MiningResult:
        """
        Run full three-stage mining pipeline.

        Args:
            vocabulary: Current capability vocabulary (for gap analysis).
                        If not provided, uses self.current_vocabulary.
        """
        if vocabulary is not None:
            self.set_vocabulary(vocabulary)

        result = MiningResult()

        cases = self.importer.cases
        result.total_cases_analyzed = len(cases)
        result.success_cases = len(self.importer.get_success_cases())
        result.partial_cases = len(self.importer.get_partial_cases())
        result.failure_cases = len(self.importer.get_failure_cases())

        # Stage A: Evidence Pattern Mining
        result.evidence_patterns = self._mine_evidence_patterns(cases)
        result.new_evidence_pattern_count = len(result.evidence_patterns)

        # Stage B: Recognition Pattern Mining
        result.recognition_patterns = self._mine_recognition_patterns(cases)
        result.new_recognition_pattern_count = len(result.recognition_patterns)

        # Stage C: Failure Contrast
        result.failure_contrasts = self._mine_failure_contrasts()
        result.vocabulary_gaps = self._identify_vocabulary_gaps(cases)
        result.missing_categories = list(result.vocabulary_gaps.keys())
        result.knowledge_deficit_summary = self._summarize_deficits(result)

        return result

    # ═══════════════════════════════════════════════════════════
    # STAGE A: EVIDENCE PATTERN MINING
    # ═══════════════════════════════════════════════════════════

    def _mine_evidence_patterns(
        self, cases: list[ExperienceCase],
    ) -> list[EvidencePattern]:
        """
        Extract Evidence Patterns from success cases.

        For each extracted component in each success case:
        1. Classify its semantic type
        2. Analyze its context (what surrounds it)
        3. Build a structured evidence pattern
        """
        patterns: dict[str, EvidencePattern] = {}  # token → pattern

        for case in cases:
            if case.category not in ("success", "partial"):
                continue

            components = case.extraction_result.get("components", [])
            for comp in components:
                name = comp.get("name", "")
                if not name:
                    continue

                # Determine semantic type
                semantic_type = self._classify_semantic_type(name)

                # Determine category
                category = self._find_category(name, self.current_vocabulary)
                if not category:
                    category = semantic_type  # use semantic type as fallback category

                # Analyze surrounding context
                surrounding = self._analyze_surrounding(comp, components)

                key = name.lower()
                if key in patterns:
                    # Update existing pattern
                    pat = patterns[key]
                    pat.source_count += 1
                    if case.document_id not in pat.source_documents:
                        pat.source_documents.append(case.document_id)
                    # Merge surrounding
                    for k, v in surrounding.items():
                        if k not in pat.surrounding_pattern:
                            pat.surrounding_pattern[k] = v
                    pat.confidence = min(1.0, pat.source_count / 3.0)
                else:
                    pat = EvidencePattern(
                        pattern_id=f"EVD-PAT-{name.replace(' ', '-').upper()[:30]}",
                        semantic_type=semantic_type,
                        context="component_table",
                        token=name,
                        category=category,
                        surrounding_pattern=surrounding,
                        source_count=1,
                        source_documents=[case.document_id],
                        confidence=0.33,  # 1/3 for single source
                        discovered_from="success_cases",
                    )
                    patterns[key] = pat

        return sorted(patterns.values(), key=lambda p: p.source_count, reverse=True)

    def _classify_semantic_type(self, token: str) -> str:
        """Classify a token into a semantic type using regex patterns."""
        for sem_type, patterns in self._SEMANTIC_TYPE_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, token):
                    return sem_type
        return "unknown"

    def _find_category(
        self, token: str, vocabulary: dict[str, list[str]],
    ) -> str:
        """Find which vocabulary category a token belongs to."""
        token_lower = token.lower()
        for category, terms in vocabulary.items():
            for term in terms:
                if term.lower() == token_lower:
                    return category
        return ""

    def _analyze_surrounding(
        self, comp: dict[str, Any], all_components: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze what surrounds this component in the list."""
        surrounding: dict[str, Any] = {}

        # Check if quantity follows
        if comp.get("quantity"):
            surrounding["has_quantity"] = True

        # Check if catalog number follows
        if comp.get("catalog_number"):
            surrounding["has_catalog_number"] = True

        # Check if unit is present
        if comp.get("unit"):
            surrounding["has_unit"] = True
            surrounding["unit"] = comp.get("unit")

        # Check position in list
        idx = next(
            (i for i, c in enumerate(all_components)
             if c.get("name") == comp.get("name")),
            -1,
        )
        if idx == 0:
            surrounding["position"] = "first"
        elif idx == len(all_components) - 1:
            surrounding["position"] = "last"
        else:
            surrounding["position"] = "middle"

        return surrounding

    # ═══════════════════════════════════════════════════════════
    # STAGE B: RECOGNITION PATTERN MINING
    # ═══════════════════════════════════════════════════════════

    def _mine_recognition_patterns(
        self, cases: list[ExperienceCase],
    ) -> list[RecognitionPattern]:
        """
        Mine structural Recognition Patterns across cases.

        What structural regularities do component tables exhibit?
        """
        patterns = []

        success_cases = [c for c in cases if c.category in ("success", "partial")]
        if not success_cases:
            return patterns

        # Pattern 1: Column structure analysis
        col_pattern = self._mine_column_structure(success_cases)
        if col_pattern:
            patterns.append(col_pattern)

        # Pattern 2: Vocabulary density analysis
        density_pattern = self._mine_density_pattern(success_cases)
        if density_pattern:
            patterns.append(density_pattern)

        # Pattern 3: Quantity pairing consistency
        qty_pattern = self._mine_quantity_pairing_pattern(success_cases)
        if qty_pattern:
            patterns.append(qty_pattern)

        return patterns

    def _mine_column_structure(
        self, cases: list[ExperienceCase],
    ) -> Optional[RecognitionPattern]:
        """Mine column structure: what columns do component tables have?"""
        all_components = []
        for case in cases:
            comps = case.extraction_result.get("components", [])
            all_components.extend(comps)

        if not all_components:
            return None

        has_name = sum(1 for c in all_components if c.get("name"))
        has_quantity = sum(1 for c in all_components if c.get("quantity"))
        has_catalog = sum(1 for c in all_components if c.get("catalog_number"))
        has_unit = sum(1 for c in all_components if c.get("unit"))
        total = len(all_components)

        constraints = []
        if has_name / total > 0.8:
            constraints.append("has_name_column")
        if has_quantity / total > 0.5:
            constraints.append("has_quantity_column")
        if has_catalog / total > 0.3:
            constraints.append("has_identifier_column")

        source_docs = list(set(c.document_id for c in cases))

        return RecognitionPattern(
            pattern_id="REC-PAT-COLUMN-STRUCTURE",
            pattern_name="Component Table Column Structure",
            pattern_type="column_structure",
            description="Component tables consistently have name, quantity, and identifier columns",
            constraints=constraints,
            typical_vocabulary_categories=["biochemical_reagents", "buffers_solutions", "consumables"],
            source_count=len(cases),
            source_documents=source_docs,
            confidence=min(1.0, len(cases) / 3.0),
        )

    def _mine_density_pattern(
        self, cases: list[ExperienceCase],
    ) -> Optional[RecognitionPattern]:
        """Mine vocabulary density patterns."""
        densities = []
        for case in cases:
            words = case.content.split()
            if not words:
                continue
            # Count vocab hits in content
            vocab_hits = 0
            content_lower = case.content.lower()
            for terms in self.current_vocabulary.values():
                for term in terms:
                    if term.lower() in content_lower:
                        vocab_hits += 1
            if words:
                densities.append(vocab_hits / len(words))

        if not densities:
            return None

        return RecognitionPattern(
            pattern_id="REC-PAT-VOCAB-DENSITY",
            pattern_name="Component Vocabulary Density Range",
            pattern_type="vocabulary_density",
            description="Component sections have 5-50% vocabulary density",
            constraints=["vocabulary_density > 0.05"],
            typical_density_range=(min(densities), max(densities)),
            typical_entry_count_range=(3, 20),
            source_count=len(cases),
            source_documents=list(set(c.document_id for c in cases)),
            confidence=min(1.0, len(cases) / 3.0),
        )

    def _mine_quantity_pairing_pattern(
        self, cases: list[ExperienceCase],
    ) -> Optional[RecognitionPattern]:
        """Mine quantity pairing consistency."""
        pairing_ratios = []
        for case in cases:
            content_lower = case.content.lower()
            # Count quantity patterns
            qty_count = 0
            for pat in [
                r"\d+\s*(?:×|x)\s*\d+",
                r"\d+\s*(?:μL|mL|mg|μg|ng|g|L)\b",
                r"\d+\s*(?:pcs|pieces?|tubes?|strips?)\b",
            ]:
                qty_count += len(re.findall(pat, content_lower, re.IGNORECASE))

            # Count component names
            comp_count = len(case.extraction_result.get("components", []))
            if comp_count > 0:
                pairing_ratios.append(qty_count / comp_count)

        if not pairing_ratios:
            return None

        avg_ratio = sum(pairing_ratios) / len(pairing_ratios)

        return RecognitionPattern(
            pattern_id="REC-PAT-QUANTITY-PAIRING",
            pattern_name="Component-Quantity Pairing Consistency",
            pattern_type="quantity_pairing",
            description=f"Components consistently paired with quantities (avg {avg_ratio:.1f} qty/comp)",
            constraints=["quantity_follows_name", "ratio > 0.6"],
            source_count=len(cases),
            source_documents=list(set(c.document_id for c in cases)),
            confidence=min(1.0, avg_ratio),
        )

    # ═══════════════════════════════════════════════════════════
    # STAGE C: FAILURE CONTRAST
    # ═══════════════════════════════════════════════════════════

    def _mine_failure_contrasts(self) -> list[FailureContrast]:
        """
        Compare failure cases against success cases to find gaps.

        For each failure: what vocabulary/patterns do success cases have
        that this failure lacks?
        """
        contrasts = []

        success_cases = self.importer.get_success_cases()
        failure_cases = self.importer.get_failure_cases() + self.importer.get_partial_cases()

        if not failure_cases or not success_cases:
            return contrasts

        # Compute success case statistics
        success_vocab_all: Counter = Counter()
        success_vocab_categories: Counter = Counter()
        for case in success_cases:
            content_lower = case.content.lower()
            for category, terms in self.current_vocabulary.items():
                for term in terms:
                    if term.lower() in content_lower:
                        success_vocab_all[term] += 1
                        success_vocab_categories[category] += 1

        success_avg_vocab_hits = (
            sum(success_vocab_all.values()) / len(success_cases)
            if success_cases else 0.0
        )

        # Analyze each failure
        for failure in failure_cases:
            content_lower = failure.content.lower()

            # Find vocabulary that exists in success average but missing here
            missing_terms = []
            missing_cats: Counter = Counter()
            for term, count in success_vocab_all.items():
                if count >= 2 and term.lower() not in content_lower:  # at least 2 success cases
                    missing_terms.append(term)
                    # Find category
                    for cat, terms in self.current_vocabulary.items():
                        if term in terms:
                            missing_cats[cat] += 1
                            break

            # Count vocab hits in failure
            failure_hits = 0
            for terms in self.current_vocabulary.values():
                for term in terms:
                    if term.lower() in content_lower:
                        failure_hits += 1

            # Determine root cause
            if missing_terms:
                root_cause = "vocabulary_gap"
                recommendation = (
                    f"Add {len(missing_terms)} missing terms to vocabulary: "
                    f"{', '.join(missing_terms[:5])}..."
                )
            elif failure_hits < success_avg_vocab_hits * 0.3:
                root_cause = "density_below_threshold"
                recommendation = "Content has format that doesn't match current patterns"
            else:
                root_cause = "structural_mismatch"
                recommendation = "Content structure differs from known patterns"

            contrast = FailureContrast(
                contrast_id=f"CONTRAST-{failure.document_id}",
                failure_document_id=failure.document_id,
                failure_case_id=failure.case_id,
                missing_vocabulary=missing_terms,
                missing_vocabulary_categories=list(missing_cats.keys()),
                success_avg_vocab_hits=success_avg_vocab_hits,
                failure_vocab_hits=failure_hits,
                vocab_coverage_ratio=(
                    failure_hits / success_avg_vocab_hits
                    if success_avg_vocab_hits > 0 else 0.0
                ),
                root_cause=root_cause,
                recommendation=recommendation,
                confidence=0.7 if missing_terms else 0.3,
            )
            contrasts.append(contrast)

        return contrasts

    # ═══════════════════════════════════════════════════════════
    # VOCABULARY GAP ANALYSIS
    # ═══════════════════════════════════════════════════════════

    def _identify_vocabulary_gaps(
        self, cases: list[ExperienceCase],
    ) -> dict[str, list[str]]:
        """
        Identify vocabulary terms that appear in ground truth but
        are NOT in the current vocabulary.
        """
        existing_terms: set[str] = set()
        for terms in self.current_vocabulary.values():
            for term in terms:
                existing_terms.add(term.lower())

        gaps: dict[str, list[str]] = {}

        for case in cases:
            for comp in case.ground_truth:
                name = comp.get("name", "")
                if not name:
                    continue
                if name.lower() not in existing_terms:
                    sem_type = self._classify_semantic_type(name)
                    gaps.setdefault(sem_type, [])
                    if name not in gaps[sem_type]:
                        gaps[sem_type].append(name)
                        existing_terms.add(name.lower())  # avoid duplicates

        return gaps

    def _summarize_deficits(self, result: MiningResult) -> str:
        """Generate human-readable summary of knowledge deficits."""
        parts = []

        if result.failure_cases > 0:
            parts.append(
                f"{result.failure_cases} case(s) failed or partial out of "
                f"{result.total_cases_analyzed} total."
            )

        if result.vocabulary_gaps:
            total_gaps = sum(len(v) for v in result.vocabulary_gaps.values())
            parts.append(
                f"Found {total_gaps} vocabulary terms missing from capability "
                f"across {len(result.vocabulary_gaps)} semantic categories: "
                + ", ".join(
                    f"{cat}({len(terms)})"
                    for cat, terms in sorted(result.vocabulary_gaps.items())
                )
            )

        # Classify root causes
        vocab_failures = sum(
            1 for fc in result.failure_contrasts
            if fc.root_cause == "vocabulary_gap"
        )
        struct_failures = sum(
            1 for fc in result.failure_contrasts
            if fc.root_cause == "structural_mismatch"
        )
        density_failures = sum(
            1 for fc in result.failure_contrasts
            if fc.root_cause == "density_below_threshold"
        )

        parts.append(
            f"Root causes: vocabulary_gap={vocab_failures}, "
            f"structural_mismatch={struct_failures}, "
            f"density_below_threshold={density_failures}."
        )

        if result.new_evidence_pattern_count > 0:
            parts.append(
                f"Mined {result.new_evidence_pattern_count} evidence patterns "
                f"from success cases."
            )

        return " ".join(parts)
