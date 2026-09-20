"""
Phase 16.11: CapabilityCandidateObservation — draft container type contract.

CAND-002 (datasheet EXTEND) — Human Validation → Capability Formation bridge,
layer 1 (the memory foundation).

This module introduces ONLY the type/schema contract for a Capability
Candidate observation. It is a DRAFT container: a placeholder that future
formation phases MAY populate via deterministic, Human-gated aggregation of
Validation Memory.

CRITICAL BOUNDARY (Phase 16.11 Scope, §4):
    - SCHEMA/TYPE CONTRACT ONLY. This phase implements NO automatic filling,
      NO automatic aggregation of ValidationRecord, NO automatic candidate
      generation, NO automatic capability registration.
    - `status` is ALWAYS "draft". There is NO code path that writes
      "registered" / "active" / "approved" / "promoted". The object is a
      draft container BY CONSTRUCTION — it can never enter the Registry.
    - ZERO authority: no capability_id-selection logic, no priority, no
      score, no recommendation, no ranking, no routing, no execution.

FORBIDDEN fields (never present by construction):
    decision / recommendation / ranking / score / confidence / priority /
    selection / routing / fallback / activation / execution_plan /
    selected_capability / capability_id-selection logic

Invariants (I-1 ~ I-5) enforced by construction.

The formation-threshold observation fields (document_count / accept_count /
reject_count / reason_distribution / eqs_threshold_met) are FACTS that a
FUTURE deterministic aggregation step MAY record. In THIS phase they remain
default/empty — nothing populates them. They exist so the draft container's
contract is ready, WITHOUT introducing any aggregation logic now.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# The ONLY legal status. A CapabilityCandidateObservation is a draft container
# by construction; there is no promotion path within this module.
DRAFT_STATUS = "draft"


@dataclass
class CapabilityCandidateObservation:
    """A draft container for a (future) Capability Candidate observation.

    This is a SCHEMA/TYPE CONTRACT ONLY. It records, as OBSERVATION FACTS, the
    recurring semantics and formation-threshold counts that a FUTURE
    deterministic aggregation step may fill. It is FORBIDDEN from carrying any
    decision/selection/routing/execution authority, and its `status` is
    ALWAYS "draft".

    Fields:
        candidate_id        : candidate identity (fact; future-assigned)
        span_type           : observed recurring span_type (fact)
        attribute_pattern   : observed recurring attribute/pattern (fact)
        document_count      : F-1 cross-document count (observation fact)
        accept_count        : F-2 ACCEPT count (observation fact)
        reject_count        : negative-sample count (observation fact)
        reason_distribution : reason → count distribution (observation fact)
        eqs_threshold_met   : F-4 EQS threshold reached (observation fact,
                              NOT a decision)
        status              : ALWAYS "draft" (never registered/active/approved)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution: invariant fields (I-1 ~ I-5)
        observed_at         : ISO-8601 timestamp (fact)
    """

    # ── identity ──
    candidate_id: str = ""

    # ── observed recurring semantics (facts; draft container contract only) ──
    span_type: str = ""
    attribute_pattern: str = ""

    # ── formation-threshold observations (F-1 ~ F-4 facts, zero decision) ──
    document_count: int = 0
    accept_count: int = 0
    reject_count: int = 0
    reason_distribution: Dict[str, int] = field(default_factory=dict)
    eqs_threshold_met: bool = False      # observation fact, NOT a decision

    # ── draft status ──
    status: str = DRAFT_STATUS           # ALWAYS "draft" — never promoted here

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None         # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False   # invariant I-5: never True

    # ── Metadata ──
    observed_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "span_type": self.span_type,
            "attribute_pattern": self.attribute_pattern,
            "document_count": self.document_count,
            "accept_count": self.accept_count,
            "reject_count": self.reject_count,
            "reason_distribution": dict(self.reason_distribution),
            "eqs_threshold_met": self.eqs_threshold_met,
            "status": self.status,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "observed_at": self.observed_at,
        }


__all__ = [
    "CapabilityCandidateObservation",
    "DRAFT_STATUS",
]
