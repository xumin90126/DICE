"""
Capability Bootstrap — initial capability registration.

Phase 4.0: Migrates from dice/runtime/capability_registry.py (hardcoded)
to the unified CapabilityRegistry.

Each capability is built with structured fields:
    Identity  → id, name, layer, description, scope
    Strategy  → input_schema, output_schema, execution_strategy,
                evidence_requirements, pattern_ids
    Evidence  → status, source_evidence_ids, documents_tested
    Evolution → version, epoch, validation_history, evolution_history
"""

from __future__ import annotations

from typing import Any

from dice.graph.nodes import (
    Capability, Pattern, Implementation, Rule,
    PatternStatus, CapabilityStatus,
)
from dice.registry import CapabilityRegistry


# ═══════════════════════════════════════════════════════════════════════════
# COMPONENT VOCABULARY — semantic categories, NOT doc_class
# ═══════════════════════════════════════════════════════════════════════════

COMPONENT_VOCABULARY: dict[str, list[str]] = {
    "biochemical_reagents": [
        "Rnase", "Dnase", "Proteinase K", "Lysozyme", "Protease",
        "RNase A", "DNase I", "RNase Inhibitor", "Reverse Transcriptase",
        "DNA Polymerase", "Taq Polymerase", "T4 DNA Ligase",
        "Restriction Enzyme", "Endonuclease", "Exonuclease",
    ],
    "buffers_solutions": [
        "Buffer", "Elution Buffer", "Binding Buffer", "Wash Buffer",
        "Lysis Buffer", "Neutralization Buffer", "Resuspension Buffer",
        "TE Buffer", "TBE Buffer", "TAE Buffer", "Nuclease-Free Water",
        "Ethanol", "Isopropanol", "PBS", "Tris-HCl",
    ],
    "nucleic_acid": [
        "DNA", "RNA", "cDNA", "gDNA", "cfDNA", "ctDNA",
        "Primer", "Probe", "Oligonucleotide", "Nucleotide",
        "dNTP", "dATP", "dCTP", "dGTP", "dTTP",
        "Library", "Adapter", "Index", "Barcode",
    ],
    "purification_media": [
        "Magnetic Beads", "Magnetic Bead", "Silica Membrane",
        "Silica Column", "Spin Column", "Filter Column",
        "Purification Column", "Affinity Resin", "Agarose Beads",
        "Streptavidin Beads", "Dynabeads",
    ],
    "consumables": [
        "Collection Tube", "Elution Tube", "Microcentrifuge Tube",
        "PCR Tube", "PCR Strip", "PCR Plate", "Deep Well Plate",
        "Pipette Tip", "Filter Tip", "Syringe", "Needle",
        "Glove", "Tube", "Plate", "Strip",
    ],
    "instruments": [
        "Thermal Cycler", "PCR Machine", "Centrifuge", "Vortex",
        "Magnetic Rack", "Magnetic Stand", "Heat Block",
        "Water Bath", "Thermomixer", "Shaker", "Incubator",
        "Spectrophotometer", "Fluorometer", "Qubit",
        "Bioanalyzer", "Fragment Analyzer",
    ],
    "kits": [
        "Kit", "Master Mix", "Reaction Mix", "Enzyme Mix",
        "Premix", "Ready Mix",
    ],
}

QUANTITY_PATTERNS: list[str] = [
    r"(\d+)\s*(?:×|x)\s*(\d+(?:\.\d+)?)\s*(\w*l)",
    r"(\d+)\s*(\w*l)",
    r"(\d+)\s*(?:pcs|pieces?|tubes?|strips?|plates?)",
    r"(\d+(?:\.\d+)?)\s*(mg|g|μg|ng|ml|μl|l)",
    r"(\d+)\s*(?:tests?|rxns?|reactions?)",
    r"(\d+)\s*(?:preps?)",
]

UNIT_NORMALIZATION: dict[str, str] = {
    "μl": "μL", "ul": "μL", "µl": "μL",
    "ml": "mL", "ML": "mL",
    "l": "L", "L": "L",
    "mg": "mg", "MG": "mg",
    "μg": "μg", "ug": "μg", "µg": "μg",
    "g": "g", "G": "g",
    "ng": "ng", "NG": "ng",
}


# ═══════════════════════════════════════════════════════════════════════════
# PATTERNS
# ═══════════════════════════════════════════════════════════════════════════


def build_patterns_v2() -> list[Pattern]:
    """Build detection patterns for component table understanding."""

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
            "presence of catalog/part numbers adjacent to component names",
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


# ═══════════════════════════════════════════════════════════════════════════
# CAPABILITY — v2 with structured fields
# ═══════════════════════════════════════════════════════════════════════════


def build_cap_comp_table_v2() -> Capability:
    """
    Build ComponentsTableUnderstanding Capability (v2).

    Uses Phase 4.0 structured fields:
        input_schema, output_schema, execution_strategy, evidence_requirements.

    Does NOT contain: doc_class, product_id, filename — anywhere.
    """
    return Capability(
        # ── Identity ──
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
                "during text extraction."
            ),
            "vocabulary": COMPONENT_VOCABULARY,
            "quantity_patterns": QUANTITY_PATTERNS,
            "unit_normalization": UNIT_NORMALIZATION,
        },

        # ── Strategy ──
        input_schema={
            "fields": {
                "content": {"type": "str", "required": True,
                            "description": "Raw text content of the slice/chapter"},
                "structure_features": {"type": "dict", "required": False,
                                       "description": "Pre-computed L1 structure signals"},
            },
            "constraints": {
                "min_content_length": 50,
                "max_content_length": 50000,
            },
        },
        output_schema={
            "fields": {
                "components": {"type": "list[dict]", "required": True,
                               "description": "Extracted component entries"},
                "total_components": {"type": "int", "required": True},
                "covered_components": {"type": "int", "required": True},
                "missing_components": {"type": "int", "required": True},
                "coverage_ratio": {"type": "float", "required": True},
                "extraction_method": {"type": "str", "required": True,
                                      "description": "anchor_split | vocabulary_density | structural"},
                "warnings": {"type": "list[str]", "required": False},
                "evidence_items": {"type": "list[dict]", "required": False},
            },
        },
        execution_strategy=(
            "TWO-PHASE EXTRACTION: "
            "Phase A (Component Anchor Split): Use component vocabulary as "
            "anchors to split collapsed table text back into individual "
            "component entries. Each known component name serves as a boundary "
            "marker. "
            "Phase B (Vocabulary Density Fallback): If anchor splitting fails "
            "or produces insufficient coverage, fall back to vocabulary density "
            "scanning with quantity-anchor extraction."
        ),
        evidence_requirements={
            "min_pattern_matches": 1,
            "min_content_length": 50,
            "preferred_patterns": [
                "PAT-COMP-TABLE-COLLAPSE",
                "PAT-COMP-QUANTITY-PAIRING",
            ],
        },
        pattern_ids=[
            "PAT-COMP-TABLE-COLLAPSE",
            "PAT-COMP-NAME-DENSITY",
            "PAT-COMP-QUANTITY-PAIRING",
        ],

        # ── Evidence ──
        status=CapabilityStatus.BETA,
        source_pattern_ids=[
            "PAT-COMP-TABLE-COLLAPSE",
            "PAT-COMP-NAME-DENSITY",
            "PAT-COMP-QUANTITY-PAIRING",
        ],
        documents_tested=[
            "DC201-C1", "DC201-C2", "NDB609", "NDMB609",
            "VS101", "VSMB101", "NH101", "E803",
        ],
        cross_doc_success_rate=0.80,

        # ── Evolution ──
        version=2,
        epoch=1,
        validation_history=[
            {
                "timestamp": "2026-08-06T12:00:00Z",
                "validator": "phase3_manual",
                "result": "passed",
                "notes": "Phase 1-3 validation: 8 products, 3 doc_classes, 80% success rate",
            },
        ],
        evolution_history=[
            {
                "timestamp": "2026-08-06T12:00:00Z",
                "change": "initial_registration",
                "detail": "First registration with structured Phase 4.0 fields",
            },
        ],
    )


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════


def build_implementations_v2() -> list[Implementation]:
    """Build concrete implementations for ComponentsTableUnderstanding."""

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
            "max_text_between_anchors": 500,
            "fallback_to_density": True,
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
            "density_threshold": 0.3,
            "min_segment_length": 10,
            "max_segment_length": 300,
        },
    )

    return [impl_anchor, impl_density]


def build_rules_v2() -> list[Rule]:
    """Build extraction rules for component handling."""
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
            description="Extract quantity and unit from component text using regex",
            priority=2,
        ),
        Rule(
            id="RULE-COMP-CATALOG-EXTRACT",
            implementation_id="IMPL-COMP-TABLE-ANCHOR",
            name="Component Catalog Number Extraction",
            rule_type="regex",
            pattern=r"\b[A-Z]{2,4}\d{4,8}\b|\b\d{6,12}\b",
            description="Extract catalog/part numbers",
            priority=3,
        ),
        Rule(
            id="RULE-COMP-DENSITY-SCAN",
            implementation_id="IMPL-COMP-TABLE-DENSITY",
            name="Vocabulary Density Scanner",
            rule_type="keyword",
            pattern="",
            description="Scan text for component vocabulary density",
            priority=1,
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 1 PATTERNS (Phase 5.1a — promoted from Phase 3.2 candidates)
# ═══════════════════════════════════════════════════════════════════════════


def build_patterns_v3() -> list[Pattern]:
    """Build all patterns — v2 + Batch 1 structural primitives."""
    patterns = build_patterns_v2()

    # ── PAT-TABLE-COLLAPSE-STRUCT (from PAT-CAND-004) ──
    pat_table_collapse_struct = Pattern(
        id="PAT-TABLE-COLLAPSE-STRUCT",
        name="Generic Collapsed Table Structure",
        description=(
            "Text block where original table columns have been collapsed "
            "into a single text stream without delimiters. Detected purely "
            "by structural signals: long unbroken segments, quantity-unit "
            "pairs in dense proximity, and word-smashed artifacts. "
            "Domain-independent."
        ),
        detection_signals=[
            "long unbroken text segments (>200 chars) with inline data artifacts",
            "quantity-unit pairs appearing mid-sentence without column separators",
            "word-boundary smashing patterns (CamelCase adjacent to numbers)",
        ],
        structural_indicators=[
            "text block spans multiple lines with compressed row-like structure",
            "original source was a table (2+ columns) that collapsed during extraction",
            "no tab/column-delimiter artifacts — pure concatenation",
        ],
        content_indicators=[
            "high frequency of numeric tokens in mid-text positions",
            "unit abbreviations embedded without whitespace separation",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.75,
        evidence_count=3,
        source_documents=["DC201-C1", "NDB609", "VSMB101"],
        cross_doc_count=3,
        tags=["table", "collapse", "reconstruction", "structure"],
    )

    # ── PAT-ANCHOR-DRIVEN-EXTRACT (from PAT-CAND-003) ──
    pat_anchor_extract = Pattern(
        id="PAT-ANCHOR-DRIVEN-EXTRACT",
        name="Anchor-Driven Key-Value Extraction",
        description=(
            "Content organized as Label: Value pairs where the label "
            "serves as an anchor for extracting the associated value. "
            "Common in specification sheets, parameter tables, and "
            "configuration sections. Domain-independent."
        ),
        detection_signals=[
            "key: value or key = value patterns repeated across the text",
            "label terms are short, capitalized, and followed by colon/equals",
            "value portion contains numbers, ranges, or enumerations",
        ],
        structural_indicators=[
            "consistent label: value alignment pattern",
            "labels share similar grammatical category (all nouns or all noun phrases)",
            "line-oriented layout — one key-value per line or per segment",
        ],
        content_indicators=[
            "colon-separated pairs at line starts",
            "numeric values associated with descriptive labels",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.70,
        evidence_count=3,
        source_documents=["DC201-C1", "NH101", "VS101"],
        cross_doc_count=3,
        tags=["key-value", "anchor", "extraction", "label"],
    )

    # ── PAT-COLUMNAR-ALIGNMENT (from PAT-CAND-005) ──
    pat_columnar = Pattern(
        id="PAT-COLUMNAR-ALIGNMENT",
        name="Columnar Text Alignment",
        description=(
            "Text with intact column alignment — spaces or tabs separate "
            "fields into identifiable columns. Unlike collapsed tables, "
            "the column structure is preserved. Domain-independent."
        ),
        detection_signals=[
            "consistent multi-space gaps forming aligned columns across lines",
            "tab-separated fields with consistent field count per line",
            "column positions remain stable across consecutive lines",
        ],
        structural_indicators=[
            "tabular layout with visible column boundaries",
            "each column has a consistent data type (text vs numeric vs date)",
            "header row followed by aligned data rows",
        ],
        content_indicators=[
            "aligned fields share semantic category per column",
            "numeric columns right-aligned by spacing",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.72,
        evidence_count=3,
        source_documents=["DC201-C1", "E803", "NDB609"],
        cross_doc_count=3,
        tags=["columnar", "table", "alignment", "extraction"],
    )

    # ── PAT-NAME-QUANTITY-TRIPLE (from PAT-CAND-001) ──
    pat_name_qty_triple = Pattern(
        id="PAT-NAME-QUANTITY-TRIPLE",
        name="Name-Quantity-Unit Triple Identification",
        description=(
            "Sequences where a name token is immediately (within same line "
            "or adjacent line) followed by a quantity and unit, forming a "
            "recognizable (name, quantity, unit) triple. Domain-independent."
        ),
        detection_signals=[
            "sequences matching NAME → NUMBER → UNIT within 60 characters",
            "quantity expressions follow standard patterns (number + unit)",
            "triple consistency > 50% across the text block",
        ],
        structural_indicators=[
            "name and quantity appear within the same line",
            "separator patterns: 2+ spaces, tabs, or dash between fields",
            "repeated triple pattern across consecutive lines",
        ],
        content_indicators=[
            "numeric values immediately adjacent to unit symbols",
            "proper-name-capitalized tokens preceding numeric values",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.68,
        evidence_count=3,
        source_documents=["DC201-C1", "DC201-C2", "NDB609"],
        cross_doc_count=3,
        tags=["triple", "name", "quantity", "unit", "extraction"],
    )

    patterns.extend([
        pat_table_collapse_struct,
        pat_anchor_extract,
        pat_columnar,
        pat_name_qty_triple,
    ])
    return patterns


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 2 PATTERNS (Phase 5.1b — content type detection)
# ═══════════════════════════════════════════════════════════════════════════


def build_patterns_v4() -> list[Pattern]:
    """Build all patterns — v3 + Batch 2 content type detectors."""
    patterns = build_patterns_v3()

    pat_storage = Pattern(
        id="PAT-STORAGE-CONDITIONS",
        name="Storage Conditions Pattern",
        description=(
            "Content describing storage conditions — characterized by "
            "temperature values (℃/°C), time ranges, and key-value "
            "formatting of storage parameters. Domain-independent."
        ),
        detection_signals=[
            "temperature values with ℃/°C units",
            "storage duration specifications (hours, days, months)",
            "key: value layout for storage parameters",
        ],
        structural_indicators=[
            "key-value pair formatting for conditions",
            "compact section with parameter-like entries",
        ],
        content_indicators=[
            "temperature patterns (℃/°C symbols)",
            "time duration expressions (hours/days/months)",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.60,
        evidence_count=2,
        source_documents=["DC201-C1", "NDB609"],
        cross_doc_count=2,
        tags=["storage", "temperature", "conditions", "detection"],
    )

    pat_safety = Pattern(
        id="PAT-SAFETY-WARNINGS",
        name="Safety Warnings Pattern",
        description=(
            "Content organized as warning/safety information — characterized "
            "by high density of header-like lines (ALL CAPS short lines), "
            "and list-formatted caution statements. Domain-independent."
        ),
        detection_signals=[
            "multiple short ALL-CAPS header lines",
            "key-value formatted warning/precaution items",
            "concentrated block of advisory statements",
        ],
        structural_indicators=[
            "header-heavy layout with many section markers",
            "list-formatted caution items",
        ],
        content_indicators=[
            "high header density (≥2 headers in section)",
            "enumerated or bulleted advisory statements",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.55,
        evidence_count=2,
        source_documents=["DC201-C1", "VS101"],
        cross_doc_count=2,
        tags=["safety", "warning", "caution", "detection"],
    )

    pat_troubleshoot = Pattern(
        id="PAT-TROUBLESHOOT-QA",
        name="Troubleshooting Q&A Pattern",
        description=(
            "Content structured as problem-solution pairs — characterized "
            "by list-formatted entries with header-like problem statements "
            "followed by explanatory solutions. Domain-independent."
        ),
        detection_signals=[
            "list structure with descriptive headers",
            "each entry begins with a problem-like statement",
            "longer-than-average explanations following short headers",
        ],
        structural_indicators=[
            "list-formatted entries with section headers",
            "entry-oriented layout with headers + body pattern",
        ],
        content_indicators=[
            "header count ≥ 1 per section",
            "list structure with descriptive content",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.55,
        evidence_count=2,
        source_documents=["DC201-C1", "NDB609"],
        cross_doc_count=2,
        tags=["troubleshooting", "faq", "qa", "detection"],
    )

    pat_procedure = Pattern(
        id="PAT-PROCEDURE-STEPS",
        name="Procedure Steps Pattern",
        description=(
            "Content organized as sequential procedural steps — characterized "
            "by long line count and list/dot-point structure. Procedure "
            "sections tend to be the longest sections with step-by-step "
            "layout. Domain-independent."
        ),
        detection_signals=[
            "high line count relative to other sections",
            "list-formatted step-by-step structure",
            "sequential numbering or enumeration",
        ],
        structural_indicators=[
            "long section with enumerated entries",
            "each step is a self-contained instruction block",
        ],
        content_indicators=[
            "line count ≥ 12 (procedures are rarely short)",
            "list structure with sequential progression",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.55,
        evidence_count=2,
        source_documents=["DC201-C1", "NH101"],
        cross_doc_count=2,
        tags=["procedure", "steps", "method", "detection"],
    )

    pat_materials = Pattern(
        id="PAT-MATERIALS-LIST",
        name="Materials List Pattern",
        description=(
            "Content listing required/preparation materials — characterized "
            "by named items with discrete counts (tubes, pieces, plates) "
            "and list-formatted layout. Domain-independent."
        ),
        detection_signals=[
            "named items with count indicators",
            "list-formatted material entries",
            "discrete quantity patterns (pcs, tubes, strips)",
        ],
        structural_indicators=[
            "list of named items with quantity specifications",
            "compact itemized layout",
        ],
        content_indicators=[
            "name-type elements ≥ 2 per section",
            "count-type elements (tubes, strips, pieces)",
        ],
        status=PatternStatus.VERIFIED,
        confidence=0.55,
        evidence_count=2,
        source_documents=["DC201-C1", "VS101"],
        cross_doc_count=2,
        tags=["materials", "preparation", "list", "detection"],
    )

    patterns.extend([
        pat_storage, pat_safety, pat_troubleshoot, pat_procedure, pat_materials,
    ])
    return patterns


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 2 CAPABILITIES (Phase 5.1b — content type detectors)
# ═══════════════════════════════════════════════════════════════════════════


def build_cap_storage_detect() -> Capability:
    """CAP-STORAGE-DETECT: storage condition section detection."""
    return Capability(
        id="CAP-STORAGE-DETECT",
        name="StorageConditionsDetection",
        layer="chapter_handler",
        description=(
            "Detects content sections describing storage conditions — "
            "identified by temperature values (℃/°C), time ranges, "
            "and key-value formatted storage parameters."
        ),
        scope={
            "problem_space": "Detection of storage condition sections in technical documents",
            "vocabulary": {},
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "is_storage_section": {"type": "bool", "required": True},
            "confidence": {"type": "float", "required": True},
            "detected_signals": {"type": "list[str]", "required": False},
        }},
        execution_strategy="SIGNAL SCAN: Detect temperature patterns and key-value storage format.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-STORAGE-CONDITIONS"]},
        pattern_ids=["PAT-STORAGE-CONDITIONS"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-STORAGE-CONDITIONS"],
        documents_tested=["DC201-C1", "NDB609"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T00:00:00Z",
                             "validator": "phase5_1b_bootstrap", "result": "beta",
                             "notes": "Phase 5.1b Batch 2: content type detector"}],
        evolution_history=[{"timestamp": "2026-08-07T00:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1b Batch 2"}],
    )


def build_cap_safety_detect() -> Capability:
    """CAP-SAFETY-DETECT: safety/warning section detection."""
    return Capability(
        id="CAP-SAFETY-DETECT",
        name="SafetyWarningsDetection",
        layer="chapter_handler",
        description=(
            "Detects content sections containing safety warnings and "
            "precautionary statements — identified by high header density "
            "and list-formatted caution items."
        ),
        scope={
            "problem_space": "Detection of safety/warning sections in technical documents",
            "vocabulary": {},
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "is_safety_section": {"type": "bool", "required": True},
            "confidence": {"type": "float", "required": True},
        }},
        execution_strategy="HEADER SCAN: Detect high header density and list-formatted warnings.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-SAFETY-WARNINGS"]},
        pattern_ids=["PAT-SAFETY-WARNINGS"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-SAFETY-WARNINGS"],
        documents_tested=["DC201-C1", "VS101"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T00:00:00Z",
                             "validator": "phase5_1b_bootstrap", "result": "beta",
                             "notes": "Phase 5.1b Batch 2"}],
        evolution_history=[{"timestamp": "2026-08-07T00:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1b Batch 2"}],
    )


def build_cap_troubleshoot_detect() -> Capability:
    """CAP-TROUBLESHOOT-DETECT: troubleshooting/FAQ section detection."""
    return Capability(
        id="CAP-TROUBLESHOOT-DETECT",
        name="TroubleshootingDetection",
        layer="chapter_handler",
        description=(
            "Detects troubleshooting/FAQ content sections — identified "
            "by list-formatted entries with header-like problem statements "
            "followed by solution descriptions."
        ),
        scope={
            "problem_space": "Detection of troubleshooting/FAQ sections in technical documents",
            "vocabulary": {},
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "is_troubleshooting_section": {"type": "bool", "required": True},
            "confidence": {"type": "float", "required": True},
        }},
        execution_strategy="QA SCAN: Detect list structure with header-like entries.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-TROUBLESHOOT-QA"]},
        pattern_ids=["PAT-TROUBLESHOOT-QA"],
        # ── Phase 0.6 Schema Extension: Capability Definition ──
        positive_boundary={
            "definition": "Detects content sections describing anomalous phenomena with corrective/resolution actions",
            "core_structure": "anomaly → resolution pair",
            "types": [
                {"type": "anomaly_corrective",
                 "description": "Observed anomaly + corrective action steps forming a causal chain",
                 "example": "No band visible after electrophoresis → increase template amount to 50 ng and repeat PCR",
                 "signal": "anomaly word + corrective action word in same section"},
                {"type": "problem_resolution",
                 "description": "Explicitly marked problem statement + corresponding solution",
                 "example": "Problem: Low transformation efficiency → Solution: Use fresh competent cells",
                 "signal": "explicit problem/solution marker headers"},
                {"type": "failure_recovery",
                 "description": "Operation failure symptom description + recovery/repeat steps",
                 "example": "If the ligation fails to produce colonies → re-purify insert DNA and repeat ligation",
                 "signal": "failure description + recovery/repeat action word"},
                {"type": "unexpected_fix",
                 "description": "Unexpected/abnormal result deviating from expectation + fix instruction",
                 "example": "Unexpected band at ~150 bp — primer-dimer artifact → reduce primer concentration by 50%",
                 "signal": "unexpected/abnormal signal + fix/adjust instruction"},
                {"type": "troubleshooting_table_faq",
                 "description": "Structured troubleshooting guide table or FAQ with Problem/Cause/Solution rows",
                 "example": "Troubleshooting Guide table: Problem → Possible Cause → Recommended Action",
                 "signal": "table/list structure + problem-solution paired rows"},
                {"type": "conditional_anomaly",
                 "description": "Condition-triggered anomaly + condition-specific corrective steps",
                 "example": "In case of low recovery (<50%) → repeat elution with pre-heated buffer at 55°C",
                 "signal": "if/in case of/should + anomaly clause + corrective clause"},
            ],
            "signal_requirements": {
                "problem_signal_required": True,
                "resolution_signal_required": True,
                "logic": "AND — both problem and resolution signals must be present",
            },
        },
        negative_boundary={
            "exclusions": [
                {"domain": "Safety Warning",
                 "belongs_to": "CAP-SAFETY-DETECT",
                 "rationale": "Safety is pre-incident prevention; Troubleshooting is post-incident repair",
                 "discrimination": "Safety keywords: danger/warning/hazard/toxic/harmful/poison/first aid/PPE/seek medical",
                 "priority": 1},
                {"domain": "Storage Condition",
                 "belongs_to": "CAP-STORAGE-DETECT",
                 "rationale": "Pure storage parameters are preservation requirements, not anomaly repair",
                 "discrimination": "Pure storage: temperature/shelf-life/stability without anomaly+resolution pair. Exception: storage context WITH anomaly+resolution still qualifies.",
                 "priority": 3},
                {"domain": "Procedure Instruction",
                 "belongs_to": "CAP-PROCEDURE-DETECT",
                 "rationale": "Forward operation workflow is not reverse anomaly repair",
                 "discrimination": "Conditional if-then alone doesn't distinguish: must check whether condition premise is anomaly (Troubleshooting) or operational option (Procedure)",
                 "priority": 4},
                {"domain": "Product Feature/Specification",
                 "belongs_to": "N/A (no specific Capability)",
                 "rationale": "Product marketing/feature/specification content does not address usage faults",
                 "discrimination": "Descriptive product content without anomaly+resolution pair",
                 "priority": 5},
                {"domain": "Comparison/Test Report",
                 "belongs_to": "N/A (no specific Capability)",
                 "rationale": "Competitive comparison, performance test results, benchmark data",
                 "discrimination": "Comparison/benchmark/test data description without anomaly+resolution pair",
                 "priority": 5},
            ],
        },
        activation_rule={
            "type": "pair_requirement",
            "description": "TroubleshootingDetection activates ONLY when both anomaly and resolution signals are detected",
            "problem_signals": {
                "definition": "Semantic signals indicating an anomaly/problem/failure/unexpected result exists",
                "signal_types": [
                    {"type": "explicit_anomaly", "strength": "STRONG",
                     "anchors": ["no band", "no signal", "no amplification", "no colony", "no product",
                                 "smear", "degradation", "contamination", "inhibition", "low yield",
                                 "low recovery", "low efficiency", "high background", "non-specific",
                                 "primer-dimer", "artifact", "failed", "failure", "abnormal", "unexpected"]},
                    {"type": "explicit_problem_marker", "strength": "STRONG",
                     "anchors": ["Problem:", "Issue:", "Troubleshooting", "FAQ", "常见问题", "故障"]},
                    {"type": "failure_description", "strength": "STRONG",
                     "anchors": ["does not work", "not working", "no result", "cannot", "unable to",
                                 "fails to", "incomplete", "missing", "lost"]},
                    {"type": "conditional_anomaly", "strength": "MEDIUM",
                     "anchors": ["if no", "if the", "in case of", "when no", "should not",
                                 "lower than expected", "higher than expected", "less than",
                                 "weak or no", "poor", "insufficient"]},
                    {"type": "result_deviation", "strength": "MEDIUM",
                     "anchors": ["lower than", "higher than", "less than", "greater than",
                                 "outside", "exceeds", "below", "above"]},
                ],
            },
            "resolution_signals": {
                "definition": "Semantic signals indicating a corrective action/diagnostic/resolution exists",
                "signal_types": [
                    {"type": "corrective_action", "strength": "STRONG",
                     "anchors": ["increase", "decrease", "reduce", "add", "remove", "replace",
                                 "repeat", "re-purify", "re-extract", "re-amplify", "re-run",
                                 "use fresh", "prepare fresh", "check", "verify", "confirm",
                                 "adjust", "optimize", "dilute", "concentrate", "extend",
                                 "change", "switch to", "try", "ensure", "make sure"]},
                    {"type": "diagnostic_action", "strength": "STRONG",
                     "anchors": ["check", "verify", "confirm", "test", "examine", "inspect",
                                 "measure", "quantify", "assess", "evaluate", "determine",
                                 "run a control", "include a control", "compare with"]},
                    {"type": "resolution_marker", "strength": "STRONG",
                     "anchors": ["Solution:", "Remedy:", "To resolve", "To fix", "Recommended action:",
                                 "Corrective action:", "解决方法", "解决方案"]},
                    {"type": "cause_fix_pair", "strength": "STRONG",
                     "anchors": ["may be due to", "may result from", "could be caused by",
                                 "this is typically", "this is often", "the most common cause",
                                 "likely caused by"]},
                ],
            },
            "activation_condition": {
                "problem_minimum": 1,
                "resolution_minimum": 1,
                "logic": "Problem Signal count >= 1 AND Resolution Signal count >= 1",
                "pre_exclusion_check": "Before activation, run exclusion_rules.hard_exclusions — if any trigger, suppress",
            },
        },
        conflict_resolution={
            "default_priority": 2,
            "priority_schema": {
                1: "SafetyWarningsDetection — SAFETY FIRST, not negotiable",
                2: "TroubleshootingDetection",
                3: "StorageConditionsDetection",
                4: "ProcedureDetection",
            },
            "conflicts": [
                {"rival": "CAP-SAFETY-DETECT",
                 "resolution": "Safety takes priority. Content marked SAFETY_ZONE → TroubleshootingDetection suppressed.",
                 "rule": "Safety keywords present → suppress Troubleshooting regardless of Problem+Resolution signals",
                 "discriminator": "Safety domain keywords: danger/warning/hazard/toxic/harmful/poison/first aid/PPE/seek medical",
                 "example_suppressed": "\"If the solution contacts skin, wash with water. If irritation persists, seek medical attention.\" → Safety (seek medical attention), NOT Troubleshooting"},
                {"rival": "CAP-STORAGE-DETECT",
                 "resolution": "Semantic context determines winner. Pure storage params → Storage wins. Storage anomaly+fix → Troubleshooting wins.",
                 "rule": "Check for anomaly+resolution pair in storage context. Without pair → Storage. With pair → Troubleshooting.",
                 "discriminator": "anomaly+resolution pair presence in storage context",
                 "example_storage": "\"Store at -20°C. Protect from light.\" → StorageConditionsDetection",
                 "example_troubleshooting": "\"If stored at room temp for >24h, enzyme activity may decrease. Check activity with control. If <80%, use fresh aliquot.\" → TroubleshootingDetection (storage-induced fault + fix)"},
                {"rival": "CAP-PROCEDURE-DETECT",
                 "resolution": "Condition premise determines winner. Normal operation branch → Procedure. Anomaly repair branch → Troubleshooting.",
                 "rule": "Check condition premise semantics: anomaly/failure premise → Troubleshooting; operational option → Procedure.",
                 "discriminator": "condition premise semantic type (anomaly vs operational variant)",
                 "example_procedure": "\"If using Option A, add 5 µL. If using Option B, add 10 µL.\" → ProcedureDetection (operational variants)",
                 "example_troubleshooting": "\"If no amplification after 35 cycles, check enzyme activity and repeat with fresh aliquot.\" → TroubleshootingDetection (anomaly repair)"},
            ],
        },
        exclusion_rules={
            "hard_exclusions": [
                {"rule_id": "EXCL-SAFETY-001",
                 "description": "Safety domain content — absolute exclusion regardless of structure",
                 "triggers": ["danger", "warning", "hazard", "toxic", "harmful", "poison",
                              "first aid", "PPE", "personal protective", "seek medical",
                              "irritant", "corrosive", "flammable", "H302", "H315", "H319"],
                 "condition": "ANY trigger word present in content",
                 "action": "Suppress TroubleshootingDetection entirely",
                 "routing": "Content belongs to CAP-SAFETY-DETECT domain"},
                {"rule_id": "EXCL-PROCEDURE-001",
                 "description": "Pure forward procedure — no anomaly premise, just operational steps",
                 "triggers": [],
                 "condition": "Content has list/step structure AND zero anomaly signals AND zero resolution signals",
                 "action": "Suppress TroubleshootingDetection",
                 "routing": "Content belongs to CAP-PROCEDURE-DETECT domain"},
            ],
            "soft_exclusions": [
                {"rule_id": "EXCL-STORAGE-001",
                 "description": "Pure storage parameters — exclude unless anomaly+resolution pair present",
                 "triggers": ["store at", "storage", "shelf life", "stability", "shipping",
                              "protect from light", "freeze-thaw", "aliquot", "reconstitution"],
                 "condition": "Storage keywords present AND no anomaly+resolution pair found",
                 "action": "Suppress TroubleshootingDetection",
                 "factor": "storage_context"},
                {"rule_id": "EXCL-FEATURE-001",
                 "description": "Product feature/specification description without troubleshooting context",
                 "triggers": ["feature", "advantage", "benefit", "specification", "application",
                              "suitable for", "designed for", "compatible with"],
                 "condition": "Content is product description/marketing without anomaly+resolution pair",
                 "action": "Suppress TroubleshootingDetection",
                 "factor": "semantic_context"},
                {"rule_id": "EXCL-COMPARISON-001",
                 "description": "Comparison/test report/benchmark data without troubleshooting context",
                 "triggers": ["vs", "versus", "compared to", "comparison", "average", "±", "CV",
                              "benchmark", "recovery rate", "Ct value"],
                 "condition": "Content is comparison/test/benchmark data without anomaly+resolution pair",
                 "action": "Suppress TroubleshootingDetection",
                 "factor": "semantic_context"},
            ],
        },
        validation_criteria={
            "primary_metrics": [
                {"name": "Semantic Precision",
                 "definition": "TP / (TP + FP) — proportion of triggers that are true troubleshooting",
                 "target": 0.70,
                 "measurement": "Human review of each TroubleshootingDetection trigger content"},
                {"name": "Boundary Correctness",
                 "definition": "Zero Safety FP + Zero pure Storage FP + Zero pure Procedure FP",
                 "target": 1.0,
                 "measurement": "Per-exclusion audit of all triggered content"},
                {"name": "Safety False Positive Rate",
                 "definition": "FP where content is actually Safety / total triggers",
                 "target": 0.0,
                 "measurement": "Human review of Safety keyword matches in triggered content"},
            ],
            "forbidden_metrics": [
                "unmatched reduction", "trigger count increase",
                "cross_doc_success_rate", "average confidence",
            ],
            "pass_condition": "Semantic Precision >= 0.70 AND Zero Safety FP AND Zero pure Storage FP AND All FP classified and explained",
            "reject_condition": "Any Safety FP (hard redline) OR Semantic Precision < 0.50",
            "revise_condition": "Semantic Precision 0.50-0.69 without Safety FP",
            "review_questions": [
                "Is this content truly about troubleshooting? (anomaly → resolution pair)",
                "Is any Safety/Storage/Procedure/Feature/Comparison content misclassified?",
                "Is the evidence quality STRONG (same paragraph) / GOOD (adjacent) / WEAK (distant)?",
            ],
        },
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-TROUBLESHOOT-QA"],
        documents_tested=["DC201-C1", "NDB609"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[
            {"timestamp": "2026-08-07T00:00:00Z",
             "validator": "phase5_1b_bootstrap", "result": "beta",
             "notes": "Phase 5.1b Batch 2"},
            {"timestamp": "2026-08-10T00:00:00Z",
             "validator": "phase0_6_schema_extension",
             "result": "definition_enhanced",
             "notes": "Phase 0.6: Capability Definition Schema Extension. "
                      "Added positive_boundary/negative_boundary/activation_rule/"
                      "conflict_resolution/exclusion_rules/validation_criteria.",
             "definition_version": "2.0"},
        ],
        evolution_history=[{"timestamp": "2026-08-07T00:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1b Batch 2"}],
    )


def build_cap_procedure_detect() -> Capability:
    """CAP-PROCEDURE-DETECT: procedure/method section detection."""
    return Capability(
        id="CAP-PROCEDURE-DETECT",
        name="ProcedureDetection",
        layer="chapter_handler",
        description=(
            "Detects procedure/method content sections — identified "
            "by high line count and sequential list-formatted step structure."
        ),
        scope={
            "problem_space": "Detection of procedure/method sections in technical documents",
            "vocabulary": {},
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 30}},
        output_schema={"fields": {
            "is_procedure_section": {"type": "bool", "required": True},
            "confidence": {"type": "float", "required": True},
        }},
        execution_strategy="LENGTH SCAN: Detect long sections with sequential list structure.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 30,
                               "preferred_patterns": ["PAT-PROCEDURE-STEPS"]},
        pattern_ids=["PAT-PROCEDURE-STEPS"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-PROCEDURE-STEPS"],
        documents_tested=["DC201-C1", "NH101"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T00:00:00Z",
                             "validator": "phase5_1b_bootstrap", "result": "beta",
                             "notes": "Phase 5.1b Batch 2"}],
        evolution_history=[{"timestamp": "2026-08-07T00:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1b Batch 2"}],
    )


def build_cap_prep_materials_detect() -> Capability:
    """CAP-PREP-MATERIALS-DETECT: required materials section detection."""
    return Capability(
        id="CAP-PREP-MATERIALS-DETECT",
        name="PrepMaterialsDetection",
        layer="chapter_handler",
        description=(
            "Detects content sections listing required/preparation materials "
            "— identified by named items with discrete count indicators "
            "and list-formatted layout."
        ),
        scope={
            "problem_space": "Detection of materials/preparation sections in technical documents",
            "vocabulary": {},
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "is_materials_section": {"type": "bool", "required": True},
            "confidence": {"type": "float", "required": True},
        }},
        execution_strategy="COUNT SCAN: Detect named items with discrete count indicators.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-MATERIALS-LIST"]},
        pattern_ids=["PAT-MATERIALS-LIST"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-MATERIALS-LIST"],
        documents_tested=["DC201-C1", "VS101"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T00:00:00Z",
                             "validator": "phase5_1b_bootstrap", "result": "beta",
                             "notes": "Phase 5.1b Batch 2"}],
        evolution_history=[{"timestamp": "2026-08-07T00:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1b Batch 2"}],
    )


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 3 PATTERNS (Phase 5.1c — validation & composition)
# ═══════════════════════════════════════════════════════════════════════════


def build_patterns_v5() -> list[Pattern]:
    """Build all patterns — v4 + Batch 3 validation & composition detectors."""
    patterns = build_patterns_v4()

    pat_temp_range = Pattern(
        id="PAT-TEMP-RANGE",
        name="Temperature Range Pattern",
        description=(
            "Content containing temperature ranges — characterized by "
            "temperature values connected by range indicators (dash, 'to', '~'). "
            "Common in storage conditions, stability data, and assay protocols."
        ),
        detection_signals=[
            "temperature values connected by range separators (-, to, ~)",
            "range expressions like '2-8°C', '-20°C to -80°C'",
            "multiple temperature + time pairs in proximity",
        ],
        structural_indicators=[
            "key-value pairs with temperature as value",
            "compact parameter-like layout",
        ],
        content_indicators=[
            "temperature_range element count ≥ 1",
            "temperature element count ≥ 2",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.50,
        evidence_count=1,
        source_documents=["DC201-C1"],
        cross_doc_count=1,
        tags=["temperature", "range", "storage", "validation"],
    )

    pat_time_spec = Pattern(
        id="PAT-TIME-SPEC",
        name="Time Specification Pattern",
        description=(
            "Content containing time specifications — durations, incubation "
            "times, reaction periods. Detected by time unit patterns (min, "
            "hour, day, sec) combined with numeric values. Domain-independent."
        ),
        detection_signals=[
            "time unit words (min, hour, day, sec, minute) near numeric values",
            "duration ranges like '5-10 min', '1-2 hours'",
            "density of time expressions across the content",
        ],
        structural_indicators=[
            "time specifications in procedure or method sections",
            "paired with temperature or step sequences",
        ],
        content_indicators=[
            "time element count ≥ 2",
            "time expressions distributed across content",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.50,
        evidence_count=1,
        source_documents=["DC201-C1"],
        cross_doc_count=1,
        tags=["time", "duration", "incubation", "extraction"],
    )

    pat_catalog = Pattern(
        id="PAT-CATALOG-NUMBER",
        name="Catalog Number Pattern",
        description=(
            "Content with high density of catalog/part numbers — "
            "alphanumeric identifiers following manufacturer formats. "
            "Distinct from component tables by requiring absence of "
            "collapsed-table structure (pure catalog listing)."
        ),
        detection_signals=[
            "alphanumeric patterns (2-5 uppercase letters + 4-8 digits)",
            "catalog numbers on separate lines or in list format",
            "high catalog-to-name ratio indicates catalog listing",
        ],
        structural_indicators=[
            "list format with catalog numbers as primary content",
            "NO collapsed table structure (excludes component tables)",
            "compact format — one catalog entry per line",
        ],
        content_indicators=[
            "catalog_number element count ≥ 4",
            "catalog number density > name density",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.50,
        evidence_count=1,
        source_documents=["DC201-C1"],
        cross_doc_count=1,
        tags=["catalog", "part-number", "extraction", "identification"],
    )

    pat_quantity_integrity = Pattern(
        id="PAT-QUANTITY-INTEGRITY",
        name="Quantity Integrity Pattern",
        description=(
            "Content where multiple quantity dimensions co-exist (volume, "
            "concentration, count, weight) and need consistency validation. "
            "Detected by diversity of quantity element types in proximity."
        ),
        detection_signals=[
            "volume elements ≥ 2",
            "concentration elements ≥ 2",
            "count elements ≥ 1",
            "multiple quantity dimensions in same content block",
        ],
        structural_indicators=[
            "dense numeric content with diverse units",
            "quantity pairs that should be validated for consistency",
        ],
        content_indicators=[
            "volume + concentration + count diversity",
            "high quantity element count overall (≥ 8)",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.45,
        evidence_count=1,
        source_documents=["DC201-C1"],
        cross_doc_count=1,
        tags=["quantity", "validation", "consistency", "integrity"],
    )

    pat_unit_diversity = Pattern(
        id="PAT-UNIT-DIVERSITY",
        name="Unit Diversity Pattern",
        description=(
            "Content containing multiple distinct measurement unit types "
            "(μL, mg, mM, %, etc.) requiring normalization and consistency "
            "checking. Detected by unit type count ≥ 3 distinct categories."
        ),
        detection_signals=[
            "≥ 3 distinct unit types (μL, mg, mM, %, ng/μL, U/μL)",
            "unit elements distributed across content",
            "potential unit mismatch or inconsistency signals",
        ],
        structural_indicators=[
            "units embedded in structured (table) or semi-structured content",
            "concentration units mixed with volume/weight units",
        ],
        content_indicators=[
            "unit element count ≥ 3",
            "≥ 2 distinct unit categories",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.45,
        evidence_count=1,
        source_documents=["DC201-C1"],
        cross_doc_count=1,
        tags=["unit", "normalization", "consistency", "validation"],
    )

    pat_table_classify = Pattern(
        id="PAT-TABLE-CLASSIFY",
        name="Table Type Classification Pattern",
        description=(
            "Content with intact table structure where column types need "
            "classification — distinguishing name columns, numeric columns, "
            "date columns, and catalog columns. Requires columnar alignment "
            "WITHOUT collapse artifacts."
        ),
        detection_signals=[
            "table_structure = True",
            "column boundary artifacts (multi-space gaps or tabs)",
            "header row with column typing hints",
            "NOT collapsed — column alignment is preserved",
        ],
        structural_indicators=[
            "intact tabular layout with ≥ 3 rows",
            "column data types distinguishable by content pattern",
            "header row present with column labels",
        ],
        content_indicators=[
            "has_table_structure + line_count ≥ 6",
            "column content type diversity (text vs numeric vs date)",
        ],
        status=PatternStatus.CANDIDATE,
        confidence=0.50,
        evidence_count=1,
        source_documents=["DC201-C1", "E803"],
        cross_doc_count=2,
        tags=["table", "classification", "column", "typing"],
    )

    patterns.extend([
        pat_temp_range, pat_time_spec, pat_catalog,
        pat_quantity_integrity, pat_unit_diversity, pat_table_classify,
    ])
    return patterns


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5.2 PATTERNS — discrimination test patterns with shared signals
# ═══════════════════════════════════════════════════════════════════════════


def build_patterns_v6() -> list[Pattern]:
    """Build all patterns — v5 + Phase 5.2 discrimination-test patterns."""
    patterns = build_patterns_v5()

    # These are intentionally VERY similar to existing patterns.
    # They share structural signals with v2-v5 patterns to test discrimination.

    pat_table_basic = Pattern(
        id="PAT-TABLE-BASIC-STRUCT",
        name="Basic Table Structure (Simplified)",
        description=(
            "Simplified version of PAT-TABLE-COLLAPSE-STRUCT. Detects "
            "collapsed table artifacts with lower thresholds. Intentionally "
            "overlaps to test discrimination between established and new "
            "capabilities that share pattern signals."
        ),
        detection_signals=[
            "collapsed table with >= 3 quantity-unit pairs",
            "long segments > 150 chars",
        ],
        structural_indicators=["long unbroken text segments"],
        content_indicators=["quantity element density"],
        status=PatternStatus.CANDIDATE, confidence=0.35,
        evidence_count=0, source_documents=[], cross_doc_count=0,
        tags=["table", "basic", "discrimination-test"],
    )

    pat_param_list = Pattern(
        id="PAT-PARAMETER-LIST",
        name="Parameter List Pattern",
        description=(
            "Overlaps with PAT-ANCHOR-DRIVEN-EXTRACT — detects key-value "
            "pairs but with lower line-count threshold. Designed to compete "
            "with the established ANCHOR-EXTRACT pattern."
        ),
        detection_signals=["key-value pairs >= 2", "lower structural bar"],
        structural_indicators=["label-value layout"],
        content_indicators=["parameter-like line structure"],
        status=PatternStatus.CANDIDATE, confidence=0.35,
        evidence_count=0, source_documents=[], cross_doc_count=0,
        tags=["parameter", "list", "discrimination-test"],
    )

    pat_storage_lt = Pattern(
        id="PAT-STORAGE-LONG-TERM",
        name="Long-Term Storage Conditions",
        description=(
            "Specialization of PAT-STORAGE-CONDITIONS. Focused on long-term "
            "storage with temperature ranges. Shares temperature signal with "
            "the established pattern to test specialization discrimination."
        ),
        detection_signals=["temperature >= 1", "key-value pairs"],
        structural_indicators=["compact parameter layout"],
        content_indicators=["storage-related temperature mentions"],
        status=PatternStatus.CANDIDATE, confidence=0.35,
        evidence_count=0, source_documents=[], cross_doc_count=0,
        tags=["storage", "long-term", "discrimination-test"],
    )

    pat_warning_extract = Pattern(
        id="PAT-WARNING-EXTRACT",
        name="Warning Phrase Extraction",
        description=(
            "Specialization of PAT-SAFETY-WARNINGS. Focused on extracting "
            "individual warning phrases rather than detecting sections."
        ),
        detection_signals=["header count >= 1", "capitalized lines"],
        structural_indicators=["header-like lines"],
        content_indicators=["warning keywords in proximity"],
        status=PatternStatus.CANDIDATE, confidence=0.35,
        evidence_count=0, source_documents=[], cross_doc_count=0,
        tags=["warning", "extraction", "discrimination-test"],
    )

    pat_step_count = Pattern(
        id="PAT-STEP-COUNT",
        name="Step Counting Pattern",
        description=(
            "Specialization of PAT-PROCEDURE-STEPS. Focused on counting "
            "steps rather than understanding the procedure."
        ),
        detection_signals=["line count >= 5", "enumerated lines"],
        structural_indicators=["numbered or bulleted sequence"],
        content_indicators=["step indicator density"],
        status=PatternStatus.CANDIDATE, confidence=0.35,
        evidence_count=0, source_documents=[], cross_doc_count=0,
        tags=["step", "counting", "discrimination-test"],
    )

    patterns.extend([
        pat_table_basic, pat_param_list, pat_storage_lt,
        pat_warning_extract, pat_step_count,
    ])
    return patterns


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5.2 CAPABILITIES — highly similar discrimination-test caps
# ═══════════════════════════════════════════════════════════════════════════


def build_cap_table_extract_basic() -> Capability:
    """CAP-TABLE-EXTRACT-BASIC: simpler version sharing PAT-TABLE-COLLAPSE-STRUCT."""
    return Capability(
        id="CAP-TABLE-EXTRACT-BASIC",
        name="BasicTableExtraction",
        layer="chapter_handler",
        description=(
            "Simplified table extraction — shares PAT-TABLE-COLLAPSE-STRUCT "
            "with CAP-TABLE-COLLAPSE-RECONSTRUCT but with lower evidence and "
            "narrower scope. Designed to test ranking discrimination."
        ),
        scope={"problem_space": "Basic table entry reconstruction"},
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 30}},
        output_schema={"fields": {"entries": {"type": "list[str]", "required": True},
                                   "entry_count": {"type": "int", "required": True}}},
        execution_strategy="BASIC RECONSTRUCT: Split collapsed table by structural boundaries.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 30,
                               "preferred_patterns": ["PAT-TABLE-COLLAPSE-STRUCT"]},
        pattern_ids=["PAT-TABLE-COLLAPSE-STRUCT", "PAT-TABLE-BASIC-STRUCT"],
        status=CapabilityStatus.PROPOSED,
        source_pattern_ids=["PAT-TABLE-COLLAPSE-STRUCT"],
        documents_tested=[], cross_doc_success_rate=0.0,
        version=1, epoch=0,
        validation_history=[{"timestamp": "2026-08-07T12:00:00Z",
                             "validator": "phase5_2_bootstrap", "result": "candidate",
                             "notes": "Phase 5.2 discrimination test — intentionally similar to CAP-TABLE-COLLAPSE-RECONSTRUCT"}],
        evolution_history=[{"timestamp": "2026-08-07T12:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.2: discrimination test cap"}],
    )


def build_cap_parameter_list() -> Capability:
    """CAP-PARAMETER-LIST: shares PAT-ANCHOR-DRIVEN-EXTRACT with CAP-ANCHOR-EXTRACT."""
    return Capability(
        id="CAP-PARAMETER-LIST",
        name="ParameterListExtraction",
        layer="extraction_rule",
        description=(
            "Simplified parameter list extraction — shares PAT-ANCHOR-DRIVEN-EXTRACT "
            "with CAP-ANCHOR-EXTRACT but with lower evidence. Designed to test "
            "discrimination between established and new extraction caps."
        ),
        scope={"problem_space": "Generic parameter list from key-value pairs"},
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {"parameters": {"type": "list[dict]", "required": True},
                                   "count": {"type": "int", "required": True}}},
        execution_strategy="PARAM SCAN: Simple Label: Value pair extraction.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-ANCHOR-DRIVEN-EXTRACT"]},
        pattern_ids=["PAT-ANCHOR-DRIVEN-EXTRACT", "PAT-PARAMETER-LIST"],
        status=CapabilityStatus.PROPOSED,
        source_pattern_ids=["PAT-ANCHOR-DRIVEN-EXTRACT"],
        documents_tested=[], cross_doc_success_rate=0.0,
        version=1, epoch=0,
        validation_history=[{"timestamp": "2026-08-07T12:00:00Z",
                             "validator": "phase5_2_bootstrap", "result": "candidate",
                             "notes": "Phase 5.2: similar to CAP-ANCHOR-EXTRACT"}],
        evolution_history=[{"timestamp": "2026-08-07T12:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.2 discrimination test"}],
    )


def build_cap_storage_long_term() -> Capability:
    """CAP-STORAGE-LONG-TERM: shares PAT-STORAGE-CONDITIONS with CAP-STORAGE-DETECT."""
    return Capability(
        id="CAP-STORAGE-LONG-TERM",
        name="LongTermStorageDetection",
        layer="chapter_handler",
        description=(
            "Long-term storage specialization — shares PAT-STORAGE-CONDITIONS "
            "with CAP-STORAGE-DETECT. Narrower scope, lower evidence. Tests "
            "specialization vs generalization ranking."
        ),
        scope={"problem_space": "Long-term storage conditions (temp + duration)"},
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {"conditions": {"type": "list[dict]", "required": True},
                                   "count": {"type": "int", "required": True}}},
        execution_strategy="LONG-TERM SCAN: Storage condition with temperature range.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-STORAGE-CONDITIONS"]},
        pattern_ids=["PAT-STORAGE-CONDITIONS", "PAT-STORAGE-LONG-TERM"],
        status=CapabilityStatus.PROPOSED,
        source_pattern_ids=["PAT-STORAGE-CONDITIONS"],
        documents_tested=[], cross_doc_success_rate=0.0,
        version=1, epoch=0,
        validation_history=[{"timestamp": "2026-08-07T12:00:00Z",
                             "validator": "phase5_2_bootstrap", "result": "candidate",
                             "notes": "Phase 5.2: similar to CAP-STORAGE-DETECT"}],
        evolution_history=[{"timestamp": "2026-08-07T12:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.2 discrimination test"}],
    )


def build_cap_warning_extract() -> Capability:
    """CAP-WARNING-EXTRACT: shares PAT-SAFETY-WARNINGS with CAP-SAFETY-DETECT."""
    return Capability(
        id="CAP-WARNING-EXTRACT",
        name="WarningPhraseExtraction",
        layer="extraction_rule",
        description=(
            "Warning phrase extraction — shares PAT-SAFETY-WARNINGS with "
            "CAP-SAFETY-DETECT. Extraction-level vs detection-level. Tests "
            "cross-layer related-capability discrimination."
        ),
        scope={"problem_space": "Individual warning phrase extraction"},
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {"warnings": {"type": "list[str]", "required": True},
                                   "count": {"type": "int", "required": True}}},
        execution_strategy="WARNING SCAN: Extract individual caution/warning/danger phrases.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-SAFETY-WARNINGS"]},
        pattern_ids=["PAT-SAFETY-WARNINGS", "PAT-WARNING-EXTRACT"],
        status=CapabilityStatus.PROPOSED,
        source_pattern_ids=["PAT-SAFETY-WARNINGS"],
        documents_tested=[], cross_doc_success_rate=0.0,
        version=1, epoch=0,
        validation_history=[{"timestamp": "2026-08-07T12:00:00Z",
                             "validator": "phase5_2_bootstrap", "result": "candidate",
                             "notes": "Phase 5.2: similar to CAP-SAFETY-DETECT"}],
        evolution_history=[{"timestamp": "2026-08-07T12:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.2 discrimination test"}],
    )


def build_cap_step_counter() -> Capability:
    """CAP-STEP-COUNTER: shares PAT-PROCEDURE-STEPS with CAP-PROCEDURE-DETECT."""
    return Capability(
        id="CAP-STEP-COUNTER",
        name="StepCounter",
        layer="extraction_rule",
        description=(
            "Step counting — shares PAT-PROCEDURE-STEPS with CAP-PROCEDURE-DETECT. "
            "Extraction-level simple counter vs detection-level procedure understanding. "
            "Tests narrow extraction vs broad detection ranking."
        ),
        scope={"problem_space": "Count procedure steps in enumerated content"},
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {"step_count": {"type": "int", "required": True},
                                   "steps": {"type": "list[str]", "required": True}}},
        execution_strategy="STEP COUNT: Count enumerated steps in content.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-PROCEDURE-STEPS"]},
        pattern_ids=["PAT-PROCEDURE-STEPS", "PAT-STEP-COUNT"],
        status=CapabilityStatus.PROPOSED,
        source_pattern_ids=["PAT-PROCEDURE-STEPS"],
        documents_tested=[], cross_doc_success_rate=0.0,
        version=1, epoch=0,
        validation_history=[{"timestamp": "2026-08-07T12:00:00Z",
                             "validator": "phase5_2_bootstrap", "result": "candidate",
                             "notes": "Phase 5.2: similar to CAP-PROCEDURE-DETECT"}],
        evolution_history=[{"timestamp": "2026-08-07T12:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.2 discrimination test"}],
    )


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5.2 IMPLEMENTATIONS & RULES
# ═══════════════════════════════════════════════════════════════════════════


def build_phase5_2_implementations() -> list[Implementation]:
    """Build implementations for Phase 5.2 discrimination-test caps."""
    return [
        Implementation(id="IMPL-TABLE-BASIC", capability_id="CAP-TABLE-EXTRACT-BASIC",
                       name="Basic Table Extractor", strategy="basic_reconstruct",
                       config={"signals": ["has_collapsed_table", "quantity"]}),
        Implementation(id="IMPL-PARAM-LIST", capability_id="CAP-PARAMETER-LIST",
                       name="Parameter List Extractor", strategy="param_scan",
                       config={"signals": ["key_value_pairs"]}),
        Implementation(id="IMPL-STORAGE-LT", capability_id="CAP-STORAGE-LONG-TERM",
                       name="Long-Term Storage Detector", strategy="lt_storage_scan",
                       config={"signals": ["temperature", "key_value_pairs"]}),
        Implementation(id="IMPL-WARNING-EXTRACT", capability_id="CAP-WARNING-EXTRACT",
                       name="Warning Phrase Extractor", strategy="warning_scan",
                       config={"signals": ["header_count", "capitalized_lines"]}),
        Implementation(id="IMPL-STEP-COUNT", capability_id="CAP-STEP-COUNTER",
                       name="Step Counter", strategy="step_count",
                       config={"signals": ["line_count", "list_structure"]}),
    ]


def build_phase5_2_rules() -> list[Rule]:
    """Build rules for Phase 5.2 discrimination-test caps."""
    return [
        Rule(id="RULE-TABLE-BASIC", implementation_id="IMPL-TABLE-BASIC",
             name="Basic Table Boundary", rule_type="threshold",
             pattern="", description="Detect basic table boundaries", priority=1),
        Rule(id="RULE-PARAM-LIST", implementation_id="IMPL-PARAM-LIST",
             name="Parameter List Rule", rule_type="regex",
             pattern=r"^([A-Z][a-zA-Z\s]{2,30}):\s*(.+)$",
             description="Extract parameter key-value pairs", priority=1),
        Rule(id="RULE-STORAGE-LT", implementation_id="IMPL-STORAGE-LT",
             name="Long-Term Storage Rule", rule_type="threshold",
             pattern="", description="Detect long-term storage conditions", priority=1),
        Rule(id="RULE-WARNING-EXTRACT", implementation_id="IMPL-WARNING-EXTRACT",
             name="Warning Extraction Rule", rule_type="regex",
             pattern=r"(Warning|Caution|Danger|Note)\s*[:\-]\s*(.+)",
             description="Extract warning/caution phrases", priority=1),
        Rule(id="RULE-STEP-COUNT", implementation_id="IMPL-STEP-COUNT",
             name="Step Counting Rule", rule_type="regex",
             pattern=r"(\d+)[.)]\s+",
             description="Count enumerated steps", priority=1),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 3 CAPABILITIES (Phase 5.1c — validation & composition)
# ═══════════════════════════════════════════════════════════════════════════


def build_cap_temp_range() -> Capability:
    """CAP-TEMP-RANGE: temperature range detection and parsing."""
    return Capability(
        id="CAP-TEMP-RANGE",
        name="TemperatureRangeExtraction",
        layer="extraction_rule",
        description=(
            "Detects and parses temperature ranges from text content. "
            "Extracts min/max values, units, and range type (explicit "
            "range, single point, or storage condition). Validates "
            "temperature values against physical plausibility."
        ),
        scope={
            "problem_space": "Temperature range extraction and validation in technical docs",
            "vocabulary": {},
            "range_patterns": [
                r"(-?\d+(?:\.\d+)?)\s*(?:-|to|~)\s*(-?\d+(?:\.\d+)?)\s*(?:℃|°C)",
                r"(-?\d+(?:\.\d+)?)\s*(?:℃|°C)\s*(?:-|to|~)\s*(-?\d+(?:\.\d+)?)\s*(?:℃|°C)",
                r"(?:store\s+)?at\s+(-?\d+(?:\.\d+)?)\s*(?:℃|°C)",
            ],
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "ranges": {"type": "list[dict]", "required": True},
            "range_count": {"type": "int", "required": True},
            "single_points": {"type": "list[float]", "required": False},
        }},
        execution_strategy="RANGE SCAN: Detect temp ranges via regex, extract min/max, validate.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-TEMP-RANGE"]},
        pattern_ids=["PAT-TEMP-RANGE"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-TEMP-RANGE"],
        documents_tested=["DC201-C1"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3: validation capability"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


def build_cap_time_extract() -> Capability:
    """CAP-TIME-EXTRACT: time specification detection and extraction."""
    return Capability(
        id="CAP-TIME-EXTRACT",
        name="TimeSpecExtraction",
        layer="extraction_rule",
        description=(
            "Detects and extracts time specifications from text — "
            "durations, incubation times, reaction periods. Parses "
            "numeric+unit pairs (30 min, 1 hour, 5 days) and "
            "duration ranges (5-10 min). Normalizes to standard units."
        ),
        scope={
            "problem_space": "Time specification extraction from technical protocols",
            "vocabulary": {},
            "time_patterns": [
                r"(\d+(?:\.\d+)?)\s*(min|minute|hour|hr|day|sec|second|s)\b",
                r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(min|hour|day)",
            ],
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "durations": {"type": "list[dict]", "required": True},
            "duration_count": {"type": "int", "required": True},
            "total_time_estimate": {"type": "str", "required": False},
        }},
        execution_strategy="TIME SCAN: Detect time expressions via regex, normalize units.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-TIME-SPEC"]},
        pattern_ids=["PAT-TIME-SPEC"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-TIME-SPEC"],
        documents_tested=["DC201-C1"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


def build_cap_catalog_extract() -> Capability:
    """CAP-CATALOG-EXTRACT: catalog/part number extraction."""
    return Capability(
        id="CAP-CATALOG-EXTRACT",
        name="CatalogNumberExtraction",
        layer="extraction_rule",
        description=(
            "Detects and extracts catalog/part numbers from text. "
            "Identifies alphanumeric patterns matching manufacturer "
            "format conventions. Requires high catalog density and "
            "absence of collapsed-table structure to avoid competing "
            "with component table extraction."
        ),
        scope={
            "problem_space": "Catalog number extraction from technical documentation",
            "vocabulary": {},
            "catalog_patterns": [
                r"\b([A-Z]{2,5}[-\s]?\d{4,8}(?:[-\s]\d+)?)\b",
                r"\b(\d{6,12})\b",
            ],
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "catalog_numbers": {"type": "list[str]", "required": True},
            "catalog_count": {"type": "int", "required": True},
            "format_detected": {"type": "str", "required": False},
        }},
        execution_strategy="CATALOG SCAN: Detect alphanumeric ID patterns, exclude comp tables.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-CATALOG-NUMBER"]},
        pattern_ids=["PAT-CATALOG-NUMBER"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-CATALOG-NUMBER"],
        documents_tested=["DC201-C1"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


def build_cap_quantity_validate() -> Capability:
    """CAP-QUANTITY-VALIDATE: cross-dimensional quantity validation."""
    return Capability(
        id="CAP-QUANTITY-VALIDATE",
        name="QuantityConsistencyValidation",
        layer="parameter_constraint",
        description=(
            "Validates quantity consistency across multiple dimensions "
            "(volume, concentration, count, weight). Checks that related "
            "quantities are internally consistent — e.g., total volume "
            "vs component volumes, concentration vs dilution factor."
        ),
        scope={
            "problem_space": "Cross-dimensional quantity validation in technical content",
            "vocabulary": {},
            "validation_rules": [
                "volume_consistency: component volumes ≤ total volume",
                "concentration_range: concentration values within documented limits",
                "count_integrity: discrete counts match listed items",
            ],
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 30}},
        output_schema={"fields": {
            "validations": {"type": "list[dict]", "required": True},
            "violations": {"type": "list[dict]", "required": True},
            "overall_integrity": {"type": "float", "required": True},
        }},
        execution_strategy="INTEGRITY CHECK: Cross-validate quantities across dimensions.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 30,
                               "preferred_patterns": ["PAT-QUANTITY-INTEGRITY"]},
        pattern_ids=["PAT-QUANTITY-INTEGRITY"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-QUANTITY-INTEGRITY"],
        documents_tested=["DC201-C1"],
        cross_doc_success_rate=0.35,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3: parameter constraint layer"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


def build_cap_unit_consistency() -> Capability:
    """CAP-UNIT-CONSISTENCY: unit normalization and consistency."""
    return Capability(
        id="CAP-UNIT-CONSISTENCY",
        name="UnitConsistencyValidation",
        layer="parameter_constraint",
        description=(
            "Validates unit consistency and performs normalization. "
            "Detects mixed unit conventions (μL vs ul, mg vs MG), "
            "identifies potential unit errors, and normalizes to "
            "standard representations. Requires diverse unit presence."
        ),
        scope={
            "problem_space": "Unit normalization and consistency checking",
            "vocabulary": {},
            "normalization_map": UNIT_NORMALIZATION,
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 20}},
        output_schema={"fields": {
            "normalized_units": {"type": "list[dict]", "required": True},
            "inconsistencies": {"type": "list[dict]", "required": True},
            "unit_types_detected": {"type": "list[str]", "required": True},
        }},
        execution_strategy="UNIT SCAN: Detect all units, normalize variants, flag inconsistencies.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 20,
                               "preferred_patterns": ["PAT-UNIT-DIVERSITY"]},
        pattern_ids=["PAT-UNIT-DIVERSITY"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-UNIT-DIVERSITY"],
        documents_tested=["DC201-C1"],
        cross_doc_success_rate=0.35,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


def build_cap_table_type_classify() -> Capability:
    """CAP-TABLE-TYPE-CLASSIFY: table column type classification."""
    return Capability(
        id="CAP-TABLE-TYPE-CLASSIFY",
        name="TableTypeClassification",
        layer="chapter_handler",
        description=(
            "Classifies table column types from intact tabular content. "
            "Distinguishes name columns, numeric columns, date columns, "
            "and catalog columns based on content patterns. Requires "
            "intact (non-collapsed) table structure."
        ),
        scope={
            "problem_space": "Table column type classification for structured extraction",
            "vocabulary": {},
            "column_types": ["name", "numeric", "date", "catalog", "text", "mixed"],
        },
        input_schema={"fields": {"content": {"type": "str", "required": True}},
                      "constraints": {"min_content_length": 30}},
        output_schema={"fields": {
            "column_types": {"type": "list[dict]", "required": True},
            "columns_detected": {"type": "int", "required": True},
            "table_type": {"type": "str", "required": True},
        }},
        execution_strategy="COLUMN CLASSIFY: Analyze column content to classify data types.",
        evidence_requirements={"min_pattern_matches": 1, "min_content_length": 30,
                               "preferred_patterns": ["PAT-TABLE-CLASSIFY"]},
        pattern_ids=["PAT-TABLE-CLASSIFY"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-TABLE-CLASSIFY"],
        documents_tested=["DC201-C1", "E803"],
        cross_doc_success_rate=0.40,
        version=1, epoch=1,
        validation_history=[{"timestamp": "2026-08-07T10:00:00Z",
                             "validator": "phase5_1c_bootstrap", "result": "beta",
                             "notes": "Phase 5.1c Batch 3"}],
        evolution_history=[{"timestamp": "2026-08-07T10:00:00Z",
                            "change": "initial_registration",
                            "detail": "Phase 5.1c Batch 3"}],
    )


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 2 IMPLEMENTATIONS & RULES
# ═══════════════════════════════════════════════════════════════════════════


def build_batch2_implementations() -> list[Implementation]:
    """Build implementations for all Batch 2 capabilities."""
    return [
        Implementation(id="IMPL-STORAGE-DETECT", capability_id="CAP-STORAGE-DETECT",
                       name="Storage Signal Scanner", strategy="signal_scan",
                       config={"signals": ["temperature", "key_value_pairs"]}),
        Implementation(id="IMPL-SAFETY-DETECT", capability_id="CAP-SAFETY-DETECT",
                       name="Warning Header Scanner", strategy="header_scan",
                       config={"signals": ["header_density", "list_structure"]}),
        Implementation(id="IMPL-TROUBLESHOOT-DETECT", capability_id="CAP-TROUBLESHOOT-DETECT",
                       name="QA Pattern Scanner", strategy="qa_scan",
                       config={"signals": ["list_structure", "headers"]}),
        Implementation(id="IMPL-PROCEDURE-DETECT", capability_id="CAP-PROCEDURE-DETECT",
                       name="Procedure Length Scanner", strategy="length_scan",
                       config={"signals": ["line_count", "list_structure"]}),
        Implementation(id="IMPL-MATERIALS-DETECT", capability_id="CAP-PREP-MATERIALS-DETECT",
                       name="Materials Count Scanner", strategy="count_scan",
                       config={"signals": ["name_count", "count_indicators"]}),
    ]


def build_batch2_rules() -> list[Rule]:
    """Build rules for all Batch 2 capabilities."""
    return [
        Rule(id="RULE-STORAGE-SIGNAL", implementation_id="IMPL-STORAGE-DETECT",
             name="Temperature Signal Rule", rule_type="threshold",
             pattern="", description="Check temperature element count ≥ 1", priority=1),
        Rule(id="RULE-SAFETY-SIGNAL", implementation_id="IMPL-SAFETY-DETECT",
             name="Header Density Rule", rule_type="threshold",
             pattern="", description="Check header count ≥ 2", priority=1),
        Rule(id="RULE-TROUBLESHOOT-SIGNAL", implementation_id="IMPL-TROUBLESHOOT-DETECT",
             name="QA Structure Rule", rule_type="threshold",
             pattern="", description="Check list + header presence", priority=1),
        Rule(id="RULE-PROCEDURE-SIGNAL", implementation_id="IMPL-PROCEDURE-DETECT",
             name="Length Threshold Rule", rule_type="threshold",
             pattern="", description="Check line count ≥ 12", priority=1),
        Rule(id="RULE-MATERIALS-SIGNAL", implementation_id="IMPL-MATERIALS-DETECT",
             name="Materials Count Rule", rule_type="threshold",
             pattern="", description="Check name ≥ 2 + count ≥ 1", priority=1),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 3 IMPLEMENTATIONS & RULES (Phase 5.1c)
# ═══════════════════════════════════════════════════════════════════════════


def build_batch3_implementations() -> list[Implementation]:
    """Build implementations for all Batch 3 capabilities."""
    return [
        Implementation(id="IMPL-TEMP-RANGE", capability_id="CAP-TEMP-RANGE",
                       name="Temperature Range Scanner", strategy="range_scan",
                       config={"signals": ["temperature_range", "key_value_pairs"]}),
        Implementation(id="IMPL-TIME-EXTRACT", capability_id="CAP-TIME-EXTRACT",
                       name="Time Expression Scanner", strategy="time_scan",
                       config={"signals": ["time", "numeric_density"]}),
        Implementation(id="IMPL-CATALOG-EXTRACT", capability_id="CAP-CATALOG-EXTRACT",
                       name="Catalog Number Scanner", strategy="catalog_scan",
                       config={"signals": ["catalog_number", "list_structure"]}),
        Implementation(id="IMPL-QUANTITY-VALIDATE", capability_id="CAP-QUANTITY-VALIDATE",
                       name="Quantity Integrity Validator", strategy="integrity_check",
                       config={"signals": ["volume", "concentration", "count"]}),
        Implementation(id="IMPL-UNIT-CONSISTENCY", capability_id="CAP-UNIT-CONSISTENCY",
                       name="Unit Normalization Scanner", strategy="unit_scan",
                       config={"signals": ["unit", "concentration"]}),
        Implementation(id="IMPL-TABLE-CLASSIFY", capability_id="CAP-TABLE-TYPE-CLASSIFY",
                       name="Table Column Classifier", strategy="column_classify",
                       config={"signals": ["table_structure", "header_count"]}),
    ]


def build_batch3_rules() -> list[Rule]:
    """Build rules for all Batch 3 capabilities."""
    return [
        Rule(id="RULE-TEMP-RANGE", implementation_id="IMPL-TEMP-RANGE",
             name="Temperature Range Detection", rule_type="regex",
             pattern=r"(-?\d+(?:\.\d+)?)\s*(?:-|to|~)\s*(-?\d+(?:\.\d+)?)\s*(?:℃|°C)",
             description="Detect temperature ranges with separators", priority=1),
        Rule(id="RULE-TIME-EXTRACT", implementation_id="IMPL-TIME-EXTRACT",
             name="Time Expression Extraction", rule_type="regex",
             pattern=r"(\d+(?:\.\d+)?)\s*(min|minute|hour|hr|day|sec|second)",
             description="Extract time durations with units", priority=1),
        Rule(id="RULE-CATALOG-EXTRACT", implementation_id="IMPL-CATALOG-EXTRACT",
             name="Catalog Number Extraction", rule_type="regex",
             pattern=r"\b([A-Z]{2,5}[-\s]?\d{4,8}(?:[-\s]\d+)?)\b",
             description="Extract alphanumeric catalog numbers", priority=1),
        Rule(id="RULE-QUANTITY-CHECK", implementation_id="IMPL-QUANTITY-VALIDATE",
             name="Quantity Consistency Check", rule_type="schema",
             pattern="", description="Cross-validate quantity dimensions", priority=1),
        Rule(id="RULE-UNIT-NORMALIZE", implementation_id="IMPL-UNIT-CONSISTENCY",
             name="Unit Normalization", rule_type="keyword",
             pattern="", description="Normalize unit variants to standard", priority=1),
        Rule(id="RULE-TABLE-COLUMN-TYPE", implementation_id="IMPL-TABLE-CLASSIFY",
             name="Column Type Classification", rule_type="schema",
             pattern="", description="Classify table columns by content type", priority=1),
    ]


def build_cap_table_collapse_reconstruct() -> Capability:
    """CAP-TABLE-COLLAPSE-RECONSTRUCT: generic collapsed table reconstruction."""
    return Capability(
        id="CAP-TABLE-COLLAPSE-RECONSTRUCT",
        name="CollapsedTableReconstruction",
        layer="chapter_handler",
        description=(
            "Detects and reconstructs entries from text-collapsed tables "
            "in any document type. Uses structural signals (line length, "
            "numeric density, segment patterns) to identify collapsed "
            "table regions and reconstruct individual entries. "
            "Completely domain-independent."
        ),
        scope={
            "problem_space": (
                "Reconstructing structured entries from text that was "
                "originally a table but collapsed into undelimited text "
                "during extraction. Based solely on structural patterns."
            ),
            "vocabulary": {},  # domain-independent — no vocabulary
            "quantity_patterns": QUANTITY_PATTERNS,
            "unit_normalization": UNIT_NORMALIZATION,
        },
        input_schema={
            "fields": {
                "content": {"type": "str", "required": True,
                            "description": "Raw text content"},
            },
            "constraints": {
                "min_content_length": 30,
                "max_content_length": 50000,
            },
        },
        output_schema={
            "fields": {
                "reconstructed_entries": {"type": "list[str]", "required": True},
                "entry_count": {"type": "int", "required": True},
                "confidence": {"type": "float", "required": True},
            },
        },
        execution_strategy=(
            "ENTRY RECONSTRUCTION: Scan text for structural boundaries "
            "(quantity-unit pairs, catalog-number patterns) that indicate "
            "original row boundaries. Split text at these boundaries to "
            "reconstruct individual table entries."
        ),
        evidence_requirements={
            "min_pattern_matches": 1,
            "min_content_length": 30,
            "preferred_patterns": ["PAT-TABLE-COLLAPSE-STRUCT"],
        },
        pattern_ids=["PAT-TABLE-COLLAPSE-STRUCT"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-TABLE-COLLAPSE-STRUCT"],
        documents_tested=["DC201-C1", "NDB609", "VSMB101"],
        cross_doc_success_rate=0.50,
        version=1,
        epoch=1,
        validation_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "validator": "phase5_1a_bootstrap",
            "result": "beta",
            "notes": "Bootstrapped from Phase 3.2 PAT-CAND-004. Beta status — cross-doc validation pending.",
        }],
        evolution_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "change": "initial_registration",
            "detail": "Phase 5.1a Batch 1: promoted from Pattern Candidate",
        }],
    )


def build_cap_anchor_extract() -> Capability:
    """CAP-ANCHOR-EXTRACT: anchor-driven key-value extraction."""
    return Capability(
        id="CAP-ANCHOR-EXTRACT",
        name="AnchorDrivenExtraction",
        layer="extraction_rule",
        description=(
            "Extracts structured key-value pairs from content organized "
            "as Label: Value patterns. Uses the label as an anchor to "
            "locate and extract the associated value. Works across "
            "specifications, parameters, storage conditions, and "
            "configuration sections."
        ),
        scope={
            "problem_space": (
                "Structured extraction from key-value formatted text "
                "where labels serve as anchors for values. Common in "
                "parameter tables, storage specifications, and "
                "configuration sections."
            ),
            "vocabulary": {},
            "anchor_patterns": [
                r"^([A-Z][a-zA-Z\s]{2,30}):\s*(.+)$",
                r"^([A-Z][a-zA-Z\s]{2,30})\s*=\s*(.+)$",
            ],
        },
        input_schema={
            "fields": {
                "content": {"type": "str", "required": True},
            },
            "constraints": {
                "min_content_length": 20,
            },
        },
        output_schema={
            "fields": {
                "pairs": {"type": "list[dict]", "required": True},
                "pair_count": {"type": "int", "required": True},
            },
        },
        execution_strategy=(
            "ANCHOR SCAN: Detect Label: Value patterns via regex. "
            "Extract label as key and subsequent content as value. "
            "Normalize units and values."
        ),
        evidence_requirements={
            "min_pattern_matches": 1,
            "min_content_length": 20,
            "preferred_patterns": ["PAT-ANCHOR-DRIVEN-EXTRACT"],
        },
        pattern_ids=["PAT-ANCHOR-DRIVEN-EXTRACT"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-ANCHOR-DRIVEN-EXTRACT"],
        documents_tested=["DC201-C1", "NH101", "VS101"],
        cross_doc_success_rate=0.50,
        version=1,
        epoch=1,
        validation_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "validator": "phase5_1a_bootstrap",
            "result": "beta",
            "notes": "Bootstrapped from Phase 3.2 PAT-CAND-003.",
        }],
        evolution_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "change": "initial_registration",
            "detail": "Phase 5.1a Batch 1: promoted from Pattern Candidate",
        }],
    )


def build_cap_columnar_extract() -> Capability:
    """CAP-COLUMNAR-EXTRACT: column-aligned text structured extraction."""
    return Capability(
        id="CAP-COLUMNAR-EXTRACT",
        name="ColumnarTextExtraction",
        layer="extraction_rule",
        description=(
            "Extracts structured data from text with intact column "
            "alignment. Identifies column boundaries from multi-space "
            "gaps or tab separators, then extracts per-column values. "
            "Works on any tabular text where the column structure is "
            "still visible."
        ),
        scope={
            "problem_space": (
                "Structured extraction from column-aligned text where "
                "column positions are preserved by spaces or tabs. "
                "Columns may contain names, quantities, units, or dates."
            ),
            "vocabulary": {},
            "column_detection": {
                "min_column_gap": 2,  # spaces
                "max_columns": 6,
            },
        },
        input_schema={
            "fields": {
                "content": {"type": "str", "required": True},
            },
            "constraints": {
                "min_content_length": 30,
            },
        },
        output_schema={
            "fields": {
                "columns": {"type": "list[list[str]]", "required": True},
                "row_count": {"type": "int", "required": True},
                "column_count": {"type": "int", "required": True},
            },
        },
        execution_strategy=(
            "COLUMN DETECTION: Identify column boundaries by analyzing "
            "character-position gaps across consecutive lines. Extract "
            "each column's content independently."
        ),
        evidence_requirements={
            "min_pattern_matches": 1,
            "min_content_length": 30,
            "preferred_patterns": ["PAT-COLUMNAR-ALIGNMENT"],
        },
        pattern_ids=["PAT-COLUMNAR-ALIGNMENT"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-COLUMNAR-ALIGNMENT"],
        documents_tested=["DC201-C1", "E803", "NDB609"],
        cross_doc_success_rate=0.50,
        version=1,
        epoch=1,
        validation_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "validator": "phase5_1a_bootstrap",
            "result": "beta",
            "notes": "Bootstrapped from Phase 3.2 PAT-CAND-005.",
        }],
        evolution_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "change": "initial_registration",
            "detail": "Phase 5.1a Batch 1: promoted from Pattern Candidate",
        }],
    )


def build_cap_name_qty_pair() -> Capability:
    """CAP-NAME-QTY-PAIR: Name→Quantity→Unit triple identification."""
    return Capability(
        id="CAP-NAME-QTY-PAIR",
        name="NameQuantityPairExtraction",
        layer="extraction_rule",
        description=(
            "Identifies and extracts Name→Quantity→Unit triples from "
            "text. Detects sequences where a named entity is followed "
            "by a numeric quantity and a unit of measurement within "
            "close proximity. Domain-independent — works on any content "
            "with name-quantity patterns."
        ),
        scope={
            "problem_space": (
                "Extracting (name, quantity, unit) triples from text "
                "where names and quantities appear in close proximity. "
                "The name is detected as a multi-word capitalized phrase, "
                "the quantity as a number, and the unit as a standard "
                "measurement abbreviation."
            ),
            "vocabulary": {},
            "quantity_patterns": QUANTITY_PATTERNS,
            "unit_normalization": UNIT_NORMALIZATION,
            "triple_proximity": 60,  # max chars between name and quantity
        },
        input_schema={
            "fields": {
                "content": {"type": "str", "required": True},
            },
            "constraints": {
                "min_content_length": 20,
            },
        },
        output_schema={
            "fields": {
                "triples": {"type": "list[dict]", "required": True},
                "triple_count": {"type": "int", "required": True},
            },
        },
        execution_strategy=(
            "TRIPLE SCAN: Scan text for sequences of: multi-word "
            "capitalized phrase → numeric value → unit symbol, within "
            "a configurable proximity window. Extract as structured "
            "(name, quantity, unit) triples."
        ),
        evidence_requirements={
            "min_pattern_matches": 1,
            "min_content_length": 20,
            "preferred_patterns": ["PAT-NAME-QUANTITY-TRIPLE"],
        },
        pattern_ids=["PAT-NAME-QUANTITY-TRIPLE"],
        status=CapabilityStatus.BETA,
        source_pattern_ids=["PAT-NAME-QUANTITY-TRIPLE"],
        documents_tested=["DC201-C1", "DC201-C2", "NDB609"],
        cross_doc_success_rate=0.50,
        version=1,
        epoch=1,
        validation_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "validator": "phase5_1a_bootstrap",
            "result": "beta",
            "notes": "Bootstrapped from Phase 3.2 PAT-CAND-001.",
        }],
        evolution_history=[{
            "timestamp": "2026-08-07T00:00:00Z",
            "change": "initial_registration",
            "detail": "Phase 5.1a Batch 1: promoted from Pattern Candidate",
        }],
    )


def build_cap_unspsc_match() -> Capability:
    """CAP-UNSPSC-MATCH: laboratory product → UNSPSC classification (Phase 10, PROPOSED)."""
    return Capability(
        id="CAP-UNSPSC-MATCH",
        name="UnspscProductClassificationMatching",
        layer="extraction_rule",
        description=(
            "Maps laboratory product records (name / description / catalog number) "
            "to UNSPSC classification codes. Derives the 8-digit UNSPSC code "
            "(Segment-Family-Class-Commodity) from the product's semantic features. "
            "Distinct from catalog number extraction (CAP-CATALOG-EXTRACT): this "
            "capability classifies by semantic category, not by alphanumeric pattern."
        ),
        scope={
            "problem_space": "Classification of laboratory product records into the UNSPSC taxonomy",
            "vocabulary": {},
            "unspsc_domain": "laboratory_products",
        },
        input_schema={
            "fields": {
                "product_name": {"type": "str", "required": True},
                "product_description": {"type": "str", "required": False},
                "catalog_number": {"type": "str", "required": False},
            },
            "constraints": {"min_content_length": 1},
        },
        output_schema={
            "fields": {
                "unspsc_code": {"type": "str", "required": True},
                "segment": {"type": "str", "required": True},
                "family": {"type": "str", "required": True},
                "class": {"type": "str", "required": True},
                "commodity": {"type": "str", "required": True},
                "match_basis": {"type": "str", "required": False},
            },
        },
        execution_strategy=(
            "UNSPSC MATCH: Identify semantic features of a laboratory product record "
            "and map them to the UNSPSC taxonomy. Describes WHAT to derive, not HOW "
            "(no if-else procedure, no scoring, no ranking)."
        ),
        evidence_requirements={
            "min_pattern_matches": 0,
            "min_content_length": 1,
            "validation_gate": "cross_document_unspsc_accuracy",
        },
        pattern_ids=[],
        implementation_ids=[],
        # ── Phase 0.6 Schema Extension: Capability Definition ──
        positive_boundary={
            "definition": (
                "Classification of a laboratory product record into the UNSPSC "
                "taxonomy, deriving an 8-digit code from the product's semantic "
                "identity (what the product IS, not how it is cataloged)."
            ),
            "core_structure": "product identity → UNSPSC semantic category",
            "input_forms": ["product_name", "product_description", "catalog_number"],
            "output_forms": ["unspsc_code", "segment", "family", "class", "commodity"],
            "domain_scope": "laboratory products (reagents, consumables, instruments, equipment)",
        },
        negative_boundary={
            "exclusions": [
                {
                    "domain": "Catalog number extraction",
                    "belongs_to": "CAP-CATALOG-EXTRACT",
                    "reason": (
                        "Extracting alphanumeric catalog/part numbers is a "
                        "pattern-matching task, NOT semantic classification."
                    ),
                },
                {
                    "domain": "Document section detection",
                    "belongs_to": "chapter_handler layer capabilities",
                    "reason": (
                        "Detecting storage/safety/procedure SECTIONS is structural, "
                        "NOT product classification."
                    ),
                },
                {
                    "domain": "Non-laboratory product classification",
                    "belongs_to": "NONE (out of scope)",
                    "reason": (
                        "General commercial product classification is outside the "
                        "declared domain_scope."
                    ),
                },
            ],
        },
        activation_rule={
            "type": "semantic_presence",
            "trigger": "laboratory product identity signals present in input",
            "no_doc_class": True,
            "note": "Activation is a semantic observation, NOT a Runtime decision.",
        },
        conflict_resolution={
            "conflicts": [
                {
                    "rival": "CAP-CATALOG-EXTRACT",
                    "resolution": (
                        "Orthogonal: UNSPSC MATCH classifies semantic category; "
                        "CATALOG EXTRACT extracts number patterns. No mutual "
                        "exclusion; both may apply to the same input without conflict."
                    ),
                }
            ],
            "note_d_priority": "No numeric default_priority is introduced (Design Decision D-PRIORITY).",
        },
        exclusion_rules={
            "hard_exclusions": ["non-laboratory product", "structural section detection"],
            "soft_exclusions": ["ambiguous product name with no laboratory context"],
        },
        validation_criteria={
            "primary_metrics": ["unspsc_match_accuracy"],
            "pass_condition": (
                "cross_document unspsc accuracy ≥ threshold (to be set at verification)"
            ),
            "review_questions": [
                "Does the derived UNSPSC code match the ground-truth taxonomy?",
                "Is the match semantically grounded (not pattern-based)?",
            ],
        },
        status=CapabilityStatus.PROPOSED,
        version=1,
        epoch=1,
        evolution_history=[{
            "timestamp": "2026-08-18T00:00:00Z",
            "change": "initial_registration",
            "detail": "Phase 10: CAP-UNSPSC-MATCH registered at PROPOSED (evidence empty)",
        }],
    )


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 1 IMPLEMENTATIONS & RULES
# ═══════════════════════════════════════════════════════════════════════════


def build_batch1_implementations() -> list[Implementation]:
    """Build implementations for all Batch 1 capabilities."""
    impls = []

    # CAP-TABLE-COLLAPSE-RECONSTRUCT
    impls.append(Implementation(
        id="IMPL-TABLE-COLLAPSE-GENERIC",
        capability_id="CAP-TABLE-COLLAPSE-RECONSTRUCT",
        name="Generic Collapse Reconstruction",
        strategy="structural_boundary_split",
        config={
            "min_entry_length": 10,
            "max_entry_length": 500,
            "content_signals": [
                {"name": "numeric_density", "threshold": 0.05, "weight": 0.30},
                {"name": "line_count", "threshold": 5, "weight": 0.20},
            ],
        },
    ))

    # CAP-ANCHOR-EXTRACT
    impls.append(Implementation(
        id="IMPL-ANCHOR-GENERIC",
        capability_id="CAP-ANCHOR-EXTRACT",
        name="Generic Anchor Extraction",
        strategy="anchor_scan",
        config={
            "anchor_patterns": [
                r"^([A-Z][a-zA-Z\s]{2,30}):\s*(.+)$",
                r"^([A-Z][a-zA-Z\s]{2,30})\s*=\s*(.+)$",
            ],
            "content_signals": [
                {"name": "line_count", "threshold": 3, "weight": 0.25},
            ],
        },
    ))

    # CAP-COLUMNAR-EXTRACT
    impls.append(Implementation(
        id="IMPL-COLUMNAR-GENERIC",
        capability_id="CAP-COLUMNAR-EXTRACT",
        name="Generic Columnar Extraction",
        strategy="column_boundary_scan",
        config={
            "min_column_gap": 2,
            "max_columns": 6,
            "content_signals": [
                {"name": "line_count", "threshold": 3, "weight": 0.25},
            ],
        },
    ))

    # CAP-NAME-QTY-PAIR
    impls.append(Implementation(
        id="IMPL-NAME-QTY-GENERIC",
        capability_id="CAP-NAME-QTY-PAIR",
        name="Generic Triple Extraction",
        strategy="triple_scan",
        config={
            "triple_proximity": 60,
            "content_signals": [
                {"name": "numeric_density", "threshold": 0.05, "weight": 0.30},
                {"name": "vocabulary_presence", "threshold": 3, "weight": 0.20},
            ],
        },
    ))

    return impls


def build_batch1_rules() -> list[Rule]:
    """Build rules for all Batch 1 capabilities."""
    return [
        Rule(id="RULE-TABLE-COLLAPSE-BOUNDARY", implementation_id="IMPL-TABLE-COLLAPSE-GENERIC",
             name="Structural Boundary Detection", rule_type="regex",
             pattern="|".join(QUANTITY_PATTERNS),
             description="Detect entry boundaries via quantity-unit patterns", priority=1),
        Rule(id="RULE-ANCHOR-LABEL", implementation_id="IMPL-ANCHOR-GENERIC",
             name="Label Anchor Extraction", rule_type="regex",
             pattern=r"^([A-Z][a-zA-Z\s]{2,30}):\s*(.+)$",
             description="Extract Label: Value pairs", priority=1),
        Rule(id="RULE-COLUMNAR-BOUNDARY", implementation_id="IMPL-COLUMNAR-GENERIC",
             name="Column Boundary Detection", rule_type="schema",
             pattern="",
             description="Identify column boundaries from position gaps", priority=1),
        Rule(id="RULE-NAME-QTY-TRIPLE", implementation_id="IMPL-NAME-QTY-GENERIC",
             name="Name-Quantity-Unit Triple", rule_type="regex",
             pattern="|".join(QUANTITY_PATTERNS),
             description="Extract (name, qty, unit) triples", priority=1),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BOOTSTRAP — register all capabilities (Phase 5.1a: 5 total)
# ═══════════════════════════════════════════════════════════════════════════

# Map capability_id → builder function for batch registration
_CAPABILITY_BUILDERS: dict[str, Any] = {}  # populated below


def bootstrap_registry(registry: CapabilityRegistry) -> CapabilityRegistry:
    """
    Register all capabilities into the given Registry.

    Phase 5.2: 21 capabilities total (1 base + 4 B1 + 5 B2 + 6 B3 + 5 B Discrimination).
    This is the single source of truth for capability registration.
    """
    builders = [
        # Base
        ("CAP-COMP-TABLE", build_cap_comp_table_v2),
        # Batch 1: structural primitives
        ("CAP-TABLE-COLLAPSE-RECONSTRUCT", build_cap_table_collapse_reconstruct),
        ("CAP-ANCHOR-EXTRACT", build_cap_anchor_extract),
        ("CAP-COLUMNAR-EXTRACT", build_cap_columnar_extract),
        ("CAP-NAME-QTY-PAIR", build_cap_name_qty_pair),
        # Batch 2: content type detectors
        ("CAP-STORAGE-DETECT", build_cap_storage_detect),
        ("CAP-SAFETY-DETECT", build_cap_safety_detect),
        ("CAP-TROUBLESHOOT-DETECT", build_cap_troubleshoot_detect),
        ("CAP-PROCEDURE-DETECT", build_cap_procedure_detect),
        ("CAP-PREP-MATERIALS-DETECT", build_cap_prep_materials_detect),
        # Batch 3: validation & composition
        ("CAP-TEMP-RANGE", build_cap_temp_range),
        ("CAP-TIME-EXTRACT", build_cap_time_extract),
        ("CAP-CATALOG-EXTRACT", build_cap_catalog_extract),
        ("CAP-QUANTITY-VALIDATE", build_cap_quantity_validate),
        ("CAP-UNIT-CONSISTENCY", build_cap_unit_consistency),
        ("CAP-TABLE-TYPE-CLASSIFY", build_cap_table_type_classify),
        # Phase 5.2: discrimination test (intentionally similar)
        ("CAP-TABLE-EXTRACT-BASIC", build_cap_table_extract_basic),
        ("CAP-PARAMETER-LIST", build_cap_parameter_list),
        ("CAP-STORAGE-LONG-TERM", build_cap_storage_long_term),
        ("CAP-WARNING-EXTRACT", build_cap_warning_extract),
        ("CAP-STEP-COUNTER", build_cap_step_counter),
        # Phase 10: UNSPSC classification (PROPOSED, no patterns/implementations)
        ("CAP-UNSPSC-MATCH", build_cap_unspsc_match),
    ]

    for cap_id, builder in builders:
        cap = builder()
        result = registry.register(cap)
        if not result.success:
            raise RuntimeError(f"Failed to register {cap_id}: {result.message}")

    return registry


_ALL_CAP_IDS = [
    "CAP-COMP-TABLE",
    "CAP-TABLE-COLLAPSE-RECONSTRUCT", "CAP-ANCHOR-EXTRACT",
    "CAP-COLUMNAR-EXTRACT", "CAP-NAME-QTY-PAIR",
    "CAP-STORAGE-DETECT", "CAP-SAFETY-DETECT",
    "CAP-TROUBLESHOOT-DETECT", "CAP-PROCEDURE-DETECT",
    "CAP-PREP-MATERIALS-DETECT",
    "CAP-TEMP-RANGE", "CAP-TIME-EXTRACT",
    "CAP-CATALOG-EXTRACT", "CAP-QUANTITY-VALIDATE",
    "CAP-UNIT-CONSISTENCY", "CAP-TABLE-TYPE-CLASSIFY",
    "CAP-TABLE-EXTRACT-BASIC", "CAP-PARAMETER-LIST",
    "CAP-STORAGE-LONG-TERM", "CAP-WARNING-EXTRACT",
    "CAP-STEP-COUNTER",
    "CAP-UNSPSC-MATCH",
]


def bootstrap_patterns_to_graph(registry: CapabilityRegistry, graph: Any) -> Any:
    """
    Sync Patterns and Implementations from Registry to ExperienceGraph.
    """
    from dice.graph.experience_graph import ExperienceGraph

    # Add all Patterns (v6 = v5 + Phase 5.2 discrimination)
    for pat in build_patterns_v6():
        if pat.id not in graph.patterns:
            graph.add_pattern(pat)

    # Add all Capabilities from Registry
    for cap_id in _ALL_CAP_IDS:
        cap = registry.get(cap_id)
        if cap and cap.id not in graph.capabilities:
            graph.add_capability(cap)

    # Add all Implementations (v2 + B1 + B2 + B3 + B Discrimination)
    all_impls = (build_implementations_v2() + build_batch1_implementations()
                 + build_batch2_implementations() + build_batch3_implementations()
                 + build_phase5_2_implementations())
    for impl in all_impls:
        if impl.id not in graph.implementations:
            graph.add_implementation(impl)

    # Add all Rules (v2 + B1 + B2 + B3 + B Discrimination)
    all_rules = (build_rules_v2() + build_batch1_rules()
                 + build_batch2_rules() + build_batch3_rules()
                 + build_phase5_2_rules())
    for rule in all_rules:
        if rule.id not in graph.rules:
            graph.add_rule(rule)

    # Add Edges: Implementation → Capability
    for impl in all_impls:
        edge = Edge(
            id=f"EDGE-{impl.id}-IMPLEMENTS-{impl.capability_id}",
            source_id=impl.id,
            target_id=impl.capability_id,
            edge_type=EdgeType.IMPLEMENTS,
            source_type="Implementation",
            target_type="Capability",
        )
        graph.add_edge(edge)

    # Add Edges: Implementation → Rule
    for rule in all_rules:
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

    # Add Edges: Pattern → Capability
    cap_patterns: dict[str, list[str]] = {}
    for cap_id in _ALL_CAP_IDS:
        cap = registry.get(cap_id)
        if cap:
            cap_patterns[cap_id] = cap.pattern_ids

    for pat in build_patterns_v4():
        if pat.id not in graph.patterns:
            continue
        for cap_id, pat_ids in cap_patterns.items():
            if pat.id in pat_ids:
                edge = Edge(
                    id=f"EDGE-{pat.id}-PATTERN_SUPPORTS-{cap_id}",
                    source_id=pat.id,
                    target_id=cap_id,
                    edge_type=EdgeType.PATTERN_SUPPORTS,
                    source_type="Pattern",
                    target_type="Capability",
                    weight=pat.confidence,
                )
                graph.add_edge(edge)

    return graph
