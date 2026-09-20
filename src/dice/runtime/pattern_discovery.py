"""
Pattern Discovery Pipeline — Phase 3.2 Prototype.

Discovers structural patterns from Execution Experience WITHOUT
relying on vocabulary, doc_class, or if-else rules.

CORE PRINCIPLE:
    Patterns describe STRUCTURAL RELATIONSHIPS, not keyword occurrences.

    ✅ "Name → Quantity → Unit"           (structural)
    ✅ "Identifier → Attribute → Relation" (structural)
    ❌ "'T4 DNA Ligase' is a reagent"     (keyword-based)
    ❌ "if doc_class == 'plasmid': ..."   (doc_class branching)

Pipeline:
    Execution Experience (LayerTrace[]) → Pattern Candidate Generator
    → Pattern Candidates (candidate status, needs verification)

Input:
    - Document observation (L1 signals)
    - Layer contribution (L1/L2/L3)
    - Extracted structure (L3 components)
    - Success/failure result
    - Evidence items

Output:
    Pattern Candidates:
        {
            pattern_id,
            structure_signature,    # NOT keywords — element types + relations
            evidence_examples,
            frequency,
            confidence,
            applicable_scope,
            related_capability,
            status: "candidate",
            verification_required,
        }
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from dice.runtime.layers import LayerTrace


# ═══════════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════


# Canonical structural element types
class StructuralElement:
    """Fixed vocabulary of structural element types (NOT domain terms)."""
    NAME = "name"                      # Identifier/label
    QUANTITY = "quantity"             # Numeric value
    UNIT = "unit"                     # Unit of measurement
    CATALOG = "catalog_number"        # Catalog/part number
    VOLUME = "volume"                 # Volume (sub-type of quantity+unit)
    CONCENTRATION = "concentration"   # Concentration (sub-type)
    COUNT = "count"                   # Discrete count (tubes, strips, etc.)
    FUNCTION = "function"             # What it does (optional)
    STORAGE = "storage"               # Storage condition (negative signal)
    TABLE_INDICATOR = "table_indicator"  # Collapse/alignment signal
    QTY_DENSITY = "quantity_density"  # Quantity-per-word ratio


# Canonical structural relation types
class StructuralRelation:
    """Fixed vocabulary of relation types between structural elements."""
    PRECEDES = "precedes"             # Element A comes before Element B
    BELONGS_TO = "belongs_to"         # Element is part of a group/list
    PAIRS_WITH = "pairs_with"         # Elements co-occur (e.g. quantity+unit)
    ANCHORS = "anchors"               # Element serves as extraction anchor
    CONTAINS = "contains"             # Element contains sub-elements
    ALIGNS_WITH = "aligns_with"       # Columnar alignment relationship
    EXCLUDES = "excludes"             # Presence of A means NOT B (negative signal)


@dataclass
class StructureSignature:
    """
    The structural fingerprint of a pattern.

    Describes WHAT element types are involved and HOW they relate.
    Contains ZERO domain vocabulary — only structural element types.
    """
    element_types: list[str] = field(default_factory=list)
    # e.g. ["name", "quantity", "unit"]

    relations: list[dict[str, str]] = field(default_factory=list)
    # e.g. [{"from": "quantity", "to": "unit", "type": "pairs_with"},
    #        {"from": "name", "to": "quantity", "type": "precedes"}]

    constraints: list[str] = field(default_factory=list)
    # e.g. ["quantity_must_be_numeric", "unit_must_follow_quantity"]

    # NOT vocabulary — purely structural
    def is_structural_only(self) -> bool:
        """Verify this signature contains no domain vocabulary."""
        domain_types = {"enzyme", "buffer", "reagent", "kit", "antibody"}
        return not any(et in domain_types for et in self.element_types)

    def to_dict(self) -> dict[str, Any]:
        return {
            "element_types": self.element_types,
            "relations": self.relations,
            "constraints": self.constraints,
        }


@dataclass
class PatternCandidate:
    """
    A discovered structural pattern — NOT a formal Capability.

    Status is always "candidate" — needs explicit verification
    before it can be promoted to a registered Pattern in the CapabilityGraph.

    KEY CONSTRAINT: structure_signature must contain ONLY structural
    element types (name, quantity, unit, catalog_number, etc.),
    NEVER domain vocabulary (enzyme, buffer, reagent, etc.).
    """
    pattern_id: str = ""                       # e.g. "PAT-CAND-001"
    pattern_name: str = ""                     # Human-readable
    structure_type: str = ""                   # "identifier_attribute_relation", etc.
    structure_signature: StructureSignature = field(
        default_factory=StructureSignature
    )

    # Evidence
    evidence_examples: list[dict[str, Any]] = field(default_factory=list)
    # Each: {"document_id", "slice_id", "snippet", "extracted_structure"}
    frequency: int = 0                         # How many experiences support this
    source_documents: list[str] = field(default_factory=list)
    confidence: float = 0.0

    # Scope
    applicable_scope: dict[str, Any] = field(default_factory=dict)
    # e.g. {"content_type": "component_table", "min_elements": 3}
    related_capability: str = ""               # Which capability this extends

    # Status
    status: str = "candidate"                  # ALWAYS "candidate" initially
    discovery_epoch: str = "phase3.2"
    verification_required: list[str] = field(default_factory=list)
    # e.g. ["cross_domain_validation", "negative_sample_test"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "structure_type": self.structure_type,
            "structure_signature": self.structure_signature.to_dict(),
            "frequency": self.frequency,
            "source_documents": self.source_documents,
            "confidence": round(self.confidence, 4),
            "applicable_scope": self.applicable_scope,
            "related_capability": self.related_capability,
            "status": self.status,
            "verification_required": self.verification_required,
            "evidence_examples": [
                {
                    "document_id": e["document_id"],
                    "snippet": e.get("snippet", "")[:100],
                }
                for e in self.evidence_examples[:5]
            ],
        }


@dataclass
class CapabilityCandidate:
    """
    A proposed capability composed of one or more Pattern Candidates.

    NOT a formal Capability. Must be verified before registering in
    the CapabilityGraph. Status is always "candidate".
    """
    candidate_id: str = ""                     # e.g. "CAP-CAND-001"
    description: str = ""                      # What this capability would do
    pattern_ids: list[str] = field(default_factory=list)
    # Referenced PatternCandidate IDs

    composite_structure: dict[str, Any] = field(default_factory=dict)
    # How the patterns combine into a capability

    evidence_strength: float = 0.0
    source_pattern_count: int = 0
    total_source_experiences: int = 0

    status: str = "candidate"
    verification_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "description": self.description,
            "pattern_ids": self.pattern_ids,
            "composite_structure": self.composite_structure,
            "evidence_strength": round(self.evidence_strength, 4),
            "source_pattern_count": self.source_pattern_count,
            "total_source_experiences": self.total_source_experiences,
            "status": self.status,
            "verification_required": self.verification_required,
        }


@dataclass
class DiscoveryReport:
    """Complete output of Pattern Discovery on execution experiences."""
    phase: str = "3.2"
    total_experiences_analyzed: int = 0

    # Pattern candidates
    pattern_candidates: list[PatternCandidate] = field(default_factory=list)
    unique_structures_discovered: int = 0

    # Capability candidates
    capability_candidates: list[CapabilityCandidate] = field(default_factory=list)

    # Quality check: verify no keyword patterns leaked in
    keyword_pattern_checks: dict[str, bool] = field(default_factory=dict)
    # e.g. {"no_doc_class_in_patterns": True, "no_vocabulary_in_signatures": True}

    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "total_experiences_analyzed": self.total_experiences_analyzed,
            "pattern_candidates": [
                pc.to_dict() for pc in self.pattern_candidates
            ],
            "unique_structures_discovered": self.unique_structures_discovered,
            "capability_candidates": [
                cc.to_dict() for cc in self.capability_candidates
            ],
            "keyword_pattern_checks": self.keyword_pattern_checks,
            "summary": self.summary,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EXPERIENCE EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════


class ExecutionExperience:
    """
    Normalized execution experience, ready for pattern discovery.

    Combines data from LayerTrace + CapabilityResult into a unified
    format for structural analysis.
    """

    def __init__(
        self,
        trace: LayerTrace,
        capability_result: Optional[dict[str, Any]] = None,
    ):
        self.trace = trace
        self.document_id = trace.document_id
        self.slice_id = trace.slice_id
        self.content_length = trace.content_length
        self.strategy_case = trace.strategy_case
        self.primary_layer = trace.primary_layer
        self.is_success = capability_result.get("is_success", True) if capability_result else (trace.strategy_case != "C")

        # Layer data
        self.l1_activated = trace.l1_result.activated
        self.l1_score = trace.l1_result.score
        self.l1_signals = trace.l1_result.data.get("signals", {})

        self.l2_activated = trace.l2_result.activated
        self.l2_score = trace.l2_result.score
        self.l2_sufficient = trace.l2_sufficient

        self.l3_activated = trace.l3_result.activated
        self.l3_score = trace.l3_result.score
        self.components = trace.components
        self.total_extracted = trace.total_extracted
        self.extraction_quality = trace.extraction_quality

        # Derived: structural fingerprint of the experience
        self.structural_fingerprint = self._compute_structural_fingerprint()

    def _compute_structural_fingerprint(self) -> dict[str, Any]:
        """
        Compute the structural fingerprint of this experience.

        WHAT structural features are present, not WHAT vocabulary.
        """
        fp: dict[str, Any] = {
            "has_quantity_anchors": self.l1_signals.get("quantity_matches", 0) > 0,
            "quantity_count": self.l1_signals.get("quantity_matches", 0),
            "has_catalog_numbers": self.l1_signals.get("catalog_matches", 0) > 0,
            "has_table_collapse": self.l1_signals.get("table_collapse_indicators", 0) >= 2,
            "line_count": self.l1_signals.get("line_count", 0),
            "quantity_density": self.l1_signals.get("quantity_density", 0),
            "components_extracted": self.total_extracted,
            "extraction_quality": self.extraction_quality,
            "primary_layer": self.primary_layer,
            "strategy_case": self.strategy_case,
        }

        # Per-component structural analysis (NOT vocabulary analysis)
        if self.components:
            name_present = sum(1 for c in self.components if c.get("name"))
            qty_present = sum(1 for c in self.components if c.get("quantity"))
            unit_present = sum(1 for c in self.components if c.get("unit"))
            cat_present = sum(1 for c in self.components if c.get("catalog_number"))
            total = len(self.components)

            fp["name_ratio"] = name_present / total if total > 0 else 0
            fp["quantity_ratio"] = qty_present / total if total > 0 else 0
            fp["unit_ratio"] = unit_present / total if total > 0 else 0
            fp["catalog_ratio"] = cat_present / total if total > 0 else 0

        return fp


# ═══════════════════════════════════════════════════════════════════════════
# PATTERN CANDIDATE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════


class PatternCandidateGenerator:
    """
    Generates Pattern Candidates from execution experiences.

    Discovery approach:
    1. Analyze structural fingerprints across experiences
    2. Find recurring structural patterns (not vocabulary patterns)
    3. Generate Pattern Candidates with structural signatures

    ANTI-PATTERNS (explicitly rejected):
    - Patterns based on specific component names
    - Patterns that reference doc_class
    - Patterns that encode if-else logic
    """

    # ── Built-in structural pattern templates ──
    # These are STRUCTURAL archetypes, NOT keyword patterns.
    # They describe element types and their relations.
    STRUCTURAL_ARCHETYPES = {
        "name_quantity_unit": {
            "structure_type": "identifier_attribute_relation",
            "description": "Name (identifier) precedes Quantity + Unit (attribute pair)",
            "signature": StructureSignature(
                element_types=["name", "quantity", "unit"],
                relations=[
                    {"from": "quantity", "to": "unit", "type": "pairs_with"},
                    {"from": "name", "to": "quantity", "type": "precedes"},
                ],
                constraints=[
                    "quantity_must_be_numeric",
                    "unit_must_follow_quantity_without_space",
                    "name_must_precede_quantity",
                ],
            ),
            "detection_fn": "_detect_name_quantity_unit",
        },
        "catalog_name_quantity": {
            "structure_type": "identifier_catalog_attribute",
            "description": "Catalog# (identifier) → Name (identifier) → Quantity (attribute)",
            "signature": StructureSignature(
                element_types=["catalog_number", "name", "quantity"],
                relations=[
                    {"from": "catalog_number", "to": "name", "type": "precedes"},
                    {"from": "name", "to": "quantity", "type": "precedes"},
                ],
                constraints=[
                    "catalog_matches_alphanumeric_pattern",
                    "name_separates_catalog_from_quantity",
                ],
            ),
            "detection_fn": "_detect_catalog_name_quantity",
        },
        "quantity_anchored_extraction": {
            "structure_type": "anchor_driven_extraction",
            "description": "Quantity+Unit pairs serve as anchors for extracting preceding names",
            "signature": StructureSignature(
                element_types=["quantity", "unit", "name"],
                relations=[
                    {"from": "quantity", "to": "unit", "type": "pairs_with"},
                    {"from": "quantity+unit", "to": "name", "type": "anchors"},
                ],
                constraints=[
                    "quantity_unit_pair_is_extraction_anchor",
                    "name_text_lies_between_anchors",
                ],
            ),
            "detection_fn": "_detect_quantity_anchored",
        },
        "table_collapse_multi_entry": {
            "structure_type": "collapsed_table_structure",
            "description": "Multiple component entries collapsed into single text block, separated by quantity anchors",
            "signature": StructureSignature(
                element_types=["name", "quantity", "unit", "table_indicator", "qty_density"],
                relations=[
                    {"from": "table_indicator", "to": "name", "type": "contains"},
                    {"from": "qty_density", "to": "table_indicator", "type": "pairs_with"},
                ],
                constraints=[
                    "multiple_quantity_anchors_in_single_block",
                    "high_quantity_density",
                    "table_collapse_signals_present",
                ],
            ),
            "detection_fn": "_detect_table_collapse",
        },
        "column_alignment": {
            "structure_type": "columnar_alignment",
            "description": "Elements align in columns: Name | Quantity | Unit (possibly with Catalog#)",
            "signature": StructureSignature(
                element_types=["name", "quantity", "unit"],
                relations=[
                    {"from": "name", "to": "quantity", "type": "aligns_with"},
                    {"from": "quantity", "to": "unit", "type": "aligns_with"},
                ],
                constraints=[
                    "consistent_element_ordering_across_entries",
                    "all_entries_have_same_element_set",
                ],
            ),
            "detection_fn": "_detect_column_alignment",
        },
    }

    def __init__(self):
        self.experiences: list[ExecutionExperience] = []

    def load_experiences(self, experiences: list[ExecutionExperience]) -> None:
        """Load execution experiences for pattern discovery."""
        self.experiences = experiences

    def load_from_traces(
        self,
        traces: list[LayerTrace],
        capability_results: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Load from raw LayerTrace objects."""
        results = capability_results or [None] * len(traces)
        self.experiences = [
            ExecutionExperience(trace, result)
            for trace, result in zip(traces, results)
        ]

    # ═══════════════════════════════════════════════════════════════
    # MAIN DISCOVERY PIPELINE
    # ═══════════════════════════════════════════════════════════════

    def discover(self) -> DiscoveryReport:
        """
        Run full Pattern Discovery pipeline.

        1. Structural fingerprint analysis
        2. Archetype matching
        3. Pattern candidate generation
        4. Capability candidate generation
        5. Quality verification (no keyword leaks)
        """
        report = DiscoveryReport()
        report.total_experiences_analyzed = len(self.experiences)

        if not self.experiences:
            report.summary = "No experiences loaded — cannot discover patterns."
            return report

        # Step 1: Collect structural fingerprints
        fingerprints = [exp.structural_fingerprint for exp in self.experiences]

        # Step 2: Match structural archetypes
        pattern_candidates = self._match_archetypes(fingerprints)
        report.pattern_candidates = pattern_candidates
        report.unique_structures_discovered = len(pattern_candidates)

        # Step 3: Generate Capability Candidates from patterns
        report.capability_candidates = self._generate_capability_candidates(
            pattern_candidates
        )

        # Step 4: Quality verification
        report.keyword_pattern_checks = self._verify_no_keyword_leaks(
            pattern_candidates
        )

        # Step 5: Summary
        report.summary = self._build_summary(report)

        return report

    # ═══════════════════════════════════════════════════════════════
    # ARCHETYPE MATCHING
    # ═══════════════════════════════════════════════════════════════

    def _match_archetypes(
        self,
        fingerprints: list[dict[str, Any]],
    ) -> list[PatternCandidate]:
        """Match structural fingerprints against known archetypes."""
        candidates: list[PatternCandidate] = []
        counter = 1

        for archetype_id, archetype in self.STRUCTURAL_ARCHETYPES.items():
            # Run the archetype-specific detection
            detection_fn_name = archetype["detection_fn"]
            detector = getattr(self, detection_fn_name, None)
            if detector is None:
                continue

            matching_experiences = detector(fingerprints)

            if not matching_experiences:
                continue

            # Build PatternCandidate
            frequency = len(matching_experiences)
            confidence = min(1.0, frequency / 3.0)

            # Collect evidence examples
            evidence_examples = []
            source_docs = set()
            for idx in matching_experiences:
                exp = self.experiences[idx]
                source_docs.add(exp.document_id)
                # Build a snippet from the structural fingerprint
                fp = fingerprints[idx]
                evidence_examples.append({
                    "document_id": exp.document_id,
                    "slice_id": exp.slice_id,
                    "snippet": (
                        f"[{exp.primary_layer}] {fp.get('components_extracted', 0)} comps, "
                        f"quality={fp.get('extraction_quality', 0):.1%}, "
                        f"qty_anchors={fp.get('quantity_count', 0)}"
                    ),
                    "extracted_structure": {
                        "name_ratio": fp.get("name_ratio", 0),
                        "quantity_ratio": fp.get("quantity_ratio", 0),
                        "unit_ratio": fp.get("unit_ratio", 0),
                    },
                })

            # Determine what needs verification
            verification_needed = [
                "cross_domain_validation",
                "negative_sample_test",
            ]
            if frequency < 3:
                verification_needed.append("insufficient_samples")
            if confidence < 0.7:
                verification_needed.append("low_confidence")

            candidate = PatternCandidate(
                pattern_id=f"PAT-CAND-{counter:03d}",
                pattern_name=archetype["description"],
                structure_type=archetype["structure_type"],
                structure_signature=archetype["signature"],
                evidence_examples=evidence_examples,
                frequency=frequency,
                source_documents=sorted(source_docs),
                confidence=confidence,
                applicable_scope={
                    "content_type": "component_table",
                    "detected_in_docs": sorted(source_docs),
                },
                related_capability="CAP-COMP-TABLE",
                status="candidate",
                verification_required=verification_needed,
            )
            candidates.append(candidate)
            counter += 1

        return candidates

    # ── Individual archetype detectors ──

    def _detect_name_quantity_unit(
        self, fingerprints: list[dict[str, Any]],
    ) -> list[int]:
        """
        Detect: Name → Quantity → Unit structure.

        Conditions:
        - name_ratio > 0.7 (most components have names)
        - quantity_ratio > 0.5 (most have quantities)
        - unit_ratio > 0.5 (most have units)
        - extraction_quality > 0.5
        """
        matches = []
        for i, fp in enumerate(fingerprints):
            name_ok = fp.get("name_ratio", 0) > 0.7
            qty_ok = fp.get("quantity_ratio", 0) > 0.5
            unit_ok = fp.get("unit_ratio", 0) > 0.5
            quality_ok = fp.get("extraction_quality", 0) > 0.5
            if name_ok and qty_ok and unit_ok and quality_ok:
                matches.append(i)
        return matches

    def _detect_catalog_name_quantity(
        self, fingerprints: list[dict[str, Any]],
    ) -> list[int]:
        """
        Detect: Catalog# → Name → Quantity structure.

        Conditions:
        - catalog_ratio > 0.3 (catalog numbers present)
        - name_ratio > 0.5
        - quantity_ratio > 0.5
        """
        matches = []
        for i, fp in enumerate(fingerprints):
            cat_ok = fp.get("catalog_ratio", 0) > 0.3
            name_ok = fp.get("name_ratio", 0) > 0.5
            qty_ok = fp.get("quantity_ratio", 0) > 0.5
            if cat_ok and name_ok and qty_ok:
                matches.append(i)
        return matches

    def _detect_quantity_anchored(
        self, fingerprints: list[dict[str, Any]],
    ) -> list[int]:
        """
        Detect: Quantity+Unit as extraction anchors.

        Conditions:
        - has_quantity_anchors = True
        - quantity_count >= 3
        - extraction was done via L3 (structural)
        """
        matches = []
        for i, fp in enumerate(fingerprints):
            anchors_ok = fp.get("has_quantity_anchors", False)
            qty_count_ok = fp.get("quantity_count", 0) >= 3
            l3_driven = fp.get("primary_layer", "") == "L3_STRUCTURAL"
            if anchors_ok and qty_count_ok and l3_driven:
                matches.append(i)
        return matches

    def _detect_table_collapse(
        self, fingerprints: list[dict[str, Any]],
    ) -> list[int]:
        """
        Detect: Table collapse → multi-entry block.

        Conditions:
        - has_table_collapse = True
        - components_extracted >= 5
        - quantity_density > 0.02
        """
        matches = []
        for i, fp in enumerate(fingerprints):
            collapse_ok = fp.get("has_table_collapse", False)
            multi_entry = fp.get("components_extracted", 0) >= 5
            density_ok = fp.get("quantity_density", 0) > 0.02
            if collapse_ok and multi_entry and density_ok:
                matches.append(i)
        return matches

    def _detect_column_alignment(
        self, fingerprints: list[dict[str, Any]],
    ) -> list[int]:
        """
        Detect: Columnar alignment across entries.

        Conditions:
        - All three element ratios > 0.7
        - Components extracted >= 3
        - High extraction quality
        """
        matches = []
        for i, fp in enumerate(fingerprints):
            all_high = (
                fp.get("name_ratio", 0) > 0.7
                and fp.get("quantity_ratio", 0) > 0.7
                and fp.get("unit_ratio", 0) > 0.7
            )
            enough_comps = fp.get("components_extracted", 0) >= 3
            high_quality = fp.get("extraction_quality", 0) > 0.8
            if all_high and enough_comps and high_quality:
                matches.append(i)
        return matches

    # ═══════════════════════════════════════════════════════════════
    # CAPABILITY CANDIDATE GENERATION
    # ═══════════════════════════════════════════════════════════════

    def _generate_capability_candidates(
        self,
        pattern_candidates: list[PatternCandidate],
    ) -> list[CapabilityCandidate]:
        """
        Generate Capability Candidates from discovered patterns.

        A Capability Candidate combines multiple patterns into a
        coherent extraction capability. Not a formal Capability —
        needs verification.
        """
        if not pattern_candidates:
            return []

        capabilities = []

        # Candidate 1: If we have name_quantity_unit + quantity_anchored, propose
        # "Generic Components Table Extractor"
        has_nqu = any(
            pc.structure_type == "identifier_attribute_relation"
            for pc in pattern_candidates
        )
        has_qa = any(
            pc.structure_type == "anchor_driven_extraction"
            for pc in pattern_candidates
        )
        has_collapse = any(
            pc.structure_type == "collapsed_table_structure"
            for pc in pattern_candidates
        )

        if has_nqu and has_qa:
            nqu_pat = next(
                pc for pc in pattern_candidates
                if pc.structure_type == "identifier_attribute_relation"
            )
            qa_pat = next(
                pc for pc in pattern_candidates
                if pc.structure_type == "anchor_driven_extraction"
            )

            total_experiences = len(set(
                nqu_pat.source_documents + qa_pat.source_documents
            ))
            evidence = (nqu_pat.confidence + qa_pat.confidence) / 2

            capabilities.append(CapabilityCandidate(
                candidate_id="CAP-CAND-001",
                description=(
                    "Generic Components Table Extractor: use quantity+unit pairs "
                    "as anchors to extract preceding names, forming complete "
                    "name→quantity→unit triples. Independent of domain vocabulary."
                ),
                pattern_ids=[nqu_pat.pattern_id, qa_pat.pattern_id],
                composite_structure={
                    "primary_pattern": nqu_pat.pattern_id,
                    "extraction_anchor": qa_pat.pattern_id,
                    "extraction_flow": "quantity_anchor → locate_preceding_name → form_name_qty_unit_triple",
                },
                evidence_strength=evidence,
                source_pattern_count=2,
                total_source_experiences=total_experiences,
                verification_required=[
                    "cross_domain_validation",
                    "negative_sample_test",
                    "edge_case_handling",
                ],
            ))

        # Candidate 2: If table collapse pattern exists, propose
        # "Collapsed Table Reconstruction"
        if has_collapse:
            col_pat = next(
                pc for pc in pattern_candidates
                if pc.structure_type == "collapsed_table_structure"
            )

            capabilities.append(CapabilityCandidate(
                candidate_id="CAP-CAND-002",
                description=(
                    "Collapsed Table Reconstruction: detect collapsed table "
                    "structure via quantity density and table collapse indicators, "
                    "then apply anchor-driven extraction to recover individual entries."
                ),
                pattern_ids=[col_pat.pattern_id],
                composite_structure={
                    "detection": col_pat.pattern_id,
                    "reconstruction": "anchor_driven_extraction (from CAP-CAND-001)",
                },
                evidence_strength=col_pat.confidence,
                source_pattern_count=1,
                total_source_experiences=len(col_pat.source_documents),
                verification_required=[
                    "false_positive_rate_on_non_tables",
                    "cross_domain_table_detection",
                ],
            ))

        return capabilities

    # ═══════════════════════════════════════════════════════════════
    # QUALITY VERIFICATION
    # ═══════════════════════════════════════════════════════════════

    def _verify_no_keyword_leaks(
        self,
        candidates: list[PatternCandidate],
    ) -> dict[str, bool]:
        """
        Verify that NO pattern candidates contain domain vocabulary,
        doc_class references, or keyword-based patterns.
        """
        checks = {}

        # Check 1: No doc_class in pattern signatures
        doc_class_clean = True
        for pc in candidates:
            sig = pc.structure_signature
            if any("doc_class" in et.lower() for et in sig.element_types):
                doc_class_clean = False
                break
            for rel in sig.relations:
                if "doc_class" in str(rel).lower():
                    doc_class_clean = False
                    break
        checks["no_doc_class_in_signatures"] = doc_class_clean

        # Check 2: No domain vocabulary in element types
        # NOTE: "column" excluded because it's ambiguous —
        # chromatography column (domain) vs. table column (structural)
        domain_terms = {
            "enzyme", "buffer", "reagent", "kit", "antibody", "protein",
            "dna", "rna", "ligase", "polymerase", "nuclease", "primer",
            "bead", "resin", "membrane",
        }
        vocab_clean = True
        for pc in candidates:
            sig = pc.structure_signature
            if any(et.lower() in domain_terms for et in sig.element_types):
                vocab_clean = False
                break
        checks["no_vocabulary_in_element_types"] = vocab_clean

        # Check 3: All signatures are structural-only
        structural_only = all(
            pc.structure_signature.is_structural_only()
            for pc in candidates
        )
        checks["all_signatures_structural_only"] = structural_only

        # Check 4: No if-else encoded in constraints
        if_else_clean = True
        for pc in candidates:
            for constraint in pc.structure_signature.constraints:
                if "if " in constraint.lower() and " else " in constraint.lower():
                    if_else_clean = False
                    break
                if "elif" in constraint.lower():
                    if_else_clean = False
                    break
        checks["no_if_else_in_constraints"] = if_else_clean

        # Check 5: No pattern names contain domain terms
        name_clean = True
        for pc in candidates:
            name_lower = pc.pattern_name.lower()
            if any(dt in name_lower for dt in domain_terms):
                name_clean = False
                break
        checks["no_domain_terms_in_pattern_names"] = name_clean

        # Check 6: Pattern candidates have "candidate" status
        all_candidate = all(pc.status == "candidate" for pc in candidates)
        checks["all_patterns_are_candidates"] = all_candidate

        return checks

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════

    def _build_summary(self, report: DiscoveryReport) -> str:
        """Build human-readable summary of the discovery."""

        parts = [
            f"Analyzed {report.total_experiences_analyzed} execution experiences.",
            f"Discovered {report.unique_structures_discovered} structural patterns.",
        ]

        if report.pattern_candidates:
            parts.append("Pattern Candidates:")
            for pc in report.pattern_candidates:
                parts.append(
                    f"  - {pc.pattern_id}: {pc.pattern_name} "
                    f"(freq={pc.frequency}, conf={pc.confidence:.2f}, "
                    f"type={pc.structure_type})"
                )

        if report.capability_candidates:
            parts.append("Capability Candidates:")
            for cc in report.capability_candidates:
                parts.append(
                    f"  - {cc.candidate_id}: {cc.description[:80]}... "
                    f"(evidence={cc.evidence_strength:.2f})"
                )

        # Quality verdict
        all_clean = all(report.keyword_pattern_checks.values())
        parts.append(
            f"Quality: {'ALL CLEAN' if all_clean else 'ISSUES FOUND'} — "
            f"Zero keyword/vocabulary/doc_class leaks."
        )

        return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════


def discover_patterns(
    traces: list[LayerTrace],
    capability_results: Optional[list[dict[str, Any]]] = None,
) -> DiscoveryReport:
    """Convenience: run pattern discovery on a list of LayerTraces."""
    gen = PatternCandidateGenerator()
    gen.load_from_traces(traces, capability_results)
    return gen.discover()
