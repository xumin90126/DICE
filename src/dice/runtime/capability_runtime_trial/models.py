"""
Phase 16.16: Capability Runtime Trial — Request & Boundary models (Skeleton).

This module is STEP 1 (Skeleton) of the Phase 16.16 Implementation. It
defines ONLY the two data-model contracts required by the trial design
(Phase 16.15 §4 / §7):

    1. CapabilityRuntimeRequest   — the Human-specified consumption request
    2. BoundaryEvaluationReport   — the boundary-evaluation observation

Both are PURE observation/data carriers. They hold ZERO authority: no
selection, no routing, no planning, no execution, no decision, no retry,
no fallback, no score, no ranking (Runtime Authority = ZERO).

They are the FIRST Capability Runtime Trial artifacts — the minimal,
Human-driven, read-only verification that a Registered Capability can be
consumed through the Capability Runtime boundary (Phase 16.14) WITHOUT
acquiring any authority.

Skeleton contract (Phase 16.16 Step 1):
    - The request carries the Human-specified exact `capability_id`
      (explicit identity, NOT a query/feature), the frozen-schema
      `DocumentSpan` fact, and a fixed `invocation_intent` of "observe".
    - The boundary report carries a THREE-state boundary observation
      (WITHIN / NEGATIVE_BOUNDARY_HIT / SCHEMA_MISMATCH), a factual list
      of touched declarations, and a factual reason.

CRITICAL: `capability_id` is an EXPLICIT identity supplied by Human BEFORE
the request is built. It is NEVER derived, selected, matched, or routed by
any code path here (Phase 16.15 §4.3). `span_type` on `document_span` is
owned by Human (assigned upstream by the Human Validation Gate, Phase 16.8),
and is only READ here.

Invariants enforced by construction on BOTH artifacts (I-1 ~ I-5):
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from dice.runtime.extensions.datasheet.normalization_adapter import DocumentSpan


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BoundaryStatus(Enum):
    """Boundary-evaluation outcome (a pure observation, not an action).

    Three states (Phase 16.16 Scope; the minimal trial vocabulary from
    Phase 16.15 §7.3):

        WITHIN              — the input span falls inside the capability's
                              declared Positive Boundary.
        NEGATIVE_BOUNDARY_HIT — the input span hits a declared negative
                              boundary exclusion (e.g. a procedure step /
                              marketing content).
        SCHEMA_MISMATCH     — the input span's schema does not satisfy the
                              capability's input_schema (e.g. missing the
                              required unit token).

    NOTE: this status is a FACTUAL statement of the boundary comparison. It
    is NOT a filter, NOT a block, NOT a routing decision, and NOT an action.
    What to do with it is decided by Human, never by this component.
    """

    WITHIN = "within"
    NEGATIVE_BOUNDARY_HIT = "negative_boundary_hit"
    SCHEMA_MISMATCH = "schema_mismatch"


@dataclass
class CapabilityRuntimeRequest:
    """The Human-specified Capability consumption request (input carrier).

    This is the INPUT to the Capability Runtime Trial Runner. It carries the
    Human's explicit, already-made selection of a capability identity, the
    frozen-schema DocumentSpan fact to observe, and a fixed observation
    intent. It is a FACTUAL description of "what Human asked the Runtime to
    observe" — NOT a query, NOT a trigger, NOT a routing signal, NOT a
    selection object.

    CRITICAL (Phase 16.15 §4.3):
        - `capability_id` is an EXPLICIT identity supplied by Human BEFORE
          this request is built. It is NEVER a "find me a capability" query,
          and NEVER selected/matched/routed by any code path.
        - `document_span` is a FACT to observe, not a trigger for which
          capability to use.
        - `invocation_intent` is fixed to "observe" for this trial (the
          execute intent is OUT of scope — Execution belongs to Human,
          Production = FALSE).

    Fields:
        capability_id      : explicit capability identity (Human-specified)
        document_span      : frozen-schema span to observe (Human-supplied)
        invocation_intent  : fixed "observe" (no execute path in this trial)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
    """

    # ── Explicit identity (Human-specified, NOT a query/feature) ──
    capability_id: str = ""

    # ── Frozen-schema span fact (Human-supplied; read-only) ──
    document_span: Optional[DocumentSpan] = None

    # ── Fixed observation intent (this trial: always "observe") ──
    invocation_intent: str = "observe"

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "document_span": (
                self.document_span.to_dict() if self.document_span else None
            ),
            "invocation_intent": self.invocation_intent,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
        }


@dataclass
class BoundaryEvaluationReport:
    """Boundary-evaluation observation (report-only, NOT a correction).

    Produced by the boundary-evaluation step of the Trial Runner (to be
    wired in a later step). It records the FACTUAL comparison between the
    input span and the capability's declared boundary. It is a pure
    observation: it NEVER corrects the input, NEVER retries, NEVER falls
    back, NEVER re-routes, NEVER blocks, NEVER authorizes (Phase 16.14 §8).

    Fields:
        boundary_status : one of BoundaryStatus (WITHIN /
                          NEGATIVE_BOUNDARY_HIT / SCHEMA_MISMATCH)
        violated_fields : factual list of touched declarations (empty = none)
        reason          : factual explanation (references the exclusion /
                          schema constraint that was compared)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
        evaluated_at    : ISO-8601 timestamp of the evaluation (fact)
    """

    # ── Boundary outcome (factual, three states) ──
    boundary_status: BoundaryStatus = BoundaryStatus.WITHIN

    # ── Touched declarations (factual list; empty = none touched) ──
    violated_fields: List[str] = field(default_factory=list)

    # ── Factual reason (references the compared declaration, not an action) ──
    reason: str = ""

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    evaluated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boundary_status": self.boundary_status.value,
            "violated_fields": list(self.violated_fields),
            "reason": self.reason,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "evaluated_at": self.evaluated_at,
        }


__all__ = [
    "BoundaryStatus",
    "CapabilityRuntimeRequest",
    "BoundaryEvaluationReport",
]
