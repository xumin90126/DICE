"""
Phase 6.1-L2.2: EvidenceCollector — Logic (Phase B implemented).

Read-only evidence collection from L2.1 shadow artifacts. Consumes
L2.1 Evidence Snapshot (read-only copy) + Trace/Result references and
produces ValidationEvidence (read-only copies, shadow_marked=True).

This module NEVER modifies L2.1 data, NEVER writes to StorageAdapter,
and NEVER touches Production.

Phase B implements ``collect_evidence()`` + supporting read-only helpers
(4 logical steps):
    1. Read-only copy of source_snapshot  (deepcopy isolation)
    2. Read-only trace/result references  (ID-only strings)
    3. Incomplete marking                 (incomplete + missing_fields)
    4. Shadow marker injection            (shadow_marked / origin / is_hypothetical)

Forbidden:
    - ❌ Modify Simulation Result / Trace / Snapshot (L2.1 data)
    - ❌ StorageAdapter write
    - ❌ Production Integration
    - ❌ evaluate_evidence / execute_validation / ValidationResult construction
    - ❌ Rule execution / severity decision / metrics / governance

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

from .models import ValidationEvidence, ValidationRequest


class EvidenceCollector:
    """Read-only evidence collector (Shadow-only, Phase B implemented)."""

    SHADOW_ORIGIN: str = "composition_shadow_storage"

    def __init__(self) -> None:
        self._initialized: bool = True

    def collect_evidence(
        self,
        request: ValidationRequest,
        evidence_snapshot: Dict[str, Any],
        trace_ids: List[str],
        result_ids: List[str],
    ) -> List[ValidationEvidence]:
        """Collect read-only evidence from L2.1 shadow artifacts.

        Pure observation, zero side effects. Four logical steps:
            1. Deep-copy ``evidence_snapshot`` into each evidence's
               ``source_snapshot`` (isolation from the source).
            2. Normalize ``trace_ids`` / ``result_ids`` into ID-only string
               references (never live pointers).
            3. Mark ``incomplete`` + ``missing_fields`` when a source is absent
               (degradation, never a raise, never a skip of the evidence chain).
            4. Force-inject shadow markers (shadow_marked=True,
               origin="composition_shadow_storage", is_hypothetical=True).

        Safe degradation:
            - ``request is None`` → empty list (no ownership to attach to).
            - empty snapshot + empty trace + empty result → empty list.

        Args:
            request: ValidationRequest referencing the source artifacts.
            evidence_snapshot: Read-only copy of L2.1 SimulationEvidenceSnapshot.
            trace_ids: Read-only Trace references (trace_ids).
            result_ids: Read-only Result references (result_ids).

        Returns:
            List of ValidationEvidence (read-only copies, shadow_marked=True).
        """
        # ── Safe degradation: no ownership → no evidence ──
        if request is None:
            return []

        # Step 1: read-only copy of source snapshot (deepcopy isolation).
        snapshot_copy = self._copy_snapshot(evidence_snapshot)

        # Step 2: normalize trace/result references (ID-only strings).
        traces = self._normalize_ids(trace_ids)
        results = self._normalize_ids(result_ids)

        # Step 3: incomplete marking (absent sources are flagged, not raised).
        missing = self._detect_missing(snapshot_copy, traces, results)

        # ── Safe fallback: no evidence source at all ──
        if not snapshot_copy and not traces and not results:
            return []

        request_id = getattr(request, "request_id", "") or ""

        # Step 4: pair references → one evidence per (trace, result) pair,
        # force-inject shadow markers on every artifact.
        evidence_list: List[ValidationEvidence] = []
        for trace_ref, result_ref in self._pair_refs(traces, results):
            evidence_list.append(
                ValidationEvidence(
                    request_id=request_id,
                    source_snapshot=deepcopy(snapshot_copy),
                    source_trace_ref=trace_ref,
                    source_result_ref=result_ref,
                    incomplete=bool(missing),
                    missing_fields=list(missing),
                    shadow_marked=True,
                    origin=self.SHADOW_ORIGIN,
                    is_hypothetical=True,
                )
            )
        return evidence_list

    # ── Supporting read-only helpers ──

    def _copy_snapshot(self, evidence_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Deep-copy the snapshot (isolation from the source, C-A1).

        Non-dict input degrades to an empty dict — never raises.
        """
        if not isinstance(evidence_snapshot, dict):
            return {}
        return deepcopy(evidence_snapshot)

    def _normalize_ids(self, ids: List[str]) -> List[str]:
        """Normalize ID references to non-empty strings only.

        Non-list / non-string entries are dropped (never a live pointer).
        """
        if not isinstance(ids, (list, tuple)):
            return []
        return [i for i in ids if isinstance(i, str) and i.strip()]

    def _detect_missing(
        self,
        snapshot: Dict[str, Any],
        traces: List[str],
        results: List[str],
    ) -> List[str]:
        """Return the list of absent evidence sources (ordered, stable)."""
        missing: List[str] = []
        if not snapshot:
            missing.append("source_snapshot")
        if not traces:
            missing.append("source_trace_ref")
        if not results:
            missing.append("source_result_ref")
        return missing

    def _pair_refs(
        self, traces: List[str], results: List[str]
    ) -> List[Tuple[str, str]]:
        """Pair trace/result references (zip-longest semantics).

        Empty on both sides yields a single ("", "") pair so a snapshot-only
        evidence can still be recorded (marked incomplete on trace/result).
        """
        if not traces and not results:
            return [("", "")]
        n = max(len(traces), len(results))
        pairs: List[Tuple[str, str]] = []
        for i in range(n):
            t = traces[i] if i < len(traces) else ""
            r = results[i] if i < len(results) else ""
            pairs.append((t, r))
        return pairs

    def __repr__(self) -> str:
        return f"EvidenceCollector(initialized={self._initialized}, status=IMPLEMENTED_PHASE_B)"
