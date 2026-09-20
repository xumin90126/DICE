"""
Phase 6.1-L3: Capability Runtime — Shadow Capability Runtime Layer (INCREMENTAL).

This package hosts the L3 Capability Runtime Boundary modules. L3 Runtime is a
PASSIVE CARRIER LAYER — it hosts authorized invocations, loads capability
definitions read-only, reports permission evaluation results, and records
per-invocation traces. It NEVER decides, plans, routes, activates, governs,
measures, or connects to production.

Authorized implementation sequence (each component = Implementation -> Test ->
Boundary Review -> STOP):

    1. Context Holder      (context_holder.py)          <- COMPLETE (approved)
    2. Invocation Context  (invocation_context.py)      <- COMPLETE (approved)
    3. Permission Evaluation (permission_evaluation.py) <- COMPLETE (pending review)
    4. Capability Loader   (capability_loader.py)          <- COMPLETE (Step 2)
    5. Audit Trace         (audit_trace.py)                <- COMPLETE (Step 2)

Shadow guarantees (invariants):
    I-1  parent = None            (no self/cross/recursive invocation)
    I-2  shadow_marked = True     (all artifacts are observation artifacts)
    I-3  is_hypothetical = True   (observations are never applied)
    I-4  origin always marked
    I-5  production_execution = False (zero production connection)
    I-6  Registry = 21 (FROZEN, never modified here)
"""

__version__ = "6.1.0-l3"
__status__ = "L3_AUDIT_TRACE"  # five components implemented (Step 2)

# ── Component 1: Context Holder (authorized) ──
from .context_holder import RuntimeContextHolder

# ── Component 2: Invocation Context (authorized) ──
from .invocation_context import InvocationContextRecorder

# ── Component 3: Permission Evaluation (authorized) ──
from .permission_evaluation import PermissionEvaluator

# ── Component 4: Capability Loader (authorized, Step 2) ──
from .capability_loader import CapabilityLoader

# ── Component 5: Audit Trace (authorized, Step 2) ──
from .audit_trace import AuditTrace

__all__ = [
    "RuntimeContextHolder",
    "InvocationContextRecorder",
    "PermissionEvaluator",
    "CapabilityLoader",
    "AuditTrace",
]
