"""
Phase 6.1-L3: Audit Trace Data Models (Component 5).

Defines the passive carrier data structures produced by the Audit Trace
component. These are observation-only artifacts:

    TraceStatus         — RECORDED / REJECTED (a factual recording outcome,
                          NOT a decision, NOT an action)
    TraceRecord         — an immutable, append-only fact record of exactly
                          ONE already-occurred invocation (the core artifact)
    TraceRecordResult   — the observation result of record_trace()

This component is a FACT RECORDING PROVIDER (AT-L1). It records facts that
have ALREADY happened; it NEVER infers causes, generates recommendations,
evaluates quality, produces decision evidence, or rewrites the meaning of
events.

Field whitelist (from Human Authorization, Component 5, AT-L1~AT-L5):
    ALLOWED   trace_id / invocation_id / capability_id / capability_version
              / input_ref_id / output_ref_id / invoked_at / recorded_at
              / status / message / parent / shadow_marked / origin
              / is_hypothetical / production_execution
    FORBIDDEN decision / score / ranking / confidence / quality / performance
              / priority / rating / trend / alert / recommendation / policy
              / action authority / success / failure / duration / latency
              / result_count / pass_rate / cumulative_* / risk_level
              / decision_by / decision_result / approval_status / gate_result
              / production_impact / production_log

AT-condition compliance:
    AT-L1  Fact Recording Provider Only — facts only, no inference/recommendation
                                          /evaluation/decision-evidence/rewrite
    AT-L2  No Control Authority         — no decide/approve/reject/activate/
                                          invoke/execute/route/dispatch/govern
    AT-L3  No Metrics / Monitoring      — no score/ranking/confidence/quality/
                                          performance/priority/rating/trend/alert
    AT-L4  Append-only                  — facts appended; never modify/delete/
                                          overwrite/back-write Runtime state
    AT-L5  No Frozen Baseline Break     — zero Registry / Layer 1-8 coupling

Invariants enforced by construction:
    parent always None              (I-1: no recursive/self/cross invocation)
    shadow_marked always True       (I-2)
    is_hypothetical always True     (I-3)
    origin always "composition_shadow_storage" (I-4)
    production_execution always False (I-5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class TraceStatus(Enum):
    """Outcome of a record_trace() attempt (a factual observation, not action).

    RECORDED — the invocation fact was appended to the audit trace.
    REJECTED — the supplied fact was malformed/absent and was NOT recorded
               (reported back as an observation; no action taken).

    NOTE: this status is NOT a decision, approval, rejection action, or
    quality judgment. It is a factual statement of the recording outcome.
    What to do with it is decided by Human, never by this component.
    """

    RECORDED = "recorded"
    REJECTED = "rejected"


@dataclass
class TraceRecord:
    """An immutable, append-only fact record of exactly one invocation.

    This is the core Output of the Audit Trace component (Component 5). It
    holds FACTS ONLY: which invocation happened, which capability identity
    was invoked, which input and output are referenced (by read-only ID,
    never by copying their contents), and when it happened. There is NO
    inference, NO recommendation, NO evaluation, NO decision evidence, NO
    metrics, NO governance, NO production anywhere in this structure.

    The record is IMMUTABLE by convention (append-only, AT-L4): it is a
    frozen fact snapshot. There are NO mutator methods; history is never
    modified, deleted, or overwritten.

    Fields (factual whitelist — AT-L1):
        trace_id:          Unique identity of this trace (uuid)
        invocation_id:     Read-only reference to the invocation this trace
                           belongs to (echoed fact, not rewritten)
        capability_id:     The exact capability identity that was invoked
        capability_version: The capability version (fact, empty if absent)
        input_ref_id:      Read-only ID reference to the input (no data copy)
        output_ref_id:     Read-only ID reference to the output (no data copy)
        invoked_at:        ISO-8601 timestamp of when the invocation happened
        parent:            Always None (invariant I-1)
        shadow_marked:     Always True (invariant I-2)
        origin:            Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:   Always True (invariant I-3)
        production_execution: Always False (invariant I-5)
    """

    # ── Identity ──
    trace_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Factual payload (read-only references, no live pointers, no data copy) ──
    invocation_id: str = ""
    capability_id: str = ""
    capability_version: str = ""
    input_ref_id: str = ""
    output_ref_id: str = ""

    # ── Factual timestamp (when the invocation happened, echoed fact) ──
    invoked_at: str = ""

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "invocation_id": self.invocation_id,
            "capability_id": self.capability_id,
            "capability_version": self.capability_version,
            "input_ref_id": self.input_ref_id,
            "output_ref_id": self.output_ref_id,
            "invoked_at": self.invoked_at,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "recorded_at": self.recorded_at,
        }

    def __repr__(self) -> str:
        return (
            f"TraceRecord(id={self.trace_id[:8]}..., "
            f"invocation={self.invocation_id!r}, "
            f"capability={self.capability_id!r}, parent={self.parent}, "
            f"shadow_marked={self.shadow_marked})"
        )


@dataclass
class TraceRecordResult:
    """Observation result of a record_trace() attempt.

    Pure observation — reports whether the invocation fact was appended to
    the audit trace, and carries a read-only message when rejected. It NEVER
    performs an action: no retry, no fallback, no routing, no activation, no
    governance, no production (AT-L2, AT-L4, AT-L5).

    Fields:
        status:             RECORDED / REJECTED (factual outcome)
        record:             The immutable TraceRecord (present only when RECORDED)
        message:            Read-only observation message (reason, empty when
                            RECORDED)
        shadow_marked:      Always True (invariant I-2)
        origin:             Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:    Always True (invariant I-3)
        recorded_at:        ISO-8601 timestamp of the recording (fact)
    """

    # ── Outcome ──
    status: TraceStatus = TraceStatus.RECORDED

    # ── Produced record (present only when RECORDED) ──
    record: Optional[TraceRecord] = None

    # ── Observation message (reason, read-only) ──
    message: str = ""

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True

    # ── Metadata ──
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def recorded(self) -> bool:
        """Convenience read: whether the trace fact was appended (observation)."""
        return self.status == TraceStatus.RECORDED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "record": self.record.to_dict() if self.record is not None else None,
            "message": self.message,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "recorded_at": self.recorded_at,
        }

    def __repr__(self) -> str:
        return (
            f"TraceRecordResult(status={self.status.value}, "
            f"recorded={self.recorded}, shadow_marked={self.shadow_marked})"
        )
