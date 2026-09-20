"""
Capability Registry — the authoritative source for all Capabilities.

Phase 4.0: Unified CRUD API managing Capability lifecycle independent
of the ExperienceGraph. The Registry owns Capability identity, the
graph is a derived view.

KEY DESIGN:
    - Registry is NOT a Rule store
    - Capabilities are registered with structured Identity/Strategy/Evidence/Evolution
    - No doc_class, product_id, or filename-based routing
    - Feedback Loop calls update_evidence() and update_health()

Architecture:
    Registry (authoritative)
        │
        ├── register() / get() / deprecate()
        ├── update_evidence() / update_health()    ← Feedback Loop
        ├── export_index()                         ← CLI / reporting
        │
        └── ExperienceGraph (derived view, synced via sync_to_graph())
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from dice.graph.nodes import (
    Capability, Pattern, Implementation, Rule,
    PatternStatus, CapabilityStatus, ConfidenceLevel,
)
from dice.graph.edges import Edge, EdgeType


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# Registry Result Types
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class RegistrationResult:
    """Result of a capability registration attempt."""
    success: bool
    capability_id: str
    action: str = ""                 # "created", "updated", "rejected"
    message: str = ""
    timestamp: str = field(default_factory=_now)


@dataclass
class EvidenceUpdate:
    """Evidence update payload from Feedback Loop."""
    document_id: str
    success: bool
    pattern_ids_triggered: list[str] = field(default_factory=list)
    new_evidence_ids: list[str] = field(default_factory=list)
    execution_confidence: float = 0.0
    notes: str = ""


@dataclass
class HealthSnapshot:
    """Capability health snapshot from Feedback Loop."""
    success_rate: float = 0.0
    recent_failures: int = 0
    pattern_activation_rate: dict[str, float] = field(default_factory=dict)
    confidence_trend: str = "stable"  # "improving", "stable", "degrading"
    enhancement_signals: list[str] = field(default_factory=list)


@dataclass
class RegistryIndex:
    """Lightweight export of all registered capabilities."""
    capabilities: list[dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    active_count: int = 0
    deprecated_count: int = 0
    generated_at: str = field(default_factory=_now)


# ═══════════════════════════════════════════════════════════════════════════
# CapabilityRegistry
# ═══════════════════════════════════════════════════════════════════════════


class CapabilityRegistry:
    """
    Authoritative Capability registry — manages the complete lifecycle.

    Storage: in-memory dict[str, Capability] with optional JSON persistence.
    Does NOT depend on ExperienceGraph. The graph is a downstream consumer.

    Usage:
        registry = CapabilityRegistry()
        result = registry.register(cap)
        cap = registry.get("CAP-COMP-TABLE")
        active = registry.list_active()
        registry.update_evidence("CAP-COMP-TABLE", evidence)
        registry.deprecate("CAP-OLD", "superseded by CAP-NEW")
    """

    def __init__(self, storage_path: Optional[str] = None):
        self._capabilities: dict[str, Capability] = {}
        self._implementations: dict[str, Implementation] = {}
        self._storage_path = storage_path
        self._registration_log: list[RegistrationResult] = []

    # ──────────────────────── CRUD ────────────────────────

    def register(self, capability: Capability) -> RegistrationResult:
        """
        Register a new or update an existing Capability.

        - New ID: creates capability
        - Existing ID + same version: updates metadata (non-destructive)
        - Existing ID + higher version: supersedes old version
        """
        existing = self._capabilities.get(capability.id)

        if existing is None:
            self._capabilities[capability.id] = capability
            result = RegistrationResult(
                success=True,
                capability_id=capability.id,
                action="created",
                message=f"Registered new capability '{capability.name}' v{capability.version}",
            )
        elif capability.version > existing.version:
            # Supersede: old version marked as previous
            capability.previous_version_id = existing.id
            capability.evolution_ids = list(set(
                existing.evolution_ids + capability.evolution_ids
            ))
            capability.evolution_history = (
                existing.evolution_history + capability.evolution_history
            )
            existing.status = CapabilityStatus.DEPRECATED
            existing.deprecated_at = _now()
            existing.deprecation_reason = f"Superseded by v{capability.version}"
            self._capabilities[capability.id] = capability
            result = RegistrationResult(
                success=True,
                capability_id=capability.id,
                action="superseded",
                message=(
                    f"Superseded '{capability.name}' v{existing.version} "
                    f"→ v{capability.version}"
                ),
            )
        else:
            # Same version: update metadata in place
            for field_name in [
                "description", "scope", "input_schema", "output_schema",
                "execution_strategy", "evidence_requirements",
                "pattern_ids", "implementation_ids",
                "source_evidence_ids", "source_pattern_ids",
                "positive_boundary", "negative_boundary",
                "activation_rule", "conflict_resolution",
                "exclusion_rules", "validation_criteria",
            ]:
                new_val = getattr(capability, field_name)
                if new_val:  # non-empty updates overwrite
                    setattr(existing, field_name, new_val)
            result = RegistrationResult(
                success=True,
                capability_id=capability.id,
                action="updated",
                message=f"Updated metadata for '{capability.name}' v{capability.version}",
            )

        self._registration_log.append(result)
        self._persist()
        return result

    def get(self, capability_id: str) -> Optional[Capability]:
        """Retrieve a capability by ID (including deprecated)."""
        return self._capabilities.get(capability_id)

    def list_all(self) -> list[Capability]:
        """List all capabilities (including deprecated)."""
        return list(self._capabilities.values())

    def list_active(self) -> list[Capability]:
        """List only active (non-deprecated, non-failed) capabilities."""
        return [c for c in self._capabilities.values() if c.is_active()]

    def find_by_pattern(self, pattern_id: str) -> list[Capability]:
        """Find all capabilities that support a given pattern."""
        return [
            c for c in self._capabilities.values()
            if pattern_id in c.pattern_ids and c.is_active()
        ]

    def register_implementation(self, impl: Implementation) -> None:
        """Register an Implementation (execution strategy) for a Capability."""
        self._implementations[impl.id] = impl
        # Auto-link to parent capability
        cap = self._capabilities.get(impl.capability_id)
        if cap and impl.id not in cap.implementation_ids:
            cap.implementation_ids.append(impl.id)

    def get_implementations(self, cap: Capability) -> list[Implementation]:
        """
        Get all registered Implementations for a Capability.

        Looks up by capability.implementation_ids first, then falls back
        to scanning all implementations for matching capability_id.
        """
        impls = []
        for impl_id in cap.implementation_ids:
            if impl_id in self._implementations:
                impls.append(self._implementations[impl_id])
        if not impls:
            # Fallback: scan all implementations
            for impl in self._implementations.values():
                if impl.capability_id == cap.id:
                    impls.append(impl)
        return impls

    def deprecate(self, capability_id: str, reason: str = "") -> RegistrationResult:
        """Mark a capability as deprecated."""
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return RegistrationResult(
                success=False,
                capability_id=capability_id,
                action="rejected",
                message=f"Capability '{capability_id}' not found",
            )
        cap.deprecate(reason)
        result = RegistrationResult(
            success=True,
            capability_id=capability_id,
            action="deprecated",
            message=f"Deprecated '{cap.name}': {reason}" if reason else f"Deprecated '{cap.name}'",
        )
        self._registration_log.append(result)
        self._persist()
        return result

    # ──────────────────────── Evidence Consumption (Phase 4.3) ────────────────────────
    #
    #  Architecture:
    #     ExperienceGraph.write() → Evidence.produce() → EvidenceView
    #                                                          │
    #     Registry.consume_evidence(view) ◄────────────────────┘
    #
    #  Registry reads EvidenceView — NEVER directly called by ExperienceGraph.

    def consume_evidence(self, evidence_view: Any) -> dict[str, RegistrationResult]:
        """
        Consume evidence from EvidenceView and update capability stats.

        This is the MAIN entry point for feedback → Registry.
        Called AFTER FeedbackLoop.process() by the orchestrator.

        Registry reads from EvidenceView (derived view of Evidence nodes),
        never directly from ExecutionExperiences or the ExperienceGraph.

        For each capability with new evidence:
        1. Count success/failure from evidence
        2. Update execution stats
        3. Check for health signals
        4. Record enhancement observations

        Returns dict[capability_id → RegistrationResult].
        """
        from dice.evidence import EvidenceType
        results: dict[str, RegistrationResult] = {}

        # Collect all capability IDs that have evidence
        capability_ids: set[str] = set()
        for etype in [EvidenceType.EXECUTION_SUCCESS, EvidenceType.EXECUTION_FAILURE]:
            for evd in evidence_view.by_type(etype):
                if evd.capability_id:
                    capability_ids.add(evd.capability_id)

        for cid in capability_ids:
            cap = self._capabilities.get(cid)
            if cap is None:
                results[cid] = RegistrationResult(
                    success=False,
                    capability_id=cid,
                    action="rejected",
                    message=f"Capability '{cid}' not found in Registry",
                )
                continue

            # Read success/failure from evidence
            success_count, total, success_rate = evidence_view.success_rate(cid)

            # Update execution stats (batch)
            if total > 0:
                # Record each execution from evidence
                for evd in evidence_view.by_type(EvidenceType.EXECUTION_SUCCESS, cid):
                    cap.record_execution(True, evd.document_id)
                for evd in evidence_view.by_type(EvidenceType.EXECUTION_FAILURE, cid):
                    cap.record_execution(False, evd.document_id)

                # Collect evidence IDs for traceability
                for evd in evidence_view.by_capability(cid):
                    if evd.id not in cap.source_evidence_ids:
                        cap.source_evidence_ids.append(evd.id)

            # Check for critical signals (observation only, not auto-action)
            critical_failures = evidence_view.by_type(EvidenceType.EXECUTION_FAILURE, cid)
            if len(critical_failures) >= 5 and success_rate < 0.3:
                if "persistent_low_success_rate" not in cap.enhancement_signals:
                    cap.enhancement_signals.append("persistent_low_success_rate")

            results[cid] = RegistrationResult(
                success=True,
                capability_id=cid,
                action="evidence_consumed",
                message=(
                    f"Consumed evidence for '{cap.name}': "
                    f"execution_count={cap.execution_count}, "
                    f"success_rate={cap.cross_doc_success_rate:.2f}"
                ),
            )

        self._persist()
        return results

    # ──────────────────────── Legacy Hooks (deprecated, kept for backward compat) ─────
    #
    #  These are NO LONGER called by ExperienceGraph directly.
    #  Use consume_evidence(evidence_view) instead.

    def update_evidence(
        self, capability_id: str, update: EvidenceUpdate
    ) -> RegistrationResult:
        """
        [DEPRECATED] Legacy hook — use consume_evidence() with EvidenceView instead.

        Kept for backward compatibility with pre-Phase-4.3 code paths.
        Will be removed once all callers migrate to consume_evidence().
        """
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return RegistrationResult(
                success=False,
                capability_id=capability_id,
                action="rejected",
                message=f"Capability '{capability_id}' not found",
            )

        cap.record_execution(update.success, update.document_id)

        for evd_id in update.new_evidence_ids:
            if evd_id not in cap.source_evidence_ids:
                cap.source_evidence_ids.append(evd_id)

        self._persist()
        return RegistrationResult(
            success=True,
            capability_id=capability_id,
            action="evidence_updated",
            message=(
                f"Updated evidence for '{cap.name}': "
                f"execution_count={cap.execution_count}, "
                f"success_rate={cap.cross_doc_success_rate:.2f}"
            ),
        )

    def update_health(
        self, capability_id: str, health: HealthSnapshot
    ) -> RegistrationResult:
        """
        [DEPRECATED] Legacy hook — health signals now derived from EvidenceView.

        Kept for backward compatibility. Enhancement signals are now
        managed through consume_evidence().
        """
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return RegistrationResult(
                success=False,
                capability_id=capability_id,
                action="rejected",
                message=f"Capability '{capability_id}' not found",
            )

        for sig in health.enhancement_signals:
            if sig not in cap.enhancement_signals:
                cap.enhancement_signals.append(sig)

        self._persist()
        return RegistrationResult(
            success=True,
            capability_id=capability_id,
            action="health_updated",
            message=(
                f"Health updated for '{cap.name}': "
                f"trend={health.confidence_trend}, "
                f"enhancement_signals={health.enhancement_signals}"
            ),
        )

    # ──────────────────────── Export ────────────────────────

    def export_index(self) -> RegistryIndex:
        """Export a lightweight index of all capabilities."""
        caps_data = [c.to_dict() for c in self._capabilities.values()]
        return RegistryIndex(
            capabilities=caps_data,
            total_count=len(caps_data),
            active_count=len(self.list_active()),
            deprecated_count=len(caps_data) - len(self.list_active()),
        )

    # ──────────────────────── Persistence ────────────────────────

    def _persist(self) -> None:
        """Persist registry state to JSON if storage_path is configured."""
        if not self._storage_path:
            return
        os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
        data = {
            "capabilities": {
                cid: _capability_to_serializable(cap)
                for cid, cap in self._capabilities.items()
            },
            "updated_at": _now(),
        }
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> int:
        """Load registry state from storage_path. Returns count of loaded capabilities."""
        if not self._storage_path or not os.path.exists(self._storage_path):
            return 0
        with open(self._storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for cid, cdata in data.get("capabilities", {}).items():
            cap = _capability_from_serializable(cdata)
            self._capabilities[cid] = cap
            count += 1
        return count

    def __len__(self) -> int:
        return len(self._capabilities)

    def __contains__(self, capability_id: str) -> bool:
        return capability_id in self._capabilities


# ═══════════════════════════════════════════════════════════════════════════
# Serialization Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _capability_to_serializable(cap: Capability) -> dict[str, Any]:
    """Convert Capability to a JSON-serializable dict."""
    d = asdict(cap)
    # Convert enum values
    d["status"] = cap.status.value
    d["maturity"] = cap.maturity.value
    return d


def _capability_from_serializable(data: dict[str, Any]) -> Capability:
    """Reconstruct Capability from a serialized dict."""
    # Restore enums
    data["status"] = CapabilityStatus(data.get("status", "proposed"))
    data["maturity"] = ConfidenceLevel(data.get("maturity", "low"))
    return Capability(**data)
