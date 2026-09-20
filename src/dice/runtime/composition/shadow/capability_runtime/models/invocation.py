"""
Phase 6.1-L3: Invocation Context Data Models (Component 2).

Defines the passive carrier data structures produced by the Invocation
Context Recorder. These are observation-only artifacts:

    InvocationContext      — a structured record of one Human-authorized call
    InvocationRecordResult — the observation result of record_invocation()

Invariants enforced by construction:
    authorized_by always "human" (I-A: no autonomous invocation, IR-L3)
    parent always None           (I-1: no recursive/self/cross invocation)
    shadow_marked always True    (I-2)
    is_hypothetical always True  (I-3)
    origin always "composition_shadow_storage" (I-4)

These models are PURE PASSIVE CARRIERS — they hold facts only. They contain
no decision, no routing, no activation, no governance, no metrics, no
recommendation, no ranking fields (the "strategic fields" forbidden by the
Invocation Context contract §3.3 and CH-1~CH-3 completion conditions).

CH-condition compliance (Context Holder Completion Review):
    CH-1  immutable hosting boundary   — this is a fact record, not memory
    CH-2  no upward authority flow     — context never flows to Decision
    CH-3  no cross-component expansion — no shared state bus, self-contained
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class InvocationRecordStatus(Enum):
    """Outcome of a record_invocation() attempt (observation, not action)."""

    RECORDED = "recorded"    # invocation context recorded successfully
    REJECTED = "rejected"    # unauthorized/invalid -> not recorded (report only)


@dataclass
class InvocationContext:
    """A structured record of exactly one Human-authorized invocation.

    This is the Output of the Invocation Context Recorder (Component 2).
    It holds FACTS ONLY: who authorized (always "human"), which capability
    identity was requested, which input is referenced (by ID, read-only),
    and when the invocation happened. There is no decision, no order, no
    retry, no fallback, no priority, no governance, no metrics anywhere in
    this structure.

    Fields:
        invocation_id:   Human-issued invocation identifier
        capability_id:   The exact capability identity Human selected
        input_reference: Read-only reference to the input (ID / document id)
        input_ref_type:  The kind of reference (observation / simulation / etc.)
        authorized_by:   Always "human" (fact; IR-L3 no autonomous invocation)
        parent:          Always None (invariant I-1)
        shadow_marked:   Always True (invariant I-2)
        origin:          Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical: Always True (invariant I-3)
        invoked_at:      ISO-8601 timestamp of the recorded invocation (fact)
    """

    # ── Identity ──
    invocation_record_id: str = field(default_factory=lambda: str(uuid4()))
    invocation_id: str = ""

    # ── Factual payload (read-only references, no live pointers) ──
    capability_id: str = ""
    input_reference: str = ""
    input_ref_type: str = ""

    # ── Invocation ownership (fact, IR-L3) ──
    authorized_by: str = "human"  # ALWAYS "human" — never set to anything else

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    shadow_version: str = "1.0"

    # ── Metadata ──
    invoked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invocation_record_id": self.invocation_record_id,
            "invocation_id": self.invocation_id,
            "capability_id": self.capability_id,
            "input_reference": self.input_reference,
            "input_ref_type": self.input_ref_type,
            "authorized_by": self.authorized_by,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "invoked_at": self.invoked_at,
        }

    def __repr__(self) -> str:
        return (
            f"InvocationContext(id={self.invocation_record_id[:8]}..., "
            f"capability={self.capability_id!r}, "
            f"authorized_by={self.authorized_by!r}, parent={self.parent}, "
            f"shadow_marked={self.shadow_marked})"
        )


@dataclass
class InvocationRecordResult:
    """Observation result of a record_invocation() attempt.

    Pure observation — reports whether the invocation context was recorded,
    and carries a read-only reason when rejected. It NEVER performs an
    action: no block, no retry, no fallback, no routing (E1/E2/E3 error
    contract principles).
    """

    # ── Outcome ──
    status: InvocationRecordStatus = InvocationRecordStatus.RECORDED

    # ── Produced context (present only when RECORDED) ──
    context: Optional[InvocationContext] = None

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
        """Convenience read: whether the invocation context was recorded."""
        return self.status == InvocationRecordStatus.RECORDED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "context": self.context.to_dict() if self.context is not None else None,
            "message": self.message,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "recorded_at": self.recorded_at,
        }

    def __repr__(self) -> str:
        return (
            f"InvocationRecordResult(status={self.status.value}, "
            f"recorded={self.recorded}, shadow_marked={self.shadow_marked})"
        )
