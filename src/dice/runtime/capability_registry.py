from __future__ import annotations

"""
[DEPRECATED — Phase 4.0] Capability registration moved to dice/bootstrap.py.

This file is preserved for backward compatibility with Phase 1-3 code.
New code should use:
    from dice.registry import CapabilityRegistry
    from dice.bootstrap import bootstrap_registry

The ExperienceGraph-based registration function (register_components_table_capability)
is retained but should be replaced by bootstrap_patterns_to_graph().

KEY DESIGN CONSTRAINT:
    Capability scope MUST NOT contain doc_class lists.
    Scope describes the PROBLEM SPACE — what kind of content patterns
    the capability handles, not which document types it applies to.

The first registered capability is ComponentsTableUnderstanding (CAP-COMP-TABLE),
migrated from the old ComponentsTableHandler (which was doc_class-dependent).
"""
# ⚠️  DEPRECATION NOTICE (2026-08-06, Phase 4.0)
# ⚠️  Capability definitions → dice/bootstrap.py (build_cap_comp_table_v2)
# ⚠️  Registry management     → dice/registry.py  (CapabilityRegistry)
# ⚠️  Graph sync              → dice/bootstrap.py (bootstrap_patterns_to_graph)
# ⚠️  This file remains as read-only backward-compat shim.
# ⚠️  Do NOT add new capabilities here.


from dice.graph.experience_graph import ExperienceGraph
from dice.graph.nodes import (
    Pattern, Evidence, Capability, Implementation, Rule,
    PatternStatus, CapabilityStatus,
    Observation, CapabilityCandidate,
)
from dice.graph.edges import Edge, EdgeType
from dice.models import SourceRef


# ═══════════════════════════════════════════════════════════════════════
# COMPONENT VOCABULARY — organized by SEMANTIC CATEGORY, not doc_class
# ═══════════════════════════════════════════════════════════════════════

COMPONENT_VOCABULARY = {
    # Biochemical reagents
    "biochemical_reagents": [
        "Rnase", "Dnase", "Proteinase K", "Lysozyme", "Protease",
        "RNase A", "DNase I", "RNase Inhibitor", "Reverse Transcriptase",
        "DNA Polymerase", "Taq Polymerase", "T4 DNA Ligase",
        "Restriction Enzyme", "Endonuclease", "Exonuclease",
    ],
    # Buffers and solutions
    "buffers_solutions": [
        "Buffer", "Elution Buffer", "Binding Buffer", "Wash Buffer",
        "Lysis Buffer", "Neutralization Buffer", "Resuspension Buffer",
        "TE Buffer", "TBE Buffer", "TAE Buffer", "Nuclease-Free Water",
        "Ethanol", "Isopropanol", "PBS", "Tris-HCl",
    ],
    # Nucleic acid related
    "nucleic_acid": [
        "DNA", "RNA", "cDNA", "gDNA", "cfDNA", "ctDNA",
        "Primer", "Probe", "Oligonucleotide", "Nucleotide",
        "dNTP", "dATP", "dCTP", "dGTP", "dTTP",
        "Library", "Adapter", "Index", "Barcode",
    ],
    # Magnetic beads / purification media
    "purification_media": [
        "Magnetic Beads", "Magnetic Bead", "Silica Membrane",
        "Silica Column", "Spin Column", "Filter Column",
        "Purification Column", "Affinity Resin", "Agarose Beads",
        "Streptavidin Beads", "Dynabeads",
    ],
    # Consumables and disposables
    "consumables": [
        "Collection Tube", "Elution Tube", "Microcentrifuge Tube",
        "PCR Tube", "PCR Strip", "PCR Plate", "Deep Well Plate",
        "Pipette Tip", "Filter Tip", "Syringe", "Needle",
        "Glove", "Tube", "Plate", "Strip",
    ],
    # Instruments and equipment
    "instruments": [
        "Thermal Cycler", "PCR Machine", "Centrifuge", "Vortex",
        "Magnetic Rack", "Magnetic Stand", "Heat Block",
        "Water Bath", "Thermomixer", "Shaker", "Incubator",
        "Spectrophotometer", "Fluorometer", "Qubit",
        "Bioanalyzer", "Fragment Analyzer",
    ],
    # Kits
    "kits": [
        "Kit", "Master Mix", "Reaction Mix", "Enzyme Mix",
        "Premix", "Ready Mix",
    ],
}

# Quantity patterns (cross-document)
QUANTITY_PATTERNS = [
    r"(\d+)\s*(?:×|x)\s*(\d+(?:\.\d+)?)\s*(\w*l)",       # "1 × 250 μL"
    r"(\d+)\s*(\w*l)",                                      # "250 μL"
    r"(\d+)\s*(?:pcs|pieces?|tubes?|strips?|plates?)",     # "50 pcs"
    r"(\d+(?:\.\d+)?)\s*(mg|g|μg|ng|ml|μl|l)",             # "1.5 ml"
    r"(\d+)\s*(?:tests?|rxns?|reactions?)",                 # "50 tests"
    r"(\d+)\s*(?:preps?)",                                   # "250 preps"
]

# Unit normalization
UNIT_NORMALIZATION = {
    "μl": "μL", "ul": "μL", "µl": "μL",
    "ml": "mL", "ML": "mL",
    "l": "L", "L": "L",
    "mg": "mg", "MG": "mg",
    "μg": "μg", "ug": "μg", "µg": "μg",
    "g": "g", "G": "g",
    "ng": "ng", "NG": "ng",
}


# ═══════════════════════════════════════════════════════════════════════
# PATTERN DEFINITIONS — descriptive, NOT procedural
# ═══════════════════════════════════════════════════════════════════════

def build_component_patterns() -> list[Pattern]:
    """
    Build detection patterns for component table understanding.

    These patterns are DESCRIPTIVE — they describe what component
    content looks like, not which document types contain it.
    """

    pat_table_collapse = Pattern(
        id="PAT-COMP-TABLE-COLLAPSE",
        name="Dual-Column Table Text Collapse",
        description=(
            "Tabular content where component names and their attributes "
            "(quantities, catalog numbers) appear in adjacent columns but "
            "get text-collapsed (merged into a single text block) during "
            "PDF slicing, causing information loss."
        ),
        detection_signals=[
            "component names followed by quantity specifications in close proximity",
            "text block contains multiple 'component → quantity' pairs in sequence",
            "presence of catalog/part numbers (alphanumeric codes) adjacent to component names",
            "density of component name tokens > 2 per 100 characters",
        ],
        structural_indicators=[
            "text block spans multiple lines with repeating name-value structure",
            "original source was a 2+ column table",
            "column alignment artifacts (tab-separated or space-padded layout)",
        ],
        content_indicators=[
            "high frequency of reagent/buffer/kit terms",
            "presence of volume/weight units (μL, mL, mg, μg)",
            "catalog number patterns (alphanumeric, 6-15 chars)",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.8,
        evidence_count=4,
        source_documents=["DC201-C1", "DC201-C2", "NDB609", "VSMB101"],
        cross_doc_count=4,
        tags=["components", "table", "text-collapse", "extraction"],
    )

    pat_density = Pattern(
        id="PAT-COMP-NAME-DENSITY",
        name="High Component Name Density in Text",
        description=(
            "A text block with unusually high concentration of known "
            "component vocabulary terms, indicating this is likely "
            "a components listing section regardless of document type."
        ),
        detection_signals=[
            "> 30% of words match known component vocabulary",
            "component terms appear in list-like sequence",
            "each line or sentence introduces a new component",
        ],
        structural_indicators=[
            "list-like structure (numbered, bulleted, or line-separated)",
            "each entry has similar grammatical structure",
        ],
        content_indicators=[
            "domain vocabulary density exceeds threshold",
            "quantity patterns appear with each entry",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.7,
        evidence_count=3,
        source_documents=["DC201-C1", "NDB609", "NDMB609"],
        cross_doc_count=3,
        tags=["components", "vocabulary-density", "detection"],
    )

    pat_quantity_pairing = Pattern(
        id="PAT-COMP-QUANTITY-PAIRING",
        name="Component-Quantity Pairing Pattern",
        description=(
            "Component names are consistently followed by quantity "
            "specifications (volume/weight + unit), forming recognizable "
            "pairs that can be extracted as structured data."
        ),
        detection_signals=[
            "text contains sequences matching: NAME → QUANTITY → (optional) CAT#",
            "quantity expressions follow standard patterns (number + unit)",
            "pairing consistency > 60% across the text block",
        ],
        structural_indicators=[
            "component and quantity appear within same line or adjacent lines",
            "separator patterns: tabs, multiple spaces, or line breaks between fields",
        ],
        content_indicators=[
            "numbered list where each number precedes a component name",
            "quantity always follows component name (not precedes it)",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.75,
        evidence_count=3,
        source_documents=["DC201-C1", "DC201-C2", "NDB609"],
        cross_doc_count=3,
        tags=["components", "quantity", "pairing", "extraction"],
    )

    return [pat_table_collapse, pat_density, pat_quantity_pairing]


# ═══════════════════════════════════════════════════════════════════════
# CAPABILITY DEFINITION
# ═══════════════════════════════════════════════════════════════════════

def build_components_table_capability() -> Capability:
    """
    Build the ComponentsTableUnderstanding capability.

    CRITICAL: scope describes PROBLEM SPACE, not document types.
    This capability does NOT know or care about plasmid_extraction_ifu
    vs ngs_library_prep. It only knows about structural patterns
    in component listings.
    """
    return Capability(
        id="CAP-COMP-TABLE",
        name="ComponentsTableUnderstanding",
        layer="chapter_handler",
        description=(
            "Identifies and extracts structured component lists from "
            "table-like text content in technical documentation. Handles "
            "text-collapsed dual-column tables, component-quantity pairing, "
            "and vocabulary-based detection — regardless of source document type."
        ),
        scope={
            "problem_space": (
                "Extracting structured component inventories (name, quantity, "
                "catalog number, function) from semi-structured text blocks "
                "that originated from multi-column tables but were collapsed "
                "during text extraction. Applicable wherever component listings "
                "appear in technical documentation."
            ),
            "input_semantics": (
                "Text block containing multiple component entries, each with "
                "a name and associated attributes (quantity, unit, catalog number). "
                "May be collapsed from a table or formatted as a list."
            ),
            "output_semantics": (
                "Structured list of components, each with: name, quantity, "
                "unit, catalog_number (if present), function (if inferable). "
                "Plus: total_components, covered_components, missing_count, "
                "coverage_ratio."
            ),
            "pattern_ids": [
                "PAT-COMP-TABLE-COLLAPSE",
                "PAT-COMP-NAME-DENSITY",
                "PAT-COMP-QUANTITY-PAIRING",
            ],
            "evidence_types": [
                "component_identified",
                "quantity_extracted",
                "catalog_matched",
                "function_inferred",
            ],
            # Vocabulary by SEMANTIC CATEGORY, not by doc_class
            "vocabulary": COMPONENT_VOCABULARY,
            "quantity_patterns": QUANTITY_PATTERNS,
            "unit_normalization": UNIT_NORMALIZATION,
        },
        pattern_ids=[
            "PAT-COMP-TABLE-COLLAPSE",
            "PAT-COMP-NAME-DENSITY",
            "PAT-COMP-QUANTITY-PAIRING",
        ],
        status=CapabilityStatus.BETA,
        version=1,
        epoch=1,
        source_pattern_ids=[
            "PAT-COMP-TABLE-COLLAPSE",
            "PAT-COMP-NAME-DENSITY",
            "PAT-COMP-QUANTITY-PAIRING",
        ],
        documents_tested=[],
        cross_doc_success_rate=0.0,
    )


# ═══════════════════════════════════════════════════════════════════════
# IMPLEMENTATION DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

def build_implementations() -> list[Implementation]:
    """
    Build concrete implementations for ComponentsTableUnderstanding.

    Different strategies handle different structural variants:
    - anchor_split: for dual-column text collapse (use component dictionary as anchors)
    - vocabulary_density: for vocabulary-based detection + line-by-line extraction
    """

    impl_anchor = Implementation(
        id="IMPL-COMP-TABLE-ANCHOR",
        capability_id="CAP-COMP-TABLE",
        name="Component Anchor Split Strategy",
        strategy=(
            "Use the component vocabulary as anchors to split collapsed table "
            "text back into individual component entries. Each known component "
            "name serves as a boundary marker. Reconstruct component entries "
            "from the text segments between anchors."
        ),
        config={
            "min_component_name_length": 3,
            "case_sensitive": False,
            "anchor_priority": [
                "biochemical_reagents",
                "buffers_solutions",
                "nucleic_acid",
                "purification_media",
            ],
            "max_text_between_anchors": 500,  # chars before assuming lost anchor
            "fallback_to_density": True,      # if anchor fails, try density approach
        },
    )

    impl_density = Implementation(
        id="IMPL-COMP-TABLE-DENSITY",
        capability_id="CAP-COMP-TABLE",
        name="Vocabulary Density Detection Strategy",
        strategy=(
            "Scan the text for vocabulary density patterns. When density "
            "exceeds threshold, treat each line/segment as a potential "
            "component entry. Extract name + quantity from each segment "
            "using pattern matching."
        ),
        config={
            "density_threshold": 0.3,         # 30% vocab match rate
            "min_segment_length": 10,          # chars
            "max_segment_length": 300,         # chars
        },
    )

    return [impl_anchor, impl_density]


# ═══════════════════════════════════════════════════════════════════════
# RULE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

def build_rules() -> list[Rule]:
    """Build low-level extraction rules for component handling."""
    return [
        Rule(
            id="RULE-COMP-NAME-EXTRACT",
            implementation_id="IMPL-COMP-TABLE-ANCHOR",
            name="Component Name Extraction",
            rule_type="anchor",
            pattern="",
            description="Extract component name from text segment between anchors",
            priority=1,
        ),
        Rule(
            id="RULE-COMP-QUANTITY-EXTRACT",
            implementation_id="IMPL-COMP-TABLE-ANCHOR",
            name="Component Quantity Extraction",
            rule_type="regex",
            pattern="|".join(QUANTITY_PATTERNS),
            description="Extract quantity and unit from component text using regex patterns",
            priority=2,
        ),
        Rule(
            id="RULE-COMP-CATALOG-EXTRACT",
            implementation_id="IMPL-COMP-TABLE-ANCHOR",
            name="Component Catalog Number Extraction",
            rule_type="regex",
            pattern=r"\b[A-Z]{2,4}\d{4,8}\b|\b\d{6,12}\b",
            description="Extract catalog/part numbers (alphanumeric patterns)",
            priority=3,
        ),
        Rule(
            id="RULE-COMP-DENSITY-SCAN",
            implementation_id="IMPL-COMP-TABLE-DENSITY",
            name="Vocabulary Density Scanner",
            rule_type="keyword",
            pattern="",
            description="Scan text for component vocabulary density to trigger extraction",
            priority=1,
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════

def register_components_table_capability(graph: ExperienceGraph) -> ExperienceGraph:
    """
    Register the ComponentsTableUnderstanding capability and all its
    dependencies (patterns, implementations, rules) into the graph.

    Returns the updated graph.
    """
    # 1. Add Patterns
    for pat in build_component_patterns():
        if pat.id not in graph.patterns:
            graph.add_pattern(pat)

    # 2. Add Capability
    cap = build_components_table_capability()
    if cap.id not in graph.capabilities:
        graph.add_capability(cap)

    # 3. Add Implementations
    for impl in build_implementations():
        if impl.id not in graph.implementations:
            graph.add_implementation(impl)

    # 4. Add Rules
    for rule in build_rules():
        if rule.id not in graph.rules:
            graph.add_rule(rule)

    # 5. Add Edges: Implementation → Capability
    for impl in build_implementations():
        edge = Edge(
            id=f"EDGE-{impl.id}-IMPLEMENTS-{cap.id}",
            source_id=impl.id,
            target_id=cap.id,
            edge_type=EdgeType.IMPLEMENTS,
            source_type="Implementation",
            target_type="Capability",
        )
        graph.add_edge(edge)

    # 6. Add Edges: Implementation → Rule
    for rule in build_rules():
        if rule.implementation_id in graph.implementations:
            edge = Edge(
                id=f"EDGE-{rule.implementation_id}-HAS_RULE-{rule.id}",
                source_id=rule.implementation_id,
                target_id=rule.id,
                edge_type=EdgeType.HAS_RULE,
                source_type="Implementation",
                target_type="Rule",
            )
            graph.add_edge(edge)

    # 7. Add Edges: Pattern → Capability (SUPPORTS via synthetic candidate)
    cand_id = "CAND-COMP-TABLE"
    cand = CapabilityCandidate(
        id=cand_id,
        name="ComponentsTableUnderstanding Candidate",
        pattern_ids=[p.id for p in build_component_patterns()],
        verification_score=0.85,
        is_verified=True,
        gates_passed=3,
        total_gates=3,
    )
    if cand_id not in graph.candidates:
        graph.add_candidate(cand)

    # Pattern → Candidate (SUPPORTS)
    for pat in build_component_patterns():
        edge = Edge(
            id=f"EDGE-{pat.id}-SUPPORTS-{cand_id}",
            source_id=pat.id,
            target_id=cand_id,
            edge_type=EdgeType.SUPPORTS,
            source_type="Pattern",
            target_type="CapabilityCandidate",
        )
        graph.add_edge(edge)

    # Candidate → Capability (GENERALIZES)
    edge = Edge(
        id=f"EDGE-{cand_id}-GENERALIZES-{cap.id}",
        source_id=cand_id,
        target_id=cap.id,
        edge_type=EdgeType.GENERALIZES,
        source_type="CapabilityCandidate",
        target_type="Capability",
    )
    graph.add_edge(edge)

    return graph
