"""
Phase 6.1-L3: Permission Evaluation Data Models (Component 3).

Defines the passive carrier data structures produced by the Permission
Evaluation component. These are observation-only artifacts:

    PermissionVerdict           — COMPLIANT / NON_COMPLIANT (observation)
    PermissionEvaluationResult  — the evaluation result (factual, no action)

This component is an OBSERVATION CONTRACT PROVIDER (RED-GRD-003). It reports
a permission verdict only; it NEVER blocks, rejects, stops, authorizes,
grants, or acts. The block/allow decision authority belongs solely to Human.

Field whitelist (from Human Authorization, Component 3):
    ALLOWED   status / subject / action / capability_id / evaluated_against
              / reason_code / evidence_reference
    FORBIDDEN decision / approval / rejection_action / block_action / retry
              / fallback / recommendation / priority / score / confidence
              / policy_generation

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
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


class PermissionVerdict(Enum):
    """Permission evaluation outcome (a pure observation, not an action).

    COMPLIANT     — the (subject, action) is permitted by the frozen matrix.
    NON_COMPLIANT — the (subject, action) hits a forbidden path in the matrix.

    NOTE: this verdict is NOT a block/reject/stop action. It is a factual
    statement of compliance. What to do with it (block, allow, escalate) is
    decided by Human, never by this component.
    """

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"


@dataclass
class PermissionEvaluationResult:
    """Observation result of an evaluate_permission() evaluation.

    This is the Output of the Permission Evaluation component (Component 3).
    It holds FACTS ONLY: which subject requested which action against which
    capability, what the frozen permission matrix says (COMPLIANT /
    NON_COMPLIANT), and read-only basis references. It NEVER performs an
    action: no block, no reject, no stop, no retry, no fallback, no routing,
    no authorization, no grant (PE-L1 ~ PE-L5).

    Fields:
        evaluation_id:      Unique identity of this evaluation (uuid)
        invocation_id:      Read-only reference to the invocation context
        subject:            The requesting actor (e.g. "runtime")
        action:             The requested behavior (e.g. "produce")
        capability_id:      The target capability identity (read-only)
        status:             COMPLIANT / NON_COMPLIANT (the verdict)
        evaluated_against:  Reference to the frozen permission matrix used
        reason_code:        Factual reason code (empty string when compliant)
        evidence_reference: Read-only basis references (matrix entries / contract)
        parent:             Always None (invariant I-1)
        shadow_marked:      Always True (invariant I-2)
        origin:             Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:    Always True (invariant I-3)
        production_execution: Always False (invariant I-5)
        evaluated_at:       ISO-8601 timestamp of the evaluation (fact)
    """

    # ── Identity ──
    evaluation_id: str = field(default_factory=lambda: str(uuid4()))
    invocation_id: str = ""

    # ── Factual payload (read-only facts of the evaluated request) ──
    subject: str = ""
    action: str = ""
    capability_id: str = ""

    # ── Verdict (observation, NOT action) ──
    status: PermissionVerdict = PermissionVerdict.COMPLIANT

    # ── Evaluation basis (read-only references) ──
    evaluated_against: str = ""          # e.g. "permission_matrix_v1"
    reason_code: str = ""                # factual code; empty when COMPLIANT
    evidence_reference: Tuple[str, ...] = ()  # read-only basis references

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def compliant(self) -> bool:
        """Convenience read: whether the request is COMPLIANT."""
        return self.status == PermissionVerdict.COMPLIANT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "invocation_id": self.invocation_id,
            "subject": self.subject,
            "action": self.action,
            "capability_id": self.capability_id,
            "status": self.status.value,
            "evaluated_against": self.evaluated_against,
            "reason_code": self.reason_code,
            "evidence_reference": list(self.evidence_reference),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "evaluated_at": self.evaluated_at,
        }

    def __repr__(self) -> str:
        return (
            f"PermissionEvaluationResult(id={self.evaluation_id[:8]}..., "
            f"subject={self.subject!r}, action={self.action!r}, "
            f"capability={self.capability_id!r}, status={self.status.value}, "
            f"reason_code={self.reason_code!r}, shadow_marked={self.shadow_marked})"
        )
