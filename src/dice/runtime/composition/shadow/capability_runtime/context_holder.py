"""
Phase 6.1-L3: Runtime Context Holder (Component 1).

The Runtime Context Holder is the FIRST passive carrier module of the L3
Capability Runtime. Its single responsibility is:

    HOLD the context of one Human-authorized invocation.

It produces a `HostedContext` (an isolated, shadow-marked hosting container
with parent=None) and reports a `HostContextResult` observation. It does NOT
decide, route, reason, activate, or touch production.

Contract (from phase6_1_l3_runtime_interface_contract.md §3.1):

    Input     Human authorized invocation request
              (capability identity + input reference + invocation_id)
    Output    Isolated hosting context (parent=None)
    Duty      Save the context of one authorized invocation
    Error     Unauthorized call -> reject hosting (report only, no action)
    Forbidden decision / routing / reasoning / activation

Implementation constraints (IR-L1~IR-L5):
    - IR-L1  Infrastructure only: no decision/planning/routing fields
    - IR-L3  No autonomous invocation: parent always None
    - IR-L4  No metrics: no counters, no scoring, no aggregation
    - IR-L5  No production: zero production dependency
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models.context import (
    HostedContext,
    HostContextResult,
    HostContextStatus,
)


class RuntimeContextHolder:
    """
    Passive carrier for one authorized invocation's context.

    Usage (Human-driven, per call):
        holder = RuntimeContextHolder()
        result = holder.host_context(
            capability_id="CAP-STORAGE-DETECT",
            input_reference="sim_result_123",
            invocation_id="inv_001",
        )
        if result.hosted:
            ctx = result.context   # HostedContext (parent=None, shadow-marked)
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

    def host_context(
        self,
        capability_id: str,
        input_reference: str,
        invocation_id: str,
        input_ref_type: str = "",
    ) -> HostContextResult:
        """
        Host an isolated context for one Human-authorized invocation.

        Report-only: an unauthorized/invalid request yields a REJECTED result
        (a pure observation). No block, no retry, no fallback, no routing.

        Args:
            capability_id:  Exact capability identity Human selected.
            input_reference: Read-only reference to the input (by ID).
            invocation_id:  Human-issued invocation identifier.
            input_ref_type: Factual kind of the input reference.

        Returns:
            HostContextResult (observation; HOSTED or REJECTED).
        """
        reason = self._rejection_reason(
            capability_id=capability_id,
            input_reference=input_reference,
            invocation_id=invocation_id,
            input_ref_type=input_ref_type,
        )
        if reason is not None:
            # Reject hosting — report only, never act (E2 reject-first).
            return HostContextResult(
                status=HostContextStatus.REJECTED,
                context=None,
                message=reason,
            )

        context = HostedContext(
            invocation_id=invocation_id,
            capability_id=capability_id,
            input_reference=input_reference,
            input_ref_type=input_ref_type,
            parent=None,  # invariant I-1: never set to anything else
        )
        return HostContextResult(
            status=HostContextStatus.HOSTED,
            context=context,
            message="context hosted",
        )

    # ────────────────────────────────────────────────────────────────────
    # Private validation helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    def _rejection_reason(
        self,
        capability_id: str,
        input_reference: str,
        invocation_id: str,
        input_ref_type: str,
    ) -> Optional[str]:
        """Return a rejection reason string, or None if the request is valid.

        Validation is deterministic and factual. It never recommends an
        alternative, never ranks, never matches, never falls back.
        """
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
