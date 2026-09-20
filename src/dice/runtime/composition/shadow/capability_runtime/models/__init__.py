"""
Phase 6.1-L3: Capability Runtime Data Models — Context Holder + Invocation Context + Permission Evaluation + Capability Loader + Audit Trace.

All models carry shadow_marked=True, origin="composition_shadow_storage",
and is_hypothetical=True. No connection to Runtime Storage, Capability
Registry, or Production Database.

Modules:
    context:     HostedContext + HostContextResult (Component 1 — Context Holder)
    invocation:  InvocationContext + InvocationRecordResult (Component 2 — Invocation Context)
    permission:  PermissionVerdict + PermissionEvaluationResult (Component 3 — Permission Evaluation)
    loader:      LookupStatus + CapabilityMetadata + CapabilityReference + CapabilityLoadResult (Component 4 — Capability Loader)
    trace:       TraceStatus + TraceRecord + TraceRecordResult (Component 5 — Audit Trace)
"""

from .context import (
    HostedContext,
    HostContextResult,
    HostContextStatus,
)
from .invocation import (
    InvocationContext,
    InvocationRecordResult,
    InvocationRecordStatus,
)
from .permission import (
    PermissionVerdict,
    PermissionEvaluationResult,
)
from .loader import (
    LookupStatus,
    CapabilityMetadata,
    CapabilityReference,
    CapabilityLoadResult,
)
from .trace import (
    TraceStatus,
    TraceRecord,
    TraceRecordResult,
)

__all__ = [
    "HostedContext",
    "HostContextResult",
    "HostContextStatus",
    "InvocationContext",
    "InvocationRecordResult",
    "InvocationRecordStatus",
    "PermissionVerdict",
    "PermissionEvaluationResult",
    "LookupStatus",
    "CapabilityMetadata",
    "CapabilityReference",
    "CapabilityLoadResult",
    "TraceStatus",
    "TraceRecord",
    "TraceRecordResult",
]
