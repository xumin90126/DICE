"""
Phase 16.1: Datasheet Extension — Schema Adapter (Skeleton).

CAND-002 (datasheet EXTEND) Implementation Adapter layer, component 2 of 4.
This module is a STRUCTURE-ONLY skeleton: it defines the schema-mapping
intermediate type (`SchemaMappingCandidate`) and the adapter class with its
method signature. NO business mapping logic is implemented here — the
map_schema() body raises NotImplementedError by design.

Architecture position (Phase 14.5 Review 1 = B. Implementation Adapter layer):
    Declarative schema adaptation. Maps a normalized span's STRUCTURE onto an
    EXISTING Capability's `input_schema` — WITHOUT creating a new identity,
    WITHOUT modifying the Capability Definition, WITHOUT executing anything.

Chain position (single-direction data flow, Phase 14.5 §6.2):
    NormalizedDocumentSpan (component 1 out) → SchemaMappingCandidate (component 2 out)

Interface:
    Input  : NormalizedDocumentSpan
    Output : SchemaMappingCandidate

Responsibilities:
    IN  : schema mapping adapter (declarative adaptation, zero execution)
    OUT : capability selection / document_type routing / ranking / decision

Field whitelist (ALLOWED only):
    span_id / span_type / source_schema / target_capability_input_schema
    (read-only references + declarative schema descriptors)
FORBIDDEN:
    decision / recommendation / ranking / score / confidence / priority /
    selection / routing / fallback / activation / execution_plan /
    capability_id selection logic

CRITICAL: the schema mapping is a DECLARATIVE, design-time-fixed adaptation
of a span's structure onto an existing capability input schema. It does NOT
select which capability to use; it merely records the structural compatibility
fact. No `document_type` routing, no capability selection.

Invariants enforced by construction on the OUTPUT artifact:
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False  (I-1 ~ I-5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .normalization_adapter import NormalizedDocumentSpan, SpanType


# Design-time-fixed declarative mapping (Phase 14.5 §4 Reuse Mapping).
#
# This is a DECLARATIVE, design-time-fixed correspondence between a span's
# declarative semantic category (SpanType) and an EXISTING capability
# identity. It is NOT a runtime selection: there is no fallback, no ranking,
# no score, no priority, no "choose the best capability". An UNKNOWN span type
# maps to an empty identity — the honest fact "no declarative mapping applies".
#
# The values are READ-ONLY identity references into the frozen capability
# table (capability_loader.FROZEN_CAPABILITY_TABLE); they are never rewritten
# here and never grant execution authority.
DECLARATIVE_SPAN_TYPE_TO_CAPABILITY: Dict[str, str] = {
    SpanType.SPECIFICATION_STATEMENT.value: "CAP-PARAMETER-LIST",
    SpanType.RECOMMENDED_CONDITION.value: "CAP-TEMP-RANGE",
    SpanType.COMPONENT_INFORMATION.value: "CAP-NAME-QTY-PAIR",
    SpanType.SPECIFICATION_TABLE.value: "CAP-TABLE-EXTRACT-BASIC",
    # SpanType.UNKNOWN -> "" (no declarative mapping — a fact, not a fallback)
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SchemaMappingCandidate:
    """Schema adaptation OUTPUT — a declarative structural-compatibility record.

    Produced by SchemaAdapter.map_schema(). It records the structural
    compatibility between a normalized span and an existing capability's
    input schema. It is a FACTUAL observation, NOT a selection, NOT a
    decision, NOT an execution plan.

    The `target_capability_input_schema` field is a READ-ONLY reference to an
    existing capability's input schema descriptor — it is never rewritten and
    never grants execution. It carries NO capability_id-selection logic.

    Invariants (I-1 ~ I-5) enforced by construction.

    Fields:
        span_id                     : read-only reference to the source span
        span_type                   : declarative semantic category (fact)
        source_schema               : read-only structural descriptor of the
                                      source span (declarative schema)
        target_capability_input_schema : read-only reference to an existing
                                      capability's input schema descriptor
        parent / shadow_marked / origin / is_hypothetical /
        production_execution        : invariant fields (I-1 ~ I-5)
        mapped_at                   : ISO-8601 timestamp (fact)
    """

    # ── Read-only references ──
    span_id: str = ""
    span_type: str = ""

    # ── Declarative schema descriptors (read-only, zero execution) ──
    source_schema: Dict[str, Any] = field(default_factory=dict)
    target_capability_input_schema: Dict[str, Any] = field(default_factory=dict)

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None       # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    mapped_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "span_type": self.span_type,
            "source_schema": dict(self.source_schema),
            "target_capability_input_schema": dict(self.target_capability_input_schema),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "mapped_at": self.mapped_at,
        }


class SchemaAdapter:
    """Component 2 of 4 — declarative schema adaptation (zero execution).

    Maps a normalized span's structure onto an existing capability's input
    schema as a DECLARATIVE adaptation. It records structural compatibility
    as a fact; it does NOT select a capability, does NOT route, does NOT
    execute, does NOT modify any Capability Definition.

    Usage (Human-driven):
        adapter = SchemaAdapter()
        candidate = adapter.map_schema(normalized_span)

    SKELETON NOTE (Phase 16.1): map_schema() raises NotImplementedError.
    The declarative schema-adaptation algorithm is business logic to be
    implemented in a later phase.
    """

    def map_schema(self, span: NormalizedDocumentSpan) -> SchemaMappingCandidate:
        """Adapt a normalized span's structure onto an existing input schema.

        Phase 16.2 — declarative, read-only adaptation: derives a structural
        descriptor of the source span and records a READ-ONLY reference to an
        existing capability's input schema (identity taken from the
        design-time-fixed DECLARATIVE_SPAN_TYPE_TO_CAPABILITY table). ZERO
        selection, ZERO routing, ZERO execution, ZERO identity creation.

        Args:
            span: the normalized span (component 1 output, observation).

        Returns:
            SchemaMappingCandidate (observation artifact, invariants I-1~I-5).
        """
        source_schema = {
            "span_id": span.span_id,
            "span_type": span.span_type,
            "normalized_text": span.normalized_text,
        }
        # Read-only identity reference from the design-time-fixed table.
        # NOT a selection: UNKNOWN -> "" (no declarative mapping applies).
        capability_id = DECLARATIVE_SPAN_TYPE_TO_CAPABILITY.get(span.span_type, "")
        target_capability_input_schema = {
            "capability_reference": capability_id,
        }
        return SchemaMappingCandidate(
            span_id=span.span_id,
            span_type=span.span_type,
            source_schema=source_schema,
            target_capability_input_schema=target_capability_input_schema,
        )


__all__ = [
    "SchemaMappingCandidate",
    "SchemaAdapter",
]
