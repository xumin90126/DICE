"""
Phase 16.11: Validation Memory Foundation — ValidationRecord + ValidationMemory.

CAND-002 (datasheet EXTEND) — Human Validation → Capability Formation bridge,
layer 1 (the memory foundation).

This module introduces the Validation Memory Foundation: the structured,
append-only, zero-authority record of Human validation decisions. It upgrades
the human's per-span decision (previously just `promote: bool` + `span_type`)
into a structured, aggregate-able, traceable `ValidationRecord`, plus an
append-only store with a read-only query interface.

Position in the data flow (Phase 16.10 Design Review §4 Evidence Learning Loop):
    Human Validation (gate produces PromotionResult)   ← existing, UNCHANGED
        → caller constructs a ValidationRecord         ← NEW, OUT-OF-BAND
        → ValidationMemory.append(record)              ← NEW, append-only
        → (future) Capability Formation reads history  ← NOT in this phase

CRITICAL BOUNDARY (Phase 16.11 Scope):
    - ValidationRecord is a FACT RECORD (observation + decision history). It
      is NOT a decision object, NOT a capability, NOT an execution plan.
    - ValidationMemory is an append-only, read-only store. It is NOT a
      classifier, NOT an aggregator, NOT a registrar, NOT a decision engine.
    - `human_validation_gate.py` is NOT modified. The gate produces the
      decision (Decision Authority); this module records the decision
      (Decision Memory). The two responsibilities are DECOUPLED.
    - No automatic formation: this module does NOT aggregate records into a
      CapabilityCandidateObservation. (Aggregation is a future formation
      concern, and even then it is deterministic + Human-gated.)
    - No external model (LLM/embedding/OCR). stdlib + same-package only.

FORBIDDEN fields (never present by construction):
    decision / recommendation / ranking / score / confidence / priority /
    selection / routing / fallback / activation / execution_plan /
    capability_id-selection logic

Invariants (I-1 ~ I-5) enforced by construction on every artifact:
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────────
# Structured reason enumeration (Phase 16.10 §5.2).
#
# This frozenset is a DOCUMENTATION / REFERENCE contract, NOT a validation
# gate. The store ACCEPTS unknown reasons (keeping observation-only semantics);
# reason validation is deferred to a future formation phase. A frozen set also
# guarantees the enumerated contract is never mutated at runtime.
# ──────────────────────────────────────────────────────────────────────────
VALIDATION_REASONS: frozenset = frozenset({
    "SPEC_DECLARATION",        # 规格声明
    "RECOMMENDED_CONDITION",   # 推荐条件
    "COMPONENT_INFO",          # 组分信息
    "SPEC_TABLE",              # 规格表
    "PROCEDURE_EXCLUDED",      # 过程性内容（排除）
    "MARKETING_EXCLUDED",      # 营销内容（排除）
    "AMBIGUOUS_UNKNOWN",       # 无法判定
})

# Decision outcome tokens (documentation contract). The store does NOT enforce
# these — it records whatever the Human decided, keeping observation-only
# semantics. Enforcement/validation is a future formation concern.
DECISION_ACCEPT = "ACCEPT"
DECISION_REJECT = "REJECT"


@dataclass
class ValidationRecord:
    """A structured, zero-authority record of ONE Human validation decision.

    This is a FACT RECORD: it records the human's decision, the structured
    reason, the context the human used, the structural patterns that triggered
    the judgment, and any exception marking — plus the mandatory shadow
    invariants. It is the memory foundation for future Capability Formation.

    It is FORBIDDEN from carrying capability selection, execution plans,
    confidence scores, or automatic approval. It records WHAT happened and
    WHY (per the human), never WHAT TO DO NEXT.

    Invariants (I-1 ~ I-5) enforced by construction.

    Fields:
        validation_id   : unique record identity (store-generated or supplied)
        candidate_key   : the related CandidateSpan identity (fact; reuses
                          human_validation_gate.candidate_key semantics)
        document_id     : source document identifier (fact)
        page_reference  : 1-based source page number (fact)
        decision        : the human decision outcome (ACCEPT / REJECT; fact)
        span_type       : the human-assigned span_type (ACCEPT); UNKNOWN/empty
                          on REJECT (fact)
        reason          : structured reason enum (fact; see VALIDATION_REASONS)
        context_snapshot: what context the human used (span_text_fragment /
                          hint_matches / page_geometry) (fact)
        pattern_evidence: which structural patterns triggered the judgment
                          (e.g. colon_kv / number_unit / table_row) (fact)
        is_exception    : whether this is an exception case (fact; negative
                          boundary evidence source)
        exception_note  : structured exception note (fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
        recorded_at     : ISO-8601 timestamp (fact)
    """

    # ── identity + provenance ──
    validation_id: str = ""             # unique record id (store-generated or supplied)
    candidate_key: str = ""             # related CandidateSpan identity (fact)
    document_id: str = ""               # source document id (fact)
    page_reference: int = 0             # 1-based page number (fact)

    # ── decision (Human decision, fact — NOT a system decision) ──
    decision: str = ""                  # ACCEPT / REJECT (fact)
    span_type: str = ""                 # human-assigned span_type (fact)

    # ── reason (structured enum, fact) ──
    reason: str = ""                    # VALIDATION_REASONS member or unknown

    # ── context (what context the human used) ──
    context_snapshot: Dict[str, Any] = field(default_factory=dict)

    # ── pattern (which structural patterns triggered the judgment) ──
    pattern_evidence: List[str] = field(default_factory=list)

    # ── exception (例外标记) ──
    is_exception: bool = False
    exception_note: str = ""

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None        # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    recorded_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "candidate_key": self.candidate_key,
            "document_id": self.document_id,
            "page_reference": self.page_reference,
            "decision": self.decision,
            "span_type": self.span_type,
            "reason": self.reason,
            "context_snapshot": dict(self.context_snapshot),
            "pattern_evidence": list(self.pattern_evidence),
            "is_exception": self.is_exception,
            "exception_note": self.exception_note,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "recorded_at": self.recorded_at,
        }


class ValidationMemory:
    """Append-only, read-only, zero-authority store of ValidationRecord.

    This is the Decision Memory: it persists the human's validation history as
    an append-only sequence of fact records, and exposes a READ-ONLY query
    interface. It is NOT a classifier, NOT an aggregator, NOT a registrar,
    NOT a decision engine.

    KEY CONTRACTS:
        - APPEND-ONLY : only `append` mutates; there is NO update / delete /
          overwrite method. Records are immutable once stored.
        - IMMUTABLE READS : every query returns a `copy.deepcopy`, so the
          caller can never mutate the stored history.
        - ZERO AUTHORITY : queries are deterministic field-equality filters
          (no ranking / scoring / selection / routing / decision).
        - NO FORMATION   : this store does NOT aggregate records into a
          CapabilityCandidateObservation (future phase, Human-gated).

    Usage (Human-driven):
        memory = ValidationMemory()
        vid = memory.append(record)
        records = memory.query_by_document("DS-001")
    """

    def __init__(self) -> None:
        self._records: List[ValidationRecord] = []
        # Read-only id → last-insertion-index map (O(1) exact lookup). This is
        # a READ-ONLY index over the history, NOT a selection/ranking.
        self._index: Dict[str, int] = {}
        self._seq: int = 0

    def append(self, record: ValidationRecord) -> str:
        """Append one record (append-only). Returns its validation_id.

        A deep copy is stored, so later mutation of the caller's object does
        NOT affect the stored history. If the record has no validation_id, a
        unique one is generated (`vr-{n}`). No update/delete/overwrite is
        possible — appending is the ONLY mutation.

        Args:
            record: the ValidationRecord to persist (fact).

        Returns:
            The validation_id of the stored record.
        """
        stored = copy.deepcopy(record)
        if not stored.validation_id:
            self._seq += 1
            stored.validation_id = f"vr-{self._seq}"
        self._records.append(stored)
        self._index[stored.validation_id] = len(self._records) - 1
        return stored.validation_id

    def get(self, validation_id: str) -> Optional[ValidationRecord]:
        """Exact lookup by validation_id; returns an immutable deep copy.

        Returns None when the id is unknown. This is a deterministic exact
        lookup (fact), NOT a selection/ranking.
        """
        idx = self._index.get(validation_id)
        if idx is None:
            return None
        return copy.deepcopy(self._records[idx])

    # ── Read-only query interface (deterministic filters, immutable results) ──

    def query_by_document(self, document_id: str) -> List[ValidationRecord]:
        """All records whose document_id equals the given value (insertion order)."""
        return [copy.deepcopy(r) for r in self._records
                if r.document_id == document_id]

    def query_by_span_type(self, span_type: str) -> List[ValidationRecord]:
        """All records whose span_type equals the given value (insertion order)."""
        return [copy.deepcopy(r) for r in self._records
                if r.span_type == span_type]

    def query_by_decision(self, decision: str) -> List[ValidationRecord]:
        """All records whose decision equals the given value (insertion order)."""
        return [copy.deepcopy(r) for r in self._records
                if r.decision == decision]

    def query_by_reason(self, reason: str) -> List[ValidationRecord]:
        """All records whose reason equals the given value (insertion order)."""
        return [copy.deepcopy(r) for r in self._records
                if r.reason == reason]

    def query_by_exception(self, is_exception: bool) -> List[ValidationRecord]:
        """All records matching the given exception flag (insertion order)."""
        return [copy.deepcopy(r) for r in self._records
                if r.is_exception == is_exception]

    def query_by_pattern(self, pattern_name: str) -> List[ValidationRecord]:
        """All records whose pattern_evidence contains the given name (in order)."""
        return [copy.deepcopy(r) for r in self._records
                if pattern_name in r.pattern_evidence]

    def all_records(self) -> List[ValidationRecord]:
        """All records in insertion order (immutable deep copies)."""
        return [copy.deepcopy(r) for r in self._records]

    def count(self) -> int:
        """Number of stored records (fact)."""
        return len(self._records)


__all__ = [
    "ValidationRecord",
    "ValidationMemory",
    "VALIDATION_REASONS",
    "DECISION_ACCEPT",
    "DECISION_REJECT",
]
