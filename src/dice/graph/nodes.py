"""
Experience Graph data model — core entity types (nodes).

Six core entities forming the Capability Evolution chain:
    Observation → Evidence → Pattern → CapabilityCandidate → Capability
                                                                  ↓
                                                            Implementation
                                                                  ↓
                                                                  Rule

Design principle: Patterns are DESCRIPTIVE (detection_signals describe
phenomena), not procedural (they don't contain if-else logic). Confidence
is computed from evidence_count, not hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from dice.models import PatternStatus, CapabilityStatus, ConfidenceLevel, SourceRef


# ──────────────────────────────── Helpers ────────────────────────────────


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────── Observation ────────────────────────────────


@dataclass
class Observation:
    """
    Raw observation — a fact noticed during document processing.

    Observations are NEUTRAL: they record "what happened" without
    judging "what it means". This is the entry point into the
    evidence → pattern → capability chain.
    """
    id: str                                    # unique ID, e.g. "OBS-001"
    timestamp: str = field(default_factory=_now)
    # WHAT was observed
    phenomenon: str = ""
    # WHERE it was observed
    source: Optional[SourceRef] = None
    # Context: what pipeline/handler produced this
    pipeline: str = ""                         # e.g. "long_v25", "components_handler"
    handler_name: str = ""
    # Raw data captured
    raw_data: dict[str, Any] = field(default_factory=dict)
    # Optional severity hint (not a judgment, just a signal)
    severity_hint: str = ""                    # "info", "warning", "critical"

    def __post_init__(self):
        if not self.id:
            raise ValueError("Observation.id is required")


# ──────────────────────────────── DocumentObservation (Phase 4.1) ────────────────────────────────


@dataclass
class DocumentObservation:
    """
    What the system observes about a document chunk BEFORE any capability
    is selected. This is the INPUT to the CapabilityMatcher.

    CRITICAL: Contains ZERO doc_class, product_id, or filename fields.
    All signals are pure structural/semantic content characteristics.

    This is NOT the same as Observation (which records pipeline events).
    DocumentObservation is the matching-layer input: "what does this
    content look like structurally?"
    """
    id: str = ""                                    # unique observation id
    # ── Source (for traceability only, NOT for routing) ──
    document_id: str = ""
    slice_id: str = ""
    content_snippet: str = ""                       # first 500 chars for inspection

    # ── Structure signals (L1 style) ──
    # These describe structural characteristics — NOT domain vocabulary.
    line_count: int = 0
    avg_line_length: float = 0.0
    has_table_structure: bool = False               # columnar/tabular layout detected
    has_collapsed_table: bool = False               # word-smashed table artifacts
    has_list_structure: bool = False                # bulleted or enumerated list
    has_key_value_pairs: bool = False               # "Label: Value" patterns
    has_markdown_table: bool = False                # Markdown |---|---| table format (Phase 5.5)
    has_numbered_list: bool = False                 # consecutive numbered list (Phase 5.5)
    has_numeric_density_high: bool = False          # many numbers relative to text
    header_section_count: int = 0                   # # of header-like lines

    # ── Semantic signals ──
    # Presence/absence counts of structural element types (NOT specific terms).
    detected_element_types: dict[str, int] = field(default_factory=dict)
    # e.g. {"name": 12, "quantity": 8, "unit": 6, "catalog_number": 3}

    # ── Pattern signals (from L1/L3 detectors) ──
    detected_pattern_ids: list[str] = field(default_factory=list)
    # Pattern IDs that L1/L3 structural detectors have flagged.
    pattern_match_scores: dict[str, float] = field(default_factory=dict)
    # Per-pattern confidence from structural detection.

    # ── Content quality ──
    content_length: int = 0
    unique_token_ratio: float = 0.0                 # vocabulary diversity signal
    noise_ratio: float = 0.0                        # estimated noise proportion

    # ── Metadata ──
    timestamp: str = field(default_factory=_now)

    def to_summary(self) -> dict[str, Any]:
        """Compact summary for ranking model input."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "line_count": self.line_count,
            "has_table_structure": self.has_table_structure,
            "has_collapsed_table": self.has_collapsed_table,
            "has_markdown_table": self.has_markdown_table,
            "has_numbered_list": self.has_numbered_list,
            "detected_element_types": dict(self.detected_element_types),
            "detected_pattern_ids": self.detected_pattern_ids,
            "pattern_match_scores": dict(self.pattern_match_scores),
            "content_length": self.content_length,
        }


@dataclass
class MatchCandidate:
    """
    A ranked capability candidate produced by the Matcher.

    This is OUTPUT of CapabilityMatcher.match() — NOT the same as
    CapabilityCandidate (which is for proposed-but-unverified capabilities).

    MatchCandidate represents a registered Capability that the Ranking Model
    believes is applicable to the given DocumentObservation.
    """
    capability_id: str = ""
    capability_name: str = ""

    # ── Ranking scores (all 0.0–1.0) ──
    score: float = 0.0                              # composite score
    pattern_match_score: float = 0.0                # structural pattern similarity
    evidence_quality_score: float = 0.0             # how strong is the evidence match
    historical_success_score: float = 0.0           # past execution success rate
    cross_domain_score: float = 0.0                 # cross-domain transfer confidence
    failure_penalty: float = 0.0                    # penalty from past failures

    # ── Evidence ──
    matched_patterns: list[str] = field(default_factory=list)
    matched_element_types: list[str] = field(default_factory=list)
    evidence_summary: str = ""                      # human-readable

    # ── Metadata ──
    capability_version: int = 0
    capability_status: str = ""
    timestamp: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "score": round(self.score, 4),
            "breakdown": {
                "pattern_match": round(self.pattern_match_score, 4),
                "evidence_quality": round(self.evidence_quality_score, 4),
                "historical_success": round(self.historical_success_score, 4),
                "cross_domain": round(self.cross_domain_score, 4),
                "failure_penalty": round(self.failure_penalty, 4),
            },
            "matched_patterns": self.matched_patterns,
            "matched_element_types": self.matched_element_types,
            "evidence_summary": self.evidence_summary,
            "capability_version": self.capability_version,
            "capability_status": self.capability_status,
        }


# ──────────────────────────────── Evidence ────────────────────────────────


@dataclass
class Evidence:
    """
    Confirmed observation that supports (or contradicts) a Pattern.

    Evidence is the bridge between raw Observation and structured Pattern.
    Multiple Evidence items pointing to the same Pattern raise its confidence.
    """
    id: str                                    # e.g. "EVD-001"
    observation_ids: list[str] = field(default_factory=list)  # links to Observations
    pattern_id: str = ""                       # which Pattern this supports
    timestamp: str = field(default_factory=_now)
    # WHAT phenomenon does this evidence describe
    phenomenon: str = ""
    # WHERE: specific document/slice
    source_document: str = ""
    source_slice: str = ""
    # HOW confident is this evidence itself
    evidence_strength: float = 0.0             # 0.0–1.0
    # Extraction results (if any)
    extraction: dict[str, Any] = field(default_factory=dict)
    # Whether this evidence is confirming or disconfirming
    is_confirmed: bool = True

    def __post_init__(self):
        if not self.id:
            raise ValueError("Evidence.id is required")

    def confirm(self, strength: float = 1.0) -> "Evidence":
        self.is_confirmed = True
        self.evidence_strength = min(1.0, strength)
        return self


# ──────────────────────────────── Pattern ────────────────────────────────


@dataclass
class Pattern:
    """
    A recurring structural or semantic pattern observed across documents.

    KEY DESIGN: detection_signals are DESCRIPTIVE, not procedural.
    They describe what the pattern LOOKS LIKE, not what to DO.

    Example:
        detection_signals = [
            "table structure with component names in first column",
            "quantity/catalog numbers in adjacent columns",
            "rows separated by alternating product entries"
        ]

    NOT:
        detection_signals = [
            "if doc_class == 'plasmid_extraction' then ..."
        ]
    """
    id: str                                    # e.g. "PAT-001"
    name: str = ""
    description: str = ""
    # DESCRIPTIVE signals — describe the phenomenon, don't encode logic
    detection_signals: list[str] = field(default_factory=list)
    structural_indicators: list[str] = field(default_factory=list)
    content_indicators: list[str] = field(default_factory=list)
    # Status machine: candidate → verified → deprecated
    status: PatternStatus = PatternStatus.CANDIDATE
    # Confidence is DERIVED from evidence_count, not hardcoded
    confidence: float = 0.0
    evidence_count: int = 0
    evidence_ids: list[str] = field(default_factory=list)
    # Source documents where this pattern was observed
    source_documents: list[str] = field(default_factory=list)
    # When was this pattern first/last observed
    first_observed: str = ""
    last_observed: str = field(default_factory=_now)
    # Cross-document metrics
    cross_doc_count: int = 0                  # # of distinct documents
    # Tags for categorization
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            raise ValueError("Pattern.id is required")

    def add_evidence(self, evidence_id: str) -> None:
        """Add evidence and auto-update confidence."""
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)
            self.evidence_count = len(self.evidence_ids)
            self.confidence = self._compute_confidence()

    def verify(self) -> None:
        """Promote to verified status if threshold met."""
        if self.evidence_count >= 3:
            self.status = PatternStatus.VERIFIED

    def _compute_confidence(self) -> float:
        """Confidence = min(1.0, evidence_count / 5.0)."""
        return min(1.0, self.evidence_count / 5.0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "detection_signals": self.detection_signals,
            "source_documents": self.source_documents,
        }


# ──────────────────────────────── CapabilityCandidate ────────────────────────────────


@dataclass
class CapabilityCandidate:
    """
    A proposed Capability that has NOT yet been verified.

    Created by the Learning Engine when enough Evidence + Pattern
    convergence is detected. Goes through validation gate before
    becoming a registered Capability.
    """
    id: str                                    # e.g. "CAP-CAND-001"
    name: str = ""
    description: str = ""
    pattern_ids: list[str] = field(default_factory=list)
    # Proposed scope — NOT doc_class list
    scope_description: str = ""                # problem space description
    # Verification results
    verification_score: float = 0.0
    verification_results: list[dict[str, Any]] = field(default_factory=list)
    # Gate status
    gates_passed: int = 0
    total_gates: int = 3                       # structure, content, cross-doc
    is_verified: bool = False
    timestamp: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.id:
            raise ValueError("CapabilityCandidate.id is required")


# ──────────────────────────────── Capability ────────────────────────────────


@dataclass
class Capability:
    """
    A verified, registered document understanding capability.

    A Capability encapsulates:
    1. What it does (description)
    2. When it applies (scope + patterns, NOT doc_class list)
    3. How to execute (implementation)
    4. Where it came from (evidence trace)

    Maturity is AUTO-COMPUTED from evidence diversity and cross-document
    performance, not manually assigned.
    """
    id: str                                    # e.g. "CAP-COMP-TABLE"
    name: str = ""
    layer: str = "chapter_handler"             # DICE layer
    description: str = ""

    # ── Identity (Registry 四类存储之一) ──
    # SCOPE: describes problem space, NOT document types
    scope: dict[str, Any] = field(default_factory=dict)

    # ── Strategy (Registry 四类存储之二) ──
    # Patterns that detect this capability's applicability
    pattern_ids: list[str] = field(default_factory=list)
    # Implementations that execute this capability
    implementation_ids: list[str] = field(default_factory=list)
    # Structured I/O schemas (Phase 4.0: promoted from scope dict)
    input_schema: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"fields": ["content", "structure_features"], "constraints": {...}}
    output_schema: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"fields": ["components", "total_count", "coverage_ratio"], "types": {...}}
    # Declarative strategy description (what it does, not how)
    execution_strategy: str = ""
    # What evidence is required to apply this capability
    evidence_requirements: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"min_pattern_matches": 2, "min_content_length": 50}

    # ── Definition (Phase 0.6 Schema Extension) ──
    # Semantic boundaries, activation rules, conflict resolution & validation criteria.
    # All default to {} — only filled when a Capability has explicit semantic definition.
    # definition_version can be inferred: all 6 {} = v1.0, any non-empty = v2.0.
    positive_boundary: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"definition": "...", "core_structure": "...", "types": [...]}
    negative_boundary: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"exclusions": [{"domain": "Safety", "belongs_to": "CAP-SAFETY-DETECT", ...}, ...]}
    activation_rule: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"type": "pair_requirement", "problem_signals": {...}, "resolution_signals": {...}}
    conflict_resolution: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"default_priority": 2, "conflicts": [{"rival": "...", "resolution": "..."}, ...]}
    exclusion_rules: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"hard_exclusions": [...], "soft_exclusions": [...]}
    validation_criteria: dict[str, Any] = field(default_factory=dict)
    #   e.g. {"primary_metrics": [...], "pass_condition": "...", "review_questions": [...]}

    # ── Evidence (Registry 四类存储之三) ──
    # Status
    status: CapabilityStatus = CapabilityStatus.PROPOSED
    # Auto-computed maturity
    maturity: ConfidenceLevel = ConfidenceLevel.LOW
    maturity_score: float = 0.0                # 0.0–1.0
    # Source trace
    source_evidence_ids: list[str] = field(default_factory=list)
    source_pattern_ids: list[str] = field(default_factory=list)
    # Cross-document performance
    documents_tested: list[str] = field(default_factory=list)
    cross_doc_success_rate: float = 0.0
    # Execution statistics (updated by Feedback Loop)
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_execution_at: str = ""

    # ── Evolution History (Registry 四类存储之四) ──
    # Version tracking
    version: int = 1
    epoch: int = 1
    # Supersede chain
    previous_version_id: str = ""              # supersede chain
    evolution_ids: list[str] = field(default_factory=list)
    # Structured history records (Phase 4.0: promoted from ad-hoc tracking)
    validation_history: list[dict[str, Any]] = field(default_factory=list)
    #   e.g. [{"timestamp": "...", "validator": "regression_guard", "result": "passed"}]
    evolution_history: list[dict[str, Any]] = field(default_factory=list)
    #   e.g. [{"timestamp": "...", "change": "new_pattern_added", "detail": "..."}]
    # Pending enhancement signals (from Feedback Loop, NOT auto-applied)
    enhancement_signals: list[str] = field(default_factory=list)

    # ── Lifecycle ──
    created_at: str = field(default_factory=_now)
    verified_at: str = ""
    deprecated_at: str = ""
    deprecation_reason: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("Capability.id is required")
        self._auto_compute_maturity()

    def _auto_compute_maturity(self) -> None:
        """
        Maturity is computed from:
        - Evidence diversity (# of distinct source documents)
        - Cross-document performance (success rate across doc classes)
        """
        doc_count = len(set(self.documents_tested))
        success = self.cross_doc_success_rate
        self.maturity_score = min(1.0, (doc_count * 0.15 + success * 0.55))
        if self.maturity_score >= 0.8:
            self.maturity = ConfidenceLevel.HIGH
        elif self.maturity_score >= 0.5:
            self.maturity = ConfidenceLevel.MEDIUM
        else:
            self.maturity = ConfidenceLevel.LOW

    def to_dict(self) -> dict[str, Any]:
        return {
            # Identity
            "id": self.id,
            "name": self.name,
            "layer": self.layer,
            "description": self.description[:200],
            # Strategy
            "pattern_ids": self.pattern_ids,
            "implementation_ids": self.implementation_ids,
            "input_schema_keys": list(self.input_schema.keys()),
            "output_schema_keys": list(self.output_schema.keys()),
            "execution_strategy": self.execution_strategy[:200],
            # Definition (Phase 0.6)
            "positive_boundary": self.positive_boundary,
            "negative_boundary": self.negative_boundary,
            "activation_rule": self.activation_rule,
            "conflict_resolution": self.conflict_resolution,
            "exclusion_rules": self.exclusion_rules,
            "validation_criteria": self.validation_criteria,
            # Evidence
            "status": self.status.value,
            "maturity": self.maturity.value,
            "maturity_score": self.maturity_score,
            "source_evidence_count": len(self.source_evidence_ids),
            "documents_tested": len(self.documents_tested),
            "cross_doc_success_rate": self.cross_doc_success_rate,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            # Evolution
            "version": self.version,
            "epoch": self.epoch,
            "validation_history_count": len(self.validation_history),
            "evolution_history_count": len(self.evolution_history),
            "enhancement_signals": self.enhancement_signals,
        }

    def record_execution(self, success: bool, document_id: str) -> None:
        """Update execution statistics (called by Feedback Loop)."""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        if document_id and document_id not in self.documents_tested:
            self.documents_tested.append(document_id)
        self.last_execution_at = _now()
        self.cross_doc_success_rate = (
            self.success_count / self.execution_count
            if self.execution_count > 0 else 0.0
        )
        self._auto_compute_maturity()

    def deprecate(self, reason: str = "") -> None:
        """Mark this capability as deprecated (reversible via reactivate)."""
        self.status = CapabilityStatus.DEPRECATED
        self.deprecated_at = _now()
        self.deprecation_reason = reason

    def is_active(self) -> bool:
        """Check if capability is available for execution."""
        return self.status not in (CapabilityStatus.DEPRECATED, CapabilityStatus.FAILED)


# ──────────────────────────────── Implementation ────────────────────────────────


@dataclass
class Implementation:
    """
    A concrete execution strategy for a Capability.

    One Capability can have multiple Implementations (e.g. different
    structural variants). The Implementation contains the actual
    execution logic AND its constituent Rules.
    """
    id: str                                    # e.g. "IMPL-COMP-TABLE-ANCHOR"
    capability_id: str = ""                    # which Capability this implements
    name: str = ""
    strategy: str = ""                         # execution strategy description
    version: int = 1
    # Configuration — strategy-specific parameters
    config: dict[str, Any] = field(default_factory=dict)
    # Constituent Rules (Capability → Implementation → Rule nesting)
    rule_ids: list[str] = field(default_factory=list)
    # Performance metrics
    success_count: int = 0
    failure_count: int = 0
    avg_confidence: float = 0.0
    # Timestamps
    created_at: str = field(default_factory=_now)
    last_used: str = ""


# ──────────────────────────────── Rule ────────────────────────────────


@dataclass
class Rule:
    """
    The lowest-level extraction/validation rule.

    Rules are the LEAVES of the Capability tree. They are always
    owned by an Implementation, which is owned by a Capability.
    Rules should NEVER be invoked directly without going through
    their parent Capability.
    """
    id: str                                    # e.g. "RULE-COMP-NAME-EXTRACT"
    implementation_id: str = ""                # parent Implementation
    name: str = ""
    rule_type: str = ""                        # "regex", "anchor", "keyword", "schema"
    pattern: str = ""                          # the actual rule pattern
    description: str = ""
    priority: int = 0
    is_active: bool = True
    # Statistics
    hit_count: int = 0
    miss_count: int = 0


# ──────────────────────────────── Evolution ────────────────────────────────


@dataclass
class Evolution:
    """
    A record of Capability evolution — how a capability changed over time.

    Each Evolution is an Episode (Graphiti concept) in the capability's
    lifecycle. Together they form the capability's lineage.
    """
    id: str                                    # e.g. "EVO-001"
    capability_id: str = ""
    from_version: int = 0
    to_version: int = 0
    change_type: str = ""                      # "new_pattern", "new_implementation", "scope_expanded"
    description: str = ""
    trigger_observation_ids: list[str] = field(default_factory=list)
    trigger_pattern_ids: list[str] = field(default_factory=list)
    outcome: str = ""                          # "success", "partial", "regression"
    timestamp: str = field(default_factory=_now)


# ──────────────────────────────── Fix ────────────────────────────────


@dataclass
class Fix:
    """
    A parameter-tuning fix — AUXILIARY, not a primary entity.

    Fixes are the LEAST valuable type of learning. They record
    parameter adjustments (e.g. "min_rows 2→1") but don't produce
    reusable capabilities. The system should prefer Pattern →
    Capability evolution over accumulating Fixes.
    """
    id: str                                    # e.g. "FIX-001"
    target: str = ""                           # what was fixed (parameter path)
    old_value: str = ""
    new_value: str = ""
    reason: str = ""
    trigger_observation_id: str = ""
    timestamp: str = field(default_factory=_now)
