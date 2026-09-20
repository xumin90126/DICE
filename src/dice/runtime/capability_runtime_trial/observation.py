"""
Phase 16.16: Capability Runtime Trial — Observation output model (Step 2).

CapabilityRuntimeObservation is the OUTPUT of the Capability Runtime Trial
Runner. It is a READ-ONLY observation package that carries the observation
artifacts produced by ONE Human-driven consumption of a Registered
Capability through the Capability Runtime boundary (Phase 16.14):

    0. capability_id       — exact capability identity echo (FACT, never a
                              selection, never a Capability instance)
    1. load_result         — CapabilityLoadResult    (Exact Lookup observation)
    2. invocation_context  — InvocationContext       (Human authorization fact)
    3. boundary_report     — BoundaryEvaluationReport (boundary observation)
    4. evidence_record     — MappingEvidence          (pipeline observation,
                                                        present only when
                                                        boundary = WITHIN)
    5. trace_record        — TraceRecord              (append-only fact)

Each artifact is ALREADY a zero-authority observation produced by an
already-frozen zero-authority component (L3 five components + Datasheet
Pipeline). The `capability_id` is a STRING echo of the Human-specified
identity — it holds NO Capability instance (Phase 16.13 object model has no
runtime implementation; the only "reference" held here is the Loader's
read-only `CapabilityReference` with reference_kind="readonly_reference",
never an execution handle). This Observation therefore holds ZERO authority
itself: it is a pure carrier of observation artifacts, and inherits its
zero-authority by CONSTRUCTION (Phase 16.15 §8.2/§8.3).

FORBIDDEN fields (never present by construction):
    decision / score / confidence / selection / routing / execution / action /
    selected_capability / capability_decision / execution_plan / priority /
    ranking / recommendation / block / reject_action / fallback / retry /
    Capability instance (no full Capability object is ever held here)

Invariants enforced by construction (I-1 ~ I-5):
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dice.runtime.composition.shadow.capability_runtime.models.invocation import (
    InvocationContext,
)
from dice.runtime.composition.shadow.capability_runtime.models.loader import (
    CapabilityLoadResult,
)
from dice.runtime.composition.shadow.capability_runtime.models.trace import (
    TraceRecord,
)
from dice.runtime.extensions.datasheet.evidence_adapter import MappingEvidence

from .models import BoundaryEvaluationReport


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CapabilityRuntimeObservation:
    """READ-ONLY observation package (output of the Trial Runtime Runner).

    Carries the five observation artifacts of one Human-driven consumption of
    a Registered Capability. Each artifact is itself a zero-authority
    observation; the Observation is a pure carrier and introduces ZERO
    authority of its own. It does NOT decide, score, select, route, or
    execute anything — it merely presents what the frozen components observed.

    CRITICAL: the five artifacts are held as READ-ONLY references (instances
    produced by frozen components, never mutated here). There is no
    `selected_capability`, no `capability_decision`, no `execution_plan`, no
    `score`, no `priority`, no `confidence`, no action field.

    Fields:
        capability_id       : exact capability identity echo (FACT, from the
                              Human-specified request; never a selection)
        load_result         : CapabilityLoadResult (Exact Lookup; FOUND/...)
        invocation_context  : InvocationContext (authorized_by="human", fact)
        boundary_report     : BoundaryEvaluationReport (WITHIN / ...)
        evidence_record     : MappingEvidence (pipeline observation; WITHIN only)
        trace_record        : TraceRecord (append-only invocation fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
        observed_at         : ISO-8601 timestamp (fact)
    """

    # ── Exact identity echo (FACT, not a selection / not a Capability instance) ──
    capability_id: str = ""

    # ── Observation artifacts (each a zero-authority observation) ──
    load_result: Optional[CapabilityLoadResult] = None
    invocation_context: Optional[InvocationContext] = None
    boundary_report: Optional[BoundaryEvaluationReport] = None
    evidence_record: Optional[MappingEvidence] = None
    trace_record: Optional[TraceRecord] = None

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    observed_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "load_result": (
                self.load_result.to_dict() if self.load_result else None
            ),
            "invocation_context": (
                self.invocation_context.to_dict()
                if self.invocation_context
                else None
            ),
            "boundary_report": (
                self.boundary_report.to_dict() if self.boundary_report else None
            ),
            "evidence_record": (
                self.evidence_record.to_dict() if self.evidence_record else None
            ),
            "trace_record": (
                self.trace_record.to_dict() if self.trace_record else None
            ),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "observed_at": self.observed_at,
        }


__all__ = [
    "CapabilityRuntimeObservation",
]
