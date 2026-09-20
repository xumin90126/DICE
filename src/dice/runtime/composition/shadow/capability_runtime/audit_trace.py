"""
Phase 6.1-L3: Audit Trace (Component 5).

The Audit Trace is the FIFTH and final passive carrier module of the L3
Capability Runtime. Its single responsibility is:

    RECORD the fact of exactly one already-occurred invocation.

It is a FACT RECORDING PROVIDER (AT-L1). It receives facts that have
ALREADY happened and appends them as an immutable `TraceRecord` (a frozen,
append-only historical fact snapshot). It NEVER infers causes, interprets
facts, evaluates quality, generates recommendations, produces decision
evidence, rewrites event meaning, or triggers any action.

It is NOT a Decision Maker, NOT a Governance Engine, NOT a Metrics Engine,
NOT a Monitoring System, NOT a Policy Engine, NOT a Recommendation Engine,
and NOT an Execution Engine.

Contract (from phase6_1_l3_audit_trace_design_package.md §5, method name
per Component 5 Step 2 Authorization):

    Input     Facts of one already-occurred invocation:
              invocation_id / capability_id (+ capability_version /
              input_ref_id / output_ref_id / invoked_at, read-only echoes)
    Output    TraceRecordResult (RECORDED + immutable TraceRecord, or
              REJECTED + factual message)
    Duty      Record already-happened facts as an append-only fact record
    Error     missing invocation identity / capability identity -> REJECTED
              (a factual observation; no retry, no fallback, no action)
    Forbidden inference / interpretation / evaluation / recommendation /
              decision / action-triggering / cross-invocation aggregation

Implementation constraints (AT-L1~AT-L5):
    - AT-L1  Fact Recording Provider Only: facts only; no inference,
             recommendation, evaluation, decision-evidence, or rewrite
    - AT-L2  No Control Authority: no decide/approve/reject/activate/
             invoke/execute/route/dispatch/govern
    - AT-L3  No Metrics / Monitoring: no score/ranking/confidence/quality/
             performance/priority/rating/trend/alert
    - AT-L4  Append-only: facts appended; never modify/delete/overwrite/
             back-write Runtime state / change Capability state
    - AT-L5  No Frozen Baseline Break: zero Registry / Layer 1-8 coupling

Invariants enforced by construction (aligned with the five frozen L3
invariants I-1~I-5):
    parent always None              (I-1: no recursive/self/cross invocation)
    shadow_marked always True       (I-2)
    is_hypothetical always True     (I-3)
    origin always "composition_shadow_storage" (I-4)
    production_execution always False (I-5)
"""

from __future__ import annotations

from typing import Optional

from .models.trace import (
    TraceRecord,
    TraceRecordResult,
    TraceStatus,
)


class AuditTrace:
    """
    Fact Recording Provider for a single already-occurred invocation.

    Usage (Human-driven, per call):
        audit = AuditTrace()
        result = audit.record_trace(
            invocation_id="inv_001",
            capability_id="CAP-STORAGE-DETECT",
        )
        if result.recorded:
            record = result.record   # TraceRecord (immutable, append-only)

    The AuditTrace has EXACTLY ONE public method: record_trace().
    It has NO select/route/recommend/rank/score/choose/match/resolve/
    dispatch/decide/plan/activate/invoke/execute/govern/monitor/evaluate/
    approve/reject/authorize methods. It is stateless: each call produces a
    fresh, unique, immutable TraceRecord and never mutates prior records.
    """

    # ── Factual recording basis (read-only, descriptive) ──
    TRACE_BASIS: str = "per_invocation_fact_v1"

    # ── Factual reason messages (observation only, NOT actions) ──
    RM_INVALID_INVOCATION: str = (
        "rejected: invocation_id is required (the invocation identity of the "
        "already-occurred fact, AT-L1)"
    )
    RM_INVALID_CAPABILITY: str = (
        "rejected: capability_id is required (the capability identity that "
        "was invoked, AT-L1)"
    )

    def record_trace(
        self,
        invocation_id: str,
        capability_id: str,
        invoked_at: str = "",
        capability_version: str = "",
        input_ref_id: str = "",
        output_ref_id: str = "",
    ) -> TraceRecordResult:
        """
        Record the fact of one already-occurred invocation.

        Report-only: this appends an immutable `TraceRecord` fact snapshot
        and returns a `TraceRecordResult` observation. It NEVER infers,
        interprets, evaluates, recommends, decides, or acts. An invalid
        request yields a REJECTED observation (no block, no retry, no
        fallback, no routing, no action).

        Args:
            invocation_id:    Identity of the invocation that already happened.
            capability_id:    Exact capability identity that was invoked.
            invoked_at:       ISO-8601 timestamp of when the invocation
                              happened (read-only echo; empty when not supplied).
            capability_version: The capability version (fact; empty if absent).
            input_ref_id:     Read-only ID reference to the input (no data copy).
            output_ref_id:    Read-only ID reference to the output (no data copy).

        Returns:
            TraceRecordResult (observation; RECORDED or REJECTED).
        """
        reason = self._rejection_reason(
            invocation_id=invocation_id,
            capability_id=capability_id,
        )
        if reason is not None:
            # Reject recording — report only, never act (AT-L1 reject-first).
            return TraceRecordResult(
                status=TraceStatus.REJECTED,
                record=None,
                message=reason,
            )

        record = TraceRecord(
            invocation_id=invocation_id,
            capability_id=capability_id,
            capability_version=capability_version,
            input_ref_id=input_ref_id,
            output_ref_id=output_ref_id,
            invoked_at=invoked_at,
            parent=None,                          # invariant I-1: never anything else
            shadow_marked=True,                   # invariant I-2
            origin="composition_shadow_storage",  # invariant I-4
            is_hypothetical=True,                 # invariant I-3
            production_execution=False,           # invariant I-5: never True
        )
        return TraceRecordResult(
            status=TraceStatus.RECORDED,
            record=record,
            message="trace recorded",
        )

    # ────────────────────────────────────────────────────────────────────
    # Private validation helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _rejection_reason(
        invocation_id: str,
        capability_id: str,
    ) -> Optional[str]:
        """Return a rejection message, or None if the fact set is recordable.

        Validation is deterministic and factual. It never recommends an
        alternative, never ranks, never matches, never falls back, and never
        triggers an action.
        """
        if not isinstance(invocation_id, str) or not invocation_id.strip():
            return AuditTrace.RM_INVALID_INVOCATION

        if not isinstance(capability_id, str) or not capability_id.strip():
            return AuditTrace.RM_INVALID_CAPABILITY

        return None
