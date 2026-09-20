"""
Evidence Layer — the bridge between Experience and Registry.

Phase 4.3 Architecture:
    ExecutionExperience
            │
            ▼
    ExperienceGraph.write()      ← write/persist/route ONLY
            │
            ▼
    Evidence.produce()           ← Experience → Evidence transformation
            │
            ▼
    EvidenceView                 ← Registry reads from this
            │
            ▼
    CapabilityRegistry.consume_evidence()  ← updates stats

CRITICAL DESIGN:
    1. Evidence is produced FROM experience, not injected INTO Registry
    2. Registry reads EvidenceView — a read-only derived view
    3. Evidence is immutable: created, stored, never modified
    4. Evidence nodes are the BRIDGE — Registry never touches raw experiences
    5. No direct ExperienceGraph → Registry coupling
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# NOTE: ExecutionExperience is imported LAZILY inside Evidence.from_experience()
# to avoid circular import: evidence → execution_models → runtime.__init__
# → experience.__init__ → feedback_loop → evidence.
# With `from __future__ import annotations`, the type annotation in the
# classmethod signature is already a string and doesn't trigger the import.


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Evidence Types
# ═══════════════════════════════════════════════════════════════════════════


class EvidenceType:
    """Evidence type constants — what KIND of evidence was observed."""

    EXECUTION_SUCCESS = "execution_success"
    EXECUTION_FAILURE = "execution_failure"
    PATTERN_MATCH = "pattern_match"
    PATTERN_MISMATCH = "pattern_mismatch"
    COMPONENT_EXTRACTED = "component_extracted"
    COMPONENT_MISSING = "component_missing"
    CONFIDENCE_CHANGE = "confidence_change"
    STRATEGY_USED = "strategy_used"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"

    # Source signature: which pipeline produced this evidence
    SOURCE_SIGNATURES = {
        EXECUTION_SUCCESS: "capability_executor",
        EXECUTION_FAILURE: "capability_executor",
        PATTERN_MATCH: "ranking_model",
        PATTERN_MISMATCH: "ranking_model",
        COMPONENT_EXTRACTED: "capability_executor",
        COMPONENT_MISSING: "capability_executor",
        CONFIDENCE_CHANGE: "capability_executor",
        STRATEGY_USED: "capability_executor",
        VALIDATION_PASSED: "validation_gate",
        VALIDATION_FAILED: "validation_gate",
    }


# ═══════════════════════════════════════════════════════════════════════════
# Evidence
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class Evidence:
    """
    A single piece of evidence derived from an execution experience.

    Evidence is IMMUTABLE. Once produced, it describes what happened —
    it does not prescribe what should change.

    Evidence is the UNIT of communication between ExperienceGraph and Registry.
    Registry reads EvidenceView (a collection of Evidence nodes) and updates
    its internal stats. Registry NEVER directly accesses ExecutionExperiences.
    """

    id: str = ""
    # ── What ──
    evidence_type: str = ""        # one of EvidenceType constants
    capability_id: str = ""
    description: str = ""          # human-readable description of what was observed

    # ── Source (traceability to the experience that produced this) ──
    experience_id: str = ""        # links back to ExecutionExperience.id
    source_signature: str = ""     # which pipeline/handler produced this

    # ── Content ──
    payload: dict[str, Any] = field(default_factory=dict)
    # Evidence-type-specific payload:
    #   EXECUTION_SUCCESS: {"confidence": 0.85, "execution_time_ms": 123}
    #   EXECUTION_FAILURE: {"failure_reason": "...", "failure_count": 5}
    #   PATTERN_MATCH: {"pattern_id": "PAT-X", "score": 0.9}
    #   COMPONENT_EXTRACTED: {"component_name": "...", "quantity": "...", "unit": "..."}

    # ── Metadata ──
    confidence: float = 0.0        # how confident is this evidence? (0-1)
    document_id: str = ""
    slice_id: str = ""
    produced_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.id:
            self.id = _uid("EVD-")
        if not self.source_signature and self.evidence_type:
            self.source_signature = EvidenceType.SOURCE_SIGNATURES.get(
                self.evidence_type, "unknown"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "evidence_type": self.evidence_type,
            "capability_id": self.capability_id,
            "description": self.description,
            "experience_id": self.experience_id,
            "source_signature": self.source_signature,
            "payload": self.payload,
            "confidence": round(self.confidence, 4),
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "produced_at": self.produced_at,
        }

    @classmethod
    def from_experience(
        cls, experience: "ExecutionExperience"
    ) -> list["Evidence"]:
        """
        Produce Evidence nodes from a single ExecutionExperience.

        One experience can generate MULTIPLE evidence nodes:
        - success → EXECUTION_SUCCESS evidence
        - failure → EXECUTION_FAILURE evidence
        - matched patterns → PATTERN_MATCH evidence (one per pattern)
        - extracted components → COMPONENT_EXTRACTED evidence (one per component)
        - confidence change → CONFIDENCE_CHANGE evidence
        - strategy used → STRATEGY_USED evidence

        This is the CORE transformation: Experience → Evidence.
        The caller (ExperienceGraph) is responsible for persistence and routing.
        """
        from dice.runtime.experience.execution_models import ExecutionExperience  # noqa: F811 — lazy import to break circular dep
        evidence_nodes: list[Evidence] = []

        # ── Core: success/failure ──
        if experience.success:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.EXECUTION_SUCCESS,
                capability_id=experience.capability_id,
                description=(
                    f"Capability '{experience.capability_name}' executed successfully "
                    f"on {experience.document_id}/{experience.slice_id}"
                ),
                experience_id=experience.id,
                payload={
                    "confidence": experience.confidence_after,
                    "execution_time_ms": experience.execution_time_ms,
                    "strategy": experience.execution_strategy_used,
                },
                confidence=experience.confidence_after,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))
        else:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.EXECUTION_FAILURE,
                capability_id=experience.capability_id,
                description=(
                    f"Capability '{experience.capability_name}' failed "
                    f"on {experience.document_id}/{experience.slice_id}: "
                    f"{experience.failure_reason[:200]}"
                ),
                experience_id=experience.id,
                payload={
                    "failure_reason": experience.failure_reason,
                    "confidence": experience.confidence_after,
                    "strategy": experience.execution_strategy_used,
                },
                confidence=0.0,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        # ── Pattern matches ──
        matched_patterns = experience.input_evidence.get("matched_patterns", [])
        for pid in matched_patterns:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.PATTERN_MATCH,
                capability_id=experience.capability_id,
                description=f"Pattern '{pid}' matched in {experience.document_id}/{experience.slice_id}",
                experience_id=experience.id,
                payload={
                    "pattern_id": pid,
                    "match_score": experience.input_evidence.get("match_score", 0.0),
                },
                confidence=experience.input_evidence.get("match_score", 0.5),
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        # ── Strategy used ──
        if experience.execution_strategy_used:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.STRATEGY_USED,
                capability_id=experience.capability_id,
                description=(
                    f"Strategy '{experience.execution_strategy_used}' used "
                    f"for {experience.capability_name}"
                ),
                experience_id=experience.id,
                payload={"strategy": experience.execution_strategy_used},
                confidence=0.9,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        # ── Confidence change ──
        if abs(experience.confidence_delta) > 0.01:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.CONFIDENCE_CHANGE,
                capability_id=experience.capability_id,
                description=(
                    f"Confidence changed {experience.confidence_delta:+.4f} "
                    f"({experience.confidence_before:.4f} → {experience.confidence_after:.4f})"
                ),
                experience_id=experience.id,
                payload={
                    "confidence_before": experience.confidence_before,
                    "confidence_after": experience.confidence_after,
                    "delta": experience.confidence_delta,
                },
                confidence=0.95,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        # ── Validation results ──
        validation = experience.validation
        if validation.get("gates_passed", 0) == validation.get("total_gates", 0):
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.VALIDATION_PASSED,
                capability_id=experience.capability_id,
                description=(
                    f"All {validation.get('total_gates', 0)} validation gates passed"
                ),
                experience_id=experience.id,
                payload=validation,
                confidence=0.85,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))
        elif validation.get("total_gates", 0) > 0:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.VALIDATION_FAILED,
                capability_id=experience.capability_id,
                description=(
                    f"{validation.get('gates_passed', 0)}/{validation.get('total_gates', 0)} "
                    f"validation gates passed"
                ),
                experience_id=experience.id,
                payload=validation,
                confidence=0.5,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        # ── Component extraction results ──
        result_summary = experience.result_summary
        components_count = result_summary.get("components_extracted", 0)
        missing_count = result_summary.get("missing_count", 0)
        if components_count > 0:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.COMPONENT_EXTRACTED,
                capability_id=experience.capability_id,
                description=(
                    f"Extracted {components_count} components "
                    f"(missing: {missing_count}, coverage: {result_summary.get('coverage_ratio', 0):.1%})"
                ),
                experience_id=experience.id,
                payload={
                    "components_extracted": components_count,
                    "missing_count": missing_count,
                    "coverage_ratio": result_summary.get("coverage_ratio", 0),
                },
                confidence=result_summary.get("confidence", 0.5),
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))
        elif missing_count > 0:
            evidence_nodes.append(Evidence(
                evidence_type=EvidenceType.COMPONENT_MISSING,
                capability_id=experience.capability_id,
                description=f"{missing_count} components not found in {experience.document_id}/{experience.slice_id}",
                experience_id=experience.id,
                payload={"missing_count": missing_count},
                confidence=0.3,
                document_id=experience.document_id,
                slice_id=experience.slice_id,
            ))

        return evidence_nodes


# ═══════════════════════════════════════════════════════════════════════════
# EvidenceView
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvidenceView:
    """
    Read-only derived view of accumulated Evidence.

    Registry reads from this — never directly from experiences.
    Provides filtered, aggregated views of evidence organized by:
        - capability_id
        - evidence_type
        - recency

    Usage:
        view = EvidenceView()
        view.add(evidence_nodes)
        success_evidences = view.by_capability("CAP-COMP-TABLE")
        failures = view.by_type(EvidenceType.EXECUTION_FAILURE)
    """

    # capability_id → list[Evidence]
    _by_capability: dict[str, list[Evidence]] = field(default_factory=dict)

    # evidence_type → list[Evidence]
    _by_type: dict[str, list[Evidence]] = field(default_factory=dict)

    # Flat list for iteration
    _all: list[Evidence] = field(default_factory=list)

    def add(self, evidence_nodes: list[Evidence]) -> None:
        """Add evidence nodes to the view."""
        for evd in evidence_nodes:
            self._all.append(evd)

            cid = evd.capability_id
            if cid not in self._by_capability:
                self._by_capability[cid] = []
            self._by_capability[cid].append(evd)

            etype = evd.evidence_type
            if etype not in self._by_type:
                self._by_type[etype] = []
            self._by_type[etype].append(evd)

    def by_capability(self, capability_id: str) -> list[Evidence]:
        """Get all evidence for a capability."""
        return list(self._by_capability.get(capability_id, []))

    def by_type(
        self, evidence_type: str, capability_id: str = ""
    ) -> list[Evidence]:
        """Get evidence of a specific type, optionally filtered by capability."""
        nodes = self._by_type.get(evidence_type, [])
        if capability_id:
            nodes = [n for n in nodes if n.capability_id == capability_id]
        return list(nodes)

    def recent(self, capability_id: str = "", limit: int = 50) -> list[Evidence]:
        """Get most recent evidence, optionally filtered by capability."""
        nodes = (
            self.by_capability(capability_id)
            if capability_id else list(self._all)
        )
        return sorted(nodes, key=lambda e: e.produced_at, reverse=True)[:limit]

    def counts(self, capability_id: str = "") -> dict[str, int]:
        """Count evidence by type, optionally filtered by capability."""
        result: dict[str, int] = {}
        for etype, nodes in self._by_type.items():
            if capability_id:
                count = sum(1 for n in nodes if n.capability_id == capability_id)
            else:
                count = len(nodes)
            if count > 0:
                result[etype] = count
        return result

    def success_rate(self, capability_id: str) -> tuple[int, int, float]:
        """(success_count, total_count, success_rate) for a capability."""
        success = len(self.by_type(EvidenceType.EXECUTION_SUCCESS, capability_id))
        failure = len(self.by_type(EvidenceType.EXECUTION_FAILURE, capability_id))
        total = success + failure
        rate = success / total if total > 0 else 0.0
        return success, total, rate

    def total(self) -> int:
        """Total evidence nodes in view."""
        return len(self._all)

    def clear(self) -> None:
        """Clear all evidence."""
        self._by_capability.clear()
        self._by_type.clear()
        self._all.clear()


# ═══════════════════════════════════════════════════════════════════════════
# EvidenceStore (persistence)
# ═══════════════════════════════════════════════════════════════════════════


class EvidenceStore:
    """
    File-based persistence for Evidence nodes.

    Appends JSON lines to per-capability evidence logs.
    Independent from ExperienceGraph persistence — Evidence has its own store.

    Storage layout:
        dice_output/evidence/
        └── {capability_id}/
            └── evidence.jsonl
    """

    def __init__(self, storage_dir: str = "dice_output/evidence"):
        self._storage_dir = storage_dir
        os.makedirs(self._storage_dir, exist_ok=True)

    def persist(self, evidence_nodes: list[Evidence]) -> int:
        """Persist evidence nodes to storage. Returns count persisted."""
        count = 0
        for evd in evidence_nodes:
            if not evd.capability_id:
                continue
            cap_dir = os.path.join(
                self._storage_dir,
                evd.capability_id.replace("/", "_"),
            )
            os.makedirs(cap_dir, exist_ok=True)
            filepath = os.path.join(cap_dir, "evidence.jsonl")
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(evd.to_dict(), ensure_ascii=False) + "\n")
            count += 1
        return count

    def load(
        self,
        capability_id: str = "",
        limit: int = 1000,
    ) -> list[Evidence]:
        """Load evidence from storage. Optionally filtered by capability."""
        evidence_nodes: list[Evidence] = []

        if capability_id:
            cap_dir = os.path.join(
                self._storage_dir,
                capability_id.replace("/", "_"),
            )
            filepath = os.path.join(cap_dir, "evidence.jsonl")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if limit and len(evidence_nodes) >= limit:
                            break
                        try:
                            data = json.loads(line.strip())
                            evidence_nodes.append(Evidence(**data))
                        except (json.JSONDecodeError, TypeError):
                            continue
        else:
            # Scan all capability directories
            if os.path.exists(self._storage_dir):
                for entry in os.listdir(self._storage_dir):
                    cap_dir = os.path.join(self._storage_dir, entry)
                    filepath = os.path.join(cap_dir, "evidence.jsonl")
                    if os.path.exists(filepath):
                        with open(filepath, "r", encoding="utf-8") as f:
                            for line in f:
                                if limit and len(evidence_nodes) >= limit:
                                    break
                                try:
                                    data = json.loads(line.strip())
                                    evidence_nodes.append(Evidence(**data))
                                except (json.JSONDecodeError, TypeError):
                                    continue

        return evidence_nodes
