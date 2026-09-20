"""
Phase 16.2: Datasheet Extension — Evidence Pipeline (Orchestration Layer).

CAND-002 (datasheet EXTEND) Implementation Adapter layer, orchestration.

This module wires the four skeleton components (Normalization → Schema →
Extraction → Evidence) into a single Human-driven pipeline that turns an
interface-contract `DocumentSpan` into a `MappingEvidence` observation
artifact. It is PURE ORCHESTRATION: it holds no authority, performs no
selection/routing/decision, and delegates every step to a component that
itself carries zero authority.

Chain (single-direction data flow, Phase 14.5 §6.2):
    DocumentSpan (input)
      → NormalizationAdapter.normalize  → NormalizedDocumentSpan
      → SchemaAdapter.map_schema        → SchemaMappingCandidate
      → ExtractionAdapter.extract       → ExtractedFact
      → EvidenceAdapter.produce         → MappingEvidence (output)

Responsibilities:
    IN  : adapter orchestration (wiring, sequencing, zero decision)
    OUT : capability selection / document_type routing / ranking / decision /
          execution planning / any authority

EXPLICIT NON-GOALS (Phase 16.2):
    - NO PDF parser, NO NLP, NO regex extractor, NO ML model
    - NO matcher, NO selector, NO router, NO ranking, NO scorer, NO executor
    - NO capability decision, NO selected capability, NO execution plan
    - `doc_type` enters only as input metadata; never as a routing signal

CRITICAL: `capability_reference` / `mapped_capability` are READ-ONLY identity
references produced by the design-time-fixed DECLARATIVE_SPAN_TYPE_TO_CAPABILITY
table in schema_adapter. They are NEVER a selected capability (decision).
"""

from __future__ import annotations

from .normalization_adapter import (
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


class DatasheetPipeline:
    """Orchestration layer — wires the four components into one pipeline.

    A Human-driven, single-direction, zero-authority pipeline that turns an
    interface-contract `DocumentSpan` into a `MappingEvidence` observation.
    It is PURE ORCHESTRATION: it sequences the four adapters and passes each
    intermediate observation to the next. It performs NO selection, NO
    routing, NO decision, NO execution.

    Usage (Human-driven):
        pipeline = DatasheetPipeline()
        evidence = pipeline.run(document_span)

    The four component adapters are stateless; instances are created per-run
    (or may be shared — they hold no mutable authority).
    """

    def __init__(self) -> None:
        self._normalizer = NormalizationAdapter()
        self._schema = SchemaAdapter()
        self._extractor = ExtractionAdapter()
        self._evidence = EvidenceAdapter()

    def run(self, document: DocumentSpan) -> MappingEvidence:
        """Run the full Observation → Evidence pipeline.

        Sequentially delegates: normalize → map_schema → extract → produce.
        Each step is a read-only observation; the final artifact is an
        append-only MappingEvidence. ZERO decision/selection/routing.

        Args:
            document: the interface-contract input DocumentSpan (fact).

        Returns:
            MappingEvidence (observation artifact, invariants I-1~I-5).
        """
        normalized: NormalizedDocumentSpan = self._normalizer.normalize(document)
        candidate: SchemaMappingCandidate = self._schema.map_schema(normalized)
        fact: ExtractedFact = self._extractor.extract(candidate)
        evidence: MappingEvidence = self._evidence.produce(fact)
        return evidence


__all__ = [
    "DatasheetPipeline",
]
