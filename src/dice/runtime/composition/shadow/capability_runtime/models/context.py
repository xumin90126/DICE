"""
Phase 6.1-L3: Context Holder Data Models.

Defines the passive carrier data structures produced by the Runtime Context
Holder (Component 1). These are observation-only artifacts:

    HostedContext      — an isolated hosting context for one authorized call
    HostContextResult  — the observation result of a host_context() attempt

Invariants enforced by construction:
    parent is always None      (I-1: no recursive/self/cross invocation)
    shadow_marked always True  (I-2)
    is_hypothetical always True(I-3)
    origin always "composition_shadow_storage" (I-4)

These models are PURE PASSIVE CARRIERS — they hold facts only. They contain
no decision, no routing, no scheduling, no retry, no fallback, no priority
fields (the "strategic fields" forbidden by the Context Holder contract).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class HostContextStatus(Enum):
    """Outcome of a host_context() attempt (observation, not action)."""

    HOSTED = "hosted"          # context hosted successfully
    REJECTED = "rejected"      # unauthorized/invalid → not hosted (report only)


@dataclass
class HostedContext:
    """An isolated hosting context for exactly one authorized invocation.

    This is the Output of the Runtime Context Holder. It holds FACTS ONLY:
    which capability identity was requested, which input is referenced
    (by ID, read-only), and the invocation identifier. There is no decision,
    no order, no retry, no fallback, no priority anywhere in this structure.

    Fields:
        invocation_id:     Human-issued invocation identifier
        capability_id:     The exact capability identity Human selected
        input_reference:   Read-only reference to the input (ID / document id)
        input_ref_type:    The kind of reference (observation / simulation / etc.)
        parent:            Always None (invariant I-1)
        shadow_marked:     Always True (invariant I-2)
        origin:            Always "composition_shadow_storage" (invariant I-4)
        is_hypothetical:   Always True (invariant I-3)
    """

    # ── Identity ──
    context_id: str = field(default_factory=lambda: str(uuid4()))
    invocation_id: str = ""

    # ── Factual payload (read-only references, no live pointers) ──
    capability_id: str = ""
    input_reference: str = ""
    input_ref_type: str = ""

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    shadow_version: str = "1.0"

    # ── Metadata ──
    hosted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "invocation_id": self.invocation_id,
            "capability_id": self.capability_id,
            "input_reference": self.input_reference,
            "input_ref_type": self.input_ref_type,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "shadow_version": self.shadow_version,
            "hosted_at": self.hosted_at,
        }

    def __repr__(self) -> str:
        return (
            f"HostedContext(id={self.context_id[:8]}..., "
            f"capability={self.capability_id!r}, "
            f"parent={self.parent}, shadow_marked={self.shadow_marked})"
        )


@dataclass
class HostContextResult:
    """Observation result of a host_context() attempt.

    Pure observation — reports whether the context was hosted, and carries
    a read-only reason when rejected. It NEVER performs an action: no block,
    no retry, no fallback, no routing (E1/E2/E3 error contract principles).
    """

    # ── Outcome ──
    status: HostContextStatus = HostContextStatus.HOSTED

    # ── Produced context (present only when HOSTED) ──
    context: Optional[HostedContext] = None

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
    def hosted(self) -> bool:
        """Convenience read: whether the context was hosted."""
        return self.status == HostContextStatus.HOSTED

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
            f"HostContextResult(status={self.status.value}, "
            f"hosted={self.hosted}, shadow_marked={self.shadow_marked})"
        )
