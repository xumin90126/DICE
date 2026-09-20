"""
Phase 6.1-L3: Permission Evaluation (Component 3).

The Permission Evaluation component is the THIRD passive carrier module of
the L3 Capability Runtime. Its single responsibility is:

    REPORT the permission verdict for one Runtime behavior request.

It is an OBSERVATION CONTRACT PROVIDER (RED-GRD-003). It produces a
`PermissionEvaluationResult` (COMPLIANT / NON_COMPLIANT + read-only basis
references). It NEVER blocks, rejects, stops, authorizes, grants, routes,
or acts — the block/allow decision authority belongs solely to Human.

Contract (from phase6_1_l3_runtime_interface_contract.md §3.4 guard(), after
red-team semantic reconstruction):
    Input     a hosting request + permission claim (subject, action)
    Output    PermissionEvaluationResult (verdict, report-only, no action)
    Duty      verify Runtime Boundary before hosting (read-only)
    Error     violation -> NON_COMPLIANT (a verdict, NOT a block action)
    Forbidden autonomous authorize / autonomous allow / activation decision
              / production permission grant / Block / Reject / Stop / Action

Implementation constraints (IR-L1~IR-L5 + PE-L1~PE-L5):
    - IR-L1  Infrastructure only: no decision/planning/routing fields
    - IR-L3  No autonomous invocation: passive check, parent always None
    - IR-L4  No metrics: no counters, no scoring, no aggregation
    - IR-L5  No production: production_execution always False
    - PE-L1  Report-only: no block/deny/stop/reject
    - PE-L2  Not a Policy Engine: deterministic table lookup, no rule inference
    - PE-L3  No capability control: no invoke/activate/disable
    - PE-L4  No production access: no connector, no external execution
    - PE-L5  No metrics/ranking/governance info
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Optional, Tuple

from .models.permission import (
    PermissionEvaluationResult,
    PermissionVerdict,
)


class PermissionEvaluator:
    """Observation contract provider for Runtime permission evaluation.

    Usage (Human-driven, per call):
        evaluator = PermissionEvaluator()
        result = evaluator.evaluate_permission(
            subject="runtime",
            action="produce",
            capability_id="CAP-STORAGE-DETECT",
            invocation_id="inv_001",
        )
        if not result.compliant:
            # result.reason_code -> "PRODUCTION_FORBIDDEN" (observation only)
    """

    # ── Frozen Permission Matrix (deterministic lookup, deny-by-default) ──
    # This is the AUTHORITATIVE subject x action matrix, encoding the frozen
    # boundary matrix (phase6_1_l3_runtime_implementation_boundary_matrix.md §4)
    # and permission matrix (phase6_1_l3_runtime_permission_matrix.md §2).
    #
    # It is a pure DATA TABLE. evaluate_permission() performs a single
    # deterministic lookup against it. There is NO rule inference, NO policy
    # combination, NO condition chain, NO if/else accumulation (PE-L2).
    PERMISSION_MATRIX: Dict[str, Dict[str, bool]] = {
        "human": {
            "host": True,
            "load": True,
            "record": True,
            "evaluate": True,
            "trace": True,
            "invoke": True,
            "decide": True,
            "activate": True,   # potential permission, governance-constrained
            "govern": True,
            "metrics": True,
            "mutate": True,     # potential permission, governance-constrained
            "produce": False,   # Production Permission is ALWAYS FALSE
        },
        "runtime": {
            "host": True,
            "load": True,
            "record": True,
            "evaluate": True,
            "trace": True,
            "invoke": False,    # invocation authority belongs to Human
            "decide": False,    # decision authority belongs to Human
            "activate": False,  # activation authority belongs to Human
            "govern": False,    # governance belongs to L4 + Human
            "metrics": False,   # metrics forbidden (IR-L4)
            "mutate": False,    # no upstream write (P1 least privilege)
            "produce": False,   # production always FALSE
        },
        "capability": {
            # Pure passive execution unit — NO active permission whatsoever.
            "host": False,
            "load": False,
            "record": False,
            "evaluate": False,
            "trace": False,
            "invoke": False,
            "decide": False,
            "activate": False,
            "govern": False,
            "metrics": False,
            "mutate": False,
            "produce": False,
        },
    }

    # ── Matrix reference (read-only, factual) ──
    EVALUATED_AGAINST: str = "permission_matrix_v1"

    # ── Factual reason codes (observation only, NOT actions) ──
    RC_COMPLIANT: str = ""
    RC_PRODUCTION_FORBIDDEN: str = "PRODUCTION_FORBIDDEN"
    RC_ACTIVATION_FORBIDDEN: str = "ACTIVATION_FORBIDDEN"
    RC_MUTATION_FORBIDDEN: str = "MUTATION_FORBIDDEN"
    RC_GOVERNANCE_FORBIDDEN: str = "GOVERNANCE_FORBIDDEN"
    RC_DECISION_FORBIDDEN: str = "DECISION_FORBIDDEN"
    RC_METRICS_FORBIDDEN: str = "METRICS_FORBIDDEN"
    RC_INVOCATION_FORBIDDEN: str = "INVOCATION_FORBIDDEN"
    RC_CAPABILITY_PASSIVE: str = "CAPABILITY_PASSIVE"
    RC_UNKNOWN_SUBJECT: str = "UNKNOWN_SUBJECT"
    RC_UNKNOWN_ACTION: str = "UNKNOWN_ACTION"

    # ── Deterministic action -> reason_code mapping (a DATA table) ──
    _FORBIDDEN_REASONS: Dict[str, str] = {
        "produce": RC_PRODUCTION_FORBIDDEN,
        "activate": RC_ACTIVATION_FORBIDDEN,
        "mutate": RC_MUTATION_FORBIDDEN,
        "govern": RC_GOVERNANCE_FORBIDDEN,
        "decide": RC_DECISION_FORBIDDEN,
        "metrics": RC_METRICS_FORBIDDEN,
        "invoke": RC_INVOCATION_FORBIDDEN,
    }

    def evaluate_permission(
        self,
        subject: str,
        action: str,
        capability_id: str = "",
        invocation_id: str = "",
    ) -> PermissionEvaluationResult:
        """Evaluate one Runtime behavior request against the frozen matrix.

        Report-only: this returns a PermissionEvaluationResult observation.
        It NEVER blocks, rejects, stops, authorizes, grants, or acts. The
        block/allow decision authority belongs solely to Human (PE-L1).

        Args:
            subject:       The requesting actor ("human" / "runtime" / "capability").
            action:        The requested behavior (e.g. "produce", "activate").
            capability_id: Read-only reference to the target capability (optional).
            invocation_id: Read-only reference to the invocation context (optional).

        Returns:
            PermissionEvaluationResult (observation; COMPLIANT or NON_COMPLIANT).
        """
        subj = self._normalize(subject)
        act = self._normalize(action)

        subject_perms = self.PERMISSION_MATRIX.get(subj)
        if subject_perms is None:
            return self._result(
                subject=subj,
                action=act,
                capability_id=capability_id,
                invocation_id=invocation_id,
                verdict=PermissionVerdict.NON_COMPLIANT,
                reason_code=self.RC_UNKNOWN_SUBJECT,
            )

        allowed = subject_perms.get(act)
        if allowed is None:
            return self._result(
                subject=subj,
                action=act,
                capability_id=capability_id,
                invocation_id=invocation_id,
                verdict=PermissionVerdict.NON_COMPLIANT,
                reason_code=self.RC_UNKNOWN_ACTION,
            )

        if allowed:
            return self._result(
                subject=subj,
                action=act,
                capability_id=capability_id,
                invocation_id=invocation_id,
                verdict=PermissionVerdict.COMPLIANT,
                reason_code=self.RC_COMPLIANT,
            )

        # Forbidden — a pure observation, never an action.
        reason_code = self._forbidden_reason(subj, act)
        return self._result(
            subject=subj,
            action=act,
            capability_id=capability_id,
            invocation_id=invocation_id,
            verdict=PermissionVerdict.NON_COMPLIANT,
            reason_code=reason_code,
        )

    # ────────────────────────────────────────────────────────────────────
    # Private helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(value) -> str:
        """Normalize a subject/action to a lowercase key (factual, not a decision)."""
        if isinstance(value, str):
            return value.strip().lower()
        return ""

    def _forbidden_reason(self, subject: str, action: str) -> str:
        """Deterministic reason code for a forbidden (subject, action)."""
        if subject == "capability":
            # Capability is a pure passive unit — no active permission at all.
            return self.RC_CAPABILITY_PASSIVE
        return self._FORBIDDEN_REASONS.get(action, self.RC_UNKNOWN_ACTION)

    def _result(
        self,
        subject: str,
        action: str,
        capability_id: str,
        invocation_id: str,
        verdict: PermissionVerdict,
        reason_code: str,
    ) -> PermissionEvaluationResult:
        """Assemble a PermissionEvaluationResult observation."""
        evidence: Tuple[str, ...] = ()
        if verdict is PermissionVerdict.NON_COMPLIANT:
            evidence = (
                f"{self.EVALUATED_AGAINST}#{subject}#{action}",
            )

        return PermissionEvaluationResult(
            invocation_id=invocation_id,
            subject=subject,
            action=action,
            capability_id=capability_id,
            status=verdict,
            evaluated_against=self.EVALUATED_AGAINST,
            reason_code=reason_code,
            evidence_reference=evidence,
            parent=None,               # invariant I-1: never anything else
            production_execution=False,  # invariant I-5: never True
        )
