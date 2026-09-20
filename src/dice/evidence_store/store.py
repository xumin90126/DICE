"""
Phase 6.1 MatchEvidenceStore — accumulates MatchRecords for evolution analysis.

Independent from dice/evidence.py's EvidenceStore (which persists execution-level
Evidence nodes). This store holds MATCH-LEVEL snapshots — what the CapabilityMatcher
decided for each observation, regardless of whether execution happened.

Storage layout:
    dice_output/evidence_store/
    └── records.jsonl          ← append-only JSON lines
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence_store.models import MatchRecord, EvolutionCandidate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


class MatchEvidenceStore:
    """
    In-memory + persistent store for MatchRecords.

    Usage:
        store = MatchEvidenceStore()
        store.record(match_record)
        records = store.query(document_id="NDM609ME")
        low_conf = store.get_low_confidence(threshold=0.3)
    """

    def __init__(self, storage_dir: str = "dice_output/evidence_store"):
        self._storage_dir = storage_dir
        self._records: list[MatchRecord] = []
        os.makedirs(self._storage_dir, exist_ok=True)
        # Load existing records on init
        self._load()

    # ═══════════════════════════════════════════════════════════════════
    # WRITE
    # ═══════════════════════════════════════════════════════════════════

    def record(self, mr: MatchRecord) -> str:
        """
        Record a single MatchRecord. Auto-assigns ID if empty.
        Returns the record ID.

        Also persists to disk for cross-session durability.
        """
        if not mr.id:
            mr.id = _uid("MR-")
        self._records.append(mr)
        self._persist_one(mr)
        return mr.id

    def record_batch(self, records: list[MatchRecord]) -> list[str]:
        """Record multiple MatchRecords. Returns list of IDs."""
        ids = []
        for mr in records:
            ids.append(self.record(mr))
        return ids

    # ═══════════════════════════════════════════════════════════════════
    # QUERY
    # ═══════════════════════════════════════════════════════════════════

    def query(
        self,
        document_id: str = "",
        slice_id: str = "",
        capability_id: str = "",
        validation_result: str = "",
        limit: int = 0,
    ) -> list[MatchRecord]:
        """
        Filter records by optional criteria.
        All criteria are AND-combined.
        """
        results = self._records

        if document_id:
            results = [r for r in results if r.document_id == document_id]
        if slice_id:
            results = [r for r in results if r.slice_id == slice_id]
        if capability_id:
            results = [
                r for r in results
                if any(
                    c.get("capability_id") == capability_id
                    for c in r.matched_capabilities
                )
            ]
        if validation_result:
            results = [r for r in results if r.validation_result == validation_result]

        if limit and limit > 0:
            results = results[:limit]

        return results

    def get_all(self) -> list[MatchRecord]:
        """Return all records."""
        return list(self._records)

    def count(self) -> int:
        """Total number of records."""
        return len(self._records)

    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def get_low_confidence(self, threshold: float = 0.3) -> list[MatchRecord]:
        """
        Records where the top capability score is below threshold.
        These suggest the content type isn't well-served by any capability.
        """
        return [r for r in self._records if r.top_capability_score < threshold]

    def get_with_unmatched_signals(self) -> list[MatchRecord]:
        """Records where detected patterns had no matching capability."""
        return [r for r in self._records if r.has_unmatched_signals]

    def get_failures(self) -> list[MatchRecord]:
        """Records where validation failed."""
        return [r for r in self._records if r.is_failure]

    def get_repeated_failures(self, min_count: int = 3) -> dict[str, list[MatchRecord]]:
        """
        Group failures by a signature (document_id + top patterns).
        Returns {signature_key: [records]} for groups with ≥min_count.
        """
        groups: dict[str, list[MatchRecord]] = {}
        for r in self._records:
            if not r.is_failure:
                continue
            # Signature: document_id + sorted patterns
            sig = f"{r.document_id}::{'|'.join(sorted(r.detected_patterns))}"
            groups.setdefault(sig, []).append(r)

        return {k: v for k, v in groups.items() if len(v) >= min_count}

    def get_document_ids(self) -> list[str]:
        """Unique document IDs across all records."""
        return list(set(r.document_id for r in self._records if r.document_id))

    # ═══════════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════

    def _filepath(self) -> str:
        return os.path.join(self._storage_dir, "records.jsonl")

    def _persist_one(self, mr: MatchRecord) -> None:
        """Append a single record to disk."""
        filepath = self._filepath()
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(mr.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> None:
        """Load existing records from disk."""
        filepath = self._filepath()
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    mr = MatchRecord(
                        id=data.get("id", ""),
                        document_id=data.get("document_id", ""),
                        slice_id=data.get("slice_id", ""),
                        content_snippet=data.get("content_snippet", ""),
                        line_count=data.get("line_count", 0),
                        structure_flags=data.get("structure_flags", {}),
                        element_types=data.get("element_types", {}),
                        detected_patterns=data.get("detected_patterns", []),
                        pattern_scores=data.get("pattern_scores", {}),
                        matched_capabilities=data.get("matched_capabilities", []),
                        top_capability_id=data.get("top_capability_id", ""),
                        top_capability_score=data.get("top_capability_score", 0.0),
                        total_candidates_above_threshold=data.get("total_candidates_above_threshold", 0),
                        max_match_score=data.get("max_match_score", 0.0),
                        validation_result=data.get("validation_result", ""),
                        failure_reason=data.get("failure_reason", ""),
                        unmatched_signals=data.get("unmatched_signals", []),
                        timestamp=data.get("timestamp", ""),
                        pipeline_version=data.get("pipeline_version", ""),
                    )
                    self._records.append(mr)
                except (json.JSONDecodeError, TypeError):
                    continue

    def clear(self) -> None:
        """Clear all records (memory + disk)."""
        self._records.clear()
        filepath = self._filepath()
        if os.path.exists(filepath):
            os.remove(filepath)

    # ═══════════════════════════════════════════════════════════════════
    # FACTORY: Build MatchRecord from Observation + MatchResult
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def from_observation_and_match(
        document_id: str,
        slice_id: str,
        content: str,
        obs,       # DocumentObservation
        match_result,  # MatchResult from CapabilityMatcher.match()
        validation_result: str = "",
        failure_reason: str = "",
        pipeline_version: str = "phase6.1",
    ) -> MatchRecord:
        """
        Factory method: build a MatchRecord from ObservationBuilder +
        CapabilityMatcher outputs.

        This is the MAIN way to create records — call it after every
        ObservationBuilder.from_content() + CapabilityMatcher.match().
        """
        # ── Extract matched capabilities ──
        matched_caps = []
        for i, c in enumerate(match_result.candidates[:10]):
            matched_caps.append({
                "capability_id": c.capability_id,
                "capability_name": c.capability_name,
                "score": round(c.score, 4),
                "rank": i + 1,
                "matched_patterns": c.matched_patterns,
                "matched_element_types": c.matched_element_types,
            })

        # ── Determine unmatched signals ──
        # Patterns that were detected but NOT matched to any candidate.
        matched_pattern_ids: set[str] = set()
        for c in match_result.candidates:
            matched_pattern_ids.update(c.matched_patterns)

        unmatched_patterns = [
            p for p in obs.detected_pattern_ids
            if p not in matched_pattern_ids
        ]

        # Element types detected but not referenced by any candidate
        matched_elem_types: set[str] = set()
        for c in match_result.candidates:
            matched_elem_types.update(c.matched_element_types)

        element_types_with_values = [
            k for k, v in obs.detected_element_types.items()
            if v > 0 and k not in matched_elem_types
        ]

        unmatched_signals = unmatched_patterns + [
            f"elem:{et}" for et in element_types_with_values
        ]

        # ── Top candidate ──
        top = match_result.candidates[0] if match_result.candidates else None

        # ── Threshold count ──
        threshold = 0.25
        above = sum(1 for c in match_result.candidates if c.score >= threshold)

        return MatchRecord(
            document_id=document_id,
            slice_id=slice_id,
            content_snippet=content[:300],
            line_count=obs.line_count,
            structure_flags={
                "has_table_structure": obs.has_table_structure,
                "has_collapsed_table": obs.has_collapsed_table,
                "has_list_structure": obs.has_list_structure,
                "has_key_value_pairs": obs.has_key_value_pairs,
                "has_markdown_table": obs.has_markdown_table,
                "has_numbered_list": obs.has_numbered_list,
                "has_numeric_density_high": obs.has_numeric_density_high,
            },
            element_types=dict(obs.detected_element_types),
            detected_patterns=obs.detected_pattern_ids,
            pattern_scores=dict(obs.pattern_match_scores),
            matched_capabilities=matched_caps,
            top_capability_id=top.capability_id if top else "",
            top_capability_score=top.score if top else 0.0,
            total_candidates_above_threshold=above,
            max_match_score=max((c.score for c in match_result.candidates), default=0.0),
            validation_result=validation_result,
            failure_reason=failure_reason,
            unmatched_signals=unmatched_signals,
            pipeline_version=pipeline_version,
        )
