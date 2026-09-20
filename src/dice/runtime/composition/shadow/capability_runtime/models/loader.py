"""
Phase 6.1-L3: Capability Loader Data Models (Component 4).

Defines the passive carrier data structures produced by the Capability
Loader component. These are observation-only artifacts:

    LookupStatus          — FOUND / NOT_FOUND / INVALID_IDENTITY / UNAVAILABLE
                            (a factual lookup outcome, NOT a decision)
    CapabilityMetadata    — read-only descriptive metadata (name + references)
    CapabilityReference   — a read-only reference to a specified capability
    CapabilityLoadResult  — the observation result of load_capability()

This component is an EXACT LOOKUP PROVIDER (RED-LDR-004). It resolves a
given, explicitly-specified `capability_id` to a read-only reference. It
NEVER recommends, ranks, scores, selects, optimizes, falls back, routes,
activates, decides, or executes. The selection authority and execution
authority belong solely to Human.

Field whitelist (from Human Authorization, Component 4, LDR-L1~LDR-L5):
    ALLOWED   capability_id / capability_reference / lookup_status
              / evidence_reference / reason_code / metadata (read-only
              name + reference strings) / reference_kind
    FORBIDDEN decision / recommendation / ranking / score / confidence
              / priority / selection / fallback / route / activation
              / execution_plan / quality / suitability

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


class LookupStatus(Enum):
    """Outcome of a load_capability() lookup (a pure observation, not a decision).

    FOUND            — the specified capability identity resolved to a reference.
    NOT_FOUND        — the identity is well-formed but absent (CAPABILITY_NOT_FOUND).
    INVALID_IDENTITY — the identity is missing / malformed (INVALID_IDENTITY).
    UNAVAILABLE      — the identity is known but not loadable (CAPABILITY_UNAVAILABLE).

    NOTE: this status is NOT a selection, recommendation, or routing decision.
    It is a factual statement of the lookup outcome. What to do with it
    (retry, choose another, give up) is decided by Human, never by this
    component.
    """

    FOUND = "found"
    NOT_FOUND = "not_found"
    INVALID_IDENTITY = "invalid_identity"
    UNAVAILABLE = "unavailable"


@dataclass
class CapabilityMetadata:
    """Read-only descriptive metadata for a capability (P-2: Metadata Loading).

    Holds FACTS ONLY: a human-readable name and read-only references to the
    capability's boundary definition and interface contract documents. It
    NEVER contains score / ranking / confidence / suitability / priority /
    recommendation fields (LDR-L2, LDR-L4, IC-L4 no semantic expansion).

    Fields:
        name:                Read-only display name of the capability (fact)
        boundary_reference:  Read-only reference to the boundary definition
        contract_reference:  Read-only reference to the interface contract
    """

    name: str = ""
    boundary_reference: str = ""
    contract_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "boundary_reference": self.boundary_reference,
            "contract_reference": self.contract_reference,
        }

    def __repr__(self) -> str:
        return (
            f"CapabilityMetadata(name={self.name!r}, "
            f"boundary_reference={self.boundary_reference!r}, "
            f"contract_reference={self.contract_reference!r})"
        )


@dataclass
class CapabilityReference:
    """A read-only reference to a specified capability (P-3: Reference Resolution).

    This is the Output of the Capability Loader (Component 4). It is a
    READ-ONLY REFERENCE, NOT an execution handle: it holds the exact
    capability identity (echoed, never rewritten) plus read-only metadata.
    It NEVER performs an action and never grants an execution/activation
    handle (LDR-L3 Read-only Reference).

    Fields:
        reference_id:      Unique identity of this reference (uuid)
        capability_id:     The exact capability identity (echoed, not rewritten)
        metadata:          Read-only metadata (name + references), or None
        reference_kind:    Fixed marker "readonly_reference" (not an execution
                           handle, not an activation token)
        parent:            Always None (invariant I-1)
        shadow_marked:     Always True (invariant I-2)
        origin:            Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:   Always True (invariant I-3)
        production_execution: Always False (invariant I-5)
        resolved_at:       ISO-8601 timestamp of the resolution (fact)
    """

    # ── Identity ──
    reference_id: str = field(default_factory=lambda: str(uuid4()))
    capability_id: str = ""

    # ── Read-only payload ──
    metadata: Optional[CapabilityMetadata] = None

    # ── Fixed reference kind marker (read-only, never an execution handle) ──
    reference_kind: str = "readonly_reference"

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    resolved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "capability_id": self.capability_id,
            "metadata": self.metadata.to_dict() if self.metadata is not None else None,
            "reference_kind": self.reference_kind,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "resolved_at": self.resolved_at,
        }

    def __repr__(self) -> str:
        return (
            f"CapabilityReference(id={self.reference_id[:8]}..., "
            f"capability={self.capability_id!r}, "
            f"kind={self.reference_kind!r}, parent={self.parent}, "
            f"shadow_marked={self.shadow_marked})"
        )


@dataclass
class CapabilityLoadResult:
    """Observation result of a load_capability() attempt.

    Pure observation — reports the factual outcome of an exact identity
    lookup: FOUND (with a read-only reference) or a failure status
    (NOT_FOUND / INVALID_IDENTITY / UNAVAILABLE) with a factual reason code.
    It NEVER performs an action: no retry, no fallback, no alternative
    selection, no routing, no activation, no decision (LDR-L1~LDR-L5).

    Field whitelist (from Human Authorization, Component 4):
        capability_id           — the exact identity that was requested (echo)
        capability_reference    — read-only reference (present only when FOUND)
        lookup_status           — FOUND / NOT_FOUND / INVALID_IDENTITY / UNAVAILABLE
        evidence_reference      — read-only basis references (read-only)
        reason_code             — factual reason code (empty when FOUND)

    Fields:
        load_id:            Unique identity of this lookup (uuid)
        capability_id:      The exact capability identity requested (echo)
        lookup_status:      The factual lookup outcome (LookupStatus)
        capability_reference: Read-only reference (present only when FOUND)
        reason_code:        Factual reason code (empty string when FOUND)
        evidence_reference: Read-only basis references (frozen lookup table)
        parent:             Always None (invariant I-1)
        shadow_marked:      Always True (invariant I-2)
        origin:             Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:    Always True (invariant I-3)
        production_execution: Always False (invariant I-5)
        resolved_at:        ISO-8601 timestamp of the lookup (fact)
    """

    # ── Identity ──
    load_id: str = field(default_factory=lambda: str(uuid4()))

    # ── Factual payload (exact identity echo, not rewritten) ──
    capability_id: str = ""

    # ── Lookup outcome (observation, NOT decision) ──
    lookup_status: LookupStatus = LookupStatus.FOUND

    # ── Resolved reference (present only when FOUND) ──
    capability_reference: Optional[CapabilityReference] = None

    # ── Factual reason + read-only basis references ──
    reason_code: str = ""                # factual code; empty when FOUND
    evidence_reference: Tuple[str, ...] = ()  # read-only basis references

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    # ── Metadata ──
    resolved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def found(self) -> bool:
        """Convenience read: whether the lookup resolved to a reference."""
        return self.lookup_status == LookupStatus.FOUND

    def to_dict(self) -> Dict[str, Any]:
        return {
            "load_id": self.load_id,
            "capability_id": self.capability_id,
            "lookup_status": self.lookup_status.value,
            "capability_reference": (
                self.capability_reference.to_dict()
                if self.capability_reference is not None
                else None
            ),
            "reason_code": self.reason_code,
            "evidence_reference": list(self.evidence_reference),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "resolved_at": self.resolved_at,
        }

    def __repr__(self) -> str:
        return (
            f"CapabilityLoadResult(id={self.load_id[:8]}..., "
            f"capability={self.capability_id!r}, status={self.lookup_status.value}, "
            f"reason_code={self.reason_code!r}, shadow_marked={self.shadow_marked})"
        )
