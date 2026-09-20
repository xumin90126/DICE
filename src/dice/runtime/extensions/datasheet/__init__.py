"""
Phase 16.1: Datasheet Extension package (Skeleton).

CAND-002 (datasheet EXTEND) Implementation Adapter layer package.

This __init__.py is a PACKAGE-EXPORT-ONLY module. Its sole responsibility is
to re-export the four adapter components and their data types so downstream
(Human-driven) callers can import them cleanly.

EXPLICIT NON-GOALS (Phase 16.1 §3):
    - NO automatic capability registration
    - NO import of bootstrap
    - NO registry modification
    - NO loader modification
    - NO side effects on import

Importing this package performs ZERO mutation, ZERO registration, ZERO
authority acquisition. It only binds names for the four skeleton components.

Component chain (single-direction data flow, Phase 14.5 §6.2):
    DocumentSpan (input) → NormalizationAdapter → NormalizedDocumentSpan
        → SchemaAdapter → SchemaMappingCandidate
        → ExtractionAdapter → ExtractedFact
        → EvidenceAdapter → MappingEvidence (output)
"""

from .normalization_adapter import (
    SpanType,
    DocumentSpan,
    NormalizedDocumentSpan,
    NormalizationAdapter,
)
from .schema_adapter import (
    SchemaMappingCandidate,
    SchemaAdapter,
)
from .extraction_adapter import (
    ExtractedFact,
    ExtractionAdapter,
)
from .evidence_adapter import (
    MappingEvidence,
    EvidenceAdapter,
)
from .pipeline import (
    DatasheetPipeline,
)
from .validation_memory import (
    ValidationRecord,
    ValidationMemory,
    VALIDATION_REASONS,
    DECISION_ACCEPT,
    DECISION_REJECT,
)
from .capability_candidate_observation import (
    CapabilityCandidateObservation,
    DRAFT_STATUS,
)
from .candidate_aggregator import (
    CandidateAggregator,
)

__all__ = [
    # Component 1 — normalization
    "SpanType",
    "DocumentSpan",
    "NormalizedDocumentSpan",
    "NormalizationAdapter",
    # Component 2 — schema adaptation
    "SchemaMappingCandidate",
    "SchemaAdapter",
    # Component 3 — extraction
    "ExtractedFact",
    "ExtractionAdapter",
    # Component 4 — evidence assembly
    "MappingEvidence",
    "EvidenceAdapter",
    # Orchestration layer
    "DatasheetPipeline",
    # Validation Memory Foundation (Phase 16.11)
    "ValidationRecord",
    "ValidationMemory",
    "VALIDATION_REASONS",
    "DECISION_ACCEPT",
    "DECISION_REJECT",
    "CapabilityCandidateObservation",
    "DRAFT_STATUS",
    # Candidate Discovery Aggregation (Phase 44)
    "CandidateAggregator",
]
