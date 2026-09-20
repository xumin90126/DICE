"""
Phase 6.1-L3: Invocation Context Recorder (Component 2).

The Invocation Context Recorder is the SECOND passive carrier module of the
L3 Capability Runtime. Its single responsibility is:

    RECORD the context of one Human-authorized invocation.

It produces an `InvocationContext` (an isolated, shadow-marked fact record
with authorized_by="human", parent=None) and reports an
`InvocationRecordResult` observation. It does NOT decide, route, reason,
activate, invoke, govern, measure, or touch production.

Contract (from phase6_1_l3_runtime_interface_contract.md §3.3):

    Input     Human authorization + capability identity + input reference
    Output    Structured InvocationContext
              (invocation_id / invoked_at / parent=None / origin)
    Duty      Record the context of one Human-initiated invocation
    Error     No Human authorization -> reject recording (no autonomous call)
    Forbidden Autonomous Invocation / Recursive Invocation (parent always None)

Implementation constraints (IR-L1~IR-L5 + CH-1~CH-3):
    - IR-L1  Infrastructure only: no decision/planning/routing/activation fields
    - IR-L3  No autonomous invocation: authorized_by always "human", parent None
    - IR-L4  No metrics: no counters, no scoring, no aggregation
    - IR-L5  No production: zero production dependency
    - CH-1   Immutable hosting boundary (fact record, not memory)
    - CH-2   No upward authority flow (never flows to Decision)
    - CH-3   No cross-component expansion (self-contained, no shared bus)
"""

from __future__ import annotations

from typing import Optional

from .models.invocation import (
    InvocationContext,
    InvocationRecordResult,
    InvocationRecordStatus,
)


class InvocationContextRecorder:
    """
    Passive recorder for one authorized invocation's context.

    Usage (Human-driven, per call):
        recorder = InvocationContextRecorder()
        result = recorder.record_invocation(
            capability_id="CAP-STORAGE-DETECT",
            input_reference="sim_result_123",
            invocation_id="inv_001",
            authorized_by="human",
        )
        if result.recorded:
            ctx = result.context   # InvocationContext (parent=None, shadow-marked)
    """

    # ── Whitelist: the ONLY input_ref_type values accepted ──
    # This is a factual classification, not a routing decision.
    ALLOWED_INPUT_REF_TYPES = frozenset({
        "observation",
        "simulation_result",
        "trace",
        "snapshot",
        "document",
        "",
    })

    # ── The ONLY authorized initiator (IR-L3: no autonomous invocation) ──
    ALLOWED_AUTHORIZERS = frozenset({"human"})

    def record_invocation(
        self,
        capability_id: str,
        input_reference: str,
        invocation_id: str,
        authorized_by: str = "human",
        input_ref_type: str = "",
    ) -> InvocationRecordResult:
        """
        Record an isolated context for one Human-authorized invocation.

        Report-only: an unauthorized/invalid request yields a REJECTED result
        (a pure observation). No block, no retry, no fallback, no routing.

        Args:
            capability_id:  Exact capability identity Human selected.
            input_reference: Read-only reference to the input (by ID).
            invocation_id:  Human-issued invocation identifier.
            authorized_by:  The initiator. MUST be "human" (IR-L3). Any other
                            value is rejected (no autonomous invocation).
            input_ref_type: Factual kind of the input reference.

        Returns:
            InvocationRecordResult (observation; RECORDED or REJECTED).
        """
        reason = self._rejection_reason(
            capability_id=capability_id,
            input_reference=input_reference,
            invocation_id=invocation_id,
            authorized_by=authorized_by,
            input_ref_type=input_ref_type,
        )
        if reason is not None:
            # Reject recording — report only, never act (E2 reject-first).
            return InvocationRecordResult(
                status=InvocationRecordStatus.REJECTED,
                context=None,
                message=reason,
            )

        context = InvocationContext(
            invocation_id=invocation_id,
            capability_id=capability_id,
            input_reference=input_reference,
            input_ref_type=input_ref_type,
            authorized_by="human",  # invariant I-A: never anything else
            parent=None,            # invariant I-1: never anything else
        )
        return InvocationRecordResult(
            status=InvocationRecordStatus.RECORDED,
            context=context,
            message="invocation context recorded",
        )

    # ────────────────────────────────────────────────────────────────────
    # Private validation helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    def _rejection_reason(
        self,
        capability_id: str,
        input_reference: str,
        invocation_id: str,
        authorized_by: str,
        input_ref_type: str,
    ) -> Optional[str]:
        """Return a rejection reason string, or None if the request is valid.

        Validation is deterministic and factual. It never recommends an
        alternative, never ranks, never matches, never falls back.
        """
        if not isinstance(authorized_by, str) or not authorized_by.strip():
            return "rejected: authorized_by is required (Human authorization, IR-L3)"

        if authorized_by.strip() not in self.ALLOWED_AUTHORIZERS:
            return (
                f"rejected: authorized_by {authorized_by!r} is not permitted — "
                f"invocation authority belongs solely to Human (no autonomous invocation)"
            )

        if not isinstance(capability_id, str) or not capability_id.strip():
            return "rejected: capability_id is required (Human must select an exact capability identity)"

        if not isinstance(invocation_id, str) or not invocation_id.strip():
            return "rejected: invocation_id is required (Human authorization)"

        if not isinstance(input_reference, str) or not input_reference.strip():
            return "rejected: input_reference is required (read-only ID reference)"

        if not isinstance(input_ref_type, str):
            return "rejected: input_ref_type must be a string"

        if input_ref_type not in self.ALLOWED_INPUT_REF_TYPES:
            return (
                f"rejected: input_ref_type {input_ref_type!r} is not a known "
                f"factual reference kind"
            )

        return None
