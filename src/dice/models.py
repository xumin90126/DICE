"""
Core data models for the DICE system.

These models define the foundational data structures that the graph and
runtime layers build upon. They are pure dataclass/serializable objects
with no runtime execution logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from datetime import datetime, timezone


# ──────────────────────────────── Enums ────────────────────────────────


class SkillLayer(str, Enum):
    """Four-layer DICE skill hierarchy."""
    DOCUMENT_CLASS = "document_class"       # Whole-document structure
    CHAPTER_HANDLER = "chapter_handler"     # Chapter-level processing
    EXTRACTION_RULE = "extraction_rule"     # Single-field extraction
    PARAMETER_CONSTRAINT = "parameter_constraint"  # Cross-document param knowledge


class PatternStatus(str, Enum):
    CANDIDATE = "candidate"    # < 3 evidence
    VERIFIED = "verified"      # 3+ evidence, confidence >= threshold
    DEPRECATED = "deprecated"  # superseded or invalidated


class CapabilityStatus(str, Enum):
    PROPOSED = "proposed"      # from CapabilityCandidate, not yet verified
    BETA = "beta"              # verified on source docs, not yet cross-tested
    ACTIVE = "active"          # validated across multiple document classes
    DEPRECATED = "deprecated"  # superseded
    FAILED = "failed"          # verification failed


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ──────────────────────────────── Source Reference ────────────────────────────────


@dataclass
class SourceRef:
    """Traceable reference to the origin document/slice/lines of a finding."""
    source_document: str          # e.g. "DC201-C1"
    source_slice: str             # e.g. "04_components"
    source_lines: str = ""        # e.g. "L12-L45"
    product_name: str = ""
    catalog_number: str = ""

    def __hash__(self) -> int:
        return hash((self.source_document, self.source_slice, self.source_lines))


# ──────────────────────────────── Trigger / Pattern ────────────────────────────────


@dataclass
class TriggerPattern:
    """
    Describes what activates a Skill — declarative, not procedural.

    Key design constraint: detection_signals MUST NOT reference doc_class
    or document type. They describe structural/semantic phenomena.
    """
    name: str
    description: str = ""
    # Detection signals: descriptive patterns that indicate "this content
    # falls in my problem space". These are checked by Pattern Matching,
    # not by doc_class lookup.
    detection_signals: list[str] = field(default_factory=list)
    # Structural indicators (e.g. "table with >2 columns", "key-value pairs")
    structural_indicators: list[str] = field(default_factory=list)
    # Content indicators (e.g. "component names", "temperature ranges")
    content_indicators: list[str] = field(default_factory=list)
    confidence: float = 0.0


# ──────────────────────────────── Capability Scope ────────────────────────────────


@dataclass
class CapabilityScope:
    """
    Describes the PROBLEM SPACE a capability operates in.

    CRITICAL: Must NOT contain doc_class lists. The scope describes
    semantic and structural characteristics, not document taxonomy.
    """
    capability_id: str = ""
    description: str = ""
    # Problem space description (human-readable)
    problem_space: str = ""
    # Input semantics: what kind of content this capability consumes
    input_semantics: str = ""
    # Output semantics: what this capability produces
    output_semantics: str = ""
    # Patterns this capability uses for detection
    pattern_ids: list[str] = field(default_factory=list)
    # Evidence types this capability generates
    evidence_types: list[str] = field(default_factory=list)
    # Domain vocabulary — NOT indexed by doc_class
    # Organized by semantic category (e.g. "biochemical_reagents", "consumables")
    vocabulary: dict[str, list[str]] = field(default_factory=dict)


# ──────────────────────────────── Document Skill ────────────────────────────────


@dataclass
class DocumentSkill:
    """
    A transferable document understanding capability.

    Encapsulates:
    1. Recognition pattern (trigger) — what activates this skill
    2. Extraction logic — what information to extract
    3. Validation rules — constraints on extracted data
    4. Source trace — which documents this was learned from
    """
    id: str = ""
    name: str = ""
    layer: SkillLayer = SkillLayer.EXTRACTION_RULE
    trigger: TriggerPattern = field(default_factory=TriggerPattern)
    extraction_rules: list[dict[str, Any]] = field(default_factory=list)
    validation_rules: list[dict[str, Any]] = field(default_factory=list)
    source_documents: list[SourceRef] = field(default_factory=list)
    maturity: ConfidenceLevel = ConfidenceLevel.LOW
    version: int = 1
    status: CapabilityStatus = CapabilityStatus.PROPOSED

    def evidence_count(self) -> int:
        return len(self.source_documents)


# ──────────────────────────────── Skill Candidate ────────────────────────────────


@dataclass
class SkillCandidate:
    """A proposed skill not yet verified."""
    skill: DocumentSkill
    cluster_size: int = 0
    cluster_cohesion: float = 0.0          # avg pairwise similarity
    cross_doc_support: int = 0             # # of docs supporting this pattern
    proposed_by: str = ""                  # which process proposed this


# ──────────────────────────────── Validation ────────────────────────────────


@dataclass
class ValidationResult:
    """Result of a validation gate check."""
    gate_name: str                         # "structure_gate", "content_gate", "cross_doc_gate"
    passed: bool
    score: float = 0.0
    details: str = ""
    failed_rules: list[str] = field(default_factory=list)


# ──────────────────────────────── Capability Result ────────────────────────────────


@dataclass
class EvidenceRecord:
    """A single piece of evidence collected during capability execution."""
    evidence_id: str = ""
    phenomenon: str = ""                   # what was observed
    source: Optional[SourceRef] = None     # where it was found
    confidence: float = 0.0
    extraction: Optional[dict[str, Any]] = None  # what was extracted


@dataclass
class CapabilityResult:
    """
    Unified output format for all capability executions.

    MUST contain not just the final output, but also:
    - WHY this judgment was made (evidence)
    - WHAT patterns were used (pattern_used)
    - HOW confident the result is (confidence)
    """
    capability_name: str = ""
    capability_id: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    evidence: list[EvidenceRecord] = field(default_factory=list)
    pattern_used: list[str] = field(default_factory=list)
    implementation_version: str = ""
    diagnosis: str = ""                    # human-readable explanation
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "capability_id": self.capability_id,
            "result": self.result,
            "confidence": self.confidence,
            "evidence_count": len(self.evidence),
            "evidence": [
                {
                    "id": e.evidence_id,
                    "phenomenon": e.phenomenon,
                    "source": (
                        f"{e.source.source_document}/{e.source.source_slice}"
                        if e.source else "unknown"
                    ),
                    "confidence": e.confidence,
                }
                for e in self.evidence
            ],
            "pattern_used": self.pattern_used,
            "implementation_version": self.implementation_version,
            "diagnosis": self.diagnosis,
            "timestamp": self.timestamp,
        }


# ──────────────────────────────── Capability Graph (simplified) ────────────────────────────────


@dataclass
class GraphNode:
    id: str
    type: str  # Node type discriminator
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: str  # Edge type discriminator
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityGraph:
    """The capability graph — DocumentClass → Chapter → Skill → Parameter."""
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: list[GraphEdge] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_outgoing(self, node_id: str, edge_type: Optional[str] = None) -> list[GraphEdge]:
        results = [e for e in self.edges if e.source_id == node_id]
        if edge_type:
            results = [e for e in results if e.edge_type == edge_type]
        return results

    def get_incoming(self, node_id: str, edge_type: Optional[str] = None) -> list[GraphEdge]:
        results = [e for e in self.edges if e.target_id == node_id]
        if edge_type:
            results = [e for e in results if e.edge_type == edge_type]
        return results
