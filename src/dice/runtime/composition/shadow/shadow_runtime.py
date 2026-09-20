"""
ShadowObserver — Production Runtime output capture.

Phase 6.1-L1: Captures read-only snapshots of Evidence and Capability
Match results from the production Runtime (Layer 1-8). These snapshots
are the input to the Shadow pipeline.

Constraints:
    ✅ Reads only public production Runtime outputs
    ✅ Creates ShadowObservation with shadow_marked=True
    ❌ Never calls Execution Runtime
    ❌ Never calls Capability Activation
    ❌ Never triggers Production Pipeline
    ❌ Never modifies Registry
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models.observation import (
    ShadowObservation,
    EvidenceSnapshot,
    CapabilityMatchSnapshot,
)
from .shadow_storage import ShadowStorage


class ShadowObserver:
    """Captures production Runtime outputs as ShadowObservations.

    ShadowObserver is a read-only sidecar. It observes what the
    production Runtime produces, but NEVER modifies, redirects, or
    influences production execution.

    Usage:
        observer = ShadowObserver(storage)
        obs = observer.capture_observation(
            document_id="NDM609ME",
            document_type="IFU",
            evidence_results=[...],
            capability_matches=[...],
            production_trace_id="trace-123",
        )
        # or batch:
        observations = observer.capture_batch([...])
    """

    def __init__(self, storage: Optional[ShadowStorage] = None):
        """Initialize ShadowObserver with optional storage.

        Args:
            storage: ShadowStorage instance. If None, creates a new one.
        """
        self._storage = storage or ShadowStorage()
        self._capture_count: int = 0
        self._batch_count: int = 0
        self._error_count: int = 0

    # ── Public API ──

    def capture_observation(
        self,
        document_id: str,
        document_type: str = "",
        evidence_results: Optional[List[Dict[str, Any]]] = None,
        capability_matches: Optional[List[Dict[str, Any]]] = None,
        production_trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_store: bool = True,
    ) -> ShadowObservation:
        """Capture a single production Runtime output as a ShadowObservation.

        Args:
            document_id: Source document identifier (required)
            document_type: Document type (e.g. "IFU", "SOP")
            evidence_results: EvidenceRuntime output snapshots
            capability_matches: CapabilityRuntime match snapshots
            production_trace_id: Production trace ID for cross-reference
            metadata: Additional metadata
            auto_store: If True, automatically store in ShadowStorage

        Returns:
            ShadowObservation with shadow_marked=True

        Raises:
            ValueError: If document_id is empty
        """
        if not document_id:
            raise ValueError("ShadowObserver.capture_observation() requires document_id")

        try:
            # ── Build evidence snapshots ──
            evidence_snapshots = self._build_evidence_snapshots(
                evidence_results or []
            )

            # ── Build capability match snapshots ──
            match_snapshots = self._build_capability_snapshots(
                capability_matches or []
            )

            # ── Create observation ──
            observation = ShadowObservation(
                observation_id=str(uuid4()),
                document_id=document_id,
                document_type=document_type,
                timestamp=datetime.now(timezone.utc).isoformat(),
                production_trace_id=production_trace_id,
                evidence_results=evidence_snapshots,
                capability_matches=match_snapshots,
                shadow_marked=True,
                metadata=metadata or {},
            )

            # ── Auto-store ──
            if auto_store:
                self._storage.store(
                    "observations",
                    observation.observation_id,
                    observation.to_dict(),
                )

            self._capture_count += 1
            return observation

        except Exception as e:
            self._error_count += 1
            raise RuntimeError(
                f"ShadowObserver.capture_observation() failed for "
                f"document_id={document_id}: {e}"
            ) from e

    def capture_batch(
        self,
        documents: List[Dict[str, Any]],
        auto_store: bool = True,
    ) -> List[ShadowObservation]:
        """Capture observations for a batch of documents.

        Args:
            documents: List of document spec dicts, each containing:
                - document_id (str, required)
                - document_type (str, optional)
                - evidence_results (list, optional)
                - capability_matches (list, optional)
                - production_trace_id (str, optional)
                - metadata (dict, optional)
            auto_store: If True, auto-store each observation

        Returns:
            List of ShadowObservation objects

        Raises:
            ValueError: If any document is missing document_id
        """
        observations: List[ShadowObservation] = []
        errors: List[Dict[str, Any]] = []

        for i, doc in enumerate(documents):
            try:
                obs = self.capture_observation(
                    document_id=doc["document_id"],
                    document_type=doc.get("document_type", ""),
                    evidence_results=doc.get("evidence_results"),
                    capability_matches=doc.get("capability_matches"),
                    production_trace_id=doc.get("production_trace_id"),
                    metadata=doc.get("metadata"),
                    auto_store=auto_store,
                )
                observations.append(obs)
            except Exception as e:
                errors.append({
                    "index": i,
                    "document_id": doc.get("document_id", f"unknown[{i}]"),
                    "error": str(e),
                })

        self._batch_count += 1

        # If any errors occurred, attach them to the last observation's metadata
        if errors and observations:
            observations[-1].metadata["_batch_errors"] = errors

        return observations

    # ── Queries ──

    @property
    def storage(self) -> ShadowStorage:
        """Access the underlying ShadowStorage."""
        return self._storage

    @property
    def capture_count(self) -> int:
        """Total single captures performed."""
        return self._capture_count

    @property
    def batch_count(self) -> int:
        """Total batch captures performed."""
        return self._batch_count

    def stats(self) -> Dict[str, Any]:
        """Return observer statistics."""
        return {
            "capture_count": self._capture_count,
            "batch_count": self._batch_count,
            "error_count": self._error_count,
            "stored_observations": self._storage.count("observations"),
            "storage_stats": self._storage.stats(),
        }

    # ── Internal ──

    def _build_evidence_snapshots(
        self, raw: List[Dict[str, Any]]
    ) -> List[EvidenceSnapshot]:
        """Build EvidenceSnapshot list from raw dicts."""
        snapshots: List[EvidenceSnapshot] = []
        for item in raw:
            snapshots.append(EvidenceSnapshot(
                evidence_id=item.get("evidence_id", str(uuid4())),
                evidence_type=item.get("evidence_type", ""),
                span_text=item.get("span_text", ""),
                confidence=float(item.get("confidence", 0.0)),
                source_capability=item.get("source_capability", ""),
                metadata=item.get("metadata", {}),
            ))
        return snapshots

    def _build_capability_snapshots(
        self, raw: List[Dict[str, Any]]
    ) -> List[CapabilityMatchSnapshot]:
        """Build CapabilityMatchSnapshot list from raw dicts."""
        snapshots: List[CapabilityMatchSnapshot] = []
        for item in raw:
            snapshots.append(CapabilityMatchSnapshot(
                capability_id=item.get("capability_id", ""),
                capability_name=item.get("capability_name", ""),
                match_score=float(item.get("match_score", 0.0)),
                matched_patterns=item.get("matched_patterns", []),
                execution_decision=item.get("execution_decision", ""),
                metadata=item.get("metadata", {}),
            ))
        return snapshots

    def __repr__(self) -> str:
        return (
            f"ShadowObserver(captures={self._capture_count}, "
            f"batches={self._batch_count}, "
            f"errors={self._error_count}, "
            f"stored={self._storage.count('observations')})"
        )